from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "market_state_on_demand_capability_promotion_review_runner_v0_1"
GATE_ID = "market_state_on_demand_capability_promotion_review_v0_1"
STATUS_PASS = "CLOSED_PASS_CAPABILITY_PROMOTED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION"
STATUS_BLOCKED = "CLOSED_BLOCKED_CAPABILITY_PROMOTION_REVIEW_NO_PROMOTION"
NEXT_GATE = "market_state_capability_consumption_policy_v0_1"

BASE = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = BASE / "runs"

AUTH_MD_PATH = BASE / "market_state_on_demand_capability_promotion_review_authorization_v0_1.md"
SCOPE_PATH = BASE / "configs" / "market_state_on_demand_capability_promotion_review_scope_v0_1.json"
CONTRACT_PATH = BASE / "market_state_on_demand_capability_promotion_review_contract_v0_1.json"
MATRIX_PATH = BASE / "market_state_on_demand_capability_promotion_review_matrix_v0_1.json"
READOUT_PATH = BASE / "market_state_on_demand_capability_promotion_review_readout_v0_1.md"

EVIDENCE_PATHS = {
    "bounded_execution": BASE / "runs" / "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z" / "final_manifest.json",
    "deterministic_rerun": BASE / "runs" / "market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z" / "final_manifest.json",
    "exact_reuse": BASE / "runs" / "market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z" / "final_manifest.json",
    "incremental_overlap_execution": BASE / "runs" / "market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z" / "final_manifest.json",
    "incremental_overlap_reuse": BASE / "runs" / "market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1_20260727T094006Z" / "final_manifest.json",
    "second_generation_incremental": BASE / "runs" / "market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103901Z" / "final_manifest.json",
    "lineage_chain_validation": BASE / "market_state_on_demand_incremental_lineage_chain_validation_matrix_v0_1.json",
    "scale_validation": BASE / "runs" / "market_state_on_demand_scale_validation_v0_1_20260727T133641Z" / "final_manifest.json",
    "scale_validation_matrix": BASE / "market_state_on_demand_scale_validation_matrix_v0_1.json",
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


def evidence_status(evidence: dict[str, dict[str, Any]], key: str) -> str:
    return str(evidence[key]["payload"].get("status", ""))


def evidence_value(evidence: dict[str, dict[str, Any]], key: str, field: str, default: Any = None) -> Any:
    return evidence[key]["payload"].get(field, default)


def make_readout(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Market State On-Demand Capability Promotion Review Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-27`

```text
review_id = {matrix['review_id']}
capability_id = {d['capability_id']}
capability_promotion_decision = {d['capability_promotion_decision']}
capability_status_after_review = {d['capability_status_after_review']}
reviewed_evidence_items = {d['reviewed_evidence_items']}
scale_requested_contexts = {d['scale_requested_contexts']}
scale_represented_contexts = {d['scale_represented_contexts']}
scale_unavailable_contexts = {d['scale_unavailable_contexts']}
hard_review_failures = {d['hard_review_failures']}
official_dataset = false
production = false
downstream = false
new_materialization_authorized = false
new_registry_entries_written = 0
source_market_data_rows_read = 0
next_allowed_gate = {matrix['next_allowed_gate']}
```

The Market State on-demand runtime capability is promoted only as a restricted
candidate-generation capability. This review does not promote an official
physical Market State dataset, does not authorize production and does not open
downstream ML/RL/backtest consumption.
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
        evidence[key] = {
            "path": str(path),
            "sha256": sha256_file(path),
            "payload": read_json(path),
        }

    checks: list[tuple[bool, str, str]] = []
    checks.append((not missing_files, "required_evidence_files_present", "; ".join(missing_files)))

    if not missing_files:
        checks.extend(
            [
                (
                    evidence_status(evidence, "bounded_execution")
                    == "CLOSED_PASS_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
                    "bounded_build_closed",
                    evidence_status(evidence, "bounded_execution"),
                ),
                (
                    evidence_status(evidence, "deterministic_rerun")
                    == "CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS",
                    "deterministic_rerun_closed",
                    evidence_status(evidence, "deterministic_rerun"),
                ),
                (
                    evidence_status(evidence, "exact_reuse")
                    == "CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS",
                    "exact_reuse_closed",
                    evidence_status(evidence, "exact_reuse"),
                ),
                (
                    evidence_status(evidence, "incremental_overlap_execution")
                    == "CLOSED_PASS_INCREMENTAL_OVERLAP_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
                    "incremental_overlap_closed",
                    evidence_status(evidence, "incremental_overlap_execution"),
                ),
                (
                    evidence_status(evidence, "incremental_overlap_reuse")
                    == "CLOSED_PASS_INCREMENTAL_OVERLAP_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS",
                    "incremental_overlap_reuse_closed",
                    evidence_status(evidence, "incremental_overlap_reuse"),
                ),
                (
                    evidence_status(evidence, "second_generation_incremental")
                    == "CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
                    "second_generation_incremental_closed",
                    evidence_status(evidence, "second_generation_incremental"),
                ),
                (
                    evidence_status(evidence, "lineage_chain_validation")
                    == "CLOSED_PASS_INCREMENTAL_LINEAGE_CHAIN_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION",
                    "lineage_chain_validation_closed",
                    evidence_status(evidence, "lineage_chain_validation"),
                ),
                (
                    evidence_status(evidence, "scale_validation")
                    == "CLOSED_PASS_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
                    "scale_validation_closed",
                    evidence_status(evidence, "scale_validation"),
                ),
                (
                    evidence_value(evidence, "scale_validation", "requested_contexts") == 120,
                    "scale_requested_contexts_120",
                    str(evidence_value(evidence, "scale_validation", "requested_contexts")),
                ),
                (
                    evidence_value(evidence, "scale_validation", "represented_contexts") == 104,
                    "scale_represented_contexts_104",
                    str(evidence_value(evidence, "scale_validation", "represented_contexts")),
                ),
                (
                    evidence_value(evidence, "scale_validation", "unavailable_contexts") == 16,
                    "scale_unavailable_contexts_16",
                    str(evidence_value(evidence, "scale_validation", "unavailable_contexts")),
                ),
                (
                    evidence_value(evidence, "scale_validation", "source_market_data_rows_read") == 0,
                    "no_source_market_data_rows_read_for_scale_validation",
                    str(evidence_value(evidence, "scale_validation", "source_market_data_rows_read")),
                ),
                (
                    all(evidence_value(evidence, key, "official_dataset", False) is False for key in evidence if key != "lineage_chain_validation"),
                    "official_dataset_boundaries_closed",
                    "checked final manifests",
                ),
                (
                    all(evidence_value(evidence, key, "production", False) is False for key in evidence if key != "lineage_chain_validation"),
                    "production_boundaries_closed",
                    "checked final manifests",
                ),
                (
                    all(evidence_value(evidence, key, "downstream", False) is False for key in evidence if key != "lineage_chain_validation"),
                    "downstream_boundaries_closed",
                    "checked final manifests",
                ),
            ]
        )

    hard_failures = sum(0 if passed else 1 for passed, _, _ in checks)
    status = STATUS_PASS if hard_failures == 0 else STATUS_BLOCKED
    promoted = hard_failures == 0

    scope = {
        "scope_id": "market_state_on_demand_capability_promotion_review_scope_v0_1",
        "gate": GATE_ID,
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REVIEW",
        "consumed_by_review_id": run_id,
        "consumed_at_utc": now,
        "authority": {
            "metadata_evidence_read_allowed": True,
            "source_market_data_reads_allowed": False,
            "parquet_content_reads_allowed": False,
            "new_materialization_allowed": False,
            "candidate_registry_mutation_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_consumption_allowed": False,
        },
        "reviewed_gate_chain": list(EVIDENCE_PATHS.keys()),
        "next_allowed_gate_on_pass": NEXT_GATE,
    }
    scope["scope_content_sha256_excluding_hash_field"] = hash_excluding(scope, "scope_content_sha256_excluding_hash_field")

    contract = {
        "contract_id": "market_state_on_demand_capability_promotion_review_contract_v0_1",
        "gate": GATE_ID,
        "contract_status": "accepted_for_metadata_only_capability_promotion_review",
        "consumed_by_review_id": run_id,
        "promotion_target": "market_state_on_demand_runtime_capability_v0_1",
        "promotion_decision_values": [
            "promote_with_restrictions_candidate_generation_only",
            "block_capability_promotion",
        ],
        "required_evidence": list(EVIDENCE_PATHS.keys()),
        "required_boundary_invariants": {
            "new_materialization_authorized": False,
            "source_market_data_rows_read": 0,
            "new_candidate_registry_entries_written": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "next_gate_on_pass": NEXT_GATE,
    }
    contract["contract_content_sha256_excluding_hash_field"] = hash_excluding(contract, "contract_content_sha256_excluding_hash_field")

    matrix = {
        "review_id": run_id,
        "gate": GATE_ID,
        "status": status,
        "decision": {
            "capability_id": "market_state_on_demand_runtime_capability_v0_1",
            "capability_promotion_decision": "promote_with_restrictions_candidate_generation_only" if promoted else "block_capability_promotion",
            "capability_status_after_review": "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY" if promoted else "NOT_PROMOTED",
            "reviewed_evidence_items": len(evidence),
            "scale_requested_contexts": evidence_value(evidence, "scale_validation", "requested_contexts", 0) if evidence else 0,
            "scale_represented_contexts": evidence_value(evidence, "scale_validation", "represented_contexts", 0) if evidence else 0,
            "scale_unavailable_contexts": evidence_value(evidence, "scale_validation", "unavailable_contexts", 0) if evidence else 0,
            "hard_review_failures": hard_failures,
        },
        "checks": [
            {
                "check_id": check_id,
                "status": "PASS" if passed else "FAIL",
                "observed": observed,
            }
            for passed, check_id, observed in checks
        ],
        "evidence": {
            key: {
                "path": value["path"],
                "sha256": value["sha256"],
                "status": value["payload"].get("status"),
            }
            for key, value in evidence.items()
        },
        "restrictions": {
            "official_dataset": False,
            "production": False,
            "downstream": False,
            "full_universe_build": False,
            "unbounded_generation": False,
            "ml_rl_backtest_consumption": False,
            "event_state_on_demand": False,
            "consumption_policy_required_before_any_downstream_use": True,
        },
        "counters": {
            "source_market_data_rows_read": 0,
            "parquet_content_rows_read": 0,
            "materializer_executions": 0,
            "validator_executions": 0,
            "new_candidate_registry_entries_written": 0,
            "datasets_written": 0,
        },
        "next_allowed_gate": NEXT_GATE if promoted else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    matrix["matrix_sha256"] = hash_excluding(matrix, "matrix_sha256")

    authorization_md = f"""# Market State On-Demand Capability Promotion Review Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REVIEW`
Date: `2026-07-27`

```text
review_id = {run_id}
gate = {GATE_ID}
metadata_evidence_read_allowed = true
source_market_data_reads_allowed = false
parquet_content_reads_allowed = false
new_materialization_allowed = false
candidate_registry_mutation_allowed = false
official_dataset_promotion_allowed = false
production_allowed = false
downstream_consumption_allowed = false
```

This authorization is consumed by the metadata-only capability promotion review.
It does not authorize a new Market State build.
"""

    readout = make_readout(matrix)

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
        "capability_promotion_decision": matrix["decision"]["capability_promotion_decision"],
        "capability_status_after_review": matrix["decision"]["capability_status_after_review"],
        "reviewed_evidence_items": matrix["decision"]["reviewed_evidence_items"],
        "hard_review_failures": hard_failures,
        "source_market_data_rows_read": 0,
        "parquet_content_rows_read": 0,
        "materializer_executions": 0,
        "validator_executions": 0,
        "new_candidate_registry_entries_written": 0,
        "datasets_written": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
        "artifacts": {
            "authorization": str(AUTH_MD_PATH),
            "scope": str(SCOPE_PATH),
            "contract": str(CONTRACT_PATH),
            "matrix": str(MATRIX_PATH),
            "readout": str(READOUT_PATH),
            "run_readout": str(run_dir / "market_state_on_demand_capability_promotion_review_readout_v0_1.md"),
        },
    }

    write_json(SCOPE_PATH, scope)
    write_json(CONTRACT_PATH, contract)
    write_json(MATRIX_PATH, matrix)
    write_text(AUTH_MD_PATH, authorization_md)
    write_text(READOUT_PATH, readout)
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_text(run_dir / "market_state_on_demand_capability_promotion_review_readout_v0_1.md", readout)

    print(json.dumps(final_manifest, indent=2, ensure_ascii=True))
    return 0 if hard_failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
