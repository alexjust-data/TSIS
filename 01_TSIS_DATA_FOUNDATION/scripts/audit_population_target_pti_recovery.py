#!/usr/bin/env python3
"""Read-only recovery audit for the historical population_target_pti panel."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq


REQUIRED_COLUMNS = {
    "date",
    "ticker",
    "entity_id",
    "status",
    "close_t",
    "shares_outstanding_t",
    "shares_source",
    "shares_observed_date",
    "shares_age_days",
    "market_cap_t",
    "is_small_cap_t",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-parquet", required=True, type=Path)
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--artifacts-json", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--master-daily-manifest", type=Path)
    parser.add_argument("--fundamentals-manifest", type=Path)
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def audit(
    legacy_parquet: Path,
    summary_json: Path,
    artifacts_json: Path,
    master_daily_manifest: Path | None = None,
    fundamentals_manifest: Path | None = None,
) -> dict[str, Any]:
    summary = _load_json(summary_json)
    artifacts = _load_json(artifacts_json)
    master_manifest = _load_json(master_daily_manifest)
    fundamentals = _load_json(fundamentals_manifest)
    assert summary is not None
    assert artifacts is not None

    parquet_file = pq.ParquetFile(legacy_parquet)
    columns = parquet_file.schema_arrow.names
    missing_columns = sorted(REQUIRED_COLUMNS.difference(columns))

    escaped = str(legacy_parquet).replace("'", "''")
    connection = duckdb.connect(database=":memory:")
    connection.execute(
        f"CREATE VIEW legacy AS SELECT * FROM read_parquet('{escaped}')"
    )
    metrics_row = connection.execute(
        """
        SELECT
            COUNT(*) AS rows_total,
            COUNT(DISTINCT ticker) AS tickers_total,
            COUNT(DISTINCT struct_pack(ticker := ticker, date := date)) AS unique_keys,
            COUNT(DISTINCT struct_pack(entity_id := entity_id, date := date))
                AS unique_entity_date_keys,
            COUNT(*) FILTER (WHERE entity_id IS NULL) AS null_entity_id_rows,
            MIN(date) AS date_min,
            MAX(date) AS date_max,
            COUNT(*) FILTER (WHERE close_t IS NOT NULL) AS rows_with_close_t,
            COUNT(*) FILTER (WHERE shares_outstanding_t IS NOT NULL) AS rows_with_shares_t,
            COUNT(*) FILTER (WHERE market_cap_t IS NOT NULL) AS rows_classifiable,
            COUNT(*) FILTER (
                WHERE shares_observed_date IS NOT NULL
                  AND shares_observed_date > date
            ) AS anti_lookahead_violations,
            COUNT(*) FILTER (
                WHERE shares_outstanding_t IS NOT NULL
                  AND shares_age_days > 180
            ) AS ttl_violations,
            COUNT(*) FILTER (
                WHERE shares_outstanding_t IS NOT NULL
                  AND shares_observed_date = date
            ) AS same_date_share_observation_rows,
            COUNT(*) FILTER (
                WHERE market_cap_t IS NOT NULL
                  AND ABS(market_cap_t - close_t * shares_outstanding_t)
                      > GREATEST(0.000001, ABS(market_cap_t) * 0.000000000001)
            ) AS market_cap_formula_mismatches,
            COUNT(*) FILTER (
                WHERE is_small_cap_t IS DISTINCT FROM
                    CASE
                        WHEN market_cap_t IS NULL THEN NULL
                        ELSE market_cap_t < 2000000000
                    END
            ) AS legacy_2b_flag_mismatches,
            COUNT(*) FILTER (
                WHERE close_t BETWEEN 0.50 AND 20.00
                  AND market_cap_t < 100000000
            ) AS same_day_rows_in_ta3_numeric_bands
        FROM legacy
        """
    ).fetchone()
    metric_names = [item[0] for item in connection.description]
    metrics = dict(zip(metric_names, metrics_row, strict=True))
    source_rows = connection.execute(
        """
        SELECT
            COALESCE(shares_source, '<NULL>') AS shares_source,
            COUNT(*) AS rows,
            COUNT(*) FILTER (WHERE shares_outstanding_t IS NOT NULL) AS usable_rows
        FROM legacy
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    collision_rows = connection.execute(
        """
        SELECT
            ticker,
            date,
            COUNT(*) AS rows,
            COUNT(DISTINCT entity_id) AS entity_count,
            STRING_AGG(DISTINCT COALESCE(entity_id, '<NULL>'), '|') AS entity_ids
        FROM legacy
        GROUP BY 1, 2
        HAVING COUNT(*) > 1
        ORDER BY rows DESC, ticker, date
        """
    ).fetchall()
    connection.close()

    declared = summary.get("metrics", {})
    checks = {
        "required_schema_present": not missing_columns,
        "metadata_row_count_matches_scan": (
            parquet_file.metadata.num_rows == metrics["rows_total"]
        ),
        "summary_row_count_matches_scan": (
            declared.get("rows_total") == metrics["rows_total"]
        ),
        "summary_ticker_count_matches_scan": (
            declared.get("tickers_total") == metrics["tickers_total"]
        ),
        "summary_classifiable_count_matches_scan": (
            declared.get("rows_classifiable") == metrics["rows_classifiable"]
        ),
        "grain_unique": metrics["rows_total"] == metrics["unique_keys"],
        "entity_date_grain_unique": (
            metrics["rows_total"] == metrics["unique_entity_date_keys"]
        ),
        "anti_lookahead_zero": metrics["anti_lookahead_violations"] == 0,
        "ttl_enforcement_pass": metrics["ttl_violations"] == 0,
        "market_cap_formula_pass": metrics["market_cap_formula_mismatches"] == 0,
        "legacy_2b_flag_semantics_pass": metrics["legacy_2b_flag_mismatches"] == 0,
    }
    hard_checks_pass = all(
        value for key, value in checks.items() if key != "grain_unique"
    )
    if hard_checks_pass:
        recovery_gate = "PASS" if checks["grain_unique"] else "PASS_WITH_RESTRICTIONS"
    else:
        recovery_gate = "FAIL"

    return {
        "audit_id": "population_target_pti_recovery_inventory_v0_1",
        "audit_role": "READ_ONLY_RECOVERY_AND_SOURCE_FIT_AUDIT",
        "created_at_utc": datetime.now().astimezone().isoformat(),
        "legacy_artifact": {
            "path": str(legacy_parquet),
            "size_bytes": legacy_parquet.stat().st_size,
            "sha256": sha256_file(legacy_parquet),
            "sha256_semantics": "post_recovery_integrity_anchor_without_original_hash_comparator",
            "parquet_created_by": parquet_file.metadata.created_by,
            "row_groups": parquet_file.metadata.num_row_groups,
            "schema_columns": columns,
            "missing_required_columns": missing_columns,
        },
        "declared_summary": summary,
        "declared_artifacts": artifacts,
        "physical_metrics": metrics,
        "shares_source_counts": [
            {"shares_source": row[0], "rows": row[1], "usable_rows": row[2]}
            for row in source_rows
        ],
        "ticker_date_collisions": [
            {
                "ticker": row[0],
                "date": row[1],
                "rows": row[2],
                "entity_count": row[3],
                "entity_ids": row[4],
            }
            for row in collision_rows
        ],
        "checks": checks,
        "recovery_integrity_gate": recovery_gate,
        "direct_session_start_selector_gate": "FAIL",
        "direct_reuse_blockers": [
            "TARGET_SESSION_CLOSE_SEMANTICS",
            "DATE_LEVEL_SHARES_AVAILABILITY",
            "DILUTED_OR_BASIC_PERIOD_AVERAGE_SHARES_PROXY",
            "LEGACY_THRESHOLD_FLAG_IS_2B_NOT_100M",
        ],
        "authorized_next_use": (
            "SOURCE_EVIDENCE_AND_INPUT_TO_NEW_SESSION_START_CANDIDATE"
            if recovery_gate in {"PASS", "PASS_WITH_RESTRICTIONS"}
            else "FORENSIC_EVIDENCE_ONLY"
        ),
        "upstream_manifests": {
            "master_daily_table": master_manifest,
            "fundamentals_asof_table": fundamentals,
        },
    }


def main() -> int:
    args = _parser().parse_args()
    payload = audit(
        args.legacy_parquet,
        args.summary_json,
        args.artifacts_json,
        args.master_daily_manifest,
        args.fundamentals_manifest,
    )
    _atomic_write_json(args.output_json, payload)
    print(json.dumps({
        "output_json": str(args.output_json),
        "recovery_integrity_gate": payload["recovery_integrity_gate"],
        "direct_session_start_selector_gate": payload[
            "direct_session_start_selector_gate"
        ],
        "rows_total": payload["physical_metrics"]["rows_total"],
        "sha256": payload["legacy_artifact"]["sha256"],
    }, indent=2))
    return (
        0
        if payload["recovery_integrity_gate"] in {"PASS", "PASS_WITH_RESTRICTIONS"}
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
