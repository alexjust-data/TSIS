"""Add Quotes audit workers without stopping the active Quotes pool or Trades.

The sidecar reuses the already-tested transactional claim/commit functions from
``accelerate_quotes_workers``.  It writes its own pre-manifest, PID manifest,
heartbeat, logs and final manifest.  All source data remains read-only.
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

import accelerate_quotes_workers as ACCEL


VERSION = "0.1.0"
FAMILY = ACCEL.FAMILY


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def paths(run_root: Path) -> dict[str, Path]:
    root = run_root / "00_control" / "quotes_scaleout_6_workers"
    return {
        "root": root,
        "pre_manifest": root / "pre_manifest.json",
        "pids": root / "pids.json",
        "heartbeat": root / "heartbeat.json",
        "heartbeat_log": root / "heartbeat.jsonl",
        "log": root / "scaleout.log",
        "final_manifest": root / "final_manifest.json",
        "launch_lock": root / "launch.lock",
    }


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{iso_utc()} {message}\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pid_alive(pid: int | None) -> bool:
    return bool(pid and psutil.pid_exists(int(pid)))


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def acquire_launch_lock(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"Scale-out launch lock already exists: {path}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"created_at_utc": iso_utc(), "pid": os.getpid()}))
        handle.flush()
        os.fsync(handle.fileno())


def ledger_snapshot(ledger_path: Path) -> dict[str, Any]:
    connection = ACCEL.AUDIT.connect_ledger(ledger_path)
    try:
        counts = {
            str(status): int(count)
            for status, count in connection.execute(
                "SELECT status,COUNT(*) FROM tasks WHERE family=? GROUP BY status",
                (FAMILY,),
            )
        }
        total = int(
            connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE family=?", (FAMILY,)
            ).fetchone()[0]
        )
        active = [
            {"ticker": str(ticker), "worker_pid": int(worker_pid), "attempt": int(attempt)}
            for ticker, worker_pid, attempt in connection.execute(
                "SELECT ticker,worker_pid,attempt FROM tasks "
                "WHERE family=? AND status='running' ORDER BY ticker",
                (FAMILY,),
            )
        ]
        trades = [
            {"ticker": str(ticker), "worker_pid": int(worker_pid)}
            for ticker, worker_pid in connection.execute(
                "SELECT ticker,worker_pid FROM tasks "
                "WHERE family='trades_ticks_prod_2005_2026' AND status='running'"
            )
        ]
        duplicate_active = int(
            connection.execute(
                "SELECT COUNT(*) FROM (SELECT family,ticker,COUNT(*) AS n FROM tasks "
                "WHERE status='running' GROUP BY family,ticker HAVING n>1)"
            ).fetchone()[0]
        )
    finally:
        connection.close()
    counts["total"] = total
    return {
        "quotes_counts": counts,
        "active_quotes": active,
        "active_trades": trades,
        "duplicate_active_tasks": duplicate_active,
    }


def preflight(run_root: Path, target_total_workers: int) -> dict[str, Any]:
    control = run_root / "00_control"
    ledger_path = control / "run_state.sqlite"
    run_pre_manifest_path = control / "pre_manifest.json"
    accelerator_heartbeat_path = control / "quotes_accelerator" / "heartbeat.json"
    accelerator_pids_path = control / "quotes_accelerator" / "pids.json"
    for required in (
        ledger_path,
        run_pre_manifest_path,
        accelerator_heartbeat_path,
        accelerator_pids_path,
    ):
        if not required.is_file():
            raise RuntimeError(f"Required active-run artifact is missing: {required}")

    run_pre_manifest = read_json(run_pre_manifest_path)
    accelerator_heartbeat = read_json(accelerator_heartbeat_path)
    accelerator_pids = read_json(accelerator_pids_path)
    if accelerator_heartbeat.get("status") != "running":
        raise RuntimeError(f"Quotes accelerator is not running: {accelerator_heartbeat}")
    heartbeat_age = (utc_now() - parse_utc(str(accelerator_heartbeat["observed_at_utc"]))).total_seconds()
    if heartbeat_age > 60:
        raise RuntimeError(f"Quotes accelerator heartbeat is stale: {heartbeat_age:.1f}s")

    coordinator_pid = int(accelerator_pids["coordinator_pid"])
    existing_worker_pids = [int(pid) for pid in accelerator_pids.get("worker_pids", [])]
    if not pid_alive(coordinator_pid):
        raise RuntimeError(f"Quotes accelerator coordinator is not alive: {coordinator_pid}")
    if not existing_worker_pids or not all(pid_alive(pid) for pid in existing_worker_pids):
        raise RuntimeError(f"Existing Quotes workers are not all alive: {existing_worker_pids}")
    additional_workers = target_total_workers - len(existing_worker_pids)
    if additional_workers <= 0:
        raise RuntimeError(
            f"Target {target_total_workers} does not exceed active pool {len(existing_worker_pids)}"
        )

    snapshot = ledger_snapshot(ledger_path)
    if int(snapshot["quotes_counts"].get("failed", 0)):
        raise RuntimeError(f"Quotes already has terminal failures: {snapshot['quotes_counts']}")
    if int(snapshot["duplicate_active_tasks"]):
        raise RuntimeError(f"Duplicate active task ownership detected: {snapshot}")
    active_owner_pids = {int(row["worker_pid"]) for row in snapshot["active_quotes"]}
    if not set(existing_worker_pids).issubset(active_owner_pids):
        raise RuntimeError(
            f"Existing pool PIDs do not own the expected active tasks: {snapshot['active_quotes']}"
        )
    trades = snapshot["active_trades"]
    if len(trades) != 1 or not pid_alive(int(trades[0]["worker_pid"])):
        raise RuntimeError(f"Trades worker is not uniquely active and alive: {trades}")

    config_path = Path(str(run_pre_manifest["config_path"]))
    config, config_sha = ACCEL.AUDIT.load_config(config_path)
    if config_sha != str(run_pre_manifest["config_sha256"]):
        raise RuntimeError("Current config hash differs from the active run pre-manifest")
    return {
        "run_pre_manifest": run_pre_manifest,
        "config": config,
        "config_path": str(config_path),
        "ledger_path": str(ledger_path),
        "existing_coordinator_pid": coordinator_pid,
        "existing_worker_pids": existing_worker_pids,
        "additional_workers": additional_workers,
        "target_total_workers": target_total_workers,
        "trades_worker": trades[0],
        "accelerator_heartbeat_age_seconds": round(heartbeat_age, 3),
        "initial_ledger_snapshot": snapshot,
    }


def recover_added_worker_tasks(ledger_path: Path, worker_pids: list[int], reason: str) -> list[str]:
    if not worker_pids:
        return []
    recovered: list[str] = []
    connection = ACCEL.AUDIT.connect_ledger(ledger_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        placeholders = ",".join("?" for _ in worker_pids)
        rows = connection.execute(
            f"SELECT ticker FROM tasks WHERE family=? AND status='running' "
            f"AND worker_pid IN ({placeholders})",
            (FAMILY, *worker_pids),
        ).fetchall()
        recovered = [str(row[0]) for row in rows]
        connection.execute(
            f"UPDATE tasks SET status='pending',worker_pid=NULL,started_at_utc=NULL,"
            f"ended_at_utc=NULL,error_message=? WHERE family=? AND status='running' "
            f"AND worker_pid IN ({placeholders})",
            (reason, FAMILY, *worker_pids),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return recovered


def write_heartbeat(
    run_root: Path,
    *,
    started: datetime,
    status: str,
    processes: list[mp.Process],
    preflight_payload: dict[str, Any],
) -> dict[str, Any]:
    output = paths(run_root)
    snapshot = ledger_snapshot(Path(str(preflight_payload["ledger_path"])))
    added_workers = [
        {
            "pid": int(process.pid) if process.pid else None,
            "alive": process.is_alive(),
            "exitcode": process.exitcode,
        }
        for process in processes
    ]
    original_pids = [int(pid) for pid in preflight_payload["existing_worker_pids"]]
    payload = {
        "scaleout_version": VERSION,
        "run_id": run_root.name,
        "status": status,
        "observed_at_utc": iso_utc(),
        "started_at_utc": iso_utc(started),
        "elapsed_seconds": round((utc_now() - started).total_seconds(), 1),
        "coordinator_pid": os.getpid(),
        "target_total_quote_workers": int(preflight_payload["target_total_workers"]),
        "original_quote_worker_pids": original_pids,
        "original_quote_workers_alive": sum(pid_alive(pid) for pid in original_pids),
        "added_quote_workers": added_workers,
        "added_quote_workers_alive": sum(bool(row["alive"]) for row in added_workers),
        "trades_worker": preflight_payload["trades_worker"],
        "trades_worker_alive": pid_alive(int(preflight_payload["trades_worker"]["worker_pid"])),
        **snapshot,
    }
    ACCEL.AUDIT.atomic_write_json(output["heartbeat"], payload)
    with output["heartbeat_log"].open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
    ACCEL.AUDIT.atomic_write_json(
        output["pids"],
        {
            "observed_at_utc": payload["observed_at_utc"],
            "coordinator_pid": os.getpid(),
            "worker_pids": [row["pid"] for row in added_workers if row["alive"]],
            "original_quote_worker_pids": original_pids,
            "trades_worker": preflight_payload["trades_worker"],
        },
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--target-total-workers", type=int, default=6, choices=range(4, 9))
    parser.add_argument("--heartbeat-seconds", type=int, default=10)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--human-authorized", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.human_authorized:
        raise SystemExit("Quotes scale-out refused without --human-authorized")
    run_root = args.run_root.resolve()
    if not run_root.is_dir():
        raise SystemExit(f"Run root does not exist: {run_root}")
    output = paths(run_root)
    output["root"].mkdir(parents=True, exist_ok=True)
    if output["pids"].is_file():
        prior = read_json(output["pids"])
        if pid_alive(int(prior.get("coordinator_pid") or 0)):
            raise SystemExit(f"Quotes scale-out is already active: {prior}")
    if output["final_manifest"].is_file():
        prior_final = read_json(output["final_manifest"])
        if prior_final.get("status") == "completed":
            raise SystemExit("Quotes scale-out already completed")
    verification = preflight(run_root, args.target_total_workers)
    acquire_launch_lock(output["launch_lock"])
    pre_manifest = {
        "run_id": run_root.name,
        "scaleout_version": VERSION,
        "status": "preregistered",
        "created_at_utc": iso_utc(),
        "scope": "add Quotes workers only; preserve existing Quotes pool and Trades",
        "source_mutation_policy": "G:/TSIS/data/quotes_ remains read-only",
        "claim_policy": "SQLite BEGIN IMMEDIATE plus exact PID/attempt ownership commit",
        "target_total_quote_workers": args.target_total_workers,
        "additional_quote_workers": verification["additional_workers"],
        "max_attempts": args.max_attempts,
        "verification": {key: value for key, value in verification.items() if key != "config"},
        "implementation_path": str(Path(__file__).resolve()),
        "implementation_sha256": ACCEL.AUDIT.sha256_file(Path(__file__).resolve()),
        "monitor_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            f'"{Path(__file__).resolve().parent / "monitor_quotes_scaleout.ps1"}" '
            f'-RunRoot "{run_root}" -Watch'
        ),
    }
    ACCEL.AUDIT.atomic_write_json(output["pre_manifest"], pre_manifest)
    append_log(output["log"], f"preflight_pass {json.dumps(pre_manifest, sort_keys=True)}")

    started = utc_now()
    context = mp.get_context("spawn")
    processes: list[mp.Process] = []
    status = "running"
    failure: str | None = None
    recovered: list[str] = []
    try:
        for _ in range(int(verification["additional_workers"])):
            process = context.Process(
                target=ACCEL.quote_worker,
                args=(
                    verification["config"],
                    str(run_root),
                    run_root.name,
                    str(verification["run_pre_manifest"]["run_contract_sha256"]),
                    args.max_attempts,
                ),
                name="core-market-audit-quotes-scaleout",
            )
            process.start()
            processes.append(process)
            append_log(output["log"], f"added_quote_worker_launched pid={process.pid}")

        last_heartbeat = 0.0
        while True:
            snapshot = ledger_snapshot(Path(str(verification["ledger_path"])))
            counts = snapshot["quotes_counts"]
            if int(counts.get("failed", 0)):
                raise RuntimeError(f"Terminal Quotes task failures detected: {counts}")
            if int(snapshot["duplicate_active_tasks"]):
                raise RuntimeError(f"Duplicate active task ownership detected: {snapshot}")
            if not pid_alive(int(verification["trades_worker"]["worker_pid"])):
                raise RuntimeError("Protected Trades worker died during Quotes scale-out")
            pending = int(counts.get("pending", 0))
            running = int(counts.get("running", 0))
            committed = int(counts.get("committed", 0))
            total = int(counts["total"])
            if pending > 0 and not all(
                pid_alive(int(pid)) for pid in verification["existing_worker_pids"]
            ):
                raise RuntimeError("An original Quotes worker died while tasks remain pending")
            if committed == total and pending == 0 and running == 0:
                status = "completed"
                break
            unexpected = [process for process in processes if not process.is_alive() and process.exitcode]
            if unexpected and pending > 0:
                raise RuntimeError(
                    "Added Quotes worker exited unexpectedly: "
                    + json.dumps(
                        [{"pid": process.pid, "exitcode": process.exitcode} for process in unexpected]
                    )
                )
            now = time.monotonic()
            if now - last_heartbeat >= max(2, args.heartbeat_seconds):
                write_heartbeat(
                    run_root,
                    started=started,
                    status=status,
                    processes=processes,
                    preflight_payload=verification,
                )
                last_heartbeat = now
            time.sleep(1)
    except BaseException as exc:
        status = "failed" if not isinstance(exc, KeyboardInterrupt) else "interrupted"
        failure = f"{type(exc).__name__}: {exc}"
        append_log(output["log"], failure + "\n" + traceback.format_exc())
        for process in processes:
            if process.is_alive():
                process.terminate()
        for process in processes:
            process.join(timeout=30)
        recovered = recover_added_worker_tasks(
            Path(str(verification["ledger_path"])),
            [int(process.pid) for process in processes if process.pid],
            "recovered_after_quotes_scaleout_interruption",
        )
        if not isinstance(exc, KeyboardInterrupt):
            raise
    finally:
        for process in processes:
            process.join(timeout=2)
        heartbeat = write_heartbeat(
            run_root,
            started=started,
            status=status,
            processes=processes,
            preflight_payload=verification,
        )
        final_manifest = {
            "run_id": run_root.name,
            "status": status,
            "completed_at_utc": iso_utc(),
            "failure": failure,
            "recovered_tickers": recovered,
            "quotes_counts": heartbeat["quotes_counts"],
            "duplicate_active_tasks": heartbeat["duplicate_active_tasks"],
            "original_quote_worker_pids": verification["existing_worker_pids"],
            "added_quote_workers": heartbeat["added_quote_workers"],
            "trades_worker": verification["trades_worker"],
            "pre_manifest_path": str(output["pre_manifest"]),
            "pre_manifest_sha256": ACCEL.AUDIT.sha256_file(output["pre_manifest"]),
        }
        ACCEL.AUDIT.atomic_write_json(output["final_manifest"], final_manifest)
        append_log(output["log"], f"scaleout_terminal status={status}")
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
