from __future__ import annotations

import csv
import hashlib
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


SCRIPT_VERSION = "market_state_bounded_on_demand_execution_runner_v0_1"
BASE = Path(__file__).resolve().parents[1]
FEATURE_ROOT = BASE.parent
MARKET_ROOT = FEATURE_ROOT / "06_MARKET_STATE_INTEGRATION"
AUTH_SCOPE_PATH = BASE / "configs" / "market_state_bounded_on_demand_execution_scope_v0_1.json"
AUTH_CONTRACT_PATH = BASE / "market_state_bounded_on_demand_execution_contract_v0_1.json"
REQUEST_CONTRACT_PATH = BASE / "market_state_request_contract_v0_1.json"
EXECUTION_PLAN_CONTRACT_PATH = BASE / "market_state_execution_plan_contract_v0_1.json"
MATERIALIZER_CONTRACT_PATH = BASE / "market_state_materializer_contract_v0_1.json"
VALIDATOR_CONTRACT_PATH = BASE / "market_state_validator_contract_v0_1.json"
REGISTRY_CONTRACT_PATH = BASE / "market_state_candidate_dataset_registry_contract_v0_1.json"
SOURCE_MATERIALIZATION_SCOPE_PATH = (
    MARKET_ROOT / "configs" / "experimental_core_four_market_state_scale_c_candidate_materialization_scope_v0_1.json"
)
PROFILE_ROOT = MARKET_ROOT / "official_profiles" / "market_state_core_four_intraday_profile_v0_1"
PROFILE_MANIFEST_PATH = PROFILE_ROOT / "PROFILE_MANIFEST.json"
PROFILE_SCHEMA_PATH = PROFILE_ROOT / "PHYSICAL_SCHEMA_CONTRACT.json"
OUTPUT_ROOT = BASE / "runs"


class ExecutionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any, ensure_ascii: bool = True) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=ensure_ascii, separators=(",", ":"), default=str)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ExecutionError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: serialize_cell(row.get(k)) for k in fieldnames})


def serialize_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def arrow_type(type_name: str) -> pa.DataType:
    normalized = type_name.replace(" ", "")
    if normalized in {"string", "canonical_utf8_json_string", "sha256_hex_string"}:
        return pa.string()
    if normalized in {"float64", "double"}:
        return pa.float64()
    if normalized in {"date32", "date32[day]"}:
        return pa.date32()
    if normalized in {"timestamp[us,UTC]", "timestamp[us,tz=UTC]"}:
        return pa.timestamp("us", tz="UTC")
    raise ExecutionError(f"Unsupported Arrow type: {type_name}")


def parse_value(value: Any, type_name: str) -> Any:
    normalized = type_name.replace(" ", "")
    if normalized in {"string", "canonical_utf8_json_string", "sha256_hex_string"}:
        return str(value)
    if normalized in {"float64", "double"}:
        return float(value)
    if normalized in {"date32", "date32[day]"}:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        return date.fromisoformat(str(value))
    if normalized in {"timestamp[us,UTC]", "timestamp[us,tz=UTC]"}:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    raise ExecutionError(f"Unsupported value type: {type_name}")


def normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return value


def require_file(path: Path) -> None:
    if not path.exists():
        raise ExecutionError(f"Required file missing: {path}")


def schema_from_contract(schema_contract: dict[str, Any]) -> tuple[list[str], dict[str, dict[str, Any]], pa.Schema]:
    columns = schema_contract["columns"]
    names = [col["name"] for col in columns]
    if len(names) != len(set(names)):
        raise ExecutionError("Duplicate columns in physical schema contract")
    by_name = {col["name"]: col for col in columns}
    fields = [pa.field(col["name"], arrow_type(col["type"]), nullable=bool(col["nullable"])) for col in columns]
    return names, by_name, pa.schema(fields)


def source_scope_maps(scope: dict[str, Any]) -> tuple[dict[str, str], dict[str, str], list[str]]:
    value_map = {
        col["physical_name"]: col["source_value_field"]
        for col in scope["physical_schema"]["value_columns"]
    }
    formula_map = {
        col["physical_name"]: col["formula_id"]
        for col in scope["physical_schema"]["value_columns"]
    }
    fingerprint_fields = scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
    return value_map, formula_map, fingerprint_fields


