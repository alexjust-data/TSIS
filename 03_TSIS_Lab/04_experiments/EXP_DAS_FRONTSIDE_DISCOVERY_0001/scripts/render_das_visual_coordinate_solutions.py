
"""Render DAS visual inspection cases with three coordinate-safe solutions.

This script intentionally does not use the legacy notebook/Plotly annotation stack.
Every solution draws price marks in the same coordinate system as its candles:

1. Plotly native: candles and marks are Plotly data traces on the same x/y axes.
2. Matplotlib: candles and marks share the same Axes transform.
3. Canvas/PIL: candles and marks share the same explicit x_scale/y_scale functions.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageStat

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import plotly.graph_objects as go
from plotly.subplots import make_subplots

DAS_SCRIPT_DIR = Path(r"C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\scripts")
if str(DAS_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(DAS_SCRIPT_DIR))

import das_widgets as dw  # noqa: E402

DEFAULT_RUN_DIRS = [
    Path(r"C:\tmp\TSIS_DAS_smoke_semantics_v07_CYTO\das_scanner_appearance_20260706T080957Z"),
    Path(r"C:\tmp\TSIS_DAS_smoke_semantics_v07_KTTA\das_scanner_appearance_20260706T080956Z"),
    Path(r"C:\tmp\TSIS_DAS_smoke_semantics_v07_PRSO\das_scanner_appearance_20260706T080957Z"),
]
DEFAULT_OUTPUT_DIR = Path(r"C:\Users\AlexJ\TSIS_smoke_review")
DEFAULT_VISUAL_QUOTES_ROOT = Path(r"D:\quotes")
VISUAL_QUOTE_GUARD_MIN_QUOTES = 3
VISUAL_QUOTE_GUARD_BID_Q = 0.01
VISUAL_QUOTE_GUARD_ASK_Q = 0.99

GREEN = "#10b981"
RED = "#ef4444"
BLUE = "#2563eb"
DARK = "#111827"
ORANGE_BG = "#fde8c5"
GRID = "#e6edf7"

STYLE = {
    "scanner_seed": {"name": "momentum trigger", "color": "#111827", "marker": "circle"},
    "first_push_high": {"name": "first push high", "color": "#16a34a", "marker": "circle"},
    "first_dip_low": {"name": "first dip low", "color": "#dc2626", "marker": "circle"},
    "rebreak_confirmed": {"name": "rebreak confirmed", "color": "#2563eb", "marker": "x"},
    "fake_rebreak": {"name": "fake rebreak", "color": "#f59e0b", "marker": "x"},
}


@dataclass
class DasCase:
    row: dict
    df: pd.DataFrame
    ticker: str
    session_date: str
    candidate_id: str
    anchors: dict[str, dict[str, object]]
    prior_close: float
    y_min: float
    y_max: float


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "segoeui.ttf"]
    for name in names:
        path = Path(r"C:\Windows\Fonts") / name
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _clean(value):
    return dw._clean_value(value)


def _format_compact(value: object) -> str:
    v = _clean(value)
    if v is None:
        return "na"
    v = float(v)
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.0f}k"
    return f"{v:.0f}"


def _quotes_path_for_session(ticker: str, session_date: str, quotes_root: Path = DEFAULT_VISUAL_QUOTES_ROOT) -> Path | None:
    day = str(session_date)[:10]
    year = day[:4]
    month = int(day[5:7])
    day_num = int(day[8:10])
    candidates = [
        quotes_root / ticker.upper() / f"year={year}" / f"month={month:02d}" / f"day={day_num}" / "quotes.parquet",
        quotes_root / ticker.upper() / f"year={year}" / f"month={month:02d}" / f"day={day}" / "quotes.parquet",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _load_quotes_for_session(ticker: str, session_date: str) -> pd.DataFrame:
    path = _quotes_path_for_session(ticker, session_date)
    if path is None:
        return pd.DataFrame(columns=["minute_utc", "quote_bid_floor", "quote_ask_cap", "quote_count"])
    q = pd.read_parquet(path, columns=["timestamp", "bid_price", "ask_price"])
    if q.empty:
        return pd.DataFrame(columns=["minute_utc", "quote_bid_floor", "quote_ask_cap", "quote_count"])
    q["bid_price"] = pd.to_numeric(q["bid_price"], errors="coerce")
    q["ask_price"] = pd.to_numeric(q["ask_price"], errors="coerce")
    q = q[(q["bid_price"] > 0) & (q["ask_price"] > 0)].copy()
    if q.empty:
        return pd.DataFrame(columns=["minute_utc", "quote_bid_floor", "quote_ask_cap", "quote_count"])
    q["ts_utc_dt"] = pd.to_datetime(q["timestamp"], unit="ns", utc=True, errors="coerce")
    q = q.dropna(subset=["ts_utc_dt"])
    q["minute_utc"] = q["ts_utc_dt"].dt.floor("min")
    grouped = q.groupby("minute_utc", sort=True).agg(
        quote_bid_floor=("bid_price", lambda s: float(s.quantile(VISUAL_QUOTE_GUARD_BID_Q))),
        quote_ask_cap=("ask_price", lambda s: float(s.quantile(VISUAL_QUOTE_GUARD_ASK_Q))),
        quote_count=("ask_price", "size"),
    ).reset_index()
    grouped["source_quotes_path"] = str(path)
    return grouped


def _apply_visual_quote_guarded_view(df: pd.DataFrame, ticker: str) -> tuple[pd.DataFrame, dict[str, object]]:
    """Clip rendered OHLC to the per-minute quote envelope before visual audit.

    This is a visual-inspection bridge. It prevents raw 1m outlier wicks from
    driving scanner/push/dip/rebreak labels while the full-universe
    master_intraday quote-guarded table is not materialized for these tickers.
    """
    out = df.copy().reset_index(drop=True)
    summary: dict[str, object] = {
        "visual_price_source": "raw_1m_plus_quotes_q01_q99_visual_guard",
        "visual_quote_guarded_min_quotes": VISUAL_QUOTE_GUARD_MIN_QUOTES,
        "visual_quote_guarded_bid_q": VISUAL_QUOTE_GUARD_BID_Q,
        "visual_quote_guarded_ask_q": VISUAL_QUOTE_GUARD_ASK_Q,
        "visual_quote_guarded_changed_rows": 0,
        "visual_quote_guarded_eligible_rows": 0,
        "visual_quote_guarded_quotes_missing": False,
    }
    if out.empty or "session_date" not in out.columns:
        summary["visual_price_source"] = "raw_1m_no_visual_quote_guard_empty_df"
        return out, summary
    for col in ["px_o", "px_h", "px_l", "px_c"]:
        out[f"source_raw_{col}"] = pd.to_numeric(out[col], errors="coerce")
    out["minute_utc"] = pd.to_datetime(out["ts_utc_dt"] if "ts_utc_dt" in out.columns else out["ts_utc"], utc=True, errors="coerce").dt.floor("min")
    quote_frames: list[pd.DataFrame] = []
    missing_sessions: list[str] = []
    for session_date in sorted(set(out["session_date"].astype(str))):
        q = _load_quotes_for_session(ticker, session_date)
        if q.empty:
            missing_sessions.append(session_date)
        else:
            quote_frames.append(q)
    if not quote_frames:
        summary["visual_price_source"] = "raw_1m_no_visual_quotes_available"
        summary["visual_quote_guarded_quotes_missing"] = True
        summary["visual_quote_guarded_missing_sessions"] = ",".join(missing_sessions)
        return out, summary
    quotes = pd.concat(quote_frames, ignore_index=True).drop_duplicates(subset=["minute_utc"], keep="last")
    out = out.merge(quotes, on="minute_utc", how="left")
    eligible = (
        out["quote_count"].fillna(0).astype(float).ge(VISUAL_QUOTE_GUARD_MIN_QUOTES)
        & out["quote_bid_floor"].notna()
        & out["quote_ask_cap"].notna()
        & out["quote_bid_floor"].astype(float).gt(0)
        & out["quote_ask_cap"].astype(float).ge(out["quote_bid_floor"].astype(float))
    )

    raw_close = pd.to_numeric(out["px_c"], errors="coerce")
    quote_mid = (
        pd.to_numeric(out["quote_bid_floor"], errors="coerce")
        + pd.to_numeric(out["quote_ask_cap"], errors="coerce")
    ) / 2.0
    ratio_rows = eligible & raw_close.gt(0) & quote_mid.gt(0)
    scale_ratio = np.nan
    if bool(ratio_rows.any()):
        ratios = (raw_close.loc[ratio_rows] / quote_mid.loc[ratio_rows]).replace([np.inf, -np.inf], np.nan).dropna()
        if not ratios.empty:
            scale_ratio = float(ratios.median())
    summary["visual_quote_guarded_scale_ratio_median"] = None if pd.isna(scale_ratio) else float(scale_ratio)

    # If raw 1m and quotes are on different price scales, clipping would
    # destroy the chart. Keep raw prices and flag the case for data repair.
    if pd.notna(scale_ratio) and (scale_ratio > 3.0 or scale_ratio < (1.0 / 3.0)):
        summary["visual_price_source"] = "raw_1m_quote_guard_skipped_scale_mismatch"
        summary["visual_quote_guarded_scale_guard_triggered"] = True
        summary["visual_quote_guarded_eligible_rows"] = int(eligible.sum())
        summary["visual_quote_guarded_changed_rows"] = 0
        summary["visual_quote_guarded_quotes_missing"] = bool(missing_sessions)
        summary["visual_quote_guarded_missing_sessions"] = ",".join(missing_sessions)
        summary["visual_quote_guarded_source_quotes_paths"] = ";".join(sorted(set(out["source_quotes_path"].dropna().astype(str))))
        out["visual_quote_guarded_repair_applied"] = False
        out["visual_quote_guarded_eligible"] = eligible
        return out, summary

    summary["visual_quote_guarded_scale_guard_triggered"] = False
    before = out[["px_o", "px_h", "px_l", "px_c"]].apply(pd.to_numeric, errors="coerce").copy()
    for col in ["px_o", "px_h", "px_l", "px_c"]:
        vals = pd.to_numeric(out[col], errors="coerce")
        clipped = vals.clip(lower=out["quote_bid_floor"], upper=out["quote_ask_cap"])
        out.loc[eligible, col] = clipped.loc[eligible]
    # Preserve OHLC invariants after independent clipping.
    ohlc = out[["px_o", "px_h", "px_l", "px_c"]].apply(pd.to_numeric, errors="coerce")
    out["px_h"] = ohlc.max(axis=1)
    out["px_l"] = ohlc.min(axis=1)
    after = out[["px_o", "px_h", "px_l", "px_c"]].apply(pd.to_numeric, errors="coerce")
    changed = eligible & (before.round(10) != after.round(10)).any(axis=1)
    out["visual_quote_guarded_repair_applied"] = changed
    out["visual_quote_guarded_eligible"] = eligible
    out["vwap"] = pd.NA
    summary["visual_quote_guarded_changed_rows"] = int(changed.sum())
    summary["visual_quote_guarded_eligible_rows"] = int(eligible.sum())
    summary["visual_quote_guarded_quotes_missing"] = bool(missing_sessions)
    summary["visual_quote_guarded_missing_sessions"] = ",".join(missing_sessions)
    summary["visual_quote_guarded_source_quotes_paths"] = ";".join(sorted(set(out["source_quotes_path"].dropna().astype(str))))
    return out, summary


def _true_segments(mask: Iterable[bool]) -> list[tuple[int, int]]:
    values = list(bool(v) for v in mask)
    segments: list[tuple[int, int]] = []
    start: int | None = None
    for idx, value in enumerate(values):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            segments.append((start, idx - 1))
            start = None
    if start is not None:
        segments.append((start, len(values) - 1))
    return segments


def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _blend_rgb(bg: tuple[int, int, int], fg: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    return tuple(int(round(bg[i] * (1.0 - alpha) + fg[i] * alpha)) for i in range(3))

def _bar_x_for_ts(df: pd.DataFrame, ts_utc: object) -> int | None:
    if _clean(ts_utc) is None:
        return None
    try:
        target = pd.Timestamp(ts_utc)
        target = target.tz_localize("UTC") if target.tzinfo is None else target.tz_convert("UTC")
    except Exception:
        return None
    if "ts_utc_dt" in df.columns:
        s = df["ts_utc_dt"]
    else:
        s = pd.to_datetime(df["ts_utc"], utc=True)
    exact = df.index[s.eq(target)]
    if len(exact):
        return int(exact[0])
    nearest = (s - target).abs().idxmin()
    return int(nearest)


def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    out["bar_index"] = out.index.astype(int)
    close = pd.to_numeric(out["px_c"], errors="coerce")
    out["ema8_calc"] = close.ewm(span=8, adjust=False).mean()
    out["wilder8_calc"] = close.ewm(alpha=1/8, adjust=False).mean()
    if "vwap" not in out.columns or out["vwap"].isna().all():
        typical = (out["px_h"].astype(float) + out["px_l"].astype(float) + out["px_c"].astype(float)) / 3.0
        vol = out["v"].astype(float)
        out["vwap"] = (typical * vol).cumsum() / vol.cumsum().replace(0, np.nan)
    return out


def _trigger_time(row: dict) -> str:
    text = str(_clean(row.get("visual_momentum_gate_ts_et")) or _clean(row.get("visual_momentum_gate_ts_utc")) or "")
    import re
    m = re.search(r"\b(\d{1,2}:\d{2})(?::\d{2})?\b", text)
    suffix = " EDT" if "EDT" in text else " EST" if "EST" in text else " ET"
    return (m.group(1) + suffix) if m else "time na"


def _force_visual_gate_to_scanner_close(row: dict, df: pd.DataFrame) -> None:
    """For visual audit, scanner gate is the scanner candle close, not its wick high.

    das_widgets._visual_momentum_gate_fields may use first_push_high when the
    scanner timestamp and first_push_high timestamp share the same minute. That
    is useful for old labels, but wrong for auditing the scanner trigger point.
    """
    scanner_ts = _clean(row.get("scanner_trigger_ts_utc"))
    if scanner_ts is None:
        return
    scanner_price = None
    x = _bar_x_for_ts(df, scanner_ts)
    if x is not None:
        hit = df[df["bar_index"].astype(int).eq(int(x))]
        if not hit.empty:
            scanner_price = float(hit.iloc[0]["px_c"])
    if scanner_price is None:
        scanner_price = _clean(row.get("price_at_trigger")) or _clean(row.get("scanner_trigger_price"))
    if scanner_price is None:
        return
    scanner_volume = (
        _clean(row.get("premarket_volume_at_trigger"))
        or _clean(row.get("session_volume_at_trigger"))
        or _clean(row.get("momentum_trigger_volume"))
    )
    prior_close = _clean(row.get("prior_close"))
    prior_pct = None
    if prior_close is not None and float(prior_close) != 0:
        prior_pct = (float(scanner_price) - float(prior_close)) / float(prior_close) * 100.0
    row["visual_momentum_gate_ts_utc"] = scanner_ts
    row["visual_momentum_gate_ts_et"] = _clean(row.get("scanner_trigger_ts_et")) or scanner_ts
    row["visual_momentum_gate_price"] = float(scanner_price)
    row["visual_momentum_gate_volume"] = float(scanner_volume) if scanner_volume is not None else None
    row["visual_momentum_gate_prior_close_pct"] = prior_pct
    row["visual_momentum_gate_source"] = "scanner_gate_trigger_close"
    row["visual_momentum_gate_prior_close_value"] = prior_close
    row["visual_momentum_gate_prior_close_source"] = "candidate_prior_close"
    row["visual_momentum_gate_prior_close_formula"] = "(scanner_trigger_close - prior_close) / prior_close * 100"


def _series_ts_value(series: pd.Series, *names: str):
    for name in names:
        if name in series.index and pd.notna(series.get(name)):
            return series.get(name)
    return None


def _is_visual_green(row: pd.Series) -> bool:
    return float(row["px_c"]) > float(row["px_o"])


def _is_visual_red(row: pd.Series) -> bool:
    return float(row["px_c"]) < float(row["px_o"])


def _find_visual_first_push_scanner_anchored(
    premarket: pd.DataFrame,
    pm_open_price: float,
    config: dw.DasConfig,
    scanner_x: int | None,
) -> tuple[pd.Series | None, pd.Series | None, pd.Series | None]:
    """Find DAS first push/dip for scanner-driven visual inspection.

    Critical audit rule: when a scanner gate exists, the first red candle that
    starts the dip must be at or after the scanner gate. This prevents impossible
    charts where first_push/dip/rebreak are drawn before the system had actually
    detected the candidate.
    """
    if premarket.empty or pm_open_price <= 0:
        return None, None, None
    if scanner_x is None:
        return dw._find_first_push(premarket, pm_open_price, config)

    push_threshold = pm_open_price * (1.0 + config.push_label_pct / 100.0)
    threshold_rows = premarket[premarket["px_h"].astype(float) >= push_threshold]
    threshold_rows_before_gate = threshold_rows[threshold_rows["bar_index"].astype(int) <= int(scanner_x)]
    if threshold_rows_before_gate.empty:
        threshold_rows_before_gate = threshold_rows
    if threshold_rows_before_gate.empty:
        return None, None, None

    first_threshold_row = threshold_rows_before_gate.iloc[0]
    threshold_pos = int(first_threshold_row.name)
    awakening_row = dw._find_awakening_start(premarket, pm_open_price, threshold_pos)
    awakening_pos = int(awakening_row.name)

    first_green_pos: int | None = None
    for _, r in premarket.iloc[awakening_pos : max(threshold_pos, int(scanner_x)) + 1].iterrows():
        if _is_visual_green(r):
            first_green_pos = int(r.name)
            break
    if first_green_pos is None:
        return None, None, None

    first_red_pos: int | None = None
    threshold_reached = False
    for _, r in premarket.iloc[first_green_pos:].iterrows():
        if float(r["px_h"]) >= push_threshold:
            threshold_reached = True
        if int(r.name) < int(scanner_x):
            continue
        if threshold_reached and _is_visual_red(r):
            first_red_pos = int(r.name)
            break

    if first_red_pos is None:
        return premarket.loc[first_green_pos], None, None

    push_window = premarket.iloc[first_green_pos : first_red_pos + 1]
    if push_window.empty:
        return None, None, None
    first_push_high_row = premarket.loc[push_window["px_h"].astype(float).idxmax()]

    dip_end_pos = len(premarket)
    for _, r in premarket.iloc[first_red_pos + 1 :].iterrows():
        if _is_visual_green(r):
            dip_end_pos = int(r.name) + 1
            break
    dip_window = premarket.iloc[first_red_pos:dip_end_pos]
    if dip_window.empty:
        return premarket.loc[first_green_pos], first_push_high_row, None
    first_dip_low_row = premarket.loc[dip_window["px_l"].astype(float).idxmin()]
    return premarket.loc[first_green_pos], first_push_high_row, first_dip_low_row


def _override_visual_sequence_with_human_das_rule(row: dict, df: pd.DataFrame) -> None:
    """Recompute first push and first dip from 1m candles for visual audit.

    Scanner-driven rule:
    - scanner gate is the first moment the configured filter detects the ticker;
    - push start can be before the scanner gate, because that history is known at gate time;
    - first push high, first dip and rebreak must belong to the structure that is
      still alive at/after scanner gate, not to an already-finished older mini push.
    """
    pm_open_price = _clean(row.get("pm_open_price"))
    if pm_open_price is None:
        if df.empty:
            return
        pm_open_price = _clean(df.iloc[0].get("px_o"))
    if pm_open_price is None:
        return
    cfg = dw.DasConfig(
        push_label_pct=float(_clean(row.get("push_label_pct")) or 20.0),
        dip_label_pct=float(_clean(row.get("dip_label_pct")) or 3.0),
        momentum_trigger_pct=float(_clean(row.get("momentum_trigger_pct_threshold")) or 50.0),
    )
    scanner_x = _bar_x_for_ts(df, row.get("visual_momentum_gate_ts_utc"))
    push_start_row, first_push_high_row, first_dip_low_row = _find_visual_first_push_scanner_anchored(
        df, float(pm_open_price), cfg, scanner_x
    )
    if push_start_row is None or first_push_high_row is None:
        row["visual_sequence_source"] = "human_das_scanner_anchored_no_push"
        return
    row["visual_sequence_source"] = "human_das_scanner_anchored"
    row["first_push_start_ts_utc"] = _series_ts_value(push_start_row, "ts_utc_dt", "ts_utc")
    row["first_push_start_ts_et"] = _series_ts_value(push_start_row, "ts_et")
    row["first_push_start_price"] = float(_clean(push_start_row.get("px_l")) or _clean(push_start_row.get("px_o")) or _clean(push_start_row.get("px_c")))
    row["first_push_high_ts_utc"] = _series_ts_value(first_push_high_row, "ts_utc_dt", "ts_utc")
    row["first_push_high_ts_et"] = _series_ts_value(first_push_high_row, "ts_et")
    row["first_push_high"] = float(first_push_high_row["px_h"])
    row["pm_open_to_first_push_high_pct"] = (float(row["first_push_high"]) - float(pm_open_price)) / float(pm_open_price) * 100.0
    if first_dip_low_row is None:
        for key in ["first_dip_low", "first_dip_low_ts_utc", "first_dip_low_ts_et", "first_dip_depth_pct"]:
            row[key] = None
        row["visual_sequence_source"] = "human_das_scanner_anchored_no_dip"
        return
    row["first_dip_low_ts_utc"] = _series_ts_value(first_dip_low_row, "ts_utc_dt", "ts_utc")
    row["first_dip_low_ts_et"] = _series_ts_value(first_dip_low_row, "ts_et")
    row["first_dip_low"] = float(first_dip_low_row["px_l"])
    if float(row["first_push_high"]) > 0:
        row["first_dip_depth_pct"] = (float(row["first_push_high"]) - float(row["first_dip_low"])) / float(row["first_push_high"]) * 100.0


def _trigger_label(row: dict, bars_from_push_start: int | None = None) -> str:
    prior_pct = _clean(row.get("visual_momentum_gate_prior_close_pct"))
    price = _clean(row.get("visual_momentum_gate_price"))
    volume = _clean(row.get("visual_momentum_gate_volume"))
    mcap = _clean(row.get("market_cap"))
    thr = _clean(row.get("momentum_trigger_pct_threshold"))
    mcap_gate = "na"
    if mcap is not None:
        mcap_gate = "pass" if float(mcap) < 100_000_000 else "FAIL"
    price_gate = "na"
    if price is not None:
        price_gate = "pass" if 0.5 <= float(price) <= 20.0 else "FAIL"
    return "\n".join([
        f"scanner gate {_trigger_time(row)}",
        f"bars_from_push_start = {bars_from_push_start}" if bars_from_push_start is not None else "bars_from_push_start = na",
        f"prior close = {float(prior_pct):+.1f}%" if prior_pct is not None else "prior close = na",
        f"price = ${float(price):.4f}" if price is not None else "price = na",
        f"acc vol = {_format_compact(volume)}" if volume is not None else "acc vol = na",
        f"threshold = +{float(thr):.0f}%" if thr is not None else "threshold = na",
        f"mcap = {_format_compact(mcap)}" if mcap is not None else "mcap = na",
        f"mcap_gate = {mcap_gate} <100M",
        f"price_gate = {price_gate} $0.50-$20",
    ])

def _load_case(run_dir: Path, candidate_index: int = 0) -> DasCase:
    candidates = dw._load_candidates_from_run(run_dir)
    if candidates.empty:
        candidates = dw._load_partial_candidates_from_run(run_dir)
    if candidates.empty:
        raise RuntimeError(f"No candidates in {run_dir}")
    if candidate_index < 0 or candidate_index >= len(candidates):
        raise IndexError(f"candidate_index={candidate_index} outside candidates={len(candidates)} for {run_dir}")
    row = candidates.to_dict("records")[candidate_index]
    row["_render_position"] = candidate_index + 1
    df = dw._load_chart_window(
        row["ticker"],
        dw._candidate_event_ts_utc(row),
        str(dw.DEFAULT_DATA_ROOT),
        price_view="raw",
        vwap_source="calculated",
    )
    row = dw._enrich_candidate_from_chart_window(row, df)
    df = dw._premarket_window_for_event_day(df, row)
    df, visual_price_summary = _apply_visual_quote_guarded_view(df, str(row["ticker"]))
    df = _add_indicators(df)
    row = dict(row)
    row.update(visual_price_summary)
    row.update(dw._visual_momentum_gate_fields(row))
    _force_visual_gate_to_scanner_close(row, df)
    _override_visual_sequence_with_human_das_rule(row, df)
    prior_close = float(row["prior_close"])
    anchors: dict[str, dict[str, object]] = {}

    def add_anchor(signal: str, ts_key: str, price_key: str, label: str, y_override: object | None = None):
        ts = row.get(ts_key)
        price = row.get(price_key) if y_override is None else y_override
        x = _bar_x_for_ts(df, ts)
        if x is None or _clean(price) is None:
            return
        anchors[signal] = {"x": int(x), "y": float(price), "label": label, "ts": ts}

    push_start_ts = row.get("first_push_start_ts_utc") or row.get("awakening_start_ts_utc") or row.get("premarket_open_ts_utc") or row.get("visual_momentum_gate_ts_utc")
    push_start_x = _bar_x_for_ts(df, push_start_ts)
    momentum_x = _bar_x_for_ts(df, row.get("visual_momentum_gate_ts_utc"))
    first_push_x = _bar_x_for_ts(df, row.get("first_push_high_ts_utc"))
    first_dip_x = _bar_x_for_ts(df, row.get("first_dip_low_ts_utc"))
    # Rebreak visual inspection rule: recompute from rendered 1m bars.
    # A candle wick above first_push_high is only a rebreak attempt. Confirmation
    # requires a green breakout/recovery candle, close above level, and volume
    # above the prior local average. Important: the same candle that prints the
    # first_dip_low wick may also be the valid rebreak if it recovers and breaks.
    rebreak_x = None
    rebreak_volume = None
    rebreak_prior_volume_avg = None
    fake_rebreak_x = None
    fake_rebreak_volume = None
    fake_rebreak_prior_volume_avg = None
    fake_rebreak_reasons: list[str] = []
    if first_dip_x is not None and _clean(row.get("first_push_high")) is not None:
        level = float(row.get("first_push_high"))
        eps = max(abs(level) * 1e-9, 1e-8)
        after_dip = df[df["bar_index"].astype(int) >= int(first_dip_x)].copy()
        if not after_dip.empty:
            for _, rb_row in after_dip.iterrows():
                high_px = float(rb_row["px_h"])
                if high_px <= level + eps:
                    continue
                rb_idx = int(rb_row["bar_index"])
                local_prev = df[(df["bar_index"].astype(int) >= max(0, rb_idx - 5)) & (df["bar_index"].astype(int) < rb_idx)]
                prior_avg = float(local_prev["v"].astype(float).mean()) if not local_prev.empty else 0.0
                volume = float(rb_row["v"])
                close_px = float(rb_row["px_c"])
                open_px = float(rb_row["px_o"])
                reasons = []
                if close_px <= open_px:
                    reasons.append("not_green")
                if close_px <= level + eps:
                    reasons.append("close_not_above_level")
                if prior_avg > 0 and volume <= prior_avg:
                    reasons.append("volume_not_above_prior_avg")
                if not reasons:
                    rebreak_x = rb_idx
                    rebreak_volume = volume
                    rebreak_prior_volume_avg = prior_avg
                    row["visual_validated_rebreak_ts_utc"] = rb_row.get("ts_utc")
                    row["visual_validated_rebreak_price"] = level
                    row["visual_validated_rebreak_volume"] = rebreak_volume
                    row["visual_validated_rebreak_prior_volume_avg"] = rebreak_prior_volume_avg
                    row["visual_validated_rebreak_from_bars"] = True
                    break
                if fake_rebreak_x is None:
                    fake_rebreak_x = rb_idx
                    fake_rebreak_volume = volume
                    fake_rebreak_prior_volume_avg = prior_avg
                    fake_rebreak_reasons = reasons
                    row["visual_fake_rebreak_ts_utc"] = rb_row.get("ts_utc")
                    row["visual_fake_rebreak_price"] = level
                    row["visual_fake_rebreak_volume"] = fake_rebreak_volume
                    row["visual_fake_rebreak_prior_volume_avg"] = fake_rebreak_prior_volume_avg
                    row["visual_fake_rebreak_reasons"] = "+".join(fake_rebreak_reasons)
    row["visual_validated_rebreak_from_bars"] = bool(row.get("visual_validated_rebreak_from_bars", False))
    row["visual_fake_rebreak_from_bars"] = bool(fake_rebreak_x is not None)

    def bars_since(start_x: int | None, end_x: int | None) -> int | None:
        if start_x is None or end_x is None:
            return None
        return int(max(0, end_x - start_x + 1))

    add_anchor(
        "scanner_seed",
        "visual_momentum_gate_ts_utc",
        "visual_momentum_gate_price",
        _trigger_label(row, bars_since(push_start_x, momentum_x)),
    )
    push_pct = _clean(row.get("pm_open_to_first_push_high_pct"))
    first_push_label = "\n".join([
        "first push high",
        f"bars_from_push_start = {bars_since(push_start_x, first_push_x)}" if bars_since(push_start_x, first_push_x) is not None else "bars_from_push_start = na",
        f"push = {float(push_pct):+.1f}%" if push_pct is not None else "push = na",
        f"price = ${float(row.get('first_push_high')):.4f}" if _clean(row.get("first_push_high")) is not None else "price = na",
    ])
    add_anchor("first_push_high", "first_push_high_ts_utc", "first_push_high", first_push_label)

    first_push_high = _clean(row.get("first_push_high"))
    first_dip_low = _clean(row.get("first_dip_low"))
    dip_from_push = None
    if first_push_high is not None and first_dip_low is not None and float(first_push_high) != 0:
        dip_from_push = (float(first_dip_low) - float(first_push_high)) / float(first_push_high) * 100.0
    first_dip_label = "\n".join([
        "first dip low",
        f"bars_from_first_push = {bars_since(first_push_x, first_dip_x)}" if bars_since(first_push_x, first_dip_x) is not None else "bars_from_first_push = na",
        f"dip_from_firts_push = {float(dip_from_push):.1f}%" if dip_from_push is not None else "dip_from_firts_push = na",
        f"price = ${float(first_dip_low):.4f}" if first_dip_low is not None else "price = na",
    ])
    add_anchor("first_dip_low", "first_dip_low_ts_utc", "first_dip_low", first_dip_label)

    if rebreak_x is not None and first_push_high is not None:
        rebreak_label = "\n".join([
            "rebreak confirmed",
            f"bars_from_first_dip = {bars_since(first_dip_x, rebreak_x)}" if bars_since(first_dip_x, rebreak_x) is not None else "bars_from_first_dip = na",
            f"vol = {_format_compact(rebreak_volume)}",
            f"prior_vol_avg = {_format_compact(rebreak_prior_volume_avg)}",
            f"price = ${float(first_push_high):.4f}",
        ])
        anchors["rebreak_confirmed"] = {
            "x": int(rebreak_x),
            "y": float(first_push_high),
            "label": rebreak_label,
            "ts": row.get("visual_validated_rebreak_ts_utc"),
        }
    if fake_rebreak_x is not None and first_push_high is not None:
        fake_label = "\n".join([
            "fake rebreak",
            f"bars_from_first_dip = {bars_since(first_dip_x, fake_rebreak_x)}" if bars_since(first_dip_x, fake_rebreak_x) is not None else "bars_from_first_dip = na",
            f"vol = {_format_compact(fake_rebreak_volume)}",
            f"prior_vol_avg = {_format_compact(fake_rebreak_prior_volume_avg)}",
            f"reason = {'+'.join(fake_rebreak_reasons) if fake_rebreak_reasons else 'na'}",
        ])
        anchors["fake_rebreak"] = {
            "x": int(fake_rebreak_x),
            "y": float(first_push_high),
            "label": fake_label,
            "ts": row.get("visual_fake_rebreak_ts_utc"),
        }

    lows = [float(df["px_l"].min()), prior_close]
    highs = [float(df["px_h"].max()), prior_close]
    for a in anchors.values():
        lows.append(float(a["y"]))
        highs.append(float(a["y"]))
    y_low = min(lows)
    y_high = max(highs)
    span = max(y_high - y_low, y_high * 0.05, 0.01)
    y_min = y_low - span * 0.035
    y_max = y_high + span * 0.065
    return DasCase(
        row=row,
        df=df,
        ticker=str(row.get("ticker")),
        session_date=str(row.get("session_date")),
        candidate_id=str(row.get("candidate_id")),
        anchors=anchors,
        prior_close=prior_close,
        y_min=y_min,
        y_max=y_max,
    )

def _session_spans(df: pd.DataFrame) -> list[tuple[int, int]]:
    if "session_segment" not in df.columns:
        return [(0, len(df) - 1)]
    mask = df["session_segment"].astype(str).eq("premarket")
    if not mask.any():
        return []
    idx = list(df.index[mask])
    return [(int(min(idx)), int(max(idx)))]



def _visible_maxpush_label(case: DasCase) -> str:
    value = dw._visible_maxpush_pct(case.row)
    return f"{float(value):.4f}%" if value is not None and pd.notna(value) else "na"


def _notebook_das_title_lines(case: DasCase) -> list[str]:
    row = case.row
    state = "rebreak_confirmed" if "rebreak_confirmed" in case.anchors else "fake_rebreak_no_confirmation" if "fake_rebreak" in case.anchors else "no_valid_rebreak_in_window"
    maxpush = _visible_maxpush_label(case)
    first_push = _clean(row.get("pm_open_to_first_push_high_pct"))
    dip = _clean(row.get("first_dip_pct"))
    trigger = _clean(row.get("visual_momentum_gate_prior_close_pct"))
    line2 = f"event-day 03:30-10:00 NY detail | state={state} | maxpush={maxpush}"
    if first_push is not None:
        line2 += f" | first_push={float(first_push):+.1f}%"
    line3 = []
    if trigger is not None:
        line3.append(f"momentum_trigger={float(trigger):+.1f}%")
    if dip is not None:
        line3.append(f"dip_manifest={float(dip):.1f}%")
    line3.append(f"visual_rebreak_from_bars={row.get('visual_validated_rebreak_from_bars')}")
    line3.append(f"visual_fake_rebreak={row.get('visual_fake_rebreak_from_bars')}")
    source = row.get("visual_price_source")
    changed = row.get("visual_quote_guarded_changed_rows")
    scale_ratio = row.get("visual_quote_guarded_scale_ratio_median")
    if source:
        line3.append(f"visual_price_source={source}")
    if changed is not None:
        line3.append(f"qg_changed_rows={int(changed)}")
    if source and "scale_mismatch" in str(source) and scale_ratio not in (None, ""):
        try:
            line3.append(f"qg_scale_ratio={float(scale_ratio):.2f}")
        except (TypeError, ValueError):
            pass
    return [f"DAS {case.ticker} {case.session_date}", line2, " | ".join(line3)]

def _label_positions(case: DasCase) -> dict[str, tuple[float, float]]:
    df = case.df
    pm_spans = _session_spans(df)
    if pm_spans:
        x0, x1 = pm_spans[0]
    else:
        x0, x1 = 0, len(df) - 1
    order = ["scanner_seed", "first_push_high", "first_dip_low", "rebreak_confirmed", "fake_rebreak"]
    present = [s for s in order if s in case.anchors]
    width = max(x1 - x0, 1)
    xs = np.linspace(x0 + width * 0.12, x0 + width * 0.88, len(present)) if present else []
    y = case.prior_close + (case.y_max - case.y_min) * 0.045
    return {signal: (float(x), float(y)) for signal, x in zip(present, xs)}


def _plotly_box_style(signal: str) -> dict:
    color = STYLE[signal]["color"]
    fill = {
        "scanner_seed": "rgba(255,255,255,0.94)",
        "first_push_high": "rgba(240,253,244,0.94)",
        "first_dip_low": "rgba(254,242,242,0.94)",
        "rebreak_confirmed": "rgba(239,246,255,0.94)",
        "fake_rebreak": "rgba(255,251,235,0.96)",
    }[signal]
    return dict(font=dict(size=11, color=color), bgcolor=fill, bordercolor=color, borderwidth=1, borderpad=3)


def render_solution_1_plotly(case: DasCase, output_dir: Path) -> Path:
    df = case.df
    x = df["bar_index"]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.02)
    for start, end in _session_spans(df):
        fig.add_vrect(x0=start - 0.5, x1=end + 0.5, fillcolor=ORANGE_BG, opacity=0.75, line_width=0, row="all", col=1)
    fig.add_trace(go.Candlestick(x=x, open=df["px_o"], high=df["px_h"], low=df["px_l"], close=df["px_c"], increasing_line_color=GREEN, decreasing_line_color=RED, increasing_fillcolor="rgba(16,185,129,0.65)", decreasing_fillcolor="rgba(239,68,68,0.65)", name="1m candles", hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["vwap"], mode="lines", line=dict(color=BLUE, width=1.5), name="VWAP", hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["ema8_calc"], mode="lines", line=dict(color="#22c55e", width=1.2), name="EMA8", hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["wilder8_calc"], mode="lines", line=dict(color="#ef4444", width=1.2), name="Wilder8", hoverinfo="skip"), row=1, col=1)
    vol_colors = [GREEN if c >= o else RED for o, c in zip(df["px_o"], df["px_c"])]
    fig.add_trace(go.Bar(x=x, y=df["v"], marker_color=vol_colors, name="1m volume", hoverinfo="skip"), row=2, col=1)
    fig.add_hline(y=case.prior_close, line=dict(color="rgba(75,85,99,0.85)", width=1.2, dash="dot"), annotation_text="prior close", annotation_position="bottom right", row=1, col=1)
    fp = case.anchors.get("first_push_high")
    rb = case.anchors.get("rebreak_confirmed")
    fake_rb = case.anchors.get("fake_rebreak")
    line_rb = rb or fake_rb
    if fp and line_rb:
        fig.add_trace(go.Scatter(x=[0, fp["x"]], y=[fp["y"], fp["y"]], mode="lines", line=dict(color=STYLE["first_push_high"]["color"], dash="dot", width=2), name="first push high level", hoverinfo="skip"), row=1, col=1)
        fig.add_trace(go.Scatter(x=[fp["x"], line_rb["x"]], y=[fp["y"], fp["y"]], mode="lines", line=dict(color=STYLE["rebreak_confirmed" if rb else "fake_rebreak"]["color"], dash="dot", width=2), name="rebreak level", hoverinfo="skip"), row=1, col=1)
    symbol_map = {"circle": "circle", "x": "x", "diamond": "diamond"}
    for signal, anchor in case.anchors.items():
        style = STYLE[signal]
        fig.add_trace(go.Scatter(x=[anchor["x"]], y=[anchor["y"]], mode="markers", marker=dict(symbol=symbol_map[style["marker"]], size=20 if style["marker"] != "x" else 24, color=style["color"], line=dict(color="white", width=2)), name=style["name"], hoverinfo="skip"), row=1, col=1)
    label_pos = _label_positions(case)
    for signal, anchor in case.anchors.items():
        if signal not in label_pos:
            continue
        lx, ly = label_pos[signal]
        fig.add_annotation(x=lx, y=ly, text=str(anchor["label"]).replace("\n", "<br>"), showarrow=False, align="left", xanchor="center", yanchor="bottom", row=1, col=1, **_plotly_box_style(signal))
    fig.update_layout(title=f"SOLUTION 1 - PLOTLY NATIVE SAME COORDINATES | {case.ticker} {case.session_date}", template="plotly_white", height=1530, margin=dict(l=35, r=75, t=220, b=35), showlegend=True, legend=dict(orientation="h", y=1.02, x=0))
    fig.update_xaxes(range=[-0.5, len(df) - 0.5], fixedrange=True, row=1, col=1)
    fig.update_xaxes(range=[-0.5, len(df) - 0.5], fixedrange=True, row=2, col=1)
    fig.update_yaxes(range=[case.y_min, case.y_max], side="right", fixedrange=True, row=1, col=1)
    fig.update_yaxes(title_text="Volume", side="right", fixedrange=True, row=2, col=1)
    tick_step = max(len(df) // 10, 1)
    fig.update_xaxes(tickmode="array", tickvals=df["bar_index"].iloc[::tick_step], ticktext=df["ts_et"].iloc[::tick_step].dt.strftime("%H:%M").tolist(), title_text="New York time, observed 1m bars", row=2, col=1)
    out = output_dir / f"DAS_SOL1_plotly_native_{case.ticker}_{case.session_date}_visual.png"
    fig.write_image(str(out), width=1530, height=1530, scale=2)
    return out


def _draw_mpl_labels(ax, case: DasCase) -> None:
    for signal, (lx, ly) in _label_positions(case).items():
        if signal not in case.anchors:
            continue
        style = STYLE[signal]
        face = {"scanner_seed": "white", "first_push_high": "#f0fdf4", "first_dip_low": "#fef2f2", "rebreak_confirmed": "#eff6ff", "fake_rebreak": "#fffbeb"}[signal]
        ax.text(lx, ly, str(case.anchors[signal]["label"]), ha="center", va="bottom", fontsize=8.5, color=style["color"], bbox=dict(boxstyle="square,pad=0.25", facecolor=face, edgecolor=style["color"], linewidth=1.0, alpha=0.95), zorder=20)


def render_solution_2_matplotlib(case: DasCase, output_dir: Path) -> Path:
    df = case.df
    fig, (ax, av) = plt.subplots(2, 1, figsize=(15.3, 15.3), dpi=200, sharex=True, gridspec_kw={"height_ratios": [3, 1], "hspace": 0.03})
    fig.patch.set_facecolor("white")
    for a in (ax, av):
        a.grid(True, color=GRID, linewidth=0.8)
        a.set_facecolor("white")
    for start, end in _session_spans(df):
        ax.axvspan(start - 0.5, end + 0.5, color=ORANGE_BG, alpha=0.75, zorder=0)
        av.axvspan(start - 0.5, end + 0.5, color=ORANGE_BG, alpha=0.75, zorder=0)
    width = 0.58
    for _, r in df.iterrows():
        x = float(r["bar_index"])
        o, h, l, c = map(float, (r["px_o"], r["px_h"], r["px_l"], r["px_c"]))
        color = GREEN if c >= o else RED
        ax.vlines(x, l, h, color=color, linewidth=1.2, zorder=3)
        bottom = min(o, c)
        height = max(abs(c - o), (case.y_max - case.y_min) * 0.001)
        ax.add_patch(Rectangle((x - width / 2, bottom), width, height, facecolor=color, edgecolor=color, alpha=0.72, zorder=4))
        av.bar(x, float(r["v"]), color=color, width=width, alpha=0.72, zorder=2)
    ax.plot(df["bar_index"], df["vwap"], color=BLUE, linewidth=1.3, label="VWAP", zorder=5)
    ax.plot(df["bar_index"], df["ema8_calc"], color="#22c55e", linewidth=1.1, label="EMA8", zorder=5)
    ax.plot(df["bar_index"], df["wilder8_calc"], color="#ef4444", linewidth=1.1, label="Wilder8", zorder=5)
    ax.axhline(case.prior_close, color="#4b5563", linewidth=1.2, linestyle=(0, (1, 3)), zorder=2)
    ax.text(len(df) - 0.5, case.prior_close, "prior close", ha="right", va="bottom", fontsize=9, color="#4b5563")
    fp = case.anchors.get("first_push_high")
    rb = case.anchors.get("rebreak_confirmed")
    fake_rb = case.anchors.get("fake_rebreak")
    line_rb = rb or fake_rb
    if fp and line_rb:
        ax.hlines(fp["y"], -0.5, fp["x"], color=STYLE["first_push_high"]["color"], linewidth=1.6, linestyles=(0, (1, 3)), zorder=6)
        ax.hlines(fp["y"], fp["x"], rb["x"], color=STYLE["rebreak_confirmed"]["color"], linewidth=1.6, linestyles=(0, (1, 3)), zorder=6)
    for signal, anchor in case.anchors.items():
        style = STYLE[signal]
        marker = "x" if style["marker"] == "x" else "D" if style["marker"] == "diamond" else "o"
        if marker == "x":
            ax.scatter([anchor["x"]], [anchor["y"]], s=330, marker=marker, color=style["color"], linewidths=4.5, zorder=12)
        else:
            ax.scatter([anchor["x"]], [anchor["y"]], s=230, marker=marker, color=style["color"], edgecolors="white", linewidths=2.5, zorder=12)
    _draw_mpl_labels(ax, case)
    ax.set_ylim(case.y_min, case.y_max)
    ax.set_xlim(-0.5, len(df) - 0.5)
    ax.yaxis.tick_right()
    av.yaxis.tick_right()
    tick_step = max(len(df) // 10, 1)
    ticks = df["bar_index"].iloc[::tick_step].tolist()
    labels = df["ts_et"].iloc[::tick_step].dt.strftime("%H:%M").tolist()
    av.set_xticks(ticks)
    av.set_xticklabels(labels, rotation=0, fontsize=8)
    ax.set_title(f"SOLUTION 2 - MATPLOTLIB SINGLE AXES TRANSFORM | {case.ticker} {case.session_date}", loc="left", fontsize=13, color="#334155", pad=20)
    ax.legend(loc="upper left", ncol=3, fontsize=8, frameon=False)
    av.set_ylabel("Volume", fontsize=9)
    out = output_dir / f"DAS_SOL2_matplotlib_single_axis_{case.ticker}_{case.session_date}_visual.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return out


def _canvas_text_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, color: tuple[int, int, int], fill: tuple[int, int, int]) -> tuple[int, int, int, int]:
    lines = text.splitlines() or [""]
    # +2 px vs previous canvas labels.
    f1 = _font(32, True)
    f2 = _font(31, False)
    widths = []
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=f1 if i == 0 else f2)
        widths.append(bbox[2] - bbox[0])
    w = max(widths) + 28
    h = len(lines) * 36 + 24
    x, y = xy
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=color, width=3)
    ty = y + 9
    for i, line in enumerate(lines):
        draw.text((x + 14, ty), line, font=f1 if i == 0 else f2, fill=color)
        ty += 36
    return (x, y, x + w, y + h)


def _measure_canvas_text_box(text: str) -> tuple[int, int]:
    probe = Image.new("RGB", (10, 10), "white")
    draw = ImageDraw.Draw(probe)
    lines = text.splitlines() or [""]
    f1 = _font(32, True)
    f2 = _font(31, False)
    widths = []
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=f1 if i == 0 else f2)
        widths.append(bbox[2] - bbox[0])
    return max(widths) + 28, len(lines) * 36 + 24

def render_solution_3_canvas(case: DasCase, output_dir: Path) -> Path:
    df = case.df
    W = H = 3060
    left, right = 120, 145
    top, price_bottom = 370, 2245
    vol_top, vol_bottom = 2320, 2920
    plot_w = W - left - right
    x_min, x_max = -0.5, len(df) - 0.5
    y_min, y_max = case.y_min, case.y_max
    max_vol = max(float(df["v"].max()), 1.0)

    def xs(x: float) -> float:
        return left + (float(x) - x_min) / (x_max - x_min) * plot_w

    def ys(y: float) -> float:
        return price_bottom - (float(y) - y_min) / (y_max - y_min) * (price_bottom - top)

    def vs(v: float) -> float:
        return vol_bottom - float(v) / max_vol * (vol_bottom - vol_top)

    im = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(im)
    # Backgrounds, soft grid and right-side axes. Ticks use the same transforms as candles/volume.
    grid_rgb = (224, 232, 242)
    axis_font = _font(31)
    axis_fill = (75, 85, 99)
    for start, end in _session_spans(df):
        draw.rectangle((xs(start - 0.5), top, xs(end + 0.5), price_bottom), fill=(253, 232, 197))
        draw.rectangle((xs(start - 0.5), vol_top, xs(end + 0.5), vol_bottom), fill=(253, 232, 197))
    for tick in np.linspace(y_min, y_max, 8):
        y = ys(float(tick))
        draw.line((left, y, W - right, y), fill=grid_rgb, width=1)
        draw.text((W - right + 10, y - 18), f"{float(tick):.2f}", font=axis_font, fill=axis_fill)
    for tick in np.linspace(0, max_vol, 5):
        y = vs(float(tick))
        draw.line((left, y, W - right, y), fill=grid_rgb, width=1)
        draw.text((W - right + 10, y - 18), _format_compact(tick), font=axis_font, fill=axis_fill)
    draw.text((W - right + 10, vol_top - 42), "Volume", font=axis_font, fill=axis_fill)
    # Time axis: labels are placed using the same x-scale as candles.
    tick_positions = np.linspace(0, max(len(df) - 1, 0), min(10, max(len(df), 1))).astype(int)
    tick_positions = sorted(set(int(v) for v in tick_positions))
    time_font = _font(31)
    for idx in tick_positions:
        x = xs(float(idx))
        draw.line((x, top, x, price_bottom), fill=grid_rgb, width=1)
        draw.line((x, vol_top, x, vol_bottom), fill=grid_rgb, width=1)
        if 0 <= idx < len(df):
            ts = df.iloc[idx].get("ts_et")
            try:
                label = pd.Timestamp(ts).strftime("%H:%M")
            except Exception:
                label = str(ts)[11:16] if ts is not None else ""
            bbox = draw.textbbox((0, 0), label, font=time_font)
            tw = bbox[2] - bbox[0]
            draw.text((x - tw / 2, vol_bottom + 18), label, font=time_font, fill=axis_fill)
    axis_label = "New York time (ET), observed 1m bars"
    bbox = draw.textbbox((0, 0), axis_label, font=time_font)
    draw.text((left + plot_w / 2 - (bbox[2] - bbox[0]) / 2, vol_bottom + 62), axis_label, font=time_font, fill=axis_fill)
    title_font = _font(44, True)
    title_font_small = _font(39, False)
    title_y = 70
    for idx, line in enumerate(_notebook_das_title_lines(case)):
        draw.text((40, title_y), line, font=title_font if idx == 0 else title_font_small, fill=(51, 65, 85))
        title_y += 56 if idx == 0 else 50
    width_px = max(7, plot_w / max(len(df), 1) * 0.56)
    # Same EMA/Wilder regime logic as the original notebook/shared helper:
    # bullish when ema8 > wilder8, bearish when ema8 < wilder8.
    bullish = (df["ema8_calc"] > df["wilder8_calc"]).fillna(False).tolist()
    bearish = (df["ema8_calc"] < df["wilder8_calc"]).fillna(False).tolist()
    for mask, fill_rgb, alpha in [
        (bullish, (16, 185, 129), 0.18),
        (bearish, (239, 68, 68), 0.16),
    ]:
        for start, end in _true_segments(mask):
            if end <= start:
                continue
            segment = df.iloc[start:end + 1]
            upper = segment[["ema8_calc", "wilder8_calc"]].max(axis=1)
            lower = segment[["ema8_calc", "wilder8_calc"]].min(axis=1)
            pts_upper = [(xs(float(x)), ys(float(y))) for x, y in zip(segment["bar_index"], upper)]
            pts_lower = [(xs(float(x)), ys(float(y))) for x, y in zip(reversed(segment["bar_index"].tolist()), reversed(lower.tolist()))]
            draw.polygon(pts_upper + pts_lower, fill=_blend_rgb((253, 232, 197), fill_rgb, alpha))

    for _, r in df.iterrows():
        x = xs(float(r["bar_index"]))
        o, h, l, c = map(float, (r["px_o"], r["px_h"], r["px_l"], r["px_c"]))
        col = (16, 185, 129) if c >= o else (239, 68, 68)
        draw.line((x, ys(l), x, ys(h)), fill=col, width=3)
        y0, y1 = ys(o), ys(c)
        if abs(y1 - y0) < 2:
            y1 = y0 + 2
        draw.rectangle((x - width_px / 2, min(y0, y1), x + width_px / 2, max(y0, y1)), fill=col, outline=col)
        draw.rectangle((x - width_px / 2, vs(float(r["v"])), x + width_px / 2, vol_bottom), fill=col)
    # Lines. VWAP is continuous; EMA/Wilder are masked by bullish/bearish regime like the original.
    pts = [(xs(float(r["bar_index"])), ys(float(r["vwap"]))) for _, r in df.dropna(subset=["vwap"]).iterrows()]
    if len(pts) > 1:
        draw.line(pts, fill=(37, 99, 235), width=3)
    for mask, line_rgb in [(bullish, (22, 163, 74)), (bearish, (220, 38, 38))]:
        for start, end in _true_segments(mask):
            if end <= start:
                continue
            segment = df.iloc[start:end + 1]
            for col_name, width_line in [("ema8_calc", 3), ("wilder8_calc", 5)]:
                pts = [(xs(float(r["bar_index"])), ys(float(r[col_name]))) for _, r in segment.dropna(subset=[col_name]).iterrows()]
                if len(pts) > 1:
                    draw.line(pts, fill=line_rgb, width=width_line)
    prior_y = ys(case.prior_close)
    for x0 in np.arange(left, W - right, 18):
        draw.line((x0, prior_y, x0 + 8, prior_y), fill=(75, 85, 99), width=2)
    draw.text((W - right - 245, prior_y + 8), "prior close", font=_font(31), fill=(75, 85, 99))
    fp = case.anchors.get("first_push_high")
    rb = case.anchors.get("rebreak_confirmed")
    fake_rb = case.anchors.get("fake_rebreak")
    if fp:
        y = ys(float(fp["y"]))
        for x0 in np.arange(left, xs(float(fp["x"])), 18):
            draw.line((x0, y, x0 + 8, y), fill=(22, 163, 74), width=3)
        if fake_rb:
            for x0 in np.arange(xs(float(fp["x"])), xs(float(fake_rb["x"])), 18):
                draw.line((x0, y, x0 + 8, y), fill=(245, 158, 11), width=3)
        if rb:
            for x0 in np.arange(xs(float(fp["x"])), xs(float(rb["x"])), 18):
                draw.line((x0, y, x0 + 8, y), fill=(37, 99, 235), width=3)
    label_pos = _label_positions(case)
    # Marks use the same xs/ys functions as candles. If two signals share the
    # exact same candle/price, draw concentric marks on the same true center.
    marker_order = ["first_push_high", "first_dip_low", "fake_rebreak", "rebreak_confirmed", "scanner_seed"]
    marker_items = []
    for signal in marker_order:
        if signal not in case.anchors:
            continue
        a = case.anchors[signal]
        marker_items.append({
            "signal": signal,
            "anchor": a,
            "screen_x": xs(float(a["x"])),
            "screen_y": ys(float(a["y"])),
            "data_key": (int(a["x"]), round(float(a["y"]), 8)),
        })
    grouped: dict[tuple[int, float], list[dict[str, object]]] = {}
    for item in marker_items:
        grouped.setdefault(item["data_key"], []).append(item)

    def draw_circle_mark(x: float, y: float, color: tuple[int, int, int], radius: int, filled: bool) -> None:
        if filled:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=(255, 255, 255), width=6)
        else:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(255, 255, 255), width=12)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color, width=8)

    def draw_x_mark(x: float, y: float, color: tuple[int, int, int], radius: int) -> None:
        draw.line((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255), width=14)
        draw.line((x - radius, y + radius, x + radius, y - radius), fill=(255, 255, 255), width=14)
        draw.line((x - radius, y - radius, x + radius, y + radius), fill=color, width=9)
        draw.line((x - radius, y + radius, x + radius, y - radius), fill=color, width=9)

    for group in grouped.values():
        if not group:
            continue
        x = float(group[0]["screen_x"])
        y = float(group[0]["screen_y"])
        if len(group) == 1:
            signal = str(group[0]["signal"])
            style = STYLE[signal]
            color = _rgb(style["color"])
            if style["marker"] == "x":
                draw_x_mark(x, y, color, 27)
            elif style["marker"] == "diamond":
                r = 22
                draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=color)
            else:
                draw_circle_mark(x, y, color, 23 if signal == "scanner_seed" else 21, True)
            continue

        # Overlap case: every signal remains centered at the true coordinate.
        # Circles become visible concentric rings; the scanner remains a filled core.
        circles = [item for item in group if STYLE[str(item["signal"])] ["marker"] != "x"]
        crosses = [item for item in group if STYLE[str(item["signal"])] ["marker"] == "x"]
        ring_radii = [42, 32, 23, 14]
        for idx, item in enumerate(circles):
            signal = str(item["signal"])
            color = _rgb(STYLE[signal]["color"])
            is_core = signal == "scanner_seed" or idx == len(circles) - 1
            if is_core:
                draw_circle_mark(x, y, color, 16, True)
            else:
                draw_circle_mark(x, y, color, ring_radii[min(idx, len(ring_radii) - 1)], False)
        for item in crosses:
            signal = str(item["signal"])
            draw_x_mark(x, y, _rgb(STYLE[signal]["color"]), 31)
    # Boxes: one contiguous centered row; bottom edge sits just above prior close.
    label_order = ["scanner_seed", "first_push_high", "first_dip_low", "fake_rebreak", "rebreak_confirmed"]
    present = [signal for signal in label_order if signal in case.anchors]
    box_gap = 6
    measurements = [(signal, *_measure_canvas_text_box(str(case.anchors[signal]["label"]))) for signal in present]
    total_w = sum(w for _, w, _ in measurements) + box_gap * max(0, len(measurements) - 1)
    start_x = int(round((W - total_w) / 2))
    row_bottom = int(round(prior_y - 8))
    cursor = start_x
    for signal, w, h in measurements:
        style = STYLE[signal]
        color = _rgb(style["color"])
        fill = {
            "scanner_seed": (255, 255, 255),
            "first_push_high": (240, 253, 244),
            "first_dip_low": (254, 242, 242),
            "rebreak_confirmed": (239, 246, 255),
            "fake_rebreak": (255, 251, 235),
        }[signal]
        _canvas_text_box(draw, (int(cursor), int(row_bottom - h)), str(case.anchors[signal]["label"]), color, fill)
        cursor += w + box_gap
    position = case.row.get("_render_position")
    prefix = f"{int(position):04d}_" if position is not None else ""
    out = output_dir / f"DAS_SOL3_canvas_shared_scale_{prefix}{case.ticker}_{case.session_date}_visual.png"
    im.save(out)
    return out


def validate_png(path: Path) -> str:
    im = Image.open(path).convert("RGB")
    stat = ImageStat.Stat(im)
    std = [round(v, 2) for v in stat.stddev]
    if min(std) < 2:
        raise RuntimeError(f"blank_or_low_variance_image: {path} stddev={std}")
    return f"{path.name} size={im.size} stddev={std}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-dir", action="append")
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dirs = [Path(p) for p in args.run_dir] if args.run_dir else DEFAULT_RUN_DIRS
    outputs: list[Path] = []
    for run_dir in run_dirs:
        candidates = dw._load_candidates_from_run(run_dir)
        if candidates.empty:
            candidates = dw._load_partial_candidates_from_run(run_dir)
        if candidates.empty:
            raise RuntimeError(f"No candidates in {run_dir}")
        limit = min(max(int(args.limit), 1), len(candidates))
        for idx in range(limit):
            case = _load_case(run_dir, candidate_index=idx)
            outputs.append(render_solution_3_canvas(case, output_dir))
    for path in outputs:
        print(validate_png(path))
    print(f"outputs={len(outputs)} solution=3 limit={args.limit}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
