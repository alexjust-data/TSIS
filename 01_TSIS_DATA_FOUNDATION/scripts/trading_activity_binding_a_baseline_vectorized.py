"""Vectorized Stage-8 kernel for Trading Activity Binding A."""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd
from trading_activity_binding_a_multisession_engine import (
    BASELINE_RESULT_COLUMNS,
    BASELINE_VALUE_COLUMNS,
    _typed_numeric,
    _typed_utc,
    build_baseline_cache,
)

STATE_COLUMNS = (
    "feature_spec_id",
    "feature_version",
    "binding_id",
    "scope_id",
    "pilot_scope_id",
    "instrument_id",
    "ticker",
    "session_date",
    "decision_timestamp",
    "window_seconds",
    "subwindow_seconds",
    "trade_eligibility_policy_id",
    "duplicate_policy_id",
    "latency_policy_id",
    "source_dataset_id",
    "source_schema_version",
    "market_calendar_build_run_id",
    "instrument_master_build_run_id",
    "foundation_quality_label",
    "local_window_disposition",
    "quality_state",
    "coverage_state",
    "coverage_mode",
    "calculation_state",
    "feature_input_max_available_at",
    "lineage_manifest_id",
    "future_window_used",
)

VALUE_COLUMNS = {
    "trade_count": "eligible_trade_count",
    "share_volume": "eligible_share_volume",
    "dollar_volume": "eligible_dollar_volume",
    "arrival_rate": "trade_arrival_rate",
}


def _flat_cache(cache: dict[tuple[str, int, str], dict[str, Any]]) -> tuple[pd.DataFrame, dict[tuple[str, int, str, str], np.ndarray]]:
    rows: list[dict[str, Any]] = []
    sorted_values: dict[tuple[str, int, str, str], np.ndarray] = {}
    for (clock_minute, window_seconds, candidate), entry in cache.items():
        row = {
            "clock_minute_et": clock_minute,
            "window_seconds": window_seconds,
            "baseline_candidate_id": candidate,
            **{key: value for key, value in entry.items() if key not in {"distributions", "sorted_values", "baseline_candidate_id"}},
        }
        for label, summary in entry.get("distributions", {}).items():
            for field, value in summary.items():
                row[f"baseline_{label}_{field}"] = value
        for label, values in entry.get("sorted_values", {}).items():
            sorted_values[(clock_minute, window_seconds, candidate, label)] = np.asarray(values, dtype=np.float64)
        rows.append(row)
    return pd.DataFrame(rows), sorted_values


