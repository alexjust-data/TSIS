from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


SCRIPT_VERSION = "market_state_on_demand_second_generation_incremental_extension_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
FEATURE_ROOT = BASE.parent
MARKET_ROOT = FEATURE_ROOT / "06_MARKET_STATE_INTEGRATION"
OUTPUT_ROOT = BASE / "runs"

BOUNDED_RUNNER_PATH = BASE / "scripts" / "market_state_bounded_on_demand_execution_runner_v0_1.py"
AUTH_SCOPE_PATH = BASE / "configs" / "market_state_on_demand_second_generation_incremental_extension_scope_v0_1.json"
AUTH_CONTRACT_PATH = BASE / "market_state_on_demand_second_generation_incremental_extension_contract_v0_1.json"
VALIDATOR_CONTRACT_PATH = BASE / "market_state_validator_contract_v0_1.json"
SOURCE_MATERIALIZATION_SCOPE_PATH = (
    MARKET_ROOT / "configs" / "experimental_core_four_market_state_scale_c_candidate_materialization_scope_v0_1.json"
)
PROFILE_ROOT = MARKET_ROOT / "official_profiles" / "market_state_core_four_intraday_profile_v0_1"
PROFILE_MANIFEST_PATH = PROFILE_ROOT / "PROFILE_MANIFEST.json"
PROFILE_SCHEMA_PATH = PROFILE_ROOT / "PHYSICAL_SCHEMA_CONTRACT.json"

BASELINE_RUN_ID = "market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z"
BASELINE_RUN_DIR = OUTPUT_ROOT / BASELINE_RUN_ID
PARENT_REUSE_RUN_ID = "market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1_20260727T094006Z"
PARENT_REUSE_RUN_DIR = OUTPUT_ROOT / PARENT_REUSE_RUN_ID
COMBINED_CONTEXT_LEDGER_PATH = BASE / "combined_candidate_context_ledger_v0_1.json"


class IncrementalExecutionError(RuntimeError):
    pass


def load_bounded_runner() -> Any:
    spec = importlib.util.spec_from_file_location("bounded_market_state_runner", BOUNDED_RUNNER_PATH)
    if not spec or not spec.loader:
        raise IncrementalExecutionError(f"Cannot import bounded runner: {BOUNDED_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bounded = load_bounded_runner()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def hash_excluding(payload: dict[str, Any], excluded_key: str) -> str:
    return sha256_payload({k: v for k, v in payload.items() if k != excluded_key})


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
                raise IncrementalExecutionError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n")


def serialize_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: serialize_cell(row.get(k)) for k in fieldnames})


def normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return value


def require_file(path: Path) -> None:
    if not path.exists():
        raise IncrementalExecutionError(f"Required file missing: {path}")


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def context_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["instrument_id"], row["session_date"], row["decision_timestamp_utc"])


def build_request_c(scope: dict[str, Any]) -> tuple[dict[str, Any], str]:
    instruments = [item["instrument_id"] for item in scope["instrument_scope"]]
    labels = {item["instrument_id"]: item["ticker"] for item in scope["instrument_scope"]}
    sessions = scope["session_scope"]["all_requested_sessions"]
    template = {
        "request_type": "market_state",
        "request_contract_version": "market_state_request_contract_v0_1",
        "profile_id": scope["requested_profile"]["profile_id"],
        "profile_version": "v0_1",
        "profile_version_policy": "exact",
        "resolution": "1m",
        "grain": "instrument_decision_timestamp",
        "universe_definition_id": "explicit_instrument_ids",
        "explicit_instrument_ids": instruments,
        "instrument_labels_non_authoritative": labels,
        "session_dates": sessions,
        "exchange_scope": scope["exchange_scope"],
        "calendar_authority_id": "governed_exchange_session_calendar_xnys_v0_1",
        "point_in_time_policy_id": "bounded_explicit_scope_not_revalidated_v0_1",
        "source_version_policy": "exact_governed_or_block",
        "output_mode": "candidate_second_generation_incremental",
        "output_format": "parquet_delta2_plus_reuse_manifest",
        "reuse_policy": "reuse_proven_combined_candidate_and_build_second_delta_only",
        "validation_level": "bounded_second_generation_incremental",
    }
    request_fingerprint = sha256_payload(template)
    request = {
        "request_id": "market_state_request_incremental_gen2_v0_1_" + request_fingerprint[:16],
        "request_status": "accepted_for_second_generation_incremental_resolution",
        "requested_at_utc": utc_now(),
        "requested_by": os.environ.get("USERNAME") or os.environ.get("USER"),
        "request_purpose": "bounded_second_generation_incremental_extension_probe",
        **template,
        "request_fingerprint": request_fingerprint,
    }
    return request, request_fingerprint


def make_logical_partition_id(profile_id: str, instrument_id: str, session_date_value: str, anchor: str) -> str:
    return sha256_payload(
        {
            "profile_id": profile_id,
            "instrument_id": instrument_id,
            "session_date": session_date_value,
            "decision_timestamp_utc": anchor,
        }
    )


