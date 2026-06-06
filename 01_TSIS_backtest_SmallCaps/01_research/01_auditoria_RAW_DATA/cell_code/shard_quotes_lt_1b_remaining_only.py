from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


def utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remaining-csv", required=True)
    ap.add_argument("--num-shards", type=int, required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    remaining_csv = Path(args.remaining_csv)
    if not remaining_csv.exists():
        raise SystemExit(f"remaining csv not found: {remaining_csv}")
    if args.num_shards <= 0:
        raise SystemExit("--num-shards must be > 0")

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_shards\{utc_stamp()}_shard_quotes_lt_1b_remaining_only"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(remaining_csv)
    if "ticker" not in df.columns or "date" not in df.columns:
        raise SystemExit("remaining csv must contain ticker,date")

    rows_total = int(len(df))
    shards_meta = []

    for shard_idx in range(args.num_shards):
        shard_id = shard_idx + 1
        shard = df.iloc[shard_idx::args.num_shards].copy().reset_index(drop=True)
        shard_name = f"tasks_quotes_lt_1b_remaining_only.shard_{shard_id:02d}_of_{args.num_shards:02d}.csv"
        shard_path = outdir / shard_name
        shard.to_csv(shard_path, index=False)

        meta = {
            "shard_id": shard_id,
            "num_shards": args.num_shards,
            "rows": int(len(shard)),
            "path": str(shard_path),
            "date_min": str(shard["date"].min()) if len(shard) else None,
            "date_max": str(shard["date"].max()) if len(shard) else None,
        }
        shards_meta.append(meta)

    manifest = {
        "remaining_csv": str(remaining_csv),
        "outdir": str(outdir),
        "num_shards": int(args.num_shards),
        "rows_total": rows_total,
        "shards": shards_meta,
    }

    manifest_path = outdir / "quotes_lt_1b_shards_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
