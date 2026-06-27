from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _helpers.data_foundation import write_json_artifact


MODULE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = MODULE_ROOT.parent
ROOT_FIXTURE_DIR = (
    REPO_ROOT / "tests/fixtures/data_foundation_outputs/market_event_state_v0_1"
)
CONFIG_PATH = (
    MODULE_ROOT
    / "configs/data_foundation_outputs/event_state_builder_fixture_v0_1.json"
)

CONTRACT_PATHS = {
    "composition_contract": MODULE_ROOT
    / "01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "build_loop_runbook": MODULE_ROOT
    / "01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "schema": MODULE_ROOT
    / "01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md",
    "dataset_contract": MODULE_ROOT
    / "01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md",
    "consumption_policy": MODULE_ROOT
    / "01_foundations/data_consumption_policies/event_state_table_consumption_policy.md",
    "registry_entry": MODULE_ROOT
    / "01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml",
    "validators": MODULE_ROOT
    / "01_foundations/validators/outputs/event_state_table_validators.md",
    "builder": MODULE_ROOT / "scripts/materialize_event_state_table.py",
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

ALLOWED_ROLES = ["pre_event", "at_event", "post_event_review", "research_replay"]


def test_event_state_contract_stack_exists(tsis_artifacts_dir: Path) -> None:
    missing = [name for name, path in CONTRACT_PATHS.items() if not path.exists()]
    assert missing == []
    write_json_artifact(
        tsis_artifacts_dir,
        "event_state_contract_stack.json",
        {name: str(path) for name, path in CONTRACT_PATHS.items()},
    )


def test_event_state_schema_blocks_inline_labels_rewards() -> None:
    schema = CONTRACT_PATHS["schema"].read_text(encoding="utf-8")
    policy = CONTRACT_PATHS["consumption_policy"].read_text(encoding="utf-8")

    assert "event_state_table_v0_1 materialized = false" in schema
    assert "outcome_values_inline_allowed = false" in schema
    assert "label_columns_inline_allowed = false" in schema
    assert "reward_columns_inline_allowed = false" in schema
    assert "post_event_review rows are forensic/research" in policy
    for family in PROHIBITED_FAMILIES:
        assert family in schema
    for role in ALLOWED_ROLES:
        assert role in schema


def test_event_state_registry_declares_not_materialized() -> None:
    registry = CONTRACT_PATHS["registry_entry"].read_text(encoding="utf-8")
    assert "status: contract_defined_not_materialized" in registry
    assert "official_manifest_exists: false" in registry
    assert "official_dataset_exists: false" in registry
    assert "direct_rl_training_allowed: false" in registry
    assert "execution_truth: false" in registry


def test_event_state_builder_skeleton_contract_check(tsis_artifacts_dir: Path) -> None:
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
    assert payload["dataset_id"] == "event_state_table_v0_1"
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

    write_json_artifact(tsis_artifacts_dir, "event_state_builder_contract_check.json", payload)


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
    path = tsis_artifacts_dir / f"event_state_{fixture_name}.config.json"
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def test_event_state_builder_fixture_sample(tsis_artifacts_dir: Path) -> None:
    output_dir = tsis_artifacts_dir / "event_state_fixture_builder"
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
    assert manifest["dataset_id"] == "event_state_table_v0_1"
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
    assert rows[0]["event_state_id"].startswith("event_state_fixture_")
    assert rows[0]["state_role"] == "pre_event"
    assert rows[0]["full_universe_claim"] is False
    assert rows[0]["label_columns_inline_allowed"] is False

    write_json_artifact(
        tsis_artifacts_dir,
        "event_state_fixture_builder_manifest.json",
        manifest,
    )


def test_event_state_builder_rejects_inline_label(tsis_artifacts_dir: Path) -> None:
    config_path = _config_with_fixture(
        tsis_artifacts_dir,
        "event_state_events_inline_label_bad_v0_1.json",
        "bad_inline_label.jsonl",
        "bad_inline_label_manifest.json",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--config",
            str(config_path),
            "--output-dir",
            str(tsis_artifacts_dir / "event_state_bad_inline_label"),
        ],
        cwd=MODULE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "prohibited state feature family detected" in result.stderr
    assert "label__future_winner" in result.stderr


def test_event_state_builder_rejects_post_event_review_as_ml_feature(
    tsis_artifacts_dir: Path,
) -> None:
    config_path = _config_with_fixture(
        tsis_artifacts_dir,
        "event_state_events_post_review_bad_ml_v0_1.json",
        "bad_post_review_ml.jsonl",
        "bad_post_review_ml_manifest.json",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_PATHS["builder"]),
            "--config",
            str(config_path),
            "--output-dir",
            str(tsis_artifacts_dir / "event_state_bad_post_review_ml"),
        ],
        cwd=MODULE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "post_event/replay rows cannot be valid_for_ml_feature_candidate" in result.stderr
