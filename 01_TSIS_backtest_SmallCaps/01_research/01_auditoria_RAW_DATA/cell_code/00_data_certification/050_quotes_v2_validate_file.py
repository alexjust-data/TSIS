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

VALIDATOR_VERSION = "quotes_v2_validate_file/0.1.1"
PARTITION_RE = re.compile(
    r"(?P<ticker>[^\\/]+)[\\/]year=(?P<year>\d{4})[\\/]month=(?P<month>\d{2})[\\/]day=(?P<day>\d{2})[\\/]quotes\.parquet$"
)
REQUIRED_COLUMNS = ["timestamp", "bid_price", "ask_price", "bid_size", "ask_size"]


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
        dt = pd.Timestamp(f"{gd['year']}-{gd['month']}-{gd['day']}").normalize()
    except Exception:
        issues.append("unparseable_partition_date")
        dt = pd.NaT
    return {
        "ticker": gd["ticker"],
        "date": None if pd.isna(dt) else dt.strftime("%Y-%m-%d"),
        "year": int(gd["year"]),
        "month": int(gd["month"]),
        "day": int(gd["day"]),
        "issues": issues,
    }


def infer_ts_unit(series: pd.Series) -> str | None:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    vmax = float(s.abs().max())
    if vmax >= 1e17:
        return "ns"
    if vmax >= 1e14:
        return "us"
    if vmax >= 1e11:
        return "ms"
    if vmax >= 1e9:
        return "s"
    return None


def to_utc_timestamp(series: pd.Series) -> tuple[pd.Series, str | None]:
    unit = infer_ts_unit(series)
    if unit is None:
        return pd.to_datetime(pd.Series([], dtype="datetime64[ns, UTC]"), utc=True, errors="coerce"), None
    ts = pd.to_datetime(pd.to_numeric(series, errors="coerce"), unit=unit, utc=True, errors="coerce")
    return ts, unit


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


