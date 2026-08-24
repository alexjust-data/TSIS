"""Governed read-only audit of the restored historical Quotes C root.

The historical pre-merge C inventory is the expected-file authority.  Every
restored file is checked with the same Parquet inspector used by the closed
core-market physical audit.  The source roots are never modified.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import socket
import sqlite3
import sys
import time
import traceback
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import quote

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from core_market_raw_alignment_audit.audit_core_market_raw_alignment import (  # noqa: E402
    INVENTORY_SCHEMA,
    atomic_write_json,
    atomic_write_table,
    inspect_parquet_file,
    sha256_file,
    stable_json_hash,
    table_from_rows,
)


UTC = timezone.utc
EXTENDED_SCHEMA = pa.schema(
    list(INVENTORY_SCHEMA)
    + [
        pa.field("historical_date", pa.date32()),
        pa.field("historical_expected", pa.bool_()),
        pa.field("historical_size_bytes", pa.int64()),
        pa.field("historical_severity", pa.string()),
        pa.field("historical_action", pa.string()),
        pa.field("historical_size_match", pa.bool_()),
        pa.field("restoration_path_state", pa.string()),
    ]
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def safe_ticker(ticker: str) -> str:
    return quote(ticker, safe="._-")


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    with partial.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)


def load_yaml(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    payload = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Config must be a mapping")
    return payload, hashlib.sha256(raw).hexdigest().upper()


def load_expected(
    inventory_path: Path, selected: set[str] | None
) -> dict[str, list[dict[str, Any]]]:
    table = pq.ParquetFile(inventory_path).read(
        columns=["ticker", "date", "relpath", "size_bytes", "severity", "action"]
    )
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    columns = table.to_pydict()
    for ticker, value_date, relpath, size, severity, action in zip(
        columns["ticker"], columns["date"], columns["relpath"], columns["size_bytes"],
        columns["severity"], columns["action"], strict=True,
    ):
        ticker = str(ticker)
        if selected is not None and ticker not in selected:
            continue
        result[ticker].append(
            {
                "date": str(value_date)[:10],
                "relpath": str(relpath).replace("/", "\\"),
                "size_bytes": int(size),
                "severity": None if severity is None else str(severity),
                "action": None if action is None else str(action),
            }
        )
    return dict(result)


def task_paths(run_root: Path, ticker: str) -> dict[str, Path]:
    safe = safe_ticker(ticker)
    return {
        "inventory": run_root / "01_inventory" / f"ticker={safe}" / "inventory.parquet",
        "manifest": run_root / "00_control" / "task_results" / f"ticker={safe}.json",
    }


def connect_ledger(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=60)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA busy_timeout=60000")
    return connection


def initialize_ledger(path: Path, run_id: str, contract_hash: str, tickers: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect_ledger(path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS run_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(
              ticker TEXT PRIMARY KEY,status TEXT NOT NULL,worker_pid INTEGER,
              started_at_utc TEXT,ended_at_utc TEXT,expected_files INTEGER DEFAULT 0,
              actual_files INTEGER DEFAULT 0,matched_files INTEGER DEFAULT 0,
              missing_files INTEGER DEFAULT 0,extra_files INTEGER DEFAULT 0,
              physical_error_files INTEGER DEFAULT 0,error_message TEXT
            );
            """
        )
        connection.execute("INSERT OR REPLACE INTO run_metadata VALUES('run_id',?)", (run_id,))
        connection.execute(
            "INSERT OR REPLACE INTO run_metadata VALUES('run_contract_sha256',?)", (contract_hash,)
        )
        connection.executemany(
            "INSERT OR IGNORE INTO tasks(ticker,status) VALUES(?, 'pending')",
            [(ticker,) for ticker in tickers],
        )


def ledger_update(path: Path, ticker: str, status: str, **values: Any) -> None:
    fields = {"status": status, **values}
    assignments = ",".join(f"{key}=?" for key in fields)
    with connect_ledger(path) as connection:
        connection.execute(
            f"UPDATE tasks SET {assignments} WHERE ticker=?",
            [*fields.values(), ticker],
        )


