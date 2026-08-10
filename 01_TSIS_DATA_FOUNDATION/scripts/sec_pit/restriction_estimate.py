from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def resolve_tradability_eligibility(
    *,
    daily_float_rows: Iterable[dict[str, Any]],
    restriction_events: Iterable[dict[str, Any]],
    restriction_coverage: dict[str, Any],
    methodology_id: str = "restriction_and_resale_eligibility_v0_1",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    float_rows = list(daily_float_rows)
    events = list(restriction_events)
    blockers: list[str] = []

    non_null_float_rows = [
        row for row in float_rows
        if row.get("float_owner_exclusion_estimate_as_known") is not None
    ]
    if not non_null_float_rows:
        blockers.append("OWNER_EXCLUSION_FLOAT_NOT_ADMITTED")
    elif len(non_null_float_rows) < len(float_rows):
        blockers.append("OWNER_EXCLUSION_FLOAT_PARTIAL_COVERAGE")
    if any(
        row.get("ownership_conflict_state")
        for row in non_null_float_rows
    ):
        blockers.append("OWNER_EXCLUSION_FLOAT_SOURCE_CONFLICT")
    if not restriction_coverage.get("structured_extraction_complete"):
        blockers.append("RESTRICTION_STRUCTURED_EXTRACTION_INCOMPLETE")
    if not restriction_coverage.get("condition_resolution_complete"):
        blockers.append("RESTRICTION_CONDITIONS_UNRESOLVED")
    if not restriction_coverage.get("methodology_authorized"):
        blockers.append("TRADABILITY_METHODOLOGY_NOT_AUTHORIZED")

    rows: list[dict[str, Any]] = []
    if blockers:
        for float_row in float_rows:
            rows.append({
                "instrument_id": float_row["instrument_id"],
                "session_date": float_row["session_date"],
                "float_owner_exclusion_estimate_as_known": float_row.get(
                    "float_owner_exclusion_estimate_as_known"
                ),
                "float_tradability_eligibility_estimate_as_known": None,
                "restricted_or_locked_shares_estimate_as_known": None,
                "methodology_id": methodology_id,
                "estimation_state": "BLOCKED_BY_INPUT_GATES",
                "blocker_codes": blockers,
            })
        return rows, {
            "methodology_id": methodology_id,
            "status": "BLOCKED_BY_INPUT_GATES",
            "blocker_codes": blockers,
            "daily_rows": len(rows),
            "non_null_tradability_rows": 0,
            "restriction_events_considered": len(events),
        }

    raise NotImplementedError(
        "Tradability arithmetic requires admitted restriction events and policy"
    )