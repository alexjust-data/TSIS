"""Build hash-frozen PROBE or FULL plans for TA Stage-8 target-only recovery."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

import trading_activity_stage8_target_only_contract as contract

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
RUNNER = SCRIPT_DIR / "run_trading_activity_stage8_target_only_recovery.py"
MONITOR = SCRIPT_DIR / "monitor_trading_activity_stage8_target_only_recovery.ps1"
CONTRACT = SCRIPT_DIR / "trading_activity_stage8_target_only_contract.py"
PLAN_SCHEMA = "trading_activity_stage8_target_only_recovery_plan_v0_2"

DEFAULT_HISTORICAL_PLAN = Path(
    "C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/VARIABLES_FEATURES/"
    "TRADING_ACTIVITY_STAGE8_CPP_FULL_MATERIALIZATION_PLAN_v0_1.json"
)
DEFAULT_TARGET_TABLE = Path(
    "G:/TSIS/data/data_foundation_outputs/trading_activity_ta3_stratified_sample/"
    "trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z/"
    "selected_target_contexts_v0_1.parquet"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def block_to_shard(historical: dict[str, Any]) -> dict[str, int]:
    runtime_root = Path(historical["runtime_root"]).resolve()
    result: dict[str, int] = {}
    for shard in historical["shards"]:
        manifest = json.loads(
            (runtime_root / shard["run_id"] / "final_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        if manifest.get("final_status") != "COMPLETE":
            raise AssertionError(f"Source shard is not COMPLETE: {shard['run_id']}")
        for item in manifest.get("completed_blocks", []):
            block_id = str(item["block_id"])
            if block_id in result:
                raise AssertionError(f"Duplicate source block: {block_id}")
            result[block_id] = int(shard["shard_index"])
    if len(result) != 240:
        raise AssertionError(f"Expected 240 source blocks, got {len(result)}")
    return result


def choose_probe_rows(
    rows: list[dict[str, Any]], block_shards: dict[str, int]
) -> dict[str, list[dict[str, Any]]]:
    by_shard: dict[int, list[dict[str, Any]]] = {index: [] for index in range(4)}
    for row in rows:
        by_shard[block_shards[str(row["block_id"])]] .append(row)
    selected: dict[str, list[dict[str, Any]]] = {}
    for shard, shard_rows in by_shard.items():
        ordered = sorted(
            shard_rows,
            key=lambda row: (
                str(row["block_id"]),
                contract.normalized_session_date(row["session_date"]),
            ),
        )
        first = ordered[0]
        second = next(
            (
                row
                for row in ordered
                if bool(row.get("is_early_close"))
                and contract.exact_target_key(row) != contract.exact_target_key(first)
            ),
            ordered[-1],
        )
        if contract.exact_target_key(second) == contract.exact_target_key(first):
            second = ordered[-1]
        chosen = [first, second]
        if len({contract.exact_target_key(row) for row in chosen}) != 2:
            raise AssertionError(f"Could not choose two sparse probe targets for shard {shard}")
        selected[str(shard)] = chosen
    return selected


def probe_evidence(root: Path | None) -> dict[str, Any] | None:
    if root is None:
        return None
    evidence: dict[str, Any] = {}
    schemas: dict[str, set[str]] = {
        family: set() for family in contract.PHYSICAL_FAMILY_KEYS
    }
    for shard in range(4):
        final_path = root / f"shard_{shard}" / "runtime" / "final_manifest.json"
        final = json.loads(final_path.read_text(encoding="utf-8"))
        if final.get("status") != "PASS" or final.get("probe_shard") != shard:
            raise AssertionError(f"Probe shard {shard} is not terminal PASS")
        for family, values in final["schema_variants"].items():
            schemas[family].update(values)
        evidence[str(shard)] = {
            "final_manifest": str(final_path),
            "final_manifest_sha256": sha256_file(final_path),
            "exact_target_contract": final["exact_target_contract"],
        }
    variants = {family: len(values) for family, values in schemas.items()}
    if variants != {family: 1 for family in contract.PHYSICAL_FAMILY_KEYS}:
        raise AssertionError(f"Cross-shard schema variants differ: {variants}")
    return {"shards": evidence, "cross_shard_schema_variant_counts": variants}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("PROBE", "FULL"), required=True)
    parser.add_argument("--historical-plan", type=Path, default=DEFAULT_HISTORICAL_PLAN)
    parser.add_argument("--target-table", type=Path, default=DEFAULT_TARGET_TABLE)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--human-authorization", default="NOT_AUTHORIZED")
    parser.add_argument("--probe-evidence-root", type=Path)
    args = parser.parse_args()

    historical_path = args.historical_plan.resolve()
    target_path = args.target_table.resolve()
    historical = json.loads(historical_path.read_text(encoding="utf-8"))
    if historical.get("run_id") != "trading_activity_ta3_cpp_full_v0_1_20260811":
        raise ValueError("Unexpected immutable source run")
    if sha256_file(historical_path) != "2e7e4be33237cd1836cfe6ecf1c6ad5ca227b284a9152c87ca6dbddbebdaf5a5":
        raise ValueError("Historical plan SHA-256 differs from the frozen identity")
    if sha256_file(target_path) != "55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220":
        raise ValueError("Frozen target-table SHA-256 mismatch")
    sample_manifest = Path(historical["sample_manifest"]).resolve()
    if sha256_file(sample_manifest) != historical["sample_manifest_sha256"]:
        raise ValueError("Frozen sample-manifest SHA-256 mismatch")

    rows = pq.read_table(target_path).to_pylist()
    full_scope = contract.aggregate_contract(rows)
    expected_full = {
        "current_state": 279330000,
        "multiscale_contrast": 111732000,
        "pit_baseline_and_surprise": 837990000,
    }
    contract.assert_physical_counts(
        full_scope["physical_family_row_counts"], expected_full
    )
    block_shards = block_to_shard(historical)
    chosen = choose_probe_rows(rows, block_shards)
    probe_keys = {
        shard: [
            {
                "block_id": str(row["block_id"]),
                "instrument_id": str(row["instrument_id"]),
                "ticker_as_of_session": str(row["ticker_as_of_session"]),
                "session_date": contract.normalized_session_date(row["session_date"]),
            }
            for row in selected
        ]
        for shard, selected in chosen.items()
    }
    probe_contracts = {
        shard: contract.aggregate_contract(selected)
        for shard, selected in chosen.items()
    }
    root = args.run_root.resolve()
    evidence = probe_evidence(
        args.probe_evidence_root.resolve() if args.probe_evidence_root else None
    )
    if args.mode == "PROBE":
        artifact_status = "PREREGISTERED_PROBE_AUTHORIZED"
    elif str(args.human_authorization).startswith("AUTHORIZED_") and evidence:
        artifact_status = "PREREGISTERED_HUMAN_AUTHORIZED"
    else:
        artifact_status = "PREREGISTERED_NOT_AUTHORIZED"

    control_status = "PENDING_RUNTIME_PROBE" if evidence is None else "PASS"
    controls = [
        {
            "control_id": control_id,
            "source_incident_id": incident_id,
            "applicability": "applicable",
            "implementation_reference": {
                "runner": str(RUNNER.resolve()),
                "runner_sha256": sha256_file(RUNNER),
                "contract": str(CONTRACT.resolve()),
                "contract_sha256": sha256_file(CONTRACT),
            },
            "regression_test_reference": (
                "01_TSIS_DATA_FOUNDATION/tests/"
                "test_trading_activity_stage8_target_only_recovery.py"
            ),
            "probe_evidence_reference": evidence,
            "terminal_rehearsal_reference": evidence,
            "status": control_status,
        }
        for control_id, incident_id in (
            ("RM-MAT-CTRL-001", "RM-MAT-INC-001"),
            ("RM-MAT-CTRL-002", "RM-MAT-INC-002"),
            ("RM-MAT-CTRL-003", "RM-MAT-INC-003"),
            ("RM-MAT-CTRL-004", "RM-MAT-INC-004"),
            ("RM-MAT-CTRL-005", "RM-MAT-INC-005"),
        )
    ]
    plan = {
        "plan_schema_version": PLAN_SCHEMA,
        "plan_version": "trading_activity_stage8_target_only_recovery_plan_v0_2",
        "artifact_status": artifact_status,
        "mode": args.mode,
        "human_authorization": args.human_authorization,
        "run_id": args.run_id,
        "run_root": str(root),
        "probe_run_roots": {
            str(shard): str(root / f"shard_{shard}") for shard in range(4)
        },
        "source_run_id": historical["run_id"],
        "source_run_status": "FAILED_NOT_PROMOTED",
        "source_run_root": str(Path(historical["output_root"]).resolve().parent),
        "source_output_root": str(Path(historical["output_root"]).resolve()),
        "source_runtime_root": str(Path(historical["runtime_root"]).resolve()),
        "source_blocks_recomputed": 0,
        "historical_plan": str(historical_path),
        "historical_plan_sha256": sha256_file(historical_path),
        "target_table": str(target_path),
        "target_table_sha256": sha256_file(target_path),
        "sample_manifest": str(sample_manifest),
        "sample_manifest_sha256": sha256_file(sample_manifest),
        "expected_stage8_engine_fingerprint": historical[
            "expected_stage8_engine_fingerprint"
        ],
        "source_shards": historical["shards"],
        "full_scope_contract": full_scope,
        "probe_target_keys_by_shard": probe_keys,
        "probe_scope_contracts": probe_contracts,
        "authoritative_cardinality_contract_id": contract.CONTRACT_ID,
        "runner": str(RUNNER.resolve()),
        "runner_sha256": sha256_file(RUNNER),
        "contract": str(CONTRACT.resolve()),
        "contract_sha256": sha256_file(CONTRACT),
        "monitor": str(MONITOR.resolve()),
        "monitor_sha256": sha256_file(MONITOR),
        "plan_builder": str(SCRIPT_PATH),
        "plan_builder_sha256": sha256_file(SCRIPT_PATH),
        "inherited_incident_controls": controls,
        "resume_policy": (
            "SAME_PLAN_SCRIPT_CONTRACT_TARGET_SOURCE_HASHES_ONLY_"
            "REUSE_HASH_VALIDATED_PASS_UNITS"
        ),
        "overwrite_policy": "NEVER",
        "canonical_promotion_authorized": False,
        "success_criteria": [
            "exact frozen target membership",
            "three typed physical-family count keys only",
            "selected partition SHA-256 and Parquet footer rows PASS",
            "one schema variant per family",
            "block grain temporal baseline validators PASS and hash-bound",
            "future_window_used false",
            "source blocks recomputed equals zero",
            "canonical promotion remains false",
        ],
    }
    atomic_json(args.output.resolve(), plan)
    print(json.dumps(plan, indent=2))
    print(str(args.output.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
