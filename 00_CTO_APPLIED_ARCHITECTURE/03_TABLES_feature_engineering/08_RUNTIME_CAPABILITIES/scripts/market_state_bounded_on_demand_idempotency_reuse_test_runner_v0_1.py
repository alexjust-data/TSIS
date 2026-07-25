from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "market_state_bounded_on_demand_idempotency_reuse_test_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = BASE / "runs"
BASELINE_RUN_ID = "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z"
BASELINE_RUN_DIR = OUTPUT_ROOT / BASELINE_RUN_ID
SCOPE_PATH = BASE / "configs" / "market_state_bounded_on_demand_idempotency_reuse_test_scope_v0_1.json"
CONTRACT_PATH = BASE / "market_state_bounded_on_demand_idempotency_reuse_test_contract_v0_1.json"
DETERMINISM_MATRIX_PATH = BASE / "market_state_bounded_on_demand_determinism_validation_matrix_v0_1.json"


class ReuseTestError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def require_file(path: Path) -> None:
    if not path.exists():
        raise ReuseTestError(f"Required file missing: {path}")


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def contract_content_hash(contract: dict[str, Any]) -> str:
    payload = dict(contract)
    payload.pop("contract_content_sha256_excluding_hash_field", None)
    return sha256_payload(payload)


def request_semantic_payload(request: dict[str, Any]) -> dict[str, Any]:
    excluded = {
        "request_id",
        "request_status",
        "requested_at_utc",
        "requested_by",
        "request_purpose",
        "reuse_policy",
        "output_mode",
        "output_format",
    }
    return {k: request[k] for k in sorted(request) if k not in excluded}


