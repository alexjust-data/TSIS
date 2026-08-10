from datetime import date

import pandas as pd
from pandas.testing import assert_frame_equal
from test_trading_activity_binding_a_baseline_vectorized import _row
from trading_activity_binding_a_baseline_cpp import materialize_baseline_and_surprise_cpp
from trading_activity_binding_a_multisession_engine import materialize_baseline_and_surprise


def test_cpp_kernel_matches_reference() -> None:
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
    cpp = materialize_baseline_and_surprise_cpp(current, prior_current=prior, config=config, evaluation_session_date=evaluation)
    assert_frame_equal(cpp, reference, check_dtype=True, rtol=1e-12, atol=1e-12)
