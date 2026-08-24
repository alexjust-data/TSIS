# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "sec_pit"))

import run_massive_sec_acquisition as runner
from sec_pit.massive_sec_authorization import AuthorizationDecision, FrozenTarget
from sec_pit.massive_sec_client import FetchedPage, MassiveResponseContractError
from sec_pit.massive_sec_storage import MassiveSecStorage, file_sha256


class _RateLimiter:
    current_requests_per_second = 2.0


class FakeClient:
    def __init__(self, *, fail_on_call: int | None) -> None:
        self.fail_on_call = fail_on_call
        self.calls: list[str] = []
        self.rate_limiter = _RateLimiter()

    def build_initial_url(self, spec, *, cik: str | None) -> str:
        return (
            f"https://api.massive.com{spec.path}"
            f"?cik={cik or 'singleton'}&limit={spec.page_limit}"
        )

    def fetch_page(self, *, spec, url: str, target_cik: str | None) -> FetchedPage:
        self.calls.append(url)
        if self.fail_on_call == len(self.calls):
            raise MassiveResponseContractError("simulated abrupt network loss")
        result = {
            "accession_number": f"accession-{target_cik}",
            "cik": target_cik,
            "form_type": "8-K",
        }
        payload = {
            "status": "OK",
            "request_id": f"request-{target_cik}",
            "results": [result],
        }
        response_bytes = json.dumps(payload, sort_keys=True).encode()
        return FetchedPage(
            endpoint_id=spec.endpoint_id,
            target_cik=target_cik,
            sanitized_url=url,
            request_id=str(payload["request_id"]),
            retrieved_at_utc="2026-08-22T00:00:00+00:00",
            response_bytes=response_bytes,
            payload=payload,
            results=[result],
            next_url=None,
            http_status=200,
            attempts=1,
            retry_count=0,
            http_429_count=0,
            elapsed_seconds=0.01,
            observed_fields=tuple(sorted(result)),
        )


def test_failed_run_resumes_from_first_uncommitted_page(
    tmp_path: Path, monkeypatch
) -> None:
    output_root = tmp_path / "output"
    control_root = tmp_path / "control"
    output_root.mkdir()
    objective = tmp_path / "objective.md"
    objective.write_text("# Exact objective\n", encoding="utf-8")
    target_path = tmp_path / "target.parquet"
    pd.DataFrame(
        [
            {
                "selection_order": 1,
                "instrument_id": "instrument-1",
                "ticker": "AAA",
                "cik": "1",
            },
            {
                "selection_order": 2,
                "instrument_id": "instrument-2",
                "ticker": "BBB",
                "cik": "2",
            },
        ]
    ).to_parquet(target_path, index=False)
    target_manifest = tmp_path / "target_manifest.json"
    target_manifest.write_text('{"target_id":"test"}', encoding="utf-8")
    config_path = tmp_path / "config.json"
    config_path.write_text('{"config_id":"test"}', encoding="utf-8")
    authorization = tmp_path / "authorization.json"
    authorization.write_text('{"status":"AUTHORIZED"}', encoding="utf-8")
    config = {
        "objective_path": objective.as_posix(),
        "target_manifest_path": target_manifest.as_posix(),
        "output_root": output_root.as_posix(),
        "control_runtime_root": control_root.as_posix(),
        "base_url": "https://api.massive.com",
        "endpoint_ids": ["edgar_index"],
        "http_workers": 1,
        "maximum_http_workers_after_probe": 1,
        "requests_per_second": 2.0,
        "timeout_seconds": 1.0,
        "max_attempts": 1,
        "maximum_pages_per_chain": 10,
        "telemetry_interval_seconds": 60.0,
        "minimum_free_space_gib": 0.0,
    }
    frozen = FrozenTarget(
        path=target_path,
        sha256=file_sha256(target_path),
        row_count=2,
        unique_ticker_count=2,
        unique_instrument_count=2,
        unique_cik_count=2,
    )
    monkeypatch.setattr(runner, "validate_config", lambda _path: config)
    monkeypatch.setattr(runner, "validate_frozen_target", lambda _path: frozen)
    monkeypatch.setattr(
        runner,
        "validate_authorization",
        lambda *_args, **_kwargs: AuthorizationDecision(
            "PASS", "TEST", "test", ("edgar_index",), 2, 2
        ),
    )
    monkeypatch.setenv("MASSIVE_API_KEY", "test-secret")
    first_client = FakeClient(fail_on_call=2)
    monkeypatch.setattr(runner, "MassiveSecClient", lambda **_kwargs: first_client)
    base_args = {
        "config": config_path,
        "target_manifest": target_manifest,
        "authorization": authorization,
        "run_id": "resume-test",
        "execution_mode": "PROBE",
    }

    first_exit = runner.execute(
        argparse.Namespace(**base_args, execute=True, resume=False)
    )
    storage = MassiveSecStorage(output_root, "resume-test")
    assert first_exit == 1
    assert len(list(storage.iter_receipts())) == 1

    resume_client = FakeClient(fail_on_call=None)
    monkeypatch.setattr(runner, "MassiveSecClient", lambda **_kwargs: resume_client)
    resume_exit = runner.execute(
        argparse.Namespace(**base_args, execute=False, resume=True)
    )

    assert resume_exit == 0
    assert len(resume_client.calls) == 1
    assert len(list(storage.iter_receipts())) == 2
    final = json.loads(
        (storage.run_root / "final_manifest.json").read_text(encoding="utf-8")
    )
    assert final["status"] == "COMPLETE"
    assert final["runtime_counters"]["pages_resumed"] == 1
