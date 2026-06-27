from __future__ import annotations

from pathlib import Path

import duckdb

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    sha256_file,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table")
DATASET_DIR = OUTPUT_ROOT / "master_intraday_bar_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_master_intraday_bar_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_master_intraday_bar_table_summary_v0_1.csv"

EXPECTED_PRICE_VIEWS = {"1m_raw", "1m_split_normalized"}
EXPECTED_SCOPE = "scoped_split_normalized_event_cases"
REQUIRED_COLUMNS = {
    "master_intraday_bar_id",
    "ticker",
    "instrument_id",
    "ts_utc",
    "session_date",
    "year",
    "month",
    "bar_size",
    "price_view",
    "quality_gate_family",
    "source_dataset",
    "source_root",
    "source_file",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
    "transaction_count",
    "source_t_epoch_ms",
    "source_raw_open",
    "source_raw_high",
    "source_raw_low",
    "source_raw_close",
    "source_raw_vwap",
    "source_raw_volume",
    "source_raw_transaction_count",
    "future_split_factor",
    "o_split_normalized",
    "h_split_normalized",
    "l_split_normalized",
    "c_split_normalized",
    "vw_split_normalized",
    "materialized_source_price_view",
    "source_1m_file_reported",
    "source_splits_file",
    "source_split_normalized_file",
    "pilot_role",
    "pilot_event_type",
    "pilot_event_date",
    "session_segment",
    "raw_quality_manifest_present",
    "raw_quality_manifest_rows",
    "raw_core_quality_state",
    "raw_core_issue_family",
    "raw_combined_quality_state",
    "raw_allowed_consumption",
    "raw_vw_quality_state",
    "raw_vw_issue_family",
    "raw_final_policy_bucket_lt1b",
    "raw_manifest_negative_or_zero_ohlc_rows",
    "raw_manifest_negative_volume_rows",
    "raw_manifest_high_low_inversion_rows",
    "raw_manifest_duplicate_ts_utc_rows",
    "raw_manifest_vw_outside_range_rows",
    "corporate_action_count",
    "split_action_count",
    "dividend_action_count",
    "ticker_change_action_count",
    "has_split_action",
    "has_dividend_action",
    "has_ticker_change_action",
    "has_any_corporate_action",
    "row_level_price_integrity_state",
    "selected_price_hard_invalid",
    "negative_volume",
    "core_ohlcv_consumption_allowed",
    "vwap_consumption_allowed",
    "vwap_consumption_state",
    "event_research_bar_candidate",
    "backtest_core_bar_candidate",
    "full_universe_claim",
    "materialization_scope",
    "family_data_quality_verdict",
    "family_foundations_completion_status",
    "family_visual_inspection_status",
    "family_production_use_gate",
    "family_event_consumption_gate",
    "gate_quality_policy_version",
    "dataset_certification_matrix_build_run_id",
    "instrument_master_build_run_id",
    "instrument_master_schema_version",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _dataset_glob() -> str:
    return str(DATASET_DIR / "**" / "*.parquet").replace("\\", "/")


def test_master_intraday_manifest_tree_hashes_and_contract_links(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "master_intraday_bar_table_v0_1"
    assert manifest["schema_version"] == "master_intraday_bar_table_v0_1"
    assert manifest["quality_policy_version"] == "master_intraday_bar_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["full_universe_claim"] is False
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert sha256_parquet_tree(Path(manifest["source_split_normalized_root"])) == manifest[
        "source_split_normalized_tree"
    ]
    assert sha256_file(Path(manifest["source_instrument_master"])) == manifest[
        "source_instrument_master_sha256"
    ]
    assert sha256_file(Path(manifest["source_corporate_actions"])) == manifest[
        "source_corporate_actions_sha256"
    ]
    assert sha256_file(Path(manifest["source_dataset_certification_matrix"])) == manifest[
        "source_dataset_certification_matrix_sha256"
    ]
    assert sha256_file(Path(manifest["source_raw_1m_quality_manifest"])) == manifest[
        "source_raw_1m_quality_manifest_sha256"
    ]
    assert assert_relative_contract_paths_exist(manifest) is None

    write_json_artifact(
        tsis_artifacts_dir,
        "master_intraday_bar_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "materialization_scope": manifest["materialization_scope"],
            "output_tree": manifest["output_tree"],
            "validations": manifest["validations"],
        },
    )


def test_master_intraday_schema_scope_price_views_and_flags(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    dataset_glob = _dataset_glob()

    columns = set(
        duckdb.sql(f"describe select * from read_parquet('{dataset_glob}', hive_partitioning=true)").fetchdf()[
            "column_name"
        ]
    )
    assert REQUIRED_COLUMNS <= columns

    row = duckdb.sql(
        f"""
        with rows as (
            select * from read_parquet('{dataset_glob}', hive_partitioning=true)
        ),
        dupes as (
            select count(*)::bigint as duplicate_key_groups
            from (
                select ticker, ts_utc, bar_size, price_view, count(*) as n
                from rows
                group by 1, 2, 3, 4
                having count(*) > 1
            )
        )
        select
            count(*)::bigint as rows,
            count(distinct ticker)::integer as tickers,
            count(distinct price_view)::integer as price_views,
            count(distinct ticker || '|' || year::varchar || '|' || month::varchar)::integer as ticker_months,
            strftime(min(ts_utc) at time zone 'UTC', '%Y-%m-%d %H:%M:%S') as first_ts_utc,
            strftime(max(ts_utc) at time zone 'UTC', '%Y-%m-%d %H:%M:%S') as last_ts_utc,
            sum(case when selected_price_hard_invalid then 1 else 0 end)::bigint as hard_invalid_rows,
            sum(case when negative_volume then 1 else 0 end)::bigint as negative_volume_rows,
            sum(case when event_research_bar_candidate then 1 else 0 end)::bigint as event_candidate_rows,
            sum(case when backtest_core_bar_candidate then 1 else 0 end)::bigint as backtest_core_rows,
            sum(case when not raw_quality_manifest_present then 1 else 0 end)::bigint as raw_quality_missing_rows,
            sum(case when full_universe_claim then 1 else 0 end)::bigint as full_universe_claim_rows,
            count(distinct materialization_scope)::integer as materialization_scope_count,
            min(materialization_scope) as materialization_scope,
            count(distinct schema_version)::integer as schema_versions,
            count(distinct build_run_id)::integer as build_run_ids,
            (select duplicate_key_groups from dupes)::bigint as duplicate_key_groups
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    assert row["rows"] == validations["row_count"] == 175_252
    assert row["tickers"] == validations["ticker_count"] == 8
    assert row["ticker_months"] == validations["ticker_month_count"] == 10
    assert row["price_views"] == validations["price_view_count"] == 2
    assert row["first_ts_utc"] == "2006-03-01 13:02:00"
    assert row["last_ts_utc"] == "2025-02-28 22:10:00"
    assert row["hard_invalid_rows"] == validations["selected_price_hard_invalid_rows"] == 0
    assert row["negative_volume_rows"] == validations["negative_volume_rows"] == 0
    assert row["event_candidate_rows"] == validations["event_research_bar_candidate_rows"] == 161_176
    assert row["backtest_core_rows"] == validations["backtest_core_bar_candidate_rows"] == 0
    assert row["raw_quality_missing_rows"] == validations["raw_quality_manifest_missing_rows"] == 14_076
    assert row["full_universe_claim_rows"] == 0
    assert row["materialization_scope_count"] == 1
    assert row["materialization_scope"] == EXPECTED_SCOPE
    assert row["duplicate_key_groups"] == validations["duplicate_key_groups"] == 0
    assert row["schema_versions"] == 1
    assert row["build_run_ids"] == 1
    assert validations["hard_fail_count"] == 0

    write_json_artifact(
        tsis_artifacts_dir,
        "master_intraday_bar_table_scope_check.json",
        row,
    )


def test_master_intraday_reconciles_split_source_and_rows_by_price_view(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    dataset_glob = _dataset_glob()
    source_glob = str(Path(manifest["source_split_normalized_root"]) / "**" / "*.parquet").replace("\\", "/")

    source_rows = duckdb.sql(
        f"select count(*)::bigint from read_parquet('{source_glob}', hive_partitioning=false)"
    ).fetchone()[0]
    assert source_rows == validations["source_split_normalized_bar_rows"] == 87_626
    assert validations["row_count"] == source_rows * len(EXPECTED_PRICE_VIEWS)

    by_view = duckdb.sql(
        f"""
        select
            price_view,
            count(*)::bigint as rows,
            sum(case when selected_price_hard_invalid then 1 else 0 end)::bigint as hard_invalid_rows,
            sum(case when negative_volume then 1 else 0 end)::bigint as negative_volume_rows,
            sum(case when event_research_bar_candidate then 1 else 0 end)::bigint as event_candidate_rows,
            sum(case when backtest_core_bar_candidate then 1 else 0 end)::bigint as backtest_core_rows,
            sum(case when not raw_quality_manifest_present then 1 else 0 end)::bigint as raw_quality_missing_rows,
            sum(case when vwap_consumption_state = 'blocked_by_raw_vw_quality' then 1 else 0 end)::bigint as vwap_blocked_rows,
            sum(case when has_any_corporate_action then 1 else 0 end)::bigint as rows_with_corporate_action
        from read_parquet('{dataset_glob}', hive_partitioning=true)
        group by price_view
        """
    ).fetchdf()
    actual = {
        row["price_view"]: {
            "rows": int(row["rows"]),
            "hard_invalid_rows": int(row["hard_invalid_rows"]),
            "negative_volume_rows": int(row["negative_volume_rows"]),
            "event_research_bar_candidate_rows": int(row["event_candidate_rows"]),
            "backtest_core_bar_candidate_rows": int(row["backtest_core_rows"]),
            "raw_quality_manifest_missing_rows": int(row["raw_quality_missing_rows"]),
            "vwap_blocked_rows": int(row["vwap_blocked_rows"]),
            "rows_with_corporate_action": int(row["rows_with_corporate_action"]),
        }
        for _, row in by_view.iterrows()
    }
    assert set(actual) == EXPECTED_PRICE_VIEWS
    assert actual == validations["rows_by_price_view"]
    for payload in actual.values():
        assert payload["rows"] == source_rows
        assert payload["backtest_core_bar_candidate_rows"] == 0
        assert payload["hard_invalid_rows"] == 0
        assert payload["negative_volume_rows"] == 0

    write_json_artifact(
        tsis_artifacts_dir,
        "master_intraday_bar_table_source_reconciliation.json",
        {"source_rows": source_rows, "rows_by_price_view": actual},
    )


def test_master_intraday_price_view_formula_integrity() -> None:
    dataset_glob = _dataset_glob()
    row = duckdb.sql(
        f"""
        with rows as (
            select * from read_parquet('{dataset_glob}', hive_partitioning=true)
        )
        select
            max(case when price_view = '1m_raw' then abs(open - source_raw_open) else 0 end) as raw_open_diff,
            max(case when price_view = '1m_raw' then abs(high - source_raw_high) else 0 end) as raw_high_diff,
            max(case when price_view = '1m_raw' then abs(low - source_raw_low) else 0 end) as raw_low_diff,
            max(case when price_view = '1m_raw' then abs(close - source_raw_close) else 0 end) as raw_close_diff,
            max(case
                when price_view = '1m_split_normalized'
                then abs(open - (source_raw_open * future_split_factor))
                else 0
            end) as split_open_diff,
            max(case
                when price_view = '1m_split_normalized'
                then abs(high - (source_raw_high * future_split_factor))
                else 0
            end) as split_high_diff,
            max(case
                when price_view = '1m_split_normalized'
                then abs(low - (source_raw_low * future_split_factor))
                else 0
            end) as split_low_diff,
            max(case
                when price_view = '1m_split_normalized'
                then abs(close - (source_raw_close * future_split_factor))
                else 0
            end) as split_close_diff,
            max(case
                when price_view = '1m_split_normalized' and vwap is not null and source_raw_vwap is not null
                then abs(vwap - (source_raw_vwap * future_split_factor))
                else 0
            end) as split_vwap_diff
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    for value in row.values():
        assert float(value) <= 1e-6


def test_master_intraday_quality_gate_invariants() -> None:
    dataset_glob = _dataset_glob()
    row = duckdb.sql(
        f"""
        with rows as (
            select * from read_parquet('{dataset_glob}', hive_partitioning=true)
        )
        select
            sum(case
                when event_research_bar_candidate and not raw_quality_manifest_present then 1 else 0
            end)::bigint as event_candidate_without_raw_quality,
            sum(case
                when event_research_bar_candidate and selected_price_hard_invalid then 1 else 0
            end)::bigint as event_candidate_with_bad_price,
            sum(case
                when event_research_bar_candidate and negative_volume then 1 else 0
            end)::bigint as event_candidate_with_negative_volume,
            sum(case
                when backtest_core_bar_candidate then 1 else 0
            end)::bigint as backtest_core_rows,
            sum(case
                when vwap_consumption_allowed
                 and vwap_consumption_state <> 'allowed_with_declared_vw_policy'
                then 1 else 0
            end)::bigint as inconsistent_vwap_allowed_rows,
            sum(case
                when raw_vw_quality_state = 'bad'
                 and vwap is not null
                 and vwap_consumption_state <> 'blocked_by_raw_vw_quality'
                then 1 else 0
            end)::bigint as bad_vw_not_blocked_rows
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    assert row["event_candidate_without_raw_quality"] == 0
    assert row["event_candidate_with_bad_price"] == 0
    assert row["event_candidate_with_negative_volume"] == 0
    assert row["backtest_core_rows"] == 0
    assert row["inconsistent_vwap_allowed_rows"] == 0
    assert row["bad_vw_not_blocked_rows"] == 0
