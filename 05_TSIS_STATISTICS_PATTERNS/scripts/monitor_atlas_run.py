from __future__ import annotations

import argparse
import ctypes
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _age_seconds(value: str | None) -> float | None:
    if not value:
        return None
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)).total_seconds()
    except ValueError:
        return None


def _pid_alive(value: Any) -> bool | None:
    try:
        pid = int(value)
    except (TypeError, ValueError):
        return None
    if os.name == "nt":
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def render(run_root: Path, compact: bool) -> tuple[str, bool]:
    heartbeat = _read_json(run_root / "heartbeat_latest.json") or {}
    pid_manifest = _read_json(run_root / "pid_manifest.json") or {}
    final = _read_json(run_root / "operation_final_manifest.json")
    wrapper_pid = heartbeat.get("wrapper_pid") or pid_manifest.get("wrapper_pid")
    wrapper_alive = _pid_alive(wrapper_pid)
    latest_age = _age_seconds(heartbeat.get("observed_at_utc"))
    raw_status = str(heartbeat.get("status", "unknown"))
    status = str(final.get("status")) if final else raw_status
    if (
        not final and raw_status == "running" and latest_age is not None
        and latest_age > 180 and wrapper_alive is False
    ):
        status = "stale_no_process"
    active = heartbeat.get("active_child_processes") or []
    current = heartbeat.get("current_index")
    total = heartbeat.get("total_count")
    progress = f"{current}/{total}" if total is not None else "unknown"
    if compact:
        line = (
            f"[{datetime.now().isoformat(timespec='seconds')}] "
            f"status={status} raw_status={raw_status} stage={heartbeat.get('stage')} "
            f"processes={heartbeat.get('process_count', 0)} "
            f"wrapper_pid={wrapper_pid} wrapper_alive={wrapper_alive} "
            f"latest_age_sec={None if latest_age is None else round(latest_age, 1)} "
            f"elapsed_sec={heartbeat.get('elapsed_seconds')} progress={progress} "
            f"shards={heartbeat.get('completed_shards')}/{total} "
            f"item={','.join(str(item.get('label')) for item in active) or '-'} "
            f"cpu={heartbeat.get('cpu_percent')} "
            f"io_read_Bps={heartbeat.get('io_read_Bps')} "
            f"io_write_Bps={heartbeat.get('io_write_Bps')} "
            f"output_free_GB={heartbeat.get('output_free_gb')} "
            f"log_size={heartbeat.get('log_size')} "
            f"error={heartbeat.get('last_error')}"
        )
        return line, final is not None
    payload = {
        "status": status,
        "raw_status": raw_status,
        "stage": heartbeat.get("stage"),
        "wrapper_pid": wrapper_pid,
        "wrapper_alive": wrapper_alive,
        "heartbeat_age_seconds": latest_age,
        "elapsed_seconds": heartbeat.get("elapsed_seconds"),
        "progress": progress,
        "active_children": active,
        "failed_shards": heartbeat.get("failed_shards"),
        "log_path": heartbeat.get("log_path"),
        "log_size": heartbeat.get("log_size"),
        "output_free_gb": heartbeat.get("output_free_gb"),
        "last_error": heartbeat.get("last_error"),
        "operation_final_manifest": (
            str((run_root / "operation_final_manifest.json").resolve()) if final else None
        ),
    }
    return json.dumps(payload, indent=2), final is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor a governed Daily Pattern Atlas run")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--interval-sec", type=float, default=30.0)
    args = parser.parse_args()
    while True:
        output, finished = render(args.run_root.resolve(), args.compact)
        print(output, flush=True)
        if not args.watch or finished:
            return 0
        time.sleep(max(1.0, args.interval_sec))


if __name__ == "__main__":
    raise SystemExit(main())
