from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.restriction_estimate import resolve_tradability_eligibility  # noqa: E402


def test_tradability_is_null_when_float_or_restriction_gates_are_open() -> None:
    rows, readout = resolve_tradability_eligibility(
        daily_float_rows=[{
            "instrument_id": "i",
            "session_date": "2025-01-02",
            "float_owner_exclusion_estimate_as_known": None,
            "estimation_state": "BLOCKED_BY_INPUT_GATES",
        }],
        restriction_events=[],
        restriction_coverage={
            "structured_extraction_complete": False,
            "condition_resolution_complete": False,
            "methodology_authorized": False,
        },
    )
    assert rows[0]["float_tradability_eligibility_estimate_as_known"] is None
    assert rows[0]["estimation_state"] == "BLOCKED_BY_INPUT_GATES"
    assert readout["non_null_tradability_rows"] == 0
    assert "OWNER_EXCLUSION_FLOAT_NOT_ADMITTED" in readout["blocker_codes"]

def test_tradability_distinguishes_partial_float_coverage() -> None:
    _, readout = resolve_tradability_eligibility(
        daily_float_rows=[
            {
                "instrument_id": "i",
                "session_date": "2025-01-02",
                "float_owner_exclusion_estimate_as_known": 9_000_000.0,
                "ownership_conflict_state": "SOURCE_CONFLICT_PRECEDENCE_APPLIED",
                "estimation_state": "CALCULATED_WITH_SOURCE_CONFLICT",
            },
            {
                "instrument_id": "i",
                "session_date": "2025-01-03",
                "float_owner_exclusion_estimate_as_known": None,
                "ownership_conflict_state": None,
                "estimation_state": "POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED",
            },
        ],
        restriction_events=[],
        restriction_coverage={
            "structured_extraction_complete": False,
            "condition_resolution_complete": False,
            "methodology_authorized": False,
        },
    )
    assert "OWNER_EXCLUSION_FLOAT_NOT_ADMITTED" not in readout["blocker_codes"]
    assert "OWNER_EXCLUSION_FLOAT_PARTIAL_COVERAGE" in readout["blocker_codes"]
    assert "OWNER_EXCLUSION_FLOAT_SOURCE_CONFLICT" in readout["blocker_codes"]