from __future__ import annotations

import argparse
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import PerformanceWarning


BUILDER_ID = "build_das_candidate_state_table_experimental"
BUILDER_VERSION = "0.1.0"
LOGICAL_DATASET_ID = "das_candidate_state_table_experimental"
LOGICAL_VERSION = "0.1.0"
OUTPUT_BASENAME = "das_candidate_state_table_experimental_v0_1"

warnings.simplefilter("ignore", PerformanceWarning)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_candidates(run_dir: Path) -> tuple[pd.DataFrame, str]:
    parquet_path = run_dir / "candidate_events.parquet"
    csv_path = run_dir / "candidate_events.csv"
    partial_path = run_dir / "candidate_events_partial.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path), parquet_path.name
    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path.name
    if partial_path.exists():
        return pd.read_csv(partial_path), partial_path.name
    raise FileNotFoundError(f"No candidate_events file found in {run_dir}")


def _read_export_manifest(run_dir: Path) -> pd.DataFrame:
    path = run_dir / "chart_exports" / "EXPORT_MANIFEST.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "candidate_id" not in df.columns:
        return pd.DataFrame()
    return df


def _config_value(manifest: dict[str, Any], key: str, default: Any = None) -> Any:
    config = manifest.get("config") or {}
    if isinstance(config, dict):
        return config.get(key, default)
    return default


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _column(df: pd.DataFrame, name: str, default: Any = pd.NA) -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series([default] * len(df), index=df.index)


def _bool_column(df: pd.DataFrame, name: str, default: Any = pd.NA) -> pd.Series:
    s = _column(df, name, default)
    if s.dtype == object:
        return s.map(
            lambda v: (
                pd.NA
                if pd.isna(v)
                else str(v).strip().lower() in {"true", "1", "yes", "y"}
            )
        )
    return s


def _safe_relpath(path_value: Any, base: Path) -> Any:
    if pd.isna(path_value):
        return pd.NA
    try:
        path = Path(str(path_value))
        return str(path.relative_to(base))
    except Exception:
        return str(path_value)


def _candidate_state(row: pd.Series) -> str:
    state = row.get("das_state")
    quality = row.get("event_quality_state")
    if pd.notna(state) and str(state).strip():
        return str(state)
    if pd.notna(quality) and str(quality).strip():
        return str(quality)
    if pd.notna(row.get("first_rebreak_ts_utc")):
        return "rebreak_confirmed"
    if pd.notna(row.get("first_dip_low_ts_utc")):
        return "first_dip_detected"
    if pd.notna(row.get("first_push_high_ts_utc")):
        return "first_push_detected"
    if pd.notna(row.get("scanner_trigger_ts_utc")):
        return "scanner_only"
    return "manual_review_required"


def _quality_state(row: pd.Series) -> str:
    original = row.get("event_quality_state")
    if pd.notna(original) and str(original).strip():
        return str(original)
    if bool(row.get("first_dip_destroyed_structure", False)):
        return "failed_candidate"
    if bool(row.get("stale_scanner_trigger", False)):
        return "review_candidate"
    if pd.notna(row.get("first_rebreak_ts_utc")):
        return "good_candidate"
    return "review_candidate"


def _variant(row: pd.Series) -> str:
    state = str(row.get("das_state") or "")
    rebreak_type = str(row.get("first_rebreak_type") or "")
    wick_type = str(row.get("first_green_wick_dip_type") or "")
    dip_depth = row.get("first_dip_depth_pct")

    if "failed" in state.lower():
        return "backside_false_positive"
    if rebreak_type == "ascending_flag_break":
        return "A_plus_continuation"
    if rebreak_type == "last_red_high_break":
        return "early_red_high_break"
    if rebreak_type == "vwap_reclaim_rebreak":
        return "vwap_dip_reclaim"
    if "green_wick" in wick_type:
        return "green_wick_reactivation"
    try:
        if pd.notna(dip_depth) and float(dip_depth) >= 45:
            return "deep_dip_reclaim"
    except Exception:
        pass
    if bool(row.get("stale_scanner_trigger", False)):
        return "late_scanner_but_valid"
    if pd.isna(row.get("first_rebreak_ts_utc")):
        return "unclear"
    return "unclear"


