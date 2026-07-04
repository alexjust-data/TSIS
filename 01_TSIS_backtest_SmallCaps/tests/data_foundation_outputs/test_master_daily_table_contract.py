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


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/master_daily_table")
DATASET_DIR = OUTPUT_ROOT / "master_daily_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_master_daily_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_master_daily_table_summary_v0_1.csv"

EXPECTED_PRICE_VIEWS = {"daily_raw", "split_normalized", "adjusted"}
REQUIRED_COLUMNS = {
    "master_daily_id",
    "instrument_id",
    "ticker",
    "session_date",
    "year",
    "month",
    "price_view",
    "quality_gate_family",
    "source_dataset",
    "source_root",
    "expected_session",
    "expected_reason",
    "expected_dataset_id",
    "expected_source_root",
    "data_present",
    "missing_expected_data",
    "source_daily_present",
    "source_adjusted_present",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
    "source_raw_vwap",
    "transaction_count",
    "source_t_epoch_ms",
    "prior_close",
    "gap_pct",
    "daily_return_pct",
    "intraday_return_pct",
    "daily_range_pct",
    "dollar_volume",
    "volume_20d_avg",
    "rvol_20d",
    "future_split_factor",
    "future_dividend_sum",
    "future_dividend_factor",
    "future_adjustment_factor",
    "adjusted_materialized_price_view",
    "adjusted_proxy_open",
    "adjusted_proxy_high",
    "adjusted_proxy_low",
    "adjusted_proxy_close",
    "source_daily_file",
    "source_splits_file",
    "source_dividends_file",
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
    "backtest_core_row_candidate",
    "family_data_quality_verdict",
    "family_foundations_completion_status",
    "family_visual_inspection_status",
    "family_production_use_gate",
    "family_event_consumption_gate",
    "gate_quality_policy_version",
    "expected_data_calendar_build_run_id",
    "dataset_certification_matrix_build_run_id",
    "corporate_actions_build_run_id",
    "expectation_policy_version",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _dataset_glob() -> str:
    return str(DATASET_DIR / "**" / "*.parquet").replace("\\", "/")


def _file_inventory(root: Path) -> dict:
    count = 0
    total_bytes = 0
    for path in root.rglob("*.parquet"):
        count += 1
        total_bytes += path.stat().st_size
    return {"parquet_file_count": count, "total_bytes": total_bytes}


def test_master_daily_manifest_tree_hashes_and_contract_links(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "master_daily_table_v0_1"
    assert manifest["schema_version"] == "master_daily_table_v0_1"
    assert manifest["quality_policy_version"] == "master_daily_table_policy_v0_1"
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert sha256_file(Path(manifest["source_corporate_actions"])) == manifest["source_corporate_actions_sha256"]
    assert sha256_file(Path(manifest["source_dataset_certification_matrix"])) == manifest[
        "source_dataset_certification_matrix_sha256"
    ]
    assert assert_relative_contract_paths_exist(manifest) is None

    write_json_artifact(
        tsis_artifacts_dir,
        "master_daily_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": manifest["output_path"],
            "output_tree": manifest["output_tree"],
            "validations": manifest["validations"],
        },
    )


def test_master_daily_schema_counts_price_views_and_flags() -> None:
    manifest = _manifest()
    dataset_glob = _dataset_glob()
    validations = manifest["validations"]

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
                select ticker, session_date, price_view, count(*) as n
                from rows
                group by 1, 2, 3
                having count(*) > 1
            )
        )
        select
            count(*)::bigint as rows,
            count(distinct ticker)::integer as tickers,
            count(distinct instrument_id)::integer as instrument_ids,
            count(distinct price_view)::integer as price_views,
            min(session_date)::varchar as first_session,
            max(session_date)::varchar as last_session,
            sum(case when data_present then 1 else 0 end)::bigint as present_rows,
            sum(case when missing_expected_data then 1 else 0 end)::bigint as missing_rows,
            sum(case when selected_price_hard_invalid then 1 else 0 end)::bigint as hard_invalid_rows,
            sum(case when negative_volume then 1 else 0 end)::bigint as negative_volume_rows,
            sum(case when backtest_core_row_candidate then 1 else 0 end)::bigint as candidate_rows,
            sum(case when has_any_corporate_action then 1 else 0 end)::bigint as corporate_action_rows,
            count(distinct schema_version)::integer as schema_versions,
            count(distinct build_run_id)::integer as build_run_ids,
            (select duplicate_key_groups from dupes)::bigint as duplicate_key_groups
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    assert row["rows"] == validations["row_count"] == 22_109_097
    assert row["tickers"] == validations["ticker_count"] == 4824
    assert row["instrument_ids"] == validations["instrument_id_count"] == 4626
    assert row["price_views"] == validations["price_view_count"] == 3
    assert row["first_session"] == validations["first_session"] == "2005-01-03"
    assert row["last_session"] == validations["last_session"] == "2026-03-09"
    assert row["present_rows"] == validations["data_present_rows"] == 20_106_954
    assert row["missing_rows"] == validations["missing_expected_data_rows"] == 2_002_143
    assert row["hard_invalid_rows"] == validations["selected_price_hard_invalid_rows"] == 0
    assert row["negative_volume_rows"] == validations["negative_volume_rows"] == 0
    assert row["candidate_rows"] == validations["backtest_core_row_candidate_rows"] == 20_106_954
    assert row["corporate_action_rows"] == validations["rows_with_corporate_action"] == 94_275
    assert row["duplicate_key_groups"] == validations["duplicate_key_groups"] == 0
    assert row["schema_versions"] == 1
    assert row["build_run_ids"] == 1
    assert validations["hard_fail_count"] == 0


