from datetime import UTC, date, datetime

import pandas as pd
from pandas.testing import assert_frame_equal
from trading_activity_binding_a_baseline_vectorized import (
    materialize_baseline_and_surprise_vectorized,
)
from trading_activity_binding_a_multisession_engine import materialize_baseline_and_surprise


def _row(session_date: date, second: int, window: int, count: int) -> dict:
    timestamp = pd.Timestamp(datetime.combine(session_date, datetime.min.time(), tzinfo=UTC)) + pd.Timedelta(hours=14, minutes=30, seconds=second)
    return {
        "feature_spec_id": "spec", "feature_version": "v0_2", "binding_id": "binding",
        "scope_id": "scope", "pilot_scope_id": "pilot", "instrument_id": "fixture:TST",
        "ticker": "TST", "session_date": session_date, "decision_timestamp": timestamp,
        "window_seconds": window, "subwindow_seconds": 1, "trade_eligibility_policy_id": "eligible",
        "duplicate_policy_id": "duplicate", "latency_policy_id": "latency", "source_dataset_id": "raw",
        "source_schema_version": "v1", "market_calendar_build_run_id": "calendar",
        "instrument_master_build_run_id": "identity", "foundation_quality_label": "GOOD",
        "local_window_disposition": "USABLE", "quality_state": "OBSERVED",
        "coverage_state": "OBSERVED_COMPLETE_REQUEST", "coverage_mode": "FULL",
        "calculation_state": "CALCULATED", "feature_input_max_available_at": timestamp,
        "lineage_manifest_id": "lineage", "future_window_used": False,
        "eligible_trade_count": count, "eligible_share_volume": count * 100,
        "eligible_dollar_volume": count * 250.0, "trade_arrival_rate": count / window,
        "median_intertrade_duration_us": 1000.0 / count if count else None,
    }


def test_vectorized_kernel_matches_reference() -> None:
    evaluation = date(2025, 3, 3)
    prior = pd.DataFrame([
        _row(date(2025, 1, day), second, window, (day + second + window) % 7)
        for day in range(1, 21)
        for second in range(3)
        for window in (5, 15)
    ])
    current = pd.DataFrame([_row(evaluation, second, window, second + 2) for second in range(3) for window in (5, 15)])
    config = {"binding": {"baseline_candidates": ["B20"]}}
    reference = materialize_baseline_and_surprise(current, prior_current=prior, config=config, evaluation_session_date=evaluation)
    vectorized = materialize_baseline_and_surprise_vectorized(current, prior_current=prior, config=config, evaluation_session_date=evaluation)
    assert_frame_equal(vectorized, reference, check_like=False, check_dtype=True, rtol=1e-12, atol=1e-12)
