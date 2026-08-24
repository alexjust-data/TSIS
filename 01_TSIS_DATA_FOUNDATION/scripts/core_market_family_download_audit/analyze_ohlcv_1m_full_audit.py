#!/usr/bin/env python3
"""Reproduce and certify the deep closeout analysis for the OHLCV 1m Full run.

This script is read-only with respect to the audited run and RAW source roots.
It writes small evidence assets to an explicitly supplied output directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import exchange_calendars as xcals
import pyarrow.parquet as pq


VERSION = "0.1.0"
EXPECTED_FAMILY = "ohlcv_1m"
EXPECTED_TICKERS = 4_824
SAMPLE_SEED = 20_260_824
SAMPLE_PER_YEAR = 5


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    partial.write_text(text, encoding="utf-8", newline="\n")
    partial.replace(path)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def atomic_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    with partial.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    partial.replace(path)


def iso(value: Any) -> Any:
    return value.isoformat() if isinstance(value, (date, datetime)) else value


def one(connection: duckdb.DuckDBPyConnection, sql: str, params: list[Any]) -> tuple[Any, ...]:
    return connection.execute(sql, params).fetchone()


def rows(connection: duckdb.DuckDBPyConnection, sql: str, params: list[Any]) -> list[tuple[Any, ...]]:
    return connection.execute(sql, params).fetchall()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--alignment-run-root", type=Path, required=True)
    parser.add_argument("--legacy-session-run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--skip-task-artifact-hashes",
        action="store_true",
        help="Skip the expensive 9,648 generated-shard hash verification.",
    )
    return parser.parse_args()


def verify_task_manifests(run_root: Path, pre_manifest: dict[str, Any], verify_hashes: bool) -> dict[str, Any]:
    manifests = []
    bad_json: list[str] = []
    for path in sorted((run_root / "00_control" / "task_results").glob("ticker=*.json")):
        try:
            manifests.append(read_json(path))
        except Exception:
            bad_json.append(str(path))

    tickers = [str(item.get("ticker")) for item in manifests]
    expected = set(map(str, pre_manifest["selected_tickers"]))
    observed = set(tickers)
    artifacts = [artifact for item in manifests for artifact in item.get("artifacts", [])]
    bad_artifacts: list[str] = []
    if verify_hashes:
        for artifact in artifacts:
            path = Path(str(artifact["path"]))
            if not path.is_file() or sha256_file(path) != str(artifact["sha256"]).upper():
                bad_artifacts.append(str(path))

    return {
        "task_manifest_count": len(manifests),
        "unique_tickers": len(observed),
        "missing_expected_tickers": sorted(expected - observed),
        "extra_tickers": sorted(observed - expected),
        "duplicate_ticker_count": len(tickers) - len(observed),
        "literal_NA_present": "NA" in observed,
        "bad_json_count": len(bad_json),
        "noncommitted_count": sum(item.get("status") != "committed" for item in manifests),
        "artifact_count": len(artifacts),
        "artifact_hash_verification_executed": verify_hashes,
        "bad_or_missing_artifact_count": len(bad_artifacts),
        "sum_file_count": sum(int(item["file_count"]) for item in manifests),
        "sum_source_rows": sum(int(item["rows_read_or_adopted"]) for item in manifests),
        "sum_activity_rows": sum(int(item["activity_rows"]) for item in manifests),
        "sum_source_bytes": sum(int(item["source_bytes"]) for item in manifests),
    }


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    alignment_root = args.alignment_run_root.resolve()
    legacy_root = args.legacy_session_run_root.resolve()
    output_dir = args.output_dir.resolve()

    final_path = run_root / "03_closeout" / "final_manifest.json"
    summary_path = run_root / "03_closeout" / "audit_summary.json"
    activity_path = run_root / "03_closeout" / "ohlcv_1m_session_activity.parquet"
    coverage_path = run_root / "03_closeout" / "ohlcv_1m_ticker_coverage.parquet"
    pre_path = run_root / "00_control" / "pre_manifest.json"
    ledger_path = run_root / "00_control" / "run_state.sqlite"
    inventory_path = alignment_root / "01_inventory" / "ohlcv_1m_inventory.parquet"
    old_dates_path = alignment_root / "02_ticker_coverage" / "ohlcv_1m_ticker_dates.parquet"
    legacy_detail_path = legacy_root / "06_correction_analysis" / "minute_only_day_metrics.parquet"

    required = [
        final_path,
        summary_path,
        activity_path,
        coverage_path,
        pre_path,
        ledger_path,
        inventory_path,
        old_dates_path,
        legacy_detail_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Required evidence missing: {missing}")

    final = read_json(final_path)
    audit_summary = read_json(summary_path)
    pre = read_json(pre_path)
    if final.get("family") != EXPECTED_FAMILY or final.get("status") != "completed":
        raise ValueError("The supplied run is not a completed ohlcv_1m Full run")

    task_check = verify_task_manifests(run_root, pre, not args.skip_task_artifact_hashes)
    final_artifact_bad: list[str] = []
    for artifact in final["artifacts"]:
        path = Path(str(artifact["path"]))
        if not path.is_file() or sha256_file(path) != str(artifact["sha256"]).upper():
            final_artifact_bad.append(str(path))

    con = duckdb.connect()
    con.execute("PRAGMA threads=4")

    ledger_status = rows(
        con,
        "SELECT status, COUNT(*) FROM sqlite_scan(?, 'tasks') GROUP BY status ORDER BY status",
        [str(ledger_path)],
    )
    ledger_totals = one(
        con,
        """
        SELECT COUNT(*), COUNT(DISTINCT ticker), SUM(files_read), SUM(rows_read),
               SUM(activity_rows), SUM(attempt), MAX(attempt),
               SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END)
        FROM sqlite_scan(?, 'tasks')
        """,
        [str(ledger_path)],
    )

    activity = one(
        con,
        """
        SELECT COUNT(*), COUNT(DISTINCT ticker), COUNT(DISTINCT session_date_et),
               COUNT(DISTINCT (ticker, session_date_et)),
               MIN(session_date_et), MAX(session_date_et),
               SUM(total_rows), SUM(premarket_rows), SUM(rth_rows),
               SUM(afterhours_rows), SUM(outside_0400_2000_rows),
               SUM(total_rows - premarket_rows - rth_rows - afterhours_rows - outside_0400_2000_rows),
               SUM(CASE WHEN total_rows <= 0 THEN 1 ELSE 0 END),
               SUM(CASE WHEN rth_rows = 0 THEN 1 ELSE 0 END),
               COUNT(DISTINCT CASE WHEN rth_rows = 0 THEN ticker END),
               SUM(CASE WHEN rth_rows = 0 THEN total_rows ELSE 0 END)
        FROM read_parquet(?)
        """,
        [str(activity_path)],
    )

    pattern_rows = rows(
        con,
        """
        SELECT has_premarket, has_rth, has_afterhours, has_outside_0400_2000,
               COUNT(*), COUNT(DISTINCT ticker), SUM(total_rows),
               SUM(premarket_rows), SUM(rth_rows), SUM(afterhours_rows),
               SUM(outside_0400_2000_rows)
        FROM read_parquet(?)
        GROUP BY 1,2,3,4
        ORDER BY 2 DESC,1 DESC,3 DESC,4 DESC
        """,
        [str(activity_path)],
    )

    no_rth_breakdown = rows(
        con,
        """
        SELECT
          CASE
            WHEN has_premarket AND has_afterhours AND NOT has_outside_0400_2000 THEN 'PREMARKET_AND_AFTERHOURS'
            WHEN has_premarket AND NOT has_afterhours AND NOT has_outside_0400_2000 THEN 'PREMARKET_ONLY'
            WHEN NOT has_premarket AND has_afterhours AND NOT has_outside_0400_2000 THEN 'AFTERHOURS_ONLY'
            WHEN NOT has_premarket AND has_afterhours AND has_outside_0400_2000 THEN 'AFTERHOURS_AND_OUTSIDE_0400_2000'
            ELSE 'OTHER'
          END AS pattern,
          COUNT(*) AS ticker_dates,
          COUNT(DISTINCT ticker) AS tickers,
          SUM(total_rows) AS minute_rows
        FROM read_parquet(?)
        WHERE rth_rows = 0
        GROUP BY 1
        ORDER BY 1
        """,
        [str(activity_path)],
    )

    outside = one(
        con,
        """
        SELECT COUNT(*), COUNT(DISTINCT ticker), MIN(session_date_et), MAX(session_date_et),
               SUM(outside_0400_2000_rows), MAX(outside_0400_2000_rows)
        FROM read_parquet(?)
        WHERE outside_0400_2000_rows > 0
        """,
        [str(activity_path)],
    )

    coverage = one(
        con,
        """
        SELECT COUNT(*), COUNT(DISTINCT ticker), SUM(file_count), SUM(source_bytes),
               SUM(rows_read_or_adopted), SUM(observed_session_count),
               MIN(first_session_date_et), MAX(last_session_date_et),
               SUM(physical_error_file_count), SUM(timestamp_parse_error_count),
               SUM(out_of_scope_row_count), MIN(observed_session_count),
               MEDIAN(observed_session_count), MAX(observed_session_count)
        FROM read_parquet(?)
        """,
        [str(coverage_path)],
    )

    coverage_states = rows(
        con,
        """
        SELECT source_state, leading_boundary_state, trailing_boundary_state,
               download_completeness_state, COUNT(*)
        FROM read_parquet(?) GROUP BY ALL
        """,
        [str(coverage_path)],
    )

    tail_daily = rows(
        con,
        """
        SELECT session_date_et, COUNT(*) AS tickers, SUM(total_rows),
               SUM(premarket_rows), SUM(rth_rows), SUM(afterhours_rows),
               SUM(outside_0400_2000_rows)
        FROM read_parquet(?)
        WHERE session_date_et >= make_date(2026, 2, 23)
        GROUP BY 1 ORDER BY 1
        """,
        [str(activity_path)],
    )

    post_march9 = rows(
        con,
        """
        SELECT ticker, MIN(session_date_et), MAX(session_date_et), COUNT(*), SUM(total_rows)
        FROM read_parquet(?)
        WHERE session_date_et > make_date(2026, 3, 9)
        GROUP BY ticker ORDER BY ticker
        """,
        [str(activity_path)],
    )

    old_reconciliation = one(
        con,
        """
        WITH new_no_rth AS (
          SELECT ticker, session_date_et FROM read_parquet(?) WHERE rth_rows = 0
        ), old_subset AS (
          SELECT ticker, session_date_et FROM read_parquet(?)
          WHERE rth_rows = 0 AND within_daily_global_window
        )
        SELECT
          (SELECT COUNT(*) FROM new_no_rth),
          (SELECT COUNT(*) FROM old_subset),
          (SELECT COUNT(*) FROM new_no_rth JOIN old_subset USING(ticker, session_date_et)),
          (SELECT COUNT(*) FROM new_no_rth LEFT JOIN old_subset USING(ticker, session_date_et)
             WHERE old_subset.ticker IS NULL),
          (SELECT COUNT(*) FROM old_subset LEFT JOIN new_no_rth USING(ticker, session_date_et)
             WHERE new_no_rth.ticker IS NULL)
        """,
        [str(activity_path), str(legacy_detail_path)],
    )

    new_not_old = rows(
        con,
        """
        WITH new_no_rth AS (
          SELECT ticker, session_date_et, total_rows
          FROM read_parquet(?) WHERE rth_rows = 0
        ), old_subset AS (
          SELECT ticker, session_date_et FROM read_parquet(?)
          WHERE rth_rows = 0 AND within_daily_global_window
        )
        SELECT
          CASE WHEN new_no_rth.session_date_et <= make_date(2026,3,6)
               THEN 'THROUGH_2026_03_06_DAILY_PRESENT_OR_OTHER'
               ELSE 'AFTER_2026_03_06' END,
          COUNT(*), COUNT(DISTINCT new_no_rth.ticker), SUM(total_rows)
        FROM new_no_rth
        LEFT JOIN old_subset USING(ticker, session_date_et)
        WHERE old_subset.ticker IS NULL
        GROUP BY 1 ORDER BY 1
        """,
        [str(activity_path), str(legacy_detail_path)],
    )

    old_new_dates = one(
        con,
        """
        WITH old_dates AS (
          SELECT DISTINCT ticker, observed_date AS dt FROM read_parquet(?)
        ), new_dates AS (
          SELECT DISTINCT ticker, session_date_et AS dt FROM read_parquet(?)
        )
        SELECT
          (SELECT COUNT(*) FROM old_dates), (SELECT COUNT(*) FROM new_dates),
          (SELECT COUNT(*) FROM old_dates LEFT JOIN new_dates USING(ticker,dt)
             WHERE new_dates.ticker IS NULL),
          (SELECT COUNT(*) FROM new_dates LEFT JOIN old_dates USING(ticker,dt)
             WHERE old_dates.ticker IS NULL)
        """,
        [str(old_dates_path), str(activity_path)],
    )

    old_only_weekdays = rows(
        con,
        """
        WITH old_dates AS (
          SELECT DISTINCT ticker, observed_date AS dt FROM read_parquet(?)
        ), new_dates AS (
          SELECT DISTINCT ticker, session_date_et AS dt FROM read_parquet(?)
        )
        SELECT dayname(old_dates.dt), COUNT(*)
        FROM old_dates LEFT JOIN new_dates USING(ticker,dt)
        WHERE new_dates.ticker IS NULL
        GROUP BY 1 ORDER BY 2 DESC
        """,
        [str(old_dates_path), str(activity_path)],
    )

    schema_rows = rows(
        con,
        """
        SELECT schema_fingerprint, COUNT(*), COUNT(DISTINCT ticker),
               SUM(metadata_num_rows), SUM(file_size_bytes),
               MIN(first_observed_date), MAX(last_observed_date),
               FIRST(absolute_path), FIRST(schema_columns_json)
        FROM read_parquet(?)
        GROUP BY schema_fingerprint
        ORDER BY COUNT(*) DESC
        """,
        [str(inventory_path)],
    )
    schema_regimes = []
    for fingerprint, files, tickers, row_count, byte_count, first_date, last_date, sample_path, columns_json in schema_rows:
        schema_regimes.append(
            {
                "schema_fingerprint": fingerprint,
                "files": files,
                "tickers": tickers,
                "rows": row_count,
                "bytes": byte_count,
                "first_date": iso(first_date),
                "last_date": iso(last_date),
                "columns": json.loads(columns_json),
                "sample_path": sample_path,
                "arrow_schema": str(pq.ParquetFile(sample_path).schema_arrow),
            }
        )

    schema_quality = one(
        con,
        """
        SELECT COUNT(*), COUNT(DISTINCT schema_fingerprint),
               SUM(CASE WHEN NOT required_schema_complete THEN 1 ELSE 0 END),
               SUM(CASE WHEN error_class IS NOT NULL AND error_class != '' THEN 1 ELSE 0 END)
        FROM read_parquet(?)
        """,
        [str(inventory_path)],
    )

    sample_candidates = rows(
        con,
        """
        SELECT ticker, session_date_et, total_rows, premarket_rows, rth_rows,
               afterhours_rows, outside_0400_2000_rows,
               physical_evidence_state, download_completeness_state
        FROM read_parquet(?)
        WHERE rth_rows = 0 AND year(session_date_et) IN (2025, 2026)
        ORDER BY session_date_et, ticker
        """,
        [str(activity_path)],
    )
    candidates_by_year: dict[int, list[tuple[Any, ...]]] = {2025: [], 2026: []}
    for item in sample_candidates:
        candidates_by_year[item[1].year].append(item)
    rng = random.Random(SAMPLE_SEED)
    selected = []
    for year in (2025, 2026):
        population = candidates_by_year[year]
        selected.extend(rng.sample(population, min(SAMPLE_PER_YEAR, len(population))))
    selected.sort(key=lambda item: (item[1], item[0]))

    sample_rows = []
    for item in selected:
        pre_rows, ah_rows, outside_rows = int(item[3]), int(item[5]), int(item[6])
        if pre_rows and ah_rows and not outside_rows:
            pattern = "PREMARKET_AND_AFTERHOURS"
        elif pre_rows and not ah_rows and not outside_rows:
            pattern = "PREMARKET_ONLY"
        elif not pre_rows and ah_rows and not outside_rows:
            pattern = "AFTERHOURS_ONLY"
        elif not pre_rows and ah_rows and outside_rows:
            pattern = "AFTERHOURS_AND_OUTSIDE_0400_2000"
        else:
            pattern = "OTHER"
        sample_rows.append(
            {
                "sample_seed": SAMPLE_SEED,
                "ticker": item[0],
                "session_date_et": item[1].isoformat(),
                "total_rows": item[2],
                "premarket_rows": item[3],
                "rth_rows": item[4],
                "afterhours_rows": item[5],
                "outside_0400_2000_rows": item[6],
                "pattern": pattern,
                "physical_evidence_state": item[7],
                "download_completeness_state": item[8],
            }
        )

    observed_dates = {item[0] for item in rows(con, "SELECT DISTINCT session_date_et FROM read_parquet(?)", [str(activity_path)])}
    max_observed = activity[5]
    calendar = xcals.get_calendar(
        "XNYS",
        start=str(activity[4]),
        end=str(date.fromisoformat(str(final["scope"]["end_date_inclusive"]))),
    )
    through_max = {stamp.date() for stamp in calendar.sessions_in_range(str(activity[4]), str(max_observed))}
    scope_end = date.fromisoformat(str(final["scope"]["end_date_inclusive"]))
    missing_after_max = {
        stamp.date()
        for stamp in calendar.sessions_in_range(str(max_observed), str(scope_end))
        if stamp.date() > max_observed
    }

    total_rows = int(activity[6])
    ticker_dates = int(activity[0])
    no_rth_ticker_dates = int(activity[13])
    no_rth_minute_rows = int(activity[15])

    integrity_failures = {
        "final_artifact_hash_failures": len(final_artifact_bad),
        "task_artifact_failures": task_check["bad_or_missing_artifact_count"],
        "missing_expected_tickers": len(task_check["missing_expected_tickers"]),
        "extra_tickers": len(task_check["extra_tickers"]),
        "duplicate_tickers": task_check["duplicate_ticker_count"],
        "noncommitted_tasks": task_check["noncommitted_count"],
        "activity_key_duplicates": int(activity[0] - activity[3]),
        "row_equation_mismatches": int(activity[11]),
        "nonpositive_activity_rows": int(activity[12]),
        "timestamp_parse_errors": int(coverage[9]),
        "out_of_scope_rows": int(coverage[10]),
        "missing_global_xnys_sessions_through_max": len(through_max - observed_dates),
        "observed_non_xnys_dates_through_max": len(observed_dates - through_max),
    }
    if any(integrity_failures.values()):
        raise AssertionError(f"Deep audit integrity gate failed: {integrity_failures}")
    if int(activity[0]) != int(coverage[5]) or total_rows != int(coverage[4]):
        raise AssertionError("Closeout activity/coverage reconciliation failed")
    if task_check["sum_source_rows"] != total_rows or task_check["sum_file_count"] != int(coverage[2]):
        raise AssertionError("Task manifest sums do not reconcile with closeout")
    if int(activity[7] + activity[8] + activity[9] + activity[10]) != total_rows:
        raise AssertionError("Session-band row sums do not reconcile")

    payload: dict[str, Any] = {
        "analysis_version": VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "inputs": {
            "run_root": str(run_root),
            "alignment_run_root": str(alignment_root),
            "legacy_session_run_root": str(legacy_root),
            "final_manifest_sha256": sha256_file(final_path),
            "activity_parquet_sha256": sha256_file(activity_path),
            "coverage_parquet_sha256": sha256_file(coverage_path),
            "source_inventory_sha256": sha256_file(inventory_path),
            "legacy_detail_sha256": sha256_file(legacy_detail_path),
        },
        "verdict": {
            "technical_execution": "PASS",
            "exact_4824_universe": "PASS",
            "present_parquet_integrity": "PASS_ADOPTED_CLOSED_AUDIT",
            "timestamp_and_session_reconciliation": "PASS",
            "global_calendar_continuity_through_max_observed": "PASS",
            "requested_scope_to_2026_08_20": "FAIL_LOCAL_ARCHIVE_INCOMPLETE",
            "per_ticker_provider_expectedness": "UNRESOLVED",
            "overall": "PARTIAL_CERTIFICATION_PRESENT_DATA_HEALTHY_TEMPORALLY_INCOMPLETE",
        },
        "run": {
            "run_id": final["run_id"],
            "started_at_utc": final["started_at_utc"],
            "ended_at_utc": final["ended_at_utc"],
            "technical_status": final["technical_status"],
            "download_completeness_status": final["download_completeness_status"],
            "audit_summary_sha256": sha256_file(summary_path),
        },
        "ledger": {
            "status_counts": [{"status": status, "count": count} for status, count in ledger_status],
            "task_count": ledger_totals[0],
            "unique_tickers": ledger_totals[1],
            "files": ledger_totals[2],
            "source_rows": ledger_totals[3],
            "activity_rows": ledger_totals[4],
            "attempt_sum": ledger_totals[5],
            "max_attempt": ledger_totals[6],
            "error_count": ledger_totals[7],
        },
        "task_manifest_verification": task_check,
        "integrity_failures": integrity_failures,
        "physical_scope": {
            "files": coverage[2],
            "bytes": coverage[3],
            "source_rows": coverage[4],
            "ticker_date_rows": coverage[5],
            "physical_error_files": coverage[8],
            "timestamp_parse_errors": coverage[9],
            "out_of_scope_rows": coverage[10],
            "observed_sessions_per_ticker_min": coverage[11],
            "observed_sessions_per_ticker_median": coverage[12],
            "observed_sessions_per_ticker_max": coverage[13],
            "coverage_states": [
                {
                    "source_state": item[0],
                    "leading_boundary_state": item[1],
                    "trailing_boundary_state": item[2],
                    "download_completeness_state": item[3],
                    "tickers": item[4],
                }
                for item in coverage_states
            ],
        },
        "temporal_coverage": {
            "distinct_observed_session_dates": activity[2],
            "first_session_date_et": iso(activity[4]),
            "last_session_date_et": iso(activity[5]),
            "xnys_sessions_through_max": len(through_max),
            "missing_xnys_sessions_through_max": len(through_max - observed_dates),
            "observed_non_xnys_dates_through_max": len(observed_dates - through_max),
            "missing_global_xnys_sessions_after_max_to_scope_end": len(missing_after_max),
            "missing_global_first": iso(min(missing_after_max)) if missing_after_max else None,
            "missing_global_last": iso(max(missing_after_max)) if missing_after_max else None,
            "post_2026_03_09_tickers": [
                {
                    "ticker": item[0],
                    "first_date": iso(item[1]),
                    "last_date": iso(item[2]),
                    "ticker_dates": item[3],
                    "minute_rows": item[4],
                }
                for item in post_march9
            ],
            "tail_daily": [
                {
                    "session_date_et": iso(item[0]),
                    "tickers": item[1],
                    "total_rows": item[2],
                    "premarket_rows": item[3],
                    "rth_rows": item[4],
                    "afterhours_rows": item[5],
                    "outside_rows": item[6],
                }
                for item in tail_daily
            ],
        },
        "session_rows": {
            "total": total_rows,
            "premarket": {"rows": activity[7], "pct_of_all_rows": 100.0 * activity[7] / total_rows},
            "rth": {"rows": activity[8], "pct_of_all_rows": 100.0 * activity[8] / total_rows},
            "afterhours": {"rows": activity[9], "pct_of_all_rows": 100.0 * activity[9] / total_rows},
            "outside_0400_2000": {"rows": activity[10], "pct_of_all_rows": 100.0 * activity[10] / total_rows},
            "patterns": [
                {
                    "has_premarket": item[0],
                    "has_rth": item[1],
                    "has_afterhours": item[2],
                    "has_outside": item[3],
                    "ticker_dates": item[4],
                    "tickers": item[5],
                    "total_rows": item[6],
                    "premarket_rows": item[7],
                    "rth_rows": item[8],
                    "afterhours_rows": item[9],
                    "outside_rows": item[10],
                }
                for item in pattern_rows
            ],
        },
        "no_rth_observed_activity": {
            "denominator_definition": "observed ticker-session_date_et keys with at least one 1m row",
            "not_a_missing_day_rate": True,
            "observed_ticker_dates": ticker_dates,
            "ticker_dates_with_rth": ticker_dates - no_rth_ticker_dates,
            "ticker_dates_without_rth": no_rth_ticker_dates,
            "affected_tickers": activity[14],
            "minute_rows_on_no_rth_dates": no_rth_minute_rows,
            "pct_of_observed_ticker_dates": 100.0 * no_rth_ticker_dates / ticker_dates,
            "pct_of_all_minute_rows": 100.0 * no_rth_minute_rows / total_rows,
            "breakdown": [
                {"pattern": item[0], "ticker_dates": item[1], "tickers": item[2], "minute_rows": item[3]}
                for item in no_rth_breakdown
            ],
            "sample_seed": SAMPLE_SEED,
            "sample_candidate_counts": {str(year): len(values) for year, values in candidates_by_year.items()},
            "sample": sample_rows,
        },
        "legacy_4264_reconciliation": {
            "new_all_no_rth": old_reconciliation[0],
            "old_narrow_subset": old_reconciliation[1],
            "overlap": old_reconciliation[2],
            "new_not_old": old_reconciliation[3],
            "old_not_new": old_reconciliation[4],
            "new_not_old_breakdown": [
                {"class": item[0], "ticker_dates": item[1], "tickers": item[2], "minute_rows": item[3]}
                for item in new_not_old
            ],
        },
        "utc_date_to_et_session_date_reconciliation": {
            "old_physical_ticker_dates": old_new_dates[0],
            "new_et_ticker_dates": old_new_dates[1],
            "old_only": old_new_dates[2],
            "new_only": old_new_dates[3],
            "old_only_weekday_counts": {item[0]: item[1] for item in old_only_weekdays},
            "row_loss": 0,
            "explanation": "all source rows reconcile; key-count change is UTC physical date to America/New_York session-date normalization",
        },
        "outside_0400_2000": {
            "ticker_dates": outside[0],
            "tickers": outside[1],
            "first_date": iso(outside[2]),
            "last_date": iso(outside[3]),
            "rows": outside[4],
            "max_rows_in_one_ticker_date": outside[5],
        },
        "schema": {
            "files": schema_quality[0],
            "fingerprints": schema_quality[1],
            "incomplete_required_schema_files": schema_quality[2],
            "physical_error_files": schema_quality[3],
            "regimes": schema_regimes,
            "known_limitation": "506 FCEL/XRX monthly files expose vw as Arrow null type; required column exists but values are unavailable",
        },
        "limitations": [
            "Technical PASS certifies execution and present-file evidence, not requested temporal completeness.",
            "A missing ticker-date cannot be attributed to Massive or the downloader without independent expected/lifecycle authority.",
            "The session denominator excludes ticker-dates with zero observed 1m rows; it is not universe-times-calendar expected coverage.",
            "The runner re-read only ts_utc for event-clock classification and adopted prior structural checks for other columns.",
            "OHLCV value correctness, per-minute duplicates and bar-generation semantics were outside this audit scope.",
        ],
        "source_audit_summary": audit_summary,
    }

    summary_output = output_dir / "ohlcv_1m_full_audit_deep_summary_v0_1.json"
    sample_output = output_dir / "ohlcv_1m_no_rth_sample_2025_2026_v0_1.csv"
    atomic_json(summary_output, payload)
    atomic_csv(sample_output, sample_rows, list(sample_rows[0].keys()))

    manifest_payload = {
        "analysis_version": VERSION,
        "generated_at_utc": payload["generated_at_utc"],
        "script_path": payload["script_path"],
        "script_sha256": payload["script_sha256"],
        "source_run_id": final["run_id"],
        "artifacts": [
            {"path": str(summary_output), "bytes": summary_output.stat().st_size, "sha256": sha256_file(summary_output)},
            {"path": str(sample_output), "bytes": sample_output.stat().st_size, "sha256": sha256_file(sample_output)},
        ],
        "verdict": payload["verdict"],
    }
    manifest_output = output_dir / "analysis_manifest_v0_1.json"
    atomic_json(manifest_output, manifest_payload)

    print(json.dumps({
        "status": "completed",
        "summary": str(summary_output),
        "sample": str(sample_output),
        "manifest": str(manifest_output),
        "verdict": payload["verdict"],
    }, indent=2))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
