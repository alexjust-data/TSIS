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


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/event_windows_table")
OUTPUT_PATH = OUTPUT_ROOT / "event_windows_table_v0_1.parquet"
MANIFEST_PATH = OUTPUT_ROOT / "_event_windows_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_event_windows_table_summary_v0_1.csv"

SOURCE_HALTS = Path("E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet")
SOURCE_INSTRUMENT_MASTER = Path(
    "E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet"
)
SOURCE_MARKET_CALENDAR = Path(
    "E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet"
)

EXPECTED_SCOPE = "halts_intraday_lt1b_calendar_covered"
EXPECTED_ROLES = {
    "prior_session_regular",
    "pre_event_30m",
    "event_to_resume_or_30m",
    "same_session_regular",
    "next_session_regular",
}

REQUIRED_COLUMNS = {
    "event_window_id",
    "source_event_id",
    "event_source_dataset_id",
    "event_family",
    "event_type",
    "event_code",
    "event_source",
    "ticker",
    "instrument_id",
    "issuer_name",
    "listing_exchange",
    "session_date",
    "year",
    "month",
    "event_time_utc",
    "resume_trade_utc",
    "event_session_phase",
    "window_role",
    "window_start_utc",
    "window_end_utc",
    "window_duration_minutes",
    "window_start_source",
    "window_end_source",
    "contains_event_time",
    "contains_post_event_information",
    "leakage_safe_as_pre_event_feature",
    "source_event_quality_state",
    "source_halt_event_state",
    "source_resume_trade_observed",
    "event_response_end_observed",
    "event_window_quality_state",
    "event_window_consumption_state",
    "session_open_utc",
    "session_close_utc",
    "session_minutes",
    "is_early_close",
    "calendar",
    "timezone",
    "previous_session_date",
    "next_session_date",
    "instrument_identity_temporal_match",
    "is_common_stock",
    "is_lt1b_operational",
    "lt1b_classification_1b",
    "valid_for_event_engine",
    "valid_for_microstructure_feature_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_outcome_window_candidate",
    "valid_for_backtest_event_window_candidate",
    "valid_for_rl_state_component_candidate",
    "requires_decision_time_availability_contract",
    "full_universe_claim",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
    "source_halts_table_path",
    "source_halts_table_sha256",
    "source_instrument_master_path",
    "source_instrument_master_sha256",
    "source_market_calendar_path",
    "source_market_calendar_sha256",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _dataset_glob() -> str:
    return str(OUTPUT_PATH).replace("\\", "/")


def _frame() -> pd.DataFrame:
    return duckdb.sql(f"select * from read_parquet('{_dataset_glob()}')").fetchdf()


def test_event_windows_manifest_hashes_contracts_and_sources(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "event_windows_table_v0_1"
    assert manifest["schema_version"] == "event_windows_table_v0_1"
    assert manifest["quality_policy_version"] == "event_windows_table_policy_v0_1"
    assert manifest["source_event_dataset_id"] == "halts_table_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["full_universe_claim"] is False
    assert OUTPUT_PATH.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == OUTPUT_PATH
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_file(OUTPUT_PATH) == manifest["output_sha256"]
    assert Path(manifest["source_halts_table"]) == SOURCE_HALTS
    assert Path(manifest["source_instrument_master"]) == SOURCE_INSTRUMENT_MASTER
    assert Path(manifest["source_market_calendar"]) == SOURCE_MARKET_CALENDAR
    assert sha256_file(SOURCE_HALTS) == manifest["source_halts_table_sha256"]
    assert sha256_file(SOURCE_INSTRUMENT_MASTER) == manifest["source_instrument_master_sha256"]
    assert sha256_file(SOURCE_MARKET_CALENDAR) == manifest["source_market_calendar_sha256"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "event_windows_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "materialization_scope": manifest["materialization_scope"],
            "output_sha256": manifest["output_sha256"],
            "source_event_dataset_id": manifest["source_event_dataset_id"],
            "validations": manifest["validations"],
        },
    )


def test_event_windows_schema_scope_counts_and_gates(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    df = _frame()

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 214_112
    assert df["event_window_id"].nunique() == validations["unique_event_window_id_count"] == 214_112
    assert validations["duplicate_event_window_id_count"] == 0
    assert df["source_event_id"].nunique() == validations["source_event_count"] == 42_829
    assert validations["source_valid_intraday_event_count"] == 131_671
    assert validations["identity_temporal_match_event_count"] == 44_976
    assert validations["calendar_covered_event_count"] == 42_829
    assert validations["excluded_no_temporal_identity_event_count"] == 86_695
    assert validations["excluded_no_market_calendar_session_event_count"] == 2_147
    assert non_empty_string_mask(df["event_window_id"]).all()
    assert non_empty_string_mask(df["source_event_id"]).all()
    assert set(df["event_source_dataset_id"]) == {"halts_table_v0_1"}
    assert set(df["event_family"]) == {"halt"}
    assert set(df["window_role"]) == EXPECTED_ROLES
    assert set(df["materialization_scope"]) == {EXPECTED_SCOPE}
    assert set(df["schema_version"]) == {"event_windows_table_v0_1"}
    assert set(df["quality_policy_version"]) == {"event_windows_table_policy_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_rl_state_component_candidate"].any()
    assert df["requires_decision_time_availability_contract"].all()
    assert df["instrument_identity_temporal_match"].all()
    assert df["is_common_stock"].all()
    assert df["is_lt1b_operational"].all()

    assert validations["window_role_counts"] == {
        "prior_session_regular": 42_829,
        "pre_event_30m": 42_829,
        "event_to_resume_or_30m": 42_829,
        "same_session_regular": 42_829,
        "next_session_regular": 42_796,
    }
    assert validations["event_session_phase_counts"] == {
        "regular": 38_672,
        "afterhours": 2_537,
        "premarket": 1_620,
    }
    assert validations["event_window_quality_state_counts"] == {
        "good": 213_651,
        "review_resume_fallback": 461,
    }
    assert validations["resume_fallback_window_count"] == 461
    assert validations["full_universe_claim_rows"] == 0
    assert validations["rl_state_component_candidate_rows"] == 0

    write_json_artifact(
        tsis_artifacts_dir,
        "event_windows_table_scope_check.json",
        {
            "rows": int(len(df)),
            "source_events": int(df["source_event_id"].nunique()),
            "window_role_counts": validations["window_role_counts"],
            "event_session_phase_counts": validations["event_session_phase_counts"],
            "quality_counts": validations["event_window_quality_state_counts"],
        },
    )


def test_event_windows_temporal_leakage_and_role_semantics() -> None:
    df = _frame()
    start = pd.to_datetime(df["window_start_utc"], utc=True)
    end = pd.to_datetime(df["window_end_utc"], utc=True)
    event_time = pd.to_datetime(df["event_time_utc"], utc=True)

    assert (end > start).all()
    assert (df["window_duration_minutes"] > 0).all()

    pre = df[df["window_role"].eq("pre_event_30m")]
    pre_end = pd.to_datetime(pre["window_end_utc"], utc=True)
    pre_event = pd.to_datetime(pre["event_time_utc"], utc=True)
    assert (pre_end == pre_event).all()
    assert pre["leakage_safe_as_pre_event_feature"].all()
    assert pre["valid_for_ml_feature_candidate"].all()
    assert not pre["contains_post_event_information"].any()

    response = df[df["window_role"].eq("event_to_resume_or_30m")]
    response_start = pd.to_datetime(response["window_start_utc"], utc=True)
    response_event = pd.to_datetime(response["event_time_utc"], utc=True)
    assert (response_start == response_event).all()
    assert response["contains_event_time"].all()
    assert response["contains_post_event_information"].all()
    assert response["valid_for_outcome_window_candidate"].all()
    assert not response["valid_for_ml_feature_candidate"].any()

    ml_features = df[df["valid_for_ml_feature_candidate"]]
    assert ml_features["leakage_safe_as_pre_event_feature"].all()
    assert not ml_features["contains_post_event_information"].any()
    assert set(ml_features["window_role"]) == {"prior_session_regular", "pre_event_30m"}

    post_info = df[df["contains_post_event_information"]]
    assert not post_info["valid_for_ml_feature_candidate"].any()


def test_event_windows_source_reconciliation(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    validations = manifest["validations"]

    halts = pd.read_parquet(
        SOURCE_HALTS,
        columns=["halt_event_id", "ticker", "halt_date", "valid_for_intraday_mask"],
    )
    instruments = pd.read_parquet(
        SOURCE_INSTRUMENT_MASTER,
        columns=["instrument_id", "ticker", "valid_from", "valid_to"],
    )
    calendar = pd.read_parquet(SOURCE_MARKET_CALENDAR, columns=["session_date"])

    halts = halts[halts["valid_for_intraday_mask"].eq(True)].copy()
    halts["ticker"] = halts["ticker"].astype(str).str.upper().str.strip()
    halts["halt_date"] = pd.to_datetime(halts["halt_date"]).dt.normalize()
    instruments["ticker"] = instruments["ticker"].astype(str).str.upper().str.strip()
    instruments["valid_from"] = pd.to_datetime(instruments["valid_from"], errors="coerce").dt.normalize()
    instruments["valid_to"] = pd.to_datetime(instruments["valid_to"], errors="coerce").dt.normalize()
    calendar_dates = set(pd.to_datetime(calendar["session_date"]).dt.normalize())

    merged = halts.merge(instruments, on="ticker", how="left")
    temporal = merged[
        merged["instrument_id"].notna()
        & (merged["valid_from"].isna() | (merged["valid_from"] <= merged["halt_date"]))
        & (merged["valid_to"].isna() | (merged["valid_to"] >= merged["halt_date"]))
    ].copy()
    temporal_events = temporal["halt_event_id"].nunique()
    calendar_events = temporal[temporal["halt_date"].isin(calendar_dates)]["halt_event_id"].nunique()

    assert halts["halt_event_id"].nunique() == validations["source_valid_intraday_event_count"]
    assert temporal_events == validations["identity_temporal_match_event_count"]
    assert calendar_events == validations["calendar_covered_event_count"]
    assert validations["source_valid_intraday_event_count"] - temporal_events == validations[
        "excluded_no_temporal_identity_event_count"
    ]
    assert temporal_events - calendar_events == validations[
        "excluded_no_market_calendar_session_event_count"
    ]

    df = _frame()
    assert set(df["source_event_id"]).issubset(set(temporal["halt_event_id"]))

    write_json_artifact(
        tsis_artifacts_dir,
        "event_windows_table_source_reconciliation.json",
        {
            "source_valid_intraday_event_count": int(halts["halt_event_id"].nunique()),
            "identity_temporal_match_event_count": int(temporal_events),
            "calendar_covered_event_count": int(calendar_events),
            "output_source_event_count": int(df["source_event_id"].nunique()),
        },
    )
