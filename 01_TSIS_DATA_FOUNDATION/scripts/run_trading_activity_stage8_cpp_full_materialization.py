"""Run the authorized 240-block TA-3 Binding A materialization with C++."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil
from trading_activity_binding_a_baseline_engine import resolve_stage8_engine

SCRIPT_DIR = Path(__file__).resolve().parent
COORDINATOR = SCRIPT_DIR / "run_trading_activity_ta3_binding_a.py"
CONFORMANCE_AUDIT = SCRIPT_DIR / "audit_trading_activity_ta3_binding_a_conformance.py"
MONITOR = SCRIPT_DIR / "monitor_long_running_operation.ps1"
EXPECTED_SCHEMA = "trading_activity_stage8_cpp_full_materialization_v0_1"


def utc_text() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def git_value(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=SCRIPT_DIR.parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    value = result.stdout.strip()
    return value or None


def load_plan(path: Path) -> dict[str, Any]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("plan_schema_version") != EXPECTED_SCHEMA:
        raise ValueError("Unsupported full-materialization plan")
    if plan.get("artifact_status") != "PREREGISTERED_AUTHORIZED_NOT_EXECUTED":
        raise ValueError("Plan is not preregistered and authorized")
    if plan.get("human_authorization") != "AUTHORIZED_2026-08-11":
        raise ValueError("Explicit human authorization is missing")
    if plan.get("broad_materialization_authorized") is not True:
        raise ValueError("Broad materialization is not authorized by the plan")
    shards = plan.get("shards", [])
    if len(shards) != 4 or sorted(int(s["shard_index"]) for s in shards) != [0, 1, 2, 3]:
        raise ValueError("Exactly shards 0,1,2,3 are required")
    if sum(int(s["expected_block_count"]) for s in shards) != 240:
        raise ValueError("The plan must cover exactly 240 blocks")
    return plan


def command_for(plan: dict[str, Any], shard: dict[str, Any], resume: bool) -> list[str]:
    command = [
        sys.executable,
        str(COORDINATOR),
        "--sample-manifest",
        str(Path(plan["sample_manifest"]).resolve()),
        "--base-config",
        str(Path(plan["base_config"]).resolve()),
        "--run-id",
        str(shard["run_id"]),
        "--output-root",
        str(Path(plan["output_root"]).resolve()),
        "--runtime-root",
        str(Path(plan["runtime_root"]).resolve()),
        "--pointer-root",
        str(Path(plan["pointer_root"]).resolve()),
        "--shard-index",
        str(shard["shard_index"]),
        "--shard-count",
        "4",
        "--stage8-engine",
        "cpp",
        "--expected-stage8-engine-fingerprint",
        str(plan["expected_stage8_engine_fingerprint"]),
    ]
    if resume:
        command.append("--resume")
    return command


def active_duplicate(plan: dict[str, Any]) -> list[dict[str, Any]]:
    matches = []
    needle = str(plan["run_id"])
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        if process.pid == os.getpid():
            continue
        try:
            command = " ".join(process.info.get("cmdline") or [])
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
        if needle in command or str(plan["runtime_root"]) in command:
            matches.append({"pid": process.pid, "name": process.info.get("name"), "command": command})
    return matches


def validate_static_preflight(plan: dict[str, Any], engine: dict[str, Any]) -> dict[str, Any]:
    if sha256_file(Path(__file__).resolve()) != plan["runner_sha256"]:
        raise ValueError("Full-materialization runner hash differs from plan")
    if engine["engine_fingerprint_sha256"] != plan["expected_stage8_engine_fingerprint"]:
        raise ValueError("C++ engine fingerprint differs from plan")
    code_paths = {
        "ta3_coordinator_sha256": COORDINATOR,
        "multisession_runner_sha256": SCRIPT_DIR / "run_trading_activity_binding_a_multisession_pilot.py",
        "conformance_audit_sha256": CONFORMANCE_AUDIT,
    }
    for key, path in code_paths.items():
        if sha256_file(path) != plan["code_fingerprints"][key]:
            raise ValueError(f"Code hash mismatch for {path}")
    for key, hash_key in (("sample_manifest", "sample_manifest_sha256"), ("base_config", "base_config_sha256")):
        path = Path(plan[key]).resolve()
        if not path.is_file() or sha256_file(path) != plan[hash_key]:
            raise ValueError(f"Input hash mismatch: {path}")
    duplicates = active_duplicate(plan)
    if duplicates:
        raise RuntimeError(f"Duplicate target process detected: {duplicates}")
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    free_gib = shutil.disk_usage(Path(plan["output_root"]).anchor).free / 1024**3
    if free_gib < float(plan["minimum_free_space_gib"]):
        raise ValueError(f"Insufficient D free space: {free_gib:.2f} GiB")
    if memory.available / 1024**3 < float(plan["minimum_initial_available_memory_gib"]):
        raise ValueError("Insufficient available RAM for even one worker")
    return {
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "total_memory_gib": memory.total / 1024**3,
        "available_memory_gib": memory.available / 1024**3,
        "memory_percent": memory.percent,
        "pagefile_used_gib": swap.used / 1024**3,
        "output_free_gib": free_gib,
    }


def validate_roots(plan: dict[str, Any], plan_path: Path, engine: dict[str, Any], resume: bool) -> None:
    roots = [Path(plan[key]).resolve() for key in ("output_root", "runtime_root", "pointer_root")]
    if not resume:
        existing = [str(path) for path in roots if path.exists()]
        if existing:
            raise FileExistsError(f"Fresh materialization roots already exist: {existing}")
        return
    if not all(path.exists() for path in roots):
        raise FileNotFoundError("Resume requires all three existing roots")
    pre_path = Path(plan["runtime_root"]).resolve() / "pre_manifest.json"
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    if pre.get("plan_sha256") != sha256_file(plan_path):
        raise ValueError("Resume plan hash differs from original pre-manifest")
    if pre.get("stage8_engine", {}).get("engine_fingerprint_sha256") != engine["engine_fingerprint_sha256"]:
        raise ValueError("Resume engine fingerprint differs from original run")


def process_tree_metrics(root_pids: list[int]) -> dict[str, float]:
    processes: dict[int, psutil.Process] = {}
    for pid in root_pids:
        try:
            root = psutil.Process(pid)
            processes[root.pid] = root
            for child in root.children(recursive=True):
                processes[child.pid] = child
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    rss = private = read_bytes = write_bytes = cpu_seconds = 0
    for process in processes.values():
        try:
            memory = process.memory_info()
            rss += memory.rss
            private += getattr(memory, "private", memory.rss)
            io = process.io_counters()
            read_bytes += io.read_bytes
            write_bytes += io.write_bytes
            cpu = process.cpu_times()
            cpu_seconds += cpu.user + cpu.system
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return {
        "process_count": float(len(processes)),
        "rss_bytes": float(rss),
        "private_bytes": float(private),
        "io_read_bytes": float(read_bytes),
        "io_write_bytes": float(write_bytes),
        "cpu_seconds": float(cpu_seconds),
    }


def completed_progress(runtime_root: Path, shards: list[dict[str, Any]]) -> tuple[int, list[str]]:
    completed = 0
    items = []
    for shard in shards:
        root = runtime_root / str(shard["run_id"])
        heartbeat_path = root / "heartbeat_latest.json"
        final_path = root / "final_manifest.json"
        try:
            if final_path.is_file():
                final = json.loads(final_path.read_text(encoding="utf-8"))
                if final.get("final_status") == "COMPLETE":
                    completed += len(final.get("completed_blocks", []))
                    continue
            if heartbeat_path.is_file():
                heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8"))
                completed += int(heartbeat.get("completed_blocks", 0))
                if heartbeat.get("item"):
                    items.append(str(heartbeat["item"]))
        except (OSError, ValueError, TypeError):
            continue
    return completed, items


def write_stop_requests(runtime_root: Path, reason: str) -> int:
    written = 0
    for block_root in runtime_root.glob("*/blocks/*"):
        if block_root.is_dir() and not (block_root / "final_manifest.json").exists():
            atomic_json(block_root / "stop_requested.json", {"requested_at_utc": utc_text(), "reason": reason})
            written += 1
    return written


def conformance_passes(payload: dict[str, Any], expected_count: int) -> bool:
    if payload.get("completed_manifest_count") != expected_count:
        return False
    if payload.get("missing_output_roots"):
        return False
    lineage = payload.get("lineage_values", [])
    if len(lineage) != 1 or lineage[0].get("future_window_used") is not False:
        return False
    for family in payload.get("families", {}).values():
        if family.get("schema_variant_count") != 1:
            return False
        if family.get("missing_from_every_variant"):
            return False
        if family.get("required_metadata_missing_from_every_variant"):
            return False
    return True


def certify_full(
    plan: dict[str, Any], runtime_root: Path, output_path: Path
) -> dict[str, Any]:
    expected_fp = plan["expected_stage8_engine_fingerprint"]
    row_totals = {
        "current_state_rows": 0,
        "multiscale_rows": 0,
        "baseline_rows": 0,
    }
    block_ids: set[str] = set()
    fingerprints: set[str] = set()
    partition_count = 0
    warnings: list[dict[str, Any]] = []
    parent_results = []
    for shard in plan["shards"]:
        parent_path = runtime_root / shard["run_id"] / "final_manifest.json"
        parent = json.loads(parent_path.read_text(encoding="utf-8"))
        completed = parent.get("completed_blocks", [])
        if parent.get("final_status") != "COMPLETE":
            raise AssertionError(f"Parent is not COMPLETE: {parent_path}")
        if len(completed) != int(shard["expected_block_count"]):
            raise AssertionError(f"Unexpected block count: {parent_path}")
        parent_results.append(
            {
                "run_id": shard["run_id"],
                "completed_blocks": len(completed),
                "status": "PASS",
            }
        )
        for record in completed:
            block_run_id = str(record["block_run_id"])
            if block_run_id in block_ids:
                raise AssertionError(f"Duplicate block run id: {block_run_id}")
            block_ids.add(block_run_id)
            block_path = (
                parent_path.parent / "blocks" / block_run_id / "final_manifest.json"
            )
            block = json.loads(block_path.read_text(encoding="utf-8"))
            if block.get("status") != "COMPLETE":
                raise AssertionError(f"Block is not COMPLETE: {block_path}")
            engine = block.get("stage8_engine", {})
            fingerprint = engine.get("engine_fingerprint_sha256")
            if engine.get("engine_name") != "cpp" or fingerprint != expected_fp:
                raise AssertionError(f"Engine mismatch: {block_path}")
            fingerprints.add(str(fingerprint))
            partition_count += int(block.get("partition_count", 0))
            output_root = Path(block["output_run_root"])
            summary_path = output_root / "metadata" / "run_summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            if summary.get("run_completion") != "PASS":
                raise AssertionError(f"Run summary is not PASS: {summary_path}")
            summary_engine = summary.get("stage8_engine", {})
            if summary_engine.get("engine_fingerprint_sha256") != expected_fp:
                raise AssertionError(f"Summary engine mismatch: {summary_path}")
            if summary.get("row_counts") != summary.get("expected_row_counts"):
                raise AssertionError(f"Row count mismatch: {summary_path}")
            for key in row_totals:
                row_totals[key] += int(summary["row_counts"][key])
            if summary.get("warnings"):
                warnings.append(
                    {"run_id": block_run_id, "warnings": summary["warnings"]}
                )
    if len(block_ids) != int(plan["expected_block_count"]):
        raise AssertionError(f"Expected 240 unique blocks, got {len(block_ids)}")
    if fingerprints != {expected_fp}:
        raise AssertionError(f"Fingerprint variants: {fingerprints}")
    if row_totals != plan["expected_row_counts"]:
        raise AssertionError(
            f"Aggregate rows differ: {row_totals} != {plan['expected_row_counts']}"
        )
    if warnings:
        raise AssertionError(f"Completed blocks emitted warnings: {warnings[:3]}")
    payload = {
        "status": "PASS",
        "certification_scope": "FULL_240_BLOCK_CPP_MATERIALIZATION",
        "completed_block_count": len(block_ids),
        "stage8_engine_fingerprints": sorted(fingerprints),
        "aggregate_row_counts": row_totals,
        "partition_count": partition_count,
        "parent_results": parent_results,
        "warnings": warnings,
        "canonical_promotion_authorized": False,
    }
    atomic_json(output_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    plan = load_plan(plan_path)
    engine = resolve_stage8_engine("cpp").manifest
    resource_baseline = validate_static_preflight(plan, engine)
    validate_roots(plan, plan_path, engine, args.resume)
    if args.preflight_only:
        print(json.dumps({
            "status": "PREFLIGHT_PASS",
            "run_id": plan["run_id"],
            "blocks": plan["expected_block_count"],
            "engine_fingerprint": engine["engine_fingerprint_sha256"],
            "resources": resource_baseline,
            "output_root": str(Path(plan["output_root"]).resolve()),
            "estimated_output_gib": plan["estimated_output_gib"],
            "max_concurrent_workers": plan["max_concurrent_workers"],
        }, indent=2))
        return 0

    runtime_root = Path(plan["runtime_root"]).resolve()
    output_root = Path(plan["output_root"]).resolve()
    pointer_root = Path(plan["pointer_root"]).resolve()
    if not args.resume:
        runtime_root.mkdir(parents=True)
        output_root.mkdir(parents=True)
        pointer_root.mkdir(parents=True)
    log_root = runtime_root / "logs"
    log_root.mkdir(exist_ok=True)
    pre_path = runtime_root / "pre_manifest.json"
    pid_path = runtime_root / "pid_manifest.json"
    heartbeat_path = runtime_root / "heartbeat_latest.json"
    heartbeat_history = runtime_root / "heartbeat_history.jsonl"
    human_log = runtime_root / "run.log"
    final_path = runtime_root / "final_manifest.json"
    monitor_command = (
        f"powershell -File {MONITOR} -RunRoot {runtime_root} "
        "-IntervalSeconds 30 -Compact -Watch"
    )
    commands = [
        {
            "shard_index": shard["shard_index"],
            "command": command_for(plan, shard, args.resume),
        }
        for shard in plan["shards"]
    ]
    premanifest = {
        "run_id": plan["run_id"],
        "status": "STARTING",
        "created_at_utc": utc_text(),
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "plan_path": str(plan_path),
        "plan_sha256": sha256_file(plan_path),
        "command_line": sys.argv,
        "cwd": str(Path.cwd()),
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "git_branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty_state": bool(git_value("status", "--porcelain")),
        "mode": "FULL_240_BLOCK_CPP_MATERIALIZATION",
        "resume": args.resume,
        "input_roots": {
            "sample_manifest": plan["sample_manifest"],
            "base_config": plan["base_config"],
        },
        "output_roots": {
            "outputs": str(output_root),
            "runtime": str(runtime_root),
            "pointers": str(pointer_root),
        },
        "log_root": str(log_root),
        "manifest_paths": {
            "pre": str(pre_path),
            "pid": str(pid_path),
            "heartbeat": str(heartbeat_path),
            "heartbeat_history": str(heartbeat_history),
            "final": str(final_path),
        },
        "expected_scope": {
            "blocks": 240,
            "shards": plan["shards"],
            "row_counts": plan["expected_row_counts"],
        },
        "resource_baseline": resource_baseline,
        "parallelism_policy": plan["parallelism_policy"],
        "resume_policy": plan["resume_policy"],
        "overwrite_policy": "NEVER",
        "success_criteria": plan["success_criteria"],
        "monitor_command": monitor_command,
        "safe_stop": f"write {{}} to {runtime_root / 'stop_requested.json'}",
        "stage8_engine": engine,
        "commands": commands,
        "materialization_execution_authorized": True,
        "canonical_promotion_authorized": False,
    }
    if args.resume:
        with (runtime_root / "resume_events.jsonl").open(
            "a", encoding="utf-8"
        ) as handle:
            handle.write(json.dumps({
                "resumed_at_utc": utc_text(),
                "command_line": sys.argv,
                "wrapper_pid": os.getpid(),
            }) + "\n")
    else:
        atomic_json(pre_path, premanifest)

    print(f"run_id={plan['run_id']}", flush=True)
    print("mode=FULL_240_BLOCK_CPP_MATERIALIZATION", flush=True)
    print(f"input_roots={premanifest['input_roots']}", flush=True)
    print(f"output_roots={premanifest['output_roots']}", flush=True)
    print(f"pre_manifest={pre_path}", flush=True)
    print(f"heartbeat={heartbeat_path}", flush=True)
    print(f"log={human_log}", flush=True)
    print(f"pid_manifest={pid_path}", flush=True)
    print(f"monitor_command={monitor_command}", flush=True)
    print(f"success_rule={plan['success_criteria']}", flush=True)
    print(f"resume_policy={plan['resume_policy']}", flush=True)

    started = time.monotonic()
    pending = list(plan["shards"])
    active: dict[int, dict[str, Any]] = {}
    completed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    stop_requested = False
    final_status = "FAILED"
    final_reason: str | None = None
    last_launch_at: float | None = None
    last_metrics_at = started
    last_metrics = process_tree_metrics([])
    peak_tree_rss_gib = 0.0
    peak_tree_private_gib = 0.0
    peak_memory_percent = resource_baseline["memory_percent"]
    peak_pagefile_used_gib = resource_baseline["pagefile_used_gib"]
    launch_deferred_reason: str | None = None

    if args.resume:
        still_pending = []
        for shard in pending:
            parent_path = runtime_root / shard["run_id"] / "final_manifest.json"
            if parent_path.is_file():
                parent = json.loads(parent_path.read_text(encoding="utf-8"))
                if (
                    parent.get("final_status") == "COMPLETE"
                    and len(parent.get("completed_blocks", []))
                    == int(shard["expected_block_count"])
                ):
                    completed.append({
                        "shard_index": shard["shard_index"],
                        "run_id": shard["run_id"],
                        "return_code": 0,
                        "resume_state": "SKIPPED_COMPLETE",
                    })
                    continue
            still_pending.append(shard)
        pending = still_pending

    def emit(stage: str, item: str | None = None) -> None:
        nonlocal last_metrics_at, last_metrics, peak_tree_rss_gib
        nonlocal peak_tree_private_gib, peak_memory_percent
        nonlocal peak_pagefile_used_gib
        now = time.monotonic()
        tree = process_tree_metrics(sorted(active))
        dt = max(now - last_metrics_at, 1e-9)
        cpu_delta = max(
            tree["cpu_seconds"] - last_metrics["cpu_seconds"], 0.0
        )
        read_delta = max(
            tree["io_read_bytes"] - last_metrics["io_read_bytes"], 0.0
        )
        write_delta = max(
            tree["io_write_bytes"] - last_metrics["io_write_bytes"], 0.0
        )
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        rss_gib = tree["rss_bytes"] / 1024**3
        private_gib = tree["private_bytes"] / 1024**3
        peak_tree_rss_gib = max(peak_tree_rss_gib, rss_gib)
        peak_tree_private_gib = max(peak_tree_private_gib, private_gib)
        peak_memory_percent = max(peak_memory_percent, memory.percent)
        peak_pagefile_used_gib = max(
            peak_pagefile_used_gib, swap.used / 1024**3
        )
        block_done, current_items = completed_progress(
            runtime_root, plan["shards"]
        )
        payload = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": "STOPPING" if stop_requested else "RUNNING",
            "stage": stage,
            "elapsed_seconds": now - started,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "active_child_pids": sorted(active),
            "current_item": item or ",".join(current_items[:2]) or None,
            "current_index": block_done,
            "total_count": 240,
            "percentage": 100.0 * block_done / 240.0,
            "completed_blocks": block_done,
            "failed_shards": len(failed),
            "active_worker_count": len(active),
            "process_tree_count": int(tree["process_count"]),
            "process_tree_rss_gib": rss_gib,
            "process_tree_private_gib": private_gib,
            "system_cpu_percent": psutil.cpu_percent(interval=None),
            "process_cpu_core_percent": 100.0 * cpu_delta / dt,
            "available_memory_gib": memory.available / 1024**3,
            "memory_percent": memory.percent,
            "pagefile_used_gib": swap.used / 1024**3,
            "io_read_Bps": read_delta / dt,
            "io_write_Bps": write_delta / dt,
            "output_root": str(output_root),
            "output_free_gib": (
                shutil.disk_usage(output_root.anchor).free / 1024**3
            ),
            "log_path": str(human_log),
            "log_size": human_log.stat().st_size if human_log.exists() else 0,
            "launch_deferred_reason": launch_deferred_reason,
        }
        atomic_json(heartbeat_path, payload)
        with heartbeat_history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
        line = (
            f"[{payload['observed_at_utc']}] status={payload['status']} "
            f"stage={stage} processes={len(active)} "
            f"elapsed_sec={payload['elapsed_seconds']:.1f} "
            f"progress={block_done}/240 item={payload['current_item']} "
            f"cpu={payload['system_cpu_percent']:.1f} rss_GB={rss_gib:.2f} "
            f"ram_free_GB={payload['available_memory_gib']:.2f} "
            f"io_read_Bps={payload['io_read_Bps']:.0f} "
            f"io_write_Bps={payload['io_write_Bps']:.0f} "
            f"output_free_GB={payload['output_free_gib']:.2f} "
            f"defer={launch_deferred_reason}\n"
        )
        with human_log.open("a", encoding="utf-8") as handle:
            handle.write(line)
        atomic_json(pid_path, {
            "run_id": plan["run_id"],
            "wrapper_pid": os.getpid(),
            "stage": stage,
            "observed_at_utc": utc_text(),
            "children": [
                {
                    "pid": pid,
                    "shard_index": state["shard"]["shard_index"],
                    "run_id": state["shard"]["run_id"],
                    "expected_alive": True,
                }
                for pid, state in active.items()
            ],
        })
        last_metrics_at = now
        last_metrics = tree

    def can_launch_additional() -> bool:
        nonlocal launch_deferred_reason
        if not active:
            return True
        now = time.monotonic()
        stagger = float(
            plan["parallelism_policy"]["additional_worker_stagger_seconds"]
        )
        if last_launch_at is not None and now - last_launch_at < stagger:
            launch_deferred_reason = "STAGGER_OBSERVATION_WINDOW"
            return False
        available_gib = psutil.virtual_memory().available / 1024**3
        active_metrics = process_tree_metrics(sorted(active))
        active_rss_gib = active_metrics["rss_bytes"] / 1024**3
        observed_per_worker = max(
            peak_tree_rss_gib / max(len(active), 1), 4.0
        )
        policy = plan["parallelism_policy"]
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
        emit("LAUNCH")
        while pending or active:
            if (runtime_root / "stop_requested.json").exists():
                stop_requested = True
                write_stop_requests(
                    runtime_root, "FULL_MATERIALIZATION_STOP_REQUESTED"
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
                command = command_for(plan, shard, args.resume)
                stdout_path = (
                    log_root / f"shard_{shard['shard_index']}.stdout.log"
                )
                stderr_path = (
                    log_root / f"shard_{shard['shard_index']}.stderr.log"
                )
                mode = "a" if args.resume else "w"
                stdout = stdout_path.open(mode, encoding="utf-8")
                stderr = stderr_path.open(mode, encoding="utf-8")
                process = subprocess.Popen(
                    command, stdout=stdout, stderr=stderr
                )
                active[process.pid] = {
                    "process": process,
                    "shard": shard,
                    "command": command,
                    "stdout": stdout,
                    "stderr": stderr,
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "started_at_utc": utc_text(),
                }
                last_launch_at = time.monotonic()
                emit("SHARD_LAUNCHED", str(shard["shard_index"]))
            if stop_requested:
                write_stop_requests(
                    runtime_root, "FULL_MATERIALIZATION_STOP_REQUESTED"
                )
            time.sleep(10)
            for pid, state in list(active.items()):
                return_code = state["process"].poll()
                if return_code is None:
                    continue
                state["stdout"].close()
                state["stderr"].close()
                record = {
                    "shard_index": state["shard"]["shard_index"],
                    "run_id": state["shard"]["run_id"],
                    "return_code": int(return_code),
                    "started_at_utc": state["started_at_utc"],
                    "finished_at_utc": utc_text(),
                    "stdout_log": str(state["stdout_path"]),
                    "stderr_log": str(state["stderr_path"]),
                }
                (completed if return_code == 0 else failed).append(record)
                del active[pid]
                emit("SHARD_FINISHED", str(record["shard_index"]))
            if failed and not active:
                pending.clear()
            emit(
                "FAIL_CLOSED_WAITING_ACTIVE_SHARDS" if failed else "RUNNING"
            )

        if stop_requested:
            final_status = "INTERRUPTED_COOPERATIVE"
            final_reason = "wrapper stop requested"
        elif failed:
            final_reason = "one or more shard coordinators failed"
        else:
            certification_path = (
                runtime_root / "full_materialization_certification.json"
            )
            conformance_path = (
                runtime_root / "full_materialization_conformance.json"
            )
            emit("CERTIFY_240_BLOCKS")
            certify_full(plan, runtime_root, certification_path)
            emit("AUDIT_240_BLOCK_SCHEMAS")
            audit = subprocess.run(
                [
                    sys.executable,
                    str(CONFORMANCE_AUDIT),
                    "--runtime-root",
                    str(runtime_root),
                    "--output",
                    str(conformance_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            (log_root / "conformance.stdout.log").write_text(
                audit.stdout, encoding="utf-8"
            )
            (log_root / "conformance.stderr.log").write_text(
                audit.stderr, encoding="utf-8"
            )
            if audit.returncode != 0:
                raise RuntimeError(
                    f"Conformance audit failed: {audit.stderr}"
                )
            conformance = json.loads(
                conformance_path.read_text(encoding="utf-8")
            )
            if not conformance_passes(conformance, 240):
                raise AssertionError(
                    "Full variable/schema conformance did not pass"
                )
            final_status = "PASS"
    except Exception as exc:
        final_status = "FAILED"
        final_reason = f"{type(exc).__name__}: {exc}"
        with human_log.open("a", encoding="utf-8") as handle:
            handle.write(traceback.format_exc())
    finally:
        elapsed = time.monotonic() - started
        certification_path = (
            runtime_root / "full_materialization_certification.json"
        )
        conformance_path = (
            runtime_root / "full_materialization_conformance.json"
        )
        final = {
            **premanifest,
            "status": final_status,
            "finished_at_utc": utc_text(),
            "elapsed_seconds": elapsed,
            "exit_code": 0 if final_status == "PASS" else 1,
            "completed_shards": completed,
            "failed_shards": failed,
            "failure_reason": final_reason,
            "resource_peaks": {
                "process_tree_rss_gib": peak_tree_rss_gib,
                "process_tree_private_gib": peak_tree_private_gib,
                "system_memory_percent": peak_memory_percent,
                "pagefile_used_gib": peak_pagefile_used_gib,
            },
            "important_outputs": {
                "certification": (
                    str(certification_path)
                    if certification_path.exists()
                    else None
                ),
                "certification_sha256": (
                    sha256_file(certification_path)
                    if certification_path.exists()
                    else None
                ),
                "conformance": (
                    str(conformance_path)
                    if conformance_path.exists()
                    else None
                ),
                "conformance_sha256": (
                    sha256_file(conformance_path)
                    if conformance_path.exists()
                    else None
                ),
            },
            "resume_instructions": (
                f"python {Path(__file__).resolve()} "
                f"--plan {plan_path} --resume"
            ),
            "canonical_promotion_authorized": False,
        }
        atomic_json(final_path, final)
        block_done, _ = completed_progress(runtime_root, plan["shards"])
        final_heartbeat = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": final_status,
            "stage": "FINAL",
            "elapsed_seconds": elapsed,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "current_index": block_done,
            "total_count": 240,
            "completed_blocks": block_done,
            "failed_shards": len(failed),
            "final_manifest": str(final_path),
        }
        atomic_json(heartbeat_path, final_heartbeat)
        with heartbeat_history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(final_heartbeat) + "\n")
        atomic_json(pid_path, {
            "run_id": plan["run_id"],
            "wrapper_pid": os.getpid(),
            "children": [],
            "stage": "FINAL",
            "expected_alive": False,
            "observed_at_utc": utc_text(),
        })
    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
