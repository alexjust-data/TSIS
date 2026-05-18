from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026.parquet"
)
DEFAULT_OUT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026_upper.parquet"
)


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(DEFAULT_INPUT))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    input_path = Path(args.input)
    out_path = Path(args.out)
    if not input_path.exists():
        raise SystemExit(f"input not found: {input_path}")

    u = pd.read_parquet(input_path).copy()
    input_rows = int(len(u))
    ticker_na_before = int(u["ticker"].isna().sum()) if "ticker" in u.columns else None
    ticker_nunique_before = int(u["ticker"].astype("string").nunique()) if "ticker" in u.columns else None

    u["ticker"] = u["ticker"].astype("string").str.strip().str.upper()
    u = u.dropna(subset=["ticker"]).drop_duplicates(subset=["ticker"]).sort_values("ticker").reset_index(drop=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    u.to_parquet(out_path, index=False)

    summary = {
        "input_parquet": str(input_path),
        "output_parquet": str(out_path),
        "transformation": [
            "ticker -> strip().upper()",
            "dropna(subset=['ticker'])",
            "drop_duplicates(subset=['ticker'])",
            "sort_values('ticker')",
        ],
        "input_rows": input_rows,
        "output_rows": int(len(u)),
        "ticker_na_before": ticker_na_before,
        "ticker_unique_before": ticker_nunique_before,
        "ticker_na_after": int(u["ticker"].isna().sum()),
        "ticker_unique_after": int(u["ticker"].astype("string").nunique()),
        "entity_id_unique_after": int(u["entity_id"].astype("string").nunique()) if "entity_id" in u.columns else None,
    }

    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
