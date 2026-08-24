# ruff: noqa: E402
from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.massive_sec_storage import (
    DuplicateWriterError,
    MassiveSecStorage,
    OutputWriterLock,
    file_sha256,
)


def _commit(storage: MassiveSecStorage, *, work_id: str = "a" * 64) -> None:
    payload = {
        "status": "OK",
        "request_id": "request-1",
        "results": [{"accession_number": "0001", "cik": "0000000001"}],
    }
    storage.commit_page(
        endpoint_id="edgar_index",
        dataset_directory="edgar_index",
        work_id=work_id,
        target_cik="0000000001",
        sanitized_url="https://api.massive.com/stocks/filings/vX/index?cik=0000000001",
        request_id="request-1",
        retrieved_at_utc="2026-08-22T00:00:00+00:00",
        response_bytes=json.dumps(payload, sort_keys=True).encode("utf-8"),
        results=payload["results"],
        next_url=None,
        http_status=200,
        attempts=1,
        retry_count=0,
        http_429_count=0,
        elapsed_seconds=0.1,
        observed_fields=("accession_number", "cik"),
    )


def test_page_commit_is_durable_and_hash_validated(tmp_path: Path) -> None:
    storage = MassiveSecStorage(tmp_path, "run-1")
    storage.prepare_topology(["edgar_index"])
    _commit(storage)

    receipt = storage.load_receipt("edgar_index", "a" * 64)

    assert receipt is not None
    assert receipt["status"] == "COMMITTED"
    assert receipt["result_count"] == 1
    assert receipt["observed_fields"] == ["accession_number", "cik"]
    assert Path(receipt["raw_object_path"]).is_file()
    assert Path(receipt["normalized_path"]).is_file()


def test_power_loss_after_receipt_before_ledger_is_recoverable(tmp_path: Path) -> None:
    storage = MassiveSecStorage(tmp_path, "run-power-loss")
    storage.prepare_topology(["edgar_index"])
    _commit(storage)
    storage.ledger_path.unlink()

    summary = storage.rebuild_request_ledgers()
    ledger_rows = pd.read_parquet(summary["request_ledger_parquet"])

    assert summary["receipt_count"] == 1
    assert storage.ledger_path.read_text(encoding="utf-8").count("\n") == 1
    assert len(ledger_rows) == 1
    assert file_sha256(Path(summary["request_ledger_parquet"])) == summary[
        "request_ledger_parquet_sha256"
    ]


def test_existing_normalized_work_id_cannot_change_content(tmp_path: Path) -> None:
    storage = MassiveSecStorage(tmp_path, "run-collision")
    storage.prepare_topology(["edgar_index"])
    _commit(storage)
    storage.receipt_path("edgar_index", "a" * 64).unlink()

    with pytest.raises(FileExistsError, match="different content"):
        storage.commit_page(
            endpoint_id="edgar_index",
            dataset_directory="edgar_index",
            work_id="a" * 64,
            target_cik="0000000001",
            sanitized_url="https://api.massive.com/stocks/filings/vX/index?cik=0000000001",
            request_id="request-2",
            retrieved_at_utc="2026-08-22T00:00:01+00:00",
            response_bytes=b'{"status":"OK","request_id":"request-2","results":[]}',
            results=[],
            next_url=None,
            http_status=200,
            attempts=1,
            retry_count=0,
            http_429_count=0,
            elapsed_seconds=0.1,
            observed_fields=(),
        )


def test_duplicate_live_writer_is_blocked(tmp_path: Path) -> None:
    first = OutputWriterLock(tmp_path, "run-first")
    second = OutputWriterLock(tmp_path, "run-second")
    first.acquire(allow_stale_takeover=False)
    try:
        with pytest.raises(DuplicateWriterError, match="live Massive SEC writer"):
            second.acquire(allow_stale_takeover=True)
    finally:
        first.release()


def test_resume_archives_same_host_stale_lock(tmp_path: Path) -> None:
    lock_path = tmp_path / "locks" / "massive_sec_acquisition.lock"
    lock_path.parent.mkdir(parents=True)
    lock_path.write_text(
        json.dumps(
            {
                "run_id": "dead-run",
                "host": socket.gethostname(),
                "pid": 2_147_483_647,
                "process_create_time": 0.0,
                "token": "dead-token",
            }
        ),
        encoding="utf-8",
    )
    resumed = OutputWriterLock(tmp_path, "resumed-run")
    resumed.acquire(allow_stale_takeover=True)
    try:
        assert resumed.acquired
        assert list((tmp_path / "locks").glob("*.stale.*.json"))
        assert json.loads(resumed.path.read_text(encoding="utf-8"))["pid"] == os.getpid()
    finally:
        resumed.release()
