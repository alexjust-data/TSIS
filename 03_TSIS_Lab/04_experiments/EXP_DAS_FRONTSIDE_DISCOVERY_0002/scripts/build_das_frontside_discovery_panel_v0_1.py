"""Build DAS frontside discovery panels for EXP_DAS_FRONTSIDE_DISCOVERY_0002.

This builder converts the visual/semantic DAS anchors into tabular evidence:
- scanner denominator
- long-form anchor events
- dip recovery / destruction research panel

It intentionally does not validate a trading strategy. The outputs are research
evidence for threshold, recovery, fake rebreak and opportunity decomposition.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_das_frontside_discovery_panel_v0_1"
DEFAULT_RUN_DIR = Path(r"C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z")
DEFAULT_OUTPUT_DIR = Path(r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence")
RENDER_SCRIPT = Path(r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0001\scripts\render_das_visual_coordinate_solutions.py")
HORIZON_BARS = [1, 2, 5, 10, 30]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_render_module():
    spec = importlib.util.spec_from_file_location("das_render_v0001", RENDER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load render script: {RENDER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    original_load_quotes = module._load_quotes_for_session

    @lru_cache(maxsize=4096)
    def cached_load_quotes(ticker: str, session_date: str):
        return original_load_quotes(ticker, session_date)

    module._load_quotes_for_session = cached_load_quotes
    return module


def _clean(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return value


def _float(value: Any) -> float | None:
    value = _clean(value)
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    return v


def _pct(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return (float(numerator) / float(denominator) - 1.0) * 100.0


def _bar_at(df: pd.DataFrame, x: Any) -> pd.Series | None:
    if x is None:
        return None
    try:
        xi = int(x)
    except (TypeError, ValueError):
        return None
    if "bar_index" in df.columns:
        hit = df[df["bar_index"].astype(int).eq(xi)]
        if not hit.empty:
            return hit.iloc[0]
    if 0 <= xi < len(df):
        return df.iloc[xi]
    return None


def _window_from_x(df: pd.DataFrame, x: Any, horizon: int | None = None) -> pd.DataFrame:
    try:
        xi = int(x)
    except (TypeError, ValueError):
        return df.iloc[0:0]
    if "bar_index" in df.columns:
        mask = df["bar_index"].astype(int).ge(xi)
        if horizon is not None:
            mask &= df["bar_index"].astype(int).le(xi + int(horizon))
        return df.loc[mask].copy()
    end = None if horizon is None else xi + int(horizon) + 1
    return df.iloc[xi:end].copy()


def _metrics_from_anchor(df: pd.DataFrame, x: Any, anchor_price: float | None, prefix: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if anchor_price is None or anchor_price <= 0 or x is None:
        for h in HORIZON_BARS:
            out[f"{prefix}_mfe_{h}b_envelope_pct"] = None
            out[f"{prefix}_mae_{h}b_envelope_pct"] = None
            out[f"{prefix}_return_{h}b_close_pct"] = None
        return out
    for h in HORIZON_BARS:
        w = _window_from_x(df, x, h)
        if w.empty:
            out[f"{prefix}_mfe_{h}b_envelope_pct"] = None
            out[f"{prefix}_mae_{h}b_envelope_pct"] = None
            out[f"{prefix}_return_{h}b_close_pct"] = None
            continue
        high = _float(pd.to_numeric(w["px_h"], errors="coerce").max())
        low = _float(pd.to_numeric(w["px_l"], errors="coerce").min())
        close = _float(pd.to_numeric(w.iloc[-1]["px_c"], errors="coerce"))
        out[f"{prefix}_mfe_{h}b_envelope_pct"] = _pct(high, anchor_price)
        out[f"{prefix}_mae_{h}b_envelope_pct"] = _pct(low, anchor_price)
        out[f"{prefix}_return_{h}b_close_pct"] = _pct(close, anchor_price)
    return out


def _anchor_row(case: Any, signal: str, anchor: dict[str, Any]) -> dict[str, Any]:
    df = case.df
    bar = _bar_at(df, anchor.get("x"))
    row = case.row
    return {
        "experiment_id": EXPERIMENT_ID,
        "candidate_id": case.candidate_id,
        "ticker": case.ticker,
        "session_date": case.session_date,
        "anchor_type": signal,
        "anchor_ts_utc": anchor.get("ts"),
        "anchor_bar_index": anchor.get("x"),
        "anchor_price": anchor.get("y"),
        "anchor_volume": _float(bar.get("v")) if bar is not None else None,
        "anchor_open": _float(bar.get("px_o")) if bar is not None else None,
        "anchor_high": _float(bar.get("px_h")) if bar is not None else None,
        "anchor_low": _float(bar.get("px_l")) if bar is not None else None,
        "anchor_close": _float(bar.get("px_c")) if bar is not None else None,
        "anchor_label": anchor.get("label"),
        "visual_price_source": row.get("visual_price_source"),
        "scale_guard_triggered": row.get("visual_quote_guarded_scale_guard_triggered"),
        "scale_ratio": row.get("visual_quote_guarded_scale_ratio_median"),
        "builder_id": BUILDER_ID,
    }


def _case_state(case: Any) -> str:
    if "rebreak_confirmed" in case.anchors:
        return "rebreak_confirmed"
    if "fake_rebreak" in case.anchors:
        return "fake_rebreak_no_confirmation"
    if "first_dip_low" in case.anchors:
        return "first_push_dip_no_rebreak"
    if "first_push_high" in case.anchors:
        return "first_push_no_clean_dip"
    if "scanner_seed" in case.anchors:
        return "scanner_only_no_clean_push"
    return "no_valid_scanner_anchor"


def _base_denominator_row(case: Any, position: int, run_dir: Path, created_utc: str) -> dict[str, Any]:
    r = case.row
    scanner_price = _float(r.get("visual_momentum_gate_price")) or _float(r.get("price_at_trigger"))
    return {
        "experiment_id": EXPERIMENT_ID,
        "sweep_id": "baseline_threshold50_from_das_run_20260628T114046Z",
        "run_dir": str(run_dir),
        "run_position": position,
        "candidate_id": case.candidate_id,
        "ticker": case.ticker,
        "session_date": case.session_date,
        "strategy_id": r.get("strategy_id"),
        "scanner_gate_ts_utc": r.get("visual_momentum_gate_ts_utc") or r.get("scanner_trigger_ts_utc"),
        "scanner_gate_ts_et": r.get("visual_momentum_gate_ts_et") or r.get("scanner_trigger_ts_et"),
        "scanner_gate_price": scanner_price,
        "scanner_gate_prior_close_pct": _float(r.get("visual_momentum_gate_prior_close_pct")) or _float(r.get("pm_open_to_scanner_pct")),
        "scanner_gate_accumulated_volume": _float(r.get("visual_momentum_gate_volume")) or _float(r.get("session_volume_at_trigger")),
        "threshold_pct": _float(r.get("momentum_trigger_pct_threshold")) or 50.0,
        "prior_close": _float(r.get("prior_close")),
        "pm_open_price": _float(r.get("pm_open_price")),
        "market_cap": _float(r.get("market_cap")),
        "market_cap_filter_pass": r.get("market_cap_filter_pass"),
        "price_gate_pass_candidate": bool(scanner_price is not None and 0.5 <= scanner_price <= 20.0),
        "visual_price_source": r.get("visual_price_source"),
        "visual_quote_guarded_changed_rows": r.get("visual_quote_guarded_changed_rows"),
        "visual_quote_guarded_eligible_rows": r.get("visual_quote_guarded_eligible_rows"),
        "scale_guard_triggered": r.get("visual_quote_guarded_scale_guard_triggered"),
        "scale_ratio": r.get("visual_quote_guarded_scale_ratio_median"),
        "data_quality_state": "scale_mismatch_review" if r.get("visual_quote_guarded_scale_guard_triggered") else "research_candidate",
        "builder_id": BUILDER_ID,
        "created_utc": created_utc,
    }


def _panel_row(case: Any, position: int, run_dir: Path, created_utc: str) -> dict[str, Any]:
    r = case.row
    a = case.anchors
    df = case.df
    scanner = a.get("scanner_seed")
    first_push = a.get("first_push_high")
    first_dip = a.get("first_dip_low")
    rebreak = a.get("rebreak_confirmed")
    fake = a.get("fake_rebreak")
    scanner_price = _float(scanner.get("y")) if scanner else (_float(r.get("visual_momentum_gate_price")) or _float(r.get("price_at_trigger")))
    first_push_price = _float(first_push.get("y")) if first_push else _float(r.get("first_push_high"))
    first_dip_price = _float(first_dip.get("y")) if first_dip else _float(r.get("first_dip_low"))
    rebreak_price = _float(rebreak.get("y")) if rebreak else None
    fake_price = _float(fake.get("y")) if fake else None
    state = _case_state(case)
    panel: dict[str, Any] = {
        "experiment_id": EXPERIMENT_ID,
        "sweep_id": "baseline_threshold50_from_das_run_20260628T114046Z",
        "run_dir": str(run_dir),
        "run_position": position,
        "candidate_id": case.candidate_id,
        "ticker": case.ticker,
        "session_date": case.session_date,
        "trajectory_state_candidate": state,
        "scanner_gate_ts_utc": scanner.get("ts") if scanner else r.get("visual_momentum_gate_ts_utc"),
        "scanner_gate_bar_index": scanner.get("x") if scanner else None,
        "scanner_gate_price": scanner_price,
        "first_push_high_ts_utc": first_push.get("ts") if first_push else r.get("first_push_high_ts_utc"),
        "first_push_high_bar_index": first_push.get("x") if first_push else None,
        "first_push_high_price": first_push_price,
        "first_dip_low_ts_utc": first_dip.get("ts") if first_dip else r.get("first_dip_low_ts_utc"),
        "first_dip_low_bar_index": first_dip.get("x") if first_dip else None,
        "first_dip_low_price": first_dip_price,
        "rebreak_ts_utc": rebreak.get("ts") if rebreak else None,
        "rebreak_bar_index": rebreak.get("x") if rebreak else None,
        "rebreak_price": rebreak_price,
        "fake_rebreak_ts_utc": fake.get("ts") if fake else None,
        "fake_rebreak_bar_index": fake.get("x") if fake else None,
        "fake_rebreak_price": fake_price,
        "fake_rebreak_reasons": r.get("visual_fake_rebreak_reasons"),
        "has_first_push": bool(first_push is not None),
        "has_first_dip": bool(first_dip is not None),
        "has_rebreak_confirmed": bool(rebreak is not None),
        "has_fake_rebreak": bool(fake is not None),
        "scanner_to_first_push_move_pct": _pct(first_push_price, scanner_price),
        "first_push_to_first_dip_drawdown_pct": _pct(first_dip_price, first_push_price),
        "dip_to_rebreak_recovery_pct_candidate": _pct(rebreak_price, first_dip_price),
        "missed_move_to_rebreak_candidate_pct": _pct(rebreak_price, scanner_price),
        "visual_price_source": r.get("visual_price_source"),
        "visual_quote_guarded_changed_rows": r.get("visual_quote_guarded_changed_rows"),
        "scale_guard_triggered": r.get("visual_quote_guarded_scale_guard_triggered"),
        "scale_ratio": r.get("visual_quote_guarded_scale_ratio_median"),
        "data_quality_state": "scale_mismatch_review" if r.get("visual_quote_guarded_scale_guard_triggered") else "research_candidate",
        "builder_id": BUILDER_ID,
        "created_utc": created_utc,
    }
    panel.update(_metrics_from_anchor(df, panel["scanner_gate_bar_index"], scanner_price, "scanner"))
    panel.update(_metrics_from_anchor(df, panel["first_dip_low_bar_index"], first_dip_price, "first_dip"))
    panel.update(_metrics_from_anchor(df, panel["rebreak_bar_index"], rebreak_price, "rebreak"))
    # Candidate destruction flags are descriptive research flags, not strategy rules.
    panel["post_dip_down_20pct_30b_candidate"] = None
    v = panel.get("first_dip_return_30b_close_pct")
    if v is not None and not pd.isna(v):
        panel["post_dip_down_20pct_30b_candidate"] = bool(float(v) <= -20.0)
    panel["death_below_scanner_gate_30b_candidate"] = None
    if first_dip is not None and scanner_price is not None:
        w = _window_from_x(df, first_dip.get("x"), 30)
        if not w.empty:
            lo = _float(pd.to_numeric(w["px_l"], errors="coerce").min())
            panel["death_below_scanner_gate_30b_candidate"] = bool(lo is not None and lo <= scanner_price)
    return panel


def _write_outputs(denominator: pd.DataFrame, anchors: pd.DataFrame, panel: pd.DataFrame, output_dir: Path, run_dir: Path, created_utc: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "das_frontside_scanner_denominator_v0_1": denominator,
        "das_frontside_anchor_events_v0_1": anchors,
        "das_frontside_dip_recovery_panel_v0_1": panel,
    }
    for stem, df in outputs.items():
        df.to_parquet(output_dir / f"{stem}.parquet", index=False)
        df.to_csv(output_dir / f"{stem}.csv", index=False)

    counts = panel["trajectory_state_candidate"].value_counts(dropna=False).to_dict() if not panel.empty else {}
    sources = panel["visual_price_source"].value_counts(dropna=False).to_dict() if not panel.empty else {}
    summary_lines = [
        "# DAS Frontside Discovery Summary v0.1",
        "",
        f"Fecha UTC: {created_utc}",
        f"Experimento: `{EXPERIMENT_ID}`",
        f"Builder: `{BUILDER_ID}`",
        f"Run source: `{run_dir}`",
        "",
        "## Outputs",
        "",
        "```text",
        "das_frontside_scanner_denominator_v0_1.parquet/csv",
        "das_frontside_anchor_events_v0_1.parquet/csv",
        "das_frontside_dip_recovery_panel_v0_1.parquet/csv",
        "```",
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
        summary_lines.append(f"- `{k}`: {v}")
    summary_lines += ["", "## Visual Price Source", ""]
    for k, v in sources.items():
        summary_lines.append(f"- `{k}`: {v}")
    if not panel.empty:
        summary_lines += [
            "",
            "## Ratios Iniciales",
            "",
            f"first_push present: {int(panel['has_first_push'].sum())} / {len(panel)}",
            f"first_dip present: {int(panel['has_first_dip'].sum())} / {len(panel)}",
            f"rebreak confirmed: {int(panel['has_rebreak_confirmed'].sum())} / {len(panel)}",
            f"fake rebreak: {int(panel['has_fake_rebreak'].sum())} / {len(panel)}",
            f"scale mismatch review: {int(panel['scale_guard_triggered'].fillna(False).sum())} / {len(panel)}",
            "",
            "## Nota",
            "",
            "Estos outputs son evidencia de investigacion. No validan estrategia, entrada, salida ni edge operativo.",
            "Las metricas `*_envelope_pct` son opportunity envelope sobre barras observadas, no fills ejecutables.",
        ]
    (output_dir / "das_frontside_discovery_summary_v0_1.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "builder_id": BUILDER_ID,
        "created_utc": created_utc,
        "run_dir": str(run_dir),
        "outputs": {stem: {"rows": int(len(df)), "parquet": str(output_dir / f"{stem}.parquet"), "csv": str(output_dir / f"{stem}.csv")} for stem, df in outputs.items()},
        "summary": str(output_dir / "das_frontside_discovery_summary_v0_1.md"),
    }
    (output_dir / "das_frontside_discovery_manifest_v0_1.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def build(run_dir: Path, output_dir: Path, limit: int | None = None, start_index: int = 0) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    module = _load_render_module()
    candidates = module.dw._load_candidates_from_run(run_dir)
    if candidates.empty:
        candidates = module.dw._load_partial_candidates_from_run(run_dir)
    total = len(candidates)
    end = total if limit is None else min(total, start_index + limit)
    created_utc = _utc_now()
    denominator_rows: list[dict[str, Any]] = []
    anchor_rows: list[dict[str, Any]] = []
    panel_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for idx in range(start_index, end):
        try:
            case = module._load_case(run_dir, candidate_index=idx)
            position = idx + 1
            denominator_rows.append(_base_denominator_row(case, position, run_dir, created_utc))
            for signal, anchor in case.anchors.items():
                anchor_rows.append(_anchor_row(case, signal, anchor))
            panel_rows.append(_panel_row(case, position, run_dir, created_utc))
        except Exception as exc:  # keep experiment running and emit error row
            errors.append({"run_position": idx + 1, "error": repr(exc)})
    denominator = pd.DataFrame(denominator_rows)
    anchors = pd.DataFrame(anchor_rows)
    panel = pd.DataFrame(panel_rows)
    _write_outputs(denominator, anchors, panel, output_dir, run_dir, created_utc)
    if errors:
        pd.DataFrame(errors).to_csv(output_dir / "das_frontside_discovery_errors_v0_1.csv", index=False)
    return denominator, anchors, panel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start-index", type=int, default=0)
    args = parser.parse_args()
    denominator, anchors, panel = build(args.run_dir, args.output_dir, args.limit, args.start_index)
    print(f"denominator_rows={len(denominator)}")
    print(f"anchor_rows={len(anchors)}")
    print(f"panel_rows={len(panel)}")
    if not panel.empty:
        print(panel["trajectory_state_candidate"].value_counts(dropna=False).to_string())
    print(f"output_dir={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