def ledger_snapshot(path: Path) -> dict[str, Any]:
    uri = path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=30) as connection:
        counts = dict(connection.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status"))
        totals = connection.execute(
            "SELECT COALESCE(SUM(expected_files),0),COALESCE(SUM(actual_files),0),"
            "COALESCE(SUM(matched_files),0),COALESCE(SUM(missing_files),0),"
            "COALESCE(SUM(extra_files),0),COALESCE(SUM(physical_error_files),0) "
            "FROM tasks WHERE status='committed'"
        ).fetchone()
        active = [row[0] for row in connection.execute(
            "SELECT ticker FROM tasks WHERE status='running' ORDER BY ticker"
        )]
    return {
        "task_counts": {str(k): int(v) for k, v in counts.items()},
        "expected_files": int(totals[0]),
        "actual_files": int(totals[1]),
        "matched_files": int(totals[2]),
        "missing_files": int(totals[3]),
        "extra_files": int(totals[4]),
        "physical_error_files": int(totals[5]),
        "active": active,
    }


def write_heartbeat(
    run_root: Path, ledger: Path, stage: str, status: str, started: datetime,
    workers: int, last_error: str | None = None,
) -> None:
    snapshot = ledger_snapshot(ledger)
    payload = {
        "run_id": json.loads((run_root / "00_control" / "pre_manifest.json").read_text(encoding="utf-8"))["run_id"],
        "observed_at_utc": iso_utc(),
        "status": status,
        "stage": stage,
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 3),
        "runner_pid": os.getpid(),
        "runner_alive": True,
        "workers": workers,
        **snapshot,
        "last_error": last_error,
    }
    atomic_write_json(run_root / "00_control" / "heartbeat.latest.json", payload)
    with (run_root / "00_control" / "heartbeat.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def canonical_relpath(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("/", "\\")


def audit_ticker(
    ticker: str, expected_rows: list[dict[str, Any]], restored_root_text: str,
    spec: dict[str, Any], scope_start: date, scope_end: date, run_root_text: str,
    ledger_text: str, contract_hash: str,
) -> dict[str, Any]:
    restored_root = Path(restored_root_text)
    run_root = Path(run_root_text)
    ledger = Path(ledger_text)
    paths = task_paths(run_root, ticker)
    started = utc_now()
    ledger_update(ledger, ticker, "running", worker_pid=os.getpid(), started_at_utc=iso_utc(started))
    expected = {row["relpath"]: row for row in expected_rows}
    ticker_root = restored_root / ticker
    actual_paths = sorted(ticker_root.rglob("quotes.parquet")) if ticker_root.is_dir() else []
    actual = {canonical_relpath(path, restored_root): path for path in actual_paths}
    rows: list[dict[str, Any]] = []
    for relpath in sorted(set(expected) | set(actual)):
        historical = expected.get(relpath)
        path = actual.get(relpath, restored_root / Path(relpath))
        inspected, _ = inspect_parquet_file(
            path=path, family="quotes_restored", ticker=ticker, family_root=restored_root,
            spec=spec, scope_start=scope_start, scope_end=scope_end,
        )
        expected_size = int(historical["size_bytes"]) if historical else None
        actual_size = inspected.get("file_size_bytes")
        size_match = (
            bool(actual_size == expected_size)
            if historical is not None and actual_size is not None else None
        )
        inspected.update(
            {
                "historical_date": (
                    date.fromisoformat(historical["date"]) if historical is not None else None
                ),
                "historical_expected": historical is not None,
                "historical_size_bytes": expected_size,
                "historical_severity": historical.get("severity") if historical else None,
                "historical_action": historical.get("action") if historical else None,
                "historical_size_match": size_match,
                "restoration_path_state": (
                    "RESTORED_EXPECTED" if historical is not None and path.is_file()
                    else "MISSING_KNOWN_NONEMPTY" if historical is not None
                    else "RESTORED_NOT_IN_HISTORICAL_C_INVENTORY"
                ),
            }
        )
        rows.append(inspected)
    atomic_write_table(paths["inventory"], table_from_rows(rows, EXTENDED_SCHEMA))
    matched = sum(bool(r["historical_expected"] and r["file_exists"]) for r in rows)
    missing = sum(bool(r["historical_expected"] and not r["file_exists"]) for r in rows)
    extra = sum(bool(not r["historical_expected"] and r["file_exists"]) for r in rows)
    errors = sum(bool(r["file_exists"] and r["error_class"]) for r in rows)
    size_mismatch = sum(
        bool(r["historical_expected"] and r["file_exists"] and not r["historical_size_match"])
        for r in rows
    )
    payload = {
        "ticker": ticker,
        "status": "committed",
        "worker_pid": os.getpid(),
        "started_at_utc": iso_utc(started),
        "ended_at_utc": iso_utc(),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 3),
        "run_contract_sha256": contract_hash,
        "expected_files": len(expected),
        "actual_files": len(actual),
        "matched_files": matched,
        "missing_files": missing,
        "extra_files": extra,
        "size_mismatch_files": size_mismatch,
        "physical_error_files": errors,
        "inventory_path": str(paths["inventory"]),
        "inventory_sha256": sha256_file(paths["inventory"]),
    }
    atomic_write_json(paths["manifest"], payload)
    ledger_update(
        ledger, ticker, "committed", worker_pid=os.getpid(), ended_at_utc=payload["ended_at_utc"],
        expected_files=len(expected), actual_files=len(actual), matched_files=matched,
        missing_files=missing, extra_files=extra, physical_error_files=errors,
        error_message=None,
    )
    return payload


