from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering")
RUNTIME = ROOT / "08_RUNTIME_CAPABILITIES"
CONFIGS = RUNTIME / "configs"

FORBIDDEN_KEYS = [
    "physical_path",
    "physical_data_path",
    "source_parquet_file",
    "source_parquet_path",
    "market_state_candidate_parquet_path",
    "market_state_candidate_path",
    "event_state_output_path",
    "temporary_output_directory",
    "resolved_partition_path",
    "builder_implementation",
    "materializer_implementation",
    "validator_implementation",
    "dataset_registry_id",
    "machine_specific_state",
]

CANON = {
    "canonicalization_algorithm": "recursive_lexicographic_key_sort_then_json_compact",
    "encoding": "utf-8-no-bom",
    "line_endings_for_file": "LF",
    "hash_input_line_endings": "none_json_compact_single_line",
    "property_order_policy": "sort_object_keys_lexicographically_at_every_depth",
    "array_order_policy": "preserve_contractual_array_order",
    "final_newline_in_hash_input": False,
    "hash_scope": "entire_json_document_excluding_contract_content_sha256_excluding_hash_field",
    "hash_algorithm": "sha256",
}


def sort_obj(obj):
    if isinstance(obj, dict):
        return {k: sort_obj(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [sort_obj(x) for x in obj]
    return obj


def without_field(obj, field):
    if isinstance(obj, dict):
        return {k: without_field(v, field) for k, v in obj.items() if k != field}
    if isinstance(obj, list):
        return [without_field(x, field) for x in obj]
    return obj


def canonical_hash(obj, field="contract_content_sha256_excluding_hash_field"):
    payload = sort_obj(without_field(obj, field))
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return sha256(data.encode("utf-8")).hexdigest()


def write_json(path: Path, obj: dict, hash_field="contract_content_sha256_excluding_hash_field"):
    obj[hash_field] = "PENDING"
    obj[hash_field] = canonical_hash(obj, hash_field)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_md(path: Path, text: str):
    path.write_text(text.strip() + "\n", encoding="utf-8")


def s():
    return {"type": "string", "minLength": 1}


def arr(min_items=0, max_items=None, const_item=None):
    schema = {"type": "array", "minItems": min_items, "items": {"type": "string"}}
    if max_items is not None:
        schema["maxItems"] = max_items
    if const_item is not None:
        schema["items"] = {"const": const_item}
    return schema


def enum(*vals):
    return {"enum": list(vals)}


def ref(kind=None):
    props = {
        "ref_id": s(),
        "ref_type": {"const": kind} if kind else s(),
        "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "availability": enum("available", "archived", "missing", "not_required"),
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["ref_id", "ref_type", "sha256", "availability"],
        "properties": props,
    }


def dataset_ref(kind):
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "dataset_id",
            "dataset_kind",
            "candidate_dataset_fingerprint",
            "validation_status",
            "reuse_eligibility",
            "artifact_availability",
        ],
        "properties": {
            "dataset_id": s(),
            "dataset_kind": {"const": kind},
            "candidate_dataset_fingerprint": {"type": "string", "pattern": "^[a-f0-9]{16,64}$"},
            "validation_status": enum("PASS", "PASS_WITH_RESTRICTIONS"),
            "reuse_eligibility": enum("eligible", "eligible_with_restrictions", "pending_policy_review"),
            "artifact_availability": enum("available", "archived"),
        },
    }


def reject_forbidden():
    return {"not": {"anyOf": [{"required": [k]} for k in FORBIDDEN_KEYS]}}


market_fields = {
    "request_type": {"const": "market_state"},
    "request_contract_version": s(),
    "request_id": s(),
    "requested_at_utc": s(),
    "requested_by": s(),
    "request_purpose": s(),
    "profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"},
    "profile_version_policy": {"const": "exact"},
    "profile_version": s(),
    "resolution": s(),
    "grain": s(),
    "universe_definition_id": {"type": ["string", "null"]},
    "explicit_instrument_ids": arr(),
    "universe_selection_mode": s(),
    "instrument_filter_mode": s(),
    "start_date": {"type": ["string", "null"]},
    "end_date": {"type": ["string", "null"]},
    "session_dates": arr(),
    "calendar_authority_id": s(),
    "exchange_scope": s(),
    "point_in_time_policy_id": s(),
    "as_of_policy_id": s(),
    "source_version_policy": {"const": "exact_governed_or_block"},
    "output_mode": {"const": "candidate"},
    "output_format": s(),
    "partition_policy": s(),
    "validation_level": s(),
    "reuse_policy": enum("reuse_if_exact_validated_match", "force_rebuild_only_when_authorized"),
}

