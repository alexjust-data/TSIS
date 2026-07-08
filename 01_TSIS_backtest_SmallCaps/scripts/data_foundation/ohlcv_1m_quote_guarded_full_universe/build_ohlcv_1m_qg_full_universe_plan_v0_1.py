from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from qg_full_universe_common import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_RAW_ROOT,
    base_manifest,
    build_run_root,
    file_stat,
    make_run_id,
    parse_raw_partition,
    parse_years,
    utc_now,
    write_csv,
    write_heartbeat,
    atomic_write_json,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build governed task plan for OHLCV 1m quote-guarded full-universe materialization.")
    p.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--years", required=True, help="Year list or range, e.g. 2026 or 2005-2026")
    p.add_argument("--run-id", default=None)
    p.add_argument("--max-files", type=int, default=None, help="Optional smoke cap for enumeration.")
    p.add_argument("--heartbeat-every-files", type=int, default=50000)
    return p


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    years = parse_years(args.years)
    run_id = args.run_id or make_run_id("qg_plan")
    run_root = build_run_root(args.output_root, run_id)
    run_root.mkdir(parents=True, exist_ok=True)

    monitor_cmd = (
        f'python "{Path(__file__).with_name("monitor_ohlcv_1m_qg_year_run_v0_1.py")}" '
        f'--run-root "{run_root}" --watch --interval-sec 30 --compact'
    )
    manifest = base_manifest(
        run_id=run_id,
        script_path=Path(__file__),
        command_line=sys.argv,
        mode="build_plan",
        input_roots={"raw_root": str(args.raw_root)},
        output_roots={"output_root": str(args.output_root), "run_root": str(run_root)},
        expected_scope={"years": years, "max_files": args.max_files},
        monitor_command=monitor_cmd,
        resume_policy="safe_to_rerun_same_run_id_rewrites_task_plan_before_materialization",
        overwrite_policy="no_dataset_output_written_by_this_script",
        success_criteria=["task_plan_year_YYYY.csv exists for every requested year", "plan_summary.json exists"],
    )
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    print("run_id", run_id)
    print("mode build_plan")
    print("raw_root", args.raw_root)
    print("output_root", args.output_root)
    print("run_root", run_root)
    print("monitor", monitor_cmd)

    started = time.time()
    rows_by_year: Dict[int, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    total_files = 0
    total_bytes = 0

    for year in years:
        pattern = f"ticker=*/year={year}/month=*/*.parquet"
        for path in args.raw_root.glob(pattern):
            total_files += 1
            if args.max_files is not None and total_files > args.max_files:
                break
            meta = parse_raw_partition(path)
            if not meta:
                continue
            stat = file_stat(path)
            total_bytes += int(stat["bytes"])
            ticker = meta["ticker"]
            bucket = rows_by_year[year].setdefault(
                ticker,
                {
                    "year": year,
                    "ticker": ticker,
                    "file_count": 0,
                    "total_bytes": 0,
                    "months": set(),
                    "input_files": [],
                },
            )
            bucket["file_count"] += 1
            bucket["total_bytes"] += int(stat["bytes"])
            bucket["months"].add(int(meta["month"]))
            bucket["input_files"].append(str(path))
            if total_files % max(1, args.heartbeat_every_files) == 0:
                write_heartbeat(
                    run_root,
                    {
                        "run_id": run_id,
                        "status": "running",
                        "stage": "enumerating_raw_files",
                        "elapsed_seconds": round(time.time() - started, 1),
                        "active_ticker": ticker,
                        "completed_tickers": sum(len(v) for v in rows_by_year.values()),
                        "total_tickers": "unknown_until_enumeration_finished",
                        "files_seen": total_files,
                        "bytes_seen": total_bytes,
                        "rows_written": 0,
                        "repairs_applied": 0,
                        "failed_tickers": 0,
                    },
                )
        if args.max_files is not None and total_files >= args.max_files:
            break

    summary: Dict[str, Any] = {
        "run_id": run_id,
        "status": "planned",
        "created_at_utc": utc_now(),
        "years": years,
        "raw_root": str(args.raw_root),
        "output_root": str(args.output_root),
        "run_root": str(run_root),
        "total_files": total_files,
        "total_bytes": total_bytes,
        "years_summary": {},
    }

    for year in sorted(rows_by_year):
        out = run_root / f"task_plan_year_{year}.csv"
        records = []
        for ticker, row in sorted(rows_by_year[year].items()):
            records.append(
                {
                    "year": year,
                    "ticker": ticker,
                    "file_count": row["file_count"],
                    "total_bytes": row["total_bytes"],
                    "months": json.dumps(sorted(row["months"])),
                    "input_files_json": json.dumps(row["input_files"]),
                }
            )
        write_csv(out, records, ["year", "ticker", "file_count", "total_bytes", "months", "input_files_json"])
        summary["years_summary"][str(year)] = {
            "tickers": len(records),
            "files": sum(int(r["file_count"]) for r in records),
            "bytes": sum(int(r["total_bytes"]) for r in records),
            "task_plan_path": str(out),
        }

    atomic_write_json(run_root / "plan_summary.json", summary)
    final_payload = {
        "run_id": run_id,
        "status": "complete",
        "stage": "plan_written",
        "elapsed_seconds": round(time.time() - started, 1),
        "active_ticker": None,
        "completed_tickers": sum(v["tickers"] for v in summary["years_summary"].values()),
        "total_tickers": sum(v["tickers"] for v in summary["years_summary"].values()),
        "files_seen": total_files,
        "bytes_seen": total_bytes,
        "rows_written": 0,
        "repairs_applied": 0,
        "failed_tickers": 0,
    }
    write_heartbeat(run_root, final_payload)
    atomic_write_json(run_root / "final_manifest.json", {**summary, "finished_at_utc": utc_now(), "final_status": "complete"})
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
