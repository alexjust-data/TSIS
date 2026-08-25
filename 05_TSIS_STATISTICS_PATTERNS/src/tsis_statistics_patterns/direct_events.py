from __future__ import annotations

from pathlib import Path

import duckdb


def _sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def materialize_direct_activation_event_statistics(
    con: duckdb.DuckDBPyConnection,
    final_root: Path,
    horizon_sessions: int,
) -> None:
    sessions = _sql_path(final_root / "session_observables.parquet")
    activations = _sql_path(final_root / "activation_labels.parquet")
    con.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE atlas_event_sessions AS
        SELECT ticker, date,
               row_number() OVER (PARTITION BY ticker ORDER BY date) AS rn,
               h_split_normalized, analysis_eligible,
               is_red_candle, is_lower_close, is_lower_high
        FROM read_parquet('{sessions}')
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP TABLE atlas_direct_event_stats (
          activation_family VARCHAR,
          activation_label VARCHAR,
          event_label VARCHAR,
          activation_cases BIGINT,
          event_observed BIGINT,
          mean_offset DOUBLE,
          median_offset DOUBLE,
          p25_offset DOUBLE,
          p75_offset DOUBLE,
          p90_offset DOUBLE
        )
        """
    )
    labels = con.execute(
        f"""
        SELECT DISTINCT activation_family, activation_label
        FROM read_parquet('{activations}') ORDER BY 1,2
        """
    ).fetchall()
    for family, label in labels:
        family_sql = str(family).replace("'", "''")
        label_sql = str(label).replace("'", "''")
        con.execute(
            f"""
            INSERT INTO atlas_direct_event_stats
            WITH joined AS (
              SELECT a.ticker, a.date AS anchor_date,
                     CAST(t.rn-anchor.rn AS INTEGER) AS offset_session,
                     t.h_split_normalized, t.is_red_candle,
                     t.is_lower_close, t.is_lower_high,
                     max(t.h_split_normalized) OVER (
                       PARTITION BY a.ticker, a.date
                       ORDER BY t.rn ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                     ) AS prior_running_high
              FROM read_parquet('{activations}') a
              JOIN atlas_event_sessions anchor
                ON a.ticker=anchor.ticker AND a.date=anchor.date
              JOIN atlas_event_sessions t
                ON t.ticker=anchor.ticker
               AND t.rn BETWEEN anchor.rn AND anchor.rn + {horizon_sessions}
              WHERE a.activation_label='{label_sql}' AND t.analysis_eligible
            ), per_case AS (
              SELECT ticker, anchor_date,
                     first(offset_session ORDER BY h_split_normalized DESC, offset_session ASC)
                       AS horizon_peak,
                     min(offset_session) FILTER (WHERE is_red_candle)
                       AS first_red_candle,
                     min(offset_session) FILTER (
                       WHERE offset_session >= 1 AND is_red_candle
                     ) AS first_red_candle_after_d0,
                     min(offset_session) FILTER (WHERE is_lower_close)
                       AS first_lower_close,
                     min(offset_session) FILTER (WHERE is_lower_high)
                       AS first_lower_high,
                     min(offset_session) FILTER (
                       WHERE offset_session >= 1
                         AND h_split_normalized <= prior_running_high
                     ) AS first_day_without_new_episode_high
              FROM joined GROUP BY ticker, anchor_date
            ), long_events AS (
              SELECT *, event.event_label,
                     CASE event.event_label
                       WHEN 'horizon_peak' THEN horizon_peak
                       WHEN 'first_red_candle' THEN first_red_candle
                       WHEN 'first_red_candle_after_d0' THEN first_red_candle_after_d0
                       WHEN 'first_lower_close' THEN first_lower_close
                       WHEN 'first_lower_high' THEN first_lower_high
                       WHEN 'first_day_without_new_episode_high'
                         THEN first_day_without_new_episode_high
                     END AS event_offset
              FROM per_case
              CROSS JOIN (VALUES
                ('horizon_peak'),
                ('first_red_candle'),
                ('first_red_candle_after_d0'),
                ('first_lower_close'),
                ('first_lower_high'),
                ('first_day_without_new_episode_high')
              ) AS event(event_label)
            )
            SELECT '{family_sql}', '{label_sql}', event_label,
                   count(*) AS activation_cases,
                   count(event_offset) AS event_observed,
                   avg(event_offset) AS mean_offset,
                   quantile_cont(event_offset, 0.50) AS median_offset,
                   quantile_cont(event_offset, 0.25) AS p25_offset,
                   quantile_cont(event_offset, 0.75) AS p75_offset,
                   quantile_cont(event_offset, 0.90) AS p90_offset
            FROM long_events GROUP BY event_label
            """
        )
    con.execute(
        f"""
        COPY (
          SELECT * FROM atlas_direct_event_stats
          ORDER BY activation_family, activation_label, event_label
        ) TO '{_sql_path(final_root / 'activation_event_statistics.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    con.execute("DROP TABLE atlas_direct_event_stats")
    con.execute("DROP TABLE atlas_event_sessions")
