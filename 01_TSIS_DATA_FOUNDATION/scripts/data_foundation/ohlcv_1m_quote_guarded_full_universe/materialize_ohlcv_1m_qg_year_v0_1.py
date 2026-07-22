from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from qg_full_universe_common import (
    DATASET_ID,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_RAW_ROOT,
    atomic_write_json,
    base_manifest,
    build_run_root,
    read_csv_dicts,
    utc_now,
    write_heartbeat,
)

PRICE_COLS = ["o", "h", "l", "c"]
REPAIR_COLS = ["o_qg", "h_qg", "l_qg", "c_qg"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Materialize one year of OHLCV 1m quote-guarded full universe.")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--run-id", required=True, help="Existing run id produced by plan/index or a new materialization run id.")
    p.add_argument("--task-plan", type=Path, required=True)
    p.add_argument("--repair-index", type=Path, required=True)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--tickers", default=None, help="Optional comma-separated ticker subset for smoke/pilot.")
    p.add_argument("--limit-tickers", type=int, default=None)
    p.add_argument("--compression", default="zstd", choices=["zstd", "snappy", "gzip", "brotli", "none"])
    p.add_argument("--preserve-raw-price-columns", action="store_true", default=True)
    p.add_argument("--early-inspection-after-tickers", type=int, default=3)
    p.add_argument("--pause-after-early-inspection", action="store_true")
    p.add_argument("--heartbeat-every-sec", type=float, default=30.0)
    return p


def load_repair_index(path: Path, year: int) -> Dict[Tuple[str, int], Path]:
    if not path.exists():
        raise FileNotFoundError(f"missing repair index: {path}")
    rows = read_csv_dicts(path)
    index: Dict[Tuple[str, int], Path] = {}
    for row in rows:
        if int(row["year"]) != year:
            continue
        key = (row["ticker"], int(row["month"]))
        shard = Path(row["repair_shard_path"])
        if not shard.exists():
            raise FileNotFoundError(f"repair shard listed in index is missing: {shard}")
        index[key] = shard
    return index


def load_tasks(path: Path, year: int, tickers: Optional[List[str]], limit: Optional[int]) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"missing task plan: {path}")
    rows = read_csv_dicts(path)
    allowed = set(tickers) if tickers else None
    tasks: List[Dict[str, Any]] = []
    for row in rows:
        if int(row["year"]) != year:
            continue
        ticker = row["ticker"]
        if allowed is not None and ticker not in allowed:
            continue
        files = json.loads(row["input_files_json"])
        months = json.loads(row["months"])
        tasks.append({"year": year, "ticker": ticker, "input_files": files, "months": months})
    tasks.sort(key=lambda x: x["ticker"])
    if limit is not None:
        tasks = tasks[:limit]
    return tasks


def normalize_ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce").dt.floor("min")


