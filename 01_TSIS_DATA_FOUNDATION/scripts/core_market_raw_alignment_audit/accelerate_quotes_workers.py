"""Safely replace the single Quotes audit worker with an adaptive worker pool.

This sidecar is intentionally scoped to the existing ``quotes_`` tasks.  It
does not stop or modify the parent, ``ohlcv_1m`` or Trades workers.  SQLite
``BEGIN IMMEDIATE`` transactions provide exclusive task claims, while every
task continues to use the original auditor and its task-local atomic outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
import os
import sqlite3
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


SCRIPT_DIR = Path(__file__).resolve().parent
AUDITOR_PATH = SCRIPT_DIR / "audit_core_market_raw_alignment.py"
FAMILY = "quotes_"
ACCELERATOR_VERSION = "0.1.0"


def _load_auditor() -> Any:
    name = "core_market_raw_alignment_audit_runtime"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, AUDITOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import auditor: {AUDITOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_auditor()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def accelerator_paths(run_root: Path) -> dict[str, Path]:
    root = run_root / "00_control" / "quotes_accelerator"
    return {
        "root": root,
        "pre_manifest": root / "pre_manifest.json",
        "pids": root / "pids.json",
        "heartbeat": root / "heartbeat.json",
        "heartbeat_log": root / "heartbeat.jsonl",
        "log": root / "accelerator.log",
        "final_manifest": root / "final_manifest.json",
    }


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{iso_utc()} {message}\n")
        handle.flush()
        os.fsync(handle.fileno())


def _sql_retry(operation: Any, attempts: int = 20) -> Any:
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


def initialize_accelerator_ledger(ledger_path: Path) -> None:
    def operation() -> None:
        connection = AUDIT.connect_ledger(ledger_path)
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS quote_accelerator_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    observed_at_utc TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    ticker TEXT,
                    worker_pid INTEGER,
                    attempt INTEGER,
                    detail_json TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_quote_accelerator_events_ticker
                    ON quote_accelerator_events(ticker, event_id);
                """
            )
            connection.commit()
        finally:
            connection.close()

    _sql_retry(operation)


