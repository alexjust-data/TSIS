"""Governed runner for independent Trading Activity percentile replay."""

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
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import psutil
import pyarrow.parquet as pq

from trading_activity_binding_a_percentile_replay_oracle import (
    ORACLE_ID,
    audit_target_session,
    load_history_matrix,
)


SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
ORACLE_PATH = SCRIPT_DIR / "trading_activity_binding_a_percentile_replay_oracle.py"
MONITOR_PATH = SCRIPT_DIR / "monitor_trading_activity_binding_a_percentile_replay.ps1"
PLAN_SCHEMA = "trading_activity_binding_a_percentile_replay_plan_v0_1"
HASH_CHUNK_BYTES = 8 * 1024 * 1024


def utc_text() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    error: OSError | None = None
    for attempt in range(8):
        try:
            os.replace(temporary, path)
            return
        except PermissionError as exc:
            error = exc
            time.sleep(0.025 * (attempt + 1))
    temporary.unlink(missing_ok=True)
    if error is not None:
        raise error


def append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(payload), default=str) + "\n")
        handle.flush()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def git_value(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=SCRIPT_DIR.parents[1], capture_output=True,
        text=True, check=False,
    )
    return result.stdout.strip() or None


def verify_plan(plan: Mapping[str, Any], plan_path: Path) -> None:
    if plan.get("plan_schema_version") != PLAN_SCHEMA:
        raise ValueError("Unsupported replay plan schema")
    mode = plan.get("mode")
    if mode == "PROBE":
        if plan.get("artifact_status") != "PREREGISTERED_PROBE_PREPARED_FOR_HUMAN_LAUNCH":
            raise ValueError("Probe plan is not prepared for human launch")
    elif mode == "FULL":
        if plan.get("artifact_status") != "PREREGISTERED_FULL_HUMAN_AUTHORIZED_AFTER_PROBE_PASS":
            raise ValueError("FULL replay is not authorized; a prepared scope is not executable")
        if not str(plan.get("human_authorization", "")).startswith("AUTHORIZED_BY_"):
            raise ValueError("FULL replay lacks explicit human authorization")
        probe = Path(str(plan.get("probe_final_manifest", "")))
        if not probe.is_file() or read_json(probe).get("status") != "PASS":
            raise ValueError("FULL replay requires a bound PASS probe final manifest")
        if sha256_file(probe) != plan.get("probe_final_manifest_sha256"):
            raise ValueError("Bound probe final manifest hash mismatch")
    else:
        raise ValueError(f"Unsupported replay mode: {mode}")
    if plan.get("workers") != 1:
        raise ValueError("v0.1 permits exactly one worker until measured probe evidence exists")
    if plan.get("exact_match_required") is not True or int(plan.get("mismatch_tolerance", -1)) != 0:
        raise ValueError("Replay must remain exact and zero-tolerance")
    if plan.get("canonical_promotion_authorized") is not False:
        raise ValueError("Replay cannot authorize canonical promotion")
    static = {
        SCRIPT_PATH: plan["runner_sha256"],
        ORACLE_PATH: plan["oracle_sha256"],
        MONITOR_PATH: plan["monitor_sha256"],
        Path(plan["source_reference_manifest"]): plan["source_reference_manifest_sha256"],
        Path(plan["source_final_manifest"]): plan["source_final_manifest_sha256"],
        Path(plan["specification_path"]): plan["specification_sha256"],
    }
    for path, expected in static.items():
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"Frozen static input mismatch: {path}")
    if not plan_path.is_file():
        raise FileNotFoundError(plan_path)


def active_duplicates(run_root: Path) -> list[int]:
    needle = normalized(run_root)
    matches = []
    for process in psutil.process_iter(["pid", "cmdline"]):
        if process.pid == os.getpid():
            continue
        try:
            command = " ".join(process.info.get("cmdline") or [])
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
        if SCRIPT_PATH.name in command and needle in normalized(command):
            matches.append(process.pid)
    return matches


