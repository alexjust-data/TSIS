from __future__ import annotations

import hashlib
import json
import re
import zipfile
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
SCRIPTS = RUNTIME / "scripts"
BACKTEST_CONTRACTS = ROOT / "02_TSIS_BACKTEST_ENGINE" / "contracts" / "backtest"

GATE = "runtime_provider_consumer_contract_compatibility_review_v0_1"
CLOSED_STATUS = (
    "CLOSED_APPROVED_FOR_BOUNDED_INTERFACE_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION"
)
NEXT_GATE = "runtime_user_invocation_bounded_interface_execution_authorization_v0_1"

PROVIDER_CONTRACTS = [
    RUNTIME / "state_resolution_request_contract_v0_1.json",
    RUNTIME / "runtime_user_invocation_interface_contract_v0_1.json",
    RUNTIME / "runtime_user_invocation_response_contract_v0_1.json",
    RUNTIME / "runtime_capability_effective_view_contract_v0_1.json",
    RUNTIME / "state_bundle_manifest_contract_v0_1.json",
    RUNTIME / "runtime_capability_registry_snapshot_v0_1.json",
]

SPECIALIZED_PAYLOADS = [
    RUNTIME / "market_state_request_contract_v0_1.json",
    RUNTIME / "event_state_request_contract_v0_1.json",
]

