from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import duckdb
import pandas as pd

from _helpers.data_foundation import sha256_file, write_json_artifact


MODULE_ROOT = Path(__file__).resolve().parents[2]
BUILDER = MODULE_ROOT / "scripts/build_microstructure_candidate_window_manifest.py"
MATERIALIZER = MODULE_ROOT / "scripts/materialize_microstructure_features_table.py"
EVENT_WINDOWS = Path("E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet")
OFFICIAL_MICROSTRUCTURE_V0_1 = Path(
    "E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_1"
)

PLAN = (
    MODULE_ROOT
    / "01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md"
)
EVENT_WINDOWS_CONTRACT = (
    MODULE_ROOT / "01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md"
)
MICROSTRUCTURE_CONTRACT = (
    MODULE_ROOT
    / "01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md"
)


def _run_builder(output_dir: Path, max_per_role: int = 3) -> tuple[dict, pd.DataFrame]:
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--event-windows",
            str(EVENT_WINDOWS),
            "--output-dir",
            str(output_dir),
            "--max-per-role",
            str(max_per_role),
            "--overwrite",
        ],
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    manifest = json.loads(Path(payload["manifest"]).read_text(encoding="utf-8"))
    frame = pd.read_csv(payload["csv"])
    return manifest, frame


def test_microstructure_candidate_manifest_contract_stack_exists(tsis_artifacts_dir: Path) -> None:
    paths = {
        "builder": BUILDER,
        "materializer": MATERIALIZER,
        "event_windows_table": EVENT_WINDOWS,
        "microstructure_plan": PLAN,
        "event_windows_contract": EVENT_WINDOWS_CONTRACT,
        "microstructure_contract": MICROSTRUCTURE_CONTRACT,
    }
    missing = {name: str(path) for name, path in paths.items() if not path.exists()}
    assert missing == {}
    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_candidate_window_manifest_contract_stack.json",
        {name: str(path) for name, path in paths.items()},
    )


def test_microstructure_candidate_manifest_builds_from_event_windows_denominator(
    tsis_artifacts_dir: Path,
) -> None:
    output_dir = tsis_artifacts_dir / "microstructure_candidate_window_manifest"
    manifest, frame = _run_builder(output_dir, max_per_role=3)

    assert manifest["manifest_id"] == "microstructure_features_table_v0_2_candidate_window_manifest"
    assert manifest["manifest_version"] == "v0_1"
    assert manifest["candidate_dataset_id"] == "microstructure_features_table_v0_2_candidate"
    assert manifest["candidate_materialization_scope"] == "halt_event_windows_microstructure_candidate"
    assert manifest["candidate_full_universe_claim"] is False
    assert manifest["source_window_dataset_id"] == "event_windows_table_v0_1"
    assert manifest["source_event_dataset_id"] == "halts_table_v0_1"
    assert manifest["source_event_family"] == "halt"
    assert manifest["requested_roles"] == ["pre_event_30m", "same_session_regular"]
    assert manifest["max_per_role"] == 3
    assert manifest["source_counts"]["source_event_windows_rows"] == 214_112
    assert manifest["source_counts"]["eligible_microstructure_rows"] == 85_658
    assert manifest["source_counts"]["eligible_role_counts"] == {
        "pre_event_30m": 42_829,
        "same_session_regular": 42_829,
    }
    assert manifest["source_counts"]["selected_rows"] == 6
    assert manifest["source_counts"]["selected_role_counts"] == {
        "pre_event_30m": 3,
        "same_session_regular": 3,
    }
    assert manifest["root_policy"]["feature_materialization_started"] is False
    assert manifest["root_policy"]["official_dataset_created"] is False

    csv_path = Path(manifest["output_csv"])
    json_path = Path(manifest["output_json"])
    assert csv_path.exists()
    assert json_path.exists()
    assert sha256_file(csv_path) == manifest["output_csv_sha256"]
    assert sha256_file(EVENT_WINDOWS) == manifest["source_event_windows_table_sha256"]

    assert len(frame) == 6
    assert set(frame["event_family"]) == {"halt"}
    assert set(frame["source_window_dataset_id"]) == {"event_windows_table_v0_1"}
    assert set(frame["event_source_dataset_id"]) == {"halts_table_v0_1"}
    assert set(frame["window_role"]) == {"pre_event_30m", "same_session_regular"}
    assert set(frame["candidate_dataset_id"]) == {"microstructure_features_table_v0_2_candidate"}
    assert set(frame["candidate_materialization_scope"]) == {"halt_event_windows_microstructure_candidate"}
    assert frame["valid_for_microstructure_feature_candidate"].astype(bool).all()
    assert not frame["candidate_full_universe_claim"].astype(bool).any()
    assert not frame["valid_for_rl_state_component_candidate"].astype(bool).any()

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_candidate_window_manifest_build_check.json",
        {
            "manifest": str(json_path),
            "csv": str(csv_path),
            "source_counts": manifest["source_counts"],
        },
    )


