from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from sec_pit.extract import stable_id

FORM_AUTHORITY = {"8-K": 0, "8-K/A": 1, "424B3": 2}


def reconcile_assignment_restriction_events(
    rows: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        event_type = (row.get("attributes") or {}).get("restriction_event_type")
        if isinstance(event_type, str):
            grouped[(event_type, row.get("effective_at"))].append(row)

    reconciled: list[dict[str, Any]] = []
    for (event_type, effective_at), evidence in sorted(grouped.items()):
        evidence.sort(
            key=lambda row: (
                FORM_AUTHORITY.get(str(row.get("form", "")).upper(), 99),
                row.get("filing_accepted_at") or "",
                row.get("accession_number") or "",
            )
        )
        chosen = evidence[0]
        values = sorted({float(row["value"]) for row in evidence if row.get("value") is not None})
        numeric_conflict = (
            any(
                bool((row.get("attributes") or {}).get("source_numeric_conflict"))
                for row in evidence
            )
            or len(values) > 1
        )
        reconciled.append(
            {
                **chosen,
                "economic_event_id": stable_id(
                    "reconciled_assignment_restriction_event_v0_1",
                    chosen.get("cik"),
                    event_type,
                    effective_at,
                ),
                "source_accessions": sorted(
                    {row["accession_number"] for row in evidence if row.get("accession_number")}
                ),
                "corroborating_observation_ids": sorted(row["observation_id"] for row in evidence),
                "corroboration_count": len(evidence),
                "source_numeric_conflict": numeric_conflict,
                "reconciliation_state": (
                    "SOURCE_NUMERIC_CONFLICT_PRESERVED"
                    if numeric_conflict
                    else "RECONCILED_ORIGIN_WITH_CORROBORATION"
                ),
                "tradable_supply_confirmation": False,
            }
        )

    conflict_count = sum(row["source_numeric_conflict"] for row in reconciled)
    readout = {
        "status": "PASS_WITH_RESTRICTIONS" if reconciled else "BLOCKED_BY_INPUT_GATES",
        "source_observation_rows": sum(len(value) for value in grouped.values()),
        "economic_event_rows": len(reconciled),
        "source_numeric_conflict_events": conflict_count,
        "tradable_supply_confirmed_events": 0,
        "authority_policy": "8-K > 8-K/A > 424B3 > other",
    }
    return reconciled, readout
