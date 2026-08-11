from __future__ import annotations

from typing import Any, Iterable

from sec_pit.extract import stable_id
from sec_pit.holders_v2 import build_holder_position_ledger_v0_8


_UNRESOLVED_STATES = {
    "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED",
    "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED",
}


def _group_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("instrument_id"),
        row.get("security_class_id"),
        row.get("accession_number"),
        row.get("eligible_from_session"),
    )


def build_holder_position_ledger_v0_9(
    observations: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Prefer an exact proxy management aggregate over its additive components."""
    rows, readout = build_holder_position_ledger_v0_8(observations)
    aggregates = {
        _group_key(row): row
        for row in rows
        if row.get("holder_category") == "AGGREGATE_GROUP"
    }
    suppressed = 0
    aggregate_used = 0
    affiliate_overlap_unresolved = 0
    for key, aggregate in aggregates.items():
        supported = aggregate.get("supported_issued_common_shares")
        aggregate["methodology_relevant"] = True
        if supported is None:
            aggregate["deduplication_state"] = (
                "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED"
            )
            aggregate["economic_position_id"] = None
            continue
        aggregate["economic_position_id"] = stable_id(
            "aggregate_officer_director_position_v0_1", *key, supported
        )
        aggregate["deduplication_state"] = (
            "AGGREGATE_OFFICER_DIRECTOR_POSITION_RESOLVED"
        )
        aggregate["owner_exclusion_eligible"] = True
        aggregate_used += 1
        for row in rows:
            if row is aggregate or _group_key(row) != key:
                continue
            if row.get("holder_category") == "OFFICER_OR_DIRECTOR":
                row["methodology_relevant"] = False
                row["economic_position_id"] = None
                row["owner_exclusion_eligible"] = False
                row["deduplication_state"] = (
                    "COMPONENT_SUPPRESSED_BY_MANAGEMENT_AGGREGATE"
                )
                suppressed += 1
            elif (
                float(supported) > 0
                and row.get("holder_category") == "EXPLICIT_AFFILIATE"
                and float(row.get("supported_issued_common_shares") or 0) > 0
            ):
                row["deduplication_state"] = (
                    "AGGREGATE_AFFILIATE_OVERLAP_UNRESOLVED"
                )
                row["economic_position_id"] = None
                affiliate_overlap_unresolved += 1

    unresolved = sum(
        row.get("methodology_relevant")
        and row.get("deduplication_state") in _UNRESOLVED_STATES
        for row in rows
    )
    relevant_positions = {
        row.get("economic_position_id")
        for row in rows
        if row.get("methodology_relevant") and row.get("economic_position_id")
    }
    readout.update(
        {
            "policy_id": "holder_methodology_scoped_economic_position_resolution_v0_9",
            "methodology_relevant_rows": sum(
                bool(row.get("methodology_relevant")) for row in rows
            ),
            "methodology_relevant_economic_positions": len(relevant_positions),
            "unresolved_methodology_relevant_rows": unresolved,
            "row_level_economic_position_resolution_complete": unresolved == 0,
            "aggregate_group_rows_used_as_baseline": aggregate_used,
            "aggregate_component_rows_suppressed": suppressed,
            "aggregate_affiliate_overlap_unresolved_rows": affiliate_overlap_unresolved,
            "temporal_baseline_overlap_resolution_authority": (
                "DAILY_FLOAT_RESOLVER"
            ),
            "status": "PASS_WITH_RESTRICTIONS" if rows and unresolved == 0 else "FAIL",
        }
    )
    return rows, readout
