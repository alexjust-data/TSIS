"""Target-scoped physical and ticker-date alignment audit for four RAW families.

The source roots are strictly read-only. Runtime artifacts are written below
``C:/TSIS_Data/runs/data_ops/core_market_raw_alignment_audit/<run_id>``.

The production topology is one sequential reader per family. A task is the
atomic pair ``family x ticker``; committed task artifacts can be reused after an
interruption only when their hashes and run-contract hash still match.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import multiprocessing as mp
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence
from urllib.parse import quote

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml

try:
    import psutil
except ImportError:  # pragma: no cover - the governed host currently provides it.
    psutil = None  # type: ignore[assignment]


AUDITOR_VERSION = "0.1.0"
REPO_ROOT = Path(r"C:\TSIS_Data")
DEFAULT_CONFIG = REPO_ROOT / "01_TSIS_DATA_FOUNDATION" / "configs" / "core_market_raw_alignment_audit_v0_1.yaml"
EXPECTED_FAMILIES = (
    "ohlcv_daily",
    "ohlcv_1m",
    "quotes_",
    "trades_ticks_prod_2005_2026",
)
FAMILY_OUTPUT_STEMS = {
    "ohlcv_daily": "ohlcv_daily",
    "ohlcv_1m": "ohlcv_1m",
    "quotes_": "quotes",
    "trades_ticks_prod_2005_2026": "trades",
}
REPARSE_POINT = 0x400


INVENTORY_SCHEMA = pa.schema(
    [
        ("family", pa.string()),
        ("ticker", pa.string()),
        ("absolute_path", pa.string()),
        ("relative_path", pa.string()),
        ("file_exists", pa.bool_()),
        ("file_size_bytes", pa.int64()),
        ("magic_header_ok", pa.bool_()),
        ("magic_footer_ok", pa.bool_()),
        ("parquet_openable", pa.bool_()),
        ("metadata_readable", pa.bool_()),
        ("metadata_num_rows", pa.int64()),
        ("row_group_count", pa.int32()),
        ("schema_readable", pa.bool_()),
        ("schema_fingerprint", pa.string()),
        ("schema_columns_json", pa.string()),
        ("missing_required_columns_json", pa.string()),
        ("extra_columns_json", pa.string()),
        ("required_schema_complete", pa.bool_()),
        ("date_extraction_method", pa.string()),
        ("observed_date_count", pa.int32()),
        ("first_observed_date", pa.date32()),
        ("last_observed_date", pa.date32()),
        ("out_of_scope_date_count", pa.int32()),
        ("error_class", pa.string()),
        ("error_message", pa.string()),
    ]
)

TICKER_DATE_SCHEMA = pa.schema(
    [
        ("family", pa.string()),
        ("ticker", pa.string()),
        ("observed_date", pa.date32()),
    ]
)

TICKER_DATE_DIFFERENCE_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("observed_date", pa.date32()),
        ("present_in_ohlcv_daily", pa.bool_()),
        ("present_in_ohlcv_1m", pa.bool_()),
        ("present_in_quotes", pa.bool_()),
        ("present_in_trades", pa.bool_()),
        ("present_family_count", pa.int8()),
        ("missing_family_count", pa.int8()),
    ]
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


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
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


def _fsync_file(path: Path) -> None:
    # Windows requires a writable descriptor for a reliable FlushFileBuffers
    # call; a read-only descriptor can raise OSError with errno 9.
    with path.open("rb+") as handle:
        os.fsync(handle.fileno())


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def atomic_write_table(path: Path, table: pa.Table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.partial")
    pq.write_table(table, tmp, compression="zstd")
    _fsync_file(tmp)
    os.replace(tmp, path)


def table_from_rows(rows: Sequence[dict[str, Any]], schema: pa.Schema) -> pa.Table:
    return pa.Table.from_pylist(list(rows), schema=schema)


def safe_ticker(ticker: str) -> str:
    return quote(ticker, safe="._-")


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def normalize_date_value(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def load_config(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    config = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"Config is not a mapping: {path}")
    families = config.get("families")
    if not isinstance(families, dict) or tuple(families) != EXPECTED_FAMILIES:
        raise ValueError(f"Config families must be ordered exactly as {EXPECTED_FAMILIES}")
    scope = config.get("scope", {})
    parse_iso_date(str(scope["start_date_inclusive"]))
    parse_iso_date(str(scope["end_date_inclusive"]))
    if not bool(scope.get("target_scoped")):
        raise ValueError("This auditor requires scope.target_scoped=true")
    return config, sha256_bytes(raw)


def get_git_snapshot(repo_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"branch": None, "commit": None, "dirty_state": "unknown"}
    try:
        result["branch"] = subprocess.check_output(
            ["git", "-C", str(repo_root), "branch", "--show-current"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        result["commit"] = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        result["dirty_state"] = "clean" if not dirty.strip() else "dirty"
    except Exception:
        result["dirty_state"] = "unavailable"
    return result


def load_universe(config: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    universe_cfg = config["universe"]
    path = Path(str(universe_cfg["path"]))
    ticker_column = str(universe_cfg.get("ticker_column", "ticker"))
    if not path.is_file():
        raise FileNotFoundError(f"Universe artifact does not exist: {path}")
    parquet = pq.ParquetFile(path)
    if ticker_column not in parquet.schema_arrow.names:
        raise ValueError(f"Universe ticker column missing: {ticker_column}")
    values = parquet.read(columns=[ticker_column]).column(ticker_column).to_pylist()
    tickers = [str(value) for value in values if value is not None]
    expected = int(config["scope"]["expected_universe_members"])
    if len(tickers) != expected or len(set(tickers)) != expected:
        raise ValueError(
            f"Universe cardinality invariant failed: rows={len(tickers)} unique={len(set(tickers))} expected={expected}"
        )
    if "NA" not in tickers:
        raise ValueError("Literal ticker `NA` is absent from the governed universe")
    metadata = {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "metadata_rows": parquet.metadata.num_rows,
        "ticker_rows": len(tickers),
        "ticker_unique": len(set(tickers)),
        "literal_NA_count": sum(ticker == "NA" for ticker in tickers),
        "ticker_column": ticker_column,
    }
    return tickers, metadata


def select_tickers(config: dict[str, Any], universe: Sequence[str], mode: str, explicit: str) -> list[str]:
    universe_set = set(universe)
    if explicit:
        selected = [value.strip() for value in explicit.split(",") if value.strip()]
    elif mode == "probe":
        selected = [str(value) for value in config.get("probe", {}).get("tickers", [])]
    else:
        selected = list(universe)
    if not selected:
        raise ValueError("No tickers selected")
    if len(selected) != len(set(selected)):
        raise ValueError("Selected ticker list contains duplicates")
    missing = [ticker for ticker in selected if ticker not in universe_set]
    if missing:
        raise ValueError(f"Selected tickers are outside the governed universe: {missing}")
    return selected


def is_reparse_point(path: Path) -> bool:
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes  # type: ignore[attr-defined]
        return bool(attrs & REPARSE_POINT)
    except AttributeError:
        return path.is_symlink()
    except OSError:
        return False


def iter_parquet_files(root: Path) -> Iterator[Path]:
    if not root.is_dir():
        return
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda item: item.name.lower(), reverse=True)
        except OSError:
            continue
        for entry in entries:
            try:
                path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    if not is_reparse_point(path):
                        pending.append(path)
                elif entry.is_file(follow_symlinks=False) and entry.name.lower().endswith(".parquet"):
                    yield path
            except OSError:
                continue


def roster_for_family(spec: dict[str, Any], universe: set[str]) -> dict[str, Any]:
    root = Path(str(spec["root"]))
    template = str(spec["ticker_directory_template"])
    prefix, suffix = template.split("{ticker}")
    observed: set[str] = set()
    if root.is_dir():
        for entry in os.scandir(root):
            try:
                if not entry.is_dir(follow_symlinks=False) or entry.name.startswith("_"):
                    continue
                if not entry.name.startswith(prefix) or (suffix and not entry.name.endswith(suffix)):
                    continue
                end = len(entry.name) - len(suffix) if suffix else len(entry.name)
                observed.add(entry.name[len(prefix) : end])
            except OSError:
                continue
    missing = sorted(universe - observed)
    extra = sorted(observed - universe)
    return {
        "root": str(root.resolve()) if root.exists() else str(root),
        "root_exists": root.is_dir(),
        "observed_ticker_directory_count": len(observed),
        "expected_target_present_count": len(universe & observed),
        "missing_expected_count": len(missing),
        "extra_outside_target_count": len(extra),
        "missing_expected_sample": missing[:50],
        "extra_outside_target_sample": extra[:50],
        "observed_roster_sha256": stable_json_hash(sorted(observed)),
        "observed": observed,
        "missing": missing,
        "extra": extra,
    }


def derive_date_from_path(relative_path: str, strategy: str) -> date | None:
    normalized = relative_path.replace("\\", "/")
    if strategy == "path_ymd_parts":
        year_match = re.search(r"(?:^|/)year=(\d{4})(?:/|$)", normalized)
        month_match = re.search(r"(?:^|/)month=(\d{1,2})(?:/|$)", normalized)
        day_match = re.search(r"(?:^|/)day=(\d{1,2})(?:/|$)", normalized)
        if not (year_match and month_match and day_match):
            return None
        try:
            return date(int(year_match.group(1)), int(month_match.group(1)), int(day_match.group(1)))
        except ValueError:
            return None
    if strategy == "path_day_iso":
        match = re.search(r"(?:^|/)day=(\d{4}-\d{2}-\d{2})(?:/|$)", normalized)
        if not match:
            return None
        try:
            return date.fromisoformat(match.group(1))
        except ValueError:
            return None
    raise ValueError(f"Unsupported path date strategy: {strategy}")


def read_unique_dates_from_column(parquet: pq.ParquetFile, column: str) -> tuple[set[date], int]:
    dates: set[date] = set()
    invalid_values = 0
    for row_group in range(parquet.metadata.num_row_groups):
        chunked = parquet.read_row_group(row_group, columns=[column]).column(column)
        for chunk in chunked.chunks:
            for value in pc.unique(chunk).to_pylist():
                normalized = normalize_date_value(value)
                if normalized is None:
                    invalid_values += 1
                else:
                    dates.add(normalized)
    return dates, invalid_values


def inspect_parquet_file(
    *,
    path: Path,
    family: str,
    ticker: str,
    family_root: Path,
    spec: dict[str, Any],
    scope_start: date,
    scope_end: date,
) -> tuple[dict[str, Any], set[date]]:
    errors: list[str] = []
    messages: list[str] = []
    relative_path = str(path.relative_to(family_root)).replace("/", "\\")
    row: dict[str, Any] = {
        "family": family,
        "ticker": ticker,
        "absolute_path": str(path),
        "relative_path": relative_path,
        "file_exists": path.is_file(),
        "file_size_bytes": None,
        "magic_header_ok": False,
        "magic_footer_ok": False,
        "parquet_openable": False,
        "metadata_readable": False,
        "metadata_num_rows": None,
        "row_group_count": None,
        "schema_readable": False,
        "schema_fingerprint": None,
        "schema_columns_json": "[]",
        "missing_required_columns_json": "[]",
        "extra_columns_json": "[]",
        "required_schema_complete": False,
        "date_extraction_method": str(spec["date_strategy"]),
        "observed_date_count": 0,
        "first_observed_date": None,
        "last_observed_date": None,
        "out_of_scope_date_count": 0,
        "error_class": None,
        "error_message": None,
    }
    all_dates: set[date] = set()
    if not path.is_file():
        errors.append("FILE_MISSING")
        row["error_class"] = ";".join(errors)
        return row, set()
    try:
        size = path.stat().st_size
        row["file_size_bytes"] = size
    except OSError as exc:
        errors.append("FILE_STAT_FAILED")
        messages.append(repr(exc))
        row["error_class"] = ";".join(errors)
        row["error_message"] = " | ".join(messages)[:4000]
        return row, set()
    if size <= 0:
        errors.append("ZERO_BYTE_PARQUET")
    if size >= 8:
        try:
            with path.open("rb") as handle:
                row["magic_header_ok"] = handle.read(4) == b"PAR1"
                handle.seek(-4, os.SEEK_END)
                row["magic_footer_ok"] = handle.read(4) == b"PAR1"
        except OSError as exc:
            messages.append(f"magic:{exc!r}")
    if not row["magic_header_ok"]:
        errors.append("INVALID_PARQUET_HEADER")
    if not row["magic_footer_ok"]:
        errors.append("INVALID_PARQUET_FOOTER")

    parquet: pq.ParquetFile | None = None
    schema_columns: list[str] = []
    try:
        parquet = pq.ParquetFile(path)
        row["parquet_openable"] = True
        metadata = parquet.metadata
        if metadata is None:
            errors.append("PARQUET_METADATA_MISSING")
        else:
            row["metadata_readable"] = True
            row["metadata_num_rows"] = int(metadata.num_rows)
            row["row_group_count"] = int(metadata.num_row_groups)
            if metadata.num_rows <= 0:
                errors.append("EMPTY_PARQUET")
        schema = parquet.schema_arrow
        row["schema_readable"] = True
        schema_columns = list(schema.names)
        row["schema_fingerprint"] = sha256_bytes(str(schema).encode("utf-8"))
        row["schema_columns_json"] = json.dumps(schema_columns, ensure_ascii=False)
        required = [str(value) for value in spec.get("required_columns", [])]
        missing = sorted(set(required) - set(schema_columns))
        extra = sorted(set(schema_columns) - set(required))
        row["missing_required_columns_json"] = json.dumps(missing, ensure_ascii=False)
        row["extra_columns_json"] = json.dumps(extra, ensure_ascii=False)
        row["required_schema_complete"] = not missing
        if missing:
            errors.append("SCHEMA_MISSING_REQUIRED_COLUMNS")
            messages.append(f"missing_required={missing}")
    except Exception as exc:
        errors.append("UNREADABLE_PARQUET")
        messages.append(repr(exc))

    if parquet is not None and row["metadata_readable"] and int(row["metadata_num_rows"] or 0) > 0:
        strategy = str(spec["date_strategy"])
        if strategy == "column":
            column = str(spec["date_column"])
            if column not in schema_columns:
                errors.append("DATE_COLUMN_MISSING")
            else:
                try:
                    all_dates, invalid = read_unique_dates_from_column(parquet, column)
                    if invalid:
                        errors.append("UNPARSEABLE_DATE_VALUE")
                        messages.append(f"unparseable_unique_date_values={invalid}")
                except Exception as exc:
                    errors.append("DATE_COLUMN_READ_FAILED")
                    messages.append(repr(exc))
        else:
            parsed = derive_date_from_path(relative_path, strategy)
            if parsed is None:
                errors.append("PATH_DATE_UNPARSEABLE")
            else:
                all_dates = {parsed}

    in_scope = {value for value in all_dates if scope_start <= value <= scope_end}
    out_scope = all_dates - in_scope
    row["observed_date_count"] = len(in_scope)
    row["first_observed_date"] = min(in_scope) if in_scope else None
    row["last_observed_date"] = max(in_scope) if in_scope else None
    row["out_of_scope_date_count"] = len(out_scope)
    unique_errors = list(dict.fromkeys(errors))
    row["error_class"] = ";".join(unique_errors) if unique_errors else None
    row["error_message"] = " | ".join(messages)[:4000] if messages else None
    return row, in_scope


def runtime_paths(run_root: Path) -> dict[str, Path]:
    return {
        "control": run_root / "00_control",
        "inventory": run_root / "01_inventory",
        "coverage": run_root / "02_ticker_coverage",
        "differences": run_root / "03_differences",
        "closeout": run_root / "04_closeout",
    }


def ensure_runtime_dirs(run_root: Path) -> dict[str, Path]:
    paths = runtime_paths(run_root)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    (paths["control"] / "task_results").mkdir(parents=True, exist_ok=True)
    return paths


def task_paths(run_root: Path, family: str, ticker: str) -> dict[str, Path]:
    paths = runtime_paths(run_root)
    safe = safe_ticker(ticker)
    return {
        "inventory": paths["inventory"] / family / f"ticker={safe}" / "inventory.parquet",
        "dates": paths["coverage"] / family / f"ticker={safe}" / "ticker_dates.parquet",
        "manifest": paths["control"] / "task_results" / family / f"ticker={safe}.json",
    }


def task_manifest_valid(path: Path, run_contract_sha256: str) -> bool:
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("run_contract_sha256") != run_contract_sha256:
            return False
        for artifact in payload.get("artifacts", []):
            artifact_path = Path(str(artifact["path"]))
            if not artifact_path.is_file():
                return False
            if artifact_path.stat().st_size != int(artifact["bytes"]):
                return False
            if sha256_file(artifact_path) != str(artifact["sha256"]):
                return False
        return payload.get("status") == "committed"
    except Exception:
        return False


def connect_ledger(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=60)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def with_sql_retry(operation: Any, attempts: int = 12) -> Any:
    delay = 0.05
    for attempt in range(attempts):
        try:
            return operation()
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or attempt + 1 == attempts:
                raise
            time.sleep(delay)
            delay = min(delay * 1.7, 1.0)
    raise AssertionError("unreachable")


def initialize_ledger(
    ledger_path: Path,
    *,
    run_id: str,
    run_contract_sha256: str,
    families: Sequence[str],
    tickers: Sequence[str],
) -> None:
    connection = connect_ledger(ledger_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS run_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                family TEXT NOT NULL,
                ticker TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt INTEGER NOT NULL DEFAULT 0,
                worker_pid INTEGER,
                started_at_utc TEXT,
                ended_at_utc TEXT,
                source_dir_exists INTEGER,
                file_count INTEGER,
                source_bytes INTEGER,
                date_count INTEGER,
                error_file_count INTEGER,
                task_manifest_path TEXT,
                error_message TEXT,
                PRIMARY KEY (family, ticker)
            );
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            """
        )
        connection.execute(
            "INSERT OR REPLACE INTO run_metadata(key,value) VALUES('run_id',?)", (run_id,)
        )
        connection.execute(
            "INSERT OR REPLACE INTO run_metadata(key,value) VALUES('run_contract_sha256',?)",
            (run_contract_sha256,),
        )
        connection.executemany(
            "INSERT OR IGNORE INTO tasks(family,ticker,status) VALUES(?,?,'pending')",
            [(family, ticker) for family in families for ticker in tickers],
        )
        connection.commit()
    finally:
        connection.close()


