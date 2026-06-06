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
            / f"{stamp}_problematic57_cross_1m_quotes_trades"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_problematic(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Problematic parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError("Missing ticker column in problematic parquet")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    return df[df["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)


def load_tasks(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Tasks parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "year"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Missing required columns in tasks parquet: {required}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ticker", "year"]).copy()
    df["year"] = df["year"].astype(int)
    return df


def load_daily_span(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Daily span parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError("Missing ticker column in daily span parquet")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    return df


def load_inventory_by_ticker(path: Path, prefix: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory-by-ticker parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError(f"Missing ticker column in {path}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    keep = ["ticker", "files_total", "task_keys", "roots_present", "date_min", "date_max", "bytes_total"]
    df = df[[c for c in keep if c in df.columns]].copy()
    rename_map = {c: f"{prefix}_{c}" for c in df.columns if c != "ticker"}
    return df.rename(columns=rename_map)


def scan_minute_root_for_tickers(root: Path, tickers: list[str]) -> pd.DataFrame:
    records: list[dict] = []
    for ticker in tickers:
        base = root / f"ticker={ticker}"
        years: list[int] = []
        files_total = 0
        if base.exists():
            for yd in base.glob("year=*"):
                if yd.is_dir():
                    try:
                        years.append(int(yd.name.split("=", 1)[1]))
                    except Exception:
                        pass
                    files_total += sum(1 for _ in yd.rglob("*.parquet"))
        records.append(
            {
                "ticker": ticker,
                "in_ohlcv_1m": bool(base.exists()),
                "minute_year_min": min(years) if years else None,
                "minute_year_max": max(years) if years else None,
                "minute_years_count": len(sorted(set(years))),
                "minute_files_total": int(files_total),
            }
        )
    return pd.DataFrame(records)


def build_missing_years_summary(tasks: pd.DataFrame) -> pd.DataFrame:
    out = (
        tasks.groupby("ticker", dropna=False)
        .agg(
            daily_missing_year_rows=("year", "size"),
            daily_missing_years=("year", lambda s: sorted(pd.Series(s).dropna().astype(int).unique().tolist())),
            daily_missing_year_min=("year", "min"),
            daily_missing_year_max=("year", "max"),
        )
        .reset_index()
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare the 57 really problematic daily tickers across 1m, quotes, and trades")
    ap.add_argument("--problematic-parquet", required=True)
    ap.add_argument("--tasks-parquet", required=True)
    ap.add_argument("--daily-span-by-ticker-parquet", required=True)
    ap.add_argument("--minute-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--quotes-by-ticker-parquet", required=True)
    ap.add_argument("--trades-by-ticker-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    problematic = load_problematic(Path(args.problematic_parquet))
    tasks = load_tasks(Path(args.tasks_parquet))
    daily_span = load_daily_span(Path(args.daily_span_by_ticker_parquet))
    quotes = load_inventory_by_ticker(Path(args.quotes_by_ticker_parquet), "quotes")
    trades = load_inventory_by_ticker(Path(args.trades_by_ticker_parquet), "trades")

    tickers = sorted(problematic["ticker"].unique().tolist())
    minute = scan_minute_root_for_tickers(Path(args.minute_root), tickers)
    missing_years = build_missing_years_summary(tasks[tasks["ticker"].isin(tickers)].copy())

    daily_keep = [
        "ticker",
        "start_year_observed",
        "end_year_observed",
        "unique_years_observed",
        "expected_years_in_span",
        "missing_years_in_span_count",
        "missing_years_in_span",
        "is_contiguous_span",
    ]
    daily_keep = [c for c in daily_keep if c in daily_span.columns]
    daily_span = daily_span[daily_keep].copy()

    compare = problematic.merge(missing_years, on="ticker", how="left")
    compare = compare.merge(daily_span, on="ticker", how="left")
    compare = compare.merge(minute, on="ticker", how="left")
    compare = compare.merge(quotes, on="ticker", how="left")
    compare = compare.merge(trades, on="ticker", how="left")

    compare["in_quotes"] = compare["quotes_files_total"].fillna(0).gt(0) if "quotes_files_total" in compare.columns else False
    compare["in_trades"] = compare["trades_files_total"].fillna(0).gt(0) if "trades_files_total" in compare.columns else False

    compare["coverage_signature"] = compare.apply(
        lambda r: "|".join(
            [
                "1m" if bool(r.get("in_ohlcv_1m")) else "no1m",
                "quotes" if bool(r.get("in_quotes")) else "noquotes",
                "trades" if bool(r.get("in_trades")) else "notrades",
            ]
        ),
        axis=1,
    )

    by_signature = (
        compare["coverage_signature"]
        .value_counts(dropna=False)
        .rename_axis("coverage_signature")
        .reset_index(name="tickers")
        .sort_values(["tickers", "coverage_signature"], ascending=[False, True])
        .reset_index(drop=True)
    )

    compare = compare.sort_values(
        ["daily_missing_year_rows", "ticker"],
        ascending=[False, True],
    ).reset_index(drop=True)

    compare_parquet = outdir / "problematic57_cross_1m_quotes_trades.parquet"
    compare_csv = outdir / "problematic57_cross_1m_quotes_trades.csv"
    signature_parquet = outdir / "problematic57_cross_1m_quotes_trades_by_signature.parquet"
    signature_csv = outdir / "problematic57_cross_1m_quotes_trades_by_signature.csv"
    summary_json = outdir / "problematic57_cross_1m_quotes_trades_summary.json"

    compare.to_parquet(compare_parquet, index=False)
    compare.to_csv(compare_csv, index=False)
    by_signature.to_parquet(signature_parquet, index=False)
    by_signature.to_csv(signature_csv, index=False)

    summary = {
        "audited_at_utc": utc_now(),
        "problematic57_tickers": int(len(tickers)),
        "with_ohlcv_1m": int(compare["in_ohlcv_1m"].fillna(False).astype(bool).sum()),
        "with_quotes": int(compare["in_quotes"].fillna(False).astype(bool).sum()),
        "with_trades": int(compare["in_trades"].fillna(False).astype(bool).sum()),
        "without_ohlcv_1m": int((~compare["in_ohlcv_1m"].fillna(False).astype(bool)).sum()),
        "without_quotes": int((~compare["in_quotes"].fillna(False).astype(bool)).sum()),
        "without_trades": int((~compare["in_trades"].fillna(False).astype(bool)).sum()),
        "coverage_signature_counts": {
            str(r["coverage_signature"]): int(r["tickers"]) for r in by_signature.to_dict(orient="records")
        },
        "inputs": {
            "problematic_parquet": str(args.problematic_parquet),
            "tasks_parquet": str(args.tasks_parquet),
            "daily_span_by_ticker_parquet": str(args.daily_span_by_ticker_parquet),
            "minute_root": str(args.minute_root),
            "quotes_by_ticker_parquet": str(args.quotes_by_ticker_parquet),
            "trades_by_ticker_parquet": str(args.trades_by_ticker_parquet),
        },
        "outputs": {
            "compare_parquet": str(compare_parquet),
            "compare_csv": str(compare_csv),
            "signature_parquet": str(signature_parquet),
            "signature_csv": str(signature_csv),
            "summary_json": str(summary_json),
        },
        "outdir": str(outdir),
    }
    summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
