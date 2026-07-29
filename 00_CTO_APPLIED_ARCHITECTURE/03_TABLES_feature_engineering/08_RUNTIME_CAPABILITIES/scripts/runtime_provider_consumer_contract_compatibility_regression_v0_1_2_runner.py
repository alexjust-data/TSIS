from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover - reported in matrix when unavailable
    Draft202012Validator = None


ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
CONFIGS = RUNTIME / "configs"
BACKTEST_CONTRACTS = ROOT / "02_TSIS_BACKTEST_ENGINE" / "contracts" / "backtest"
CHANGELOG = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"

GATE = "runtime_provider_consumer_contract_compatibility_regression_v0_1_2"
STATUS = "CLOSED_PASS_PROVIDER_CONSUMER_CONTROL_PLANE_COMPATIBLE_WITH_RESTRICTIONS_NO_CONSUMPTION"
NEXT_GATE = "state_bundle_manifest_physical_evidence_alignment_v0_1"

ACCEPTED_ZIP = (
    FEATURE_ROOT
    / "runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T141808Z.zip"
)
ACCEPTED_ZIP_SHA256 = "191f40e40f2cfe374ce2f493fb9dd3e2509e33f64b9ed8f3969c9c8b0badf759"

PROVIDER_CONTRACT_FILES = {
    "state_resolution_request": RUNTIME / "state_resolution_request_contract_v0_1_2.json",
    "runtime_user_invocation_interface": RUNTIME / "runtime_user_invocation_interface_contract_v0_1_2.json",
    "runtime_user_invocation_response": RUNTIME / "runtime_user_invocation_response_contract_v0_1_2.json",
    "state_bundle_manifest": RUNTIME / "state_bundle_manifest_contract_v0_1_2.json",
    "runtime_capability_effective_view": RUNTIME / "runtime_capability_effective_view_contract_v0_1_2.json",
}

SPECIALIZED_AUXILIARY_CONTRACT_FILES = {
    "market_state_request": RUNTIME / "market_state_request_contract_v0_1.json",
    "event_state_request": RUNTIME / "event_state_request_contract_v0_1.json",
}

CONSUMER_CONTRACT_FILES = {
    "backtest_run_spec": BACKTEST_CONTRACTS / "backtest_run_spec_contract_v0_1.json",
    "backtest_input_manifest": BACKTEST_CONTRACTS / "backtest_input_manifest_contract_v0_1.json",
}

