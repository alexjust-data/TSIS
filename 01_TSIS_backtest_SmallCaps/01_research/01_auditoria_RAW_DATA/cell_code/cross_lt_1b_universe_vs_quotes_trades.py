from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


TARGET_FP = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
QUOTES_TXT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean\inputs\quotes_final_file_paths_v2.txt"
)
TRADES_TXT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\trades_ticks_prod_2005_2026\inputs\trades_ticks_final_file_paths.txt"
)

RUN_ID = globals().get(
    "RUN_ID",
    datetime.now().strftime("%Y%m%d_lt_1b_quotes_trades_cross"),
)
OUTDIR = Path(
    globals().get(
        "OUTDIR",
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\universe_coverage_lt_1b\{RUN_ID}",
    )
)


def load_target_universe(fp: Path) -> pd.DataFrame:
    df = pd.read_parquet(fp).copy()
    if "ticker" not in df.columns:
        raise ValueError(f"Missing ticker column in {fp}")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df = df.dropna(subset=["ticker"])
    df = df[df["ticker"] != ""]
    return df.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)


def extract_tickers_from_paths(txt_path: Path, kind: str) -> pd.DataFrame:
    lines = txt_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if kind == "quotes":
        pattern = re.compile(
            r"^[A-Za-z]:\\quotes\\([^\\]+)\\year=\d{4}\\month=\d{2}\\day=.*\\quotes\.parquet$",
            re.IGNORECASE,
        )
    elif kind == "trades":
        pattern = re.compile(
            r"^[A-Za-z]:\\trades_ticks_prod_2005_2026\\([^\\]+)\\year=\d{4}\\month=\d{2}\\day=.*\\market\.parquet$",
            re.IGNORECASE,
        )
    else:
        raise ValueError(f"Unsupported kind: {kind}")

    tickers: set[str] = set()
    for line in lines:
        item = line.strip()
        if not item:
            continue
        match = pattern.match(item)
        if match:
            tickers.add(match.group(1).strip().upper())

    return pd.DataFrame({"ticker": sorted(tickers)})


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
    OUTDIR.mkdir(parents=True, exist_ok=True)

    target_df = load_target_universe(TARGET_FP)
    quotes_df = extract_tickers_from_paths(QUOTES_TXT, "quotes")
    trades_df = extract_tickers_from_paths(TRADES_TXT, "trades")

    target = set(target_df["ticker"])
    quotes_have = set(quotes_df["ticker"])
    trades_have = set(trades_df["ticker"])

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
        "run_id": RUN_ID,
        "inputs": {
            "target_fp": str(TARGET_FP),
            "quotes_txt": str(QUOTES_TXT),
            "trades_txt": str(TRADES_TXT),
        },
        "outputs": {
            "outdir": str(OUTDIR),
            "coverage_matrix_csv": str(OUTDIR / "lt_1b_target_coverage_matrix.csv"),
            "coverage_matrix_parquet": str(OUTDIR / "lt_1b_target_coverage_matrix.parquet"),
            "summary_json": str(OUTDIR / "summary.json"),
        },
        "metrics": {
            "target_universe_tickers": len(target),
            "quotes_inventory_tickers": len(quotes_have),
            "trades_inventory_tickers": len(trades_have),
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

    save_ticker_list(OUTDIR / "quotes_missing.csv", quotes_missing)
    save_ticker_list(OUTDIR / "trades_missing.csv", trades_missing)
    save_ticker_list(OUTDIR / "have_both.csv", have_both)
    save_ticker_list(OUTDIR / "quotes_only.csv", quotes_only)
    save_ticker_list(OUTDIR / "trades_only.csv", trades_only)
    save_ticker_list(OUTDIR / "missing_both.csv", missing_both)

    coverage_df.to_csv(OUTDIR / "lt_1b_target_coverage_matrix.csv", index=False)
    coverage_df.to_parquet(OUTDIR / "lt_1b_target_coverage_matrix.parquet", index=False)
    (OUTDIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=== SUMMARY ===")
    print(json.dumps(summary["metrics"], indent=2, ensure_ascii=False))
    print("\n=== COVERAGE CLASS COUNTS ===")
    print(coverage_df["coverage_class"].value_counts(dropna=False).to_string())
    print(f"\nSaved to: {OUTDIR}")


if __name__ == "__main__":
    main()
