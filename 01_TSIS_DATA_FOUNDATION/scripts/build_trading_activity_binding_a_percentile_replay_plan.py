"""Freeze PROBE and non-runnable FULL scope for independent percentile replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from trading_activity_binding_a_percentile_replay_oracle import (
    CANDIDATES,
    LOOKBACKS,
    MINIMUM_SESSIONS,
    PERCENTILE_COLUMNS,
)


SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
ORACLE_PATH = SCRIPT_DIR / "trading_activity_binding_a_percentile_replay_oracle.py"
RUNNER_PATH = SCRIPT_DIR / "run_trading_activity_binding_a_percentile_replay.py"
MONITOR_PATH = SCRIPT_DIR / "monitor_trading_activity_binding_a_percentile_replay.ps1"
AUTHORIZER_PATH = SCRIPT_DIR / "authorize_trading_activity_binding_a_percentile_replay_full.py"
SPEC_PATH = Path(
    r"C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\VARIABLES_FEATURES\TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md"
)
PLAN_SCHEMA = "trading_activity_binding_a_percentile_replay_plan_v0_1"


def utc_text() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, path)


def output_root_from_partition(path: Path, family: str) -> Path:
    parts = list(path.parts)
    indexes = [index for index, item in enumerate(parts) if item == family]
    if len(indexes) != 1:
        raise ValueError(f"Cannot resolve unique {family} root from {path}")
    return Path(*parts[: indexes[0]])


def family_from_path(path: str) -> str | None:
    parts = Path(path).parts
    for family in ("current_state", "pit_baseline_and_surprise"):
        if family in parts:
            return family
    return None


def build_block_records(reference_manifest: Path) -> list[dict[str, Any]]:
    columns = [
        "block_id", "block_run_id", "shard_index", "target_ordinal",
        "instrument_id", "ticker", "session_date", "is_early_close",
        "family", "source_path", "source_bytes", "actual_sha256",
        "actual_rows", "block_final_manifest", "block_final_sha256",
        "source_engine_fingerprint",
    ]
    rows = pq.read_table(reference_manifest, columns=columns).to_pylist()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["block_id"])].append(row)
    blocks: list[dict[str, Any]] = []
    for block_id, items in sorted(grouped.items()):
        current = {str(item["session_date"]): item for item in items if item["family"] == "current_state"}
        baseline = {str(item["session_date"]): item for item in items if item["family"] == "pit_baseline_and_surprise"}
        if set(current) != set(baseline) or len(current) != 10:
            raise AssertionError(f"Block {block_id} does not contain exact 10 paired targets")
        first = next(iter(current.values()))
        output_root = output_root_from_partition(Path(first["source_path"]), "current_state")
        index_path = output_root / "validation" / "output_hashes.parquet"
        index_sidecar = index_path.with_name(index_path.name + ".sha256")
        index_sha = sha256_file(index_path)
        if index_sidecar.read_text(encoding="utf-8").strip() != index_sha:
            raise AssertionError(f"Hash-index sidecar mismatch: {index_path}")
        index_rows = pq.read_table(index_path, columns=["path", "sha256", "rows", "bytes"]).to_pylist()
        history_rows = [item for item in index_rows if family_from_path(str(item["path"])) == "current_state"]
        lineage_path = output_root / "metadata" / "lineage_manifest.json"
        lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
        targets = []
        for session in sorted(current):
            left, right = current[session], baseline[session]
            targets.append(
                {
                    "session_date": session,
                    "target_ordinal": int(left["target_ordinal"]),
                    "is_early_close": bool(left["is_early_close"]),
                    "current_path": str(Path(left["source_path"]).resolve()),
                    "current_sha256": str(left["actual_sha256"]),
                    "current_rows": int(left["actual_rows"]),
                    "current_bytes": int(left["source_bytes"]),
                    "baseline_path": str(Path(right["source_path"]).resolve()),
                    "baseline_sha256": str(right["actual_sha256"]),
                    "baseline_rows": int(right["actual_rows"]),
                    "baseline_bytes": int(right["source_bytes"]),
                }
            )
        block_final = Path(first["block_final_manifest"]).resolve()
        if sha256_file(block_final) != str(first["block_final_sha256"]):
            raise AssertionError(f"Block final hash mismatch: {block_final}")
        blocks.append(
            {
                "block_id": block_id,
                "block_run_id": str(first["block_run_id"]),
                "shard_index": int(first["shard_index"]),
                "instrument_id": str(first["instrument_id"]),
                "ticker": str(first["ticker"]),
                "source_engine_fingerprint": str(first["source_engine_fingerprint"]),
                "output_root": str(output_root.resolve()),
                "output_hash_index": str(index_path.resolve()),
                "output_hash_index_sha256": index_sha,
                "block_final_manifest": str(block_final),
                "block_final_sha256": str(first["block_final_sha256"]),
                "lineage_manifest": str(lineage_path.resolve()),
                "lineage_manifest_sha256": sha256_file(lineage_path),
                "config_sha256": str(lineage["config_sha256"]),
                "history_partition_count": len(history_rows),
                "history_rows": sum(int(item["rows"]) for item in history_rows),
                "history_bytes": sum(int(item["bytes"]) for item in history_rows),
                "targets": targets,
            }
        )
    if len(blocks) != 240:
        raise AssertionError(f"Expected 240 blocks, found {len(blocks)}")
    if Counter(block["shard_index"] for block in blocks) != Counter({0: 60, 1: 60, 2: 60, 3: 60}):
        raise AssertionError("Expected exactly 60 blocks in every shard")
    return blocks


def select_probe_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for shard in range(4):
        candidates = [
            block for block in blocks
            if block["shard_index"] == shard and any(target["is_early_close"] for target in block["targets"])
        ]
        if not candidates:
            raise AssertionError(f"No early-close probe block in shard {shard}")
        source = min(candidates, key=lambda item: (item["history_bytes"], item["block_id"]))
        early = next(target for target in source["targets"] if target["is_early_close"])
        regular = next(target for target in source["targets"] if not target["is_early_close"])
        selected.append({**source, "targets": [regular, early]})
    return selected


def scope_summary(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    targets = [target for block in blocks for target in block["targets"]]
    return {
        "block_count": len(blocks),
        "target_session_count": len(targets),
        "history_partition_count": sum(block["history_partition_count"] for block in blocks),
        "history_rows": sum(block["history_rows"] for block in blocks),
        "history_bytes": sum(block["history_bytes"] for block in blocks),
        "baseline_rows": sum(target["baseline_rows"] for target in targets),
        "baseline_bytes": sum(target["baseline_bytes"] for target in targets),
        "percentile_cells_to_compare": sum(target["baseline_rows"] for target in targets) * 4,
        "early_close_target_count": sum(bool(target["is_early_close"]) for target in targets),
        "shard_block_counts": dict(sorted(Counter(block["shard_index"] for block in blocks).items())),
    }


def base_plan(
    *,
    run_id: str,
    mode: str,
    run_root: Path,
    reference_manifest: Path,
    source_final: Path,
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    source_final_payload = json.loads(source_final.read_text(encoding="utf-8"))
    if source_final_payload.get("status") != "PASS":
        raise AssertionError("Frozen target-only source final is not PASS")
    required_files = [SCRIPT_PATH, ORACLE_PATH, RUNNER_PATH, MONITOR_PATH, AUTHORIZER_PATH, SPEC_PATH]
    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(path)
    return {
        "plan_schema_version": PLAN_SCHEMA,
        "run_id": run_id,
        "mode": mode,
        "artifact_status": (
            "PREREGISTERED_PROBE_PREPARED_FOR_HUMAN_LAUNCH"
            if mode == "PROBE"
            else "FULL_SCOPE_PREPARED_NOT_AUTHORIZED"
        ),
        "created_at_utc": utc_text(),
        "scientific_question": "Do all four materialized PIT percentiles equal an independent right-inclusive empirical rank replay from prior current_state observations?",
        "why_required": "The prior bounded evidence audit checked percentile domains and states but did not reconstruct the empirical ranks from historical observation vectors.",
        "independence_rule": "The oracle MUST NOT import or call the Python, vectorized, adapter or C++ Trading Activity baseline engines.",
        "formula": "count(reference_value <= current_value) / baseline_total_count",
        "interpolation": "PROHIBITED",
        "midrank": "PROHIBITED",
        "tie_policy": "RIGHT_INCLUSIVE",
        "variables": list(PERCENTILE_COLUMNS.values()),
        "baseline_candidates": list(CANDIDATES),
        "lookbacks": LOOKBACKS,
        "minimum_sessions": MINIMUM_SESSIONS,
        "exact_match_required": True,
        "null_mask_exact_required": True,
        "mismatch_tolerance": 0,
        "fail_closed": True,
        "source_reference_manifest": str(reference_manifest.resolve()),
        "source_reference_manifest_sha256": sha256_file(reference_manifest),
        "source_final_manifest": str(source_final.resolve()),
        "source_final_manifest_sha256": sha256_file(source_final),
        "source_exact_target_contract": source_final_payload["exact_target_contract"],
        "specification_path": str(SPEC_PATH.resolve()),
        "specification_sha256": sha256_file(SPEC_PATH),
        "builder_path": str(SCRIPT_PATH),
        "builder_sha256": sha256_file(SCRIPT_PATH),
        "oracle_path": str(ORACLE_PATH),
        "oracle_sha256": sha256_file(ORACLE_PATH),
        "runner_path": str(RUNNER_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "monitor_path": str(MONITOR_PATH),
        "monitor_sha256": sha256_file(MONITOR_PATH),
        "authorizer_path": str(AUTHORIZER_PATH),
        "authorizer_sha256": sha256_file(AUTHORIZER_PATH),
        "run_root": str(run_root.resolve()),
        "runtime_root": str((run_root / "runtime").resolve()),
        "artifacts_root": str((run_root / "artifacts").resolve()),
        "checkpoint_granularity": "ONE_BLOCK",
        "resume_policy": "ALLOWED_ONLY_FOR_HASH_IDENTICAL_PLAN_AND_PASS_BLOCK_CHECKPOINTS",
        "overwrite_policy": "NEVER",
        "safe_stop_file": str((run_root / "runtime" / "stop_requested.json").resolve()),
        "workers": 1,
        "worker_rationale": "D: is a mechanical USB source and one block uses substantial RAM; establish measured probe throughput before considering concurrency.",
        "scope": scope_summary(blocks),
        "blocks": blocks,
        "success_criteria": "All planned blocks and sessions complete; every metadata/null/value comparison is exact; total mismatches=0.",
        "canonical_promotion_authorized": False,
        "binding_b_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-manifest", required=True, type=Path)
    parser.add_argument("--source-final", required=True, type=Path)
    parser.add_argument("--probe-plan", required=True, type=Path)
    parser.add_argument("--full-preparation", required=True, type=Path)
    parser.add_argument("--probe-run-root", required=True, type=Path)
    parser.add_argument("--full-run-root", required=True, type=Path)
    parser.add_argument("--probe-run-id", required=True)
    parser.add_argument("--full-run-id", required=True)
    args = parser.parse_args()
    blocks = build_block_records(args.reference_manifest.resolve())
    probe = base_plan(
        run_id=args.probe_run_id,
        mode="PROBE",
        run_root=args.probe_run_root,
        reference_manifest=args.reference_manifest,
        source_final=args.source_final,
        blocks=select_probe_blocks(blocks),
    )
    full = base_plan(
        run_id=args.full_run_id,
        mode="FULL",
        run_root=args.full_run_root,
        reference_manifest=args.reference_manifest,
        source_final=args.source_final,
        blocks=blocks,
    )
    full["authorization_gate"] = "PROBE_PASS_PLUS_EXPLICIT_HUMAN_AUTHORIZATION_REQUIRED"
    write_json(args.probe_plan, probe)
    write_json(args.full_preparation, full)
    print(json.dumps({
        "status": "PREPARED",
        "probe_plan": str(args.probe_plan.resolve()),
        "probe_scope": probe["scope"],
        "full_preparation": str(args.full_preparation.resolve()),
        "full_scope": full["scope"],
        "full_authorized": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
