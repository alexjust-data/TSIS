"""DuckDB/C++ baseline-cache kernel for Trading Activity Binding A."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from trading_activity_binding_a_kernel import (
    BASELINE_LOOKBACKS,
    BASELINE_MIN_SESSIONS,
    POSITIVE_STAT_MINIMUMS,
)

FIELDS = {
    "trade_count": "eligible_trade_count",
    "share_volume": "eligible_share_volume",
    "dollar_volume": "eligible_dollar_volume",
    "arrival_rate": "trade_arrival_rate",
}


def _summary(row: Any, label: str) -> tuple[dict[str, Any], list[float]]:
    values = np.asarray(getattr(row, f"{label}_values"), dtype=np.float64)
    positive = values[values > 0]
    quantile_values = getattr(row, f"{label}_positive_quantiles")
    quantiles = [None] * 5 if quantile_values is None or quantile_values is pd.NA else list(quantile_values)
    positive_count = len(positive)
    positive_median = float(np.median(positive)) if positive_count >= POSITIVE_STAT_MINIMUMS["median"] else None
    positive_mad = float(np.median(np.abs(positive - positive_median))) if positive_count >= POSITIVE_STAT_MINIMUMS["mad"] else None
    summary = {
        "total_count": len(values),
        "zero_count": int(np.count_nonzero(values == 0)),
        "positive_count": positive_count,
        "zero_fraction": float(np.count_nonzero(values == 0) / len(values)),
        "unconditional_median": float(getattr(row, f"{label}_median")),
        "positive_median": positive_median,
        "positive_mad": positive_mad,
    }
    for index, name in enumerate(("p50", "p75", "p90", "p95", "p99")):
        summary[f"positive_{name}"] = float(quantiles[index]) if positive_count >= POSITIVE_STAT_MINIMUMS[name] else None
    return summary, values.tolist()


def build_baseline_cache_native(
    prior_current: pd.DataFrame,
    *,
    evaluation_session_date: date,
    baseline_candidates: Sequence[str],
    threads: int = 8,
) -> dict[tuple[str, int, str], dict[str, Any]]:
    prior = prior_current.copy()
    prior["session_day"] = pd.to_datetime(prior["session_date"]).dt.date
    prior = prior.loc[prior["session_day"] < evaluation_session_date].copy()
    timestamps = pd.to_datetime(prior["decision_timestamp"], utc=True).dt.tz_convert("America/New_York")
    prior["clock_minute_et"] = timestamps.dt.strftime("%H:%M")
    dates = sorted(prior["session_day"].unique())
    selection_rows: list[dict[str, Any]] = []
    candidate_dates: dict[str, list[date]] = {}
    for candidate in baseline_candidates:
        selected = dates[-BASELINE_LOOKBACKS[candidate] :]
        candidate_dates[candidate] = selected
        selection_rows.extend({"baseline_candidate_id": candidate, "session_day": value} for value in selected)
    selections = pd.DataFrame(selection_rows)
    if prior.empty or selections.empty:
        return {}

    aggregate_parts = []
    for label, field in FIELDS.items():
        aggregate_parts.extend([
            f"median({field}) AS {label}_median",
            f"quantile_disc({field}, [0.50,0.75,0.90,0.95,0.99]) FILTER (WHERE {field} > 0) AS {label}_positive_quantiles",
            f"list({field} ORDER BY {field}) FILTER (WHERE {field} IS NOT NULL) AS {label}_values",
        ])
    query = f"""
        SELECT s.baseline_candidate_id, p.clock_minute_et, p.window_seconds,
               count(*) AS reference_observation_count,
               max(p.feature_input_max_available_at) AS baseline_input_max_available_at,
               median(p.median_intertrade_duration_us) FILTER (WHERE p.median_intertrade_duration_us IS NOT NULL) AS duration_median,
               count(p.median_intertrade_duration_us) AS duration_count,
               {", ".join(aggregate_parts)}
        FROM prior p JOIN selections s USING (session_day)
        WHERE p.calculation_state = 'CALCULATED'
        GROUP BY s.baseline_candidate_id, p.clock_minute_et, p.window_seconds
    """
    connection = duckdb.connect(":memory:")
    try:
        connection.execute(f"SET threads={max(1, int(threads))}")
        connection.register("prior", prior)
        connection.register("selections", selections)
        aggregates = connection.execute(query).fetch_df()
    finally:
        connection.close()

    cache: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in aggregates.itertuples(index=False):
        candidate = str(row.baseline_candidate_id)
        selected_dates = candidate_dates[candidate]
        minimum = BASELINE_MIN_SESSIONS[candidate]
        base = {
            "baseline_candidate_id": candidate,
            "reference_session_count": len(selected_dates),
            "reference_observation_count": int(row.reference_observation_count),
            "first_reference_date": min(selected_dates) if selected_dates else None,
            "last_reference_date": max(selected_dates) if selected_dates else None,
            "baseline_input_max_available_at": row.baseline_input_max_available_at,
            "baseline_duration_calculation_state": "BASELINE_INSUFFICIENT_HISTORY",
            "baseline_median_intertrade_duration_us": None,
        }
        if len(selected_dates) < minimum or int(row.reference_observation_count) < minimum:
            entry = {**base, "baseline_calculation_state": "BASELINE_INSUFFICIENT_HISTORY"}
        else:
            distributions: dict[str, dict[str, Any]] = {}
            sorted_values: dict[str, list[float]] = {}
            for label in FIELDS:
                summary, values = _summary(row, label)
                distributions[label] = summary
                sorted_values[label] = values
            zero_dominated = distributions["trade_count"]["zero_fraction"] >= 0.80
            duration_available = int(row.duration_count) >= minimum
            entry = {
                **base,
                "baseline_calculation_state": "BASELINE_ZERO_DOMINATED" if zero_dominated else "BASELINE_AVAILABLE",
                "baseline_zero_dominated": zero_dominated,
                "baseline_duration_calculation_state": "BASELINE_AVAILABLE" if duration_available else "BASELINE_INSUFFICIENT_HISTORY",
                "baseline_median_intertrade_duration_us": float(row.duration_median) if duration_available else None,
                "distributions": distributions,
                "sorted_values": sorted_values,
            }
        cache[(str(row.clock_minute_et), int(row.window_seconds), candidate)] = entry
    return cache