def validate_quotes_file(
    *,
    file_path: Path,
    expected_root: Path | None,
    run_id: str,
    batch_id: str,
    scan_reason: str,
    validation_kind: str,
    crossed_ratio_threshold_pct: float,
    hard_fail_crossed_pct: float,
    hard_fail_ask_integer_pct: float,
    hard_fail_ask_int_crossed_pct: float,
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
        base.update({
            "severity": severity,
            "issues": issues,
            "warns": warns,
            "action": decide_action(severity),
            "metrics_json": {"size_bytes": None},
        })
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
        base.update({
            "severity": severity,
            "issues": issues,
            "warns": warns,
            "action": decide_action(severity),
            "metrics_json": {"size_bytes": size_bytes, "read_error": repr(exc)},
        })
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

    expected_numeric_float = {"bid_price", "ask_price"}
    expected_numeric_int = {"timestamp", "bid_size", "ask_size"}
    for c in expected_numeric_float:
        got = dtypes.get(c)
        if got is not None and not any(x in got for x in ["double", "float", "decimal"]):
            dtype_mismatches.append(f"{c}:{got}")
    for c in expected_numeric_int:
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
        "partition_year": partition["year"],
        "partition_month": partition["month"],
        "partition_day": partition["day"],
    }

    if not missing_required_cols:
        df = table.select([c for c in REQUIRED_COLUMNS if c in columns]).to_pandas()
        base["rows"] = int(len(df))

        ts = pd.to_numeric(df["timestamp"], errors="coerce")
        bid = pd.to_numeric(df["bid_price"], errors="coerce")
        ask = pd.to_numeric(df["ask_price"], errors="coerce")
        bid_size = pd.to_numeric(df["bid_size"], errors="coerce")
        ask_size = pd.to_numeric(df["ask_size"], errors="coerce")

        invalid_after_parse = ts.isna() | bid.isna() | ask.isna() | bid_size.isna() | ask_size.isna()
        valid_df = pd.DataFrame({
            "timestamp": ts,
            "bid_price": bid,
            "ask_price": ask,
            "bid_size": bid_size,
            "ask_size": ask_size,
        })
        valid_df = valid_df[~invalid_after_parse].copy()
        if valid_df.empty:
            issues.append("all_rows_invalid_after_parse")
        else:
            ts_utc, ts_unit = to_utc_timestamp(valid_df["timestamp"])
            valid_df["ts_utc"] = ts_utc
            if valid_df["ts_utc"].isna().all():
                issues.append("all_rows_invalid_after_parse")
            else:
                timestamp_partition_mismatch = False
                expected_day = None
                actual_days = []
                if partition["date"] is not None:
                    expected_day = pd.Timestamp(partition["date"]).date()
                    actual_days = sorted(valid_df["ts_utc"].dt.date.dropna().unique().tolist())
                    timestamp_partition_mismatch = any(day != expected_day for day in actual_days)
                    if timestamp_partition_mismatch:
                        warns.append("timestamp_out_of_partition_day")
                crossed_rows = int((valid_df["bid_price"] > valid_df["ask_price"]).sum())
                negative_price_rows = int(((valid_df["bid_price"] < 0) | (valid_df["ask_price"] < 0)).sum())
                base_n = max(int(len(valid_df)), 1)
                crossed_ratio_pct = float(crossed_rows / base_n * 100.0)
                ask_integer_pct = float(np.mean(np.isclose(valid_df["ask_price"] % 1.0, 0.0)) * 100.0)
                bid_integer_pct = float(np.mean(np.isclose(valid_df["bid_price"] % 1.0, 0.0)) * 100.0)
                ask_eq_round_bid_pct = float(np.mean(np.isclose(valid_df["ask_price"], np.round(valid_df["bid_price"]))) * 100.0)

                if negative_price_rows > 0:
                    issues.append("negative_prices_any_row")
                if crossed_rows > 0:
                    if crossed_ratio_pct > hard_fail_crossed_pct:
                        issues.append("crossed_ratio_gt_hard_cap")
                    if crossed_ratio_pct > crossed_ratio_threshold_pct:
                        issues.append("crossed_ratio_gt_threshold")
                    else:
                        warns.append("crossed_rows_present_but_under_threshold")
                if ask_integer_pct > hard_fail_ask_integer_pct and crossed_ratio_pct > hard_fail_ask_int_crossed_pct:
                    issues.append("ask_integer_with_crossed_anomaly")

                metrics.update({
                    "timestamp_unit_inferred": ts_unit,
                    "rows_after_parse": int(len(valid_df)),
                    "crossed_rows": crossed_rows,
                    "crossed_ratio_pct": crossed_ratio_pct,
                    "negative_price_rows": negative_price_rows,
                    "ask_integer_pct": ask_integer_pct,
                    "bid_integer_pct": bid_integer_pct,
                    "ask_eq_round_bid_pct": ask_eq_round_bid_pct,
                    "expected_partition_date": None if expected_day is None else expected_day.isoformat(),
                    "actual_timestamp_dates_utc": [day.isoformat() for day in actual_days],
                    "timestamp_out_of_partition_day": bool(timestamp_partition_mismatch),
                    "ts_min_utc": json_ready(valid_df["ts_utc"].min()),
                    "ts_max_utc": json_ready(valid_df["ts_utc"].max()),
                })

    issues = sorted(set(issues))
    warns = sorted(set(warns))
    if issues:
        severity = "HARD_FAIL"
    elif warns:
        severity = "SOFT_FAIL"
    else:
        severity = "PASS"

    base.update({
        "severity": severity,
        "issues": issues,
        "warns": warns,
        "action": decide_action(severity),
        "metrics_json": {k: json_ready(v) for k, v in metrics.items()},
    })
    return base


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate one quotes.parquet under Agent02 v2 contract")
    ap.add_argument("--file", required=True)
    ap.add_argument("--expected-root", default="")
    ap.add_argument("--run-id", default="manual")
    ap.add_argument("--batch-id", default="manual")
    ap.add_argument("--scan-reason", default="manual_recheck")
    ap.add_argument("--validation-kind", default="revalidation_only")
    ap.add_argument("--crossed-ratio-threshold-pct", type=float, default=0.8)
    ap.add_argument("--hard-fail-crossed-pct", type=float, default=5.0)
    ap.add_argument("--hard-fail-ask-integer-pct", type=float, default=95.0)
    ap.add_argument("--hard-fail-ask-int-crossed-pct", type=float, default=20.0)
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    expected_root = Path(args.expected_root) if str(args.expected_root).strip() else None
    res = validate_quotes_file(
        file_path=Path(args.file),
        expected_root=expected_root,
        run_id=args.run_id,
        batch_id=args.batch_id,
        scan_reason=args.scan_reason,
        validation_kind=args.validation_kind,
        crossed_ratio_threshold_pct=float(args.crossed_ratio_threshold_pct),
        hard_fail_crossed_pct=float(args.hard_fail_crossed_pct),
        hard_fail_ask_integer_pct=float(args.hard_fail_ask_integer_pct),
        hard_fail_ask_int_crossed_pct=float(args.hard_fail_ask_int_crossed_pct),
    )
    payload = json.dumps(res, indent=2, ensure_ascii=False)
    if str(args.out_json).strip():
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