def apply_repairs(raw: pd.DataFrame, repairs: Optional[pd.DataFrame], *, source_shard: Optional[str], preserve_raw: bool) -> pd.DataFrame:
    out = raw.copy()
    for col in PRICE_COLS:
        if col not in out.columns:
            raise ValueError(f"raw file missing required price column {col}")
    if "ts_utc" not in out.columns:
        raise ValueError("raw file missing required ts_utc column")
    if preserve_raw:
        for col in PRICE_COLS:
            out[f"{col}_raw"] = out[col]
    out["_qg_key"] = normalize_ts(out["ts_utc"])
    out["quote_guarded_repair_applied"] = False
    out["quote_guarded_view"] = "raw_1m_plus_quote_guarded_overlay"
    out["repair_lookup_state"] = "indexed_no_repair_rows"
    out["repair_state"] = pd.NA
    out["repair_reason"] = pd.NA
    out["source_quote_guarded_repair_manifest"] = source_shard or "indexed_no_repair_rows"

    if repairs is None or repairs.empty:
        return out.drop(columns=["_qg_key"])

    rep = repairs.copy()
    rep["_qg_key"] = normalize_ts(rep["ts_utc"])
    keep_cols = ["_qg_key", "repair_state", "repair_reason"] + [c for c in REPAIR_COLS if c in rep.columns]
    optional_cols = [
        "vw_quote_guarded_status",
        "quote_bid_floor",
        "quote_ask_cap",
        "quote_mid_p50",
        "quote_count",
        "source_quotes_path",
    ]
    keep_cols += [c for c in optional_cols if c in rep.columns]
    rep = rep[keep_cols].drop_duplicates(subset=["_qg_key"], keep="last")
    merged = out.merge(rep, on="_qg_key", how="left", suffixes=("", "_repair"))
    applied = merged["repair_state_repair"].notna() if "repair_state_repair" in merged.columns else merged["repair_state"].notna()
    if "repair_state_repair" in merged.columns:
        repair_state_col = "repair_state_repair"
        repair_reason_col = "repair_reason_repair"
    else:
        repair_state_col = "repair_state"
        repair_reason_col = "repair_reason"
    applied = applied & merged[repair_state_col].astype(str).str.contains("ohlc", case=False, na=False)
    for raw_col, repair_col in zip(PRICE_COLS, REPAIR_COLS):
        if repair_col in merged.columns:
            merged.loc[applied & merged[repair_col].notna(), raw_col] = merged.loc[applied & merged[repair_col].notna(), repair_col]
    merged.loc[applied, "quote_guarded_repair_applied"] = True
    merged.loc[applied, "repair_lookup_state"] = "repair_rows_found"
    merged.loc[applied, "repair_state"] = merged.loc[applied, repair_state_col]
    merged.loc[applied, "repair_reason"] = merged.loc[applied, repair_reason_col]
    merged["source_quote_guarded_repair_manifest"] = source_shard or "repair_index_resolved"
    drop_cols = [c for c in merged.columns if c in REPAIR_COLS or c.endswith("_repair") or c == "_qg_key"]
    return merged.drop(columns=drop_cols)


def validate_output(df: pd.DataFrame) -> List[str]:
    issues: List[str] = []
    missing = [c for c in ["ts_utc", "o", "h", "l", "c", "v"] if c not in df.columns]
    if missing:
        return [f"missing_required_columns={missing}"]
    prices = df[["o", "h", "l", "c"]].apply(pd.to_numeric, errors="coerce")
    if prices.isna().any().any():
        issues.append("nan_price_after_materialization")
    bad_high = prices["h"] < prices[["o", "l", "c"]].max(axis=1)
    bad_low = prices["l"] > prices[["o", "h", "c"]].min(axis=1)
    if bool(bad_high.any()):
        issues.append(f"bad_high_rows={int(bad_high.sum())}")
    if bool(bad_low.any()):
        issues.append(f"bad_low_rows={int(bad_low.sum())}")
    vol = pd.to_numeric(df["v"], errors="coerce")
    if bool((vol < 0).any()):
        issues.append(f"negative_volume_rows={int((vol < 0).sum())}")
    return issues


def month_from_path(path: Path) -> int:
    for part in path.parts:
        if part.startswith("month="):
            return int(part.split("=", 1)[1])
    raise ValueError(f"cannot infer month from path: {path}")


def write_inspection_sample(run_root: Path, year: int, ticker: str, summary: Dict[str, Any], outputs: List[Path]) -> None:
    sample_dir = run_root / "inspection_samples" / f"year={year}"
    sample_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(sample_dir / f"{ticker}_summary.json", summary)
    rows_written = False
    repair_rows_written = False
    for out_path in outputs:
        try:
            df = pd.read_parquet(out_path)
        except Exception:
            continue
        if not rows_written:
            cols = [c for c in ["ticker", "ts_utc", "o", "h", "l", "c", "v", "vw", "n", "quote_guarded_repair_applied", "repair_lookup_state", "repair_state", "source_quote_guarded_repair_manifest"] if c in df.columns]
            pd.concat([df.head(10), df.tail(10)]).drop_duplicates().loc[:, cols].to_csv(sample_dir / f"{ticker}_sample_rows.csv", index=False)
            rows_written = True
        if "quote_guarded_repair_applied" in df.columns:
            repaired = df[df["quote_guarded_repair_applied"].fillna(False)]
            if not repaired.empty and not repair_rows_written:
                cols = [c for c in ["ticker", "ts_utc", "o_raw", "h_raw", "l_raw", "c_raw", "o", "h", "l", "c", "v", "repair_state", "repair_reason", "source_quote_guarded_repair_manifest"] if c in repaired.columns]
                repaired.head(50).loc[:, cols].to_csv(sample_dir / f"{ticker}_repair_rows.csv", index=False)
                repair_rows_written = True
    if not repair_rows_written:
        (sample_dir / f"{ticker}_repair_rows.csv").write_text("no_repair_rows_for_sample\n", encoding="utf-8")


