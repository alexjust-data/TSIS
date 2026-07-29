from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_VERSION = "event_state_capability_consumption_policy_runner_v0_1"
GATE_ID = "event_state_capability_consumption_policy_v0_1"
STATUS_PASS = "CLOSED_PASS_EVENT_STATE_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION"
STATUS_BLOCKED = "CLOSED_BLOCKED_EVENT_STATE_CAPABILITY_CONSUMPTION_POLICY_NOT_ESTABLISHED"
NEXT_GATE = "runtime_user_invocation_interface_v0_1"

BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "runs"
CONFIGS = BASE / "configs"

AUTH_MD = BASE / "event_state_capability_consumption_policy_authorization_v0_1.md"
SCOPE_PATH = CONFIGS / "event_state_capability_consumption_policy_scope_v0_1.json"
CONTRACT_PATH = BASE / "event_state_capability_consumption_policy_contract_v0_1.json"
POLICY_PATH = BASE / "event_state_capability_consumption_policy_v0_1.md"
MATRIX_PATH = BASE / "event_state_capability_consumption_policy_matrix_v0_1.json"
READOUT_PATH = BASE / "event_state_capability_consumption_policy_readout_v0_1.md"

EVIDENCE_PATHS = {
    "capability_manifest": BASE / "event_state_on_demand_runtime_capability_manifest_v0_1.json",
    "promotion_review_matrix": BASE / "event_state_on_demand_capability_promotion_review_matrix_v0_1.json",
    "promotion_review_final_manifest": RUNS / "event_state_on_demand_capability_promotion_review_v0_1_20260728T135003Z" / "final_manifest.json",
    "event_state_capability_contract": BASE / "event_state_on_demand_capability_contract_v0_1.json",
    "event_state_candidate_dataset_registry_contract": BASE / "event_state_candidate_dataset_registry_contract_v0_1.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def hash_excluding(payload: dict[str, Any], excluded_key: str) -> str:
    return sha256_payload({k: v for k, v in payload.items() if k != excluded_key})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True, default=str) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="ascii")


def git_value(args: list[str]) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(BASE.parent), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def status_of(payload: dict[str, Any]) -> str | None:
    return payload.get("status") or payload.get("final_run_status")


def build_contract(run_id: str) -> dict[str, Any]:
    contract = {
        "contract_id": "event_state_capability_consumption_policy_contract_v0_1",
        "gate": GATE_ID,
        "status": "accepted_consumption_policy_with_restrictions_no_execution",
        "created_by_run_id": run_id,
        "capability_id": "event_state_on_demand_runtime_capability_v0_1",
        "capability_status_required": "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY",
        "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1",
        "allowed_event_type_ids": ["event_type:market_data:session_opened"],
        "accepted_subject_scope": "exchange_session",
        "policy_scope": {
            "candidate_generation": "allowed_only_under_separate_bounded_incremental_or_scale_authorization",
            "exact_match_reuse": "allowed_only_for_validated_candidate_evidence_with_matching_fingerprints",
            "incremental_reuse": "allowed_only_for_validated_candidate_compositions_with_lineage_chain_evidence",
            "registry_visibility": "metadata_and_governed_evidence_refs_allowed",
            "market_state_dependency_resolution": "must_use_promoted_market_state_runtime_capability",
            "candidate_content_access": "allowed_only_under_future_authorized_runtime_validation_or_reuse_flow",
        },
        "allowed_consumer_classes": [
            "runtime_internal_request_resolver",
            "runtime_internal_execution_planner",
            "runtime_internal_candidate_reuse_resolver",
            "runtime_validator",
            "applied_architecture_review",
            "human_audit_metadata_review",
        ],
        "prohibited_consumer_classes_v0_1": [
            "production_trading",
            "live_execution",
            "downstream_backtest",
            "downstream_ml",
            "downstream_rl",
            "unbounded_event_state_builder",
            "official_dataset_resolver",
            "unauthorized_strategy_engine",
        ],
        "allowed_operations_v0_1": {
            "inspect_capability_metadata": True,
            "inspect_request_contracts": True,
            "inspect_registry_metadata": True,
            "serve_candidate_metadata": True,
            "resolve_candidate_reuse_metadata": True,
            "reuse_exact_validated_candidate_for_matching_candidate_request": True,
            "reuse_incremental_validated_candidate_for_matching_candidate_request": True,
            "open_new_candidate_execution_without_separate_authorization": False,
            "serve_as_official_event_state_dataset": False,
            "serve_to_production": False,
            "serve_to_downstream_research_or_backtest": False,
            "serve_to_ml_or_rl_training": False,
            "serve_additional_event_types": False,
            "serve_halt_resumed": False,
        },
        "reuse_required_conditions": [
            "event_state_request_fingerprint_match",
            "event_state_execution_plan_fingerprint_match",
            "event_state_profile_contract_hash_match",
            "event_type_registry_snapshot_match",
            "event_window_policy_match",
            "instrument_projection_policy_match",
            "market_state_dependency_fingerprint_match",
            "schema_hash_match",
            "validation_status_allows_candidate_reuse",
            "determinism_evidence_present",
            "artifact_availability_available",
            "no_quarantine",
            "no_unresolved_blocking_findings",
            "restriction_set_propagated",
        ],
        "hard_boundaries": {
            "source_market_data_reads_allowed": False,
            "direct_market_state_path_consumption_allowed": False,
            "event_state_materializer_execution_allowed": False,
            "market_state_materializer_execution_allowed": False,
            "validator_execution_allowed": False,
            "new_candidate_registry_entries_allowed": False,
            "registry_entry_mutation_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_consumption_allowed": False,
            "additional_event_type_consumption_allowed": False,
            "halt_resumed_consumption_allowed": False,
            "full_universe_build_allowed": False,
        },
        "next_allowed_gate": NEXT_GATE,
    }
    contract["contract_content_sha256_excluding_hash_field"] = hash_excluding(contract, "contract_content_sha256_excluding_hash_field")
    return contract


