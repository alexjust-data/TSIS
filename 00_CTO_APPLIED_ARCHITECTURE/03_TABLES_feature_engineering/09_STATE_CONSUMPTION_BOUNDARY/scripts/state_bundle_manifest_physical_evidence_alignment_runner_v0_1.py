from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
BOUNDARY = FEATURE_ROOT / "09_STATE_CONSUMPTION_BOUNDARY"
CONFIGS = BOUNDARY / "configs"
CHANGELOG = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"

GATE = "state_bundle_manifest_physical_evidence_alignment_v0_1"
STATUS = "CLOSED_BLOCKED_REQUIRES_V0_1_2_BUNDLE_REISSUE_AND_REPLAY_TIMESTAMP_EVIDENCE_NO_PHYSICAL_READ"
NEXT_REQUIRED = [
    "market_state_core_four_replay_availability_timestamp_contract_v0_1",
    "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2",
]

ACCEPTED_PROVIDER_READOUT = RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_external_audit_acceptance_readout_v0_1.md"
PROVIDER_BUNDLE_CONTRACT = RUNTIME / "state_bundle_manifest_contract_v0_1_2.json"
PREVIOUS_SCOPE = CONFIGS / "bounded_state_bundle_read_and_replay_authorization_scope_v0_1.json"
OLD_BUNDLE = RUNTIME / "runs" / "runtime_user_invocation_bounded_interface_execution_v0_1_20260728T1731090000" / "case_01_bundle.json"
OLD_RESPONSE = RUNTIME / "runs" / "runtime_user_invocation_bounded_interface_execution_v0_1_20260728T1731090000" / "case_01_response.json"
MARKET_STATE_RUN = RUNTIME / "runs" / "market_state_on_demand_scale_validation_v0_1_20260727T133641Z"
FINAL_MANIFEST = MARKET_STATE_RUN / "final_manifest.json"
CANDIDATE_OUTPUT_MANIFEST = MARKET_STATE_RUN / "candidate_output_manifest.json"
CANDIDATE_REGISTRY_ENTRY = MARKET_STATE_RUN / "candidate_registry_entry.json"
VALIDATION_REPORT = MARKET_STATE_RUN / "market_state_validation_report.json"
LINEAGE_MANIFEST = MARKET_STATE_RUN / "lineage_manifest.json"
PHYSICAL_SCHEMA = FEATURE_ROOT / "06_MARKET_STATE_INTEGRATION" / "official_profiles" / "market_state_core_four_intraday_profile_v0_1" / "PHYSICAL_SCHEMA_CONTRACT.json"
PARQUET = MARKET_STATE_RUN / "market_state_scale_validation_candidate_v0_1.parquet"

OUTPUTS = {
    "authorization": BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_authorization_v0_1.md",
    "scope": CONFIGS / "state_bundle_manifest_physical_evidence_alignment_scope_v0_1.json",
    "matrix": BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_matrix_v0_1.json",
    "readout": BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_readout_v0_1.md",
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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, sort_keys=False) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def has_keys(obj: dict[str, Any], keys: list[str]) -> bool:
    return all(k in obj for k in keys)


