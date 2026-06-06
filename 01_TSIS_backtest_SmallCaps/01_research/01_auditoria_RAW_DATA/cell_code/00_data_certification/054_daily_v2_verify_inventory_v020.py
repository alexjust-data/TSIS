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
    "year",
    "filename_ticker",
    "filename_year",
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
    ap = argparse.ArgumentParser(description="Verify daily v2 inventory outputs")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    summary_path = outdir / "daily_inventory_summary.json"
    checkpoint_path = outdir / "inventory_checkpoint.json"
    manifest_path = outdir / "inventory_run_manifest.json"
    files_parquet_path = outdir / "daily_inventory_files.parquet"
    by_ticker_parquet_path = outdir / "daily_inventory_by_ticker.parquet"
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

    expected_roots = sorted(list(summary.get("roots", {}).keys()))
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

    inventory_rows_sum = 0
    for inv in summary.get("inventories", {}).values():
        inventory_rows_sum += safe_int(inv.get("rows")) or 0
    add_check(
        checks,
        "summary_root_rows_add_up",
        inventory_rows_sum == (all_rows or 0),
        {"inventory_rows_sum": inventory_rows_sum, "all_rows": all_rows},
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

    add_check(checks, "parquet_vs_summary_rows", parquet_rows == (all_rows or 0), {"parquet_rows": parquet_rows, "summary_all_rows": all_rows})
    add_check(
        checks,
        "parquet_vs_summary_tickers_total",
        parquet_all_tickers == safe_int(summary.get("all_tickers")),
        {"parquet_all_tickers": parquet_all_tickers, "summary_all_tickers": safe_int(summary.get("all_tickers"))},
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

    year_min_total = safe_int(pd.to_numeric(df["year"], errors="coerce").min()) if "year" in df.columns and not df.empty else None
    year_max_total = safe_int(pd.to_numeric(df["year"], errors="coerce").max()) if "year" in df.columns and not df.empty else None
    add_check(
        checks,
        "year_range_total_ordered",
        year_min_total is None or year_max_total is None or year_min_total <= year_max_total,
        {"year_min_total": year_min_total, "year_max_total": year_max_total},
    )

    for root_label in sorted(summary.get("roots", {}).keys()):
        root_df = df[df["root"] == root_label].copy() if "root" in df.columns else pd.DataFrame()
        root_min = safe_int(pd.to_numeric(root_df["year"], errors="coerce").min()) if not root_df.empty else None
        root_max = safe_int(pd.to_numeric(root_df["year"], errors="coerce").max()) if not root_df.empty else None
        add_check(
            checks,
            f"year_range_{root_label}_ordered",
            root_min is None or root_max is None or root_min <= root_max,
            {"root": root_label, "year_min": root_min, "year_max": root_max},
        )

    roots_present = sorted(summary.get("roots", {}).keys())
    ticker_sets: dict[str, set[str]] = {}
    for root_label in roots_present:
        if {"root", "ticker"}.issubset(df.columns):
            ticker_sets[root_label] = set(df.loc[df["root"] == root_label, "ticker"].astype(str).unique())
        else:
            ticker_sets[root_label] = set()

    by_ticker_rows = int(len(by_ticker_df))
    add_check(
        checks,
        "by_ticker_rowcount_matches_unique_tickers",
        by_ticker_rows == parquet_all_tickers,
        {"by_ticker_rows": by_ticker_rows, "parquet_unique_tickers": parquet_all_tickers},
    )

    filename_ticker_mismatch_rows = int((df["ticker"].astype(str) != df["filename_ticker"].astype(str)).sum()) if {"ticker", "filename_ticker"}.issubset(df.columns) else None
    filename_year_mismatch_rows = int((pd.to_numeric(df["year"], errors="coerce") != pd.to_numeric(df["filename_year"], errors="coerce")).sum()) if {"year", "filename_year"}.issubset(df.columns) else None
    add_check(
        checks,
        "filename_ticker_matches_partition_ticker",
        filename_ticker_mismatch_rows == 0,
        {"filename_ticker_mismatch_rows": filename_ticker_mismatch_rows},
    )
    add_check(
        checks,
        "filename_year_matches_partition_year",
        filename_year_mismatch_rows == 0,
        {"filename_year_mismatch_rows": filename_year_mismatch_rows},
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
            "year_min_total": year_min_total,
            "year_max_total": year_max_total,
            "batch_files_found": int(len(batch_files)),
            "roots_present": roots_present,
            "tickers_by_root": {root_label: int(len(ticker_sets[root_label])) for root_label in roots_present},
        },
        "warnings": {
            "years_before_2005_present": bool("year" in df.columns and (pd.to_numeric(df["year"], errors="coerce") < 2005).any()),
            "years_before_2005_examples": (
                sorted(pd.to_numeric(df.loc[pd.to_numeric(df["year"], errors="coerce") < 2005, "year"], errors="coerce").dropna().astype(int).unique().tolist())[:10]
                if "year" in df.columns
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
