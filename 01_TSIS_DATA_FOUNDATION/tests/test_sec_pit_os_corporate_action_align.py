from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.os_corporate_action_align import align_daily_os_to_splits  # noqa: E402


def test_pre_split_anchor_is_transformed_from_effective_session() -> None:
    daily = [
        {
            "session_date": "2025-12-12",
            "anchor_measurement_at": "2025-11-25",
            "shares_outstanding_estimate_as_known": 44_880_795,
            "os_state": "OS_STALE_ANCHOR",
        }
    ]
    splits = [
        {
            "corporate_action_id": "s",
            "action_type": "split",
            "action_date": "2025-12-12",
            "source_system": "reference",
            "within_instrument_valid_window": True,
            "split_ratio": 0.1,
        }
    ]
    rows, readout = align_daily_os_to_splits(daily, splits)
    assert rows[0]["shares_outstanding_estimate_as_known"] == 4_488_079.5
    assert rows[0]["os_state"] == "OS_SPLIT_TRANSFORMED_STALE_ANCHOR"
    assert readout["split_transformed_rows"] == 1


def test_post_split_anchor_is_not_transformed_again() -> None:
    daily = [
        {
            "session_date": "2026-04-20",
            "anchor_measurement_at": "2026-04-13",
            "shares_outstanding_estimate_as_known": 5_857_955,
            "os_state": "OS_REPORTED_ANCHOR",
        }
    ]
    splits = [
        {
            "corporate_action_id": "s",
            "action_type": "split",
            "action_date": "2025-12-12",
            "source_system": "reference",
            "within_instrument_valid_window": True,
            "split_ratio": 0.1,
        }
    ]
    rows, _ = align_daily_os_to_splits(daily, splits)
    assert rows[0]["shares_outstanding_estimate_as_known"] == 5_857_955
