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


SCRIPT_VERSION = "experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1"
RUN_ID_PREFIX = "experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_c_builder_resolution_execution_scope_v0_1.json"
)
OBJECT_ORDER = [
    "price_location_structure",
    "price_movement",
    "trading_activity",
    "volatility_range_state",
]
PASS_STATUSES = {"PASS", "PASS_WITH_RESTRICTIONS"}


class ScaleBBuilderError(RuntimeError):
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
                raise ScaleBBuilderError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
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
        raise ScaleBBuilderError(f"Cannot load builder module from {script_path}")
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
    for key in [
        "scale_c_builder_resolution_execution_authorized",
        "experimental_resolution_records_allowed",
        "experimental_formula_execution_allowed",
        "bounded_sample_data_read_allowed",
        "accepted_surface_read_allowed",
        "daily_004_read_allowed",
        "governed_calendar_read_allowed",
        "builder_resolution_execution_allowed_for_scale_c",
    ]:
        if authority.get(key) is not True:
            raise ScaleBBuilderError(f"Authority violation: {key} must be true")
    for key in [
        "market_state_integration_allowed_for_scale_c",
        "candidate_materialization_allowed_for_scale_c",
        "candidate_physical_validation_allowed_for_scale_c",
        "candidate_parquet_output_allowed_for_scale_c",
        "sample_reselection_allowed",
        "sample_manifest_mutation_allowed",
        "surface_rebuild_allowed",
        "013_direct_builder_reads_allowed",
        "013_upstream_read_allowed",
        "raw_quotes_read_allowed",
        "fixed_utc_probe_calendar_fallback_allowed",
        "quote_dependent_object_integration_allowed",
        "official_market_state_allowed",
        "official_state_table_write_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
    ]:
        if authority.get(key) is not False:
            raise ScaleBBuilderError(f"Authority violation: {key} must be false")
    forbidden = set(scope.get("source_aliases_forbidden", []))
    for alias in ["013_ohlcv_1m_quote_guarded", "surface_reconstruction_from_013", "fixed_utc_probe_calendar_v0_1_as_authority"]:
        if alias not in forbidden:
            raise ScaleBBuilderError(f"Forbidden source/boundary missing from scope: {alias}")
    if set(scope.get("source_aliases_allowed", [])) != {"004_master_daily_table", "014_master_intraday_bar_table_candidate"}:
        raise ScaleBBuilderError("Scale C builder must allow only 004 and accepted 014 aliases")
    override = scope.get("source_overrides", {}).get("014_master_intraday_bar_table_candidate", {})
    if override.get("accepted_surface_only") is not True:
        raise ScaleBBuilderError("014 override must require accepted_surface_only=true")
    if override.get("surface_rebuild_allowed") is not False or override.get("direct_013_read_allowed") is not False:
        raise ScaleBBuilderError("014 override must forbid surface rebuilds and direct 013 reads")
    if scope.get("calendar_policy", {}).get("fixed_utc_probe_calendar_as_current_authority_allowed") is not False:
        raise ScaleBBuilderError("Fixed UTC probe calendar must not be current authority in Scale C")



def load_sample(sample_path: Path, scope: dict[str, Any]) -> list[dict[str, Any]]:
    rows = read_jsonl(sample_path)
    expected_rows = int(scope["limits"]["requested_contexts"])
    if len(rows) != expected_rows:
        raise ScaleBBuilderError(f"Sample row count mismatch: expected={expected_rows} observed={len(rows)}")
    observed_fp = sha256_payload(rows)
    expected_fp = scope["input_artifacts"]["frozen_sample"]["scale_c_sample_fingerprint"]
    chain_fp = scope["execution_chain"]["sample_fingerprint_must_match"]
    invariant_fp = scope["identity_invariants"]["sample_fingerprint_must_match"]
    if observed_fp != expected_fp or observed_fp != chain_fp or observed_fp != invariant_fp:
        raise ScaleBBuilderError(f"Scale C sample fingerprint mismatch: observed={observed_fp}")
    duplicate_ids = [key for key, count in Counter(row["sample_context_id"] for row in rows).items() if count > 1]
    if duplicate_ids:
        raise ScaleBBuilderError(f"Duplicate sample_context_id values: {duplicate_ids[:5]}")
    if any(row.get("fixed_utc_probe_calendar_as_current_authority") is not False for row in rows):
        raise ScaleBBuilderError("Frozen Scale C sample admits fixed UTC probe calendar authority")
    observed_blocked = sum(1 for row in rows if row.get("expected_context_outcome") == "REJECTED_REQUIRED_OBJECT_BLOCKED")
    if observed_blocked != int(scope["limits"]["expected_blocked_contexts"]):
        raise ScaleBBuilderError(f"Blocked context expectation mismatch in sample: observed={observed_blocked}")
    return rows


