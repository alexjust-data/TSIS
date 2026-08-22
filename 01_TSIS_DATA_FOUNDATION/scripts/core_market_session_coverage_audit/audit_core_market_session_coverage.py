"""Corrected session-date coverage audit for the TSIS core market RAW families.

The source physical audit remains immutable.  This auditor reuses its committed
task artifacts, normalizes minute aggregates from UTC to America/New_York, and
persists factual observed absences separately from their diagnostic class.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import time
import traceback
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import quote
from zoneinfo import ZoneInfo

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml


FAMILIES = (
    "ohlcv_daily",
    "ohlcv_1m",
    "quotes_",
    "trades_ticks_prod_2005_2026",
)
NY = ZoneInfo("America/New_York")
UTC = timezone.utc

SESSION_DATE_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("session_date_et", pa.date32()),
    ]
)

PRESENCE_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("session_date_et", pa.date32()),
        ("ohlcv_daily_present", pa.bool_()),
        ("ohlcv_1m_present", pa.bool_()),
        ("quotes_present", pa.bool_()),
        ("trades_present", pa.bool_()),
        ("available_family_count", pa.int8()),
        ("present_family_count", pa.int8()),
        ("source_pending_families_json", pa.string()),
        ("deferred_families_json", pa.string()),
    ]
)

GAP_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("session_date_et", pa.date32()),
        ("missing_family", pa.string()),
        ("present_families_json", pa.string()),
        ("gap_class", pa.string()),
        ("diagnostic_confidence", pa.string()),
        ("source_shard_expected", pa.string()),
        ("source_shard_exists", pa.bool_()),
        ("requires_vendor_reconciliation", pa.bool_()),
        ("evidence_reference", pa.string()),
    ]
)

WINDOW_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("family", pa.string()),
        ("source_state", pa.string()),
        ("date_count", pa.int32()),
        ("first_session_date_et", pa.date32()),
        ("last_session_date_et", pa.date32()),
        ("scope_start_inclusive", pa.date32()),
        ("scope_end_inclusive", pa.date32()),
        ("leading_unverified_start", pa.date32()),
        ("leading_unverified_end", pa.date32()),
        ("trailing_unverified_start", pa.date32()),
        ("trailing_unverified_end", pa.date32()),
        ("leading_boundary_state", pa.string()),
        ("trailing_boundary_state", pa.string()),
        ("observed_absence_count", pa.int32()),
        ("absence_within_observed_window_count", pa.int32()),
        ("physical_error_file_count", pa.int32()),
        ("gap_classes_json", pa.string()),
    ]
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def stable_json_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(raw.encode("utf-8"))


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    with partial.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def atomic_write_table(path: Path, table: pa.Table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    pq.write_table(table, partial, compression="zstd")
    with partial.open("rb+") as handle:
        os.fsync(handle.fileno())
    os.replace(partial, path)


def table_from_rows(rows: Sequence[dict[str, Any]], schema: pa.Schema) -> pa.Table:
    return pa.Table.from_pylist(list(rows), schema=schema)


def safe_ticker(ticker: str) -> str:
    return quote(ticker, safe="._-")


def parse_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def family_presence_column(family: str) -> str:
    return {
        "ohlcv_daily": "ohlcv_daily_present",
        "ohlcv_1m": "ohlcv_1m_present",
        "quotes_": "quotes_present",
        "trades_ticks_prod_2005_2026": "trades_present",
    }[family]


def load_config(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    config = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Config must be a mapping")
    if tuple(config.get("families", {})) != FAMILIES:
        raise ValueError(f"families must be ordered exactly as {FAMILIES}")
    parse_date(str(config["scope"]["start_date_inclusive"]))
    parse_date(str(config["scope"]["end_date_inclusive"]))
    return config, sha256_bytes(raw)


def load_universe(config: dict[str, Any]) -> list[str]:
    spec = config["universe"]
    path = Path(str(spec["path"]))
    column = str(spec["ticker_column"])
    table = pq.ParquetFile(path).read(columns=[column])
    tickers = [str(value) for value in table.column(column).to_pylist() if value is not None]
    if len(tickers) != len(set(tickers)):
        raise ValueError("Governed universe contains duplicate ticker strings")
    expected = int(config["scope"]["expected_universe_members"])
    if len(tickers) != expected:
        raise ValueError(f"Governed universe cardinality is {len(tickers)}, expected {expected}")
    if "NA" not in tickers:
        raise ValueError("Literal ticker NA was not preserved")
    return sorted(tickers)


def select_tickers(config: dict[str, Any], universe: Sequence[str], mode: str, explicit: str) -> list[str]:
    if mode == "full":
        if explicit:
            raise ValueError("Full mode cannot override the governed universe")
        return list(universe)
    requested = [value.strip() for value in explicit.split(",") if value.strip()]
    if not requested:
        requested = [str(value) for value in config["probe"]["tickers"]]
    missing = sorted(set(requested) - set(universe))
    if missing:
        raise ValueError(f"Probe tickers outside governed universe: {missing}")
    return list(dict.fromkeys(requested))


def parse_deferred_families(explicit: str) -> tuple[str, ...]:
    requested = tuple(dict.fromkeys(value.strip() for value in explicit.split(",") if value.strip()))
    unknown = sorted(set(requested) - set(FAMILIES))
    if unknown:
        raise ValueError(f"Unknown deferred families: {unknown}")
    if len(requested) == len(FAMILIES):
        raise ValueError("At least one family must remain in the comparison")
    return requested


def source_task_paths(source_run: Path, family: str, ticker: str) -> dict[str, Path]:
    safe = safe_ticker(ticker)
    return {
        "manifest": source_run / "00_control" / "task_results" / family / f"ticker={safe}.json",
        "dates": source_run / "02_ticker_coverage" / family / f"ticker={safe}" / "ticker_dates.parquet",
        "inventory": source_run / "01_inventory" / family / f"ticker={safe}" / "inventory.parquet",
    }


def read_source_ledger_status(source_run: Path, family: str, ticker: str) -> str:
    ledger = source_run / "00_control" / "run_state.sqlite"
    uri = f"file:{ledger.as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=60)
    try:
        row = connection.execute(
            "SELECT status FROM tasks WHERE family=? AND ticker=?", (family, ticker)
        ).fetchone()
        return str(row[0]) if row else "missing"
    finally:
        connection.close()


def source_snapshot(
    config: dict[str, Any], ticker: str, deferred_families: Sequence[str] = ()
) -> dict[str, Any]:
    source_run = Path(str(config["source_audit"]["run_root"]))
    deferred = set(deferred_families)
    families: dict[str, Any] = {}
    for family in FAMILIES:
        paths = source_task_paths(source_run, family, ticker)
        if family in deferred:
            families[family] = {
                "ledger_status": "deferred",
                "manifest_path": str(paths["manifest"]),
                "manifest_sha256": None,
                "date_artifact_path": str(paths["dates"]),
                "date_artifact_bytes": None,
                "source_state": "DEFERRED_BY_RUN_CONTRACT",
                "date_artifact_sha256": None,
                "physical_error_file_count": None,
                "source_file_count": None,
            }
            continue
        ledger_status = read_source_ledger_status(source_run, family, ticker)
        record: dict[str, Any] = {
            "ledger_status": ledger_status,
            "manifest_path": str(paths["manifest"]),
            "manifest_sha256": sha256_file(paths["manifest"]) if paths["manifest"].is_file() else None,
            "date_artifact_path": str(paths["dates"]),
            "date_artifact_bytes": paths["dates"].stat().st_size if paths["dates"].is_file() else None,
        }
        if ledger_status == "committed" and paths["manifest"].is_file() and paths["dates"].is_file():
            payload = json.loads(paths["manifest"].read_text(encoding="utf-8"))
            record["source_state"] = "COMMITTED"
            record["date_artifact_sha256"] = sha256_file(paths["dates"])
            record["physical_error_file_count"] = int(payload.get("error_file_count", 0))
            record["source_file_count"] = int(payload.get("file_count", 0))
        elif ledger_status in {"pending", "running"}:
            record["source_state"] = "SOURCE_PENDING"
            record["date_artifact_sha256"] = None
            record["physical_error_file_count"] = None
            record["source_file_count"] = None
        else:
            record["source_state"] = "SOURCE_UNAVAILABLE"
            record["date_artifact_sha256"] = None
            record["physical_error_file_count"] = None
            record["source_file_count"] = None
        families[family] = record
    return {"ticker": ticker, "families": families}


def load_source_dates(source_run: Path, family: str, ticker: str) -> set[date]:
    path = source_task_paths(source_run, family, ticker)["dates"]
    values = pq.ParquetFile(path).read(columns=["observed_date"]).column("observed_date").to_pylist()
    return {value for value in values if isinstance(value, date)}


def normalize_utc_hour_to_session_date(hour: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}", hour):
        raise ValueError(f"Invalid UTC hour token: {hour!r}")
    value = datetime.fromisoformat(f"{hour}:00:00+00:00")
    return value.astimezone(NY).date()


def normalize_ts_chunk(chunk: pa.Array) -> tuple[set[date], set[date], int]:
    """Return raw UTC dates, ET session dates, and invalid unique values."""
    raw_dates: set[date] = set()
    session_dates: set[date] = set()
    invalid = 0
    hours = pc.unique(pc.utf8_slice_codeunits(chunk, start=0, stop=13)).to_pylist()
    for value in hours:
        if value is None:
            invalid += 1
            continue
        text = str(value)
        try:
            raw_dates.add(date.fromisoformat(text[:10]))
            session_dates.add(normalize_utc_hour_to_session_date(text))
        except ValueError:
            invalid += 1
    return raw_dates, session_dates, invalid


def minute_shard_key(path: Path) -> tuple[int, int] | None:
    normalized = str(path).replace("\\", "/")
    match = re.search(r"/year=(\d{4})/month=(\d{1,2})/", normalized)
    return (int(match.group(1)), int(match.group(2))) if match else None


def normalize_minute_ticker(
    config: dict[str, Any], ticker: str, scope_start: date, scope_end: date
) -> tuple[set[date], set[date], set[tuple[int, int]], dict[str, Any]]:
    source_run = Path(str(config["source_audit"]["run_root"]))
    inventory = source_task_paths(source_run, "ohlcv_1m", ticker)["inventory"]
    table = pq.ParquetFile(inventory).read(columns=["absolute_path", "error_class"])
    raw_dates: set[date] = set()
    session_dates: set[date] = set()
    shards: set[tuple[int, int]] = set()
    invalid_unique_tokens = 0
    rows_read = 0
    bytes_read = 0
    files_read = 0
    for row in table.to_pylist():
        if row.get("error_class"):
            raise ValueError(f"Minute source inventory has a physical error: {row}")
        path = Path(str(row["absolute_path"]))
        key = minute_shard_key(path)
        if key is not None:
            shards.add(key)
        parquet = pq.ParquetFile(path)
        bytes_read += path.stat().st_size
        files_read += 1
        if "ts_utc" not in parquet.schema_arrow.names:
            raise ValueError(f"ts_utc missing from {path}")
        for row_group in range(parquet.metadata.num_row_groups):
            array = parquet.read_row_group(row_group, columns=["ts_utc"]).column("ts_utc")
            rows_read += len(array)
            for chunk in array.chunks:
                raw, sessions, invalid = normalize_ts_chunk(chunk)
                raw_dates.update(raw)
                session_dates.update(sessions)
                invalid_unique_tokens += invalid
    if invalid_unique_tokens:
        raise ValueError(f"Ticker {ticker}: {invalid_unique_tokens} invalid unique ts_utc tokens")
    raw_dates = {value for value in raw_dates if scope_start <= value <= scope_end}
    session_dates = {value for value in session_dates if scope_start <= value <= scope_end}
    source_raw_dates = load_source_dates(source_run, "ohlcv_1m", ticker)
    if raw_dates != source_raw_dates:
        only_derived = sorted(raw_dates - source_raw_dates)[:20]
        only_source = sorted(source_raw_dates - raw_dates)[:20]
        raise ValueError(
            f"Minute UTC-date reconstruction mismatch for {ticker}: "
            f"only_derived={only_derived} only_source={only_source}"
        )
    stats = {
        "files_read": files_read,
        "source_bytes_read": bytes_read,
        "minute_rows_read": rows_read,
        "raw_utc_date_count": len(raw_dates),
        "session_date_et_count": len(session_dates),
        "raw_only_date_count_after_normalization": len(raw_dates - session_dates),
        "session_only_date_count_after_normalization": len(session_dates - raw_dates),
    }
    return raw_dates, session_dates, shards, stats


def next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def expected_minute_shards(session_date: date) -> list[tuple[int, int]]:
    current = (session_date.year, session_date.month)
    following = next_month(*current)
    return [current, following] if (session_date + timedelta(days=1)).month != session_date.month else [current]


def classify_gap(
    *,
    missing_family: str,
    session_date: date,
    date_sets: dict[str, set[date]],
    minute_shards: set[tuple[int, int]],
) -> dict[str, Any]:
    values = date_sets[missing_family]
    first = min(values) if values else None
    last = max(values) if values else None
    expected_shard: str | None = None
    shard_exists: bool | None = None
    requires_vendor = True
    confidence = "CANDIDATE"

    if missing_family == "ohlcv_1m":
        expected = expected_minute_shards(session_date)
        expected_shard = json.dumps([f"year={y}/month={m:02d}" for y, m in expected])
        shard_exists = any(value in minute_shards for value in expected)
        if last is not None and session_date > last:
            gap_class = "DOWNLOAD_TAIL_MISSING"
            confidence = "CONFIRMED_LOCAL_ABSENCE"
        elif not shard_exists:
            gap_class = "MISSING_MONTH_SHARD"
            confidence = "CONFIRMED_LOCAL_ABSENCE"
        else:
            gap_class = "MISSING_INTRAMONTH_SESSION"
    elif not values:
        gap_class = "POSSIBLE_TICKER_REUSE_OR_IDENTITY_INTERVAL"
    elif first is not None and session_date < first:
        gap_class = "POSSIBLE_TICKER_REUSE_OR_IDENTITY_INTERVAL"
    elif last is not None and session_date > last:
        gap_class = "DOWNLOAD_TAIL_MISSING"
        confidence = "CONFIRMED_LOCAL_ABSENCE"
    elif missing_family == "trades_ticks_prod_2005_2026" and (
        session_date in date_sets["ohlcv_daily"] or session_date in date_sets["ohlcv_1m"]
    ):
        gap_class = "MISSING_INTRAMONTH_SESSION"
    else:
        gap_class = "PRODUCT_SEMANTIC_DIFFERENCE"
        confidence = "PRODUCT_DEPENDENT"
    return {
        "gap_class": gap_class,
        "diagnostic_confidence": confidence,
        "source_shard_expected": expected_shard,
        "source_shard_exists": shard_exists,
        "requires_vendor_reconciliation": requires_vendor,
    }


def boundary_fields(
    values: set[date], source_state: str, scope_start: date, scope_end: date
) -> dict[str, Any]:
    if source_state == "DEFERRED_BY_RUN_CONTRACT":
        return {
            "scope_start_inclusive": scope_start,
            "scope_end_inclusive": scope_end,
            "leading_unverified_start": None,
            "leading_unverified_end": None,
            "trailing_unverified_start": None,
            "trailing_unverified_end": None,
            "leading_boundary_state": "DEFERRED_NOT_EVALUATED",
            "trailing_boundary_state": "DEFERRED_NOT_EVALUATED",
        }
    if source_state != "COMMITTED":
        return {
            "scope_start_inclusive": scope_start,
            "scope_end_inclusive": scope_end,
            "leading_unverified_start": None,
            "leading_unverified_end": None,
            "trailing_unverified_start": None,
            "trailing_unverified_end": None,
            "leading_boundary_state": "SOURCE_PENDING_NOT_EVALUATED",
            "trailing_boundary_state": "SOURCE_PENDING_NOT_EVALUATED",
        }
    if not values:
        return {
            "scope_start_inclusive": scope_start,
            "scope_end_inclusive": scope_end,
            "leading_unverified_start": scope_start,
            "leading_unverified_end": scope_end,
            "trailing_unverified_start": scope_start,
            "trailing_unverified_end": scope_end,
            "leading_boundary_state": "NO_OBSERVED_ROWS_IN_SCOPE",
            "trailing_boundary_state": "NO_OBSERVED_ROWS_IN_SCOPE",
        }
    first = min(values)
    last = max(values)
    return {
        "scope_start_inclusive": scope_start,
        "scope_end_inclusive": scope_end,
        "leading_unverified_start": scope_start if first > scope_start else None,
        "leading_unverified_end": first - timedelta(days=1) if first > scope_start else None,
        "trailing_unverified_start": last + timedelta(days=1) if last < scope_end else None,
        "trailing_unverified_end": scope_end if last < scope_end else None,
        "leading_boundary_state": (
            "UNVERIFIED_BEFORE_FIRST_OBSERVED" if first > scope_start else "REACHES_SCOPE_START"
        ),
        "trailing_boundary_state": (
            "UNVERIFIED_AFTER_LAST_OBSERVED" if last < scope_end else "REACHES_SCOPE_END"
        ),
    }


def runtime_paths(run_root: Path) -> dict[str, Path]:
    return {
        "control": run_root / "00_control",
        "minute": run_root / "01_normalized_1m",
        "presence": run_root / "02_presence",
        "gaps": run_root / "03_gaps",
        "windows": run_root / "04_windows",
        "closeout": run_root / "05_closeout",
    }


def ensure_dirs(run_root: Path) -> dict[str, Path]:
    paths = runtime_paths(run_root)
    for value in paths.values():
        value.mkdir(parents=True, exist_ok=True)
    (paths["control"] / "task_results").mkdir(parents=True, exist_ok=True)
    return paths


def task_paths(run_root: Path, ticker: str) -> dict[str, Path]:
    paths = runtime_paths(run_root)
    safe = safe_ticker(ticker)
    return {
        "minute": paths["minute"] / f"ticker={safe}" / "session_dates_et.parquet",
        "presence": paths["presence"] / f"ticker={safe}" / "presence.parquet",
        "gaps": paths["gaps"] / f"ticker={safe}" / "gaps.parquet",
        "windows": paths["windows"] / f"ticker={safe}" / "windows.parquet",
        "manifest": paths["control"] / "task_results" / f"ticker={safe}.json",
    }


def connect_ledger(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=60)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    return connection


def initialize_ledger(path: Path, run_id: str, contract_hash: str, tickers: Sequence[str]) -> None:
    connection = connect_ledger(path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS run_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(
                ticker TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt INTEGER NOT NULL DEFAULT 0,
                worker_pid INTEGER,
                started_at_utc TEXT,
                ended_at_utc TEXT,
                source_snapshot_sha256 TEXT,
                files_read INTEGER,
                source_bytes_read INTEGER,
                minute_rows_read INTEGER,
                presence_rows INTEGER,
                gap_rows INTEGER,
                error_message TEXT
            );
            """
        )
        connection.execute("INSERT OR REPLACE INTO run_metadata VALUES('run_id',?)", (run_id,))
        connection.execute(
            "INSERT OR REPLACE INTO run_metadata VALUES('run_contract_sha256',?)", (contract_hash,)
        )
        connection.executemany(
            "INSERT OR IGNORE INTO tasks(ticker,status) VALUES(?,'pending')", [(t,) for t in tickers]
        )
        connection.commit()
    finally:
        connection.close()


