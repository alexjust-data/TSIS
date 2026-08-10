from __future__ import annotations

from collections.abc import Iterable
from typing import Any

CURRENT_ISSUED_CLASSES = {
    "REPORTED_COMMON_STOCK_OFFER_COMPONENT",
    "REPORTED_HELD",
    "REPORTED_ISSUED",
    "REPORTED_TRANSFERRED",
}


def reconcile_registration_components_to_os(
    *,
    component_condition_rows: Iterable[dict[str, Any]],
    daily_os_rows: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Check reported-current components against causal O/S capacity.

    A passing capacity check is corroboration only. It does not prove that a
    component is included in a specific O/S anchor or is freely tradable.
    """
    os_by_instrument: dict[str, list[dict[str, Any]]] = {}
    for row in daily_os_rows:
        instrument_id = row.get("instrument_id")
        session_date = row.get("session_date")
        if isinstance(instrument_id, str) and isinstance(session_date, str):
            os_by_instrument.setdefault(instrument_id, []).append(row)
    for rows in os_by_instrument.values():
        rows.sort(key=lambda row: row["session_date"])

    output: list[dict[str, Any]] = []
    for component in component_condition_rows:
        classification = component.get("component_classification")
        if classification not in CURRENT_ISSUED_CLASSES:
            continue
        instrument_id = component.get("instrument_id")
        eligible_session = component.get("component_eligible_from_session")
        candidate_os_rows = [
            row
            for row in os_by_instrument.get(instrument_id, [])
            if isinstance(eligible_session, str) and row["session_date"] >= eligible_session
        ]
        os_row = candidate_os_rows[0] if candidate_os_rows else None
        component_shares = component.get("component_shares")
        os_value = os_row.get("shares_outstanding_estimate_as_known") if os_row else None
        source_conflict = os_row.get("source_conflict_state") if os_row else None

        if os_row is None or os_value is None:
            state = "REPORTED_CURRENT_ISSUED_OS_UNAVAILABLE"
        elif source_conflict != "NO_KNOWN_CONFLICT":
            state = "REPORTED_CURRENT_ISSUED_OS_SOURCE_CONFLICT"
        elif not isinstance(component_shares, int | float):
            state = "REPORTED_CURRENT_ISSUED_COMPONENT_VALUE_UNAVAILABLE"
        elif float(component_shares) > float(os_value):
            state = "REPORTED_CURRENT_ISSUED_EXCEEDS_OS_CONFLICT"
        else:
            state = "REPORTED_CURRENT_ISSUED_OS_CAPACITY_CONSISTENT"

        output.append(
            {
                **component,
                "os_reconciliation_session": (os_row.get("session_date") if os_row else None),
                "shares_outstanding_estimate_as_known": os_value,
                "os_state": os_row.get("os_state") if os_row else None,
                "os_anchor_observation_id": (
                    os_row.get("anchor_observation_id") if os_row else None
                ),
                "os_source_conflict_state": source_conflict,
                "os_reconciliation_state": state,
                "os_capacity_check_pass": state == "REPORTED_CURRENT_ISSUED_OS_CAPACITY_CONSISTENT",
                "os_inclusion_confirmation": False,
                "tradable_supply_confirmation": False,
                "tradability_estimate_contribution": None,
            }
        )

    state_counts = {
        state: sum(row["os_reconciliation_state"] == state for row in output)
        for state in sorted({row["os_reconciliation_state"] for row in output})
    }
    conflicts = sum("CONFLICT" in row["os_reconciliation_state"] for row in output)
    unavailable = sum(row["os_reconciliation_state"].endswith("UNAVAILABLE") for row in output)
    readout = {
        "status": (
            "PASS_WITH_RESTRICTIONS"
            if output and conflicts == 0 and unavailable == 0
            else "BLOCKED_BY_INPUT_GATES"
        ),
        "reported_current_component_rows": len(output),
        "state_counts": state_counts,
        "capacity_consistent_rows": sum(row["os_capacity_check_pass"] for row in output),
        "conflict_rows": conflicts,
        "unavailable_rows": unavailable,
        "os_inclusion_confirmed_rows": 0,
        "tradable_supply_confirmed_rows": 0,
        "interpretation": "OS_CAPACITY_CONSISTENCY_NOT_COMPONENT_INCLUSION",
    }
    return output, readout
