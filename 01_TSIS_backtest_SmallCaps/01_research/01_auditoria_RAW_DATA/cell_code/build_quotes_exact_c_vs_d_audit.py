from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def normalize_ticker_series(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.upper()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--inventory-dir",
        required=True,
        help="Outdir produced by scan_quotes_c_vs_d_inventory.py",
    )
    args = ap.parse_args()

    base = Path(args.inventory_dir)
    c_csv = base / "quotes_c_inventory.csv"
    d_csv = base / "quotes_d_inventory.csv"

    if not c_csv.exists():
        raise FileNotFoundError(c_csv)
    if not d_csv.exists():
        raise FileNotFoundError(d_csv)

    c = pd.read_csv(c_csv).copy()
    d = pd.read_csv(d_csv).copy()

    c["ticker"] = normalize_ticker_series(c["ticker"])
    d["ticker"] = normalize_ticker_series(d["ticker"])
    c["task_key"] = c["task_key"].astype("string")
    d["task_key"] = d["task_key"].astype("string")

    ci = c[["task_key", "ticker", "date", "file", "file_size_bytes"]].rename(
        columns={"file": "c_file", "file_size_bytes": "c_size_bytes"}
    )
    di = d[["task_key", "ticker", "date", "file", "file_size_bytes"]].rename(
        columns={"file": "d_file", "file_size_bytes": "d_size_bytes"}
    )

    both = ci.merge(di, on=["task_key", "ticker", "date"], how="inner")
    both["same_size_bytes"] = both["c_size_bytes"].fillna(-1).eq(both["d_size_bytes"].fillna(-2))
    both = both.sort_values(["ticker", "date"]).reset_index(drop=True)

    tick_c = sorted(set(c["ticker"].dropna().tolist()))
    tick_d = sorted(set(d["ticker"].dropna().tolist()))
    tick_b = sorted(set(tick_c) & set(tick_d))

    pd.DataFrame({"ticker": tick_c}).to_csv(base / "quotes_tickers_in_c.csv", index=False)
    pd.DataFrame({"ticker": tick_d}).to_csv(base / "quotes_tickers_in_d.csv", index=False)
    pd.DataFrame({"ticker": tick_b}).to_csv(base / "quotes_tickers_in_both.csv", index=False)
    both.to_csv(base / "quotes_intersection_exact_files.csv", index=False)

    ta = (
        c.groupby("ticker").size().rename("c_files").reset_index()
        .merge(d.groupby("ticker").size().rename("d_files").reset_index(), on="ticker", how="outer")
        .fillna(0)
    )
    bi = both.groupby("ticker").size().rename("files_in_both").reset_index()
    ta = ta.merge(bi, on="ticker", how="left").fillna(0)
    ta["only_in_c_files"] = ta["c_files"] - ta["files_in_both"]
    ta["only_in_d_files"] = ta["d_files"] - ta["files_in_both"]
    ta = ta.sort_values("ticker").reset_index(drop=True)
    ta.to_csv(base / "quotes_ticker_audit_c_vs_d.csv", index=False)

    summary = {
        "inventory_dir": str(base),
        "tickers_in_c": len(tick_c),
        "tickers_in_d": len(tick_d),
        "tickers_in_both": len(tick_b),
        "files_in_c": int(len(c)),
        "files_in_d": int(len(d)),
        "files_in_both_exact": int(len(both)),
        "files_only_in_c": int(len(c) - len(both)),
        "files_only_in_d": int(len(d) - len(both)),
        "outputs": {
            "quotes_tickers_in_c": str(base / "quotes_tickers_in_c.csv"),
            "quotes_tickers_in_d": str(base / "quotes_tickers_in_d.csv"),
            "quotes_tickers_in_both": str(base / "quotes_tickers_in_both.csv"),
            "quotes_intersection_exact_files": str(base / "quotes_intersection_exact_files.csv"),
            "quotes_ticker_audit_c_vs_d": str(base / "quotes_ticker_audit_c_vs_d.csv"),
            "summary_json": str(base / "quotes_exact_audit_summary.json"),
        },
    }
    (base / "quotes_exact_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
