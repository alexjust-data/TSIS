#!/usr/bin/env python3
"""Bind the experimental Daily Eligible Universe to A/B consumption evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq

from trading_activity_stage8_target_only_contract import aggregate_contract


GATE_ID = "daily_eligible_universe_restricted_consumption_gate_v0_1"
SCHEMA_VERSION = "daily_eligible_universe_consumption_manifest_v0_1"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--memory-limit", default="8GB")
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str) + "\n")


def _log(path: Path, message: str) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"[{_now()}] {message}\n")


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _git_state(repo_root: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        return result.stdout.strip()

    return {
        "branch": run("branch", "--show-current"),
        "commit": run("rev-parse", "HEAD"),
        "dirty": bool(run("status", "--porcelain")),
    }


def _heartbeat(
    output_root: Path,
    run_id: str,
    status: str,
    stage: str,
    **fields: Any,
) -> None:
    payload = {
        "run_id": run_id,
        "observed_at_utc": _now(),
        "status": status,
        "stage": stage,
        "wrapper_pid": os.getpid(),
        "wrapper_pid_alive": True,
        **fields,
    }
    _atomic_json(output_root / "heartbeat_latest.json", payload)
    _append_jsonl(output_root / "heartbeat.jsonl", payload)


def _verify_source(source: dict[str, Any], path_key: str = "path") -> Path:
    path = Path(source[path_key])
    if not path.is_file():
        raise FileNotFoundError(path)
    expected = source[f"{path_key.removesuffix('_path')}_sha256"] if path_key.endswith("_path") else source["sha256"]
    actual = _sha256(path)
    if actual != expected:
        raise ValueError(f"SHA-256 drift for {path}: {actual} != {expected}")
    return path


def _split_case(splits: dict[str, list[str]]) -> str:
    branches = []
    for split_id, (start, end) in splits.items():
        branches.append(
            f"WHEN session_date BETWEEN DATE '{start}' AND DATE '{end}' THEN '{split_id}'"
        )
    return "CASE " + " ".join(branches) + " ELSE 'OUTSIDE_EXPERIMENT_SPLITS' END"


def _target_rows(path: Path) -> list[dict[str, Any]]:
    columns = [
        "block_id",
        "instrument_id",
        "ticker_as_of_session",
        "session_date",
        "decision_seconds",
        "session_minutes",
        "is_early_close",
    ]
    return pq.read_table(path, columns=columns).to_pylist()


def build(config_path: Path, output_root: Path, run_id: str, threads: int, memory_limit: str) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite existing run root: {output_root}")
    output_root.mkdir(parents=True)
    log_path = output_root / "run.log"
    monitor_command = f"Get-Content -LiteralPath '{output_root / 'heartbeat_latest.json'}' -Raw"
    repo_root = Path(__file__).resolve().parents[2]
    config = _read_json(config_path)
    started_at = _now()
    pre_manifest = {
        "run_id": run_id,
        "status": "STARTING",
        "created_at_utc": started_at,
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "config_path": str(config_path.resolve()),
        "config_sha256": _sha256(config_path),
        "command_line": subprocess.list2cmdline(sys.argv),
        "cwd": str(Path.cwd()),
        "host": platform.node(),
        "python": sys.version,
        "duckdb": duckdb.__version__,
        "wrapper_pid": os.getpid(),
        "mode": "FULL_RESTRICTED_CONSUMPTION_GATE",
        "input_roots": [
            config["population_candidate"]["path"],
            config["development_targets"]["path"],
            config["market_calendar"]["path"],
        ],
        "output_root": str(output_root),
        "resume_policy": "NO_RESUME_SHORT_FAIL_CLOSED_NEW_RUN_ID_REQUIRED",
        "overwrite_policy": "PROHIBITED",
        "success_criteria": "ALL_HARD_CHECKS_PASS",
        "monitor_command": monitor_command,
        "git": _git_state(repo_root),
    }
    _atomic_json(output_root / "pre_manifest.json", pre_manifest)
    _atomic_json(
        output_root / "pid_manifest.json",
        {
            "run_id": run_id,
            "wrapper_pid": os.getpid(),
            "process_name": "python",
            "started_at_utc": started_at,
            "stage": "STARTING",
            "expected_alive": True,
        },
    )
    _heartbeat(output_root, run_id, "RUNNING", "VERIFY_SOURCE_HASHES")
    _log(log_path, "gate started")

    final_path = output_root / "final_manifest.json"
    try:
        candidate_cfg = config["population_candidate"]
        targets_cfg = config["development_targets"]
        candidate_path = _verify_source(candidate_cfg)
        candidate_manifest_path = Path(candidate_cfg["manifest_path"])
        if _sha256(candidate_manifest_path) != candidate_cfg["manifest_sha256"]:
            raise ValueError("Population candidate manifest SHA-256 drift")
        target_path = _verify_source(targets_cfg)
        sample_manifest_path = Path(targets_cfg["sample_manifest_path"])
        if _sha256(sample_manifest_path) != targets_cfg["sample_manifest_sha256"]:
            raise ValueError("TA-3 sample manifest SHA-256 drift")
        calendar_path = _verify_source(config["market_calendar"])
        cardinality_path = Path(targets_cfg["cardinality_contract_path"])
        if _sha256(cardinality_path) != targets_cfg["cardinality_contract_sha256"]:
            raise ValueError("Cardinality contract SHA-256 drift")

        candidate_manifest = _read_json(candidate_manifest_path)
        source_manifest_checks = {
            "candidate_output_hash_bound": candidate_manifest.get("output_sha256") == candidate_cfg["sha256"],
            "candidate_remains_experimental": candidate_manifest.get("promotion_state") == "EXPERIMENTAL_CANDIDATE_NOT_CANONICAL",
            "candidate_exact_point_shares_claim_false": not candidate_manifest.get("claims", {}).get("exact_point_shares_outstanding", True),
            "candidate_full_population_claim_false": not candidate_manifest.get("claims", {}).get("full_historical_us_lt100m_population", True),
        }

        _heartbeat(output_root, run_id, "RUNNING", "AUDIT_MEMBERSHIP_AND_SPLITS")
        con = duckdb.connect(database=":memory:")
        con.execute(f"SET threads={max(1, threads)}")
        con.execute(f"SET memory_limit='{memory_limit}'")
        con.execute(f"CREATE VIEW candidate AS SELECT * FROM read_parquet('{_sql_path(candidate_path)}')")
        con.execute(f"CREATE VIEW targets AS SELECT * FROM read_parquet('{_sql_path(target_path)}')")
        con.execute(f"CREATE VIEW calendar AS SELECT * FROM read_parquet('{_sql_path(calendar_path)}')")
        split_case = _split_case(config["splits"])
        con.execute(
            f"""
            CREATE TEMP TABLE split_state_accounting AS
            SELECT
                {split_case} AS split_id,
                population_membership_state,
                COUNT(*)::BIGINT AS row_count,
                COUNT(DISTINCT instrument_id)::BIGINT AS instrument_count,
                MIN(session_date) AS min_session_date,
                MAX(session_date) AS max_session_date
            FROM candidate
            GROUP BY 1, 2
            ORDER BY 1, 2
            """
        )
        accounting_path = output_root / "split_state_accounting.parquet"
        con.execute(
            f"COPY split_state_accounting TO '{_sql_path(accounting_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        totals = con.execute(
            """
            SELECT
                COUNT(*)::BIGINT,
                COUNT(*) FILTER (WHERE population_membership_state = 'ELIGIBLE_UNDER_DECLARED_PROXY')::BIGINT,
                COUNT(DISTINCT population_context_id)::BIGINT,
                COUNT(DISTINCT (instrument_id, ticker_as_of_session, session_date))::BIGINT
            FROM candidate
            """
        ).fetchone()
        selector = config["selector_policy"]
        invalid_eligible = con.execute(
            f"""
            SELECT COUNT(*)::BIGINT
            FROM candidate
            WHERE population_membership_state = '{candidate_cfg['eligible_state']}'
              AND NOT (
                presession_reference_price >= {selector['minimum_price_inclusive']}
                AND presession_reference_price <= {selector['maximum_price_inclusive']}
                AND presession_reference_market_cap_proxy < {selector['maximum_market_cap_proxy_exclusive']}
                AND share_selection_policy_id = '{candidate_cfg['share_selection_policy_id']}'
                AND shares_ttl_policy_id = '{candidate_cfg['shares_ttl_policy_id']}'
                AND NOT exact_point_shares_claim
                AND NOT full_historical_us_lt100m_population_claim
              )
            """
        ).fetchone()[0]

        _heartbeat(output_root, run_id, "RUNNING", "RECONCILE_DEVELOPMENT_TARGETS")
        target_metrics = con.execute(
            """
            SELECT
                COUNT(*)::BIGINT AS target_rows,
                COUNT(DISTINCT (t.block_id, t.instrument_id, t.ticker_as_of_session, t.session_date))::BIGINT AS unique_target_rows,
                COUNT(*) FILTER (WHERE p.population_context_id IS NULL)::BIGINT AS unmatched_population,
                COUNT(*) FILTER (WHERE p.population_membership_state <> 'ELIGIBLE_UNDER_DECLARED_PROXY')::BIGINT AS noneligible,
                COUNT(*) FILTER (
                    WHERE p.instrument_id IS DISTINCT FROM t.instrument_id
                       OR p.ticker_as_of_session IS DISTINCT FROM t.ticker_as_of_session
                       OR p.session_date IS DISTINCT FROM t.session_date
                       OR p.presession_reference_price IS DISTINCT FROM t.presession_reference_price
                       OR p.presession_reference_market_cap_proxy IS DISTINCT FROM t.presession_reference_market_cap_proxy
                )::BIGINT AS field_mismatches,
                COUNT(*) FILTER (WHERE c.session_date IS NULL)::BIGINT AS unmatched_calendar,
                COUNT(*) FILTER (
                    WHERE CAST(ROUND(t.decision_seconds) AS BIGINT)
                          <> date_diff('second', c.open_utc, c.close_utc)
                )::BIGINT AS decision_grid_mismatches
            FROM targets t
            LEFT JOIN candidate p USING (population_context_id)
            LEFT JOIN calendar c ON c.session_date = t.session_date
            """
        ).fetchone()
        target_contract = aggregate_contract(_target_rows(target_path))
        target_scalars = target_contract["metadata_scalars"]
        intervals_path = output_root / "development_target_denominator_intervals.parquet"
        con.execute(
            f"""
            COPY (
                SELECT
                    'DEVELOPMENT' AS split_id,
                    t.block_id,
                    t.target_ordinal,
                    t.population_context_id,
                    t.instrument_id,
                    t.ticker_as_of_session,
                    t.session_date,
                    c.open_utc AS session_open_utc,
                    c.close_utc AS session_close_utc,
                    c.open_utc + INTERVAL 1 SECOND AS first_decision_timestamp_utc,
                    c.close_utc - INTERVAL 1 SECOND AS last_decision_timestamp_utc,
                    CAST(ROUND(t.decision_seconds) AS BIGINT) - 1 AS decision_point_count,
                    t.is_early_close,
                    t.population_membership_state,
                    '{candidate_cfg['sha256']}' AS membership_authority_sha256,
                    '{targets_cfg['sha256']}' AS target_authority_sha256,
                    'instrument_id x session_date x decision_timestamp_utc' AS logical_identity_grain,
                    'open_utc < decision_timestamp_utc < close_utc; integer UTC seconds' AS expansion_rule
                FROM targets t
                INNER JOIN candidate p USING (population_context_id)
                INNER JOIN calendar c ON c.session_date = t.session_date
                ORDER BY t.block_id, t.target_ordinal
            ) TO '{_sql_path(intervals_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """
        )
        interval_metrics = con.execute(
            f"""
            SELECT
                COUNT(*)::BIGINT,
                SUM(decision_point_count)::BIGINT,
                COUNT(*) FILTER (WHERE is_early_close)::BIGINT,
                COUNT(DISTINCT (block_id, instrument_id, ticker_as_of_session, session_date))::BIGINT
            FROM read_parquet('{_sql_path(intervals_path)}')
            """
        ).fetchone()

        split_rows = con.execute(
            "SELECT split_id, population_membership_state, row_count, instrument_count, min_session_date, max_session_date FROM split_state_accounting ORDER BY 1,2"
        ).fetchall()
        con.close()
        split_summary: dict[str, Any] = {}
        for split_id, state, rows, instruments, minimum, maximum in split_rows:
            split_summary.setdefault(split_id, {})[state] = {
                "rows": int(rows),
                "instruments": int(instruments),
                "min_session_date": str(minimum),
                "max_session_date": str(maximum),
            }

        checks = {
            **source_manifest_checks,
            "candidate_row_count_exact": int(totals[0]) == candidate_cfg["expected_rows"],
            "candidate_eligible_count_exact": int(totals[1]) == candidate_cfg["expected_eligible_rows"],
            "population_context_id_unique": int(totals[0]) == int(totals[2]),
            "composite_membership_grain_unique": int(totals[0]) == int(totals[3]),
            "eligible_policy_semantics_exact": int(invalid_eligible) == 0,
            "development_target_count_exact": int(target_metrics[0]) == targets_cfg["expected_target_count"],
            "development_target_identity_unique": int(target_metrics[0]) == int(target_metrics[1]),
            "development_targets_resolve": int(target_metrics[2]) == 0,
            "development_targets_all_eligible": int(target_metrics[3]) == 0,
            "development_target_fields_exact": int(target_metrics[4]) == 0,
            "development_calendar_resolves": int(target_metrics[5]) == 0,
            "development_decision_grid_exact": int(target_metrics[6]) == 0,
            "cardinality_target_count_exact": target_scalars["target_count"] == targets_cfg["expected_target_count"],
            "cardinality_decision_points_exact": target_scalars["decision_points_total"] == targets_cfg["expected_decision_points"],
            "cardinality_early_close_exact": target_scalars["early_close_target_count"] == targets_cfg["expected_early_close_targets"],
            "interval_target_count_exact": int(interval_metrics[0]) == targets_cfg["expected_target_count"],
            "interval_decision_points_exact": int(interval_metrics[1]) == targets_cfg["expected_decision_points"],
            "interval_early_close_exact": int(interval_metrics[2]) == targets_cfg["expected_early_close_targets"],
            "interval_identity_unique": int(interval_metrics[0]) == int(interval_metrics[3]),
        }
        status = "PASS" if all(checks.values()) else "FAIL"
        consumption_manifest = {
            "manifest_id": "daily_eligible_universe_restricted_consumption_manifest_v0_1",
            "schema_version": SCHEMA_VERSION,
            "status": status,
            "promotion_state": "RESTRICTED_EXPERIMENTAL_CONSUMPTION_NOT_CANONICAL",
            "created_at_utc": _now(),
            "selector_owns_membership": True,
            "bindings_recalculate_thresholds": False,
            "daily_membership_authority": {
                "path": str(candidate_path),
                "sha256": candidate_cfg["sha256"],
                "logical_view": "all rows; eligible rows are population_membership_state = ELIGIBLE_UNDER_DECLARED_PROXY",
                "split_state_accounting_path": str(accounting_path),
                "split_state_accounting_sha256": _sha256(accounting_path),
            },
            "split_membership_references": split_summary,
            "development_target_authority": {
                "path": str(target_path),
                "sha256": targets_cfg["sha256"],
                "target_count": target_scalars["target_count"],
            },
            "development_symbol_second_denominator": {
                "encoding": "LOSSLESS_SESSION_INTERVAL_ENCODING",
                "path": str(intervals_path),
                "sha256": _sha256(intervals_path),
                "physical_interval_rows": int(interval_metrics[0]),
                "logical_symbol_second_rows": int(interval_metrics[1]),
                "identity_grain": config["denominator_identity"]["grain"],
                "expansion_rule": config["denominator_identity"]["grid"],
                "flat_materialization": False,
            },
            "checks": checks,
            "restrictions": {
                "canonical_screener": False,
                "exact_historical_market_cap": False,
                "exact_point_shares": False,
                "validation_or_final_oos_targets_created": False,
                "labels_created": False,
                "binding_b_implementation_authorized": False,
            },
        }
        consumption_path = output_root / "consumption_manifest.json"
        _atomic_json(consumption_path, consumption_manifest)
        _heartbeat(
            output_root,
            run_id,
            "COMPLETED" if status == "PASS" else "FAILED",
            "FINAL",
            candidate_rows=int(totals[0]),
            eligible_rows=int(totals[1]),
            targets=int(interval_metrics[0]),
            logical_symbol_seconds=int(interval_metrics[1]),
        )
        final = {
            "run_id": run_id,
            "gate_id": GATE_ID,
            "status": status,
            "started_at_utc": started_at,
            "completed_at_utc": _now(),
            "exit_code": 0 if status == "PASS" else 1,
            "config_path": str(config_path.resolve()),
            "config_sha256": _sha256(config_path),
            "script_path": str(Path(__file__).resolve()),
            "script_sha256": _sha256(Path(__file__).resolve()),
            "consumption_manifest": str(consumption_path),
            "consumption_manifest_sha256": _sha256(consumption_path),
            "split_state_accounting": str(accounting_path),
            "split_state_accounting_sha256": _sha256(accounting_path),
            "development_denominator_intervals": str(intervals_path),
            "development_denominator_intervals_sha256": _sha256(intervals_path),
            "candidate_rows": int(totals[0]),
            "eligible_rows": int(totals[1]),
            "development_targets": int(interval_metrics[0]),
            "logical_symbol_seconds": int(interval_metrics[1]),
            "checks": checks,
            "next_gate": "HUMAN_REVIEW_RESTRICTED_SELECTOR_CONSUMPTION_THEN_D07_NUMERIC_AUTHORITY",
            "promotion_state": "NOT_CANONICAL",
        }
        _atomic_json(final_path, final)
        _log(log_path, f"gate finished status={status}")
        return final
    except Exception as exc:
        _heartbeat(output_root, run_id, "FAILED", "FINAL", error=repr(exc))
        final = {
            "run_id": run_id,
            "gate_id": GATE_ID,
            "status": "FAILED",
            "started_at_utc": started_at,
            "completed_at_utc": _now(),
            "exit_code": 1,
            "error": repr(exc),
            "promotion_state": "NOT_PROMOTED",
        }
        _atomic_json(final_path, final)
        _log(log_path, f"gate failed error={exc!r}")
        raise


def main() -> int:
    args = _parser().parse_args()
    result = build(
        config_path=args.config,
        output_root=args.output_root,
        run_id=args.run_id,
        threads=args.threads,
        memory_limit=args.memory_limit,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
