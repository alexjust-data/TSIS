from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

TSIS_ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = TSIS_ROOT / "02_TSIS_BACKTEST_ENGINE"
GOV_ROOT = TSIS_ROOT / "00_CTO/14_BACKTEST_ENGINE"
BASE_PACKET = ENGINE_ROOT / "deliverables/bt_gate_015_non_physical_acceptance_packet_r3_20260731T115617Z.zip"
SPEC_PATH = ENGINE_ROOT / "configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_4_spec.json"
RUN_ID = "bt_gate_015_single_use_physical_event_state_consumer_v0_4"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_nested_handoff(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as archive:
        names = [info.filename for info in archive.infolist()]
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise RuntimeError(f"invalid nested handoff: {path}")
        for info in archive.infolist():
            member = PurePosixPath(info.filename.replace("\\", "/"))
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError(f"unsafe nested path: {path}: {info.filename}")
            if stat.S_ISLNK(info.external_attr >> 16):
                raise RuntimeError(f"nested symlink: {path}: {info.filename}")
            if member.suffix.lower() in {".jsonl", ".parquet"}:
                raise RuntimeError(f"physical state inside handoff: {path}: {info.filename}")


def main() -> int:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    governance_manifest = json.loads(
        (GOV_ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8")
    )
    with zipfile.ZipFile(BASE_PACKET, "r") as archive:
        base_manifest = json.loads(archive.read("ZIP_MANIFEST.json"))

    paths = set(base_manifest["declared_files"])
    paths.update(governance_manifest["files"])
    paths.add("00_CTO/14_BACKTEST_ENGINE/PACKAGE_MANIFEST.json")
    paths.update(
        {
            "02_TSIS_BACKTEST_ENGINE/RUN_BT_GATE_015_PHYSICAL_V0_4.py",
            "02_TSIS_BACKTEST_ENGINE/RUN_BT_GATE_015_V0_4_PREEXECUTION_TESTS.py",
            "02_TSIS_BACKTEST_ENGINE/RUN_FULL_REPOSITORY_TESTS.py",
            "02_TSIS_BACKTEST_ENGINE/GRAPHIFY_REFRESH_QUEUE.md",
            "02_TSIS_BACKTEST_ENGINE/configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_4.json",
            "02_TSIS_BACKTEST_ENGINE/configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_4_spec.json",
            "02_TSIS_BACKTEST_ENGINE/configs/runs/bt_gate_015_single_use_physical_event_state_consumer_v0_4.json",
            "02_TSIS_BACKTEST_ENGINE/configs/fixtures/BT_GATE_015_PHYSICAL_INTEGRATION_BARRIERS_V0_4.json",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/20_BT_GATE_015_POINT_IN_TIME_EVENT_STATE_CONSUMER_CONTRACT_V0_1.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/28_BT_GATE_015_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_4.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/29_BT_GATE_015_V0_4_PREEXECUTION_REVIEW_REQUEST.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/30_BT_GATE_015_V0_4_PREEXECUTION_PACKET_READOUT.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/26_BT_GATE_015_V0_3_CONSUMED_FAILURE_READOUT.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/27_BT_GATE_015_V0_3_POSTEXECUTION_EXTERNAL_REVIEW.md",
            "02_TSIS_BACKTEST_ENGINE/configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_3.json",
            "02_TSIS_BACKTEST_ENGINE/runs/bt_gate_015_single_use_physical_event_state_consumer_v0_3/authorization_consumption_receipt.json",
            "02_TSIS_BACKTEST_ENGINE/runs/bt_gate_015_single_use_physical_event_state_consumer_v0_3/failure_manifest.json",
            "02_TSIS_BACKTEST_ENGINE/runs/bt_gate_015_single_use_physical_event_state_consumer_v0_3/physical_progress.json",
            "02_TSIS_BACKTEST_ENGINE/scripts/materialize_bt_gate_015_v0_4_preexecution.py",
            "02_TSIS_BACKTEST_ENGINE/scripts/package_bt_gate_015_v0_4_preexecution.py",
            "02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/event_state/physical_authorization_v0_4.py",
            "02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/event_state/physical_consumer_v0_4.py",
            "02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/event_state/physical_runner_v0_4.py",
            "02_TSIS_BACKTEST_ENGINE/tests/unit/test_bt_gate_015_single_use_physical_v0_4.py",
        }
    )
    candidate_relative = spec["governed_inputs"]["candidate_jsonl"]["relative_path"]
    for name, binding in spec["governed_inputs"].items():
        if name != "candidate_jsonl":
            paths.add(binding["relative_path"])
    if candidate_relative in paths:
        raise RuntimeError("physical Event State candidate must not be packaged")
    if (ENGINE_ROOT / "runs" / RUN_ID).exists():
        raise RuntimeError("V0.4 physical run directory must be absent")

    files: dict[str, dict[str, object]] = {}
    provider_handoff_count = 0
    market_bar_parquets = 0
    for relative in sorted(paths):
        path = TSIS_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        normalized = relative.replace("\\", "/")
        if normalized == candidate_relative or normalized.endswith("event_state_candidate_records.jsonl"):
            raise RuntimeError(f"physical Event State candidate prohibited: {relative}")
        if f"/runs/{RUN_ID}/" in f"/{normalized}/":
            raise RuntimeError(f"physical V0.4 run evidence prohibited: {relative}")
        if path.suffix.lower() == ".parquet":
            if "02_TSIS_BACKTEST_ENGINE/tests/fixtures/" not in normalized:
                raise RuntimeError(f"non-fixture Parquet prohibited: {relative}")
            market_bar_parquets += 1
        if relative in {
            spec["governed_inputs"]["initial_provider_handoff"]["relative_path"],
            spec["governed_inputs"]["provider_completion_handoff"]["relative_path"],
        }:
            validate_nested_handoff(path)
            provider_handoff_count += 1
        files[normalized] = {
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
        }

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ENGINE_ROOT / "deliverables" / (
        f"bt_gate_015_single_use_physical_preexecution_packet_v0_4_corrected_r1_{stamp}.zip"
    )
    manifest = {
        "package_id": "BT_GATE_015_SINGLE_USE_PHYSICAL_PREEXECUTION_PACKET_V0_4",
        "status": "PENDING_EXTERNAL_PREEXECUTION_REVIEW",
        "bt_gate_015": "NON_PHYSICAL_IMPLEMENTATION_ACCEPTED_PENDING_V0_4_PREEXECUTION_EXTERNAL_REVIEW",
        "implementation_acceptance": "ACCEPTED_NON_PHYSICAL_ONLY",
        "authorization_id": spec["authorization_id"],
        "authorization_status": "AUTHORIZED_NOT_CONSUMED",
        "physical_command_execution": "NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW",
        "event_state_physical_read": "NOT_EXECUTED",
        "physical_state_records_scanned": 0,
        "physical_state_rows_selected": 0,
        "focused_suite": "24/24 PASS",
        "full_repository_suite": "280/280 PASS",
        "governance_validation": f"PASS / {len(governance_manifest['files'])} hashes",
        "governed_input_count": 11,
        "metadata_inputs_included": 10,
        "physical_candidate_included": False,
        "provider_handoffs_included_and_crc_valid": provider_handoff_count,
        "market_bar_fixture_parquets": market_bar_parquets,
        "provider_event_state_parquets": 0,
        "provider_event_state_jsonl": 0,
        "executable_binding_count": spec["executable_binding_count"],
        "physical_binding_correction": "CORRECTED_R1_PENDING_EXTERNAL_PREEXECUTION_REVIEW",
        "bt_gate_015_closed_pass": "NOT_AUTHORIZED",
        "declared_file_count": len(files),
        "declared_files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for relative in sorted(files):
            archive.write(TSIS_ROOT / relative, relative)
        archive.writestr(
            "ZIP_MANIFEST.json",
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        )
    print(
        json.dumps(
            {
                "zip_path": str(output),
                "zip_sha256": sha256(output),
                "zip_entries": len(files) + 1,
                "manifest_declared_files": len(files),
                "provider_event_state_jsonl": 0,
                "authorization_status": "AUTHORIZED_NOT_CONSUMED",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
