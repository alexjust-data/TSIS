from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
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
    "trade_eligibility_pilot_auditor",
    SCRIPTS / "audit_trading_activity_trade_eligibility_pilot.py",
)


def condition_rule(condition_id: int, effect: str) -> dict[str, str]:
    return {
        "condition_id": str(condition_id),
        "condition_name": f"condition-{condition_id}",
        "policy_review_state": "CANDIDATE_REVIEWED_FOR_PILOT",
        "activity_event_effect": effect,
        "share_volume_effect": effect,
        "dollar_volume_effect": effect,
        "causal_arrival_effect": effect,
        "price_path_effect": effect,
        "reason_code": f"CONDITION_{condition_id}",
    }


def test_audit_reads_physical_file_without_hive_partition_merge(tmp_path):
    physical = tmp_path / "TEST" / "year=2026" / "month=08" / "market.parquet"
    physical.parent.mkdir(parents=True)
    table = pa.table(
        {
            "ticker": ["TEST", "TEST"],
            "date": ["2026-08-06", "2026-08-06"],
            "timestamp": [
                datetime(2026, 8, 6, 14, 0),
                datetime(2026, 8, 6, 14, 0, 1),
            ],
            "price": [2.0, 2.1],
            "size": [100, 200],
            "exchange": [4, 4],
            "conditions": pa.array([[], [32]], type=pa.list_(pa.int64())),
            "year": [2026, 2026],
        }
    )
    pq.write_table(table, physical)

    sidecar = {
        "task_key": "TEST|2026-08-06|market",
        "ticker": "TEST",
        "trading_date": "2026-08-06",
        "session": "market",
        "acquisition_status": "DOWNLOADED_OK",
        "coverage_gate_state": "PASS_WITH_RESTRICTIONS",
        "physical_row_count": "2",
        "active_physical_file": str(physical),
    }
    matrix = {32: condition_rule(32, "DENY")}
    result, conditions, reasons = auditor.audit_file(sidecar, matrix)

    assert result["evaluated_row_count"] == 2
    assert result["activity_eligible_count"] == 1
    assert result["activity_ineligible_count"] == 1
    assert conditions == {32: 1}
    assert reasons["CONDITION_32"] == 1


def test_empty_acquisition_is_observed_zero_without_file_read():
    sidecar = {
        "task_key": "TEST|2026-08-07|market",
        "ticker": "TEST",
        "trading_date": "2026-08-07",
        "session": "market",
        "acquisition_status": "DOWNLOADED_EMPTY",
        "coverage_gate_state": "PASS_WITH_RESTRICTIONS",
        "physical_row_count": "0",
        "active_physical_file": "",
    }
    result, conditions, reasons = auditor.audit_file(sidecar, {})
    assert result["file_policy_state"] == "OBSERVED_ZERO_WITH_RESTRICTIONS"
    assert result["evaluated_row_count"] == 0
    assert not conditions
    assert not reasons
