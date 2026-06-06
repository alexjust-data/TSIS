from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_inventory(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory parquet not found: {path}")
    return pd.read_parquet(path)


def apply_filters(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    out = df.copy()
    if str(args.root).strip():
        roots = {x.strip().upper() for x in str(args.root).split(",") if x.strip()}
        out = out[out["root"].astype(str).str.upper().isin(roots)]
    if str(args.ticker).strip():
        tickers = {x.strip().upper() for x in str(args.ticker).split(",") if x.strip()}
        out = out[out["ticker"].astype(str).str.upper().isin(tickers)]
    if str(args.date_from).strip():
        out = out[pd.to_datetime(out["date"], errors="coerce") >= pd.Timestamp(args.date_from)]
    if str(args.date_to).strip():
        out = out[pd.to_datetime(out["date"], errors="coerce") <= pd.Timestamp(args.date_to)]
    if int(args.limit) > 0:
        out = out.head(int(args.limit)).copy()
    return out.reset_index(drop=True)


def stable_shard(task_key: str, num_shards: int) -> int:
    digest = hashlib.md5(task_key.encode("utf-8")).hexdigest()
    return int(digest, 16) % num_shards


def main() -> None:
    ap = argparse.ArgumentParser(description="Build deterministic trades validation shards from inventory parquet")
    ap.add_argument("--inventory-parquet", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--num-shards", type=int, default=8)
    ap.add_argument("--root", default="")
    ap.add_argument("--ticker", default="")
    ap.add_argument("--date-from", default="")
    ap.add_argument("--date-to", default="")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if int(args.num_shards) <= 0:
        raise ValueError("--num-shards must be > 0")

    inventory_path = Path(args.inventory_parquet)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_inventory(inventory_path)
    filtered = apply_filters(df, args)

    if "task_key" not in filtered.columns:
        raise ValueError("Inventory parquet must contain 'task_key'")

    filtered["task_key"] = filtered["task_key"].astype(str)
    if filtered["task_key"].duplicated().any():
        dupes = int(filtered["task_key"].duplicated().sum())
        raise ValueError(f"Filtered inventory has duplicate task_key rows: {dupes}")

    filtered["shard_id"] = filtered["task_key"].map(lambda s: stable_shard(s, int(args.num_shards)))

    shard_rows: list[dict[str, Any]] = []
    for shard_id in range(int(args.num_shards)):
        shard_df = filtered[filtered["shard_id"] == shard_id].drop(columns=["shard_id"]).copy()
        shard_path = outdir / f"trades_inventory.shard_{shard_id + 1:02d}_of_{int(args.num_shards):02d}.parquet"
        shard_df.to_parquet(shard_path, index=False)
        shard_rows.append(
            {
                "shard_id": shard_id + 1,
                "shard_path": str(shard_path),
                "rows": int(len(shard_df)),
                "task_keys": int(shard_df["task_key"].nunique()),
                "tickers": int(shard_df["ticker"].astype(str).str.upper().nunique()) if not shard_df.empty else 0,
                "date_min": None if shard_df.empty else str(pd.to_datetime(shard_df["date"], errors="coerce").min()),
                "date_max": None if shard_df.empty else str(pd.to_datetime(shard_df["date"], errors="coerce").max()),
            }
        )

    shard_manifest = {
        "created_at_utc": utc_now(),
        "inventory_parquet": str(inventory_path),
        "outdir": str(outdir),
        "num_shards": int(args.num_shards),
        "filters": {
            "root": args.root,
            "ticker": args.ticker,
            "date_from": args.date_from,
            "date_to": args.date_to,
            "limit": int(args.limit),
        },
        "rows_total": int(len(filtered)),
        "task_keys_total": int(filtered["task_key"].nunique()),
        "tickers_total": int(filtered["ticker"].astype(str).str.upper().nunique()) if not filtered.empty else 0,
        "date_min": None if filtered.empty else str(pd.to_datetime(filtered["date"], errors="coerce").min()),
        "date_max": None if filtered.empty else str(pd.to_datetime(filtered["date"], errors="coerce").max()),
        "shards": shard_rows,
    }
    write_json(outdir / "trades_validation_shards_manifest.json", shard_manifest)

    summary_df = pd.DataFrame(shard_rows)
    summary_df.to_csv(outdir / "trades_validation_shards_summary.csv", index=False)
    print(json.dumps(shard_manifest, indent=2))


if __name__ == "__main__":
    main()
