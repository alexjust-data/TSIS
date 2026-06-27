from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    non_empty_string_mask,
    sha256_file,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/outcomes_table")
OUTPUT_PATH = OUTPUT_ROOT / "outcomes_table_v0_1.parquet"
MANIFEST_PATH = OUTPUT_ROOT / "_outcomes_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_outcomes_table_summary_v0_1.csv"

SOURCE_EVENT_WINDOWS = Path(
    "E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet"
)
SOURCE_MASTER_DAILY = Path("E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1")

EXPECTED_PRICE_VIEWS = {"daily_raw", "split_normalized", "adjusted"}
EXPECTED_SCOPE = "halt_next_session_daily_outcomes_v0_1"
EXPECTED_HORIZON = "next_session_regular_daily"

REQUIRED_COLUMNS = {
    "outcome_id",
    "event_window_id",
    "source_event_id",
    "event_source_dataset_id",
    "event_family",
    "event_type",
    "event_code",
    "ticker",
    "instrument_id",
    "event_session_date",
    "outcome_session_date",
    "outcome_horizon",
    "price_view",
    "event_time_utc",
    "window_role",
    "event_master_daily_id",
    "outcome_master_daily_id",
    "event_data_present",
    "outcome_data_present",
    "event_close",
    "outcome_open",
    "outcome_high",
    "outcome_low",
    "outcome_close",
    "event_close_to_outcome_open_return_pct",
    "event_close_to_outcome_high_return_pct",
    "event_close_to_outcome_low_return_pct",
    "event_close_to_outcome_close_return_pct",
    "label_next_close_positive",
    "label_next_close_ge_5pct",
    "label_next_close_ge_10pct",
    "label_next_close_le_minus_5pct",
    "label_next_close_le_minus_10pct",
    "label_next_high_ge_10pct",
    "label_next_high_ge_20pct",
    "label_next_low_le_minus_10pct",
    "label_next_open_ge_5pct",
    "label_next_open_le_minus_5pct",
    "outcome_quality_state",
    "valid_for_outcome_research",
    "valid_for_ml_label_candidate",
    "valid_for_strategy_label_candidate",
    "valid_for_backtest_outcome_candidate",
    "valid_for_rl_reward_candidate",
    "contains_post_event_information",
    "prohibited_as_pre_event_feature",
    "requires_feature_label_separation",
    "full_universe_claim",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "source_event_windows_table_sha256",
    "source_master_daily_table_tree_sha256",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _frame() -> pd.DataFrame:
    return duckdb.sql(f"select * from read_parquet('{OUTPUT_PATH.as_posix()}')").fetchdf()


def test_outcomes_manifest_hashes_contracts_and_sources(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "outcomes_table_v0_1"
    assert manifest["schema_version"] == "outcomes_table_v0_1"
    assert manifest["quality_policy_version"] == "outcomes_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["outcome_horizon"] == EXPECTED_HORIZON
    assert manifest["source_event_windows_dataset_id"] == "event_windows_table_v0_1"
    assert manifest["source_daily_dataset_id"] == "master_daily_table_v0_1"
    assert manifest["full_universe_claim"] is False
    assert OUTPUT_PATH.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == OUTPUT_PATH
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_file(OUTPUT_PATH) == manifest["output_sha256"]
    assert Path(manifest["source_event_windows_table"]) == SOURCE_EVENT_WINDOWS
    assert Path(manifest["source_master_daily_dataset"]) == SOURCE_MASTER_DAILY
    assert sha256_file(SOURCE_EVENT_WINDOWS) == manifest["source_event_windows_table_sha256"]
    assert sha256_parquet_tree(SOURCE_MASTER_DAILY) == manifest["source_master_daily_tree"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "outcomes_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "materialization_scope": manifest["materialization_scope"],
            "output_sha256": manifest["output_sha256"],
            "source_event_windows_table_sha256": manifest["source_event_windows_table_sha256"],
            "source_master_daily_tree": manifest["source_master_daily_tree"],
            "validations": manifest["validations"],
        },
    )


def test_outcomes_schema_counts_quality_and_gates(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    df = _frame()

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 128_388
    assert df["outcome_id"].nunique() == validations["unique_outcome_id_count"] == 128_388
    assert validations["duplicate_outcome_id_count"] == 0
    assert df["event_window_id"].nunique() == validations["event_window_count"] == 42_796
    assert df["source_event_id"].nunique() == validations["source_event_count"] == 42_796
    assert df["ticker"].nunique() == validations["ticker_count"] == 3_709
    assert df["instrument_id"].nunique() == validations["instrument_count"] == 3_566
    assert set(df["price_view"]) == EXPECTED_PRICE_VIEWS
    assert df["price_view"].nunique() == validations["price_view_count"] == 3
    assert set(df["outcome_horizon"]) == {EXPECTED_HORIZON}
    assert set(df["materialization_scope"]) == {EXPECTED_SCOPE}
    assert set(df["schema_version"]) == {"outcomes_table_v0_1"}
    assert set(df["quality_policy_version"]) == {"outcomes_table_policy_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert non_empty_string_mask(df["outcome_id"]).all()
    assert non_empty_string_mask(df["event_window_id"]).all()
    assert set(df["window_role"]) == {"next_session_regular"}

    assert validations["outcome_quality_state_counts"] == {
        "good_daily_outcome": 121_761,
        "review_outcome_daily_missing": 3_858,
        "review_event_and_outcome_daily_missing": 1_980,
        "review_event_daily_missing": 789,
    }
    assert validations["good_daily_outcome_rows"] == 121_761
    assert validations["review_rows"] == 6_627
    assert validations["event_data_present_rows"] == 125_619
    assert validations["outcome_data_present_rows"] == 122_550
    assert validations["valid_for_ml_label_candidate_rows"] == 121_761
    assert validations["valid_for_strategy_label_candidate_rows"] == 121_761
    assert validations["valid_for_backtest_outcome_candidate_rows"] == 121_761
    assert validations["valid_for_rl_reward_candidate_rows"] == 0
    assert validations["full_universe_claim_rows"] == 0
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_rl_reward_candidate"].any()
    assert df["contains_post_event_information"].all()
    assert df["prohibited_as_pre_event_feature"].all()
    assert df["requires_feature_label_separation"].all()
    assert df["valid_for_ml_label_candidate"].equals(df["outcome_quality_state"].eq("good_daily_outcome"))

    write_json_artifact(
        tsis_artifacts_dir,
        "outcomes_table_scope_quality_check.json",
        {
            "rows": int(len(df)),
            "event_windows": int(df["event_window_id"].nunique()),
            "quality_counts": validations["outcome_quality_state_counts"],
            "rows_by_price_view": validations["rows_by_price_view"],
        },
    )


def test_outcomes_price_view_grain_and_source_reconciliation(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    df = _frame()

    duplicate_keys = (
        df.groupby(["event_window_id", "outcome_horizon", "price_view"])
        .size()
        .reset_index(name="n")
        .query("n > 1")
    )
    assert duplicate_keys.empty

    by_window = df.groupby("event_window_id")["price_view"].nunique()
    assert by_window.min() == 3
    assert by_window.max() == 3

    source = pd.read_parquet(
        SOURCE_EVENT_WINDOWS,
        columns=["event_window_id", "window_role", "valid_for_outcome_window_candidate"],
    )
    expected_windows = source[
        source["window_role"].eq("next_session_regular")
        & source["valid_for_outcome_window_candidate"].eq(True)
    ]
    assert len(expected_windows) == 42_796
    assert set(df["event_window_id"]) == set(expected_windows["event_window_id"])
    assert len(df) == len(expected_windows) * len(EXPECTED_PRICE_VIEWS)

    for price_view, payload in manifest["validations"]["rows_by_price_view"].items():
        assert payload["rows"] == 42_796
        assert payload["event_data_present_rows"] == 41_873
        assert payload["outcome_data_present_rows"] == 40_850
        assert payload["good_daily_outcome_rows"] == 40_587
        assert payload["valid_for_ml_label_candidate_rows"] == 40_587

    write_json_artifact(
        tsis_artifacts_dir,
        "outcomes_table_source_reconciliation.json",
        {
            "expected_windows": int(len(expected_windows)),
            "output_rows": int(len(df)),
            "rows_by_price_view": manifest["validations"]["rows_by_price_view"],
        },
    )


def test_outcomes_return_math_labels_and_leakage_guards() -> None:
    df = _frame()
    good = df[df["outcome_quality_state"].eq("good_daily_outcome")].copy()

    assert not good.empty
    assert good["event_close"].gt(0).all()
    assert good["outcome_open"].gt(0).all()
    assert good["outcome_high"].gt(0).all()
    assert good["outcome_low"].gt(0).all()
    assert good["outcome_close"].gt(0).all()

    sample = good.sample(n=1000, random_state=7)
    expected_close_return = ((sample["outcome_close"] / sample["event_close"]) - 1.0) * 100.0
    max_abs_error = (expected_close_return - sample["event_close_to_outcome_close_return_pct"]).abs().max()
    assert max_abs_error < 1e-9

    assert sample["label_next_close_positive"].equals(
        sample["event_close_to_outcome_close_return_pct"].gt(0)
    )
    assert sample["label_next_close_ge_10pct"].equals(
        sample["event_close_to_outcome_close_return_pct"].ge(10.0)
    )
    assert sample["label_next_low_le_minus_10pct"].equals(
        sample["event_close_to_outcome_low_return_pct"].le(-10.0)
    )

    review = df[df["outcome_quality_state"].ne("good_daily_outcome")]
    assert not review["valid_for_ml_label_candidate"].any()
    assert not review["valid_for_strategy_label_candidate"].any()
    label_columns = [column for column in df.columns if column.startswith("label_")]
    assert not review[label_columns].any(axis=None)
