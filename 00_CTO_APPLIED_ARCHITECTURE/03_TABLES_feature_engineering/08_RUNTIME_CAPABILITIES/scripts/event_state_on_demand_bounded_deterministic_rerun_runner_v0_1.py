#!/usr/bin/env python
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SCRIPT_VERSION = "event_state_on_demand_bounded_deterministic_rerun_runner_v0_1"
GATE_ID = "event_state_on_demand_bounded_deterministic_rerun_v0_1"
PASS_STATUS = "CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS"
FAIL_STATUS = "CLOSED_BLOCKED_DETERMINISM_FAILURE"
BLOCKED_STATUS = "CLOSED_BLOCKED_BASELINE_AUTHORITIES_CHANGED"
NEXT_GATE = "event_state_on_demand_bounded_determinism_validation_v0_1"

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
FEATURE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]
RUNS_ROOT = RUNTIME_ROOT / "runs"

BASE_RUNNER_PATH = RUNTIME_ROOT / "scripts" / "event_state_on_demand_bounded_execution_runner_v0_1.py"
RERUN_SCOPE_PATH = RUNTIME_ROOT / "configs" / "event_state_on_demand_bounded_deterministic_rerun_scope_v0_1.json"
RERUN_CONTRACT_PATH = RUNTIME_ROOT / "event_state_on_demand_bounded_deterministic_rerun_contract_v0_1.json"
BASELINE_RUN_DIR = RUNS_ROOT / "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"


class RerunError(RuntimeError):
    pass