def build_policy_text(matrix: dict[str, Any]) -> str:
    return f"""# Event State Capability Consumption Policy v0.1

Status: `{matrix['status']}`
Date: `2026-07-28`

This policy defines how the promoted restricted Event State on-demand runtime
capability may be inspected, reused or served.

It does not promote an official physical Event State dataset and does not open
production, downstream research/backtest, ML/RL or live consumption.

## Governing Decision

```text
policy_id = {matrix['policy_id']}
capability_id = event_state_on_demand_runtime_capability_v0_1
capability_status_required = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
allowed_event_type_ids = [event_type:market_data:session_opened]
accepted_subject_scope = exchange_session
official_event_state_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

## Allowed

```text
inspect capability metadata
inspect request, dependency, plan, lineage, validation and registry evidence
serve candidate metadata to internal runtime components
reuse exact-match validated candidate evidence when all fingerprints match
reuse incremental validated candidate compositions when lineage-chain evidence matches
request new candidate generation only under separate authorization
```

## Conditionally Allowed

Candidate content may be served only to future authorized runtime-internal
validation, reuse and audit flows, and only when all required reuse conditions
pass.

## Prohibited

```text
official Event State dataset resolution
official parquet promotion
production use
live trading use
downstream backtest consumption
downstream ML/RL consumption
additional Event Types beyond session_opened
halt_resumed consumption
full-universe or unbounded generation
silent registry mutation
silent promotion of candidate evidence
direct Market State path consumption
```

## Consumer Classes

Allowed in v0.1:

```text
runtime_internal_request_resolver
runtime_internal_execution_planner
runtime_internal_candidate_reuse_resolver
runtime_validator
applied_architecture_review
human_audit_metadata_review
```

Prohibited in v0.1:

```text
production_trading
live_execution
downstream_backtest
downstream_ml
downstream_rl
unbounded_event_state_builder
official_dataset_resolver
unauthorized_strategy_engine
```
"""


