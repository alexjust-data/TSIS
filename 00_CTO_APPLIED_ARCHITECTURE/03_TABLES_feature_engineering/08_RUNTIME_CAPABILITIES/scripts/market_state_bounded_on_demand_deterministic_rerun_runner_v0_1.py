from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


SCRIPT_VERSION = "market_state_bounded_on_demand_deterministic_rerun_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
FEATURE_ROOT = BASE.parent
MARKET_ROOT = FEATURE_ROOT / "06_MARKET_STATE_INTEGRATION"
OUTPUT_ROOT = BASE / "runs"
BASELINE_RUN_DIR = OUTPUT_ROOT / "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z"
AUTH_SCOPE_PATH = BASE / "configs" / "market_state_bounded_on_demand_deterministic_rerun_scope_v0_1.json"
RERUN_CONTRACT_PATH = BASE / "market_state_bounded_on_demand_deterministic_rerun_contract_v0_1.json"
BASE_RUNNER_PATH = BASE / "scripts" / "market_state_bounded_on_demand_execution_runner_v0_1.py"
SOURCE_MATERIALIZATION_SCOPE_PATH = (
    MARKET_ROOT / "configs" / "experimental_core_four_market_state_scale_c_candidate_materialization_scope_v0_1.json"
)
PROFILE_ROOT = MARKET_ROOT / "official_profiles" / "market_state_core_four_intraday_profile_v0_1"
PROFILE_MANIFEST_PATH = PROFILE_ROOT / "PROFILE_MANIFEST.json"
PROFILE_SCHEMA_PATH = PROFILE_ROOT / "PHYSICAL_SCHEMA_CONTRACT.json"
VALIDATOR_CONTRACT_PATH = BASE / "market_state_validator_contract_v0_1.json"


class RerunError(RuntimeError):
    pass


def load_base_runner() -> Any:
    spec = importlib.util.spec_from_file_location("market_state_bounded_base_runner", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RerunError(f"Cannot import base runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_runner()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_payload(payload: Any) -> str:
    return base.sha256_payload(payload)


def sha256_file(path: Path) -> str:
    return base.sha256_file(path)


def normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return value


def canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): canonicalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [canonicalize(v) for v in value]
    return normalize(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: base.serialize_cell(row.get(k)) for k in fieldnames})


def require_file(path: Path) -> None:
    if not path.exists():
        raise RerunError(f"Required file missing: {path}")


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def normalized_execution_plan(plan: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(plan, default=str))
    normalized.pop("execution_plan_fingerprint", None)
    normalized["execution_plan_status"] = "<AUTHORIZED_EXECUTION_STATUS>"
    if "quantitative_limits" in normalized:
        limits = normalized["quantitative_limits"]
        normalized["quantitative_limits"] = {
            "maximum_requests": limits.get("maximum_requests"),
            "maximum_execution_plans": limits.get("maximum_execution_plans"),
            "maximum_runs": limits.get("maximum_runs"),
            "maximum_instruments": limits.get("maximum_instruments"),
            "maximum_sessions": limits.get("maximum_sessions"),
            "maximum_instrument_session_contexts": limits.get("maximum_instrument_session_contexts"),
            "run_artifact_entry_limit": "<RUN_ARTIFACT_ENTRY_LIMIT>",
        }
    if "output_plan" in normalized:
        normalized["output_plan"] = {
            "output_mode": normalized["output_plan"].get("output_mode"),
            "candidate_output_root": "<RUN_LOCAL_OUTPUT_ROOT>",
            "candidate_parquet_filename": "<RUN_LOCAL_CANDIDATE_PARQUET>",
            "candidate_registry_entry_filename": "<RUN_LOCAL_REGISTRY_OR_EVIDENCE_ENTRY>",
        }
    return normalized


def normalized_row(row: dict[str, Any]) -> dict[str, Any]:
    excluded = {
        "materialization_run_id",
    }
    return {k: canonicalize(v) for k, v in sorted(row.items()) if k not in excluded}


def normalized_rows_from_parquet(path: Path) -> list[dict[str, Any]]:
    rows = pq.read_table(path).to_pylist()
    return sorted(
        (normalized_row(row) for row in rows),
        key=lambda row: (
            row.get("materialized_state_candidate_id", ""),
            row.get("instrument_id", ""),
            row.get("decision_timestamp_utc", ""),
        ),
    )


def canonical_contexts(rows: list[dict[str, Any]]) -> list[str]:
    return sorted(
        f"{row['instrument_id']}|{row['session_date']}|{row['decision_timestamp_utc']}"
        for row in rows
    )


def unavailable_context_signature(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "instrument_id": context["instrument_id"],
        "session_date": context["session_date"],
        "exchange_id": context["exchange_id"],
        "decision_timestamp_utc": context["decision_timestamp_utc"],
        "disposition": context.get("disposition") or context.get("partition_disposition"),
        "reason": context.get("blocking_reason") or context.get("disposition_cause"),
        "available_same_instrument_session_timestamps": sorted(context.get("available_same_instrument_session_timestamps") or []),
    }


