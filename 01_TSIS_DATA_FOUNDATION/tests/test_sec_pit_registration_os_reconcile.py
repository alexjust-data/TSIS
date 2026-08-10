from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.registration_os_reconcile import (  # noqa: E402
    reconcile_registration_components_to_os,
)


def _component(value: float, classification: str = "REPORTED_HELD") -> dict:
    return {
        "component_observation_id": "c",
        "instrument_id": "i",
        "component_classification": classification,
        "component_shares": value,
        "component_eligible_from_session": "2024-01-03",
        "tradable_supply_confirmation": False,
    }


def _os(value: float | None, conflict: str = "NO_KNOWN_CONFLICT") -> dict:
    return {
        "instrument_id": "i",
        "session_date": "2024-01-03",
        "shares_outstanding_estimate_as_known": value,
        "os_state": "OS_REPORTED_ANCHOR",
        "anchor_observation_id": "a",
        "source_conflict_state": conflict,
    }


def test_capacity_consistency_never_confirms_inclusion_or_tradability() -> None:
    rows, readout = reconcile_registration_components_to_os(
        component_condition_rows=[_component(100)],
        daily_os_rows=[_os(1_000)],
    )
    assert rows[0]["os_reconciliation_state"] == ("REPORTED_CURRENT_ISSUED_OS_CAPACITY_CONSISTENT")
    assert rows[0]["os_capacity_check_pass"] is True
    assert rows[0]["os_inclusion_confirmation"] is False
    assert rows[0]["tradable_supply_confirmation"] is False
    assert rows[0]["tradability_estimate_contribution"] is None
    assert readout["status"] == "PASS_WITH_RESTRICTIONS"


def test_component_exceeding_os_is_a_conflict() -> None:
    rows, readout = reconcile_registration_components_to_os(
        component_condition_rows=[_component(1_001)],
        daily_os_rows=[_os(1_000)],
    )
    assert rows[0]["os_reconciliation_state"] == ("REPORTED_CURRENT_ISSUED_EXCEEDS_OS_CONFLICT")
    assert readout["status"] == "BLOCKED_BY_INPUT_GATES"


def test_missing_os_and_non_current_components_remain_explicit() -> None:
    rows, readout = reconcile_registration_components_to_os(
        component_condition_rows=[
            _component(100),
            _component(200, "CONTINGENT_OR_FUTURE"),
        ],
        daily_os_rows=[],
    )
    assert len(rows) == 1
    assert rows[0]["os_reconciliation_state"] == ("REPORTED_CURRENT_ISSUED_OS_UNAVAILABLE")
    assert readout["unavailable_rows"] == 1
