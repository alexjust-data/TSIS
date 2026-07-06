#!/usr/bin/env python
"""Compact monitor for governed scanner 2026 runs."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def tail(path: Path, n: int) -> list[str]:
    if not path.exists() or n <= 0:
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-n:]
    except Exception as exc:
        return [f"log_tail_error={exc}"]


def fmt_bytes(n: int | float | None) -> str:
    if n is None:
        return "na"
    n = float(n)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"


def compact_line(run_root: Path, tail_lines: int) -> str:
    hb_path = run_root / "monitor" / "heartbeat_latest.json"
    pid_path = run_root / "monitor" / "pid_manifest.json"
    pre_path = run_root / "monitor" / "pre_manifest.json"
    hb = read_json(hb_path)
    pid = read_json(pid_path) or {}
    pre = read_json(pre_path) or {}
    now = utc_now_dt()

    if not hb:
        return f"[{now.isoformat()}] status=no_heartbeat run_root={run_root} pre_manifest={pre_path.exists()} pid_manifest={pid_path.exists()}"

    observed = hb.get("observed_at_utc")
    try:
        observed_dt = datetime.fromisoformat(observed)
        latest_age = round((now - observed_dt).total_seconds(), 1)
    except Exception:
        latest_age = "na"

    status = hb.get("status")
    if isinstance(latest_age, (int, float)) and latest_age > 180 and status == "running":
        status = "stale_running"

    latest_item = hb.get("latest_progress_line") or hb.get("latest_ok_line") or hb.get("latest_line") or ""
    if len(latest_item) > 140:
        latest_item = latest_item[:137] + "..."

    line = (
        f"[{now.isoformat()}] "
        f"status={status} "
        f"wrapper_pid={pid.get('wrapper_pid', hb.get('wrapper_pid'))} "
        f"child_pid={hb.get('child_pid')} "
        f"elapsed_sec={hb.get('elapsed_seconds')} "
        f"latest_age_sec={latest_age} "
        f"files={hb.get('files_scanned')}/{hb.get('total_files')} "
        f"ok_files={hb.get('ok_lines')} "
        f"progress={hb.get('progress_lines')} "
        f"candidates={hb.get('candidates_so_far')} "
        f"warns={hb.get('warn_lines')} "
        f"log={fmt_bytes(hb.get('log_bytes'))} "
        f"outputs={hb.get('output_file_count')} "
        f"out_bytes={fmt_bytes(hb.get('output_bytes'))} "
        f"latest=\"{latest_item}\""
    )

    if tail_lines:
        log_path = Path(hb.get("log_path") or pre.get("log_path") or "")
        t = tail(log_path, tail_lines)
        if t:
            line += "\n" + "\n".join("  log> " + x for x in t)
    return line


def run(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root)
    while True:
        print(compact_line(run_root, args.tail_log), flush=True)
        if not args.watch:
            return 0
        hb = read_json(run_root / "monitor" / "heartbeat_latest.json")
        if hb and hb.get("status") in {"complete", "failed"}:
            return 0
        time.sleep(args.interval_sec)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval-sec", type=int, default=30)
    parser.add_argument("--tail-log", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
