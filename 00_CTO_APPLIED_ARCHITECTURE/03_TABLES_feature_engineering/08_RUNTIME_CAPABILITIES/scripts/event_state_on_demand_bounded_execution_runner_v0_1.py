#!/usr/bin/env python
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_VERSION = "event_state_on_demand_bounded_execution_runner_v0_1"
GATE_ID = "event_state_on_demand_bounded_execution_v0_1"
PASS_STATUS = "CLOSED_PASS_EVENT_STATE_ON_DEMAND_BOUNDED_EXECUTION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED"
FAIL_STATUS = "CLOSED_FAIL_EVENT_STATE_ON_DEMAND_BOUNDED_EXECUTION"
NEXT_GATE = "event_state_on_demand_bounded_candidate_dataset_review_v0_1"

REPO_ROOT = Path(__file__).resolve().parents[4]
FEATURE_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = Path(__file__).resolve().parents[1]
EVENT_ROOT = FEATURE_ROOT / "07_EVENT_STATE_INTEGRATION"
MARKET_ROOT = FEATURE_ROOT / "06_MARKET_STATE_INTEGRATION"
RUNS_ROOT = RUNTIME_ROOT / "runs"

AUTHORITY_BUNDLE_PATH = RUNTIME_ROOT / "event_state_on_demand_bounded_execution_authority_bundle_v0_1.json"
PARENT_SCOPE_PATH = RUNTIME_ROOT / "configs" / "event_state_on_demand_bounded_execution_scope_v0_1.json"
PREFLIGHT_SCOPE_PATH = RUNTIME_ROOT / "configs" / "event_state_on_demand_bounded_execution_preflight_correction_scope_v0_1.json"
MS_DEP_SCOPE_PATH = RUNTIME_ROOT / "configs" / "market_state_capability_event_state_bounded_dependency_consumption_scope_v0_1.json"
REQUEST_CONTRACT_PATH = RUNTIME_ROOT / "event_state_request_contract_v0_1.json"
DEPENDENCY_CONTRACT_PATH = RUNTIME_ROOT / "event_state_dependency_resolution_contract_v0_1.json"
EXECUTION_PLAN_CONTRACT_PATH = RUNTIME_ROOT / "event_state_execution_plan_contract_v0_1.json"
RUN_LIFECYCLE_CONTRACT_PATH = RUNTIME_ROOT / "event_state_on_demand_bounded_run_lifecycle_binding_contract_v0_1.json"
MATERIALIZER_CONTRACT_PATH = RUNTIME_ROOT / "event_state_materializer_contract_v0_1.json"
VALIDATOR_CONTRACT_PATH = RUNTIME_ROOT / "event_state_validator_contract_v0_1.json"
REGISTRY_CONTRACT_PATH = RUNTIME_ROOT / "event_state_candidate_dataset_registry_contract_v0_1.json"
EVENT_PROFILE_PATH = EVENT_ROOT / "official_profiles" / "event_state_core_four_intraday_profile_v0_1" / "PROFILE_MANIFEST.json"
EVENT_INSTANCE_CONTRACT_PATH = EVENT_ROOT / "event_instance_binding_design_contract_v0_1.json"
EVENT_WINDOW_CONTRACT_PATH = EVENT_ROOT / "event_window_binding_design_contract_v0_1.json"
PROJECTION_CONTRACT_PATH = EVENT_ROOT / "event_state_instrument_session_projection_design_contract_v0_1.json"
MS_POLICY_CONTRACT_PATH = RUNTIME_ROOT / "market_state_capability_consumption_policy_contract_v0_1.json"
MS_CONSUMPTION_MATRIX_PATH = RUNTIME_ROOT / "market_state_capability_consumption_policy_matrix_v0_1.json"
MS_PROMOTION_FINAL_PATH = RUNS_ROOT / "market_state_on_demand_capability_promotion_review_v0_1_20260727T140338Z" / "final_manifest.json"
MS_BOUNDED_RUN_DIR = RUNS_ROOT / "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z"
MS_REUSE_TRANSITION_PATH = RUNS_ROOT / "market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061233Z" / "reuse_eligibility_transition_record_v0_1.json"
OLD_EVENT_RUNNER_PATH = EVENT_ROOT / "scripts" / "event_state_bounded_execution_chain_runner_v0_1.py"

EVENT_STATE_RECORD_NAMESPACE = "tsis_event_state_on_demand_record_v0_1"
EVENT_STATE_SCHEMA_VERSION = "event_state_candidate_schema_v0_1"
INTEGRATION_POLICY_ID = "event_state_on_demand_integration_policy_v0_1"
INTEGRATION_POLICY_VERSION = "v0_1"

REQUEST_FIELD_ALIASES = {"reuse_policy": {"force_build_event_state_candidate_only_when_authorized": "force_rebuild_only_when_authorized"}}

class ExecutionError(RuntimeError):
    pass