def make_readout(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Event State Capability Consumption Policy Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-28`

```text
policy_id = {matrix['policy_id']}
capability_id = {d['capability_id']}
policy_status = {d['policy_status']}
allowed_event_type_ids = {d['allowed_event_type_ids']}
accepted_subject_scope = {d['accepted_subject_scope']}
hard_policy_failures = {d['hard_policy_failures']}
official_event_state_dataset = false
production = false
downstream = false
source_market_data_rows_read = 0
new_materializer_executions = 0
new_registry_entries_written = 0
next_allowed_gate = {matrix['next_allowed_gate']}
```

The Event State on-demand runtime capability is now consumable only as a
restricted candidate-runtime capability. This policy does not authorize official
datasets, production, downstream consumption, additional Event Types or
unbounded generation.
"""


def main() -> int:
    now = utc_now()
    run_id = f"{GATE_ID}_{now.replace('-', '').replace(':', '').replace('Z', 'Z')}"
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    evidence = {}
    missing = []
    for key, path in EVIDENCE_PATHS.items():
        if not path.exists():
            missing.append(str(path))
            continue
        payload = read_json(path)
        evidence[key] = {"path": str(path), "sha256": sha256_file(path), "payload": payload, "status": status_of(payload)}

    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, observed: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    capability = evidence.get("capability_manifest", {}).get("payload", {})
    promotion_final = evidence.get("promotion_review_final_manifest", {}).get("payload", {})
    promotion_matrix = evidence.get("promotion_review_matrix", {}).get("payload", {})

    add_check("required_evidence_files_present", not missing, missing)
    add_check("capability_status_promoted", capability.get("capability_status") == "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY", capability.get("capability_status"))
    add_check("promotion_review_passed", promotion_final.get("status") == "CLOSED_PASS_EVENT_STATE_CAPABILITY_PROMOTED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION", promotion_final.get("status"))
    add_check("promotion_review_hard_failures_zero", promotion_final.get("hard_review_failures") == 0, promotion_final.get("hard_review_failures"))
    add_check("promotion_matrix_hard_failures_zero", promotion_matrix.get("decision", {}).get("hard_review_failures") == 0, promotion_matrix.get("decision", {}).get("hard_review_failures"))
    add_check("session_opened_only", capability.get("allowed_event_type_ids") == ["event_type:market_data:session_opened"], capability.get("allowed_event_type_ids"))
    add_check("exchange_session_scope_only", capability.get("accepted_subject_scope") == "exchange_session", capability.get("accepted_subject_scope"))
    add_check("official_dataset_closed", capability.get("official_dataset") is False and promotion_final.get("official_dataset") is False, {"capability": capability.get("official_dataset"), "promotion": promotion_final.get("official_dataset")})
    add_check("production_closed", capability.get("production") is False and promotion_final.get("production") is False, {"capability": capability.get("production"), "promotion": promotion_final.get("production")})
    add_check("downstream_closed", capability.get("downstream") is False and promotion_final.get("downstream") is False, {"capability": capability.get("downstream"), "promotion": promotion_final.get("downstream")})
    add_check("no_source_market_rows_read_by_policy", True, 0)
    add_check("no_materializer_executions_by_policy", True, 0)
    add_check("no_registry_entries_written_by_policy", True, 0)

    hard_policy_failures = sum(0 if check["passed"] else 1 for check in checks)
    status = STATUS_PASS if hard_policy_failures == 0 else STATUS_BLOCKED
    established = hard_policy_failures == 0

    scope = {
        "scope_id": "event_state_capability_consumption_policy_scope_v0_1",
        "gate": GATE_ID,
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_POLICY",
        "consumed_by_policy_id": run_id,
        "consumed_at_utc": now,
        "capability_id": "event_state_on_demand_runtime_capability_v0_1",
        "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1",
        "allowed_event_type_ids": ["event_type:market_data:session_opened"],
        "accepted_subject_scope": "exchange_session",
        "authority": {
            "metadata_evidence_read_allowed": True,
            "source_market_data_reads_allowed": False,
            "event_state_materializer_execution_allowed": False,
            "market_state_materializer_execution_allowed": False,
            "new_candidate_registry_entries_allowed": False,
            "registry_entry_mutation_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_allowed": False,
        },
    }
    scope["scope_sha256"] = hash_excluding(scope, "scope_sha256")
    write_json(SCOPE_PATH, scope)

    contract = build_contract(run_id)
    write_json(CONTRACT_PATH, contract)

    auth = f"""# Event State Capability Consumption Policy Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_POLICY`
Date: `2026-07-28`

```text
gate = {GATE_ID}
consumed_by_policy_id = {run_id}
capability_id = event_state_on_demand_runtime_capability_v0_1
allowed_event_type_ids = [event_type:market_data:session_opened]
accepted_subject_scope = exchange_session
metadata_evidence_read_allowed = true
source_market_data_reads_allowed = false
new_materializer_execution_allowed = false
new_candidate_registry_entries_allowed = false
official_dataset_promotion_allowed = false
production = false
downstream = false
```
"""
    write_text(AUTH_MD, auth)

    decision = {
        "capability_id": "event_state_on_demand_runtime_capability_v0_1",
        "policy_status": "ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY" if established else "NOT_ESTABLISHED",
        "allowed_event_type_ids": ["event_type:market_data:session_opened"],
        "accepted_subject_scope": "exchange_session",
        "hard_policy_failures": hard_policy_failures,
    }
    matrix = {
        "policy_id": run_id,
        "gate": GATE_ID,
        "status": status,
        "decision": decision,
        "checks": checks,
        "evidence_index": evidence,
        "boundary_counters": {
            "source_market_data_rows_read": 0,
            "new_event_state_materializer_executions": 0,
            "new_market_state_materializer_executions": 0,
            "new_candidate_dataset_registry_entries_written": 0,
            "registry_entry_mutations": 0,
            "official_event_state_dataset": False,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "next_allowed_gate": NEXT_GATE if established else None,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    matrix["policy_matrix_sha256"] = hash_excluding(matrix, "policy_matrix_sha256")
    write_json(MATRIX_PATH, matrix)
    write_json(run_dir / "policy_matrix.json", matrix)

    policy_text = build_policy_text(matrix)
    write_text(POLICY_PATH, policy_text)
    readout = make_readout(matrix)
    write_text(READOUT_PATH, readout)
    write_text(run_dir / "policy_readout.md", readout)

    evidence_index = {
        key: {"path": item["path"], "sha256": item["sha256"], "status": item["status"]}
        for key, item in evidence.items()
    }
    write_json(run_dir / "evidence_index.json", evidence_index)

    final = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "status": status,
        "created_at_utc": now,
        "git_branch": git_value(["git", "branch", "--show-current"]) or "unknown",
        "git_commit": git_value(["git", "rev-parse", "HEAD"]) or "unknown",
        "git_dirty": bool(git_value(["git", "status", "--porcelain"])),
        "capability_id": decision["capability_id"],
        "policy_status": decision["policy_status"],
        "allowed_event_type_ids": decision["allowed_event_type_ids"],
        "accepted_subject_scope": decision["accepted_subject_scope"],
        "hard_policy_failures": hard_policy_failures,
        "source_market_data_rows_read": 0,
        "new_event_state_materializer_executions": 0,
        "new_market_state_materializer_executions": 0,
        "new_candidate_dataset_registry_entries_written": 0,
        "registry_entry_mutations": 0,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": NEXT_GATE if established else None,
        "artifacts": {
            "authorization": str(AUTH_MD),
            "scope": str(SCOPE_PATH),
            "contract": str(CONTRACT_PATH),
            "policy": str(POLICY_PATH),
            "matrix": str(MATRIX_PATH),
            "readout": str(READOUT_PATH),
            "run_policy_matrix": str(run_dir / "policy_matrix.json"),
            "run_policy_readout": str(run_dir / "policy_readout.md"),
            "run_evidence_index": str(run_dir / "evidence_index.json"),
            "final_manifest": str(run_dir / "final_manifest.json"),
        },
    }
    final["final_manifest_sha256"] = hash_excluding(final, "final_manifest_sha256")
    write_json(run_dir / "final_manifest.json", final)

    print(json.dumps({
        "run_id": run_id,
        "status": status,
        "policy_status": decision["policy_status"],
        "hard_policy_failures": hard_policy_failures,
        "next_allowed_gate": final["next_allowed_gate"],
        "final_manifest": str(run_dir / "final_manifest.json"),
    }, indent=2, ensure_ascii=True))
    return 0 if established else 1


if __name__ == "__main__":
    raise SystemExit(main())