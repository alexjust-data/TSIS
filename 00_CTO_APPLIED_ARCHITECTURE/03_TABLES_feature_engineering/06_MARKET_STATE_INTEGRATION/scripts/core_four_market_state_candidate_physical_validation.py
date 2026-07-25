from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


SCRIPT_VERSION = "core_four_market_state_candidate_physical_validation_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_materialization_scope_v0_1.json"
)
DEFAULT_MATERIALIZATION_RUN_ID = "experimental_core_four_market_state_materialization_v0_1_20260722T081155Z"
RUN_ID_PREFIX = "core_four_market_state_candidate_physical_validation_v0_1"


class ValidationError(RuntimeError):
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
                raise ValidationError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return records


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: serialize_cell(row.get(k)) for k in fieldnames})


def resolve_path(raw: str, base: Path) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def arrow_type(type_name: str) -> pa.DataType:
    if type_name in {"string", "canonical_utf8_json_string", "sha256_hex_string"}:
        return pa.string()
    if type_name == "float64":
        return pa.float64()
    if type_name == "date32":
        return pa.date32()
    if type_name == "timestamp[us, UTC]":
        return pa.timestamp("us", tz="UTC")
    raise ValidationError(f"Unsupported physical type: {type_name}")


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
        if isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    raise ValidationError(f"Unsupported physical type: {type_name}")


def normalize_for_compare(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
    if isinstance(value, date):
        return value.isoformat()
    return value


def values_equal(left: Any, right: Any, type_name: str | None = None) -> bool:
    if left is None or right is None:
        return left is right
    if type_name == "float64" or isinstance(left, float) or isinstance(right, float):
        try:
            return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)
        except (TypeError, ValueError):
            return False
    return normalize_for_compare(left) == normalize_for_compare(right)


def all_physical_columns(scope: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        col["physical_name"]: col
        for col in scope["physical_schema"]["base_columns"]
        + scope["physical_schema"]["value_columns"]
        + scope["physical_schema"]["lineage_columns"]
    }


def expected_arrow_schema(scope: dict[str, Any]) -> pa.Schema:
    by_name = all_physical_columns(scope)
    fields = []
    for name in scope["physical_schema"]["column_order"]:
        col = by_name[name]
        fields.append(pa.field(name, arrow_type(col["type"]), nullable=bool(col.get("nullable", True))))
    return pa.schema(fields)


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda r: (
            str(r.get("instrument_id")),
            str(r.get("decision_timestamp_utc")),
            str(r.get("context_id")),
        ),
    )


def sort_rows(rows: list[dict[str, Any]], pk_fields: list[str]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: tuple(str(normalize_for_compare(r.get(f))) for f in pk_fields))


def formula_versions(scope: dict[str, Any]) -> dict[str, str]:
    return {col["physical_name"]: col["formula_id"] for col in scope["physical_schema"]["value_columns"]}


def build_expected_rows(records: list[dict[str, Any]], scope: dict[str, Any], run_id: str) -> list[dict[str, Any]]:
    column_order = scope["physical_schema"]["column_order"]
    by_name = all_physical_columns(scope)
    formula_json = canonical_json(formula_versions(scope), ensure_ascii=True)
    rows: list[dict[str, Any]] = []
    for record in records:
        row: dict[str, Any] = {
            "state_profile_id": scope["logical_profile_id"],
            "state_schema_version": scope["physical_schema_id"],
            "materialization_run_id": run_id,
            "source_integration_run_id": scope["source_integration_run_id"],
            "source_candidate_record_id": record["market_state_candidate_id"],
            "source_integration_profile_id": record["market_state_profile_id"],
            "object_completeness_status": "COMPLETE_REQUIRED_OBJECTS_WITH_RESTRICTIONS",
            "quality_status": "PASS_WITH_RESTRICTIONS",
            "calendar_version": record.get("calendar_version") or "fixed_utc_probe_calendar_v0_1",
        }
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

        values = record.get("values") or {}
        for col in scope["physical_schema"]["value_columns"]:
            row[col["physical_name"]] = values[col["source_value_field"]]

        row["source_lineage_json"] = canonical_json(
            {
                "shared_source_evidence": record.get("shared_source_evidence") or {},
                "object_record_ids": record.get("object_record_ids") or {},
            },
            ensure_ascii=True,
        )
        row["policy_versions_json"] = canonical_json(record.get("policy_versions") or {}, ensure_ascii=True)
        row["formula_versions_json"] = formula_json
        row["restriction_codes_json"] = canonical_json(
            sorted(set(record.get("restrictions") or [])), ensure_ascii=True
        )
        row["context_input_fingerprint"] = record["context_input_fingerprint"]

        payload = {
            field: normalize_for_compare(row[field])
            for field in scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
        }
        row["state_output_fingerprint"] = sha256_payload(payload)
        id_payload = {
            field: normalize_for_compare(row[field])
            for field in scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
        }
        row["materialized_state_candidate_id"] = sha256_payload(id_payload)

        missing = [name for name in column_order if name not in row]
        extra = sorted(set(row) - set(column_order))
        if missing or extra:
            raise ValidationError(f"Expected row column mismatch missing={missing} extra={extra}")

        physical_row: dict[str, Any] = {}
        for name in column_order:
            col = by_name[name]
            physical_row[name] = parse_physical_value(row[name], col["type"])
        rows.append(physical_row)
    return rows


