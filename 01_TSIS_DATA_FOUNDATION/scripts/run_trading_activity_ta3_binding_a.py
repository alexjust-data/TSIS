"""Orchestrate frozen TA-3 blocks through the validated Binding A runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from trading_activity_binding_a_baseline_engine import resolve_stage8_engine

RUNNER = Path(__file__).with_name("run_trading_activity_binding_a_multisession_pilot.py")
OFFICIAL_TRADE_ROOT = "G:/TSIS/data/trades_ticks_prod_2005_2026"
OFFICIAL_REPRESENTATION_ROOT = Path("D:/TSIS/IO")


def require_representation_root(path: Path, label: str) -> Path:
    resolved = path.resolve()
    root = OFFICIAL_REPRESENTATION_ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"{label} must be under {root}: {resolved}")
    return resolved


def utc_text() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-manifest", required=True, type=Path)
    parser.add_argument("--base-config", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--pointer-root", required=True, type=Path)
    parser.add_argument("--block-limit", type=int)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--decision-seconds-limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--stage8-engine", choices=("python", "cpp"), default="python")
    parser.add_argument("--expected-stage8-engine-fingerprint")
    return parser.parse_args()


def block_resume_state(
    output_root: Path, runtime_root: Path, block_run_id: str
) -> str:
    output_run_root = output_root / f"run_id={block_run_id}"
    runtime_run_root = runtime_root / block_run_id
    final_path = runtime_run_root / "final_manifest.json"
    if final_path.is_file():
        final = json.loads(final_path.read_text(encoding="utf-8-sig"))
        if final.get("status") == "COMPLETE":
            return "COMPLETE"
    if output_run_root.exists():
        return "PARTIAL"
    return "NEW"

def load_and_verify_sample(path: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "trading_activity_ta3_sample_manifest_v0_2":
        raise ValueError("TA-3 sample manifest v0_2 is required")
    if manifest.get("official_trade_source_root") != OFFICIAL_TRADE_ROOT:
        raise ValueError("TA-3 official trade root is not the governed G root")
    if manifest.get("legacy_root_fallback") != "PROHIBITED":
        raise ValueError("Legacy source fallback must be prohibited")
    if manifest.get("promotion_state") != "FROZEN_EXPERIMENTAL_SAMPLE_NOT_CANONICAL":
        raise ValueError("TA-3 sample is not frozen for experimental use")

    required = {
        "blocks": "selected_blocks",
        "targets": "selected_targets",
        "scope": "selected_scope_sessions",
    }
    paths: dict[str, Path] = {}
    for key, output_name in required.items():
        binding = manifest["outputs"][output_name]
        candidate = Path(binding["path"])
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        if sha256_file(candidate) != binding["sha256"]:
            raise ValueError(f"TA-3 {key} hash mismatch: {candidate}")
        paths[key] = candidate
    return manifest, paths


def build_block_config(
    base: dict[str, Any], block: pd.Series, scope: pd.DataFrame
) -> dict[str, Any]:
    config = json.loads(json.dumps(base))
    dates = pd.to_datetime(scope["session_date"]).dt.date.sort_values().tolist()
    targets = scope.loc[scope["scope_role"] == "TARGET"].copy()
    warmup = scope.loc[scope["scope_role"] == "WARMUP"].copy()
    target_dates = pd.to_datetime(targets["session_date"]).dt.date.sort_values().tolist()
    if not dates or not target_dates:
        raise ValueError(f"Block has no scope or target dates: {block['block_id']}")
    config["config_id"] = "trading_activity_ta3_binding_a_block_v0_2"
    config["scope"].update(
        {
            "scope_id": "legacy_rth_reconciled_event_time_research_only",
            "pilot_scope_id": str(block["block_id"]),
            "ticker": str(block["ticker_as_of_session"]),
            "instrument_id": str(block["instrument_id"]),
            "session_start": dates[0].isoformat(),
            "session_end": dates[-1].isoformat(),
            "expected_session_count": len(dates),
            "warmup_end": (
                pd.to_datetime(warmup["session_date"]).dt.date.max().isoformat()
                if not warmup.empty
                else target_dates[0].isoformat()
            ),
            "evaluation_start": target_dates[0].isoformat(),
            "evaluation_end": target_dates[-1].isoformat(),
            "expected_evaluation_session_count": len(target_dates),
        }
    )
    config["sources"]["raw_trade_root"] = OFFICIAL_TRADE_ROOT
    config["outputs"]["overwrite_policy"] = "NEVER"
    config["outputs"]["resume_policy"] = "RESUME_HASH_VALIDATED_COMPLETE_PARTITIONS"
    return config


def main() -> int:
    args = parse_args()
    args.output_root = require_representation_root(args.output_root, "output-root")
    args.runtime_root = require_representation_root(args.runtime_root, "runtime-root")
    args.pointer_root = require_representation_root(args.pointer_root, "pointer-root")
    sample_manifest, paths = load_and_verify_sample(args.sample_manifest.resolve())
    base_config = json.loads(args.base_config.read_text(encoding="utf-8"))
    stage8_engine = resolve_stage8_engine(args.stage8_engine)
    if (
        args.expected_stage8_engine_fingerprint
        and stage8_engine.manifest["engine_fingerprint_sha256"]
        != args.expected_stage8_engine_fingerprint
    ):
        raise ValueError("Resolved Stage-8 engine fingerprint differs from expected")
    if base_config["sources"]["raw_trade_root"] != OFFICIAL_TRADE_ROOT:
        raise ValueError("Base config does not use the governed G trade root")

    blocks = pd.read_parquet(paths["blocks"]).sort_values(
        ["cohort_id", "selected_rank_in_cohort"]
    )
    scope = pd.read_parquet(paths["scope"])
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        raise ValueError("shard-index must be in [0, shard-count)")
    blocks = blocks.iloc[args.shard_index :: args.shard_count].copy()
    if args.block_limit is not None:
        blocks = blocks.head(args.block_limit).copy()
    if blocks.empty:
        raise ValueError("No TA-3 blocks selected")

    run_root = args.runtime_root.resolve() / args.run_id
    config_root = run_root / "block_configs"
    run_root.mkdir(parents=True, exist_ok=True)
    config_root.mkdir(parents=True, exist_ok=True)
    premanifest = {
        "operation": "trading_activity_ta3_binding_a",
        "run_id": args.run_id,
        "created_at_utc": utc_text(),
        "sample_manifest": str(args.sample_manifest.resolve()),
        "sample_manifest_sha256": sha256_file(args.sample_manifest.resolve()),
        "base_config": str(args.base_config.resolve()),
        "base_config_sha256": sha256_file(args.base_config.resolve()),
        "official_trade_source_root": OFFICIAL_TRADE_ROOT,
        "legacy_root_fallback": "PROHIBITED",
        "block_count": int(len(blocks)),
        "block_limit": args.block_limit,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "decision_seconds_limit": args.decision_seconds_limit,
        "stage8_engine": stage8_engine.manifest,
        "expected_stage8_engine_fingerprint": args.expected_stage8_engine_fingerprint,
        "projected_binding_a_rows": sample_manifest["summary"]["expected_binding_a_rows"]["total"],
        "promotion_status": "NOT_AUTHORIZED",
    }
    atomic_json(run_root / "pre_manifest.json", premanifest)
    atomic_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "active_pid": None,
            "created_at_utc": utc_text(),
        },
    )

    completed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    for ordinal, block in enumerate(blocks.itertuples(index=False), start=1):
        block_id = str(block.block_id)
        block_scope = scope.loc[scope["block_id"] == block_id].copy()
        config = build_block_config(base_config, pd.Series(block._asdict()), block_scope)
        block_key = block_id.split(":", 1)[-1]
        config_path = config_root / f"{block_key}.json"
        atomic_json(config_path, config)
        block_run_id = f"{args.run_id}__{block_key}"
        resume_state = block_resume_state(
            args.output_root.resolve(), run_root / "blocks", block_run_id
        )
        if args.resume and resume_state == "COMPLETE":
            completed.append(
                {
                    "block_id": block_id,
                    "block_run_id": block_run_id,
                    "ordinal": ordinal,
                    "return_code": 0,
                    "resume_state": "SKIPPED_COMPLETE",
                }
            )
            continue
        command = [
            sys.executable,
            str(RUNNER),
            "--config",
            str(config_path),
            "--run-id",
            block_run_id,
            "--output-root",
            str(args.output_root.resolve()),
            "--runtime-root",
            str(run_root / "blocks"),
            "--pointer-root",
            str(args.pointer_root.resolve()),
            "--stage8-engine",
            args.stage8_engine,
        ]
        if args.expected_stage8_engine_fingerprint:
            command.extend(
                [
                    "--expected-stage8-engine-fingerprint",
                    args.expected_stage8_engine_fingerprint,
                ]
            )
        if args.decision_seconds_limit is not None:
            command.extend(["--decision-seconds-limit", str(args.decision_seconds_limit)])
        if args.resume and resume_state == "PARTIAL":
            command.append("--resume")
        log_root = run_root / "block_logs"
        log_root.mkdir(parents=True, exist_ok=True)
        stdout_handle = (log_root / f"{block_key}.stdout.log").open(
            "a", encoding="utf-8"
        )
        stderr_handle = (log_root / f"{block_key}.stderr.log").open(
            "a", encoding="utf-8"
        )
        process = subprocess.Popen(
            command, stdout=stdout_handle, stderr=stderr_handle
        )
        while process.poll() is None:
            heartbeat = {
                "run_id": args.run_id,
                "status": "RUNNING",
                "stage": "BLOCK_EXECUTION",
                "observed_at_utc": utc_text(),
                "current_index": ordinal - 1,
                "total_count": int(len(blocks)),
                "item": block_id,
                "completed_blocks": len(completed),
                "failed_blocks": len(failed),
                "wrapper_pid": os.getpid(),
                "active_pid": process.pid,
            }
            atomic_json(run_root / "heartbeat_latest.json", heartbeat)
            with (run_root / "heartbeat_history.jsonl").open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write(json.dumps(heartbeat) + "\n")
            atomic_json(
                run_root / "pid_manifest.json",
                {
                    "run_id": args.run_id,
                    "wrapper_pid": os.getpid(),
                    "active_pid": process.pid,
                    "block_id": block_id,
                    "observed_at_utc": utc_text(),
                },
            )
            time.sleep(30)
        return_code = int(process.returncode or 0)
        stdout_handle.close()
        stderr_handle.close()
        record = {
            "block_id": block_id,
            "block_run_id": block_run_id,
            "ordinal": ordinal,
            "return_code": return_code,
        }
        (completed if return_code == 0 else failed).append(record)
        atomic_json(
            run_root / "heartbeat_latest.json",
            {
                "run_id": args.run_id,
                "status": "RUNNING",
                "stage": "BLOCK_EXECUTION",
                "observed_at_utc": utc_text(),
                "current_index": ordinal,
                "total_count": int(len(blocks)),
                "item": block_id,
                "completed_blocks": len(completed),
                "failed_blocks": len(failed),
            },
        )
        if return_code != 0:
            break

    status = "COMPLETE" if not failed and len(completed) == len(blocks) else "FAILED"
    final = {
        **premanifest,
        "final_status": status,
        "completed_at_utc": utc_text(),
        "completed_blocks": completed,
        "failed_blocks": failed,
    }
    atomic_json(run_root / "final_manifest.json", final)
    atomic_json(
        run_root / "heartbeat_latest.json",
        {
            "run_id": args.run_id,
            "status": status,
            "stage": "FINAL",
            "observed_at_utc": utc_text(),
            "current_index": len(completed) + len(failed),
            "total_count": int(len(blocks)),
            "completed_blocks": len(completed),
            "failed_blocks": len(failed),
        },
    )
    return 0 if status == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

