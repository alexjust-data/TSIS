from __future__ import annotations

from pathlib import Path

import duckdb


def _sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def certify_exact_scope_and_sources(
    final_root: Path, activity_path: Path, mode: str
) -> dict:
    sessions = _sql_path(final_root / "session_observables.parquet")
    activity = _sql_path(activity_path)
    con = duckdb.connect()
    try:
        missing = int(
            con.execute(
                f"""
                SELECT count(*) FROM (
                  SELECT ticker, date FROM read_parquet('{activity}')
                  EXCEPT
                  SELECT ticker, date FROM read_parquet('{sessions}')
                )
                """
            ).fetchone()[0]
        )
        additional = int(
            con.execute(
                f"""
                SELECT count(*) FROM (
                  SELECT ticker, date FROM read_parquet('{sessions}')
                  EXCEPT
                  SELECT ticker, date FROM read_parquet('{activity}')
                )
                """
            ).fetchone()[0]
        )
        cohort_mismatches = int(
            con.execute(
                f"""
                WITH labels AS (
                  SELECT activation_label, count(*) AS cases
                  FROM read_parquet('{_sql_path(final_root / 'activation_labels.parquet')}')
                  GROUP BY 1
                ), cohorts AS (
                  SELECT activation_label, activation_cases AS cases
                  FROM read_parquet('{_sql_path(final_root / 'cohort_statistics.parquet')}')
                  WHERE offset_session=0
                )
                SELECT count(*) FROM labels FULL JOIN cohorts USING (activation_label)
                WHERE labels.cases IS DISTINCT FROM cohorts.cases
                """
            ).fetchone()[0]
        )
        event_case_mismatches = int(
            con.execute(
                f"""
                WITH labels AS (
                  SELECT activation_label, count(*) AS cases
                  FROM read_parquet('{_sql_path(final_root / 'activation_labels.parquet')}')
                  GROUP BY 1
                ), event_stats AS (
                  SELECT activation_label, event_label, activation_cases AS cases
                  FROM read_parquet('{_sql_path(final_root / 'activation_event_statistics.parquet')}')
                )
                SELECT count(*) FROM labels JOIN event_stats USING (activation_label)
                WHERE labels.cases IS DISTINCT FROM event_stats.cases
                """
            ).fetchone()[0]
        )
        case_index_key_difference = int(
            con.execute(
                f"""
                SELECT count(*) FROM (
                  (SELECT DISTINCT ticker, date
                   FROM read_parquet('{_sql_path(final_root / 'activation_labels.parquet')}')
                   EXCEPT
                   SELECT ticker, anchor_date AS date
                   FROM read_parquet('{_sql_path(final_root / 'activation_case_index.parquet')}'))
                  UNION ALL
                  (SELECT ticker, anchor_date AS date
                   FROM read_parquet('{_sql_path(final_root / 'activation_case_index.parquet')}')
                   EXCEPT
                   SELECT DISTINCT ticker, date
                   FROM read_parquet('{_sql_path(final_root / 'activation_labels.parquet')}'))
                )
                """
            ).fetchone()[0]
        )
        source_files = [
            Path(row[0])
            for row in con.execute(
                f"SELECT DISTINCT source_daily_file FROM read_parquet('{sessions}')"
            ).fetchall()
        ]
    finally:
        con.close()
    missing_sources = [str(path) for path in source_files if not path.exists()]
    membership_pass = additional == 0 and (mode != "full" or missing == 0)
    passed = (
        membership_pass
        and cohort_mismatches == 0
        and event_case_mismatches == 0
        and case_index_key_difference == 0
        and not missing_sources
    )
    return {
        "status": "pass" if passed else "fail",
        "mode": mode,
        "full_scope_membership_required": mode == "full",
        "missing_ticker_dates": missing,
        "additional_ticker_dates": additional,
        "direct_cohort_d0_mismatches": cohort_mismatches,
        "direct_event_case_count_mismatches": event_case_mismatches,
        "activation_case_index_key_difference": case_index_key_difference,
        "distinct_source_files": len(source_files),
        "missing_source_files": len(missing_sources),
        "missing_source_file_examples": missing_sources[:10],
    }
