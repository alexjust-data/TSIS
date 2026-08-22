from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.audit_authorized_primary_acquisition_v0_1 import (  # noqa: E402
    reconcile_logs,
    summarize_plan,
    verify_cas_object,
)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_scope_is_exact_first_authorized_eligible_ticker() -> None:
    selection = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "cohort_selection_order": [1, 1, 2],
            "cik": ["1", "1", "2"],
            "instrument_id": ["i1", "i1", "i2"],
            "accession_number": ["a1", "a2", "b1"],
            "form": ["10-K", "4", "10-K"],
            "filing_date": ["2024-01-01", "2024-02-01", "2024-01-01"],
            "primary_document_url": [
                "https://www.sec.gov/a1.htm",
                "https://www.sec.gov/a2.xml",
                "https://www.sec.gov/b1.htm",
            ],
        }
    )
    gates = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "primary_document_acquisition_state": [
                "ELIGIBLE_FOR_REVIEW_NOT_AUTHORIZED",
                "ELIGIBLE_FOR_REVIEW_NOT_AUTHORIZED",
            ],
        }
    )
    authorization = {
        "allowed_tickers": ["AAA"],
        "allowed_ticker_count": 1,
        "planned_document_count": 2,
    }
    plan, summary, issues = summarize_plan(selection, gates, authorization)
    assert not issues
    assert [row["ticker"] for row in plan] == ["AAA", "AAA"]
    assert [row["selection_index"] for row in plan] == [1, 2]
    assert summary["blocked_or_unapproved_rows"] == 1


def test_reconciliation_treats_404_fallback_as_resolved_not_terminal_failure(
    tmp_path: Path,
) -> None:
    primary_1 = "https://www.sec.gov/Archives/edgar/data/1/0001/doc.htm"
    primary_2 = "https://www.sec.gov/Archives/edgar/data/1/0002/doc.htm"
    fallback_1 = "https://www.sec.gov/Archives/edgar/data/1/0001/0001.txt"
    plan = [
        {
            "selection_index": 1,
            "ticker": "AAA",
            "accession_number": "0001",
            "form": "4",
            "filing_year": "2001",
            "primary_document_url": primary_1,
            "logical_path": "primary/AAA/0001/doc.htm",
        },
        {
            "selection_index": 2,
            "ticker": "AAA",
            "accession_number": "0002",
            "form": "10-K",
            "filing_year": "2002",
            "primary_document_url": primary_2,
            "logical_path": "primary/AAA/0002/doc.htm",
        },
    ]
    acquisition = [
        {
            "url": primary_1,
            "logical_path": "primary/AAA/0001/doc.htm",
            "status": "FAILED",
            "http_status": 404,
            "bytes": 0,
        },
        {
            "url": fallback_1,
            "logical_path": "complete_submission_fallback/AAA/0001.txt",
            "status": "FETCHED",
            "http_status": 200,
            "bytes": 10,
            "sha256": "a" * 64,
            "object_path": "D:/objects/a.txt.gz",
        },
        {
            "url": primary_1,
            "logical_path": "primary/AAA/0001/doc.htm",
            "status": "FETCHED",
            "http_status": 200,
            "bytes": 10,
            "sha256": "a" * 64,
            "object_path": "D:/objects/a.txt.gz",
            "fallback_resolved_url": fallback_1,
            "fallback_policy_id": "policy",
        },
        {
            "url": primary_2,
            "logical_path": "primary/AAA/0002/doc.htm",
            "status": "FETCHED",
            "http_status": 200,
            "bytes": 20,
            "sha256": "b" * 64,
            "object_path": "D:/objects/b.htm.gz",
        },
    ]
    performance = [
        {
            "selection_index": 1,
            "ticker": "AAA",
            "accession_number": "0001",
            "url": primary_1,
            "status": "FAILED",
            "http_status": 404,
            "retry_count": 2,
            "http_429_count": 0,
            "total_seconds": 3.0,
        },
        {
            "selection_index": 1,
            "ticker": "AAA",
            "accession_number": "0001",
            "url": fallback_1,
            "status": "FETCHED",
            "http_status": 200,
            "retry_count": 0,
            "http_429_count": 0,
            "total_seconds": 1.0,
            "fallback_policy_id": "policy",
        },
        {
            "selection_index": 2,
            "ticker": "AAA",
            "accession_number": "0002",
            "url": primary_2,
            "status": "FETCHED",
            "http_status": 200,
            "retry_count": 1,
            "http_429_count": 0,
            "total_seconds": 2.0,
        },
    ]
    acquisition_path = tmp_path / "acquisition.jsonl"
    performance_path = tmp_path / "performance.jsonl"
    write_jsonl(acquisition_path, acquisition)
    write_jsonl(performance_path, performance)
    summary, final_records, fallbacks, issues = reconcile_logs(
        plan, acquisition_path, performance_path
    )
    assert not issues
    assert len(final_records) == 2
    assert len(fallbacks) == 1
    assert summary["performance_status_counts"] == {"FAILED": 1, "FETCHED": 2}
    assert summary["resolved_primary_404_fallbacks"] == 1
    assert summary["logical_terminal_failures"] == 0
    assert summary["performance_retry_total"] == 3
    assert summary["failed_primary_call_retries"] == 2
    assert summary["recalculated_bytes"] == 30


def test_full_cas_verification_hashes_uncompressed_payload(tmp_path: Path) -> None:
    payload = b"SEC primary evidence\n" * 50
    digest = hashlib.sha256(payload).hexdigest()
    object_root = tmp_path / "objects"
    object_path = (
        object_root
        / "sha256"
        / digest[:2]
        / digest[2:4]
        / f"{digest}.txt.gz"
    )
    object_path.parent.mkdir(parents=True)
    object_path.write_bytes(gzip.compress(payload, mtime=0))
    result = verify_cas_object(
        {
            "object_path": str(object_path),
            "sha256": digest,
            "bytes": len(payload),
        },
        object_root,
    )
    assert result["status"] == "PASS"
    assert result["actual_bytes"] == len(payload)
    object_path.write_bytes(gzip.compress(payload + b"corruption", mtime=0))
    corrupted = verify_cas_object(
        {
            "object_path": str(object_path),
            "sha256": digest,
            "bytes": len(payload),
        },
        object_root,
    )
    assert corrupted["status"] == "FAIL"
    assert "OBJECT_CONTENT_SHA_MISMATCH" in corrupted["error"]
