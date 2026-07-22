"""Fast baseline panels for EXP_DAS_FRONTSIDE_DISCOVERY_0002.

This builder starts the experiment from the existing DAS run candidate_events
without recalculating visual anchors case by case. It is a population baseline:
fast, reproducible, and explicitly marked as not fully visual-audited.

The slower visual-audited overlay from EXP_DAS_FRONTSIDE_DISCOVERY_0001 remains
required for calibration and disputed anchor semantics.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_das_frontside_discovery_baseline_fast_v0_1"
ANCHOR_SOURCE = "das_run_candidate_events_original_not_visual_recalculated"
DEFAULT_RUN_DIR = Path(r"C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z")
DEFAULT_OUTPUT_DIR = Path(r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\baseline_fast_v0_1")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clean(v: Any) -> Any:
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except TypeError:
        pass
    return v


def _float(v: Any) -> float | None:
    v = _clean(v)
    if v is None:
        return None
    try:
        out = float(v)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(out):
        return None
    return out


def _pct(numerator: Any, denominator: Any) -> float | None:
    n = _float(numerator)
    d = _float(denominator)
    if n is None or d is None or d == 0:
        return None
    return (n / d - 1.0) * 100.0


def _read_candidates(run_dir: Path) -> pd.DataFrame:
    p = run_dir / "candidate_events.parquet"
    if not p.exists():
        raise FileNotFoundError(p)
    return pd.read_parquet(p).reset_index(drop=True)


def _trajectory_state(row: pd.Series) -> str:
    if str(row.get("event_quality_state", "")).lower() not in {"", "nan", "candidate_event"}:
        return str(row.get("event_quality_state"))
    if bool(row.get("first_dip_destroyed_structure")):
        return "first_push_dip_destroyed_structure"
    if pd.notna(row.get("first_rebreak_ts_utc")) or str(row.get("das_state", "")) == "rebreak_confirmed":
        return "rebreak_confirmed"
    if pd.notna(row.get("first_dip_low")):
        if row.get("structure_alive_after_pullback") is False:
            return "first_push_dip_no_recovery"
        return "first_push_dip_no_rebreak"
    if pd.notna(row.get("first_push_high")):
        return "first_push_no_clean_dip"
    return "scanner_only"


def _denominator(df: pd.DataFrame, run_dir: Path, created_utc: str) -> pd.DataFrame:
    rows = []
    for pos, r in df.iterrows():
        price = _float(r.get("price_at_trigger"))
        rows.append({
            "experiment_id": EXPERIMENT_ID,
            "sweep_id": "baseline_threshold50_from_das_run_20260628T114046Z",
            "run_dir": str(run_dir),
            "run_position": int(pos) + 1,
            "candidate_id": r.get("candidate_id"),
            "ticker": r.get("ticker"),
            "session_date": r.get("session_date"),
            "strategy_id": r.get("strategy_id"),
            "scanner_gate_ts_utc": r.get("scanner_trigger_ts_utc"),
            "scanner_gate_ts_et": r.get("scanner_trigger_ts_et"),
            "scanner_gate_price": price,
            "scanner_gate_prior_close_pct": _float(r.get("pm_open_to_scanner_pct")),
            "scanner_gate_accumulated_volume": _float(r.get("session_volume_at_trigger")),
            "scanner_trigger_quality": r.get("scanner_trigger_quality"),
            "threshold_pct": 50.0,
            "prior_close": _float(r.get("prior_close")),
            "pm_open_price": _float(r.get("pm_open_price")),
            "session_volume": _float(r.get("session_volume")),
            "premarket_volume": _float(r.get("premarket_volume")),
            "market_cap": _float(r.get("market_cap")),
            "market_cap_filter_pass": r.get("market_cap_filter_pass"),
            "price_gate_pass_candidate": bool(price is not None and 0.5 <= price <= 20.0),
            "anchor_source": ANCHOR_SOURCE,
            "visual_audit_state": "pending_visual_overlay",
            "data_quality_state": r.get("event_quality_state"),
            "builder_id": BUILDER_ID,
            "created_utc": created_utc,
        })
    return pd.DataFrame(rows)


def _anchor_events(df: pd.DataFrame, created_utc: str) -> pd.DataFrame:
    specs = [
        ("scanner_gate", "scanner_trigger_ts_utc", "price_at_trigger", "session_volume_at_trigger"),
        ("push_start", "first_push_start_ts_utc", "first_push_start_price", None),
        ("first_push_high", "first_push_high_ts_utc", "first_push_high", None),
        ("first_dip_low", "first_dip_low_ts_utc", "first_dip_low", None),
        ("rebreak", "first_rebreak_ts_utc", "structural_rebreak_level", "rebreak_volume"),
        ("max_momentum_high", "max_momentum_high_ts_utc", "max_momentum_high", None),
    ]
    rows = []
    for pos, r in df.iterrows():
        for anchor_type, ts_col, price_col, vol_col in specs:
            ts = _clean(r.get(ts_col))
            price = _float(r.get(price_col))
            if ts is None or price is None:
                continue
            rows.append({
                "experiment_id": EXPERIMENT_ID,
                "candidate_id": r.get("candidate_id"),
                "ticker": r.get("ticker"),
                "session_date": r.get("session_date"),
                "anchor_type": anchor_type,
                "anchor_ts_utc": ts,
                "anchor_price": price,
                "anchor_volume": _float(r.get(vol_col)) if vol_col else None,
                "anchor_source": ANCHOR_SOURCE,
                "visual_audit_state": "pending_visual_overlay",
                "builder_id": BUILDER_ID,
                "created_utc": created_utc,
            })
    return pd.DataFrame(rows)


def _panel(df: pd.DataFrame, run_dir: Path, created_utc: str) -> pd.DataFrame:
    rows = []
    for pos, r in df.iterrows():
        scanner_price = _float(r.get("price_at_trigger"))
        first_push_high = _float(r.get("first_push_high"))
        first_dip_low = _float(r.get("first_dip_low"))
        rebreak_level = _float(r.get("structural_rebreak_level"))
        max_after_trigger = _float(r.get("max_high_after_trigger"))
        max_momentum_high = _float(r.get("max_momentum_high"))
        state = _trajectory_state(r)
        row = {
            "experiment_id": EXPERIMENT_ID,
            "sweep_id": "baseline_threshold50_from_das_run_20260628T114046Z",
            "run_dir": str(run_dir),
            "run_position": int(pos) + 1,
            "candidate_id": r.get("candidate_id"),
            "ticker": r.get("ticker"),
            "session_date": r.get("session_date"),
            "trajectory_state_candidate": state,
            "scanner_gate_ts_utc": r.get("scanner_trigger_ts_utc"),
            "scanner_gate_price": scanner_price,
            "first_push_start_ts_utc": r.get("first_push_start_ts_utc"),
            "first_push_start_price": _float(r.get("first_push_start_price")),
            "first_push_high_ts_utc": r.get("first_push_high_ts_utc"),
            "first_push_high_price": first_push_high,
            "first_dip_low_ts_utc": r.get("first_dip_low_ts_utc"),
            "first_dip_low_price": first_dip_low,
            "first_rebreak_ts_utc": r.get("first_rebreak_ts_utc"),
            "first_rebreak_type": r.get("first_rebreak_type"),
            "rebreak_level_price": rebreak_level,
            "rebreak_volume": _float(r.get("rebreak_volume")),
            "max_high_after_trigger": max_after_trigger,
            "max_high_after_trigger_ts_utc": r.get("max_high_after_trigger_ts_utc"),
            "max_momentum_high": max_momentum_high,
            "max_momentum_high_ts_utc": r.get("max_momentum_high_ts_utc"),
            "has_first_push": bool(first_push_high is not None),
            "has_first_dip": bool(first_dip_low is not None),
            "has_rebreak_confirmed": bool(pd.notna(r.get("first_rebreak_ts_utc")) or str(r.get("das_state", "")) == "rebreak_confirmed"),
            "first_dip_destroyed_structure": bool(r.get("first_dip_destroyed_structure")),
            "structure_alive_after_pullback": r.get("structure_alive_after_pullback"),
            "scanner_to_first_push_move_pct": _pct(first_push_high, scanner_price),
            "first_push_to_first_dip_drawdown_pct": _pct(first_dip_low, first_push_high),
            "dip_to_rebreak_recovery_pct_candidate": _pct(rebreak_level, first_dip_low),
            "missed_move_to_rebreak_candidate_pct": _pct(rebreak_level, scanner_price),
            "scanner_to_max_high_pct": _float(r.get("scanner_to_max_high_pct")) or _pct(max_after_trigger, scanner_price),
            "pm_open_to_max_high_after_trigger_pct": _float(r.get("pm_open_to_max_high_after_trigger_pct")),
            "max_momentum_pct_from_push_start": _float(r.get("max_momentum_pct_from_push_start")),
            "minutes_from_trigger_to_rebreak": _float(r.get("minutes_from_trigger_to_rebreak")),
            "minutes_to_first_rebreak": _float(r.get("minutes_to_first_rebreak")),
            "momentum_end_reason": r.get("momentum_end_reason"),
            "das_state_original": r.get("das_state"),
            "state_reason_original": r.get("state_reason"),
            "event_quality_state": r.get("event_quality_state"),
            "market_cap": _float(r.get("market_cap")),
            "market_cap_filter_pass": r.get("market_cap_filter_pass"),
            "anchor_source": ANCHOR_SOURCE,
            "visual_audit_state": "pending_visual_overlay",
            "builder_id": BUILDER_ID,
            "created_utc": created_utc,
        }
        # Candidate descriptive flags, not trading rules.
        row["recovery_candidate"] = bool(row["has_rebreak_confirmed"] or (row["structure_alive_after_pullback"] is True))
        row["destruction_candidate"] = bool(row["first_dip_destroyed_structure"] or state == "first_push_dip_destroyed_structure")
        rows.append(row)
    return pd.DataFrame(rows)


def _write(df: pd.DataFrame, output_dir: Path, name: str) -> None:
    df.to_parquet(output_dir / f"{name}.parquet", index=False)
    df.to_csv(output_dir / f"{name}.csv", index=False)


def build(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    created_utc = _utc_now()
    candidates = _read_candidates(run_dir)
    denominator = _denominator(candidates, run_dir, created_utc)
    anchors = _anchor_events(candidates, created_utc)
    panel = _panel(candidates, run_dir, created_utc)
    outputs = {
        "das_frontside_scanner_denominator_baseline_fast_v0_1": denominator,
        "das_frontside_anchor_events_baseline_fast_v0_1": anchors,
        "das_frontside_dip_recovery_panel_baseline_fast_v0_1": panel,
    }
    for name, df in outputs.items():
        _write(df, output_dir, name)
    counts = panel["trajectory_state_candidate"].value_counts(dropna=False)
    lines = [
        "# DAS Frontside Discovery Baseline Fast Summary v0.1",
        "",
        f"Fecha UTC: {created_utc}",
        f"Experimento: `{EXPERIMENT_ID}`",
        f"Builder: `{BUILDER_ID}`",
        f"Run source: `{run_dir}`",
        f"Anchor source: `{ANCHOR_SOURCE}`",
        "",
        "## Lectura Correcta",
        "",
        "Este baseline arranca el experimento poblacional con los anchors del run DAS existente.",
        "No sustituye la auditoria visual del `0001`; queda marcado como `pending_visual_overlay`.",
        "",
        "## Conteos",
        "",
        f"Denominador rows: {len(denominator)}",
        f"Anchor rows: {len(anchors)}",
        f"Panel rows: {len(panel)}",
        "",
        "## Trajectory State Candidate",
        "",
    ]
    for k, v in counts.items():
        lines.append(f"- `{k}`: {int(v)}")
    lines += [
        "",
        "## Ratios Iniciales",
        "",
        f"has_first_push: {int(panel['has_first_push'].sum())} / {len(panel)}",
        f"has_first_dip: {int(panel['has_first_dip'].sum())} / {len(panel)}",
        f"has_rebreak_confirmed: {int(panel['has_rebreak_confirmed'].sum())} / {len(panel)}",
        f"recovery_candidate: {int(panel['recovery_candidate'].sum())} / {len(panel)}",
        f"destruction_candidate: {int(panel['destruction_candidate'].sum())} / {len(panel)}",
        "",
        "## Siguiente Paso",
        "",
        "Crear overlay visual-audit para una muestra estratificada y comparar estos anchors contra la logica del `0001`.",
    ]
    summary_path = output_dir / "das_frontside_discovery_baseline_fast_summary_v0_1.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "builder_id": BUILDER_ID,
        "created_utc": created_utc,
        "run_dir": str(run_dir),
        "anchor_source": ANCHOR_SOURCE,
        "visual_audit_state": "pending_visual_overlay",
        "outputs": {name: {"rows": int(len(df)), "parquet": str(output_dir / f"{name}.parquet"), "csv": str(output_dir / f"{name}.csv")} for name, df in outputs.items()},
        "summary": str(summary_path),
    }
    manifest_path = output_dir / "das_frontside_discovery_baseline_fast_manifest_v0_1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    manifest = build(args.run_dir, args.output_dir)
    print(json.dumps({"outputs": manifest["outputs"], "summary": manifest["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
