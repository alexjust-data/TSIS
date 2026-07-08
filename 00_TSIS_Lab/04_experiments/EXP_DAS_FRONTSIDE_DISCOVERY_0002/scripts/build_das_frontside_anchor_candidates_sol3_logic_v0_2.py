"""Build EXP_DAS_FRONTSIDE_DISCOVERY_0002 anchors with the SOL3 visual logic.

This is the 0002 port of the scanner-anchored human-DAS sequence used by
EXP_DAS_FRONTSIDE_DISCOVERY_0001/scripts/render_das_visual_coordinate_solutions.py.

Important semantics intentionally copied from SOL3:
- the scanner gate visual price is the scanner candle close;
- the first push/dip structure is anchored to the scanner gate;
- the first red that starts the dip must be at or after the scanner gate;
- rebreak confirmation requires green bar, close above first_push_high, and
  volume above the prior local 5-bar average.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_das_frontside_anchor_candidates_sol3_logic_v0_2"
CALCULATION_RULE = "sol3_human_das_scanner_anchored_v0_2"
NY = ZoneInfo("America/New_York")

DEFAULT_RUN_ROOT = Path(
    r"C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z"
)


@dataclass(frozen=True)
class DetectionConfig:
    session_start_et: str = "03:30"
    session_end_et: str = "10:00"
    push_label_pct: float = 20.0
    dip_label_pct: float = 3.0
    momentum_trigger_pct: float = 50.0
    rebreak_volume_lookback_bars: int = 5


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_hhmm(value: str) -> time:
    hh, mm = value.split(":")
    return time(int(hh), int(mm))


def clean(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def num(value: Any) -> float | None:
    value = clean(value)
    if value is None:
        return None
    try:
        out = float(value)
    except Exception:
        return None
    if not math.isfinite(out):
        return None
    return out


def fmt_ts(ts: Any) -> str | None:
    if ts is None:
        return None
    try:
        if pd.isna(ts):
            return None
    except Exception:
        pass
    try:
        return pd.Timestamp(ts).isoformat()
    except Exception:
        return str(ts)


def pct(new: float | None, old: float | None) -> float | None:
    if new is None or old is None:
        return None
    if not math.isfinite(float(new)) or not math.isfinite(float(old)) or float(old) == 0:
        return None
    return (float(new) / float(old) - 1.0) * 100.0


def first_existing(df: pd.DataFrame, names: list[str]) -> str:
    for name in names:
        if name in df.columns:
            return name
    raise ValueError(f"Missing expected columns: {names}")


def read_session_bars(source_file: Path, session_date: str, cfg: DetectionConfig) -> pd.DataFrame:
    bars = pd.read_parquet(source_file)
    if bars.empty:
        return pd.DataFrame()

    ts_col = first_existing(bars, ["ts_utc", "timestamp", "datetime"])
    col_o = first_existing(bars, ["o", "open", "px_o"])
    col_h = first_existing(bars, ["h", "high", "px_h"])
    col_l = first_existing(bars, ["l", "low", "px_l"])
    col_c = first_existing(bars, ["c", "close", "px_c"])
    col_v = first_existing(bars, ["v", "volume", "px_v"])

    out = bars.copy()
    out["ts_utc_dt"] = pd.to_datetime(out[ts_col], utc=True, errors="coerce").dt.floor("min")
    out = out.dropna(subset=["ts_utc_dt"]).copy()
    out["ts_et_dt"] = out["ts_utc_dt"].dt.tz_convert(NY)
    out["session_date_et"] = out["ts_et_dt"].dt.strftime("%Y-%m-%d")
    out["time_et"] = out["ts_et_dt"].dt.time

    start = parse_hhmm(cfg.session_start_et)
    end = parse_hhmm(cfg.session_end_et)
    mask = (
        out["session_date_et"].eq(str(session_date))
        & (out["time_et"] >= start)
        & (out["time_et"] <= end)
    )
    out = out.loc[mask].sort_values("ts_utc_dt").reset_index(drop=True)
    if out.empty:
        return out

    normalized = pd.DataFrame(
        {
            "ts_utc_dt": out["ts_utc_dt"],
            "ts_et_dt": out["ts_et_dt"],
            "ts_utc": out["ts_utc_dt"].map(fmt_ts),
            "ts_et": out["ts_et_dt"].map(fmt_ts),
            "session_date": out["session_date_et"],
            "time_et": out["time_et"].astype(str),
            "px_o": pd.to_numeric(out[col_o], errors="coerce"),
            "px_h": pd.to_numeric(out[col_h], errors="coerce"),
            "px_l": pd.to_numeric(out[col_l], errors="coerce"),
            "px_c": pd.to_numeric(out[col_c], errors="coerce"),
            "v": pd.to_numeric(out[col_v], errors="coerce").fillna(0.0),
        }
    )
    normalized = normalized.dropna(subset=["px_o", "px_h", "px_l", "px_c"]).reset_index(drop=True)
    normalized["bar_index"] = normalized.index.astype(int)

    # Compatibility aliases for the existing 0002 event schema.
    normalized["o"] = normalized["px_o"]
    normalized["h"] = normalized["px_h"]
    normalized["l"] = normalized["px_l"]
    normalized["c"] = normalized["px_c"]
    return normalized


def bar_x_for_ts(df: pd.DataFrame, ts_utc: Any) -> int | None:
    if clean(ts_utc) is None or df.empty:
        return None
    try:
        target = pd.Timestamp(ts_utc)
        target = target.tz_localize("UTC") if target.tzinfo is None else target.tz_convert("UTC")
        target = target.floor("min")
    except Exception:
        return None
    s = pd.to_datetime(df["ts_utc_dt"], utc=True, errors="coerce")
    exact = df.index[s.eq(target)]
    if len(exact):
        return int(exact[0])
    nearest = (s - target).abs().idxmin()
    return int(nearest)


def is_green(row: pd.Series) -> bool:
    return float(row["px_c"]) > float(row["px_o"])


def is_red(row: pd.Series) -> bool:
    return float(row["px_c"]) < float(row["px_o"])


def find_awakening_start(premarket: pd.DataFrame, pm_open_price: float | None, threshold_pos: int) -> pd.Series:
    if premarket.empty:
        raise ValueError("Cannot find awakening start in an empty premarket frame.")
    if pm_open_price is None or pm_open_price <= 0:
        return premarket.iloc[0]
    search = premarket.iloc[: threshold_pos + 1].copy()
    if search.empty:
        return premarket.iloc[0]
    awake_threshold = pm_open_price * 1.05
    awake_rows = search[search["px_h"].astype(float) >= awake_threshold]
    if awake_rows.empty:
        return search.iloc[0]
    first_awake_pos = int(awake_rows.iloc[0].name)
    lookback = search.iloc[max(0, first_awake_pos - 8) : first_awake_pos + 1]
    if lookback.empty:
        return awake_rows.iloc[0]
    low_idx = lookback["px_l"].astype(float).idxmin()
    return search.loc[low_idx]


def find_first_push_fallback(
    premarket: pd.DataFrame,
    pm_open_price: float | None,
    cfg: DetectionConfig,
) -> tuple[pd.Series | None, pd.Series | None, pd.Series | None]:
    if premarket.empty or pm_open_price is None or pm_open_price <= 0:
        return None, None, None

    push_threshold = pm_open_price * (1.0 + cfg.push_label_pct / 100.0)
    threshold_rows = premarket[premarket["px_h"].astype(float) >= push_threshold]
    if threshold_rows.empty:
        return None, None, None

    threshold_pos = int(threshold_rows.iloc[0].name)
    awakening_pos = int(find_awakening_start(premarket, pm_open_price, threshold_pos).name)

    first_green_pos: int | None = None
    for _, row in premarket.iloc[awakening_pos : threshold_pos + 1].iterrows():
        if is_green(row):
            first_green_pos = int(row.name)
            break
    if first_green_pos is None:
        return None, None, None

    threshold_reached = False
    first_red_pos: int | None = None
    current_high_row: pd.Series | None = None
    current_high = float("-inf")
    for _, row in premarket.iloc[first_green_pos:].iterrows():
        high = float(row["px_h"])
        if high > current_high:
            current_high = high
            current_high_row = row
        if high >= push_threshold:
            threshold_reached = True
        if is_red(row) and threshold_reached:
            first_red_pos = int(row.name)
            break
    if first_red_pos is None or current_high_row is None:
        return None, None, None

    push_window = premarket.iloc[first_green_pos : first_red_pos + 1]
    if push_window.empty:
        return None, None, None
    first_push_high_row = premarket.loc[push_window["px_h"].astype(float).idxmax()]

    dip_end_pos = len(premarket)
    for _, row in premarket.iloc[first_red_pos + 1 :].iterrows():
        if is_green(row):
            dip_end_pos = int(row.name) + 1
            break
    dip_window = premarket.iloc[first_red_pos:dip_end_pos]
    if dip_window.empty:
        return None, None, None
    first_dip_low_row = premarket.loc[dip_window["px_l"].astype(float).idxmin()]
    return premarket.loc[first_green_pos], first_push_high_row, first_dip_low_row


def find_visual_first_push_scanner_anchored(
    premarket: pd.DataFrame,
    pm_open_price: float,
    cfg: DetectionConfig,
    scanner_x: int | None,
) -> tuple[pd.Series | None, pd.Series | None, pd.Series | None]:
    if premarket.empty or pm_open_price <= 0:
        return None, None, None
    if scanner_x is None:
        return find_first_push_fallback(premarket, pm_open_price, cfg)

    push_threshold = pm_open_price * (1.0 + cfg.push_label_pct / 100.0)
    threshold_rows = premarket[premarket["px_h"].astype(float) >= push_threshold]
    threshold_rows_before_gate = threshold_rows[threshold_rows["bar_index"].astype(int) <= int(scanner_x)]
    if threshold_rows_before_gate.empty:
        threshold_rows_before_gate = threshold_rows
    if threshold_rows_before_gate.empty:
        return None, None, None

    threshold_pos = int(threshold_rows_before_gate.iloc[0].name)
    awakening_pos = int(find_awakening_start(premarket, pm_open_price, threshold_pos).name)

    first_green_pos: int | None = None
    for _, row in premarket.iloc[awakening_pos : max(threshold_pos, int(scanner_x)) + 1].iterrows():
        if is_green(row):
            first_green_pos = int(row.name)
            break
    if first_green_pos is None:
        return None, None, None

    first_red_pos: int | None = None
    threshold_reached = False
    for _, row in premarket.iloc[first_green_pos:].iterrows():
        if float(row["px_h"]) >= push_threshold:
            threshold_reached = True
        if int(row.name) < int(scanner_x):
            continue
        if threshold_reached and is_red(row):
            first_red_pos = int(row.name)
            break

    if first_red_pos is None:
        return premarket.loc[first_green_pos], None, None

    push_window = premarket.iloc[first_green_pos : first_red_pos + 1]
    if push_window.empty:
        return None, None, None
    first_push_high_row = premarket.loc[push_window["px_h"].astype(float).idxmax()]

    dip_end_pos = len(premarket)
    for _, row in premarket.iloc[first_red_pos + 1 :].iterrows():
        if is_green(row):
            dip_end_pos = int(row.name) + 1
            break
    dip_window = premarket.iloc[first_red_pos:dip_end_pos]
    if dip_window.empty:
        return premarket.loc[first_green_pos], first_push_high_row, None
    first_dip_low_row = premarket.loc[dip_window["px_l"].astype(float).idxmin()]
    return premarket.loc[first_green_pos], first_push_high_row, first_dip_low_row


def detect_rebreak(
    bars: pd.DataFrame,
    first_dip_x: int,
    first_push_high: float,
    cfg: DetectionConfig,
) -> dict[str, Any]:
    level = float(first_push_high)
    eps = max(abs(level) * 1e-9, 1e-8)
    fake_attempt: dict[str, Any] | None = None

    after_dip = bars[bars["bar_index"].astype(int) >= int(first_dip_x)].copy()
    for _, row in after_dip.iterrows():
        high_px = float(row["px_h"])
        if high_px <= level + eps:
            continue
        rb_idx = int(row["bar_index"])
        local_prev = bars[
            (bars["bar_index"].astype(int) >= max(0, rb_idx - int(cfg.rebreak_volume_lookback_bars)))
            & (bars["bar_index"].astype(int) < rb_idx)
        ]
        prior_avg = float(local_prev["v"].astype(float).mean()) if not local_prev.empty else 0.0
        volume = float(row["v"])
        close_px = float(row["px_c"])
        open_px = float(row["px_o"])

        reasons: list[str] = []
        if close_px <= open_px:
            reasons.append("not_green")
        if close_px <= level + eps:
            reasons.append("close_not_above_level")
        if prior_avg > 0 and volume <= prior_avg:
            reasons.append("volume_not_above_prior_avg")

        attempt = {
            "idx": rb_idx,
            "vol": volume,
            "prior_vol_avg": prior_avg,
            "green_ok": close_px > open_px,
            "close_above_level": close_px > level + eps,
            "volume_ok": not (prior_avg > 0 and volume <= prior_avg),
            "high_px": high_px,
            "close_px": close_px,
            "open_px": open_px,
            "reasons": "+".join(reasons),
        }
        if not reasons:
            return {"state": "rebreak_confirmed", "confirmed": attempt, "first_attempt": fake_attempt}
        if fake_attempt is None:
            fake_attempt = attempt

    if fake_attempt is not None:
        return {
            "state": "fake_rebreak_no_confirmation",
            "confirmed": None,
            "first_attempt": fake_attempt,
            "fake_reason": fake_attempt["reasons"],
        }
    return {"state": "no_valid_rebreak_in_window", "confirmed": None, "first_attempt": None}


def add_event(
    events: list[dict[str, Any]],
    work: pd.Series,
    bars: pd.DataFrame,
    anchor_type: str,
    idx: int,
    price: float | None,
    extra: dict[str, Any] | None = None,
) -> None:
    row = bars.iloc[int(idx)]
    event = {
        "experiment_id": EXPERIMENT_ID,
        "builder_id": BUILDER_ID,
        "anchor_worklist_id": str(work["anchor_worklist_id"]),
        "anchor_id": f"{work['anchor_worklist_id']}_{anchor_type}",
        "anchor_type": anchor_type,
        "ticker": work["ticker"],
        "session_date": work["session_date"],
        "bar_index": int(idx),
        "ts_utc": fmt_ts(row["ts_utc_dt"]),
        "ts_et": fmt_ts(row["ts_et_dt"]),
        "price": price,
        "price_source": "ohlcv_1m_quote_guarded_full_universe_v0_1",
        "calculation_rule": CALCULATION_RULE,
        "visual_label_id": f"{work['anchor_worklist_id']}_{anchor_type}",
        "quality_state": "candidate_visual_audit_required",
    }
    if extra:
        event.update(extra)
    events.append(event)


def row_to_output(work: pd.Series, bars: pd.DataFrame, cfg: DetectionConfig) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    case_id = str(work["anchor_worklist_id"])
    prior_close = num(work.get("prior_close"))
    events: list[dict[str, Any]] = []

    base: dict[str, Any] = {
        "experiment_id": EXPERIMENT_ID,
        "builder_id": BUILDER_ID,
        "calculation_rule": CALCULATION_RULE,
        "anchor_worklist_id": case_id,
        "ticker": work["ticker"],
        "session_date": work["session_date"],
        "scanner_gate_ts_utc": work["scanner_gate_ts_utc"],
        "scanner_gate_ts_et": work["scanner_gate_ts_et"],
        "scanner_gate_price_source_worklist": work.get("scanner_gate_price"),
        "scanner_gate_prior_close_pct": work.get("scanner_gate_prior_close_pct"),
        "scanner_gate_accumulated_volume": work.get("scanner_gate_accumulated_volume"),
        "prior_close": prior_close,
        "source_input_1m_file": work["source_input_1m_file"],
        "source_input_1m_dataset": work.get("source_input_1m_dataset", None),
        "source_input_1m_root": work.get("source_input_1m_root", None),
        "market_cap": work.get("market_cap", None),
        "market_cap_source_state": work.get("market_cap_source_state", None),
        "market_cap_gate_state": work.get("market_cap_gate_state", None),
        "anchor_quality_state": "candidate_visual_audit_required",
        "visual_audit_required": True,
        "session_start_et": cfg.session_start_et,
        "session_end_et": cfg.session_end_et,
        "push_label_pct": cfg.push_label_pct,
        "dip_label_pct": cfg.dip_label_pct,
        "momentum_trigger_pct": cfg.momentum_trigger_pct,
        "created_utc": utc_now(),
    }

    if bars.empty:
        base["trajectory_state"] = "data_quality_blocked_no_0330_1000_session_bars"
        return base, events

    scanner_idx = bar_x_for_ts(bars, work.get("scanner_gate_ts_utc"))
    if scanner_idx is None:
        base["trajectory_state"] = "data_quality_blocked_scanner_gate_not_found"
        return base, events

    scanner_row = bars.iloc[int(scanner_idx)]
    scanner_price = float(scanner_row["px_c"])
    scanner_volume = num(work.get("scanner_gate_accumulated_volume"))
    if scanner_volume is None:
        scanner_volume = float(bars.iloc[: int(scanner_idx) + 1]["v"].astype(float).sum())

    base["session_bars_observed"] = int(len(bars))
    base["session_first_bar_ts_utc"] = fmt_ts(bars.iloc[0]["ts_utc_dt"])
    base["session_first_bar_ts_et"] = fmt_ts(bars.iloc[0]["ts_et_dt"])
    base["scanner_gate_bar_index_resolved"] = int(scanner_idx)
    base["scanner_gate_price"] = scanner_price
    base["scanner_gate_price_source"] = "scanner_candle_close_sol3"
    base["scanner_gate_accumulated_volume_resolved"] = scanner_volume
    base["scanner_gate_prior_close_pct_resolved"] = pct(scanner_price, prior_close)

    add_event(events, work, bars, "scanner_gate", int(scanner_idx), scanner_price)

    pm_open_price = num(work.get("pm_open_price"))
    if pm_open_price is None:
        pm_open_price = num(bars.iloc[0].get("px_o"))
    if pm_open_price is None or pm_open_price <= 0:
        base["trajectory_state"] = "human_das_scanner_anchored_no_pm_open"
        return base, events
    base["pm_open_price"] = float(pm_open_price)

    push_start_row, first_push_high_row, first_dip_low_row = find_visual_first_push_scanner_anchored(
        bars, float(pm_open_price), cfg, int(scanner_idx)
    )
    if push_start_row is None or first_push_high_row is None:
        base["trajectory_state"] = "human_das_scanner_anchored_no_push"
        return base, events

    push_start_idx = int(push_start_row.name)
    push_start_price = float(clean(push_start_row.get("px_l")) or clean(push_start_row.get("px_o")) or clean(push_start_row.get("px_c")))
    base["visual_sequence_source"] = "human_das_scanner_anchored"
    base["push_start_bar_index"] = push_start_idx
    base["push_start_ts_utc"] = fmt_ts(push_start_row.get("ts_utc_dt"))
    base["push_start_ts_et"] = fmt_ts(push_start_row.get("ts_et_dt"))
    base["push_start_price"] = push_start_price
    base["first_push_start_ts_utc"] = base["push_start_ts_utc"]
    base["first_push_start_ts_et"] = base["push_start_ts_et"]
    base["first_push_start_price"] = push_start_price
    add_event(events, work, bars, "push_start", push_start_idx, push_start_price)

    high_idx = int(first_push_high_row.name)
    high_price = float(first_push_high_row["px_h"])
    base["first_push_high_bar_index"] = high_idx
    base["first_push_high_ts_utc"] = fmt_ts(first_push_high_row.get("ts_utc_dt"))
    base["first_push_high_ts_et"] = fmt_ts(first_push_high_row.get("ts_et_dt"))
    base["first_push_high_price"] = high_price
    base["first_push_high"] = high_price
    base["first_push_pct_from_prior_close"] = pct(high_price, prior_close)
    base["pm_open_to_first_push_high_pct"] = pct(high_price, float(pm_open_price))
    base["bars_from_push_start_to_first_push_high"] = int(high_idx - push_start_idx + 1)
    add_event(events, work, bars, "first_push_high", high_idx, high_price)

    if first_dip_low_row is None:
        base["trajectory_state"] = "human_das_scanner_anchored_no_dip"
        base["visual_sequence_source"] = "human_das_scanner_anchored_no_dip"
        return base, events

    dip_idx = int(first_dip_low_row.name)
    dip_price = float(first_dip_low_row["px_l"])
    base["first_dip_low_bar_index"] = dip_idx
    base["first_dip_low_ts_utc"] = fmt_ts(first_dip_low_row.get("ts_utc_dt"))
    base["first_dip_low_ts_et"] = fmt_ts(first_dip_low_row.get("ts_et_dt"))
    base["first_dip_low_price"] = dip_price
    base["first_dip_low"] = dip_price
    base["dip_from_first_push_pct"] = pct(dip_price, high_price)
    base["first_dip_depth_pct"] = ((high_price - dip_price) / high_price * 100.0) if high_price > 0 else None
    base["bars_from_first_push_high_to_first_dip_low"] = int(dip_idx - high_idx)
    add_event(events, work, bars, "first_dip_low", dip_idx, dip_price)

    rb = detect_rebreak(bars, dip_idx, high_price, cfg)
    base["trajectory_state"] = rb["state"]

    if rb["state"] == "rebreak_confirmed":
        confirmed = rb["confirmed"]
        idx = int(confirmed["idx"])
        base["rebreak_bar_index"] = idx
        base["rebreak_ts_utc"] = fmt_ts(bars.iloc[idx]["ts_utc_dt"])
        base["rebreak_ts_et"] = fmt_ts(bars.iloc[idx]["ts_et_dt"])
        base["rebreak_price"] = high_price
        base["bars_from_first_dip_to_rebreak"] = int(idx - dip_idx)
        base["rebreak_volume"] = confirmed["vol"]
        base["rebreak_prior_volume_avg"] = confirmed["prior_vol_avg"]
        base["rebreak_volume_ok"] = confirmed["volume_ok"]
        base["rebreak_green_ok"] = confirmed["green_ok"]
        base["rebreak_close_above_level"] = confirmed["close_above_level"]
        base["rebreak_confirmation_rule"] = "sol3_green_close_above_level_volume_gt_prior_5bar_avg"
        add_event(events, work, bars, "rebreak_confirmed", idx, high_price, confirmed)

        if rb.get("first_attempt") is not None:
            attempt = rb["first_attempt"]
            fake_idx = int(attempt["idx"])
            base["fake_rebreak_bar_index"] = fake_idx
            base["fake_rebreak_ts_utc"] = fmt_ts(bars.iloc[fake_idx]["ts_utc_dt"])
            base["fake_rebreak_ts_et"] = fmt_ts(bars.iloc[fake_idx]["ts_et_dt"])
            base["fake_rebreak_price"] = high_price
            base["fake_rebreak_reason"] = attempt["reasons"]
            base["fake_rebreak_volume"] = attempt["vol"]
            base["fake_rebreak_prior_volume_avg"] = attempt["prior_vol_avg"]
            add_event(events, work, bars, "fake_rebreak", fake_idx, high_price, {**attempt, "fake_reason": attempt["reasons"]})
    elif rb["state"] == "fake_rebreak_no_confirmation":
        attempt = rb["first_attempt"]
        idx = int(attempt["idx"])
        base["fake_rebreak_bar_index"] = idx
        base["fake_rebreak_ts_utc"] = fmt_ts(bars.iloc[idx]["ts_utc_dt"])
        base["fake_rebreak_ts_et"] = fmt_ts(bars.iloc[idx]["ts_et_dt"])
        base["fake_rebreak_price"] = high_price
        base["fake_rebreak_reason"] = rb.get("fake_reason")
        base["fake_rebreak_volume"] = attempt["vol"]
        base["fake_rebreak_prior_volume_avg"] = attempt["prior_vol_avg"]
        add_event(events, work, bars, "fake_rebreak", idx, high_price, {**attempt, "fake_reason": rb.get("fake_reason")})

    return base, events


def write_summary(output_dir: Path, cases: pd.DataFrame, events: pd.DataFrame, errors: pd.DataFrame, cfg: DetectionConfig) -> dict[str, Any]:
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "builder_id": BUILDER_ID,
        "calculation_rule": CALCULATION_RULE,
        "output_dir": str(output_dir),
        "case_count": int(len(cases)),
        "event_count": int(len(events)),
        "error_count": int(len(errors)),
        "session_start_et": cfg.session_start_et,
        "session_end_et": cfg.session_end_et,
        "push_label_pct": cfg.push_label_pct,
        "dip_label_pct": cfg.dip_label_pct,
        "momentum_trigger_pct": cfg.momentum_trigger_pct,
        "trajectory_state_counts": cases["trajectory_state"].value_counts(dropna=False).to_dict() if "trajectory_state" in cases.columns else {},
    }
    (output_dir / "anchor_detection_summary_sol3_logic_v0_2.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md = [
        "# Anchor Detection Summary SOL3 Logic v0.2",
        "",
        f"- experiment_id: {EXPERIMENT_ID}",
        f"- builder_id: {BUILDER_ID}",
        f"- calculation_rule: {CALCULATION_RULE}",
        f"- session_window_et: {cfg.session_start_et}-{cfg.session_end_et}",
        f"- cases: {len(cases)}",
        f"- events: {len(events)}",
        f"- errors: {len(errors)}",
        "",
        "## Trajectory State Counts",
        "",
        "```json",
        json.dumps(summary["trajectory_state_counts"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## SOL3 Rule",
        "",
        "```text",
        "scanner_gate = scanner candle close in 03:30-10:00 ET bars",
        "first_push_high = max high from first green expansion through first red candle at/after scanner gate",
        "first_dip_low = min low from that first red through the first later green recovery candle",
        "rebreak_confirmed = first post-dip high above first_push_high with green bar, close above level, and volume > prior 5-bar average",
        "fake_rebreak = first post-dip high above first_push_high that fails one of those confirmation checks",
        "```",
    ]
    (output_dir / "anchor_detection_summary_sol3_logic_v0_2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return summary


def build_anchor_candidates(run_root: Path, output_dir: Path | None, limit: int | None, cfg: DetectionConfig) -> dict[str, Any]:
    worklist_path = run_root / "anchor_worklist" / "anchor_worklist_from_denominator_v0_1.parquet"
    if not worklist_path.exists():
        raise FileNotFoundError(f"Missing anchor worklist: {worklist_path}")

    output_dir = output_dir or (run_root / "anchor_candidates_sol3_logic_v0_2")
    output_dir.mkdir(parents=True, exist_ok=True)

    work = pd.read_parquet(worklist_path).copy()
    if limit is not None:
        work = work.head(int(limit)).copy()

    case_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    total = len(work)
    for i, (_, row) in enumerate(work.iterrows(), start=1):
        try:
            bars = read_session_bars(Path(str(row["source_input_1m_file"])), str(row["session_date"]), cfg)
            case, events = row_to_output(row, bars, cfg)
            case_rows.append(case)
            event_rows.extend(events)
            print(f"[OK] {i}/{total} {row['ticker']} {row['session_date']} {case.get('trajectory_state')}", flush=True)
        except Exception as exc:
            errors.append(
                {
                    "anchor_worklist_id": row.get("anchor_worklist_id"),
                    "ticker": row.get("ticker"),
                    "session_date": row.get("session_date"),
                    "source_input_1m_file": row.get("source_input_1m_file"),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
            print(f"[ERROR] {i}/{total} {row.get('ticker')} {row.get('session_date')} {exc!r}", flush=True)

    cases = pd.DataFrame(case_rows)
    events = pd.DataFrame(event_rows)
    errors_df = pd.DataFrame(errors)

    cases_path = output_dir / "das_frontside_anchor_candidates_sol3_logic_v0_2.parquet"
    cases_csv = output_dir / "das_frontside_anchor_candidates_sol3_logic_v0_2.csv"
    events_path = output_dir / "das_frontside_anchor_events_long_sol3_logic_v0_2.parquet"
    events_csv = output_dir / "das_frontside_anchor_events_long_sol3_logic_v0_2.csv"
    errors_csv = output_dir / "anchor_detection_errors_sol3_logic_v0_2.csv"
    errors_json = output_dir / "anchor_detection_errors_sol3_logic_v0_2.json"

    cases.to_parquet(cases_path, index=False)
    cases.to_csv(cases_csv, index=False)
    events.to_parquet(events_path, index=False)
    events.to_csv(events_csv, index=False)
    errors_df.to_csv(errors_csv, index=False)
    errors_json.write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = write_summary(output_dir, cases, events, errors_df, cfg)
    summary.update(
        {
            "run_root": str(run_root),
            "worklist_path": str(worklist_path),
            "cases_path": str(cases_path),
            "events_path": str(events_path),
            "errors_path": str(errors_csv),
        }
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--session-start-et", default="03:30")
    parser.add_argument("--session-end-et", default="10:00")
    parser.add_argument("--push-label-pct", type=float, default=20.0)
    parser.add_argument("--dip-label-pct", type=float, default=3.0)
    parser.add_argument("--momentum-trigger-pct", type=float, default=50.0)
    parser.add_argument("--rebreak-volume-lookback-bars", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = DetectionConfig(
        session_start_et=args.session_start_et,
        session_end_et=args.session_end_et,
        push_label_pct=args.push_label_pct,
        dip_label_pct=args.dip_label_pct,
        momentum_trigger_pct=args.momentum_trigger_pct,
        rebreak_volume_lookback_bars=args.rebreak_volume_lookback_bars,
    )
    build_anchor_candidates(args.run_root, args.output_dir, args.limit, config)