def materialize_baseline_and_surprise_vectorized(
    current: pd.DataFrame,
    *,
    prior_current: pd.DataFrame,
    config: dict[str, Any],
    evaluation_session_date: date,
    cache_builder: Any = build_baseline_cache,
) -> pd.DataFrame:
    candidates = list(config["binding"]["baseline_candidates"])
    cache = cache_builder(
        prior_current,
        evaluation_session_date=evaluation_session_date,
        baseline_candidates=candidates,
    )
    cache_frame, sorted_values = _flat_cache(cache)
    work_columns = list(STATE_COLUMNS) + list(VALUE_COLUMNS.values()) + ["median_intertrade_duration_us"]
    work = current.loc[:, list(dict.fromkeys(work_columns))].copy()
    work["clock_minute_et"] = pd.to_datetime(work["decision_timestamp"], utc=True).dt.tz_convert("America/New_York").dt.strftime("%H:%M")
    candidate_frame = pd.DataFrame({"baseline_candidate_id": candidates})
    work = work.merge(candidate_frame, how="cross")
    keys = ["clock_minute_et", "window_seconds", "baseline_candidate_id"]
    if cache_frame.empty:
        frame = work
    else:
        frame = work.merge(cache_frame, on=keys, how="left", validate="many_to_one")

    frame["reference_session_count"] = frame.get("reference_session_count", 0).fillna(0)
    frame["reference_observation_count"] = frame.get("reference_observation_count", 0).fillna(0)
    frame["baseline_calculation_state"] = frame.get("baseline_calculation_state", pd.Series(index=frame.index, dtype="object")).fillna("BASELINE_INSUFFICIENT_HISTORY")
    frame["baseline_duration_calculation_state"] = frame.get("baseline_duration_calculation_state", pd.Series(index=frame.index, dtype="object")).fillna("BASELINE_INSUFFICIENT_HISTORY")
    for column in BASELINE_VALUE_COLUMNS:
        if column not in frame:
            frame[column] = np.nan

    available = frame["baseline_calculation_state"].isin(["BASELINE_AVAILABLE", "BASELINE_ZERO_DOMINATED"])
    grouped_indices = frame.groupby(keys, sort=False, observed=True).indices
    for group_key, indices in grouped_indices.items():
        if not available.iloc[indices].any():
            continue
        for label, source_column in VALUE_COLUMNS.items():
            values = sorted_values.get((*group_key, label))
            if values is None or not len(values):
                continue
            current_values = pd.to_numeric(frame.iloc[indices][source_column], errors="coerce").to_numpy(dtype=np.float64, na_value=np.nan)
            valid = ~np.isnan(current_values)
            result = np.full(len(indices), np.nan, dtype=np.float64)
            result[valid] = np.searchsorted(values, current_values[valid], side="right") / len(values)
            frame.loc[frame.index[indices], f"{label}_percentile_pit"] = result

    ratio_specs = (
        ("eligible_trade_count", "baseline_trade_count_unconditional_median", "trade_count_log_ratio_to_pit"),
        ("eligible_share_volume", "baseline_share_volume_unconditional_median", "share_volume_log_ratio_to_pit"),
        ("eligible_dollar_volume", "baseline_dollar_volume_unconditional_median", "dollar_volume_log_ratio_to_pit"),
    )
    for source, baseline, output in ratio_specs:
        source_values = pd.to_numeric(frame[source], errors="coerce")
        baseline_values = pd.to_numeric(frame[baseline], errors="coerce")
        valid = available & source_values.notna() & baseline_values.notna()
        frame.loc[valid, output] = np.log((source_values[valid].astype(float) + 1.0) / (baseline_values[valid].astype(float) + 1.0))

    current_duration = pd.to_numeric(frame["median_intertrade_duration_us"], errors="coerce")
    baseline_duration = pd.to_numeric(frame["baseline_median_intertrade_duration_us"], errors="coerce")
    valid_duration = available & current_duration.notna() & baseline_duration.notna()
    frame.loc[valid_duration, "intertrade_duration_compression"] = np.log((baseline_duration[valid_duration].astype(float) + 1.0) / (current_duration[valid_duration].astype(float) + 1.0))

    frame = frame.drop(columns=["clock_minute_et", *VALUE_COLUMNS.values(), "median_intertrade_duration_us"], errors="ignore")
    for column in BASELINE_VALUE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Float64")
    if "baseline_zero_dominated" not in frame:
        frame["baseline_zero_dominated"] = pd.NA
    frame["baseline_zero_dominated"] = frame["baseline_zero_dominated"].astype("boolean")
    _typed_numeric(frame, ("window_seconds", "subwindow_seconds", "reference_session_count", "reference_observation_count"), "Int64")
    for column in ("first_reference_date", "last_reference_date", "baseline_input_max_available_at"):
        if column not in frame:
            frame[column] = None
    _typed_utc(frame, ("decision_timestamp", "feature_input_max_available_at", "baseline_input_max_available_at"))
    frame["future_window_used"] = frame["future_window_used"].astype("boolean")
    leading_columns = [column for column in frame.columns if column not in BASELINE_RESULT_COLUMNS]
    return frame.reindex(columns=leading_columns + list(BASELINE_RESULT_COLUMNS))
