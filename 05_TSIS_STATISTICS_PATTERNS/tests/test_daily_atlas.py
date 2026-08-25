from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd
import pytest

from tsis_statistics_patterns.audit_probe import _expected_part_files
from tsis_statistics_patterns.contracts import AtlasConfig
from tsis_statistics_patterns.direct_cohorts import materialize_direct_activation_outputs
from tsis_statistics_patterns.direct_events import materialize_direct_activation_event_statistics
from tsis_statistics_patterns.episodes import build_atlas_tables
from tsis_statistics_patterns.features import compute_session_observables
from tsis_statistics_patterns.io import canonical_source_daily_file, load_raw_ticker


def _config() -> AtlasConfig:
    return AtlasConfig(
        trajectory_sessions=4,
        episode_cooldown_sessions=4,
        relative_volume_sessions=3,
        resistance_sessions={"previous_day": 1, "previous_week": 3},
        gap_thresholds=(0.10, 0.30),
        close_advance_thresholds=(0.20,),
        relative_volume_thresholds=(3.0,),
        range_thresholds=(0.20,),
    )


def _fixture() -> pd.DataFrame:
    dates = pd.date_range("2024-01-02", periods=10, freq="B")
    close = np.array([10, 10, 10, 10, 11, 15, 16, 14, 13, 12], dtype=float)
    open_ = np.array([10, 10, 10, 10, 10, 14, 15, 16, 14, 13], dtype=float)
    high = np.array([10.5, 10.5, 10.5, 10.5, 11.5, 16, 18, 16.5, 14.5, 13.5])
    low = np.array([9.5, 9.5, 9.5, 9.5, 9.8, 13.5, 14.5, 13.5, 12.5, 11.5])
    volume = np.array([100, 100, 100, 100, 120, 1000, 700, 500, 300, 200], dtype=float)
    return pd.DataFrame(
        {
            "ticker": "XYZ",
            "date": dates,
            "o": open_,
            "h": high,
            "l": low,
            "c": close,
            "v": volume,
            "o_split_normalized": open_,
            "h_split_normalized": high,
            "l_split_normalized": low,
            "c_split_normalized": close,
        }
    )


def test_session_features_use_only_current_and_prior_rows() -> None:
    frame = _fixture()
    early = compute_session_observables(frame.iloc[:7], _config())
    full = compute_session_observables(frame, _config()).iloc[:7]
    pd.testing.assert_frame_equal(early.reset_index(drop=True), full.reset_index(drop=True))


def test_gap_relative_volume_and_resistance_formulas() -> None:
    sessions = compute_session_observables(_fixture(), _config())
    activation = sessions.iloc[5]
    assert activation["gap_pct"] == pytest.approx(14 / 11 - 1)
    assert activation["relative_volume"] == pytest.approx(1000 / 100)
    assert bool(activation["high_breakout_previous_week"])
    assert activation["close_location"] == pytest.approx((15 - 13.5) / (16 - 13.5))


def test_flat_candle_close_location_is_null() -> None:
    frame = _fixture()
    frame.loc[4, ["o", "h", "l", "c"]] = 11.0
    frame.loc[4, ["o_split_normalized", "h_split_normalized", "l_split_normalized", "c_split_normalized"]] = 11.0
    sessions = compute_session_observables(frame, _config())
    assert pd.isna(sessions.loc[4, "close_location"])


