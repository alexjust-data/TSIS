"""Independent, resumable download-evidence audit for one core market family.

The closed physical audit is adopted as immutable evidence for every Parquet
footer/schema check.  This runner revalidates those evidence hashes and reads
only the event clock required to classify observed activity by ET session.
It never turns local absence into a vendor omission without external evidence.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import shutil
import sqlite3
import time
import traceback
from datetime import date, datetime, time as civil_time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import quote
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
FAMILIES = ("ohlcv_daily", "ohlcv_1m", "quotes_")
BANDS = ("premarket", "rth", "afterhours", "outside_0400_2000")

ACTIVITY_SCHEMA = pa.schema(
    [
        ("family", pa.string()),
        ("ticker", pa.string()),
        ("session_date_et", pa.date32()),
        ("total_rows", pa.int64()),
        ("premarket_rows", pa.int64()),
        ("rth_rows", pa.int64()),
        ("afterhours_rows", pa.int64()),
        ("outside_0400_2000_rows", pa.int64()),
        ("has_premarket", pa.bool_()),
        ("has_rth", pa.bool_()),
        ("has_afterhours", pa.bool_()),
        ("has_outside_0400_2000", pa.bool_()),
        ("session_classification_state", pa.string()),
        ("physical_evidence_state", pa.string()),
        ("download_completeness_state", pa.string()),
    ]
)

COVERAGE_SCHEMA = pa.schema(
    [
        ("family", pa.string()),
        ("ticker", pa.string()),
        ("source_state", pa.string()),
        ("file_count", pa.int32()),
        ("source_bytes", pa.int64()),
        ("rows_read_or_adopted", pa.int64()),
        ("observed_session_count", pa.int32()),
        ("first_session_date_et", pa.date32()),
        ("last_session_date_et", pa.date32()),
        ("scope_start_inclusive", pa.date32()),
        ("scope_end_inclusive", pa.date32()),
        ("leading_boundary_state", pa.string()),
        ("trailing_boundary_state", pa.string()),
        ("physical_error_file_count", pa.int32()),
        ("timestamp_parse_error_count", pa.int64()),
        ("out_of_scope_row_count", pa.int64()),
        ("download_completeness_state", pa.string()),
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


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def atomic_write_table(path: Path, table: pa.Table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    pq.write_table(table, partial, compression="zstd")
    with partial.open("rb+") as handle:
        os.fsync(handle.fileno())
    os.replace(partial, path)


def table_from_rows(rows: Sequence[dict[str, Any]], schema: pa.Schema) -> pa.Table:
    return pa.Table.from_pylist(list(rows), schema=schema)


def parse_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def safe_ticker(ticker: str) -> str:
    return quote(ticker, safe="._-")


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
    table = pq.ParquetFile(Path(str(spec["path"]))).read(columns=[str(spec["ticker_column"])])
    values = [str(v) for v in table.column(0).to_pylist() if v is not None]
    if len(values) != len(set(values)):
        raise ValueError("Universe contains duplicate ticker strings")
    if "NA" not in values:
        raise ValueError("Literal ticker NA is missing from the governed universe")
    expected = int(config["scope"]["expected_universe_members"])
    if len(values) != expected:
        raise ValueError(f"Universe cardinality mismatch: {len(values)} != {expected}")
    return sorted(values)


def select_tickers(
    config: dict[str, Any], universe: Sequence[str], mode: str, explicit: str
) -> list[str]:
    if mode == "full":
        if explicit:
            raise ValueError("Full mode must use the exact governed universe")
        return list(universe)
    requested = [value.strip() for value in explicit.split(",") if value.strip()]
    selected = requested or [str(v) for v in config["probe"]["tickers"]]
    missing = sorted(set(selected) - set(universe))
    if missing:
        raise ValueError(f"Probe tickers outside universe: {missing}")
    return selected


def source_paths(config: dict[str, Any], family: str, ticker: str) -> dict[str, Path]:
    root = Path(str(config["source_audit"]["run_root"]))
    safe = safe_ticker(ticker)
    return {
        "run": root,
        "ledger": root / "00_control" / "run_state.sqlite",
        "task": root / "00_control" / "task_results" / family / f"ticker={safe}.json",
        "inventory": root / "01_inventory" / family / f"ticker={safe}" / "inventory.parquet",
        "dates": root / "02_ticker_coverage" / family / f"ticker={safe}" / "ticker_dates.parquet",
        "final": root / "04_closeout" / "final_manifest.json",
    }


def validate_source_run(config: dict[str, Any], family: str, universe: Sequence[str]) -> dict[str, Any]:
    paths = source_paths(config, family, universe[0])
    final = json.loads(paths["final"].read_text(encoding="utf-8"))
    if final.get("technical_status") != "COMPLETED" or final.get("status") != "completed":
        raise ValueError("Source physical audit is not technically completed")
    uri = paths["ledger"].resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        connection.execute("PRAGMA query_only=ON")
        counts = dict(
            connection.execute(
                "SELECT status,COUNT(*) FROM tasks WHERE family=? GROUP BY status", (family,)
            ).fetchall()
        )
    if counts != {"committed": len(universe)}:
        raise ValueError(f"Source family ledger is not 100% committed: {counts}")
    return {
        "source_run_id": final["run_id"],
        "source_final_manifest": str(paths["final"]),
        "source_final_manifest_sha256": sha256_file(paths["final"]),
        "source_family_task_counts": counts,
    }


def validate_source_task(config: dict[str, Any], family: str, ticker: str) -> dict[str, Any]:
    paths = source_paths(config, family, ticker)
    payload = json.loads(paths["task"].read_text(encoding="utf-8"))
    if payload.get("status") != "committed":
        raise ValueError(f"Source task is not committed: {paths['task']}")
    forbidden_nonzero = (
        "empty_file_count",
        "error_file_count",
        "schema_incomplete_file_count",
        "unreadable_file_count",
        "zero_byte_file_count",
    )
    bad = {key: payload.get(key) for key in forbidden_nonzero if int(payload.get(key, 0)) != 0}
    if bad:
        raise ValueError(f"Source task has physical failures: {bad}")
    artifact_hashes = {Path(a["path"]).name: str(a["sha256"]) for a in payload["artifacts"]}
    for key in ("inventory", "dates"):
        path = paths[key]
        expected = artifact_hashes.get(path.name)
        actual = sha256_file(path)
        if expected != actual:
            raise ValueError(f"Source evidence hash mismatch for {path}: {actual} != {expected}")
    inventory = pq.ParquetFile(paths["inventory"]).read()
    required = {
        "file_exists",
        "file_size_bytes",
        "magic_header_ok",
        "magic_footer_ok",
        "parquet_openable",
        "metadata_readable",
        "metadata_num_rows",
        "schema_readable",
        "required_schema_complete",
        "absolute_path",
        "error_class",
    }
    if not required.issubset(inventory.schema.names):
        raise ValueError(f"Source inventory schema incomplete: {required-set(inventory.schema.names)}")
    rows = inventory.to_pylist()
    for row in rows:
        valid = (
            row["file_exists"]
            and int(row["file_size_bytes"]) > 0
            and row["magic_header_ok"]
            and row["magic_footer_ok"]
            and row["parquet_openable"]
            and row["metadata_readable"]
            and int(row["metadata_num_rows"]) > 0
            and row["schema_readable"]
            and row["required_schema_complete"]
            and not row["error_class"]
        )
        if not valid:
            raise ValueError(f"Invalid adopted inventory row: {row}")
    return {
        "task_payload": payload,
        "task_sha256": sha256_file(paths["task"]),
        "inventory_path": str(paths["inventory"]),
        "inventory_sha256": sha256_file(paths["inventory"]),
        "dates_path": str(paths["dates"]),
        "dates_sha256": sha256_file(paths["dates"]),
        "inventory_rows": rows,
        "file_count": len(rows),
        "source_bytes": sum(int(row["file_size_bytes"]) for row in rows),
        "metadata_rows": sum(int(row["metadata_num_rows"]) for row in rows),
    }


class SessionBoundaryIndex:
    """Vectorized UTC instant to America/New_York session classifier."""

    def __init__(self, scope_start: date, scope_end: date, unit: str) -> None:
        if unit not in {"s", "ns"}:
            raise ValueError(unit)
        self.scope_start = scope_start
        self.scope_end = scope_end
        self.unit = unit
        first = scope_start - timedelta(days=1)
        last = scope_end + timedelta(days=1)
        dates: list[date] = []
        value = first
        while value <= last:
            dates.append(value)
            value += timedelta(days=1)
        scale = 1_000_000_000 if unit == "ns" else 1

        def epoch(local_date: date, local_time: civil_time) -> int:
            local = datetime.combine(local_date, local_time, tzinfo=NY)
            return int(local.timestamp()) * scale

        self.dates = dates
        self.day_start = np.array([epoch(d, civil_time(0, 0)) for d in dates], dtype=np.int64)
        self.pre = np.array([epoch(d, civil_time(4, 0)) for d in dates], dtype=np.int64)
        self.rth = np.array([epoch(d, civil_time(9, 30)) for d in dates], dtype=np.int64)
        self.after = np.array([epoch(d, civil_time(16, 0)) for d in dates], dtype=np.int64)
        self.end = np.array([epoch(d, civil_time(20, 0)) for d in dates], dtype=np.int64)
        self.scope_offset = 1
        self.scope_days = (scope_end - scope_start).days + 1

    def classify_into(self, values: np.ndarray, counts: np.ndarray) -> tuple[int, int]:
        values = np.asarray(values, dtype=np.int64)
        if not len(values):
            return 0, 0
        day_idx = np.searchsorted(self.day_start, values, side="right") - 1
        valid_boundary = (day_idx >= 0) & (day_idx < len(self.dates))
        parseable = int(valid_boundary.sum())
        out_of_scope = len(values) - parseable
        if not parseable:
            return len(values), out_of_scope
        selected_values = values[valid_boundary]
        selected_idx = day_idx[valid_boundary]
        scope_idx = selected_idx - self.scope_offset
        in_scope = (scope_idx >= 0) & (scope_idx < self.scope_days)
        out_of_scope += int((~in_scope).sum())
        if not in_scope.any():
            return len(values), out_of_scope
        selected_values = selected_values[in_scope]
        selected_idx = selected_idx[in_scope]
        scope_idx = scope_idx[in_scope]
        band = np.full(len(selected_values), 3, dtype=np.int8)
        band[(selected_values >= self.pre[selected_idx]) & (selected_values < self.rth[selected_idx])] = 0
        band[(selected_values >= self.rth[selected_idx]) & (selected_values < self.after[selected_idx])] = 1
        band[(selected_values >= self.after[selected_idx]) & (selected_values < self.end[selected_idx])] = 2
        flat = scope_idx.astype(np.int64) * 4 + band.astype(np.int64)
        counts += np.bincount(flat, minlength=self.scope_days * 4).reshape(self.scope_days, 4)
        return len(values), out_of_scope


def task_paths(run_root: Path, ticker: str) -> dict[str, Path]:
    safe = safe_ticker(ticker)
    return {
        "activity": run_root / "01_activity" / f"ticker={safe}" / "activity.parquet",
        "coverage": run_root / "02_coverage" / f"ticker={safe}" / "coverage.parquet",
        "manifest": run_root / "00_control" / "task_results" / f"ticker={safe}.json",
    }


def connect_ledger(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=60)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    return connection


def initialize_ledger(path: Path, run_id: str, contract_hash: str, tickers: Sequence[str]) -> None:
    with connect_ledger(path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS run_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(
                ticker TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt INTEGER NOT NULL DEFAULT 0,
                worker_pid INTEGER,
                started_at_utc TEXT,
                ended_at_utc TEXT,
                files_read INTEGER,
                rows_read INTEGER,
                activity_rows INTEGER,
                error_message TEXT
            );
            """
        )
        connection.execute("INSERT OR REPLACE INTO run_metadata VALUES('run_id',?)", (run_id,))
        connection.execute("INSERT OR REPLACE INTO run_metadata VALUES('run_contract_sha256',?)", (contract_hash,))
        connection.executemany(
            "INSERT OR IGNORE INTO tasks(ticker,status) VALUES(?,'pending')", [(ticker,) for ticker in tickers]
        )
        connection.execute("UPDATE tasks SET status='pending',worker_pid=NULL WHERE status='running'")


