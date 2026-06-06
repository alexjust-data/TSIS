from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


RETRY_STATUSES = {"DOWNLOAD_FAIL", "DOWNLOAD_PARTIAL"}


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-base-dir", default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_download_c")
    ap.add_argument("--pattern", default="20260327_quotes_lt_1b_c_shard_*_of_08")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    run_base_dir = Path(args.run_base_dir)
    if not run_base_dir.exists():
        raise SystemExit(f"run-base-dir not found: {run_base_dir}")

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_retry\{utc_stamp()}_build_quotes_c_retry_from_run_dirs"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    run_dirs = sorted([p for p in run_base_dir.glob(args.pattern) if p.is_dir()])
    if not run_dirs:
        raise SystemExit(f"no run dirs matched pattern {args.pattern} under {run_base_dir}")

    rows: list[pd.DataFrame] = []
    seen_run_dirs: list[str] = []
    missing_current_csv: list[str] = []

    for rd in run_dirs:
        current_csv = rd / "download_events_current.csv"
        if not current_csv.exists():
            missing_current_csv.append(str(current_csv))
            continue
        df = pd.read_csv(current_csv)
        if df.empty:
            continue
        df = df.loc[df["status"].isin(RETRY_STATUSES)].copy()
        if df.empty:
            seen_run_dirs.append(rd.name)
            continue
        df["source_run_dir"] = rd.name
        rows.append(df)
        seen_run_dirs.append(rd.name)

    if rows:
        retry_df = pd.concat(rows, ignore_index=True)
        retry_df["ticker"] = retry_df["ticker"].astype(str).str.upper().str.strip()
        retry_df["date"] = retry_df["date"].astype(str).str.slice(0, 10)
        retry_df["task_key"] = retry_df["ticker"] + "|" + retry_df["date"]
        retry_df = retry_df.sort_values(["ticker", "date", "processed_at_utc", "source_run_dir"]).drop_duplicates(
            subset=["task_key"], keep="last"
        )
    else:
        retry_df = pd.DataFrame(columns=["ticker", "date", "task_key", "status", "source_run_dir"])

    retry_tasks = retry_df[["ticker", "date"]].copy() if not retry_df.empty else pd.DataFrame(columns=["ticker", "date"])

    retry_csv = outdir / "tasks_quotes_c_retry_only.csv"
    retry_detail_csv = outdir / "tasks_quotes_c_retry_detail.csv"
    summary_json = outdir / "quotes_c_retry_summary.json"

    retry_tasks.to_csv(retry_csv, index=False)
    retry_df.to_csv(retry_detail_csv, index=False)

    status_counts = retry_df["status"].value_counts(dropna=False).to_dict() if not retry_df.empty else {}
    summary = {
        "run_base_dir": str(run_base_dir),
        "pattern": args.pattern,
        "outdir": str(outdir),
        "matched_run_dirs": len(run_dirs),
        "seen_run_dirs": seen_run_dirs,
        "missing_current_csv": missing_current_csv,
        "retry_total": int(len(retry_tasks)),
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {retry_csv}")


if __name__ == "__main__":
    main()