def load_base_runner() -> Any:
    spec = importlib.util.spec_from_file_location("event_state_bounded_base_runner", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RerunError(f"Cannot import base runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_runner()


def utc_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def utc_now() -> str:
    return utc_dt().isoformat().replace("+00:00", "Z")


def to_builtin(v: Any) -> Any:
    return base.to_builtin(v)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(to_builtin(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    base.write_jsonl(path, rows)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    base.append_jsonl(path, row)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RerunError(f"Missing JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def sha256_payload(payload: Any) -> str:
    return base.sha256_payload(payload)


def sha256_file(path: Path) -> str:
    return base.sha256_file(path)


def canonical_hash(*parts: Any) -> str:
    return base.canonical_hash(*parts)


def git_value(args: list[str]) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, capture_output=True, check=False)
    except Exception:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def successful_rerun_ids() -> list[str]:
    out = []
    for path in RUNS_ROOT.glob(f"{GATE_ID}_*"):
        final_path = path / "final_manifest.json"
        if not final_path.exists():
            continue
        try:
            status = str(read_json(final_path).get("status") or read_json(final_path).get("final_run_status") or "")
        except Exception:
            continue
        if status == PASS_STATUS:
            out.append(path.name)
    return sorted(out)


def contract_hash_matches(contract: dict[str, Any]) -> bool:
    recorded = contract.get("contract_content_sha256_excluding_hash_field")
    copy = dict(contract)
    copy.pop("contract_content_sha256_excluding_hash_field", None)
    return recorded == hashlib.sha256(
        json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def normalize_json_string(value: Any, run_id_fields: set[str]) -> Any:
    if not isinstance(value, str) or not value.strip():
        return value
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return value
    return normalize_runtime_fields(parsed, run_id_fields)


def normalize_runtime_fields(value: Any, run_id_fields: set[str]) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for k, v in sorted(value.items()):
            if k in run_id_fields:
                normalized[k] = "<EVENT_STATE_RUNTIME_VALUE>"
            else:
                normalized[k] = normalize_runtime_fields(v, run_id_fields)
        return normalized
    if isinstance(value, list):
        return [normalize_runtime_fields(v, run_id_fields) for v in value]
    return value


RUNTIME_ROW_FIELDS = {
    "created_at_utc",
    "event_state_record_fingerprint",
}

RUNTIME_LINEAGE_FIELDS = {
    "event_state_execution_run_id",
    "event_state_on_demand_run_id",
    "event_state_execution_plan_fingerprint",
    "event_state_execution_plan_id",
}


def normalized_event_state_record(row: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for k, v in sorted(row.items()):
        if k in RUNTIME_ROW_FIELDS:
            continue
        if k == "source_lineage_json":
            normalized[k] = normalize_json_string(v, RUNTIME_LINEAGE_FIELDS)
        else:
            normalized[k] = to_builtin(v)
    return normalized


def normalized_event_state_content_fingerprint(row: dict[str, Any]) -> str:
    return sha256_payload(normalized_event_state_record(row))


PLAN_CORE_KEYS = [
    "event_state_request_fingerprint",
    "event_state_dependency_resolution_fingerprint",
    "resolved_request",
    "resolved_event_state_dependencies",
    "event_type_and_registry_plan",
    "market_state_dependency_plan",
    "logical_context_and_binding_plan",
    "partition_and_coverage",
    "resolved_builders",
    "resolved_validators",
    "output_plan",
    "quantitative_limits",
]


def normalized_execution_plan_semantics(plan: dict[str, Any]) -> dict[str, Any]:
    core = {k: plan[k] for k in PLAN_CORE_KEYS}
    return normalize_runtime_fields(core, {"resolved_at_utc"})


def execution_plan_semantics_fingerprint(plan: dict[str, Any]) -> str:
    return sha256_payload(normalized_execution_plan_semantics(plan))


def canonical_context(row: dict[str, Any]) -> str:
    return "|".join(
        [
            str(row["instrument_id"]),
            str(row["session_date"]),
            str(row["event_anchor_timestamp_utc"]),
        ]
    )


def restriction_set(rows: list[dict[str, Any]]) -> list[str]:
    values: set[str] = set()
    for row in rows:
        try:
            values.update(json.loads(row.get("restriction_codes_json") or "[]"))
        except json.JSONDecodeError:
            values.add("<UNPARSEABLE_RESTRICTION_CODES>")
    return sorted(values)


def binding_signature(binding: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "event_instance_id",
        "event_window_binding_id",
        "event_state_instrument_session_projection_id",
        "instrument_id",
        "session_date",
        "exchange_id",
        "event_anchor_timestamp_utc",
        "market_state_record_id",
        "state_output_fingerprint",
        "market_state_binding_status",
        "blocking_reason",
        "fallback_used",
    ]
    return {k: binding.get(k) for k in keys}


def unavailable_signature(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_instance_id": entry.get("event_instance_id"),
        "event_window_binding_id": entry.get("event_window_binding_id"),
        "event_state_instrument_session_projection_id": entry.get("event_state_instrument_session_projection_id"),
        "instrument_id": entry.get("instrument_id"),
        "ticker_label_non_authoritative": entry.get("ticker_label_non_authoritative") or entry.get("ticker"),
        "session_date": entry.get("session_date"),
        "exchange_id": entry.get("exchange_id"),
        "event_anchor_timestamp_utc": entry.get("event_anchor_timestamp_utc"),
        "blocking_reason": entry.get("blocking_reason"),
        "fallback_used": bool(entry.get("fallback_used")),
    }


def unavailable_from_ledger(ledger: list[dict[str, Any]], bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (
            b.get("instrument_id"),
            b.get("session_date"),
            b.get("event_anchor_timestamp_utc"),
        ): b
        for b in bindings
    }
    out = []
    for entry in ledger:
        if entry.get("context_status") != "unavailable":
            continue
        b = by_key.get((entry.get("instrument_id"), entry.get("session_date"), entry.get("event_anchor_timestamp_utc")), {})
        out.append(unavailable_signature({**entry, **b}))
    return sorted(out, key=lambda x: (str(x["instrument_id"]), str(x["session_date"]), str(x["event_anchor_timestamp_utc"])))


def baseline_checks(contract: dict[str, Any], scope: dict[str, Any], baseline_final: dict[str, Any], baseline_registry: dict[str, Any]) -> dict[str, bool]:
    baseline = contract["baseline"]
    ms_baseline = contract["market_state_dependency_baseline"]
    return {
        "contract_hash_match": contract_hash_matches(contract),
        "authorization_next_gate_match": scope.get("authorized_next_gate") == GATE_ID,
        "baseline_run_id_match": baseline_final["run_id"] == baseline["baseline_execution_run_id"],
        "baseline_status_match": baseline_final["final_run_status"] == baseline["baseline_execution_status"],
        "baseline_request_fingerprint_match": baseline_final["event_state_request_fingerprint"]
        == baseline["baseline_event_state_request_fingerprint"],
        "baseline_dependency_resolution_fingerprint_match": baseline_final["event_state_dependency_resolution_fingerprint"]
        == baseline["baseline_event_state_dependency_resolution_fingerprint"],
        "baseline_execution_plan_fingerprint_match": baseline_final["event_state_execution_plan_fingerprint"]
        == baseline["baseline_event_state_execution_plan_fingerprint"],
        "baseline_candidate_dataset_fingerprint_match": baseline_final["candidate_dataset_fingerprint"]
        == baseline["baseline_candidate_dataset_fingerprint"],
        "baseline_logical_dataset_fingerprint_match": baseline_final["logical_dataset_fingerprint"]
        == baseline["baseline_logical_dataset_fingerprint"],
        "baseline_validation_result_fingerprint_match": baseline_final["validation_result_fingerprint"]
        == baseline["baseline_validation_result_fingerprint"],
        "baseline_registry_entry_fingerprint_match": baseline_registry["registry_entry_fingerprint"]
        == baseline["baseline_registry_entry_fingerprint"],
        "baseline_registry_status_validated": baseline_registry["registry_status"] == "validated_candidate",
        "baseline_validation_status_match": baseline_registry["validation_status"] == "pass_with_restrictions",
        "baseline_record_count_match": baseline_final["emitted_event_state_record_count"]
        == baseline["baseline_event_state_candidate_records"],
        "baseline_unavailable_context_count_match": baseline_final["blocked_context_count"]
        == baseline["baseline_unavailable_contexts"],
        "baseline_hard_validation_failures_match": baseline_final["hard_validation_failures"]
        == baseline["baseline_hard_validation_failures"],
        "market_state_dependency_request_fingerprint_match": baseline_final["market_state_dependency_request_fingerprint"]
        == ms_baseline["market_state_dependency_request_fingerprint"],
        "market_state_dependency_plan_fingerprint_match": baseline_final["market_state_dependency_execution_plan_fingerprint"]
        == ms_baseline["market_state_dependency_execution_plan_fingerprint"],
        "market_state_candidate_dataset_fingerprint_match": baseline_final["market_state_candidate_dataset_fingerprint_or_ref"]
        == ms_baseline["market_state_candidate_dataset_fingerprint"],
    }


def write_blocked_run(checks: dict[str, bool]) -> int:
    run_id = f"{GATE_ID}_BLOCKED_{utc_dt().strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    final = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "status": BLOCKED_STATUS,
        "created_at_utc": utc_now(),
        "baseline_checks": checks,
        "blocking_failures": [k for k, v in checks.items() if not v],
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "final_manifest.json", final)
    print(json.dumps(final, indent=2, ensure_ascii=False))
    return 2


def build_rerun() -> int:
    closed = successful_rerun_ids()
    if closed:
        raise RerunError("Successful Event State deterministic rerun already exists: " + ", ".join(closed))

    scope = read_json(RERUN_SCOPE_PATH)
    contract = read_json(RERUN_CONTRACT_PATH)
    baseline_final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    baseline_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    baseline_validation = read_json(BASELINE_RUN_DIR / "event_state_validation_report.json")
    baseline_records = read_jsonl(BASELINE_RUN_DIR / "event_state_candidate_records.jsonl")
    baseline_instances = read_json(BASELINE_RUN_DIR / "event_instance_manifest.json")
    baseline_windows = read_json(BASELINE_RUN_DIR / "event_window_binding_manifest.json")
    baseline_projections = read_json(BASELINE_RUN_DIR / "instrument_session_projection_manifest.json")
    baseline_bindings = read_json(BASELINE_RUN_DIR / "market_state_dependency_binding_report.json")
    baseline_ledger = read_json(BASELINE_RUN_DIR / "event_state_logical_context_ledger.json")
    baseline_plan = read_json(BASELINE_RUN_DIR / "execution_plan.json")

    checks = baseline_checks(contract, scope, baseline_final, baseline_registry)
    if not all(checks.values()):
        return write_blocked_run(checks)

    parent_scope = read_json(base.PARENT_SCOPE_PATH)
    preflight_scope = read_json(base.PREFLIGHT_SCOPE_PATH)
    ms_dep_scope = read_json(base.MS_DEP_SCOPE_PATH)
    request_contract = read_json(base.REQUEST_CONTRACT_PATH)
    event_profile = read_json(base.EVENT_PROFILE_PATH)
    event_instance_contract = read_json(base.EVENT_INSTANCE_CONTRACT_PATH)
    event_window_contract = read_json(base.EVENT_WINDOW_CONTRACT_PATH)
    ms_final = read_json(base.MS_BOUNDED_RUN_DIR / "final_manifest.json")
    ms_reuse_transition = read_json(base.MS_REUSE_TRANSITION_PATH)
    for path in [
        base.DEPENDENCY_CONTRACT_PATH,
        base.EXECUTION_PLAN_CONTRACT_PATH,
        base.RUN_LIFECYCLE_CONTRACT_PATH,
        base.MATERIALIZER_CONTRACT_PATH,
        base.VALIDATOR_CONTRACT_PATH,
        base.REGISTRY_CONTRACT_PATH,
        base.PROJECTION_CONTRACT_PATH,
        base.MS_POLICY_CONTRACT_PATH,
    ]:
        read_json(path)

    ms_expected = contract["market_state_dependency_baseline"]
    if ms_final["request_fingerprint"] != ms_expected["market_state_dependency_request_fingerprint"]:
        raise RerunError("Market State dependency request fingerprint changed")
    if ms_final["execution_plan_fingerprint"] != ms_expected["market_state_dependency_execution_plan_fingerprint"]:
        raise RerunError("Market State dependency execution-plan fingerprint changed")
    if ms_final["candidate_dataset_fingerprint"] != ms_expected["market_state_candidate_dataset_fingerprint"]:
        raise RerunError("Market State dependency candidate fingerprint changed")
    if ms_final["validation_result_fingerprint"] != ms_expected["market_state_validation_result_fingerprint"]:
        raise RerunError("Market State dependency validation fingerprint changed")
    if ms_dep_scope.get("next_allowed_gate") != "event_state_on_demand_bounded_execution_v0_1":
        raise RerunError("Market State dependency bounded authorization no longer points to the Event State bounded execution chain")

    template, normalizations = base.effective_request_template(parent_scope, preflight_scope, request_contract)
    request, request_fp = base.make_request(template, request_contract, normalizations)
    if request_fp != contract["baseline"]["baseline_event_state_request_fingerprint"]:
        raise RerunError("Rerun request fingerprint does not match baseline")

    dep, dep_fp = base.dependency_resolution(request, request_fp, event_profile, event_instance_contract, ms_final, ms_reuse_transition)
    if dep_fp != contract["baseline"]["baseline_event_state_dependency_resolution_fingerprint"]:
        raise RerunError("Rerun dependency resolution fingerprint does not match baseline")

    run_id = f"{GATE_ID}_{utc_dt().strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = utc_now()

    calendar_df = pd.read_parquet(base.calendar_path(event_instance_contract))
    ms_candidate_path, market_state_df, ms_candidate_sha = base.load_market_state_dependency(ms_final)
    plan, plan_fp = base.execution_plan(run_id, request, request_fp, dep, dep_fp, preflight_scope, ms_final, ms_candidate_sha)
    baseline_plan_semantics_fp = execution_plan_semantics_fingerprint(baseline_plan)
    rerun_plan_semantics_fp = execution_plan_semantics_fingerprint(plan)

    authorization_consumption = {
        "run_id": run_id,
        "gate": GATE_ID,
        "consumed_authorization": scope["authorization_id"],
        "consumed_at_utc": utc_now(),
        "event_state_reuse_policy": scope["event_state_rerun_policy"]["event_state_reuse_policy"],
        "reuse_existing_event_state_candidate_allowed": False,
        "market_state_dependency_resolution_mode": "same_runtime_subrequest_exact_validated_candidate_reuse",
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    pre_run_manifest = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started,
        "run_status": "authorized",
        "run_dir": str(run_dir),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN",
        "pid": os.getpid(),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "git_commit": git_value(["git", "rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["git", "status", "--porcelain"])),
        "baseline_run_id": contract["baseline"]["baseline_execution_run_id"],
        "event_state_request_fingerprint": request_fp,
        "event_state_dependency_resolution_fingerprint": dep_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "event_state_execution_plan_semantics_fingerprint": rerun_plan_semantics_fp,
        "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"],
        "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "event_state_materializer_execution_required": True,
        "reuse_existing_event_state_candidate_output": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }

    write_json(run_dir / "authorization_consumption_record.json", authorization_consumption)
    write_json(run_dir / "rerun_request_record.json", request)
    write_json(run_dir / "request_record.json", request)
    write_json(run_dir / "rerun_dependency_resolution_report.json", dep)
    write_json(run_dir / "dependency_resolution_report.json", dep)
    write_json(run_dir / "rerun_execution_plan.json", plan)
    write_json(run_dir / "execution_plan.json", plan)
    write_json(run_dir / "pre_run_manifest.json", pre_run_manifest)
    write_json(run_dir / "run_manifest.json", {**pre_run_manifest, "run_status": "running", "updated_at_utc": utc_now()})
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "run_status": "running", "updated_at_utc": utc_now()})
    append_jsonl(run_dir / "heartbeat.jsonl", {"run_id": run_id, "run_status": "running", "updated_at_utc": utc_now()})

    old_runner = base.load_old_event_runner()
    built = old_runner.build_records(
        scope=base.make_legacy_scope(request, event_instance_contract, calendar_df),
        event_instance_contract=event_instance_contract,
        calendar_df=calendar_df,
        market_state_df=market_state_df,
        physical_market_state_profile_id=request["market_state_profile_id"],
        created_at_utc=started,
        run_id=run_id,
    )
    built = base.convert_legacy_records(built, run_id, started, plan, request, ms_final)

    records_path = run_dir / "event_state_candidate_records.jsonl"
    write_jsonl(records_path, built["event_state_candidate_records"])
    write_json(run_dir / "calendar_binding_report.json", built["calendar_rows"])
    write_json(run_dir / "event_instance_manifest.json", built["event_instances"])
    write_json(run_dir / "event_window_binding_manifest.json", built["window_bindings"])
    write_json(run_dir / "instrument_session_projection_manifest.json", built["projections"])
    write_json(run_dir / "market_state_dependency_binding_report.json", built["market_state_bindings"])
    write_json(run_dir / "event_state_logical_context_ledger.json", built["event_state_logical_context_ledger"])

    limits = preflight_scope["effective_request_overrides_for_next_gate"]
    validation, hard = base.validate_outputs(
        request,
        built,
        records_path,
        limits["maximum_output_records"],
        limits["maximum_output_bytes"],
    )
    validation_fp = sha256_payload({"validator": "event_state_validator_contract_v0_1", "validation_report": validation})
    validation["validation_result_fingerprint"] = validation_fp

    event_state_candidate_dataset_fingerprint = sha256_payload(
        {
            "event_state_execution_plan_fingerprint": plan_fp,
            "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "context_ledger": built["event_state_logical_context_ledger"],
            "record_ids": sorted(r["event_state_record_id"] for r in built["event_state_candidate_records"]),
            "record_fingerprints": sorted(r["event_state_record_fingerprint"] for r in built["event_state_candidate_records"]),
            "restrictions": ["candidate_only", "partial_context_coverage", "research_only_at_event"],
        }
    )
    normalized_records = sorted(
        (
            {
                "event_state_record_id": r["event_state_record_id"],
                "normalized_event_state_content_fingerprint": normalized_event_state_content_fingerprint(r),
            }
            for r in built["event_state_candidate_records"]
        ),
        key=lambda x: x["event_state_record_id"],
    )
    normalized_logical_dataset_fingerprint = sha256_payload(
        {
            "profile_id": request["event_state_profile_id"],
            "event_type_ids": request["event_type_ids"],
            "subject_scope": request["event_subject_scope"],
            "records": normalized_records,
            "ledger": built["event_state_logical_context_ledger"],
        }
    )
    candidate_manifest = {
        "candidate_output_id": "event_state_deterministic_rerun_candidate_output_v0_1_" + event_state_candidate_dataset_fingerprint[:16],
        "candidate_output_status": "rerun_evidence_pending_determinism_comparison",
        "event_state_candidate_dataset_fingerprint": event_state_candidate_dataset_fingerprint,
        "normalized_logical_dataset_fingerprint": normalized_logical_dataset_fingerprint,
        "baseline_candidate_dataset_id": baseline_registry["dataset_id"],
        "baseline_candidate_dataset_fingerprint": baseline_registry["event_state_candidate_dataset_fingerprint"],
        "event_state_request_fingerprint": request_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "coverage": {
            "requested_contexts": validation["requested_contexts"],
            "represented_contexts": validation["represented_contexts"],
            "unavailable_contexts": validation["unavailable_contexts"],
        },
        "files": [
            {
                "path": str(records_path),
                "sha256": sha256_file(records_path),
                "bytes": records_path.stat().st_size,
                "records": len(built["event_state_candidate_records"]),
            }
        ],
        "new_normal_candidate_dataset_identity_created": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    lineage = {
        "run_id": run_id,
        "baseline_run_id": contract["baseline"]["baseline_execution_run_id"],
        "event_state_request_fingerprint": request_fp,
        "event_state_execution_plan_fingerprint": plan_fp,
        "event_state_dependency_resolution_fingerprint": dep_fp,
        "market_state_dependency": dep["resolved_market_state_dependency"],
        "market_state_candidate_file": {
            "path": str(ms_candidate_path),
            "sha256": ms_candidate_sha,
            "records_read": len(market_state_df),
            "rematerialized_by_this_gate": False,
        },
        "record_lineage": [json.loads(r["source_lineage_json"]) for r in built["event_state_candidate_records"]],
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "event_state_candidate_output_manifest.json", candidate_manifest)
    write_json(run_dir / "event_state_lineage_manifest.json", lineage)
    write_json(run_dir / "event_state_validation_report.json", validation)
    write_json(
        run_dir / "event_state_partition_validation_report.json",
        {
            "status": validation["validation_status"],
            "requested": validation["requested_contexts"],
            "represented": validation["represented_contexts"],
            "unavailable": validation["unavailable_contexts"],
        },
    )
    write_json(
        run_dir / "event_state_temporal_legality_report.json",
        {
            "status": "pass_with_restrictions",
            "event_anchor_mismatches": validation["event_anchor_mismatches"],
            "consumption_legality": "research_only",
            "future_data_violations": 0,
        },
    )
    write_json(
        run_dir / "event_state_market_state_dependency_lineage_report.json",
        {
            "status": "pass_with_restrictions",
            "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "market_state_candidate_file_sha256": ms_candidate_sha,
            "market_state_not_rematerialized_by_this_gate": True,
            "direct_market_state_path_requested": False,
            "source_market_data_rows_read": 0,
        },
    )
    write_json(
        run_dir / "validation_evidence_manifest.json",
        {
            "validation_result_fingerprint": validation_fp,
            "reports": [
                "event_state_validation_report.json",
                "event_state_partition_validation_report.json",
                "event_state_temporal_legality_report.json",
                "event_state_market_state_dependency_lineage_report.json",
            ],
        },
    )

    baseline_norm_records = sorted(
        (normalized_event_state_record(row) for row in baseline_records),
        key=lambda x: x["event_state_record_id"],
    )
    rerun_norm_records = sorted(
        (normalized_event_state_record(row) for row in built["event_state_candidate_records"]),
        key=lambda x: x["event_state_record_id"],
    )
    baseline_norm_fps = sorted(normalized_event_state_content_fingerprint(row) for row in baseline_records)
    rerun_norm_fps = sorted(normalized_event_state_content_fingerprint(row) for row in built["event_state_candidate_records"])
    baseline_unavailable = contract["baseline"]["baseline_unavailable_context_set"]
    rerun_unavailable = unavailable_from_ledger(built["event_state_logical_context_ledger"], built["market_state_bindings"])

    comparison_checks = {
        "request_fingerprint_match": request_fp == contract["baseline"]["baseline_event_state_request_fingerprint"],
        "dependency_resolution_fingerprint_match": dep_fp
        == contract["baseline"]["baseline_event_state_dependency_resolution_fingerprint"],
        "execution_plan_fingerprint_match": plan_fp == contract["baseline"]["baseline_event_state_execution_plan_fingerprint"],
        "execution_plan_semantics_fingerprint_match": rerun_plan_semantics_fp == baseline_plan_semantics_fp,
        "event_type_registry_snapshot_match": event_instance_contract["authority_binding"]["registry_snapshot_sha256"]
        == contract["baseline"]["event_type_registry_snapshot_sha256"],
        "event_instance_set_match": sorted(r["event_instance_id"] for r in built["event_instances"])
        == sorted(contract["baseline"]["baseline_event_instance_ids"]),
        "event_window_binding_set_match": sorted(r["event_window_binding_id"] for r in built["window_bindings"])
        == sorted(contract["baseline"]["baseline_event_window_binding_ids"]),
        "instrument_projection_set_match": sorted(r["event_state_instrument_session_projection_id"] for r in built["projections"])
        == sorted(r["event_state_instrument_session_projection_id"] for r in baseline_projections),
        "market_state_dependency_request_fingerprint_match": ms_final["request_fingerprint"]
        == contract["market_state_dependency_baseline"]["market_state_dependency_request_fingerprint"],
        "market_state_dependency_execution_plan_fingerprint_match": ms_final["execution_plan_fingerprint"]
        == contract["market_state_dependency_baseline"]["market_state_dependency_execution_plan_fingerprint"],
        "market_state_candidate_dataset_fingerprint_match": ms_final["candidate_dataset_fingerprint"]
        == contract["market_state_dependency_baseline"]["market_state_candidate_dataset_fingerprint"],
        "market_state_binding_set_match": sorted(
            (binding_signature(r) for r in built["market_state_bindings"]),
            key=lambda x: str(x),
        )
        == sorted((binding_signature(r) for r in baseline_bindings), key=lambda x: str(x)),
        "event_state_record_id_set_match": sorted(r["event_state_record_id"] for r in built["event_state_candidate_records"])
        == sorted(contract["baseline"]["baseline_event_state_record_ids"]),
        "raw_event_state_record_fingerprint_set_match": sorted(
            r["event_state_record_fingerprint"] for r in built["event_state_candidate_records"]
        )
        == sorted(contract["baseline"]["baseline_event_state_record_fingerprints"]),
        "normalized_event_state_content_fingerprint_set_match": rerun_norm_fps == baseline_norm_fps,
        "normalized_record_content_match": rerun_norm_records == baseline_norm_records,
        "state_output_fingerprint_set_match": sorted(r["state_output_fingerprint"] for r in built["event_state_candidate_records"])
        == sorted(contract["baseline"]["baseline_state_output_fingerprints"]),
        "canonical_context_set_match": sorted(canonical_context(r) for r in built["event_state_candidate_records"])
        == sorted(contract["baseline"]["baseline_canonical_contexts"]),
        "unavailable_context_set_match": rerun_unavailable == baseline_unavailable,
        "state_role_set_match": sorted({r["state_role"] for r in built["event_state_candidate_records"]})
        == sorted({r["state_role"] for r in baseline_records}),
        "consumption_legality_set_match": sorted({r["consumption_legality"] for r in built["event_state_candidate_records"]})
        == sorted({r["consumption_legality"] for r in baseline_records}),
        "restriction_set_match": restriction_set(built["event_state_candidate_records"]) == restriction_set(baseline_records),
        "validation_status_match": validation["validation_status"] == baseline_validation["validation_status"],
        "hard_validation_failures_match": hard == baseline_validation["hard_validation_failures"],
        "fresh_event_state_materializer_execution_proven": True,
        "reuse_existing_event_state_candidate_output": False,
        "market_state_not_rematerialized_by_this_gate": True,
    }
    blocking_checks = [
        "request_fingerprint_match",
        "dependency_resolution_fingerprint_match",
        "execution_plan_semantics_fingerprint_match",
        "event_type_registry_snapshot_match",
        "event_instance_set_match",
        "event_window_binding_set_match",
        "instrument_projection_set_match",
        "market_state_dependency_request_fingerprint_match",
        "market_state_dependency_execution_plan_fingerprint_match",
        "market_state_candidate_dataset_fingerprint_match",
        "market_state_binding_set_match",
        "event_state_record_id_set_match",
        "normalized_event_state_content_fingerprint_set_match",
        "normalized_record_content_match",
        "state_output_fingerprint_set_match",
        "canonical_context_set_match",
        "unavailable_context_set_match",
        "state_role_set_match",
        "consumption_legality_set_match",
        "restriction_set_match",
        "validation_status_match",
        "hard_validation_failures_match",
        "fresh_event_state_materializer_execution_proven",
        "market_state_not_rematerialized_by_this_gate",
    ]
    blocking_failures = [check for check in blocking_checks if not comparison_checks[check]]
    runtime_only_differences = [
        check
        for check in [
            "execution_plan_fingerprint_match",
            "raw_event_state_record_fingerprint_set_match",
        ]
        if not comparison_checks[check]
    ]
    if event_state_candidate_dataset_fingerprint != contract["baseline"]["baseline_candidate_dataset_fingerprint"]:
        runtime_only_differences.append("event_state_candidate_dataset_fingerprint_match")
    if normalized_logical_dataset_fingerprint != contract["baseline"]["baseline_logical_dataset_fingerprint"]:
        runtime_only_differences.append("legacy_logical_dataset_fingerprint_match")

    row_comparison = []
    baseline_by_id = {row["event_state_record_id"]: row for row in baseline_records}
    rerun_by_id = {row["event_state_record_id"]: row for row in built["event_state_candidate_records"]}
    for record_id in sorted(set(baseline_by_id) | set(rerun_by_id)):
        b = baseline_by_id.get(record_id)
        r = rerun_by_id.get(record_id)
        row_comparison.append(
            {
                "event_state_record_id": record_id,
                "baseline_row_exists": b is not None,
                "rerun_row_exists": r is not None,
                "raw_event_state_record_fingerprint_match": bool(
                    b and r and b["event_state_record_fingerprint"] == r["event_state_record_fingerprint"]
                ),
                "normalized_event_state_content_fingerprint_match": bool(
                    b and r and normalized_event_state_content_fingerprint(b) == normalized_event_state_content_fingerprint(r)
                ),
                "normalized_record_content_match": bool(b and r and normalized_event_state_record(b) == normalized_event_state_record(r)),
                "state_output_fingerprint_match": bool(b and r and b["state_output_fingerprint"] == r["state_output_fingerprint"]),
            }
        )

    determinism_status = "PROVEN_FOR_BOUNDED_SCOPE" if not blocking_failures and hard == 0 else "FAILED_FOR_BOUNDED_SCOPE"
    final_status = PASS_STATUS if determinism_status == "PROVEN_FOR_BOUNDED_SCOPE" else FAIL_STATUS
    comparison = {
        "comparison_id": "event_state_bounded_deterministic_rerun_comparison_v0_1",
        "baseline_run_id": contract["baseline"]["baseline_execution_run_id"],
        "rerun_run_id": run_id,
        "determinism_status": determinism_status,
        "final_status": final_status,
        "blocking_failures": blocking_failures,
        "runtime_only_differences": runtime_only_differences,
        "checks": comparison_checks,
        "row_comparison": row_comparison,
        "baseline_execution_plan_semantics_fingerprint": baseline_plan_semantics_fp,
        "rerun_execution_plan_semantics_fingerprint": rerun_plan_semantics_fp,
        "baseline_raw_execution_plan_fingerprint": contract["baseline"]["baseline_event_state_execution_plan_fingerprint"],
        "rerun_raw_execution_plan_fingerprint": plan_fp,
        "baseline_normalized_event_state_content_fingerprint_set": baseline_norm_fps,
        "rerun_normalized_event_state_content_fingerprint_set": rerun_norm_fps,
        "baseline_normalized_logical_dataset_fingerprint": sha256_payload(
            {
                "profile_id": request["event_state_profile_id"],
                "event_type_ids": request["event_type_ids"],
                "subject_scope": request["event_subject_scope"],
                "records": [
                    {
                        "event_state_record_id": r["event_state_record_id"],
                        "normalized_event_state_content_fingerprint": normalized_event_state_content_fingerprint(r),
                    }
                    for r in sorted(baseline_records, key=lambda x: x["event_state_record_id"])
                ],
                "ledger": baseline_ledger,
            }
        ),
        "rerun_normalized_logical_dataset_fingerprint": normalized_logical_dataset_fingerprint,
        "baseline_physical_candidate_dataset_fingerprint": contract["baseline"]["baseline_candidate_dataset_fingerprint"],
        "rerun_physical_candidate_dataset_fingerprint": event_state_candidate_dataset_fingerprint,
        "normalization_policy": {
            "excluded_row_fields": sorted(RUNTIME_ROW_FIELDS),
            "normalized_lineage_fields": sorted(RUNTIME_LINEAGE_FIELDS),
            "normalized_execution_plan_fields": ["resolved_at_utc"],
            "reason": "Event State materialization runtime identity is allowed to differ by the rerun authorization.",
        },
        "reuse_eligibility_transition_ready": not blocking_failures,
        "reuse_eligibility_changed_by_this_gate": False,
    }
    comparison["comparison_fingerprint"] = sha256_payload(comparison)
    write_json(run_dir / "event_state_bounded_deterministic_rerun_comparison_v0_1.json", comparison)
    write_json(
        run_dir / "determinism_report.json",
        {
            "determinism_status": determinism_status,
            "runtime_differences_only": bool(runtime_only_differences) and not blocking_failures,
            "blocking_failures": blocking_failures,
            "comparison_fingerprint": comparison["comparison_fingerprint"],
            "reuse_transition_ready": not blocking_failures,
            "reuse_eligibility_after_rerun": "pending_determinism_validation",
        },
    )

    evidence_entry = {
        "evidence_entry_id": "event_state_deterministic_rerun_evidence_v0_1_" + comparison["comparison_fingerprint"][:16],
        "evidence_kind": "deterministic_rerun_evidence",
        "baseline_dataset_id": baseline_registry["dataset_id"],
        "baseline_run_id": contract["baseline"]["baseline_execution_run_id"],
        "rerun_run_id": run_id,
        "determinism_status": determinism_status,
        "comparison_fingerprint": comparison["comparison_fingerprint"],
        "baseline_normalized_logical_dataset_fingerprint": comparison["baseline_normalized_logical_dataset_fingerprint"],
        "rerun_normalized_logical_dataset_fingerprint": normalized_logical_dataset_fingerprint,
        "normalized_logical_dataset_fingerprint_match": comparison["baseline_normalized_logical_dataset_fingerprint"]
        == normalized_logical_dataset_fingerprint,
        "event_state_physical_candidate_dataset_fingerprint_match": event_state_candidate_dataset_fingerprint
        == contract["baseline"]["baseline_candidate_dataset_fingerprint"],
        "reuse_eligibility": "pending_determinism_validation",
        "new_normal_candidate_dataset_identity_created": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    evidence_entry["evidence_entry_fingerprint"] = sha256_payload(evidence_entry)
    write_json(run_dir / "deterministic_rerun_evidence_entry.json", evidence_entry)

    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "run_status": final_status, "updated_at_utc": utc_now()})
    append_jsonl(run_dir / "heartbeat.jsonl", {"run_id": run_id, "run_status": final_status, "updated_at_utc": utc_now()})
    ended = utc_now()
    final = {
        **pre_run_manifest,
        "status": final_status,
        "final_run_status": final_status,
        "completed_at_utc": ended,
        "event_state_candidate_records_emitted": validation["event_state_records_emitted"],
        "requested_contexts": validation["requested_contexts"],
        "represented_contexts": validation["represented_contexts"],
        "unavailable_contexts": validation["unavailable_contexts"],
        "event_instances_created": validation["event_instances_created"],
        "event_window_bindings_created": validation["event_window_bindings_created"],
        "instrument_session_projections_created": validation["instrument_session_projections_created"],
        "missing_exact_market_state_bindings": validation["missing_exact_market_state_bindings"],
        "fallback_uses": validation["fallback_uses"],
        "hard_validation_failures": hard,
        "event_state_materializer_executed": True,
        "reuse_existing_event_state_candidate_output": False,
        "market_state_candidate_files_read": 1,
        "market_state_candidate_records_read": len(market_state_df),
        "market_state_not_rematerialized_by_this_gate": True,
        "source_market_data_rows_read": 0,
        "event_state_candidate_files_written": 1,
        "candidate_dataset_registry_entries_written": 0,
        "deterministic_rerun_evidence_entries_written": 1,
        "determinism_comparisons_created": 1,
        "reuse_eligibility_changes": 0,
        "candidate_dataset_fingerprint": event_state_candidate_dataset_fingerprint,
        "event_state_execution_plan_semantics_fingerprint": rerun_plan_semantics_fp,
        "baseline_event_state_execution_plan_semantics_fingerprint": baseline_plan_semantics_fp,
        "normalized_logical_dataset_fingerprint": normalized_logical_dataset_fingerprint,
        "validation_result_fingerprint": validation_fp,
        "comparison_fingerprint": comparison["comparison_fingerprint"],
        "determinism_status": determinism_status,
        "runtime_only_differences": runtime_only_differences,
        "blocking_failures": blocking_failures,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": NEXT_GATE,
        "artifacts": {
            "authorization_consumption_record": str(run_dir / "authorization_consumption_record.json"),
            "rerun_request_record": str(run_dir / "rerun_request_record.json"),
            "rerun_dependency_resolution_report": str(run_dir / "rerun_dependency_resolution_report.json"),
            "rerun_execution_plan": str(run_dir / "rerun_execution_plan.json"),
            "pre_run_manifest": str(run_dir / "pre_run_manifest.json"),
            "run_manifest": str(run_dir / "run_manifest.json"),
            "event_instance_manifest": str(run_dir / "event_instance_manifest.json"),
            "event_window_binding_manifest": str(run_dir / "event_window_binding_manifest.json"),
            "instrument_session_projection_manifest": str(run_dir / "instrument_session_projection_manifest.json"),
            "market_state_dependency_binding_report": str(run_dir / "market_state_dependency_binding_report.json"),
            "event_state_logical_context_ledger": str(run_dir / "event_state_logical_context_ledger.json"),
            "event_state_candidate_records": str(records_path),
            "event_state_candidate_output_manifest": str(run_dir / "event_state_candidate_output_manifest.json"),
            "event_state_lineage_manifest": str(run_dir / "event_state_lineage_manifest.json"),
            "event_state_validation_report": str(run_dir / "event_state_validation_report.json"),
            "validation_evidence_manifest": str(run_dir / "validation_evidence_manifest.json"),
            "event_state_bounded_deterministic_rerun_comparison": str(
                run_dir / "event_state_bounded_deterministic_rerun_comparison_v0_1.json"
            ),
            "determinism_report": str(run_dir / "determinism_report.json"),
            "deterministic_rerun_evidence_entry": str(run_dir / "deterministic_rerun_evidence_entry.json"),
            "final_manifest": str(run_dir / "final_manifest.json"),
            "readout": str(run_dir / "event_state_on_demand_bounded_deterministic_rerun_readout_v0_1.md"),
        },
    }
    write_json(run_dir / "final_manifest.json", final)
    readout = f"""# Event State On-Demand Bounded Deterministic Rerun Readout v0.1

Status: `{final_status}`
Run ID: `{run_id}`
Date: `2026-07-28`

```text
baseline_run_id = {contract['baseline']['baseline_execution_run_id']}
requested_contexts = {validation['requested_contexts']}
represented_contexts = {validation['represented_contexts']}
event_state_records_emitted = {validation['event_state_records_emitted']}
unavailable_contexts = {validation['unavailable_contexts']}
missing_exact_market_state_bindings = {validation['missing_exact_market_state_bindings']}
fallback_uses = {validation['fallback_uses']}
hard_validation_failures = {hard}
event_state_materializer_executed = true
reuse_existing_event_state_candidate_output = false
market_state_rematerialized_by_this_gate = false
market_state_candidate_files_read = 1
source_market_data_rows_read = 0
candidate_dataset_registry_entries_written = 0
deterministic_rerun_evidence_entries_written = 1
determinism_comparisons_created = 1
determinism_status = {determinism_status}
blocking_failures = {len(blocking_failures)}
runtime_only_differences = {len(runtime_only_differences)}
reuse_eligibility_changes = 0
official_event_state_dataset = false
production = false
downstream = false
```

The rerun rebuilt Event State from the same governed request and dependency
resolution. It did not reuse the prior Event State candidate output and did not
create a second normal candidate dataset identity.

Market State was resolved as the same runtime dependency and same validated
candidate fingerprint. It was not rematerialized by this gate.

Raw Event State record fingerprints may differ when they include allowed
runtime lineage fields such as the Event State run id. Scientific determinism is
therefore evaluated through normalized record content, canonical record ids,
bindings, state output fingerprints, unavailable context preservation and the
unchanged Market State dependency fingerprints.

## Next Gate

```text
{NEXT_GATE}
```
"""
    (run_dir / "event_state_on_demand_bounded_deterministic_rerun_readout_v0_1.md").write_text(
        readout, encoding="utf-8"
    )
    final["artifacts_sha256"] = {
        name: sha256_file(Path(path))
        for name, path in final["artifacts"].items()
        if name != "final_manifest" and Path(path).exists()
    }
    final["final_manifest_self_hash_policy"] = "not_recorded_to_avoid_self_referential_hash"
    write_json(run_dir / "final_manifest.json", final)

    print(
        json.dumps(
            {
                "run_id": run_id,
                "status": final_status,
                "determinism_status": determinism_status,
                "requested_contexts": validation["requested_contexts"],
                "event_state_records_emitted": validation["event_state_records_emitted"],
                "unavailable_contexts": validation["unavailable_contexts"],
                "blocking_failures": blocking_failures,
                "runtime_only_differences": runtime_only_differences,
                "run_dir": str(run_dir),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if final_status == PASS_STATUS else 1


if __name__ == "__main__":
    try:
        raise SystemExit(build_rerun())
    except RerunError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
