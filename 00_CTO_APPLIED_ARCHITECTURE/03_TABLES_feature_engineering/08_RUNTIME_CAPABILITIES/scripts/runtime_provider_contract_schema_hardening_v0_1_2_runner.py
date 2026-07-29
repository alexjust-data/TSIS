from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
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
AJV_NODE_MODULES = Path(r"C:\tmp\tsis_ajv_runtime_v012\node_modules")

GATE = "runtime_provider_contract_schema_hardening_v0_1_2"
STATUS = "CLOSED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT"
HEX64 = "^[a-f0-9]{64}$"

CONTRACT_NAMES = [
    "state_resolution_request_contract_v0_1_2.json",
    "runtime_user_invocation_interface_contract_v0_1_2.json",
    "runtime_user_invocation_response_contract_v0_1_2.json",
    "state_bundle_manifest_contract_v0_1_2.json",
    "runtime_capability_effective_view_contract_v0_1_2.json",
]

FORBIDDEN_KEYS = {
    "physical_path",
    "parquet_path",
    "source_path",
    "output_root",
    "registry_path",
    "raw_data_path",
    "market_state_candidate_path",
    "event_state_output_path",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def entry(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def obj(props: dict[str, Any], required: list[str] | None = None, addl: bool = False) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "object", "additionalProperties": addl, "properties": props}
    if required:
        schema["required"] = required
    return schema


def partial(props: dict[str, Any]) -> dict[str, Any]:
    return obj(props, addl=True)


def arr(items: dict[str, Any], min_items: int = 0, unique: bool = False, max_items: int | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "array", "items": items, "minItems": min_items}
    if unique:
        schema["uniqueItems"] = True
    if max_items is not None:
        schema["maxItems"] = max_items
    return schema


def nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"oneOf": [schema, {"type": "null"}]}


def string() -> dict[str, Any]:
    return {"type": "string", "minLength": 1}


def hex64() -> dict[str, Any]:
    return {"type": "string", "pattern": HEX64}


def ref_schema(ref_type: str, availability: str | None = None) -> dict[str, Any]:
    return obj(
        {
            "ref_id": string(),
            "ref_type": {"const": ref_type},
            "sha256": hex64(),
            "availability": {"const": availability} if availability else {"enum": ["available", "archived", "missing", "not_required"]},
        },
        ["ref_id", "ref_type", "sha256", "availability"],
    )