def main() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    for path in [
        BOUNDED_RUNNER_PATH,
        AUTH_SCOPE_PATH,
        AUTH_CONTRACT_PATH,
        VALIDATOR_CONTRACT_PATH,
        SOURCE_MATERIALIZATION_SCOPE_PATH,
        PROFILE_MANIFEST_PATH,
        PROFILE_SCHEMA_PATH,
        BASELINE_RUN_DIR / "final_manifest.json",
        BASELINE_RUN_DIR / "candidate_registry_entry.json",
        BASELINE_RUN_DIR / "candidate_output_manifest.json",
        BASELINE_RUN_DIR / "partition_coverage_resolution_report.json",
        BASELINE_RUN_DIR / "market_state_validation_report.json",
        PARENT_REUSE_RUN_DIR / "final_manifest.json",
        PARENT_REUSE_RUN_DIR / "reuse_hit_evidence.json",
        COMBINED_CONTEXT_LEDGER_PATH,
    ]:
        require_file(path)

    scope = read_json(AUTH_SCOPE_PATH)
    contract = read_json(AUTH_CONTRACT_PATH)
    source_scope = read_json(SOURCE_MATERIALIZATION_SCOPE_PATH)
    profile_manifest = read_json(PROFILE_MANIFEST_PATH)
    schema_contract = read_json(PROFILE_SCHEMA_PATH)
    validator_contract = read_json(VALIDATOR_CONTRACT_PATH)
    baseline_final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    baseline_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    baseline_output_manifest = read_json(BASELINE_RUN_DIR / "candidate_output_manifest.json")
    baseline_partition_coverage = read_json(BASELINE_RUN_DIR / "partition_coverage_resolution_report.json")
    baseline_validation = read_json(BASELINE_RUN_DIR / "market_state_validation_report.json")
    parent_reuse_final = read_json(PARENT_REUSE_RUN_DIR / "final_manifest.json")
    parent_reuse_evidence = read_json(PARENT_REUSE_RUN_DIR / "reuse_hit_evidence.json")
    combined_context_ledger = read_json(COMBINED_CONTEXT_LEDGER_PATH)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"market_state_on_demand_second_generation_incremental_extension_v0_1_{timestamp}"
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists():
        raise IncrementalExecutionError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    source_records_path_for_preflight = Path(scope["second_delta_source_scope_evidence"]["source_candidate_records_path"])
    observed_combined_ledger_hash = hash_excluding(combined_context_ledger, "context_ledger_sha256")
    preflight_checks = {
        "scope_status_authorized": scope.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "scope_next_gate_match": scope.get("authorized_next_gate")
        == "market_state_on_demand_second_generation_incremental_extension_v0_1",
        "contract_status_authorized": contract.get("status") == "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "contract_next_gate_match": contract.get("authorized_next_gate")
        == "market_state_on_demand_second_generation_incremental_extension_v0_1",
        "baseline_run_match": baseline_final.get("run_id") == BASELINE_RUN_ID,
        "baseline_dataset_id_match": baseline_registry.get("dataset_id") == contract["base_combined_candidate"]["dataset_id"],
        "baseline_candidate_dataset_fingerprint_match": baseline_registry.get("candidate_dataset_fingerprint")
        == contract["base_combined_candidate"]["candidate_dataset_fingerprint"],
        "baseline_scientific_dataset_fingerprint_match": baseline_registry.get("scientific_dataset_fingerprint")
        == contract["base_combined_candidate"]["scientific_dataset_fingerprint"],
        "baseline_validation_pass_with_restrictions": baseline_validation.get("validation_status") == "PASS_WITH_RESTRICTIONS",
        "parent_reuse_run_match": parent_reuse_final.get("run_id") == PARENT_REUSE_RUN_ID,
        "parent_reuse_status_match": parent_reuse_final.get("status") == contract["parent_reuse_test"]["status"],
        "parent_reuse_idempotency_match": parent_reuse_final.get("idempotency_status")
        == contract["parent_reuse_test"]["idempotency_status"],
        "parent_reuse_dataset_match": parent_reuse_final.get("selected_dataset_id")
        == contract["base_combined_candidate"]["dataset_id"],
        "parent_reuse_evidence_dataset_match": parent_reuse_evidence.get("selected_dataset_id")
        == contract["base_combined_candidate"]["dataset_id"],
        "parent_reuse_no_materializer": parent_reuse_final.get("materializer_executions") == 0,
        "parent_reuse_no_delta_materializer": parent_reuse_final.get("delta_materializer_executions") == 0,
        "parent_reuse_no_source_rows": parent_reuse_final.get("source_market_data_rows_read") == 0,
        "combined_context_ledger_hash_match": observed_combined_ledger_hash
        == contract["base_combined_candidate"]["combined_context_ledger_sha256"],
        "second_delta_source_sha_match": sha256_file(source_records_path_for_preflight)
        == scope["second_delta_source_scope_evidence"]["source_candidate_records_sha256"],
        "authorized_context_count": contract["request_c_scope"]["requested_context_count"]
        == scope["quantitative_limits"]["maximum_requested_contexts"],
    }
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
        print(json.dumps(final_manifest, indent=2, ensure_ascii=False))
        return 2

    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

    request, request_fingerprint = build_request_c(scope)
    write_json(run_dir / "request_record.json", request)

    column_order, column_defs, arrow_schema = bounded.schema_from_contract(schema_contract)
    schema_version = schema_contract["state_schema_version"]
    profile_id = request["profile_id"]
    profile_resolution = {
        "resolution_status": "RESOLVED_EXACTLY_ONE",
        "resolved_profile_id": profile_id,
        "resolved_profile_version": request["profile_version"],
        "profile_manifest": str(PROFILE_MANIFEST_PATH),
        "profile_manifest_sha256": sha256_file(PROFILE_MANIFEST_PATH),
        "profile_schema_contract": str(PROFILE_SCHEMA_PATH),
        "profile_schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
        "expected_schema_id": schema_contract["source_physical_profile_id"],
        "expected_state_schema_version": schema_version,
        "expected_grain": request["grain"],
        "required_source_aliases": ["scale_c_integrated_market_state_candidate_records"],
        "profile_artifact_validation_run": profile_manifest.get("artifact_validation_run_id"),
    }
    resolved_profile_fingerprint = sha256_payload(profile_resolution)
    profile_resolution["resolved_profile_fingerprint"] = resolved_profile_fingerprint
    write_json(run_dir / "profile_resolution_report.json", profile_resolution)

    source_records_path = Path(scope["second_delta_source_scope_evidence"]["source_candidate_records_path"]).resolve()
    records = read_jsonl(source_records_path)
    source_records_read = len(records)
    source_sha = sha256_file(source_records_path)
    if source_sha != scope["second_delta_source_scope_evidence"]["source_candidate_records_sha256"]:
        raise IncrementalExecutionError("Authorized source sha256 mismatch")

    session_open_by_date: dict[str, str] = {}
    available_by_instrument_session: dict[tuple[str, str], list[str]] = {}
    exact_record_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in records:
        session_open_by_date.setdefault(record["session_date"], record["session_open_utc"])
        available_by_instrument_session.setdefault((record["instrument_id"], record["session_date"]), []).append(
            record["decision_timestamp_utc"]
        )
        exact_record_by_key[(record["instrument_id"], record["session_date"], record["decision_timestamp_utc"])] = record

    baseline_reusable: dict[tuple[str, str, str], dict[str, Any]] = {}
    baseline_unavailable: dict[tuple[str, str, str], dict[str, Any]] = {}
    for part in baseline_partition_coverage["partitions"]:
        key = context_key(part)
        if part["partition_disposition"] in {"reusable_validated", "to_build"}:
            baseline_reusable[key] = part
        elif part["partition_disposition"] == "unavailable":
            baseline_unavailable[key] = part

    universe_contexts: list[dict[str, Any]] = []
    partition_rows: list[dict[str, Any]] = []
    delta_records: list[dict[str, Any]] = []
    unavailable_contexts: list[dict[str, Any]] = []
    reused_contexts: list[dict[str, Any]] = []
    baseline_sessions = set(scope["session_scope"]["base_sessions"])
    delta_sessions = set(scope["session_scope"]["second_delta_sessions"])

    for session_date_value in request["session_dates"]:
        anchor = scope["decision_timestamps_utc"][session_date_value]
        for instrument_id in request["explicit_instrument_ids"]:
            ticker = request["instrument_labels_non_authoritative"].get(instrument_id, "")
            context = {
                "instrument_id": instrument_id,
                "ticker_label_non_authoritative": ticker,
                "session_date": session_date_value,
                "exchange_id": scope["exchange_scope"],
                "decision_timestamp_utc": anchor,
                "calendar_authority_id": request["calendar_authority_id"],
                "membership_status": "AUTHORIZED_EXPLICIT_SCOPE",
                "point_in_time_eligibility": "not_revalidated_in_second_generation_incremental_run",
            }
            universe_contexts.append(context)
            logical_partition_id = make_logical_partition_id(profile_id, instrument_id, session_date_value, anchor)
            key = (instrument_id, session_date_value, anchor)
            available = sorted(set(available_by_instrument_session.get((instrument_id, session_date_value), [])))
            disposition = "blocked"
            cause = "unclassified_partition"
            source_record = exact_record_by_key.get(key)

            if session_date_value in baseline_sessions:
                if key in baseline_reusable:
                    disposition = "reusable_validated"
                    cause = "selected_from_reuse_proven_combined_candidate_dataset"
                    reused_contexts.append({**context, "logical_partition_id": logical_partition_id})
                elif key in baseline_unavailable:
                    disposition = "unavailable"
                    cause = baseline_unavailable[key].get(
                        "disposition_cause", "missing_exact_decision_timestamp_source_candidate_record"
                    )
                    unavailable_contexts.append(
                        {
                            **context,
                            "logical_partition_id": logical_partition_id,
                            "disposition": disposition,
                            "blocking_reason": cause,
                            "available_same_instrument_session_timestamps": available,
                        }
                    )
                else:
                    disposition = "blocked"
                    cause = "base_combined_context_not_found_in_reusable_or_unavailable_partition_set"
            elif session_date_value in delta_sessions:
                if source_record:
                    disposition = "to_build"
                    cause = "second_delta_source_candidate_record_exact_match_found"
                    delta_records.append(source_record)
                else:
                    disposition = "unavailable"
                    cause = "second_delta_missing_exact_decision_timestamp_source_candidate_record"
                    unavailable_contexts.append(
                        {
                            **context,
                            "logical_partition_id": logical_partition_id,
                            "disposition": disposition,
                            "blocking_reason": cause,
                            "available_same_instrument_session_timestamps": available,
                        }
                    )

            partition_rows.append(
                {
                    **context,
                    "logical_partition_id": logical_partition_id,
                    "partition_disposition": disposition,
                    "disposition_cause": cause,
                    "available_same_instrument_session_timestamps": available,
                }
            )

    disposition_counts = Counter(row["partition_disposition"] for row in partition_rows)
    expected = contract["required_execution_plan_dispositions"]
    disposition_expectation_pass = (
        disposition_counts["reusable_validated"] == expected["expected_reusable_validated"]
        and disposition_counts["unavailable"] == expected["expected_known_unavailable"]
        and disposition_counts["to_build"] == expected["expected_to_build_second_delta"]
        and len(partition_rows) == expected["requested_logical_partitions"]
    )

    universe_resolution = {
        "resolution_status": "RESOLVED_WITH_RESTRICTIONS",
        "resolved_universe_definition_id": "explicit_instrument_ids",
        "instrument_count": len(request["explicit_instrument_ids"]),
        "session_count": len(request["session_dates"]),
        "requested_contexts": len(universe_contexts),
        "resolved_contexts": len(universe_contexts),
        "blocked_contexts": disposition_counts["blocked"],
        "excluded_contexts": 0,
        "contexts": universe_contexts,
    }
    resolved_universe_fingerprint = sha256_payload(universe_resolution)
    universe_resolution["resolved_universe_fingerprint"] = resolved_universe_fingerprint
    write_json(run_dir / "universe_resolution_report.json", universe_resolution)

    source_resolution = {
        "resolution_status": "RESOLVED_EXACTLY_ONE",
        "resolved_source_alias": "scale_c_integrated_market_state_candidate_records",
        "source_artifact_kind": "integrated_market_state_candidate_records_jsonl",
        "source_path": str(source_records_path),
        "source_sha256": source_sha,
        "source_bytes": source_records_path.stat().st_size,
        "source_candidate_records_read": source_records_read,
        "source_market_data_rows_read": 0,
        "source_scope_contract": str(SOURCE_MATERIALIZATION_SCOPE_PATH),
        "source_scope_contract_sha256": sha256_file(SOURCE_MATERIALIZATION_SCOPE_PATH),
        "source_version_policy": request["source_version_policy"],
        "fallback_used": False,
    }
    resolved_source_set_fingerprint = sha256_payload(source_resolution)
    source_resolution["resolved_source_set_fingerprint"] = resolved_source_set_fingerprint
    write_json(run_dir / "source_resolution_report.json", source_resolution)

    partition_coverage = {
        "resolution_status": "SECOND_GENERATION_INCREMENTAL_PARTIALLY_BUILDABLE_WITH_RESTRICTIONS",
        "logical_partition_grain": "profile_id+instrument_id+session_date+decision_timestamp_utc",
        "requested_logical_partitions": len(partition_rows),
        "reusable_validated": disposition_counts["reusable_validated"],
        "to_build": disposition_counts["to_build"],
        "to_rebuild": disposition_counts["to_rebuild"],
        "unavailable": disposition_counts["unavailable"],
        "quarantined": disposition_counts["quarantined"],
        "blocked": disposition_counts["blocked"],
        "missing_is_independent_disposition": False,
        "missing_source_coverage_policy": "cause_of_unavailable",
        "partial_execution_policy": "allowed_for_preserved_unavailable_partition_plus_second_delta_build_only",
        "base_combined_candidate_dataset_id": contract["base_combined_candidate"]["dataset_id"],
        "base_combined_candidate_dataset_fingerprint": contract["base_combined_candidate"]["candidate_dataset_fingerprint"],
        "disposition_expectation_pass": disposition_expectation_pass,
        "partitions": partition_rows,
    }
    partition_coverage_fingerprint = sha256_payload(partition_coverage)
    partition_coverage["partition_coverage_resolution_fingerprint"] = partition_coverage_fingerprint
    write_json(run_dir / "partition_coverage_resolution_report.json", partition_coverage)
    write_csv(
        run_dir / "partition_coverage_resolution_report.csv",
        partition_rows,
        [
            "logical_partition_id",
            "instrument_id",
            "ticker_label_non_authoritative",
            "session_date",
            "exchange_id",
            "decision_timestamp_utc",
            "partition_disposition",
            "disposition_cause",
            "available_same_instrument_session_timestamps",
        ],
    )

    execution_plan = {
        "execution_plan_id": "market_state_execution_plan_incremental_gen2_v0_1_" + sha256_payload(partition_coverage)[:16],
        "execution_plan_contract_version": "market_state_execution_plan_contract_v0_1",
        "execution_plan_status": "authorized_for_second_generation_incremental_extension",
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "resolved_profile": profile_resolution,
        "resolved_universe_and_scope": universe_resolution,
        "resolved_sources": source_resolution,
        "partition_and_coverage": partition_coverage,
        "base_combined_reuse": {
            "base_combined_run_id": BASELINE_RUN_ID,
            "base_combined_candidate_dataset_id": contract["base_combined_candidate"]["dataset_id"],
            "base_combined_candidate_dataset_fingerprint": contract["base_combined_candidate"]["candidate_dataset_fingerprint"],
            "base_combined_scientific_dataset_fingerprint": contract["base_combined_candidate"]["scientific_dataset_fingerprint"],
            "parent_reuse_run_id": PARENT_REUSE_RUN_ID,
            "parent_reuse_status": parent_reuse_final.get("status"),
            "reused_context_count": disposition_counts["reusable_validated"],
        },
        "second_delta_build_plan": {
            "second_delta_sessions": scope["session_scope"]["second_delta_sessions"],
            "second_delta_contexts_to_build": disposition_counts["to_build"],
            "builder_id": "scale_c_integrated_candidate_record_to_market_state_physical_row_v0_1",
            "builder_contract_hash": sha256_file(SOURCE_MATERIALIZATION_SCOPE_PATH),
        },
        "resolved_validators": {
            "validator_id": "market_state_second_generation_incremental_validator_v0_1",
            "validator_contract_hash": sha256_file(VALIDATOR_CONTRACT_PATH),
        },
        "output_plan": {
            "output_mode": "candidate_second_generation_incremental",
            "candidate_output_root": str(run_dir),
            "second_delta_parquet_filename": "market_state_second_generation_delta_candidate_v0_1.parquet",
            "candidate_registry_entry_filename": "candidate_registry_entry.json",
        },
        "quantitative_limits": scope["quantitative_limits"],
    }
    execution_plan_fingerprint = sha256_payload(execution_plan)
    execution_plan["execution_plan_fingerprint"] = execution_plan_fingerprint
    write_json(run_dir / "execution_plan.json", execution_plan)

    authorization_consumption = {
        "authorization_id": scope["scope_id"],
        "authorization_document_status_observed": scope["status"],
        "authorization_consumption_status": "CONSUMED_BY_SECOND_GENERATION_INCREMENTAL_EXTENSION_RUN",
        "execution_run_id": run_id,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "consumed_at_utc": utc_now(),
    }
    write_json(run_dir / "authorization_consumption_record.json", authorization_consumption)

    pre_manifest = {
        "run_id": run_id,
        "status": "AUTHORIZED",
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_dirty_state": git_dirty_state,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "run_dir": str(run_dir),
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "pre_run_manifest.json", pre_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {"run_id": run_id, "observed_at_utc": utc_now(), "status": "RUNNING", "stage": "materializing_delta"},
    )

    physical_rows = [
        bounded.build_row(record, run_id, profile_id, schema_version, source_scope, column_order, column_defs)
        for record in sorted(delta_records, key=lambda r: (r["session_date"], r["instrument_id"], r["decision_timestamp_utc"]))
    ]
    table = pa.Table.from_pylist(physical_rows, schema=arrow_schema)
    delta_parquet_path = run_dir / "market_state_second_generation_delta_candidate_v0_1.parquet"
    pq.write_table(
        table,
        delta_parquet_path,
        compression="snappy",
        use_dictionary=False,
        row_group_size=max(1, len(physical_rows)),
        coerce_timestamps="us",
    )
    delta_parquet_sha = sha256_file(delta_parquet_path)
    delta_rows_jsonl = run_dir / "delta_market_state_rows.jsonl"
    write_jsonl(delta_rows_jsonl, [{k: normalize(v) for k, v in row.items()} for row in physical_rows])

    delta_state_output_fingerprints = sorted(row["state_output_fingerprint"] for row in physical_rows)
    scientific_dataset_fingerprint = sha256_payload(
        {
            "base_combined_scientific_dataset_fingerprint": contract["base_combined_candidate"]["scientific_dataset_fingerprint"],
            "delta_state_output_fingerprints": delta_state_output_fingerprints,
            "known_unavailable_contexts": unavailable_contexts,
            "scope": {
                "profile_id": profile_id,
                "requested_sessions": request["session_dates"],
                "instrument_ids": request["explicit_instrument_ids"],
            },
        }
    )
    candidate_dataset_fingerprint = sha256_payload(
        {
            "request_fingerprint": request_fingerprint,
            "execution_plan_fingerprint": execution_plan_fingerprint,
            "base_combined_candidate_dataset_fingerprint": contract["base_combined_candidate"]["candidate_dataset_fingerprint"],
            "base_combined_scientific_dataset_fingerprint": contract["base_combined_candidate"]["scientific_dataset_fingerprint"],
            "delta_parquet_sha256": delta_parquet_sha,
            "second_delta_row_count": len(physical_rows),
            "partition_coverage_fingerprint": partition_coverage_fingerprint,
            "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        }
    )
    candidate_output_manifest = {
        "candidate_dataset_id": "market_state_candidate_dataset_incremental_gen2_v0_1_" + candidate_dataset_fingerprint[:16],
        "candidate_dataset_status": "candidate_pending_validation",
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "profile_id": profile_id,
        "coverage": {
            "requested_contexts": len(partition_rows),
            "reusable_validated_contexts": disposition_counts["reusable_validated"],
            "second_delta_materialized_contexts": len(physical_rows),
            "combined_candidate_contexts_represented": disposition_counts["reusable_validated"] + len(physical_rows),
            "unavailable_contexts": disposition_counts["unavailable"],
        },
        "base_combined_candidate_reused": {
            "dataset_id": contract["base_combined_candidate"]["dataset_id"],
            "candidate_dataset_fingerprint": contract["base_combined_candidate"]["candidate_dataset_fingerprint"],
            "scientific_dataset_fingerprint": contract["base_combined_candidate"]["scientific_dataset_fingerprint"],
            "candidate_output_manifest": str(BASELINE_RUN_DIR / "candidate_output_manifest.json"),
        },
        "new_second_delta_files": [
            {
                "path": str(delta_parquet_path),
                "sha256": delta_parquet_sha,
                "bytes": delta_parquet_path.stat().st_size,
                "rows": len(physical_rows),
            }
        ],
        "schema_contract": str(PROFILE_SCHEMA_PATH),
        "schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
    }
    write_json(run_dir / "candidate_output_manifest.json", candidate_output_manifest)

    lineage_manifest = {
        "run_id": run_id,
        "base_combined_candidate_reused": candidate_output_manifest["base_combined_candidate_reused"],
        "reused_contexts": reused_contexts,
        "source_resolution": source_resolution,
        "second_delta_source_candidate_records_used": [
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "instrument_id": row["instrument_id"],
                "ticker": row["ticker"],
                "session_date": normalize(row["session_date"]),
                "decision_timestamp_utc": normalize(row["decision_timestamp_utc"]),
                "context_input_fingerprint": row["context_input_fingerprint"],
            }
            for row in physical_rows
        ],
        "unavailable_contexts": unavailable_contexts,
    }
    write_json(run_dir / "lineage_manifest.json", lineage_manifest)

    observed_rows = pq.read_table(delta_parquet_path).to_pylist()
    schema_match = [field.name for field in pq.read_schema(delta_parquet_path)] == column_order
    primary_key_fields = ["instrument_id", "decision_timestamp_utc", "state_profile_id", "state_schema_version"]
    primary_keys = [tuple(normalize(row[field]) for field in primary_key_fields) for row in observed_rows]
    duplicate_primary_keys = sum(count - 1 for count in Counter(primary_keys).values() if count > 1)
    baseline_keys = {
        (part["instrument_id"], part["session_date"], part["decision_timestamp_utc"])
        for part in baseline_partition_coverage["partitions"]
    }
    delta_keys = {
        (row["instrument_id"], normalize(row["session_date"]), normalize(row["decision_timestamp_utc"]))
        for row in observed_rows
    }
    second_delta_overlaps_base_combined_candidate = len(delta_keys.intersection(baseline_keys))
    null_failures = sum(1 for row in observed_rows for name in column_order if row.get(name) is None and not column_defs[name]["nullable"])

    fingerprint_failures = 0
    fingerprint_rows: list[dict[str, Any]] = []
    fp_fields = source_scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
    id_fields = source_scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
    for row in observed_rows:
        recalculated_state = bounded.row_fingerprint(row, fp_fields)
        recalculated_id = bounded.row_fingerprint({**row, "state_output_fingerprint": recalculated_state}, id_fields)
        state_match = recalculated_state == row["state_output_fingerprint"]
        id_match = recalculated_id == row["materialized_state_candidate_id"]
        if not state_match or not id_match:
            fingerprint_failures += 1
        fingerprint_rows.append(
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
                "recalculated_state_output_fingerprint": recalculated_state,
                "state_output_fingerprint_match": state_match,
                "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                "recalculated_materialized_state_candidate_id": recalculated_id,
                "materialized_state_candidate_id_match": id_match,
            }
        )
    write_csv(
        run_dir / "fingerprint_validation_report.csv",
        fingerprint_rows,
        [
            "source_candidate_record_id",
            "state_output_fingerprint",
            "recalculated_state_output_fingerprint",
            "state_output_fingerprint_match",
            "materialized_state_candidate_id",
            "recalculated_materialized_state_candidate_id",
            "materialized_state_candidate_id_match",
        ],
    )

    temporal_failures = 0
    temporal_rows: list[dict[str, Any]] = []
    for row in observed_rows:
        expected_anchor = scope["decision_timestamps_utc"][normalize(row["session_date"])]
        ok = normalize(row["decision_timestamp_utc"]) == expected_anchor
        temporal_failures += 0 if ok else 1
        temporal_rows.append(
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "session_date": normalize(row["session_date"]),
                "decision_timestamp_utc": normalize(row["decision_timestamp_utc"]),
                "expected_session_open_utc": expected_anchor,
                "temporal_legality_pass": ok,
            }
        )
    write_json(run_dir / "market_state_temporal_legality_report.json", {"failures": temporal_failures, "rows": temporal_rows})

    lineage_failures = 0
    for row in observed_rows:
        for field in ["source_lineage_json", "policy_versions_json", "formula_versions_json", "restriction_codes_json"]:
            try:
                json.loads(row[field])
            except Exception:
                lineage_failures += 1
    write_json(
        run_dir / "market_state_lineage_validation_report.json",
        {"lineage_json_parse_failures": lineage_failures, "lineage_manifest": str(run_dir / "lineage_manifest.json")},
    )

    partition_accounting_pass = len(partition_rows) == sum(
        disposition_counts[state]
        for state in ["reusable_validated", "to_build", "to_rebuild", "unavailable", "quarantined", "blocked"]
    )
    materializer_second_delta_only_pass = (
        len(observed_rows) == disposition_counts["to_build"]
        and disposition_counts["reusable_validated"] == contract["success_criteria"]["base_combined_reusable_contexts_selected"]
        and second_delta_overlaps_base_combined_candidate == 0
    )
    partition_validation = {
        "requested_logical_partitions": len(partition_rows),
        "reusable_validated": disposition_counts["reusable_validated"],
        "to_build": disposition_counts["to_build"],
        "to_rebuild": disposition_counts["to_rebuild"],
        "unavailable": disposition_counts["unavailable"],
        "quarantined": disposition_counts["quarantined"],
        "blocked": disposition_counts["blocked"],
        "second_delta_materialized_partitions": len(observed_rows),
        "combined_candidate_contexts_represented": disposition_counts["reusable_validated"] + len(observed_rows),
        "partition_accounting_pass": partition_accounting_pass,
        "disposition_expectation_pass": disposition_expectation_pass,
        "materializer_second_delta_only_pass": materializer_second_delta_only_pass,
        "second_delta_overlaps_base_combined_candidate": second_delta_overlaps_base_combined_candidate,
    }
    write_json(run_dir / "market_state_partition_validation_report.json", partition_validation)

    validation_hard_failures = sum(
        [
            0 if schema_match else 1,
            duplicate_primary_keys,
            second_delta_overlaps_base_combined_candidate,
            null_failures,
            fingerprint_failures,
            temporal_failures,
            lineage_failures,
            0 if partition_accounting_pass else 1,
            0 if disposition_expectation_pass else 1,
            0 if materializer_second_delta_only_pass else 1,
        ]
    )
    validation_status = "PASS_WITH_RESTRICTIONS" if validation_hard_failures == 0 else "FAIL"
    validation_report = {
        "validation_status": validation_status,
        "schema_match": schema_match,
        "second_delta_row_count": len(observed_rows),
        "combined_candidate_contexts_represented": disposition_counts["reusable_validated"] + len(observed_rows),
        "duplicate_primary_keys": duplicate_primary_keys,
        "second_delta_overlaps_base_combined_candidate": second_delta_overlaps_base_combined_candidate,
        "non_nullable_null_failures": null_failures,
        "fingerprint_failures": fingerprint_failures,
        "temporal_failures": temporal_failures,
        "lineage_failures": lineage_failures,
        "partition_accounting_pass": partition_accounting_pass,
        "disposition_expectation_pass": disposition_expectation_pass,
        "materializer_second_delta_only_pass": materializer_second_delta_only_pass,
        "hard_validation_failures": validation_hard_failures,
        "eligible_for_candidate_registry": validation_hard_failures == 0,
        "reuse_eligibility": "pending_second_generation_incremental_review",
        "promotion_review_eligibility": "not_eligible_pending_lineage_chain_validation_and_scale_validation",
    }
    validation_result_fingerprint = sha256_payload(validation_report)
    validation_report["validation_result_fingerprint"] = validation_result_fingerprint
    write_json(run_dir / "market_state_validation_report.json", validation_report)
    write_json(
        run_dir / "validation_evidence_manifest.json",
        {
            "validation_result_fingerprint": validation_result_fingerprint,
            "reports": {
                "market_state_validation_report": str(run_dir / "market_state_validation_report.json"),
                "market_state_partition_validation_report": str(run_dir / "market_state_partition_validation_report.json"),
                "market_state_temporal_legality_report": str(run_dir / "market_state_temporal_legality_report.json"),
                "market_state_lineage_validation_report": str(run_dir / "market_state_lineage_validation_report.json"),
                "fingerprint_validation_report": str(run_dir / "fingerprint_validation_report.csv"),
            },
        },
    )

    second_generation_incremental_extension_report = {
        "run_id": run_id,
        "status": "PASS" if validation_hard_failures == 0 else "FAIL",
        "base_combined_candidate_reused": contract["base_combined_candidate"]["dataset_id"],
        "base_combined_registry_entry_mutated": False,
        "request_c_fingerprint": request_fingerprint,
        "request_c_differs_from_base_combined_request": request_fingerprint != baseline_registry["request_fingerprint"],
        "execution_plan_c_fingerprint": execution_plan_fingerprint,
        "execution_plan_c_differs_from_base_combined_plan": execution_plan_fingerprint
        != baseline_registry["execution_plan_fingerprint"],
        "reusable_validated_contexts": disposition_counts["reusable_validated"],
        "known_unavailable_contexts": disposition_counts["unavailable"],
        "second_delta_contexts_built": len(observed_rows),
        "materializer_build_scope_second_delta_only": materializer_second_delta_only_pass,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
    }
    write_json(run_dir / "market_state_second_generation_incremental_extension_report.json", second_generation_incremental_extension_report)

    registry_entry = {
        "dataset_id": candidate_output_manifest["candidate_dataset_id"],
        "dataset_kind": "market_state_candidate_dataset_incremental_evolution_second_generation",
        "registry_status": "validated_candidate" if validation_hard_failures == 0 else "failed",
        "validation_status": validation_status.lower(),
        "reuse_eligibility": "pending_second_generation_incremental_review",
        "promotion_review_eligibility": "not_eligible_pending_lineage_chain_validation_and_scale_validation",
        "downstream_eligibility": False,
        "request_fingerprint": request_fingerprint,
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "profile_id": profile_id,
        "coverage": candidate_output_manifest["coverage"],
        "base_combined_candidate_ref": candidate_output_manifest["base_combined_candidate_reused"],
        "file_manifest_ref": "candidate_output_manifest.json",
        "lineage_manifest_ref": "lineage_manifest.json",
        "validation_report_ref": "market_state_validation_report.json",
    }
    registry_entry["registry_entry_fingerprint"] = sha256_payload(registry_entry)
    write_json(run_dir / "candidate_registry_entry.json", registry_entry)

    final_status = (
        "CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED"
        if validation_hard_failures == 0 and disposition_counts["unavailable"]
        else "CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_CANDIDATE_REGISTERED"
        if validation_hard_failures == 0
        else "CLOSED_BLOCKED_SECOND_GENERATION_INCREMENTAL_EXTENSION_VALIDATION_FAILED"
    )
    final_manifest = {
        **pre_manifest,
        "status": final_status,
        "completed_at_utc": utc_now(),
        "source_candidate_records_read": source_records_read,
        "source_market_data_rows_read": 0,
        "requested_contexts": len(partition_rows),
        "reusable_validated_contexts": disposition_counts["reusable_validated"],
        "second_delta_materialized_candidate_rows": len(observed_rows),
        "combined_candidate_contexts_represented": disposition_counts["reusable_validated"] + len(observed_rows),
        "unavailable_contexts": disposition_counts["unavailable"],
        "candidate_parquet_files_written": 1,
        "candidate_registry_entries_written": 1 if validation_hard_failures == 0 else 0,
        "base_combined_registry_entry_mutations": 0,
        "materializer_build_scope_second_delta_only": materializer_second_delta_only_pass,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "request_fingerprint": request_fingerprint,
        "resolved_profile_fingerprint": resolved_profile_fingerprint,
        "resolved_universe_fingerprint": resolved_universe_fingerprint,
        "resolved_source_set_fingerprint": resolved_source_set_fingerprint,
        "partition_coverage_resolution_fingerprint": partition_coverage_fingerprint,
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "artifacts": {
            "request_record": str(run_dir / "request_record.json"),
            "profile_resolution_report": str(run_dir / "profile_resolution_report.json"),
            "universe_resolution_report": str(run_dir / "universe_resolution_report.json"),
            "source_resolution_report": str(run_dir / "source_resolution_report.json"),
            "partition_coverage_resolution_report": str(run_dir / "partition_coverage_resolution_report.json"),
            "execution_plan": str(run_dir / "execution_plan.json"),
            "pre_run_manifest": str(run_dir / "pre_run_manifest.json"),
            "candidate_output_manifest": str(run_dir / "candidate_output_manifest.json"),
            "lineage_manifest": str(run_dir / "lineage_manifest.json"),
            "market_state_validation_report": str(run_dir / "market_state_validation_report.json"),
            "second_generation_incremental_extension_report": str(run_dir / "market_state_second_generation_incremental_extension_report.json"),
            "candidate_registry_entry": str(run_dir / "candidate_registry_entry.json"),
            "second_delta_candidate_parquet": str(delta_parquet_path),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": final_status, "stage": "closed"})

    readout = f"""# Market State On-Demand Second-Generation Incremental Extension Readout v0.1

Status: `{final_status}`
Date: `2026-07-27`

```text
run_id = {run_id}
request_id = {request['request_id']}
execution_plan_id = {execution_plan['execution_plan_id']}
requested_contexts = {len(partition_rows)}
reusable_validated_contexts = {disposition_counts['reusable_validated']}
known_unavailable_contexts = {disposition_counts['unavailable']}
second_delta_materialized_candidate_rows = {len(observed_rows)}
combined_candidate_contexts_represented = {disposition_counts['reusable_validated'] + len(observed_rows)}
candidate_parquet_files_written = 1
candidate_registry_entries_written = {1 if validation_hard_failures == 0 else 0}
base_combined_registry_entry_mutations = 0
source_candidate_records_read = {source_records_read}
source_market_data_rows_read = 0
hard_validation_failures = {validation_hard_failures}
reuse_eligibility = pending_second_generation_incremental_review
official_dataset = false
production = false
downstream = false
next_recommended_gate = market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1
```

The second-generation incremental extension reused the validated combined
candidate by reference and materialized only the authorized second delta
session. It did not rebuild the base combined candidate and did not mutate its
registry entry.
"""
    (run_dir / "run_readout.md").write_text(
        readout, encoding="utf-8"
    )

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False, default=str))
    return 0 if validation_hard_failures == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IncrementalExecutionError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
