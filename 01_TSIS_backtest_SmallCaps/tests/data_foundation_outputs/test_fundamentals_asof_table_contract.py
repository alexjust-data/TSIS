from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    non_empty_string_mask,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table")
DATASET_DIR = OUTPUT_ROOT / "fundamentals_asof_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_fundamentals_asof_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_fundamentals_asof_table_summary_v0_1.csv"

EXPECTED_SCOPE = "additional_financials_core_lt1b_statement_asof_v0_1"
EXPECTED_SOURCE_ROOT = "E:/TSIS/data/additional/financials"
EXPECTED_STATEMENT_FAMILIES = {
    "income_statements",
    "balance_sheets",
    "cash_flow_statements",
}

REQUIRED_COLUMNS = {
    "fundamental_asof_id",
    "ticker",
    "instrument_id",
    "statement_family",
    "source_dataset_id",
    "source_subblock",
    "period_end",
    "filing_date",
    "as_of_date",
    "as_of_year",
    "fiscal_year",
    "fiscal_quarter",
    "timeframe",
    "cik",
    "source_tickers",
    "instrument_identity_temporal_match",
    "instrument_identity_state",
    "fundamental_quality_state",
    "valid_for_event_context_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_backtest_context_candidate",
    "valid_for_state_component_candidate",
    "valid_for_rl_training_direct",
    "as_of_semantics",
    "period_end_is_availability_date",
    "requires_event_time_filter",
    "prohibited_without_asof_filter",
    "contains_future_information_without_event_filter",
    "ratios_excluded_from_core_v0_1",
    "standalone_financial_root_excluded_from_core_v0_1",
    "source_root",
    "source_file",
    "source_file_relative_path",
    "source_file_row_number",
    "source_empty_sentinel",
    "_dataset",
    "_ingested_utc",
    "full_universe_claim",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
    "revenue",
    "total_assets",
    "net_cash_from_operating_activities",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _glob() -> str:
    return (DATASET_DIR / "**" / "*.parquet").as_posix()


def _frame() -> pd.DataFrame:
    return duckdb.sql(
        f"select * from read_parquet('{_glob()}', union_by_name=true, hive_partitioning=true)"
    ).fetchdf()


def test_fundamentals_asof_manifest_hashes_contracts_and_sources(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "fundamentals_asof_table_v0_1"
    assert manifest["schema_version"] == "fundamentals_asof_table_v0_1"
    assert manifest["quality_policy_version"] == "fundamentals_asof_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["source_dataset_id"] == "additional_v0_1"
    assert manifest["source_subblock"] == "financials_core"
    assert set(manifest["source_statement_families"]) == EXPECTED_STATEMENT_FAMILIES
    assert manifest["source_root"] == EXPECTED_SOURCE_ROOT
    assert manifest["full_universe_claim"] is False
    assert manifest["direct_rl_training_allowed"] is False
    assert Path(manifest["dataset_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert manifest["excluded_source_subblocks"]["ratios"].startswith("review_sparse")
    assert "audit_status_FAIL" in manifest["excluded_source_subblocks"]["E:/TSIS/data/financial"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "fundamentals_asof_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "build_run_id": manifest["build_run_id"],
            "output_tree": manifest["output_tree"],
            "source_inventory": manifest["source_inventory"],
        },
    )


def test_fundamentals_asof_schema_counts_quality_and_gates(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    df = _frame()

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 621_756
    assert df["fundamental_asof_id"].nunique() == 621_756
    assert validations["duplicate_fundamental_asof_id_count"] == 0
    assert validations["duplicate_source_key_count"] == 0
    assert df["ticker"].nunique() == validations["ticker_count"] == 4_813
    assert df["instrument_id"].nunique() == validations["instrument_count"] == 4_590
    assert set(df["statement_family"]) == EXPECTED_STATEMENT_FAMILIES
    assert set(df["materialization_scope"]) == {EXPECTED_SCOPE}
    assert set(df["schema_version"]) == {"fundamentals_asof_table_v0_1"}
    assert set(df["quality_policy_version"]) == {"fundamentals_asof_table_policy_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert non_empty_string_mask(df["fundamental_asof_id"]).all()
    assert non_empty_string_mask(df["ticker"]).all()

    assert validations["fundamental_quality_state_counts"] == {
        "good_statement_asof": 500_530,
        "review_no_temporal_identity": 121_217,
        "review_period_after_filing_date": 9,
    }
    assert validations["good_statement_asof_rows"] == 500_530
    assert validations["review_rows"] == 121_226
    assert validations["bad_rows"] == 0
    assert validations["valid_for_event_context_candidate_rows"] == 500_530
    assert validations["valid_for_ml_feature_candidate_rows"] == 500_530
    assert validations["valid_for_backtest_context_candidate_rows"] == 500_530
    assert validations["valid_for_state_component_candidate_rows"] == 500_530
    assert validations["valid_for_rl_training_direct_rows"] == 0
    assert validations["full_universe_claim_rows"] == 0

    assert not df["full_universe_claim"].any()
    assert not df["valid_for_rl_training_direct"].any()
    assert df["requires_event_time_filter"].all()
    assert df["prohibited_without_asof_filter"].all()
    assert df["ratios_excluded_from_core_v0_1"].all()
    assert df["standalone_financial_root_excluded_from_core_v0_1"].all()

    write_json_artifact(
        tsis_artifacts_dir,
        "fundamentals_asof_scope_quality_check.json",
        {
            "rows": int(len(df)),
            "quality_counts": validations["fundamental_quality_state_counts"],
            "statement_family_counts": validations["statement_family_counts"],
        },
    )


def test_fundamentals_asof_source_reconciliation_and_family_counts(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    source_inventory = manifest["source_inventory"]
    df = _frame()

    assert source_inventory["file_count"] == 14_472
    assert source_inventory["business_file_count"] == 14_436
    assert source_inventory["empty_sentinel_file_count"] == 36
    assert source_inventory["business_row_count"] == 621_756
    assert source_inventory["families"]["income_statements"]["business_rows"] == 242_886
    assert source_inventory["families"]["balance_sheets"]["business_rows"] == 136_661
    assert source_inventory["families"]["cash_flow_statements"]["business_rows"] == 242_209

    for family, expected in validations["statement_family_counts"].items():
        actual = df[df["statement_family"].eq(family)]
        assert len(actual) == expected["rows"]
        assert actual["ticker"].nunique() == expected["tickers"]
        assert actual["instrument_id"].nunique() == expected["instruments"]
        assert int(actual["valid_for_event_context_candidate"].sum()) == expected[
            "valid_for_event_context_candidate_rows"
        ]
        assert not actual["source_empty_sentinel"].any()

    summary = pd.read_csv(SUMMARY_PATH)
    assert int(summary["rows"].sum()) == 621_756

    write_json_artifact(
        tsis_artifacts_dir,
        "fundamentals_asof_source_reconciliation.json",
        {
            "source_inventory": source_inventory,
            "summary_rows": int(summary["rows"].sum()),
        },
    )


def test_fundamentals_asof_temporal_semantics_and_leakage_guards() -> None:
    df = _frame()

    assert df["as_of_date"].equals(df["filing_date"])
    assert not df["period_end_is_availability_date"].any()
    assert set(df["as_of_semantics"]) == {"filing_date_available_from_date_only"}

    good = df[df["fundamental_quality_state"].eq("good_statement_asof")]
    assert not good.empty
    assert (good["period_end"] <= good["as_of_date"]).all()
    assert good["instrument_identity_temporal_match"].all()
    assert good["valid_for_event_context_candidate"].all()
    assert good["valid_for_ml_feature_candidate"].all()
    assert good["valid_for_backtest_context_candidate"].all()

    review = df[df["fundamental_quality_state"].ne("good_statement_asof")]
    assert not review.empty
    assert not review["valid_for_event_context_candidate"].any()
    assert not review["valid_for_ml_feature_candidate"].any()
    assert not review["valid_for_backtest_context_candidate"].any()

    period_after_filing = df[df["fundamental_quality_state"].eq("review_period_after_filing_date")]
    assert len(period_after_filing) == 9
    assert (period_after_filing["period_end"] > period_after_filing["as_of_date"]).all()
