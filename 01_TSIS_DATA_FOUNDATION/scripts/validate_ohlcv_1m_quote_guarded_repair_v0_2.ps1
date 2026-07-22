param(
    [Parameter(Mandatory=$true)]
    [string]$RunRoot,
    [int]$IntervalSeconds = 300,
    [int]$MaxShardsPerPass = 500,
    [int]$SampleRowsPerShard = 200,
    [int]$MinShardAgeSeconds = 120,
    [string]$PythonExe = "python",
    [switch]$Watch
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $RunRoot)) {
    throw "Missing RunRoot: $RunRoot"
}

$validatorCode = @'
from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

REQUIRED_COLUMNS = {
    "quote_guarded_view",
    "ticker",
    "ts_utc",
    "repair_state",
    "repair_reason",
    "quote_guarded_repair_applied",
    "o_raw",
    "h_raw",
    "l_raw",
    "c_raw",
    "o_qg",
    "h_qg",
    "l_qg",
    "c_qg",
    "vw_quote_guarded_status",
    "quote_bid_floor",
    "quote_ask_cap",
    "quote_count",
    "source_ohlcv_path",
    "source_quotes_path",
    "run_root",
}


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def iter_json(path: Path, cutoff_ts: float | None = None) -> tuple[list[dict], list[str]]:
    rows = []
    bad = []
    if not path.exists():
        return rows, bad
    for item in path.glob("*.json"):
        if cutoff_ts is not None and item.stat().st_mtime > cutoff_ts:
            continue
        obj = read_json(item)
        if obj is None:
            bad.append(str(item))
        else:
            rows.append(obj)
    return rows, bad


def parquet_rows(path: Path) -> tuple[int | None, str]:
    try:
        return pq.ParquetFile(path).metadata.num_rows, ""
    except Exception as exc:
        return None, repr(exc)


