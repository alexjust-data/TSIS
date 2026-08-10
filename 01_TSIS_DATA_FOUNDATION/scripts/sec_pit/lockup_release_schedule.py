from __future__ import annotations

from datetime import date
from io import BytesIO
from typing import Any

import pandas as pd

from sec_pit.extract import stable_id


def _name(value: Any) -> str:
    return " ".join(str(value).replace(",", " ").lower().split())


def _number(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def extract_lockup_release_schedule(payload: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    table = None
    for candidate in pd.read_html(BytesIO(payload)):
        rendered = (
            " ".join(map(str, candidate.columns))
            + " "
            + " ".join(candidate.astype(str).to_numpy().ravel())
        )
        if "Shares" in rendered and "Released from Lockup" in rendered:
            table = candidate
            break
    if table is None:
        return [], {"status": "NOT_OBSERVABLE", "reason": "LOCKUP_RELEASE_SCHEDULE_NOT_FOUND"}

    holder_col = table.columns[0]
    numeric_cols = [col for col in table.columns if table[col].map(_number).notna().sum()]
    shares_col = max(numeric_cols, key=lambda col: table[col].map(_number).notna().sum())
    rows = []
    reported_total = None
    for _, source in table.iterrows():
        holder = str(source[holder_col]).strip()
        shares = _number(source[shares_col])
        if holder.lower() == "total":
            reported_total = shares
        elif holder.lower() != "nan" and shares is not None:
            rows.append(
                {
                    "release_lot_id": stable_id("lockup_release_lot_v0_1", _name(holder), shares),
                    "holder_name_reported": holder,
                    "holder_name_key": _name(holder),
                    "shares_released_from_prior_lockup_reported": shares,
                    "prior_lockup_release_state": "CONDITIONAL_ON_SIDE_LETTER_AND_TRANSFER_INITIATION",
                    "new_adv_restriction_state": "REPORTED_ACTIVE_UNTIL_EARLIEST_END_CONDITION",
                    "maximum_adv_percent": 25.0,
                    "scheduled_end_date": "2025-03-14",
                    "legend_removal_instruction_state": "REPORTED_INSTRUCTION_NOT_COMPLETION",
                    "tradable_supply_confirmation": False,
                }
            )
    calculated_total = sum(row["shares_released_from_prior_lockup_reported"] for row in rows)
    return rows, {
        "status": "PASS_WITH_RESTRICTIONS"
        if calculated_total == reported_total
        else "SOURCE_CONFLICT",
        "holder_rows": len(rows),
        "calculated_total": calculated_total,
        "reported_total": reported_total,
        "tradable_supply_confirmed_rows": 0,
    }


def resolve_lockup_release_conditions(
    rows: list[dict[str, Any]],
    *,
    transfer_initiation_confirmed: bool,
    confirmation_eligible_from_session: str | None,
) -> list[dict[str, Any]]:
    resolved = []
    for row in rows:
        item = dict(row)
        item["transfer_initiation_confirmed"] = transfer_initiation_confirmed
        item["condition_resolution_eligible_from_session"] = confirmation_eligible_from_session
        item["prior_lockup_release_state"] = (
            "CONDITIONS_SUPPORTED_AS_KNOWN"
            if transfer_initiation_confirmed and confirmation_eligible_from_session
            else "CONDITIONS_UNRESOLVED"
        )
        item["tradable_supply_confirmation"] = False
        resolved.append(item)
    return resolved


def resolve_lockup_lot_on_session(row: dict[str, Any], session_date: str) -> dict[str, Any]:
    session = date.fromisoformat(session_date)
    agreement_eligible = date.fromisoformat(row["agreement_eligible_from_session"])
    condition_eligible = date.fromisoformat(row["condition_resolution_eligible_from_session"])
    scheduled_end = date.fromisoformat(row["scheduled_end_date"])
    if session < agreement_eligible:
        state = "OUT_OF_SCOPE_BEFORE_PUBLIC_AGREEMENT"
    elif session < condition_eligible:
        state = "PRIOR_LOCKUP_RELEASE_CONDITIONS_UNRESOLVED"
    elif session < scheduled_end:
        state = "PRIOR_LOCKUP_RELEASE_SUPPORTED_ADV_RESTRICTION_ACTIVE"
    else:
        state = "ADV_RESTRICTION_EXPIRED_OTHER_TRADABILITY_GATES_UNRESOLVED"
    return {
        "release_lot_id": row["release_lot_id"],
        "holder_name_key": row["holder_name_key"],
        "session_date": session_date,
        "shares_released_from_prior_lockup_reported": row[
            "shares_released_from_prior_lockup_reported"
        ],
        "restriction_lifecycle_state": state,
        "tradable_supply_confirmation": False,
    }
