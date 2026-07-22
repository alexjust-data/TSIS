#!/usr/bin/env python
"""
Governed wrapper for EXP_DAS_FRONTSIDE_DISCOVERY_0002 scanner 2026.

It launches build_2026_scanner_from_quote_guarded_1m_v0_1.py with --verbose,
records PID/log/heartbeat, and lets a human monitor progress while the run is alive.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BUILDER_ID = "run_scanner_2026_quote_guarded_monitored_v0_1"
DEFAULT_EXPERIMENT_ROOT = Path(r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002")
DEFAULT_SCANNER = DEFAULT_EXPERIMENT_ROOT / "scripts" / "build_2026_scanner_from_quote_guarded_1m_v0_1.py"
DEFAULT_EVIDENCE = DEFAULT_EXPERIMENT_ROOT / "evidence"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_replace_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.{int(time.time() * 1000)}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def parse_log(log_path: Path) -> dict:
    if not log_path.exists():
        return {
            "ok_lines": 0,
            "warn_lines": 0,
            "latest_ok_line": None,
            "latest_line": None,
            "candidates_so_far": None,
        }
    ok_lines = 0
    warn_lines = 0
    progress_lines = 0
    latest_ok = None
    latest_progress = None
    latest = None
    candidates = None
    files_scanned = None
    total_files = None
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                text = line.rstrip("\n")
                if text:
                    latest = text
                if text.startswith("files_to_scan="):
                    m = re.search(r"files_to_scan=(\d+)", text)
                    if m:
                        total_files = int(m.group(1))
                if text.startswith("[OK]"):
                    ok_lines += 1
                    latest_ok = text
                if text.startswith("progress ") or text.startswith("processing "):
                    progress_lines += 1
                    latest_progress = text
                m = re.search(r"files_scanned=(\d+)/(\d+)", text)
                if m:
                    files_scanned = int(m.group(1))
                    total_files = int(m.group(2))
                m = re.search(r"(?:raw_candidates|candidates_so_far)=(\d+)", text)
                if m:
                    candidates = int(m.group(1))
                if text.startswith("[WARN]"):
                    warn_lines += 1
    except OSError as exc:
        latest = f"log_read_error={exc}"
    return {
        "ok_lines": ok_lines,
        "warn_lines": warn_lines,
        "progress_lines": progress_lines,
        "latest_ok_line": latest_ok,
        "latest_progress_line": latest_progress,
        "latest_line": latest,
        "files_scanned": files_scanned,
        "total_files": total_files,
        "candidates_so_far": candidates,
    }


def pid_alive(pid: int | None) -> bool | None:
    if not pid:
        return None
    try:
        import psutil  # type: ignore

        return psutil.pid_exists(pid)
    except Exception:
        # On Windows, os.kill(pid, 0) is not reliable for all cases.
        return None


def process_cpu_seconds(pid: int | None) -> float | None:
    if not pid:
        return None
    try:
        import psutil  # type: ignore

        p = psutil.Process(pid)
        c = p.cpu_times()
        return float(c.user + c.system)
    except Exception:
        return None


def output_stats(output_dir: Path) -> dict:
    count = 0
    size = 0
    newest = None
    if output_dir.exists():
        for p in output_dir.rglob("*"):
            if p.is_file():
                count += 1
                try:
                    st = p.stat()
                    size += st.st_size
                    if newest is None or st.st_mtime > newest:
                        newest = st.st_mtime
                except OSError:
                    pass
    return {
        "output_file_count": count,
        "output_bytes": size,
        "output_latest_write_utc": datetime.fromtimestamp(newest, timezone.utc).isoformat() if newest else None,
    }


def write_heartbeat(run_root: Path, payload: dict) -> None:
    monitor_dir = run_root / "monitor"
    latest = monitor_dir / "heartbeat_latest.json"
    jsonl = monitor_dir / "heartbeat.jsonl"
    safe_replace_json(latest, payload)
    with jsonl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def build_command(args: argparse.Namespace, output_dir: Path) -> list[str]:
    cmd = [
        sys.executable,
        "-u",
        str(Path(args.scanner_script)),
        "--output-dir",
        str(output_dir),
        "--year",
        str(args.year),
        "--threshold-pct",
        str(args.threshold_pct),
        "--min-volume",
        str(args.min_volume),
        "--min-price",
        str(args.min_price),
        "--max-price",
        str(args.max_price),
        "--max-market-cap",
        str(args.max_market_cap),
        "--session-start-et",
        args.session_start_et,
        "--session-end-et",
        args.session_end_et,
        "--market-cap-policy",
        args.market_cap_policy,
        "--progress-every",
        str(args.progress_every),
        "--partial-flush-every",
        str(args.partial_flush_every),
        "--verbose",
    ]
    if args.extra_args:
        cmd.extend(args.extra_args)
    return cmd


def run(args: argparse.Namespace) -> int:
    run_id = args.run_id or "scanner_2026_quote_guarded_full_monitored_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = Path(args.output_base) / run_id
    output_dir = run_root / "outputs"
    log_dir = run_root / "logs"
    monitor_dir = run_root / "monitor"
    log_dir.mkdir(parents=True, exist_ok=True)
    monitor_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / "scanner_stdout_stderr.log"
    cmd = build_command(args, output_dir)
    created = utc_now()
    pre_manifest = {
        "run_id": run_id,
        "status": "starting",
        "created_at_utc": created,
        "script_path": str(Path(__file__).resolve()),
        "builder_id": BUILDER_ID,
        "command_line": cmd,
        "cwd": os.getcwd(),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getpid(),
        "output_dir": str(output_dir),
        "log_path": str(log_path),
        "heartbeat_latest": str(monitor_dir / "heartbeat_latest.json"),
        "monitor_command": f'python "{DEFAULT_EXPERIMENT_ROOT / "scripts" / "monitor_scanner_2026_quote_guarded_run_v0_1.py"}" --run-root "{run_root}" --watch',
        "expected_scope": "full 2026 scanner denominator from raw 1m + quote-guarded repair shards",
        "legacy_candidate_events_used": False,
    }
    safe_replace_json(monitor_dir / "pre_manifest.json", pre_manifest)

    with log_path.open("a", encoding="utf-8", errors="replace") as log_fh:
        log_fh.write(f"[{utc_now()}] launching {' '.join(cmd)}\n")
        log_fh.flush()
        proc = subprocess.Popen(cmd, stdout=log_fh, stderr=subprocess.STDOUT, cwd=os.getcwd())

    pid_manifest = {
        "run_id": run_id,
        "wrapper_pid": os.getpid(),
        "child_pid": proc.pid,
        "status": "running",
        "created_at_utc": created,
        "updated_at_utc": utc_now(),
        "command_line": cmd,
        "log_path": str(log_path),
        "output_dir": str(output_dir),
    }
    safe_replace_json(monitor_dir / "pid_manifest.json", pid_manifest)

    started = time.time()
    status = "running"
    return_code = None
    while True:
        return_code = proc.poll()
        if return_code is None:
            status = "running"
        elif return_code == 0:
            status = "complete"
        else:
            status = "failed"

        log_info = parse_log(log_path)
        heartbeat = {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": status,
            "stage": "scanner_denominator_2026",
            "elapsed_seconds": round(time.time() - started, 1),
            "wrapper_pid": os.getpid(),
            "child_pid": proc.pid,
            "child_return_code": return_code,
            "child_alive": return_code is None,
            "child_cpu_seconds": process_cpu_seconds(proc.pid),
            "log_path": str(log_path),
            "log_bytes": log_path.stat().st_size if log_path.exists() else 0,
            "output_dir": str(output_dir),
            **log_info,
            **output_stats(output_dir),
        }
        write_heartbeat(run_root, heartbeat)

        if return_code is not None:
            final_manifest = dict(pre_manifest)
            final_manifest.update(
                {
                    "status": status,
                    "finished_at_utc": utc_now(),
                    "return_code": return_code,
                    "elapsed_seconds": heartbeat["elapsed_seconds"],
                    "final_heartbeat": heartbeat,
                }
            )
            safe_replace_json(monitor_dir / "final_manifest.json", final_manifest)
            return int(return_code)

        time.sleep(args.heartbeat_interval_sec)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scanner-script", default=str(DEFAULT_SCANNER))
    parser.add_argument("--output-base", default=str(DEFAULT_EVIDENCE))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--heartbeat-interval-sec", type=int, default=30)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--threshold-pct", type=float, default=50.0)
    parser.add_argument("--min-volume", type=float, default=500000.0)
    parser.add_argument("--min-price", type=float, default=0.5)
    parser.add_argument("--max-price", type=float, default=20.0)
    parser.add_argument("--max-market-cap", type=float, default=100000000.0)
    parser.add_argument("--session-start-et", default="04:00")
    parser.add_argument("--session-end-et", default="09:30")
    parser.add_argument("--market-cap-policy", default="snapshot_allowed_flagged")
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--partial-flush-every", type=int, default=1)
    parser.add_argument("extra_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))

