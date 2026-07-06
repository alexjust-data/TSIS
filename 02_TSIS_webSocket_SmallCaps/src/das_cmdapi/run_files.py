"""Run-directory and file writers for DAS CMD API capture."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_run_id(prefix: str = "dry_run") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"das_cmdapi_{prefix}_{stamp}"


def raw_run_root(data_root: Path, run_id: str) -> Path:
    return data_root / "raw_cmdapi" / "runs" / run_id


def ensure_run_files(run_root: Path) -> dict[str, Path]:
    run_root.mkdir(parents=True, exist_ok=False)
    paths = {
        "pre_manifest": run_root / "pre_manifest.json",
        "pid_manifest": run_root / "pid_manifest.json",
        "heartbeat": run_root / "heartbeat.json",
        "command_transcript": run_root / "command_transcript.jsonl",
        "events": run_root / "events.jsonl",
        "subscription_state": run_root / "subscription_state.json",
        "capture_log": run_root / "capture.log",
        "final_summary": run_root / "final_summary.json",
    }
    paths["command_transcript"].touch()
    paths["events"].touch()
    paths["capture_log"].touch()
    return paths


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")
        fh.flush()


def append_log(path: Path, message: str) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{utc_now()} {message}\n")
        fh.flush()
