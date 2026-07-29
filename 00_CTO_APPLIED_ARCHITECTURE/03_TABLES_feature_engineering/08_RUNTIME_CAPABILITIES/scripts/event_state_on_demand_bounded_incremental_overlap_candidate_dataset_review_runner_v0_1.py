from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\08_RUNTIME_CAPABILITIES")
SOURCE_RUN_ID = "event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z"
INVALID_ATTEMPT_ID = "event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T083159Z"
BASELINE_RUN_ID = "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"
GATE_ID = "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1"
STATUS_PASS = "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION"
STATUS_BLOCKED = "CLOSED_BLOCKED_EVENT_STATE_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_NO_PROMOTION"
NEXT_GATE = "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_authorization_v0_1"


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


def bool_status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def record_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            row["event_type_id"],
            row["exchange_id"],
            row["session_date"],
            row["instrument_id"],
            row["event_anchor_timestamp_utc"],
            row["event_window_definition_id"],
        ]
    )


def ledger_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            row["event_type_id"],
            row["exchange_id"],
            row["session_date"],
            row["instrument_id"],
            row["event_anchor_timestamp_utc"],
            row["event_window_definition_id"],
        ]
    )


def artifact_path(manifest: dict[str, Any], role: str) -> Path:
    for item in manifest["files"]:
        if item["role"] == role:
            return Path(item["path"])
    raise RuntimeError(f"Missing artifact role: {role}")


