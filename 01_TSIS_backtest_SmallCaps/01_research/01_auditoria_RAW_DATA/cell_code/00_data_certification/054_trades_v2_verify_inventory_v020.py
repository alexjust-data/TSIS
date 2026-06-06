from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

EXPECTED_COLUMNS = [
    "root",
    "root_path",
    "file",
    "relpath",
    "ticker",
    "date",
    "year",
    "month",
    "day",
    "task_key",
    "size_bytes",
    "mtime_utc",
    "inventory_seen_utc",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def add_check(checks: list[dict[str, Any]], name: str, ok: bool, detail: Any) -> None:
    checks.append(
        {
            "check": name,
            "status": as_bool(ok),
            "ok": bool(ok),
            "detail": detail,
        }
    )


def safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify trades v2 inventory outputs")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    summary_path = outdir / "trades_inventory_summary.json"
    checkpoint_path = outdir / "inventory_checkpoint.json"
    manifest_path = outdir / "inventory_run_manifest.json"
    files_parquet_path = outdir / "trades_inventory_files.parquet"
    by_ticker_parquet_path = outdir / "trades_inventory_by_ticker.parquet"
    batch_dir = outdir / "inventory_batches"

    required_paths = {
        "summary_json": summary_path,
        "checkpoint_json": checkpoint_path,
        "manifest_json": manifest_path,
        "files_parquet": files_parquet_path,
        "by_ticker_parquet": by_ticker_parquet_path,
        "batch_dir": batch_dir,
    }

    checks: list[dict[str, Any]] = []
    missing_paths = {name: str(path) for name, path in required_paths.items() if not path.exists()}
    add_check(checks, "required_paths_exist", len(missing_paths) == 0, {"missing": missing_paths})
    if missing_paths:
        payload = {
            "verified_at_utc": utc_now(),
            "outdir": str(outdir),
            "status": "FAIL",
            "checks": checks,
        }
        text = json.dumps(payload, indent=2)
        if str(args.out_json).strip():
            Path(args.out_json).write_text(text, encoding="utf-8")
        print(text)
        return

    summary = load_json(summary_path)
    checkpoint = load_json(checkpoint_path)
    manifest = load_json(manifest_path)

    df = pd.read_parquet(files_parquet_path)
    by_ticker_df = pd.read_parquet(by_ticker_parquet_path)
    batch_files = sorted(batch_dir.glob("inventory_batch_*.parquet"))

    expected_roots = ["C", "D"]
    completed_roots = sorted(map(str, checkpoint.get("completed_roots", [])))
    add_check(
        checks,
        "checkpoint_completed_roots",
        completed_roots == expected_roots,
        {"completed_roots": completed_roots, "expected": expected_roots},
    )
    add_check(
        checks,
        "checkpoint_idle",
        checkpoint.get("active_root") is None and checkpoint.get("last_relpath_persisted") is None,
        {
            "active_root": checkpoint.get("active_root"),
            "last_relpath_persisted": checkpoint.get("last_relpath_persisted"),
        },
    )
    add_check(checks, "manifest_finalized", bool(manifest.get("finalized", False)), {"finalized": manifest.get("finalized", False)})

    persisted_rows_total = safe_int(checkpoint.get("persisted_rows_total"))
    all_rows = safe_int(summary.get("all_rows"))
    add_check(
        checks,
        "checkpoint_vs_summary_rows",
        persisted_rows_total == all_rows,
        {"persisted_rows_total": persisted_rows_total, "summary_all_rows": all_rows},
    )

    c_rows = safe_int(summary.get("c_inventory", {}).get("rows"))
    d_rows = safe_int(summary.get("d_inventory", {}).get("rows"))
    add_check(
        checks,
        "summary_root_rows_add_up",
        (c_rows or 0) + (d_rows or 0) == (all_rows or 0),
        {"c_rows": c_rows, "d_rows": d_rows, "all_rows": all_rows},
    )

    batches_written = safe_int(checkpoint.get("batches_written"))
    add_check(
        checks,
        "checkpoint_vs_batch_file_count",
        batches_written == len(batch_files),
        {"checkpoint_batches_written": batches_written, "batch_files_found": len(batch_files)},
    )

    manifest_batch_files = manifest.get("batch_files", []) if isinstance(manifest.get("batch_files"), list) else []
    add_check(
        checks,
        "manifest_vs_batch_file_count",
        len(manifest_batch_files) == len(batch_files),
        {"manifest_batch_files": len(manifest_batch_files), "batch_files_found": len(batch_files)},
    )

    parquet_rows = int(len(df))
    parquet_all_tickers = int(df["ticker"].nunique()) if "ticker" in df.columns else None
    parquet_c_tickers = int(df.loc[df["root"] == "C", "ticker"].nunique()) if {"root", "ticker"}.issubset(df.columns) else None
    parquet_d_tickers = int(df.loc[df["root"] == "D", "ticker"].nunique()) if {"root", "ticker"}.issubset(df.columns) else None

    add_check(checks, "parquet_vs_summary_rows", parquet_rows == (all_rows or 0), {"parquet_rows": parquet_rows, "summary_all_rows": all_rows})
    add_check(
        checks,
        "parquet_vs_summary_tickers_total",
        parquet_all_tickers == safe_int(summary.get("all_tickers")),
        {"parquet_all_tickers": parquet_all_tickers, "summary_all_tickers": safe_int(summary.get("all_tickers"))},
    )
    add_check(
        checks,
        "parquet_vs_summary_tickers_c",
        parquet_c_tickers == safe_int(summary.get("c_inventory", {}).get("tickers")),
        {"parquet_c_tickers": parquet_c_tickers, "summary_c_tickers": safe_int(summary.get("c_inventory", {}).get("tickers"))},
    )
    add_check(
        checks,
        "parquet_vs_summary_tickers_d",
        parquet_d_tickers == safe_int(summary.get("d_inventory", {}).get("tickers")),
        {"parquet_d_tickers": parquet_d_tickers, "summary_d_tickers": safe_int(summary.get("d_inventory", {}).get("tickers"))},
    )

    expected_columns_ok = all(col in df.columns for col in EXPECTED_COLUMNS)
    add_check(
        checks,
        "expected_columns_present",
        expected_columns_ok,
        {"missing_columns": [col for col in EXPECTED_COLUMNS if col not in df.columns]},
    )

    add_check(checks, "non_null_file", bool(df["file"].notna().all()), {"null_file_rows": int(df["file"].isna().sum()) if "file" in df.columns else None})
    add_check(checks, "non_null_ticker", bool(df["ticker"].notna().all()), {"null_ticker_rows": int(df["ticker"].isna().sum()) if "ticker" in df.columns else None})
    add_check(checks, "non_null_task_key", bool(df["task_key"].notna().all()), {"null_task_key_rows": int(df["task_key"].isna().sum()) if "task_key" in df.columns else None})

    date_min_total = str(df["date"].min()) if "date" in df.columns and not df.empty else None
    date_max_total = str(df["date"].max()) if "date" in df.columns and not df.empty else None
    add_check(
        checks,
        "date_range_total_ordered",
        date_min_total is None or date_max_total is None or date_min_total <= date_max_total,
        {"date_min_total": date_min_total, "date_max_total": date_max_total},
    )

    for root_label in ["C", "D"]:
        root_df = df[df["root"] == root_label].copy() if "root" in df.columns else pd.DataFrame()
        root_min = str(root_df["date"].min()) if not root_df.empty else None
        root_max = str(root_df["date"].max()) if not root_df.empty else None
        add_check(
            checks,
            f"date_range_{root_label}_ordered",
            root_min is None or root_max is None or root_min <= root_max,
            {"root": root_label, "date_min": root_min, "date_max": root_max},
        )

    tickers_c = set(df.loc[df["root"] == "C", "ticker"].astype(str).unique()) if {"root", "ticker"}.issubset(df.columns) else set()
    tickers_d = set(df.loc[df["root"] == "D", "ticker"].astype(str).unique()) if {"root", "ticker"}.issubset(df.columns) else set()
    tickers_overlap = sorted(tickers_c & tickers_d)

    by_ticker_rows = int(len(by_ticker_df))
    add_check(
        checks,
        "by_ticker_rowcount_matches_unique_tickers",
        by_ticker_rows == parquet_all_tickers,
        {"by_ticker_rows": by_ticker_rows, "parquet_unique_tickers": parquet_all_tickers},
    )

    overall_ok = all(check["ok"] for check in checks)
    payload = {
        "verified_at_utc": utc_now(),
        "outdir": str(outdir),
        "status": "PASS" if overall_ok else "FAIL",
        "checks": checks,
        "metrics": {
            "rows_total": parquet_rows,
            "tickers_total": parquet_all_tickers,
            "tickers_c": parquet_c_tickers,
            "tickers_d": parquet_d_tickers,
            "tickers_overlap": int(len(tickers_overlap)),
            "tickers_only_c": int(len(tickers_c - tickers_d)),
            "tickers_only_d": int(len(tickers_d - tickers_c)),
            "date_min_total": date_min_total,
            "date_max_total": date_max_total,
            "batch_files_found": int(len(batch_files)),
        },
        "warnings": {
            "dates_before_2005_present": bool("date" in df.columns and (pd.to_datetime(df["date"], errors="coerce") < pd.Timestamp("2005-01-01")).any()),
            "dates_before_2005_examples": (
                sorted(pd.to_datetime(df.loc[pd.to_datetime(df["date"], errors="coerce") < pd.Timestamp("2005-01-01"), "date"], errors="coerce").dt.strftime("%Y-%m-%d").dropna().unique().tolist())[:10]
                if "date" in df.columns
                else []
            ),
        },
    }

    text = json.dumps(payload, indent=2)
    if str(args.out_json).strip():
        Path(args.out_json).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
