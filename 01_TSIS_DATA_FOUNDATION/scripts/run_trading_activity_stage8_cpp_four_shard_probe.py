"""Run and certify four bounded TA-3 Stage-8 C++ shard probes."""

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

from trading_activity_binding_a_baseline_engine import resolve_stage8_engine

SCRIPT_DIR = Path(__file__).resolve().parent
COORDINATOR = SCRIPT_DIR / "run_trading_activity_ta3_binding_a.py"
VALIDATOR = SCRIPT_DIR / "validate_trading_activity_binding_a_shard_probes.py"
CONFORMANCE_AUDIT = SCRIPT_DIR / "audit_trading_activity_ta3_binding_a_conformance.py"
MONITOR = SCRIPT_DIR / "monitor_long_running_operation.ps1"


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
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


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
    schema_version = plan.get("plan_schema_version", plan.get("plan_version"))
    if schema_version != "trading_activity_stage8_cpp_four_shard_probe_v0_1":
        raise ValueError("Unsupported four-shard probe plan")
    if plan.get("artifact_status") != "PREREGISTERED_NOT_EXECUTED":
        raise ValueError("Probe plan is not in preregistered state")
    if len(plan.get("shards", [])) != 4:
        raise ValueError("Exactly four shard entries are required")
    if sorted(int(item["shard_index"]) for item in plan["shards"]) != [0, 1, 2, 3]:
        raise ValueError("Shard indexes must be exactly 0,1,2,3")
    return plan


def command_for(plan: dict[str, Any], shard: dict[str, Any]) -> list[str]:
    return [
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
        "--block-limit",
        "1",
        "--shard-index",
        str(shard["shard_index"]),
        "--shard-count",
        "4",
        "--decision-seconds-limit",
        str(plan["decision_seconds_limit"]),
        "--stage8-engine",
        "cpp",
        "--expected-stage8-engine-fingerprint",
        str(plan["expected_stage8_engine_fingerprint"]),
    ]


def validate_preflight(plan: dict[str, Any], engine: dict[str, Any]) -> None:
    if sha256_file(Path(__file__).resolve()) != plan["runner_sha256"]:
        raise ValueError("Four-shard runner hash differs from preregistered plan")
    if (
        engine["engine_fingerprint_sha256"]
        != plan["expected_stage8_engine_fingerprint"]
    ):
        raise ValueError("C++ engine fingerprint differs from preregistered plan")
    code_paths = {
        "ta3_coordinator_sha256": COORDINATOR,
        "multisession_runner_sha256": SCRIPT_DIR
        / "run_trading_activity_binding_a_multisession_pilot.py",
        "four_shard_validator_sha256": VALIDATOR,
        "conformance_audit_sha256": CONFORMANCE_AUDIT,
    }
    for key, path in code_paths.items():
        if sha256_file(path) != plan["code_fingerprints"][key]:
            raise ValueError(f"Code hash mismatch for {path}")
    for key, hash_key in (
        ("sample_manifest", "sample_manifest_sha256"),
        ("base_config", "base_config_sha256"),
    ):
        path = Path(plan[key]).resolve()
        if not path.is_file() or sha256_file(path) != plan[hash_key]:
            raise ValueError(f"Input hash mismatch: {path}")
    for key in ("output_root", "runtime_root", "pointer_root"):
        path = Path(plan[key]).resolve()
        if path.exists():
            raise FileExistsError(f"Fresh probe root already exists: {path}")
    output_drive = Path(plan["output_root"]).anchor
    free_gib = shutil.disk_usage(output_drive).free / 1024**3
    if free_gib < float(plan["minimum_free_space_gib"]):
        raise ValueError(f"Insufficient output free space: {free_gib:.2f} GiB")


def write_stop_requests(runtime_root: Path, reason: str) -> int:
    written = 0
    for block_root in runtime_root.glob("*/blocks/*"):
        if block_root.is_dir() and not (block_root / "final_manifest.json").exists():
            atomic_json(
                block_root / "stop_requested.json",
                {"requested_at_utc": utc_text(), "reason": reason},
            )
            written += 1
    return written


