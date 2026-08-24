"""Auditable Massive REST client with shared adaptive throttling and safe pagination."""

from __future__ import annotations

import json
import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

import requests

from sec_pit.massive_sec_models import EndpointSpec, sanitize_url

RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class MassiveResponseContractError(RuntimeError):
    """Response cannot be committed because its identity/schema is unsafe."""


class AdaptiveRateLimiter:
    """One process-wide limiter shared by every HTTP worker.

    The public Massive docs do not publish one universal REST rate limit.  The
    configured rate is therefore an engineering ceiling, not a vendor claim.
    HTTP 429 halves the current rate; sustained successes recover slowly up to
    the configured ceiling.
    """

    def __init__(
        self,
        requests_per_second: float,
        *,
        minimum_requests_per_second: float = 0.25,
        recovery_successes: int = 100,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if not 0 < minimum_requests_per_second <= requests_per_second:
            raise ValueError("minimum rate must be within (0, configured rate]")
        self.ceiling = float(requests_per_second)
        self.minimum = float(minimum_requests_per_second)
        self.current = float(requests_per_second)
        self.recovery_successes = int(recovery_successes)
        self.sleep = sleep
        self._lock = threading.Lock()
        self._last_slot = 0.0
        self._successes_since_penalty = 0

    @property
    def current_requests_per_second(self) -> float:
        with self._lock:
            return self.current

    def wait(self) -> float:
        with self._lock:
            now = time.monotonic()
            interval = 1.0 / self.current
            scheduled = max(now, self._last_slot + interval)
            self._last_slot = scheduled
        delay = max(0.0, scheduled - time.monotonic())
        if delay:
            self.sleep(delay)
        return delay

    def on_429(self) -> None:
        with self._lock:
            self.current = max(self.minimum, self.current / 2.0)
            self._successes_since_penalty = 0

    def on_success(self) -> None:
        with self._lock:
            self._successes_since_penalty += 1
            if self._successes_since_penalty >= self.recovery_successes:
                self.current = min(self.ceiling, self.current * 1.10)
                self._successes_since_penalty = 0


@dataclass(frozen=True)
class FetchedPage:
    endpoint_id: str
    target_cik: str | None
    sanitized_url: str
    request_id: str
    retrieved_at_utc: str
    response_bytes: bytes
    payload: dict[str, Any]
    results: list[dict[str, Any]]
    next_url: str | None
    http_status: int
    attempts: int
    retry_count: int
    http_429_count: int
    elapsed_seconds: float
    observed_fields: tuple[str, ...]


class MassiveSecClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.massive.com",
        requests_per_second: float = 2.0,
        timeout_seconds: float = 60.0,
        max_attempts: int = 6,
        session_factory: Callable[[], requests.Session] = requests.Session,
        sleep: Callable[[float], None] = time.sleep,
        random_source: random.Random | None = None,
    ) -> None:
        if not api_key or api_key.strip() != api_key:
            raise ValueError("MASSIVE_API_KEY is missing or malformed")
        parsed = urlsplit(base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("Massive base URL must be absolute HTTPS")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.allowed_host = parsed.netloc.casefold()
        self.timeout_seconds = float(timeout_seconds)
        self.max_attempts = int(max_attempts)
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        self.session_factory = session_factory
        self.sleep = sleep
        self.random = random_source or random.SystemRandom()
        self.rate_limiter = AdaptiveRateLimiter(
            requests_per_second, sleep=sleep
        )
        self._local = threading.local()

    def _session(self) -> requests.Session:
        session = getattr(self._local, "session", None)
        if session is None:
            session = self.session_factory()
            session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "User-Agent": "TSIS-Massive-SEC-Acquisition/0.1",
                }
            )
            self._local.session = session
        return session

    def build_initial_url(self, spec: EndpointSpec, *, cik: str | None) -> str:
        query = urlencode(sorted(spec.initial_parameters(cik=cik).items()))
        return f"{self.base_url}{spec.path}?{query}"

    def validate_page_url(self, url: str, spec: EndpointSpec) -> str:
        clean = sanitize_url(url)
        parsed = urlsplit(clean)
        if parsed.scheme != "https" or parsed.netloc.casefold() != self.allowed_host:
            raise MassiveResponseContractError(
                f"pagination URL escaped the governed Massive host: {clean}"
            )
        if parsed.path != spec.path:
            raise MassiveResponseContractError(
                f"pagination URL path drift: expected {spec.path}, got {parsed.path}"
            )
        return clean

    @staticmethod
    def _retry_delay(response: requests.Response | None, attempt: int, jitter: float) -> float:
        retry_after = response.headers.get("Retry-After") if response is not None else None
        if retry_after:
            try:
                return min(120.0, max(0.0, float(retry_after)))
            except ValueError:
                pass
        return min(60.0, 2.0 ** max(0, attempt - 1)) + jitter

    @staticmethod
    def _validate_payload(
        spec: EndpointSpec, payload: Any
    ) -> tuple[str, list[dict[str, Any]], str | None, tuple[str, ...]]:
        if not isinstance(payload, dict):
            raise MassiveResponseContractError("response root is not a JSON object")
        if payload.get("status") != "OK":
            raise MassiveResponseContractError(
                f"response status is not OK: {payload.get('status')!r}"
            )
        request_id = payload.get("request_id")
        if not isinstance(request_id, str) or not request_id.strip():
            raise MassiveResponseContractError("response has no auditable request_id")
        results = payload.get("results")
        if not isinstance(results, list) or any(not isinstance(row, dict) for row in results):
            raise MassiveResponseContractError("response results is not an array of objects")
        next_url = payload.get("next_url")
        if next_url is not None and not isinstance(next_url, str):
            raise MassiveResponseContractError("response next_url is not a string")
        observed = tuple(sorted({key for row in results for key in row}))
        for index, row in enumerate(results):
            missing = [field for field in spec.identity_fields if row.get(field) in (None, "")]
            if missing:
                raise MassiveResponseContractError(
                    f"{spec.endpoint_id} row {index} lacks identity fields: {missing}"
                )
        return request_id, results, next_url, observed

    def fetch_page(
        self,
        *,
        spec: EndpointSpec,
        url: str,
        target_cik: str | None,
    ) -> FetchedPage:
        clean_url = self.validate_page_url(url, spec)
        started = time.perf_counter()
        attempts = retry_count = http_429_count = 0
        last_error: str | None = None
        for attempts in range(1, self.max_attempts + 1):
            response: requests.Response | None = None
            try:
                self.rate_limiter.wait()
                response = self._session().get(clean_url, timeout=self.timeout_seconds)
                status = int(response.status_code)
                if status in RETRYABLE_HTTP_STATUS:
                    retry_count += 1
                    if status == 429:
                        http_429_count += 1
                        self.rate_limiter.on_429()
                    if attempts >= self.max_attempts:
                        raise MassiveResponseContractError(
                            f"retryable HTTP status exhausted: {status}"
                        )
                    self.sleep(
                        self._retry_delay(response, attempts, self.random.uniform(0.0, 0.5))
                    )
                    continue
                response.raise_for_status()
                try:
                    payload = json.loads(response.content.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise MassiveResponseContractError(
                        f"response is not valid UTF-8 JSON: {exc}"
                    ) from exc
                request_id, results, next_url, observed = self._validate_payload(spec, payload)
                if next_url is not None:
                    next_url = self.validate_page_url(next_url, spec)
                self.rate_limiter.on_success()
                return FetchedPage(
                    endpoint_id=spec.endpoint_id,
                    target_cik=target_cik,
                    sanitized_url=clean_url,
                    request_id=request_id,
                    retrieved_at_utc=utc_now(),
                    response_bytes=response.content,
                    payload=payload,
                    results=results,
                    next_url=next_url,
                    http_status=status,
                    attempts=attempts,
                    retry_count=retry_count,
                    http_429_count=http_429_count,
                    elapsed_seconds=time.perf_counter() - started,
                    observed_fields=observed,
                )
            except MassiveResponseContractError:
                raise
            except requests.RequestException as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                status = int(response.status_code) if response is not None else None
                if status is not None and 400 <= status < 500 and status != 429:
                    raise MassiveResponseContractError(
                        f"terminal HTTP status {status} for {clean_url}"
                    ) from exc
                if attempts >= self.max_attempts:
                    break
                retry_count += 1
                self.sleep(
                    self._retry_delay(response, attempts, self.random.uniform(0.0, 0.5))
                )
        raise MassiveResponseContractError(
            f"request failed after {attempts} attempts: {last_error or clean_url}"
        )


def without_query(url: str) -> str:
    """Small helper used only in error messages and tests."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
