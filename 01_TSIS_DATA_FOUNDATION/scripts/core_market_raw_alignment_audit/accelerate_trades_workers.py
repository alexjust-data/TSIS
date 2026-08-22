"""Suspend the original Trades worker and run a transactional worker pool.

The original process keeps ownership of its current ticker. Added workers claim
only pending tasks. After they drain, the original worker resumes and lets the
existing parent close normally.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sqlite3
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil

import accelerate_quotes_workers as BASE


FAMILY = "trades_ticks_prod_2005_2026"
VERSION = "0.1.0"
AUDIT = BASE.AUDIT


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def paths(run_root: Path) -> dict[str, Path]:
    root = run_root / "00_control" / "trades_accelerator"
    return {
        "root": root,
        "pre_manifest": root / "pre_manifest.json",
        "heartbeat": root / "heartbeat.json",
        "heartbeat_log": root / "heartbeat.jsonl",
        "pids": root / "pids.json",
        "log": root / "accelerator.log",
        "final_manifest": root / "final_manifest.json",
        "launch_lock": root / "launch.lock",
        "stop_request": root / "stop.requested",
        "stop_ack": root / "stop.acknowledged",
    }


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{iso_utc()} {message}\n")
        handle.flush()
        os.fsync(handle.fileno())


def pid_alive(pid: int | None) -> bool:
    return bool(pid and psutil.pid_exists(int(pid)))


def record_event(
    connection: sqlite3.Connection,
    event_type: str,
    *,
    ticker: str | None = None,
    worker_pid: int | None = None,
    attempt: int | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    connection.execute(
        "INSERT INTO trades_accelerator_events"
        "(observed_at_utc,event_type,ticker,worker_pid,attempt,detail_json) VALUES(?,?,?,?,?,?)",
        (
            iso_utc(),
            event_type,
            ticker,
            worker_pid,
            attempt,
            json.dumps(detail, ensure_ascii=False, sort_keys=True) if detail else None,
        ),
    )


def configure_base() -> None:
    BASE.FAMILY = FAMILY
    BASE.accelerator_paths = paths
    BASE._record_event = record_event


def initialize_event_ledger(ledger_path: Path) -> None:
    connection = AUDIT.connect_ledger(ledger_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS trades_accelerator_events(
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                observed_at_utc TEXT NOT NULL,
                event_type TEXT NOT NULL,
                ticker TEXT,
                worker_pid INTEGER,
                attempt INTEGER,
                detail_json TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_trades_accelerator_events_ticker
                ON trades_accelerator_events(ticker,event_id);
            """
        )
        connection.commit()
    finally:
        connection.close()


def acquire_launch_lock(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"created_at_utc": iso_utc(), "pid": os.getpid()}))
        handle.flush()
        os.fsync(handle.fileno())


def ledger_snapshot(ledger_path: Path) -> dict[str, Any]:
    connection = AUDIT.connect_ledger(ledger_path)
    try:
        counts = {
            str(status): int(count)
            for status, count in connection.execute(
                "SELECT status,COUNT(*) FROM tasks WHERE family=? GROUP BY status", (FAMILY,)
            )
        }
        counts["total"] = int(
            connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE family=?", (FAMILY,)
            ).fetchone()[0]
        )
        active = [
            {"ticker": str(ticker), "worker_pid": int(pid), "attempt": int(attempt)}
            for ticker, pid, attempt in connection.execute(
                "SELECT ticker,worker_pid,attempt FROM tasks "
                "WHERE family=? AND status='running' ORDER BY ticker",
                (FAMILY,),
            )
        ]
        other_open = int(
            connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE family<>? AND status<>'committed'", (FAMILY,)
            ).fetchone()[0]
        )
    finally:
        connection.close()
    return {
        "trades_counts": counts,
        "active_trades": active,
        "other_family_open_tasks": other_open,
    }