def ledger_update(path: Path, ticker: str, status: str, **values: Any) -> None:
    allowed = {
        "worker_pid",
        "started_at_utc",
        "ended_at_utc",
        "source_snapshot_sha256",
        "files_read",
        "source_bytes_read",
        "minute_rows_read",
        "presence_rows",
        "gap_rows",
        "error_message",
    }
    unknown = set(values) - allowed
    if unknown:
        raise ValueError(f"Unsupported ledger fields: {unknown}")
    assignments = ["status=?"] + [f"{key}=?" for key in values]
    params = [status] + list(values.values()) + [ticker]
    connection = connect_ledger(path)
    try:
        connection.execute(f"UPDATE tasks SET {','.join(assignments)} WHERE ticker=?", params)
        if status == "running":
            connection.execute("UPDATE tasks SET attempt=attempt+1 WHERE ticker=?", (ticker,))
        connection.commit()
    finally:
        connection.close()


def ledger_snapshot(path: Path) -> dict[str, Any]:
    connection = connect_ledger(path)
    try:
        counts = {status: int(count) for status, count in connection.execute(
            "SELECT status,COUNT(*) FROM tasks GROUP BY status"
        )}
        totals = connection.execute(
            "SELECT COALESCE(SUM(files_read),0),COALESCE(SUM(source_bytes_read),0),"
            "COALESCE(SUM(minute_rows_read),0),COALESCE(SUM(presence_rows),0),"
            "COALESCE(SUM(gap_rows),0) FROM tasks WHERE status='committed'"
        ).fetchone()
        active = connection.execute(
            "SELECT ticker,worker_pid,started_at_utc FROM tasks WHERE status='running'"
        ).fetchone()
        return {
            "task_counts": counts,
            "files_read": int(totals[0]),
            "source_bytes_read": int(totals[1]),
            "minute_rows_read": int(totals[2]),
            "presence_rows": int(totals[3]),
            "gap_rows": int(totals[4]),
            "active_task": (
                {"ticker": active[0], "worker_pid": active[1], "started_at_utc": active[2]}
                if active else None
            ),
        }
    finally:
        connection.close()


