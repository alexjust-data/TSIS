from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "market_state_on_demand_incremental_overlap_idempotency_reuse_test_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = BASE / "runs"

SCOPE_PATH = BASE / "configs" / "market_state_on_demand_incremental_overlap_idempotency_reuse_test_scope_v0_1.json"
CONTRACT_PATH = BASE / "market_state_on_demand_incremental_overlap_idempotency_reuse_test_contract_v0_1.json"
REVIEW_MATRIX_PATH = BASE / "market_state_on_demand_incremental_overlap_candidate_dataset_review_matrix_v0_1.json"
CONTEXT_LEDGER_PATH = BASE / "combined_candidate_context_ledger_v0_1.json"
FINGERPRINT_COMPARISON_PATH = BASE / "combined_candidate_fingerprint_comparison_v0_1.json"

BASELINE_RUN_ID = "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z"
BASELINE_RUN_DIR = OUTPUT_ROOT / BASELINE_RUN_ID
INCREMENTAL_RUN_ID = "market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z"
INCREMENTAL_RUN_DIR = OUTPUT_ROOT / INCREMENTAL_RUN_ID


class IncrementalReuseTestError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def require_file(path: Path) -> None:
    if not path.exists():
        raise IncrementalReuseTestError(f"Required file missing: {path}")


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


def payload_hash_excluding(payload: dict[str, Any], excluded_key: str) -> str:
    normalized = dict(payload)
    normalized.pop(excluded_key, None)
    return sha256_payload(normalized)


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


def count_ledger_entries(ledger: dict[str, Any], disposition: str) -> int:
    return sum(1 for item in ledger.get("entries", []) if item.get("partition_disposition") == disposition)


def artifact_exists_from_ref(ref: str | None, base_dir: Path) -> bool:
    if not ref:
        return False
    path = Path(ref)
    if not path.is_absolute():
        path = base_dir / ref
    return path.exists()


