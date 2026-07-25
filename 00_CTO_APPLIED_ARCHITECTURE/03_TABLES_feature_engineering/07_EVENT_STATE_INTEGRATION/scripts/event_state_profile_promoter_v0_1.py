#!/usr/bin/env python
"""Promote the bounded Event State profile registry.

This script writes only official semantic profile-registry metadata. It does
not copy candidate records, write parquet, promote an official dataset,
authorize production or authorize downstream consumption.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "event_state_profile_promotion_v0_1"
DEFAULT_RUN_PREFIX = "event_state_profile_promotion_v0_1"
SCHEMA_CONTRACT_FILE = "EVENT_STATE_SCHEMA_CONTRACT.json"


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


def verify_hash(path: Path, expected: str, label: str, failures: list[str]) -> str | None:
    if not path.exists():
        failures.append(f"missing_required_artifact:{label}")
        return None
    observed = sha256_file(path)
    if observed.lower() != expected.lower():
        failures.append(f"sha256_mismatch:{label}")
    return observed


def resolve_base_path(base_dir: Path, relative_path: str) -> Path:
    return (base_dir / relative_path).resolve()


def count_jsonl_records(path: Path) -> int:
    with path.open("r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def logical_schema_fields(field_names: list[str]) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for name in field_names:
        if name.endswith("_json"):
            logical_type = "json_string"
        elif name.endswith("_utc"):
            logical_type = "timestamp_utc_string"
        elif name == "session_date":
            logical_type = "date_string"
        elif name == "relative_time_to_event":
            logical_type = "iso8601_duration_string"
        else:
            logical_type = "string_or_profile_defined_scalar"
        fields.append({"field_name": name, "logical_type": logical_type, "required": "true"})
    return fields


def write_blocked(run_dir: Path, run_id: str, started_at: str, failures: list[str]) -> None:
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "blocked", "updated_at_utc": utc_now()})
    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "status": "blocked",
        "promotion_status": "BLOCKED_PENDING_EVIDENCE",
        "blocking_failures": failures,
        "official_event_state_profile_promotion_executed": False,
        "official_event_state_dataset_promotion": False,
        "official_event_state_parquet_files_written": 0,
        "candidate_event_state_records_copied": False,
        "production": False,
        "downstream_consumption": False,
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    print(json.dumps(final_manifest, indent=2, sort_keys=True))


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
    target = scope["promotion_target"]
    evidence = scope["required_source_evidence"]
    prior = scope["required_prior_review"]
    registry_dir = resolve_base_path(base_dir, scope["official_profile_registry_path"])
    root_readout_path = base_dir / "event_state_profile_promotion_readout_v0_1.md"

    failures: list[str] = []
    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "registry_dir": str(registry_dir),
        "authority_boundary": scope["authority_boundary"],
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "started", "updated_at_utc": utc_now()})

    if registry_dir.exists():
        failures.append(f"profile_registry_already_exists:{registry_dir}")

    review_run_dir = runs_root / prior["run_id"]
    review_final = review_run_dir / "final_manifest.json"
    review_decision = review_run_dir / "profile_promotion_decision.json"
    review_inventory = review_run_dir / "evidence_inventory_report.csv"
    review_restrictions = review_run_dir / "profile_promotion_restrictions_report.csv"

    verify_hash(review_final, prior["final_manifest_sha256"], "review_final_manifest", failures)
    verify_hash(review_decision, prior["decision_artifact_sha256"], "review_decision", failures)
    verify_hash(review_inventory, prior["evidence_inventory_sha256"], "review_evidence_inventory", failures)
    verify_hash(review_restrictions, prior["restrictions_report_sha256"], "review_restrictions_report", failures)

    bounded_final = resolve_base_path(base_dir, evidence["bounded_execution_final_manifest_relative_path"])
    candidate_records = resolve_base_path(base_dir, evidence["candidate_event_state_records_relative_path"])
    bounded_validation_report = bounded_final.parent / "event_state_validation_report.json"
    physical_final = resolve_base_path(base_dir, evidence["physical_validation_final_manifest_relative_path"])
    physical_schema_report = physical_final.parent / "schema_validation_report.json"
    candidate_review_final = resolve_base_path(base_dir, evidence["candidate_dataset_review_final_manifest_relative_path"])
    candidate_review_decision = candidate_review_final.parent / "candidate_dataset_review_decision.json"
    integration_contract_path = base_dir / "event_state_integration_design_contract_v0_1.json"

    verify_hash(bounded_final, evidence["bounded_execution_final_manifest_sha256"], "bounded_execution_final_manifest", failures)
    verify_hash(candidate_records, evidence["bounded_execution_candidate_records_sha256"], "candidate_records", failures)
    verify_hash(bounded_validation_report, evidence["bounded_execution_validation_report_sha256"], "bounded_validation_report", failures)
    verify_hash(physical_final, evidence["physical_validation_final_manifest_sha256"], "physical_validation_final_manifest", failures)
    verify_hash(physical_schema_report, evidence["physical_validation_schema_report_sha256"], "physical_schema_report", failures)
    verify_hash(candidate_review_final, evidence["candidate_dataset_review_final_manifest_sha256"], "candidate_dataset_review_final_manifest", failures)
    verify_hash(candidate_review_decision, evidence["candidate_dataset_review_decision_sha256"], "candidate_review_decision", failures)
    verify_hash(integration_contract_path, evidence["event_state_integration_design_contract_sha256"], "event_state_integration_design_contract", failures)

    review_final_payload = load_json(review_final) if review_final.exists() else {}
    review_decision_payload = load_json(review_decision) if review_decision.exists() else {}
    bounded_payload = load_json(bounded_final) if bounded_final.exists() else {}
    physical_payload = load_json(physical_final) if physical_final.exists() else {}
    candidate_review_payload = load_json(candidate_review_final) if candidate_review_final.exists() else {}
    candidate_review_decision_payload = load_json(candidate_review_decision) if candidate_review_decision.exists() else {}
    physical_schema_payload = load_json(physical_schema_report) if physical_schema_report.exists() else {}
    integration_contract = load_json(integration_contract_path) if integration_contract_path.exists() else {}

    if review_final_payload.get("decision") != prior["decision"]:
        failures.append("review_decision_not_approved_for_promotion")
    if review_decision_payload.get("decision") != prior["decision"]:
        failures.append("review_decision_artifact_not_approved")
    if review_final_payload.get("official_event_state_profile_promotion_executed") is not False:
        failures.append("review_boundary_expected_no_prior_promotion")
    if bounded_payload.get("event_state_bounded_execution_chain_execution") != "CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT":
        failures.append("bounded_execution_not_closed_pass_with_restrictions")
    if physical_payload.get("event_state_bounded_execution_chain_physical_validation") != "CLOSED_PASS_WITH_RESTRICTIONS":
        failures.append("physical_validation_not_closed_pass_with_restrictions")
    if candidate_review_payload.get("event_state_candidate_dataset_review") != "CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION":
        failures.append("candidate_dataset_review_not_approved")
    if candidate_review_decision_payload.get("accepted_as_candidate_dataset_review_evidence") is not True:
        failures.append("candidate_review_decision_not_accepted_as_evidence")
    if physical_payload.get("hard_validation_failures") != 0:
        failures.append("physical_validation_hard_failures_nonzero")
    if candidate_review_payload.get("hard_review_failures") != 0:
        failures.append("candidate_dataset_review_hard_failures_nonzero")
    if physical_schema_payload.get("schema_failures") != 0:
        failures.append("physical_schema_failures_nonzero")
    if integration_contract.get("status") != "CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION":
        failures.append("integration_contract_not_closed_design")
    if integration_contract.get("event_state_profile_id") != target["promoted_profile_id"]:
        failures.append("integration_contract_profile_id_mismatch")
    if integration_contract.get("event_type_id") not in target["accepted_event_type_ids"]:
        failures.append("integration_contract_event_type_not_in_scope")
    if integration_contract.get("accepted_subject_scope") != target["accepted_subject_scope"]:
        failures.append("integration_contract_subject_scope_mismatch")

    if candidate_records.exists():
        observed_records = count_jsonl_records(candidate_records)
        if observed_records != evidence["candidate_records_expected"]:
            failures.append("candidate_record_count_mismatch")
    else:
        observed_records = 0

    invariant_checks = {
        "requested_contexts": 9,
        "event_instances_created": 3,
        "event_window_bindings_created": 3,
        "instrument_session_projections_created": 9,
        "market_state_bindings_found": 8,
        "event_state_candidate_records_emitted": 8,
        "blocked_contexts": 1,
        "missing_exact_market_state_bindings": 1,
        "multiple_exact_market_state_bindings": 0,
        "fallback_uses": 0,
        "hard_validation_failures": 0,
    }
    for key, expected in invariant_checks.items():
        if bounded_payload.get(key) != expected:
            failures.append(f"bounded_invariant_mismatch:{key}")

    forbidden_true_flags = [
        (bounded_payload, "official_event_state_dataset_promotion"),
        (bounded_payload, "downstream_consumption"),
        (physical_payload, "official_event_state_profile_promotion"),
        (physical_payload, "official_event_state_dataset_promotion"),
        (physical_payload, "production"),
        (physical_payload, "downstream_consumption"),
        (candidate_review_payload, "official_event_state_profile_promotion"),
        (candidate_review_payload, "official_event_state_dataset_promotion"),
        (candidate_review_payload, "official_parquet_write"),
        (candidate_review_payload, "production"),
        (candidate_review_payload, "downstream_consumption"),
    ]
    for payload, key in forbidden_true_flags:
        if payload.get(key) is not False:
            failures.append(f"forbidden_boundary_not_false:{key}")

    if failures:
        write_blocked(run_dir, run_id, started_at, failures)
        return 2

    registry_dir.mkdir(parents=True, exist_ok=False)
    promoted_at = utc_now()
    future_minimum_fields = integration_contract["future_minimum_fields"]

    profile_manifest = {
        "accepted_event_type_ids": target["accepted_event_type_ids"],
        "accepted_subject_scope": target["accepted_subject_scope"],
        "complete_tsis_event_state": False,
        "downstream_consumption_authorized": False,
        "event_detection_authorized": False,
        "event_family_ids": target["event_family_ids"],
        "event_state_materialization_authorized": False,
        "official_dataset_registry_write_authorized": False,
        "official_event_state_dataset_promotion": False,
        "official_event_state_parquet_written": False,
        "primary_evidence": scope["evidence_summary"],
        "production_authorized": False,
        "profile_classification": target["profile_classification"],
        "profile_id": target["promoted_profile_id"],
        "profile_scope": target["profile_scope"],
        "promoted_at_utc": promoted_at,
        "promotion_run_id": run_id,
        "source_market_state_physical_dataset_official": False,
        "source_market_state_profile_id": target["source_market_state_profile_id"],
        "source_market_state_schema_version": target["source_market_state_schema_version"],
        "status": scope["accepted_promotion_status"],
    }

    evidence_manifest = {
        "candidate_event_state_records_copied": False,
        "candidate_event_state_records_reference_only": True,
        "event_state_profile_id": target["promoted_profile_id"],
        "promotion_run_id": run_id,
        "required_prior_review": prior,
        "required_source_evidence": evidence,
        "scope_restrictions": scope["scope_restrictions"],
        "source_market_data_rows_read_by_promotion": 0,
    }

    schema_contract = {
        "candidate_records_checked": physical_schema_payload["records_checked"],
        "candidate_schema_version_reference": "event_state_candidate_schema_v0_1",
        "event_state_profile_id": target["promoted_profile_id"],
        "field_contract": logical_schema_fields(future_minimum_fields),
        "field_count": len(future_minimum_fields),
        "physical_validation_schema_failures": physical_schema_payload["schema_failures"],
        "profile_schema_contract_id": "event_state_core_four_intraday_profile_schema_contract_v0_1",
        "schema_authority": [
            "event_state_integration_design_contract_v0_1",
            "event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z"
        ],
        "schema_scope": "official_semantic_profile_schema_not_official_physical_dataset_schema",
        "source_market_state_schema_version": target["source_market_state_schema_version"],
    }

    readme = f"""# {target['promoted_profile_id']}

