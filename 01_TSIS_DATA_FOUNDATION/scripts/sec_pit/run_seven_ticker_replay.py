"""Governed sequential coordinator for the seven-ticker SEC PIT replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ONE_TICKER_RUNNER = SCRIPT_DIR / "run_one_ticker_pilot.py"
DEFAULT_CONFIG = (
    SCRIPT_DIR.parent.parent
    / "configs"
    / "sec_pit_seven_ticker_stratified_replay_v0_1.json"
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def completed(run_root: Path) -> bool:
    final = run_root / "final_manifest.json"
    if not final.is_file():
        return False
    return json.loads(final.read_text(encoding="utf-8-sig")).get("status") == "COMPLETE"


def disk_free_gib(path: Path) -> float:
    anchor = path if path.exists() else path.parent
    while not anchor.exists() and anchor != anchor.parent:
        anchor = anchor.parent
    return shutil.disk_usage(anchor).free / (1024**3)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    value.add_argument("--run-id", required=True)
    value.add_argument("--execute", action="store_true")
    value.add_argument("--metadata-only", action="store_true")
    value.add_argument("--resume", action="store_true")
    value.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT"))
    return value


def main() -> int:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_root = Path(config["output_root"])
    coordinator_root = output_root / "replays" / args.run_id
    if coordinator_root.exists() and not args.resume:
        raise FileExistsError(f"Replay exists; use --resume: {coordinator_root}")
    coordinator_root.mkdir(parents=True, exist_ok=True)

    free_gib = disk_free_gib(output_root)
    floor = float(config["minimum_free_space_gib"])
    if free_gib < floor:
        raise RuntimeError(f"Free-space gate failed: {free_gib:.2f} GiB < {floor:.2f} GiB")
    if (args.execute or args.metadata_only) and not args.user_agent:
        raise ValueError("--user-agent or SEC_USER_AGENT is required with --execute")

    mode = "metadata_only" if args.metadata_only else ("execute" if args.execute else "plan")
    manifest = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "mode": mode,
        "config_path": config_path.as_posix(),
        "config_sha256": sha256(config_path),
        "output_root": output_root.as_posix(),
        "coordinator_root": coordinator_root.as_posix(),
        "case_count": len(config["cases"]),
        "maximum_concurrent_tickers": 1,
        "free_space_gib_at_start": round(free_gib, 3),
        "minimum_free_space_gib": floor,
        "resume_policy": "skip_child_runs_with_complete_final_manifest",
        "promotion_status": "NOT_AUTHORIZED",
        "monitor_command": (
            f'powershell -NoProfile -File "{(SCRIPT_DIR / "monitor_seven_ticker_replay.ps1")}" '
            f'-ReplayRoot "{coordinator_root}" -Compact'
        ),
    }
    atomic_json(coordinator_root / "pre_manifest.json", manifest)
    atomic_json(
        coordinator_root / "pid_manifest.json",
        {"wrapper_pid": os.getpid(), "observed_at_utc": utc_now()},
    )
    print(manifest["monitor_command"], flush=True)

    results: list[dict[str, Any]] = []
    for index, case in enumerate(config["cases"], start=1):
        child_run_id = f"{args.run_id}__{case['ticker'].lower()}"
        child_root = output_root / "runs" / child_run_id
        if args.resume and completed(child_root):
            results.append({"ticker": case["ticker"], "status": "SKIPPED_COMPLETE"})
            continue
        free_gib = disk_free_gib(output_root)
        if free_gib < floor:
            atomic_json(
                coordinator_root / "heartbeat_latest.json",
                {
                    "status": "PAUSED_LOW_DISK",
                    "observed_at_utc": utc_now(),
                    "current_index": index - 1,
                    "total_count": len(config["cases"]),
                    "free_space_gib": round(free_gib, 3),
                },
            )
            return 2
        command = [
            sys.executable,
            str(ONE_TICKER_RUNNER),
            "--ticker",
            case["ticker"],
            "--run-id",
            child_run_id,
            "--output-root",
            str(output_root),
            "--requests-per-second",
            str(config["requests_per_second"]),
            "--max-primary-documents",
            str(config["max_primary_documents"]),
        ]
        if args.metadata_only:
            command.extend(["--execute", "--metadata-only", "--user-agent", args.user_agent])
        elif args.execute:
            command.extend(["--execute", "--user-agent", args.user_agent])
        log_root = coordinator_root / "logs"
        log_root.mkdir(parents=True, exist_ok=True)
        with (log_root / f"{case['ticker']}.stdout.log").open("a", encoding="utf-8") as stdout, (
            log_root / f"{case['ticker']}.stderr.log"
        ).open("a", encoding="utf-8") as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            while process.poll() is None:
                heartbeat = {
                    "run_id": args.run_id,
                    "status": "RUNNING",
                    "mode": mode,
                    "observed_at_utc": utc_now(),
                    "current_index": index - 1,
                    "total_count": len(config["cases"]),
                    "ticker": case["ticker"],
                    "stratum": case["stratum"],
                    "active_pid": process.pid,
                    "free_space_gib": round(disk_free_gib(output_root), 3),
                }
                atomic_json(coordinator_root / "heartbeat_latest.json", heartbeat)
                with (coordinator_root / "heartbeat.jsonl").open("a", encoding="utf-8") as log:
                    log.write(json.dumps(heartbeat) + "\n")
                time.sleep(10 if not args.execute else 60)
        status = "COMPLETE" if process.returncode == 0 else "FAILED"
        results.append({"ticker": case["ticker"], "status": status, "return_code": process.returncode})
        if process.returncode != 0:
            break

    final_status = "COMPLETE" if len(results) == len(config["cases"]) and all(
        row["status"] in {"COMPLETE", "SKIPPED_COMPLETE"} for row in results
    ) else "FAILED"
    atomic_json(
        coordinator_root / "final_manifest.json",
        {**manifest, "status": final_status, "completed_at_utc": utc_now(), "results": results},
    )
    atomic_json(
        coordinator_root / "heartbeat_latest.json",
        {"run_id": args.run_id, "status": final_status, "observed_at_utc": utc_now(), "results": results},
    )
    return 0 if final_status == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