def schema_report(scope: dict[str, Any], table: pa.Table) -> dict[str, Any]:
    expected = expected_arrow_schema(scope)
    observed = table.schema
    expected_columns = scope["physical_schema"]["column_order"]
    observed_columns = observed.names
    field_rows = []
    by_name = all_physical_columns(scope)
    for name in expected_columns:
        expected_field = expected.field(name)
        observed_field = observed.field(name) if name in observed.names else None
        field_rows.append(
            {
                "column": name,
                "expected_type": str(expected_field.type),
                "observed_type": str(observed_field.type) if observed_field else None,
                "expected_nullable": expected_field.nullable,
                "observed_nullable": observed_field.nullable if observed_field else None,
                "type_match": bool(observed_field and observed_field.type.equals(expected_field.type)),
                "nullable_match": bool(observed_field and observed_field.nullable == expected_field.nullable),
                "declared_scope_type": by_name[name]["type"],
            }
        )
    missing = [c for c in expected_columns if c not in observed_columns]
    extra = [c for c in observed_columns if c not in expected_columns]
    type_mismatches = [r for r in field_rows if not r["type_match"]]
    nullable_mismatches = [r for r in field_rows if not r["nullable_match"]]
    return {
        "expected_column_count": len(expected_columns),
        "observed_column_count": len(observed_columns),
        "column_order_exact": expected_columns == observed_columns,
        "missing_columns": missing,
        "extra_columns": extra,
        "arrow_schema_exact_ignoring_metadata": observed.equals(expected, check_metadata=False),
        "type_mismatch_count": len(type_mismatches),
        "nullable_mismatch_count": len(nullable_mismatches),
        "timestamp_timezone_utc": str(observed.field("decision_timestamp_utc").type) == "timestamp[us, tz=UTC]"
        if "decision_timestamp_utc" in observed.names
        else False,
        "fields": field_rows,
    }


def counter_duplicate_count(values: list[Any]) -> int:
    return sum(count - 1 for count in Counter(values).values() if count > 1)


def row_key(row: dict[str, Any], fields: list[str]) -> tuple[Any, ...]:
    return tuple(normalize_for_compare(row.get(field)) for field in fields)


