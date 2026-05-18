from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def ticker_set_from_input(path: Path) -> list[str]:
    df = pd.read_parquet(path, columns=["ticker"])
    s = df["ticker"].astype("string").str.strip().dropna().str.upper()
    s = s[s != ""]
    return sorted(s.drop_duplicates().tolist())


def ticker_dirs(root: Path) -> list[str]:
    if not root.exists():
        raise FileNotFoundError(f"No existe root: {root}")
    out: list[str] = []
    for p in root.glob("ticker=*"):
        if p.is_dir():
            out.append(p.name.split("=", 1)[1])
    return sorted(set(out))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input-parquet",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026_upper.parquet",
    )
    ap.add_argument("--daily-root", default=r"D:\ohlcv_daily")
    ap.add_argument("--minute-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--daily-audit-csv", default="")
    ap.add_argument("--minute-audit-csv", default="")
    ap.add_argument("--minute-errors-csv", default="")
    ap.add_argument("--top-n", type=int, default=50)
    args = ap.parse_args()

    input_parquet = Path(args.input_parquet)
    daily_root = Path(args.daily_root)
    minute_root = Path(args.minute_root)
    daily_audit_csv = Path(args.daily_audit_csv) if args.daily_audit_csv else daily_root / "_run" / "download_ohlcv_daily_v1.ticker_audit.csv"
    minute_audit_csv = Path(args.minute_audit_csv) if args.minute_audit_csv else minute_root / "_run" / "download_ohlcv_minute_v1.ticker_audit.csv"
    minute_errors_csv = Path(args.minute_errors_csv) if args.minute_errors_csv else minute_root / "_run" / "download_ohlcv_minute_v1.errors.csv"

    for p in [input_parquet, daily_audit_csv, minute_audit_csv]:
        if not p.exists():
            raise FileNotFoundError(p)

    input_tickers = ticker_set_from_input(input_parquet)
    daily_dirs = ticker_dirs(daily_root)
    minute_dirs = ticker_dirs(minute_root)

    daily_audit = pd.read_csv(daily_audit_csv)
    minute_audit = pd.read_csv(minute_audit_csv)
    minute_errors = pd.read_csv(minute_errors_csv) if minute_errors_csv.exists() else pd.DataFrame()

    input_set = set(input_tickers)
    daily_set = set(daily_dirs)
    minute_set = set(minute_dirs)

    missing_in_daily = sorted(input_set - daily_set)
    missing_in_minute = sorted(input_set - minute_set)
    extra_in_daily = sorted(daily_set - input_set)
    extra_in_minute = sorted(minute_set - input_set)
    missing_minute_vs_daily = sorted(daily_set - minute_set)

    minute_missing_audit = minute_audit[minute_audit["ticker"].isin(missing_in_minute)].copy()

    minute_error_causes = pd.DataFrame()
    if not minute_missing_audit.empty:
        minute_error_causes = (
            minute_missing_audit.groupby(["status", "http_status", "msg"], dropna=False)
            .size()
            .reset_index(name="count")
            .sort_values(["count", "http_status", "msg"], ascending=[False, True, True])
            .reset_index(drop=True)
        )

    summary = {
        "input_unique_tickers": len(input_tickers),
        "daily_dir_tickers": len(daily_dirs),
        "minute_dir_tickers": len(minute_dirs),
        "missing_in_daily": len(missing_in_daily),
        "missing_in_minute": len(missing_in_minute),
        "extra_in_daily": len(extra_in_daily),
        "extra_in_minute": len(extra_in_minute),
        "missing_minute_vs_daily": len(missing_minute_vs_daily),
    }

    print("=== PATHS USADOS ===")
    print(f"input_parquet: {input_parquet}")
    print(f"daily_root: {daily_root}")
    print(f"minute_root: {minute_root}")
    print(f"daily_audit_csv: {daily_audit_csv}")
    print(f"minute_audit_csv: {minute_audit_csv}")
    print(f"minute_errors_csv: {minute_errors_csv}")

    print("\n=== RESUMEN ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    print("\n=== AUDIT DAILY STATUS ===")
    print(daily_audit["status"].value_counts(dropna=False).to_string())

    print("\n=== AUDIT MINUTE STATUS ===")
    print(minute_audit["status"].value_counts(dropna=False).to_string())

    print(f"\n=== EJEMPLOS FALTANTES EN 1M (TOP {args.top_n}) ===")
    print(pd.DataFrame({"ticker": missing_in_minute[: args.top_n]}).to_string(index=False))

    print(f"\n=== EJEMPLOS FALTANTES EN DAILY (TOP {args.top_n}) ===")
    print(pd.DataFrame({"ticker": missing_in_daily[: args.top_n]}).to_string(index=False))

    print(f"\n=== INPUT vs DAILY vs MINUTE (TOP {args.top_n}) ===")
    comparison = pd.DataFrame({"ticker": input_tickers}).assign(
        in_daily=lambda x: x["ticker"].isin(daily_set),
        in_minute=lambda x: x["ticker"].isin(minute_set),
    )
    comparison = comparison[(~comparison["in_daily"]) | (~comparison["in_minute"])].head(args.top_n).reset_index(drop=True)
    print(comparison.to_string(index=False))

    print("\n=== CAUSAS DE LOS FALTANTES EN 1M ===")
    if minute_error_causes.empty:
        print("Sin causas; no hay faltantes en 1m")
    else:
        print(minute_error_causes.to_string(index=False))

    if not minute_missing_audit.empty:
        print(f"\n=== DETAIL MINUTE AUDIT PARA FALTANTES (TOP {args.top_n}) ===")
        print(minute_missing_audit.sort_values(["http_status", "ticker"]).head(args.top_n).to_string(index=False))

    if not minute_errors.empty:
        print(f"\n=== MINUTE ERRORS CSV (TOP {args.top_n}) ===")
        print(minute_errors.head(args.top_n).to_string(index=False))


if __name__ == "__main__":
    main()
