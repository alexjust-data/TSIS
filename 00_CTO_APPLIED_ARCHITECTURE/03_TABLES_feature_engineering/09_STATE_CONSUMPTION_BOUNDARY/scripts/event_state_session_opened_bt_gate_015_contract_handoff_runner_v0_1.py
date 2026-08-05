from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


GATE = "event_state_session_opened_bt_gate_015_contract_handoff_v0_1"
HERE = Path(__file__).resolve()
BOUNDARY = HERE.parent.parent
TABLES = BOUNDARY.parent
SELECTION = BOUNDARY / "event_state_session_opened_bt_gate_015_selection_manifest_v0_1.json"
TEMPORAL = BOUNDARY / "event_state_session_opened_replay_availability_contract_v0_1.json"
SCOPE = BOUNDARY / "configs" / "event_state_session_opened_bt_gate_015_handoff_scope_v0_1.json"
HANDOFF = BOUNDARY / "event_state_session_opened_bt_gate_015_contract_handoff_v0_1.md"
MATRIX = BOUNDARY / "event_state_session_opened_bt_gate_015_contract_handoff_matrix_v0_1.json"
READOUT = BOUNDARY / "event_state_session_opened_bt_gate_015_contract_handoff_readout_v0_1.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(rows, case_id, passed, observed):
    rows.append(
        {
            "case_id": case_id,
            "expected": "PASS",
            "observed": observed,
            "status": "PASS" if passed else "FAIL",
        }
    )


