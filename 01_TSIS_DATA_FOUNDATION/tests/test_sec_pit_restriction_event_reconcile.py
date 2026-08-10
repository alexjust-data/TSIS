from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.restriction_event_reconcile import (  # noqa: E402
    reconcile_assignment_restriction_events,
)


def _row(accession: str, form: str, *, conflict: bool = False) -> dict:
    return {
        "observation_id": accession,
        "cik": "1",
        "accession_number": accession,
        "form": form,
        "effective_at": "2024-08-26",
        "filing_accepted_at": "2024-08-27T00:00:00Z",
        "value": None if conflict else 100.0,
        "attributes": {
            "restriction_event_type": "EVENT",
            "source_numeric_conflict": conflict,
            "tradable_supply_confirmation": False,
        },
    }


def test_reconciliation_prefers_origin_8k_and_preserves_corroboration() -> None:
    rows, readout = reconcile_assignment_restriction_events(
        [_row("prospectus", "424B3"), _row("origin", "8-K")]
    )
    assert len(rows) == 1
    assert rows[0]["accession_number"] == "origin"
    assert rows[0]["source_accessions"] == ["origin", "prospectus"]
    assert rows[0]["corroboration_count"] == 2
    assert rows[0]["tradable_supply_confirmation"] is False
    assert readout["economic_event_rows"] == 1


def test_reconciliation_preserves_numeric_conflict() -> None:
    rows, readout = reconcile_assignment_restriction_events(
        [_row("origin", "8-K", conflict=True), _row("p", "424B3", conflict=True)]
    )
    assert rows[0]["source_numeric_conflict"] is True
    assert rows[0]["reconciliation_state"] == "SOURCE_NUMERIC_CONFLICT_PRESERVED"
    assert readout["source_numeric_conflict_events"] == 1
