#!/usr/bin/env python3
"""Build the representation-neutral Wake-up RTH calibration candidate pool."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

from wake_up_rth_core import (
    as_path,
    atomic_json,
    build_session_second_metrics,
    choose_probe_targets,
    discover_candidates,
    load_config,
    load_policy_module,
    load_targets_and_calendar,
    sha256_file,
    utc_now,
    verify_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("preflight", "probe", "full"), default="probe")
    parser.add_argument("--probe-per-cohort", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def write_log(handle, message: str) -> None:
    line = f"[{utc_now()}] {message}"
    print(line, flush=True)
    handle.write(line + "\n")
    handle.flush()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    run_root = as_path(config["outputs"]["run_parent"]) / args.run_id
    run_root.mkdir(parents=True, exist_ok=True)
    log_path = run_root / "live.log"
    heartbeat_path = run_root / "heartbeat_latest.json"
    pre_manifest_path = run_root / "pre_manifest.json"
    final_manifest_path = run_root / "final_manifest.json"
    shard_root = run_root / "candidate_shards"
    metric_root = run_root / "session_metrics"
    shard_root.mkdir(exist_ok=True)
    metric_root.mkdir(exist_ok=True)

    config_sha = sha256_file(args.config)
    all_contexts = load_targets_and_calendar(config)
    contexts = all_contexts
    if args.mode == "probe":
        contexts = choose_probe_targets(contexts, args.probe_per_cohort)
    elif args.mode == "preflight":
        contexts = contexts[:0]
    elif args.mode == "full" and len(contexts) != 2400:
        raise ValueError(f"Full run requires exact 2,400 targets, found {len(contexts)}")

    pre_manifest = {
        "run_id": args.run_id,
        "status": "PREFLIGHT_PASS",
        "mode": args.mode,
        "created_at_utc": utc_now(),
        "pid": os.getpid(),
        "config_path": str(args.config.resolve()),
        "config_sha256": config_sha,
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__)),
        "core_script_sha256": sha256_file(Path(__file__).with_name("wake_up_rth_core.py")),
        "governed_target_count": len(all_contexts),
        "processing_target_count": len(contexts),
        "decision_grid_authority": "CALENDAR_OPEN_PLUS_1_THROUGH_CLOSE_MINUS_1",
        "legacy_manifest_cardinality_discrepancy_targets": sum(
            context.manifest_declared_decision_seconds
            != context.expected_decision_seconds
            for context in all_contexts
        ),
        "resume": args.resume,
        "network_access": "PROHIBITED_AND_NOT_USED",
        "binding_a_consumed": False,
        "binding_b_consumed": False,
        "intraday_price_path_consumed": False,
        "trade_price_consumption": "ELIGIBLE_TRADE_PRICE_TIMES_SIZE_FOR_DOLLAR_NOTIONAL_ONLY",
        "dollar_volume_used_for_candidate_reduction": True,
    }
    if pre_manifest_path.exists():
        old = json.loads(pre_manifest_path.read_text(encoding="utf-8"))
        current_script_sha = sha256_file(Path(__file__))
        current_core_sha = sha256_file(Path(__file__).with_name("wake_up_rth_core.py"))
        if (
            old.get("config_sha256") != config_sha
            or old.get("mode") != args.mode
            or old.get("script_sha256") != current_script_sha
            or old.get("core_script_sha256") != current_core_sha
        ):
            raise ValueError(
                "Resume/run-root cannot mix config, mode or code versions"
            )
        if not args.resume:
            raise FileExistsError(f"Run already exists; use --resume: {run_root}")
        pre_manifest = old
    else:
        atomic_json(pre_manifest_path, pre_manifest)
    if args.mode == "preflight":
        atomic_json(
            final_manifest_path,
            {**pre_manifest, "status": "COMPLETE_PREFLIGHT_ONLY", "completed_at_utc": utc_now()},
        )
        print(run_root)
        return 0

    sources = config["sources"]
    policy_script = as_path(sources["data_foundation_scripts"]) / "evaluate_trading_activity_trade_eligibility.py"
    matrix_path = as_path(sources["condition_policy_matrix"])
    verify_file(policy_script, sources.get("trade_eligibility_helper_sha256"), "policy helper")
    verify_file(matrix_path, sources.get("condition_policy_matrix_sha256"), "condition matrix")
    policy_module = load_policy_module(policy_script)
    condition_matrix = policy_module.load_condition_matrix(matrix_path)
    raw_root = as_path(sources["raw_trade_root"])
    discovery = config["discovery"]
    started = time.time()
    audits: list[dict] = []
    failures: list[dict] = []

    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        write_log(log, f"START mode={args.mode} targets={len(contexts)} run_root={run_root}")
        for ordinal, context in enumerate(contexts, start=1):
            shard_path = shard_root / f"{context.target_file_key}.parquet"
            metrics_path = metric_root / f"{context.target_file_key}.parquet"
            if args.resume and shard_path.exists() and metrics_path.exists():
                resumed_metrics = pd.read_parquet(
                    metrics_path, columns=["target_file_key", "source_state"]
                )
                if (
                    len(resumed_metrics) != context.expected_decision_seconds
                    or resumed_metrics["target_file_key"].nunique() != 1
                    or str(resumed_metrics["target_file_key"].iloc[0])
                    != context.target_file_key
                ):
                    raise ValueError(
                        f"Resume partition validation failed: {metrics_path}"
                    )
                write_log(log, f"RESUME_SKIP {ordinal}/{len(contexts)} {context.ticker}:{context.session_date}")
                continue
            heartbeat = {
                "run_id": args.run_id,
                "status": "RUNNING",
                "stage": "CANDIDATE_SEARCH",
                "pid": os.getpid(),
                "updated_at_utc": utc_now(),
                "target_progress": f"{ordinal - 1}/{len(contexts)}",
                "target_ordinal": context.target_ordinal,
                "ticker": context.ticker,
                "session_date": context.session_date,
                "elapsed_seconds": round(time.time() - started, 3),
            }
            atomic_json(heartbeat_path, heartbeat)
            try:
                metrics, audit, _ = build_session_second_metrics(
                    context,
                    raw_root,
                    policy_module,
                    condition_matrix,
                    int(config["scope"]["simulated_latency_ms"]),
                )
                candidates = discover_candidates(
                    metrics,
                    [int(x) for x in discovery["dormancy_seconds"]],
                    [int(x) for x in discovery["confirmation_seconds"]],
                    int(discovery["minimum_confirmation_trade_count_for_candidate_reduction"]),
                    int(discovery["minimum_confirmation_cluster_count_for_candidate_reduction"]),
                    int(discovery["top_per_window_pair"]),
                    int(discovery["maximum_candidates_per_session"]),
                    int(discovery["candidate_merge_gap_seconds"]),
                )
                metrics.to_parquet(metrics_path, index=False)
                candidates.to_parquet(shard_path, index=False)
                audit["candidate_count"] = len(candidates)
                audits.append(audit)
                write_log(
                    log,
                    f"TARGET_PASS {ordinal}/{len(contexts)} {context.ticker}:{context.session_date} "
                    f"source={audit['source_state']} candidates={len(candidates)}",
                )
            except Exception as exc:  # terminal manifest must preserve every failure
                failure = {
                    "target_ordinal": context.target_ordinal,
                    "ticker": context.ticker,
                    "session_date": context.session_date,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
                failures.append(failure)
                write_log(log, f"TARGET_FAIL {ordinal}/{len(contexts)} {failure}")
                break

        shard_paths = sorted(shard_root.glob("target_*.parquet"))
        metric_paths = sorted(metric_root.glob("target_*.parquet"))
        candidate_frames = [pd.read_parquet(path) for path in shard_paths]
        audit_frame = pd.DataFrame(audits)
        candidate_pool = (
            pd.concat(candidate_frames, ignore_index=True)
            if candidate_frames
            else pd.DataFrame()
        )
        candidate_pool.to_parquet(run_root / "candidate_pool.parquet", index=False)
        audit_frame.to_parquet(run_root / "source_and_session_audit.parquet", index=False)
        status = "COMPLETE" if not failures and len(metric_paths) == len(contexts) else "FAILED"
        final = {
            **pre_manifest,
            "status": status,
            "completed_at_utc": utc_now(),
            "elapsed_seconds": round(time.time() - started, 3),
            "completed_targets": len(metric_paths),
            "expected_targets": len(contexts),
            "candidate_count": len(candidate_pool),
            "source_unavailable_targets": int(
                (audit_frame.get("source_state", pd.Series(dtype=str)) == "UNAVAILABLE_SOURCE_FILE").sum()
            ),
            "failure_count": len(failures),
            "failures": failures,
            "outputs": {
                "candidate_pool": str(run_root / "candidate_pool.parquet"),
                "source_and_session_audit": str(run_root / "source_and_session_audit.parquet"),
                "session_metrics": str(metric_root),
            },
        }
        atomic_json(final_manifest_path, final)
        atomic_json(
            heartbeat_path,
            {
                "run_id": args.run_id,
                "status": status,
                "stage": "FINAL",
                "pid": os.getpid(),
                "updated_at_utc": utc_now(),
                "target_progress": f"{len(metric_paths)}/{len(contexts)}",
                "elapsed_seconds": round(time.time() - started, 3),
            },
        )
        write_log(log, f"FINAL status={status} targets={len(metric_paths)}/{len(contexts)}")
    print(run_root)
    return 0 if status == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
