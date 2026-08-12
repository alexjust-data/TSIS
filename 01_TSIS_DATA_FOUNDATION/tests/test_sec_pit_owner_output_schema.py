from __future__ import annotations

import sys
from pathlib import Path

import pyarrow.parquet as pq

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.run_no_network_owner_exclusion_probe import (  # noqa: E402
    DAILY_FLOAT_STATE_SCHEMA,
    write_parquet,
)


def _row(*, calculated: bool) -> dict:
    value = 80.0 if calculated else None
    return {
        "instrument_id": "instrument:test",
        "session_date": "2020-01-02",
        "schema_version": "sec_pit_resolved_daily_states_v0_2",
        "shares_outstanding_estimate_as_known": 100.0 if calculated else None,
        "float_owner_exclusion_estimate_as_known": value,
        "float_fraction_estimate_as_known": 0.8 if calculated else None,
        "float_percent_estimate_as_known": 80.0 if calculated else None,
        "unique_supported_excluded_shares": 20.0 if calculated else None,
        "methodology_id": "test_v0_1",
        "ownership_baseline_accession": "0000000000-20-000001" if calculated else None,
        "ownership_baseline_eligible_from_session": "2020-01-02" if calculated else None,
        "ownership_update_observation_count": 0,
        "ownership_update_latest_transaction_date": None,
        "ownership_conflict_state": None,
        "estimation_state": "CALCULATED" if calculated else "BLOCKED",
        "blocker_codes": [] if calculated else ["SHARES_OUTSTANDING_UNAVAILABLE"],
    }


def test_daily_float_parquet_schema_is_stable_when_values_are_all_null(tmp_path: Path) -> None:
    calculated = tmp_path / "calculated.parquet"
    blocked = tmp_path / "blocked.parquet"
    write_parquet(calculated, [_row(calculated=True)], schema=DAILY_FLOAT_STATE_SCHEMA)
    write_parquet(blocked, [_row(calculated=False)], schema=DAILY_FLOAT_STATE_SCHEMA)
    calculated_schema = pq.read_schema(calculated)
    blocked_schema = pq.read_schema(blocked)
    assert calculated_schema == DAILY_FLOAT_STATE_SCHEMA
    assert blocked_schema == DAILY_FLOAT_STATE_SCHEMA
    assert calculated_schema == blocked_schema
