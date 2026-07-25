from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import json
import os
import socket
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "event_state_bounded_execution_chain_physical_validation_v0_1"
RUN_ID_PREFIX = "event_state_bounded_execution_chain_physical_validation_v0_1"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_z(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid_jsonl_line_{line_no}: {exc}") from exc
    return records


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def add_failure(failures: list[str], condition: bool, code: str) -> None:
    if condition:
        failures.append(code)


def parse_embedded_json(value: str, failures: list[str], code: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
        failures.append(code)
        return None


def recompute_record_fingerprint(record: dict[str, Any]) -> str:
    payload = dict(record)
    payload.pop("event_state_record_fingerprint", None)
    payload.pop("created_at_utc", None)
    return sha256_text(stable_json(payload))


def validate_schema(records: list[dict[str, Any]], scope: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    required_fields = scope["required_candidate_record_fields"]
    expected = scope["identity_authority"]
    missing_by_record: list[dict[str, Any]] = []
    value_failures: list[dict[str, str]] = []
    field_counts = Counter()

    for idx, record in enumerate(records, start=1):
        field_counts[len(record)] += 1
        missing = [field for field in required_fields if field not in record]
        if missing:
            missing_by_record.append({"record_ordinal": idx, "missing_fields": missing})
        for field in required_fields:
            if field in record and record[field] is None:
                value_failures.append({"record_ordinal": str(idx), "field": field, "failure": "null_value"})

        for field in (
            "event_type_id",
            "event_family_id",
            "event_state_profile_id",
            "event_state_schema_version",
            "event_window_definition_id",
            "state_role",
            "consumption_legality",
            "relative_time_to_event",
            "integration_policy_id",
            "integration_policy_version",
            "integration_status",
            "quality_status",
        ):
            if record.get(field) != expected[field]:
                value_failures.append(
                    {
                        "record_ordinal": str(idx),
                        "field": field,
                        "failure": f"expected_{expected[field]}_observed_{record.get(field)}",
                    }
                )

        if record.get("source_market_state_profile_id") != expected["source_market_state_semantic_profile_id"]:
            value_failures.append(
                {"record_ordinal": str(idx), "field": "source_market_state_profile_id", "failure": "unexpected_source_market_state_semantic_profile"}
            )
        if record.get("source_market_state_physical_profile_id") != expected["source_market_state_physical_profile_id"]:
            value_failures.append(
                {"record_ordinal": str(idx), "field": "source_market_state_physical_profile_id", "failure": "unexpected_source_market_state_physical_profile"}
            )
        if record.get("event_anchor_timestamp_utc") != record.get("decision_timestamp_utc"):
            value_failures.append({"record_ordinal": str(idx), "field": "decision_timestamp_utc", "failure": "decision_timestamp_not_equal_event_anchor"})
        if record.get("event_anchor_timestamp_utc") != record.get("window_start_utc"):
            value_failures.append({"record_ordinal": str(idx), "field": "window_start_utc", "failure": "window_start_not_equal_event_anchor"})
        if record.get("event_anchor_timestamp_utc") != record.get("window_end_utc"):
            value_failures.append({"record_ordinal": str(idx), "field": "window_end_utc", "failure": "window_end_not_equal_event_anchor"})

    add_failure(failures, bool(missing_by_record), "schema_missing_required_fields")
    add_failure(failures, bool(value_failures), "schema_value_failures")

    report = {
        "records_checked": len(records),
        "required_fields": len(required_fields),
        "field_count_distribution": dict(sorted(field_counts.items())),
        "records_with_missing_fields": missing_by_record,
        "value_failures": value_failures,
        "schema_failures": len(failures),
    }
    return report, failures


def validate_record_fingerprints(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    rows: list[dict[str, Any]] = []
    record_ids = [r.get("event_state_record_id", "") for r in records]
    fingerprints = [r.get("event_state_record_fingerprint", "") for r in records]
    duplicate_record_ids = {k for k, v in Counter(record_ids).items() if v > 1}
    duplicate_fingerprints = {k for k, v in Counter(fingerprints).items() if v > 1}

    for idx, record in enumerate(records, start=1):
        observed = record.get("event_state_record_fingerprint", "")
        recomputed = recompute_record_fingerprint(record)
        status = "PASS" if observed == recomputed else "FAIL"
        if status != "PASS":
            failures.append(f"record_{idx}_fingerprint_mismatch")
        rows.append(
            {
                "record_ordinal": idx,
                "event_state_record_id": record.get("event_state_record_id", ""),
                "observed_event_state_record_fingerprint": observed,
                "recomputed_event_state_record_fingerprint": recomputed,
                "fingerprint_status": status,
                "duplicate_record_id": str(record.get("event_state_record_id", "") in duplicate_record_ids),
                "duplicate_record_fingerprint": str(record.get("event_state_record_fingerprint", "") in duplicate_fingerprints),
            }
        )

    add_failure(failures, bool(duplicate_record_ids), "duplicate_event_state_record_ids")
    add_failure(failures, bool(duplicate_fingerprints), "duplicate_event_state_record_fingerprints")
    return rows, failures


def validate_bindings(records: list[dict[str, Any]], binding_rows: list[dict[str, str]], scope: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    records_by_projection = {r["event_state_instrument_session_projection_id"]: r for r in records}
    rows: list[dict[str, Any]] = []

    bound_rows = [r for r in binding_rows if r.get("market_state_binding_status") == "BOUND"]
    blocked_rows = [r for r in binding_rows if r.get("market_state_binding_status") == "BLOCKED"]
    add_failure(failures, len(binding_rows) != scope["expected_counts"]["instrument_session_projections_created"], "binding_report_row_count_mismatch")
    add_failure(failures, len(bound_rows) != scope["expected_counts"]["market_state_bindings_found"], "binding_bound_count_mismatch")
    add_failure(failures, len(blocked_rows) != scope["expected_counts"]["blocked_contexts"], "binding_blocked_count_mismatch")

    for row in binding_rows:
        projection_id = row.get("event_state_instrument_session_projection_id", "")
        record = records_by_projection.get(projection_id)
        status = row.get("market_state_binding_status")
        expected_record = status == "BOUND"
        actual_record = record is not None
        failure_codes: list[str] = []

        if expected_record and not actual_record:
            failure_codes.append("bound_binding_missing_candidate_record")
        if not expected_record and actual_record:
            failure_codes.append("blocked_binding_emitted_candidate_record")
        if row.get("fallback_used") != "False":
            failure_codes.append("fallback_used_not_false")
        if status == "BOUND":
            if row.get("market_state_rows_found") != "1":
                failure_codes.append("bound_row_not_exactly_one")
            if record:
                if record.get("market_state_record_id") != row.get("market_state_record_id"):
                    failure_codes.append("market_state_record_id_mismatch")
                if record.get("state_output_fingerprint") != row.get("state_output_fingerprint"):
                    failure_codes.append("state_output_fingerprint_mismatch")
                if record.get("decision_timestamp_utc") != row.get("decision_timestamp_utc"):
                    failure_codes.append("decision_timestamp_mismatch")
        if status == "BLOCKED":
            if row.get("blocking_reason") != "missing_exact_market_state_binding":
                failure_codes.append("unexpected_blocking_reason")
            if row.get("market_state_record_id") or row.get("state_output_fingerprint"):
                failure_codes.append("blocked_row_has_market_state_identity")

        failures.extend(f"projection_{projection_id}_{code}" for code in failure_codes)
        rows.append(
            {
                "projection_id": projection_id,
                "ticker": row.get("ticker", ""),
                "session_date": row.get("session_date", ""),
                "binding_status": status,
                "candidate_record_found": str(actual_record),
                "market_state_rows_found": row.get("market_state_rows_found", ""),
                "fallback_used": row.get("fallback_used", ""),
                "blocking_reason": row.get("blocking_reason", ""),
                "validation_status": "PASS" if not failure_codes else "FAIL",
                "failure_codes": "|".join(failure_codes),
            }
        )
    return rows, failures


def validate_lineage(records: list[dict[str, Any]], scope: dict[str, Any], execution_run_id: str) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    required_restrictions = set(scope["required_restriction_codes"])
    value_field_count_failures = 0
    lineage_parse_failures = 0
    policy_parse_failures = 0
    restriction_parse_failures = 0
    value_parse_failures = 0
    lineage_field_failures: list[str] = []
    restriction_failures: list[str] = []

    for idx, record in enumerate(records, start=1):
        lineage = parse_embedded_json(record.get("source_lineage_json", ""), failures, f"record_{idx}_source_lineage_json_unparseable")
        policy_versions = parse_embedded_json(record.get("policy_versions_json", ""), failures, f"record_{idx}_policy_versions_json_unparseable")
        restrictions = parse_embedded_json(record.get("restriction_codes_json", ""), failures, f"record_{idx}_restriction_codes_json_unparseable")
        value_snapshot = parse_embedded_json(record.get("source_market_state_value_snapshot_json", ""), failures, f"record_{idx}_value_snapshot_json_unparseable")

        if not isinstance(lineage, dict):
            lineage_parse_failures += 1
            continue
        if not isinstance(policy_versions, dict):
            policy_parse_failures += 1
        if not isinstance(restrictions, list):
            restriction_parse_failures += 1
        if not isinstance(value_snapshot, dict):
            value_parse_failures += 1

        expected_pairs = {
            "event_state_execution_run_id": execution_run_id,
            "event_instance_id": record.get("event_instance_id"),
            "event_window_binding_id": record.get("event_window_binding_id"),
            "projection_id": record.get("event_state_instrument_session_projection_id"),
            "calendar_row_fingerprint": record.get("calendar_row_fingerprint"),
        }
        for key, expected in expected_pairs.items():
            if lineage.get(key) != expected:
                lineage_field_failures.append(f"record_{idx}_{key}_mismatch")

        if isinstance(restrictions, list):
            missing = sorted(required_restrictions.difference(restrictions))
            if missing:
                restriction_failures.append(f"record_{idx}_missing_restrictions_{','.join(missing)}")

        if isinstance(value_snapshot, dict) and len(value_snapshot) != scope["expected_source_market_state_value_field_count"]:
            value_field_count_failures += 1

    failures.extend(lineage_field_failures)
    failures.extend(restriction_failures)
    if value_field_count_failures:
        failures.append("source_market_state_value_field_count_mismatch")

    report = {
        "records_checked": len(records),
        "lineage_parse_failures": lineage_parse_failures,
        "policy_parse_failures": policy_parse_failures,
        "restriction_parse_failures": restriction_parse_failures,
        "value_snapshot_parse_failures": value_parse_failures,
        "lineage_field_failures": lineage_field_failures,
        "restriction_failures": restriction_failures,
        "value_field_count_failures": value_field_count_failures,
        "lineage_failures": len(failures),
    }
    return report, failures


def build_readout(summary: dict[str, Any]) -> str:
    return f"""# Event State Bounded Execution Chain Physical Validation Readout v0.1

Status: `{summary['event_state_bounded_execution_chain_physical_validation']}`
Date: `{summary['completed_at_utc'][:10]}`

Accepted execution run:

```text
{summary['validated_execution_run_id']}
```

## Summary

```text
candidate_records_checked = {summary['candidate_records_checked']}
requested_contexts = {summary['requested_contexts']}
emitted_candidate_records = {summary['event_state_candidate_records_emitted']}
blocked_contexts = {summary['blocked_contexts']}
missing_exact_market_state_bindings = {summary['missing_exact_market_state_bindings']}

schema_failures = {summary['schema_failures']}
hash_failures = {summary['hash_failures']}
record_fingerprint_failures = {summary['record_fingerprint_failures']}
binding_reconciliation_failures = {summary['binding_reconciliation_failures']}
lineage_failures = {summary['lineage_failures']}
authority_failures = {summary['authority_failures']}
determinism_failures = {summary['determinism_failures']}
unexpected_parquet_outputs = {summary['unexpected_parquet_outputs']}
hard_validation_failures = {summary['hard_validation_failures']}
```

The one blocked context is expected and remains blocked by exact Market State
binding policy. No fallback row was admitted.

## Boundary

```text
event_state_candidate_jsonl_validated = true
event_state_parquet_files_written = 0
official_event_state_profile_promotion = false
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
```

## Restrictions Preserved

```text
bounded_scope_only
non_official_scale_c_market_state_candidate_source
one_context_blocked_by_exact_market_state_binding_policy
instrument_projection_from_authorized_scope_not_master_lifecycle_revalidated
not_downstream_consumable
```

## Next Gate

```text
event_state_candidate_dataset_review_v0_1
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
    runs_root = root / "runs"
    run_id = args.run_id or f"{RUN_ID_PREFIX}_{started.strftime('%Y%m%dT%H%M%SZ')}"
    output_dir = runs_root / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    execution_final_manifest_path = Path(scope["validation_target"]["execution_final_manifest"])
    execution_manifest = load_json(execution_final_manifest_path)
    execution_run_dir = Path(scope["validation_target"]["execution_run_dir"])
    execution_run_id = scope["validation_target"]["execution_run_id"]

    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": iso_z(started),
        "scope_path": str(scope_path),
        "validated_execution_run_id": execution_run_id,
        "validated_execution_final_manifest": str(execution_final_manifest_path),
        "host": socket.gethostname(),
        "user": getpass.getuser(),
    }
    write_json(output_dir / "pre_manifest.json", pre_manifest)
    write_json(output_dir / "heartbeat.json", {"run_id": run_id, "status": "running", "updated_at_utc": iso_z(utc_now())})

    failures: list[str] = []
    hash_failures: list[str] = []

    add_failure(
        failures,
        execution_manifest.get("event_state_bounded_execution_chain_execution") != scope["validation_target"]["execution_status_required"],
        "execution_status_mismatch",
    )
    add_failure(failures, execution_manifest.get("run_id") != execution_run_id, "execution_run_id_mismatch")

    artifacts = execution_manifest.get("artifacts", {})
    artifacts_sha256 = execution_manifest.get("artifacts_sha256", {})
    for name, path_value in artifacts.items():
        if name == "final_manifest":
            continue
        path = Path(path_value)
        if not path.exists():
            hash_failures.append(f"{name}_missing")
            continue
        expected_hash = artifacts_sha256.get(name)
        if expected_hash and sha256_file(path) != expected_hash:
            hash_failures.append(f"{name}_hash_mismatch")
    failures.extend(hash_failures)

    candidate_manifest = load_json(Path(artifacts["event_state_candidate_manifest"]))
    validation_report = load_json(Path(artifacts["event_state_validation_report"]))
    determinism_report = load_json(Path(artifacts["determinism_report"]))
    records_path = Path(artifacts["event_state_candidate_records"])
    binding_rows = read_csv(Path(artifacts["market_state_binding_report"]))
    records = read_jsonl(records_path)

    expected_counts = scope["expected_counts"]
    for key, expected in expected_counts.items():
        observed = execution_manifest.get(key, validation_report.get(key))
        add_failure(failures, observed != expected, f"count_{key}_expected_{expected}_observed_{observed}")

    candidate_records_hash = sha256_file(records_path)
    add_failure(
        failures,
        candidate_records_hash != candidate_manifest.get("event_state_candidate_records_sha256"),
        "candidate_records_hash_mismatch_candidate_manifest",
    )
    add_failure(
        failures,
        candidate_records_hash != artifacts_sha256.get("event_state_candidate_records"),
        "candidate_records_hash_mismatch_final_manifest",
    )
    add_failure(failures, len(records) != expected_counts["event_state_candidate_records_emitted"], "candidate_record_count_mismatch")

    schema_report, schema_failures = validate_schema(records, scope)
    fingerprint_rows, fingerprint_failures = validate_record_fingerprints(records)
    binding_reconciliation_rows, binding_failures = validate_bindings(records, binding_rows, scope)
    lineage_report, lineage_failures = validate_lineage(records, scope, execution_run_id)

    failures.extend(schema_failures)
    failures.extend(fingerprint_failures)
    failures.extend(binding_failures)
    failures.extend(lineage_failures)

    determinism_failures = 0
    expected_record_ids = [r["event_state_record_id"] for r in records]
    expected_record_fingerprints = [r["event_state_record_fingerprint"] for r in records]
    if determinism_report.get("status") != "PASS":
        determinism_failures += 1
    if determinism_report.get("event_state_record_ids") != expected_record_ids:
        determinism_failures += 1
    if determinism_report.get("event_state_record_fingerprints") != expected_record_fingerprints:
        determinism_failures += 1
    if determinism_report.get("determinism_failures") != 0:
        determinism_failures += int(determinism_report.get("determinism_failures", 1))
    if determinism_failures:
        failures.append("determinism_evidence_mismatch")

    event_state_parquet_outputs = sorted(str(p) for p in execution_run_dir.glob("*event_state*.parquet"))
    unexpected_parquet_outputs = len(event_state_parquet_outputs)
    if unexpected_parquet_outputs:
        failures.append("unexpected_event_state_parquet_outputs")

    authority_flags = {
        "event_state_parquet_files_written": execution_manifest.get("event_state_parquet_files_written", candidate_manifest.get("event_state_parquet_files_written")),
        "official_event_state_profile_promotion": execution_manifest.get(
            "official_event_state_profile_promotion",
            validation_report.get("official_event_state_profile_promotion"),
        ),
        "official_event_state_dataset_promotion": execution_manifest.get("official_event_state_dataset_promotion"),
        "production": execution_manifest.get("production", validation_report.get("production")),
        "downstream_consumption": execution_manifest.get("downstream_consumption"),
        "source_market_data_rows_read": validation_report.get("source_market_data_rows_read"),
        "fallback_uses": execution_manifest.get("fallback_uses"),
        "partial_event_state_records": validation_report.get("partial_event_state_records"),
    }
    authority_failures = []
    expected_authority = {
        "event_state_parquet_files_written": 0,
        "official_event_state_profile_promotion": False,
        "official_event_state_dataset_promotion": False,
        "production": False,
        "downstream_consumption": False,
        "source_market_data_rows_read": 0,
        "fallback_uses": 0,
        "partial_event_state_records": 0,
    }
    for key, expected in expected_authority.items():
        if authority_flags.get(key) != expected:
            authority_failures.append(f"{key}_expected_{expected}_observed_{authority_flags.get(key)}")
    failures.extend(authority_failures)

    write_json(output_dir / "schema_validation_report.json", schema_report)
    write_csv(
        output_dir / "record_fingerprint_validation_report.csv",
        fingerprint_rows,
        [
            "record_ordinal",
            "event_state_record_id",
            "observed_event_state_record_fingerprint",
            "recomputed_event_state_record_fingerprint",
            "fingerprint_status",
            "duplicate_record_id",
            "duplicate_record_fingerprint",
        ],
    )
    write_csv(
        output_dir / "binding_reconciliation_report.csv",
        binding_reconciliation_rows,
        [
            "projection_id",
            "ticker",
            "session_date",
            "binding_status",
            "candidate_record_found",
            "market_state_rows_found",
            "fallback_used",
            "blocking_reason",
            "validation_status",
            "failure_codes",
        ],
    )
    write_json(output_dir / "lineage_validation_report.json", lineage_report)
    write_json(
        output_dir / "authority_boundary_report.json",
        {
            "authority_flags": authority_flags,
            "authority_failures": authority_failures,
            "unexpected_event_state_parquet_outputs": unexpected_parquet_outputs,
            "event_state_parquet_outputs": event_state_parquet_outputs,
        },
    )
    write_json(
        output_dir / "determinism_validation_report.json",
        {
            "source_determinism_status": determinism_report.get("status"),
            "determinism_failures": determinism_failures,
            "record_ids_match": determinism_report.get("event_state_record_ids") == expected_record_ids,
            "record_fingerprints_match": determinism_report.get("event_state_record_fingerprints") == expected_record_fingerprints,
        },
    )

    hard_validation_failures = len(failures)
    status = "CLOSED_PASS_WITH_RESTRICTIONS" if hard_validation_failures == 0 else "CLOSED_FAILED_PHYSICAL_VALIDATION"
    completed = utc_now()
    physical_report = {
        "run_id": run_id,
        "validated_execution_run_id": execution_run_id,
        "physical_validation_status": status,
        "candidate_records_checked": len(records),
        "hard_validation_failures": hard_validation_failures,
        "failure_codes": failures,
        "known_restrictions": candidate_manifest.get("known_restrictions", []),
    }
    write_json(output_dir / "physical_validation_report.json", physical_report)

    summary = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": iso_z(started),
        "completed_at_utc": iso_z(completed),
        "scope_path": str(scope_path),
        "validated_execution_run_id": execution_run_id,
        "validated_execution_final_manifest": str(execution_final_manifest_path),
        "event_state_bounded_execution_chain_physical_validation": status,
        "candidate_records_checked": len(records),
        "requested_contexts": execution_manifest.get("requested_contexts"),
        "event_state_candidate_records_emitted": execution_manifest.get("event_state_candidate_records_emitted"),
        "blocked_contexts": execution_manifest.get("blocked_contexts"),
        "missing_exact_market_state_bindings": execution_manifest.get("missing_exact_market_state_bindings"),
        "schema_failures": len(schema_failures),
        "hash_failures": len(hash_failures),
        "record_fingerprint_failures": len(fingerprint_failures),
        "binding_reconciliation_failures": len(binding_failures),
        "lineage_failures": len(lineage_failures),
        "authority_failures": len(authority_failures),
        "determinism_failures": determinism_failures,
        "unexpected_parquet_outputs": unexpected_parquet_outputs,
        "hard_validation_failures": hard_validation_failures,
        "candidate_records_sha256": candidate_records_hash,
        "official_event_state_profile_promotion": False,
        "official_event_state_dataset_promotion": False,
        "production": False,
        "downstream_consumption": False,
        "next_gate": scope["next_gate_after_pass"] if hard_validation_failures == 0 else "blocked_pending_physical_validation_fix",
        "artifacts": {
            "pre_manifest": str(output_dir / "pre_manifest.json"),
            "heartbeat": str(output_dir / "heartbeat.json"),
            "schema_validation_report": str(output_dir / "schema_validation_report.json"),
            "record_fingerprint_validation_report": str(output_dir / "record_fingerprint_validation_report.csv"),
            "binding_reconciliation_report": str(output_dir / "binding_reconciliation_report.csv"),
            "lineage_validation_report": str(output_dir / "lineage_validation_report.json"),
            "authority_boundary_report": str(output_dir / "authority_boundary_report.json"),
            "determinism_validation_report": str(output_dir / "determinism_validation_report.json"),
            "physical_validation_report": str(output_dir / "physical_validation_report.json"),
            "readout": str(output_dir / "event_state_bounded_execution_chain_physical_validation_readout_v0_1.md"),
        },
        "final_manifest_self_hash_policy": "not_recorded_to_avoid_self_referential_hash",
    }

    readout_text = build_readout(summary)
    readout_path = output_dir / "event_state_bounded_execution_chain_physical_validation_readout_v0_1.md"
    readout_path.write_text(readout_text, encoding="utf-8", newline="\n")
    root_readout = root / "event_state_bounded_execution_chain_physical_validation_readout_v0_1.md"
    root_readout.write_text(readout_text, encoding="utf-8", newline="\n")
    summary["artifacts"]["root_readout"] = str(root_readout)

    write_json(output_dir / "heartbeat.json", {"run_id": run_id, "status": "complete", "updated_at_utc": iso_z(utc_now())})
    artifact_hashes = {}
    for key, path_value in summary["artifacts"].items():
        artifact_hashes[key] = sha256_file(Path(path_value))
    summary["artifacts_sha256"] = artifact_hashes
    write_json(output_dir / "final_manifest.json", summary)

    print(json.dumps({"run_id": run_id, "status": status, "hard_validation_failures": hard_validation_failures}, indent=2))
    return 0 if hard_validation_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