def validate_shard(path: Path, run_root: Path, sample_rows: int) -> dict:
    out = {
        "path": str(path),
        "rows": 0,
        "errors": [],
        "warnings": [],
    }
    try:
        pf = pq.ParquetFile(path)
        out["rows"] = int(pf.metadata.num_rows)
        columns = set(pf.schema_arrow.names)
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            out["errors"].append("missing_columns=" + ",".join(missing))
            return out
        cols = sorted(REQUIRED_COLUMNS | {"year", "month"})
        table = pq.read_table(path, columns=[c for c in cols if c in columns])
        df = table.to_pandas()
    except Exception as exc:
        out["errors"].append("parquet_read_error=" + repr(exc))
        return out

    if df.empty:
        out["warnings"].append("empty_shard")
        return out

    if len(df) > sample_rows > 0:
        df = df.sample(n=sample_rows, random_state=17)

    numeric_cols = [
        "o_raw", "h_raw", "l_raw", "c_raw", "o_qg", "h_qg", "l_qg", "c_qg",
        "quote_bid_floor", "quote_ask_cap", "quote_count",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df["ticker"].isna().any() or (df["ticker"].astype(str).str.len() == 0).any():
        out["errors"].append("blank_ticker")
    if df["source_ohlcv_path"].isna().any() or (df["source_ohlcv_path"].astype(str).str.len() == 0).any():
        out["errors"].append("blank_source_ohlcv_path")
    if (df["run_root"].astype(str) != str(run_root)).any():
        out["errors"].append("run_root_mismatch")
    if df["quote_count"].lt(3).any():
        out["errors"].append("quote_count_below_min")
    if df["quote_bid_floor"].gt(df["quote_ask_cap"]).any():
        out["errors"].append("quote_floor_gt_cap")

    repaired = df["quote_guarded_repair_applied"].fillna(False).astype(bool)
    if repaired.any():
        r = df.loc[repaired]
        if (r[["o_qg", "h_qg", "l_qg", "c_qg"]].isna().any(axis=1)).any():
            out["errors"].append("null_qg_ohlc_on_repaired_rows")
        if (r["h_qg"] < r[["o_qg", "c_qg", "l_qg"]].max(axis=1)).any():
            out["errors"].append("invalid_repaired_high")
        if (r["l_qg"] > r[["o_qg", "c_qg", "h_qg"]].min(axis=1)).any():
            out["errors"].append("invalid_repaired_low")
        for col in ("o_qg", "h_qg", "l_qg", "c_qg"):
            below = r[col] < r["quote_bid_floor"] - 1e-9
            above = r[col] > r["quote_ask_cap"] + 1e-9
            if below.any() or above.any():
                out["errors"].append(f"{col}_outside_quote_envelope")
                break

    state = df["repair_state"].astype(str)
    invalid_state = ~state.isin({
        "quote_repairable_ohlc_vw_invalid",
        "quote_repairable_ohlc",
        "vw_invalid_only",
    })
    if invalid_state.any():
        out["errors"].append("invalid_repair_state")

    vw_status = df["vw_quote_guarded_status"].astype(str)
    invalid_vw = ~vw_status.isin({"invalid_not_repaired_from_quotes", "raw_preserved"})
    if invalid_vw.any():
        out["errors"].append("invalid_vw_status")

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True, type=Path)
    ap.add_argument("--max-shards", type=int, default=0)
    ap.add_argument("--sample-rows-per-shard", type=int, default=200)
    ap.add_argument("--min-shard-age-seconds", type=int, default=120)
    args = ap.parse_args()

    run_root = args.run_root
    month_dir = run_root / "month_summaries"
    shard_dir = run_root / "repair_shards"
    status_dir = run_root / "ticker_status"
    report_dir = run_root / "validation"
    report_dir.mkdir(parents=True, exist_ok=True)

    snapshot_cutoff_ts = datetime.now(timezone.utc).timestamp() - max(0, args.min_shard_age_seconds)
    snapshot_cutoff_utc = datetime.fromtimestamp(snapshot_cutoff_ts, tz=timezone.utc).isoformat()

    month_rows, bad_month_json = iter_json(month_dir, cutoff_ts=snapshot_cutoff_ts)
    status_rows, bad_status_json = iter_json(status_dir)
    all_shards = sorted(shard_dir.glob("*.parquet")) if shard_dir.exists() else []
    shards = [
        p for p in all_shards
        if p.stat().st_mtime <= snapshot_cutoff_ts
    ]
    if args.max_shards and len(shards) > args.max_shards:
        random.seed(17)
        shards_to_validate = sorted(random.sample(shards, args.max_shards))
        shards_for_row_total = shards_to_validate
        row_total_scope = "sampled_stable_shards"
    else:
        shards_to_validate = shards
        shards_for_row_total = shards
        row_total_scope = "all_stable_shards"

    stable_shard_names = {p.name for p in shards_for_row_total}
    stable_month_rows = [
        row for row in month_rows
        if not row.get("repair_shard_path")
        or Path(str(row.get("repair_shard_path"))).name in stable_shard_names
    ]
    month_repair_rows = sum(int(row.get("repair_rows", 0) or 0) for row in stable_month_rows)
    month_ohlc_rows = sum(int(row.get("ohlc_repair_rows", 0) or 0) for row in stable_month_rows)
    month_vw_rows = sum(int(row.get("vw_invalid_rows", 0) or 0) for row in stable_month_rows)
    shard_row_total = 0
    bad_parquet = []
    shard_errors = []
    shard_warnings = []

    for shard in shards_for_row_total:
        rows, err = parquet_rows(shard)
        if rows is None:
            bad_parquet.append({"path": str(shard), "error": err})
        else:
            shard_row_total += rows

    for shard in shards_to_validate:
        result = validate_shard(shard, run_root, args.sample_rows_per_shard)
        if result["errors"]:
            shard_errors.append(result)
        if result["warnings"]:
            shard_warnings.append(result)

    summary_repair_shards = {
        str(Path(row.get("repair_shard_path", "")).name)
        for row in stable_month_rows
        if int(row.get("repair_rows", 0) or 0) > 0 and row.get("repair_shard_path")
    }
    actual_shards = stable_shard_names
    missing_shards_from_summaries = sorted(summary_repair_shards - actual_shards)
    orphan_shards = sorted(actual_shards - summary_repair_shards)

    errors = []
    if bad_month_json:
        errors.append("bad_month_summary_json")
    if bad_status_json:
        errors.append("bad_ticker_status_json")
    if bad_parquet:
        errors.append("bad_repair_shard_parquet")
    if missing_shards_from_summaries:
        errors.append("missing_shards_from_month_summaries")
    if shard_row_total != month_repair_rows:
        errors.append("repair_row_total_mismatch")
    if shard_errors:
        errors.append("shard_invariant_errors")

    status_counts = {}
    for row in status_rows:
        status = str(row.get("status", "UNKNOWN"))
        status_counts[status] = status_counts.get(status, 0) + 1

    report = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_root": str(run_root),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "min_shard_age_seconds": args.min_shard_age_seconds,
        "snapshot_cutoff_utc": snapshot_cutoff_utc,
        "row_total_scope": row_total_scope,
        "ticker_status_counts": status_counts,
        "month_summary_files": len(month_rows),
        "stable_month_summary_files": len(stable_month_rows),
        "bad_month_summary_json_count": len(bad_month_json),
        "ticker_status_files": len(status_rows),
        "bad_ticker_status_json_count": len(bad_status_json),
        "repair_shards": len(all_shards),
        "stable_repair_shards": len(shards),
        "counted_repair_shards": len(shards_for_row_total),
        "validated_shards": len(shards_to_validate),
        "bad_parquet_count": len(bad_parquet),
        "month_summary_repair_rows": int(month_repair_rows),
        "month_summary_ohlc_repair_rows": int(month_ohlc_rows),
        "month_summary_vw_invalid_rows": int(month_vw_rows),
        "shard_row_total": int(shard_row_total),
        "missing_shards_from_summaries_count": len(missing_shards_from_summaries),
        "orphan_shards_count": len(orphan_shards),
        "bad_month_json_sample": bad_month_json[:20],
        "bad_status_json_sample": bad_status_json[:20],
        "bad_parquet_sample": bad_parquet[:20],
        "missing_shards_from_summaries_sample": missing_shards_from_summaries[:20],
        "orphan_shards_sample": orphan_shards[:20],
        "shard_errors_sample": shard_errors[:20],
        "shard_warnings_sample": shard_warnings[:20],
    }
    out = report_dir / "latest_validation_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    timestamped = report_dir / ("validation_report_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".json")
    timestamped.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "errors": report["errors"],
        "month_summary_files": report["month_summary_files"],
        "stable_month_summary_files": report["stable_month_summary_files"],
        "repair_shards": report["repair_shards"],
        "stable_repair_shards": report["stable_repair_shards"],
        "counted_repair_shards": report["counted_repair_shards"],
        "validated_shards": report["validated_shards"],
        "month_summary_repair_rows": report["month_summary_repair_rows"],
        "shard_row_total": report["shard_row_total"],
        "row_total_scope": report["row_total_scope"],
        "report": str(out),
    }, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
'@

$tmp = Join-Path $env:TEMP ("tsis_qg_validator_{0}.py" -f $PID)
Set-Content -LiteralPath $tmp -Value $validatorCode -Encoding UTF8

try {
    do {
        Write-Host ("TSIS quote-guarded v0_2 validation pass at {0}" -f (Get-Date).ToString("o"))
        & $PythonExe $tmp --run-root $RunRoot --max-shards $MaxShardsPerPass --sample-rows-per-shard $SampleRowsPerShard --min-shard-age-seconds $MinShardAgeSeconds
        $exit = $LASTEXITCODE
        if ($exit -eq 0) {
            Write-Host "Validation PASS"
        } else {
            Write-Host "Validation FAIL. See validation\latest_validation_report.json under RunRoot."
        }
        if ($Watch) {
            Start-Sleep -Seconds $IntervalSeconds
        }
    } while ($Watch)
} finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}