def test_duplicate_session_is_rejected() -> None:
    frame = pd.concat([_fixture(), _fixture().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        compute_session_observables(frame, _config())


def test_activation_labels_are_multilabel_and_observable() -> None:
    sessions = compute_session_observables(_fixture(), _config())
    tables = build_atlas_tables(sessions, _config())
    labels = tables.activations.loc[tables.activations["date"].eq(pd.Timestamp("2024-01-09"))]
    assert {"gap", "relative_volume", "resistance_breakout"}.issubset(
        set(labels["activation_family"])
    )
    assert set(labels["knowledge_role"]) == {"observable"}


def test_episode_outcomes_are_separate_and_censored() -> None:
    sessions = compute_session_observables(_fixture(), _config())
    tables = build_atlas_tables(sessions, _config())
    assert "horizon_peak_offset" not in tables.sessions.columns
    assert "future_split_factor" not in tables.sessions.columns
    assert set(tables.trajectories["knowledge_role"]) == {"outcome"}
    assert tables.episodes["episode_id"].is_unique
    assert not tables.trajectories.duplicated(["episode_id", "offset_session"]).any()


def test_first_red_day_and_horizon_peak_are_distinct_events() -> None:
    sessions = compute_session_observables(_fixture(), _config())
    tables = build_atlas_tables(sessions, _config())
    episode_id = tables.episodes.iloc[0]["episode_id"]
    events = tables.events.loc[tables.events["episode_id"].eq(episode_id)]
    first_red = events.loc[events["event_label"].eq("first_red_candle")].iloc[0]
    peak = events.loc[events["event_label"].eq("horizon_peak")].iloc[0]
    assert first_red["offset_session"] > peak["offset_session"]
    assert first_red["knowledge_role"] == "outcome"



def test_nonpositive_price_is_retained_but_not_activation_eligible() -> None:
    frame = _fixture()
    frame.loc[5, ["o", "h", "l", "c"]] = 0.0
    frame.loc[5, ["o_split_normalized", "h_split_normalized", "l_split_normalized", "c_split_normalized"]] = 0.0
    sessions = compute_session_observables(frame, _config())
    tables = build_atlas_tables(sessions, _config())
    assert len(sessions) == len(frame)
    assert not bool(sessions.loc[5, "analysis_eligible"])
    assert sessions.loc[5, "quality_state"] == "invalid_ohlcv"
    assert not tables.activations["date"].eq(sessions.loc[5, "date"]).any()

def test_invalid_future_session_is_auditable_but_not_an_event() -> None:
    frame = _fixture()
    frame.loc[6, ["o", "h", "l", "c"]] = [15.0, 10_000.0, 20_000.0, 16.0]
    frame.loc[6, ["o_split_normalized", "h_split_normalized", "l_split_normalized", "c_split_normalized"]] = [15.0, 10_000.0, 20_000.0, 16.0]
    sessions = compute_session_observables(frame, _config())
    tables = build_atlas_tables(sessions, _config())
    invalid_trajectory = tables.trajectories.loc[tables.trajectories["date"].eq(frame.loc[6, "date"])]
    assert not invalid_trajectory.empty
    assert not invalid_trajectory["analysis_eligible"].any()
    assert set(invalid_trajectory["quality_state"]) == {"invalid_ohlcv"}
    invalid_date = frame.loc[6, "date"]
    assert not tables.events["event_date"].eq(invalid_date).any()
    episode = tables.episodes.iloc[0]
    assert episode["horizon_peak_date"] != invalid_date
    invalid_outcome = invalid_trajectory.iloc[0]
    assert pd.isna(invalid_outcome["close_from_anchor_pct"])
    assert pd.isna(invalid_outcome["high_from_anchor_pct"])
    assert pd.isna(invalid_outcome["drawdown_from_running_high_pct"])
    assert not bool(invalid_outcome["is_new_episode_high"])


def test_threshold_names_keep_percent_and_multiple_units_distinct() -> None:
    sessions = compute_session_observables(_fixture(), _config())
    labels = build_atlas_tables(sessions, _config()).activations["activation_label"].tolist()
    assert "relative_volume_ge_3x" in labels
    assert "gap_ge_10pct" in labels

def test_numeric_output_schema_is_stable_for_integer_source_volume() -> None:
    frame = _fixture()
    frame["v"] = frame["v"].astype("int64")
    sessions = compute_session_observables(frame, _config())
    tables = build_atlas_tables(sessions, _config())
    assert str(sessions["v"].dtype) == "float64"
    assert str(tables.trajectories["v"].dtype) == "float64"

def test_split_normalized_view_avoids_raw_split_gap_and_drops_factor() -> None:
    frame = _fixture()
    frame["future_split_factor"] = 2.0
    frame.loc[5:, ["o", "h", "l", "c"]] /= 2.0
    sessions = compute_session_observables(frame, _config())
    assert sessions.loc[5, "gap_pct"] == pytest.approx(14 / 11 - 1)
    assert "future_split_factor" not in sessions.columns


def test_null_price_is_retained_and_marked_invalid() -> None:
    frame = _fixture()
    frame.loc[6, "h_split_normalized"] = np.nan
    sessions = compute_session_observables(frame, _config())
    assert len(sessions) == len(frame)
    assert not bool(sessions.loc[6, "analysis_eligible"])
    assert sessions.loc[6, "quality_state"] == "invalid_ohlcv"


def test_tied_horizon_peak_uses_first_observation() -> None:
    frame = _fixture()
    frame.loc[6, ["h", "h_split_normalized"]] = 18.0
    frame.loc[7, ["h", "h_split_normalized"]] = 18.0
    sessions = compute_session_observables(frame, _config())
    episode = build_atlas_tables(sessions, _config()).episodes.iloc[0]
    assert episode["horizon_peak_offset"] == 2


def test_right_censoring_is_explicit_when_fewer_than_horizon_rows_exist() -> None:
    cfg = AtlasConfig(
        trajectory_sessions=6,
        episode_cooldown_sessions=6,
        relative_volume_sessions=3,
        resistance_sessions={"previous_day": 1},
        gap_thresholds=(10.0,),
        close_advance_thresholds=(10.0,),
        relative_volume_thresholds=(100.0,),
        range_thresholds=(10.0,),
    )
    sessions = compute_session_observables(_fixture(), cfg)
    episode = build_atlas_tables(sessions, cfg).episodes.iloc[0]
    assert not bool(episode["complete_horizon"])
    assert bool(episode["right_censored"])
    assert episode["observed_sessions"] < cfg.trajectory_sessions + 1


def test_legacy_source_path_maps_to_canonical_raw_root() -> None:
    resolved = canonical_source_daily_file(
        r"D:\ohlcv_daily\ticker=XYZ\year=2024\day_aggs_XYZ_2024.parquet"
    )
    assert resolved == "G:/TSIS/data/ohlcv_daily/ticker=XYZ/year=2024/day_aggs_XYZ_2024.parquet"

def test_direct_cohorts_and_event_stats_reconcile_all_activation_labels(tmp_path) -> None:
    sessions = compute_session_observables(_fixture(), _config())
    activations = build_atlas_tables(sessions, _config()).activations
    sessions.to_parquet(tmp_path / "session_observables.parquet", index=False)
    activations.to_parquet(tmp_path / "activation_labels.parquet", index=False)

    con = duckdb.connect()
    try:
        materialize_direct_activation_outputs(con, tmp_path, 4)
        materialize_direct_activation_event_statistics(con, tmp_path, 4)
    finally:
        con.close()

    expected = activations.groupby("activation_label").size().sort_index()
    cohorts = pd.read_parquet(tmp_path / "cohort_statistics.parquet")
    d0 = cohorts.loc[cohorts["offset_session"].eq(0)].set_index("activation_label")
    pd.testing.assert_series_equal(
        d0["activation_cases"].astype("int64").sort_index(),
        expected.astype("int64"),
        check_names=False,
    )

    event_stats = pd.read_parquet(tmp_path / "activation_event_statistics.parquet")
    assert set(event_stats["event_label"].unique()) == {
        "horizon_peak",
        "first_red_candle",
        "first_red_candle_after_d0",
        "first_lower_close",
        "first_lower_high",
        "first_day_without_new_episode_high",
    }
    for label, rows in event_stats.groupby("activation_label"):
        assert rows["activation_cases"].nunique() == 1
        assert int(rows["activation_cases"].iloc[0]) == int(expected.loc[label])

    case_index = pd.read_parquet(tmp_path / "activation_case_index.parquet")
    assert len(case_index) == len(activations[["ticker", "date"]].drop_duplicates())


def test_audit_part_cardinality_uses_run_mode() -> None:
    cfg = {"sharding": {"count": 8}}
    full = {"mode": "full", "expected_scope": {"tickers": 4824}}
    probe = {"mode": "probe", "limit_tickers_per_shard": 1}
    assert _expected_part_files(full, cfg) == 4824
    assert _expected_part_files(probe, cfg) == 8


def test_raw_loader_uses_vendor_split_adjusted_prices_without_reapplying_splits(tmp_path) -> None:
    root = tmp_path / "ohlcv_daily"
    part = root / "ticker=IBG" / "year=2026"
    part.mkdir(parents=True)
    pd.DataFrame(
        {
            "ticker": ["IBG", "IBG"],
            "date": ["2026-01-29", "2026-01-30"],
            "year": [2026, 2026],
            "o": [3.1, 3.5], "h": [3.4, 3.8], "l": [3.0, 3.4],
            "c": [3.3525, 3.73], "v": [49334.0, 100000.0],
            "vw": [3.2, 3.6], "n": [100, 200], "t": [1, 2],
        }
    ).to_parquet(part / "day_aggs_IBG_2026.parquet", index=False)
    result = load_raw_ticker(root, "IBG")
    assert result["c_split_normalized"].tolist() == [3.3525, 3.73]
    assert result["c_split_normalized"].equals(result["c"])
    assert set(result["materialized_price_view"]) == {
        "massive_adjusted_true_split_adjusted_v0_1"
    }