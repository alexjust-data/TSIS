from __future__ import annotations

from pathlib import Path

import duckdb

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/regime_context_table")
DATASET_DIR = OUTPUT_ROOT / "regime_context_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_regime_context_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_regime_context_table_summary_v0_1.csv"

EXPECTED_SCOPE = "regime_indicators_minute_aggregated_daily_context_v0_1"

REQUIRED_COLUMNS = {
    "regime_context_id",
    "regime_symbol",
    "source_symbol_dir",
    "regime_proxy_role",
    "source_dataset_id",
    "source_granularity",
    "context_granularity",
    "trading_date",
    "session_open_utc",
    "as_of_utc",
    "as_of_date",
    "as_of_semantics",
    "first_bar_timestamp",
    "last_bar_timestamp",
    "bars_observed",
    "distinct_timestamp_count",
    "duplicate_timestamp_rows",
    "bar_coverage_state",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "previous_close_price",
    "intraday_return",
    "close_to_previous_close_return",
    "high_to_open_return",
    "low_to_open_return",
    "intraday_range_pct",
    "volume",
    "vwap",
    "null_ohlc_bar_count",
    "non_positive_price_bar_count",
    "source_bad_ohlc_bar_count",
    "negative_volume_bar_count",
    "missing_volume_bar_count",
    "missing_vwap_bar_count",
    "market_calendar_covered",
    "session_minutes",
    "is_early_close",
    "market_calendar",
    "market_timezone",
    "timestamp_timezone_state",
    "daily_source_files_blocked",
    "built_from_blocked_day_parquet",
    "built_from_minute_parquet",
    "intraday_regime_features_source_included",
    "regime_quality_state",
    "valid_for_event_context_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_state_component_candidate",
    "valid_for_backtest_core_direct",
    "valid_for_rl_training_direct",
    "requires_asof_filter",
    "contains_future_information_without_event_filter",
    "same_session_intraday_causal_claim_allowed",
    "execution_truth",
    "source_root",
    "source_file",
    "source_file_relative_path",
    "market_calendar_source",
    "market_calendar_build_run_id",
    "market_calendar_schema_version",
    "full_universe_claim",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
    "observation_year",
    "source_proxy_family",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _glob() -> str:
    return (DATASET_DIR / "**" / "*.parquet").as_posix()


def _connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("pragma threads=8")
    return con


def _scalar(sql: str):
    con = _connect()
    return con.execute(sql).fetchone()[0]


def _dict(sql: str) -> dict[str, int]:
    con = _connect()
    return {str(key): int(value) for key, value in con.execute(sql).fetchall()}


def test_regime_context_manifest_hashes_contracts_and_sources(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "regime_context_table_v0_1"
    assert manifest["schema_version"] == "regime_context_table_v0_1"
    assert manifest["quality_policy_version"] == "regime_context_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["full_universe_claim"] is False
    assert manifest["direct_rl_training_allowed"] is False
    assert manifest["execution_truth"] is False
    assert manifest["requires_asof_filter"] is True
    assert manifest["contains_future_information_without_event_filter"] is True
    assert manifest["same_session_intraday_causal_claim_allowed"] is False
    assert Path(manifest["dataset_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert_relative_contract_paths_exist(manifest)

    source_inventory = manifest["source_inventory"]
    assert source_inventory["minute_file_count"] == 33
    assert source_inventory["day_file_count_blocked"] == 34
    assert source_inventory["minute_row_count"] == 64_348_953
    assert source_inventory["minute_total_bytes"] == 1_213_579_950

    source_semantics = manifest["source_semantics"]
    assert source_semantics["used_source_granularity"] == "minute.parquet"
    assert source_semantics["blocked_source_granularity"] == "day.parquet"
    assert source_semantics["intraday_regime_features_included"] is False
    assert (
        source_semantics["timestamp_timezone_state"]
        == "vendor_naive_timestamp_review"
    )
    assert (
        source_semantics["as_of_semantics"]
        == "session_close_aggregate_from_minute_bars"
    )

    write_json_artifact(
        tsis_artifacts_dir,
        "regime_context_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "build_run_id": manifest["build_run_id"],
            "output_tree": manifest["output_tree"],
            "source_inventory": {
                "minute_file_count": source_inventory["minute_file_count"],
                "day_file_count_blocked": source_inventory["day_file_count_blocked"],
                "minute_row_count": source_inventory["minute_row_count"],
            },
        },
    )


def test_regime_context_schema_counts_and_quality(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    columns = set(
        duckdb.sql(
            f"describe select * from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)"
        ).fetchdf()["column_name"]
    )
    assert REQUIRED_COLUMNS <= columns

    assert validations["row_count"] == 154_692
    assert validations["unique_regime_context_id_count"] == 154_692
    assert validations["duplicate_regime_context_id_count"] == 0
    assert validations["regime_symbol_count"] == 33
    assert validations["first_trading_date"] == "2004-01-02"
    assert validations["last_trading_date"] == "2025-12-02"
    assert validations["calendar_covered_rows"] == 145_478
    assert validations["no_calendar_rows"] == 9_214
    assert validations["quality_state_counts"] == {
        "good_minute_aggregated_regime_context": 143_840,
        "review_no_market_calendar_session": 9_214,
        "review_source_bar_integrity": 107,
        "review_sparse_minute_coverage": 1_531,
    }
    assert validations["source_proxy_family_counts"] == {
        "etf": 154_603,
        "index": 89,
    }
    assert validations["source_minute_rows_aggregated"] == 64_348_953
    assert validations["source_bad_ohlc_bar_count"] == 2_109
    assert validations["duplicate_timestamp_rows"] == 0
    assert validations["bad_rows"] == 0
    assert validations["hard_fail_count"] == 0

    assert _scalar(
        f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)"
    ) == validations["row_count"]

    write_json_artifact(
        tsis_artifacts_dir,
        "regime_context_quality_counts.json",
        {
            "rows": validations["row_count"],
            "quality_counts": validations["quality_state_counts"],
            "source_proxy_family_counts": validations["source_proxy_family_counts"],
        },
    )


def test_regime_context_source_and_leakage_guards() -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    assert validations["built_from_blocked_day_parquet_rows"] == 0
    assert validations["intraday_regime_features_source_included_rows"] == 0
    assert validations["built_from_minute_parquet_rows"] == 154_692
    assert validations["daily_source_files_blocked_rows"] == 154_692
    assert validations["valid_for_backtest_core_direct_rows"] == 0
    assert validations["valid_for_rl_training_direct_rows"] == 0

    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where built_from_blocked_day_parquet
           or not built_from_minute_parquet
           or intraday_regime_features_source_included
           or valid_for_backtest_core_direct
           or valid_for_rl_training_direct
           or execution_truth
           or full_universe_claim
           or not requires_asof_filter
           or not contains_future_information_without_event_filter
           or same_session_intraday_causal_claim_allowed
        """
    ) == 0


def test_regime_context_gate_semantics_and_role_counts(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    assert validations["valid_for_event_context_candidate_rows"] == 143_840
    assert validations["valid_for_ml_feature_candidate_rows"] == 143_834
    assert validations["valid_for_state_component_candidate_rows"] == 143_840

    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where valid_for_event_context_candidate
          and (
              regime_quality_state <> 'good_minute_aggregated_regime_context'
              or not market_calendar_covered
              or bars_observed < 60
              or source_bad_ohlc_bar_count <> 0
              or built_from_blocked_day_parquet
              or intraday_regime_features_source_included
          )
        """
    ) == 0

    assert _scalar(
        f"""
        select coalesce(sum(bars_observed), 0)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        """
    ) == validations["source_minute_rows_aggregated"]

    role_counts = _dict(
        f"""
        select regime_proxy_role, count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        group by regime_proxy_role
        order by regime_proxy_role
        """
    )
    assert role_counts == {
        "broad_market_large_cap": 11_736,
        "credit_liquidity": 10_327,
        "currency_proxy": 9_836,
        "energy_commodity": 10_126,
        "international_equity": 11_229,
        "nasdaq_composite_index": 23,
        "nasdaq_growth_tech": 4_274,
        "precious_metals": 10_817,
        "rates_duration": 5_682,
        "sector_etf": 55_079,
        "small_cap_proxy": 13_374,
        "volatility_etp": 12_189,
    }

    write_json_artifact(
        tsis_artifacts_dir,
        "regime_context_gate_semantics.json",
        {
            "valid_for_event_context_candidate_rows": validations[
                "valid_for_event_context_candidate_rows"
            ],
            "valid_for_ml_feature_candidate_rows": validations[
                "valid_for_ml_feature_candidate_rows"
            ],
            "regime_proxy_role_counts": role_counts,
        },
    )