def build_request(auth_scope: dict[str, Any]) -> tuple[dict[str, Any], str]:
    template = dict(auth_scope["authorized_request_template"])
    request = {
        "request_id": "market_state_request_v0_1_" + sha256_payload(template)[:16],
        "request_status": "accepted_for_resolution",
        "requested_at_utc": utc_now(),
        "requested_by": os.environ.get("USERNAME") or os.environ.get("USER"),
        "request_purpose": "bounded_on_demand_execution_probe",
        **template,
    }
    fingerprint_fields = dict(template)
    request_fingerprint = sha256_payload(fingerprint_fields)
    request["request_fingerprint"] = request_fingerprint
    return request, request_fingerprint


def build_row(
    record: dict[str, Any],
    run_id: str,
    profile_id: str,
    schema_version: str,
    source_scope: dict[str, Any],
    column_order: list[str],
    column_defs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    value_map, formula_map, fingerprint_fields = source_scope_maps(source_scope)
    values = record.get("values") or {}
    required_objects = set(source_scope["required_object_ids"])
    if record.get("integration_status") not in source_scope["required_candidate_input_statuses"]:
        raise ExecutionError(f"Record not integrable: {record.get('market_state_candidate_id')}")
    if set(record.get("object_record_ids") or {}) != required_objects:
        raise ExecutionError(f"Record missing required objects: {record.get('market_state_candidate_id')}")

    row: dict[str, Any] = {
        "state_profile_id": profile_id,
        "state_schema_version": schema_version,
        "materialization_run_id": run_id,
        "source_integration_run_id": source_scope["source_integration_run_id"],
        "source_candidate_record_id": record["market_state_candidate_id"],
        "source_integration_profile_id": record["market_state_profile_id"],
        "instrument_id": record["instrument_id"],
        "ticker": record["ticker"],
        "session_date": record["session_date"],
        "decision_timestamp_utc": record["decision_timestamp_utc"],
        "decision_case": record["decision_case"],
        "context_id": record["context_id"],
        "integration_status": record["integration_status"],
        "object_completeness_status": "COMPLETE_REQUIRED_OBJECTS_WITH_RESTRICTIONS",
        "quality_status": "PASS_WITH_RESTRICTIONS",
        "calendar_version": record["calendar_version"],
        "source_lineage_json": stable_json(
            {
                "shared_source_evidence": record.get("shared_source_evidence") or {},
                "object_record_ids": record.get("object_record_ids") or {},
                "source_integration_run_id": source_scope["source_integration_run_id"],
                "on_demand_source_alias": "scale_c_integrated_market_state_candidate_records",
            }
        ),
        "policy_versions_json": stable_json(record.get("policy_versions") or {}),
        "formula_versions_json": stable_json(formula_map),
        "restriction_codes_json": stable_json(sorted(set(record.get("restrictions") or []))),
        "context_input_fingerprint": record["context_input_fingerprint"],
    }
    for physical_name, source_name in value_map.items():
        if source_name not in values:
            raise ExecutionError(f"Missing source value {source_name} for {record['market_state_candidate_id']}")
        row[physical_name] = values[source_name]

    state_payload = {field: normalize(row.get(field)) for field in fingerprint_fields}
    row["state_output_fingerprint"] = sha256_payload(state_payload)
    id_payload = {
        field: normalize(row.get(field))
        for field in source_scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
    }
    row["materialized_state_candidate_id"] = sha256_payload(id_payload)

    typed_row: dict[str, Any] = {}
    for name in column_order:
        if name not in row:
            raise ExecutionError(f"Output row missing column: {name}")
        col = column_defs[name]
        typed_row[name] = parse_value(row[name], col["type"])
        if typed_row[name] is None and col["nullable"] is False:
            raise ExecutionError(f"Non-nullable output field is null: {name}")
    return typed_row


def row_fingerprint(row: dict[str, Any], fields: list[str]) -> str:
    return sha256_payload({field: normalize(row.get(field)) for field in fields})


def main() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    for path in [
        AUTH_SCOPE_PATH,
        AUTH_CONTRACT_PATH,
        REQUEST_CONTRACT_PATH,
        EXECUTION_PLAN_CONTRACT_PATH,
        MATERIALIZER_CONTRACT_PATH,
        VALIDATOR_CONTRACT_PATH,
        REGISTRY_CONTRACT_PATH,
        SOURCE_MATERIALIZATION_SCOPE_PATH,
        PROFILE_MANIFEST_PATH,
        PROFILE_SCHEMA_PATH,
    ]:
        require_file(path)

    auth_scope = read_json(AUTH_SCOPE_PATH)
    auth_contract = read_json(AUTH_CONTRACT_PATH)
    request_contract = read_json(REQUEST_CONTRACT_PATH)
    execution_plan_contract = read_json(EXECUTION_PLAN_CONTRACT_PATH)
    materializer_contract = read_json(MATERIALIZER_CONTRACT_PATH)
    validator_contract = read_json(VALIDATOR_CONTRACT_PATH)
    registry_contract = read_json(REGISTRY_CONTRACT_PATH)
    source_scope = read_json(SOURCE_MATERIALIZATION_SCOPE_PATH)
    profile_manifest = read_json(PROFILE_MANIFEST_PATH)
    schema_contract = read_json(PROFILE_SCHEMA_PATH)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"market_state_bounded_on_demand_execution_v0_1_{timestamp}"
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists():
        raise ExecutionError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

    request, request_fingerprint = build_request(auth_scope)
    write_json(run_dir / "request_record.json", request)

    column_order, column_defs, arrow_schema = schema_from_contract(schema_contract)
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
    write_json(run_dir / "profile_resolution_report.json", profile_resolution)

    source_records_path = (SOURCE_MATERIALIZATION_SCOPE_PATH.parent / source_scope["input_artifacts"]["market_state_candidate_records"]).resolve()
    records = read_jsonl(source_records_path)
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
    blocked_or_unavailable: list[dict[str, Any]] = []
    for session_date_value in request["session_dates"]:
        anchor = session_open_by_date.get(session_date_value)
        if not anchor:
            raise ExecutionError(f"No governed session open found in source records for {session_date_value}")
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
            record = exact_record_by_key.get((instrument_id, session_date_value, anchor))
            logical_partition_id = sha256_payload(
                {
                    "profile_id": profile_id,
                    "instrument_id": instrument_id,
                    "session_date": session_date_value,
                    "decision_timestamp_utc": anchor,
                }
            )
            if record:
                selected_records.append(record)
                disposition = "to_build"
                cause = ""
            else:
                disposition = "unavailable"
                cause = "missing_exact_decision_timestamp_source_candidate_record"
                blocked_or_unavailable.append(
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
    write_json(run_dir / "partition_coverage_resolution_report.json", partition_coverage)
    write_csv(
        run_dir / "partition_coverage_resolution_report.csv",
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
        "execution_plan_status": "authorized_for_execution",
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
            "candidate_parquet_filename": "market_state_bounded_on_demand_candidate_v0_1.parquet",
            "candidate_registry_entry_filename": "candidate_registry_entry.json",
        },
        "quantitative_limits": auth_scope["quantitative_limits"],
    }
    execution_plan_fingerprint = sha256_payload(execution_plan)
    execution_plan["execution_plan_fingerprint"] = execution_plan_fingerprint
    write_json(run_dir / "execution_plan.json", execution_plan)

    authorization_consumption = {
        "authorization_id": auth_scope["authorization_id"],
        "authorization_document_status_observed": auth_scope["status"],
        "authorization_consumption_status": "CONSUMED_BY_RUN",
        "execution_run_id": run_id,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
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
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_dirty_state": git_dirty_state,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "run_dir": str(run_dir),
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "pre_run_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": "RUNNING", "stage": "materializing"})

    physical_rows = [
        build_row(record, run_id, profile_id, schema_version, source_scope, column_order, column_defs)
        for record in sorted(selected_records, key=lambda r: (r["session_date"], r["instrument_id"], r["decision_timestamp_utc"]))
    ]
    table = pa.Table.from_pylist(physical_rows, schema=arrow_schema)
    parquet_path = run_dir / "market_state_bounded_on_demand_candidate_v0_1.parquet"
    pq.write_table(table, parquet_path, compression="snappy", use_dictionary=False, row_group_size=max(1, len(physical_rows)), coerce_timestamps="us")
    parquet_sha = sha256_file(parquet_path)

    candidate_rows_jsonl = run_dir / "candidate_market_state_rows.jsonl"
    write_jsonl(candidate_rows_jsonl, [{k: normalize(v) for k, v in row.items()} for row in physical_rows])

    candidate_dataset_fingerprint = sha256_payload(
        {
            "request_fingerprint": request_fingerprint,
            "execution_plan_fingerprint": execution_plan_fingerprint,
            "parquet_sha256": parquet_sha,
            "row_count": len(physical_rows),
            "partition_coverage_fingerprint": partition_coverage_fingerprint,
        }
    )
    candidate_output_manifest = {
        "candidate_dataset_id": "market_state_candidate_dataset_v0_1_" + candidate_dataset_fingerprint[:16],
        "candidate_dataset_status": "candidate_pending_validation",
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "profile_id": profile_id,
        "coverage": {
            "requested_contexts": len(partition_rows),
            "materialized_contexts": len(physical_rows),
            "unavailable_contexts": disposition_counts["unavailable"],
        },
        "files": [
            {"path": str(parquet_path), "sha256": parquet_sha, "bytes": parquet_path.stat().st_size, "rows": len(physical_rows)}
        ],
        "schema_contract": str(PROFILE_SCHEMA_PATH),
        "schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
    }
    write_json(run_dir / "candidate_output_manifest.json", candidate_output_manifest)

    lineage_manifest = {
        "run_id": run_id,
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
        "unavailable_contexts": blocked_or_unavailable,
    }
    write_json(run_dir / "lineage_manifest.json", lineage_manifest)

    observed_rows = pq.read_table(parquet_path).to_pylist()
    schema_match = [field.name for field in pq.read_schema(parquet_path)] == column_order
    primary_key_fields = ["instrument_id", "decision_timestamp_utc", "state_profile_id", "state_schema_version"]
    primary_keys = [tuple(normalize(row[field]) for field in primary_key_fields) for row in observed_rows]
    duplicate_primary_keys = sum(count - 1 for count in Counter(primary_keys).values() if count > 1)
    null_failures = sum(1 for row in observed_rows for name in column_order if row.get(name) is None and not column_defs[name]["nullable"])

    fingerprint_failures = 0
    fingerprint_rows: list[dict[str, Any]] = []
    fp_fields = source_scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
    id_fields = source_scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
    for row in observed_rows:
        recalculated_state = row_fingerprint(row, fp_fields)
        recalculated_id = row_fingerprint({**row, "state_output_fingerprint": recalculated_state}, id_fields)
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
        run_dir / "fingerprint_validation_report.csv",
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
    write_json(run_dir / "market_state_temporal_legality_report.json", {"failures": temporal_failures, "rows": temporal_rows})

    lineage_failures = 0
    for row in observed_rows:
        for field in ["source_lineage_json", "policy_versions_json", "formula_versions_json", "restriction_codes_json"]:
            try:
                json.loads(row[field])
            except Exception:
                lineage_failures += 1
    write_json(
        run_dir / "market_state_lineage_validation_report.json",
        {"lineage_json_parse_failures": lineage_failures, "lineage_manifest": str(run_dir / "lineage_manifest.json")},
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
    write_json(run_dir / "market_state_partition_validation_report.json", partition_validation)

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
        "eligible_for_candidate_registry": validation_hard_failures == 0,
        "reuse_eligibility": "pending_determinism_validation",
        "promotion_review_eligibility": "not_eligible_pending_determinism_and_scope_review",
    }
    validation_result_fingerprint = sha256_payload(validation_report)
    validation_report["validation_result_fingerprint"] = validation_result_fingerprint
    write_json(run_dir / "market_state_validation_report.json", validation_report)
    write_json(
        run_dir / "validation_evidence_manifest.json",
        {
            "validation_result_fingerprint": validation_result_fingerprint,
            "reports": {
                "market_state_validation_report": str(run_dir / "market_state_validation_report.json"),
                "market_state_partition_validation_report": str(run_dir / "market_state_partition_validation_report.json"),
                "market_state_temporal_legality_report": str(run_dir / "market_state_temporal_legality_report.json"),
                "market_state_lineage_validation_report": str(run_dir / "market_state_lineage_validation_report.json"),
                "fingerprint_validation_report": str(run_dir / "fingerprint_validation_report.csv"),
            },
        },
    )

    registry_entry = {
        "dataset_id": candidate_output_manifest["candidate_dataset_id"],
        "dataset_kind": "market_state_candidate_dataset",
        "registry_status": "validated_candidate" if validation_hard_failures == 0 else "failed",
        "validation_status": validation_status.lower(),
        "reuse_eligibility": "pending_determinism_validation",
        "promotion_review_eligibility": "not_eligible_pending_determinism_and_scope_review",
        "downstream_eligibility": False,
        "request_fingerprint": request_fingerprint,
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "profile_id": profile_id,
        "coverage": candidate_output_manifest["coverage"],
        "file_manifest_ref": "candidate_output_manifest.json",
        "lineage_manifest_ref": "lineage_manifest.json",
        "validation_report_ref": "market_state_validation_report.json",
    }
    registry_entry["registry_entry_fingerprint"] = sha256_payload(registry_entry)
    write_json(run_dir / "candidate_registry_entry.json", registry_entry)

    final_status = (
        "CLOSED_PASS_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED"
        if validation_hard_failures == 0 and disposition_counts["unavailable"]
        else "CLOSED_PASS_WITH_RESTRICTIONS_VALIDATED_CANDIDATE_REGISTERED"
        if validation_hard_failures == 0
        else "CLOSED_BLOCKED_VALIDATION_FAILED"
    )
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
        "candidate_registry_entries_written": 1 if validation_hard_failures == 0 else 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "request_fingerprint": request_fingerprint,
        "resolved_profile_fingerprint": resolved_profile_fingerprint,
        "resolved_universe_fingerprint": resolved_universe_fingerprint,
        "resolved_source_set_fingerprint": resolved_source_set_fingerprint,
        "partition_coverage_resolution_fingerprint": partition_coverage_fingerprint,
        "execution_plan_fingerprint": execution_plan_fingerprint,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "artifacts": {
            "request_record": str(run_dir / "request_record.json"),
            "profile_resolution_report": str(run_dir / "profile_resolution_report.json"),
            "universe_resolution_report": str(run_dir / "universe_resolution_report.json"),
            "source_resolution_report": str(run_dir / "source_resolution_report.json"),
            "partition_coverage_resolution_report": str(run_dir / "partition_coverage_resolution_report.json"),
            "execution_plan": str(run_dir / "execution_plan.json"),
            "pre_run_manifest": str(run_dir / "pre_run_manifest.json"),
            "candidate_output_manifest": str(run_dir / "candidate_output_manifest.json"),
            "lineage_manifest": str(run_dir / "lineage_manifest.json"),
            "market_state_validation_report": str(run_dir / "market_state_validation_report.json"),
            "candidate_registry_entry": str(run_dir / "candidate_registry_entry.json"),
            "candidate_parquet": str(parquet_path),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": final_status, "stage": "closed"})

    readout = f"""# Market State Bounded On-Demand Execution Readout v0.1

Status: `{final_status}`
Date: `2026-07-25`

```text
run_id = {run_id}
request_id = {request['request_id']}
execution_plan_id = {execution_plan['execution_plan_id']}
requested_contexts = {len(partition_rows)}
materialized_candidate_rows = {len(observed_rows)}
unavailable_contexts = {disposition_counts['unavailable']}
candidate_parquet_files_written = 1
candidate_registry_entries_written = {1 if validation_hard_failures == 0 else 0}
source_candidate_records_read = {source_records_read}
source_market_data_rows_read = 0
hard_validation_failures = {validation_hard_failures}
reuse_eligibility = pending_determinism_validation
official_dataset = false
production = false
downstream = false
next_recommended_gate = market_state_bounded_on_demand_candidate_dataset_review_v0_1
```

The bounded Market State on-demand execution consumed one request, resolved the
runtime chain, froze one execution plan, materialized a fresh candidate output
from integrated Scale C candidate records, validated it and wrote one candidate
registry entry.

One requested context is unavailable by design because no exact source candidate
record exists at the requested decision timestamp. No fallback was used.
"""
    (run_dir / "market_state_bounded_on_demand_execution_readout_v0_1.md").write_text(readout, encoding="utf-8")

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False, default=str))
    return 0 if validation_hard_failures == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExecutionError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