def history_inventory(block: Mapping[str, Any]) -> list[dict[str, Any]]:
    index_path = Path(block["output_hash_index"])
    if sha256_file(index_path) != block["output_hash_index_sha256"]:
        raise AssertionError(f"Output hash index mismatch: {index_path}")
    root = normalized(Path(block["output_root"]) / "current_state")
    rows = []
    for item in pq.read_table(index_path, columns=["path", "sha256", "rows", "bytes"]).to_pylist():
        path = Path(item["path"])
        if normalized(path).startswith(root + os.sep):
            rows.append({**item, "path": str(path.resolve())})
    rows.sort(key=lambda item: item["path"])
    if len(rows) != int(block["history_partition_count"]):
        raise AssertionError(f"History partition count changed for {block['block_id']}")
    if sum(int(item["rows"]) for item in rows) != int(block["history_rows"]):
        raise AssertionError(f"History row count changed for {block['block_id']}")
    if sum(int(item["bytes"]) for item in rows) != int(block["history_bytes"]):
        raise AssertionError(f"History byte count changed for {block['block_id']}")
    return rows


def execute(plan_path: Path, resume: bool) -> int:
    plan_path = plan_path.resolve()
    plan = read_json(plan_path)
    verify_plan(plan, plan_path)
    run_root = Path(plan["run_root"]).resolve()
    runtime_root = run_root / "runtime"
    artifacts_root = run_root / "artifacts"
    block_root = artifacts_root / "blocks"
    if active_duplicates(run_root):
        raise RuntimeError("An active replay writer already targets this run root")
    pre_path = runtime_root / "pre_manifest.json"
    pid_path = runtime_root / "pid_manifest.json"
    heartbeat_path = runtime_root / "heartbeat_latest.json"
    heartbeat_history = runtime_root / "heartbeat_history.jsonl"
    log_path = runtime_root / "run.log"
    final_path = runtime_root / "final_manifest.json"
    if pre_path.exists() and not resume:
        raise FileExistsError(f"Run root already initialized; use --resume: {run_root}")
    runtime_root.mkdir(parents=True, exist_ok=True)
    block_root.mkdir(parents=True, exist_ok=True)
    plan_sha = sha256_file(plan_path)
    runner_sha = sha256_file(SCRIPT_PATH)
    oracle_sha = sha256_file(ORACLE_PATH)
    monitor_command = (
        f'& "{MONITOR_PATH}" -RunRoot "{runtime_root}" '
        "-IntervalSeconds 10 -Compact -Watch"
    )
    if pre_path.exists():
        prior_pre = read_json(pre_path)
        if prior_pre.get("plan_sha256") != plan_sha or prior_pre.get("runner_sha256") != runner_sha or prior_pre.get("oracle_sha256") != oracle_sha:
            raise ValueError("Resume identity mismatch: plan/runner/oracle changed")
    else:
        atomic_json(pre_path, {
            "run_id": plan["run_id"], "status": "starting", "created_at_utc": utc_text(),
            "script_path": str(SCRIPT_PATH), "runner_sha256": runner_sha,
            "oracle_path": str(ORACLE_PATH), "oracle_sha256": oracle_sha,
            "oracle_id": ORACLE_ID, "command_line": subprocess.list2cmdline(sys.argv),
            "cwd": os.getcwd(), "host": socket.gethostname(), "user": getpass.getuser(),
            "wrapper_pid": os.getpid(), "git_branch": git_value("branch", "--show-current"),
            "git_commit": git_value("rev-parse", "HEAD"),
            "git_dirty_state": bool(git_value("status", "--porcelain")),
            "mode": plan["mode"], "plan_path": str(plan_path), "plan_sha256": plan_sha,
            "input_roots": sorted({block["output_root"] for block in plan["blocks"]}),
            "output_root": str(run_root), "runtime_root": str(runtime_root),
            "log_path": str(log_path), "heartbeat_path": str(heartbeat_path),
            "pid_manifest_path": str(pid_path), "final_manifest_path": str(final_path),
            "expected_scope": plan["scope"], "resume_policy": plan["resume_policy"],
            "overwrite_policy": plan["overwrite_policy"], "success_criteria": plan["success_criteria"],
            "monitor_command": monitor_command, "safe_stop_file": plan["safe_stop_file"],
        })
    atomic_json(pid_path, {
        "run_id": plan["run_id"], "wrapper_pid": os.getpid(),
        "process_name": psutil.Process().name(), "started_at_utc": utc_text(),
        "stage": "PREFLIGHT", "expected_alive": True,
    })
    log_path.touch(exist_ok=True)
    print(f"run_id={plan['run_id']}", flush=True)
    print(f"mode={plan['mode']}", flush=True)
    print(f"input_roots={len(plan['blocks'])} immutable block roots", flush=True)
    print(f"output_root={run_root}", flush=True)
    print(f"pre_manifest={pre_path}", flush=True)
    print(f"heartbeat={heartbeat_path}", flush=True)
    print(f"log={log_path}", flush=True)
    print(f"pid_manifest={pid_path}", flush=True)
    print(f"monitor_command={monitor_command}", flush=True)
    print(f"success_rule={plan['success_criteria']}", flush=True)
    print(f"resume_policy={plan['resume_policy']}", flush=True)
    print(f"safe_stop_file={plan['safe_stop_file']}", flush=True)

    started = time.monotonic()
    process = psutil.Process()
    last_emit = 0.0
    last_io = process.io_counters()
    completed_blocks = 0
    completed_sessions = 0
    rows_checked = 0
    cells_checked = 0
    mismatches = 0
    current_item = "preflight"
    current_shard: int | None = None
    current_session: str | None = None
    current_stage = "PREFLIGHT"
    dynamic: dict[str, Any] = {}

    def log(message: str) -> None:
        stamped = f"[{utc_text()}] {message}"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(stamped + "\n")
        print(stamped, flush=True)

    def emit(update: Mapping[str, Any] | None = None, *, force: bool = False) -> None:
        nonlocal last_emit, last_io, current_item, current_stage, dynamic
        if update:
            dynamic.update(update)
            current_item = str(update.get("current_item", current_item))
            current_stage = str(update.get("stage", current_stage))
        now = time.monotonic()
        if not force and now - last_emit < 5:
            return
        io = process.io_counters()
        delta = max(now - last_emit, 0.001) if last_emit else 1.0
        memory = psutil.virtual_memory()
        payload = {
            "run_id": plan["run_id"], "observed_at_utc": utc_text(),
            "status": "running", "stage": current_stage,
            "elapsed_seconds": round(now - started, 3), "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(), "active_pid_alive": True,
            "current_item": current_item, "current_shard": current_shard,
            "current_session": current_session, "blocks_completed": completed_blocks,
            "blocks_total": int(plan["scope"]["block_count"]),
            "sessions_completed": completed_sessions,
            "sessions_total": int(plan["scope"]["target_session_count"]),
            "rows_checked": rows_checked, "percentile_cells_checked": cells_checked,
            "mismatch_count": mismatches,
            "process_cpu_pct": process.cpu_percent(interval=None),
            "process_tree_rss_gib": round(process.memory_info().rss / 1024**3, 3),
            "available_memory_gib": round(memory.available / 1024**3, 3),
            "io_read_bytes_per_sec": round((io.read_bytes - last_io.read_bytes) / delta, 2),
            "io_write_bytes_per_sec": round((io.write_bytes - last_io.write_bytes) / delta, 2),
            "output_drive_free_gb": round(shutil.disk_usage(run_root.anchor).free / 1024**3, 3),
            "log_path": str(log_path), "target_root": str(run_root),
            **{key: value for key, value in dynamic.items() if key not in {"stage", "current_item"}},
        }
        atomic_json(heartbeat_path, payload)
        append_jsonl(heartbeat_history, payload)
        last_io, last_emit = io, now

    try:
        prior_checkpoints: dict[str, dict[str, Any]] = {}
        if resume:
            for path in block_root.glob("*.json"):
                item = read_json(path)
                if item.get("status") == "PASS" and item.get("plan_sha256") == plan_sha and item.get("runner_sha256") == runner_sha and item.get("oracle_sha256") == oracle_sha:
                    prior_checkpoints[str(item["block_id"])] = item
        emit({"stage": "PREFLIGHT", "current_item": "validate immutable block identities"}, force=True)
        results: list[dict[str, Any]] = []
        for block_ordinal, block in enumerate(plan["blocks"], start=1):
            block_id = str(block["block_id"])
            safe_id = block_id.replace(":", "_")
            checkpoint_path = block_root / f"{safe_id}.json"
            current_shard = int(block["shard_index"])
            current_item = block_id
            prior = prior_checkpoints.get(block_id)
            if prior is not None and prior.get("block_binding_sha256") == hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest():
                results.append(prior)
                completed_blocks += 1
                completed_sessions += int(prior["session_count"])
                rows_checked += int(prior["baseline_rows_checked"])
                cells_checked += int(prior["percentile_cells_checked"])
                emit({"stage": "RESUME_REUSE", "current_item": block_id}, force=True)
                continue
            if Path(plan["safe_stop_file"]).is_file():
                raise InterruptedError("Safe stop requested")
            for path_key, hash_key in (
                ("block_final_manifest", "block_final_sha256"),
                ("lineage_manifest", "lineage_manifest_sha256"),
            ):
                if sha256_file(Path(block[path_key])) != block[hash_key]:
                    raise AssertionError(f"Frozen block identity mismatch: {block[path_key]}")
            inventory = history_inventory(block)
            verified_paths: set[str] = set()
            for file_ordinal, item in enumerate(inventory, start=1):
                path = Path(item["path"])
                emit({
                    "stage": "VERIFY_HISTORY_HASHES", "current_item": str(path),
                    "history_partitions_verified": file_ordinal,
                    "history_partitions_total": len(inventory),
                    "block_ordinal": block_ordinal,
                })
                if sha256_file(path) != item["sha256"]:
                    raise AssertionError(f"History partition hash mismatch: {path}")
                verified_paths.add(normalized(path))
            history = load_history_matrix(
                [Path(item["path"]) for item in inventory], progress=emit
            )
            session_results = []
            for target in block["targets"]:
                if Path(plan["safe_stop_file"]).is_file():
                    raise InterruptedError("Safe stop requested")
                current_session = str(target["session_date"])
                for path_key, hash_key in (("current_path", "current_sha256"), ("baseline_path", "baseline_sha256")):
                    path = Path(target[path_key])
                    if path_key == "current_path" and normalized(path) in verified_paths:
                        continue
                    if sha256_file(path) != target[hash_key]:
                        raise AssertionError(f"Target partition hash mismatch: {path}")
                emit({"stage": "REPLAY_PERCENTILES", "current_item": f"{block['ticker']}:{current_session}"}, force=True)
                session_result = audit_target_session(
                    history, current_path=Path(target["current_path"]),
                    baseline_path=Path(target["baseline_path"]), progress=emit,
                )
                session_result.update({
                    "block_id": block_id, "block_run_id": block["block_run_id"],
                    "shard_index": current_shard, "ticker": block["ticker"],
                    "is_early_close": bool(target["is_early_close"]),
                })
                session_results.append(session_result)
                completed_sessions += 1
                rows_checked += int(session_result["baseline_rows"])
                cells_checked += int(session_result["percentile_cells_checked"])
                mismatches += int(session_result["mismatch_count"])
                log(f"SESSION: {block['ticker']} {current_session} status={session_result['status']} rows={session_result['baseline_rows']} mismatches={session_result['mismatch_count']}")
                if session_result["status"] != "PASS":
                    raise AssertionError(f"Independent percentile replay mismatch in {block_id}:{current_session}")
            result = {
                "status": "PASS", "block_id": block_id,
                "block_run_id": block["block_run_id"], "shard_index": current_shard,
                "ticker": block["ticker"], "session_count": len(session_results),
                "history_partition_count": history.source_partition_count,
                "history_rows": history.row_count,
                "baseline_rows_checked": sum(item["baseline_rows"] for item in session_results),
                "percentile_cells_checked": sum(item["percentile_cells_checked"] for item in session_results),
                "mismatch_count": 0, "sessions": session_results,
                "block_binding_sha256": hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest(),
                "plan_sha256": plan_sha, "runner_sha256": runner_sha,
                "oracle_sha256": oracle_sha, "completed_at_utc": utc_text(),
            }
            atomic_json(checkpoint_path, result)
            results.append(result)
            completed_blocks += 1
            current_session = None
            log(f"BLOCK: {completed_blocks}/{plan['scope']['block_count']} {block_id} PASS")
            emit({"stage": "BLOCK_COMPLETE", "current_item": block_id}, force=True)
            del history
        final = {
            "run_id": plan["run_id"], "status": "PASS", "mode": plan["mode"],
            "started_at_utc": read_json(pre_path)["created_at_utc"],
            "completed_at_utc": utc_text(), "elapsed_seconds": round(time.monotonic() - started, 3),
            "blocks_completed": completed_blocks, "sessions_completed": completed_sessions,
            "baseline_rows_checked": rows_checked, "percentile_cells_checked": cells_checked,
            "mismatch_count": mismatches, "exact_match": True, "null_mask_exact": True,
            "oracle_id": ORACLE_ID, "plan_path": str(plan_path), "plan_sha256": plan_sha,
            "runner_sha256": runner_sha, "oracle_sha256": oracle_sha,
            "block_checkpoint_count": len(results),
            "checkpoint_manifest_sha256s": {item["block_id"]: sha256_file(block_root / f"{item['block_id'].replace(':', '_')}.json") for item in results},
            "canonical_promotion_authorized": False,
            "next_gate": "HUMAN_REVIEW_AND_FULL_AUTHORIZATION" if plan["mode"] == "PROBE" else "UPDATE_SCIENTIFIC_EVIDENCE_VERDICT",
            "resume_instructions": "NOT_REQUIRED_TERMINAL_PASS",
        }
        atomic_json(final_path, final)
        terminal = {
            "run_id": plan["run_id"], "observed_at_utc": utc_text(),
            "status": "completed", "stage": "FINAL", "elapsed_seconds": final["elapsed_seconds"],
            "wrapper_pid": os.getpid(), "active_pid_alive": False,
            "current_item": "complete", "blocks_completed": completed_blocks,
            "blocks_total": plan["scope"]["block_count"],
            "sessions_completed": completed_sessions, "sessions_total": plan["scope"]["target_session_count"],
            "rows_checked": rows_checked, "percentile_cells_checked": cells_checked,
            "mismatch_count": mismatches, "final_manifest": str(final_path), "log_path": str(log_path),
        }
        atomic_json(heartbeat_path, terminal); append_jsonl(heartbeat_history, terminal)
        atomic_json(pid_path, {"run_id": plan["run_id"], "wrapper_pid": os.getpid(), "completed_at_utc": utc_text(), "stage": "FINAL", "expected_alive": False})
        log("FINAL: PASS")
        return 0
    except BaseException as exc:
        interrupted = isinstance(exc, (KeyboardInterrupt, InterruptedError))
        status = "INTERRUPTED" if interrupted else "FAILED"
        failure = {
            "run_id": plan["run_id"], "status": status, "mode": plan["mode"],
            "failed_at_utc": utc_text(), "elapsed_seconds": round(time.monotonic() - started, 3),
            "failure_type": type(exc).__name__, "failure_reason": str(exc),
            "traceback": traceback.format_exc(), "blocks_completed": completed_blocks,
            "sessions_completed": completed_sessions, "baseline_rows_checked": rows_checked,
            "percentile_cells_checked": cells_checked, "mismatch_count": mismatches,
            "plan_sha256": plan_sha, "runner_sha256": runner_sha, "oracle_sha256": oracle_sha,
            "resume_instructions": f'python "{SCRIPT_PATH}" --plan "{plan_path}" --resume',
            "canonical_promotion_authorized": False,
        }
        atomic_json(final_path, failure)
        terminal = {
            "run_id": plan["run_id"], "observed_at_utc": utc_text(),
            "status": "interrupted" if interrupted else "failed", "stage": "FINAL",
            "elapsed_seconds": failure["elapsed_seconds"], "wrapper_pid": os.getpid(),
            "active_pid_alive": False, "current_item": current_item,
            "blocks_completed": completed_blocks, "blocks_total": plan["scope"]["block_count"],
            "sessions_completed": completed_sessions, "sessions_total": plan["scope"]["target_session_count"],
            "rows_checked": rows_checked, "percentile_cells_checked": cells_checked,
            "mismatch_count": mismatches, "last_error": str(exc),
            "final_manifest": str(final_path), "log_path": str(log_path),
        }
        atomic_json(heartbeat_path, terminal); append_jsonl(heartbeat_history, terminal)
        atomic_json(pid_path, {"run_id": plan["run_id"], "wrapper_pid": os.getpid(), "completed_at_utc": utc_text(), "stage": "FINAL", "expected_alive": False})
        log(f"FINAL: {status}: {exc}")
        return 130 if interrupted else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    return execute(args.plan, args.resume)


if __name__ == "__main__":
    raise SystemExit(main())

