from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from .contracts import AtlasConfig
from .episodes import build_atlas_tables
from .features import compute_session_observables
from .io import (
    load_raw_ticker,
    load_universe_tickers,
    tickers_for_shard,
    write_table_part,
)


TABLE_NAMES = {
    "sessions": "session_observables",
    "activations": "activation_labels",
    "episodes": "episodes",
    "trajectories": "episode_trajectories",
    "events": "episode_events",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def run_shard(
    config_path: Path,
    run_root: Path,
    shard_index: int,
    shard_count: int,
    limit_tickers: int | None = None,
) -> dict:
    raw_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    cfg = AtlasConfig.from_yaml(config_path)
    tickers = load_universe_tickers(raw_config["data"]["universe_activity_path"])
    shard_tickers = tickers_for_shard(tickers, shard_index, shard_count)
    if limit_tickers is not None:
        shard_tickers = shard_tickers[:limit_tickers]
    shard_root = run_root / f"shard={shard_index:02d}"
    shard_root.mkdir(parents=True, exist_ok=True)
    heartbeat_path = shard_root / "heartbeat.json"
    manifest_path = shard_root / "shard_manifest.json"
    started = _utc_now()
    counts = {name: 0 for name in TABLE_NAMES.values()}
    failures: list[dict] = []

    _atomic_json(
        heartbeat_path,
        {
            "status": "running",
            "pid": os.getpid(),
            "started_at": started,
            "updated_at": started,
            "shard_index": shard_index,
            "shard_count": shard_count,
            "planned_tickers": len(shard_tickers),
            "completed_tickers": 0,
        },
    )

    for ordinal, ticker in enumerate(shard_tickers, start=1):
        try:
            source = load_raw_ticker(raw_config["data"]["raw_root"], ticker)
            sessions = compute_session_observables(source, cfg)
            tables = build_atlas_tables(sessions, cfg)
            for attribute, table_name in TABLE_NAMES.items():
                table = getattr(tables, attribute)
                write_table_part(table, shard_root / table_name, ticker)
                counts[table_name] += len(table)
        except Exception as exc:  # persisted and certified; never silently skipped
            failures.append({"ticker": ticker, "error_type": type(exc).__name__, "message": str(exc)})
        _atomic_json(
            heartbeat_path,
            {
                "status": "running",
                "pid": os.getpid(),
                "started_at": started,
                "updated_at": _utc_now(),
                "shard_index": shard_index,
                "shard_count": shard_count,
                "planned_tickers": len(shard_tickers),
                "completed_tickers": ordinal,
                "last_ticker": ticker,
                "failures": len(failures),
            },
        )

    finished = _utc_now()
    manifest = {
        "status": "pass" if not failures else "fail",
        "started_at": started,
        "finished_at": finished,
        "shard_index": shard_index,
        "shard_count": shard_count,
        "planned_tickers": len(shard_tickers),
        "completed_tickers": len(shard_tickers),
        "counts": counts,
        "failures": failures,
        "config_path": str(config_path.resolve()),
        "python": sys.version,
        "platform": platform.platform(),
        "pid": os.getpid(),
    }
    _atomic_json(manifest_path, manifest)
    _atomic_json(heartbeat_path, {**manifest, "updated_at": finished})
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one governed Daily Pattern Atlas shard")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--limit-tickers", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = run_shard(
        args.config.resolve(),
        args.run_root.resolve(),
        args.shard_index,
        args.shard_count,
        args.limit_tickers,
    )
    print(json.dumps(manifest, indent=2))
    return 0 if manifest["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
