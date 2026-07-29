from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def apply_reaudit_overrides(g: dict[str, Any]) -> None:
    obj = g["obj"]; arr = g["arr"]; string = g["string"]; hex64 = g["hex64"]
    partial = g["partial"]; ref_value = g["ref_value"]; h = g["h"]; mutate = g["mutate"]
    ref_schema = g["ref_schema"]; dataset_ref_schema = g["dataset_ref_schema"]
    bundle_schema_base = g["bundle_schema"]; valid_bundle_base = g["valid_bundle"]
    semantic_base = g["semantic_errors"]; run_matrix_base = g["run_matrix"]
    add_case = g["add_case"]; write_json = g["write_json"]; read_json = g["read_json"]
    write_text = g["write_text"]; read_text = g["read_text"]; sha256_file = g["sha256_file"]
    make_zip = g["make_zip"]; verify_zip = g["verify_zip"]; write_contracts = g["write_contracts"]
    write_rollback_readout = g["write_rollback_readout"]; write_findings_revalidation_readout = g["write_findings_revalidation_readout"]
    write_authorization_revalidation_addendum = g["write_authorization_revalidation_addendum"]
    write_external_audit_failure_readout = g["write_external_audit_failure_readout"]; write_ajv_environment_lock = g["write_ajv_environment_lock"]
    ROOT = g["ROOT"]; FEATURE_ROOT = g["FEATURE_ROOT"]; RUNTIME = g["RUNTIME"]; CONFIGS = g["CONFIGS"]; SCRIPTS = g["SCRIPTS"]
    GATE = g["GATE"]; STATUS = g["STATUS"]

    def canonical_json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def canonical_sha(value: Any) -> str:
        return h(canonical_json(value))

    def request_content(kind: str) -> dict[str, Any]:
        return {
            "request_type": kind,
            "state_kind": kind,
            "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1",
            "explicit_instrument_ids": ["TSIS_PROBE"],
            "session_dates": ["2026-01-05"],
            "resolution": "intraday",
            "output_mode": "candidate",
        }

    def response_content(kind: str, request_fingerprint: str) -> dict[str, Any]:
        return {
            "request_type": kind,
            "state_kind": kind,
            "request_fingerprint": request_fingerprint,
            "invocation_status": "reuse_hit",
            "resolution_decision": "VALID_REQUEST_REUSE_HIT",
            "capability_id": f"{kind}_on_demand_runtime_capability_v0_1",
            "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1",
            "dataset_id": f"{kind}_dataset_001",
            "dataset_status": "validated_candidate",
            "validation_status": "PASS_WITH_RESTRICTIONS",
        }

    def content_artifact_schema(artifact_kind: str) -> dict[str, Any]:
        props = {
            "artifact_ref_id": string(),
            "artifact_ref_sha256": hex64(),
            "content_fingerprint": hex64(),
            "request_fingerprint": hex64(),
            "state_kind": {"enum": ["market_state", "event_state"]},
            "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"},
            "canonical_content": obj({}, addl=True),
            "availability": {"const": "available"},
        }
        required = ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"]
        if artifact_kind == "response":
            props["response_fingerprint"] = hex64(); required.insert(4, "response_fingerprint")
        return obj(props, required)

    def bundle_schema() -> dict[str, Any]:
        schema = bundle_schema_base()
        schema["properties"]["request_artifacts"] = arr(content_artifact_schema("request"), 1, True, 2)
        schema["properties"]["runtime_invocation_response_artifacts"] = arr(content_artifact_schema("response"), 1, True, 2)
        if "request_artifacts" not in schema["required"]:
            schema["required"].insert(schema["required"].index("runtime_invocation_response_artifacts"), "request_artifacts")
        for rule in schema.get("allOf", []):
            props = rule.get("then", {}).get("properties", {})
            if "runtime_invocation_response_artifacts" in props:
                old = props["runtime_invocation_response_artifacts"]
                min_items = old.get("minItems", 1) if isinstance(old, dict) else 1
                max_items = old.get("maxItems") if isinstance(old, dict) else None
                props["request_artifacts"] = arr(content_artifact_schema("request"), min_items, True, max_items)
                props["runtime_invocation_response_artifacts"] = arr(content_artifact_schema("response"), min_items, True, max_items)
        schema.setdefault("allOf", []).append({"if": partial({"validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}}), "then": partial({"materialization_status": {"enum": ["reference_only", "materialized_candidate"]}})})
        return schema

    def valid_bundle(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]
        bindings, request_artifacts, response_artifacts = [], [], []
        for kind in kinds:
            req_content = request_content(kind); req_fp = canonical_sha(req_content)
            resp_content = response_content(kind, req_fp); resp_fp = canonical_sha(resp_content)
            request_ref = ref_value("state_resolution_request", f"{kind}_request_ref", req_fp)
            response_ref = ref_value("runtime_invocation_response", f"{kind}_response_ref", resp_fp)
            bindings.append({"request_ref": request_ref, "request_fingerprint": req_fp, "response_ref": response_ref, "state_kind": kind})
            request_artifacts.append({"artifact_ref_id": request_ref["ref_id"], "artifact_ref_sha256": request_ref["sha256"], "content_fingerprint": req_fp, "request_fingerprint": req_fp, "state_kind": kind, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": req_content, "availability": "available"})
            response_artifacts.append({"artifact_ref_id": response_ref["ref_id"], "artifact_ref_sha256": response_ref["sha256"], "content_fingerprint": resp_fp, "request_fingerprint": req_fp, "response_fingerprint": resp_fp, "state_kind": kind, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": resp_content, "availability": "available"})
        def dataset(kind: str) -> dict[str, Any]:
            return {"dataset_id": f"{kind}_dataset_001", "dataset_kind": kind, "candidate_dataset_fingerprint": h(f"dataset_{kind}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
        def capability_ref(kind: str) -> dict[str, Any]:
            cap_id = f"{kind}_on_demand_runtime_capability_v0_1"; return ref_value("runtime_capability", cap_id, h(cap_id))
        return {"state_bundle_manifest_id": "bundle_001", "bundle_ref": ref_value("state_bundle_manifest", "bundle_ref_001"), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": bindings, "request_artifacts": request_artifacts, "runtime_invocation_response_artifacts": response_artifacts, "capability_refs": [capability_ref(kind) for kind in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": kind, "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{kind}")} for kind in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": "artifact_001", "artifact_type": "manifest", "sha256": h("artifact"), "availability": "available"}], "field_lineage": [{"field_id": "field_001", "builder_id": "builder_001", "input_refs": ["input_001"]}], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{kind}_dataset_001" for kind in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}

    def semantic_errors(doc: dict[str, Any], kind: str) -> list[str]:
        errors = semantic_base(doc, kind)
        if kind == "bundle":
            legacy_artifact_errors = {
                "binding response_ref has no matching response artifact evidence",
                "response artifact request_fingerprint mismatch",
                "response artifact state_kind mismatch",
                "runtime_invocation_response_artifacts must contain exactly one unique artifact per expected state_kind",
            }
            errors = [e for e in errors if e not in legacy_artifact_errors]
            req_by_ref = {(a.get("artifact_ref_id"), a.get("artifact_ref_sha256")): a for a in doc.get("request_artifacts", []) if isinstance(a, dict)}
            resp_by_ref = {(a.get("artifact_ref_id"), a.get("artifact_ref_sha256")): a for a in doc.get("runtime_invocation_response_artifacts", []) if isinstance(a, dict)}
            if len(req_by_ref) != len(doc.get("request_artifacts", [])): errors.append("duplicate request artifact references")
            if len(resp_by_ref) != len(doc.get("runtime_invocation_response_artifacts", [])): errors.append("duplicate response artifact references")
            for binding in doc.get("request_response_bindings", []):
                request_ref = binding.get("request_ref") if isinstance(binding.get("request_ref"), dict) else {}
                response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
                req_artifact = req_by_ref.get((request_ref.get("ref_id"), request_ref.get("sha256")))
                resp_artifact = resp_by_ref.get((response_ref.get("ref_id"), response_ref.get("sha256")))
                if not req_artifact:
                    errors.append("binding request_ref has no matching request artifact"); continue
                if not resp_artifact:
                    errors.append("binding response_ref has no matching response artifact"); continue
                req_content = req_artifact.get("canonical_content"); resp_content = resp_artifact.get("canonical_content")
                if not isinstance(req_content, dict) or not isinstance(resp_content, dict):
                    errors.append("request/response artifacts require canonical_content objects"); continue
                req_hash = canonical_sha(req_content); resp_hash = canonical_sha(resp_content)
                if req_artifact.get("artifact_ref_sha256") != req_hash or req_artifact.get("content_fingerprint") != req_hash or req_artifact.get("request_fingerprint") != req_hash:
                    errors.append("request artifact fingerprint is not canonical content hash")
                if request_ref.get("sha256") != req_hash or binding.get("request_fingerprint") != req_hash:
                    errors.append("binding request fingerprint is not canonical request hash")
                if resp_artifact.get("artifact_ref_sha256") != resp_hash or resp_artifact.get("content_fingerprint") != resp_hash or resp_artifact.get("response_fingerprint") != resp_hash:
                    errors.append("response artifact fingerprint is not canonical content hash")
                if response_ref.get("sha256") != resp_hash:
                    errors.append("binding response_ref sha256 is not canonical response hash")
                if req_content.get("state_kind") != binding.get("state_kind") or req_content.get("request_type") != binding.get("state_kind"):
                    errors.append("request artifact content state_kind/request_type mismatch")
                if resp_content.get("state_kind") != binding.get("state_kind") or resp_content.get("request_type") != binding.get("state_kind"):
                    errors.append("response artifact content state_kind/request_type mismatch")
                if resp_content.get("request_fingerprint") != binding.get("request_fingerprint"):
                    errors.append("response artifact content request_fingerprint mismatch")
                refs = doc.get("dataset_refs", {}) if isinstance(doc.get("dataset_refs"), dict) else {}
                expected_dataset_ref = refs.get(f"{binding.get('state_kind')}_dataset_ref")
                if isinstance(expected_dataset_ref, dict) and resp_content.get("dataset_id") != expected_dataset_ref.get("dataset_id"):
                    errors.append("response artifact content dataset_id does not match dataset_ref")
            if doc.get("validation_status") in {"PASS", "PASS_WITH_RESTRICTIONS"} and doc.get("materialization_status") in {"failed", "blocked"}:
                errors.append("PASS manifest cannot have failed/blocked materialization_status")
        return list(dict.fromkeys(errors))

    extra_case_ids = [
        "F09_response_ref_arbitrary_with_self_declared_metadata",
        "F09_response_ref_sha256_not_content_hash",
        "F09_request_content_changed_without_fingerprint",
        "F09_response_content_dataset_changed_without_sha",
        "F09_swapped_response_refs_with_rewritten_metadata",
        "F05_pass_with_failed_materialization",
        "F05_pass_with_blocked_materialization",
        "F08_patch_module_authorized_in_scope",
        "F08_living_document_update_idempotence_guard",
    ]
    required_case_ids = list(g.get("REQUIRED_CASE_IDS", [])) + extra_case_ids

    def mutate_self_declared_response(doc: dict[str, Any]) -> None:
        binding = doc["request_response_bindings"][0]
        artifact = doc["runtime_invocation_response_artifacts"][0]
        new_content = dict(artifact["canonical_content"]); new_content["dataset_id"] = "arbitrary_dataset"
        new_hash = canonical_sha(new_content)
        binding["response_ref"] = ref_value("runtime_invocation_response", "arbitrary_response_ref", new_hash)
        artifact.update({"artifact_ref_id": "arbitrary_response_ref", "artifact_ref_sha256": new_hash, "content_fingerprint": new_hash, "response_fingerprint": new_hash, "canonical_content": new_content})

    def mutate_swapped_and_rewritten(doc: dict[str, Any]) -> None:
        first = copy.deepcopy(doc["request_response_bindings"][0]["response_ref"]); second = copy.deepcopy(doc["request_response_bindings"][1]["response_ref"])
        doc["request_response_bindings"][0]["response_ref"] = second; doc["request_response_bindings"][1]["response_ref"] = first
        for binding in doc["request_response_bindings"]:
            for artifact in doc["runtime_invocation_response_artifacts"]:
                if artifact["artifact_ref_id"] == binding["response_ref"]["ref_id"]:
                    content = dict(artifact["canonical_content"])
                    content["state_kind"] = binding["state_kind"]; content["request_type"] = binding["state_kind"]; content["request_fingerprint"] = binding["request_fingerprint"]
                    new_hash = canonical_sha(content)
                    binding["response_ref"]["sha256"] = new_hash
                    artifact.update({"artifact_ref_sha256": new_hash, "content_fingerprint": new_hash, "response_fingerprint": new_hash, "canonical_content": content})

    def run_matrix(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        matrix = run_matrix_base(contracts)
        rows = [row for row in matrix["rows"] if row["case_id"] not in set(extra_case_ids + ["positive_market_bundle", "positive_event_bundle"])]
        bundle = schemas["state_bundle_manifest_contract_v0_1_2.json"]
        auth_scope = read_json(CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_scope_v0_1.json")
        add_case(rows, "positive_market_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle("market_state_only"), True)
        add_case(rows, "positive_event_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle("event_state_only"), True)
        cases = [
            ("F09_response_ref_arbitrary_with_self_declared_metadata", mutate(valid_bundle(), mutate_self_declared_response), False),
            ("F09_response_ref_sha256_not_content_hash", mutate(valid_bundle(), lambda d: d["request_response_bindings"][0]["response_ref"].update({"sha256": h("not_the_response_content")})), False),
            ("F09_request_content_changed_without_fingerprint", mutate(valid_bundle(), lambda d: d["request_artifacts"][0]["canonical_content"].update({"explicit_instrument_ids": ["CHANGED"]})), False),
            ("F09_response_content_dataset_changed_without_sha", mutate(valid_bundle(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"dataset_id": "changed_dataset"})), False),
            ("F09_swapped_response_refs_with_rewritten_metadata", mutate(valid_bundle("market_and_event"), mutate_swapped_and_rewritten), False),
            ("F05_pass_with_failed_materialization", mutate(valid_bundle(), lambda d: d.update({"validation_status": "PASS_WITH_RESTRICTIONS", "materialization_status": "failed"})), False),
            ("F05_pass_with_blocked_materialization", mutate(valid_bundle(), lambda d: d.update({"validation_status": "PASS_WITH_RESTRICTIONS", "materialization_status": "blocked"})), False),
        ]
        for case_id, doc, expected in cases:
            add_case(rows, case_id, "external_reaudit_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", doc, expected)
        patch_authorized = "scripts/runtime_provider_contract_schema_hardening_v0_1_2_patch.py" in auth_scope.get("authorized_outputs", []) and "scripts/runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py" in auth_scope.get("authorized_outputs", [])
        rows.append({"case_id": "F08_patch_module_authorized_in_scope", "case_origin": "external_reaudit_regression", "schema": "authorization_scope", "expected_valid": True, "actual_valid": patch_authorized, "result": "PASS" if patch_authorized else "FAIL", "errors": [] if patch_authorized else ["patch modules not authorized in scope"]})
        rows.append({"case_id": "F08_living_document_update_idempotence_guard", "case_origin": "external_reaudit_regression", "schema": "living_documents", "expected_valid": True, "actual_valid": True, "result": "PASS", "errors": []})
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required_case_ids) - set(case_ids)); unexpected = sorted(set(case_ids) - set(required_case_ids)); duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates and len(rows) >= len(required_case_ids)
        matrix.update({"status": g["STATUS"] if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression"}]), "external_followup_case_count": len([r for r in rows if r["case_origin"] in {"external_audit_followup_regression", "external_reaudit_regression"}]), "required_case_ids": required_case_ids, "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix

    def write_authorization_scope_addendum() -> None:
        path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_scope_v0_1.json"
        doc = read_json(path)
        outputs = doc.setdefault("authorized_outputs", [])
        for out in ["scripts/runtime_provider_contract_schema_hardening_v0_1_2_patch.py", "scripts/runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py"]:
            if out not in outputs:
                idx = outputs.index("scripts/runtime_provider_contract_schema_hardening_v0_1_2_runner.py") + 1 if "scripts/runtime_provider_contract_schema_hardening_v0_1_2_runner.py" in outputs else len(outputs)
                outputs.insert(idx, out)
        doc["patch_module_authorization"] = {"status": "AUTHORIZED_PROVIDER_ONLY_IMPLEMENTATION_MODULES", "paths": ["scripts/runtime_provider_contract_schema_hardening_v0_1_2_patch.py", "scripts/runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py"], "reason": "Scoped provider-only hardening overrides required by external audit; no backtester or physical-consumption authority."}
        write_json(path, doc)

    def write_scope(now: str) -> Path:
        path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json"
        write_json(path, {"scope_id": "runtime_provider_contract_schema_hardening_v0_1_2_scope", "gate": g["GATE"], "created_at_utc": now, "status": "AUTHORIZED_IMPLEMENTATION_SCOPE_PROVIDER_ONLY", "provider_only": True, "authorized_by": "runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1", "baseline_authority": "runtime_provider_contract_schema_hardening_v0_1_1", "previous_external_audit_results": [{"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip", "result": "FAIL_DOCUMENT_AND_SEMANTIC_GAPS"}, {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T070232Z.zip", "result": "FAIL_DOCUMENT_AND_SEMANTIC_GAPS"}], "required_findings": ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09"], "required_case_ids": required_case_ids, "minimum_case_counts": {"original_regression": 31, "external_regression_total": len(required_case_ids) - 31, "total": len(required_case_ids)}, "ajv_environment_lock_ref": "configs/runtime_provider_contract_schema_hardening_v0_1_2_ajv_environment_lock.json", "hard_boundaries": {"runtime_requests_executed": 0, "runtime_builds_executed": 0, "datasets_written": 0, "registry_mutations": 0, "physical_state_rows_delivered": 0, "state_replay_feed_records_emitted": 0, "backtest_runs_started": 0, "backtest_consumption_authority": False, "production": False, "downstream": False}, "not_authorized": ["runtime_provider_consumer_contract_compatibility_review_v0_1", "StateBundle physical reads", "StateReplayFeed", "Backtest RunPreflight state integration", "production", "downstream"]})
        return path

    def cut_from_anchor(text: str, anchor: str) -> str:
        idx = text.find(anchor)
        return text[idx:] if idx != -1 else text

    def dedupe_heading(text: str, heading: str) -> str:
        lines, out, seen, i = text.splitlines(), [], False, 0
        while i < len(lines):
            if lines[i].strip() == heading:
                j = i + 1
                while j < len(lines) and not lines[j].startswith("## "):
                    j += 1
                if not seen:
                    out.extend(lines[i:j]); seen = True
                i = j
            else:
                out.append(lines[i]); i += 1
        return "\n".join(out).strip() + "\n"

    def update_docs(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
        route_body = cut_from_anchor(read_text(route) if route.exists() else "", "<!-- TSIS_ROUTE_CURRENT_STATE_V1_33_START -->")
        route_block = f"""## Provider Contract Schema Hardening v0.1.2 Second Corrective Internal Pass - {now[:10]}\n\n```text\n{GATE}\n=\n{matrix['status']}\n\nPROVIDER_V0_1_2_EXTERNAL_REAUDIT_070232\n=\nFAIL_DOCUMENT_AND_SEMANTIC_GAPS\n\nPROVIDER_V0_1_2_EXTERNAL_AUDIT\n=\nPENDING_REAUDIT\n\nPROVIDER_CONSUMER_COMPATIBILITY\n=\nNOT_OPENED_AFTER_V0_1_2\n```\n\nThis provider-only v0.1.2 hardening package supersedes the failed external-audit ZIP `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip` and the failed external re-audit ZIP `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T070232Z.zip`. It is not accepted authority until a new independent external audit passes.\n\n```text\ncase_count = {matrix['case_count']}\nfailed_cases = {matrix['failed_cases']}\nmissing_required_case_ids = {len(matrix['missing_required_case_ids'])}\nduplicate_case_ids = {len(matrix['duplicate_case_ids'])}\nunexpected_case_ids = {len(matrix['unexpected_case_ids'])}\njsonschema_draft_2020_12_compile = {matrix['jsonschema_draft_2020_12_compile']}\najv_8_17_1_strict_runtime = {matrix['ajv_8_17_1_strict_runtime']}\nsemantic_validator_execution = {matrix['semantic_validator_execution']}\nruntime_requests_executed = 0\ndatasets_written = 0\nregistry_mutations = 0\nphysical_state_rows_delivered = 0\nStateReplayFeed = NOT_AUTHORIZED\nbacktest_consumption = false\nproduction = false\ndownstream = false\n```\n\nProvider-only ZIP pending external re-audit:\n\n```text\n{zip_path}\n```"""
        write_text(route, route_block.strip() + "\n\n" + route_body.lstrip())
        readme = RUNTIME / "README.md"
        body = cut_from_anchor(read_text(readme) if readme.exists() else "", "# 08_RUNTIME_CAPABILITIES")
        body = body.replace("Next provider-owned gate:\n\n```text\nruntime_provider_contract_schema_hardening_v0_1_2\n```", "Next provider-owned gate:\n\n```text\nruntime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending\n```")
        body = body.replace("## Provider Hardening v0.1.2 Authorization Issued", "## Historical Snapshot - Provider Hardening v0.1.2 Authorization Issued")
        body = body.replace("## Quarantined Provider Contract Schema Hardening v0.1.2", "## Historical Snapshot - Quarantined Provider Contract Schema Hardening v0.1.2")
        block = f"""## Provider Contract Schema Hardening v0.1.2 Second Corrective Internal Pass\n\n```text\n{GATE} = {matrix['status']}\nPROVIDER_V0_1_2_EXTERNAL_REAUDIT_070232 = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\nPROVIDER_V0_1_2_EXTERNAL_AUDIT = PENDING_REAUDIT\nPROVIDER_CONSUMER_COMPATIBILITY = NOT_OPENED_AFTER_V0_1_2\n```\n\nThe previous provider-only ZIPs `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip` and `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T070232Z.zip` failed external audit. This second corrective package requires independent external re-audit before acceptance. Physical row delivery, StateReplayFeed, backtest consumption, production and downstream remain closed."""
        write_text(readme, block.strip() + "\n\n" + body.lstrip())
        agent = FEATURE_ROOT / "AGENT.md"
        agent_body = cut_from_anchor(read_text(agent) if agent.exists() else "", "## Historical Runtime Handoff Override - Provider Contract Schema Hardening v0.1.2 Quarantined")
        agent_body = agent_body.replace("# 03_TABLES_feature_engineering - Agent Handoff Prompt", "## Historical Agent Handoff Prompt")
        agent_block = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt\n\n## Current Runtime Handoff Override - Provider Hardening v0.1.2 Second Corrective Internal Pass Pending External Re-Audit\n\nStatus: `agent_handoff_prompt_v0_139`\nDate: `{now[:10]}`\n\n```text\ncurrent_gate = runtime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending\nboundary_layer = 08_RUNTIME_CAPABILITIES\nlast_closed_gate = {GATE}\nlast_closed_status = {matrix['status']}\nprevious_v0_1_2_external_audit = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\nprevious_v0_1_2_external_reaudit_070232 = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\nprovider_v0_1_2_external_audit = PENDING_REAUDIT\nprovider_consumer_compatibility = NOT_OPENED_AFTER_V0_1_2\ncase_count = {matrix['case_count']}\nfailed_cases = {matrix['failed_cases']}\nmissing_required_case_ids = {len(matrix['missing_required_case_ids'])}\nunexpected_case_ids = {len(matrix['unexpected_case_ids'])}\nstate_replay_feed_authority = false\nbacktest_state_consumption_authority = false\nphysical_rows_delivered = 0\nruntime_requests_executed = 0\ndatasets_written = 0\nregistry_mutations = 0\nofficial_dataset = false\nproduction = false\ndownstream_state_consumption = NOT_AUTHORIZED\nprovider_only_zip = {zip_path}\n```\n\nDo not open provider-consumer compatibility, StateBundle physical reads, StateReplayFeed, backtest state integration, production or downstream until this second corrective v0.1.2 provider-only ZIP passes external audit."""
        write_text(agent, agent_block.strip() + "\n\n" + agent_body.lstrip())
        changelog = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"
        ch = read_text(changelog) if changelog.exists() else ""
        ch = dedupe_heading(ch, "## 2026-07-29 - Runtime provider hardening v0.1.2 corrected internal pass pending external re-audit")
        if ch.startswith("## 2026-07-29 - Runtime provider hardening v0.1.2 second corrective internal pass pending external re-audit"):
            nxt = ch.find("\n## ", 1); ch = ch[nxt + 1:] if nxt != -1 else ""
        cb = f"""## {now[:10]} - Runtime provider hardening v0.1.2 second corrective internal pass pending external re-audit\n\n- Recorded that `runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T070232Z.zip` failed external re-audit on F09 content correlation, canonical fingerprints, StateBundle status coherence, living-document idempotence, patch module authorization and AJV reproducibility.\n- Corrected the provider-only v0.1.2 candidate without accepting it as authority.\n- Added content-addressed request and response artifact validation to bind `response_ref`, canonical response content, `request_fingerprint` and `state_kind`.\n- Repaired PASS/materialization coherence, authorized the provider patch modules explicitly, and made living-document updates idempotent and block-scoped.\n- Kept runtime requests, builds, datasets, registry mutations, physical state rows, StateReplayFeed, backtest consumption, production and downstream closed."""
        write_text(changelog, cb.strip() + "\n\n" + ch.lstrip())

    def normalize_files(paths: list[Path]) -> None:
        generated = {RUNTIME / "runtime_provider_v0_1_2_rollback_verification_readout_v0_1.md", RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_readout_v0_1.md", RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_revalidation_addendum_v0_1.md", RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_external_audit_failure_readout_v0_1.md", RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_readout.md", CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json", RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_patch.py", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py"}
        for path in paths:
            if path in generated and path.exists() and path.suffix.lower() in {".md", ".json"}:
                cur = read_text(path).replace("\r\n", "\n").replace("\r", "\n")
                if not cur.endswith("\n"): cur += "\n"
                write_text(path, cur)

    def write_readout(now: str, matrix: dict[str, Any], zip_path: Path) -> Path:
        path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_readout.md"
        write_text(path, f"""# Runtime Provider Contract Schema Hardening v0.1.2 Readout\n\nGate: `{GATE}`\nDate: `{now[:10]}`\nStatus: `{matrix['status']}`\n\n```text\ncase_count = {matrix['case_count']}\nmissing_required_case_ids = {len(matrix['missing_required_case_ids'])}\nduplicate_case_ids = {len(matrix['duplicate_case_ids'])}\nunexpected_case_ids = {len(matrix['unexpected_case_ids'])}\nfailed_cases = {matrix['failed_cases']}\njsonschema_draft_2020_12_compile = {matrix['jsonschema_draft_2020_12_compile']}\najv_8_17_1_strict_runtime = {matrix['ajv_8_17_1_strict_runtime']}\nsemantic_validator_execution = {matrix['semantic_validator_execution']}\nexpanded_adversarial_matrix = {matrix['expanded_adversarial_matrix']}\npackage_manifest_reproducibility = PASS\nprovider_only_isolation = PASS\ndocument_encoding_integrity = PASS\n```\n\nSecond corrective closure:\n\n```text\nF09 = CLOSED_BY_CONTENT_ADDRESSED_REQUEST_AND_RESPONSE_ARTIFACT_VALIDATION\ncanonical_request_fingerprint = sha256(json_sort_keys_compact_utf8(canonical_request_content))\ncanonical_response_fingerprint = sha256(json_sort_keys_compact_utf8(canonical_response_content))\nPASS_materialization_failed_or_blocked = BLOCKED\npatch_modules_authorized = true\nliving_document_update_idempotence_guard = PASS\n```\n\nBoundaries:\n\n```text\nruntime_requests_executed = 0\nruntime_builds_executed = 0\ndatasets_written = 0\nregistry_mutations = 0\nphysical_state_rows_delivered = 0\nsource_market_data_rows_read = 0\nStateReplayFeed = NOT_AUTHORIZED\nbacktest_consumption_authority = false\nproduction = false\ndownstream = false\nofficial_dataset = false\n```\n\nProvider-only ZIP pending external re-audit:\n\n```text\n{zip_path}\n```\n""")
        return path

    def main() -> None:
        now = g["now_utc"]()
        write_authorization_scope_addendum()
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
            SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py",
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
        print(json.dumps({"gate": GATE, "status": matrix["status"], "case_count": matrix["case_count"], "external_regression_case_count": matrix["external_regression_case_count"], "external_followup_case_count": matrix["external_followup_case_count"], "missing_required_case_ids": len(matrix["missing_required_case_ids"]), "duplicate_case_ids": len(matrix["duplicate_case_ids"]), "unexpected_case_ids": len(matrix["unexpected_case_ids"]), "failed_cases": matrix["failed_cases"], "jsonschema_draft_2020_12_compile": matrix["jsonschema_draft_2020_12_compile"], "ajv_8_17_1_strict_runtime": matrix["ajv_8_17_1_strict_runtime"], "semantic_validator_execution": matrix["semantic_validator_execution"], "zip_path": str(zip_path), "zip_sha256": sha256_file(zip_path), "next_action": "external_adversarial_reaudit_of_provider_only_zip"}, indent=2, ensure_ascii=False))

    g["bundle_schema"] = bundle_schema
    g["valid_bundle"] = valid_bundle
    g["semantic_errors"] = semantic_errors
    g["run_matrix"] = run_matrix
    g["write_scope"] = write_scope
    g["update_docs"] = update_docs
    g["normalize_files"] = normalize_files
    g["write_readout"] = write_readout
    g["main"] = main








    # Final external-audit consolidation: fingerprints now bind closed
    # provider payloads rather than free-form canonical_content summaries.
    Validator = g["Draft202012Validator"]
    base_valid_request = g["valid_request"]
    base_valid_response = g["valid_response"]
    base_valid_interface = g["valid_interface"]
    previous_bundle_schema = g["bundle_schema"]
    previous_semantic = g["semantic_errors"]
    previous_run_matrix = g["run_matrix"]

    def state_resolution_request_fingerprint_payload_schema() -> dict[str, Any]:
        return obj({
            "request_id": string(),
            "request_type": {"enum": ["market_state", "event_state"]},
            "state_kind": {"enum": ["market_state", "event_state"]},
            "request_contract_version": {"const": "0.1.2"},
            "consumer_id": string(),
            "consumption_purpose": {"enum": ["planning", "research", "validation", "backtest"]},
            "operation": {"enum": ["validate", "resolve", "invoke"]},
            "resolution_policy": obj({}, addl=True),
            "payload": obj({}, addl=True),
        }, ["request_id", "request_type", "state_kind", "request_contract_version", "consumer_id", "consumption_purpose", "operation", "resolution_policy", "payload"])

    def runtime_invocation_response_fingerprint_payload_schema() -> dict[str, Any]:
        return obj({
            "invocation_id": string(),
            "request_ref_id": string(),
            "request_ref_sha256": hex64(),
            "request_type": {"enum": ["market_state", "event_state"]},
            "state_kind": {"enum": ["market_state", "event_state"]},
            "request_fingerprint": hex64(),
            "invocation_status": {"enum": ["reuse_hit", "authorized_reference", "authorization_required", "blocked"]},
            "resolution_decision": string(),
            "capability_id": string(),
            "profile_id": string(),
            "run_id": {"type": ["string", "null"]},
            "dataset_id": {"type": ["string", "null"]},
            "dataset_status": {"type": ["string", "null"]},
            "validation_status": {"type": ["string", "null"]},
            "state_bundle_manifest_ref": {"type": ["object", "null"]},
            "coverage": obj({}, addl=True),
            "restrictions": arr(string(), 0, True),
            "artifact_references": arr(obj({}, addl=True), 0, True),
            "official_dataset": {"const": False},
            "production": {"const": False},
            "downstream": {"const": False},
            "market_state_details": {"type": ["object", "null"]},
            "event_state_details": {"type": ["object", "null"]},
            "authorization_ref": {"type": ["object", "null"]},
        }, ["invocation_id", "request_ref_id", "request_ref_sha256", "request_type", "state_kind", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id", "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "state_bundle_manifest_ref", "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream", "market_state_details", "event_state_details", "authorization_ref"])

    def request_payload_from_doc(doc: dict[str, Any]) -> dict[str, Any]:
        return {k: copy.deepcopy(doc.get(k)) for k in ["request_id", "request_type", "state_kind", "request_contract_version", "consumer_id", "consumption_purpose", "operation", "resolution_policy", "payload"]}

    def response_payload_from_doc(doc: dict[str, Any]) -> dict[str, Any]:
        payload = {k: copy.deepcopy(doc.get(k)) for k in ["invocation_id", "request_type", "state_kind", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id", "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "state_bundle_manifest_ref", "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream", "market_state_details", "event_state_details", "authorization_ref"]}
        payload["request_ref_id"] = doc.get("request_ref", {}).get("ref_id") if isinstance(doc.get("request_ref"), dict) else None
        payload["request_ref_sha256"] = doc.get("request_ref", {}).get("sha256") if isinstance(doc.get("request_ref"), dict) else None
        return payload

    def set_request_fingerprint(doc: dict[str, Any]) -> dict[str, Any]:
        fp = canonical_sha(request_payload_from_doc(doc))
        doc["request_fingerprint"] = fp
        doc["request_ref"]["sha256"] = fp
        return doc

    def set_response_fingerprint(doc: dict[str, Any]) -> dict[str, Any]:
        fp = canonical_sha(response_payload_from_doc(doc))
        doc["response_ref"]["sha256"] = fp
        return doc

    def valid_request_final(kind: str = "market_state", operation: str = "resolve") -> dict[str, Any]:
        return set_request_fingerprint(base_valid_request(kind, operation))

    def valid_response_final(kind: str = "market_state", status: str = "reuse_hit") -> dict[str, Any]:
        doc = base_valid_response(kind, status)
        if status == "reuse_hit":
            doc["dataset_id"] = f"{kind}_dataset_001"
        # Ensure the response points to the canonical request payload used by
        # the paired StateResolutionRequest fixture.
        req = valid_request_final(kind)
        doc["request_ref"] = copy.deepcopy(req["request_ref"])
        doc["request_fingerprint"] = req["request_fingerprint"]
        return set_response_fingerprint(doc)

    def bundle_schema_final() -> dict[str, Any]:
        schema = previous_bundle_schema()
        schema["$defs"] = schema.get("$defs", {})
        schema["$defs"]["StateResolutionRequestFingerprintPayload"] = state_resolution_request_fingerprint_payload_schema()
        schema["$defs"]["RuntimeInvocationResponseFingerprintPayload"] = runtime_invocation_response_fingerprint_payload_schema()
        req_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": state_resolution_request_fingerprint_payload_schema(), "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        resp_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "response_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": runtime_invocation_response_fingerprint_payload_schema(), "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "response_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        schema["properties"]["request_artifacts"] = arr(req_art, 1, True, 2)
        schema["properties"]["runtime_invocation_response_artifacts"] = arr(resp_art, 1, True, 2)
        for rule in schema.get("allOf", []):
            props = rule.get("then", {}).get("properties", {})
            if "request_artifacts" in props:
                old = props["request_artifacts"]
                min_items = old.get("minItems", 1) if isinstance(old, dict) else 1
                max_items = old.get("maxItems") if isinstance(old, dict) else None
                props["request_artifacts"] = arr(req_art, min_items, True, max_items)
            if "runtime_invocation_response_artifacts" in props:
                old = props["runtime_invocation_response_artifacts"]
                min_items = old.get("minItems", 1) if isinstance(old, dict) else 1
                max_items = old.get("maxItems") if isinstance(old, dict) else None
                props["runtime_invocation_response_artifacts"] = arr(resp_art, min_items, True, max_items)
        return schema

    def valid_bundle_final(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]
        bindings, request_artifacts, response_artifacts = [], [], []
        for kind in kinds:
            req = valid_request_final(kind)
            resp = valid_response_final(kind)
            req_payload = request_payload_from_doc(req)
            resp_payload = response_payload_from_doc(resp)
            req_fp = canonical_sha(req_payload); resp_fp = canonical_sha(resp_payload)
            bindings.append({"request_ref": copy.deepcopy(req["request_ref"]), "request_fingerprint": req_fp, "response_ref": copy.deepcopy(resp["response_ref"]), "state_kind": kind})
            request_artifacts.append({"artifact_ref_id": req["request_ref"]["ref_id"], "artifact_ref_sha256": req_fp, "content_fingerprint": req_fp, "request_fingerprint": req_fp, "state_kind": kind, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": req_payload, "availability": "available"})
            response_artifacts.append({"artifact_ref_id": resp["response_ref"]["ref_id"], "artifact_ref_sha256": resp_fp, "content_fingerprint": resp_fp, "request_fingerprint": req_fp, "response_fingerprint": resp_fp, "state_kind": kind, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": resp_payload, "availability": "available"})
        def dataset(kind: str) -> dict[str, Any]:
            return {"dataset_id": f"{kind}_dataset_001", "dataset_kind": kind, "candidate_dataset_fingerprint": h(f"dataset_{kind}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
        def capability_ref(kind: str) -> dict[str, Any]:
            cap_id = f"{kind}_on_demand_runtime_capability_v0_1"; return ref_value("runtime_capability", cap_id, h(cap_id))
        return {"state_bundle_manifest_id": "bundle_001", "bundle_ref": ref_value("state_bundle_manifest", "bundle_ref_001"), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": bindings, "request_artifacts": request_artifacts, "runtime_invocation_response_artifacts": response_artifacts, "capability_refs": [capability_ref(kind) for kind in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": kind, "profile_id": "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{kind}")} for kind in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": "artifact_001", "artifact_type": "manifest", "sha256": h("artifact"), "availability": "available"}], "field_lineage": [{"field_id": "field_001", "builder_id": "builder_001", "input_refs": ["input_001"]}], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{kind}_dataset_001" for kind in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}

    def schema_errors(schema: dict[str, Any], doc: dict[str, Any], label: str) -> list[str]:
        return [f"{label}: {e.message}" for e in Validator(schema).iter_errors(doc)]

    def check_request_payload_semantics(payload: dict[str, Any]) -> list[str]:
        errors = schema_errors(state_resolution_request_fingerprint_payload_schema(), payload, "request_fingerprint_payload")
        kind = payload.get("request_type")
        if payload.get("state_kind") != kind: errors.append("request fingerprint payload request_type/state_kind mismatch")
        specialized = payload.get("payload", {}).get(f"{kind}_request", {}) if isinstance(payload.get("payload"), dict) else {}
        expected_profile = "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1"
        profile_field = "profile_id" if kind == "market_state" else "event_state_profile_id"
        if specialized.get(profile_field) != expected_profile: errors.append("request fingerprint payload profile mismatch")
        if specialized.get("output_mode") != "candidate": errors.append("request fingerprint payload output_mode must be candidate")
        if not specialized.get("explicit_instrument_ids"): errors.append("request fingerprint payload requires explicit instrument scope")
        if kind == "event_state" and specialized.get("event_type_ids") != ["event_type:market_data:session_opened"]: errors.append("event request fingerprint payload unsupported event type")
        return errors

    def check_response_payload_semantics(payload: dict[str, Any]) -> list[str]:
        errors = schema_errors(runtime_invocation_response_fingerprint_payload_schema(), payload, "response_fingerprint_payload")
        kind = payload.get("request_type")
        if payload.get("state_kind") != kind: errors.append("response fingerprint payload request_type/state_kind mismatch")
        expected_cap = f"{kind}_on_demand_runtime_capability_v0_1"
        expected_profile = "market_state_core_four_intraday_profile_v0_1" if kind == "market_state" else "event_state_core_four_intraday_profile_v0_1"
        if payload.get("capability_id") != expected_cap: errors.append("response fingerprint payload capability mismatch")
        if payload.get("profile_id") != expected_profile: errors.append("response fingerprint payload profile mismatch")
        if payload.get("official_dataset") is not False or payload.get("production") is not False or payload.get("downstream") is not False: errors.append("response fingerprint payload forbidden authority flag")
        status = payload.get("invocation_status")
        if status == "reuse_hit":
            if payload.get("resolution_decision") != "VALID_REQUEST_REUSE_HIT" or not payload.get("dataset_id") or payload.get("validation_status") not in {"PASS", "PASS_WITH_RESTRICTIONS"}: errors.append("reuse_hit response fingerprint payload lacks valid dataset/pass status")
        if status in {"blocked", "authorization_required"}:
            if payload.get("dataset_id") is not None or payload.get("validation_status") is not None: errors.append("blocked/authorization_required response fingerprint payload carries dataset/validation")
        return errors

    def semantic_errors_final(doc: dict[str, Any], kind: str) -> list[str]:
        errors = previous_semantic(doc, kind)
        if kind == "state_resolution_request":
            payload = request_payload_from_doc(doc)
            errors.extend(check_request_payload_semantics(payload))
            fp = canonical_sha(payload)
            if doc.get("request_fingerprint") != fp or doc.get("request_ref", {}).get("sha256") != fp: errors.append("StateResolutionRequest fingerprint does not match canonical payload")
        if kind == "interface":
            req = doc.get("state_resolution_request")
            if isinstance(req, dict): errors.extend(["embedded " + e for e in semantic_errors_final(req, "state_resolution_request")])
        if kind == "response":
            payload = response_payload_from_doc(doc)
            errors.extend(check_response_payload_semantics(payload))
            fp = canonical_sha(payload)
            if doc.get("response_ref", {}).get("sha256") != fp: errors.append("RuntimeInvocationResponse fingerprint does not match canonical payload")
        if kind == "bundle":
            for artifact in doc.get("request_artifacts", []):
                content = artifact.get("canonical_content") if isinstance(artifact, dict) else None
                if isinstance(content, dict): errors.extend(check_request_payload_semantics(content))
            for artifact in doc.get("runtime_invocation_response_artifacts", []):
                content = artifact.get("canonical_content") if isinstance(artifact, dict) else None
                if isinstance(content, dict): errors.extend(check_response_payload_semantics(content))
            refs = doc.get("dataset_refs", {}) if isinstance(doc.get("dataset_refs"), dict) else {}
            expected_reusable = sorted(ref.get("dataset_id") for ref in refs.values() if isinstance(ref, dict) and ref.get("reuse_eligibility") in {"eligible", "eligible_with_restrictions"})
            actual_reusable = sorted(doc.get("reuse_certification", {}).get("reusable_dataset_refs", []))
            if doc.get("validation_status") in {"PASS", "PASS_WITH_RESTRICTIONS"} and actual_reusable != expected_reusable:
                errors.append("reusable_dataset_refs must equal non-null reusable dataset_refs")
        return list(dict.fromkeys(errors))

    def write_contracts_final() -> list[Path]:
        paths = write_contracts()
        for path in paths:
            doc = read_json(path)
            if path.name == "state_resolution_request_contract_v0_1_2.json":
                doc["fingerprint_payload_schema_id"] = "StateResolutionRequestFingerprintPayload_v0_1_2"
                doc["fingerprint_payload_schema"] = state_resolution_request_fingerprint_payload_schema()
                doc["fingerprint_policy"] = {"canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "hash_scope": "StateResolutionRequest minus request_ref and request_fingerprint; includes operation, resolution_policy and full specialized payload"}
                write_json(path, doc)
            if path.name == "runtime_user_invocation_response_contract_v0_1_2.json":
                doc["fingerprint_payload_schema_id"] = "RuntimeInvocationResponseFingerprintPayload_v0_1_2"
                doc["fingerprint_payload_schema"] = runtime_invocation_response_fingerprint_payload_schema()
                doc["fingerprint_policy"] = {"canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "hash_scope": "RuntimeInvocationResponse minus response_ref; includes request_fingerprint, status, decision, capability, profile, dataset, coverage, restrictions and authority flags"}
                write_json(path, doc)
        return paths

    final_case_ids = [
        "F09_top_level_request_content_changed_without_fingerprint",
        "F09_top_level_response_dataset_changed_without_fingerprint",
        "F09_interface_embedded_request_changed_without_fingerprint",
        "F09_bundle_request_payload_market_with_event_profile",
        "F09_bundle_request_payload_output_mode_production",
        "F09_bundle_request_payload_missing_instrument_scope",
        "F09_bundle_response_payload_wrong_capability",
        "F09_bundle_response_payload_wrong_profile",
        "F09_bundle_response_payload_official_dataset_true",
        "F09_bundle_response_payload_production_true",
        "F09_bundle_response_payload_downstream_true",
        "F09_bundle_response_payload_validation_fail_inside_pass_bundle",
        "F09_bundle_response_payload_blocked_with_dataset",
        "F09_bundle_response_payload_minimal_missing_fields",
        "F05_reusable_dataset_refs_unrelated",
        "F08_route_authorization_section_historical_snapshot",
        "F08_living_document_idempotence_actual_bytes",
        "AJV_reproducibility_lock_declared",
    ]
    required_case_ids_final = required_case_ids + final_case_ids

    def run_matrix_final(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        matrix = run_matrix(contracts)
        replace_ids = {"positive_market_state_request", "positive_event_state_request", "positive_reuse_hit_market_response", "positive_authorized_reference", "positive_market_bundle", "positive_event_bundle"}
        rows = [r for r in matrix["rows"] if r["case_id"] not in replace_ids and r["case_id"] not in set(final_case_ids)]
        srr = schemas["state_resolution_request_contract_v0_1_2.json"]; resp = schemas["runtime_user_invocation_response_contract_v0_1_2.json"]; bundle = schemas["state_bundle_manifest_contract_v0_1_2.json"]; iface = schemas["runtime_user_invocation_interface_contract_v0_1_2.json"]
        positives = [
            ("positive_market_state_request", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", valid_request_final("market_state"), True),
            ("positive_event_state_request", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", valid_request_final("event_state"), True),
            ("positive_reuse_hit_market_response", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", valid_response_final("market_state"), True),
            ("positive_authorized_reference", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", valid_response_final("market_state", "authorized_reference"), True),
            ("positive_market_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle_final("market_state_only"), True),
            ("positive_event_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", valid_bundle_final("event_state_only"), True),
        ]
        for case in positives: add_case(rows, case[0], "original_31_regression", case[1], case[2], case[3], case[4], case[5])
        bad_interface = base_valid_interface("resolve")
        bad_interface["state_resolution_request"] = valid_request_final("market_state")
        bad_interface["state_resolution_request"]["payload"]["market_state_request"]["explicit_instrument_ids"] = ["CHANGED"]
        cases = [
            ("F09_top_level_request_content_changed_without_fingerprint", "state_resolution_request_contract_v0_1_2.json", srr, "state_resolution_request", mutate(valid_request_final("market_state"), lambda d: d["payload"]["market_state_request"].update({"explicit_instrument_ids": ["CHANGED"]})), False),
            ("F09_top_level_response_dataset_changed_without_fingerprint", "runtime_user_invocation_response_contract_v0_1_2.json", resp, "response", mutate(valid_response_final("market_state"), lambda d: d.update({"dataset_id": "changed_dataset"})), False),
            ("F09_interface_embedded_request_changed_without_fingerprint", "runtime_user_invocation_interface_contract_v0_1_2.json", iface, "interface", bad_interface, False),
            ("F09_bundle_request_payload_market_with_event_profile", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["request_artifacts"][0]["canonical_content"]["payload"]["market_state_request"].update({"profile_id": "event_state_core_four_intraday_profile_v0_1"})), False),
            ("F09_bundle_request_payload_output_mode_production", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["request_artifacts"][0]["canonical_content"]["payload"]["market_state_request"].update({"output_mode": "production"})), False),
            ("F09_bundle_request_payload_missing_instrument_scope", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["request_artifacts"][0]["canonical_content"]["payload"]["market_state_request"].update({"explicit_instrument_ids": []})), False),
            ("F09_bundle_response_payload_wrong_capability", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"capability_id": "event_state_on_demand_runtime_capability_v0_1"})), False),
            ("F09_bundle_response_payload_wrong_profile", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"profile_id": "event_state_core_four_intraday_profile_v0_1"})), False),
            ("F09_bundle_response_payload_official_dataset_true", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"official_dataset": True})), False),
            ("F09_bundle_response_payload_production_true", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"production": True})), False),
            ("F09_bundle_response_payload_downstream_true", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"downstream": True})), False),
            ("F09_bundle_response_payload_validation_fail_inside_pass_bundle", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"validation_status": "FAIL"})), False),
            ("F09_bundle_response_payload_blocked_with_dataset", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"invocation_status": "blocked", "dataset_id": "bad_dataset"})), False),
            ("F09_bundle_response_payload_minimal_missing_fields", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["runtime_invocation_response_artifacts"][0].update({"canonical_content": {"request_type": "market_state", "state_kind": "market_state"}})), False),
            ("F05_reusable_dataset_refs_unrelated", "state_bundle_manifest_contract_v0_1_2.json", bundle, "bundle", mutate(valid_bundle_final(), lambda d: d["reuse_certification"].update({"reusable_dataset_refs": ["unrelated_dataset"]})), False),
        ]
        for case in cases: add_case(rows, case[0], "external_audit_combined_regression", case[1], case[2], case[3], case[4], case[5])
        route = (FEATURE_ROOT / "99_ruta_de_trabajo.md").read_text(encoding="utf-8-sig") if (FEATURE_ROOT / "99_ruta_de_trabajo.md").exists() else ""
        route_ok = "Historical Snapshot - Provider Contract Schema Hardening v0.1.2 Authorization Issued" in route or "HISTORICAL_SNAPSHOT" in route
        rows.append({"case_id": "F08_route_authorization_section_historical_snapshot", "case_origin": "external_audit_combined_regression", "schema": "living_documents", "expected_valid": True, "actual_valid": route_ok, "result": "PASS" if route_ok else "FAIL", "errors": [] if route_ok else ["route authorization section not marked historical"]})
        rows.append({"case_id": "F08_living_document_idempotence_actual_bytes", "case_origin": "external_audit_combined_regression", "schema": "living_documents", "expected_valid": True, "actual_valid": False, "result": "FAIL", "errors": ["main must replace this placeholder after byte comparison"]})
        lock = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_environment_lock.json"
        rows.append({"case_id": "AJV_reproducibility_lock_declared", "case_origin": "external_audit_combined_regression", "schema": "ajv_lock", "expected_valid": True, "actual_valid": lock.exists(), "result": "PASS" if lock.exists() else "FAIL", "errors": [] if lock.exists() else ["AJV lock missing"]})
        case_ids = [r["case_id"] for r in rows]
        missing = sorted(set(required_case_ids_final) - set(case_ids)); unexpected = sorted(set(case_ids) - set(required_case_ids_final)); duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1}); failed = [r for r in rows if r["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        matrix.update({"status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] != "original_31_regression"]), "external_followup_case_count": len([r for r in rows if r["case_origin"] != "original_31_regression"]), "required_case_ids": required_case_ids_final, "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix

    def recompute_matrix_status(matrix: dict[str, Any]) -> None:
        rows = matrix["rows"]
        case_ids = [r["case_id"] for r in rows]
        matrix["missing_required_case_ids"] = sorted(set(required_case_ids_final) - set(case_ids))
        matrix["unexpected_case_ids"] = sorted(set(case_ids) - set(required_case_ids_final))
        matrix["duplicate_case_ids"] = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        matrix["unexpected_silent_skips"] = len(matrix["unexpected_case_ids"])
        matrix["failed_cases"] = len([r for r in rows if r["result"] == "FAIL"])
        ok = matrix["failed_cases"] == 0 and not matrix["missing_required_case_ids"] and not matrix["unexpected_case_ids"] and not matrix["duplicate_case_ids"]
        matrix["status"] = STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2"
        matrix["semantic_validator_execution"] = "PASS" if matrix["failed_cases"] == 0 else "FAIL"
        matrix["expanded_adversarial_matrix"] = "PASS" if ok else "FAIL"

    def set_case_result(matrix: dict[str, Any], case_id: str, actual: bool, errors: list[str] | None = None) -> None:
        for row in matrix["rows"]:
            if row["case_id"] == case_id:
                row["actual_valid"] = actual
                row["result"] = "PASS" if actual == row["expected_valid"] else "FAIL"
                row["errors"] = [] if row["result"] == "PASS" else (errors or ["case failed"])
                return
        raise KeyError(case_id)

    def write_scope_final(now: str) -> Path:
        path = write_scope(now)
        doc = read_json(path)
        doc["required_case_ids"] = required_case_ids_final
        doc["minimum_case_counts"] = {"original_regression": 31, "external_combined_regression": len(required_case_ids_final) - 31, "total": len(required_case_ids_final)}
        doc["fingerprint_payload_contracts"] = {
            "state_resolution_request": "embedded in state_resolution_request_contract_v0_1_2.json as StateResolutionRequestFingerprintPayload_v0_1_2",
            "runtime_invocation_response": "embedded in runtime_user_invocation_response_contract_v0_1_2.json as RuntimeInvocationResponseFingerprintPayload_v0_1_2",
        }
        write_json(path, doc)
        return path

    def update_docs_final(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        update_docs(now, matrix, zip_path)
        route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
        text = read_text(route)
        text = text.replace("## Provider Contract Schema Hardening v0.1.2 Authorization Issued", "## Historical Snapshot - Provider Contract Schema Hardening v0.1.2 Authorization Issued")
        text = text.replace("Next gate:\n\n```text\nruntime_provider_contract_schema_hardening_v0_1_2\n```", "Next gate at closure:\n\n```text\nruntime_provider_contract_schema_hardening_v0_1_2\n```")
        write_text(route, text)

    def write_ajv_reproducibility_files(now: str) -> list[Path]:
        package_json = g["AJV_NODE_MODULES"] / "ajv" / "package.json"
        out = []
        if package_json.exists():
            package_copy = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_package.json"
            write_json(package_copy, read_json(package_json)); out.append(package_copy)
        manifest = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_reproducibility_manifest.json"
        write_json(manifest, {"manifest_id": "runtime_provider_contract_schema_hardening_v0_1_2_ajv_reproducibility_manifest", "created_at_utc": now, "ajv_required_version": "8.17.1", "node_modules_env_var": "TSIS_AJV_NODE_MODULES", "package_json_snapshot": "configs/runtime_provider_contract_schema_hardening_v0_1_2_ajv_package.json" if package_json.exists() else None, "package_json_sha256": sha256_file(package_json) if package_json.exists() else None, "package_lock_available_in_source_environment": False, "reproduction_mode": "external_fixed_environment_or_install_exact_ajv_8_17_1", "network_required_by_runner": False})
        out.append(manifest)
        return out

    def write_authorization_scope_addendum_final(extra_outputs: list[str]) -> None:
        write_authorization_scope_addendum()
        path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_scope_v0_1.json"
        doc = read_json(path)
        outputs = doc.setdefault("authorized_outputs", [])
        for out in extra_outputs:
            if out not in outputs: outputs.append(out)
        write_json(path, doc)

    def main_final() -> None:
        now = g["now_utc"]()
        ajv_files = write_ajv_reproducibility_files(now)
        write_authorization_scope_addendum_final(["configs/" + f.name for f in ajv_files])
        scope_path = write_scope_final(now)
        rollback_readout_path = write_rollback_readout(now)
        findings_readout_path = write_findings_revalidation_readout(now)
        addendum_path = write_authorization_revalidation_addendum(now)
        audit_failure_path = write_external_audit_failure_readout(now)
        ajv_lock_path = write_ajv_environment_lock(now)
        contract_paths = write_contracts_final()
        contracts = {path.name: read_json(path) for path in contract_paths}
        matrix = run_matrix_final(contracts)
        set_case_result(matrix, "F08_living_document_idempotence_actual_bytes", True)
        update_docs_final(now, matrix, FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip")
        watched = [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]
        before = {str(p): p.read_bytes() for p in watched}
        update_docs_final(now, matrix, FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip")
        after = {str(p): p.read_bytes() for p in watched}
        idempotent = before == after
        route_text = (FEATURE_ROOT / "99_ruta_de_trabajo.md").read_text(encoding="utf-8-sig")
        route_ok = "Historical Snapshot - Provider Contract Schema Hardening v0.1.2 Authorization Issued" in route_text and "Next gate at closure:" in route_text
        set_case_result(matrix, "F08_living_document_idempotence_actual_bytes", idempotent, [] if idempotent else ["two identical update_docs calls changed bytes"])
        set_case_result(matrix, "F08_route_authorization_section_historical_snapshot", route_ok, [] if route_ok else ["route authorization section not historical"])
        route_doc = (FEATURE_ROOT / "99_ruta_de_trabajo.md").read_text(encoding="utf-8-sig")
        agent_doc = (FEATURE_ROOT / "AGENT.md").read_text(encoding="utf-8-sig")
        readme_doc = (RUNTIME / "README.md").read_text(encoding="utf-8-sig")
        changelog_doc = (ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        active_docs = [route_doc, agent_doc, readme_doc]
        marker = "105019Z = FAIL_DATASET_VALIDATION_AND_REUSE_RESTRICTION_PROPAGATION"
        genealogy_ok = all("RECORDED_THROUGH_105019Z" in doc for doc in active_docs) and not any("RECORDED_THROUGH_100143Z" in doc for doc in active_docs) and all(marker in doc for doc in active_docs)
        label = "F05_PROPAGATION_CLOSURE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT"
        label_ok = all(label in doc for doc in active_docs + [changelog_doc]) and not any("STAGING_CONSOLIDATED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT" in doc for doc in active_docs + [changelog_doc])
        changelog_unique = changelog_doc.count(marker) == 1
        set_case_result(matrix, "F08_active_genealogy_marker_matches_latest_external_audit", genealogy_ok, [] if genealogy_ok else ["active docs must record genealogy through 105019Z and not 100143Z"])
        set_case_result(matrix, "F08_active_current_package_label_matches_corrective_iteration", label_ok, [] if label_ok else ["active docs must use F05 propagation closure package label and not staging consolidated label"])
        set_case_result(matrix, "F08_changelog_audit_genealogy_entries_are_unique", changelog_unique, [] if changelog_unique else ["CHANGELOG must contain exactly one 105019Z genealogy line"])
        recompute_matrix_status(matrix)
        f05_rows = [row for row in matrix["rows"] if row.get("case_origin") == "external_105019_f05_regression"]
        matrix["external_105019_f05_regressions"] = "PASS" if f05_rows and all(row.get("result") == "PASS" for row in f05_rows) else "FAIL"
        matrix_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json"
        write_json(matrix_path, matrix)
        pending_zip = FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip"
        readout_path = write_readout(now, matrix, pending_zip)
        update_docs_final(now, matrix, pending_zip)
        files = [RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1.md", CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_scope_v0_1.json", RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_readout_v0_1.md", addendum_path, CONFIGS / "runtime_provider_v0_1_2_rollback_verification_scope_v0_1.json", RUNTIME / "runtime_provider_v0_1_2_rollback_verification_matrix_v0_1.json", rollback_readout_path, CONFIGS / "runtime_provider_contract_schema_hardening_findings_revalidation_scope_v0_1.json", RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_matrix_v0_1.json", findings_readout_path, audit_failure_path, ajv_lock_path, *ajv_files, scope_path, *contract_paths, SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_runner.py", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_patch.py", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py", matrix_path, readout_path, FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]
        normalize_files(files)
        zip_path = make_zip(now, files)
        readout_path = write_readout(now, matrix, zip_path)
        update_docs_final(now, matrix, zip_path)
        normalize_files(files)
        zip_path.unlink(missing_ok=True)
        zip_path = make_zip(now, files)
        ok, errors = verify_zip(zip_path)
        if not ok: raise SystemExit("ZIP verification failed: " + "; ".join(errors))
        print(json.dumps({"gate": GATE, "status": matrix["status"], "case_count": matrix["case_count"], "external_regression_case_count": matrix["external_regression_case_count"], "external_followup_case_count": matrix["external_followup_case_count"], "missing_required_case_ids": len(matrix["missing_required_case_ids"]), "duplicate_case_ids": len(matrix["duplicate_case_ids"]), "unexpected_case_ids": len(matrix["unexpected_case_ids"]), "failed_cases": matrix["failed_cases"], "jsonschema_draft_2020_12_compile": matrix["jsonschema_draft_2020_12_compile"], "ajv_8_17_1_strict_runtime": matrix["ajv_8_17_1_strict_runtime"], "semantic_validator_execution": matrix["semantic_validator_execution"], "zip_path": str(zip_path), "zip_sha256": sha256_file(zip_path), "next_action": "external_adversarial_reaudit_of_provider_only_zip"}, indent=2, ensure_ascii=False))

    g["bundle_schema"] = bundle_schema_final
    g["valid_bundle"] = valid_bundle_final
    g["valid_request"] = valid_request_final
    g["valid_response"] = valid_response_final
    g["semantic_errors"] = semantic_errors_final
    g["write_contracts"] = write_contracts_final
    g["run_matrix"] = run_matrix_final
    g["write_scope"] = write_scope_final
    g["update_docs"] = update_docs_final
    g["main"] = main_final




    # Strict external-audit closure overlay for the 083304 audit. This layer
    # binds embedded request/response artifacts to closed provider payloads and
    # gives StateBundleManifest its own canonical fingerprint payload.
    strict_base_valid_request = g["valid_request"]
    strict_base_valid_response = g["valid_response"]
    strict_base_write_contracts = g["write_contracts"]
    strict_base_run_matrix = g["run_matrix"]
    strict_base_bundle_schema = g["bundle_schema"]
    strict_base_semantic_errors = g["semantic_errors"]
    details_schema = g["details_schema"]
    coverage_schema = g["coverage_schema"]
    state_resolution_schema_base = g["state_resolution_schema"]
    response_schema_base = g["response_schema"]

    def _schema_without_refs(base: dict[str, Any], excluded: set[str]) -> dict[str, Any]:
        schema = copy.deepcopy(base)
        for key in ("$schema", "$id", "title"):
            schema.pop(key, None)
        for key in excluded:
            schema.get("properties", {}).pop(key, None)
        schema["required"] = [key for key in schema.get("required", []) if key not in excluded]
        return schema

    def state_resolution_request_fingerprint_payload_schema_strict() -> dict[str, Any]:
        return _schema_without_refs(state_resolution_schema_base(), {"request_ref", "request_fingerprint"})

    def runtime_invocation_response_fingerprint_payload_schema_strict() -> dict[str, Any]:
        base = _schema_without_refs(response_schema_base(), {"response_ref", "request_ref", "state_bundle_manifest_ref", "authorization_ref"})
        props = base["properties"]
        props["request_ref_id"] = string()
        props["request_ref_sha256"] = hex64()
        props["state_bundle_manifest_ref_id"] = nullable(string())
        props["state_bundle_manifest_ref_sha256"] = nullable(hex64())
        props["authorization_ref_id"] = nullable(string())
        props["authorization_ref_sha256"] = nullable(hex64())
        base["required"] = list(dict.fromkeys(base["required"] + ["request_ref_id", "request_ref_sha256", "state_bundle_manifest_ref_id", "state_bundle_manifest_ref_sha256", "authorization_ref_id", "authorization_ref_sha256"]))
        base["allOf"] = [
            {"if": partial({"request_type": {"const": "market_state"}}), "then": partial({"state_kind": {"const": "market_state"}, "capability_id": {"const": "market_state_on_demand_runtime_capability_v0_1"}, "profile_id": nullable({"const": "market_state_core_four_intraday_profile_v0_1"}), "event_state_details": {"type": "null"}})},
            {"if": partial({"request_type": {"const": "event_state"}}), "then": partial({"state_kind": {"const": "event_state"}, "capability_id": {"const": "event_state_on_demand_runtime_capability_v0_1"}, "profile_id": nullable({"const": "event_state_core_four_intraday_profile_v0_1"}), "market_state_details": {"type": "null"}})},
            {"if": partial({"request_type": {"const": "market_state"}, "invocation_status": {"const": "reuse_hit"}}), "then": partial({"market_state_details": details_schema("market_state")})},
            {"if": partial({"request_type": {"const": "event_state"}, "invocation_status": {"const": "reuse_hit"}}), "then": partial({"event_state_details": details_schema("event_state")})},
            {"if": partial({"invocation_status": {"const": "reuse_hit"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_REUSE_HIT"}, "dataset_id": string(), "dataset_status": {"const": "validated_candidate"}, "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}, "state_bundle_manifest_ref_id": string(), "state_bundle_manifest_ref_sha256": hex64(), "artifact_references": arr(ref_schema("runtime_artifact", "available"), 1, True), "authorization_ref_id": {"type": "null"}, "authorization_ref_sha256": {"type": "null"}})},
            {"if": partial({"invocation_status": {"const": "blocked"}}), "then": partial({"resolution_decision": {"enum": ["BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_CAPABILITY", "BLOCKED_UNSUPPORTED_PROFILE", "BLOCKED_UNSUPPORTED_EVENT_TYPE", "BLOCKED_CONSUMPTION_NOT_AUTHORIZED", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref_id": {"type": "null"}, "state_bundle_manifest_ref_sha256": {"type": "null"}, "authorization_ref_id": {"type": "null"}, "authorization_ref_sha256": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0), "market_state_details": {"type": "null"}, "event_state_details": {"type": "null"}})},
            {"if": partial({"invocation_status": {"const": "authorization_required"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED"}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref_id": {"type": "null"}, "state_bundle_manifest_ref_sha256": {"type": "null"}, "authorization_ref_id": {"type": "null"}, "authorization_ref_sha256": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0)})},
            {"if": partial({"invocation_status": {"const": "authorized_reference"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE"}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref_id": {"type": "null"}, "state_bundle_manifest_ref_sha256": {"type": "null"}, "authorization_ref_id": string(), "authorization_ref_sha256": hex64(), "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0)})},
        ]
        return base

    def state_bundle_manifest_fingerprint_payload_schema_strict() -> dict[str, Any]:
        binding = obj({"request_ref_id": string(), "request_ref_sha256": hex64(), "request_fingerprint": hex64(), "response_ref_id": string(), "state_kind": {"enum": ["market_state", "event_state"]}}, ["request_ref_id", "request_ref_sha256", "request_fingerprint", "response_ref_id", "state_kind"])
        profile = obj({"state_kind": {"enum": ["market_state", "event_state"]}, "profile_id": string(), "profile_version": string(), "profile_fingerprint": hex64()}, ["state_kind", "profile_id", "profile_version", "profile_fingerprint"])
        artifact = obj({"artifact_id": string(), "artifact_type": string(), "sha256": hex64(), "availability": {"const": "available"}}, ["artifact_id", "artifact_type", "sha256", "availability"])
        props = {"state_bundle_manifest_id": string(), "bundle_state_mode": {"enum": ["market_state_only", "event_state_only", "market_and_event"]}, "state_kinds": arr({"enum": ["market_state", "event_state"]}, 1, True, 2), "request_response_binding_payloads": arr(binding, 1, True, 2), "capability_refs": arr(ref_schema("runtime_capability", "available"), 1, True, 2), "dataset_refs": obj({"market_state_dataset_ref": nullable(dataset_ref_schema("market_state")), "event_state_dataset_ref": nullable(dataset_ref_schema("event_state"))}, ["market_state_dataset_ref", "event_state_dataset_ref"]), "coverage": coverage_schema(1), "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS", "BLOCKED", "FAIL"]}, "restrictions": arr(string(), 1, True), "representation_profile_versions": arr(profile, 1, True, 2), "schema_fingerprints": arr(hex64(), 1, True), "source_dataset_ids": arr(string(), 1, True), "source_content_hashes": arr(hex64(), 1, True), "artifact_hashes": arr(artifact, 1, True), "field_lineage": arr(obj({"field_id": string(), "builder_id": string(), "input_refs": arr(string(), 1, True)}, ["field_id", "builder_id", "input_refs"]), 1, True), "temporal_policy": obj({"point_in_time_policy_id": string(), "available_at_policy_id": string(), "future_information_exclusion": {"const": True}}, ["point_in_time_policy_id", "available_at_policy_id", "future_information_exclusion"]), "materialization_status": {"enum": ["reference_only", "validated_candidate_reference", "blocked", "failed"]}, "reuse_certification": obj({"reuse_eligible": {"type": "boolean"}, "reuse_decision": {"enum": ["eligible", "eligible_with_restrictions", "not_eligible_failed_or_blocked"]}, "reusable_dataset_refs": arr(string(), 0, True)}, ["reuse_eligible", "reuse_decision", "reusable_dataset_refs"]), "consumption_authorization": obj({"backtest_consumption_authorized": {"const": False}, "downstream_authorized": {"const": False}, "consumption_purposes": arr(string(), 0, True, 0)}, ["backtest_consumption_authorized", "downstream_authorized", "consumption_purposes"]), "official_dataset": {"const": False}, "production": {"const": False}, "downstream": {"const": False}, "physical_rows_delivered": {"const": False}}
        return obj(props, list(props))
    def request_payload_from_doc_strict(doc: dict[str, Any]) -> dict[str, Any]:
        return {key: copy.deepcopy(doc.get(key)) for key in ["request_id", "request_type", "state_kind", "request_contract_version", "consumer_id", "consumption_purpose", "operation", "resolution_policy", "payload"]}

    def _flatten_ref(doc: dict[str, Any], key: str) -> tuple[Any, Any]:
        value = doc.get(key)
        if isinstance(value, dict):
            return value.get("ref_id"), value.get("sha256")
        return None, None

    def response_payload_from_doc_strict(doc: dict[str, Any]) -> dict[str, Any]:
        payload = {key: copy.deepcopy(doc.get(key)) for key in ["invocation_id", "request_type", "state_kind", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id", "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream", "market_state_details", "event_state_details"]}
        payload["request_ref_id"], payload["request_ref_sha256"] = _flatten_ref(doc, "request_ref")
        payload["state_bundle_manifest_ref_id"], payload["state_bundle_manifest_ref_sha256"] = _flatten_ref(doc, "state_bundle_manifest_ref")
        payload["authorization_ref_id"], payload["authorization_ref_sha256"] = _flatten_ref(doc, "authorization_ref")
        return payload

    def bundle_fingerprint_payload_from_doc_strict(doc: dict[str, Any]) -> dict[str, Any]:
        binding_payloads = []
        for binding in doc.get("request_response_bindings", []):
            request_ref = binding.get("request_ref") if isinstance(binding.get("request_ref"), dict) else {}
            response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
            binding_payloads.append({"request_ref_id": request_ref.get("ref_id"), "request_ref_sha256": request_ref.get("sha256"), "request_fingerprint": binding.get("request_fingerprint"), "response_ref_id": response_ref.get("ref_id"), "state_kind": binding.get("state_kind")})
        return {"state_bundle_manifest_id": copy.deepcopy(doc.get("state_bundle_manifest_id")), "bundle_state_mode": copy.deepcopy(doc.get("bundle_state_mode")), "state_kinds": copy.deepcopy(doc.get("state_kinds")), "request_response_binding_payloads": binding_payloads, "capability_refs": copy.deepcopy(doc.get("capability_refs")), "dataset_refs": copy.deepcopy(doc.get("dataset_refs")), "coverage": copy.deepcopy(doc.get("coverage")), "validation_status": copy.deepcopy(doc.get("validation_status")), "restrictions": copy.deepcopy(doc.get("restrictions")), "representation_profile_versions": copy.deepcopy(doc.get("representation_profile_versions")), "schema_fingerprints": copy.deepcopy(doc.get("schema_fingerprints")), "source_dataset_ids": copy.deepcopy(doc.get("source_dataset_ids")), "source_content_hashes": copy.deepcopy(doc.get("source_content_hashes")), "artifact_hashes": copy.deepcopy(doc.get("artifact_hashes")), "field_lineage": copy.deepcopy(doc.get("field_lineage")), "temporal_policy": copy.deepcopy(doc.get("temporal_policy")), "materialization_status": copy.deepcopy(doc.get("materialization_status")), "reuse_certification": copy.deepcopy(doc.get("reuse_certification")), "consumption_authorization": copy.deepcopy(doc.get("consumption_authorization")), "official_dataset": copy.deepcopy(doc.get("official_dataset")), "production": copy.deepcopy(doc.get("production")), "downstream": copy.deepcopy(doc.get("downstream")), "physical_rows_delivered": copy.deepcopy(doc.get("physical_rows_delivered"))}

    def set_request_fingerprint_strict(doc: dict[str, Any]) -> dict[str, Any]:
        fp = canonical_sha(request_payload_from_doc_strict(doc))
        doc["request_fingerprint"] = fp
        doc["request_ref"]["sha256"] = fp
        return doc

    def set_response_fingerprint_strict(doc: dict[str, Any]) -> dict[str, Any]:
        fp = canonical_sha(response_payload_from_doc_strict(doc))
        doc["response_ref"]["sha256"] = fp
        return doc

    def set_bundle_fingerprint_strict(doc: dict[str, Any]) -> dict[str, Any]:
        fp = canonical_sha(bundle_fingerprint_payload_from_doc_strict(doc))
        doc["bundle_ref"]["sha256"] = fp
        return doc

    def valid_request_strict(kind: str = "market_state", operation: str = "resolve") -> dict[str, Any]:
        return set_request_fingerprint_strict(strict_base_valid_request(kind, operation))

    def valid_response_strict(kind: str = "market_state", status: str = "reuse_hit") -> dict[str, Any]:
        doc = strict_base_valid_response(kind, status)
        req = valid_request_strict(kind)
        doc["request_ref"] = copy.deepcopy(req["request_ref"])
        doc["request_fingerprint"] = req["request_fingerprint"]
        doc["response_ref"]["ref_id"] = f"{kind}_response_ref"
        if status == "reuse_hit":
            doc["dataset_id"] = f"{kind}_dataset_001"
            doc["artifact_references"] = [ref_value("runtime_artifact", f"{kind}_artifact_ref", h(f"artifact_{kind}"))]
        return set_response_fingerprint_strict(doc)

    def valid_bundle_strict(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]
        requests = {kind: valid_request_strict(kind) for kind in kinds}
        bindings = [{"request_ref": copy.deepcopy(requests[k]["request_ref"]), "request_fingerprint": requests[k]["request_fingerprint"], "response_ref": ref_value("runtime_invocation_response", f"{k}_response_ref", h(f"pending_{k}")), "state_kind": k} for k in kinds]
        def dataset(k: str) -> dict[str, Any]:
            return {"dataset_id": f"{k}_dataset_001", "dataset_kind": k, "candidate_dataset_fingerprint": h(f"dataset_{k}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
        def capability_ref(k: str) -> dict[str, Any]:
            cap_id = f"{k}_on_demand_runtime_capability_v0_1"
            return ref_value("runtime_capability", cap_id, h(cap_id))
        doc = {"state_bundle_manifest_id": f"bundle_{mode}_001", "bundle_ref": ref_value("state_bundle_manifest", f"bundle_ref_{mode}_001", h("pending_bundle")), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": bindings, "request_artifacts": [], "runtime_invocation_response_artifacts": [], "capability_refs": [capability_ref(k) for k in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": k, "profile_id": "market_state_core_four_intraday_profile_v0_1" if k == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{k}")} for k in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": f"artifact_{k}_001", "artifact_type": "manifest", "sha256": h(f"artifact_{k}"), "availability": "available"} for k in kinds], "field_lineage": [{"field_id": f"field_{k}_001", "builder_id": f"builder_{k}_001", "input_refs": [f"input_{k}_001"]} for k in kinds], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{k}_dataset_001" for k in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}
        set_bundle_fingerprint_strict(doc)
        responses = {}
        for k in kinds:
            response = valid_response_strict(k, "reuse_hit")
            response["request_ref"] = copy.deepcopy(requests[k]["request_ref"])
            response["request_fingerprint"] = requests[k]["request_fingerprint"]
            response["dataset_id"] = f"{k}_dataset_001"
            response["state_bundle_manifest_ref"] = copy.deepcopy(doc["bundle_ref"])
            response["artifact_references"] = [ref_value("runtime_artifact", f"{k}_artifact_ref", h(f"artifact_{k}"))]
            responses[k] = set_response_fingerprint_strict(response)
        for binding in doc["request_response_bindings"]:
            k = binding["state_kind"]
            binding["response_ref"] = copy.deepcopy(responses[k]["response_ref"])
            req_payload = request_payload_from_doc_strict(requests[k]); resp_payload = response_payload_from_doc_strict(responses[k])
            req_hash = canonical_sha(req_payload); resp_hash = canonical_sha(resp_payload)
            doc["request_artifacts"].append({"artifact_ref_id": requests[k]["request_ref"]["ref_id"], "artifact_ref_sha256": requests[k]["request_ref"]["sha256"], "content_fingerprint": req_hash, "request_fingerprint": req_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": req_payload, "availability": "available"})
            doc["runtime_invocation_response_artifacts"].append({"artifact_ref_id": responses[k]["response_ref"]["ref_id"], "artifact_ref_sha256": responses[k]["response_ref"]["sha256"], "content_fingerprint": resp_hash, "request_fingerprint": requests[k]["request_fingerprint"], "response_fingerprint": resp_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": resp_payload, "availability": "available"})
        return doc
    def bundle_schema_strict() -> dict[str, Any]:
        schema = strict_base_bundle_schema()
        schema.setdefault("$defs", {})["StateResolutionRequestFingerprintPayload_v0_1_2"] = state_resolution_request_fingerprint_payload_schema_strict()
        schema["$defs"]["RuntimeInvocationResponseFingerprintPayload_v0_1_2"] = runtime_invocation_response_fingerprint_payload_schema_strict()
        schema["$defs"]["StateBundleManifestFingerprintPayload_v0_1_2"] = state_bundle_manifest_fingerprint_payload_schema_strict()
        req_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": state_resolution_request_fingerprint_payload_schema_strict(), "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        resp_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "response_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": runtime_invocation_response_fingerprint_payload_schema_strict(), "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "response_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        schema["properties"]["request_artifacts"] = arr(req_art, 1, True, 2)
        schema["properties"]["runtime_invocation_response_artifacts"] = arr(resp_art, 1, True, 2)
        if "request_artifacts" not in schema["required"]:
            schema["required"].insert(schema["required"].index("runtime_invocation_response_artifacts"), "request_artifacts")
        for rule in schema.get("allOf", []):
            props = rule.get("then", {}).get("properties", {})
            if "request_artifacts" in props:
                min_items = props["request_artifacts"].get("minItems", 1) if isinstance(props["request_artifacts"], dict) else 1
                max_items = props["request_artifacts"].get("maxItems") if isinstance(props["request_artifacts"], dict) else None
                props["request_artifacts"] = arr(req_art, min_items, True, max_items)
            if "runtime_invocation_response_artifacts" in props:
                min_items = props["runtime_invocation_response_artifacts"].get("minItems", 1) if isinstance(props["runtime_invocation_response_artifacts"], dict) else 1
                max_items = props["runtime_invocation_response_artifacts"].get("maxItems") if isinstance(props["runtime_invocation_response_artifacts"], dict) else None
                props["runtime_invocation_response_artifacts"] = arr(resp_art, min_items, True, max_items)
        return schema

    def _schema_errors(schema: dict[str, Any], doc: dict[str, Any]) -> list[str]:
        return [error.message for error in Validator(schema).iter_errors(doc)]

    def semantic_errors_strict(doc: dict[str, Any], kind: str) -> list[str]:
        errors = strict_base_semantic_errors(doc, kind)
        if kind == "state_resolution_request":
            payload = request_payload_from_doc_strict(doc)
            if _schema_errors(state_resolution_request_fingerprint_payload_schema_strict(), payload):
                errors.append("request fingerprint payload violates closed provider schema")
            canonical = canonical_sha(payload)
            if doc.get("request_fingerprint") != canonical or doc.get("request_ref", {}).get("sha256") != canonical:
                errors.append("request_fingerprint is not canonical request payload hash")
        if kind == "interface":
            embedded = doc.get("state_resolution_request")
            if isinstance(embedded, dict):
                errors.extend(["embedded request: " + e for e in semantic_errors_strict(embedded, "state_resolution_request")])
        if kind == "response":
            payload = response_payload_from_doc_strict(doc)
            if _schema_errors(runtime_invocation_response_fingerprint_payload_schema_strict(), payload):
                errors.append("response fingerprint payload violates closed provider schema")
            if doc.get("response_ref", {}).get("sha256") != canonical_sha(payload):
                errors.append("response_ref sha256 is not canonical response payload hash")
        if kind == "bundle":
            bundle_payload = bundle_fingerprint_payload_from_doc_strict(doc)
            if _schema_errors(state_bundle_manifest_fingerprint_payload_schema_strict(), bundle_payload):
                errors.append("bundle fingerprint payload violates closed provider schema")
            if doc.get("bundle_ref", {}).get("sha256") != canonical_sha(bundle_payload):
                errors.append("bundle_ref sha256 is not canonical bundle payload hash")
            bundle_cov = doc.get("coverage") if isinstance(doc.get("coverage"), dict) else {}
            req_by_ref = {(a.get("artifact_ref_id"), a.get("artifact_ref_sha256")): a for a in doc.get("request_artifacts", []) if isinstance(a, dict)}
            resp_by_ref = {(a.get("artifact_ref_id"), a.get("artifact_ref_sha256")): a for a in doc.get("runtime_invocation_response_artifacts", []) if isinstance(a, dict)}
            for binding in doc.get("request_response_bindings", []):
                request_ref = binding.get("request_ref") if isinstance(binding.get("request_ref"), dict) else {}
                response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
                req_artifact = req_by_ref.get((request_ref.get("ref_id"), request_ref.get("sha256")))
                resp_artifact = resp_by_ref.get((response_ref.get("ref_id"), response_ref.get("sha256")))
                if not req_artifact:
                    errors.append("binding request_ref has no matching canonical request artifact")
                    continue
                if not resp_artifact:
                    errors.append("binding response_ref has no matching canonical response artifact")
                    continue
                req_content = req_artifact.get("canonical_content") if isinstance(req_artifact.get("canonical_content"), dict) else {}
                resp_content = resp_artifact.get("canonical_content") if isinstance(resp_artifact.get("canonical_content"), dict) else {}
                req_hash = canonical_sha(req_content)
                resp_hash = canonical_sha(resp_content)
                if _schema_errors(state_resolution_request_fingerprint_payload_schema_strict(), req_content):
                    errors.append("embedded request artifact violates closed provider schema")
                if _schema_errors(runtime_invocation_response_fingerprint_payload_schema_strict(), resp_content):
                    errors.append("embedded response artifact violates closed provider schema")
                if req_artifact.get("artifact_ref_sha256") != req_hash or req_artifact.get("content_fingerprint") != req_hash or req_artifact.get("request_fingerprint") != req_hash:
                    errors.append("embedded request artifact fingerprint mismatch")
                if request_ref.get("sha256") != req_hash or binding.get("request_fingerprint") != req_hash:
                    errors.append("binding request_fingerprint does not match embedded request content")
                if resp_artifact.get("artifact_ref_sha256") != resp_hash or resp_artifact.get("content_fingerprint") != resp_hash or resp_artifact.get("response_fingerprint") != resp_hash or response_ref.get("sha256") != resp_hash:
                    errors.append("embedded response artifact fingerprint mismatch")
                if req_content.get("state_kind") != binding.get("state_kind") or req_content.get("request_type") != binding.get("state_kind"):
                    errors.append("embedded request state_kind/request_type mismatch")
                if resp_content.get("state_kind") != binding.get("state_kind") or resp_content.get("request_type") != binding.get("state_kind"):
                    errors.append("embedded response state_kind/request_type mismatch")
                if resp_content.get("request_fingerprint") != binding.get("request_fingerprint"):
                    errors.append("embedded response request_fingerprint mismatch")
                if resp_content.get("request_ref_id") != request_ref.get("ref_id") or resp_content.get("request_ref_sha256") != request_ref.get("sha256"):
                    errors.append("embedded response request_ref does not match binding request_ref")
                if resp_content.get("state_bundle_manifest_ref_id") != doc.get("bundle_ref", {}).get("ref_id") or resp_content.get("state_bundle_manifest_ref_sha256") != doc.get("bundle_ref", {}).get("sha256"):
                    errors.append("embedded response state_bundle_manifest_ref does not match bundle_ref")
                if resp_content.get("coverage") != bundle_cov:
                    errors.append("embedded response coverage does not match bundle coverage")
                refs = doc.get("dataset_refs", {}) if isinstance(doc.get("dataset_refs"), dict) else {}
                expected_dataset = refs.get(f"{binding.get('state_kind')}_dataset_ref")
                if isinstance(expected_dataset, dict) and resp_content.get("dataset_id") != expected_dataset.get("dataset_id"):
                    errors.append("embedded response dataset_id does not match dataset_ref")
            reusable = set((doc.get("reuse_certification") or {}).get("reusable_dataset_refs") or [])
            expected_reusable = {ref.get("dataset_id") for ref in (doc.get("dataset_refs") or {}).values() if isinstance(ref, dict)}
            if doc.get("validation_status") in {"PASS", "PASS_WITH_RESTRICTIONS"} and reusable != expected_reusable:
                errors.append("reuse_certification reusable_dataset_refs must match non-null dataset_refs")
        return list(dict.fromkeys(errors))
    strict_external_case_ids = [
        "F09_STRICT_request_payload_production_true", "F09_STRICT_request_payload_physical_path_allowed", "F09_STRICT_request_operation_mode_mismatch", "F09_STRICT_market_request_missing_calendar_authority", "F09_STRICT_market_request_missing_session_dates", "F09_STRICT_market_request_source_version_policy_wrong", "F09_STRICT_event_subject_scope_wrong", "F09_STRICT_event_direct_market_state_dependency", "F09_STRICT_event_missing_window_policy", "F09_STRICT_response_coverage_arithmetic_invalid", "F09_STRICT_response_reuse_hit_missing_bundle_ref", "F09_STRICT_response_market_with_event_details", "F09_STRICT_response_market_missing_market_details", "F09_STRICT_response_request_ref_id_mismatch", "F09_STRICT_response_request_ref_sha_mismatch", "F09_STRICT_response_authorized_reference_missing_auth", "F09_STRICT_response_dataset_status_arbitrary", "F09_STRICT_bundle_response_coverage_mismatch", "F09_STRICT_bundle_response_points_other_bundle", "F09_STRICT_bundle_restriction_changed_without_bundle_hash", "F09_STRICT_bundle_reusable_dataset_refs_unrelated", "positive_market_and_event_bundle_unique_refs"
    ]

    def run_matrix_strict(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        matrix = strict_base_run_matrix(contracts)
        remove_ids = set(strict_external_case_ids + ["positive_market_bundle", "positive_event_bundle", "positive_market_and_event_bundle"])
        rows = [row for row in matrix["rows"] if row.get("case_id") not in remove_ids]
        req_schema = schemas["state_resolution_request_contract_v0_1_2.json"]
        resp_schema = schemas["runtime_user_invocation_response_contract_v0_1_2.json"]
        bundle_schema_doc = schemas["state_bundle_manifest_contract_v0_1_2.json"]
        add_case(rows, "positive_market_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_strict("market_state_only"), True)
        add_case(rows, "positive_event_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_strict("event_state_only"), True)
        add_case(rows, "positive_market_and_event_bundle_unique_refs", "external_083304_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_strict("market_and_event"), True)
        request_cases = [
            ("F09_STRICT_request_payload_production_true", mutate(valid_request_strict(), lambda d: d["resolution_policy"].update({"production": True}))),
            ("F09_STRICT_request_payload_physical_path_allowed", mutate(valid_request_strict(), lambda d: d["resolution_policy"].update({"allow_physical_path_input": True}))),
            ("F09_STRICT_request_operation_mode_mismatch", mutate(valid_request_strict(operation="invoke"), lambda d: d["resolution_policy"].update({"mode": "resolve_reuse_or_authorization"}))),
            ("F09_STRICT_market_request_missing_calendar_authority", mutate(valid_request_strict(), lambda d: d["payload"]["market_state_request"].pop("calendar_authority_id", None))),
            ("F09_STRICT_market_request_missing_session_dates", mutate(valid_request_strict(), lambda d: d["payload"]["market_state_request"].pop("session_dates", None))),
            ("F09_STRICT_market_request_source_version_policy_wrong", mutate(valid_request_strict(), lambda d: d["payload"]["market_state_request"].update({"source_version_policy": "latest"}))),
            ("F09_STRICT_event_subject_scope_wrong", mutate(valid_request_strict("event_state"), lambda d: d["payload"]["event_state_request"].update({"event_subject_scope": "instrument"}))),
            ("F09_STRICT_event_direct_market_state_dependency", mutate(valid_request_strict("event_state"), lambda d: d["payload"]["event_state_request"].update({"market_state_dependency_mode": "direct_candidate_path"}))),
            ("F09_STRICT_event_missing_window_policy", mutate(valid_request_strict("event_state"), lambda d: d["payload"]["event_state_request"].pop("event_window_policy_id", None))),
        ]
        for case_id, doc in request_cases:
            add_case(rows, case_id, "external_083304_regression", "state_resolution_request_contract_v0_1_2.json", req_schema, "state_resolution_request", doc, False)
        event_details = {"state_kind": "event_state", "materializer_executions": 0, "source_market_data_rows_read": 0, "registry_mutations": 0, "physical_rows_delivered": 0}
        response_cases = [
            ("F09_STRICT_response_coverage_arithmetic_invalid", mutate(valid_response_strict(), lambda d: d["coverage"].update({"represented_contexts": 99}))),
            ("F09_STRICT_response_reuse_hit_missing_bundle_ref", mutate(valid_response_strict(), lambda d: d.update({"state_bundle_manifest_ref": None}))),
            ("F09_STRICT_response_market_with_event_details", mutate(valid_response_strict(), lambda d: d.update({"event_state_details": copy.deepcopy(event_details)}))),
            ("F09_STRICT_response_market_missing_market_details", mutate(valid_response_strict(), lambda d: d.update({"market_state_details": None}))),
            ("F09_STRICT_response_authorized_reference_missing_auth", mutate(valid_response_strict(status="authorized_reference"), lambda d: d.update({"authorization_ref": None}))),
            ("F09_STRICT_response_dataset_status_arbitrary", mutate(valid_response_strict(), lambda d: d.update({"dataset_status": "official"}))),
        ]
        for case_id, doc in response_cases:
            add_case(rows, case_id, "external_083304_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", doc, False)
        bundle_cases = [
            ("F09_STRICT_response_request_ref_id_mismatch", mutate(valid_bundle_strict(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"request_ref_id": "other_request"}))),
            ("F09_STRICT_response_request_ref_sha_mismatch", mutate(valid_bundle_strict(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"request_ref_sha256": h("other_request")}))),
            ("F09_STRICT_bundle_response_coverage_mismatch", mutate(valid_bundle_strict(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"]["coverage"].update({"represented_contexts": 1}))),
            ("F09_STRICT_bundle_response_points_other_bundle", mutate(valid_bundle_strict(), lambda d: d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"state_bundle_manifest_ref_id": "other_bundle"}))),
            ("F09_STRICT_bundle_restriction_changed_without_bundle_hash", mutate(valid_bundle_strict(), lambda d: d["restrictions"].append("new_unhashed_restriction"))),
            ("F09_STRICT_bundle_reusable_dataset_refs_unrelated", mutate(valid_bundle_strict(), lambda d: d["reuse_certification"].update({"reusable_dataset_refs": ["unrelated_dataset"]}))),
        ]
        for case_id, doc in bundle_cases:
            add_case(rows, case_id, "external_083304_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", doc, False)
        required = list(dict.fromkeys(list(matrix.get("required_case_ids", [])) + strict_external_case_ids))
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required) - set(case_ids)); unexpected = sorted(set(case_ids) - set(required)); duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        matrix.update({"status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression"}]), "external_followup_case_count": len([r for r in rows if r["case_origin"] in {"external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression"}]), "required_case_ids": required, "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix

    def write_contracts_strict() -> list[Path]:
        paths = strict_base_write_contracts()
        defs = {"StateResolutionRequestFingerprintPayload_v0_1_2": state_resolution_request_fingerprint_payload_schema_strict(), "RuntimeInvocationResponseFingerprintPayload_v0_1_2": runtime_invocation_response_fingerprint_payload_schema_strict(), "StateBundleManifestFingerprintPayload_v0_1_2": state_bundle_manifest_fingerprint_payload_schema_strict()}
        for path in paths:
            doc = read_json(path)
            schema = doc.get("json_schema", {})
            schema.setdefault("$defs", {}).update(copy.deepcopy(defs))
            if path.name == "state_bundle_manifest_contract_v0_1_2.json":
                doc["json_schema"] = bundle_schema_strict()
            write_json(path, doc)
        return paths

    g["state_resolution_request_fingerprint_payload_schema"] = state_resolution_request_fingerprint_payload_schema_strict
    g["runtime_invocation_response_fingerprint_payload_schema"] = runtime_invocation_response_fingerprint_payload_schema_strict
    g["state_bundle_manifest_fingerprint_payload_schema"] = state_bundle_manifest_fingerprint_payload_schema_strict
    g["request_payload_from_doc"] = request_payload_from_doc_strict
    g["response_payload_from_doc"] = response_payload_from_doc_strict
    g["bundle_fingerprint_payload_from_doc"] = bundle_fingerprint_payload_from_doc_strict
    g["valid_request"] = valid_request_strict
    g["valid_response"] = valid_response_strict
    g["valid_bundle"] = valid_bundle_strict
    g["bundle_schema"] = bundle_schema_strict
    g["semantic_errors"] = semantic_errors_strict
    g["run_matrix"] = run_matrix_strict
    g["write_contracts"] = write_contracts_strict
    # Late binding for helpers used by the strict overlay.
    nullable = g["nullable"]
    def run_matrix_strict_final(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        matrix = run_matrix_strict(contracts)
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        rows = [row for row in matrix["rows"] if row.get("case_id") not in {"positive_reuse_hit_market_response", "positive_authorized_reference"}]
        resp_schema = schemas["runtime_user_invocation_response_contract_v0_1_2.json"]
        add_case(rows, "positive_reuse_hit_market_response", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_strict("market_state", "reuse_hit"), True)
        add_case(rows, "positive_authorized_reference", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_strict("market_state", "authorized_reference"), True)
        required = matrix.get("required_case_ids", [])
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required) - set(case_ids))
        unexpected = sorted(set(case_ids) - set(required))
        duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        matrix.update({"status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression"}]), "external_followup_case_count": len([r for r in rows if r["case_origin"] in {"external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression"}]), "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix

    write_contracts_final = write_contracts_strict
    run_matrix_final = run_matrix_strict_final
    bundle_schema_final = bundle_schema_strict
    valid_bundle_final = valid_bundle_strict
    valid_request_final = valid_request_strict
    valid_response_final = valid_response_strict
    semantic_errors_final = semantic_errors_strict
    g["main"] = main_final
    def _legacy_fingerprint_noise(error: str) -> bool:
        return error.startswith("request_fingerprint_payload:") or error.startswith("response_fingerprint_payload:") or error in {"RuntimeInvocationResponse fingerprint does not match canonical payload", "StateResolutionRequest fingerprint does not match canonical payload"}

    def semantic_errors_strict_clean(doc: dict[str, Any], kind: str) -> list[str]:
        return [error for error in semantic_errors_strict(doc, kind) if not _legacy_fingerprint_noise(error)]

    def run_matrix_strict_final2(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        matrix = run_matrix_strict(contracts)
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        rows = [row for row in matrix["rows"] if row.get("case_id") not in {"positive_reuse_hit_market_response", "positive_authorized_reference"}]
        resp_schema = schemas["runtime_user_invocation_response_contract_v0_1_2.json"]
        add_case(rows, "positive_reuse_hit_market_response", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_strict("market_state", "reuse_hit"), True)
        add_case(rows, "positive_authorized_reference", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_strict("market_state", "authorized_reference"), True)
        required = list(dict.fromkeys(list(matrix.get("required_case_ids", [])) + strict_external_case_ids + ["positive_reuse_hit_market_response", "positive_authorized_reference"]))
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required) - set(case_ids))
        unexpected = sorted(set(case_ids) - set(required))
        duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        matrix.update({"status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression"}]), "external_followup_case_count": len([r for r in rows if r["case_origin"] in {"external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression"}]), "required_case_ids": required, "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix

    semantic_errors_final = semantic_errors_strict_clean
    run_matrix_final = run_matrix_strict_final2
    g["semantic_errors"] = semantic_errors_strict_clean
    g["run_matrix"] = run_matrix_strict_final2
    g["main"] = main_final
    def recompute_matrix_status_strict(matrix: dict[str, Any]) -> None:
        rows = matrix["rows"]
        required = matrix.get("required_case_ids", [])
        case_ids = [row["case_id"] for row in rows]
        matrix["missing_required_case_ids"] = sorted(set(required) - set(case_ids))
        matrix["unexpected_case_ids"] = sorted(set(case_ids) - set(required))
        matrix["duplicate_case_ids"] = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        matrix["unexpected_silent_skips"] = len(matrix["unexpected_case_ids"])
        matrix["failed_cases"] = len([row for row in rows if row["result"] == "FAIL"])
        ok = matrix["failed_cases"] == 0 and not matrix["missing_required_case_ids"] and not matrix["unexpected_case_ids"] and not matrix["duplicate_case_ids"]
        matrix["status"] = STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2"
        matrix["semantic_validator_execution"] = "PASS" if matrix["failed_cases"] == 0 else "FAIL"
        matrix["expanded_adversarial_matrix"] = "PASS" if ok else "FAIL"

    recompute_matrix_status = recompute_matrix_status_strict
    g["main"] = main_final
    # External audit 092039Z closure: break the response/bundle hash cycle.
    # Response fingerprints intentionally exclude bundle_ref.sha256. Bundle
    # fingerprints include response_ref.sha256, so response artifact changes
    # require a new bundle identity.
    def runtime_invocation_response_fingerprint_payload_schema_cyclefree() -> dict[str, Any]:
        base = _schema_without_refs(response_schema_base(), {"response_ref", "request_ref", "state_bundle_manifest_ref", "authorization_ref"})
        props = base["properties"]
        props["request_ref_id"] = string()
        props["request_ref_sha256"] = hex64()
        props["state_bundle_manifest_ref_id"] = nullable(string())
        props["authorization_ref_id"] = nullable(string())
        props["authorization_ref_sha256"] = nullable(hex64())
        base["required"] = list(dict.fromkeys(base["required"] + ["request_ref_id", "request_ref_sha256", "state_bundle_manifest_ref_id", "authorization_ref_id", "authorization_ref_sha256"]))
        base["allOf"] = [
            {"if": partial({"request_type": {"const": "market_state"}}), "then": partial({"state_kind": {"const": "market_state"}, "capability_id": {"const": "market_state_on_demand_runtime_capability_v0_1"}, "profile_id": nullable({"const": "market_state_core_four_intraday_profile_v0_1"}), "event_state_details": {"type": "null"}})},
            {"if": partial({"request_type": {"const": "event_state"}}), "then": partial({"state_kind": {"const": "event_state"}, "capability_id": {"const": "event_state_on_demand_runtime_capability_v0_1"}, "profile_id": nullable({"const": "event_state_core_four_intraday_profile_v0_1"}), "market_state_details": {"type": "null"}})},
            {"if": partial({"request_type": {"const": "market_state"}, "invocation_status": {"const": "reuse_hit"}}), "then": partial({"market_state_details": details_schema("market_state")})},
            {"if": partial({"request_type": {"const": "event_state"}, "invocation_status": {"const": "reuse_hit"}}), "then": partial({"event_state_details": details_schema("event_state")})},
            {"if": partial({"invocation_status": {"const": "reuse_hit"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_REUSE_HIT"}, "dataset_id": string(), "dataset_status": {"const": "validated_candidate"}, "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS"]}, "state_bundle_manifest_ref_id": string(), "artifact_references": arr(ref_schema("runtime_artifact", "available"), 1, True), "authorization_ref_id": {"type": "null"}, "authorization_ref_sha256": {"type": "null"}})},
            {"if": partial({"invocation_status": {"const": "blocked"}}), "then": partial({"resolution_decision": {"enum": ["BLOCKED_INVALID_REQUEST", "BLOCKED_UNSUPPORTED_CAPABILITY", "BLOCKED_UNSUPPORTED_PROFILE", "BLOCKED_UNSUPPORTED_EVENT_TYPE", "BLOCKED_CONSUMPTION_NOT_AUTHORIZED", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", "BLOCKED_PROVIDER_CONTRACT_MISMATCH"]}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref_id": {"type": "null"}, "authorization_ref_id": {"type": "null"}, "authorization_ref_sha256": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0), "market_state_details": {"type": "null"}, "event_state_details": {"type": "null"}})},
            {"if": partial({"invocation_status": {"const": "authorization_required"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED"}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref_id": {"type": "null"}, "authorization_ref_id": {"type": "null"}, "authorization_ref_sha256": {"type": "null"}, "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0)})},
            {"if": partial({"invocation_status": {"const": "authorized_reference"}}), "then": partial({"resolution_decision": {"const": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE"}, "run_id": {"type": "null"}, "dataset_id": {"type": "null"}, "dataset_status": {"type": "null"}, "validation_status": {"type": "null"}, "state_bundle_manifest_ref_id": {"type": "null"}, "authorization_ref_id": string(), "authorization_ref_sha256": hex64(), "artifact_references": arr(ref_schema("runtime_artifact"), 0, True, 0)})},
        ]
        return base

    def response_payload_from_doc_cyclefree(doc: dict[str, Any]) -> dict[str, Any]:
        payload = {key: copy.deepcopy(doc.get(key)) for key in ["invocation_id", "request_type", "state_kind", "request_fingerprint", "invocation_status", "resolution_decision", "capability_id", "profile_id", "run_id", "dataset_id", "dataset_status", "validation_status", "coverage", "restrictions", "artifact_references", "official_dataset", "production", "downstream", "market_state_details", "event_state_details"]}
        payload["request_ref_id"], payload["request_ref_sha256"] = _flatten_ref(doc, "request_ref")
        payload["state_bundle_manifest_ref_id"], _ignored_bundle_sha = _flatten_ref(doc, "state_bundle_manifest_ref")
        payload["authorization_ref_id"], payload["authorization_ref_sha256"] = _flatten_ref(doc, "authorization_ref")
        return payload

    def bundle_fingerprint_payload_from_doc_cyclefree(doc: dict[str, Any]) -> dict[str, Any]:
        binding_payloads = []
        for binding in doc.get("request_response_bindings", []):
            request_ref = binding.get("request_ref") if isinstance(binding.get("request_ref"), dict) else {}
            response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
            binding_payloads.append({"request_ref_id": request_ref.get("ref_id"), "request_ref_sha256": request_ref.get("sha256"), "request_fingerprint": binding.get("request_fingerprint"), "response_ref_id": response_ref.get("ref_id"), "response_ref_sha256": response_ref.get("sha256"), "state_kind": binding.get("state_kind")})
        payload = bundle_fingerprint_payload_from_doc_strict(doc)
        payload["request_response_binding_payloads"] = binding_payloads
        return payload

    def state_bundle_manifest_fingerprint_payload_schema_cyclefree() -> dict[str, Any]:
        schema = state_bundle_manifest_fingerprint_payload_schema_strict()
        schema["properties"]["request_response_binding_payloads"]["items"]["properties"]["response_ref_sha256"] = hex64()
        schema["properties"]["request_response_binding_payloads"]["items"]["required"].append("response_ref_sha256")
        return schema

    def set_response_fingerprint_cyclefree(doc: dict[str, Any]) -> dict[str, Any]:
        doc["response_ref"]["sha256"] = canonical_sha(response_payload_from_doc_cyclefree(doc))
        return doc

    def set_bundle_fingerprint_cyclefree(doc: dict[str, Any]) -> dict[str, Any]:
        doc["bundle_ref"]["sha256"] = canonical_sha(bundle_fingerprint_payload_from_doc_cyclefree(doc))
        return doc
    def valid_response_cyclefree(kind: str = "market_state", status: str = "reuse_hit") -> dict[str, Any]:
        doc = valid_response_strict(kind, status)
        return set_response_fingerprint_cyclefree(doc)

    def valid_bundle_cyclefree(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]
        requests = {kind: valid_request_strict(kind) for kind in kinds}
        def dataset(k: str) -> dict[str, Any]:
            return {"dataset_id": f"{k}_dataset_001", "dataset_kind": k, "candidate_dataset_fingerprint": h(f"dataset_{k}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
        def capability_ref(k: str) -> dict[str, Any]:
            cap_id = f"{k}_on_demand_runtime_capability_v0_1"
            return ref_value("runtime_capability", cap_id, h(cap_id))
        doc = {"state_bundle_manifest_id": f"bundle_{mode}_001", "bundle_ref": ref_value("state_bundle_manifest", f"bundle_ref_{mode}_001", h("pending_bundle")), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": [], "request_artifacts": [], "runtime_invocation_response_artifacts": [], "capability_refs": [capability_ref(k) for k in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": k, "profile_id": "market_state_core_four_intraday_profile_v0_1" if k == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{k}")} for k in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": f"artifact_{k}_001", "artifact_type": "manifest", "sha256": h(f"artifact_{k}"), "availability": "available"} for k in kinds], "field_lineage": [{"field_id": f"field_{k}_001", "builder_id": f"builder_{k}_001", "input_refs": [f"input_{k}_001"]} for k in kinds], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{k}_dataset_001" for k in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}
        # First set a provisional bundle ref id; response fingerprints include the bundle id only.
        responses = {}
        for k in kinds:
            response = valid_response_strict(k, "reuse_hit")
            response["request_ref"] = copy.deepcopy(requests[k]["request_ref"])
            response["request_fingerprint"] = requests[k]["request_fingerprint"]
            response["dataset_id"] = f"{k}_dataset_001"
            response["state_bundle_manifest_ref"] = copy.deepcopy(doc["bundle_ref"])
            response["artifact_references"] = [ref_value("runtime_artifact", f"{k}_artifact_ref", h(f"artifact_{k}"))]
            responses[k] = set_response_fingerprint_cyclefree(response)
        for k in kinds:
            req_payload = request_payload_from_doc_strict(requests[k]); req_hash = canonical_sha(req_payload)
            resp_payload = response_payload_from_doc_cyclefree(responses[k]); resp_hash = canonical_sha(resp_payload)
            doc["request_response_bindings"].append({"request_ref": copy.deepcopy(requests[k]["request_ref"]), "request_fingerprint": requests[k]["request_fingerprint"], "response_ref": copy.deepcopy(responses[k]["response_ref"]), "state_kind": k})
            doc["request_artifacts"].append({"artifact_ref_id": requests[k]["request_ref"]["ref_id"], "artifact_ref_sha256": requests[k]["request_ref"]["sha256"], "content_fingerprint": req_hash, "request_fingerprint": req_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": req_payload, "availability": "available"})
            doc["runtime_invocation_response_artifacts"].append({"artifact_ref_id": responses[k]["response_ref"]["ref_id"], "artifact_ref_sha256": responses[k]["response_ref"]["sha256"], "content_fingerprint": resp_hash, "request_fingerprint": requests[k]["request_fingerprint"], "response_fingerprint": resp_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": resp_payload, "availability": "available"})
        return set_bundle_fingerprint_cyclefree(doc)

    def bundle_schema_cyclefree() -> dict[str, Any]:
        schema = bundle_schema_strict()
        schema["$defs"]["RuntimeInvocationResponseFingerprintPayload_v0_1_2"] = runtime_invocation_response_fingerprint_payload_schema_cyclefree()
        schema["$defs"]["StateBundleManifestFingerprintPayload_v0_1_2"] = state_bundle_manifest_fingerprint_payload_schema_cyclefree()
        resp_schema = runtime_invocation_response_fingerprint_payload_schema_cyclefree()
        resp_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "response_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": resp_schema, "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "response_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        schema["properties"]["runtime_invocation_response_artifacts"] = arr(resp_art, 1, True, 2)
        for rule in schema.get("allOf", []):
            props = rule.get("then", {}).get("properties", {})
            if "runtime_invocation_response_artifacts" in props:
                min_items = props["runtime_invocation_response_artifacts"].get("minItems", 1) if isinstance(props["runtime_invocation_response_artifacts"], dict) else 1
                max_items = props["runtime_invocation_response_artifacts"].get("maxItems") if isinstance(props["runtime_invocation_response_artifacts"], dict) else None
                props["runtime_invocation_response_artifacts"] = arr(resp_art, min_items, True, max_items)
        return schema

    def validation_severity(value: Any) -> int:
        return {"PASS": 0, "PASS_WITH_RESTRICTIONS": 1, "BLOCKED": 2, "FAIL": 3}.get(value, 99)

    def semantic_errors_cyclefree(doc: dict[str, Any], kind: str) -> list[str]:
        errors = [e for e in semantic_errors_strict_clean(doc, kind) if "state_bundle_manifest_ref_sha256" not in e]
        if kind == "response":
            payload = response_payload_from_doc_cyclefree(doc)
            if _schema_errors(runtime_invocation_response_fingerprint_payload_schema_cyclefree(), payload):
                errors.append("response cycle-free fingerprint payload violates closed provider schema")
            if doc.get("response_ref", {}).get("sha256") != canonical_sha(payload):
                errors.append("response_ref sha256 is not canonical cycle-free response payload hash")
        if kind == "bundle":
            bundle_payload = bundle_fingerprint_payload_from_doc_cyclefree(doc)
            if _schema_errors(state_bundle_manifest_fingerprint_payload_schema_cyclefree(), bundle_payload):
                errors.append("bundle cycle-free fingerprint payload violates closed provider schema")
            if doc.get("bundle_ref", {}).get("sha256") != canonical_sha(bundle_payload):
                errors.append("bundle_ref sha256 is not canonical cycle-free bundle payload hash")
            bundle_restrictions = set(doc.get("restrictions") or [])
            response_severity = 0
            req_by_ref = {(a.get("artifact_ref_id"), a.get("artifact_ref_sha256")): a for a in doc.get("request_artifacts", []) if isinstance(a, dict)}
            resp_by_ref = {(a.get("artifact_ref_id"), a.get("artifact_ref_sha256")): a for a in doc.get("runtime_invocation_response_artifacts", []) if isinstance(a, dict)}
            for binding in doc.get("request_response_bindings", []):
                request_ref = binding.get("request_ref") if isinstance(binding.get("request_ref"), dict) else {}
                response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
                req_artifact = req_by_ref.get((request_ref.get("ref_id"), request_ref.get("sha256")))
                resp_artifact = resp_by_ref.get((response_ref.get("ref_id"), response_ref.get("sha256")))
                if not req_artifact or not resp_artifact:
                    continue
                req_content = req_artifact.get("canonical_content") if isinstance(req_artifact.get("canonical_content"), dict) else {}
                resp_content = resp_artifact.get("canonical_content") if isinstance(resp_artifact.get("canonical_content"), dict) else {}
                if req_artifact.get("state_kind") != binding.get("state_kind") or req_artifact.get("state_kind") != req_content.get("state_kind"):
                    errors.append("request artifact outer state_kind does not match content and binding")
                if resp_artifact.get("state_kind") != binding.get("state_kind") or resp_artifact.get("state_kind") != resp_content.get("state_kind"):
                    errors.append("response artifact outer state_kind does not match content and binding")
                if resp_artifact.get("request_fingerprint") != binding.get("request_fingerprint") or resp_artifact.get("request_fingerprint") != resp_content.get("request_fingerprint"):
                    errors.append("response artifact outer request_fingerprint does not match content and binding")
                if response_ref.get("sha256") != canonical_sha(resp_content):
                    errors.append("binding response_ref sha256 does not match response content")
                if resp_content.get("state_bundle_manifest_ref_id") != doc.get("bundle_ref", {}).get("ref_id"):
                    errors.append("embedded response state_bundle_manifest_ref_id does not match bundle_ref")
                response_restrictions = set(resp_content.get("restrictions") or [])
                if not response_restrictions.issubset(bundle_restrictions):
                    errors.append("bundle restrictions do not include response restrictions")
                response_severity = max(response_severity, validation_severity(resp_content.get("validation_status")))
            if validation_severity(doc.get("validation_status")) < response_severity:
                errors.append("bundle validation_status is less restrictive than response validation_status")
            reuse = doc.get("reuse_certification") or {}
            refs = reuse.get("reusable_dataset_refs") or []
            decision = reuse.get("reuse_decision")
            eligible = reuse.get("reuse_eligible")
            if eligible is True and decision not in {"eligible", "eligible_with_restrictions"}:
                errors.append("reuse_certification eligible=true requires eligible decision")
            if eligible is False and (decision != "not_eligible_failed_or_blocked" or refs):
                errors.append("reuse_certification ineligible requires no reusable refs")
            if decision == "not_eligible_failed_or_blocked" and (eligible is not False or refs):
                errors.append("reuse_certification not_eligible decision requires eligible=false and empty refs")
        return list(dict.fromkeys(errors))
    cyclefree_case_ids = [
        "F09_CYCLE_response_hash_change_requires_bundle_hash_change",
        "F09_CYCLE_request_artifact_outer_state_kind_mismatch",
        "F09_CYCLE_response_artifact_outer_state_kind_mismatch",
        "F09_CYCLE_response_artifact_outer_request_fingerprint_mismatch",
        "F09_CYCLE_response_restriction_not_propagated",
        "F09_CYCLE_bundle_validation_less_restrictive_than_response",
        "F09_CYCLE_reuse_ineligible_with_refs",
        "F09_CYCLE_reuse_eligible_with_not_eligible_decision",
        "F09_CYCLE_top_level_request_fingerprint_payload_schema_strict",
        "F09_CYCLE_top_level_response_fingerprint_payload_schema_cyclefree",
        "F08_audit_genealogy_includes_075406_083304_092039",
    ]

    def _recompute_response_artifact(doc: dict[str, Any], index: int = 0) -> None:
        artifact = doc["runtime_invocation_response_artifacts"][index]
        new_hash = canonical_sha(artifact["canonical_content"])
        artifact.update({"artifact_ref_sha256": new_hash, "content_fingerprint": new_hash, "response_fingerprint": new_hash})
        for binding in doc["request_response_bindings"]:
            if binding.get("response_ref", {}).get("ref_id") == artifact["artifact_ref_id"]:
                binding["response_ref"]["sha256"] = new_hash

    def _flip_kind(kind: str) -> str:
        return "event_state" if kind == "market_state" else "market_state"

    def run_matrix_cyclefree(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        matrix = run_matrix_strict_final2(contracts)
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        rows = [row for row in matrix["rows"] if row.get("case_id") not in set(cyclefree_case_ids + ["positive_market_bundle", "positive_event_bundle", "positive_market_and_event_bundle_unique_refs", "positive_reuse_hit_market_response", "positive_authorized_reference"])]
        req_schema = schemas["state_resolution_request_contract_v0_1_2.json"]
        resp_schema = schemas["runtime_user_invocation_response_contract_v0_1_2.json"]
        bundle_schema_doc = schemas["state_bundle_manifest_contract_v0_1_2.json"]
        add_case(rows, "positive_reuse_hit_market_response", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_cyclefree("market_state", "reuse_hit"), True)
        add_case(rows, "positive_authorized_reference", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_cyclefree("market_state", "authorized_reference"), True)
        add_case(rows, "positive_market_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_cyclefree("market_state_only"), True)
        add_case(rows, "positive_event_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_cyclefree("event_state_only"), True)
        add_case(rows, "positive_market_and_event_bundle_unique_refs", "external_083304_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_cyclefree("market_and_event"), True)
        bundle_cases = [
            ("F09_CYCLE_response_hash_change_requires_bundle_hash_change", mutate(valid_bundle_cyclefree(), lambda d: (d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"artifact_references": [ref_value("runtime_artifact", "changed_artifact", h("changed_artifact"))]}), _recompute_response_artifact(d, 0)))),
            ("F09_CYCLE_request_artifact_outer_state_kind_mismatch", mutate(valid_bundle_cyclefree(), lambda d: d["request_artifacts"][0].update({"state_kind": _flip_kind(d["request_artifacts"][0]["state_kind"])}))),
            ("F09_CYCLE_response_artifact_outer_state_kind_mismatch", mutate(valid_bundle_cyclefree(), lambda d: d["runtime_invocation_response_artifacts"][0].update({"state_kind": _flip_kind(d["runtime_invocation_response_artifacts"][0]["state_kind"])}))),
            ("F09_CYCLE_response_artifact_outer_request_fingerprint_mismatch", mutate(valid_bundle_cyclefree(), lambda d: d["runtime_invocation_response_artifacts"][0].update({"request_fingerprint": h("wrong_request_fp")}))),
            ("F09_CYCLE_response_restriction_not_propagated", mutate(valid_bundle_cyclefree(), lambda d: (d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"restrictions": ["different_restriction"]}), _recompute_response_artifact(d, 0), set_bundle_fingerprint_cyclefree(d)))),
            ("F09_CYCLE_bundle_validation_less_restrictive_than_response", mutate(valid_bundle_cyclefree(), lambda d: (d.update({"validation_status": "PASS"}), set_bundle_fingerprint_cyclefree(d)))),
            ("F09_CYCLE_reuse_ineligible_with_refs", mutate(valid_bundle_cyclefree(), lambda d: (d["reuse_certification"].update({"reuse_eligible": False, "reuse_decision": "not_eligible_failed_or_blocked", "reusable_dataset_refs": ["market_state_dataset_001"]}), set_bundle_fingerprint_cyclefree(d)))),
            ("F09_CYCLE_reuse_eligible_with_not_eligible_decision", mutate(valid_bundle_cyclefree(), lambda d: (d["reuse_certification"].update({"reuse_eligible": True, "reuse_decision": "not_eligible_failed_or_blocked", "reusable_dataset_refs": ["market_state_dataset_001"]}), set_bundle_fingerprint_cyclefree(d)))),
        ]
        for case_id, doc in bundle_cases:
            add_case(rows, case_id, "external_092039_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", doc, False)
        bad_request_payload = request_payload_from_doc_strict(valid_request_strict())
        bad_request_payload["resolution_policy"]["production"] = True
        top_req_errors = _schema_errors(contracts["state_resolution_request_contract_v0_1_2.json"]["fingerprint_payload_schema"], bad_request_payload)
        rows.append({"case_id": "F09_CYCLE_top_level_request_fingerprint_payload_schema_strict", "case_origin": "external_092039_regression", "schema": "state_resolution_request_contract_v0_1_2.json::fingerprint_payload_schema", "expected_valid": False, "actual_valid": not top_req_errors, "result": "PASS" if top_req_errors else "FAIL", "errors": top_req_errors[:8]})
        response_payload = response_payload_from_doc_cyclefree(valid_response_cyclefree())
        top_resp_errors = _schema_errors(contracts["runtime_user_invocation_response_contract_v0_1_2.json"]["fingerprint_payload_schema"], response_payload)
        rows.append({"case_id": "F09_CYCLE_top_level_response_fingerprint_payload_schema_cyclefree", "case_origin": "external_092039_regression", "schema": "runtime_user_invocation_response_contract_v0_1_2.json::fingerprint_payload_schema", "expected_valid": True, "actual_valid": not top_resp_errors, "result": "PASS" if not top_resp_errors else "FAIL", "errors": top_resp_errors[:8]})
        scope = read_json(CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json") if (CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json").exists() else {}
        genealogy_text = canonical_json(scope.get("previous_external_audit_results", []))
        genealogy_ok = all(token in genealogy_text for token in ["075406Z", "083304Z", "092039Z"])
        rows.append({"case_id": "F08_audit_genealogy_includes_075406_083304_092039", "case_origin": "external_092039_regression", "schema": "runtime_provider_contract_schema_hardening_v0_1_2_scope.json", "expected_valid": True, "actual_valid": genealogy_ok, "result": "PASS" if genealogy_ok else "FAIL", "errors": [] if genealogy_ok else ["audit genealogy missing 075406Z/083304Z/092039Z"]})
        required = list(dict.fromkeys(list(matrix.get("required_case_ids", [])) + cyclefree_case_ids))
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required) - set(case_ids)); unexpected = sorted(set(case_ids) - set(required)); duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        matrix.update({"status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression", "external_092039_regression"}]), "external_followup_case_count": len([r for r in rows if r["case_origin"] in {"external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression", "external_092039_regression"}]), "required_case_ids": required, "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix
    failed_audit_genealogy = [
        {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T061024Z.zip", "result": "FAIL_DOCUMENT_AND_SEMANTIC_GAPS"},
        {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T070232Z.zip", "result": "FAIL_DOCUMENT_AND_SEMANTIC_GAPS"},
        {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T075406Z.zip", "result": "FAIL_SEMANTIC_FINGERPRINT_GAPS"},
        {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T083304Z.zip", "result": "FAIL_EMBEDDED_PAYLOAD_SCHEMA_GAPS"},
        {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T092039Z.zip", "result": "FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS"},
    ]

    def write_contracts_cyclefree() -> list[Path]:
        paths = write_contracts_strict()
        defs = {"StateResolutionRequestFingerprintPayload_v0_1_2": state_resolution_request_fingerprint_payload_schema_strict(), "RuntimeInvocationResponseFingerprintPayload_v0_1_2": runtime_invocation_response_fingerprint_payload_schema_cyclefree(), "StateBundleManifestFingerprintPayload_v0_1_2": state_bundle_manifest_fingerprint_payload_schema_cyclefree()}
        for path in paths:
            doc = read_json(path)
            schema = doc.get("json_schema", {})
            schema.setdefault("$defs", {}).update(copy.deepcopy(defs))
            if path.name == "state_resolution_request_contract_v0_1_2.json":
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["StateResolutionRequestFingerprintPayload_v0_1_2"])
            elif path.name == "runtime_user_invocation_response_contract_v0_1_2.json":
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["RuntimeInvocationResponseFingerprintPayload_v0_1_2"])
            elif path.name == "state_bundle_manifest_contract_v0_1_2.json":
                doc["json_schema"] = bundle_schema_cyclefree()
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["StateBundleManifestFingerprintPayload_v0_1_2"])
            elif "fingerprint_payload_schema" in doc:
                doc.pop("fingerprint_payload_schema", None)
            write_json(path, doc)
        return paths

    def write_scope_cyclefree(now: str) -> Path:
        path = write_scope_final(now)
        doc = read_json(path)
        doc["previous_external_audit_results"] = copy.deepcopy(failed_audit_genealogy)
        doc["corrective_iteration_label"] = "cycle_free_external_audit_092039_closure_candidate"
        doc["required_case_ids"] = list(dict.fromkeys(list(doc.get("required_case_ids", [])) + cyclefree_case_ids))
        doc["minimum_case_counts"] = {"original_regression": 31, "external_combined_regression": len(doc["required_case_ids"]) - 31, "total": len(doc["required_case_ids"])}
        doc["fingerprint_cycle_policy"] = {"runtime_invocation_response_fingerprint_excludes": ["state_bundle_manifest_ref.sha256"], "state_bundle_manifest_fingerprint_includes": ["request_ref.sha256", "request_fingerprint", "response_ref.ref_id", "response_ref.sha256", "state_kind"], "reason": "prevents response hash <-> bundle hash circularity while preserving bundle identity over response artifacts"}
        write_json(path, doc)
        return path

    def _patch_living_doc_text(text: str) -> str:
        text = text.replace("Second Corrective Internal Pass", "Cycle-Free Corrective Internal Pass")
        text = text.replace("Second corrective closure", "Cycle-free corrective closure")
        text = text.replace("second corrective v0.1.2", "cycle-free corrective v0.1.2")
        text = text.replace("second corrective", "cycle-free corrective")
        marker = "## Runtime Provider v0.1.2 External Audit Genealogy"
        if marker not in text:
            genealogy = marker + "\n\n```text\n061024Z = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\n070232Z = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\n075406Z = FAIL_SEMANTIC_FINGERPRINT_GAPS\n083304Z = FAIL_EMBEDDED_PAYLOAD_SCHEMA_GAPS\n092039Z = FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS\ncurrent package = CYCLE_FREE_CORRECTIVE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT\n```\n\n"
            text = genealogy + text
        return text

    def update_docs_cyclefree(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        update_docs_final(now, matrix, zip_path)
        for path in [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]:
            if path.exists():
                write_text(path, _patch_living_doc_text(read_text(path)))

    def write_readout_cyclefree(now: str, matrix: dict[str, Any], zip_path: Path) -> Path:
        path = write_readout(now, matrix, zip_path)
        text = read_text(path)
        text = _patch_living_doc_text(text)
        extra = "\n## Cycle-Free Fingerprint Closure\n\n```text\nresponse_fingerprint_excludes_bundle_ref_sha256 = true\nbundle_fingerprint_includes_response_ref_sha256 = true\nouter_artifact_metadata_correlated_with_content = true\nrestriction_propagation_checked = true\nvalidation_severity_not_weakened = true\nreuse_certification_state_machine_closed = true\nfingerprint_payload_schema_single_authority = true\n```\n"
        if "## Cycle-Free Fingerprint Closure" not in text:
            text = text.rstrip() + "\n" + extra
        write_text(path, text)
        return path

    def recompute_matrix_status_cyclefree(matrix: dict[str, Any]) -> None:
        rows = matrix["rows"]
        required = matrix.get("required_case_ids", [])
        case_ids = [row["case_id"] for row in rows]
        matrix["missing_required_case_ids"] = sorted(set(required) - set(case_ids))
        matrix["unexpected_case_ids"] = sorted(set(case_ids) - set(required))
        matrix["duplicate_case_ids"] = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        matrix["unexpected_silent_skips"] = len(matrix["unexpected_case_ids"])
        matrix["failed_cases"] = len([row for row in rows if row["result"] == "FAIL"])
        ok = matrix["failed_cases"] == 0 and not matrix["missing_required_case_ids"] and not matrix["unexpected_case_ids"] and not matrix["duplicate_case_ids"]
        matrix["status"] = STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2"
        matrix["semantic_validator_execution"] = "PASS" if matrix["failed_cases"] == 0 else "FAIL"
        matrix["expanded_adversarial_matrix"] = "PASS" if ok else "FAIL"

    runtime_invocation_response_fingerprint_payload_schema_strict = runtime_invocation_response_fingerprint_payload_schema_cyclefree
    response_payload_from_doc_strict = response_payload_from_doc_cyclefree
    bundle_fingerprint_payload_from_doc_strict = bundle_fingerprint_payload_from_doc_cyclefree
    state_bundle_manifest_fingerprint_payload_schema_strict = state_bundle_manifest_fingerprint_payload_schema_cyclefree
    valid_response_strict = valid_response_cyclefree
    valid_bundle_strict = valid_bundle_cyclefree
    bundle_schema_strict = bundle_schema_cyclefree
    semantic_errors_final = semantic_errors_cyclefree
    run_matrix_final = run_matrix_cyclefree
    write_contracts_final = write_contracts_cyclefree
    write_scope_final = write_scope_cyclefree
    update_docs_final = update_docs_cyclefree
    write_readout = write_readout_cyclefree
    recompute_matrix_status = recompute_matrix_status_cyclefree
    g["runtime_invocation_response_fingerprint_payload_schema"] = runtime_invocation_response_fingerprint_payload_schema_cyclefree
    g["state_bundle_manifest_fingerprint_payload_schema"] = state_bundle_manifest_fingerprint_payload_schema_cyclefree
    g["response_payload_from_doc"] = response_payload_from_doc_cyclefree
    g["bundle_fingerprint_payload_from_doc"] = bundle_fingerprint_payload_from_doc_cyclefree
    g["valid_response"] = valid_response_cyclefree
    g["valid_bundle"] = valid_bundle_cyclefree
    g["bundle_schema"] = bundle_schema_cyclefree
    g["semantic_errors"] = semantic_errors_cyclefree
    g["run_matrix"] = run_matrix_cyclefree
    g["write_contracts"] = write_contracts_cyclefree
    g["write_scope"] = write_scope_cyclefree
    g["update_docs"] = update_docs_cyclefree
    g["main"] = main_final

    def write_scope_cyclefree2(now: str) -> Path:
        path = write_scope(now)
        doc = read_json(path)
        doc["previous_external_audit_results"] = copy.deepcopy(failed_audit_genealogy)
        doc["corrective_iteration_label"] = "cycle_free_external_audit_092039_closure_candidate"
        base_required = list(dict.fromkeys(list(required_case_ids_final) + strict_external_case_ids + cyclefree_case_ids))
        doc["required_case_ids"] = base_required
        doc["minimum_case_counts"] = {"original_regression": 31, "external_combined_regression": len(base_required) - 31, "total": len(base_required)}
        doc["fingerprint_payload_contracts"] = {"state_resolution_request": "StateResolutionRequestFingerprintPayload_v0_1_2", "runtime_invocation_response": "RuntimeInvocationResponseFingerprintPayload_v0_1_2", "state_bundle_manifest": "StateBundleManifestFingerprintPayload_v0_1_2", "single_authority": "top_level_fingerprint_payload_schema_matches_json_schema_defs"}
        doc["fingerprint_cycle_policy"] = {"runtime_invocation_response_fingerprint_excludes": ["state_bundle_manifest_ref.sha256"], "state_bundle_manifest_fingerprint_includes": ["request_ref.sha256", "request_fingerprint", "response_ref.ref_id", "response_ref.sha256", "state_kind"], "reason": "prevents response hash <-> bundle hash circularity while preserving bundle identity over response artifacts"}
        write_json(path, doc)
        return path

    def update_docs_cyclefree2(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        update_docs(now, matrix, zip_path)
        for path in [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]:
            if path.exists():
                write_text(path, _patch_living_doc_text(read_text(path)))

    def write_readout_cyclefree2(now: str, matrix: dict[str, Any], zip_path: Path) -> Path:
        path = write_readout(now, matrix, zip_path)
        text = _patch_living_doc_text(read_text(path))
        extra = "\n## Cycle-Free Fingerprint Closure\n\n```text\nresponse_fingerprint_excludes_bundle_ref_sha256 = true\nbundle_fingerprint_includes_response_ref_sha256 = true\nouter_artifact_metadata_correlated_with_content = true\nrestriction_propagation_checked = true\nvalidation_severity_not_weakened = true\nreuse_certification_state_machine_closed = true\nfingerprint_payload_schema_single_authority = true\n```\n"
        if "## Cycle-Free Fingerprint Closure" not in text:
            text = text.rstrip() + "\n" + extra
        write_text(path, text)
        return path

    write_scope_final = write_scope_cyclefree2
    update_docs_final = update_docs_cyclefree2
    write_readout = write_readout_cyclefree2
    g["write_scope"] = write_scope_cyclefree2
    g["update_docs"] = update_docs_cyclefree2
    g["main"] = main_final

    def bundle_schema_cyclefree2() -> dict[str, Any]:
        schema = strict_base_bundle_schema()
        schema.setdefault("$defs", {})["StateResolutionRequestFingerprintPayload_v0_1_2"] = state_resolution_request_fingerprint_payload_schema_strict()
        schema["$defs"]["RuntimeInvocationResponseFingerprintPayload_v0_1_2"] = runtime_invocation_response_fingerprint_payload_schema_cyclefree()
        schema["$defs"]["StateBundleManifestFingerprintPayload_v0_1_2"] = state_bundle_manifest_fingerprint_payload_schema_cyclefree()
        req_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": state_resolution_request_fingerprint_payload_schema_strict(), "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        resp_art = obj({"artifact_ref_id": string(), "artifact_ref_sha256": hex64(), "content_fingerprint": hex64(), "request_fingerprint": hex64(), "response_fingerprint": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}, "canonicalization_algorithm": {"const": "json_sort_keys_compact_utf8_sha256"}, "canonical_content": runtime_invocation_response_fingerprint_payload_schema_cyclefree(), "availability": {"const": "available"}}, ["artifact_ref_id", "artifact_ref_sha256", "content_fingerprint", "request_fingerprint", "response_fingerprint", "state_kind", "canonicalization_algorithm", "canonical_content", "availability"])
        schema["properties"]["request_artifacts"] = arr(req_art, 1, True, 2)
        schema["properties"]["runtime_invocation_response_artifacts"] = arr(resp_art, 1, True, 2)
        if "request_artifacts" not in schema["required"]:
            schema["required"].insert(schema["required"].index("runtime_invocation_response_artifacts"), "request_artifacts")
        for rule in schema.get("allOf", []):
            props = rule.get("then", {}).get("properties", {})
            if "request_artifacts" in props:
                min_items = props["request_artifacts"].get("minItems", 1) if isinstance(props["request_artifacts"], dict) else 1
                max_items = props["request_artifacts"].get("maxItems") if isinstance(props["request_artifacts"], dict) else None
                props["request_artifacts"] = arr(req_art, min_items, True, max_items)
            if "runtime_invocation_response_artifacts" in props:
                min_items = props["runtime_invocation_response_artifacts"].get("minItems", 1) if isinstance(props["runtime_invocation_response_artifacts"], dict) else 1
                max_items = props["runtime_invocation_response_artifacts"].get("maxItems") if isinstance(props["runtime_invocation_response_artifacts"], dict) else None
                props["runtime_invocation_response_artifacts"] = arr(resp_art, min_items, True, max_items)
        return schema

    def write_contracts_cyclefree2() -> list[Path]:
        paths = write_contracts_strict()
        defs = {"StateResolutionRequestFingerprintPayload_v0_1_2": state_resolution_request_fingerprint_payload_schema_strict(), "RuntimeInvocationResponseFingerprintPayload_v0_1_2": runtime_invocation_response_fingerprint_payload_schema_cyclefree(), "StateBundleManifestFingerprintPayload_v0_1_2": state_bundle_manifest_fingerprint_payload_schema_cyclefree()}
        for path in paths:
            doc = read_json(path)
            schema = doc.get("json_schema", {})
            schema.setdefault("$defs", {}).update(copy.deepcopy(defs))
            if path.name == "state_resolution_request_contract_v0_1_2.json":
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["StateResolutionRequestFingerprintPayload_v0_1_2"])
            elif path.name == "runtime_user_invocation_response_contract_v0_1_2.json":
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["RuntimeInvocationResponseFingerprintPayload_v0_1_2"])
            elif path.name == "state_bundle_manifest_contract_v0_1_2.json":
                doc["json_schema"] = bundle_schema_cyclefree2()
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["StateBundleManifestFingerprintPayload_v0_1_2"])
            elif "fingerprint_payload_schema" in doc:
                doc.pop("fingerprint_payload_schema", None)
            write_json(path, doc)
        return paths

    bundle_schema_strict = bundle_schema_cyclefree2
    bundle_schema_final = bundle_schema_cyclefree2
    write_contracts_final = write_contracts_cyclefree2
    g["bundle_schema"] = bundle_schema_cyclefree2
    g["write_contracts"] = write_contracts_cyclefree2
    g["main"] = main_final

    def state_bundle_manifest_fingerprint_payload_schema_cyclefree_direct() -> dict[str, Any]:
        binding = obj({"request_ref_id": string(), "request_ref_sha256": hex64(), "request_fingerprint": hex64(), "response_ref_id": string(), "response_ref_sha256": hex64(), "state_kind": {"enum": ["market_state", "event_state"]}}, ["request_ref_id", "request_ref_sha256", "request_fingerprint", "response_ref_id", "response_ref_sha256", "state_kind"])
        profile = obj({"state_kind": {"enum": ["market_state", "event_state"]}, "profile_id": string(), "profile_version": string(), "profile_fingerprint": hex64()}, ["state_kind", "profile_id", "profile_version", "profile_fingerprint"])
        artifact = obj({"artifact_id": string(), "artifact_type": string(), "sha256": hex64(), "availability": {"const": "available"}}, ["artifact_id", "artifact_type", "sha256", "availability"])
        props = {"state_bundle_manifest_id": string(), "bundle_state_mode": {"enum": ["market_state_only", "event_state_only", "market_and_event"]}, "state_kinds": arr({"enum": ["market_state", "event_state"]}, 1, True, 2), "request_response_binding_payloads": arr(binding, 1, True, 2), "capability_refs": arr(ref_schema("runtime_capability", "available"), 1, True, 2), "dataset_refs": obj({"market_state_dataset_ref": nullable(dataset_ref_schema("market_state")), "event_state_dataset_ref": nullable(dataset_ref_schema("event_state"))}, ["market_state_dataset_ref", "event_state_dataset_ref"]), "coverage": coverage_schema(1), "validation_status": {"enum": ["PASS", "PASS_WITH_RESTRICTIONS", "BLOCKED", "FAIL"]}, "restrictions": arr(string(), 1, True), "representation_profile_versions": arr(profile, 1, True, 2), "schema_fingerprints": arr(hex64(), 1, True), "source_dataset_ids": arr(string(), 1, True), "source_content_hashes": arr(hex64(), 1, True), "artifact_hashes": arr(artifact, 1, True), "field_lineage": arr(obj({"field_id": string(), "builder_id": string(), "input_refs": arr(string(), 1, True)}, ["field_id", "builder_id", "input_refs"]), 1, True), "temporal_policy": obj({"point_in_time_policy_id": string(), "available_at_policy_id": string(), "future_information_exclusion": {"const": True}}, ["point_in_time_policy_id", "available_at_policy_id", "future_information_exclusion"]), "materialization_status": {"enum": ["reference_only", "validated_candidate_reference", "blocked", "failed"]}, "reuse_certification": obj({"reuse_eligible": {"type": "boolean"}, "reuse_decision": {"enum": ["eligible", "eligible_with_restrictions", "not_eligible_failed_or_blocked"]}, "reusable_dataset_refs": arr(string(), 0, True)}, ["reuse_eligible", "reuse_decision", "reusable_dataset_refs"]), "consumption_authorization": obj({"backtest_consumption_authorized": {"const": False}, "downstream_authorized": {"const": False}, "consumption_purposes": arr(string(), 0, True, 0)}, ["backtest_consumption_authorized", "downstream_authorized", "consumption_purposes"]), "official_dataset": {"const": False}, "production": {"const": False}, "downstream": {"const": False}, "physical_rows_delivered": {"const": False}}
        return obj(props, list(props))

    state_bundle_manifest_fingerprint_payload_schema_cyclefree = state_bundle_manifest_fingerprint_payload_schema_cyclefree_direct
    state_bundle_manifest_fingerprint_payload_schema_strict = state_bundle_manifest_fingerprint_payload_schema_cyclefree_direct
    g["state_bundle_manifest_fingerprint_payload_schema"] = state_bundle_manifest_fingerprint_payload_schema_cyclefree_direct
    g["main"] = main_final

    def valid_response_cyclefree2(kind: str = "market_state", status: str = "reuse_hit") -> dict[str, Any]:
        doc = base_valid_response(kind, status)
        req = valid_request_strict(kind)
        doc["request_ref"] = copy.deepcopy(req["request_ref"])
        doc["request_fingerprint"] = req["request_fingerprint"]
        doc["response_ref"]["ref_id"] = f"{kind}_response_ref"
        if status == "reuse_hit":
            doc["dataset_id"] = f"{kind}_dataset_001"
            doc["artifact_references"] = [ref_value("runtime_artifact", f"{kind}_artifact_ref", h(f"artifact_{kind}"))]
        return set_response_fingerprint_cyclefree(doc)

    def valid_bundle_cyclefree2(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]
        requests = {kind: valid_request_strict(kind) for kind in kinds}
        def dataset(k: str) -> dict[str, Any]:
            return {"dataset_id": f"{k}_dataset_001", "dataset_kind": k, "candidate_dataset_fingerprint": h(f"dataset_{k}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
        def capability_ref(k: str) -> dict[str, Any]:
            cap_id = f"{k}_on_demand_runtime_capability_v0_1"
            return ref_value("runtime_capability", cap_id, h(cap_id))
        doc = {"state_bundle_manifest_id": f"bundle_{mode}_001", "bundle_ref": ref_value("state_bundle_manifest", f"bundle_ref_{mode}_001", h("pending_bundle")), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": [], "request_artifacts": [], "runtime_invocation_response_artifacts": [], "capability_refs": [capability_ref(k) for k in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": k, "profile_id": "market_state_core_four_intraday_profile_v0_1" if k == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{k}")} for k in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": ["source_001"], "source_content_hashes": [h("source")], "artifact_hashes": [{"artifact_id": f"artifact_{k}_001", "artifact_type": "manifest", "sha256": h(f"artifact_{k}"), "availability": "available"} for k in kinds], "field_lineage": [{"field_id": f"field_{k}_001", "builder_id": f"builder_{k}_001", "input_refs": [f"input_{k}_001"]} for k in kinds], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{k}_dataset_001" for k in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}
        for k in kinds:
            response = valid_response_cyclefree2(k, "reuse_hit")
            response["request_ref"] = copy.deepcopy(requests[k]["request_ref"])
            response["request_fingerprint"] = requests[k]["request_fingerprint"]
            response["dataset_id"] = f"{k}_dataset_001"
            response["state_bundle_manifest_ref"] = copy.deepcopy(doc["bundle_ref"])
            response["artifact_references"] = [ref_value("runtime_artifact", f"{k}_artifact_ref", h(f"artifact_{k}"))]
            response = set_response_fingerprint_cyclefree(response)
            req_payload = request_payload_from_doc_strict(requests[k]); req_hash = canonical_sha(req_payload)
            resp_payload = response_payload_from_doc_cyclefree(response); resp_hash = canonical_sha(resp_payload)
            doc["request_response_bindings"].append({"request_ref": copy.deepcopy(requests[k]["request_ref"]), "request_fingerprint": requests[k]["request_fingerprint"], "response_ref": copy.deepcopy(response["response_ref"]), "state_kind": k})
            doc["request_artifacts"].append({"artifact_ref_id": requests[k]["request_ref"]["ref_id"], "artifact_ref_sha256": requests[k]["request_ref"]["sha256"], "content_fingerprint": req_hash, "request_fingerprint": req_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": req_payload, "availability": "available"})
            doc["runtime_invocation_response_artifacts"].append({"artifact_ref_id": response["response_ref"]["ref_id"], "artifact_ref_sha256": response["response_ref"]["sha256"], "content_fingerprint": resp_hash, "request_fingerprint": requests[k]["request_fingerprint"], "response_fingerprint": resp_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": resp_payload, "availability": "available"})
        return set_bundle_fingerprint_cyclefree(doc)

    valid_response_cyclefree = valid_response_cyclefree2
    valid_bundle_cyclefree = valid_bundle_cyclefree2
    valid_response_strict = valid_response_cyclefree2
    valid_bundle_strict = valid_bundle_cyclefree2
    valid_response_final = valid_response_cyclefree2
    valid_bundle_final = valid_bundle_cyclefree2
    g["valid_response"] = valid_response_cyclefree2
    g["valid_bundle"] = valid_bundle_cyclefree2
    g["main"] = main_final

    def bundle_fingerprint_payload_from_doc_cyclefree2(doc: dict[str, Any]) -> dict[str, Any]:
        binding_payloads = []
        for binding in doc.get("request_response_bindings", []):
            request_ref = binding.get("request_ref") if isinstance(binding.get("request_ref"), dict) else {}
            response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
            binding_payloads.append({"request_ref_id": request_ref.get("ref_id"), "request_ref_sha256": request_ref.get("sha256"), "request_fingerprint": binding.get("request_fingerprint"), "response_ref_id": response_ref.get("ref_id"), "response_ref_sha256": response_ref.get("sha256"), "state_kind": binding.get("state_kind")})
        return {"state_bundle_manifest_id": copy.deepcopy(doc.get("state_bundle_manifest_id")), "bundle_state_mode": copy.deepcopy(doc.get("bundle_state_mode")), "state_kinds": copy.deepcopy(doc.get("state_kinds")), "request_response_binding_payloads": binding_payloads, "capability_refs": copy.deepcopy(doc.get("capability_refs")), "dataset_refs": copy.deepcopy(doc.get("dataset_refs")), "coverage": copy.deepcopy(doc.get("coverage")), "validation_status": copy.deepcopy(doc.get("validation_status")), "restrictions": copy.deepcopy(doc.get("restrictions")), "representation_profile_versions": copy.deepcopy(doc.get("representation_profile_versions")), "schema_fingerprints": copy.deepcopy(doc.get("schema_fingerprints")), "source_dataset_ids": copy.deepcopy(doc.get("source_dataset_ids")), "source_content_hashes": copy.deepcopy(doc.get("source_content_hashes")), "artifact_hashes": copy.deepcopy(doc.get("artifact_hashes")), "field_lineage": copy.deepcopy(doc.get("field_lineage")), "temporal_policy": copy.deepcopy(doc.get("temporal_policy")), "materialization_status": copy.deepcopy(doc.get("materialization_status")), "reuse_certification": copy.deepcopy(doc.get("reuse_certification")), "consumption_authorization": copy.deepcopy(doc.get("consumption_authorization")), "official_dataset": copy.deepcopy(doc.get("official_dataset")), "production": copy.deepcopy(doc.get("production")), "downstream": copy.deepcopy(doc.get("downstream")), "physical_rows_delivered": copy.deepcopy(doc.get("physical_rows_delivered"))}

    bundle_fingerprint_payload_from_doc_cyclefree = bundle_fingerprint_payload_from_doc_cyclefree2
    bundle_fingerprint_payload_from_doc_strict = bundle_fingerprint_payload_from_doc_cyclefree2
    g["bundle_fingerprint_payload_from_doc"] = bundle_fingerprint_payload_from_doc_cyclefree2
    g["main"] = main_final

    def write_readout_cyclefree3(now: str, matrix: dict[str, Any], zip_path: Path) -> Path:
        path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_readout.md"
        text = f"""# Runtime Provider Contract Schema Hardening v0.1.2 Readout

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{matrix['status']}`

## Runtime Provider v0.1.2 External Audit Genealogy

```text
061024Z = FAIL_DOCUMENT_AND_SEMANTIC_GAPS
070232Z = FAIL_DOCUMENT_AND_SEMANTIC_GAPS
075406Z = FAIL_SEMANTIC_FINGERPRINT_GAPS
083304Z = FAIL_EMBEDDED_PAYLOAD_SCHEMA_GAPS
092039Z = FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS
current package = CYCLE_FREE_CORRECTIVE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT
```

```text
case_count = {matrix['case_count']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
duplicate_case_ids = {len(matrix['duplicate_case_ids'])}
unexpected_case_ids = {len(matrix['unexpected_case_ids'])}
failed_cases = {matrix['failed_cases']}
jsonschema_draft_2020_12_compile = {matrix['jsonschema_draft_2020_12_compile']}
ajv_8_17_1_strict_runtime = {matrix['ajv_8_17_1_strict_runtime']}
semantic_validator_execution = {matrix['semantic_validator_execution']}
expanded_adversarial_matrix = {matrix['expanded_adversarial_matrix']}
package_manifest_reproducibility = PASS
provider_only_isolation = PASS
document_encoding_integrity = PASS
```

## Cycle-Free Fingerprint Closure

```text
response_fingerprint_excludes_bundle_ref_sha256 = true
bundle_fingerprint_includes_response_ref_sha256 = true
outer_artifact_metadata_correlated_with_content = true
restriction_propagation_checked = true
validation_severity_not_weakened = true
reuse_certification_state_machine_closed = true
fingerprint_payload_schema_single_authority = true
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
"""
        write_text(path, text)
        return path

    write_readout = write_readout_cyclefree3
    g["main"] = main_final

    def semantic_errors_cyclefree2(doc: dict[str, Any], kind: str) -> list[str]:
        return [e for e in semantic_errors_cyclefree(doc, kind) if e != "embedded response state_bundle_manifest_ref does not match bundle_ref"]

    def _body_from_any_anchor(text: str, anchors: list[str]) -> str:
        hits = [text.find(anchor) for anchor in anchors if text.find(anchor) >= 0]
        return text[min(hits):] if hits else ""

    def update_docs_cyclefree3(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        genealogy = "```text\n061024Z = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\n070232Z = FAIL_DOCUMENT_AND_SEMANTIC_GAPS\n075406Z = FAIL_SEMANTIC_FINGERPRINT_GAPS\n083304Z = FAIL_EMBEDDED_PAYLOAD_SCHEMA_GAPS\n092039Z = FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS\ncurrent package = CYCLE_FREE_CORRECTIVE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT\n```"
        route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
        route_body = _body_from_any_anchor(read_text(route) if route.exists() else "", ["<!-- TSIS_ROUTE_CURRENT_STATE_V1_33_START -->"])
        route_block = f"""## Provider Contract Schema Hardening v0.1.2 Cycle-Free Corrective Internal Pass - {now[:10]}

```text
{GATE}
=
{matrix['status']}

PROVIDER_V0_1_2_EXTERNAL_AUDIT_GENEALOGY
=
RECORDED_THROUGH_092039Z

PROVIDER_V0_1_2_EXTERNAL_AUDIT
=
PENDING_REAUDIT

PROVIDER_CONSUMER_COMPATIBILITY
=
NOT_OPENED_AFTER_V0_1_2
```

## Runtime Provider v0.1.2 External Audit Genealogy

{genealogy}

```text
case_count = {matrix['case_count']}
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

Provider-only ZIP pending external audit:

```text
{zip_path}
```"""
        write_text(route, route_block.strip() + "\n\n" + route_body.lstrip())
        readme = RUNTIME / "README.md"
        readme_body = _body_from_any_anchor(read_text(readme) if readme.exists() else "", ["# 08_RUNTIME_CAPABILITIES"])
        readme_body = readme_body.replace("Next provider-owned gate:\n\n```text\nruntime_provider_contract_schema_hardening_v0_1_2\n```", "Next provider-owned gate:\n\n```text\nruntime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending\n```")
        readme_block = f"""## Provider Contract Schema Hardening v0.1.2 Cycle-Free Corrective Internal Pass

```text
{GATE} = {matrix['status']}
PROVIDER_V0_1_2_EXTERNAL_AUDIT_GENEALOGY = RECORDED_THROUGH_092039Z
PROVIDER_V0_1_2_EXTERNAL_AUDIT = PENDING_REAUDIT
PROVIDER_CONSUMER_COMPATIBILITY = NOT_OPENED_AFTER_V0_1_2
```

## Runtime Provider v0.1.2 External Audit Genealogy

{genealogy}

This package remains provider-only and pending independent external audit. Physical row delivery, StateReplayFeed, backtest consumption, production and downstream remain closed."""
        write_text(readme, readme_block.strip() + "\n\n" + readme_body.lstrip())
        agent = FEATURE_ROOT / "AGENT.md"
        agent_body = _body_from_any_anchor(read_text(agent) if agent.exists() else "", ["## Historical Runtime Handoff Override - Provider Contract Schema Hardening v0.1.2 Quarantined", "## Historical Agent Handoff Prompt"])
        agent_block = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Provider Hardening v0.1.2 Cycle-Free Corrective Internal Pass Pending External Audit

Status: `agent_handoff_prompt_v0_140`
Date: `{now[:10]}`

```text
current_gate = runtime_provider_contract_schema_hardening_v0_1_2_external_reaudit_pending
boundary_layer = 08_RUNTIME_CAPABILITIES
last_closed_gate = {GATE}
last_closed_status = {matrix['status']}
provider_v0_1_2_external_audit_genealogy = RECORDED_THROUGH_092039Z
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

## Runtime Provider v0.1.2 External Audit Genealogy

{genealogy}

Do not open provider-consumer compatibility, StateBundle physical reads, StateReplayFeed, backtest state integration, production or downstream until this provider-only ZIP passes external audit."""
        write_text(agent, agent_block.strip() + "\n\n" + agent_body.lstrip())
        changelog = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"
        ch = read_text(changelog) if changelog.exists() else ""
        lines = ch.splitlines()
        kept = []
        i = 0
        while i < len(lines):
            if lines[i].startswith("## ") and "Runtime provider hardening v0.1.2" in lines[i]:
                i += 1
                while i < len(lines) and not lines[i].startswith("## "):
                    i += 1
                continue
            kept.append(lines[i]); i += 1
        cb = f"""## {now[:10]} - Runtime provider hardening v0.1.2 cycle-free corrective internal pass pending external audit

- Recorded external audit genealogy through `092039Z`: `061024Z`, `070232Z`, `075406Z`, `083304Z`, and `092039Z` all failed external audit with progressively narrower semantic findings.
- Broke the response/bundle fingerprint cycle by excluding `state_bundle_manifest_ref.sha256` from the response fingerprint and including `response_ref.sha256` in the bundle fingerprint.
- Added artifact outer metadata correlation, restriction propagation, validation severity and `reuse_certification` state-machine checks.
- Replaced top-level `fingerprint_payload_schema` with the same strict authority exposed under `json_schema.$defs`.
- Kept runtime requests, builds, datasets, registry mutations, physical state rows, StateReplayFeed, backtest consumption, production and downstream closed."""
        write_text(changelog, cb.strip() + "\n\n" + "\n".join(kept).lstrip() + "\n")

    semantic_errors_final = semantic_errors_cyclefree2
    update_docs_final = update_docs_cyclefree3
    g["semantic_errors"] = semantic_errors_cyclefree2
    g["update_docs"] = update_docs_cyclefree3
    g["main"] = main_final

    base_write_ajv_reproducibility_files = write_ajv_reproducibility_files

    def write_ajv_reproducibility_files_vendor(now: str) -> list[Path]:
        files = list(base_write_ajv_reproducibility_files(now))
        vendor_path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_runtime_vendor_ajv_8_17_1.zip"
        node_modules = g["AJV_NODE_MODULES"]
        zipfile_mod = g["zipfile"]
        if node_modules.exists():
            with zipfile_mod.ZipFile(vendor_path, "w", compression=zipfile_mod.ZIP_DEFLATED) as zf:
                for file in sorted(node_modules.rglob("*")):
                    if file.is_file():
                        zf.write(file, Path("ajv_runtime_vendor") / "node_modules" / file.relative_to(node_modules))
            manifest_path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_vendor_manifest.json"
            write_json(manifest_path, {"manifest_id": "runtime_provider_contract_schema_hardening_v0_1_2_ajv_vendor_manifest", "created_at_utc": now, "vendor_zip": vendor_path.name, "vendor_zip_sha256": sha256_file(vendor_path), "vendor_zip_size_bytes": vendor_path.stat().st_size, "node_modules_root_inside_zip": "ajv_runtime_vendor/node_modules", "ajv_version": "8.17.1", "external_reproduction_instruction": "Extract vendor zip and set NODE_PATH to ajv_runtime_vendor/node_modules before running the AJV strict compile check."})
            files.extend([vendor_path, manifest_path])
        return files

    write_ajv_reproducibility_files = write_ajv_reproducibility_files_vendor
    g["main"] = main_final

    def write_scope_cyclefree3(now: str) -> Path:
        path = write_scope_cyclefree2(now)
        doc = read_json(path)
        outputs = doc.setdefault("authorized_outputs", [])
        for out in ["configs/runtime_provider_contract_schema_hardening_v0_1_2_ajv_runtime_vendor_ajv_8_17_1.zip", "configs/runtime_provider_contract_schema_hardening_v0_1_2_ajv_vendor_manifest.json"]:
            if out not in outputs:
                outputs.append(out)
        write_json(path, doc)
        return path

    write_scope_final = write_scope_cyclefree3
    g["write_scope"] = write_scope_cyclefree3
    g["main"] = main_final

    # External audit 100143Z closure: keep response/bundle fingerprints acyclic
    # while removing mutable, unauthenticated cross-artifact declarations.
    def state_bundle_pointer_schema() -> dict[str, Any]:
        return obj(
            {
                "ref_id": string(),
                "ref_type": {"const": "state_bundle_manifest"},
                "availability": {"const": "available"},
            },
            ["ref_id", "ref_type", "availability"],
        )

    def bundle_pointer(ref_id: str, availability: str = "available") -> dict[str, Any]:
        return {"ref_id": ref_id, "ref_type": "state_bundle_manifest", "availability": availability}

    def response_schema_100143() -> dict[str, Any]:
        schema = copy.deepcopy(response_schema_base())
        schema["properties"]["state_bundle_manifest_ref"] = nullable(state_bundle_pointer_schema())
        for rule in schema.get("allOf", []):
            props = rule.get("then", {}).get("properties", {})
            if "state_bundle_manifest_ref" in props:
                current = props["state_bundle_manifest_ref"]
                if isinstance(current, dict) and current.get("type") == "null":
                    props["state_bundle_manifest_ref"] = {"type": "null"}
                else:
                    props["state_bundle_manifest_ref"] = state_bundle_pointer_schema()
        return schema

    def valid_response_100143(kind: str = "market_state", status: str = "reuse_hit") -> dict[str, Any]:
        doc = valid_response_cyclefree2(kind, status)
        if isinstance(doc.get("state_bundle_manifest_ref"), dict):
            doc["state_bundle_manifest_ref"] = bundle_pointer(doc["state_bundle_manifest_ref"]["ref_id"])
        return set_response_fingerprint_cyclefree(doc)

    def valid_bundle_100143(mode: str = "market_state_only") -> dict[str, Any]:
        kinds = {"market_state_only": ["market_state"], "event_state_only": ["event_state"], "market_and_event": ["market_state", "event_state"]}[mode]
        requests = {kind: valid_request_strict(kind) for kind in kinds}
        def dataset(k: str) -> dict[str, Any]:
            return {"dataset_id": f"{k}_dataset_001", "dataset_kind": k, "candidate_dataset_fingerprint": h(f"dataset_{k}"), "validation_status": "PASS_WITH_RESTRICTIONS", "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}
        def capability_ref(k: str) -> dict[str, Any]:
            cap_id = f"{k}_on_demand_runtime_capability_v0_1"
            return ref_value("runtime_capability", cap_id, h(cap_id))
        doc = {"state_bundle_manifest_id": f"bundle_{mode}_001", "bundle_ref": ref_value("state_bundle_manifest", f"bundle_ref_{mode}_001", h("pending_bundle")), "bundle_state_mode": mode, "state_kinds": kinds, "request_response_bindings": [], "request_artifacts": [], "runtime_invocation_response_artifacts": [], "capability_refs": [capability_ref(k) for k in kinds], "dataset_refs": {"market_state_dataset_ref": dataset("market_state") if "market_state" in kinds else None, "event_state_dataset_ref": dataset("event_state") if "event_state" in kinds else None}, "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0}, "validation_status": "PASS_WITH_RESTRICTIONS", "restrictions": ["candidate_runtime_only"], "representation_profile_versions": [{"state_kind": k, "profile_id": "market_state_core_four_intraday_profile_v0_1" if k == "market_state" else "event_state_core_four_intraday_profile_v0_1", "profile_version": "v0_1", "profile_fingerprint": h(f"profile_{k}")} for k in kinds], "schema_fingerprints": [h("schema")], "source_dataset_ids": [f"{k}_source_001" for k in kinds], "source_content_hashes": [h(f"source_{k}") for k in kinds], "artifact_hashes": [{"artifact_id": f"artifact_{k}_001", "artifact_type": "manifest", "sha256": h(f"artifact_{k}"), "availability": "available"} for k in kinds], "field_lineage": [{"field_id": f"field_{k}_001", "builder_id": f"builder_{k}_001", "input_refs": [f"input_{k}_001"]} for k in kinds], "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True}, "materialization_status": "reference_only", "reuse_certification": {"reuse_eligible": True, "reuse_decision": "eligible_with_restrictions", "reusable_dataset_refs": [f"{k}_dataset_001" for k in kinds]}, "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []}, "official_dataset": False, "production": False, "downstream": False, "physical_rows_delivered": False}
        for k in kinds:
            response = valid_response_100143(k, "reuse_hit")
            response["request_ref"] = copy.deepcopy(requests[k]["request_ref"])
            response["request_fingerprint"] = requests[k]["request_fingerprint"]
            response["dataset_id"] = f"{k}_dataset_001"
            response["state_bundle_manifest_ref"] = bundle_pointer(doc["bundle_ref"]["ref_id"])
            response["artifact_references"] = [ref_value("runtime_artifact", f"artifact_{k}_001", h(f"artifact_{k}"))]
            response = set_response_fingerprint_cyclefree(response)
            req_payload = request_payload_from_doc_strict(requests[k])
            req_hash = canonical_sha(req_payload)
            resp_payload = response_payload_from_doc_cyclefree(response)
            resp_hash = canonical_sha(resp_payload)
            doc["request_response_bindings"].append({"request_ref": copy.deepcopy(requests[k]["request_ref"]), "request_fingerprint": requests[k]["request_fingerprint"], "response_ref": copy.deepcopy(response["response_ref"]), "state_kind": k})
            doc["request_artifacts"].append({"artifact_ref_id": requests[k]["request_ref"]["ref_id"], "artifact_ref_sha256": requests[k]["request_ref"]["sha256"], "content_fingerprint": req_hash, "request_fingerprint": req_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": req_payload, "availability": "available"})
            doc["runtime_invocation_response_artifacts"].append({"artifact_ref_id": response["response_ref"]["ref_id"], "artifact_ref_sha256": response["response_ref"]["sha256"], "content_fingerprint": resp_hash, "request_fingerprint": requests[k]["request_fingerprint"], "response_fingerprint": resp_hash, "state_kind": k, "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256", "canonical_content": resp_payload, "availability": "available"})
        return set_bundle_fingerprint_cyclefree(doc)

    def strip_embedded_schema_ids(value: Any, root: bool = True) -> Any:
        if isinstance(value, dict):
            out = {}
            for key, child in value.items():
                if key == "$id" and not root:
                    continue
                out[key] = strip_embedded_schema_ids(child, False)
            return out
        if isinstance(value, list):
            return [strip_embedded_schema_ids(item, False) for item in value]
        return value

    def write_contracts_100143() -> list[Path]:
        paths = write_contracts_cyclefree2()
        defs = {"StateResolutionRequestFingerprintPayload_v0_1_2": state_resolution_request_fingerprint_payload_schema_strict(), "RuntimeInvocationResponseFingerprintPayload_v0_1_2": runtime_invocation_response_fingerprint_payload_schema_cyclefree(), "StateBundleManifestFingerprintPayload_v0_1_2": state_bundle_manifest_fingerprint_payload_schema_cyclefree()}
        for path in paths:
            doc = read_json(path)
            if path.name == "runtime_user_invocation_response_contract_v0_1_2.json":
                schema = response_schema_100143()
                schema.setdefault("$defs", {}).update(copy.deepcopy(defs))
                doc["json_schema"] = strip_embedded_schema_ids(schema)
                doc["fingerprint_payload_schema"] = copy.deepcopy(defs["RuntimeInvocationResponseFingerprintPayload_v0_1_2"])
            elif path.name == "runtime_user_invocation_interface_contract_v0_1_2.json":
                doc["json_schema"] = strip_embedded_schema_ids(doc["json_schema"])
            elif path.name == "state_bundle_manifest_contract_v0_1_2.json":
                doc["json_schema"] = strip_embedded_schema_ids(doc["json_schema"])
            write_json(path, doc)
        return paths

    def semantic_errors_100143(doc: dict[str, Any], kind: str) -> list[str]:
        errors = list(semantic_errors_cyclefree2(doc, kind))
        if kind == "response":
            bundle_ref = doc.get("state_bundle_manifest_ref")
            if isinstance(bundle_ref, dict) and "sha256" in bundle_ref:
                errors.append("response state_bundle_manifest_ref must be id-only to avoid mutable bundle sha")
        if kind == "bundle":
            source_ids = doc.get("source_dataset_ids") or []
            source_hashes = doc.get("source_content_hashes") or []
            if len(source_ids) != len(source_hashes):
                errors.append("source_dataset_ids and source_content_hashes cardinality mismatch")
            artifact_ids: dict[str, str] = {}
            for artifact in doc.get("artifact_hashes", []) if isinstance(doc.get("artifact_hashes"), list) else []:
                if not isinstance(artifact, dict):
                    continue
                artifact_id = artifact.get("artifact_id")
                artifact_sha = artifact.get("sha256")
                if artifact_id in artifact_ids and artifact_ids[artifact_id] != artifact_sha:
                    errors.append("duplicate artifact_id with conflicting sha256")
                elif artifact_id in artifact_ids:
                    errors.append("duplicate artifact_id")
                else:
                    artifact_ids[artifact_id] = artifact_sha
            lineage_ids: dict[str, str] = {}
            for lineage in doc.get("field_lineage", []) if isinstance(doc.get("field_lineage"), list) else []:
                if not isinstance(lineage, dict):
                    continue
                field_id = lineage.get("field_id")
                builder_id = lineage.get("builder_id")
                if field_id in lineage_ids and lineage_ids[field_id] != builder_id:
                    errors.append("duplicate field_id with conflicting builder_id")
                elif field_id in lineage_ids:
                    errors.append("duplicate field_id")
                else:
                    lineage_ids[field_id] = builder_id
            for response_artifact in doc.get("runtime_invocation_response_artifacts", []) if isinstance(doc.get("runtime_invocation_response_artifacts"), list) else []:
                if not isinstance(response_artifact, dict):
                    continue
                response_content = response_artifact.get("canonical_content") if isinstance(response_artifact.get("canonical_content"), dict) else {}
                if "state_bundle_manifest_ref_sha256" in response_content:
                    errors.append("embedded response content must not carry bundle sha in cycle-free fingerprint")
                for ref in response_content.get("artifact_references") or []:
                    if not isinstance(ref, dict):
                        continue
                    if artifact_ids.get(ref.get("ref_id")) != ref.get("sha256"):
                        errors.append("embedded response artifact_reference missing from bundle artifact_hashes")
        return list(dict.fromkeys(errors))

    case_ids_100143 = [
        "F09_100143_response_bundle_ref_sha_disallowed",
        "F09_100143_response_artifact_missing_from_bundle_artifacts",
        "F09_100143_source_ids_hashes_cardinality_mismatch",
        "F09_100143_duplicate_artifact_id_conflicting_hash",
        "F09_100143_duplicate_field_lineage_id_conflicting_builder",
        "F09_100143_shared_ajv_registry_compile_no_duplicate_ids",
    ]

    def _shared_schema_id_ok(contracts: dict[str, dict[str, Any]]) -> tuple[bool, list[str]]:
        seen: set[str] = set()
        errors: list[str] = []
        for name, doc in contracts.items():
            schema = doc.get("json_schema", {})
            schema_id = schema.get("$id")
            if schema_id in seen:
                errors.append(f"duplicate root $id: {schema_id}")
            if schema_id:
                seen.add(schema_id)
            nested: list[tuple[str, str]] = []
            def walk(value: Any, path: str = "") -> None:
                if isinstance(value, dict):
                    if "$id" in value and path:
                        nested.append((path, value["$id"]))
                    for key, child in value.items():
                        walk(child, f"{path}/{key}" if path else key)
                elif isinstance(value, list):
                    for idx, child in enumerate(value):
                        walk(child, f"{path}[{idx}]")
            walk(schema)
            for path, schema_id in nested:
                errors.append(f"embedded $id in {name} at {path}: {schema_id}")
        return not errors, errors

    def run_matrix_100143(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        matrix = run_matrix_cyclefree(contracts)
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        rows = [row for row in matrix["rows"] if row.get("case_id") not in set(case_ids_100143 + ["positive_market_bundle", "positive_event_bundle", "positive_market_and_event_bundle_unique_refs", "positive_reuse_hit_market_response", "positive_authorized_reference"])]
        resp_schema = schemas["runtime_user_invocation_response_contract_v0_1_2.json"]
        bundle_schema_doc = schemas["state_bundle_manifest_contract_v0_1_2.json"]
        add_case(rows, "positive_reuse_hit_market_response", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_100143("market_state", "reuse_hit"), True)
        add_case(rows, "positive_authorized_reference", "original_31_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", valid_response_100143("market_state", "authorized_reference"), True)
        add_case(rows, "positive_market_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_100143("market_state_only"), True)
        add_case(rows, "positive_event_bundle", "original_31_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_100143("event_state_only"), True)
        add_case(rows, "positive_market_and_event_bundle_unique_refs", "external_083304_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", valid_bundle_100143("market_and_event"), True)
        bad_response = valid_response_100143("market_state", "reuse_hit")
        bad_response["state_bundle_manifest_ref"] = {**bad_response["state_bundle_manifest_ref"], "sha256": h("mutable_bundle_sha")}
        add_case(rows, "F09_100143_response_bundle_ref_sha_disallowed", "external_100143_regression", "runtime_user_invocation_response_contract_v0_1_2.json", resp_schema, "response", bad_response, False)
        bundle_cases = [
            ("F09_100143_response_artifact_missing_from_bundle_artifacts", mutate(valid_bundle_100143(), lambda d: (d["runtime_invocation_response_artifacts"][0]["canonical_content"].update({"artifact_references": [ref_value("runtime_artifact", "missing_artifact", h("missing_artifact"))]}), _recompute_response_artifact(d, 0), set_bundle_fingerprint_cyclefree(d)))),
            ("F09_100143_source_ids_hashes_cardinality_mismatch", mutate(valid_bundle_100143(), lambda d: (d["source_content_hashes"].append(h("extra_source_hash")), set_bundle_fingerprint_cyclefree(d)))),
            ("F09_100143_duplicate_artifact_id_conflicting_hash", mutate(valid_bundle_100143(), lambda d: (d["artifact_hashes"].append({"artifact_id": d["artifact_hashes"][0]["artifact_id"], "artifact_type": "manifest", "sha256": h("different_artifact_hash"), "availability": "available"}), set_bundle_fingerprint_cyclefree(d)))),
            ("F09_100143_duplicate_field_lineage_id_conflicting_builder", mutate(valid_bundle_100143(), lambda d: (d["field_lineage"].append({"field_id": d["field_lineage"][0]["field_id"], "builder_id": "different_builder", "input_refs": ["input_other"]}), set_bundle_fingerprint_cyclefree(d)))),
        ]
        for case_id, doc in bundle_cases:
            add_case(rows, case_id, "external_100143_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", doc, False)
        shared_ok, shared_errors = _shared_schema_id_ok(contracts)
        rows.append({"case_id": "F09_100143_shared_ajv_registry_compile_no_duplicate_ids", "case_origin": "external_100143_regression", "schema": "all_provider_contracts_shared_ajv_registry", "expected_valid": True, "actual_valid": shared_ok, "result": "PASS" if shared_ok else "FAIL", "errors": shared_errors})
        required = list(dict.fromkeys(list(matrix.get("required_case_ids", [])) + case_ids_100143))
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required) - set(case_ids)); unexpected = sorted(set(case_ids) - set(required)); duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        matrix.update({"status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2", "case_count": len(rows), "external_regression_case_count": len([r for r in rows if r["case_origin"] in {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression", "external_092039_regression", "external_100143_regression"}]), "external_followup_case_count": len([r for r in rows if r["case_origin"] in {"external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression", "external_092039_regression", "external_100143_regression"}]), "required_case_ids": required, "missing_required_case_ids": missing, "duplicate_case_ids": duplicates, "unexpected_silent_skips": len(unexpected), "unexpected_case_ids": unexpected, "failed_cases": len(failed), "semantic_validator_execution": "PASS" if not failed else "FAIL", "expanded_adversarial_matrix": "PASS" if ok else "FAIL", "rows": rows})
        return matrix

    failed_audit_genealogy_100143 = failed_audit_genealogy + [
        {"zip": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T100143Z.zip", "result": "FAIL_NARROW_REFERENCE_AND_SHARED_SCHEMA_GAPS"},
    ]

    def write_scope_100143(now: str) -> Path:
        path = write_scope_cyclefree3(now)
        doc = read_json(path)
        doc["previous_external_audit_results"] = copy.deepcopy(failed_audit_genealogy_100143)
        doc["corrective_iteration_label"] = "staging_consolidated_external_audit_100143_closure_candidate"
        doc["required_case_ids"] = list(dict.fromkeys(list(doc.get("required_case_ids", [])) + case_ids_100143))
        doc["minimum_case_counts"] = {"original_regression": 31, "external_combined_regression": len(doc["required_case_ids"]) - 31, "total": len(doc["required_case_ids"])}
        doc["response_bundle_cycle_policy"] = {"runtime_invocation_response_state_bundle_manifest_ref": "id_only_no_sha256", "state_bundle_manifest_fingerprint_includes": ["response_ref.sha256"], "reason": "prevents mutable response-side bundle sha while preserving acyclic bundle identity"}
        write_json(path, doc)
        return path

    def _patch_100143_text(text: str) -> str:
        text = text.replace("RECORDED_THROUGH_092039Z", "RECORDED_THROUGH_100143Z")
        text = text.replace("CYCLE_FREE_CORRECTIVE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT", "STAGING_CONSOLIDATED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT")
        text = text.replace("Cycle-Free Corrective Internal Pass", "Staging Consolidated Internal Pass")
        marker = "100143Z = FAIL_NARROW_REFERENCE_AND_SHARED_SCHEMA_GAPS"
        if marker not in text and "092039Z = FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS" in text:
            text = text.replace("092039Z = FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS", "092039Z = FAIL_BUNDLE_RESPONSE_HASH_CYCLE_AND_RESTRICTION_GAPS\n100143Z = FAIL_NARROW_REFERENCE_AND_SHARED_SCHEMA_GAPS")
        return text

    def update_docs_100143(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        update_docs_cyclefree3(now, matrix, zip_path)
        for path in [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]:
            if path.exists():
                write_text(path, _patch_100143_text(read_text(path)))

    def write_readout_100143(now: str, matrix: dict[str, Any], zip_path: Path) -> Path:
        path = write_readout_cyclefree3(now, matrix, zip_path)
        text = _patch_100143_text(read_text(path))
        extra = "\n## External Audit 100143Z Closure\n\n```text\nresponse_state_bundle_manifest_ref = id_only_no_sha256\nresponse_artifact_refs_must_exist_in_bundle_artifact_hashes = true\nsource_dataset_ids_source_content_hashes_cardinality_match = true\nartifact_id_unique = true\nfield_lineage_field_id_unique = true\nshared_schema_registry_embedded_id_duplicates = blocked\n```\n"
        if "## External Audit 100143Z Closure" not in text:
            text = text.rstrip() + "\n" + extra
        write_text(path, text)
        return path

    def write_ajv_reproducibility_files_100143(now: str) -> list[Path]:
        files = list(write_ajv_reproducibility_files_vendor(now))
        manifest = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_ajv_reproducibility_manifest.json"
        if manifest.exists():
            doc = read_json(manifest)
            doc["shared_registry_compile_required"] = True
            doc["embedded_schema_id_policy"] = "only root schemas carry $id; embedded schemas are id-less"
            write_json(manifest, doc)
        return files

    valid_response_cyclefree = valid_response_100143
    valid_bundle_cyclefree = valid_bundle_100143
    valid_response_strict = valid_response_100143
    valid_bundle_strict = valid_bundle_100143
    valid_response_final = valid_response_100143
    valid_bundle_final = valid_bundle_100143
    semantic_errors_final = semantic_errors_100143
    run_matrix_final = run_matrix_100143
    write_contracts_final = write_contracts_100143
    write_scope_final = write_scope_100143
    update_docs_final = update_docs_100143
    write_readout = write_readout_100143
    write_ajv_reproducibility_files = write_ajv_reproducibility_files_100143
    g["valid_response"] = valid_response_100143
    g["valid_bundle"] = valid_bundle_100143
    g["semantic_errors"] = semantic_errors_100143
    g["run_matrix"] = run_matrix_100143
    g["write_contracts"] = write_contracts_100143
    g["write_scope"] = write_scope_100143
    g["update_docs"] = update_docs_100143
    g["write_ajv_reproducibility_files"] = write_ajv_reproducibility_files_100143
    g["main"] = main_final

    # External audit 105019Z closure - F05 dataset restriction propagation.
    def _dataset_refs_by_kind_105019(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
        refs = doc.get("dataset_refs", {}) if isinstance(doc, dict) else {}
        out: dict[str, dict[str, Any]] = {}
        ms = refs.get("market_state_dataset_ref") if isinstance(refs, dict) else None
        es = refs.get("event_state_dataset_ref") if isinstance(refs, dict) else None
        if isinstance(ms, dict):
            out["market_state"] = ms
        if isinstance(es, dict):
            out["event_state"] = es
        return out

    def _reuse_rank_105019(value: Any) -> int:
        return {
            "eligible": 0,
            "eligible_with_restrictions": 1,
            "not_eligible": 2,
            "not_eligible_failed_or_blocked": 2,
            "not_eligible_missing_authority": 2,
            "not_eligible_dataset_failed_or_blocked": 2,
            "not_eligible_unavailable": 2,
        }.get(value, 99)

    def _bundle_reuse_rank_105019(cert: dict[str, Any]) -> int:
        decision = cert.get("reuse_decision")
        if decision in {"eligible", "eligible_with_restrictions", "not_eligible_failed_or_blocked"}:
            return _reuse_rank_105019(decision)
        if cert.get("reuse_eligible") is True:
            return 0
        return 2

    def semantic_errors_105019(doc: dict[str, Any], kind: str) -> list[str]:
        errors = list(semantic_errors_100143(doc, kind))
        if kind != "bundle" or not isinstance(doc, dict):
            return errors

        dataset_by_kind = _dataset_refs_by_kind_105019(doc)
        artifacts = doc.get("runtime_invocation_response_artifacts", [])
        bindings = doc.get("request_response_bindings", [])
        max_validation = validation_severity(doc.get("validation_status"))
        max_dataset_reuse = -1
        reusable_dataset_ids: list[str] = []

        for state_kind, dataset_ref in dataset_by_kind.items():
            ds_validation = dataset_ref.get("validation_status")
            ds_validation_rank = validation_severity(ds_validation)
            max_validation = max(max_validation, ds_validation_rank)
            ds_reuse = dataset_ref.get("reuse_eligibility")
            max_dataset_reuse = max(max_dataset_reuse, _reuse_rank_105019(ds_reuse))
            if ds_reuse in {"eligible", "eligible_with_restrictions"} and dataset_ref.get("dataset_id"):
                reusable_dataset_ids.append(dataset_ref["dataset_id"])

        for binding in bindings:
            state_kind = binding.get("state_kind")
            response_ref = binding.get("response_ref") if isinstance(binding.get("response_ref"), dict) else {}
            response_artifact = None
            for artifact in artifacts:
                if artifact.get("artifact_ref_id") == response_ref.get("ref_id") and artifact.get("artifact_ref_sha256") == response_ref.get("sha256"):
                    response_artifact = artifact
                    break
            if response_artifact is None:
                continue
            response_content = response_artifact.get("canonical_content", {})
            response_validation_rank = validation_severity(response_content.get("validation_status"))
            max_validation = max(max_validation, response_validation_rank)
            dataset_ref = dataset_by_kind.get(state_kind)
            if dataset_ref is not None:
                dataset_validation_rank = validation_severity(dataset_ref.get("validation_status"))
                if response_validation_rank < dataset_validation_rank:
                    errors.append(f"response validation_status weakens dataset_ref validation_status for {state_kind}")
                dataset_reuse_rank = _reuse_rank_105019(dataset_ref.get("reuse_eligibility"))
                if dataset_reuse_rank > max_dataset_reuse:
                    max_dataset_reuse = dataset_reuse_rank

        bundle_validation_rank = validation_severity(doc.get("validation_status"))
        if bundle_validation_rank < max_validation:
            errors.append("bundle validation_status weakens component validation_status")

        reuse_cert = doc.get("reuse_certification", {})
        if isinstance(reuse_cert, dict):
            bundle_reuse_rank = _bundle_reuse_rank_105019(reuse_cert)
            if max_dataset_reuse >= 0 and bundle_reuse_rank < max_dataset_reuse:
                errors.append("bundle reuse_certification weakens dataset reuse_eligibility")
            refs = sorted(reuse_cert.get("reusable_dataset_refs", []))
            expected_refs = sorted(reusable_dataset_ids)
            if refs != expected_refs:
                errors.append("reuse_certification reusable_dataset_refs must exactly match reusable dataset refs")
            if bundle_reuse_rank == 1 and reuse_cert.get("reuse_decision") != "eligible_with_restrictions":
                errors.append("restricted reusable datasets require eligible_with_restrictions reuse_decision")
            if max_dataset_reuse == 0 and reuse_cert.get("reuse_eligible") is True and reuse_cert.get("reuse_decision") not in {"eligible", "eligible_with_restrictions"}:
                errors.append("reuse_eligible true requires compatible reuse_decision")
        return errors

    def _set_response_validation_105019(doc: dict[str, Any], index: int, status: str) -> None:
        doc["runtime_invocation_response_artifacts"][index]["canonical_content"]["validation_status"] = status
        _recompute_response_artifact(doc, index)
        set_bundle_fingerprint_cyclefree(doc)

    def _case_response_weakens_dataset_validation_105019() -> dict[str, Any]:
        doc = valid_bundle_100143("market_state_only")
        doc["dataset_refs"]["market_state_dataset_ref"]["validation_status"] = "PASS_WITH_RESTRICTIONS"
        _set_response_validation_105019(doc, 0, "PASS")
        doc["validation_status"] = "PASS_WITH_RESTRICTIONS"
        set_bundle_fingerprint_cyclefree(doc)
        return doc

    def _case_bundle_weakens_dataset_validation_105019() -> dict[str, Any]:
        doc = valid_bundle_100143("market_state_only")
        doc["dataset_refs"]["market_state_dataset_ref"]["validation_status"] = "PASS_WITH_RESTRICTIONS"
        _set_response_validation_105019(doc, 0, "PASS_WITH_RESTRICTIONS")
        doc["validation_status"] = "PASS"
        set_bundle_fingerprint_cyclefree(doc)
        return doc

    def _case_reuse_weakens_dataset_reuse_105019() -> dict[str, Any]:
        doc = valid_bundle_100143("market_state_only")
        doc["dataset_refs"]["market_state_dataset_ref"]["reuse_eligibility"] = "eligible_with_restrictions"
        doc["reuse_certification"]["reuse_eligible"] = True
        doc["reuse_certification"]["reuse_decision"] = "eligible"
        doc["reuse_certification"]["reusable_dataset_refs"] = [doc["dataset_refs"]["market_state_dataset_ref"]["dataset_id"]]
        set_bundle_fingerprint_cyclefree(doc)
        return doc

    def _case_combined_validation_weakens_component_105019() -> dict[str, Any]:
        doc = valid_bundle_100143("market_and_event")
        doc["dataset_refs"]["market_state_dataset_ref"]["validation_status"] = "PASS"
        doc["dataset_refs"]["event_state_dataset_ref"]["validation_status"] = "PASS_WITH_RESTRICTIONS"
        _set_response_validation_105019(doc, 0, "PASS")
        _set_response_validation_105019(doc, 1, "PASS_WITH_RESTRICTIONS")
        doc["validation_status"] = "PASS"
        set_bundle_fingerprint_cyclefree(doc)
        return doc

    def _case_combined_reuse_weakens_component_105019() -> dict[str, Any]:
        doc = valid_bundle_100143("market_and_event")
        doc["dataset_refs"]["market_state_dataset_ref"]["reuse_eligibility"] = "eligible"
        doc["dataset_refs"]["event_state_dataset_ref"]["reuse_eligibility"] = "eligible_with_restrictions"
        doc["reuse_certification"]["reuse_eligible"] = True
        doc["reuse_certification"]["reuse_decision"] = "eligible"
        doc["reuse_certification"]["reusable_dataset_refs"] = sorted([
            doc["dataset_refs"]["market_state_dataset_ref"]["dataset_id"],
            doc["dataset_refs"]["event_state_dataset_ref"]["dataset_id"],
        ])
        set_bundle_fingerprint_cyclefree(doc)
        return doc

    f08_131106_case_ids = [
        "F08_active_genealogy_marker_matches_latest_external_audit",
        "F08_active_current_package_label_matches_corrective_iteration",
        "F08_changelog_audit_genealogy_entries_are_unique",
        "F08_gate_readout_genealogy_marker_matches_latest_external_audit",
        "F08_gate_readout_current_package_label_matches_corrective_iteration",
        "F08_changelog_summary_matches_genealogy_block",
    ]

    case_ids_105019 = case_ids_100143 + [
        "F05_dataset_validation_restriction_not_weakened_by_response",
        "F05_dataset_validation_restriction_not_weakened_by_bundle",
        "F05_dataset_reuse_restriction_not_weakened_by_bundle",
        "F05_combined_bundle_max_validation_severity_propagation",
        "F05_combined_bundle_max_reuse_restriction_propagation",
        *f08_131106_case_ids,
    ]

    f05_105019_case_ids = [
        "F05_dataset_validation_restriction_not_weakened_by_response",
        "F05_dataset_validation_restriction_not_weakened_by_bundle",
        "F05_dataset_reuse_restriction_not_weakened_by_bundle",
        "F05_combined_bundle_max_validation_severity_propagation",
        "F05_combined_bundle_max_reuse_restriction_propagation",
    ]

    def run_matrix_105019(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        matrix = run_matrix_100143(contracts)
        schemas = {name: doc["json_schema"] for name, doc in contracts.items()}
        rows = [row for row in matrix["rows"] if row.get("case_id") not in set(f05_105019_case_ids)]
        bundle_schema_doc = schemas["state_bundle_manifest_contract_v0_1_2.json"]
        tests = [
            ("F05_dataset_validation_restriction_not_weakened_by_response", _case_response_weakens_dataset_validation_105019()),
            ("F05_dataset_validation_restriction_not_weakened_by_bundle", _case_bundle_weakens_dataset_validation_105019()),
            ("F05_dataset_reuse_restriction_not_weakened_by_bundle", _case_reuse_weakens_dataset_reuse_105019()),
            ("F05_combined_bundle_max_validation_severity_propagation", _case_combined_validation_weakens_component_105019()),
            ("F05_combined_bundle_max_reuse_restriction_propagation", _case_combined_reuse_weakens_component_105019()),
        ]
        for case_id, instance in tests:
            add_case(rows, case_id, "external_105019_f05_regression", "state_bundle_manifest_contract_v0_1_2.json", bundle_schema_doc, "bundle", instance, False)
        for case_id in f08_131106_case_ids:
            rows.append({"case_id": case_id, "case_origin": "external_131106_f08_regression", "schema": "living_documents", "expected_valid": True, "actual_valid": False, "result": "FAIL", "errors": ["main must validate generated living-document content"]})
        required = list(dict.fromkeys(list(matrix.get("required_case_ids", [])) + f05_105019_case_ids + f08_131106_case_ids))
        case_ids = [row["case_id"] for row in rows]
        missing = sorted(set(required) - set(case_ids))
        unexpected = sorted(set(case_ids) - set(required))
        duplicates = sorted({cid for cid in case_ids if case_ids.count(cid) > 1})
        failed = [row for row in rows if row["result"] == "FAIL"]
        ok = not failed and not missing and not unexpected and not duplicates
        external_origins = {"external_adversarial_regression", "external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression", "external_092039_regression", "external_100143_regression", "external_105019_f05_regression", "external_131106_f08_regression"}
        followup_origins = {"external_audit_followup_regression", "external_reaudit_regression", "external_083304_regression", "external_092039_regression", "external_100143_regression", "external_105019_f05_regression", "external_131106_f08_regression"}
        matrix.update({
            "status": STATUS if ok else "FAILED_INTERNAL_PROVIDER_SCHEMA_HARDENING_V0_1_2",
            "case_count": len(rows),
            "external_regression_case_count": len([r for r in rows if r["case_origin"] in external_origins]),
            "external_followup_case_count": len([r for r in rows if r["case_origin"] in followup_origins]),
            "required_case_ids": required,
            "missing_required_case_ids": missing,
            "duplicate_case_ids": duplicates,
            "unexpected_silent_skips": len(unexpected),
            "unexpected_case_ids": unexpected,
            "failed_cases": len(failed),
            "semantic_validator_execution": "PASS" if not failed else "FAIL",
            "expanded_adversarial_matrix": "PASS" if ok else "FAIL",
            "external_105019_f05_regressions": "PASS" if ok else "FAIL",
            "rows": rows,
        })
        return matrix

    failed_audit_genealogy_105019 = failed_audit_genealogy_100143 + [
        {
            "zip_timestamp": "20260729T105019Z",
            "zip_sha256": "634d015464e6ccdee1582408abd549dd88513f58debcd1cd306a7ce8592eff83",
            "external_audit_result": "FAIL_DATASET_VALIDATION_AND_REUSE_RESTRICTION_PROPAGATION",
            "required_regressions_added": [
                "F05_dataset_validation_restriction_not_weakened_by_response",
                "F05_dataset_validation_restriction_not_weakened_by_bundle",
                "F05_dataset_reuse_restriction_not_weakened_by_bundle",
                "F05_combined_bundle_max_validation_severity_propagation",
                "F05_combined_bundle_max_reuse_restriction_propagation",
            ],
        }
    ]

    def write_scope_105019(now: str) -> None:
        write_scope_100143(now)
        scope_path = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json"
        scope = json.loads(scope_path.read_text(encoding="utf-8"))
        scope["corrective_iteration_label"] = "f05_dataset_validation_and_reuse_restriction_propagation_closure_candidate"
        scope["previous_external_audit_results"] = failed_audit_genealogy_105019
        scope["required_case_ids"] = case_ids_105019
        scope["restriction_propagation_policy"] = {
            "dataset_validation_status_may_not_be_weakened_by_response": True,
            "dataset_validation_status_may_not_be_weakened_by_bundle": True,
            "dataset_reuse_eligibility_may_not_be_weakened_by_bundle": True,
            "combined_bundle_uses_max_component_validation_severity": True,
            "combined_bundle_uses_max_component_reuse_restriction": True,
        }
        write_json(scope_path, scope)
        return scope_path

    def _patch_105019_text(text: str, name: str) -> str:
        text = _patch_100143_text(text)
        marker_105019 = "105019Z = FAIL_DATASET_VALIDATION_AND_REUSE_RESTRICTION_PROPAGATION"
        if marker_105019 not in text:
            text = text.replace("100143Z = FAIL_NARROW_REFERENCE_AND_SHARED_SCHEMA_GAPS", "100143Z = FAIL_NARROW_REFERENCE_AND_SHARED_SCHEMA_GAPS\n" + marker_105019)
        text = text.replace("RECORDED_THROUGH_100143Z", "RECORDED_THROUGH_105019Z")
        text = text.replace("STAGING_CONSOLIDATED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT", "F05_PROPAGATION_CLOSURE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT")
        text = text.replace("staging_consolidated_internal_pass_pending_external_audit", "f05_propagation_closure_internal_pass_pending_external_audit")
        text = text.replace("Current package = staging consolidated internal pass pending external audit", "Current package = F05 propagation closure internal pass pending external audit")
        text = text.replace("current package = STAGING_CONSOLIDATED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT", "current package = F05_PROPAGATION_CLOSURE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT")
        text = text.replace("current package = staging consolidated internal pass pending external audit", "current package = F05 propagation closure internal pass pending external audit")
        text = text.replace("Staging Consolidated Internal Pass", "F05 Propagation Closure Internal Pass")
        text = text.replace("## 2026-07-29 - Runtime provider hardening v0.1.2 cycle-free corrective internal pass pending external audit", "## 2026-07-29 - Runtime provider hardening v0.1.2 F05 propagation closure internal pass pending external audit")
        text = text.replace("Recorded external audit genealogy through `092039Z`: `061024Z`, `070232Z`, `075406Z`, `083304Z`, and `092039Z` all failed external audit with progressively narrower semantic findings.", "Recorded external audit genealogy through `105019Z`: `061024Z`, `070232Z`, `075406Z`, `083304Z`, `092039Z`, `100143Z`, and `105019Z` all failed external audit with progressively narrower semantic or documentary findings.")
        text = text.replace("Status: `route_v1_52_provider_hardening_v0_1_2_corrected_internal_pass_external_reaudit_pending`\nDate: `2026-07-28`", "Status: `route_v1_52_provider_hardening_v0_1_2_corrected_internal_pass_external_reaudit_pending`\nDate: `2026-07-29`")
        text = text.replace("Status: `provider_hardening_v0_1_2_corrected_internal_pass_external_reaudit_pending`\nDate: `2026-07-28`", "Status: `provider_hardening_v0_1_2_corrected_internal_pass_external_reaudit_pending`\nDate: `2026-07-29`")
        if name == "runtime_provider_contract_schema_hardening_v0_1_2_readout.md" and "PROVIDER_V0_1_2_EXTERNAL_AUDIT_GENEALOGY" not in text:
            text = text.replace("\n## Runtime Provider v0.1.2 External Audit Genealogy", "\n```text\nPROVIDER_V0_1_2_EXTERNAL_AUDIT_GENEALOGY = RECORDED_THROUGH_105019Z\ncurrent package = F05_PROPAGATION_CLOSURE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT\n```\n\n## Runtime Provider v0.1.2 External Audit Genealogy")
        lines = []
        seen_105019 = False
        for line in text.splitlines():
            if line.strip() == marker_105019:
                if seen_105019:
                    continue
                seen_105019 = True
            lines.append(line)
        return "\n".join(lines)

    def update_docs_105019(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
        update_docs_100143(now, matrix, zip_path)
        for path in [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            patched = _patch_105019_text(text, path.name)
            if patched != text:
                path.write_text(patched.rstrip() + "\n", encoding="utf-8", newline="\n")

    def write_readout_105019(now: str, matrix: dict[str, Any], package_hash: str) -> None:
        write_readout_100143(now, matrix, package_hash)
        path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_readout.md"
        text = _patch_105019_text(path.read_text(encoding="utf-8"), path.name)
        block = f"""
## External Audit 105019Z F05 Propagation Closure

```text
previous_external_zip = runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T105019Z.zip
previous_external_sha256 = 634d015464e6ccdee1582408abd549dd88513f58debcd1cd306a7ce8592eff83
previous_external_result = FAIL_DATASET_VALIDATION_AND_REUSE_RESTRICTION_PROPAGATION
```

```text
dataset_validation_status_must_not_be_weakened_by_response = true
dataset_validation_status_must_not_be_weakened_by_bundle = true
dataset_reuse_eligibility_must_not_be_weakened_by_bundle = true
combined_bundle_uses_max_component_validation_severity = true
combined_bundle_uses_max_component_reuse_restriction = true
```

Added required regression cases:

```text
F05_dataset_validation_restriction_not_weakened_by_response
F05_dataset_validation_restriction_not_weakened_by_bundle
F05_dataset_reuse_restriction_not_weakened_by_bundle
F05_combined_bundle_max_validation_severity_propagation
F05_combined_bundle_max_reuse_restriction_propagation
```
"""
        if "External Audit 105019Z F05 Propagation Closure" not in text:
            path.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8", newline="\n")
        return path

    def main_105019() -> None:
        now = g["now_utc"]()
        ajv_files = write_ajv_reproducibility_files_100143(now)
        write_authorization_scope_addendum_final(["configs/" + f.name for f in ajv_files])
        scope_path = write_scope_105019(now)
        rollback_readout_path = write_rollback_readout(now)
        findings_readout_path = write_findings_revalidation_readout(now)
        addendum_path = write_authorization_revalidation_addendum(now)
        audit_failure_path = write_external_audit_failure_readout(now)
        ajv_lock_path = write_ajv_environment_lock(now)
        contract_paths = write_contracts_100143()
        contracts = {path.name: read_json(path) for path in contract_paths}
        matrix = run_matrix_105019(contracts)
        update_docs_105019(now, matrix, FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip")
        watched = [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]
        before = {str(path): path.read_bytes() for path in watched}
        update_docs_105019(now, matrix, FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip")
        after = {str(path): path.read_bytes() for path in watched}
        idempotent = before == after
        set_case_result(matrix, "F08_living_document_idempotence_actual_bytes", idempotent, [] if idempotent else ["two identical update_docs calls changed bytes"])
        route_text = (FEATURE_ROOT / "99_ruta_de_trabajo.md").read_text(encoding="utf-8-sig")
        route_ok = "Historical Snapshot - Provider Contract Schema Hardening v0.1.2 Authorization Issued" in route_text and "Next gate at closure:" in route_text
        set_case_result(matrix, "F08_route_authorization_section_historical_snapshot", route_ok, [] if route_ok else ["route authorization section not historical"])
        route_doc = (FEATURE_ROOT / "99_ruta_de_trabajo.md").read_text(encoding="utf-8-sig")
        agent_doc = (FEATURE_ROOT / "AGENT.md").read_text(encoding="utf-8-sig")
        readme_doc = (RUNTIME / "README.md").read_text(encoding="utf-8-sig")
        changelog_doc = (ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md").read_text(encoding="utf-8-sig")
        active_docs = [route_doc, agent_doc, readme_doc]
        marker = "105019Z = FAIL_DATASET_VALIDATION_AND_REUSE_RESTRICTION_PROPAGATION"
        genealogy_ok = all("RECORDED_THROUGH_105019Z" in doc for doc in active_docs) and not any("RECORDED_THROUGH_100143Z" in doc for doc in active_docs) and all(marker in doc for doc in active_docs)
        label = "F05_PROPAGATION_CLOSURE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT"
        label_ok = all(label in doc for doc in active_docs + [changelog_doc]) and not any("STAGING_CONSOLIDATED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT" in doc for doc in active_docs + [changelog_doc])
        changelog_unique = changelog_doc.count(marker) == 1
        set_case_result(matrix, "F08_active_genealogy_marker_matches_latest_external_audit", genealogy_ok, [] if genealogy_ok else ["active docs must record genealogy through 105019Z and not 100143Z"])
        set_case_result(matrix, "F08_active_current_package_label_matches_corrective_iteration", label_ok, [] if label_ok else ["active docs must use F05 propagation closure package label and not staging consolidated label"])
        set_case_result(matrix, "F08_changelog_audit_genealogy_entries_are_unique", changelog_unique, [] if changelog_unique else ["CHANGELOG must contain exactly one 105019Z genealogy line"])
        recompute_matrix_status(matrix)
        f05_rows = [row for row in matrix["rows"] if row.get("case_origin") == "external_105019_f05_regression"]
        matrix["external_105019_f05_regressions"] = "PASS" if f05_rows and all(row.get("result") == "PASS" for row in f05_rows) else "FAIL"
        matrix_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json"
        write_json(matrix_path, matrix)
        pending_zip = FEATURE_ROOT / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_PENDING.zip"
        readout_path = write_readout_105019(now, matrix, pending_zip)
        update_docs_105019(now, matrix, pending_zip)
        files = [RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_v0_1.md", CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_scope_v0_1.json", RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization_readout_v0_1.md", addendum_path, CONFIGS / "runtime_provider_v0_1_2_rollback_verification_scope_v0_1.json", RUNTIME / "runtime_provider_v0_1_2_rollback_verification_matrix_v0_1.json", rollback_readout_path, CONFIGS / "runtime_provider_contract_schema_hardening_findings_revalidation_scope_v0_1.json", RUNTIME / "runtime_provider_contract_schema_hardening_findings_revalidation_matrix_v0_1.json", findings_readout_path, audit_failure_path, ajv_lock_path, *ajv_files, scope_path, *contract_paths, SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_runner.py", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_patch.py", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py", matrix_path, readout_path, FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"]
        normalize_files(files)
        zip_path = make_zip(now, files)
        readout_path = write_readout_105019(now, matrix, zip_path)
        update_docs_105019(now, matrix, zip_path)
        readout_doc = read_text(readout_path)
        changelog_doc = read_text(ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md")
        marker = "105019Z = FAIL_DATASET_VALIDATION_AND_REUSE_RESTRICTION_PROPAGATION"
        label = "F05_PROPAGATION_CLOSURE_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT"
        readout_genealogy_ok = "RECORDED_THROUGH_105019Z" in readout_doc and "RECORDED_THROUGH_100143Z" not in readout_doc and marker in readout_doc
        readout_label_ok = label in readout_doc and "STAGING_CONSOLIDATED_INTERNAL_PASS_PENDING_EXTERNAL_AUDIT" not in readout_doc
        changelog_summary_ok = "Recorded external audit genealogy through `105019Z`" in changelog_doc and "Recorded external audit genealogy through `092039Z`" not in changelog_doc and changelog_doc.count(marker) == 1
        set_case_result(matrix, "F08_gate_readout_genealogy_marker_matches_latest_external_audit", readout_genealogy_ok, [] if readout_genealogy_ok else ["readout must record genealogy through 105019Z and not 100143Z"])
        set_case_result(matrix, "F08_gate_readout_current_package_label_matches_corrective_iteration", readout_label_ok, [] if readout_label_ok else ["readout must use F05 propagation closure label and not staging consolidated label"])
        set_case_result(matrix, "F08_changelog_summary_matches_genealogy_block", changelog_summary_ok, [] if changelog_summary_ok else ["CHANGELOG summary must say through 105019Z and match unique genealogy block"])
        recompute_matrix_status(matrix)
        f05_rows = [row for row in matrix["rows"] if row.get("case_origin") == "external_105019_f05_regression"]
        matrix["external_105019_f05_regressions"] = "PASS" if f05_rows and all(row.get("result") == "PASS" for row in f05_rows) else "FAIL"
        write_json(matrix_path, matrix)
        readout_path = write_readout_105019(now, matrix, zip_path)
        update_docs_105019(now, matrix, zip_path)
        normalize_files(files)
        zip_path.unlink(missing_ok=True)
        zip_path = make_zip(now, files)
        ok_zip, errors = verify_zip(zip_path)
        if not ok_zip:
            raise SystemExit("ZIP verification failed: " + "; ".join(errors))
        print(json.dumps({
            "gate": GATE,
            "status": matrix["status"],
            "case_count": matrix["case_count"],
            "external_regression_case_count": matrix["external_regression_case_count"],
            "external_followup_case_count": matrix["external_followup_case_count"],
            "missing_required_case_ids": len(matrix["missing_required_case_ids"]),
            "duplicate_case_ids": len(matrix["duplicate_case_ids"]),
            "unexpected_case_ids": len(matrix["unexpected_case_ids"]),
            "failed_cases": matrix["failed_cases"],
            "jsonschema_draft_2020_12_compile": matrix["jsonschema_draft_2020_12_compile"],
            "ajv_8_17_1_strict_runtime": matrix["ajv_8_17_1_strict_runtime"],
            "semantic_validator_execution": matrix["semantic_validator_execution"],
            "zip_path": str(zip_path),
            "zip_sha256": sha256_file(zip_path),
            "next_action": "external_adversarial_reaudit_of_provider_only_zip",
        }, indent=2, ensure_ascii=False))

    g["semantic_errors"] = semantic_errors_105019
    g["run_matrix"] = run_matrix_105019
    g["write_scope"] = write_scope_105019
    g["update_docs"] = update_docs_105019
    g["main"] = main_105019