event_fields = {
    "request_type": {"const": "event_state"},
    "request_contract_version": s(),
    "request_id": s(),
    "requested_at_utc": s(),
    "requested_by": s(),
    "request_purpose": s(),
    "event_state_profile_id": {"const": "event_state_core_four_intraday_profile_v0_1"},
    "event_state_profile_version_policy": {"const": "exact"},
    "event_state_profile_version": s(),
    "resolution": s(),
    "grain": s(),
    "event_type_ids": arr(1, 1, "event_type:market_data:session_opened"),
    "event_type_registry_snapshot_policy": {"const": "exact"},
    "event_type_registry_snapshot_id": s(),
    "event_subject_scope": {"const": "exchange_session"},
    "event_instance_policy_id": s(),
    "event_anchor_policy_id": s(),
    "event_window_policy_id": s(),
    "event_window_definition_ids": arr(1),
    "instrument_projection_policy_id": s(),
    "universe_definition_id": {"type": ["string", "null"]},
    "explicit_instrument_ids": arr(),
    "universe_selection_mode": s(),
    "instrument_filter_mode": s(),
    "exchange_scope": s(),
    "start_date": {"type": ["string", "null"]},
    "end_date": {"type": ["string", "null"]},
    "session_dates": arr(),
    "market_state_dependency_mode": {"const": "emit_or_resolve_market_state_subrequest_through_runtime_capability"},
    "market_state_profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"},
    "market_state_profile_version_policy": {"const": "exact"},
    "market_state_profile_version": s(),
    "market_state_capability_policy_id": s(),
    "market_state_dependency_reuse_policy": enum("reuse_if_exact_validated_dependency_match", "force_rebuild_only_when_authorized"),
    "calendar_authority_id": s(),
    "point_in_time_policy_id": s(),
    "as_of_policy_id": s(),
    "source_version_policy": {"const": "exact_governed_or_block"},
    "output_mode": {"const": "candidate"},
    "output_format": s(),
    "partition_policy": s(),
    "validation_level": s(),
    "reuse_policy": enum("reuse_if_exact_validated_dependency_match", "force_rebuild_only_when_authorized"),
}

market_schema = {
    "type": "object",
    "additionalProperties": False,
    "required": list(market_fields),
    "properties": market_fields,
    "allOf": [reject_forbidden()],
}

event_schema = {
    "type": "object",
    "additionalProperties": False,
    "required": list(event_fields),
    "properties": event_fields,
    "allOf": [reject_forbidden()],
}

state_resolution_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://tsis.local/contracts/state_resolution_request_contract_v0_1.schema.json",
    "title": "TSIS StateResolutionRequest v0.1 hardened",
    "type": "object",
    "additionalProperties": False,
    "required": ["request_type", "request_contract_version", "consumer", "consumption_purpose", "resolution_policy", "payload"],
    "properties": {
        "request_type": enum("market_state", "event_state"),
        "request_contract_version": {"const": "0.1.0"},
        "consumer": s(),
        "consumption_purpose": enum("planning", "backtest", "research", "validation"),
        "resolution_policy": {
            "type": "object",
            "additionalProperties": False,
            "required": ["mode", "reuse_policy", "allow_new_candidate_execution", "allow_physical_path_input"],
            "properties": {
                "mode": enum("validate_only", "resolve_reuse_or_authorization", "invoke_with_authorization"),
                "reuse_policy": enum("metadata_only", "reuse_if_exact_validated_match", "reuse_if_exact_validated_match_or_authorization_required"),
                "allow_new_candidate_execution": {"type": "boolean", "const": False},
                "allow_physical_path_input": {"type": "boolean", "const": False},
            },
        },
        "payload": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "market_state_request": market_schema,
                "event_state_request": event_schema,
            },
        },
    },
    "allOf": [
        {
            "if": {"properties": {"request_type": {"const": "market_state"}}, "required": ["request_type"]},
            "then": {
                "properties": {
                    "payload": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["market_state_request"],
                        "properties": {"market_state_request": market_schema},
                        "not": {"required": ["event_state_request"]},
                    }
                }
            },
        },
        {
            "if": {"properties": {"request_type": {"const": "event_state"}}, "required": ["request_type"]},
            "then": {
                "properties": {
                    "payload": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["event_state_request"],
                        "properties": {"event_state_request": event_schema},
                        "not": {"required": ["market_state_request"]},
                    }
                }
            },
        },
    ],
}

