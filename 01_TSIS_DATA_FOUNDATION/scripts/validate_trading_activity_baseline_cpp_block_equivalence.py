"""Fail-closed block equivalence gate for the Trading Activity Stage-8 C++ kernel.

The preserved Python materialization is the frozen oracle.  For every block and
evaluation session in a versioned plan, this script rematerializes Stage 8 with
the candidate C++ kernel, writes the new partition separately, and compares the
entire output contract: row count/order, column names/order, dtypes, null masks,
values, and the serialized Parquet hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from trading_activity_binding_a_baseline_cpp import materialize_baseline_and_surprise_cpp

BASELINE_INPUT_COLUMNS = [
    "session_date",
    "decision_timestamp",
    "window_seconds",
    "calculation_state",
    "eligible_trade_count",
    "eligible_share_volume",
    "eligible_dollar_volume",
    "trade_arrival_rate",
    "median_intertrade_duration_us",
    "feature_input_max_available_at",
]
DEFAULT_RTOL = 1e-12
DEFAULT_ATOL = 1e-12


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def append_log(path: Path, event: str, **fields: Any) -> None:
    payload = {"observed_at_utc": utc_now(), "event": event, **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()


def compare_frames(
    expected: pd.DataFrame,
    actual: pd.DataFrame,
    *,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> dict[str, Any]:
    expected_columns = list(expected.columns)
    actual_columns = list(actual.columns)
    result: dict[str, Any] = {
        "expected_rows": len(expected),
        "actual_rows": len(actual),
        "column_order_exact": expected_columns == actual_columns,
        "expected_columns": expected_columns,
        "actual_columns": actual_columns,
        "rtol": rtol,
        "atol": atol,
        "dtype_mismatches": {},
        "column_results": {},
    }
    if expected_columns != actual_columns or len(expected) != len(actual):
        result["status"] = "FAIL"
        result["contract_mismatch_count"] = None
        return result

    total_contract_mismatches = 0
    total_exact_mismatches = 0
    for column in expected_columns:
        left = expected[column]
        right = actual[column]
        if str(left.dtype) != str(right.dtype):
            result["dtype_mismatches"][column] = {
                "expected": str(left.dtype),
                "actual": str(right.dtype),
            }

        left_na = left.isna().to_numpy()
        right_na = right.isna().to_numpy()
        null_mask_mismatches = int(np.count_nonzero(left_na != right_na))
        valid = ~(left_na | right_na)
        contract_mismatches = null_mask_mismatches
        exact_mismatches = null_mask_mismatches
        max_absolute_difference: float | None = None

        if valid.any():
            if is_numeric_dtype(left.dtype) and is_numeric_dtype(right.dtype):
                left_values = pd.to_numeric(left[valid], errors="raise").to_numpy(dtype=np.float64)
                right_values = pd.to_numeric(right[valid], errors="raise").to_numpy(dtype=np.float64)
                close = np.isclose(left_values, right_values, rtol=rtol, atol=atol, equal_nan=False)
                exact = left_values == right_values
                contract_mismatches += int(np.count_nonzero(~close))
                exact_mismatches += int(np.count_nonzero(~exact))
                if len(left_values):
                    max_absolute_difference = float(np.max(np.abs(left_values - right_values)))
            else:
                equal = left[valid].reset_index(drop=True).eq(
                    right[valid].reset_index(drop=True)
                ).fillna(False).to_numpy(dtype=bool)
                mismatches = int(np.count_nonzero(~equal))
                contract_mismatches += mismatches
                exact_mismatches += mismatches

        total_contract_mismatches += contract_mismatches
        total_exact_mismatches += exact_mismatches
        result["column_results"][column] = {
            "null_mask_mismatches": null_mask_mismatches,
            "contract_value_mismatches": contract_mismatches,
            "exact_value_mismatches": exact_mismatches,
            "max_absolute_difference": max_absolute_difference,
        }

    result["contract_mismatch_count"] = total_contract_mismatches
    result["exact_mismatch_count"] = total_exact_mismatches
    result["all_dtypes_exact"] = not result["dtype_mismatches"]
    result["status"] = (
        "PASS"
        if not result["dtype_mismatches"] and total_contract_mismatches == 0
        else "FAIL"
    )
    return result


def _native_module_path() -> Path:
    build = Path(__file__).parents[1] / "native" / "trading_activity" / "build"
    candidates = list(build.glob("tsis_baseline_native_cpp*.pyd"))
    if len(candidates) != 1:
        raise RuntimeError(f"expected one C++ module, found {len(candidates)}")
    return candidates[0]


def _session_from_partition(path: Path) -> str:
    for parent in path.parents:
        if parent.name.startswith("session_date="):
            return parent.name.split("=", 1)[1]
    raise ValueError(f"session_date partition not found in {path}")


def _ticker_from_partition(path: Path) -> str:
    for parent in path.parents:
        if parent.name.startswith("ticker="):
            return parent.name.split("=", 1)[1]
    raise ValueError(f"ticker partition not found in {path}")


def _resolve_block_paths(plan: dict[str, Any], block: dict[str, Any]) -> tuple[Path, Path]:
    if "python_run_root" in block and "config_path" in block:
        return Path(block["python_run_root"]), Path(block["config_path"])
    binding_root = Path(plan["binding_root"])
    operation_id = block["operation_id"]
    block_id = block["block_id"]
    run_id = f"{operation_id}__{block_id}"
    return (
        binding_root / "runs" / f"run_id={run_id}",
        binding_root / "operations" / operation_id / "block_configs" / f"{block_id}.json",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    args = parser.parse_args()

    if args.runtime_root.exists():
        raise FileExistsError(f"runtime root already exists; overwrite is prohibited: {args.runtime_root}")
    args.runtime_root.mkdir(parents=True)
    output_root = args.runtime_root / "cpp_blocks"
    output_root.mkdir()
    log_path = args.runtime_root / "equivalence.live.jsonl"
    heartbeat_path = args.runtime_root / "equivalence.heartbeat.json"
    final_path = args.runtime_root / "equivalence.final_manifest.json"

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if plan.get("plan_version") != "trading_activity_stage8_cpp_block_equivalence_v0_1":
        raise ValueError("unsupported or missing plan_version")
    if plan.get("python_oracle") != "FROZEN_PYTHON_REFERENCE_MATERIALIZATION":
        raise ValueError("plan must declare the frozen Python materialization as oracle")
    rtol = float(plan.get("rtol", DEFAULT_RTOL))
    atol = float(plan.get("atol", DEFAULT_ATOL))
    require_exact = bool(plan.get("require_exact_value_match", True))
    require_hash = bool(plan.get("require_parquet_hash_match", True))
    native_path = _native_module_path()
    source_paths = [
        Path(__file__),
        Path(__file__).with_name("trading_activity_binding_a_baseline_cpp.py"),
        Path(__file__).parents[1] / "native" / "trading_activity" / "tsis_baseline_native_cpp.cpp",
    ]
    pre_manifest = {
        "operation": "trading_activity_stage8_cpp_block_equivalence",
        "status": "PREPARED",
        "created_at_utc": utc_now(),
        "plan_path": str(args.plan.resolve()),
        "plan_sha256": sha256(args.plan),
        "runtime_root": str(args.runtime_root.resolve()),
        "pre_manifest_path": str((args.runtime_root / "equivalence.pre_manifest.json").resolve()),
        "pid_manifest_path": str((args.runtime_root / "equivalence.pid_manifest.json").resolve()),
        "heartbeat_path": str(heartbeat_path.resolve()),
        "live_log_path": str(log_path.resolve()),
        "final_manifest_path": str(final_path.resolve()),
        "checkpoint_granularity": "ONE_EVALUATION_SESSION",
        "resume_policy": "PROHIBITED_START_NEW_RUNTIME_ROOT_AFTER_INTERRUPTION",
        "python_oracle": plan["python_oracle"],
        "rtol": rtol,
        "atol": atol,
        "require_exact_value_match": require_exact,
        "require_parquet_hash_match": require_hash,
        "block_count": len(plan.get("blocks", [])),
        "native_module": str(native_path.resolve()),
        "native_module_sha256": sha256(native_path),
        "source_sha256": {str(path.resolve()): sha256(path) for path in source_paths},
        "promotion_status": "NOT_AUTHORIZED",
        "broad_materialization_authorized": False,
    }
    write_json(args.runtime_root / "equivalence.pre_manifest.json", pre_manifest)
    write_json(
        args.runtime_root / "equivalence.pid_manifest.json",
        {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "started_at_utc": utc_now(),
            "command": sys.argv,
        },
    )

    results: list[dict[str, Any]] = []
    total_sessions = 0
    complete_block_count = sum(1 for block in plan["blocks"] if not block.get("session_dates"))
    targeted_session_count = sum(len(block.get("session_dates", [])) for block in plan["blocks"])
    for block in plan["blocks"]:
        run_root, _ = _resolve_block_paths(plan, block)
        requested = block.get("session_dates")
        total_sessions += len(requested) if requested else len(
            list((run_root / "pit_baseline_and_surprise").rglob("part-*.parquet"))
        )
    expected_total = plan.get("expected_total_session_partitions")
    if expected_total is not None and total_sessions != int(expected_total):
        raise ValueError(f"plan expected {expected_total} sessions, resolved {total_sessions}")
    expected_complete_blocks = plan.get("expected_complete_block_count")
    if expected_complete_blocks is not None and complete_block_count != int(expected_complete_blocks):
        raise ValueError(
            f"plan expected {expected_complete_blocks} complete blocks, resolved {complete_block_count}"
        )
    expected_targeted = plan.get("expected_targeted_session_count")
    if expected_targeted is not None and targeted_session_count != int(expected_targeted):
        raise ValueError(
            f"plan expected {expected_targeted} targeted sessions, resolved {targeted_session_count}"
        )
    completed_sessions = 0

    def heartbeat(status: str, **fields: Any) -> None:
        write_json(
            heartbeat_path,
            {
                "status": status,
                "observed_at_utc": utc_now(),
                "pid": os.getpid(),
                "completed_sessions": completed_sessions,
                "total_sessions": total_sessions,
                **fields,
            },
        )

    heartbeat("RUNNING", stage="load_plan")
    started = time.perf_counter()
    try:
        for block_index, block in enumerate(plan["blocks"], start=1):
            run_root, config_path = _resolve_block_paths(plan, block)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            run_id = run_root.name.removeprefix("run_id=")
            expected_ticker = block.get("ticker")
            configured_ticker = config.get("scope", {}).get("ticker")
            if expected_ticker is not None and configured_ticker != expected_ticker:
                raise ValueError(
                    f"ticker mismatch for {run_id}: plan={expected_ticker}, config={configured_ticker}"
                )
            current_paths = sorted((run_root / "current_state").rglob("part-*.parquet"))
            current_by_session = {_session_from_partition(path): path for path in current_paths}
            oracle_paths = sorted((run_root / "pit_baseline_and_surprise").rglob("part-*.parquet"))
            oracle_by_session = {_session_from_partition(path): path for path in oracle_paths}
            requested_sessions = block.get("session_dates") or sorted(oracle_by_session)
            if not requested_sessions:
                raise ValueError(f"no Python oracle sessions found for {run_id}")
            expected_sessions = block.get("expected_session_count")
            if expected_sessions is not None and len(requested_sessions) != int(expected_sessions):
                raise ValueError(
                    f"session count mismatch for {run_id}: plan={expected_sessions}, resolved={len(requested_sessions)}"
                )
            missing = [session for session in requested_sessions if session not in current_by_session or session not in oracle_by_session]
            if missing:
                raise ValueError(f"missing current/oracle partitions for {run_id}: {missing}")

            heartbeat("RUNNING", stage="load_current_state", block_run_id=run_id)
            prior = pd.concat(
                [pd.read_parquet(path, columns=BASELINE_INPUT_COLUMNS) for path in current_paths],
                ignore_index=True,
            )
            block_results: list[dict[str, Any]] = []
            for session in requested_sessions:
                heartbeat("RUNNING", stage="cpp_materialization", block_run_id=run_id, session_date=session)
                current = pd.read_parquet(current_by_session[session])
                kernel_started = time.perf_counter()
                actual = materialize_baseline_and_surprise_cpp(
                    current,
                    prior_current=prior,
                    config=config,
                    evaluation_session_date=pd.Timestamp(session).date(),
                )
                kernel_seconds = time.perf_counter() - kernel_started
                expected = pd.read_parquet(oracle_by_session[session])
                comparison = compare_frames(expected, actual, rtol=rtol, atol=atol)

                ticker = _ticker_from_partition(oracle_by_session[session])
                compact_block_id = run_id.rsplit("__", 1)[-1]
                target = output_root / compact_block_id / ticker / f"{session}.parquet"
                target.parent.mkdir(parents=True, exist_ok=True)
                actual.to_parquet(target, index=False, compression="zstd")
                oracle_hash = sha256(oracle_by_session[session])
                cpp_hash = sha256(target)
                hash_match = oracle_hash == cpp_hash
                exact_match = comparison.get("exact_mismatch_count") == 0
                status = (
                    "PASS"
                    if comparison["status"] == "PASS"
                    and (exact_match or not require_exact)
                    and (hash_match or not require_hash)
                    else "FAIL"
                )
                session_result = {
                    "status": status,
                    "block_run_id": run_id,
                    "block_index": block_index,
                    "session_date": session,
                    "ticker": ticker,
                    "kernel_seconds": kernel_seconds,
                    "python_oracle_path": str(oracle_by_session[session]),
                    "cpp_output_path": str(target),
                    "python_oracle_sha256": oracle_hash,
                    "cpp_output_sha256": cpp_hash,
                    "parquet_hash_exact": hash_match,
                    "exact_value_match": exact_match,
                    "comparison": comparison,
                }
                block_results.append(session_result)
                completed_sessions += 1
                write_json(target.parent / "equivalence_readout.json", session_result)
                append_log(log_path, "session_compared", **{key: session_result[key] for key in ("status", "block_run_id", "session_date", "ticker", "kernel_seconds", "parquet_hash_exact")})
                heartbeat("RUNNING", stage="session_complete", block_run_id=run_id, session_date=session, latest_status=status)

            block_status = "PASS" if all(item["status"] == "PASS" for item in block_results) else "FAIL"
            block_result = {
                "status": block_status,
                "block_run_id": run_id,
                "config_path": str(config_path),
                "config_sha256": sha256(config_path),
                "current_partition_count": len(current_paths),
                "session_count": len(block_results),
                "sessions": block_results,
            }
            results.append(block_result)
            compact_block_id = run_id.rsplit("__", 1)[-1]
            write_json(output_root / compact_block_id / "block_equivalence_readout.json", block_result)

        final_status = "PASS" if results and all(item["status"] == "PASS" for item in results) else "FAIL"
        final = {
            **pre_manifest,
            "status": final_status,
            "finished_at_utc": utc_now(),
            "elapsed_seconds": time.perf_counter() - started,
            "completed_blocks": len(results),
            "completed_sessions": completed_sessions,
            "results": results,
            "promotion_status": "NOT_AUTHORIZED",
            "broad_materialization_authorized": False,
        }
        write_json(final_path, final)
        heartbeat(final_status, stage="final_manifest_written", final_manifest=str(final_path))
        print(json.dumps({"status": final_status, "final_manifest": str(final_path)}, indent=2))
        if final_status != "PASS":
            raise SystemExit(1)
    except BaseException as exc:
        if not final_path.exists():
            write_json(
                final_path,
                {
                    **pre_manifest,
                    "status": "FAIL",
                    "finished_at_utc": utc_now(),
                    "elapsed_seconds": time.perf_counter() - started,
                    "completed_blocks": len(results),
                    "completed_sessions": completed_sessions,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "results": results,
                },
            )
            heartbeat("FAIL", stage="exception", error_type=type(exc).__name__, error=str(exc))
        raise


if __name__ == "__main__":
    main()
