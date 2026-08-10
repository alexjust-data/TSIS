#!/usr/bin/env python3
"""Read-only G0-G3 audit for the 4,824-instrument presession selector."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


REQUIRED_TTLS = [90, 180, 365]
REQUIRED_SHARE_POLICIES = {
    "S1_DILUTED_FIRST": [
        "diluted_shares_outstanding",
        "basic_shares_outstanding",
    ],
    "S2_BASIC_FIRST": [
        "basic_shares_outstanding",
        "diluted_shares_outstanding",
    ],
}
FINAL_GATE_VERDICTS = {"PASS_WITH_RESTRICTIONS", "FAIL"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--master-daily-root", required=True, type=Path)
    parser.add_argument("--instrument-master", required=True, type=Path)
    parser.add_argument("--fundamentals-root", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--legacy-parquet", type=Path)
    parser.add_argument("--master-manifest", type=Path)
    parser.add_argument("--fundamentals-manifest", type=Path)
    parser.add_argument("--session-start", type=date.fromisoformat)
    parser.add_argument("--session-end", type=date.fromisoformat)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--memory-limit", default="8GB")
    parser.add_argument("--temp-directory", type=Path)
    return parser


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_value) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _parquet_glob(root: Path) -> str:
    return _sql_path(root).rstrip("/") + "/**/*.parquet"


def _fetch_one_dict(connection: duckdb.DuckDBPyConnection, sql: str) -> dict[str, Any]:
    row = connection.execute(sql).fetchone()
    assert row is not None
    names = [item[0] for item in connection.description]
    return dict(zip(names, row, strict=True))


def _fetch_dicts(connection: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    rows = connection.execute(sql).fetchall()
    names = [item[0] for item in connection.description]
    return [dict(zip(names, row, strict=True)) for row in rows]


def validate_g0_config(config: dict[str, Any]) -> dict[str, Any]:
    policies = {
        item.get("policy_id"): item.get("priority")
        for item in config.get("share_selection_candidates", [])
    }
    checks = {
        "parent_universe_frozen_to_4824": (
            config.get("parent_universe_id") == "lt1b_universe_v0_1"
            and config.get("parent_universe_expected_ticker_count") == 4824
        ),
        "cutoff_is_0400_new_york": (
            config.get("cutoff", {}).get("local_time") == "04:00:00"
            and config.get("cutoff", {}).get("timezone") == "America/New_York"
        ),
        "availability_is_strict": (
            config.get("cutoff", {}).get("availability_operator")
            == "strictly_before"
            and config.get("cutoff", {}).get("date_only_proxy_rule")
            == "source_as_of_date < session_date"
        ),
        "reference_price_is_prior_close": (
            config.get("reference_price", {}).get("field") == "prior_close"
            and config.get("reference_price", {}).get("semantic_name")
            == "PRESESSION_REFERENCE_PRICE"
            and config.get("reference_price", {}).get("source_price_view")
            == "daily_raw"
        ),
        "price_boundaries_frozen": (
            config.get("reference_price", {}).get("minimum_inclusive") == 0.5
            and config.get("reference_price", {}).get("maximum_inclusive") == 20.0
        ),
        "market_cap_threshold_is_strict_lt_100m": (
            config.get("market_cap_proxy", {}).get("threshold_exclusive")
            == 100_000_000.0
        ),
        "share_policies_complete": policies == REQUIRED_SHARE_POLICIES,
        "ttl_candidates_complete": (
            config.get("shares_ttl_candidates_days") == REQUIRED_TTLS
        ),
        "float_is_nonblocking_context": (
            config.get("float_policy", {}).get("membership_predicate") is False
            and config.get("float_policy", {}).get("missingness_blocks_ta3") is False
        ),
        "final_gate_is_not_predeclared": (
            set(config.get("possible_gate_verdicts", [])) == FINAL_GATE_VERDICTS
        ),
        "prohibited_claims_are_false": all(
            value is False for value in config.get("claims", {}).values()
        ),
    }
    return {
        "checks": checks,
        "g0_contract_gate": "PASS" if all(checks.values()) else "FAIL",
    }


def _scope_predicate(session_start: date | None, session_end: date | None) -> str:
    clauses = ["price_view = 'daily_raw'"]
    if session_start is not None:
        clauses.append(f"session_date >= DATE '{session_start.isoformat()}'")
    if session_end is not None:
        clauses.append(f"session_date <= DATE '{session_end.isoformat()}'")
    return " AND ".join(clauses)


def audit(
    config_path: Path,
    master_daily_root: Path,
    instrument_master: Path,
    fundamentals_root: Path,
    legacy_parquet: Path | None = None,
    master_manifest: Path | None = None,
    fundamentals_manifest: Path | None = None,
    session_start: date | None = None,
    session_end: date | None = None,
    threads: int = 4,
    memory_limit: str = "8GB",
    temp_directory: Path | None = None,
) -> dict[str, Any]:
    config = _read_json(config_path)
    assert config is not None
    g0 = validate_g0_config(config)

    connection = duckdb.connect(database=":memory:")
    connection.execute(f"SET threads={max(1, threads)}")
    connection.execute(f"SET memory_limit='{memory_limit}'")
    if temp_directory is not None:
        temp_directory.mkdir(parents=True, exist_ok=True)
        connection.execute(
            f"SET temp_directory='{_sql_path(temp_directory)}'"
        )

    scope_predicate = _scope_predicate(session_start, session_end)
    connection.execute(
        f"""
        CREATE VIEW master_daily_all AS
        SELECT *
        FROM read_parquet(
            '{_parquet_glob(master_daily_root)}',
            hive_partitioning=true,
            union_by_name=true
        )
        """
    )
    connection.execute(
        f"""
        CREATE TEMP TABLE sessions AS
        SELECT
            master_daily_id,
            instrument_id,
            ticker,
            session_date,
            expected_session,
            data_present,
            missing_expected_data,
            prior_close,
            selected_price_hard_invalid,
            has_split_action,
            has_ticker_change_action,
            has_any_corporate_action,
            row_level_price_integrity_state
        FROM master_daily_all
        WHERE {scope_predicate}
        """
    )
    connection.execute(
        f"""
        CREATE VIEW instrument_master AS
        SELECT * FROM read_parquet('{_sql_path(instrument_master)}')
        """
    )
    connection.execute(
        f"""
        CREATE VIEW fundamentals_all AS
        SELECT *
        FROM read_parquet(
            '{_parquet_glob(fundamentals_root)}',
            hive_partitioning=true,
            union_by_name=true
        )
        """
    )

    parent_metrics = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS rows_total,
            COUNT(DISTINCT ticker) AS ticker_count,
            COUNT(DISTINCT instrument_id) AS instrument_count,
            COUNT(*) FILTER (WHERE instrument_id IS NULL) AS null_instrument_rows,
            COUNT(*) FILTER (WHERE is_common_stock) AS common_stock_rows,
            COUNT(*) FILTER (WHERE NOT COALESCE(is_common_stock, false))
                AS non_common_or_unknown_rows,
            COUNT(*) FILTER (WHERE is_lt1b_operational) AS lt1b_operational_rows
        FROM instrument_master
        """,
    )
    g1_metrics = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS rows_total,
            COUNT(DISTINCT ticker) AS ticker_count,
            COUNT(DISTINCT instrument_id) AS instrument_count,
            COUNT(DISTINCT master_daily_id) AS master_daily_id_count,
            COUNT(DISTINCT struct_pack(ticker := ticker, session_date := session_date))
                AS ticker_session_key_count,
            COUNT(DISTINCT struct_pack(
                instrument_id := instrument_id,
                session_date := session_date
            )) FILTER (WHERE instrument_id IS NOT NULL)
                AS instrument_session_key_count,
            COUNT(*) FILTER (WHERE instrument_id IS NULL) AS null_instrument_rows,
            MIN(session_date) AS session_date_min,
            MAX(session_date) AS session_date_max,
            COUNT(*) FILTER (WHERE expected_session) AS expected_session_rows,
            COUNT(*) FILTER (WHERE data_present) AS data_present_rows,
            COUNT(*) FILTER (WHERE missing_expected_data) AS missing_expected_rows,
            COUNT(*) FILTER (WHERE prior_close IS NOT NULL) AS prior_close_available_rows,
            COUNT(*) FILTER (WHERE prior_close > 0) AS positive_prior_close_rows,
            COUNT(*) FILTER (WHERE prior_close BETWEEN 0.50 AND 20.00)
                AS reference_price_in_profile_rows,
            COUNT(*) FILTER (WHERE selected_price_hard_invalid)
                AS selected_price_hard_invalid_rows,
            COUNT(*) FILTER (WHERE has_split_action) AS split_review_rows,
            COUNT(*) FILTER (WHERE has_ticker_change_action)
                AS ticker_change_review_rows,
            COUNT(*) FILTER (WHERE has_any_corporate_action)
                AS any_corporate_action_rows
        FROM sessions
        """,
    )
    g1_join_metrics = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS rows_total,
            COUNT(*) FILTER (WHERE i.ticker IS NOT NULL) AS ticker_join_rows,
            COUNT(*) FILTER (
                WHERE i.ticker IS NOT NULL
                  AND s.instrument_id IS NOT DISTINCT FROM i.instrument_id
            ) AS exact_identity_join_rows,
            COUNT(*) FILTER (
                WHERE i.ticker IS NOT NULL
                  AND s.instrument_id IS DISTINCT FROM i.instrument_id
            ) AS identity_mismatch_rows
        FROM sessions s
        LEFT JOIN instrument_master i USING (ticker)
        """,
    )
    g1_duplicate_instrument_sessions = _fetch_one_dict(
        connection,
        """
        SELECT COUNT(*) AS groups
        FROM (
            SELECT instrument_id, session_date
            FROM sessions
            WHERE instrument_id IS NOT NULL
            GROUP BY 1, 2
            HAVING COUNT(*) > 1
        )
        """,
    )["groups"]
    g1_checks = {
        "parent_row_count_matches_4824": parent_metrics["rows_total"] == 4824,
        "parent_ticker_count_matches_4824": parent_metrics["ticker_count"] == 4824,
        "parent_ticker_unique": parent_metrics["rows_total"] == parent_metrics["ticker_count"],
        "daily_master_id_unique": g1_metrics["rows_total"] == g1_metrics["master_daily_id_count"],
        "daily_ticker_session_unique": (
            g1_metrics["rows_total"] == g1_metrics["ticker_session_key_count"]
        ),
        "daily_parent_ticker_join_complete": (
            g1_join_metrics["rows_total"] == g1_join_metrics["ticker_join_rows"]
        ),
        "daily_identity_join_exact": g1_join_metrics["identity_mismatch_rows"] == 0,
        "composite_identity_session_grain_unique": (
            g1_metrics["rows_total"] == g1_metrics["ticker_session_key_count"]
            and g1_join_metrics["identity_mismatch_rows"] == 0
        ),
        "hard_invalid_reference_price_zero": (
            g1_metrics["selected_price_hard_invalid_rows"] == 0
        ),
    }
    g1_hard = [
        "parent_row_count_matches_4824",
        "parent_ticker_count_matches_4824",
        "parent_ticker_unique",
        "daily_master_id_unique",
        "daily_ticker_session_unique",
        "daily_parent_ticker_join_complete",
        "daily_identity_join_exact",
        "composite_identity_session_grain_unique",
    ]
    g1_gate = (
        "PASS_WITH_RESTRICTIONS"
        if all(g1_checks[name] for name in g1_hard)
        else "FAIL"
    )

    g2_metrics = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS income_rows,
            COUNT(DISTINCT ticker) AS ticker_count,
            COUNT(DISTINCT instrument_id) AS instrument_count,
            MIN(as_of_date) AS as_of_date_min,
            MAX(as_of_date) AS as_of_date_max,
            COUNT(*) FILTER (WHERE instrument_id IS NULL) AS null_instrument_rows,
            COUNT(*) FILTER (WHERE instrument_identity_temporal_match)
                AS temporal_identity_match_rows,
            COUNT(*) FILTER (WHERE valid_for_event_context_candidate)
                AS valid_event_context_rows,
            COUNT(*) FILTER (
                WHERE basic_shares_outstanding > 0
                  AND isfinite(basic_shares_outstanding)
            ) AS positive_basic_rows,
            COUNT(*) FILTER (
                WHERE diluted_shares_outstanding > 0
                  AND isfinite(diluted_shares_outstanding)
            ) AS positive_diluted_rows,
            COUNT(*) FILTER (
                WHERE basic_shares_outstanding > 0
                  AND isfinite(basic_shares_outstanding)
                  AND diluted_shares_outstanding > 0
                  AND isfinite(diluted_shares_outstanding)
            ) AS positive_both_rows,
            COUNT(*) FILTER (WHERE period_end > as_of_date)
                AS period_after_availability_rows,
            COUNT(*) FILTER (WHERE as_of_semantics <> 'filing_date_available_from_date_only')
                AS unexpected_asof_semantics_rows
        FROM fundamentals_all
        WHERE statement_family = 'income_statements'
        """,
    )
    g2_duplicate_groups = _fetch_one_dict(
        connection,
        """
        SELECT COUNT(*) AS groups
        FROM (
            SELECT instrument_id, ticker, as_of_date
            FROM fundamentals_all
            WHERE statement_family = 'income_statements'
              AND instrument_id IS NOT NULL
            GROUP BY 1, 2, 3
            HAVING COUNT(*) > 1
        )
        """,
    )["groups"]
    g2_same_date_excluded = _fetch_one_dict(
        connection,
        """
        SELECT COUNT(*) AS rows
        FROM fundamentals_all f
        INNER JOIN (
            SELECT DISTINCT instrument_id, ticker, session_date
            FROM sessions
            WHERE instrument_id IS NOT NULL
        ) s
          ON f.instrument_id = s.instrument_id
         AND f.ticker = s.ticker
         AND f.as_of_date = s.session_date
        WHERE f.statement_family = 'income_statements'
          AND (
              (f.basic_shares_outstanding > 0 AND isfinite(f.basic_shares_outstanding))
              OR
              (f.diluted_shares_outstanding > 0 AND isfinite(f.diluted_shares_outstanding))
          )
        """,
    )["rows"]

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
    admissible_metrics = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS observation_rows,
            COUNT(DISTINCT instrument_id) AS instrument_count,
            MIN(as_of_date) AS as_of_date_min,
            MAX(as_of_date) AS as_of_date_max
        FROM admissible_share_observations
        """,
    )
    both_measure_distribution = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS rows,
            quantile_cont(diluted_shares_outstanding / basic_shares_outstanding, 0.01)
                AS ratio_p01,
            quantile_cont(diluted_shares_outstanding / basic_shares_outstanding, 0.50)
                AS ratio_p50,
            quantile_cont(diluted_shares_outstanding / basic_shares_outstanding, 0.99)
                AS ratio_p99,
            MAX(diluted_shares_outstanding / basic_shares_outstanding) AS ratio_max
        FROM admissible_share_observations
        WHERE basic_shares_outstanding > 0
          AND diluted_shares_outstanding > 0
        """,
    )

    legacy_metrics: dict[str, Any] | None = None
    if legacy_parquet is not None:
        connection.execute(
            f"CREATE VIEW legacy AS SELECT * FROM read_parquet('{_sql_path(legacy_parquet)}')"
        )
        legacy_metrics = _fetch_one_dict(
            connection,
            """
            SELECT
                COUNT(*) AS parent_ticker_rows,
                COUNT(DISTINCT l.ticker) AS parent_ticker_count,
                MIN(l.date) AS date_min,
                MAX(l.date) AS date_max,
                COUNT(*) FILTER (WHERE l.shares_outstanding_t > 0)
                    AS positive_selected_share_rows,
                COUNT(*) FILTER (WHERE l.shares_observed_date = l.date)
                    AS same_date_observation_rows,
                COUNT(*) FILTER (WHERE l.shares_source = 'diluted') AS diluted_source_rows,
                COUNT(*) FILTER (WHERE l.shares_source = 'basic') AS basic_source_rows
            FROM legacy l
            INNER JOIN instrument_master i USING (ticker)
            """,
        )

    g2_checks = {
        "income_source_has_rows": g2_metrics["income_rows"] > 0,
        "income_source_has_temporal_identity_matches": (
            g2_metrics["temporal_identity_match_rows"] > 0
        ),
        "admissible_proxy_observations_exist": admissible_metrics["observation_rows"] > 0,
        "admissible_proxy_instruments_exist": admissible_metrics["instrument_count"] > 0,
        "asof_semantics_expected": g2_metrics["unexpected_asof_semantics_rows"] == 0,
        "strict_same_date_exclusion_is_measurable": g2_same_date_excluded >= 0,
        "deterministic_duplicate_tie_break_required": g2_duplicate_groups >= 0,
    }
    g2_hard = [
        "income_source_has_rows",
        "income_source_has_temporal_identity_matches",
        "admissible_proxy_observations_exist",
        "admissible_proxy_instruments_exist",
        "asof_semantics_expected",
    ]
    g2_gate = (
        "PASS_WITH_RESTRICTIONS"
        if all(g2_checks[name] for name in g2_hard)
        else "FAIL"
    )

    connection.execute(
        """
        CREATE TEMP TABLE session_share_candidates AS
        SELECT
            s.master_daily_id,
            s.instrument_id,
            s.ticker,
            s.session_date,
            s.prior_close,
            s.has_split_action,
            s.has_ticker_change_action,
            f.fundamental_asof_id,
            f.as_of_date AS shares_as_of_date,
            f.period_end AS shares_period_end,
            date_diff('day', f.as_of_date, s.session_date) AS shares_age_days,
            f.basic_shares_outstanding,
            f.diluted_shares_outstanding,
            CASE
                WHEN f.diluted_shares_outstanding > 0
                    THEN f.diluted_shares_outstanding
                WHEN f.basic_shares_outstanding > 0
                    THEN f.basic_shares_outstanding
            END AS shares_s1_diluted_first,
            CASE
                WHEN f.basic_shares_outstanding > 0
                    THEN f.basic_shares_outstanding
                WHEN f.diluted_shares_outstanding > 0
                    THEN f.diluted_shares_outstanding
            END AS shares_s2_basic_first
        FROM sessions s
        ASOF LEFT JOIN admissible_share_observations f
          ON s.instrument_id = f.instrument_id
         AND s.ticker = f.ticker
         AND s.session_date > f.as_of_date
        """
    )
    g3_overall = _fetch_one_dict(
        connection,
        """
        SELECT
            COUNT(*) AS session_rows,
            COUNT(*) FILTER (WHERE fundamental_asof_id IS NOT NULL)
                AS rows_with_prior_share_observation,
            COUNT(*) FILTER (WHERE prior_close BETWEEN 0.50 AND 20.00)
                AS rows_in_price_profile,
            COUNT(*) FILTER (WHERE has_split_action OR has_ticker_change_action)
                AS corporate_action_review_rows,
            COUNT(*) FILTER (
                WHERE basic_shares_outstanding > 0
                  AND diluted_shares_outstanding > 0
                  AND basic_shares_outstanding <> diluted_shares_outstanding
            ) AS basic_diluted_difference_rows,
            COUNT(*) FILTER (
                WHERE shares_age_days = 0
            ) AS same_date_selected_rows
        FROM session_share_candidates
        """,
    )
    ttl_values = ", ".join(f"({ttl})" for ttl in REQUIRED_TTLS)
    g3_ttl_metrics = _fetch_dicts(
        connection,
        f"""
        SELECT
            ttl_days,
            COUNT(*) AS requested_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s1_diluted_first IS NOT NULL
                  AND shares_age_days <= ttl_days
                  AND NOT (has_split_action OR has_ticker_change_action)
            ) AS classifiable_s1_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s2_basic_first IS NOT NULL
                  AND shares_age_days <= ttl_days
                  AND NOT (has_split_action OR has_ticker_change_action)
            ) AS classifiable_s2_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s1_diluted_first IS NOT NULL
                  AND shares_age_days <= ttl_days
                  AND prior_close * shares_s1_diluted_first < 100000000.0
                  AND NOT (has_split_action OR has_ticker_change_action)
            ) AS eligible_s1_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s2_basic_first IS NOT NULL
                  AND shares_age_days <= ttl_days
                  AND prior_close * shares_s2_basic_first < 100000000.0
                  AND NOT (has_split_action OR has_ticker_change_action)
            ) AS eligible_s2_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s1_diluted_first IS NOT NULL
                  AND shares_s2_basic_first IS NOT NULL
                  AND shares_age_days <= ttl_days
                  AND (
                      (prior_close * shares_s1_diluted_first < 100000000.0)
                      IS DISTINCT FROM
                      (prior_close * shares_s2_basic_first < 100000000.0)
                  )
                  AND NOT (has_split_action OR has_ticker_change_action)
            ) AS classification_disagreement_rows,
            COUNT(*) FILTER (
                WHERE shares_s1_diluted_first IS NOT NULL
                  AND shares_age_days > ttl_days
            ) AS stale_s1_rows,
            COUNT(*) FILTER (
                WHERE shares_s2_basic_first IS NOT NULL
                  AND shares_age_days > ttl_days
            ) AS stale_s2_rows
        FROM session_share_candidates
        CROSS JOIN (VALUES {ttl_values}) AS ttl(ttl_days)
        GROUP BY ttl_days
        ORDER BY ttl_days
        """,
    )
    g3_year_ttl_metrics = _fetch_dicts(
        connection,
        f"""
        SELECT
            year(session_date) AS session_year,
            ttl_days,
            COUNT(*) AS requested_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s1_diluted_first IS NOT NULL
                  AND shares_age_days <= ttl_days
            ) AS classifiable_s1_rows,
            COUNT(*) FILTER (
                WHERE prior_close BETWEEN 0.50 AND 20.00
                  AND shares_s2_basic_first IS NOT NULL
                  AND shares_age_days <= ttl_days
            ) AS classifiable_s2_rows
        FROM session_share_candidates
        CROSS JOIN (VALUES {ttl_values}) AS ttl(ttl_days)
        GROUP BY session_year, ttl_days
        ORDER BY session_year, ttl_days
        """,
    )
    g3_checks = {
        "strict_prior_date_selection": g3_overall["same_date_selected_rows"] == 0,
        "all_ttl_candidates_evaluated": (
            [row["ttl_days"] for row in g3_ttl_metrics] == REQUIRED_TTLS
        ),
        "s1_has_classifiable_rows": any(
            row["classifiable_s1_rows"] > 0 for row in g3_ttl_metrics
        ),
        "s2_has_classifiable_rows": any(
            row["classifiable_s2_rows"] > 0 for row in g3_ttl_metrics
        ),
        "requested_denominator_preserved": all(
            row["requested_rows"] == g3_overall["session_rows"]
            for row in g3_ttl_metrics
        ),
        "ttl_coverage_is_monotonic_s1": all(
            left["classifiable_s1_rows"] <= right["classifiable_s1_rows"]
            for left, right in zip(g3_ttl_metrics, g3_ttl_metrics[1:])
        ),
        "ttl_coverage_is_monotonic_s2": all(
            left["classifiable_s2_rows"] <= right["classifiable_s2_rows"]
            for left, right in zip(g3_ttl_metrics, g3_ttl_metrics[1:])
        ),
    }
    g3_gate = (
        "PASS_WITH_RESTRICTIONS" if all(g3_checks.values()) else "FAIL"
    )

    connection.close()

    master_manifest_payload = _read_json(master_manifest)
    fundamentals_manifest_payload = _read_json(fundamentals_manifest)
    selector_gate = "NOT_EVALUATED_PENDING_FIXTURES_AND_PROBE"
    next_authorization = (
        "CONTROLLED_FIXTURE_IMPLEMENTATION_AUTHORIZED"
        if g0["g0_contract_gate"] == "PASS"
        and g1_gate == "PASS_WITH_RESTRICTIONS"
        and g2_gate == "PASS_WITH_RESTRICTIONS"
        and g3_gate == "PASS_WITH_RESTRICTIONS"
        else "REPAIR_FAILED_GATE_BEFORE_FIXTURES"
    )

    return {
        "audit_id": "population_target_presession_4824_g0_g3_audit_v0_1",
        "audit_role": "READ_ONLY_SOURCE_AND_PROXY_FIT_AUDIT",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "session_start": session_start,
            "session_end": session_end,
            "scope_type": "FULL_AVAILABLE_HISTORY"
            if session_start is None and session_end is None
            else "BOUNDED_AUDIT_SCOPE",
        },
        "config": {
            "path": str(config_path),
            "sha256": _sha256(config_path),
            "payload": config,
        },
        "sources": {
            "master_daily_root": str(master_daily_root),
            "instrument_master": str(instrument_master),
            "fundamentals_root": str(fundamentals_root),
            "legacy_parquet": str(legacy_parquet) if legacy_parquet else None,
            "master_manifest": master_manifest_payload,
            "fundamentals_manifest": fundamentals_manifest_payload,
        },
        "g0": g0,
        "g1": {
            "gate": g1_gate,
            "parent_metrics": parent_metrics,
            "daily_spine_metrics": g1_metrics,
            "identity_join_metrics": g1_join_metrics,
            "duplicate_instrument_session_groups": g1_duplicate_instrument_sessions,
            "checks": g1_checks,
        },
        "g2": {
            "gate": g2_gate,
            "fundamentals_metrics": g2_metrics,
            "duplicate_instrument_asof_groups": g2_duplicate_groups,
            "same_date_share_rows_conservatively_excluded": g2_same_date_excluded,
            "admissible_observation_metrics": admissible_metrics,
            "basic_diluted_ratio_distribution": both_measure_distribution,
            "legacy_reconciliation_metrics": legacy_metrics,
            "checks": g2_checks,
        },
        "g3": {
            "gate": g3_gate,
            "overall_metrics": g3_overall,
            "ttl_metrics": g3_ttl_metrics,
            "year_ttl_metrics": g3_year_ttl_metrics,
            "checks": g3_checks,
        },
        "selector_gate": selector_gate,
        "next_authorization": next_authorization,
        "broad_materialization_authorized": False,
        "ta3_sample_freeze_authorized": False,
        "canonical_promotion_authorized": False,
    }


def main() -> int:
    args = _parser().parse_args()
    payload = audit(
        config_path=args.config,
        master_daily_root=args.master_daily_root,
        instrument_master=args.instrument_master,
        fundamentals_root=args.fundamentals_root,
        legacy_parquet=args.legacy_parquet,
        master_manifest=args.master_manifest,
        fundamentals_manifest=args.fundamentals_manifest,
        session_start=args.session_start,
        session_end=args.session_end,
        threads=args.threads,
        memory_limit=args.memory_limit,
        temp_directory=args.temp_directory,
    )
    _atomic_write_json(args.output_json, payload)
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "scope": payload["scope"],
                "g0": payload["g0"]["g0_contract_gate"],
                "g1": payload["g1"]["gate"],
                "g2": payload["g2"]["gate"],
                "g3": payload["g3"]["gate"],
                "selector_gate": payload["selector_gate"],
                "next_authorization": payload["next_authorization"],
            },
            indent=2,
            default=_json_value,
        )
    )
    return 0 if payload["next_authorization"] != "REPAIR_FAILED_GATE_BEFORE_FIXTURES" else 1


if __name__ == "__main__":
    raise SystemExit(main())