def source_snapshot_hash(snapshot: dict[str, Any]) -> str:
    return stable_json_hash(snapshot)


def task_manifest_valid(run_root: Path, ticker: str, contract_hash: str, snapshot_hash: str) -> bool:
    manifest = task_paths(run_root, ticker)["manifest"]
    if not manifest.is_file():
        return False
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if payload.get("status") != "committed":
            return False
        if payload.get("run_contract_sha256") != contract_hash:
            return False
        if payload.get("source_snapshot_sha256") != snapshot_hash:
            return False
        for artifact in payload["artifacts"]:
            path = Path(str(artifact["path"]))
            if not path.is_file() or path.stat().st_size != int(artifact["bytes"]):
                return False
            if sha256_file(path) != artifact["sha256"]:
                return False
        return True
    except Exception:
        return False


def build_ticker_task(
    config: dict[str, Any], run_root: Path, ticker: str, run_id: str, contract_hash: str,
    snapshot: dict[str, Any]
) -> dict[str, Any]:
    started = utc_now()
    scope_start = parse_date(str(config["scope"]["start_date_inclusive"]))
    scope_end = parse_date(str(config["scope"]["end_date_inclusive"]))
    source_run = Path(str(config["source_audit"]["run_root"]))
    paths = task_paths(run_root, ticker)
    family_states = {family: snapshot["families"][family]["source_state"] for family in FAMILIES}

    date_sets: dict[str, set[date]] = {family: set() for family in FAMILIES}
    raw_minute_dates: set[date] = set()
    minute_shards: set[tuple[int, int]] = set()
    minute_stats = {"files_read": 0, "source_bytes_read": 0, "minute_rows_read": 0}
    for family in FAMILIES:
        if family_states[family] != "COMMITTED":
            continue
        if family == "ohlcv_1m":
            raw_minute_dates, sessions, minute_shards, minute_stats = normalize_minute_ticker(
                config, ticker, scope_start, scope_end
            )
            date_sets[family] = sessions
        else:
            date_sets[family] = load_source_dates(source_run, family, ticker)

    minute_rows = [{"ticker": ticker, "session_date_et": value} for value in sorted(date_sets["ohlcv_1m"])]
    atomic_write_table(paths["minute"], table_from_rows(minute_rows, SESSION_DATE_SCHEMA))

    available = [family for family in FAMILIES if family_states[family] == "COMMITTED"]
    pending = [
        family
        for family in FAMILIES
        if family_states[family] in {"SOURCE_PENDING", "SOURCE_UNAVAILABLE"}
    ]
    deferred = [
        family for family in FAMILIES if family_states[family] == "DEFERRED_BY_RUN_CONTRACT"
    ]
    union_dates = set().union(*(date_sets[family] for family in available)) if available else set()
    presence_rows: list[dict[str, Any]] = []
    gap_rows: list[dict[str, Any]] = []
    gap_counts: dict[str, Counter[str]] = {family: Counter() for family in FAMILIES}
    evidence = str(paths["manifest"])
    for session in sorted(union_dates):
        present = [family for family in available if session in date_sets[family]]
        row: dict[str, Any] = {
            "ticker": ticker,
            "session_date_et": session,
            "available_family_count": len(available),
            "present_family_count": len(present),
            "source_pending_families_json": json.dumps(pending),
            "deferred_families_json": json.dumps(deferred),
        }
        for family in FAMILIES:
            row[family_presence_column(family)] = (
                session in date_sets[family] if family in available else None
            )
        presence_rows.append(row)
        for missing_family in available:
            if session in date_sets[missing_family] or not present:
                continue
            diagnosis = classify_gap(
                missing_family=missing_family,
                session_date=session,
                date_sets=date_sets,
                minute_shards=minute_shards,
            )
            gap_counts[missing_family][diagnosis["gap_class"]] += 1
            gap_rows.append(
                {
                    "ticker": ticker,
                    "session_date_et": session,
                    "missing_family": missing_family,
                    "present_families_json": json.dumps(present),
                    **diagnosis,
                    "evidence_reference": evidence,
                }
            )
    atomic_write_table(paths["presence"], table_from_rows(presence_rows, PRESENCE_SCHEMA))
    atomic_write_table(paths["gaps"], table_from_rows(gap_rows, GAP_SCHEMA))

    window_rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        values = date_sets[family]
        absences = [row for row in gap_rows if row["missing_family"] == family]
        first = min(values) if values else None
        last = max(values) if values else None
        within = sum(bool(first and last and first <= row["session_date_et"] <= last) for row in absences)
        window_rows.append(
            {
                "ticker": ticker,
                "family": family,
                "source_state": family_states[family],
                "date_count": len(values),
                "first_session_date_et": first,
                "last_session_date_et": last,
                **boundary_fields(values, family_states[family], scope_start, scope_end),
                "observed_absence_count": len(absences),
                "absence_within_observed_window_count": within,
                "physical_error_file_count": snapshot["families"][family].get("physical_error_file_count"),
                "gap_classes_json": json.dumps(dict(sorted(gap_counts[family].items()))),
            }
        )
    atomic_write_table(paths["windows"], table_from_rows(window_rows, WINDOW_SCHEMA))

    artifacts = []
    for path in (paths["minute"], paths["presence"], paths["gaps"], paths["windows"]):
        artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    payload = {
        "run_id": run_id,
        "run_contract_sha256": contract_hash,
        "source_snapshot_sha256": source_snapshot_hash(snapshot),
        "source_snapshot": snapshot,
        "status": "committed",
        "ticker": ticker,
        "started_at_utc": iso_utc(started),
        "ended_at_utc": iso_utc(),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 3),
        "source_family_states": family_states,
        "date_counts": {family: len(date_sets[family]) for family in FAMILIES},
        "first_dates": {family: min(date_sets[family]).isoformat() if date_sets[family] else None for family in FAMILIES},
        "last_dates": {family: max(date_sets[family]).isoformat() if date_sets[family] else None for family in FAMILIES},
        "minute_normalization": minute_stats,
        "raw_minute_utc_date_count": len(raw_minute_dates),
        "presence_rows": len(presence_rows),
        "gap_rows": len(gap_rows),
        "gap_counts": {family: dict(sorted(value.items())) for family, value in gap_counts.items()},
        "artifacts": artifacts,
    }
    atomic_write_json(paths["manifest"], payload)
    return payload


