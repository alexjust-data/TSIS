from __future__ import annotations

from pathlib import Path

import duckdb

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/short_context_table")
DATASET_DIR = OUTPUT_ROOT / "short_context_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_short_context_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_short_context_table_summary_v0_1.csv"

EXPECTED_SCOPE = "short_and_short_review_source_scoped_context_v0_1"

REQUIRED_COLUMNS = {
    "short_context_id",
    "ticker",
    "instrument_id",
    "source_dataset_id",
    "source_family",
    "source_system",
    "source_scope",
    "observation_family",
    "observation_date_type",
    "observation_date",
    "observation_year",
    "settlement_date",
    "trade_date",
    "as_of_date",
    "as_of_semantics",
    "short_interest",
    "avg_daily_volume",
    "days_to_cover",
    "total_volume",
    "short_volume",
    "exempt_volume",
    "non_exempt_volume",
    "short_volume_ratio",
    "nyse_short_volume",
    "nyse_short_volume_exempt",
    "nasdaq_carteret_short_volume",
    "nasdaq_carteret_short_volume_exempt",
    "nasdaq_chicago_short_volume",
    "nasdaq_chicago_short_volume_exempt",
    "adf_short_volume",
    "adf_short_volume_exempt",
    "orf_short_volume",
    "orf_short_volume_exempt",
    "local_certification_status",
    "local_certification_reason",
    "local_certified_date_start",
    "local_certified_date_end",
    "local_observation_inside_certified_window",
    "instrument_identity_temporal_match",
    "instrument_identity_state",
    "source_duplicate_key_flag",
    "source_duplicate_key_count",
    "source_duplicate_key_ordinal",
    "source_duplicate_excess_row",
    "finra_official_free_baseline",
    "local_polygon_operational_source",
    "short_volume_source_scope_not_consolidated_market_wide",
    "finra_pre_modern_short_interest_semantics_flag",
    "full_2005_2026_official_free_history_claim",
    "borrow_data_present",
    "ssr_data_present",
    "execution_truth",
    "requires_availability_lag_assumption",
    "same_day_intraday_causal_claim_allowed",
    "prohibited_without_asof_filter",
    "contains_future_information_without_event_filter",
    "short_quality_state",
    "valid_for_event_context_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_backtest_context_candidate",
    "valid_for_state_component_candidate",
    "valid_for_rl_training_direct",
    "source_root",
    "source_file",
    "source_file_relative_path",
    "source_file_row_number",
    "full_universe_claim",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
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


def test_short_context_manifest_hashes_contracts_and_sources(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "short_context_table_v0_1"
    assert manifest["schema_version"] == "short_context_table_v0_1"
    assert manifest["quality_policy_version"] == "short_context_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["full_universe_claim"] is False
    assert manifest["direct_rl_training_allowed"] is False
    assert manifest["borrow_data_present"] is False
    assert manifest["ssr_data_present"] is False
    assert manifest["execution_truth"] is False
    assert manifest["requires_availability_lag_assumption"] is True
    assert manifest["prohibited_without_asof_filter"] is True
    assert Path(manifest["dataset_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert_relative_contract_paths_exist(manifest)

    assert manifest["local_short_file_counts"] == {
        "short_interest_files": 4_824,
        "short_volume_files": 4_824,
    }
    assert manifest["finra_manifests"]["short_interest"]["rows"] == 505_745
    assert manifest["finra_manifests"]["short_volume"]["rows"] == 4_689_038
    assert len(manifest["source_file_hashes"]["finra_short_interest_all_biweekly"]) == 64
    assert len(manifest["source_file_hashes"]["finra_short_volume_all_daily"]) == 64

    write_json_artifact(
        tsis_artifacts_dir,
        "short_context_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "build_run_id": manifest["build_run_id"],
            "output_tree": manifest["output_tree"],
            "source_observation_counts": manifest["validations"]["source_observation_counts"],
        },
    )


def test_short_context_schema_counts_quality_and_source_planes(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    columns = set(
        duckdb.sql(
            f"describe select * from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)"
        ).fetchdf()["column_name"]
    )
    assert REQUIRED_COLUMNS <= columns

    assert validations["row_count"] == 7_145_337
    assert validations["unique_short_context_id_count"] == 7_145_337
    assert validations["duplicate_short_context_id_count"] == 0
    assert validations["ticker_count"] == 4_694
    assert validations["instrument_count"] == 4_462
    assert validations["first_observation_date"] == "2017-12-29"
    assert validations["last_observation_date"] == "2026-04-29"
    assert validations["source_system_counts"] == {
        "finra_official_free": 5_194_783,
        "local_polygon": 1_950_554,
    }
    assert validations["observation_family_counts"] == {
        "short_interest": 1_025_793,
        "short_volume": 6_119_544,
    }
    assert validations["source_observation_counts"] == {
        "finra_official_free:short_interest": {"rows": 505_745, "tickers": 4_687},
        "finra_official_free:short_volume": {"rows": 4_689_038, "tickers": 4_623},
        "local_polygon:short_interest": {"rows": 520_048, "tickers": 4_693},
        "local_polygon:short_volume": {"rows": 1_430_506, "tickers": 3_381},
    }
    assert validations["short_quality_state_counts"] == {
        "good_finra_official_free_short_interest_context": 306_856,
        "good_finra_official_free_short_volume_context": 4_528_387,
        "good_local_certified_short_interest_context": 130_656,
        "good_local_certified_short_volume_context": 114_128,
        "review_finra_pre_2021_short_interest_semantics": 160_406,
        "review_local_certification_status": 1_705_770,
        "review_no_temporal_identity": 193_060,
        "review_source_duplicate_key": 6_074,
    }

    assert _scalar(
        f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)"
    ) == validations["row_count"]

    write_json_artifact(
        tsis_artifacts_dir,
        "short_context_quality_source_planes.json",
        {
            "rows": validations["row_count"],
            "source_counts": validations["source_system_counts"],
            "quality_counts": validations["short_quality_state_counts"],
        },
    )


def test_short_context_duplicate_and_missing_family_guards() -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    assert validations["duplicate_key_rows"] == 6_074
    assert validations["duplicate_key_excess_rows"] == 5_250
    assert validations["finra_short_volume_duplicate_key_excess_rows"] == 5_250
    assert validations["bad_rows"] == 0
    assert validations["borrow_data_present_rows"] == 0
    assert validations["ssr_data_present_rows"] == 0
    assert validations["full_universe_claim_rows"] == 0
    assert validations["valid_for_rl_training_direct_rows"] == 0

    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where source_duplicate_excess_row
          and not (
              source_system = 'finra_official_free'
              and observation_family = 'short_volume'
          )
        """
    ) == 0
    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where borrow_data_present
           or ssr_data_present
           or execution_truth
           or full_universe_claim
           or valid_for_rl_training_direct
           or full_2005_2026_official_free_history_claim
           or not requires_availability_lag_assumption
           or same_day_intraday_causal_claim_allowed
           or not prohibited_without_asof_filter
           or not contains_future_information_without_event_filter
        """
    ) == 0


def test_short_context_gate_semantics_and_partitions(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    assert validations["valid_for_event_context_candidate_rows"] == 5_240_433
    assert validations["valid_for_ml_feature_candidate_rows"] == 5_080_027
    assert validations["valid_for_state_component_candidate_rows"] == 5_240_433
    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where valid_for_event_context_candidate
          and (
              source_duplicate_key_flag
              or not instrument_identity_temporal_match
              or observation_date is null
          )
        """
    ) == 0
    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where source_system = 'local_polygon'
          and valid_for_event_context_candidate
          and local_certification_status not in ('CERTIFIED_OK', 'CERTIFIED_OK_WITH_LIMITED_WINDOW')
        """
    ) == 0
    assert _scalar(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where finra_pre_modern_short_interest_semantics_flag
          and valid_for_ml_feature_candidate
        """
    ) == 0

    source_family_counts = _dict(
        f"""
        select source_system || ':' || observation_family as key, count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        group by key
        order by key
        """
    )
    assert source_family_counts == {
        key: value["rows"] for key, value in validations["source_observation_counts"].items()
    }

    write_json_artifact(
        tsis_artifacts_dir,
        "short_context_gate_semantics.json",
        {
            "valid_for_event_context_candidate_rows": validations[
                "valid_for_event_context_candidate_rows"
            ],
            "valid_for_ml_feature_candidate_rows": validations[
                "valid_for_ml_feature_candidate_rows"
            ],
            "source_family_counts": source_family_counts,
        },
    )
