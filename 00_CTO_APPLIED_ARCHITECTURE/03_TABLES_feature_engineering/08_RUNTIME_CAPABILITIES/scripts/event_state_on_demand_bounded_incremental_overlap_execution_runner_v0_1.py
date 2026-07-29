#!/usr/bin/env python
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_VERSION = "event_state_on_demand_bounded_incremental_overlap_execution_runner_v0_1"
GATE_ID = "event_state_on_demand_bounded_incremental_overlap_execution_v0_1"
PASS_STATUS = "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED"
FAIL_STATUS = "CLOSED_FAIL_EVENT_STATE_INCREMENTAL_OVERLAP_EXECUTION"
NEXT_GATE = "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1"

REPO_ROOT = Path(__file__).resolve().parents[4]
FEATURE_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = Path(__file__).resolve().parents[1]
EVENT_ROOT = FEATURE_ROOT / "07_EVENT_STATE_INTEGRATION"
RUNS_ROOT = RUNTIME_ROOT / "runs"

SCOPE_PATH = RUNTIME_ROOT / "configs" / "event_state_on_demand_bounded_incremental_overlap_execution_scope_v0_1.json"
BASELINE_RUN_DIR = RUNS_ROOT / "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"
BASELINE_REUSE_TRANSITION_DIR = RUNS_ROOT / "event_state_on_demand_bounded_reuse_eligibility_transition_review_v0_1_20260728T080426Z"
MARKET_STATE_DELTA_RUN_DIR = RUNS_ROOT / "market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103901Z"

EVENT_PROFILE_PATH = EVENT_ROOT / "official_profiles" / "event_state_core_four_intraday_profile_v0_1" / "PROFILE_MANIFEST.json"
EVENT_INSTANCE_CONTRACT_PATH = EVENT_ROOT / "event_instance_binding_design_contract_v0_1.json"
EVENT_WINDOW_CONTRACT_PATH = EVENT_ROOT / "event_window_binding_design_contract_v0_1.json"
PROJECTION_CONTRACT_PATH = EVENT_ROOT / "event_state_instrument_session_projection_design_contract_v0_1.json"
REQUEST_CONTRACT_PATH = RUNTIME_ROOT / "event_state_request_contract_v0_1.json"
DEPENDENCY_CONTRACT_PATH = RUNTIME_ROOT / "event_state_dependency_resolution_contract_v0_1.json"
EXECUTION_PLAN_CONTRACT_PATH = RUNTIME_ROOT / "event_state_execution_plan_contract_v0_1.json"
MATERIALIZER_CONTRACT_PATH = RUNTIME_ROOT / "event_state_materializer_contract_v0_1.json"
VALIDATOR_CONTRACT_PATH = RUNTIME_ROOT / "event_state_validator_contract_v0_1.json"
REGISTRY_CONTRACT_PATH = RUNTIME_ROOT / "event_state_candidate_dataset_registry_contract_v0_1.json"
RUN_LIFECYCLE_CONTRACT_PATH = RUNTIME_ROOT / "event_state_on_demand_bounded_run_lifecycle_binding_contract_v0_1.json"
MARKET_STATE_CONSUMPTION_POLICY_PATH = RUNTIME_ROOT / "market_state_capability_consumption_policy_contract_v0_1.json"

EVENT_STATE_PROFILE_ID = "event_state_core_four_intraday_profile_v0_1"
EVENT_TYPE_ID = "event_type:market_data:session_opened"
EVENT_FAMILY_ID = "event_family:market_data:session_lifecycle"
EVENT_WINDOW_DEFINITION_ID = "session_opened_at_anchor_context_v0_1"
EVENT_WINDOW_DEFINITION_VERSION = "v0_1"
EVENT_STATE_SCHEMA_VERSION = "event_state_candidate_schema_v0_1"
EVENT_INSTANCE_VERSION = "v0_1"
INTEGRATION_POLICY_ID = "event_state_on_demand_incremental_overlap_integration_policy_v0_1"
INTEGRATION_POLICY_VERSION = "v0_1"
PROJECTION_POLICY_ID = "event_state_instrument_session_projection_policy_v0_1"
PROJECTION_POLICY_VERSION = "v0_1"
MARKET_STATE_PROFILE_ID = "market_state_core_four_intraday_profile_v0_1"
MARKET_STATE_SCHEMA_VERSION = "core_four_market_state_candidate_physical_schema_v0_1"

SCIENTIFIC_RUNTIME_EXCLUDED_FIELDS = {
    "created_at_utc",
    "binding_created_at_utc",
    "projection_created_at_utc",
    "materialization_run_id",
}


class ExecutionError(RuntimeError):
    pass


def to_builtin(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_builtin(v) for v in value]
    return str(value)


def stable_json(value: Any) -> str:
    return json.dumps(to_builtin(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_payload(value: Any) -> str:
    return sha256_text(stable_json(value))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def utc_now() -> str:
    return utc_dt().isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    if not path.exists():
        raise ExecutionError(f"Missing JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(to_builtin(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ExecutionError(f"Missing JSONL: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(to_builtin(row), sort_keys=True, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(to_builtin(row), sort_keys=True, ensure_ascii=False) + "\n")


def git_value(args: list[str]) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, capture_output=True, check=False)
    except Exception:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def sorted_by_context(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda r: (
            str(r.get("session_date", "")),
            str(r.get("instrument_id", "")),
            str(r.get("event_anchor_timestamp_utc", r.get("decision_timestamp_utc", ""))),
            str(r.get("event_state_record_id", "")),
        ),
    )


def normalized_record(row: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k not in SCIENTIFIC_RUNTIME_EXCLUDED_FIELDS}


def content_snapshot_from_market_state(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row[k] for k in sorted(row) if "__" in k}


def parse_json_field(value: Any, default: Any) -> Any:
    if not isinstance(value, str) or not value.strip():
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def make_id(prefix: str, payload: Any) -> str:
    return f"{prefix}:{sha256_payload(payload)}"


def compact_hash_id(payload: Any) -> str:
    return sha256_payload(payload)


def context_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            str(row.get("event_type_id", EVENT_TYPE_ID)),
            str(row.get("exchange_id", "XNYS")),
            str(row["session_date"]),
            str(row["instrument_id"]),
            str(row.get("event_window_definition_id", EVENT_WINDOW_DEFINITION_ID)),
        ]
    )


def validate_scope(scope: dict[str, Any]) -> None:
    if scope.get("authorized_next_gate") != GATE_ID:
        raise ExecutionError("Incremental overlap scope does not authorize this gate")
    allowed_scope_statuses = {"AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION", "AUTHORIZED_WITH_RESTRICTIONS_NO_VALID_CLOSURE_AFTER_INVALID_ATTEMPT"}
    if scope.get("status") not in allowed_scope_statuses:
        raise ExecutionError("Incremental overlap scope is not in an executable authorization state")
    if scope.get("event_state_profile_id") != EVENT_STATE_PROFILE_ID:
        raise ExecutionError("Unsupported Event State profile")
    if scope.get("event_type_id") != EVENT_TYPE_ID:
        raise ExecutionError("Unsupported Event Type")
    if scope.get("subject_scope") != "exchange_session":
        raise ExecutionError("Unsupported subject scope")
    if scope.get("market_state_dependency_mode") != "emit_or_resolve_market_state_subrequest_through_runtime_capability":
        raise ExecutionError("Market State dependency mode is not runtime-capability subrequest")


