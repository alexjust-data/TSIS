from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


DEFAULT_MISSING = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_missing_only\latest\tasks_trades_lt_1b_missing_only.csv"
)
DEFAULT_OUT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_shards")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Parte trades missing_only en shards disjuntos")
    ap.add_argument("--missing-csv", default=str(DEFAULT_MISSING))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--num-shards", type=int, default=4)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    missing_path = Path(args.missing_csv)
    if not missing_path.exists():
        raise FileNotFoundError(f"No existe missing csv: {missing_path}")
    if args.num_shards < 2:
        raise ValueError("--num-shards debe ser >= 2")

    if args.outdir:
        outdir = Path(args.outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = DEFAULT_OUT_ROOT / f"{stamp}_shard_trades_lt_1b_missing_only"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(missing_path).copy()
    required = {"ticker", "date"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Faltan columnas en missing csv: {sorted(missing)}")

    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["ticker", "date"], keep="first").sort_values(["ticker", "date"]).reset_index(drop=True)

    # Round-robin sobre el orden estable para balancear carga.
    df["shard_id"] = df.index % args.num_shards

    shard_manifest: list[dict[str, object]] = []
    for shard_id in range(args.num_shards):
        sub = df[df["shard_id"] == shard_id][["ticker", "date"]].copy().reset_index(drop=True)
        shard_csv = outdir / f"tasks_trades_lt_1b_missing_only.shard_{shard_id+1:02d}_of_{args.num_shards:02d}.csv"
        sub.to_csv(shard_csv, index=False)
        shard_manifest.append(
            {
                "shard_id": int(shard_id + 1),
                "num_shards": int(args.num_shards),
                "rows": int(len(sub)),
                "path": str(shard_csv),
                "date_min": str(sub["date"].min()) if len(sub) else None,
                "date_max": str(sub["date"].max()) if len(sub) else None,
            }
        )

    manifest = {
        "missing_csv": str(missing_path),
        "outdir": str(outdir),
        "num_shards": int(args.num_shards),
        "rows_total": int(len(df)),
        "shards": shard_manifest,
    }
    (outdir / "trades_lt_1b_shards_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
