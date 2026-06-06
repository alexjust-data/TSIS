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

VALIDATOR_VERSION = "trades_v2_validate_file/0.2.0"
PARTITION_RE = re.compile(
    r"(?P<ticker>[^\\/]+)[\\/]year=(?P<year>\d{4})[\\/]month=(?P<month>\d{2})[\\/]day=(?P<day>\d{4}-\d{2}-\d{2})[\\/]market\.parquet$",
    re.IGNORECASE,
)
REQUIRED_COLUMNS = ["ticker", "date", "timestamp", "price", "size", "exchange", "conditions", "year", "month", "day"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decide_action(severity: str) -> str:
    if severity == "HARD_FAIL":
        return "quarantine_and_retry"
    if severity == "SOFT_FAIL":
        return "review_queue"
    return "accept_raw"


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
            "date": None,
            "year": None,
            "month": None,
            "day": None,
            "issues": ["invalid_partition_path"],
        }
    gd = m.groupdict()
    try:
        dt = pd.Timestamp(gd["day"]).normalize()
    except Exception:
        issues.append("unparseable_partition_date")
        dt = pd.NaT
    return {
        "ticker": str(gd["ticker"]).upper().strip(),
        "date": None if pd.isna(dt) else dt.strftime("%Y-%m-%d"),
        "year": int(gd["year"]),
        "month": int(gd["month"]),
        "day": gd["day"],
        "issues": issues,
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, (np.floating, np.integer)):
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


def near(value: float | None, target: float, tol_pct: float = 5.0) -> bool:
    if value is None or pd.isna(value):
        return False
    if target == 0:
        return False
    return abs(float(value) - float(target)) / abs(float(target)) * 100.0 <= tol_pct


def factor_far_from_one(value: float | None, min_distance_pct: float = 20.0) -> bool:
    if value is None or pd.isna(value):
        return False
    value = float(value)
    if value <= 0:
        return False
    return abs(value - 1.0) / 1.0 * 100.0 >= min_distance_pct


def factors_agree(a: float | None, b: float | None, tol_pct: float = 20.0) -> bool:
    if a is None or b is None or pd.isna(a) or pd.isna(b):
        return False
    a = float(a)
    b = float(b)
    if a <= 0 or b <= 0:
        return False
    return abs(a - b) / max(abs(a), abs(b)) * 100.0 <= tol_pct


def inverse_factor_match(price_factor: float | None, volume_ratio: float | None, tol_pct: float = 35.0) -> bool:
    if price_factor is None or volume_ratio is None or pd.isna(price_factor) or pd.isna(volume_ratio):
        return False
    price_factor = float(price_factor)
    volume_ratio = float(volume_ratio)
    if price_factor <= 0 or volume_ratio <= 0:
        return False
    expected = 1.0 / price_factor
    return abs(volume_ratio - expected) / max(abs(expected), 1e-12) * 100.0 <= tol_pct


def detect_scale_mismatch_confidence(
    *,
    price_factor_daily: float | None,
    price_factor_1m: float | None,
    volume_ratio_daily: float | None,
    volume_ratio_1m: float | None,
) -> str:
    price_pair_agree = factors_agree(price_factor_daily, price_factor_1m, tol_pct=20.0)
    price_shift_daily = factor_far_from_one(price_factor_daily, min_distance_pct=20.0)
    price_shift_1m = factor_far_from_one(price_factor_1m, min_distance_pct=20.0)
    any_price_shift = price_shift_daily or price_shift_1m

    vol_daily_match = inverse_factor_match(price_factor_daily, volume_ratio_daily, tol_pct=35.0)
    vol_1m_match = inverse_factor_match(price_factor_1m, volume_ratio_1m, tol_pct=35.0)

    if price_pair_agree and any_price_shift and (vol_daily_match or vol_1m_match):
        return "strong"
    if price_pair_agree and any_price_shift:
        return "probable"
    if price_shift_daily and vol_daily_match:
        return "probable"
    if price_shift_1m and vol_1m_match:
        return "probable"
    return "none"


