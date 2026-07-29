from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "event_state_on_demand_capability_promotion_review_runner_v0_1"
GATE_ID = "event_state_on_demand_capability_promotion_review_v0_1"
STATUS_PASS = "CLOSED_PASS_EVENT_STATE_CAPABILITY_PROMOTED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION"
STATUS_BLOCKED = "CLOSED_BLOCKED_EVENT_STATE_CAPABILITY_PROMOTION_REVIEW_NO_PROMOTION"
NEXT_GATE = "event_state_capability_consumption_policy_v0_1"

BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "runs"
CONFIGS = BASE / "configs"

AUTH_MD = BASE / "event_state_on_demand_capability_promotion_review_authorization_v0_1.md"
SCOPE_PATH = CONFIGS / "event_state_on_demand_capability_promotion_review_scope_v0_1.json"
CONTRACT_PATH = BASE / "event_state_on_demand_capability_promotion_review_contract_v0_1.json"
MATRIX_PATH = BASE / "event_state_on_demand_capability_promotion_review_matrix_v0_1.json"
READOUT_PATH = BASE / "event_state_on_demand_capability_promotion_review_readout_v0_1.md"
CAPABILITY_MANIFEST_PATH = BASE / "event_state_on_demand_runtime_capability_manifest_v0_1.json"

EVIDENCE_PATHS = {
    "bounded_execution": RUNS / "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z" / "final_manifest.json",
    "bounded_candidate_review": RUNS / "event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T202013Z" / "final_manifest.json",
    "deterministic_rerun": RUNS / "event_state_on_demand_bounded_deterministic_rerun_v0_1_20260728T070338Z" / "final_manifest.json",
    "determinism_validation": BASE / "event_state_on_demand_bounded_determinism_validation_matrix_v0_1.json",
    "exact_reuse": RUNS / "event_state_on_demand_bounded_idempotency_reuse_test_v0_1_20260728T074624Z" / "final_manifest.json",
    "reuse_transition": RUNS / "event_state_on_demand_bounded_reuse_eligibility_transition_review_v0_1_20260728T080426Z" / "final_manifest.json",
    "incremental_execution": RUNS / "event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z" / "final_manifest.json",
    "incremental_candidate_review": RUNS / "event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1_20260728T091026Z" / "final_manifest.json",
    "incremental_reuse": RUNS / "event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_v0_1_20260728T091759Z" / "final_manifest.json",
    "second_generation_incremental": RUNS / "event_state_on_demand_second_generation_incremental_extension_v0_1_20260728T103016Z" / "final_manifest.json",
    "second_generation_candidate_review": RUNS / "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260728T110845Z" / "final_manifest.json",
    "lineage_chain_validation": BASE / "event_state_on_demand_incremental_lineage_chain_validation_matrix_v0_1.json",
    "scale_validation": RUNS / "event_state_on_demand_scale_validation_v0_1_20260728T120123Z" / "final_manifest.json",
    "scale_validation_matrix": BASE / "event_state_on_demand_scale_validation_matrix_v0_1.json",
}

