#!/usr/bin/env python
"""Review bounded Event State evidence for semantic-profile promotion readiness.

This gate is review-only. It reads accepted artifacts and emits a decision, but
it never promotes an Event State profile, writes official parquet, promotes a
dataset, materializes Event State, or opens downstream consumption.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "event_state_profile_promotion_review_v0_1"
DEFAULT_RUN_PREFIX = "event_state_profile_promotion_review_v0_1"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig") as fh:
        return sum(1 for line in fh if line.strip())


def artifact_path(base_dir: Path, rel: str) -> Path:
    return (base_dir / rel).resolve()


def fail_if(condition: bool, failures: list[str], code: str) -> None:
    if condition:
        failures.append(code)


def find_type(snapshot: dict[str, Any], event_type_id: str) -> dict[str, Any] | None:
    for entry in snapshot.get("type_entries", []):
        if entry.get("event_type_id") == event_type_id:
            return entry
    return None


def closed_design_status(payload: dict[str, Any]) -> bool:
    return str(payload.get("status", "")).startswith("CLOSED_DESIGN_READY")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    parser.add_argument("--output-root")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    scope_path = Path(args.scope).resolve()
    base_dir = scope_path.parents[1]
    runs_root = base_dir / "runs"
    output_root = Path(args.output_root).resolve() if args.output_root else runs_root
    run_id = args.run_id or f"{DEFAULT_RUN_PREFIX}_{utc_stamp()}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    started_at = utc_now()
    scope = load_json(scope_path)
    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "authority_boundary": scope["authority_boundary"],
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "started", "updated_at_utc": utc_now()})

    hard_failures: list[str] = []
    inventory_rows: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}

    for artifact in scope["required_artifacts"]:
        path = artifact_path(base_dir, artifact["path"])
        exists = path.exists()
        observed_sha = sha256_file(path) if exists else None
        sha_match = exists and observed_sha == artifact["sha256"]
        observed_count: int | None = None
        if exists and path.suffix == ".jsonl":
            observed_count = count_jsonl(path)
        expected_count = artifact.get("expected_records")
        count_match = expected_count is None or observed_count == expected_count

        if not exists:
            hard_failures.append(f"missing_accepted_run_artifact:{artifact['artifact_id']}")
        elif not sha_match:
            hard_failures.append(f"fingerprint_mismatch:{artifact['artifact_id']}")
        if exists and not count_match:
            hard_failures.append(f"record_count_mismatch:{artifact['artifact_id']}")

        if exists and path.suffix == ".json":
            loaded[artifact["artifact_id"]] = load_json(path)

        inventory_rows.append({
            "artifact_id": artifact["artifact_id"],
            "path": str(path),
            "exists": exists,
            "expected_sha256": artifact["sha256"],
            "observed_sha256": observed_sha or "",
            "sha256_match": sha_match,
            "expected_count": expected_count if expected_count is not None else "",
            "observed_count": observed_count if observed_count is not None else "",
            "count_match": count_match,
        })

    profile_contract = loaded["event_state_profile_contract_design_contract"]
    registry_snapshot = loaded["event_type_registry_post_initial_admission_snapshot"]
    instance_contract = loaded["event_instance_binding_design_contract"]
    window_contract = loaded["event_window_binding_design_contract"]
    compatibility_contract = loaded["market_state_profile_compatibility_design_contract"]
    projection_contract = loaded["instrument_session_projection_design_contract"]
    integration_contract = loaded["event_state_integration_design_contract"]
    joint_review = loaded["event_state_execution_chain_joint_review_matrix"]
    bounded_contract = loaded["event_state_bounded_execution_chain_contract"]
    execution_manifest = loaded["bounded_execution_final_manifest"]
    physical_manifest = loaded["physical_validation_final_manifest"]
    candidate_review_manifest = loaded["candidate_dataset_review_final_manifest"]
    candidate_review_decision = loaded["candidate_dataset_review_decision"]

    reviewed = scope["reviewed_object"]
    invariants = scope["required_invariants"]

    event_type = find_type(registry_snapshot, invariants["event_type_id"])

    fail_if(profile_contract.get("status") != "CLOSED_DESIGN_READY_WITH_RESTRICTIONS", hard_failures, "profile_contract_not_closed")
    fail_if(profile_contract.get("event_state_profile", {}).get("profile_id") != reviewed["event_state_profile_id"], hard_failures, "profile_id_mismatch")
    fail_if(profile_contract.get("parent_market_state_profile", {}).get("status") != "OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS", hard_failures, "parent_market_state_profile_not_official")

    fail_if(registry_snapshot.get("registry_metadata", {}).get("accepted_event_types") != invariants["accepted_event_types"], hard_failures, "accepted_event_type_count_mismatch")
    fail_if(event_type is None, hard_failures, "accepted_event_type_missing")
    if event_type is not None:
        fail_if(event_type.get("status") != "accepted_with_restrictions", hard_failures, "event_type_not_accepted_with_restrictions")
        fail_if(event_type.get("accepted_subject_scope") != invariants["accepted_subject_scope"], hard_failures, "subject_scope_mismatch")
        fail_if(event_type.get("event_instance_binding_design_eligible_if_separately_authorized") is not True, hard_failures, "event_type_not_instance_design_eligible")

    for name, payload in [
        ("event_instance_binding_design_contract", instance_contract),
        ("event_window_binding_design_contract", window_contract),
        ("market_state_profile_compatibility_design_contract", compatibility_contract),
        ("instrument_session_projection_design_contract", projection_contract),
        ("event_state_integration_design_contract", integration_contract),
    ]:
        fail_if(not closed_design_status(payload), hard_failures, f"design_contract_not_closed:{name}")

    fail_if(joint_review.get("status") != "CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION", hard_failures, "joint_review_not_closed")
    fail_if(joint_review.get("summary", {}).get("blocking_design_findings") != 0, hard_failures, "joint_review_blocking_findings")
    fail_if(joint_review.get("summary", {}).get("approved_for_bounded_execution_chain_authorization") is not True, hard_failures, "joint_review_not_approved")

    shape = bounded_contract.get("bounded_execution_shape", {})
    fail_if(shape.get("exchange_sessions") != 3, hard_failures, "bounded_contract_exchange_session_scope_mismatch")
    fail_if(shape.get("instruments") != 3, hard_failures, "bounded_contract_instrument_scope_mismatch")
    fail_if(shape.get("instrument_session_contexts") != invariants["requested_contexts"], hard_failures, "bounded_contract_context_scope_mismatch")
    fail_if(bounded_contract.get("candidate_output_status", {}).get("official_profile_promotion_allowed") is not False, hard_failures, "bounded_contract_profile_promotion_open")
    fail_if(bounded_contract.get("candidate_output_status", {}).get("official_dataset_promotion_allowed") is not False, hard_failures, "bounded_contract_dataset_promotion_open")

    observed = {
        "requested_contexts": execution_manifest.get("requested_contexts"),
        "event_instances_created": execution_manifest.get("event_instances_created"),
        "event_window_bindings_created": execution_manifest.get("event_window_bindings_created"),
        "instrument_session_projections_created": execution_manifest.get("instrument_session_projections_created"),
        "market_state_bindings_found": execution_manifest.get("market_state_bindings_found"),
        "event_state_candidate_records_emitted": execution_manifest.get("event_state_candidate_records_emitted"),
        "blocked_contexts": execution_manifest.get("blocked_contexts"),
        "missing_exact_market_state_bindings": execution_manifest.get("missing_exact_market_state_bindings"),
        "multiple_exact_market_state_bindings": execution_manifest.get("multiple_exact_market_state_bindings"),
        "fallback_uses": execution_manifest.get("fallback_uses"),
        "physical_validation_hard_failures": physical_manifest.get("hard_validation_failures"),
        "candidate_dataset_review_hard_failures": candidate_review_manifest.get("hard_review_failures"),
        "candidate_records_reviewed": candidate_review_manifest.get("candidate_records_reviewed"),
        "official_event_state_profile_promotion": candidate_review_manifest.get("official_event_state_profile_promotion"),
        "official_event_state_dataset_promotion": candidate_review_manifest.get("official_event_state_dataset_promotion"),
        "official_parquet_write": candidate_review_manifest.get("official_parquet_write"),
        "downstream_consumption": candidate_review_manifest.get("downstream_consumption"),
    }

    for key, expected in invariants.items():
        if key in observed and observed[key] != expected:
            hard_failures.append(f"invariant_mismatch:{key}:expected={expected}:observed={observed[key]}")

    fail_if(execution_manifest.get("event_state_bounded_execution_chain_execution") != "CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT", hard_failures, "bounded_execution_not_closed")
    fail_if(execution_manifest.get("hard_validation_failures") != 0, hard_failures, "bounded_execution_hard_failures")
    fail_if(physical_manifest.get("event_state_bounded_execution_chain_physical_validation") != "CLOSED_PASS_WITH_RESTRICTIONS", hard_failures, "physical_validation_not_closed")
    fail_if(candidate_review_manifest.get("event_state_candidate_dataset_review") != "CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION", hard_failures, "candidate_dataset_review_not_closed")
    fail_if(candidate_review_decision.get("accepted_as_candidate_dataset_review_evidence") is not True, hard_failures, "candidate_dataset_review_not_accepted")
    fail_if(candidate_review_decision.get("promotion_executed") is not False, hard_failures, "candidate_review_promoted_profile_or_dataset")

    decision = scope["accepted_review_decision"] if not hard_failures else "BLOCKED_PENDING_EVIDENCE"
    next_gate = scope["next_allowed_gate_if_approved"] if not hard_failures else scope["next_allowed_gate_if_blocked"]

    with (run_dir / "evidence_inventory_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(inventory_rows[0].keys()))
        writer.writeheader()
        writer.writerows(inventory_rows)

    restriction_rows = [
        {"restriction": key, "value": value, "blocking": False}
        for key, value in scope["scope_restrictions"].items()
    ]
    with (run_dir / "profile_promotion_restrictions_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["restriction", "value", "blocking"])
        writer.writeheader()
        writer.writerows(restriction_rows)

    decision_payload = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "reviewed_profile_id": reviewed["event_state_profile_id"],
        "source_market_state_profile_id": reviewed["source_market_state_profile_id"],
        "event_type_scope": reviewed["event_type_scope"],
        "decision": decision,
        "blocking_failures": hard_failures,
        "observed_invariants": observed,
        "scope_restrictions_preserved": scope["scope_restrictions"],
        "authority_boundary_preserved": scope["authority_boundary"],
        "next_allowed_gate": next_gate,
        "official_event_state_profile_promotion_executed": False,
        "official_event_state_dataset_promotion": False,
        "official_parquet_files_written": 0,
        "event_state_materialization": False,
        "production": False,
        "downstream_consumption": False,
        "source_market_data_rows_read": 0,
    }
    write_json(run_dir / "profile_promotion_decision.json", decision_payload)

    readout = f"""# Event State Profile Promotion Review Readout v0.1

