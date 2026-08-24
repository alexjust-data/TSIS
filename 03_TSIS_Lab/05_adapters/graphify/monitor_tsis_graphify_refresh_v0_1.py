#!/usr/bin/env python
"""Compact monitor for governed TSIS Graphify refresh runs."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def line(run_root: Path) -> str:
    hb = read_json(run_root / "monitor" / "heartbeat_latest.json") or {}
    observed = hb.get("observed_at_utc")
    age = "na"
    if observed:
        try:
            age = round((datetime.now(timezone.utc) - datetime.fromisoformat(observed)).total_seconds(), 1)
        except Exception:
            pass
    return (
        f"[{datetime.now(timezone.utc).isoformat()}] "
        f"status={hb.get('status', 'no_heartbeat')} stage={hb.get('stage', 'na')} "
        f"target={hb.get('target_id', 'na')} pid={hb.get('pid', 'na')} age_sec={age} "
        f"files={hb.get('files', 'na')} code={hb.get('code_files', 'na')} "
        f"semantic={hb.get('semantic_files', 'na')} chunks={hb.get('chunks_complete', 0)}/{hb.get('chunks_total', 0)} "
        f"nodes={hb.get('nodes', 'na')} edges={hb.get('edges', 'na')} detail={hb.get('detail', '')}"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--interval-sec", type=int, default=15)
    args = ap.parse_args()
    root = Path(args.run_root)
    while True:
        print(line(root), flush=True)
        if not args.watch:
            return 0
        hb = read_json(root / "monitor" / "heartbeat_latest.json") or {}
        if hb.get("status") in {"complete", "failed", "blocked"}:
            return 0
        time.sleep(args.interval_sec)


if __name__ == "__main__":
    raise SystemExit(main())