def ledger_mark_pending(ledger_path: Path, family: str, ticker: str, message: str = "") -> None:
    def operation() -> None:
        connection = connect_ledger(ledger_path)
        try:
            connection.execute(
                "UPDATE tasks SET status='pending',worker_pid=NULL,started_at_utc=NULL,ended_at_utc=NULL,error_message=? "
                "WHERE family=? AND ticker=?",
                (message or None, family, ticker),
            )
            connection.commit()
        finally:
            connection.close()

    with_sql_retry(operation)


def ledger_mark_running(ledger_path: Path, family: str, ticker: str) -> None:
    def operation() -> None:
        connection = connect_ledger(ledger_path)
        try:
            connection.execute(
                "UPDATE tasks SET status='running',attempt=attempt+1,worker_pid=?,started_at_utc=?,"
                "ended_at_utc=NULL,error_message=NULL WHERE family=? AND ticker=?",
                (os.getpid(), iso_utc(), family, ticker),
            )
            connection.commit()
        finally:
            connection.close()

    with_sql_retry(operation)


def ledger_mark_committed(ledger_path: Path, family: str, ticker: str, result: dict[str, Any]) -> None:
    def operation() -> None:
        connection = connect_ledger(ledger_path)
        try:
            connection.execute(
                "UPDATE tasks SET status='committed',worker_pid=?,ended_at_utc=?,source_dir_exists=?,"
                "file_count=?,source_bytes=?,date_count=?,error_file_count=?,task_manifest_path=?,error_message=NULL "
                "WHERE family=? AND ticker=?",
                (
                    os.getpid(),
                    iso_utc(),
                    int(bool(result["source_ticker_dir_exists"])),
                    int(result["file_count"]),
                    int(result["source_bytes"]),
                    int(result["date_count"]),
                    int(result["error_file_count"]),
                    str(result["task_manifest_path"]),
                    family,
                    ticker,
                ),
            )
            connection.commit()
        finally:
            connection.close()

    with_sql_retry(operation)


