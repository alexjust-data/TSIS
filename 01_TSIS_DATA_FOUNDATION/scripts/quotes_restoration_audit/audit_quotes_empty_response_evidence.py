#!/usr/bin/env python3
"""Audit how many independent ledger events support each empty Quotes task."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import duckdb


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".partial")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-root", required=True)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    history_root = Path(args.history_root).resolve()
    classification = Path(args.classification).resolve()
    output = Path(args.output_root).resolve()
    control = output / "00_control"
    closeout = output / "03_closeout"
    histories = sorted(
        path for path in history_root.rglob("download_events_history.csv")
        if "quotes" in str(path).lower()
    )
    if not histories:
        raise FileNotFoundError(f"No Quotes histories below {history_root}")
    if not classification.exists():
        raise FileNotFoundError(classification)

    pre = {
        "run_id": args.run_id,
        "pid": os.getpid(),
        "started_at_utc": now(),
        "operation": "quotes_empty_response_evidence_depth_audit",
        "classification": str(classification),
        "history_files": [str(path) for path in histories],
        "history_bytes": sum(path.stat().st_size for path in histories),
        "raw_parquet_reads": 0,
    }
    atomic_json(control / "pre_manifest.json", pre)

    con = duckdb.connect(str(output / "audit.duckdb"))
    con.execute("PRAGMA threads=2")
    con.execute("PRAGMA memory_limit='4GB'")
    con.execute("CREATE OR REPLACE TABLE empty_events(ticker VARCHAR, date DATE, status VARCHAR, processed_at_utc VARCHAR, run_id VARCHAR, source_history VARCHAR)")

    for index, history in enumerate(histories, start=1):
        atomic_json(control / "heartbeat.latest.json", {
            "updated_at_utc": now(),
            "stage": "history_scan",
            "progress": index - 1,
            "total": len(histories),
            "active_history": str(history),
        })
        con.execute(
            f"""
            INSERT INTO empty_events
            SELECT upper(trim(ticker)), try_cast(date AS DATE), upper(trim(status)),
                   processed_at_utc, run_id, '{sql_path(history)}'
            FROM read_csv_auto('{sql_path(history)}', header=true, all_varchar=true,
                               sample_size=1000, strict_mode=true)
            WHERE upper(trim(status)) IN ('DOWNLOADED_EMPTY', 'EMPTY_CONFIRMED')
              AND ticker IS NOT NULL AND trim(ticker) <> ''
              AND try_cast(date AS DATE) IS NOT NULL
            """
        )

    con.execute("""
        CREATE OR REPLACE TABLE empty_events_distinct AS
        SELECT DISTINCT ticker, date, status, processed_at_utc, run_id
        FROM empty_events
    """)
    ledger_path = sql_path(classification)
    con.execute(f"""
        CREATE OR REPLACE TABLE evidence AS
        WITH expected AS (
          SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date,
                 daily_present, coverage_state
          FROM read_parquet('{ledger_path}')
          WHERE coverage_state LIKE 'PROVIDER_EMPTY%'
        ), event_counts AS (
          SELECT ticker, date, count(*) empty_event_count,
                 count(DISTINCT run_id) distinct_run_count,
                 string_agg(DISTINCT status, '|' ORDER BY status) statuses
          FROM empty_events_distinct GROUP BY ticker, date
        )
        SELECT e.*, coalesce(c.empty_event_count, 0) empty_event_count,
               coalesce(c.distinct_run_count, 0) distinct_run_count,
               c.statuses,
               CASE
                 WHEN coalesce(c.distinct_run_count, 0) >= 2 THEN 'REPEATED_ACROSS_RUNS'
                 WHEN coalesce(c.empty_event_count, 0) >= 2 THEN 'REPEATED_WITHIN_RUN'
                 WHEN coalesce(c.empty_event_count, 0) = 1 THEN 'SINGLE_RECORDED_EMPTY'
                 ELSE 'NO_RAW_HISTORY_EVENT_RECOVERED'
               END evidence_state
        FROM expected e LEFT JOIN event_counts c USING (ticker, date)
    """)

    closeout.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY evidence TO '{sql_path(closeout / 'empty_response_evidence_by_task.parquet')}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.execute(f"""
        COPY (
          SELECT ticker, CAST(date AS VARCHAR) date, evidence_state,
                 empty_event_count, distinct_run_count
          FROM evidence WHERE daily_present
          ORDER BY ticker, date
        ) TO '{sql_path(closeout / 'provider_empty_daily_present_recheck_requests.csv')}'
        (FORMAT CSV, HEADER TRUE)
    """)

    rows = con.execute("""
        SELECT daily_present, evidence_state, count(*) tasks, count(DISTINCT ticker) tickers
        FROM evidence GROUP BY ALL ORDER BY daily_present DESC, evidence_state
    """).fetchall()
    evidence_summary = [
        {"daily_present": bool(row[0]), "evidence_state": row[1], "tasks": int(row[2]), "tickers": int(row[3])}
        for row in rows
    ]
    missing_events = int(con.execute("SELECT count(*) FROM evidence WHERE empty_event_count=0").fetchone()[0])
    summary = {
        "run_id": args.run_id,
        "completed_at_utc": now(),
        "technical_status": "PASS" if missing_events == 0 else "PASS_WITH_RECOVERED_LEDGER_ONLY_CASES",
        "semantics": "EMPTY_CONFIRMED is only strong when supported by repeated requests; historical DOWNLOADED_EMPTY was resume-terminal in the legacy code",
        "history_files": len(histories),
        "empty_tasks": int(con.execute("SELECT count(*) FROM evidence").fetchone()[0]),
        "empty_tasks_daily_present": int(con.execute("SELECT count(*) FROM evidence WHERE daily_present").fetchone()[0]),
        "empty_tasks_without_raw_history_event": missing_events,
        "evidence_breakdown": evidence_summary,
    }
    atomic_json(closeout / "audit_summary.json", summary)
    con.close()

    artifacts = []
    for path in sorted(closeout.iterdir()):
        if path.is_file() and path.name != "final_manifest.json":
            artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    atomic_json(closeout / "final_manifest.json", {**summary, "artifacts": artifacts})
    atomic_json(control / "heartbeat.latest.json", {
        "updated_at_utc": now(), "stage": "closed", "progress": len(histories), "total": len(histories)
    })
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