def preflight(run_root: Path, workers: int) -> dict[str, Any]:
    control = run_root / "00_control"
    ledger_path = control / "run_state.sqlite"
    pre_manifest_path = control / "pre_manifest.json"
    pids_path = control / "pids.json"
    for required in (ledger_path, pre_manifest_path, pids_path):
        if not required.is_file():
            raise RuntimeError(f"Missing active-run artifact: {required}")
    run_pre = json.loads(pre_manifest_path.read_text(encoding="utf-8"))
    pid_payload = json.loads(pids_path.read_text(encoding="utf-8"))
    parent_pid = int(pid_payload["active_pid"])
    snapshot = ledger_snapshot(ledger_path)
    counts = snapshot["trades_counts"]
    if snapshot["other_family_open_tasks"]:
        raise RuntimeError(f"Non-Trades families are not closed: {snapshot}")
    if int(counts.get("failed", 0)):
        raise RuntimeError(f"Trades has terminal failures: {counts}")
    if int(counts.get("pending", 0)) <= 0:
        raise RuntimeError(f"Trades has no pending work to accelerate: {counts}")
    active = snapshot["active_trades"]
    if len(active) != 1:
        raise RuntimeError(f"Expected exactly one original Trades task: {active}")
    original_pid = int(active[0]["worker_pid"])
    if not pid_alive(parent_pid) or not pid_alive(original_pid):
        raise RuntimeError(
            f"Parent/original worker is not alive: parent={parent_pid} worker={original_pid}"
        )
    process = psutil.Process(original_pid)
    if process.ppid() != parent_pid:
        raise RuntimeError(
            f"Original Trades worker parent mismatch: {process.ppid()} != {parent_pid}"
        )
    command_line = " ".join(process.cmdline())
    if "multiprocessing.spawn" not in command_line or f"parent_pid={parent_pid}" not in command_line:
        raise RuntimeError(f"Unexpected original worker command line: {command_line}")
    config_path = Path(str(run_pre["config_path"]))
    config, config_sha = AUDIT.load_config(config_path)
    if config_sha != str(run_pre["config_sha256"]):
        raise RuntimeError("Active config hash differs from the run pre-manifest")
    return {
        "run_pre_manifest": run_pre,
        "config": config,
        "config_path": str(config_path),
        "ledger_path": str(ledger_path),
        "parent_pid": parent_pid,
        "original_worker_pid": original_pid,
        "original_active_task": active[0],
        "workers": workers,
        "initial_snapshot": snapshot,
    }


def suspend_without_sql_lock(ledger_path: Path, original_pid: int, attempts: int = 20) -> None:
    process = psutil.Process(original_pid)
    for _ in range(attempts):
        process.suspend()
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(ledger_path, timeout=1)
            connection.execute("BEGIN IMMEDIATE")
            connection.commit()
            if process.status() != psutil.STATUS_STOPPED:
                raise RuntimeError(
                    f"Trades worker did not enter stopped state: {process.status()}"
                )
            return
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower():
                raise
            process.resume()
            time.sleep(0.2)
        finally:
            if connection is not None:
                connection.close()
    raise RuntimeError("Could not suspend original Trades worker outside a SQLite transaction")


