# ruff: noqa: E402
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit import storage
from sec_pit.client import SecClient
from sec_pit.storage import ContentAddressedStore, atomic_write_bytes, read_jsonl
from sec_pit.telemetry import LiveResourceTelemetry, summarize_document_performance


class FakeResponse:
    def __init__(
        self, status_code: int, payload: bytes = b"filing", headers: dict[str, str] | None = None
    ) -> None:
        self.status_code = status_code
        self.content = payload
        self.headers = headers or {"Content-Type": "text/html"}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = iter(responses)
        self.headers: dict[str, str] = {}

    def get(self, _url: str, timeout: float) -> FakeResponse:
        assert timeout > 0
        return next(self.responses)


def test_atomic_write_retries_transient_windows_reader_lock(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "heartbeat_latest.json"
    real_replace = storage.os.replace
    attempts = {"count": 0}

    def flaky_replace(source: str, destination: Path) -> None:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise PermissionError(5, "transient reader lock")
        real_replace(source, destination)

    monkeypatch.setattr(storage.os, "replace", flaky_replace)
    monkeypatch.setattr(storage.time, "sleep", lambda _seconds: None)

    atomic_write_bytes(target, b'{"status":"RUNNING"}\n')

    assert attempts["count"] == 3
    assert target.read_bytes() == b'{"status":"RUNNING"}\n'


def test_fetch_emits_stage_timing_without_changing_acquisition_result(tmp_path: Path) -> None:
    performance = tmp_path / "document_performance.jsonl"
    client = SecClient(
        user_agent="TSIS test test@example.com",
        store=ContentAddressedStore(tmp_path / "objects"),
        acquisition_log=tmp_path / "acquisition.jsonl",
        telemetry_log=performance,
        session=FakeSession([FakeResponse(200)]),
        requests_per_second=10,
    )
    result = client.fetch("https://example.test/a.htm", "primary/AAA/a/a.htm", {"ticker": "AAA"})

    assert result.status == "FETCHED"
    rows = list(read_jsonl([performance]))
    assert len(rows) == 1
    assert rows[0]["ticker"] == "AAA"
    assert rows[0]["request_seconds"] >= 0
    assert rows[0]["sha256_seconds"] >= 0
    assert rows[0]["gzip_seconds"] >= 0
    assert rows[0]["atomic_write_seconds"] >= 0
    assert client.last_performance == rows[0]


def test_fetch_counts_429_and_retry_wait(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("sec_pit.client.time.sleep", lambda _seconds: None)
    client = SecClient(
        user_agent="TSIS test test@example.com",
        store=ContentAddressedStore(tmp_path / "objects"),
        acquisition_log=tmp_path / "acquisition.jsonl",
        telemetry_log=tmp_path / "performance.jsonl",
        session=FakeSession(
            [
                FakeResponse(429, headers={"Retry-After": "2"}),
                FakeResponse(200),
            ]
        ),
        requests_per_second=10,
    )
    result = client.fetch("https://example.test/retry.htm")

    assert result.status == "FETCHED"
    assert client.last_performance is not None
    assert client.last_performance["http_429_count"] == 1
    assert client.last_performance["retry_count"] == 1
    assert client.last_performance["retry_wait_seconds"] == 2.0


def test_fetch_does_not_retry_terminal_404(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("sec_pit.client.time.sleep", lambda _seconds: None)
    client = SecClient(
        user_agent="TSIS test test@example.com",
        store=ContentAddressedStore(tmp_path / "objects"),
        acquisition_log=tmp_path / "acquisition.jsonl",
        telemetry_log=tmp_path / "performance.jsonl",
        session=FakeSession([FakeResponse(404)]),
        requests_per_second=10,
    )
    result = client.fetch("https://example.test/missing.json")

    assert result.status == "FAILED"
    assert result.http_status == 404
    assert result.attempts == 1
    assert client.last_performance is not None
    assert client.last_performance["retry_count"] == 0
    assert client.last_performance["retry_wait_seconds"] == 0.0


def test_summary_identifies_http_bound_candidate() -> None:
    summary = summarize_document_performance(
        [
            {
                "status": "FETCHED",
                "bytes": 100,
                "retry_count": 0,
                "http_429_count": 0,
                "total_seconds": 10.0,
                "throttle_seconds": 1.0,
                "request_seconds": 8.0,
                "request_attempt_seconds": [8.0],
                "retry_wait_seconds": 0.0,
                "storage_seconds": 1.0,
                "sha256_seconds": 0.1,
                "gzip_seconds": 0.2,
                "atomic_write_seconds": 0.3,
            }
        ]
    )

    assert summary["provisional_bottleneck_candidate"] == "SEC_RATE_LIMIT_OR_NETWORK"
    assert summary["http_attempt_latency_seconds"]["p95"] == 8.0
    assert summary["downstream_stage_telemetry"]["parse"].startswith("NOT_APPLICABLE")


def test_live_resource_sample_writes_monitor_compatible_heartbeat(tmp_path: Path) -> None:
    state = {
        "status": "RUNNING",
        "stage": "PRIMARY_ACQUISITION",
        "current_index": 1,
        "total_count": 3,
    }
    sampler = LiveResourceTelemetry(
        run_root=tmp_path / "run",
        output_root=tmp_path,
        run_id="telemetry-test",
        interval_seconds=60,
        state_snapshot=lambda: state,
    )
    heartbeat = sampler.sample()

    persisted = json.loads((tmp_path / "run" / "heartbeat_latest.json").read_text(encoding="utf-8"))
    assert heartbeat["current_index"] == 1
    assert persisted["total_count"] == 3
    assert persisted["process_tree_count"] >= 1
    assert persisted["available_memory_gib"] > 0
    assert persisted["output_free_gib"] > 0
    assert sampler.last_sample["process_tree_rss_gib"] >= 0
    assert sampler.last_sample["available_memory_gib"] > 0


def test_sec_monitor_renders_live_domain_fields(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    sampler = LiveResourceTelemetry(
        run_root=run_root,
        output_root=tmp_path,
        run_id="monitor-test",
        interval_seconds=60,
        state_snapshot=lambda: {
            "status": "RUNNING",
            "stage": "PRIMARY_ACQUISITION",
            "current_index": 2,
            "total_count": 3,
            "current_item": "AAA:a2",
            "documents_per_minute": 12.5,
            "mib_per_minute": 3.25,
            "http_p95_ms": 42.0,
            "retry_count": 1,
            "http_429_count": 1,
        },
    )
    sampler.sample()
    monitor = ROOT / "scripts" / "sec_pit" / "monitor_authorized_primary_acquisition_v0_2.ps1"
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(monitor),
            "-RunRoot",
            str(run_root),
            "-Compact",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "progress=2/3" in completed.stdout
    assert "docs_min=12.5" in completed.stdout
    assert "http_p95_ms=42" in completed.stdout
    assert "http_429=1" in completed.stdout