def stream_consolidate(shards: Iterable[Path], destination: Path, schema: pa.Schema) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(f"{destination.name}.{os.getpid()}.{time.time_ns()}.partial")
    writer = pq.ParquetWriter(partial, schema=schema, compression="zstd")
    rows = 0
    try:
        for shard in shards:
            table = pq.ParquetFile(shard).read()
            if table.schema != schema:
                table = table.cast(schema)
            if table.num_rows:
                writer.write_table(table)
                rows += table.num_rows
    finally:
        writer.close()
    with partial.open("rb+") as handle:
        os.fsync(handle.fileno())
    os.replace(partial, destination)
    return rows


def aggregate_source_states(manifests: Sequence[dict[str, Any]]) -> dict[str, dict[str, int]]:
    result: dict[str, Counter[str]] = {family: Counter() for family in FAMILIES}
    for manifest in manifests:
        for family, state in manifest["source_family_states"].items():
            result[family][state] += 1
    return {family: dict(sorted(counts.items())) for family, counts in result.items()}


def finalize_run(config: dict[str, Any], run_root: Path, pre_manifest: dict[str, Any]) -> dict[str, Any]:
    tickers = [str(value) for value in pre_manifest["selected_tickers"]]
    comparison_families = [str(value) for value in pre_manifest["comparison_families"]]
    deferred_families = [str(value) for value in pre_manifest["deferred_families"]]
    paths = runtime_paths(run_root)
    manifests = [json.loads(task_paths(run_root, ticker)["manifest"].read_text(encoding="utf-8")) for ticker in tickers]
    outputs = {
        "minute": paths["closeout"] / "ohlcv_1m_session_dates_et.parquet",
        "presence": paths["closeout"] / "ticker_family_session_presence.parquet",
        "gaps": paths["closeout"] / "family_gap_ledger.parquet",
        "windows": paths["closeout"] / "ticker_family_windows.parquet",
    }
    row_counts = {
        "ohlcv_1m_session_dates_et": stream_consolidate(
            (task_paths(run_root, ticker)["minute"] for ticker in tickers), outputs["minute"], SESSION_DATE_SCHEMA
        ),
        "ticker_family_session_presence": stream_consolidate(
            (task_paths(run_root, ticker)["presence"] for ticker in tickers), outputs["presence"], PRESENCE_SCHEMA
        ),
        "family_gap_ledger": stream_consolidate(
            (task_paths(run_root, ticker)["gaps"] for ticker in tickers), outputs["gaps"], GAP_SCHEMA
        ),
        "ticker_family_windows": stream_consolidate(
            (task_paths(run_root, ticker)["windows"] for ticker in tickers), outputs["windows"], WINDOW_SCHEMA
        ),
    }

    gap_counts: Counter[tuple[str, str]] = Counter()
    for manifest in manifests:
        for family, classes in manifest["gap_counts"].items():
            for gap_class, count in classes.items():
                gap_counts[(family, gap_class)] += int(count)
    by_family_path = paths["closeout"] / "gap_summary_by_family.csv"
    with by_family_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["family", "observed_absence_count"])
        writer.writeheader()
        for family in FAMILIES:
            writer.writerow({"family": family, "observed_absence_count": sum(
                count for (candidate, _), count in gap_counts.items() if candidate == family
            )})
    by_class_path = paths["closeout"] / "gap_summary_by_class.csv"
    with by_class_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["family", "gap_class", "observed_absence_count"])
        writer.writeheader()
        for (family, gap_class), count in sorted(gap_counts.items()):
            writer.writerow({"family": family, "gap_class": gap_class, "observed_absence_count": count})

    source_states = aggregate_source_states(manifests)
    scope_end = parse_date(str(config["scope"]["end_date_inclusive"]))
    family_global_windows: dict[str, Any] = {}
    for family in FAMILIES:
        first_values = [
            parse_date(value)
            for manifest in manifests
            if manifest["source_family_states"][family] == "COMMITTED"
            for value in [manifest["first_dates"][family]]
            if value is not None
        ]
        last_values = [
            parse_date(value)
            for manifest in manifests
            if manifest["source_family_states"][family] == "COMMITTED"
            for value in [manifest["last_dates"][family]]
            if value is not None
        ]
        global_last = max(last_values) if last_values else None
        family_global_windows[family] = {
            "tickers_with_observed_dates": len(last_values),
            "global_first_session_date_et": min(first_values).isoformat() if first_values else None,
            "global_last_session_date_et": global_last.isoformat() if global_last else None,
            "scope_end_reached": bool(global_last is not None and global_last >= scope_end),
            "unverified_common_tail_start": (
                (global_last + timedelta(days=1)).isoformat()
                if global_last is not None and global_last < scope_end
                else None
            ),
            "unverified_common_tail_end": (
                scope_end.isoformat() if global_last is not None and global_last < scope_end else None
            ),
        }
    pending = sum(
        source_states[family].get("SOURCE_PENDING", 0)
        + source_states[family].get("SOURCE_UNAVAILABLE", 0)
        for family in comparison_families
    )
    technical_status = "PASS" if len(manifests) == len(tickers) else "FAIL"
    if pending:
        comparison_state = "PARTIAL_SOURCE_PENDING"
    elif deferred_families:
        comparison_state = "COMPARISON_COMPLETE_WITH_DEFERRED_FAMILIES"
    else:
        comparison_state = "FULL_COMPARISON_COMPLETE"
    if str(pre_manifest["mode"]) == "probe":
        dataset_certification = "NOT_GRANTED_PROBE"
    elif pending:
        dataset_certification = "NOT_GRANTED_SOURCE_PENDING"
    elif not all(family_global_windows[family]["scope_end_reached"] for family in comparison_families):
        dataset_certification = "NOT_GRANTED_SCOPE_END_NOT_REACHED"
    else:
        dataset_certification = "NOT_GRANTED_REQUIRES_GAP_ADJUDICATION"
    summary = {
        "run_id": pre_manifest["run_id"],
        "mode": pre_manifest["mode"],
        "technical_status": technical_status,
        "comparison_state": comparison_state,
        "comparison_families": comparison_families,
        "deferred_families": deferred_families,
        "dataset_certification": dataset_certification,
        "selected_ticker_count": len(tickers),
        "expected_ticker_count": int(config["scope"]["expected_universe_members"]),
        "source_family_states": source_states,
        "family_global_windows": family_global_windows,
        "row_counts": row_counts,
        "gap_counts": {f"{family}|{gap_class}": count for (family, gap_class), count in sorted(gap_counts.items())},
        "minute_files_read": sum(int(m["minute_normalization"]["files_read"]) for m in manifests),
        "minute_source_bytes_read": sum(int(m["minute_normalization"]["source_bytes_read"]) for m in manifests),
        "minute_rows_read": sum(int(m["minute_normalization"]["minute_rows_read"]) for m in manifests),
        "ended_at_utc": iso_utc(),
    }
    atomic_write_json(paths["closeout"] / "audit_summary.json", summary)
    report = "# Core Market Session Coverage Audit\n\n"
    report += f"- Run: `{pre_manifest['run_id']}`\n- Technical status: `{technical_status}`\n"
    report += f"- Comparison state: `{comparison_state}`\n- Tickers: `{len(tickers)}`\n"
    report += f"- Observed absences: `{row_counts['family_gap_ledger']}`\n\n"
    report += "`observed absence` is factual; the diagnostic class does not by itself prove a vendor omission. "
    report += "Rows from source tasks that were not committed were excluded and recorded as `SOURCE_PENDING`. "
    report += "Families deferred by the run contract were not read and are recorded as `DEFERRED_BY_RUN_CONTRACT`.\n"
    report_path = paths["closeout"] / "CORE_MARKET_SESSION_COVERAGE_AUDIT.md"
    atomic_write_text(report_path, report)
    artifacts = []
    for path in [
        *outputs.values(),
        by_family_path,
        by_class_path,
        paths["closeout"] / "audit_summary.json",
        report_path,
    ]:
        artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    final_manifest = {**summary, "artifacts": artifacts}
    atomic_write_json(paths["closeout"] / "final_manifest.json", final_manifest)
    return final_manifest