def _record_event(
    connection: sqlite3.Connection,
    event_type: str,
    *,
    ticker: str | None = None,
    worker_pid: int | None = None,
    attempt: int | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    connection.execute(
        "INSERT INTO quote_accelerator_events(observed_at_utc,event_type,ticker,worker_pid,attempt,detail_json) "
        "VALUES(?,?,?,?,?,?)",
        (
            iso_utc(),
            event_type,
            ticker,
            worker_pid,
            attempt,
            json.dumps(detail, ensure_ascii=False, sort_keys=True) if detail else None,
        ),
    )


def family_counts(ledger_path: Path, family: str) -> dict[str, int]:
    connection = AUDIT.connect_ledger(ledger_path)
    try:
        counts = {
            str(status): int(count)
            for status, count in connection.execute(
                "SELECT status,COUNT(*) FROM tasks WHERE family=? GROUP BY status", (family,)
            )
        }
        counts["total"] = int(
            connection.execute("SELECT COUNT(*) FROM tasks WHERE family=?", (family,)).fetchone()[0]
        )
        return counts
    finally:
        connection.close()


def claim_next_quote_task(ledger_path: Path, worker_pid: int) -> tuple[str, int] | None:
    """Atomically claim one pending Quotes ticker and return ``(ticker, attempt)``."""

    def operation() -> tuple[str, int] | None:
        connection = AUDIT.connect_ledger(ledger_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT ticker,attempt FROM tasks "
                "WHERE family=? AND status='pending' ORDER BY ticker LIMIT 1",
                (FAMILY,),
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            ticker = str(row[0])
            attempt = int(row[1]) + 1
            cursor = connection.execute(
                "UPDATE tasks SET status='running',attempt=?,worker_pid=?,started_at_utc=?,"
                "ended_at_utc=NULL,error_message=NULL "
                "WHERE family=? AND ticker=? AND status='pending'",
                (attempt, worker_pid, iso_utc(), FAMILY, ticker),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                return None
            _record_event(
                connection,
                "TASK_CLAIMED",
                ticker=ticker,
                worker_pid=worker_pid,
                attempt=attempt,
            )
            connection.commit()
            return ticker, attempt
        finally:
            connection.close()

    return _sql_retry(operation)


def mark_quote_committed(
    ledger_path: Path,
    ticker: str,
    worker_pid: int,
    attempt: int,
    result: dict[str, Any],
) -> None:
    def operation() -> None:
        connection = AUDIT.connect_ledger(ledger_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE tasks SET status='committed',ended_at_utc=?,source_dir_exists=?,"
                "file_count=?,source_bytes=?,date_count=?,error_file_count=?,task_manifest_path=?,error_message=NULL "
                "WHERE family=? AND ticker=? AND status='running' AND worker_pid=? AND attempt=?",
                (
                    iso_utc(),
                    int(bool(result["source_ticker_dir_exists"])),
                    int(result["file_count"]),
                    int(result["source_bytes"]),
                    int(result["date_count"]),
                    int(result["error_file_count"]),
                    str(result["task_manifest_path"]),
                    FAMILY,
                    ticker,
                    worker_pid,
                    attempt,
                ),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise RuntimeError(f"Lost task ownership before commit: {ticker} pid={worker_pid}")
            _record_event(
                connection,
                "TASK_COMMITTED",
                ticker=ticker,
                worker_pid=worker_pid,
                attempt=attempt,
                detail={"file_count": int(result["file_count"]), "date_count": int(result["date_count"])},
            )
            connection.commit()
        finally:
            connection.close()

    _sql_retry(operation)


def mark_quote_failure(
    ledger_path: Path,
    ticker: str,
    worker_pid: int,
    attempt: int,
    message: str,
    max_attempts: int,
) -> str:
    terminal_status = "failed" if attempt >= max_attempts else "pending"

    def operation() -> str:
        connection = AUDIT.connect_ledger(ledger_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE tasks SET status=?,worker_pid=NULL,ended_at_utc=?,error_message=? "
                "WHERE family=? AND ticker=? AND status='running' AND worker_pid=? AND attempt=?",
                (
                    terminal_status,
                    iso_utc(),
                    message[:4000],
                    FAMILY,
                    ticker,
                    worker_pid,
                    attempt,
                ),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise RuntimeError(f"Lost task ownership after failure: {ticker} pid={worker_pid}")
            _record_event(
                connection,
                "TASK_FAILED" if terminal_status == "failed" else "TASK_REQUEUED",
                ticker=ticker,
                worker_pid=worker_pid,
                attempt=attempt,
                detail={"error": message[:4000]},
            )
            connection.commit()
            return terminal_status
        finally:
            connection.close()

    return _sql_retry(operation)


def recover_replaced_quote_task(ledger_path: Path, replaced_pid: int) -> str | None:
    """Return only the exact running Quotes task owned by the replaced PID to pending."""

    def operation() -> str | None:
        connection = AUDIT.connect_ledger(ledger_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                "SELECT ticker,attempt FROM tasks WHERE family=? AND status='running' AND worker_pid=?",
                (FAMILY, replaced_pid),
            ).fetchall()
            if not rows:
                connection.commit()
                return None
            if len(rows) != 1:
                connection.rollback()
                raise RuntimeError(f"Expected one Quotes task for PID {replaced_pid}; found {len(rows)}")
            ticker, attempt = str(rows[0][0]), int(rows[0][1])
            cursor = connection.execute(
                "UPDATE tasks SET status='pending',worker_pid=NULL,started_at_utc=NULL,ended_at_utc=NULL,"
                "error_message=? WHERE family=? AND ticker=? AND status='running' AND worker_pid=?",
                ("recovered_after_authorized_quotes_worker_replacement", FAMILY, ticker, replaced_pid),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise RuntimeError(f"Could not recover Quotes task {ticker} from PID {replaced_pid}")
            _record_event(
                connection,
                "ORIGINAL_WORKER_TASK_RECOVERED",
                ticker=ticker,
                worker_pid=replaced_pid,
                attempt=attempt,
            )
            connection.commit()
            return ticker
        finally:
            connection.close()

    return _sql_retry(operation)


def verify_replacement_target(run_root: Path, replace_pid: int) -> dict[str, Any]:
    ledger_path = run_root / "00_control" / "run_state.sqlite"
    pid_payload = json.loads((run_root / "00_control" / "pids.json").read_text(encoding="utf-8"))
    parent_pid = int(pid_payload["active_pid"])
    connection = AUDIT.connect_ledger(ledger_path)
    try:
        active_rows = connection.execute(
            "SELECT family,ticker,worker_pid FROM tasks WHERE status='running' ORDER BY family"
        ).fetchall()
    finally:
        connection.close()
    owned = [(str(f), str(t), int(p)) for f, t, p in active_rows if int(p) == replace_pid]
    if len(owned) != 1 or owned[0][0] != FAMILY:
        raise RuntimeError(f"Replacement PID must own exactly one running quotes_ task; found {owned}")
    protected = [row for row in active_rows if str(row[0]) in {"ohlcv_1m", "trades_ticks_prod_2005_2026"}]
    if any(int(row[2]) == replace_pid for row in protected):
        raise RuntimeError("Replacement PID is shared with a protected 1m/Trades task")
    process = psutil.Process(replace_pid)
    if process.ppid() != parent_pid:
        raise RuntimeError(f"Quotes PID parent mismatch: expected {parent_pid}, observed {process.ppid()}")
    command_line = " ".join(process.cmdline())
    if "multiprocessing.spawn" not in command_line or f"parent_pid={parent_pid}" not in command_line:
        raise RuntimeError(f"Unexpected Quotes process command line: {command_line}")
    if not psutil.pid_exists(parent_pid):
        raise RuntimeError(f"Parent PID is not alive: {parent_pid}")
    protected_payload = [
        {"family": str(f), "ticker": str(t), "worker_pid": int(p)} for f, t, p in protected
    ]
    if len(protected_payload) != 2 or not all(psutil.pid_exists(item["worker_pid"]) for item in protected_payload):
        raise RuntimeError(f"Protected 1m/Trades workers are not both alive: {protected_payload}")
    return {
        "parent_pid": parent_pid,
        "replace_pid": replace_pid,
        "replace_ticker": owned[0][1],
        "protected_workers": protected_payload,
        "replace_command_line": command_line,
    }


def stop_original_quotes_worker(replace_pid: int, timeout_seconds: int = 30) -> None:
    process = psutil.Process(replace_pid)
    process.terminate()
    try:
        process.wait(timeout=timeout_seconds)
    except psutil.TimeoutExpired as exc:
        raise RuntimeError(f"Quotes PID {replace_pid} did not stop within {timeout_seconds}s") from exc
    if psutil.pid_exists(replace_pid):
        raise RuntimeError(f"Quotes PID still exists after termination: {replace_pid}")


def quote_worker(
    config: dict[str, Any],
    run_root_s: str,
    run_id: str,
    run_contract_sha256: str,
    max_attempts: int,
) -> None:
    run_root = Path(run_root_s)
    ledger_path = run_root / "00_control" / "run_state.sqlite"
    worker_pid = os.getpid()
    worker_log = accelerator_paths(run_root)["root"] / f"worker_{worker_pid}.log"
    append_log(worker_log, f"worker_started pid={worker_pid}")
    while True:
        claim = claim_next_quote_task(ledger_path, worker_pid)
        if claim is None:
            break
        ticker, attempt = claim
        append_log(worker_log, f"claimed ticker={ticker} attempt={attempt}")
        try:
            manifest_path = AUDIT.task_paths(run_root, FAMILY, ticker)["manifest"]
            if AUDIT.task_manifest_valid(manifest_path, run_contract_sha256):
                result = json.loads(manifest_path.read_text(encoding="utf-8"))
                adopted = True
            else:
                result = AUDIT.audit_ticker_task(
                    config=config,
                    run_root=run_root,
                    family=FAMILY,
                    ticker=ticker,
                    run_id=run_id,
                    run_contract_sha256=run_contract_sha256,
                )
                adopted = False
            mark_quote_committed(ledger_path, ticker, worker_pid, attempt, result)
            append_log(
                worker_log,
                f"committed ticker={ticker} attempt={attempt} adopted={adopted} "
                f"files={result['file_count']} dates={result['date_count']}",
            )
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            try:
                status = mark_quote_failure(
                    ledger_path, ticker, worker_pid, attempt, message, max_attempts
                )
            except Exception as ownership_exc:
                append_log(worker_log, f"ownership_failure ticker={ticker} error={ownership_exc}")
                raise
            append_log(
                worker_log,
                f"task_error ticker={ticker} attempt={attempt} status={status} error={message}\n"
                f"{traceback.format_exc()}",
            )
            if status == "failed":
                break
    append_log(worker_log, "worker_ended")


def write_accelerator_heartbeat(
    run_root: Path,
    *,
    started: datetime,
    status: str,
    stage: str,
    worker_processes: list[mp.Process],
    desired_workers: int,
    protected_workers: list[dict[str, Any]],
) -> dict[str, Any]:
    paths = accelerator_paths(run_root)
    ledger_path = run_root / "00_control" / "run_state.sqlite"
    quote_counts = family_counts(ledger_path, FAMILY)
    minute_counts = family_counts(ledger_path, "ohlcv_1m")
    worker_rows = [
        {
            "pid": int(process.pid) if process.pid else None,
            "alive": process.is_alive(),
            "exitcode": process.exitcode,
        }
        for process in worker_processes
    ]
    payload = {
        "accelerator_version": ACCELERATOR_VERSION,
        "run_id": run_root.name,
        "status": status,
        "stage": stage,
        "observed_at_utc": iso_utc(),
        "started_at_utc": iso_utc(started),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 1),
        "coordinator_pid": os.getpid(),
        "desired_quote_workers": desired_workers,
        "alive_quote_workers": sum(bool(row["alive"]) for row in worker_rows),
        "quote_workers": worker_rows,
        "quotes_counts": quote_counts,
        "ohlcv_1m_counts": minute_counts,
        "protected_workers": protected_workers,
    }
    AUDIT.atomic_write_json(paths["heartbeat"], payload)
    with paths["heartbeat_log"].open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
    AUDIT.atomic_write_json(
        paths["pids"],
        {
            "observed_at_utc": payload["observed_at_utc"],
            "coordinator_pid": os.getpid(),
            "worker_pids": [row["pid"] for row in worker_rows if row["alive"]],
            "protected_workers": protected_workers,
        },
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--replace-worker-pid", type=int, required=True)
    parser.add_argument("--initial-workers", type=int, default=2, choices=range(1, 5))
    parser.add_argument("--scale-workers", type=int, default=3, choices=range(1, 5))
    parser.add_argument("--heartbeat-seconds", type=int, default=10)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--human-authorized", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.human_authorized:
        raise SystemExit("Quotes worker replacement refused without --human-authorized")
    if args.scale_workers < args.initial_workers:
        raise SystemExit("--scale-workers must be >= --initial-workers")
    run_root = args.run_root.resolve()
    if not run_root.is_dir():
        raise SystemExit(f"Run root does not exist: {run_root}")
    paths = accelerator_paths(run_root)
    paths["root"].mkdir(parents=True, exist_ok=True)
    if paths["final_manifest"].is_file():
        existing = json.loads(paths["final_manifest"].read_text(encoding="utf-8"))
        if existing.get("status") == "completed":
            raise SystemExit("Quotes accelerator already completed")

    pre_manifest_path = run_root / "00_control" / "pre_manifest.json"
    ledger_path = run_root / "00_control" / "run_state.sqlite"
    pre_manifest = json.loads(pre_manifest_path.read_text(encoding="utf-8"))
    config_path = Path(str(pre_manifest["config_path"]))
    config, config_sha = AUDIT.load_config(config_path)
    if config_sha != str(pre_manifest["config_sha256"]):
        raise SystemExit("Current config hash differs from the active run pre-manifest")
    if run_root.name != str(pre_manifest["run_id"]):
        raise SystemExit("Run root name differs from the active run ID")

    initialize_accelerator_ledger(ledger_path)
    verification = verify_replacement_target(run_root, args.replace_worker_pid)
    monitor_command = (
        'powershell -NoProfile -ExecutionPolicy Bypass -File '
        '"C:\\TSIS_Data\\01_TSIS_DATA_FOUNDATION\\scripts\\core_market_raw_alignment_audit\\'
        f'monitor_quotes_accelerator.ps1" -RunRoot "{run_root}" -Watch'
    )
    accelerator_pre_manifest = {
        "run_id": run_root.name,
        "accelerator_version": ACCELERATOR_VERSION,
        "status": "preregistered",
        "created_at_utc": iso_utc(),
        "scope": "quotes_ worker replacement only",
        "source_mutation_policy": "G:/TSIS/data/quotes_ remains read-only",
        "protected_process_policy": "parent, ohlcv_1m and Trades must remain alive and untouched",
        "initial_workers": args.initial_workers,
        "scale_workers": args.scale_workers,
        "scale_gate": "ohlcv_1m committed equals its full ledger cardinality",
        "max_attempts": args.max_attempts,
        "active_run_contract_sha256": pre_manifest["run_contract_sha256"],
        "accelerator_implementation_path": str(Path(__file__).resolve()),
        "accelerator_implementation_sha256": AUDIT.sha256_file(Path(__file__).resolve()),
        "replacement_verification": verification,
        "monitor_command": monitor_command,
    }
    AUDIT.atomic_write_json(paths["pre_manifest"], accelerator_pre_manifest)
    append_log(paths["log"], f"preflight_pass verification={json.dumps(verification, sort_keys=True)}")

    stop_original_quotes_worker(args.replace_worker_pid)
    recovered_ticker = recover_replaced_quote_task(ledger_path, args.replace_worker_pid)
    append_log(
        paths["log"],
        f"original_quotes_worker_stopped pid={args.replace_worker_pid} recovered_ticker={recovered_ticker}",
    )
    for protected in verification["protected_workers"]:
        if not psutil.pid_exists(int(protected["worker_pid"])):
            raise RuntimeError(f"Protected worker died during Quotes replacement: {protected}")

    started = utc_now()
    context = mp.get_context("spawn")
    processes: list[mp.Process] = []

    def launch_one() -> None:
        process = context.Process(
            target=quote_worker,
            args=(
                config,
                str(run_root),
                run_root.name,
                str(pre_manifest["run_contract_sha256"]),
                args.max_attempts,
            ),
            name="core-market-audit-quotes-accelerated",
        )
        process.start()
        processes.append(process)
        append_log(paths["log"], f"quote_worker_launched pid={process.pid}")

    for _ in range(args.initial_workers):
        launch_one()

    desired = args.initial_workers
    last_heartbeat = 0.0
    status = "running"
    stage = "quotes_two_workers"
    try:
        while True:
            quote_counts = family_counts(ledger_path, FAMILY)
            minute_counts = family_counts(ledger_path, "ohlcv_1m")
            if int(minute_counts.get("committed", 0)) == int(minute_counts["total"]):
                desired = args.scale_workers
                stage = "quotes_scaled_after_ohlcv_1m"

            alive = [process for process in processes if process.is_alive()]
            pending = int(quote_counts.get("pending", 0))
            running = int(quote_counts.get("running", 0))
            committed = int(quote_counts.get("committed", 0))
            failed = int(quote_counts.get("failed", 0))
            if failed:
                raise RuntimeError(f"Terminal Quotes task failures detected: {failed}")
            if committed == int(quote_counts["total"]) and pending == 0 and running == 0:
                status = "completed"
                stage = "quotes_complete"
                break
            if pending > 0:
                while len(alive) < desired:
                    launch_one()
                    alive = [process for process in processes if process.is_alive()]
            now = time.monotonic()
            if now - last_heartbeat >= max(2, args.heartbeat_seconds):
                write_accelerator_heartbeat(
                    run_root,
                    started=started,
                    status=status,
                    stage=stage,
                    worker_processes=processes,
                    desired_workers=desired,
                    protected_workers=verification["protected_workers"],
                )
                last_heartbeat = now
            time.sleep(1)
    except Exception:
        status = "failed"
        stage = "accelerator_failed"
        append_log(paths["log"], traceback.format_exc())
        raise
    finally:
        for process in processes:
            process.join(timeout=2)
        payload = write_accelerator_heartbeat(
            run_root,
            started=started,
            status=status,
            stage=stage,
            worker_processes=processes,
            desired_workers=desired,
            protected_workers=verification["protected_workers"],
        )
        final_payload = {
            "run_id": run_root.name,
            "status": status,
            "stage": stage,
            "completed_at_utc": iso_utc(),
            "replacement_pid": args.replace_worker_pid,
            "recovered_ticker": recovered_ticker,
            "quotes_counts": payload["quotes_counts"],
            "ohlcv_1m_counts": payload["ohlcv_1m_counts"],
            "worker_processes": payload["quote_workers"],
            "pre_manifest_path": str(paths["pre_manifest"]),
            "pre_manifest_sha256": AUDIT.sha256_file(paths["pre_manifest"]),
        }
        AUDIT.atomic_write_json(paths["final_manifest"], final_payload)
        append_log(paths["log"], f"accelerator_terminal status={status} stage={stage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