def validate_values(
    records_by_id: dict[str, dict[str, Any]],
    rows_by_source_id: dict[str, dict[str, Any]],
    scope: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    report_rows: list[dict[str, Any]] = []
    expected_source_fields = {col["source_value_field"] for col in scope["physical_schema"]["value_columns"]}
    rvol_source = "trading_activity__daily_rvol_20d"
    rvol_target = "trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean"
    missing_source_fields = 0
    extra_source_fields = 0
    mismatches = 0
    rvol_checks = 0
    rvol_mismatches = 0
    for source_id, record in sorted(records_by_id.items()):
        row = rows_by_source_id.get(source_id)
        values = record.get("values") or {}
        missing_source_fields += len(expected_source_fields - set(values))
        extra_source_fields += len(set(values) - expected_source_fields)
        if row is None:
            mismatches += len(scope["physical_schema"]["value_columns"])
            continue
        for col in scope["physical_schema"]["value_columns"]:
            source_field = col["source_value_field"]
            physical_field = col["physical_name"]
            type_name = col["type"]
            source_raw = values.get(source_field)
            source_value = parse_physical_value(source_raw, type_name) if source_field in values else None
            physical_value = row.get(physical_field)
            match = values_equal(source_value, physical_value, type_name)
            if not match:
                mismatches += 1
            if source_field == rvol_source and physical_field == rvol_target:
                rvol_checks += 1
                if not match:
                    rvol_mismatches += 1
            report_rows.append(
                {
                    "source_candidate_record_id": source_id,
                    "context_id": record.get("context_id"),
                    "source_value_field": source_field,
                    "physical_field": physical_field,
                    "source_value": normalize_for_compare(source_value),
                    "physical_value": normalize_for_compare(physical_value),
                    "type": type_name,
                    "match": match,
                }
            )
    summary = {
        "value_mappings_checked": len(report_rows),
        "expected_value_mappings": len(records_by_id) * len(scope["physical_schema"]["value_columns"]),
        "source_to_physical_value_mismatches": mismatches,
        "missing_source_value_fields": missing_source_fields,
        "extra_source_value_fields": extra_source_fields,
        "rvol_rename_checks": rvol_checks,
        "rvol_rename_mismatches": rvol_mismatches,
        "rvol_rename_passed": rvol_checks == len(records_by_id) and rvol_mismatches == 0,
    }
    return report_rows, summary


def validate_lineage(
    records_by_id: dict[str, dict[str, Any]],
    rows_by_source_id: dict[str, dict[str, Any]],
    scope: dict[str, Any],
) -> dict[str, Any]:
    formula_json = canonical_json(formula_versions(scope), ensure_ascii=True)
    row_reports = []
    counts = Counter()
    for source_id, record in sorted(records_by_id.items()):
        row = rows_by_source_id.get(source_id)
        if row is None:
            counts["missing_physical_row"] += 1
            continue
        expected_source_lineage = canonical_json(
            {
                "shared_source_evidence": record.get("shared_source_evidence") or {},
                "object_record_ids": record.get("object_record_ids") or {},
            },
            ensure_ascii=True,
        )
        expected_policy = canonical_json(record.get("policy_versions") or {}, ensure_ascii=True)
        expected_restrictions = canonical_json(sorted(set(record.get("restrictions") or [])), ensure_ascii=True)
        checks = {
            "source_lineage_json_match": row.get("source_lineage_json") == expected_source_lineage,
            "policy_versions_json_match": row.get("policy_versions_json") == expected_policy,
            "formula_versions_json_match": row.get("formula_versions_json") == formula_json,
            "restriction_codes_json_match": row.get("restriction_codes_json") == expected_restrictions,
            "context_input_fingerprint_match": row.get("context_input_fingerprint")
            == record.get("context_input_fingerprint"),
        }
        for name, matched in checks.items():
            if not matched:
                counts[name.replace("_match", "_mismatch")] += 1
        row_reports.append({"source_candidate_record_id": source_id, "context_id": record.get("context_id"), **checks})
    return {
        "source_lineage_content_mismatches": counts["source_lineage_json_mismatch"],
        "policy_version_mismatches": counts["policy_versions_json_mismatch"],
        "formula_version_mismatches": counts["formula_versions_json_mismatch"],
        "restriction_mismatches": counts["restriction_codes_json_mismatch"],
        "context_fingerprint_mismatches": counts["context_input_fingerprint_mismatch"],
        "rows": row_reports,
    }


def validate_fingerprints(rows: list[dict[str, Any]], scope: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    report_rows = []
    state_matches = 0
    id_matches = 0
    for row in rows:
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
        state_match = recalculated_state == row.get("state_output_fingerprint")
        id_match = recalculated_id == row.get("materialized_state_candidate_id")
        state_matches += int(state_match)
        id_matches += int(id_match)
        report_rows.append(
            {
                "source_candidate_record_id": row.get("source_candidate_record_id"),
                "context_id": row.get("context_id"),
                "state_output_fingerprint": row.get("state_output_fingerprint"),
                "recalculated_state_output_fingerprint": recalculated_state,
                "state_output_fingerprint_match": state_match,
                "materialized_state_candidate_id": row.get("materialized_state_candidate_id"),
                "recalculated_materialized_state_candidate_id": recalculated_id,
                "materialized_state_candidate_id_match": id_match,
            }
        )
    return report_rows, {
        "state_output_fingerprint_matches": state_matches,
        "state_output_fingerprint_mismatches": len(rows) - state_matches,
        "materialized_state_candidate_id_matches": id_matches,
        "materialized_state_candidate_id_mismatches": len(rows) - id_matches,
    }


def validate_roundtrip(
    expected_rows: list[dict[str, Any]],
    observed_rows: list[dict[str, Any]],
    scope: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    column_order = scope["physical_schema"]["column_order"]
    by_name = all_physical_columns(scope)
    observed_by_source = {row["source_candidate_record_id"]: row for row in observed_rows}
    report_rows = []
    mismatch_rows = 0
    mismatch_fields = 0
    for expected in expected_rows:
        source_id = expected["source_candidate_record_id"]
        observed = observed_by_source.get(source_id)
        field_mismatches = []
        if observed is None:
            field_mismatches = column_order[:]
        else:
            for field in column_order:
                type_name = by_name[field]["type"]
                if not values_equal(expected.get(field), observed.get(field), type_name):
                    field_mismatches.append(field)
        mismatch_rows += int(bool(field_mismatches))
        mismatch_fields += len(field_mismatches)
        report_rows.append(
            {
                "source_candidate_record_id": source_id,
                "context_id": expected.get("context_id"),
                "fields_checked": len(column_order),
                "field_mismatch_count": len(field_mismatches),
                "roundtrip_match": len(field_mismatches) == 0,
                "mismatched_fields": field_mismatches,
            }
        )
    return report_rows, {
        "roundtrip_rows_checked": len(expected_rows),
        "roundtrip_row_mismatches": mismatch_rows,
        "roundtrip_field_mismatches": mismatch_fields,
    }


def validate_semantic_rebuild(
    expected_rows: list[dict[str, Any]],
    rebuild_rows: list[dict[str, Any]],
    scope: dict[str, Any],
) -> dict[str, Any]:
    fields = scope["determinism_contract"]["semantic_rebuild_compare_fields"]
    by_name = all_physical_columns(scope)
    rebuild_by_source = {row["source_candidate_record_id"]: row for row in rebuild_rows}
    differences = []
    for expected in expected_rows:
        source_id = expected["source_candidate_record_id"]
        rebuilt = rebuild_by_source.get(source_id)
        if rebuilt is None:
            differences.append({"source_candidate_record_id": source_id, "field": "__row__", "left": "present", "right": "missing"})
            continue
        for field in fields:
            type_name = by_name[field]["type"]
            if not values_equal(expected.get(field), rebuilt.get(field), type_name):
                differences.append(
                    {
                        "source_candidate_record_id": source_id,
                        "field": field,
                        "left": normalize_for_compare(expected.get(field)),
                        "right": normalize_for_compare(rebuilt.get(field)),
                    }
                )
    return {
        "semantic_rebuild_compare_field_count": len(fields),
        "semantic_rebuild_row_count": len(expected_rows),
        "semantic_rebuild_field_comparisons": len(fields) * len(expected_rows),
        "semantic_rebuild_differences": len(differences),
        "ignored_fields": scope["determinism_contract"].get("semantic_rebuild_ignored_fields", []),
        "byte_identical_parquet_rebuild_required": bool(
            scope["determinism_contract"].get("byte_identical_parquet_rebuild_required")
        ),
        "differences": differences,
    }


def validate_authority(scope: dict[str, Any], records: list[dict[str, Any]], final_manifest: dict[str, Any]) -> dict[str, Any]:
    failures = []
    scope_authority = scope.get("authority") or {}
    manifest_false_flags = [
        "candidate_rows_are_canonical_market_state",
        "candidate_rows_are_downstream_consumable",
        "official_market_state_allowed",
        "production_builder_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
    ]
    scope_false_flags = [
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
    for flag in scope_false_flags:
        if scope_authority.get(flag) is not False:
            failures.append({"level": "scope", "flag": flag, "observed": scope_authority.get(flag)})
    for flag in manifest_false_flags:
        if final_manifest.get(flag) is not False:
            failures.append({"level": "final_manifest", "flag": flag, "observed": final_manifest.get(flag)})
    for record in records:
        authority = record.get("authority") or {}
        for flag in [
            "candidate_records_are_canonical_market_state",
            "candidate_records_are_downstream_consumable",
            "parquet_write_allowed",
            "state_materialization_allowed",
        ]:
            if authority.get(flag) is not False:
                failures.append(
                    {
                        "level": "candidate_record",
                        "source_candidate_record_id": record.get("market_state_candidate_id"),
                        "flag": flag,
                        "observed": authority.get(flag),
                    }
                )
    return {
        "authority_failures": len(failures),
        "source_market_data_rows_read": 0,
        "source_market_data_read_verification": "verified_by_static_input_boundary_not_os_filesystem_audit",
        "failures": failures,
    }


def validate_artifacts(
    scope: dict[str, Any],
    scope_path: Path,
    materialization_run_dir: Path,
    materialization_manifest: dict[str, Any],
    final_manifest: dict[str, Any],
) -> dict[str, Any]:
    parquet_name = scope["authority"]["candidate_parquet_filename"]
    parquet_path = materialization_run_dir / parquet_name
    parquet_files = sorted(materialization_run_dir.glob("*.parquet"))
    actual_sha = sha256_file(parquet_path) if parquet_path.exists() else None
    actual_bytes = parquet_path.stat().st_size if parquet_path.exists() else None
    manifest_sha = materialization_manifest.get("parquet_sha256")
    manifest_bytes = materialization_manifest.get("parquet_bytes")
    final_sha = final_manifest.get("parquet_sha256")
    final_bytes = final_manifest.get("candidate_parquet_bytes") or final_manifest.get("parquet_bytes")
    input_artifact_checks = []
    for name, rel_path in (scope.get("input_artifacts") or {}).items():
        path = resolve_path(rel_path, scope_path.parent)
        mm = (materialization_manifest.get("input_artifacts") or {}).get(name, {})
        actual_input_sha = sha256_file(path) if path.exists() else None
        actual_input_bytes = path.stat().st_size if path.exists() else None
        input_artifact_checks.append(
            {
                "artifact": name,
                "path": str(path),
                "exists": path.exists(),
                "sha256_matches_materialization_manifest": actual_input_sha == mm.get("sha256"),
                "bytes_match_materialization_manifest": actual_input_bytes == mm.get("bytes"),
                "actual_sha256": actual_input_sha,
                "manifest_sha256": mm.get("sha256"),
                "actual_bytes": actual_input_bytes,
                "manifest_bytes": mm.get("bytes"),
            }
        )
    return {
        "materialization_run_dir": str(materialization_run_dir),
        "parquet_path": str(parquet_path),
        "parquet_exists": parquet_path.exists(),
        "parquet_files_found": len(parquet_files),
        "parquet_files": [str(p) for p in parquet_files],
        "parquet_sha256": actual_sha,
        "parquet_bytes": actual_bytes,
        "parquet_sha256_matches_materialization_manifest": actual_sha == manifest_sha,
        "parquet_bytes_match_materialization_manifest": actual_bytes == manifest_bytes,
        "parquet_sha256_matches_final_manifest": actual_sha == final_sha if final_sha else None,
        "parquet_bytes_match_final_manifest": actual_bytes == final_bytes if final_bytes else None,
        "maximum_output_bytes_respected": bool(
            actual_bytes is not None and actual_bytes <= scope["limits"]["maximum_output_bytes"]
        ),
        "input_artifact_checks": input_artifact_checks,
    }


def build_run_id() -> str:
    return f"{RUN_ID_PREFIX}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def main() -> int:
    parser = argparse.ArgumentParser(description=SCRIPT_VERSION)
    parser.add_argument("--scope", default=str(DEFAULT_SCOPE))
    parser.add_argument("--materialization-run-id", default=DEFAULT_MATERIALIZATION_RUN_ID)
    parser.add_argument("--materialization-run-dir", default=None)
    parser.add_argument("--output-run-id", default=None)
    args = parser.parse_args()

    scope_path = Path(args.scope).resolve()
    integration_root = scope_path.parents[1]
    runs_root = integration_root / "runs"
    scope = read_json(scope_path)
    materialization_run_dir = (
        Path(args.materialization_run_dir).resolve()
        if args.materialization_run_dir
        else runs_root / args.materialization_run_id
    )
    if not materialization_run_dir.exists():
        raise ValidationError(f"Missing materialization run dir: {materialization_run_dir}")

    run_id = args.output_run_id or build_run_id()
    output_dir = runs_root / run_id
    if output_dir.exists():
        raise ValidationError(f"Output run already exists: {output_dir}")
    output_dir.mkdir(parents=True)

    started_at = utc_now()
    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started_at,
        "scope_path": str(scope_path),
        "materialization_run_dir": str(materialization_run_dir),
        "validation_scope": "independent_physical_candidate_validation_no_parquet_write",
        "writes_candidate_parquet": False,
        "source_market_data_rows_read": 0,
        "source_market_data_read_verification": "verified_by_static_input_boundary_not_os_filesystem_audit",
    }
    write_json(output_dir / "pre_manifest.json", pre_manifest)
    write_json(output_dir / "heartbeat.json", {**pre_manifest, "status": "running", "updated_at_utc": utc_now()})

    materialization_manifest = read_json(materialization_run_dir / "materialization_manifest.json")
    materialization_final_manifest = read_json(materialization_run_dir / "final_manifest.json")
    parquet_path = materialization_run_dir / scope["authority"]["candidate_parquet_filename"]
    candidate_records_path = resolve_path(scope["input_artifacts"]["market_state_candidate_records"], scope_path.parent)
    rejected_context_path = resolve_path(scope["input_artifacts"]["rejected_context_report"], scope_path.parent)
    records = sort_records(read_jsonl(candidate_records_path))
    rejected_rows = read_csv_rows(rejected_context_path)
    rejected_context_ids = {row.get("context_id") for row in rejected_rows if row.get("context_id")}

    table = pq.read_table(parquet_path)
    observed_rows = table.to_pylist()
    pk_fields = scope["physical_schema"]["primary_key"]
    observed_rows = sort_rows(observed_rows, pk_fields)
    expected_rows = sort_rows(build_expected_rows(records, scope, materialization_manifest["run_id"]), pk_fields)
    semantic_rebuild_rows = sort_rows(
        build_expected_rows(records, scope, materialization_manifest["run_id"] + "_semantic_rebuild_validation"),
        pk_fields,
    )

    records_by_id = {record["market_state_candidate_id"]: record for record in records}
    rows_by_source_id = {row["source_candidate_record_id"]: row for row in observed_rows}

    artifact = validate_artifacts(scope, scope_path, materialization_run_dir, materialization_manifest, materialization_final_manifest)
    schema = schema_report(scope, table)
    source_ids = [row.get("source_candidate_record_id") for row in observed_rows]
    materialized_ids = [row.get("materialized_state_candidate_id") for row in observed_rows]
    primary_keys = [row_key(row, pk_fields) for row in observed_rows]
    rejected_in_parquet = sorted(rejected_context_ids & {row.get("context_id") for row in observed_rows})
    source_id_counts = Counter(source_ids)
    materialized_id_counts = Counter(materialized_ids)
    primary_key_counts = Counter(primary_keys)
    grain_rows = [
        {
            "source_candidate_record_id": row.get("source_candidate_record_id"),
            "materialized_state_candidate_id": row.get("materialized_state_candidate_id"),
            "context_id": row.get("context_id"),
            "primary_key": canonical_json(list(row_key(row, pk_fields)), ensure_ascii=False),
            "primary_key_duplicate": primary_key_counts[row_key(row, pk_fields)] > 1,
            "source_candidate_record_id_duplicate": source_id_counts[row.get("source_candidate_record_id")] > 1,
            "materialized_state_candidate_id_duplicate": materialized_id_counts[row.get("materialized_state_candidate_id")] > 1,
            "rejected_context_materialized": row.get("context_id") in rejected_context_ids,
        }
        for row in observed_rows
    ]
    grain = {
        "rows": len(observed_rows),
        "expected_rows": scope["limits"]["maximum_output_candidate_rows"],
        "input_candidate_records": len(records),
        "expected_input_candidate_records": scope["limits"]["maximum_input_candidate_records"],
        "duplicate_primary_keys": counter_duplicate_count(primary_keys),
        "duplicate_source_candidate_record_ids": counter_duplicate_count(source_ids),
        "duplicate_materialized_state_candidate_ids": counter_duplicate_count(materialized_ids),
        "rejected_contexts_in_parquet": len(rejected_in_parquet),
        "rejected_context_ids_in_parquet": rejected_in_parquet,
    }

    value_rows, value_summary = validate_values(records_by_id, rows_by_source_id, scope)
    lineage = validate_lineage(records_by_id, rows_by_source_id, scope)
    fingerprint_rows, fingerprint_summary = validate_fingerprints(observed_rows, scope)
    roundtrip_rows, roundtrip_summary = validate_roundtrip(expected_rows, observed_rows, scope)
    rebuild = validate_semantic_rebuild(expected_rows, semantic_rebuild_rows, scope)
    authority = validate_authority(scope, records, materialization_final_manifest)

    write_json(output_dir / "artifact_report.json", artifact)
    write_json(output_dir / "schema_validation_report.json", schema)
    write_csv_rows(
        output_dir / "grain_validation_report.csv",
        [
            "source_candidate_record_id",
            "materialized_state_candidate_id",
            "context_id",
            "primary_key",
            "primary_key_duplicate",
            "source_candidate_record_id_duplicate",
            "materialized_state_candidate_id_duplicate",
            "rejected_context_materialized",
        ],
        grain_rows,
    )
    write_csv_rows(
        output_dir / "value_reconciliation_report.csv",
        [
            "source_candidate_record_id",
            "context_id",
            "source_value_field",
            "physical_field",
            "source_value",
            "physical_value",
            "type",
            "match",
        ],
        value_rows,
    )
    write_json(output_dir / "lineage_content_report.json", lineage)
    write_csv_rows(
        output_dir / "fingerprint_validation_report.csv",
        [
            "source_candidate_record_id",
            "context_id",
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
        output_dir / "roundtrip_validation_report.csv",
        [
            "source_candidate_record_id",
            "context_id",
            "fields_checked",
            "field_mismatch_count",
            "roundtrip_match",
            "mismatched_fields",
        ],
        roundtrip_rows,
    )
    write_json(output_dir / "semantic_rebuild_validation_report.json", rebuild)
    write_json(output_dir / "authority_validation_report.json", authority)

    hard_failures = {
        "parquet_missing": int(not artifact["parquet_exists"]),
        "parquet_file_count_failures": int(artifact["parquet_files_found"] != scope["limits"]["maximum_candidate_parquet_files"]),
        "parquet_sha256_manifest_mismatches": int(not artifact["parquet_sha256_matches_materialization_manifest"]),
        "parquet_bytes_manifest_mismatches": int(not artifact["parquet_bytes_match_materialization_manifest"]),
        "parquet_size_limit_failures": int(not artifact["maximum_output_bytes_respected"]),
        "row_count_failures": int(len(observed_rows) != scope["limits"]["maximum_output_candidate_rows"]),
        "input_record_count_failures": int(len(records) != scope["limits"]["maximum_input_candidate_records"]),
        "column_order_failures": int(not schema["column_order_exact"]),
        "schema_failures": int(not schema["arrow_schema_exact_ignoring_metadata"]),
        "timestamp_timezone_failures": int(not schema["timestamp_timezone_utc"]),
        "duplicate_primary_keys": grain["duplicate_primary_keys"],
        "duplicate_source_candidate_record_ids": grain["duplicate_source_candidate_record_ids"],
        "duplicate_materialized_state_candidate_ids": grain["duplicate_materialized_state_candidate_ids"],
        "rejected_contexts_materialized_as_rows": grain["rejected_contexts_in_parquet"],
        "source_to_physical_value_mismatches": value_summary["source_to_physical_value_mismatches"],
        "missing_source_value_fields": value_summary["missing_source_value_fields"],
        "extra_source_value_fields": value_summary["extra_source_value_fields"],
        "rvol_rename_failures": int(not value_summary["rvol_rename_passed"]),
        "source_lineage_content_mismatches": lineage["source_lineage_content_mismatches"],
        "policy_version_mismatches": lineage["policy_version_mismatches"],
        "formula_version_mismatches": lineage["formula_version_mismatches"],
        "restriction_mismatches": lineage["restriction_mismatches"],
        "context_fingerprint_mismatches": lineage["context_fingerprint_mismatches"],
        "state_output_fingerprint_mismatches": fingerprint_summary["state_output_fingerprint_mismatches"],
        "materialized_state_candidate_id_mismatches": fingerprint_summary["materialized_state_candidate_id_mismatches"],
        "roundtrip_row_mismatches": roundtrip_summary["roundtrip_row_mismatches"],
        "roundtrip_field_mismatches": roundtrip_summary["roundtrip_field_mismatches"],
        "semantic_rebuild_differences": rebuild["semantic_rebuild_differences"],
        "authority_failures": authority["authority_failures"],
    }
    hard_validation_failures = sum(int(v) for v in hard_failures.values())
    status = "PASS_WITH_RESTRICTIONS" if hard_validation_failures == 0 else "FAIL"
    overall_status = (
        "passed_core_four_market_state_candidate_physical_validation_with_restrictions"
        if hard_validation_failures == 0
        else "failed_core_four_market_state_candidate_physical_validation"
    )

    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "status": "complete",
        "overall_status": overall_status,
        "core_four_market_state_candidate_physical_validation": status,
        "source_materialization_run_id": materialization_manifest["run_id"],
        "source_integration_run_id": scope["source_integration_run_id"],
        "logical_profile_id": scope["logical_profile_id"],
        "physical_schema_id": scope["physical_schema_id"],
        "parquet_exists": artifact["parquet_exists"],
        "parquet_files_found": artifact["parquet_files_found"],
        "parquet_sha256": artifact["parquet_sha256"],
        "parquet_bytes": artifact["parquet_bytes"],
        "parquet_sha256_matches_manifest": artifact["parquet_sha256_matches_materialization_manifest"],
        "parquet_bytes_match_manifest": artifact["parquet_bytes_match_materialization_manifest"],
        "input_candidate_records": len(records),
        "output_physical_rows": len(observed_rows),
        "physical_column_count": len(table.schema.names),
        "physical_value_column_count": len(scope["physical_schema"]["value_columns"]),
        "schema_match": schema["arrow_schema_exact_ignoring_metadata"],
        "column_order_exact": schema["column_order_exact"],
        "timestamp_timezone_utc": schema["timestamp_timezone_utc"],
        **grain,
        **value_summary,
        "source_lineage_content_mismatches": lineage["source_lineage_content_mismatches"],
        "policy_version_mismatches": lineage["policy_version_mismatches"],
        "formula_version_mismatches": lineage["formula_version_mismatches"],
        "restriction_mismatches": lineage["restriction_mismatches"],
        "context_fingerprint_mismatches": lineage["context_fingerprint_mismatches"],
        **fingerprint_summary,
        **roundtrip_summary,
        "semantic_rebuild_compare_field_count": rebuild["semantic_rebuild_compare_field_count"],
        "semantic_rebuild_field_comparisons": rebuild["semantic_rebuild_field_comparisons"],
        "semantic_rebuild_differences": rebuild["semantic_rebuild_differences"],
        "byte_identical_parquet_rebuild_required": rebuild["byte_identical_parquet_rebuild_required"],
        "source_market_data_rows_read": authority["source_market_data_rows_read"],
        "source_market_data_read_verification": authority["source_market_data_read_verification"],
        "authority_failures": authority["authority_failures"],
        "hard_failures": hard_failures,
        "hard_validation_failures": hard_validation_failures,
        "candidate_rows_are_canonical_market_state": False,
        "candidate_rows_are_downstream_consumable": False,
        "official_market_state_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
        "next_allowed_gate": "bounded_multi_context_or_review_planning_only_after_explicit_authorization",
    }
    write_json(output_dir / "final_manifest.json", final_manifest)
    write_json(
        output_dir / "heartbeat.json",
        {"run_id": run_id, "status": "complete", "updated_at_utc": utc_now(), "overall_status": overall_status},
    )
    print(json.dumps(final_manifest, indent=2, ensure_ascii=False))
    return 0 if hard_validation_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
