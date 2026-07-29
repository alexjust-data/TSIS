from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_VERSION = "event_state_on_demand_bounded_reuse_eligibility_transition_review_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "runs"
GATE = "event_state_on_demand_bounded_reuse_eligibility_transition_review_v0_1"
SCOPE_PATH = BASE / "configs" / "event_state_on_demand_bounded_reuse_eligibility_transition_review_scope_v0_1.json"
BASELINE_RUN_ID = "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"
IDEMP_RUN_ID = "event_state_on_demand_bounded_idempotency_reuse_test_v0_1_20260728T074624Z"
BASELINE_RUN_DIR = RUNS / BASELINE_RUN_ID
IDEMP_RUN_DIR = RUNS / IDEMP_RUN_ID
NEXT_GATE = "event_state_on_demand_bounded_incremental_overlap_execution_authorization_v0_1"


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
    candidate_review = read_json(BASE / "event_state_on_demand_bounded_candidate_dataset_review_matrix_v0_1.json")
    determinism_matrix = read_json(BASE / "event_state_on_demand_bounded_determinism_validation_matrix_v0_1.json")
    idemp_final = read_json(IDEMP_RUN_DIR / "final_manifest.json")
    idemp_report = read_json(IDEMP_RUN_DIR / "idempotency_reuse_test_report.json")
    idemp_evidence = read_json(IDEMP_RUN_DIR / "idempotency_reuse_evidence_entry.json")

    transition = scope["authorized_transition"]
    checks = {
        "scope_status_authorized": scope.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "baseline_dataset_id_match": baseline_registry.get("dataset_id") == scope.get("candidate_dataset_id"),
        "baseline_request_fingerprint_match": baseline_registry.get("event_state_request_fingerprint") == scope.get("event_state_request_fingerprint"),
        "baseline_execution_plan_fingerprint_match": baseline_registry.get("event_state_execution_plan_fingerprint") == scope.get("event_state_execution_plan_fingerprint"),
        "baseline_candidate_dataset_fingerprint_match": baseline_registry.get("event_state_candidate_dataset_fingerprint") == scope.get("candidate_dataset_fingerprint"),
        "baseline_logical_dataset_fingerprint_match": baseline_registry.get("logical_dataset_fingerprint") == scope.get("logical_dataset_fingerprint"),
        "baseline_registry_status_validated_candidate": baseline_registry.get("registry_status") == "validated_candidate",
        "baseline_validation_passed_with_restrictions": baseline_registry.get("validation_status") == "pass_with_restrictions",
        "baseline_reuse_pending": baseline_registry.get("reuse_eligibility") == transition.get("from_reuse_eligibility"),
        "candidate_dataset_review_approved": candidate_review.get("status") == "CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION",
        "candidate_review_hard_failures_zero": candidate_review.get("decision", {}).get("hard_review_failures", 0) == 0,
        "determinism_validation_approved": determinism_matrix.get("status") == "CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION",
        "determinism_transition_ready": determinism_matrix.get("decision", {}).get("reuse_transition_ready") is True,
        "determinism_normalized_logical_fingerprint_match": determinism_matrix.get("normalized_logical_dataset_fingerprint") == scope.get("normalized_logical_dataset_fingerprint"),
        "idempotency_run_passed": idemp_final.get("status") == "CLOSED_PASS_EVENT_STATE_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS",
        "idempotency_status_match": idemp_final.get("idempotency_status") == scope.get("required_idempotency_status"),
        "idempotency_selected_same_dataset": idemp_final.get("selected_candidate_dataset_id") == scope.get("candidate_dataset_id") or idemp_final.get("baseline_candidate_dataset_id") == scope.get("candidate_dataset_id"),
        "idempotency_candidate_fingerprint_match": idemp_final.get("selected_candidate_dataset_fingerprint") == scope.get("candidate_dataset_fingerprint"),
        "idempotency_normalized_logical_fingerprint_match": idemp_final.get("selected_normalized_logical_dataset_fingerprint") == scope.get("normalized_logical_dataset_fingerprint"),
        "idempotency_zero_event_state_materializer": idemp_final.get("event_state_materializer_executions") == 0,
        "idempotency_zero_market_state_materializer": idemp_final.get("market_state_materializer_executions") == 0,
        "idempotency_zero_event_state_candidate_record_reads": idemp_final.get("event_state_candidate_records_read") == 0,
        "idempotency_zero_market_state_candidate_record_reads": idemp_final.get("market_state_candidate_records_read") == 0,
        "idempotency_zero_source_rows": idemp_final.get("source_market_data_rows_read") == 0,
        "idempotency_zero_new_registry_entries": idemp_final.get("new_candidate_dataset_registry_entries") == 0,
        "idempotency_evidence_entry_written": idemp_final.get("idempotency_reuse_evidence_entries_written") == 1,
        "idempotency_report_fingerprint_match": idemp_final.get("report_fingerprint") == idemp_report.get("report_fingerprint"),
        "idempotency_evidence_fingerprint_match": idemp_final.get("evidence_entry_fingerprint") == idemp_evidence.get("evidence_entry_fingerprint"),
        "no_official_event_state_dataset": idemp_final.get("official_event_state_dataset") is False and baseline_final.get("official_event_state_dataset") is False,
        "no_official_dataset": idemp_final.get("official_dataset") is False and baseline_final.get("official_dataset") is False,
        "no_production": idemp_final.get("production") is False and baseline_final.get("production") is False,
        "no_downstream": idemp_final.get("downstream") is False and baseline_final.get("downstream") is False,
    }
    hard_failures = [name for name, ok in checks.items() if not ok]
    approved = not hard_failures
    status = "CLOSED_APPROVED_EVENT_STATE_REUSE_ELIGIBILITY_TRANSITION_FOR_BOUNDED_EXACT_MATCH_WITH_RESTRICTIONS_NO_PROMOTION" if approved else "CLOSED_BLOCKED_EVENT_STATE_REUSE_ELIGIBILITY_TRANSITION_REVIEW"

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
        "authorized_transition": transition,
        "transition_approved": approved,
        "restrictions": [
            "eligible only for the same bounded Event State exact-match request and resolved authorities",
            "no official Event State dataset promotion",
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
        "transition_record_id": f"event_state_reuse_eligibility_transition:{scope.get('candidate_dataset_id')}:bounded_exact_match:v0_1",
        "review_id": run_id,
        "candidate_dataset_id": scope.get("candidate_dataset_id"),
        "baseline_registry_entry_fingerprint": baseline_registry.get("registry_entry_fingerprint"),
        "event_state_request_fingerprint": scope.get("event_state_request_fingerprint"),
        "event_state_execution_plan_fingerprint": scope.get("event_state_execution_plan_fingerprint"),
        "candidate_dataset_fingerprint": scope.get("candidate_dataset_fingerprint"),
        "logical_dataset_fingerprint": scope.get("logical_dataset_fingerprint"),
        "normalized_logical_dataset_fingerprint": scope.get("normalized_logical_dataset_fingerprint"),
        "validation_result_fingerprint": scope.get("validation_result_fingerprint"),
        "reuse_eligibility_before_review": baseline_registry.get("reuse_eligibility"),
        "reuse_eligibility_after_review": transition.get("to_reuse_eligibility") if approved else baseline_registry.get("reuse_eligibility"),
        "transition_scope": transition.get("transition_scope"),
        "transition_status": "approved" if approved else "blocked",
        "transition_reason": "bounded candidate review, deterministic rerun validation and Event State exact-match reuse lookup all passed" if approved else "blocking review findings present",
        "baseline_registry_entry_mutated": False,
        "official_event_state_dataset": False,
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
        "transition_scope": transition.get("transition_scope"),
        "registry_entry_mutations": 0,
        "event_state_candidate_files_read": 0,
        "event_state_candidate_records_read": 0,
        "market_state_candidate_files_read": 0,
        "market_state_candidate_records_read": 0,
        "source_market_data_rows_read": 0,
        "event_state_materializer_executions": 0,
        "market_state_materializer_executions": 0,
        "official_event_state_dataset": False,
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

    readout = f"""# Event State On-Demand Bounded Reuse Eligibility Transition Review v0.1

Status: `{status}`
Run: `{run_id}`
Date: `2026-07-28`

## Decision

```text
transition_approved = {str(approved).lower()}
reuse_eligibility_before_review = {baseline_registry.get('reuse_eligibility')}
reuse_eligibility_after_review = {transition_record.get('reuse_eligibility_after_review')}
transition_scope = {transition.get('transition_scope')}
registry_entry_mutations = 0
```

## Evidence

```text
baseline_candidate_dataset = {scope.get('candidate_dataset_id')}
idempotency_reuse_test_run = {IDEMP_RUN_ID}
idempotency_status = {idemp_final.get('idempotency_status')}
event_state_materializer_executions = {idemp_final.get('event_state_materializer_executions')}
market_state_materializer_executions = {idemp_final.get('market_state_materializer_executions')}
event_state_candidate_records_read = {idemp_final.get('event_state_candidate_records_read')}
market_state_candidate_records_read = {idemp_final.get('market_state_candidate_records_read')}
source_market_data_rows_read = {idemp_final.get('source_market_data_rows_read')}
new_candidate_dataset_registry_entries = {idemp_final.get('new_candidate_dataset_registry_entries')}
hard_failures = {len(hard_failures)}
```

## Boundary

No official Event State dataset, production use, downstream consumption,
unbounded reuse, incremental execution or new materialization is authorized by
this review. The transition is represented by a transition record; the baseline
candidate registry entry is not rewritten in place.

Next gate:

```text
{final_manifest['next_gate']}
```
"""
    (run_dir / "review_readout.md").write_text(readout, encoding="utf-8", newline="\n")

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False))
    return 0 if approved else 2


if __name__ == "__main__":
    raise SystemExit(main())
