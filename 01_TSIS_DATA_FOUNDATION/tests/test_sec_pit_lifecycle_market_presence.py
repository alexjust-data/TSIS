from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

RUNNER_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "sec_pit"
    / "reconcile_lifecycle_market_presence.py"
)
SPEC = importlib.util.spec_from_file_location("reconcile_lifecycle_market_presence", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_daily_presence_is_bounded_by_identity_window(tmp_path: Path) -> None:
    ticker_root = tmp_path / "ticker=TEST" / "year=2025"
    ticker_root.mkdir(parents=True)
    pd.DataFrame(
        {"date": ["2024-12-31", "2025-01-02", "2025-01-03", "2025-02-01"]}
    ).to_parquet(ticker_root / "daily.parquet", index=False)

    result = RUNNER.daily_presence(ticker_root.parent, "2025-01-01", "2025-01-31")

    assert result["daily_observation_count"] == 2
    assert result["first_observed_daily_date"] == "2025-01-02"
    assert result["last_observed_daily_date"] == "2025-01-03"


def test_trade_presence_preserves_naive_timestamp_semantics(tmp_path: Path) -> None:
    ticker_root = tmp_path / "TEST"
    day_root = ticker_root / "year=2025" / "month=01" / "day=2025-01-02"
    day_root.mkdir(parents=True)
    pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2025-01-02 13:30:00.100", "2025-01-02 20:59:59.900"]
            )
        }
    ).to_parquet(day_root / "market.parquet", index=False)

    result = RUNNER.trade_presence(ticker_root, "2025-01-01", "2025-01-31")

    assert result["trade_presence_state"] == "OBSERVED_TAPE_BOUNDS_WITHIN_IDENTITY_WINDOW"
    assert str(result["first_observed_trade_timestamp_source_naive"]).startswith(
        "2025-01-02 13:30:00.100"
    )
    assert result["trade_timestamp_semantics"] == "SOURCE_NAIVE_REQUIRES_TIMEZONE_REVIEW"


def test_missing_tape_is_unavailable_not_zero(tmp_path: Path) -> None:
    result = RUNNER.trade_presence(tmp_path / "MISSING", "2025-01-01", "2025-01-31")

    assert result["trade_presence_state"] == "TAPE_SOURCE_UNAVAILABLE"
    assert result["first_observed_trade_timestamp_source_naive"] is None
    assert result["last_observed_trade_timestamp_source_naive"] is None

def test_cross_source_boundary_difference_is_preserved() -> None:
    daily = {
        "first_observed_daily_date": "2025-01-02",
        "last_observed_daily_date": "2025-01-31",
    }
    trades = {
        "first_observed_trade_timestamp_source_naive": pd.Timestamp(
            "2025-01-03 13:30:00"
        ),
        "last_observed_trade_timestamp_source_naive": pd.Timestamp(
            "2025-01-31 20:59:59"
        ),
    }

    assert (
        RUNNER.cross_source_boundary_state(daily, trades)
        == "CROSS_SOURCE_BOUNDARY_DATE_DIFFERENCE"
    )