from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from _helpers.data_foundation import assert_relative_contract_paths_exist, sha256_file, write_json_artifact


MODULE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/microstructure_features_table")
DATASET_DIR = OUTPUT_ROOT / "microstructure_features_table_v0_2_candidate_controlled_25_per_role"
DATASET_PARTITION = DATASET_DIR / "year=2025" / "month=12" / "part-0000.parquet"
MANIFEST_PATH = OUTPUT_ROOT / "_microstructure_features_table_manifest_v0_2_candidate_controlled_25_per_role.json"
SUMMARY_PATH = OUTPUT_ROOT / "_microstructure_features_table_summary_v0_2_candidate_controlled_25_per_role.csv"
SOURCE_WINDOWS_CSV = (
    MODULE_ROOT
    / "runs/data_foundation/microstructure_features_table_v0_2_candidate_controlled_25_per_role"
    / "microstructure_features_table_v0_2_candidate_window_manifest_v0_1.csv"
)
OFFICIAL_V0_1_DIR = OUTPUT_ROOT / "microstructure_features_table_v0_1"
VISUAL_READOUT = (
    MODULE_ROOT
    / "01_foundations/inspection_dossiers/microstructure_features/"
    "microstructure_candidate_controlled_visual_readout_v0_2.md"
)
VISUAL_MANIFEST = (
    MODULE_ROOT
    / "01_foundations/inspection_dossiers/microstructure_features/"
    "visual_evidence_v0_2_controlled_25_per_role/microstructure_candidate_controlled_visual_manifest_v0_2.json"
)


def _load_manifest() -> dict[str, Any]:
    assert MANIFEST_PATH.exists(), f"Missing manifest: {MANIFEST_PATH}"
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _parquet_files() -> list[Path]:
    assert DATASET_PARTITION.exists(), f"Missing declared candidate partition: {DATASET_PARTITION}"
    return [DATASET_PARTITION]


def _sha256_partitioned_parquet_tree(root: Path) -> dict[str, int | str]:
    digest = hashlib.sha256()
    files = _parquet_files()
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        file_hash = sha256_file(path)
        size = path.stat().st_size
        total_bytes += size
        digest.update(rel.encode("utf-8"))
        digest.update(str(size).encode("ascii"))
        digest.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def _read_candidate_frame() -> pd.DataFrame:
    return pd.read_parquet(DATASET_PARTITION)


