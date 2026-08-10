from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.presession_market_cap import build_presession_reference_market_cap  # noqa: E402

SPLIT = {
    "corporate_action_id": "split-1",
    "action_type": "split",
    "action_date": "2025-12-12",
    "source_system": "reference",
    "within_instrument_valid_window": True,
    "split_ratio": 0.1,
}


def test_pre_split_session_recovers_historical_price_basis() -> None:
    os_rows = [
        {
            "session_date": "2025-12-11",
            "shares_outstanding_estimate_as_known": 42_000_000,
        }
    ]
    prices = [{"date": "2025-12-10", "c": 2.95}]
    rows, _ = build_presession_reference_market_cap(os_rows, prices, [SPLIT])
    assert round(rows[0]["presession_reference_price_as_known"], 6) == 0.295
    assert round(rows[0]["presession_reference_market_cap_estimate_as_known"]) == 12_390_000


def test_split_session_aligns_prior_close_to_post_split_basis() -> None:
    os_rows = [
        {
            "session_date": "2025-12-12",
            "shares_outstanding_estimate_as_known": 4_200_000,
        }
    ]
    prices = [{"date": "2025-12-11", "c": 2.84}]
    rows, _ = build_presession_reference_market_cap(os_rows, prices, [SPLIT])
    assert round(rows[0]["presession_reference_price_as_known"], 6) == 2.84
    assert rows[0]["price_applied_corporate_action_ids"] == ["split-1"]
    assert round(rows[0]["presession_reference_market_cap_estimate_as_known"]) == 11_928_000


def test_missing_os_preserves_null_market_cap() -> None:
    os_rows = [
        {
            "session_date": "2025-12-11",
            "shares_outstanding_estimate_as_known": None,
        }
    ]
    prices = [{"date": "2025-12-10", "c": 2.95}]
    rows, readout = build_presession_reference_market_cap(os_rows, prices, [SPLIT])
    assert rows[0]["presession_reference_market_cap_estimate_as_known"] is None
    assert rows[0]["market_cap_state"] == "MARKET_CAP_UNAVAILABLE_OS"
    assert readout["market_cap_unavailable_rows"] == 1


def test_nan_os_preserves_null_market_cap() -> None:
    os_rows = [
        {
            "session_date": "2025-12-11",
            "shares_outstanding_estimate_as_known": float("nan"),
        }
    ]
    prices = [{"date": "2025-12-10", "c": 2.95}]
    rows, readout = build_presession_reference_market_cap(os_rows, prices, [SPLIT])
    assert rows[0]["presession_reference_market_cap_estimate_as_known"] is None
    assert rows[0]["market_cap_state"] == "MARKET_CAP_UNAVAILABLE_OS"
    assert readout["market_cap_non_null_rows"] == 0


def test_current_session_bar_is_never_used_as_presession_reference() -> None:
    os_rows = [
        {
            "session_date": "2025-12-12",
            "shares_outstanding_estimate_as_known": 4_200_000,
        }
    ]
    prices = [
        {"date": "2025-12-11", "c": 2.84},
        {"date": "2025-12-12", "c": 2.58},
    ]
    rows, _ = build_presession_reference_market_cap(os_rows, prices, [SPLIT])
    assert rows[0]["reference_price_observation_date"] == "2025-12-11"
    assert rows[0]["vendor_adjusted_prior_close"] == 2.84
