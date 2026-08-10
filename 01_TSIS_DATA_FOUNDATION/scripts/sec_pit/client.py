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
    ) -> None:
        if not user_agent or "@" not in user_agent:
            raise ValueError("SEC User-Agent must identify the organization and contain a contact email")
        if not 0 < requests_per_second <= 10:
            raise ValueError("requests_per_second must be within (0, 10]")
        self.user_agent = user_agent
        self.store = store
        self.acquisition_log = acquisition_log
        self.interval = 1.0 / requests_per_second
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        self._last_request_at = 0.0

    def _throttle(self) -> None:
        remaining = self.interval - (time.monotonic() - self._last_request_at)
        if remaining > 0:
            time.sleep(remaining)

    @staticmethod
    def _suffix(url: str, content_type: str | None) -> str:
        suffix = Path(urlparse(url).path).suffix
        if suffix:
            return suffix
        guessed = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
        return guessed or ".bin"

    def fetch(self, url: str, logical_path: str | None = None) -> AcquisitionResult:
        attempts = 0
        error: str | None = None
        for attempts in range(1, self.retries + 1):
            try:
                self._throttle()
                response = self.session.get(url, timeout=self.timeout_seconds)
                self._last_request_at = time.monotonic()
                if response.status_code in {429, 500, 502, 503, 504}:
                    delay = float(response.headers.get("Retry-After", min(30, 2 ** (attempts - 1))))
                    time.sleep(delay)
                    continue
                response.raise_for_status()
                content_type = response.headers.get("Content-Type")
                digest, object_path, byte_count = self.store.put(
                    response.content,
                    suffix=self._suffix(url, content_type),
                    compress=True,
                )
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
                return result
            except requests.RequestException as exc:
                error = f"{type(exc).__name__}: {exc}"
                if attempts < self.retries:
                    time.sleep(min(30, 2 ** (attempts - 1)))

        result = AcquisitionResult(
            url=url,
            status="FAILED",
            http_status=None,
            fetched_at_utc=datetime.now(UTC).isoformat(),
            sha256=None,
            bytes=0,
            content_type=None,
            object_path=None,
            logical_path=logical_path,
            attempts=attempts,
            error=error,
        )
        append_jsonl(self.acquisition_log, result.to_dict())
        return result

    def fetch_json(self, url: str, logical_path: str | None = None) -> tuple[AcquisitionResult, dict[str, Any] | None]:
        result = self.fetch(url, logical_path)
        if result.status != "FETCHED" or result.object_path is None:
            return result, None
        payload = self.store.read(Path(result.object_path))
        return result, json.loads(payload.decode("utf-8"))