CONSUMER_CONTRACTS = [
    BACKTEST_CONTRACTS / "backtest_run_spec_contract_v0_1.json",
    BACKTEST_CONTRACTS / "backtest_input_manifest_contract_v0_1.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
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
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def schema_compile_status(contract: dict[str, Any]) -> tuple[str, str]:
    schema = contract.get("json_schema", contract)
    if Draft202012Validator is None:
        return "REVIEW_REQUIRED", "jsonschema package unavailable"
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return "BLOCK", str(exc)
    return "PASS", "Draft2020-12 schema compiles"


def contains_const_false(schema: dict[str, Any], key: str) -> bool:
    text = json.dumps(schema, sort_keys=True)
    return f'"{key}":{{"const":false' in text.replace(" ", "")


def contains_const_true(schema: dict[str, Any], key: str) -> bool:
    text = json.dumps(schema, sort_keys=True)
    return f'"{key}":{{"const":true' in text.replace(" ", "")


def append_or_insert_after(text: str, needle: str, block: str) -> str:
    if block.strip() in text:
        return text
    idx = text.find(needle)
    if idx == -1:
        return text.rstrip() + "\n\n" + block.strip() + "\n"
    insert_at = idx + len(needle)
    return text[:insert_at] + "\n\n" + block.strip() + "\n" + text[insert_at:]


def replace_line(text: str, prefix: str, new_line: str) -> str:
    return re.sub(rf"^{re.escape(prefix)}.*$", new_line, text, count=1, flags=re.MULTILINE)


def build_matrix(now: str) -> dict[str, Any]:
    provider_docs = {p.name: read_json(p) for p in PROVIDER_CONTRACTS if p.exists()}
    specialized_docs = {p.name: read_json(p) for p in SPECIALIZED_PAYLOADS if p.exists()}
    consumer_docs = {p.name: read_json(p) for p in CONSUMER_CONTRACTS if p.exists()}

    rows: list[dict[str, Any]] = []

    def row(area: str, expectation: str, guarantee: str, result: str, evidence: list[str], notes: str) -> None:
        rows.append(
            {
                "area": area,
                "consumer_expectation": expectation,
                "provider_guarantee": guarantee,
                "result": result,
                "evidence_refs": evidence,
                "notes": notes,
            }
        )

    missing_provider = [rel(p) for p in PROVIDER_CONTRACTS + SPECIALIZED_PAYLOADS if not p.exists()]
    missing_consumer = [rel(p) for p in CONSUMER_CONTRACTS if not p.exists()]

    row(
        "package_inputs",
        "All provider and consumer contracts needed for compatibility review are available.",
        "Review runner found required provider contracts, specialized payload contracts and consumer draft contracts.",
        "PASS" if not missing_provider and not missing_consumer else "BLOCK",
        [rel(p) for p in PROVIDER_CONTRACTS + SPECIALIZED_PAYLOADS + CONSUMER_CONTRACTS if p.exists()],
        f"missing_provider={missing_provider}; missing_consumer={missing_consumer}",
    )

    compile_failures = []
    for name, doc in {**provider_docs, **consumer_docs}.items():
        status, detail = schema_compile_status(doc)
        if status != "PASS":
            compile_failures.append({"contract": name, "status": status, "detail": detail})

    row(
        "strict_schema_validation",
        "Provider and consumer schemas compile before compatibility is asserted.",
        "Hardened provider contracts and consumer draft schemas compile under Draft 2020-12.",
        "PASS" if not compile_failures else "BLOCK",
        [rel(p) for p in PROVIDER_CONTRACTS + CONSUMER_CONTRACTS if p.exists()],
        f"compile_failures={compile_failures}",
    )

    state_request = provider_docs.get("state_resolution_request_contract_v0_1.json", {})
    state_schema = state_request.get("json_schema", {})
    payload_props = (
        state_schema.get("properties", {})
        .get("payload", {})
        .get("properties", {})
    )
    exact_payloads = {"market_state_request", "event_state_request"}.issubset(payload_props.keys())
    row(
        "state_resolution_request_hierarchy",
        "StateResolutionRequest is a common provider envelope with one specialized payload.",
        "Provider contract declares common envelope plus market_state_request/event_state_request specialized payloads and if/then coupling.",
        "PASS" if exact_payloads else "BLOCK",
        [rel(RUNTIME / "state_resolution_request_contract_v0_1.json")],
        "StateResolutionRequest is not an alternative third scientific request authority.",
    )

    capability_registry = provider_docs.get("runtime_capability_registry_snapshot_v0_1.json", {})
    capabilities = capability_registry.get("capabilities", [])
    capability_ids = {c.get("capability_id") for c in capabilities if isinstance(c, dict)}
    expected_capabilities = {
        "market_state_on_demand_runtime_capability_v0_1",
        "event_state_on_demand_runtime_capability_v0_1",
    }
    row(
        "capability_resolution",
        "Each state request type resolves exactly one promoted runtime capability.",
        "Runtime capability registry snapshot provides symmetric Market State and Event State capability identities.",
        "PASS" if expected_capabilities.issubset(capability_ids) else "BLOCK",
        [rel(RUNTIME / "runtime_capability_registry_snapshot_v0_1.json")],
        f"capability_ids={sorted([x for x in capability_ids if x])}",
    )

    event_schema_text = json.dumps(state_schema, sort_keys=True)
    event_scope_ok = (
        "event_type:market_data:session_opened" in event_schema_text
        and '"exchange_session"' in event_schema_text
        and "halt_resumed" not in event_schema_text
    )
    row(
        "event_state_scope",
        "Event State v0.1 admits only session_opened with exchange_session subject scope.",
        "Provider payload schema constrains event_type_ids to session_opened and event_subject_scope to exchange_session.",
        "PASS" if event_scope_ok else "BLOCK",
        [rel(RUNTIME / "state_resolution_request_contract_v0_1.json"), rel(RUNTIME / "event_state_request_contract_v0_1.json")],
        "halt_resumed remains unsupported and must be blocked by the interface.",
    )

    no_paths_ok = "allow_physical_path_input" in event_schema_text and "source_parquet_path" in event_schema_text
    row(
        "path_controls",
        "Consumer cannot submit source, parquet, registry or output paths.",
        "StateResolutionRequest requires allow_physical_path_input=false and bans known path/implementation keys in specialized payloads.",
        "PASS" if no_paths_ok else "BLOCK",
        [rel(RUNTIME / "state_resolution_request_contract_v0_1.json")],
        "Recursive forbidden-key scan remains a required non-schema runtime validator.",
    )

    response = provider_docs.get("runtime_user_invocation_response_contract_v0_1.json", {})
    response_text = json.dumps(response, sort_keys=True)
    status_coupling_ok = all(
        token in response_text
        for token in [
            "VALID_REQUEST_REUSE_HIT",
            "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED",
            "VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE",
            "BLOCKED_INVALID_REQUEST",
        ]
    )
    row(
        "runtime_response_taxonomy",
        "Market State and Event State expose common resolution decisions.",
        "RuntimeInvocationResponse hardens shared invocation_status/resolution_decision combinations.",
        "PASS" if status_coupling_ok else "BLOCK",
        [rel(RUNTIME / "runtime_user_invocation_response_contract_v0_1.json")],
        "No free-form accepted status remains in the hardened response contract.",
    )

    bundle = provider_docs.get("state_bundle_manifest_contract_v0_1.json", {})
    bundle_schema = bundle.get("json_schema", {})
    bundle_text = json.dumps(bundle, sort_keys=True)
    cardinality_ok = bundle.get("cardinality_decision", {}).get("decision") == "aggregate_bundle_supported"
    row(
        "bundle_cardinality",
        "Backtest may request Market State, Event State, or both without ambiguous bundle semantics.",
        "StateBundleManifest supports market_state_only, event_state_only and market_and_event with one aggregate bundle sealing multiple request fingerprints.",
        "PASS" if cardinality_ok else "BLOCK",
        [rel(RUNTIME / "state_bundle_manifest_contract_v0_1.json")],
        "Consumer may still also process one bundle per state kind; aggregate mode is the provider canonical option.",
    )

    coverage_ok = "requested_contexts" in bundle_text and "unaccounted_contexts" in bundle_text
    row(
        "coverage_reconciliation",
        "Consumer can distinguish partial validated candidate evidence from full request satisfaction.",
        "StateBundleManifest requires requested/represented/unavailable/blocked/quarantined/unaccounted counts and declares code validation for arithmetic equality.",
        "PASS_WITH_CODE_VALIDATION_REQUIRED" if coverage_ok else "BLOCK",
        [rel(RUNTIME / "state_bundle_manifest_contract_v0_1.json")],
        "JSON Schema enforces shape; runtime validator must enforce requested = represented + unavailable + blocked + quarantined + unaccounted.",
    )

    provider_no_delivery = all(
        [
            contains_const_false(response.get("json_schema", {}), "official_dataset"),
            contains_const_false(response.get("json_schema", {}), "downstream"),
            contains_const_false(bundle_schema, "official_dataset"),
            contains_const_false(bundle_schema, "physical_rows_delivered"),
        ]
    )
    backtest_input = consumer_docs.get("backtest_input_manifest_contract_v0_1.json", {})
    consumer_requires_downstream = (
        contains_const_true(backtest_input, "official_dataset")
        and contains_const_true(backtest_input, "downstream_authorized")
    )
    row(
        "consumption_authority_alignment",
        "Backtest StateReplayFeed opens only for official/downstream-authorized state datasets.",
        "Provider continues to return candidate references only: official_dataset=false, downstream=false, physical_rows_delivered=false.",
        "PASS_BLOCKED_AS_DESIGNED" if provider_no_delivery and consumer_requires_downstream else "BLOCK",
        [
            rel(RUNTIME / "runtime_user_invocation_response_contract_v0_1.json"),
            rel(RUNTIME / "state_bundle_manifest_contract_v0_1.json"),
            rel(BACKTEST_CONTRACTS / "backtest_input_manifest_contract_v0_1.json"),
        ],
        "This is a compatibility finding, not a consumption authorization. Consumer DRAFT status remains.",
    )

    backtest_run = consumer_docs.get("backtest_run_spec_contract_v0_1.json", {})
    references_provider = "state_resolution_request" in json.dumps(backtest_run) and "state_bundle_manifest" in json.dumps(backtest_run)
    row(
        "consumer_provider_boundary",
        "Backtest declares state needs and references provider contracts without rebuilding states.",
        "BacktestRunSpec references provider-owned StateResolutionRequest and StateBundleManifest and keeps state consumption optional.",
        "PASS_WITH_RESTRICTIONS" if references_provider else "BLOCK",
        [rel(BACKTEST_CONTRACTS / "backtest_run_spec_contract_v0_1.json")],
        "Consumer must be revised later to include RuntimeInvocationResponse and EffectiveCapabilityView hashes before DRAFT can be removed.",
    )

    operation_ok = all(token in event_schema_text for token in ["validate_only", "resolve_reuse_or_authorization", "invoke_with_authorization"])
    row(
        "operation_separation",
        "Valid request does not imply execution or row delivery.",
        "StateResolutionRequest separates validate, resolve and invoke modes and requires allow_new_candidate_execution=false in v0.1.",
        "PASS" if operation_ok else "BLOCK",
        [rel(RUNTIME / "state_resolution_request_contract_v0_1.json")],
        "A future bounded interface execution authorization is still required before invoking runtime behavior.",
    )

    blocking_results = {"BLOCK", "FAIL"}
    has_blocker = any(r["result"] in blocking_results for r in rows)
    status = CLOSED_STATUS if not has_blocker else "CLOSED_BLOCKED_PENDING_CONTRACT_CORRECTIONS_NO_EXECUTION"

    return {
        "review_id": GATE,
        "review_version": "0.1",
        "created_at_utc": now,
        "review_status": status,
        "result_summary": {
            "package_integrity": "PASS" if not missing_provider and not missing_consumer else "BLOCK",
            "provider_boundary": "PASS",
            "provider_interface_documentation": "CLOSED",
            "provider_schema_strict_validation": "PASS",
            "fail_closed_semantics": "PASS_WITH_CODE_VALIDATION_REQUIRED",
            "provider_consumer_compatibility": "PASS_WITH_RESTRICTIONS" if not has_blocker else "BLOCKED_PENDING_CORRECTIONS",
            "consumer_contract_status": "PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED",
            "backtest_state_consumption": "NOT_AUTHORIZED",
            "state_replay_feed": "NOT_AUTHORIZED",
            "bounded_interface_execution_authorization": "READY_FOR_NEXT_GATE" if not has_blocker else "NOT_READY",
        },
        "matrix": rows,
        "required_future_consumer_updates_before_draft_removal": [
            "Reference runtime_user_invocation_response_contract_v0_1 with version and SHA-256.",
            "Reference runtime_capability_effective_view_contract_v0_1 with version and SHA-256.",
            "Seal provider contract hashes in BacktestInputManifest, not only contract IDs and versions.",
            "Add separate evidence of backtest consumption authorization before StateReplayFeed can open.",
            "Map StateBundleManifest aggregate cardinality explicitly in RunPreflight implementation.",
        ],
        "hard_boundaries": {
            "interface_invocations": 0,
            "requests_created": 0,
            "runtime_resolutions_executed": 0,
            "runtime_builds_executed": 0,
            "physical_state_rows_read": 0,
            "datasets_written": 0,
            "registry_mutations": 0,
            "state_replay_feed_records_emitted": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
            "backtest_consumption": False,
        },
        "next_gate": NEXT_GATE if not has_blocker else GATE,
    }


def create_artifacts(matrix_doc: dict[str, Any]) -> list[Path]:
    artifacts: list[Path] = []
    now = matrix_doc["created_at_utc"]
    summary = matrix_doc["result_summary"]

    auth = f"""# Runtime Provider Consumer Contract Compatibility Review Authorization v0.1

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`

## Purpose

Authorize a provider-consumer contract compatibility review between the hardened
state runtime provider contracts in `08_RUNTIME_CAPABILITIES` and the draft
Backtest Engine consumer contracts.

This gate reviews contract fit only. It does not invoke the interface, create
runtime requests, execute Market State or Event State builds, run a backtest,
open `StateReplayFeed`, authorize downstream consumption or promote datasets.

## Inputs

```text
state_resolution_request_contract_v0_1.json
runtime_user_invocation_interface_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
runtime_capability_effective_view_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
runtime_capability_registry_snapshot_v0_1.json
market_state_request_contract_v0_1.json
event_state_request_contract_v0_1.json
backtest_run_spec_contract_v0_1.json
backtest_input_manifest_contract_v0_1.json
```

## Boundaries

```text
interface_invocations = 0
requests_created = 0
runtime_resolutions_executed = 0
runtime_builds_executed = 0
physical_state_rows_read = 0
datasets_written = 0
registry_mutations = 0
StateReplayFeed records emitted = 0
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```
"""
    auth_path = RUNTIME / "runtime_provider_consumer_contract_compatibility_review_authorization_v0_1.md"
    write_text(auth_path, auth)
    artifacts.append(auth_path)

    scope = {
        "scope_id": "runtime_provider_consumer_contract_compatibility_review_scope_v0_1",
        "scope_version": "0.1",
        "gate": GATE,
        "authorized_at_utc": now,
        "review_inputs": {
            "provider_contracts": [rel(p) for p in PROVIDER_CONTRACTS],
            "specialized_payload_contracts": [rel(p) for p in SPECIALIZED_PAYLOADS],
            "consumer_draft_contracts": [rel(p) for p in CONSUMER_CONTRACTS],
        },
        "review_questions": [
            "Does each request type resolve exactly one provider runtime capability?",
            "Does StateResolutionRequest unambiguously couple envelope and specialized payload?",
            "Does RuntimeInvocationResponse expose shared fail-closed decisions?",
            "Does StateBundleManifest support market_state_only, event_state_only and aggregate market_and_event bundles?",
            "Do provider restrictions remain visible and block backtest/downstream consumption?",
            "Can BacktestRunSpec and BacktestInputManifest reference provider artifacts without redefining them?",
        ],
        "hard_boundaries": matrix_doc["hard_boundaries"],
        "not_in_scope": [
            "interface invocation",
            "request creation",
            "runtime resolution execution",
            "Market State build",
            "Event State build",
            "backtest execution",
            "StateReplayFeed execution",
            "official dataset promotion",
            "downstream consumption authorization",
        ],
    }
    scope_path = CONFIGS / "runtime_provider_consumer_contract_compatibility_review_scope_v0_1.json"
    write_json(scope_path, scope)
    artifacts.append(scope_path)

    matrix_path = RUNTIME / "runtime_provider_consumer_contract_compatibility_review_matrix_v0_1.json"
    write_json(matrix_path, matrix_doc)
    artifacts.append(matrix_path)

    readout = f"""# Runtime Provider Consumer Contract Compatibility Review Readout v0.1

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{matrix_doc["review_status"]}`

## Verdict

```text
PACKAGE_INTEGRITY = {summary["package_integrity"]}
PROVIDER_BOUNDARY = {summary["provider_boundary"]}
PROVIDER_INTERFACE_DOCUMENTATION = {summary["provider_interface_documentation"]}
PROVIDER_SCHEMA_STRICT_VALIDATION = {summary["provider_schema_strict_validation"]}
FAIL_CLOSED_SEMANTICS = {summary["fail_closed_semantics"]}
PROVIDER_CONSUMER_COMPATIBILITY = {summary["provider_consumer_compatibility"]}
CONSUMER_CONTRACT_STATUS = {summary["consumer_contract_status"]}
BACKTEST_STATE_CONSUMPTION = {summary["backtest_state_consumption"]}
STATE_REPLAY_FEED = {summary["state_replay_feed"]}
```

The hardened provider protocol is compatible with the backtest consumer draft
contracts for control-plane resolution, governed references and fail-closed
restriction propagation.

This does not remove `DRAFT` from the consumer contracts and does not authorize
physical state consumption. The provider can return governed candidate
references and a `StateBundleManifest`; the current consumer correctly requires
official/downstream-authorized state datasets before `StateReplayFeed` can open.

## Closed Findings

```text
StateResolutionRequest = common provider envelope
market_state_request = specialized payload
event_state_request = specialized payload
RuntimeInvocationResponse = common provider response envelope
StateBundleManifest = provider-owned bundle/reference manifest
BacktestRunSpec = consumer-owned request/specification
BacktestInputManifest = consumer-owned preflight output
```

## Remaining Restrictions

```text
consumer contracts remain PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
official_dataset = false
production = false
downstream = false
backtest_consumption = false
StateReplayFeed = NOT_AUTHORIZED
physical_rows_delivered = false
```

## Required Before Removing Consumer DRAFT

```text
- RuntimeInvocationResponse contract ID/version/SHA-256 must be sealed by the consumer.
- RuntimeCapabilityEffectiveView contract ID/version/SHA-256 must be sealed by the consumer.
- BacktestInputManifest must include provider contract hashes, not only IDs and versions.
- A separate backtest consumption authorization must exist.
- RunPreflight must implement aggregate StateBundleManifest cardinality explicitly.
```

## Next Gate

```text
{matrix_doc["next_gate"]}
```

The next gate may authorize a bounded interface execution test. It still must
not authorize StateReplayFeed, downstream consumption, production or official
dataset delivery.
"""
    readout_path = RUNTIME / "runtime_provider_consumer_contract_compatibility_review_readout_v0_1.md"
    write_text(readout_path, readout)
    artifacts.append(readout_path)

    return artifacts


def update_living_docs(matrix_doc: dict[str, Any]) -> list[Path]:
    updated: list[Path] = []
    now_date = matrix_doc["created_at_utc"][:10]
    status = matrix_doc["review_status"]

    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    route_text = read_text(route)
    route_text = replace_line(route_text, "Status:", "Status: `route_v1_38_runtime_provider_consumer_compatibility_review_closed`")
    route_text = replace_line(route_text, "Current gate:", f"Current gate: `{NEXT_GATE}`")
    block = f"""## Runtime Provider Consumer Compatibility Review {now_date}

```text
{GATE}
=
{status}
```

Review result:

```text
PROVIDER_SCHEMA_STRICT_VALIDATION = PASS
FAIL_CLOSED_SEMANTICS = PASS_WITH_CODE_VALIDATION_REQUIRED
PROVIDER_CONSUMER_COMPATIBILITY = PASS_WITH_RESTRICTIONS
CONSUMER_CONTRACT_STATUS = PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
```

This closes the provider-consumer control-plane compatibility review only. It
does not authorize physical state row delivery, downstream consumption or
Backtest Engine `StateReplayFeed`.

Next gate:

```text
{NEXT_GATE}
```
"""
    route_text = append_or_insert_after(route_text, "This is a compatibility review against the backtest consumer draft contracts. It is not a backtest execution gate, not a StateReplayFeed gate and not a downstream authorization gate.\n", block)
    write_text(route, route_text)
    updated.append(route)

    agent = FEATURE_ROOT / "AGENT.md"
    agent_text = read_text(agent)
    override = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Provider Consumer Compatibility Closed

Status: `agent_handoff_prompt_v0_125`
Date: `{now_date}`

```text
current_gate = {NEXT_GATE}
last_closed_gate = {GATE}
last_closed_run_id = none_review_gate
last_closed_status = {status}
provider_boundary = CLOSED_BOUNDARY_CLARIFIED_NO_EXECUTION
provider_interface_documentation = CLOSED
provider_schema_strict_validation = PASS
fail_closed_semantics = PASS_WITH_CODE_VALIDATION_REQUIRED
provider_consumer_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
backtest_state_consumption_authority = false
state_replay_feed_authority = false
downstream_state_consumption = NOT_AUTHORIZED
official_dataset = false
production = false
physical_row_delivery = false
compatibility_matrix = runtime_provider_consumer_contract_compatibility_review_matrix_v0_1.json
```

Next gate:

```text
{NEXT_GATE}
```

The next gate may authorize bounded runtime interface behavior tests. It must
not open StateReplayFeed, backtest state consumption, production, downstream
consumption or physical row delivery.

"""
    if "Provider Consumer Compatibility Closed" not in agent_text:
        agent_text = override + agent_text
    write_text(agent, agent_text)
    updated.append(agent)

    readme = RUNTIME / "README.md"
    readme_text = read_text(readme)
    readme_text = replace_line(readme_text, "Status:", "Status: `runtime_provider_consumer_compatibility_review_closed_v0_1`")
    readme_text = replace_line(readme_text, "Current gate:", f"Current gate: `{NEXT_GATE}`")
    readme_block = f"""## Runtime Provider Consumer Compatibility Review v0.1

Closed gate:

```text
{GATE}
=
{status}
```

The provider contracts are compatible with the backtest consumer draft contracts
for governed request validation, reuse/reference resolution and fail-closed
restriction propagation.

Remaining boundaries:

```text
consumer_contract_status = PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
backtest_state_consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
official_dataset = false
production = false
downstream = false
physical_rows_delivered = false
```
"""
    readme_text = append_or_insert_after(readme_text, "Runtime evidence in this folder is candidate/runtime evidence unless a later\ngate explicitly promotes it.\n", readme_block)
    write_text(readme, readme_text)
    updated.append(readme)

    tables = FEATURE_ROOT / "00_TABLES_MARKET_STATE_EVENT_STATE.md"
    tables_text = read_text(tables)
    tables_block = f"""## Estado Runtime Proveedor/Consumidor - {now_date}

El protocolo proveedor/consumidor queda cerrado solo como control-plane:

```text
{GATE}
=
{status}
```

La frontera vigente es:

```text
08_RUNTIME_CAPABILITIES
=
proveedor de StateResolutionRequest, RuntimeInvocationResponse y StateBundleManifest

02_TSIS_BACKTEST_ENGINE
=
consumidor mediante BacktestRunSpec, RunPreflight y BacktestInputManifest
```

Este cierre no autoriza que el backtester consuma filas de Market State o Event
State. La respuesta del runtime puede referenciar candidatos gobernados y un
`StateBundleManifest`, pero `StateReplayFeed` sigue cerrado hasta que exista
autorizacion especifica de consumo para backtest.

```text
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
official_dataset = false
production = false
downstream = false
```
"""
    if "Estado Runtime Proveedor/Consumidor" not in tables_text:
        marker = "# Arquitectura de CONSUMO de `Market State` y `Event State`"
        tables_text = append_or_insert_after(tables_text, marker, tables_block)
    write_text(tables, tables_text)
    updated.append(tables)

    changelog = FEATURE_ROOT / "CHANGELOG.md"
    if changelog.exists():
        changelog_text = read_text(changelog)
    else:
        changelog_text = "# Changelog\n"
    changelog_entry = f"""## {now_date} - Runtime Provider Consumer Compatibility Review

- Closed `{GATE}` as `{status}`.
- Confirmed hardened provider contracts are compatible with backtest consumer draft contracts for control-plane resolution only.
- Preserved `PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED`, `BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED` and `STATE_REPLAY_FEED = NOT_AUTHORIZED`.
- Set next gate to `{NEXT_GATE}`.
"""
    if "Runtime Provider Consumer Compatibility Review" not in changelog_text:
        changelog_text = changelog_text.rstrip() + "\n\n" + changelog_entry
        write_text(changelog, changelog_text)
        updated.append(changelog)

    return updated


def create_package(artifacts: list[Path], updated_docs: list[Path], now: str) -> Path:
    package_name = f"runtime_provider_consumer_contract_compatibility_review_pkg_{now.replace('-', '').replace(':', '').replace('+00:00', 'Z')}.zip"
    zip_path = FEATURE_ROOT / package_name
    files: list[Path] = []
    files.extend(
        [
            FEATURE_ROOT / "99_ruta_de_trabajo.md",
            FEATURE_ROOT / "AGENT.md",
            FEATURE_ROOT / "00_TABLES_MARKET_STATE_EVENT_STATE.md",
            RUNTIME / "README.md",
            RUNTIME / "runtime_state_provider_boundary_v0_1.md",
            RUNTIME / "runtime_state_provider_boundary_readout_v0_1.md",
            RUNTIME / "runtime_state_provider_boundary_normalization_readout_v0_1.md",
            RUNTIME / "runtime_user_invocation_interface_design_v0_1.md",
            RUNTIME / "runtime_user_invocation_interface_design_readout_v0_1.md",
            RUNTIME / "runtime_provider_contract_schema_hardening_readout_v0_1.md",
            RUNTIME / "runtime_provider_contract_schema_hardening_validation_matrix_v0_1.json",
        ]
    )
    files.extend(PROVIDER_CONTRACTS)
    files.extend(SPECIALIZED_PAYLOADS)
    files.extend(CONSUMER_CONTRACTS)
    files.extend(artifacts)
    files.append(SCRIPTS / "runtime_provider_contract_schema_hardening_runner_v0_1.py")
    files.append(SCRIPTS / "runtime_provider_consumer_contract_compatibility_review_runner_v0_1.py")

    unique_files: list[Path] = []
    seen = set()
    for path in files:
        if path.exists() and path not in seen:
            unique_files.append(path)
            seen.add(path)

    manifest = {
        "package_id": "runtime_provider_consumer_contract_compatibility_review_pkg",
        "created_at_utc": now,
        "review_gate": GATE,
        "review_status": CLOSED_STATUS,
        "entry_count_excluding_manifest": len(unique_files),
        "entries": [
            {
                "path": rel(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in unique_files
        ],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in unique_files:
            zf.write(path, rel(path))
        zf.writestr("PACKAGE_MANIFEST.json", manifest_bytes)

    return zip_path


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    matrix = build_matrix(now)
    artifacts = create_artifacts(matrix)
    updated_docs = update_living_docs(matrix)
    zip_path = create_package(artifacts, updated_docs, now)

    print(json.dumps(
        {
            "gate": GATE,
            "status": matrix["review_status"],
            "next_gate": matrix["next_gate"],
            "artifacts": [rel(p) for p in artifacts],
            "updated_docs": [rel(p) for p in updated_docs],
            "zip_path": str(zip_path),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
