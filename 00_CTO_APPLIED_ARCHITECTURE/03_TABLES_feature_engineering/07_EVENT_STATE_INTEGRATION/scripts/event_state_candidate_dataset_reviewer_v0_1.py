from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import json
import socket
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "event_state_candidate_dataset_review_v0_1"
RUN_ID_PREFIX = "event_state_candidate_dataset_review_v0_1"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_z(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid_jsonl_line_{line_no}: {exc}") from exc
    return rows


def embedded_json(value: str) -> Any:
    return json.loads(value)


def artifact_hash_failures(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for name, path_value in manifest.get("artifacts", {}).items():
        if name == "final_manifest":
            continue
        path = Path(path_value)
        if not path.exists():
            failures.append(f"{name}_missing")
            continue
        expected = manifest.get("artifacts_sha256", {}).get(name)
        if expected and sha256_file(path) != expected:
            failures.append(f"{name}_hash_mismatch")
    return failures


def add(matrix: list[dict[str, Any]], finding_id: str, status: str, details: str) -> None:
    matrix.append({"finding_id": finding_id, "status": status, "details": details})


def fail_if(matrix: list[dict[str, Any]], failures: list[str], condition: bool, finding_id: str, details: str) -> None:
    if condition:
        failures.append(finding_id)
        add(matrix, finding_id, "FAIL", details)
    else:
        add(matrix, finding_id, "PASS", details)


def review_candidate_dataset(scope: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    matrix: list[dict[str, Any]] = []

    execution_manifest = load_json(Path(scope["review_target"]["execution_final_manifest"]))
    physical_manifest = load_json(Path(scope["review_target"]["physical_validation_final_manifest"]))
    artifacts = execution_manifest["artifacts"]

    records = read_jsonl(Path(artifacts["event_state_candidate_records"]))
    event_instances = read_csv(Path(artifacts["event_instance_report"]))
    windows = read_csv(Path(artifacts["event_window_binding_report"]))
    projections = read_csv(Path(artifacts["instrument_session_projection_report"]))
    bindings = read_csv(Path(artifacts["market_state_binding_report"]))
    candidate_manifest = load_json(Path(artifacts["event_state_candidate_manifest"]))
    physical_report = load_json(Path(physical_manifest["artifacts"]["physical_validation_report"]))

    expected_counts = scope["expected_counts"]
    identity = scope["identity_authority"]

    fail_if(
        matrix,
        failures,
        execution_manifest.get("event_state_bounded_execution_chain_execution") != scope["expected_status"]["execution_status"],
        "accepted_execution_status_mismatch",
        f"observed={execution_manifest.get('event_state_bounded_execution_chain_execution')}",
    )
    fail_if(
        matrix,
        failures,
        physical_manifest.get("event_state_bounded_execution_chain_physical_validation") != scope["expected_status"]["physical_validation_status"],
        "accepted_physical_validation_status_mismatch",
        f"observed={physical_manifest.get('event_state_bounded_execution_chain_physical_validation')}",
    )
    fail_if(
        matrix,
        failures,
        physical_manifest.get("hard_validation_failures") != scope["expected_status"]["physical_validation_hard_failures"],
        "physical_validation_hard_failures_nonzero",
        f"observed={physical_manifest.get('hard_validation_failures')}",
    )

    exec_hash_failures = artifact_hash_failures(execution_manifest)
    phys_hash_failures = artifact_hash_failures(physical_manifest)
    fail_if(matrix, failures, bool(exec_hash_failures), "execution_artifact_hash_failures", "|".join(exec_hash_failures))
    fail_if(matrix, failures, bool(phys_hash_failures), "physical_validation_artifact_hash_failures", "|".join(phys_hash_failures))

    for key, expected in expected_counts.items():
        observed = execution_manifest.get(key)
        if observed is None:
            observed = physical_manifest.get(key)
        fail_if(matrix, failures, observed != expected, f"count_{key}_mismatch", f"expected={expected}; observed={observed}")

    fail_if(
        matrix,
        failures,
        len(records) != expected_counts["event_state_candidate_records_emitted"],
        "candidate_record_count_mismatch",
        f"records={len(records)}",
    )
    fail_if(
        matrix,
        failures,
        sha256_file(Path(artifacts["event_state_candidate_records"])) != physical_manifest.get("candidate_records_sha256"),
        "candidate_jsonl_hash_not_physical_validation_hash",
        "candidate JSONL hash must match accepted physical validation",
    )
    fail_if(
        matrix,
        failures,
        candidate_manifest.get("candidate_output_status") != "non_official_candidate_evidence_only",
        "candidate_output_status_not_non_official",
        f"observed={candidate_manifest.get('candidate_output_status')}",
    )

    record_ids = [r.get("event_state_record_id", "") for r in records]
    fail_if(matrix, failures, len(set(record_ids)) != len(record_ids), "event_state_record_id_not_unique", "record ids must be unique")

    required_restrictions = set(scope["required_restriction_codes"])
    record_failures: list[str] = []
    for idx, record in enumerate(records, start=1):
        for field, expected in (
            ("event_type_id", identity["event_type_id"]),
            ("event_family_id", identity["event_family_id"]),
            ("event_state_profile_id", identity["event_state_profile_id"]),
            ("event_window_definition_id", identity["event_window_definition_id"]),
            ("state_role", identity["state_role"]),
            ("consumption_legality", identity["consumption_legality"]),
            ("integration_status", identity["integration_status"]),
            ("quality_status", identity["quality_status"]),
            ("source_market_state_profile_id", identity["source_market_state_profile_id"]),
            ("source_market_state_physical_profile_id", identity["source_market_state_physical_profile_id"]),
        ):
            if record.get(field) != expected:
                record_failures.append(f"record_{idx}_{field}_mismatch")
        if not record.get("market_state_record_id") or not record.get("state_output_fingerprint"):
            record_failures.append(f"record_{idx}_missing_market_state_identity_or_fingerprint")
        if record.get("event_anchor_timestamp_utc") != record.get("decision_timestamp_utc"):
            record_failures.append(f"record_{idx}_anchor_decision_mismatch")
        if record.get("event_anchor_timestamp_utc") != record.get("window_start_utc") or record.get("event_anchor_timestamp_utc") != record.get("window_end_utc"):
            record_failures.append(f"record_{idx}_window_anchor_mismatch")
        try:
            restrictions = set(embedded_json(record.get("restriction_codes_json", "[]")))
            missing = required_restrictions.difference(restrictions)
            if missing:
                record_failures.append(f"record_{idx}_missing_required_restrictions")
            embedded_json(record.get("source_lineage_json", "{}"))
            embedded_json(record.get("policy_versions_json", "{}"))
            embedded_json(record.get("source_market_state_value_snapshot_json", "{}"))
        except Exception:
            record_failures.append(f"record_{idx}_embedded_json_unparseable")

    fail_if(matrix, failures, bool(record_failures), "candidate_record_semantic_failures", "|".join(record_failures))

    instance_failures = []
    for row in event_instances:
        if row.get("event_type_id") != identity["event_type_id"]:
            instance_failures.append("event_type_id_mismatch")
        if row.get("event_subject_scope") != identity["event_subject_scope"]:
            instance_failures.append("event_subject_scope_mismatch")
        if row.get("native_identity_includes_instrument_id") != "False":
            instance_failures.append("native_identity_includes_instrument_id")
        if row.get("event_anchor_timestamp_utc") != row.get("session_open_utc"):
            instance_failures.append("anchor_not_session_open")
        if row.get("event_instance_quality_state") != "PASS_WITH_RESTRICTIONS":
            instance_failures.append("event_instance_quality_not_pass")
    fail_if(matrix, failures, len(event_instances) != expected_counts["event_instances_created"], "event_instance_count_mismatch", f"observed={len(event_instances)}")
    fail_if(matrix, failures, bool(instance_failures), "event_instance_semantic_failures", "|".join(sorted(set(instance_failures))))

    window_failures = []
    for row in windows:
        if row.get("state_role") != identity["state_role"]:
            window_failures.append("state_role_mismatch")
        if row.get("consumption_legality") != identity["consumption_legality"]:
            window_failures.append("consumption_legality_mismatch")
        if row.get("window_start_utc") != row.get("event_anchor_timestamp_utc") or row.get("window_end_utc") != row.get("event_anchor_timestamp_utc"):
            window_failures.append("window_not_exact_anchor")
        if row.get("window_duration_seconds") != "0":
            window_failures.append("window_duration_not_zero")
    fail_if(matrix, failures, len(windows) != expected_counts["event_window_bindings_created"], "event_window_count_mismatch", f"observed={len(windows)}")
    fail_if(matrix, failures, bool(window_failures), "event_window_semantic_failures", "|".join(sorted(set(window_failures))))

    projection_failures = []
    for row in projections:
        if row.get("instrument_session_eligibility_state") != "AUTHORIZED_SCOPE_PROJECTION_WITH_RESTRICTIONS":
            projection_failures.append("projection_eligibility_mismatch")
        if row.get("projection_quality_state") != "PASS_WITH_RESTRICTIONS":
            projection_failures.append("projection_quality_mismatch")
    fail_if(matrix, failures, len(projections) != expected_counts["instrument_session_projections_created"], "projection_count_mismatch", f"observed={len(projections)}")
    fail_if(matrix, failures, bool(projection_failures), "projection_semantic_failures", "|".join(sorted(set(projection_failures))))

    bound = [r for r in bindings if r.get("market_state_binding_status") == "BOUND"]
    blocked = [r for r in bindings if r.get("market_state_binding_status") == "BLOCKED"]
    bound_projection_ids = {r["event_state_instrument_session_projection_id"] for r in bound}
    blocked_projection_ids = {r["event_state_instrument_session_projection_id"] for r in blocked}
    record_projection_ids = {r["event_state_instrument_session_projection_id"] for r in records}
    binding_failures = []
    if record_projection_ids != bound_projection_ids:
        binding_failures.append("record_projection_ids_do_not_equal_bound_projection_ids")
    if record_projection_ids.intersection(blocked_projection_ids):
        binding_failures.append("blocked_projection_emitted")
    if any(r.get("fallback_used") != "False" for r in bindings):
        binding_failures.append("fallback_used")
    if any(r.get("blocking_reason") != "missing_exact_market_state_binding" for r in blocked):
        binding_failures.append("unexpected_blocking_reason")
    fail_if(matrix, failures, len(bound) != expected_counts["market_state_bindings_found"], "bound_market_state_count_mismatch", f"observed={len(bound)}")
    fail_if(matrix, failures, len(blocked) != expected_counts["blocked_contexts"], "blocked_context_count_mismatch", f"observed={len(blocked)}")
    fail_if(matrix, failures, bool(binding_failures), "binding_semantic_failures", "|".join(binding_failures))

    physical_restrictions = set(physical_report.get("known_restrictions", []))
    required_known = {
        "bounded_scope_only",
        "non_official_scale_c_market_state_candidate_source",
        "one_context_blocked_by_exact_market_state_binding_policy",
        "instrument_projection_from_authorized_scope_not_master_lifecycle_revalidated",
        "not_downstream_consumable",
    }
    fail_if(
        matrix,
        failures,
        bool(required_known.difference(physical_restrictions)),
        "physical_validation_restrictions_not_preserved",
        ",".join(sorted(required_known.difference(physical_restrictions))),
    )

    closed_boundary_failures = []
    if candidate_manifest.get("event_state_parquet_files_written") != 0:
        closed_boundary_failures.append("event_state_parquet_written")
    for key, expected in scope["closed_boundaries"].items():
        if key in ("event_state_materialization", "official_event_state_profile_promotion", "official_event_state_dataset_promotion", "production", "downstream_consumption"):
            observed = physical_manifest.get(key)
            if observed is not None and observed != expected:
                closed_boundary_failures.append(f"{key}_opened")
    fail_if(matrix, failures, bool(closed_boundary_failures), "closed_boundary_failures", "|".join(closed_boundary_failures))

    finding_status = {
        item: "PASS" for item in scope["required_review_findings"]
    }
    if failures:
        finding_status = {item: "BLOCKED_BY_REVIEW_FAILURES" for item in scope["required_review_findings"]}

    decision = "APPROVED_AS_BOUNDED_CANDIDATE_DATASET_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION"
    if failures:
        decision = "BLOCKED_PENDING_CANDIDATE_DATASET_FINDINGS"

    report = {
        "review_decision": decision,
        "review_failures": failures,
        "candidate_records_reviewed": len(records),
        "event_instances_reviewed": len(event_instances),
        "event_window_bindings_reviewed": len(windows),
        "instrument_session_projections_reviewed": len(projections),
        "market_state_bound_contexts": len(bound),
        "blocked_contexts": len(blocked),
        "blocked_context_keys": [
            {
                "ticker": r.get("ticker"),
                "session_date": r.get("session_date"),
                "event_anchor_timestamp_utc": r.get("event_anchor_timestamp_utc"),
                "blocking_reason": r.get("blocking_reason"),
                "available_same_instrument_session_timestamps": r.get("available_same_instrument_session_timestamps"),
            }
            for r in blocked
        ],
        "finding_status": finding_status,
        "candidate_dataset_status": "non_official_bounded_candidate_evidence_only",
        "next_gate": scope["next_gate_after_approval"] if not failures else "blocked_pending_candidate_dataset_review_fix",
    }
    return report, matrix, failures


def build_readout(summary: dict[str, Any]) -> str:
    return f"""# Event State Candidate Dataset Review Readout v0.1

Status: `{summary['event_state_candidate_dataset_review']}`
Date: `{summary['completed_at_utc'][:10]}`

Reviewed execution run:

```text
{summary['reviewed_execution_run_id']}
```

Reviewed physical validation run:

```text
{summary['reviewed_physical_validation_run_id']}
```

## Decision

```text
review_decision = {summary['review_decision']}
candidate_records_reviewed = {summary['candidate_records_reviewed']}
event_instances_reviewed = {summary['event_instances_reviewed']}
event_window_bindings_reviewed = {summary['event_window_bindings_reviewed']}
instrument_session_projections_reviewed = {summary['instrument_session_projections_reviewed']}
market_state_bound_contexts = {summary['market_state_bound_contexts']}
blocked_contexts = {summary['blocked_contexts']}
review_failures = {summary['review_failure_count']}
hard_review_failures = {summary['hard_review_failures']}
```

The reviewed output is suitable only as bounded candidate Event State evidence.
It is not an official Event State profile, not an official Event State dataset
and not downstream-consumable.

## Blocked Context

```text
ticker = AAME
session_date = 2022-11-25
blocking_reason = missing_exact_market_state_binding
```

The blocked context remains a valid restriction and was not emitted as a partial
Event State record.

## Boundary

```text
event_state_materialization = false
official_event_state_profile_promotion = false
official_event_state_dataset_promotion = false
official_parquet_write = false
production = false
downstream_consumption = false
```

## Next Gate

```text
{summary['next_gate']}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    started = utc_now()
    scope_path = Path(args.scope).resolve()
    scope = load_json(scope_path)
    root = Path(__file__).resolve().parents[1]
    run_id = args.run_id or f"{RUN_ID_PREFIX}_{started.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": iso_z(started),
        "scope_path": str(scope_path),
        "host": socket.gethostname(),
        "user": getpass.getuser(),
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "running", "updated_at_utc": iso_z(utc_now())})

    report, matrix, failures = review_candidate_dataset(scope)
    hard_review_failures = len(failures)
    status = "CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION" if not failures else "CLOSED_BLOCKED_PENDING_FINDINGS"
    completed = utc_now()

    decision_payload = {
        "run_id": run_id,
        "review_decision": report["review_decision"],
        "event_state_candidate_dataset_review": status,
        "accepted_as_candidate_dataset_review_evidence": not failures,
        "promotion_executed": False,
        "official_dataset_created": False,
        "downstream_consumption_authorized": False,
        "next_gate": report["next_gate"],
    }
    write_json(run_dir / "candidate_dataset_review_matrix.json", {"run_id": run_id, "findings": matrix})
    write_json(run_dir / "candidate_dataset_review_report.json", report)
    write_json(run_dir / "candidate_dataset_review_decision.json", decision_payload)

    summary = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": iso_z(started),
        "completed_at_utc": iso_z(completed),
        "scope_path": str(scope_path),
        "reviewed_execution_run_id": scope["review_target"]["execution_run_id"],
        "reviewed_physical_validation_run_id": scope["review_target"]["physical_validation_run_id"],
        "event_state_candidate_dataset_review": status,
        "review_decision": report["review_decision"],
        "candidate_records_reviewed": report["candidate_records_reviewed"],
        "event_instances_reviewed": report["event_instances_reviewed"],
        "event_window_bindings_reviewed": report["event_window_bindings_reviewed"],
        "instrument_session_projections_reviewed": report["instrument_session_projections_reviewed"],
        "market_state_bound_contexts": report["market_state_bound_contexts"],
        "blocked_contexts": report["blocked_contexts"],
        "review_failure_count": len(failures),
        "hard_review_failures": hard_review_failures,
        "official_event_state_profile_promotion": False,
        "official_event_state_dataset_promotion": False,
        "official_parquet_write": False,
        "production": False,
        "downstream_consumption": False,
        "next_gate": report["next_gate"],
        "artifacts": {
            "pre_manifest": str(run_dir / "pre_manifest.json"),
            "heartbeat": str(run_dir / "heartbeat.json"),
            "candidate_dataset_review_matrix": str(run_dir / "candidate_dataset_review_matrix.json"),
            "candidate_dataset_review_report": str(run_dir / "candidate_dataset_review_report.json"),
            "candidate_dataset_review_decision": str(run_dir / "candidate_dataset_review_decision.json"),
            "readout": str(run_dir / "event_state_candidate_dataset_review_readout_v0_1.md"),
            "root_readout": str(root / "event_state_candidate_dataset_review_readout_v0_1.md"),
        },
        "final_manifest_self_hash_policy": "not_recorded_to_avoid_self_referential_hash",
    }

    readout = build_readout(summary)
    Path(summary["artifacts"]["readout"]).write_text(readout, encoding="utf-8", newline="\n")
    Path(summary["artifacts"]["root_readout"]).write_text(readout, encoding="utf-8", newline="\n")
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "complete", "updated_at_utc": iso_z(utc_now())})
    summary["artifacts_sha256"] = {name: sha256_file(Path(path)) for name, path in summary["artifacts"].items()}
    write_json(run_dir / "final_manifest.json", summary)

    print(json.dumps({"run_id": run_id, "status": status, "hard_review_failures": hard_review_failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
