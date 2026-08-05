#!/usr/bin/env python3
"""Validate the State provider-consumer cold-start surface."""
import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
F = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
B = F / "09_STATE_CONSUMPTION_BOUNDARY"
R = B / "runs" / "bounded_state_bundle_read_and_replay_execution_v0_1_20260730T075225Z"

PATHS = [
    ROOT / "README.md", ROOT / "AGENTS.md", Path("G:/TSIS/data/README.md"),
    ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "LOCAL_RULES.md",
    F / "LOCAL_RULES.md", F / "STATE_PROVIDER_CONSUMER_RECOVERY.md",
    F / "AGENT.md", F / "99_ruta_de_trabajo.md", B / "README.md",
    B / "market_state_pit_bt_gate_014_handoff_v0_1.md",
    B / "market_state_core_four_scale_validation_physical_schema_binding_v0_1.json",
    B / "market_state_core_four_scale_validation_physical_schema_binding_readout_v0_1.md",
    B / "bounded_state_bundle_read_and_replay_review_readout_v0_1.md",
    B / "bounded_state_bundle_read_and_replay_review_matrix_v0_1.json",
    B / "event_state_session_opened_replay_availability_contract_v0_1.json",
    B / "event_state_session_opened_bt_gate_015_selection_manifest_v0_1.json",
    B / "event_state_session_opened_bt_gate_015_contract_handoff_v0_1.md",
    B / "event_state_session_opened_bt_gate_015_contract_handoff_matrix_v0_1.json",
    B / "event_state_session_opened_bt_gate_015_contract_handoff_readout_v0_1.md",
    B / "event_state_session_opened_replay_availability_sidecar_authorization_consumption_v0_1.json",
    B / "event_state_session_opened_replay_availability_sidecar_contract_v0_1.json",
    B / "event_state_session_opened_replay_availability_sidecar_manifest_v0_1.json",
    B / "event_state_session_opened_typed_payload_binding_v0_1.json",
    B / "event_state_session_opened_replay_availability_sidecar_matrix_v0_1.json",
    B / "event_state_session_opened_replay_availability_sidecar_readout_v0_1.md",
    B / "event_state_session_opened_bt_gate_015_provider_completion_handoff_v0_1.md",
    R / "final_manifest.json", R / "bounded_replay_report.json",
]
ZIPS = {
    F / "99_archive" / "bounded_state_bundle_read_and_replay_execution_and_review_v0_1_files_20260730T080831Z.zip":
        "8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7",
    F / "99_archive" / "market_state_pit_bt_gate_014_contract_handoff_v0_1_20260730T091041Z.zip":
        "2c578ce9216bb3fd9010ef1f4afe8ba4022ab6b15f665d276a957f50acb35112",
}
MARKERS = {
    F / "STATE_PROVIDER_CONSUMER_RECOVERY.md": [
        "BT-GATE-014 provider evidence handoff = COMPLETE",
        "backtester current-gate authority = 02_TSIS_BACKTEST_ENGINE/AGENTS.md",
        "Event State provider-to-consumer contract handoff = READY_WITH_RESTRICTIONS",
        "BT-GATE-015 non-physical implementation = ACCEPTED_NON_PHYSICAL_ONLY",
        "Event State physical read = NOT_AUTHORIZED",
        "Event State row-addressable available-at evidence = CLOSED_PASS_WITH_RESTRICTIONS",
        "Event State typed payload binding = CLOSED_READY_WITH_RESTRICTIONS",
        "active provider gate = none",
        "Historical Snapshot - Superseded - BT-GATE-014 Next Owner and Work",
        "BT-GATE-015 contract owner review and non-physical external review passed",
    ],
    F / "AGENT.md": ["canonical cold-start entry = STATE_PROVIDER_CONSUMER_RECOVERY.md", "Current Runtime Handoff Override - Event State Provider Completion Ready"],
    F / "99_ruta_de_trabajo.md": ["BT-GATE-015 contract and non-physical external review = PASS", "BT-GATE-015 non-physical implementation = ACCEPTED_NON_PHYSICAL_ONLY"],
    B / "README.md": ["../STATE_PROVIDER_CONSUMER_RECOVERY.md", "typed payload binding = CLOSED_READY_WITH_RESTRICTIONS", "Event State physical consumer read = NOT_AUTHORIZED", "single-use physical authorization = NOT_AUTHORIZED"],
}


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            value.update(chunk)
    return value.hexdigest()


def main():
    errors = [f"missing: {path}" for path in PATHS if not path.is_file()]
    for path, markers in MARKERS.items():
        text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        errors += [f"marker missing: {marker}" for marker in markers if marker not in text]
    recovery_text = (F / "STATE_PROVIDER_CONSUMER_RECOVERY.md").read_text(encoding="utf-8-sig")
    for obsolete in (
        "## Next Owner and Work",
        "Event State handoff was not opened by this provider work",
    ):
        if obsolete in recovery_text:
            errors.append(f"obsolete live recovery statement: {obsolete}")
    for path, expected in ZIPS.items():
        if not path.is_file():
            errors.append(f"ZIP missing: {path}")
        elif digest(path) != expected:
            errors.append(f"ZIP hash mismatch: {path}")
        elif zipfile.ZipFile(path).testzip() is not None:
            errors.append(f"ZIP corrupt: {path}")
    for path in (ROOT / "README.md",):
        text = path.read_text(encoding="utf-8-sig").replace("\\", "/")
        if "E:/TSIS/data" in text:
            errors.append(f"legacy active pointer: {path}")
    print("STATE_PROVIDER_CONSUMER_RECOVERY_VALIDATION=" + ("FAIL" if errors else "PASS"))
    for error in errors:
        print(f"- {error}")
    if not errors:
        print(f"required_paths={len(PATHS)} accepted_zips={len(ZIPS)} failures=0")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
