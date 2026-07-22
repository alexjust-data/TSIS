from __future__ import annotations

from pathlib import Path

import pandas as pd

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    non_empty_string_mask,
    sha256_file,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/instrument_master")
MANIFEST_PATH = OUTPUT_ROOT / "_instrument_master_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_instrument_master_summary_v0_1.csv"

REQUIRED_COLUMNS = {
    "instrument_id",
    "ticker",
    "identity_resolution_level",
    "ticker_identity_scope",
    "valid_from",
    "valid_to",
    "name",
    "market",
    "locale",
    "primary_exchange",
    "ticker_type_code",
    "ticker_type_description",
    "is_common_stock",
    "active_in_reference",
    "currency_name",
    "cik",
    "composite_figi",
    "share_class_figi",
    "exchange_name",
    "exchange_acronym",
    "exchange_mic",
    "exchange_operating_mic",
    "overview_request_date",
    "overview_market_cap",
    "overview_sic_code",
    "overview_sic_description",
    "overview_list_date",
    "overview_ticker_root",
    "overview_weighted_shares_outstanding",
    "is_lt1b_operational",
    "lt1b_first_seen_date",
    "lt1b_last_observed_date",
    "lt1b_anchor_date_used",
    "lt1b_status_rebuilt",
    "lt1b_classification_1b",
    "lt1b_classification_reason_1b",
    "lt1b_market_cap_t",
    "lt1b_is_small_cap_t",
    "lt1b_shares_source",
    "lt1b_shares_observed_date",
    "lt1b_shares_age_days",
    "has_reference_events",
    "ticker_change_event_count",
    "first_ticker_change_date",
    "latest_ticker_change_date",
    "reference_snapshot_date",
    "reference_snapshot_timing",
    "reference_last_updated_utc",
    "source_reference_root",
    "source_lt1b_universe_path",
    "build_run_id",
    "schema_version",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _frame() -> pd.DataFrame:
    return pd.read_parquet(_manifest()["output_path"])


def test_instrument_master_manifest_paths_hashes_and_contract_links(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    output_path = Path(manifest["output_path"])
    summary_path = Path(manifest["summary_path"])

    assert manifest["dataset_id"] == "instrument_master_v0_1"
    assert manifest["schema_version"] == "instrument_master_v0_1"
    assert output_path.exists()
    assert summary_path.exists()
    assert summary_path == SUMMARY_PATH
    assert sha256_file(output_path) == manifest["output_sha256"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "instrument_master_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": str(output_path),
            "output_sha256": manifest["output_sha256"],
            "summary_path": str(summary_path),
            "validations": manifest["validations"],
        },
    )


def test_instrument_master_schema_lineage_and_manifest_counts() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 4824
    assert df["ticker"].nunique() == validations["ticker_count"] == 4824
    assert set(df["schema_version"]) == {"instrument_master_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert non_empty_string_mask(df["created_at_utc"]).all()
    assert non_empty_string_mask(df["source_reference_root"]).all()
    assert non_empty_string_mask(df["source_lt1b_universe_path"]).all()


def test_instrument_master_identity_and_operational_filters() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert non_empty_string_mask(df["ticker"]).all()
    assert non_empty_string_mask(df["instrument_id"]).all()
    assert df["ticker"].duplicated().sum() == validations["duplicate_ticker_count"] == 0
    assert df["is_lt1b_operational"].eq(True).all()
    assert df["is_common_stock"].eq(True).all()
    assert set(df["ticker_type_code"]) == {"CS"}
    assert validations["non_common_stock_count"] == 0
    assert validations["hard_fail_count"] == 0
    assert validations["invalid_window_count"] == 0
    assert (df["valid_from"] <= df["valid_to"]).all()
    assert df["ticker_change_event_count"].ge(0).all()
    assert set(df["identity_resolution_level"]).issubset(
        {"share_class_figi", "composite_figi", "cik_ticker", "ticker_only_fallback"}
    )
    assert df["identity_resolution_level"].value_counts().to_dict() == validations["identity_resolution_counts"]


def test_instrument_master_reconciles_to_lt1b_source_universe(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    df = _frame()
    source_path = Path(manifest["source_lt1b_universe_path"])
    assert source_path.exists()

    source = pd.read_parquet(source_path, columns=["ticker"])
    source_tickers = set(source["ticker"].astype(str))
    output_tickers = set(df["ticker"].astype(str))

    assert len(source) == len(df)
    assert output_tickers == source_tickers

    write_json_artifact(
        tsis_artifacts_dir,
        "instrument_master_source_reconciliation.json",
        {
            "source_lt1b_universe_path": str(source_path),
            "source_row_count": len(source),
            "output_row_count": len(df),
            "ticker_set_match": True,
        },
    )

