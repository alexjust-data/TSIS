from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


QUOTES_PATTERN_DD = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<day>\d{2})[\\/]+quotes\.parquet$",
    re.IGNORECASE,
)
QUOTES_PATTERN_ISO = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<date>\d{4}-\d{2}-\d{2})[\\/]+quotes\.parquet$",
    re.IGNORECASE,
)
TRADES_PATTERN_DD = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<day>\d{2})[\\/]+market\.parquet$",
    re.IGNORECASE,
)
TRADES_PATTERN_ISO = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<date>\d{4}-\d{2}-\d{2})[\\/]+market\.parquet$",
    re.IGNORECASE,
)


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def parse_relpath(relpath: str, dataset: str) -> tuple[str, str] | None:
    rel = relpath.replace("/", "\\")
    if dataset == "quotes":
        patterns = (QUOTES_PATTERN_ISO, QUOTES_PATTERN_DD)
        leaf_kind = "quotes"
    else:
        patterns = (TRADES_PATTERN_ISO, TRADES_PATTERN_DD)
        leaf_kind = "trades"

    for pat in patterns:
        m = pat.match(rel)
        if not m:
            continue
        ticker = str(m.group("ticker")).upper().strip()
        if "date" in m.groupdict() and m.group("date"):
            date = str(m.group("date"))
        else:
            date = f"{m.group('year')}-{m.group('month')}-{m.group('day')}"
        return ticker, date

    return None


def scan_root(root: Path, dataset: str, location: str, progress_every: int = 100000) -> pd.DataFrame:
    target = "quotes.parquet" if dataset == "quotes" else "market.parquet"
    rows: list[dict] = []
    count = 0
    matched = 0

    for p in root.rglob(target):
        count += 1
        try:
            rel = str(p.relative_to(root))
        except Exception:
            rel = p.name
        parsed = parse_relpath(rel, dataset)
        if parsed is None:
            continue
        ticker, date = parsed
        rows.append(
            {
                "dataset": dataset,
                "location": location,
                "ticker": ticker,
                "date": date,
                "task_key": f"{ticker}|{date}",
                "file": str(p),
            }
        )
        matched += 1
        if matched % progress_every == 0:
            print(f"scan_{dataset}_{location}: matched={matched}")

    print(f"scan_{dataset}_{location}: files_seen={count} matched={matched}")
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["ticker", "date", "file"]).reset_index(drop=True)
    return df


def summarize_keys(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "rows": 0,
            "unique_task_keys": 0,
            "tickers": 0,
            "date_min": None,
            "date_max": None,
        }
    return {
        "rows": int(len(df)),
        "unique_task_keys": int(df["task_key"].nunique()),
        "tickers": int(df["ticker"].nunique()),
        "date_min": str(df["date"].min()),
        "date_max": str(df["date"].max()),
    }


