from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sec_pit.float_estimate import resolve_owner_exclusion_float


def resolve_owner_exclusion_float_v0_2(
    *,
    daily_os_rows: Iterable[dict[str, Any]],
    holder_ledger: Iterable[dict[str, Any]],
    ownership_coverage: dict[str, Any],
    holder_deduplication: dict[str, Any],
    methodology_authorized: bool,
    methodology_id: str = "officer_director_explicit_affiliate_v0_1",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    coverage = dict(ownership_coverage)
    coverage["structured_extraction_complete"] = bool(
        ownership_coverage.get("methodology_structured_extraction_complete")
    )
    coverage["blocker_codes"] = list(
        ownership_coverage.get("methodology_blocker_codes") or []
    )
    rows, readout = resolve_owner_exclusion_float(
        daily_os_rows=daily_os_rows,
        holder_ledger=holder_ledger,
        ownership_coverage=coverage,
        holder_deduplication=holder_deduplication,
        methodology_authorized=methodology_authorized,
        methodology_id=methodology_id,
    )
    readout["coverage_gate_semantics"] = (
        "methodology-relevant source families complete; broad institutional "
        "ownership may remain extraction-restricted"
    )
    readout["broad_structured_extraction_complete"] = bool(
        ownership_coverage.get("broad_structured_extraction_complete")
    )
    readout["methodology_structured_extraction_complete"] = bool(
        ownership_coverage.get("methodology_structured_extraction_complete")
    )
    return rows, readout