run_id = `{run_id}`
script_version = `{SCRIPT_VERSION}`

```text
event_state_profile_promotion_review = {decision}
reviewed_profile_id = {reviewed["event_state_profile_id"]}
source_market_state_profile_id = {reviewed["source_market_state_profile_id"]}
event_type_scope = {", ".join(reviewed["event_type_scope"])}
evidence_artifacts_checked = {len(inventory_rows)}
candidate_records_reviewed = {observed["candidate_records_reviewed"]}
event_instances_created = {observed["event_instances_created"]}
event_window_bindings_created = {observed["event_window_bindings_created"]}
instrument_session_projections_created = {observed["instrument_session_projections_created"]}
market_state_bindings_found = {observed["market_state_bindings_found"]}
blocked_contexts = {observed["blocked_contexts"]}
fallback_uses = {observed["fallback_uses"]}
physical_validation_hard_failures = {observed["physical_validation_hard_failures"]}
candidate_dataset_review_hard_failures = {observed["candidate_dataset_review_hard_failures"]}
hard_review_failures = {len(hard_failures)}
official_event_state_profile_promotion_executed = false
official_event_state_dataset_promotion = false
official_parquet_files_written = 0
event_state_materialization = false
production = false
downstream_consumption = false
next_allowed_gate = {next_gate}
```

