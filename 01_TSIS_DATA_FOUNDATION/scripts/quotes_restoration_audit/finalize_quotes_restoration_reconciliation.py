#!/usr/bin/env python3
"""Reconcile restored Quotes metadata and build exact repair/recheck queues.

The script reads only prior audit inventories and ledgers.  It never opens the
raw Quotes Parquet files, so the physical audit is performed exactly once.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import duckdb


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".partial")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def copy_query(con: duckdb.DuckDBPyConnection, query: str, target: Path, fmt: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".partial")
    if temp.exists():
        temp.unlink()
    options = "FORMAT PARQUET, COMPRESSION ZSTD" if fmt == "parquet" else "FORMAT CSV, HEADER TRUE"
    con.execute(f"COPY ({query}) TO '{sql_path(temp)}' ({options})")
    os.replace(temp, target)


def scalar(con: duckdb.DuckDBPyConnection, query: str) -> int:
    return int(con.execute(query).fetchone()[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restoration-run", required=True)
    parser.add_argument("--ledger-classification", required=True)
    parser.add_argument("--historical-c-inventory", required=True)
    parser.add_argument("--current-alignment-run", required=True)
    parser.add_argument("--tail-repair-csv", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    restoration_run = Path(args.restoration_run).resolve()
    restoration_manifest = restoration_run / "03_closeout" / "final_manifest.json"
    restored_inventory = restoration_run / "03_closeout" / "quotes_restored_inventory.parquet"
    ledger = Path(args.ledger_classification).resolve()
    historical_c = Path(args.historical_c_inventory).resolve()
    alignment_run = Path(args.current_alignment_run).resolve()
    alignment_manifest = alignment_run / "04_closeout" / "final_manifest.json"
    current_glob = alignment_run / "01_inventory" / "quotes_" / "ticker=*" / "inventory.parquet"
    tail_csv = Path(args.tail_repair_csv).resolve()
    output = Path(args.output_root).resolve()
    control = output / "00_control"
    reconciliation = output / "02_reconciliation"
    closeout = output / "03_closeout"

    required = [restoration_manifest, restored_inventory, ledger, historical_c, alignment_manifest, tail_csv]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required closed evidence is missing: {missing}")
    restoration_final = json.loads(restoration_manifest.read_text(encoding="utf-8"))
    if restoration_final.get("technical_status") != "PASS":
        raise RuntimeError("Restoration physical audit is not closed PASS")

    output.mkdir(parents=True, exist_ok=True)
    pre_manifest = {
        "run_id": args.run_id,
        "started_at_utc": utc_now(),
        "operation": "quotes_restoration_metadata_reconciliation_and_repair_plan",
        "raw_parquet_reads": 0,
        "inputs": {
            "restoration_manifest": str(restoration_manifest),
            "restored_inventory": str(restored_inventory),
            "ledger_classification": str(ledger),
            "historical_c_inventory": str(historical_c),
            "current_alignment_manifest": str(alignment_manifest),
            "current_inventory_glob": str(current_glob),
            "tail_repair_csv": str(tail_csv),
        },
    }
    atomic_json(control / "pre_manifest.json", pre_manifest)

    database = output / "reconciliation.duckdb"
    con = duckdb.connect(str(database))
    con.execute("PRAGMA threads=4")
    con.execute("PRAGMA memory_limit='8GB'")
    con.execute("PRAGMA temp_directory='{}'".format(sql_path(output / "duckdb_temp")))

    con.execute(f"CREATE OR REPLACE VIEW master AS SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date, daily_present, coverage_state, latest_status FROM read_parquet('{sql_path(ledger)}')")
    con.execute(f"CREATE OR REPLACE VIEW historical_c AS SELECT upper(trim(ticker)) ticker, CAST(date AS DATE) date, rows historical_rows, size_bytes historical_size_bytes, relpath historical_relpath FROM read_parquet('{sql_path(historical_c)}')")
    con.execute(f"CREATE OR REPLACE VIEW restored AS SELECT upper(trim(ticker)) ticker, historical_date date, file_exists, file_size_bytes, metadata_num_rows, physical_errors, historical_size_match, restoration_path_state, absolute_path FROM (SELECT *, CASE WHEN error_class IS NULL THEN 0 ELSE 1 END physical_errors FROM read_parquet('{sql_path(restored_inventory)}'))")

    current_glob_sql = sql_path(current_glob)
    con.execute(
        f"""
        CREATE OR REPLACE TABLE current_quotes AS
        WITH source AS (
          SELECT upper(trim(ticker)) ticker, relative_path, file_exists
          FROM read_parquet('{current_glob_sql}', union_by_name=true, hive_partitioning=false)
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
        FROM parsed
        WHERE yyyy <> '' AND mm <> '' AND dd <> ''
        """
    )
    con.execute("CREATE UNIQUE INDEX current_quotes_key ON current_quotes(ticker, date)")
    con.execute("CREATE OR REPLACE TABLE restored_present AS SELECT DISTINCT ticker, date, metadata_num_rows, file_size_bytes, absolute_path FROM restored WHERE file_exists")
    con.execute("CREATE UNIQUE INDEX restored_present_key ON restored_present(ticker, date)")

    row_mismatch_query = """
        SELECT r.ticker, r.date, c.historical_rows, r.metadata_num_rows,
               c.historical_size_bytes, r.file_size_bytes, r.absolute_path
        FROM restored_present r
        JOIN historical_c c USING (ticker, date)
        WHERE r.metadata_num_rows IS DISTINCT FROM c.historical_rows
        ORDER BY r.ticker, r.date
    """
    copy_query(con, row_mismatch_query, reconciliation / "restored_row_count_mismatches.parquet", "parquet")

    missing_master_query = """
        SELECT c.ticker, c.date, c.historical_rows, c.historical_size_bytes,
               c.historical_relpath, m.daily_present
        FROM historical_c c
        JOIN master m USING (ticker, date)
        LEFT JOIN restored_present r USING (ticker, date)
        LEFT JOIN current_quotes q USING (ticker, date)
        WHERE r.ticker IS NULL AND q.ticker IS NULL
        ORDER BY c.ticker, c.date
    """
    copy_query(con, missing_master_query, reconciliation / "known_nonempty_missing_master.parquet", "parquet")
    copy_query(con, f"SELECT * FROM ({missing_master_query}) WHERE daily_present", reconciliation / "known_nonempty_missing_daily_present.parquet", "parquet")

    decomposition_query = """
        SELECT m.ticker, m.date,
               CASE
                 WHEN r.ticker IS NOT NULL THEN 'RESTORED_C_AVAILABLE'
                 WHEN c.ticker IS NOT NULL THEN 'C_KNOWN_NONEMPTY_STILL_MISSING'
                 WHEN m.coverage_state LIKE 'PROVIDER_EMPTY%' THEN 'PROVIDER_EMPTY_SINGLE_RECORDED_RESPONSE'
                 WHEN m.coverage_state = 'NO_TERMINAL_EVENT' THEN 'NO_TERMINAL_EVENT'
                 ELSE 'UNEXPLAINED'
               END resolution_state
        FROM master m
        LEFT JOIN current_quotes q USING (ticker, date)
        LEFT JOIN restored_present r USING (ticker, date)
        LEFT JOIN historical_c c USING (ticker, date)
        WHERE m.daily_present AND q.ticker IS NULL
    """
    copy_query(con, decomposition_query, reconciliation / "daily_without_current_quotes_decomposition.parquet", "parquet")

    repair_missing_query = """
        SELECT ticker, CAST(date AS VARCHAR) date, 'KNOWN_NONEMPTY_C_FILE_MISSING' repair_reason
        FROM read_parquet('{}')
    """.format(sql_path(reconciliation / "known_nonempty_missing_master.parquet"))
    repair_na_query = """
        SELECT ticker, CAST(date AS VARCHAR) date, 'LITERAL_NA_NEVER_EXECUTED' repair_reason
        FROM master WHERE coverage_state='NO_TERMINAL_EVENT'
    """
    provider_recheck_query = """
        SELECT ticker, CAST(date AS VARCHAR) date, 'PROVIDER_EMPTY_DAILY_PRESENT_RECHECK' repair_reason
        FROM master WHERE daily_present AND coverage_state LIKE 'PROVIDER_EMPTY%'
    """
    copy_query(con, f"SELECT * FROM ({repair_missing_query}) ORDER BY ticker, date", closeout / "quotes_historical_known_nonempty_missing_requests.csv", "csv")
    copy_query(con, f"SELECT * FROM ({repair_na_query}) ORDER BY ticker, date", closeout / "quotes_historical_na_repair_requests.csv", "csv")
    copy_query(con, f"SELECT * FROM ({provider_recheck_query}) ORDER BY ticker, date", closeout / "quotes_provider_empty_daily_present_recheck_requests.csv", "csv")

    con.execute(f"CREATE OR REPLACE VIEW tail AS SELECT upper(trim(ticker)) ticker, CAST(date AS VARCHAR) date, 'TAIL_TO_2026_08_20' repair_reason FROM read_csv_auto('{sql_path(tail_csv)}', header=true, all_varchar=true)")
    union_query = f"""
        SELECT ticker, date, string_agg(repair_reason, '|' ORDER BY repair_reason) repair_reason
        FROM (
          {repair_missing_query}
          UNION ALL
          {repair_na_query}
          UNION ALL
          SELECT * FROM tail
        )
        GROUP BY ticker, date
        ORDER BY ticker, date
    """
    copy_query(con, union_query, closeout / "quotes_repair_requests_union.csv", "csv")

    decomposition = {
        row[0]: int(row[1])
        for row in con.execute(f"SELECT resolution_state, count(*) FROM ({decomposition_query}) GROUP BY 1 ORDER BY 1").fetchall()
    }
    metrics = {
        "master_tasks": scalar(con, "SELECT count(*) FROM master"),
        "master_tickers": scalar(con, "SELECT count(DISTINCT ticker) FROM master"),
        "daily_present_master_tasks": scalar(con, "SELECT count(*) FROM master WHERE daily_present"),
        "current_quotes_path_keys": scalar(con, "SELECT count(*) FROM current_quotes"),
        "restored_present_files": scalar(con, "SELECT count(*) FROM restored_present"),
        "restored_present_rows": scalar(con, "SELECT coalesce(sum(metadata_num_rows), 0) FROM restored_present"),
        "restored_present_bytes": scalar(con, "SELECT coalesce(sum(file_size_bytes), 0) FROM restored_present"),
        "historical_c_expected_rows": scalar(con, "SELECT coalesce(sum(historical_rows), 0) FROM historical_c"),
        "historical_c_expected_bytes": scalar(con, "SELECT coalesce(sum(historical_size_bytes), 0) FROM historical_c"),
        "restored_row_count_mismatches": scalar(con, f"SELECT count(*) FROM ({row_mismatch_query})"),
        "known_nonempty_missing_master": scalar(con, f"SELECT count(*) FROM ({missing_master_query})"),
        "known_nonempty_missing_master_rows": scalar(con, f"SELECT coalesce(sum(historical_rows), 0) FROM ({missing_master_query})"),
        "known_nonempty_missing_master_bytes": scalar(con, f"SELECT coalesce(sum(historical_size_bytes), 0) FROM ({missing_master_query})"),
        "known_nonempty_missing_daily_present": scalar(con, f"SELECT count(*) FROM ({missing_master_query}) WHERE daily_present"),
        "historical_na_repair_requests": scalar(con, f"SELECT count(*) FROM ({repair_na_query})"),
        "provider_empty_daily_present_recheck_requests": scalar(con, f"SELECT count(*) FROM ({provider_recheck_query})"),
        "tail_missing_requests": scalar(con, "SELECT count(*) FROM tail"),
        "repair_union_requests": scalar(con, f"SELECT count(*) FROM ({union_query})"),
        "daily_without_current_quotes": sum(decomposition.values()),
        "daily_without_current_quotes_decomposition": decomposition,
    }
    summary = {
        "run_id": args.run_id,
        "created_at_utc": utc_now(),
        "technical_status": "PASS" if metrics["restored_row_count_mismatches"] == 0 and decomposition.get("UNEXPLAINED", 0) == 0 else "FAIL",
        "interpretation": {
            "provider_empty_label": "one or more recorded empty API responses; not independently provider-certified absence",
            "repair_union_excludes_provider_empty_rechecks": True,
            "raw_parquet_reopened": False,
        },
        "metrics": metrics,
    }
    atomic_json(closeout / "reconciliation_summary.json", summary)

    output_files = sorted(
        path
        for path in output.rglob("*")
        if path.is_file()
        and not path.name.startswith("reconciliation.duckdb")
        and "duckdb_temp" not in path.parts
    )
    final_manifest = {
        **summary,
        "completed_at_utc": utc_now(),
        "artifacts": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in output_files
        ],
    }
    atomic_json(closeout / "final_manifest.json", final_manifest)
    con.close()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["technical_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
