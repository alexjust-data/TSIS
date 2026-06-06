from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


TICKER_DATASETS = {
    "splits": {
        "path": Path("corporate_actions") / "splits",
        "file_glob": "ticker=*/*.parquet",
    },
    "dividends": {
        "path": Path("corporate_actions") / "dividends",
        "file_glob": "ticker=*/*.parquet",
    },
    "ticker_events": {
        "path": Path("corporate_actions") / "ticker_events",
        "file_glob": "ticker=*/*.parquet",
    },
    "news": {
        "path": Path("news") / "news",
        "file_glob": "ticker=*/*.parquet",
    },
    "ipos": {
        "path": Path("ipos") / "ipos",
        "file_glob": "ticker=*/*.parquet",
    },
    "income_statements": {
        "path": Path("financials") / "income_statements",
        "file_glob": "ticker=*/*.parquet",
    },
    "balance_sheets": {
        "path": Path("financials") / "balance_sheets",
        "file_glob": "ticker=*/*.parquet",
    },
    "cash_flow_statements": {
        "path": Path("financials") / "cash_flow_statements",
        "file_glob": "ticker=*/*.parquet",
    },
    "ratios": {
        "path": Path("financials") / "ratios",
        "file_glob": "ticker=*/*.parquet",
    },
}

MACRO_DATASETS = {
    "inflation": Path("economic") / "inflation.parquet",
    "inflation_expectations": Path("economic") / "inflation_expectations.parquet",
    "treasury_yields": Path("economic") / "treasury_yields.parquet",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_universe_tickers(universe_parquet: Path) -> List[str]:
    df = pd.read_parquet(universe_parquet, columns=["ticker"])
    ser = df["ticker"].astype("string").str.strip().dropna()
    return sorted({x.upper() for x in ser.tolist() if x})


def infer_ticker_from_path(path: Path) -> Optional[str]:
    for part in path.parts:
        if part.startswith("ticker="):
            ticker = part.split("=", 1)[1].strip().upper()
            return ticker or None
    stem = path.stem
    if "_" in stem:
        return stem.rsplit("_", 1)[-1].strip().upper() or None
    return None


def read_rows_and_empty_flag(path: Path) -> Tuple[int, bool]:
    df = pd.read_parquet(path)
    rows = int(len(df))
    empty_flag = False
    if "_empty" in df.columns and rows > 0:
        try:
            empty_flag = bool(df["_empty"].fillna(False).astype(bool).all())
        except Exception:
            empty_flag = False
    if rows == 0:
        empty_flag = True
    return rows, empty_flag


def audit_ticker_dataset(additional_root: Path, dataset: str, universe: List[str]) -> Tuple[Dict[str, object], pd.DataFrame]:
    spec = TICKER_DATASETS[dataset]
    base = additional_root / spec["path"]
    universe_set = set(universe)
    records: List[Dict[str, object]] = []

    if base.exists():
        files = sorted(base.glob(spec["file_glob"]))
    else:
        files = []

    for path in files:
        ticker = infer_ticker_from_path(path)
        rows, is_empty = read_rows_and_empty_flag(path)
        records.append(
            {
                "dataset": dataset,
                "ticker": ticker,
                "file_path": str(path),
                "file_present": True,
                "rows": rows,
                "is_empty": bool(is_empty),
                "is_non_empty": bool(rows > 0 and not is_empty),
                "in_target_universe": bool(ticker in universe_set) if ticker else False,
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        summary = {
            "dataset": dataset,
            "files_present": 0,
            "files_non_empty": 0,
            "files_empty": 0,
            "target_hit_non_empty": 0,
            "target_miss_non_empty": len(universe),
            "coverage_non_empty_pct": 0.0,
            "target_hit_any_file": 0,
            "target_miss_any_file": len(universe),
            "coverage_any_file_pct": 0.0,
            "rows_total": 0,
            "extra_files_outside_target": 0,
        }
        return summary, df

    files_present = int(len(df))
    files_non_empty = int(df["is_non_empty"].sum())
    files_empty = int(df["is_empty"].sum())
    rows_total = int(df["rows"].sum())
    target_non_empty = set(df.loc[df["in_target_universe"] & df["is_non_empty"], "ticker"].dropna().astype(str).str.upper())
    target_any = set(df.loc[df["in_target_universe"], "ticker"].dropna().astype(str).str.upper())
    all_found = set(df["ticker"].dropna().astype(str).str.upper())

    summary = {
        "dataset": dataset,
        "files_present": files_present,
        "files_non_empty": files_non_empty,
        "files_empty": files_empty,
        "target_hit_non_empty": len(target_non_empty),
        "target_miss_non_empty": len(universe_set - target_non_empty),
        "coverage_non_empty_pct": round(100.0 * len(target_non_empty) / len(universe_set), 3) if universe_set else 0.0,
        "target_hit_any_file": len(target_any),
        "target_miss_any_file": len(universe_set - target_any),
        "coverage_any_file_pct": round(100.0 * len(target_any) / len(universe_set), 3) if universe_set else 0.0,
        "rows_total": rows_total,
        "extra_files_outside_target": len(all_found - universe_set),
    }
    return summary, df


def audit_macro_dataset(additional_root: Path, dataset: str) -> Dict[str, object]:
    path = additional_root / MACRO_DATASETS[dataset]
    if not path.exists():
        return {
            "dataset": dataset,
            "file_present": False,
            "rows_total": 0,
            "date_min": None,
            "date_max": None,
            "file_path": str(path),
        }

    df = pd.read_parquet(path)
    date_col = "date" if "date" in df.columns else None
    if date_col:
        ser = pd.to_datetime(df[date_col], errors="coerce").dropna()
        date_min = ser.min().date().isoformat() if not ser.empty else None
        date_max = ser.max().date().isoformat() if not ser.empty else None
    else:
        date_min = None
        date_max = None
    return {
        "dataset": dataset,
        "file_present": True,
        "rows_total": int(len(df)),
        "date_min": date_min,
        "date_max": date_max,
        "file_path": str(path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit LT<1B coverage and effective non-empty presence for additional datasets")
    parser.add_argument("--universe-parquet", required=True)
    parser.add_argument("--additional-root", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    universe_parquet = Path(args.universe_parquet)
    additional_root = Path(args.additional_root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    universe = load_universe_tickers(universe_parquet)

    ticker_summaries: List[Dict[str, object]] = []
    ticker_frames: List[pd.DataFrame] = []
    for dataset in TICKER_DATASETS:
        summary, df = audit_ticker_dataset(additional_root, dataset, universe)
        ticker_summaries.append(summary)
        ticker_frames.append(df)

    ticker_summary_df = pd.DataFrame(ticker_summaries).sort_values("dataset").reset_index(drop=True)
    ticker_summary_df.to_parquet(outdir / "additional_ticker_datasets_summary.parquet", index=False)
    ticker_summary_df.to_csv(outdir / "additional_ticker_datasets_summary.csv", index=False)

    ticker_detail_df = pd.concat(ticker_frames, ignore_index=True) if ticker_frames else pd.DataFrame()
    ticker_detail_df.to_parquet(outdir / "additional_ticker_datasets_by_file.parquet", index=False)
    ticker_detail_df.to_csv(outdir / "additional_ticker_datasets_by_file.csv", index=False)

    macro_rows = [audit_macro_dataset(additional_root, dataset) for dataset in MACRO_DATASETS]
    macro_df = pd.DataFrame(macro_rows).sort_values("dataset").reset_index(drop=True)
    macro_df.to_parquet(outdir / "additional_macro_datasets_summary.parquet", index=False)
    macro_df.to_csv(outdir / "additional_macro_datasets_summary.csv", index=False)

    summary = {
        "audited_at_utc": utc_now_iso(),
        "inputs": {
            "universe_parquet": str(universe_parquet),
            "additional_root": str(additional_root),
        },
        "universe_tickers": len(universe),
        "ticker_datasets": ticker_summaries,
        "macro_datasets": macro_rows,
        "outputs": {
            "ticker_summary_parquet": str(outdir / "additional_ticker_datasets_summary.parquet"),
            "ticker_summary_csv": str(outdir / "additional_ticker_datasets_summary.csv"),
            "ticker_detail_parquet": str(outdir / "additional_ticker_datasets_by_file.parquet"),
            "ticker_detail_csv": str(outdir / "additional_ticker_datasets_by_file.csv"),
            "macro_summary_parquet": str(outdir / "additional_macro_datasets_summary.parquet"),
            "macro_summary_csv": str(outdir / "additional_macro_datasets_summary.csv"),
            "summary_json": str(outdir / "additional_lt1b_coverage_audit_summary.json"),
        },
    }
    (outdir / "additional_lt1b_coverage_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
