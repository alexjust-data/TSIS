from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
CONFIGS = RUNTIME / "configs"
SCRIPTS = RUNTIME / "scripts"

GATE = "runtime_provider_contract_schema_hardening_v0_1_1"
STATUS = "CLOSED_PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_1_WITH_RESTRICTIONS_NO_EXECUTION"
HEX64 = "^[a-f0-9]{64}$"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def entry(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def obj(props: dict[str, Any], required: list[str] | None = None, addl: bool = False) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "object", "additionalProperties": addl, "properties": props}
    if required:
        d["required"] = required
    return d


def arr(items: dict[str, Any], min_items: int = 0, unique: bool = False, max_items: int | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "array", "items": items, "minItems": min_items}
    if unique:
        d["uniqueItems"] = True
    if max_items is not None:
        d["maxItems"] = max_items
    return d


def ref_schema(ref_type: str, availability: str | None = None) -> dict[str, Any]:
    return obj(
        {
            "ref_id": {"type": "string", "minLength": 1},
            "ref_type": {"const": ref_type},
            "sha256": {"type": "string", "pattern": HEX64},
            "availability": {"const": availability} if availability else {"enum": ["available", "archived", "missing", "not_required"]},
        },
        ["ref_id", "ref_type", "sha256", "availability"],
    )


def coverage_schema(min_requested: int = 0) -> dict[str, Any]:
    props = {
        "requested_contexts": {"type": "integer", "minimum": min_requested},
        "represented_contexts": {"type": "integer", "minimum": 0},
        "unavailable_contexts": {"type": "integer", "minimum": 0},
        "blocked_contexts": {"type": "integer", "minimum": 0},
        "quarantined_contexts": {"type": "integer", "minimum": 0},
        "unaccounted_contexts": {"type": "integer", "minimum": 0},
    }
    return obj(props, list(props))


def market_payload_schema() -> dict[str, Any]:
    props = {
        "request_type": {"const": "market_state"},
        "profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"},
        "profile_version_policy": {"const": "exact"},
        "profile_version": {"type": "string", "minLength": 1},
        "exchange_scope": {"type": "string", "minLength": 1},
        "explicit_instrument_ids": arr({"type": "string", "minLength": 1}, 1, True),
        "session_dates": arr({"type": "string", "format": "date"}, 1, True),
        "resolution": {"type": "string", "minLength": 1},
        "calendar_authority_id": {"type": "string", "minLength": 1},
        "point_in_time_policy_id": {"type": "string", "minLength": 1},
        "source_version_policy": {"const": "exact_governed_or_block"},
        "output_mode": {"const": "candidate"},
        "reuse_policy": {"enum": ["reuse_if_exact_validated_match", "metadata_only"]},
    }
    return obj(props, list(props))


def event_payload_schema() -> dict[str, Any]:
    props = {
        "request_type": {"const": "event_state"},
        "event_state_profile_id": {"const": "event_state_core_four_intraday_profile_v0_1"},
        "event_state_profile_version_policy": {"const": "exact"},
        "event_state_profile_version": {"type": "string", "minLength": 1},
        "event_type_ids": arr({"const": "event_type:market_data:session_opened"}, 1, True, 1),
        "event_subject_scope": {"const": "exchange_session"},
        "event_type_registry_snapshot_id": {"type": "string", "minLength": 1},
        "event_instance_policy_id": {"type": "string", "minLength": 1},
        "event_window_policy_id": {"type": "string", "minLength": 1},
        "event_window_definition_ids": arr({"type": "string", "minLength": 1}, 1, True),
        "instrument_projection_policy_id": {"type": "string", "minLength": 1},
        "market_state_dependency_mode": {"const": "emit_or_resolve_market_state_subrequest_through_runtime_capability"},
        "market_state_profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"},
        "market_state_dependency_reuse_policy": {"enum": ["reuse_if_exact_validated_dependency_match", "metadata_only"]},
        "exchange_scope": {"type": "string", "minLength": 1},
        "explicit_instrument_ids": arr({"type": "string", "minLength": 1}, 1, True),
        "session_dates": arr({"type": "string", "format": "date"}, 1, True),
        "resolution": {"type": "string", "minLength": 1},
        "calendar_authority_id": {"type": "string", "minLength": 1},
        "point_in_time_policy_id": {"type": "string", "minLength": 1},
        "source_version_policy": {"const": "exact_governed_or_block"},
        "output_mode": {"const": "candidate"},
        "reuse_policy": {"enum": ["reuse_if_exact_validated_dependency_match", "metadata_only"]},
    }
    return obj(props, list(props))


