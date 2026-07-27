from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\08_RUNTIME_CAPABILITIES")
SOURCE_RUN_ID = "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"
SOURCE_RUN_DIR = BASE / "runs" / SOURCE_RUN_ID
FAILED_ATTEMPT_ID = "event_state_on_demand_bounded_execution_v0_1_20260727T200207Z"
GATE_ID = "event_state_on_demand_bounded_candidate_dataset_review_v0_1"
REVIEW_ID = f"{GATE_ID}_20260727T000000Z"
STATUS_PASS = "CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION"
STATUS_BLOCKED = "CLOSED_BLOCKED_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_NO_PROMOTION"
NEXT_GATE = "event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1"


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


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


def record_key(row: dict[str, Any]) -> str:
    return "|".join([
        row["event_type_id"],
        row["exchange_id"],
        row["session_date"],
        row["instrument_id"],
        row["event_anchor_timestamp_utc"],
        row["event_window_definition_id"],
    ])


def ledger_key(row: dict[str, Any]) -> str:
    return "|".join([
        row["event_type_id"],
        row["exchange_id"],
        row["session_date"],
        row["instrument_id"],
        row["event_anchor_timestamp_utc"],
        row["event_window_definition_id"],
    ])


def bool_status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def markdown(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Event State On-Demand Bounded Candidate Dataset Review Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-27`

```text
review_id = {matrix['review_id']}
reviewed_run = {matrix['reviewed_run']}
reviewed_candidate_dataset_id = {matrix['reviewed_candidate_dataset_id']}
review_decision = {d['review_decision']}
requested_contexts = {d['requested_contexts']}
represented_contexts = {d['represented_contexts']}
unavailable_contexts = {d['unavailable_contexts']}
unaccounted_contexts = {d['unaccounted_contexts']}
event_state_candidate_records = {d['event_state_candidate_records']}
hard_review_failures = {d['hard_review_failures']}
candidate_dataset_review_approved = {str(d['candidate_dataset_review_approved']).lower()}
reuse_eligibility_after_review = {d['reuse_eligibility_after_review']}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

The candidate is accepted only as bounded Event State on-demand evidence. It is
not an official Event State dataset, not production, and not downstream
consumable. The review does not mutate the candidate registry entry and does
not authorize another materialization.
"""


def main() -> int:
    run_id = f"{GATE_ID}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    review_run_dir = BASE / "runs" / run_id
    if review_run_dir.exists():
        raise RuntimeError(f"review run directory already exists: {review_run_dir}")
    review_run_dir.mkdir(parents=True)

    final_manifest = read_json(SOURCE_RUN_DIR / "final_manifest.json")
    candidate_manifest = read_json(SOURCE_RUN_DIR / "event_state_candidate_output_manifest.json")
    registry_entry = read_json(SOURCE_RUN_DIR / "candidate_registry_entry.json")
    validation_report = read_json(SOURCE_RUN_DIR / "event_state_validation_report.json")
    context_ledger_source = read_json(SOURCE_RUN_DIR / "event_state_logical_context_ledger.json")
    binding_report = read_json(SOURCE_RUN_DIR / "market_state_dependency_binding_report.json")
    event_instance_manifest = read_json(SOURCE_RUN_DIR / "event_instance_manifest.json")
    event_window_manifest = read_json(SOURCE_RUN_DIR / "event_window_binding_manifest.json")
    projection_manifest = read_json(SOURCE_RUN_DIR / "instrument_session_projection_manifest.json")
    lineage_manifest = read_json(SOURCE_RUN_DIR / "event_state_lineage_manifest.json")
    failed_attempt = read_json(BASE / "runs" / FAILED_ATTEMPT_ID / "failure_manifest.json")

    candidate_file = Path(candidate_manifest["files"][0]["path"])
    records = read_jsonl(candidate_file)
    candidate_file_hash_match = sha_file(candidate_file) == candidate_manifest["files"][0]["sha256"]

    represented_ledger = [x for x in context_ledger_source if x["context_status"] == "represented"]
    unavailable_ledger = [x for x in context_ledger_source if x["context_status"] == "unavailable"]
    record_keys = {record_key(x) for x in records}
    represented_keys = {ledger_key(x) for x in represented_ledger}
    unavailable_keys = {ledger_key(x) for x in unavailable_ledger}

    event_instance_ids_by_session = {}
    for row in records:
        event_instance_ids_by_session.setdefault(row["session_date"], set()).add(row["event_instance_id"])

    parsed_lineage_count = 0
    lineage_failures = 0
    for row in records:
        try:
            lineage = json.loads(row["source_lineage_json"])
            parsed_lineage_count += 1
            if lineage.get("market_state_candidate_dataset_fingerprint") != candidate_manifest["market_state_candidate_dataset_fingerprint"]:
                lineage_failures += 1
            if lineage.get("market_state_dependency_consumption_authorization") != "market_state_capability_event_state_bounded_dependency_consumption_authorization_v0_1":
                lineage_failures += 1
        except Exception:
            lineage_failures += 1

    binding_rows = binding_report
    binding_bound = [x for x in binding_rows if x["market_state_binding_status"] == "BOUND"]
    binding_blocked = [x for x in binding_rows if x["market_state_binding_status"] != "BOUND"]

    context_ledger = {
        "review_id": REVIEW_ID,
        "review_run_id": run_id,
        "review_gate": GATE_ID,
        "source_run_id": SOURCE_RUN_ID,
        "ledger_grain": "event_type_id+exchange_id+session_date+instrument_id+event_anchor_timestamp_utc+event_window_definition_id",
        "requested_contexts": len(context_ledger_source),
        "represented_contexts": len(represented_ledger),
        "unavailable_contexts": len(unavailable_ledger),
        "records_emitted": len(records),
        "unavailable_context_keys": sorted(unavailable_keys),
        "represented_context_keys": sorted(represented_keys),
        "record_context_keys": sorted(record_keys),
        "source_ledger_ref": str(SOURCE_RUN_DIR / "event_state_logical_context_ledger.json"),
    }
    context_ledger["context_ledger_sha256"] = sha_json(without_key(context_ledger, "context_ledger_sha256"))

    fingerprint_comparison = {
        "review_id": REVIEW_ID,
        "review_run_id": run_id,
        "review_gate": GATE_ID,
        "source_run_id": SOURCE_RUN_ID,
        "candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "logical_dataset_fingerprint": candidate_manifest["logical_dataset_fingerprint"],
        "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "validation_result_fingerprint": validation_report["validation_result_fingerprint"],
        "candidate_file_recorded_sha256": candidate_manifest["files"][0]["sha256"],
        "candidate_file_current_sha256": sha_file(candidate_file),
        "candidate_file_hash_match": candidate_file_hash_match,
        "request_fingerprint_match": final_manifest["event_state_request_fingerprint"] == candidate_manifest["event_state_request_fingerprint"] == registry_entry["event_state_request_fingerprint"],
        "dependency_resolution_fingerprint_match": final_manifest["event_state_dependency_resolution_fingerprint"] == candidate_manifest["event_state_dependency_resolution_fingerprint"] == registry_entry["event_state_dependency_resolution_fingerprint"],
        "execution_plan_fingerprint_match": final_manifest["event_state_execution_plan_fingerprint"] == candidate_manifest["event_state_execution_plan_fingerprint"] == registry_entry["event_state_execution_plan_fingerprint"],
        "market_state_candidate_dataset_fingerprint_match": final_manifest["market_state_candidate_dataset_fingerprint_or_ref"] == candidate_manifest["market_state_candidate_dataset_fingerprint"] == registry_entry["market_state_candidate_dataset_fingerprint"],
    }
    fingerprint_comparison["fingerprint_comparison_sha256"] = sha_json(without_key(fingerprint_comparison, "fingerprint_comparison_sha256"))

    checks = [
        (final_manifest["final_run_status"] == "CLOSED_PASS_EVENT_STATE_ON_DEMAND_BOUNDED_EXECUTION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED", "source_run_closed_pass"),
        (final_manifest["requested_event_state_context_count"] == 9, "requested_contexts_is_9"),
        (final_manifest["represented_context_count"] == 8, "represented_contexts_is_8"),
        (final_manifest["blocked_context_count"] == 1, "unavailable_contexts_is_1"),
        (len(records) == 8, "candidate_jsonl_records_is_8"),
        (candidate_file_hash_match, "candidate_file_hash_match"),
        (validation_report["validation_status"] == "pass_with_restrictions", "validation_pass_with_restrictions"),
        (validation_report["hard_validation_failures"] == 0, "hard_validation_failures_zero"),
        (validation_report["fallback_uses"] == 0, "fallback_uses_zero"),
        (validation_report["duplicate_event_state_record_ids"] == 0, "duplicate_event_state_record_ids_zero"),
        (validation_report["native_event_instance_identity_instrument_id_uses"] == 0, "native_event_instance_identity_excludes_instrument"),
        (validation_report["partial_event_state_records"] == 0, "partial_event_state_records_zero"),
        (record_keys == represented_keys, "record_keys_equal_represented_ledger_keys"),
        (len(unavailable_keys) == 1 and all("BBG001S5N8T1" in x and "2022-11-25" in x for x in unavailable_keys), "unavailable_context_expected"),
        (all(x.get("blocking_reason") == "missing_exact_market_state_binding" for x in unavailable_ledger), "unavailable_reason_expected"),
        (len({x["event_state_record_id"] for x in records}) == len(records), "event_state_record_ids_unique"),
        (len({x["event_state_record_fingerprint"] for x in records}) == len(records), "event_state_record_fingerprints_unique"),
        (all(x["event_type_id"] == "event_type:market_data:session_opened" for x in records), "event_type_scope_session_opened_only"),
        (all(x["event_state_profile_id"] == "event_state_core_four_intraday_profile_v0_1" for x in records), "event_state_profile_scope_match"),
        (all(x["event_window_definition_id"] == "session_opened_at_anchor_context_v0_1" for x in records), "event_window_scope_match"),
        (all(x["state_role"] == "at_event" for x in records), "state_role_at_event"),
        (all(x["consumption_legality"] == "research_only" for x in records), "consumption_legality_research_only"),
        (all(x["event_anchor_timestamp_utc"] == x["decision_timestamp_utc"] == x["window_start_utc"] == x["window_end_utc"] for x in records), "at_event_timestamp_alignment"),
        (all(len(v) == 1 for v in event_instance_ids_by_session.values()) and len(event_instance_ids_by_session) == 3, "one_native_event_instance_per_session"),
        (len(event_instance_manifest) == 3, "event_instance_manifest_count_3"),
        (len(event_window_manifest) == 3, "event_window_manifest_count_3"),
        (len(projection_manifest) == 9, "instrument_projection_manifest_count_9"),
        (len(binding_bound) == 8 and len(binding_blocked) == 1, "market_state_dependency_binding_8_bound_1_blocked"),
        (all(x["market_state_rows_found"] == 1 for x in binding_bound), "bound_market_state_rows_exactly_one"),
        (all(not x["fallback_used"] for x in binding_rows), "dependency_fallbacks_zero"),
        (parsed_lineage_count == len(records) and lineage_failures == 0, "row_lineage_parse_and_dependency_match"),
        (registry_entry["registry_status"] == "validated_candidate", "registry_status_validated_candidate"),
        (registry_entry["reuse_eligibility"] == "pending_determinism", "reuse_pending_determinism"),
        (registry_entry["promotion_review_eligibility"] == "not_eligible_pending_candidate_dataset_review", "promotion_review_pending_before_review"),
        (registry_entry["downstream_eligibility"] is False, "registry_downstream_false"),
        (final_manifest["official_event_state_dataset"] is False and final_manifest["production"] is False and final_manifest["downstream"] is False, "official_production_downstream_closed"),
        ((failed_attempt.get("valid_gate_closure") is False) or str(failed_attempt.get("failure_status", failed_attempt.get("status", ""))).startswith("FAILED"), "failed_attempt_preserved_as_invalid"),
    ]
    hard_review_failures = sum(0 if passed else 1 for passed, _ in checks)
    status = STATUS_PASS if hard_review_failures == 0 else STATUS_BLOCKED

    matrix = {
        "review_id": REVIEW_ID,
        "review_run_id": run_id,
        "review_gate": GATE_ID,
        "status": status,
        "reviewed_run": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_id": candidate_manifest["candidate_dataset_id"],
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "reviewed_logical_dataset_fingerprint": candidate_manifest["logical_dataset_fingerprint"],
        "decision": {
            "review_decision": "approved_as_event_state_on_demand_bounded_candidate_evidence_with_restrictions" if hard_review_failures == 0 else "blocked",
            "requested_contexts": len(context_ledger_source),
            "represented_contexts": len(represented_ledger),
            "unavailable_contexts": len(unavailable_ledger),
            "unaccounted_contexts": len(context_ledger_source) - len(represented_ledger) - len(unavailable_ledger),
            "event_state_candidate_records": len(records),
            "hard_review_failures": hard_review_failures,
            "candidate_dataset_review_approved": hard_review_failures == 0,
            "dataset_completeness": "partial",
            "reuse_eligibility_after_review": "pending_deterministic_rerun",
            "official_dataset_after_review": False,
            "production_after_review": False,
            "downstream_after_review": False,
        },
        "checks": [{"check_id": name, "status": bool_status(passed)} for passed, name in checks],
        "evidence": {
            "source_final_manifest": str(SOURCE_RUN_DIR / "final_manifest.json"),
            "candidate_manifest": str(SOURCE_RUN_DIR / "event_state_candidate_output_manifest.json"),
            "candidate_registry_entry": str(SOURCE_RUN_DIR / "candidate_registry_entry.json"),
            "validation_report": str(SOURCE_RUN_DIR / "event_state_validation_report.json"),
            "logical_context_ledger": str(SOURCE_RUN_DIR / "event_state_logical_context_ledger.json"),
            "context_ledger_sha256": context_ledger["context_ledger_sha256"],
            "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
        },
        "registry_entry_mutations": 0,
        "materializer_executions": 0,
        "market_state_candidate_files_read_by_review": 0,
        "event_state_records_emitted_by_review": 0,
        "candidate_dataset_registry_entries_written_by_review": 0,
        "next_allowed_gate": NEXT_GATE if hard_review_failures == 0 else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    matrix["review_matrix_sha256"] = sha_json(without_key(matrix, "review_matrix_sha256"))

    scope = {
        "scope_id": "event_state_on_demand_bounded_candidate_dataset_review_scope_v0_1",
        "gate": GATE_ID,
        "review_id": REVIEW_ID,
        "review_run_id": run_id,
        "reviewed_run": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "allowed_inputs": [
            "final_manifest.json",
            "event_state_candidate_output_manifest.json",
            "candidate_registry_entry.json",
            "event_state_validation_report.json",
            "event_state_logical_context_ledger.json",
            "market_state_dependency_binding_report.json",
            "event_instance_manifest.json",
            "event_window_binding_manifest.json",
            "instrument_session_projection_manifest.json",
            "event_state_candidate_records.jsonl",
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

    auth = f"""# Event State On-Demand Bounded Candidate Dataset Review Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_REVIEW`
Date: `2026-07-27`

```text
review_id = {REVIEW_ID}
review_run_id = {run_id}
reviewed_run = {SOURCE_RUN_ID}
reviewed_candidate_dataset_fingerprint = {candidate_manifest['candidate_dataset_fingerprint']}
execution_authorized = false
market_state_read_authorized = false
event_state_materialization_authorized = false
registry_mutation_authorized = false
official_dataset_promotion_authorized = false
production_authorized = false
downstream_authorized = false
```

This gate authorizes review only. It does not authorize rebuilding Event State,
reading Market State again, mutating the candidate registry entry, promoting an
official dataset, production, or downstream consumption.
"""

    final = {
        "gate": GATE_ID,
        "review_id": REVIEW_ID,
        "review_run_id": run_id,
        "status": status,
        "reviewed_run": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_id": candidate_manifest["candidate_dataset_id"],
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "reviewed_logical_dataset_fingerprint": candidate_manifest["logical_dataset_fingerprint"],
        "hard_review_failures": hard_review_failures,
        "requested_contexts": matrix["decision"]["requested_contexts"],
        "represented_contexts": matrix["decision"]["represented_contexts"],
        "unavailable_contexts": matrix["decision"]["unavailable_contexts"],
        "event_state_candidate_records": matrix["decision"]["event_state_candidate_records"],
        "review_matrix_sha256": matrix["review_matrix_sha256"],
        "context_ledger_sha256": context_ledger["context_ledger_sha256"],
        "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
        "registry_entry_mutations": 0,
        "materializer_executions": 0,
        "market_state_candidate_files_read_by_review": 0,
        "event_state_records_emitted_by_review": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
        "created_at_utc": now_z(),
    }
    final["final_manifest_sha256"] = sha_json(without_key(final, "final_manifest_sha256"))

    write_json(BASE / "configs" / "event_state_on_demand_bounded_candidate_dataset_review_scope_v0_1.json", scope)
    write_json(BASE / "event_state_on_demand_bounded_candidate_context_ledger_v0_1.json", context_ledger)
    write_json(BASE / "event_state_on_demand_bounded_candidate_fingerprint_comparison_v0_1.json", fingerprint_comparison)
    write_json(BASE / "event_state_on_demand_bounded_candidate_dataset_review_matrix_v0_1.json", matrix)
    (BASE / "event_state_on_demand_bounded_candidate_dataset_review_authorization_v0_1.md").write_text(auth, encoding="utf-8")
    readout = markdown(matrix)
    (BASE / "event_state_on_demand_bounded_candidate_dataset_review_readout_v0_1.md").write_text(readout, encoding="utf-8")

    write_json(review_run_dir / "final_manifest.json", final)
    write_json(review_run_dir / "event_state_on_demand_bounded_candidate_dataset_review_matrix_v0_1.json", matrix)
    write_json(review_run_dir / "event_state_on_demand_bounded_candidate_context_ledger_v0_1.json", context_ledger)
    write_json(review_run_dir / "event_state_on_demand_bounded_candidate_fingerprint_comparison_v0_1.json", fingerprint_comparison)
    (review_run_dir / "event_state_on_demand_bounded_candidate_dataset_review_readout_v0_1.md").write_text(readout, encoding="utf-8")

    print(json.dumps({"status": status, "review_run_id": run_id, "hard_review_failures": hard_review_failures, "next_gate": matrix["next_allowed_gate"]}, indent=2))
    return 0 if hard_review_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())