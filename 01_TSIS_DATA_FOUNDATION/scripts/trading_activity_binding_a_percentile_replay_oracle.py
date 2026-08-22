"""Independent empirical-percentile replay for Trading Activity Binding A.

This module deliberately does not import any Trading Activity production engine.
It reconstructs the four governed empirical ranks directly from immutable
``current_state`` partitions using NumPy/PyArrow and compares them with the
materialized ``pit_baseline_and_surprise`` values.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ORACLE_ID = "trading_activity_binding_a_independent_percentile_replay_oracle_v0_1"
CANDIDATES = ("B20", "B60", "B120")
LOOKBACKS = {"B20": 20, "B60": 60, "B120": 120}
MINIMUM_SESSIONS = {"B20": 15, "B60": 40, "B120": 80}
VALUE_COLUMNS = {
    "trade_count": "eligible_trade_count",
    "share_volume": "eligible_share_volume",
    "dollar_volume": "eligible_dollar_volume",
    "arrival_rate": "trade_arrival_rate",
}
PERCENTILE_COLUMNS = {
    label: f"{label}_percentile_pit" for label in VALUE_COLUMNS
}
TOTAL_COUNT_COLUMNS = {
    label: f"baseline_{label}_total_count" for label in VALUE_COLUMNS
}
AVAILABLE_STATES = {"BASELINE_AVAILABLE", "BASELINE_ZERO_DOMINATED"}
HISTORY_COLUMNS = (
    "session_date",
    "decision_timestamp",
    "window_seconds",
    "calculation_state",
    *VALUE_COLUMNS.values(),
)
BASELINE_COLUMNS = (
    "decision_timestamp",
    "window_seconds",
    "baseline_candidate_id",
    "reference_session_count",
    "reference_observation_count",
    "first_reference_date",
    "last_reference_date",
    "baseline_calculation_state",
    "baseline_zero_dominated",
    *TOTAL_COUNT_COLUMNS.values(),
    *PERCENTILE_COLUMNS.values(),
)


def empirical_percentile(
    reference_values: np.ndarray, current_values: np.ndarray
) -> np.ndarray:
    """Return count(reference <= x) / N; ties are right-inclusive."""

    references = np.asarray(reference_values, dtype=np.float64)
    current = np.asarray(current_values, dtype=np.float64)
    result = np.full(current.shape, np.nan, dtype=np.float64)
    references = references[~np.isnan(references)]
    valid = ~np.isnan(current)
    if references.size and np.any(valid):
        ordered = np.sort(references, kind="quicksort")
        result[valid] = (
            np.searchsorted(ordered, current[valid], side="right")
            / float(ordered.size)
        )
    return result


def select_reference_dates(
    available_dates: np.ndarray, target_day: int, candidate: str
) -> np.ndarray:
    """Select the causal, group-local tail of unique session dates."""

    if candidate not in LOOKBACKS:
        raise ValueError(f"Unknown baseline candidate: {candidate}")
    dates = np.unique(np.asarray(available_dates, dtype=np.int32))
    dates = dates[dates < int(target_day)]
    return dates[-LOOKBACKS[candidate] :]


def _date_days(column: pa.ChunkedArray) -> np.ndarray:
    return column.cast(pa.int32()).to_numpy(zero_copy_only=False).astype(
        np.int32, copy=False
    )


def _nullable_float(column: pa.ChunkedArray) -> np.ndarray:
    return column.to_pandas().to_numpy(dtype=np.float64, na_value=np.nan)


def _nullable_int(column: pa.ChunkedArray) -> np.ndarray:
    return column.to_pandas().to_numpy(dtype=np.float64, na_value=np.nan)


def _clock_window_codes(
    timestamps: pa.ChunkedArray, windows: pa.ChunkedArray
) -> tuple[np.ndarray, np.ndarray]:
    stamps = pd.DatetimeIndex(timestamps.to_pandas())
    if stamps.tz is None:
        stamps = stamps.tz_localize("UTC")
    local = stamps.tz_convert("America/New_York")
    minute = np.asarray(local.hour * 60 + local.minute, dtype=np.int32)
    window = windows.to_numpy(zero_copy_only=False).astype(np.int32, copy=False)
    return (minute * 1000 + window).astype(np.int32, copy=False), stamps.asi8


@dataclass
class HistoryMatrix:
    group_code: np.ndarray
    session_day: np.ndarray
    calculated: np.ndarray
    values: dict[str, np.ndarray]
    group_bounds: dict[int, tuple[int, int]]
    row_count: int
    source_partition_count: int

    def group(self, code: int) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
        bounds = self.group_bounds.get(int(code))
        if bounds is None:
            empty_i = np.empty(0, dtype=np.int32)
            empty_b = np.empty(0, dtype=bool)
            return empty_i, empty_b, {
                label: np.empty(0, dtype=np.float64) for label in VALUE_COLUMNS
            }
        start, stop = bounds
        return (
            self.session_day[start:stop],
            self.calculated[start:stop],
            {label: values[start:stop] for label, values in self.values.items()},
        )


def load_history_matrix(
    paths: Iterable[Path],
    *,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> HistoryMatrix:
    """Load only replay columns and compact/sort them by minute-window/date."""

    path_list = list(paths)
    groups: list[np.ndarray] = []
    days: list[np.ndarray] = []
    calculated: list[np.ndarray] = []
    values: dict[str, list[np.ndarray]] = {label: [] for label in VALUE_COLUMNS}
    rows = 0
    for ordinal, path in enumerate(path_list, start=1):
        table = pq.ParquetFile(path).read(columns=list(HISTORY_COLUMNS))
        code, _ = _clock_window_codes(table["decision_timestamp"], table["window_seconds"])
        groups.append(code)
        days.append(_date_days(table["session_date"]))
        calculated.append(
            np.asarray(table["calculation_state"].to_pylist(), dtype=object)
            == "CALCULATED"
        )
        for label, column in VALUE_COLUMNS.items():
            values[label].append(_nullable_float(table[column]))
        rows += table.num_rows
        if progress is not None:
            progress(
                {
                    "stage": "LOAD_HISTORY",
                    "history_partitions_loaded": ordinal,
                    "history_partitions_total": len(path_list),
                    "history_rows_loaded": rows,
                    "current_item": str(path),
                }
            )

    group_array = np.concatenate(groups)
    day_array = np.concatenate(days)
    calculated_array = np.concatenate(calculated)
    value_arrays = {label: np.concatenate(parts) for label, parts in values.items()}
    order = np.lexsort((day_array, group_array))
    group_array = group_array[order]
    day_array = day_array[order]
    calculated_array = calculated_array[order]
    value_arrays = {label: array[order] for label, array in value_arrays.items()}
    unique, first, counts = np.unique(
        group_array, return_index=True, return_counts=True
    )
    bounds = {
        int(code): (int(start), int(start + count))
        for code, start, count in zip(unique, first, counts, strict=True)
    }
    return HistoryMatrix(
        group_code=group_array,
        session_day=day_array,
        calculated=calculated_array,
        values=value_arrays,
        group_bounds=bounds,
        row_count=rows,
        source_partition_count=len(path_list),
    )


def _record_mismatch(
    summary: dict[str, Any],
    column: str,
    count: int,
    *,
    examples: list[dict[str, Any]],
    candidate: str,
    code: int,
    target_indices: np.ndarray,
    actual: np.ndarray,
    expected: np.ndarray,
    cap: int,
) -> None:
    if count <= 0:
        return
    summary["mismatch_counts"][column] = (
        int(summary["mismatch_counts"].get(column, 0)) + int(count)
    )
    summary["mismatch_count"] += int(count)
    if len(examples) >= cap:
        return
    left_null = pd.isna(actual)
    right_null = pd.isna(expected)
    unequal = left_null != right_null
    both = ~(left_null | right_null)
    if np.any(both):
        unequal[both] |= actual[both] != expected[both]
    for local in np.flatnonzero(unequal)[: cap - len(examples)]:
        examples.append(
            {
                "column": column,
                "candidate": candidate,
                "clock_window_code": int(code),
                "current_row_index": int(target_indices[local]),
                "materialized": None if left_null[local] else actual[local].item() if hasattr(actual[local], "item") else actual[local],
                "replayed": None if right_null[local] else expected[local].item() if hasattr(expected[local], "item") else expected[local],
            }
        )


def _compare_array(
    summary: dict[str, Any],
    column: str,
    actual: np.ndarray,
    expected: np.ndarray,
    **context: Any,
) -> None:
    actual = np.asarray(actual)
    expected = np.asarray(expected)
    left_null = pd.isna(actual)
    right_null = pd.isna(expected)
    unequal = left_null != right_null
    both = ~(left_null | right_null)
    if np.any(both):
        unequal[both] |= actual[both] != expected[both]
    _record_mismatch(
        summary,
        column,
        int(np.count_nonzero(unequal)),
        actual=actual,
        expected=expected,
        **context,
    )


def audit_target_session(
    history: HistoryMatrix,
    *,
    current_path: Path,
    baseline_path: Path,
    mismatch_cap: int = 100,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Replay and compare every one of the four ranks for one target session."""

    current = pq.ParquetFile(current_path).read(columns=list(HISTORY_COLUMNS))
    baseline = pq.ParquetFile(baseline_path).read(columns=list(BASELINE_COLUMNS))
    current_codes, current_timestamps = _clock_window_codes(
        current["decision_timestamp"], current["window_seconds"]
    )
    current_days = _date_days(current["session_date"])
    if current.num_rows == 0 or np.unique(current_days).size != 1:
        raise AssertionError("Current target must contain exactly one non-empty session")
    target_day = int(current_days[0])
    n = current.num_rows
    if baseline.num_rows != n * len(CANDIDATES):
        raise AssertionError(
            f"Baseline cardinality {baseline.num_rows} != {n}*{len(CANDIDATES)}"
        )
    baseline_codes, baseline_timestamps = _clock_window_codes(
        baseline["decision_timestamp"], baseline["window_seconds"]
    )
    candidate_grid = np.asarray(
        baseline["baseline_candidate_id"].to_pylist(), dtype=object
    ).reshape(n, len(CANDIDATES))
    first_candidates = tuple(str(item) for item in candidate_grid[0])
    if set(first_candidates) != set(CANDIDATES) or not np.all(
        candidate_grid == np.asarray(first_candidates, dtype=object)
    ):
        raise AssertionError("Baseline candidate order is not stable per current row")
    candidate_column = {candidate: first_candidates.index(candidate) for candidate in CANDIDATES}
    if not np.array_equal(
        baseline_timestamps.reshape(n, len(CANDIDATES))[:, 0], current_timestamps
    ) or not np.array_equal(
        baseline_codes.reshape(n, len(CANDIDATES))[:, 0], current_codes
    ):
        raise AssertionError("Current/baseline row identity or order mismatch")
    for column in range(len(CANDIDATES)):
        if not np.array_equal(
            baseline_timestamps.reshape(n, len(CANDIDATES))[:, column],
            current_timestamps,
        ) or not np.array_equal(
            baseline_codes.reshape(n, len(CANDIDATES))[:, column], current_codes
        ):
            raise AssertionError("Baseline candidate rows do not repeat current identity")

    current_values = {
        label: _nullable_float(current[column])
        for label, column in VALUE_COLUMNS.items()
    }
    baseline_arrays: dict[str, np.ndarray] = {}
    for column in BASELINE_COLUMNS:
        if column in {"decision_timestamp", "window_seconds", "baseline_candidate_id"}:
            continue
        if column in {"first_reference_date", "last_reference_date"}:
            series = baseline[column].to_pandas()
            baseline_arrays[column] = series.to_numpy(dtype="datetime64[D]").astype("int64").astype(np.float64)
            baseline_arrays[column][series.isna().to_numpy()] = np.nan
        elif column in {"baseline_calculation_state"}:
            baseline_arrays[column] = np.asarray(baseline[column].to_pylist(), dtype=object)
        elif column == "baseline_zero_dominated":
            baseline_arrays[column] = np.asarray(baseline[column].to_pylist(), dtype=object)
        else:
            baseline_arrays[column] = _nullable_float(baseline[column])
        baseline_arrays[column] = baseline_arrays[column].reshape(n, len(CANDIDATES))

    summary: dict[str, Any] = {
        "status": "PASS",
        "target_session_date": date.fromordinal(target_day + date(1970, 1, 1).toordinal()).isoformat(),
        "current_path": str(current_path),
        "baseline_path": str(baseline_path),
        "current_rows": n,
        "baseline_rows": baseline.num_rows,
        "percentile_cells_checked": int(baseline.num_rows * len(PERCENTILE_COLUMNS)),
        "group_count": int(np.unique(current_codes).size),
        "mismatch_count": 0,
        "mismatch_counts": {},
        "mismatch_examples": [],
        "oracle_id": ORACLE_ID,
        "candidate_order_materialized": list(first_candidates),
    }
    groups = np.unique(current_codes)
    for group_ordinal, code in enumerate(groups, start=1):
        target_indices = np.flatnonzero(current_codes == code)
        history_days, history_calculated, history_values = history.group(int(code))
        available_dates = np.unique(history_days[history_days < target_day])
        for candidate in CANDIDATES:
            candidate_index = candidate_column[candidate]
            selected_dates = select_reference_dates(
                available_dates, target_day, candidate
            )
            minimum = MINIMUM_SESSIONS[candidate]
            if selected_dates.size:
                selected = (
                    (history_days >= int(selected_dates[0]))
                    & (history_days <= int(selected_dates[-1]))
                    & (history_days < target_day)
                    & history_calculated
                )
            else:
                selected = np.zeros(history_days.shape, dtype=bool)
            observation_count = int(np.count_nonzero(selected))
            field_references = {
                label: values[selected & ~np.isnan(values)]
                for label, values in history_values.items()
            }
            available = (
                selected_dates.size >= minimum
                and observation_count >= minimum
                and all(values.size >= minimum for values in field_references.values())
            )
            zero_dominated = (
                bool(np.count_nonzero(field_references["trade_count"] == 0) / field_references["trade_count"].size >= 0.80)
                if available
                else None
            )
            expected_state = (
                "BASELINE_ZERO_DOMINATED"
                if available and zero_dominated
                else "BASELINE_AVAILABLE"
                if available
                else "BASELINE_INSUFFICIENT_HISTORY"
            )
            col = candidate_index
            context = {
                "examples": summary["mismatch_examples"],
                "candidate": candidate,
                "code": int(code),
                "target_indices": target_indices,
                "cap": mismatch_cap,
            }
            _compare_array(
                summary,
                "reference_session_count",
                baseline_arrays["reference_session_count"][target_indices, col],
                np.full(target_indices.size, selected_dates.size, dtype=np.float64),
                **context,
            )
            _compare_array(
                summary,
                "reference_observation_count",
                baseline_arrays["reference_observation_count"][target_indices, col],
                np.full(target_indices.size, observation_count, dtype=np.float64),
                **context,
            )
            first_day = float(selected_dates[0]) if selected_dates.size else np.nan
            last_day = float(selected_dates[-1]) if selected_dates.size else np.nan
            for name, value in (("first_reference_date", first_day), ("last_reference_date", last_day)):
                _compare_array(
                    summary,
                    name,
                    baseline_arrays[name][target_indices, col],
                    np.full(target_indices.size, value, dtype=np.float64),
                    **context,
                )
            _compare_array(
                summary,
                "baseline_calculation_state",
                baseline_arrays["baseline_calculation_state"][target_indices, col],
                np.full(target_indices.size, expected_state, dtype=object),
                **context,
            )
            expected_zero = np.full(target_indices.size, zero_dominated, dtype=object)
            _compare_array(
                summary,
                "baseline_zero_dominated",
                baseline_arrays["baseline_zero_dominated"][target_indices, col],
                expected_zero,
                **context,
            )
            for label in VALUE_COLUMNS:
                total_column = TOTAL_COUNT_COLUMNS[label]
                percentile_column = PERCENTILE_COLUMNS[label]
                total = float(field_references[label].size) if available else np.nan
                replayed = (
                    empirical_percentile(
                        field_references[label], current_values[label][target_indices]
                    )
                    if available
                    else np.full(target_indices.size, np.nan, dtype=np.float64)
                )
                _compare_array(
                    summary,
                    total_column,
                    baseline_arrays[total_column][target_indices, col],
                    np.full(target_indices.size, total, dtype=np.float64),
                    **context,
                )
                _compare_array(
                    summary,
                    percentile_column,
                    baseline_arrays[percentile_column][target_indices, col],
                    replayed,
                    **context,
                )
        if progress is not None and (group_ordinal % 10 == 0 or group_ordinal == len(groups)):
            progress(
                {
                    "stage": "REPLAY_PERCENTILES",
                    "groups_completed_in_session": group_ordinal,
                    "groups_total_in_session": len(groups),
                    "current_item": f"clock_window_code={int(code)}",
                    "mismatch_count": summary["mismatch_count"],
                }
            )
        if summary["mismatch_count"] and len(summary["mismatch_examples"]) >= mismatch_cap:
            break
    summary["status"] = "PASS" if summary["mismatch_count"] == 0 else "FAIL"
    return summary