def ledger_mark_failed(ledger_path: Path, family: str, ticker: str, message: str) -> None:
    def operation() -> None:
        connection = connect_ledger(ledger_path)
        try:
            connection.execute(
                "UPDATE tasks SET status='failed',worker_pid=?,ended_at_utc=?,error_message=? "
                "WHERE family=? AND ticker=?",
                (os.getpid(), iso_utc(), message[:4000], family, ticker),
            )
            connection.commit()
        finally:
            connection.close()

    with_sql_retry(operation)


def ledger_task_status(ledger_path: Path, family: str, ticker: str) -> str:
    connection = connect_ledger(ledger_path)
    try:
        row = connection.execute(
            "SELECT status FROM tasks WHERE family=? AND ticker=?", (family, ticker)
        ).fetchone()
        return str(row[0]) if row else "missing"
    finally:
        connection.close()


def ledger_snapshot(ledger_path: Path) -> dict[str, Any]:
    connection = connect_ledger(ledger_path)
    try:
        status_counts = {
            str(status): int(count)
            for status, count in connection.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status")
        }
        family_rows = connection.execute(
            "SELECT family,status,COUNT(*) FROM tasks GROUP BY family,status ORDER BY family,status"
        ).fetchall()
        family_counts: dict[str, dict[str, int]] = {}
        for family, status, count in family_rows:
            family_counts.setdefault(str(family), {})[str(status)] = int(count)
        totals = connection.execute(
            "SELECT COALESCE(SUM(file_count),0),COALESCE(SUM(source_bytes),0),"
            "COALESCE(SUM(date_count),0),COALESCE(SUM(error_file_count),0) FROM tasks WHERE status='committed'"
        ).fetchone()
        active = [
            {"family": family, "ticker": ticker, "worker_pid": pid, "started_at_utc": started}
            for family, ticker, pid, started in connection.execute(
                "SELECT family,ticker,worker_pid,started_at_utc FROM tasks WHERE status='running' ORDER BY family"
            )
        ]
        return {
            "status_counts": status_counts,
            "family_counts": family_counts,
            "committed_file_count": int(totals[0]),
            "committed_source_bytes": int(totals[1]),
            "committed_date_count": int(totals[2]),
            "committed_error_file_count": int(totals[3]),
            "active_tasks": active,
        }
    finally:
        connection.close()


