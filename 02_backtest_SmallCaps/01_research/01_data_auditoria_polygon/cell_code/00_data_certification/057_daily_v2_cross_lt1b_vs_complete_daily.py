from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = (
            Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit")
            / f"{stamp}_cross_lt1b_vs_complete_daily"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_lt1b(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"LT1B parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError(f"Missing ticker column in {path}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df = df[df["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    return df


def load_complete_daily(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Daily span audit parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "is_contiguous_span"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Missing required columns in {path}: {required}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["is_contiguous_span"] = df["is_contiguous_span"].fillna(False).astype(bool)
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross LT1B universe vs complete daily tickers")
    ap.add_argument("--lt1b-parquet", required=True)
    ap.add_argument("--daily-span-by-ticker-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    lt1b = load_lt1b(Path(args.lt1b_parquet))
    daily_span = load_complete_daily(Path(args.daily_span_by_ticker_parquet))

    complete_daily = daily_span[daily_span["is_contiguous_span"]].copy()
    compare = lt1b.merge(
        complete_daily[
            [
                c
                for c in [
                    "ticker",
                    "is_contiguous_span",
                    "start_year_observed",
                    "end_year_observed",
                    "expected_years_in_span",
                    "missing_years_in_span_count",
                ]
                if c in complete_daily.columns
            ]
        ],
        on="ticker",
        how="left",
    )
    compare["has_complete_daily"] = compare["is_contiguous_span"].fillna(False).astype(bool)
    compare["coverage_status"] = compare["has_complete_daily"].map(
        lambda x: "HAS_COMPLETE_DAILY" if bool(x) else "MISSING_COMPLETE_DAILY"
    )

    missing = compare[~compare["has_complete_daily"]].copy()
    covered = compare[compare["has_complete_daily"]].copy()

    summary = {
        "audited_at_utc": utc_now(),
        "lt1b_tickers_total": int(lt1b["ticker"].nunique()),
        "complete_daily_tickers_total": int(complete_daily["ticker"].nunique()),
        "lt1b_with_complete_daily": int(covered["ticker"].nunique()),
        "lt1b_missing_complete_daily": int(missing["ticker"].nunique()),
        "pct_lt1b_with_complete_daily": round(
            100.0 * float(covered["ticker"].nunique()) / max(int(lt1b["ticker"].nunique()), 1), 4
        ),
        "pct_lt1b_missing_complete_daily": round(
            100.0 * float(missing["ticker"].nunique()) / max(int(lt1b["ticker"].nunique()), 1), 4
        ),
        "inputs": {
            "lt1b_parquet": str(args.lt1b_parquet),
            "daily_span_by_ticker_parquet": str(args.daily_span_by_ticker_parquet),
        },
        "outdir": str(outdir),
    }

    compare_parquet = outdir / "lt1b_vs_complete_daily.parquet"
    compare_csv = outdir / "lt1b_vs_complete_daily.csv"
    missing_parquet = outdir / "lt1b_missing_complete_daily.parquet"
    missing_csv = outdir / "lt1b_missing_complete_daily.csv"
    covered_parquet = outdir / "lt1b_with_complete_daily.parquet"
    covered_csv = outdir / "lt1b_with_complete_daily.csv"
    summary_json = outdir / "lt1b_vs_complete_daily_summary.json"

    compare.to_parquet(compare_parquet, index=False)
    compare.to_csv(compare_csv, index=False)
    missing.to_parquet(missing_parquet, index=False)
    missing.to_csv(missing_csv, index=False)
    covered.to_parquet(covered_parquet, index=False)
    covered.to_csv(covered_csv, index=False)
    summary_json.write_text(
        json.dumps(
            {
                **summary,
                "outputs": {
                    "compare_parquet": str(compare_parquet),
                    "compare_csv": str(compare_csv),
                    "missing_parquet": str(missing_parquet),
                    "missing_csv": str(missing_csv),
                    "covered_parquet": str(covered_parquet),
                    "covered_csv": str(covered_csv),
                    "summary_json": str(summary_json),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                **summary,
                "outputs": {
                    "compare_parquet": str(compare_parquet),
                    "missing_parquet": str(missing_parquet),
                    "covered_parquet": str(covered_parquet),
                    "summary_json": str(summary_json),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
