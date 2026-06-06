from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

INVENTORY_COLUMNS = [
    "root",
    "root_path",
    "file",
    "relpath",
    "ticker",
    "year",
    "month",
    "filename_ticker",
    "filename_year",
    "filename_month",
    "task_key",
    "size_bytes",
    "mtime_utc",
    "inventory_seen_utc",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        outdir = Path(
            r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def discover_shard_dirs(base_dir: Path, pattern: str) -> list[Path]:
    return sorted([p for p in base_dir.glob(pattern) if p.is_dir()])


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge shard inventories for ohlcv_1m v2")
    ap.add_argument("--base-dir", required=True)
    ap.add_argument("--pattern", default="ohlcv_1m_inventory_shard_*_of_*")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        raise SystemExit(f"base-dir not found: {base_dir}")

    outdir = build_outdir(args.outdir)
    shard_dirs = discover_shard_dirs(base_dir, args.pattern)
    if not shard_dirs:
        raise SystemExit("No shard directories found")

    frames: list[pd.DataFrame] = []
    shard_records: list[dict] = []
    missing_outputs: list[str] = []

    for shard_dir in shard_dirs:
        files_parquet = shard_dir / "ohlcv_1m_inventory_files.parquet"
        by_ticker_parquet = shard_dir / "ohlcv_1m_inventory_by_ticker.parquet"
        summary_json = shard_dir / "ohlcv_1m_inventory_summary.json"
        if not files_parquet.exists():
            missing_outputs.append(str(files_parquet))
            continue
        df = pd.read_parquet(files_parquet).copy()
        frames.append(df)

        summary = None
        if summary_json.exists():
            try:
                summary = json.loads(summary_json.read_text(encoding="utf-8"))
            except Exception:
                summary = None

        shard_records.append(
            {
                "run_dir": shard_dir.name,
                "files_parquet": str(files_parquet),
                "by_ticker_parquet": str(by_ticker_parquet) if by_ticker_parquet.exists() else None,
                "summary_json": str(summary_json) if summary_json.exists() else None,
                "rows": int(len(df)),
                "task_keys": int(df["task_key"].nunique()) if "task_key" in df.columns else None,
                "tickers": int(df["ticker"].nunique()) if "ticker" in df.columns else None,
                "summary_all_rows": int(summary["all_rows"]) if summary and "all_rows" in summary else None,
                "summary_all_tickers": int(summary["all_tickers"]) if summary and "all_tickers" in summary else None,
            }
        )

    if missing_outputs:
        raise SystemExit("Missing shard outputs:\n" + "\n".join(missing_outputs))

    all_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=INVENTORY_COLUMNS)
    all_df = all_df[[c for c in INVENTORY_COLUMNS if c in all_df.columns]].copy()
    if not all_df.empty:
        all_df = all_df.sort_values(["ticker", "year", "month", "root", "file"]).reset_index(drop=True)

    dup_task_keys = pd.DataFrame(columns=["task_key", "rows"])
    if not all_df.empty and "task_key" in all_df.columns:
        dup_task_keys = (
            all_df.groupby("task_key", dropna=False)
            .size()
            .reset_index(name="rows")
        )
        dup_task_keys = dup_task_keys[dup_task_keys["rows"] > 1].sort_values(["rows", "task_key"], ascending=[False, True]).reset_index(drop=True)

    by_ticker = (
        all_df.groupby("ticker", dropna=False)
        .agg(
            files_total=("file", "count"),
            task_keys=("task_key", "nunique"),
            roots_present=("root", lambda s: "|".join(sorted(set(map(str, s))))),
            year_min=("year", "min"),
            year_max=("year", "max"),
            month_min=("month", "min"),
            month_max=("month", "max"),
            bytes_total=("size_bytes", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum())),
        )
        .reset_index()
        if not all_df.empty
        else pd.DataFrame(columns=["ticker", "files_total", "task_keys", "roots_present", "year_min", "year_max", "month_min", "month_max", "bytes_total"])
    )

    shard_manifest_df = pd.DataFrame(shard_records)

    files_parquet = outdir / "ohlcv_1m_inventory_files.parquet"
    files_csv = outdir / "ohlcv_1m_inventory_files.csv"
    by_ticker_parquet = outdir / "ohlcv_1m_inventory_by_ticker.parquet"
    by_ticker_csv = outdir / "ohlcv_1m_inventory_by_ticker.csv"
    dup_parquet = outdir / "ohlcv_1m_inventory_duplicate_task_keys.parquet"
    dup_csv = outdir / "ohlcv_1m_inventory_duplicate_task_keys.csv"
    shard_manifest_parquet = outdir / "ohlcv_1m_inventory_shard_manifest.parquet"
    shard_manifest_csv = outdir / "ohlcv_1m_inventory_shard_manifest.csv"
    summary_json = outdir / "ohlcv_1m_inventory_summary.json"

    all_df.to_parquet(files_parquet, index=False)
    all_df.to_csv(files_csv, index=False)
    by_ticker.to_parquet(by_ticker_parquet, index=False)
    by_ticker.to_csv(by_ticker_csv, index=False)
    dup_task_keys.to_parquet(dup_parquet, index=False)
    dup_task_keys.to_csv(dup_csv, index=False)
    shard_manifest_df.to_parquet(shard_manifest_parquet, index=False)
    shard_manifest_df.to_csv(shard_manifest_csv, index=False)

    summary = {
        "merged_at_utc": utc_now(),
        "base_dir": str(base_dir),
        "pattern": str(args.pattern),
        "shards_found": int(len(shard_dirs)),
        "merged_rows": int(len(all_df)),
        "merged_task_keys": int(all_df["task_key"].nunique()) if not all_df.empty else 0,
        "merged_tickers": int(all_df["ticker"].nunique()) if not all_df.empty else 0,
        "duplicate_task_keys": int(len(dup_task_keys)),
        "year_min": int(pd.to_numeric(all_df["year"], errors="coerce").min()) if not all_df.empty else None,
        "year_max": int(pd.to_numeric(all_df["year"], errors="coerce").max()) if not all_df.empty else None,
        "month_min": int(pd.to_numeric(all_df["month"], errors="coerce").min()) if not all_df.empty else None,
        "month_max": int(pd.to_numeric(all_df["month"], errors="coerce").max()) if not all_df.empty else None,
        "total_bytes": int(pd.to_numeric(all_df["size_bytes"], errors="coerce").fillna(0).sum()) if not all_df.empty else 0,
        "outputs": {
            "ohlcv_1m_inventory_files_parquet": str(files_parquet),
            "ohlcv_1m_inventory_files_csv": str(files_csv),
            "ohlcv_1m_inventory_by_ticker_parquet": str(by_ticker_parquet),
            "ohlcv_1m_inventory_by_ticker_csv": str(by_ticker_csv),
            "duplicate_task_keys_parquet": str(dup_parquet),
            "duplicate_task_keys_csv": str(dup_csv),
            "shard_manifest_parquet": str(shard_manifest_parquet),
            "shard_manifest_csv": str(shard_manifest_csv),
            "summary_json": str(summary_json),
        },
        "outdir": str(outdir),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
