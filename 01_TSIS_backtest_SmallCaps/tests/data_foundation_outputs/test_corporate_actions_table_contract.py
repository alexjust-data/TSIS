from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    non_empty_string_mask,
    sha256_file,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/corporate_actions_table")
MANIFEST_PATH = OUTPUT_ROOT / "_corporate_actions_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_corporate_actions_table_summary_v0_1.csv"

REQUIRED_COLUMNS = {
    "corporate_action_id",
    "instrument_id",
    "ticker",
    "action_type",
    "action_date",
    "action_year",
    "source_system",
    "source_dataset",
    "source_root",
    "source_priority",
    "source_event_id",
    "is_reference_primary_source",
    "is_additional_secondary_source",
    "split_from",
    "split_to",
    "split_ratio",
    "cash_amount",
    "currency",
    "declaration_date",
    "ex_dividend_date",
    "pay_date",
    "record_date",
    "dividend_type",
    "dividend_frequency",
    "ticker_change_date",
    "ticker_change_ticker",
    "event_name",
    "source_ingested_utc",
    "valid_from",
    "valid_to",
    "within_instrument_valid_window",
    "instrument_master_schema_version",
    "instrument_master_build_run_id",
    "build_run_id",
    "schema_version",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _frame() -> pd.DataFrame:
    return pd.read_parquet(_manifest()["output_path"])


def test_corporate_actions_manifest_hashes_contracts_and_source_fingerprints(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    output_path = Path(manifest["output_path"])
    summary_path = Path(manifest["summary_path"])

    assert manifest["dataset_id"] == "corporate_actions_table_v0_1"
    assert manifest["schema_version"] == "corporate_actions_table_v0_1"
    assert output_path.exists()
    assert summary_path.exists()
    assert summary_path == SUMMARY_PATH
    assert sha256_file(output_path) == manifest["output_sha256"]
    assert sha256_file(Path(manifest["source_instrument_master"])) == manifest["source_instrument_master_sha256"]
    assert_relative_contract_paths_exist(manifest)

    expected_fingerprint_keys = {
        "reference_splits",
        "reference_dividends",
        "reference_events",
        "additional_splits",
        "additional_dividends",
        "additional_ticker_events",
    }
    assert set(manifest["source_fingerprints"]) == expected_fingerprint_keys
    assert manifest["source_fingerprints"]["reference_dividends"]["parquet_file_count"] == 12468
    assert manifest["source_fingerprints"]["additional_dividends"]["parquet_file_count"] == 4824

    write_json_artifact(
        tsis_artifacts_dir,
        "corporate_actions_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": str(output_path),
            "output_sha256": manifest["output_sha256"],
            "validations": manifest["validations"],
            "source_fingerprint_file_counts": {
                k: v["parquet_file_count"] for k, v in manifest["source_fingerprints"].items()
            },
        },
    )


def test_corporate_actions_schema_lineage_and_manifest_counts() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 104_757
    assert df["ticker"].nunique() == validations["ticker_count"] == 3621
    assert df["instrument_id"].nunique() == validations["instrument_id_count"] == 3497
    assert set(df["schema_version"]) == {"corporate_actions_table_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert set(df["instrument_master_schema_version"]) == {"instrument_master_v0_1"}
    assert non_empty_string_mask(df["created_at_utc"]).all()
    assert non_empty_string_mask(df["source_root"]).all()
    assert non_empty_string_mask(df["source_ingested_utc"]).all()


def test_corporate_actions_payload_integrity_rules() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert non_empty_string_mask(df["corporate_action_id"]).all()
    assert df["corporate_action_id"].duplicated().sum() == validations["duplicate_corporate_action_id_count"] == 0
    assert non_empty_string_mask(df["instrument_id"]).all()
    assert non_empty_string_mask(df["ticker"]).all()
    assert set(df["action_type"]) == {"split", "dividend", "ticker_change"}
    assert set(df["source_system"]) == {"reference", "additional"}
    assert df["action_date"].notna().all()
    assert validations["missing_action_date_count"] == 0
    assert validations["missing_instrument_id_count"] == 0
    assert validations["hard_fail_count"] == 0

    splits = df.loc[df["action_type"].eq("split")]
    assert splits["split_from"].gt(0).all()
    assert splits["split_to"].gt(0).all()
    assert validations["invalid_split_terms_count"] == 0

    dividends = df.loc[df["action_type"].eq("dividend")]
    assert dividends["cash_amount"].ge(0).all()
    assert validations["negative_dividend_amount_count"] == 0

    assert df.loc[df["source_system"].eq("reference"), "is_reference_primary_source"].all()
    assert df.loc[df["source_system"].eq("additional"), "is_additional_secondary_source"].all()
    assert df["source_priority"].isin([1, 2]).all()


def test_corporate_actions_reconciles_counts_to_source_roots(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    con = duckdb.connect()
    result = con.execute(
        """
        with instruments as (
          select ticker from read_parquet('E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet')
        ),
        ref_splits as (
          select 'reference:split' as source_action_key, upper(ticker) ticker
          from read_parquet('E:/TSIS/data/reference/splits/**/*.parquet', union_by_name=true)
          where execution_date is not null and split_from is not null and split_to is not null
        ),
        add_splits as (
          select 'additional:split' as source_action_key, upper(ticker) ticker
          from read_parquet('E:/TSIS/data/additional/corporate_actions/splits/**/*.parquet', union_by_name=true)
          where coalesce(_empty,false)=false and execution_date is not null and split_from is not null and split_to is not null
        ),
        ref_divs as (
          select 'reference:dividend' as source_action_key, upper(ticker) ticker
          from read_parquet('E:/TSIS/data/reference/dividends/**/*.parquet', union_by_name=true)
          where ex_dividend_date is not null and cash_amount is not null
        ),
        add_divs as (
          select 'additional:dividend' as source_action_key, upper(ticker) ticker
          from read_parquet('E:/TSIS/data/additional/corporate_actions/dividends/**/*.parquet', union_by_name=true)
          where coalesce(_empty,false)=false and ex_dividend_date is not null and cash_amount is not null
        ),
        ref_events_raw as (
          select upper(ticker) ticker, unnest(events) as e
          from read_parquet('E:/TSIS/data/reference/events/**/*.parquet', union_by_name=true)
          where events is not null
        ),
        ref_events as (
          select 'reference:ticker_change' as source_action_key, ticker
          from ref_events_raw
          where e.type='ticker_change' and e.date is not null
        ),
        add_events as (
          select 'additional:ticker_change' as source_action_key, upper(ticker) ticker
          from read_parquet('E:/TSIS/data/additional/corporate_actions/ticker_events/**/*.parquet', union_by_name=true)
          where coalesce(_empty,false)=false and type='ticker_change' and date is not null
        ),
        all_rows as (
          select * from ref_splits union all select * from add_splits union all
          select * from ref_divs union all select * from add_divs union all
          select * from ref_events union all select * from add_events
        )
        select source_action_key, count(*)::bigint as row_count
        from all_rows inner join instruments using(ticker)
        group by source_action_key
        order by source_action_key
        """
    ).fetchdf()

    actual = {row["source_action_key"]: int(row["row_count"]) for _, row in result.iterrows()}
    assert actual == manifest["validations"]["counts_by_source_action"]
    assert sum(actual.values()) == manifest["validations"]["row_count"]

    write_json_artifact(
        tsis_artifacts_dir,
        "corporate_actions_table_source_reconciliation.json",
        {
            "counts_by_source_action": actual,
            "row_count": sum(actual.values()),
        },
    )
