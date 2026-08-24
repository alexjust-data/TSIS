"""Compact monitor for the governed Quotes restoration audit."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval-seconds", type=int, default=10)
    return parser.parse_args()


def live_pids(run_id: str) -> list[int]:
    result = []
    for process in psutil.process_iter(["pid", "cmdline"]):
        try:
            command = " ".join(process.info.get("cmdline") or [])
            if "audit_quotes_restoration.py" in command and run_id in command:
                result.append(int(process.info["pid"]))
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            pass
    return sorted(result)


def snapshot(run_root: Path) -> dict[str, object]:
    pre = json.loads((run_root / "00_control" / "pre_manifest.json").read_text(encoding="utf-8"))
    database = run_root / "00_control" / "run_state.sqlite"
    uri = database.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=10) as connection:
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
    return {"pre": pre, "counts": counts, "totals": totals, "active": active}


def render(run_root: Path) -> bool:
    data = snapshot(run_root)
    pre = data["pre"]
    counts = data["counts"]
    total = sum(counts.values())
    committed = int(counts.get("committed", 0))
    pids = live_pids(str(pre["run_id"]))
    final_path = run_root / "03_closeout" / "final_manifest.json"
    final = json.loads(final_path.read_text(encoding="utf-8")) if final_path.is_file() else None
    heartbeat_path = run_root / "00_control" / "heartbeat.latest.json"
    heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8")) if heartbeat_path.is_file() else {}
    age = time.time() - heartbeat_path.stat().st_mtime if heartbeat_path.is_file() else float("inf")
    if final:
        status, stage = "completed", "closed"
    elif pids:
        status, stage = "running", str(heartbeat.get("stage", "ticker_physical_audit"))
    elif age > 120:
        status, stage = "stale_no_process", "resume_required"
    else:
        status, stage = "stopped", "not_running"
    totals = [int(v) for v in data["totals"]]
    free = shutil.disk_usage(run_root.anchor or "C:\\").free / 1024**3
    active = ",".join(data["active"]) or "n/a"
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] status={status} stage={stage} "
        f"progress={committed}/{total} pending={counts.get('pending',0)} "
        f"running={counts.get('running',0)} failed={counts.get('failed',0)} "
        f"heartbeat_age_sec={age:.1f} runner_pids={pids or 'n/a'} active={active} "
        f"expected_files={totals[0]} actual_files={totals[1]} matched={totals[2]} "
        f"missing={totals[3]} extra={totals[4]} physical_errors={totals[5]} "
        f"output_free_GB={free:.3f}",
        flush=True,
    )
    if status == "stale_no_process":
        print("WARNING: stale heartbeat and no live runner; resume is required.", flush=True)
    if final:
        print(
            f"final technical_status={final['technical_status']} dataset_status={final['dataset_status']}",
            flush=True,
        )
    return bool(final)


def main() -> int:
    args = parse_args()
    while True:
        try:
            terminal = render(args.run_root)
        except (OSError, sqlite3.Error, json.JSONDecodeError) as exc:
            print(f"status=monitor_retry error={type(exc).__name__}:{exc}", flush=True)
            terminal = False
        if not args.watch or terminal:
            return 0
        time.sleep(max(2, args.interval_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
