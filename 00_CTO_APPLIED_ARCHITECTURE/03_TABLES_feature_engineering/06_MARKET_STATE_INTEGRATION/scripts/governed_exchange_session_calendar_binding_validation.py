from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


SCRIPT_VERSION = "governed_exchange_session_calendar_binding_validation_v0_1"
RUN_ID_PREFIX = "governed_exchange_session_calendar_binding_validation_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "governed_exchange_session_calendar_binding_scope_v0_1.json"
)


class ValidationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_run_id() -> str:
    return f"{RUN_ID_PREFIX}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: serialize_csv(row.get(k)) for k in fieldnames})


def serialize_csv(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return canonical_json(value)
    return str(value)


def ensure_authority(scope: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    authority = scope.get("authority", {})
    required_true = [
        "calendar_binding_validation_authorized",
        "calendar_source_parquet_read_allowed",
        "calendar_source_meta_read_allowed",
        "run_local_bound_calendar_artifact_write_allowed",
    ]
    required_false = [
        "official_calendar_write_allowed",
        "calendar_source_mutation_allowed",
        "market_price_data_read_allowed",
        "builder_execution_allowed",
        "information_object_resolution_allowed",
        "market_state_integration_allowed",
        "market_state_materialization_allowed",
        "market_state_parquet_write_allowed",
        "scale_b_authorization_allowed",
        "scale_b_execution_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
        "reference_library_read_or_stage_allowed",
    ]
    for key in required_true:
        if authority.get(key) is not True:
            failures.append({"flag": key, "expected": True, "observed": authority.get(key)})
    for key in required_false:
        if authority.get(key) is not False:
            failures.append({"flag": key, "expected": False, "observed": authority.get(key)})
    return failures


def source_snapshot(scope: dict[str, Any]) -> dict[str, Any]:
    source_cfg = scope["source_boundary"]["active_physical_source_artifact"]
    documented_cfg = scope["source_boundary"]["preferred_documented_representation"]
    source_path = Path(source_cfg["path"])
    meta_path = Path(source_cfg["meta_path"])
    documented_path = Path(documented_cfg["documented_processed_path"])
    if not source_path.exists():
        raise ValidationError(f"Calendar source parquet missing: {source_path}")
    if not meta_path.exists():
        raise ValidationError(f"Calendar source meta missing: {meta_path}")
    source_sha = sha256_file(source_path)
    meta_sha = sha256_file(meta_path)
    meta = read_json(meta_path)
    pf = pq.ParquetFile(source_path)
    snapshot_payload = {
        "source_path": str(source_path),
        "source_sha256": source_sha,
        "source_bytes": source_path.stat().st_size,
        "meta_path": str(meta_path),
        "meta_sha256": meta_sha,
        "expected_sha256": source_cfg["expected_sha256"],
        "expected_rows": source_cfg["expected_rows"],
        "expected_calendar": source_cfg["expected_calendar"],
        "expected_timezone": source_cfg["expected_timezone"],
        "calendar_version": scope["calendar_version"],
        "field_binding_rules": scope["field_binding_rules"],
    }
    meta_files = meta.get("files", []) if isinstance(meta, dict) else []
    meta_declared_paths = [str(item.get("path")) for item in meta_files if isinstance(item, dict)]
    meta_declared_hash_match = any(
        isinstance(item, dict) and item.get("sha256") == source_sha for item in meta_files
    )
    meta_declared_resolved_path_match = any(
        Path(path).as_posix().lower() == source_path.as_posix().lower()
        for path in meta_declared_paths
    )
    return {
        "source_path": str(source_path),
        "source_exists": source_path.exists(),
        "source_bytes": source_path.stat().st_size,
        "source_sha256": source_sha,
        "source_sha256_match": source_sha == source_cfg["expected_sha256"],
        "meta_path": str(meta_path),
        "meta_exists": meta_path.exists(),
        "meta_sha256": meta_sha,
        "meta_declared_paths": meta_declared_paths,
        "meta_declared_hash_match": meta_declared_hash_match,
        "meta_declared_resolved_path_match": meta_declared_resolved_path_match,
        "documented_processed_path": str(documented_path),
        "documented_processed_path_exists": documented_path.exists(),
        "documented_processed_path_expected_available": documented_cfg.get(
            "documented_processed_path_available_in_workspace"
        ),
        "parquet_rows": pf.metadata.num_rows,
        "parquet_row_groups": pf.metadata.num_row_groups,
        "parquet_columns": pf.schema_arrow.names,
        "source_snapshot_payload": snapshot_payload,
        "source_snapshot_fingerprint": sha256_payload(snapshot_payload),
    }


def parse_calendar(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "open_utc": pd.to_datetime(df["open_utc"], utc=True, errors="coerce"),
        "close_utc": pd.to_datetime(df["close_utc"], utc=True, errors="coerce"),
        "open_et_as_utc": pd.to_datetime(df["open_et"], utc=True, errors="coerce"),
        "close_et_as_utc": pd.to_datetime(df["close_et"], utc=True, errors="coerce"),
    }


def iso_z(ts: pd.Timestamp) -> str:
    if pd.isna(ts):
        return ""
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def build_bound_rows(
    df: pd.DataFrame, scope: dict[str, Any], snapshot: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    parsed = parse_calendar(df)
    source_cfg = scope["source_boundary"]["active_physical_source_artifact"]
    version = scope["calendar_version"]
    rows: list[dict[str, Any]] = []
    reports = {
        "binding_rows": [],
        "duration_rows": [],
        "timezone_rows": [],
        "early_close_rows": [],
    }
    for idx, source in df.reset_index(drop=True).iterrows():
        session_date = str(source["session_date"])
        open_utc = parsed["open_utc"].iloc[idx]
        close_utc = parsed["close_utc"].iloc[idx]
        open_et_utc = parsed["open_et_as_utc"].iloc[idx]
        close_et_utc = parsed["close_et_as_utc"].iloc[idx]
        utc_minutes = None if pd.isna(open_utc) or pd.isna(close_utc) else int((close_utc - open_utc).total_seconds() // 60)
        local_minutes = None if pd.isna(open_et_utc) or pd.isna(close_et_utc) else int((close_et_utc - open_et_utc).total_seconds() // 60)
        source_early = bool(source["is_early_close"])
        derived_early = utc_minutes is not None and utc_minutes < 390
        is_regular = (not source_early) and utc_minutes == 390
        session_type = "early_close" if source_early else "regular"
        calendar_code = str(source["calendar"])
        row = {
            "calendar_id": f"{calendar_code}::{session_date}::{version}",
            "exchange_calendar_code": calendar_code,
            "mic_or_exchange_code": calendar_code,
            "session_date": session_date,
            "session_open_utc": iso_z(open_utc),
            "session_close_utc": iso_z(close_utc),
            "session_open_local": str(source["open_et"]),
            "session_close_local": str(source["close_et"]),
            "timezone": str(source["timezone"]),
            "session_minutes": int(utc_minutes) if utc_minutes is not None else -1,
            "session_type": session_type,
            "is_regular_session": bool(is_regular),
            "is_early_close": source_early,
            "is_closed_or_holiday": False,
            "calendar_version": version,
            "source_calendar_artifact": str(Path(source_cfg["path"])),
            "source_snapshot_fingerprint": snapshot["source_snapshot_fingerprint"],
        }
        row["calendar_row_fingerprint"] = sha256_payload(row)
        rows.append(row)
        open_equivalent = bool(not pd.isna(open_utc) and not pd.isna(open_et_utc) and open_utc == open_et_utc)
        close_equivalent = bool(not pd.isna(close_utc) and not pd.isna(close_et_utc) and close_utc == close_et_utc)
        duration_match = bool(utc_minutes == local_minutes and utc_minutes is not None)
        early_match = bool(source_early == derived_early)
        reports["binding_rows"].append({
            "source_row_index": idx,
            "session_date": session_date,
            "calendar_id": row["calendar_id"],
            "session_type": session_type,
            "session_minutes": row["session_minutes"],
            "is_regular_session": row["is_regular_session"],
            "is_early_close": source_early,
            "all_checks_passed": open_equivalent and close_equivalent and duration_match and early_match,
            "calendar_row_fingerprint": row["calendar_row_fingerprint"],
        })
        reports["duration_rows"].append({
            "source_row_index": idx,
            "session_date": session_date,
            "utc_minutes": utc_minutes,
            "local_minutes": local_minutes,
            "duration_match": duration_match,
            "regular_duration_expected": not source_early,
            "regular_duration_match": (utc_minutes == 390) if not source_early else "not_applicable",
        })
        reports["timezone_rows"].append({
            "source_row_index": idx,
            "session_date": session_date,
            "open_utc": str(source["open_utc"]),
            "open_et": str(source["open_et"]),
            "open_utc_equivalent_to_open_et": open_equivalent,
            "close_utc": str(source["close_utc"]),
            "close_et": str(source["close_et"]),
            "close_utc_equivalent_to_close_et": close_equivalent,
        })
        reports["early_close_rows"].append({
            "source_row_index": idx,
            "session_date": session_date,
            "source_is_early_close": source_early,
            "derived_is_early_close_from_duration": derived_early,
            "session_minutes": utc_minutes,
            "early_close_match": early_match,
        })
    return rows, reports


def arrow_schema() -> pa.Schema:
    return pa.schema([
        pa.field("calendar_id", pa.string(), nullable=False),
        pa.field("exchange_calendar_code", pa.string(), nullable=False),
        pa.field("mic_or_exchange_code", pa.string(), nullable=False),
        pa.field("session_date", pa.string(), nullable=False),
        pa.field("session_open_utc", pa.string(), nullable=False),
        pa.field("session_close_utc", pa.string(), nullable=False),
        pa.field("session_open_local", pa.string(), nullable=False),
        pa.field("session_close_local", pa.string(), nullable=False),
        pa.field("timezone", pa.string(), nullable=False),
        pa.field("session_minutes", pa.int32(), nullable=False),
        pa.field("session_type", pa.string(), nullable=False),
        pa.field("is_regular_session", pa.bool_(), nullable=False),
        pa.field("is_early_close", pa.bool_(), nullable=False),
        pa.field("is_closed_or_holiday", pa.bool_(), nullable=False),
        pa.field("calendar_version", pa.string(), nullable=False),
        pa.field("source_calendar_artifact", pa.string(), nullable=False),
        pa.field("source_snapshot_fingerprint", pa.string(), nullable=False),
        pa.field("calendar_row_fingerprint", pa.string(), nullable=False),
    ])


def validate_rows(
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    reports: dict[str, list[dict[str, Any]]],
    scope: dict[str, Any],
) -> dict[str, Any]:
    source_cfg = scope["source_boundary"]["active_physical_source_artifact"]
    expected_columns = source_cfg["observed_columns"]
    missing_columns = [c for c in expected_columns if c not in df.columns]
    extra_columns = [c for c in df.columns if c not in expected_columns]
    calendar_values = sorted(str(x) for x in df["calendar"].dropna().unique()) if "calendar" in df else []
    timezone_values = sorted(str(x) for x in df["timezone"].dropna().unique()) if "timezone" in df else []
    duplicate_session_dates = int(df["session_date"].duplicated().sum()) if "session_date" in df else -1
    parsed = parse_calendar(df)
    open_utc_before_close_failures = 0
    open_local_before_close_failures = 0
    for i in range(len(df)):
        ou = parsed["open_utc"].iloc[i]
        cu = parsed["close_utc"].iloc[i]
        ol = parsed["open_et_as_utc"].iloc[i]
        cl = parsed["close_et_as_utc"].iloc[i]
        if pd.isna(ou) or pd.isna(cu) or not (ou < cu):
            open_utc_before_close_failures += 1
        if pd.isna(ol) or pd.isna(cl) or not (ol < cl):
            open_local_before_close_failures += 1
    duration_mismatches = sum(1 for r in reports["duration_rows"] if r["duration_match"] is not True)
    timezone_open_mismatches = sum(1 for r in reports["timezone_rows"] if r["open_utc_equivalent_to_open_et"] is not True)
    timezone_close_mismatches = sum(1 for r in reports["timezone_rows"] if r["close_utc_equivalent_to_close_et"] is not True)
    early_close_mismatches = sum(1 for r in reports["early_close_rows"] if r["early_close_match"] is not True)
    row_fp_mismatches = 0
    fingerprint_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        payload = dict(row)
        observed = payload.pop("calendar_row_fingerprint")
        recomputed = sha256_payload(payload)
        match = observed == recomputed
        row_fp_mismatches += int(not match)
        fingerprint_rows.append({
            "row_index": idx,
            "session_date": row["session_date"],
            "calendar_row_fingerprint": observed,
            "recomputed_calendar_row_fingerprint": recomputed,
            "match": match,
        })
    return {
        "source_rows": int(len(df)),
        "bound_rows": int(len(rows)),
        "source_columns": list(df.columns),
        "missing_source_columns": missing_columns,
        "extra_source_columns": extra_columns,
        "calendar_values": calendar_values,
        "timezone_values": timezone_values,
        "calendar_all_rows_expected": calendar_values == [source_cfg["expected_calendar"]],
        "timezone_all_rows_expected": timezone_values == [source_cfg["expected_timezone"]],
        "session_date_duplicates": duplicate_session_dates,
        "open_utc_before_close_utc_failures": open_utc_before_close_failures,
        "open_local_before_close_local_failures": open_local_before_close_failures,
        "utc_local_equivalence_failures": timezone_open_mismatches + timezone_close_mismatches,
        "session_minutes_duration_mismatches": duration_mismatches,
        "early_close_mismatches": early_close_mismatches,
        "calendar_row_fingerprint_mismatches": row_fp_mismatches,
        "fingerprint_rows": fingerprint_rows,
        "expected_early_close_sessions_match": int(df["is_early_close"].sum()) == source_cfg["expected_early_close_sessions"],
        "first_session": str(df["session_date"].min()),
        "last_session": str(df["session_date"].max()),
        "years": sorted(int(x) for x in df["year"].dropna().unique()),
        "early_close_sessions": int(df["is_early_close"].sum()),
    }


def build_readout(final_manifest: dict[str, Any]) -> str:
    return f"""# Governed Exchange Session Calendar Binding Validation Readout v0.1

Status: `{final_manifest['governed_exchange_session_calendar_binding_validation']}`
Date: `2026-07-23`
Run: `{final_manifest['run_id']}`

The run validates the bounded governed calendar binding required before Scale B. It does not authorize Scale B execution, builders, Market State integration, Market State materialization, production, downstream consumption, full-history/full-universe execution or promotion.

## Result

```text
source_rows = {final_manifest['source_rows']}
bound_rows = {final_manifest['bound_rows']}
source_sha256_match = {str(final_manifest['calendar_source_sha256_match']).lower()}
early_close_sessions = {final_manifest['early_close_sessions']}
session_date_duplicates = {final_manifest['session_date_duplicates']}
utc_local_equivalence_failures = {final_manifest['utc_local_equivalence_failures']}
session_minutes_duration_mismatches = {final_manifest['session_minutes_duration_mismatches']}
early_close_mismatches = {final_manifest['early_close_mismatches']}
calendar_row_fingerprint_mismatches = {final_manifest['calendar_row_fingerprint_mismatches']}
determinism_failures = {final_manifest['determinism_failures']}
authority_failures = {final_manifest['authority_failures']}
hard_validation_failures = {final_manifest['hard_validation_failures']}
```

## Source Boundary

```text
documented_processed_path_exists = {str(final_manifest['documented_processed_path_exists']).lower()}
active_source_path = {final_manifest['active_source_path']}
source_snapshot_fingerprint = {final_manifest['source_snapshot_fingerprint']}
```

The documented processed `E:\\TSIS\\data\\data_foundation_outputs\\market_calendar\\market_calendar_v0_1.parquet` path is unavailable in this workspace. The accepted binding evidence is the resolved local source path plus SHA-256.

## Next Gate

```text
next_allowed_gate = {final_manifest['next_allowed_gate']}
```

Scale B remains blocked until a separate authorization consumes this accepted calendar binding.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=SCRIPT_VERSION)
    parser.add_argument("--scope", default=str(DEFAULT_SCOPE))
    parser.add_argument("--output-run-id", default=None)
    args = parser.parse_args()
    integration_root = Path(__file__).resolve().parents[1]
    runs_root = integration_root / "runs"
    run_id = args.output_run_id or build_run_id()
    output_dir = runs_root / run_id
    output_dir.mkdir(parents=True, exist_ok=False)
    started_at = utc_now()

    scope_path = Path(args.scope)
    scope = read_json(scope_path)
    write_json(output_dir / "pre_manifest.json", {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started_at,
        "scope_path": str(scope_path),
        "authorization_artifact": scope.get("authorization_artifact"),
        "status": "running",
    })
    write_json(output_dir / "heartbeat.json", {"run_id": run_id, "status": "running", "updated_at_utc": utc_now()})

    authority_failures = ensure_authority(scope)
    snapshot = source_snapshot(scope)
    write_json(output_dir / "calendar_source_snapshot_manifest.json", snapshot)
    df = pd.read_parquet(snapshot["source_path"])
    rows, reports = build_bound_rows(df, scope, snapshot)
    validation = validate_rows(df, rows, reports, scope)

    schema = arrow_schema()
    table = pa.Table.from_pylist(rows, schema=schema)
    parquet_path = output_dir / "governed_exchange_session_calendar_bound_v0_1.parquet"
    pq.write_table(table, parquet_path, compression="snappy")
    parquet_sha = sha256_file(parquet_path)
    parquet_bytes = parquet_path.stat().st_size
    reread_rows = pq.read_table(parquet_path).to_pylist()

    fingerprint_rows = validation.pop("fingerprint_rows")
    write_csv(output_dir / "governed_exchange_session_calendar_binding_report.csv", [
        "source_row_index", "session_date", "calendar_id", "session_type", "session_minutes", "is_regular_session", "is_early_close", "all_checks_passed", "calendar_row_fingerprint",
    ], reports["binding_rows"])
    write_csv(output_dir / "calendar_duration_report.csv", [
        "source_row_index", "session_date", "utc_minutes", "local_minutes", "duration_match", "regular_duration_expected", "regular_duration_match",
    ], reports["duration_rows"])
    write_csv(output_dir / "calendar_timezone_equivalence_report.csv", [
        "source_row_index", "session_date", "open_utc", "open_et", "open_utc_equivalent_to_open_et", "close_utc", "close_et", "close_utc_equivalent_to_close_et",
    ], reports["timezone_rows"])
    write_csv(output_dir / "calendar_early_close_report.csv", [
        "source_row_index", "session_date", "source_is_early_close", "derived_is_early_close_from_duration", "session_minutes", "early_close_match",
    ], reports["early_close_rows"])
    write_csv(output_dir / "calendar_fingerprint_report.csv", [
        "row_index", "session_date", "calendar_row_fingerprint", "recomputed_calendar_row_fingerprint", "match",
    ], fingerprint_rows)

    expected_schema_names = [field.name for field in schema]
    observed_schema_names = pq.read_table(parquet_path).schema.names
    schema_report = {
        "source_columns": validation["source_columns"],
        "missing_source_columns": validation["missing_source_columns"],
        "extra_source_columns": validation["extra_source_columns"],
        "bound_schema_names": expected_schema_names,
        "observed_parquet_schema_names": observed_schema_names,
        "bound_schema_exact": observed_schema_names == expected_schema_names,
    }
    write_json(output_dir / "calendar_schema_report.json", schema_report)

    coverage_report = {
        "source_rows": validation["source_rows"],
        "bound_rows": validation["bound_rows"],
        "first_session": validation["first_session"],
        "last_session": validation["last_session"],
        "years": validation["years"],
        "year_count": len(validation["years"]),
        "early_close_sessions": validation["early_close_sessions"],
        "calendar_values": validation["calendar_values"],
        "timezone_values": validation["timezone_values"],
        "documented_processed_path_exists": snapshot["documented_processed_path_exists"],
        "meta_declared_hash_match": snapshot["meta_declared_hash_match"],
        "meta_declared_resolved_path_match": snapshot["meta_declared_resolved_path_match"],
    }
    write_json(output_dir / "calendar_coverage_report.json", coverage_report)
    authority_report = {
        "authority_failures": len(authority_failures),
        "authority_failure_rows": authority_failures,
        "calendar_source_files_read": 2,
        "market_price_data_rows_read": 0,
        "market_state_parquet_files_written": 0,
        "scale_b_execution_authorized": False,
        "official_calendar_write_allowed": False,
        "source_calendar_mutation_allowed": False,
    }
    write_json(output_dir / "calendar_authority_report.json", authority_report)

    rebuilt_rows, _ = build_bound_rows(df.copy(), scope, snapshot)
    determinism_differences = sum(
        1 for left, right in zip(rows, rebuilt_rows) if canonical_json(left) != canonical_json(right)
    )
    roundtrip_differences = sum(
        1 for left, right in zip(rows, reread_rows) if canonical_json(left) != canonical_json(right)
    )
    determinism_report = {
        "rebuilt_rows": len(rebuilt_rows),
        "source_rows": len(rows),
        "semantic_rebuild_differences": determinism_differences,
        "roundtrip_row_differences": roundtrip_differences,
        "byte_identical_parquet_rebuild_required": False,
    }
    write_json(output_dir / "calendar_binding_determinism_report.json", determinism_report)

    limits = scope["limits"]
    hard_failures = {
        "source_sha256_mismatches": int(not snapshot["source_sha256_match"]),
        "source_row_count_mismatches": int(validation["source_rows"] != limits["expected_calendar_rows"]),
        "bound_row_count_mismatches": int(validation["bound_rows"] != limits["maximum_bound_calendar_rows"]),
        "missing_source_columns": len(validation["missing_source_columns"]),
        "calendar_value_mismatches": int(not validation["calendar_all_rows_expected"]),
        "timezone_value_mismatches": int(not validation["timezone_all_rows_expected"]),
        "session_date_duplicates": validation["session_date_duplicates"],
        "open_utc_before_close_utc_failures": validation["open_utc_before_close_utc_failures"],
        "open_local_before_close_local_failures": validation["open_local_before_close_local_failures"],
        "utc_local_equivalence_failures": validation["utc_local_equivalence_failures"],
        "session_minutes_duration_mismatches": validation["session_minutes_duration_mismatches"],
        "early_close_mismatches": validation["early_close_mismatches"],
        "early_close_count_mismatches": int(not validation["expected_early_close_sessions_match"]),
        "calendar_row_fingerprint_mismatches": validation["calendar_row_fingerprint_mismatches"],
        "schema_failures": int(not schema_report["bound_schema_exact"]),
        "roundtrip_row_differences": roundtrip_differences,
        "determinism_failures": determinism_differences,
        "authority_failures": len(authority_failures),
        "bound_parquet_byte_limit_failures": int(parquet_bytes > limits["maximum_bound_calendar_parquet_bytes"]),
    }
    hard_validation_failures = sum(int(v) for v in hard_failures.values())
    status = "CLOSED_PASS_WITH_RESTRICTIONS" if hard_validation_failures == 0 else "FAILED_VALIDATION"
    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "status": "complete",
        "governed_exchange_session_calendar_binding_validation": status,
        "source_scope_id": scope["scope_id"],
        "calendar_profile_id": scope["calendar_profile_id"],
        "calendar_version": scope["calendar_version"],
        "active_source_path": snapshot["source_path"],
        "documented_processed_path": snapshot["documented_processed_path"],
        "documented_processed_path_exists": snapshot["documented_processed_path_exists"],
        "calendar_source_sha256": snapshot["source_sha256"],
        "calendar_source_sha256_match": snapshot["source_sha256_match"],
        "source_snapshot_fingerprint": snapshot["source_snapshot_fingerprint"],
        "meta_declared_hash_match": snapshot["meta_declared_hash_match"],
        "meta_declared_resolved_path_match": snapshot["meta_declared_resolved_path_match"],
        "source_rows": validation["source_rows"],
        "bound_rows": validation["bound_rows"],
        "bound_parquet_path": str(parquet_path),
        "bound_parquet_sha256": parquet_sha,
        "bound_parquet_bytes": parquet_bytes,
        "bound_schema_column_count": len(expected_schema_names),
        "maximum_bound_calendar_parquet_bytes": limits["maximum_bound_calendar_parquet_bytes"],
        "maximum_total_run_output_bytes": limits["maximum_total_run_output_bytes"],
        "calendar_values": validation["calendar_values"],
        "timezone_values": validation["timezone_values"],
        "first_session": validation["first_session"],
        "last_session": validation["last_session"],
        "early_close_sessions": validation["early_close_sessions"],
        "session_date_duplicates": validation["session_date_duplicates"],
        "open_utc_before_close_utc_failures": validation["open_utc_before_close_utc_failures"],
        "open_local_before_close_local_failures": validation["open_local_before_close_local_failures"],
        "utc_local_equivalence_failures": validation["utc_local_equivalence_failures"],
        "session_minutes_duration_mismatches": validation["session_minutes_duration_mismatches"],
        "early_close_mismatches": validation["early_close_mismatches"],
        "calendar_row_fingerprint_mismatches": validation["calendar_row_fingerprint_mismatches"],
        "roundtrip_row_differences": roundtrip_differences,
        "determinism_failures": determinism_differences,
        "authority_failures": len(authority_failures),
        "hard_failures": hard_failures,
        "hard_validation_failures": hard_validation_failures,
        "official_calendar_authorized": False,
        "scale_b_authorization_allowed": False,
        "scale_b_execution_allowed": False,
        "market_state_parquet_write_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
        "next_allowed_gate": "experimental_core_four_market_state_scale_b_authorization_design_or_calendar_aware_sample_design_after_explicit_review" if hard_validation_failures == 0 else "calendar_binding_remediation",
    }
    readout_text = build_readout(final_manifest)
    (output_dir / "governed_exchange_session_calendar_binding_validation_readout_v0_1.md").write_text(readout_text, encoding="utf-8", newline="\n")
    (integration_root / "governed_exchange_session_calendar_binding_validation_readout_v0_1.md").write_text(readout_text, encoding="utf-8", newline="\n")
    write_json(output_dir / "final_manifest.json", final_manifest)
    write_json(output_dir / "heartbeat.json", {"run_id": run_id, "status": "complete", "updated_at_utc": utc_now(), "overall_status": status})

    required_outputs = set(scope["required_outputs"])
    output_files = [item for item in output_dir.iterdir() if item.is_file()]
    output_names = {item.name for item in output_files}
    total_run_output_bytes = sum(item.stat().st_size for item in output_files)
    missing_outputs = sorted(required_outputs - output_names)
    unexpected_outputs = sorted(output_names - required_outputs)
    total_output_limit_failure = total_run_output_bytes > limits["maximum_total_run_output_bytes"]
    final_manifest["total_run_output_bytes"] = total_run_output_bytes
    if missing_outputs or unexpected_outputs or len(output_names) > limits["maximum_output_files"] or total_output_limit_failure:
        final_manifest["output_contract_failure"] = {
            "missing_outputs": missing_outputs,
            "unexpected_outputs": unexpected_outputs,
            "output_file_count": len(output_names),
            "total_run_output_bytes": total_run_output_bytes,
            "maximum_total_run_output_bytes": limits["maximum_total_run_output_bytes"],
            "total_output_limit_failure": total_output_limit_failure,
        }
        final_manifest["hard_validation_failures"] += (
            len(missing_outputs)
            + len(unexpected_outputs)
            + int(len(output_names) > limits["maximum_output_files"])
            + int(total_output_limit_failure)
        )
        final_manifest["governed_exchange_session_calendar_binding_validation"] = "FAILED_VALIDATION"
        write_json(output_dir / "final_manifest.json", final_manifest)
    else:
        write_json(output_dir / "final_manifest.json", final_manifest)

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False))
    return 0 if final_manifest["hard_validation_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