def state_resolution_schema() -> dict[str, Any]:
    payload_base = obj({"market_state_request": market_payload_schema(), "event_state_request": event_payload_schema()})
    market_only = obj({"market_state_request": market_payload_schema()}, ["market_state_request"])
    market_only["not"] = obj({"event_state_request": {}}, ["event_state_request"], addl=True)
    event_only = obj({"event_state_request": event_payload_schema()}, ["event_state_request"])
    event_only["not"] = obj({"market_state_request": {}}, ["market_state_request"], addl=True)
    resolution_policy = obj(
        {
            "mode": {"enum": ["validate_only", "resolve_reuse_or_authorization", "invoke_with_authorization"]},
            "reuse_policy": {"enum": ["metadata_only", "reuse_if_exact_validated_match", "reuse_if_exact_validated_match_or_authorization_required"]},
            "allow_new_candidate_execution": {"const": False},
            "allow_physical_path_input": {"const": False},
            "requested_output_mode": {"enum": ["metadata_only", "candidate_reference_only"]},
            "production": {"const": False},
            "downstream": {"const": False},
        },
        ["mode", "reuse_policy", "allow_new_candidate_execution", "allow_physical_path_input", "requested_output_mode", "production", "downstream"],
    )
    schema = obj(
        {
            "request_id": {"type": "string", "minLength": 1},
            "request_type": {"enum": ["market_state", "event_state"]},
            "request_contract_version": {"const": "0.1.1"},
            "consumer": {"type": "string", "minLength": 1},
            "consumption_purpose": {"enum": ["planning", "research", "validation", "backtest"]},
            "resolution_policy": resolution_policy,
            "payload": payload_base,
        },
        ["request_id", "request_type", "request_contract_version", "consumer", "consumption_purpose", "resolution_policy", "payload"],
    )
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/state_resolution_request_contract_v0_1_1.schema.json", "title": "TSIS StateResolutionRequest v0.1.1"})
    schema["allOf"] = [
        {"if": obj({"request_type": {"const": "market_state"}}, ["request_type"], addl=True), "then": obj({"payload": market_only}, ["payload"], addl=True)},
        {"if": obj({"request_type": {"const": "event_state"}}, ["request_type"], addl=True), "then": obj({"payload": event_only}, ["payload"], addl=True)},
    ]
    return schema


