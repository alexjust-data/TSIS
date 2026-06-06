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
            / f"{stamp}_problematic57_per_day_cross"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_problematic_tickers(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Problematic parquet not found: {path}")
    df = pd.read_parquet(path, columns=["ticker"]).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    out = sorted(df.loc[df["ticker"] != "", "ticker"].drop_duplicates().tolist())
    if not out:
        raise RuntimeError("No problematic tickers found")
    return out


def load_quotes_dates(path: Path, tickers: list[str]) -> pd.DataFrame:
    df = pd.read_parquet(path, columns=["ticker", "date"]).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df[df["ticker"].isin(set(tickers))].dropna(subset=["date"]).copy()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    return df.assign(in_quotes=True)


def load_trades_dates(path: Path, tickers: list[str]) -> pd.DataFrame:
    df = pd.read_parquet(path, columns=["ticker", "date"]).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df[df["ticker"].isin(set(tickers))].dropna(subset=["date"]).copy()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    return df.assign(in_trades=True)


def load_daily_dates(root: Path, tickers: list[str]) -> pd.DataFrame:
    records: list[dict] = []
    for ticker in tickers:
        base = root / f"ticker={ticker}"
        if not base.exists():
            continue
        for fp in sorted(base.glob(r"year=*\day_aggs_*.parquet")):
            try:
                d = pd.read_parquet(fp, columns=["date"]).copy()
            except Exception:
                continue
            if d.empty or "date" not in d.columns:
                continue
            s = pd.to_datetime(d["date"], errors="coerce").dt.strftime("%Y-%m-%d").dropna()
            for dt in s.drop_duplicates().tolist():
                records.append({"ticker": ticker, "date": dt, "in_daily": True})
    return pd.DataFrame(records).drop_duplicates(subset=["ticker", "date"], keep="first")


def load_minute_dates(root: Path, tickers: list[str]) -> pd.DataFrame:
    records: list[dict] = []
    for ticker in tickers:
        base = root / f"ticker={ticker}"
        if not base.exists():
            continue
        for fp in sorted(base.glob(r"year=*\month=*\minute_aggs_*.parquet")):
            try:
                d = pd.read_parquet(fp, columns=["date"]).copy()
            except Exception:
                continue
            if d.empty or "date" not in d.columns:
                continue
            s = pd.to_datetime(d["date"], errors="coerce").dt.strftime("%Y-%m-%d").dropna()
            for dt in s.drop_duplicates().tolist():
                records.append({"ticker": ticker, "date": dt, "in_1m": True})
    return pd.DataFrame(records).drop_duplicates(subset=["ticker", "date"], keep="first")


def summarize_per_ticker(panel: pd.DataFrame) -> pd.DataFrame:
    def uniq_sorted(series: pd.Series) -> list[str]:
        return sorted(pd.Series(series).dropna().astype(str).unique().tolist())

    g = (
        panel.groupby("ticker", dropna=False)
        .agg(
            dates_union_count=("date", "nunique"),
            daily_days=("in_daily", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            minute_days=("in_1m", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            quotes_days=("in_quotes", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            trades_days=("in_trades", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            daily_years=("year", lambda s: sorted(panel.loc[s.index & s.index, :].loc[panel.loc[s.index, "in_daily"].fillna(False), "year"].dropna().astype(int).unique().tolist())),
            minute_years=("year", lambda s: sorted(panel.loc[s.index, :].loc[panel.loc[s.index, "in_1m"].fillna(False), "year"].dropna().astype(int).unique().tolist())),
            quotes_years=("year", lambda s: sorted(panel.loc[s.index, :].loc[panel.loc[s.index, "in_quotes"].fillna(False), "year"].dropna().astype(int).unique().tolist())),
            trades_years=("year", lambda s: sorted(panel.loc[s.index, :].loc[panel.loc[s.index, "in_trades"].fillna(False), "year"].dropna().astype(int).unique().tolist())),
            last_daily_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_daily"].fillna(False)].max() if panel.loc[s.index, "in_daily"].fillna(False).any() else None),
            last_1m_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_1m"].fillna(False)].max() if panel.loc[s.index, "in_1m"].fillna(False).any() else None),
            last_quotes_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_quotes"].fillna(False)].max() if panel.loc[s.index, "in_quotes"].fillna(False).any() else None),
            last_trades_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_trades"].fillna(False)].max() if panel.loc[s.index, "in_trades"].fillna(False).any() else None),
            daily_missing_vs_1m=("date", lambda s: uniq_sorted(pd.Series(s)[panel.loc[s.index, "in_1m"].fillna(False) & ~panel.loc[s.index, "in_daily"].fillna(False)])),
            daily_missing_vs_quotes=("date", lambda s: uniq_sorted(pd.Series(s)[panel.loc[s.index, "in_quotes"].fillna(False) & ~panel.loc[s.index, "in_daily"].fillna(False)])),
            daily_missing_vs_trades=("date", lambda s: uniq_sorted(pd.Series(s)[panel.loc[s.index, "in_trades"].fillna(False) & ~panel.loc[s.index, "in_daily"].fillna(False)])),
            all_four_overlap_days=("date", lambda s: int((panel.loc[s.index, ["in_daily", "in_1m", "in_quotes", "in_trades"]].fillna(False).all(axis=1)).sum())),
        )
        .reset_index()
    )

    g["daily_missing_vs_1m_count"] = g["daily_missing_vs_1m"].apply(len)
    g["daily_missing_vs_quotes_count"] = g["daily_missing_vs_quotes"].apply(len)
    g["daily_missing_vs_trades_count"] = g["daily_missing_vs_trades"].apply(len)
    g["last_dates_match_all"] = (
        (g["last_daily_date"] == g["last_1m_date"])
        & (g["last_daily_date"] == g["last_quotes_date"])
        & (g["last_daily_date"] == g["last_trades_date"])
    )
    return g.sort_values(
        ["daily_missing_vs_1m_count", "daily_missing_vs_quotes_count", "daily_missing_vs_trades_count", "ticker"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def summarize_per_ticker_year(panel: pd.DataFrame) -> pd.DataFrame:
    g = (
        panel.groupby(["ticker", "year"], dropna=False)
        .agg(
            daily_days=("in_daily", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            minute_days=("in_1m", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            quotes_days=("in_quotes", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            trades_days=("in_trades", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            last_daily_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_daily"].fillna(False)].max() if panel.loc[s.index, "in_daily"].fillna(False).any() else None),
            last_1m_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_1m"].fillna(False)].max() if panel.loc[s.index, "in_1m"].fillna(False).any() else None),
            last_quotes_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_quotes"].fillna(False)].max() if panel.loc[s.index, "in_quotes"].fillna(False).any() else None),
            last_trades_date=("date", lambda s: pd.Series(s)[panel.loc[s.index, "in_trades"].fillna(False)].max() if panel.loc[s.index, "in_trades"].fillna(False).any() else None),
            daily_missing_vs_1m_count=("date", lambda s: int((panel.loc[s.index, "in_1m"].fillna(False) & ~panel.loc[s.index, "in_daily"].fillna(False)).sum())),
            daily_missing_vs_quotes_count=("date", lambda s: int((panel.loc[s.index, "in_quotes"].fillna(False) & ~panel.loc[s.index, "in_daily"].fillna(False)).sum())),
            daily_missing_vs_trades_count=("date", lambda s: int((panel.loc[s.index, "in_trades"].fillna(False) & ~panel.loc[s.index, "in_daily"].fillna(False)).sum())),
        )
        .reset_index()
    )
    g["last_dates_match_all"] = (
        (g["last_daily_date"] == g["last_1m_date"])
        & (g["last_daily_date"] == g["last_quotes_date"])
        & (g["last_daily_date"] == g["last_trades_date"])
    )
    return g.sort_values(
        ["daily_missing_vs_1m_count", "daily_missing_vs_quotes_count", "daily_missing_vs_trades_count", "ticker", "year"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Per-day comparison for the 57 problematic daily tickers across daily, 1m, quotes, and trades")
    ap.add_argument("--problematic-parquet", required=True)
    ap.add_argument("--daily-root", default=r"D:\ohlcv_daily")
    ap.add_argument("--minute-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--quotes-files-parquet", required=True)
    ap.add_argument("--trades-files-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    tickers = load_problematic_tickers(Path(args.problematic_parquet))

    daily_dates = load_daily_dates(Path(args.daily_root), tickers)
    minute_dates = load_minute_dates(Path(args.minute_root), tickers)
    quotes_dates = load_quotes_dates(Path(args.quotes_files_parquet), tickers)
    trades_dates = load_trades_dates(Path(args.trades_files_parquet), tickers)

    panel = pd.DataFrame({"ticker": pd.Series(dtype=str), "date": pd.Series(dtype=str)})
    for d in [daily_dates, minute_dates, quotes_dates, trades_dates]:
        if d is not None and not d.empty:
            panel = pd.concat([panel, d[["ticker", "date"]]], ignore_index=True)
    panel = panel.drop_duplicates(subset=["ticker", "date"], keep="first")

    panel = panel.merge(daily_dates, on=["ticker", "date"], how="left")
    panel = panel.merge(minute_dates, on=["ticker", "date"], how="left")
    panel = panel.merge(quotes_dates, on=["ticker", "date"], how="left")
    panel = panel.merge(trades_dates, on=["ticker", "date"], how="left")

    for c in ["in_daily", "in_1m", "in_quotes", "in_trades"]:
        if c not in panel.columns:
            panel[c] = False
        panel[c] = panel[c].fillna(False).astype(bool)

    panel["date"] = pd.to_datetime(panel["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    panel = panel.dropna(subset=["date"]).copy()
    panel["year"] = pd.to_datetime(panel["date"], errors="coerce").dt.year.astype("Int64")
    panel["year"] = panel["year"].astype(int)

    per_ticker = summarize_per_ticker(panel)
    per_ticker_year = summarize_per_ticker_year(panel)

    panel = panel.sort_values(["ticker", "date"], ascending=[True, True]).reset_index(drop=True)

    panel_parquet = outdir / "problematic57_per_day_panel.parquet"
    panel_csv = outdir / "problematic57_per_day_panel.csv"
    ticker_parquet = outdir / "problematic57_per_ticker_summary.parquet"
    ticker_csv = outdir / "problematic57_per_ticker_summary.csv"
    ticker_year_parquet = outdir / "problematic57_per_ticker_year_summary.parquet"
    ticker_year_csv = outdir / "problematic57_per_ticker_year_summary.csv"
    summary_json = outdir / "problematic57_per_day_cross_summary.json"

    panel.to_parquet(panel_parquet, index=False)
    panel.to_csv(panel_csv, index=False)
    per_ticker.to_parquet(ticker_parquet, index=False)
    per_ticker.to_csv(ticker_csv, index=False)
    per_ticker_year.to_parquet(ticker_year_parquet, index=False)
    per_ticker_year.to_csv(ticker_year_csv, index=False)

    summary = {
        "audited_at_utc": utc_now(),
        "problematic57_tickers": int(len(tickers)),
        "panel_rows_union_dates": int(len(panel)),
        "tickers_with_daily_missing_vs_1m": int(per_ticker["daily_missing_vs_1m_count"].gt(0).sum()),
        "tickers_with_daily_missing_vs_quotes": int(per_ticker["daily_missing_vs_quotes_count"].gt(0).sum()),
        "tickers_with_daily_missing_vs_trades": int(per_ticker["daily_missing_vs_trades_count"].gt(0).sum()),
        "tickers_last_dates_match_all": int(per_ticker["last_dates_match_all"].fillna(False).sum()),
        "inputs": {
            "problematic_parquet": str(args.problematic_parquet),
            "daily_root": str(args.daily_root),
            "minute_root": str(args.minute_root),
            "quotes_files_parquet": str(args.quotes_files_parquet),
            "trades_files_parquet": str(args.trades_files_parquet),
        },
        "outputs": {
            "panel_parquet": str(panel_parquet),
            "panel_csv": str(panel_csv),
            "ticker_parquet": str(ticker_parquet),
            "ticker_csv": str(ticker_csv),
            "ticker_year_parquet": str(ticker_year_parquet),
            "ticker_year_csv": str(ticker_year_csv),
            "summary_json": str(summary_json),
        },
        "outdir": str(outdir),
    }
    summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