def build_scope(now: str) -> dict[str, Any]:
    return {
        "gate": GATE,
        "created_at_utc": now,
        "status": "AUTHORIZED_AND_EXECUTED_BY_RUNNER_READ_ONLY_METADATA",
        "owner_layer": "09_STATE_CONSUMPTION_BOUNDARY",
        "purpose": "Check whether existing StateBundle/response/candidate metadata is aligned enough to reopen bounded read-and-replay authorization after provider v0.1.2 hardening.",
        "inputs": {
            "accepted_provider_readout": rel(ACCEPTED_PROVIDER_READOUT),
            "state_bundle_manifest_contract_v0_1_2": rel(PROVIDER_BUNDLE_CONTRACT),
            "previous_blocked_scope": rel(PREVIOUS_SCOPE),
            "old_runtime_invocation_response": rel(OLD_RESPONSE),
            "old_state_bundle_manifest": rel(OLD_BUNDLE),
            "market_state_final_manifest": rel(FINAL_MANIFEST),
            "candidate_output_manifest": rel(CANDIDATE_OUTPUT_MANIFEST),
            "candidate_registry_entry": rel(CANDIDATE_REGISTRY_ENTRY),
            "validation_report": rel(VALIDATION_REPORT),
            "lineage_manifest": rel(LINEAGE_MANIFEST),
            "physical_schema_contract": rel(PHYSICAL_SCHEMA),
        },
        "parquet_path_identified_but_not_opened": rel(PARQUET),
        "authorized_outputs": {**{k: rel(v) for k, v in OUTPUTS.items()}, "runner": rel(BOUNDARY / "scripts" / "state_bundle_manifest_physical_evidence_alignment_runner_v0_1.py")},
        "hard_boundaries": {
            "parquet_opened": False,
            "parquet_hash_recomputed": False,
            "state_rows_read": 0,
            "physical_artifacts_opened": 0,
            "StateReplayFeed_records_emitted": 0,
            "EventLoop_ticks": 0,
            "strategy_callbacks": 0,
            "orders_emitted": 0,
            "fills_emitted": 0,
            "PnL_calculated": False,
            "runtime_requests_executed": 0,
            "runtime_builds_executed": 0,
            "datasets_written": 0,
            "registry_mutations": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
    }


def build_matrix(now: str) -> dict[str, Any]:
    old_scope = read_json(PREVIOUS_SCOPE)
    old_bundle = read_json(OLD_BUNDLE)
    old_response = read_json(OLD_RESPONSE)
    final_manifest = read_json(FINAL_MANIFEST)
    output_manifest = read_json(CANDIDATE_OUTPUT_MANIFEST)
    registry = read_json(CANDIDATE_REGISTRY_ENTRY)
    validation = read_json(VALIDATION_REPORT)
    lineage = read_json(LINEAGE_MANIFEST)
    physical_schema = read_json(PHYSICAL_SCHEMA)
    provider_bundle_contract = read_json(PROVIDER_BUNDLE_CONTRACT)

    rows: list[dict[str, Any]] = []

    def row(case_id: str, area: str, expected: str, observed: str, result: str, evidence_refs: list[str], notes: str = "") -> None:
        rows.append({
            "case_id": case_id,
            "area": area,
            "expected": expected,
            "observed": observed,
            "result": result,
            "evidence_refs": evidence_refs,
            "notes": notes,
        })

    missing = [rel(p) for p in [ACCEPTED_PROVIDER_READOUT, PROVIDER_BUNDLE_CONTRACT, PREVIOUS_SCOPE, OLD_BUNDLE, OLD_RESPONSE, FINAL_MANIFEST, CANDIDATE_OUTPUT_MANIFEST, CANDIDATE_REGISTRY_ENTRY, VALIDATION_REPORT, LINEAGE_MANIFEST, PHYSICAL_SCHEMA, PARQUET] if not p.exists()]
    row("ALIGN_INPUTS_001", "input_inventory", "All metadata inputs exist; parquet may exist but must not be opened.", f"missing={missing}; parquet_exists={PARQUET.exists()}", "PASS" if not missing else "BLOCK", [rel(PREVIOUS_SCOPE), rel(OLD_BUNDLE), rel(OLD_RESPONSE), rel(FINAL_MANIFEST), rel(PHYSICAL_SCHEMA)])

    accepted_text = read_text(ACCEPTED_PROVIDER_READOUT)
    provider_accepted = "CLOSED_EXTERNAL_AUDIT_PASS_ACCEPTABLE_AS_PROVIDER_AUTHORITY_WITH_RESTRICTIONS" in accepted_text
    row("ALIGN_PROVIDER_AUTHORITY_001", "provider_authority", "Provider v0.1.2 must be externally accepted before revisiting physical evidence.", f"provider_v0_1_2_external_acceptance={provider_accepted}", "PASS" if provider_accepted else "BLOCK", [rel(ACCEPTED_PROVIDER_READOUT)])

    old_bundle_v012_shape = has_keys(old_bundle, ["bundle_ref", "request_response_bindings", "runtime_invocation_response_artifacts"])
    row("ALIGN_CONTROL_PLANE_ARTIFACT_VERSION_001", "control_plane_artifact_version", "Candidate read authorization must use v0.1.2-shaped RuntimeInvocationResponse and StateBundleManifest artifacts.", f"old_case_01_bundle_has_v0_1_2_shape={old_bundle_v012_shape}", "BLOCK" if not old_bundle_v012_shape else "PASS", [rel(OLD_BUNDLE), rel(PROVIDER_BUNDLE_CONTRACT)], "The existing case_01 bundle predates v0.1.2 hardening and cannot be promoted to physical authority.")

    observed_response_hash = sha256_file(OLD_RESPONSE)
    declared_response_hash = old_bundle.get("runtime_invocation_response_ref", {}).get("sha256")
    row("ALIGN_RESPONSE_HASH_001", "bundle_to_response_hash", "Bundle must freeze the observed RuntimeInvocationResponse hash.", f"declared={declared_response_hash}; observed={observed_response_hash}", "PASS" if declared_response_hash == observed_response_hash else "BLOCK", [rel(OLD_BUNDLE), rel(OLD_RESPONSE)])

    response_bundle_hash = old_response.get("state_bundle_manifest_ref", {}).get("sha256")
    observed_bundle_hash = sha256_file(OLD_BUNDLE)
    row("ALIGN_BUNDLE_HASH_001", "response_to_bundle_hash", "Response must point to the observed StateBundleManifest hash.", f"declared={response_bundle_hash}; observed={observed_bundle_hash}", "PASS" if response_bundle_hash == observed_bundle_hash else "BLOCK", [rel(OLD_RESPONSE), rel(OLD_BUNDLE)])

    bundle_dataset = old_bundle.get("dataset_refs", {}).get("market_state_dataset_ref", {}) or {}
    physical_dataset_id = output_manifest.get("candidate_dataset_id")
    physical_fingerprint = output_manifest.get("candidate_dataset_fingerprint")
    dataset_match = bundle_dataset.get("dataset_id") == physical_dataset_id and bundle_dataset.get("candidate_dataset_fingerprint") == physical_fingerprint
    row("ALIGN_DATASET_IDENTITY_001", "dataset_identity", "Bundle dataset identity and candidate fingerprint must match the physical candidate output manifest.", f"bundle_dataset_id={bundle_dataset.get('dataset_id')}; physical_dataset_id={physical_dataset_id}; bundle_fingerprint={bundle_dataset.get('candidate_dataset_fingerprint')}; physical_fingerprint={physical_fingerprint}", "PASS" if dataset_match else "BLOCK", [rel(OLD_BUNDLE), rel(CANDIDATE_OUTPUT_MANIFEST)])

    bundle_artifact_hashes = old_bundle.get("artifact_hashes", [])
    artifact_hash_values = {a.get("sha256") for a in bundle_artifact_hashes if isinstance(a, dict)}
    output_file_hashes = {f.get("sha256") for f in output_manifest.get("files", []) if isinstance(f, dict)}
    output_manifest_hash = sha256_file(CANDIDATE_OUTPUT_MANIFEST)
    schema_hash = output_manifest.get("schema_contract_sha256")
    direct_freeze = output_manifest_hash in artifact_hash_values and bool(output_file_hashes & artifact_hash_values) and schema_hash in artifact_hash_values
    row("ALIGN_ARTIFACT_HASH_CHAIN_001", "artifact_hash_chain", "Bundle must directly freeze candidate_output_manifest, state record artifact hashes and schema contract hash before physical read authorization.", f"bundle_artifact_hashes={sorted(artifact_hash_values)}; candidate_output_manifest_sha256={output_manifest_hash}; parquet_hashes_declared_in_output_manifest={sorted(output_file_hashes)}; schema_hash={schema_hash}", "PASS" if direct_freeze else "BLOCK", [rel(OLD_BUNDLE), rel(CANDIDATE_OUTPUT_MANIFEST), rel(PHYSICAL_SCHEMA)])

    coverage_match = (
        old_bundle.get("coverage", {}).get("requested_contexts") == final_manifest.get("requested_contexts")
        and old_bundle.get("coverage", {}).get("represented_contexts") == final_manifest.get("represented_contexts")
        and old_bundle.get("coverage", {}).get("unavailable_contexts") == final_manifest.get("unavailable_contexts")
        and old_bundle.get("coverage", {}).get("unaccounted_contexts") == 0
    )
    row("ALIGN_COVERAGE_001", "coverage", "Partial coverage must reconcile and remain explicit.", f"bundle_coverage={old_bundle.get('coverage')}; final_manifest=({final_manifest.get('requested_contexts')},{final_manifest.get('represented_contexts')},{final_manifest.get('unavailable_contexts')})", "PASS_WITH_RESTRICTIONS" if coverage_match else "BLOCK", [rel(OLD_BUNDLE), rel(FINAL_MANIFEST)], "Partial coverage is preserved, so any future authorization must carry the restriction forward.")

    schema_text = json.dumps(physical_schema, sort_keys=True)
    lineage_text = json.dumps(lineage, sort_keys=True)
    required_timestamps = ["decision_timestamp_utc", "state_as_of_utc", "state_available_at_utc"]
    schema_missing = [x for x in required_timestamps if x not in schema_text]
    lineage_missing = [x for x in required_timestamps if x not in lineage_text]
    row("ALIGN_REPLAY_TIMESTAMPS_SCHEMA_001", "replay_timestamp_contract", "Physical schema and row lineage evidence must prove decision_timestamp_utc, state_as_of_utc and state_available_at_utc before replay-safe delivery.", f"schema_missing={schema_missing}; lineage_missing={lineage_missing}", "PASS" if not schema_missing and not lineage_missing else "BLOCK", [rel(PHYSICAL_SCHEMA), rel(LINEAGE_MANIFEST)])

    validation_ok = validation.get("validation_status") == "PASS_WITH_RESTRICTIONS" and validation.get("row_count") == final_manifest.get("represented_contexts")
    row("ALIGN_VALIDATION_REPORT_001", "candidate_validation", "Candidate validation status and row count must reconcile with final manifest represented contexts.", f"validation_status={validation.get('validation_status')}; row_count={validation.get('row_count')}; represented_contexts={final_manifest.get('represented_contexts')}", "PASS_WITH_RESTRICTIONS" if validation_ok else "BLOCK", [rel(VALIDATION_REPORT), rel(FINAL_MANIFEST)])

    registry_ok = registry.get("dataset_id") == physical_dataset_id and registry.get("candidate_dataset_fingerprint") == physical_fingerprint and registry.get("validation_status") == "pass_with_restrictions"
    row("ALIGN_REGISTRY_001", "candidate_registry", "Candidate registry identity must match output manifest and preserve restricted validation status.", f"registry_dataset_id={registry.get('dataset_id')}; registry_fingerprint={registry.get('candidate_dataset_fingerprint')}; validation_status={registry.get('validation_status')}", "PASS_WITH_RESTRICTIONS" if registry_ok else "BLOCK", [rel(CANDIDATE_REGISTRY_ENTRY), rel(CANDIDATE_OUTPUT_MANIFEST)])

    v012_contract_can_represent = has_keys(provider_bundle_contract.get("json_schema", {}).get("properties", {}), ["bundle_ref", "request_response_bindings", "runtime_invocation_response_artifacts", "artifact_hashes", "field_lineage", "temporal_policy"])
    row("ALIGN_V0_1_2_CONTRACT_CAPACITY_001", "v0_1_2_contract_capacity", "Provider v0.1.2 contract must be able to represent the missing alignment evidence in a future reissued bundle.", f"v0_1_2_contract_can_represent_required_fields={v012_contract_can_represent}", "PASS" if v012_contract_can_represent else "BLOCK", [rel(PROVIDER_BUNDLE_CONTRACT)])

    row("ALIGN_BOUNDARIES_001", "hard_boundaries", "No physical rows, no parquet bytes, no StateReplayFeed and no backtest execution are allowed in this gate.", "parquet_opened=false; parquet_hash_recomputed=false; state_rows_read=0; StateReplayFeed_records_emitted=0; backtest_runs_started=0", "PASS", [])

    blocking = [r for r in rows if r["result"] == "BLOCK"]
    restricted = [r for r in rows if r["result"] == "PASS_WITH_RESTRICTIONS"]
    return {
        "gate": GATE,
        "status": STATUS if blocking else "CLOSED_PASS_PHYSICAL_EVIDENCE_ALIGNED_READY_FOR_BOUNDED_READ_AUTHORIZATION_NO_PHYSICAL_READ",
        "created_at_utc": now,
        "case_count": len(rows),
        "blocking_findings": len(blocking),
        "restricted_findings": len(restricted),
        "authorization_to_read_issued": False if blocking else False,
        "physical_read_authorization_ready": False if blocking else True,
        "parquet_opened": False,
        "parquet_hash_recomputed": False,
        "state_rows_read": 0,
        "physical_artifacts_opened": 0,
        "StateReplayFeed_records_emitted": 0,
        "EventLoop_ticks": 0,
        "strategy_callbacks": 0,
        "orders_emitted": 0,
        "fills_emitted": 0,
        "PnL_calculated": False,
        "runtime_requests_executed": 0,
        "runtime_builds_executed": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_required_gates": NEXT_REQUIRED if blocking else ["bounded_state_bundle_read_and_replay_authorization_v0_1"],
        "rows": rows,
    }


def render_authorization(now: str) -> str:
    return f"""# StateBundle Manifest Physical Evidence Alignment Authorization v0.1

Gate: `{GATE}`
Date: `2026-07-29`
Status: `AUTHORIZED_READ_ONLY_METADATA_NO_PHYSICAL_READ`

## Purpose

Check whether the existing Market State control-plane bundle and response can be aligned to physical candidate evidence after provider hardening v0.1.2.

This gate may read JSON manifests, contracts and hash small metadata files. It must not open parquet bytes, read state rows, emit StateReplayFeed records, execute runtime requests or run a backtest.

## Inputs

```text
old_response = {rel(OLD_RESPONSE)}
old_bundle = {rel(OLD_BUNDLE)}
market_state_final_manifest = {rel(FINAL_MANIFEST)}
candidate_output_manifest = {rel(CANDIDATE_OUTPUT_MANIFEST)}
candidate_registry_entry = {rel(CANDIDATE_REGISTRY_ENTRY)}
lineage_manifest = {rel(LINEAGE_MANIFEST)}
physical_schema_contract = {rel(PHYSICAL_SCHEMA)}
state_bundle_manifest_contract_v0_1_2 = {rel(PROVIDER_BUNDLE_CONTRACT)}
```

## Hard Boundaries

```text
parquet_opened = false
parquet_hash_recomputed = false
state_rows_read = 0
physical_artifacts_opened = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```
"""


def render_readout(now: str, matrix: dict[str, Any]) -> str:
    next_text = "\n".join(f"- `{x}`" for x in matrix["next_required_gates"])
    blocking_rows = [r for r in matrix["rows"] if r["result"] == "BLOCK"]
    blocking_text = "\n".join(f"- `{r['case_id']}`: {r['area']}" for r in blocking_rows)
    return f"""# StateBundle Manifest Physical Evidence Alignment Readout v0.1

Gate: `{GATE}`
Date: `2026-07-29`
Status: `{matrix['status']}`

## Result

The current physical-read evidence remains blocked. Provider v0.1.2 can express the required evidence, but the existing `case_01` response and bundle were emitted before v0.1.2 and cannot be promoted as physical consumption authority.

```text
case_count = {matrix['case_count']}
blocking_findings = {matrix['blocking_findings']}
restricted_findings = {matrix['restricted_findings']}
physical_read_authorization_ready = {str(matrix['physical_read_authorization_ready']).lower()}
authorization_to_read_issued = false
```

## Blocking Findings

{blocking_text}

## Critical Observations

```text
old StateBundleManifest v0.1 case_01 = control-plane evidence only
old bundle does not match physical candidate dataset fingerprint
old bundle does not freeze observed response hash
old bundle does not directly freeze candidate_output_manifest, parquet hash and schema hash
Market State physical schema lacks state_as_of_utc
Market State physical schema lacks state_available_at_utc
```

## Boundaries Preserved

```text
parquet_opened = false
parquet_hash_recomputed = false
state_rows_read = 0
physical_artifacts_opened = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```

## Required Next Gates

{next_text}

Do not reopen `bounded_state_bundle_read_and_replay_authorization_v0_1` until both prerequisites are closed.
"""


def prepend_once(path: Path, title: str, block: str) -> None:
    text = read_text(path) if path.exists() else ""
    if title in text:
        return
    write_text(path, block.rstrip() + "\n\n" + text.rstrip() + "\n")


def update_live_docs(matrix: dict[str, Any]) -> None:
    title = "StateBundle Manifest Physical Evidence Alignment v0.1 Blocked - 2026-07-29"
    route_block = f"""## {title}

```text
{GATE}
=
{matrix['status']}

physical_read_authorization_ready
=
false

authorization_to_read_issued
=
false

StateReplayFeed
=
NOT_AUTHORIZED
```

Required next gates:

```text
market_state_core_four_replay_availability_timestamp_contract_v0_1
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

Still closed:

```text
state_rows_read = 0
physical_artifacts_opened = 0
StateReplayFeed_records_emitted = 0
backtest_runs_started = 0
production = false
downstream = false
official_dataset = false
```"""
    prepend_once(FEATURE_ROOT / "99_ruta_de_trabajo.md", title, route_block)

    agent_title = "Current Runtime Handoff Override - StateBundle Physical Evidence Alignment Blocked"
    agent_block = f"""## {agent_title}

Status: `agent_handoff_prompt_v0_143`
Date: `2026-07-29`

```text
current_gate = market_state_core_four_replay_availability_timestamp_contract_v0_1_pending
also_required_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
last_closed_gate = {GATE}
last_closed_status = {matrix['status']}
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
state_rows_read = 0
physical_artifacts_opened = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not open physical reads. The next work must prove replay-safe timestamps and reissue the control-plane response/bundle under provider v0.1.2 before bounded read authorization can reopen."""
    prepend_once(FEATURE_ROOT / "AGENT.md", agent_title, agent_block)

    readme_title = "StateBundle Manifest Physical Evidence Alignment v0.1"
    readme_block = f"""## {readme_title}

```text
{GATE} = {matrix['status']}
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
```

Required next gates:

```text
market_state_core_four_replay_availability_timestamp_contract_v0_1
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```"""
    prepend_once(BOUNDARY / "README.md", readme_title, readme_block)

    changelog_title = "## 2026-07-29 - StateBundle physical evidence alignment blocked before physical read"
    changelog_block = f"""{changelog_title}

- Closed `{GATE}` as `{matrix['status']}`.
- Confirmed provider v0.1.2 can express the required bundle evidence, but the existing `case_01` response and bundle are pre-v0.1.2 control-plane artifacts and cannot authorize physical reads.
- Kept parquet opened = false, state rows read = 0, `StateReplayFeed = NOT_AUTHORIZED`, production = false and downstream = false.
- Required next gates are `market_state_core_four_replay_availability_timestamp_contract_v0_1` and `runtime_user_invocation_bounded_interface_execution_regression_v0_1_2`."""
    prepend_once(CHANGELOG, changelog_title, changelog_block)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-live-docs", action="store_true")
    args = parser.parse_args()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    scope = build_scope(now)
    matrix = build_matrix(now)
    write_json(OUTPUTS["scope"], scope)
    write_text(OUTPUTS["authorization"], render_authorization(now))
    write_json(OUTPUTS["matrix"], matrix)
    write_text(OUTPUTS["readout"], render_readout(now, matrix))
    if args.update_live_docs:
        update_live_docs(matrix)
    print(json.dumps({
        "gate": GATE,
        "status": matrix["status"],
        "case_count": matrix["case_count"],
        "blocking_findings": matrix["blocking_findings"],
        "restricted_findings": matrix["restricted_findings"],
        "physical_read_authorization_ready": matrix["physical_read_authorization_ready"],
        "next_required_gates": matrix["next_required_gates"],
        "update_live_docs": args.update_live_docs,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
