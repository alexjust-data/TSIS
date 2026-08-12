from __future__ import annotations

import json
import mimetypes
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from sec_pit.models import AcquisitionResult
from sec_pit.storage import ContentAddressedStore, append_jsonl


class SecClient:
    def __init__(
        self,
        *,
        user_agent: str,
        store: ContentAddressedStore,
        acquisition_log: Path,
        requests_per_second: float = 5.0,
        timeout_seconds: float = 60.0,
        retries: int = 5,
        session: requests.Session | None = None,
        telemetry_log: Path | None = None,
    ) -> None:
        if not user_agent or "@" not in user_agent:
            raise ValueError(
                "SEC User-Agent must identify the organization and contain a contact email"
            )
        if not 0 < requests_per_second <= 10:
            raise ValueError("requests_per_second must be within (0, 10]")
        self.user_agent = user_agent
        self.store = store
        self.acquisition_log = acquisition_log
        self.interval = 1.0 / requests_per_second
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.session = session or requests.Session()
        self.telemetry_log = telemetry_log
        self.last_performance: dict[str, Any] | None = None
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        self._last_request_at = 0.0

    def _throttle(self) -> float:
        remaining = self.interval - (time.monotonic() - self._last_request_at)
        if remaining > 0:
            time.sleep(remaining)
            return remaining
        return 0.0

    @staticmethod
    def _suffix(url: str, content_type: str | None) -> str:
        suffix = Path(urlparse(url).path).suffix
        if suffix:
            return suffix
        guessed = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
        return guessed or ".bin"

    def fetch(
        self,
        url: str,
        logical_path: str | None = None,
        telemetry_context: dict[str, Any] | None = None,
    ) -> AcquisitionResult:
        started = time.perf_counter()
        attempts = 0
        error: str | None = None
        throttle_seconds = 0.0
        retry_wait_seconds = 0.0
        request_attempt_seconds: list[float] = []
        retry_count = 0
        http_429_count = 0
        last_http_status: int | None = None
        storage_timings: dict[str, Any] = {}
        result: AcquisitionResult | None = None
        for attempts in range(1, self.retries + 1):
            try:
                throttle_seconds += self._throttle()
                request_started = time.perf_counter()
                response = self.session.get(url, timeout=self.timeout_seconds)
                request_attempt_seconds.append(time.perf_counter() - request_started)
                self._last_request_at = time.monotonic()
                last_http_status = response.status_code
                if response.status_code in {429, 500, 502, 503, 504}:
                    delay = float(response.headers.get("Retry-After", min(30, 2 ** (attempts - 1))))
                    retry_count += 1
                    http_429_count += response.status_code == 429
                    time.sleep(delay)
                    retry_wait_seconds += delay
                    continue
                response.raise_for_status()
                content_type = response.headers.get("Content-Type")
                storage_started = time.perf_counter()
                digest, object_path, byte_count = self.store.put(
                    response.content,
                    suffix=self._suffix(url, content_type),
                    compress=True,
                    timings=storage_timings,
                )
                storage_timings["storage_seconds"] = time.perf_counter() - storage_started
                result = AcquisitionResult(
                    url=url,
                    status="FETCHED",
                    http_status=response.status_code,
                    fetched_at_utc=datetime.now(UTC).isoformat(),
                    sha256=digest,
                    bytes=byte_count,
                    content_type=content_type,
                    object_path=object_path.as_posix(),
                    logical_path=logical_path,
                    attempts=attempts,
                )
                append_jsonl(self.acquisition_log, result.to_dict())
                break
            except requests.RequestException as exc:
                if len(request_attempt_seconds) < attempts:
                    request_attempt_seconds.append(time.perf_counter() - request_started)
                error = f"{type(exc).__name__}: {exc}"
                if (
                    last_http_status is not None
                    and 400 <= last_http_status < 500
                    and last_http_status != 429
                ):
                    break
                if attempts < self.retries:
                    delay = min(30, 2 ** (attempts - 1))
                    retry_count += 1
                    time.sleep(delay)
                    retry_wait_seconds += delay

        if result is None:
            result = AcquisitionResult(
                url=url,
                status="FAILED",
                http_status=last_http_status,
                fetched_at_utc=datetime.now(UTC).isoformat(),
                sha256=None,
                bytes=0,
                content_type=None,
                object_path=None,
                logical_path=logical_path,
                attempts=attempts,
                error=error or f"retryable HTTP status exhausted: {last_http_status}",
            )
            append_jsonl(self.acquisition_log, result.to_dict())
        performance = {
            "observed_at_utc": datetime.now(UTC).isoformat(),
            "url": url,
            "logical_path": logical_path,
            "status": result.status,
            "http_status": result.http_status,
            "attempts": attempts,
            "retry_count": retry_count,
            "http_429_count": http_429_count,
            "bytes": result.bytes,
            "total_seconds": time.perf_counter() - started,
            "throttle_seconds": throttle_seconds,
            "request_seconds": sum(request_attempt_seconds),
            "request_attempt_seconds": request_attempt_seconds,
            "retry_wait_seconds": retry_wait_seconds,
            "storage_seconds": storage_timings.get("storage_seconds", 0.0),
            "sha256_seconds": storage_timings.get("sha256_seconds", 0.0),
            "gzip_seconds": storage_timings.get("gzip_seconds", 0.0),
            "atomic_write_seconds": storage_timings.get("atomic_write_seconds", 0.0),
            "stored_bytes": storage_timings.get("stored_bytes", 0),
            "deduplicated": storage_timings.get("deduplicated", False),
            **(telemetry_context or {}),
        }
        self.last_performance = performance
        if self.telemetry_log is not None:
            append_jsonl(self.telemetry_log, performance)
        return result

    def fetch_json(
        self, url: str, logical_path: str | None = None
    ) -> tuple[AcquisitionResult, dict[str, Any] | None]:
        result = self.fetch(url, logical_path)
        if result.status != "FETCHED" or result.object_path is None:
            return result, None
        payload = self.store.read(Path(result.object_path))
        return result, json.loads(payload.decode("utf-8"))