EXPECTED_STATUSES = {
    "bounded_execution": "CLOSED_PASS_EVENT_STATE_ON_DEMAND_BOUNDED_EXECUTION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
    "bounded_candidate_review": "CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION",
    "deterministic_rerun": "CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS",
    "determinism_validation": "CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION",
    "exact_reuse": "CLOSED_PASS_EVENT_STATE_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS",
    "reuse_transition": "CLOSED_APPROVED_EVENT_STATE_REUSE_ELIGIBILITY_TRANSITION_FOR_BOUNDED_EXACT_MATCH_WITH_RESTRICTIONS_NO_PROMOTION",
    "incremental_execution": "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
    "incremental_candidate_review": "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION",
    "incremental_reuse": "CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS",
    "second_generation_incremental": "CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
    "second_generation_candidate_review": "CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION",
    "scale_validation": "CLOSED_PASS_EVENT_STATE_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
    "scale_validation_matrix": "CLOSED_PASS_EVENT_STATE_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
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
    return payload.get("status") or payload.get("final_run_status") or payload.get("review_status")


def hard_failures_of(payload: dict[str, Any]) -> int:
    for key in ("hard_validation_failures", "hard_review_failures", "hard_policy_failures"):
        if key in payload and payload[key] is not None:
            return int(payload[key])
    decision = payload.get("decision", {})
    for key in ("hard_validation_failures", "hard_review_failures", "hard_policy_failures"):
        if key in decision and decision[key] is not None:
            return int(decision[key])
    return 0


def false_boundary(payload: dict[str, Any], key: str) -> bool:
    if key in payload:
        return payload[key] is False
    boundary = payload.get("boundary_counters", {})
    if key in boundary:
        return boundary[key] is False
    return True


def make_readout(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Event State On-Demand Capability Promotion Review Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-28`

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
official_event_state_dataset = false
production = false
downstream = false
new_materialization_authorized = false
new_registry_entries_written = 0
source_market_data_rows_read = 0
next_allowed_gate = {matrix['next_allowed_gate']}
```

The Event State on-demand runtime capability is promoted only as a restricted
candidate-runtime capability for `session_opened` / `exchange_session`. This
review does not promote an official physical Event State dataset, does not
authorize production and does not open downstream ML/RL/backtest consumption.
"""


def main() -> int:
    now = utc_now()
    run_id = f"{GATE_ID}_{now.replace('-', '').replace(':', '').replace('Z', 'Z')}"
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    evidence: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for key, path in EVIDENCE_PATHS.items():
        if not path.exists():
            missing.append(str(path))
            continue
        payload = read_json(path)
        evidence[key] = {"path": str(path), "sha256": sha256_file(path), "payload": payload, "status": status_of(payload)}

    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, observed: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    add_check("required_evidence_files_present", not missing, missing)

    for key, expected in EXPECTED_STATUSES.items():
        observed = evidence.get(key, {}).get("status")
        add_check(f"{key}_status", observed == expected, observed)

    lineage_payload = evidence.get("lineage_chain_validation", {}).get("payload", {})
    lineage_decision = lineage_payload.get("decision", {})
    add_check("lineage_chain_hard_failures_zero", int(lineage_decision.get("hard_validation_failures", 0)) == 0, lineage_decision.get("hard_validation_failures"))
    add_check("lineage_chain_represented_contexts_14", int(lineage_decision.get("represented_contexts", 0)) == 14, lineage_decision.get("represented_contexts"))

    scale_payload = evidence.get("scale_validation", {}).get("payload", {})
    add_check("scale_requested_contexts_80", scale_payload.get("requested_event_state_context_count") == 80, scale_payload.get("requested_event_state_context_count"))
    add_check("scale_represented_contexts_74", scale_payload.get("represented_context_count") == 74, scale_payload.get("represented_context_count"))
    add_check("scale_unavailable_contexts_6", scale_payload.get("unavailable_context_count") == 6, scale_payload.get("unavailable_context_count"))
    add_check("scale_hard_failures_zero", scale_payload.get("hard_validation_failures") == 0, scale_payload.get("hard_validation_failures"))
    add_check("scale_market_state_materializer_zero", scale_payload.get("market_state_materializer_executions") == 0, scale_payload.get("market_state_materializer_executions"))
    add_check("scale_source_market_rows_zero", scale_payload.get("source_market_data_rows_read") == 0, scale_payload.get("source_market_data_rows_read"))
    add_check("scale_event_type_session_opened", scale_payload.get("event_type_id") == "event_type:market_data:session_opened", scale_payload.get("event_type_id"))
    add_check("scale_subject_scope_exchange_session", scale_payload.get("subject_scope") == "exchange_session", scale_payload.get("subject_scope"))

    for key, item in evidence.items():
        payload = item["payload"]
        add_check(f"{key}_hard_failures_zero", hard_failures_of(payload) == 0, hard_failures_of(payload))
        add_check(f"{key}_official_dataset_closed", false_boundary(payload, "official_dataset"), payload.get("official_dataset", payload.get("boundary_counters", {}).get("official_dataset")))
        add_check(f"{key}_production_closed", false_boundary(payload, "production"), payload.get("production", payload.get("boundary_counters", {}).get("production")))
        add_check(f"{key}_downstream_closed", false_boundary(payload, "downstream"), payload.get("downstream", payload.get("boundary_counters", {}).get("downstream")))

    hard_review_failures = sum(0 if check["passed"] else 1 for check in checks)
    status = STATUS_PASS if hard_review_failures == 0 else STATUS_BLOCKED
    promoted = hard_review_failures == 0

    scope = {
        "scope_id": "event_state_on_demand_capability_promotion_review_scope_v0_1",
        "gate": GATE_ID,
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REVIEW",
        "consumed_by_review_id": run_id,
        "consumed_at_utc": now,
        "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1",
        "event_type_scope": ["event_type:market_data:session_opened"],
        "subject_scope": "exchange_session",
        "authority": {
            "metadata_evidence_read_allowed": True,
            "source_market_data_reads_allowed": False,
            "new_event_state_materialization_allowed": False,
            "new_market_state_materialization_allowed": False,
            "candidate_registry_mutation_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_allowed": False,
        },
    }
    scope["scope_sha256"] = hash_excluding(scope, "scope_sha256")
    write_json(SCOPE_PATH, scope)

    contract = {
        "contract_id": "event_state_on_demand_capability_promotion_review_contract_v0_1",
        "gate": GATE_ID,
        "contract_status": "accepted_for_metadata_only_capability_promotion_review",
        "consumed_by_review_id": run_id,
        "promotion_target": "event_state_on_demand_runtime_capability_v0_1",
        "promotion_decision_values": ["promote_with_restrictions_candidate_runtime_only", "block_capability_promotion"],
        "required_evidence": list(EVIDENCE_PATHS.keys()),
        "required_boundary_invariants": {
            "new_materialization_authorized": False,
            "source_market_data_rows_read_by_review": 0,
            "new_candidate_registry_entries_written_by_review": 0,
            "official_event_state_dataset": False,
            "production": False,
            "downstream": False,
        },
        "next_gate_on_pass": NEXT_GATE,
    }
    contract["contract_content_sha256_excluding_hash_field"] = hash_excluding(contract, "contract_content_sha256_excluding_hash_field")
    write_json(CONTRACT_PATH, contract)

    auth = f"""# Event State On-Demand Capability Promotion Review Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REVIEW`
Date: `2026-07-28`

```text
gate = {GATE_ID}
consumed_by_review_id = {run_id}
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_type_scope = event_type:market_data:session_opened
subject_scope = exchange_session
metadata_evidence_read_allowed = true
new_event_state_materialization_allowed = false
new_market_state_materialization_allowed = false
source_market_data_rows_read_allowed = false
candidate_registry_mutation_allowed = false
official_dataset_promotion_allowed = false
production = false
downstream = false
```
"""
    write_text(AUTH_MD, auth)

    evidence_index = {
        key: {"path": item["path"], "sha256": item["sha256"], "status": item["status"]}
        for key, item in evidence.items()
    }
    write_json(run_dir / "evidence_index.json", evidence_index)

    decision = {
        "capability_id": "event_state_on_demand_runtime_capability_v0_1",
        "capability_promotion_decision": "promote_with_restrictions_candidate_runtime_only" if promoted else "block_capability_promotion",
        "capability_status_after_review": "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY" if promoted else "NOT_PROMOTED",
        "reviewed_evidence_items": len(evidence),
        "scale_requested_contexts": scale_payload.get("requested_event_state_context_count"),
        "scale_represented_contexts": scale_payload.get("represented_context_count"),
        "scale_unavailable_contexts": scale_payload.get("unavailable_context_count"),
        "hard_review_failures": hard_review_failures,
    }
    matrix = {
        "review_id": run_id,
        "gate": GATE_ID,
        "status": status,
        "decision": decision,
        "checks": checks,
        "evidence_index": evidence_index,
        "boundary_counters": {
            "source_market_data_rows_read": 0,
            "new_event_state_materializer_executions": 0,
            "new_market_state_materializer_executions": 0,
            "new_candidate_dataset_registry_entries_written": 0,
            "official_event_state_dataset": False,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "next_allowed_gate": NEXT_GATE if promoted else None,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    matrix["review_matrix_sha256"] = hash_excluding(matrix, "review_matrix_sha256")
    write_json(MATRIX_PATH, matrix)
    write_json(run_dir / "review_matrix.json", matrix)

    capability_manifest = {
        "capability_id": "event_state_on_demand_runtime_capability_v0_1",
        "capability_status": "PROMOTED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY" if promoted else "NOT_PROMOTED",
        "promotion_review_id": run_id,
        "promotion_review_status": status,
        "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1",
        "allowed_event_type_ids": ["event_type:market_data:session_opened"],
        "accepted_subject_scope": "exchange_session",
        "candidate_generation_allowed_under_separate_authorization": promoted,
        "candidate_reuse_allowed_under_future_consumption_policy": False,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "restrictions": [
            "candidate_runtime_only",
            "session_opened_only",
            "exchange_session_subject_scope_only",
            "market_state_dependency_must_resolve_through_runtime_capability",
            "no_direct_market_state_path_consumption",
            "no_official_dataset_promotion",
            "no_production",
            "no_downstream",
            "consumption_policy_required_before_general_reuse",
        ],
    }
    capability_manifest["capability_manifest_sha256"] = hash_excluding(capability_manifest, "capability_manifest_sha256")
    write_json(CAPABILITY_MANIFEST_PATH, capability_manifest)
    write_json(run_dir / "capability_manifest.json", capability_manifest)

    readout = make_readout(matrix)
    write_text(READOUT_PATH, readout)
    write_text(run_dir / "review_readout.md", readout)

    final = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "status": status,
        "reviewed_at_utc": now,
        "git_branch": git_value(["git", "branch", "--show-current"]) or "unknown",
        "git_commit": git_value(["git", "rev-parse", "HEAD"]) or "unknown",
        "git_dirty": bool(git_value(["git", "status", "--porcelain"])),
        "capability_id": decision["capability_id"],
        "capability_promotion_decision": decision["capability_promotion_decision"],
        "capability_status_after_review": decision["capability_status_after_review"],
        "reviewed_evidence_items": decision["reviewed_evidence_items"],
        "scale_requested_contexts": decision["scale_requested_contexts"],
        "scale_represented_contexts": decision["scale_represented_contexts"],
        "scale_unavailable_contexts": decision["scale_unavailable_contexts"],
        "hard_review_failures": hard_review_failures,
        "source_market_data_rows_read": 0,
        "new_event_state_materializer_executions": 0,
        "new_market_state_materializer_executions": 0,
        "new_candidate_dataset_registry_entries_written": 0,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": NEXT_GATE if promoted else None,
        "artifacts": {
            "authorization": str(AUTH_MD),
            "scope": str(SCOPE_PATH),
            "contract": str(CONTRACT_PATH),
            "matrix": str(MATRIX_PATH),
            "capability_manifest": str(CAPABILITY_MANIFEST_PATH),
            "readout": str(READOUT_PATH),
            "run_evidence_index": str(run_dir / "evidence_index.json"),
            "run_review_matrix": str(run_dir / "review_matrix.json"),
            "run_capability_manifest": str(run_dir / "capability_manifest.json"),
            "run_readout": str(run_dir / "review_readout.md"),
            "final_manifest": str(run_dir / "final_manifest.json"),
        },
    }
    final["final_manifest_sha256"] = hash_excluding(final, "final_manifest_sha256")
    write_json(run_dir / "final_manifest.json", final)

    print(json.dumps({
        "run_id": run_id,
        "status": status,
        "capability_status_after_review": decision["capability_status_after_review"],
        "reviewed_evidence_items": decision["reviewed_evidence_items"],
        "hard_review_failures": hard_review_failures,
        "next_allowed_gate": final["next_allowed_gate"],
        "final_manifest": str(run_dir / "final_manifest.json"),
    }, indent=2, ensure_ascii=True))
    return 0 if promoted else 1


if __name__ == "__main__":
    raise SystemExit(main())