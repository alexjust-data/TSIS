"""Build DAS frontside anchor candidates from the scanner denominator worklist.

This builder starts from the frozen scanner denominator. It does not decide that
a case is a good DAS setup, an in-play strategy event, or a trade. It only
creates candidate structural anchors that can be audited visually and measured
later.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_das_frontside_anchor_candidates_from_worklist_v0_1"
NY = ZoneInfo("America/New_York")

DEFAULT_RUN_ROOT = Path(
    r"C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z"
)


@dataclass(frozen=True)
class DetectionConfig:
    session_start_et: str = "03:30"
    session_end_et: str = "10:00"
    min_dip_pct: float = 3.0
    rebreak_volume_lookback_bars: int = 5
    rebreak_volume_ratio_min: float = 1.0
    require_green_rebreak_bar: bool = True
    max_bars_after_scanner: int | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_hhmm(value: str) -> time:
    hh, mm = value.split(":")
    return time(int(hh), int(mm))


def fmt_ts(ts: pd.Timestamp | None) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.Timestamp(ts).isoformat()


def pct(new: float | None, old: float | None) -> float | None:
    if new is None or old is None or not math.isfinite(float(new)) or not math.isfinite(float(old)) or float(old) == 0:
        return None
    return (float(new) / float(old) - 1.0) * 100.0


def read_session_bars(source_file: Path, session_date: str, cfg: DetectionConfig) -> pd.DataFrame:
    bars = pd.read_parquet(source_file)
    required = ["ts_utc", "o", "h", "l", "c", "v"]
    missing = [c for c in required if c not in bars.columns]
    if missing:
        raise ValueError(f"{source_file} missing required bar columns: {missing}")

    bars = bars.copy()
    bars["ts_utc_dt"] = pd.to_datetime(bars["ts_utc"], utc=True, errors="coerce").dt.floor("min")
    bars = bars.dropna(subset=["ts_utc_dt"])
    bars["ts_et_dt"] = bars["ts_utc_dt"].dt.tz_convert(NY)
    bars["session_date_et"] = bars["ts_et_dt"].dt.strftime("%Y-%m-%d")
    bars["time_et"] = bars["ts_et_dt"].dt.time

    start = parse_hhmm(cfg.session_start_et)
    end = parse_hhmm(cfg.session_end_et)
    mask = (
        (bars["session_date_et"] == str(session_date))
        & (bars["time_et"] >= start)
        & (bars["time_et"] <= end)
    )
    bars = bars.loc[mask].sort_values("ts_utc_dt").reset_index(drop=True)
    bars["bar_index"] = range(len(bars))
    for col in ["o", "h", "l", "c", "v"]:
        bars[col] = pd.to_numeric(bars[col], errors="coerce")
    return bars


def find_scanner_index(bars: pd.DataFrame, scanner_ts_utc: str) -> int | None:
    target = pd.to_datetime(scanner_ts_utc, utc=True, errors="coerce").floor("min")
    if pd.isna(target) or bars.empty:
        return None
    matches = bars.index[bars["ts_utc_dt"] == target].tolist()
    if matches:
        return int(matches[0])
    prior = bars.index[bars["ts_utc_dt"] <= target].tolist()
    if prior:
        return int(prior[-1])
    return None


def find_push_start(bars: pd.DataFrame, scanner_idx: int, prior_close: float) -> int:
    """Candidate wake-up start before the scanner gate.

    This is deliberately mechanical and conservative: use the lowest low before
    the scanner gate, then walk forward to the first bar whose range touches that
    low. It gives a reproducible anchor for measuring how much movement was
    already under way before the scanner fired.
    """

    if scanner_idx <= 0:
        return 0
    pre = bars.iloc[: scanner_idx + 1]
    lows = pre["l"].dropna()
    if lows.empty:
        return 0
    low_value = float(lows.min())
    low_positions = pre.index[pre["l"] == low_value].tolist()
    if not low_positions:
        return 0
    start = int(low_positions[-1])
    if start > scanner_idx:
        start = scanner_idx
    return start


def find_first_push_and_dip(bars: pd.DataFrame, push_start_idx: int, config: DetectionConfig) -> dict:
    """Detect the first push and the first local pullback after it.

    Human rule used for DAS visual audit:
    - first push starts at scanner/push start;
    - first push continues until the first red candle after the initial green expansion;
    - first_push_high is the maximum high up to and including that first red candle,
      because the upper wick of that red candle can be the real push high;
    - first dip is the first pullback immediately after that push: the first red
      candle/sequence plus the first green candle that ends the pullback;
    - first_dip_low is the lowest low inside that local pullback block. It must
      not drift later into a second structure.
    """
    if len(bars) == 0:
        return {"state": "empty_bars"}

    start_idx = int(max(0, min(push_start_idx, len(bars) - 1)))
    end_idx = min(len(bars) - 1, start_idx + int(config.max_bars_after_scanner))
    window = bars.iloc[start_idx : end_idx + 1]
    if window.empty:
        return {"state": "empty_window"}

    # The first expansion candle is normally green. If the scanner/push start is
    # not green, use the first green candle in the local window as the expansion
    # start. Fallback to start_idx for pathological cases.
    first_green_idx = None
    for idx in range(start_idx, end_idx + 1):
        row = bars.iloc[idx]
        if float(row["close"]) > float(row["open"]):
            first_green_idx = idx
            break
    if first_green_idx is None:
        first_green_idx = start_idx

    first_red_idx = None
    for idx in range(first_green_idx + 1, end_idx + 1):
        row = bars.iloc[idx]
        if float(row["close"]) < float(row["open"]):
            first_red_idx = idx
            break

    if first_red_idx is None:
        push_window = bars.iloc[first_green_idx : end_idx + 1]
        high_offset = int(push_window["high"].astype(float).to_numpy().argmax())
        high_idx = int(first_green_idx + high_offset)
        high_price = float(bars.iloc[high_idx]["high"])
        return {
            "state": "first_push_no_clean_dip",
            "push_start_idx": first_green_idx,
            "first_push_high_idx": high_idx,
            "first_push_high_price": high_price,
            "first_dip_low_idx": None,
            "first_dip_low_price": None,
            "first_red_idx": None,
            "dip_end_idx": None,
            "bars_from_push_start_to_high": high_idx - first_green_idx + 1,
        }

    push_window = bars.iloc[first_green_idx : first_red_idx + 1]
    high_offset = int(push_window["high"].astype(float).to_numpy().argmax())
    high_idx = int(first_green_idx + high_offset)
    high_price = float(bars.iloc[high_idx]["high"])

    # First local pullback: first red sequence plus the first green candle that
    # ends it. The low can be on that green candle's lower wick.
    dip_end_idx = first_red_idx
    for idx in range(first_red_idx + 1, end_idx + 1):
        row = bars.iloc[idx]
        dip_end_idx = idx
        if float(row["close"]) > float(row["open"]):
            break

    dip_window = bars.iloc[first_red_idx : dip_end_idx + 1]
    if dip_window.empty:
        return {"state": "first_push_no_clean_dip"}

    dip_low_idx = int(dip_window["low"].astype(float).idxmin())
    dip_low = float(bars.iloc[dip_low_idx]["low"])
    dip_pct = (dip_low / high_price - 1.0) * 100.0 if high_price else None

    return {
        "state": "first_push_first_local_dip_found",
        "push_start_idx": first_green_idx,
        "first_push_high_idx": high_idx,
        "first_push_high_price": high_price,
        "first_red_idx": first_red_idx,
        "dip_end_idx": dip_end_idx,
        "first_dip_low_idx": dip_low_idx,
        "first_dip_low_price": dip_low,
        "first_dip_pct_from_first_push": dip_pct,
        "bars_from_push_start_to_high": high_idx - first_green_idx + 1,
        "bars_from_first_push_to_dip_low": dip_low_idx - high_idx if dip_low_idx is not None else None,
        "bars_in_first_pullback_block": dip_end_idx - first_red_idx + 1,
    }

def classify_rebreak(bars: pd.DataFrame, anchors: dict, config: DetectionConfig) -> dict:
    """Classify rebreak using strict two-close confirmation.

    A valid DAS in-play rebreak requires:
    - the candidate candle trades above first_push_high;
    - that same candle closes above first_push_high;
    - the following candle also closes above first_push_high.

    Volume and candle color remain diagnostic fields only. They are not hard
    filters in this version because they belong to later parameter sweeps.
    """
    high_price = anchors.get("first_push_high_price")
    high_idx = anchors.get("first_push_high_idx")
    dip_idx = anchors.get("first_dip_low_idx")
    if high_price is None or high_idx is None or dip_idx is None:
        return {"state": "no_rebreak_missing_anchor"}

    level = float(high_price)
    start_idx = max(int(high_idx) + 1, int(dip_idx) + 1)
    first_failed_attempt = None

    for idx in range(start_idx, len(bars) - 1):
        row = bars.iloc[idx]
        next_row = bars.iloc[idx + 1]
        high_break = float(row["high"]) > level
        if not high_break:
            continue

        prior = bars.iloc[max(0, idx - config.rebreak_volume_lookback_bars) : idx]
        prior_vol_avg = float(prior["volume"].mean()) if not prior.empty else 0.0
        vol = float(row["volume"])
        volume_ratio = vol / prior_vol_avg if prior_vol_avg > 0 else None
        close_above = float(row["close"]) > level
        next_close_above = float(next_row["close"]) > level
        green_ok = float(row["close"]) > float(row["open"])

        reasons = []
        if not close_above:
            reasons.append("close_not_above_level")
        if not next_close_above:
            reasons.append("next_close_not_above_level")

        attempt = {
            "idx": idx,
            "ts_utc": row["ts_utc"],
            "price": level,
            "volume": vol,
            "prior_volume_avg": prior_vol_avg,
            "volume_ratio": volume_ratio,
            "volume_ok": volume_ratio is not None and volume_ratio >= config.rebreak_volume_ratio_min,
            "green_ok": green_ok,
            "close_above_level": close_above,
            "next_close_above_level": next_close_above,
            "next_ts_utc": next_row["ts_utc"],
            "bars_from_first_dip": idx - int(dip_idx),
            "failure_reason": "+".join(reasons) if reasons else None,
            "confirmation_rule": "break_bar_close_above_and_next_close_above_v0_2",
        }

        if close_above and next_close_above:
            return {
                "state": "rebreak_confirmed",
                "confirmed": attempt,
                "first_failed_attempt": first_failed_attempt,
            }

        if first_failed_attempt is None:
            first_failed_attempt = attempt

    if first_failed_attempt is not None:
        return {
            "state": "fake_rebreak_no_confirmation",
            "confirmed": None,
            "first_failed_attempt": first_failed_attempt,
        }

    return {"state": "no_rebreak_in_window", "confirmed": None, "first_failed_attempt": None}

def row_to_output(work: pd.Series, bars: pd.DataFrame, cfg: DetectionConfig) -> tuple[dict, list[dict]]:
    case_id = str(work["anchor_worklist_id"])
    prior_close = float(work["prior_close"])
    scanner_idx = find_scanner_index(bars, str(work["scanner_gate_ts_utc"]))

    base = {
        "experiment_id": EXPERIMENT_ID,
        "builder_id": BUILDER_ID,
        "anchor_worklist_id": case_id,
        "ticker": work["ticker"],
        "session_date": work["session_date"],
        "scanner_gate_ts_utc": work["scanner_gate_ts_utc"],
        "scanner_gate_ts_et": work["scanner_gate_ts_et"],
        "scanner_gate_price": work["scanner_gate_price"],
        "scanner_gate_prior_close_pct": work["scanner_gate_prior_close_pct"],
        "scanner_gate_accumulated_volume": work["scanner_gate_accumulated_volume"],
        "prior_close": prior_close,
        "source_input_1m_file": work["source_input_1m_file"],
        "source_input_1m_dataset": work.get("source_input_1m_dataset", None),
        "market_cap": work.get("market_cap", None),
        "market_cap_source_state": work.get("market_cap_source_state", None),
        "market_cap_gate_state": work.get("market_cap_gate_state", None),
        "anchor_quality_state": "candidate_visual_audit_required",
        "visual_audit_required": True,
        "created_utc": utc_now(),
    }

    events: list[dict] = []
    if bars.empty:
        base["trajectory_state"] = "data_quality_blocked_no_session_bars"
        return base, events
    if scanner_idx is None:
        base["trajectory_state"] = "data_quality_blocked_scanner_gate_not_found"
        return base, events

    push_start_idx = find_push_start(bars, scanner_idx, prior_close)
    detection = find_first_push_and_dip(bars, push_start_idx, scanner_idx, float(work["scanner_gate_price"]), cfg)

    base["session_bars_observed"] = int(len(bars))
    base["scanner_gate_bar_index_resolved"] = int(scanner_idx)
    base["push_start_bar_index"] = int(push_start_idx)
    base["push_start_ts_utc"] = fmt_ts(bars.iloc[push_start_idx]["ts_utc_dt"])
    base["push_start_price"] = float(bars.iloc[push_start_idx]["o"]) if pd.notna(bars.iloc[push_start_idx]["o"]) else None

    def add_event(anchor_type: str, idx: int, price: float | None, extra: dict | None = None) -> None:
        row = bars.iloc[int(idx)]
        event = {
            "experiment_id": EXPERIMENT_ID,
            "anchor_worklist_id": case_id,
            "anchor_id": f"{case_id}_{anchor_type}",
            "anchor_type": anchor_type,
            "ticker": work["ticker"],
            "session_date": work["session_date"],
            "bar_index": int(idx),
            "ts_utc": fmt_ts(row["ts_utc_dt"]),
            "ts_et": fmt_ts(row["ts_et_dt"]),
            "price": price,
            "price_source": "ohlcv_1m_quote_guarded_full_universe_v0_1",
            "calculation_rule": "candidate_mechanical_v0_1_visual_audit_required",
            "visual_label_id": f"{case_id}_{anchor_type}",
            "quality_state": "candidate_visual_audit_required",
        }
        if extra:
            event.update(extra)
        events.append(event)

    add_event("scanner_gate", scanner_idx, float(work["scanner_gate_price"]))
    add_event("push_start", push_start_idx, base["push_start_price"])

    if detection["state"] in {"first_push_no_clean_dip", "first_push_and_dip_detected"}:
        high_idx = int(detection["first_push_high_idx"])
        high_price = float(detection["first_push_high_price"])
        base["first_push_high_bar_index"] = high_idx
        base["first_push_high_ts_utc"] = fmt_ts(bars.iloc[high_idx]["ts_utc_dt"])
        base["first_push_high_price"] = high_price
        base["first_push_pct_from_prior_close"] = pct(high_price, prior_close)
        base["bars_from_push_start_to_first_push_high"] = int(high_idx - push_start_idx + 1)
        add_event("first_push_high", high_idx, high_price)
    else:
        base["trajectory_state"] = detection["state"]
        return base, events

    if detection["state"] == "first_push_no_clean_dip":
        base["trajectory_state"] = "first_push_no_clean_dip"
        return base, events

    dip_idx = int(detection["first_dip_low_idx"])
    dip_price = float(detection["first_dip_low_price"])
    base["first_dip_low_bar_index"] = dip_idx
    base["first_dip_low_ts_utc"] = fmt_ts(bars.iloc[dip_idx]["ts_utc_dt"])
    base["first_dip_low_price"] = dip_price
    base["dip_from_first_push_pct"] = pct(dip_price, base["first_push_high_price"])
    base["bars_from_first_push_high_to_first_dip_low"] = int(dip_idx - int(base["first_push_high_bar_index"]))
    add_event("first_dip_low", dip_idx, dip_price)

    rb = classify_rebreak(
        bars,
        int(base["first_push_high_bar_index"]),
        dip_idx,
        float(base["first_push_high_price"]),
        cfg,
    )
    base["trajectory_state"] = rb["state"]

    if rb["state"] == "rebreak_confirmed":
        confirmed = rb["confirmed"]
        idx = int(confirmed["idx"])
        base["rebreak_bar_index"] = idx
        base["rebreak_ts_utc"] = fmt_ts(bars.iloc[idx]["ts_utc_dt"])
        base["rebreak_price"] = float(base["first_push_high_price"])
        base["bars_from_first_dip_to_rebreak"] = int(idx - dip_idx)
        base["rebreak_volume"] = confirmed["vol"]
        base["rebreak_prior_volume_avg"] = confirmed["prior_vol_avg"]
        base["rebreak_volume_ok"] = confirmed["volume_ok"]
        base["rebreak_green_ok"] = confirmed["green_ok"]
        base["rebreak_close_above_level"] = confirmed["close_above_level"]
        base["rebreak_next_close_above_level"] = confirmed["next_close_above_level"]
        base["rebreak_confirmation_rule"] = confirmed.get("confirmation_rule", "break_bar_close_above_and_next_close_above_v0_2")
        add_event("rebreak_confirmed", idx, float(base["first_push_high_price"]), confirmed)
    elif rb["state"] == "fake_rebreak_no_confirmation":
        attempt = rb["first_attempt"]
        idx = int(attempt["idx"])
        base["fake_rebreak_bar_index"] = idx
        base["fake_rebreak_ts_utc"] = fmt_ts(bars.iloc[idx]["ts_utc_dt"])
        base["fake_rebreak_price"] = float(base["first_push_high_price"])
        base["fake_rebreak_reason"] = rb["fake_reason"]
        base["fake_rebreak_volume"] = attempt["vol"]
        base["fake_rebreak_prior_volume_avg"] = attempt["prior_vol_avg"]
        add_event("fake_rebreak", idx, float(base["first_push_high_price"]), {**attempt, "fake_reason": rb["fake_reason"]})

    return base, events


def build_anchor_candidates(run_root: Path, output_dir: Path | None, limit: int | None, cfg: DetectionConfig) -> dict:
    worklist_path = run_root / "anchor_worklist" / "anchor_worklist_from_denominator_v0_1.parquet"
    if not worklist_path.exists():
        raise FileNotFoundError(f"Missing anchor worklist: {worklist_path}")

    output_dir = output_dir or (run_root / "anchor_candidates")
    output_dir.mkdir(parents=True, exist_ok=True)

    work = pd.read_parquet(worklist_path).copy()
    if limit is not None:
        work = work.head(int(limit)).copy()

    case_rows: list[dict] = []
    event_rows: list[dict] = []
    errors: list[dict] = []

    for _, row in work.iterrows():
        try:
            bars = read_session_bars(Path(str(row["source_input_1m_file"])), str(row["session_date"]), cfg)
            case, events = row_to_output(row, bars, cfg)
            case_rows.append(case)
            event_rows.extend(events)
        except Exception as exc:  # keep all cases auditable; do not abort full batch
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

    cases = pd.DataFrame(case_rows)
    events = pd.DataFrame(event_rows)
    errors_df = pd.DataFrame(errors)

    cases_path = output_dir / "das_frontside_anchor_candidates_v0_1.parquet"
    cases_csv = output_dir / "das_frontside_anchor_candidates_v0_1.csv"
    events_path = output_dir / "das_frontside_anchor_events_long_v0_1.parquet"
    events_csv = output_dir / "das_frontside_anchor_events_long_v0_1.csv"
    errors_csv = output_dir / "das_frontside_anchor_detection_errors_v0_1.csv"

    cases.to_parquet(cases_path, index=False)
    cases.to_csv(cases_csv, index=False)
    events.to_parquet(events_path, index=False)
    events.to_csv(events_csv, index=False)
    errors_df.to_csv(errors_csv, index=False)

    summary = {
        "builder_id": BUILDER_ID,
        "experiment_id": EXPERIMENT_ID,
        "created_utc": utc_now(),
        "run_root": str(run_root),
        "worklist_path": str(worklist_path),
        "output_dir": str(output_dir),
        "input_rows": int(len(work)),
        "case_rows": int(len(cases)),
        "event_rows": int(len(events)),
        "errors": int(len(errors_df)),
        "trajectory_state_counts": cases.get("trajectory_state", pd.Series(dtype=str)).fillna("__NA__").astype(str).value_counts().to_dict(),
        "config": {
            "session_start_et": cfg.session_start_et,
            "session_end_et": cfg.session_end_et,
            "min_dip_pct": cfg.min_dip_pct,
            "rebreak_volume_lookback_bars": cfg.rebreak_volume_lookback_bars,
            "rebreak_volume_ratio_min": cfg.rebreak_volume_ratio_min,
            "require_green_rebreak_bar": cfg.require_green_rebreak_bar,
            "max_bars_after_scanner": cfg.max_bars_after_scanner,
        },
        "outputs": {
            "cases_parquet": str(cases_path),
            "events_parquet": str(events_path),
            "errors_csv": str(errors_csv),
        },
    }
    (output_dir / "anchor_detection_summary_v0_1.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# DAS Frontside Anchor Candidates v0.1",
        "",
        f"created_utc: `{summary['created_utc']}`",
        f"builder_id: `{BUILDER_ID}`",
        "",
        "## Lectura Correcta",
        "",
        "Este output detecta anchors candidatos desde el denominador scanner 2026.",
        "",
        "```text",
        "anchor_candidates != DAS bueno",
        "anchor_candidates != in-play oficial",
        "anchor_candidates != trade",
        "anchor_candidates != edge",
        "```",
        "",
        "Toda fila mantiene `visual_audit_required = True` porque las reglas de first push, first dip y rebreak siguen siendo reglas candidatas.",
        "",
        "## Counts",
        "",
        f"- input_rows: `{summary['input_rows']}`",
        f"- case_rows: `{summary['case_rows']}`",
        f"- event_rows: `{summary['event_rows']}`",
        f"- errors: `{summary['errors']}`",
        "",
        "## Trajectory State Counts",
        "",
        "```json",
        json.dumps(summary["trajectory_state_counts"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Candidate Rule v0.1",
        "",
        "```text",
        "first_push_high = running high in the scanner-relevant push, frozen only after running high is at least scanner_gate_price and a later low retraces min_dip_pct from that high",
        "first_dip_low = lowest low after first_push_high and before first later touch of first_push_high",
        "rebreak_confirmed = later high crosses first_push_high with candidate volume confirmation and green bar rule",
        "fake_rebreak = later high crosses first_push_high but candidate confirmation fails",
        "no_rebreak = no later high touches first_push_high in the analysis window",
        "```",
    ]
    (output_dir / "anchor_detection_summary_v0_1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--session-start-et", default="04:00")
    parser.add_argument("--session-end-et", default="10:00")
    parser.add_argument("--min-dip-pct", type=float, default=3.0)
    parser.add_argument("--rebreak-volume-lookback-bars", type=int, default=5)
    parser.add_argument("--rebreak-volume-ratio-min", type=float, default=1.0)
    parser.add_argument("--allow-red-rebreak-bar", action="store_true")
    parser.add_argument("--max-bars-after-scanner", type=int, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = DetectionConfig(
        session_start_et=args.session_start_et,
        session_end_et=args.session_end_et,
        min_dip_pct=args.min_dip_pct,
        rebreak_volume_lookback_bars=args.rebreak_volume_lookback_bars,
        rebreak_volume_ratio_min=args.rebreak_volume_ratio_min,
        require_green_rebreak_bar=not args.allow_red_rebreak_bar,
        max_bars_after_scanner=args.max_bars_after_scanner,
    )
    result = build_anchor_candidates(args.run_root, args.output_dir, args.limit, config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
