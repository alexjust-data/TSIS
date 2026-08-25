from __future__ import annotations

import hashlib
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

from .certify import EXPECTED_KEYS


def _sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def certify_partition_schemas(run_root: Path) -> dict:
    tables: dict[str, dict] = {}
    overall = True
    for table_name in EXPECTED_KEYS:
        files = sorted(run_root.glob(f"shard=*/{table_name}/*.parquet"))
        fingerprints: dict[str, int] = {}
        for path in files:
            schema = pq.ParquetFile(path).schema_arrow.to_string(show_field_metadata=True)
            digest = hashlib.sha256(schema.encode("utf-8")).hexdigest()
            fingerprints[digest] = fingerprints.get(digest, 0) + 1
        passed = bool(files) and len(fingerprints) == 1
        overall = overall and passed
        tables[table_name] = {
            "files": len(files),
            "schema_variants": len(fingerprints),
            "fingerprints": fingerprints,
            "status": "pass" if passed else "fail",
        }
    return {"status": "pass" if overall else "fail", "tables": tables}


def certify_outcome_quality(final_root: Path) -> dict:
    trajectories = _sql_path(final_root / "episode_trajectories.parquet")
    events = _sql_path(final_root / "episode_events.parquet")
    episodes = _sql_path(final_root / "episodes.parquet")
    sessions = _sql_path(final_root / "session_observables.parquet")
    activations = _sql_path(final_root / "activation_labels.parquet")

    con = duckdb.connect()
    try:
        query = f"""
        WITH trajectory_checks AS (
          SELECT *,
                 max(CASE WHEN analysis_eligible THEN h_split_normalized END)
                   OVER (PARTITION BY episode_id ORDER BY offset_session
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                   AS expected_running_high
          FROM read_parquet('{trajectories}')
        ), event_quality AS (
          SELECT count(*) FILTER (WHERE NOT t.analysis_eligible) AS events_on_invalid_rows
          FROM read_parquet('{events}') e
          JOIN read_parquet('{trajectories}') t
            ON e.episode_id=t.episode_id AND e.offset_session=t.offset_session
        ), peak_quality AS (
          SELECT count(*) FILTER (WHERE NOT t.analysis_eligible) AS peaks_on_invalid_rows,
                 count(*) FILTER (
                   WHERE abs(e.horizon_peak_high - t.h_split_normalized) > 1e-12
                 ) AS peak_value_mismatches
          FROM read_parquet('{episodes}') e
          JOIN read_parquet('{trajectories}') t
            ON e.episode_id=t.episode_id
           AND e.horizon_peak_offset=t.offset_session
        )
        SELECT
          count(*) FILTER (
            WHERE NOT analysis_eligible AND (
              close_from_anchor_pct IS NOT NULL OR
              high_from_anchor_pct IS NOT NULL OR
              drawdown_from_running_high_pct IS NOT NULL OR
              is_new_episode_high
            )
          ) AS invalid_rows_with_outcomes,
          count(*) FILTER (
            WHERE analysis_eligible AND (
              close_from_anchor_pct IS NULL OR
              high_from_anchor_pct IS NULL OR
              running_episode_high IS NULL OR
              drawdown_from_running_high_pct IS NULL
            )
          ) AS eligible_rows_with_null_outcomes,
          count(*) FILTER (
            WHERE analysis_eligible AND
                  abs(running_episode_high - expected_running_high) > 1e-12
          ) AS running_high_mismatches,
          count(*) FILTER (
            WHERE (close_from_anchor_pct IS NOT NULL AND NOT isfinite(close_from_anchor_pct)) OR
                  (high_from_anchor_pct IS NOT NULL AND NOT isfinite(high_from_anchor_pct)) OR
                  (running_episode_high IS NOT NULL AND NOT isfinite(running_episode_high)) OR
                  (drawdown_from_running_high_pct IS NOT NULL AND NOT isfinite(drawdown_from_running_high_pct))
          ) AS nonfinite_outcome_rows,
          (SELECT events_on_invalid_rows FROM event_quality) AS events_on_invalid_rows,
          (SELECT peaks_on_invalid_rows FROM peak_quality) AS peaks_on_invalid_rows,
          (SELECT peak_value_mismatches FROM peak_quality) AS peak_value_mismatches
        FROM trajectory_checks
        """
        columns = [column[0] for column in con.execute(query).description]
        values = con.fetchone()
        violations = dict(zip(columns, (int(value) for value in values), strict=True))

        role_query = f"""
        SELECT
          (SELECT count(*) FROM read_parquet('{sessions}') WHERE knowledge_role <> 'observable')
            AS session_role_mismatches,
          (SELECT count(*) FROM read_parquet('{activations}') WHERE knowledge_role <> 'observable')
            AS activation_role_mismatches,
          (SELECT count(*) FROM read_parquet('{trajectories}') WHERE knowledge_role <> 'outcome')
            AS trajectory_role_mismatches,
          (SELECT count(*) FROM read_parquet('{events}') WHERE knowledge_role <> 'outcome')
            AS event_role_mismatches,
          (SELECT count(*) FROM read_parquet('{episodes}') WHERE knowledge_role <> 'episode_summary')
            AS episode_role_mismatches
        """
        role_columns = [column[0] for column in con.execute(role_query).description]
        role_values = con.fetchone()
        role_violations = dict(
            zip(role_columns, (int(value) for value in role_values), strict=True)
        )
    finally:
        con.close()

    all_violations = {**violations, **role_violations}
    passed = all(value == 0 for value in all_violations.values())
    return {
        "status": "pass" if passed else "fail",
        "violations": all_violations,
    }