def audit_ticker_task(
    *,
    config: dict[str, Any],
    run_root: Path,
    family: str,
    ticker: str,
    run_id: str,
    run_contract_sha256: str,
) -> dict[str, Any]:
    started = utc_now()
    spec = config["families"][family]
    family_root = Path(str(spec["root"]))
    ticker_dir = family_root / str(spec["ticker_directory_template"]).format(ticker=ticker)
    scope_start = parse_iso_date(str(config["scope"]["start_date_inclusive"]))
    scope_end = parse_iso_date(str(config["scope"]["end_date_inclusive"]))
    paths = task_paths(run_root, family, ticker)

    inventory_rows: list[dict[str, Any]] = []
    observed_dates: set[date] = set()
    if ticker_dir.is_dir():
        for parquet_path in iter_parquet_files(ticker_dir):
            row, dates = inspect_parquet_file(
                path=parquet_path,
                family=family,
                ticker=ticker,
                family_root=family_root,
                spec=spec,
                scope_start=scope_start,
                scope_end=scope_end,
            )
            inventory_rows.append(row)
            observed_dates.update(dates)

    date_rows = [
        {"family": family, "ticker": ticker, "observed_date": observed_date}
        for observed_date in sorted(observed_dates)
    ]
    atomic_write_table(paths["inventory"], table_from_rows(inventory_rows, INVENTORY_SCHEMA))
    atomic_write_table(paths["dates"], table_from_rows(date_rows, TICKER_DATE_SCHEMA))

    artifacts = []
    for artifact_path in (paths["inventory"], paths["dates"]):
        artifacts.append(
            {
                "path": str(artifact_path),
                "bytes": artifact_path.stat().st_size,
                "sha256": sha256_file(artifact_path),
            }
        )
    task_payload: dict[str, Any] = {
        "run_id": run_id,
        "run_contract_sha256": run_contract_sha256,
        "status": "committed",
        "family": family,
        "ticker": ticker,
        "source_ticker_directory": str(ticker_dir),
        "source_ticker_dir_exists": ticker_dir.is_dir(),
        "started_at_utc": iso_utc(started),
        "ended_at_utc": iso_utc(),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 3),
        "file_count": len(inventory_rows),
        "source_bytes": sum(int(row["file_size_bytes"] or 0) for row in inventory_rows),
        "date_count": len(observed_dates),
        "first_observed_date": min(observed_dates).isoformat() if observed_dates else None,
        "last_observed_date": max(observed_dates).isoformat() if observed_dates else None,
        "error_file_count": sum(bool(row["error_class"]) for row in inventory_rows),
        "zero_byte_file_count": sum("ZERO_BYTE_PARQUET" in str(row["error_class"]) for row in inventory_rows),
        "empty_file_count": sum("EMPTY_PARQUET" in str(row["error_class"]) for row in inventory_rows),
        "unreadable_file_count": sum("UNREADABLE_PARQUET" in str(row["error_class"]) for row in inventory_rows),
        "schema_incomplete_file_count": sum(
            "SCHEMA_MISSING_REQUIRED_COLUMNS" in str(row["error_class"]) for row in inventory_rows
        ),
        "artifacts": artifacts,
        "task_manifest_path": str(paths["manifest"]),
    }
    atomic_write_json(paths["manifest"], task_payload)
    return task_payload


def _append_worker_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{iso_utc()} {message}\n")
        handle.flush()


def family_worker(
    config: dict[str, Any],
    run_root_s: str,
    family: str,
    tickers: list[str],
    run_id: str,
    run_contract_sha256: str,
    stop_event: Any,
) -> None:
    run_root = Path(run_root_s)
    ledger_path = runtime_paths(run_root)["control"] / "run_state.sqlite"
    worker_log = runtime_paths(run_root)["control"] / f"family_{family}.log"
    _append_worker_log(worker_log, f"worker_started pid={os.getpid()} ticker_count={len(tickers)}")
    for ticker in tickers:
        if stop_event is not None and stop_event.is_set():
            _append_worker_log(worker_log, "stop_event_observed")
            break
        manifest_path = task_paths(run_root, family, ticker)["manifest"]
        if ledger_task_status(ledger_path, family, ticker) == "committed" and task_manifest_valid(
            manifest_path, run_contract_sha256
        ):
            continue
        ledger_mark_running(ledger_path, family, ticker)
        try:
            result = audit_ticker_task(
                config=config,
                run_root=run_root,
                family=family,
                ticker=ticker,
                run_id=run_id,
                run_contract_sha256=run_contract_sha256,
            )
            ledger_mark_committed(ledger_path, family, ticker, result)
            _append_worker_log(
                worker_log,
                f"committed ticker={ticker} files={result['file_count']} dates={result['date_count']} "
                f"error_files={result['error_file_count']}",
            )
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            ledger_mark_failed(ledger_path, family, ticker, message)
            _append_worker_log(worker_log, f"failed ticker={ticker} error={message}\n{traceback.format_exc()}")
    _append_worker_log(worker_log, "worker_ended")


def adopt_or_reset_tasks(
    ledger_path: Path,
    run_root: Path,
    families: Sequence[str],
    tickers: Sequence[str],
    run_contract_sha256: str,
) -> dict[str, int]:
    adopted = 0
    reset = 0
    for family in families:
        for ticker in tickers:
            manifest_path = task_paths(run_root, family, ticker)["manifest"]
            if task_manifest_valid(manifest_path, run_contract_sha256):
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                ledger_mark_committed(ledger_path, family, ticker, payload)
                adopted += 1
            else:
                status = ledger_task_status(ledger_path, family, ticker)
                if status != "pending":
                    ledger_mark_pending(ledger_path, family, ticker, "invalid_or_missing_committed_artifact")
                    reset += 1
    return {"adopted": adopted, "reset": reset}


def configure_parent_logging(run_root: Path) -> logging.Logger:
    logger = logging.getLogger(f"core_market_raw_alignment.{run_root.name}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)sZ %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
    formatter.converter = time.gmtime
    file_handler = logging.FileHandler(runtime_paths(run_root)["control"] / "audit.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def heartbeat_payload(
    *,
    run_id: str,
    run_root: Path,
    started: datetime,
    stage: str,
    status: str,
    ledger_path: Path,
    child_pids: Sequence[int],
) -> dict[str, Any]:
    snapshot = ledger_snapshot(ledger_path)
    output_free_gb = None
    try:
        output_free_gb = round(shutil.disk_usage(run_root.anchor).free / (1024**3), 3)
    except OSError:
        pass
    process_cpu_pct = None
    process_rss_bytes = None
    if psutil is not None:
        try:
            current = psutil.Process(os.getpid())
            processes = [current] + [psutil.Process(pid) for pid in child_pids if psutil.pid_exists(pid)]
            process_cpu_pct = round(sum(process.cpu_percent(interval=None) for process in processes), 3)
            process_rss_bytes = sum(process.memory_info().rss for process in processes)
        except Exception:
            pass
    total_count = sum(snapshot["status_counts"].values())
    committed = int(snapshot["status_counts"].get("committed", 0))
    return {
        "run_id": run_id,
        "status": status,
        "stage": stage,
        "observed_at_utc": iso_utc(),
        "started_at_utc": iso_utc(started),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 1),
        "wrapper_pid": os.getpid(),
        "active_pid": os.getpid(),
        "child_pids": list(child_pids),
        "active_worker_count": sum(1 for pid in child_pids if _pid_alive(pid)),
        "current_index": committed,
        "total_count": total_count,
        "progress_pct": round(100 * committed / total_count, 4) if total_count else 0.0,
        "family_counts": snapshot["family_counts"],
        "status_counts": snapshot["status_counts"],
        "active_tasks": snapshot["active_tasks"],
        "committed_file_count": snapshot["committed_file_count"],
        "committed_source_bytes": snapshot["committed_source_bytes"],
        "committed_date_count": snapshot["committed_date_count"],
        "committed_error_file_count": snapshot["committed_error_file_count"],
        "process_cpu_pct": process_cpu_pct,
        "process_rss_bytes": process_rss_bytes,
        "output_free_gb": output_free_gb,
        "run_root": str(run_root),
        "log_path": str(runtime_paths(run_root)["control"] / "audit.log"),
    }


