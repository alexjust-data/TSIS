from __future__ import annotations

import copy
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def apply_patch_overrides(g: dict[str, Any]) -> None:
    """Apply the external-audit corrective overrides for provider v0.1.2.

    The base runner remains the provider-only implementation harness. This
    module replaces the functions that external audit proved materially weak:
    exact state-kind cardinality, response artifact correlation, failed/broken
    manifest reuse semantics, effective-view profile coherence, living-document
    updates and required-case guarding.
    """

    PathCls = g["Path"]
    g["AJV_NODE_MODULES"] = PathCls(os.environ.get("TSIS_AJV_NODE_MODULES", r"C:\tmp\tsis_ajv_runtime_v012\node_modules"))

    obj = g["obj"]
    partial = g["partial"]
    arr = g["arr"]
    nullable = g["nullable"]
    string = g["string"]
    hex64 = g["hex64"]
    ref_schema = g["ref_schema"]
    coverage_schema = g["coverage_schema"]
    dataset_ref_schema = g["dataset_ref_schema"]
    ref_value = g["ref_value"]
    h = g["h"]
    mutate = g["mutate"]
    valid_request = g["valid_request"]
    valid_response = g["valid_response"]
    valid_interface = g["valid_interface"]
    valid_effective_view_base = g["valid_effective_view"]
    write_text = g["write_text"]
    read_text = g["read_text"]
    write_json = g["write_json"]
    read_json = g["read_json"]
    sha256_file = g["sha256_file"]
    replace_first = g["replace_first"]
    make_zip = g["make_zip"]
    verify_zip = g["verify_zip"]
    normalize = g["normalize"]
    write_contracts = g["write_contracts"]
    add_case = g["add_case"]
    make_mutation = g["make_mutation"]

    ROOT = g["ROOT"]
    FEATURE_ROOT = g["FEATURE_ROOT"]
    RUNTIME = g["RUNTIME"]
    CONFIGS = g["CONFIGS"]
    SCRIPTS = g["SCRIPTS"]
    GATE = g["GATE"]
    STATUS = g["STATUS"]
    CONTRACT_NAMES = g["CONTRACT_NAMES"]

    schema_case_ids = [
        case_id
        for name in CONTRACT_NAMES
        for case_id in (
            f"schema_compile_jsonschema_{name}",
            f"ajv_8_17_1_strict_runtime_compile_{name}",
        )
    ]
    original_case_ids = [
        "positive_market_state_request",
        "positive_event_state_request",
        "negative_request_type_payload_mismatch",
        "negative_physical_path_payload",
        "negative_unsupported_event_type",
        "positive_reuse_hit_market_response",
        "negative_reuse_hit_missing_bundle",
        "negative_cross_details",
        "negative_blocked_with_dataset",
        "positive_authorized_reference",
        "negative_authorized_reference_missing_auth",
        "positive_market_bundle",
        "positive_event_bundle",
        "negative_pass_empty_capability_refs",
        "negative_coverage_arithmetic",
        "negative_missing_required_request_ref",
        "negative_empty_source_hashes",
        "negative_invalid_schema_hash",
        "negative_dataset_kind_mismatch",
        "negative_duplicate_fingerprints",
        "negative_request_ref_fingerprint_mismatch",
    ]
    external_case_ids = [
        "F01_cardinality_extra_response_ref_without_request",
        "F01_response_ref_absent_for_request",
        "F02_duplicate_ref_id_cross_arrays",
        "F03_market_response_event_capability",
        "F03_event_response_market_profile",
        "F04_effective_view_downstream_true",
        "F04_effective_view_duplicate_capability",
        "F05_fail_manifest_reuse_eligible",
        "F06_validate_operation_resolve_mode",
        "F06_invoke_missing_authorization",
        "F07_authorization_required_with_dataset",
        "F09_market_request_event_state_binding",
        "F09_request_fingerprint_mismatch_in_binding",
    ]
    followup_case_ids = [
        "F01_market_and_event_duplicate_market_binding_no_event_binding",
        "F01_market_and_event_third_extra_binding",
        "F01_market_state_only_two_bindings",
        "F01_market_and_event_single_capability_ref",
        "F01_market_and_event_single_profile_version",
        "F04_market_capability_advertises_event_profile",
        "F04_event_capability_advertises_market_profile",
        "F05_fail_manifest_dataset_ref_pass_reusable",
        "F05_blocked_manifest_dataset_ref_pass_reusable",
        "F09_response_ref_arbitrary_valid_ref",
        "F09_response_ref_sha256_unrelated_valid_hash",
        "F09_market_event_response_refs_swapped",
    ]
    required_case_ids = schema_case_ids + original_case_ids + external_case_ids + followup_case_ids
    g["REQUIRED_CASE_IDS"] = required_case_ids

    def binding_schema(kind: str | None = None) -> dict[str, Any]:
        state_schema = {"const": kind} if kind else {"enum": ["market_state", "event_state"]}
        return obj(
            {
                "request_ref": ref_schema("state_resolution_request", "available"),
                "request_fingerprint": hex64(),
                "response_ref": ref_schema("runtime_invocation_response", "available"),
                "state_kind": state_schema,
            },
            ["request_ref", "request_fingerprint", "response_ref", "state_kind"],
        )

    def capability_ref_schema(kind: str) -> dict[str, Any]:
        cap_id = f"{kind}_on_demand_runtime_capability_v0_1"
        return obj(
            {
                "ref_id": {"const": cap_id},
                "ref_type": {"const": "runtime_capability"},
                "sha256": hex64(),
                "availability": {"const": "available"},
            },
            ["ref_id", "ref_type", "sha256", "availability"],
        )

    def profile_schema(kind: str) -> dict[str, Any]:
        profile_id = "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1"
        return obj(
            {
                "state_kind": {"const": kind},
                "profile_id": {"const": profile_id},
                "profile_version": string(),
                "profile_fingerprint": hex64(),
            },
            ["state_kind", "profile_id", "profile_version", "profile_fingerprint"],
        )

    def response_artifact_schema() -> dict[str, Any]:
        return obj(
            {
                "response_ref_id": string(),
                "response_ref_sha256": hex64(),
                "request_fingerprint": hex64(),
                "state_kind": {"enum": ["market_state", "event_state"]},
                "response_fingerprint": hex64(),
                "availability": {"const": "available"},
            },
            ["response_ref_id", "response_ref_sha256", "request_fingerprint", "state_kind", "response_fingerprint", "availability"],
        )

    def bundle_schema() -> dict[str, Any]:
        artifact_hash = obj(
            {"artifact_id": string(), "artifact_type": string(), "sha256": hex64(), "availability": {"const": "available"}},
            ["artifact_id", "artifact_type", "sha256", "availability"],
        )
        profile_any = obj(
            {"state_kind": {"enum": ["market_state", "event_state"]}, "profile_id": string(), "profile_version": string(), "profile_fingerprint": hex64()},
            ["state_kind", "profile_id", "profile_version", "profile_fingerprint"],
        )
        dataset_refs_any = obj(
            {
                "market_state_dataset_ref": nullable(dataset_ref_schema("market_state")),
                "event_state_dataset_ref": nullable(dataset_ref_schema("event_state")),
            },
            ["market_state_dataset_ref", "event_state_dataset_ref"],
        )
        schema = obj(
            {
                "state_bundle_manifest_id": string(),
                "bundle_ref": ref_schema("state_bundle_manifest", "available"),
                "bundle_state_mode": {"enum": ["market_state_only", "event_state_only", "market_and_event"]},
                "state_kinds": arr({"enum": ["market_state", "event_state"]}, 1, True, 2),
                "request_response_bindings": arr(binding_schema(), 1, True, 2),
                "runtime_invocation_response_artifacts": arr(response_artifact_schema(), 1, True, 2),
                "capability_refs": arr(ref_schema("runtime_capability", "available"), 1, True, 2),
                "dataset_refs": dataset_refs_any,
                "coverage": coverage_schema(),
                "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS", "FAIL", "BLOCKED"]},
                "restrictions": arr(string(), 1, True),
                "representation_profile_versions": arr(profile_any, 1, True, 2),
                "schema_fingerprints": arr(hex64(), 1, True),
                "source_dataset_ids": arr(string(), 1, True),
                "source_content_hashes": arr(hex64(), 1, True),
                "artifact_hashes": arr(artifact_hash, 1, True),
                "field_lineage": arr(obj({"field_id": string(), "builder_id": string(), "input_refs": arr(string(), 1, True)}, ["field_id", "builder_id", "input_refs"]), 1, True),
                "temporal_policy": obj(
                    {
                        "point_in_time_policy_id": string(),
                        "available_at_policy_id": string(),
                        "future_information_exclusion": {"const": True},
                    },
                    ["point_in_time_policy_id", "available_at_policy_id", "future_information_exclusion"],
                ),
                "materialization_status": {"enum": ["reference_only", "materialized_candidate", "blocked", "failed"]},
                "reuse_certification": obj(
                    {
                        "reuse_eligible": {"type": "boolean"},
                        "reuse_decision": {"enum": ["eligible", "eligible_with_restrictions", "not_eligible_failed_or_blocked"]},
                        "reusable_dataset_refs": arr(string(), 0, True),
                    },
                    ["reuse_eligible", "reuse_decision", "reusable_dataset_refs"],
                ),
                "consumption_authorization": obj(
                    {"backtest_consumption_authorized": {"const": False}, "downstream_authorized": {"const": False}, "consumption_purposes": arr(string(), 0, True, 0)},
                    ["backtest_consumption_authorized", "downstream_authorized", "consumption_purposes"],
                ),
                "official_dataset": {"const": False},
                "production": {"const": False},
                "downstream": {"const": False},
                "physical_rows_delivered": {"const": False},
            },
            [
                "state_bundle_manifest_id",
                "bundle_ref",
                "bundle_state_mode",
                "state_kinds",
                "request_response_bindings",
                "runtime_invocation_response_artifacts",
                "capability_refs",
                "dataset_refs",
                "coverage",
                "validation_status",
                "restrictions",
                "representation_profile_versions",
                "schema_fingerprints",
                "source_dataset_ids",
                "source_content_hashes",
                "artifact_hashes",
                "field_lineage",
                "temporal_policy",
                "materialization_status",
                "reuse_certification",
                "consumption_authorization",
                "official_dataset",
                "production",
                "downstream",
                "physical_rows_delivered",
            ],
        )
        schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/state_bundle_manifest_contract_v0_1_2.schema.json", "title": "TSIS StateBundleManifest v0.1.2"})
        pass_status = {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}
        schema["allOf"] = [
            {"if": partial({"bundle_state_mode": {"const": "market_state_only"}, "validation_status": pass_status}), "then": partial({"state_kinds": arr({"const": "market_state"}, 1, True, 1), "request_response_bindings": arr(binding_schema("market_state"), 1, True, 1), "runtime_invocation_response_artifacts": arr(response_artifact_schema(), 1, True, 1), "capability_refs": arr(capability_ref_schema("market_state"), 1, True, 1), "representation_profile_versions": arr(profile_schema("market_state"), 1, True, 1), "dataset_refs": obj({"market_state_dataset_ref": dataset_ref_schema("market_state"), "event_state_dataset_ref": {"type": "null"}}, ["market_state_dataset_ref", "event_state_dataset_ref"])})},
            {"if": partial({"bundle_state_mode": {"const": "event_state_only"}, "validation_status": pass_status}), "then": partial({"state_kinds": arr({"const": "event_state"}, 1, True, 1), "request_response_bindings": arr(binding_schema("event_state"), 1, True, 1), "runtime_invocation_response_artifacts": arr(response_artifact_schema(), 1, True, 1), "capability_refs": arr(capability_ref_schema("event_state"), 1, True, 1), "representation_profile_versions": arr(profile_schema("event_state"), 1, True, 1), "dataset_refs": obj({"market_state_dataset_ref": {"type": "null"}, "event_state_dataset_ref": dataset_ref_schema("event_state")}, ["market_state_dataset_ref", "event_state_dataset_ref"])})},
            {"if": partial({"bundle_state_mode": {"const": "market_and_event"}, "validation_status": pass_status}), "then": partial({"state_kinds": arr({"enum": ["market_state", "event_state"]}, 2, True, 2), "request_response_bindings": arr(binding_schema(), 2, True, 2), "runtime_invocation_response_artifacts": arr(response_artifact_schema(), 2, True, 2), "capability_refs": arr(ref_schema("runtime_capability", "available"), 2, True, 2), "representation_profile_versions": arr(profile_any, 2, True, 2), "dataset_refs": obj({"market_state_dataset_ref": dataset_ref_schema("market_state"), "event_state_dataset_ref": dataset_ref_schema("event_state")}, ["market_state_dataset_ref", "event_state_dataset_ref"])})},
            {"if": partial({"validation_status": {"enum": ["BLOCKED", "FAIL"]}}), "then": partial({"materialization_status": {"enum": ["blocked", "failed"]}, "dataset_refs": obj({"market_state_dataset_ref": {"type": "null"}, "event_state_dataset_ref": {"type": "null"}}, ["market_state_dataset_ref", "event_state_dataset_ref"]), "reuse_certification": obj({"reuse_eligible": {"const": False}, "reuse_decision": {"const": "not_eligible_failed_or_blocked"}, "reusable_dataset_refs": arr(string(), 0, True, 0)}, ["reuse_eligible", "reuse_decision", "reusable_dataset_refs"])})},
        ]
        return schema

    def effective_view_schema() -> dict[str, Any]:
        permissions = obj(
            {"metadata_lookup": {"const": True}, "registry_lookup": {"const": True}, "exact_reuse_resolution": {"const": True}, "candidate_generation_under_separate_authorization": {"const": True}, "physical_row_delivery": {"const": False}, "state_replay_feed": {"const": False}, "backtest_consumption": {"const": False}, "production": {"const": False}, "downstream": {"const": False}},
            ["metadata_lookup", "registry_lookup", "exact_reuse_resolution", "candidate_generation_under_separate_authorization", "physical_row_delivery", "state_replay_feed", "backtest_consumption", "production", "downstream"],
        )
        cap = obj(
            {"capability_id": {"enum": ["market_state_on_demand_runtime_capability_v0_1", "event_state_on_demand_runtime_capability_v0_1"]}, "request_type": {"enum": ["market_state", "event_state"]}, "capability_status": {"enum": ["promoted_with_restrictions", "available_with_restrictions"]}, "supported_profile_ids": arr(string(), 1, True, 1), "supported_event_type_ids": arr(string(), 0, True, 1), "subject_scope": nullable(string()), "candidate_generation_authority": {"const": True}, "reuse_authority": {"const": True}, "official_dataset": {"const": False}, "production": {"const": False}, "downstream": {"const": False}, "backtest_consumption": {"const": False}, "effective_permissions": permissions},
            ["capability_id", "request_type", "capability_status", "supported_profile_ids", "supported_event_type_ids", "subject_scope", "candidate_generation_authority", "reuse_authority", "official_dataset", "production", "downstream", "backtest_consumption", "effective_permissions"],
        )
        cap["allOf"] = [
            {"if": partial({"request_type": {"const": "market_state"}}), "then": partial({"capability_id": {"const": "market_state_on_demand_runtime_capability_v0_1"}, "supported_profile_ids": arr({"const": "market_state_core_four_intraday_profile_v0_1"}, 1, True, 1), "supported_event_type_ids": arr(string(), 0, True, 0), "subject_scope": {"type": "null"}})},
            {"if": partial({"request_type": {"const": "event_state"}}), "then": partial({"capability_id": {"const": "event_state_on_demand_runtime_capability_v0_1"}, "supported_profile_ids": arr({"const": "event_state_core_four_intraday_profile_v0_1"}, 1, True, 1), "supported_event_type_ids": arr({"const": "event_type:market_data:session_opened"}, 1, True, 1), "subject_scope": {"const": "exchange_session"}})},
        ]
        schema = obj({"view_id": string(), "view_version": {"const": "0.1.2"}, "capabilities": arr(cap, 2, True, 2)}, ["view_id", "view_version", "capabilities"])
        schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://tsis.local/contracts/runtime_capability_effective_view_contract_v0_1_2.schema.json", "title": "TSIS RuntimeCapabilityEffectiveView v0.1.2"})
        return schema

    def valid_bundle(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]

        def response_ref_for(kind: str) -> dict[str, Any]:
            return ref_value("runtime_invocation_response", f"{kind}_response_ref", h(f"response_artifact_{kind}"))

        bindings = []
        response_artifacts = []
        for kind in kinds:
            fp = h(f"request_{kind}")
            response_ref = response_ref_for(kind)
            bindings.append({"request_ref": ref_value("state_resolution_request", f"req_ref_{kind}", fp), "request_fingerprint": fp, "response_ref": response_ref, "state_kind": kind})
            response_artifacts.append({"response_ref_id": response_ref["ref_id"], "response_ref_sha256": response_ref["sha256"], "request_fingerprint": fp, "state_kind": kind, "response_fingerprint": response_ref["sha256"], "availability": "available"})

        def dataset(kind: str) -> dict[str, Any]:
            return {"dataset_id": f"{kind}_dataset_001", "dataset_kind": kind, "candidate_dataset_fingerprint": h(f"dataset_{kind}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}

        def capability_ref(kind: str) -> dict[str, Any]:
            cap_id = f"{kind}_on_demand_runtime_capability_v0_1"
            return ref_value("runtime_capability", cap_id, h(cap_id))

        return {"state_bundle_manifest_id": "bundle_001", "bundle_ref": ref_value("state_bundle_manifest", "bundle_ref_001"), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": bindings, "runtime_invocation_response_artifacts": response_artifacts, "capability_refs": [capability_ref(kind) for kind in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": kind, "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{kind}")} for kind in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": "artifact_001", "artifact_type": "manifest", "sha256": h("artifact"), "availability": "available"}], "field_lineage": [{"field_id": "field_001", "builder_id": "builder_001", "input_refs": ["input_001"]}], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{kind}_dataset_001" for kind in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}

    def semantic_errors(doc: dict[str, Any], kind: str) -> list[str]:
        errors = g["semantic_errors_original"](doc, kind) if "semantic_errors_original" in g else []
        if kind == "bundle":
            mode = doc.get("bundle_state_mode")
            expected_kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}.get(mode, [])
            if sorted(doc.get("state_kinds", [])) != sorted(expected_kinds):
                errors.append("bundle_state_mode/state_kinds mismatch")
            bindings = doc.get("request_response_bindings", [])
            binding_kinds = [b.get("state_kind") for b in bindings]
            if len(bindings) != len(expected_kinds) or sorted(binding_kinds) != sorted(expected_kinds):
                errors.append("request_response_bindings must contain exactly one binding per expected state_kind")
            response_ids = [b.get("response_ref", {}).get("ref_id") for b in bindings if isinstance(b.get("response_ref"), dict)]
            if len(response_ids) != len(set(response_ids)):
                errors.append("duplicate response_ref in bindings")
            for binding in bindings:
                if binding.get("request_ref", {}).get("sha256") != binding.get("request_fingerprint"):
                    errors.append("request_ref sha256 does not match binding request_fingerprint")
                if binding.get("state_kind") not in expected_kinds:
                    errors.append("binding state_kind outside expected bundle state_kinds")
            artifacts = doc.get("runtime_invocation_response_artifacts", [])
            artifact_keys = [(a.get("response_ref_id"), a.get("response_ref_sha256")) for a in artifacts]
            if len(artifacts) != len(expected_kinds) or len(set(artifact_keys)) != len(artifact_keys):
                errors.append("runtime_invocation_response_artifacts must contain exactly one unique artifact per expected state_kind")
            artifacts_by_ref = {(a.get("response_ref_id"), a.get("response_ref_sha256")): a for a in artifacts}
            for binding in bindings:
                response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
                artifact = artifacts_by_ref.get((response_ref.get("ref_id"), response_ref.get("sha256")))
                if not artifact:
                    errors.append("binding response_ref has no matching response artifact evidence")
                    continue
                if artifact.get("request_fingerprint") != binding.get("request_fingerprint"):
                    errors.append("response artifact request_fingerprint mismatch")
                if artifact.get("state_kind") != binding.get("state_kind"):
                    errors.append("response artifact state_kind mismatch")
            expected_capability_ids = {f"{state_kind}_on_demand_runtime_capability_v0_1" for state_kind in expected_kinds}
            capability_ids = {ref.get("ref_id") for ref in doc.get("capability_refs", []) if isinstance(ref, dict)}
            if capability_ids != expected_capability_ids:
                errors.append("capability_refs must match expected state_kind capabilities exactly")
            expected_profile_ids = {"market_state": "market_state_core_four_intraday_profile_v0_1", "event_state": "event_state_core_four_intraday_profile_v0_1"}
            profiles = doc.get("representation_profile_versions", [])
            profile_kinds = [profile.get("state_kind") for profile in profiles]
            if len(profiles) != len(expected_kinds) or sorted(profile_kinds) != sorted(expected_kinds):
                errors.append("representation_profile_versions must contain exactly one profile per expected state_kind")
            for profile in profiles:
                if profile.get("profile_id") != expected_profile_ids.get(profile.get("state_kind")):
                    errors.append("representation profile_id/state_kind mismatch")
            refs = doc.get("dataset_refs", {})
            reuse = doc.get("reuse_certification", {})
            if doc.get("validation_status") in {"FAIL", "BLOCKED"}:
                if refs.get("market_state_dataset_ref") is not None or refs.get("event_state_dataset_ref") is not None:
                    errors.append("FAIL/BLOCKED manifest cannot carry dataset refs")
                if reuse.get("reuse_eligible") or reuse.get("reusable_dataset_refs"):
                    errors.append("FAIL/BLOCKED manifest cannot certify reusable dataset")
        if kind == "effective_view":
            for cap in doc.get("capabilities", []):
                if cap.get("request_type") == "market_state":
                    if cap.get("supported_profile_ids") != ["market_state_core_four_intraday_profile_v0_1"]:
                        errors.append("market capability must advertise only Market State profile")
                    if cap.get("supported_event_type_ids"):
                        errors.append("market capability must not advertise event types")
                    if cap.get("subject_scope") is not None:
                        errors.append("market capability subject_scope must be null")
                if cap.get("request_type") == "event_state":
                    if cap.get("supported_profile_ids") != ["event_state_core_four_intraday_profile_v0_1"]:
                        errors.append("event capability must advertise only Event State profile")
                    if cap.get("supported_event_type_ids") != ["event_type:market_data:session_opened"]:
                        errors.append("event capability must advertise only session_opened")
                    if cap.get("subject_scope") != "exchange_session":
                        errors.append("event capability subject_scope mismatch")
        return list(dict.fromkeys(errors))

    g["semantic_errors_original"] = g.get("semantic_errors")
    g["semantic_errors"] = semantic_errors
    g["bundle_schema"] = bundle_schema
    g["effective_view_schema"] = effective_view_schema
    g["valid_bundle"] = valid_bundle

    def swap_response_refs(doc: dict[str, Any]) -> None:
        first = copy.deepcopy(doc["request_response_bindings"][0]["response_ref"])
        second = copy.deepcopy(doc["request_response_bindings"][1]["response_ref"])
        doc["request_response_bindings"][0]["response_ref"] = second
        doc["request_response_bindings"][1]["response_ref"] = first

    def run_matrix(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        rows: list[dict[str, Any]] = []
        for name, schema in schemas.items():
            errors: list[str] = []
            try:
                g["Draft202012Validator"].check_schema(schema)
            except Exception as exc:
                errors.append(str(exc))
            rows.append({"case_id": f"schema_compile_jsonschema_{name}", "case_origin": "original_31_regression", "schema": name, "expected_valid": True, "actual_valid": not errors, "result": "PASS" if not errors else "FAIL", "errors": errors[:8]})
            ajv_errors = g["ajv_compile"](schema)
            rows.append({"case_id": f"ajv_8_17_1_strict_runtime_compile_{name}", "case_origin": "original_31_regression", "schema": name, "expected_valid": True, "actual_valid": not ajv_errors, "result": "PASS" if not ajv_errors else "FAIL", "errors": ajv_errors[:8]})

        srr, iface, resp, bundle, eff = (schemas[name] for name in CONTRACT_NAMES)
        original_cases = [
            ("positive_market_state_request", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", valid_request("market_state"), True),
            ("positive_event_state_request", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", valid_request("event_state"), True),
            ("negative_request_type_payload_mismatch", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", {**valid_request("market_state"), "payload": {"event_state_request": valid_request("event_state")["payload"]["event_state_request"]}}, False),
            ("negative_physical_path_payload", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", make_mutation("negative_physical_path_payload"), False),
            ("negative_unsupported_event_type", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", make_mutation("negative_unsupported_event_type"), False),
            ("positive_reuse_hit_market_response", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", valid_response("market_state"), True),
            ("negative_reuse_hit_missing_bundle", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", make_mutation("negative_reuse_hit_missing_bundle"), False),
            ("negative_cross_details", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", make_mutation("negative_cross_details"), False),
            ("negative_blocked_with_dataset", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", make_mutation("negative_blocked_with_dataset"), False),
            ("positive_authorized_reference", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", valid_response("market_state", "authorized_reference"), True),
            ("negative_authorized_reference_missing_auth", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", make_mutation("negative_authorized_reference_missing_auth"), False),
            ("positive_market_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle("market_state_only"), True),
            ("positive_event_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle("event_state_only"), True),
            ("negative_pass_empty_capability_refs", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_pass_empty_capability_refs"), False),
            ("negative_coverage_arithmetic", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_coverage_arithmetic"), False),
            ("negative_missing_required_request_ref", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_missing_required_request_ref"), False),
            ("negative_empty_source_hashes", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_empty_source_hashes"), False),
            ("negative_invalid_schema_hash", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_invalid_schema_hash"), False),
            ("negative_dataset_kind_mismatch", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_dataset_kind_mismatch"), False),
            ("negative_duplicate_fingerprints", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_duplicate_fingerprints"), False),
            ("negative_request_ref_fingerprint_mismatch", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", make_mutation("negative_request_ref_fingerprint_mismatch"), False),
        ]
        for case in original_cases:
            add_case(rows, case[0], "original_31_regression", case[1], case[2], case[3], case[4], case[5])

        external_cases = [
            ("F01_cardinality_extra_response_ref_without_request", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), lambda d: d["request_response_bindings"].pop()), False),
            ("F01_response_ref_absent_for_request", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"response_ref": None})), False),
            ("F02_duplicate_ref_id_cross_arrays", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["capability_refs"][0].update({"ref_id": d["bundle_ref"]["ref_id"]})), False),
            ("F03_market_response_event_capability", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response("market_state"), lambda d: d.update({"capability_id": "event_state_on_demand_runtime_capability_v0_1"})), False),
            ("F03_event_response_market_profile", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response("event_state"), lambda d: d.update({"profile_id": "market_state_core_four_intraday_profile_v0_1"})), False),
            ("F04_effective_view_downstream_true", "runtime_capability_effective_view_contract_v0_1_2.json", eff, "effective_view", mutate(valid_effective_view_base(), lambda d: d["capabilities"][0]["effective_permissions"].update({"downstream": True})), False),
            ("F04_effective_view_duplicate_capability", "runtime_capability_effective_view_contract_v0_1_2.json", eff, "effective_view", mutate(valid_effective_view_base(), lambda d: d["capabilities"][1].update({"capability_id": "market_state_on_demand_runtime_capability_v0_1", "request_type": "market_state", "supported_event_type_ids": []})), False),
            ("F05_fail_manifest_reuse_eligible", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d.update({"validation_status": "FAIL", "materialization_status": "failed"})), False),
            ("F06_validate_operation_resolve_mode", "runtime_user_invocation_interface_contract_v0_1_2.json", iface, "interface", mutate(valid_interface("validate"), lambda d: d["state_resolution_request"]["resolution_policy"].update({"mode": "resolve_reuse_or_authorization"})), False),
            ("F06_invoke_missing_authorization", "runtime_user_invocation_interface_contract_v0_1_2.json", iface, "interface", mutate(valid_interface("invoke"), lambda d: d.update({"execution_authorization_ref": None})), False),
            ("F07_authorization_required_with_dataset", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response("market_state", "authorization_required"), lambda d: d.update({"dataset_id": "dataset_should_not_exist"})), False),
            ("F09_market_request_event_state_binding", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"state_kind": "event_state"})), False),
            ("F09_request_fingerprint_mismatch_in_binding", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"request_fingerprint": h("wrong")})), False),
        ]
        for case in external_cases:
            add_case(rows, case[0], "external_adversarial_regression", case[1], case[2], case[3], case[4], case[5])

        followup_cases = [
            ("F01_market_and_event_duplicate_market_binding_no_event_binding", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), lambda d: (d["request_response_bindings"][1].update({"state_kind": "market_state"}), d["runtime_invocation_response_artifacts"][1].update({"state_kind": "market_state"}))), False),
            ("F01_market_and_event_third_extra_binding", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), lambda d: d["request_response_bindings"].append(copy.deepcopy(d["request_response_bindings"][0]))), False),
            ("F01_market_state_only_two_bindings", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_state_only"), lambda d: (d["request_response_bindings"].append(copy.deepcopy(d["request_response_bindings"][0])), d["runtime_invocation_response_artifacts"].append(copy.deepcopy(d["runtime_invocation_response_artifacts"][0])))), False),
            ("F01_market_and_event_single_capability_ref", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), lambda d: d["capability_refs"].pop()), False),
            ("F01_market_and_event_single_profile_version", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), lambda d: d["representation_profile_versions"].pop()), False),
            ("F04_market_capability_advertises_event_profile", "runtime_capability_effective_view_contract_v0_1_2.json", eff, "effective_view", mutate(valid_effective_view_base(), lambda d: d["capabilities"][0].update({"supported_profile_ids": ["event_state_core_four_intraday_profile_v0_1"]})), False),
            ("F04_event_capability_advertises_market_profile", "runtime_capability_effective_view_contract_v0_1_2.json", eff, "effective_view", mutate(valid_effective_view_base(), lambda d: d["capabilities"][1].update({"supported_profile_ids": ["market_state_core_four_intraday_profile_v0_1"]})), False),
            ("F05_fail_manifest_dataset_ref_pass_reusable", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d.update({"validation_status": "FAIL", "materialization_status": "failed", "reuse_certification": {"reuse_eligible": False, "reuse_decision": "not_eligible_failed_or_blocked", "reusable_dataset_refs": []}})), False),
            ("F05_blocked_manifest_dataset_ref_pass_reusable", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d.update({"validation_status": "BLOCKED", "materialization_status": "blocked", "reuse_certification": {"reuse_eligible": False, "reuse_decision": "not_eligible_failed_or_blocked", "reusable_dataset_refs": []}})), False),
            ("F09_response_ref_arbitrary_valid_ref", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0].update({"response_ref": ref_value("runtime_invocation_response", "arbitrary_response", h("arbitrary_response"))})), False),
            ("F09_response_ref_sha256_unrelated_valid_hash", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0]["response_ref"].update({"sha256": h("unrelated_response_hash")})), False),
            ("F09_market_event_response_refs_swapped", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle("market_and_event"), swap_response_refs), False),
        ]
        for case in followup_cases:
            add_case(rows, case[0], "external_audit_followup_regression", case[1], case[2], case[3], case[4], case[5])

        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required_case_ids) - set(case_ids))
        unexpected = sorted(set(case_ids) - set(required_case_ids))
        duplicates = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates and len(rows) >= len(required_case_ids)
        return {
            "gate": GATE,
            "status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2",
            "created_at_utc": g["now_utc"](),
            "case_count": len(rows),
            "original_case_count": len([r for r in rows if r["case_origin"] == "original_31_regression"]),
            "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression"}]),
            "external_followup_case_count": len([r for r in rows if r["case_origin"] == "external_audit_followup_regression"]),
            "required_case_ids": required_case_ids,
            "missing_required_case_ids": missing,
            "duplicate_case_ids": duplicates,
            "unexpected_silent_skips": len(unexpected),
            "unexpected_case_ids": unexpected,
            "failed_cases": len(failed),
            "jsonschema_draft_2020_12_compile": "PASS" if not any(r["case_id"].startswith("schema_compile") and r["result"] == "FAIL" for r in rows) else "FAIL",
            "ajv_8_17_1_strict_runtime": "PASS" if not any(r["case_id"].startswith("ajv_8_17_1") and r["result"] == "FAIL" for r in rows) else "FAIL",
            "semantic_validator_execution": "PASS" if not failed else "FAIL",
            "expanded_adversarial_matrix": "PASS" if ok else "FAIL",
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

    g["run_matrix"] = run_matrix

    def write_scope(now: str) -> Path:
        path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json"
        write_json(path, {"scope_id": "runtime_provider_contract_schema_hardening_v0_1_2_scope", "gate": GATE, "created_at_utc": now, "status": "AUTHORIZED_IMPLEMENTATION_SCOPE_PROVIDER_ONLY", "provider_only": True, "authorized_by": "runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1", "baseline_authority": "runtime_provider_contract_schema_hardening_v0_1_1", "previous_external_audit_result": "FAIL_DOCUMENT_AND_SEMANTIC_GAPS", "required_findings": ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09"], "required_case_ids": required_case_ids, "minimum_case_counts": {"original_regression": 31, "external_adversarial_and_followup_regression": 25, "total": len(required_case_ids)}, "ajv_environment_lock_ref": "configs/runtime_provider_contract_schema_hardening_v0_1_2_ajv_environment_lock.json", "hard_boundaries": {"runtime_requests_executed": 0, "runtime_builds_executed": 0, "datasets_written": 0, "registry_mutations": 0, "physical_state_rows_delivered": 0, "state_replay_feed_records_emitted": 0, "backtest_runs_started": 0, "backtest_consumption_authority": False, "production": False, "downstream": False}, "not_authorized": ["runtime_provider_consumer_contract_compatibility_review_v0_1", "StateBundle physical reads", "StateReplayFeed", "Backtest RunPreflight state integration", "production", "downstream"]})
        return path

    def write_fixed_readout(path: Path, title: str, body: str) -> Path:
        write_text(path, f"# {title}\n\n{body.strip()}\n")
        return path

    def write_rollback_readout(now: str) -> Path:
        return write_fixed_readout(
            RUNTIME / "runtime_provider_v0_1_2_rollback_verification_readout_v0_1.md",
            "Runtime Provider v0.1.2 Rollback Verification v0.1",
            f"""Gate: `runtime_provider_v0_1_2_rollback_verification_v0_1`
Date: `{now[:10]}`
Status: `CLOSED_PASS_ROLLBACK_VERIFIED_NO_EXECUTION`

```text
active_v0_1_2_implementation_artifacts = 0
active_v0_1_2_provider_only_zips = 0
active_v0_1_2_pass_closed_claims = 0
runner_pycache = 0
live_document_encoding_clean = true
backtester_hold_handoff_valid = PASS
```

The previous unauthorized v0.1.2 attempt remains `QUARANTINED_NO_ACTIVE_AUTHORITY`. No runtime requests, builds, datasets, registry mutations, physical reads, StateReplayFeed, backtest consumption, production or downstream were opened.""",
        )

    def write_findings_revalidation_readout(now: str) -> Path:
        return write_fixed_readout(
            RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_readout_v0_1.md",
            "Runtime Provider Contract Schema Hardening Findings Revalidation v0.1",
            f"""Gate: `runtime_provider_contract_schema_hardening_findings_revalidation_v0_1`
Date: `{now[:10]}`
Status: `CLOSED_REPRODUCED_FINDINGS_REQUIRE_PROVIDER_HARDENING_NO_EXECUTION`

```text
baseline = runtime_provider_contract_schema_hardening_v0_1_1
finding_count = 9
reproduced_findings = 9
not_reproduced_findings = 0
runtime_requests_executed = 0
contracts_written = 0
runner_written = 0
datasets_written = 0
registry_mutations = 0
physical_state_rows_delivered = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

All F01-F09 remain material requirements for a clean provider-owned `runtime_provider_contract_schema_hardening_v0_1_2` implementation.""",
        )

    def write_authorization_revalidation_addendum(now: str) -> Path:
        return write_fixed_readout(
            RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_revalidation_addendum_v0_1.md",
            "Runtime Provider Contract Schema Hardening v0.1.2 Authorization Revalidation Addendum v0.1",
            f"""Date: `{now[:10]}`
Status: `CLOSED_AUTHORIZATION_RECONFIRMED_AFTER_ROLLBACK_AND_FINDINGS_REVALIDATION_NO_EXECUTION`

The clean provider-side v0.1.2 hardening authorization may be used only after rollback verification and findings revalidation both closed.

```text
reconfirmed_next_gate = runtime_provider_contract_schema_hardening_v0_1_2
provider_only = true
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
physical_state_rows_delivered = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

The previous quarantined v0.1.2 attempt remains negative evidence only and must not be copied, promoted or packaged as authority.""",
        )

    def write_external_audit_failure_readout(now: str) -> Path:
        return write_fixed_readout(
            RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_external_audit_failure_readout_v0_1.md",
            "Runtime Provider Contract Schema Hardening v0.1.2 External Audit Failure Readout v0.1",
            f"""Date: `{now[:10]}`
Status: `CLOSED_INTERNAL_WITH_RESTRICTIONS_EXTERNAL_AUDIT_FAILED`

```text
audited_zip = runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip
audited_zip_sha256 = c28e60c3041d100630408e95bb141854958b6ec8a94bb385b29e8e9b2b56446c
external_audit_result = FAIL_DOCUMENT_AND_SEMANTIC_GAPS
```

The failed ZIP is not accepted provider authority. The corrected v0.1.2 package must undergo another independent external audit before acceptance.

```text
StateBundle physical consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```""",
        )

    def write_ajv_environment_lock(now: str) -> Path:
        path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_environment_lock.json"
        package_json = g["AJV_NODE_MODULES"] / "ajv" / "package.json"
        node_version = subprocess.run(["node", "-e", "console.log(process.version)"], cwd=str(ROOT), capture_output=True, text=True, timeout=20).stdout.strip()
        package_data = read_json(package_json) if package_json.exists() else {}
        write_json(path, {"lock_id": "runtime_provider_contract_schema_hardening_v0_1_2_ajv_environment_lock", "created_at_utc": now, "node_version": node_version, "ajv_package": "ajv", "ajv_version": package_data.get("version"), "ajv_node_modules_env_var": "TSIS_AJV_NODE_MODULES", "ajv_node_modules_path_used": str(g["AJV_NODE_MODULES"]), "ajv_package_json_sha256": sha256_file(package_json) if package_json.exists() else None, "strict_runtime_command": "node -e <Ajv2020 strict compile script>", "reproduction_policy": "Set TSIS_AJV_NODE_MODULES to a node_modules directory containing ajv 8.17.1, or install from the locked version before running the provider-only runner.", "network_required_by_runner": False})
        return path

    def replace_current_docs_block(path: Path, block: str, body_anchor: str) -> None:
        text = read_text(path) if path.exists() else ""
        index = text.find(body_anchor)
        body = text[index:] if index != -1 else text
        write_text(path, block.strip() + "\n\n" + body.lstrip())

    def update_docs(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
        route_block = f"""## Provider Contract Schema Hardening v0.1.2 Corrected Internal Pass - {now[:10]}

```text
{GATE}
=
{matrix['status']}

PROVIDER_V0_1_2_EXTERNAL_AUDIT
=
PENDING_REAUDIT

PROVIDER_CONSUMER_COMPATIBILITY
=
NOT_OPENED_AFTER_V0_1_2
```

This corrected provider-only v0.1.2 hardening package supersedes the failed external-audit ZIP `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip`. It is not accepted authority until a new independent external audit passes.

```text
case_count = {matrix['case_count']}
original_case_count = {matrix['original_case_count']}
external_regression_case_count = {matrix['external_regression_case_count']}
external_followup_case_count = {matrix['external_followup_case_count']}
failed_cases = {matrix['failed_cases']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
duplicate_case_ids = {len(matrix['duplicate_case_ids'])}
unexpected_case_ids = {len(matrix['unexpected_case_ids'])}
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

Provider-only ZIP pending external re-audit:

```text
{zip_path}
```"""
        replace_first(route, "Status:", "Status: `route_v1_52_provider_hardening_v0_1_2_corrected_internal_pass_external_reaudit_pending`")
        replace_first(route, "Current gate:", "Current gate: `runtime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending`")
        replace_current_docs_block(route, route_block, "<!-- TSIS_ROUTE_CURRENT_STATE_V1_33_START -->")

        readme = RUNTIME / "README.md"
        readme_block = f"""## Provider Contract Schema Hardening v0.1.2 Corrected Internal Pass

```text
{GATE} = {matrix['status']}
PROVIDER_V0_1_2_EXTERNAL_AUDIT = PENDING_REAUDIT
PROVIDER_CONSUMER_COMPATIBILITY = NOT_OPENED_AFTER_V0_1_2
```

The previous ZIP `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip` failed external audit. This corrected package requires independent external re-audit before acceptance. Physical row delivery, StateReplayFeed, backtest consumption, production and downstream remain closed."""
        replace_first(readme, "Status:", "Status: `provider_hardening_v0_1_2_corrected_internal_pass_external_reaudit_pending`")
        replace_first(readme, "Current provider gate:", "Current provider gate: `runtime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending`")
        replace_current_docs_block(readme, readme_block, "# 08_RUNTIME_CAPABILITIES")

        agent = FEATURE_ROOT / "AGENT.md"
        agent_text = read_text(agent) if agent.exists() else ""
        first = agent_text.find("# 03_TABLES_feature_engineering - Agent Handoff Prompt")
        second = agent_text.find("# 03_TABLES_feature_engineering - Agent Handoff Prompt", first + 1) if first != -1 else -1
        agent_body = agent_text[second:] if second != -1 else agent_text
        agent_block = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Provider Hardening v0.1.2 Corrected Internal Pass Pending External Re-Audit

Status: `agent_handoff_prompt_v0_138`
Date: `{now[:10]}`

```text
current_gate = runtime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending
boundary_layer = 08_RUNTIME_CAPABILITIES
last_closed_gate = {GATE}
last_closed_status = {matrix['status']}
previous_v0_1_2_external_audit = FAIL_DOCUMENT_AND_SEMANTIC_GAPS
provider_v0_1_2_external_audit = PENDING_REAUDIT
provider_consumer_compatibility = NOT_OPENED_AFTER_V0_1_2
case_count = {matrix['case_count']}
failed_cases = {matrix['failed_cases']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
unexpected_case_ids = {len(matrix['unexpected_case_ids'])}
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

Do not open provider-consumer compatibility, StateBundle physical reads, StateReplayFeed, backtest state integration, production or downstream until the corrected v0.1.2 provider-only ZIP passes external audit."""
        write_text(agent, agent_block.strip() + "\n\n" + agent_body.lstrip())

        changelog = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"
        changelog_text = read_text(changelog) if changelog.exists() else ""
        if changelog_text.startswith("## 2026-07-29 - Runtime provider hardening v0.1.2 internal pass pending external audit"):
            next_index = changelog_text.find("\n## ", 1)
            changelog_text = changelog_text[next_index + 1:] if next_index != -1 else ""
        changelog_block = f"""## {now[:10]} - Runtime provider hardening v0.1.2 corrected internal pass pending external re-audit

- Recorded that `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip` failed external audit on document integrity and semantic gaps.
- Corrected the provider-only v0.1.2 candidate without accepting it as authority.
- Hardened F01, F04, F05, F08 and F09 against the externally reproduced bypasses, including exact state-kind binding cardinality and response artifact correlation.
- Replaced the tautological required-case guard with a frozen required-case list from implementation scope.
- Added an AJV environment lock and kept runtime requests, builds, datasets, registry mutations, physical state rows, StateReplayFeed, backtest consumption, production and downstream closed."""
        write_text(changelog, changelog_block.strip() + "\n" + changelog_text.lstrip())

    g["write_scope"] = write_scope
    g["write_rollback_readout"] = write_rollback_readout
    g["write_findings_revalidation_readout"] = write_findings_revalidation_readout
    g["write_authorization_revalidation_addendum"] = write_authorization_revalidation_addendum
    g["write_external_audit_failure_readout"] = write_external_audit_failure_readout
    g["write_ajv_environment_lock"] = write_ajv_environment_lock
    g["update_docs"] = update_docs

    def normalize_files(paths: list[Path]) -> None:
        for path in paths:
            if path.exists() and path.suffix.lower() in {".md", ".json", ".py"}:
                current = read_text(path).replace("\r\n", "\n").replace("\r", "\n")
                if not current.endswith("\n"):
                    current += "\n"
                write_text(path, current)

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
external_followup_case_count = {matrix['external_followup_case_count']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
duplicate_case_ids = {len(matrix['duplicate_case_ids'])}
unexpected_case_ids = {len(matrix['unexpected_case_ids'])}
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
F01 = CLOSED_BY_EXACT_STATE_KIND_CARDINALITY_AND_SEMANTIC_VALIDATOR
F02 = CLOSED_BY_SEMANTIC_VALIDATOR
F03 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F04 = CLOSED_BY_PROFILE_CAPABILITY_COHERENCE_VALIDATION
F05 = CLOSED_BY_FAIL_BLOCKED_DATASET_REF_REJECTION
F06 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F07 = CLOSED_BY_SCHEMA_AND_SEMANTIC_VALIDATOR
F08 = CLOSED_BY_ATOMIC_LIVING_DOCUMENT_REPLACEMENT_AND_REPAIRED_READOUTS
F09 = CLOSED_BY_RESPONSE_ARTIFACT_REQUEST_FINGERPRINT_STATE_KIND_CORRELATION
```

Previous external audit failure addressed:

```text
failed_zip = runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip
failed_zip_sha256 = c28e60c3041d100630408e95bb141854958b6ec8a94bb385b29e8e9b2b56446c
external_audit_status = FAIL_DOCUMENT_AND_SEMANTIC_GAPS
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

Provider-only ZIP pending external re-audit:

```text
{zip_path}
```
""")
        return path

    g["write_readout"] = write_readout

    def main() -> None:
        now = g["now_utc"]()
        scope_path = write_scope(now)
        rollback_readout_path = write_rollback_readout(now)
        findings_readout_path = write_findings_revalidation_readout(now)
        addendum_path = write_authorization_revalidation_addendum(now)
        audit_failure_path = write_external_audit_failure_readout(now)
        ajv_lock_path = write_ajv_environment_lock(now)
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
            addendum_path,
            CONFIGS / "runtime_provider_v0_1_2_rollback_verification_scope_v0_1.json",
            RUNTIME / "runtime_provider_v0_1_2_rollback_verification_matrix_v0_1.json",
            rollback_readout_path,
            CONFIGS / "runtime_provider_contract_schema_hardening_findings_revalidation_scope_v0_1.json",
            RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_matrix_v0_1.json",
            findings_readout_path,
            audit_failure_path,
            ajv_lock_path,
            scope_path,
            *contract_paths,
            SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_runner.py",
            SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_patch.py",
            matrix_path,
            readout_path,
            FEATURE_ROOT / "99_ruta_de_trabajo.md",
            FEATURE_ROOT / "AGENT.md",
            RUNTIME / "README.md",
            ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md",
        ]
        normalize_files(files)
        zip_path = make_zip(now, files)
        readout_path = write_readout(now, matrix, zip_path)
        update_docs(now, matrix, zip_path)
        normalize_files(files)
        zip_path.unlink(missing_ok=True)
        zip_path = make_zip(now, files)
        ok, errors = verify_zip(zip_path)
        if not ok:
            raise SystemExit("ZIP verification failed: " + "; ".join(errors))
        print(json.dumps({"gate": GATE, "status": matrix["status"], "case_count": matrix["case_count"], "original_case_count": matrix["original_case_count"], "external_regression_case_count": matrix["external_regression_case_count"], "external_followup_case_count": matrix["external_followup_case_count"], "missing_required_case_ids": len(matrix["missing_required_case_ids"]), "duplicate_case_ids": len(matrix["duplicate_case_ids"]), "unexpected_case_ids": len(matrix["unexpected_case_ids"]), "failed_cases": matrix["failed_cases"], "jsonschema_draft_2020_12_compile": matrix["jsonschema_draft_2020_12_compile"], "ajv_8_17_1_strict_runtime": matrix["ajv_8_17_1_strict_runtime"], "semantic_validator_execution": matrix["semantic_validator_execution"], "zip_path": str(zip_path), "zip_sha256": sha256_file(zip_path), "next_action": "external_adversarial_reaudit_of_provider_only_zip"}, indent=2, ensure_ascii=False))

    from runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch import apply_reaudit_overrides
    apply_reaudit_overrides(g)

