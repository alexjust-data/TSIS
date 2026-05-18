from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd


def load_live_status(run_dir: Path) -> dict:
    fp = run_dir / "download_live_status.json"
    if not fp.exists():
        return {
            "run_dir": run_dir.name,
            "status": "missing_live_status",
        }

    try:
        js = json.loads(fp.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "run_dir": run_dir.name,
            "status": f"invalid_json: {exc}",
        }

    done_ok = int(js.get("done_ok", 0))
    done_bad = int(js.get("done_bad", 0))
    tasks_total = int(js.get("tasks_total", 0))
    pending = int(js.get("pending", max(tasks_total - done_ok, 0)))
    pct_done = round(100.0 * (done_ok + done_bad) / tasks_total, 4) if tasks_total else None
    status_counts = js.get("status_counts_current", {}) or {}

    return {
        "run_dir": run_dir.name,
        "updated_utc": js.get("updated_utc"),
        "tasks_total": tasks_total,
        "done_ok": done_ok,
        "done_bad": done_bad,
        "pending": pending,
        "pct_done": pct_done,
        "ok_count": status_counts.get("DOWNLOADED_OK"),
        "empty_count": status_counts.get("DOWNLOADED_EMPTY"),
        "fail_count": status_counts.get("DOWNLOAD_FAIL"),
        "partial_count": status_counts.get("DOWNLOAD_PARTIAL"),
        "concurrent": js.get("concurrent"),
        "status": "ok",
    }


def discover_run_dirs(base_dir: Path, pattern: str) -> list[Path]:
    return sorted([p for p in base_dir.glob(pattern) if p.is_dir()])


def clear_terminal() -> None:
    os.system("cls")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--base-dir",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_download",
    )
    ap.add_argument(
        "--pattern",
        default="20260325_quotes_lt_1b_shard_*_of_10",
    )
    ap.add_argument("--interval-sec", type=float, default=10.0)
    ap.add_argument("--iterations", type=int, default=0, help="0 = infinite")
    args = ap.parse_args()

    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        raise SystemExit(f"Base dir not found: {base_dir}")

    iterations = 0
    while True:
        run_dirs = discover_run_dirs(base_dir, args.pattern)
        rows = [load_live_status(rd) for rd in run_dirs]
        df = pd.DataFrame(rows)

        clear_terminal()
        print(f"base_dir={base_dir}")
        print(f"pattern={args.pattern}")
        print(f"run_dirs={len(run_dirs)}")
        print(f"interval_sec={args.interval_sec}")
        print()

        if df.empty:
            print("No matching run dirs.")
        else:
            preferred_cols = [
                "run_dir",
                "updated_utc",
                "done_ok",
                "done_bad",
                "pending",
                "pct_done",
                "ok_count",
                "empty_count",
                "fail_count",
                "partial_count",
                "concurrent",
                "status",
            ]
            cols = [c for c in preferred_cols if c in df.columns]
            df = df[cols].sort_values("run_dir")
            print(df.to_string(index=False))

            total_ok = int(pd.to_numeric(df.get("done_ok"), errors="coerce").fillna(0).sum())
            total_bad = int(pd.to_numeric(df.get("done_bad"), errors="coerce").fillna(0).sum())
            total_pending = int(pd.to_numeric(df.get("pending"), errors="coerce").fillna(0).sum())
            total_tasks = total_ok + total_pending
            pct = round(100.0 * (total_ok + total_bad) / total_tasks, 4) if total_tasks else None

            print()
            print("TOTAL")
            print(
                f"done_ok={total_ok} | done_bad={total_bad} | "
                f"pending={total_pending} | pct_done={pct}"
            )

        iterations += 1
        if args.iterations and iterations >= args.iterations:
            break
        time.sleep(args.interval_sec)


if __name__ == "__main__":
    main()