def test_master_daily_reconciles_expected_denominator_and_rows_by_price_view(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    dataset_glob = _dataset_glob()
    validations = manifest["validations"]
    expected_glob = (
        Path(manifest["source_expected_data_calendar"]) / "**" / "*.parquet"
    ).as_posix()

    expected_daily_rows = duckdb.sql(
        f"""
        select count(*)::bigint
        from read_parquet('{expected_glob}', hive_partitioning=true)
        where dataset_family = 'daily_raw'
        """
    ).fetchone()[0]
    assert expected_daily_rows == validations["expected_daily_rows"] == 7_369_699
    assert validations["row_count"] == expected_daily_rows * len(EXPECTED_PRICE_VIEWS)

    by_view = duckdb.sql(
        f"""
        select
            price_view,
            count(*)::bigint as rows,
            sum(case when data_present then 1 else 0 end)::bigint as present_rows,
            sum(case when missing_expected_data then 1 else 0 end)::bigint as missing_rows,
            sum(case when selected_price_hard_invalid then 1 else 0 end)::bigint as hard_invalid_rows,
            sum(case when backtest_core_row_candidate then 1 else 0 end)::bigint as candidate_rows
        from read_parquet('{dataset_glob}', hive_partitioning=true)
        group by price_view
        """
    ).fetchdf()
    actual = {
        row["price_view"]: {
            "rows": int(row["rows"]),
            "present_rows": int(row["present_rows"]),
            "missing_rows": int(row["missing_rows"]),
            "hard_invalid_rows": int(row["hard_invalid_rows"]),
            "backtest_core_candidate_rows": int(row["candidate_rows"]),
        }
        for _, row in by_view.iterrows()
    }
    assert set(actual) == EXPECTED_PRICE_VIEWS
    assert actual == validations["rows_by_price_view"]
    for payload in actual.values():
        assert payload["rows"] == expected_daily_rows
        assert payload["present_rows"] == 6_702_318
        assert payload["missing_rows"] == 667_381
        assert payload["hard_invalid_rows"] == 0

    write_json_artifact(
        tsis_artifacts_dir,
        "master_daily_table_source_reconciliation.json",
        {
            "expected_daily_rows": expected_daily_rows,
            "rows_by_price_view": actual,
            "source_expected_data_calendar": manifest["source_expected_data_calendar"],
        },
    )


def test_master_daily_price_view_semantics_metrics_and_source_inventory() -> None:
    manifest = _manifest()
    dataset_glob = _dataset_glob()

    raw_inventory = _file_inventory(Path(manifest["source_raw_daily_root"]))
    adjusted_inventory = _file_inventory(Path(manifest["source_daily_adjusted_root"]))
    assert raw_inventory["parquet_file_count"] == manifest["source_raw_daily_inventory"]["parquet_file_count"]
    assert raw_inventory["total_bytes"] == manifest["source_raw_daily_inventory"]["total_bytes"]
    assert adjusted_inventory["parquet_file_count"] == manifest["source_daily_adjusted_inventory"]["parquet_file_count"]
    assert adjusted_inventory["total_bytes"] == manifest["source_daily_adjusted_inventory"]["total_bytes"]

    row = duckdb.sql(
        f"""
        select
            sum(case when price_view = 'daily_raw' and vwap is null and data_present then 1 else 0 end)::bigint
                as raw_present_missing_vwap,
            sum(case when price_view in ('split_normalized','adjusted') and vwap is not null then 1 else 0 end)::bigint
                as derived_view_vwap_populated,
            sum(case when data_present and row_level_price_integrity_state != 'row_candidate' then 1 else 0 end)::bigint
                as present_non_candidate_integrity_rows,
            sum(case when not data_present and row_level_price_integrity_state != 'missing_expected_data' then 1 else 0 end)::bigint
                as missing_wrong_state_rows,
            sum(case when dollar_volume is not null and abs(dollar_volume - close * volume) > 0.0001 then 1 else 0 end)::bigint
                as bad_dollar_volume_rows,
            sum(case when prior_close is null and (gap_pct is not null or daily_return_pct is not null) then 1 else 0 end)::bigint
                as bad_prior_metric_rows
        from read_parquet('{dataset_glob}', hive_partitioning=true)
        """
    ).fetchdf().iloc[0].to_dict()

    assert row["derived_view_vwap_populated"] == 0
    assert row["present_non_candidate_integrity_rows"] == 0
    assert row["missing_wrong_state_rows"] == 0
    assert row["bad_dollar_volume_rows"] == 0
    assert row["bad_prior_metric_rows"] == 0