def write_heartbeat(run_root: Path, payload: dict[str, Any]) -> None:
    payload = {**payload, "observed_at_utc": iso_utc(), "active_pid": os.getpid()}
    atomic_write_json(runtime_paths(run_root)["control"] / "heartbeat.json", payload)


def prepare_pre_manifest(
    config: dict[str, Any], config_path: Path, config_hash: str, run_id: str, mode: str,
    universe: Sequence[str], selected: Sequence[str], deferred_families: Sequence[str]
) -> dict[str, Any]:
    source_run = Path(str(config["source_audit"]["run_root"]))
    source_pre = source_run / "00_control" / "pre_manifest.json"
    script_root = Path(__file__).resolve().parent
    operational_files = [
        Path(__file__).resolve(),
        script_root / "run_core_market_session_coverage.ps1",
        script_root / "monitor_core_market_session_coverage.ps1",
        script_root / "stop_core_market_session_coverage.ps1",
    ]
    operational_sha256 = {str(path): sha256_file(path) for path in operational_files}
    deferred = list(deferred_families)
    comparison = [family for family in FAMILIES if family not in set(deferred)]
    contract = {
        "config_sha256": config_hash,
        "operational_file_sha256": operational_sha256,
        "source_run_root": str(source_run),
        "source_pre_manifest_sha256": sha256_file(source_pre),
        "selected_tickers": list(selected),
        "scope": config["scope"],
        "timezone": "America/New_York",
        "normalization_clock": "ohlcv_1m.ts_utc",
        "comparison_families": comparison,
        "deferred_families": deferred,
    }
    return {
        "run_id": run_id,
        "mode": mode,
        "started_at_utc": iso_utc(),
        "config_path": str(config_path),
        "config_sha256": config_hash,
        "operational_file_sha256": operational_sha256,
        "run_contract_sha256": stable_json_hash(contract),
        "source_run_root": str(source_run),
        "source_pre_manifest_sha256": contract["source_pre_manifest_sha256"],
        "universe_ticker_count": len(universe),
        "universe_sha256": stable_json_hash(list(universe)),
        "selected_tickers": list(selected),
        "comparison_families": comparison,
        "deferred_families": deferred,
        "timezone_contract": "America/New_York",
        "source_roots_read_only": True,
    }


