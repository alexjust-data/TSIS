#!/usr/bin/env python3
"""Independent physical validator for the restricted universe consumption gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


VALIDATOR_ID = "daily_eligible_universe_consumption_gate_validator_v0_1"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
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


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def validate(config_path: Path, run_root: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    final_path = run_root / "final_manifest.json"
    consumption_path = run_root / "consumption_manifest.json"
    accounting_path = run_root / "split_state_accounting.parquet"
    intervals_path = run_root / "development_target_denominator_intervals.parquet"
    for path in (final_path, consumption_path, accounting_path, intervals_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    final = _read_json(final_path)
    consumption = _read_json(consumption_path)
    candidate = Path(config["population_candidate"]["path"])
    targets = Path(config["development_targets"]["path"])
    calendar = Path(config["market_calendar"]["path"])

    con = duckdb.connect(database=":memory:")
    interval_metrics = con.execute(
        f"""
        SELECT
            COUNT(*)::BIGINT,
            COUNT(DISTINCT (block_id, instrument_id, ticker_as_of_session, session_date))::BIGINT,
            SUM(decision_point_count)::BIGINT,
            COUNT(*) FILTER (WHERE first_decision_timestamp_utc <= session_open_utc)::BIGINT,
            COUNT(*) FILTER (WHERE last_decision_timestamp_utc >= session_close_utc)::BIGINT,
            COUNT(*) FILTER (
                WHERE decision_point_count
                      <> date_diff('second', session_open_utc, session_close_utc) - 1
            )::BIGINT
        FROM read_parquet('{_sql_path(intervals_path)}')
        """
    ).fetchone()
    authority_metrics = con.execute(
        f"""
        SELECT
            COUNT(*)::BIGINT,
            COUNT(*) FILTER (WHERE p.population_context_id IS NULL)::BIGINT,
            COUNT(*) FILTER (WHERE p.population_membership_state <> 'ELIGIBLE_UNDER_DECLARED_PROXY')::BIGINT,
            COUNT(*) FILTER (WHERE i.population_context_id IS NULL)::BIGINT,
            COUNT(*) FILTER (
                WHERE i.decision_point_count <> CAST(ROUND(t.decision_seconds) AS BIGINT) - 1
                   OR i.session_open_utc IS DISTINCT FROM c.open_utc
                   OR i.session_close_utc IS DISTINCT FROM c.close_utc
                   OR i.instrument_id IS DISTINCT FROM t.instrument_id
                   OR i.ticker_as_of_session IS DISTINCT FROM t.ticker_as_of_session
                   OR i.session_date IS DISTINCT FROM t.session_date
            )::BIGINT
        FROM read_parquet('{_sql_path(targets)}') t
        LEFT JOIN read_parquet('{_sql_path(candidate)}') p USING (population_context_id)
        LEFT JOIN read_parquet('{_sql_path(intervals_path)}') i USING (population_context_id)
        LEFT JOIN read_parquet('{_sql_path(calendar)}') c ON c.session_date = t.session_date
        """
    ).fetchone()
    accounting_rows = con.execute(
        f"SELECT COUNT(*)::BIGINT FROM read_parquet('{_sql_path(accounting_path)}')"
    ).fetchone()[0]
    con.close()

    expected_targets = config["development_targets"]["expected_target_count"]
    expected_points = config["development_targets"]["expected_decision_points"]
    forbidden_names = {
        "temporal_validation_target_identities.parquet",
        "final_oos_target_identities.parquet",
        "wake_up_labels.parquet",
    }
    present_names = {path.name for path in run_root.iterdir()}
    checks = {
        "builder_final_pass": final.get("status") == "PASS",
        "consumption_manifest_pass": consumption.get("status") == "PASS",
        "consumption_manifest_hash_matches_final": _sha256(consumption_path) == final.get("consumption_manifest_sha256"),
        "accounting_hash_matches_final": _sha256(accounting_path) == final.get("split_state_accounting_sha256"),
        "interval_hash_matches_final": _sha256(intervals_path) == final.get("development_denominator_intervals_sha256"),
        "candidate_hash_exact": _sha256(candidate) == config["population_candidate"]["sha256"],
        "target_hash_exact": _sha256(targets) == config["development_targets"]["sha256"],
        "calendar_hash_exact": _sha256(calendar) == config["market_calendar"]["sha256"],
        "accounting_nonempty": int(accounting_rows) > 0,
        "interval_rows_exact": int(interval_metrics[0]) == expected_targets,
        "interval_identity_unique": int(interval_metrics[0]) == int(interval_metrics[1]),
        "logical_symbol_seconds_exact": int(interval_metrics[2]) == expected_points,
        "first_timestamp_strictly_after_open": int(interval_metrics[3]) == 0,
        "last_timestamp_strictly_before_close": int(interval_metrics[4]) == 0,
        "interval_cardinality_formula_exact": int(interval_metrics[5]) == 0,
        "target_authority_count_exact": int(authority_metrics[0]) == expected_targets,
        "target_population_resolves": int(authority_metrics[1]) == 0,
        "target_population_all_eligible": int(authority_metrics[2]) == 0,
        "every_target_has_interval": int(authority_metrics[3]) == 0,
        "target_interval_calendar_fields_exact": int(authority_metrics[4]) == 0,
        "selector_owns_membership": consumption.get("selector_owns_membership") is True,
        "bindings_do_not_recalculate_thresholds": consumption.get("bindings_recalculate_thresholds") is False,
        "not_canonical": consumption.get("promotion_state") == "RESTRICTED_EXPERIMENTAL_CONSUMPTION_NOT_CANONICAL",
        "no_lockbox_or_label_outputs": not bool(forbidden_names & present_names),
        "flat_denominator_not_materialized": consumption.get("development_symbol_second_denominator", {}).get("flat_materialization") is False,
    }
    return {
        "validator_id": VALIDATOR_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_root": str(run_root),
        "config_path": str(config_path),
        "config_sha256": _sha256(config_path),
        "interval_metrics": {
            "physical_rows": int(interval_metrics[0]),
            "logical_symbol_seconds": int(interval_metrics[2]),
        },
        "checks": checks,
        "validation_gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion_state": "RESTRICTED_EXPERIMENTAL_CONSUMPTION_NOT_CANONICAL",
    }


def main() -> int:
    args = _parser().parse_args()
    result = validate(args.config, args.run_root)
    _atomic_json(args.output_json, result)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["validation_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