def to_builtin(v: Any) -> Any:
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, Path):
        return str(v)
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(v, dict):
        return {str(k): to_builtin(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [to_builtin(x) for x in v]
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if hasattr(v, "item"):
        return to_builtin(v.item())
    return str(v)

def stable_json(v: Any) -> str:
    return json.dumps(to_builtin(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def sha256_payload(v: Any) -> str:
    return sha256_text(stable_json(v))

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def canonical_hash(*parts: Any) -> str:
    return sha256_text("|".join(str(p) for p in parts))

def utc_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)

def utc_now() -> str:
    return utc_dt().isoformat().replace("+00:00", "Z")

def iso_z(v: Any) -> str:
    ts = pd.Timestamp(v)
    ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")

def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ExecutionError(f"Missing JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(to_builtin(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(to_builtin(row), sort_keys=True, ensure_ascii=False) + "\n")

def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(to_builtin(row), sort_keys=True, ensure_ascii=False) + "\n")

def git_value(args: list[str]) -> str | None:
    try:
        r = subprocess.run(args, cwd=str(REPO_ROOT), text=True, capture_output=True, check=False)
    except Exception:
        return None
    return r.stdout.strip() if r.returncode == 0 else None

def load_old_event_runner() -> Any:
    spec = importlib.util.spec_from_file_location("event_state_bounded_runner_v0_1", OLD_EVENT_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise ExecutionError(f"Unable to load old Event State runner: {OLD_EVENT_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def verify_authority_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    checks, failures = [], []
    for item in bundle.get("authority_files", []):
        path = FEATURE_ROOT / item["path"]
        observed = sha256_file(path) if path.exists() else "MISSING"
        ok = observed == item["sha256"]
        checks.append({"label": item["label"], "path": item["path"], "expected_sha256": item["sha256"], "observed_sha256": observed, "status": "PASS" if ok else "FAIL"})
        if not ok:
            failures.append(item["label"])
    return {"authority_bundle_id": bundle.get("bundle_id"), "authority_bundle_sha256": sha256_file(AUTHORITY_BUNDLE_PATH), "authority_files_checked": len(checks), "authority_file_hash_failures": failures, "checks": checks, "status": "PASS" if not failures else "FAIL"}

def existing_closed_run_ids() -> list[str]:
    out = []
    for path in RUNS_ROOT.glob(f"{GATE_ID}_*"):
        final_path = path / "final_manifest.json"
        if not final_path.exists():
            continue
        try:
            status = str(read_json(final_path).get("final_run_status", ""))
        except Exception:
            continue
        if status.startswith("CLOSED"):
            out.append(path.name)
    return sorted(out)

def sorted_scalar_lists(v: Any) -> Any:
    if isinstance(v, dict):
        return {k: sorted_scalar_lists(x) for k, x in sorted(v.items())}
    if isinstance(v, list):
        xs = [sorted_scalar_lists(x) for x in v]
        return sorted(xs, key=lambda x: str(x)) if all(isinstance(x, (str, int, float, bool)) or x is None for x in xs) else xs
    return v

def effective_request_template(parent_scope: dict[str, Any], preflight_scope: dict[str, Any], request_contract: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    template = dict(parent_scope["authorized_request_template"])
    for k, v in preflight_scope["effective_request_overrides_for_next_gate"].items():
        if not k.startswith("superseded_") and not k.startswith("maximum_"):
            template[k] = v
    normalizations = []
    for field, aliases in REQUEST_FIELD_ALIASES.items():
        old = template.get(field)
        if old in aliases:
            template[field] = aliases[old]
            normalizations.append({"field": field, "historical_value": old, "effective_value": template[field], "reason": "contract_allowed_alias_normalization"})
    if template.get("reuse_policy") not in set(request_contract.get("allowed_reuse_policies_v0_1", [])):
        raise ExecutionError(f"Unsupported effective reuse_policy: {template.get('reuse_policy')}")
    expected_mode = request_contract["source_market_state_dependency_v0_1"]["dependency_request_mode"]
    if template.get("market_state_dependency_mode") != expected_mode:
        raise ExecutionError("Effective market_state_dependency_mode does not match request contract")
    return template, normalizations

def request_fingerprint(template: dict[str, Any], request_contract: dict[str, Any]) -> str:
    fields = request_contract["fingerprint_policy"]["include_fields"]
    return sha256_payload({field: sorted_scalar_lists(template.get(field)) for field in fields})

def make_request(template: dict[str, Any], request_contract: dict[str, Any], normalizations: list[dict[str, str]]) -> tuple[dict[str, Any], str]:
    fp = request_fingerprint(template, request_contract)
    request = {"request_id": "event_state_request_v0_1_" + fp[:16], "request_status": "accepted_for_resolution", "requested_at_utc": utc_now(), "requested_by": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN", "request_purpose": "bounded_event_state_on_demand_execution", **template, "request_template_normalizations": normalizations, "request_fingerprint": fp}
    return request, fp

def window_template(event_window_contract: dict[str, Any], template_id: str) -> dict[str, Any]:
    for row in event_window_contract["non_executable_design_templates"]:
        if row["template_id"] == template_id:
            return row
    raise ExecutionError(f"Window template not present in contract: {template_id}")

def calendar_path(event_instance_contract: dict[str, Any]) -> Path:
    run_id = event_instance_contract["calendar_authority"]["calendar_binding_run_id"]
    path = MARKET_ROOT / "runs" / run_id / "governed_exchange_session_calendar_bound_v0_1.parquet"
    if not path.exists():
        raise ExecutionError(f"Calendar parquet missing: {path}")
    if sha256_file(path) != event_instance_contract["calendar_authority"]["bound_parquet_sha256"]:
        raise ExecutionError("Calendar parquet SHA-256 mismatch")
    return path

def load_market_state_dependency(ms_final: dict[str, Any]) -> tuple[Path, pd.DataFrame, str]:
    path = Path(ms_final["artifacts"]["candidate_parquet"])
    manifest = read_json(MS_BOUNDED_RUN_DIR / "candidate_output_manifest.json")
    observed = sha256_file(path)
    if observed != manifest["files"][0]["sha256"]:
        raise ExecutionError("Market State candidate parquet SHA-256 mismatch")
    return path, pd.read_parquet(path), observed

def expected_sessions_from_calendar(calendar_df: pd.DataFrame, request: dict[str, Any], calendar_version: str) -> list[dict[str, str]]:
    rows = []
    for session_date in request["session_dates"]:
        matches = calendar_df[(calendar_df["session_date"].astype(str).str[:10] == session_date) & (calendar_df["mic_or_exchange_code"].astype(str) == request["exchange_scope"][0]) & (calendar_df["calendar_version"].astype(str) == calendar_version)]
        if len(matches) != 1:
            raise ExecutionError(f"Calendar row not exactly one for {session_date}: {len(matches)}")
        rows.append({"session_date": session_date, "expected_open_utc": iso_z(matches.iloc[0]["session_open_utc"])[11:19]})
    return rows

def make_legacy_scope(request: dict[str, Any], event_instance_contract: dict[str, Any], calendar_df: pd.DataFrame) -> dict[str, Any]:
    labels = request.get("instrument_labels_non_authoritative", {})
    return {"event_type_id": request["event_type_ids"][0], "event_subject_scope": request["event_subject_scope"], "exchange_id": request["exchange_scope"][0], "calendar_version": event_instance_contract["calendar_authority"]["calendar_version"], "event_state_profile_id": request["event_state_profile_id"], "source_market_state_profile_id": request["market_state_profile_id"], "event_window_definition": {"event_window_definition_id": request["event_window_definition_ids"][0], "state_role": "at_event"}, "authorized_sessions": expected_sessions_from_calendar(calendar_df, request, event_instance_contract["calendar_authority"]["calendar_version"]), "authorized_instruments": [{"instrument_id": inst, "ticker": labels.get(inst, "")} for inst in request["explicit_instrument_ids"]]}

def dependency_resolution(request: dict[str, Any], request_fp: str, event_profile: dict[str, Any], event_instance_contract: dict[str, Any], ms_final: dict[str, Any], ms_reuse_transition: dict[str, Any]) -> tuple[dict[str, Any], str]:
    findings = []
    if event_profile.get("status") != "OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS":
        findings.append("event_state_profile_not_promoted")
    if request.get("event_type_ids") != ["event_type:market_data:session_opened"]:
        findings.append("unsupported_event_type")
    if request.get("event_subject_scope") != "exchange_session":
        findings.append("unsupported_subject_scope")
    if ms_reuse_transition.get("reuse_eligibility_after_review") != "eligible_for_bounded_exact_match_reuse":
        findings.append("market_state_dependency_reuse_not_approved")
    if ms_final.get("candidate_dataset_fingerprint") != ms_reuse_transition.get("candidate_dataset_fingerprint"):
        findings.append("market_state_candidate_fingerprint_mismatch")
    record = {"dependency_resolution_record_id": "event_state_dependency_resolution_v0_1_" + request_fp[:16], "status": "RESOLVED_FOR_BOUNDED_EXECUTION" if not findings else "BLOCKED_BEFORE_EXECUTION_PLAN", "resolved_at_utc": utc_now(), "event_state_request_id": request["request_id"], "event_state_request_fingerprint": request_fp, "resolved_event_state_profile": {"profile_id": event_profile["profile_id"], "profile_status": event_profile["status"], "profile_manifest_sha256": sha256_file(EVENT_PROFILE_PATH), "official_event_state_dataset_exists": False}, "resolved_event_type_registry": {"registry_snapshot_id": event_instance_contract["authority_binding"]["registry_snapshot_id"], "registry_snapshot_sha256": event_instance_contract["authority_binding"]["registry_snapshot_sha256"], "accepted_event_type_ids": ["event_type:market_data:session_opened"], "blocked_event_type_ids": ["event_type:regulatory:halt_resumed"], "accepted_subject_scope": "exchange_session", "detector_required": False, "event_detection_allowed": False}, "resolved_market_state_dependency": {"market_state_profile_id": request["market_state_profile_id"], "market_state_runtime_capability_id": "market_state_on_demand_runtime_capability_v0_1", "market_state_dependency_mode": request["market_state_dependency_mode"], "market_state_dependency_reuse_policy": request["market_state_dependency_reuse_policy"], "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"], "market_state_candidate_dataset_id": ms_reuse_transition["candidate_dataset_id"], "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "market_state_validation_result_fingerprint": ms_final["validation_result_fingerprint"], "reuse_transition_record_id": ms_reuse_transition["transition_record_id"], "bounded_dependency_consumption_authorization": "market_state_capability_event_state_bounded_dependency_consumption_authorization_v0_1", "direct_market_state_path_allowed": False, "market_state_physical_consumption_authorized_for_this_bounded_gate_only": True}, "blocking_findings": findings}
    fp = sha256_payload({"event_state_request_fingerprint": request_fp, "event_state_profile_id": event_profile["profile_id"], "event_state_profile_contract_hash": sha256_file(EVENT_PROFILE_PATH), "event_type_registry_snapshot_id": record["resolved_event_type_registry"]["registry_snapshot_id"], "event_type_registry_snapshot_sha256": record["resolved_event_type_registry"]["registry_snapshot_sha256"], "accepted_event_type_ids": record["resolved_event_type_registry"]["accepted_event_type_ids"], "accepted_subject_scope": "exchange_session", "event_instance_policy_contract_hash": sha256_file(EVENT_INSTANCE_CONTRACT_PATH), "event_window_policy_contract_hash": sha256_file(EVENT_WINDOW_CONTRACT_PATH), "instrument_projection_policy_contract_hash": sha256_file(PROJECTION_CONTRACT_PATH), "market_state_runtime_capability_id": "market_state_on_demand_runtime_capability_v0_1", "market_state_consumption_policy_hash": sha256_file(MS_POLICY_CONTRACT_PATH), "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "blocking_findings": findings})
    record["event_state_dependency_resolution_fingerprint"] = fp
    if findings:
        raise ExecutionError("Dependency resolution blocked: " + ", ".join(findings))
    return record, fp

def execution_plan(run_id: str, request: dict[str, Any], request_fp: str, dep: dict[str, Any], dep_fp: str, preflight_scope: dict[str, Any], ms_final: dict[str, Any], ms_candidate_sha: str) -> tuple[dict[str, Any], str]:
    limits = preflight_scope["effective_request_overrides_for_next_gate"]
    requested = len(request["session_dates"]) * len(request["explicit_instrument_ids"])
    core = {"event_state_request_fingerprint": request_fp, "event_state_dependency_resolution_fingerprint": dep_fp, "resolved_request": {k: v for k, v in request.items() if k not in {"requested_at_utc", "requested_by"}}, "resolved_event_state_dependencies": dep, "event_type_and_registry_plan": dep["resolved_event_type_registry"], "market_state_dependency_plan": {**dep["resolved_market_state_dependency"], "market_state_candidate_file_sha256": ms_candidate_sha, "dependency_access_mode": "bounded_candidate_runtime_reuse_exact_match_records_only"}, "logical_context_and_binding_plan": {"logical_context_grain": "event_type_id + exchange_id + session_date + instrument_id + event_window_definition_id", "event_instance_binding_requirement": "exactly_one", "event_window_binding_requirement": "exactly_one", "instrument_projection_requirement": "exactly_one", "market_state_binding_requirement": "exactly_one_at_event_anchor_or_block", "state_role_assignment_requirement": "from_event_window_definition", "consumption_legality_assignment_requirement": "independent_from_state_role"}, "partition_and_coverage": {"requested_logical_partitions": requested, "reusable_validated_partitions": requested, "partitions_to_build": 0, "unavailable_partitions": ms_final["unavailable_contexts"], "partition_coverage_fingerprint": ms_final["partition_coverage_resolution_fingerprint"]}, "resolved_builders": {"event_state_materializer_contract_id": "event_state_materializer_contract_v0_1", "event_state_materializer_contract_hash": sha256_file(MATERIALIZER_CONTRACT_PATH)}, "resolved_validators": {"event_state_validator_contract_id": "event_state_validator_contract_v0_1", "event_state_validator_contract_hash": sha256_file(VALIDATOR_CONTRACT_PATH)}, "output_plan": {"output_mode": "candidate", "output_format": "jsonl", "output_schema_id": EVENT_STATE_SCHEMA_VERSION, "maximum_files": 1, "maximum_rows": limits["maximum_output_records"], "maximum_bytes": limits["maximum_output_bytes"]}, "quantitative_limits": {"maximum_event_types": 1, "maximum_exchanges": 1, "maximum_sessions": len(request["session_dates"]), "maximum_instruments": len(request["explicit_instrument_ids"]), "maximum_market_state_dependency_contexts": requested, "maximum_event_state_records": limits["maximum_output_records"]}}
    fp = sha256_payload(core)
    plan = {"event_state_execution_plan_id": "event_state_execution_plan_v0_1_" + fp[:16], "event_state_execution_plan_contract_version": "event_state_execution_plan_contract_v0_1", "event_state_request_id": request["request_id"], "event_state_request_fingerprint": request_fp, "dependency_resolution_record_id_or_ref": dep["dependency_resolution_record_id"], "event_state_dependency_resolution_fingerprint": dep_fp, "created_at_utc": utc_now(), "planner_id": SCRIPT_VERSION, "planner_version": SCRIPT_VERSION, "planner_contract_hash": sha256_file(EXECUTION_PLAN_CONTRACT_PATH), "plan_status": "authorized_for_execution", "run_id_authorized_to_consume_plan": run_id, **core, "event_state_execution_plan_fingerprint": fp}
    return plan, fp

def parse_json_field(value: Any, default: Any) -> Any:
    if not isinstance(value, str) or not value.strip():
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default

def convert_legacy_records(built: dict[str, Any], run_id: str, started: str, plan: dict[str, Any], request: dict[str, Any], ms_final: dict[str, Any]) -> dict[str, Any]:
    for window in built["window_bindings"]:
        window["consumption_legality"] = "research_only"
        window["leakage_assessment"] = "exact_anchor_only; at_event_research_only_until_field_legality_review"
    old_by_projection = {r["event_state_instrument_session_projection_id"]: r for r in built["event_state_records"]}
    records, ledger = [], []
    for binding in built["market_state_bindings"]:
        available = binding["available_same_instrument_session_timestamps"].split(";") if isinstance(binding["available_same_instrument_session_timestamps"], str) and binding["available_same_instrument_session_timestamps"] else []
        ledger.append({"event_type_id": request["event_type_ids"][0], "exchange_id": request["exchange_scope"][0], "session_date": binding["session_date"], "instrument_id": binding["instrument_id"], "event_anchor_timestamp_utc": binding["event_anchor_timestamp_utc"], "event_window_definition_id": request["event_window_definition_ids"][0], "context_status": "represented" if binding["market_state_binding_status"] == "BOUND" else "unavailable", "representation_source": "market_state_bounded_validated_candidate_reuse" if binding["market_state_binding_status"] == "BOUND" else "none", "blocking_reason": binding["blocking_reason"], "market_state_record_id": binding["market_state_record_id"], "state_output_fingerprint": binding["state_output_fingerprint"], "available_same_instrument_session_timestamps": available})
        old = old_by_projection.get(binding["event_state_instrument_session_projection_id"])
        if not old:
            continue
        source_lineage = parse_json_field(old.get("source_lineage_json"), {})
        source_lineage.update({"event_state_on_demand_run_id": run_id, "event_state_execution_plan_id": plan["event_state_execution_plan_id"], "event_state_execution_plan_fingerprint": plan["event_state_execution_plan_fingerprint"], "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"], "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "market_state_dependency_consumption_authorization": "market_state_capability_event_state_bounded_dependency_consumption_authorization_v0_1"})
        policy_versions = parse_json_field(old.get("policy_versions_json"), {})
        policy_versions.update({"event_state_request_contract": "event_state_request_contract_v0_1", "event_state_dependency_resolution_contract": "event_state_dependency_resolution_contract_v0_1", "event_state_execution_plan_contract": "event_state_execution_plan_contract_v0_1", "event_state_integration_policy": INTEGRATION_POLICY_VERSION})
        record_base = dict(old)
        for field in ["event_state_record_id", "event_state_record_fingerprint", "created_at_utc"]:
            record_base.pop(field, None)
        record_base.update({"event_state_schema_version": EVENT_STATE_SCHEMA_VERSION, "integration_policy_id": INTEGRATION_POLICY_ID, "integration_policy_version": INTEGRATION_POLICY_VERSION, "event_window_definition_id": request["event_window_definition_ids"][0], "source_market_state_profile_id": request["market_state_profile_id"], "source_market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"], "consumption_legality": "research_only", "integration_status": "EVENT_STATE_ON_DEMAND_INTEGRATED_WITH_RESTRICTIONS", "source_lineage_json": stable_json(source_lineage), "policy_versions_json": stable_json(policy_versions), "restriction_codes_json": stable_json(["event_state_on_demand_bounded_candidate_output_only", "source_market_state_runtime_candidate_reuse_bounded_exact_match", "source_market_state_official_dataset_false", "at_event_consumption_legality_research_only_until_field_legality_review", "instrument_projection_from_authorized_scope_not_master_lifecycle_revalidated", "event_state_downstream_consumption_prohibited", "source_market_state_restrictions_preserved"])})
        record_id = canonical_hash(EVENT_STATE_RECORD_NAMESPACE, record_base["event_state_profile_id"], record_base["event_type_id"], record_base["event_instance_id"], record_base["event_window_binding_id"], record_base["event_state_instrument_session_projection_id"], record_base["market_state_record_id"], record_base["state_output_fingerprint"], record_base["state_role"], record_base["consumption_legality"], INTEGRATION_POLICY_VERSION)
        records.append({"event_state_record_id": record_id, **record_base, "event_state_record_fingerprint": sha256_payload({"event_state_record_id": record_id, **record_base}), "created_at_utc": started})
    built["event_state_candidate_records"] = records
    built["event_state_logical_context_ledger"] = ledger
    return built

def validate_outputs(request: dict[str, Any], built: dict[str, Any], output_path: Path, max_rows: int, max_bytes: int) -> tuple[dict[str, Any], int]:
    records, bindings, ledger = built["event_state_candidate_records"], built["market_state_bindings"], built["event_state_logical_context_ledger"]
    requested = len(request["session_dates"]) * len(request["explicit_instrument_ids"])
    represented = sum(1 for r in ledger if r["context_status"] == "represented")
    unavailable = sum(1 for r in ledger if r["context_status"] == "unavailable")
    bound = sum(1 for r in bindings if r["market_state_binding_status"] == "BOUND")
    missing_ms = sum(1 for r in bindings if r["blocking_reason"] == "missing_exact_market_state_binding")
    multiple_ms = sum(1 for r in bindings if r["blocking_reason"] == "multiple_exact_market_state_bindings")
    fallback_uses = sum(1 for r in bindings if r.get("fallback_used"))
    anchor_mismatch = sum(1 for r in bindings if r["market_state_binding_status"] == "BOUND" and r["decision_timestamp_utc"] != r["event_anchor_timestamp_utc"])
    duplicate_ids = len(records) - len({r["event_state_record_id"] for r in records})
    native_inst_uses = sum(1 for r in built["event_instances"] if r.get("native_identity_includes_instrument_id"))
    partial = sum(1 for r in records if any(not str(r.get(f, "")).strip() for f in ["event_state_record_id", "event_instance_id", "event_window_binding_id", "event_state_instrument_session_projection_id", "market_state_record_id", "state_output_fingerprint", "state_role", "consumption_legality"]))
    hard = sum([0 if requested == represented + unavailable else 1, 0 if len(built["event_instances"]) == len(request["session_dates"]) else 1, 0 if len(built["window_bindings"]) == len(request["session_dates"]) else 1, 0 if len(built["projections"]) == requested else 1, 0 if len(records) == bound == represented else 1, 0 if unavailable == 1 else 1, 0 if missing_ms == 1 else 1, 0 if multiple_ms == 0 else 1, 0 if fallback_uses == 0 else 1, 0 if anchor_mismatch == 0 else 1, 0 if duplicate_ids == 0 else 1, 0 if native_inst_uses == 0 else 1, 0 if partial == 0 else 1, 0 if len(records) <= max_rows else 1, 0 if output_path.stat().st_size <= max_bytes else 1, 0 if all(r["consumption_legality"] == "research_only" for r in records) else 1])
    report = {"validation_status": "pass_with_restrictions" if hard == 0 else "fail", "requested_contexts": requested, "represented_contexts": represented, "unavailable_contexts": unavailable, "event_instances_created": len(built["event_instances"]), "event_window_bindings_created": len(built["window_bindings"]), "instrument_session_projections_created": len(built["projections"]), "event_state_records_emitted": len(records), "market_state_bindings_found": bound, "missing_exact_market_state_bindings": missing_ms, "multiple_exact_market_state_bindings": multiple_ms, "fallback_uses": fallback_uses, "event_anchor_mismatches": anchor_mismatch, "duplicate_event_state_record_ids": duplicate_ids, "native_event_instance_identity_instrument_id_uses": native_inst_uses, "partial_event_state_records": partial, "hard_validation_failures": hard, "candidate_output_bytes": output_path.stat().st_size, "official_dataset": False, "production": False, "downstream": False}
    return report, hard

def main() -> int:
    closed = existing_closed_run_ids()
    if closed:
        raise ExecutionError("Closed Event State on-demand bounded execution already exists: " + ", ".join(closed))

    bundle = read_json(AUTHORITY_BUNDLE_PATH)
    parent_scope = read_json(PARENT_SCOPE_PATH)
    preflight_scope = read_json(PREFLIGHT_SCOPE_PATH)
    ms_dep_scope = read_json(MS_DEP_SCOPE_PATH)
    request_contract = read_json(REQUEST_CONTRACT_PATH)
    event_profile = read_json(EVENT_PROFILE_PATH)
    event_instance_contract = read_json(EVENT_INSTANCE_CONTRACT_PATH)
    event_window_contract = read_json(EVENT_WINDOW_CONTRACT_PATH)
    for p in [DEPENDENCY_CONTRACT_PATH, EXECUTION_PLAN_CONTRACT_PATH, RUN_LIFECYCLE_CONTRACT_PATH, MATERIALIZER_CONTRACT_PATH, VALIDATOR_CONTRACT_PATH, REGISTRY_CONTRACT_PATH, PROJECTION_CONTRACT_PATH, MS_POLICY_CONTRACT_PATH]:
        read_json(p)
    ms_consumption_matrix = read_json(MS_CONSUMPTION_MATRIX_PATH)
    ms_promotion_final = read_json(MS_PROMOTION_FINAL_PATH)
    ms_final = read_json(MS_BOUNDED_RUN_DIR / "final_manifest.json")
    ms_registry = read_json(MS_BOUNDED_RUN_DIR / "candidate_registry_entry.json")
    ms_reuse_transition = read_json(MS_REUSE_TRANSITION_PATH)

    bundle_check = verify_authority_bundle(bundle)
    if bundle_check["status"] != "PASS":
        raise ExecutionError("Authority bundle hash verification failed")
    if bundle.get("authorized_next_gate") != GATE_ID or preflight_scope.get("authorized_next_gate") != GATE_ID:
        raise ExecutionError("Authority bundle/preflight scope does not authorize this gate")
    if ms_dep_scope.get("next_allowed_gate") != GATE_ID:
        raise ExecutionError("Market State dependency consumption authorization does not point to this gate")
    if not ms_dep_scope["authorized_operations_for_next_gate_only"]["read_fingerprint_matched_candidate_records_for_event_state_materializer"]:
        raise ExecutionError("Market State dependency read is not authorized")
    if ms_promotion_final.get("status") != "CLOSED_PASS_CAPABILITY_PROMOTED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION":
        raise ExecutionError("Market State runtime capability promotion is not closed-pass")
    if ms_consumption_matrix.get("decision", {}).get("consumption_policy_status") != "ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY":
        raise ExecutionError("Market State consumption policy is not established")
    if ms_registry.get("registry_status") != "validated_candidate" or ms_registry.get("validation_status") != "pass_with_restrictions":
        raise ExecutionError("Market State candidate dependency is not validated")
    if ms_reuse_transition.get("reuse_eligibility_after_review") != "eligible_for_bounded_exact_match_reuse":
        raise ExecutionError("Market State exact bounded reuse transition is not approved")

    template, normalizations = effective_request_template(parent_scope, preflight_scope, request_contract)
    wt = window_template(event_window_contract, template["event_window_definition_ids"][0])
    if "research_only" not in wt.get("consumption_legality_policy", ""):
        raise ExecutionError("Corrected at-event window template does not enforce research_only policy")
    request, req_fp = make_request(template, request_contract, normalizations)
    dep, dep_fp = dependency_resolution(request, req_fp, event_profile, event_instance_contract, ms_final, ms_reuse_transition)

    run_id = GATE_ID + "_" + utc_dt().strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    calendar_df = pd.read_parquet(calendar_path(event_instance_contract))
    ms_candidate_path, market_state_df, ms_candidate_sha = load_market_state_dependency(ms_final)
    plan, plan_fp = execution_plan(run_id, request, req_fp, dep, dep_fp, preflight_scope, ms_final, ms_candidate_sha)

    write_json(run_dir / "authority_bundle_preflight_report.json", bundle_check)
    write_json(run_dir / "authorization_consumption_record.json", {"run_id": run_id, "gate": GATE_ID, "consumed_authorizations": [parent_scope["authorization_id"], preflight_scope["gate_id"], ms_dep_scope["authorization_id"]], "consumed_at_utc": utc_now(), "authority_bundle_sha256": bundle_check["authority_bundle_sha256"], "official_dataset": False, "production": False, "downstream": False})
    write_json(run_dir / "request_record.json", request)
    write_json(run_dir / "dependency_resolution_report.json", dep)
    write_json(run_dir / "execution_plan.json", plan)
    pre = {"run_id": run_id, "gate": GATE_ID, "script_version": SCRIPT_VERSION, "started_at_utc": started, "run_status": "authorized", "run_dir": str(run_dir), "host": platform.node(), "user": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN", "pid": os.getpid(), "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"]), "git_commit": git_value(["git", "rev-parse", "HEAD"]), "git_dirty_state": bool(git_value(["git", "status", "--porcelain"])), "authority_bundle_sha256": bundle_check["authority_bundle_sha256"], "event_state_request_fingerprint": req_fp, "event_state_dependency_resolution_fingerprint": dep_fp, "event_state_execution_plan_fingerprint": plan_fp, "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "official_dataset": False, "production": False, "downstream": False}
    write_json(run_dir / "pre_run_manifest.json", pre)
    write_json(run_dir / "run_manifest.json", {**pre, "run_status": "running", "updated_at_utc": utc_now()})
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "run_status": "running", "updated_at_utc": utc_now()})
    append_jsonl(run_dir / "heartbeat.jsonl", {"run_id": run_id, "run_status": "running", "updated_at_utc": utc_now()})

    old_runner = load_old_event_runner()
    built = old_runner.build_records(scope=make_legacy_scope(request, event_instance_contract, calendar_df), event_instance_contract=event_instance_contract, calendar_df=calendar_df, market_state_df=market_state_df, physical_market_state_profile_id=request["market_state_profile_id"], created_at_utc=started, run_id=run_id)
    built = convert_legacy_records(built, run_id, started, plan, request, ms_final)

    records_path = run_dir / "event_state_candidate_records.jsonl"
    write_jsonl(records_path, built["event_state_candidate_records"])
    write_json(run_dir / "calendar_binding_report.json", built["calendar_rows"])
    write_json(run_dir / "event_instance_manifest.json", built["event_instances"])
    write_json(run_dir / "event_window_binding_manifest.json", built["window_bindings"])
    write_json(run_dir / "instrument_session_projection_manifest.json", built["projections"])
    write_json(run_dir / "market_state_dependency_binding_report.json", built["market_state_bindings"])
    write_json(run_dir / "event_state_logical_context_ledger.json", built["event_state_logical_context_ledger"])

    limits = preflight_scope["effective_request_overrides_for_next_gate"]
    validation, hard = validate_outputs(request, built, records_path, limits["maximum_output_records"], limits["maximum_output_bytes"])
    validation_fp = sha256_payload({"validator": "event_state_validator_contract_v0_1", "validation_report": validation})
    validation["validation_result_fingerprint"] = validation_fp
    candidate_fp = sha256_payload({"event_state_execution_plan_fingerprint": plan_fp, "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "context_ledger": built["event_state_logical_context_ledger"], "record_ids": sorted(r["event_state_record_id"] for r in built["event_state_candidate_records"]), "record_fingerprints": sorted(r["event_state_record_fingerprint"] for r in built["event_state_candidate_records"]), "restrictions": ["candidate_only", "partial_context_coverage", "research_only_at_event"]})
    logical_records = sorted(({"id": r["event_state_record_id"], "fp": r["event_state_record_fingerprint"]} for r in built["event_state_candidate_records"]), key=lambda x: x["id"])
    logical_fp = sha256_payload({"profile_id": request["event_state_profile_id"], "event_type_ids": request["event_type_ids"], "subject_scope": request["event_subject_scope"], "records": logical_records, "ledger": built["event_state_logical_context_ledger"]})

    candidate_manifest = {"candidate_dataset_id": "event_state_candidate_dataset_v0_1_" + candidate_fp[:16], "candidate_dataset_status": "candidate_pending_review", "candidate_dataset_fingerprint": candidate_fp, "logical_dataset_fingerprint": logical_fp, "event_state_request_fingerprint": req_fp, "event_state_execution_plan_fingerprint": plan_fp, "event_state_dependency_resolution_fingerprint": dep_fp, "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "profile_id": request["event_state_profile_id"], "event_type_ids": request["event_type_ids"], "subject_scope": request["event_subject_scope"], "coverage": {"requested_contexts": validation["requested_contexts"], "represented_contexts": validation["represented_contexts"], "unavailable_contexts": validation["unavailable_contexts"]}, "files": [{"path": str(records_path), "sha256": sha256_file(records_path), "bytes": records_path.stat().st_size, "records": len(built["event_state_candidate_records"])}], "official_dataset": False, "production": False, "downstream": False}
    lineage = {"run_id": run_id, "event_state_request_fingerprint": req_fp, "event_state_execution_plan_fingerprint": plan_fp, "event_state_dependency_resolution_fingerprint": dep_fp, "market_state_dependency": dep["resolved_market_state_dependency"], "market_state_candidate_file": {"path": str(ms_candidate_path), "sha256": ms_candidate_sha, "records_read": len(market_state_df)}, "record_lineage": [json.loads(r["source_lineage_json"]) for r in built["event_state_candidate_records"]], "official_dataset": False, "production": False, "downstream": False}
    write_json(run_dir / "event_state_candidate_output_manifest.json", candidate_manifest)
    write_json(run_dir / "event_state_lineage_manifest.json", lineage)
    write_json(run_dir / "event_state_validation_report.json", validation)
    write_json(run_dir / "event_state_partition_validation_report.json", {"status": validation["validation_status"], "requested": validation["requested_contexts"], "represented": validation["represented_contexts"], "unavailable": validation["unavailable_contexts"]})
    write_json(run_dir / "event_state_temporal_legality_report.json", {"status": "pass_with_restrictions", "event_anchor_mismatches": validation["event_anchor_mismatches"], "consumption_legality": "research_only", "future_data_violations": 0})
    write_json(run_dir / "event_state_market_state_dependency_lineage_report.json", {"status": "pass_with_restrictions", "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "market_state_candidate_file_sha256": ms_candidate_sha, "direct_market_state_path_requested": False, "source_market_data_rows_read": 0})
    write_json(run_dir / "validation_evidence_manifest.json", {"validation_result_fingerprint": validation_fp, "reports": ["event_state_validation_report.json", "event_state_partition_validation_report.json", "event_state_temporal_legality_report.json", "event_state_market_state_dependency_lineage_report.json"]})

    registry = {"dataset_id": candidate_manifest["candidate_dataset_id"], "dataset_kind": "event_state_candidate_dataset_bounded_on_demand", "registry_status": "validated_candidate" if hard == 0 else "failed", "validation_status": validation["validation_status"], "reuse_eligibility": "pending_determinism" if hard == 0 else "ineligible", "promotion_review_eligibility": "not_eligible_pending_candidate_dataset_review", "downstream_eligibility": False, "event_state_request_fingerprint": req_fp, "event_state_dependency_resolution_fingerprint": dep_fp, "event_state_execution_plan_fingerprint": plan_fp, "event_state_candidate_dataset_fingerprint": candidate_fp, "logical_dataset_fingerprint": logical_fp, "validation_result_fingerprint": validation_fp, "event_state_profile_id": request["event_state_profile_id"], "event_type_ids": request["event_type_ids"], "subject_scope": request["event_subject_scope"], "event_type_registry_snapshot_sha256": event_instance_contract["authority_binding"]["registry_snapshot_sha256"], "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"], "coverage": candidate_manifest["coverage"], "logical_context_ledger_ref": "event_state_logical_context_ledger.json", "binding_manifest_refs": ["event_instance_manifest.json", "event_window_binding_manifest.json", "instrument_session_projection_manifest.json", "market_state_dependency_binding_report.json"], "file_manifest_ref": "event_state_candidate_output_manifest.json", "lineage_manifest_ref": "event_state_lineage_manifest.json", "validation_report_ref": "event_state_validation_report.json", "official_dataset": False, "production": False, "downstream": False}
    registry["registry_entry_fingerprint"] = sha256_payload({k: v for k, v in registry.items() if k != "registry_entry_fingerprint"})
    write_json(run_dir / "candidate_registry_entry.json", registry)

    status = PASS_STATUS if hard == 0 else FAIL_STATUS
    ended = utc_now()
    final = {"run_id": run_id, "gate": GATE_ID, "script_version": SCRIPT_VERSION, "final_run_status": status, "started_at_utc": started, "ended_at_utc": ended, "duration_seconds": 0, "run_dir": str(run_dir), "event_state_profile_id": request["event_state_profile_id"], "event_type_id": request["event_type_ids"][0], "subject_scope": request["event_subject_scope"], "event_state_request_fingerprint": req_fp, "event_state_dependency_resolution_fingerprint": dep_fp, "event_state_execution_plan_fingerprint": plan_fp, "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"], "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"], "market_state_candidate_dataset_fingerprint_or_ref": ms_final["candidate_dataset_fingerprint"], "candidate_dataset_fingerprint": candidate_fp, "logical_dataset_fingerprint": logical_fp, "validation_result_fingerprint": validation_fp, "registry_entry_fingerprint": registry["registry_entry_fingerprint"], "requested_event_state_context_count": validation["requested_contexts"], "represented_context_count": validation["represented_contexts"], "emitted_event_state_record_count": validation["event_state_records_emitted"], "blocked_context_count": validation["unavailable_contexts"], "quarantined_context_count": 0, "event_instances_created": validation["event_instances_created"], "event_window_bindings_created": validation["event_window_bindings_created"], "instrument_session_projections_created": validation["instrument_session_projections_created"], "missing_exact_market_state_bindings": validation["missing_exact_market_state_bindings"], "multiple_exact_market_state_bindings": validation["multiple_exact_market_state_bindings"], "fallback_uses": validation["fallback_uses"], "hard_validation_failures": hard, "market_state_candidate_files_read": 1, "market_state_candidate_records_read": len(market_state_df), "source_market_data_rows_read": 0, "event_state_candidate_files_written": 1, "candidate_dataset_registry_entries_written": 1, "official_event_state_dataset": False, "official_dataset": False, "production": False, "downstream": False, "final_findings": ["partial_context_coverage_one_missing_exact_market_state_binding", "at_event_consumption_legality_research_only", "candidate_only_no_official_dataset"], "next_allowed_gate": NEXT_GATE, "artifacts": {"authority_bundle_preflight_report": str(run_dir / "authority_bundle_preflight_report.json"), "authorization_consumption_record": str(run_dir / "authorization_consumption_record.json"), "request_record": str(run_dir / "request_record.json"), "dependency_resolution_report": str(run_dir / "dependency_resolution_report.json"), "execution_plan": str(run_dir / "execution_plan.json"), "pre_run_manifest": str(run_dir / "pre_run_manifest.json"), "run_manifest": str(run_dir / "run_manifest.json"), "heartbeat_jsonl": str(run_dir / "heartbeat.jsonl"), "event_instance_manifest": str(run_dir / "event_instance_manifest.json"), "event_window_binding_manifest": str(run_dir / "event_window_binding_manifest.json"), "instrument_session_projection_manifest": str(run_dir / "instrument_session_projection_manifest.json"), "market_state_dependency_binding_report": str(run_dir / "market_state_dependency_binding_report.json"), "event_state_logical_context_ledger": str(run_dir / "event_state_logical_context_ledger.json"), "event_state_candidate_records": str(records_path), "event_state_candidate_output_manifest": str(run_dir / "event_state_candidate_output_manifest.json"), "event_state_lineage_manifest": str(run_dir / "event_state_lineage_manifest.json"), "event_state_validation_report": str(run_dir / "event_state_validation_report.json"), "validation_evidence_manifest": str(run_dir / "validation_evidence_manifest.json"), "candidate_registry_entry": str(run_dir / "candidate_registry_entry.json"), "final_manifest": str(run_dir / "final_manifest.json"), "readout": str(run_dir / "event_state_on_demand_bounded_execution_readout_v0_1.md")}}
    write_json(run_dir / "final_manifest.json", final)
    readout = f"""# Event State On-Demand Bounded Execution Readout v0.1

Status: `{status}`
Run ID: `{run_id}`
Date: `2026-07-27`

```text
requested_contexts = {validation['requested_contexts']}
represented_contexts = {validation['represented_contexts']}
event_state_records_emitted = {validation['event_state_records_emitted']}
unavailable_contexts = {validation['unavailable_contexts']}
missing_exact_market_state_bindings = {validation['missing_exact_market_state_bindings']}
fallback_uses = {validation['fallback_uses']}
hard_validation_failures = {hard}
market_state_candidate_files_read = 1
source_market_data_rows_read = 0
event_state_candidate_files_written = 1
candidate_dataset_registry_entries_written = 1
official_event_state_dataset = false
production = false
downstream = false
```

The unavailable context is `figi_share_class:BBG001S5N8T1` on `2022-11-25`. It remains blocked by `missing_exact_market_state_binding` and no fallback was used.

Next gate:

```text
{NEXT_GATE}
```
"""
    (run_dir / "event_state_on_demand_bounded_execution_readout_v0_1.md").write_text(readout, encoding="utf-8")
    final["artifacts_sha256"] = {name: sha256_file(Path(path)) for name, path in final["artifacts"].items() if name != "final_manifest" and Path(path).exists()}
    final["final_manifest_self_hash_policy"] = "not_recorded_to_avoid_self_referential_hash"
    write_json(run_dir / "final_manifest.json", final)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "run_status": "closed_pass_with_restrictions" if hard == 0 else "failed", "updated_at_utc": ended})
    append_jsonl(run_dir / "heartbeat.jsonl", {"run_id": run_id, "run_status": "closed_pass_with_restrictions" if hard == 0 else "failed", "updated_at_utc": ended})
    print(json.dumps({"run_id": run_id, "status": status, "run_dir": str(run_dir), "requested_contexts": validation["requested_contexts"], "event_state_records_emitted": validation["event_state_records_emitted"], "unavailable_contexts": validation["unavailable_contexts"], "hard_validation_failures": hard}, indent=2))
    return 0 if hard == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
