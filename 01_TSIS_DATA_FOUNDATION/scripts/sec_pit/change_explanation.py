from __future__ import annotations

from datetime import date
from typing import Any


def _cusip_for_session(session: str, intervals: list[dict[str, Any]]) -> str | None:
    target = date.fromisoformat(session[:10])
    for row in intervals:
        if date.fromisoformat(str(row["effective_from"])[:10]) <= target <= date.fromisoformat(
            str(row["effective_to"])[:10]
        ):
            return str(row["cusip"])
    return None


def build_daily_change_explanations(
    daily_rows: list[dict[str, Any]], cusip_intervals: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted(daily_rows, key=lambda row: str(row["session_date"]))
    explanations: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    previous_cusip: str | None = None
    for row in ordered:
        session = str(row["session_date"])[:10]
        cusip = _cusip_for_session(session, cusip_intervals)
        causes: list[str] = []
        if previous is None:
            causes.append("INITIAL_DAILY_STATE")
        else:
            if row.get("anchor_observation_id") != previous.get("anchor_observation_id"):
                causes.append("OS_ANCHOR_VINTAGE_CHANGE")
            if row.get("split_alignment_factor") != previous.get("split_alignment_factor"):
                causes.append("CORPORATE_ACTION_BASIS_CHANGE")
            if row.get("reference_price_observation_date") != previous.get(
                "reference_price_observation_date"
            ):
                causes.append("PRIOR_ELIGIBLE_RTH_CLOSE_UPDATE")
            if row.get("balance_sheet_measurement_at") != previous.get(
                "balance_sheet_measurement_at"
            ):
                causes.append("BALANCE_SHEET_VINTAGE_CHANGE")
            if cusip != previous_cusip:
                causes.append("CUSIP_INTERVAL_CHANGE")
        explanations.append(
            {
                "instrument_id": row.get("instrument_id"),
                "session_date": session,
                "change_causes": causes or ["NO_GOVERNED_INPUT_CHANGE"],
                "cusip_as_known": cusip,
                "os_anchor_observation_id": row.get("anchor_observation_id"),
                "reference_price_observation_date": row.get(
                    "reference_price_observation_date"
                ),
                "balance_sheet_measurement_at": row.get("balance_sheet_measurement_at"),
                "market_cap_state": row.get("market_cap_state"),
                "balance_sheet_state": row.get("balance_sheet_state"),
            }
        )
        previous = row
        previous_cusip = cusip
    unexplained = sum(item["change_causes"] == ["NO_GOVERNED_INPUT_CHANGE"] for item in explanations)
    return explanations, {
        "status": "PASS_WITH_RESTRICTIONS",
        "daily_rows": len(ordered),
        "explanation_rows": len(explanations),
        "no_governed_input_change_rows": unexplained,
        "manual_review_scope": "KEY_TRANSITIONS_AND_STRATIFIED_SAMPLE",
    }