def scientific_dataset_fingerprint(
    request_fingerprint: str,
    execution_plan_semantics_fingerprint: str,
    schema_contract_sha256: str,
    rows: list[dict[str, Any]],
    unavailable_contexts: list[dict[str, Any]],
) -> str:
    return sha256_payload(
        {
            "request_fingerprint": request_fingerprint,
            "execution_plan_semantics_fingerprint": execution_plan_semantics_fingerprint,
            "schema_contract_sha256": schema_contract_sha256,
            "normalized_rows": rows,
            "unavailable_contexts": sorted(
                (unavailable_context_signature(ctx) for ctx in unavailable_contexts),
                key=lambda ctx: (ctx["instrument_id"], ctx["session_date"], ctx["decision_timestamp_utc"]),
            ),
        }
    )


def build_rerun() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    for path in [
        AUTH_SCOPE_PATH,
        RERUN_CONTRACT_PATH,
        BASELINE_RUN_DIR / "final_manifest.json",
        BASELINE_RUN_DIR / "request_record.json",
        BASELINE_RUN_DIR / "execution_plan.json",
        BASELINE_RUN_DIR / "candidate_registry_entry.json",
        BASELINE_RUN_DIR / "lineage_manifest.json",
        BASELINE_RUN_DIR / "market_state_validation_report.json",
        SOURCE_MATERIALIZATION_SCOPE_PATH,
        PROFILE_MANIFEST_PATH,
        PROFILE_SCHEMA_PATH,
        VALIDATOR_CONTRACT_PATH,
    ]:
        require_file(path)

    auth_scope = read_json(AUTH_SCOPE_PATH)
    rerun_contract = read_json(RERUN_CONTRACT_PATH)
    baseline = rerun_contract["baseline"]
    baseline_final = read_json(BASELINE_RUN_DIR / "final_manifest.json")
    baseline_request = read_json(BASELINE_RUN_DIR / "request_record.json")
    baseline_plan = read_json(BASELINE_RUN_DIR / "execution_plan.json")
    baseline_registry = read_json(BASELINE_RUN_DIR / "candidate_registry_entry.json")
    baseline_lineage = read_json(BASELINE_RUN_DIR / "lineage_manifest.json")
    baseline_validation = read_json(BASELINE_RUN_DIR / "market_state_validation_report.json")
    source_scope = read_json(SOURCE_MATERIALIZATION_SCOPE_PATH)
    profile_manifest = read_json(PROFILE_MANIFEST_PATH)
    schema_contract = read_json(PROFILE_SCHEMA_PATH)

    baseline_parquet = Path(baseline_final["artifacts"]["candidate_parquet"])
    require_file(baseline_parquet)
    baseline_rows = normalized_rows_from_parquet(baseline_parquet)

    baseline_checks = {
        "baseline_run_id_match": baseline_final["run_id"] == baseline["baseline_run_id"],
        "baseline_candidate_dataset_fingerprint_match": baseline_final["candidate_dataset_fingerprint"]
        == baseline["baseline_candidate_dataset_fingerprint"],
        "baseline_rows_match": baseline_final["materialized_candidate_rows"] == baseline["baseline_candidate_rows"],
        "baseline_unavailable_contexts_match": baseline_final["unavailable_contexts"] == baseline["baseline_unavailable_contexts"],
        "baseline_request_fingerprint_match": baseline_final["request_fingerprint"] == baseline["baseline_request_fingerprint"],
        "baseline_execution_plan_fingerprint_match": baseline_final["execution_plan_fingerprint"]
        == baseline["baseline_execution_plan_fingerprint"],
        "baseline_source_hash_match": baseline_lineage["source_resolution"]["source_sha256"] == baseline["baseline_source_sha256"],
        "baseline_registry_entry_match": baseline_registry["registry_entry_fingerprint"] == baseline["baseline_registry_entry_fingerprint"],
    }
    if not all(baseline_checks.values()):
        run_id = "market_state_bounded_on_demand_deterministic_rerun_v0_1_BLOCKED_" + datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )
        run_dir = OUTPUT_ROOT / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        final_manifest = {
            "run_id": run_id,
            "status": "CLOSED_BLOCKED_BASELINE_AUTHORITIES_CHANGED",
            "created_at_utc": utc_now(),
            "baseline_checks": baseline_checks,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        }
        write_json(run_dir / "final_manifest.json", final_manifest)
        print(json.dumps(final_manifest, indent=2))
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"market_state_bounded_on_demand_deterministic_rerun_v0_1_{timestamp}"
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists():
        raise RerunError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

    request = dict(baseline_request)
    request["rerun_record_id"] = "market_state_bounded_on_demand_deterministic_rerun_request_v0_1_" + baseline[
        "baseline_request_fingerprint"
    ][:16]
    request["rerun_of_request_id"] = baseline["baseline_request_id"]
    request["rerun_record_created_at_utc"] = utc_now()
    request["rerun_policy"] = "force_rebuild_for_determinism_test"
    write_json(run_dir / "rerun_request_record.json", request)
    write_json(run_dir / "request_record.json", request)
    request_fingerprint = request["request_fingerprint"]

    column_order, column_defs, arrow_schema = base.schema_from_contract(schema_contract)
    schema_version = schema_contract["state_schema_version"]
    profile_id = request["profile_id"]
    profile_resolution = {
        "resolution_status": "RESOLVED_EXACTLY_ONE",
        "resolved_profile_id": profile_id,
        "resolved_profile_version": request["profile_version"],
        "profile_manifest": str(PROFILE_MANIFEST_PATH),
        "profile_manifest_sha256": sha256_file(PROFILE_MANIFEST_PATH),
        "profile_schema_contract": str(PROFILE_SCHEMA_PATH),
        "profile_schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
        "expected_schema_id": schema_contract["source_physical_profile_id"],
        "expected_state_schema_version": schema_version,
        "expected_grain": request["grain"],
        "required_source_aliases": ["scale_c_integrated_market_state_candidate_records"],
        "profile_artifact_validation_run": profile_manifest.get("artifact_validation_run_id"),
    }
    resolved_profile_fingerprint = sha256_payload(profile_resolution)
    profile_resolution["resolved_profile_fingerprint"] = resolved_profile_fingerprint
    write_json(run_dir / "rerun_profile_resolution_report.json", profile_resolution)
    write_json(run_dir / "profile_resolution_report.json", profile_resolution)

    source_records_path = (SOURCE_MATERIALIZATION_SCOPE_PATH.parent / source_scope["input_artifacts"]["market_state_candidate_records"]).resolve()
    records = base.read_jsonl(source_records_path)
    source_records_read = len(records)
    session_open_by_date: dict[str, str] = {}
    available_by_instrument_session: dict[tuple[str, str], list[str]] = {}
    exact_record_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in records:
        session_open_by_date.setdefault(record["session_date"], record["session_open_utc"])
        available_by_instrument_session.setdefault((record["instrument_id"], record["session_date"]), []).append(
            record["decision_timestamp_utc"]
        )
        exact_record_by_key[(record["instrument_id"], record["session_date"], record["decision_timestamp_utc"])] = record

    universe_contexts: list[dict[str, Any]] = []
    partition_rows: list[dict[str, Any]] = []
    selected_records: list[dict[str, Any]] = []
    unavailable_contexts: list[dict[str, Any]] = []
    for session_date_value in request["session_dates"]:
        anchor = session_open_by_date.get(session_date_value)
        if not anchor:
            raise RerunError(f"No governed session open found in source records for {session_date_value}")
        for instrument_id in request["explicit_instrument_ids"]:
            ticker = request["instrument_labels_non_authoritative"].get(instrument_id, "")
            context = {
                "instrument_id": instrument_id,
                "ticker_label_non_authoritative": ticker,
                "session_date": session_date_value,
                "exchange_id": "XNYS",
                "decision_timestamp_utc": anchor,
                "calendar_authority_id": request["calendar_authority_id"],
                "membership_status": "AUTHORIZED_EXPLICIT_SCOPE",
                "point_in_time_eligibility": "not_revalidated_in_bounded_run",
            }
            universe_contexts.append(context)
            logical_partition_id = sha256_payload(
                {
                    "profile_id": profile_id,
                    "instrument_id": instrument_id,
                    "session_date": session_date_value,
                    "decision_timestamp_utc": anchor,
                }
            )
            record = exact_record_by_key.get((instrument_id, session_date_value, anchor))
            if record:
                selected_records.append(record)
                disposition = "to_build"
                cause = ""
            else:
                disposition = "unavailable"
                cause = "missing_exact_decision_timestamp_source_candidate_record"
                unavailable_contexts.append(
                    {
                        **context,
                        "logical_partition_id": logical_partition_id,
                        "disposition": disposition,
                        "blocking_reason": cause,
                        "available_same_instrument_session_timestamps": sorted(
                            set(available_by_instrument_session.get((instrument_id, session_date_value), []))
                        ),
                    }
                )
            partition_rows.append(
                {
                    **context,
                    "logical_partition_id": logical_partition_id,
                    "partition_disposition": disposition,
                    "disposition_cause": cause,
                    "available_same_instrument_session_timestamps": sorted(
                        set(available_by_instrument_session.get((instrument_id, session_date_value), []))
                    ),
                }
            )

    universe_resolution = {
        "resolution_status": "RESOLVED_WITH_RESTRICTIONS",
        "resolved_universe_definition_id": "explicit_instrument_ids",
        "instrument_count": len(request["explicit_instrument_ids"]),
        "session_count": len(request["session_dates"]),
        "requested_contexts": len(universe_contexts),
        "resolved_contexts": len(universe_contexts),
        "blocked_contexts": 0,
        "excluded_contexts": 0,
        "contexts": universe_contexts,
    }
    resolved_universe_fingerprint = sha256_payload(universe_resolution)
    universe_resolution["resolved_universe_fingerprint"] = resolved_universe_fingerprint
    write_json(run_dir / "rerun_universe_resolution_report.json", universe_resolution)
    write_json(run_dir / "universe_resolution_report.json", universe_resolution)

    source_resolution = {
        "resolution_status": "RESOLVED_EXACTLY_ONE",
        "resolved_source_alias": "scale_c_integrated_market_state_candidate_records",
        "source_artifact_kind": "integrated_market_state_candidate_records_jsonl",
        "source_path": str(source_records_path),
        "source_sha256": sha256_file(source_records_path),
        "source_bytes": source_records_path.stat().st_size,
        "source_candidate_records_read": source_records_read,
        "source_market_data_rows_read": 0,
        "source_scope_contract": str(SOURCE_MATERIALIZATION_SCOPE_PATH),
        "source_scope_contract_sha256": sha256_file(SOURCE_MATERIALIZATION_SCOPE_PATH),
        "source_version_policy": request["source_version_policy"],
        "fallback_used": False,
    }
    resolved_source_set_fingerprint = sha256_payload(source_resolution)
    source_resolution["resolved_source_set_fingerprint"] = resolved_source_set_fingerprint
    write_json(run_dir / "rerun_source_resolution_report.json", source_resolution)
    write_json(run_dir / "source_resolution_report.json", source_resolution)

    disposition_counts = Counter(row["partition_disposition"] for row in partition_rows)
    partition_coverage = {
        "resolution_status": "PARTIALLY_BUILDABLE_WITH_RESTRICTIONS",
        "logical_partition_grain": "profile_id+instrument_id+session_date+decision_timestamp_utc",
        "requested_logical_partitions": len(partition_rows),
        "reusable_validated": disposition_counts["reusable_validated"],
        "to_build": disposition_counts["to_build"],
        "to_rebuild": disposition_counts["to_rebuild"],
        "unavailable": disposition_counts["unavailable"],
        "quarantined": disposition_counts["quarantined"],
        "blocked": disposition_counts["blocked"],
        "missing_is_independent_disposition": False,
        "missing_source_coverage_policy": "cause_of_unavailable",
        "partial_execution_policy": "allowed_for_reported_unavailable_partitions_in_this_bounded_run",
        "partitions": partition_rows,
    }
    partition_coverage_fingerprint = sha256_payload(partition_coverage)
    partition_coverage["partition_coverage_resolution_fingerprint"] = partition_coverage_fingerprint
    write_json(run_dir / "rerun_partition_coverage_resolution_report.json", partition_coverage)
    write_json(run_dir / "partition_coverage_resolution_report.json", partition_coverage)
    write_csv(
        run_dir / "rerun_partition_coverage_resolution_report.csv",
        partition_rows,
        [
            "logical_partition_id",
            "instrument_id",
            "ticker_label_non_authoritative",
            "session_date",
            "exchange_id",
            "decision_timestamp_utc",
            "partition_disposition",
            "disposition_cause",
            "available_same_instrument_session_timestamps",
        ],
    )

    execution_plan = {
        "execution_plan_id": "market_state_execution_plan_v0_1_" + sha256_payload(partition_coverage)[:16],
        "execution_plan_contract_version": "market_state_execution_plan_contract_v0_1",
        "execution_plan_status": "authorized_for_deterministic_rerun_execution",
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "resolved_profile": profile_resolution,
        "resolved_universe_and_scope": universe_resolution,
        "resolved_sources": source_resolution,
        "partition_and_coverage": partition_coverage,
        "resolved_builders": {
            "builder_id": "scale_c_integrated_candidate_record_to_market_state_physical_row_v0_1",
            "builder_contract_hash": sha256_file(SOURCE_MATERIALIZATION_SCOPE_PATH),
            "source_materialization_scope": str(SOURCE_MATERIALIZATION_SCOPE_PATH),
        },
        "resolved_validators": {
            "validator_id": "market_state_bounded_on_demand_validator_v0_1",
            "validator_contract_hash": sha256_file(VALIDATOR_CONTRACT_PATH),
        },
        "output_plan": {
            "output_mode": "candidate",
            "candidate_output_root": str(run_dir),
            "candidate_parquet_filename": "market_state_bounded_on_demand_deterministic_rerun_candidate_v0_1.parquet",
            "candidate_registry_entry_filename": "deterministic_rerun_evidence_entry.json",
        },
        "quantitative_limits": {
            "maximum_requests": 1,
            "maximum_execution_plans": 1,
            "maximum_runs": 1,
            "maximum_instruments": 3,
            "maximum_sessions": 3,
            "maximum_instrument_session_contexts": 9,
            "maximum_candidate_dataset_registry_entries": 0,
            "maximum_rerun_evidence_entries": 1,
        },
    }
    execution_plan_fingerprint = sha256_payload(execution_plan)
    execution_plan["execution_plan_fingerprint"] = execution_plan_fingerprint
    execution_plan_semantics_fingerprint = sha256_payload(normalized_execution_plan(execution_plan))
    write_json(run_dir / "rerun_execution_plan.json", execution_plan)
    write_json(run_dir / "execution_plan.json", execution_plan)

    authorization_consumption = {
        "authorization_id": auth_scope["gate"],
        "authorization_document_status_observed": auth_scope["status"],
        "authorization_consumption_status": "CONSUMED_BY_RERUN",
        "execution_run_id": run_id,
        "baseline_run_id": baseline["baseline_run_id"],
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "execution_plan_semantics_fingerprint": execution_plan_semantics_fingerprint,
        "consumed_at_utc": utc_now(),
    }
    write_json(run_dir / "authorization_consumption_record.json", authorization_consumption)

    pre_manifest = {
        "run_id": run_id,
        "status": "AUTHORIZED",
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], Path("C:/TSIS_Data")),
        "git_commit": git_value(["git", "rev-parse", "HEAD"], Path("C:/TSIS_Data")),
        "git_dirty_state": bool(git_value(["git", "status", "--porcelain"], Path("C:/TSIS_Data"))),
        "baseline_run_id": baseline["baseline_run_id"],
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "execution_plan_semantics_fingerprint": execution_plan_semantics_fingerprint,
        "run_dir": str(run_dir),
        "reuse_existing_candidate_parquet": False,
        "fresh_materializer_execution_required": True,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "pre_run_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": "RUNNING", "stage": "materializing"})

    physical_rows = [
        base.build_row(record, run_id, profile_id, schema_contract["state_schema_version"], source_scope, column_order, column_defs)
        for record in sorted(selected_records, key=lambda r: (r["session_date"], r["instrument_id"], r["decision_timestamp_utc"]))
    ]
    table = pa.Table.from_pylist(physical_rows, schema=arrow_schema)
    parquet_path = run_dir / "market_state_bounded_on_demand_deterministic_rerun_candidate_v0_1.parquet"
    pq.write_table(table, parquet_path, compression="snappy", use_dictionary=False, row_group_size=max(1, len(physical_rows)), coerce_timestamps="us")
    parquet_sha = sha256_file(parquet_path)
    base.write_jsonl(run_dir / "rerun_candidate_market_state_rows.jsonl", [{k: normalize(v) for k, v in row.items()} for row in physical_rows])

    candidate_dataset_fingerprint = sha256_payload(
        {
            "request_fingerprint": request_fingerprint,
            "execution_plan_fingerprint": execution_plan_fingerprint,
            "parquet_sha256": parquet_sha,
            "row_count": len(physical_rows),
            "partition_coverage_fingerprint": partition_coverage_fingerprint,
        }
    )
    candidate_manifest = {
        "candidate_dataset_id": "market_state_candidate_dataset_v0_1_" + candidate_dataset_fingerprint[:16],
        "candidate_dataset_status": "deterministic_rerun_candidate_pending_validation",
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "execution_plan_semantics_fingerprint": execution_plan_semantics_fingerprint,
        "profile_id": profile_id,
        "coverage": {
            "requested_contexts": len(partition_rows),
            "materialized_contexts": len(physical_rows),
            "unavailable_contexts": disposition_counts["unavailable"],
        },
        "files": [{"path": str(parquet_path), "sha256": parquet_sha, "bytes": parquet_path.stat().st_size, "rows": len(physical_rows)}],
        "schema_contract": str(PROFILE_SCHEMA_PATH),
        "schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
    }
    write_json(run_dir / "rerun_candidate_manifest.json", candidate_manifest)
    write_json(run_dir / "candidate_output_manifest.json", candidate_manifest)

    lineage_manifest = {
        "run_id": run_id,
        "baseline_run_id": baseline["baseline_run_id"],
        "source_resolution": source_resolution,
        "source_candidate_records_used": [
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "instrument_id": row["instrument_id"],
                "ticker": row["ticker"],
                "session_date": normalize(row["session_date"]),
                "decision_timestamp_utc": normalize(row["decision_timestamp_utc"]),
                "context_input_fingerprint": row["context_input_fingerprint"],
            }
            for row in physical_rows
        ],
        "unavailable_contexts": unavailable_contexts,
        "reuse_existing_candidate_parquet": False,
    }
    write_json(run_dir / "rerun_lineage_manifest.json", lineage_manifest)
    write_json(run_dir / "lineage_manifest.json", lineage_manifest)

    observed_rows = pq.read_table(parquet_path).to_pylist()
    schema_match = [field.name for field in pq.read_schema(parquet_path)] == column_order
    primary_key_fields = ["instrument_id", "decision_timestamp_utc", "state_profile_id", "state_schema_version"]
    primary_keys = [tuple(normalize(row[field]) for field in primary_key_fields) for row in observed_rows]
    duplicate_primary_keys = sum(count - 1 for count in Counter(primary_keys).values() if count > 1)
    null_failures = sum(1 for row in observed_rows for name in column_order if row.get(name) is None and not column_defs[name]["nullable"])

    fingerprint_failures = 0
    fp_fields = source_scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
    id_fields = source_scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
    fingerprint_rows: list[dict[str, Any]] = []
    for row in observed_rows:
        recalculated_state = base.row_fingerprint(row, fp_fields)
        recalculated_id = base.row_fingerprint({**row, "state_output_fingerprint": recalculated_state}, id_fields)
        state_match = recalculated_state == row["state_output_fingerprint"]
        id_match = recalculated_id == row["materialized_state_candidate_id"]
        if not state_match or not id_match:
            fingerprint_failures += 1
        fingerprint_rows.append(
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
                "recalculated_state_output_fingerprint": recalculated_state,
                "state_output_fingerprint_match": state_match,
                "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                "recalculated_materialized_state_candidate_id": recalculated_id,
                "materialized_state_candidate_id_match": id_match,
            }
        )
    write_csv(
        run_dir / "rerun_fingerprint_validation_report.csv",
        fingerprint_rows,
        [
            "source_candidate_record_id",
            "state_output_fingerprint",
            "recalculated_state_output_fingerprint",
            "state_output_fingerprint_match",
            "materialized_state_candidate_id",
            "recalculated_materialized_state_candidate_id",
            "materialized_state_candidate_id_match",
        ],
    )

    temporal_failures = 0
    temporal_rows: list[dict[str, Any]] = []
    for row in observed_rows:
        expected_anchor = session_open_by_date[normalize(row["session_date"])]
        ok = normalize(row["decision_timestamp_utc"]) == expected_anchor
        temporal_failures += 0 if ok else 1
        temporal_rows.append(
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "session_date": normalize(row["session_date"]),
                "decision_timestamp_utc": normalize(row["decision_timestamp_utc"]),
                "expected_session_open_utc": expected_anchor,
                "temporal_legality_pass": ok,
            }
        )
    write_json(run_dir / "rerun_market_state_temporal_legality_report.json", {"failures": temporal_failures, "rows": temporal_rows})

    lineage_failures = 0
    for row in observed_rows:
        for field in ["source_lineage_json", "policy_versions_json", "formula_versions_json", "restriction_codes_json"]:
            try:
                json.loads(row[field])
            except Exception:
                lineage_failures += 1
    write_json(
        run_dir / "rerun_market_state_lineage_validation_report.json",
        {"lineage_json_parse_failures": lineage_failures, "lineage_manifest": str(run_dir / "rerun_lineage_manifest.json")},
    )

    partition_validation = {
        "requested_logical_partitions": len(partition_rows),
        "reusable_validated": disposition_counts["reusable_validated"],
        "to_build": disposition_counts["to_build"],
        "to_rebuild": disposition_counts["to_rebuild"],
        "unavailable": disposition_counts["unavailable"],
        "quarantined": disposition_counts["quarantined"],
        "blocked": disposition_counts["blocked"],
        "materialized_partitions": len(observed_rows),
        "partition_accounting_pass": len(partition_rows)
        == sum(disposition_counts[state] for state in ["reusable_validated", "to_build", "to_rebuild", "unavailable", "quarantined", "blocked"]),
    }
    write_json(run_dir / "rerun_market_state_partition_validation_report.json", partition_validation)

    validation_hard_failures = sum(
        [
            0 if schema_match else 1,
            duplicate_primary_keys,
            null_failures,
            fingerprint_failures,
            temporal_failures,
            lineage_failures,
            0 if partition_validation["partition_accounting_pass"] else 1,
        ]
    )
    validation_status = "PASS_WITH_RESTRICTIONS" if validation_hard_failures == 0 else "FAIL"
    validation_report = {
        "validation_status": validation_status,
        "schema_match": schema_match,
        "row_count": len(observed_rows),
        "duplicate_primary_keys": duplicate_primary_keys,
        "non_nullable_null_failures": null_failures,
        "fingerprint_failures": fingerprint_failures,
        "temporal_failures": temporal_failures,
        "lineage_failures": lineage_failures,
        "partition_accounting_pass": partition_validation["partition_accounting_pass"],
        "hard_validation_failures": validation_hard_failures,
        "eligible_for_candidate_registry": False,
        "eligible_for_rerun_evidence": validation_hard_failures == 0,
        "reuse_eligibility": "pending_determinism_validation",
        "promotion_review_eligibility": "not_eligible_deterministic_rerun_evidence_only",
    }
    validation_result_fingerprint = sha256_payload(validation_report)
    validation_report["validation_result_fingerprint"] = validation_result_fingerprint
    write_json(run_dir / "rerun_market_state_validation_report.json", validation_report)
    write_json(run_dir / "market_state_validation_report.json", validation_report)
    write_json(
        run_dir / "rerun_validation_evidence_manifest.json",
        {
            "validation_result_fingerprint": validation_result_fingerprint,
            "reports": {
                "rerun_market_state_validation_report": str(run_dir / "rerun_market_state_validation_report.json"),
                "rerun_market_state_partition_validation_report": str(run_dir / "rerun_market_state_partition_validation_report.json"),
                "rerun_market_state_temporal_legality_report": str(run_dir / "rerun_market_state_temporal_legality_report.json"),
                "rerun_market_state_lineage_validation_report": str(run_dir / "rerun_market_state_lineage_validation_report.json"),
                "rerun_fingerprint_validation_report": str(run_dir / "rerun_fingerprint_validation_report.csv"),
            },
        },
    )

    rerun_rows = normalized_rows_from_parquet(parquet_path)
    baseline_plan_semantics_fingerprint = sha256_payload(normalized_execution_plan(baseline_plan))
    baseline_scientific_fingerprint = scientific_dataset_fingerprint(
        baseline_final["request_fingerprint"],
        baseline_plan_semantics_fingerprint,
        baseline["baseline_schema_contract_sha256"],
        baseline_rows,
        baseline_lineage["unavailable_contexts"],
    )
    rerun_scientific_fingerprint = scientific_dataset_fingerprint(
        request_fingerprint,
        execution_plan_semantics_fingerprint,
        sha256_file(PROFILE_SCHEMA_PATH),
        rerun_rows,
        unavailable_contexts,
    )

    comparison_checks = {
        "request_fingerprint_match": request_fingerprint == baseline["baseline_request_fingerprint"],
        "profile_fingerprint_match": resolved_profile_fingerprint == baseline["baseline_resolved_profile_fingerprint"],
        "universe_fingerprint_match": resolved_universe_fingerprint == baseline["baseline_resolved_universe_fingerprint"],
        "source_set_fingerprint_match": resolved_source_set_fingerprint == baseline["baseline_resolved_source_set_fingerprint"],
        "partition_coverage_fingerprint_match": partition_coverage_fingerprint
        == baseline["baseline_partition_coverage_resolution_fingerprint"],
        "physical_execution_plan_fingerprint_match": execution_plan_fingerprint == baseline["baseline_execution_plan_fingerprint"],
        "execution_plan_semantics_fingerprint_match": execution_plan_semantics_fingerprint == baseline_plan_semantics_fingerprint,
        "physical_candidate_dataset_fingerprint_match": candidate_dataset_fingerprint
        == baseline["baseline_candidate_dataset_fingerprint"],
        "scientific_dataset_fingerprint_match": rerun_scientific_fingerprint == baseline_scientific_fingerprint,
        "schema_hash_match": sha256_file(PROFILE_SCHEMA_PATH) == baseline["baseline_schema_contract_sha256"],
        "row_count_match": len(rerun_rows) == len(baseline_rows),
        "column_count_match": len(observed_rows[0]) == len(pq.read_table(baseline_parquet).to_pylist()[0]),
        "state_id_set_match": sorted(row["materialized_state_candidate_id"] for row in rerun_rows)
        == baseline["baseline_state_ids"],
        "state_output_fingerprint_set_match": sorted(row["state_output_fingerprint"] for row in rerun_rows)
        == baseline["baseline_state_output_fingerprints"],
        "canonical_context_set_match": canonical_contexts(rerun_rows) == canonical_contexts(baseline_rows),
        "unavailable_context_set_match": sorted(
            (unavailable_context_signature(ctx) for ctx in unavailable_contexts),
            key=lambda ctx: (ctx["instrument_id"], ctx["session_date"], ctx["decision_timestamp_utc"]),
        )
        == sorted(
            (unavailable_context_signature(ctx) for ctx in baseline_lineage["unavailable_contexts"]),
            key=lambda ctx: (ctx["instrument_id"], ctx["session_date"], ctx["decision_timestamp_utc"]),
        ),
        "validation_status_match": validation_status == baseline_validation["validation_status"],
        "hard_validation_failures_match": validation_hard_failures == baseline_validation["hard_validation_failures"],
        "source_sha256_match": source_resolution["source_sha256"] == baseline["baseline_source_sha256"],
        "source_scope_contract_sha256_match": source_resolution["source_scope_contract_sha256"]
        == baseline["baseline_source_scope_contract_sha256"],
        "fresh_materializer_execution_proven": True,
        "reuse_existing_candidate_parquet": False,
    }
    blocking_checks = [
        "request_fingerprint_match",
        "profile_fingerprint_match",
        "universe_fingerprint_match",
        "source_set_fingerprint_match",
        "partition_coverage_fingerprint_match",
        "execution_plan_semantics_fingerprint_match",
        "scientific_dataset_fingerprint_match",
        "schema_hash_match",
        "row_count_match",
        "column_count_match",
        "state_id_set_match",
        "state_output_fingerprint_set_match",
        "canonical_context_set_match",
        "unavailable_context_set_match",
        "validation_status_match",
        "hard_validation_failures_match",
        "source_sha256_match",
        "source_scope_contract_sha256_match",
        "fresh_materializer_execution_proven",
    ]
    blocking_failures = [check for check in blocking_checks if not comparison_checks[check]]
    runtime_only_differences = [
        check
        for check in ["physical_execution_plan_fingerprint_match", "physical_candidate_dataset_fingerprint_match"]
        if not comparison_checks[check]
    ]
    row_comparison = []
    baseline_by_id = {row["materialized_state_candidate_id"]: row for row in baseline_rows}
    rerun_by_id = {row["materialized_state_candidate_id"]: row for row in rerun_rows}
    for state_id in sorted(set(baseline_by_id) | set(rerun_by_id)):
        b = baseline_by_id.get(state_id)
        r = rerun_by_id.get(state_id)
        row_comparison.append(
            {
                "materialized_state_candidate_id": state_id,
                "baseline_row_exists": b is not None,
                "rerun_row_exists": r is not None,
                "state_output_fingerprint_match": bool(b and r and b["state_output_fingerprint"] == r["state_output_fingerprint"]),
                "normalized_row_content_match": b == r,
            }
        )

    determinism_status = "PROVEN_FOR_BOUNDED_SCOPE" if not blocking_failures else "FAILED_FOR_BOUNDED_SCOPE"
    final_status = (
        "CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS"
        if not blocking_failures
        else "CLOSED_BLOCKED_DETERMINISM_FAILURE"
    )
    comparison = {
        "comparison_id": "market_state_deterministic_rerun_comparison_v0_1",
        "baseline_run_id": baseline["baseline_run_id"],
        "rerun_run_id": run_id,
        "determinism_status": determinism_status,
        "final_status": final_status,
        "blocking_failures": blocking_failures,
        "runtime_only_differences": runtime_only_differences,
        "baseline_scientific_dataset_fingerprint": baseline_scientific_fingerprint,
        "rerun_scientific_dataset_fingerprint": rerun_scientific_fingerprint,
        "baseline_execution_plan_semantics_fingerprint": baseline_plan_semantics_fingerprint,
        "rerun_execution_plan_semantics_fingerprint": execution_plan_semantics_fingerprint,
        "checks": comparison_checks,
        "row_comparison": row_comparison,
        "reuse_eligibility_transition_ready": not blocking_failures,
        "reuse_eligibility_changed_by_this_gate": False,
    }
    comparison["comparison_fingerprint"] = sha256_payload(comparison)
    write_json(run_dir / "market_state_deterministic_rerun_comparison_v0_1.json", comparison)
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
        "evidence_entry_id": "market_state_deterministic_rerun_evidence_v0_1_" + comparison["comparison_fingerprint"][:16],
        "evidence_kind": "deterministic_rerun_evidence",
        "baseline_dataset_id": baseline_registry["dataset_id"],
        "baseline_run_id": baseline["baseline_run_id"],
        "rerun_run_id": run_id,
        "determinism_status": determinism_status,
        "baseline_scientific_dataset_fingerprint": baseline_scientific_fingerprint,
        "rerun_scientific_dataset_fingerprint": rerun_scientific_fingerprint,
        "comparison_fingerprint": comparison["comparison_fingerprint"],
        "candidate_dataset_fingerprint_physical_match": comparison_checks["physical_candidate_dataset_fingerprint_match"],
        "scientific_dataset_fingerprint_match": comparison_checks["scientific_dataset_fingerprint_match"],
        "reuse_eligibility": "pending_determinism_validation",
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    evidence_entry["evidence_entry_fingerprint"] = sha256_payload(evidence_entry)
    write_json(run_dir / "deterministic_rerun_evidence_entry.json", evidence_entry)

    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": final_status, "stage": "closed"})
    final_manifest = {
        **pre_manifest,
        "status": final_status,
        "completed_at_utc": utc_now(),
        "source_candidate_records_read": source_records_read,
        "source_market_data_rows_read": 0,
        "requested_contexts": len(partition_rows),
        "materialized_candidate_rows": len(observed_rows),
        "unavailable_contexts": disposition_counts["unavailable"],
        "candidate_parquet_files_written": 1,
        "candidate_registry_entries_written": 0,
        "deterministic_rerun_evidence_entries_written": 1,
        "determinism_comparisons_created": 1,
        "materializer_executed": True,
        "reuse_existing_candidate_parquet": False,
        "reuse_eligibility_changes": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "request_fingerprint": request_fingerprint,
        "resolved_profile_fingerprint": resolved_profile_fingerprint,
        "resolved_universe_fingerprint": resolved_universe_fingerprint,
        "resolved_source_set_fingerprint": resolved_source_set_fingerprint,
        "partition_coverage_resolution_fingerprint": partition_coverage_fingerprint,
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "execution_plan_semantics_fingerprint": execution_plan_semantics_fingerprint,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": rerun_scientific_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "comparison_fingerprint": comparison["comparison_fingerprint"],
        "determinism_status": determinism_status,
        "runtime_only_differences": runtime_only_differences,
        "blocking_failures": blocking_failures,
        "artifacts": {
            "rerun_request_record": str(run_dir / "rerun_request_record.json"),
            "rerun_execution_plan": str(run_dir / "rerun_execution_plan.json"),
            "rerun_candidate_manifest": str(run_dir / "rerun_candidate_manifest.json"),
            "rerun_lineage_manifest": str(run_dir / "rerun_lineage_manifest.json"),
            "rerun_validation_report": str(run_dir / "rerun_market_state_validation_report.json"),
            "deterministic_rerun_comparison": str(run_dir / "market_state_deterministic_rerun_comparison_v0_1.json"),
            "determinism_report": str(run_dir / "determinism_report.json"),
            "deterministic_rerun_evidence_entry": str(run_dir / "deterministic_rerun_evidence_entry.json"),
            "rerun_candidate_parquet": str(parquet_path),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)

    readout = f"""# Market State Bounded On-Demand Deterministic Rerun Readout v0.1

Status: `{final_status}`
Date: `2026-07-25`

```text
run_id = {run_id}
baseline_run_id = {baseline['baseline_run_id']}
requested_contexts = {len(partition_rows)}
materialized_candidate_rows = {len(observed_rows)}
unavailable_contexts = {disposition_counts['unavailable']}
candidate_parquet_files_written = 1
candidate_registry_entries_written = 0
deterministic_rerun_evidence_entries_written = 1
determinism_comparisons_created = 1
source_candidate_records_read = {source_records_read}
source_market_data_rows_read = 0
hard_validation_failures = {validation_hard_failures}
determinism_status = {determinism_status}
blocking_failures = {len(blocking_failures)}
runtime_only_differences = {len(runtime_only_differences)}
reuse_eligibility = pending_determinism_validation
reuse_eligibility_changes = 0
official_dataset = false
production = false
downstream = false
```

The deterministic rerun rebuilt the bounded candidate output from the same
governed request, source evidence, builder and validator authority. It did not
reuse the prior candidate parquet and did not create a second normal candidate
dataset registry entry.

Physical run-local fingerprints may differ when they include output paths or
`materialization_run_id`. Scientific determinism is evaluated through normalized
row content, state ids, state output fingerprints, unavailable context
preservation and normalized execution-plan semantics.

## Next Gate

```text
market_state_bounded_on_demand_determinism_validation_v0_1
```
"""
    (run_dir / "market_state_bounded_on_demand_deterministic_rerun_readout_v0_1.md").write_text(
        readout, encoding="utf-8"
    )

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False, default=str))
    return 0 if not blocking_failures and validation_hard_failures == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(build_rerun())
    except RerunError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
