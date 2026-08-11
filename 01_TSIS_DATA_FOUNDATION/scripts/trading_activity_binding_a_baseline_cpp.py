"""Python adapter for the compiled TSIS Trading Activity baseline kernel."""

from __future__ import annotations

import importlib.util
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from trading_activity_binding_a_baseline_vectorized import STATE_COLUMNS, VALUE_COLUMNS
from trading_activity_binding_a_kernel import BASELINE_LOOKBACKS, BASELINE_MIN_SESSIONS
from trading_activity_binding_a_multisession_engine import (
    BASELINE_DISTRIBUTION_FIELDS,
    BASELINE_LABELS,
    BASELINE_RESULT_COLUMNS,
    BASELINE_VALUE_COLUMNS,
    _typed_numeric,
    _typed_utc,
)


@lru_cache(maxsize=1)
def native_module_path() -> Path:
    build = Path(__file__).parents[1] / "native" / "trading_activity" / "build"
    candidates = list(build.glob("tsis_baseline_native_cpp*.pyd"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one compiled native module, found {len(candidates)}")
    return candidates[0].resolve()


@lru_cache(maxsize=1)
def _load_native() -> Any:
    module_path = native_module_path()
    spec = importlib.util.spec_from_file_location("tsis_baseline_native_cpp", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load native baseline module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _minute(values: pd.Series) -> np.ndarray:
    timestamps = pd.to_datetime(values, utc=True).dt.tz_convert("America/New_York")
    return (timestamps.dt.hour * 60 + timestamps.dt.minute).to_numpy(dtype=np.int16)


def _ordinals(values: pd.Series) -> np.ndarray:
    return np.asarray([pd.Timestamp(value).date().toordinal() for value in values], dtype=np.int32)


def materialize_baseline_and_surprise_cpp(
    current: pd.DataFrame,
    *,
    prior_current: pd.DataFrame,
    config: dict[str, Any],
    evaluation_session_date: date,
) -> pd.DataFrame:
    native = _load_native()
    candidates = list(config["binding"]["baseline_candidates"])
    prior_days = _ordinals(prior_current["session_date"])
    evaluation_ordinal = evaluation_session_date.toordinal()
    prior_values = np.column_stack([
        pd.to_numeric(prior_current[column], errors="coerce").to_numpy(dtype=np.float64, na_value=np.nan)
        for column in (*VALUE_COLUMNS.values(), "median_intertrade_duration_us")
    ])
    current_values = np.column_stack([
        pd.to_numeric(current[column], errors="coerce").to_numpy(dtype=np.float64, na_value=np.nan)
        for column in (*VALUE_COLUMNS.values(), "median_intertrade_duration_us")
    ])
    available = pd.to_datetime(prior_current["feature_input_max_available_at"], utc=True, errors="coerce").astype("int64").to_numpy(copy=True)
    result = native.compute(
        prior_days,
        _minute(prior_current["decision_timestamp"]),
        pd.to_numeric(prior_current["window_seconds"], errors="raise").to_numpy(dtype=np.int16),
        prior_current["calculation_state"].eq("CALCULATED").to_numpy(dtype=np.uint8),
        prior_values,
        available,
        _minute(current["decision_timestamp"]),
        pd.to_numeric(current["window_seconds"], errors="raise").to_numpy(dtype=np.int16),
        current_values,
        np.asarray([BASELINE_LOOKBACKS[candidate] for candidate in candidates], dtype=np.int32),
        np.asarray([BASELINE_MIN_SESSIONS[candidate] for candidate in candidates], dtype=np.int32),
        evaluation_ordinal,
    )
    candidate_count = len(candidates)
    frame = current.loc[current.index.repeat(candidate_count), list(STATE_COLUMNS)].reset_index(drop=True)
    frame["baseline_candidate_id"] = np.tile(np.asarray(candidates, dtype=object), len(current))
    frame["reference_session_count"] = result["reference_sessions"]
    frame["reference_observation_count"] = result["reference_observations"]
    frame["first_reference_date"] = [date.fromordinal(int(value)) if value else None for value in result["first_reference"]]
    frame["last_reference_date"] = [date.fromordinal(int(value)) if value else None for value in result["last_reference"]]
    max_available = np.asarray(result["max_available"], dtype=np.int64)
    max_available[max_available == np.iinfo(np.int64).min] = np.iinfo(np.int64).min
    frame["baseline_input_max_available_at"] = pd.to_datetime(max_available, utc=True, errors="coerce")
    state = np.asarray(result["state"])
    frame["baseline_calculation_state"] = np.select([state == 1, state == 2], ["BASELINE_AVAILABLE", "BASELINE_ZERO_DOMINATED"], default="BASELINE_INSUFFICIENT_HISTORY")
    zero = np.asarray(result["zero_dominated"])
    frame["baseline_zero_dominated"] = pd.array([None if value < 0 else bool(value) for value in zero], dtype="boolean")
    duration_state = np.asarray(result["duration_state"])
    frame["baseline_duration_calculation_state"] = np.where(duration_state == 1, "BASELINE_AVAILABLE", "BASELINE_INSUFFICIENT_HISTORY")

    distributions = np.asarray(result["distributions"])
    column_index = 0
    for label in BASELINE_LABELS:
        for field in BASELINE_DISTRIBUTION_FIELDS:
            frame[f"baseline_{label}_{field}"] = distributions[:, column_index]
            column_index += 1
    percentiles = np.asarray(result["percentiles"])
    for index, label in enumerate(BASELINE_LABELS):
        frame[f"{label}_percentile_pit"] = percentiles[:, index]
    ratios = np.asarray(result["ratios"])
    for index, label in enumerate(("trade_count", "share_volume", "dollar_volume")):
        frame[f"{label}_log_ratio_to_pit"] = ratios[:, index]
    durations = np.asarray(result["durations"])
    frame["baseline_median_intertrade_duration_us"] = durations[:, 0]
    frame["intertrade_duration_compression"] = durations[:, 1]

    for column in BASELINE_VALUE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Float64")
    _typed_numeric(frame, ("window_seconds", "subwindow_seconds", "reference_session_count", "reference_observation_count"), "Int64")
    _typed_utc(frame, ("decision_timestamp", "feature_input_max_available_at", "baseline_input_max_available_at"))
    frame["future_window_used"] = frame["future_window_used"].astype("boolean")
    leading = [column for column in frame.columns if column not in BASELINE_RESULT_COLUMNS]
    return frame.reindex(columns=leading + list(BASELINE_RESULT_COLUMNS))
