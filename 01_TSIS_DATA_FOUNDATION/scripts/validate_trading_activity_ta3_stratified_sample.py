#!/usr/bin/env python3
"""Independently validate the frozen TA-3 stratified sample."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--sample-root", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    return parser


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _one(connection: duckdb.DuckDBPyConnection, sql: str) -> dict[str, Any]:
    row = connection.execute(sql).fetchone()
    if row is None:
        raise RuntimeError("Validation query returned no row")
    columns = [item[0] for item in connection.description]
    return dict(zip(columns, row, strict=True))


def _many(connection: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    rows = connection.execute(sql).fetchall()
    columns = [item[0] for item in connection.description]
    return [dict(zip(columns, row, strict=True)) for row in rows]


def validate(config_path: Path, sample_root: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    manifest_path = sample_root / "sample_manifest_v0_2.json"
    summary_path = sample_root / "sample_design_summary_v0_2.json"
    if not manifest_path.is_file() or not summary_path.is_file():
        manifest_path = sample_root / "sample_manifest_v0_1.json"
        summary_path = sample_root / "sample_design_summary_v0_1.json"
    manifest = _read_json(manifest_path)
    summary = _read_json(summary_path)
    paths = {
        "accounting": sample_root / "development_context_accounting_v0_1.parquet",
        "feasible": sample_root / "feasible_blocks_v0_1.parquet",
        "blocks": sample_root / "selected_blocks_v0_1.parquet",
        "targets": sample_root / "selected_target_contexts_v0_1.parquet",
        "scope": sample_root / "selected_block_scope_sessions_v0_1.parquet",
    }
    missing_paths = [str(path) for path in paths.values() if not path.is_file()]
    if missing_paths:
        raise FileNotFoundError(f"Missing sample outputs: {missing_paths}")

    connection = duckdb.connect(database=":memory:")
    for name, path in paths.items():
        connection.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{_sql_path(path)}')")
    population_path = Path(config["sources"]["population_candidate"])
    connection.execute(
        f"CREATE VIEW population AS SELECT * FROM read_parquet('{_sql_path(population_path)}')"
    )
    block = config["block"]
    projection = config["binding_a_row_projection"]
    metrics = _one(
        connection,
        f"""
        SELECT
          (SELECT COUNT(*) FROM accounting) AS accounting_rows,
          (SELECT COUNT(*) FROM feasible) AS feasible_rows,
          (SELECT COUNT(*) FROM blocks) AS selected_block_rows,
          (SELECT COUNT(DISTINCT block_id) FROM blocks) AS selected_block_ids,
          (SELECT COUNT(*) FROM targets) AS selected_target_rows,
          (SELECT COUNT(DISTINCT population_context_id) FROM targets) AS selected_target_context_ids,
          (SELECT COUNT(*) FROM scope) AS selected_scope_rows,
          (SELECT COUNT(*) FROM scope WHERE NOT source_exists) AS missing_scope_source_rows,
          (SELECT COUNT(*) FROM scope WHERE scope_role='TARGET' AND NOT source_exists)
            AS missing_target_source_rows,
          (SELECT COUNT(*) FROM scope WHERE source_exists IS NULL)
            AS null_source_availability_rows,
          (SELECT COUNT(*) FROM scope
             WHERE replace(source_path, '\\', '/') NOT LIKE
                   'G:/TSIS/data/trades_ticks_prod_2005_2026/%')
            AS unauthorized_source_root_rows,
          (SELECT COUNT(*) FROM targets
             WHERE session_date < DATE '{config["scope"]["development_start"]}'
                OR session_date > DATE '{config["scope"]["development_end"]}')
            AS target_lockbox_violation_rows,
          (SELECT COUNT(*) FROM feasible
             WHERE block_start_session < DATE '{config["scope"]["development_start"]}'
                OR block_end_session > DATE '{config["scope"]["development_end"]}')
            AS feasible_lockbox_violation_rows,
          (SELECT COUNT(*) FROM targets
             WHERE population_membership_state <> '{config["population_binding"]["eligible_membership_state"]}')
            AS target_population_violation_rows,
          (SELECT COUNT(*) FROM targets
             WHERE target_ordinal < 1 OR target_ordinal > {block["target_eligible_contexts"]})
            AS target_ordinal_violation_rows,
          (SELECT COUNT(*) FROM targets
             WHERE expected_current_state_rows <> decision_seconds * {projection["current_state_rows_per_decision_second"]}
                OR expected_multiscale_contrast_rows <> decision_seconds * {projection["multiscale_contrast_rows_per_decision_second"]}
                OR expected_pit_baseline_rows <> decision_seconds * {projection["pit_baseline_rows_per_decision_second"]})
            AS row_projection_violation_rows,
          (SELECT COUNT(*) FROM blocks
             WHERE selection_hash <> sha256(
               '{config["sample_seed"]}' || '|' || cohort_id || '|' || instrument_id || '|' ||
               CAST(CAST(block_start_session AS DATE) AS VARCHAR)
             )) AS selection_hash_violation_rows,
          (SELECT COUNT(*) FROM blocks
             WHERE block_start_governed_index - warmup_start_governed_index
                   <> {block["prior_governed_sessions"]})
            AS warmup_distance_violation_rows
        """,
    )
    cohorts = _many(
        connection,
        "SELECT cohort_id, COUNT(*) AS blocks FROM blocks GROUP BY 1 ORDER BY 1",
    )
    targets_per_block = _many(
        connection,
        "SELECT block_id, COUNT(*) AS targets, MIN(target_ordinal) AS ordinal_min, "
        "MAX(target_ordinal) AS ordinal_max FROM targets GROUP BY 1 ORDER BY 1",
    )
    reuse = _one(
        connection,
        """
        SELECT
          (SELECT COALESCE(MAX(n),0) FROM (
            SELECT instrument_context_key, COUNT(*) AS n FROM blocks GROUP BY 1
          )) AS max_blocks_per_composite,
          (SELECT COALESCE(MAX(n),0) FROM (
            SELECT instrument_id, COUNT(*) AS n FROM blocks GROUP BY 1
          )) AS max_blocks_per_bare_instrument,
          (SELECT COUNT(*) FROM blocks a INNER JOIN blocks b
             ON a.instrument_context_key=b.instrument_context_key
            AND a.block_id < b.block_id
            AND ABS(a.block_start_governed_index-b.block_start_governed_index) < 252)
            AS reuse_separation_violation_pairs
        """,
    )
    population_reconciliation = _one(
        connection,
        """
        SELECT
          COUNT(*) FILTER (WHERE p.population_context_id IS NULL) AS unresolved_targets,
          COUNT(*) FILTER (
            WHERE p.population_context_id IS NOT NULL
              AND (
                p.instrument_id <> t.instrument_id
                OR p.ticker_as_of_session <> t.ticker_as_of_session
                OR p.session_date <> t.session_date
              )
          ) AS identity_mismatch_targets
        FROM targets t
        LEFT JOIN population p USING (population_context_id)
        """,
    )
    scope_target_reconciliation = _one(
        connection,
        """
        SELECT
          COUNT(*) FILTER (WHERE s.population_context_id IS NULL) AS targets_missing_from_scope,
          COUNT(*) FILTER (WHERE s.scope_role <> 'TARGET') AS targets_with_wrong_scope_role
        FROM targets t
        LEFT JOIN scope s
          ON t.block_id=s.block_id
         AND t.population_context_id=s.population_context_id
        """,
    )
    actual_output_hashes = {name: _sha256(path) for name, path in paths.items()}
    declared_outputs = manifest.get("outputs", {})
    hash_key = {
        "accounting": "development_context_accounting",
        "feasible": "feasible_blocks",
        "blocks": "selected_blocks",
        "targets": "selected_targets",
        "scope": "selected_scope_sessions",
    }
    output_hash_checks = {
        name: actual_output_hashes[name] == declared_outputs.get(hash_key[name], {}).get("sha256")
        for name in paths
    }
    expected_blocks = int(block["blocks_per_cohort"]) * len(config["scope"]["cohorts"])
    expected_targets = expected_blocks * int(block["target_eligible_contexts"])
    cohort_counts_ok = all(
        int(item["blocks"]) == int(block["blocks_per_cohort"]) for item in cohorts
    ) and len(cohorts) == len(config["scope"]["cohorts"])
    target_block_counts_ok = (
        all(
            int(item["targets"]) == int(block["target_eligible_contexts"])
            and int(item["ordinal_min"]) == 1
            and int(item["ordinal_max"]) == int(block["target_eligible_contexts"])
            for item in targets_per_block
        )
        and len(targets_per_block) == expected_blocks
    )
    checks = {
        "config_hash_matches_manifest": _sha256(config_path) == manifest.get("config_sha256"),
        "summary_hash_matches_manifest": _sha256(summary_path)
        == declared_outputs.get("summary", {}).get("sha256"),
        "all_output_hashes_match_manifest": all(output_hash_checks.values()),
        "selected_block_count_exact": metrics["selected_block_rows"] == expected_blocks,
        "selected_block_ids_unique": metrics["selected_block_ids"] == expected_blocks,
        "cohort_block_counts_exact": cohort_counts_ok,
        "selected_target_count_exact": metrics["selected_target_rows"] == expected_targets,
        "selected_targets_unique": metrics["selected_target_context_ids"] == expected_targets,
        "ten_targets_per_block": target_block_counts_ok,
        "development_lockbox_guard": metrics["target_lockbox_violation_rows"] == 0
        and metrics["feasible_lockbox_violation_rows"] == 0,
        "target_population_state_exact": metrics["target_population_violation_rows"] == 0,
        "target_ordinals_valid": metrics["target_ordinal_violation_rows"] == 0,
        "row_projection_exact": metrics["row_projection_violation_rows"] == 0,
        "selection_hash_exact": metrics["selection_hash_violation_rows"] == 0,
        "warmup_distance_exact": metrics["warmup_distance_violation_rows"] == 0,
        "composite_reuse_limit": reuse["max_blocks_per_composite"]
        <= int(block["maximum_blocks_per_composite_instrument"]),
        "bare_instrument_reuse_limit": reuse["max_blocks_per_bare_instrument"]
        <= int(block["maximum_blocks_per_bare_instrument_id"]),
        "reuse_separation_exact": reuse["reuse_separation_violation_pairs"] == 0,
        "source_availability_state_complete": metrics["null_source_availability_rows"] == 0,
        "official_g_source_authority_exact": metrics["unauthorized_source_root_rows"] == 0,
        "missing_source_accounting_preserved": metrics["missing_scope_source_rows"]
        == summary.get("selected_scope_missing_source_rows")
        and metrics["missing_target_source_rows"]
        == summary.get("selected_target_missing_source_rows"),
        "population_contexts_resolve": population_reconciliation["unresolved_targets"] == 0,
        "population_identity_exact": population_reconciliation["identity_mismatch_targets"] == 0,
        "targets_resolve_in_scope": scope_target_reconciliation["targets_missing_from_scope"] == 0,
        "target_scope_roles_exact": scope_target_reconciliation["targets_with_wrong_scope_role"]
        == 0,
        "prohibited_claims_false": not manifest.get("claims", {}).get(
            "validation_lockbox_opened", True
        )
        and not manifest.get("claims", {}).get("final_test_lockbox_opened", True)
        and not manifest.get("claims", {}).get("full_historical_us_lt100m_population", True)
        and not manifest.get("claims", {}).get("canonical_feature_promotion", True),
    }
    connection.close()
    hard_shortfalls = [
        {"cohort_id": cohort_id, **shortfall}
        for cohort_id, audit in summary.get("cohort_selection_audits", {}).items()
        for shortfall in audit.get("shortfalls", [])
    ]
    validation_gate = "PASS_WITH_RESTRICTIONS" if all(checks.values()) else "FAIL"
    return {
        "validator_id": "trading_activity_ta3_stratified_sample_validator_v0_1",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "sample_root": str(sample_root),
        "sample_manifest": str(manifest_path),
        "sample_manifest_sha256": _sha256(manifest_path),
        "metrics": metrics,
        "cohort_counts": cohorts,
        "reuse_metrics": reuse,
        "population_reconciliation": population_reconciliation,
        "scope_target_reconciliation": scope_target_reconciliation,
        "output_hash_checks": output_hash_checks,
        "hard_quota_shortfalls": hard_shortfalls,
        "checks": checks,
        "validation_gate": validation_gate,
        "promotion_state": "VALIDATED_FROZEN_EXPERIMENTAL_SAMPLE_NOT_CANONICAL"
        if validation_gate != "FAIL"
        else "INVALID_SAMPLE_NOT_AUTHORIZED",
    }


def main() -> int:
    args = _parser().parse_args()
    result = validate(args.config, args.sample_root)
    _atomic_json(args.output_json, result)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["validation_gate"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