def load_daily_reference(ohlcv_daily_root: Path | None, ticker: str | None, date_str: str | None) -> dict[str, Any]:
    if ohlcv_daily_root is None or not ticker or not date_str:
        return {"ohlcv_daily_found": False}
    ts = pd.Timestamp(date_str)
    path = ohlcv_daily_root / f"ticker={ticker}" / f"year={ts.year:04d}" / f"day_aggs_{ticker}_{ts.year:04d}.parquet"
    if not path.exists():
        return {"ohlcv_daily_found": False, "ohlcv_daily_path": str(path)}
    try:
        df = pd.read_parquet(path, columns=["date", "o", "h", "l", "c", "v", "vw", "n"])
        row = df[df["date"].astype(str) == date_str]
        if row.empty:
            return {"ohlcv_daily_found": False, "ohlcv_daily_path": str(path)}
        rec = row.iloc[0].to_dict()
        rec["ohlcv_daily_found"] = True
        rec["ohlcv_daily_path"] = str(path)
        return rec
    except Exception as exc:
        return {"ohlcv_daily_found": False, "ohlcv_daily_path": str(path), "ohlcv_daily_error": repr(exc)}


def load_1m_reference(ohlcv_1m_root: Path | None, ticker: str | None, date_str: str | None) -> dict[str, Any]:
    if ohlcv_1m_root is None or not ticker or not date_str:
        return {"ohlcv_1m_found": False}
    ts = pd.Timestamp(date_str)
    path = (
        ohlcv_1m_root
        / f"ticker={ticker}"
        / f"year={ts.year:04d}"
        / f"month={ts.month:02d}"
        / f"minute_aggs_{ticker}_{ts.year:04d}_{ts.month:02d}.parquet"
    )
    if not path.exists():
        return {"ohlcv_1m_found": False, "ohlcv_1m_path": str(path)}
    try:
        df = pd.read_parquet(path, columns=["date", "o", "h", "l", "c", "v", "vw", "n", "t"])
        day_df = df[df["date"].astype(str) == date_str]
        if day_df.empty:
            return {"ohlcv_1m_found": False, "ohlcv_1m_path": str(path)}
        out = {
            "ohlcv_1m_found": True,
            "ohlcv_1m_path": str(path),
            "ohlcv_1m_rows_for_day": int(len(day_df)),
            "ohlcv_1m_low_min": json_ready(pd.to_numeric(day_df["l"], errors="coerce").min()),
            "ohlcv_1m_high_max": json_ready(pd.to_numeric(day_df["h"], errors="coerce").max()),
            "ohlcv_1m_volume_sum": json_ready(pd.to_numeric(day_df["v"], errors="coerce").fillna(0).sum()),
            "ohlcv_1m_trade_count_sum": json_ready(pd.to_numeric(day_df["n"], errors="coerce").fillna(0).sum()),
            "ohlcv_1m_vw_mean": json_ready(pd.to_numeric(day_df["vw"], errors="coerce").mean()),
        }
        return out
    except Exception as exc:
        return {"ohlcv_1m_found": False, "ohlcv_1m_path": str(path), "ohlcv_1m_error": repr(exc)}


