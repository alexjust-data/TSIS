from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


SCRIPT_VERSION = "experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1"
RUN_ID_PREFIX = "experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_a_execution_scope_v0_1.json"
)
OBJECT_ORDER = [
    "price_location_structure",
    "price_movement",
    "trading_activity",
    "volatility_range_state",
]
PASS_STATUSES = {"PASS", "PASS_WITH_RESTRICTIONS"}


class ScaleABuilderError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe_value(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe_value(v) for v in value]
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return json_safe_value(value.item())
        except Exception:
            pass
    return value


def canonical_json(value: Any, *, ensure_ascii: bool = True) -> str:
    return json.dumps(
        json_safe_value(value),
        ensure_ascii=ensure_ascii,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json(value, ensure_ascii=True).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_safe_value(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ScaleABuilderError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row, ensure_ascii=False))
            handle.write("\n")


def serialize_cell(value: Any) -> str:
    safe = json_safe_value(value)
    if safe is None:
        return ""
    if isinstance(safe, (dict, list)):
        return canonical_json(safe, ensure_ascii=False)
    return str(safe)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialize_cell(row.get(field)) for field in fieldnames})


def resolve_path(raw: str, base: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_info(repo_root: Path) -> dict[str, Any]:
    return {
        "commit": git_value(["git", "rev-parse", "HEAD"], repo_root),
        "branch": git_value(["git", "branch", "--show-current"], repo_root),
        "dirty": bool(git_value(["git", "status", "--porcelain"], repo_root)),
    }


def load_builder_module(script_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("tsis_experimental_state_builder_probe", script_path)
    if spec is None or spec.loader is None:
        raise ScaleABuilderError(f"Cannot load builder module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_date(value: Any) -> date:
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime().date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def parse_utc_datetime(value: Any) -> datetime:
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def validate_authority(scope: dict[str, Any]) -> None:
    authority = scope.get("authority", {})
    for key in ["scale_a_execution_authorized", "builder_resolution_execution_allowed_for_scale_a"]:
        if authority.get(key) is not True:
            raise ScaleABuilderError(f"Authority violation: {key} must be true")
    for key in [
        "sample_reselection_allowed",
        "sample_manifest_mutation_allowed",
        "013_upstream_read_allowed",
        "raw_quotes_read_allowed",
        "quote_dependent_object_integration_allowed",
        "official_market_state_allowed",
        "official_state_table_write_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
        "scale_b_calendar_aware_execution_allowed",
        "scale_c_historical_bounded_execution_allowed",
    ]:
        if authority.get(key) is not False:
            raise ScaleABuilderError(f"Authority violation: {key} must be false")
    if "013_ohlcv_1m_quote_guarded" not in set(scope.get("source_aliases_forbidden", [])):
        raise ScaleABuilderError("013 must remain forbidden in this subgate")
    if set(scope.get("source_aliases_allowed", [])) != {
        "004_master_daily_table",
        "014_master_intraday_bar_table_candidate",
    }:
        raise ScaleABuilderError("Scale A builder must allow only 004 and 014 aliases")


def load_sample(sample_path: Path, scope: dict[str, Any]) -> list[dict[str, Any]]:
    rows = read_jsonl(sample_path)
    expected_rows = int(scope["limits"]["requested_contexts"])
    if len(rows) != expected_rows:
        raise ScaleABuilderError(f"Sample row count mismatch: expected={expected_rows} observed={len(rows)}")
    observed_fp = sha256_payload(rows)
    expected_fp = scope["input_artifacts"]["frozen_sample"]["scale_a_sample_fingerprint"]
    chain_fp = scope["execution_chain"]["sample_fingerprint_must_match"]
    if observed_fp != expected_fp or observed_fp != chain_fp:
        raise ScaleABuilderError(f"Sample fingerprint mismatch: observed={observed_fp}")
    duplicate_ids = [key for key, count in Counter(row["sample_context_id"] for row in rows).items() if count > 1]
    if duplicate_ids:
        raise ScaleABuilderError(f"Duplicate sample_context_id values: {duplicate_ids[:5]}")
    return rows


def source_path_report(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def load_daily_rows(daily_root: Path, sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tickers = sorted({str(row["ticker"]).upper() for row in sample_rows})
    years = sorted({parse_date(row["session_date"]).year for row in sample_rows})
    selected_rows: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    columns = ["instrument_id", "ticker", "session_date", "open", "prior_close", "volume"]
    for year in years:
        pattern_root = daily_root / f"year={year}" / "price_view=split_normalized"
        parquet_files = sorted(pattern_root.glob("*.parquet"))
        if not parquet_files:
            raise ScaleABuilderError(f"No 004 daily files found under {pattern_root}")
        for file_path in parquet_files:
            table = pq.read_table(file_path, columns=columns, filters=[("ticker", "in", tickers)])
            frame = table.to_pandas()
            files.append({"path": str(file_path), "rows_read_from_file": int(len(frame)), "sha256": sha256_file(file_path)})
            frame["__row_ordinal_in_file"] = range(len(frame))
            frame["ticker"] = frame["ticker"].astype(str).str.upper()
            for _, row in frame.iterrows():
                values = {col: json_safe_value(row[col]) for col in columns}
                selected_rows.append(
                    {
                        "file_path": str(file_path),
                        "row_ordinal_in_file": int(row["__row_ordinal_in_file"]),
                        "values": values,
                    }
                )
    manifest = {
        "source_alias": "004_master_daily_table",
        "root": str(daily_root),
        "files_sampled": files,
        "rows_read": len(selected_rows),
        "row_read_mode": "selected_tickers_from_authorized_year_price_view_partition",
        "tickers": tickers,
        "years": years,
        "price_view": "split_normalized",
    }
    return selected_rows, manifest


def load_intraday_rows(surface_path: Path, expected_sha256: str, sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    observed_sha = sha256_file(surface_path)
    if observed_sha != expected_sha256:
        raise ScaleABuilderError(
            f"Accepted 014 surface sha256 mismatch: expected={expected_sha256} observed={observed_sha}"
        )
    metadata = pq.ParquetFile(surface_path).metadata
    source_rows_observed = int(metadata.num_rows)
    tickers = sorted({str(row["ticker"]).upper() for row in sample_rows})
    sessions = sorted({str(row["session_date"]) for row in sample_rows})
    table = pq.read_table(surface_path, filters=[("ticker", "in", tickers), ("session_date", "in", sessions)])
    frame = table.to_pandas()
    frame["__derived_row_ordinal_in_file"] = range(len(frame))
    frame["ticker"] = frame["ticker"].astype(str).str.upper()
    frame["session_date"] = frame["session_date"].astype(str)
    filtered = frame.copy()
    columns = [
        "ticker",
        "instrument_id",
        "session_date",
        "ts_utc",
        "bar_end_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "duplicate_status",
        "source_alias",
        "source_file",
        "source_row_ordinal",
        "source_snapshot_fingerprint",
        "bar_size",
        "price_view",
        "selection_reason",
    ]
    rows: list[dict[str, Any]] = []
    for _, row in filtered.iterrows():
        values = {col: json_safe_value(row[col]) for col in columns if col in filtered.columns}
        values["ts_utc"] = values.get("bar_end_utc") or values.get("ts_utc")
        rows.append(
            {
                "file_path": str(surface_path),
                "row_ordinal_in_file": int(row["__derived_row_ordinal_in_file"]),
                "values": values,
            }
        )
    manifest = {
        "source_alias": "014_master_intraday_bar_table_candidate",
        "path": str(surface_path),
        "sha256": observed_sha,
        "bytes": surface_path.stat().st_size,
        "source_rows_observed": source_rows_observed,
        "rows_read": len(rows),
        "row_read_mode": "accepted_run_local_014_derived_candidate_surface_filtered_to_frozen_sample",
        "tickers": tickers,
        "sessions": sessions,
    }
    return rows, manifest


def prepare_intraday_rows_preserving_surface_status(builder: Any, rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, date], list[dict[str, Any]]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    bars_by_session: dict[tuple[str, date], list[dict[str, Any]]] = defaultdict(list)
    conflict_by_key: dict[str, dict[str, Any]] = {}
    findings: list[dict[str, Any]] = []
    for sample_row in rows:
        values = sample_row.get("values", {})
        ticker = builder.normalize_ticker(values.get("ticker"))
        session_date = builder.parse_session_date_value(values.get("session_date"))
        bar_end, parse_message, _, _ = builder.parse_timestamp_value(values.get("bar_end_utc") or values.get("ts_utc"))
        if not ticker or session_date is None or bar_end is None:
            findings.append(
                {
                    "source_alias": "014_master_intraday_bar_table_candidate",
                    "finding_type": "missing_intraday_key",
                    "severity": "FAIL",
                    "finding": f"014 row missing ticker/session_date/bar_end_utc: {parse_message}",
                    "evidence": builder.compact_json(
                        {
                            "file_path": sample_row.get("file_path"),
                            "row_ordinal_in_file": sample_row.get("row_ordinal_in_file"),
                        }
                    ),
                }
            )
            continue
        duplicate_status = str(values.get("duplicate_status") or "unique")
        duplicate_group_row_count = 2 if duplicate_status == "identical_duplicate_rows_collapsed" else 1
        duplicate_group_distinct_state_count = 1 if duplicate_status != "conflicting_duplicate_rows" else 2
        duplicate_group_key = builder.compact_json(
            [("ticker", ticker), ("bar_end_utc", builder.iso_utc(bar_end))]
        )
        if duplicate_status == "conflicting_duplicate_rows":
            conflict_by_key[duplicate_group_key] = {
                "row_count": duplicate_group_row_count,
                "distinct_state_count": duplicate_group_distinct_state_count,
            }
            findings.append(
                {
                    "source_alias": "014_master_intraday_bar_table_candidate",
                    "finding_type": "conflicting_intraday_duplicate",
                    "severity": "FAIL",
                    "finding": "014-derived surface marks selected candidate key as conflicting duplicate",
                    "evidence": builder.compact_json({"key": duplicate_group_key}),
                }
            )
        elif duplicate_status == "identical_duplicate_rows_collapsed":
            findings.append(
                {
                    "source_alias": "014_master_intraday_bar_table_candidate",
                    "finding_type": "identical_intraday_duplicate",
                    "severity": "WARN",
                    "finding": "014-derived surface preserves identical duplicate collapse status",
                    "evidence": builder.compact_json({"key": duplicate_group_key}),
                }
            )
        prepared = {
            "source_alias": "014_master_intraday_bar_table_candidate",
            "file_path": sample_row.get("file_path"),
            "row_ordinal_in_file": sample_row.get("row_ordinal_in_file"),
            "ticker": ticker,
            "instrument_id": builder.json_safe_value(values.get("instrument_id")),
            "session_date": session_date,
            "bar_end_utc": bar_end,
            "open": builder.float_or_none(values.get("open")),
            "high": builder.float_or_none(values.get("high")),
            "low": builder.float_or_none(values.get("low")),
            "close": builder.float_or_none(values.get("close")),
            "volume": builder.float_or_none(values.get("volume")),
            "duplicate_status": duplicate_status,
            "duplicate_group_key": duplicate_group_key,
            "duplicate_group_row_count": duplicate_group_row_count,
            "duplicate_group_distinct_state_count": duplicate_group_distinct_state_count,
            "raw_values": {key: builder.json_safe_value(value) for key, value in values.items()},
        }
        bars_by_session[(ticker, session_date)].append(prepared)
    for session_key in bars_by_session:
        bars_by_session[session_key] = sorted(
            bars_by_session[session_key],
            key=lambda row: (row["bar_end_utc"], str(row.get("file_path")), int(row.get("row_ordinal_in_file") or 0)),
        )
    return dict(bars_by_session), conflict_by_key, findings


def build_requests(sample_rows: list[dict[str, Any]], scope: dict[str, Any]) -> list[dict[str, Any]]:
    objects_per_context = int(scope["limits"]["required_objects_per_context"])
    if len(OBJECT_ORDER) != objects_per_context:
        raise ScaleABuilderError("Object order does not match required_objects_per_context")
    requests: list[dict[str, Any]] = []
    for context_index, sample in enumerate(sample_rows, start=1):
        context_id = str(sample["sample_context_id"])
        session_date = parse_date(sample["session_date"])
        decision_timestamp = parse_utc_datetime(sample["decision_timestamp_utc"])
        for object_id in OBJECT_ORDER:
            requests.append(
                {
                    "request_id": f"scale_a_req_{len(requests) + 1:04d}",
                    "context_id": context_id,
                    "sample_context_id": context_id,
                    "object_id": object_id,
                    "ticker": str(sample["ticker"]).upper(),
                    "instrument_id": sample.get("instrument_id"),
                    "session_date": session_date,
                    "decision_case": sample.get("decision_case"),
                    "decision_case_family": sample.get("decision_case_family"),
                    "decision_timestamp_utc": decision_timestamp,
                    "expected_context_outcome": sample.get("expected_context_outcome"),
                    "expected_materialized_as_row": sample.get("expected_materialized_as_row"),
                    "sample_index": context_index,
                }
            )
    expected = int(scope["limits"]["expected_resolution_records"])
    if len(requests) != expected:
        raise ScaleABuilderError(f"Resolution request count mismatch: expected={expected} observed={len(requests)}")
    return requests


def scale_a_restrictions_for_record(record: dict[str, Any], sample_by_context: dict[str, dict[str, Any]]) -> list[str]:
    sample = sample_by_context.get(str(record.get("context_id")), {})
    restrictions = [
        "scale_a_is_not_calendar_aware_validation",
        "fixed_utc_probe_calendar_requires_compatibility_guard",
    ]
    if sample.get("decision_case_family") == "after_last_sampled_bar_not_session_close":
        restrictions.append("after_last_sampled_bar_is_not_end_of_session")
    selected_bar = ((record.get("source_evidence") or {}).get("014_selected_closed_bar") or {})
    if selected_bar.get("duplicate_status") == "identical_duplicate_rows_collapsed":
        restrictions.append("014_identical_duplicate_rows_collapsed_deterministically")
    return restrictions


def recompute_record_fingerprint(builder: Any, record: dict[str, Any]) -> str:
    payload = {
        "request": {
            "object_id": record["object_id"],
            "instrument_id": record.get("instrument_id"),
            "ticker": record.get("ticker"),
            "decision_timestamp_utc": record.get("decision_timestamp_utc"),
        },
        "values": record.get("values") or {},
        "source_evidence": record.get("source_evidence") or {},
        "cutoff_evidence": record.get("cutoff_evidence") or {},
        "quality_evidence": record.get("quality_evidence") or {},
        "lineage": record.get("lineage") or {},
        "restrictions": record.get("restrictions") or [],
        "resolution_status": record.get("resolution_status"),
    }
    return builder.resolution_fingerprint(payload)


def enrich_outputs(builder: Any, outputs: tuple[list[dict[str, Any]], ...], sample_by_context: dict[str, dict[str, Any]], scale_scope: dict[str, Any]) -> tuple[list[dict[str, Any]], ...]:
    request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records = outputs
    records_by_request = {record["request_id"]: record for record in resolution_records}
    new_restriction_rows: list[dict[str, Any]] = []
    for record in resolution_records:
        record_restrictions = list(record.get("restrictions") or [])
        for restriction in scale_a_restrictions_for_record(record, sample_by_context):
            if restriction not in record_restrictions:
                record_restrictions.append(restriction)
                new_restriction_rows.append({
                    "request_id": record["request_id"],
                    "object_id": record["object_id"],
                    "restriction_type": "scale_a_execution_restriction",
                    "restriction": restriction,
                    "severity": "WARN",
                    "finding": "Scale A builder/resolution restriction preserved on the object record",
                })
        if record.get("resolution_status") == "PASS" and record_restrictions:
            record["resolution_status"] = "PASS_WITH_RESTRICTIONS"
        lineage = dict(record.get("lineage") or {})
        lineage["source_scope_id"] = SCRIPT_VERSION
        lineage["scale_a_execution_scope_id"] = scale_scope.get("scope_id")
        lineage["frozen_sample_fingerprint"] = scale_scope["input_artifacts"]["frozen_sample"]["scale_a_sample_fingerprint"]
        lineage["bounded_014_candidate_surface_sha256"] = scale_scope["input_artifacts"]["accepted_eligible_surface"]["bounded_014_candidate_surface_parquet_sha256"]
        record["lineage"] = lineage
        record["restrictions"] = sorted(set(record_restrictions))
        record["resolution_fingerprint"] = recompute_record_fingerprint(builder, record)
    restriction_rows.extend(new_restriction_rows)
    for row in request_rows:
        record = records_by_request[row["request_id"]]
        row["resolution_status"] = record["resolution_status"]
        row["resolution_fingerprint"] = record["resolution_fingerprint"]
        row["restrictions_count"] = len(record.get("restrictions") or [])
    return request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records


def execute_resolution_once(builder: Any, core_scope: dict[str, Any], scale_scope: dict[str, Any], requests: list[dict[str, Any]], daily_by_key: dict[tuple[str, date], dict[str, Any]], daily_by_ticker: dict[str, list[dict[str, Any]]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]], sample_by_context: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], ...]:
    outputs = builder.execute_core_four_resolution_pass(core_scope, requests, daily_by_key, daily_by_ticker, bars_by_session)
    return enrich_outputs(builder, outputs, sample_by_context, scale_scope)

def build_context_summary(records: list[dict[str, Any]], sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    expected_outcome_by_context = {row["sample_context_id"]: row.get("expected_context_outcome") for row in sample_rows}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["context_id"])].append(record)
    context_rows: list[dict[str, Any]] = []
    counts = Counter()
    for context_id in sorted(grouped):
        context_records = sorted(grouped[context_id], key=lambda row: row["object_id"])
        statuses = {row["object_id"]: row.get("resolution_status") for row in context_records}
        if any(str(status).startswith("FAILED") or status == "BLOCKED_CONFLICTING_SOURCE_ROWS" for status in statuses.values()):
            context_status = "FAILED_CONTEXT"
        elif any(status == "BLOCKED_INPUT_UNAVAILABLE" for status in statuses.values()):
            context_status = "BLOCKED_REQUIRED_OBJECT_INPUT_UNAVAILABLE"
        elif all(status in PASS_STATUSES for status in statuses.values()):
            context_status = "INTEGRABLE_COMPLETE_OR_WITH_RESTRICTIONS"
        else:
            context_status = "FAILED_CONTEXT"
        counts[context_status] += 1
        representative = context_records[0]
        context_fingerprint_payload = {
            "context_id": context_id,
            "instrument_id": representative.get("instrument_id"),
            "ticker": representative.get("ticker"),
            "session_date": representative.get("session_date"),
            "decision_timestamp_utc": representative.get("decision_timestamp_utc"),
            "decision_case": representative.get("decision_case"),
            "object_record_ids": {row["object_id"]: row.get("record_id") for row in context_records},
            "resolution_fingerprints": {row["object_id"]: row.get("resolution_fingerprint") for row in context_records},
        }
        context_rows.append({
            "context_id": context_id,
            "record_count": len(context_records),
            "object_ids": "|".join(sorted(statuses)),
            "context_resolution_status": context_status,
            "expected_context_outcome": expected_outcome_by_context.get(context_id),
            "context_input_fingerprint": sha256_payload(context_fingerprint_payload),
        })
    return context_rows, dict(counts)


def semantic_equality_report(records: list[dict[str, Any]]) -> tuple[int, int]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["context_id"]].append(record)
    checks = [
        ("price_movement__daily_prior_close", "price_location_structure__daily_prior_close"),
        ("price_movement__intraday_bar_close_price", "price_location_structure__intraday_bar_close_price"),
        ("price_movement__intraday_return_vs_prior_close_ratio", "price_location_structure__intraday_return_vs_prior_close_ratio_as_location"),
        ("price_movement__intraday_return_vs_session_open_ratio", "price_location_structure__intraday_return_vs_session_open_ratio_as_location"),
    ]
    total = 0
    failures = 0
    for context_records in grouped.values():
        if any(record.get("resolution_status") not in PASS_STATUSES for record in context_records):
            continue
        values: dict[str, Any] = {}
        for record in context_records:
            values.update(record.get("values") or {})
        for left, right in checks:
            total += 1
            if left not in values or right not in values:
                failures += 1
                continue
            try:
                if abs(float(values[left]) - float(values[right])) > 1e-12:
                    failures += 1
            except (TypeError, ValueError):
                if values[left] != values[right]:
                    failures += 1
    return total, failures

def build_summary(*, run_id: str, scope: dict[str, Any], sample_rows: list[dict[str, Any]], records: list[dict[str, Any]], formula_rows: list[dict[str, Any]], output_contract_rows: list[dict[str, Any]], determinism_rows: list[dict[str, Any]], restriction_rows: list[dict[str, Any]], duplicate_rows: list[dict[str, Any]], cutoff_rows: list[dict[str, Any]], source_manifests: dict[str, Any], context_counts: dict[str, int]) -> dict[str, Any]:
    limits = scope["limits"]
    source_rows_read = sum(int(doc.get("rows_read", 0)) for doc in source_manifests.values())
    formula_failures = sum(1 for row in formula_rows if row.get("formula_status") == "FAILED_FORMULA")
    contract_failures = sum(1 for row in output_contract_rows if row.get("output_contract_status") == "FAILED_OUTPUT_CONTRACT")
    nondeterministic = sum(1 for row in determinism_rows if row.get("repeat_run_fingerprint_match") is not True)
    future_leaks = sum(1 for row in cutoff_rows if row.get("future_leak") is True or str(row.get("future_leak")) == "True")
    conflict_blocks = sum(1 for row in records if row.get("resolution_status") == "BLOCKED_CONFLICTING_SOURCE_ROWS")
    input_blocks = sum(1 for row in records if row.get("resolution_status") == "BLOCKED_INPUT_UNAVAILABLE")
    pass_records = sum(1 for row in records if row.get("resolution_status") in PASS_STATUSES)
    failed_records = sum(1 for row in records if str(row.get("resolution_status", "")).startswith("FAILED"))
    blocked_contexts = int(context_counts.get("BLOCKED_REQUIRED_OBJECT_INPUT_UNAVAILABLE", 0))
    integrable_contexts = int(context_counts.get("INTEGRABLE_COMPLETE_OR_WITH_RESTRICTIONS", 0))
    failed_contexts = int(context_counts.get("FAILED_CONTEXT", 0))
    semantic_checks, semantic_failures = semantic_equality_report(records)
    hard_failures = sum([
        formula_failures,
        contract_failures,
        nondeterministic,
        future_leaks,
        conflict_blocks,
        failed_records,
        failed_contexts,
        semantic_failures,
        int(source_rows_read > int(limits["maximum_source_market_data_rows_read"])),
        int(len(records) != int(limits["expected_resolution_records"])),
        int(blocked_contexts > int(limits["maximum_blocked_contexts"])),
    ])
    expected_partition_ok = (
        integrable_contexts == int(limits["expected_integrable_contexts"])
        and blocked_contexts == int(limits["expected_blocked_contexts"])
        and failed_contexts == 0
    )
    if hard_failures:
        status = "FAILED"
    elif not expected_partition_ok:
        status = "PASS_WITH_RESTRICTIONS_UNEXPECTED_CONTEXT_PARTITION"
    else:
        status = "CLOSED_PASS_WITH_RESTRICTIONS"
    return {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_id": scope.get("scope_id"),
        "builder_resolution_execution_status": status,
        "sample_preflight_run_id": scope["input_artifacts"]["frozen_sample"]["preflight_run_id"],
        "sample_fingerprint_match": True,
        "scale_a_sample_fingerprint": scope["input_artifacts"]["frozen_sample"]["scale_a_sample_fingerprint"],
        "requested_contexts": len(sample_rows),
        "resolution_records": len(records),
        "expected_resolution_records": int(limits["expected_resolution_records"]),
        "required_objects_per_context": int(limits["required_objects_per_context"]),
        "pass_or_pass_with_restrictions_records": pass_records,
        "blocked_input_unavailable_records": input_blocks,
        "conflicting_source_row_blocks": conflict_blocks,
        "failed_records": failed_records,
        "integrable_contexts": integrable_contexts,
        "expected_integrable_contexts": int(limits["expected_integrable_contexts"]),
        "blocked_contexts": blocked_contexts,
        "expected_blocked_contexts": int(limits["expected_blocked_contexts"]),
        "failed_contexts": failed_contexts,
        "source_market_data_rows_read": source_rows_read,
        "maximum_source_market_data_rows_read": int(limits["maximum_source_market_data_rows_read"]),
        "source_rows_read_mode": "bounded_returned_rows_not_filesystem_access_audit",
        "source_004_rows_read": int(source_manifests["004_master_daily_table"].get("rows_read", 0)),
        "source_014_rows_read": int(source_manifests["014_master_intraday_bar_table_candidate"].get("rows_read", 0)),
        "formula_rows": len(formula_rows),
        "formula_failures": formula_failures,
        "future_bar_leaks": future_leaks,
        "output_contract_failures": contract_failures,
        "nondeterministic_records": nondeterministic,
        "restriction_rows": len(restriction_rows),
        "duplicate_report_rows": len(duplicate_rows),
        "duplicate_warning_rows": sum(1 for row in duplicate_rows if row.get("severity") == "WARN"),
        "semantic_equality_checks": semantic_checks,
        "semantic_equality_failures": semantic_failures,
        "hard_validation_failures": hard_failures,
        "sample_reselected": False,
        "sample_manifest_mutated": False,
        "013_upstream_rows_read": 0,
        "raw_quotes_rows_read": 0,
        "market_state_integration_executed": False,
        "candidate_market_state_records_emitted": 0,
        "candidate_parquet_files_written": 0,
        "official_market_state_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
        "next_allowed_gate": "experimental_core_four_market_state_scale_a_market_state_integration_execution",
    }

def write_readout(path: Path, summary: dict[str, Any], run_dir: Path) -> None:
    lines = [
        "# Experimental Core Four Market State Scale A Builder/Resolution Execution Readout v0.1",
        "",
        f"run_id: `{summary['run_id']}`",
        f"status: `{summary['builder_resolution_execution_status']}`",
        "",
        "## Scope",
        "",
        "This gate consumed the frozen Scale A sample and emitted Information Object resolution records only.",
        "It did not execute Market State integration, did not write candidate Market State parquet, and did not read 013 or raw quotes.",
        "",
        "## Counts",
        "",
        f"requested_contexts = {summary['requested_contexts']}",
        f"resolution_records = {summary['resolution_records']}",
        f"integrable_contexts = {summary['integrable_contexts']}",
        f"blocked_contexts = {summary['blocked_contexts']}",
        f"failed_contexts = {summary['failed_contexts']}",
        f"pass_or_pass_with_restrictions_records = {summary['pass_or_pass_with_restrictions_records']}",
        f"blocked_input_unavailable_records = {summary['blocked_input_unavailable_records']}",
        "",
        "## Validation",
        "",
        f"source_market_data_rows_read = {summary['source_market_data_rows_read']}",
        f"formula_failures = {summary['formula_failures']}",
        f"future_bar_leaks = {summary['future_bar_leaks']}",
        f"output_contract_failures = {summary['output_contract_failures']}",
        f"nondeterministic_records = {summary['nondeterministic_records']}",
        f"semantic_equality_failures = {summary['semantic_equality_failures']}",
        f"hard_validation_failures = {summary['hard_validation_failures']}",
        "",
        "## Restrictions Preserved",
        "",
        "- candidate artifacts remain non-canonical",
        "- core-four profile is not complete TSIS Market State",
        "- Scale A is not calendar-aware validation",
        "- fixed UTC probe calendar remains guarded",
        "- after_last_sampled_bar remains not-session-close semantics",
        "- quote-dependent objects remain excluded",
        "",
        "## Next Gate",
        "",
        "Allowed next: `experimental_core_four_market_state_scale_a_market_state_integration_execution`.",
        "Still closed: official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale B, Scale C.",
        "",
        "## Run Directory",
        "",
        f"`{run_dir}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def artifact_report(run_dir: Path, names: list[str]) -> dict[str, dict[str, Any]]:
    report: dict[str, dict[str, Any]] = {}
    for name in names:
        path = run_dir / name
        if path.exists():
            report[name] = {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute Scale A core-four builder/resolution records from a frozen sample.")
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    scope_path = args.scope.resolve()
    integration_root = scope_path.parents[1]
    feature_root = integration_root.parent
    repo_root = feature_root.parents[1]
    scope = read_json(scope_path)
    validate_authority(scope)

    run_id = args.run_id or f"{RUN_ID_PREFIX}_{safe_timestamp()}"
    run_dir = integration_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    started_at = utc_now()
    write_json(run_dir / "pre_manifest.json", {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "authority": scope.get("authority", {}),
        "status": "STARTED",
    })
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "RUNNING", "updated_at_utc": utc_now()})

    sample_info = scope["input_artifacts"]["frozen_sample"]
    sample_path = resolve_path(sample_info["sample_manifest_path"], scope_path.parent)
    sample_rows = load_sample(sample_path, scope)
    write_jsonl(run_dir / "scale_a_sample_manifest.jsonl", sample_rows)

    surface_info = scope["input_artifacts"]["accepted_eligible_surface"]
    surface_path = resolve_path(surface_info["bounded_014_candidate_surface_path"], scope_path.parent)
    expected_surface_sha = surface_info["bounded_014_candidate_surface_parquet_sha256"]

    registry_path = resolve_path(scope["governance_inputs"]["source_binding_registry"], scope_path.parent)
    registry = read_json(registry_path)
    daily_root = Path(registry["bindings"]["004_master_daily_table"]["physical_candidate_root"])
    core_scope_path = resolve_path(scope["governance_inputs"]["core_four_builder_scope_reference"], scope_path.parent)
    core_scope = read_json(core_scope_path)
    core_scope["scope_id"] = SCRIPT_VERSION
    core_scope["global_limits"] = {
        **core_scope.get("global_limits", {}),
        "maximum_total_input_rows": int(scope["limits"]["maximum_source_market_data_rows_read"]),
        "maximum_resolution_requests": int(scope["limits"]["maximum_resolution_records"]),
        "maximum_objects": int(scope["limits"]["required_objects_per_context"]),
        "maximum_instruments": int(scope["limits"]["instrument_count"]),
    }
    core_scope["request_generation"] = {
        **core_scope.get("request_generation", {}),
        "session_open_time_utc": scope["calendar_policy"]["required_selected_session_properties"]["regular_open_utc"],
        "session_close_time_utc": scope["calendar_policy"]["required_selected_session_properties"]["regular_close_utc"],
    }

    builder_script = feature_root / "05_STATE_BUILDER_VALIDATION" / "experimental_state_builder_probe" / "scripts" / "experimental_state_builder_probe.py"
    builder = load_builder_module(builder_script)

    daily_rows, daily_manifest = load_daily_rows(daily_root, sample_rows)
    intraday_rows, intraday_manifest = load_intraday_rows(surface_path, expected_surface_sha, sample_rows)
    source_manifests = {
        "004_master_daily_table": daily_manifest,
        "014_master_intraday_bar_table_candidate": intraday_manifest,
    }
    source_rows_read = sum(int(doc.get("rows_read", 0)) for doc in source_manifests.values())
    if source_rows_read > int(scope["limits"]["maximum_source_market_data_rows_read"]):
        raise ScaleABuilderError("Source row read limit exceeded")

    daily_by_key, daily_by_ticker, daily_findings = builder.prepare_core_daily_rows(daily_rows)
    bars_by_session, conflict_by_key, intraday_findings = prepare_intraday_rows_preserving_surface_status(builder, intraday_rows)
    requests = build_requests(sample_rows, scope)
    sample_by_context = {str(row["sample_context_id"]): row for row in sample_rows}

    first = execute_resolution_once(builder, core_scope, scope, requests, daily_by_key, daily_by_ticker, bars_by_session, sample_by_context)
    second = execute_resolution_once(builder, core_scope, scope, requests, daily_by_key, daily_by_ticker, bars_by_session, sample_by_context)
    request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records = first
    second_records = second[-1]
    second_by_id = {record["record_id"]: record for record in second_records}
    determinism_rows: list[dict[str, Any]] = []
    for record in resolution_records:
        second_record = second_by_id.get(record["record_id"])
        match = bool(second_record and second_record.get("resolution_fingerprint") == record.get("resolution_fingerprint"))
        determinism_rows.append({
            "request_id": record["request_id"],
            "object_id": record["object_id"],
            "record_id": record["record_id"],
            "first_resolution_fingerprint": record.get("resolution_fingerprint"),
            "second_resolution_fingerprint": second_record.get("resolution_fingerprint") if second_record else "",
            "repeat_run_fingerprint_match": match,
            "determinism_status": "PASS" if match else "FAILED_NON_DETERMINISTIC",
            "severity": "INFO" if match else "FAIL",
            "finding": "repeat execution produced identical fingerprint" if match else "repeat execution produced divergent fingerprint",
        })

    preparation_findings = builder.aggregate_core_preparation_findings(daily_findings + intraday_findings)
    for finding in preparation_findings:
        if finding.get("severity") == "FAIL":
            restriction_rows.append({
                "request_id": "preparation",
                "object_id": "core_four",
                "restriction_type": str(finding.get("finding_type")),
                "restriction": str(finding.get("finding")),
                "severity": str(finding.get("severity")),
                "finding": canonical_json({"count": finding.get("count"), "evidence_examples": finding.get("evidence_examples", [])}, ensure_ascii=False),
            })

    context_rows, context_counts = build_context_summary(resolution_records, sample_rows)
    summary = build_summary(
        run_id=run_id,
        scope=scope,
        sample_rows=sample_rows,
        records=resolution_records,
        formula_rows=formula_rows,
        output_contract_rows=output_contract_rows,
        determinism_rows=determinism_rows,
        restriction_rows=restriction_rows,
        duplicate_rows=duplicate_rows,
        cutoff_rows=cutoff_rows,
        source_manifests=source_manifests,
        context_counts=context_counts,
    )

    write_csv_rows(run_dir / "builder_request_report.csv", [
        "request_id", "context_id", "object_id", "instrument_id", "ticker", "session_date",
        "decision_case", "decision_timestamp_utc", "resolution_status", "resolution_fingerprint",
        "capabilities_requested", "capabilities_resolved", "restrictions_count",
    ], request_rows)
    write_csv_rows(run_dir / "capability_resolution_report.csv", [
        "request_id", "object_id", "capability_id", "source_alias", "input_fields", "formula_id",
        "resolution_rule", "resolution_status", "restriction", "finding",
    ], capability_rows)
    write_csv_rows(run_dir / "selected_source_rows_report.csv", [
        "request_id", "object_id", "source_alias", "input_role", "source_file_path",
        "source_row_ordinal_in_file", "selected_source_timestamp_utc", "session_date",
        "source_row_count", "selection_rule", "selection_status", "evidence",
    ], selected_rows)
    write_csv_rows(run_dir / "cutoff_enforcement_report.csv", [
        "request_id", "object_id", "source_alias", "input_role", "source_timestamp_utc",
        "availability_timestamp_utc", "decision_timestamp_utc", "eligible_at_decision",
        "future_leak", "cutoff_status", "finding",
    ], cutoff_rows)
    write_csv_rows(run_dir / "duplicate_handling_report.csv", [
        "request_id", "object_id", "source_alias", "selected_bar_end_utc", "duplicate_group_key",
        "duplicate_group_row_count", "duplicate_group_distinct_state_count", "duplicate_handling_status",
        "severity", "finding",
    ], duplicate_rows)
    write_csv_rows(run_dir / "formula_validation_report.csv", [
        "request_id", "object_id", "capability_id", "formula_id", "input_fields", "formula_status",
        "output_field", "output_value", "severity", "finding", "restriction",
    ], formula_rows)
    write_csv_rows(run_dir / "builder_output_contract_report.csv", [
        "request_id", "object_id", "required_schema_fields_present", "output_namespace",
        "namespace_fields_valid", "required_capabilities", "value_fields_produced",
        "missing_required_value_fields", "output_contract_status", "severity", "finding",
    ], output_contract_rows)
    write_csv_rows(run_dir / "determinism_report.csv", [
        "request_id", "object_id", "record_id", "first_resolution_fingerprint",
        "second_resolution_fingerprint", "repeat_run_fingerprint_match", "determinism_status",
        "severity", "finding",
    ], determinism_rows)
    write_csv_rows(run_dir / "builder_restrictions_report.csv", [
        "request_id", "object_id", "restriction_type", "restriction", "severity", "finding",
    ], restriction_rows)
    write_jsonl(run_dir / "core_four_resolution_records.jsonl", resolution_records)
    write_json(run_dir / "core_four_builder_validation_summary.json", summary)
    write_readout(run_dir / "readout.md", summary, run_dir)

    root_readout = integration_root / "experimental_core_four_market_state_scale_a_builder_resolution_execution_readout_v0_1.md"
    write_readout(root_readout, summary, run_dir)

    required_outputs = scope["required_outputs_by_stage"]["scale_a_builder_resolution_execution"]
    missing_outputs = [name for name in required_outputs if name != "final_manifest.json" and not (run_dir / name).exists()]
    if missing_outputs:
        raise ScaleABuilderError(f"Missing required outputs: {missing_outputs}")

    completed_at = utc_now()
    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "status": summary["builder_resolution_execution_status"],
        "summary": summary,
        "source_manifests": source_manifests,
        "preparation_findings": preparation_findings,
        "conflicting_intraday_duplicate_keys": conflict_by_key,
        "input_artifacts": {
            "scope": source_path_report(scope_path),
            "sample_manifest": source_path_report(sample_path),
            "accepted_014_surface": source_path_report(surface_path),
            "core_four_builder_scope": source_path_report(core_scope_path),
            "source_binding_registry": source_path_report(registry_path),
        },
        "artifacts": artifact_report(run_dir, required_outputs),
        "versioned_readout": str(root_readout),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "pyarrow": getattr(pq, "__version__", "unknown"),
        },
        "git": git_info(repo_root),
        "authority": {
            "sample_reselected": False,
            "sample_manifest_mutated": False,
            "013_upstream_read_allowed": False,
            "013_upstream_rows_read": 0,
            "raw_quotes_rows_read": 0,
            "market_state_integration_executed": False,
            "candidate_parquet_files_written": 0,
            "official_market_state_allowed": False,
            "production_builder_allowed": False,
            "downstream_consumption_allowed": False,
            "dataset_promotion_allowed": False,
            "full_history_execution_allowed": False,
            "full_universe_execution_allowed": False,
        },
        "next_allowed_gate": summary["next_allowed_gate"],
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": summary["builder_resolution_execution_status"], "updated_at_utc": completed_at})

    print(json.dumps(json_safe_value(summary), indent=2, ensure_ascii=False))
    return 0 if summary["hard_validation_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())


