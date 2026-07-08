#!/usr/bin/env python
"""
Wrapper gobernado para el denominador 2026 de EXP_DAS_FRONTSIDE_DISCOVERY_0002.

Esta version lanza el scanner sobre la base materializada:

    ohlcv_1m_quote_guarded_full_universe_v0_1

No vuelve a reconstruir la vista desde raw 1m + shards durante el scanner.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BUILDER_ID = "run_scanner_2026_qg_full_universe_monitored_v0_2"
DEFAULT_EXPERIMENT_ROOT = Path(r"C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002")
DEFAULT_SCANNER = DEFAULT_EXPERIMENT_ROOT / "scripts" / "build_2026_scanner_from_qg_full_universe_1m_v0_2.py"
DEFAULT_MONITOR = DEFAULT_EXPERIMENT_ROOT / "scripts" / "monitor_scanner_2026_quote_guarded_run_v0_1.py"
DEFAULT_EVIDENCE = DEFAULT_EXPERIMENT_ROOT / "evidence"
DEFAULT_SOURCE_DATASET = (
    r"C:\TSIS_Data\data\data_foundation_outputs"
    r"\ohlcv_1m_quote_guarded_full_universe_v0_1"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_shared_monitoring_module():
    shared_path = DEFAULT_EXPERIMENT_ROOT / "scripts" / "run_scanner_2026_quote_guarded_monitored_v0_1.py"
    spec = importlib.util.spec_from_file_location("_scanner_monitoring_v0_1", shared_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import shared monitoring module: {shared_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
    if args.tickers:
        cmd.extend(["--tickers", args.tickers])
    if args.extra_args:
        cmd.extend(args.extra_args)
    return cmd


def run(args: argparse.Namespace) -> int:
    shared = load_shared_monitoring_module()
    run_id = args.run_id or (
        "scanner_2026_qg_full_universe_full_monitored_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
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
        "scanner_script": str(Path(args.scanner_script).resolve()),
        "command_line": cmd,
        "cwd": os.getcwd(),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getpid(),
        "source_input_1m_dataset": "ohlcv_1m_quote_guarded_full_universe_v0_1",
        "source_input_1m_root": args.source_input_1m_root,
        "output_dir": str(output_dir),
        "log_path": str(log_path),
        "heartbeat_latest": str(monitor_dir / "heartbeat_latest.json"),
        "monitor_command": f'python "{DEFAULT_MONITOR}" --run-root "{run_root}" --watch --tail-log 3',
        "expected_scope": "full 2026 scanner denominator from materialized quote-guarded full-universe 1m",
        "legacy_candidate_events_used": False,
        "raw_plus_repair_on_the_fly_used": False,
    }
    shared.safe_replace_json(monitor_dir / "pre_manifest.json", pre_manifest)

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
    shared.safe_replace_json(monitor_dir / "pid_manifest.json", pid_manifest)

    started = time.time()
    while True:
        return_code = proc.poll()
        if return_code is None:
            status = "running"
        elif return_code == 0:
            status = "complete"
        else:
            status = "failed"

        log_info = shared.parse_log(log_path)
        heartbeat = {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": status,
            "stage": "scanner_denominator_2026_qg_full_universe",
            "elapsed_seconds": round(time.time() - started, 1),
            "wrapper_pid": os.getpid(),
            "child_pid": proc.pid,
            "child_return_code": return_code,
            "child_alive": return_code is None,
            "child_cpu_seconds": shared.process_cpu_seconds(proc.pid),
            "log_path": str(log_path),
            "log_bytes": log_path.stat().st_size if log_path.exists() else 0,
            "output_dir": str(output_dir),
            **log_info,
            **shared.output_stats(output_dir),
        }
        shared.write_heartbeat(run_root, heartbeat)

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
            shared.safe_replace_json(monitor_dir / "final_manifest.json", final_manifest)
            return int(return_code)

        time.sleep(args.heartbeat_interval_sec)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scanner-script", default=str(DEFAULT_SCANNER))
    parser.add_argument("--source-input-1m-root", default=DEFAULT_SOURCE_DATASET)
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
    parser.add_argument("--partial-flush-every", type=int, default=25)
    parser.add_argument("--tickers", default=None)
    parser.add_argument("extra_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