def task_valid(run_root: Path, ticker: str, contract_hash: str) -> bool:
    paths = task_paths(run_root, ticker)
    if not paths["manifest"].is_file() or not paths["inventory"].is_file():
        return False
    try:
        payload = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        return (
            payload.get("status") == "committed"
            and payload.get("run_contract_sha256") == contract_hash
            and sha256_file(paths["inventory"]) == payload.get("inventory_sha256")
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


def consolidate(paths: Iterable[Path], destination: Path) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    writer = pq.ParquetWriter(partial, EXTENDED_SCHEMA, compression="zstd")
    count = 0
    try:
        for path in paths:
            table = pq.ParquetFile(path).read()
            if table.schema != EXTENDED_SCHEMA:
                table = table.cast(EXTENDED_SCHEMA)
            writer.write_table(table)
            count += table.num_rows
    finally:
        writer.close()
    os.replace(partial, destination)
    return count


def filtered_table(table: pa.Table, expression: pa.Array) -> pa.Table:
    return table.filter(expression)


def finalize(run_root: Path, tickers: Sequence[str], pre: dict[str, Any], ledger: Path) -> dict[str, Any]:
    closeout = run_root / "03_closeout"
    inventory_path = closeout / "quotes_restored_inventory.parquet"
    total_rows = consolidate((task_paths(run_root, t)["inventory"] for t in tickers), inventory_path)
    table = pq.ParquetFile(inventory_path).read()
    expected = pc.fill_null(table["historical_expected"], False)
    exists = pc.fill_null(table["file_exists"], False)
    errors = pc.is_valid(table["error_class"])
    missing_mask = pc.and_(expected, pc.invert(exists))
    extra_mask = pc.and_(pc.invert(expected), exists)
    physical_error_mask = pc.and_(exists, errors)
    missing_table = filtered_table(table, missing_mask)
    extra_table = filtered_table(table, extra_mask)
    error_table = filtered_table(table, physical_error_mask)
    size_mismatch_mask = pc.and_(
        pc.and_(expected, exists),
        pc.equal(pc.fill_null(table["historical_size_match"], True), False),
    )
    size_mismatch_table = filtered_table(table, size_mismatch_mask)
    missing_path = closeout / "known_nonempty_missing.parquet"
    extra_path = closeout / "restored_not_in_historical_inventory.parquet"
    error_path = closeout / "restored_physical_errors.parquet"
    size_mismatch_path = closeout / "restored_size_mismatches.parquet"
    atomic_write_table(missing_path, missing_table)
    atomic_write_table(extra_path, extra_table)
    atomic_write_table(error_path, error_table)
    atomic_write_table(size_mismatch_path, size_mismatch_table)
    repair_csv = closeout / "repair_known_nonempty_missing.csv"
    repair_table = pa.table(
        {
            "ticker": missing_table["ticker"],
            "date": pc.cast(missing_table["historical_date"], pa.string()),
        }
    )
    partial_csv = repair_csv.with_suffix(".csv.partial")
    pacsv.write_csv(repair_table, partial_csv)
    os.replace(partial_csv, repair_csv)
    snapshot = ledger_snapshot(ledger)
    committed = int(snapshot["task_counts"].get("committed", 0))
    technical = "PASS" if committed == len(tickers) else "FAIL"
    missing_count = missing_table.num_rows
    physical_errors = error_table.num_rows
    size_mismatches = size_mismatch_table.num_rows
    dataset = (
        "FAIL_INCOMPLETE_RESTORATION" if missing_count
        else "FAIL_PHYSICAL_INTEGRITY" if physical_errors
        else "FAIL_RESTORATION_SIZE_MISMATCH" if size_mismatches
        else "PASS_RESTORED_C_PHYSICAL_PARITY"
    )
    summary = {
        "run_id": pre["run_id"],
        "status": "completed",
        "technical_status": technical,
        "dataset_status": dataset,
        "expected_tickers": len(tickers),
        "committed_tickers": committed,
        "inventory_rows": total_rows,
        "historical_expected_files": int(pc.sum(pc.cast(expected, pa.int64())).as_py()),
        "restored_actual_files": int(pc.sum(pc.cast(exists, pa.int64())).as_py()),
        "known_nonempty_missing_files": missing_count,
        "restored_extra_files": extra_table.num_rows,
        "restored_physical_error_files": physical_errors,
        "restored_size_mismatch_files": size_mismatches,
        "started_at_utc": pre["started_at_utc"],
        "ended_at_utc": iso_utc(),
    }
    summary_path = closeout / "audit_summary.json"
    atomic_write_json(summary_path, summary)
    report_path = closeout / "QUOTES_RESTORATION_AUDIT.md"
    atomic_write_text(
        report_path,
        "# Quotes Restoration Audit\n\n"
        f"- Technical status: `{technical}`\n"
        f"- Dataset status: `{dataset}`\n"
        f"- Historical C files expected: `{summary['historical_expected_files']}`\n"
        f"- Restored files observed: `{summary['restored_actual_files']}`\n"
        f"- Known non-empty files still missing: `{missing_count}`\n"
        f"- Restored files outside the historical C inventory: `{extra_table.num_rows}`\n"
        f"- Restored files failing physical/schema checks: `{physical_errors}`\n"
        f"- Restored files with a different byte size: `{size_mismatches}`\n\n"
        "The source roots were read-only. Missing historical files are proven non-empty because "
        "they existed in the closed pre-merge C inventory. Provider-empty dates are a separate "
        "classification and are not included in this count.\n",
    )
    artifacts = []
    for path in (
        inventory_path, missing_path, extra_path, error_path, size_mismatch_path,
        repair_csv, summary_path, report_path,
    ):
        artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    final = {**summary, "artifacts": artifacts}
    atomic_write_json(closeout / "final_manifest.json", final)
    return final


def run(args: argparse.Namespace) -> int:
    config, config_hash = load_yaml(args.config)
    restored_root = Path(config["sources"]["restored_root"])
    historical = Path(config["sources"]["historical_c_inventory"])
    if not restored_root.is_dir() or not historical.is_file():
        raise FileNotFoundError(f"Missing input: restored={restored_root} historical={historical}")
    probe = [str(v) for v in config["probe"]["tickers"]]
    explicit = [v.strip() for v in args.tickers.split(",") if v.strip()]
    selected_filter = None if args.mode == "full" else set(explicit or probe)
    if args.mode == "full" and not args.human_authorized_full:
        raise ValueError("Full audit requires --human-authorized-full")
    expected = load_expected(historical, selected_filter)
    tickers = sorted(expected)
    if selected_filter is not None and set(tickers) != selected_filter:
        raise ValueError(f"Probe tickers absent from historical C inventory: {selected_filter-set(tickers)}")
    run_root = Path(config["runtime"]["output_root"]) / args.run_id
    control = run_root / "00_control"
    pre_path = control / "pre_manifest.json"
    if pre_path.exists() and not args.resume:
        raise ValueError(f"Run already exists; use --resume: {run_root}")
    for name in ("00_control/task_results", "01_inventory", "03_closeout"):
        (run_root / name).mkdir(parents=True, exist_ok=True)
    workers = args.workers or int(config["runtime"]["workers"])
    spec = dict(config["quotes_contract"])
    scope_start = date.fromisoformat(config["scope"]["start_date_inclusive"])
    scope_end = date.fromisoformat(config["scope"]["target_end_inclusive"])
    operational = [Path(__file__).resolve(), SCRIPT_DIR / "run_quotes_restoration_audit.ps1", SCRIPT_DIR / "monitor_quotes_restoration_audit.py"]
    contract = {
        "config_sha256": config_hash,
        "operational_hashes": {str(p): sha256_file(p) for p in operational},
        "historical_inventory_sha256": sha256_file(historical),
        "restored_root": str(restored_root),
        "tickers": tickers,
        "mode": args.mode,
    }
    contract_hash = stable_json_hash(contract)
    started = utc_now()
    pre = {
        "run_id": args.run_id,
        "status": "starting",
        "mode": args.mode,
        "started_at_utc": iso_utc(started),
        "script_path": str(Path(__file__).resolve()),
        "config_path": str(args.config.resolve()),
        "config_sha256": config_hash,
        "run_contract_sha256": contract_hash,
        "cwd": os.getcwd(),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME"),
        "runner_pid": os.getpid(),
        "input_roots": [str(restored_root), str(historical)],
        "output_root": str(run_root),
        "selected_tickers": tickers,
        "expected_files": sum(len(v) for v in expected.values()),
        "workers": workers,
        "read_only_sources": True,
        "resume_policy": "ticker-private immutable Parquet shard; committed shard hash-validated",
        "overwrite_policy": "never modify source roots; refuse existing run without --resume",
        "success_criteria": "all selected tickers committed and every restored file physically readable",
        "monitor_command": f'powershell -NoProfile -ExecutionPolicy Bypass -File "{SCRIPT_DIR / "monitor_quotes_restoration_audit.ps1"}" -RunRoot "{run_root}" -Watch',
    }
    if pre_path.exists():
        persisted = json.loads(pre_path.read_text(encoding="utf-8"))
        if persisted["run_contract_sha256"] != contract_hash:
            raise ValueError("Resume contract mismatch")
        pre = persisted
        started = datetime.fromisoformat(pre["started_at_utc"])
    else:
        atomic_write_json(pre_path, pre)
    ledger = control / "run_state.sqlite"
    initialize_ledger(ledger, args.run_id, contract_hash, tickers)
    atomic_write_json(control / "pid_manifest.json", {
        "run_id": args.run_id, "runner_pid": os.getpid(), "parent_pid": os.getppid(),
        "started_at_utc": pre["started_at_utc"], "expected_alive": True,
    })
    print(json.dumps({
        "run_id": args.run_id, "mode": args.mode, "input_root": str(restored_root),
        "historical_inventory": str(historical), "output_root": str(run_root),
        "pre_manifest": str(pre_path), "ledger": str(ledger), "workers": workers,
        "monitor": pre["monitor_command"], "resume_policy": pre["resume_policy"],
        "success_criteria": pre["success_criteria"],
    }, indent=2), flush=True)
    pending = []
    for ticker in tickers:
        if task_valid(run_root, ticker, contract_hash):
            manifest = json.loads(task_paths(run_root, ticker)["manifest"].read_text(encoding="utf-8"))
            ledger_update(
                ledger, ticker, "committed", worker_pid=manifest["worker_pid"],
                ended_at_utc=manifest["ended_at_utc"], expected_files=manifest["expected_files"],
                actual_files=manifest["actual_files"], matched_files=manifest["matched_files"],
                missing_files=manifest["missing_files"], extra_files=manifest["extra_files"],
                physical_error_files=manifest["physical_error_files"], error_message=None,
            )
        else:
            pending.append(ticker)
    write_heartbeat(run_root, ledger, "ticker_physical_audit", "running", started, workers)
    failures: list[tuple[str, str]] = []
    stop_requested = False
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        iterator = iter(pending)
        active: dict[concurrent.futures.Future[dict[str, Any]], str] = {}

        def submit_next() -> bool:
            nonlocal stop_requested
            if (control / "stop.requested").is_file():
                stop_requested = True
                return False
            try:
                ticker = next(iterator)
            except StopIteration:
                return False
            future = pool.submit(
                audit_ticker, ticker, expected[ticker], str(restored_root), spec,
                scope_start, scope_end, str(run_root), str(ledger), contract_hash,
            )
            active[future] = ticker
            return True

        for _ in range(workers):
            submit_next()
        last_heartbeat = time.monotonic()
        while active:
            done, _ = concurrent.futures.wait(
                active, timeout=5, return_when=concurrent.futures.FIRST_COMPLETED
            )
            if time.monotonic() - last_heartbeat >= int(config["runtime"]["heartbeat_seconds"]):
                write_heartbeat(run_root, ledger, "ticker_physical_audit", "running", started, workers)
                last_heartbeat = time.monotonic()
            for future in done:
                ticker = active.pop(future)
                try:
                    future.result()
                except Exception as exc:
                    message = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"[:12000]
                    ledger_update(ledger, ticker, "failed", ended_at_utc=iso_utc(), error_message=message)
                    failures.append((ticker, message))
                if not failures and not stop_requested:
                    submit_next()
            if failures:
                stop_requested = True
    if failures:
        write_heartbeat(run_root, ledger, "ticker_physical_audit", "failed", started, workers, failures[0][1])
        raise RuntimeError(f"Audit failed for {failures[0][0]}")
    if stop_requested:
        write_heartbeat(run_root, ledger, "controlled_stop", "interrupted", started, workers)
        return 130
    write_heartbeat(run_root, ledger, "finalizing", "running", started, workers)
    final = finalize(run_root, tickers, pre, ledger)
    atomic_write_json(control / "pid_manifest.json", {
        "run_id": args.run_id, "runner_pid": os.getpid(), "parent_pid": os.getppid(),
        "started_at_utc": pre["started_at_utc"], "ended_at_utc": iso_utc(), "expected_alive": False,
    })
    write_heartbeat(run_root, ledger, "closed", "completed", started, workers)
    print(json.dumps(final, indent=2), flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("probe", "full"), required=True)
    parser.add_argument("--tickers", default="")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--human-authorized-full", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
