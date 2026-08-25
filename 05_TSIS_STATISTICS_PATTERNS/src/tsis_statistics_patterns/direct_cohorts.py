from __future__ import annotations

from pathlib import Path

import duckdb


def _sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def materialize_direct_activation_outputs(
    con: duckdb.DuckDBPyConnection,
    final_root: Path,
    horizon_sessions: int,
) -> None:
    sessions = _sql_path(final_root / "session_observables.parquet")
    activations = _sql_path(final_root / "activation_labels.parquet")

    con.execute("SET threads=4")
    con.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE atlas_indexed_sessions AS
        SELECT ticker, date,
               row_number() OVER (PARTITION BY ticker ORDER BY date) AS rn,
               c_split_normalized, h_split_normalized,
               analysis_eligible, is_red_candle
        FROM read_parquet('{sessions}')
        """
    )

    con.execute(
        f"""
        COPY (
          WITH bounds AS (
            SELECT ticker, max(rn) AS max_rn
            FROM atlas_indexed_sessions GROUP BY ticker
          )
          SELECT substr(sha256(
                   a.ticker || '|' || CAST(a.date AS VARCHAR) || '|activation_case_v0_1'
                 ), 1, 24) AS activation_case_id,
                 a.ticker,
                 a.date AS anchor_date,
                 CAST(least({horizon_sessions + 1}, b.max_rn - s.rn + 1) AS INTEGER)
                   AS observed_sessions,
                 (s.rn + {horizon_sessions} <= b.max_rn) AS complete_horizon,
                 NOT (s.rn + {horizon_sessions} <= b.max_rn) AS right_censored,
                 string_agg(a.activation_label, ',' ORDER BY a.activation_label)
                   AS activation_labels
          FROM read_parquet('{activations}') a
          JOIN atlas_indexed_sessions s
            ON a.ticker=s.ticker AND a.date=s.date
          JOIN bounds b ON b.ticker=a.ticker
          GROUP BY a.ticker, a.date, s.rn, b.max_rn
          ORDER BY a.ticker, a.date
        ) TO '{_sql_path(final_root / 'activation_case_index.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    con.execute(
        f"""
        COPY (
          SELECT a.activation_family, a.activation_label,
                 CAST(t.rn - anchor.rn AS INTEGER) AS offset_session,
                 count(*) AS observations,
                 count(*) AS activation_cases,
                 count(DISTINCT a.ticker) AS tickers,
                 avg(t.c_split_normalized / anchor.c_split_normalized - 1.0)
                   AS mean_close_from_anchor_pct,
                 stddev_samp(t.c_split_normalized / anchor.c_split_normalized - 1.0)
                   AS std_close_from_anchor_pct,
                 quantile_cont(t.c_split_normalized / anchor.c_split_normalized - 1.0, 0.10)
                   AS p10_close_from_anchor_pct,
                 quantile_cont(t.c_split_normalized / anchor.c_split_normalized - 1.0, 0.25)
                   AS p25_close_from_anchor_pct,
                 quantile_cont(t.c_split_normalized / anchor.c_split_normalized - 1.0, 0.50)
                   AS median_close_from_anchor_pct,
                 quantile_cont(t.c_split_normalized / anchor.c_split_normalized - 1.0, 0.75)
                   AS p75_close_from_anchor_pct,
                 quantile_cont(t.c_split_normalized / anchor.c_split_normalized - 1.0, 0.90)
                   AS p90_close_from_anchor_pct,
                 avg(CAST(t.is_red_candle AS INTEGER)) AS observed_share_red_candle
          FROM read_parquet('{activations}') a
          JOIN atlas_indexed_sessions anchor
            ON a.ticker=anchor.ticker AND a.date=anchor.date
          JOIN atlas_indexed_sessions t
            ON t.ticker=anchor.ticker
           AND t.rn BETWEEN anchor.rn AND anchor.rn + {horizon_sessions}
          WHERE t.analysis_eligible
          GROUP BY 1,2,3
          ORDER BY 1,2,3
        ) TO '{_sql_path(final_root / 'cohort_statistics.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    con.execute("DROP TABLE atlas_indexed_sessions")
