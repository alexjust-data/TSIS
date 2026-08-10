#!/usr/bin/env python3
"""Reconcile TA-3 sample source availability under the official G-only root."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

OFFICIAL_ROOT = "G:/TSIS/data/trades_ticks_prod_2005_2026/"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--sample-root", required=True, type=Path)
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
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _write_query(connection: duckdb.DuckDBPyConnection, sql: str, path: Path) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    connection.execute(f"COPY ({sql}) TO '{_sql_path(path)}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    return {
        "path": str(path),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
        "rows": connection.execute(f"SELECT COUNT(*) FROM ({sql})").fetchone()[0],
    }


def reconcile(config_path: Path, sample_root: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    configured_root = config["sources"]["raw_trade_root"].replace("\\", "/").rstrip("/") + "/"
    if configured_root != OFFICIAL_ROOT:
        raise ValueError(
            f"Configured trade root is not the frozen G-only authority: {configured_root}"
        )
    if config["sources"].get("legacy_root_fallback") != "PROHIBITED":
        raise ValueError("Legacy-root fallback is not explicitly prohibited")
    manifest_v1_path = sample_root / "sample_manifest_v0_1.json"
    summary_v1_path = sample_root / "sample_design_summary_v0_1.json"
    manifest_v1 = _read_json(manifest_v1_path)
    summary_v1 = _read_json(summary_v1_path)
    scope_path = sample_root / "selected_block_scope_sessions_v0_1.parquet"
    blocks_path = sample_root / "selected_blocks_v0_1.parquet"
    targets_path = sample_root / "selected_target_contexts_v0_1.parquet"

    connection = duckdb.connect(database=":memory:")
    connection.execute(
        f"CREATE VIEW scope AS SELECT * FROM read_parquet('{_sql_path(scope_path)}')"
    )
    connection.execute(
        f"CREATE VIEW blocks AS SELECT * FROM read_parquet('{_sql_path(blocks_path)}')"
    )
    connection.execute(
        f"CREATE VIEW targets AS SELECT * FROM read_parquet('{_sql_path(targets_path)}')"
    )
    authority = connection.execute(
        """
        SELECT
          COUNT(*) AS rows_total,
          COUNT(*) FILTER (WHERE source_exists) AS available_rows,
          COUNT(*) FILTER (WHERE NOT source_exists) AS unavailable_rows,
          COUNT(*) FILTER (WHERE source_exists IS NULL) AS null_state_rows,
          COUNT(*) FILTER (
            WHERE replace(source_path, '\\', '/') NOT LIKE
                  'G:/TSIS/data/trades_ticks_prod_2005_2026/%'
          ) AS unauthorized_root_rows,
          COUNT(*) FILTER (WHERE scope_role='TARGET') AS target_rows,
          COUNT(*) FILTER (WHERE scope_role='TARGET' AND source_exists)
            AS available_target_rows,
          COUNT(*) FILTER (WHERE scope_role='TARGET' AND NOT source_exists)
            AS unavailable_target_rows
        FROM scope
        """
    ).fetchone()
    names = [item[0] for item in connection.description]
    authority_metrics = dict(zip(names, authority, strict=True))

    # Recheck every declared path against the official root at reconciliation time.
    source_rows = connection.execute(
        "SELECT source_path, source_exists FROM scope ORDER BY block_id, governed_index"
    ).fetchall()
    recheck_mismatches = 0
    for source_path, declared_exists in source_rows:
        normalized = str(source_path).replace("\\", "/")
        if not normalized.startswith(OFFICIAL_ROOT):
            continue
        if Path(normalized).is_file() != bool(declared_exists):
            recheck_mismatches += 1

    connection.execute(
        """
        CREATE TEMP TABLE scope_cardinality AS
        SELECT
          *,
          SUM(CASE WHEN source_exists THEN 1 ELSE 0 END) OVER (
            PARTITION BY block_id ORDER BY governed_index
            ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING
          ) AS prior_20_available_file_count,
          SUM(CASE WHEN source_exists THEN 1 ELSE 0 END) OVER (
            PARTITION BY block_id ORDER BY governed_index
            ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING
          ) AS prior_60_available_file_count,
          SUM(CASE WHEN source_exists THEN 1 ELSE 0 END) OVER (
            PARTITION BY block_id ORDER BY governed_index
            ROWS BETWEEN 120 PRECEDING AND 1 PRECEDING
          ) AS prior_120_available_file_count
        FROM scope
        """
    )
    connection.execute(
        """
        CREATE TEMP TABLE target_audit AS
        SELECT
          block_id,
          cohort_id,
          selected_rank_in_cohort,
          target_ordinal,
          instrument_id,
          ticker_as_of_session,
          session_date,
          source_path,
          CASE WHEN source_exists
            THEN 'AVAILABLE_G_OFFICIAL'
            ELSE 'UNAVAILABLE_G_OFFICIAL'
          END AS target_source_state,
          prior_20_available_file_count,
          prior_60_available_file_count,
          prior_120_available_file_count,
          CASE WHEN prior_20_available_file_count >= 15
            THEN 'B20_FILE_CARDINALITY_PASS'
            ELSE 'B20_FILE_CARDINALITY_INSUFFICIENT'
          END AS b20_file_cardinality_state,
          CASE WHEN prior_60_available_file_count >= 40
            THEN 'B60_FILE_CARDINALITY_PASS'
            ELSE 'B60_FILE_CARDINALITY_INSUFFICIENT'
          END AS b60_file_cardinality_state,
          CASE WHEN prior_120_available_file_count >= 80
            THEN 'B120_FILE_CARDINALITY_PASS'
            ELSE 'B120_FILE_CARDINALITY_INSUFFICIENT'
          END AS b120_file_cardinality_state,
          'G:/TSIS/data/trades_ticks_prod_2005_2026' AS official_source_root,
          false AS legacy_root_fallback_used
        FROM scope_cardinality
        WHERE scope_role='TARGET'
        """
    )
    connection.execute(
        """
        CREATE TEMP TABLE block_audit AS
        WITH scope_summary AS (
          SELECT
            block_id,
            COUNT(*) AS scope_rows,
            COUNT(*) FILTER (WHERE source_exists) AS available_scope_rows,
            COUNT(*) FILTER (WHERE NOT source_exists) AS unavailable_scope_rows,
            COUNT(*) FILTER (WHERE scope_role='WARMUP' AND NOT source_exists)
              AS unavailable_warmup_rows,
            COUNT(*) FILTER (WHERE scope_role='INTERVENING_NON_TARGET' AND NOT source_exists)
              AS unavailable_intervening_rows
          FROM scope
          GROUP BY block_id
        ), target_summary AS (
          SELECT
            block_id,
            COUNT(*) FILTER (WHERE target_source_state='AVAILABLE_G_OFFICIAL')
              AS available_target_rows,
            COUNT(*) FILTER (WHERE target_source_state='UNAVAILABLE_G_OFFICIAL')
              AS unavailable_target_rows,
            MIN(prior_20_available_file_count) AS minimum_b20_available_files,
            MIN(prior_60_available_file_count) AS minimum_b60_available_files,
            MIN(prior_120_available_file_count) AS minimum_b120_available_files,
            COUNT(*) FILTER (WHERE b20_file_cardinality_state='B20_FILE_CARDINALITY_PASS')
              AS b20_pass_targets,
            COUNT(*) FILTER (WHERE b60_file_cardinality_state='B60_FILE_CARDINALITY_PASS')
              AS b60_pass_targets,
            COUNT(*) FILTER (WHERE b120_file_cardinality_state='B120_FILE_CARDINALITY_PASS')
              AS b120_pass_targets
          FROM target_audit
          GROUP BY block_id
        )
        SELECT
          b.block_id,
          b.cohort_id,
          b.selected_rank_in_cohort,
          b.instrument_id,
          b.ticker_as_of_session,
          b.block_start_session,
          b.block_end_session,
          s.* EXCLUDE (block_id),
          t.* EXCLUDE (block_id),
          CASE
            WHEN s.unavailable_scope_rows=0 THEN 'G_SOURCE_COMPLETE'
            WHEN t.unavailable_target_rows=0 THEN 'G_SOURCE_PARTIAL_TARGET_COMPLETE'
            ELSE 'G_SOURCE_PARTIAL_TARGET_UNAVAILABLE'
          END AS g_source_availability_state,
          'RETAIN_WITH_EXPLICIT_SOURCE_STATES' AS local_sample_disposition,
          false AS legacy_root_fallback_used
        FROM blocks b
        INNER JOIN scope_summary s USING (block_id)
        INNER JOIN target_summary t USING (block_id)
        """
    )

    target_audit_path = sample_root / "selected_target_g_source_audit_v0_1.parquet"
    block_audit_path = sample_root / "selected_block_g_source_audit_v0_1.parquet"
    target_output = _write_query(
        connection,
        "SELECT * FROM target_audit ORDER BY cohort_id, selected_rank_in_cohort, target_ordinal",
        target_audit_path,
    )
    block_output = _write_query(
        connection,
        "SELECT * FROM block_audit ORDER BY cohort_id, selected_rank_in_cohort",
        block_audit_path,
    )
    baseline_counts = {
        state: int(rows)
        for state, rows in connection.execute(
            """
            SELECT state, COUNT(*) FROM (
              SELECT b20_file_cardinality_state AS state FROM target_audit
              UNION ALL
              SELECT b60_file_cardinality_state FROM target_audit
              UNION ALL
              SELECT b120_file_cardinality_state FROM target_audit
            ) GROUP BY 1 ORDER BY 1
            """
        ).fetchall()
    }
    block_state_counts = {
        state: int(rows)
        for state, rows in connection.execute(
            "SELECT g_source_availability_state, COUNT(*) FROM block_audit GROUP BY 1 ORDER BY 1"
        ).fetchall()
    }
    connection.close()

    checks = {
        "official_g_root_only": authority_metrics["unauthorized_root_rows"] == 0,
        "source_state_complete": authority_metrics["null_state_rows"] == 0,
        "filesystem_recheck_exact": recheck_mismatches == 0,
        "scope_accounting_matches_v0_1": authority_metrics["unavailable_rows"]
        == summary_v1["selected_scope_missing_source_rows"],
        "target_accounting_matches_v0_1": authority_metrics["unavailable_target_rows"]
        == summary_v1["selected_target_missing_source_rows"],
        "target_denominator_preserved": target_output["rows"] == 2400,
        "block_denominator_preserved": block_output["rows"] == 240,
        "legacy_fallback_prohibited": True,
    }
    source_gate = "PASS_WITH_RESTRICTIONS" if all(checks.values()) else "FAIL"
    source_audit = {
        "audit_id": "trading_activity_ta3_g_only_source_audit_v0_1",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "official_source_root": OFFICIAL_ROOT.rstrip("/"),
        "legacy_root_fallback": "PROHIBITED",
        "authority_metrics": authority_metrics,
        "filesystem_recheck_mismatch_rows": recheck_mismatches,
        "baseline_file_cardinality_state_counts": baseline_counts,
        "block_source_state_counts": block_state_counts,
        "target_audit": target_output,
        "block_audit": block_output,
        "checks": checks,
        "source_gate": source_gate,
        "interpretation": (
            "Missing official-G files remain UNAVAILABLE and are retained in the "
            "sample denominator. File cardinality does not replace content-level "
            "coverage validation by the Binding A runner."
        ),
    }
    source_audit_path = sample_root / "g_only_source_audit_summary_v0_1.json"
    _atomic_json(source_audit_path, source_audit)

    summary_v2 = dict(summary_v1)
    summary_v2.update(
        {
            "supersedes_summary": "sample_design_summary_v0_1.json",
            "official_trade_source_root": OFFICIAL_ROOT.rstrip("/"),
            "legacy_root_fallback": "PROHIBITED",
            "g_only_source_audit": source_audit,
            "sample_manifest_gate_candidate": source_gate,
            "missing_source_semantics": "UNAVAILABLE_G_OFFICIAL_RETAINED_IN_DENOMINATOR",
        }
    )
    summary_v2_path = sample_root / "sample_design_summary_v0_2.json"
    _atomic_json(summary_v2_path, summary_v2)

    manifest_v2 = dict(manifest_v1)
    manifest_v2.update(
        {
            "schema_version": "trading_activity_ta3_sample_manifest_v0_2",
            "config_path": str(config_path),
            "config_sha256": _sha256(config_path),
            "created_at_utc": datetime.now(UTC).isoformat(),
            "supersedes_manifest": "sample_manifest_v0_1.json",
            "promotion_state": "FROZEN_EXPERIMENTAL_SAMPLE_NOT_CANONICAL",
            "official_trade_source_root": OFFICIAL_ROOT.rstrip("/"),
            "legacy_root_fallback": "PROHIBITED",
            "summary": summary_v2,
        }
    )
    manifest_v2["outputs"] = dict(manifest_v1["outputs"])
    manifest_v2["outputs"].update(
        {
            "selected_target_g_source_audit": target_output,
            "selected_block_g_source_audit": block_output,
            "g_only_source_audit_summary": {
                "path": str(source_audit_path),
                "sha256": _sha256(source_audit_path),
                "size_bytes": source_audit_path.stat().st_size,
            },
            "summary": {
                "path": str(summary_v2_path),
                "sha256": _sha256(summary_v2_path),
                "size_bytes": summary_v2_path.stat().st_size,
            },
        }
    )
    manifest_v2_path = sample_root / "sample_manifest_v0_2.json"
    _atomic_json(manifest_v2_path, manifest_v2)
    return {
        "source_gate": source_gate,
        "sample_manifest_v0_2": str(manifest_v2_path),
        "sample_manifest_v0_2_sha256": _sha256(manifest_v2_path),
        "summary_v0_2": str(summary_v2_path),
        "summary_v0_2_sha256": _sha256(summary_v2_path),
        "source_audit": source_audit,
    }


def main() -> int:
    args = _parser().parse_args()
    result = reconcile(args.config, args.sample_root)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["source_gate"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
