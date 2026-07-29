from __future__ import annotations

import copy
import hashlib
import importlib.util
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
BASE_RUNNER = SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_1_runner.py"

GATE = "runtime_provider_contract_schema_hardening_v0_1_2"
STATUS = "CLOSED_PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_2_WITH_RESTRICTIONS_NO_EXECUTION"
PREV_GATE = "runtime_provider_contract_schema_hardening_v0_1_1"
PREV_STATUS = "CLOSED_PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_1_WITH_RESTRICTIONS_NO_EXECUTION"
PREV_AUDIT = "FAIL_EXECUTABLE_SEMANTIC_GAPS"
MIN_CASES = 44

MARKET = "market_state"
EVENT = "event_state"
MARKET_CAP = "market_state_on_demand_runtime_capability_v0_1"
EVENT_CAP = "event_state_on_demand_runtime_capability_v0_1"
MARKET_PROFILE = "market_state_core_four_intraday_profile_v0_1"
EVENT_PROFILE = "event_state_core_four_intraday_profile_v0_1"
SESSION_OPENED = "event_type:market_data:session_opened"

FILES = {
    "request": "state_resolution_request_contract_v0_1_2.json",
    "interface": "runtime_user_invocation_interface_contract_v0_1_2.json",
    "response": "runtime_user_invocation_response_contract_v0_1_2.json",
    "bundle": "state_bundle_manifest_contract_v0_1_2.json",
    "view": "runtime_capability_effective_view_contract_v0_1_2.json",
}