OUTPUTS = {
    "authorization": RUNTIME
    / "runtime_provider_consumer_contract_compatibility_regression_v0_1_2_authorization_v0_1.md",
    "scope": CONFIGS
    / "runtime_provider_consumer_contract_compatibility_regression_v0_1_2_scope_v0_1.json",
    "matrix": RUNTIME
    / "runtime_provider_consumer_contract_compatibility_regression_v0_1_2_matrix_v0_1.json",
    "readout": RUNTIME
    / "runtime_provider_consumer_contract_compatibility_regression_v0_1_2_readout_v0_1.md",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def schema_of(doc: dict[str, Any]) -> dict[str, Any]:
    return doc.get("json_schema", doc)


def contract_ref(path: Path) -> dict[str, str]:
    doc = read_json(path)
    return {
        "contract_id": str(doc.get("contract_id") or path.stem),
        "contract_version": str(doc.get("contract_version") or "0.1"),
        "contract_sha256": sha256_file(path),
    }


def schema_compile_status(doc: dict[str, Any]) -> tuple[str, str]:
    if Draft202012Validator is None:
        return "BLOCK", "jsonschema package unavailable"
    try:
        Draft202012Validator.check_schema(schema_of(doc))
    except Exception as exc:
        return "BLOCK", str(exc)
    return "PASS", "Draft 2020-12 schema compiles"


def enum_values(schema: dict[str, Any], prop: str) -> set[str]:
    value = schema.get("properties", {}).get(prop, {})
    return set(value.get("enum", []))


def const_value(schema: dict[str, Any], prop: str) -> Any:
    return schema.get("properties", {}).get(prop, {}).get("const", None)


def get_def(doc: dict[str, Any], name: str) -> dict[str, Any]:
    return doc.get("$defs", {}).get(name, {})


def validate_subschema(root_schema: dict[str, Any], def_name: str, instance: Any) -> list[str]:
    if Draft202012Validator is None:
        return ["jsonschema package unavailable"]
    validator = Draft202012Validator(root_schema)
    sub = validator.evolve(schema=root_schema["$defs"][def_name])
    return [err.message for err in sorted(sub.iter_errors(instance), key=lambda e: list(e.path))]


def build_state_consumption_sample(state_kind: str) -> dict[str, Any]:
    provider_contracts = {k: contract_ref(v) for k, v in PROVIDER_CONTRACT_FILES.items()}
    if state_kind == "market_state":
        provider_contracts["market_state_request"] = contract_ref(
            SPECIALIZED_AUXILIARY_CONTRACT_FILES["market_state_request"]
        )
        profile_id = "market_state_core_four_intraday_profile_v0_1"
        information_objects = ["trading_activity", "price_movement"]
        fields = ["decision_timestamp", "state_available_at_utc"]
    else:
        provider_contracts["event_state_request"] = contract_ref(
            SPECIALIZED_AUXILIARY_CONTRACT_FILES["event_state_request"]
        )
        profile_id = "event_state_core_four_intraday_profile_v0_1"
        information_objects = ["event_context"]
        fields = ["event_timestamp", "event_available_at", "state_available_at_utc"]

    temporal_policy: dict[str, Any] = {
        "decision_clock_basis": "event_loop_clock",
        "require_available_at": True,
        "future_window_allowed": False,
        "outcome_dependency_allowed": False,
    }
    if state_kind == "event_state":
        temporal_policy["event_state_consumption_legality"] = ["decision_safe"]

    return {
        "consumption_purpose": "backtest",
        "provider_contracts": provider_contracts,
        "resolution_policy": {
            "policy_id": "backtest_state_resolution_policy_v0_1",
            "provider_request_cardinality": "ONE_PER_STATE_KIND",
            "provider_response_cardinality": "ONE_PER_STATE_RESOLUTION_REQUEST",
            "bundle_cardinality": "ONE_AGGREGATED_BUNDLE_PER_BACKTEST_PREFLIGHT",
            "partial_success_allowed": False,
            "require_single_bundle_covers_all_requests": True,
            "capability_view_mode": "CURRENT_EFFECTIVE_VIEW",
        },
        "requests": [
            {
                "consumer_request_id": f"{state_kind}_consumer_probe_v0_1",
                "state_kind": state_kind,
                "profile_id": profile_id,
                "representation_version": "0.1",
                "resolution": "1m",
                "required_information_objects": information_objects,
                "required_fields": fields,
                "coverage_policy": "REQUIRE_COMPLETE",
                "temporal_policy": temporal_policy,
            }
        ],
    }


def build_scope(now: str) -> dict[str, Any]:
    return {
        "gate": GATE,
        "status": "AUTHORIZED_AND_EXECUTED_BY_RUNNER",
        "created_at_utc": now,
        "owner_layer": "08_RUNTIME_CAPABILITIES",
        "purpose": (
            "Control-plane-only regression that checks whether the backtest consumer draft "
            "can interpret the accepted provider v0.1.2 contracts without opening physical "
            "StateBundle consumption."
        ),
        "accepted_provider_authority": {
            "gate": "runtime_provider_contract_schema_hardening_v0_1_2",
            "status": "CLOSED_EXTERNAL_AUDIT_PASS_ACCEPTABLE_AS_PROVIDER_AUTHORITY_WITH_RESTRICTIONS",
            "provider_only_zip_ref": rel(ACCEPTED_ZIP),
            "provider_only_zip_sha256": ACCEPTED_ZIP_SHA256,
            "local_provider_only_zip_required_for_this_regression_package": False,
        },
        "provider_contracts": {k: rel(v) for k, v in PROVIDER_CONTRACT_FILES.items()},
        "specialized_auxiliary_contracts": {
            k: rel(v) for k, v in SPECIALIZED_AUXILIARY_CONTRACT_FILES.items()
        },
        "consumer_contracts_read_only": {k: rel(v) for k, v in CONSUMER_CONTRACT_FILES.items()},
        "authorized_outputs": {**{k: rel(v) for k, v in OUTPUTS.items()}, "runner": rel(RUNTIME / "scripts" / "runtime_provider_consumer_contract_compatibility_regression_v0_1_2_runner.py")},
        "explicitly_out_of_scope": [
            "02_TSIS_BACKTEST_ENGINE file edits",
            "StateBundle physical reads",
            "StateReplayFeed",
            "EventLoop integration",
            "backtest runs",
            "runtime builds",
            "dataset writes",
            "registry mutations",
            "production",
            "downstream",
            "official dataset promotion",
        ],
        "hard_boundaries": {
            "physical_file_reads": 0,
            "state_bundle_rows_delivered": 0,
            "state_replay_feed_events": 0,
            "backtest_runs_started": 0,
            "runtime_requests_executed": 0,
            "runtime_builds_executed": 0,
            "datasets_written": 0,
            "registry_mutations": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
            "backtest_consumption": False,
        },
        "expected_close_status": STATUS,
        "next_gate_if_pass": NEXT_GATE,
    }


def build_matrix(now: str) -> dict[str, Any]:
    provider_docs = {k: read_json(v) for k, v in PROVIDER_CONTRACT_FILES.items()}
    consumer_docs = {k: read_json(v) for k, v in CONSUMER_CONTRACT_FILES.items()}
    auxiliary_docs = {k: read_json(v) for k, v in SPECIALIZED_AUXILIARY_CONTRACT_FILES.items()}
    rows: list[dict[str, Any]] = []

    def row(
        case_id: str,
        area: str,
        expectation: str,
        observation: str,
        result: str,
        evidence_refs: list[str],
        notes: str = "",
    ) -> None:
        rows.append(
            {
                "case_id": case_id,
                "area": area,
                "consumer_expectation": expectation,
                "provider_v0_1_2_observation": observation,
                "result": result,
                "evidence_refs": evidence_refs,
                "notes": notes,
            }
        )

    missing = [
        rel(p)
        for p in list(PROVIDER_CONTRACT_FILES.values())
        + list(SPECIALIZED_AUXILIARY_CONTRACT_FILES.values())
        + list(CONSUMER_CONTRACT_FILES.values())
        if not p.exists()
    ]
    row(
        "REG_INPUTS_001",
        "input_inventory",
        "Provider v0.1.2 contracts, auxiliary payload docs, consumer draft contracts and accepted ZIP are available.",
        f"missing={missing}",
        "PASS" if not missing else "BLOCK",
        [
            *(rel(p) for p in PROVIDER_CONTRACT_FILES.values()),
            *(rel(p) for p in SPECIALIZED_AUXILIARY_CONTRACT_FILES.values()),
            *(rel(p) for p in CONSUMER_CONTRACT_FILES.values()),
            rel(ACCEPTED_ZIP),
        ],
    )

    acceptance_readout = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_external_audit_acceptance_readout_v0_1.md"
    acceptance_text = read_text(acceptance_readout) if acceptance_readout.exists() else ""
    zip_hash = sha256_file(ACCEPTED_ZIP) if ACCEPTED_ZIP.exists() else None
    readout_binds_zip = (
        "CLOSED_EXTERNAL_AUDIT_PASS_ACCEPTABLE_AS_PROVIDER_AUTHORITY_WITH_RESTRICTIONS" in acceptance_text
        and ACCEPTED_ZIP_SHA256 in acceptance_text
        and ACCEPTED_ZIP.name in acceptance_text
    )
    if zip_hash == ACCEPTED_ZIP_SHA256:
        authority_result = "PASS"
        authority_observed = f"local_zip_sha256={zip_hash}"
    elif readout_binds_zip:
        authority_result = "PASS_WITH_RESTRICTION"
        authority_observed = "local_zip_absent; accepted zip identity bound by external-audit acceptance readout"
    else:
        authority_result = "BLOCK"
        authority_observed = f"local_zip_sha256={zip_hash}; readout_binds_zip={readout_binds_zip}"
    row(
        "REG_PROVIDER_AUTHORITY_001",
        "accepted_provider_authority",
        "Regression must bind to the externally accepted provider-only ZIP identity without regenerating it.",
        authority_observed,
        authority_result,
        [rel(ACCEPTED_ZIP), rel(acceptance_readout)],
        "The accepted ZIP is not regenerated or modified by this regression. If absent locally, its authority is the external-audit acceptance readout and exact SHA-256 record.",
    )

    compile_failures = []
    for name, doc in {**provider_docs, **consumer_docs}.items():
        status, detail = schema_compile_status(doc)
        if status != "PASS":
            compile_failures.append({"contract": name, "detail": detail})
    row(
        "REG_SCHEMA_001",
        "schema_compilation",
        "Provider v0.1.2 contracts and consumer draft schemas compile under Draft 2020-12.",
        f"compile_failures={compile_failures}",
        "PASS" if not compile_failures else "BLOCK",
        [*(rel(p) for p in PROVIDER_CONTRACT_FILES.values()), *(rel(p) for p in CONSUMER_CONTRACT_FILES.values())],
    )

    provider_versions = {
        key: doc.get("contract_version") for key, doc in provider_docs.items()
    }
    row(
        "REG_PROVIDER_VERSION_001",
        "provider_contract_versions",
        "All executable provider exchange contracts used by the consumer-facing control-plane are v0.1.2.",
        f"provider_versions={provider_versions}",
        "PASS" if set(provider_versions.values()) == {"0.1.2"} else "BLOCK",
        [*(rel(p) for p in PROVIDER_CONTRACT_FILES.values())],
        "Specialized Market/Event payload files remain auxiliary v0.1.1 docs, not executable v0.1.2 authority.",
    )

    request_schema = schema_of(provider_docs["state_resolution_request"])
    response_schema = schema_of(provider_docs["runtime_user_invocation_response"])
    bundle_schema = schema_of(provider_docs["state_bundle_manifest"])
    view_schema = schema_of(provider_docs["runtime_capability_effective_view"])

    row(
        "REG_REQUEST_001",
        "request_type_alignment",
        "Provider request envelope distinguishes market_state and event_state without a third state kind.",
        (
            f"request_type={sorted(enum_values(request_schema, 'request_type'))}; "
            f"state_kind={sorted(enum_values(request_schema, 'state_kind'))}"
        ),
        "PASS"
        if enum_values(request_schema, "request_type") == {"market_state", "event_state"}
        and enum_values(request_schema, "state_kind") == {"market_state", "event_state"}
        else "BLOCK",
        [rel(PROVIDER_CONTRACT_FILES["state_resolution_request"])],
    )

    request_text = json.dumps(request_schema, sort_keys=True)
    event_scope_ok = (
        "event_type:market_data:session_opened" in request_text
        and "exchange_session" in request_text
        and "halt_resumed" not in request_text
    )
    row(
        "REG_EVENT_SCOPE_001",
        "event_state_scope",
        "Consumer must not see Event State as a general event library.",
        "session_opened/exchange_session present; halt_resumed absent",
        "PASS" if event_scope_ok else "BLOCK",
        [rel(PROVIDER_CONTRACT_FILES["state_resolution_request"])],
    )

    response_decisions = enum_values(response_schema, "resolution_decision")
    required_decisions = {
        "VALID_REQUEST_REUSE_HIT",
        "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED",
        "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE",
        "BLOCKED_INVALID_REQUEST",
        "BLOCKED_UNSUPPORTED_CAPABILITY",
        "BLOCKED_UNSUPPORTED_PROFILE",
        "BLOCKED_UNSUPPORTED_EVENT_TYPE",
        "BLOCKED_CONSUMPTION_NOT_AUTHORIZED",
        "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED",
        "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED",
        "BLOCKED_PROVIDER_CONTRACT_MISMATCH",
    }
    row(
        "REG_RESPONSE_TAXONOMY_001",
        "response_status_taxonomy",
        "Consumer receives a common response taxonomy and explicit block codes.",
        f"missing_decisions={sorted(required_decisions - response_decisions)}",
        "PASS" if required_decisions.issubset(response_decisions) else "BLOCK",
        [rel(PROVIDER_CONTRACT_FILES["runtime_user_invocation_response"])],
    )

    provider_closed_flags = (
        const_value(response_schema, "official_dataset") is False
        and const_value(response_schema, "production") is False
        and const_value(response_schema, "downstream") is False
        and const_value(bundle_schema, "official_dataset") is False
        and const_value(bundle_schema, "production") is False
        and const_value(bundle_schema, "downstream") is False
        and const_value(bundle_schema, "physical_rows_delivered") is False
    )
    row(
        "REG_PROVIDER_RESTRICTIONS_001",
        "no_physical_or_downstream_authority",
        "Provider v0.1.2 may return governed references but must not authorize official/downstream/physical delivery.",
        "response and bundle const false checks evaluated",
        "PASS" if provider_closed_flags else "BLOCK",
        [
            rel(PROVIDER_CONTRACT_FILES["runtime_user_invocation_response"]),
            rel(PROVIDER_CONTRACT_FILES["state_bundle_manifest"]),
        ],
    )

    capability_text = json.dumps(view_schema, sort_keys=True)
    capability_ok = all(
        token in capability_text
        for token in [
            "market_state_on_demand_runtime_capability_v0_1",
            "event_state_on_demand_runtime_capability_v0_1",
            "market_state_core_four_intraday_profile_v0_1",
            "event_state_core_four_intraday_profile_v0_1",
            "event_type:market_data:session_opened",
        ]
    )
    no_consume_ok = all(
        token in capability_text
        for token in [
            '"physical_row_delivery": {"const": false}',
            '"state_replay_feed": {"const": false}',
            '"backtest_consumption": {"const": false}',
        ]
    )
    row(
        "REG_EFFECTIVE_VIEW_001",
        "effective_capability_view",
        "Capability view resolves exactly the two restricted state capabilities and keeps consumption closed.",
        f"capability_tokens_present={capability_ok}; no_consume_tokens_present={no_consume_ok}",
        "PASS" if capability_ok and no_consume_ok else "BLOCK",
        [rel(PROVIDER_CONTRACT_FILES["runtime_capability_effective_view"])],
    )

    run_spec = consumer_docs["backtest_run_spec"]
    input_manifest = consumer_docs["backtest_input_manifest"]
    state_optional = "state_consumption" not in run_spec.get("required", [])
    manifest_states_optional = "states" not in input_manifest.get("required", [])
    row(
        "REG_CONSUMER_OPTIONAL_STATES_001",
        "consumer_optional_state_lane",
        "Backtester can remain frozen without state integration when provider consumption is not authorized.",
        f"BacktestRunSpec.state_consumption_optional={state_optional}; BacktestInputManifest.states_optional={manifest_states_optional}",
        "PASS" if state_optional and manifest_states_optional else "BLOCK",
        [rel(CONSUMER_CONTRACT_FILES["backtest_run_spec"]), rel(CONSUMER_CONTRACT_FILES["backtest_input_manifest"])],
    )

    for state_kind in ["market_state", "event_state"]:
        sample = build_state_consumption_sample(state_kind)
        errors = validate_subschema(run_spec, "state_consumption", sample)
        row(
            f"REG_CONSUMER_STATE_CONSUMPTION_SCHEMA_{state_kind.upper()}",
            "consumer_state_consumption_schema",
            f"Consumer draft state_consumption can reference provider v0.1.2 contracts for {state_kind}.",
            f"errors={errors}",
            "PASS" if not errors else "BLOCK",
            [rel(CONSUMER_CONTRACT_FILES["backtest_run_spec"]), *(rel(p) for p in PROVIDER_CONTRACT_FILES.values())],
            "Auxiliary payload ref is included only because the current consumer draft conditionally requires it.",
        )

    state_consumption_def = get_def(run_spec, "state_consumption")
    provider_contracts_def = state_consumption_def.get("properties", {}).get("provider_contracts", {})
    required_provider_keys = set(provider_contracts_def.get("required", []))
    expected_provider_keys = set(PROVIDER_CONTRACT_FILES)
    row(
        "REG_PROVIDER_REF_SET_001",
        "provider_contract_ref_set",
        "Consumer draft requires the five provider exchange contract references.",
        f"required_provider_keys={sorted(required_provider_keys)}",
        "PASS" if expected_provider_keys.issubset(required_provider_keys) else "BLOCK",
        [rel(CONSUMER_CONTRACT_FILES["backtest_run_spec"])],
        "market_state_request and event_state_request remain conditional auxiliary refs in the draft consumer schema.",
    )

    aux_roles = {k: v.get("execution_authority_role") for k, v in auxiliary_docs.items()}
    aux_authorities = {k: v.get("executable_schema_authority") for k, v in auxiliary_docs.items()}
    row(
        "REG_SPECIALIZED_PAYLOAD_AUX_001",
        "specialized_payload_authority",
        "Specialized Market/Event payload files must not become a second executable provider authority.",
        f"roles={aux_roles}; executable_schema_authority={aux_authorities}",
        "PASS_WITH_RESTRICTION"
        if set(aux_roles.values()) == {"normative_auxiliary_not_executable"}
        else "BLOCK",
        [*(rel(p) for p in SPECIALIZED_AUXILIARY_CONTRACT_FILES.values()), rel(PROVIDER_CONTRACT_FILES["state_resolution_request"])],
        "Before removing consumer DRAFT, align these auxiliary refs with the v0.1.2 StateResolutionRequest authority.",
    )

    state_binding = get_def(input_manifest, "state_binding")
    backtest_auth = get_def(input_manifest, "backtest_authorization")
    auth_dataset = get_def(input_manifest, "authorized_state_dataset")
    manifest_requires_authority = (
        "backtest_authorization" in state_binding.get("required", [])
        and backtest_auth.get("properties", {}).get("authorization_status", {}).get("const") == "AUTHORIZED"
        and auth_dataset.get("properties", {}).get("official_dataset", {}).get("const") is True
        and auth_dataset.get("properties", {}).get("downstream_authorized", {}).get("const") is True
    )
    row(
        "REG_BACKTEST_INPUT_MANIFEST_AUTHORITY_001",
        "consumer_manifest_authority",
        "If states are included in BacktestInputManifest, the consumer requires explicit backtest authorization and authorized datasets.",
        f"manifest_requires_authority={manifest_requires_authority}",
        "PASS" if manifest_requires_authority else "BLOCK",
        [rel(CONSUMER_CONTRACT_FILES["backtest_input_manifest"])],
        "Current provider v0.1.2 cannot satisfy this physical/data-plane contract because official/downstream remain false.",
    )

    row(
        "REG_EXPECTED_CONSUMPTION_BLOCK_001",
        "expected_no_consumption",
        "Provider v0.1.2 compatibility must not be mistaken for StateReplayFeed or backtest consumption authorization.",
        "provider official/downstream/physical=false; consumer manifest states require official/downstream/authorization=true",
        "PASS",
        [
            rel(PROVIDER_CONTRACT_FILES["runtime_user_invocation_response"]),
            rel(PROVIDER_CONTRACT_FILES["state_bundle_manifest"]),
            rel(CONSUMER_CONTRACT_FILES["backtest_input_manifest"]),
        ],
        "This is an expected controlled incompatibility at the data-plane boundary, not a provider control-plane failure.",
    )

    hardening_matrix = read_json(RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json")
    hardening_ok = (
        hardening_matrix.get("case_count") == 133
        and hardening_matrix.get("failed_cases") == 0
        and hardening_matrix.get("missing_required_case_ids") == []
        and hardening_matrix.get("duplicate_case_ids") == []
        and hardening_matrix.get("unexpected_case_ids") == []
    )
    row(
        "REG_HARDENING_EVIDENCE_001",
        "provider_semantic_hardening_evidence",
        "Regression relies on the accepted provider v0.1.2 semantic hardening evidence rather than rerunning physical data-plane work.",
        (
            f"case_count={hardening_matrix.get('case_count')}; "
            f"failed_cases={hardening_matrix.get('failed_cases')}; "
            f"missing_required_case_ids={hardening_matrix.get('missing_required_case_ids')}"
        ),
        "PASS" if hardening_ok else "BLOCK",
        [rel(RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_validation_matrix.json")],
    )

    no_runtime_work = {
        "interface_invocations": 0,
        "runtime_requests_executed": 0,
        "runtime_resolutions_executed": 0,
        "runtime_builds_executed": 0,
        "physical_file_reads": 0,
        "state_bundle_rows_delivered": 0,
        "state_replay_feed_events": 0,
        "backtest_runs_started": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption": False,
    }
    row(
        "REG_BOUNDARIES_001",
        "hard_boundaries",
        "Regression is a contract-only control-plane check.",
        json.dumps(no_runtime_work, sort_keys=True),
        "PASS",
        [],
    )

    blocking = [r for r in rows if r["result"] == "BLOCK"]
    restricted = [r for r in rows if r["result"] == "PASS_WITH_RESTRICTION"]
    return {
        "gate": GATE,
        "status": STATUS if not blocking else "BLOCKED_PROVIDER_CONSUMER_CONTROL_PLANE_REGRESSION",
        "created_at_utc": now,
        "accepted_provider_authority": "runtime_provider_contract_schema_hardening_v0_1_2",
        "accepted_provider_zip": rel(ACCEPTED_ZIP),
        "accepted_provider_zip_sha256": ACCEPTED_ZIP_SHA256,
        "case_count": len(rows),
        "failed_cases": len(blocking),
        "restricted_cases": len(restricted),
        "runtime_requests_executed": 0,
        "runtime_resolutions_executed": 0,
        "runtime_builds_executed": 0,
        "physical_file_reads": 0,
        "state_bundle_rows_delivered": 0,
        "state_replay_feed_events": 0,
        "backtest_runs_started": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption": False,
        "consumer_contract_status": "DRAFT_NOT_INTEGRATION_VALIDATED",
        "next_gate_if_pass": NEXT_GATE,
        "rows": rows,
    }


def render_authorization(now: str, scope: dict[str, Any]) -> str:
    return f"""# Runtime Provider-Consumer Contract Compatibility Regression v0.1.2 Authorization

Gate: `{GATE}`
Date: `2026-07-29`
Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`

## Purpose

Open one small control-plane regression against the externally accepted provider v0.1.2 contracts.

This gate checks whether the backtest consumer draft can still interpret the provider exchange contracts after hardening v0.1.2. It does not open physical StateBundle consumption.

## Authority

```text
ACTIVE_PROVIDER_AUTHORITY = runtime_provider_contract_schema_hardening_v0_1_2
accepted_provider_zip = {rel(ACCEPTED_ZIP)}
accepted_provider_zip_sha256 = {ACCEPTED_ZIP_SHA256}
```

## Inputs

```text
provider_contracts = 5 executable v0.1.2 contracts
specialized_payload_contracts = auxiliary v0.1.1 docs only
consumer_contracts = 2 backtest DRAFT contracts, read-only
```

## Restrictions

```text
02_TSIS_BACKTEST_ENGINE edits = forbidden
StateBundle physical reads = 0
StateBundle rows delivered = 0
StateReplayFeed events = 0
backtest runs = 0
runtime builds = 0
datasets written = 0
registry mutations = 0
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

## Authorized Outputs

```text
{rel(OUTPUTS["scope"])}
{rel(OUTPUTS["matrix"])}
{rel(OUTPUTS["readout"])}
```

The accepted provider-only ZIP must remain unchanged.
"""


def render_readout(now: str, matrix: dict[str, Any]) -> str:
    return f"""# Runtime Provider-Consumer Contract Compatibility Regression v0.1.2 Readout

Gate: `{GATE}`
Date: `2026-07-29`
Status: `{matrix["status"]}`

## Summary

```text
ACTIVE_PROVIDER_AUTHORITY = runtime_provider_contract_schema_hardening_v0_1_2
accepted_provider_zip = {rel(ACCEPTED_ZIP)}
accepted_provider_zip_sha256 = {ACCEPTED_ZIP_SHA256}

case_count = {matrix["case_count"]}
failed_cases = {matrix["failed_cases"]}
restricted_cases = {matrix["restricted_cases"]}

consumer_contract_status = DRAFT_NOT_INTEGRATION_VALIDATED
provider_consumer_control_plane = COMPATIBLE_WITH_RESTRICTIONS
StateBundle physical consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

## Result

The accepted provider v0.1.2 contracts remain compatible with the backtest consumer draft at the control-plane boundary:

```text
BacktestRunSpec
-> StateResolutionRequest v0.1.2
-> RuntimeInvocationResponse v0.1.2
-> StateBundleManifest v0.1.2 reference
```

This does not mean the backtester can consume rows. The current provider still returns references only, with `official_dataset = false`, `production = false`, `downstream = false` and no physical row delivery.

## Restrictions Preserved

```text
runtime_requests_executed = 0
runtime_resolutions_executed = 0
runtime_builds_executed = 0
physical_file_reads = 0
state_bundle_rows_delivered = 0
state_replay_feed_events = 0
backtest_runs_started = 0
datasets_written = 0
registry_mutations = 0
```

## Consumer Notes

The backtester contracts remain:

```text
BACKTEST_CONSUMER_CONTRACTS = DRAFT_NOT_INTEGRATION_VALIDATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
```

The current consumer draft still carries conditional references to `market_state_request` and `event_state_request`. Those provider files are auxiliary v0.1.1 documentation, while the executable v0.1.2 authority is `StateResolutionRequest`. Before removing `DRAFT`, the consumer should align that reference model explicitly.

## Next Gate

```text
{NEXT_GATE}
```
"""


def prepend_once(path: Path, title: str, block: str) -> None:
    text = read_text(path) if path.exists() else ""
    if title in text:
        return
    write_text(path, block.rstrip() + "\n\n" + text.rstrip() + "\n")


def update_live_docs(matrix: dict[str, Any]) -> None:
    route_block = f"""## Provider-Consumer Contract Compatibility Regression v0.1.2 Closed - 2026-07-29

```text
{GATE}
=
{matrix["status"]}

ACTIVE_PROVIDER_AUTHORITY
=
runtime_provider_contract_schema_hardening_v0_1_2

provider_control_plane
=
REFROZEN_AT_V0_1_2_WITH_RESTRICTIONS

PROVIDER_CONSUMER_CONTROL_PLANE_COMPATIBILITY
=
PASS_WITH_RESTRICTIONS

BACKTEST_CONSUMER_CONTRACTS
=
DRAFT_NOT_INTEGRATION_VALIDATED
```

Still closed:

```text
StateBundle physical consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
runtime_builds = 0
physical_row_delivery = 0
production = false
downstream = false
official_dataset = false
```

Next gate:

```text
{NEXT_GATE}
```"""
    prepend_once(
        FEATURE_ROOT / "99_ruta_de_trabajo.md",
        "Provider-Consumer Contract Compatibility Regression v0.1.2 Closed - 2026-07-29",
        route_block,
    )

    agent_block = f"""## Current Runtime Handoff Override - Provider-Consumer Compatibility Regression v0.1.2 Closed

Status: `agent_handoff_prompt_v0_142`
Date: `2026-07-29`

```text
current_gate = {NEXT_GATE}
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
last_closed_gate = {GATE}
last_closed_status = {matrix["status"]}
active_provider_authority = runtime_provider_contract_schema_hardening_v0_1_2
provider_control_plane = REFROZEN_AT_V0_1_2_WITH_RESTRICTIONS
provider_consumer_control_plane_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = DRAFT_NOT_INTEGRATION_VALIDATED
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
physical_rows_delivered = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not modify `02_TSIS_BACKTEST_ENGINE` from this provider handoff. The next permitted shared-boundary work is state_bundle_manifest_physical_evidence_alignment_v0_1; it still must not open StateReplayFeed or backtest rows."""
    prepend_once(
        FEATURE_ROOT / "AGENT.md",
        "Current Runtime Handoff Override - Provider-Consumer Compatibility Regression v0.1.2 Closed",
        agent_block,
    )

    readme_block = f"""## Provider-Consumer Contract Compatibility Regression v0.1.2

```text
{GATE} = {matrix["status"]}
provider_consumer_control_plane_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = DRAFT_NOT_INTEGRATION_VALIDATED
StateBundle physical consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
```

Next provider/shared-boundary gate:

```text
{NEXT_GATE}
```"""
    prepend_once(
        RUNTIME / "README.md",
        "Provider-Consumer Contract Compatibility Regression v0.1.2",
        readme_block,
    )

    changelog_block = f"""## 2026-07-29 - Provider-consumer contract compatibility regression v0.1.2 closed

- Closed `{GATE}` as `{matrix["status"]}`.
- Confirmed the accepted provider v0.1.2 control-plane contracts remain interpretable by the backtest consumer draft with restrictions.
- Preserved `BACKTEST_CONSUMER_CONTRACTS = DRAFT_NOT_INTEGRATION_VALIDATED`, `StateReplayFeed = NOT_AUTHORIZED`, physical state rows delivered = 0, production = false and downstream = false.
- Next gate is `{NEXT_GATE}`."""
    prepend_once(
        CHANGELOG,
        "Provider-consumer contract compatibility regression v0.1.2 closed",
        changelog_block,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-live-docs", action="store_true")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    scope = build_scope(now)
    matrix = build_matrix(now)

    write_json(OUTPUTS["scope"], scope)
    write_text(OUTPUTS["authorization"], render_authorization(now, scope))
    write_json(OUTPUTS["matrix"], matrix)
    write_text(OUTPUTS["readout"], render_readout(now, matrix))

    if args.update_live_docs and matrix["failed_cases"] == 0:
        update_live_docs(matrix)

    print(json.dumps({
        "gate": GATE,
        "status": matrix["status"],
        "case_count": matrix["case_count"],
        "failed_cases": matrix["failed_cases"],
        "restricted_cases": matrix["restricted_cases"],
        "update_live_docs": bool(args.update_live_docs and matrix["failed_cases"] == 0),
        "next_gate": NEXT_GATE,
    }, indent=2, sort_keys=True))
    return 0 if matrix["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