def validate(selection: dict, temporal: dict, scope: dict):
    rows = []
    selected = selection["slice"]
    case(rows, "SCOPE_provider_shared_boundary_owner", scope["owner_layer"].endswith("09_STATE_CONSUMPTION_BOUNDARY"), scope["owner_layer"])
    case(rows, "SCOPE_no_physical_read", scope["prohibited_operations"]["read_physical_state_rows"], scope["execution_counters"])
    case(rows, "TYPE_session_opened_only", selected["event_instance_id"] and selection["event_type_id"] == "event_type:market_data:session_opened", selection["event_type_id"])
    case(rows, "TYPE_exchange_session_scope", selection["subject_scope"] == "exchange_session", selection["subject_scope"])
    case(rows, "PROFILE_exact_profile", selection["profile_id"] == "event_state_core_four_intraday_profile_v0_1", selection["profile_id"])
    case(rows, "SLICE_exact_AAME_context", (selected["ticker"], selected["session_date"], selected["exchange_id"]) == ("AAME", "2021-01-19", "XNYS"), selected)
    case(rows, "IDENTITY_event_instance", len(selected["event_instance_id"]) == 64, selected["event_instance_id"])
    case(rows, "IDENTITY_event_window", len(selected["event_window_binding_id"]) == 64, selected["event_window_binding_id"])
    case(rows, "IDENTITY_projection", len(selected["event_state_instrument_session_projection_id"]) == 64, selected["event_state_instrument_session_projection_id"])
    case(rows, "IDENTITY_market_state_record", len(selected["market_state_record_id"]) == 64, selected["market_state_record_id"])
    case(rows, "IDENTITY_market_state_fingerprint", len(selected["market_state_state_output_fingerprint"]) == 64, selected["market_state_state_output_fingerprint"])
    case(rows, "IDENTITY_event_state_record", len(selected["event_state_record_id"]) == 64, selected["event_state_record_id"])
    case(rows, "IDENTITY_event_state_fingerprint", len(selected["event_state_record_fingerprint"]) == 64, selected["event_state_record_fingerprint"])

    for authority in selection["frozen_authorities"]:
        path = TABLES / authority["relative_path"]
        actual = sha256(path) if path.is_file() else "MISSING"
        hash_case_id = "HASH_" + "_".join(path.relative_to(TABLES).parts[-3:]).replace(".", "_")
        case(rows, hash_case_id, actual == authority["sha256"], actual)

    profile = load_json(TABLES / selection["frozen_authorities"][0]["relative_path"])
    registry = load_json(TABLES / selection["frozen_authorities"][2]["relative_path"])
    case(rows, "PROFILE_status_promoted_with_restrictions", profile["status"] == "OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS", profile["status"])
    entries = registry.get("type_entries", [])
    accepted = [x for x in entries if x.get("event_type_id") == selection["event_type_id"]]
    case(rows, "REGISTRY_session_opened_present", len(accepted) == 1, len(accepted))

    execution = TABLES / "07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z"
    with (execution / "event_instance_report.csv").open(encoding="utf-8", newline="") as handle:
        instances = list(csv.DictReader(handle))
    with (execution / "event_window_binding_report.csv").open(encoding="utf-8", newline="") as handle:
        windows = list(csv.DictReader(handle))
    with (execution / "instrument_session_projection_report.csv").open(encoding="utf-8", newline="") as handle:
        projections = list(csv.DictReader(handle))
    with (execution / "market_state_binding_report.csv").open(encoding="utf-8", newline="") as handle:
        dependencies = list(csv.DictReader(handle))
    physical = TABLES / "07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z"
    with (physical / "record_fingerprint_validation_report.csv").open(encoding="utf-8", newline="") as handle:
        fingerprints = list(csv.DictReader(handle))
    case(rows, "BIND_event_instance_exact", any(x["event_instance_id"] == selected["event_instance_id"] for x in instances), selected["event_instance_id"])
    case(rows, "BIND_event_window_exact", any(x["event_window_binding_id"] == selected["event_window_binding_id"] for x in windows), selected["event_window_binding_id"])
    case(rows, "BIND_projection_exact", any(x["event_state_instrument_session_projection_id"] == selected["event_state_instrument_session_projection_id"] and x["ticker"] == "AAME" for x in projections), selected["event_state_instrument_session_projection_id"])
    case(rows, "BIND_market_state_exact", any(x["event_state_instrument_session_projection_id"] == selected["event_state_instrument_session_projection_id"] and x["market_state_record_id"] == selected["market_state_record_id"] and x["state_output_fingerprint"] == selected["market_state_state_output_fingerprint"] for x in dependencies), selected["market_state_record_id"])
    record = next((x for x in fingerprints if int(x["record_ordinal"]) == selected["event_state_record_ordinal"]), None)
    case(rows, "BIND_event_state_record_exact", bool(record) and record["event_state_record_id"] == selected["event_state_record_id"] and record["observed_event_state_record_fingerprint"] == selected["event_state_record_fingerprint"] and record["fingerprint_status"] == "PASS", record or "MISSING")

    status = temporal["current_evidence_status"]
    case(rows, "TEMPORAL_available_at_not_overclaimed", status["event_state_available_at_utc"] == "NOT_YET_PROVEN", status)
    case(rows, "TEMPORAL_sidecar_absent_visible", status["row_addressable_replay_availability_sidecar"] == "ABSENT", status)
    case(rows, "TEMPORAL_delivery_uses_available_at", "event_loop.clock >= event_state_available_at_utc" == temporal["required_formula"]["delivery_eligibility"], temporal["required_formula"])
    case(rows, "BOUNDARY_no_consumer_authority", not any(temporal["authorization"].values()), temporal["authorization"])

    mutation = deepcopy(selection)
    mutation["slice"]["event_instance_id"] = "0" * 64
    case(rows, "NEG_mutated_event_instance_rejected", not any(x["event_instance_id"] == mutation["slice"]["event_instance_id"] for x in instances), mutation["slice"]["event_instance_id"])
    mutation = deepcopy(selection)
    mutation["slice"]["market_state_state_output_fingerprint"] = "0" * 64
    case(rows, "NEG_mutated_market_state_fingerprint_rejected", not any(x["state_output_fingerprint"] == mutation["slice"]["market_state_state_output_fingerprint"] for x in dependencies), mutation["slice"]["market_state_state_output_fingerprint"])
    mutation = deepcopy(selection)
    mutation["slice"]["event_state_record_fingerprint"] = "0" * 64
    case(rows, "NEG_mutated_event_state_fingerprint_rejected", not any(x["observed_event_state_record_fingerprint"] == mutation["slice"]["event_state_record_fingerprint"] for x in fingerprints), mutation["slice"]["event_state_record_fingerprint"])
    case(rows, "NEG_anchor_alone_does_not_authorize_delivery", status["event_state_available_at_utc"] != "PROVEN", selected["event_anchor_timestamp_utc"])
    return rows


