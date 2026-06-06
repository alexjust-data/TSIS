from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_tickers_from_shard(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["ticker"]).copy()
    df["ticker"] = df["ticker"].astype("string").str.strip().str.upper()
    df = df.dropna(subset=["ticker"])
    df = df[df["ticker"] != ""]
    return pd.DataFrame({"ticker": sorted(df["ticker"].drop_duplicates().tolist())})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cutoff",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    )
    ap.add_argument(
        "--shard-09",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_shards\20260325_095007_shard_trades_lt_1b_missing_only\tasks_trades_lt_1b_missing_only.shard_09_of_10.csv",
    )
    ap.add_argument(
        "--shard-10",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_shards\20260325_095007_shard_trades_lt_1b_missing_only\tasks_trades_lt_1b_missing_only.shard_10_of_10.csv",
    )
    ap.add_argument(
        "--outdir",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_shards_vs_lt1b_cutoff\20260330_audit_trades_shards_09_10_vs_lt1b",
    )
    args = ap.parse_args()

    cutoff = Path(args.cutoff)
    shard_09 = Path(args.shard_09)
    shard_10 = Path(args.shard_10)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cut_df = pd.read_parquet(cutoff).copy()
    cut_df["ticker"] = cut_df["ticker"].astype("string").str.strip().str.upper()
    cut_df = cut_df.dropna(subset=["ticker"])
    cut_df = cut_df[cut_df["ticker"] != ""].copy()

    keep_cols = [
        c
        for c in [
            "ticker",
            "first_seen_date",
            "last_observed_date",
            "status_rebuilt",
            "anchor_date_used",
            "market_cap_t",
            "classification_1b",
            "classification_reason_1b",
        ]
        if c in cut_df.columns
    ]
    cut_df = cut_df[keep_cols].drop_duplicates(subset=["ticker"], keep="first")

    outputs = {}
    metrics = {}

    for label, path in [("09", shard_09), ("10", shard_10)]:
        shard_tickers = load_tickers_from_shard(path)
        audit = shard_tickers.merge(cut_df, on="ticker", how="left", indicator=True)
        audit["in_lt1b_cutoff"] = audit["_merge"].eq("both")
        audit = audit.drop(columns=["_merge"]).sort_values("ticker").reset_index(drop=True)

        all_csv = outdir / f"shard_{label}_tickers_vs_lt1b_cutoff.csv"
        in_csv = outdir / f"shard_{label}_tickers_in_lt1b_cutoff.csv"
        out_csv = outdir / f"shard_{label}_tickers_not_in_lt1b_cutoff.csv"

        audit.to_csv(all_csv, index=False)
        audit[audit["in_lt1b_cutoff"]].to_csv(in_csv, index=False)
        audit[~audit["in_lt1b_cutoff"]].to_csv(out_csv, index=False)

        outputs[f"shard_{label}"] = {
            "all": str(all_csv),
            "in_lt1b": str(in_csv),
            "not_in_lt1b": str(out_csv),
        }
        metrics[f"shard_{label}"] = {
            "tickers_total": int(len(audit)),
            "tickers_in_lt1b_cutoff": int(audit["in_lt1b_cutoff"].sum()),
            "tickers_not_in_lt1b_cutoff": int((~audit["in_lt1b_cutoff"]).sum()),
        }

    summary = {
        "cutoff": str(cutoff),
        "shard_09": str(shard_09),
        "shard_10": str(shard_10),
        "outdir": str(outdir),
        "metrics": metrics,
        "outputs": outputs,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