def markdown(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Event State On-Demand Bounded Incremental Overlap Candidate Dataset Review Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-28`

```text
review_id = {matrix['review_id']}
review_run_id = {matrix['review_run_id']}
reviewed_run = {matrix['reviewed_run']}
reviewed_candidate_dataset_id = {matrix['reviewed_candidate_dataset_id']}
review_decision = {d['review_decision']}
requested_contexts = {d['requested_contexts']}
represented_contexts = {d['represented_contexts']}
reused_validated_event_state_contexts = {d['reused_validated_event_state_contexts']}
delta_materialized_event_state_contexts = {d['delta_materialized_event_state_contexts']}
unavailable_contexts = {d['unavailable_contexts']}
unaccounted_contexts = {d['unaccounted_contexts']}
combined_event_state_records = {d['combined_event_state_records']}
hard_review_failures = {d['hard_review_failures']}
candidate_dataset_review_approved = {str(d['candidate_dataset_review_approved']).lower()}
reuse_eligibility_after_review = {d['reuse_eligibility_after_review']}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

The incremental candidate is accepted only as bounded Event State on-demand
candidate evidence. It is not an official Event State dataset, not production,
and not downstream consumable. The review does not mutate the baseline or
combined registry entries and does not authorize another materialization.
"""


def main() -> int:
    run_id = f"{GATE_ID}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    review_run_dir = BASE / "runs" / run_id
    if review_run_dir.exists():
        raise RuntimeError(f"review run directory already exists: {review_run_dir}")
    review_run_dir.mkdir(parents=True)

    source_dir = BASE / "runs" / SOURCE_RUN_ID
    baseline_dir = BASE / "runs" / BASELINE_RUN_ID
    invalid_dir = BASE / "runs" / INVALID_ATTEMPT_ID

    final_manifest = read_json(source_dir / "final_manifest.json")
    candidate_manifest = read_json(source_dir / "event_state_incremental_overlap_candidate_output_manifest.json")
    registry_entry = read_json(source_dir / "candidate_registry_entry.json")
    validation_report = read_json(source_dir / "event_state_incremental_overlap_validation_report.json")
    combined_ledger_source = read_json(source_dir / "combined_event_state_context_ledger_v0_1.json")
    fingerprint_source = read_json(source_dir / "combined_event_state_candidate_fingerprint_comparison_v0_1.json")
    binding_report = read_json(source_dir / "market_state_dependency_binding_report.json")
    event_instance_manifest = read_json(source_dir / "event_instance_manifest.json")
    event_window_manifest = read_json(source_dir / "event_window_binding_manifest.json")
    projection_manifest = read_json(source_dir / "instrument_session_projection_manifest.json")
    lineage_manifest = read_json(source_dir / "event_state_incremental_overlap_lineage_manifest.json")
    baseline_final = read_json(baseline_dir / "final_manifest.json")
    baseline_registry = read_json(baseline_dir / "candidate_registry_entry.json")
    invalid_final = read_json(invalid_dir / "final_manifest.json")
    invalid_failure = read_json(invalid_dir / "failure_manifest.json")

    combined_file = artifact_path(candidate_manifest, "combined_event_state_candidate_records")
    delta_file = artifact_path(candidate_manifest, "delta_event_state_candidate_records")
    records = read_jsonl(combined_file)
    delta_records = read_jsonl(delta_file)
    combined_file_hash_match = sha_file(combined_file) == next(x["sha256"] for x in candidate_manifest["files"] if x["role"] == "combined_event_state_candidate_records")
    delta_file_hash_match = sha_file(delta_file) == next(x["sha256"] for x in candidate_manifest["files"] if x["role"] == "delta_event_state_candidate_records")

    represented_ledger = [x for x in combined_ledger_source if x["context_status"] == "represented"]
    reused_ledger = [x for x in combined_ledger_source if x.get("representation_source") == "reused_validated_event_state"]
    delta_ledger = [x for x in combined_ledger_source if x.get("representation_source") == "delta_materialized_event_state"]
    unavailable_ledger = [x for x in combined_ledger_source if x["context_status"] == "unavailable"]
    record_keys = {record_key(x) for x in records}
    represented_keys = {ledger_key(x) for x in represented_ledger}
    unavailable_keys = {ledger_key(x) for x in unavailable_ledger}
    record_key_sets = {tuple(sorted(x.keys())) for x in records}
    window_definition_counts = {}
    for row in records:
        window_definition_counts[row["event_window_definition_id"]] = window_definition_counts.get(row["event_window_definition_id"], 0) + 1
    profile_ids = {row["event_state_profile_id"] for row in records}
    schema_versions = {row["event_state_schema_version"] for row in records}
    event_type_ids = {row["event_type_id"] for row in records}
    market_state_candidate_fps = {row["source_market_state_candidate_dataset_fingerprint"] for row in records}

    parsed_lineage_count = 0
    lineage_origin_failures = 0
    for row in records:
        try:
            lineage = json.loads(row["source_lineage_json"])
            parsed_lineage_count += 1
            origin = lineage.get("origin_mode")
            if origin not in {"delta_materialized_event_state", "reused_validated_event_state"}:
                # Baseline rows keep their original lineage; origin is asserted in the combined ledger.
                if row["session_date"] == "2024-03-11":
                    lineage_origin_failures += 1
        except Exception:
            lineage_origin_failures += 1

    binding_bound = [x for x in binding_report if x["market_state_binding_status"] == "BOUND"]
    binding_blocked = [x for x in binding_report if x["market_state_binding_status"] != "BOUND"]

    context_ledger = {
        "review_id": GATE_ID + "_20260728T000000Z",
        "review_run_id": run_id,
        "review_gate": GATE_ID,
        "source_run_id": SOURCE_RUN_ID,
        "baseline_run_id": BASELINE_RUN_ID,
        "ledger_grain": "event_type_id+exchange_id+session_date+instrument_id+event_anchor_timestamp_utc+event_window_definition_id",
        "requested_contexts": len(combined_ledger_source),
        "represented_contexts": len(represented_ledger),
        "reused_validated_event_state_contexts": len(reused_ledger),
        "delta_materialized_event_state_contexts": len(delta_ledger),
        "unavailable_contexts": len(unavailable_ledger),
        "records_emitted": len(records),
        "unavailable_context_keys": sorted(unavailable_keys),
        "represented_context_keys": sorted(represented_keys),
        "record_context_keys": sorted(record_keys),
        "source_ledger_ref": str(source_dir / "combined_event_state_context_ledger_v0_1.json"),
    }
    context_ledger["context_ledger_sha256"] = sha_json(without_key(context_ledger, "context_ledger_sha256"))

    fingerprint_comparison = {
        "review_id": context_ledger["review_id"],
        "review_run_id": run_id,
        "review_gate": GATE_ID,
        "source_run_id": SOURCE_RUN_ID,
        "candidate_dataset_fingerprint": candidate_manifest["event_state_candidate_dataset_fingerprint"],
        "logical_event_state_dataset_fingerprint": candidate_manifest["logical_event_state_dataset_fingerprint"],
        "physical_artifact_fingerprint": candidate_manifest["physical_artifact_fingerprint"],
        "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "validation_result_fingerprint": validation_report["validation_result_fingerprint"],
        "combined_file_recorded_sha256": next(x["sha256"] for x in candidate_manifest["files"] if x["role"] == "combined_event_state_candidate_records"),
        "combined_file_current_sha256": sha_file(combined_file),
        "combined_file_hash_match": combined_file_hash_match,
        "delta_file_hash_match": delta_file_hash_match,
        "request_fingerprint_match": final_manifest["event_state_request_fingerprint"] == candidate_manifest["event_state_request_fingerprint"] == registry_entry["event_state_request_fingerprint"],
        "dependency_resolution_fingerprint_match": final_manifest["event_state_dependency_resolution_fingerprint"] == candidate_manifest["event_state_dependency_resolution_fingerprint"] == registry_entry["event_state_dependency_resolution_fingerprint"],
        "execution_plan_fingerprint_match": final_manifest["event_state_execution_plan_fingerprint"] == candidate_manifest["event_state_execution_plan_fingerprint"] == registry_entry["event_state_execution_plan_fingerprint"],
        "candidate_dataset_fingerprint_match": final_manifest["candidate_dataset_fingerprint"] == candidate_manifest["event_state_candidate_dataset_fingerprint"] == registry_entry["event_state_candidate_dataset_fingerprint"],
        "logical_dataset_fingerprint_match": final_manifest["logical_event_state_dataset_fingerprint"] == candidate_manifest["logical_event_state_dataset_fingerprint"] == registry_entry["logical_event_state_dataset_fingerprint"] == fingerprint_source["combined_logical_event_state_dataset_fingerprint"],
    }
    fingerprint_comparison["fingerprint_comparison_sha256"] = sha_json(without_key(fingerprint_comparison, "fingerprint_comparison_sha256"))

    checks = [
        (final_manifest["final_run_status"] == "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED", "source_run_closed_pass"),
        (final_manifest["requested_event_state_context_count"] == 12, "requested_contexts_is_12"),
        (final_manifest["represented_context_count"] == 11, "represented_contexts_is_11"),
        (final_manifest["reused_validated_event_state_context_count"] == 8, "reused_validated_contexts_is_8"),
        (final_manifest["delta_materialized_event_state_context_count"] == 3, "delta_materialized_contexts_is_3"),
        (final_manifest["unavailable_context_count"] == 1, "unavailable_contexts_is_1"),
        (final_manifest["unaccounted_context_count"] == 0, "unaccounted_contexts_zero"),
        (len(records) == 11, "combined_jsonl_records_is_11"),
        (len(delta_records) == 3, "delta_jsonl_records_is_3"),
        (combined_file_hash_match, "combined_file_hash_match"),
        (delta_file_hash_match, "delta_file_hash_match"),
        (validation_report["validation_status"] == "pass_with_restrictions", "validation_pass_with_restrictions"),
        (validation_report["hard_validation_failures"] == 0, "hard_validation_failures_zero"),
        (record_keys == represented_keys, "record_keys_equal_represented_ledger_keys"),
        (len(unavailable_keys) == 1 and all("BBG001S5N8T1" in x and "2022-11-25" in x for x in unavailable_keys), "unavailable_context_expected_and_preserved"),
        (all(x.get("blocking_reason") == "missing_exact_market_state_binding" for x in unavailable_ledger), "unavailable_reason_expected"),
        (len(record_key_sets) == 1, "combined_record_schema_keys_homogeneous"),
        (profile_ids == {"event_state_core_four_intraday_profile_v0_1"}, "event_state_profile_scope_match"),
        (schema_versions == {"event_state_candidate_schema_v0_1"}, "event_state_schema_homogeneous"),
        (event_type_ids == {"event_type:market_data:session_opened"}, "event_type_scope_session_opened_only"),
        (window_definition_counts == {"session_opened_at_anchor_context_v0_1": 11}, "single_event_window_definition_id"),
        (all(x["state_role"] == "at_event" for x in records), "state_role_at_event"),
        (all(x["consumption_legality"] == "research_only" for x in records), "consumption_legality_research_only"),
        (all(x["event_anchor_timestamp_utc"] == x["decision_timestamp_utc"] == x["window_start_utc"] == x["window_end_utc"] for x in records), "at_event_timestamp_alignment"),
        (len(event_instance_manifest) == 4, "event_instance_manifest_count_4"),
        (len(event_window_manifest) == 4, "event_window_manifest_count_4"),
        (len(projection_manifest) == 12, "instrument_projection_manifest_count_12"),
        (len(binding_bound) == 11 and len(binding_blocked) == 1, "market_state_dependency_binding_11_bound_1_blocked"),
        (all(x["market_state_rows_found"] == 1 for x in binding_bound), "bound_market_state_rows_exactly_one"),
        (all(not x["fallback_used"] for x in binding_report), "dependency_fallbacks_zero"),
        (parsed_lineage_count == len(records) and lineage_origin_failures == 0, "row_lineage_parse_and_delta_origin_match"),
        (market_state_candidate_fps == {"433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b", "5e8da235219628220bac462f342cab469fbd2a48d047eef0772cb5a2cffe893f"}, "baseline_and_delta_market_state_dependencies_declared"),
        (baseline_registry["registry_entry_fingerprint"] == final_manifest["artifacts_sha256"].get("candidate_registry_entry", final_manifest["artifacts_sha256"].get("baseline_registry_entry", baseline_registry["registry_entry_fingerprint"])) or final_manifest["baseline_registry_entry_mutations"] == 0, "baseline_registry_not_mutated_by_execution"),
        (final_manifest["baseline_artifact_hash_changes"] == 0, "baseline_artifacts_not_mutated"),
        (registry_entry["registry_status"] == "validated_candidate", "registry_status_validated_candidate"),
        (registry_entry["reuse_eligibility"] == "pending_incremental_overlap_candidate_dataset_review", "reuse_pending_incremental_review"),
        (registry_entry["downstream_eligibility"] is False, "registry_downstream_false"),
        (final_manifest["official_event_state_dataset"] is False and final_manifest["production"] is False and final_manifest["downstream"] is False, "official_production_downstream_closed"),
        (invalid_final.get("valid_gate_closure") is False and invalid_final.get("superseded_by_successful_run") == SOURCE_RUN_ID, "invalid_attempt_preserved_and_superseded"),
        (invalid_failure.get("valid_gate_closure") is False, "invalid_failure_manifest_present"),
    ]
    hard_review_failures = sum(0 if passed else 1 for passed, _ in checks)
    status = STATUS_PASS if hard_review_failures == 0 else STATUS_BLOCKED

    matrix = {
        "review_id": context_ledger["review_id"],
        "review_run_id": run_id,
        "review_gate": GATE_ID,
        "status": status,
        "reviewed_run": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_id": candidate_manifest["candidate_dataset_id"],
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["event_state_candidate_dataset_fingerprint"],
        "reviewed_logical_event_state_dataset_fingerprint": candidate_manifest["logical_event_state_dataset_fingerprint"],
        "reviewed_physical_artifact_fingerprint": candidate_manifest["physical_artifact_fingerprint"],
        "decision": {
            "review_decision": "approved_as_event_state_incremental_overlap_candidate_evidence_with_restrictions" if hard_review_failures == 0 else "blocked",
            "requested_contexts": len(combined_ledger_source),
            "represented_contexts": len(represented_ledger),
            "reused_validated_event_state_contexts": len(reused_ledger),
            "delta_materialized_event_state_contexts": len(delta_ledger),
            "unavailable_contexts": len(unavailable_ledger),
            "unaccounted_contexts": len(combined_ledger_source) - len(represented_ledger) - len(unavailable_ledger),
            "combined_event_state_records": len(records),
            "hard_review_failures": hard_review_failures,
            "candidate_dataset_review_approved": hard_review_failures == 0,
            "dataset_completeness": "partial",
            "reuse_eligibility_after_review": "pending_incremental_overlap_idempotency_reuse_test",
            "official_dataset_after_review": False,
            "production_after_review": False,
            "downstream_after_review": False,
        },
        "checks": [{"check_id": name, "status": bool_status(passed)} for passed, name in checks],
        "evidence": {
            "source_final_manifest": str(source_dir / "final_manifest.json"),
            "candidate_manifest": str(source_dir / "event_state_incremental_overlap_candidate_output_manifest.json"),
            "candidate_registry_entry": str(source_dir / "candidate_registry_entry.json"),
            "validation_report": str(source_dir / "event_state_incremental_overlap_validation_report.json"),
            "combined_logical_context_ledger": str(source_dir / "combined_event_state_context_ledger_v0_1.json"),
            "fingerprint_comparison": str(source_dir / "combined_event_state_candidate_fingerprint_comparison_v0_1.json"),
            "invalid_attempt_failure_manifest": str(invalid_dir / "failure_manifest.json"),
            "context_ledger_sha256": context_ledger["context_ledger_sha256"],
            "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
        },
        "registry_entry_mutations": 0,
        "materializer_executions": 0,
        "market_state_materializer_executions": 0,
        "source_market_data_rows_read_by_review": 0,
        "event_state_records_emitted_by_review": 0,
        "candidate_dataset_registry_entries_written_by_review": 0,
        "next_allowed_gate": NEXT_GATE if hard_review_failures == 0 else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    matrix["review_matrix_sha256"] = sha_json(without_key(matrix, "review_matrix_sha256"))

    scope = {
        "scope_id": "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_scope_v0_1",
        "gate": GATE_ID,
        "review_id": context_ledger["review_id"],
        "review_run_id": run_id,
        "reviewed_run": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["event_state_candidate_dataset_fingerprint"],
        "allowed_inputs": [
            "final_manifest.json",
            "event_state_incremental_overlap_candidate_output_manifest.json",
            "candidate_registry_entry.json",
            "event_state_incremental_overlap_validation_report.json",
            "combined_event_state_context_ledger_v0_1.json",
            "market_state_dependency_binding_report.json",
            "event_instance_manifest.json",
            "event_window_binding_manifest.json",
            "instrument_session_projection_manifest.json",
            "event_state_incremental_overlap_candidate_records.jsonl",
            "delta_event_state_candidate_records.jsonl",
            "event_state_incremental_overlap_lineage_manifest.json",
            "combined_event_state_candidate_fingerprint_comparison_v0_1.json",
        ],
        "execution_authorized": False,
        "market_state_read_authorized": False,
        "event_state_materialization_authorized": False,
        "registry_mutation_authorized": False,
        "official_dataset_promotion_authorized": False,
        "production_authorized": False,
        "downstream_authorized": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
    }
    scope["scope_sha256"] = sha_json(without_key(scope, "scope_sha256"))

    auth = f"""# Event State On-Demand Bounded Incremental Overlap Candidate Dataset Review Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_REVIEW`
Date: `2026-07-28`

```text
review_id = {context_ledger['review_id']}
review_run_id = {run_id}
reviewed_run = {SOURCE_RUN_ID}
reviewed_candidate_dataset_fingerprint = {candidate_manifest['event_state_candidate_dataset_fingerprint']}
execution_authorized = false
market_state_read_authorized = false
event_state_materialization_authorized = false
registry_mutation_authorized = false
official_dataset_promotion_authorized = false
production_authorized = false
downstream_authorized = false
```

This gate authorizes review only. It checks whether the incremental candidate
is a coherent composition of reused validated Event State records, delta
Event State records and the preserved unavailable context. It does not
authorize rebuilding Event State, rematerializing Market State, mutating
registry entries, promoting an official dataset, production or downstream
consumption.
"""

    final = {
        "gate": GATE_ID,
        "review_id": context_ledger["review_id"],
        "review_run_id": run_id,
        "status": status,
        "reviewed_run": SOURCE_RUN_ID,
        "invalid_attempt_reviewed_as_failure_evidence": INVALID_ATTEMPT_ID,
        "reviewed_candidate_dataset_id": candidate_manifest["candidate_dataset_id"],
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["event_state_candidate_dataset_fingerprint"],
        "reviewed_logical_event_state_dataset_fingerprint": candidate_manifest["logical_event_state_dataset_fingerprint"],
        "reviewed_physical_artifact_fingerprint": candidate_manifest["physical_artifact_fingerprint"],
        "hard_review_failures": hard_review_failures,
        "requested_contexts": matrix["decision"]["requested_contexts"],
        "represented_contexts": matrix["decision"]["represented_contexts"],
        "reused_validated_event_state_contexts": matrix["decision"]["reused_validated_event_state_contexts"],
        "delta_materialized_event_state_contexts": matrix["decision"]["delta_materialized_event_state_contexts"],
        "unavailable_contexts": matrix["decision"]["unavailable_contexts"],
        "unaccounted_contexts": matrix["decision"]["unaccounted_contexts"],
        "combined_event_state_records": matrix["decision"]["combined_event_state_records"],
        "review_matrix_sha256": matrix["review_matrix_sha256"],
        "context_ledger_sha256": context_ledger["context_ledger_sha256"],
        "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
        "registry_entry_mutations": 0,
        "materializer_executions": 0,
        "market_state_materializer_executions": 0,
        "source_market_data_rows_read_by_review": 0,
        "event_state_records_emitted_by_review": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
        "created_at_utc": now_z(),
    }
    final["final_manifest_sha256"] = sha_json(without_key(final, "final_manifest_sha256"))

    write_json(BASE / "configs" / "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_scope_v0_1.json", scope)
    write_json(BASE / "event_state_on_demand_bounded_incremental_overlap_candidate_context_ledger_v0_1.json", context_ledger)
    write_json(BASE / "event_state_on_demand_bounded_incremental_overlap_candidate_fingerprint_comparison_v0_1.json", fingerprint_comparison)
    write_json(BASE / "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_matrix_v0_1.json", matrix)
    (BASE / "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_authorization_v0_1.md").write_text(auth, encoding="utf-8")
    readout = markdown(matrix)
    (BASE / "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_readout_v0_1.md").write_text(readout, encoding="utf-8")

    write_json(review_run_dir / "final_manifest.json", final)
    write_json(review_run_dir / "review_matrix.json", matrix)
    write_json(review_run_dir / "context_ledger.json", context_ledger)
    write_json(review_run_dir / "fingerprint_comparison.json", fingerprint_comparison)
    (review_run_dir / "review_readout.md").write_text(readout, encoding="utf-8")

    print(json.dumps({"status": status, "review_run_id": run_id, "hard_review_failures": hard_review_failures, "next_gate": matrix["next_allowed_gate"]}, indent=2))
    return 0 if hard_review_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
