from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Monitor governed OHLCV 1m quote-guarded full-universe runs.")
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--watch", action="store_true")
    p.add_argument("--interval-sec", type=float, default=30.0)
    p.add_argument("--compact", action="store_true")
    p.add_argument("--tail-heartbeat", type=int, default=0)
    return p


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def latest_age_sec(path: Path) -> Optional[float]:
    try:
        return max(0.0, time.time() - path.stat().st_mtime)
    except OSError:
        return None


def dir_size_hint(path: Path) -> str:
    if not path.exists():
        return "missing"
    files = 0
    bytes_ = 0
    try:
        for p in path.rglob("*.parquet"):
            files += 1
            bytes_ += p.stat().st_size
            if files >= 2000:
                break
    except Exception:
        return "unavailable"
    suffix = "+" if files >= 2000 else ""
    return f"{files}{suffix} parquet, {bytes_ / (1024**3):.2f} GiB sampled"


def line(run_root: Path, compact: bool) -> str:
    hb_path = run_root / "heartbeat_latest.json"
    hb = load_json(hb_path)
    age = latest_age_sec(hb_path)
    if hb is None:
        return f"[{datetime.now(timezone.utc).isoformat()}] status=no_heartbeat run_root={run_root}"
    status = hb.get("status")
    if age is not None and age > 300 and status == "running":
        status = "stale_heartbeat"
    inspection = run_root / "early_inspection_ready.json"
    early = load_json(inspection) if inspection.exists() else None
    final = None
    for candidate in ["final_manifest_materialize_year.json", "final_manifest.json"]:
        p = run_root / candidate
        if p.exists():
            final = load_json(p)
            break
    if compact:
        age_text = f"{age:.1f}" if age is not None else "na"
        return (
            f"[{datetime.now(timezone.utc).isoformat()}] status={status} raw_status={hb.get('status')} "
            f"stage={hb.get('stage')} latest_age_sec={age_text} "
            f"elapsed_sec={hb.get('elapsed_seconds')} progress={hb.get('completed_tickers')}/{hb.get('total_tickers')} "
            f"item={hb.get('active_ticker')} rows={hb.get('rows_written')} repairs={hb.get('repairs_applied')} "
            f"failures={hb.get('failed_tickers')} early={bool(early)} final={bool(final)}"
        )
    chunks = [
        f"status={status}",
        f"raw_status={hb.get('status')}",
        f"stage={hb.get('stage')}",
        f"latest_age_sec={age}",
        f"elapsed_sec={hb.get('elapsed_seconds')}",
        f"progress={hb.get('completed_tickers')}/{hb.get('total_tickers')}",
        f"active_ticker={hb.get('active_ticker')}",
        f"rows_written={hb.get('rows_written')}",
        f"repairs_applied={hb.get('repairs_applied')}",
        f"failed_tickers={hb.get('failed_tickers')}",
        f"early_inspection_ready={bool(early)}",
    ]
    if early:
        chunks.append(f"inspection_root={early.get('inspection_root')}")
    if final:
        chunks.append(f"final_status={final.get('final_status') or final.get('status')}")
    output_root = hb.get("output_root") or (final or {}).get("output_root")
    if output_root:
        chunks.append(f"output_hint={dir_size_hint(Path(output_root))}")
    return " | ".join(chunks)


def print_tail(run_root: Path, n: int) -> None:
    if n <= 0:
        return
    path = run_root / "heartbeat.jsonl"
    if not path.exists():
        return
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
        for row in lines:
            print("  hb>", row[:1000])
    except Exception as exc:
        print(f"  hb_tail_error={exc}")


def main() -> int:
    args = build_parser().parse_args()
    while True:
        print(line(args.run_root, args.compact))
        print_tail(args.run_root, args.tail_heartbeat)
        if not args.watch:
            break
        time.sleep(args.interval_sec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
