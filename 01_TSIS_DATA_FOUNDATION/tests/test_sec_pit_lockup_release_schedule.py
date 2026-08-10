from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.lockup_release_schedule import (  # noqa: E402
    extract_lockup_release_schedule,
    resolve_lockup_lot_on_session,
    resolve_lockup_release_conditions,
)


def test_release_schedule_preserves_new_restriction() -> None:
    payload = b"""<table><tr><th>Sponsor Member Party</th><th>Shares Released from Lockup</th></tr>
    <tr><td>Pat Wilkison</td><td>97500</td></tr><tr><td>Amit Yoran</td><td>195000</td></tr>
    <tr><td>Total</td><td>292500</td></tr></table>"""
    rows, readout = extract_lockup_release_schedule(payload)
    assert readout["calculated_total"] == 292_500
    assert rows[0]["maximum_adv_percent"] == 25.0
    assert rows[0]["tradable_supply_confirmation"] is False


def test_condition_confirmation_does_not_confirm_tradability() -> None:
    rows = [{"tradable_supply_confirmation": False}]
    resolved = resolve_lockup_release_conditions(
        rows, transfer_initiation_confirmed=True, confirmation_eligible_from_session="2024-11-15"
    )
    assert resolved[0]["prior_lockup_release_state"] == "CONDITIONS_SUPPORTED_AS_KNOWN"
    assert resolved[0]["tradable_supply_confirmation"] is False


def test_adv_expiry_does_not_confirm_other_tradability_gates() -> None:
    row = {
        "release_lot_id": "x",
        "holder_name_key": "h",
        "shares_released_from_prior_lockup_reported": 10,
        "agreement_eligible_from_session": "2024-08-27",
        "condition_resolution_eligible_from_session": "2024-11-15",
        "scheduled_end_date": "2025-03-14",
    }
    state = resolve_lockup_lot_on_session(row, "2025-03-14")
    assert (
        state["restriction_lifecycle_state"]
        == "ADV_RESTRICTION_EXPIRED_OTHER_TRADABILITY_GATES_UNRESOLVED"
    )
    assert state["tradable_supply_confirmation"] is False
