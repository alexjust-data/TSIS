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
            / f"{stamp}_lt1b_really_problematic_download_tasks"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_problematic_tickers(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Problematic parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError(f"Missing ticker column in {path}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    return df[df["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)


def load_missing_audit(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing-audit parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "missing_year", "classification"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Missing required columns in {path}: {required}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["missing_year"] = pd.to_numeric(df["missing_year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ticker", "missing_year"]).copy()
    df["missing_year"] = df["missing_year"].astype(int)
    return df


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build ticker-year download tasks for really problematic LT1B daily gaps"
    )
    ap.add_argument("--problematic-parquet", required=True)
    ap.add_argument("--missing-audit-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    problematic = load_problematic_tickers(Path(args.problematic_parquet))
    missing_audit = load_missing_audit(Path(args.missing_audit_parquet))

    keep_classes = {"unexpected_missing", "unexpected_missing_calendar_unavailable"}
    tasks = missing_audit[
        missing_audit["ticker"].isin(set(problematic["ticker"]))
        & missing_audit["classification"].isin(keep_classes)
    ].copy()

    tasks["year"] = tasks["missing_year"].astype(int)
    tasks["task_key"] = tasks["ticker"] + "|" + tasks["year"].astype(str)
    tasks["date_from"] = tasks["year"].astype(str) + "-01-01"
    tasks["date_to"] = tasks["year"].astype(str) + "-12-31"
    tasks["download_reason"] = "lt1b_really_problematic_unexpected_missing_daily_year"
    tasks["target_path"] = tasks.apply(
        lambda r: rf"D:\ohlcv_daily\ticker={r['ticker']}\year={int(r['year'])}\day_aggs_{r['ticker']}_{int(r['year'])}.parquet",
        axis=1,
    )

    cols = [
        "task_key",
        "ticker",
        "year",
        "date_from",
        "date_to",
        "download_reason",
        "classification",
        "expected_year_start",
        "expected_year_end",
        "expected_session_count_in_year",
        "target_path",
    ]
    cols = [c for c in cols if c in tasks.columns]
    tasks = tasks[cols].sort_values(["ticker", "year"], ascending=[True, True]).reset_index(drop=True)

    tickers_only = tasks[["ticker"]].drop_duplicates().sort_values("ticker").reset_index(drop=True)

    tasks_parquet = outdir / "lt1b_really_problematic_daily_download_tasks.parquet"
    tasks_csv = outdir / "lt1b_really_problematic_daily_download_tasks.csv"
    tickers_parquet = outdir / "lt1b_really_problematic_daily_download_tickers.parquet"
    tickers_csv = outdir / "lt1b_really_problematic_daily_download_tickers.csv"
    summary_json = outdir / "lt1b_really_problematic_daily_download_tasks_summary.json"

    tasks.to_parquet(tasks_parquet, index=False)
    tasks.to_csv(tasks_csv, index=False)
    tickers_only.to_parquet(tickers_parquet, index=False)
    tickers_only.to_csv(tickers_csv, index=False)

    summary = {
        "built_at_utc": utc_now(),
        "problematic_tickers_input": int(problematic["ticker"].nunique()),
        "download_task_rows": int(len(tasks)),
        "download_task_tickers": int(tickers_only["ticker"].nunique()),
        "class_counts": tasks["classification"].value_counts(dropna=False).to_dict(),
        "inputs": {
            "problematic_parquet": str(args.problematic_parquet),
            "missing_audit_parquet": str(args.missing_audit_parquet),
        },
        "outputs": {
            "tasks_parquet": str(tasks_parquet),
            "tasks_csv": str(tasks_csv),
            "tickers_parquet": str(tickers_parquet),
            "tickers_csv": str(tickers_csv),
            "summary_json": str(summary_json),
        },
        "outdir": str(outdir),
    }
    summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
