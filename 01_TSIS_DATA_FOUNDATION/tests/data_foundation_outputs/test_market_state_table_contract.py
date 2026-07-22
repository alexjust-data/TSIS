from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from _helpers.data_foundation import write_json_artifact


MODULE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = MODULE_ROOT.parent
ROOT_FIXTURE_DIR = (
    REPO_ROOT / "tests/fixtures/data_foundation_outputs/market_event_state_v0_1"
)
CONFIG_PATH = (
    MODULE_ROOT
    / "configs/data_foundation_outputs/market_state_builder_fixture_v0_1.json"
)

CONTRACT_PATHS = {
    "composition_contract": MODULE_ROOT
    / "01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "build_loop_runbook": MODULE_ROOT
    / "01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "schema": MODULE_ROOT
    / "01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md",
    "dataset_contract": MODULE_ROOT
    / "01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md",
    "consumption_policy": MODULE_ROOT
    / "01_foundations/data_consumption_policies/market_state_table_consumption_policy.md",
    "registry_entry": MODULE_ROOT
    / "01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml",
    "validators": MODULE_ROOT
    / "01_foundations/validators/outputs/market_state_table_validators.md",
    "builder": MODULE_ROOT / "scripts/materialize_market_state_table.py",
}

PROHIBITED_FAMILIES = [
    "outcome__*",
    "label__*",
    "reward__*",
    "action__*",
    "policy__*",
    "fill__*",
    "pnl__*",
    "future__*",
    "strategy__*",
    "signal__*",
]

REQUIRED_NAMESPACES = [
    "identity__",
    "calendar__",
    "daily__",
    "intraday__",
    "microstructure__",
    "halt__",
    "fundamentals__",
    "news__",
    "short_context__",
    "short_constraints__",
    "regime__",
    "quality__",
]


def test_market_state_contract_stack_exists(tsis_artifacts_dir: Path) -> None:
    missing = [name for name, path in CONTRACT_PATHS.items() if not path.exists()]
    assert missing == []
    write_json_artifact(
        tsis_artifacts_dir,
        "market_state_contract_stack.json",
        {name: str(path) for name, path in CONTRACT_PATHS.items()},
    )


def test_market_state_schema_blocks_labels_rewards_and_unscoped_features() -> None:
    schema = CONTRACT_PATHS["schema"].read_text(encoding="utf-8")
    composition = CONTRACT_PATHS["composition_contract"].read_text(encoding="utf-8")

    assert "market_state_table_v0_1 materialized = false" in schema
    assert "component_as_of_utc <= decision_timestamp_utc" in schema
    assert "state != signal" in composition
    for family in PROHIBITED_FAMILIES:
        assert family in schema
    for namespace in REQUIRED_NAMESPACES:
        assert namespace in schema


def test_market_state_registry_declares_not_materialized() -> None:
    registry = CONTRACT_PATHS["registry_entry"].read_text(encoding="utf-8")
    assert "status: contract_defined_not_materialized" in registry
    assert "official_manifest_exists: false" in registry
    assert "official_dataset_exists: false" in registry
    assert "direct_rl_training_allowed: false" in registry
    assert "execution_truth: false" in registry


def test_market_state_builder_skeleton_contract_check(tsis_artifacts_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--contract-check-only",
        ],
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["dataset_id"] == "market_state_table_v0_1"
    assert payload["status"] == "contract_defined_not_materialized"
    assert payload["materialized"] is False
    assert payload["builder_implemented"] is False
    assert payload["official_builder_implemented"] is False
    assert payload["fixture_builder_implemented"] is True
    assert payload["writes_output"] is False
    assert payload["official_output_writes"] is False
    assert payload["missing_contracts"] == []

    blocked = subprocess.run(
        [sys.executable, str(CONTRACT_PATHS["builder"])],
        cwd=MODULE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert blocked.returncode != 0
    assert "not materialized" in blocked.stderr or "not materialized" in blocked.stdout

    write_json_artifact(tsis_artifacts_dir, "market_state_builder_contract_check.json", payload)


def _config_with_fixture(
    tsis_artifacts_dir: Path,
    fixture_name: str,
    output_file: str,
    manifest_file: str,
) -> Path:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["input_fixture"] = str(ROOT_FIXTURE_DIR / fixture_name)
    config["output_file"] = output_file
    config["manifest_file"] = manifest_file
    path = tsis_artifacts_dir / f"market_state_{fixture_name}.config.json"
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def test_market_state_builder_fixture_sample(tsis_artifacts_dir: Path) -> None:
    output_dir = tsis_artifacts_dir / "market_state_fixture_builder"
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--config",
            str(CONFIG_PATH),
            "--output-dir",
            str(output_dir),
        ],
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = json.loads(result.stdout)
    assert manifest["dataset_id"] == "market_state_table_v0_1"
    assert manifest["status"] == "deterministic_fixture_sample_only"
    assert manifest["official_output_allowed"] is False
    assert manifest["official_output_materialized"] is False
    assert manifest["sample_output_written"] is True
    assert manifest["full_universe_claim"] is False
    assert manifest["rows"] == 1

    output_file = Path(manifest["output_file"])
    manifest_file = Path(manifest["manifest_file"])
    assert output_file.exists()
    assert manifest_file.exists()
    rows = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["market_state_id"].startswith("market_state_fixture_")
    assert rows[0]["full_universe_claim"] is False
    assert rows[0]["valid_for_rl_training_direct"] is False

    write_json_artifact(
        tsis_artifacts_dir,
        "market_state_fixture_builder_manifest.json",
        manifest,
    )