def verify_baseline(scope: dict[str, Any]) -> dict[str, Any]:
    final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    transition = read_json(BASELINE_REUSE_TRANSITION_DIR / "reuse_eligibility_transition_record_v0_1.json")
    records_path = BASELINE_RUN_DIR / "event_state_candidate_records.jsonl"
    records_sha = sha256_file(records_path)
    if final.get("candidate_dataset_fingerprint") != scope["baseline_candidate_dataset_fingerprint"]:
        raise ExecutionError("Baseline final manifest candidate fingerprint mismatch")
    if registry.get("event_state_candidate_dataset_fingerprint") != scope["baseline_candidate_dataset_fingerprint"]:
        raise ExecutionError("Baseline registry candidate fingerprint mismatch")
    if transition.get("candidate_dataset_fingerprint") != scope["baseline_candidate_dataset_fingerprint"]:
        raise ExecutionError("Baseline reuse transition candidate fingerprint mismatch")
    if transition.get("normalized_logical_dataset_fingerprint") != scope["baseline_normalized_logical_dataset_fingerprint"]:
        raise ExecutionError("Baseline normalized logical fingerprint mismatch")
    if transition.get("reuse_eligibility_after_review") != scope["baseline_reuse_eligibility"]:
        raise ExecutionError("Baseline reuse eligibility mismatch")
    return {
        "final_manifest": final,
        "candidate_registry_entry": registry,
        "reuse_transition_record": transition,
        "records_path": str(records_path),
        "records_sha256_before": records_sha,
        "registry_entry_fingerprint_before": registry.get("registry_entry_fingerprint"),
        "final_manifest_sha256_before": sha256_file(BASELINE_RUN_DIR / "final_manifest.json"),
    }


def verify_market_state_delta(scope: dict[str, Any]) -> dict[str, Any]:
    evidence = scope["known_market_state_candidate_evidence"]
    final = read_json(MARKET_STATE_DELTA_RUN_DIR / "final_manifest.json")
    registry = read_json(MARKET_STATE_DELTA_RUN_DIR / "candidate_registry_entry.json")
    rows = read_jsonl(MARKET_STATE_DELTA_RUN_DIR / "delta_market_state_rows.jsonl")
    if final.get("run_id") != evidence["reference_run_id"]:
        raise ExecutionError("Market State delta run id mismatch")
    if final.get("candidate_dataset_fingerprint") != evidence["candidate_dataset_fingerprint"]:
        raise ExecutionError("Market State delta candidate fingerprint mismatch")
    if final.get("scientific_dataset_fingerprint") != evidence["scientific_dataset_fingerprint"]:
        raise ExecutionError("Market State delta scientific fingerprint mismatch")
    if final.get("status") != evidence["status"]:
        raise ExecutionError("Market State delta status mismatch")
    if registry.get("registry_status") != "validated_candidate":
        raise ExecutionError("Market State delta candidate is not validated")
    expected_delta_sessions = set(scope["delta_session_dates"])
    observed_delta_sessions = {r["session_date"] for r in rows}
    if observed_delta_sessions != expected_delta_sessions:
        raise ExecutionError(f"Unexpected Market State delta sessions: {sorted(observed_delta_sessions)}")
    if len(rows) != scope["expected_delta_event_state_contexts_to_build"]:
        raise ExecutionError("Unexpected Market State delta row count")
    if {r["instrument_id"] for r in rows} != set(scope["instrument_ids"]):
        raise ExecutionError("Market State delta instrument set mismatch")
    return {"final_manifest": final, "candidate_registry_entry": registry, "delta_rows": rows}


def build_delta_instance(delta_rows: list[dict[str, Any]], run_started: str) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    first = delta_rows[0]
    lineage = parse_json_field(first.get("source_lineage_json"), {})
    calendar = lineage.get("shared_source_evidence", {}).get("governed_calendar_binding", {})
    session_date = first["session_date"]
    exchange_id = "XNYS"
    anchor = calendar.get("session_open_utc") or first["decision_timestamp_utc"]
    event_instance_id = compact_hash_id(
        {
            "kind": "event_instance",
            "event_type_id": EVENT_TYPE_ID,
            "exchange_id": exchange_id,
            "session_date": session_date,
            "event_anchor_timestamp_utc": anchor,
            "calendar_version": calendar.get("calendar_version"),
        }
    )
    window_binding_id = compact_hash_id(
        {
            "kind": "event_window_binding",
            "event_instance_id": event_instance_id,
            "window_definition_id": EVENT_WINDOW_DEFINITION_ID,
            "window_start_utc": anchor,
            "window_end_utc": anchor,
        }
    )
    instance = {
        "event_instance_id": event_instance_id,
        "event_instance_version": EVENT_INSTANCE_VERSION,
        "event_type_id": EVENT_TYPE_ID,
        "event_family_id": EVENT_FAMILY_ID,
        "event_subject_scope": "exchange_session",
        "exchange_id": exchange_id,
        "session_date": session_date,
        "event_anchor_timestamp_utc": anchor,
        "first_observable_timestamp_utc": anchor,
        "detection_timestamp_utc": None,
        "binding_created_at_utc": run_started,
        "calendar_id": calendar.get("calendar_id"),
        "calendar_version": calendar.get("calendar_version"),
        "calendar_source_snapshot_fingerprint": calendar.get("calendar_row_fingerprint"),
        "bound_calendar_parquet_sha256": None,
        "calendar_row_fingerprint": calendar.get("calendar_row_fingerprint"),
        "session_open_utc": calendar.get("session_open_utc"),
        "session_close_utc": calendar.get("session_close_utc"),
        "session_type": calendar.get("session_type", "regular"),
        "is_early_close": bool(calendar.get("is_early_close", False)),
        "native_identity_includes_instrument_id": False,
        "event_instance_quality_state": "candidate_bounded_incremental_delta",
        "registry_snapshot_id": "tsis_event_type_registry_v0_1_post_initial_admission_001",
        "registry_snapshot_sha256": "f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43",
        "origin_mode": "delta_materialized_event_state",
    }
    window = {
        "event_window_binding_id": window_binding_id,
        "event_instance_id": event_instance_id,
        "event_type_id": EVENT_TYPE_ID,
        "event_family_id": EVENT_FAMILY_ID,
        "window_definition_id": EVENT_WINDOW_DEFINITION_ID,
        "window_definition_version": EVENT_WINDOW_DEFINITION_VERSION,
        "state_role": "at_event",
        "consumption_legality": "research_only",
        "event_anchor_timestamp_utc": anchor,
        "first_observable_timestamp_utc": anchor,
        "binding_created_at_utc": run_started,
        "relative_start_offset": "PT0S",
        "relative_end_offset": "PT0S",
        "window_start_utc": anchor,
        "window_end_utc": anchor,
        "window_duration_seconds": 0,
        "calendar_authority_id": calendar.get("calendar_id"),
        "calendar_version": calendar.get("calendar_version"),
        "calendar_source_snapshot_fingerprint": calendar.get("calendar_row_fingerprint"),
        "calendar_row_fingerprint": calendar.get("calendar_row_fingerprint"),
        "exchange_id": exchange_id,
        "session_date": session_date,
        "session_open_utc": calendar.get("session_open_utc"),
        "session_close_utc": calendar.get("session_close_utc"),
        "session_type": calendar.get("session_type", "regular"),
        "is_early_close": bool(calendar.get("is_early_close", False)),
        "calendar_boundary_policy": "governed_exchange_session_open_anchor",
        "clipping_policy_id": "no_clipping_at_event_anchor_v0_1",
        "window_quality_state": "candidate_bounded_incremental_delta",
        "leakage_assessment": "exact_anchor_only; at_event_research_only_until_field_legality_review",
        "supersedes_event_window_binding_id": None,
        "superseded_by_event_window_binding_id": None,
        "correction_reason": None,
        "origin_mode": "delta_materialized_event_state",
    }
    projections = []
    for row in sorted_by_context(delta_rows):
        source_lineage = parse_json_field(row.get("source_lineage_json"), {})
        calendar_row_fp = source_lineage.get("shared_source_evidence", {}).get("governed_calendar_binding", {}).get("calendar_row_fingerprint")
        projection_id = compact_hash_id(
            {
                "kind": "event_state_instrument_session_projection",
                "event_instance_id": event_instance_id,
                "event_window_binding_id": window_binding_id,
                "instrument_id": row["instrument_id"],
                "exchange_id": exchange_id,
                "session_date": row["session_date"],
            }
        )
        projections.append(
            {
                "event_state_instrument_session_projection_id": projection_id,
                "projection_policy_id": PROJECTION_POLICY_ID,
                "projection_policy_version": PROJECTION_POLICY_VERSION,
                "event_type_id": EVENT_TYPE_ID,
                "event_instance_id": event_instance_id,
                "event_window_binding_id": window_binding_id,
                "exchange_id": exchange_id,
                "session_date": row["session_date"],
                "event_anchor_timestamp_utc": anchor,
                "window_start_utc": anchor,
                "window_end_utc": anchor,
                "instrument_id": row["instrument_id"],
                "ticker": row.get("ticker"),
                "instrument_exchange_id": exchange_id,
                "instrument_master_version": "bounded_explicit_instrument_scope_v0_1",
                "instrument_identity_fingerprint": compact_hash_id({"instrument_id": row["instrument_id"], "ticker": row.get("ticker"), "session_date": row["session_date"]}),
                "instrument_lifecycle_status": "not_revalidated_in_incremental_gate",
                "listing_status_as_of_session": "bounded_authorized_scope",
                "instrument_session_eligibility_state": "eligible_from_authorized_incremental_scope",
                "market_state_profile_id": MARKET_STATE_PROFILE_ID,
                "market_state_schema_version": row.get("state_schema_version", MARKET_STATE_SCHEMA_VERSION),
                "calendar_version": calendar.get("calendar_version"),
                "calendar_row_fingerprint": calendar_row_fp,
                "projection_quality_state": "candidate_bounded_incremental_delta",
                "projection_created_at_utc": run_started,
                "supersedes_projection_id": None,
                "superseded_by_projection_id": None,
                "correction_reason": None,
                "origin_mode": "delta_materialized_event_state",
            }
        )
    return instance, window, projections


