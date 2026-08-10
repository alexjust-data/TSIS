from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.resolver import resolve_daily_os  # noqa: E402


def observation(quality_state: str) -> dict:
    return {
        "observation_id": quality_state,
        "observation_type": "SHARES_OUTSTANDING_ANCHOR_CANDIDATE",
        "value": 10_000_000,
        "measurement_at": "2025-01-02",
        "filing_accepted_at": "2025-01-03T15:00:00Z",
        "eligible_from_session": "2025-01-06",
        "causality_state": "AVAILABILITY_SESSION_RESOLVED",
        "quality_state": quality_state,
    }


def test_candidate_cannot_produce_daily_os_state() -> None:
    rows = resolve_daily_os(
        instrument_id="i",
        sessions=[date(2025, 1, 6)],
        observations=[observation("CANDIDATE_REQUIRES_RECONCILIATION")],
    )
    assert rows[0].os_state == "OS_UNAVAILABLE"
    assert rows[0].shares_outstanding_estimate_as_known is None


def test_only_admitted_anchor_can_produce_daily_os_state() -> None:
    rows = resolve_daily_os(
        instrument_id="i",
        sessions=[date(2025, 1, 6)],
        observations=[observation("ADMITTED_OS_ANCHOR")],
    )
    assert rows[0].os_state == "OS_REPORTED_ANCHOR"
    assert rows[0].shares_outstanding_estimate_as_known == 10_000_000

