from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = (
    ROOT
    / "01_foundations"
    / "data_consumption_policies"
    / "trading_activity_wake_up_trade_condition_policy_candidate_v0_1.json"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = load_module(
    "trade_condition_matrix_builder",
    ROOT / "scripts" / "build_trading_activity_trade_condition_policy_matrix.py",
)
evaluator = load_module(
    "trade_eligibility_evaluator",
    ROOT / "scripts" / "evaluate_trading_activity_trade_eligibility.py",
)


@pytest.fixture()
def policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def snapshot_row(condition_id: int, name: str) -> dict[str, str]:
    return {
        "id": str(condition_id),
        "name": name,
        "type": "trade_thru_exempt" if condition_id == 41 else "sale_condition",
        "legacy": "True" if condition_id == 31 else "",
        "consolidated_updates_high_low": "True",
        "consolidated_updates_open_close": "True",
        "consolidated_updates_volume": "True",
    }


@pytest.fixture()
def matrix(policy):
    rows = [
        snapshot_row(rule["condition_id"], rule["expected_name"])
        for rule in policy["condition_rules"]
    ]
    rows.append(snapshot_row(1, "Regular Sale"))
    matrix_rows, summary = builder.build_matrix(rows, policy)
    assert summary["candidate_reviewed_condition_count"] == 14
    assert summary["known_but_unreviewed_condition_count"] == 1
    return {row["condition_id"]: row for row in matrix_rows}


def base_row(**overrides):
    row = {
        "ticker": "TEST",
        "date": "2026-08-06",
        "timestamp": "2026-08-06T15:00:00",
        "price": 2.5,
        "size": 100,
        "exchange": 4,
        "conditions": [],
    }
    row.update(overrides)
    return row


def evaluate(row, matrix, **overrides):
    kwargs = {"in_rth": True, "source_available": True}
    kwargs.update(overrides)
    return evaluator.evaluate_trade(row, matrix, **kwargs)


def test_empty_conditions_are_restricted_legacy_eligible(matrix):
    result = evaluate(base_row(), matrix)
    assert result["trade_activity_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert result["trade_volume_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert "NO_SPECIAL_CONDITION_REPORTED_LEGACY" in result["eligibility_reason_codes"]


def test_contemporaneous_condition_is_allowed_with_context(matrix):
    result = evaluate(base_row(conditions=[14]), matrix)
    assert result["trade_activity_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert result["trade_causal_arrival_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert "INTERMARKET_SWEEP_TRANSACTION" in result["eligibility_reason_codes"]


def test_odd_lot_is_activity_but_not_price_forming(matrix):
    result = evaluate(base_row(conditions=[37]), matrix)
    assert result["trade_activity_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert result["trade_volume_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert result["trade_price_forming_eligibility_state"] == "INELIGIBLE"


def test_qualifier_only_does_not_restrict_base_trade(matrix):
    result = evaluate(base_row(conditions=[41]), matrix)
    assert result["trade_activity_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
    assert result["trade_price_forming_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"


def test_most_restrictive_condition_wins(matrix):
    result = evaluate(base_row(conditions=[14, 32]), matrix)
    assert result["trade_activity_eligibility_state"] == "INELIGIBLE"
    assert result["trade_volume_eligibility_state"] == "INELIGIBLE"
    assert "OUT_OF_SEQUENCE_NOT_CAUSAL_ACTIVITY" in result["eligibility_reason_codes"]


@pytest.mark.parametrize("conditions", [[1], [999]])
def test_unreviewed_or_unknown_condition_fails_closed(matrix, conditions):
    result = evaluate(base_row(conditions=conditions), matrix)
    assert result["trade_row_policy_state"] == "UNKNOWN_FAIL_CLOSED"
    assert result["trade_activity_eligibility_state"] == "UNKNOWN_FAIL_CLOSED"


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"ticker": ""}, "INVALID_TICKER"),
        ({"date": "not-a-date"}, "INVALID_DATE"),
        ({"timestamp": "not-a-time"}, "INVALID_TIMESTAMP"),
        ({"price": 0}, "NONPOSITIVE_OR_INVALID_PRICE"),
        ({"size": -1}, "NONPOSITIVE_OR_INVALID_SIZE"),
        ({"exchange": "X"}, "INVALID_EXCHANGE"),
        ({"conditions": "14"}, "UNPARSABLE_CONDITIONS"),
    ],
)
def test_hard_checks_fail_closed(matrix, overrides, reason):
    result = evaluate(base_row(**overrides), matrix)
    assert result["trade_row_policy_state"] == "INELIGIBLE"
    assert reason in result["eligibility_reason_codes"]


def test_scope_and_source_gates_fail_closed(matrix):
    outside = evaluate(base_row(), matrix, in_rth=False)
    unavailable = evaluate(base_row(), matrix, source_available=False)
    assert "OUTSIDE_RTH_SCOPE" in outside["eligibility_reason_codes"]
    assert "SOURCE_UNAVAILABLE" in unavailable["eligibility_reason_codes"]


def test_exact_duplicates_are_flagged_but_not_silently_removed(matrix):
    result = evaluate(base_row(), matrix, exact_duplicate_research_flag=True)
    assert result["duplicate_research_flag"] == "EXACT_DUPLICATE_RESEARCH_FLAG"
    assert result["trade_activity_eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"


def test_policy_name_drift_fails_matrix_build(policy):
    source = []
    for rule in policy["condition_rules"]:
        name = "Unexpected Rename" if rule["condition_id"] == 14 else rule["expected_name"]
        source.append(snapshot_row(rule["condition_id"], name))
    with pytest.raises(ValueError, match="Condition name mismatch"):
        builder.build_matrix(source, policy)
