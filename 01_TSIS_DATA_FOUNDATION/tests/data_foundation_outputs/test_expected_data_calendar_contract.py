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


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/expected_data_calendar")
DATASET_DIR = OUTPUT_ROOT / "expected_data_calendar_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_expected_data_calendar_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_expected_data_calendar_summary_v0_1.csv"

EXPECTED_FAMILIES = {"daily_raw", "ohlcv_1m_raw", "trades_raw", "quotes_raw"}
REQUIRED_COLUMNS = {
    "dataset_family",
    "expected_dataset_id",
    "expected_source_root",
    "instrument_id",
    "ticker",
    "session_date",
    "expected_session",
    "expected_reason",
    "expectation_scope",
    "calendar",
    "timezone",
    "year",
    "month",
    "valid_from",
    "valid_to",
    "instrument_master_schema_version",
    "instrument_master_build_run_id",
    "market_calendar_schema_version",
    "market_calendar_build_run_id",
    "expectation_policy_version",
    "build_run_id",
    "schema_version",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _dataset_glob() -> str:
    return str(DATASET_DIR / "**" / "*.parquet").replace("\\", "/")


def _scalar(query: str):
    return duckdb.sql(query).fetchone()[0]


def test_expected_data_calendar_manifest_tree_hashes_and_contract_links(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    assert manifest["dataset_id"] == "expected_data_calendar_v0_1"
    assert manifest["schema_version"] == "expected_data_calendar_v0_1"
    assert manifest["expectation_policy_version"] == "expected_data_calendar_policy_v0_1"
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert sha256_file(Path(manifest["source_instrument_master"])) == manifest["source_instrument_master_sha256"]
    assert sha256_file(Path(manifest["source_market_calendar"])) == manifest["source_market_calendar_sha256"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "expected_data_calendar_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": manifest["output_path"],
            "output_tree": manifest["output_tree"],
            "validations": manifest["validations"],
        },
    )


def test_expected_data_calendar_schema_lineage_and_counts() -> None:
    manifest = _manifest()
    dataset_glob = _dataset_glob()

    columns = set(
        duckdb.sql(f"describe select * from read_parquet('{dataset_glob}', hive_partitioning=true)").fetchdf()[
            "column_name"
        ]
    )
    assert REQUIRED_COLUMNS <= columns

    validations = manifest["validations"]
    row = duckdb.sql(
        f"""
        select
            count(*)::bigint as rows,
            count(distinct dataset_family)::integer as families,
            count(distinct ticker)::integer as tickers,
            min(session_date)::varchar as first_session,
            max(session_date)::varchar as last_session,
            count(distinct schema_version)::integer as schema_versions,
            count(distinct build_run_id)::integer as build_run_ids,
            count(distinct expectation_policy_version)::integer as policy_versions
        from read_parquet('{dataset_glob}', hive_partitioning=true)
        """
    ).fetchdf().iloc[0].to_dict()

    assert row["rows"] == validations["row_count"] == 29_478_796
    assert row["families"] == validations["dataset_family_count"] == 4
    assert row["tickers"] == validations["ticker_count"] == 4824
    assert row["first_session"] == validations["first_session"] == "2005-01-03"
    assert row["last_session"] == validations["last_session"] == "2026-03-09"
    assert row["schema_versions"] == 1
    assert row["build_run_ids"] == 1
    assert row["policy_versions"] == 1


def test_expected_data_calendar_key_window_and_family_rules() -> None:
    manifest = _manifest()
    dataset_glob = _dataset_glob()
    validations = manifest["validations"]

    row = duckdb.sql(
        f"""
        with rows as (
            select * from read_parquet('{dataset_glob}', hive_partitioning=true)
        ),
        dupes as (
            select count(*)::bigint as duplicate_key_groups
            from (
                select dataset_family, ticker, session_date, count(*) as n
                from rows
                group by 1, 2, 3
                having count(*) > 1
            )
        )
        select
            sum(case when expected_session then 0 else 1 end)::bigint as unexpected_false_count,
            sum(case when session_date < valid_from or session_date > valid_to then 1 else 0 end)::bigint
                as invalid_window_count,
            sum(case when calendar != 'XNYS' then 1 else 0 end)::bigint as unexpected_calendar_count,
            sum(case when timezone != 'America/New_York' then 1 else 0 end)::bigint as unexpected_timezone_count,
            (select duplicate_key_groups from dupes)::bigint as duplicate_key_groups
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    assert row["unexpected_false_count"] == validations["unexpected_false_count"] == 0
    assert row["invalid_window_count"] == validations["invalid_window_count"] == 0
    assert row["duplicate_key_groups"] == validations["duplicate_key_groups"] == 0
    assert row["unexpected_calendar_count"] == 0
    assert row["unexpected_timezone_count"] == 0
    assert validations["hard_fail_count"] == 0

    families = set(
        duckdb.sql(
            f"select distinct dataset_family from read_parquet('{dataset_glob}', hive_partitioning=true)"
        ).fetchdf()["dataset_family"]
    )
    assert families == EXPECTED_FAMILIES


def test_expected_data_calendar_reconciles_to_instrument_calendar_intersection(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    expected_one_family = _scalar(
        f"""
        select count(*)::bigint
        from read_parquet('{str(Path(manifest["source_instrument_master"])).replace("\\", "/")}') i
        join read_parquet('{str(Path(manifest["source_market_calendar"])).replace("\\", "/")}') c
          on cast(c.session_date as date) between cast(i.valid_from as date) and cast(i.valid_to as date)
        where i.is_lt1b_operational = true
          and c.calendar = 'XNYS'
        """
    )
    validations = manifest["validations"]
    assert expected_one_family == 7_369_699
    assert validations["row_count"] == expected_one_family * len(EXPECTED_FAMILIES)
    for family in EXPECTED_FAMILIES:
        assert validations["rows_by_family"][family]["rows"] == expected_one_family
        assert validations["rows_by_family"][family]["tickers"] == 4824

    write_json_artifact(
        tsis_artifacts_dir,
        "expected_data_calendar_source_reconciliation.json",
        {
            "single_family_expected_rows": expected_one_family,
            "family_count": len(EXPECTED_FAMILIES),
            "total_expected_rows": validations["row_count"],
            "source_instrument_master": manifest["source_instrument_master"],
            "source_market_calendar": manifest["source_market_calendar"],
        },
    )