Status: `{scope['accepted_promotion_status']}`
Date: `2026-07-24`

This directory registers the bounded Event State profile as an official semantic
profile contract under Applied Architecture.

It is not complete TSIS Event State, not an operational Data Foundation dataset
registry, not production, and not downstream-consumable by itself.

```text
promotion_run_id = {run_id}
event_state_profile_id = {target['promoted_profile_id']}
source_market_state_profile_id = {target['source_market_state_profile_id']}
accepted_event_type_id = {target['accepted_event_type_ids'][0]}
accepted_subject_scope = {target['accepted_subject_scope']}
candidate_records_reviewed = {scope['evidence_summary']['candidate_records_reviewed']}
blocked_contexts = {scope['evidence_summary']['blocked_contexts']}
hard_validation_failures = {scope['evidence_summary']['hard_validation_failures']}
official_event_state_dataset_promotion = false
official_event_state_parquet_written = false
event_detection_authorized = false
downstream_consumption_authorized = false
```

Live restrictions:

```text
complete_tsis_event_state = false
event_type_scope = session_opened_only
halt_resumed_excluded = true
source_market_state_physical_dataset_official = false
full_history = false
full_universe = false
production = false
downstream_consumable = false
```
"""

    write_json(registry_dir / "PROFILE_MANIFEST.json", profile_manifest)
    write_json(registry_dir / "EVIDENCE_MANIFEST.json", evidence_manifest)
    write_json(registry_dir / SCHEMA_CONTRACT_FILE, schema_contract)
    (registry_dir / "README.md").write_text(readme, encoding="utf-8")

    registry_paths = [
        registry_dir / "README.md",
        registry_dir / "PROFILE_MANIFEST.json",
        registry_dir / "EVIDENCE_MANIFEST.json",
        registry_dir / SCHEMA_CONTRACT_FILE,
    ]
    write_report_rows = [
        {
            "artifact_class": "official_event_state_profile_registry_metadata",
            "bytes": path.stat().st_size,
            "path": str(path),
            "sha256": sha256_file(path),
        }
        for path in registry_paths
    ]
    with (run_dir / "official_profile_registry_write_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "bytes", "sha256", "artifact_class"])
        writer.writeheader()
        writer.writerows(write_report_rows)

    promotion_manifest = {
        "candidate_event_state_records_copied": False,
        "event_detection_authorized": False,
        "official_event_state_dataset_promotion": False,
        "official_event_state_parquet_files_written": 0,
        "official_event_state_profile_promotion_executed": True,
        "profile_id": target["promoted_profile_id"],
        "promotion_status": scope["accepted_promotion_status"],
        "production": False,
        "registry_artifacts_written": len(write_report_rows),
        "registry_dir": str(registry_dir),
        "registry_write_report": "official_profile_registry_write_report.csv",
        "run_id": run_id,
        "source_market_data_rows_read": 0,
        "source_market_state_profile_id": target["source_market_state_profile_id"],
        "downstream_consumption": False,
        "next_allowed_gate": scope["next_allowed_gate"],
    }
    write_json(run_dir / "promotion_manifest.json", promotion_manifest)

    readout = f"""# Event State Profile Promotion Readout v0.1

