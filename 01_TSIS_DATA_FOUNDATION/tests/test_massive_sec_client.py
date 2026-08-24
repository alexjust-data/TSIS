# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.massive_sec_client import MassiveResponseContractError, MassiveSecClient
from sec_pit.massive_sec_models import ENDPOINT_SPECS


class FakeSession:
    def __init__(self, responses: list[requests.Response]) -> None:
        self.headers: dict[str, str] = {}
        self.responses = list(responses)
        self.urls: list[str] = []

    def get(self, url: str, timeout: float) -> requests.Response:
        assert timeout > 0
        self.urls.append(url)
        return self.responses.pop(0)


def _response(status: int, payload: dict[str, object]) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(payload).encode("utf-8")
    response.headers = {}
    response.url = "https://api.massive.com/test"
    return response


def _taxonomy_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": "OK",
        "request_id": "request-1",
        "results": [{"taxonomy": "Item 1.01", "primary_category": "Agreement"}],
    }
    payload.update(overrides)
    return payload


def test_bearer_secret_never_enters_url() -> None:
    session = FakeSession([_response(200, _taxonomy_payload())])
    client = MassiveSecClient(
        api_key="secret-value",
        session_factory=lambda: session,
        sleep=lambda _seconds: None,
    )
    spec = ENDPOINT_SPECS["disclosure_taxonomy"]
    page = client.fetch_page(
        spec=spec, url=client.build_initial_url(spec, cik=None), target_cik=None
    )

    assert session.headers["Authorization"] == "Bearer secret-value"
    assert all("secret-value" not in url and "apiKey" not in url for url in session.urls)
    assert "secret-value" not in page.sanitized_url


def test_http_429_reduces_global_rate_and_retries() -> None:
    session = FakeSession(
        [_response(429, {"status": "ERROR"}), _response(200, _taxonomy_payload())]
    )
    client = MassiveSecClient(
        api_key="secret",
        requests_per_second=2.0,
        max_attempts=3,
        session_factory=lambda: session,
        sleep=lambda _seconds: None,
    )
    spec = ENDPOINT_SPECS["disclosure_taxonomy"]
    page = client.fetch_page(
        spec=spec, url=client.build_initial_url(spec, cik=None), target_cik=None
    )

    assert page.http_429_count == 1
    assert page.retry_count == 1
    assert client.rate_limiter.current_requests_per_second == 1.0


def test_pagination_cannot_escape_host_or_endpoint_path() -> None:
    client = MassiveSecClient(api_key="secret", sleep=lambda _seconds: None)
    spec = ENDPOINT_SPECS["edgar_index"]

    with pytest.raises(MassiveResponseContractError, match="escaped"):
        client.validate_page_url(
            "https://attacker.example/stocks/filings/vX/index?cursor=x", spec
        )
    with pytest.raises(MassiveResponseContractError, match="path drift"):
        client.validate_page_url(
            "https://api.massive.com/stocks/filings/vX/form-4?cursor=x", spec
        )


def test_response_without_request_id_fails_closed() -> None:
    session = FakeSession([_response(200, _taxonomy_payload(request_id=""))])
    client = MassiveSecClient(
        api_key="secret",
        session_factory=lambda: session,
        sleep=lambda _seconds: None,
    )
    spec = ENDPOINT_SPECS["disclosure_taxonomy"]

    with pytest.raises(MassiveResponseContractError, match="request_id"):
        client.fetch_page(
            spec=spec, url=client.build_initial_url(spec, cik=None), target_cik=None
        )