RULES = [
    "bundle cardinality binds state kinds, request fingerprints, request refs and response refs",
    "ref_id uniqueness is semantic per reference array",
    "request_type binds capability_id, profile_id and detail branch",
    "effective capability view contains exactly one market capability and one event capability",
    "FAIL or BLOCKED manifests cannot certify reusable datasets",
    "operation governs resolution mode and execution authorization semantics",
    "invocation_status governs required and prohibited fields",
    "superseded compatibility snapshots remain historical and do not authorize consumption",
]


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("base_v011", BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {BASE_RUNNER}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = load_base()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def entry(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def rep(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: rep(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rep(v) for v in value]
    if isinstance(value, str):
        return (
            value.replace("0.1.1", "0.1.2")
            .replace("v0_1_1", "v0_1_2")
            .replace("V0_1_1", "V0_1_2")
            .replace(PREV_GATE, GATE)
            .replace("PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_1", "PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_2")
        )
    return value


def cap(kind: str) -> str:
    return MARKET_CAP if kind == MARKET else EVENT_CAP


def profile(kind: str) -> str:
    return MARKET_PROFILE if kind == MARKET else EVENT_PROFILE


def doc(contract_id: str, schema: dict[str, Any], purpose: str) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "contract_version": "0.1.2",
        "status": "PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_2_NO_EXECUTION",
        "owner_layer": "08_RUNTIME_CAPABILITIES",
        "schema_hardening_gate": GATE,
        "previous_internal_gate": PREV_GATE,
        "previous_internal_status": PREV_STATUS,
        "previous_external_audit_status": PREV_AUDIT,
        "purpose": purpose,
        "contract_hash_policy": {
            "hash_authority": "PACKAGE_MANIFEST.full_file_sha256",
            "embedded_contract_hash": "not_used_in_v0_1_2",
        },
        "semantic_validator_required": True,
        "semantic_rules": RULES,
        "json_schema": rep(schema),
    }


def write_contracts() -> list[Path]:
    payloads = {
        FILES["request"]: doc("state_resolution_request_contract_v0_1_2", base.state_resolution_schema(), "Executable provider envelope for state resolution requests."),
        FILES["interface"]: doc("runtime_user_invocation_interface_contract_v0_1_2", base.interface_schema(), "Executable interface envelope for validate/resolve/invoke operations."),
        FILES["response"]: doc("runtime_user_invocation_response_contract_v0_1_2", base.response_schema(), "Executable provider response envelope."),
        FILES["bundle"]: doc("state_bundle_manifest_contract_v0_1_2", base.bundle_schema(), "Executable governed StateBundleManifest reference."),
        FILES["view"]: doc("runtime_capability_effective_view_contract_v0_1_2", base.effective_view_schema(), "Executable effective capability view."),
    }
    paths = []
    for name, payload in payloads.items():
        path = RUNTIME / name
        write_json(path, payload)
        paths.append(path)
    return paths


def valid_request(kind: str) -> dict[str, Any]:
    d = base.valid_state_request(kind)
    d["request_contract_version"] = "0.1.2"
    d["consumer"] = "hardening_v0_1_2"
    return d


def auth_ref() -> dict[str, Any]:
    return {"ref_id": "auth_001", "ref_type": "execution_authorization", "sha256": h("auth"), "availability": "available"}


def valid_interface(operation: str) -> dict[str, Any]:
    req = valid_request(MARKET)
    auth = None
    if operation == "validate":
        req["resolution_policy"].update({"mode": "validate_only", "reuse_policy": "metadata_only", "requested_output_mode": "metadata_only"})
    elif operation == "resolve":
        req["resolution_policy"].update({"mode": "resolve_reuse_or_authorization", "reuse_policy": "reuse_if_exact_validated_match", "requested_output_mode": "candidate_reference_only"})
    elif operation == "invoke":
        req["resolution_policy"].update({"mode": "invoke_with_authorization", "reuse_policy": "reuse_if_exact_validated_match_or_authorization_required", "requested_output_mode": "candidate_reference_only"})
        auth = auth_ref()
    else:
        raise ValueError(operation)
    return {"operation": operation, "state_resolution_request": req, "execution_authorization_ref": auth}


def valid_response(kind: str = MARKET, status: str = "reuse_hit") -> dict[str, Any]:
    d = base.valid_response(kind)
    details = {"materializer_executions": 0, "source_market_data_rows_read": 0, "registry_mutations": 0, "physical_rows_delivered": 0}
    d["capability_id"] = cap(kind)
    d["profile_id"] = profile(kind)
    d["market_state_details"] = details if kind == MARKET else None
    d["event_state_details"] = details if kind == EVENT else None
    if status == "reuse_hit":
        d.update({"invocation_status": "reuse_hit", "resolution_decision": "VALID_REQUEST_REUSE_HIT", "dataset_id": "dataset_001", "dataset_status": "validated_candidate", "validation_status": "PASS_WITH_RESTRICTIONS", "state_bundle_manifest_ref": {"ref_id": "bundle_001", "ref_type": "state_bundle_manifest", "sha256": h("bundle"), "availability": "available"}, "artifact_references": [{"ref_id": "artifact_001", "ref_type": "runtime_artifact", "sha256": h("artifact"), "availability": "available"}], "authorization_ref": None})
    elif status == "blocked":
        d.update({"invocation_status": "blocked", "resolution_decision": "BLOCKED_INVALID_REQUEST", "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "artifact_references": [], "authorization_ref": None})
    elif status == "authorization_required":
        d.update({"invocation_status": "authorization_required", "resolution_decision": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED", "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "artifact_references": [], "authorization_ref": None})
    elif status == "authorized_reference":
        d.update({"invocation_status": "authorized_reference", "resolution_decision": "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE", "dataset_id": None, "dataset_status": None, "validation_status": None, "state_bundle_manifest_ref": None, "artifact_references": [], "authorization_ref": auth_ref()})
    return d


def ds(kind: str, validation_status: str = "PASS_WITH_RESTRICTIONS") -> dict[str, Any]:
    return {"dataset_id": f"{kind}_dataset_001", "dataset_kind": kind, "candidate_dataset_fingerprint": h(f"{kind}_dataset"), "validation_status": validation_status, "reuse_eligibility": "eligible_with_restrictions", "artifact_availability": "available"}


def valid_bundle(mode: str = "market_state_only") -> dict[str, Any]:
    kinds = { "market_state_only": [MARKET], "event_state_only": [EVENT], "market_and_event": [MARKET, EVENT] }[mode]
    return {
        "state_bundle_manifest_id": "bundle_001",
        "bundle_state_mode": mode,
        "state_kinds": kinds,
        "request_fingerprints": [h(f"{k}_request") for k in kinds],
        "state_resolution_request_refs": [{"ref_id": f"{k}_request_ref_001", "ref_type": "state_resolution_request", "sha256": h(f"{k}_request"), "availability": "available"} for k in kinds],
        "runtime_invocation_response_refs": [{"ref_id": f"{k}_response_ref_001", "ref_type": "runtime_invocation_response", "sha256": h(f"{k}_response"), "availability": "available"} for k in kinds],
        "capability_refs": [{"ref_id": cap(k), "ref_type": "runtime_capability", "sha256": h(cap(k)), "availability": "available"} for k in kinds],
        "dataset_refs": {"market_state_dataset_ref": ds(MARKET) if MARKET in kinds else None, "event_state_dataset_ref": ds(EVENT) if EVENT in kinds else None},
        "coverage": {"requested_contexts": 10, "represented_contexts": 8, "unavailable_contexts": 2, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0},
        "validation_status": "PASS_WITH_RESTRICTIONS",
        "restrictions": ["candidate_runtime_only"],
        "representation_profile_versions": [{"state_kind": k, "profile_id": profile(k), "profile_version": "v0_1", "profile_fingerprint": h(f"{k}_profile")} for k in kinds],
        "schema_fingerprints": [h("schema")],
        "source_dataset_ids": ["source_001"],
        "source_content_hashes": [h("source")],
        "artifact_hashes": [{"artifact_id": "artifact_001", "artifact_type": "manifest", "sha256": h("artifact"), "availability": "available"}],
        "field_lineage": [{"field_id": "field_001", "builder_id": "builder_001", "input_refs": ["input_001"]}],
        "temporal_policy": {"point_in_time_policy_id": "pit:v0_1", "available_at_policy_id": "available_at:v0_1", "future_information_exclusion": True},
        "materialization_status": "reference_only",
        "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []},
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "physical_rows_delivered": False,
    }


def valid_view() -> dict[str, Any]:
    return {
        "view_id": "effective_view_001",
        "view_version": "0.1.2",
        "capabilities": [
            {"capability_id": MARKET_CAP, "request_type": MARKET, "capability_status": "available_with_restrictions", "supported_profile_ids": [MARKET_PROFILE], "supported_event_type_ids": [], "candidate_generation_authority": True, "reuse_authority": True, "official_dataset": False, "production": False, "downstream": False, "backtest_consumption": False},
            {"capability_id": EVENT_CAP, "request_type": EVENT, "capability_status": "available_with_restrictions", "supported_profile_ids": [EVENT_PROFILE], "supported_event_type_ids": [SESSION_OPENED], "candidate_generation_authority": True, "reuse_authority": True, "official_dataset": False, "production": False, "downstream": False, "backtest_consumption": False},
        ],
    }


def dupes(values: list[Any]) -> list[Any]:
    seen, out = set(), []
    for v in values:
        if v in seen and v not in out:
            out.append(v)
        seen.add(v)
    return out


def coverage_ok(c: dict[str, Any]) -> bool:
    return c.get("requested_contexts") == sum(c.get(k, 0) for k in ["represented_contexts", "unavailable_contexts", "blocked_contexts", "quarantined_contexts", "unaccounted_contexts"])


def sem_bundle(d: dict[str, Any]) -> list[str]:
    e = []
    expected = {"market_state_only": [MARKET], "event_state_only": [EVENT], "market_and_event": [MARKET, EVENT]}.get(d.get("bundle_state_mode"), [])
    if sorted(d.get("state_kinds", [])) != sorted(expected):
        e.append("SEM_BUNDLE_STATE_KIND_MODE_MISMATCH")
    n = len(expected)
    for f in ["request_fingerprints", "state_resolution_request_refs", "runtime_invocation_response_refs", "capability_refs"]:
        if len(d.get(f, [])) != n:
            e.append(f"SEM_BUNDLE_CARDINALITY_{f.upper()}")
    for f in ["state_resolution_request_refs", "runtime_invocation_response_refs"]:
        ids = [x.get("ref_id") for x in d.get(f, []) if isinstance(x, dict)]
        if dupes(ids):
            e.append(f"SEM_DUPLICATE_REF_ID_{f.upper()}")
    if set(d.get("request_fingerprints", [])) != {x.get("sha256") for x in d.get("state_resolution_request_refs", []) if isinstance(x, dict)}:
        e.append("SEM_REQUEST_FINGERPRINT_REF_HASH_MISMATCH")
    if {x.get("ref_id") for x in d.get("capability_refs", []) if isinstance(x, dict)} != {cap(k) for k in expected}:
        e.append("SEM_BUNDLE_CAPABILITY_KIND_MISMATCH")
    profiles = {(x.get("state_kind"), x.get("profile_id")) for x in d.get("representation_profile_versions", []) if isinstance(x, dict)}
    if profiles != {(k, profile(k)) for k in expected}:
        e.append("SEM_BUNDLE_PROFILE_KIND_MISMATCH")
    datasets = [v for v in d.get("dataset_refs", {}).values() if isinstance(v, dict)]
    if d.get("validation_status") in {"FAIL", "BLOCKED"} and datasets:
        e.append("SEM_BUNDLE_FAIL_OR_BLOCKED_WITH_REUSABLE_DATASET")
    if isinstance(d.get("coverage"), dict) and not coverage_ok(d["coverage"]):
        e.append("SEM_COVERAGE_ARITHMETIC")
    return e


def sem_response(d: dict[str, Any]) -> list[str]:
    e, kind = [], d.get("request_type")
    if kind in {MARKET, EVENT}:
        if d.get("capability_id") != cap(kind):
            e.append("SEM_RESPONSE_CAPABILITY_REQUEST_TYPE_MISMATCH")
        if d.get("profile_id") != profile(kind):
            e.append("SEM_RESPONSE_PROFILE_REQUEST_TYPE_MISMATCH")
        if d.get("market_state_details" if kind == MARKET else "event_state_details") is None:
            e.append("SEM_RESPONSE_EXPECTED_DETAILS_MISSING")
        if d.get("event_state_details" if kind == MARKET else "market_state_details") is not None:
            e.append("SEM_RESPONSE_OPPOSITE_DETAILS_PRESENT")
    status = d.get("invocation_status")
    artifacts, auth, bundle = d.get("artifact_references", []), d.get("authorization_ref"), d.get("state_bundle_manifest_ref")
    has_dataset = d.get("dataset_id") is not None or d.get("dataset_status") is not None or d.get("validation_status") is not None
    if status == "reuse_hit" and (auth is not None or bundle is None or not artifacts):
        e.append("SEM_REUSE_HIT_FIELD_INCOMPATIBILITY")
    if status == "blocked" and (has_dataset or bundle is not None or auth is not None or artifacts):
        e.append("SEM_BLOCKED_WITH_AVAILABLE_OUTPUTS")
    if status == "authorization_required" and (has_dataset or bundle is not None or auth is not None or artifacts):
        e.append("SEM_AUTHORIZATION_REQUIRED_WITH_OUTPUTS")
    if status == "authorized_reference" and (has_dataset or bundle is not None or auth is None or artifacts):
        e.append("SEM_AUTHORIZED_REFERENCE_FIELD_INCOMPATIBILITY")
    if isinstance(d.get("coverage"), dict) and not coverage_ok(d["coverage"]):
        e.append("SEM_COVERAGE_ARITHMETIC")
    return e


def sem_view(d: dict[str, Any]) -> list[str]:
    e, caps = [], d.get("capabilities", [])
    by_type = {MARKET: [], EVENT: []}
    for c in caps:
        if isinstance(c, dict) and c.get("request_type") in by_type:
            by_type[c["request_type"]].append(c)
    if len(by_type[MARKET]) != 1 or len(by_type[EVENT]) != 1:
        e.append("SEM_EFFECTIVE_VIEW_REQUIRES_ONE_MARKET_AND_ONE_EVENT_CAPABILITY")
    for kind in [MARKET, EVENT]:
        for c in by_type.get(kind, []):
            if c.get("capability_id") != cap(kind):
                e.append("SEM_EFFECTIVE_VIEW_CAPABILITY_REQUEST_TYPE_MISMATCH")
            if c.get("supported_profile_ids") != [profile(kind)]:
                e.append("SEM_EFFECTIVE_VIEW_PROFILE_MISMATCH")
            if c.get("supported_event_type_ids") != ([] if kind == MARKET else [SESSION_OPENED]):
                e.append("SEM_EFFECTIVE_VIEW_EVENT_TYPE_SCOPE_MISMATCH")
    return e


def sem_interface(d: dict[str, Any]) -> list[str]:
    e, op = [], d.get("operation")
    mode = d.get("state_resolution_request", {}).get("resolution_policy", {}).get("mode")
    auth = d.get("execution_authorization_ref")
    expected = {"validate": ("validate_only", None), "resolve": ("resolve_reuse_or_authorization", None), "invoke": ("invoke_with_authorization", "available")}.get(op)
    if expected and mode != expected[0]:
        e.append("SEM_INTERFACE_OPERATION_MODE_MISMATCH")
    if expected and expected[1] is None and auth is not None:
        e.append("SEM_INTERFACE_AUTHORIZATION_NOT_ALLOWED_FOR_OPERATION")
    if expected and expected[1] == "available" and (not isinstance(auth, dict) or auth.get("availability") != "available"):
        e.append("SEM_INTERFACE_AUTHORIZATION_REQUIRED_FOR_INVOKE")
    return e


def semantic_errors(name: str, d: dict[str, Any]) -> list[str]:
    if name == FILES["bundle"]:
        return sem_bundle(d)
    if name == FILES["response"]:
        return sem_response(d)
    if name == FILES["view"]:
        return sem_view(d)
    if name == FILES["interface"]:
        return sem_interface(d)
    return []


def validate_doc(name: str, schema: dict[str, Any], d: dict[str, Any]) -> list[str]:
    errors = [x.message for x in Draft202012Validator(schema).iter_errors(d)]
    errors.extend(base.forbidden_scan(d))
    errors.extend(semantic_errors(name, d))
    return errors


def ajv_env() -> dict[str, str]:
    env = dict(os.environ)
    local = Path(r"C:\tmp\tsis_ajv_runtime\node_modules")
    if local.exists():
        env["NODE_PATH"] = str(local) + (os.pathsep + env["NODE_PATH"] if env.get("NODE_PATH") else "")
    return env


def run_ajv(schemas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    js = """
const fs=require('fs');
let Ajv2020, version;
try { Ajv2020=require('ajv/dist/2020'); version=require('ajv/package.json').version; }
catch(e){ console.log(JSON.stringify({available:false, version:null, error:String(e.message||e), rows:[]})); process.exit(0); }
const schemas=JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const rows=[];
for (const [name,schema] of Object.entries(schemas)) {
  try { const ajv=new Ajv2020({strict:true, allErrors:true}); ajv.addFormat('date', true); ajv.addFormat('date-time', true); ajv.compile(schema); rows.push({schema:name,result:'PASS',errors:[]}); }
  catch(e){ rows.push({schema:name,result:'FAIL',errors:[String(e.message||e)]}); }
}
console.log(JSON.stringify({available:true, version, error:null, rows}));
"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "schemas.json"
        s = Path(tmp) / "ajv_compile.js"
        p.write_text(json.dumps(schemas), encoding="utf-8")
        s.write_text(js, encoding="utf-8")
        proc = subprocess.run(["node", str(s), str(p)], capture_output=True, text=True, timeout=30, env=ajv_env())
    if proc.returncode != 0:
        return {"available": False, "version": None, "error": proc.stderr.strip() or proc.stdout.strip(), "rows": []}
    try:
        return json.loads(proc.stdout)
    except Exception as exc:
        return {"available": False, "version": None, "error": f"invalid_ajv_output: {exc}", "rows": []}


def add(rows: list[dict[str, Any]], case_id: str, name: str, schema: dict[str, Any], d: dict[str, Any], expected: bool, group: str) -> None:
    errs = validate_doc(name, schema, d)
    actual = not errs
    rows.append({"case_id": case_id, "case_group": group, "schema": name, "expected_valid": expected, "actual_valid": actual, "result": "PASS" if actual == expected else "FAIL", "errors": errs[:8]})


def compile_rows(rows: list[dict[str, Any]], schemas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for name, schema in schemas.items():
        errs = []
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errs = [str(exc)]
        rows.append({"case_id": f"jsonschema_compile_{name}", "case_group": "original_internal_schema_compile", "schema": name, "expected_valid": True, "actual_valid": not errs, "result": "PASS" if not errs else "FAIL", "errors": errs[:5]})
        lint = base.strict_lint(schema)
        rows.append({"case_id": f"ajv_strict_static_lint_{name}", "case_group": "original_internal_static_lint", "schema": name, "expected_valid": True, "actual_valid": not lint, "result": "PASS" if not lint else "FAIL", "errors": lint[:5]})
    ajv = run_ajv(schemas)
    for name in schemas:
        found = next((r for r in ajv.get("rows", []) if r.get("schema") == name), None)
        ok = bool(ajv.get("available")) and found is not None and found.get("result") == "PASS"
        rows.append({"case_id": f"ajv_strict_runtime_compile_{name}", "case_group": "ajv_draft_2020_12_strict_runtime", "schema": name, "expected_valid": True, "actual_valid": ok, "result": "PASS" if ok else "FAIL", "errors": [] if ok else ((found or {}).get("errors") or [ajv.get("error") or "AJV runtime unavailable"])})
    return ajv


def original_cases(rows: list[dict[str, Any]], schemas: dict[str, dict[str, Any]]) -> None:
    sr, resp, bundle = FILES["request"], FILES["response"], FILES["bundle"]
    add(rows, "positive_market_state_request", sr, schemas[sr], valid_request(MARKET), True, "original_internal_31")
    add(rows, "positive_event_state_request", sr, schemas[sr], valid_request(EVENT), True, "original_internal_31")
    bad = valid_request(MARKET); bad["payload"] = {"event_state_request": valid_request(EVENT)["payload"]["event_state_request"]}
    add(rows, "negative_request_type_payload_mismatch", sr, schemas[sr], bad, False, "original_internal_31")
    bad = valid_request(MARKET); bad["payload"]["market_state_request"]["physical_path"] = "C:/forbidden.parquet"
    add(rows, "negative_physical_path_payload", sr, schemas[sr], bad, False, "original_internal_31")
    bad = valid_request(EVENT); bad["payload"]["event_state_request"]["event_type_ids"] = ["event_type:regulatory:halt_resumed"]
    add(rows, "negative_unsupported_event_type", sr, schemas[sr], bad, False, "original_internal_31")
    add(rows, "positive_reuse_hit_market_response", resp, schemas[resp], valid_response(MARKET), True, "original_internal_31")
    bad = valid_response(MARKET); bad["state_bundle_manifest_ref"]["availability"] = "missing"
    add(rows, "negative_reuse_hit_missing_bundle", resp, schemas[resp], bad, False, "original_internal_31")
    bad = valid_response(MARKET); bad["event_state_details"] = bad["market_state_details"]
    add(rows, "negative_cross_details", resp, schemas[resp], bad, False, "original_internal_31")
    bad = valid_response(MARKET); bad["invocation_status"] = "blocked"; bad["resolution_decision"] = "BLOCKED_INVALID_REQUEST"
    add(rows, "negative_blocked_with_dataset", resp, schemas[resp], bad, False, "original_internal_31")
    add(rows, "positive_authorized_reference", resp, schemas[resp], valid_response(MARKET, "authorized_reference"), True, "original_internal_31")
    bad = valid_response(MARKET, "authorized_reference"); bad["authorization_ref"] = None
    add(rows, "negative_authorized_reference_missing_auth", resp, schemas[resp], bad, False, "original_internal_31")
    add(rows, "positive_market_bundle", bundle, schemas[bundle], valid_bundle("market_state_only"), True, "original_internal_31")
    add(rows, "positive_event_bundle", bundle, schemas[bundle], valid_bundle("event_state_only"), True, "original_internal_31")
    muts = [
        ("negative_pass_empty_capability_refs", lambda b: b.update({"capability_refs": []})),
        ("negative_coverage_arithmetic", lambda b: b["coverage"].update({"represented_contexts": 11})),
        ("negative_missing_required_request_ref", lambda b: b["state_resolution_request_refs"][0].update({"availability": "missing"})),
        ("negative_empty_source_hashes", lambda b: b.update({"source_content_hashes": []})),
        ("negative_invalid_schema_hash", lambda b: b.update({"schema_fingerprints": ["not_hash"]})),
        ("negative_dataset_kind_mismatch", lambda b: b.update({"bundle_state_mode": "event_state_only"})),
        ("negative_duplicate_fingerprints", lambda b: (b.update({"request_fingerprints": [h("x"), h("x")]}), b.update({"state_resolution_request_refs": [{"ref_id": "a", "ref_type": "state_resolution_request", "sha256": h("x"), "availability": "available"}, {"ref_id": "b", "ref_type": "state_resolution_request", "sha256": h("x"), "availability": "available"}]}))),
        ("negative_request_ref_fingerprint_mismatch", lambda b: b["state_resolution_request_refs"][0].update({"sha256": h("different")})),
    ]
    for cid, mut in muts:
        bad = valid_bundle("market_state_only"); mut(bad)
        add(rows, cid, bundle, schemas[bundle], bad, False, "original_internal_31")


def external_cases(rows: list[dict[str, Any]], schemas: dict[str, dict[str, Any]]) -> None:
    bundle, resp, view, iface = FILES["bundle"], FILES["response"], FILES["view"], FILES["interface"]
    add(rows, "external_positive_market_and_event_bundle", bundle, schemas[bundle], valid_bundle("market_and_event"), True, "external_13_regression")
    bad = valid_bundle("market_and_event"); bad["runtime_invocation_response_refs"] = [bad["runtime_invocation_response_refs"][0]]
    add(rows, "external_negative_aggregated_bundle_missing_response_ref", bundle, schemas[bundle], bad, False, "external_13_regression")
    bad = valid_bundle("market_and_event"); bad["state_resolution_request_refs"][1]["ref_id"] = bad["state_resolution_request_refs"][0]["ref_id"]; bad["state_resolution_request_refs"][1]["sha256"] = h("other")
    add(rows, "external_negative_duplicate_state_request_ref_id", bundle, schemas[bundle], bad, False, "external_13_regression")
    bad = valid_bundle("market_and_event"); bad["runtime_invocation_response_refs"][1]["ref_id"] = bad["runtime_invocation_response_refs"][0]["ref_id"]; bad["runtime_invocation_response_refs"][1]["sha256"] = h("other")
    add(rows, "external_negative_duplicate_runtime_response_ref_id", bundle, schemas[bundle], bad, False, "external_13_regression")
    bad = valid_response(MARKET); bad["capability_id"] = EVENT_CAP
    add(rows, "external_negative_market_response_event_capability", resp, schemas[resp], bad, False, "external_13_regression")
    bad = valid_response(MARKET); bad["profile_id"] = EVENT_PROFILE
    add(rows, "external_negative_market_response_event_profile", resp, schemas[resp], bad, False, "external_13_regression")
    bad = valid_view(); bad["capabilities"][1]["request_type"] = MARKET
    add(rows, "external_negative_effective_view_event_capability_market_type", view, schemas[view], bad, False, "external_13_regression")
    bad = valid_view(); bad["capabilities"][1] = copy.deepcopy(bad["capabilities"][0]); bad["capabilities"][1]["capability_status"] = "promoted_with_restrictions"
    add(rows, "external_negative_effective_view_two_market_semantics", view, schemas[view], bad, False, "external_13_regression")
    bad = valid_bundle("market_state_only"); bad["validation_status"] = "FAIL"
    add(rows, "external_negative_fail_manifest_with_reusable_dataset", bundle, schemas[bundle], bad, False, "external_13_regression")
    bad = valid_interface("invoke"); bad["execution_authorization_ref"] = None
    add(rows, "external_negative_invoke_without_authorization", iface, schemas[iface], bad, False, "external_13_regression")
    bad = valid_interface("validate"); bad["execution_authorization_ref"] = auth_ref()
    add(rows, "external_negative_validate_with_authorization", iface, schemas[iface], bad, False, "external_13_regression")
    bad = valid_response(MARKET); bad["authorization_ref"] = auth_ref()
    add(rows, "external_negative_reuse_hit_with_authorization", resp, schemas[resp], bad, False, "external_13_regression")
    bad = valid_response(MARKET, "authorization_required"); bad["artifact_references"] = [{"ref_id": "artifact_001", "ref_type": "runtime_artifact", "sha256": h("artifact"), "availability": "available"}]
    add(rows, "external_negative_authorization_required_with_artifacts", resp, schemas[resp], bad, False, "external_13_regression")


def additional_cases(rows: list[dict[str, Any]], schemas: dict[str, dict[str, Any]]) -> None:
    bundle, resp, view, iface = FILES["bundle"], FILES["response"], FILES["view"], FILES["interface"]
    bad = valid_bundle("market_state_only"); bad["capability_refs"][0]["ref_id"] = EVENT_CAP
    add(rows, "finding_negative_bundle_wrong_capability_ref", bundle, schemas[bundle], bad, False, "additional_finding_regression")
    bad = valid_bundle("event_state_only"); bad["representation_profile_versions"][0]["profile_id"] = MARKET_PROFILE
    add(rows, "finding_negative_bundle_wrong_profile_record", bundle, schemas[bundle], bad, False, "additional_finding_regression")
    bad = valid_response(EVENT); bad["event_state_details"] = None
    add(rows, "finding_negative_event_response_missing_details", resp, schemas[resp], bad, False, "additional_finding_regression")
    bad = valid_response(MARKET, "authorized_reference"); bad["artifact_references"] = [{"ref_id": "artifact_001", "ref_type": "runtime_artifact", "sha256": h("artifact"), "availability": "available"}]
    add(rows, "finding_negative_authorized_reference_with_artifacts", resp, schemas[resp], bad, False, "additional_finding_regression")
    bad = valid_interface("resolve"); bad["state_resolution_request"]["resolution_policy"]["mode"] = "invoke_with_authorization"
    add(rows, "finding_negative_resolve_with_invoke_mode", iface, schemas[iface], bad, False, "additional_finding_regression")
    bad = valid_view(); bad["capabilities"][0]["supported_event_type_ids"] = [SESSION_OPENED]
    add(rows, "finding_negative_market_capability_event_type_scope", view, schemas[view], bad, False, "additional_finding_regression")


def run_matrix(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    schemas = {n: d["json_schema"] for n, d in contracts.items()}
    rows: list[dict[str, Any]] = []
    ajv = compile_rows(rows, schemas)
    original_cases(rows, schemas)
    external_cases(rows, schemas)
    additional_cases(rows, schemas)
    failed = [r for r in rows if r["result"] == "FAIL"]
    semantic_groups = {"external_13_regression", "additional_finding_regression"}
    semantic_failed = [r for r in rows if r["case_group"] in semantic_groups and r["result"] == "FAIL"]
    return {
        "gate": GATE,
        "created_at_utc": now_utc(),
        "status": STATUS if not failed and len(rows) >= MIN_CASES else "FAILED_PROVIDER_CONTRACT_SCHEMA_HARDENING_V0_1_2",
        "case_count": len(rows),
        "minimum_case_count": MIN_CASES,
        "original_internal_cases_declared": 31,
        "external_audit_cases_promoted_to_regression": 13,
        "additional_finding_regression_cases": len([r for r in rows if r["case_group"] == "additional_finding_regression"]),
        "failed_cases": len(failed),
        "jsonschema_compile": "PASS" if not [r for r in rows if r["case_group"] == "original_internal_schema_compile" and r["result"] == "FAIL"] else "FAIL",
        "ajv_strict_runtime": "PASS" if ajv.get("available") and not [r for r in rows if r["case_group"] == "ajv_draft_2020_12_strict_runtime" and r["result"] == "FAIL"] else "FAIL",
        "ajv_runtime_available": bool(ajv.get("available")),
        "ajv_version": ajv.get("version"),
        "ajv_error": ajv.get("error"),
        "semantic_validator_execution": "PASS" if not semantic_failed else "FAIL",
        "runtime_requests_executed": 0,
        "datasets_written": 0,
        "builds_materializations": 0,
        "registry_mutations": 0,
        "StateReplayFeed": "NOT_AUTHORIZED",
        "backtest_consumption_authority": False,
        "production": False,
        "downstream": False,
        "rows": rows,
    }


def replace_line(text: str, prefix: str, new_line: str) -> str:
    lines, done = text.splitlines(), False
    for i, line in enumerate(lines):
        if line.startswith(prefix) and not done:
            lines[i], done = new_line, True
    return "\n".join(lines) + "\n"


def insert_top(text: str, block: str) -> str:
    if block.strip() in text:
        return text
    lines = text.splitlines()
    idx = min(len(lines), 7)
    return "\n".join(lines[:idx]) + "\n\n" + block.strip() + "\n\n" + "\n".join(lines[idx:]) + "\n"


def update_docs(now: str, matrix: dict[str, Any], zip_path: Path) -> None:
    block = f"""## Corrective Provider Contract Schema Hardening v0.1.2 - {now[:10]}

```text
{PREV_GATE} = {PREV_STATUS}
PROVIDER_V0_1_1_EXTERNAL_AUDIT = {PREV_AUDIT}
{GATE} = {matrix['status']}
case_count = {matrix['case_count']}
minimum_case_count = {matrix['minimum_case_count']}
failed_cases = {matrix['failed_cases']}
jsonschema Draft 2020-12 compile = {matrix['jsonschema_compile']}
AJV Draft 2020-12 strict runtime = {matrix['ajv_strict_runtime']}
semantic validator execution = {matrix['semantic_validator_execution']}
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

Provider-only package for external audit:

```text
{zip_path}
```
"""
    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    text = replace_line(read_text(route), "Status:", "Status: `route_v1_44_provider_contract_schema_hardened_v0_1_2_external_audit_pending`")
    text = replace_line(text, "Current gate:", "Current gate: `runtime_provider_contract_schema_hardening_v0_1_2_external_audit_pending`")
    write_text(route, insert_top(text, block))

    agent = FEATURE_ROOT / "AGENT.md"
    agent_block = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Provider Contract Schema Hardened v0.1.2 Pending External Audit

Status: `agent_handoff_prompt_v0_131`
Date: `{now[:10]}`

```text
current_gate = runtime_provider_contract_schema_hardening_v0_1_2_external_audit_pending
last_closed_gate = {GATE}
last_closed_status = {matrix['status']}
previous_internal_status = {PREV_STATUS}
previous_external_audit_status = {PREV_AUDIT}
provider_consumer_compatibility = NOT_OPENED_AFTER_V0_1_2
consumer_contract_status = DRAFT
case_count = {matrix['case_count']}
minimum_case_count = {matrix['minimum_case_count']}
failed_cases = {matrix['failed_cases']}
ajv_strict_runtime = {matrix['ajv_strict_runtime']}
semantic_validator_execution = {matrix['semantic_validator_execution']}
runtime_requests_executed = 0
datasets_written = 0
registry_mutations = 0
state_replay_feed_authority = false
backtest_state_consumption_authority = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
provider_only_zip = {zip_path}
```

Do not open provider-consumer compatibility, StateReplayFeed, physical state row delivery, production or downstream until this v0.1.2 provider-only package passes external adversarial audit.

"""
    write_text(agent, agent_block + read_text(agent))

    readme = RUNTIME / "README.md"
    text = replace_line(read_text(readme), "Status:", "Status: `provider_contract_schema_hardened_v0_1_2_external_audit_pending`")
    text = replace_line(text, "Current gate:", "Current gate: `runtime_provider_contract_schema_hardening_v0_1_2_external_audit_pending`")
    write_text(readme, insert_top(text, "## Provider Contract Schema Hardening v0.1.2\n\n" + block))

    changelog = FEATURE_ROOT / "CHANGELOG.md"
    text = read_text(changelog) if changelog.exists() else "# Changelog\n"
    if "Provider Contract Schema Hardening v0.1.2" not in text:
        text = text.rstrip() + f"""

## {now[:10]} - Provider Contract Schema Hardening v0.1.2

- Preserved `{PREV_GATE}` as `{PREV_STATUS}` while recording external audit status `{PREV_AUDIT}`.
- Closed `{GATE}` as `{matrix['status']}`.
- Added v0.1.2 provider-only contracts without overwriting v0.1.1 contract artifacts.
- Promoted 13 external adversarial cases into permanent regression coverage.
- Added semantic validation for the eight external findings.
- Verification: case_count={matrix['case_count']}, failed_cases={matrix['failed_cases']}, AJV strict runtime={matrix['ajv_strict_runtime']}, semantic validator={matrix['semantic_validator_execution']}.
- Kept provider-consumer compatibility, StateReplayFeed, physical state consumption, production and downstream closed.
"""
    write_text(changelog, text)


def write_readout(path: Path, now: str, m: dict[str, Any], zip_path: Path) -> None:
    write_text(path, f"""# Runtime Provider Contract Schema Hardening v0.1.2 Readout

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{m['status']}`

```text
PROVIDER_SCHEMA_HARDENING_V0_1_1 = {PREV_STATUS}
PROVIDER_V0_1_1_EXTERNAL_AUDIT = {PREV_AUDIT}
case_count = {m['case_count']}
minimum_case_count = {m['minimum_case_count']}
failed_cases = {m['failed_cases']}
jsonschema Draft 2020-12 compile = {m['jsonschema_compile']}
AJV Draft 2020-12 strict runtime = {m['ajv_strict_runtime']}
ajv_runtime_available = {str(m['ajv_runtime_available']).lower()}
ajv_version = {m['ajv_version']}
semantic validator execution = {m['semantic_validator_execution']}
runtime_requests_executed = 0
datasets_written = 0
builds_materializations = 0
registry_mutations = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption_authority = false
production = false
downstream = false
```

This is provider-only schema and semantic hardening. It does not execute requests, deliver physical state rows, promote official datasets, open StateReplayFeed, authorize backtest consumption, open production, or open downstream.

Provider-only package for external audit:

```text
{zip_path}
```
""")


def main() -> None:
    now = now_utc()
    stamp = now.replace("-", "").replace(":", "").replace("+00:00", "Z")
    contract_paths = write_contracts()
    contracts = {p.name: read_json(p) for p in contract_paths}
    matrix = run_matrix(contracts)
    matrix["created_at_utc"] = now

    auth = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_authorization.md"
    write_text(auth, f"# Runtime Provider Contract Schema Hardening v0.1.2 Authorization\n\nGate: `{GATE}`\nDate: `{now[:10]}`\nStatus: `AUTHORIZED_PROVIDER_ONLY_NO_EXECUTION`\n\nCorrect only the eight executable semantic gaps found by the external/adversarial audit of v0.1.1. No runtime requests, builds, datasets, registry mutations, physical row delivery, backtest consumption, StateReplayFeed, production or downstream are authorized.\n")
    scope = CONFIGS / "runtime_provider_contract_schema_hardening_v0_1_2_scope.json"
    write_json(scope, {"scope_id": "runtime_provider_contract_schema_hardening_v0_1_2_scope", "gate": GATE, "created_at_utc": now, "provider_only": True, "previous_internal_status": PREV_STATUS, "previous_external_audit_status": PREV_AUDIT, "minimum_case_count": MIN_CASES, "not_in_scope": ["runtime_provider_consumer_contract_compatibility_review_v0_1", "StateReplayFeed", "backtest consumption", "physical state row delivery", "production", "downstream"], "hard_boundaries": {"runtime_requests_executed": 0, "datasets_written": 0, "builds_materializations": 0, "registry_mutations": 0, "downstream": False, "production": False, "backtest_consumption_authority": False, "state_replay_feed_authorized": False}})
    matrix_path = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json"
    write_json(matrix_path, matrix)
    readout = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_readout.md"
    zip_path = FEATURE_ROOT / f"runtime_provider_contract_schema_hardening_v0_1_2_provider_only_{stamp}.zip"
    write_readout(readout, now, matrix, zip_path)
    update_docs(now, matrix, zip_path)

    files = [auth, scope, matrix_path, readout, FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", FEATURE_ROOT / "CHANGELOG.md", SCRIPTS / "runtime_provider_contract_schema_hardening_v0_1_2_runner.py"] + contract_paths
    unique = []
    seen = set()
    for p in files:
        if p.exists() and p not in seen:
            unique.append(p)
            seen.add(p)
    manifest = {"package_id": "runtime_provider_contract_schema_hardening_v0_1_2_provider_only", "created_at_utc": now, "gate": GATE, "status": matrix["status"], "entry_count_excluding_manifest": len(unique), "explicitly_excluded": ["02_TSIS_BACKTEST_ENGINE files", "StateReplayFeed files", "runtime requests", "runtime runs", "parquet files", "physical market data", "physical state rows", "downstream artifacts"], "entries": [entry(p) for p in unique]}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in unique:
            zf.write(p, rel(p))
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"gate": GATE, "status": matrix["status"], "case_count": matrix["case_count"], "minimum_case_count": matrix["minimum_case_count"], "failed_cases": matrix["failed_cases"], "ajv_strict_runtime": matrix["ajv_strict_runtime"], "ajv_version": matrix["ajv_version"], "semantic_validator_execution": matrix["semantic_validator_execution"], "zip_path": str(zip_path)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

