from datetime import date

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from test_trading_activity_binding_a_baseline_vectorized import _row
from trading_activity_binding_a_baseline_cpp import materialize_baseline_and_surprise_cpp
from trading_activity_binding_a_multisession_engine import materialize_baseline_and_surprise


def _row_at_et_minute(session: date, minute: int, window: int, count: int) -> dict:
    row = _row(session, 0, window, count)
    timestamp = (
        pd.Timestamp(f"{session.isoformat()} 09:30", tz="America/New_York")
        + pd.Timedelta(minutes=minute)
    ).tz_convert("UTC")
    row["decision_timestamp"] = timestamp
    row["feature_input_max_available_at"] = timestamp
    return row


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


def test_cpp_kernel_matches_reference_with_group_specific_sparse_history() -> None:
    evaluation = date(2025, 7, 1)
    sessions = [stamp.date() for stamp in pd.bdate_range("2025-01-02", periods=125)]
    rows: list[dict] = []
    for index, session in enumerate(sessions):
        full = _row_at_et_minute(session, 0, 5, index % 9)
        if index == 124:
            full["calculation_state"] = "INSUFFICIENT_SOURCE_DATA"
        rows.append(full)

        if index >= 6:
            sparse = _row_at_et_minute(session, 1, 5, (index + 3) % 11)
            if index == 80:
                sparse["feature_input_max_available_at"] = pd.NaT
            rows.append(sparse)

        if index >= 105:
            insufficient = _row_at_et_minute(session, 2, 15, (index + 5) % 7)
            if index == 110:
                insufficient["eligible_dollar_volume"] = np.nan
            rows.append(insufficient)

        if index >= 100:
            zero_dominated = _row_at_et_minute(session, 3, 30, 0 if index < 120 else 2)
            rows.append(zero_dominated)

    prior = pd.DataFrame(rows)
    current = pd.DataFrame(
        [
            _row_at_et_minute(evaluation, minute, window, value)
            for minute, window, value in (
                (0, 5, 3),
                (1, 5, 4),
                (2, 15, 5),
                (3, 30, 0),
                (4, 300, 7),
            )
        ]
    )
    config = {"binding": {"baseline_candidates": ["B20", "B60", "B120"]}}

    reference = materialize_baseline_and_surprise(
        current,
        prior_current=prior,
        config=config,
        evaluation_session_date=evaluation,
    )
    cpp = materialize_baseline_and_surprise_cpp(
        current,
        prior_current=prior,
        config=config,
        evaluation_session_date=evaluation,
    )

    assert_frame_equal(cpp, reference, check_dtype=True, rtol=1e-12, atol=1e-12)
    sparse_b120 = cpp.loc[
        (cpp["decision_timestamp"] == current.iloc[1]["decision_timestamp"])
        & (cpp["baseline_candidate_id"] == "B120")
    ].iloc[0]
    assert sparse_b120["reference_session_count"] == 119
    missing_group = cpp.loc[
        cpp["decision_timestamp"] == current.iloc[4]["decision_timestamp"]
    ]
    assert missing_group["reference_session_count"].eq(0).all()
