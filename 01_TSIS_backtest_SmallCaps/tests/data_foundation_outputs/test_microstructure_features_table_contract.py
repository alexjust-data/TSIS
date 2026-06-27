from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    sha256_file,
    sha256_parquet_tree,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/microstructure_features_table")
DATASET_DIR = OUTPUT_ROOT / "microstructure_features_table_v0_1"
MANIFEST_PATH = OUTPUT_ROOT / "_microstructure_features_table_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_microstructure_features_table_summary_v0_1.csv"

EXPECTED_SCOPE = "seed_event_window_smoke"
REQUIRED_COLUMNS = {
    "microstructure_feature_id",
    "event_window_id",
    "ticker",
    "instrument_id",
    "instrument_identity_temporal_match",
    "session_date",
    "year",
    "month",
    "window_start_utc",
    "window_end_utc",
    "window_label",
    "source_scope_note",
    "quotes_root_used",
    "quotes_root_state",
    "future_official_quotes_root",
    "quotes_staging_root",
    "trades_root_used",
    "trades_root_state",
    "source_quotes_file",
    "source_trades_file",
    "source_quotes_file_present",
    "source_trades_file_present",
    "source_quotes_file_sha256",
    "source_trades_file_sha256",
    "quotes_rows",
    "quotes_window_rows",
    "quotes_crossed_rows",
    "quotes_crossed_ratio_pct_all_rows",
    "quotes_spread_bps_median",
    "trades_rows",
    "trades_window_rows",
    "trades_invalid_price_rows",
    "trades_invalid_size_rows",
    "trades_odd_lot_ratio_pct",
    "trades_duplicate_exact_ratio_pct",
    "trades_off_regular_session_ratio_pct",
    "trades_total_volume",
    "trades_dollar_volume",
    "quotes_family_data_quality_verdict",
    "trades_family_data_quality_verdict",
    "microstructure_quality_state",
    "event_research_microstructure_candidate",
    "execution_sim_candidate",
    "backtest_core_microstructure_candidate",
    "full_universe_claim",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _dataset_glob() -> str:
    return str(DATASET_DIR / "**" / "*.parquet").replace("\\", "/")


def _frame() -> pd.DataFrame:
    return duckdb.sql(f"select * from read_parquet('{_dataset_glob()}', hive_partitioning=true)").fetchdf()


def test_microstructure_manifest_hashes_and_contract_links(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "microstructure_features_table_v0_1"
    assert manifest["schema_version"] == "microstructure_features_table_v0_1"
    assert manifest["quality_policy_version"] == "microstructure_features_table_policy_v0_1"
    assert manifest["materialization_scope"] == EXPECTED_SCOPE
    assert manifest["full_universe_claim"] is False
    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == DATASET_DIR
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_parquet_tree(DATASET_DIR) == manifest["output_tree"]
    assert sha256_file(Path(manifest["source_windows_csv"])) == manifest["source_windows_csv_sha256"]
    assert sha256_file(Path(manifest["source_instrument_master"])) == manifest[
        "source_instrument_master_sha256"
    ]
    assert sha256_file(Path(manifest["source_dataset_certification_matrix"])) == manifest[
        "source_dataset_certification_matrix_sha256"
    ]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_features_table_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "materialization_scope": manifest["materialization_scope"],
            "output_tree": manifest["output_tree"],
            "validations": manifest["validations"],
        },
    )


