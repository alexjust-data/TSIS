from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


auditor = load_module(
    "population_target_pti_recovery_auditor",
    SCRIPTS / "audit_population_target_pti_recovery.py",
)


def test_recovery_audit_validates_legacy_semantics(tmp_path: Path) -> None:
    parquet_path = tmp_path / "population_target_pti.parquet"
    table = pa.table(
        {
            "date": pa.array([date(2025, 1, 2), date(2025, 1, 3)], type=pa.date32()),
            "ticker": ["TEST", "TEST"],
            "entity_id": ["entity:test", "entity:test"],
            "status": ["active", "active"],
            "close_t": [2.0, 2.5],
            "shares_outstanding_t": [10_000_000.0, 10_000_000.0],
            "shares_source": ["diluted", "diluted"],
            "shares_observed_date": pa.array(
                [date(2024, 12, 20), date(2024, 12, 20)], type=pa.date32()
            ),
            "shares_age_days": [13, 14],
            "market_cap_t": [20_000_000.0, 25_000_000.0],
            "is_small_cap_t": [True, True],
        }
    )
    pq.write_table(table, parquet_path)
    summary = {
        "metrics": {
            "rows_total": 2,
            "tickers_total": 1,
            "rows_classifiable": 2,
        }
    }
    summary_path = tmp_path / "summary.json"
    artifacts_path = tmp_path / "artifacts.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    artifacts_path.write_text(json.dumps({"output_parquet": "legacy"}), encoding="utf-8")

    result = auditor.audit(parquet_path, summary_path, artifacts_path)

    assert result["recovery_integrity_gate"] == "PASS"
    assert result["direct_session_start_selector_gate"] == "FAIL"
    assert result["physical_metrics"]["rows_total"] == 2
    assert result["physical_metrics"]["same_day_rows_in_ta3_numeric_bands"] == 2
    assert result["checks"]["grain_unique"]
    assert result["checks"]["ttl_enforcement_pass"]
    assert result["checks"]["legacy_2b_flag_semantics_pass"]


def test_recovery_audit_restricts_ticker_reuse_with_unique_entity_grain(
    tmp_path: Path,
) -> None:
    parquet_path = tmp_path / "ticker_reuse.parquet"
    table = pa.table(
        {
            "date": pa.array([date(2025, 1, 2), date(2025, 1, 2)], type=pa.date32()),
            "ticker": ["TEST", "TEST"],
            "entity_id": ["entity:old", "entity:new"],
            "status": ["inactive", "active"],
            "close_t": [2.0, 2.0],
            "shares_outstanding_t": [10_000_000.0, 8_000_000.0],
            "shares_source": ["diluted", "diluted"],
            "shares_observed_date": pa.array(
                [date(2024, 12, 20), date(2024, 12, 20)], type=pa.date32()
            ),
            "shares_age_days": [13, 13],
            "market_cap_t": [20_000_000.0, 16_000_000.0],
            "is_small_cap_t": [True, True],
        }
    )
    pq.write_table(table, parquet_path)
    summary_path = tmp_path / "summary.json"
    artifacts_path = tmp_path / "artifacts.json"
    summary_path.write_text(
        json.dumps(
            {"metrics": {"rows_total": 2, "tickers_total": 1, "rows_classifiable": 2}}
        ),
        encoding="utf-8",
    )
    artifacts_path.write_text("{}", encoding="utf-8")

    result = auditor.audit(parquet_path, summary_path, artifacts_path)

    assert result["recovery_integrity_gate"] == "PASS_WITH_RESTRICTIONS"
    assert not result["checks"]["grain_unique"]
    assert result["checks"]["entity_date_grain_unique"]
    assert len(result["ticker_date_collisions"]) == 1

def test_recovery_audit_fails_duplicate_grain(tmp_path: Path) -> None:
    parquet_path = tmp_path / "duplicate.parquet"
    table = pa.table(
        {
            "date": pa.array([date(2025, 1, 2), date(2025, 1, 2)], type=pa.date32()),
            "ticker": ["TEST", "TEST"],
            "entity_id": ["entity:test", "entity:test"],
            "status": ["active", "active"],
            "close_t": [2.0, 2.0],
            "shares_outstanding_t": [10_000_000.0, 10_000_000.0],
            "shares_source": ["diluted", "diluted"],
            "shares_observed_date": pa.array(
                [date(2024, 12, 20), date(2024, 12, 20)], type=pa.date32()
            ),
            "shares_age_days": [13, 13],
            "market_cap_t": [20_000_000.0, 20_000_000.0],
            "is_small_cap_t": [True, True],
        }
    )
    pq.write_table(table, parquet_path)
    summary_path = tmp_path / "summary.json"
    artifacts_path = tmp_path / "artifacts.json"
    summary_path.write_text(
        json.dumps({"metrics": {"rows_total": 2, "tickers_total": 1, "rows_classifiable": 2}}),
        encoding="utf-8",
    )
    artifacts_path.write_text("{}", encoding="utf-8")

    result = auditor.audit(parquet_path, summary_path, artifacts_path)

    assert result["recovery_integrity_gate"] == "FAIL"
    assert not result["checks"]["grain_unique"]