def _window_rows_from_quotes(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> int:
    quotes = pd.read_parquet(path, columns=["timestamp"])
    quotes["ts_utc"] = pd.to_datetime(quotes["timestamp"], unit="ns", utc=True, errors="coerce")
    return int(((quotes["ts_utc"] >= start) & (quotes["ts_utc"] < end)).sum())


def _window_rows_from_trades(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> int:
    trades = pd.read_parquet(path, columns=["timestamp"])
    trades["ts_utc"] = pd.to_datetime(trades["timestamp"], utc=True, errors="coerce")
    return int(((trades["ts_utc"] >= start) & (trades["ts_utc"] < end)).sum())


def test_microstructure_v0_2_controlled_candidate_manifest_and_summary(tsis_artifacts_dir: Path) -> None:
    manifest = _load_manifest()
    summary = pd.read_csv(SUMMARY_PATH).iloc[0].to_dict()

    assert DATASET_DIR.exists()
    assert SUMMARY_PATH.exists()
    assert SOURCE_WINDOWS_CSV.exists()
    assert OFFICIAL_V0_1_DIR.exists()
    assert manifest["dataset_id"] == "microstructure_features_table_v0_2_candidate"
    assert manifest["schema_version"] == "microstructure_features_table_v0_2_candidate"
    assert manifest["quality_policy_version"] == "microstructure_features_table_policy_v0_2_candidate"
    assert manifest["materialization_scope"] == "halt_event_windows_microstructure_candidate_controlled_25_per_role"
    assert manifest["full_universe_claim"] is False
    assert manifest["output_path"] == str(DATASET_DIR)
    assert manifest["summary_path"] == str(SUMMARY_PATH)
    assert manifest["manifest_path"] == str(MANIFEST_PATH)
    assert manifest["source_windows_csv"] == str(SOURCE_WINDOWS_CSV)
    assert manifest["source_windows_csv_sha256"] == sha256_file(SOURCE_WINDOWS_CSV)
    assert manifest["source_quotes_root"] == r"D:\quotes"
    assert manifest["source_quotes_root_state"] == "provisional_d_legacy_recovery_root_pending_e_parity"
    assert manifest["future_official_quotes_root"] == r"E:\TSIS\data\quotes"
    assert manifest["quotes_staging_root"] == r"E:\TSIS\data\quotes_"
    assert manifest["source_trades_root"] == r"E:\TSIS\data\trades_ticks_prod_2005_2026"
    assert manifest["source_trades_root_state"] == "official_e_raw_root"

    output_tree = _sha256_partitioned_parquet_tree(DATASET_DIR)
    assert manifest["output_tree"] == output_tree
    assert manifest["validations"]["output_tree_sha256"] == output_tree["tree_sha256"]
    assert_relative_contract_paths_exist(manifest)

    expected_summary = {
        "dataset_id": "microstructure_features_table_v0_2_candidate",
        "materialization_scope": "halt_event_windows_microstructure_candidate_controlled_25_per_role",
        "row_count": 50,
        "ticker_count": 9,
        "window_count": 50,
        "quotes_file_present_rows": 50,
        "trades_file_present_rows": 24,
        "hard_fail_count": 0,
        "execution_sim_candidate_rows": 0,
        "backtest_core_microstructure_candidate_rows": 0,
        "full_universe_claim_rows": 0,
        "duplicate_key_groups": 0,
        "output_tree_sha256": output_tree["tree_sha256"],
    }
    for key, expected in expected_summary.items():
        assert summary[key] == expected
        assert manifest["validations"][key] == expected

    assert manifest["validations"]["source_quotes_rows_total"] == 1_696_033
    assert manifest["validations"]["source_trades_rows_total"] == 202_376
    assert manifest["validations"]["instrument_identity_temporal_match_rows"] == 50

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_v0_2_controlled_candidate_manifest_summary_check.json",
        {
            "manifest": str(MANIFEST_PATH),
            "summary": str(SUMMARY_PATH),
            "dataset_dir": str(DATASET_DIR),
            "validations": manifest["validations"],
            "output_tree": output_tree,
        },
    )


def test_microstructure_v0_2_controlled_candidate_dataset_semantics(tsis_artifacts_dir: Path) -> None:
    frame = _read_candidate_frame()

    assert len(frame) == 50
    assert frame["ticker"].nunique() == 9
    assert frame["event_window_id"].nunique() == 50
    assert set(frame["materialization_scope"]) == {"halt_event_windows_microstructure_candidate_controlled_25_per_role"}
    assert set(frame["schema_version"]) == {"microstructure_features_table_v0_2_candidate"}
    assert set(frame["quality_policy_version"]) == {"microstructure_features_table_policy_v0_2_candidate"}
    assert set(frame["quotes_root_state"]) == {"provisional_d_legacy_recovery_root_pending_e_parity"}
    assert set(frame["trades_root_state"]) == {"official_e_raw_root"}
    assert frame["source_quotes_file_present"].all()
    assert int(frame["source_trades_file_present"].sum()) == 24
    assert int((~frame["source_trades_file_present"]).sum()) == 26
    assert not frame["execution_sim_candidate"].any()
    assert not frame["backtest_core_microstructure_candidate"].any()
    assert not frame["full_universe_claim"].any()

    duplicate_groups = frame.groupby(["event_window_id", "ticker", "window_start_utc", "window_end_utc"]).size()
    assert not duplicate_groups.gt(1).any()

    quality_counts = frame["microstructure_quality_state"].value_counts().to_dict()
    assert quality_counts == {"review_partial_source": 26, "pass_seed_window": 24}
    present_trades = frame[frame["source_trades_file_present"]]
    missing_trades = frame[~frame["source_trades_file_present"]]
    assert present_trades["event_research_microstructure_candidate"].all()
    assert not missing_trades["event_research_microstructure_candidate"].any()
    assert missing_trades["source_trades_file_sha256"].isna().all()
    assert (missing_trades["trades_rows"] == 0).all()
    assert (missing_trades["trades_window_rows"] == 0).all()
    assert frame["instrument_identity_temporal_match"].all()

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_v0_2_controlled_candidate_dataset_semantics_check.json",
        {
            "row_count": int(len(frame)),
            "ticker_count": int(frame["ticker"].nunique()),
            "window_count": int(frame["event_window_id"].nunique()),
            "trades_file_present_rows": int(frame["source_trades_file_present"].sum()),
            "quality_counts": quality_counts,
        },
    )


def test_microstructure_v0_2_controlled_candidate_source_windows_semantics(tsis_artifacts_dir: Path) -> None:
    source_windows = pd.read_csv(SOURCE_WINDOWS_CSV)

    assert len(source_windows) == 50
    assert set(source_windows["event_family"]) == {"halt"}
    assert set(source_windows["source_window_dataset_id"]) == {"event_windows_table_v0_1"}
    assert set(source_windows["event_source_dataset_id"]) == {"halts_table_v0_1"}
    assert set(source_windows["candidate_dataset_id"]) == {"microstructure_features_table_v0_2_candidate"}
    assert set(source_windows["candidate_materialization_scope"]) == {"halt_event_windows_microstructure_candidate"}
    assert set(source_windows["quotes_root_state_required"]) == {"provisional_d_legacy_recovery_root_pending_e_parity"}
    assert set(source_windows["trades_root_state_required"]) == {"official_e_raw_root"}
    assert source_windows["valid_for_microstructure_feature_candidate"].astype(bool).all()
    assert not source_windows["candidate_full_universe_claim"].astype(bool).any()

    role_counts = source_windows["window_role"].value_counts().to_dict()
    assert role_counts == {"pre_event_30m": 25, "same_session_regular": 25}
    ml_rows = source_windows[source_windows["valid_for_ml_feature_candidate"].astype(bool)]
    assert set(ml_rows["window_role"]) == {"pre_event_30m"}
    assert ml_rows["leakage_safe_as_pre_event_feature"].astype(bool).all()
    assert not ml_rows["contains_post_event_information"].astype(bool).any()
    same_session = source_windows[source_windows["window_role"].eq("same_session_regular")]
    assert not same_session["valid_for_ml_feature_candidate"].astype(bool).any()

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_v0_2_controlled_candidate_source_windows_check.json",
        {
            "source_windows_csv": str(SOURCE_WINDOWS_CSV),
            "source_windows_csv_sha256": sha256_file(SOURCE_WINDOWS_CSV),
            "row_count": int(len(source_windows)),
            "role_counts": role_counts,
        },
    )


