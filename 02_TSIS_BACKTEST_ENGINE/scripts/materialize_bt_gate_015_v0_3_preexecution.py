"""Derive the BT-GATE-015 V0.3 config and state from one semantic spec."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
TSIS_ROOT = ENGINE_ROOT.parent
SPEC = (
    ENGINE_ROOT
    / "configs/authorizations/"
    "bt_gate_015_single_use_physical_event_state_consumer_v0_3_spec.json"
)
CONFIG = (
    ENGINE_ROOT
    / "configs/runs/"
    "bt_gate_015_single_use_physical_event_state_consumer_v0_3.json"
)
STATE = (
    ENGINE_ROOT
    / "configs/authorizations/"
    "bt_gate_015_single_use_physical_event_state_consumer_v0_3.json"
)
AUTH_DOCUMENT = (
    ENGINE_ROOT
    / "docs/00_system/"
    "23_BT_GATE_015_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_3.md"
)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec["status"] != "AUTHORIZED_NOT_CONSUMED":
        raise SystemExit("V0.3 semantic spec is not intact")
    if spec["physical_command_status"] != (
        "NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW"
    ):
        raise SystemExit("physical command status is not fail-closed")
    if len(spec["governed_inputs"]) != 11:
        raise SystemExit("unexpected governed input count")
    specification_sha256 = sha256(SPEC)
    config = {
        "authorization_id": spec["authorization_id"],
        "barrier_fixture_relative_path": "02_TSIS_BACKTEST_ENGINE/configs/fixtures/BT_GATE_015_PHYSICAL_INTEGRATION_BARRIERS_V0_3.json",
        "boundaries": spec["boundaries"],
        "contract_id": spec["contract_id"],
        "event_state_scope": spec["event_state_scope"],
        "expected_outputs": spec["expected_outputs"],
        "gate_id": "BT-GATE-015",
        "governed_inputs": spec["governed_inputs"],
        "physical_command_status": spec["physical_command_status"],
        "run_directory_relative_path": (
            "02_TSIS_BACKTEST_ENGINE/runs/" + spec["run_id"]
        ),
        "run_id": spec["run_id"],
        "specification_relative_path": str(SPEC.relative_to(TSIS_ROOT)).replace(
            "\\", "/"
        ),
        "specification_sha256": specification_sha256,
    }
    write_json(CONFIG, config)
    binding_paths = spec.get("executable_binding_paths")
    if (
        not isinstance(binding_paths, list)
        or not binding_paths
        or len(binding_paths) != len(set(binding_paths))
        or spec.get("executable_binding_count") != len(binding_paths)
        or binding_paths != sorted(binding_paths)
    ):
        raise SystemExit("invalid exact executable binding set")
    binding_hashes = {}
    for relative in binding_paths:
        path = TSIS_ROOT / relative
        if not path.is_file():
            raise SystemExit(f"missing executable binding: {relative}")
        binding_hashes[relative] = sha256(path)
    state = {
        "authorization_id": spec["authorization_id"],
        "authorization_consumption_count": 0,
        "authorization_document_sha256": sha256(AUTH_DOCUMENT),
        "authorization_version": spec["authorization_version"],
        "binding_sha256": binding_hashes,
        "configuration_sha256": sha256(CONFIG),
        "consumed_by_run_id": None,
        "event_state_physical_read": "NOT_EXECUTED",
        "physical_command_status": spec["physical_command_status"],
        "physical_state_records_scanned": 0,
        "physical_state_rows_selected": 0,
        "preexecution_review_status": "NOT_EXECUTED",
        "run_id": spec["run_id"],
        "single_use": True,
        "specification_sha256": specification_sha256,
        "status": "AUTHORIZED_NOT_CONSUMED",
    }
    write_json(STATE, state)
    run_directory = ENGINE_ROOT / "runs" / spec["run_id"]
    if run_directory.exists():
        raise SystemExit(f"physical run directory must be absent: {run_directory}")
    print(f"SPECIFICATION_SHA256={specification_sha256}")
    print(f"CONFIGURATION_SHA256={sha256(CONFIG)}")
    print(f"AUTHORIZATION_STATE_SHA256={sha256(STATE)}")
    print(f"EXECUTABLE_BINDINGS={len(binding_hashes)}")
    print("PHYSICAL_EVENT_STATE_READ=NOT_EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
