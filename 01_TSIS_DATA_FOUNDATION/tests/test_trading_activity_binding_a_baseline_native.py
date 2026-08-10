from datetime import date

import pandas as pd
from test_trading_activity_binding_a_baseline_vectorized import _row
from trading_activity_binding_a_baseline_native import build_baseline_cache_native
from trading_activity_binding_a_multisession_engine import build_baseline_cache


def test_native_cache_matches_reference_cache() -> None:
    evaluation = date(2025, 3, 3)
    prior = pd.DataFrame([
        _row(date(2025, 1, day), second, window, (day + second + window) % 7)
        for day in range(1, 21)
        for second in range(3)
        for window in (5, 15)
    ])
    candidates = ["B20"]
    reference = build_baseline_cache(prior, evaluation_session_date=evaluation, baseline_candidates=candidates)
    native = build_baseline_cache_native(prior, evaluation_session_date=evaluation, baseline_candidates=candidates, threads=2)
    assert native.keys() == reference.keys()
    for key in reference:
        assert native[key]["baseline_calculation_state"] == reference[key]["baseline_calculation_state"]
        assert native[key]["distributions"] == reference[key]["distributions"]
        assert native[key]["sorted_values"] == reference[key]["sorted_values"]


def test_native_cache_handles_zero_only_groups() -> None:
    evaluation = date(2025, 3, 3)
    prior = pd.DataFrame([
        _row(date(2025, 1, day), second, 5, 0)
        for day in range(1, 21)
        for second in range(3)
    ])
    cache = build_baseline_cache_native(
        prior,
        evaluation_session_date=evaluation,
        baseline_candidates=["B20"],
        threads=2,
    )
    assert cache[("09:30", 5, "B20")]["distributions"]["trade_count"]["positive_p99"] is None