from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "market_state_capability_consumption_policy_runner_v0_1"
GATE_ID = "market_state_capability_consumption_policy_v0_1"
STATUS_PASS = "CLOSED_PASS_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION"
STATUS_BLOCKED = "CLOSED_BLOCKED_CAPABILITY_CONSUMPTION_POLICY_NOT_ESTABLISHED"
NEXT_GATE = "event_state_on_demand_capability_design_authorization_v0_1"

BASE = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = BASE / "runs"

AUTH_MD_PATH = BASE / "market_state_capability_consumption_policy_authorization_v0_1.md"
SCOPE_PATH = BASE / "configs" / "market_state_capability_consumption_policy_scope_v0_1.json"
CONTRACT_PATH = BASE / "market_state_capability_consumption_policy_contract_v0_1.json"
POLICY_PATH = BASE / "market_state_capability_consumption_policy_v0_1.md"
MATRIX_PATH = BASE / "market_state_capability_consumption_policy_matrix_v0_1.json"
READOUT_PATH = BASE / "market_state_capability_consumption_policy_readout_v0_1.md"

EVIDENCE_PATHS = {
    "capability_promotion_matrix": BASE / "market_state_on_demand_capability_promotion_review_matrix_v0_1.json",
    "capability_promotion_final_manifest": BASE
    / "runs"
    / "market_state_on_demand_capability_promotion_review_v0_1_20260727T140338Z"
    / "final_manifest.json",
    "market_state_on_demand_capability_contract": BASE / "market_state_on_demand_capability_contract_v0_1.json",
    "candidate_dataset_registry_contract": BASE / "market_state_candidate_dataset_registry_contract_v0_1.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def hash_excluding(payload: dict[str, Any], excluded_key: str) -> str:
    return sha256_payload({k: v for k, v in payload.items() if k != excluded_key})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
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


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def evidence_value(evidence: dict[str, dict[str, Any]], key: str, path: list[str], default: Any = None) -> Any:
    current: Any = evidence[key]["payload"]
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def build_policy_contract(run_id: str) -> dict[str, Any]:
    contract = {
        "contract_id": "market_state_capability_consumption_policy_contract_v0_1",
        "gate": GATE_ID,
        "status": "accepted_consumption_policy_with_restrictions_no_execution",
        "created_by_run_id": run_id,
        "capability_id": "market_state_on_demand_runtime_capability_v0_1",
        "capability_status_required": "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY",
        "policy_scope": {
            "candidate_generation": "allowed_only_under_separate_bounded_or_scale_authorization",
            "exact_match_reuse": "allowed_only_for_validated_candidate_evidence_with_matching_fingerprints",
            "incremental_reuse": "allowed_only_for_validated_candidate_compositions_with_lineage_chain_evidence",
            "registry_visibility": "metadata_and_governed_evidence_refs_allowed",
            "event_state_dependency_planning": "metadata_only_allowed",
        },
        "allowed_consumer_classes": [
            "runtime_internal_request_resolver",
            "runtime_internal_execution_planner",
            "runtime_internal_candidate_reuse_resolver",
            "runtime_validator",
            "applied_architecture_review",
            "event_state_design_planning_metadata_only",
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
        ],
        "allowed_operations_v0_1": {
            "inspect_capability_metadata": True,
            "inspect_request_contracts": True,
            "inspect_registry_metadata": True,
            "serve_candidate_metadata": True,
            "serve_candidate_files_to_runtime_internal_validation": True,
            "reuse_exact_validated_candidate_for_matching_candidate_request": True,
            "reuse_incremental_validated_candidate_for_matching_candidate_request": True,
            "open_new_candidate_execution_without_separate_authorization": False,
            "serve_as_official_market_state_dataset": False,
            "serve_to_production": False,
            "serve_to_downstream_research_or_backtest": False,
            "serve_to_ml_or_rl_training": False,
            "serve_to_event_state_physical_materialization": False,
        },
        "reuse_required_conditions": [
            "request_fingerprint_match",
            "execution_plan_fingerprint_match",
            "profile_contract_hash_match",
            "source_fingerprint_match",
            "builder_version_match",
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
            "parquet_content_reads_allowed": False,
            "materializer_execution_allowed": False,
            "validator_execution_allowed": False,
            "new_candidate_registry_entries_allowed": False,
            "registry_entry_mutation_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_consumption_allowed": False,
            "event_state_on_demand_execution_allowed": False,
            "full_universe_build_allowed": False,
        },
        "next_allowed_gate": NEXT_GATE,
    }
    contract["contract_content_sha256_excluding_hash_field"] = hash_excluding(
        contract, "contract_content_sha256_excluding_hash_field"
    )
    return contract


def build_policy_text(matrix: dict[str, Any]) -> str:
    return f"""# Market State Capability Consumption Policy v0.1

Status: `{matrix['status']}`
Date: `2026-07-27`

This policy defines how the promoted restricted Market State on-demand runtime
capability may be inspected, reused or served.

It does not promote an official physical Market State dataset and does not open
production, downstream research/backtest, ML/RL or Event State materialization.

## Governing Decision

```text
policy_id = {matrix['policy_id']}
capability_id = market_state_on_demand_runtime_capability_v0_1
capability_status_required = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY
consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
official_dataset = false
production = false
downstream = false
event_state_on_demand_execution = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

## Allowed

```text
inspect capability metadata
inspect request, plan, lineage, validation and registry evidence
serve candidate metadata to internal runtime components
reuse exact-match validated candidate evidence when all fingerprints match
reuse incremental validated candidate compositions when lineage-chain evidence matches
use Market State capability metadata for Event State on-demand planning
```

## Conditionally Allowed

Candidate files may be served only to runtime-internal validation, reuse and
audit flows, and only when all required reuse conditions pass:

```text
request_fingerprint_match
execution_plan_fingerprint_match
profile_contract_hash_match
source_fingerprint_match
builder_version_match
schema_hash_match
validation_status_allows_candidate_reuse
determinism_evidence_present
artifact_availability_available
no_quarantine
no_unresolved_blocking_findings
restriction_set_propagated
```

New candidate generation remains allowed only through a separate bounded,
incremental or scale authorization. This policy never authorizes a build by
itself.

## Prohibited

```text
official Market State dataset resolution
official parquet promotion
production use
live trading use
downstream backtest consumption
downstream ML/RL consumption
Event State physical materialization
full-universe or unbounded generation
silent registry mutation
silent promotion of candidate evidence
```

## Consumer Classes

Allowed in v0.1:

```text
runtime_internal_request_resolver
runtime_internal_execution_planner
runtime_internal_candidate_reuse_resolver
runtime_validator
applied_architecture_review
event_state_design_planning_metadata_only
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
```
"""


def build_readout(matrix: dict[str, Any]) -> str:
    return f"""# Market State Capability Consumption Policy Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-27`

```text
policy_id = {matrix['policy_id']}
capability_status_required = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY
consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
hard_policy_failures = {matrix['decision']['hard_policy_failures']}
allowed_candidate_generation = separate_authorization_required
allowed_exact_reuse = conditional_candidate_runtime_only
allowed_incremental_reuse = conditional_candidate_runtime_only
official_dataset = false
production = false
downstream = false
source_market_data_rows_read = 0
parquet_content_rows_read = 0
materializer_executions = 0
validator_executions = 0
new_candidate_registry_entries_written = 0
datasets_written = 0
next_allowed_gate = {matrix['next_allowed_gate']}
```

The promoted Market State on-demand runtime capability now has an explicit
consumption policy. The policy allows metadata inspection and candidate-runtime
reuse under strict fingerprint, lineage, validation and availability conditions.
It does not authorize official dataset consumption, production or downstream
use.
"""


def main() -> int:
    now = utc_now()
    run_id = f"{GATE_ID}_{now.replace('-', '').replace(':', '').replace('Z', 'Z')}"
    run_dir = OUTPUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    branch = git_value(["git", "branch", "--show-current"], BASE.parent) or "unknown"
    commit = git_value(["git", "rev-parse", "HEAD"], BASE.parent) or "unknown"
    dirty = bool(git_value(["git", "status", "--porcelain"], BASE.parent))

    evidence: dict[str, dict[str, Any]] = {}
    missing_files: list[str] = []
    for key, path in EVIDENCE_PATHS.items():
        if not path.exists():
            missing_files.append(str(path))
            continue
        evidence[key] = {"path": str(path), "sha256": sha256_file(path), "payload": read_json(path)}

    checks: list[tuple[bool, str, str]] = []
    checks.append((not missing_files, "required_evidence_files_present", "; ".join(missing_files)))
    if not missing_files:
        checks.extend(
            [
                (
                    evidence_value(evidence, "capability_promotion_matrix", ["status"])
                    == "CLOSED_PASS_CAPABILITY_PROMOTED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION",
                    "capability_promotion_review_passed",
                    str(evidence_value(evidence, "capability_promotion_matrix", ["status"])),
                ),
                (
                    evidence_value(
                        evidence,
                        "capability_promotion_matrix",
                        ["decision", "capability_status_after_review"],
                    )
                    == "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY",
                    "capability_status_is_restricted_candidate_generation",
                    str(
                        evidence_value(
                            evidence,
                            "capability_promotion_matrix",
                            ["decision", "capability_status_after_review"],
                        )
                    ),
                ),
                (
                    evidence_value(evidence, "capability_promotion_matrix", ["official_dataset"]) is False,
                    "promotion_matrix_official_dataset_false",
                    str(evidence_value(evidence, "capability_promotion_matrix", ["official_dataset"])),
                ),
                (
                    evidence_value(evidence, "capability_promotion_matrix", ["production"]) is False,
                    "promotion_matrix_production_false",
                    str(evidence_value(evidence, "capability_promotion_matrix", ["production"])),
                ),
                (
                    evidence_value(evidence, "capability_promotion_matrix", ["downstream"]) is False,
                    "promotion_matrix_downstream_false",
                    str(evidence_value(evidence, "capability_promotion_matrix", ["downstream"])),
                ),
                (
                    evidence_value(
                        evidence,
                        "market_state_on_demand_capability_contract",
                        ["target_profile", "official_market_state_dataset_exists"],
                    )
                    is False,
                    "target_profile_official_dataset_absent",
                    str(
                        evidence_value(
                            evidence,
                            "market_state_on_demand_capability_contract",
                            ["target_profile", "official_market_state_dataset_exists"],
                        )
                    ),
                ),
                (
                    evidence_value(
                        evidence,
                        "candidate_dataset_registry_contract",
                        ["downstream_eligibility_v0_1"],
                    )
                    is False,
                    "candidate_registry_downstream_eligibility_false",
                    str(
                        evidence_value(
                            evidence,
                            "candidate_dataset_registry_contract",
                            ["downstream_eligibility_v0_1"],
                        )
                    ),
                ),
            ]
        )

    hard_failures = sum(0 if passed else 1 for passed, _, _ in checks)
    status = STATUS_PASS if hard_failures == 0 else STATUS_BLOCKED

    scope = {
        "scope_id": "market_state_capability_consumption_policy_scope_v0_1",
        "gate": GATE_ID,
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_POLICY",
        "consumed_by_policy_id": run_id,
        "consumed_at_utc": now,
        "authority": {
            "metadata_evidence_read_allowed": True,
            "source_market_data_reads_allowed": False,
            "parquet_content_reads_allowed": False,
            "materializer_execution_allowed": False,
            "validator_execution_allowed": False,
            "new_candidate_registry_entries_allowed": False,
            "registry_entry_mutation_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_consumption_allowed": False,
            "event_state_on_demand_execution_allowed": False,
        },
        "next_allowed_gate_on_pass": NEXT_GATE,
    }
    scope["scope_content_sha256_excluding_hash_field"] = hash_excluding(scope, "scope_content_sha256_excluding_hash_field")

    contract = build_policy_contract(run_id)

    matrix = {
        "policy_id": run_id,
        "gate": GATE_ID,
        "status": status,
        "decision": {
            "consumption_policy_decision": "establish_with_restrictions_candidate_runtime_only"
            if hard_failures == 0
            else "block_consumption_policy",
            "consumption_policy_status": "ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY"
            if hard_failures == 0
            else "NOT_ESTABLISHED",
            "hard_policy_failures": hard_failures,
        },
        "checks": [
            {"check_id": check_id, "status": "PASS" if passed else "FAIL", "observed": observed}
            for passed, check_id, observed in checks
        ],
        "allowed_operations": contract["allowed_operations_v0_1"],
        "allowed_consumer_classes": contract["allowed_consumer_classes"],
        "prohibited_consumer_classes_v0_1": contract["prohibited_consumer_classes_v0_1"],
        "reuse_required_conditions": contract["reuse_required_conditions"],
        "evidence": {
            key: {"path": value["path"], "sha256": value["sha256"], "status": value["payload"].get("status")}
            for key, value in evidence.items()
        },
        "counters": {
            "source_market_data_rows_read": 0,
            "parquet_content_rows_read": 0,
            "materializer_executions": 0,
            "validator_executions": 0,
            "new_candidate_registry_entries_written": 0,
            "datasets_written": 0,
            "registry_entry_mutations": 0,
        },
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "event_state_on_demand_execution": False,
        "next_allowed_gate": NEXT_GATE if hard_failures == 0 else None,
    }
    matrix["matrix_sha256"] = hash_excluding(matrix, "matrix_sha256")

    authorization_md = f"""# Market State Capability Consumption Policy Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_POLICY`
Date: `2026-07-27`

```text
policy_id = {run_id}
gate = {GATE_ID}
metadata_evidence_read_allowed = true
source_market_data_reads_allowed = false
parquet_content_reads_allowed = false
materializer_execution_allowed = false
validator_execution_allowed = false
new_candidate_registry_entries_allowed = false
registry_entry_mutation_allowed = false
official_dataset_promotion_allowed = false
production_allowed = false
downstream_consumption_allowed = false
event_state_on_demand_execution_allowed = false
```

This authorization is consumed by the capability consumption policy gate.
"""

    policy_text = build_policy_text(matrix)
    readout = build_readout(matrix)

    final_manifest = {
        "run_id": run_id,
        "gate": GATE_ID,
        "status": status,
        "created_at_utc": now,
        "completed_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": branch,
        "git_commit": commit,
        "git_dirty_state": dirty,
        "consumption_policy_decision": matrix["decision"]["consumption_policy_decision"],
        "consumption_policy_status": matrix["decision"]["consumption_policy_status"],
        "hard_policy_failures": hard_failures,
        "source_market_data_rows_read": 0,
        "parquet_content_rows_read": 0,
        "materializer_executions": 0,
        "validator_executions": 0,
        "new_candidate_registry_entries_written": 0,
        "datasets_written": 0,
        "registry_entry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "event_state_on_demand_execution": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
        "artifacts": {
            "authorization": str(AUTH_MD_PATH),
            "scope": str(SCOPE_PATH),
            "contract": str(CONTRACT_PATH),
            "policy": str(POLICY_PATH),
            "matrix": str(MATRIX_PATH),
            "readout": str(READOUT_PATH),
            "run_readout": str(run_dir / "market_state_capability_consumption_policy_readout_v0_1.md"),
        },
    }

    write_json(SCOPE_PATH, scope)
    write_json(CONTRACT_PATH, contract)
    write_json(MATRIX_PATH, matrix)
    write_text(AUTH_MD_PATH, authorization_md)
    write_text(POLICY_PATH, policy_text)
    write_text(READOUT_PATH, readout)
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_text(run_dir / "market_state_capability_consumption_policy_readout_v0_1.md", readout)

    print(json.dumps(final_manifest, indent=2, ensure_ascii=True))
    return 0 if hard_failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