def test_microstructure_schema_scope_and_seed_counts(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    validations = manifest["validations"]
    df = _frame()

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 1
    assert df["ticker"].nunique() == validations["ticker_count"] == 1
    assert df["event_window_id"].nunique() == validations["window_count"] == 1
    assert set(df["ticker"]) == {"ZYXI"}
    assert set(df["event_window_id"]) == {"seed_zyxi_20251201_full_day"}
    assert set(df["materialization_scope"]) == {EXPECTED_SCOPE}
    assert set(df["schema_version"]) == {"microstructure_features_table_v0_1"}
    assert set(df["quality_policy_version"]) == {"microstructure_features_table_policy_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert df["source_quotes_file_present"].sum() == validations["quotes_file_present_rows"] == 1
    assert df["source_trades_file_present"].sum() == validations["trades_file_present_rows"] == 1
    assert df["quotes_rows"].sum() == validations["source_quotes_rows_total"] == 13_288
    assert df["trades_rows"].sum() == validations["source_trades_rows_total"] == 18_182
    assert df["instrument_identity_temporal_match"].sum() == validations["instrument_identity_temporal_match_rows"] == 1
    assert df["execution_sim_candidate"].sum() == validations["execution_sim_candidate_rows"] == 0
    assert df["backtest_core_microstructure_candidate"].sum() == validations[
        "backtest_core_microstructure_candidate_rows"
    ] == 0
    assert df["full_universe_claim"].sum() == validations["full_universe_claim_rows"] == 0
    assert validations["hard_fail_count"] == 0
    assert validations["duplicate_key_groups"] == 0
    assert set(df["quotes_root_state"]) == {"provisional_d_legacy_recovery_root_pending_e_parity"}
    assert set(df["trades_root_state"]) == {"official_e_raw_root"}
    assert set(df["microstructure_quality_state"]) == {"pass_seed_window"}
    assert df["event_research_microstructure_candidate"].all()

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_features_table_scope_check.json",
        {
            "rows": int(len(df)),
            "ticker": df.iloc[0]["ticker"],
            "event_window_id": df.iloc[0]["event_window_id"],
            "quotes_rows": int(df.iloc[0]["quotes_rows"]),
            "trades_rows": int(df.iloc[0]["trades_rows"]),
            "quotes_root_state": df.iloc[0]["quotes_root_state"],
            "materialization_scope": df.iloc[0]["materialization_scope"],
        },
    )


def test_microstructure_recomputes_seed_metrics_from_raw_sources(tsis_artifacts_dir: Path) -> None:
    df = _frame()
    row = df.iloc[0]
    quotes_file = Path(row["source_quotes_file"])
    trades_file = Path(row["source_trades_file"])
    start = pd.Timestamp(row["window_start_utc"])
    end = pd.Timestamp(row["window_end_utc"])

    assert quotes_file.exists()
    assert trades_file.exists()
    assert sha256_file(quotes_file) == row["source_quotes_file_sha256"]
    assert sha256_file(trades_file) == row["source_trades_file_sha256"]

    quotes = pd.read_parquet(quotes_file)
    quotes["ts_utc"] = pd.to_datetime(quotes["timestamp"], unit="ns", utc=True, errors="coerce")
    quotes = quotes[(quotes["ts_utc"] >= start) & (quotes["ts_utc"] < end)].copy()
    ask = pd.to_numeric(quotes["ask_price"], errors="coerce")
    bid = pd.to_numeric(quotes["bid_price"], errors="coerce")
    two_sided = ask.gt(0) & bid.gt(0)
    crossed = two_sided & ask.lt(bid)
    mid = (ask + bid) / 2.0
    valid_spread = two_sided & ask.gt(bid)
    spread_bps = ((ask - bid) / mid * 10_000.0).where(valid_spread & mid.gt(0))

    assert len(quotes) == row["quotes_rows"] == 13_288
    assert int(two_sided.sum()) == row["quotes_two_sided_rows"] == 13_286
    assert int(crossed.sum()) == row["quotes_crossed_rows"] == 2
    assert abs(float(spread_bps.median(skipna=True)) - float(row["quotes_spread_bps_median"])) < 1e-9

    trades = pd.read_parquet(trades_file)
    trades["ts_utc"] = pd.to_datetime(trades["timestamp"], utc=True, errors="coerce")
    trades = trades[(trades["ts_utc"] >= start) & (trades["ts_utc"] < end)].copy()
    price = pd.to_numeric(trades["price"], errors="coerce")
    size = pd.to_numeric(trades["size"], errors="coerce")
    duplicate_cols = pd.DataFrame(
        {
            "timestamp": trades["ts_utc"].astype(str),
            "price": price,
            "size": size,
            "exchange": trades["exchange"].astype(str),
            "conditions": trades["conditions"].map(str),
        }
    )
    duplicate_rows = duplicate_cols.duplicated(keep=False)

    assert len(trades) == row["trades_rows"] == 18_182
    assert int(price.le(0).sum()) == row["trades_invalid_price_rows"] == 0
    assert int(size.le(0).sum()) == row["trades_invalid_size_rows"] == 0
    assert abs(float(size.where(size.gt(0)).sum(skipna=True)) - float(row["trades_total_volume"])) < 1e-9
    assert abs(float(duplicate_rows.sum()) / len(trades) * 100.0 - float(row["trades_duplicate_exact_ratio_pct"])) < 1e-9

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_features_table_source_reconciliation.json",
        {
            "quotes_file": str(quotes_file),
            "trades_file": str(trades_file),
            "quotes_rows": int(len(quotes)),
            "trades_rows": int(len(trades)),
            "quotes_crossed_rows": int(crossed.sum()),
            "trades_duplicate_exact_rows": int(duplicate_rows.sum()),
        },
    )
