from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_VERSION = "market_state_bounded_on_demand_reuse_eligibility_transition_review_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "runs"
GATE = "market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1"
SCOPE_PATH = BASE / "configs" / f"{GATE}_scope.json"
BASELINE_RUN_ID = "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z"
IDEMP_RUN_ID = "market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z"
BASELINE_RUN_DIR = RUNS / BASELINE_RUN_ID
IDEMP_RUN_DIR = RUNS / IDEMP_RUN_ID
NEXT_GATE = "market_state_on_demand_incremental_overlap_execution_authorization_v0_1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=BASE, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNKNOWN"


def main() -> int:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{GATE}_{timestamp}"
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    scope = read_json(SCOPE_PATH)
    baseline_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    baseline_final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    candidate_review = read_json(BASE / "market_state_bounded_on_demand_candidate_dataset_review_matrix_v0_1.json")
    determinism_matrix = read_json(BASE / "market_state_bounded_on_demand_determinism_validation_matrix_v0_1.json")
    idemp_final = read_json(IDEMP_RUN_DIR / "final_manifest.json")
    idemp_report = read_json(IDEMP_RUN_DIR / "idempotency_reuse_test_report.json")
    idemp_evidence = read_json(IDEMP_RUN_DIR / "idempotency_reuse_evidence_entry.json")

    checks = {
        "scope_status_authorized": scope.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "baseline_dataset_id_match": baseline_registry.get("dataset_id") == scope.get("candidate_dataset_id"),
        "baseline_request_fingerprint_match": baseline_registry.get("request_fingerprint") == scope.get("baseline_request_fingerprint"),
        "baseline_execution_plan_fingerprint_match": baseline_registry.get("execution_plan_fingerprint") == scope.get("baseline_execution_plan_fingerprint"),
        "baseline_candidate_dataset_fingerprint_match": baseline_registry.get("candidate_dataset_fingerprint") == scope.get("candidate_dataset_fingerprint"),
        "baseline_registry_status_validated_candidate": baseline_registry.get("registry_status") == "validated_candidate",
        "baseline_validation_passed_with_restrictions": baseline_registry.get("validation_status") == "pass_with_restrictions",
        "baseline_reuse_pending": baseline_registry.get("reuse_eligibility") == scope.get("authorized_transition", {}).get("from_reuse_eligibility"),
        "candidate_dataset_review_approved": candidate_review.get("status") == "CLOSED_APPROVED_AS_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION",
        "determinism_validation_approved": determinism_matrix.get("status") == "CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION",
        "determinism_transition_ready": determinism_matrix.get("decision", {}).get("reuse_transition_ready") is True,
        "idempotency_run_passed": idemp_final.get("status") == "CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS",
        "idempotency_status_match": idemp_final.get("idempotency_status") == scope.get("required_idempotency_status"),
        "idempotency_selected_same_dataset": idemp_final.get("selected_dataset_id") == scope.get("candidate_dataset_id"),
        "idempotency_scientific_fp_match": idemp_final.get("selected_scientific_dataset_fingerprint") == scope.get("scientific_dataset_fingerprint"),
        "idempotency_zero_materializer": idemp_final.get("materializer_executions") == 0,
        "idempotency_zero_source_rows": idemp_final.get("source_market_data_rows_read") == 0,
        "idempotency_zero_candidate_parquet_reads": idemp_final.get("candidate_parquet_files_read") == 0,
        "idempotency_zero_new_registry_entries": idemp_final.get("new_candidate_dataset_registry_entries") == 0,
        "no_official_dataset": idemp_final.get("official_dataset") is False and baseline_final.get("official_dataset") is False,
        "no_production": idemp_final.get("production") is False and baseline_final.get("production") is False,
        "no_downstream": idemp_final.get("downstream") is False and baseline_final.get("downstream") is False,
    }
    hard_failures = [name for name, ok in checks.items() if not ok]
    approved = not hard_failures
    status = "CLOSED_APPROVED_REUSE_ELIGIBILITY_TRANSITION_FOR_BOUNDED_EXACT_MATCH_WITH_RESTRICTIONS_NO_PROMOTION" if approved else "CLOSED_BLOCKED_REUSE_ELIGIBILITY_TRANSITION_REVIEW"

    matrix = {
        "review_id": run_id,
        "gate": GATE,
        "review_status": status,
        "created_at_utc": utc_now(),
        "baseline_run_id": BASELINE_RUN_ID,
        "idempotency_reuse_test_run_id": IDEMP_RUN_ID,
        "candidate_dataset_id": scope.get("candidate_dataset_id"),
        "checks": checks,
        "hard_failures": hard_failures,
        "authorized_transition": scope.get("authorized_transition"),
        "transition_approved": approved,
        "restrictions": [
            "eligible only for the same bounded exact request and resolved authorities",
            "no official dataset promotion",
            "no production use",
            "no downstream consumption",
            "no unbounded reuse",
            "no incremental execution authority",
            "baseline candidate registry entry is not rewritten in place",
        ],
        "next_gate": NEXT_GATE if approved else GATE,
    }
    matrix["matrix_fingerprint"] = sha256_payload({k: v for k, v in matrix.items() if k != "matrix_fingerprint"})
    write_json(run_dir / "review_matrix.json", matrix)

    transition_record = {
        "transition_record_id": f"reuse_eligibility_transition:{scope.get('candidate_dataset_id')}:bounded_exact_match:v0_1",
        "review_id": run_id,
        "candidate_dataset_id": scope.get("candidate_dataset_id"),
        "baseline_registry_entry_fingerprint": baseline_registry.get("registry_entry_fingerprint"),
        "request_fingerprint": scope.get("baseline_request_fingerprint"),
        "execution_plan_fingerprint": scope.get("baseline_execution_plan_fingerprint"),
        "candidate_dataset_fingerprint": scope.get("candidate_dataset_fingerprint"),
        "scientific_dataset_fingerprint": scope.get("scientific_dataset_fingerprint"),
        "reuse_eligibility_before_review": baseline_registry.get("reuse_eligibility"),
        "reuse_eligibility_after_review": "eligible_for_bounded_exact_match_reuse" if approved else baseline_registry.get("reuse_eligibility"),
        "transition_scope": "bounded_exact_match_only",
        "transition_status": "approved" if approved else "blocked",
        "transition_reason": "bounded candidate review, deterministic rerun validation and idempotency/reuse lookup all passed" if approved else "blocking review findings present",
        "baseline_registry_entry_mutated": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "created_at_utc": utc_now(),
    }
    transition_record["transition_record_fingerprint"] = sha256_payload({k: v for k, v in transition_record.items() if k != "transition_record_fingerprint"})
    write_json(run_dir / "reuse_eligibility_transition_record_v0_1.json", transition_record)

    final_manifest = {
        "run_id": run_id,
        "status": status,
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"]),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["status", "--porcelain"])),
        "candidate_dataset_id": scope.get("candidate_dataset_id"),
        "reuse_eligibility_before_review": baseline_registry.get("reuse_eligibility"),
        "reuse_eligibility_after_review": transition_record.get("reuse_eligibility_after_review"),
        "transition_approved": approved,
        "transition_scope": "bounded_exact_match_only",
        "registry_entry_mutations": 0,
        "candidate_parquet_files_read": 0,
        "source_market_data_rows_read": 0,
        "materializer_executions": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "hard_failures": hard_failures,
        "matrix_fingerprint": matrix["matrix_fingerprint"],
        "transition_record_fingerprint": transition_record["transition_record_fingerprint"],
        "next_gate": NEXT_GATE if approved else GATE,
        "artifacts": {
            "review_matrix": str(run_dir / "review_matrix.json"),
            "transition_record": str(run_dir / "reuse_eligibility_transition_record_v0_1.json"),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)

    readout = f"""# Market State Bounded On-Demand Reuse Eligibility Transition Review v0.1\n\nStatus: `{status}`\nRun: `{run_id}`\nDate: `2026-07-25`\n\n## Decision\n\n```text\ntransition_approved = {str(approved).lower()}\nreuse_eligibility_before_review = {baseline_registry.get('reuse_eligibility')}\nreuse_eligibility_after_review = {transition_record.get('reuse_eligibility_after_review')}\ntransition_scope = bounded_exact_match_only\nregistry_entry_mutations = 0\n```\n\n## Evidence\n\n```text\nbaseline_candidate_dataset = {scope.get('candidate_dataset_id')}\nidempotency_reuse_test_run = {IDEMP_RUN_ID}\nidempotency_status = {idemp_final.get('idempotency_status')}\nmaterializer_executions = {idemp_final.get('materializer_executions')}\nsource_market_data_rows_read = {idemp_final.get('source_market_data_rows_read')}\ncandidate_parquet_files_read = {idemp_final.get('candidate_parquet_files_read')}\nnew_candidate_dataset_registry_entries = {idemp_final.get('new_candidate_dataset_registry_entries')}\nhard_failures = {len(hard_failures)}\n```\n\n## Boundary\n\nNo official Market State dataset, production use, downstream consumption,\nunbounded reuse or incremental execution is authorized by this review. The\ntransition is represented by a transition record; the baseline candidate\nregistry entry is not rewritten in place.\n\nNext gate:\n\n```text\n{final_manifest['next_gate']}\n```\n"""
    (run_dir / "review_readout.md").write_text(readout, encoding="utf-8", newline="\n")

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False))
    return 0 if approved else 2


if __name__ == "__main__":
    raise SystemExit(main())