def run_root_requires_resume(run_root: Path, resume: bool) -> bool:
    return (
        not resume
        and (run_root / "00_control" / "pre_manifest.json").is_file()
    )


def run(
    config_path: Path,
    run_id: str,
    mode: str,
    explicit: str,
    resume: bool,
    authorized: bool,
    deferred_explicit: str = "",
) -> int:
    config, config_hash = load_config(config_path)
    if mode == "full" and not authorized:
        raise ValueError("Full audit requires --human-authorized-full")
    universe = load_universe(config)
    selected = select_tickers(config, universe, mode, explicit)
    deferred_families = parse_deferred_families(deferred_explicit)
    output_root = Path(str(config["runtime"]["output_root"]))
    run_root = output_root / run_id
    if run_root_requires_resume(run_root, resume):
        raise ValueError(f"Run root already exists; use --resume: {run_root}")
    paths = ensure_dirs(run_root)
    pre_path = paths["control"] / "pre_manifest.json"
    proposed = prepare_pre_manifest(
        config, config_path, config_hash, run_id, mode, universe, selected, deferred_families
    )
    if pre_path.is_file():
        pre_manifest = json.loads(pre_path.read_text(encoding="utf-8"))
        if pre_manifest["run_contract_sha256"] != proposed["run_contract_sha256"]:
            raise ValueError("Resume contract differs from persisted pre-manifest")
    else:
        pre_manifest = proposed
        atomic_write_json(pre_path, pre_manifest)
    contract_hash = str(pre_manifest["run_contract_sha256"])
    ledger = paths["control"] / "run_state.sqlite"
    initialize_ledger(ledger, run_id, contract_hash, selected)
    started = utc_now()
    write_heartbeat(run_root, {"status": "running", "stage": "ticker_session_audit", **ledger_snapshot(ledger)})

    for index, ticker in enumerate(selected, start=1):
        stop_request = paths["control"] / "stop.requested"
        if stop_request.is_file():
            os.replace(stop_request, paths["control"] / "stop.acknowledged")
            write_heartbeat(
                run_root,
                {
                    "status": "interrupted",
                    "stage": "controlled_stop",
                    "current_index": index,
                    "total_count": len(selected),
                    **ledger_snapshot(ledger),
                },
            )
            return 130
        snapshot = source_snapshot(config, ticker, deferred_families)
        snapshot_hash = source_snapshot_hash(snapshot)
        if task_manifest_valid(run_root, ticker, contract_hash, snapshot_hash):
            payload = json.loads(task_paths(run_root, ticker)["manifest"].read_text(encoding="utf-8"))
            ledger_update(
                ledger, ticker, "committed", source_snapshot_sha256=snapshot_hash,
                files_read=int(payload["minute_normalization"]["files_read"]),
                source_bytes_read=int(payload["minute_normalization"]["source_bytes_read"]),
                minute_rows_read=int(payload["minute_normalization"]["minute_rows_read"]),
                presence_rows=int(payload["presence_rows"]), gap_rows=int(payload["gap_rows"]),
                ended_at_utc=payload["ended_at_utc"], error_message=None,
            )
            continue
        ledger_update(
            ledger, ticker, "running", worker_pid=os.getpid(), started_at_utc=iso_utc(),
            source_snapshot_sha256=snapshot_hash, error_message=None,
        )
        write_heartbeat(run_root, {
            "status": "running", "stage": "ticker_session_audit", "current_index": index,
            "total_count": len(selected), "active_ticker": ticker, **ledger_snapshot(ledger),
        })
        try:
            result = build_ticker_task(config, run_root, ticker, run_id, contract_hash, snapshot)
            minute = result["minute_normalization"]
            ledger_update(
                ledger, ticker, "committed", worker_pid=os.getpid(), ended_at_utc=iso_utc(),
                files_read=int(minute["files_read"]), source_bytes_read=int(minute["source_bytes_read"]),
                minute_rows_read=int(minute["minute_rows_read"]), presence_rows=int(result["presence_rows"]),
                gap_rows=int(result["gap_rows"]), error_message=None,
            )
        except Exception as exc:
            ledger_update(
                ledger, ticker, "failed", worker_pid=os.getpid(), ended_at_utc=iso_utc(),
                error_message=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"[:12000],
            )
            write_heartbeat(run_root, {
                "status": "failed", "stage": "ticker_session_audit", "current_index": index,
                "total_count": len(selected), "active_ticker": ticker, "last_error": repr(exc),
                **ledger_snapshot(ledger),
            })
            raise

    snapshot = ledger_snapshot(ledger)
    if int(snapshot["task_counts"].get("committed", 0)) != len(selected):
        raise RuntimeError(f"Not all tasks committed: {snapshot['task_counts']}")
    write_heartbeat(run_root, {"status": "running", "stage": "finalizing", **snapshot})
    final = finalize_run(config, run_root, pre_manifest)
    write_heartbeat(run_root, {
        "status": "completed", "stage": "closed", "elapsed_seconds": round((utc_now()-started).total_seconds(), 3),
        "technical_status": final["technical_status"], "comparison_state": final["comparison_state"],
        **ledger_snapshot(ledger),
    })
    print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("probe", "full"), required=True)
    parser.add_argument("--tickers", default="")
    parser.add_argument("--deferred-families", default="")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--human-authorized-full", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run(
        args.config,
        args.run_id,
        args.mode,
        args.tickers,
        args.resume,
        args.human_authorized_full,
        args.deferred_families,
    )


if __name__ == "__main__":
    raise SystemExit(main())
