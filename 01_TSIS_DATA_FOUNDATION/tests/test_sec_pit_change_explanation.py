from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.change_explanation import build_daily_change_explanations  # noqa: E402


def test_explains_split_and_cusip_transition() -> None:
    daily = [
        {
            "session_date": "2025-12-11",
            "anchor_observation_id": "a",
            "split_alignment_factor": 1.0,
            "reference_price_observation_date": "2025-12-10",
            "balance_sheet_measurement_at": "2025-09-30",
        },
        {
            "session_date": "2025-12-12",
            "anchor_observation_id": "a",
            "split_alignment_factor": 0.1,
            "reference_price_observation_date": "2025-12-11",
            "balance_sheet_measurement_at": "2025-09-30",
        },
    ]
    intervals = [
        {"cusip": "104932108", "effective_from": "2024-07-29", "effective_to": "2025-12-11"},
        {"cusip": "104932207", "effective_from": "2025-12-12", "effective_to": "2026-03-09"},
    ]
    rows, _ = build_daily_change_explanations(daily, intervals)
    assert "CORPORATE_ACTION_BASIS_CHANGE" in rows[1]["change_causes"]
    assert "CUSIP_INTERVAL_CHANGE" in rows[1]["change_causes"]
    assert "PRIOR_ELIGIBLE_RTH_CLOSE_UPDATE" in rows[1]["change_causes"]
