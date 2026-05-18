from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

VALIDATOR_VERSION = "daily_v2_validate_file/0.1.0"
PARTITION_RE = re.compile(
    r"ticker=(?P<ticker>[^\\/]+)[\\/]year=(?P<year>\d{4})[\\/](?P<filename>day_aggs_(?P<filename_ticker>[^_]+)_(?P<filename_year>\d{4})\.parquet)$",
    re.IGNORECASE,
)
REQUIRED_COLUMNS = ["ticker", "date", "year", "o", "h", "l", "c", "v", "vw", "n", "t"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decide_action(severity: str) -> str:
    if severity == "HARD_FAIL":
        return "quarantine_and_retry"
    if severity == "SOFT_FAIL":
        return "review_queue"
    return "accept_raw"


def json_ready(value: Any) -> Any:
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        if pd.isna(value):
            return None
        return value.item()
    if isinstance(value, (pd.Timestamp, datetime)):
        if pd.isna(value):
            return None
        return value.isoformat()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def parse_partition(file_path: Path, expected_root: Path | None) -> dict[str, Any]:
    issues: list[str] = []
    rel_source = str(file_path)
    if expected_root is not None:
        try:
            rel_source = str(file_path.relative_to(expected_root))
        except Exception:
            pass

    m = PARTITION_RE.search(rel_source)
    if not m:
        return {
            "ticker": None,
            "year": None,
            "filename_ticker": None,
            "filename_year": None,
            "issues": ["invalid_partition_path"],
        }

    gd = m.groupdict()
    return {
        "ticker": str(gd["ticker"]).upper().strip(),
        "year": int(gd["year"]),
        "filename_ticker": str(gd["filename_ticker"]).upper().strip(),
        "filename_year": int(gd["filename_year"]),
        "issues": issues,
    }


def business_days_in_year(year: int) -> int:
    start = pd.Timestamp(year=year, month=1, day=1)
    end = pd.Timestamp(year=year, month=12, day=31)
    return int(len(pd.bdate_range(start, end)))


def validate_daily_file(
    *,
    file_path: Path,
    expected_root: Path | None,
    run_id: str,
    batch_id: str,
    scan_reason: str,
    validation_kind: str,
    min_expected_price: float = 0.0,
    min_coverage_ratio_warn: float = 0.50,
    max_gap_days_warn: int = 20,
) -> dict[str, Any]:
    processed_at_utc = utc_now()
    issues: list[str] = []
    warns: list[str] = []
    missing_required_cols: list[str] = []
    dtype_mismatches: list[str] = []

    partition = parse_partition(file_path, expected_root)
    issues.extend(partition["issues"])

    base: dict[str, Any] = {
        "file": str(file_path),
        "ticker": partition["ticker"],
        "year": partition["year"],
        "rows": 0,
        "severity": None,
        "issues": None,
        "warns": None,
        "action": None,
        "metrics_json": None,
        "validator_version": VALIDATOR_VERSION,
        "processed_at_utc": processed_at_utc,
        "run_id": run_id,
        "batch_id": batch_id,
        "scan_reason": scan_reason,
        "validation_kind": validation_kind,
    }

    if not file_path.exists():
        issues.append("file_missing")
        severity = "HARD_FAIL"
        base.update(
            {
                "severity": severity,
                "issues": issues,
                "warns": warns,
                "action": decide_action(severity),
                "metrics_json": {"size_bytes": None},
            }
        )
        return base

    size_bytes = int(file_path.stat().st_size)
    if size_bytes <= 0:
        issues.append("zero_byte_file")

    dataset_read_compatible = True
    dataset_read_error = None
    try:
        _ = pq.read_table(file_path)
    except Exception as exc:
        dataset_read_compatible = False
        dataset_read_error = repr(exc)
        warns.append("dataset_read_incompatible_schema")
        if "incompatible types" in repr(exc) and "dictionary" in repr(exc) and "ticker" in repr(exc):
            warns.append("schema_merge_conflict_ticker_encoding")

    try:
        pf = pq.ParquetFile(file_path)
        table = pf.read()
    except Exception as exc:
        issues.append("parquet_unreadable")
        severity = "HARD_FAIL"
        base.update(
            {
                "severity": severity,
                "issues": issues,
                "warns": warns,
                "action": decide_action(severity),
                "metrics_json": {
                    "size_bytes": size_bytes,
                    "parquet_read_error": repr(exc),
                    "dataset_read_compatible": dataset_read_compatible,
                    "dataset_read_error": dataset_read_error,
                },
            }
        )
        return base

    rows = int(table.num_rows)
    columns = list(table.schema.names)
    dtypes = {f.name: str(f.type) for f in table.schema}
    if rows < 1:
        issues.append("zero_rows")

    for c in REQUIRED_COLUMNS:
        if c not in columns:
            missing_required_cols.append(c)
    if missing_required_cols:
        issues.append("missing_required_columns")

    expected_string = {"ticker", "date"}
    expected_float = {"o", "h", "l", "c", "v", "vw"}
    expected_int = {"year", "n", "t"}
    for c in expected_string:
        got = dtypes.get(c)
        if got is not None and "string" not in got:
            dtype_mismatches.append(f"{c}:{got}")
    for c in expected_float:
        got = dtypes.get(c)
        if got is not None and not any(x in got for x in ["double", "float", "decimal", "int"]):
            dtype_mismatches.append(f"{c}:{got}")
    for c in expected_int:
        got = dtypes.get(c)
        if got is not None and "int" not in got:
            dtype_mismatches.append(f"{c}:{got}")
    if dtype_mismatches:
        warns.append("dtype_mismatch")

    metrics: dict[str, Any] = {
        "size_bytes": size_bytes,
        "schema_columns": columns,
        "schema_types": dtypes,
        "missing_required_cols": missing_required_cols,
        "dtype_mismatches": dtype_mismatches,
        "partition_ticker": partition["ticker"],
        "partition_year": partition["year"],
        "filename_ticker": partition["filename_ticker"],
        "filename_year": partition["filename_year"],
        "dataset_read_compatible": dataset_read_compatible,
        "dataset_read_error": dataset_read_error,
    }

    if partition["ticker"] is not None and partition["filename_ticker"] is not None and partition["ticker"] != partition["filename_ticker"]:
        issues.append("partition_vs_filename_ticker_mismatch")
    if partition["year"] is not None and partition["filename_year"] is not None and int(partition["year"]) != int(partition["filename_year"]):
        issues.append("partition_vs_filename_year_mismatch")

    if not missing_required_cols:
        df = table.select([c for c in REQUIRED_COLUMNS if c in columns]).to_pandas()
        base["rows"] = int(len(df))

        work = pd.DataFrame(
            {
                "ticker": df["ticker"].astype(str).str.upper().str.strip(),
                "date": pd.to_datetime(df["date"], errors="coerce").dt.normalize(),
                "year": pd.to_numeric(df["year"], errors="coerce"),
                "o": pd.to_numeric(df["o"], errors="coerce"),
                "h": pd.to_numeric(df["h"], errors="coerce"),
                "l": pd.to_numeric(df["l"], errors="coerce"),
                "c": pd.to_numeric(df["c"], errors="coerce"),
                "v": pd.to_numeric(df["v"], errors="coerce"),
                "vw": pd.to_numeric(df["vw"], errors="coerce"),
                "n": pd.to_numeric(df["n"], errors="coerce"),
                "t": pd.to_numeric(df["t"], errors="coerce"),
            }
        )

        invalid_after_parse = (
            work["date"].isna()
            | work["year"].isna()
            | work["o"].isna()
            | work["h"].isna()
            | work["l"].isna()
            | work["c"].isna()
            | work["v"].isna()
            | work["vw"].isna()
            | work["n"].isna()
            | work["t"].isna()
        )
        valid_df = work[~invalid_after_parse].copy()

        if valid_df.empty:
            issues.append("all_rows_invalid_after_parse")
        else:
            if valid_df["ticker"].nunique(dropna=False) > 1:
                issues.append("multiple_tickers_in_file")
            if valid_df["year"].nunique(dropna=False) > 1:
                issues.append("multiple_years_in_file")

            if partition["ticker"] is not None and valid_df["ticker"].nunique() == 1 and valid_df["ticker"].iloc[0] != partition["ticker"]:
                issues.append("partition_vs_column_ticker_mismatch")
            if partition["year"] is not None and valid_df["year"].nunique() == 1 and int(valid_df["year"].iloc[0]) != int(partition["year"]):
                issues.append("partition_vs_column_year_mismatch")

            duplicate_dates = int(valid_df["date"].duplicated(keep=False).sum())
            if duplicate_dates > 0:
                issues.append("duplicate_dates_in_file")

            if partition["year"] is not None:
                dates_outside_partition_year = int((valid_df["date"].dt.year != int(partition["year"])).sum())
                if dates_outside_partition_year > 0:
                    issues.append("date_out_of_partition_year")
            else:
                dates_outside_partition_year = None

            nonpositive_mask = (valid_df[["o", "h", "l", "c"]] <= min_expected_price).any(axis=1)
            negative_or_zero_ohlc_rows = int(nonpositive_mask.sum())
            if negative_or_zero_ohlc_rows > 0:
                issues.append("negative_or_zero_ohlc_rows")

            negative_volume_rows = int((valid_df["v"] < 0).sum())
            if negative_volume_rows > 0:
                issues.append("negative_volume_rows")

            high_low_inversion_rows = int(
                (
                    (valid_df["h"] < valid_df["l"])
                    | (valid_df["h"] < valid_df["o"])
                    | (valid_df["h"] < valid_df["c"])
                    | (valid_df["l"] > valid_df["o"])
                    | (valid_df["l"] > valid_df["c"])
                ).sum()
            )
            if high_low_inversion_rows > 0:
                issues.append("high_low_inversion_rows")

            vw_outside_range_rows = int(
                (
                    (valid_df["v"] > 0)
                    & ((valid_df["vw"] < valid_df["l"]) | (valid_df["vw"] > valid_df["h"]))
                ).sum()
            )
            if vw_outside_range_rows > 0:
                issues.append("vw_outside_range_rows")

            date_min = valid_df["date"].min()
            date_max = valid_df["date"].max()
            rows_after_parse = int(len(valid_df))
            date_year = int(partition["year"]) if partition["year"] is not None else int(valid_df["date"].dt.year.mode().iloc[0])
            business_days_covered_est = business_days_in_year(date_year)
            coverage_ratio_vs_business_days = float(rows_after_parse / max(business_days_covered_est, 1))
            sorted_dates = valid_df["date"].drop_duplicates().sort_values()
            gaps = sorted_dates.diff().dropna().dt.days
            max_gap_days = int(gaps.max()) if not gaps.empty else 0

            if rows_after_parse < 10:
                warns.append("rows_lt_10")
            if coverage_ratio_vs_business_days < float(min_coverage_ratio_warn):
                warns.append("suspicious_sparse_year")
            if max_gap_days > int(max_gap_days_warn):
                warns.append("large_internal_gap_days")

            metrics.update(
                {
                    "rows_after_parse": rows_after_parse,
                    "duplicate_dates_rows": duplicate_dates,
                    "dates_outside_partition_year": dates_outside_partition_year,
                    "negative_or_zero_ohlc_rows": negative_or_zero_ohlc_rows,
                    "negative_volume_rows": negative_volume_rows,
                    "high_low_inversion_rows": high_low_inversion_rows,
                    "vw_outside_range_rows": vw_outside_range_rows,
                    "date_min": json_ready(date_min),
                    "date_max": json_ready(date_max),
                    "ticker_nunique": int(valid_df["ticker"].nunique()),
                    "year_nunique": int(valid_df["year"].nunique()),
                    "business_days_covered_est": business_days_covered_est,
                    "coverage_ratio_vs_business_days": coverage_ratio_vs_business_days,
                    "max_gap_days": max_gap_days,
                    "o_min": json_ready(valid_df["o"].min()),
                    "h_max": json_ready(valid_df["h"].max()),
                    "l_min": json_ready(valid_df["l"].min()),
                    "c_max": json_ready(valid_df["c"].max()),
                    "v_sum": json_ready(valid_df["v"].sum()),
                    "vw_mean": json_ready(valid_df["vw"].mean()),
                    "n_sum": json_ready(valid_df["n"].sum()),
                }
            )

    issues = sorted(set(issues))
    warns = sorted(set(warns))
    severity = "HARD_FAIL" if issues else ("SOFT_FAIL" if warns else "PASS")
    base.update(
        {
            "severity": severity,
            "issues": issues,
            "warns": warns,
            "action": decide_action(severity),
            "metrics_json": {k: json_ready(v) for k, v in metrics.items()},
        }
    )
    return base


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate one day_aggs parquet under Agent02 daily v2 contract")
    ap.add_argument("--file", required=True)
    ap.add_argument("--expected-root", default="")
    ap.add_argument("--run-id", default="manual")
    ap.add_argument("--batch-id", default="manual")
    ap.add_argument("--scan-reason", default="manual_recheck")
    ap.add_argument("--validation-kind", default="revalidation_only")
    ap.add_argument("--min-expected-price", type=float, default=0.0)
    ap.add_argument("--min-coverage-ratio-warn", type=float, default=0.50)
    ap.add_argument("--max-gap-days-warn", type=int, default=20)
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    expected_root = Path(args.expected_root) if str(args.expected_root).strip() else None

    res = validate_daily_file(
        file_path=Path(args.file),
        expected_root=expected_root,
        run_id=args.run_id,
        batch_id=args.batch_id,
        scan_reason=args.scan_reason,
        validation_kind=args.validation_kind,
        min_expected_price=float(args.min_expected_price),
        min_coverage_ratio_warn=float(args.min_coverage_ratio_warn),
        max_gap_days_warn=int(args.max_gap_days_warn),
    )
    payload = json.dumps(res, indent=2, ensure_ascii=False)
    if str(args.out_json).strip():
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