state_resolution_contract = {
    "contract_id": "state_resolution_request_contract_v0_1",
    "contract_version": "0.1.1-hardened",
    "status": "PROVIDER_CONTRACT_SCHEMA_HARDENED_NO_EXECUTION",
    "owner_layer": "08_RUNTIME_CAPABILITIES",
    "purpose": "Common provider envelope for requesting governed Market State or Event State resolution.",
    "schema_hardening_gate": "runtime_provider_contract_schema_hardening_v0_1",
    "canonicalization_policy": CANON,
    "request_hierarchy": {
        "state_resolution_request": "common_provider_envelope",
        "market_state_request": "specialized_payload",
        "event_state_request": "specialized_payload",
        "backtest_run_spec": "consumer_owned_projection_source",
    },
    "json_schema": state_resolution_schema,
    "specialized_payloads": {
        "market_state_request": {"governed_by": "market_state_request_contract_v0_1.json", "included_in_review_package": True, "physical_paths_allowed": False},
        "event_state_request": {"governed_by": "event_state_request_contract_v0_1.json", "included_in_review_package": True, "allowed_event_type_ids": ["event_type:market_data:session_opened"], "accepted_subject_scope": "exchange_session", "physical_market_state_path_allowed": False},
    },
    "non_schema_fail_closed_checks_required": [
        "recursive_forbidden_key_scan_for_path_like_or_runtime_implementation_fields",
        "payload_validation_against_specialized_contract_authority",
        "request_fingerprint_canonicalization_check",
    ],
    "hard_boundaries": {
        "request_validation_allowed": True,
        "request_normalization_allowed": True,
        "request_fingerprint_creation_allowed": True,
        "registry_metadata_lookup_allowed": True,
        "exact_reuse_resolution_allowed_under_policy": True,
        "new_candidate_execution_allowed_without_authorization": False,
        "physical_path_input_allowed": False,
        "physical_row_delivery_allowed": False,
        "official_dataset_delivery_allowed": False,
        "downstream_data_delivery_allowed": False,
    },
}
write_json(RUNTIME / "state_resolution_request_contract_v0_1.json", state_resolution_contract)

