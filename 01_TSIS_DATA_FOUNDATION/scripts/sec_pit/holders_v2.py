from __future__ import annotations

from typing import Any, Iterable

from sec_pit.extract import stable_id
from sec_pit.holders import build_holder_position_ledger


_UNRESOLVED_STATES = {
    "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED",
    "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED",
}


def build_holder_position_ledger_v0_8(
    observations: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, readout = build_holder_position_ledger(observations)
    for row in rows:
        if row.get("holder_category") != "EXPLICIT_AFFILIATE":
            continue
        row["methodology_relevant"] = True
        supported = row.get("supported_issued_common_shares")
        if supported is None:
            row["deduplication_state"] = (
                "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED"
            )
            row["economic_position_id"] = None
            continue
        row["economic_position_id"] = stable_id(
            "explicit_affiliate_position_v0_1",
            row.get("instrument_id"),
            row.get("accession_number"),
            row.get("canonical_holder_id"),
            supported,
        )
        row["deduplication_state"] = "EXPLICIT_AFFILIATE_POSITION_RESOLVED"
        row["owner_exclusion_eligible"] = True

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
            "policy_id": "holder_methodology_scoped_economic_position_resolution_v0_8",
            "methodology_relevant_rows": sum(
                bool(row.get("methodology_relevant")) for row in rows
            ),
            "methodology_relevant_economic_positions": len(relevant_positions),
            "explicit_affiliate_rows": sum(
                row.get("holder_category") == "EXPLICIT_AFFILIATE" for row in rows
            ),
            "unresolved_methodology_relevant_rows": unresolved,
            "row_level_economic_position_resolution_complete": unresolved == 0,
            "economic_position_resolution_complete": False,
            "owner_exclusion_authorized": False,
            "status": "PASS_WITH_RESTRICTIONS" if rows and unresolved == 0 else "FAIL",
        }
    )
    return rows, readout