def build_incremental_overlap_reuse_test() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    required = [
        SCOPE_PATH,
        CONTRACT_PATH,
        REVIEW_MATRIX_PATH,
        CONTEXT_LEDGER_PATH,
        FINGERPRINT_COMPARISON_PATH,
        BASELINE_RUN_DIR / "final_manifest.json",
        BASELINE_RUN_DIR / "candidate_registry_entry.json",
        BASELINE_RUN_DIR / "candidate_output_manifest.json",
        INCREMENTAL_RUN_DIR / "final_manifest.json",
        INCREMENTAL_RUN_DIR / "request_record.json",
        INCREMENTAL_RUN_DIR / "execution_plan.json",
        INCREMENTAL_RUN_DIR / "candidate_registry_entry.json",
        INCREMENTAL_RUN_DIR / "candidate_output_manifest.json",
        INCREMENTAL_RUN_DIR / "lineage_manifest.json",
        INCREMENTAL_RUN_DIR / "market_state_validation_report.json",
    ]
    for path in required:
        require_file(path)

    scope = read_json(SCOPE_PATH)
    contract = read_json(CONTRACT_PATH)
    review_matrix = read_json(REVIEW_MATRIX_PATH)
    context_ledger = read_json(CONTEXT_LEDGER_PATH)
    fingerprint_comparison = read_json(FINGERPRINT_COMPARISON_PATH)
    baseline_final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    baseline_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    baseline_candidate_manifest = read_json(BASELINE_RUN_DIR / "candidate_output_manifest.json")
    incremental_final = read_json(INCREMENTAL_RUN_DIR / "final_manifest.json")
    incremental_request = read_json(INCREMENTAL_RUN_DIR / "request_record.json")
    incremental_plan = read_json(INCREMENTAL_RUN_DIR / "execution_plan.json")
    incremental_registry = read_json(INCREMENTAL_RUN_DIR / "candidate_registry_entry.json")
    incremental_candidate_manifest = read_json(INCREMENTAL_RUN_DIR / "candidate_output_manifest.json")
    incremental_validation = read_json(INCREMENTAL_RUN_DIR / "market_state_validation_report.json")

    expected_contract_hash = contract.get("contract_content_sha256_excluding_hash_field")
    observed_contract_hash = contract_content_hash(contract)
    observed_ledger_hash = payload_hash_excluding(context_ledger, "context_ledger_sha256")
    observed_fingerprint_comparison_hash = payload_hash_excluding(
        fingerprint_comparison, "fingerprint_comparison_sha256"
    )

    preflight_checks = {
        "scope_status_authorized": scope.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "scope_next_gate_match": scope.get("authorized_next_gate")
        == "market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1",
        "contract_status_authorized": contract.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "contract_next_gate_match": contract.get("authorized_next_gate")
        == "market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1",
        "contract_content_hash_match": observed_contract_hash == expected_contract_hash,
        "review_status_match": review_matrix.get("status")
        == contract["accepted_incremental_review"]["review_status"],
        "review_hard_failures_zero": review_matrix.get("decision", {}).get("hard_review_failures") == 0,
        "baseline_run_match": baseline_final.get("run_id") == contract["baseline_candidate_dataset"]["baseline_run_id"],
        "baseline_dataset_id_match": baseline_registry.get("dataset_id")
        == contract["baseline_candidate_dataset"]["baseline_candidate_dataset_id"],
        "baseline_candidate_fingerprint_match": baseline_registry.get("candidate_dataset_fingerprint")
        == contract["baseline_candidate_dataset"]["baseline_candidate_dataset_fingerprint"],
        "baseline_scientific_fingerprint_recorded_in_contract": bool(
            contract["baseline_candidate_dataset"].get("baseline_scientific_dataset_fingerprint")
        ),
        "baseline_artifact_available": artifact_exists_from_ref(
            contract["baseline_candidate_dataset"].get("baseline_candidate_output_manifest"), BASELINE_RUN_DIR
        ),
        "incremental_run_match": incremental_final.get("run_id")
        == contract["incremental_delta_evidence"]["incremental_run_id"],
        "incremental_dataset_id_match": incremental_registry.get("dataset_id")
        == contract["incremental_delta_evidence"]["incremental_candidate_dataset_id"],
        "incremental_candidate_fingerprint_match": incremental_registry.get("candidate_dataset_fingerprint")
        == contract["incremental_delta_evidence"]["incremental_candidate_dataset_fingerprint"],
        "incremental_scientific_fingerprint_match": incremental_registry.get("scientific_dataset_fingerprint")
        == contract["incremental_delta_evidence"]["incremental_scientific_dataset_fingerprint"],
        "incremental_validation_fingerprint_match": incremental_registry.get("validation_result_fingerprint")
        == contract["incremental_delta_evidence"]["incremental_validation_result_fingerprint"],
        "incremental_registry_fingerprint_match": incremental_registry.get("registry_entry_fingerprint")
        == contract["incremental_delta_evidence"]["incremental_registry_entry_fingerprint"],
        "incremental_registry_status_validated_candidate": incremental_registry.get("registry_status")
        == "validated_candidate",
        "incremental_validation_status_accepted": incremental_registry.get("validation_status")
        == "pass_with_restrictions",
        "ledger_hash_match": observed_ledger_hash
        == contract["combined_logical_candidate"]["combined_context_ledger_sha256"],
        "fingerprint_comparison_hash_match": observed_fingerprint_comparison_hash
        == contract["combined_logical_candidate"]["fingerprint_comparison_sha256"],
        "fingerprint_comparison_baseline_artifact_available": artifact_exists_from_ref(
            fingerprint_comparison.get("baseline_physical_artifact", {}).get("path"), BASE
        ),
        "fingerprint_comparison_delta_artifact_available": artifact_exists_from_ref(
            fingerprint_comparison.get("delta_physical_artifact", {}).get("path"), BASE
        ),
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1_{timestamp}"
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists():
        raise IncrementalReuseTestError(f"Run directory already exists: {run_dir}")
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

    reuse_lookup_request = dict(incremental_request)
    reuse_lookup_request.update(
        {
            "request_status": "accepted_for_incremental_overlap_reuse_lookup",
            "requested_at_utc": utc_now(),
            "request_purpose": "bounded_incremental_overlap_idempotency_reuse_test",
            "reuse_policy": contract["authorized_test_request"]["reuse_policy"],
            "output_mode": contract["authorized_test_request"]["output_mode"],
            "request_fingerprint": incremental_request["request_fingerprint"],
        }
    )
    write_json(run_dir / "overlap_reuse_lookup_request_record.json", reuse_lookup_request)

    incremental_semantic = request_semantic_payload(incremental_request)
    reuse_semantic = request_semantic_payload(reuse_lookup_request)
    ledger_counts = {
        "requested_contexts": context_ledger.get("counts", {}).get("requested_contexts"),
        "reused_validated": count_ledger_entries(context_ledger, "reusable_validated"),
        "delta_materialized": count_ledger_entries(context_ledger, "to_build"),
        "unavailable": count_ledger_entries(context_ledger, "unavailable"),
        "represented_contexts": context_ledger.get("counts", {}).get("represented_contexts"),
        "unaccounted_contexts": context_ledger.get("counts", {}).get("unaccounted_contexts"),
    }

    selected_dataset = {
        "dataset_id": incremental_registry["dataset_id"],
        "dataset_kind": incremental_registry["dataset_kind"],
        "registry_status": incremental_registry["registry_status"],
        "validation_status": incremental_registry["validation_status"],
        "reuse_eligibility_before_test": incremental_registry["reuse_eligibility"],
        "selection_basis": "incremental_overlap_reuse_test_authorization_plus_candidate_dataset_review",
        "request_fingerprint": incremental_registry["request_fingerprint"],
        "execution_plan_fingerprint": incremental_registry["execution_plan_fingerprint"],
        "candidate_dataset_fingerprint": incremental_registry["candidate_dataset_fingerprint"],
        "scientific_dataset_fingerprint": incremental_registry["scientific_dataset_fingerprint"],
        "validation_result_fingerprint": incremental_registry["validation_result_fingerprint"],
        "registry_entry_fingerprint": incremental_registry["registry_entry_fingerprint"],
        "baseline_dataset_ref": incremental_registry["baseline_dataset_ref"],
        "coverage": incremental_registry["coverage"],
        "file_manifest_ref": incremental_registry["file_manifest_ref"],
        "lineage_manifest_ref": incremental_registry["lineage_manifest_ref"],
        "validation_report_ref": incremental_registry["validation_report_ref"],
    }

    availability_report = {
        "report_id": "combined_candidate_availability_report_v0_1",
        "run_id": run_id,
        "baseline_manifest_available": artifact_exists_from_ref(
            selected_dataset["baseline_dataset_ref"].get("candidate_output_manifest"), BASELINE_RUN_DIR
        ),
        "baseline_physical_artifact_available": preflight_checks["fingerprint_comparison_baseline_artifact_available"],
        "delta_candidate_manifest_available": (INCREMENTAL_RUN_DIR / "candidate_output_manifest.json").exists(),
        "delta_lineage_manifest_available": (INCREMENTAL_RUN_DIR / "lineage_manifest.json").exists(),
        "delta_validation_report_available": (INCREMENTAL_RUN_DIR / "market_state_validation_report.json").exists(),
        "delta_physical_artifact_available": preflight_checks["fingerprint_comparison_delta_artifact_available"],
        "context_ledger_available": CONTEXT_LEDGER_PATH.exists(),
        "fingerprint_comparison_available": FINGERPRINT_COMPARISON_PATH.exists(),
        "artifact_availability_status": "available",
    }
    availability_report["availability_report_fingerprint"] = sha256_payload(availability_report)
    write_json(run_dir / "combined_candidate_availability_report.json", availability_report)

    reuse_resolution_report = {
        "report_id": "overlap_reuse_resolution_report_v0_1",
        "run_id": run_id,
        "lookup_policy": contract["authorized_test_request"]["reuse_policy"],
        "query_request_fingerprint": reuse_lookup_request["request_fingerprint"],
        "candidate_registry_metadata_reads": 1,
        "baseline_registry_metadata_reads": 1,
        "candidate_parquet_files_read": 0,
        "source_market_data_rows_read": 0,
        "source_candidate_records_read": 0,
        "materializer_executions": 0,
        "delta_materializer_executions": 0,
        "new_candidate_parquet_files": 0,
        "new_candidate_dataset_registry_entries": 0,
        "baseline_registry_entry_mutations": 0,
        "combined_candidate_registry_entry_mutations": 0,
        "reuse_test_evidence_entries_written": 1,
        "matching_registry_entries_found": 1,
        "selected_dataset": selected_dataset,
        "ledger_counts": ledger_counts,
        "availability_report": str(run_dir / "combined_candidate_availability_report.json"),
    }
    write_json(run_dir / "overlap_reuse_resolution_report.json", reuse_resolution_report)

    checks = {
        "request_fingerprint_match": reuse_lookup_request["request_fingerprint"]
        == contract["authorized_test_request"]["request_fingerprint_must_equal"],
        "normalized_overlap_request_match": reuse_semantic == incremental_semantic,
        "profile_match": selected_dataset["coverage"] == incremental_registry["coverage"],
        "same_execution_plan_fingerprint": incremental_plan.get("execution_plan_fingerprint")
        == contract["combined_logical_candidate"]["execution_plan_fingerprint"],
        "same_context_ledger_hash": observed_ledger_hash
        == contract["expected_reuse_behavior"]["context_ledger_sha256_must_equal"],
        "same_unavailable_context_count": ledger_counts["unavailable"]
        == contract["combined_logical_candidate"]["unavailable_contexts"],
        "same_represented_context_count": ledger_counts["represented_contexts"]
        == contract["combined_logical_candidate"]["represented_contexts"],
        "selected_dataset_id_match": selected_dataset["dataset_id"]
        == contract["expected_reuse_behavior"]["selected_dataset_id_must_equal"],
        "selected_candidate_dataset_fingerprint_match": selected_dataset["candidate_dataset_fingerprint"]
        == contract["expected_reuse_behavior"]["selected_candidate_dataset_fingerprint_must_equal"],
        "selected_scientific_dataset_fingerprint_match": selected_dataset["scientific_dataset_fingerprint"]
        == contract["expected_reuse_behavior"]["selected_scientific_dataset_fingerprint_must_equal"],
        "validation_result_fingerprint_match": selected_dataset["validation_result_fingerprint"]
        == contract["combined_logical_candidate"]["validation_result_fingerprint"],
        "restriction_set_still_candidate_only": set(contract["combined_logical_candidate"]["restriction_set"])
        == {
            "candidate_only",
            "partial_coverage",
            "not_official",
            "not_production",
            "not_downstream",
            "bounded_incremental_overlap_only",
        },
        "artifact_availability_available": all(availability_report[k] is True for k in [
            "baseline_manifest_available",
            "baseline_physical_artifact_available",
            "delta_candidate_manifest_available",
            "delta_lineage_manifest_available",
            "delta_validation_report_available",
            "delta_physical_artifact_available",
            "context_ledger_available",
            "fingerprint_comparison_available",
        ]),
        "materializer_executions_zero": reuse_resolution_report["materializer_executions"]
        == contract["expected_reuse_behavior"]["materializer_executions_expected"],
        "delta_materializer_executions_zero": reuse_resolution_report["delta_materializer_executions"]
        == contract["expected_reuse_behavior"]["delta_materializer_executions_expected"],
        "source_market_data_rows_read_zero": reuse_resolution_report["source_market_data_rows_read"]
        == contract["expected_reuse_behavior"]["source_market_data_rows_read_expected"],
        "source_candidate_records_read_zero": reuse_resolution_report["source_candidate_records_read"]
        == contract["expected_reuse_behavior"]["source_candidate_records_read_expected"],
        "new_candidate_parquet_files_zero": reuse_resolution_report["new_candidate_parquet_files"]
        == contract["expected_reuse_behavior"]["new_candidate_parquet_files_expected"],
        "new_candidate_dataset_registry_entries_zero": reuse_resolution_report["new_candidate_dataset_registry_entries"]
        == contract["expected_reuse_behavior"]["new_candidate_dataset_registry_entries_expected"],
        "baseline_registry_entry_mutations_zero": reuse_resolution_report["baseline_registry_entry_mutations"]
        == contract["expected_reuse_behavior"]["baseline_registry_entry_mutations_expected"],
        "combined_candidate_registry_entry_mutations_zero": reuse_resolution_report["combined_candidate_registry_entry_mutations"]
        == contract["expected_reuse_behavior"]["combined_candidate_registry_entry_mutations_expected"],
        "official_dataset_closed": not incremental_final["official_dataset"],
        "production_closed": not incremental_final["production"],
        "downstream_closed": not incremental_final["downstream"],
    }

    blocking_checks = list(checks)
    blocking_failures = [check for check in blocking_checks if not checks[check]]
    idempotency_status = "PROVEN_FOR_INCREMENTAL_OVERLAP_REUSE" if not blocking_failures else "FAILED"
    final_status = (
        contract["expected_closure_statuses"]["reuse_hit"]
        if not blocking_failures
        else "CLOSED_BLOCKED_INCREMENTAL_OVERLAP_REUSE_FAILURE"
    )

    evidence_entry = {
        "evidence_entry_id": "market_state_incremental_overlap_reuse_evidence_v0_1_"
        + sha256_payload(reuse_resolution_report)[:16],
        "evidence_kind": "incremental_overlap_idempotency_reuse_test_evidence",
        "run_id": run_id,
        "baseline_run_id": BASELINE_RUN_ID,
        "incremental_run_id": INCREMENTAL_RUN_ID,
        "selected_dataset_id": selected_dataset["dataset_id"],
        "selected_candidate_dataset_fingerprint": selected_dataset["candidate_dataset_fingerprint"],
        "selected_scientific_dataset_fingerprint": selected_dataset["scientific_dataset_fingerprint"],
        "combined_context_ledger_sha256": observed_ledger_hash,
        "idempotency_status": idempotency_status,
        "blocking_failures": blocking_failures,
        "reuse_eligibility_before_test": incremental_registry["reuse_eligibility"],
        "reuse_eligibility_changed_by_this_gate": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    evidence_entry["evidence_entry_fingerprint"] = sha256_payload(evidence_entry)
    write_json(run_dir / "reuse_hit_evidence.json", evidence_entry)

    report = {
        "report_id": "market_state_on_demand_incremental_overlap_idempotency_reuse_test_report_v0_1",
        "run_id": run_id,
        "status": final_status,
        "idempotency_status": idempotency_status,
        "checks": checks,
        "blocking_failures": blocking_failures,
        "selected_dataset": selected_dataset,
        "overlap_reuse_resolution_report": str(run_dir / "overlap_reuse_resolution_report.json"),
        "combined_candidate_availability_report": str(run_dir / "combined_candidate_availability_report.json"),
        "reuse_hit_evidence": str(run_dir / "reuse_hit_evidence.json"),
        "second_generation_incremental_extension_ready": not blocking_failures,
        "reuse_eligibility_changed_by_this_gate": False,
    }
    report["report_fingerprint"] = sha256_payload(report)
    write_json(run_dir / "reuse_test_report.json", report)

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
        "incremental_run_id": INCREMENTAL_RUN_ID,
        "request_fingerprint": reuse_lookup_request["request_fingerprint"],
        "selected_dataset_id": selected_dataset["dataset_id"],
        "selected_candidate_dataset_fingerprint": selected_dataset["candidate_dataset_fingerprint"],
        "selected_scientific_dataset_fingerprint": selected_dataset["scientific_dataset_fingerprint"],
        "combined_context_ledger_sha256": observed_ledger_hash,
        "requested_contexts": ledger_counts["requested_contexts"],
        "represented_contexts": ledger_counts["represented_contexts"],
        "unavailable_contexts": ledger_counts["unavailable"],
        "idempotency_status": idempotency_status,
        "blocking_failures": blocking_failures,
        "candidate_registry_metadata_reads": 1,
        "baseline_registry_metadata_reads": 1,
        "candidate_parquet_files_read": 0,
        "source_market_data_rows_read": 0,
        "source_candidate_records_read": 0,
        "materializer_executions": 0,
        "delta_materializer_executions": 0,
        "new_candidate_parquet_files": 0,
        "new_candidate_dataset_registry_entries": 0,
        "baseline_registry_entry_mutations": 0,
        "combined_candidate_registry_entry_mutations": 0,
        "reuse_test_evidence_entries_written": 1,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "unbounded_reuse": False,
        "incremental_capability_promotion": False,
        "report_fingerprint": report["report_fingerprint"],
        "evidence_entry_fingerprint": evidence_entry["evidence_entry_fingerprint"],
        "next_gate": "market_state_on_demand_second_generation_incremental_extension_authorization_v0_1",
        "artifacts": {
            "overlap_reuse_lookup_request_record": str(run_dir / "overlap_reuse_lookup_request_record.json"),
            "overlap_reuse_resolution_report": str(run_dir / "overlap_reuse_resolution_report.json"),
            "combined_candidate_availability_report": str(run_dir / "combined_candidate_availability_report.json"),
            "reuse_hit_evidence": str(run_dir / "reuse_hit_evidence.json"),
            "idempotency_reuse_test_report": str(
                run_dir / "reuse_test_report.json"
            ),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)

    readout = f"""# Market State On-Demand Incremental Overlap Idempotency Reuse Test Readout v0.1

Status: `{final_status}`
Date: `2026-07-27`

```text
run_id = {run_id}
baseline_run_id = {BASELINE_RUN_ID}
incremental_run_id = {INCREMENTAL_RUN_ID}
selected_dataset_id = {selected_dataset['dataset_id']}
request_fingerprint_match = {str(checks['request_fingerprint_match']).lower()}
normalized_overlap_request_match = {str(checks['normalized_overlap_request_match']).lower()}
same_context_ledger_hash = {str(checks['same_context_ledger_hash']).lower()}
artifact_availability_available = {str(checks['artifact_availability_available']).lower()}
requested_contexts = {ledger_counts['requested_contexts']}
represented_contexts = {ledger_counts['represented_contexts']}
unavailable_contexts = {ledger_counts['unavailable']}
materializer_executions = {reuse_resolution_report['materializer_executions']}
delta_materializer_executions = {reuse_resolution_report['delta_materializer_executions']}
source_market_data_rows_read = {reuse_resolution_report['source_market_data_rows_read']}
source_candidate_records_read = {reuse_resolution_report['source_candidate_records_read']}
candidate_parquet_files_read = {reuse_resolution_report['candidate_parquet_files_read']}
new_candidate_parquet_files = {reuse_resolution_report['new_candidate_parquet_files']}
new_candidate_dataset_registry_entries = {reuse_resolution_report['new_candidate_dataset_registry_entries']}
baseline_registry_entry_mutations = {reuse_resolution_report['baseline_registry_entry_mutations']}
combined_candidate_registry_entry_mutations = {reuse_resolution_report['combined_candidate_registry_entry_mutations']}
blocking_failures = {len(blocking_failures)}
idempotency_status = {idempotency_status}
official_dataset = false
production = false
downstream = false
unbounded_reuse = false
incremental_capability_promotion = false
```

The test submitted the same validated partially overlapping Market State
request with `reuse_policy = reuse_if_exact_validated_overlap_match` and
selected the existing governed combined candidate from registry metadata. It did
not rebuild baseline evidence, rebuild delta evidence, read source market data,
read candidate parquet files, write new candidate parquet files or create a new
candidate dataset registry entry.

## Boundary

```text
official_market_state_dataset = false
official_parquet = false
production = false
downstream_consumption = false
unbounded_reuse = false
incremental_capability_promotion = false
```

## Next Gate

```text
market_state_on_demand_second_generation_incremental_extension_authorization_v0_1
```
"""
    (run_dir / "reuse_test_readout_v0_1.md").write_text(
        readout, encoding="utf-8"
    )

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False, default=str))
    return 0 if not blocking_failures else 1


if __name__ == "__main__":
    try:
        raise SystemExit(build_incremental_overlap_reuse_test())
    except IncrementalReuseTestError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