def process_ticker(
    task: Dict[str, Any],
    *,
    repair_index: Dict[Tuple[str, int], Path],
    output_root: Path,
    run_root: Path,
    run_id: str,
    compression: str,
    preserve_raw: bool,
    resume: bool,
) -> Dict[str, Any]:
    year = int(task["year"])
    ticker = task["ticker"]
    commit_path = run_root / "commits" / f"year={year}" / f"{ticker}.json"
    final_ticker_dir = output_root / f"year={year}" / f"ticker={ticker}"
    tmp_ticker_dir = run_root / "_tmp" / f"year={year}" / f"ticker={ticker}"
    if resume and commit_path.exists() and final_ticker_dir.exists():
        existing = json.loads(commit_path.read_text(encoding="utf-8"))
        return {**existing, "skipped_existing_commit": True}
    if tmp_ticker_dir.exists():
        shutil.rmtree(tmp_ticker_dir)
    tmp_ticker_dir.mkdir(parents=True, exist_ok=True)

    total_input_rows = 0
    total_output_rows = 0
    total_repairs = 0
    outputs: List[Path] = []
    issues: List[str] = []
    repair_shards_used: List[str] = []
    no_repair_months: List[int] = []

    for input_file in sorted(task["input_files"]):
        raw_path = Path(input_file)
        month = month_from_path(raw_path)
        raw = pd.read_parquet(raw_path)
        total_input_rows += len(raw)
        repair_path = repair_index.get((ticker, month))
        repairs = None
        if repair_path is not None:
            repairs = pd.read_parquet(repair_path)
            repair_shards_used.append(str(repair_path))
        else:
            no_repair_months.append(month)
        out_df = apply_repairs(raw, repairs, source_shard=str(repair_path) if repair_path else None, preserve_raw=preserve_raw)
        out_df["dataset_id"] = DATASET_ID
        out_df["build_run_id"] = run_id
        out_df["created_utc"] = utc_now()
        out_df["source_raw_path"] = str(raw_path)
        if "ticker" not in out_df.columns:
            out_df["ticker"] = ticker
        out_issues = validate_output(out_df)
        issues.extend([f"month={month}:{x}" for x in out_issues])
        repairs_applied = int(out_df["quote_guarded_repair_applied"].fillna(False).sum())
        total_repairs += repairs_applied
        total_output_rows += len(out_df)
        month_dir = tmp_ticker_dir / f"month={month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)
        out_path = month_dir / "part-000.parquet"
        parquet_compression = None if compression == "none" else compression
        out_df.to_parquet(out_path, index=False, compression=parquet_compression)
        outputs.append(out_path)
        try:
            check = pd.read_parquet(out_path, columns=["ts_utc"])
            if len(check) != len(out_df):
                issues.append(f"month={month}:parquet_readback_row_mismatch")
        except Exception as exc:
            issues.append(f"month={month}:parquet_readback_failed:{exc}")

    status = "complete" if not issues and total_input_rows == total_output_rows else "failed"
    summary = {
        "run_id": run_id,
        "year": year,
        "ticker": ticker,
        "status": status,
        "finished_at_utc": utc_now(),
        "input_files": task["input_files"],
        "output_dir": str(final_ticker_dir),
        "temp_dir": str(tmp_ticker_dir),
        "input_rows": total_input_rows,
        "output_rows": total_output_rows,
        "repairs_applied": total_repairs,
        "repair_shards_used": sorted(set(repair_shards_used)),
        "indexed_no_repair_months": sorted(set(no_repair_months)),
        "issues": issues,
    }
    if status != "complete":
        fail_dir = run_root / "failures" / f"year={year}"
        fail_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(fail_dir / f"{ticker}.json", summary)
        return summary

    if final_ticker_dir.exists():
        if not resume:
            raise FileExistsError(f"final output exists and --resume not set: {final_ticker_dir}")
        shutil.rmtree(final_ticker_dir)
    final_ticker_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_ticker_dir), str(final_ticker_dir))
    final_outputs = sorted(final_ticker_dir.rglob("*.parquet"))
    summary["output_files"] = [str(x) for x in final_outputs]
    atomic_write_json(commit_path, summary)
    return summary


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_root = build_run_root(args.output_root, args.run_id)
    run_root.mkdir(parents=True, exist_ok=True)
    monitor_cmd = (
        f'python "{Path(__file__).with_name("monitor_ohlcv_1m_qg_year_run_v0_1.py")}" '
        f'--run-root "{run_root}" --watch --interval-sec 30 --compact'
    )
    tickers = [x.strip().upper() for x in args.tickers.split(",") if x.strip()] if args.tickers else None
    tasks = load_tasks(args.task_plan, args.year, tickers, args.limit_tickers)
    if args.pause_after_early_inspection and args.early_inspection_after_tickers > 0:
        tasks = tasks[: args.early_inspection_after_tickers]
    repair_index = load_repair_index(args.repair_index, args.year)
    manifest = base_manifest(
        run_id=args.run_id,
        script_path=Path(__file__),
        command_line=sys.argv,
        mode="materialize_year",
        input_roots={"raw_root": str(args.raw_root), "task_plan": str(args.task_plan), "repair_index": str(args.repair_index)},
        output_roots={"output_root": str(args.output_root), "run_root": str(run_root)},
        expected_scope={"year": args.year, "tickers": len(tasks), "workers": args.workers},
        monitor_command=monitor_cmd,
        resume_policy="commit markers by year+ticker; temp ticker dirs are discarded on resume",
        overwrite_policy="final ticker dir overwritten only with --resume after valid commit logic",
        success_criteria=["all requested tickers committed or failed with explicit reason", "year_materialization_summary.json exists"],
    )
    atomic_write_json(run_root / "pre_manifest_materialize_year.json", manifest)
    print("run_id", args.run_id)
    print("mode materialize_year")
    print("year", args.year)
    print("tasks", len(tasks))
    print("workers", args.workers)
    print("output_root", args.output_root)
    print("run_root", run_root)
    print("monitor", monitor_cmd)
    print("early_inspection_after_tickers", args.early_inspection_after_tickers)
    print("pause_after_early_inspection", args.pause_after_early_inspection)

    started = time.time()
    completed = 0
    failed = 0
    rows_written = 0
    repairs_applied = 0
    summaries: List[Dict[str, Any]] = []
    early_written = False
    last_heartbeat = 0.0

    write_heartbeat(
        run_root,
        {
            "run_id": args.run_id,
            "status": "running",
            "stage": "materializing_year",
            "elapsed_seconds": 0,
            "active_ticker": None,
            "completed_tickers": 0,
            "total_tickers": len(tasks),
            "rows_written": 0,
            "repairs_applied": 0,
            "failed_tickers": 0,
            "early_inspection_after_tickers": args.early_inspection_after_tickers,
            "early_inspection_ready": False,
        },
    )

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_ticker = {
            executor.submit(
                process_ticker,
                task,
                repair_index=repair_index,
                output_root=args.output_root,
                run_root=run_root,
                run_id=args.run_id,
                compression=args.compression,
                preserve_raw=args.preserve_raw_price_columns,
                resume=args.resume,
            ): task["ticker"]
            for task in tasks
        }
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                summary = future.result()
            except Exception as exc:
                summary = {"run_id": args.run_id, "year": args.year, "ticker": ticker, "status": "failed", "issues": [repr(exc)], "finished_at_utc": utc_now()}
                fail_dir = run_root / "failures" / f"year={args.year}"
                fail_dir.mkdir(parents=True, exist_ok=True)
                atomic_write_json(fail_dir / f"{ticker}.json", summary)
            summaries.append(summary)
            if summary.get("status") == "complete" or summary.get("skipped_existing_commit"):
                completed += 1
                rows_written += int(summary.get("output_rows", 0) or 0)
                repairs_applied += int(summary.get("repairs_applied", 0) or 0)
                if completed <= max(0, args.early_inspection_after_tickers):
                    output_files = [Path(x) for x in summary.get("output_files", [])]
                    write_inspection_sample(run_root, args.year, summary["ticker"], summary, output_files)
            else:
                failed += 1
            if (not early_written) and args.early_inspection_after_tickers > 0 and completed >= args.early_inspection_after_tickers:
                early_payload = {
                    "run_id": args.run_id,
                    "status": "early_inspection_ready" if not args.pause_after_early_inspection else "paused_for_human_inspection",
                    "created_at_utc": utc_now(),
                    "year": args.year,
                    "completed_tickers": completed,
                    "failed_tickers": failed,
                    "inspection_root": str(run_root / "inspection_samples" / f"year={args.year}"),
                    "resume_command": "rerun materialize_ohlcv_1m_qg_year_v0_1.py with same --run-id and --resume",
                    "pause_after_early_inspection": args.pause_after_early_inspection,
                }
                atomic_write_json(run_root / "early_inspection_ready.json", early_payload)
                write_heartbeat(
                    run_root,
                    {
                        "run_id": args.run_id,
                        "status": early_payload["status"],
                        "stage": "early_inspection_ready",
                        "elapsed_seconds": round(time.time() - started, 1),
                        "active_ticker": ticker,
                        "completed_tickers": completed,
                        "total_tickers": len(tasks),
                        "rows_written": rows_written,
                        "repairs_applied": repairs_applied,
                        "failed_tickers": failed,
                        "early_inspection_ready": True,
                        "inspection_root": early_payload["inspection_root"],
                    },
                )
                early_written = True
            now = time.time()
            if now - last_heartbeat >= args.heartbeat_every_sec:
                write_heartbeat(
                    run_root,
                    {
                        "run_id": args.run_id,
                        "status": "running",
                        "stage": "materializing_year",
                        "elapsed_seconds": round(now - started, 1),
                        "active_ticker": ticker,
                        "completed_tickers": completed,
                        "total_tickers": len(tasks),
                        "rows_written": rows_written,
                        "repairs_applied": repairs_applied,
                        "failed_tickers": failed,
                        "early_inspection_ready": early_written,
                        "inspection_root": str(run_root / "inspection_samples" / f"year={args.year}") if early_written else None,
                    },
                )
                last_heartbeat = now

    final_status = "paused_for_human_inspection" if args.pause_after_early_inspection else ("complete" if failed == 0 else "complete_with_failures")
    final = {
        "run_id": args.run_id,
        "final_status": final_status,
        "finished_at_utc": utc_now(),
        "year": args.year,
        "total_tickers": len(tasks),
        "completed_tickers": completed,
        "failed_tickers": failed,
        "rows_written": rows_written,
        "repairs_applied": repairs_applied,
        "output_root": str(args.output_root),
        "run_root": str(run_root),
        "inspection_root": str(run_root / "inspection_samples" / f"year={args.year}"),
        "summaries": summaries,
    }
    atomic_write_json(run_root / f"year_{args.year}_materialization_summary.json", final)
    atomic_write_json(run_root / "final_manifest_materialize_year.json", final)
    write_heartbeat(
        run_root,
        {
            "run_id": args.run_id,
            "status": final_status,
            "stage": "materialization_finished",
            "elapsed_seconds": round(time.time() - started, 1),
            "active_ticker": None,
            "completed_tickers": completed,
            "total_tickers": len(tasks),
            "rows_written": rows_written,
            "repairs_applied": repairs_applied,
            "failed_tickers": failed,
            "early_inspection_ready": early_written,
            "inspection_root": final["inspection_root"],
        },
    )
    print(f"final_status={final_status} completed={completed} failed={failed} rows={rows_written} repairs={repairs_applied}")
    print(f"summary={run_root / f'year_{args.year}_materialization_summary.json'}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
