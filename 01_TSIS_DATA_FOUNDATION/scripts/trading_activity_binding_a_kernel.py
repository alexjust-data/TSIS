#!/usr/bin/env python3
"""Pure computational kernel for experimental Trading Activity Binding A."""

from __future__ import annotations

import math
import statistics
from datetime import date, datetime, timedelta
from typing import Any, Iterable


WINDOW_SECONDS = (5, 15, 30, 60, 300)
SHORT_LONG_PAIRS = ((5, 60), (15, 300))
BASELINE_LOOKBACKS = {"B20": 20, "B60": 60, "B120": 120}
BASELINE_MIN_SESSIONS = {"B20": 15, "B60": 40, "B120": 80}
POSITIVE_STAT_MINIMUMS = {
    "median": 10,
    "mad": 10,
    "p50": 10,
    "p75": 20,
    "p90": 50,
    "p95": 100,
    "p99": 500,
}


def _event_in_window(event: dict[str, Any], left: datetime, right: datetime) -> bool:
    return (
        left < event["legacy_event_time"] <= right
        and event["simulated_available_at"] <= right
    )


def _nearest_rank(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("nearest-rank quantile requires at least one value")
    ordered = sorted(values)
    rank = max(1, math.ceil(probability * len(ordered)))
    return float(ordered[rank - 1])


def _maximum_consecutive_active(counts: list[int]) -> int:
    best = current = 0
    for count in counts:
        current = current + 1 if count > 0 else 0
        best = max(best, current)
    return best


def _null_current_values() -> dict[str, Any]:
    return {
        "eligible_trade_count": None,
        "eligible_share_volume": None,
        "eligible_dollar_volume": None,
        "trade_arrival_rate": None,
        "median_intertrade_duration_us": None,
        "p10_intertrade_duration_us": None,
        "largest_trade_volume_share": None,
        "active_subwindow_fraction": None,
        "max_subwindow_trade_share": None,
        "max_subwindow_volume_share": None,
        "consecutive_active_subwindows": None,
        "input_event_count": None,
        "feature_input_max_available_at": None,
    }


def compute_window_state(
    events: Iterable[dict[str, Any]],
    *,
    decision_timestamp: datetime,
    session_open: datetime,
    window_seconds: int,
    coverage_gate_pass: bool,
) -> dict[str, Any]:
    if window_seconds not in WINDOW_SECONDS:
        raise ValueError(f"Unregistered window: {window_seconds}")
    left = decision_timestamp - timedelta(seconds=window_seconds)
    event_list = list(events)
    base = {
        "decision_timestamp": decision_timestamp,
        "window_seconds": window_seconds,
        "subwindow_seconds": 1 if window_seconds <= 30 else 5,
        "future_window_used": False,
        "observable_seconds": window_seconds,
    }

    if not coverage_gate_pass:
        return {
            **base,
            **_null_current_values(),
            "observation_state": "DEGRADED",
            "calculation_state": "NOT_CALCULATED_COVERAGE_GATE_FAILED",
            "duration_calculation_state": "NOT_CALCULATED_COVERAGE_GATE_FAILED",
            "concentration_calculation_state": "NOT_CALCULATED_COVERAGE_GATE_FAILED",
            "degrading_event_count": 0,
        }

    if left < session_open:
        visible = [
            event
            for event in event_list
            if session_open < event["legacy_event_time"] <= decision_timestamp
            and event["simulated_available_at"] <= decision_timestamp
            and event["eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS"
        ]
        return {
            **base,
**_null_current_values(),
            "input_event_count": len(visible),
            "feature_input_max_available_at": (
                max(event["simulated_available_at"] for event in visible)
                if visible
                else None
            ),
            "observation_state": "OBSERVED_NONZERO" if visible else "OBSERVED_ZERO",
            "calculation_state": "INSUFFICIENT_WINDOW_HISTORY",
            "duration_calculation_state": "INSUFFICIENT_WINDOW_HISTORY",
            "concentration_calculation_state": "INSUFFICIENT_WINDOW_HISTORY",
            "degrading_event_count": 0,
        }

    degrading = [
        event
        for event in event_list
        if event.get("eligibility_state") == "UNKNOWN_FAIL_CLOSED"
        and _event_in_window(event, left, decision_timestamp)
    ]
    if degrading:
        return {
            **base,
            **_null_current_values(),
            "observation_state": "DEGRADED",
            "calculation_state": "NOT_CALCULATED_COVERAGE_GATE_FAILED",
            "duration_calculation_state": "NOT_CALCULATED_COVERAGE_GATE_FAILED",
            "concentration_calculation_state": "NOT_CALCULATED_COVERAGE_GATE_FAILED",
            "degrading_event_count": len(degrading),
        }

    eligible = [
        event
        for event in event_list
        if event.get("eligibility_state") == "ELIGIBLE_WITH_RESTRICTIONS"
        and _event_in_window(event, left, decision_timestamp)
    ]
    eligible.sort(key=lambda event: (event["legacy_event_time"], event["ordinal"]))
    count = len(eligible)
    shares = sum(float(event["size"]) for event in eligible)
    dollars = sum(float(event["price"]) * float(event["size"]) for event in eligible)
    result = {
        **base,
        "observation_state": "OBSERVED_NONZERO" if count else "OBSERVED_ZERO",
        "calculation_state": "CALCULATED",
        "eligible_trade_count": count,
        "eligible_share_volume": shares,
        "eligible_dollar_volume": dollars,
        "trade_arrival_rate": count / window_seconds,
        "input_event_count": count,
        "feature_input_max_available_at": (
            max(event["simulated_available_at"] for event in eligible)
            if eligible
            else None
        ),
        "degrading_event_count": 0,
    }

    if count >= 2:
        durations_us = [
            (current["legacy_event_time"] - previous["legacy_event_time"]).total_seconds()
            * 1_000_000
            for previous, current in zip(eligible, eligible[1:])
        ]
        result.update(
            {
                "median_intertrade_duration_us": float(statistics.median(durations_us)),
                "p10_intertrade_duration_us": _nearest_rank(durations_us, 0.10),
                "duration_calculation_state": "CALCULATED",
            }
        )
    else:
        result.update(
            {
                "median_intertrade_duration_us": None,
                "p10_intertrade_duration_us": None,
                "duration_calculation_state": "INSUFFICIENT_SAMPLE",
            }
        )

    if count == 0:
        result.update(
            {
                "largest_trade_volume_share": None,
                "active_subwindow_fraction": None,
                "max_subwindow_trade_share": None,
                "max_subwindow_volume_share": None,
                "consecutive_active_subwindows": None,
                "concentration_calculation_state": "NOT_APPLICABLE_ZERO_ACTIVITY",
            }
        )
        return result

    subwindow_seconds = result["subwindow_seconds"]
    subwindow_count = window_seconds // subwindow_seconds
    trade_counts = [0] * subwindow_count
    volume_counts = [0.0] * subwindow_count
    for event in eligible:
        offset = (event["legacy_event_time"] - left).total_seconds()
        index = min(subwindow_count - 1, math.ceil(offset / subwindow_seconds) - 1)
        trade_counts[index] += 1
        volume_counts[index] += float(event["size"])
    result.update(
        {
            "largest_trade_volume_share": max(float(event["size"]) for event in eligible)
            / shares,
            "active_subwindow_fraction": sum(count > 0 for count in trade_counts)
            / subwindow_count,
            "max_subwindow_trade_share": max(trade_counts) / count,
            "max_subwindow_volume_share": max(volume_counts) / shares,
            "consecutive_active_subwindows": _maximum_consecutive_active(trade_counts),
            "concentration_calculation_state": "CALCULATED",
        }
    )
    return result


def compute_multiscale_log_ratio(
    short_state: dict[str, Any], long_state: dict[str, Any]
) -> float | None:
    short_rate = short_state.get("trade_arrival_rate")
    long_rate = long_state.get("trade_arrival_rate")
    if short_rate is None or long_rate is None:
        return None
    try:
        short_rate_value = float(short_rate)
        long_rate_value = float(long_rate)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(short_rate_value) or not math.isfinite(long_rate_value):
        return None
    epsilon_rate = 1 / int(long_state["window_seconds"])
    return math.log(
        (short_rate_value + epsilon_rate) / (long_rate_value + epsilon_rate)
    )


def _session_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _mad(values: list[float]) -> float:
    center = float(statistics.median(values))
    return float(statistics.median(abs(value - center) for value in values))


def _distribution_summary(values: list[float]) -> dict[str, Any]:
    positive = [value for value in values if value > 0]
    zeros = sum(value == 0 for value in values)
    summary: dict[str, Any] = {
        "total_count": len(values),
        "zero_count": zeros,
        "positive_count": len(positive),
        "zero_fraction": zeros / len(values),
        "unconditional_median": float(statistics.median(values)),
        "positive_median": None,
        "positive_mad": None,
        "positive_p50": None,
        "positive_p75": None,
        "positive_p90": None,
        "positive_p95": None,
        "positive_p99": None,
    }
    if len(positive) >= POSITIVE_STAT_MINIMUMS["median"]:
        summary["positive_median"] = float(statistics.median(positive))
    if len(positive) >= POSITIVE_STAT_MINIMUMS["mad"]:
        summary["positive_mad"] = _mad(positive)
    for label, probability in (
        ("p50", 0.50),
        ("p75", 0.75),
        ("p90", 0.90),
        ("p95", 0.95),
        ("p99", 0.99),
    ):
        if len(positive) >= POSITIVE_STAT_MINIMUMS[label]:
            summary[f"positive_{label}"] = _nearest_rank(positive, probability)
    return summary


def compute_pit_baseline(
    reference_rows: Iterable[dict[str, Any]],
    current_state: dict[str, Any],
    *,
    current_session_date: date,
    baseline_candidate_id: str,
) -> dict[str, Any]:
    if baseline_candidate_id not in BASELINE_LOOKBACKS:
        raise ValueError(f"Unknown baseline candidate: {baseline_candidate_id}")
    prior = [
        row
        for row in reference_rows
        if _session_date(row["session_date"]) < current_session_date
        and row.get("calculation_state") == "CALCULATED"
    ]
    prior_dates = sorted({_session_date(row["session_date"]) for row in prior})
    selected_dates = set(prior_dates[-BASELINE_LOOKBACKS[baseline_candidate_id] :])
    selected = [row for row in prior if _session_date(row["session_date"]) in selected_dates]
    minimum = BASELINE_MIN_SESSIONS[baseline_candidate_id]
    base = {
        "baseline_candidate_id": baseline_candidate_id,
        "reference_session_count": len(selected_dates),
        "reference_observation_count": len(selected),
        "first_reference_date": min(selected_dates) if selected_dates else None,
        "last_reference_date": max(selected_dates) if selected_dates else None,
        "baseline_input_max_available_at": max(
            (
                row.get("feature_input_max_available_at")
                for row in selected
                if row.get("feature_input_max_available_at") is not None
            ),
            default=None,
        ),
    }
    if len(selected_dates) < minimum or len(selected) < minimum:
        return _insufficient_baseline(base)

    variables = {
        "trade_count": "eligible_trade_count",
        "share_volume": "eligible_share_volume",
        "dollar_volume": "eligible_dollar_volume",
        "arrival_rate": "trade_arrival_rate",
    }
    distributions: dict[str, dict[str, Any]] = {}
    percentiles: dict[str, float | None] = {}
    for label, field in variables.items():
        values = [float(row[field]) for row in selected if row.get(field) is not None]
        if len(values) < minimum:
            return _insufficient_baseline(base)
        distributions[label] = _distribution_summary(values)
        current = current_state.get(field)
        percentiles[label] = (
            sum(value <= float(current) for value in values) / len(values)
            if current is not None
            else None
        )

    surprise = None
    if all(
        current_state.get(field) is not None
        for field in (
            "eligible_trade_count",
            "eligible_share_volume",
            "eligible_dollar_volume",
        )
    ):
        surprise = {
            "trade_count_log_ratio_to_pit": math.log(
                (float(current_state["eligible_trade_count"]) + 1)
                / (distributions["trade_count"]["unconditional_median"] + 1)
            ),
            "share_volume_log_ratio_to_pit": math.log(
                (float(current_state["eligible_share_volume"]) + 1)
                / (distributions["share_volume"]["unconditional_median"] + 1)
            ),
            "dollar_volume_log_ratio_to_pit": math.log(
                (float(current_state["eligible_dollar_volume"]) + 1)
                / (distributions["dollar_volume"]["unconditional_median"] + 1)
            ),
        }
    zero_dominated = distributions["trade_count"]["zero_fraction"] >= 0.80
    return {
        **base,
        "baseline_calculation_state": (
            "BASELINE_ZERO_DOMINATED" if zero_dominated else "BASELINE_AVAILABLE"
        ),
        "baseline_zero_dominated": zero_dominated,
        "distributions": distributions,
        "surprise": surprise,
        "percentiles": percentiles,
    }


def _insufficient_baseline(base: dict[str, Any]) -> dict[str, Any]:
    return {
        **base,
        "baseline_calculation_state": "BASELINE_INSUFFICIENT_HISTORY",
        "baseline_zero_dominated": None,
        "distributions": None,
        "surprise": None,
        "percentiles": None,
    }