response_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://tsis.local/contracts/runtime_user_invocation_response_contract_v0_1.schema.json",
    "title": "TSIS RuntimeInvocationResponse v0.1 hardened",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "invocation_id", "request_type", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id",
        "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "state_bundle_manifest_ref",
        "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream",
        "market_state_details", "event_state_details", "authorization_ref",
    ],
    "properties": {
        "invocation_id": s(),
        "request_type": enum("market_state", "event_state"),
        "request_fingerprint": {"type": "string", "minLength": 16},
        "invocation_status": enum("blocked", "reuse_hit", "authorization_required", "authorized_reference"),
        "resolution_decision": enum(
            "VALID_REQUEST_REUSE_HIT",
            "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED",
            "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE",
            "BLOCKED_INVALID_REQUEST",
            "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE",
            "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED",
            "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED",
            "BLOCKED_PROVIDER_CONTRACT_MISMATCH",
        ),
        "capability_id": s(),
        "profile_id": {"type": ["string", "null"]},
        "run_id": {"type": ["string", "null"]},
        "dataset_id": {"type": ["string", "null"]},
        "dataset_status": {"type": ["string", "null"]},
        "validation_status": {"type": ["string", "null"]},
        "state_bundle_manifest_ref": {"oneOf": [ref("state_bundle_manifest"), {"type": "null"}]},
        "coverage": {"type": "object", "additionalProperties": True},
        "restrictions": {"type": "array", "items": {"type": "string"}},
        "artifact_references": {"type": "array", "items": ref()},
        "official_dataset": {"type": "boolean", "const": False},
        "production": {"type": "boolean", "const": False},
        "downstream": {"type": "boolean", "const": False},
        "market_state_details": {"type": ["object", "null"]},
        "event_state_details": {"type": ["object", "null"]},
        "authorization_ref": {"oneOf": [ref("execution_authorization"), {"type": "null"}]},
    },
    "allOf": [
        {"if": {"properties": {"invocation_status": {"const": "blocked"}}, "required": ["invocation_status"]}, "then": {"properties": {"resolution_decision": {"enum": ["BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": {"type": "null"}, "artifact_references": {"type": "array", "maxItems": 0}}}},
        {"if": {"properties": {"invocation_status": {"const": "reuse_hit"}}, "required": ["invocation_status"]}, "then": {"properties": {"resolution_decision": {"const": "VALID_REQUEST_REUSE_HIT"}, "dataset_id": s(), "dataset_status": {"const": "validated_candidate"}, "validation_status": enum("PASS", "PASS_WITH_RESTRICTIONS"), "state_bundle_manifest_ref": ref("state_bundle_manifest"), "artifact_references": {"type": "array", "minItems": 1, "items": ref()}, "authorization_ref": {"type": "null"}}}},
        {"if": {"properties": {"invocation_status": {"const": "authorization_required"}}, "required": ["invocation_status"]}, "then": {"properties": {"resolution_decision": {"const": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": {"type": "null"}}}},
        {"if": {"properties": {"invocation_status": {"const": "authorized_reference"}}, "required": ["invocation_status"]}, "then": {"properties": {"resolution_decision": {"const": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref": {"type": "null"}, "authorization_ref": ref("execution_authorization")}}},
    ],
}

response_contract = {
    "contract_id": "runtime_user_invocation_response_contract_v0_1",
    "contract_version": "0.1.1-hardened",
    "status": "PROVIDER_CONTRACT_SCHEMA_HARDENED_NO_EXECUTION",
    "owner_layer": "08_RUNTIME_CAPABILITIES",
    "purpose": "Common response envelope returned by the provider-side runtime invocation interface.",
    "schema_hardening_gate": "runtime_provider_contract_schema_hardening_v0_1",
    "canonicalization_policy": CANON,
    "json_schema": response_schema,
    "response_semantics": {
        "successful_reference_does_not_authorize_row_delivery": True,
        "reuse_hit_requires_state_bundle_manifest_ref": True,
        "blocked_response_must_not_create_dataset": True,
        "blocked_response_must_not_return_artifacts": True,
        "downstream_consumption_requires_future_separate_authorization": True,
    },
}
write_json(RUNTIME / "runtime_user_invocation_response_contract_v0_1.json", response_contract)

bundle_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://tsis.local/contracts/state_bundle_manifest_contract_v0_1.schema.json",
    "title": "TSIS StateBundleManifest v0.1 hardened",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "state_bundle_manifest_id", "bundle_state_mode", "state_kinds", "request_fingerprints", "state_resolution_request_refs",
        "runtime_invocation_response_ref", "capability_refs", "dataset_refs", "coverage", "validation_status", "restrictions",
        "representation_profile_versions", "schema_fingerprints", "source_dataset_ids", "source_content_hashes", "artifact_hashes",
        "field_lineage", "temporal_policy", "materialization_status", "consumption_authorization", "official_dataset", "production", "downstream", "physical_rows_delivered",
    ],
    "properties": {
        "state_bundle_manifest_id": s(),
        "bundle_state_mode": enum("market_state_only", "event_state_only", "market_and_event"),
        "state_kinds": {"type": "array", "minItems": 1, "uniqueItems": True, "items": enum("market_state", "event_state")},
        "request_fingerprints": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 16}},
        "state_resolution_request_refs": {"type": "array", "minItems": 1, "items": ref("state_resolution_request")},
        "runtime_invocation_response_ref": ref("runtime_invocation_response"),
        "capability_refs": {"type": "array", "minItems": 1, "items": ref("runtime_capability")},
        "dataset_refs": {
            "type": "object",
            "additionalProperties": False,
            "required": ["market_state_dataset_ref", "event_state_dataset_ref"],
            "properties": {"market_state_dataset_ref": {"oneOf": [dataset_ref("market_state"), {"type": "null"}]}, "event_state_dataset_ref": {"oneOf": [dataset_ref("event_state"), {"type": "null"}]}},
        },
        "coverage": {"type": "object", "additionalProperties": False, "required": ["requested_contexts", "represented_contexts", "unavailable_contexts", "blocked_contexts", "quarantined_contexts", "unaccounted_contexts"], "properties": {"requested_contexts": {"type": "integer", "minimum": 1}, "represented_contexts": {"type": "integer", "minimum": 0}, "unavailable_contexts": {"type": "integer", "minimum": 0}, "blocked_contexts": {"type": "integer", "minimum": 0}, "quarantined_contexts": {"type": "integer", "minimum": 0}, "unaccounted_contexts": {"type": "integer", "minimum": 0}}},
        "validation_status": enum("PASS", "PASS_WITH_RESTRICTIONS", "BLOCKED", "FAIL", "NOT_EXECUTED"),
        "restrictions": {"type": "array", "items": {"type": "string"}},
        "representation_profile_versions": {"type": "array", "minItems": 1, "items": {"type": "object"}},
        "schema_fingerprints": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "source_dataset_ids": {"type": "array", "items": {"type": "string"}},
        "source_content_hashes": {"type": "array", "items": {"type": "string"}},
        "artifact_hashes": {"type": "array", "minItems": 1, "items": {"type": "object"}},
        "field_lineage": {"type": "array", "items": {"type": "object"}},
        "temporal_policy": {"type": "object"},
        "materialization_status": s(),
        "consumption_authorization": {"type": "object", "additionalProperties": False, "required": ["backtest_consumption_authorized", "downstream_authorized", "consumption_purposes"], "properties": {"backtest_consumption_authorized": {"type": "boolean", "const": False}, "downstream_authorized": {"type": "boolean", "const": False}, "consumption_purposes": {"type": "array", "maxItems": 0}}},
        "official_dataset": {"type": "boolean", "const": False},
        "production": {"type": "boolean", "const": False},
        "downstream": {"type": "boolean", "const": False},
        "physical_rows_delivered": {"type": "boolean", "const": False},
    },
    "allOf": [
        {"if": {"properties": {"bundle_state_mode": {"const": "market_state_only"}}, "required": ["bundle_state_mode"]}, "then": {"properties": {"state_kinds": {"prefixItems": [{"const": "market_state"}], "minItems": 1, "maxItems": 1}, "dataset_refs": {"properties": {"market_state_dataset_ref": dataset_ref("market_state"), "event_state_dataset_ref": {"type": "null"}}}}}},
        {"if": {"properties": {"bundle_state_mode": {"const": "event_state_only"}}, "required": ["bundle_state_mode"]}, "then": {"properties": {"state_kinds": {"prefixItems": [{"const": "event_state"}], "minItems": 1, "maxItems": 1}, "dataset_refs": {"properties": {"market_state_dataset_ref": {"type": "null"}, "event_state_dataset_ref": dataset_ref("event_state")}}}}},
        {"if": {"properties": {"bundle_state_mode": {"const": "market_and_event"}}, "required": ["bundle_state_mode"]}, "then": {"properties": {"state_kinds": {"allOf": [{"contains": {"const": "market_state"}}, {"contains": {"const": "event_state"}}], "minItems": 2, "maxItems": 2}, "request_fingerprints": {"minItems": 2}, "state_resolution_request_refs": {"minItems": 2}, "dataset_refs": {"properties": {"market_state_dataset_ref": dataset_ref("market_state"), "event_state_dataset_ref": dataset_ref("event_state")}}}}},
        {"if": {"properties": {"validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}}, "required": ["validation_status"]}, "then": {"properties": {"capability_refs": {"minItems": 1}, "artifact_hashes": {"minItems": 1}, "schema_fingerprints": {"minItems": 1}}}},
    ],
}

bundle_contract = {
    "contract_id": "state_bundle_manifest_contract_v0_1",
    "contract_version": "0.1.1-hardened",
    "status": "PROVIDER_CONTRACT_SCHEMA_HARDENED_NO_EXECUTION",
    "owner_layer": "08_RUNTIME_CAPABILITIES",
    "purpose": "Provider-owned manifest that seals the state datasets/references returned to an institutional consumer preflight.",
    "schema_hardening_gate": "runtime_provider_contract_schema_hardening_v0_1",
    "canonicalization_policy": CANON,
    "json_schema": bundle_schema,
    "cardinality_decision": {
        "decision": "aggregate_bundle_supported",
        "meaning": "One StateBundleManifest may seal one or more StateResolutionRequests via request_fingerprints and state_resolution_request_refs.",
        "supported_modes": ["market_state_only", "event_state_only", "market_and_event"],
    },
    "coverage_validation_policy": {
        "json_schema_enforces_non_negative_counts_and_required_fields": True,
        "code_validator_must_enforce": "requested_contexts = represented_contexts + unavailable_contexts + blocked_contexts + quarantined_contexts + unaccounted_contexts and represented_contexts <= requested_contexts",
    },
    "relationship_to_backtest": {"backtest_input_manifest_may_reference_state_bundle": True, "backtester_must_not_redefine_state_bundle_schema": True, "state_replay_feed_not_authorized_by_this_contract": True},
    "hard_boundaries": {"backtest_consumption_authority": False, "physical_row_delivery_allowed": False, "official_dataset": False, "production": False, "downstream": False},
}
write_json(RUNTIME / "state_bundle_manifest_contract_v0_1.json", bundle_contract)

scope = {
    "scope_id": "runtime_provider_contract_schema_hardening_scope_v0_1",
    "gate": "runtime_provider_contract_schema_hardening_v0_1",
    "status": "HARDENING_SCOPE_CLOSED_NO_EXECUTION",
    "created_at_utc": "2026-07-28T00:00:00Z",
    "owner_layer": "08_RUNTIME_CAPABILITIES",
    "hardened_contracts": ["state_resolution_request_contract_v0_1.json", "runtime_user_invocation_response_contract_v0_1.json", "state_bundle_manifest_contract_v0_1.json"],
    "included_specialized_contract_authorities": ["market_state_request_contract_v0_1.json", "event_state_request_contract_v0_1.json"],
    "hard_boundaries": {"runtime_executions": 0, "market_state_requests_created": 0, "event_state_requests_created": 0, "state_bundle_manifests_created": 0, "datasets_written": 0, "registry_mutations": 0, "backtest_runs_created": 0, "state_replay_feed_opened": False, "official_dataset": False, "production": False, "downstream": False},
}
write_json(CONFIGS / "runtime_provider_contract_schema_hardening_scope_v0_1.json", scope)

write_md(RUNTIME / "runtime_provider_contract_schema_hardening_authorization_v0_1.md", """
# runtime_provider_contract_schema_hardening_authorization_v0_1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`
Gate: `runtime_provider_contract_schema_hardening_v0_1`
Owner layer: `08_RUNTIME_CAPABILITIES`

## Purpose

This gate corrects provider-side schema weaknesses found during provider-consumer compatibility preflight.

It hardens only provider contracts. It does not open runtime execution, backtest consumption, `StateReplayFeed`, production, downstream or official dataset delivery.

## Authorized corrections

```text
state_resolution_request_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
```

## Closed boundaries

```text
runtime_executions = 0
state_bundle_manifests_created = 0
datasets_written = 0
registry_mutations = 0
backtest_runs_created = 0
StateReplayFeed_opened = false
official_dataset = false
production = false
downstream = false
```
""")


def validate(schema, instance):
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    return not errors, [e.message for e in errors[:5]]


valid_market = {
    "request_type": "market_state", "request_contract_version": "0.1.0", "request_id": "req_m", "requested_at_utc": "2026-07-28T00:00:00Z", "requested_by": "test", "request_purpose": "validation",
    "profile_id": "market_state_core_four_intraday_profile_v0_1", "profile_version_policy": "exact", "profile_version": "0.1", "resolution": "1m", "grain": "instrument_session",
    "universe_definition_id": None, "explicit_instrument_ids": ["AAME"], "universe_selection_mode": "explicit", "instrument_filter_mode": "none", "start_date": None, "end_date": None, "session_dates": ["2021-01-19"],
    "calendar_authority_id": "XNYS_calendar_v0_1", "exchange_scope": "XNYS", "point_in_time_policy_id": "pit_v0_1", "as_of_policy_id": "asof_v0_1", "source_version_policy": "exact_governed_or_block",
    "output_mode": "candidate", "output_format": "jsonl", "partition_policy": "logical_context", "validation_level": "strict", "reuse_policy": "reuse_if_exact_validated_match",
}
valid_event = {
    "request_type": "event_state", "request_contract_version": "0.1.0", "request_id": "req_e", "requested_at_utc": "2026-07-28T00:00:00Z", "requested_by": "test", "request_purpose": "validation",
    "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1", "event_state_profile_version_policy": "exact", "event_state_profile_version": "0.1", "resolution": "1m", "grain": "instrument_session_event",
    "event_type_ids": ["event_type:market_data:session_opened"], "event_type_registry_snapshot_policy": "exact", "event_type_registry_snapshot_id": "snapshot", "event_subject_scope": "exchange_session",
    "event_instance_policy_id": "event_instance_policy_v0_1", "event_anchor_policy_id": "anchor_v0_1", "event_window_policy_id": "window_v0_1", "event_window_definition_ids": ["session_opened_at_anchor_context_v0_1"],
    "instrument_projection_policy_id": "projection_v0_1", "universe_definition_id": None, "explicit_instrument_ids": ["AAME"], "universe_selection_mode": "explicit", "instrument_filter_mode": "none", "exchange_scope": "XNYS", "start_date": None, "end_date": None, "session_dates": ["2021-01-19"],
    "market_state_dependency_mode": "emit_or_resolve_market_state_subrequest_through_runtime_capability", "market_state_profile_id": "market_state_core_four_intraday_profile_v0_1", "market_state_profile_version_policy": "exact", "market_state_profile_version": "0.1", "market_state_capability_policy_id": "market_state_capability_consumption_policy_v0_1", "market_state_dependency_reuse_policy": "reuse_if_exact_validated_dependency_match",
    "calendar_authority_id": "XNYS_calendar_v0_1", "point_in_time_policy_id": "pit_v0_1", "as_of_policy_id": "asof_v0_1", "source_version_policy": "exact_governed_or_block", "output_mode": "candidate", "output_format": "jsonl", "partition_policy": "logical_context", "validation_level": "strict", "reuse_policy": "reuse_if_exact_validated_dependency_match",
}
base_req = {"request_type": "market_state", "request_contract_version": "0.1.0", "consumer": "backtest_runpreflight", "consumption_purpose": "backtest", "resolution_policy": {"mode": "resolve_reuse_or_authorization", "reuse_policy": "reuse_if_exact_validated_match", "allow_new_candidate_execution": False, "allow_physical_path_input": False}, "payload": {"market_state_request": valid_market}}
base_resp_blocked = {"invocation_id": "inv1", "request_type": "market_state", "request_fingerprint": "abcdef0123456789", "invocation_status": "blocked", "resolution_decision": "BLOCKED_INVALID_REQUEST", "capability_id": "cap", "profile_id": None, "run_id": None, "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "coverage": {}, "restrictions": ["blocked"], "artifact_references": [], "official_dataset": False, "production": False, "downstream": False, "market_state_details": None, "event_state_details": None, "authorization_ref": None}
ref_bundle = {"ref_id": "bundle1", "ref_type": "state_bundle_manifest", "sha256": "a" * 64, "availability": "available"}
ref_artifact = {"ref_id": "art1", "ref_type": "validation_report", "sha256": "b" * 64, "availability": "available"}
valid_reuse = deepcopy(base_resp_blocked)
valid_reuse.update({"invocation_status": "reuse_hit", "resolution_decision": "VALID_REQUEST_REUSE_HIT", "dataset_id": "ds1", "dataset_status": "validated_candidate", "validation_status": "PASS", "state_bundle_manifest_ref": ref_bundle, "artifact_references": [ref_artifact], "restrictions": []})
valid_bundle = {"state_bundle_manifest_id": "bundle1", "bundle_state_mode": "market_state_only", "state_kinds": ["market_state"], "request_fingerprints": ["abcdef0123456789"], "state_resolution_request_refs": [{"ref_id": "req", "ref_type": "state_resolution_request", "sha256": "c" * 64, "availability": "available"}], "runtime_invocation_response_ref": {"ref_id": "resp", "ref_type": "runtime_invocation_response", "sha256": "d" * 64, "availability": "available"}, "capability_refs": [{"ref_id": "cap", "ref_type": "runtime_capability", "sha256": "e" * 64, "availability": "available"}], "dataset_refs": {"market_state_dataset_ref": {"dataset_id": "ds1", "dataset_kind": "market_state", "candidate_dataset_fingerprint": "f" * 64, "validation_status": "PASS", "reuse_eligibility": "eligible", "artifact_availability": "available"}, "event_state_dataset_ref": None}, "coverage": {"requested_contexts": 1, "represented_contexts": 1, "unavailable_contexts": 0, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS", "restrictions": [], "representation_profile_versions": [{}], "schema_fingerprints": ["schema"], "source_dataset_ids": [], "source_content_hashes": [], "artifact_hashes": [{}], "field_lineage": [], "temporal_policy": {}, "materialization_status": "validated_candidate", "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}


def coverage_check(inst):
    c = inst.get("coverage", {})
    lhs = c.get("requested_contexts")
    rhs = sum(c.get(k, 0) for k in ["represented_contexts", "unavailable_contexts", "blocked_contexts", "quarantined_contexts", "unaccounted_contexts"])
    if lhs != rhs or c.get("represented_contexts", 0) > lhs:
        return False, ["coverage arithmetic failed"]
    return True, []


cases = []


def add_case(case_id, schema, instance, expected_valid, custom_check=None):
    ok, errors = validate(schema, instance)
    custom_ok, custom_errors = (True, [])
    if custom_check:
        custom_ok, custom_errors = custom_check(instance)
    actual = ok and custom_ok
    cases.append({"case_id": case_id, "schema_valid": ok, "custom_valid": custom_ok, "expected_valid": expected_valid, "result": "PASS" if actual == expected_valid else "FAIL", "schema_errors": errors, "custom_errors": custom_errors})


add_case("valid_market_state_resolution_request", state_resolution_schema, base_req, True)
wrong_payload = deepcopy(base_req)
wrong_payload["payload"] = {"event_state_request": valid_event}
add_case("market_request_with_event_payload_rejected", state_resolution_schema, wrong_payload, False)
physical = deepcopy(base_req)
physical["payload"]["market_state_request"]["physical_path"] = "C:/forbidden.parquet"
add_case("payload_physical_path_rejected", state_resolution_schema, physical, False)
accepted_blocked = deepcopy(base_resp_blocked)
accepted_blocked["invocation_status"] = "accepted"
add_case("accepted_status_rejected", response_schema, accepted_blocked, False)
reuse_missing_bundle = deepcopy(valid_reuse)
reuse_missing_bundle["state_bundle_manifest_ref"] = None
add_case("reuse_hit_without_bundle_rejected", response_schema, reuse_missing_bundle, False)
blocked_with_dataset = deepcopy(base_resp_blocked)
blocked_with_dataset["dataset_id"] = "ds_bad"
add_case("blocked_response_with_dataset_rejected", response_schema, blocked_with_dataset, False)
empty_cap = deepcopy(valid_bundle)
empty_cap["capability_refs"] = []
add_case("pass_bundle_empty_capability_refs_rejected", bundle_schema, empty_cap, False, coverage_check)
bad_cov = deepcopy(valid_bundle)
bad_cov["coverage"]["represented_contexts"] = 2
add_case("bundle_coverage_arithmetic_rejected_by_code_validator", bundle_schema, bad_cov, False, coverage_check)
add_case("valid_reuse_response", response_schema, valid_reuse, True)
add_case("valid_state_bundle_manifest", bundle_schema, valid_bundle, True, coverage_check)

matrix = {"matrix_id": "runtime_provider_contract_schema_hardening_validation_matrix_v0_1", "gate": "runtime_provider_contract_schema_hardening_v0_1", "status": "CLOSED_SCHEMA_HARDENING_VALIDATION_PASS_NO_EXECUTION", "jsonschema_library": "jsonschema.Draft202012Validator", "case_count": len(cases), "failed_cases": [c for c in cases if c["result"] != "PASS"], "cases": cases}
write_json(RUNTIME / "runtime_provider_contract_schema_hardening_validation_matrix_v0_1.json", matrix)
if matrix["failed_cases"]:
    raise SystemExit("Validation matrix has failing expectations")

write_md(RUNTIME / "runtime_provider_contract_schema_hardening_readout_v0_1.md", f"""
# runtime_provider_contract_schema_hardening_readout_v0_1

Status: `CLOSED_SCHEMA_HARDENED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`
Gate: `runtime_provider_contract_schema_hardening_v0_1`
Owner layer: `08_RUNTIME_CAPABILITIES`

## Reason

A provider-consumer compatibility preflight found that the provider documentation was coherent, but the provider JSON Schemas did not yet enforce the fail-closed semantics described by the documents.

## Hardened contracts

```text
state_resolution_request_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
```

Specialized request contracts are now required package authorities:

```text
market_state_request_contract_v0_1.json
event_state_request_contract_v0_1.json
```

## Corrections made

```text
StateResolutionRequest links request_type to the matching payload.
payload is type object with additionalProperties=false.
Market and Event payload shapes reject unexpected physical path fields.
RuntimeInvocationResponse ties invocation_status to resolution_decision and allowed refs.
blocked responses cannot return dataset ids or artifact references.
reuse_hit responses require a StateBundleManifest reference.
StateBundleManifest requires capability refs, request refs, dataset refs, artifact hashes and explicit cardinality.
StateBundleManifest supports an aggregate bundle for market_and_event requests.
Coverage arithmetic is declared as mandatory code validation where JSON Schema is insufficient.
Contract hash canonicalization policy is declared in hardened contracts.
```

## Validation evidence

```text
validation_matrix = runtime_provider_contract_schema_hardening_validation_matrix_v0_1.json
case_count = {len(cases)}
failed_cases = 0
schema_validator = jsonschema.Draft202012Validator
```

## Institutional result

```text
PACKAGE_INTEGRITY = PASS
PROVIDER_BOUNDARY = PASS
PROVIDER_INTERFACE_DOCUMENTATION = CLOSED
PROVIDER_SCHEMA_STRICT_VALIDATION = HARDENED_PENDING_COMPATIBILITY_REVIEW
FAIL_CLOSED_SEMANTICS = HARDENED_PENDING_COMPATIBILITY_REVIEW
PROVIDER_CONSUMER_COMPATIBILITY = READY_FOR_REVIEW_NOT_VALIDATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
```

## What remains closed

```text
runtime_executions = 0
market_state_requests_created = 0
event_state_requests_created = 0
state_bundle_manifests_created = 0
datasets_written = 0
registry_mutations = 0
backtest_runs_created = 0
StateReplayFeed_opened = false
official_dataset = false
production = false
downstream = false
```

## Next gate

```text
runtime_provider_consumer_contract_compatibility_review_v0_1
```

This next review may now rerun against hardened provider schemas. It must still keep the backtest consumer contracts in DRAFT unless field-by-field compatibility passes and separate backtest consumption authority is established.
""")

print(json.dumps({"status": "HARDENED_PROVIDER_CONTRACTS", "validation_cases": len(cases), "failed_cases": 0}, indent=2))