def read_universe(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, usecols=["ticker", "date"])
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = df["date"].astype(str).str.slice(0, 10)
    df["task_key"] = df["ticker"] + "|" + df["date"]
    return df.drop_duplicates(["task_key"]).sort_values(["ticker", "date"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quotes-c-root", default=r"C:\TSIS_Data\data\quotes")
    ap.add_argument("--quotes-d-root", default=r"D:\quotes")
    ap.add_argument("--trades-c-root", default=r"C:\TSIS_Data\data\trades_ticks_prod_2005_2026")
    ap.add_argument("--trades-d-root", default=r"D:\trades_ticks_prod_2005_2026")
    ap.add_argument(
        "--universe-csv",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_tasks\20260322_221029_build_quotes_lt_1b_master_from_ohlcv_windows\tasks_quotes_lt_1b_master.csv",
    )
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    quotes_c_root = Path(args.quotes_c_root)
    quotes_d_root = Path(args.quotes_d_root)
    trades_c_root = Path(args.trades_c_root)
    trades_d_root = Path(args.trades_d_root)
    universe_csv = Path(args.universe_csv)

    for p in (quotes_c_root, quotes_d_root, trades_c_root, trades_d_root, universe_csv):
        if not p.exists():
            raise SystemExit(f"path not found: {p}")

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_vs_trades_total_coverage\{utc_stamp()}_compare_quotes_vs_trades_total_coverage"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    q_c = scan_root(quotes_c_root, "quotes", "C")
    q_d = scan_root(quotes_d_root, "quotes", "D")
    t_c = scan_root(trades_c_root, "trades", "C")
    t_d = scan_root(trades_d_root, "trades", "D")

    quotes_all = pd.concat([q_c, q_d], ignore_index=True) if not q_c.empty or not q_d.empty else pd.DataFrame(columns=["dataset", "location", "ticker", "date", "task_key", "file"])
    trades_all = pd.concat([t_c, t_d], ignore_index=True) if not t_c.empty or not t_d.empty else pd.DataFrame(columns=["dataset", "location", "ticker", "date", "task_key", "file"])

    quotes_keys = quotes_all[["task_key", "ticker", "date"]].drop_duplicates().copy()
    trades_keys = trades_all[["task_key", "ticker", "date"]].drop_duplicates().copy()
    universe = read_universe(universe_csv)

    quotes_keys["has_quotes_total"] = True
    trades_keys["has_trades_total"] = True

    coverage = universe.merge(quotes_keys, on=["task_key", "ticker", "date"], how="left")
    coverage = coverage.merge(trades_keys, on=["task_key", "ticker", "date"], how="left")
    coverage["has_quotes_total"] = coverage["has_quotes_total"].fillna(False).astype(bool)
    coverage["has_trades_total"] = coverage["has_trades_total"].fillna(False).astype(bool)
    coverage["coverage_status"] = "HAS_BOTH"
    coverage.loc[coverage["has_quotes_total"] & ~coverage["has_trades_total"], "coverage_status"] = "ONLY_QUOTES"
    coverage.loc[~coverage["has_quotes_total"] & coverage["has_trades_total"], "coverage_status"] = "ONLY_TRADES"
    coverage.loc[~coverage["has_quotes_total"] & ~coverage["has_trades_total"], "coverage_status"] = "MISSING_BOTH"

    combined = quotes_keys.merge(trades_keys, on=["task_key", "ticker", "date"], how="outer")
    combined["has_quotes_total"] = combined["has_quotes_total"].fillna(False).astype(bool)
    combined["has_trades_total"] = combined["has_trades_total"].fillna(False).astype(bool)
    combined["universe_member"] = combined["task_key"].isin(set(universe["task_key"]))
    combined["dataset_compare_status"] = "IN_BOTH_QUOTES_AND_TRADES"
    combined.loc[combined["has_quotes_total"] & ~combined["has_trades_total"], "dataset_compare_status"] = "ONLY_QUOTES_TOTAL"
    combined.loc[~combined["has_quotes_total"] & combined["has_trades_total"], "dataset_compare_status"] = "ONLY_TRADES_TOTAL"
    combined = combined.sort_values(["ticker", "date"]).reset_index(drop=True)

    coverage_csv = outdir / "quotes_vs_trades_universe_coverage.csv"
    coverage_parquet = outdir / "quotes_vs_trades_universe_coverage.parquet"
    combined_csv = outdir / "quotes_vs_trades_total_comparison.csv"
    combined_parquet = outdir / "quotes_vs_trades_total_comparison.parquet"
    both_csv = outdir / "quotes_and_trades_in_both.csv"
    only_quotes_csv = outdir / "quotes_only_total.csv"
    only_trades_csv = outdir / "trades_only_total.csv"
    missing_both_csv = outdir / "missing_both_from_universe.csv"
    summary_json = outdir / "quotes_vs_trades_total_coverage_summary.json"

    coverage.to_csv(coverage_csv, index=False)
    coverage.to_parquet(coverage_parquet, index=False)
    combined.to_csv(combined_csv, index=False)
    combined.to_parquet(combined_parquet, index=False)
    coverage.loc[coverage["coverage_status"] == "HAS_BOTH"].to_csv(both_csv, index=False)
    coverage.loc[coverage["coverage_status"] == "ONLY_QUOTES"].to_csv(only_quotes_csv, index=False)
    coverage.loc[coverage["coverage_status"] == "ONLY_TRADES"].to_csv(only_trades_csv, index=False)
    coverage.loc[coverage["coverage_status"] == "MISSING_BOTH"].to_csv(missing_both_csv, index=False)

    summary = {
        "outdir": str(outdir),
        "universe_csv": str(universe_csv),
        "universe": summarize_keys(universe),
        "quotes_total": summarize_keys(quotes_keys),
        "trades_total": summarize_keys(trades_keys),
        "coverage_rows": int(len(coverage)),
        "has_both": int(coverage["coverage_status"].eq("HAS_BOTH").sum()),
        "only_quotes": int(coverage["coverage_status"].eq("ONLY_QUOTES").sum()),
        "only_trades": int(coverage["coverage_status"].eq("ONLY_TRADES").sum()),
        "missing_both": int(coverage["coverage_status"].eq("MISSING_BOTH").sum()),
        "combined_rows": int(len(combined)),
        "in_both_quotes_and_trades_total": int(combined["dataset_compare_status"].eq("IN_BOTH_QUOTES_AND_TRADES").sum()),
        "only_quotes_total": int(combined["dataset_compare_status"].eq("ONLY_QUOTES_TOTAL").sum()),
        "only_trades_total": int(combined["dataset_compare_status"].eq("ONLY_TRADES_TOTAL").sum()),
        "outside_universe_total": int((~combined["universe_member"]).sum()),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {coverage_csv}")


if __name__ == "__main__":
    main()