def _merge_exports(candidates: pd.DataFrame, exports: pd.DataFrame, run_dir: Path) -> pd.DataFrame:
    if exports.empty:
        return candidates.copy()
    keep = [
        "candidate_id",
        "candidate_export_dir",
        "three_day_overview_image_path",
        "event_day_premarket_detail_image_path",
        "event_day_detail_until_1600_ny_image_path",
        "daily_context_image_path",
        "position",
    ]
    keep = [c for c in keep if c in exports.columns]
    out = candidates.merge(exports[keep], on="candidate_id", how="left", suffixes=("", "_export"))
    for col in [
        "candidate_export_dir",
        "three_day_overview_image_path",
        "event_day_premarket_detail_image_path",
        "event_day_detail_until_1600_ny_image_path",
        "daily_context_image_path",
    ]:
        if col in out.columns:
            out[col] = out[col].map(lambda v: _safe_relpath(v, run_dir))
    return out


def build_table(run_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    candidates, candidate_file = _read_candidates(run_dir)
    manifest = _read_json(run_dir / "manifest.json")
    exports = _read_export_manifest(run_dir)
    df = _merge_exports(candidates, exports, run_dir)

    built_at = datetime.now(timezone.utc).isoformat()
    config = manifest.get("config") or {}

    table = pd.DataFrame(index=df.index)

    table["identity__das_candidate_id"] = _column(df, "candidate_id")
    table["identity__logical_dataset_id"] = LOGICAL_DATASET_ID
    table["identity__logical_version"] = LOGICAL_VERSION
    table["identity__status"] = "experimental"
    table["identity__ticker"] = _column(df, "ticker")
    table["identity__primary_exchange"] = _column(df, "primary_exchange")
    table["identity__tradingview_symbol"] = _column(df, "tradingview_symbol")
    table["identity__company_name"] = _column(df, "security_name").fillna(_column(df, "name"))
    table["identity__session_date"] = _column(df, "session_date")
    table["identity__timezone"] = "America/New_York"
    table["identity__canonical_security_id"] = pd.NA
    table["identity__symbol_identity_quality"] = table["identity__primary_exchange"].map(
        lambda v: "resolved" if pd.notna(v) and str(v).strip() else "unresolved"
    )

    table["source__run_id"] = manifest.get("run_id") or run_dir.name
    table["source__run_dir"] = str(run_dir)
    table["source__candidate_file"] = candidate_file
    table["source__data_root"] = _config_value(manifest, "data_root")
    table["source__reference_overview_root"] = _config_value(manifest, "reference_overview_root")
    table["source__price_view"] = _config_value(manifest, "price_view")
    table["source__detector_version"] = "das_widgets_current"
    table["source__builder_id"] = BUILDER_ID
    table["source__builder_version"] = BUILDER_VERSION
    table["source__notebook_path"] = str(run_dir.parents[1] / "notebooks" / "das_case_explorer.ipynb")
    table["source__build_commit"] = pd.NA
    table["source__created_at_utc"] = built_at
    table["source__config_json"] = _json_dumps(config)
    table["source__launcher_command"] = manifest.get("terminal_launcher_one_line")

    table["scanner__definition_id"] = manifest.get("query_name") or "das_scanner_appearance"
    table["scanner__mode"] = _config_value(manifest, "session_scope", "premarket")
    table["scanner__trigger_ts"] = _column(df, "scanner_trigger_ts_utc")
    table["scanner__trigger_ts_et"] = _column(df, "scanner_trigger_ts_et")
    table["scanner__trigger_price"] = _column(df, "price_at_trigger")
    table["scanner__trigger_gap_pct_from_prior_close"] = _column(df, "day_gap_pct")
    table["scanner__trigger_pct_from_premarket_open"] = _column(df, "pm_open_to_scanner_pct")
    table["scanner__trigger_volume_today"] = _column(df, "session_volume_at_trigger")
    table["scanner__trigger_premarket_volume"] = _column(df, "premarket_volume_at_trigger")
    table["scanner__trigger_dollar_volume_today"] = (
        pd.to_numeric(table["scanner__trigger_price"], errors="coerce")
        * pd.to_numeric(table["scanner__trigger_volume_today"], errors="coerce")
    )
    table["scanner__trigger_rank"] = _column(df, "position")
    table["scanner__trigger_reason"] = _column(df, "awakening_reason")
    table["scanner__trigger_reasons_json"] = df.apply(
        lambda r: _json_dumps(
            {
                "awakening_reason": r.get("awakening_reason"),
                "scanner_trigger_quality": r.get("scanner_trigger_quality"),
                "prior_extension_before_trigger": r.get("prior_extension_before_trigger"),
            }
        ),
        axis=1,
    )
    table["scanner__top_n_inclusion"] = pd.NA
    table["scanner__eligible_before_momentum"] = ~_bool_column(
        df, "scanner_trigger_after_first_push", False
    )
    table["scanner__late_vs_momentum_trigger"] = _bool_column(df, "stale_scanner_trigger", False)
    table["scanner__minutes_after_momentum_trigger"] = _column(df, "scanner_delay_minutes")
    table["scanner__volume_threshold_reached_ts"] = _column(df, "scanner_eligibility_ts_utc")
    table["scanner__volume_threshold_reached_before_entry_zone"] = pd.NA

    table["daily__prior_close"] = _column(df, "prior_close")
    table["daily__prior_open"] = pd.NA
    table["daily__prior_high"] = pd.NA
    table["daily__prior_low"] = pd.NA
    table["daily__prior_volume"] = pd.NA
    table["daily__current_day_open_0400"] = _column(df, "pm_open_price")
    table["daily__gap_pct_from_prior_close_at_0400"] = (
        (pd.to_numeric(_column(df, "pm_open_price"), errors="coerce")
         - pd.to_numeric(_column(df, "prior_close"), errors="coerce"))
        / pd.to_numeric(_column(df, "prior_close"), errors="coerce")
        * 100.0
    )
    table["daily__gap_pct_from_prior_close_at_scanner"] = _column(df, "day_gap_pct")
    table["daily__prior_high_reclaim_before_trigger"] = pd.NA
    table["daily__multi_day_extension_count"] = pd.NA
    table["daily__days_since_last_major_extension"] = pd.NA
    table["daily__daily_resistance_nearby"] = pd.NA
    table["daily__daily_breakout_context"] = pd.NA
    table["daily__daily_chart_context_quality"] = "not_enriched"

    for col in [
        "afterhours__prev_session_has_activity",
        "afterhours__prev_session_high",
        "afterhours__prev_session_low",
        "afterhours__prev_session_close",
        "afterhours__prev_session_volume",
        "afterhours__breakout_above_prior_regular_high",
        "afterhours__breakout_held_into_premarket",
        "afterhours__failed_breakout_before_premarket",
        "afterhours__exhaustion_flag",
        "afterhours__structure_highs_lows_json",
    ]:
        table[col] = pd.NA

    table["premarket__window_start_ts"] = _column(df, "pm_open_ts_utc")
    table["premarket__window_end_ts"] = _column(df, "first_rebreak_ts_utc").fillna(
        _column(df, "scanner_trigger_ts_utc")
    )
    table["premarket__open_price"] = _column(df, "pm_open_price")
    table["premarket__open_ts"] = _column(df, "pm_open_ts_utc")
    table["premarket__high"] = _column(df, "max_high_after_trigger")
    table["premarket__high_ts"] = _column(df, "max_high_after_trigger_ts_utc")
    table["premarket__low"] = pd.NA
    table["premarket__low_ts"] = pd.NA
    table["premarket__volume_total"] = _column(df, "premarket_volume")
    table["premarket__dollar_volume_total"] = (
        pd.to_numeric(_column(df, "premarket_volume"), errors="coerce")
        * pd.to_numeric(_column(df, "price_at_trigger"), errors="coerce")
    )
    table["premarket__range_pct_from_open"] = _column(df, "pm_open_to_max_high_after_trigger_pct")
    table["premarket__first_liquid_bar_ts"] = _column(df, "awakening_start_ts_utc")
    table["premarket__minutes_from_open_to_scanner"] = _column(df, "scanner_delay_minutes")
    table["premarket__minutes_from_open_to_momentum_trigger"] = _column(df, "scanner_delay_minutes")
    table["premarket__minutes_from_open_to_first_push_high"] = pd.NA
    table["premarket__minutes_from_open_to_rebreak"] = _column(df, "minutes_to_first_rebreak")

    table["frontside__momentum_trigger_ts"] = _column(df, "awakening_start_ts_utc")
    table["frontside__momentum_trigger_price"] = _column(df, "awakening_start_price")
    table["frontside__momentum_trigger_gap_pct_from_prior_close"] = (
        (pd.to_numeric(_column(df, "awakening_start_price"), errors="coerce")
         - pd.to_numeric(_column(df, "prior_close"), errors="coerce"))
        / pd.to_numeric(_column(df, "prior_close"), errors="coerce")
        * 100.0
    )
    table["frontside__momentum_trigger_pct_from_premarket_open"] = (
        (pd.to_numeric(_column(df, "awakening_start_price"), errors="coerce")
         - pd.to_numeric(_column(df, "pm_open_price"), errors="coerce"))
        / pd.to_numeric(_column(df, "pm_open_price"), errors="coerce")
        * 100.0
    )
    table["frontside__momentum_trigger_volume_today"] = pd.NA
    table["frontside__first_push_start_ts"] = _column(df, "first_push_start_ts_utc")
    table["frontside__first_push_start_price"] = _column(df, "first_push_start_price")
    table["frontside__first_push_high_ts"] = _column(df, "first_push_high_ts_utc")
    table["frontside__first_push_high_price"] = _column(df, "first_push_high")
    table["frontside__first_push_pct_from_premarket_open"] = _column(
        df, "first_push_pct_from_pm_open"
    )
    table["frontside__first_push_pct_from_prior_close"] = (
        (pd.to_numeric(_column(df, "first_push_high"), errors="coerce")
         - pd.to_numeric(_column(df, "prior_close"), errors="coerce"))
        / pd.to_numeric(_column(df, "prior_close"), errors="coerce")
        * 100.0
    )
    table["frontside__first_push_duration_minutes"] = pd.NA
    table["frontside__first_push_volume"] = pd.NA
    table["frontside__first_push_dollar_volume"] = pd.NA
    table["frontside__first_push_bar_count"] = pd.NA
    table["frontside__first_push_red_bar_high_to_break"] = _column(df, "last_red_pullback_high")
    table["frontside__first_dip_start_ts"] = _column(df, "first_dip_low_ts_utc")
    table["frontside__first_dip_low_ts"] = _column(df, "first_dip_low_ts_utc")
    table["frontside__first_dip_low_price"] = _column(df, "first_dip_low")
    table["frontside__first_dip_depth_pct"] = _column(df, "first_dip_depth_pct")
    table["frontside__first_dip_holds_vwap"] = pd.NA
    table["frontside__first_dip_holds_higher_low"] = _column(
        df, "structure_alive_after_pullback"
    )
    table["frontside__first_dip_duration_minutes"] = pd.NA
    table["frontside__rebreak_ts"] = _column(df, "first_rebreak_ts_utc")
    table["frontside__rebreak_price"] = _column(df, "rebreak_close")
    table["frontside__rebreak_type"] = _column(df, "first_rebreak_type")
    table["frontside__rebreak_above_first_push_high"] = _column(
        df, "rebreak_close_above_required_level"
    )
    table["frontside__rebreak_above_red_bar_high"] = _column(
        df, "rebreak_close_above_required_level"
    )
    table["frontside__rebreak_volume"] = _column(df, "rebreak_volume")
    table["frontside__rebreak_minutes_after_first_push_high"] = _column(
        df, "minutes_to_first_rebreak"
    )
    table["frontside__max_momentum_high_ts"] = _column(df, "max_momentum_high_ts_utc")
    table["frontside__max_momentum_high_price"] = _column(df, "max_momentum_high")
    table["frontside__max_momentum_pct_from_premarket_open"] = _column(
        df, "max_momentum_pct_from_pm_open"
    )
    table["frontside__max_momentum_pct_from_prior_close"] = (
        (pd.to_numeric(_column(df, "max_momentum_high"), errors="coerce")
         - pd.to_numeric(_column(df, "prior_close"), errors="coerce"))
        / pd.to_numeric(_column(df, "prior_close"), errors="coerce")
        * 100.0
    )
    table["frontside__minutes_to_max_momentum_high"] = pd.NA
    table["frontside__backside_damage_ts"] = _column(df, "momentum_end_ts_utc")
    table["frontside__backside_damage_reason"] = _column(df, "momentum_end_reason")
    table["frontside__frontside_duration_minutes"] = pd.NA
    table["frontside__new_lows_after_rebreak_count"] = pd.NA
    table["frontside__higher_high_count_after_rebreak"] = pd.NA
    table["frontside__higher_low_count_after_rebreak"] = pd.NA

    table["das__state"] = df.apply(_candidate_state, axis=1)
    table["das__variant"] = df.apply(_variant, axis=1)
    table["das__sequence_index"] = 1
    table["das__is_first_das"] = True
    table["das__active_sequence_started_ts"] = _column(df, "first_rebreak_ts_utc")
    table["das__active_sequence_ended_ts"] = _column(df, "momentum_end_ts_utc")
    table["das__entry_zone_observed"] = pd.NA
    table["das__entry_zone_type"] = pd.NA
    table["das__entry_zone_ts"] = pd.NA
    table["das__entry_zone_price_low"] = pd.NA
    table["das__entry_zone_price_high"] = pd.NA
    table["das__invalidated_ts"] = _column(df, "momentum_end_ts_utc")
    table["das__invalidation_reason"] = _column(df, "momentum_end_reason")
    table["das__pattern_family"] = table["das__variant"]

    table["vwap__source_selected"] = _config_value(manifest, "vwap_source", "calculated")
    table["vwap__calculated_available"] = True
    table["vwap__raw_available"] = pd.NA
    table["vwap__at_scanner"] = pd.NA
    table["vwap__at_momentum_trigger"] = pd.NA
    table["vwap__at_first_push_high"] = pd.NA
    table["vwap__at_first_dip_low"] = pd.NA
    table["vwap__at_rebreak"] = _column(df, "vwap_at_rebreak")
    table["vwap__price_above_vwap_at_scanner"] = pd.NA
    table["vwap__price_above_vwap_at_momentum_trigger"] = pd.NA
    table["vwap__first_dip_holds_vwap"] = pd.NA
    table["vwap__vwap_reclaim_before_rebreak"] = _column(df, "rebreak_close_above_vwap")
    table["vwap__vwap_loss_after_rebreak_ts"] = pd.NA

    for col in [
        "ema_wilder__ema8_at_scanner",
        "ema_wilder__wilder8_at_scanner",
        "ema_wilder__state_at_scanner",
        "ema_wilder__ema8_at_momentum_trigger",
        "ema_wilder__wilder8_at_momentum_trigger",
        "ema_wilder__state_at_momentum_trigger",
        "ema_wilder__ema8_at_rebreak",
        "ema_wilder__wilder8_at_rebreak",
        "ema_wilder__state_at_rebreak",
        "ema_wilder__bullish_spread_at_rebreak",
        "ema_wilder__bearish_flip_ts",
        "ema_wilder__bullish_duration_minutes",
    ]:
        table[col] = pd.NA

    table["quality__state"] = df.apply(_quality_state, axis=1)
    table["quality__manual_review_required"] = table["quality__state"].isin(
        ["review_candidate", "degraded_candidate"]
    )
    table["quality__missing_1m_bars"] = False
    table["quality__missing_premarket_window"] = table["premarket__open_price"].isna()
    table["quality__suspicious_wicks"] = pd.NA
    table["quality__direction_mismatch"] = (
        pd.to_numeric(table["frontside__max_momentum_pct_from_premarket_open"], errors="coerce")
        <= 0
    )
    table["quality__split_or_reverse_split_nearby"] = pd.NA
    table["quality__halt_overlap"] = pd.NA
    table["quality__market_cap_missing"] = _column(df, "market_cap").isna()
    table["quality__identity_unresolved"] = table["identity__symbol_identity_quality"].eq(
        "unresolved"
    )
    table["quality__scanner_late"] = table["scanner__late_vs_momentum_trigger"]
    table["quality__insufficient_volume_at_scanner"] = (
        pd.to_numeric(table["scanner__trigger_volume_today"], errors="coerce")
        < float(_config_value(manifest, "min_session_volume", 500000.0) or 500000.0)
    )
    table["quality__candidate_from_partial_run"] = candidate_file == "candidate_events_partial.csv"
    table["quality__notes"] = _column(df, "state_reason")

    table["human_label__grade"] = "unlabeled"
    table["human_label__folder_source"] = pd.NA
    table["human_label__tags"] = pd.NA
    table["human_label__annotator"] = pd.NA
    table["human_label__label_ts"] = pd.NA
    table["human_label__discretionary_entry_notes"] = pd.NA
    table["human_label__discretionary_stop_notes"] = pd.NA
    table["human_label__why_good"] = pd.NA
    table["human_label__why_bad"] = pd.NA
    table["human_label__pattern_name_manual"] = pd.NA
    table["human_label__image_annotation_path"] = pd.NA

    table["outcome__max_high_after_scanner"] = _column(df, "max_high_after_trigger")
    table["outcome__max_high_after_scanner_ts"] = _column(df, "max_high_after_trigger_ts_utc")
    table["outcome__max_extension_pct_after_scanner"] = _column(df, "scanner_to_max_high_pct")
    table["outcome__max_high_after_momentum_trigger"] = _column(df, "max_momentum_high")
    table["outcome__max_extension_pct_after_momentum_trigger"] = _column(
        df, "max_momentum_pct_from_push_start"
    )
    table["outcome__max_high_after_rebreak"] = _column(df, "max_momentum_high")
    table["outcome__max_extension_pct_after_rebreak"] = pd.NA
    table["outcome__minutes_to_max_high_after_rebreak"] = pd.NA
    table["outcome__drawdown_after_rebreak_pct"] = pd.NA
    table["outcome__vwap_loss_after_rebreak"] = _column(df, "momentum_end_reason").map(
        lambda v: pd.NA if pd.isna(v) else "vwap_loss" in str(v)
    )
    table["outcome__first_lower_low_after_rebreak_ts"] = pd.NA
    table["outcome__backside_confirmed"] = _column(df, "momentum_end_reason").map(
        lambda v: pd.NA
        if pd.isna(v)
        else any(token in str(v) for token in ["structure_break", "vwap_loss"])
    )
    table["outcome__backside_confirmed_ts"] = _column(df, "momentum_end_ts_utc")
    table["outcome__failed_to_hold_first_push_high"] = ~_bool_column(
        df, "structure_alive_after_pullback", True
    )
    table["outcome__failed_to_hold_vwap"] = table["outcome__vwap_loss_after_rebreak"]
    table["outcome__close_vs_rebreak_pct"] = pd.NA
    table["outcome__close_vs_premarket_open_pct"] = pd.NA

    table["export__chart_01_interactive_available"] = True
    table["export__chart_02_three_day_overview_path"] = _column(
        df, "three_day_overview_image_path"
    )
    table["export__chart_03_event_day_premarket_detail_path"] = _column(
        df, "event_day_premarket_detail_image_path"
    )
    table["export__chart_04_event_day_until_1600_path"] = _column(
        df, "event_day_detail_until_1600_ny_image_path"
    )
    table["export__chart_daily_context_path"] = _column(df, "daily_context_image_path")
    table["export__chart_export_root"] = "chart_exports"
    table["export__chart_export_manifest_path"] = (
        "chart_exports/EXPORT_MANIFEST.csv"
        if (run_dir / "chart_exports" / "EXPORT_MANIFEST.csv").exists()
        else pd.NA
    )
    table["export__chart_export_created_at_utc"] = built_at

    metadata = {
        "logical_dataset_id": LOGICAL_DATASET_ID,
        "logical_version": LOGICAL_VERSION,
        "builder_id": BUILDER_ID,
        "builder_version": BUILDER_VERSION,
        "created_at_utc": built_at,
        "run_dir": str(run_dir),
        "source_candidate_file": candidate_file,
        "source_rows": int(len(candidates)),
        "output_rows": int(len(table)),
        "export_manifest_found": bool(not exports.empty),
        "source_run_id": manifest.get("run_id") or run_dir.name,
        "source_run_status": manifest.get("run_status"),
        "source_query_name": manifest.get("query_name"),
        "anti_leakage_rule": "human_label__ and outcome__ are not features",
    }
    return table, metadata


def _column_classification(columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        if col.startswith("human_label__"):
            cls = "human_label_after_review"
            allowed = False
        elif col.startswith("outcome__"):
            cls = "outcome_after_event"
            allowed = False
        elif col.startswith("export__"):
            cls = "lineage_only"
            allowed = False
        elif col.startswith("source__"):
            cls = "lineage_only"
            allowed = False
        elif col.startswith("scanner__"):
            cls = "observable_at_scanner"
            allowed = True
        elif col.startswith("frontside__rebreak") or col.startswith("das__"):
            cls = "observable_at_rebreak"
            allowed = True
        elif col.startswith("frontside__") or col.startswith("vwap__") or col.startswith("ema_wilder__"):
            cls = "derived_without_future"
            allowed = True
        elif col.startswith("quality__"):
            cls = "quality_control"
            allowed = False
        else:
            cls = "context"
            allowed = True
        rows.append(
            {
                "column": col,
                "anti_leakage_class": cls,
                "allowed_as_feature_candidate": allowed,
            }
        )
    return pd.DataFrame(rows)


def _write_summary(output_dir: Path, table: pd.DataFrame, metadata: dict[str, Any]) -> None:
    state_counts = table["das__state"].value_counts(dropna=False).to_dict()
    variant_counts = table["das__variant"].value_counts(dropna=False).head(20).to_dict()
    quality_counts = table["quality__state"].value_counts(dropna=False).to_dict()

    lines = [
        "# DAS Candidate State Table Experimental Summary",
        "",
        f"- logical_dataset_id: `{metadata['logical_dataset_id']}`",
        f"- logical_version: `{metadata['logical_version']}`",
        f"- builder_version: `{metadata['builder_version']}`",
        f"- created_at_utc: `{metadata['created_at_utc']}`",
        f"- run_dir: `{metadata['run_dir']}`",
        f"- source_candidate_file: `{metadata['source_candidate_file']}`",
        f"- rows: `{metadata['output_rows']}`",
        "",
        "## Anti-leakage rule",
        "",
        "`human_label__` and `outcome__` columns are not features.",
        "",
        "## DAS state counts",
        "",
    ]
    for key, value in state_counts.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Variant counts", ""])
    for key, value in variant_counts.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Quality counts", ""])
    for key, value in quality_counts.items():
        lines.append(f"- `{key}`: {value}")

    output_dir.joinpath(f"{OUTPUT_BASENAME}_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_outputs(run_dir: Path, output_dir: Path) -> Path:
    table, metadata = build_table(run_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = output_dir / f"{OUTPUT_BASENAME}.parquet"
    csv_path = output_dir / f"{OUTPUT_BASENAME}.csv"
    manifest_path = output_dir / f"{OUTPUT_BASENAME}_manifest.json"
    classification_path = output_dir / f"{OUTPUT_BASENAME}_column_classification.csv"

    table.to_parquet(parquet_path, index=False)
    table.to_csv(csv_path, index=False)

    classification = _column_classification(list(table.columns))
    classification.to_csv(classification_path, index=False)

    metadata.update(
        {
            "outputs": {
                "parquet": str(parquet_path),
                "csv": str(csv_path),
                "manifest": str(manifest_path),
                "column_classification": str(classification_path),
                "summary": str(output_dir / f"{OUTPUT_BASENAME}_summary.md"),
            },
            "columns": list(table.columns),
        }
    )
    manifest_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_summary(output_dir, table, metadata)
    return parquet_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="DAS run directory.")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to <run-dir>/state_tables.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else run_dir / "state_tables"

    parquet_path = write_outputs(run_dir, output_dir)
    print(f"wrote={parquet_path}")
    print(f"output_dir={output_dir}")


if __name__ == "__main__":
    main()