def validate_trades_file(
    *,
    file_path: Path,
    expected_root: Path | None,
    run_id: str,
    batch_id: str,
    scan_reason: str,
    validation_kind: str,
    ohlcv_daily_root: Path | None = None,
    ohlcv_1m_root: Path | None = None,
    duplicate_excess_warn_pct: float = 3.0,
    duplicate_excess_hard_pct: float = 10.0,
    daily_range_tolerance_pct: float = 1.0,
    min_expected_price: float = 0.0,
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
        "date": partition["date"],
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
        base.update({"severity": severity, "issues": issues, "warns": warns, "action": decide_action(severity), "metrics_json": {"size_bytes": None}})
        return base

    size_bytes = int(file_path.stat().st_size)
    if size_bytes <= 0:
        issues.append("zero_byte_file")

    try:
        pf = pq.ParquetFile(file_path)
        table = pf.read()
    except Exception as exc:
        issues.append("parquet_unreadable")
        severity = "HARD_FAIL"
        base.update({"severity": severity, "issues": issues, "warns": warns, "action": decide_action(severity), "metrics_json": {"size_bytes": size_bytes, "read_error": repr(exc)}})
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

    expected_string = {"ticker", "date", "day"}
    expected_float = {"price"}
    expected_int = {"size", "exchange", "year", "month"}
    expected_ts = {"timestamp"}
    for c in expected_string:
        got = dtypes.get(c)
        if got is not None and "string" not in got:
            dtype_mismatches.append(f"{c}:{got}")
    for c in expected_float:
        got = dtypes.get(c)
        if got is not None and not any(x in got for x in ["double", "float", "decimal"]):
            dtype_mismatches.append(f"{c}:{got}")
    for c in expected_int:
        got = dtypes.get(c)
        if got is not None and "int" not in got:
            dtype_mismatches.append(f"{c}:{got}")
    for c in expected_ts:
        got = dtypes.get(c)
        if got is not None and "timestamp" not in got:
            dtype_mismatches.append(f"{c}:{got}")
    got = dtypes.get("conditions")
    if got is not None and "list" not in got:
        dtype_mismatches.append(f"conditions:{got}")
    if dtype_mismatches:
        warns.append("dtype_mismatch")

    metrics: dict[str, Any] = {
        "size_bytes": size_bytes,
        "schema_columns": columns,
        "schema_types": dtypes,
        "missing_required_cols": missing_required_cols,
        "dtype_mismatches": dtype_mismatches,
        "partition_year": partition["year"],
        "partition_month": partition["month"],
        "partition_day": partition["day"],
    }

    if not missing_required_cols:
        df = table.select([c for c in REQUIRED_COLUMNS if c in columns]).to_pandas()
        base["rows"] = int(len(df))

        work = pd.DataFrame(
            {
                "ticker": df["ticker"].astype(str).str.upper().str.strip(),
                "date": df["date"].astype(str).str.strip(),
                "timestamp": pd.to_datetime(df["timestamp"], utc=True, errors="coerce"),
                "price": pd.to_numeric(df["price"], errors="coerce"),
                "size": pd.to_numeric(df["size"], errors="coerce"),
                "exchange": pd.to_numeric(df["exchange"], errors="coerce"),
                "year": pd.to_numeric(df["year"], errors="coerce"),
                "month": pd.to_numeric(df["month"], errors="coerce"),
                "day": df["day"].astype(str).str.strip(),
            }
        )
        invalid_after_parse = (
            work["timestamp"].isna()
            | work["price"].isna()
            | work["size"].isna()
            | work["exchange"].isna()
            | work["year"].isna()
            | work["month"].isna()
        )
        valid_df = work[~invalid_after_parse].copy()

        if valid_df.empty:
            issues.append("all_rows_invalid_after_parse")
        else:
            if valid_df["ticker"].nunique(dropna=False) > 1:
                issues.append("multiple_tickers_in_file")
            if valid_df["date"].nunique(dropna=False) > 1:
                issues.append("multiple_dates_in_file")

            if partition["ticker"] is not None and valid_df["ticker"].nunique() == 1 and valid_df["ticker"].iloc[0] != partition["ticker"]:
                issues.append("partition_vs_column_ticker_mismatch")
            if partition["date"] is not None and valid_df["date"].nunique() == 1 and valid_df["date"].iloc[0] != partition["date"]:
                issues.append("partition_vs_column_date_mismatch")
            if partition["year"] is not None and valid_df["year"].nunique() == 1 and int(valid_df["year"].iloc[0]) != int(partition["year"]):
                issues.append("partition_vs_column_year_mismatch")
            if partition["month"] is not None and valid_df["month"].nunique() == 1 and int(valid_df["month"].iloc[0]) != int(partition["month"]):
                issues.append("partition_vs_column_month_mismatch")

            negative_or_zero_price_rows = int((valid_df["price"] <= min_expected_price).sum())
            negative_or_zero_size_rows = int((valid_df["size"] <= 0).sum())
            if negative_or_zero_price_rows > 0:
                issues.append("negative_or_zero_price_rows")
            if negative_or_zero_size_rows > 0:
                issues.append("negative_or_zero_size_rows")

            expected_day = pd.Timestamp(partition["date"]).date() if partition["date"] else None
            actual_days = sorted(valid_df["timestamp"].dt.date.dropna().unique().tolist())
            timestamp_partition_mismatch = bool(expected_day is not None and any(day != expected_day for day in actual_days))
            if timestamp_partition_mismatch:
                issues.append("timestamp_out_of_partition_day")

            dup_subset = ["timestamp", "price", "size", "exchange"]
            duplicate_group_rows = int(valid_df.duplicated(subset=dup_subset, keep=False).sum())
            group_sizes = valid_df.groupby(dup_subset, dropna=False).size()
            duplicate_excess_rows = int((group_sizes[group_sizes > 1] - 1).sum())
            duplicate_excess_ratio_pct = float(100.0 * duplicate_excess_rows / max(int(len(valid_df)), 1))
            if duplicate_excess_ratio_pct > duplicate_excess_hard_pct:
                issues.append("duplicate_excess_ratio_gt_hard_cap")
            elif duplicate_excess_ratio_pct > duplicate_excess_warn_pct:
                warns.append("duplicate_excess_ratio_gt_threshold")
            elif duplicate_excess_rows > 0:
                warns.append("duplicate_exact_trade_rows_present")

            off_session_mask = (valid_df["timestamp"].dt.hour < 13) | ((valid_df["timestamp"].dt.hour == 13) & (valid_df["timestamp"].dt.minute < 30)) | (valid_df["timestamp"].dt.hour >= 20)
            off_session_trade_pct = float(100.0 * off_session_mask.sum() / max(int(len(valid_df)), 1))
            if off_session_trade_pct > 0:
                warns.append("off_session_trades_present")
            if len(valid_df) < 10:
                warns.append("rows_lt_10")

            conditions_nonempty_pct = float(
                100.0
                * np.mean(
                    df["conditions"].map(
                        lambda x: len(x) > 0 if isinstance(x, list) else (hasattr(x, "tolist") and len(x.tolist()) > 0)
                    )
                )
            ) if "conditions" in df.columns and len(df) > 0 else 0.0
            max_trades_same_timestamp = int(valid_df.groupby("timestamp", dropna=False).size().max())

            trade_vwap = float((valid_df["price"] * valid_df["size"]).sum() / max(valid_df["size"].sum(), 1.0))
            metrics.update(
                {
                    "rows_after_parse": int(len(valid_df)),
                    "negative_or_zero_price_rows": negative_or_zero_price_rows,
                    "negative_or_zero_size_rows": negative_or_zero_size_rows,
                    "duplicate_group_rows": duplicate_group_rows,
                    "duplicate_excess_rows": duplicate_excess_rows,
                    "duplicate_excess_ratio_pct": duplicate_excess_ratio_pct,
                    "off_session_trade_pct": off_session_trade_pct,
                    "conditions_nonempty_pct": conditions_nonempty_pct,
                    "exchange_nunique": int(valid_df["exchange"].nunique()),
                    "price_min": json_ready(valid_df["price"].min()),
                    "price_max": json_ready(valid_df["price"].max()),
                    "size_sum": json_ready(valid_df["size"].sum()),
                    "size_max": json_ready(valid_df["size"].max()),
                    "trade_vwap": json_ready(trade_vwap),
                    "timestamp_out_of_partition_day": bool(timestamp_partition_mismatch),
                    "expected_partition_date": None if expected_day is None else expected_day.isoformat(),
                    "actual_timestamp_dates_utc": [day.isoformat() for day in actual_days],
                    "timestamp_min_utc": json_ready(valid_df["timestamp"].min()),
                    "timestamp_max_utc": json_ready(valid_df["timestamp"].max()),
                    "max_trades_same_timestamp": max_trades_same_timestamp,
                }
            )

            trade_volume_vs_daily_ratio = None
            trade_volume_vs_1m_ratio = None
            possible_price_scale_factor = None
            possible_price_scale_factor_vs_1m = None

            daily_ref = load_daily_reference(ohlcv_daily_root, partition["ticker"], partition["date"])
            metrics.update(daily_ref)
            if not daily_ref.get("ohlcv_daily_found", False):
                warns.append("missing_ohlcv_daily_reference")
            else:
                daily_low = pd.to_numeric(pd.Series([daily_ref.get("l")]), errors="coerce").iloc[0]
                daily_high = pd.to_numeric(pd.Series([daily_ref.get("h")]), errors="coerce").iloc[0]
                daily_vol = pd.to_numeric(pd.Series([daily_ref.get("v")]), errors="coerce").iloc[0]
                daily_vw = pd.to_numeric(pd.Series([daily_ref.get("vw")]), errors="coerce").iloc[0]
                tol_low = float(daily_low) * (daily_range_tolerance_pct / 100.0) if pd.notna(daily_low) else 0.0
                tol_high = float(daily_high) * (daily_range_tolerance_pct / 100.0) if pd.notna(daily_high) else 0.0
                outside_daily = False
                possible_volume_scale_factor = None
                trade_price_min = float(valid_df["price"].min())
                trade_price_max = float(valid_df["price"].max())
                trade_size_sum = float(valid_df["size"].sum())
                if pd.notna(daily_low) and float(valid_df["price"].min()) < float(daily_low) - tol_low:
                    outside_daily = True
                if pd.notna(daily_high) and float(valid_df["price"].max()) > float(daily_high) + tol_high:
                    outside_daily = True
                if pd.notna(daily_vol) and float(daily_vol) > 0:
                    possible_volume_scale_factor = trade_size_sum / float(daily_vol)
                    trade_volume_vs_daily_ratio = possible_volume_scale_factor
                    metrics["trade_volume_vs_daily_ratio"] = json_ready(trade_volume_vs_daily_ratio)
                if pd.notna(daily_vw) and float(daily_vw) > 0:
                    metrics["trade_vwap_vs_daily_vw_diff_pct"] = json_ready(abs(trade_vwap - float(daily_vw)) / float(daily_vw) * 100.0)
                    possible_price_scale_factor = trade_vwap / float(daily_vw)
                if outside_daily:
                    issues.append("trade_price_outside_daily_range")
                metrics["possible_price_scale_factor_vs_daily"] = json_ready(possible_price_scale_factor)
                metrics["possible_volume_scale_factor_vs_daily"] = json_ready(possible_volume_scale_factor)

            m1_ref = load_1m_reference(ohlcv_1m_root, partition["ticker"], partition["date"])
            metrics.update(m1_ref)
            if not m1_ref.get("ohlcv_1m_found", False):
                warns.append("missing_ohlcv_1m_reference")
            else:
                low_1m = pd.to_numeric(pd.Series([m1_ref.get("ohlcv_1m_low_min")]), errors="coerce").iloc[0]
                high_1m = pd.to_numeric(pd.Series([m1_ref.get("ohlcv_1m_high_max")]), errors="coerce").iloc[0]
                vw_1m = pd.to_numeric(pd.Series([m1_ref.get("ohlcv_1m_vw_mean")]), errors="coerce").iloc[0]
                if pd.notna(vw_1m) and float(vw_1m) > 0:
                    possible_price_scale_factor_vs_1m = trade_vwap / float(vw_1m)
                if pd.notna(low_1m) and pd.notna(high_1m):
                    if float(valid_df["price"].min()) < float(low_1m) or float(valid_df["price"].max()) > float(high_1m):
                        warns.append("trade_price_outside_1m_range")
                vol_1m = pd.to_numeric(pd.Series([m1_ref.get("ohlcv_1m_volume_sum")]), errors="coerce").iloc[0]
                if pd.notna(vol_1m) and float(vol_1m) > 0:
                    trade_volume_vs_1m_ratio = float(valid_df["size"].sum()) / float(vol_1m)
                    metrics["trade_volume_vs_1m_ratio"] = json_ready(trade_volume_vs_1m_ratio)
            metrics["possible_price_scale_factor_vs_1m"] = json_ready(possible_price_scale_factor_vs_1m)

            scale_mismatch_confidence = detect_scale_mismatch_confidence(
                price_factor_daily=possible_price_scale_factor,
                price_factor_1m=possible_price_scale_factor_vs_1m,
                volume_ratio_daily=trade_volume_vs_daily_ratio,
                volume_ratio_1m=trade_volume_vs_1m_ratio,
            )
            metrics["scale_mismatch_confidence"] = scale_mismatch_confidence
            metrics["scale_mismatch_detected"] = scale_mismatch_confidence in {"strong", "probable"}

            if scale_mismatch_confidence == "strong":
                if "trade_price_outside_daily_range" in issues:
                    issues = [x for x in issues if x != "trade_price_outside_daily_range"]
                warns.append("possible_corporate_action_scale_mismatch")
                if "trade_price_outside_1m_range" in warns:
                    warns = [x for x in warns if x != "trade_price_outside_1m_range"]
                warns.append("possible_corporate_action_scale_mismatch_vs_daily")
                warns.append("possible_corporate_action_scale_mismatch_vs_1m")
            elif scale_mismatch_confidence == "probable":
                if "trade_price_outside_daily_range" in issues:
                    issues = [x for x in issues if x != "trade_price_outside_daily_range"]
                warns.append("possible_corporate_action_scale_mismatch")

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
    ap = argparse.ArgumentParser(description="Validate one market.parquet under Agent02 trades v2 contract")
    ap.add_argument("--file", required=True)
    ap.add_argument("--expected-root", default="")
    ap.add_argument("--run-id", default="manual")
    ap.add_argument("--batch-id", default="manual")
    ap.add_argument("--scan-reason", default="manual_recheck")
    ap.add_argument("--validation-kind", default="revalidation_only")
    ap.add_argument("--ohlcv-daily-root", default="")
    ap.add_argument("--ohlcv-1m-root", default="")
    ap.add_argument("--duplicate-excess-warn-pct", type=float, default=3.0)
    ap.add_argument("--duplicate-excess-hard-pct", type=float, default=10.0)
    ap.add_argument("--daily-range-tolerance-pct", type=float, default=1.0)
    ap.add_argument("--min-expected-price", type=float, default=0.0)
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    expected_root = Path(args.expected_root) if str(args.expected_root).strip() else None
    ohlcv_daily_root = Path(args.ohlcv_daily_root) if str(args.ohlcv_daily_root).strip() else None
    ohlcv_1m_root = Path(args.ohlcv_1m_root) if str(args.ohlcv_1m_root).strip() else None

    res = validate_trades_file(
        file_path=Path(args.file),
        expected_root=expected_root,
        run_id=args.run_id,
        batch_id=args.batch_id,
        scan_reason=args.scan_reason,
        validation_kind=args.validation_kind,
        ohlcv_daily_root=ohlcv_daily_root,
        ohlcv_1m_root=ohlcv_1m_root,
        duplicate_excess_warn_pct=float(args.duplicate_excess_warn_pct),
        duplicate_excess_hard_pct=float(args.duplicate_excess_hard_pct),
        daily_range_tolerance_pct=float(args.daily_range_tolerance_pct),
        min_expected_price=float(args.min_expected_price),
    )
    payload = json.dumps(res, indent=2, ensure_ascii=False)
    if str(args.out_json).strip():
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()

