#!/usr/bin/env python3
"""Package the completed Event State provider handoff without physical data."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TABLES = Path(__file__).resolve().parents[2]
B = TABLES / "09_STATE_CONSUMPTION_BOUNDARY"
RUNTIME_RUN = TABLES / "08_RUNTIME_CAPABILITIES" / "runs" / "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    matrix = json.loads((B / "event_state_session_opened_replay_availability_sidecar_matrix_v0_1.json").read_text(encoding="utf-8"))
    if matrix["failed_cases"] != 0 or matrix["case_count"] < 51:
        raise SystemExit("sidecar/payload validation is below the required case floor or failed")

    sources = [
        B / "configs" / "event_state_session_opened_bt_gate_015_handoff_scope_v0_1.json",
        B / "event_state_session_opened_replay_availability_contract_v0_1.json",
        B / "event_state_session_opened_bt_gate_015_selection_manifest_v0_1.json",
        B / "event_state_session_opened_bt_gate_015_contract_handoff_v0_1.md",
        B / "event_state_session_opened_bt_gate_015_contract_handoff_matrix_v0_1.json",
        B / "event_state_session_opened_bt_gate_015_contract_handoff_readout_v0_1.md",
        B / "scripts" / "event_state_session_opened_bt_gate_015_contract_handoff_runner_v0_1.py",
        B / "configs" / "event_state_session_opened_replay_availability_sidecar_execution_scope_v0_1.json",
        B / "event_state_session_opened_replay_availability_sidecar_authorization_consumption_v0_1.json",
        B / "event_state_session_opened_replay_availability_sidecar_contract_v0_1.json",
        B / "event_state_session_opened_replay_availability_sidecar_manifest_v0_1.json",
        B / "event_state_session_opened_typed_payload_binding_v0_1.json",
        B / "event_state_session_opened_replay_availability_sidecar_matrix_v0_1.json",
        B / "event_state_session_opened_replay_availability_sidecar_readout_v0_1.md",
        B / "event_state_session_opened_bt_gate_015_provider_completion_handoff_v0_1.md",
        B / "scripts" / "event_state_session_opened_replay_availability_sidecar_runner_v0_1.py",
        Path(__file__).resolve(),
        TABLES / "06_MARKET_STATE_INTEGRATION" / "official_profiles" / "market_state_core_four_intraday_profile_v0_1" / "PHYSICAL_SCHEMA_CONTRACT.json",
        TABLES / "07_EVENT_STATE_INTEGRATION" / "official_profiles" / "event_state_core_four_intraday_profile_v0_1" / "EVENT_STATE_SCHEMA_CONTRACT.json",
        B / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json",
        RUNTIME_RUN / "event_instance_manifest.json",
        RUNTIME_RUN / "event_window_binding_manifest.json",
        RUNTIME_RUN / "instrument_session_projection_manifest.json",
        RUNTIME_RUN / "event_state_candidate_output_manifest.json",
        RUNTIME_RUN / "event_state_lineage_manifest.json",
        RUNTIME_RUN / "event_state_validation_report.json",
        RUNTIME_RUN / "final_manifest.json",
        TABLES / "STATE_PROVIDER_CONSUMER_RECOVERY.md",
        TABLES / "AGENT.md",
        TABLES / "99_ruta_de_trabajo.md",
        B / "README.md",
        TABLES / "scripts" / "validate_state_provider_consumer_recovery_v0_1.py",
    ]
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise SystemExit(f"missing package inputs: {missing}")

    artifacts = []
    for path in sources:
        relative = path.relative_to(TABLES).as_posix()
        artifacts.append({"path": relative, "sha256": sha256(path), "size_bytes": path.stat().st_size})
    manifest = {
        "package_id": "event_state_session_opened_bt_gate_015_provider_completion_v0_1",
        "provider_only": True,
        "physical_data_included": False,
        "event_state_candidate_records_included": False,
        "backtester_files_included": False,
        "bt_gate_015_implementation_authorized": False,
        "artifacts": artifacts,
    }
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = TABLES / f"event_state_session_opened_bt_gate_015_provider_completion_v0_1_{timestamp}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("PACKAGE_MANIFEST.json", (json.dumps(manifest, indent=2) + "\n").encode())
        for path in sources:
            archive.write(path, path.relative_to(TABLES).as_posix())
    print(json.dumps({"zip_path": str(output), "zip_sha256": sha256(output), "artifact_count": len(artifacts)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