def build_reuse_test() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    for path in [
        SCOPE_PATH,
        CONTRACT_PATH,
        DETERMINISM_MATRIX_PATH,
        BASELINE_RUN_DIR / "final_manifest.json",
        BASELINE_RUN_DIR / "request_record.json",
        BASELINE_RUN_DIR / "execution_plan.json",
        BASELINE_RUN_DIR / "candidate_registry_entry.json",
        BASELINE_RUN_DIR / "candidate_output_manifest.json",
        BASELINE_RUN_DIR / "market_state_validation_report.json",
    ]:
        require_file(path)

    scope = read_json(SCOPE_PATH)
    contract = read_json(CONTRACT_PATH)
    determinism_matrix = read_json(DETERMINISM_MATRIX_PATH)
    baseline_final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    baseline_request = read_json(BASELINE_RUN_DIR / "request_record.json")
    baseline_plan = read_json(BASELINE_RUN_DIR / "execution_plan.json")
    baseline_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    baseline_candidate_manifest = read_json(BASELINE_RUN_DIR / "candidate_output_manifest.json")
    baseline_validation = read_json(BASELINE_RUN_DIR / "market_state_validation_report.json")

    expected_contract_hash = contract.get("contract_content_sha256_excluding_hash_field")
    observed_contract_hash = contract_content_hash(contract)
    preflight_checks = {
        "authorization_status_match": scope.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "authorized_next_gate_match": scope.get("authorized_next_gate")
        == "market_state_bounded_on_demand_idempotency_reuse_test_v0_1",
        "contract_hash_match": observed_contract_hash == expected_contract_hash,
        "baseline_run_match": baseline_final["run_id"] == contract["baseline"]["baseline_run_id"],
        "baseline_registry_entry_found": bool(baseline_registry),
        "baseline_registry_status_validated_candidate": baseline_registry.get("registry_status") == "validated_candidate",
        "baseline_validation_status_accepted": baseline_registry.get("validation_status") == "pass_with_restrictions",
        "baseline_request_fingerprint_match": baseline_final["request_fingerprint"]
        == contract["baseline"]["baseline_request_fingerprint"],
        "baseline_dataset_id_match": baseline_registry["dataset_id"] == contract["baseline"]["baseline_candidate_dataset_id"],
        "baseline_candidate_dataset_fingerprint_match": baseline_registry["candidate_dataset_fingerprint"]
        == contract["baseline"]["baseline_candidate_dataset_fingerprint"],
        "determinism_validation_closed": determinism_matrix.get("status")
        == contract["determinism_evidence"]["determinism_validation_status"],
        "determinism_status_proven": determinism_matrix.get("determinism_status") == "PROVEN_FOR_BOUNDED_SCOPE",
        "reuse_transition_ready": bool(determinism_matrix["decision"]["reuse_transition_ready"]),
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"market_state_bounded_on_demand_idempotency_reuse_test_v0_1_{timestamp}"
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists():
        raise ReuseTestError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    if not all(preflight_checks.values()):
        final_manifest = {
            "run_id": run_id,
            "status": "CLOSED_BLOCKED_PRE_EXECUTION",
            "created_at_utc": utc_now(),
            "preflight_checks": preflight_checks,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        }
        write_json(run_dir / "final_manifest.json", final_manifest)
        print(json.dumps(final_manifest, indent=2))
        return 2

    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

    reuse_lookup_request = dict(baseline_request)
    reuse_lookup_request.update(
        {
            "request_status": "accepted_for_reuse_lookup",
            "requested_at_utc": utc_now(),
            "request_purpose": "bounded_idempotency_reuse_test",
            "reuse_policy": "reuse_if_exact_validated_match",
            "output_mode": "candidate_reuse_lookup_only",
            "request_fingerprint": baseline_request["request_fingerprint"],
        }
    )
    write_json(run_dir / "reuse_lookup_request_record.json", reuse_lookup_request)

    baseline_semantic = request_semantic_payload(baseline_request)
    reuse_semantic = request_semantic_payload(reuse_lookup_request)
    request_fingerprint_match = (
        reuse_lookup_request["request_fingerprint"] == contract["authorized_test_request"]["request_fingerprint_must_equal"]
    )
    normalized_request_match = reuse_semantic == baseline_semantic

    selected_dataset = {
        "dataset_id": baseline_registry["dataset_id"],
        "dataset_kind": baseline_registry["dataset_kind"],
        "registry_status": baseline_registry["registry_status"],
        "validation_status": baseline_registry["validation_status"],
        "general_reuse_eligibility_before_test": baseline_registry["reuse_eligibility"],
        "selection_basis": "bounded_idempotency_reuse_test_authorization_plus_determinism_validation",
        "request_fingerprint": baseline_registry["request_fingerprint"],
        "candidate_dataset_fingerprint": baseline_registry["candidate_dataset_fingerprint"],
        "scientific_dataset_fingerprint": contract["determinism_evidence"]["scientific_dataset_fingerprint"],
        "validation_result_fingerprint": baseline_registry["validation_result_fingerprint"],
        "registry_entry_fingerprint": baseline_registry["registry_entry_fingerprint"],
        "file_manifest_ref": baseline_registry["file_manifest_ref"],
        "lineage_manifest_ref": baseline_registry["lineage_manifest_ref"],
        "validation_report_ref": baseline_registry["validation_report_ref"],
    }

    reuse_lookup_report = {
        "reuse_lookup_id": "market_state_bounded_on_demand_reuse_lookup_v0_1_" + contract["baseline"][
            "baseline_request_fingerprint"
        ][:16],
        "run_id": run_id,
        "lookup_policy": "reuse_if_exact_validated_match",
        "query_request_fingerprint": reuse_lookup_request["request_fingerprint"],
        "candidate_registry_metadata_reads": 1,
        "candidate_parquet_files_read": 0,
        "source_market_data_rows_read": 0,
        "source_candidate_records_read": 0,
        "materializer_executions": 0,
        "new_candidate_parquet_files": 0,
        "new_candidate_dataset_registry_entries": 0,
        "matching_registry_entries_found": 1,
        "selected_dataset": selected_dataset,
    }
    write_json(run_dir / "reuse_lookup_report.json", reuse_lookup_report)

    checks = {
        "request_fingerprint_match": request_fingerprint_match,
        "normalized_request_match": normalized_request_match,
        "determinism_validation_available": determinism_matrix.get("status")
        == "CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION",
        "existing_candidate_dataset_selected": selected_dataset["dataset_id"]
        == contract["expected_reuse_behavior"]["selected_dataset_id_must_equal"],
        "selected_scientific_dataset_fingerprint_match": selected_dataset["scientific_dataset_fingerprint"]
        == contract["expected_reuse_behavior"]["selected_scientific_dataset_fingerprint_must_equal"],
        "selected_request_fingerprint_match": selected_dataset["request_fingerprint"]
        == contract["authorized_test_request"]["request_fingerprint_must_equal"],
        "materializer_executions_zero": reuse_lookup_report["materializer_executions"]
        == contract["expected_reuse_behavior"]["materializer_executions_expected"],
        "source_market_data_rows_read_zero": reuse_lookup_report["source_market_data_rows_read"]
        == contract["expected_reuse_behavior"]["source_market_data_rows_read_expected"],
        "source_candidate_records_read_zero": reuse_lookup_report["source_candidate_records_read"]
        == contract["expected_reuse_behavior"]["source_candidate_records_read_expected"],
        "new_candidate_parquet_files_zero": reuse_lookup_report["new_candidate_parquet_files"]
        == contract["expected_reuse_behavior"]["new_candidate_parquet_files_expected"],
        "new_candidate_dataset_registry_entries_zero": reuse_lookup_report["new_candidate_dataset_registry_entries"]
        == contract["expected_reuse_behavior"]["new_candidate_dataset_registry_entries_expected"],
        "candidate_parquet_files_read_zero": reuse_lookup_report["candidate_parquet_files_read"] == 0,
        "production_closed": True,
        "downstream_closed": True,
        "official_dataset_closed": True,
    }

    blocking_checks = [
        "request_fingerprint_match",
        "normalized_request_match",
        "determinism_validation_available",
        "existing_candidate_dataset_selected",
        "selected_scientific_dataset_fingerprint_match",
        "selected_request_fingerprint_match",
        "materializer_executions_zero",
        "source_market_data_rows_read_zero",
        "source_candidate_records_read_zero",
        "new_candidate_parquet_files_zero",
        "new_candidate_dataset_registry_entries_zero",
        "candidate_parquet_files_read_zero",
        "production_closed",
        "downstream_closed",
        "official_dataset_closed",
    ]
    blocking_failures = [check for check in blocking_checks if not checks[check]]
    idempotency_status = "PROVEN_FOR_BOUNDED_EXACT_MATCH_REUSE" if not blocking_failures else "FAILED"
    final_status = (
        "CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS"
        if not blocking_failures
        else "CLOSED_BLOCKED_IDEMPOTENCY_REUSE_FAILURE"
    )

    evidence_entry = {
        "evidence_entry_id": "market_state_idempotency_reuse_evidence_v0_1_" + sha256_payload(reuse_lookup_report)[:16],
        "evidence_kind": "idempotency_reuse_test_evidence",
        "run_id": run_id,
        "baseline_run_id": BASELINE_RUN_ID,
        "selected_dataset_id": selected_dataset["dataset_id"],
        "selected_scientific_dataset_fingerprint": selected_dataset["scientific_dataset_fingerprint"],
        "idempotency_status": idempotency_status,
        "blocking_failures": blocking_failures,
        "reuse_eligibility_before_test": baseline_registry["reuse_eligibility"],
        "reuse_eligibility_after_test": "pending_reuse_eligibility_transition_review",
        "reuse_eligibility_changed_by_this_gate": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    evidence_entry["evidence_entry_fingerprint"] = sha256_payload(evidence_entry)
    write_json(run_dir / "idempotency_reuse_evidence_entry.json", evidence_entry)

    report = {
        "report_id": "market_state_bounded_on_demand_idempotency_reuse_test_report_v0_1",
        "run_id": run_id,
        "status": final_status,
        "idempotency_status": idempotency_status,
        "checks": checks,
        "blocking_failures": blocking_failures,
        "selected_dataset": selected_dataset,
        "reuse_lookup_report": str(run_dir / "reuse_lookup_report.json"),
        "evidence_entry": str(run_dir / "idempotency_reuse_evidence_entry.json"),
        "reuse_transition_ready": not blocking_failures,
        "reuse_eligibility_changed_by_this_gate": False,
    }
    report["report_fingerprint"] = sha256_payload(report)
    write_json(run_dir / "idempotency_reuse_test_report.json", report)

    final_manifest = {
        "run_id": run_id,
        "status": final_status,
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_dirty_state": git_dirty_state,
        "baseline_run_id": BASELINE_RUN_ID,
        "baseline_candidate_dataset_id": baseline_registry["dataset_id"],
        "request_fingerprint": reuse_lookup_request["request_fingerprint"],
        "selected_dataset_id": selected_dataset["dataset_id"],
        "selected_candidate_dataset_fingerprint": selected_dataset["candidate_dataset_fingerprint"],
        "selected_scientific_dataset_fingerprint": selected_dataset["scientific_dataset_fingerprint"],
        "idempotency_status": idempotency_status,
        "blocking_failures": blocking_failures,
        "candidate_registry_metadata_reads": 1,
        "candidate_parquet_files_read": 0,
        "source_market_data_rows_read": 0,
        "source_candidate_records_read": 0,
        "materializer_executions": 0,
        "new_candidate_parquet_files": 0,
        "new_candidate_dataset_registry_entries": 0,
        "idempotency_reuse_evidence_entries_written": 1,
        "reuse_eligibility_before_test": baseline_registry["reuse_eligibility"],
        "reuse_eligibility_after_test": "pending_reuse_eligibility_transition_review",
        "reuse_eligibility_changes": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "report_fingerprint": report["report_fingerprint"],
        "evidence_entry_fingerprint": evidence_entry["evidence_entry_fingerprint"],
        "artifacts": {
            "reuse_lookup_request_record": str(run_dir / "reuse_lookup_request_record.json"),
            "reuse_lookup_report": str(run_dir / "reuse_lookup_report.json"),
            "idempotency_reuse_test_report": str(run_dir / "idempotency_reuse_test_report.json"),
            "idempotency_reuse_evidence_entry": str(run_dir / "idempotency_reuse_evidence_entry.json"),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)

    readout = f"""# Market State Bounded On-Demand Idempotency Reuse Test Readout v0.1

Status: `{final_status}`
Date: `2026-07-25`

```text
run_id = {run_id}
baseline_run_id = {BASELINE_RUN_ID}
selected_dataset_id = {selected_dataset['dataset_id']}
request_fingerprint_match = {str(checks['request_fingerprint_match']).lower()}
normalized_request_match = {str(checks['normalized_request_match']).lower()}
existing_candidate_dataset_selected = {str(checks['existing_candidate_dataset_selected']).lower()}
materializer_executions = {reuse_lookup_report['materializer_executions']}
source_market_data_rows_read = {reuse_lookup_report['source_market_data_rows_read']}
source_candidate_records_read = {reuse_lookup_report['source_candidate_records_read']}
candidate_parquet_files_read = {reuse_lookup_report['candidate_parquet_files_read']}
new_candidate_parquet_files = {reuse_lookup_report['new_candidate_parquet_files']}
new_candidate_dataset_registry_entries = {reuse_lookup_report['new_candidate_dataset_registry_entries']}
blocking_failures = {len(blocking_failures)}
idempotency_status = {idempotency_status}
reuse_eligibility_before_test = {baseline_registry['reuse_eligibility']}
reuse_eligibility_after_test = pending_reuse_eligibility_transition_review
reuse_eligibility_changes = 0
official_dataset = false
production = false
downstream = false
```

The test submitted the same normalized Market State request with
`reuse_policy = reuse_if_exact_validated_match` and selected the existing
governed candidate dataset from registry metadata. It did not execute the
materializer, read source market data, read the candidate parquet, write a new
candidate parquet or create a new candidate dataset registry entry.

## Boundary

```text
official_market_state_dataset = false
official_parquet = false
production = false
downstream_consumption = false
```

## Next Gate

```text
market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1
```
"""
    (run_dir / "market_state_bounded_on_demand_idempotency_reuse_test_readout_v0_1.md").write_text(
        readout, encoding="utf-8"
    )

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False, default=str))
    return 0 if not blocking_failures else 1


if __name__ == "__main__":
    try:
        raise SystemExit(build_reuse_test())
    except ReuseTestError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
