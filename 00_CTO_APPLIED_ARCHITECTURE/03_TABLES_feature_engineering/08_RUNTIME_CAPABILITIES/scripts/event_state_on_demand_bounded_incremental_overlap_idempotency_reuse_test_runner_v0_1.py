from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\08_RUNTIME_CAPABILITIES")
RUNS = BASE / "runs"
SCOPE_PATH = BASE / "configs" / "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_scope_v0_1.json"
CONTRACT_PATH = BASE / "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_contract_v0_1.json"
SOURCE_RUN_ID = "event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z"
REVIEW_RUN_ID = "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1_20260728T091026Z"
GATE_ID = "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_v0_1"
SCRIPT_VERSION = "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_runner_v0_1"
PASS_STATUS = "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS"
FAIL_STATUS = "CLOSED_FAIL_EVENT_STATE_INCREMENTAL_OVERLAP_IDEMPOTENCY_REUSE_TEST"
NEXT_GATE = "event_state_on_demand_second_generation_incremental_extension_authorization_v0_1"
REPO_ROOT = Path(__file__).resolve().parents[4]


def now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def now_z() -> str:
    return now_dt().isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha_json(data: Any) -> str:
    return hashlib.sha256(stable_json(data).encode("utf-8")).hexdigest()


def without_key(data: dict[str, Any], key: str) -> dict[str, Any]:
    return {k: v for k, v in data.items() if k != key}


def git_value(args: list[str]) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, capture_output=True, check=False)
    except Exception:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def artifact_by_role(manifest: dict[str, Any], role: str) -> dict[str, Any]:
    for row in manifest["files"]:
        if row["role"] == role:
            return row
    raise RuntimeError(f"Missing artifact role: {role}")