def source_path_report(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def load_daily_rows(daily_root: Path, sample_rows: list[dict[str, Any]], allowed_years: set[int]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tickers = sorted({str(row["ticker"]).upper() for row in sample_rows})
    sample_years = {parse_date(row["session_date"]).year for row in sample_rows}
    years = sorted(sample_years | {year - 1 for year in sample_years})
    if not set(years) <= set(allowed_years):
        raise ScaleBBuilderError(f"004 daily loader requested years outside scope: requested={years} allowed={sorted(allowed_years)}")
    selected_rows: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    columns = ["instrument_id", "ticker", "session_date", "open", "prior_close", "volume"]
    for year in years:
        pattern_root = daily_root / f"year={year}" / "price_view=split_normalized"
        parquet_files = sorted(pattern_root.glob("*.parquet"))
        if not parquet_files:
            raise ScaleBBuilderError(f"No 004 daily files found under {pattern_root}")
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
        "row_read_mode": "selected_tickers_from_authorized_sample_year_and_prior_year_price_view_partitions_for_prior_20",
        "tickers": tickers,
        "years": years,
        "price_view": "split_normalized",
    }
    return selected_rows, manifest



def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def load_calendar_rows(calendar_path: Path, expected_sha256: str, sample_rows: list[dict[str, Any]], scope: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    observed_sha = sha256_file(calendar_path)
    if observed_sha != expected_sha256:
        raise ScaleBBuilderError(f"Calendar bound parquet sha256 mismatch: expected={expected_sha256} observed={observed_sha}")
    sessions = sorted({str(row["session_date"]) for row in sample_rows})
    info = scope["input_artifacts"]["accepted_calendar_binding"]
    columns = ["calendar_id", "exchange_calendar_code", "mic_or_exchange_code", "session_date", "session_open_utc", "session_close_utc", "session_open_local", "session_close_local", "timezone", "session_minutes", "session_type", "is_regular_session", "is_early_close", "is_closed_or_holiday", "calendar_version", "source_snapshot_fingerprint", "calendar_row_fingerprint"]
    frame = pq.read_table(calendar_path, columns=columns, filters=[("session_date", "in", sessions)]).to_pandas()
    frame["session_date"] = frame["session_date"].astype(str)
    by_session: dict[str, dict[str, Any]] = {}
    for session_date in sessions:
        matches = frame[frame["session_date"] == session_date]
        if len(matches) != 1:
            raise ScaleBBuilderError(f"Calendar binding cardinality failure for {session_date}: observed={len(matches)}")
        row = {col: json_safe_value(matches.iloc[0][col]) for col in columns}
        if row.get("calendar_version") != info["calendar_version"]:
            raise ScaleBBuilderError(f"Calendar version mismatch for {session_date}: {row.get('calendar_version')}")
        if row.get("source_snapshot_fingerprint") != info["calendar_source_snapshot_fingerprint"]:
            raise ScaleBBuilderError(f"Calendar source snapshot fingerprint mismatch for {session_date}")
        if str(row.get("mic_or_exchange_code")) != info.get("exchange") or str(row.get("timezone")) != info.get("timezone"):
            raise ScaleBBuilderError(f"Calendar exchange/timezone mismatch for {session_date}")
        if bool_value(row.get("is_closed_or_holiday")):
            raise ScaleBBuilderError(f"Scale C sample selected a closed/holiday calendar row: {session_date}")
        row["session_open_utc_dt"] = parse_utc_datetime(row["session_open_utc"])
        row["session_close_utc_dt"] = parse_utc_datetime(row["session_close_utc"])
        row["is_early_close"] = bool_value(row.get("is_early_close"))
        by_session[session_date] = row
    return by_session, {"source_alias": "governed_exchange_session_calendar_bound_v0_1", "path": str(calendar_path), "sha256": observed_sha, "bytes": calendar_path.stat().st_size, "rows_observed_in_calendar_artifact": int(pq.ParquetFile(calendar_path).metadata.num_rows), "rows_bound_to_scale_c_sample_sessions": len(by_session), "sessions": sessions, "calendar_version": info["calendar_version"], "calendar_source_snapshot_fingerprint": info["calendar_source_snapshot_fingerprint"], "row_read_mode": "governed_calendar_rows_filtered_to_frozen_scale_c_sessions"}


def validate_accepted_surface_manifest(surface_manifest_path: Path, final_manifest_path: Path, expected_fingerprint: str, expected_sha256: str) -> dict[str, Any]:
    surface_manifest = read_json(surface_manifest_path)
    final_manifest = read_json(final_manifest_path)
    if surface_manifest.get("scale_c_execution_surface_fingerprint") != expected_fingerprint or surface_manifest.get("parquet_sha256") != expected_sha256:
        raise ScaleBBuilderError("Surface manifest fingerprint or sha256 mismatch")
    if final_manifest.get("status") != "CLOSED_PASS_WITH_RESTRICTIONS":
        raise ScaleBBuilderError(f"Accepted surface final manifest status is not closed pass: {final_manifest.get('status')}")
    summary = final_manifest.get("summary", {})
    if summary.get("scale_c_execution_surface_fingerprint") != expected_fingerprint:
        raise ScaleBBuilderError("Surface final manifest summary fingerprint mismatch")
    if int(summary.get("builder_records_emitted", -1)) != 0 or int(summary.get("market_state_records_emitted", -1)) != 0 or summary.get("013_direct_builder_input") is not False:
        raise ScaleBBuilderError("Accepted surface manifest violates builder boundary")
    return {"surface_manifest": surface_manifest, "surface_final_summary": summary}


def load_intraday_rows(surface_path: Path, expected_sha256: str, expected_surface_fingerprint: str, surface_manifest_path: Path, final_manifest_path: Path, sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    observed_sha = sha256_file(surface_path)
    if observed_sha != expected_sha256:
        raise ScaleBBuilderError(f"Accepted Scale C 014 surface sha256 mismatch: expected={expected_sha256} observed={observed_sha}")
    manifest_evidence = validate_accepted_surface_manifest(surface_manifest_path, final_manifest_path, expected_surface_fingerprint, expected_sha256)
    metadata = pq.ParquetFile(surface_path).metadata
    tickers = sorted({str(row["ticker"]).upper() for row in sample_rows})
    sessions = sorted({str(row["session_date"]) for row in sample_rows})
    frame = pq.read_table(surface_path, filters=[("ticker", "in", tickers), ("session_date", "in", sessions)]).to_pandas()
    frame["__derived_row_ordinal_in_file"] = range(len(frame))
    frame["ticker"] = frame["ticker"].astype(str).str.upper()
    frame["session_date"] = frame["session_date"].astype(str)
    columns = ["ticker", "instrument_id", "session_date", "ts_utc", "bar_end_utc", "open", "high", "low", "close", "volume", "vwap", "transaction_count", "duplicate_status", "source_alias", "source_file", "source_row_ordinal", "source_snapshot_fingerprint", "upstream_source_alias", "upstream_source_file", "upstream_source_row_ordinal", "bar_size", "price_view", "selection_reason", "calendar_version", "calendar_row_fingerprint", "session_open_utc", "session_close_utc", "session_type", "is_early_close", "sample_context_ids_for_ticker_session"]
    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        values = {col: json_safe_value(row[col]) for col in columns if col in frame.columns}
        values["ts_utc"] = values.get("bar_end_utc") or values.get("ts_utc")
        rows.append({"file_path": str(surface_path), "row_ordinal_in_file": int(row["__derived_row_ordinal_in_file"]), "values": values})
    manifest = {"source_alias": "014_master_intraday_bar_table_candidate", "path": str(surface_path), "sha256": observed_sha, "bytes": surface_path.stat().st_size, "scale_c_execution_surface_fingerprint": expected_surface_fingerprint, "source_rows_observed": int(metadata.num_rows), "rows_read": len(rows), "row_read_mode": "accepted_run_local_014_derived_scale_c_execution_surface_filtered_to_frozen_sample", "tickers": tickers, "sessions": sessions, "surface_semantics": "run_local_014_derived_execution_surface_candidate_not_official_not_promoted", "manifest_evidence": manifest_evidence}
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
            "calendar_version": values.get("calendar_version"),
            "calendar_row_fingerprint": values.get("calendar_row_fingerprint"),
            "session_open_utc": parse_utc_datetime(values.get("session_open_utc")),
            "session_close_utc": parse_utc_datetime(values.get("session_close_utc")),
            "session_type": values.get("session_type"),
            "is_early_close": bool_value(values.get("is_early_close")),
            "upstream_source_alias": values.get("upstream_source_alias"),
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



def build_requests(sample_rows: list[dict[str, Any]], scope: dict[str, Any], calendar_by_session: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    objects_per_context = int(scope["limits"]["required_objects_per_context"])
    if len(OBJECT_ORDER) != objects_per_context:
        raise ScaleBBuilderError("Object order does not match required_objects_per_context")
    if list(scope.get("required_object_ids", [])) != OBJECT_ORDER:
        raise ScaleBBuilderError("Scope required_object_ids do not match executable object order")
    requests: list[dict[str, Any]] = []
    for context_index, sample in enumerate(sample_rows, start=1):
        context_id = str(sample["sample_context_id"])
        session_date_raw = str(sample["session_date"])
        session_date = parse_date(session_date_raw)
        calendar = calendar_by_session[session_date_raw]
        if sample.get("calendar_id") != calendar.get("calendar_id") or sample.get("calendar_version") != calendar.get("calendar_version"):
            raise ScaleBBuilderError(f"Sample/calendar identity mismatch for {context_id}")
        decision_timestamp = parse_utc_datetime(sample["decision_timestamp_utc"])
        for object_id in OBJECT_ORDER:
            requests.append({
                "request_id": f"scale_c_req_{len(requests) + 1:04d}",
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
                "calendar_id": calendar.get("calendar_id"),
                "calendar_version": calendar.get("calendar_version"),
                "calendar_row_fingerprint": calendar.get("calendar_row_fingerprint"),
                "session_open_utc": calendar["session_open_utc_dt"],
                "session_close_utc": calendar["session_close_utc_dt"],
                "session_type": calendar.get("session_type"),
                "is_early_close": calendar.get("is_early_close"),
            })
    expected = int(scope["limits"]["expected_resolution_records"])
    if len(requests) != expected:
        raise ScaleBBuilderError(f"Resolution request count mismatch: expected={expected} observed={len(requests)}")
    return requests


def install_calendar_aware_context_selector(builder: Any) -> None:
    def selected_input_context(request: dict[str, Any], scope_doc: dict[str, Any], daily_by_key: dict[tuple[str, date], dict[str, Any]], daily_by_ticker: dict[str, list[dict[str, Any]]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]]) -> dict[str, Any]:
        ticker = str(request["ticker"])
        session_date = request["session_date"]
        decision_timestamp = request["decision_timestamp_utc"]
        session_open = request.get("session_open_utc")
        session_close = request.get("session_close_utc")
        if not isinstance(session_open, datetime):
            session_open = parse_utc_datetime(session_open)
        if not isinstance(session_close, datetime):
            session_close = parse_utc_datetime(session_close)
        bars_all = bars_by_session.get((ticker, session_date), [])
        bars = [bar for bar in bars_all if session_open <= bar["bar_end_utc"] <= session_close]
        closed_bars = [bar for bar in bars if bar["bar_end_utc"] <= decision_timestamp]
        selected_bar = closed_bars[-1] if closed_bars else None
        daily_row = daily_by_key.get((ticker, session_date))
        history_20 = builder.prior_daily_rows(daily_by_ticker, ticker, session_date, 20)
        return {"ticker": ticker, "session_date": session_date, "decision_timestamp_utc": decision_timestamp, "session_open_utc": session_open, "session_close_utc": session_close, "daily_row": daily_row, "history_20": history_20, "bars": bars, "closed_bars": closed_bars, "selected_bar": selected_bar, "decision_after_session_open": decision_timestamp >= session_open}
    builder.selected_input_context = selected_input_context



def scale_c_restrictions_for_record(record: dict[str, Any], sample_by_context: dict[str, dict[str, Any]]) -> list[str]:
    sample = sample_by_context.get(str(record.get("context_id")), {})
    restrictions = [
        "candidate_artifacts_remain_non_canonical",
        "accepted_surface_is_run_local_not_official_014",
        "fixed_utc_probe_calendar_not_used_as_current_authority",
        "013_may_appear_only_as_surface_lineage_not_builder_input",
        "quote_dependent_objects_remain_excluded",
    ]
    if sample.get("decision_case") == "before_first_observable_bar_governed_session":
        restrictions.append("pre_bar_current_session_values_remain_blocked")
    if sample.get("decision_case") == "after_last_sampled_bar_not_session_close":
        restrictions.append("after_last_sampled_bar_is_not_end_of_session")
    if sample.get("early_close") is True:
        restrictions.append("governed_early_close_boundary_preserved")
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



def enrich_outputs(builder: Any, outputs: tuple[list[dict[str, Any]], ...], sample_by_context: dict[str, dict[str, Any]], calendar_by_session: dict[str, dict[str, Any]], scale_scope: dict[str, Any]) -> tuple[list[dict[str, Any]], ...]:
    request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records = outputs
    records_by_request = {record["request_id"]: record for record in resolution_records}
    new_restriction_rows: list[dict[str, Any]] = []
    surface_info = scale_scope["input_artifacts"]["accepted_execution_surface"]
    calendar_info = scale_scope["input_artifacts"]["accepted_calendar_binding"]
    sample_info = scale_scope["input_artifacts"]["frozen_sample"]
    for record in resolution_records:
        sample_by_context[str(record.get("context_id"))]
        calendar = calendar_by_session[str(record["session_date"])]
        record_restrictions = list(record.get("restrictions") or [])
        for restriction in scale_c_restrictions_for_record(record, sample_by_context):
            if restriction not in record_restrictions:
                record_restrictions.append(restriction)
                new_restriction_rows.append({"request_id": record["request_id"], "object_id": record["object_id"], "restriction_type": "scale_c_execution_restriction", "restriction": restriction, "severity": "WARN", "finding": "Scale C builder/resolution restriction preserved on the object record"})
        if record.get("resolution_status") == "PASS" and record_restrictions:
            record["resolution_status"] = "PASS_WITH_RESTRICTIONS"
        temporal_lineage = {
            "calendar_id": calendar.get("calendar_id"),
            "calendar_version": calendar.get("calendar_version"),
            "calendar_row_fingerprint": calendar.get("calendar_row_fingerprint"),
            "session_open_utc": calendar["session_open_utc_dt"].isoformat().replace("+00:00", "Z"),
            "session_close_utc": calendar["session_close_utc_dt"].isoformat().replace("+00:00", "Z"),
            "session_type": calendar.get("session_type"),
            "is_early_close": calendar.get("is_early_close"),
        }
        for key, value in temporal_lineage.items():
            record[key] = value
        source_evidence = dict(record.get("source_evidence") or {})
        source_evidence["governed_calendar_binding"] = temporal_lineage
        record["source_evidence"] = source_evidence
        cutoff_evidence = dict(record.get("cutoff_evidence") or {})
        selected_bar = (source_evidence.get("014_selected_closed_bar") or {})
        selected_end = selected_bar.get("bar_end_utc")
        selected_dt = parse_utc_datetime(selected_end) if selected_end else None
        cutoff_evidence["governed_session_close_utc"] = temporal_lineage["session_close_utc"]
        cutoff_evidence["bar_end_lte_governed_session_close"] = bool(selected_dt is not None and selected_dt <= calendar["session_close_utc_dt"]) if selected_dt else None
        cutoff_evidence["fixed_utc_probe_calendar_fallback_used"] = False
        record["cutoff_evidence"] = cutoff_evidence
        lineage = dict(record.get("lineage") or {})
        lineage["source_scope_id"] = SCRIPT_VERSION
        lineage["scale_c_builder_resolution_scope_id"] = scale_scope.get("scope_id")
        lineage["frozen_sample_fingerprint"] = sample_info["scale_c_sample_fingerprint"]
        lineage["scale_c_sample_fingerprint"] = sample_info["scale_c_sample_fingerprint"]
        lineage["scale_c_execution_surface_fingerprint"] = surface_info["scale_c_execution_surface_fingerprint"]
        lineage["bounded_014_candidate_surface_sha256"] = surface_info["bounded_014_candidate_surface_parquet_sha256"]
        lineage["calendar_binding_run_id"] = calendar_info["calendar_binding_run_id"]
        lineage["calendar_source_snapshot_fingerprint"] = calendar_info["calendar_source_snapshot_fingerprint"]
        lineage["temporal_lineage"] = temporal_lineage
        record["lineage"] = lineage
        record["restrictions"] = sorted(set(record_restrictions))
        record["resolution_fingerprint"] = recompute_record_fingerprint(builder, record)
    restriction_rows.extend(new_restriction_rows)
    for row in request_rows:
        record = records_by_request[row["request_id"]]
        row["resolution_status"] = record["resolution_status"]
        row["resolution_fingerprint"] = record["resolution_fingerprint"]
        row["restrictions_count"] = len(record.get("restrictions") or [])
        for field in ["calendar_id", "calendar_version", "calendar_row_fingerprint", "session_open_utc", "session_close_utc", "session_type", "is_early_close"]:
            row[field] = record.get(field)
    return request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records



def execute_resolution_once(builder: Any, core_scope: dict[str, Any], scale_scope: dict[str, Any], requests: list[dict[str, Any]], daily_by_key: dict[tuple[str, date], dict[str, Any]], daily_by_ticker: dict[str, list[dict[str, Any]]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]], sample_by_context: dict[str, dict[str, Any]], calendar_by_session: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], ...]:
    outputs = builder.execute_core_four_resolution_pass(core_scope, requests, daily_by_key, daily_by_ticker, bars_by_session)
    return enrich_outputs(builder, outputs, sample_by_context, calendar_by_session, scale_scope)



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
        context_fingerprint_payload = {"context_id": context_id, "instrument_id": representative.get("instrument_id"), "ticker": representative.get("ticker"), "session_date": representative.get("session_date"), "decision_timestamp_utc": representative.get("decision_timestamp_utc"), "decision_case": representative.get("decision_case"), "calendar_row_fingerprint": representative.get("calendar_row_fingerprint"), "object_record_ids": {row["object_id"]: row.get("record_id") for row in context_records}, "resolution_fingerprints": {row["object_id"]: row.get("resolution_fingerprint") for row in context_records}}
        context_rows.append({
            "context_id": context_id,
            "ticker": representative.get("ticker"),
            "instrument_id": representative.get("instrument_id"),
            "session_date": representative.get("session_date"),
            "decision_case": representative.get("decision_case"),
            "decision_timestamp_utc": representative.get("decision_timestamp_utc"),
            "record_count": len(context_records),
            "object_ids": "|".join(sorted(statuses)),
            "context_resolution_status": context_status,
            "expected_context_outcome": expected_outcome_by_context.get(context_id),
            "calendar_id": representative.get("calendar_id"),
            "calendar_version": representative.get("calendar_version"),
            "calendar_row_fingerprint": representative.get("calendar_row_fingerprint"),
            "session_open_utc": representative.get("session_open_utc"),
            "session_close_utc": representative.get("session_close_utc"),
            "session_type": representative.get("session_type"),
            "is_early_close": representative.get("is_early_close"),
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


def build_calendar_binding_report(sample_rows: list[dict[str, Any]], calendar_by_session: dict[str, dict[str, Any]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    counts = Counter()
    for sample in sample_rows:
        context_id = str(sample["sample_context_id"])
        ticker = str(sample["ticker"]).upper()
        session_date_text = str(sample["session_date"])
        session_date = parse_date(session_date_text)
        calendar = calendar_by_session.get(session_date_text)
        decision_ts = parse_utc_datetime(sample["decision_timestamp_utc"])
        bars = bars_by_session.get((ticker, session_date), [])
        eligible_bars = [bar for bar in bars if calendar and bar["bar_end_utc"] <= decision_ts and bar["bar_end_utc"] <= calendar["session_close_utc_dt"]]
        selected_bar = eligible_bars[-1] if eligible_bars else None
        binding_status = "PASS" if calendar else "FAILED_CALENDAR_BINDING"
        semantic_status = "PASS"
        finding = "decision case satisfied governed calendar semantics"
        decision_case = str(sample.get("decision_case"))
        if not calendar:
            semantic_status = "FAILED_DECISION_CASE_SEMANTICS"; finding = "missing governed calendar binding"
        elif decision_case in {"before_first_observable_bar_governed_session", "historical_period_pre_open_boundary_blocked"}:
            first_bar = parse_utc_datetime(sample.get("intraday_first_bar_utc"))
            if not (decision_ts < first_bar and selected_bar is None):
                semantic_status = "FAILED_DECISION_CASE_SEMANTICS"; finding = "pre-bar context admitted current-session bar or is not before first observable bar"
        elif decision_case == "first_observable_bar_governed_session":
            if selected_bar is None or selected_bar["bar_end_utc"] > decision_ts:
                semantic_status = "FAILED_DECISION_CASE_SEMANTICS"; finding = "first-observable context did not select a closed bar at or before decision"
        elif decision_case == "after_last_sampled_bar_not_session_close":
            if sample.get("after_last_sampled_bar_semantics") != "not_session_close":
                semantic_status = "FAILED_DECISION_CASE_SEMANTICS"; finding = "after-last-sampled context missing not_session_close semantic marker"
        elif decision_case in {"governed_session_close_boundary", "governed_historical_session_close_boundary"}:
            if decision_ts != calendar["session_close_utc_dt"]:
                semantic_status = "FAILED_DECISION_CASE_SEMANTICS"; finding = "session close boundary context decision timestamp differs from governed close"
        else:
            semantic_status = "FAILED_DECISION_CASE_SEMANTICS"; finding = f"unsupported Scale C decision_case={decision_case}"
        early_close_status = "PASS"
        if calendar and calendar.get("is_early_close") and selected_bar and selected_bar["bar_end_utc"] > calendar["session_close_utc_dt"]:
            early_close_status = "FAILED_EARLY_CLOSE_CUTOFF"
        if binding_status != "PASS":
            counts["calendar_binding_failures"] += 1; counts["calendar_row_bindings_missing"] += 1
        if semantic_status != "PASS":
            counts["decision_case_semantic_mismatches"] += 1
        if early_close_status != "PASS":
            counts["early_close_cutoff_failures"] += 1
        rows.append({"context_id": context_id, "ticker": ticker, "session_date": session_date_text, "decision_case": decision_case, "decision_timestamp_utc": decision_ts.isoformat().replace("+00:00", "Z"), "calendar_id": calendar.get("calendar_id") if calendar else "", "calendar_version": calendar.get("calendar_version") if calendar else "", "calendar_row_fingerprint": calendar.get("calendar_row_fingerprint") if calendar else "", "session_open_utc": calendar["session_open_utc_dt"].isoformat().replace("+00:00", "Z") if calendar else "", "session_close_utc": calendar["session_close_utc_dt"].isoformat().replace("+00:00", "Z") if calendar else "", "session_type": calendar.get("session_type") if calendar else "", "is_early_close": calendar.get("is_early_close") if calendar else "", "selected_bar_end_utc": selected_bar["bar_end_utc"].isoformat().replace("+00:00", "Z") if selected_bar else "", "calendar_binding_status": binding_status, "decision_case_semantic_status": semantic_status, "early_close_cutoff_status": early_close_status, "fixed_utc_fallback_used": False, "finding": finding})
    return rows, dict(counts)


def validate_surface_calendar_boundaries(bars_by_session: dict[tuple[str, date], list[dict[str, Any]]], calendar_by_session: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for (_, session_date), bars in bars_by_session.items():
        calendar = calendar_by_session[session_date.isoformat()]
        for bar in bars:
            if bar.get("calendar_version") != calendar.get("calendar_version") or bar.get("calendar_row_fingerprint") != calendar.get("calendar_row_fingerprint"):
                counts["session_boundary_failures"] += 1
            if bar["bar_end_utc"] > calendar["session_close_utc_dt"]:
                counts["bars_beyond_governed_close_admitted"] += 1
            if bar["bar_end_utc"] < calendar["session_open_utc_dt"]:
                counts["session_boundary_failures"] += 1
            if calendar.get("is_early_close") and bar["bar_end_utc"] > calendar["session_close_utc_dt"]:
                counts["early_close_failures"] += 1
    counts["fixed_utc_fallback_uses"] = 0
    return dict(counts)



def build_summary(*, run_id: str, scope: dict[str, Any], sample_rows: list[dict[str, Any]], records: list[dict[str, Any]], formula_rows: list[dict[str, Any]], output_contract_rows: list[dict[str, Any]], determinism_rows: list[dict[str, Any]], restriction_rows: list[dict[str, Any]], duplicate_rows: list[dict[str, Any]], cutoff_rows: list[dict[str, Any]], source_manifests: dict[str, Any], context_counts: dict[str, int], calendar_report_rows: list[dict[str, Any]], calendar_counts: dict[str, int], surface_boundary_counts: dict[str, int]) -> dict[str, Any]:
    limits = scope["limits"]
    source_004_rows = int(source_manifests["004_master_daily_table"].get("rows_read", 0))
    source_014_rows = int(source_manifests["014_master_intraday_bar_table_candidate"].get("rows_read", 0))
    source_rows_read = source_004_rows + source_014_rows
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
    calendar_binding_failures = int(calendar_counts.get("calendar_binding_failures", 0))
    calendar_missing = int(calendar_counts.get("calendar_row_bindings_missing", 0))
    calendar_multiple = int(calendar_counts.get("calendar_row_bindings_multiple", 0))
    decision_mismatches = int(calendar_counts.get("decision_case_semantic_mismatches", 0))
    early_close_cutoff_failures = int(calendar_counts.get("early_close_cutoff_failures", 0))
    session_boundary_failures = int(surface_boundary_counts.get("session_boundary_failures", 0))
    early_close_failures = int(surface_boundary_counts.get("early_close_failures", 0))
    bars_beyond_close = int(surface_boundary_counts.get("bars_beyond_governed_close_admitted", 0))
    fixed_utc_fallback_uses = int(surface_boundary_counts.get("fixed_utc_fallback_uses", 0))
    authority_failures = sum([int(scope["authority"].get("013_direct_builder_reads_allowed") is not False), int(scope["authority"].get("surface_rebuild_allowed") is not False), int(scope["authority"].get("market_state_integration_allowed_for_scale_c") is not False), int(source_manifests["014_master_intraday_bar_table_candidate"].get("scale_c_execution_surface_fingerprint") != scope["input_artifacts"]["accepted_execution_surface"]["scale_c_execution_surface_fingerprint"])])
    hard_failures = sum([formula_failures, contract_failures, nondeterministic, future_leaks, conflict_blocks, failed_records, failed_contexts, semantic_failures, calendar_binding_failures, calendar_missing, calendar_multiple, decision_mismatches, early_close_cutoff_failures, session_boundary_failures, early_close_failures, bars_beyond_close, fixed_utc_fallback_uses, authority_failures, int(source_rows_read > int(limits["maximum_source_market_data_rows_read"])), int(source_004_rows > int(limits["maximum_source_004_rows_read"])), int(source_014_rows > int(limits["maximum_accepted_surface_rows_read"])), int(len(records) != int(limits["expected_resolution_records"])), int(blocked_contexts != int(limits["expected_blocked_contexts"])), int(integrable_contexts != int(limits["expected_integrable_contexts"]))])
    status = "FAILED" if hard_failures else "CLOSED_PASS_WITH_RESTRICTIONS"
    return {
        "run_id": run_id, "script_version": SCRIPT_VERSION, "scope_id": scope.get("scope_id"), "builder_resolution_execution_status": status,
        "sample_preflight_run_id": scope["input_artifacts"]["frozen_sample"]["preflight_run_id"], "sample_fingerprint_match": True, "surface_fingerprint_match": True, "calendar_source_snapshot_fingerprint_match": True,
        "scale_c_sample_fingerprint": scope["input_artifacts"]["frozen_sample"]["scale_c_sample_fingerprint"], "scale_c_execution_surface_fingerprint": scope["input_artifacts"]["accepted_execution_surface"]["scale_c_execution_surface_fingerprint"],
        "calendar_binding_run_id": scope["input_artifacts"]["accepted_calendar_binding"]["calendar_binding_run_id"], "calendar_version": scope["input_artifacts"]["accepted_calendar_binding"]["calendar_version"], "calendar_source_snapshot_fingerprint": scope["input_artifacts"]["accepted_calendar_binding"]["calendar_source_snapshot_fingerprint"],
        "requested_contexts": len(sample_rows), "resolution_records": len(records), "expected_resolution_records": int(limits["expected_resolution_records"]), "required_objects_per_context": int(limits["required_objects_per_context"]),
        "pass_or_pass_with_restrictions_records": pass_records, "blocked_input_unavailable_records": input_blocks, "conflicting_source_row_blocks": conflict_blocks, "failed_records": failed_records,
        "integrable_contexts": integrable_contexts, "expected_integrable_contexts": int(limits["expected_integrable_contexts"]), "blocked_contexts": blocked_contexts, "expected_blocked_contexts": int(limits["expected_blocked_contexts"]), "failed_contexts": failed_contexts,
        "source_market_data_rows_read": source_rows_read, "maximum_source_market_data_rows_read": int(limits["maximum_source_market_data_rows_read"]), "source_rows_read_mode": "004_daily_plus_accepted_run_local_014_surface_only", "source_004_rows_read": source_004_rows, "source_014_rows_read": source_014_rows, "source_013_rows_read": 0, "013_direct_builder_rows_read": 0,
        "formula_rows": len(formula_rows), "formula_failures": formula_failures, "future_bar_leaks": future_leaks, "calendar_binding_failures": calendar_binding_failures, "calendar_row_bindings_missing": calendar_missing, "calendar_row_bindings_multiple": calendar_multiple, "session_boundary_failures": session_boundary_failures, "decision_case_semantic_mismatches": decision_mismatches, "early_close_failures": early_close_failures, "early_close_cutoff_failures": early_close_cutoff_failures, "bars_beyond_governed_close_admitted": bars_beyond_close, "fixed_utc_fallback_uses": fixed_utc_fallback_uses,
        "output_contract_failures": contract_failures, "nondeterministic_records": nondeterministic, "restriction_rows": len(restriction_rows), "duplicate_report_rows": len(duplicate_rows), "duplicate_warning_rows": sum(1 for row in duplicate_rows if row.get("severity") == "WARN"), "semantic_equality_checks": semantic_checks, "semantic_equality_failures": semantic_failures, "authority_failures": authority_failures, "hard_validation_failures": hard_failures,
        "sample_reselected": False, "sample_manifest_mutated": False, "surface_rebuilt": False, "raw_quotes_rows_read": 0, "market_state_integration_executed": False, "candidate_market_state_records_emitted": 0, "candidate_parquet_files_written": 0, "market_state_parquet_files_written": 0, "official_market_state_allowed": False, "production_builder_allowed": False, "downstream_consumption_allowed": False, "dataset_promotion_allowed": False, "full_history_execution_allowed": False, "full_universe_execution_allowed": False,
        "next_allowed_gate": "experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization_v0_1",
    }



def write_readout(path: Path, summary: dict[str, Any], run_dir: Path) -> None:
    lines = [
        "# Experimental Core Four Market State Scale C Builder/Resolution Execution Readout v0.1", "",
        f"run_id: `{summary['run_id']}`", f"status: `{summary['builder_resolution_execution_status']}`", "",
        "## Scope", "",
        "This gate consumed the frozen Scale C sample, the accepted run-local Scale C execution surface, governed calendar binding, and 004 daily rows.",
        "It emitted Information Object resolution records only. It did not read 013 directly, rebuild the surface, execute Market State integration, or write candidate Market State parquet.", "",
        "## Counts", "",
        f"requested_contexts = {summary['requested_contexts']}", f"resolution_records = {summary['resolution_records']}", f"integrable_contexts = {summary['integrable_contexts']}", f"blocked_contexts = {summary['blocked_contexts']}", f"failed_contexts = {summary['failed_contexts']}", f"pass_or_pass_with_restrictions_records = {summary['pass_or_pass_with_restrictions_records']}", f"blocked_input_unavailable_records = {summary['blocked_input_unavailable_records']}", "",
        "## Bound Inputs", "",
        f"scale_c_sample_fingerprint = `{summary['scale_c_sample_fingerprint']}`", f"scale_c_execution_surface_fingerprint = `{summary['scale_c_execution_surface_fingerprint']}`", f"calendar_binding_run_id = `{summary['calendar_binding_run_id']}`", f"calendar_version = `{summary['calendar_version']}`", f"calendar_source_snapshot_fingerprint = `{summary['calendar_source_snapshot_fingerprint']}`", "",
        "## Validation", "",
        f"source_market_data_rows_read = {summary['source_market_data_rows_read']}", f"source_004_rows_read = {summary['source_004_rows_read']}", f"source_014_rows_read = {summary['source_014_rows_read']}", f"source_013_rows_read = {summary['source_013_rows_read']}", f"formula_failures = {summary['formula_failures']}", f"future_bar_leaks = {summary['future_bar_leaks']}", f"calendar_binding_failures = {summary['calendar_binding_failures']}", f"session_boundary_failures = {summary['session_boundary_failures']}", f"decision_case_semantic_mismatches = {summary['decision_case_semantic_mismatches']}", f"early_close_cutoff_failures = {summary['early_close_cutoff_failures']}", f"bars_beyond_governed_close_admitted = {summary['bars_beyond_governed_close_admitted']}", f"fixed_utc_fallback_uses = {summary['fixed_utc_fallback_uses']}", f"output_contract_failures = {summary['output_contract_failures']}", f"nondeterministic_records = {summary['nondeterministic_records']}", f"semantic_equality_failures = {summary['semantic_equality_failures']}", f"authority_failures = {summary['authority_failures']}", f"hard_validation_failures = {summary['hard_validation_failures']}", "",
        "## Restrictions Preserved", "",
        "- candidate artifacts remain non-canonical", "- accepted surface is run-local, not official 014", "- core-four profile is not complete TSIS Market State", "- fixed UTC probe calendar is not current authority", "- 013 may appear only as surface lineage, not builder input", "- pre-bar current-session values remain blocked", "- after_last_sampled_bar remains not-session-close semantics", "- quote-dependent objects remain excluded", "",
        "## Next Gate", "",
        "Allowed next: `experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization_v0_1`.",
        "Still closed: Market State integration until separate authorization, materialization, official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale C.", "",
        "## Run Directory", "", f"`{run_dir}`", "",
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
    parser = argparse.ArgumentParser(description="Execute Scale C core-four builder/resolution records from a frozen sample.")
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
    write_jsonl(run_dir / "scale_c_sample_manifest.jsonl", sample_rows)

    calendar_info = scope["input_artifacts"]["accepted_calendar_binding"]
    calendar_path = resolve_path(calendar_info["calendar_bound_parquet_path"], scope_path.parent)
    calendar_by_session, calendar_manifest = load_calendar_rows(calendar_path, calendar_info["calendar_bound_parquet_sha256"], sample_rows, scope)

    surface_info = scope["input_artifacts"]["accepted_execution_surface"]
    surface_path = resolve_path(surface_info["bounded_014_candidate_surface_path"], scope_path.parent)
    expected_surface_sha = surface_info["bounded_014_candidate_surface_parquet_sha256"]
    expected_surface_fp = surface_info["scale_c_execution_surface_fingerprint"]
    surface_manifest_path = resolve_path(surface_info["surface_manifest_path"], scope_path.parent)
    surface_final_manifest_path = resolve_path(surface_info["surface_final_manifest_path"], scope_path.parent)

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
        "maximum_sessions_per_instrument": int(scope["limits"]["session_count"]),
        "maximum_decision_timestamps_per_session": int(scope["limits"]["decision_case_family_count"]),
    }
    core_scope["request_generation"] = {
        **core_scope.get("request_generation", {}),
        "session_open_time_utc": "00:00:00",
        "session_close_time_utc": "23:59:59",
        "calendar_authority": "governed_exchange_session_calendar_bound_v0_1_per_request",
    }

    builder_script = feature_root / "05_STATE_BUILDER_VALIDATION" / "experimental_state_builder_probe" / "scripts" / "experimental_state_builder_probe.py"
    builder = load_builder_module(builder_script)
    install_calendar_aware_context_selector(builder)

    daily_allowed_years = set(int(year) for year in scope["source_overrides"]["004_master_daily_table"]["allowed_years"])
    daily_rows, daily_manifest = load_daily_rows(daily_root, sample_rows, daily_allowed_years)
    intraday_rows, intraday_manifest = load_intraday_rows(surface_path, expected_surface_sha, expected_surface_fp, surface_manifest_path, surface_final_manifest_path, sample_rows)
    source_manifests = {
        "004_master_daily_table": daily_manifest,
        "014_master_intraday_bar_table_candidate": intraday_manifest,
        "governed_exchange_session_calendar_bound_v0_1": calendar_manifest,
    }
    source_rows_read = int(daily_manifest.get("rows_read", 0)) + int(intraday_manifest.get("rows_read", 0))
    if source_rows_read > int(scope["limits"]["maximum_source_market_data_rows_read"]):
        raise ScaleBBuilderError("Source row read limit exceeded")

    daily_by_key, daily_by_ticker, daily_findings = builder.prepare_core_daily_rows(daily_rows)
    bars_by_session, conflict_by_key, intraday_findings = prepare_intraday_rows_preserving_surface_status(builder, intraday_rows)
    surface_boundary_counts = validate_surface_calendar_boundaries(bars_by_session, calendar_by_session)
    calendar_report_rows, calendar_counts = build_calendar_binding_report(sample_rows, calendar_by_session, bars_by_session)
    requests = build_requests(sample_rows, scope, calendar_by_session)
    sample_by_context = {str(row["sample_context_id"]): row for row in sample_rows}

    first = execute_resolution_once(builder, core_scope, scope, requests, daily_by_key, daily_by_ticker, bars_by_session, sample_by_context, calendar_by_session)
    second = execute_resolution_once(builder, core_scope, scope, requests, daily_by_key, daily_by_ticker, bars_by_session, sample_by_context, calendar_by_session)
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
        calendar_report_rows=calendar_report_rows,
        calendar_counts=calendar_counts,
        surface_boundary_counts=surface_boundary_counts,
    )

    write_csv_rows(run_dir / "builder_request_report.csv", [
        "request_id", "context_id", "object_id", "instrument_id", "ticker", "session_date",
        "decision_case", "decision_timestamp_utc", "calendar_id", "calendar_version",
        "calendar_row_fingerprint", "session_open_utc", "session_close_utc", "session_type",
        "is_early_close", "resolution_status", "resolution_fingerprint",
        "capabilities_requested", "capabilities_resolved", "restrictions_count",
    ], request_rows)
    write_csv_rows(run_dir / "context_resolution_summary.csv", [
        "context_id", "ticker", "instrument_id", "session_date", "decision_case", "decision_timestamp_utc",
        "record_count", "object_ids", "context_resolution_status", "expected_context_outcome",
        "calendar_id", "calendar_version", "calendar_row_fingerprint", "session_open_utc", "session_close_utc",
        "session_type", "is_early_close", "context_input_fingerprint",
    ], context_rows)
    write_csv_rows(run_dir / "capability_resolution_report.csv", [
        "request_id", "object_id", "capability_id", "source_alias", "input_fields", "formula_id",
        "resolution_rule", "resolution_status", "restriction", "finding",
    ], capability_rows)
    write_csv_rows(run_dir / "selected_source_rows_report.csv", [
        "request_id", "object_id", "source_alias", "input_role", "source_file_path",
        "source_row_ordinal_in_file", "selected_source_timestamp_utc", "session_date",
        "source_row_count", "selection_rule", "selection_status", "evidence",
    ], selected_rows)
    write_csv_rows(run_dir / "calendar_binding_report.csv", [
        "context_id", "ticker", "session_date", "decision_case", "decision_timestamp_utc",
        "calendar_id", "calendar_version", "calendar_row_fingerprint", "session_open_utc", "session_close_utc",
        "session_type", "is_early_close", "selected_bar_end_utc", "calendar_binding_status",
        "decision_case_semantic_status", "early_close_cutoff_status", "fixed_utc_fallback_used", "finding",
    ], calendar_report_rows)
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

    root_readout = integration_root / "experimental_core_four_market_state_scale_c_builder_resolution_execution_readout_v0_1.md"
    write_readout(root_readout, summary, run_dir)

    required_outputs = scope["required_outputs"]
    missing_outputs = [name for name in required_outputs if name != "final_manifest.json" and not (run_dir / name).exists()]
    if missing_outputs:
        raise ScaleBBuilderError(f"Missing required outputs: {missing_outputs}")

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
        "calendar_validation_counts": {**calendar_counts, **surface_boundary_counts},
        "input_artifacts": {
            "scope": source_path_report(scope_path),
            "sample_manifest": source_path_report(sample_path),
            "accepted_scale_c_execution_surface": source_path_report(surface_path),
            "accepted_calendar_binding": source_path_report(calendar_path),
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
            "surface_rebuilt": False,
            "013_direct_builder_reads_allowed": False,
            "013_direct_builder_rows_read": 0,
            "013_upstream_read_allowed": False,
            "raw_quotes_rows_read": 0,
            "fixed_utc_probe_calendar_fallback_used": False,
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


