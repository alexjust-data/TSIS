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


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/halts_table")
MANIFEST_PATH = OUTPUT_ROOT / "_halts_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_halts_table_summary_v0_1.csv"

SOURCE_MASTER = Path("E:/TSIS/data/Halts/processed/halts_master_multisource.parquet")

REQUIRED_COLUMNS = {
    "halt_event_id",
    "source_event_key",
    "source_row_number",
    "duplicate_source_event_key",
    "source_dataset_id",
    "source",
    "source_priority",
    "ticker",
    "issuer_name",
    "listing_exchange",
    "halt_date",
    "halt_start_et",
    "resume_quote_et",
    "resume_trade_et",
    "halt_code",
    "halt_type",
    "raw_reason",
    "release_no",
    "item_link",
    "url_source",
    "is_sec_suspension",
    "halt_event_state",
    "event_granularity",
    "quality_state",
    "intraday_consumption_state",
    "source_allowed",
    "has_ticker",
    "has_halt_date",
    "has_halt_start_et",
    "has_resume_quote_et",
    "has_resume_trade_et",
    "future_date_flag",
    "timestamp_order_review_flag",
    "parse_suspect_flag",
    "missing_core_event_flag",
    "valid_for_event_engine",
    "valid_for_intraday_mask",
    "valid_for_date_context",
    "valid_for_backtest_event_mask_candidate",
    "valid_for_ml_flagged_candidate",
    "valid_for_execution_context_candidate",
    "prohibited_as_alpha",
    "requires_decision_time_availability_contract",
    "visual_case_bucket",
    "market_overlay_state",
    "source_master_path",
    "source_master_sha256",
    "schema_version",
    "build_run_id",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _frame() -> pd.DataFrame:
    return pd.read_parquet(_manifest()["output_path"])


def test_halts_table_manifest_hashes_contracts_and_source(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    output_path = Path(manifest["output_path"])
    summary_path = Path(manifest["summary_path"])
    source_master = Path(manifest["source_master"])
    source_summary = Path(manifest["source_summary"])

    assert manifest["dataset_id"] == "halts_table_v0_1"
    assert manifest["schema_version"] == "halts_table_v0_1"
    assert manifest["source_dataset_id"] == "halts_v0_1"
    assert output_path.exists()
    assert summary_path.exists()
    assert summary_path == SUMMARY_PATH
    assert source_master == SOURCE_MASTER
    assert source_master.exists()
    assert source_summary.exists()
    assert sha256_file(output_path) == manifest["output_sha256"]
    assert sha256_file(source_master) == manifest["source_master_sha256"]
    assert sha256_file(source_summary) == manifest["source_summary_sha256"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "halts_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": str(output_path),
            "output_sha256": manifest["output_sha256"],
            "source_master": str(source_master),
            "source_master_sha256": manifest["source_master_sha256"],
            "validations": manifest["validations"],
        },
    )


def test_halts_table_schema_counts_and_lineage() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 133_116
    assert df["halt_event_id"].nunique() == validations["unique_halt_event_id_count"] == 133_116
    assert validations["duplicate_halt_event_id_count"] == 0
    assert non_empty_string_mask(df["halt_event_id"]).all()
    assert non_empty_string_mask(df["source_event_key"]).all()
    assert set(df["schema_version"]) == {"halts_table_v0_1"}
    assert set(df["source_dataset_id"]) == {"halts_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert set(df["source_master_sha256"]) == {manifest["source_master_sha256"]}
    assert df["source_row_number"].is_unique
    assert df["source_row_number"].min() == 0
    assert df["source_row_number"].max() == 133_115


def test_halts_table_source_reconciliation(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    df = _frame()
    source = pd.read_parquet(SOURCE_MASTER)

    expected_source_counts = {"nasdaq": 118_592, "nyse": 13_178, "sec": 1_346}
    actual_source_counts = {str(k): int(v) for k, v in df["source"].value_counts().items()}
    source_counts = {str(k): int(v) for k, v in source["source"].value_counts().items()}

    assert actual_source_counts == expected_source_counts
    assert source_counts == expected_source_counts
    assert manifest["validations"]["source_counts"] == expected_source_counts
    assert len(df) == len(source)

    for column in [
        "source",
        "source_priority",
        "ticker",
        "halt_date",
        "halt_start_et",
        "resume_trade_et",
        "halt_code",
        "is_sec_suspension",
    ]:
        pd.testing.assert_series_equal(
            df[column].reset_index(drop=True),
            source[column].reset_index(drop=True),
            check_names=False,
        )

    write_json_artifact(
        tsis_artifacts_dir,
        "halts_table_source_reconciliation.json",
        {
            "source_counts": actual_source_counts,
            "row_count": len(df),
            "source_master": str(SOURCE_MASTER),
        },
    )


def test_halts_table_quality_gates_and_known_anomalies(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert set(df["source"]) == {"nasdaq", "nyse", "sec"}
    assert df["source_allowed"].all()
    assert set(df["quality_state"]) == {"good", "review", "bad"}
    assert set(df["halt_event_state"]) == {
        "good_full_intraday_event",
        "regulatory_context_only",
        "review_partial_identity",
        "bad_unusable_event",
    }

    assert validations["missing_halt_date_count"] == 11
    assert validations["future_date_flag_count"] == 8
    assert validations["timestamp_order_review_flag_count"] == 87
    assert validations["parse_suspect_flag_count"] == 88
    assert validations["hard_fail_count"] == 11
    assert validations["review_count"] == 88
    assert validations["duplicate_source_event_key_row_count"] == 1709

    assert validations["event_state_counts"] == {
        "good_full_intraday_event": 131_671,
        "regulatory_context_only": 1_346,
        "review_partial_identity": 88,
        "bad_unusable_event": 11,
    }
    assert validations["quality_state_counts"] == {
        "good": 133_017,
        "review": 88,
        "bad": 11,
    }

    bad = df.loc[df["quality_state"].eq("bad")]
    review = df.loc[df["quality_state"].eq("review")]
    regulatory = df.loc[df["halt_event_state"].eq("regulatory_context_only")]

    assert not bad["valid_for_event_engine"].any()
    assert not bad["valid_for_intraday_mask"].any()
    assert not review["valid_for_intraday_mask"].any()
    assert not regulatory["valid_for_intraday_mask"].any()
    assert df.loc[df["valid_for_backtest_event_mask_candidate"], "valid_for_intraday_mask"].all()
    assert df["prohibited_as_alpha"].all()
    assert df["requires_decision_time_availability_contract"].all()

    write_json_artifact(
        tsis_artifacts_dir,
        "halts_table_quality_gates.json",
        {
            "event_state_counts": validations["event_state_counts"],
            "quality_state_counts": validations["quality_state_counts"],
            "known_anomalies": {
                "missing_halt_date_count": validations["missing_halt_date_count"],
                "future_date_flag_count": validations["future_date_flag_count"],
                "timestamp_order_review_flag_count": validations["timestamp_order_review_flag_count"],
                "duplicate_source_event_key_row_count": validations["duplicate_source_event_key_row_count"],
            },
        },
    )