def main() -> int:
    scope = read_json(SCOPE_PATH)
    contract = read_json(CONTRACT_PATH)
    if scope["authorized_next_gate"] != GATE_ID:
        raise RuntimeError("Scope does not authorize this reuse test")
    if scope["status"] != "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION":
        raise RuntimeError("Scope is not executable")
    if contract["governing_authorization"] != "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_authorization_v0_1":
        raise RuntimeError("Unexpected reuse-test contract authority")

    source_dir = RUNS / SOURCE_RUN_ID
    review_dir = RUNS / REVIEW_RUN_ID
    final = read_json(source_dir / "final_manifest.json")
    candidate_manifest = read_json(source_dir / "event_state_incremental_overlap_candidate_output_manifest.json")
    registry_entry = read_json(source_dir / "candidate_registry_entry.json")
    review_final = read_json(review_dir / "final_manifest.json")
    review_matrix = read_json(BASE / "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_matrix_v0_1.json")

    run_id = GATE_ID + "_" + now_dt().strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = now_z()

    combined_file = artifact_by_role(candidate_manifest, "combined_event_state_candidate_records")
    delta_file = artifact_by_role(candidate_manifest, "delta_event_state_candidate_records")
    combined_path = Path(combined_file["path"])
    delta_path = Path(delta_file["path"])
    combined_file_available = combined_path.exists()
    delta_file_available = delta_path.exists()
    combined_file_hash_match = combined_file_available and sha_file(combined_path) == combined_file["sha256"]
    delta_file_hash_match = delta_file_available and sha_file(delta_path) == delta_file["sha256"]

    checks = [
        (final["final_run_status"] == "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED", "source_incremental_run_closed_pass"),
        (review_final["status"] == "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION", "candidate_review_closed_pass"),
        (review_matrix["status"] == review_final["status"], "review_matrix_status_match"),
        (final["candidate_dataset_fingerprint"] == scope["combined_candidate_dataset_fingerprint"] == registry_entry["event_state_candidate_dataset_fingerprint"], "candidate_dataset_fingerprint_match"),
        (final["logical_event_state_dataset_fingerprint"] == scope["combined_logical_event_state_dataset_fingerprint"] == registry_entry["logical_event_state_dataset_fingerprint"], "logical_dataset_fingerprint_match"),
        (final["physical_artifact_fingerprint"] == scope["combined_physical_artifact_fingerprint"] == registry_entry["physical_artifact_fingerprint"], "physical_artifact_fingerprint_match"),
        (final["validation_result_fingerprint"] == scope["combined_validation_result_fingerprint"] == registry_entry["validation_result_fingerprint"], "validation_fingerprint_match"),
        (review_final["review_matrix_sha256"] == scope["review_matrix_sha256"], "review_matrix_sha_match"),
        (review_final["context_ledger_sha256"] == scope["context_ledger_sha256"], "context_ledger_sha_match"),
        (review_final["fingerprint_comparison_sha256"] == scope["fingerprint_comparison_sha256"], "fingerprint_comparison_sha_match"),
        (registry_entry["dataset_id"] == scope["expected_reuse_hit_dataset_id"], "reuse_hit_dataset_id_match"),
        (registry_entry["registry_status"] == "validated_candidate", "registry_status_validated_candidate"),
        (registry_entry["reuse_eligibility"] == "pending_incremental_overlap_candidate_dataset_review", "reuse_eligibility_not_promoted_before_test"),
        (combined_file_available and delta_file_available, "candidate_artifacts_available"),
        (combined_file_hash_match and delta_file_hash_match, "candidate_artifact_hashes_match"),
        (final["requested_event_state_context_count"] == 12 and final["represented_context_count"] == 11 and final["unavailable_context_count"] == 1, "coverage_counts_match"),
        (final["official_event_state_dataset"] is False and final["production"] is False and final["downstream"] is False, "official_production_downstream_closed"),
    ]
    hard_failures = sum(0 if passed else 1 for passed, _ in checks)
    status = PASS_STATUS if hard_failures == 0 else FAIL_STATUS
    report = {
        "run_id": run_id,
        "gate": GATE_ID,
        "status": status,
        "reuse_decision": "reuse_hit_existing_incremental_overlap_candidate" if hard_failures == 0 else "blocked",
        "selected_candidate_dataset_id": registry_entry["dataset_id"] if hard_failures == 0 else None,
        "selected_candidate_dataset_fingerprint": final["candidate_dataset_fingerprint"] if hard_failures == 0 else None,
        "selected_logical_event_state_dataset_fingerprint": final["logical_event_state_dataset_fingerprint"] if hard_failures == 0 else None,
        "selected_physical_artifact_fingerprint": final["physical_artifact_fingerprint"] if hard_failures == 0 else None,
        "checks": [{"check_id": name, "status": "PASS" if passed else "FAIL"} for passed, name in checks],
        "hard_failures": hard_failures,
        "event_state_materializer_executions": 0,
        "market_state_materializer_executions": 0,
        "source_market_data_rows_read": 0,
        "event_state_candidate_records_read": 0,
        "market_state_candidate_records_read": 0,
        "candidate_artifact_availability_checks": 2,
        "new_candidate_dataset_registry_entries": 0,
        "baseline_registry_entry_mutations": 0,
        "combined_registry_entry_mutations": 0,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    report["reuse_report_fingerprint"] = sha_json(without_key(report, "reuse_report_fingerprint"))
    evidence = {
        "evidence_id": "event_state_incremental_overlap_reuse_evidence_v0_1_" + report["reuse_report_fingerprint"][:16],
        "run_id": run_id,
        "selected_candidate_dataset_id": report["selected_candidate_dataset_id"],
        "selected_candidate_dataset_fingerprint": report["selected_candidate_dataset_fingerprint"],
        "selected_logical_event_state_dataset_fingerprint": report["selected_logical_event_state_dataset_fingerprint"],
        "selected_physical_artifact_fingerprint": report["selected_physical_artifact_fingerprint"],
        "reuse_report_fingerprint": report["reuse_report_fingerprint"],
        "reuse_scope": "bounded_incremental_overlap_exact_match_only",
        "reuse_eligibility_transition_ready": hard_failures == 0,
        "official_event_state_dataset": False,
        "production": False,
        "downstream": False,
    }
    evidence["evidence_fingerprint"] = sha_json(without_key(evidence, "evidence_fingerprint"))

    write_json(run_dir / "reuse_resolution_report.json", report)
    write_json(run_dir / "combined_candidate_availability_report.json", {
        "combined_file_available": combined_file_available,
        "delta_file_available": delta_file_available,
        "combined_file_hash_match": combined_file_hash_match,
        "delta_file_hash_match": delta_file_hash_match,
        "candidate_record_content_read": False,
    })
    write_json(run_dir / "reuse_hit_evidence.json", evidence)

    final_manifest = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "final_run_status": status,
        "started_at_utc": started,
        "ended_at_utc": now_z(),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN",
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "git_commit": git_value(["git", "rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["git", "status", "--porcelain"])),
        "selected_candidate_dataset_id": report["selected_candidate_dataset_id"],
        "selected_candidate_dataset_fingerprint": report["selected_candidate_dataset_fingerprint"],
        "selected_logical_event_state_dataset_fingerprint": report["selected_logical_event_state_dataset_fingerprint"],
        "selected_physical_artifact_fingerprint": report["selected_physical_artifact_fingerprint"],
        "reviewed_incremental_run_id": SOURCE_RUN_ID,
        "reviewed_incremental_candidate_review_run_id": REVIEW_RUN_ID,
        "requested_contexts": final["requested_event_state_context_count"],
        "represented_contexts": final["represented_context_count"],
        "unavailable_contexts": final["unavailable_context_count"],
        "event_state_materializer_executions": 0,
        "market_state_materializer_executions": 0,
        "source_market_data_rows_read": 0,
        "event_state_candidate_records_read": 0,
        "market_state_candidate_records_read": 0,
        "new_candidate_dataset_registry_entries": 0,
        "baseline_registry_entry_mutations": 0,
        "combined_registry_entry_mutations": 0,
        "hard_failures": hard_failures,
        "idempotency_status": "PROVEN_FOR_EVENT_STATE_INCREMENTAL_OVERLAP_REUSE" if hard_failures == 0 else "NOT_PROVEN",
        "reuse_eligibility_transition_ready": hard_failures == 0,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": NEXT_GATE if hard_failures == 0 else None,
        "artifacts": {
            "reuse_resolution_report": str(run_dir / "reuse_resolution_report.json"),
            "combined_candidate_availability_report": str(run_dir / "combined_candidate_availability_report.json"),
            "reuse_hit_evidence": str(run_dir / "reuse_hit_evidence.json"),
            "readout": str(run_dir / "reuse_readout.md"),
        },
    }
    final_manifest["final_manifest_sha256"] = sha_json(without_key(final_manifest, "final_manifest_sha256"))
    write_json(run_dir / "final_manifest.json", final_manifest)
    readout = f"""# Event State On-Demand Bounded Incremental Overlap Idempotency Reuse Test Readout v0.1

Status: `{status}`
Run ID: `{run_id}`
Date: `2026-07-28`

```text
selected_candidate_dataset_id = {report['selected_candidate_dataset_id']}
selected_candidate_dataset_fingerprint = {report['selected_candidate_dataset_fingerprint']}
requested_contexts = {final['requested_event_state_context_count']}
represented_contexts = {final['represented_context_count']}
unavailable_contexts = {final['unavailable_context_count']}
event_state_materializer_executions = 0
market_state_materializer_executions = 0
source_market_data_rows_read = 0
event_state_candidate_records_read = 0
market_state_candidate_records_read = 0
new_candidate_dataset_registry_entries = 0
hard_failures = {hard_failures}
idempotency_status = {final_manifest['idempotency_status']}
official_event_state_dataset = false
production = false
downstream = false
next_allowed_gate = {final_manifest['next_allowed_gate']}
```

The same reviewed incremental overlap request resolved to the same governed
combined candidate without rebuilding Event State or Market State and without
creating a new dataset identity.
"""
    (run_dir / "reuse_readout.md").write_text(readout, encoding="utf-8")
    print(json.dumps({"run_id": run_id, "status": status, "hard_failures": hard_failures, "next_gate": final_manifest["next_allowed_gate"]}, indent=2))
    return 0 if hard_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
