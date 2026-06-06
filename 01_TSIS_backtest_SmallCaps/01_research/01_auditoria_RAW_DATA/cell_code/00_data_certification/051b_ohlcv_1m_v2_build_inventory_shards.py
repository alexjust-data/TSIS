from __future__ import annotations

import argparse
import json
import math
import os
from datetime import UTC, datetime, timezone
from pathlib import Path

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        outdir = Path(
            rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\{utc_stamp()}_shard_ohlcv_1m_inventory"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def discover_tickers(root: Path) -> list[str]:
    tickers: list[str] = []
    with os.scandir(root) as it:
        entries = [e for e in it if e.is_dir() and e.name.startswith("ticker=")]
    entries.sort(key=lambda e: e.name)
    for entry in entries:
        ticker = entry.name.split("=", 1)[1].upper().strip()
        if ticker:
            tickers.append(ticker)
    return sorted(set(tickers))


def shardify(items: list[str], shard_count: int) -> list[list[str]]:
    if shard_count < 1:
        raise ValueError("shard_count must be >= 1")
    shards = [[] for _ in range(shard_count)]
    for idx, item in enumerate(items):
        shards[idx % shard_count].append(item)
    return shards


def main() -> None:
    ap = argparse.ArgumentParser(description="Build ticker shards for parallel ohlcv_1m inventory")
    ap.add_argument("--d-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--outdir", default="")
    ap.add_argument("--shards", type=int, default=8)
    ap.add_argument("--prefix", default="tasks_ohlcv_1m_inventory")
    args = ap.parse_args()

    root = Path(args.d_root)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    outdir = build_outdir(args.outdir)
    shard_count = int(args.shards)
    prefix = str(args.prefix).strip() or "tasks_ohlcv_1m_inventory"

    tickers = discover_tickers(root)
    shard_lists = shardify(tickers, shard_count)

    manifest_records: list[dict] = []
    for i, shard_tickers in enumerate(shard_lists, start=1):
        df = pd.DataFrame({"ticker": shard_tickers})
        csv_path = outdir / f"{prefix}.shard_{i:02d}_of_{shard_count:02d}.csv"
        parquet_path = outdir / f"{prefix}.shard_{i:02d}_of_{shard_count:02d}.parquet"
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        manifest_records.append(
            {
                "shard_id": i,
                "shard_name": f"shard_{i:02d}_of_{shard_count:02d}",
                "tickers": int(len(df)),
                "ticker_min": str(df["ticker"].min()) if not df.empty else None,
                "ticker_max": str(df["ticker"].max()) if not df.empty else None,
                "csv_path": str(csv_path),
                "parquet_path": str(parquet_path),
            }
        )

    manifest = {
        "built_at_utc": utc_now(),
        "d_root": str(root),
        "tickers_total": int(len(tickers)),
        "shards": int(shard_count),
        "prefix": prefix,
        "shard_size_floor": int(math.floor(len(tickers) / shard_count)) if shard_count else None,
        "shard_size_ceil": int(math.ceil(len(tickers) / shard_count)) if shard_count else None,
        "shard_files": manifest_records,
        "outdir": str(outdir),
    }

    manifest_path = outdir / "ohlcv_1m_inventory_shards_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