def test_market_state_builder_rejects_future_asof(tsis_artifacts_dir: Path) -> None:
    config_path = _config_with_fixture(
        tsis_artifacts_dir,
        "market_state_components_future_asof_bad_v0_1.json",
        "bad_future_asof.jsonl",
        "bad_future_asof_manifest.json",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--config",
            str(config_path),
            "--output-dir",
            str(tsis_artifacts_dir / "market_state_bad_future_asof"),
        ],
        cwd=MODULE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "regime_as_of_utc" in result.stderr
    assert "<= decision_timestamp_utc" in result.stderr


def test_market_state_builder_rejects_prohibited_feature(
    tsis_artifacts_dir: Path,
) -> None:
    config_path = _config_with_fixture(
        tsis_artifacts_dir,
        "market_state_components_prohibited_feature_bad_v0_1.json",
        "bad_prohibited_feature.jsonl",
        "bad_prohibited_feature_manifest.json",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--config",
            str(config_path),
            "--output-dir",
            str(tsis_artifacts_dir / "market_state_bad_prohibited_feature"),
        ],
        cwd=MODULE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "prohibited state feature family detected" in result.stderr
    assert "label__future_return" in result.stderr


def test_market_state_candidate_materializes_from_microstructure(
    tsis_artifacts_dir: Path,
) -> None:
    output_root = tsis_artifacts_dir / "market_state_candidate_from_microstructure"
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--materialize-candidate",
            "--candidate-output-root",
            str(output_root),
            "--overwrite",
        ],
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    manifest = json.loads(Path(payload["manifest"]).read_text(encoding="utf-8"))
    frame = pd.read_parquet(payload["output"])

    assert manifest["dataset_id"] == "market_state_table_v0_1_candidate"
    assert manifest["status"] == "controlled_candidate_not_promoted"
    assert manifest["full_universe_claim"] is False
    assert manifest["source_root_states"]["quotes_root_state"] == (
        "provisional_d_legacy_recovery_root_pending_e_parity"
    )
    assert manifest["source_root_states"]["requires_rebuild_after_e_quotes_parity"] is True
    assert len(frame) == 50
    assert frame["ticker"].nunique() == 9
    assert frame["market_state_id"].is_unique
    assert set(frame["state_quality_state"]) == {"state_review_microstructure_seed_only"}
    assert frame["valid_for_event_context_candidate"].all()
    assert not frame["valid_for_ml_feature_candidate"].any()
    assert not frame["valid_for_rl_state_candidate"].any()
    assert not frame["valid_for_rl_training_direct"].any()
    assert not frame["valid_for_execution_simulator_direct"].any()
    assert not frame["full_universe_claim"].any()
    assert not frame["execution_truth"].any()

    prohibited_prefixes = (
        "outcome__",
        "label__",
        "reward__",
        "action__",
        "policy__",
        "fill__",
        "pnl__",
        "future__",
        "strategy__",
        "signal__",
    )
    assert not any(column.startswith(prohibited_prefixes) for column in frame.columns)

    decision_ts = pd.to_datetime(frame["decision_timestamp_utc"], utc=True)
    for column in [c for c in frame.columns if c.endswith("_as_of_utc")]:
        values = pd.to_datetime(frame[column], utc=True, errors="coerce")
        assert not (values.notna() & (values > decision_ts)).any(), column

    write_json_artifact(
        tsis_artifacts_dir,
        "market_state_candidate_materialization_check.json",
        {
            "manifest": payload["manifest"],
            "output": payload["output"],
            "validations": manifest["validations"],
        },
    )
