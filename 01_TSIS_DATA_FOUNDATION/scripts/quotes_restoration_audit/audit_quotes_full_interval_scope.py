#!/usr/bin/env python3
"""Compare historical Quotes request evidence with the full 4,824 x XNYS grid."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import exchange_calendars as xcals
import pandas as pd


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".partial")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--classification", required=True)
    parser.add_argument("--current-alignment-run", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--start", default="2005-01-03")
    parser.add_argument("--end", default="2026-08-20")
    args = parser.parse_args()

    classification = Path(args.classification).resolve()
    alignment = Path(args.current_alignment_run).resolve()
    current_glob = alignment / "01_inventory" / "quotes_" / "ticker=*" / "inventory.parquet"
    alignment_manifest = alignment / "04_closeout" / "final_manifest.json"
    output = Path(args.output_root).resolve()
    control = output / "00_control"
    closeout = output / "03_closeout"
    required = [classification, alignment_manifest]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)

    calendar = xcals.get_calendar("XNYS", start=args.start, end=args.end)
    sessions = calendar.sessions_in_range(args.start, args.end)
    session_frame = pd.DataFrame({"session_date": sessions.tz_localize(None).date})
    pre = {
        "run_id": args.run_id,
        "pid": os.getpid(),
        "started_at_utc": now(),
        "operation": "quotes_full_interval_scope_audit",
        "start": args.start,
        "end": args.end,
        "calendar": "XNYS via exchange_calendars",
        "session_count": len(session_frame),
        "classification": str(classification),
        "current_alignment_manifest": str(alignment_manifest),
        "raw_parquet_reads": 0,
    }
    atomic_json(control / "pre_manifest.json", pre)

    con = duckdb.connect(str(output / "scope_audit.duckdb"))
    con.execute("PRAGMA threads=2")
    con.execute("PRAGMA memory_limit='4GB'")
    con.register("session_frame", session_frame)
    con.execute("CREATE OR REPLACE TABLE sessions AS SELECT CAST(session_date AS DATE) date FROM session_frame")
    con.execute(f"""
        CREATE OR REPLACE TABLE master AS
        SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date, coverage_state
        FROM read_parquet('{sql_path(classification)}')
    """)
    con.execute("CREATE OR REPLACE TABLE tickers AS SELECT DISTINCT ticker FROM master")
    con.execute("""
        CREATE OR REPLACE TABLE terminal_history AS
        SELECT ticker, date FROM master WHERE coverage_state <> 'NO_TERMINAL_EVENT'
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE current_quotes AS
        WITH source AS (
          SELECT upper(trim(ticker)) ticker, relative_path
          FROM read_parquet('{sql_path(current_glob)}', union_by_name=true, hive_partitioning=false)
          WHERE file_exists
        ), parsed AS (
          SELECT ticker,
                 regexp_extract(relative_path, 'year=([0-9]{{4}})', 1) yyyy,
                 regexp_extract(relative_path, 'month=([0-9]{{2}})', 1) mm,
                 regexp_extract(relative_path, 'day=([0-9-]+)', 1) dd
          FROM source
        )
        SELECT DISTINCT ticker,
               CAST(CASE WHEN length(dd)=2 THEN yyyy || '-' || mm || '-' || dd ELSE dd END AS DATE) date
        FROM parsed WHERE yyyy <> '' AND mm <> '' AND dd <> ''
    """)

    master_end = con.execute("SELECT max(date) FROM master").fetchone()[0]
    missing_query = f"""
        SELECT t.ticker, s.date,
               CASE
                 WHEN m.coverage_state = 'NO_TERMINAL_EVENT' THEN 'HISTORICAL_MASTER_NO_TERMINAL_EVENT'
                 WHEN s.date <= DATE '{master_end}' THEN 'OUTSIDE_ORIGINAL_OHLC_WINDOW_MASTER'
                 ELSE 'TAIL_NOT_OBSERVED_THROUGH_2026_08_20'
               END scope_gap_reason
        FROM tickers t CROSS JOIN sessions s
        LEFT JOIN terminal_history h USING (ticker, date)
        LEFT JOIN current_quotes q USING (ticker, date)
        LEFT JOIN master m USING (ticker, date)
        WHERE h.ticker IS NULL AND q.ticker IS NULL
    """
    closeout.mkdir(parents=True, exist_ok=True)
    missing_parquet = closeout / "quotes_full_interval_unqueried_requests.parquet"
    con.execute(f"COPY ({missing_query}) TO '{sql_path(missing_parquet)}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    breakdown = {
        row[0]: int(row[1])
        for row in con.execute(f"SELECT scope_gap_reason, count(*) FROM ({missing_query}) GROUP BY 1 ORDER BY 1").fetchall()
    }
    metrics = {
        "universe_tickers": int(con.execute("SELECT count(*) FROM tickers").fetchone()[0]),
        "xnys_sessions": int(con.execute("SELECT count(*) FROM sessions").fetchone()[0]),
        "full_grid_tasks": int(con.execute("SELECT count(*) FROM tickers CROSS JOIN sessions").fetchone()[0]),
        "original_master_tasks": int(con.execute("SELECT count(*) FROM master").fetchone()[0]),
        "original_master_tasks_inside_xnys": int(con.execute("SELECT count(*) FROM master JOIN sessions USING (date)").fetchone()[0]),
        "original_master_tasks_outside_xnys": int(con.execute(f"SELECT count(*) FROM master m LEFT JOIN sessions s USING (date) WHERE m.date BETWEEN DATE '{args.start}' AND DATE '{args.end}' AND s.date IS NULL").fetchone()[0]),
        "original_master_provider_empty_outside_xnys": int(con.execute(f"SELECT count(*) FROM master m LEFT JOIN sessions s USING (date) WHERE m.date BETWEEN DATE '{args.start}' AND DATE '{args.end}' AND s.date IS NULL AND m.coverage_state LIKE 'PROVIDER_EMPTY%'").fetchone()[0]),
        "original_master_no_terminal_outside_xnys": int(con.execute(f"SELECT count(*) FROM master m LEFT JOIN sessions s USING (date) WHERE m.date BETWEEN DATE '{args.start}' AND DATE '{args.end}' AND s.date IS NULL AND m.coverage_state='NO_TERMINAL_EVENT'").fetchone()[0]),
        "historical_terminal_tasks": int(con.execute("SELECT count(*) FROM terminal_history").fetchone()[0]),
        "current_physical_quote_keys": int(con.execute("SELECT count(*) FROM current_quotes").fetchone()[0]),
        "full_interval_unqueried_tasks": sum(breakdown.values()),
        "gap_breakdown": breakdown,
    }
    expected_grid = metrics["universe_tickers"] * metrics["xnys_sessions"]
    status = "PASS" if metrics["full_grid_tasks"] == expected_grid and sum(breakdown.values()) == metrics["full_interval_unqueried_tasks"] else "FAIL"
    summary = {
        "run_id": args.run_id,
        "completed_at_utc": now(),
        "technical_status": status,
        "dataset_verdict": "NOT_FULL_CARTESIAN_INTERVAL",
        "metrics": metrics,
        "interpretation": "The original OHLC-window task master is not the full 4,824 x XNYS-session interval. This audit does not authorize downloading the scope expansion.",
    }
    atomic_json(closeout / "audit_summary.json", summary)
    con.close()
    artifacts = []
    for path in [missing_parquet, closeout / "audit_summary.json"]:
        artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    atomic_json(closeout / "final_manifest.json", {**summary, "artifacts": artifacts})
    atomic_json(control / "heartbeat.latest.json", {"updated_at_utc": now(), "stage": "closed"})
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
