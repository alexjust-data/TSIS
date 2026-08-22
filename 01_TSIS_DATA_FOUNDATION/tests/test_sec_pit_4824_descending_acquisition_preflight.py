# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.build_4824_descending_acquisition_preflight import build_acquisition_order


def fixtures() -> tuple[pd.DataFrame, pd.DataFrame]:
    universe = pd.DataFrame({
        "ticker": ["CCC", "AAA", "BBB", "DDD", "EEE"],
        "first_seen_date": pd.to_datetime(["2020-01-01"] * 5),
        "last_observed_date": pd.to_datetime([
            "2025-02-01", "2026-03-09", "2026-03-09", "2024-12-31", "2023-01-01"
        ]),
        "status_rebuilt": ["active"] * 5,
    })
    master = pd.DataFrame({
        "instrument_id": ["i-c", "i-a", "i-b", "i-d", "i-e"],
        "ticker": ["CCC", "AAA", "BBB", "DDD", "EEE"],
        "cik": [3, 1, 2, 4, 5],
        "name": ["C", "A", "B", "D", "E"],
        "primary_exchange": ["X"] * 5,
        "share_class_figi": [f"f{i}" for i in range(5)],
        "is_common_stock": [True] * 5,
        "active_in_reference": [True] * 5,
    })
    return universe, master


def test_descending_order_and_exact_cohorts_are_deterministic() -> None:
    universe, master = fixtures()
    first = build_acquisition_order(
        universe, master, expected_count=5, cohort_sizes=[2, 1, 1, 1], shard_count=4
    )
    second = build_acquisition_order(
        universe.sample(frac=1, random_state=7),
        master.sample(frac=1, random_state=8),
        expected_count=5,
        cohort_sizes=[2, 1, 1, 1],
        shard_count=4,
    )
    assert first["ticker"].tolist() == ["AAA", "BBB", "CCC", "DDD", "EEE"]
    assert first["ticker"].tolist() == second["ticker"].tolist()
    assert first["cohort_sequence"].value_counts().sort_index().tolist() == [2, 1, 1, 1]
    assert first["cohort_selection_order"].tolist() == [1, 2, 1, 1, 1]
    assert first["last_observed_date"].is_monotonic_decreasing


def test_cohort_sizes_must_cover_the_complete_universe() -> None:
    universe, master = fixtures()
    with pytest.raises(ValueError, match="sum exactly"):
        build_acquisition_order(
            universe, master, expected_count=5, cohort_sizes=[2, 2], shard_count=4
        )


def test_missing_identity_or_cik_fails_closed() -> None:
    universe, master = fixtures()
    master.loc[master["ticker"].eq("DDD"), "cik"] = None
    with pytest.raises(ValueError, match="requires instrument identity and CIK"):
        build_acquisition_order(
            universe, master, expected_count=5, cohort_sizes=[5], shard_count=4
        )


def test_ticker_aliases_share_identity_but_remain_explicit_rows() -> None:
    universe, master = fixtures()
    master.loc[master["ticker"].eq("DDD"), "instrument_id"] = "i-a"
    frame = build_acquisition_order(
        universe, master, expected_count=5, cohort_sizes=[5], shard_count=4
    )
    aliases = frame.loc[frame["instrument_id"].eq("i-a")]
    assert set(aliases["ticker"]) == {"AAA", "DDD"}
    assert aliases["instrument_identity_reused_in_parent_universe"].all()
    assert aliases["instrument_identity_cik_conflict"].all()
    assert aliases["instrument_identity_tickers_json"].nunique() == 1
