from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


DEFAULT_ALL = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_all.parquet"
)
DEFAULT_OUT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026.parquet"
)


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-all", default=str(DEFAULT_ALL))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--start", default="2005-01-01")
    ap.add_argument("--end", default="2026-12-31")
    args = ap.parse_args()

    start = pd.to_datetime(args.start).date()
    end = pd.to_datetime(args.end).date()

    in_all = Path(args.in_all)
    out_path = Path(args.out)
    if not in_all.exists():
        raise SystemExit(f"in-all not found: {in_all}")

    d = pd.read_parquet(in_all).copy()
    d["first_seen_date"] = pd.to_datetime(d["first_seen_date"], errors="coerce").dt.date
    d["last_seen_date"] = pd.to_datetime(d["last_seen_date"], errors="coerce").dt.date

    mask = (
        d["first_seen_date"].notna()
        & d["last_seen_date"].notna()
        & (d["first_seen_date"] <= end)
        & (d["last_seen_date"] >= start)
    )
    out = d.loc[mask].copy()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)

    summary = {
        "input_parquet": str(in_all),
        "output_parquet": str(out_path),
        "start": str(start),
        "end": str(end),
        "input_rows": int(len(d)),
        "output_rows": int(len(out)),
        "input_entity_id_unique": int(d["entity_id"].astype("string").nunique()) if "entity_id" in d.columns else None,
        "output_entity_id_unique": int(out["entity_id"].astype("string").nunique()) if "entity_id" in out.columns else None,
        "input_ticker_unique": int(d["ticker"].astype("string").nunique()) if "ticker" in d.columns else None,
        "output_ticker_unique": int(out["ticker"].astype("string").nunique()) if "ticker" in out.columns else None,
        "output_date_min": str(out["first_seen_date"].min()) if len(out) else None,
        "output_date_max": str(out["last_seen_date"].max()) if len(out) else None,
    }

    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