def ledger_update(path: Path, ticker: str, status: str, **values: Any) -> None:
    allowed = {
        "worker_pid",
        "started_at_utc",
        "ended_at_utc",
        "files_read",
        "rows_read",
        "activity_rows",
        "error_message",
    }
    if set(values) - allowed:
        raise ValueError(f"Unsupported ledger fields: {set(values)-allowed}")
    assignments = ["status=?"] + [f"{key}=?" for key in values]
    params = [status, *values.values(), ticker]
    with connect_ledger(path) as connection:
        connection.execute(f"UPDATE tasks SET {','.join(assignments)} WHERE ticker=?", params)
        if status == "running":
            connection.execute("UPDATE tasks SET attempt=attempt+1 WHERE ticker=?", (ticker,))


def ledger_snapshot(path: Path) -> dict[str, Any]:
    with connect_ledger(path) as connection:
        counts = dict(connection.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status").fetchall())
        totals = connection.execute(
            "SELECT COALESCE(SUM(files_read),0),COALESCE(SUM(rows_read),0),"
            "COALESCE(SUM(activity_rows),0) FROM tasks WHERE status='committed'"
        ).fetchone()
        active = [row[0] for row in connection.execute(
            "SELECT ticker FROM tasks WHERE status='running' ORDER BY ticker"
        ).fetchall()]
    return {
        "task_counts": {str(k): int(v) for k, v in counts.items()},
        "total_tasks": sum(int(v) for v in counts.values()),
        "files_read": int(totals[0]),
        "rows_read": int(totals[1]),
        "activity_rows": int(totals[2]),
        "active_tickers": active,
    }


def write_heartbeat(run_root: Path, stage: str, status: str, ledger: Path, **extra: Any) -> None:
    payload = {
        "run_id": run_root.name,
        "observed_at_utc": iso_utc(),
        "status": status,
        "stage": stage,
        "runner_pid": os.getpid(),
        **ledger_snapshot(ledger),
        **extra,
    }
    atomic_write_json(run_root / "00_control" / "heartbeat.json", payload)
    append_jsonl(run_root / "00_control" / "heartbeat.jsonl", payload)


def daily_activity(
    config: dict[str, Any], ticker: str, evidence: dict[str, Any]
) -> tuple[list[dict[str, Any]], int, int, int]:
    dates = pq.ParquetFile(Path(evidence["dates_path"])).read(columns=["observed_date"]).column(0).to_pylist()
    scope_start = parse_date(str(config["scope"]["start_date_inclusive"]))
    scope_end = parse_date(str(config["scope"]["end_date_inclusive"]))
    observed = sorted({value for value in dates if scope_start <= value <= scope_end})
    rows = [
        {
            "family": "ohlcv_daily",
            "ticker": ticker,
            "session_date_et": value,
            "total_rows": 1,
            "premarket_rows": None,
            "rth_rows": None,
            "afterhours_rows": None,
            "outside_0400_2000_rows": None,
            "has_premarket": None,
            "has_rth": None,
            "has_afterhours": None,
            "has_outside_0400_2000": None,
            "session_classification_state": "NOT_APPLICABLE_DAILY_AGGREGATE",
            "physical_evidence_state": "ADOPTED_CLOSED_PHYSICAL_AUDIT",
            "download_completeness_state": "PRESENT_VALID_FILE",
        }
        for value in observed
    ]
    return rows, int(evidence["metadata_rows"]), 0, 0


def timestamp_activity(
    config: dict[str, Any], family: str, ticker: str, evidence: dict[str, Any]
) -> tuple[list[dict[str, Any]], int, int, int]:
    scope_start = parse_date(str(config["scope"]["start_date_inclusive"]))
    scope_end = parse_date(str(config["scope"]["end_date_inclusive"]))
    spec = config["families"][family]
    mode = str(spec["timestamp_mode"])
    column = str(spec["timestamp_column"])
    unit = "s" if mode == "iso_utc_string" else "ns"
    boundary = SessionBoundaryIndex(scope_start, scope_end, unit)
    counts = np.zeros((boundary.scope_days, 4), dtype=np.int64)
    rows_read = 0
    parse_errors = 0
    out_of_scope = 0
    for row in evidence["inventory_rows"]:
        path = Path(str(row["absolute_path"]))
        parquet = pq.ParquetFile(path)
        if column not in parquet.schema_arrow.names:
            raise ValueError(f"Timestamp column {column} missing from {path}")
        for group in range(parquet.metadata.num_row_groups):
            array = parquet.read_row_group(group, columns=[column]).column(0).combine_chunks()
            if mode == "iso_utc_string":
                parsed = pc.strptime(array, format="%Y-%m-%dT%H:%M:%SZ", unit="s", error_is_null=True)
                parse_errors += parsed.null_count
                valid = pc.drop_null(parsed)
                values = pc.cast(valid, pa.int64()).to_numpy(zero_copy_only=False)
            elif mode == "epoch_ns_int64":
                parse_errors += array.null_count
                valid = pc.drop_null(array)
                values = pc.cast(valid, pa.int64()).to_numpy(zero_copy_only=False)
            else:
                raise ValueError(f"Unsupported timestamp mode: {mode}")
            consumed, outside = boundary.classify_into(values, counts)
            rows_read += len(array)
            out_of_scope += outside
            if consumed != len(values):
                raise AssertionError("Session classifier did not consume all non-null values")
    if parse_errors:
        raise ValueError(f"{ticker}: {parse_errors} invalid/null timestamp values")
    if rows_read != int(evidence["metadata_rows"]):
        raise ValueError(f"Row reconciliation failed for {ticker}: {rows_read} != {evidence['metadata_rows']}")
    output: list[dict[str, Any]] = []
    for offset in np.flatnonzero(counts.sum(axis=1)):
        values = counts[int(offset)]
        session = scope_start + timedelta(days=int(offset))
        output.append(
            {
                "family": family,
                "ticker": ticker,
                "session_date_et": session,
                "total_rows": int(values.sum()),
                "premarket_rows": int(values[0]),
                "rth_rows": int(values[1]),
                "afterhours_rows": int(values[2]),
                "outside_0400_2000_rows": int(values[3]),
                "has_premarket": bool(values[0]),
                "has_rth": bool(values[1]),
                "has_afterhours": bool(values[2]),
                "has_outside_0400_2000": bool(values[3]),
                "session_classification_state": "EXACT_EVENT_CLOCK_AMERICA_NEW_YORK",
                "physical_evidence_state": "ADOPTED_CLOSED_PHYSICAL_AUDIT",
                "download_completeness_state": "PRESENT_VALID_FILE",
            }
        )
    return output, rows_read, parse_errors, out_of_scope


def build_ticker_task(
    config: dict[str, Any], run_root_text: str, family: str, ticker: str,
    run_id: str, contract_hash: str, ledger_text: str
) -> dict[str, Any]:
    run_root = Path(run_root_text)
    ledger = Path(ledger_text)
    paths = task_paths(run_root, ticker)
    started = utc_now()
    ledger_update(
        ledger, ticker, "running", worker_pid=os.getpid(), started_at_utc=iso_utc(started),
        error_message=None,
    )
    evidence = validate_source_task(config, family, ticker)
    source_snapshot = {
        key: evidence[key]
        for key in ("task_sha256", "inventory_sha256", "dates_sha256", "file_count", "source_bytes", "metadata_rows")
    }
    if family == "ohlcv_daily":
        activity_rows, rows_read, parse_errors, out_of_scope = daily_activity(config, ticker, evidence)
    else:
        activity_rows, rows_read, parse_errors, out_of_scope = timestamp_activity(
            config, family, ticker, evidence
        )
    dates = [row["session_date_et"] for row in activity_rows]
    scope_start = parse_date(str(config["scope"]["start_date_inclusive"]))
    scope_end = parse_date(str(config["scope"]["end_date_inclusive"]))
    first = min(dates) if dates else None
    last = max(dates) if dates else None
    coverage_row = {
        "family": family,
        "ticker": ticker,
        "source_state": "COMMITTED_ADOPTED_PHYSICAL_AUDIT",
        "file_count": int(evidence["file_count"]),
        "source_bytes": int(evidence["source_bytes"]),
        "rows_read_or_adopted": int(rows_read),
        "observed_session_count": len(dates),
        "first_session_date_et": first,
        "last_session_date_et": last,
        "scope_start_inclusive": scope_start,
        "scope_end_inclusive": scope_end,
        "leading_boundary_state": "UNRESOLVED_NO_INDEPENDENT_EXPECTED_AUTHORITY" if first != scope_start else "REACHES_SCOPE_START",
        "trailing_boundary_state": "UNRESOLVED_NO_INDEPENDENT_EXPECTED_AUTHORITY" if last != scope_end else "REACHES_SCOPE_END",
        "physical_error_file_count": 0,
        "timestamp_parse_error_count": int(parse_errors),
        "out_of_scope_row_count": int(out_of_scope),
        "download_completeness_state": "NOT_CERTIFIED_PROVIDER_EMPTY_UNRESOLVED",
    }
    atomic_write_table(paths["activity"], table_from_rows(activity_rows, ACTIVITY_SCHEMA))
    atomic_write_table(paths["coverage"], table_from_rows([coverage_row], COVERAGE_SCHEMA))
    artifacts = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in (paths["activity"], paths["coverage"])
    ]
    payload = {
        "run_id": run_id,
        "run_contract_sha256": contract_hash,
        "family": family,
        "ticker": ticker,
        "status": "committed",
        "worker_pid": os.getpid(),
        "started_at_utc": iso_utc(started),
        "ended_at_utc": iso_utc(),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 3),
        "source_snapshot": source_snapshot,
        "source_snapshot_sha256": stable_json_hash(source_snapshot),
        "file_count": int(evidence["file_count"]),
        "source_bytes": int(evidence["source_bytes"]),
        "rows_read_or_adopted": int(rows_read),
        "activity_rows": len(activity_rows),
        "first_session_date_et": first.isoformat() if first else None,
        "last_session_date_et": last.isoformat() if last else None,
        "timestamp_parse_error_count": int(parse_errors),
        "out_of_scope_row_count": int(out_of_scope),
        "artifacts": artifacts,
    }
    atomic_write_json(paths["manifest"], payload)
    ledger_update(
        ledger, ticker, "committed", worker_pid=os.getpid(), ended_at_utc=payload["ended_at_utc"],
        files_read=payload["file_count"], rows_read=payload["rows_read_or_adopted"],
        activity_rows=payload["activity_rows"], error_message=None,
    )
    return payload


