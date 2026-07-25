from __future__ import annotations

import argparse
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


SCRIPT_VERSION = "experimental_core_four_market_state_materialization_execution_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_materialization_scope_v0_1.json"
)


class MaterializationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any, ensure_ascii: bool = True) -> str:
    return json.dumps(value, ensure_ascii=ensure_ascii, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload, ensure_ascii=True).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise MaterializationError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return records


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: serialize_cell(row.get(k)) for k in fieldnames})


def serialize_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return canonical_json(value, ensure_ascii=False)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def resolve_path(raw: str, base: Path) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def is_within_or_equal(candidate: Path, allowed: Path) -> bool:
    candidate = candidate.resolve()
    allowed = allowed.resolve()
    if candidate == allowed:
        return True
    try:
        candidate.relative_to(allowed)
        return True
    except ValueError:
        return False


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def arrow_type(type_name: str) -> pa.DataType:
    if type_name in {"string", "canonical_utf8_json_string", "sha256_hex_string"}:
        return pa.string()
    if type_name == "float64":
        return pa.float64()
    if type_name == "date32":
        return pa.date32()
    if type_name == "timestamp[us, UTC]":
        return pa.timestamp("us", tz="UTC")
    raise MaterializationError(f"Unsupported physical type: {type_name}")


def parse_physical_value(value: Any, type_name: str) -> Any:
    if value is None:
        return None
    if type_name in {"string", "canonical_utf8_json_string", "sha256_hex_string"}:
        return str(value)
    if type_name == "float64":
        return float(value)
    if type_name == "date32":
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        return date.fromisoformat(str(value))
    if type_name == "timestamp[us, UTC]":
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    raise MaterializationError(f"Unsupported physical type: {type_name}")


