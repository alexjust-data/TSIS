from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

DEFAULT_WINDOWS = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\lt_1b_vs_ohlcv_daily_windows\20260322_202042_cross_lt_1b_vs_ohlcv_daily_windows\lt_1b_vs_ohlcv_daily_windows.parquet")
DEFAULT_OUT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_tasks")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Construye task master de quotes desde ventanas observadas en ohlcv_daily")
    ap.add_argument("--windows-parquet", default=str(DEFAULT_WINDOWS))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--only-has-ohlcv", action="store_true", default=True)
    ap.add_argument("--limit-tickers", type=int, default=0)
    return ap.parse_args()


def load_windows(path: Path, limit_tickers: int = 0) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe windows parquet: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "ohlcv_first_day", "ohlcv_last_day", "has_ohlcv_daily"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Faltan columnas en windows parquet: {sorted(missing)}")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["ohlcv_first_day"] = pd.to_datetime(df["ohlcv_first_day"], errors="coerce").dt.normalize()
    df["ohlcv_last_day"] = pd.to_datetime(df["ohlcv_last_day"], errors="coerce").dt.normalize()
    df["has_ohlcv_daily"] = df["has_ohlcv_daily"].fillna(False).astype(bool)
    df = df[df["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="first").sort_values("ticker").reset_index(drop=True)
    if limit_tickers and limit_tickers > 0:
        df = df.head(limit_tickers).copy()
    return df


def main() -> int:
    args = parse_args()
    windows_path = Path(args.windows_parquet)
    if args.outdir:
        outdir = Path(args.outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = DEFAULT_OUT_ROOT / f"{stamp}_build_quotes_lt_1b_master_from_ohlcv_windows"
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_windows(windows_path, limit_tickers=args.limit_tickers)
    src_rows = len(df)
    if args.only_has_ohlcv:
        df = df[df["has_ohlcv_daily"]].copy()

    task_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []

    total = len(df)
    for i, r in enumerate(df.itertuples(index=False), start=1):
        ticker = str(r.ticker)
        d0 = r.ohlcv_first_day
        d1 = r.ohlcv_last_day

        if pd.isna(d0) or pd.isna(d1) or d1 < d0:
            summary_rows.append({
                "ticker": ticker,
                "effective_start": pd.NaT,
                "effective_end": pd.NaT,
                "n_tasks": 0,
                "status": "SKIPPED_INVALID_WINDOW",
            })
            continue

        days = pd.bdate_range(d0, d1)
        if len(days) == 0:
            summary_rows.append({
                "ticker": ticker,
                "effective_start": d0.date().isoformat(),
                "effective_end": d1.date().isoformat(),
                "n_tasks": 0,
                "status": "SKIPPED_NO_BUSINESS_DAYS",
            })
            continue

        task_frames.append(pd.DataFrame({
            "ticker": ticker,
            "date": pd.Series(days).dt.strftime("%Y-%m-%d"),
        }))
        summary_rows.append({
            "ticker": ticker,
            "effective_start": d0.date().isoformat(),
            "effective_end": d1.date().isoformat(),
            "n_tasks": int(len(days)),
            "status": "READY",
        })

        if i == 1 or i % 250 == 0 or i == total:
            print(f"build_tasks: tickers={i}/{total}")

    tasks = pd.concat(task_frames, ignore_index=True) if task_frames else pd.DataFrame(columns=["ticker", "date"])
    tasks = tasks.drop_duplicates(subset=["ticker", "date"], keep="first").sort_values(["ticker", "date"]).reset_index(drop=True)
    summary = pd.DataFrame(summary_rows).sort_values(["status", "ticker"]).reset_index(drop=True)

    tasks_csv = outdir / "tasks_quotes_lt_1b_master.csv"
    tasks_parquet = outdir / "tasks_quotes_lt_1b_master.parquet"
    summary_csv = outdir / "tasks_quotes_lt_1b_summary_by_ticker.csv"
    manifest_json = outdir / "tasks_quotes_lt_1b_manifest.json"

    tasks.to_csv(tasks_csv, index=False)
    tasks.to_parquet(tasks_parquet, index=False)
    summary.to_csv(summary_csv, index=False)

    manifest = {
        "windows_path": str(windows_path),
        "outdir": str(outdir),
        "source_rows": int(src_rows),
        "rows_after_has_ohlcv_filter": int(len(df)),
        "tickers_in_tasks": int(tasks["ticker"].nunique()) if len(tasks) else 0,
        "tasks_total": int(len(tasks)),
        "date_min": str(tasks["date"].min()) if len(tasks) else None,
        "date_max": str(tasks["date"].max()) if len(tasks) else None,
        "only_has_ohlcv": bool(args.only_has_ohlcv),
    }
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))
    print(f"saved: {tasks_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
