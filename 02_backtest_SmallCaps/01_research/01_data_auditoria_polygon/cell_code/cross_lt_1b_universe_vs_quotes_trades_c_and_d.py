from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


def normalize_ticker_series(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.upper()


def load_target_universe(fp: Path) -> pd.DataFrame:
    df = pd.read_parquet(fp).copy()
    if "ticker" not in df.columns:
        raise ValueError(f"Missing ticker column in {fp}")
    df["ticker"] = normalize_ticker_series(df["ticker"])
    df = df.dropna(subset=["ticker"])
    df = df[df["ticker"] != ""]
    return df.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)


def load_inventory_tickers(fp: Path) -> set[str]:
    df = pd.read_csv(fp).copy()
    if "ticker" not in df.columns:
        raise ValueError(f"Missing ticker column in {fp}")
    s = normalize_ticker_series(df["ticker"]).dropna()
    s = s[s != ""]
    return set(s.drop_duplicates().tolist())


def classify_coverage(has_quotes: bool, has_trades: bool) -> str:
    if has_quotes and has_trades:
        return "have_both"
    if has_quotes and not has_trades:
        return "quotes_only"
    if (not has_quotes) and has_trades:
        return "trades_only"
    return "missing_both"


def save_ticker_list(path: Path, tickers: list[str]) -> None:
    pd.DataFrame({"ticker": tickers}).to_csv(path, index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--target",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    )
    ap.add_argument(
        "--quotes-c-inventory",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_c_vs_d_inventory\20260328_091257_scan_quotes_c_vs_d_inventory\quotes_c_inventory.csv",
    )
    ap.add_argument(
        "--quotes-d-inventory",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_c_vs_d_inventory\20260328_091257_scan_quotes_c_vs_d_inventory\quotes_d_inventory.csv",
    )
    ap.add_argument(
        "--trades-c-inventory",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_c_vs_d_inventory\20260328_204152_scan_trades_c_vs_d_inventory\trades_c_inventory.csv",
    )
    ap.add_argument(
        "--trades-d-inventory",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_c_vs_d_inventory\20260328_204152_scan_trades_c_vs_d_inventory\trades_d_inventory.csv",
    )
    ap.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d_%H%M%S_lt_1b_quotes_trades_cross_cd"))
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    target_fp = Path(args.target)
    quotes_c_inventory = Path(args.quotes_c_inventory)
    quotes_d_inventory = Path(args.quotes_d_inventory)
    trades_c_inventory = Path(args.trades_c_inventory)
    trades_d_inventory = Path(args.trades_d_inventory)

    for fp in [target_fp, quotes_c_inventory, quotes_d_inventory, trades_c_inventory, trades_d_inventory]:
        if not fp.exists():
            raise FileNotFoundError(fp)

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\universe_coverage_lt_1b\{args.run_id}"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    target_df = load_target_universe(target_fp)
    quotes_c = load_inventory_tickers(quotes_c_inventory)
    quotes_d = load_inventory_tickers(quotes_d_inventory)
    trades_c = load_inventory_tickers(trades_c_inventory)
    trades_d = load_inventory_tickers(trades_d_inventory)

    target = set(target_df["ticker"])
    quotes_have = quotes_c | quotes_d
    trades_have = trades_c | trades_d

    quotes_missing = sorted(target - quotes_have)
    trades_missing = sorted(target - trades_have)
    have_both = sorted(target & quotes_have & trades_have)
    quotes_only = sorted((target & quotes_have) - trades_have)
    trades_only = sorted((target & trades_have) - quotes_have)
    missing_both = sorted(target - (quotes_have | trades_have))

    coverage_df = target_df.copy()
    coverage_df["has_quotes"] = coverage_df["ticker"].isin(quotes_have)
    coverage_df["has_trades"] = coverage_df["ticker"].isin(trades_have)
    coverage_df["coverage_class"] = coverage_df.apply(
        lambda row: classify_coverage(bool(row["has_quotes"]), bool(row["has_trades"])),
        axis=1,
    )

    summary = {
        "run_id": args.run_id,
        "inputs": {
            "target_fp": str(target_fp),
            "quotes_c_inventory": str(quotes_c_inventory),
            "quotes_d_inventory": str(quotes_d_inventory),
            "trades_c_inventory": str(trades_c_inventory),
            "trades_d_inventory": str(trades_d_inventory),
        },
        "outputs": {
            "outdir": str(outdir),
            "coverage_matrix_csv": str(outdir / "lt_1b_target_coverage_matrix.csv"),
            "coverage_matrix_parquet": str(outdir / "lt_1b_target_coverage_matrix.parquet"),
            "summary_json": str(outdir / "summary.json"),
        },
        "metrics": {
            "target_universe_tickers": len(target),
            "quotes_inventory_tickers_c": len(quotes_c),
            "quotes_inventory_tickers_d": len(quotes_d),
            "quotes_inventory_tickers_total": len(quotes_have),
            "trades_inventory_tickers_c": len(trades_c),
            "trades_inventory_tickers_d": len(trades_d),
            "trades_inventory_tickers_total": len(trades_have),
            "target_with_quotes": len(target & quotes_have),
            "target_with_trades": len(target & trades_have),
            "have_both": len(have_both),
            "quotes_only": len(quotes_only),
            "trades_only": len(trades_only),
            "quotes_missing": len(quotes_missing),
            "trades_missing": len(trades_missing),
            "missing_both": len(missing_both),
        },
        "coverage_class_counts": coverage_df["coverage_class"].value_counts(dropna=False).to_dict(),
    }

    save_ticker_list(outdir / "quotes_missing.csv", quotes_missing)
    save_ticker_list(outdir / "trades_missing.csv", trades_missing)
    save_ticker_list(outdir / "have_both.csv", have_both)
    save_ticker_list(outdir / "quotes_only.csv", quotes_only)
    save_ticker_list(outdir / "trades_only.csv", trades_only)
    save_ticker_list(outdir / "missing_both.csv", missing_both)

    coverage_df.to_csv(outdir / "lt_1b_target_coverage_matrix.csv", index=False)
    coverage_df.to_parquet(outdir / "lt_1b_target_coverage_matrix.parquet", index=False)
    (outdir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=== SUMMARY ===")
    print(json.dumps(summary["metrics"], indent=2, ensure_ascii=False))
    print("\n=== COVERAGE CLASS COUNTS ===")
    print(coverage_df["coverage_class"].value_counts(dropna=False).to_string())
    print(f"\nSaved to: {outdir}")


if __name__ == "__main__":
    main()