def normalize_for_compare(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
    if isinstance(value, date):
        return value.isoformat()
    return value


def row_hash(row: dict[str, Any], fields: list[str]) -> str:
    return sha256_payload({field: normalize_for_compare(row.get(field)) for field in fields})


def validate_authority(scope: dict[str, Any]) -> None:
    if scope.get("mode") != "experimental_core_four_market_state_materialization_execution":
        raise MaterializationError(f"Unsupported mode: {scope.get('mode')}")
    authority = scope.get("authority") or {}
    if authority.get("experimental_candidate_parquet_output_allowed") is not True:
        raise MaterializationError("Candidate parquet output must be explicitly allowed")
    must_be_false = [
        "source_market_data_reread_allowed",
        "filesystem_market_data_reads_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "official_market_state_allowed",
        "official_state_table_write_allowed",
    ]
    for key in must_be_false:
        if authority.get(key) is not False:
            raise MaterializationError(f"Authority violation: {key} must be false")
    output_policy = scope.get("output_policy") or {}
    if output_policy.get("official_dataset_root_allowed") is not False:
        raise MaterializationError("Official dataset root must remain closed")
    if output_policy.get("production_dataset_root_allowed") is not False:
        raise MaterializationError("Production dataset root must remain closed")


def validate_schema_scope(
    scope: dict[str, Any],
) -> tuple[list[str], dict[str, dict[str, Any]], pa.Schema]:
    physical = scope["physical_schema"]
    if physical.get("schema_inference_from_sample_allowed") is not False:
        raise MaterializationError("Schema inference from sample must be disabled")
    if physical.get("schema_first_records_second") is not True:
        raise MaterializationError("Scope must declare schema_first_records_second")
    column_order = list(physical["column_order"])
    column_defs = (
        list(physical["base_columns"])
        + list(physical["value_columns"])
        + list(physical["lineage_columns"])
    )
    by_name = {col["physical_name"]: col for col in column_defs}
    if len(by_name) != len(column_defs):
        raise MaterializationError("Duplicate physical column definitions in scope")
    if set(column_order) != set(by_name):
        missing = sorted(set(column_order) - set(by_name))
        extra = sorted(set(by_name) - set(column_order))
        raise MaterializationError(f"Column order/definition mismatch missing={missing} extra={extra}")
    fields = [
        pa.field(name, arrow_type(by_name[name]["type"]), nullable=bool(by_name[name]["nullable"]))
        for name in column_order
    ]
    return column_order, by_name, pa.schema(fields)


def validate_input_artifact_paths(paths: dict[str, Path], allowed_root: Path) -> dict[str, dict[str, Any]]:
    report: dict[str, dict[str, Any]] = {}
    for name, path in paths.items():
        if not is_within_or_equal(path, allowed_root):
            raise MaterializationError(f"Input artifact {name} resolves outside allowed run root: {path}")
        if not path.exists():
            raise MaterializationError(f"Input artifact {name} missing: {path}")
        if path.suffix.lower() == ".parquet":
            raise MaterializationError(f"Parquet input is not authorized: {path}")
        report[name] = {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
    return report


def compact_json_from_scope(scope: dict[str, Any], value: Any) -> str:
    js = scope["json_serialization"]
    if tuple(js.get("separators") or [",", ":"]) != (",", ":"):
        raise MaterializationError("Only compact canonical separators are supported")
    return json.dumps(
        value,
        ensure_ascii=bool(js.get("ensure_ascii")),
        sort_keys=bool(js.get("sort_keys")),
        separators=(",", ":"),
    )


def require_sha256(value: str, field: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise MaterializationError(f"{field} must be a 64-char sha256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise MaterializationError(f"{field} must be a sha256 hex string") from exc


def validate_candidate_input(
    records: list[dict[str, Any]],
    scope: dict[str, Any],
    integration_summary: dict[str, Any],
    rejected_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    limits = scope["limits"]
    expected_count = int(limits["maximum_input_candidate_records"])
    if len(records) != expected_count:
        raise MaterializationError(f"Expected {expected_count} candidate records, observed {len(records)}")
    if len(rejected_rows) != int(limits["maximum_input_rejected_context_records"]):
        raise MaterializationError("Rejected context report count does not match authorization")
    if integration_summary.get("run_id") != scope["source_integration_run_id"]:
        raise MaterializationError("Integration summary run_id does not match scope")
    if integration_summary.get("candidate_records_emitted") != expected_count:
        raise MaterializationError("Integration summary candidate count does not match scope")
    if integration_summary.get("source_market_data_rows_read") != 0:
        raise MaterializationError("Source market data rows were read upstream; boundary violation")

    required_objects = set(scope["required_object_ids"])
    allowed_statuses = set(scope["required_candidate_input_statuses"])
    value_sources = [col["source_value_field"] for col in scope["physical_schema"]["value_columns"]]
    expected_value_sources = set(value_sources)
    seen_candidate_ids: set[str] = set()
    seen_context_ids: set[str] = set()
    rejected_context_ids = {row.get("context_id") for row in rejected_rows}

    for record in records:
        source_candidate_id = record.get("market_state_candidate_id")
        context_id = record.get("context_id")
        if source_candidate_id in seen_candidate_ids:
            raise MaterializationError(f"Duplicate source_candidate_record_id: {source_candidate_id}")
        if context_id in seen_context_ids:
            raise MaterializationError(f"Duplicate context_id: {context_id}")
        if context_id in rejected_context_ids:
            raise MaterializationError(f"Rejected context appears in candidate records: {context_id}")
        seen_candidate_ids.add(str(source_candidate_id))
        seen_context_ids.add(str(context_id))
        require_sha256(str(source_candidate_id), "market_state_candidate_id")
        require_sha256(str(record.get("context_input_fingerprint")), "context_input_fingerprint")
        if record.get("integration_status") not in allowed_statuses:
            raise MaterializationError(f"Unexpected candidate status: {record.get('integration_status')}")
        if record.get("market_state_profile_id") != scope["source_integration_profile_id"]:
            raise MaterializationError("Unexpected source integration profile id")
        object_ids = set((record.get("object_record_ids") or {}).keys())
        if object_ids != required_objects:
            raise MaterializationError(f"Required object payload mismatch for {context_id}: {sorted(object_ids)}")
        object_statuses = set((record.get("object_statuses") or {}).keys())
        if object_statuses != required_objects:
            raise MaterializationError(f"Object status mismatch for {context_id}: {sorted(object_statuses)}")
        values = record.get("values") or {}
        value_keys = set(values.keys())
        missing = sorted(expected_value_sources - value_keys)
        extra = sorted(value_keys - expected_value_sources)
        if missing or extra:
            raise MaterializationError(f"Value field mismatch for {context_id}: missing={missing} extra={extra}")
        for key in value_sources:
            if values.get(key) is None:
                raise MaterializationError(f"Null required source value {key} for {context_id}")
    return sorted(
        records,
        key=lambda r: (
            str(r.get("instrument_id")),
            str(r.get("decision_timestamp_utc")),
            str(r.get("context_id")),
        ),
    )


def formula_versions(scope: dict[str, Any]) -> dict[str, str]:
    return {col["physical_name"]: col["formula_id"] for col in scope["physical_schema"]["value_columns"]}


def build_rows(records: list[dict[str, Any]], scope: dict[str, Any], run_id: str) -> list[dict[str, Any]]:
    column_order = scope["physical_schema"]["column_order"]
    by_name = {
        col["physical_name"]: col
        for col in scope["physical_schema"]["base_columns"]
        + scope["physical_schema"]["value_columns"]
        + scope["physical_schema"]["lineage_columns"]
    }
    rows: list[dict[str, Any]] = []
    formula_json = compact_json_from_scope(scope, formula_versions(scope))
    for record in records:
        row: dict[str, Any] = {}
        row["state_profile_id"] = scope["logical_profile_id"]
        row["state_schema_version"] = scope["physical_schema_id"]
        row["materialization_run_id"] = run_id
        row["source_integration_run_id"] = scope["source_integration_run_id"]
        row["source_candidate_record_id"] = record["market_state_candidate_id"]
        row["source_integration_profile_id"] = record["market_state_profile_id"]
        for field in [
            "instrument_id",
            "ticker",
            "session_date",
            "decision_timestamp_utc",
            "decision_case",
            "context_id",
            "integration_status",
        ]:
            row[field] = record[field]
        row["object_completeness_status"] = "COMPLETE_REQUIRED_OBJECTS_WITH_RESTRICTIONS"
        row["quality_status"] = "PASS_WITH_RESTRICTIONS"

        values = record["values"]
        for col in scope["physical_schema"]["value_columns"]:
            row[col["physical_name"]] = values[col["source_value_field"]]

        row["calendar_version"] = record.get("calendar_version") or "fixed_utc_probe_calendar_v0_1"
        row["source_lineage_json"] = compact_json_from_scope(
            scope,
            {
                "shared_source_evidence": record.get("shared_source_evidence") or {},
                "object_record_ids": record.get("object_record_ids") or {},
            },
        )
        row["policy_versions_json"] = compact_json_from_scope(scope, record.get("policy_versions") or {})
        row["formula_versions_json"] = formula_json
        row["restriction_codes_json"] = compact_json_from_scope(
            scope, sorted(set(record.get("restrictions") or []))
        )
        row["context_input_fingerprint"] = record["context_input_fingerprint"]

        payload_fields = scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
        excluded = set(scope["fingerprint_contract"]["state_output_fingerprint_excluded_fields"])
        if any(field in payload_fields for field in excluded):
            raise MaterializationError("Fingerprint payload includes an excluded field")
        fingerprint_payload = {field: normalize_for_compare(row[field]) for field in payload_fields}
        row["state_output_fingerprint"] = sha256_payload(fingerprint_payload)
        id_payload = {
            field: normalize_for_compare(row[field])
            for field in scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
        }
        row["materialized_state_candidate_id"] = sha256_payload(id_payload)

        missing = [name for name in column_order if name not in row]
        extra = sorted(set(row) - set(column_order))
        if missing or extra:
            raise MaterializationError(f"Physical row column mismatch missing={missing} extra={extra}")

        physical_row: dict[str, Any] = {}
        for name in column_order:
            col = by_name[name]
            value = parse_physical_value(row[name], col["type"])
            if value is None and col.get("nullable") is False:
                raise MaterializationError(f"Non-nullable physical field is null: {name}")
            physical_row[name] = value
        rows.append(physical_row)
    return rows


def validate_semantic_equalities(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = [
        ("price_movement__daily_prior_close", "price_location_structure__daily_prior_close"),
        ("price_movement__intraday_bar_close_price", "price_location_structure__intraday_bar_close_price"),
        (
            "price_movement__intraday_return_vs_prior_close_ratio",
            "price_location_structure__intraday_return_vs_prior_close_ratio_as_location",
        ),
        (
            "price_movement__intraday_return_vs_session_open_ratio",
            "price_location_structure__intraday_return_vs_session_open_ratio_as_location",
        ),
    ]
    findings: list[dict[str, Any]] = []
    for row in rows:
        for left, right in pairs:
            ok = abs(float(row[left]) - float(row[right])) <= 1e-12
            findings.append(
                {
                    "source_candidate_record_id": row["source_candidate_record_id"],
                    "left_field": left,
                    "right_field": right,
                    "left_value": row[left],
                    "right_value": row[right],
                    "semantic_equal": ok,
                }
            )
    return findings


def row_hash(row: dict[str, Any], fields: list[str]) -> str:
    return sha256_payload({field: normalize_for_compare(row.get(field)) for field in fields})


def read_parquet_rows(path: Path, pk_fields: list[str]) -> list[dict[str, Any]]:
    rows = pq.read_table(path).to_pylist()
    return sorted(rows, key=lambda r: tuple(str(normalize_for_compare(r.get(field))) for field in pk_fields))


def build_schema_report(expected_schema: pa.Schema, observed_schema: pa.Schema) -> dict[str, Any]:
    expected = [{"name": f.name, "type": str(f.type), "nullable": f.nullable} for f in expected_schema]
    observed = [{"name": f.name, "type": str(f.type), "nullable": f.nullable} for f in observed_schema]
    mismatches: list[dict[str, Any]] = []
    if len(expected) != len(observed):
        mismatches.append({"field": "column_count", "expected": len(expected), "observed": len(observed)})
    for idx, exp in enumerate(expected):
        obs = observed[idx] if idx < len(observed) else None
        if obs != exp:
            mismatches.append({"index": idx, "expected": exp, "observed": obs})
    return {
        "expected_column_count": len(expected),
        "observed_column_count": len(observed),
        "expected_schema": expected,
        "observed_schema": observed,
        "schema_mismatches": mismatches,
        "schema_match": not mismatches,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=str(DEFAULT_SCOPE))
    args = parser.parse_args(argv)

    scope_path = Path(args.scope).resolve()
    scope_dir = scope_path.parent
    integration_root = scope_dir.parent
    workspace_root = Path("C:/TSIS_Data").resolve()

    scope = read_json(scope_path)
    validate_authority(scope)
    column_order, _by_name, arrow_schema = validate_schema_scope(scope)

    run_root = resolve_path(scope["output_policy"]["output_root"], scope_dir)
    if not is_within_or_equal(run_root, integration_root):
        raise MaterializationError(f"Output root must stay inside integration root: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{scope['output_policy']['run_id_prefix']}_{timestamp}"
    run_dir = run_root / run_id
    if run_dir.exists():
        raise MaterializationError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    if not is_within_or_equal(run_dir, workspace_root):
        raise MaterializationError(f"Refusing to write outside workspace: {run_dir}")

    command_line = " ".join([str(Path(__file__).resolve()), "--scope", str(scope_path)])
    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))
    expected_candidate_records = int(scope["limits"]["maximum_input_candidate_records"])

    pre_manifest = {
        "run_id": run_id,
        "status": "starting",
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "command_line": command_line,
        "cwd": str(Path.cwd()),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getppid(),
        "pid": os.getpid(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_dirty_state": git_dirty_state,
        "mode": scope["mode"],
        "execution_class": "experimental_candidate_physical_materialization",
        "input_scope_path": str(scope_path),
        "output_root": str(run_root),
        "run_dir": str(run_dir),
        "expected_scope": f"materialize exactly {expected_candidate_records} accepted core-four candidate records; no source market data reads",
        "overwrite_policy": "refuse_existing_run_dir",
        "success_criteria": f"{expected_candidate_records} rows, 1 candidate parquet, no schema/grain/lineage/restriction/fingerprint/roundtrip/rebuild failures",
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "validate_inputs",
            "pid": os.getpid(),
            "run_dir": str(run_dir),
        },
    )

    input_paths = {key: resolve_path(raw, scope_dir) for key, raw in scope.get("input_artifacts", {}).items()}
    candidate_input_root = input_paths["market_state_candidate_records"].parent
    artifact_report = validate_input_artifact_paths(input_paths, candidate_input_root)
    integration_summary = read_json(input_paths["integration_summary"])
    integration_final_manifest = read_json(input_paths["integration_final_manifest"])
    if integration_final_manifest.get("run_id") != scope["source_integration_run_id"]:
        raise MaterializationError("Integration final manifest run_id does not match scope")

    candidate_records = read_jsonl(input_paths["market_state_candidate_records"])
    rejected_context_rows = read_csv_rows(input_paths["rejected_context_report"])
    value_manifest_rows = read_csv_rows(input_paths["integration_value_manifest"])
    sorted_records = validate_candidate_input(candidate_records, scope, integration_summary, rejected_context_rows)

    expected_value_sources = {col["source_value_field"] for col in scope["physical_schema"]["value_columns"]}
    manifest_values = {
        row.get("value_field")
        for row in value_manifest_rows
        if str(row.get("value_admitted")).lower() == "true"
    }
    if manifest_values != expected_value_sources:
        raise MaterializationError(
            "Integration value manifest does not match closed value source fields: "
            f"missing={sorted(expected_value_sources - manifest_values)} "
            f"extra={sorted(manifest_values - expected_value_sources)}"
        )

    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "build_physical_rows",
            "pid": os.getpid(),
            "input_candidate_records": len(sorted_records),
        },
    )
    physical_rows = build_rows(sorted_records, scope, run_id)
    if len(physical_rows) != int(scope["limits"]["maximum_output_candidate_rows"]):
        raise MaterializationError("Output row count does not match authorization")

    pk_fields = scope["physical_schema"]["primary_key"]
    primary_keys = [tuple(normalize_for_compare(row[field]) for field in pk_fields) for row in physical_rows]
    duplicate_primary_keys = sum(count - 1 for count in Counter(primary_keys).values() if count > 1)
    source_id_duplicates = sum(
        count - 1 for count in Counter(row["source_candidate_record_id"] for row in physical_rows).values() if count > 1
    )
    materialized_id_duplicates = sum(
        count - 1
        for count in Counter(row["materialized_state_candidate_id"] for row in physical_rows).values()
        if count > 1
    )
    semantic_equality_rows = validate_semantic_equalities(physical_rows)
    semantic_equality_failures = sum(1 for row in semantic_equality_rows if not row["semantic_equal"])
    if duplicate_primary_keys or source_id_duplicates or materialized_id_duplicates or semantic_equality_failures:
        raise MaterializationError("Grain or semantic equality validation failed before parquet write")

    table = pa.Table.from_pylist(physical_rows, schema=arrow_schema)
    parquet_path = run_dir / scope["authority"]["candidate_parquet_filename"]
    writer_settings = {
        "pyarrow_version": pa.__version__,
        "compression": "snappy",
        "use_dictionary": False,
        "timestamp_unit": "us",
        "timezone": "UTC",
        "row_group_size": len(physical_rows),
        "schema_arrow": str(arrow_schema),
    }
    pq.write_table(
        table,
        parquet_path,
        compression=writer_settings["compression"],
        use_dictionary=writer_settings["use_dictionary"],
        row_group_size=writer_settings["row_group_size"],
        coerce_timestamps="us",
        allow_truncated_timestamps=False,
    )
    parquet_size = parquet_path.stat().st_size
    if parquet_size > int(scope["limits"]["maximum_output_bytes"]):
        raise MaterializationError("Parquet output byte limit exceeded")
    parquet_files = list(run_dir.glob("*.parquet"))
    if len(parquet_files) != int(scope["limits"]["maximum_candidate_parquet_files"]):
        raise MaterializationError("Unexpected parquet file count")

    observed_table = pq.read_table(parquet_path)
    schema_report = build_schema_report(arrow_schema, observed_table.schema)
    observed_rows = read_parquet_rows(parquet_path, pk_fields)
    pre_rows_sorted = sorted(
        physical_rows,
        key=lambda r: tuple(str(normalize_for_compare(r.get(field))) for field in pk_fields),
    )

    roundtrip_rows: list[dict[str, Any]] = []
    roundtrip_failures = 0
    for idx, (pre, post) in enumerate(zip(pre_rows_sorted, observed_rows)):
        pre_hash = row_hash(pre, column_order)
        post_hash = row_hash(post, column_order)
        matches = pre_hash == post_hash
        if not matches:
            roundtrip_failures += 1
        roundtrip_rows.append(
            {
                "row_index": idx,
                "source_candidate_record_id": pre["source_candidate_record_id"],
                "pre_write_row_hash": pre_hash,
                "post_read_row_hash": post_hash,
                "roundtrip_match": matches,
            }
        )
    if len(pre_rows_sorted) != len(observed_rows):
        roundtrip_failures += abs(len(pre_rows_sorted) - len(observed_rows))

    rebuild_rows = build_rows(sorted_records, scope, run_id + "_rebuild_check")
    semantic_fields = scope["determinism_contract"]["semantic_rebuild_compare_fields"]
    semantic_differences: list[dict[str, Any]] = []
    rebuild_sorted = sorted(
        rebuild_rows,
        key=lambda r: tuple(str(normalize_for_compare(r.get(field))) for field in pk_fields),
    )
    for left, right in zip(pre_rows_sorted, rebuild_sorted):
        for field in semantic_fields:
            if normalize_for_compare(left.get(field)) != normalize_for_compare(right.get(field)):
                semantic_differences.append(
                    {
                        "source_candidate_record_id": left.get("source_candidate_record_id"),
                        "field": field,
                        "left": normalize_for_compare(left.get(field)),
                        "right": normalize_for_compare(right.get(field)),
                    }
                )

    recalculated_fingerprint_failures = 0
    fingerprint_rows: list[dict[str, Any]] = []
    for row in physical_rows:
        payload = {
            field: normalize_for_compare(row[field])
            for field in scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
        }
        recalculated_state = sha256_payload(payload)
        id_payload = {
            field: normalize_for_compare(row[field])
            for field in scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
        }
        recalculated_id = sha256_payload(id_payload)
        state_match = recalculated_state == row["state_output_fingerprint"]
        id_match = recalculated_id == row["materialized_state_candidate_id"]
        if not state_match or not id_match:
            recalculated_fingerprint_failures += 1
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

    lineage_rows = [
        {
            "source_candidate_record_id": row["source_candidate_record_id"],
            "context_id": row["context_id"],
            "source_lineage_json_present": bool(row["source_lineage_json"]),
            "policy_versions_json_present": bool(row["policy_versions_json"]),
            "formula_versions_json_present": bool(row["formula_versions_json"]),
            "context_input_fingerprint": row["context_input_fingerprint"],
        }
        for row in physical_rows
    ]
    lineage_losses = sum(
        1
        for row in lineage_rows
        if not all(
            [
                row["source_lineage_json_present"],
                row["policy_versions_json_present"],
                row["formula_versions_json_present"],
                row["context_input_fingerprint"],
            ]
        )
    )
    restriction_rows: list[dict[str, Any]] = []
    restriction_losses = 0
    for record, row in zip(sorted_records, physical_rows):
        input_restrictions = sorted(set(record.get("restrictions") or []))
        output_restrictions = json.loads(row["restriction_codes_json"])
        preserved = input_restrictions == output_restrictions
        if not preserved:
            restriction_losses += 1
        restriction_rows.append(
            {
                "source_candidate_record_id": row["source_candidate_record_id"],
                "input_restriction_count": len(input_restrictions),
                "output_restriction_count": len(output_restrictions),
                "restrictions_preserved": preserved,
                "restriction_codes_json": row["restriction_codes_json"],
            }
        )

    missing_required_columns = 0 if set(column_order) == set(observed_table.schema.names) else len(set(column_order) - set(observed_table.schema.names))
    extra_columns = len(set(observed_table.schema.names) - set(column_order))
    hard_failures = sum(
        [
            duplicate_primary_keys,
            source_id_duplicates,
            materialized_id_duplicates,
            semantic_equality_failures,
            missing_required_columns,
            extra_columns,
            lineage_losses,
            restriction_losses,
            recalculated_fingerprint_failures,
            roundtrip_failures,
            len(semantic_differences),
            0 if schema_report["schema_match"] else 1,
        ]
    )
    gate_status = "PASS_WITH_RESTRICTIONS" if hard_failures == 0 else "FAILED"
    overall_status = (
        "passed_core_four_market_state_materialization_with_restrictions"
        if hard_failures == 0
        else "failed_core_four_market_state_materialization"
    )

    grain_rows = [
        {
            "source_candidate_record_id": row["source_candidate_record_id"],
            "materialized_state_candidate_id": row["materialized_state_candidate_id"],
            "primary_key": canonical_json([normalize_for_compare(v) for v in pk], ensure_ascii=False),
            "primary_key_duplicate": primary_keys.count(pk) > 1,
        }
        for row, pk in zip(physical_rows, primary_keys)
    ]
    reconciliation_rows = [
        {
            "source_candidate_record_id": row["source_candidate_record_id"],
            "context_id": row["context_id"],
            "source_value_fields": len(record.get("values") or {}),
            "physical_value_columns": len(scope["physical_schema"]["value_columns"]),
            "source_to_physical_reconciled": True,
        }
        for record, row in zip(sorted_records, physical_rows)
    ]

    write_json(run_dir / "schema_report.json", schema_report)
    write_csv_rows(
        run_dir / "grain_report.csv",
        ["source_candidate_record_id", "materialized_state_candidate_id", "primary_key", "primary_key_duplicate"],
        grain_rows,
    )
    write_json(run_dir / "lineage_report.json", {"lineage_losses": lineage_losses, "rows": lineage_rows})
    write_csv_rows(
        run_dir / "restriction_report.csv",
        [
            "source_candidate_record_id",
            "input_restriction_count",
            "output_restriction_count",
            "restrictions_preserved",
            "restriction_codes_json",
        ],
        restriction_rows,
    )
    write_csv_rows(
        run_dir / "fingerprint_report.csv",
        [
            "source_candidate_record_id",
            "state_output_fingerprint",
            "recalculated_state_output_fingerprint",
            "state_output_fingerprint_match",
            "materialized_state_candidate_id",
            "recalculated_materialized_state_candidate_id",
            "materialized_state_candidate_id_match",
        ],
        fingerprint_rows,
    )
    write_csv_rows(
        run_dir / "roundtrip_report.csv",
        ["row_index", "source_candidate_record_id", "pre_write_row_hash", "post_read_row_hash", "roundtrip_match"],
        roundtrip_rows,
    )
    write_csv_rows(
        run_dir / "reconciliation_report.csv",
        ["source_candidate_record_id", "context_id", "source_value_fields", "physical_value_columns", "source_to_physical_reconciled"],
        reconciliation_rows,
    )
    write_json(
        run_dir / "rebuild_determinism_report.json",
        {
            "semantic_rebuild_differences": len(semantic_differences),
            "semantic_rebuild_compare_field_count": len(semantic_fields),
            "semantic_rebuild_compare_fields": semantic_fields,
            "byte_identical_parquet_rebuild_required": False,
            "ignored_fields": scope["determinism_contract"]["semantic_rebuild_ignored_fields"],
            "differences": semantic_differences,
        },
    )

    materialization_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_id": scope["scope_id"],
        "input_candidate_records": len(sorted_records),
        "output_candidate_rows": len(physical_rows),
        "candidate_parquet_files_written": len(parquet_files),
        "source_market_data_rows_read": 0,
        "parquet_path": str(parquet_path),
        "parquet_sha256": sha256_file(parquet_path),
        "parquet_bytes": parquet_size,
        "writer_settings": writer_settings,
        "input_artifacts": artifact_report,
    }
    write_json(run_dir / "materialization_manifest.json", materialization_manifest)

    summary = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "mode": scope["mode"],
        "overall_status": overall_status,
        "experimental_core_four_market_state_materialization_execution": gate_status,
        "logical_profile_id": scope["logical_profile_id"],
        "physical_schema_id": scope["physical_schema_id"],
        "source_integration_run_id": scope["source_integration_run_id"],
        "input_candidate_records": len(sorted_records),
        "output_candidate_rows": len(physical_rows),
        "rejected_contexts_materialized_as_rows": 0,
        "source_market_data_rows_read": 0,
        "candidate_parquet_files_written": len(parquet_files),
        "candidate_parquet_bytes": parquet_size,
        "physical_column_count": len(column_order),
        "physical_value_column_count": len(scope["physical_schema"]["value_columns"]),
        "duplicate_primary_keys": duplicate_primary_keys,
        "duplicate_source_candidate_record_ids": source_id_duplicates,
        "duplicate_materialized_state_candidate_ids": materialized_id_duplicates,
        "missing_required_columns": missing_required_columns,
        "extra_columns": extra_columns,
        "namespace_collisions": 0,
        "non_nullable_nulls": 0,
        "type_coercion_failures": 0,
        "semantic_equality_failures": semantic_equality_failures,
        "lineage_losses": lineage_losses,
        "restriction_losses": restriction_losses,
        "fingerprint_mismatches": recalculated_fingerprint_failures,
        "roundtrip_failures": roundtrip_failures,
        "semantic_rebuild_differences": len(semantic_differences),
        "semantic_rebuild_compare_field_count": len(semantic_fields),
        "byte_identical_parquet_rebuild_required": False,
        "schema_match": schema_report["schema_match"],
        "hard_validation_failures": hard_failures,
        "experimental_candidate_parquet_output_allowed": True,
        "candidate_rows_are_canonical_market_state": False,
        "candidate_rows_are_downstream_consumable": False,
        "official_market_state_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
        "created_at_utc": pre_manifest["created_at_utc"],
        "completed_at_utc": utc_now(),
        "artifacts": {
            "pre_manifest": str(run_dir / "pre_manifest.json"),
            "heartbeat": str(run_dir / "heartbeat.json"),
            "candidate_parquet": str(parquet_path),
            "materialization_manifest": str(run_dir / "materialization_manifest.json"),
            "schema_report": str(run_dir / "schema_report.json"),
            "grain_report": str(run_dir / "grain_report.csv"),
            "lineage_report": str(run_dir / "lineage_report.json"),
            "restriction_report": str(run_dir / "restriction_report.csv"),
            "fingerprint_report": str(run_dir / "fingerprint_report.csv"),
            "roundtrip_report": str(run_dir / "roundtrip_report.csv"),
            "reconciliation_report": str(run_dir / "reconciliation_report.csv"),
            "rebuild_determinism_report": str(run_dir / "rebuild_determinism_report.json"),
            "final_manifest": str(run_dir / "final_manifest.json"),
        },
        "input_artifacts": artifact_report,
    }
    final_manifest = dict(pre_manifest)
    final_manifest.update(summary)
    final_manifest["status"] = "complete"
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "complete",
            "stage": "complete",
            "pid": os.getpid(),
            "overall_status": overall_status,
            "output_candidate_rows": len(physical_rows),
            "candidate_parquet_files_written": len(parquet_files),
        },
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if gate_status == "PASS_WITH_RESTRICTIONS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MaterializationError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
