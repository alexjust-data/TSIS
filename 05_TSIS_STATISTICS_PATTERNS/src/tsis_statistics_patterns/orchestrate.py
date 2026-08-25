from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_commit(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _command(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", module, *args]


def _run_logged(command: list[str], log_path: Path, env: dict[str, str]) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env)
    return process.returncode


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
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root) + os.pathsep + env.get("PYTHONPATH", "")
    run_root.mkdir(parents=True, exist_ok=False)
    pre_manifest = {
        "status": "running",
        "mode": mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "config_path": str(config_path.resolve()),
        "config_sha256": _sha256(config_path),
        "shard_count": shard_count,
        "workers": workers,
        "limit_tickers_per_shard": limit_tickers_per_shard,
        "code_commit": _git_commit(repo_root),
        "upstream_audit_manifest": config["data"]["audit_manifest_path"],
    }
    (run_root / "pre_manifest.json").write_text(
        json.dumps(pre_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

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
        code = _run_logged(command, run_root / "logs" / f"shard_{shard_index:02d}.log", env)
        if code == 0:
            cert = _command(
                "tsis_statistics_patterns.certify",
                "--shard-root", str(run_root / f"shard={shard_index:02d}"),
            )
            code = _run_logged(cert, run_root / "logs" / f"certify_{shard_index:02d}.log", env)
        return shard_index, code

    failures: list[int] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_one, index) for index in range(shard_count)]
        for future in as_completed(futures):
            shard_index, code = future.result()
            if code != 0:
                failures.append(shard_index)
    if failures:
        pre_manifest["status"] = "fail"
        pre_manifest["failed_shards"] = sorted(failures)
        pre_manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_root / "pre_manifest.json").write_text(
            json.dumps(pre_manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        return 1

    aggregate = _command(
        "tsis_statistics_patterns.aggregate",
        "--run-root", str(run_root),
        "--config", str(config_path),
    )
    if _run_logged(aggregate, run_root / "logs" / "aggregate.log", env) != 0:
        pre_manifest["status"] = "fail"
        pre_manifest["failed_stage"] = "aggregate"
        pre_manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_root / "pre_manifest.json").write_text(
            json.dumps(pre_manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        return 1
    terminal = _command(
        "tsis_statistics_patterns.terminal_certify",
        "--run-root", str(run_root),
        "--config", str(config_path),
        "--mode", mode,
    )
    terminal_code = _run_logged(
        terminal, run_root / "logs" / "terminal_certify.log", env
    )
    pre_manifest["status"] = "pass" if terminal_code == 0 else "fail"
    pre_manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    (run_root / "pre_manifest.json").write_text(
        json.dumps(pre_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return terminal_code


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