run_id = `{run_id}`
script_version = `{SCRIPT_VERSION}`

```text
event_state_profile_promotion = {scope['accepted_promotion_status']}
promoted_profile_id = {target['promoted_profile_id']}
source_market_state_profile_id = {target['source_market_state_profile_id']}
accepted_event_type_id = {target['accepted_event_type_ids'][0]}
accepted_subject_scope = {target['accepted_subject_scope']}
registry_artifacts_written = {len(write_report_rows)}
candidate_records_reviewed = {scope['evidence_summary']['candidate_records_reviewed']}
blocked_contexts = {scope['evidence_summary']['blocked_contexts']}
hard_validation_failures = 0
official_event_state_profile_promotion_executed = true
official_event_state_dataset_promotion = false
official_event_state_parquet_files_written = 0
candidate_event_state_records_copied = false
event_detection_authorized = false
source_market_data_rows_read = 0
production = false
downstream_consumption = false
next_allowed_gate = {scope['next_allowed_gate']}
```

The promoted artifact is an official Event State semantic profile registry
package only. It does not promote complete TSIS Event State, write or copy
parquet, authorize event detection, authorize production, authorize downstream
consumption or open full-history/full-universe execution.
"""
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")
    root_readout_path.write_text(readout, encoding="utf-8")
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "complete", "updated_at_utc": utc_now()})

    artifact_paths = {
        "pre_manifest": run_dir / "pre_manifest.json",
        "heartbeat": run_dir / "heartbeat.json",
        "official_profile_registry_write_report": run_dir / "official_profile_registry_write_report.csv",
        "promotion_manifest": run_dir / "promotion_manifest.json",
        "readout": run_dir / "readout.md",
        "root_readout": root_readout_path,
        "official_profile_readme": registry_dir / "README.md",
        "official_profile_manifest": registry_dir / "PROFILE_MANIFEST.json",
        "official_evidence_manifest": registry_dir / "EVIDENCE_MANIFEST.json",
        "official_schema_contract": registry_dir / SCHEMA_CONTRACT_FILE,
    }
    final_manifest = {
        **promotion_manifest,
        "artifacts": {name: str(path) for name, path in artifact_paths.items()},
        "artifacts_sha256": {name: sha256_file(path) for name, path in artifact_paths.items()},
        "blocking_failures": [],
        "completed_at_utc": utc_now(),
        "final_manifest_self_hash_policy": "not_recorded_to_avoid_self_referential_hash",
        "hard_validation_failures": 0,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started_at,
        "status": "complete",
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    print(json.dumps(final_manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
