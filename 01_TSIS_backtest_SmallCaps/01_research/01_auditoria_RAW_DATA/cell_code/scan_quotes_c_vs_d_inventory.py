from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


PATTERN_DD = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<day>\d{2})[\\/]+quotes\.parquet$",
    re.IGNORECASE,
)
PATTERN_ISO = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<date>\d{4}-\d{2}-\d{2})[\\/]+quotes\.parquet$",
    re.IGNORECASE,
)


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def parse_relpath(relpath: str) -> tuple[str, str] | None:
    rel = relpath.replace("/", "\\")
    m = PATTERN_ISO.match(rel)
    if m:
        ticker = str(m.group("ticker")).upper().strip()
        date = str(m.group("date"))
        return ticker, date

    m = PATTERN_DD.match(rel)
    if m:
        ticker = str(m.group("ticker")).upper().strip()
        date = f"{m.group('year')}-{m.group('month')}-{m.group('day')}"
        return ticker, date

    return None


def scan_root(root: Path, label: str, progress_every: int = 100000) -> pd.DataFrame:
    rows: list[dict] = []
    count = 0
    matched = 0

    for p in root.rglob("quotes.parquet"):
        count += 1
        try:
            rel = str(p.relative_to(root))
        except Exception:
            rel = p.name
        parsed = parse_relpath(rel)
        if parsed is None:
            continue
        ticker, date = parsed
        try:
            size = p.stat().st_size
        except Exception:
            size = None
        rows.append(
            {
                "location": label,
                "ticker": ticker,
                "date": date,
                "task_key": f"{ticker}|{date}",
                "file": str(p),
                "file_size_bytes": size,
            }
        )
        matched += 1
        if matched % progress_every == 0:
            print(f"scan_{label}: matched={matched}")

    print(f"scan_{label}: files_seen={count} matched={matched}")
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["ticker", "date", "file"]).reset_index(drop=True)
    return df


def summarize_inventory(df: pd.DataFrame, label: str) -> dict:
    if df.empty:
        return {
            "location": label,
            "rows": 0,
            "unique_task_keys": 0,
            "tickers": 0,
            "date_min": None,
            "date_max": None,
            "total_bytes": 0,
        }
    return {
        "location": label,
        "rows": int(len(df)),
        "unique_task_keys": int(df["task_key"].nunique()),
        "tickers": int(df["ticker"].nunique()),
        "date_min": str(df["date"].min()),
        "date_max": str(df["date"].max()),
        "total_bytes": int(pd.to_numeric(df["file_size_bytes"], errors="coerce").fillna(0).sum()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--c-root", default=r"C:\TSIS_Data\data\quotes")
    ap.add_argument("--d-root", default=r"D:\quotes")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    c_root = Path(args.c_root)
    d_root = Path(args.d_root)
    if not c_root.exists():
        raise SystemExit(f"c-root not found: {c_root}")
    if not d_root.exists():
        raise SystemExit(f"d-root not found: {d_root}")

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_c_vs_d_inventory\{utc_stamp()}_scan_quotes_c_vs_d_inventory"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    c_df = scan_root(c_root, "C")
    d_df = scan_root(d_root, "D")

    c_inv_csv = outdir / "quotes_c_inventory.csv"
    d_inv_csv = outdir / "quotes_d_inventory.csv"
    compare_csv = outdir / "quotes_c_vs_d_comparison.csv"
    compare_parquet = outdir / "quotes_c_vs_d_comparison.parquet"
    overlap_csv = outdir / "quotes_overlap.csv"
    only_c_csv = outdir / "quotes_only_in_c.csv"
    only_d_csv = outdir / "quotes_only_in_d.csv"
    summary_json = outdir / "quotes_c_vs_d_summary.json"

    c_df.to_csv(c_inv_csv, index=False)
    d_df.to_csv(d_inv_csv, index=False)

    c_keys = c_df[["task_key", "ticker", "date"]].drop_duplicates().copy()
    c_keys["in_c"] = True
    d_keys = d_df[["task_key", "ticker", "date"]].drop_duplicates().copy()
    d_keys["in_d"] = True

    compare = c_keys.merge(d_keys, on=["task_key", "ticker", "date"], how="outer")
    compare["in_c"] = compare["in_c"].fillna(False)
    compare["in_d"] = compare["in_d"].fillna(False)
    compare["location_status"] = "IN_BOTH"
    compare.loc[compare["in_c"] & ~compare["in_d"], "location_status"] = "ONLY_IN_C"
    compare.loc[~compare["in_c"] & compare["in_d"], "location_status"] = "ONLY_IN_D"
    compare = compare.sort_values(["ticker", "date"]).reset_index(drop=True)

    compare.to_csv(compare_csv, index=False)
    compare.to_parquet(compare_parquet, index=False)
    compare.loc[compare["location_status"] == "IN_BOTH"].to_csv(overlap_csv, index=False)
    compare.loc[compare["location_status"] == "ONLY_IN_C"].to_csv(only_c_csv, index=False)
    compare.loc[compare["location_status"] == "ONLY_IN_D"].to_csv(only_d_csv, index=False)

    summary = {
        "c_root": str(c_root),
        "d_root": str(d_root),
        "outdir": str(outdir),
        "c_inventory": summarize_inventory(c_df, "C"),
        "d_inventory": summarize_inventory(d_df, "D"),
        "compare_rows": int(len(compare)),
        "in_both": int(compare["location_status"].eq("IN_BOTH").sum()),
        "only_in_c": int(compare["location_status"].eq("ONLY_IN_C").sum()),
        "only_in_d": int(compare["location_status"].eq("ONLY_IN_D").sum()),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {compare_csv}")


if __name__ == "__main__":
    main()
