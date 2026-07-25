from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


SCRIPT_VERSION = "experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1"
RUN_ID_PREFIX = "experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_c_execution_surface_construction_scope_v0_1.json"
)
SURFACE_NAME = "014_scale_c_execution_surface_candidate_v0_1.parquet"


class SurfaceConstructionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe_value(item) for item in value]
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
    except TypeError:
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


def long_path(path: Path) -> str:
    resolved = str(path.resolve())
    prefix = "\\\\?\\"
    if platform.system().lower().startswith("win") and not resolved.startswith(prefix):
        return prefix + resolved
    return resolved


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f"tmp_{os.getpid()}.txt"
    with open(long_path(tmp), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(long_path(tmp), long_path(path))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(json_safe_value(payload), indent=2, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    atomic_write_text(path, "".join(canonical_json(row, ensure_ascii=False) + "\n" for row in rows))


def serialize_cell(value: Any) -> str:
    safe = json_safe_value(value)
    if safe is None:
        return ""
    if isinstance(safe, (dict, list)):
        return canonical_json(safe, ensure_ascii=False)
    return str(safe)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f"tmp_{os.getpid()}.csv"
    with open(long_path(tmp), "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialize_cell(row.get(field)) for field in fieldnames})
    os.replace(long_path(tmp), long_path(path))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


def parse_date(value: Any) -> date:
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            raise ValueError("empty timestamp date")
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        raise ValueError("empty date")
    return date.fromisoformat(raw[:10])


def parse_utc(value: Any) -> pd.Timestamp:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"unparseable UTC timestamp: {value!r}")
    return parsed


def iso_utc(value: Any) -> str:
    return json_safe_value(parse_utc(value))


def file_doc(path: Path, *, include_hash: bool = True) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    stat = path.stat()
    payload: dict[str, Any] = {
        "path": str(path),
        "exists": True,
        "bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
    }
    if path.suffix.lower() == ".parquet":
        pf = pq.ParquetFile(path)
        payload["parquet_rows"] = int(pf.metadata.num_rows)
        payload["parquet_row_groups"] = int(pf.metadata.num_row_groups)
        payload["columns"] = list(pf.schema_arrow.names)
    if include_hash:
        payload["sha256"] = sha256_file(path)
    return payload


def validate_scope(scope: dict[str, Any]) -> None:
    if scope.get("scope_id") != "experimental_core_four_market_state_scale_c_execution_surface_construction_scope_v0_1":
        raise SurfaceConstructionError("Unexpected scope_id")
    if scope.get("mode") != "experimental_core_four_market_state_scale_c_execution_surface_construction":
        raise SurfaceConstructionError("Unexpected mode")
    authority = scope.get("authority", {})
    required_true = [
        "scale_c_execution_surface_construction_allowed",
        "013_upstream_read_allowed_for_execution_surface",
        "run_local_014_surface_creation_allowed",
    ]
    required_false = [
        "sample_reselection_allowed",
        "sample_manifest_mutation_allowed",
        "013_direct_builder_input_allowed",
        "builder_resolution_execution_allowed",
        "information_object_formula_execution_allowed",
        "market_state_integration_allowed",
        "market_state_materialization_allowed",
        "market_state_parquet_allowed",
        "raw_quotes_read_allowed",
        "quote_dependent_object_integration_allowed",
        "run_local_014_surface_promotion_allowed",
        "original_014_modification_allowed",
        "official_market_state_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
    ]
    for key in required_true:
        if authority.get(key) is not True:
            raise SurfaceConstructionError(f"Authority violation: {key} must be true")
    for key in required_false:
        if authority.get(key) is not False:
            raise SurfaceConstructionError(f"Authority violation: {key} must be false")
    allowed = set(scope.get("source_aliases_allowed", []))
    if allowed != {"013_ohlcv_1m_quote_guarded", "014_master_intraday_bar_table_candidate"}:
        raise SurfaceConstructionError(f"Unexpected allowed source aliases: {sorted(allowed)}")
    forbidden = {str(item).replace("\\", "/") for item in scope.get("source_aliases_forbidden", [])}
    if "00_CTO/99_REFERENCE_LIBRARY" not in forbidden:
        raise SurfaceConstructionError("Reference library exclusion missing")
    outputs = scope.get("required_output_files", [])
    limits = scope.get("limits", {})
    if int(limits.get("required_output_files", -1)) != len(outputs):
        raise SurfaceConstructionError("required_output_files count mismatch")
    if int(limits.get("maximum_output_files", -1)) < len(outputs):
        raise SurfaceConstructionError("maximum_output_files is lower than required outputs")


def resolve_source_roots(scope: dict[str, Any], scope_dir: Path) -> tuple[Path, dict[str, Path], dict[str, Any]]:
    registry_path = resolve_path(scope["governance_inputs"]["source_binding_registry"], scope_dir)
    registry = read_json(registry_path)
    bindings = registry.get("bindings", {})
    roots: dict[str, Path] = {}
    for alias in ["013_ohlcv_1m_quote_guarded", "014_master_intraday_bar_table_candidate"]:
        binding = bindings.get(alias)
        if not binding:
            raise SurfaceConstructionError(f"Missing source binding for {alias}")
        root = Path(str(binding.get("physical_candidate_root"))).resolve()
        root_text = str(root).replace("\\", "/")
        if "00_CTO/99_REFERENCE_LIBRARY" in root_text:
            raise SurfaceConstructionError(f"Forbidden reference library path resolved for {alias}: {root}")
        if not root.exists():
            raise SurfaceConstructionError(f"Resolved source root does not exist for {alias}: {root}")
        roots[alias] = root
    return registry_path, roots, registry


def load_sample(scope: dict[str, Any], scope_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sample_info = scope["input_artifacts"]["frozen_sample"]
    sample_path = resolve_path(sample_info["sample_manifest_path"], scope_dir)
    rows = read_jsonl(sample_path)
    observed_fp = sha256_payload(rows)
    expected_fp = sample_info["scale_c_sample_fingerprint"]
    duplicate_ids = [key for key, count in Counter(row["sample_context_id"] for row in rows).items() if count > 1]
    if duplicate_ids:
        raise SurfaceConstructionError(f"Duplicate sample_context_id values: {duplicate_ids[:5]}")
    if len(rows) != int(sample_info["sample_manifest_rows"]):
        raise SurfaceConstructionError(f"Sample row count mismatch: observed={len(rows)}")
    if observed_fp != expected_fp:
        raise SurfaceConstructionError(f"Sample fingerprint mismatch: observed={observed_fp}")
    tickers = sorted({str(row["ticker"]).upper() for row in rows})
    sessions = sorted({str(row["session_date"]) for row in rows})
    if len(tickers) != int(sample_info["selected_instruments"]):
        raise SurfaceConstructionError("Selected instrument count mismatch")
    if len(sessions) != int(sample_info["selected_sessions"]):
        raise SurfaceConstructionError("Selected session count mismatch")
    return rows, {
        "sample_manifest_path": str(sample_path),
        "sample_manifest_rows": len(rows),
        "scale_c_sample_fingerprint": observed_fp,
        "tickers": tickers,
        "sessions": sessions,
    }


def load_calendar(scope: dict[str, Any], scope_dir: Path, sessions: list[str]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    cal_info = scope["input_artifacts"]["governed_calendar_binding"]
    calendar_path = resolve_path(cal_info["bound_calendar_path"], scope_dir)
    calendar_doc = file_doc(calendar_path, include_hash=True)
    table = pq.read_table(calendar_path, filters=[("session_date", "in", sessions)])
    df = table.to_pandas()
    rows_by_date: dict[str, dict[str, Any]] = {}
    report_rows: list[dict[str, Any]] = []
    binding_failures = 0
    for session in sessions:
        matched = df[df["session_date"].astype(str) == session].copy()
        finding = "PASS"
        if len(matched) != 1:
            binding_failures += 1
            finding = "FAIL_EXACTLY_ONE_CALENDAR_ROW"
            report_rows.append(
                {
                    "session_date": session,
                    "matched_rows": int(len(matched)),
                    "finding": finding,
                }
            )
            continue
        row = {column: json_safe_value(matched.iloc[0][column]) for column in matched.columns}
        try:
            open_utc = parse_utc(row["session_open_utc"])
            close_utc = parse_utc(row["session_close_utc"])
        except ValueError:
            binding_failures += 1
            finding = "FAIL_TEMPORAL_PARSE"
            open_utc = pd.NaT
            close_utc = pd.NaT
        if row.get("calendar_version") != cal_info["calendar_version"]:
            binding_failures += 1
            finding = "FAIL_CALENDAR_VERSION"
        if row.get("source_snapshot_fingerprint") != cal_info["source_snapshot_fingerprint"]:
            binding_failures += 1
            finding = "FAIL_SOURCE_SNAPSHOT_FINGERPRINT"
        row["_session_open_utc_ts"] = open_utc
        row["_session_close_utc_ts"] = close_utc
        rows_by_date[session] = row
        report_rows.append(
            {
                "session_date": session,
                "matched_rows": 1,
                "calendar_id": row.get("calendar_id"),
                "calendar_version": row.get("calendar_version"),
                "session_open_utc": row.get("session_open_utc"),
                "session_close_utc": row.get("session_close_utc"),
                "session_type": row.get("session_type"),
                "is_early_close": row.get("is_early_close"),
                "is_closed_or_holiday": row.get("is_closed_or_holiday"),
                "calendar_row_fingerprint": row.get("calendar_row_fingerprint"),
                "source_snapshot_fingerprint": row.get("source_snapshot_fingerprint"),
                "finding": finding,
            }
        )
    selected_payload = [
        {
            key: value
            for key, value in rows_by_date[session].items()
            if not key.startswith("_")
        }
        for session in sorted(rows_by_date)
    ]
    calendar_selection_fingerprint = sha256_payload(selected_payload)
    manifest = {
        "calendar_path": str(calendar_path),
        "calendar_file_doc": calendar_doc,
        "sessions_requested": sessions,
        "sessions_bound": sorted(rows_by_date),
        "binding_failures": binding_failures,
        "calendar_selection_fingerprint": calendar_selection_fingerprint,
        "calendar_source_snapshot_fingerprint": cal_info["source_snapshot_fingerprint"],
    }
    return rows_by_date, report_rows, manifest


def discover_013_files(root: Path, sample_rows: list[dict[str, Any]]) -> tuple[list[Path], list[dict[str, Any]]]:
    groups = sorted(
        {
            (
                str(row["ticker"]).upper(),
                parse_date(row["session_date"]).year,
                parse_date(row["session_date"]).month,
            )
            for row in sample_rows
        }
    )
    files: list[Path] = []
    missing: list[dict[str, Any]] = []
    for ticker, year, month in groups:
        month_dir = root / f"year={year}" / f"ticker={ticker}" / f"month={month:02d}"
        month_files = sorted(month_dir.glob("*.parquet")) if month_dir.exists() else []
        if not month_files:
            missing.append({"ticker": ticker, "year": year, "month": month, "path": str(month_dir)})
            continue
        files.extend(month_files)
    return sorted(set(files)), missing


def load_013_rows(
    files: list[Path],
    sample_rows: list[dict[str, Any]],
    calendar: dict[str, dict[str, Any]],
) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
    selected_tickers = sorted({str(row["ticker"]).upper() for row in sample_rows})
    selected_sessions = sorted({str(row["session_date"]) for row in sample_rows})
    selected_dates_by_ticker = defaultdict(set)
    for row in sample_rows:
        selected_dates_by_ticker[str(row["ticker"]).upper()].add(str(row["session_date"]))

    columns = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v", "vw", "n"]
    frames: list[pd.DataFrame] = []
    file_docs: list[dict[str, Any]] = []
    rows_read = 0
    for path in files:
        doc = file_doc(path, include_hash=True)
        file_docs.append(doc)
        pf = pq.ParquetFile(path)
        missing_columns = [column for column in columns if column not in set(pf.schema_arrow.names)]
        if missing_columns:
            raise SurfaceConstructionError(f"013 missing columns in {path}: {missing_columns}")
        table = pf.read(columns=columns)
        df = table.to_pandas()
        rows_read += int(len(df))
        df["upstream_source_file"] = str(path)
        df["upstream_source_row_ordinal"] = range(len(df))
        frames.append(df)
    if not frames:
        empty = pd.DataFrame(columns=columns)
        return empty, file_docs, {"rows_read": 0, "rows_after_sample_filter": 0, "rows_after_calendar_filter": 0}

    raw = pd.concat(frames, ignore_index=True)
    raw["ticker"] = raw["ticker"].astype(str).str.strip().str.upper()
    raw["session_date"] = raw["date"].map(lambda value: parse_date(value).isoformat())
    raw["bar_end_utc"] = pd.to_datetime(raw["ts_utc"], utc=True, errors="coerce")
    raw = raw[raw["ticker"].isin(selected_tickers) & raw["session_date"].isin(selected_sessions)].copy()
    raw = raw[
        raw.apply(lambda row: row["session_date"] in selected_dates_by_ticker[row["ticker"]], axis=1)
    ].copy()
    rows_after_sample_filter = int(len(raw))

    def in_calendar_boundary(row: pd.Series) -> bool:
        cal = calendar.get(str(row["session_date"]))
        if not cal:
            return False
        bar_end = row["bar_end_utc"]
        if pd.isna(bar_end):
            return False
        return bool(cal["_session_open_utc_ts"] <= bar_end <= cal["_session_close_utc_ts"])

    raw["inside_governed_session"] = raw.apply(in_calendar_boundary, axis=1)
    filtered = raw[raw["inside_governed_session"]].copy()
    for src, dst in [("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"), ("v", "volume")]:
        filtered[dst] = pd.to_numeric(filtered[src], errors="coerce")
    filtered["vwap"] = pd.to_numeric(filtered.get("vw"), errors="coerce")
    filtered["transaction_count"] = pd.to_numeric(filtered.get("n"), errors="coerce")
    metrics = {
        "rows_read": int(rows_read),
        "rows_after_sample_filter": rows_after_sample_filter,
        "rows_after_calendar_filter": int(len(filtered)),
        "selected_tickers": selected_tickers,
        "selected_sessions": selected_sessions,
    }
    return filtered, file_docs, metrics


def build_surface_rows(
    *,
    filtered_013: pd.DataFrame,
    sample_rows: list[dict[str, Any]],
    calendar: dict[str, dict[str, Any]],
    source_snapshot_fingerprint: str,
    output_path: Path,
) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
    instrument_by_pair = {
        (str(row["ticker"]).upper(), str(row["session_date"])): str(row["instrument_id"])
        for row in sample_rows
    }
    context_ids_by_pair: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in sample_rows:
        context_ids_by_pair[(str(row["ticker"]).upper(), str(row["session_date"]))].append(str(row["sample_context_id"]))

    rows = filtered_013.copy()
    rows["instrument_id"] = rows.apply(
        lambda row: instrument_by_pair.get((str(row["ticker"]), str(row["session_date"])), ""),
        axis=1,
    )
    rows["calendar_row_fingerprint"] = rows["session_date"].map(
        lambda session: calendar[str(session)]["calendar_row_fingerprint"]
    )
    rows["calendar_version"] = rows["session_date"].map(lambda session: calendar[str(session)]["calendar_version"])
    rows["session_open_utc"] = rows["session_date"].map(lambda session: calendar[str(session)]["session_open_utc"])
    rows["session_close_utc"] = rows["session_date"].map(lambda session: calendar[str(session)]["session_close_utc"])
    rows["session_type"] = rows["session_date"].map(lambda session: calendar[str(session)]["session_type"])
    rows["is_early_close"] = rows["session_date"].map(lambda session: bool(calendar[str(session)]["is_early_close"]))
    rows["sample_context_ids_for_ticker_session"] = rows.apply(
        lambda row: canonical_json(context_ids_by_pair[(str(row["ticker"]), str(row["session_date"]))], ensure_ascii=False),
        axis=1,
    )
    rows["upstream_source_alias"] = "013_ohlcv_1m_quote_guarded"
    rows["source_alias"] = "014_master_intraday_bar_table_candidate"
    rows["source_file"] = str(output_path)
    rows["source_snapshot_fingerprint"] = source_snapshot_fingerprint
    rows["bar_size"] = "1m"
    rows["price_view"] = "quote_guarded"
    rows["selection_reason"] = "scale_c_frozen_sample_governed_calendar_session_surface"
    rows["year"] = pd.to_numeric(rows["year"], errors="coerce").fillna(-1).astype("int64")
    rows["month"] = pd.to_numeric(rows["month"], errors="coerce").fillna(-1).astype("int64")

    duplicate_rows: list[dict[str, Any]] = []
    statuses: dict[tuple[str, str, str], str] = {}
    keep_indexes: list[int] = []
    for key, group in rows.groupby(["ticker", "session_date", "bar_end_utc"], sort=True, dropna=False):
        ticker, session_date, bar_end = key
        state_columns = ["open", "high", "low", "close", "volume"]
        distinct_states = group[state_columns].drop_duplicates()
        if len(group) == 1:
            status = "unique"
        elif len(distinct_states) == 1:
            status = "identical_duplicate_rows_collapsed"
        else:
            status = "conflicting_duplicate_rows"
        sorted_group = group.sort_values(["upstream_source_file", "upstream_source_row_ordinal"])
        keep_indexes.append(int(sorted_group.index[0]))
        key_tuple = (str(ticker), str(session_date), iso_utc(bar_end))
        statuses[key_tuple] = status
        if len(group) > 1:
            duplicate_rows.append(
                {
                    "ticker": ticker,
                    "session_date": session_date,
                    "bar_end_utc": iso_utc(bar_end),
                    "duplicate_group_row_count": int(len(group)),
                    "duplicate_group_distinct_state_count": int(len(distinct_states)),
                    "duplicate_status": status,
                    "kept_upstream_source_file": str(sorted_group.iloc[0]["upstream_source_file"]),
                    "dropped_rows": int(max(0, len(group) - 1)),
                }
            )

    surface = rows.loc[sorted(keep_indexes)].copy()
    surface = surface.sort_values(["ticker", "session_date", "bar_end_utc", "upstream_source_file", "upstream_source_row_ordinal"]).reset_index(drop=True)
    surface["duplicate_status"] = surface.apply(
        lambda row: statuses[(str(row["ticker"]), str(row["session_date"]), iso_utc(row["bar_end_utc"]))],
        axis=1,
    )
    surface["source_row_ordinal"] = range(len(surface))
    surface["ts_utc"] = surface["bar_end_utc"]
    duplicate_metrics = {
        "duplicate_groups": len(duplicate_rows),
        "identical_duplicate_groups": sum(1 for row in duplicate_rows if row["duplicate_status"] == "identical_duplicate_rows_collapsed"),
        "conflicting_duplicate_groups": sum(1 for row in duplicate_rows if row["duplicate_status"] == "conflicting_duplicate_rows"),
    }
    return surface, duplicate_rows, duplicate_metrics


def write_surface(path: Path, rows: pd.DataFrame) -> None:
    column_order = [
        "source_alias",
        "source_file",
        "source_row_ordinal",
        "source_snapshot_fingerprint",
        "upstream_source_alias",
        "upstream_source_file",
        "upstream_source_row_ordinal",
        "ticker",
        "instrument_id",
        "session_date",
        "year",
        "month",
        "ts_utc",
        "bar_end_utc",
        "bar_size",
        "price_view",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap",
        "transaction_count",
        "duplicate_status",
        "selection_reason",
        "calendar_version",
        "calendar_row_fingerprint",
        "session_open_utc",
        "session_close_utc",
        "session_type",
        "is_early_close",
        "sample_context_ids_for_ticker_session",
    ]
    rows = rows[column_order].copy()
    rows["source_row_ordinal"] = pd.to_numeric(rows["source_row_ordinal"], errors="coerce").fillna(-1).astype("int64")
    rows["upstream_source_row_ordinal"] = pd.to_numeric(rows["upstream_source_row_ordinal"], errors="coerce").fillna(-1).astype("int64")
    rows["year"] = pd.to_numeric(rows["year"], errors="coerce").fillna(-1).astype("int64")
    rows["month"] = pd.to_numeric(rows["month"], errors="coerce").fillna(-1).astype("int64")
    for column in ["open", "high", "low", "close", "volume", "vwap", "transaction_count"]:
        rows[column] = pd.to_numeric(rows[column], errors="coerce").astype("float64")
    rows["ts_utc"] = pd.to_datetime(rows["ts_utc"], utc=True, errors="coerce")
    rows["bar_end_utc"] = pd.to_datetime(rows["bar_end_utc"], utc=True, errors="coerce")
    schema = pa.schema(
        [
            ("source_alias", pa.string()),
            ("source_file", pa.string()),
            ("source_row_ordinal", pa.int64()),
            ("source_snapshot_fingerprint", pa.string()),
            ("upstream_source_alias", pa.string()),
            ("upstream_source_file", pa.string()),
            ("upstream_source_row_ordinal", pa.int64()),
            ("ticker", pa.string()),
            ("instrument_id", pa.string()),
            ("session_date", pa.string()),
            ("year", pa.int64()),
            ("month", pa.int64()),
            ("ts_utc", pa.timestamp("us", tz="UTC")),
            ("bar_end_utc", pa.timestamp("us", tz="UTC")),
            ("bar_size", pa.string()),
            ("price_view", pa.string()),
            ("open", pa.float64()),
            ("high", pa.float64()),
            ("low", pa.float64()),
            ("close", pa.float64()),
            ("volume", pa.float64()),
            ("vwap", pa.float64()),
            ("transaction_count", pa.float64()),
            ("duplicate_status", pa.string()),
            ("selection_reason", pa.string()),
            ("calendar_version", pa.string()),
            ("calendar_row_fingerprint", pa.string()),
            ("session_open_utc", pa.string()),
            ("session_close_utc", pa.string()),
            ("session_type", pa.string()),
            ("is_early_close", pa.bool_()),
            ("sample_context_ids_for_ticker_session", pa.string()),
        ]
    )
    table = pa.Table.from_pandas(rows, schema=schema, preserve_index=False)
    pq.write_table(table, path, compression="zstd")


def surface_fingerprint(rows: pd.DataFrame) -> str:
    payload: list[dict[str, Any]] = []
    for _, row in rows.sort_values(["ticker", "session_date", "bar_end_utc", "source_row_ordinal"]).iterrows():
        payload.append(
            {
                "ticker": row["ticker"],
                "instrument_id": row["instrument_id"],
                "session_date": row["session_date"],
                "bar_end_utc": json_safe_value(row["bar_end_utc"]),
                "open": json_safe_value(row["open"]),
                "high": json_safe_value(row["high"]),
                "low": json_safe_value(row["low"]),
                "close": json_safe_value(row["close"]),
                "volume": json_safe_value(row["volume"]),
                "duplicate_status": row["duplicate_status"],
                "calendar_row_fingerprint": row["calendar_row_fingerprint"],
                "upstream_source_file": row["upstream_source_file"],
                "upstream_source_row_ordinal": int(row["upstream_source_row_ordinal"]),
            }
        )
    return sha256_payload(payload)


def build_session_boundary_report(
    surface: pd.DataFrame,
    sample_rows: list[dict[str, Any]],
    calendar: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    pairs = sorted({(str(row["ticker"]).upper(), str(row["session_date"])) for row in sample_rows})
    rows: list[dict[str, Any]] = []
    metrics = {
        "selected_instrument_sessions": len(pairs),
        "selected_instrument_sessions_missing": 0,
        "session_boundary_mismatches": 0,
        "early_close_boundary_failures": 0,
    }
    for ticker, session in pairs:
        subset = surface[(surface["ticker"] == ticker) & (surface["session_date"] == session)].copy()
        cal = calendar[session]
        open_utc = cal["_session_open_utc_ts"]
        close_utc = cal["_session_close_utc_ts"]
        if subset.empty:
            metrics["selected_instrument_sessions_missing"] += 1
            first_bar = None
            last_bar = None
            rows_in_session = 0
        else:
            first_bar = subset["bar_end_utc"].min()
            last_bar = subset["bar_end_utc"].max()
            rows_in_session = int(len(subset))
        boundary_ok = bool(rows_in_session > 0 and first_bar >= open_utc and last_bar <= close_utc)
        if not boundary_ok:
            metrics["session_boundary_mismatches"] += 1
        early_close_ok = True
        if bool(cal["is_early_close"]) and rows_in_session > 0 and last_bar > close_utc:
            early_close_ok = False
            metrics["early_close_boundary_failures"] += 1
        rows.append(
            {
                "ticker": ticker,
                "session_date": session,
                "calendar_version": cal["calendar_version"],
                "session_open_utc": cal["session_open_utc"],
                "session_close_utc": cal["session_close_utc"],
                "session_type": cal["session_type"],
                "is_early_close": cal["is_early_close"],
                "surface_rows": rows_in_session,
                "first_surface_bar_end_utc": json_safe_value(first_bar),
                "last_surface_bar_end_utc": json_safe_value(last_bar),
                "boundary_ok": boundary_ok,
                "early_close_boundary_ok": early_close_ok,
                "finding": "PASS" if boundary_ok and early_close_ok else "FAIL",
            }
        )
    return rows, metrics


def build_cutoff_report(
    surface: pd.DataFrame,
    sample_rows: list[dict[str, Any]],
    calendar: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    metrics = {
        "cutoff_failures": 0,
        "pre_bar_admitted_bar_failures": 0,
        "integrable_contexts_without_prior_or_current_bar": 0,
    }
    for sample in sample_rows:
        ticker = str(sample["ticker"]).upper()
        session = str(sample["session_date"])
        decision_ts = parse_utc(sample["decision_timestamp_utc"])
        subset = surface[(surface["ticker"] == ticker) & (surface["session_date"] == session)].copy()
        eligible = subset[subset["bar_end_utc"] <= decision_ts].copy()
        selected_bar = None if eligible.empty else eligible["bar_end_utc"].max()
        expected_blocked = sample["expected_context_outcome"] == "REJECTED_REQUIRED_OBJECT_BLOCKED"
        cutoff_ok = True
        finding = "PASS"
        if expected_blocked and len(eligible) != 0:
            cutoff_ok = False
            finding = "FAIL_PRE_BAR_ADMITTED_BAR"
            metrics["pre_bar_admitted_bar_failures"] += 1
        if not expected_blocked and len(eligible) == 0:
            cutoff_ok = False
            finding = "FAIL_NO_BAR_AVAILABLE_AT_DECISION"
            metrics["integrable_contexts_without_prior_or_current_bar"] += 1
        if not cutoff_ok:
            metrics["cutoff_failures"] += 1
        cal = calendar[session]
        rows.append(
            {
                "sample_context_id": sample["sample_context_id"],
                "ticker": ticker,
                "instrument_id": sample["instrument_id"],
                "session_date": session,
                "calendar_stratum": sample["calendar_stratum"],
                "decision_case": sample["decision_case"],
                "decision_timestamp_utc": sample["decision_timestamp_utc"],
                "expected_context_outcome": sample["expected_context_outcome"],
                "bars_at_or_before_decision": int(len(eligible)),
                "selected_bar_end_utc": json_safe_value(selected_bar),
                "surface_rows_for_ticker_session": int(len(subset)),
                "future_surface_rows_after_decision": int(len(subset) - len(eligible)),
                "governed_session_open_utc": cal["session_open_utc"],
                "governed_session_close_utc": cal["session_close_utc"],
                "decision_after_governed_close": bool(decision_ts > cal["_session_close_utc_ts"]),
                "cutoff_ok": cutoff_ok,
                "finding": finding,
            }
        )
    return rows, metrics


def write_run_readout(path: Path, summary: dict[str, Any], run_dir: Path) -> None:
    text = f"""# Experimental Core Four Market State Scale C Execution Surface Construction Readout v0.1

run_id = `{summary['run_id']}`
script_version = `{SCRIPT_VERSION}`

## Decision

```text
experimental_core_four_market_state_scale_c_execution_surface_construction = {summary['surface_construction_status']}
scale_c_builder_resolution_execution = NOT_EXECUTED_REQUIRES_SEPARATE_GATE
market_state_integration = NOT_EXECUTED
market_state_materialization = NOT_EXECUTED
official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
```

## Counts

```text
sample_manifest_rows = {summary['sample_manifest_rows']}
selected_instruments = {summary['selected_instruments']}
selected_sessions = {summary['selected_sessions']}
selected_instrument_sessions = {summary['selected_instrument_sessions']}
source_013_rows_read = {summary['source_013_rows_read']}
surface_rows_written = {summary['surface_rows_written']}
candidate_surface_parquet_files_written = {summary['candidate_surface_parquet_files_written']}
calendar_binding_failures = {summary['calendar_binding_failures']}
session_boundary_mismatches = {summary['session_boundary_mismatches']}
early_close_boundary_failures = {summary['early_close_boundary_failures']}
source_coverage_failures = {summary['source_coverage_failures']}
conflicting_duplicate_groups = {summary['conflicting_duplicate_groups']}
cutoff_failures = {summary['cutoff_failures']}
authority_failures = {summary['authority_failures']}
determinism_failures = {summary['determinism_failures']}
hard_validation_failures = {summary['hard_validation_failures']}
```

## Fingerprints

```text
scale_c_sample_fingerprint = {summary['scale_c_sample_fingerprint']}
calendar_selection_fingerprint = {summary['calendar_selection_fingerprint']}
source_snapshot_fingerprint = {summary['source_snapshot_fingerprint']}
scale_c_execution_surface_fingerprint = {summary['scale_c_execution_surface_fingerprint']}
surface_parquet_sha256 = {summary['surface_parquet_sha256']}
```

## Boundary

```text
013_direct_builder_input = false
builder_records_emitted = 0
information_object_formulas_executed = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
original_014_modified = false
```

Run directory: `{run_dir}`
"""
    atomic_write_text(path, text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    args = parser.parse_args()

    scope_path = args.scope.resolve()
    scope_dir = scope_path.parent
    base_dir = scope_dir.parent
    repo_root = base_dir.parents[2]
    scope = read_json(scope_path)
    validate_scope(scope)

    run_id = f"{RUN_ID_PREFIX}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = base_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    start = utc_now()
    surface_path = run_dir / SURFACE_NAME

    pre_manifest = {
        "run_id": run_id,
        "status": "STARTING",
        "created_at_utc": start,
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "command_line": " ".join(sys.argv),
        "cwd": str(Path.cwd()),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "scope": str(scope_path),
        "output_root": str(run_dir),
        "git_commit": git_value(["git", "rev-parse", "HEAD"], repo_root),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root),
        "git_dirty_state": git_value(["git", "status", "--short"], repo_root),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "limits": scope["limits"],
        "success_criteria": scope["acceptance_criteria"],
        "monitor_command": f"Get-Content -LiteralPath '{run_dir / 'heartbeat.json'}'",
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(
        run_dir / "pid_manifest.json",
        {
            "run_id": run_id,
            "wrapper_pid": os.getpid(),
            "parent_pid": os.getppid(),
            "process_name": "python",
            "started_at_utc": start,
            "current_stage": "starting",
            "expected_alive": True,
        },
    )

    def heartbeat(stage: str, status: str = "RUNNING", **extra: Any) -> None:
        payload = {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": status,
            "stage": stage,
            "wrapper_pid": os.getpid(),
            **extra,
        }
        write_json(run_dir / "heartbeat.json", payload)
        with (run_dir / "heartbeat.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json(payload, ensure_ascii=False) + "\n")

    heartbeat("load_scope_and_inputs")

    registry_path, roots, _ = resolve_source_roots(scope, scope_dir)
    sample_rows, sample_manifest = load_sample(scope, scope_dir)
    selected_tickers = sample_manifest["tickers"]
    selected_sessions = sample_manifest["sessions"]
    calendar, calendar_report_rows, calendar_manifest = load_calendar(scope, scope_dir, selected_sessions)
    heartbeat("read_013_partitions", selected_tickers=len(selected_tickers), selected_sessions=len(selected_sessions))

    source_013_files, missing_013_months = discover_013_files(roots["013_ohlcv_1m_quote_guarded"], sample_rows)
    filtered_013, source_013_file_docs, source_013_metrics = load_013_rows(source_013_files, sample_rows, calendar)
    original_014_path = roots["014_master_intraday_bar_table_candidate"] / "data.parquet"
    original_014_before = file_doc(original_014_path, include_hash=True)
    if source_013_metrics["rows_read"] > int(scope["limits"]["maximum_013_rows_read_for_execution_surface"]):
        raise SurfaceConstructionError("013 row-read cap exceeded")

    source_snapshot_payload = {
        "run_id": run_id,
        "source_binding_registry": str(registry_path),
        "source_paths": {
            "013_ohlcv_1m_quote_guarded": str(roots["013_ohlcv_1m_quote_guarded"]),
            "014_master_intraday_bar_table_candidate": str(roots["014_master_intraday_bar_table_candidate"]),
        },
        "sample_manifest": sample_manifest,
        "calendar_manifest": calendar_manifest,
        "selected_tickers": selected_tickers,
        "selected_sessions": selected_sessions,
        "source_files": {
            "013_selected_month_files": source_013_file_docs,
            "014_original_file_before": original_014_before,
        },
        "missing_013_month_partitions": missing_013_months,
        "source_read_rows": {
            "013_rows_read": source_013_metrics["rows_read"],
            "013_rows_after_sample_filter": source_013_metrics["rows_after_sample_filter"],
            "013_rows_after_calendar_filter": source_013_metrics["rows_after_calendar_filter"],
            "014_original_rows_read": 0,
        },
        "source_use": {
            "013_ohlcv_1m_quote_guarded": "execution_surface_construction_only",
            "014_master_intraday_bar_table_candidate": "original_hash_integrity_check_only",
        },
    }
    source_snapshot_fingerprint = sha256_payload(source_snapshot_payload)
    source_snapshot_payload["source_snapshot_fingerprint"] = source_snapshot_fingerprint
    write_json(run_dir / "scale_c_source_snapshot_manifest.json", source_snapshot_payload)

    heartbeat("build_surface_rows", rows_after_calendar_filter=source_013_metrics["rows_after_calendar_filter"])
    surface, duplicate_rows, duplicate_metrics = build_surface_rows(
        filtered_013=filtered_013,
        sample_rows=sample_rows,
        calendar=calendar,
        source_snapshot_fingerprint=source_snapshot_fingerprint,
        output_path=surface_path,
    )
    if len(surface) > int(scope["limits"]["maximum_run_local_014_execution_surface_rows"]):
        raise SurfaceConstructionError("Run-local 014 surface row cap exceeded")

    write_surface(surface_path, surface)
    parquet_files_written = 1
    surface_semantic_fingerprint = surface_fingerprint(surface)
    surface_sha256 = sha256_file(surface_path)

    session_boundary_rows, session_metrics = build_session_boundary_report(surface, sample_rows, calendar)
    cutoff_rows, cutoff_metrics = build_cutoff_report(surface, sample_rows, calendar)
    heartbeat("write_reports", surface_rows=len(surface))

    pairs = sorted({(str(row["ticker"]).upper(), str(row["session_date"])) for row in sample_rows})
    represented_pairs = set(zip(surface["ticker"].astype(str), surface["session_date"].astype(str)))
    missing_pairs = sorted(set(pairs) - represented_pairs)
    source_coverage_failures = len(missing_pairs) + len(missing_013_months)
    selected_instruments_missing = len(set(selected_tickers) - set(surface["ticker"].astype(str).unique()))
    selected_sessions_missing = len(set(selected_sessions) - set(surface["session_date"].astype(str).unique()))
    unexpected_instruments = len(set(surface["ticker"].astype(str).unique()) - set(selected_tickers))
    unexpected_sessions = len(set(surface["session_date"].astype(str).unique()) - set(selected_sessions))

    original_014_after = file_doc(original_014_path, include_hash=True)
    original_hash_unchanged = original_014_before.get("sha256") == original_014_after.get("sha256")
    original_mtime_unchanged = original_014_before.get("mtime_utc") == original_014_after.get("mtime_utc")
    authority_failures = 0 if original_hash_unchanged and original_mtime_unchanged else 1

    determinism_payload = {
        "surface_fingerprint_recomputed": surface_fingerprint(surface),
        "surface_fingerprint_recorded": surface_semantic_fingerprint,
        "source_snapshot_fingerprint_recomputed": sha256_payload(
            {key: value for key, value in source_snapshot_payload.items() if key != "source_snapshot_fingerprint"}
        ),
        "source_snapshot_fingerprint_recorded": source_snapshot_fingerprint,
        "determinism_failures": 0,
    }
    if (
        determinism_payload["surface_fingerprint_recomputed"] != determinism_payload["surface_fingerprint_recorded"]
        or determinism_payload["source_snapshot_fingerprint_recomputed"] != determinism_payload["source_snapshot_fingerprint_recorded"]
    ):
        determinism_payload["determinism_failures"] = 1

    hard_validation_failures = 0
    hard_validation_failures += int(calendar_manifest["binding_failures"])
    hard_validation_failures += int(session_metrics["session_boundary_mismatches"])
    hard_validation_failures += int(session_metrics["early_close_boundary_failures"])
    hard_validation_failures += int(source_coverage_failures)
    hard_validation_failures += int(duplicate_metrics["conflicting_duplicate_groups"])
    hard_validation_failures += int(cutoff_metrics["cutoff_failures"])
    hard_validation_failures += int(authority_failures)
    hard_validation_failures += int(determinism_payload["determinism_failures"])
    hard_validation_failures += int(selected_instruments_missing + selected_sessions_missing + unexpected_instruments + unexpected_sessions)

    total_output_bytes = sum(item.stat().st_size for item in run_dir.iterdir() if item.is_file())
    if total_output_bytes > int(scope["limits"]["maximum_output_bytes_per_stage"]):
        hard_validation_failures += 1

    status = "PASS_WITH_RESTRICTIONS"
    if duplicate_metrics["conflicting_duplicate_groups"]:
        status = "FAILED_DUPLICATE_POLICY"
    elif calendar_manifest["binding_failures"]:
        status = "BLOCKED_CALENDAR_BINDING"
    elif session_metrics["session_boundary_mismatches"] or session_metrics["early_close_boundary_failures"]:
        status = "BLOCKED_SESSION_BOUNDARY"
    elif source_coverage_failures:
        status = "BLOCKED_SOURCE_COVERAGE"
    elif hard_validation_failures:
        status = "FAILED_CONTRACT"

    surface_manifest = {
        "run_id": run_id,
        "output": str(surface_path),
        "created": bool(parquet_files_written),
        "surface_semantics": scope["output_surface_semantics"],
        "original_014_modified": False,
        "official_014_promotion": False,
        "013_direct_builder_input": False,
        "013_upstream_rows_read": int(source_013_metrics["rows_read"]),
        "surface_rows_written": int(len(surface)),
        "candidate_surface_parquet_files_written": parquet_files_written,
        "scale_c_sample_fingerprint": sample_manifest["scale_c_sample_fingerprint"],
        "calendar_selection_fingerprint": calendar_manifest["calendar_selection_fingerprint"],
        "source_snapshot_fingerprint": source_snapshot_fingerprint,
        "scale_c_execution_surface_fingerprint": surface_semantic_fingerprint,
        "parquet_sha256": surface_sha256,
        "parquet_bytes": int(surface_path.stat().st_size),
    }
    write_json(run_dir / "scale_c_execution_surface_manifest.json", surface_manifest)

    source_coverage_rows = [
        {
            "source_alias": "013_ohlcv_1m_quote_guarded",
            "rows_read": int(source_013_metrics["rows_read"]),
            "rows_after_sample_filter": int(source_013_metrics["rows_after_sample_filter"]),
            "rows_after_calendar_filter": int(source_013_metrics["rows_after_calendar_filter"]),
            "distinct_tickers": int(surface["ticker"].nunique(dropna=True)),
            "distinct_sessions": int(surface["session_date"].nunique(dropna=True)),
            "source_use": "execution_surface_construction_only",
        },
        {
            "source_alias": "014_master_intraday_bar_table_candidate",
            "rows_read": 0,
            "rows_after_sample_filter": 0,
            "rows_after_calendar_filter": 0,
            "distinct_tickers": 0,
            "distinct_sessions": 0,
            "source_use": "original_hash_integrity_check_only",
        },
    ]
    write_csv_rows(
        run_dir / "scale_c_surface_source_coverage_report.csv",
        [
            "source_alias",
            "rows_read",
            "rows_after_sample_filter",
            "rows_after_calendar_filter",
            "distinct_tickers",
            "distinct_sessions",
            "source_use",
        ],
        source_coverage_rows,
    )
    write_csv_rows(
        run_dir / "scale_c_surface_calendar_binding_report.csv",
        [
            "session_date",
            "matched_rows",
            "calendar_id",
            "calendar_version",
            "session_open_utc",
            "session_close_utc",
            "session_type",
            "is_early_close",
            "is_closed_or_holiday",
            "calendar_row_fingerprint",
            "source_snapshot_fingerprint",
            "finding",
        ],
        calendar_report_rows,
    )
    write_csv_rows(
        run_dir / "scale_c_surface_session_boundary_report.csv",
        [
            "ticker",
            "session_date",
            "calendar_version",
            "session_open_utc",
            "session_close_utc",
            "session_type",
            "is_early_close",
            "surface_rows",
            "first_surface_bar_end_utc",
            "last_surface_bar_end_utc",
            "boundary_ok",
            "early_close_boundary_ok",
            "finding",
        ],
        session_boundary_rows,
    )
    write_csv_rows(
        run_dir / "scale_c_surface_duplicate_report.csv",
        [
            "ticker",
            "session_date",
            "bar_end_utc",
            "duplicate_group_row_count",
            "duplicate_group_distinct_state_count",
            "duplicate_status",
            "kept_upstream_source_file",
            "dropped_rows",
        ],
        duplicate_rows,
    )
    write_csv_rows(
        run_dir / "scale_c_surface_cutoff_capability_report.csv",
        [
            "sample_context_id",
            "ticker",
            "instrument_id",
            "session_date",
            "calendar_stratum",
            "decision_case",
            "decision_timestamp_utc",
            "expected_context_outcome",
            "bars_at_or_before_decision",
            "selected_bar_end_utc",
            "surface_rows_for_ticker_session",
            "future_surface_rows_after_decision",
            "governed_session_open_utc",
            "governed_session_close_utc",
            "decision_after_governed_close",
            "cutoff_ok",
            "finding",
        ],
        cutoff_rows,
    )
    write_json(run_dir / "scale_c_surface_determinism_report.json", determinism_payload)
    authority_report = {
        "run_id": run_id,
        "upstream_source_use": "execution_surface_construction_only",
        "013_direct_builder_input": False,
        "builder_records_emitted": 0,
        "information_object_formulas_executed": 0,
        "market_state_records_emitted": 0,
        "market_state_parquet_files_written": 0,
        "original_014_sha256_before": original_014_before.get("sha256"),
        "original_014_sha256_after": original_014_after.get("sha256"),
        "original_014_sha256_unchanged": original_hash_unchanged,
        "original_014_mtime_before": original_014_before.get("mtime_utc"),
        "original_014_mtime_after": original_014_after.get("mtime_utc"),
        "original_014_mtime_unchanged": original_mtime_unchanged,
        "official_market_state_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
        "authority_failures": authority_failures,
    }
    write_json(run_dir / "scale_c_surface_authority_report.json", authority_report)

    distinct_open_clocks = sorted({str(row["session_open_utc"])[11:19] for row in calendar.values()})
    distinct_close_clocks = sorted({str(row["session_close_utc"])[11:19] for row in calendar.values()})
    summary = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_id": scope["scope_id"],
        "surface_construction_status": "CLOSED_PASS_WITH_RESTRICTIONS" if status == "PASS_WITH_RESTRICTIONS" else status,
        "terminal_status": status,
        "sample_manifest_rows": int(len(sample_rows)),
        "scale_c_sample_fingerprint": sample_manifest["scale_c_sample_fingerprint"],
        "sample_fingerprint_match": True,
        "selected_instruments": int(len(selected_tickers)),
        "selected_sessions": int(len(selected_sessions)),
        "selected_instrument_sessions": int(len(pairs)),
        "source_013_files_read": int(len(source_013_files)),
        "source_013_rows_read": int(source_013_metrics["rows_read"]),
        "maximum_013_rows_read_for_execution_surface": int(scope["limits"]["maximum_013_rows_read_for_execution_surface"]),
        "surface_rows_written": int(len(surface)),
        "maximum_run_local_014_execution_surface_rows": int(scope["limits"]["maximum_run_local_014_execution_surface_rows"]),
        "candidate_surface_parquet_files_written": parquet_files_written,
        "surface_parquet_sha256": surface_sha256,
        "surface_parquet_bytes": int(surface_path.stat().st_size),
        "scale_c_execution_surface_fingerprint": surface_semantic_fingerprint,
        "source_snapshot_fingerprint": source_snapshot_fingerprint,
        "calendar_selection_fingerprint": calendar_manifest["calendar_selection_fingerprint"],
        "calendar_source_snapshot_fingerprint": calendar_manifest["calendar_source_snapshot_fingerprint"],
        "calendar_binding_failures": int(calendar_manifest["binding_failures"]),
        "calendar_version_match": True,
        "fixed_utc_probe_calendar_as_current_authority": 0,
        "distinct_governed_open_utc_clocks": distinct_open_clocks,
        "distinct_governed_close_utc_clocks": distinct_close_clocks,
        "selected_instruments_missing": selected_instruments_missing,
        "selected_sessions_missing": selected_sessions_missing,
        "unexpected_instruments": unexpected_instruments,
        "unexpected_sessions": unexpected_sessions,
        "source_coverage_failures": source_coverage_failures,
        "selected_instrument_sessions_missing": session_metrics["selected_instrument_sessions_missing"],
        "session_boundary_mismatches": session_metrics["session_boundary_mismatches"],
        "early_close_boundary_failures": session_metrics["early_close_boundary_failures"],
        "duplicate_groups": duplicate_metrics["duplicate_groups"],
        "identical_duplicate_groups": duplicate_metrics["identical_duplicate_groups"],
        "conflicting_duplicate_groups": duplicate_metrics["conflicting_duplicate_groups"],
        "cutoff_failures": cutoff_metrics["cutoff_failures"],
        "pre_bar_admitted_bar_failures": cutoff_metrics["pre_bar_admitted_bar_failures"],
        "integrable_contexts_without_prior_or_current_bar": cutoff_metrics["integrable_contexts_without_prior_or_current_bar"],
        "builder_records_emitted": 0,
        "information_object_formulas_executed": 0,
        "market_state_records_emitted": 0,
        "market_state_parquet_files_written": 0,
        "original_014_modified": False,
        "013_direct_builder_input": False,
        "authority_failures": authority_failures,
        "determinism_failures": determinism_payload["determinism_failures"],
        "hard_validation_failures": hard_validation_failures,
        "next_allowed_gate": scope["next_boundary"]["allowed_next_gate_if_pass"]
        if status == "PASS_WITH_RESTRICTIONS"
        else "remediate_scale_c_execution_surface_construction",
    }
    write_json(run_dir / "scale_c_execution_surface_summary.json", summary)
    write_run_readout(
        run_dir / "experimental_core_four_market_state_scale_c_execution_surface_construction_readout_v0_1.md",
        summary,
        run_dir,
    )

    observed_outputs = sorted(
        name for name in os.listdir(long_path(run_dir)) if os.path.isfile(long_path(run_dir / name))
    )
    expected_outputs = set(scope["required_output_files"])
    missing_required_outputs = sorted(expected_outputs - set(observed_outputs) - {"scale_c_execution_surface_final_manifest.json"})
    final_outputs = sorted(set(observed_outputs) | {"scale_c_execution_surface_final_manifest.json"})
    unexpected_outputs = sorted(set(final_outputs) - expected_outputs)
    output_file_count = len(final_outputs)
    if missing_required_outputs or output_file_count > int(scope["limits"]["maximum_output_files"]):
        summary["hard_validation_failures"] += 1
        hard_validation_failures = int(summary["hard_validation_failures"])
        if status == "PASS_WITH_RESTRICTIONS":
            status = "FAILED_CONTRACT"
            summary["surface_construction_status"] = status
            summary["terminal_status"] = status
            summary["next_allowed_gate"] = "remediate_scale_c_execution_surface_construction"
            write_json(run_dir / "scale_c_execution_surface_summary.json", summary)

    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "created_at_utc": start,
        "completed_at_utc": utc_now(),
        "status": "CLOSED_PASS_WITH_RESTRICTIONS" if status == "PASS_WITH_RESTRICTIONS" else status,
        "terminal_status": status,
        "summary": summary,
        "outputs": {
            "files_written_before_final_manifest": observed_outputs,
            "final_output_files": final_outputs,
            "final_output_file_count": output_file_count,
            "required_output_files": int(scope["limits"]["required_output_files"]),
            "maximum_output_files": int(scope["limits"]["maximum_output_files"]),
            "missing_required_output_files": missing_required_outputs,
            "unexpected_output_files": unexpected_outputs,
        },
        "next_allowed_gate": summary["next_allowed_gate"],
        "still_closed": scope["next_boundary"]["still_closed"],
    }
    write_json(run_dir / "scale_c_execution_surface_final_manifest.json", final_manifest)
    heartbeat("completed", status=final_manifest["status"], final_manifest=str(run_dir / "scale_c_execution_surface_final_manifest.json"))
    print(json.dumps(json_safe_value({"run_id": run_id, "status": final_manifest["status"], "run_dir": str(run_dir), "summary": summary}), indent=2))
    return 0 if hard_validation_failures == 0 and status == "PASS_WITH_RESTRICTIONS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
