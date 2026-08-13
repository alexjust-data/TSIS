import sys
from pathlib import Path

import pandas as pd


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.audit_sharded_variable_certification import (  # noqa: E402
    audit_daily_frames,
    select_cases,
    shard_for,
)


def test_shard_assignment_is_stable() -> None:
    assert shard_for("instrument", 4) == shard_for("instrument", 4)
    assert 0 <= shard_for("instrument", 4) < 4


def test_explicit_case_selection_is_complete_and_order_preserving() -> None:
    cases = [{"ticker": "AAA"}, {"ticker": "BBB"}, {"ticker": "CCC"}]
    assert select_cases(cases, ["ccc", "AAA"]) == [cases[0], cases[2]]


def test_explicit_case_selection_rejects_missing_ticker() -> None:
    cases = [{"ticker": "AAA"}]
    try:
        select_cases(cases, ["AAA", "MISSING"])
    except ValueError as exc:
        assert "MISSING" in str(exc)
    else:
        raise AssertionError("missing ticker must fail certification selection")


def test_daily_audit_checks_formula_units_causality_and_nulls() -> None:
    os_rows = pd.DataFrame(
        [{
            "instrument_id": "i",
            "session_date": "2025-01-03",
            "shares_outstanding_estimate_as_known": 100.0,
            "anchor_eligible_from_session": "2025-01-03",
        }]
    )
    float_rows = pd.DataFrame(
        [{
            "instrument_id": "i",
            "session_date": "2025-01-03",
            "shares_outstanding_estimate_as_known": 100.0,
            "unique_supported_excluded_shares": 10.0,
            "float_owner_exclusion_estimate_as_known": 90.0,
            "float_fraction_estimate_as_known": 0.9,
            "float_percent_estimate_as_known": 90.0,
            "ownership_baseline_eligible_from_session": "2025-01-03",
            "estimation_state": "CALCULATED",
            "blocker_codes_json": "[]",
        }]
    )
    assert audit_daily_frames(os_rows, float_rows)["all_checks_pass"] is True
