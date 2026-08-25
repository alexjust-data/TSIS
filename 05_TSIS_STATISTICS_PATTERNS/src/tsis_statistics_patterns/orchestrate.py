from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo_root, check=False, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _git_porcelain(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.rstrip("\r\n")


def _porcelain_paths(porcelain: str) -> list[str]:
    paths: list[str] = []
    for entry in porcelain.splitlines():
        path = entry[3:].strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        paths.append(path.strip('"'))
    return paths


def _git_state(repo_root: Path) -> dict[str, Any]:
    porcelain = _git_porcelain(repo_root)
    entries = porcelain.splitlines() if porcelain else []
    return {
        "branch": _git(repo_root, "branch", "--show-current"),
        "commit": _git(repo_root, "rev-parse", "HEAD"),
        "dirty": bool(entries),
        "dirty_path_count": len(entries),
        "dirty_entries": entries,
        "dirty_paths": _porcelain_paths(porcelain),
        "dirty_porcelain_sha256": (
            hashlib.sha256(porcelain.encode("utf-8")).hexdigest()
            if porcelain else None
        ),
    }


def _command(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", module, *args]


class RunTelemetry:
    def __init__(self, run_root: Path, run_id: str, total_shards: int) -> None:
        self.run_root = run_root
        self.run_id = run_id
        self.total_shards = total_shards
        self.started_monotonic = time.monotonic()
        self.started_at = _utc_now()
        self.stage = "starting"
        self.status = "running"
        self.completed_shards = 0
        self.failed_shards: list[int] = []
        self.active_processes: dict[str, int] = {}
        self.last_error: str | None = None
        self._state_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.log_path = run_root / "logs" / "orchestrator.log"

    def log(self, message: str) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(f"[{_utc_now()}] {message}\n")

    def _payload(self) -> dict[str, Any]:
        with self._state_lock:
            stage = self.stage
            status = self.status
            completed = self.completed_shards
            failed = list(self.failed_shards)
            active = dict(self.active_processes)
            last_error = self.last_error
        log_files = list((self.run_root / "logs").glob("*.log"))
        log_size = sum(path.stat().st_size for path in log_files if path.exists())
        latest_write = max(
            (path.stat().st_mtime for path in log_files if path.exists()), default=None
        )
        free_gb = shutil.disk_usage(self.run_root).free / (1024 ** 3)
        percentage = 100.0 * completed / self.total_shards if self.total_shards else None
        return {
            "run_id": self.run_id,
            "observed_at_utc": _utc_now(),
            "status": status,
            "stage": stage,
            "elapsed_seconds": round(time.monotonic() - self.started_monotonic, 3),
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": not self._stop_event.is_set(),
            "active_child_processes": [
                {"label": label, "pid": pid, "expected_alive": True}
                for label, pid in sorted(active.items())
            ],
            "process_count": 1 + len(active),
            "current_index": completed,
            "total_count": self.total_shards,
            "percentage": percentage,
            "completed_shards": completed,
            "failed_shards": failed,
            "output_root": str(self.run_root.resolve()),
            "log_path": str(self.log_path.resolve()),
            "log_size": log_size,
            "log_last_write_utc": (
                datetime.fromtimestamp(latest_write, timezone.utc).isoformat()
                if latest_write is not None else None
            ),
            "output_free_gb": round(free_gb, 3),
            "cpu_percent": None,
            "io_read_Bps": None,
            "io_write_Bps": None,
            "last_error": last_error,
        }

    def heartbeat(self) -> None:
        payload = self._payload()
        with self._write_lock:
            _atomic_json(self.run_root / "heartbeat_latest.json", payload)
            _append_jsonl(self.run_root / "heartbeat.jsonl", payload)
            _atomic_json(
                self.run_root / "pid_manifest.json",
                {
                    "run_id": self.run_id,
                    "wrapper_pid": os.getpid(),
                    "wrapper_process_name": "python",
                    "started_at_utc": self.started_at,
                    "stage": payload["stage"],
                    "expected_alive": payload["status"] == "running",
                    "children": payload["active_child_processes"],
                },
            )

    def start(self) -> None:
        self.heartbeat()
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()

    def _heartbeat_loop(self) -> None:
        while not self._stop_event.wait(30.0):
            self.heartbeat()

    def set_stage(self, stage: str) -> None:
        with self._state_lock:
            self.stage = stage
        self.log(f"stage={stage}")
        self.heartbeat()

    def child_started(self, label: str, pid: int) -> None:
        with self._state_lock:
            self.active_processes[label] = pid
        self.log(f"child_started label={label} pid={pid}")
        self.heartbeat()

    def child_finished(self, label: str, exit_code: int) -> None:
        with self._state_lock:
            self.active_processes.pop(label, None)
        self.log(f"child_finished label={label} exit_code={exit_code}")
        self.heartbeat()

    def shard_finished(self, shard_index: int, exit_code: int) -> None:
        with self._state_lock:
            self.completed_shards += 1
            if exit_code != 0:
                self.failed_shards.append(shard_index)
        self.heartbeat()

    def finish(self, status: str, stage: str, error: str | None = None) -> None:
        with self._state_lock:
            self.status = status
            self.stage = stage
            self.last_error = error
            self.active_processes.clear()
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self.heartbeat()
        self.log(f"finished status={status} stage={stage} error={error}")


def _run_logged(
    command: list[str], log_path: Path, env: dict[str, str], telemetry: RunTelemetry,
    label: str,
) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
        telemetry.child_started(label, process.pid)
        try:
            return process.wait()
        finally:
            telemetry.child_finished(label, process.returncode if process.returncode is not None else -1)


def orchestrate(
    config_path: Path,
    run_root: Path,
    mode: str,
    workers: int,
    limit_tickers_per_shard: int | None,
) -> int:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    shard_count = int(config["sharding"]["count"])
    repo_root = Path(__file__).resolve().parents[3]
    src_root = Path(__file__).resolve().parents[1]
    script_path = Path(__file__).resolve()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root) + os.pathsep + env.get("PYTHONPATH", "")
    run_root.mkdir(parents=True, exist_ok=False)
    run_id = run_root.name
    monitor_script = repo_root / "05_TSIS_STATISTICS_PATTERNS" / "scripts" / "monitor_atlas_run.py"
    monitor_command = (
        f'python "{monitor_script}" --run-root "{run_root}" --watch --compact'
    )
    stop_command = (
        f"Stop-Process -Id ((Get-Content -LiteralPath '{run_root / 'pid_manifest.json'}' "
        "-Raw | ConvertFrom-Json).wrapper_pid)"
    )
    git = _git_state(repo_root)
    created_at = _utc_now()
    pre_manifest = {
        "run_id": run_id,
        "status": "running",
        "created_at_utc": created_at,
        "script_path": str(script_path),
        "script_sha256": _sha256(script_path),
        "command_line": subprocess.list2cmdline(sys.argv),
        "cwd": str(Path.cwd()),
        "host": platform.node(),
        "user": getpass.getuser(),
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "python": sys.version,
        "mode": mode,
        "dry_run": False,
        "config_path": str(config_path.resolve()),
        "config_sha256": _sha256(config_path),
        "code_commit": git["commit"],
        "git": git,
        "input_roots": {
            "raw": config["data"]["raw_root"],
            "activity": config["data"]["universe_activity_path"],
        },
        "output_root": str(run_root.resolve()),
        "log_root": str((run_root / "logs").resolve()),
        "manifest_paths": {
            "pre": str((run_root / "pre_manifest.json").resolve()),
            "pid": str((run_root / "pid_manifest.json").resolve()),
            "heartbeat_latest": str((run_root / "heartbeat_latest.json").resolve()),
            "heartbeat_jsonl": str((run_root / "heartbeat.jsonl").resolve()),
            "operation_final": str((run_root / "operation_final_manifest.json").resolve()),
        },
        "expected_scope": {
            "shards": shard_count,
            "tickers": (
                shard_count * limit_tickers_per_shard
                if limit_tickers_per_shard is not None
                else int(config["scope"]["expected_tickers"])
            ),
            "rows_full_only": int(config["scope"]["expected_raw_rows"]),
        },
        "workers": workers,
        "limit_tickers_per_shard": limit_tickers_per_shard,
        "resume_policy": "no_resume_new_run_id_required",
        "overwrite_policy": "prohibited",
        "success_criteria": "all_shards_aggregate_terminal_certification_pass",
        "monitor_command": monitor_command,
        "stop_command": stop_command,
        "upstream_audit_manifest": config["data"]["audit_manifest_path"],
    }
    _atomic_json(run_root / "pre_manifest.json", pre_manifest)
    telemetry = RunTelemetry(run_root, run_id, shard_count)
    telemetry.start()
    for key in (
        "run_id", "mode", "input_roots", "output_root", "manifest_paths",
        "monitor_command", "stop_command", "success_criteria", "resume_policy",
    ):
        print(f"{key}={pre_manifest[key]}", flush=True)

    def finalize(exit_code: int, stage: str, error: str | None = None) -> int:
        status = "pass" if exit_code == 0 else "fail"
        telemetry.finish(status, stage, error)
        finished_at = _utc_now()
        pre_manifest["status"] = status
        pre_manifest["finished_at_utc"] = finished_at
        pre_manifest["exit_code"] = exit_code
        if error:
            pre_manifest["failure_reason"] = error
        _atomic_json(run_root / "pre_manifest.json", pre_manifest)
        operation_final = {
            "run_id": run_id,
            "status": status,
            "started_at_utc": created_at,
            "finished_at_utc": finished_at,
            "duration_seconds": round(time.monotonic() - telemetry.started_monotonic, 3),
            "exit_code": exit_code,
            "success_rule": pre_manifest["success_criteria"],
            "output_root": str(run_root.resolve()),
            "important_outputs": {
                "run_manifest": str((run_root / "final" / "run_manifest.json").resolve()),
                "terminal_certification": str((run_root / "final" / "terminal_certification.json").resolve()),
            },
            "failed_shards": telemetry.failed_shards,
            "failure_reason": error,
            "resume_instruction": "use a new run_id; outputs are immutable",
            "promotion_state": "evidence_ready" if exit_code == 0 else "failed_not_promotable",
        }
        _atomic_json(run_root / "operation_final_manifest.json", operation_final)
        return exit_code

    def run_one(shard_index: int) -> tuple[int, int]:
        command = _command(
            "tsis_statistics_patterns.runner",
            "--config", str(config_path),
            "--run-root", str(run_root),
            "--shard-index", str(shard_index),
            "--shard-count", str(shard_count),
        )
        if limit_tickers_per_shard is not None:
            command += ["--limit-tickers", str(limit_tickers_per_shard)]
        code = _run_logged(
            command, run_root / "logs" / f"shard_{shard_index:02d}.log", env,
            telemetry, f"runner_shard_{shard_index:02d}",
        )
        if code == 0:
            cert = _command(
                "tsis_statistics_patterns.certify",
                "--shard-root", str(run_root / f"shard={shard_index:02d}"),
            )
            code = _run_logged(
                cert, run_root / "logs" / f"certify_{shard_index:02d}.log", env,
                telemetry, f"certify_shard_{shard_index:02d}",
            )
        telemetry.shard_finished(shard_index, code)
        return shard_index, code

    try:
        telemetry.set_stage("materialize_shards")
        failures: list[int] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(run_one, index) for index in range(shard_count)]
            for future in as_completed(futures):
                shard_index, code = future.result()
                if code != 0:
                    failures.append(shard_index)
        if failures:
            return finalize(1, "materialize_shards_failed", f"failed_shards={sorted(failures)}")

        telemetry.set_stage("aggregate")
        aggregate = _command(
            "tsis_statistics_patterns.aggregate",
            "--run-root", str(run_root),
            "--config", str(config_path),
        )
        aggregate_code = _run_logged(
            aggregate, run_root / "logs" / "aggregate.log", env, telemetry, "aggregate"
        )
        if aggregate_code != 0:
            return finalize(1, "aggregate_failed", "aggregate exit code nonzero")

        telemetry.set_stage("terminal_certify")
        terminal = _command(
            "tsis_statistics_patterns.terminal_certify",
            "--run-root", str(run_root),
            "--config", str(config_path),
            "--mode", mode,
        )
        terminal_code = _run_logged(
            terminal, run_root / "logs" / "terminal_certify.log", env,
            telemetry, "terminal_certify",
        )
        return finalize(
            terminal_code,
            "complete" if terminal_code == 0 else "terminal_certification_failed",
            None if terminal_code == 0 else "terminal certification exit code nonzero",
        )
    except Exception as exc:
        telemetry.log(f"unhandled_exception={type(exc).__name__}: {exc}")
        return finalize(1, "unhandled_exception", f"{type(exc).__name__}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Production-equivalent Atlas orchestrator")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("probe", "full"), required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--limit-tickers-per-shard", type=int)
    args = parser.parse_args()
    return orchestrate(
        args.config.resolve(),
        args.run_root.resolve(),
        args.mode,
        args.workers,
        args.limit_tickers_per_shard,
    )


if __name__ == "__main__":
    raise SystemExit(main())
