#!/usr/bin/env python3
"""Independent validator for a presession-selector candidate artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq


REQUIRED_COLUMNS = {
    "population_context_id",
    "instrument_id",
    "ticker_as_of_session",
    "session_date",
    "presession_cutoff_utc",
    "parent_universe_id",
    "presession_reference_price",
    "reference_price_state",
    "shares_proxy_as_of_session",
    "shares_measure_type",
    "shares_as_of_date",
    "shares_age_days",
    "shares_source_row_id",
    "share_selection_policy_id",
    "shares_ttl_policy_id",
    "shares_proxy_state",
    "presession_reference_market_cap_proxy",
    "market_cap_calculation_state",
    "population_membership_state",
    "population_membership_reason",
    "master_daily_id",
    "fundamental_asof_id",
    "full_historical_us_lt100m_population_claim",
    "exact_point_shares_claim",
    "historical_float_claim",
    "schema_version",
    "dataset_id",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-parquet", required=True, type=Path)
    parser.add_argument("--candidate-manifest", required=True, type=Path)
    parser.add_argument("--fundamentals-root", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _parquet_glob(root: Path) -> str:
    return _sql_path(root).rstrip("/") + "/**/*.parquet"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _fetch_one(connection: duckdb.DuckDBPyConnection, sql: str) -> dict[str, Any]:
    row = connection.execute(sql).fetchone()
    assert row is not None
    names = [item[0] for item in connection.description]
    return dict(zip(names, row, strict=True))


def _fetch_many(connection: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    rows = connection.execute(sql).fetchall()
    names = [item[0] for item in connection.description]
    return [dict(zip(names, row, strict=True)) for row in rows]


def validate(
    candidate_parquet: Path,
    candidate_manifest: Path,
    fundamentals_root: Path,
) -> dict[str, Any]:
    manifest = json.loads(candidate_manifest.read_text(encoding="utf-8-sig"))
    schema_columns = pq.ParquetFile(candidate_parquet).schema_arrow.names
    missing_columns = sorted(REQUIRED_COLUMNS.difference(schema_columns))

    connection = duckdb.connect(database=":memory:")
    connection.execute(
        f"CREATE VIEW candidate AS SELECT * FROM read_parquet('{_sql_path(candidate_parquet)}')"
    )
    connection.execute(
        f"""
        CREATE VIEW fundamentals AS
        SELECT * FROM read_parquet(
            '{_parquet_glob(fundamentals_root)}',
            hive_partitioning=true,
            union_by_name=true
        )
        """
    )
    metrics = _fetch_one(
        connection,
        """
        SELECT
            COUNT(*) AS rows_total,
            COUNT(DISTINCT population_context_id) AS context_id_count,
            COUNT(DISTINCT master_daily_id) AS master_daily_id_count,
            COUNT(DISTINCT struct_pack(
                instrument_id := instrument_id,
                ticker := ticker_as_of_session,
                session_date := session_date
            )) AS composite_grain_count,
            COUNT(DISTINCT ticker_as_of_session) AS ticker_count,
            COUNT(DISTINCT session_date) AS session_count,
            MIN(session_date) AS session_date_min,
            MAX(session_date) AS session_date_max,
            COUNT(*) FILTER (
                WHERE extract(hour FROM timezone('America/New_York', presession_cutoff_utc)) <> 4
                   OR extract(minute FROM timezone('America/New_York', presession_cutoff_utc)) <> 0
            ) AS cutoff_not_0400_et_rows,
            COUNT(*) FILTER (
                WHERE shares_as_of_date IS NOT NULL
                  AND shares_as_of_date >= session_date
            ) AS non_strict_shares_cutoff_rows,
            COUNT(*) FILTER (
                WHERE presession_reference_market_cap_proxy IS NOT NULL
                  AND ABS(
                      presession_reference_market_cap_proxy
                      - presession_reference_price * shares_proxy_as_of_session
                  ) > GREATEST(
                      0.000001,
                      ABS(presession_reference_market_cap_proxy) * 0.000000000001
                  )
            ) AS market_cap_formula_mismatch_rows,
            COUNT(*) FILTER (
                WHERE population_membership_state = 'ELIGIBLE_UNDER_DECLARED_PROXY'
                  AND NOT (
                      presession_reference_price BETWEEN 0.50 AND 20.00
                      AND presession_reference_market_cap_proxy < 100000000.0
                      AND shares_proxy_state = 'SHARES_PROXY_AVAILABLE'
                  )
            ) AS invalid_eligible_rows,
            COUNT(*) FILTER (
                WHERE population_membership_state = 'INELIGIBLE_PRICE'
                  AND presession_reference_price BETWEEN 0.50 AND 20.00
            ) AS invalid_price_ineligible_rows,
            COUNT(*) FILTER (
                WHERE population_membership_state = 'INELIGIBLE_MARKET_CAP_PROXY'
                  AND presession_reference_market_cap_proxy < 100000000.0
            ) AS invalid_cap_ineligible_rows,
            COUNT(*) FILTER (
                WHERE full_historical_us_lt100m_population_claim
                   OR exact_point_shares_claim
                   OR historical_float_claim
            ) AS prohibited_claim_true_rows,
            COUNT(*) FILTER (
                WHERE share_selection_policy_id <> 'S1_DILUTED_FIRST'
                   OR shares_ttl_policy_id <> 'SHARES_TTL_180D'
            ) AS unexpected_binding_rows
        FROM candidate
        """,
    )
    source_mismatch = _fetch_one(
        connection,
        """
        SELECT COUNT(*) AS rows
        FROM candidate c
        INNER JOIN fundamentals f
          ON c.shares_source_row_id = f.fundamental_asof_id
        WHERE c.ticker_as_of_session <> f.ticker
           OR c.instrument_id <> f.instrument_id
        """,
    )["rows"]
    unresolved_source_ids = _fetch_one(
        connection,
        """
        SELECT COUNT(*) AS rows
        FROM candidate c
        LEFT JOIN fundamentals f
          ON c.shares_source_row_id = f.fundamental_asof_id
        WHERE c.shares_source_row_id IS NOT NULL
          AND f.fundamental_asof_id IS NULL
        """,
    )["rows"]
    state_counts = _fetch_many(
        connection,
        """
        SELECT population_membership_state, COUNT(*) AS rows
        FROM candidate
        GROUP BY 1
        ORDER BY 1
        """,
    )
    price_bands = _fetch_many(
        connection,
        """
        SELECT
            CASE
                WHEN presession_reference_price >= 0.50 AND presession_reference_price < 1.00 THEN 'P_0_50_1'
                WHEN presession_reference_price >= 1.00 AND presession_reference_price < 2.00 THEN 'P_1_2'
                WHEN presession_reference_price >= 2.00 AND presession_reference_price < 5.00 THEN 'P_2_5'
                WHEN presession_reference_price >= 5.00 AND presession_reference_price < 10.00 THEN 'P_5_10'
                WHEN presession_reference_price >= 10.00 AND presession_reference_price <= 20.00 THEN 'P_10_20'
            END AS price_band,
            COUNT(*) AS rows
        FROM candidate
        WHERE presession_reference_price BETWEEN 0.50 AND 20.00
        GROUP BY 1
        ORDER BY 1
        """,
    )
    cap_bands = _fetch_many(
        connection,
        """
        SELECT
            CASE
                WHEN presession_reference_market_cap_proxy < 25000000.0 THEN 'MC_LT_25M'
                WHEN presession_reference_market_cap_proxy < 50000000.0 THEN 'MC_25_50M'
                WHEN presession_reference_market_cap_proxy < 75000000.0 THEN 'MC_50_75M'
                WHEN presession_reference_market_cap_proxy < 100000000.0 THEN 'MC_75_100M'
            END AS market_cap_band,
            COUNT(*) AS rows
        FROM candidate
        WHERE population_membership_state = 'ELIGIBLE_UNDER_DECLARED_PROXY'
        GROUP BY 1
        ORDER BY 1
        """,
    )
    connection.close()

    state_row_total = sum(item["rows"] for item in state_counts)
    price_band_names = {item["price_band"] for item in price_bands}
    cap_band_names = {item["market_cap_band"] for item in cap_bands}
    checks = {
        "required_schema_present": not missing_columns,
        "output_hash_matches_manifest": _sha256(candidate_parquet)
        == manifest.get("output_sha256"),
        "row_count_matches_manifest": metrics["rows_total"]
        == manifest.get("summary", {}).get("output_rows"),
        "denominator_preserved": metrics["rows_total"]
        == manifest.get("summary", {}).get("requested_rows"),
        "context_id_unique": metrics["rows_total"] == metrics["context_id_count"],
        "master_daily_id_unique": metrics["rows_total"]
        == metrics["master_daily_id_count"],
        "composite_grain_unique": metrics["rows_total"]
        == metrics["composite_grain_count"],
        "cutoff_is_0400_et": metrics["cutoff_not_0400_et_rows"] == 0,
        "strict_shares_cutoff": metrics["non_strict_shares_cutoff_rows"] == 0,
        "market_cap_formula_exact": metrics["market_cap_formula_mismatch_rows"] == 0,
        "eligible_semantics_valid": metrics["invalid_eligible_rows"] == 0,
        "ineligible_price_semantics_valid": metrics["invalid_price_ineligible_rows"] == 0,
        "ineligible_cap_semantics_valid": metrics["invalid_cap_ineligible_rows"] == 0,
        "prohibited_claims_false": metrics["prohibited_claim_true_rows"] == 0,
        "primary_binding_exact": metrics["unexpected_binding_rows"] == 0,
        "shares_source_identity_exact": source_mismatch == 0,
        "shares_source_ids_resolve": unresolved_source_ids == 0,
        "state_accounting_closes": state_row_total == metrics["rows_total"],
        "all_five_price_bands_present": len(price_band_names) == 5,
        "all_four_eligible_cap_bands_present": len(cap_band_names) == 4,
        "multiple_temporal_cohorts_present": metrics["session_count"] >= 5,
    }
    return {
        "validator_id": "population_target_presession_4824_candidate_validator_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_parquet": str(candidate_parquet),
        "candidate_sha256": _sha256(candidate_parquet),
        "candidate_manifest": str(candidate_manifest),
        "schema_columns": schema_columns,
        "missing_required_columns": missing_columns,
        "metrics": metrics,
        "shares_source_identity_mismatch_rows": source_mismatch,
        "unresolved_shares_source_id_rows": unresolved_source_ids,
        "state_counts": state_counts,
        "price_bands": price_bands,
        "eligible_market_cap_bands": cap_bands,
        "checks": checks,
        "validation_gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion_state": "VALIDATED_EXPERIMENTAL_CANDIDATE_NOT_CANONICAL",
    }


def main() -> int:
    args = _parser().parse_args()
    result = validate(
        args.candidate_parquet,
        args.candidate_manifest,
        args.fundamentals_root,
    )
    _atomic_write_json(args.output_json, result)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["validation_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