def test_microstructure_candidate_manifest_preserves_leakage_semantics(
    tsis_artifacts_dir: Path,
) -> None:
    manifest, frame = _run_builder(tsis_artifacts_dir / "microstructure_candidate_window_manifest_leakage")

    ml_rows = frame[frame["valid_for_ml_feature_candidate"].astype(bool)]
    assert set(ml_rows["window_role"]) == {"pre_event_30m"}
    assert ml_rows["leakage_safe_as_pre_event_feature"].astype(bool).all()
    assert not ml_rows["contains_post_event_information"].astype(bool).any()

    post_info = frame[frame["contains_post_event_information"].astype(bool)]
    assert not post_info["valid_for_ml_feature_candidate"].astype(bool).any()

    same_session = frame[frame["window_role"].eq("same_session_regular")]
    assert not same_session["valid_for_ml_feature_candidate"].astype(bool).any()

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_candidate_window_manifest_leakage_check.json",
        {
            "manifest": manifest["output_json"],
            "ml_feature_rows": int(len(ml_rows)),
            "post_information_rows": int(len(post_info)),
            "same_session_rows": int(len(same_session)),
        },
    )


def test_microstructure_candidate_manifest_does_not_touch_official_v0_1(
    tsis_artifacts_dir: Path,
) -> None:
    before = sorted(path.relative_to(OFFICIAL_MICROSTRUCTURE_V0_1).as_posix() for path in OFFICIAL_MICROSTRUCTURE_V0_1.rglob("*"))
    _run_builder(tsis_artifacts_dir / "microstructure_candidate_window_manifest_no_official_touch")
    after = sorted(path.relative_to(OFFICIAL_MICROSTRUCTURE_V0_1).as_posix() for path in OFFICIAL_MICROSTRUCTURE_V0_1.rglob("*"))
    assert before == after
    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_candidate_window_manifest_no_official_touch.json",
        {
            "official_v0_1": str(OFFICIAL_MICROSTRUCTURE_V0_1),
            "file_count": len(after),
        },
    )