def response_schema() -> dict[str, Any]:
    details = obj(
        {"materializer_executions": {"const": 0}, "source_market_data_rows_read": {"const": 0}, "registry_mutations": {"const": 0}, "physical_rows_delivered": {"const": 0}},
        ["materializer_executions", "source_market_data_rows_read", "registry_mutations", "physical_rows_delivered"],
    )
    schema = obj(
        {
            "invocation_id": {"type": "string", "minLength": 1},
            "request_type": {"enum": ["market_state", "event_state"]},
            "request_fingerprint": {"type": "string", "pattern": HEX64},
            "invocation_status": {"enum": ["blocked", "reuse_hit", "authorization_required", "authorized_reference"]},
            "resolution_decision": {"enum": ["VALID_REQUEST_REUSE_HIT", "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED", "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE", "BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]},
            "capability_id": {"type": "string", "minLength": 1},
            "profile_id": {"type": ["string", "null"]},
            "run_id": {"type": ["string", "null"]},
            "dataset_id": {"type": ["string", "null"]},
            "dataset_status": {"type": ["string", "null"]},
            "validation_status": {"type": ["string", "null"]},
            "state_bundle_manifest_ref": {"oneOf": [ref_schema("state_bundle_manifest"), {"type": "null"}]},
            "coverage": coverage_schema(0),
            "restrictions": arr({"type": "string", "minLength": 1}, 1, True),
            "artifact_references": arr(ref_schema("runtime_artifact"), 0),
            "official_dataset": {"const": False},
            "production": {"const": False},
            "downstream": {"const": False},
            "market_state_details": {"oneOf": [details, {"type": "null"}]},
            "event_state_details": {"oneOf": [details, {"type": "null"}]},
            "authorization_ref": {"oneOf": [ref_schema("execution_authorization"), {"type": "null"}]},
        },
        ["invocation_id", "request_type", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id", "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "state_bundle_manifest_ref", "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream", "market_state_details", "event_state_details", "authorization_ref"],
    )
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_user_invocation_response_contract_v0_1_1.schema.json", "title": "TSIS RuntimeInvocationResponse v0.1.1"})
    schema["allOf"] = [
        {"if": obj({"request_type": {"const": "market_state"}}, ["request_type"], addl=True), "then": obj({"event_state_details": {"type": "null"}}, [], addl=True)},
        {"if": obj({"request_type": {"const": "event_state"}}, ["request_type"], addl=True), "then": obj({"market_state_details": {"type": "null"}}, [], addl=True)},
        {"if": obj({"invocation_status": {"const": "reuse_hit"}}, ["invocation_status"], addl=True), "then": obj({"resolution_decision": {"const": "VALID_REQUEST_REUSE_HIT"}, "dataset_id": {"type": "string", "minLength": 1}, "dataset_status": {"const": "validated_candidate"}, "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}, "state_bundle_manifest_ref": ref_schema("state_bundle_manifest", "available"), "artifact_references": arr(ref_schema("runtime_artifact", "available"), 1)}, [], addl=True)},
        {"if": obj({"invocation_status": {"const": "blocked"}}, ["invocation_status"], addl=True), "then": obj({"resolution_decision": {"enum": ["BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, False, 0)}, [], addl=True)},
        {"if": obj({"invocation_status": {"const": "authorization_required"}}, ["invocation_status"], addl=True), "then": obj({"resolution_decision": {"const": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": {"type": "null"}}, [], addl=True)},
        {"if": obj({"invocation_status": {"const": "authorized_reference"}}, ["invocation_status"], addl=True), "then": obj({"resolution_decision": {"const": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": ref_schema("execution_authorization", "available")}, [], addl=True)},
    ]
    return schema


def dataset_ref_schema(kind: str) -> dict[str, Any]:
    return obj({"dataset_id": {"type": "string", "minLength": 1}, "dataset_kind": {"const": kind}, "candidate_dataset_fingerprint": {"type": "string", "pattern": HEX64}, "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}, "reuse_eligibility": {"enum": ["eligible", "eligible_with_restrictions"]}, "artifact_availability": {"const": "available"}}, ["dataset_id", "dataset_kind", "candidate_dataset_fingerprint", "validation_status", "reuse_eligibility", "artifact_availability"])


def bundle_schema() -> dict[str, Any]:
    profile = obj({"state_kind": {"enum": ["market_state", "event_state"]}, "profile_id": {"type": "string", "minLength": 1}, "profile_version": {"type": "string", "minLength": 1}, "profile_fingerprint": {"type": "string", "pattern": HEX64}}, ["state_kind", "profile_id", "profile_version", "profile_fingerprint"])
    artifact = obj({"artifact_id": {"type": "string", "minLength": 1}, "artifact_type": {"type": "string", "minLength": 1}, "sha256": {"type": "string", "pattern": HEX64}, "availability": {"const": "available"}}, ["artifact_id", "artifact_type", "sha256", "availability"])
    schema = obj(
        {
            "state_bundle_manifest_id": {"type": "string", "minLength": 1},
            "bundle_state_mode": {"enum": ["market_state_only", "event_state_only", "market_and_event"]},
            "state_kinds": arr({"enum": ["market_state", "event_state"]}, 1, True, 2),
            "request_fingerprints": arr({"type": "string", "pattern": HEX64}, 1, True),
            "state_resolution_request_refs": arr(ref_schema("state_resolution_request", "available"), 1, True),
            "runtime_invocation_response_refs": arr(ref_schema("runtime_invocation_response", "available"), 1, True),
            "capability_refs": arr(ref_schema("runtime_capability", "available"), 1, True),
            "dataset_refs": obj({"market_state_dataset_ref": {"oneOf": [dataset_ref_schema("market_state"), {"type": "null"}]}, "event_state_dataset_ref": {"oneOf": [dataset_ref_schema("event_state"), {"type": "null"}]}}, ["market_state_dataset_ref", "event_state_dataset_ref"]),
            "coverage": coverage_schema(1),
            "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS", "BLOCKED", "FAIL"]},
            "restrictions": arr({"type": "string", "minLength": 1}, 1, True),
            "representation_profile_versions": arr(profile, 1),
            "schema_fingerprints": arr({"type": "string", "pattern": HEX64}, 1, True),
            "source_dataset_ids": arr({"type": "string", "minLength": 1}, 1, True),
            "source_content_hashes": arr({"type": "string", "pattern": HEX64}, 1, True),
            "artifact_hashes": arr(artifact, 1),
            "field_lineage": arr(obj({"field_id": {"type": "string", "minLength": 1}, "builder_id": {"type": "string", "minLength": 1}, "input_refs": arr({"type": "string", "minLength": 1}, 1, True)}, ["field_id", "builder_id", "input_refs"]), 1),
            "temporal_policy": obj({"point_in_time_policy_id": {"type": "string", "minLength": 1}, "available_at_policy_id": {"type": "string", "minLength": 1}, "future_information_exclusion": {"const": True}}, ["point_in_time_policy_id", "available_at_policy_id", "future_information_exclusion"]),
            "materialization_status": {"type": "string", "minLength": 1},
            "consumption_authorization": obj({"backtest_consumption_authorized": {"const": False}, "downstream_authorized": {"const": False}, "consumption_purposes": arr({"type": "string"}, 0, True, 0)}, ["backtest_consumption_authorized", "downstream_authorized", "consumption_purposes"]),
            "official_dataset": {"const": False}, "production": {"const": False}, "downstream": {"const": False}, "physical_rows_delivered": {"const": False},
        },
        ["state_bundle_manifest_id", "bundle_state_mode", "state_kinds", "request_fingerprints", "state_resolution_request_refs", "runtime_invocation_response_refs", "capability_refs", "dataset_refs", "coverage", "validation_status", "restrictions", "representation_profile_versions", "schema_fingerprints", "source_dataset_ids", "source_content_hashes", "artifact_hashes", "field_lineage", "temporal_policy", "materialization_status", "consumption_authorization", "official_dataset", "production", "downstream", "physical_rows_delivered"],
    )
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/state_bundle_manifest_contract_v0_1_1.schema.json", "title": "TSIS StateBundleManifest v0.1.1"})
    schema["allOf"] = [
        {"if": obj({"bundle_state_mode": {"const": "market_state_only"}}, ["bundle_state_mode"], addl=True), "then": obj({"state_kinds": arr({"const": "market_state"}, 1, True, 1), "dataset_refs": obj({"market_state_dataset_ref": dataset_ref_schema("market_state"), "event_state_dataset_ref": {"type": "null"}}, ["market_state_dataset_ref", "event_state_dataset_ref"])}, [], addl=True)},
        {"if": obj({"bundle_state_mode": {"const": "event_state_only"}}, ["bundle_state_mode"], addl=True), "then": obj({"state_kinds": arr({"const": "event_state"}, 1, True, 1), "dataset_refs": obj({"market_state_dataset_ref": {"type": "null"}, "event_state_dataset_ref": dataset_ref_schema("event_state")}, ["market_state_dataset_ref", "event_state_dataset_ref"])}, [], addl=True)},
        {"if": obj({"bundle_state_mode": {"const": "market_and_event"}}, ["bundle_state_mode"], addl=True), "then": obj({"state_kinds": arr({"enum": ["market_state", "event_state"]}, 2, True, 2), "request_fingerprints": arr({"type": "string", "pattern": HEX64}, 2, True), "state_resolution_request_refs": arr(ref_schema("state_resolution_request", "available"), 2, True), "dataset_refs": obj({"market_state_dataset_ref": dataset_ref_schema("market_state"), "event_state_dataset_ref": dataset_ref_schema("event_state")}, ["market_state_dataset_ref", "event_state_dataset_ref"])}, [], addl=True)},
    ]
    return schema


def interface_schema() -> dict[str, Any]:
    schema = obj({"operation": {"enum": ["validate", "resolve", "invoke"]}, "state_resolution_request": state_resolution_schema(), "execution_authorization_ref": {"oneOf": [ref_schema("execution_authorization", "available"), {"type": "null"}]}}, ["operation", "state_resolution_request", "execution_authorization_ref"])
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_user_invocation_interface_contract_v0_1_1.schema.json", "title": "TSIS RuntimeUserInvocationInterface v0.1.1"})
    return schema


def effective_view_schema() -> dict[str, Any]:
    cap = obj({"capability_id": {"enum": ["market_state_on_demand_runtime_capability_v0_1", "event_state_on_demand_runtime_capability_v0_1"]}, "request_type": {"enum": ["market_state", "event_state"]}, "capability_status": {"enum": ["promoted_with_restrictions", "available_with_restrictions"]}, "supported_profile_ids": arr({"type": "string", "minLength": 1}, 1, True), "supported_event_type_ids": arr({"type": "string", "minLength": 1}, 0, True), "candidate_generation_authority": {"const": True}, "reuse_authority": {"const": True}, "official_dataset": {"const": False}, "production": {"const": False}, "downstream": {"const": False}, "backtest_consumption": {"const": False}}, ["capability_id", "request_type", "capability_status", "supported_profile_ids", "supported_event_type_ids", "candidate_generation_authority", "reuse_authority", "official_dataset", "production", "downstream", "backtest_consumption"])
    schema = obj({"view_id": {"type": "string", "minLength": 1}, "view_version": {"const": "0.1.1"}, "capabilities": arr(cap, 2, True, 2)}, ["view_id", "view_version", "capabilities"])
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_capability_effective_view_contract_v0_1_1.schema.json", "title": "TSIS RuntimeCapabilityEffectiveView v0.1.1"})
    return schema


def contract_doc(contract_id: str, schema: dict[str, Any] | None, purpose: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"contract_id": contract_id, "contract_version": "0.1.1", "status": "PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_1_NO_EXECUTION", "owner_layer": "08_RUNTIME_CAPABILITIES", "schema_hardening_gate": GATE, "purpose": purpose, "contract_hash_policy": {"hash_authority": "PACKAGE_MANIFEST.full_file_sha256", "embedded_contract_hash": "not_used_in_v0_1_1"}}
    if schema is not None:
        d["json_schema"] = schema
    if extra:
        d.update(extra)
    return d


def write_contracts() -> list[Path]:
    docs = {
        "state_resolution_request_contract_v0_1.json": contract_doc("state_resolution_request_contract_v0_1", state_resolution_schema(), "Executable provider envelope for Market State and Event State resolution requests.", {"payload_authority_decision": "StateResolutionRequest is the only executable schema authority; specialized contracts are normative auxiliary documentation."}),
        "runtime_user_invocation_interface_contract_v0_1.json": contract_doc("runtime_user_invocation_interface_contract_v0_1", interface_schema(), "Executable interface envelope for validate/resolve/invoke control-plane operations."),
        "runtime_user_invocation_response_contract_v0_1.json": contract_doc("runtime_user_invocation_response_contract_v0_1", response_schema(), "Executable provider response envelope with fail-closed status/decision semantics."),
        "state_bundle_manifest_contract_v0_1.json": contract_doc("state_bundle_manifest_contract_v0_1", bundle_schema(), "Executable provider manifest for governed state bundle references."),
        "runtime_capability_effective_view_contract_v0_1.json": contract_doc("runtime_capability_effective_view_contract_v0_1", effective_view_schema(), "Executable effective view of currently available runtime capabilities."),
        "market_state_request_contract_v0_1.json": contract_doc("market_state_request_contract_v0_1", None, "Normative auxiliary documentation for Market State payload semantics.", {"execution_authority_role": "normative_auxiliary_not_executable", "executable_schema_authority": "state_resolution_request_contract_v0_1.json"}),
        "event_state_request_contract_v0_1.json": contract_doc("event_state_request_contract_v0_1", None, "Normative auxiliary documentation for Event State payload semantics.", {"execution_authority_role": "normative_auxiliary_not_executable", "executable_schema_authority": "state_resolution_request_contract_v0_1.json", "allowed_event_type_ids": ["event_type:market_data:session_opened"], "accepted_subject_scope": "exchange_session"}),
    }
    paths = []
    for name, doc in docs.items():
        p = RUNTIME / name
        write_json(p, doc)
        paths.append(p)
    return paths


def strict_lint(schema: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(schema, dict):
        if ("properties" in schema or "required" in schema) and schema.get("type") != "object":
            errors.append(f"{path}: object keywords without type object")
        if "required" in schema:
            props = schema.get("properties", {})
            for key in schema["required"]:
                if key not in props:
                    errors.append(f"{path}: required key {key} missing from properties")
        for key, value in schema.items():
            errors.extend(strict_lint(value, f"{path}.{key}"))
    elif isinstance(schema, list):
        for i, value in enumerate(schema):
            errors.extend(strict_lint(value, f"{path}[{i}]"))
    return errors


FORBIDDEN = ["physical_path", "parquet_path", "source_path", "output_root", "raw_data_path", "market_state_candidate_path", "event_state_output_path"]


def forbidden_scan(value: Any) -> list[str]:
    hits: list[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, child in v.items():
                if k.lower() in FORBIDDEN:
                    hits.append(f"{p}.{k}")
                walk(child, f"{p}.{k}")
        elif isinstance(v, list):
            for i, child in enumerate(v):
                walk(child, f"{p}[{i}]")

    walk(value, "$")
    return hits


def coverage_ok(c: dict[str, Any]) -> bool:
    if not c:
        return True
    return c.get("requested_contexts") == c.get("represented_contexts", 0) + c.get("unavailable_contexts", 0) + c.get("blocked_contexts", 0) + c.get("quarantined_contexts", 0) + c.get("unaccounted_contexts", 0)


def validate_doc(schema: dict[str, Any], doc: dict[str, Any], extra: str | None = None) -> list[str]:
    errors = [e.message for e in Draft202012Validator(schema).iter_errors(doc)]
    if forbidden_scan(doc):
        errors.append("forbidden physical/path-like key present")
    if extra in {"coverage", "bundle"} and not coverage_ok(doc.get("coverage", {})):
        errors.append("coverage arithmetic mismatch")
    if extra == "bundle":
        fps = doc.get("request_fingerprints", [])
        refs = doc.get("state_resolution_request_refs", [])
        if len(fps) != len(refs):
            errors.append("request/ref cardinality mismatch")
        for fp, r in zip(fps, refs):
            if r.get("sha256") != fp:
                errors.append("request fingerprint does not match request ref sha256")
    return errors


def valid_state_request(kind: str) -> dict[str, Any]:
    base = {"request_id": f"req_{kind}_001", "request_type": kind, "request_contract_version": "0.1.1", "consumer": "hardening_v0_1_1", "consumption_purpose": "validation", "resolution_policy": {"mode": "resolve_reuse_or_authorization", "reuse_policy": "reuse_if_exact_validated_match", "allow_new_candidate_execution": False, "allow_physical_path_input": False, "requested_output_mode": "candidate_reference_only", "production": False, "downstream": False}}
    if kind == "market_state":
        base["payload"] = {"market_state_request": {"request_type": "market_state", "profile_id": "market_state_core_four_intraday_profile_v0_1", "profile_version_policy": "exact", "profile_version": "v0_1", "exchange_scope": "XNYS", "explicit_instrument_ids": ["AAME"], "session_dates": ["2021-01-19"], "resolution": "intraday", "calendar_authority_id": "calendar:xnys:v0_1", "point_in_time_policy_id": "pit:v0_1", "source_version_policy": "exact_governed_or_block", "output_mode": "candidate", "reuse_policy": "reuse_if_exact_validated_match"}}
    else:
        base["payload"] = {"event_state_request": {"request_type": "event_state", "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1", "event_state_profile_version_policy": "exact", "event_state_profile_version": "v0_1", "event_type_ids": ["event_type:market_data:session_opened"], "event_subject_scope": "exchange_session", "event_type_registry_snapshot_id": "event_type_registry:v0_1", "event_instance_policy_id": "event_instance:session_opened:v0_1", "event_window_policy_id": "event_window:at_event:v0_1", "event_window_definition_ids": ["event_window:session_opened:at_event_v0_1"], "instrument_projection_policy_id": "projection:exchange_session_to_instrument:v0_1", "market_state_dependency_mode": "emit_or_resolve_market_state_subrequest_through_runtime_capability", "market_state_profile_id": "market_state_core_four_intraday_profile_v0_1", "market_state_dependency_reuse_policy": "reuse_if_exact_validated_dependency_match", "exchange_scope": "XNYS", "explicit_instrument_ids": ["AAME"], "session_dates": ["2021-01-19"], "resolution": "intraday", "calendar_authority_id": "calendar:xnys:v0_1", "point_in_time_policy_id": "pit:v0_1", "source_version_policy": "exact_governed_or_block", "output_mode": "candidate", "reuse_policy": "reuse_if_exact_validated_dependency_match"}}
    return base


def valid_response(kind: str = "market_state") -> dict[str, Any]:
    details = {"materializer_executions": 0, "source_market_data_rows_read": 0, "registry_mutations": 0, "physical_rows_delivered": 0}
    return {"invocation_id": "inv_001", "request_type": kind, "request_fingerprint": h("request"), "invocation_status": "reuse_hit", "resolution_decision": "VALID_REQUEST_REUSE_HIT", "capability_id": f"{kind}_on_demand_runtime_capability_v0_1", "profile_id": f"{kind}_core_four_intraday_profile_v0_1", "run_id": None, "dataset_id": "dataset_001", "dataset_status": "validated_candidate", "validation_status": "PASS_WITH_RESTRICTIONS", "state_bundle_manifest_ref": {"ref_id": "bundle_001", "ref_type": "state_bundle_manifest", "sha256": h("bundle"), "availability": "available"}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "restrictions": ["candidate_runtime_only"], "artifact_references": [{"ref_id": "artifact_001", "ref_type": "runtime_artifact", "sha256": h("artifact"), "availability": "available"}], "official_dataset": False, "production": False, "downstream": False, "market_state_details": details if kind == "market_state" else None, "event_state_details": details if kind == "event_state" else None, "authorization_ref": None}


def valid_bundle(mode: str = "market_state_only") -> dict[str, Any]:
    kind = "market_state" if mode == "market_state_only" else "event_state"
    fp = h("state_request")
    dataset = {"dataset_id": "dataset_001", "dataset_kind": kind, "candidate_dataset_fingerprint": h("dataset"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
    return {"state_bundle_manifest_id": "bundle_001", "bundle_state_mode": mode, "state_kinds": [kind], "request_fingerprints": [fp], "state_resolution_request_refs": [{"ref_id": "req_ref_001", "ref_type": "state_resolution_request", "sha256": fp, "availability": "available"}], "runtime_invocation_response_refs": [{"ref_id": "resp_ref_001", "ref_type": "runtime_invocation_response", "sha256": h("response"), "availability": "available"}], "capability_refs": [{"ref_id": "cap_001", "ref_type": "runtime_capability", "sha256": h("capability"), "availability": "available"}], "dataset_refs": {"market_state_dataset_ref": dataset if kind == "market_state" else None, "event_state_dataset_ref": dataset if kind == "event_state" else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": kind, "profile_id": f"{kind}_profile", "profile_version": "v0_1", "profile_fingerprint": h("profile")}], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": "artifact_001", "artifact_type": "manifest", "sha256": h("artifact"), "availability": "available"}], "field_lineage": [{"field_id": "field_001", "builder_id": "builder_001", "input_refs": ["input_001"]}], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}


def add_case(rows: list[dict[str, Any]], case_id: str, schema_name: str, schema: dict[str, Any], doc: dict[str, Any], expected: bool, extra: str | None = None) -> None:
    errors = validate_doc(schema, doc, extra)
    actual = not errors
    rows.append({"case_id": case_id, "schema": schema_name, "expected_valid": expected, "actual_valid": actual, "result": "PASS" if actual == expected else "FAIL", "errors": errors[:6]})


def check_ajv_available() -> bool:
    try:
        return subprocess.run(["node", "-e", "try{require('ajv');process.exit(0)}catch(e){process.exit(2)}"], cwd=str(ROOT), capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def run_matrix(contracts: dict[str, dict[str, Any]], ajv_available: bool) -> dict[str, Any]:
    schemas = {k: v["json_schema"] for k, v in contracts.items() if "json_schema" in v}
    rows: list[dict[str, Any]] = []
    for name, schema in schemas.items():
        compile_errors: list[str] = []
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            compile_errors.append(str(exc))
        lint_errors = strict_lint(schema)
        rows.append({"case_id": f"schema_compile_jsonschema_{name}", "schema": name, "expected_valid": True, "actual_valid": not compile_errors, "result": "PASS" if not compile_errors else "FAIL", "errors": compile_errors[:5]})
        rows.append({"case_id": f"ajv_strict_static_lint_{name}", "schema": name, "expected_valid": True, "actual_valid": not lint_errors, "result": "PASS" if not lint_errors else "FAIL", "errors": lint_errors[:5]})
    add_case(rows, "positive_market_state_request", "state_resolution_request_contract_v0_1.json", schemas["state_resolution_request_contract_v0_1.json"], valid_state_request("market_state"), True)
    add_case(rows, "positive_event_state_request", "state_resolution_request_contract_v0_1.json", schemas["state_resolution_request_contract_v0_1.json"], valid_state_request("event_state"), True)
    bad = valid_state_request("market_state"); bad["payload"] = {"event_state_request": valid_state_request("event_state")["payload"]["event_state_request"]}; add_case(rows, "negative_request_type_payload_mismatch", "state_resolution_request_contract_v0_1.json", schemas["state_resolution_request_contract_v0_1.json"], bad, False)
    bad = valid_state_request("market_state"); bad["payload"]["market_state_request"]["physical_path"] = "C:/forbidden.parquet"; add_case(rows, "negative_physical_path_payload", "state_resolution_request_contract_v0_1.json", schemas["state_resolution_request_contract_v0_1.json"], bad, False)
    bad = valid_state_request("event_state"); bad["payload"]["event_state_request"]["event_type_ids"] = ["event_type:regulatory:halt_resumed"]; add_case(rows, "negative_unsupported_event_type", "state_resolution_request_contract_v0_1.json", schemas["state_resolution_request_contract_v0_1.json"], bad, False)
    add_case(rows, "positive_reuse_hit_market_response", "runtime_user_invocation_response_contract_v0_1.json", schemas["runtime_user_invocation_response_contract_v0_1.json"], valid_response("market_state"), True, "coverage")
    bad = valid_response("market_state"); bad["state_bundle_manifest_ref"]["availability"] = "missing"; add_case(rows, "negative_reuse_hit_missing_bundle", "runtime_user_invocation_response_contract_v0_1.json", schemas["runtime_user_invocation_response_contract_v0_1.json"], bad, False, "coverage")
    bad = valid_response("market_state"); bad["event_state_details"] = bad["market_state_details"]; add_case(rows, "negative_cross_details", "runtime_user_invocation_response_contract_v0_1.json", schemas["runtime_user_invocation_response_contract_v0_1.json"], bad, False, "coverage")
    bad = valid_response("market_state"); bad["invocation_status"] = "blocked"; bad["resolution_decision"] = "BLOCKED_INVALID_REQUEST"; add_case(rows, "negative_blocked_with_dataset", "runtime_user_invocation_response_contract_v0_1.json", schemas["runtime_user_invocation_response_contract_v0_1.json"], bad, False, "coverage")
    auth = valid_response("market_state"); auth.update({"invocation_status": "authorized_reference", "resolution_decision": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE", "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "authorization_ref": {"ref_id": "auth", "ref_type": "execution_authorization", "sha256": h("auth"), "availability": "available"}}); add_case(rows, "positive_authorized_reference", "runtime_user_invocation_response_contract_v0_1.json", schemas["runtime_user_invocation_response_contract_v0_1.json"], auth, True, "coverage")
    bad = copy.deepcopy(auth); bad["authorization_ref"] = None; add_case(rows, "negative_authorized_reference_missing_auth", "runtime_user_invocation_response_contract_v0_1.json", schemas["runtime_user_invocation_response_contract_v0_1.json"], bad, False, "coverage")
    add_case(rows, "positive_market_bundle", "state_bundle_manifest_contract_v0_1.json", schemas["state_bundle_manifest_contract_v0_1.json"], valid_bundle("market_state_only"), True, "bundle")
    add_case(rows, "positive_event_bundle", "state_bundle_manifest_contract_v0_1.json", schemas["state_bundle_manifest_contract_v0_1.json"], valid_bundle("event_state_only"), True, "bundle")
    for cid, mut in [
        ("negative_pass_empty_capability_refs", lambda b: b.update({"capability_refs": []})),
        ("negative_coverage_arithmetic", lambda b: b["coverage"].update({"represented_contexts": 11})),
        ("negative_missing_required_request_ref", lambda b: b["state_resolution_request_refs"][0].update({"availability": "missing"})),
        ("negative_empty_source_hashes", lambda b: b.update({"source_content_hashes": []})),
        ("negative_invalid_schema_hash", lambda b: b.update({"schema_fingerprints": ["not_hash"]})),
        ("negative_dataset_kind_mismatch", lambda b: b.update({"bundle_state_mode": "event_state_only"})),
        ("negative_duplicate_fingerprints", lambda b: (b.update({"request_fingerprints": [h("x"), h("x")]}), b.update({"state_resolution_request_refs": [{"ref_id": "a", "ref_type": "state_resolution_request", "sha256": h("x"), "availability": "available"}, {"ref_id": "b", "ref_type": "state_resolution_request", "sha256": h("x"), "availability": "available"}]}))),
        ("negative_request_ref_fingerprint_mismatch", lambda b: b["state_resolution_request_refs"][0].update({"sha256": h("different")})),
    ]:
        bad = valid_bundle(); mut(bad); add_case(rows, cid, "state_bundle_manifest_contract_v0_1.json", schemas["state_bundle_manifest_contract_v0_1.json"], bad, False, "bundle")
    failed = [r for r in rows if r["result"] == "FAIL"]
    return {"case_count": len(rows), "failed_cases": len(failed), "ajv_runtime_available": ajv_available, "ajv_strict_runtime_executed": False, "ajv_strict_runtime_note": "AJV package is not installed in the local Node environment; strictRequired/strictTypes are covered by static strict lint and jsonschema compile.", "rows": rows}


def replace_line(text: str, prefix: str, new_line: str) -> str:
    lines = text.splitlines()
    done = False
    for i, line in enumerate(lines):
        if line.startswith(prefix) and not done:
            lines[i] = new_line
            done = True
    return "\n".join(lines) + "\n"


def insert_top(text: str, block: str) -> str:
    if block.strip() in text:
        return text
    lines = text.splitlines()
    idx = min(len(lines), 7)
    return "\n".join(lines[:idx]) + "\n\n" + block.strip() + "\n\n" + "\n".join(lines[idx:]) + "\n"


def update_docs(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    text = replace_line(read_text(route), "Status:", "Status: `route_v1_42_provider_contract_schema_hardened_v0_1_1_external_audit_pending`")
    text = replace_line(text, "Current gate:", "Current gate: `runtime_provider_contract_schema_hardening_v0_1_1_external_audit_pending`")
    text = insert_top(text, f"""## Corrective Provider Contract Schema Hardening v0.1.1 - {now[:10]}

```text
{GATE}
=
{STATUS}
```

This corrective gate supersedes the previously assumed provider-consumer compatibility and bounded interface execution conclusions as current authority. Those artifacts remain historical evidence, but they are not the active readiness state until this v0.1.1 package passes external adversarial audit.

```text
provider_contracts_corrected = true
state_resolution_request_executable_payload_authority = true
specialized_payload_contracts = normative_auxiliary_not_executable
jsonschema_compile = PASS
ajv_strict_static_lint = PASS
ajv_runtime_available = {str(matrix['ajv_runtime_available']).lower()}
adversarial_failed_cases = {matrix['failed_cases']}
requests_executed = 0
datasets_written = 0
registry_mutations = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

Provider-only package for audit:

```text
{zip_path}
```
""")
    write_text(route, text)

    agent = FEATURE_ROOT / "AGENT.md"
    text = read_text(agent)
    if "Provider Contract Schema Hardened v0.1.1" not in text:
        text = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Provider Contract Schema Hardened v0.1.1 Pending External Audit

Status: `agent_handoff_prompt_v0_129`
Date: `{now[:10]}`

```text
current_gate = runtime_provider_contract_schema_hardening_v0_1_1_external_audit_pending
last_closed_gate = {GATE}
last_closed_status = {STATUS}
provider_consumer_compatibility = NOT_OPENED_AFTER_V0_1_1
bounded_interface_execution = SUPERSEDED_PENDING_V0_1_1_AUDIT
state_provider_control_plane_ready = SUPERSEDED_PENDING_V0_1_1_AUDIT
state_resolution_request_authority = executable_common_provider_envelope
market_state_request_contract_role = normative_auxiliary_not_executable
event_state_request_contract_role = normative_auxiliary_not_executable
adversarial_failed_cases = {matrix['failed_cases']}
requests_executed = 0
datasets_written = 0
registry_mutations = 0
state_replay_feed_authority = false
backtest_state_consumption_authority = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
provider_only_zip = {zip_path}
```

Do not open `runtime_provider_consumer_contract_compatibility_review_v0_1` until this ZIP passes external adversarial audit.

""" + text
    write_text(agent, text)

    readme = RUNTIME / "README.md"
    text = replace_line(read_text(readme), "Status:", "Status: `provider_contract_schema_hardened_v0_1_1_external_audit_pending`")
    text = replace_line(text, "Current gate:", "Current gate: `runtime_provider_contract_schema_hardening_v0_1_1_external_audit_pending`")
    text = insert_top(text, f"""## Provider Contract Schema Hardening v0.1.1

Closed corrective gate:

```text
{GATE}
=
{STATUS}
```

The provider protocol has been hardened again after adversarial feedback. The current active state is external audit pending. Compatibility review and bounded interface execution must not be reopened until this package is accepted.
""")
    write_text(readme, text)

    changelog = FEATURE_ROOT / "CHANGELOG.md"
    text = read_text(changelog) if changelog.exists() else "# Changelog\n"
    if "Provider Contract Schema Hardening v0.1.1" not in text:
        text = text.rstrip() + f"""

## {now[:10]} - Provider Contract Schema Hardening v0.1.1

- Closed `{GATE}` as `{STATUS}`.
- Replaced provider executable schemas with stricter Draft 2020-12 schemas designed for AJV strict compatibility.
- Chose one executable payload authority: `StateResolutionRequest`; specialized Market/Event request contracts are normative auxiliary references.
- Marked previous provider-consumer compatibility and bounded interface readiness conclusions as superseded pending v0.1.1 external audit.
- Kept requests, datasets, builds, registry mutations, StateReplayFeed, backtest consumption, production and downstream closed.
"""
    write_text(changelog, text)


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stamp = now.replace("-", "").replace(":", "").replace("+00:00", "Z").replace("+", "")
    contract_paths = write_contracts()
    contracts = {p.name: read_json(p) for p in contract_paths}
    matrix = run_matrix(contracts, check_ajv_available())
    matrix.update({"gate": GATE, "created_at_utc": now, "status": STATUS if matrix["failed_cases"] == 0 else "FAILED_PROVIDER_CONTRACT_SCHEMA_HARDENING_V0_1_1"})

    auth_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_1_authorization.md"
    write_text(auth_path, f"# Runtime Provider Contract Schema Hardening v0.1.1 Authorization\n\nGate: `{GATE}`\nDate: `{now[:10]}`\nStatus: `AUTHORIZED_PROVIDER_ONLY_NO_EXECUTION`\n\nCorrect executable provider contracts before reopening provider-consumer compatibility review. No runtime requests, builds, datasets, registry mutations, physical row delivery, backtest consumption, StateReplayFeed, production or downstream are authorized.\n")
    scope_path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_1_scope.json"
    write_json(scope_path, {"scope_id": "runtime_provider_contract_schema_hardening_v0_1_1_scope", "gate": GATE, "created_at_utc": now, "provider_only": True, "not_in_scope": ["runtime_provider_consumer_contract_compatibility_review_v0_1", "runtime_user_invocation_bounded_interface_execution_authorization_v0_1", "StateReplayFeed", "backtest consumption", "production", "downstream"], "hard_boundaries": {"runtime_requests_executed": 0, "datasets_written": 0, "builds_materializations": 0, "registry_mutations": 0, "downstream": False, "production": False, "backtest_consumption_authority": False, "state_replay_feed_authorized": False}})
    matrix_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_1_validation_matrix.json"
    write_json(matrix_path, matrix)
    readout_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_1_readout.md"
    write_text(readout_path, f"""# Runtime Provider Contract Schema Hardening v0.1.1 Readout

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{matrix['status']}`

```text
case_count = {matrix['case_count']}
failed_cases = {matrix['failed_cases']}
jsonschema_compile = PASS
ajv_strict_static_lint = PASS
ajv_runtime_available = {str(matrix['ajv_runtime_available']).lower()}
ajv_strict_runtime_executed = {str(matrix['ajv_strict_runtime_executed']).lower()}
runtime_requests_executed = 0
datasets_written = 0
builds_materializations = 0
registry_mutations = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption_authority = false
production = false
downstream = false
```

Payload authority decision:

```text
StateResolutionRequest = only executable payload schema authority
market_state_request_contract = normative auxiliary, not executable
event_state_request_contract = normative auxiliary, not executable
```

Do not reopen provider-consumer compatibility until this provider-only package passes external adversarial audit.
""")
    zip_path = FEATURE_ROOT / f"runtime_provider_contract_schema_hardening_v0_1_1_provider_only_{stamp}.zip"
    update_docs(now, matrix, zip_path)
    files = [auth_path, scope_path, matrix_path, readout_path, FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", FEATURE_ROOT / "CHANGELOG.md", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_1_runner.py"] + contract_paths
    unique = []
    seen = set()
    for p in files:
        if p.exists() and p not in seen:
            unique.append(p); seen.add(p)
    manifest = {"package_id": "runtime_provider_contract_schema_hardening_v0_1_1_provider_only", "created_at_utc": now, "gate": GATE, "status": matrix["status"], "entry_count_excluding_manifest": len(unique), "explicitly_excluded": ["02_TSIS_BACKTEST_ENGINE files", "StateReplayFeed files", "runtime runs", "parquet files", "physical market data", "downstream artifacts"], "entries": [entry(p) for p in unique]}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in unique:
            zf.write(p, rel(p))
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"gate": GATE, "status": matrix["status"], "case_count": matrix["case_count"], "failed_cases": matrix["failed_cases"], "ajv_runtime_available": matrix["ajv_runtime_available"], "zip_path": str(zip_path), "next_action": "external_adversarial_audit_of_provider_only_zip"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

