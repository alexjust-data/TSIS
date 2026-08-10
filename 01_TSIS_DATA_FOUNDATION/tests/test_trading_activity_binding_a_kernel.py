from __future__ import annotations

import importlib.util
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


kernel = load_module(
    "trading_activity_binding_a_kernel",
    ROOT / "scripts" / "trading_activity_binding_a_kernel.py",
)

OPEN = datetime(2026, 8, 6, 13, 30, tzinfo=timezone.utc)


def event(
    offset_seconds: float,
    *,
    available_offset_seconds: float | None = None,
    price: float = 2.0,
    size: int = 100,
    ordinal: int = 0,
    state: str = "ELIGIBLE_WITH_RESTRICTIONS",
):
    if available_offset_seconds is None:
        available_offset_seconds = offset_seconds
    return {
        "legacy_event_time": OPEN + timedelta(seconds=offset_seconds),
        "simulated_available_at": OPEN + timedelta(seconds=available_offset_seconds),
        "price": price,
        "size": size,
        "ordinal": ordinal,
        "eligibility_state": state,
    }


def compute(events, *, decision_offset=5, window=5, coverage=True):
    return kernel.compute_window_state(
        events,
        decision_timestamp=OPEN + timedelta(seconds=decision_offset),
        session_open=OPEN,
        window_seconds=window,
        coverage_gate_pass=coverage,
    )


def test_full_window_uses_fixed_denominator_and_open_left_boundary():
    result = compute([event(0), event(1), event(5)])
    assert result["eligible_trade_count"] == 2
    assert result["trade_arrival_rate"] == 2 / 5
    assert result["observable_seconds"] == 5


def test_simulated_availability_tie_is_included_but_future_availability_is_not():
    result = compute(
        [
            event(3, available_offset_seconds=5, ordinal=1),
            event(4, available_offset_seconds=5.001, ordinal=2),
        ]
    )
    assert result["eligible_trade_count"] == 1
    assert result["feature_input_max_available_at"] == OPEN + timedelta(seconds=5)


def test_one_trade_has_duration_insufficient_but_activity_calculated():
    result = compute([event(2)])
    assert result["calculation_state"] == "CALCULATED"
    assert result["duration_calculation_state"] == "INSUFFICIENT_SAMPLE"
    assert result["median_intertrade_duration_us"] is None


def test_same_timestamp_tie_preserves_zero_duration():
    result = compute([event(2, ordinal=1), event(2, ordinal=2)])
    assert result["eligible_trade_count"] == 2
    assert result["median_intertrade_duration_us"] == 0
    assert result["p10_intertrade_duration_us"] == 0


def test_zero_activity_is_observed_and_concentration_not_imputed():
    result = compute([])
    assert result["observation_state"] == "OBSERVED_ZERO"
    assert result["eligible_trade_count"] == 0
    assert result["concentration_calculation_state"] == "NOT_APPLICABLE_ZERO_ACTIVITY"
    assert result["active_subwindow_fraction"] is None


def test_unknown_condition_exposure_degrades_entire_window():
    result = compute([event(2, state="UNKNOWN_FAIL_CLOSED")])
    assert result["observation_state"] == "DEGRADED"
    assert result["eligible_trade_count"] is None
    assert result["degrading_event_count"] == 1


def test_incomplete_opening_window_and_failed_coverage_are_not_calculated():
    opening = compute([event(1)], decision_offset=4, window=5)
    failed = compute([event(1)], coverage=False)
    assert opening["calculation_state"] == "INSUFFICIENT_WINDOW_HISTORY"
    assert opening["eligible_trade_count"] is None
    assert opening["input_event_count"] == 1
    assert opening["feature_input_max_available_at"] is not None
    assert failed["calculation_state"] == "NOT_CALCULATED_COVERAGE_GATE_FAILED"
    assert failed["input_event_count"] is None
    assert failed["feature_input_max_available_at"] is None


def test_subwindow_boundaries_and_consecutive_activity_are_right_anchored():
    result = compute(
        [
            event(1, size=100),
            event(2, size=200),
            event(4.1, size=300),
        ]
    )
    assert result["active_subwindow_fraction"] == 3 / 5
    assert result["consecutive_active_subwindows"] == 2
    assert result["max_subwindow_volume_share"] == 0.5


def test_multiscale_log_ratio_uses_long_window_epsilon():
    short = {"trade_arrival_rate": 2.0, "window_seconds": 5}
    long = {"trade_arrival_rate": 0.5, "window_seconds": 60}
    expected = math.log((2 + 1 / 60) / (0.5 + 1 / 60))
    assert kernel.compute_multiscale_log_ratio(short, long) == expected
    assert kernel.compute_multiscale_log_ratio(
        {"trade_arrival_rate": None, "window_seconds": 5}, long
    ) is None


def reference_rows(session_count: int, *, include_current_and_future: bool = False):
    rows = []
    start = date(2026, 1, 1)
    for session_index in range(session_count):
        session_date = start + timedelta(days=session_index)
        value = 0 if session_index < 12 else 2
        for second in range(60):
            rows.append(
                {
                    "session_date": session_date,
                    "calculation_state": "CALCULATED",
                    "eligible_trade_count": value,
                    "eligible_share_volume": value * 100,
                    "eligible_dollar_volume": value * 200,
                    "trade_arrival_rate": value / 5,
                    "feature_input_max_available_at": datetime.combine(
                        session_date, datetime.min.time(), tzinfo=timezone.utc
                    ),
                }
            )
    if include_current_and_future:
        for extra_date in (date(2026, 2, 1), date(2026, 2, 2)):
            rows.append(
                {
                    "session_date": extra_date,
                    "calculation_state": "CALCULATED",
                    "eligible_trade_count": 1_000_000,
                    "eligible_share_volume": 1_000_000,
                    "eligible_dollar_volume": 1_000_000,
                    "trade_arrival_rate": 1_000_000,
                    "feature_input_max_available_at": datetime.combine(
                        extra_date, datetime.min.time(), tzinfo=timezone.utc
                    ),
                }
            )
    return rows


CURRENT = {
    "eligible_trade_count": 10,
    "eligible_share_volume": 1_000,
    "eligible_dollar_volume": 2_000,
    "trade_arrival_rate": 2.0,
}


def test_b20_baseline_is_pit_zero_aware_and_uses_typed_percentiles():
    result = kernel.compute_pit_baseline(
        reference_rows(15, include_current_and_future=True),
        CURRENT,
        current_session_date=date(2026, 2, 1),
        baseline_candidate_id="B20",
    )
    assert result["reference_session_count"] == 15
    assert result["last_reference_date"] < date(2026, 2, 1)
    assert result["baseline_calculation_state"] == "BASELINE_ZERO_DOMINATED"
    assert result["distributions"]["trade_count"]["zero_fraction"] == 0.8
    assert result["percentiles"]["trade_count"] == 1.0
    assert result["surprise"]["trade_count_log_ratio_to_pit"] == math.log(11)


def test_b60_fails_closed_with_39_reference_sessions():
    result = kernel.compute_pit_baseline(
        reference_rows(39),
        CURRENT,
        current_session_date=date(2026, 3, 1),
        baseline_candidate_id="B60",
    )
    assert result["reference_session_count"] == 39
    assert result["baseline_calculation_state"] == "BASELINE_INSUFFICIENT_HISTORY"
    assert result["surprise"] is None


def test_kernel_rebuild_is_deterministic():
    events = [event(1, ordinal=1), event(2, ordinal=2), event(4, ordinal=3)]
    assert compute(events) == compute(events)
