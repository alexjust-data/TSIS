from __future__ import annotations

import pandas as pd

from src.data.ohlcv_1m_quote_guarded import (
    QuoteGuardConfig,
    apply_quote_guarded_repairs,
    build_quote_minute_envelope,
    detect_quote_guarded_repairs,
)


def test_quote_guard_detects_and_clips_impossible_ohlc() -> None:
    cfg = QuoteGuardConfig(bid_quantile=0.01, ask_quantile=0.99, tolerance_pct=0.0, abs_tolerance=0.0, min_quote_count=3)
    raw = pd.DataFrame(
        {
            "ticker": ["TWG"],
            "ts_utc": [pd.Timestamp("2026-01-20 13:13:00", tz="UTC")],
            "date": ["2026-01-20"],
            "year": [2026],
            "month": [1],
            "o": [8.20],
            "h": [11.05],
            "l": [4.04],
            "c": [8.25],
            "v": [1000],
            "vw": [10.50],
            "n": [10],
        }
    )
    quotes = pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp("2026-01-20 13:13:02", tz="UTC").value,
                pd.Timestamp("2026-01-20 13:13:15", tz="UTC").value,
                pd.Timestamp("2026-01-20 13:13:43", tz="UTC").value,
            ],
            "bid_price": [8.10, 8.12, 8.11],
            "ask_price": [8.40, 8.41, 8.39],
        }
    )

    envelope = build_quote_minute_envelope(quotes, config=cfg)
    repairs = detect_quote_guarded_repairs(raw, envelope, config=cfg, ticker="TWG")

    assert len(repairs) == 1
    row = repairs.iloc[0]
    assert row["repair_state"] == "quote_repairable_ohlc_vw_invalid"
    assert "high_above_quote_ask_cap" in row["repair_reason"]
    assert "low_below_quote_bid_floor" in row["repair_reason"]
    assert row["h_qg"] <= row["quote_ask_cap"]
    assert row["l_qg"] >= row["quote_bid_floor"]
    assert row["vw_quote_guarded_status"] == "invalid_not_repaired_from_quotes"


def test_apply_quote_guarded_repairs_preserves_volume_and_raw_columns() -> None:
    raw = pd.DataFrame(
        {
            "ticker": ["TWG"],
            "ts_utc": [pd.Timestamp("2026-01-20 13:13:00", tz="UTC")],
            "o": [8.20],
            "h": [11.05],
            "l": [4.04],
            "c": [8.25],
            "v": [1000],
        }
    )
    manifest = pd.DataFrame(
        {
            "ticker": ["TWG"],
            "ts_utc": [pd.Timestamp("2026-01-20 13:13:00", tz="UTC")],
            "o_qg": [8.20],
            "h_qg": [8.41],
            "l_qg": [8.10],
            "c_qg": [8.25],
            "repair_state": ["quote_repairable_ohlc"],
            "repair_reason": ["high_above_quote_ask_cap|low_below_quote_bid_floor"],
            "vw_quote_guarded_status": ["raw_preserved"],
        }
    )

    out = apply_quote_guarded_repairs(raw, manifest, preserve_raw=True)

    assert float(out.loc[0, "h"]) == 8.41
    assert float(out.loc[0, "l"]) == 8.10
    assert int(out.loc[0, "v"]) == 1000
    assert float(out.loc[0, "h_raw"]) == 11.05
    assert float(out.loc[0, "l_raw"]) == 4.04
    assert bool(out.loc[0, "quote_guarded_repair_applied"]) is True