def _pid_alive(pid: int) -> bool:
    try:
        if psutil is not None:
            return bool(psutil.pid_exists(pid))
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def write_heartbeat(run_root: Path, payload: dict[str, Any]) -> None:
    control = runtime_paths(run_root)["control"]
    atomic_write_json(control / "heartbeat.json", payload)
    with (control / "heartbeat.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()


def stream_consolidate(shards: Iterable[Path], destination: Path, schema: pa.Schema) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(f"{destination.name}.{os.getpid()}.{time.time_ns()}.partial")
    rows = 0
    writer = pq.ParquetWriter(tmp, schema=schema, compression="zstd")
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
    _fsync_file(tmp)
    os.replace(tmp, destination)
    return rows


def load_ticker_dates(run_root: Path, family: str, ticker: str) -> set[date]:
    path = task_paths(run_root, family, ticker)["dates"]
    if not path.is_file():
        return set()
    values = pq.ParquetFile(path).read(columns=["observed_date"]).column("observed_date").to_pylist()
    return {value for value in values if isinstance(value, date)}


def load_task_manifest(run_root: Path, family: str, ticker: str) -> dict[str, Any]:
    path = task_paths(run_root, family, ticker)["manifest"]
    return json.loads(path.read_text(encoding="utf-8"))


def _inventory_error_writers(differences_root: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    names = {
        "all": "parquet_errors.csv",
        "zero": "zero_byte_parquets.csv",
        "unreadable": "unreadable_parquets.csv",
        "empty": "empty_parquets.csv",
        "schema": "unreadable_schemas.csv",
        "schema_incomplete": "schema_incomplete_parquets.csv",
        "combined": "unreadable_or_empty_parquets.csv",
    }
    paths = {key: differences_root / value for key, value in names.items()}
    fieldnames = [
        "family",
        "ticker",
        "absolute_path",
        "relative_path",
        "file_size_bytes",
        "metadata_num_rows",
        "schema_fingerprint",
        "missing_required_columns_json",
        "error_class",
        "error_message",
    ]
    writers: dict[str, Any] = {}
    for key, path in paths.items():
        handle = path.open("w", encoding="utf-8", newline="")
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writers[key] = (handle, writer)
    return writers, paths


def _write_inventory_errors(writers: dict[str, Any], row: dict[str, Any]) -> None:
    error = str(row.get("error_class") or "")
    keys: list[str] = []
    if error:
        keys.append("all")
    if "ZERO_BYTE_PARQUET" in error:
        keys.append("zero")
    if "UNREADABLE_PARQUET" in error or "INVALID_PARQUET_HEADER" in error or "INVALID_PARQUET_FOOTER" in error:
        keys.append("unreadable")
    if "EMPTY_PARQUET" in error:
        keys.append("empty")
    if not bool(row.get("schema_readable")):
        keys.append("schema")
    if "SCHEMA_MISSING_REQUIRED_COLUMNS" in error:
        keys.append("schema_incomplete")
    if error:
        keys.append("combined")
    for key in dict.fromkeys(keys):
        writers[key][1].writerow(row)


def _close_writers(writers: dict[str, Any]) -> None:
    for handle, _writer in writers.values():
        handle.flush()
        handle.close()


def coverage_schema() -> pa.Schema:
    fields: list[tuple[str, pa.DataType]] = [("ticker", pa.string())]
    for family in EXPECTED_FAMILIES:
        stem = FAMILY_OUTPUT_STEMS[family]
        fields.extend(
            [
                (f"{stem}_directory_exists", pa.bool_()),
                (f"{stem}_file_count", pa.int32()),
                (f"{stem}_date_count", pa.int32()),
                (f"{stem}_first_date", pa.date32()),
                (f"{stem}_last_date", pa.date32()),
                (f"{stem}_error_file_count", pa.int32()),
            ]
        )
    fields.extend(
        [
            ("all_target_directories_present", pa.bool_()),
            ("all_families_have_dates", pa.bool_()),
            ("first_date_equal", pa.bool_()),
            ("last_date_equal", pa.bool_()),
            ("window_equal", pa.bool_()),
            ("observed_date_set_equal", pa.bool_()),
        ]
    )
    return pa.schema(fields)


def finalize_run(config: dict[str, Any], run_root: Path, pre_manifest: dict[str, Any]) -> dict[str, Any]:
    paths = runtime_paths(run_root)
    tickers = [str(value) for value in pre_manifest["selected_tickers"]]
    mode = str(pre_manifest["mode"])
    expected_full = int(config["scope"]["expected_universe_members"])
    universe_set = set(pre_manifest["universe_tickers"])

    inventory_error_writers, error_paths = _inventory_error_writers(paths["differences"])
    inventory_rows_by_family: dict[str, int] = {}
    ticker_date_rows_by_family: dict[str, int] = {}
    try:
        for family in EXPECTED_FAMILIES:
            stem = FAMILY_OUTPUT_STEMS[family]
            inventory_shards = [task_paths(run_root, family, ticker)["inventory"] for ticker in tickers]
            date_shards = [task_paths(run_root, family, ticker)["dates"] for ticker in tickers]
            destination = paths["inventory"] / f"{stem}_inventory.parquet"
            tmp = destination.with_name(f"{destination.name}.{os.getpid()}.{time.time_ns()}.partial")
            writer = pq.ParquetWriter(tmp, INVENTORY_SCHEMA, compression="zstd")
            family_rows = 0
            try:
                for shard in inventory_shards:
                    table = pq.ParquetFile(shard).read()
                    if table.schema != INVENTORY_SCHEMA:
                        table = table.cast(INVENTORY_SCHEMA)
                    if table.num_rows:
                        writer.write_table(table)
                        family_rows += table.num_rows
                        for row in table.to_pylist():
                            _write_inventory_errors(inventory_error_writers, row)
            finally:
                writer.close()
            _fsync_file(tmp)
            os.replace(tmp, destination)
            inventory_rows_by_family[family] = family_rows
            ticker_date_rows_by_family[family] = stream_consolidate(
                date_shards,
                paths["coverage"] / f"{stem}_ticker_dates.parquet",
                TICKER_DATE_SCHEMA,
            )
    finally:
        _close_writers(inventory_error_writers)

    rosters = {family: roster_for_family(config["families"][family], universe_set) for family in EXPECTED_FAMILIES}
    ticker_set_path = paths["differences"] / "ticker_set_differences.csv"
    with ticker_set_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["family", "difference_type", "ticker", "is_target_scope", "is_blocking"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for family in EXPECTED_FAMILIES:
            for ticker in rosters[family]["missing"]:
                writer.writerow(
                    {
                        "family": family,
                        "difference_type": "MISSING_EXPECTED_TICKER",
                        "ticker": ticker,
                        "is_target_scope": True,
                        "is_blocking": True,
                    }
                )
            for ticker in rosters[family]["extra"]:
                writer.writerow(
                    {
                        "family": family,
                        "difference_type": "EXTRA_TICKER_OUTSIDE_TARGET",
                        "ticker": ticker,
                        "is_target_scope": False,
                        "is_blocking": False,
                    }
                )

    coverage_rows: list[dict[str, Any]] = []
    window_difference_path = paths["differences"] / "ticker_window_differences.csv"
    date_difference_path = paths["differences"] / "ticker_date_differences.parquet"
    date_difference_tmp = date_difference_path.with_name(
        f"{date_difference_path.name}.{os.getpid()}.{time.time_ns()}.partial"
    )
    date_difference_writer = pq.ParquetWriter(
        date_difference_tmp, TICKER_DATE_DIFFERENCE_SCHEMA, compression="zstd"
    )
    ticker_date_difference_rows = 0
    tickers_with_date_set_mismatch = 0
    tickers_with_window_mismatch = 0
    latest_by_family: dict[str, date | None] = {family: None for family in EXPECTED_FAMILIES}
    with window_difference_path.open("w", encoding="utf-8", newline="") as window_handle:
        window_fields = ["ticker", "difference_type"]
        for family in EXPECTED_FAMILIES:
            stem = FAMILY_OUTPUT_STEMS[family]
            window_fields.extend([f"{stem}_first_date", f"{stem}_last_date", f"{stem}_date_count"])
        window_writer = csv.DictWriter(window_handle, fieldnames=window_fields)
        window_writer.writeheader()
        try:
            for ticker in tickers:
                date_sets = {family: load_ticker_dates(run_root, family, ticker) for family in EXPECTED_FAMILIES}
                manifests = {family: load_task_manifest(run_root, family, ticker) for family in EXPECTED_FAMILIES}
                row: dict[str, Any] = {"ticker": ticker}
                first_values: list[date | None] = []
                last_values: list[date | None] = []
                for family in EXPECTED_FAMILIES:
                    stem = FAMILY_OUTPUT_STEMS[family]
                    values = date_sets[family]
                    first_value = min(values) if values else None
                    last_value = max(values) if values else None
                    if last_value is not None and (
                        latest_by_family[family] is None or last_value > latest_by_family[family]
                    ):
                        latest_by_family[family] = last_value
                    first_values.append(first_value)
                    last_values.append(last_value)
                    manifest = manifests[family]
                    row[f"{stem}_directory_exists"] = bool(manifest["source_ticker_dir_exists"])
                    row[f"{stem}_file_count"] = int(manifest["file_count"])
                    row[f"{stem}_date_count"] = len(values)
                    row[f"{stem}_first_date"] = first_value
                    row[f"{stem}_last_date"] = last_value
                    row[f"{stem}_error_file_count"] = int(manifest["error_file_count"])
                row["all_target_directories_present"] = all(
                    bool(manifests[family]["source_ticker_dir_exists"]) for family in EXPECTED_FAMILIES
                )
                row["all_families_have_dates"] = all(bool(date_sets[family]) for family in EXPECTED_FAMILIES)
                row["first_date_equal"] = len(set(first_values)) == 1
                row["last_date_equal"] = len(set(last_values)) == 1
                row["window_equal"] = bool(
                    row["all_families_have_dates"] and row["first_date_equal"] and row["last_date_equal"]
                )
                signatures = {tuple(sorted(date_sets[family])) for family in EXPECTED_FAMILIES}
                row["observed_date_set_equal"] = bool(row["all_families_have_dates"] and len(signatures) == 1)
                coverage_rows.append(row)

                if not row["window_equal"]:
                    tickers_with_window_mismatch += 1
                    window_row: dict[str, Any] = {"ticker": ticker, "difference_type": "WINDOW_MISMATCH"}
                    for family in EXPECTED_FAMILIES:
                        stem = FAMILY_OUTPUT_STEMS[family]
                        window_row[f"{stem}_first_date"] = row[f"{stem}_first_date"]
                        window_row[f"{stem}_last_date"] = row[f"{stem}_last_date"]
                        window_row[f"{stem}_date_count"] = row[f"{stem}_date_count"]
                    window_writer.writerow(window_row)

                if not row["observed_date_set_equal"]:
                    tickers_with_date_set_mismatch += 1
                    union = set().union(*(date_sets[family] for family in EXPECTED_FAMILIES))
                    difference_rows: list[dict[str, Any]] = []
                    for observed_date in sorted(union):
                        flags = [observed_date in date_sets[family] for family in EXPECTED_FAMILIES]
                        if all(flags):
                            continue
                        difference_rows.append(
                            {
                                "ticker": ticker,
                                "observed_date": observed_date,
                                "present_in_ohlcv_daily": flags[0],
                                "present_in_ohlcv_1m": flags[1],
                                "present_in_quotes": flags[2],
                                "present_in_trades": flags[3],
                                "present_family_count": sum(flags),
                                "missing_family_count": len(flags) - sum(flags),
                            }
                        )
                    if difference_rows:
                        table = table_from_rows(difference_rows, TICKER_DATE_DIFFERENCE_SCHEMA)
                        date_difference_writer.write_table(table)
                        ticker_date_difference_rows += table.num_rows
        finally:
            date_difference_writer.close()
    _fsync_file(date_difference_tmp)
    os.replace(date_difference_tmp, date_difference_path)

    atomic_write_table(
        paths["coverage"] / "ticker_family_coverage.parquet",
        table_from_rows(coverage_rows, coverage_schema()),
    )

    error_counts: dict[str, int] = {}
    for key, path in error_paths.items():
        with path.open("r", encoding="utf-8", newline="") as handle:
            error_counts[key] = max(sum(1 for _ in handle) - 1, 0)

    missing_expected_by_family = {family: len(rosters[family]["missing"]) for family in EXPECTED_FAMILIES}
    extra_by_family = {family: len(rosters[family]["extra"]) for family in EXPECTED_FAMILIES}
    missing_expected_union = set().union(*(set(rosters[family]["missing"]) for family in EXPECTED_FAMILIES))
    missing_expected_pairs = sum(missing_expected_by_family.values())
    no_directory_pairs = sum(
        not bool(row[f"{FAMILY_OUTPUT_STEMS[family]}_directory_exists"])
        for row in coverage_rows
        for family in EXPECTED_FAMILIES
    )
    no_parquet_pairs = sum(
        int(row[f"{FAMILY_OUTPUT_STEMS[family]}_file_count"]) == 0
        for row in coverage_rows
        for family in EXPECTED_FAMILIES
    )
    no_date_pairs = sum(
        int(row[f"{FAMILY_OUTPUT_STEMS[family]}_date_count"]) == 0
        for row in coverage_rows
        for family in EXPECTED_FAMILIES
    )
    is_full_universe = len(tickers) == expected_full and set(tickers) == universe_set
    requested_scope_end = parse_iso_date(str(config["scope"]["end_date_inclusive"]))
    scope_end_reached_by_family = {
        family: latest_by_family[family] == requested_scope_end for family in EXPECTED_FAMILIES
    }
    blocking_counts = {
        "missing_expected_tickers_any_family": len(missing_expected_union),
        "missing_expected_ticker_family_pairs": missing_expected_pairs,
        "selected_ticker_family_pairs_without_directory": no_directory_pairs,
        "selected_ticker_family_pairs_without_parquets": no_parquet_pairs,
        "selected_ticker_family_pairs_without_dates": no_date_pairs,
        "parquets_with_any_error": error_counts["all"],
        "zero_byte_parquets": error_counts["zero"],
        "unreadable_parquets": error_counts["unreadable"],
        "empty_parquets": error_counts["empty"],
        "unreadable_schemas": error_counts["schema"],
        "schema_incomplete_parquets": error_counts["schema_incomplete"],
        "tickers_with_window_mismatch": tickers_with_window_mismatch,
        "tickers_with_date_set_mismatch": tickers_with_date_set_mismatch,
        "ticker_date_difference_rows": ticker_date_difference_rows,
        "full_universe_families_not_reaching_scope_end": (
            sum(not value for value in scope_end_reached_by_family.values()) if is_full_universe else 0
        ),
    }
    selected_scope_pass = all(value == 0 for value in blocking_counts.values())
    if mode == "full":
        dataset_verdict = "PASS" if selected_scope_pass and is_full_universe else "FAIL_WITH_EXACT_DIFFERENCES_REPORTED"
    else:
        dataset_verdict = "PROBE_COMPLETED_PASS" if selected_scope_pass else "PROBE_COMPLETED_WITH_DIFFERENCES"

    summary = {
        "run_id": pre_manifest["run_id"],
        "auditor_version": AUDITOR_VERSION,
        "technical_status": "COMPLETED",
        "dataset_verdict": dataset_verdict,
        "mode": mode,
        "target_scoped": True,
        "is_full_universe": is_full_universe,
        "expected_universe_members": expected_full,
        "selected_ticker_count": len(tickers),
        "scope_start_inclusive": config["scope"]["start_date_inclusive"],
        "scope_end_inclusive": config["scope"]["end_date_inclusive"],
        "selected_scope_pass": selected_scope_pass,
        "missing_expected_tickers_by_family": missing_expected_by_family,
        "extra_tickers_outside_target_by_family": extra_by_family,
        "extra_tickers_outside_target_are_blocking": False,
        "blocking_counts": blocking_counts,
        "inventory_rows_by_family": inventory_rows_by_family,
        "ticker_date_rows_by_family": ticker_date_rows_by_family,
        "latest_observed_date_by_family": {
            family: value.isoformat() if value else None for family, value in latest_by_family.items()
        },
        "requested_scope_end_reached_by_family": scope_end_reached_by_family,
        "completed_at_utc": iso_utc(),
    }
    atomic_write_json(paths["closeout"] / "audit_summary.json", summary)
    summary_csv_path = paths["closeout"] / "audit_summary.csv"
    scalar_summary = {
        "run_id": summary["run_id"],
        "technical_status": summary["technical_status"],
        "dataset_verdict": summary["dataset_verdict"],
        "mode": mode,
        "expected_universe_members": expected_full,
        "selected_ticker_count": len(tickers),
        "selected_scope_pass": selected_scope_pass,
        **blocking_counts,
    }
    with summary_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scalar_summary))
        writer.writeheader()
        writer.writerow(scalar_summary)

    report_lines = [
        "# Core Market RAW Alignment Audit",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Technical status: `{summary['technical_status']}`",
        f"- Dataset verdict: `{summary['dataset_verdict']}`",
        f"- Mode: `{mode}`",
        f"- Selected tickers: `{len(tickers)}` of `{expected_full}`",
        f"- Requested scope: `{summary['scope_start_inclusive']}` through `{summary['scope_end_inclusive']}` inclusive",
        "- Extras outside the governed LT1B target are reported but non-blocking.",
        "",
        "## Blocking counts",
        "",
        "```json",
        json.dumps(blocking_counts, indent=2, sort_keys=True),
        "```",
        "",
        "## Latest observed date by family",
        "",
        "```json",
        json.dumps(summary["latest_observed_date_by_family"], indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "This audit certifies only physical readability, minimum required schema and exact target ticker-date alignment.",
        "It does not certify economic values, session content, provider completeness or market-event correctness.",
        "",
    ]
    atomic_write_text(paths["closeout"] / "CORE_MARKET_RAW_ALIGNMENT_AUDIT.md", "\n".join(report_lines))

    canonical_artifacts = [
        *(paths["inventory"] / f"{FAMILY_OUTPUT_STEMS[family]}_inventory.parquet" for family in EXPECTED_FAMILIES),
        *(paths["coverage"] / f"{FAMILY_OUTPUT_STEMS[family]}_ticker_dates.parquet" for family in EXPECTED_FAMILIES),
        paths["coverage"] / "ticker_family_coverage.parquet",
        ticker_set_path,
        window_difference_path,
        date_difference_path,
        *error_paths.values(),
        paths["closeout"] / "audit_summary.json",
        summary_csv_path,
        paths["closeout"] / "CORE_MARKET_RAW_ALIGNMENT_AUDIT.md",
    ]
    manifest = {
        "run_id": summary["run_id"],
        "status": "completed",
        "technical_status": summary["technical_status"],
        "dataset_verdict": summary["dataset_verdict"],
        "run_contract_sha256": pre_manifest["run_contract_sha256"],
        "pre_manifest_path": str(paths["control"] / "pre_manifest.json"),
        "ledger_path": str(paths["control"] / "run_state.sqlite"),
        "artifact_count": len(canonical_artifacts),
        "artifacts": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in canonical_artifacts
        ],
        "completed_at_utc": iso_utc(),
    }
    atomic_write_json(paths["closeout"] / "final_manifest.json", manifest)
    return summary


def prepare_pre_manifest(
    *,
    config: dict[str, Any],
    config_path: Path,
    config_sha256: str,
    universe: list[str],
    universe_metadata: dict[str, Any],
    selected_tickers: list[str],
    mode: str,
    run_id: str,
    run_root: Path,
) -> dict[str, Any]:
    implementation_path = Path(__file__).resolve()
    implementation_sha = sha256_file(implementation_path)
    selected_sha = stable_json_hash(selected_tickers)
    run_contract = {
        "auditor_version": AUDITOR_VERSION,
        "config_sha256": config_sha256,
        "universe_sha256": universe_metadata["sha256"],
        "selected_tickers_sha256": selected_sha,
        "implementation_sha256": implementation_sha,
        "scope_start": config["scope"]["start_date_inclusive"],
        "scope_end": config["scope"]["end_date_inclusive"],
        "families": list(EXPECTED_FAMILIES),
        "mode": mode,
    }
    universe_set = set(universe)
    roster_payload: dict[str, Any] = {}
    for family in EXPECTED_FAMILIES:
        roster = roster_for_family(config["families"][family], universe_set)
        roster_payload[family] = {key: value for key, value in roster.items() if key not in {"observed", "missing", "extra"}}
    monitor_command = (
        'powershell -NoProfile -ExecutionPolicy Bypass -File '
        '"C:\\TSIS_Data\\01_TSIS_DATA_FOUNDATION\\scripts\\core_market_raw_alignment_audit\\'
        f'monitor_core_market_raw_alignment.ps1" -RunRoot "{run_root}" -Watch'
    )
    return {
        "run_id": run_id,
        "audit_name": config["audit_name"],
        "auditor_version": AUDITOR_VERSION,
        "status": "preregistered",
        "mode": mode,
        "started_at_utc": iso_utc(),
        "config_path": str(config_path.resolve()),
        "config_sha256": config_sha256,
        "implementation_path": str(implementation_path),
        "implementation_sha256": implementation_sha,
        "run_contract": run_contract,
        "run_contract_sha256": stable_json_hash(run_contract),
        "universe": universe_metadata,
        "universe_tickers": universe,
        "selected_tickers": selected_tickers,
        "selected_ticker_count": len(selected_tickers),
        "selected_tickers_sha256": selected_sha,
        "scope": config["scope"],
        "family_rosters": roster_payload,
        "runtime": config["runtime"],
        "git": get_git_snapshot(REPO_ROOT),
        "resume_policy": "reuse only hash-valid committed family_x_ticker task artifacts under identical run contract",
        "source_mutation_policy": "all four RAW roots are read-only",
        "monitor_command": monitor_command,
        "final_manifest_path": str(runtime_paths(run_root)["closeout"] / "final_manifest.json"),
    }


def finalizer_worker(config: dict[str, Any], run_root_s: str, pre_manifest: dict[str, Any]) -> None:
    run_root = Path(run_root_s)
    error_path = runtime_paths(run_root)["control"] / "finalizer_error.json"
    try:
        finalize_run(config, run_root, pre_manifest)
        if error_path.exists():
            error_path.unlink()
    except Exception as exc:
        atomic_write_json(
            error_path,
            {
                "run_id": pre_manifest.get("run_id"),
                "failed_at_utc": iso_utc(),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            },
        )
        raise


def execute_run(
    *,
    config_path: Path,
    run_id: str,
    mode: str,
    explicit_tickers: str = "",
    resume: bool = False,
    use_processes: bool = True,
) -> tuple[int, dict[str, Any] | None]:
    config, config_sha = load_config(config_path)
    universe, universe_metadata = load_universe(config)
    selected_tickers = select_tickers(config, universe, mode, explicit_tickers)
    output_root = Path(str(config["runtime"]["output_root"]))
    run_root = output_root / run_id
    paths = runtime_paths(run_root)
    pre_manifest_path = paths["control"] / "pre_manifest.json"

    if resume:
        if not pre_manifest_path.is_file():
            raise FileNotFoundError(f"Cannot resume without pre-manifest: {pre_manifest_path}")
        pre_manifest = json.loads(pre_manifest_path.read_text(encoding="utf-8"))
        candidate = prepare_pre_manifest(
            config=config,
            config_path=config_path,
            config_sha256=config_sha,
            universe=universe,
            universe_metadata=universe_metadata,
            selected_tickers=selected_tickers,
            mode=mode,
            run_id=run_id,
            run_root=run_root,
        )
        if pre_manifest.get("run_contract_sha256") != candidate.get("run_contract_sha256"):
            raise ValueError("Resume refused: run contract differs from the existing pre-manifest")
    else:
        if pre_manifest_path.exists():
            raise FileExistsError(f"Run already exists; use --resume or a new run_id: {run_root}")
        ensure_runtime_dirs(run_root)
        pre_manifest = prepare_pre_manifest(
            config=config,
            config_path=config_path,
            config_sha256=config_sha,
            universe=universe,
            universe_metadata=universe_metadata,
            selected_tickers=selected_tickers,
            mode=mode,
            run_id=run_id,
            run_root=run_root,
        )
        atomic_write_json(pre_manifest_path, pre_manifest)
        atomic_write_text(paths["control"] / "monitor_command.txt", str(pre_manifest["monitor_command"]) + "\n")

    ensure_runtime_dirs(run_root)
    logger = configure_parent_logging(run_root)
    started = utc_now()
    ledger_path = paths["control"] / "run_state.sqlite"
    initialize_ledger(
        ledger_path,
        run_id=run_id,
        run_contract_sha256=str(pre_manifest["run_contract_sha256"]),
        families=EXPECTED_FAMILIES,
        tickers=selected_tickers,
    )
    resume_stats = adopt_or_reset_tasks(
        ledger_path,
        run_root,
        EXPECTED_FAMILIES,
        selected_tickers,
        str(pre_manifest["run_contract_sha256"]),
    )
    logger.info(
        "run_started run_id=%s mode=%s selected=%s resume=%s adopted=%s reset=%s",
        run_id,
        mode,
        len(selected_tickers),
        resume,
        resume_stats["adopted"],
        resume_stats["reset"],
    )

    child_pids: list[int] = []
    processes: list[Any] = []
    stop_event: Any = None
    atomic_write_json(
        paths["control"] / "pids.json",
        {
            "run_id": run_id,
            "observed_at_utc": iso_utc(),
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "child_pids": [],
            "monitor_command": pre_manifest["monitor_command"],
        },
    )
    write_heartbeat(
        run_root,
        heartbeat_payload(
            run_id=run_id,
            run_root=run_root,
            started=started,
            stage="preflight_complete",
            status="running",
            ledger_path=ledger_path,
            child_pids=[],
        ),
    )

    try:
        if use_processes:
            context = mp.get_context("spawn")
            stop_event = context.Event()
            for family in EXPECTED_FAMILIES:
                process = context.Process(
                    target=family_worker,
                    args=(
                        config,
                        str(run_root),
                        family,
                        selected_tickers,
                        run_id,
                        str(pre_manifest["run_contract_sha256"]),
                        stop_event,
                    ),
                    name=f"core-market-audit-{family}",
                )
                process.start()
                processes.append(process)
            child_pids = [int(process.pid) for process in processes if process.pid]
        else:
            for family in EXPECTED_FAMILIES:
                family_worker(
                    config,
                    str(run_root),
                    family,
                    selected_tickers,
                    run_id,
                    str(pre_manifest["run_contract_sha256"]),
                    None,
                )

        atomic_write_json(
            paths["control"] / "pids.json",
            {
                "run_id": run_id,
                "observed_at_utc": iso_utc(),
                "wrapper_pid": os.getpid(),
                "active_pid": os.getpid(),
                "child_pids": child_pids,
                "monitor_command": pre_manifest["monitor_command"],
            },
        )
        heartbeat_seconds = max(1, int(config["runtime"].get("heartbeat_seconds", 30)))
        if use_processes:
            while any(process.is_alive() for process in processes):
                payload = heartbeat_payload(
                    run_id=run_id,
                    run_root=run_root,
                    started=started,
                    stage="family_ticker_audit",
                    status="running",
                    ledger_path=ledger_path,
                    child_pids=child_pids,
                )
                write_heartbeat(run_root, payload)
                logger.info(
                    "progress committed=%s/%s errors=%s active=%s",
                    payload["current_index"],
                    payload["total_count"],
                    payload["committed_error_file_count"],
                    payload["active_tasks"],
                )
                time.sleep(heartbeat_seconds)
            for process in processes:
                process.join()
        snapshot = ledger_snapshot(ledger_path)
        expected_tasks = len(EXPECTED_FAMILIES) * len(selected_tickers)
        committed = int(snapshot["status_counts"].get("committed", 0))
        failed = int(snapshot["status_counts"].get("failed", 0))
        running = int(snapshot["status_counts"].get("running", 0))
        if committed != expected_tasks or failed or running:
            technical = {
                "run_id": run_id,
                "technical_status": "FAILED",
                "dataset_verdict": "NOT_EVALUATED",
                "expected_tasks": expected_tasks,
                "ledger_snapshot": snapshot,
                "completed_at_utc": iso_utc(),
            }
            atomic_write_json(paths["closeout"] / "final_manifest.json", technical)
            write_heartbeat(
                run_root,
                heartbeat_payload(
                    run_id=run_id,
                    run_root=run_root,
                    started=started,
                    stage="task_gate_failed",
                    status="failed",
                    ledger_path=ledger_path,
                    child_pids=child_pids,
                ),
            )
            logger.error("task_gate_failed snapshot=%s", snapshot)
            return 2, technical

        write_heartbeat(
            run_root,
            heartbeat_payload(
                run_id=run_id,
                run_root=run_root,
                started=started,
                stage="finalize",
                status="running",
                ledger_path=ledger_path,
                child_pids=child_pids,
            ),
        )
        if use_processes:
            finalize_context = mp.get_context("spawn")
            finalizer_process = finalize_context.Process(
                target=finalizer_worker,
                args=(config, str(run_root), pre_manifest),
                name="core-market-audit-finalizer",
            )
            finalizer_process.start()
            processes.append(finalizer_process)
            finalizer_pid = int(finalizer_process.pid) if finalizer_process.pid else 0
            child_pids = [finalizer_pid] if finalizer_pid else []
            atomic_write_json(
                paths["control"] / "pids.json",
                {
                    "run_id": run_id,
                    "observed_at_utc": iso_utc(),
                    "wrapper_pid": os.getpid(),
                    "active_pid": os.getpid(),
                    "child_pids": child_pids,
                    "active_stage": "finalize",
                    "monitor_command": pre_manifest["monitor_command"],
                },
            )
            while finalizer_process.is_alive():
                write_heartbeat(
                    run_root,
                    heartbeat_payload(
                        run_id=run_id,
                        run_root=run_root,
                        started=started,
                        stage="finalize",
                        status="running",
                        ledger_path=ledger_path,
                        child_pids=child_pids,
                    ),
                )
                time.sleep(heartbeat_seconds)
            finalizer_process.join()
            if finalizer_process.exitcode != 0:
                error_path = paths["control"] / "finalizer_error.json"
                error_payload = (
                    json.loads(error_path.read_text(encoding="utf-8"))
                    if error_path.is_file()
                    else {"error": f"finalizer_exit_code={finalizer_process.exitcode}"}
                )
                technical = {
                    "run_id": run_id,
                    "technical_status": "FAILED",
                    "dataset_verdict": "NOT_EVALUATED",
                    "stage": "finalize",
                    "finalizer_error": error_payload,
                    "completed_at_utc": iso_utc(),
                }
                atomic_write_json(paths["closeout"] / "final_manifest.json", technical)
                write_heartbeat(
                    run_root,
                    heartbeat_payload(
                        run_id=run_id,
                        run_root=run_root,
                        started=started,
                        stage="finalize_failed",
                        status="failed",
                        ledger_path=ledger_path,
                        child_pids=child_pids,
                    ),
                )
                logger.error("finalizer_failed payload=%s", error_payload)
                return 2, technical
            summary = json.loads((paths["closeout"] / "audit_summary.json").read_text(encoding="utf-8"))
        else:
            summary = finalize_run(config, run_root, pre_manifest)
        write_heartbeat(
            run_root,
            heartbeat_payload(
                run_id=run_id,
                run_root=run_root,
                started=started,
                stage="final_manifest_written",
                status="completed",
                ledger_path=ledger_path,
                child_pids=child_pids,
            )
            | {"dataset_verdict": summary["dataset_verdict"]},
        )
        logger.info("run_completed dataset_verdict=%s", summary["dataset_verdict"])
        return 0, summary
    except KeyboardInterrupt:
        if stop_event is not None:
            stop_event.set()
        for process in processes:
            process.join(timeout=10)
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
        write_heartbeat(
            run_root,
            heartbeat_payload(
                run_id=run_id,
                run_root=run_root,
                started=started,
                stage="interrupted_resume_available",
                status="interrupted",
                ledger_path=ledger_path,
                child_pids=child_pids,
            ),
        )
        logger.warning("run_interrupted resume_available=true")
        return 130, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=["probe", "full"], default="probe")
    parser.add_argument("--tickers", default="", help="Exact comma-separated subset; defaults to probe tickers or full universe")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--human-authorized-full",
        action="store_true",
        help="Required in full mode. This flag records authorization; it does not broaden source-write authority.",
    )
    parser.add_argument("--sequential", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "full" and not args.human_authorized_full:
        raise SystemExit("Full audit refused: pass --human-authorized-full after explicit human authorization")
    code, _summary = execute_run(
        config_path=args.config,
        run_id=args.run_id,
        mode=args.mode,
        explicit_tickers=args.tickers,
        resume=args.resume,
        use_processes=not args.sequential,
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
