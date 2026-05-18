from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


OK_STATUSES = {"DOWNLOADED_OK", "DOWNLOADED_EMPTY"}


def utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def shard_name(shard_id: int, num_shards: int = 10) -> str:
    return f"tasks_quotes_lt_1b_remaining_only.shard_{shard_id:02d}_of_{num_shards:02d}.csv"


def load_tasks(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise SystemExit(f"missing shard csv: {csv_path}")
    df = pd.read_csv(csv_path, usecols=["ticker", "date"])
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = df["date"].astype(str).str.strip()
    df = df.drop_duplicates().reset_index(drop=True)
    df["task_key"] = df["ticker"] + "|" + df["date"]
    return df


def load_history_latest(history_csv: Path) -> pd.DataFrame:
    if not history_csv.exists():
        return pd.DataFrame(columns=["task_key", "ticker", "date", "status"])
    df = pd.read_csv(history_csv, usecols=["ticker", "date", "status"])
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = df["date"].astype(str).str.strip()
    df["status"] = df["status"].astype(str).str.strip()
    df["task_key"] = df["ticker"] + "|" + df["date"]
    return df.drop_duplicates(subset=["task_key"], keep="last").reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards-dir", required=True)
    ap.add_argument("--run-base-dir", required=True)
    ap.add_argument("--num-shards", type=int, default=10)
    ap.add_argument("--completed-shards", default="1,2,3,4")
    ap.add_argument("--partial-shards", default="5,6,7,8")
    ap.add_argument("--not-started-shards", default="9,10")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    shards_dir = Path(args.shards_dir)
    run_base_dir = Path(args.run_base_dir)
    num_shards = int(args.num_shards)
    completed_shards = [int(x) for x in args.completed_shards.split(",") if str(x).strip()]
    partial_shards = [int(x) for x in args.partial_shards.split(",") if str(x).strip()]
    not_started_shards = [int(x) for x in args.not_started_shards.split(",") if str(x).strip()]

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_remaining_after_d_stop\{utc_stamp()}_build_quotes_lt_1b_remaining_after_d_stop"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    completed_ok_keys: set[str] = set()
    completed_bad_rows: list[pd.DataFrame] = []
    partial_remaining_frames: list[pd.DataFrame] = []
    not_started_frames: list[pd.DataFrame] = []

    completed_counts: dict[str, int] = {}
    partial_counts: dict[str, int] = {}
    not_started_counts: dict[str, int] = {}

    for shard_id in completed_shards:
        history_csv = run_base_dir / f"20260325_quotes_lt_1b_shard_{shard_id:02d}_of_{num_shards:02d}" / "download_events_history.csv"
        latest = load_history_latest(history_csv)
        ok = latest[latest["status"].isin(OK_STATUSES)].copy()
        bad = latest[~latest["status"].isin(OK_STATUSES)].copy()
        completed_ok_keys.update(ok["task_key"].astype(str).tolist())
        if not bad.empty:
            bad["source_group"] = "completed_shard_non_ok"
            bad["source_shard"] = shard_id
            completed_bad_rows.append(bad[["ticker", "date", "task_key", "status", "source_group", "source_shard"]])
        completed_counts[f"shard_{shard_id:02d}"] = int(len(ok))

    for shard_id in partial_shards:
        shard_csv = shards_dir / shard_name(shard_id, num_shards)
        tasks = load_tasks(shard_csv)

        history_csv = run_base_dir / f"20260325_quotes_lt_1b_shard_{shard_id:02d}_of_{num_shards:02d}" / "download_events_history.csv"
        latest = load_history_latest(history_csv)
        latest_non_ok = latest[~latest["status"].isin(OK_STATUSES)][["task_key", "status"]].copy()
        latest_non_ok = latest_non_ok.rename(columns={"status": "current_status"})
        latest_ok_keys = set(latest[latest["status"].isin(OK_STATUSES)]["task_key"].astype(str).tolist())

        remaining = tasks[~tasks["task_key"].isin(latest_ok_keys)].copy()
        remaining = remaining.merge(latest_non_ok, on="task_key", how="left")
        remaining["remaining_reason"] = remaining["current_status"].fillna("NOT_PROCESSED_YET")
        remaining["source_group"] = "partial_shard_remaining"
        remaining["source_shard"] = shard_id
        partial_remaining_frames.append(
            remaining[["ticker", "date", "task_key", "current_status", "remaining_reason", "source_group", "source_shard"]]
        )
        partial_counts[f"shard_{shard_id:02d}"] = int(len(remaining))

    for shard_id in not_started_shards:
        shard_csv = shards_dir / shard_name(shard_id, num_shards)
        tasks = load_tasks(shard_csv)
        tasks["current_status"] = pd.NA
        tasks["remaining_reason"] = "NOT_STARTED_SHARD"
        tasks["source_group"] = "not_started_shard"
        tasks["source_shard"] = shard_id
        not_started_frames.append(
            tasks[["ticker", "date", "task_key", "current_status", "remaining_reason", "source_group", "source_shard"]]
        )
        not_started_counts[f"shard_{shard_id:02d}"] = int(len(tasks))

    remaining_parts = []
    if completed_bad_rows:
        remaining_parts.append(pd.concat(completed_bad_rows, ignore_index=True))
    if partial_remaining_frames:
        remaining_parts.append(pd.concat(partial_remaining_frames, ignore_index=True))
    if not_started_frames:
        remaining_parts.append(pd.concat(not_started_frames, ignore_index=True))

    if remaining_parts:
        remaining = pd.concat(remaining_parts, ignore_index=True)
    else:
        remaining = pd.DataFrame(columns=["ticker", "date", "task_key", "current_status", "remaining_reason", "source_group", "source_shard"])

    remaining = remaining.drop_duplicates(subset=["task_key"], keep="first").reset_index(drop=True)

    remaining_csv = outdir / "tasks_quotes_lt_1b_remaining_after_d_stop.csv"
    remaining_parquet = outdir / "tasks_quotes_lt_1b_remaining_after_d_stop.parquet"
    manifest_json = outdir / "tasks_quotes_lt_1b_remaining_after_d_stop_manifest.json"

    remaining[["ticker", "date", "current_status", "remaining_reason", "source_group", "source_shard"]].to_csv(
        remaining_csv, index=False
    )
    remaining[["ticker", "date", "current_status", "remaining_reason", "source_group", "source_shard"]].to_parquet(
        remaining_parquet, index=False
    )

    manifest = {
        "shards_dir": str(shards_dir),
        "run_base_dir": str(run_base_dir),
        "outdir": str(outdir),
        "num_shards": num_shards,
        "completed_shards": completed_shards,
        "partial_shards": partial_shards,
        "not_started_shards": not_started_shards,
        "completed_ok_counts": completed_counts,
        "partial_remaining_counts": partial_counts,
        "not_started_counts": not_started_counts,
        "completed_ok_total": int(sum(completed_counts.values())),
        "remaining_total": int(len(remaining)),
        "remaining_by_reason": remaining["remaining_reason"].value_counts(dropna=False).to_dict() if len(remaining) else {},
    }
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))
    print(f"saved: {remaining_csv}")


if __name__ == "__main__":
    main()