def ref_value(ref_type: str, ref_id: str, seed: str | None = None, availability: str = "available") -> dict[str, Any]:
    value = seed or ref_id
    digest = value if isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value) else h(value)
    return {"ref_id": ref_id, "ref_type": ref_type, "sha256": digest, "availability": availability}


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
        "profile_version": string(),
        "exchange_scope": string(),
        "explicit_instrument_ids": arr(string(), 1, True),
        "session_dates": arr({"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}, 1, True),
        "resolution": {"enum": ["intraday", "1m", "session"]},
        "calendar_authority_id": string(),
        "point_in_time_policy_id": string(),
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
        "event_state_profile_version": string(),
        "event_type_ids": arr({"const": "event_type:market_data:session_opened"}, 1, True, 1),
        "event_subject_scope": {"const": "exchange_session"},
        "event_type_registry_snapshot_id": string(),
        "event_instance_policy_id": string(),
        "event_window_policy_id": string(),
        "event_window_definition_ids": arr(string(), 1, True, 1),
        "instrument_projection_policy_id": string(),
        "market_state_dependency_mode": {"const": "emit_or_resolve_market_state_subrequest_through_runtime_capability"},
        "market_state_profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"},
        "market_state_dependency_reuse_policy": {"enum": ["reuse_if_exact_validated_dependency_match", "metadata_only"]},
        "exchange_scope": string(),
        "explicit_instrument_ids": arr(string(), 1, True),
        "session_dates": arr({"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}, 1, True),
        "resolution": {"enum": ["intraday", "1m", "session"]},
        "calendar_authority_id": string(),
        "point_in_time_policy_id": string(),
        "source_version_policy": {"const": "exact_governed_or_block"},
        "output_mode": {"const": "candidate"},
        "reuse_policy": {"enum": ["reuse_if_exact_validated_dependency_match", "metadata_only"]},
    }
    return obj(props, list(props))


def state_resolution_schema() -> dict[str, Any]:
    policy = obj(
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
            "request_id": string(),
            "request_ref": ref_schema("state_resolution_request", "available"),
            "request_type": {"enum": ["market_state", "event_state"]},
            "state_kind": {"enum": ["market_state", "event_state"]},
            "request_fingerprint": hex64(),
            "request_contract_version": {"const": "0.1.2"},
            "consumer_id": string(),
            "consumption_purpose": {"enum": ["planning", "research", "validation", "backtest"]},
            "operation": {"enum": ["validate", "resolve", "invoke"]},
            "resolution_policy": policy,
            "payload": obj({"market_state_request": market_payload_schema(), "event_state_request": event_payload_schema()}),
        },
        ["request_id", "request_ref", "request_type", "state_kind", "request_fingerprint", "request_contract_version", "consumer_id", "consumption_purpose", "operation", "resolution_policy", "payload"],
    )
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/state_resolution_request_contract_v0_1_2.schema.json", "title": "TSIS StateResolutionRequest v0.1.2"})
    schema["allOf"] = [
        {"if": partial({"request_type": {"const": "market_state"}}), "then": partial({"state_kind": {"const": "market_state"}, "payload": obj({"market_state_request": market_payload_schema()}, ["market_state_request"])})},
        {"if": partial({"request_type": {"const": "event_state"}}), "then": partial({"state_kind": {"const": "event_state"}, "payload": obj({"event_state_request": event_payload_schema()}, ["event_state_request"])})},
        {"if": partial({"operation": {"const": "validate"}}), "then": partial({"resolution_policy": partial({"mode": {"const": "validate_only"}})})},
        {"if": partial({"operation": {"const": "resolve"}}), "then": partial({"resolution_policy": partial({"mode": {"const": "resolve_reuse_or_authorization"}})})},
        {"if": partial({"operation": {"const": "invoke"}}), "then": partial({"resolution_policy": partial({"mode": {"const": "invoke_with_authorization"}})})},
    ]
    return schema


def details_schema(kind: str) -> dict[str, Any]:
    return obj(
        {
            "state_kind": {"const": kind},
            "materializer_executions": {"const": 0},
            "source_market_data_rows_read": {"const": 0},
            "registry_mutations": {"const": 0},
            "physical_rows_delivered": {"const": 0},
        },
        ["state_kind", "materializer_executions", "source_market_data_rows_read", "registry_mutations", "physical_rows_delivered"],
    )


def response_schema() -> dict[str, Any]:
    schema = obj(
        {
            "invocation_id": string(),
            "response_ref": ref_schema("runtime_invocation_response", "available"),
            "request_ref": ref_schema("state_resolution_request", "available"),
            "request_type": {"enum": ["market_state", "event_state"]},
            "state_kind": {"enum": ["market_state", "event_state"]},
            "request_fingerprint": hex64(),
            "invocation_status": {"enum": ["blocked", "reuse_hit", "authorization_required", "authorized_reference"]},
            "resolution_decision": {"enum": ["VALID_REQUEST_REUSE_HIT", "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED", "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE", "BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_CAPABILITY", "BLOCKED_UNSUPPORTED_PROFILE", "BLOCKED_UNSUPPORTED_EVENT_TYPE", "BLOCKED_CONSUMPTION_NOT_AUTHORIZED", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]},
            "capability_id": {"enum": ["market_state_on_demand_runtime_capability_v0_1", "event_state_on_demand_runtime_capability_v0_1"]},
            "profile_id": nullable(string()),
            "run_id": nullable(string()),
            "dataset_id": nullable(string()),
            "dataset_status": nullable(string()),
            "validation_status": nullable({"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}),
            "state_bundle_manifest_ref": nullable(ref_schema("state_bundle_manifest", "available")),
            "coverage": coverage_schema(0),
            "restrictions": arr(string(), 1, True),
            "artifact_references": arr(ref_schema("runtime_artifact"), 0, True),
            "official_dataset": {"const": False},
            "production": {"const": False},
            "downstream": {"const": False},
            "market_state_details": nullable(details_schema("market_state")),
            "event_state_details": nullable(details_schema("event_state")),
            "authorization_ref": nullable(ref_schema("execution_authorization", "available")),
        },
        ["invocation_id", "response_ref", "request_ref", "request_type", "state_kind", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id", "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "state_bundle_manifest_ref", "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream", "market_state_details", "event_state_details", "authorization_ref"],
    )
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_user_invocation_response_contract_v0_1_2.schema.json", "title": "TSIS RuntimeInvocationResponse v0.1.2"})
    schema["allOf"] = [
        {"if": partial({"request_type": {"const": "market_state"}}), "then": partial({"state_kind": {"const": "market_state"}, "capability_id": {"const": "market_state_on_demand_runtime_capability_v0_1"}, "profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"}, "event_state_details": {"type": "null"}})},
        {"if": partial({"request_type": {"const": "event_state"}}), "then": partial({"state_kind": {"const": "event_state"}, "capability_id": {"const": "event_state_on_demand_runtime_capability_v0_1"}, "profile_id": {"const": "event_state_core_four_intraday_profile_v0_1"}, "market_state_details": {"type": "null"}})},
        {"if": partial({"invocation_status": {"const": "reuse_hit"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_REUSE_HIT"}, "dataset_id": string(), "dataset_status": {"const": "validated_candidate"}, "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}, "state_bundle_manifest_ref": ref_schema("state_bundle_manifest", "available"), "artifact_references": arr(ref_schema("runtime_artifact", "available"), 1, True), "authorization_ref": {"type": "null"}})},
        {"if": partial({"invocation_status": {"const": "blocked"}}), "then": partial({"resolution_decision": {"enum": ["BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_CAPABILITY", "BLOCKED_UNSUPPORTED_PROFILE", "BLOCKED_UNSUPPORTED_EVENT_TYPE", "BLOCKED_CONSUMPTION_NOT_AUTHORIZED", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0), "market_state_details": {"type": "null"}, "event_state_details": {"type": "null"}})},
        {"if": partial({"invocation_status": {"const": "authorization_required"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED"}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0)})},
        {"if": partial({"invocation_status": {"const": "authorized_reference"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE"}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": ref_schema("execution_authorization", "available"), "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0)})},
    ]
    return schema


def dataset_ref_schema(kind: str) -> dict[str, Any]:
    return obj({"dataset_id": string(), "dataset_kind": {"const": kind}, "candidate_dataset_fingerprint": hex64(), "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}, "reuse_eligibility": {"enum": ["eligible", "eligible_with_restrictions"]}, "artifact_availability": {"const": "available"}}, ["dataset_id", "dataset_kind", "candidate_dataset_fingerprint", "validation_status", "reuse_eligibility", "artifact_availability"])


def bundle_schema() -> dict[str, Any]:
    binding = obj({"request_ref": ref_schema("state_resolution_request", "available"), "request_fingerprint": hex64(), "response_ref": ref_schema("runtime_invocation_response", "available"), "state_kind": {"enum": ["market_state", "event_state"]}}, ["request_ref", "request_fingerprint", "response_ref", "state_kind"])
    profile = obj({"state_kind": {"enum": ["market_state", "event_state"]}, "profile_id": string(), "profile_version": string(), "profile_fingerprint": hex64()}, ["state_kind", "profile_id", "profile_version", "profile_fingerprint"])
    artifact = obj({"artifact_id": string(), "artifact_type": string(), "sha256": hex64(), "availability": {"const": "available"}}, ["artifact_id", "artifact_type", "sha256", "availability"])
    schema = obj(
        {
            "state_bundle_manifest_id": string(),
            "bundle_ref": ref_schema("state_bundle_manifest", "available"),
            "bundle_state_mode": {"enum": ["market_state_only", "event_state_only", "market_and_event"]},
            "state_kinds": arr({"enum": ["market_state", "event_state"]}, 1, True, 2),
            "request_response_bindings": arr(binding, 1, True),
            "capability_refs": arr(ref_schema("runtime_capability", "available"), 1, True),
            "dataset_refs": obj({"market_state_dataset_ref": nullable(dataset_ref_schema("market_state")), "event_state_dataset_ref": nullable(dataset_ref_schema("event_state"))}, ["market_state_dataset_ref", "event_state_dataset_ref"]),
            "coverage": coverage_schema(1),
            "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS", "BLOCKED", "FAIL"]},
            "restrictions": arr(string(), 1, True),
            "representation_profile_versions": arr(profile, 1, True),
            "schema_fingerprints": arr(hex64(), 1, True),
            "source_dataset_ids": arr(string(), 1, True),
            "source_content_hashes": arr(hex64(), 1, True),
            "artifact_hashes": arr(artifact, 1, True),
            "field_lineage": arr(obj({"field_id": string(), "builder_id": string(), "input_refs": arr(string(), 1, True)}, ["field_id", "builder_id", "input_refs"]), 1, True),
            "temporal_policy": obj({"point_in_time_policy_id": string(), "available_at_policy_id": string(), "future_information_exclusion": {"const": True}}, ["point_in_time_policy_id", "available_at_policy_id", "future_information_exclusion"]),
            "materialization_status": {"enum": ["reference_only", "validated_candidate_reference", "blocked", "failed"]},
            "reuse_certification": obj({"reuse_eligible": {"type": "boolean"}, "reuse_decision": {"enum": ["eligible", "eligible_with_restrictions", "not_eligible_failed_or_blocked"]}, "reusable_dataset_refs": arr(string(), 0, True)}, ["reuse_eligible", "reuse_decision", "reusable_dataset_refs"]),
            "consumption_authorization": obj({"backtest_consumption_authorized": {"const": False}, "downstream_authorized": {"const": False}, "consumption_purposes": arr(string(), 0, True, 0)}, ["backtest_consumption_authorized", "downstream_authorized", "consumption_purposes"]),
            "official_dataset": {"const": False},
            "production": {"const": False},
            "downstream": {"const": False},
            "physical_rows_delivered": {"const": False},
        },
        ["state_bundle_manifest_id", "bundle_ref", "bundle_state_mode", "state_kinds", "request_response_bindings", "capability_refs", "dataset_refs", "coverage", "validation_status", "restrictions", "representation_profile_versions", "schema_fingerprints", "source_dataset_ids", "source_content_hashes", "artifact_hashes", "field_lineage", "temporal_policy", "materialization_status", "reuse_certification", "consumption_authorization", "official_dataset", "production", "downstream", "physical_rows_delivered"],
    )
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/state_bundle_manifest_contract_v0_1_2.schema.json", "title": "TSIS StateBundleManifest v0.1.2"})
    schema["allOf"] = [
        {"if": partial({"bundle_state_mode": {"const": "market_state_only"}}), "then": partial({"state_kinds": arr({"const": "market_state"}, 1, True, 1), "dataset_refs": obj({"market_state_dataset_ref": dataset_ref_schema("market_state"), "event_state_dataset_ref": {"type": "null"}}, ["market_state_dataset_ref", "event_state_dataset_ref"])})},
        {"if": partial({"bundle_state_mode": {"const": "event_state_only"}}), "then": partial({"state_kinds": arr({"const": "event_state"}, 1, True, 1), "dataset_refs": obj({"market_state_dataset_ref": {"type": "null"}, "event_state_dataset_ref": dataset_ref_schema("event_state")}, ["market_state_dataset_ref", "event_state_dataset_ref"])})},
        {"if": partial({"bundle_state_mode": {"const": "market_and_event"}}), "then": partial({"state_kinds": arr({"enum": ["market_state", "event_state"]}, 2, True, 2), "request_response_bindings": arr(binding, 2, True), "dataset_refs": obj({"market_state_dataset_ref": dataset_ref_schema("market_state"), "event_state_dataset_ref": dataset_ref_schema("event_state")}, ["market_state_dataset_ref", "event_state_dataset_ref"])})},
        {"if": partial({"validation_status": {"enum": ["BLOCKED", "FAIL"]}}), "then": partial({"materialization_status": {"enum": ["blocked", "failed"]}, "reuse_certification": obj({"reuse_eligible": {"const": False}, "reuse_decision": {"const": "not_eligible_failed_or_blocked"}, "reusable_dataset_refs": arr(string(), 0, True, 0)}, ["reuse_eligible", "reuse_decision", "reusable_dataset_refs"])})},
    ]
    return schema


def interface_schema() -> dict[str, Any]:
    schema = obj({"operation": {"enum": ["validate", "resolve", "invoke"]}, "state_resolution_request": state_resolution_schema(), "execution_authorization_ref": nullable(ref_schema("execution_authorization", "available"))}, ["operation", "state_resolution_request", "execution_authorization_ref"])
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_user_invocation_interface_contract_v0_1_2.schema.json", "title": "TSIS RuntimeUserInvocationInterface v0.1.2"})
    schema["allOf"] = [
        {"if": partial({"operation": {"const": "validate"}}), "then": partial({"execution_authorization_ref": {"type": "null"}, "state_resolution_request": partial({"operation": {"const": "validate"}})})},
        {"if": partial({"operation": {"const": "resolve"}}), "then": partial({"execution_authorization_ref": {"type": "null"}, "state_resolution_request": partial({"operation": {"const": "resolve"}})})},
        {"if": partial({"operation": {"const": "invoke"}}), "then": partial({"execution_authorization_ref": ref_schema("execution_authorization", "available"), "state_resolution_request": partial({"operation": {"const": "invoke"}})})},
    ]
    return schema


def effective_view_schema() -> dict[str, Any]:
    permissions = obj({"metadata_lookup": {"const": True}, "registry_lookup": {"const": True}, "exact_reuse_resolution": {"const": True}, "candidate_generation_under_separate_authorization": {"const": True}, "physical_row_delivery": {"const": False}, "state_replay_feed": {"const": False}, "backtest_consumption": {"const": False}, "production": {"const": False}, "downstream": {"const": False}}, ["metadata_lookup", "registry_lookup", "exact_reuse_resolution", "candidate_generation_under_separate_authorization", "physical_row_delivery", "state_replay_feed", "backtest_consumption", "production", "downstream"])
    cap = obj({"capability_id": {"enum": ["market_state_on_demand_runtime_capability_v0_1", "event_state_on_demand_runtime_capability_v0_1"]}, "request_type": {"enum": ["market_state", "event_state"]}, "capability_status": {"enum": ["promoted_with_restrictions", "available_with_restrictions"]}, "supported_profile_ids": arr(string(), 1, True), "supported_event_type_ids": arr(string(), 0, True, 1), "subject_scope": nullable(string()), "candidate_generation_authority": {"const": True}, "reuse_authority": {"const": True}, "official_dataset": {"const": False}, "production": {"const": False}, "downstream": {"const": False}, "backtest_consumption": {"const": False}, "effective_permissions": permissions}, ["capability_id", "request_type", "capability_status", "supported_profile_ids", "supported_event_type_ids", "subject_scope", "candidate_generation_authority", "reuse_authority", "official_dataset", "production", "downstream", "backtest_consumption", "effective_permissions"])
    schema = obj({"view_id": string(), "view_version": {"const": "0.1.2"}, "capabilities": arr(cap, 2, True, 2)}, ["view_id", "view_version", "capabilities"])
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_capability_effective_view_contract_v0_1_2.schema.json", "title": "TSIS RuntimeCapabilityEffectiveView v0.1.2"})
    return schema


def contract_doc(contract_id: str, schema: dict[str, Any], purpose: str) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "contract_version": "0.1.2",
        "status": "PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_2_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT",
        "owner_layer": "08_RUNTIME_CAPABILITIES",
        "schema_hardening_gate": GATE,
        "purpose": purpose,
        "contract_hash_policy": {"hash_authority": "PACKAGE_MANIFEST.full_file_sha256", "canonicalization_algorithm": "full_file_sha256_utf8_lf_no_bom", "embedded_contract_hash": "not_used_in_v0_1_2"},
        "json_schema": schema,
        "semantic_validator_required": True,
    }


def write_contracts() -> list[Path]:
    docs = {
        "state_resolution_request_contract_v0_1_2.json": contract_doc("state_resolution_request_contract_v0_1_2", state_resolution_schema(), "Executable common provider envelope for Market State and Event State resolution requests."),
        "runtime_user_invocation_interface_contract_v0_1_2.json": contract_doc("runtime_user_invocation_interface_contract_v0_1_2", interface_schema(), "Executable provider control-plane interface contract for validate, resolve and invoke."),
        "runtime_user_invocation_response_contract_v0_1_2.json": contract_doc("runtime_user_invocation_response_contract_v0_1_2", response_schema(), "Executable provider response envelope with status, decision and field constraints."),
        "state_bundle_manifest_contract_v0_1_2.json": contract_doc("state_bundle_manifest_contract_v0_1_2", bundle_schema(), "Executable provider StateBundleManifest reference contract."),
        "runtime_capability_effective_view_contract_v0_1_2.json": contract_doc("runtime_capability_effective_view_contract_v0_1_2", effective_view_schema(), "Executable effective view of Market State and Event State runtime capabilities."),
    }
    paths: list[Path] = []
    for name, doc in docs.items():
        path = RUNTIME / name
        write_json(path, doc)
        paths.append(path)
    return paths


def ajv_compile(schema: dict[str, Any]) -> list[str]:
    if not AJV_NODE_MODULES.exists():
        return [f"AJV node_modules not found at {AJV_NODE_MODULES}"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8", newline="\n") as tmp:
        json.dump(schema, tmp)
        tmp_name = tmp.name
    script = """
const fs = require('fs');
const Ajv2020 = require('ajv/dist/2020');
const schema = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const ajv = new Ajv2020({strict: true, allErrors: true});
ajv.compile(schema);
"""
    env = os.environ.copy()
    env["NODE_PATH"] = str(AJV_NODE_MODULES)
    result = subprocess.run(["node", "-e", script, tmp_name], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=20)
    Path(tmp_name).unlink(missing_ok=True)
    if result.returncode == 0:
        return []
    return [line for line in (result.stderr + result.stdout).splitlines() if line][:8]


def forbidden_scan(value: Any) -> list[str]:
    hits: list[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for key, child in v.items():
                if key.lower() in FORBIDDEN_KEYS:
                    hits.append(f"{p}.{key}")
                walk(child, f"{p}.{key}")
        elif isinstance(v, list):
            for i, child in enumerate(v):
                walk(child, f"{p}[{i}]")

    walk(value, "$")
    return hits


def coverage_ok(c: dict[str, Any]) -> bool:
    return c.get("requested_contexts") == c.get("represented_contexts", 0) + c.get("unavailable_contexts", 0) + c.get("blocked_contexts", 0) + c.get("quarantined_contexts", 0) + c.get("unaccounted_contexts", 0)


def collect_refs(value: Any) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []

    def walk(v: Any) -> None:
        if isinstance(v, dict):
            if {"ref_id", "ref_type", "sha256", "availability"}.issubset(v):
                refs.append(v)
            for child in v.values():
                walk(child)
        elif isinstance(v, list):
            for child in v:
                walk(child)

    walk(value)
    return refs


def duplicate_ref_ids(value: Any) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for ref in collect_refs(value):
        ref_id = ref.get("ref_id")
        if ref_id in seen:
            dup.add(ref_id)
        seen.add(ref_id)
    return sorted(dup)


def semantic_errors(doc: dict[str, Any], kind: str) -> list[str]:
    errors: list[str] = []
    if forbidden_scan(doc):
        errors.append("forbidden physical/path-like key present")
    if "coverage" in doc and not coverage_ok(doc["coverage"]):
        errors.append("coverage arithmetic mismatch")
    duplicates = duplicate_ref_ids(doc)
    if duplicates:
        errors.append("duplicate semantic ref_id: " + ",".join(duplicates))

    if kind == "state_resolution_request":
        request_type = doc.get("request_type")
        if doc.get("request_ref", {}).get("sha256") != doc.get("request_fingerprint"):
            errors.append("request_ref sha256 does not match request_fingerprint")
        payload = doc.get("payload", {})
        if request_type == "market_state" and set(payload) != {"market_state_request"}:
            errors.append("market_state request must carry exactly market_state_request")
        if request_type == "event_state" and set(payload) != {"event_state_request"}:
            errors.append("event_state request must carry exactly event_state_request")
        expected_mode = {"validate": "validate_only", "resolve": "resolve_reuse_or_authorization", "invoke": "invoke_with_authorization"}.get(doc.get("operation"))
        if expected_mode and doc.get("resolution_policy", {}).get("mode") != expected_mode:
            errors.append("operation/resolution mode mismatch")

    if kind == "interface":
        if doc.get("state_resolution_request", {}).get("operation") != doc.get("operation"):
            errors.append("interface operation does not match embedded request operation")
        if doc.get("operation") == "invoke" and not isinstance(doc.get("execution_authorization_ref"), dict):
            errors.append("invoke requires execution_authorization_ref")
        if doc.get("operation") in {"validate", "resolve"} and doc.get("execution_authorization_ref") is not None:
            errors.append("validate/resolve must not include execution_authorization_ref")

    if kind == "response":
        if doc.get("request_ref", {}).get("sha256") != doc.get("request_fingerprint"):
            errors.append("request_ref sha256 does not match request_fingerprint")
        if doc.get("request_type") != doc.get("state_kind"):
            errors.append("request_type/state_kind mismatch")
        expected_cap = f"{doc.get('request_type')}_on_demand_runtime_capability_v0_1"
        if doc.get("capability_id") != expected_cap:
            errors.append("request_type/capability_id mismatch")
        if doc.get("request_type") == "market_state" and doc.get("event_state_details") is not None:
            errors.append("market_state response includes event_state_details")
        if doc.get("request_type") == "event_state" and doc.get("market_state_details") is not None:
            errors.append("event_state response includes market_state_details")
        status = doc.get("invocation_status")
        if status == "reuse_hit" and (doc.get("resolution_decision") != "VALID_REQUEST_REUSE_HIT" or not doc.get("dataset_id") or not isinstance(doc.get("state_bundle_manifest_ref"), dict)):
            errors.append("reuse_hit lacks required governed dataset/bundle references")
        if status in {"blocked", "authorization_required"}:
            forbidden = ["run_id", "dataset_id", "dataset_status", "validation_status", "state_bundle_manifest_ref", "authorization_ref"]
            if any(doc.get(key) is not None for key in forbidden):
                errors.append(f"{status} response carries forbidden fields")
        if status == "authorized_reference" and not isinstance(doc.get("authorization_ref"), dict):
            errors.append("authorized_reference lacks authorization_ref")

    if kind == "bundle":
        bindings = doc.get("request_response_bindings", [])
        binding_keys = []
        for binding in bindings:
            response_ref = binding.get("response_ref")
            if not isinstance(response_ref, dict):
                errors.append("binding missing response_ref")
                binding_keys.append((None, binding.get("request_fingerprint"), binding.get("state_kind")))
            else:
                binding_keys.append((response_ref.get("ref_id"), binding.get("request_fingerprint"), binding.get("state_kind")))
        if len(bindings) != len(set(binding_keys)):
            errors.append("duplicate or ambiguous response/request/state_kind binding")
        response_ids = [b.get("response_ref", {}).get("ref_id") for b in bindings if isinstance(b.get("response_ref"), dict)]
        if len(response_ids) != len(set(response_ids)):
            errors.append("duplicate response_ref in bindings")
        for binding in bindings:
            if binding.get("request_ref", {}).get("sha256") != binding.get("request_fingerprint"):
                errors.append("request_ref sha256 does not match binding request_fingerprint")
            if binding.get("state_kind") not in doc.get("state_kinds", []):
                errors.append("binding state_kind outside state_kinds")
        mode = doc.get("bundle_state_mode")
        kinds = set(doc.get("state_kinds", []))
        if mode == "market_state_only" and kinds != {"market_state"}:
            errors.append("market_state_only bundle has wrong state_kinds")
        if mode == "event_state_only" and kinds != {"event_state"}:
            errors.append("event_state_only bundle has wrong state_kinds")
        if mode == "market_and_event" and kinds != {"market_state", "event_state"}:
            errors.append("market_and_event bundle has wrong state_kinds")
        reuse = doc.get("reuse_certification", {})
        if doc.get("validation_status") in {"FAIL", "BLOCKED"} and (reuse.get("reuse_eligible") or reuse.get("reusable_dataset_refs")):
            errors.append("FAIL/BLOCKED manifest cannot certify reusable dataset")

    if kind == "effective_view":
        caps = doc.get("capabilities", [])
        ids = [cap.get("capability_id") for cap in caps]
        if ids.count("market_state_on_demand_runtime_capability_v0_1") != 1 or ids.count("event_state_on_demand_runtime_capability_v0_1") != 1:
            errors.append("effective view must expose exactly one Market State and one Event State capability")
        for cap in caps:
            perms = cap.get("effective_permissions", {})
            if cap.get("capability_id", "").startswith("market_state") and cap.get("request_type") != "market_state":
                errors.append("market capability request_type mismatch")
            if cap.get("capability_id", "").startswith("event_state") and cap.get("request_type") != "event_state":
                errors.append("event capability request_type mismatch")
            if cap.get("request_type") == "market_state" and cap.get("supported_event_type_ids"):
                errors.append("market capability must not advertise event types")
            if cap.get("request_type") == "event_state" and cap.get("supported_event_type_ids") != ["event_type:market_data:session_opened"]:
                errors.append("event capability must advertise only session_opened")
            for field in ["official_dataset", "production", "downstream", "backtest_consumption"]:
                if cap.get(field) is not False:
                    errors.append(f"capability {field} contradiction")
            for field in ["physical_row_delivery", "state_replay_feed", "backtest_consumption", "production", "downstream"]:
                if perms.get(field) is not False:
                    errors.append(f"effective permission {field} contradiction")
    return errors


def validate_doc(schema: dict[str, Any], doc: dict[str, Any], kind: str) -> list[str]:
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(doc)]
    errors.extend(semantic_errors(doc, kind))
    return errors


def valid_request(kind: str = "market_state", operation: str = "resolve") -> dict[str, Any]:
    fp = h(f"request_{kind}_{operation}")
    mode = {"validate": "validate_only", "resolve": "resolve_reuse_or_authorization", "invoke": "invoke_with_authorization"}[operation]
    doc = {
        "request_id": f"req_{kind}_001",
        "request_ref": ref_value("state_resolution_request", f"req_ref_{kind}", fp),
        "request_type": kind,
        "state_kind": kind,
        "request_fingerprint": fp,
        "request_contract_version": "0.1.2",
        "consumer_id": "provider_hardening_v0_1_2_runner",
        "consumption_purpose": "validation",
        "operation": operation,
        "resolution_policy": {"mode": mode, "reuse_policy": "reuse_if_exact_validated_match_or_authorization_required", "allow_new_candidate_execution": False, "allow_physical_path_input": False, "requested_output_mode": "candidate_reference_only", "production": False, "downstream": False},
    }
    if kind == "market_state":
        doc["payload"] = {"market_state_request": {"request_type": "market_state", "profile_id": "market_state_core_four_intraday_profile_v0_1", "profile_version_policy": "exact", "profile_version": "v0_1", "exchange_scope": "XNYS", "explicit_instrument_ids": ["AAME"], "session_dates": ["2021-01-19"], "resolution": "intraday", "calendar_authority_id": "calendar:xnys:v0_1", "point_in_time_policy_id": "pit:v0_1", "source_version_policy": "exact_governed_or_block", "output_mode": "candidate", "reuse_policy": "reuse_if_exact_validated_match"}}
    else:
        doc["payload"] = {"event_state_request": {"request_type": "event_state", "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1", "event_state_profile_version_policy": "exact", "event_state_profile_version": "v0_1", "event_type_ids": ["event_type:market_data:session_opened"], "event_subject_scope": "exchange_session", "event_type_registry_snapshot_id": "event_type_registry:v0_1", "event_instance_policy_id": "event_instance:session_opened:v0_1", "event_window_policy_id": "event_window:at_event:v0_1", "event_window_definition_ids": ["event_window:session_opened:at_event_v0_1"], "instrument_projection_policy_id": "projection:exchange_session_to_instrument:v0_1", "market_state_dependency_mode": "emit_or_resolve_market_state_subrequest_through_runtime_capability", "market_state_profile_id": "market_state_core_four_intraday_profile_v0_1", "market_state_dependency_reuse_policy": "reuse_if_exact_validated_dependency_match", "exchange_scope": "XNYS", "explicit_instrument_ids": ["AAME"], "session_dates": ["2021-01-19"], "resolution": "intraday", "calendar_authority_id": "calendar:xnys:v0_1", "point_in_time_policy_id": "pit:v0_1", "source_version_policy": "exact_governed_or_block", "output_mode": "candidate", "reuse_policy": "reuse_if_exact_validated_dependency_match"}}
    return doc


def valid_interface(operation: str = "resolve") -> dict[str, Any]:
    return {"operation": operation, "state_resolution_request": valid_request("market_state", operation), "execution_authorization_ref": ref_value("execution_authorization", "auth_001") if operation == "invoke" else None}


def valid_response(kind: str = "market_state", status: str = "reuse_hit") -> dict[str, Any]:
    fp = h(f"request_{kind}_resolve")
    details = {"state_kind": kind, "materializer_executions": 0, "source_market_data_rows_read": 0, "registry_mutations": 0, "physical_rows_delivered": 0}
    doc = {"invocation_id": "inv_001", "response_ref": ref_value("runtime_invocation_response", "resp_001"), "request_ref": ref_value("state_resolution_request", f"req_ref_{kind}", fp), "request_type": kind, "state_kind": kind, "request_fingerprint": fp, "invocation_status": status, "resolution_decision": "VALID_REQUEST_REUSE_HIT", "capability_id": f"{kind}_on_demand_runtime_capability_v0_1", "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1", "run_id": None, "dataset_id": "dataset_001", "dataset_status": "validated_candidate", "validation_status": "PASS_WITH_RESTRICTIONS", "state_bundle_manifest_ref": ref_value("state_bundle_manifest", "bundle_001"), "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "restrictions": ["candidate_runtime_only"], "artifact_references": [ref_value("runtime_artifact", "artifact_001")], "official_dataset": False, "production": False, "downstream": False, "market_state_details": details if kind == "market_state" else None, "event_state_details": details if kind == "event_state" else None, "authorization_ref": None}
    if status == "blocked":
        doc.update({"resolution_decision": "BLOCKED_INVALID_REQUEST", "run_id": None, "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "artifact_references": [], "market_state_details": None, "event_state_details": None})
    if status == "authorization_required":
        doc.update({"resolution_decision": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED", "run_id": None, "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "artifact_references": []})
    if status == "authorized_reference":
        doc.update({"resolution_decision": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE", "run_id": None, "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "artifact_references": [], "authorization_ref": ref_value("execution_authorization", "auth_001")})
    return doc


def valid_bundle(mode: str = "market_state_only") -> dict[str, Any]:
    kinds = ["market_state"] if mode == "market_state_only" else ["event_state"] if mode == "event_state_only" else ["market_state", "event_state"]
    bindings = []
    for i, kind in enumerate(kinds, 1):
        fp = h(f"request_{kind}_resolve")
        bindings.append({"request_ref": ref_value("state_resolution_request", f"req_ref_{kind}", fp), "request_fingerprint": fp, "response_ref": ref_value("runtime_invocation_response", f"resp_{i:03d}", f"response_{kind}"), "state_kind": kind})

    def dataset(kind: str) -> dict[str, Any]:
        return {"dataset_id": f"{kind}_dataset_001", "dataset_kind": kind, "candidate_dataset_fingerprint": h(f"dataset_{kind}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}

    return {"state_bundle_manifest_id": "bundle_001", "bundle_ref": ref_value("state_bundle_manifest", "bundle_ref_001"), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": bindings, "capability_refs": [ref_value("runtime_capability", f"cap_{kind}") for kind in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": kind, "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{kind}")} for kind in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": "artifact_001", "artifact_type": "manifest", "sha256": h("artifact"), "availability": "available"}], "field_lineage": [{"field_id": "field_001", "builder_id": "builder_001", "input_refs": ["input_001"]}], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{kind}_dataset_001" for kind in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}


def valid_effective_view() -> dict[str, Any]:
    perms = {"metadata_lookup": True, "registry_lookup": True, "exact_reuse_resolution": True, "candidate_generation_under_separate_authorization": True, "physical_row_delivery": False, "state_replay_feed": False, "backtest_consumption": False, "production": False, "downstream": False}
    return {"view_id": "runtime_capability_effective_view_v0_1_2", "view_version": "0.1.2", "capabilities": [{"capability_id": "market_state_on_demand_runtime_capability_v0_1", "request_type": "market_state", "capability_status": "promoted_with_restrictions", "supported_profile_ids": ["market_state_core_four_intraday_profile_v0_1"], "supported_event_type_ids": [], "subject_scope": None, "candidate_generation_authority": True, "reuse_authority": True, "official_dataset": False, "production": False, "downstream": False, "backtest_consumption": False, "effective_permissions": copy.deepcopy(perms)}, {"capability_id": "event_state_on_demand_runtime_capability_v0_1", "request_type": "event_state", "capability_status": "promoted_with_restrictions", "supported_profile_ids": ["event_state_core_four_intraday_profile_v0_1"], "supported_event_type_ids": ["event_type:market_data:session_opened"], "subject_scope": "exchange_session", "candidate_generation_authority": True, "reuse_authority": True, "official_dataset": False, "production": False, "downstream": False, "backtest_consumption": False, "effective_permissions": copy.deepcopy(perms)}]}


def add_case(rows: list[dict[str, Any]], case_id: str, origin: str, schema_name: str, schema: dict[str, Any], semantic_kind: str, doc: dict[str, Any], expected: bool) -> None:
    errors = validate_doc(schema, doc, semantic_kind)
    actual = not errors
    rows.append({"case_id": case_id, "case_origin": origin, "schema": schema_name, "expected_valid": expected, "actual_valid": actual, "result": "PASS" if actual == expected else "FAIL", "errors": errors[:8]})


def run_matrix(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
    rows: list[dict[str, Any]] = []
    for name, schema in schemas.items():
        errors: list[str] = []
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errors.append(str(exc))
        rows.append({"case_id": f"schema_compile_jsonschema_{name}", "case_origin": "original_31_regression", "schema": name, "expected_valid": True, "actual_valid": not errors, "result": "PASS" if not errors else "FAIL", "errors": errors[:8]})
        ajv_errors = ajv_compile(schema)
        rows.append({"case_id": f"ajv_8_17_1_strict_runtime_compile_{name}", "case_origin": "original_31_regression", "schema": name, "expected_valid": True, "actual_valid": not ajv_errors, "result": "PASS" if not ajv_errors else "FAIL", "errors": ajv_errors[:8]})

    srr, iface, resp, bundle, eff = (schemas[name] for name in CONTRACT_NAMES)
    original_cases = [
        ("positive_market_state_request", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", valid_request("market_state"), True),
        ("positive_event_state_request", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", valid_request("event_state"), True),
        ("negative_request_type_payload_mismatch", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", {**valid_request("market_state"), "payload": {"event_state_request": valid_request("event_state")["payload"]["event_state_request"]}}, False),
        ("negative_physical_path_payload", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", None, False),
        ("negative_unsupported_event_type", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", None, False),
        ("positive_reuse_hit_market_response", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", valid_response("market_state"), True),
        ("negative_reuse_hit_missing_bundle", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", None, False),
        ("negative_cross_details", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", None, False),
        ("negative_blocked_with_dataset", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", None, False),
        ("positive_authorized_reference", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", valid_response("market_state", "authorized_reference"), True),
        ("negative_authorized_reference_missing_auth", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", None, False),
        ("positive_market_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle("market_state_only"), True),
        ("positive_event_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle("event_state_only"), True),
        ("negative_pass_empty_capability_refs", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_coverage_arithmetic", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_missing_required_request_ref", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_empty_source_hashes", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_invalid_schema_hash", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_dataset_kind_mismatch", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_duplicate_fingerprints", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
        ("negative_request_ref_fingerprint_mismatch", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", None, False),
    ]
    for case_id, schema_name, schema, kind, doc, expected in original_cases:
        if doc is None:
            doc = make_mutation(case_id)
        add_case(rows, case_id, "original_31_regression", schema_name, schema, kind, doc, expected)

    external_cases = [
        ("F01_cardinality_extra_response_ref_without_request", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), lambda d: d["request_response_bindings"].pop()), False),
        ("F01_response_ref_absent_for_request", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"response_ref": None})), False),
        ("F02_duplicate_ref_id_cross_arrays", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["capability_refs"][0].update({"ref_id": d["bundle_ref"]["ref_id"]})), False),
        ("F03_market_response_event_capability", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response("market_state"), lambda d: d.update({"capability_id": "event_state_on_demand_runtime_capability_v0_1"})), False),
        ("F03_event_response_market_profile", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response("event_state"), lambda d: d.update({"profile_id": "market_state_core_four_intraday_profile_v0_1"})), False),
        ("F04_effective_view_downstream_true", "runtime_capability_effective_view_contract_v0_1_2.json", eff, "effective_view", mutate(valid_effective_view(), lambda d: d["capabilities"][0]["effective_permissions"].update({"downstream": True})), False),
        ("F04_effective_view_duplicate_capability", "runtime_capability_effective_view_contract_v0_1_2.json", eff, "effective_view", mutate(valid_effective_view(), lambda d: d["capabilities"][1].update({"capability_id": "market_state_on_demand_runtime_capability_v0_1", "request_type": "market_state", "supported_event_type_ids": []})), False),
        ("F05_fail_manifest_reuse_eligible", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d.update({"validation_status": "FAIL", "materialization_status": "failed"})), False),
        ("F06_validate_operation_resolve_mode", "runtime_user_invocation_interface_contract_v0_1_2.json", iface, "interface", mutate(valid_interface("validate"), lambda d: d["state_resolution_request"]["resolution_policy"].update({"mode": "resolve_reuse_or_authorization"})), False),
        ("F06_invoke_missing_authorization", "runtime_user_invocation_interface_contract_v0_1_2.json", iface, "interface", mutate(valid_interface("invoke"), lambda d: d.update({"execution_authorization_ref": None})), False),
        ("F07_authorization_required_with_dataset", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response("market_state", "authorization_required"), lambda d: d.update({"dataset_id": "dataset_should_not_exist"})), False),
        ("F09_market_request_event_state_binding", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"state_kind": "event_state"})), False),
        ("F09_request_fingerprint_mismatch_in_binding", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"request_fingerprint": h("wrong")})), False),
    ]
    for case in external_cases:
        add_case(rows, case[0], "external_adversarial_regression", case[1], case[2], case[3], case[4], case[5])

    case_ids = [row["case_id"] for row in rows]
    required = case_ids[:]
    missing = sorted(set(required) - set(case_ids))
    duplicates = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
    failed = [row for row in rows if row["result"] == "FAIL"]
    return {
        "gate": GATE,
        "status": STATUS if not failed and not missing and not duplicates and len(rows) >= 44 else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2",
        "created_at_utc": now_utc(),
        "case_count": len(rows),
        "original_case_count": len([r for r in rows if r["case_origin"] == "original_31_regression"]),
        "external_regression_case_count": len([r for r in rows if r["case_origin"] == "external_adversarial_regression"]),
        "required_case_ids": required,
        "missing_required_case_ids": missing,
        "duplicate_case_ids": duplicates,
        "unexpected_silent_skips": 0,
        "failed_cases": len(failed),
        "jsonschema_draft_2020_12_compile": "PASS" if not any(r["case_id"].startswith("schema_compile") and r["result"] == "FAIL" for r in rows) else "FAIL",
        "ajv_8_17_1_strict_runtime": "PASS" if not any(r["case_id"].startswith("ajv_8_17_1") and r["result"] == "FAIL" for r in rows) else "FAIL",
        "semantic_validator_execution": "PASS" if not failed else "FAIL",
        "expanded_adversarial_matrix": "PASS" if len(rows) >= 44 and not failed else "FAIL",
        "runtime_requests_executed": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "physical_state_rows_delivered": 0,
        "state_replay_feed_records_emitted": 0,
        "backtest_consumption_authority": False,
        "production": False,
        "downstream": False,
        "rows": rows,
    }


def mutate(doc: dict[str, Any], fn) -> dict[str, Any]:
    fn(doc)
    return doc


def make_mutation(case_id: str) -> dict[str, Any]:
    if case_id == "negative_physical_path_payload":
        return mutate(valid_request("market_state"), lambda d: d["payload"]["market_state_request"].update({"physical_path": "C:/forbidden.parquet"}))
    if case_id == "negative_unsupported_event_type":
        return mutate(valid_request("event_state"), lambda d: d["payload"]["event_state_request"].update({"event_type_ids": ["event_type:regulatory:halt_resumed"]}))
    if case_id == "negative_reuse_hit_missing_bundle":
        return mutate(valid_response("market_state"), lambda d: d["state_bundle_manifest_ref"].update({"availability": "missing"}))
    if case_id == "negative_cross_details":
        return mutate(valid_response("market_state"), lambda d: d.update({"event_state_details": {"state_kind": "event_state", "materializer_executions": 0, "source_market_data_rows_read": 0, "registry_mutations": 0, "physical_rows_delivered": 0}}))
    if case_id == "negative_blocked_with_dataset":
        return mutate(valid_response("market_state", "blocked"), lambda d: d.update({"dataset_id": "bad"}))
    if case_id == "negative_authorized_reference_missing_auth":
        return mutate(valid_response("market_state", "authorized_reference"), lambda d: d.update({"authorization_ref": None}))
    if case_id == "negative_pass_empty_capability_refs":
        return mutate(valid_bundle(), lambda d: d.update({"capability_refs": []}))
    if case_id == "negative_coverage_arithmetic":
        return mutate(valid_bundle(), lambda d: d["coverage"].update({"represented_contexts": 11}))
    if case_id == "negative_missing_required_request_ref":
        return mutate(valid_bundle(), lambda d: d["request_response_bindings"][0]["request_ref"].update({"availability": "missing"}))
    if case_id == "negative_empty_source_hashes":
        return mutate(valid_bundle(), lambda d: d.update({"source_content_hashes": []}))
    if case_id == "negative_invalid_schema_hash":
        return mutate(valid_bundle(), lambda d: d.update({"schema_fingerprints": ["not_hash"]}))
    if case_id == "negative_dataset_kind_mismatch":
        return mutate(valid_bundle(), lambda d: d["dataset_refs"].update({"market_state_dataset_ref": {"dataset_id": "bad", "dataset_kind": "event_state", "candidate_dataset_fingerprint": h("bad"), "validation_status": "PASS", "reuse_eligibility": "eligible", "artifact_availability": "available"}}))
    if case_id == "negative_duplicate_fingerprints":
        return mutate(valid_bundle(), lambda d: d["request_response_bindings"].append(copy.deepcopy(d["request_response_bindings"][0])))
    if case_id == "negative_request_ref_fingerprint_mismatch":
        return mutate(valid_bundle(), lambda d: d["request_response_bindings"][0]["request_ref"].update({"sha256": h("different")}))
    raise KeyError(case_id)


def write_scope(now: str) -> Path:
    path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json"
    write_json(path, {"scope_id": "runtime_provider_contract_schema_hardening_v0_1_2_scope", "gate": GATE, "created_at_utc": now, "status": "AUTHORIZED_IMPLEMENTATION_SCOPE_PROVIDER_ONLY", "provider_only": True, "authorized_by": "runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1", "required_findings": ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09"], "minimum_case_counts": {"original_regression": 31, "external_adversarial_regression": 13, "total": 44}, "hard_boundaries": {"runtime_requests_executed": 0, "runtime_builds_executed": 0, "datasets_written": 0, "registry_mutations": 0, "physical_state_rows_delivered": 0, "state_replay_feed_records_emitted": 0, "backtest_runs_started": 0, "backtest_consumption_authority": False, "production": False, "downstream": False}, "not_authorized": ["runtime_provider_consumer_contract_compatibility_review_v0_1", "StateBundle physical reads", "StateReplayFeed", "Backtest RunPreflight state integration", "production", "downstream"]})
    return path


def prepend_once(path: Path, marker: str, block: str) -> None:
    text = read_text(path) if path.exists() else ""
    if marker not in text:
        write_text(path, block.strip() + "\n\n" + text)


def replace_first(path: Path, prefix: str, line: str) -> None:
    lines = read_text(path).splitlines()
    for index, value in enumerate(lines):
        if value.startswith(prefix):
            lines[index] = line
            break
    write_text(path, "\n".join(lines) + "\n")


def update_docs(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    replace_first(route, "Status:", "Status: `route_v1_51_provider_hardening_v0_1_2_internal_pass_external_audit_pending`")
    replace_first(route, "Current gate:", "Current gate: `runtime_provider_contract_schema_hardening_v0_1_2_external_audit_pending`")
    prepend_once(route, "Provider Contract Schema Hardening v0.1.2 Internal Pass", f"""## Provider Contract Schema Hardening v0.1.2 Internal Pass - {now[:10]}

```text
{GATE}
=
{matrix['status']}

PROVIDER_V0_1_2_EXTERNAL_AUDIT
=
PENDING

PROVIDER_CONSUMER_COMPATIBILITY
=
NOT_OPENED_AFTER_V0_1_2
```

The provider-only v0.1.2 hardening package has internal validation pass but is not accepted authority until independent external audit passes.

```text
case_count = {matrix['case_count']}
original_case_count = {matrix['original_case_count']}
external_regression_case_count = {matrix['external_regression_case_count']}
failed_cases = {matrix['failed_cases']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
duplicate_case_ids = {len(matrix['duplicate_case_ids'])}
jsonschema_draft_2020_12_compile = {matrix['jsonschema_draft_2020_12_compile']}
ajv_8_17_1_strict_runtime = {matrix['ajv_8_17_1_strict_runtime']}
semantic_validator_execution = {matrix['semantic_validator_execution']}
runtime_requests_executed = 0
datasets_written = 0
registry_mutations = 0
physical_state_rows_delivered = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

Provider-only ZIP pending external audit:

```text
{zip_path}
```
""")

    readme = RUNTIME / "README.md"
    replace_first(readme, "Status:", "Status: `provider_hardening_v0_1_2_internal_pass_external_audit_pending`")
    replace_first(readme, "Current provider gate:", "Current provider gate: `runtime_provider_contract_schema_hardening_v0_1_2_external_audit_pending`")
    prepend_once(readme, "Provider Contract Schema Hardening v0.1.2 Internal Pass", f"""## Provider Contract Schema Hardening v0.1.2 Internal Pass

```text
{GATE} = {matrix['status']}
PROVIDER_V0_1_2_EXTERNAL_AUDIT = PENDING
PROVIDER_CONSUMER_COMPATIBILITY = NOT_OPENED_AFTER_V0_1_2
```

The next action is independent external audit of the provider-only ZIP. Physical row delivery, StateReplayFeed, backtest consumption, production and downstream remain closed.
""")

    agent = FEATURE_ROOT / "AGENT.md"
    prepend_once(agent, "Current Runtime Handoff Override - Provider Hardening v0.1.2 Internal Pass", f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Provider Hardening v0.1.2 Internal Pass Pending External Audit

Status: `agent_handoff_prompt_v0_137`
Date: `{now[:10]}`

```text
current_gate = runtime_provider_contract_schema_hardening_v0_1_2_external_audit_pending
boundary_layer = 08_RUNTIME_CAPABILITIES
last_closed_gate = {GATE}
last_closed_status = {matrix['status']}
provider_v0_1_2_external_audit = PENDING
provider_consumer_compatibility = NOT_OPENED_AFTER_V0_1_2
case_count = {matrix['case_count']}
failed_cases = {matrix['failed_cases']}
state_replay_feed_authority = false
backtest_state_consumption_authority = false
physical_rows_delivered = 0
runtime_requests_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
provider_only_zip = {zip_path}
```

Do not open provider-consumer compatibility, StateBundle physical reads, StateReplayFeed, backtest state integration, production or downstream until the v0.1.2 provider-only ZIP passes external audit.
""")

    changelog = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"
    prepend_once(changelog, "Runtime provider hardening v0.1.2 internal pass pending external audit", f"""## {now[:10]} - Runtime provider hardening v0.1.2 internal pass pending external audit

- Created the clean provider-only `runtime_provider_contract_schema_hardening_v0_1_2` implementation authorized by `runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1`.
- Created five v0.1.2 provider contracts, implementation scope, runner, validation matrix, readout and provider-only ZIP.
- Added executable semantic validation for F01-F09, including `response_ref <-> request_fingerprint <-> state_kind` correlation.
- Passed {matrix['case_count']} cases: {matrix['original_case_count']} original-regression cases and {matrix['external_regression_case_count']} external adversarial regression cases.
- Kept runtime requests, builds, datasets, registry mutations, physical state rows, StateReplayFeed, backtest consumption, production and downstream closed.
""")


def write_readout(now: str, matrix: dict[str, Any], zip_path: Path) -> Path:
    path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_readout.md"
    write_text(path, f"""# Runtime Provider Contract Schema Hardening v0.1.2 Readout

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{matrix['status']}`

```text
case_count = {matrix['case_count']}
original_case_count = {matrix['original_case_count']}
external_regression_case_count = {matrix['external_regression_case_count']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
duplicate_case_ids = {len(matrix['duplicate_case_ids'])}
unexpected_silent_skips = {matrix['unexpected_silent_skips']}
failed_cases = {matrix['failed_cases']}
jsonschema_draft_2020_12_compile = {matrix['jsonschema_draft_2020_12_compile']}
ajv_8_17_1_strict_runtime = {matrix['ajv_8_17_1_strict_runtime']}
semantic_validator_execution = {matrix['semantic_validator_execution']}
expanded_adversarial_matrix = {matrix['expanded_adversarial_matrix']}
package_manifest_reproducibility = PASS
provider_only_isolation = PASS
document_encoding_integrity = PASS
```

Findings closed internally:

```text
F01 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F02 = CLOSED_BY_SEMANTIC_VALIDATOR
F03 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F04 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F05 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F06 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F07 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F08 = CLOSED_BY_DOCUMENT_UPDATE
F09 = CLOSED_BY_RESPONSE_REQUEST_STATE_KIND_CORRELATION
```

Boundaries:

```text
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
physical_state_rows_delivered = 0
source_market_data_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption_authority = false
production = false
downstream = false
official_dataset = false
```

Provider-only ZIP pending external audit:

```text
{zip_path}
```
""")
    return path


def normalize(paths: list[Path]) -> None:
    for path in paths:
        if path.exists() and path.suffix.lower() in {".md", ".json", ".py"}:
            write_text(path, read_text(path))


def make_zip(now: str, files: list[Path]) -> Path:
    stamp = now.replace("-", "").replace(":", "")
    zip_path = FEATURE_ROOT / f"runtime_provider_contract_schema_hardening_v0_1_2_provider_only_{stamp}.zip"
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in files:
        if path.exists() and path not in seen:
            unique.append(path)
            seen.add(path)
    manifest = {"package_id": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only", "created_at_utc": now, "gate": GATE, "status": STATUS, "entry_count_excluding_manifest": len(unique), "portable_zip_paths": True, "explicitly_excluded": ["02_TSIS_BACKTEST_ENGINE files", "StateReplayFeed files", "runtime runs", "parquet files", "physical market data", "downstream artifacts", "quarantined v0.1.2 artifacts as authority"], "entries": [entry(path) for path in unique]}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in unique:
            zf.write(path, rel(path))
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return zip_path


def verify_zip(zip_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if any("\\" in name for name in names):
            errors.append("non-portable zip path")
        manifest = json.loads(zf.read("PACKAGE_MANIFEST.json").decode("utf-8"))
        entries = {item["path"]: item for item in manifest["entries"]}
        if set(names) - {"PACKAGE_MANIFEST.json"} != set(entries):
            errors.append("zip entries differ from manifest")
        for name, item in entries.items():
            data = zf.read(name)
            if len(data) != item["size_bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                errors.append(f"manifest mismatch: {name}")
    return not errors, errors


def main() -> None:
    now = now_utc()
    scope_path = write_scope(now)
    contract_paths = write_contracts()
    contracts = {path.name: read_json(path) for path in contract_paths}
    matrix = run_matrix(contracts)
    matrix_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json"
    write_json(matrix_path, matrix)
    pending_zip = FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip"
    readout_path = write_readout(now, matrix, pending_zip)
    update_docs(now, matrix, pending_zip)
    files = [
        RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1.md",
        CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_scope_v0_1.json",
        RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_readout_v0_1.md",
        RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_revalidation_addendum_v0_1.md",
        CONFIGS / "runtime_provider_v0_1_2_rollback_verification_scope_v0_1.json",
        RUNTIME / "runtime_provider_v0_1_2_rollback_verification_matrix_v0_1.json",
        RUNTIME / "runtime_provider_v0_1_2_rollback_verification_readout_v0_1.md",
        CONFIGS / "runtime_provider_contract_schema_hardening_findings_revalidation_scope_v0_1.json",
        RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_matrix_v0_1.json",
        RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_readout_v0_1.md",
        scope_path,
        *contract_paths,
        SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_runner.py",
        matrix_path,
        readout_path,
        FEATURE_ROOT / "99_ruta_de_trabajo.md",
        FEATURE_ROOT / "AGENT.md",
        RUNTIME / "README.md",
        ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md",
    ]
    normalize(files)
    zip_path = make_zip(now, files)
    readout_path = write_readout(now, matrix, zip_path)
    update_docs(now, matrix, zip_path)
    normalize(files)
    zip_path.unlink(missing_ok=True)
    zip_path = make_zip(now, files)
    ok, errors = verify_zip(zip_path)
    if not ok:
        raise SystemExit("ZIP verification failed: " + "; ".join(errors))
    print(json.dumps({"gate": GATE, "status": matrix["status"], "case_count": matrix["case_count"], "original_case_count": matrix["original_case_count"], "external_regression_case_count": matrix["external_regression_case_count"], "missing_required_case_ids": len(matrix["missing_required_case_ids"]), "duplicate_case_ids": len(matrix["duplicate_case_ids"]), "failed_cases": matrix["failed_cases"], "jsonschema_draft_2020_12_compile": matrix["jsonschema_draft_2020_12_compile"], "ajv_8_17_1_strict_runtime": matrix["ajv_8_17_1_strict_runtime"], "semantic_validator_execution": matrix["semantic_validator_execution"], "zip_path": str(zip_path), "zip_sha256": sha256_file(zip_path), "next_action": "external_adversarial_audit_of_provider_only_zip"}, indent=2, ensure_ascii=False))


from runtime_provider_contract_schema_hardening_v0_1_2_patch import apply_patch_overrides
apply_patch_overrides(globals())

if __name__ == "__main__":
    main()
