from __future__ import annotations

from pathlib import Path

import duckdb

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/news_context_table")
DATASET_DIR = OUTPUT_ROOT / "news_context_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_news_context_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_news_context_table_summary_v0_1.csv"

EXPECTED_SCOPE = "additional_news_lt1b_published_utc_context_v0_1"
EXPECTED_SOURCE_ROOT = "E:/TSIS/data/additional/news"

REQUIRED_COLUMNS = {
    "news_context_id",
    "ticker",
    "source_path_ticker",
    "instrument_id",
    "source_dataset_id",
    "source_subblock",
    "article_id",
    "article_url",
    "article_url_hash",
    "title",
    "title_hash",
    "author",
    "publisher_name",
    "publisher_homepage_url",
    "publisher_logo_url",
    "publisher_favicon_url",
    "image_url",
    "amp_url",
    "description",
    "published_utc",
    "published_utc_raw",
    "published_date",
    "published_year",
    "as_of_utc",
    "as_of_date",
    "as_of_semantics",
    "payload_tickers",
    "payload_tickers_text",
    "payload_ticker_count",
    "requested_ticker_in_payload_tickers",
    "is_mono_ticker_article",
    "is_multi_ticker_article",
    "ticker_attribution_state",
    "keywords",
    "keywords_text",
    "insights",
    "insights_text",
    "instrument_master_ticker_present",
    "instrument_identity_temporal_match",
    "instrument_identity_state",
    "is_common_stock",
    "is_lt1b_operational",
    "lt1b_classification_1b",
    "news_quality_state",
    "valid_for_event_context_candidate",
    "valid_for_catalyst_timing_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_state_component_candidate",
    "valid_for_rl_training_direct",
    "requires_event_time_filter",
    "prohibited_without_asof_filter",
    "contains_future_information_without_event_filter",
    "causal_proof_by_itself",
    "same_day_causal_claim_allowed_without_intraday_ordering",
    "timezone_alignment_required_for_intraday_claims",
    "source_root",
    "source_file",
    "source_file_relative_path",
    "source_file_row_number",
    "source_empty_sentinel",
    "_dataset",
    "_ingested_utc",
    "instrument_master_build_run_id",
    "instrument_master_schema_version",
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


def _sql(sql: str):
    con = duckdb.connect()
    con.execute("pragma threads=8")
    return con.execute(sql).fetchone()[0]


def _dict(sql: str) -> dict[str, int]:
    con = duckdb.connect()
    con.execute("pragma threads=8")
    return {str(key): int(value) for key, value in con.execute(sql).fetchall()}


def test_news_context_manifest_hashes_contracts_and_sources(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "news_context_table_v0_1"
    assert manifest["schema_version"] == "news_context_table_v0_1"
    assert manifest["quality_policy_version"] == "news_context_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["source_dataset_id"] == "additional_v0_1"
    assert manifest["source_subblock"] == "news"
    assert manifest["source_root"] == EXPECTED_SOURCE_ROOT
    assert manifest["full_universe_claim"] is False
    assert manifest["direct_rl_training_allowed"] is False
    assert manifest["requires_event_time_filter"] is True
    assert manifest["prohibited_without_asof_filter"] is True
    assert manifest["causal_proof_by_itself"] is False
    assert Path(manifest["dataset_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert_relative_contract_paths_exist(manifest)

    source_inventory = manifest["source_inventory"]
    assert source_inventory["file_count"] == 4_824
    assert source_inventory["business_file_count"] == 3_869
    assert source_inventory["empty_sentinel_file_count"] == 955
    assert source_inventory["metadata_row_count"] == 288_093
    assert source_inventory["business_row_count"] == 287_138

    write_json_artifact(
        tsis_artifacts_dir,
        "news_context_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "build_run_id": manifest["build_run_id"],
            "output_tree": manifest["output_tree"],
            "source_inventory": source_inventory,
        },
    )


def test_news_context_schema_counts_quality_and_gates(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    glob = _glob()

    columns = set(
        duckdb.sql(
            f"describe select * from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)"
        ).fetchdf()["column_name"]
    )
    assert REQUIRED_COLUMNS <= columns

    assert _sql(f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)") == 287_138
    assert validations["row_count"] == 287_138
    assert validations["unique_news_context_id_count"] == 287_138
    assert validations["duplicate_news_context_id_count"] == 0
    assert validations["duplicate_source_key_count"] == 0
    assert validations["ticker_count"] == 3_869
    assert validations["instrument_count"] == 3_699
    assert validations["publisher_count"] == 11
    assert validations["first_published_utc"] == "2016-06-23 14:31:00"
    assert validations["last_published_utc"] == "2026-04-05 16:42:00"

    assert validations["news_quality_state_counts"] == {
        "good_mono_ticker_news_context": 102_556,
        "good_review_multi_ticker_news_context": 180_051,
        "review_no_temporal_identity": 4_531,
    }
    assert validations["ticker_attribution_state_counts"] == {
        "good_mono_ticker_attributed": 104_455,
        "review_multi_ticker_attributed": 182_683,
    }
    assert validations["instrument_identity_state_counts"] == {
        "good_temporal_match": 282_607,
        "review_no_temporal_identity": 4_531,
    }
    assert validations["hard_fail_count"] == 0
    assert validations["valid_for_event_context_candidate_rows"] == 282_607
    assert validations["valid_for_catalyst_timing_candidate_rows"] == 282_607
    assert validations["valid_for_ml_feature_candidate_rows"] == 282_607
    assert validations["valid_for_state_component_candidate_rows"] == 282_607
    assert validations["valid_for_rl_training_direct_rows"] == 0
    assert validations["full_universe_claim_rows"] == 0

    write_json_artifact(
        tsis_artifacts_dir,
        "news_context_quality_check.json",
        {
            "rows": validations["row_count"],
            "quality_counts": validations["news_quality_state_counts"],
            "attribution_counts": validations["ticker_attribution_state_counts"],
        },
    )


def test_news_context_temporal_semantics_and_leakage_guards() -> None:
    glob = _glob()

    assert _sql(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where published_utc is null
           or as_of_utc <> published_utc
           or as_of_date <> published_date
           or as_of_semantics <> 'published_utc_vendor_timestamp'
        """
    ) == 0
    assert _sql(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where source_empty_sentinel
           or valid_for_rl_training_direct
           or not requires_event_time_filter
           or not prohibited_without_asof_filter
           or not contains_future_information_without_event_filter
           or causal_proof_by_itself
           or same_day_causal_claim_allowed_without_intraday_ordering
           or not timezone_alignment_required_for_intraday_claims
           or full_universe_claim
        """
    ) == 0
    assert _sql(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where valid_for_event_context_candidate
          and (
              not requested_ticker_in_payload_tickers
              or not instrument_identity_temporal_match
              or published_utc is null
              or article_id is null
              or article_url is null
              or title is null
          )
        """
    ) == 0


def test_news_context_attribution_and_year_partitions(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    glob = _glob()

    year_counts = _dict(
        f"""
        select published_year, count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        group by published_year
        order by published_year
        """
    )
    assert year_counts == manifest["validations"]["published_year_counts"] == {
        "2016": 3,
        "2019": 6,
        "2020": 372,
        "2021": 56_379,
        "2022": 87_243,
        "2023": 84_499,
        "2024": 40_736,
        "2025": 13_921,
        "2026": 3_979,
    }
    assert _sql(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where is_mono_ticker_article
          and ticker_attribution_state <> 'good_mono_ticker_attributed'
        """
    ) == 0
    assert _sql(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where is_multi_ticker_article
          and ticker_attribution_state <> 'review_multi_ticker_attributed'
        """
    ) == 0
    assert _sql(
        f"""
        select count(*)
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        where not requested_ticker_in_payload_tickers
        """
    ) == 0

    write_json_artifact(
        tsis_artifacts_dir,
        "news_context_attribution_years.json",
        {
            "year_counts": year_counts,
            "mono_ticker_article_rows": manifest["validations"]["mono_ticker_article_rows"],
            "multi_ticker_article_rows": manifest["validations"]["multi_ticker_article_rows"],
        },
    )