def task_manifest_valid(run_root: Path, ticker: str, contract_hash: str) -> bool:
    paths = task_paths(run_root, ticker)
    if not paths["manifest"].is_file():
        return False
    try:
        payload = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        if payload.get("status") != "committed" or payload.get("run_contract_sha256") != contract_hash:
            return False
        return all(Path(a["path"]).is_file() and sha256_file(Path(a["path"])) == a["sha256"] for a in payload["artifacts"])
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


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


def finalize_run(config: dict[str, Any], run_root: Path, pre: dict[str, Any]) -> dict[str, Any]:
    tickers = [str(value) for value in pre["selected_tickers"]]
    family = str(pre["family"])
    closeout = run_root / "03_closeout"
    activity_path = closeout / f"{family}_session_activity.parquet"
    coverage_path = closeout / f"{family}_ticker_coverage.parquet"
    activity_count = stream_consolidate(
        (task_paths(run_root, ticker)["activity"] for ticker in tickers), activity_path, ACTIVITY_SCHEMA
    )
    coverage_count = stream_consolidate(
        (task_paths(run_root, ticker)["coverage"] for ticker in tickers), coverage_path, COVERAGE_SCHEMA
    )
    manifests = [json.loads(task_paths(run_root, ticker)["manifest"].read_text(encoding="utf-8")) for ticker in tickers]
    snapshot = ledger_snapshot(run_root / "00_control" / "run_state.sqlite")
    committed = int(snapshot["task_counts"].get("committed", 0))
    failed = int(snapshot["task_counts"].get("failed", 0))
    technical_status = "PASS" if committed == len(tickers) and failed == 0 else "FAIL"
    summary = {
        "run_id": pre["run_id"],
        "family": family,
        "mode": pre["mode"],
        "technical_status": technical_status,
        "physical_integrity_status": "PASS_ADOPTED_CLOSED_AUDIT" if technical_status == "PASS" else "FAIL",
        "download_completeness_status": "NOT_CERTIFIED_PROVIDER_EMPTY_UNRESOLVED",
        "expected_tickers": len(tickers),
        "committed_tickers": committed,
        "failed_tickers": failed,
        "file_count": sum(int(m["file_count"]) for m in manifests),
        "source_bytes": sum(int(m["source_bytes"]) for m in manifests),
        "rows_read_or_adopted": sum(int(m["rows_read_or_adopted"]) for m in manifests),
        "activity_rows": activity_count,
        "coverage_rows": coverage_count,
        "timestamp_parse_error_count": sum(int(m["timestamp_parse_error_count"]) for m in manifests),
        "out_of_scope_row_count": sum(int(m["out_of_scope_row_count"]) for m in manifests),
        "scope": pre["scope"],
        "source_evidence": pre["source_evidence"],
        "started_at_utc": pre["started_at_utc"],
        "ended_at_utc": iso_utc(),
    }
    closeout.mkdir(parents=True, exist_ok=True)
    summary_path = closeout / "audit_summary.json"
    atomic_write_json(summary_path, summary)
    report_path = closeout / "FAMILY_DOWNLOAD_AUDIT.md"
    report = (
        f"# Family Download Audit: {family}\n\n"
        f"- Run: `{pre['run_id']}`\n"
        f"- Technical status: `{technical_status}`\n"
        f"- Tickers committed: `{committed}/{len(tickers)}`\n"
        f"- Physical integrity: `PASS_ADOPTED_CLOSED_AUDIT`\n"
        f"- Download completeness: `NOT_CERTIFIED_PROVIDER_EMPTY_UNRESOLVED`\n\n"
        "All present Parquets inherit the closed per-file footer, metadata, non-empty and schema checks. "
        "Observed session activity is exact for event-clock families. Absence is not called missing vendor data "
        "without an independent expected/lifecycle authority or vendor-confirmed empty response.\n"
    )
    atomic_write_text(report_path, report)
    artifacts = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in (activity_path, coverage_path, summary_path, report_path)
    ]
    final = {**summary, "status": "completed", "artifacts": artifacts}
    atomic_write_json(closeout / "final_manifest.json", final)
    return final


