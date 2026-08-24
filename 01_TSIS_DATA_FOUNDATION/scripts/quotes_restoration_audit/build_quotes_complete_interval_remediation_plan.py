#!/usr/bin/env python3
"""Build the exact Quotes remediation set for the full XNYS interval.

This is a metadata-only planner. It never opens or modifies RAW Quotes files.
It combines three disjoint evidence classes:

* full-interval ticker-sessions never queried by the historical workflow;
* historically known non-empty files that are still physically unavailable;
* recorded provider-empty responses with Daily present that require recheck.
"""

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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    partial.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(partial, path)


def copy_query(con: duckdb.DuckDBPyConnection, query: str, target: Path, options: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".partial")
    if partial.exists():
        partial.unlink()
    con.execute(f"COPY ({query}) TO '{sql_path(partial)}' ({options})")
    os.replace(partial, target)


def scalar(con: duckdb.DuckDBPyConnection, query: str) -> int:
    return int(con.execute(query).fetchone()[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-interval-unqueried", required=True)
    parser.add_argument("--known-nonempty-missing", required=True)
    parser.add_argument("--provider-empty-rechecks", required=True)
    parser.add_argument("--start", default="2005-01-01")
    parser.add_argument("--end", default="2026-08-20")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    unqueried = Path(args.full_interval_unqueried).resolve()
    known_missing = Path(args.known_nonempty_missing).resolve()
    empty_rechecks = Path(args.provider_empty_rechecks).resolve()
    output = Path(args.output_root).resolve()
    control = output / "00_control"
    closeout = output / "03_closeout"
    required = [unqueried, known_missing, empty_rechecks]
    absent = [str(path) for path in required if not path.is_file()]
    if absent:
        raise FileNotFoundError(f"Missing closed evidence: {absent}")

    calendar = xcals.get_calendar("XNYS", start=args.start, end=args.end)
    requested_start = pd.Timestamp(args.start)
    requested_end = pd.Timestamp(args.end)
    effective_start = max(requested_start, calendar.first_session)
    effective_end = min(requested_end, calendar.last_session)
    sessions = calendar.sessions_in_range(effective_start, effective_end)
    session_frame = pd.DataFrame(
        {
            "date": sessions.tz_localize(None).date,
            "session_ordinal": range(len(sessions)),
        }
    )

    output.mkdir(parents=True, exist_ok=True)
    pre_manifest = {
        "run_id": args.run_id,
        "started_at_utc": utc_now(),
        "operation": "quotes_complete_interval_remediation_plan",
        "raw_parquet_reads": 0,
        "calendar": "XNYS via exchange_calendars",
        "scope": {
            "requested_start": args.start,
            "requested_end": args.end,
            "first_xnys_session": str(effective_start.date()),
            "last_xnys_session": str(effective_end.date()),
        },
        "inputs": {
            "full_interval_unqueried": str(unqueried),
            "known_nonempty_missing": str(known_missing),
            "provider_empty_rechecks": str(empty_rechecks),
        },
    }
    atomic_json(control / "pre_manifest.json", pre_manifest)

    con = duckdb.connect(str(output / "plan.duckdb"))
    con.execute("PRAGMA threads=4")
    con.execute("PRAGMA memory_limit='10GB'")
    temp_directory = output / "duckdb_temp"
    temp_directory.mkdir(parents=True, exist_ok=True)
    con.execute("SET preserve_insertion_order=false")
    con.execute(f"PRAGMA temp_directory='{sql_path(temp_directory)}'")
    con.register("session_frame", session_frame)
    con.execute(
        "CREATE OR REPLACE TABLE sessions AS "
        "SELECT CAST(date AS DATE) date, CAST(session_ordinal AS INTEGER) session_ordinal "
        "FROM session_frame"
    )

    con.execute(
        f"""
        CREATE OR REPLACE VIEW unqueried_candidates AS
        SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date,
               'UNQUERIED_FULL_INTERVAL' remediation_class,
               scope_gap_reason evidence_detail
        FROM read_parquet('{sql_path(unqueried)}')
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE VIEW known_missing_candidates AS
        SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date,
               'KNOWN_NONEMPTY_PHYSICALLY_MISSING' remediation_class,
               'C_INVENTORY_NONEMPTY_FILE_MISSING' evidence_detail
        FROM read_parquet('{sql_path(known_missing)}')
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE VIEW empty_recheck_candidates AS
        SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date,
               'PROVIDER_EMPTY_RECHECK' remediation_class,
               evidence_state evidence_detail
        FROM read_csv_auto('{sql_path(empty_rechecks)}', header=true)
        """
    )
    con.execute(
        """
        CREATE OR REPLACE VIEW candidates AS
        SELECT * FROM unqueried_candidates
        UNION ALL SELECT * FROM known_missing_candidates
        UNION ALL SELECT * FROM empty_recheck_candidates
        """
    )
    overlap_keys = scalar(
        con,
        """
        SELECT count(*) FROM (
          SELECT u.ticker, u.date
          FROM unqueried_candidates u
          JOIN known_missing_candidates m USING (ticker, date)
          UNION ALL
          SELECT u.ticker, u.date
          FROM unqueried_candidates u
          JOIN empty_recheck_candidates e USING (ticker, date)
          UNION ALL
          SELECT m.ticker, m.date
          FROM known_missing_candidates m
          JOIN empty_recheck_candidates e USING (ticker, date)
        )
        """,
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE exact_daily AS
        SELECT c.ticker, c.date,
               c.remediation_class remediation_classes,
               c.evidence_detail evidence_details,
               1 source_evidence_rows
        FROM candidates c
        JOIN sessions s USING (date)
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE outside_xnys AS
        SELECT c.*
        FROM candidates c
        LEFT JOIN sessions s USING (date)
        WHERE s.date IS NULL
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE intervals AS
        WITH ordered AS (
          SELECT d.*, s.session_ordinal,
                 s.session_ordinal - row_number() OVER (
                   PARTITION BY d.ticker ORDER BY s.session_ordinal
                 ) AS island
          FROM exact_daily d
          JOIN sessions s USING (date)
        )
        SELECT ticker, min(date) start_date, max(date) end_date,
               count(*) xnys_sessions,
               string_agg(DISTINCT remediation_classes, ' || ' ORDER BY remediation_classes) remediation_classes
        FROM ordered
        GROUP BY ticker, island
        """
    )

    exact_parquet = closeout / "quotes_complete_interval_exact_daily_requests.parquet"
    intervals_parquet = closeout / "quotes_complete_interval_contiguous_intervals.parquet"
    intervals_csv = closeout / "quotes_complete_interval_contiguous_intervals.csv"
    outside_parquet = closeout / "quotes_remediation_candidates_outside_xnys.parquet"
    copy_query(
        con,
        "SELECT * FROM exact_daily ORDER BY ticker, date",
        exact_parquet,
        "FORMAT PARQUET, COMPRESSION ZSTD",
    )
    copy_query(
        con,
        "SELECT * FROM intervals ORDER BY ticker, start_date",
        intervals_parquet,
        "FORMAT PARQUET, COMPRESSION ZSTD",
    )
    copy_query(
        con,
        "SELECT * FROM intervals ORDER BY ticker, start_date",
        intervals_csv,
        "FORMAT CSV, HEADER TRUE",
    )
    copy_query(
        con,
        "SELECT * FROM outside_xnys ORDER BY ticker, date, remediation_class",
        outside_parquet,
        "FORMAT PARQUET, COMPRESSION ZSTD",
    )

    source_rows = scalar(con, "SELECT count(*) FROM candidates")
    exact_rows = scalar(con, "SELECT count(*) FROM exact_daily")

    metrics = {
        "source_evidence_rows": source_rows,
        "exact_xnys_ticker_date_requests": exact_rows,
        "duplicate_or_overlapping_evidence_keys": overlap_keys,
        "outside_xnys_evidence_rows": scalar(con, "SELECT count(*) FROM outside_xnys"),
        "contiguous_ticker_intervals": scalar(con, "SELECT count(*) FROM intervals"),
        "tickers_requiring_remediation": scalar(con, "SELECT count(DISTINCT ticker) FROM exact_daily"),
        "first_date": str(con.execute("SELECT min(date) FROM exact_daily").fetchone()[0]),
        "last_date": str(con.execute("SELECT max(date) FROM exact_daily").fetchone()[0]),
        "by_class": {
            row[0]: int(row[1])
            for row in con.execute(
                "SELECT remediation_class, count(*) FROM candidates c JOIN sessions s USING (date) GROUP BY 1 ORDER BY 1"
            ).fetchall()
        },
    }
    summary = {
        **pre_manifest,
        "completed_at_utc": utc_now(),
        "technical_status": "PASS" if overlap_keys == 0 else "FAIL_OVERLAPPING_EVIDENCE",
        "dataset_status": "REMEDIATION_REQUIRED",
        "semantics": {
            "daily_request_set": "exact missing/recheck XNYS ticker-date keys",
            "contiguous_intervals": "execution planning only; downloader must preserve all returned rows and reconcile by exact key",
            "provider_empty": "requires independent requery; it is not certified absence",
        },
        "metrics": metrics,
    }
    atomic_json(closeout / "remediation_summary.json", summary)

    artifacts = [exact_parquet, intervals_parquet, intervals_csv, outside_parquet, closeout / "remediation_summary.json"]
    final_manifest = {
        **summary,
        "artifacts": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in artifacts
        ],
    }
    atomic_json(closeout / "final_manifest.json", final_manifest)
    con.close()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["technical_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
