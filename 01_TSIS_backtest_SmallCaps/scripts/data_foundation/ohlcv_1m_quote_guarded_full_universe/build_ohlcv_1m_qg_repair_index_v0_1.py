from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from qg_full_universe_common import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_REPAIR_SHARD_ROOTS,
    atomic_write_json,
    base_manifest,
    build_run_root,
    file_stat,
    iter_repair_shards,
    make_run_id,
    parse_repair_shard,
    parse_years,
    utc_now,
    write_csv,
    write_heartbeat,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build repair shard index for quote-guarded full-universe materialization.")
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--years", required=True, help="Year list or range, e.g. 2026 or 2005-2026")
    p.add_argument("--run-id", default=None)
    p.add_argument("--repair-shard-root", action="append", type=Path, default=None)
    p.add_argument("--heartbeat-every-shards", type=int, default=50000)
    return p


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    years = parse_years(args.years)
    roots = args.repair_shard_root or DEFAULT_REPAIR_SHARD_ROOTS
    run_id = args.run_id or make_run_id("qg_repair_index")
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
        mode="build_repair_index",
        input_roots={"repair_shard_roots": [str(x) for x in roots]},
        output_roots={"output_root": str(args.output_root), "run_root": str(run_root)},
        expected_scope={"years": years},
        monitor_command=monitor_cmd,
        resume_policy="safe_to_rerun_same_run_id_rewrites_index_before_materialization",
        overwrite_policy="no_dataset_output_written_by_this_script",
        success_criteria=["repair_index_year_YYYY.csv exists for every requested year", "repair_index_summary.json exists"],
    )
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    print("run_id", run_id)
    print("mode build_repair_index")
    print("repair_shard_roots", [str(x) for x in roots])
    print("output_root", args.output_root)
    print("run_root", run_root)
    print("monitor", monitor_cmd)

    started = time.time()
    rows_by_year: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    seen_keys: Dict[tuple, str] = {}
    duplicate_keys: List[Dict[str, Any]] = []
    total_shards = 0
    total_bytes = 0

    for path in iter_repair_shards(roots, years):
        meta = parse_repair_shard(path)
        if not meta:
            continue
        stat = file_stat(path)
        key = (meta["year"], meta["ticker"], meta["month"])
        total_shards += 1
        total_bytes += int(stat["bytes"])
        row = {
            "year": meta["year"],
            "ticker": meta["ticker"],
            "month": meta["month"],
            "repair_shard_path": str(path),
            "bytes": stat["bytes"],
            "mtime_utc": stat["mtime_utc"],
            "root": str(next((root for root in roots if str(path).lower().startswith(str(root).lower())), "")),
        }
        if key in seen_keys:
            duplicate_keys.append({**row, "first_path": seen_keys[key]})
            # Keep the latest mtime shard, but expose duplicate in summary.
            existing_rows = rows_by_year[meta["year"]]
            for i, existing in enumerate(existing_rows):
                if (existing["year"], existing["ticker"], existing["month"]) == key:
                    if str(row["mtime_utc"]) >= str(existing["mtime_utc"]):
                        existing_rows[i] = row
                        seen_keys[key] = str(path)
                    break
        else:
            seen_keys[key] = str(path)
            rows_by_year[meta["year"]].append(row)
        if total_shards % max(1, args.heartbeat_every_shards) == 0:
            write_heartbeat(
                run_root,
                {
                    "run_id": run_id,
                    "status": "running",
                    "stage": "indexing_repair_shards",
                    "elapsed_seconds": round(time.time() - started, 1),
                    "active_ticker": meta["ticker"],
                    "completed_tickers": len(set(k[:2] for k in seen_keys)),
                    "total_tickers": "unknown_until_index_finished",
                    "repair_shards_seen": total_shards,
                    "repair_shard_bytes_seen": total_bytes,
                    "rows_written": 0,
                    "repairs_applied": 0,
                    "failed_tickers": 0,
                },
            )

    summary: Dict[str, Any] = {
        "run_id": run_id,
        "status": "indexed",
        "created_at_utc": utc_now(),
        "years": years,
        "repair_shard_roots": [str(x) for x in roots],
        "run_root": str(run_root),
        "total_indexed_shards": sum(len(v) for v in rows_by_year.values()),
        "total_seen_shards": total_shards,
        "total_indexed_bytes": total_bytes,
        "duplicate_key_count": len(duplicate_keys),
        "duplicate_keys_path": str(run_root / "duplicate_repair_index_keys.json") if duplicate_keys else None,
        "years_summary": {},
    }

    if duplicate_keys:
        atomic_write_json(run_root / "duplicate_repair_index_keys.json", {"duplicates": duplicate_keys})

    for year in years:
        records = sorted(rows_by_year.get(year, []), key=lambda r: (str(r["ticker"]), int(r["month"])))
        out = run_root / f"repair_index_year_{year}.csv"
        write_csv(out, records, ["year", "ticker", "month", "repair_shard_path", "bytes", "mtime_utc", "root"])
        summary["years_summary"][str(year)] = {
            "repair_shards": len(records),
            "tickers_with_repairs": len(set(str(r["ticker"]) for r in records)),
            "bytes": sum(int(r["bytes"]) for r in records),
            "repair_index_path": str(out),
        }

    atomic_write_json(run_root / "repair_index_summary.json", summary)
    write_heartbeat(
        run_root,
        {
            "run_id": run_id,
            "status": "complete",
            "stage": "repair_index_written",
            "elapsed_seconds": round(time.time() - started, 1),
            "active_ticker": None,
            "completed_tickers": len(set(k[:2] for k in seen_keys)),
            "total_tickers": len(set(k[:2] for k in seen_keys)),
            "repair_shards_seen": total_shards,
            "repair_shard_bytes_seen": total_bytes,
            "rows_written": 0,
            "repairs_applied": 0,
            "failed_tickers": 0,
        },
    )
    atomic_write_json(run_root / "final_manifest.json", {**summary, "finished_at_utc": utc_now(), "final_status": "complete"})
    print(f"repair_index_summary={run_root / 'repair_index_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
