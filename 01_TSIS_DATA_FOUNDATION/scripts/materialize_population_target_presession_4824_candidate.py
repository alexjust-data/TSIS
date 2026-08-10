#!/usr/bin/env python3
"""Materialize a controlled presession-selector candidate or probe."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


DATASET_ID = "population_target_presession_4824_candidate_v0_1"
SCHEMA_VERSION = "population_target_presession_4824_candidate_v0_1"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--master-daily-root", required=True, type=Path)
    parser.add_argument("--instrument-master", required=True, type=Path)
    parser.add_argument("--fundamentals-root", required=True, type=Path)
    parser.add_argument("--market-calendar", required=True, type=Path)
    parser.add_argument("--output-parquet", required=True, type=Path)
    parser.add_argument(
        "--share-policy",
        required=True,
        choices=["S1_DILUTED_FIRST", "S2_BASIC_FIRST"],
    )
    parser.add_argument("--ttl-days", required=True, type=int, choices=[90, 180, 365])
    parser.add_argument("--session-start", type=date.fromisoformat)
    parser.add_argument("--session-end", type=date.fromisoformat)
    parser.add_argument("--session-dates", nargs="*", type=date.fromisoformat)
    parser.add_argument("--tickers", nargs="*")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--memory-limit", default="8GB")
    parser.add_argument("--temp-directory", type=Path)
    return parser


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _parquet_glob(root: Path) -> str:
    return _sql_path(root).rstrip("/") + "/**/*.parquet"


def _quoted(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _scope_sql(
    session_start: date | None,
    session_end: date | None,
    session_dates: list[date] | None,
    tickers: list[str] | None,
) -> str:
    clauses = ["d.price_view = 'daily_raw'"]
    if session_start is not None:
        clauses.append(f"d.session_date >= DATE '{session_start.isoformat()}'")
    if session_end is not None:
        clauses.append(f"d.session_date <= DATE '{session_end.isoformat()}'")
    if session_dates:
        values = ",".join(f"DATE '{item.isoformat()}'" for item in session_dates)
        clauses.append(f"d.session_date IN ({values})")
    if tickers:
        clauses.append("d.ticker IN (" + ",".join(_quoted(item) for item in tickers) + ")")
    return " AND ".join(clauses)


def _share_expressions(policy_id: str) -> tuple[str, str]:
    if policy_id == "S1_DILUTED_FIRST":
        return (
            """
            CASE
                WHEN diluted_shares_outstanding > 0 THEN diluted_shares_outstanding
                WHEN basic_shares_outstanding > 0 THEN basic_shares_outstanding
            END
            """,
            """
            CASE
                WHEN diluted_shares_outstanding > 0
                    THEN 'DILUTED_WEIGHTED_AVERAGE_SHARES_PROXY'
                WHEN basic_shares_outstanding > 0
                    THEN 'BASIC_WEIGHTED_AVERAGE_SHARES_PROXY'
            END
            """,
        )
    return (
        """
        CASE
            WHEN basic_shares_outstanding > 0 THEN basic_shares_outstanding
            WHEN diluted_shares_outstanding > 0 THEN diluted_shares_outstanding
        END
        """,
        """
        CASE
            WHEN basic_shares_outstanding > 0
                THEN 'BASIC_WEIGHTED_AVERAGE_SHARES_PROXY'
            WHEN diluted_shares_outstanding > 0
                THEN 'DILUTED_WEIGHTED_AVERAGE_SHARES_PROXY'
        END
        """,
    )


def materialize(
    config_path: Path,
    master_daily_root: Path,
    instrument_master: Path,
    fundamentals_root: Path,
    market_calendar: Path,
    output_parquet: Path,
    share_policy: str,
    ttl_days: int,
    session_start: date | None = None,
    session_end: date | None = None,
    session_dates: list[date] | None = None,
    tickers: list[str] | None = None,
    threads: int = 4,
    memory_limit: str = "8GB",
    temp_directory: Path | None = None,
) -> dict[str, Any]:
    if output_parquet.exists():
        raise FileExistsError(f"Refusing to overwrite {output_parquet}")
    config = _read_json(config_path)
    allowed_policies = {
        item["policy_id"] for item in config["share_selection_candidates"]
    }
    if share_policy not in allowed_policies:
        raise ValueError(f"Share policy is not governed by config: {share_policy}")
    if ttl_days not in config["shares_ttl_candidates_days"]:
        raise ValueError(f"TTL is not governed by config: {ttl_days}")

    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(database=":memory:")
    connection.execute(f"SET threads={max(1, threads)}")
    connection.execute(f"SET memory_limit='{memory_limit}'")
    if temp_directory is not None:
        temp_directory.mkdir(parents=True, exist_ok=True)
        connection.execute(f"SET temp_directory='{_sql_path(temp_directory)}'")

    connection.execute(
        f"""
        CREATE VIEW master_daily_all AS
        SELECT * FROM read_parquet(
            '{_parquet_glob(master_daily_root)}',
            hive_partitioning=true,
            union_by_name=true
        )
        """
    )
    connection.execute(
        f"CREATE VIEW instrument_master AS SELECT * FROM read_parquet('{_sql_path(instrument_master)}')"
    )
    connection.execute(
        f"""
        CREATE VIEW fundamentals_all AS
        SELECT * FROM read_parquet(
            '{_parquet_glob(fundamentals_root)}',
            hive_partitioning=true,
            union_by_name=true
        )
        """
    )
    connection.execute(
        f"CREATE VIEW market_calendar AS SELECT * FROM read_parquet('{_sql_path(market_calendar)}')"
    )

    scope_sql = _scope_sql(session_start, session_end, session_dates, tickers)
    connection.execute(
        f"""
        CREATE TEMP TABLE sessions AS
        SELECT
            d.master_daily_id,
            d.instrument_id,
            d.ticker,
            d.session_date,
            d.expected_session,
            d.data_present,
            d.missing_expected_data,
            d.prior_close,
            d.selected_price_hard_invalid,
            d.has_split_action,
            d.has_ticker_change_action,
            d.has_any_corporate_action,
            d.row_level_price_integrity_state,
            d.family_data_quality_verdict,
            i.is_common_stock,
            i.ticker_identity_scope,
            c.open_utc - INTERVAL '5 hours 30 minutes' AS presession_cutoff_utc,
            c.build_run_id AS market_calendar_build_run_id
        FROM master_daily_all d
        INNER JOIN instrument_master i
          ON d.instrument_id = i.instrument_id
         AND d.ticker = i.ticker
        INNER JOIN market_calendar c USING (session_date)
        WHERE {scope_sql}
        """
    )
    connection.execute(
        """
        CREATE TEMP TABLE admissible_share_observations AS
        SELECT * EXCLUDE (source_rank)
        FROM (
            SELECT
                fundamental_asof_id,
                instrument_id,
                ticker,
                as_of_date,
                period_end,
                basic_shares_outstanding,
                diluted_shares_outstanding,
                fundamental_quality_state,
                source_file,
                source_file_row_number,
                build_run_id AS fundamentals_build_run_id,
                ROW_NUMBER() OVER (
                    PARTITION BY instrument_id, ticker, as_of_date
                    ORDER BY period_end DESC, fundamental_asof_id ASC
                ) AS source_rank
            FROM fundamentals_all
            WHERE statement_family = 'income_statements'
              AND instrument_id IS NOT NULL
              AND instrument_identity_temporal_match
              AND period_end <= as_of_date
              AND (
                  (basic_shares_outstanding > 0 AND isfinite(basic_shares_outstanding))
                  OR
                  (diluted_shares_outstanding > 0 AND isfinite(diluted_shares_outstanding))
              )
        )
        WHERE source_rank = 1
        """
    )

    share_value_expression, share_type_expression = _share_expressions(share_policy)
    connection.execute(
        f"""
        CREATE TEMP TABLE candidate_output AS
        WITH joined AS (
            SELECT
                s.*,
                f.fundamental_asof_id,
                f.as_of_date AS shares_as_of_date,
                f.period_end AS shares_period_end,
                date_diff('day', f.as_of_date, s.session_date) AS shares_age_days,
                f.basic_shares_outstanding,
                f.diluted_shares_outstanding,
                f.fundamental_quality_state,
                f.source_file AS fundamentals_source_file,
                f.source_file_row_number AS fundamentals_source_file_row_number,
                f.fundamentals_build_run_id
            FROM sessions s
            ASOF LEFT JOIN admissible_share_observations f
              ON s.instrument_id = f.instrument_id
             AND s.ticker = f.ticker
             AND s.session_date > f.as_of_date
        ), selected AS (
            SELECT
                *,
                {share_value_expression} AS shares_proxy_as_of_session,
                {share_type_expression} AS shares_measure_type
            FROM joined
        ), represented AS (
            SELECT
                *,
                CASE
                    WHEN selected_price_hard_invalid THEN 'SOURCE_SEMANTICS_REVIEW'
                    WHEN prior_close IS NULL THEN 'REFERENCE_PRICE_UNAVAILABLE'
                    WHEN prior_close <= 0 THEN 'REFERENCE_PRICE_NONPOSITIVE'
                    WHEN prior_close < 0.50 OR prior_close > 20.00
                        THEN 'REFERENCE_PRICE_OUTSIDE_PROFILE'
                    ELSE 'REFERENCE_PRICE_AVAILABLE'
                END AS reference_price_state,
                CASE
                    WHEN shares_proxy_as_of_session IS NULL THEN 'SHARES_PROXY_UNAVAILABLE'
                    WHEN shares_age_days > {ttl_days} THEN 'SHARES_PROXY_STALE'
                    ELSE 'SHARES_PROXY_AVAILABLE'
                END AS shares_proxy_state,
                CASE
                    WHEN prior_close > 0 AND shares_proxy_as_of_session > 0
                        THEN prior_close * shares_proxy_as_of_session
                END AS presession_reference_market_cap_proxy
            FROM selected
        )
        SELECT
            'ptp4824:' || md5(
                '{DATASET_ID}|' || master_daily_id || '|{share_policy}|{ttl_days}'
            ) AS population_context_id,
            instrument_id,
            ticker AS ticker_as_of_session,
            session_date,
            presession_cutoff_utc,
            'lt1b_universe_v0_1' AS parent_universe_id,
            expected_session,
            data_present,
            missing_expected_data,
            is_common_stock,
            ticker_identity_scope,
            prior_close AS presession_reference_price,
            'PRIOR_ELIGIBLE_RTH_CLOSE' AS reference_price_source,
            reference_price_state,
            shares_proxy_as_of_session,
            shares_measure_type,
            shares_as_of_date,
            shares_period_end,
            shares_age_days,
            fundamental_asof_id AS shares_source_row_id,
            'DATE_ONLY_CONSERVATIVE_AVAILABILITY' AS shares_available_at_rule,
            '{share_policy}' AS share_selection_policy_id,
            'SHARES_TTL_{ttl_days}D' AS shares_ttl_policy_id,
            shares_proxy_state,
            presession_reference_market_cap_proxy,
            CASE
                WHEN has_split_action OR has_ticker_change_action
                    THEN 'CORPORATE_ACTION_REVIEW'
                WHEN reference_price_state IN (
                    'SOURCE_SEMANTICS_REVIEW',
                    'REFERENCE_PRICE_UNAVAILABLE',
                    'REFERENCE_PRICE_NONPOSITIVE'
                ) THEN 'REFERENCE_PRICE_UNAVAILABLE'
                WHEN shares_proxy_state = 'SHARES_PROXY_UNAVAILABLE'
                    THEN 'SHARES_PROXY_UNAVAILABLE'
                WHEN shares_proxy_state = 'SHARES_PROXY_STALE'
                    THEN 'SHARES_PROXY_STALE'
                ELSE 'CALCULATED_PROXY'
            END AS market_cap_calculation_state,
            CASE
                WHEN reference_price_state = 'REFERENCE_PRICE_AVAILABLE'
                    THEN 'PRICE_ELIGIBLE'
                WHEN reference_price_state = 'REFERENCE_PRICE_OUTSIDE_PROFILE'
                    THEN 'PRICE_INELIGIBLE'
                ELSE 'PRICE_UNAVAILABLE_OR_REVIEW'
            END AS price_eligibility_state,
            CASE
                WHEN shares_proxy_state <> 'SHARES_PROXY_AVAILABLE'
                    THEN 'MARKET_CAP_NOT_CLASSIFIABLE'
                WHEN presession_reference_market_cap_proxy < 100000000.0
                    THEN 'MARKET_CAP_PROXY_ELIGIBLE'
                ELSE 'MARKET_CAP_PROXY_INELIGIBLE'
            END AS market_cap_eligibility_state,
            CASE
                WHEN NOT is_common_stock THEN 'OUTSIDE_INSTRUMENT_VALIDITY'
                WHEN has_split_action OR has_ticker_change_action
                    THEN 'CORPORATE_ACTION_REVIEW'
                WHEN reference_price_state IN (
                    'SOURCE_SEMANTICS_REVIEW',
                    'REFERENCE_PRICE_UNAVAILABLE',
                    'REFERENCE_PRICE_NONPOSITIVE'
                ) THEN 'UNAVAILABLE_REFERENCE_PRICE'
                WHEN reference_price_state = 'REFERENCE_PRICE_OUTSIDE_PROFILE'
                    THEN 'INELIGIBLE_PRICE'
                WHEN shares_proxy_state = 'SHARES_PROXY_UNAVAILABLE'
                    THEN 'UNAVAILABLE_SHARES_PROXY'
                WHEN shares_proxy_state = 'SHARES_PROXY_STALE'
                    THEN 'STALE_SHARES_PROXY'
                WHEN presession_reference_market_cap_proxy < 100000000.0
                    THEN 'ELIGIBLE_UNDER_DECLARED_PROXY'
                ELSE 'INELIGIBLE_MARKET_CAP_PROXY'
            END AS population_membership_state,
            CASE
                WHEN has_split_action OR has_ticker_change_action
                    THEN 'TARGET_SESSION_SPLIT_OR_TICKER_CHANGE'
                WHEN reference_price_state <> 'REFERENCE_PRICE_AVAILABLE'
                    THEN reference_price_state
                WHEN shares_proxy_state <> 'SHARES_PROXY_AVAILABLE'
                    THEN shares_proxy_state
                WHEN presession_reference_market_cap_proxy < 100000000.0
                    THEN 'NUMERIC_RULES_PASS_UNDER_PROXY'
                ELSE 'MARKET_CAP_PROXY_NOT_BELOW_100M'
            END AS population_membership_reason,
            row_level_price_integrity_state,
            family_data_quality_verdict,
            fundamental_quality_state,
            CASE
                WHEN has_split_action OR has_ticker_change_action THEN 'LOCAL_REVIEW_REQUIRED'
                WHEN selected_price_hard_invalid THEN 'LOCAL_REVIEW_REQUIRED'
                ELSE 'PROXY_RESEARCH_USE_WITH_DECLARED_RESTRICTIONS'
            END AS local_audit_disposition,
            master_daily_id,
            fundamental_asof_id,
            market_calendar_build_run_id,
            fundamentals_build_run_id,
            fundamentals_source_file,
            fundamentals_source_file_row_number,
            false AS full_historical_us_lt100m_population_claim,
            false AS exact_point_shares_claim,
            false AS historical_float_claim,
            '{SCHEMA_VERSION}' AS schema_version,
            '{DATASET_ID}' AS dataset_id
        FROM represented
        """
    )

    row_count = connection.execute("SELECT COUNT(*) FROM candidate_output").fetchone()[0]
    state_rows = connection.execute(
        """
        SELECT population_membership_state, COUNT(*) AS rows
        FROM candidate_output
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    requested_rows = connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    if row_count != requested_rows:
        raise RuntimeError(
            f"Denominator mismatch: sessions={requested_rows}, output={row_count}"
        )
    connection.execute(
        f"""
        COPY candidate_output
        TO '{_sql_path(output_parquet)}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    connection.close()

    created_at = datetime.now(timezone.utc).isoformat()
    manifest_path = output_parquet.with_name(output_parquet.stem + "_manifest.json")
    summary_path = output_parquet.with_name(output_parquet.stem + "_summary.json")
    state_counts = {state: rows for state, rows in state_rows}
    summary = {
        "dataset_id": DATASET_ID,
        "scope": {
            "session_start": session_start,
            "session_end": session_end,
            "session_dates": session_dates,
            "tickers": tickers,
        },
        "share_policy": share_policy,
        "ttl_days": ttl_days,
        "requested_rows": requested_rows,
        "output_rows": row_count,
        "population_membership_state_counts": state_counts,
        "denominator_preserved": requested_rows == row_count,
    }
    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "promotion_state": "EXPERIMENTAL_CANDIDATE_NOT_CANONICAL",
        "created_at_utc": created_at,
        "config_path": str(config_path),
        "config_sha256": _sha256(config_path),
        "source_master_daily_root": str(master_daily_root),
        "source_instrument_master": str(instrument_master),
        "source_fundamentals_root": str(fundamentals_root),
        "source_market_calendar": str(market_calendar),
        "output_parquet": str(output_parquet),
        "output_sha256": _sha256(output_parquet),
        "output_size_bytes": output_parquet.stat().st_size,
        "summary_path": str(summary_path),
        "summary": summary,
        "claims": config["claims"],
    }
    _atomic_write_json(summary_path, summary)
    _atomic_write_json(manifest_path, manifest)
    return manifest


def main() -> int:
    args = _parser().parse_args()
    manifest = materialize(
        config_path=args.config,
        master_daily_root=args.master_daily_root,
        instrument_master=args.instrument_master,
        fundamentals_root=args.fundamentals_root,
        market_calendar=args.market_calendar,
        output_parquet=args.output_parquet,
        share_policy=args.share_policy,
        ttl_days=args.ttl_days,
        session_start=args.session_start,
        session_end=args.session_end,
        session_dates=args.session_dates,
        tickers=args.tickers,
        threads=args.threads,
        memory_limit=args.memory_limit,
        temp_directory=args.temp_directory,
    )
    print(json.dumps(manifest, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
