from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Monitor OHLCV 1m quote-guarded merge run.")
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--watch", action="store_true")
    p.add_argument("--interval-sec", type=float, default=30.0)
    p.add_argument("--compact", action="store_true")
    return p


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def age_sec(ts: Optional[str]) -> Optional[float]:
    if not ts:
        return None
    try:
        value = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - value.astimezone(timezone.utc)).total_seconds()
    except Exception:
        return None


def pid_alive(pid: Any) -> Optional[bool]:
    if pid is None:
        return None
    try:
        pid_int = int(pid)
    except Exception:
        return None
    try:
        import os

        if os.name == "nt":
            import ctypes

            process_query_limited_information = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, pid_int)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
    except Exception:
        pass
    try:
        import os

        os.kill(pid_int, 0)
        return True
    except PermissionError:
        return True
    except Exception:
        return False


def render(run_root: Path, compact: bool) -> str:
    heartbeat = read_json(run_root / "heartbeat_latest.json") or {}
    pid_manifest = read_json(run_root / "pid_manifest.json") or {}
    final_manifest = read_json(run_root / "final_manifest_merge.json")
    counters = heartbeat.get("counters") or {}
    observed_at = heartbeat.get("observed_at_utc")
    wrapper_pid = heartbeat.get("wrapper_pid") or pid_manifest.get("wrapper_pid")
    alive = pid_alive(wrapper_pid) if wrapper_pid else None
    raw_status = heartbeat.get("status", "unknown")
    status = raw_status
    latest_age = age_sec(observed_at)
    if final_manifest:
        status = final_manifest.get("status", status)
    elif raw_status == "running" and latest_age is not None and latest_age > 180 and alive is False:
        status = "stale_no_process"

    if compact:
        return (
            f"[{datetime.now().isoformat(timespec='seconds')}] "
            f"status={status} raw_status={raw_status} stage={heartbeat.get('stage')} "
            f"wrapper_pid={wrapper_pid} wrapper_alive={alive} "
            f"latest_age_sec={None if latest_age is None else round(latest_age, 1)} "
            f"elapsed_sec={heartbeat.get('elapsed_seconds')} "
            f"original_seen={counters.get('original_files_seen')} "
            f"original_linked={counters.get('original_files_linked_or_copied')} "
            f"original_skipped_delta={counters.get('original_files_skipped_expected_delta_pair')} "
            f"delta_seen={counters.get('delta_files_seen')} "
            f"delta_linked={counters.get('delta_files_linked_or_copied')} "
            f"errors={counters.get('errors')} "
            f"output_free={heartbeat.get('output_free_human')} "
            f"log_size={heartbeat.get('log_size')} "
            f"final_manifest={(run_root / 'final_manifest_merge.json') if final_manifest else ''}"
        )

    return json.dumps(
        {
            "status": status,
            "raw_status": raw_status,
            "stage": heartbeat.get("stage"),
            "wrapper_pid": wrapper_pid,
            "wrapper_alive": alive,
            "heartbeat_age_sec": latest_age,
            "elapsed_seconds": heartbeat.get("elapsed_seconds"),
            "counters": counters,
            "latest_source": heartbeat.get("latest_source"),
            "latest_target": heartbeat.get("latest_target"),
            "output_free_human": heartbeat.get("output_free_human"),
            "log_path": heartbeat.get("log_path"),
            "log_size": heartbeat.get("log_size"),
            "final_manifest": str(run_root / "final_manifest_merge.json") if final_manifest else None,
        },
        indent=2,
        default=str,
    )


def main() -> int:
    args = build_parser().parse_args()
    while True:
        print(render(args.run_root, args.compact), flush=True)
        if not args.watch:
            return 0
        final_manifest = read_json(args.run_root / "final_manifest_merge.json")
        if final_manifest:
            return 0
        time.sleep(args.interval_sec)


if __name__ == "__main__":
    raise SystemExit(main())