def test_microstructure_candidate_materializer_writes_candidate_only(
    tsis_artifacts_dir: Path,
) -> None:
    before = sorted(
        path.relative_to(OFFICIAL_MICROSTRUCTURE_V0_1).as_posix()
        for path in OFFICIAL_MICROSTRUCTURE_V0_1.rglob("*")
    )
    manifest, _ = _run_builder(tsis_artifacts_dir / "microstructure_candidate_materializer_manifest")
    output_root = tsis_artifacts_dir / "microstructure_features_table_v0_2_candidate_output"
    result = subprocess.run(
        [
            sys.executable,
            str(MATERIALIZER),
            "--windows-csv",
            manifest["output_csv"],
            "--output-root",
            str(output_root),
            "--dataset-id",
            "microstructure_features_table_v0_2_candidate",
            "--schema-version",
            "microstructure_features_table_v0_2_candidate",
            "--quality-policy-version",
            "microstructure_features_table_policy_v0_2_candidate",
            "--materialization-scope",
            "halt_event_windows_microstructure_candidate",
            "--dataset-dir-name",
            "microstructure_features_table_v0_2_candidate",
            "--summary-name",
            "_microstructure_features_table_summary_v0_2_candidate.csv",
            "--manifest-name",
            "_microstructure_features_table_manifest_v0_2_candidate.json",
            "--overwrite",
        ],
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    candidate_manifest = json.loads(Path(payload["manifest"]).read_text(encoding="utf-8"))
    validations = candidate_manifest["validations"]
    dataset_dir = output_root / "microstructure_features_table_v0_2_candidate"

    assert candidate_manifest["dataset_id"] == "microstructure_features_table_v0_2_candidate"
    assert candidate_manifest["schema_version"] == "microstructure_features_table_v0_2_candidate"
    assert candidate_manifest["quality_policy_version"] == "microstructure_features_table_policy_v0_2_candidate"
    assert candidate_manifest["materialization_scope"] == "halt_event_windows_microstructure_candidate"
    assert candidate_manifest["full_universe_claim"] is False
    assert Path(candidate_manifest["output_path"]) == dataset_dir
    assert validations["row_count"] == 6
    assert validations["quotes_file_present_rows"] == 6
    assert validations["trades_file_present_rows"] == 6
    assert validations["hard_fail_count"] == 0
    assert validations["execution_sim_candidate_rows"] == 0
    assert validations["backtest_core_microstructure_candidate_rows"] == 0
    assert validations["full_universe_claim_rows"] == 0
    assert validations["source_quotes_rows_total"] > 0
    assert validations["source_trades_rows_total"] > 0

    glob = str(dataset_dir / "**" / "*.parquet").replace("\\", "/")
    frame = duckdb.sql(f"select * from read_parquet('{glob}', hive_partitioning=true)").fetchdf()
    assert len(frame) == 6
    assert set(frame["materialization_scope"]) == {"halt_event_windows_microstructure_candidate"}
    assert set(frame["schema_version"]) == {"microstructure_features_table_v0_2_candidate"}
    assert set(frame["quotes_root_state"]) == {"provisional_d_legacy_recovery_root_pending_e_parity"}
    assert set(frame["trades_root_state"]) == {"official_e_raw_root"}
    assert frame["source_quotes_file_present"].all()
    assert frame["source_trades_file_present"].all()
    assert not frame["execution_sim_candidate"].any()
    assert not frame["backtest_core_microstructure_candidate"].any()
    assert not frame["full_universe_claim"].any()

    quote_cache: dict[str, pd.DataFrame] = {}
    trade_cache: dict[str, pd.DataFrame] = {}
    for row in frame.itertuples(index=False):
        quotes_file = Path(row.source_quotes_file)
        trades_file = Path(row.source_trades_file)
        assert quotes_file.exists()
        assert trades_file.exists()
        assert sha256_file(quotes_file) == row.source_quotes_file_sha256
        assert sha256_file(trades_file) == row.source_trades_file_sha256

        start = pd.Timestamp(row.window_start_utc)
        end = pd.Timestamp(row.window_end_utc)

        if str(quotes_file) not in quote_cache:
            quotes = pd.read_parquet(quotes_file)
            quotes["ts_utc"] = pd.to_datetime(quotes["timestamp"], unit="ns", utc=True, errors="coerce")
            quote_cache[str(quotes_file)] = quotes
        quotes_window = quote_cache[str(quotes_file)]
        quotes_window = quotes_window[(quotes_window["ts_utc"] >= start) & (quotes_window["ts_utc"] < end)]
        assert len(quotes_window) == row.quotes_rows

        if str(trades_file) not in trade_cache:
            trades = pd.read_parquet(trades_file)
            trades["ts_utc"] = pd.to_datetime(trades["timestamp"], utc=True, errors="coerce")
            trade_cache[str(trades_file)] = trades
        trades_window = trade_cache[str(trades_file)]
        trades_window = trades_window[(trades_window["ts_utc"] >= start) & (trades_window["ts_utc"] < end)]
        assert len(trades_window) == row.trades_rows

    after = sorted(
        path.relative_to(OFFICIAL_MICROSTRUCTURE_V0_1).as_posix()
        for path in OFFICIAL_MICROSTRUCTURE_V0_1.rglob("*")
    )
    assert before == after

    write_json_artifact(
        tsis_artifacts_dir,
        "microstructure_candidate_materializer_check.json",
        {
            "candidate_manifest": str(payload["manifest"]),
            "candidate_dataset_dir": str(dataset_dir),
            "validations": validations,
        },
    )
