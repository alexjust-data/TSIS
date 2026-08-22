from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.build_4824_cohort_metadata_gate import (  # noqa: E402
    distribution,
    execute,
    projected_full_universe_bytes,
    sha256,
)


def test_distribution_reports_exact_percentiles_and_max() -> None:
    result = distribution(pd.Series([1, 2, 3, 4]))
    assert result == {"count": 4, "p50": 2.5, "p95": pytest.approx(3.85), "max": 4.0}


def test_projection_uses_observed_cohort_rate_without_claiming_representativeness() -> None:
    assert projected_full_universe_bytes(824_000, 824, 4824) == 4_824_000
    with pytest.raises(ValueError, match="positive"):
        projected_full_universe_bytes(1, 0, 4824)


def test_network_free_metadata_gate_builds_selection_and_projection(tmp_path: Path) -> None:
    pool_path = tmp_path / "cohort.parquet"
    full_order_path = tmp_path / "full_order.parquet"
    metadata_root = tmp_path / "metadata"
    ticker_root = metadata_root / "tickers" / "aaa"
    ticker_root.mkdir(parents=True)
    case = {
        "selection_order": 1,
        "ticker": "AAA",
        "cik": "0000000001",
        "instrument_id": "instrument:aaa",
        "name": "AAA Common Stock",
        "is_common_stock": True,
        "first_seen_date": pd.Timestamp("2016-01-01"),
        "last_observed_date": pd.Timestamp("2026-03-09"),
        "instrument_identity_reused_in_parent_universe": False,
        "instrument_identity_cik_conflict": False,
    }
    pd.DataFrame([case]).to_parquet(pool_path, index=False)
    pd.DataFrame([case]).to_parquet(full_order_path, index=False)
    pd.DataFrame(
        [
            {
                "cik": "0000000001",
                "accession_number": "0000000001-20-000001",
                "form": "10-K",
                "filing_date": "2020-02-01",
                "report_date": "2019-12-31",
                "acceptance_datetime": "2020-02-01T12:00:00",
                "primary_document": "a.htm",
                "primary_document_description": "10-K",
                "items": "",
                "is_xbrl": True,
                "is_inline_xbrl": True,
                "filing_size_bytes": 100,
                "metadata_source": "fixture",
                "primary_document_url": "https://example.test/a.htm",
            }
        ]
    ).to_parquet(ticker_root / "filing_inventory.parquet", index=False)
    (ticker_root / "profile.json").write_text(
        json.dumps({"ticker": "AAA", "cik": "0000000001", "filing_count": 1}),
        encoding="utf-8",
    )
    (metadata_root / "final_manifest.json").write_text(
        json.dumps(
            {
                "status": "COMPLETE",
                "completed_tickers": 1,
                "candidate_pool_sha256": sha256(pool_path),
            }
        ),
        encoding="utf-8",
    )
    performance = {
        "status": "FETCHED",
        "bytes": 100,
        "retry_count": 0,
        "http_429_count": 0,
        "total_seconds": 1.0,
        "throttle_seconds": 0.1,
        "request_seconds": 0.5,
        "request_attempt_seconds": [0.5],
        "retry_wait_seconds": 0.0,
        "storage_seconds": 0.2,
        "sha256_seconds": 0.05,
        "gzip_seconds": 0.05,
        "atomic_write_seconds": 0.1,
    }
    (metadata_root / "request_performance.jsonl").write_text(
        json.dumps(performance) + "\n", encoding="utf-8"
    )
    output = execute(
        Namespace(
            candidate_pool=pool_path,
            metadata_root=metadata_root,
            full_order=full_order_path,
            output=tmp_path / "gate",
            parent_universe_rows=4824,
        )
    )
    final = json.loads((output / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["metadata_gate"] == "PASS"
    assert final["probe_gate"] == "PASS"
    assert final["metadata_completeness"] == "1/1"
    assert final["selected_document_count"] == 1
    assert final["projected_full_universe_selected_filing_size_upper_bound_bytes"] == 482400
    assert final["download_authorization"] == "NOT_AUTHORIZED_PENDING_HUMAN_GATE"