def prepare_pre_manifest(
    config: dict[str, Any], config_path: Path, config_hash: str, run_id: str,
    mode: str, family: str, universe: Sequence[str], selected: Sequence[str],
    source_evidence: dict[str, Any]
) -> dict[str, Any]:
    script_root = Path(__file__).resolve().parent
    operational = [
        Path(__file__).resolve(),
        script_root / "run_family_download_audit.ps1",
        script_root / "monitor_family_download_audit.py",
        script_root / "monitor_family_download_audit.ps1",
        script_root / "stop_family_download_audit.ps1",
    ]
    operational_hashes = {str(path): sha256_file(path) for path in operational}
    scope = config["scope"]
    contract = {
        "config_sha256": config_hash,
        "operational_file_sha256": operational_hashes,
        "family": family,
        "selected_tickers": list(selected),
        "scope": scope,
        "source_evidence": source_evidence,
        "timezone": "America/New_York",
    }
    return {
        "run_id": run_id,
        "mode": mode,
        "family": family,
        "status": "starting",
        "started_at_utc": iso_utc(),
        "script_path": str(Path(__file__).resolve()),
        "config_path": str(config_path.resolve()),
        "config_sha256": config_hash,
        "run_contract_sha256": stable_json_hash(contract),
        "operational_file_sha256": operational_hashes,
        "source_evidence": source_evidence,
        "source_roots_read_only": True,
        "universe_members": len(universe),
        "universe_sha256": stable_json_hash(list(universe)),
        "selected_tickers": list(selected),
        "scope": scope,
        "timezone_contract": "America/New_York",
        "resume_policy": "task-private atomic shards; committed shards hash-validated and adopted",
        "overwrite_policy": "refuse existing run root unless --resume",
        "success_criteria": f"{len(selected)}/{len(selected)} committed, zero failures, final manifest",
        "download_completeness_limit": "absence remains unresolved without independent expected authority",
    }


