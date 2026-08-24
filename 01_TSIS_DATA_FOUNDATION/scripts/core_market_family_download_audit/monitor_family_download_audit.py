"""Read-only compact monitor for one family download-evidence audit."""

from __future__ import annotations

import argparse
import json
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
    args = parser.parse_args()
    if not 2 <= args.interval_seconds <= 300:
        parser.error("--interval-seconds must be between 2 and 300")
    return args


def runner_pids(run_id: str) -> list[int]:
    result: list[int] = []
    for process in psutil.process_iter(["pid", "cmdline"]):
        try:
            command = " ".join(process.info.get("cmdline") or [])
            if "audit_family_download.py" in command and run_id in command:
                result.append(int(process.info["pid"]))
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return sorted(result)


def snapshot(database: Path) -> dict[str, object]:
    uri = database.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=5) as connection:
        connection.execute("PRAGMA query_only=ON")
        run_id = connection.execute(
            "SELECT value FROM run_metadata WHERE key='run_id'"
        ).fetchone()[0]
        counts = dict(connection.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status"))
        totals = connection.execute(
            "SELECT COALESCE(SUM(files_read),0),COALESCE(SUM(rows_read),0),"
            "COALESCE(SUM(activity_rows),0) FROM tasks WHERE status='committed'"
        ).fetchone()
        active = [row[0] for row in connection.execute(
            "SELECT ticker FROM tasks WHERE status='running' ORDER BY ticker"
        ).fetchall()]
    return {
        "run_id": str(run_id),
        "counts": {str(k): int(v) for k, v in counts.items()},
        "files": int(totals[0]),
        "rows": int(totals[1]),
        "activity_rows": int(totals[2]),
        "active": active,
    }


def render(run_root: Path, data: dict[str, object]) -> bool:
    now = datetime.now(timezone.utc)
    counts = data["counts"]
    total = sum(counts.values())
    committed = counts.get("committed", 0)
    pending = counts.get("pending", 0)
    running = counts.get("running", 0)
    failed = counts.get("failed", 0)
    pids = runner_pids(str(data["run_id"]))
    final_path = run_root / "03_closeout" / "final_manifest.json"
    final = json.loads(final_path.read_text(encoding="utf-8")) if final_path.is_file() else None
    if final:
        status = "completed"
        stage = "closed"
    elif pids:
        status = "running"
        stage = "family_ticker_audit"
    elif running:
        status = "stale_no_process"
        stage = "resume_required"
    else:
        status = "stopped"
        stage = "not_running"
    free = shutil.disk_usage(run_root.anchor or "C:\\").free / (1024**3)
    active = ",".join(data["active"]) or "n/a"
    print(
        f"[{now.isoformat()}] status={status} stage={stage} progress={committed}/{total} "
        f"pending={pending} running={running} failed={failed} runner_pids={pids or 'n/a'} "
        f"active={active} files={data['files']} rows={data['rows']} "
        f"activity_rows={data['activity_rows']} output_free_GB={free:.3f}",
        flush=True,
    )
    if status == "stale_no_process":
        print("WARNING: stale task leases detected; repeat the same command with -Resume.", flush=True)
    if final:
        print(
            f"final technical_status={final['technical_status']} "
            f"download_completeness_status={final['download_completeness_status']}",
            flush=True,
        )
    return bool(final) or (committed == total and pending == 0 and running == 0 and failed > 0)


def main() -> int:
    args = parse_args()
    database = args.run_root / "00_control" / "run_state.sqlite"
    if not database.is_file():
        raise FileNotFoundError(f"Ledger not found: {database}")
    while True:
        try:
            terminal = render(args.run_root, snapshot(database))
        except (OSError, sqlite3.Error, json.JSONDecodeError) as exc:
            print(f"status=monitor_retry error={type(exc).__name__}:{exc}", flush=True)
            terminal = False
        if not args.watch or terminal:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