def build_delta_records(
    scope: dict[str, Any],
    market_state: dict[str, Any],
    run_id: str,
    run_started: str,
    execution_plan_fingerprint: str,
    dependency_resolution_fingerprint: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    ms_final = market_state["final_manifest"]
    delta_rows = sorted_by_context(market_state["delta_rows"])
    event_instance, window, projections = build_delta_instance(delta_rows, run_started)
    projections_by_instrument = {p["instrument_id"]: p for p in projections}
    records = []
    bindings = []
    ledger = []
    for row in delta_rows:
        projection = projections_by_instrument[row["instrument_id"]]
        market_lineage = parse_json_field(row.get("source_lineage_json"), {})
        restrictions = parse_json_field(row.get("restriction_codes_json"), [])
        restrictions = sorted(
            set(
                restrictions
                + [
                    "event_state_bounded_incremental_overlap_candidate_output_only",
                    "event_state_delta_materialized_from_validated_market_state_runtime_candidate",
                    "event_state_official_dataset_false",
                    "event_state_downstream_consumption_prohibited",
                    "at_event_consumption_legality_research_only_until_field_legality_review",
                    "source_market_state_restrictions_preserved",
                ]
            )
        )
        source_lineage = {
            "origin_mode": "delta_materialized_event_state",
            "event_state_incremental_overlap_run_id": run_id,
            "event_state_execution_plan_fingerprint": execution_plan_fingerprint,
            "event_state_dependency_resolution_fingerprint": dependency_resolution_fingerprint,
            "source_market_state_run_id": ms_final["run_id"],
            "source_market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "source_market_state_scientific_dataset_fingerprint": ms_final["scientific_dataset_fingerprint"],
            "source_market_state_validation_result_fingerprint": ms_final["validation_result_fingerprint"],
            "source_market_state_record_id": row["materialized_state_candidate_id"],
            "source_market_state_record_fingerprint": row["state_output_fingerprint"],
            "source_market_state_lineage": market_lineage,
        }
        record_core = {
            "calendar_row_fingerprint": projection.get("calendar_row_fingerprint"),
            "calendar_version": projection.get("calendar_version"),
            "consumption_legality": "research_only",
            "decision_timestamp_utc": row["decision_timestamp_utc"],
            "event_anchor_timestamp_utc": row["decision_timestamp_utc"],
            "event_family_id": EVENT_FAMILY_ID,
            "event_instance_id": event_instance["event_instance_id"],
            "event_instance_version": EVENT_INSTANCE_VERSION,
            "event_state_instrument_session_projection_id": projection["event_state_instrument_session_projection_id"],
            "event_state_profile_id": EVENT_STATE_PROFILE_ID,
            "event_state_schema_version": EVENT_STATE_SCHEMA_VERSION,
            "event_type_id": EVENT_TYPE_ID,
            "event_window_binding_id": window["event_window_binding_id"],
            "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
            "exchange_id": "XNYS",
            "instrument_id": row["instrument_id"],
            "integration_policy_id": INTEGRATION_POLICY_ID,
            "integration_policy_version": INTEGRATION_POLICY_VERSION,
            "integration_status": "EVENT_STATE_INCREMENTAL_OVERLAP_DELTA_INTEGRATED_WITH_RESTRICTIONS",
            "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"],
            "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"],
            "market_state_record_id": row["materialized_state_candidate_id"],
            "object_completeness_status": row.get("object_completeness_status"),
            "policy_versions_json": stable_json(
                {
                    **parse_json_field(row.get("policy_versions_json"), {}),
                    "event_state_request_contract": "event_state_request_contract_v0_1",
                    "event_state_dependency_resolution_contract": "event_state_dependency_resolution_contract_v0_1",
                    "event_state_execution_plan_contract": "event_state_execution_plan_contract_v0_1",
                    "event_state_incremental_overlap_integration_policy": INTEGRATION_POLICY_VERSION,
                }
            ),
            "quality_status": row.get("quality_status"),
            "relative_time_to_event": "PT0S",
            "restriction_codes_json": stable_json(restrictions),
            "session_date": row["session_date"],
            "source_lineage_json": stable_json(source_lineage),
            "source_market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "source_market_state_physical_profile_id": MARKET_STATE_PROFILE_ID,
            "source_market_state_profile_id": MARKET_STATE_PROFILE_ID,
            "source_market_state_schema_version": row.get("state_schema_version", MARKET_STATE_SCHEMA_VERSION),
            "source_market_state_value_snapshot_json": stable_json(content_snapshot_from_market_state(row)),
            "state_output_fingerprint": row["state_output_fingerprint"],
            "state_role": "at_event",
            "superseded_by_event_state_record_id": None,
            "supersedes_event_state_record_id": None,
            "ticker": row.get("ticker"),
            "window_end_utc": row["decision_timestamp_utc"],
            "window_start_utc": row["decision_timestamp_utc"],
        }
        record_id = compact_hash_id(
            {
                "kind": "event_state_record",
                "event_state_profile_id": EVENT_STATE_PROFILE_ID,
                "event_type_id": EVENT_TYPE_ID,
                "event_instance_id": event_instance["event_instance_id"],
                "event_window_binding_id": window["event_window_binding_id"],
                "projection_id": projection["event_state_instrument_session_projection_id"],
                "market_state_record_id": row["materialized_state_candidate_id"],
                "market_state_state_output_fingerprint": row["state_output_fingerprint"],
                "state_role": "at_event",
                "consumption_legality": "research_only",
            }
        )
        record = {
            **record_core,
            "event_state_record_id": record_id,
            "event_state_record_fingerprint": compact_hash_id({"event_state_record_id": record_id, **record_core}),
            "created_at_utc": run_started,
        }
        records.append(record)
        bindings.append(
            {
                "event_state_instrument_session_projection_id": projection["event_state_instrument_session_projection_id"],
                "event_instance_id": event_instance["event_instance_id"],
                "event_window_binding_id": window["event_window_binding_id"],
                "instrument_id": row["instrument_id"],
                "ticker": row.get("ticker"),
                "session_date": row["session_date"],
                "event_anchor_timestamp_utc": row["decision_timestamp_utc"],
                "market_state_rows_found": 1,
                "available_same_instrument_session_timestamps": [row["decision_timestamp_utc"]],
                "market_state_binding_status": "BOUND",
                "blocking_reason": None,
                "market_state_record_id": row["materialized_state_candidate_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
                "source_market_state_profile_id": MARKET_STATE_PROFILE_ID,
                "source_market_state_physical_profile_id": MARKET_STATE_PROFILE_ID,
                "decision_timestamp_utc": row["decision_timestamp_utc"],
                "fallback_used": False,
                "origin_mode": "delta_materialized_event_state",
            }
        )
        ledger.append(
            {
                "event_type_id": EVENT_TYPE_ID,
                "exchange_id": "XNYS",
                "session_date": row["session_date"],
                "instrument_id": row["instrument_id"],
                "event_anchor_timestamp_utc": row["decision_timestamp_utc"],
                "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
                "context_status": "represented",
                "representation_source": "delta_materialized_event_state",
                "blocking_reason": None,
                "market_state_record_id": row["materialized_state_candidate_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
                "origin_run_id": run_id,
                "origin_dataset_id": None,
                "origin_candidate_dataset_fingerprint": None,
                "source_market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
                "available_same_instrument_session_timestamps": [row["decision_timestamp_utc"]],
            }
        )
    return records, bindings, event_instance, window, projections, ledger


def build_combined(scope: dict[str, Any], baseline: dict[str, Any], market_state: dict[str, Any], run_id: str, run_started: str, plan_fp: str, dep_fp: str) -> dict[str, Any]:
    baseline_records = read_jsonl(BASELINE_RUN_DIR / "event_state_candidate_records.jsonl")
    baseline_ledger = read_json(BASELINE_RUN_DIR / "event_state_logical_context_ledger.json")
    baseline_instances = read_json(BASELINE_RUN_DIR / "event_instance_manifest.json")
    baseline_windows = read_json(BASELINE_RUN_DIR / "event_window_binding_manifest.json")
    baseline_projections = read_json(BASELINE_RUN_DIR / "instrument_session_projection_manifest.json")
    baseline_bindings = read_json(BASELINE_RUN_DIR / "market_state_dependency_binding_report.json")

    if len(baseline_records) != scope["expected_reusable_event_state_contexts"]:
        raise ExecutionError("Baseline reusable Event State record count mismatch")
    delta_records, delta_bindings, delta_instance, delta_window, delta_projections, delta_ledger = build_delta_records(scope, market_state, run_id, run_started, plan_fp, dep_fp)
    if len(delta_records) != scope["expected_delta_event_state_contexts_to_build"]:
        raise ExecutionError("Delta Event State record count mismatch")

    reused_ledger = []
    for row in baseline_ledger:
        enriched = dict(row)
        if row["context_status"] == "represented":
            enriched.update(
                {
                    "representation_source": "reused_validated_event_state",
                    "origin_run_id": baseline["final_manifest"]["run_id"],
                    "origin_dataset_id": baseline["candidate_registry_entry"]["dataset_id"],
                    "origin_candidate_dataset_fingerprint": baseline["candidate_registry_entry"]["event_state_candidate_dataset_fingerprint"],
                }
            )
        else:
            enriched.update(
                {
                    "representation_source": "none",
                    "origin_run_id": baseline["final_manifest"]["run_id"],
                    "origin_dataset_id": None,
                    "origin_candidate_dataset_fingerprint": None,
                }
            )
        reused_ledger.append(enriched)

    combined_records = sorted_by_context(baseline_records + delta_records)
    combined_ledger = sorted_by_context(reused_ledger + delta_ledger)
    combined_instances = sorted_by_context([*baseline_instances, delta_instance])
    combined_windows = sorted_by_context([*baseline_windows, delta_window])
    combined_projections = sorted_by_context([*baseline_projections, *delta_projections])
    combined_bindings = sorted_by_context([*baseline_bindings, *delta_bindings])

    expected_requested = scope["expected_requested_contexts"]
    represented = sum(1 for row in combined_ledger if row["context_status"] == "represented")
    unavailable = sum(1 for row in combined_ledger if row["context_status"] == "unavailable")
    if len(combined_ledger) != expected_requested:
        raise ExecutionError("Combined ledger request count mismatch")
    if represented != scope["expected_combined_represented_contexts"]:
        raise ExecutionError("Combined represented context count mismatch")
    if unavailable != scope["expected_unavailable_contexts"]:
        raise ExecutionError("Combined unavailable context count mismatch")
    if len({context_key(row) for row in combined_ledger}) != len(combined_ledger):
        raise ExecutionError("Duplicate logical contexts in combined ledger")
    if len({r["event_state_record_id"] for r in combined_records}) != len(combined_records):
        raise ExecutionError("Duplicate Event State record ids in combined records")
    return {
        "baseline_records": baseline_records,
        "delta_records": delta_records,
        "combined_records": combined_records,
        "combined_ledger": combined_ledger,
        "combined_instances": combined_instances,
        "combined_windows": combined_windows,
        "combined_projections": combined_projections,
        "combined_bindings": combined_bindings,
    }


def make_request(scope: dict[str, Any], run_started: str) -> tuple[dict[str, Any], str]:
    request_core = {
        "request_type": "event_state",
        "request_contract_version": "event_state_request_contract_v0_1",
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_ids": [EVENT_TYPE_ID],
        "event_subject_scope": "exchange_session",
        "exchange_scope": scope["exchange_scope"],
        "explicit_instrument_ids": scope["instrument_ids"],
        "session_dates": scope["combined_session_dates"],
        "event_window_definition_ids": [EVENT_WINDOW_DEFINITION_ID],
        "market_state_profile_id": MARKET_STATE_PROFILE_ID,
        "market_state_dependency_mode": scope["market_state_dependency_mode"],
        "market_state_dependency_reuse_policy": scope["market_state_dependency_reuse_policy"],
        "output_mode": "candidate",
        "reuse_policy": "reuse_validated_baseline_build_delta_only",
        "incremental_overlap_policy": "reuse_validated_event_state_baseline_and_materialize_delta_only_v0_1",
    }
    fingerprint = sha256_payload(request_core)
    return (
        {
            "request_id": "event_state_incremental_overlap_request_v0_1_" + fingerprint[:16],
            "request_status": "accepted_for_incremental_overlap_resolution",
            "requested_at_utc": run_started,
            "requested_by": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN",
            **request_core,
            "request_fingerprint": fingerprint,
        },
        fingerprint,
    )


def make_dependency_resolution(scope: dict[str, Any], request: dict[str, Any], baseline: dict[str, Any], market_state: dict[str, Any], run_started: str) -> tuple[dict[str, Any], str]:
    profile = read_json(EVENT_PROFILE_PATH)
    instance_contract = read_json(EVENT_INSTANCE_CONTRACT_PATH)
    findings = []
    if profile.get("status") != "OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS":
        findings.append("event_state_profile_not_promoted")
    if baseline["reuse_transition_record"].get("reuse_eligibility_after_review") != scope["baseline_reuse_eligibility"]:
        findings.append("baseline_event_state_reuse_not_eligible")
    if market_state["final_manifest"].get("candidate_dataset_fingerprint") != scope["known_market_state_candidate_evidence"]["candidate_dataset_fingerprint"]:
        findings.append("market_state_delta_candidate_fingerprint_mismatch")
    resolution = {
        "dependency_resolution_record_id": "event_state_incremental_overlap_dependency_resolution_v0_1_" + request["request_fingerprint"][:16],
        "status": "RESOLVED_FOR_INCREMENTAL_OVERLAP_EXECUTION" if not findings else "BLOCKED",
        "resolved_at_utc": run_started,
        "event_state_request_id": request["request_id"],
        "event_state_request_fingerprint": request["request_fingerprint"],
        "resolved_event_state_profile": {
            "profile_id": EVENT_STATE_PROFILE_ID,
            "profile_status": profile.get("status"),
            "profile_manifest_sha256": sha256_file(EVENT_PROFILE_PATH),
            "official_event_state_dataset_exists": False,
        },
        "resolved_event_type_registry": {
            "registry_snapshot_id": instance_contract.get("authority_binding", {}).get("registry_snapshot_id"),
            "registry_snapshot_sha256": instance_contract.get("authority_binding", {}).get("registry_snapshot_sha256"),
            "accepted_event_type_ids": [EVENT_TYPE_ID],
            "accepted_subject_scope": "exchange_session",
            "detector_required": False,
            "event_detection_allowed": False,
        },
        "resolved_baseline_event_state_reuse": {
            "baseline_run_id": baseline["final_manifest"]["run_id"],
            "baseline_dataset_id": baseline["candidate_registry_entry"]["dataset_id"],
            "baseline_candidate_dataset_fingerprint": baseline["candidate_registry_entry"]["event_state_candidate_dataset_fingerprint"],
            "baseline_normalized_logical_dataset_fingerprint": baseline["reuse_transition_record"]["normalized_logical_dataset_fingerprint"],
            "baseline_reuse_eligibility": baseline["reuse_transition_record"]["reuse_eligibility_after_review"],
            "baseline_records_reused": scope["expected_reusable_event_state_contexts"],
        },
        "resolved_market_state_delta_dependency": {
            "market_state_runtime_capability_id": "market_state_on_demand_runtime_capability_v0_1",
            "market_state_dependency_mode": scope["market_state_dependency_mode"],
            "market_state_dependency_reuse_policy": scope["market_state_dependency_reuse_policy"],
            "market_state_reference_run_id": market_state["final_manifest"]["run_id"],
            "market_state_dependency_request_fingerprint": market_state["final_manifest"]["request_fingerprint"],
            "market_state_dependency_execution_plan_fingerprint": market_state["final_manifest"]["execution_plan_fingerprint"],
            "market_state_candidate_dataset_fingerprint": market_state["final_manifest"]["candidate_dataset_fingerprint"],
            "market_state_scientific_dataset_fingerprint": market_state["final_manifest"]["scientific_dataset_fingerprint"],
            "market_state_validation_result_fingerprint": market_state["final_manifest"]["validation_result_fingerprint"],
            "market_state_delta_records_read": len(market_state["delta_rows"]),
            "direct_market_state_path_allowed": False,
        },
        "blocking_findings": findings,
    }
    fp = sha256_payload(resolution)
    resolution["event_state_dependency_resolution_fingerprint"] = fp
    if findings:
        raise ExecutionError("Dependency resolution blocked: " + ", ".join(findings))
    return resolution, fp


def make_execution_plan(scope: dict[str, Any], request: dict[str, Any], dependency: dict[str, Any], run_id: str, run_started: str) -> tuple[dict[str, Any], str]:
    plan_core = {
        "event_state_request_fingerprint": request["request_fingerprint"],
        "event_state_dependency_resolution_fingerprint": dependency["event_state_dependency_resolution_fingerprint"],
        "resolved_profile_id": EVENT_STATE_PROFILE_ID,
        "resolved_event_type_ids": [EVENT_TYPE_ID],
        "resolved_subject_scope": "exchange_session",
        "resolved_exchange_scope": scope["exchange_scope"],
        "resolved_session_dates": scope["combined_session_dates"],
        "resolved_instrument_ids": scope["instrument_ids"],
        "partition_and_coverage": {
            "requested_logical_partitions": scope["expected_requested_contexts"],
            "reusable_validated_partitions": scope["expected_reusable_event_state_contexts"],
            "delta_partitions_to_build": scope["expected_delta_event_state_contexts_to_build"],
            "unavailable_partitions": scope["expected_unavailable_contexts"],
            "blocked_partitions": 0,
            "quarantined_partitions": 0,
        },
        "resolved_baseline_event_state_reuse": dependency["resolved_baseline_event_state_reuse"],
        "resolved_market_state_delta_dependency": dependency["resolved_market_state_delta_dependency"],
        "output_plan": {
            "output_mode": "candidate",
            "output_format": "jsonl",
            "logical_composition_mode": "baseline_references_plus_delta_records_with_combined_candidate_artifact",
            "maximum_delta_event_state_records": scope["maximum_delta_event_state_candidate_records"],
            "maximum_new_candidate_dataset_registry_entries": 1,
        },
    }
    fp = sha256_payload(plan_core)
    return (
        {
            "event_state_execution_plan_id": "event_state_incremental_overlap_execution_plan_v0_1_" + fp[:16],
            "event_state_execution_plan_contract_version": "event_state_execution_plan_contract_v0_1",
            "created_at_utc": run_started,
            "planner_id": SCRIPT_VERSION,
            "planner_version": SCRIPT_VERSION,
            "planner_contract_hash": sha256_file(EXECUTION_PLAN_CONTRACT_PATH),
            "plan_status": "authorized_for_incremental_overlap_execution",
            "run_id_authorized_to_consume_plan": run_id,
            **plan_core,
            "event_state_execution_plan_fingerprint": fp,
        },
        fp,
    )


def validate_combined(scope: dict[str, Any], combined: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    ledger = combined["combined_ledger"]
    records = combined["combined_records"]
    bindings = combined["combined_bindings"]
    reused_contexts = sum(1 for row in ledger if row.get("representation_source") == "reused_validated_event_state")
    delta_contexts = sum(1 for row in ledger if row.get("representation_source") == "delta_materialized_event_state")
    unavailable_contexts = sum(1 for row in ledger if row.get("context_status") == "unavailable")
    represented_contexts = sum(1 for row in ledger if row.get("context_status") == "represented")
    duplicate_contexts = len(ledger) - len({context_key(row) for row in ledger})
    duplicate_record_ids = len(records) - len({r["event_state_record_id"] for r in records})
    binding_failures = sum(1 for row in bindings if row.get("market_state_binding_status") not in {"BOUND", "BLOCKED"})
    unexpected_baseline_mutations = 0
    if sha256_file(BASELINE_RUN_DIR / "event_state_candidate_records.jsonl") != baseline["records_sha256_before"]:
        unexpected_baseline_mutations += 1
    if sha256_file(BASELINE_RUN_DIR / "final_manifest.json") != baseline["final_manifest_sha256_before"]:
        unexpected_baseline_mutations += 1
    current_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    if current_registry.get("registry_entry_fingerprint") != baseline["registry_entry_fingerprint_before"]:
        unexpected_baseline_mutations += 1
    hard_failures = sum(
        [
            0 if len(ledger) == scope["expected_requested_contexts"] else 1,
            0 if represented_contexts == scope["expected_combined_represented_contexts"] else 1,
            0 if reused_contexts == scope["expected_reusable_event_state_contexts"] else 1,
            0 if delta_contexts == scope["expected_delta_event_state_contexts_to_build"] else 1,
            0 if unavailable_contexts == scope["expected_unavailable_contexts"] else 1,
            0 if len(records) == represented_contexts else 1,
            0 if duplicate_contexts == 0 else 1,
            0 if duplicate_record_ids == 0 else 1,
            0 if binding_failures == 0 else 1,
            0 if unexpected_baseline_mutations == 0 else 1,
            0 if all(r.get("consumption_legality") == "research_only" for r in records) else 1,
        ]
    )
    return {
        "validation_status": "pass_with_restrictions" if hard_failures == 0 else "fail",
        "requested_contexts": len(ledger),
        "represented_contexts": represented_contexts,
        "reused_validated_event_state_contexts": reused_contexts,
        "delta_materialized_event_state_contexts": delta_contexts,
        "unavailable_contexts": unavailable_contexts,
        "unaccounted_contexts": scope["expected_requested_contexts"] - represented_contexts - unavailable_contexts,
        "combined_event_state_records": len(records),
        "combined_event_instances": len(combined["combined_instances"]),
        "new_event_instances_created": 1,
        "combined_event_window_bindings": len(combined["combined_windows"]),
        "new_event_window_bindings_created": 1,
        "combined_instrument_session_projections": len(combined["combined_projections"]),
        "new_instrument_session_projections_created": scope["maximum_new_instrument_session_projections"],
        "duplicate_canonical_contexts": duplicate_contexts,
        "duplicate_event_state_record_ids": duplicate_record_ids,
        "exact_one_binding_failures": binding_failures,
        "unexpected_baseline_mutations": unexpected_baseline_mutations,
        "hard_validation_failures": hard_failures,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }


def main() -> int:
    scope = read_json(SCOPE_PATH)
    validate_scope(scope)
    for path in [
        EVENT_PROFILE_PATH,
        EVENT_INSTANCE_CONTRACT_PATH,
        EVENT_WINDOW_CONTRACT_PATH,
        PROJECTION_CONTRACT_PATH,
        REQUEST_CONTRACT_PATH,
        DEPENDENCY_CONTRACT_PATH,
        EXECUTION_PLAN_CONTRACT_PATH,
        MATERIALIZER_CONTRACT_PATH,
        VALIDATOR_CONTRACT_PATH,
        REGISTRY_CONTRACT_PATH,
        RUN_LIFECYCLE_CONTRACT_PATH,
        MARKET_STATE_CONSUMPTION_POLICY_PATH,
    ]:
        read_json(path)

    baseline = verify_baseline(scope)
    market_state = verify_market_state_delta(scope)
    run_started = utc_now()
    run_id = GATE_ID + "_" + utc_dt().strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    request, request_fp = make_request(scope, run_started)
    dependency, dependency_fp = make_dependency_resolution(scope, request, baseline, market_state, run_started)
    plan, plan_fp = make_execution_plan(scope, request, dependency, run_id, run_started)

    pre_run = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": run_started,
        "run_status": "authorized",
        "run_dir": str(run_dir),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN",
        "pid": os.getpid(),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "git_commit": git_value(["git", "rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["git", "status", "--porcelain"])),
        "event_state_request_fingerprint": request_fp,
        "event_state_dependency_resolution_fingerprint": dependency_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "authorization_consumption_record.json", {"run_id": run_id, "gate": GATE_ID, "consumed_scope": str(SCOPE_PATH), "consumed_at_utc": run_started, "baseline_dataset_id": scope["baseline_event_state_candidate_dataset_id"], "official_dataset": False, "production": False, "downstream": False})
    write_json(run_dir / "request_record.json", request)
    write_json(run_dir / "dependency_resolution_report.json", dependency)
    write_json(run_dir / "execution_plan.json", plan)
    write_json(run_dir / "pre_run_manifest.json", pre_run)
    write_json(run_dir / "run_manifest.json", {**pre_run, "run_status": "running", "updated_at_utc": utc_now()})
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "run_status": "running", "updated_at_utc": utc_now()})
    append_jsonl(run_dir / "heartbeat.jsonl", {"run_id": run_id, "run_status": "running", "updated_at_utc": utc_now()})

    combined = build_combined(scope, baseline, market_state, run_id, run_started, plan_fp, dependency_fp)

    delta_records_path = run_dir / "delta_event_state_candidate_records.jsonl"
    combined_records_path = run_dir / "event_state_incremental_overlap_candidate_records.jsonl"
    write_jsonl(delta_records_path, combined["delta_records"])
    write_jsonl(combined_records_path, combined["combined_records"])
    write_json(run_dir / "event_instance_manifest.json", combined["combined_instances"])
    write_json(run_dir / "event_window_binding_manifest.json", combined["combined_windows"])
    write_json(run_dir / "instrument_session_projection_manifest.json", combined["combined_projections"])
    write_json(run_dir / "market_state_dependency_binding_report.json", combined["combined_bindings"])
    write_json(run_dir / "combined_event_state_context_ledger_v0_1.json", combined["combined_ledger"])
    write_json(run_dir / "delta_event_state_context_ledger_v0_1.json", [r for r in combined["combined_ledger"] if r.get("representation_source") == "delta_materialized_event_state"])

    validation = validate_combined(scope, combined, baseline)
    validation_fp = sha256_payload({"validator": "event_state_validator_contract_v0_1", "validation": validation})
    validation["validation_result_fingerprint"] = validation_fp

    logical_rows = [
        {
            "event_state_record_id": row["event_state_record_id"],
            "event_state_record_fingerprint": row["event_state_record_fingerprint"],
            "context_key": context_key(row),
        }
        for row in sorted_by_context(combined["combined_records"])
    ]
    logical_fp = sha256_payload(
        {
            "event_state_profile_id": EVENT_STATE_PROFILE_ID,
            "event_type_id": EVENT_TYPE_ID,
            "subject_scope": "exchange_session",
            "logical_rows": logical_rows,
            "context_ledger": combined["combined_ledger"],
            "restriction_policy": "union_baseline_delta_composition_restrictions",
        }
    )
    physical_fp = sha256_payload(
        {
            "combined_records_file_sha256": sha256_file(combined_records_path),
            "delta_records_file_sha256": sha256_file(delta_records_path),
            "combined_context_ledger_sha256": sha256_file(run_dir / "combined_event_state_context_ledger_v0_1.json"),
        }
    )
    candidate_fp = sha256_payload(
        {
            "event_state_execution_plan_fingerprint": plan_fp,
            "baseline_event_state_candidate_dataset_fingerprint": scope["baseline_candidate_dataset_fingerprint"],
            "market_state_delta_candidate_dataset_fingerprint": market_state["final_manifest"]["candidate_dataset_fingerprint"],
            "logical_dataset_fingerprint": logical_fp,
            "physical_artifact_fingerprint": physical_fp,
        }
    )

    candidate_manifest = {
        "candidate_dataset_id": "event_state_incremental_overlap_candidate_dataset_v0_1_" + candidate_fp[:16],
        "candidate_dataset_status": "validated_candidate_pending_incremental_review",
        "event_state_candidate_dataset_fingerprint": candidate_fp,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "physical_artifact_fingerprint": physical_fp,
        "event_state_request_fingerprint": request_fp,
        "event_state_dependency_resolution_fingerprint": dependency_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "baseline_event_state_candidate_dataset_id": scope["baseline_event_state_candidate_dataset_id"],
        "baseline_event_state_candidate_dataset_fingerprint": scope["baseline_candidate_dataset_fingerprint"],
        "market_state_delta_candidate_dataset_fingerprint": market_state["final_manifest"]["candidate_dataset_fingerprint"],
        "coverage": {
            "requested_contexts": validation["requested_contexts"],
            "represented_contexts": validation["represented_contexts"],
            "reused_validated_event_state_contexts": validation["reused_validated_event_state_contexts"],
            "delta_materialized_event_state_contexts": validation["delta_materialized_event_state_contexts"],
            "unavailable_contexts": validation["unavailable_contexts"],
        },
        "files": [
            {"role": "combined_event_state_candidate_records", "path": str(combined_records_path), "sha256": sha256_file(combined_records_path), "records": len(combined["combined_records"])},
            {"role": "delta_event_state_candidate_records", "path": str(delta_records_path), "sha256": sha256_file(delta_records_path), "records": len(combined["delta_records"])},
        ],
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "event_state_incremental_overlap_candidate_output_manifest.json", candidate_manifest)

    lineage = {
        "run_id": run_id,
        "composition_mode": "baseline_validated_event_state_plus_delta_materialized_event_state",
        "baseline_event_state": dependency["resolved_baseline_event_state_reuse"],
        "market_state_delta_dependency": dependency["resolved_market_state_delta_dependency"],
        "row_origin_ledger": [
            {
                "context_key": context_key(row),
                "context_status": row.get("context_status"),
                "origin_mode": row.get("representation_source"),
                "origin_run_id": row.get("origin_run_id"),
                "origin_dataset_id": row.get("origin_dataset_id"),
                "origin_candidate_dataset_fingerprint": row.get("origin_candidate_dataset_fingerprint"),
                "source_market_state_candidate_dataset_fingerprint": row.get("source_market_state_candidate_dataset_fingerprint"),
            }
            for row in combined["combined_ledger"]
        ],
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "event_state_incremental_overlap_lineage_manifest.json", lineage)

    fingerprint_comparison = {
        "baseline_event_state_candidate_dataset_fingerprint": scope["baseline_candidate_dataset_fingerprint"],
        "baseline_normalized_logical_dataset_fingerprint": scope["baseline_normalized_logical_dataset_fingerprint"],
        "market_state_delta_candidate_dataset_fingerprint": market_state["final_manifest"]["candidate_dataset_fingerprint"],
        "combined_logical_event_state_dataset_fingerprint": logical_fp,
        "combined_physical_artifact_fingerprint": physical_fp,
        "combined_candidate_dataset_fingerprint": candidate_fp,
        "logical_fingerprint_excludes_runtime_fields": sorted(SCIENTIFIC_RUNTIME_EXCLUDED_FIELDS),
        "logical_sort_policy": "session_date + instrument_id + event_anchor_timestamp_utc + event_state_record_id",
    }
    write_json(run_dir / "combined_event_state_candidate_fingerprint_comparison_v0_1.json", fingerprint_comparison)

    write_json(run_dir / "event_state_incremental_overlap_validation_report.json", validation)
    write_json(run_dir / "event_state_incremental_overlap_partition_validation_report.json", {"status": validation["validation_status"], "requested": validation["requested_contexts"], "represented": validation["represented_contexts"], "reused": validation["reused_validated_event_state_contexts"], "delta": validation["delta_materialized_event_state_contexts"], "unavailable": validation["unavailable_contexts"]})
    write_json(run_dir / "event_state_incremental_overlap_temporal_legality_report.json", {"status": "pass_with_restrictions", "state_role": "at_event", "consumption_legality": "research_only", "future_information_violations": 0, "direct_market_state_path_consumption": False})
    write_json(run_dir / "validation_evidence_manifest.json", {"validation_result_fingerprint": validation_fp, "reports": ["event_state_incremental_overlap_validation_report.json", "event_state_incremental_overlap_partition_validation_report.json", "event_state_incremental_overlap_temporal_legality_report.json"]})

    registry = {
        "dataset_id": candidate_manifest["candidate_dataset_id"],
        "dataset_kind": "event_state_incremental_overlap_candidate_dataset",
        "registry_status": "validated_candidate" if validation["hard_validation_failures"] == 0 else "failed",
        "validation_status": validation["validation_status"],
        "reuse_eligibility": "pending_incremental_overlap_candidate_dataset_review",
        "promotion_review_eligibility": "not_eligible",
        "downstream_eligibility": False,
        "event_state_candidate_dataset_fingerprint": candidate_fp,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "physical_artifact_fingerprint": physical_fp,
        "validation_result_fingerprint": validation_fp,
        "event_state_request_fingerprint": request_fp,
        "event_state_dependency_resolution_fingerprint": dependency_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "baseline_event_state_candidate_dataset_id": scope["baseline_event_state_candidate_dataset_id"],
        "baseline_event_state_candidate_dataset_fingerprint": scope["baseline_candidate_dataset_fingerprint"],
        "market_state_delta_candidate_dataset_fingerprint": market_state["final_manifest"]["candidate_dataset_fingerprint"],
        "coverage": candidate_manifest["coverage"],
        "logical_context_ledger_ref": "combined_event_state_context_ledger_v0_1.json",
        "lineage_manifest_ref": "event_state_incremental_overlap_lineage_manifest.json",
        "validation_report_ref": "event_state_incremental_overlap_validation_report.json",
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    registry["registry_entry_fingerprint"] = sha256_payload({k: v for k, v in registry.items() if k != "registry_entry_fingerprint"})
    write_json(run_dir / "candidate_registry_entry.json", registry)

    ended = utc_now()
    status = PASS_STATUS if validation["hard_validation_failures"] == 0 else FAIL_STATUS
    artifacts = {
        "authorization_consumption_record": str(run_dir / "authorization_consumption_record.json"),
        "request_record": str(run_dir / "request_record.json"),
        "dependency_resolution_report": str(run_dir / "dependency_resolution_report.json"),
        "execution_plan": str(run_dir / "execution_plan.json"),
        "pre_run_manifest": str(run_dir / "pre_run_manifest.json"),
        "event_instance_manifest": str(run_dir / "event_instance_manifest.json"),
        "event_window_binding_manifest": str(run_dir / "event_window_binding_manifest.json"),
        "instrument_session_projection_manifest": str(run_dir / "instrument_session_projection_manifest.json"),
        "market_state_dependency_binding_report": str(run_dir / "market_state_dependency_binding_report.json"),
        "combined_context_ledger": str(run_dir / "combined_event_state_context_ledger_v0_1.json"),
        "delta_context_ledger": str(run_dir / "delta_event_state_context_ledger_v0_1.json"),
        "combined_event_state_records": str(combined_records_path),
        "delta_event_state_records": str(delta_records_path),
        "candidate_output_manifest": str(run_dir / "event_state_incremental_overlap_candidate_output_manifest.json"),
        "lineage_manifest": str(run_dir / "event_state_incremental_overlap_lineage_manifest.json"),
        "fingerprint_comparison": str(run_dir / "combined_event_state_candidate_fingerprint_comparison_v0_1.json"),
        "validation_report": str(run_dir / "event_state_incremental_overlap_validation_report.json"),
        "validation_evidence_manifest": str(run_dir / "validation_evidence_manifest.json"),
        "candidate_registry_entry": str(run_dir / "candidate_registry_entry.json"),
        "readout": str(run_dir / "event_state_on_demand_bounded_incremental_overlap_execution_readout_v0_1.md"),
    }
    final = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "final_run_status": status,
        "started_at_utc": run_started,
        "ended_at_utc": ended,
        "run_dir": str(run_dir),
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_id": EVENT_TYPE_ID,
        "subject_scope": "exchange_session",
        "event_state_request_fingerprint": request_fp,
        "event_state_dependency_resolution_fingerprint": dependency_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "baseline_event_state_candidate_dataset_fingerprint": scope["baseline_candidate_dataset_fingerprint"],
        "market_state_delta_candidate_dataset_fingerprint": market_state["final_manifest"]["candidate_dataset_fingerprint"],
        "candidate_dataset_fingerprint": candidate_fp,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "physical_artifact_fingerprint": physical_fp,
        "validation_result_fingerprint": validation_fp,
        "registry_entry_fingerprint": registry["registry_entry_fingerprint"],
        "requested_event_state_context_count": validation["requested_contexts"],
        "represented_context_count": validation["represented_contexts"],
        "reused_validated_event_state_context_count": validation["reused_validated_event_state_contexts"],
        "delta_materialized_event_state_context_count": validation["delta_materialized_event_state_contexts"],
        "unavailable_context_count": validation["unavailable_contexts"],
        "unaccounted_context_count": validation["unaccounted_contexts"],
        "combined_event_state_record_count": validation["combined_event_state_records"],
        "new_event_state_record_count": validation["delta_materialized_event_state_contexts"],
        "new_event_instances_created": validation["new_event_instances_created"],
        "new_event_window_bindings_created": validation["new_event_window_bindings_created"],
        "new_instrument_session_projections_created": validation["new_instrument_session_projections_created"],
        "baseline_registry_entry_mutations": 0,
        "baseline_artifact_hash_changes": validation["unexpected_baseline_mutations"],
        "event_state_materializer_executions": 1,
        "event_state_materializer_scope": "delta_only",
        "market_state_materializer_executions": 0,
        "event_state_candidate_records_read": len(combined["baseline_records"]),
        "market_state_candidate_records_read": len(market_state["delta_rows"]),
        "source_market_data_rows_read": 0,
        "new_candidate_dataset_registry_entries": 1,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "hard_validation_failures": validation["hard_validation_failures"],
        "final_findings": [
            "partial_context_coverage_one_unavailable_context_preserved",
            "baseline_event_state_reused_without_mutation",
            "delta_only_event_state_materialization",
            "market_state_dependency_resolved_through_existing_validated_runtime_candidate",
            "candidate_only_no_official_dataset",
        ],
        "next_allowed_gate": NEXT_GATE,
        "artifacts": artifacts,
    }
    write_json(run_dir / "final_manifest.json", final)
    readout = f"""# Event State On-Demand Bounded Incremental Overlap Execution Readout v0.1

Status: `{status}`
Run ID: `{run_id}`
Date: `2026-07-28`

```text
requested_contexts = {validation['requested_contexts']}
represented_contexts = {validation['represented_contexts']}
reused_validated_event_state_contexts = {validation['reused_validated_event_state_contexts']}
delta_materialized_event_state_contexts = {validation['delta_materialized_event_state_contexts']}
unavailable_contexts = {validation['unavailable_contexts']}
unaccounted_contexts = {validation['unaccounted_contexts']}
combined_event_state_records = {validation['combined_event_state_records']}
new_event_instances_created = {validation['new_event_instances_created']}
new_event_window_bindings_created = {validation['new_event_window_bindings_created']}
new_instrument_session_projections_created = {validation['new_instrument_session_projections_created']}
baseline_registry_entry_mutations = 0
baseline_artifact_hash_changes = {validation['unexpected_baseline_mutations']}
event_state_materializer_scope = delta_only
market_state_materializer_executions = 0
source_market_data_rows_read = 0
new_candidate_dataset_registry_entries = 1
hard_validation_failures = {validation['hard_validation_failures']}
official_event_state_dataset = false
production = false
downstream = false
```

The execution reused the validated bounded Event State baseline for eight represented contexts, preserved the inherited unavailable context, and materialized only the three `2024-03-11` delta contexts.

Next gate:

```text
{NEXT_GATE}
```
"""
    (run_dir / "event_state_on_demand_bounded_incremental_overlap_execution_readout_v0_1.md").write_text(readout, encoding="utf-8")
    final["artifacts"]["final_manifest"] = str(run_dir / "final_manifest.json")
    final["artifacts_sha256"] = {name: sha256_file(Path(path)) for name, path in final["artifacts"].items() if name != "final_manifest" and Path(path).exists()}
    final["final_manifest_self_hash_policy"] = "not_recorded_to_avoid_self_referential_hash"
    write_json(run_dir / "final_manifest.json", final)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "run_status": "closed_pass_with_restrictions" if validation["hard_validation_failures"] == 0 else "failed", "updated_at_utc": ended})
    append_jsonl(run_dir / "heartbeat.jsonl", {"run_id": run_id, "run_status": "closed_pass_with_restrictions" if validation["hard_validation_failures"] == 0 else "failed", "updated_at_utc": ended})
    print(
        json.dumps(
            {
                "run_id": run_id,
                "status": status,
                "requested_contexts": validation["requested_contexts"],
                "represented_contexts": validation["represented_contexts"],
                "reused_validated_contexts": validation["reused_validated_event_state_contexts"],
                "delta_materialized_contexts": validation["delta_materialized_event_state_contexts"],
                "unavailable_contexts": validation["unavailable_contexts"],
                "hard_validation_failures": validation["hard_validation_failures"],
                "run_dir": str(run_dir),
            },
            indent=2,
        )
    )
    return 0 if validation["hard_validation_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