def recover_added_tasks(ledger_path: Path, worker_pids: list[int], reason: str) -> list[str]:
    if not worker_pids:
        return []
    connection = AUDIT.connect_ledger(ledger_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        placeholders = ",".join("?" for _ in worker_pids)
        rows = connection.execute(
            f"SELECT ticker FROM tasks WHERE family=? AND status='running' "
            f"AND worker_pid IN ({placeholders})",
            (FAMILY, *worker_pids),
        ).fetchall()
        connection.execute(
            f"UPDATE tasks SET status='pending',worker_pid=NULL,started_at_utc=NULL,"
            f"ended_at_utc=NULL,error_message=? WHERE family=? AND status='running' "
            f"AND worker_pid IN ({placeholders})",
            (reason, FAMILY, *worker_pids),
        )
        connection.commit()
        return [str(row[0]) for row in rows]
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def trades_worker(
    config: dict[str, Any],
    run_root_s: str,
    run_id: str,
    run_contract_sha256: str,
    max_attempts: int,
) -> None:
    configure_base()
    BASE.quote_worker(config, run_root_s, run_id, run_contract_sha256, max_attempts)


def write_heartbeat(
    run_root: Path,
    *,
    started: datetime,
    status: str,
    stage: str,
    processes: list[mp.Process],
    verification: dict[str, Any],
) -> dict[str, Any]:
    snapshot = ledger_snapshot(Path(str(verification["ledger_path"])))
    workers = [
        {
            "pid": int(process.pid) if process.pid else None,
            "alive": process.is_alive(),
            "exitcode": process.exitcode,
        }
        for process in processes
    ]
    original_pid = int(verification["original_worker_pid"])
    original_status = None
    if pid_alive(original_pid):
        original_status = psutil.Process(original_pid).status()
    payload = {
        "accelerator_version": VERSION,
        "run_id": run_root.name,
        "status": status,
        "stage": stage,
        "observed_at_utc": iso_utc(),
        "started_at_utc": iso_utc(started),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 1),
        "coordinator_pid": os.getpid(),
        "desired_trades_workers": int(verification["workers"]),
        "added_trades_workers": workers,
        "added_trades_workers_alive": sum(bool(row["alive"]) for row in workers),
        "original_worker_pid": original_pid,
        "original_worker_alive": pid_alive(original_pid),
        "original_worker_status": original_status,
        "parent_pid": int(verification["parent_pid"]),
        "parent_alive": pid_alive(int(verification["parent_pid"])),
        **snapshot,
    }
    output = paths(run_root)
    AUDIT.atomic_write_json(output["heartbeat"], payload)
    with output["heartbeat_log"].open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
    AUDIT.atomic_write_json(
        output["pids"],
        {
            "observed_at_utc": payload["observed_at_utc"],
            "coordinator_pid": os.getpid(),
            "worker_pids": [row["pid"] for row in workers if row["alive"]],
            "original_worker_pid": original_pid,
            "parent_pid": int(verification["parent_pid"]),
        },
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6, choices=range(2, 9))
    parser.add_argument("--heartbeat-seconds", type=int, default=10)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--human-authorized", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.human_authorized:
        raise SystemExit("Trades acceleration refused without --human-authorized")
    configure_base()
    run_root = args.run_root.resolve()
    if not run_root.is_dir():
        raise SystemExit(f"Run root does not exist: {run_root}")
    output = paths(run_root)
    output["root"].mkdir(parents=True, exist_ok=True)
    verification = preflight(run_root, args.workers)
    if args.preflight_only:
        public = {key: value for key, value in verification.items() if key != "config"}
        print(json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    acquire_launch_lock(output["launch_lock"])
    initialize_event_ledger(Path(str(verification["ledger_path"])))
    pre_manifest = {
        "run_id": run_root.name,
        "accelerator_version": VERSION,
        "status": "preregistered",
        "created_at_utc": iso_utc(),
        "scope": "Trades pending tasks only; original active ticker remains privately owned",
        "source_mutation_policy": "G:/TSIS/data/trades_ticks_prod_2005_2026 remains read-only",
        "claim_policy": "SQLite BEGIN IMMEDIATE plus exact PID and attempt commit ownership",
        "original_worker_policy": "suspend, preserve active task, resume after pending drain",
        "workers": args.workers,
        "max_attempts": args.max_attempts,
        "verification": {key: value for key, value in verification.items() if key != "config"},
        "implementation_path": str(Path(__file__).resolve()),
        "implementation_sha256": AUDIT.sha256_file(Path(__file__).resolve()),
        "monitor_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f'"{Path(__file__).resolve().parent / "monitor_trades_accelerator.ps1"}" '
            f'-RunRoot "{run_root}" -Watch'
        ),
        "stop_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f'"{Path(__file__).resolve().parent / "stop_trades_accelerator.ps1"}" '
            f'-RunRoot "{run_root}"'
        ),
    }
    AUDIT.atomic_write_json(output["pre_manifest"], pre_manifest)
    append_log(output["log"], f"preflight_pass {json.dumps(pre_manifest, sort_keys=True)}")

    original_pid = int(verification["original_worker_pid"])
    ledger_path = Path(str(verification["ledger_path"]))
    suspend_without_sql_lock(ledger_path, original_pid)
    append_log(
        output["log"],
        f"original_worker_suspended pid={original_pid} task={verification['original_active_task']}",
    )
    started = utc_now()
    context = mp.get_context("spawn")
    processes: list[mp.Process] = []
    status = "running"
    stage = "accelerated_pending_pool"
    failure: str | None = None
    recovered: list[str] = []
    original_resumed = False
    try:
        for _ in range(args.workers):
            process = context.Process(
                target=trades_worker,
                args=(
                    verification["config"],
                    str(run_root),
                    run_root.name,
                    str(verification["run_pre_manifest"]["run_contract_sha256"]),
                    args.max_attempts,
                ),
                name="core-market-audit-trades-accelerated",
            )
            process.start()
            processes.append(process)
            append_log(output["log"], f"trades_worker_launched pid={process.pid}")
        last_heartbeat = 0.0
        while True:
            snapshot = ledger_snapshot(ledger_path)
            counts = snapshot["trades_counts"]
            pending = int(counts.get("pending", 0))
            running = int(counts.get("running", 0))
            committed = int(counts.get("committed", 0))
            failed = int(counts.get("failed", 0))
            total = int(counts["total"])
            if failed:
                raise RuntimeError(f"Terminal Trades task failures detected: {counts}")
            if not pid_alive(int(verification["parent_pid"])):
                raise RuntimeError("Original audit parent died during Trades acceleration")
            if output["stop_request"].is_file():
                os.replace(output["stop_request"], output["stop_ack"])
                raise KeyboardInterrupt("controlled stop requested")
            unexpected = [
                process for process in processes if not process.is_alive() and process.exitcode
            ]
            if unexpected and pending > 0:
                raise RuntimeError(
                    "Added Trades worker exited unexpectedly: "
                    + json.dumps(
                        [{"pid": process.pid, "exitcode": process.exitcode} for process in unexpected]
                    )
                )
            if not original_resumed and pending == 0 and running <= 1:
                psutil.Process(original_pid).resume()
                original_resumed = True
                stage = "original_worker_final_drain"
                append_log(output["log"], f"original_worker_resumed pid={original_pid}")
            if original_resumed and committed == total and pending == 0 and running == 0:
                status = "completed"
                stage = "trades_complete"
                break
            now = time.monotonic()
            if now - last_heartbeat >= max(2, args.heartbeat_seconds):
                write_heartbeat(
                    run_root,
                    started=started,
                    status=status,
                    stage=stage,
                    processes=processes,
                    verification=verification,
                )
                last_heartbeat = now
            time.sleep(1)
    except BaseException as exc:
        status = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        stage = "rollback_to_original_worker"
        failure = f"{type(exc).__name__}: {exc}"
        append_log(output["log"], failure + "\n" + traceback.format_exc())
        for process in processes:
            if process.is_alive():
                process.terminate()
        for process in processes:
            process.join(timeout=30)
        recovered = recover_added_tasks(
            ledger_path,
            [int(process.pid) for process in processes if process.pid],
            "recovered_after_trades_accelerator_interruption",
        )
        if pid_alive(original_pid) and not original_resumed:
            psutil.Process(original_pid).resume()
            original_resumed = True
            append_log(output["log"], f"original_worker_resumed_after_rollback pid={original_pid}")
        if not isinstance(exc, KeyboardInterrupt):
            raise
    finally:
        for process in processes:
            process.join(timeout=2)
        heartbeat = write_heartbeat(
            run_root,
            started=started,
            status=status,
            stage=stage,
            processes=processes,
            verification=verification,
        )
        final_manifest = {
            "run_id": run_root.name,
            "status": status,
            "stage": stage,
            "completed_at_utc": iso_utc(),
            "failure": failure,
            "recovered_tickers": recovered,
            "original_worker_resumed": original_resumed,
            "trades_counts": heartbeat["trades_counts"],
            "added_trades_workers": heartbeat["added_trades_workers"],
            "pre_manifest_path": str(output["pre_manifest"]),
            "pre_manifest_sha256": AUDIT.sha256_file(output["pre_manifest"]),
        }
        AUDIT.atomic_write_json(output["final_manifest"], final_manifest)
        append_log(output["log"], f"accelerator_terminal status={status} stage={stage}")
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