def run(
    config_path: Path, run_id: str, mode: str, family: str, explicit: str,
    resume: bool, authorized: bool, workers_override: int | None
) -> int:
    config, config_hash = load_config(config_path)
    if family not in FAMILIES:
        raise ValueError(family)
    if mode == "full" and not authorized:
        raise ValueError("Full audit requires --human-authorized-full")
    universe = load_universe(config)
    selected = select_tickers(config, universe, mode, explicit)
    source_evidence = validate_source_run(config, family, universe)
    output_root = Path(str(config["runtime"]["output_root"]))
    run_root = output_root / run_id
    pre_path = run_root / "00_control" / "pre_manifest.json"
    if pre_path.is_file() and not resume:
        raise ValueError(f"Run root already exists; use --resume: {run_root}")
    for name in ("00_control/task_results", "01_activity", "02_coverage", "03_closeout"):
        (run_root / name).mkdir(parents=True, exist_ok=True)
    proposed = prepare_pre_manifest(
        config, config_path, config_hash, run_id, mode, family, universe, selected, source_evidence
    )
    if pre_path.is_file():
        pre = json.loads(pre_path.read_text(encoding="utf-8"))
        if pre["run_contract_sha256"] != proposed["run_contract_sha256"]:
            raise ValueError("Resume contract differs from persisted pre-manifest")
    else:
        pre = proposed
        atomic_write_json(pre_path, pre)
    contract_hash = str(pre["run_contract_sha256"])
    ledger = run_root / "00_control" / "run_state.sqlite"
    initialize_ledger(ledger, run_id, contract_hash, selected)
    pid_manifest = {
        "run_id": run_id,
        "runner_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "started_at_utc": iso_utc(),
        "family": family,
        "expected_alive": True,
    }
    atomic_write_json(run_root / "00_control" / "pid_manifest.json", pid_manifest)
    pending: list[str] = []
    for ticker in selected:
        if task_manifest_valid(run_root, ticker, contract_hash):
            payload = json.loads(task_paths(run_root, ticker)["manifest"].read_text(encoding="utf-8"))
            ledger_update(
                ledger, ticker, "committed", worker_pid=payload["worker_pid"],
                ended_at_utc=payload["ended_at_utc"], files_read=payload["file_count"],
                rows_read=payload["rows_read_or_adopted"], activity_rows=payload["activity_rows"],
                error_message=None,
            )
        else:
            pending.append(ticker)
    workers = workers_override or int(config["runtime"]["workers_by_family"][family])
    if not 1 <= workers <= 12:
        raise ValueError("Workers must be between 1 and 12")
    write_heartbeat(run_root, "family_ticker_audit", "running", ledger, workers=workers)
    print(json.dumps({
        "run_id": run_id,
        "family": family,
        "mode": mode,
        "run_root": str(run_root),
        "pre_manifest": str(pre_path),
        "pid_manifest": str(run_root / "00_control" / "pid_manifest.json"),
        "heartbeat": str(run_root / "00_control" / "heartbeat.json"),
        "ledger": str(ledger),
        "workers": workers,
        "monitor": f'powershell -NoProfile -ExecutionPolicy Bypass -File "{Path(__file__).resolve().parent / "monitor_family_download_audit.ps1"}" -RunRoot "{run_root}" -Watch',
        "resume_policy": pre["resume_policy"],
        "success_criteria": pre["success_criteria"],
    }, ensure_ascii=False, indent=2), flush=True)
    stop_requested = False
    failures: list[tuple[str, str]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        iterator = iter(pending)
        active: dict[concurrent.futures.Future[dict[str, Any]], str] = {}

        def submit_next() -> bool:
            nonlocal stop_requested
            if (run_root / "00_control" / "stop.requested").is_file():
                stop_requested = True
                return False
            try:
                ticker = next(iterator)
            except StopIteration:
                return False
            future = pool.submit(
                build_ticker_task, config, str(run_root), family, ticker, run_id,
                contract_hash, str(ledger)
            )
            active[future] = ticker
            return True

        for _ in range(workers):
            submit_next()
        last_heartbeat = 0.0
        while active:
            done, _ = concurrent.futures.wait(
                active, timeout=5, return_when=concurrent.futures.FIRST_COMPLETED
            )
            now = time.monotonic()
            if now - last_heartbeat >= int(config["runtime"]["heartbeat_seconds"]):
                write_heartbeat(
                    run_root, "family_ticker_audit", "running", ledger,
                    workers=workers, stop_requested=stop_requested,
                )
                last_heartbeat = now
            for future in done:
                ticker = active.pop(future)
                try:
                    future.result()
                except Exception as exc:
                    message = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"[:12000]
                    ledger_update(
                        ledger, ticker, "failed", ended_at_utc=iso_utc(), error_message=message
                    )
                    failures.append((ticker, message))
                if not failures and not stop_requested:
                    submit_next()
            if failures:
                stop_requested = True
    if (run_root / "00_control" / "stop.requested").is_file():
        os.replace(
            run_root / "00_control" / "stop.requested",
            run_root / "00_control" / "stop.acknowledged",
        )
    if failures:
        write_heartbeat(run_root, "family_ticker_audit", "failed", ledger, last_error=failures[0][1])
        raise RuntimeError(f"Family audit failed for {failures[0][0]}: {failures[0][1]}")
    if stop_requested:
        write_heartbeat(run_root, "controlled_stop", "interrupted", ledger)
        return 130
    snapshot = ledger_snapshot(ledger)
    if int(snapshot["task_counts"].get("committed", 0)) != len(selected):
        raise RuntimeError(f"Not all tasks committed: {snapshot['task_counts']}")
    write_heartbeat(run_root, "finalizing", "running", ledger)
    final = finalize_run(config, run_root, pre)
    pid_manifest["expected_alive"] = False
    pid_manifest["ended_at_utc"] = iso_utc()
    atomic_write_json(run_root / "00_control" / "pid_manifest.json", pid_manifest)
    write_heartbeat(run_root, "closed", "completed", ledger, technical_status=final["technical_status"])
    print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True), flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("probe", "full"), required=True)
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--tickers", default="")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--human-authorized-full", action="store_true")
    parser.add_argument("--workers", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run(
        args.config, args.run_id, args.mode, args.family, args.tickers,
        args.resume, args.human_authorized_full, args.workers
    )


if __name__ == "__main__":
    raise SystemExit(main())