def write_outputs(rows):
    failed = [row for row in rows if row["status"] != "PASS"]
    matrix = {
        "gate": GATE,
        "case_count": len(rows),
        "failed_cases": len(failed),
        "physical_files_opened": 0,
        "physical_rows_read": 0,
        "event_state_records_delivered": 0,
        "bt_gate_015_implementation_authorized": False,
        "cases": rows,
    }
    MATRIX.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    status = (
        "CLOSED_CONTRACT_HANDOFF_READY_WITH_RESTRICTIONS_REQUIRES_REPLAY_AVAILABILITY_EVIDENCE"
        if not failed
        else "FAILED_VALIDATION"
    )
    READOUT.write_text(
        "\n".join(
            [
                "# Event State `session_opened` BT-GATE-015 Handoff Readout v0.1",
                "",
                "```text",
                f"{GATE} =",
                status,
                f"case_count = {len(rows)}",
                f"failed_cases = {len(failed)}",
                "physical_files_opened = 0",
                "physical_rows_read = 0",
                "event_state_records_delivered = 0",
                "BT_GATE_015_CONTRACT_DRAFTING = READY",
                "BT_GATE_015_IMPLEMENTATION = NOT_AUTHORIZED",
                "EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED",
                "```",
                "",
                "The exact `session_opened/AAME/2021-01-19` identity chain is",
                "frozen. Delivery remains blocked until row-addressable",
                "`event_state_available_at_utc` evidence is produced.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    return matrix, status


def package(timestamp: str):
    sources = [
        SCOPE,
        TEMPORAL,
        SELECTION,
        HANDOFF,
        MATRIX,
        READOUT,
        HERE,
        TABLES / "STATE_PROVIDER_CONSUMER_RECOVERY.md",
        TABLES / "AGENT.md",
        TABLES / "99_ruta_de_trabajo.md",
        BOUNDARY / "README.md",
        TABLES / "scripts" / "validate_state_provider_consumer_recovery_v0_1.py",
    ]
    selection = load_json(SELECTION)
    sources.extend(TABLES / item["relative_path"] for item in selection["frozen_authorities"])
    package_manifest = {
        "package_id": "event_state_session_opened_bt_gate_015_contract_handoff_v0_1",
        "provider_only": True,
        "physical_data_included": False,
        "backtester_files_included": False,
        "artifacts": [],
    }
    for path in sources:
        relative = path.relative_to(TABLES).as_posix()
        package_manifest["artifacts"].append(
            {
                "path": relative,
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest_bytes = (json.dumps(package_manifest, indent=2) + "\n").encode()
    zip_path = TABLES / f"event_state_session_opened_bt_gate_015_contract_handoff_v0_1_{timestamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("PACKAGE_MANIFEST.json", manifest_bytes)
        for path in sources:
            archive.write(path, path.relative_to(TABLES).as_posix())
    return zip_path


def main():
    selection = load_json(SELECTION)
    temporal = load_json(TEMPORAL)
    scope = load_json(SCOPE)
    rows = validate(selection, temporal, scope)
    matrix, status = write_outputs(rows)
    if matrix["failed_cases"]:
        print(json.dumps(matrix, indent=2))
        return 1
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    zip_path = package(timestamp)
    print(
        json.dumps(
            {
                "status": status,
                "case_count": matrix["case_count"],
                "failed_cases": 0,
                "zip_path": str(zip_path),
                "zip_sha256": sha256(zip_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