The review approves a separate semantic profile promotion authorization only if
the decision is `APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS`.
It does not promote an Event State profile, promote a dataset, write parquet,
materialize Event State, authorize production, or authorize downstream
consumption.
"""
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")
    (base_dir / "event_state_profile_promotion_review_readout_v0_1.md").write_text(readout, encoding="utf-8")

    artifacts = {
        "pre_manifest": str(run_dir / "pre_manifest.json"),
        "heartbeat": str(run_dir / "heartbeat.json"),
        "evidence_inventory_report": str(run_dir / "evidence_inventory_report.csv"),
        "profile_promotion_restrictions_report": str(run_dir / "profile_promotion_restrictions_report.csv"),
        "profile_promotion_decision": str(run_dir / "profile_promotion_decision.json"),
        "readout": str(run_dir / "readout.md"),
        "root_readout": str(base_dir / "event_state_profile_promotion_review_readout_v0_1.md"),
    }
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "complete", "updated_at_utc": utc_now()})
    final_manifest = {
        **decision_payload,
        "status": "complete",
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "scope_path": str(scope_path),
        "evidence_artifacts_checked": len(inventory_rows),
        "hash_mismatches": sum(1 for row in inventory_rows if not row["sha256_match"]),
        "count_mismatches": sum(1 for row in inventory_rows if not row["count_match"]),
        "hard_review_failures": len(hard_failures),
        "artifacts": artifacts,
        "artifacts_sha256": {key: sha256_file(Path(value)) for key, value in artifacts.items()},
        "final_manifest_self_hash_policy": "not_recorded_to_avoid_self_referential_hash",
    }
    write_json(run_dir / "final_manifest.json", final_manifest)

    print(json.dumps({
        "run_id": run_id,
        "decision": decision,
        "hard_review_failures": len(hard_failures),
        "next_allowed_gate": next_gate,
    }, indent=2, sort_keys=True))
    return 0 if not hard_failures else 2


if __name__ == "__main__":
    raise SystemExit(main())

