from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


SCRIPT_VERSION = "experimental_core_four_market_state_scale_b_sample_preflight_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_b_scope_v0_1.json"
)
RUN_ID_PREFIX = "experimental_core_four_market_state_scale_b_sample_preflight_v0_1"
EXPECTED_OBJECTS_PER_CONTEXT = 4


class PreflightError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
    except TypeError:
        pass
    if hasattr(value, "item"):
        try:
            return json_safe_value(value.item())
        except Exception:
            pass
    return value


def canonical_json(value: Any, ensure_ascii: bool = True) -> str:
    return json.dumps(json_safe_value(value), ensure_ascii=ensure_ascii, sort_keys=True, separators=(",", ":"))


def serialize_cell(value: Any) -> str:
    safe = json_safe_value(value)
    if safe is None:
        return ""
    if isinstance(safe, (dict, list)):
        return canonical_json(safe, ensure_ascii=False)
    return str(safe)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_safe_value(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row, ensure_ascii=False))
            handle.write("\n")


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialize_cell(row.get(field)) for field in fieldnames})


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload, ensure_ascii=True).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_path(raw: str, base: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


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


def parse_session_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        parsed = pd.to_datetime(raw, utc=True, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()


def parse_utc_timestamp(value: Any) -> pd.Timestamp:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        raise PreflightError(f"Invalid UTC timestamp: {value!r}")
    return parsed


def clock_text(value: Any) -> str:
    parsed = parse_utc_timestamp(value)
    return parsed.to_pydatetime().astimezone(timezone.utc).time().replace(microsecond=0).isoformat()


def validate_authority(scope: dict[str, Any]) -> None:
    if scope.get("scope_id") != "experimental_core_four_market_state_scale_b_scope_v0_1":
        raise PreflightError(f"Unexpected scope_id: {scope.get('scope_id')}")
    if scope.get("scope_status") != "authorized_with_restrictions_sample_preflight_only":
        raise PreflightError(f"Scale B scope is not authorized for preflight: {scope.get('scope_status')}")
    authority = scope.get("authority", {})
    required_true = [
        "scale_b_sample_preflight_authorized",
        "calendar_binding_read_allowed",
        "eligible_pool_read_allowed",
        "bounded_daily_source_coverage_read_allowed",
        "bounded_intraday_source_coverage_read_allowed",
        "013_coverage_feasibility_read_allowed",
    ]
    required_false = [
        "scale_b_execution_authorized",
        "builder_resolution_execution_authorized",
        "information_object_resolution_authorized",
        "market_state_integration_authorized",
        "market_state_materialization_authorized",
        "market_state_parquet_write_authorized",
        "candidate_market_state_parquet_allowed",
        "013_direct_builder_input_allowed",
        "run_local_014_surface_construction_authorized",
        "raw_quotes_read_allowed",
        "quote_dependent_object_integration_allowed",
        "official_market_state_authorized",
        "production_builder_authorized",
        "state_consumption_authorized",
        "downstream_consumption_authorized",
        "dataset_promotion_authorized",
        "full_history_execution_authorized",
        "full_universe_execution_authorized",
        "reference_library_read_or_stage_allowed",
    ]
    true_offenders = [key for key in required_true if authority.get(key) is not True]
    false_offenders = [key for key in required_false if authority.get(key) is not False]
    if true_offenders:
        raise PreflightError(f"Required authority flags are not true: {true_offenders}")
    if false_offenders:
        raise PreflightError(f"Forbidden authority flags are not false: {false_offenders}")
    aliases = set(scope.get("source_aliases_allowed_for_preflight", []))
    expected_aliases = {"004_master_daily_table", "014_master_intraday_bar_table_candidate", "013_ohlcv_1m_quote_guarded"}
    if aliases != expected_aliases:
        raise PreflightError(f"Unexpected source aliases allowed for Scale B preflight: {sorted(aliases)}")
    forbidden = {str(item).replace("\\", "/") for item in scope.get("source_aliases_forbidden", [])}
    if "00_CTO/99_REFERENCE_LIBRARY" not in forbidden:
        raise PreflightError("Reference library exclusion is missing from Scale B scope")
    limits = scope.get("limits", {})
    required_outputs = len(scope.get("required_preflight_outputs", []))
    if int(limits.get("required_output_files", -1)) != required_outputs:
        raise PreflightError("required_output_files does not match required_preflight_outputs length")
    if int(limits.get("maximum_output_files", -1)) < required_outputs:
        raise PreflightError("maximum_output_files is below required_preflight_outputs length")
    shape = scope.get("target_sample_shape", {})
    target_contexts = int(shape.get("target_requested_contexts", -1))
    expected_records = int(shape.get("target_resolution_records_if_later_executed", -1))
    if target_contexts * EXPECTED_OBJECTS_PER_CONTEXT != expected_records:
        raise PreflightError("target resolution records do not equal requested contexts * 4")
    if int(shape.get("expected_blocked_contexts", -1)) + int(shape.get("target_integrable_contexts", -1)) != target_contexts:
        raise PreflightError("blocked + integrable contexts do not equal target requested contexts")
    allocation = shape.get("context_allocation", {})
    if sum(int(value) for value in allocation.values()) != target_contexts:
        raise PreflightError("context allocation does not sum to target requested contexts")


def resolve_source_roots(scope: dict[str, Any], scope_dir: Path) -> tuple[Path, dict[str, Path], dict[str, Any]]:
    registry_path = resolve_path(scope["allowed_inputs"]["source_binding_registry"], scope_dir)
    registry = read_json(registry_path)
    roots: dict[str, Path] = {}
    bindings = registry.get("bindings", {})
    for alias in ("004_master_daily_table", "014_master_intraday_bar_table_candidate", "013_ohlcv_1m_quote_guarded"):
        binding = bindings.get(alias)
        if not binding:
            raise PreflightError(f"Missing source binding for {alias}")
        root = Path(str(binding.get("physical_candidate_root"))).resolve()
        if "00_CTO/99_REFERENCE_LIBRARY" in str(root).replace("\\", "/"):
            raise PreflightError(f"Forbidden reference-library path resolved for {alias}: {root}")
        if not root.exists():
            raise PreflightError(f"Resolved source root does not exist for {alias}: {root}")
        roots[alias] = root
    return registry_path, roots, registry


def load_calendar(scope: dict[str, Any], scope_dir: Path) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
    calendar_cfg = scope["calendar_binding"]
    calendar_path = resolve_path(scope["allowed_inputs"]["governed_calendar_binding"], scope_dir)
    if not calendar_path.exists():
        raise PreflightError(f"Governed calendar binding not found: {calendar_path}")
    observed_sha = sha256_file(calendar_path)
    expected_sha = str(calendar_cfg["bound_parquet_sha256"])
    if observed_sha != expected_sha:
        raise PreflightError(f"Governed calendar SHA mismatch: expected {expected_sha}, observed {observed_sha}")
    calendar = pd.read_parquet(calendar_path)
    rows_read = int(len(calendar))
    plan_rows: list[dict[str, Any]] = []
    for plan in scope["calendar_session_plan"]:
        session_date = str(plan["session_date"])
        matches = calendar[calendar["session_date"].astype(str) == session_date]
        if len(matches) != 1:
            plan_rows.append(
                {
                    "session_date": session_date,
                    "calendar_row_present": len(matches) == 1,
                    "calendar_boundary_match": False,
                    "calendar_version_match": False,
                    "finding": f"governed calendar row count is {len(matches)}",
                    **{key: plan.get(key) for key in plan},
                }
            )
            continue
        row = matches.iloc[0]
        observed_open = clock_text(row["session_open_utc"])
        observed_close = clock_text(row["session_close_utc"])
        observed_type = str(row["session_type"])
        observed_early = bool(row["is_early_close"])
        expected_open = str(plan["expected_open_utc"])
        expected_close = str(plan["expected_close_utc"])
        expected_type = str(plan["expected_session_type"])
        expected_early = bool(plan["expected_early_close"])
        boundary_match = (
            observed_open == expected_open
            and observed_close == expected_close
            and observed_type == expected_type
            and observed_early == expected_early
            and bool(row["is_closed_or_holiday"]) is False
        )
        version_match = str(row["calendar_version"]) == str(calendar_cfg["calendar_version"])
        plan_rows.append(
            {
                "session_date": session_date,
                "stratum": str(plan["stratum"]),
                "expected_open_utc": expected_open,
                "observed_open_utc": observed_open,
                "expected_close_utc": expected_close,
                "observed_close_utc": observed_close,
                "expected_session_type": expected_type,
                "observed_session_type": observed_type,
                "expected_early_close": expected_early,
                "observed_early_close": observed_early,
                "holiday_or_closed": bool(row["is_closed_or_holiday"]),
                "calendar_version": str(row["calendar_version"]),
                "calendar_version_match": version_match,
                "calendar_id": str(row["calendar_id"]),
                "calendar_row_fingerprint": str(row["calendar_row_fingerprint"]),
                "calendar_row_present": True,
                "calendar_boundary_match": boundary_match,
                "compatible": bool(boundary_match and version_match),
                "evidence_source": "accepted governed_exchange_session_calendar_bound_v0_1",
                "finding": "governed calendar boundary matches authorized Scale B session plan"
                if boundary_match and version_match
                else "governed calendar row does not match authorized Scale B session plan",
            }
        )
    report = {
        "calendar_path": str(calendar_path),
        "calendar_rows_read": rows_read,
        "calendar_sha256": observed_sha,
        "accepted_run_id": calendar_cfg["accepted_run_id"],
        "calendar_version": calendar_cfg["calendar_version"],
        "source_snapshot_fingerprint": calendar_cfg["source_snapshot_fingerprint"],
    }
    return calendar, plan_rows, report


def load_eligible_pool(scope: dict[str, Any], scope_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pool_cfg = scope["eligible_instrument_seed_pool"]
    pool_path = resolve_path(pool_cfg["eligible_instrument_pool_path"], scope_dir)
    pool = read_json(pool_path)
    if pool.get("accepted_pool") is not True:
        raise PreflightError(f"Eligible instrument pool is not accepted: {pool_path}")
    observed_fingerprint = str(pool.get("eligible_instrument_pool_fingerprint", ""))
    expected_fingerprint = str(pool_cfg["eligible_instrument_pool_fingerprint"])
    if observed_fingerprint != expected_fingerprint:
        raise PreflightError(f"Eligible pool fingerprint mismatch: expected {expected_fingerprint}, observed {observed_fingerprint}")
    instruments = list(pool.get("instruments", []))
    if len(instruments) != int(pool_cfg["eligible_instruments_available"]):
        raise PreflightError("Eligible instrument pool count does not match scope")
    seen = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(instruments):
        ticker = str(item.get("ticker", "")).strip().upper()
        instrument_id = str(item.get("instrument_id", "")).strip()
        if not ticker or not instrument_id:
            raise PreflightError("Eligible pool contains blank ticker or instrument_id")
        if ticker in seen:
            raise PreflightError(f"Eligible pool contains duplicate ticker: {ticker}")
        seen.add(ticker)
        normalized.append({**item, "ticker": ticker, "instrument_id": instrument_id, "source_pool_rank": index + 1})
    report = {
        "pool_path": str(pool_path),
        "pool_run_id": pool.get("run_id"),
        "eligible_instrument_pool_fingerprint": observed_fingerprint,
        "eligible_instruments_available": len(normalized),
        "manual_ticker_selection_allowed": bool(pool_cfg["manual_ticker_selection_allowed"]),
    }
    return normalized, report


def read_daily_source(root: Path, tickers: list[str], session_dates: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    years = sorted({int(session_date[:4]) for session_date in session_dates} | {int(session_date[:4]) - 1 for session_date in session_dates})
    columns = ["instrument_id", "ticker", "session_date", "open", "prior_close", "volume", "year", "price_view"]
    dataset = ds.dataset(str(root), format="parquet", partitioning="hive")
    available = set(dataset.schema.names)
    missing = [column for column in columns if column not in available]
    if missing:
        raise PreflightError(f"004 missing required preflight columns: {missing}")
    filt = (
        ds.field("year").isin([int(year) for year in years])
        & (ds.field("price_view") == "split_normalized")
        & ds.field("ticker").isin([str(ticker) for ticker in tickers])
    )
    table = dataset.to_table(columns=columns, filter=filt)
    df = table.to_pandas().reset_index(drop=True)
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["session_date_obj"] = df["session_date"].map(parse_session_date)
    df["session_date_iso"] = df["session_date_obj"].map(lambda value: value.isoformat() if value else "")
    for column in ["open", "prior_close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    report = {
        "source_alias": "004_master_daily_table",
        "physical_candidate_root": str(root),
        "rows_read": int(len(df)),
        "columns_read": columns,
        "years_filter": years,
        "ticker_filter": tickers,
        "selected_price_view": "split_normalized",
        "unique_tickers": int(df["ticker"].nunique(dropna=True)),
        "unique_sessions": int(df["session_date_iso"].nunique(dropna=True)),
    }
    return df, report


def discover_013_files(root: Path, tickers: list[str], session_dates: list[str]) -> tuple[list[Path], dict[str, Any]]:
    months = sorted({int(session_date[5:7]) for session_date in session_dates})
    years = sorted({int(session_date[:4]) for session_date in session_dates})
    files: list[Path] = []
    missing_dirs: list[str] = []
    inspected_dirs = 0
    for year in years:
        for ticker in tickers:
            for month in months:
                directory = root / f"year={year}" / f"ticker={ticker}" / f"month={month:02d}"
                inspected_dirs += 1
                if not directory.exists():
                    missing_dirs.append(str(directory))
                    continue
                files.extend(sorted(directory.glob("*.parquet")))
    unique_files = sorted(set(files), key=lambda item: str(item))
    report = {
        "source_alias": "013_ohlcv_1m_quote_guarded",
        "physical_candidate_root": str(root),
        "partition_lookup_mode": "bounded_by_pool_ticker_and_authorized_session_month",
        "tickers_considered": tickers,
        "session_dates_considered": session_dates,
        "directories_inspected": inspected_dirs,
        "missing_partition_directories": len(missing_dirs),
        "files_discovered": len(unique_files),
        "files": [str(path) for path in unique_files],
    }
    return unique_files, report


def read_013_files(files: list[Path], allowed_dates: set[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    columns = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v"]
    frames: list[pd.DataFrame] = []
    file_docs: list[dict[str, Any]] = []
    rows_read = 0
    for path in files:
        pf = pq.ParquetFile(path)
        available = set(pf.schema_arrow.names)
        missing = [column for column in columns if column not in available]
        if missing:
            raise PreflightError(f"013 file missing required columns {missing}: {path}")
        table = pf.read(columns=columns)
        df = table.to_pandas()
        rows_read += int(len(df))
        df["source_file"] = str(path)
        df["source_row_ordinal"] = range(len(df))
        frames.append(df)
        file_docs.append({"path": str(path), "rows": int(len(df)), "sha256": sha256_file(path)})
    if frames:
        all_rows = pd.concat(frames, ignore_index=True)
    else:
        all_rows = pd.DataFrame(columns=columns + ["source_file", "source_row_ordinal"])
    all_rows["ticker"] = all_rows["ticker"].astype(str).str.strip().str.upper()
    all_rows["session_date_iso"] = all_rows["date"].map(lambda value: parse_session_date(value).isoformat() if parse_session_date(value) else "")
    all_rows["ts"] = pd.to_datetime(all_rows["ts_utc"], utc=True, errors="coerce")
    for src, dst in [("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"), ("v", "volume")]:
        all_rows[dst] = pd.to_numeric(all_rows[src], errors="coerce")
    filtered = all_rows[all_rows["session_date_iso"].isin(allowed_dates)].copy().reset_index(drop=True)
    report = {
        "source_alias": "013_ohlcv_1m_quote_guarded",
        "rows_read": rows_read,
        "rows_after_session_date_filter": int(len(filtered)),
        "files_read": len(files),
        "file_docs": file_docs,
        "invalid_timestamp_rows": int(all_rows["ts"].isna().sum()),
        "unique_tickers_after_filter": int(filtered["ticker"].nunique(dropna=True)) if not filtered.empty else 0,
        "unique_sessions_after_filter": int(filtered["session_date_iso"].nunique(dropna=True)) if not filtered.empty else 0,
    }
    return filtered, report


def read_014_metadata(root: Path) -> dict[str, Any]:
    data_path = root / "data.parquet" if root.is_dir() else root
    if not data_path.exists():
        return {"source_alias": "014_master_intraday_bar_table_candidate", "path": str(data_path), "exists": False}
    pf = pq.ParquetFile(data_path)
    return {
        "source_alias": "014_master_intraday_bar_table_candidate",
        "path": str(data_path),
        "exists": True,
        "metadata_only": True,
        "rows_read": 0,
        "parquet_rows": int(pf.metadata.num_rows),
        "sha256": sha256_file(data_path),
        "schema_columns": pf.schema_arrow.names,
    }


def daily_maps(daily: pd.DataFrame) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    by_ticker: dict[str, list[dict[str, Any]]] = {}
    for _, row in daily.dropna(subset=["ticker", "session_date_iso"]).iterrows():
        doc = {
            "ticker": str(row["ticker"]),
            "session_date": str(row["session_date_iso"]),
            "instrument_id": json_safe_value(row.get("instrument_id")),
            "open_present": bool(pd.notna(row.get("open"))),
            "prior_close_present": bool(pd.notna(row.get("prior_close"))),
            "volume_present": bool(pd.notna(row.get("volume"))),
        }
        by_key.setdefault((doc["ticker"], doc["session_date"]), []).append(doc)
        by_ticker.setdefault(doc["ticker"], []).append(doc)
    for ticker in by_ticker:
        by_ticker[ticker] = sorted(by_ticker[ticker], key=lambda item: item["session_date"])
    return by_key, by_ticker


def resolve_instrument_id(rows: list[dict[str, Any]]) -> tuple[str, bool, bool, int]:
    ids = sorted({str(row.get("instrument_id")) for row in rows if row.get("instrument_id") not in {None, ""}})
    return (ids[0] if len(ids) == 1 else "", len(ids) == 1, len(ids) > 1, len(ids))


def prior_volume_count(rows: list[dict[str, Any]], session_date_iso: str) -> int:
    dates = sorted({row["session_date"] for row in rows if row["session_date"] < session_date_iso and row.get("volume_present")})
    return min(len(dates), 20)


def state_signature(row: pd.Series) -> str:
    return canonical_json(
        {
            "open": json_safe_value(row.get("open")),
            "high": json_safe_value(row.get("high")),
            "low": json_safe_value(row.get("low")),
            "close": json_safe_value(row.get("close")),
            "volume": json_safe_value(row.get("volume")),
        }
    )


def build_intraday_summaries(
    intraday: pd.DataFrame,
    calendar_rows: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], dict[str, Any]], list[dict[str, Any]]]:
    calendar_by_date = {row["session_date"]: row for row in calendar_rows if row.get("compatible") is True}
    valid = intraday.dropna(subset=["ticker", "session_date_iso", "ts"]).copy()
    rows: list[dict[str, Any]] = []
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    for (ticker, session_date), group in valid.groupby(["ticker", "session_date_iso"], sort=True):
        cal = calendar_by_date.get(str(session_date))
        if not cal:
            continue
        open_ts = parse_utc_timestamp(f"{session_date}T{cal['observed_open_utc']}Z")
        close_ts = parse_utc_timestamp(f"{session_date}T{cal['observed_close_utc']}Z")
        window = group[(group["ts"] >= open_ts) & (group["ts"] <= close_ts)].copy()
        if window.empty:
            summaries[(str(ticker), str(session_date))] = {
                "ticker": str(ticker),
                "session_date": str(session_date),
                "session_window_rows": 0,
                "unique_bar_timestamps": 0,
                "first_bar_utc": None,
                "last_bar_utc": None,
                "required_intraday_fields_present": False,
                "duplicate_group_count": 0,
                "conflicting_duplicate_group_count": 0,
                "source_duplicate_evidence_count": 0,
            }
            continue
        duplicate_group_count = 0
        conflicting_duplicate_group_count = 0
        for _, ts_group in window.groupby("ts", sort=True):
            if len(ts_group) > 1:
                duplicate_group_count += 1
                signatures = {state_signature(row) for _, row in ts_group.iterrows()}
                if len(signatures) > 1:
                    conflicting_duplicate_group_count += 1
        unique_times = sorted(pd.Timestamp(value) for value in window["ts"].dropna().unique())
        fields_present = bool(window[["open", "high", "low", "close", "volume"]].notna().all(axis=None))
        summaries[(str(ticker), str(session_date))] = {
            "ticker": str(ticker),
            "session_date": str(session_date),
            "session_window_rows": int(len(window)),
            "unique_bar_timestamps": int(len(unique_times)),
            "first_bar_utc": unique_times[0] if unique_times else None,
            "last_bar_utc": unique_times[-1] if unique_times else None,
            "required_intraday_fields_present": fields_present,
            "duplicate_group_count": int(duplicate_group_count),
            "conflicting_duplicate_group_count": int(conflicting_duplicate_group_count),
            "source_duplicate_evidence_count": int(duplicate_group_count),
        }
    return summaries, rows


def evaluate_instruments(
    *,
    pool_instruments: list[dict[str, Any]],
    session_dates: list[str],
    daily: pd.DataFrame,
    intraday_summaries: dict[tuple[str, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    daily_by_key, daily_by_ticker = daily_maps(daily)
    instrument_rows: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    for pool_item in pool_instruments:
        ticker = str(pool_item["ticker"])
        pool_instrument_id = str(pool_item["instrument_id"])
        ticker_daily_rows = daily_by_ticker.get(ticker, [])
        daily_instrument_id, identity_resolved, identity_ambiguous, identity_count = resolve_instrument_id(ticker_daily_rows)
        identity_matches_pool = bool(identity_resolved and daily_instrument_id == pool_instrument_id)
        eligible_session_count = 0
        daily_linked_count = 0
        intraday_linked_count = 0
        prior20_count = 0
        required_field_count = 0
        duplicate_group_count = 0
        for session_date in session_dates:
            daily_rows = daily_by_key.get((ticker, session_date), [])
            daily_row = daily_rows[0] if daily_rows else None
            intraday_summary = intraday_summaries.get((ticker, session_date))
            daily_linked = bool(
                daily_row
                and daily_row.get("instrument_id")
                and daily_row.get("open_present")
                and daily_row.get("prior_close_present")
                and daily_row.get("volume_present")
            )
            prior_count = prior_volume_count(ticker_daily_rows, session_date)
            prior_ok = prior_count >= 20
            intraday_linked = bool(intraday_summary and int(intraday_summary.get("unique_bar_timestamps", 0)) > 0)
            required_intraday_fields_present = bool(
                intraday_summary and intraday_summary.get("required_intraday_fields_present") is True
            )
            required_fields_present = bool(daily_linked and required_intraday_fields_present)
            eligible_session = bool(identity_matches_pool and daily_linked and intraday_linked and prior_ok and required_fields_present)
            daily_linked_count += int(daily_linked)
            intraday_linked_count += int(intraday_linked)
            prior20_count += int(prior_ok)
            required_field_count += int(required_fields_present)
            duplicate_group_count += int(intraday_summary.get("duplicate_group_count", 0)) if intraday_summary else 0
            eligible_session_count += int(eligible_session)
            coverage_rows.append(
                {
                    "ticker": ticker,
                    "instrument_id": pool_instrument_id,
                    "session_date": session_date,
                    "identity_matches_pool": identity_matches_pool,
                    "daily_row_present": bool(daily_row),
                    "daily_linked": daily_linked,
                    "prior_20_daily_volume_rows": prior_count,
                    "prior_20_daily_volume_coverage_available": prior_ok,
                    "intraday_feasibility_alias": "013_ohlcv_1m_quote_guarded",
                    "intraday_session_present": intraday_linked,
                    "intraday_session_window_rows": int(intraday_summary.get("session_window_rows", 0)) if intraday_summary else 0,
                    "intraday_unique_bar_timestamps": int(intraday_summary.get("unique_bar_timestamps", 0)) if intraday_summary else 0,
                    "first_bar_utc": intraday_summary.get("first_bar_utc") if intraday_summary else None,
                    "last_bar_utc": intraday_summary.get("last_bar_utc") if intraday_summary else None,
                    "required_core_four_source_fields_present": required_fields_present,
                    "duplicate_group_count": int(intraday_summary.get("duplicate_group_count", 0)) if intraday_summary else 0,
                    "conflicting_duplicate_group_count": int(intraday_summary.get("conflicting_duplicate_group_count", 0)) if intraday_summary else 0,
                    "source_coverage_status": "PASS" if eligible_session else "BLOCKED_SOURCE_SESSION_COVERAGE",
                    "finding": "daily, prior-20 and intraday feasibility coverage present for governed session"
                    if eligible_session
                    else "missing daily, prior-20, identity or intraday feasibility coverage for governed session",
                }
            )
        status = "ELIGIBLE_FOR_SCALE_B_SAMPLE" if eligible_session_count == len(session_dates) else "NOT_ELIGIBLE_FOR_SCALE_B_SAMPLE"
        doc = {
            "ticker": ticker,
            "instrument_id": pool_instrument_id,
            "source_pool_rank": int(pool_item["source_pool_rank"]),
            "daily_instrument_id": daily_instrument_id,
            "identity_resolved": identity_resolved,
            "identity_ambiguous": identity_ambiguous,
            "identity_count": identity_count,
            "identity_matches_pool": identity_matches_pool,
            "daily_linked_session_count": daily_linked_count,
            "intraday_linked_session_count": intraday_linked_count,
            "prior_20_daily_volume_complete_session_count": prior20_count,
            "required_field_complete_session_count": required_field_count,
            "eligible_session_count": eligible_session_count,
            "duplicate_group_count": duplicate_group_count,
            "instrument_selection_status": status,
            "selection_rank": "",
            "selected_for_scale_b_sample": False,
            "finding": "eligible across all governed Scale B sessions"
            if status == "ELIGIBLE_FOR_SCALE_B_SAMPLE"
            else "not eligible across all governed Scale B sessions",
        }
        instrument_rows.append(doc)
        if status == "ELIGIBLE_FOR_SCALE_B_SAMPLE":
            candidate_rows.append(doc)
    ranked = sorted(
        candidate_rows,
        key=lambda row: (
            -int(row["eligible_session_count"]),
            -int(row["daily_linked_session_count"]),
            -int(row["intraday_linked_session_count"]),
            -int(row["prior_20_daily_volume_complete_session_count"]),
            int(row["duplicate_group_count"]),
            int(row["source_pool_rank"]),
            str(row["instrument_id"]),
            str(row["ticker"]),
        ),
    )
    for rank, row in enumerate(ranked, start=1):
        for target in instrument_rows:
            if target["ticker"] == row["ticker"]:
                target["selection_rank"] = rank
                break
    return instrument_rows, coverage_rows, ranked


def build_contexts(
    *,
    scope: dict[str, Any],
    selected_instruments: list[dict[str, Any]],
    calendar_rows: list[dict[str, Any]],
    intraday_summaries: dict[tuple[str, str], dict[str, Any]],
    coverage_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    shape = scope["target_sample_shape"]
    allocation = shape["context_allocation"]
    calendar_by_date = {row["session_date"]: row for row in calendar_rows}
    session_dates = [row["session_date"] for row in calendar_rows]
    coverage_pass = {(row["ticker"], row["session_date"]): row["source_coverage_status"] == "PASS" for row in coverage_rows}
    selected = selected_instruments[: int(scope["eligible_instrument_seed_pool"]["selected_instruments_required"])]
    if len(selected) < int(scope["eligible_instrument_seed_pool"]["selected_instruments_required"]):
        return []
    rows: list[dict[str, Any]] = []
    context_index = 0

    def add_context(
        *,
        instrument: dict[str, Any],
        session_date: str,
        decision_case_family: str,
        decision_case: str,
        decision_timestamp: pd.Timestamp,
        expected_context_outcome: str,
        expected_materialized_as_row: bool,
        selection_stratum: str,
        selection_reason: str,
        after_last_sampled_bar_semantics: str = "",
    ) -> None:
        nonlocal context_index
        cal = calendar_by_date[session_date]
        summary = intraday_summaries.get((instrument["ticker"], session_date), {})
        context_index += 1
        rows.append(
            {
                "sample_context_id": f"scale_b_context_{context_index:04d}",
                "instrument_id": instrument["instrument_id"],
                "ticker": instrument["ticker"],
                "session_date": session_date,
                "decision_timestamp_utc": decision_timestamp.isoformat().replace("+00:00", "Z"),
                "decision_case": decision_case,
                "decision_case_family": decision_case_family,
                "exchange": "XNYS",
                "calendar_id": cal.get("calendar_id", ""),
                "calendar_version": cal.get("calendar_version", ""),
                "regular_open_utc": cal["observed_open_utc"],
                "regular_close_utc": cal["observed_close_utc"],
                "session_type": cal["observed_session_type"],
                "early_close": cal["observed_early_close"],
                "holiday_or_closed": cal["holiday_or_closed"],
                "calendar_compatibility_status": "PASS_GOVERNED_CALENDAR",
                "calendar_stratum": cal["stratum"],
                "source_coverage_status": "PASS" if coverage_pass.get((instrument["ticker"], session_date)) else "BLOCKED_SOURCE_SESSION_COVERAGE",
                "source_coverage_evidence_alias": "013_ohlcv_1m_quote_guarded",
                "intraday_first_bar_utc": summary.get("first_bar_utc"),
                "intraday_last_bar_utc": summary.get("last_bar_utc"),
                "selection_stratum": selection_stratum,
                "selection_reason": selection_reason,
                "expected_context_outcome": expected_context_outcome,
                "expected_materialized_as_row": expected_materialized_as_row,
                "after_last_sampled_bar_semantics": after_last_sampled_bar_semantics,
                "fixed_utc_probe_calendar_as_current_authority": False,
            }
        )

    for instrument in selected:
        for session_date in session_dates:
            summary = intraday_summaries.get((instrument["ticker"], session_date))
            if not summary or summary.get("first_bar_utc") is None:
                return []
            add_context(
                instrument=instrument,
                session_date=session_date,
                decision_case_family="instrument_session_core_context",
                decision_case="first_observable_bar_governed_session",
                decision_timestamp=pd.Timestamp(summary["first_bar_utc"]),
                expected_context_outcome="INTEGRABLE_COMPLETE_OR_WITH_RESTRICTIONS",
                expected_materialized_as_row=True,
                selection_stratum="instrument_session_core_context",
                selection_reason="one governed-session first-observable context for every selected instrument-session pair",
            )
            if len(rows) == int(allocation["instrument_session_core_contexts"]):
                break
        if len(rows) == int(allocation["instrument_session_core_contexts"]):
            break
    if len(rows) != int(allocation["instrument_session_core_contexts"]):
        return []

    first_session = session_dates[0]
    for instrument in selected:
        summary = intraday_summaries.get((instrument["ticker"], first_session))
        if not summary or summary.get("first_bar_utc") is None:
            return []
        decision_timestamp = pd.Timestamp(summary["first_bar_utc"]) - pd.Timedelta(seconds=1)
        add_context(
            instrument=instrument,
            session_date=first_session,
            decision_case_family="pre_bar_expected_blocked_context",
            decision_case="before_first_observable_bar_governed_session",
            decision_timestamp=decision_timestamp,
            expected_context_outcome="REJECTED_REQUIRED_OBJECT_BLOCKED",
            expected_materialized_as_row=False,
            selection_stratum="pre_bar_expected_blocked_context",
            selection_reason="one pre-first-observable context per selected instrument",
        )
    if len([row for row in rows if row["decision_case_family"] == "pre_bar_expected_blocked_context"]) != int(
        allocation["pre_bar_expected_blocked_contexts"]
    ):
        return []

    after_session = session_dates[-1]
    for instrument in selected:
        summary = intraday_summaries.get((instrument["ticker"], after_session))
        if not summary or summary.get("last_bar_utc") is None:
            return []
        decision_timestamp = pd.Timestamp(summary["last_bar_utc"]) + pd.Timedelta(seconds=1)
        add_context(
            instrument=instrument,
            session_date=after_session,
            decision_case_family="after_last_sampled_bar_restricted_context",
            decision_case="after_last_sampled_bar_not_session_close",
            decision_timestamp=decision_timestamp,
            expected_context_outcome="INTEGRABLE_COMPLETE_OR_WITH_RESTRICTIONS",
            expected_materialized_as_row=True,
            selection_stratum="after_last_sampled_bar_restricted_context",
            selection_reason="one after-last-sampled-bar context per selected instrument; not promoted to session close",
            after_last_sampled_bar_semantics="not_session_close",
        )
    if len([row for row in rows if row["decision_case_family"] == "after_last_sampled_bar_restricted_context"]) != int(
        allocation["after_last_sampled_bar_restricted_contexts"]
    ):
        return []

    for idx, instrument in enumerate(selected):
        session_date = session_dates[idx % len(session_dates)]
        cal = calendar_by_date[session_date]
        decision_timestamp = parse_utc_timestamp(f"{session_date}T{cal['observed_close_utc']}Z")
        add_context(
            instrument=instrument,
            session_date=session_date,
            decision_case_family="calendar_boundary_stress_context",
            decision_case="governed_session_close_boundary",
            decision_timestamp=decision_timestamp,
            expected_context_outcome="INTEGRABLE_COMPLETE_OR_WITH_RESTRICTIONS",
            expected_materialized_as_row=True,
            selection_stratum="calendar_boundary_stress_context",
            selection_reason="governed session close boundary stress context including regular and early-close sessions",
        )
    if len([row for row in rows if row["decision_case_family"] == "calendar_boundary_stress_context"]) != int(
        allocation["calendar_boundary_stress_contexts"]
    ):
        return []
    return rows if len(rows) == int(shape["target_requested_contexts"]) else []


def build_duplicate_context_report(sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    context_counts = Counter(row["sample_context_id"] for row in sample_rows)
    semantic_counts = Counter(
        (
            row["instrument_id"],
            row["ticker"],
            row["session_date"],
            row["decision_timestamp_utc"],
            row["decision_case"],
        )
        for row in sample_rows
    )
    duplicate_context_ids = sum(count - 1 for count in context_counts.values() if count > 1)
    duplicate_semantic_contexts = sum(count - 1 for count in semantic_counts.values() if count > 1)
    rows: list[dict[str, Any]] = []
    if not sample_rows:
        rows.append(
            {
                "check_name": "scale_b_sample_duplicate_contexts",
                "sample_context_id": "",
                "semantic_context_key": "",
                "duplicate_count": 0,
                "status": "NOT_APPLICABLE_SAMPLE_NOT_FROZEN",
                "finding": "no frozen sample rows were emitted because preflight blocked before sample freeze",
            }
        )
        return rows, duplicate_context_ids, duplicate_semantic_contexts
    for key, count in sorted(context_counts.items()):
        if count > 1:
            rows.append(
                {
                    "check_name": "sample_context_id",
                    "sample_context_id": key,
                    "semantic_context_key": "",
                    "duplicate_count": count - 1,
                    "status": "FAILED_DUPLICATE_CONTEXT_ID",
                    "finding": "duplicate sample_context_id detected",
                }
            )
    for key, count in sorted(semantic_counts.items()):
        if count > 1:
            rows.append(
                {
                    "check_name": "semantic_context",
                    "sample_context_id": "",
                    "semantic_context_key": canonical_json(key, ensure_ascii=False),
                    "duplicate_count": count - 1,
                    "status": "FAILED_DUPLICATE_SEMANTIC_CONTEXT",
                    "finding": "duplicate semantic context detected",
                }
            )
    if not rows:
        rows.append(
            {
                "check_name": "scale_b_sample_duplicate_contexts",
                "sample_context_id": "",
                "semantic_context_key": "",
                "duplicate_count": 0,
                "status": "PASS",
                "finding": "no duplicate context ids or duplicate semantic contexts detected",
            }
        )
    return rows, duplicate_context_ids, duplicate_semantic_contexts


def decide_status(summary: dict[str, Any]) -> str:
    if summary["authority_failures"] > 0:
        return "FAILED_AUTHORITY_BOUNDARY"
    if summary["contract_failures"] > 0:
        return "FAILED_CONTRACT"
    if summary["calendar_session_boundary_mismatches"] > 0 or summary["selected_sessions"] != summary["required_sessions"]:
        return "BLOCKED_CALENDAR_SESSION_PLAN"
    if summary["eligible_instruments"] < summary["required_instruments"]:
        return "BLOCKED_INSTRUMENT_COVERAGE"
    if summary["sample_manifest_rows"] != summary["requested_contexts"]:
        return "BLOCKED_SAMPLE_CARDINALITY"
    if summary["source_coverage_failures"] > 0:
        return "BLOCKED_SOURCE_SESSION_COVERAGE"
    if summary["identity_failures"] > 0:
        return "BLOCKED_INSTRUMENT_COVERAGE"
    if summary["duplicate_context_ids"] > 0 or summary["duplicate_semantic_contexts"] > 0:
        return "FAILED_CONTRACT"
    if summary["stratification_failures"] > 0:
        return "BLOCKED_SAMPLE_CARDINALITY"
    if summary["estimated_total_source_rows"] > summary["maximum_total_source_rows_read_for_preflight"]:
        return "BLOCKED_SOURCE_SESSION_COVERAGE"
    return "PASS_WITH_RESTRICTIONS"


def write_readout(path: Path, *, run_id: str, summary: dict[str, Any], run_dir: Path) -> None:
    status = summary["preflight_status"]
    lines = [
        "# Experimental Core Four Market State Scale B Sample Preflight Readout v0.1",
        "",
        f"run_id = `{run_id}`",
        f"script_version = `{SCRIPT_VERSION}`",
        "",
        "## Decision",
        "",
        "```text",
        f"experimental_core_four_market_state_scale_b_sample_preflight = {status}",
        f"experimental_core_four_market_state_scale_b_execution = {summary['scale_b_execution_status']}",
        "official_market_state = NOT_OPEN",
        "production_builder = NOT_AUTHORIZED",
        "downstream_consumption = NOT_AUTHORIZED",
        "dataset_promotion = NOT_AUTHORIZED",
        "full_history_execution = NOT_AUTHORIZED",
        "full_universe_execution = NOT_AUTHORIZED",
        "```",
        "",
        "## Counts",
        "",
        "```text",
        f"requested_contexts = {summary['requested_contexts']}",
        f"sample_manifest_rows = {summary['sample_manifest_rows']}",
        f"selected_sessions = {summary['selected_sessions']}",
        f"calendar_session_boundary_mismatches = {summary['calendar_session_boundary_mismatches']}",
        f"fixed_utc_probe_calendar_as_current_authority = {summary['fixed_utc_probe_calendar_as_current_authority']}",
        f"required_instruments = {summary['required_instruments']}",
        f"seed_pool_instruments = {summary['seed_pool_instruments']}",
        f"eligible_instruments = {summary['eligible_instruments']}",
        f"selected_instruments = {summary['selected_instruments']}",
        f"expected_resolution_records = {summary['expected_resolution_records']}",
        f"expected_blocked_contexts = {summary['expected_blocked_contexts']}",
        f"expected_integrable_contexts = {summary['expected_integrable_contexts']}",
        f"estimated_daily_rows = {summary['estimated_daily_rows']}",
        f"estimated_intraday_rows = {summary['estimated_intraday_rows']}",
        f"estimated_total_source_rows = {summary['estimated_total_source_rows']}",
        f"source_coverage_failures = {summary['source_coverage_failures']}",
        f"duplicate_context_ids = {summary['duplicate_context_ids']}",
        f"duplicate_semantic_contexts = {summary['duplicate_semantic_contexts']}",
        f"identity_failures = {summary['identity_failures']}",
        f"stratification_failures = {summary['stratification_failures']}",
        f"hard_preflight_failures = {summary['hard_preflight_failures']}",
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "builders_executed = false",
        "resolution_records_emitted = 0",
        "market_state_integration_executed = false",
        "market_state_materialization_executed = false",
        "market_state_parquet_files_written = 0",
        "run_local_014_surface_construction = false",
        "013_direct_builder_input = false",
        "013_use = bounded_source_coverage_feasibility_only",
        "```",
        "",
    ]
    if status == "PASS_WITH_RESTRICTIONS":
        lines.extend(
            [
                "## Frozen Sample",
                "",
                "```text",
                f"scale_b_sample_fingerprint = {summary['scale_b_sample_fingerprint']}",
                f"instrument_selection_fingerprint = {summary['instrument_selection_fingerprint']}",
                f"session_selection_fingerprint = {summary['session_selection_fingerprint']}",
                "```",
                "",
                "The preflight froze a governed-calendar Scale B sample. It did not authorize Scale B execution; the next gate must separately authorize builder/resolution execution and any run-local 014-derived execution surface needed for those builders.",
            ]
        )
    else:
        lines.extend(
            [
                "## Blocked",
                "",
                "The preflight did not freeze a Scale B sample. Builders, integration and materialization remain not started.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"Run directory: `{run_dir}`",
            "",
            "## Next Gate",
            "",
            "```text",
            "experimental_core_four_market_state_scale_b_execution_authorization = NOT_OPEN_NEXT_IF_PASS",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    run_root = integration_root / "runs"
    if not is_within_or_equal(run_root, integration_root):
        raise PreflightError(f"Output root must stay inside integration root: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{RUN_ID_PREFIX}_{timestamp}"
    run_dir = run_root / run_id
    if run_dir.exists():
        raise PreflightError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    if not is_within_or_equal(run_dir, workspace_root):
        raise PreflightError(f"Refusing to write outside workspace: {run_dir}")

    command_line = " ".join([str(Path(__file__).resolve()), "--scope", str(scope_path)])
    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

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
        "execution_class": "experimental_scale_b_sample_preflight",
        "input_scope_path": str(scope_path),
        "run_dir": str(run_dir),
        "expected_scope": "freeze 72 governed-calendar Scale B contexts only if calendar, identity and source coverage pass",
        "overwrite_policy": "refuse_existing_run_dir",
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "load_scope_and_sources",
            "pid": os.getpid(),
            "run_dir": str(run_dir),
        },
    )

    calendar, calendar_rows, calendar_report = load_calendar(scope, scope_dir)
    session_dates = [str(row["session_date"]) for row in calendar_rows if row.get("compatible") is True]
    pool_instruments, pool_report = load_eligible_pool(scope, scope_dir)
    registry_path, roots, registry = resolve_source_roots(scope, scope_dir)
    tickers = [item["ticker"] for item in pool_instruments]
    daily, daily_report = read_daily_source(roots["004_master_daily_table"], tickers, [row["session_date"] for row in calendar_rows])
    source_013_files, source_013_discovery_report = discover_013_files(
        roots["013_ohlcv_1m_quote_guarded"], tickers, [row["session_date"] for row in calendar_rows]
    )
    intraday, intraday_report = read_013_files(source_013_files, set(row["session_date"] for row in calendar_rows))
    existing_014_metadata = read_014_metadata(roots["014_master_intraday_bar_table_candidate"])
    total_source_rows = int(daily_report["rows_read"]) + int(intraday_report["rows_read"])

    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "build_preflight_reports",
            "pid": os.getpid(),
            "calendar_rows_read": calendar_report["calendar_rows_read"],
            "daily_rows_read": daily_report["rows_read"],
            "intraday_rows_read": intraday_report["rows_read"],
        },
    )

    intraday_summaries, _ = build_intraday_summaries(intraday, calendar_rows)
    instrument_rows, coverage_rows, ranked_candidates = evaluate_instruments(
        pool_instruments=pool_instruments,
        session_dates=[row["session_date"] for row in calendar_rows],
        daily=daily,
        intraday_summaries=intraday_summaries,
    )
    required_instruments = int(scope["eligible_instrument_seed_pool"]["selected_instruments_required"])
    selected_instruments = ranked_candidates[:required_instruments]
    selected_tickers = {row["ticker"] for row in selected_instruments}
    for row in instrument_rows:
        if row["ticker"] in selected_tickers:
            row["selected_for_scale_b_sample"] = True
            row["instrument_selection_status"] = "SELECTED_FOR_SCALE_B_SAMPLE"

    sample_rows = build_contexts(
        scope=scope,
        selected_instruments=selected_instruments,
        calendar_rows=calendar_rows,
        intraday_summaries=intraday_summaries,
        coverage_rows=coverage_rows,
    )
    if len(sample_rows) != int(scope["target_sample_shape"]["target_requested_contexts"]):
        sample_rows = []

    duplicate_rows, duplicate_context_ids, duplicate_semantic_contexts = build_duplicate_context_report(sample_rows)
    sample_family_counts = Counter(row.get("decision_case_family") for row in sample_rows)
    allocation = scope["target_sample_shape"]["context_allocation"]
    stratification_failures = 0
    if sample_rows:
        for family, expected in allocation.items():
            family_name = {
                "instrument_session_core_contexts": "instrument_session_core_context",
                "pre_bar_expected_blocked_contexts": "pre_bar_expected_blocked_context",
                "after_last_sampled_bar_restricted_contexts": "after_last_sampled_bar_restricted_context",
                "calendar_boundary_stress_contexts": "calendar_boundary_stress_context",
            }[family]
            stratification_failures += int(sample_family_counts.get(family_name, 0) != int(expected))
    else:
        stratification_failures = 1

    selected_coverage_keys = {(row["ticker"], row["session_date"]) for row in sample_rows}
    source_coverage_failures = sum(
        1
        for row in coverage_rows
        if (row["ticker"], row["session_date"]) in selected_coverage_keys and row["source_coverage_status"] != "PASS"
    )
    identity_failures = sum(1 for row in instrument_rows if row["selected_for_scale_b_sample"] and row["identity_matches_pool"] is not True)
    calendar_boundary_mismatches = sum(1 for row in calendar_rows if row.get("compatible") is not True)
    fixed_utc_authority_count = 0
    instrument_selection_fingerprint = sha256_payload(
        {
            "selected_instruments": [
                {"ticker": row["ticker"], "instrument_id": row["instrument_id"], "selection_rank": row["selection_rank"]}
                for row in instrument_rows
                if row["selected_for_scale_b_sample"]
            ],
            "seed_pool_fingerprint": pool_report["eligible_instrument_pool_fingerprint"],
        }
    )
    session_selection_fingerprint = sha256_payload(
        {
            "calendar_rows": calendar_rows,
            "accepted_calendar_binding_run": scope["calendar_binding"]["accepted_run_id"],
            "calendar_version": scope["calendar_binding"]["calendar_version"],
        }
    )
    scale_b_sample_fingerprint = sha256_payload(sample_rows) if sample_rows else ""

    summary: dict[str, Any] = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_id": scope["scope_id"],
        "source_binding_registry": str(registry_path),
        "source_binding_registry_id": registry.get("registry_id"),
        "accepted_calendar_binding_run_consumed": True,
        "accepted_calendar_binding_run_id": scope["calendar_binding"]["accepted_run_id"],
        "calendar_version": scope["calendar_binding"]["calendar_version"],
        "calendar_rows_read": int(calendar_report["calendar_rows_read"]),
        "calendar_session_boundary_mismatches": int(calendar_boundary_mismatches),
        "fixed_utc_probe_calendar_as_current_authority": fixed_utc_authority_count,
        "seed_pool_run_id": pool_report["pool_run_id"],
        "seed_pool_instruments": int(pool_report["eligible_instruments_available"]),
        "seed_pool_fingerprint": pool_report["eligible_instrument_pool_fingerprint"],
        "requested_contexts": int(scope["target_sample_shape"]["target_requested_contexts"]),
        "maximum_requested_contexts_respected": bool(
            len(sample_rows) <= int(scope["target_sample_shape"]["maximum_requested_contexts"])
        ),
        "sample_manifest_rows": len(sample_rows),
        "sample_freeze_status": "FROZEN" if sample_rows else "NOT_FROZEN_BLOCKED",
        "required_instruments": required_instruments,
        "eligible_instruments": len(ranked_candidates),
        "selected_instruments": len(selected_instruments) if sample_rows else 0,
        "required_sessions": int(scope["target_sample_shape"]["selected_sessions"]),
        "selected_sessions": len(session_dates),
        "expected_resolution_records": int(scope["target_sample_shape"]["target_resolution_records_if_later_executed"]),
        "expected_blocked_contexts": int(scope["target_sample_shape"]["expected_blocked_contexts"]),
        "expected_integrable_contexts": int(scope["target_sample_shape"]["target_integrable_contexts"]),
        "estimated_daily_rows": int(daily_report["rows_read"]),
        "estimated_intraday_rows": int(intraday_report["rows_read"]),
        "estimated_total_source_rows": total_source_rows,
        "maximum_total_source_rows_read_for_preflight": int(scope["limits"]["maximum_total_source_rows_read_for_preflight"]),
        "source_market_data_rows_read_mode": "bounded_returned_rows_not_filesystem_access_audit",
        "source_coverage_failures": int(source_coverage_failures),
        "duplicate_context_ids": duplicate_context_ids,
        "duplicate_semantic_contexts": duplicate_semantic_contexts,
        "identity_failures": int(identity_failures),
        "stratification_failures": int(stratification_failures),
        "authority_failures": 0,
        "contract_failures": 0,
        "instrument_selection_fingerprint": instrument_selection_fingerprint,
        "session_selection_fingerprint": session_selection_fingerprint,
        "scale_b_sample_fingerprint": scale_b_sample_fingerprint,
        "builders_executed": False,
        "resolution_records_emitted": 0,
        "market_state_integration_executed": False,
        "market_state_materialization_executed": False,
        "market_state_parquet_files_written": 0,
        "run_local_014_surface_construction": False,
        "013_direct_builder_input": False,
        "013_market_state_input": False,
        "official_market_state_authorized": False,
        "production_builder_authorized": False,
        "downstream_consumption_authorized": False,
        "dataset_promotion_authorized": False,
        "full_history_execution_authorized": False,
        "full_universe_execution_authorized": False,
    }
    summary["preflight_status"] = decide_status(summary)
    blocking_statuses = {
        "BLOCKED_SOURCE_SESSION_COVERAGE",
        "BLOCKED_INSTRUMENT_COVERAGE",
        "BLOCKED_CALENDAR_SESSION_PLAN",
        "BLOCKED_SAMPLE_CARDINALITY",
        "FAILED_AUTHORITY_BOUNDARY",
        "FAILED_CONTRACT",
    }
    summary["hard_preflight_failures"] = 1 if summary["preflight_status"] in blocking_statuses else 0
    summary["scale_b_execution_status"] = (
        "NOT_EXECUTED_READY_FOR_SEPARATE_GATE"
        if summary["preflight_status"] == "PASS_WITH_RESTRICTIONS"
        else "BLOCKED_NOT_STARTED"
    )

    write_json(run_dir / "scale_b_calendar_session_plan.json", {"run_id": run_id, "sessions": calendar_rows})
    write_csv_rows(
        run_dir / "scale_b_calendar_coverage_report.csv",
        [
            "session_date",
            "stratum",
            "expected_open_utc",
            "observed_open_utc",
            "expected_close_utc",
            "observed_close_utc",
            "expected_session_type",
            "observed_session_type",
            "expected_early_close",
            "observed_early_close",
            "holiday_or_closed",
            "calendar_version",
            "calendar_version_match",
            "calendar_id",
            "calendar_row_fingerprint",
            "calendar_boundary_match",
            "compatible",
            "evidence_source",
            "finding",
        ],
        calendar_rows,
    )
    write_csv_rows(
        run_dir / "scale_b_instrument_selection_report.csv",
        [
            "ticker",
            "instrument_id",
            "source_pool_rank",
            "daily_instrument_id",
            "identity_resolved",
            "identity_ambiguous",
            "identity_count",
            "identity_matches_pool",
            "daily_linked_session_count",
            "intraday_linked_session_count",
            "prior_20_daily_volume_complete_session_count",
            "required_field_complete_session_count",
            "eligible_session_count",
            "duplicate_group_count",
            "selection_rank",
            "selected_for_scale_b_sample",
            "instrument_selection_status",
            "finding",
        ],
        instrument_rows,
    )
    write_csv_rows(
        run_dir / "scale_b_source_coverage_preflight_report.csv",
        [
            "ticker",
            "instrument_id",
            "session_date",
            "identity_matches_pool",
            "daily_row_present",
            "daily_linked",
            "prior_20_daily_volume_rows",
            "prior_20_daily_volume_coverage_available",
            "intraday_feasibility_alias",
            "intraday_session_present",
            "intraday_session_window_rows",
            "intraday_unique_bar_timestamps",
            "first_bar_utc",
            "last_bar_utc",
            "required_core_four_source_fields_present",
            "duplicate_group_count",
            "conflicting_duplicate_group_count",
            "source_coverage_status",
            "finding",
        ],
        coverage_rows,
    )
    write_csv_rows(
        run_dir / "scale_b_context_plan_report.csv",
        [
            "sample_context_id",
            "instrument_id",
            "ticker",
            "session_date",
            "decision_timestamp_utc",
            "decision_case",
            "decision_case_family",
            "calendar_stratum",
            "session_type",
            "early_close",
            "source_coverage_status",
            "expected_context_outcome",
            "expected_materialized_as_row",
            "selection_stratum",
            "selection_reason",
        ],
        sample_rows,
    )
    write_csv_rows(
        run_dir / "scale_b_duplicate_context_report.csv",
        ["check_name", "sample_context_id", "semantic_context_key", "duplicate_count", "status", "finding"],
        duplicate_rows,
    )
    write_jsonl(run_dir / "scale_b_sample_manifest.jsonl", sample_rows)
    write_json(run_dir / "scale_b_sample_summary.json", summary)
    authority_report = {
        "run_id": run_id,
        "authority": scope["authority"],
        "forbidden_authority_preserved": True,
        "builders_executed": False,
        "resolution_records_emitted": 0,
        "market_state_integration_executed": False,
        "market_state_materialization_executed": False,
        "market_state_parquet_files_written": 0,
        "run_local_014_surface_construction": False,
        "013_direct_builder_input": False,
        "013_use": "bounded_source_coverage_feasibility_only",
        "source_reports": {
            "004_master_daily_table": daily_report,
            "013_ohlcv_1m_quote_guarded_discovery": source_013_discovery_report,
            "013_ohlcv_1m_quote_guarded_read": intraday_report,
            "014_master_intraday_bar_table_candidate_metadata": existing_014_metadata,
            "governed_calendar": calendar_report,
            "eligible_pool": pool_report,
        },
    }
    write_json(run_dir / "scale_b_authority_report.json", authority_report)
    final_manifest = {
        "run_id": run_id,
        "completed_at_utc": utc_now(),
        "script_version": SCRIPT_VERSION,
        "status": summary["preflight_status"],
        "summary": summary,
        "fingerprints": {
            "instrument_selection_fingerprint": instrument_selection_fingerprint,
            "session_selection_fingerprint": session_selection_fingerprint,
            "scale_b_sample_fingerprint": scale_b_sample_fingerprint,
        },
        "authority_boundary": {
            "builders_executed": False,
            "resolution_records_emitted": 0,
            "market_state_integration_executed": False,
            "market_state_materialization_executed": False,
            "market_state_parquet_files_written": 0,
            "run_local_014_surface_construction": False,
            "013_direct_builder_input": False,
            "official_market_state": "NOT_OPEN",
            "production_builder": "NOT_AUTHORIZED",
            "downstream_consumption": "NOT_AUTHORIZED",
            "dataset_promotion": "NOT_AUTHORIZED",
            "full_history_execution": "NOT_AUTHORIZED",
            "full_universe_execution": "NOT_AUTHORIZED",
        },
        "outputs": {name: str(run_dir / name) for name in scope["required_preflight_outputs"] if not name.endswith(".md")},
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "complete" if summary["preflight_status"] == "PASS_WITH_RESTRICTIONS" else "blocked",
            "stage": "final",
            "pid": os.getpid(),
            "preflight_status": summary["preflight_status"],
        },
    )
    readout_path = integration_root / "experimental_core_four_market_state_scale_b_sample_preflight_readout_v0_1.md"
    write_readout(readout_path, run_id=run_id, summary=summary, run_dir=run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
