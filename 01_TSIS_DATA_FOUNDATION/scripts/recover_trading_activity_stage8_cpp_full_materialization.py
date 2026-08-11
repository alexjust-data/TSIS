"""Recover and supervise the authorized TA-3 C++ full materialization.

This recovery runner preserves the identity of the original preregistered run.
It can adopt live shard coordinators left behind by a failed wrapper, resume
interrupted shards from certified block manifests, and launch pending shards
under the original resource gates.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import traceback
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil
import run_trading_activity_stage8_cpp_full_materialization as original
from trading_activity_binding_a_baseline_engine import resolve_stage8_engine

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
COORDINATOR = original.COORDINATOR.resolve()
BLOCK_RUNNER = SCRIPT_DIR / "run_trading_activity_binding_a_multisession_pilot.py"
REPLACE_ATTEMPTS = 20
REPLACE_BASE_DELAY_SECONDS = 0.05
DEFAULT_HEARTBEAT_MAX_AGE_SECONDS = 180.0


def utc_text() -> str:
    return datetime.now(UTC).isoformat()


def _replace_with_retry(
    source: Path,
    target: Path,
    attempts: int = REPLACE_ATTEMPTS,
    base_delay_seconds: float = REPLACE_BASE_DELAY_SECONDS,
) -> None:
    last_error: OSError | None = None
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except OSError as exc:
            last_error = exc
            if attempt + 1 >= attempts:
                break
            time.sleep(base_delay_seconds * (attempt + 1))
    assert last_error is not None
    raise last_error


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{time.time_ns()}.{uuid.uuid4().hex}.tmp"
    )
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        _replace_with_retry(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


# Reuse the original certification logic without its single-attempt telemetry
# writer. This does not alter the already running shard coordinators.
original.atomic_json = atomic_json


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def read_last_jsonl(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - 128 * 1024))
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return None
    for line in reversed(text.splitlines()):
        try:
            value = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict):
            return value
    return None


def option_value(command: list[str], option: str) -> str | None:
    try:
        index = command.index(option)
    except ValueError:
        return None
    return command[index + 1] if index + 1 < len(command) else None


def normalized_path(value: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(value)))


def command_script(command: list[str]) -> str | None:
    for value in command[1:3]:
        if value.lower().endswith((".py", ".pyw")):
            return normalized_path(value)
    return None


def _process_record(process: psutil.Process) -> dict[str, Any] | None:
    try:
        command = process.cmdline()
        return {
            "pid": process.pid,
            "create_time": process.create_time(),
            "name": process.name(),
            "command": command,
        }
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return None


def process_records(
    processes: Iterable[psutil.Process] | None = None,
) -> list[dict[str, Any]]:
    source = processes if processes is not None else psutil.process_iter()
    records = []
    for process in source:
        record = _process_record(process)
        if record is not None:
            records.append(record)
    return records


def command_matches_shard(
    command: list[str], plan: dict[str, Any], shard: dict[str, Any]
) -> bool:
    required = {
        "--run-id": str(shard["run_id"]),
        "--runtime-root": normalized_path(plan["runtime_root"]),
        "--output-root": normalized_path(plan["output_root"]),
        "--pointer-root": normalized_path(plan["pointer_root"]),
        "--shard-index": str(shard["shard_index"]),
        "--shard-count": "4",
        "--stage8-engine": "cpp",
        "--expected-stage8-engine-fingerprint": str(
            plan["expected_stage8_engine_fingerprint"]
        ),
    }
    for option, expected in required.items():
        actual = option_value(command, option)
        if option.endswith("-root"):
            if actual is None or normalized_path(actual) != expected:
                return False
        elif actual != expected:
            return False
    return command_script(command) == normalized_path(COORDINATOR)


def discover_live_shards(
    plan: dict[str, Any],
    records: list[dict[str, Any]] | None = None,
) -> dict[int, dict[str, Any]]:
    records = records if records is not None else process_records()
    by_index: dict[int, dict[str, Any]] = {}
    shard_by_run = {str(s["run_id"]): s for s in plan["shards"]}
    runtime_root = normalized_path(plan["runtime_root"])

    for record in records:
        command = list(record.get("command") or [])
        if not command:
            continue
        run_id = option_value(command, "--run-id")
        runtime = option_value(command, "--runtime-root")
        if run_id not in shard_by_run or runtime is None:
            continue
        if normalized_path(runtime) != runtime_root:
            continue
        shard = shard_by_run[run_id]
        index = int(shard["shard_index"])
        if not command_matches_shard(command, plan, shard):
            raise RuntimeError(
                f"Process claims governed shard {run_id} with mismatched command: "
                f"pid={record['pid']} command={command}"
            )
        if index in by_index:
            raise RuntimeError(
                f"Duplicate live coordinators for shard {run_id}: "
                f"{by_index[index]['pid']} and {record['pid']}"
            )
        by_index[index] = {
            **record,
            "shard": shard,
            "mode": "ADOPTED_COORDINATOR",
        }

    # A coordinator can die while its current block remains alive. Treat that
    # orphan as an occupied shard slot; after it exits, resume the coordinator
    # so the completed/partial block is reconciled before proceeding.
    block_script = normalized_path(BLOCK_RUNNER)
    for record in records:
        command = list(record.get("command") or [])
        run_id = option_value(command, "--run-id")
        runtime = option_value(command, "--runtime-root")
        if (
            not run_id
            or runtime is None
            or command_script(command) != block_script
        ):
            continue
        for shard in plan["shards"]:
            prefix = f"{shard['run_id']}__"
            expected_runtime = normalized_path(
                Path(plan["runtime_root"]) / str(shard["run_id"]) / "blocks"
            )
            if not run_id.startswith(prefix) or normalized_path(runtime) != expected_runtime:
                continue
            index = int(shard["shard_index"])
            if index in by_index:
                break
            by_index[index] = {
                **record,
                "shard": shard,
                "mode": "ADOPTED_ORPHAN_BLOCK",
                "block_run_id": run_id,
            }
            break
    return by_index


def process_identity_alive(state: dict[str, Any]) -> bool:
    try:
        process = psutil.Process(int(state["pid"]))
        return (
            process.is_running()
            and process.status() != psutil.STATUS_ZOMBIE
            and abs(process.create_time() - float(state["create_time"])) < 0.01
        )
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return False


def shard_complete(
    runtime_root: Path, shard: dict[str, Any]
) -> tuple[bool, dict[str, Any] | None]:
    final = read_json(runtime_root / str(shard["run_id"]) / "final_manifest.json")
    expected = int(shard["expected_block_count"])
    complete = bool(
        final
        and final.get("final_status") == "COMPLETE"
        and len(final.get("completed_blocks", [])) == expected
        and not final.get("failed_blocks")
    )
    return complete, final


def shard_progress(runtime_root: Path, shard: dict[str, Any]) -> tuple[int, str | None]:
    complete, final = shard_complete(runtime_root, shard)
    if complete and final is not None:
        return len(final.get("completed_blocks", [])), None
    heartbeat = read_last_jsonl(
        runtime_root / str(shard["run_id"]) / "heartbeat_history.jsonl"
    )
    if heartbeat is None:
        return 0, None
    return int(heartbeat.get("completed_blocks", 0)), heartbeat.get("item")


def aggregate_progress(
    runtime_root: Path, shards: list[dict[str, Any]]
) -> tuple[int, list[str]]:
    completed = 0
    items = []
    for shard in shards:
        count, item = shard_progress(runtime_root, shard)
        completed += count
        if item:
            items.append(str(item))
    return completed, items


def validate_adoption_heartbeat(
    runtime_root: Path,
    state: dict[str, Any],
    max_age_seconds: float,
) -> None:
    shard = state["shard"]
    heartbeat = read_last_jsonl(
        runtime_root / str(shard["run_id"]) / "heartbeat_history.jsonl"
    )
    if heartbeat is None:
        raise RuntimeError(f"No shard heartbeat history for {shard['run_id']}")
    observed = datetime.fromisoformat(
        str(heartbeat["observed_at_utc"]).replace("Z", "+00:00")
    )
    age = (datetime.now(UTC) - observed.astimezone(UTC)).total_seconds()
    if age > max_age_seconds:
        raise RuntimeError(
            f"Shard heartbeat is stale for {shard['run_id']}: {age:.1f}s"
        )
    if state["mode"] == "ADOPTED_COORDINATOR":
        if int(heartbeat.get("wrapper_pid", -1)) != int(state["pid"]):
            raise RuntimeError(
                f"Heartbeat PID mismatch for {shard['run_id']}: "
                f"heartbeat={heartbeat.get('wrapper_pid')} process={state['pid']}"
            )
        if heartbeat.get("status") != "RUNNING":
            raise RuntimeError(
                f"Shard is not RUNNING: {shard['run_id']} {heartbeat.get('status')}"
            )


def validate_recovery_preflight(
    plan: dict[str, Any], plan_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    runtime_root = Path(plan["runtime_root"]).resolve()
    original_pre = read_json(runtime_root / "pre_manifest.json")
    if original_pre is None:
        raise FileNotFoundError(runtime_root / "pre_manifest.json")
    if original_pre.get("plan_sha256") != original.sha256_file(plan_path):
        raise ValueError("Recovery plan hash differs from original pre-manifest")
    if original.sha256_file(Path(original.__file__).resolve()) != plan["runner_sha256"]:
        raise ValueError("Original preregistered runner changed; recovery is fail-closed")
    engine = resolve_stage8_engine("cpp").manifest
    expected_engine = plan["expected_stage8_engine_fingerprint"]
    if engine["engine_fingerprint_sha256"] != expected_engine:
        raise ValueError("Recovery engine fingerprint differs from the plan")
    if (
        original_pre.get("stage8_engine", {}).get("engine_fingerprint_sha256")
        != expected_engine
    ):
        raise ValueError("Original pre-manifest engine fingerprint differs")
    code_paths = {
        "ta3_coordinator_sha256": COORDINATOR,
        "multisession_runner_sha256": BLOCK_RUNNER,
        "conformance_audit_sha256": original.CONFORMANCE_AUDIT,
    }
    for key, path in code_paths.items():
        if original.sha256_file(path) != plan["code_fingerprints"][key]:
            raise ValueError(f"Recovery code hash mismatch for {path}")
    for key, hash_key in (
        ("sample_manifest", "sample_manifest_sha256"),
        ("base_config", "base_config_sha256"),
    ):
        path = Path(plan[key]).resolve()
        if not path.is_file() or original.sha256_file(path) != plan[hash_key]:
            raise ValueError(f"Recovery input hash mismatch: {path}")
    for root_key in ("output_root", "runtime_root", "pointer_root"):
        if not Path(plan[root_key]).resolve().exists():
            raise FileNotFoundError(plan[root_key])
    free_gib = shutil.disk_usage(Path(plan["output_root"]).anchor).free / 1024**3
    if free_gib < float(plan["minimum_free_space_gib"]):
        raise ValueError(f"Insufficient output free space: {free_gib:.2f} GiB")
    return original_pre, engine


def duplicate_recovery_supervisors(plan_path: Path) -> list[int]:
    matches = []
    for record in process_records():
        if int(record["pid"]) == os.getpid():
            continue
        command = list(record.get("command") or [])
        if command_script(command) != normalized_path(SCRIPT_PATH):
            continue
        plan_arg = option_value(command, "--plan")
        if plan_arg and normalized_path(plan_arg) == normalized_path(plan_path):
            matches.append(int(record["pid"]))
    return matches


def safe_log(path: Path, message: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{utc_text()}] {message}\n")
            handle.flush()
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    parser.add_argument("--heartbeat-max-age-seconds", type=float, default=180.0)
    parser.add_argument("--max-restarts-per-shard", type=int, default=3)
    args = parser.parse_args()
    if args.poll_seconds < 1:
        raise ValueError("poll-seconds must be at least 1")

    plan_path = args.plan.resolve()
    plan = original.load_plan(plan_path)
    original_pre, engine = validate_recovery_preflight(plan, plan_path)
    duplicates = duplicate_recovery_supervisors(plan_path)
    if duplicates:
        raise RuntimeError(f"Duplicate recovery supervisor detected: {duplicates}")

    runtime_root = Path(plan["runtime_root"]).resolve()
    output_root = Path(plan["output_root"]).resolve()
    recovery_root = runtime_root / "recovery"
    recovery_root.mkdir(exist_ok=True)
    recovery_log = recovery_root / "run.log"
    recovery_events = recovery_root / "recovery_events.jsonl"
    recovery_pre_path = recovery_root / "pre_manifest.json"
    recovery_pid_path = recovery_root / "pid_manifest.json"
    recovery_final_path = recovery_root / "final_manifest.json"
    root_heartbeat_path = runtime_root / "heartbeat_latest.json"
    root_heartbeat_history = runtime_root / "heartbeat_history.jsonl"
    root_pid_path = runtime_root / "pid_manifest.json"
    root_final_path = runtime_root / "final_manifest.json"
    monitor_command = (
        f"powershell -File {original.MONITOR} -RunRoot {runtime_root} "
        "-IntervalSeconds 30 -Compact -Watch"
    )

    discovered = discover_live_shards(plan)
    completed: list[dict[str, Any]] = []
    active: dict[int, dict[str, Any]] = {}
    pending: list[dict[str, Any]] = []
    for shard in plan["shards"]:
        index = int(shard["shard_index"])
        complete, _ = shard_complete(runtime_root, shard)
        if complete:
            completed.append(
                {
                    "shard_index": index,
                    "run_id": shard["run_id"],
                    "return_code": 0,
                    "recovery_state": "SKIPPED_COMPLETE",
                }
            )
        elif index in discovered:
            state = discovered[index]
            validate_adoption_heartbeat(
                runtime_root, state, args.heartbeat_max_age_seconds
            )
            active[index] = state
        else:
            pending.append(shard)

    preflight = {
        "status": "PREFLIGHT_PASS",
        "run_id": plan["run_id"],
        "recovery_script": str(SCRIPT_PATH),
        "recovery_script_sha256": original.sha256_file(SCRIPT_PATH),
        "plan_path": str(plan_path),
        "plan_sha256": original.sha256_file(plan_path),
        "original_runner_sha256": plan["runner_sha256"],
        "stage8_engine": engine,
        "adopted_shards": [
            {
                "shard_index": index,
                "run_id": state["shard"]["run_id"],
                "pid": state["pid"],
                "mode": state["mode"],
            }
            for index, state in sorted(active.items())
        ],
        "completed_shards": [row["shard_index"] for row in completed],
        "pending_shards": [int(row["shard_index"]) for row in pending],
        "monitor_command": monitor_command,
        "power_loss_resume_command": (
            f'"{sys.executable}" "{SCRIPT_PATH}" --plan "{plan_path}"'
        ),
        "overwrite_policy": "NEVER",
        "canonical_promotion_authorized": False,
    }
    if args.preflight_only:
        print(json.dumps(preflight, indent=2, ensure_ascii=False))
        return 0

    attempt_id = f"recovery_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}_{os.getpid()}"
    started = time.monotonic()
    recovery_pre = {
        **preflight,
        "status": "STARTING",
        "recovery_attempt_id": attempt_id,
        "created_at_utc": utc_text(),
        "command_line": sys.argv,
        "cwd": str(Path.cwd()),
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "original_pre_manifest": str(runtime_root / "pre_manifest.json"),
        "original_failed_final_manifest": str(root_final_path),
        "manifest_paths": {
            "recovery_pre": str(recovery_pre_path),
            "recovery_pid": str(recovery_pid_path),
            "recovery_final": str(recovery_final_path),
            "root_heartbeat": str(root_heartbeat_path),
            "root_heartbeat_history": str(root_heartbeat_history),
            "root_final": str(root_final_path),
        },
        "resume_policy": (
            "ADOPT_VALIDATED_LIVE_SHARDS_ELSE_RESUME_"
            "HASH_VALIDATED_COMPLETE_PARTITIONS"
        ),
        "success_criteria": plan["success_criteria"],
        "safe_stop": f"write {{}} to {runtime_root / 'stop_requested.json'}",
    }
    prior_final = read_json(root_final_path)
    if prior_final is not None:
        prior_path = recovery_root / "prior_global_final_manifest.json"
        if not prior_path.exists():
            atomic_json(prior_path, prior_final)
    atomic_json(recovery_pre_path, recovery_pre)
    append_jsonl(
        recovery_events,
        {
            "event": "RECOVERY_STARTED",
            "observed_at_utc": utc_text(),
            "attempt_id": attempt_id,
            "wrapper_pid": os.getpid(),
            "adopted": preflight["adopted_shards"],
            "pending_shards": preflight["pending_shards"],
        },
    )

    print(f"run_id={plan['run_id']}", flush=True)
    print("mode=RECOVER_FULL_240_BLOCK_CPP_MATERIALIZATION", flush=True)
    print(f"output_roots={original_pre['output_roots']}", flush=True)
    print(f"recovery_pre_manifest={recovery_pre_path}", flush=True)
    print(f"heartbeat={root_heartbeat_path}", flush=True)
    print(f"log={recovery_log}", flush=True)
    print(f"pid_manifest={recovery_pid_path}", flush=True)
    print(f"monitor_command={monitor_command}", flush=True)
    print(f"success_rule={plan['success_criteria']}", flush=True)
    print(f"resume_policy={recovery_pre['resume_policy']}", flush=True)

    for index, state in sorted(active.items()):
        append_jsonl(
            recovery_events,
            {
                "event": state["mode"],
                "observed_at_utc": utc_text(),
                "attempt_id": attempt_id,
                "shard_index": index,
                "run_id": state["shard"]["run_id"],
                "pid": state["pid"],
                "create_time": state["create_time"],
            },
        )

    failed: list[dict[str, Any]] = []
    restart_counts = {int(shard["shard_index"]): 0 for shard in plan["shards"]}
    stop_requested = False
    final_status = "FAILED"
    final_reason: str | None = None
    launch_deferred_reason: str | None = None
    last_launch_at: float | None = None
    last_metrics_at = time.monotonic()
    last_metrics = original.process_tree_metrics(
        [int(state["pid"]) for state in active.values()]
    )
    peak_tree_rss_gib = last_metrics["rss_bytes"] / 1024**3
    peak_tree_private_gib = last_metrics["private_bytes"] / 1024**3
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    peak_memory_percent = memory.percent
    peak_pagefile_used_gib = swap.used / 1024**3
    telemetry_warning: str | None = None

    def emit(stage: str, item: str | None = None) -> None:
        nonlocal last_metrics_at, last_metrics, peak_tree_rss_gib
        nonlocal peak_tree_private_gib, peak_memory_percent
        nonlocal peak_pagefile_used_gib, telemetry_warning
        now = time.monotonic()
        pids = [int(state["pid"]) for state in active.values()]
        tree = original.process_tree_metrics(pids)
        dt = max(now - last_metrics_at, 1e-9)
        cpu_delta = max(tree["cpu_seconds"] - last_metrics["cpu_seconds"], 0.0)
        read_delta = max(
            tree["io_read_bytes"] - last_metrics["io_read_bytes"], 0.0
        )
        write_delta = max(
            tree["io_write_bytes"] - last_metrics["io_write_bytes"], 0.0
        )
        memory_now = psutil.virtual_memory()
        swap_now = psutil.swap_memory()
        rss_gib = tree["rss_bytes"] / 1024**3
        private_gib = tree["private_bytes"] / 1024**3
        peak_tree_rss_gib = max(peak_tree_rss_gib, rss_gib)
        peak_tree_private_gib = max(peak_tree_private_gib, private_gib)
        peak_memory_percent = max(peak_memory_percent, memory_now.percent)
        peak_pagefile_used_gib = max(
            peak_pagefile_used_gib, swap_now.used / 1024**3
        )
        block_done, current_items = aggregate_progress(
            runtime_root, plan["shards"]
        )
        payload = {
            "run_id": plan["run_id"],
            "recovery_attempt_id": attempt_id,
            "supervisor_role": "RECOVERY_ADOPTION_SUPERVISOR",
            "observed_at_utc": utc_text(),
            "status": "STOPPING" if stop_requested else "RUNNING",
            "stage": stage,
            "elapsed_seconds": now - started,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "active_child_pids": pids,
            "adopted_shards": [
                index
                for index, state in active.items()
                if state["mode"].startswith("ADOPTED")
            ],
            "launched_shards": [
                index
                for index, state in active.items()
                if state["mode"] == "LAUNCHED_RESUME"
            ],
            "pending_shards": [int(shard["shard_index"]) for shard in pending],
            "current_item": item or ",".join(current_items[:2]) or None,
            "current_index": block_done,
            "total_count": 240,
            "percentage": 100.0 * block_done / 240.0,
            "completed_blocks": block_done,
            "completed_shards": len(completed),
            "failed_shards": len(failed),
            "active_worker_count": len(active),
            "process_tree_count": int(tree["process_count"]),
            "process_tree_rss_gib": rss_gib,
            "process_tree_private_gib": private_gib,
            "system_cpu_percent": psutil.cpu_percent(interval=None),
            "process_cpu_core_percent": 100.0 * cpu_delta / dt,
            "available_memory_gib": memory_now.available / 1024**3,
            "memory_percent": memory_now.percent,
            "pagefile_used_gib": swap_now.used / 1024**3,
            "io_read_Bps": read_delta / dt,
            "io_write_Bps": write_delta / dt,
            "output_root": str(output_root),
            "output_free_gib": shutil.disk_usage(output_root.anchor).free / 1024**3,
            "log_path": str(recovery_log),
            "log_size": recovery_log.stat().st_size if recovery_log.exists() else 0,
            "launch_deferred_reason": launch_deferred_reason,
            "telemetry_warning": telemetry_warning,
            "power_loss_resume_command": preflight["power_loss_resume_command"],
        }
        pid_payload = {
            "run_id": plan["run_id"],
            "recovery_attempt_id": attempt_id,
            "wrapper_pid": os.getpid(),
            "stage": stage,
            "observed_at_utc": utc_text(),
            "children": [
                {
                    "pid": int(state["pid"]),
                    "create_time": state["create_time"],
                    "shard_index": index,
                    "run_id": state["shard"]["run_id"],
                    "mode": state["mode"],
                    "expected_alive": True,
                }
                for index, state in sorted(active.items())
            ],
        }
        try:
            atomic_json(root_heartbeat_path, payload)
            append_jsonl(root_heartbeat_history, payload)
            atomic_json(recovery_pid_path, pid_payload)
            atomic_json(root_pid_path, pid_payload)
            telemetry_warning = None
        except OSError as exc:
            telemetry_warning = f"{type(exc).__name__}: {exc}"
            safe_log(recovery_log, f"TELEMETRY_DEGRADED {telemetry_warning}")
        safe_log(
            recovery_log,
            f"status={payload['status']} stage={stage} progress={block_done}/240 "
            f"active={len(active)} adopted={payload['adopted_shards']} "
            f"pending={payload['pending_shards']} ram_free_GiB="
            f"{payload['available_memory_gib']:.2f} rss_GiB={rss_gib:.2f} "
            f"defer={launch_deferred_reason}",
        )
        last_metrics_at = now
        last_metrics = tree

    def can_launch_additional() -> bool:
        nonlocal launch_deferred_reason
        policy = plan["parallelism_policy"]
        available_gib = psutil.virtual_memory().available / 1024**3
        if not active:
            required = float(plan["minimum_initial_available_memory_gib"])
            if available_gib < required:
                launch_deferred_reason = (
                    f"RAM_GATE_INITIAL_AVAILABLE_{available_gib:.2f}_"
                    f"REQUIRED_{required:.2f}"
                )
                return False
            return True
        now = time.monotonic()
        stagger = float(policy["additional_worker_stagger_seconds"])
        if last_launch_at is not None and now - last_launch_at < stagger:
            launch_deferred_reason = "STAGGER_OBSERVATION_WINDOW"
            return False
        active_metrics = original.process_tree_metrics(
            [int(state["pid"]) for state in active.values()]
        )
        active_rss_gib = active_metrics["rss_bytes"] / 1024**3
        observed_per_worker = max(
            peak_tree_rss_gib / max(len(active), 1), 4.0
        )
        required_available = max(
            float(policy["minimum_available_memory_gib_for_additional_worker"]),
            observed_per_worker + float(policy["memory_reserve_gib"]),
        )
        if available_gib < required_available:
            launch_deferred_reason = (
                f"RAM_GATE_AVAILABLE_{available_gib:.2f}_"
                f"REQUIRED_{required_available:.2f}"
            )
            return False
        if (
            active_rss_gib + observed_per_worker
            > float(policy["max_process_tree_rss_gib"])
        ):
            launch_deferred_reason = "PROCESS_TREE_RSS_GATE"
            return False
        return True

    try:
        emit("RECOVERY_ADOPTED")
        while pending or active:
            if (runtime_root / "stop_requested.json").exists():
                stop_requested = True
                original.write_stop_requests(
                    runtime_root, "FULL_MATERIALIZATION_RECOVERY_STOP_REQUESTED"
                )
            launch_deferred_reason = None
            while (
                pending
                and not stop_requested
                and not failed
                and len(active) < int(plan["max_concurrent_workers"])
            ):
                if not can_launch_additional():
                    break
                shard = pending.pop(0)
                index = int(shard["shard_index"])
                command = original.command_for(plan, shard, resume=True)
                stdout_path = recovery_root / f"shard_{index}.stdout.log"
                stderr_path = recovery_root / f"shard_{index}.stderr.log"
                stdout = stdout_path.open("a", encoding="utf-8")
                stderr = stderr_path.open("a", encoding="utf-8")
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
                ps_process = psutil.Process(process.pid)
                active[index] = {
                    "pid": process.pid,
                    "create_time": ps_process.create_time(),
                    "name": ps_process.name(),
                    "command": command,
                    "shard": shard,
                    "mode": "LAUNCHED_RESUME",
                    "popen": process,
                    "stdout": stdout,
                    "stderr": stderr,
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "started_at_utc": utc_text(),
                }
                last_launch_at = time.monotonic()
                append_jsonl(
                    recovery_events,
                    {
                        "event": "SHARD_LAUNCHED_RESUME",
                        "observed_at_utc": utc_text(),
                        "attempt_id": attempt_id,
                        "shard_index": index,
                        "run_id": shard["run_id"],
                        "pid": process.pid,
                        "command": command,
                    },
                )
                emit("SHARD_LAUNCHED_RESUME", str(index))

            if stop_requested and not active:
                pending.clear()
                break
            time.sleep(args.poll_seconds)
            for index, state in list(active.items()):
                if process_identity_alive(state):
                    continue
                if state.get("stdout") is not None:
                    state["stdout"].close()
                    state["stderr"].close()
                shard = state["shard"]
                complete, parent_final = shard_complete(runtime_root, shard)
                if complete:
                    record = {
                        "shard_index": index,
                        "run_id": shard["run_id"],
                        "return_code": 0,
                        "recovery_state": f"{state['mode']}_FINISHED_COMPLETE",
                        "pid": state["pid"],
                        "finished_at_utc": utc_text(),
                    }
                    completed.append(record)
                    append_jsonl(
                        recovery_events,
                        {"event": "SHARD_COMPLETE", "attempt_id": attempt_id, **record},
                    )
                    del active[index]
                    emit("SHARD_FINISHED", str(index))
                    continue
                failed_blocks = (parent_final or {}).get("failed_blocks", [])
                if failed_blocks:
                    record = {
                        "shard_index": index,
                        "run_id": shard["run_id"],
                        "recovery_state": "FAILED_BLOCK_REPORTED",
                        "failed_blocks": failed_blocks,
                        "pid": state["pid"],
                    }
                    failed.append(record)
                    del active[index]
                    append_jsonl(
                        recovery_events,
                        {"event": "SHARD_FAILED", "attempt_id": attempt_id, **record},
                    )
                    emit("SHARD_FAILED", str(index))
                    continue
                del active[index]
                restart_counts[index] += 1
                if restart_counts[index] > args.max_restarts_per_shard:
                    record = {
                        "shard_index": index,
                        "run_id": shard["run_id"],
                        "recovery_state": "RESTART_LIMIT_EXCEEDED",
                        "restart_count": restart_counts[index],
                        "pid": state["pid"],
                    }
                    failed.append(record)
                    append_jsonl(
                        recovery_events,
                        {"event": "SHARD_FAILED", "attempt_id": attempt_id, **record},
                    )
                else:
                    pending.insert(0, shard)
                    append_jsonl(
                        recovery_events,
                        {
                            "event": "SHARD_INTERRUPTED_REQUEUE_RESUME",
                            "observed_at_utc": utc_text(),
                            "attempt_id": attempt_id,
                            "shard_index": index,
                            "run_id": shard["run_id"],
                            "prior_mode": state["mode"],
                            "restart_count": restart_counts[index],
                        },
                    )
                emit("SHARD_RECONCILED_AFTER_EXIT", str(index))

            if failed and not active:
                pending.clear()
            emit("FAIL_CLOSED_WAITING_ACTIVE_SHARDS" if failed else "RUNNING")

        if stop_requested:
            final_status = "INTERRUPTED_COOPERATIVE"
            final_reason = "recovery supervisor stop requested"
        elif failed:
            final_reason = "one or more shard coordinators failed recovery gates"
        else:
            certification_path = runtime_root / "full_materialization_certification.json"
            conformance_path = runtime_root / "full_materialization_conformance.json"
            emit("CERTIFY_240_BLOCKS")
            original.certify_full(plan, runtime_root, certification_path)
            emit("AUDIT_240_BLOCK_SCHEMAS")
            audit = subprocess.run(
                [
                    sys.executable,
                    str(original.CONFORMANCE_AUDIT),
                    "--runtime-root",
                    str(runtime_root),
                    "--output",
                    str(conformance_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            (recovery_root / "conformance.stdout.log").write_text(
                audit.stdout, encoding="utf-8"
            )
            (recovery_root / "conformance.stderr.log").write_text(
                audit.stderr, encoding="utf-8"
            )
            if audit.returncode != 0:
                raise RuntimeError(f"Conformance audit failed: {audit.stderr}")
            conformance = read_json(conformance_path)
            if conformance is None or not original.conformance_passes(conformance, 240):
                raise AssertionError("Full variable/schema conformance did not pass")
            final_status = "PASS"
    except Exception as exc:
        final_status = "FAILED"
        final_reason = f"{type(exc).__name__}: {exc}"
        safe_log(recovery_log, traceback.format_exc())
    finally:
        elapsed = time.monotonic() - started
        certification_path = runtime_root / "full_materialization_certification.json"
        conformance_path = runtime_root / "full_materialization_conformance.json"
        recovery_final = {
            **recovery_pre,
            "status": final_status,
            "finished_at_utc": utc_text(),
            "elapsed_seconds": elapsed,
            "exit_code": 0 if final_status == "PASS" else 1,
            "completed_shards": completed,
            "failed_shards": failed,
            "active_shards_at_supervisor_exit": [
                {
                    "shard_index": index,
                    "run_id": state["shard"]["run_id"],
                    "pid": state["pid"],
                    "mode": state["mode"],
                    "alive": process_identity_alive(state),
                }
                for index, state in sorted(active.items())
            ],
            "failure_reason": final_reason,
            "resource_peaks": {
                "process_tree_rss_gib": peak_tree_rss_gib,
                "process_tree_private_gib": peak_tree_private_gib,
                "system_memory_percent": peak_memory_percent,
                "pagefile_used_gib": peak_pagefile_used_gib,
            },
            "important_outputs": {
                "certification": str(certification_path) if certification_path.exists() else None,
                "certification_sha256": original.sha256_file(certification_path)
                if certification_path.exists()
                else None,
                "conformance": str(conformance_path) if conformance_path.exists() else None,
                "conformance_sha256": original.sha256_file(conformance_path)
                if conformance_path.exists()
                else None,
            },
            "resume_instructions": preflight["power_loss_resume_command"],
            "canonical_promotion_authorized": False,
        }
        try:
            atomic_json(recovery_final_path, recovery_final)
            append_jsonl(
                recovery_events,
                {
                    "event": "RECOVERY_SUPERVISOR_FINISHED",
                    "observed_at_utc": utc_text(),
                    "attempt_id": attempt_id,
                    "status": final_status,
                    "active_pids": [int(state["pid"]) for state in active.values()],
                },
            )
            if final_status == "PASS":
                global_final = {
                    **original_pre,
                    "status": "PASS",
                    "finished_at_utc": utc_text(),
                    "elapsed_seconds": elapsed,
                    "exit_code": 0,
                    "recovered_by": str(SCRIPT_PATH),
                    "recovery_script_sha256": original.sha256_file(SCRIPT_PATH),
                    "recovery_attempt_id": attempt_id,
                    "recovery_manifest": str(recovery_final_path),
                    "completed_shards": completed,
                    "failed_shards": [],
                    "failure_reason": None,
                    "important_outputs": recovery_final["important_outputs"],
                    "resume_instructions": preflight["power_loss_resume_command"],
                    "canonical_promotion_authorized": False,
                }
                atomic_json(root_final_path, global_final)
            block_done, current_items = aggregate_progress(
                runtime_root, plan["shards"]
            )
            final_heartbeat = {
                "run_id": plan["run_id"],
                "recovery_attempt_id": attempt_id,
                "supervisor_role": "RECOVERY_ADOPTION_SUPERVISOR",
                "observed_at_utc": utc_text(),
                "status": final_status,
                "stage": "FINAL",
                "elapsed_seconds": elapsed,
                "wrapper_pid": os.getpid(),
                "wrapper_pid_alive": True,
                "active_child_pids": [int(state["pid"]) for state in active.values()],
                "current_item": ",".join(current_items[:2]) or None,
                "current_index": block_done,
                "total_count": 240,
                "completed_blocks": block_done,
                "failed_shards": len(failed),
                "active_worker_count": len(active),
                "recovery_manifest": str(recovery_final_path),
                "power_loss_resume_command": preflight["power_loss_resume_command"],
            }
            atomic_json(root_heartbeat_path, final_heartbeat)
            append_jsonl(root_heartbeat_history, final_heartbeat)
            final_pid = {
                "run_id": plan["run_id"],
                "recovery_attempt_id": attempt_id,
                "wrapper_pid": os.getpid(),
                "children": final_heartbeat["active_child_pids"],
                "stage": "FINAL",
                "expected_alive": False,
            }
            atomic_json(recovery_pid_path, final_pid)
            atomic_json(root_pid_path, final_pid)
        except OSError as exc:
            safe_log(recovery_log, f"FINAL_TELEMETRY_DEGRADED {type(exc).__name__}: {exc}")
    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
