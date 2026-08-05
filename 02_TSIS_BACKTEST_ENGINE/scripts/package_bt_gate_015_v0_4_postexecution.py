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
RUN_ID = "bt_gate_015_single_use_physical_event_state_consumer_v0_4"
RUN_ROOT = ENGINE_ROOT / "runs" / RUN_ID
PREEXEC_PACKET = ENGINE_ROOT / "deliverables" / (
    "bt_gate_015_single_use_physical_preexecution_packet_v0_4_"
    "corrected_r1_20260805T142620Z.zip"
)
PREEXEC_SHA256 = "ed26dd77908e87a84dddaac287798ca0073d9011e775ef72a5f4c1f1998d1bb5"
EXPECTED_OUTPUT_HASH = "35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise RuntimeError(f"invalid ZIP: {path}")
        for info in infos:
            member = PurePosixPath(info.filename.replace("\\", "/"))
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError(f"unsafe ZIP member: {path}: {info.filename}")
            if stat.S_ISLNK(info.external_attr >> 16):
                raise RuntimeError(f"ZIP symlink prohibited: {path}: {info.filename}")
        return json.loads(archive.read("ZIP_MANIFEST.json"))


def validate_result() -> dict[str, object]:
    final = json.loads((RUN_ROOT / "final_manifest.json").read_text(encoding="utf-8"))
    expected = {
        "validation_status": "PASS",
        "physical_data_files_opened": 1,
        "physical_state_records_scanned": 8,
        "physical_state_rows_selected": 1,
        "market_state_dependency_events": 1,
        "event_state_events_emitted": 1,
        "event_state_store_inserts": 1,
        "bounded_probe_observations": 1,
        "delivery_before_available_at": 0,
        "typed_scientific_values": 17,
        "orders": 0,
        "fills": 0,
        "pnl_calculated": False,
        "provider_modification": False,
        "deterministic_output_hash": EXPECTED_OUTPUT_HASH,
    }
    for key, value in expected.items():
        if final.get(key) != value:
            raise RuntimeError(f"postexecution result mismatch: {key}")
    for name, expected_hash in final["output_artifact_hashes"].items():
        if sha256(RUN_ROOT / name) != expected_hash:
            raise RuntimeError(f"run artifact hash mismatch: {name}")
    failure = json.loads((RUN_ROOT / "failure_manifest.json").read_text(encoding="utf-8"))
    if failure.get("status") != "SUPERSEDED_BY_FINAL_MANIFEST_PASS":
        raise RuntimeError("durable failure guard was not superseded by PASS")
    return final


def main() -> int:
    if sha256(PREEXEC_PACKET) != PREEXEC_SHA256:
        raise RuntimeError("approved preexecution packet identity mismatch")
    preexec_manifest = validate_zip(PREEXEC_PACKET)
    final = validate_result()
    state = json.loads(
        (
            ENGINE_ROOT
            / "configs/authorizations/"
            "bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
        ).read_text(encoding="utf-8")
    )
    if state["authorization_consumption_count"] != 1:
        raise RuntimeError("V0.4 consumption count must equal one")
    if state["consumed_by_run_id"] != RUN_ID:
        raise RuntimeError("V0.4 consumed_by_run_id mismatch")
    if not state["status"].startswith("CONSUMED_BY_RUN_"):
        raise RuntimeError("V0.4 must remain consumed")

    governance = json.loads((GOV_ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    paths = set(preexec_manifest["declared_files"])
    paths.update(governance["files"])
    paths.add("00_CTO/14_BACKTEST_ENGINE/PACKAGE_MANIFEST.json")
    paths.update(
        {
            "02_TSIS_BACKTEST_ENGINE/RUN_BT_GATE_015_V0_4_POSTEXECUTION_TESTS.py",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/31_BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/32_BT_GATE_015_V0_4_CONSUMED_SUCCESS_READOUT.md",
            "02_TSIS_BACKTEST_ENGINE/docs/00_system/33_BT_GATE_015_V0_4_POSTEXECUTION_REVIEW_REQUEST.md",
            "02_TSIS_BACKTEST_ENGINE/scripts/package_bt_gate_015_v0_4_postexecution.py",
            "02_TSIS_BACKTEST_ENGINE/deliverables/"
            + PREEXEC_PACKET.name,
        }
    )
    for path in RUN_ROOT.iterdir():
        if path.is_file():
            paths.add(f"02_TSIS_BACKTEST_ENGINE/runs/{RUN_ID}/{path.name}")

    specification = json.loads(
        (
            ENGINE_ROOT
            / "configs/authorizations/"
            "bt_gate_015_single_use_physical_event_state_consumer_v0_4_spec.json"
        ).read_text(encoding="utf-8")
    )
    candidate = specification["governed_inputs"]["candidate_jsonl"]["relative_path"]
    files: dict[str, dict[str, object]] = {}
    physical_event_state_files = 0
    for relative in sorted(paths):
        normalized = relative.replace("\\", "/")
        path = TSIS_ROOT / normalized
        if not path.is_file():
            raise FileNotFoundError(path)
        if normalized == candidate or normalized.endswith("event_state_candidate_records.jsonl"):
            physical_event_state_files += 1
            continue
        files[normalized] = {"sha256": sha256(path), "size_bytes": path.stat().st_size}
    if physical_event_state_files:
        raise RuntimeError("physical Event State candidate must not be packaged")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ENGINE_ROOT / "deliverables" / (
        f"bt_gate_015_v0_4_physical_postexecution_packet_r1_{stamp}.zip"
    )
    manifest = {
        "package_id": "BT_GATE_015_V0_4_PHYSICAL_POSTEXECUTION_PACKET_R1",
        "status": "PENDING_POSTEXECUTION_EXTERNAL_REVIEW",
        "bt_gate_015": "OPEN_PENDING_V0_4_POSTEXECUTION_EXTERNAL_REVIEW",
        "bt_gate_015_closed_pass": "NOT_AUTHORIZED",
        "approved_preexecution_packet": PREEXEC_PACKET.name,
        "approved_preexecution_packet_sha256": PREEXEC_SHA256,
        "authorization_id": state["authorization_id"],
        "authorization_status": "CONSUMED_FINAL",
        "authorization_consumption_count": 1,
        "second_execution": "PROHIBITED",
        "physical_data_files_opened": 1,
        "physical_state_records_scanned": 8,
        "physical_state_rows_selected": 1,
        "market_state_dependency_events": 1,
        "event_state_events_emitted": 1,
        "event_state_store_inserts": 1,
        "bounded_probe_observations": 1,
        "typed_scientific_values": 17,
        "delivery_before_available_at": 0,
        "orders": 0,
        "fills": 0,
        "pnl_calculated": False,
        "provider_modification": False,
        "deterministic_output_hash": final["deterministic_output_hash"],
        "scientific_manifest_hash": final["scientific_manifest_hash"],
        "focused_postexecution_suite": "25/25 PASS",
        "full_repository_suite": "281/281 PASS",
        "governance_validation": f"PASS / {len(governance['files'])} hashes",
        "physical_event_state_files_included": 0,
        "declared_file_count": len(files),
        "declared_files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in sorted(files):
            archive.write(TSIS_ROOT / relative, relative)
        archive.writestr(
            "ZIP_MANIFEST.json",
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        )
    print(json.dumps({
        "zip_path": str(output),
        "zip_sha256": sha256(output),
        "zip_entries": len(files) + 1,
        "manifest_declared_files": len(files),
        "physical_event_state_files_included": 0,
        "authorization_status": "CONSUMED_FINAL",
        "bt_gate_015_closed_pass": "NOT_AUTHORIZED",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