def conformance_passes(payload: dict[str, Any]) -> bool:
    if payload.get("completed_manifest_count") != 4:
        return False
    if payload.get("missing_output_roots"):
        return False
    for family in payload.get("families", {}).values():
        if family.get("schema_variant_count") != 1:
            return False
        if family.get("missing_from_every_variant"):
            return False
        if family.get("required_metadata_missing_from_every_variant"):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    plan = load_plan(plan_path)
    engine = resolve_stage8_engine("cpp").manifest
    validate_preflight(plan, engine)

    runtime_root = Path(plan["runtime_root"]).resolve()
    output_root = Path(plan["output_root"]).resolve()
    pointer_root = Path(plan["pointer_root"]).resolve()
    runtime_root.mkdir(parents=True)
    output_root.mkdir(parents=True)
    pointer_root.mkdir(parents=True)
    log_root = runtime_root / "logs"
    log_root.mkdir()
    premanifest_path = runtime_root / "pre_manifest.json"
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
        {"shard_index": item["shard_index"], "command": command_for(plan, item)}
        for item in plan["shards"]
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
        "mode": "FOUR_SHARD_BOUNDED_PRODUCTION_EQUIVALENT_PROBE",
        "dry_run": False,
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
            "pre": str(premanifest_path),
            "pid": str(pid_path),
            "heartbeat": str(heartbeat_path),
            "heartbeat_history": str(heartbeat_history),
            "final": str(final_path),
        },
        "expected_scope": plan["shards"],
        "max_concurrent_workers": plan["max_concurrent_workers"],
        "resume_policy": "PROHIBITED_NEW_ROOT_AFTER_ANY_FAILURE",
        "overwrite_policy": "NEVER",
        "success_criteria": plan["success_criteria"],
        "monitor_command": monitor_command,
        "safe_stop": (
            f"write {{}} to {runtime_root / 'stop_requested.json'}; "
            "the wrapper propagates cooperative stop files to active block runners"
        ),
        "stage8_engine": engine,
        "commands": commands,
        "promotion_status": "NOT_AUTHORIZED",
    }
    atomic_json(premanifest_path, premanifest)

    print(f"run_id={plan['run_id']}", flush=True)
    print("mode=FOUR_SHARD_BOUNDED_PRODUCTION_EQUIVALENT_PROBE", flush=True)
    print(f"input_roots={premanifest['input_roots']}", flush=True)
    print(f"output_roots={premanifest['output_roots']}", flush=True)
    print(f"pre_manifest={premanifest_path}", flush=True)
    print(f"heartbeat={heartbeat_path}", flush=True)
    print(f"log={human_log}", flush=True)
    print(f"pid_manifest={pid_path}", flush=True)
    print(f"monitor_command={monitor_command}", flush=True)
    print(f"success_rule={plan['success_criteria']}", flush=True)
    print("resume_policy=PROHIBITED_NEW_ROOT_AFTER_ANY_FAILURE", flush=True)

    started = time.monotonic()
    pending = list(plan["shards"])
    active: dict[int, dict[str, Any]] = {}
    completed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    stop_requested = False
    final_status = "FAILED"
    final_reason: str | None = None

    def emit(stage: str, item: str | None = None) -> None:
        elapsed = time.monotonic() - started
        free_gib = shutil.disk_usage(output_root.anchor).free / 1024**3
        payload = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": "STOPPING" if stop_requested else "RUNNING",
            "stage": stage,
            "elapsed_seconds": elapsed,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "active_child_pids": sorted(active),
            "current_item": item,
            "current_index": len(completed) + len(failed),
            "total_count": 4,
            "percentage": 25.0 * (len(completed) + len(failed)),
            "completed_shards": len(completed),
            "failed_shards": len(failed),
            "output_root": str(output_root),
            "log_path": str(human_log),
            "log_size": human_log.stat().st_size if human_log.exists() else 0,
            "output_free_gib": free_gib,
        }
        atomic_json(heartbeat_path, payload)
        with heartbeat_history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
        line = (
            f"[{payload['observed_at_utc']}] status={payload['status']} "
            f"stage={stage} processes={len(active)} elapsed_sec={elapsed:.1f} "
            f"progress={len(completed) + len(failed)}/4 item={item} "
            f"output_free_GB={free_gib:.2f}\n"
        )
        with human_log.open("a", encoding="utf-8") as handle:
            handle.write(line)
        atomic_json(
            pid_path,
            {
                "run_id": plan["run_id"],
                "wrapper": {
                    "pid": os.getpid(),
                    "process_name": Path(sys.executable).name,
                    "started_at_utc": premanifest["created_at_utc"],
                    "stage": stage,
                    "expected_alive": True,
                },
                "children": [
                    {
                        "pid": pid,
                        "shard_index": state["shard"]["shard_index"],
                        "run_id": state["shard"]["run_id"],
                        "command": state["command"],
                        "expected_alive": True,
                    }
                    for pid, state in active.items()
                ],
                "observed_at_utc": utc_text(),
            },
        )

    try:
        emit("LAUNCH")
        while pending or active:
            if (runtime_root / "stop_requested.json").exists():
                stop_requested = True
                write_stop_requests(runtime_root, "FOUR_SHARD_WRAPPER_STOP_REQUESTED")
            while (
                pending
                and not stop_requested
                and not failed
                and len(active) < int(plan["max_concurrent_workers"])
            ):
                shard = pending.pop(0)
                command = command_for(plan, shard)
                stdout_path = log_root / f"shard_{shard['shard_index']}.stdout.log"
                stderr_path = log_root / f"shard_{shard['shard_index']}.stderr.log"
                stdout = stdout_path.open("w", encoding="utf-8")
                stderr = stderr_path.open("w", encoding="utf-8")
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
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
                emit("SHARD_LAUNCHED", str(shard["shard_index"]))
            if stop_requested:
                write_stop_requests(runtime_root, "FOUR_SHARD_WRAPPER_STOP_REQUESTED")
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
                    "expected_block_id": state["shard"]["expected_block_id"],
                    "return_code": int(return_code),
                    "started_at_utc": state["started_at_utc"],
                    "finished_at_utc": utc_text(),
                    "stdout_log": str(state["stdout_path"]),
                    "stderr_log": str(state["stderr_path"]),
                }
                (completed if return_code == 0 else failed).append(record)
                del active[pid]
                emit("SHARD_FINISHED", str(record["shard_index"]))
            if failed and active:
                emit("FAIL_CLOSED_WAITING_ACTIVE_SHARDS")
            if failed and not active:
                pending.clear()
            if pending or active:
                emit("RUNNING")

        if stop_requested:
            final_status = "INTERRUPTED_COOPERATIVE"
            final_reason = "wrapper stop requested"
        elif failed:
            final_status = "FAILED"
            final_reason = "one or more shard coordinators failed"
        else:
            emit("VERIFY_PARENT_MANIFESTS")
            for record in completed:
                parent_final = (
                    runtime_root / record["run_id"] / "final_manifest.json"
                )
                payload = json.loads(parent_final.read_text(encoding="utf-8"))
                if payload.get("final_status") != "COMPLETE":
                    raise AssertionError(f"Parent run not COMPLETE: {parent_final}")
                blocks = payload.get("completed_blocks", [])
                if len(blocks) != 1 or not str(blocks[0]["block_id"]).endswith(
                    record["expected_block_id"]
                ):
                    raise AssertionError(
                        f"Unexpected block selection for shard {record['shard_index']}"
                    )

            certification_path = runtime_root / "four_shard_certification.json"
            conformance_path = runtime_root / "four_shard_conformance.json"
            validator_command = [
                sys.executable,
                str(VALIDATOR),
                "--runtime-root",
                str(runtime_root),
                "--output",
                str(certification_path),
                "--required-stage8-engine",
                "cpp",
                "--expected-stage8-engine-fingerprint",
                plan["expected_stage8_engine_fingerprint"],
            ]
            emit("CERTIFY_FOUR_SHARDS")
            validator = subprocess.run(
                validator_command, text=True, capture_output=True, check=False
            )
            (log_root / "certification.stdout.log").write_text(
                validator.stdout, encoding="utf-8"
            )
            (log_root / "certification.stderr.log").write_text(
                validator.stderr, encoding="utf-8"
            )
            if validator.returncode != 0:
                raise RuntimeError(
                    f"Four-shard certification failed: {validator.stderr}"
                )
            certification = json.loads(
                certification_path.read_text(encoding="utf-8")
            )
            results_by_parent = {
                item["parent_run_id"]: item for item in certification["results"]
            }
            for shard in plan["shards"]:
                result = results_by_parent.get(shard["run_id"])
                if result is None:
                    raise AssertionError(
                        f"Missing certification result for {shard['run_id']}"
                    )
                for field in (
                    "current_state_rows",
                    "multiscale_rows",
                    "baseline_rows",
                ):
                    expected = shard[f"expected_{field}"]
                    if result[field] != expected:
                        raise AssertionError(
                            f"{shard['run_id']} {field}: {result[field]} != {expected}"
                        )

            audit_command = [
                sys.executable,
                str(CONFORMANCE_AUDIT),
                "--runtime-root",
                str(runtime_root),
                "--output",
                str(conformance_path),
            ]
            emit("AUDIT_VARIABLES")
            audit = subprocess.run(
                audit_command, text=True, capture_output=True, check=False
            )
            (log_root / "conformance.stdout.log").write_text(
                audit.stdout, encoding="utf-8"
            )
            (log_root / "conformance.stderr.log").write_text(
                audit.stderr, encoding="utf-8"
            )
            if audit.returncode != 0:
                raise RuntimeError(f"Conformance audit failed: {audit.stderr}")
            conformance = json.loads(conformance_path.read_text(encoding="utf-8"))
            if not conformance_passes(conformance):
                raise AssertionError("Variable/schema conformance did not pass")
            final_status = "PASS"
    except Exception as exc:
        final_status = "FAILED"
        final_reason = f"{type(exc).__name__}: {exc}"
        with human_log.open("a", encoding="utf-8") as handle:
            handle.write(traceback.format_exc())
    finally:
        elapsed = time.monotonic() - started
        certification_path = runtime_root / "four_shard_certification.json"
        conformance_path = runtime_root / "four_shard_conformance.json"
        final = {
            **premanifest,
            "status": final_status,
            "finished_at_utc": utc_text(),
            "elapsed_seconds": elapsed,
            "exit_code": 0 if final_status == "PASS" else 1,
            "completed_shards": completed,
            "failed_shards": failed,
            "failure_reason": final_reason,
            "important_outputs": {
                "certification": str(certification_path)
                if certification_path.exists()
                else None,
                "certification_sha256": sha256_file(certification_path)
                if certification_path.exists()
                else None,
                "conformance": str(conformance_path)
                if conformance_path.exists()
                else None,
                "conformance_sha256": sha256_file(conformance_path)
                if conformance_path.exists()
                else None,
            },
            "resume_instructions": "PROHIBITED_START_NEW_VERSIONED_ROOT",
            "promotion_status": "NOT_AUTHORIZED",
            "broad_materialization_authorized": False,
        }
        atomic_json(final_path, final)
        final_heartbeat = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": final_status,
            "stage": "FINAL",
            "elapsed_seconds": elapsed,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "current_index": len(completed) + len(failed),
            "total_count": 4,
            "completed_shards": len(completed),
            "failed_shards": len(failed),
            "final_manifest": str(final_path),
        }
        atomic_json(heartbeat_path, final_heartbeat)
        with heartbeat_history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(final_heartbeat) + "\n")
        atomic_json(
            pid_path,
            {
                "run_id": plan["run_id"],
                "wrapper_pid": os.getpid(),
                "children": [],
                "stage": "FINAL",
                "expected_alive": False,
                "observed_at_utc": utc_text(),
            },
        )
    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