def test_microstructure_v0_2_controlled_candidate_sample_recomputes_from_raw(
    tsis_artifacts_dir: Path,
) -> None:
    frame = _read_candidate_frame()
    present_row = frame[frame["source_trades_file_present"]].iloc[0]
    missing_row = frame[~frame["source_trades_file_present"]].iloc[0]

    for row in [present_row, missing_row]:
        start = pd.Timestamp(row["window_start_utc"])
        end = pd.Timestamp(row["window_end_utc"])
        quotes_file = Path(row["source_quotes_file"])
        assert quotes_file.exists()
        assert sha256_file(quotes_file) == row["source_quotes_file_sha256"]
        assert _window_rows_from_quotes(quotes_file, start, end) == row["quotes_rows"]

    present_start = pd.Timestamp(present_row["window_start_utc"])
    present_end = pd.Timestamp(present_row["window_end_utc"])
    present_trades_file = Path(present_row["source_trades_file"])
    assert present_trades_file.exists()
    assert sha256_file(present_trades_file) == present_row["source_trades_file_sha256"]
    assert _window_rows_from_trades(present_trades_file, present_start, present_end) == present_row["trades_rows"]

    missing_trades_file = Path(missing_row["source_trades_file"])
    assert not missing_trades_file.exists()
    assert pd.isna(missing_row["source_trades_file_sha256"])
    assert not bool(missing_row["source_trades_file_present"])
    assert missing_row["trades_rows"] == 0
    assert missing_row["microstructure_quality_state"] == "review_partial_source"

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_v0_2_controlled_candidate_raw_recompute_sample.json",
        {
            "present_trade_sample": {
                "ticker": present_row["ticker"],
                "event_window_id": present_row["event_window_id"],
                "quotes_file": present_row["source_quotes_file"],
                "trades_file": present_row["source_trades_file"],
                "quotes_rows": int(present_row["quotes_rows"]),
                "trades_rows": int(present_row["trades_rows"]),
            },
            "missing_trade_sample": {
                "ticker": missing_row["ticker"],
                "event_window_id": missing_row["event_window_id"],
                "quotes_file": missing_row["source_quotes_file"],
                "trades_file": missing_row["source_trades_file"],
                "quotes_rows": int(missing_row["quotes_rows"]),
                "trades_rows": int(missing_row["trades_rows"]),
                "quality_state": missing_row["microstructure_quality_state"],
            },
        },
    )


def test_microstructure_v0_2_controlled_candidate_visual_evidence_pack(tsis_artifacts_dir: Path) -> None:
    assert VISUAL_READOUT.exists()
    assert VISUAL_MANIFEST.exists()
    visual_manifest = json.loads(VISUAL_MANIFEST.read_text(encoding="utf-8"))
    readout_text = VISUAL_READOUT.read_text(encoding="utf-8")

    assert visual_manifest["pack_id"] == "microstructure_candidate_controlled_visual_evidence_v0_2"
    assert visual_manifest["status"] == "visual_forensic_candidate_evidence_only"
    assert visual_manifest["case_count"] == 50
    assert visual_manifest["cached_quote_files_read"] == 9
    assert visual_manifest["cached_trade_files_read"] == 5
    assert visual_manifest["candidate_partition"] == str(DATASET_PARTITION)
    assert visual_manifest["window_manifest"] == str(SOURCE_WINDOWS_CSV)
    assert visual_manifest["official_dataset_created"] is False
    assert visual_manifest["full_universe_claim"] is False
    assert "# Microstructure Candidate Controlled Visual Readout v0.2" in readout_text
    assert "case_count = 50" in readout_text

    cases = visual_manifest["cases"]
    assert len(cases) == 50
    for case in cases:
        image_path = Path(case["image_path"])
        assert image_path.exists(), f"Missing visual evidence image: {image_path}"
        assert image_path.suffix.lower() == ".png"
        assert image_path.stat().st_size > 0

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_v0_2_controlled_candidate_visual_pack_check.json",
        {
            "visual_readout": str(VISUAL_READOUT),
            "visual_manifest": str(VISUAL_MANIFEST),
            "case_count": visual_manifest["case_count"],
            "cached_quote_files_read": visual_manifest["cached_quote_files_read"],
            "cached_trade_files_read": visual_manifest["cached_trade_files_read"],
        },
    )
