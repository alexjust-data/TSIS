from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
CONFIGS = RUNTIME / "configs"
SCRIPTS = RUNTIME / "scripts"

GATE = "runtime_user_invocation_bounded_interface_execution_authorization_v0_1"
PREVIOUS_GATE = "runtime_provider_consumer_contract_compatibility_review_v0_1"
NEXT_GATE = "runtime_user_invocation_bounded_interface_execution_v0_1"
STATUS = "CLOSED_AUTHORIZED_BOUNDED_INTERFACE_EXECUTION_WITH_RESTRICTIONS_NO_EXECUTION"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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


def replace_line(text: str, prefix: str, new_line: str) -> str:
    return re.sub(rf"^{re.escape(prefix)}.*$", new_line, text, count=1, flags=re.MULTILINE)


def insert_after_first(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    idx = text.find(marker)
    if idx == -1:
        return text.rstrip() + "\n\n" + block.strip() + "\n"
    return text[: idx + len(marker)] + "\n\n" + block.strip() + "\n" + text[idx + len(marker) :]


def file_ref(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def build_scope(now: str) -> dict[str, Any]:
    provider_contracts = [
        RUNTIME / "state_resolution_request_contract_v0_1.json",
        RUNTIME / "runtime_user_invocation_interface_contract_v0_1.json",
        RUNTIME / "runtime_user_invocation_response_contract_v0_1.json",
        RUNTIME / "runtime_capability_effective_view_contract_v0_1.json",
        RUNTIME / "state_bundle_manifest_contract_v0_1.json",
        RUNTIME / "runtime_capability_registry_snapshot_v0_1.json",
        RUNTIME / "market_state_request_contract_v0_1.json",
        RUNTIME / "event_state_request_contract_v0_1.json",
    ]
    authority_refs = [
        RUNTIME / "runtime_user_invocation_interface_design_readout_v0_1.md",
        RUNTIME / "runtime_provider_contract_schema_hardening_readout_v0_1.md",
        RUNTIME / "runtime_provider_consumer_contract_compatibility_review_readout_v0_1.md",
        RUNTIME / "runtime_provider_consumer_contract_compatibility_review_matrix_v0_1.json",
    ]

    return {
        "scope_id": "runtime_user_invocation_bounded_interface_execution_scope_v0_1",
        "scope_version": "0.1",
        "gate": GATE,
        "authorized_at_utc": now,
        "previous_gate": PREVIOUS_GATE,
        "authorization_status": "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "owner_layer": "08_RUNTIME_CAPABILITIES",
        "purpose": "Authorize a bounded provider-side runtime interface behavior test without state row delivery, backtest consumption or new dataset builds.",
        "authority_refs": [file_ref(p) for p in authority_refs if p.exists()],
        "provider_contract_refs": [file_ref(p) for p in provider_contracts if p.exists()],
        "test_cases_authorized": [
            {
                "case_id": "market_state_exact_reuse_hit_reference_only",
                "request_type": "market_state",
                "expected_decision": "VALID_REQUEST_REUSE_HIT",
                "expected_materializer_executions": 0,
                "expected_source_rows_read": 0,
                "expected_registry_mutations": 0,
                "physical_rows_delivered": False,
            },
            {
                "case_id": "event_state_exact_reuse_hit_reference_only",
                "request_type": "event_state",
                "expected_decision": "VALID_REQUEST_REUSE_HIT",
                "expected_materializer_executions": 0,
                "expected_source_rows_read": 0,
                "expected_registry_mutations": 0,
                "physical_rows_delivered": False,
            },
            {
                "case_id": "event_state_unsupported_halt_resumed_blocked",
                "request_type": "event_state",
                "invalid_event_type": "event_type:regulatory:halt_resumed",
                "expected_decision": "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE",
                "expected_dataset_id": None,
            },
            {
                "case_id": "new_candidate_without_execution_authorization",
                "request_type": "market_state_or_event_state",
                "expected_decision": "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED",
                "expected_materializer_executions": 0,
            },
            {
                "case_id": "production_or_downstream_request_blocked",
                "request_type": "market_state_or_event_state",
                "invalid_requested_mode": "production_or_downstream",
                "expected_decision": "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED",
                "expected_dataset_id": None,
            },
            {
                "case_id": "physical_path_input_blocked",
                "request_type": "market_state_or_event_state",
                "invalid_field_class": "user_supplied_physical_path",
                "expected_decision": "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED",
                "expected_dataset_id": None,
            },
            {
                "case_id": "partial_candidate_coverage_preserved",
                "request_type": "market_state_or_event_state",
                "expected_decision": "VALID_REQUEST_REUSE_HIT",
                "expected_assertion": "represented_contexts and unavailable_contexts are preserved and not presented as complete coverage",
            },
            {
                "case_id": "reuse_hit_zero_build_evidence",
                "request_type": "market_state_or_event_state",
                "expected_decision": "VALID_REQUEST_REUSE_HIT",
                "expected_materializer_executions": 0,
                "expected_source_rows_read": 0,
                "expected_registry_mutations": 0,
            },
        ],
        "permitted_operations": {
            "schema_validation": True,
            "request_normalization": True,
            "request_fingerprint_creation": True,
            "capability_effective_view_lookup": True,
            "candidate_registry_metadata_lookup": True,
            "state_bundle_manifest_reference_return": True,
            "runtime_materialization": False,
            "state_row_delivery": False,
            "backtest_execution": False,
            "state_replay_feed_execution": False,
            "official_dataset_delivery": False,
            "downstream_consumption": False,
        },
        "hard_boundaries": {
            "interface_executions": 0,
            "new_market_state_requests_created": 0,
            "new_event_state_requests_created": 0,
            "new_runtime_builds_executed": 0,
            "materializer_executions": 0,
            "source_market_data_rows_read": 0,
            "physical_state_rows_delivered": 0,
            "datasets_written": 0,
            "registry_mutations": 0,
            "state_replay_feed_records_emitted": 0,
            "backtest_runs_started": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
            "backtest_consumption": False,
        },
        "next_gate_if_closed": NEXT_GATE,
    }


def create_artifacts(now: str, scope: dict[str, Any]) -> list[Path]:
    artifacts: list[Path] = []

    auth_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_authorization_v0_1.md"
    auth = f"""# Runtime User Invocation Bounded Interface Execution Authorization v0.1

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`

## Purpose

Authorize a bounded behavior test of the provider-side runtime invocation
interface.

This authorization is limited to control-plane behavior:

```text
validate request
normalize request
fingerprint request
resolve capability/effective policy
lookup candidate registry metadata
return governed reference or fail-closed decision
```

It does not authorize physical state row delivery, `StateReplayFeed`, backtest
execution, downstream consumption, production, new dataset materialization or
official dataset promotion.

## Authorized Cases

```text
1. Market State exact reuse hit -> governed reference only
2. Event State exact reuse hit -> governed reference only
3. halt_resumed Event State request -> blocked
4. new candidate request without execution authorization -> authorization_required
5. production/downstream request -> blocked
6. user supplied physical path -> blocked
7. partial candidate coverage -> unavailable contexts preserved
8. reuse hit -> zero build, zero source reads, zero registry mutations
```

## Boundaries

```text
interface_executions = 0
runtime_materializations = 0
physical_state_rows_delivered = 0
backtest_runs_started = 0
StateReplayFeed records emitted = 0
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

The next gate may execute the bounded interface test under this scope:

```text
{NEXT_GATE}
```
"""
    write_text(auth_path, auth)
    artifacts.append(auth_path)

    scope_path = CONFIGS / "runtime_user_invocation_bounded_interface_execution_scope_v0_1.json"
    write_json(scope_path, scope)
    artifacts.append(scope_path)

    contract_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_contract_v0_1.json"
    contract = {
        "contract_id": "runtime_user_invocation_bounded_interface_execution_contract_v0_1",
        "contract_version": "0.1",
        "status": "AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION",
        "owner_layer": "08_RUNTIME_CAPABILITIES",
        "governed_gate": GATE,
        "execution_gate_authorized_next": NEXT_GATE,
        "required_response_contract": "runtime_user_invocation_response_contract_v0_1",
        "required_request_contract": "state_resolution_request_contract_v0_1",
        "required_bundle_contract": "state_bundle_manifest_contract_v0_1",
        "required_effective_view_contract": "runtime_capability_effective_view_contract_v0_1",
        "test_case_count": len(scope["test_cases_authorized"]),
        "allowed_resolution_decisions": [
            "VALID_REQUEST_REUSE_HIT",
            "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED",
            "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE",
            "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED",
            "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED",
            "BLOCKED_PROVIDER_CONTRACT_MISMATCH",
        ],
        "must_remain_zero": [
            "new_runtime_builds_executed",
            "materializer_executions_for_reuse_hit",
            "source_market_data_rows_read_for_reuse_hit",
            "registry_mutations",
            "physical_state_rows_delivered",
            "state_replay_feed_records_emitted",
            "backtest_runs_started",
        ],
        "forbidden_outputs": [
            "raw_rows",
            "parquet_bytes",
            "free_physical_path",
            "official_dataset",
            "downstream_authority",
            "backtest_consumption_authority",
        ],
        "closure_requirements_for_execution_gate": [
            "one response artifact per authorized case",
            "all responses validate against runtime_user_invocation_response_contract_v0_1",
            "reuse hit cases include StateBundleManifest reference and no materializer/source/registry mutation evidence",
            "blocked cases contain no dataset_id, no artifact references and no authorization reference",
            "partial coverage case preserves represented and unavailable context counts",
            "final readout reconciles all cases",
        ],
    }
    write_json(contract_path, contract)
    artifacts.append(contract_path)

    readout_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_authorization_readout_v0_1.md"
    readout = f"""# Runtime User Invocation Bounded Interface Execution Authorization Readout v0.1

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{STATUS}`

## Verdict

```text
PROVIDER_CONTROL_PLANE = READY_FOR_BOUNDED_BEHAVIOR_TEST
AUTHORIZED_TEST_CASES = {len(scope["test_cases_authorized"])}
RUNTIME_BUILDS_AUTHORIZED = false
PHYSICAL_ROW_DELIVERY_AUTHORIZED = false
BACKTEST_STATE_CONSUMPTION_AUTHORIZED = false
STATE_REPLAY_FEED_AUTHORIZED = false
PRODUCTION = false
DOWNSTREAM = false
```

This gate authorizes the next bounded interface execution test only. It does
not authorize building new Market State or Event State candidates, delivering
rows to a consumer, starting a backtest or opening downstream usage.

## Next Gate

```text
{NEXT_GATE}
```
"""
    write_text(readout_path, readout)
    artifacts.append(readout_path)

    return artifacts


def update_docs(now: str) -> list[Path]:
    updated: list[Path] = []

    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    route_text = read_text(route)
    route_text = replace_line(route_text, "Status:", "Status: `route_v1_39_bounded_interface_execution_authorized`")
    route_text = replace_line(route_text, "Current gate:", f"Current gate: `{NEXT_GATE}`")
    route_block = f"""## Runtime User Invocation Bounded Interface Execution Authorization {now[:10]}

```text
{GATE}
=
{STATUS}
```

Authorized next action:

```text
{NEXT_GATE}
```

Scope:

```text
Market State exact reuse hit -> governed reference only
Event State exact reuse hit -> governed reference only
unsupported Event Type halt_resumed -> blocked
new candidate without execution authorization -> authorization_required
production/downstream request -> blocked
physical path input -> blocked
partial coverage -> preserved as partial
reuse hit -> zero build / zero source rows / zero registry mutation
```

Still closed:

```text
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
physical_rows_delivered = false
official_dataset = false
production = false
downstream = false
```
"""
    route_text = insert_after_first(route_text, "Current gate: `runtime_user_invocation_bounded_interface_execution_authorization_v0_1`", route_block)
    write_text(route, route_text)
    updated.append(route)

    agent = FEATURE_ROOT / "AGENT.md"
    agent_text = read_text(agent)
    override = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Current Runtime Handoff Override - Bounded Interface Execution Authorized

Status: `agent_handoff_prompt_v0_126`
Date: `{now[:10]}`

```text
current_gate = {NEXT_GATE}
last_closed_gate = {GATE}
last_closed_run_id = none_authorization_gate
last_closed_status = {STATUS}
provider_control_plane = READY_FOR_BOUNDED_BEHAVIOR_TEST
provider_consumer_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
authorized_test_cases = 8
runtime_builds_authorized = false
physical_row_delivery = false
backtest_state_consumption_authority = false
state_replay_feed_authority = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Next gate:

```text
{NEXT_GATE}
```

The next gate may execute bounded provider interface behavior tests only. It
must not build datasets, start a backtest, open StateReplayFeed, deliver state
rows, promote official datasets or authorize downstream consumption.

"""
    if "Bounded Interface Execution Authorized" not in agent_text:
        agent_text = override + agent_text
    write_text(agent, agent_text)
    updated.append(agent)

    readme = RUNTIME / "README.md"
    readme_text = read_text(readme)
    readme_text = replace_line(readme_text, "Status:", "Status: `runtime_user_invocation_bounded_interface_execution_authorized_v0_1`")
    readme_text = replace_line(readme_text, "Current gate:", f"Current gate: `{NEXT_GATE}`")
    readme_block = f"""## Runtime User Invocation Bounded Interface Execution Authorization v0.1

Closed authorization gate:

```text
{GATE}
=
{STATUS}
```

The next gate may run a bounded provider-side interface behavior test. The test
is limited to validation, resolution, reuse/reference decisions and blocked
responses.

Still not authorized:

```text
runtime builds
physical state row delivery
StateReplayFeed
backtest state consumption
production
downstream
official dataset delivery
```
"""
    readme_text = insert_after_first(readme_text, "Runtime evidence in this folder is candidate/runtime evidence unless a later\ngate explicitly promotes it.", readme_block)
    write_text(readme, readme_text)
    updated.append(readme)

    changelog = FEATURE_ROOT / "CHANGELOG.md"
    changelog_text = read_text(changelog) if changelog.exists() else "# Changelog\n"
    entry = f"""## {now[:10]} - Runtime User Invocation Bounded Interface Execution Authorization

- Closed `{GATE}` as `{STATUS}`.
- Authorized bounded provider-side interface behavior tests for reuse hits, blocked unsupported requests, authorization-required requests, physical-path rejection and partial coverage preservation.
- Kept `StateReplayFeed`, backtest state consumption, physical row delivery, production, downstream and official dataset delivery closed.
- Set next gate to `{NEXT_GATE}`.
"""
    if "Runtime User Invocation Bounded Interface Execution Authorization" not in changelog_text:
        changelog_text = changelog_text.rstrip() + "\n\n" + entry
        write_text(changelog, changelog_text)
        updated.append(changelog)

    return updated


def create_provider_zip(now: str, artifacts: list[Path], updated: list[Path]) -> Path:
    zip_path = FEATURE_ROOT / f"runtime_user_invocation_bounded_interface_execution_authorization_provider_only_{now.replace('-', '').replace(':', '').replace('+00:00', 'Z')}.zip"
    files = [
        FEATURE_ROOT / "99_ruta_de_trabajo.md",
        FEATURE_ROOT / "AGENT.md",
        RUNTIME / "README.md",
        RUNTIME / "runtime_user_invocation_interface_design_v0_1.md",
        RUNTIME / "runtime_user_invocation_interface_design_readout_v0_1.md",
        RUNTIME / "runtime_provider_contract_schema_hardening_readout_v0_1.md",
        RUNTIME / "runtime_provider_consumer_contract_compatibility_review_readout_v0_1.md",
        RUNTIME / "runtime_provider_consumer_contract_compatibility_review_matrix_v0_1.json",
        RUNTIME / "state_resolution_request_contract_v0_1.json",
        RUNTIME / "runtime_user_invocation_interface_contract_v0_1.json",
        RUNTIME / "runtime_user_invocation_response_contract_v0_1.json",
        RUNTIME / "runtime_capability_effective_view_contract_v0_1.json",
        RUNTIME / "state_bundle_manifest_contract_v0_1.json",
        RUNTIME / "runtime_capability_registry_snapshot_v0_1.json",
        RUNTIME / "market_state_request_contract_v0_1.json",
        RUNTIME / "event_state_request_contract_v0_1.json",
        SCRIPTS / "runtime_user_invocation_bounded_interface_execution_authorization_runner_v0_1.py",
    ]
    files.extend(artifacts)
    unique = []
    seen = set()
    for path in files:
        if path.exists() and path not in seen:
            unique.append(path)
            seen.add(path)

    manifest = {
        "package_id": "runtime_user_invocation_bounded_interface_execution_authorization_provider_only",
        "created_at_utc": now,
        "scope": "provider_only_runtime_capabilities",
        "gate": GATE,
        "status": STATUS,
        "entry_count_excluding_manifest": len(unique),
        "explicitly_excluded": [
            "02_TSIS_BACKTEST_ENGINE consumer implementation files",
            "StateReplayFeed implementation files",
            "backtest run outputs",
            "parquet files",
            "physical market data",
        ],
        "entries": [file_ref(path) for path in unique],
    }
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in unique:
            zf.write(path, rel(path))
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return zip_path


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    scope = build_scope(now)
    artifacts = create_artifacts(now, scope)
    updated = update_docs(now)
    zip_path = create_provider_zip(now, artifacts, updated)
    print(
        json.dumps(
            {
                "gate": GATE,
                "status": STATUS,
                "next_gate": NEXT_GATE,
                "artifacts": [rel(p) for p in artifacts],
                "updated_docs": [rel(p) for p in updated],
                "provider_only_zip": str(zip_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
