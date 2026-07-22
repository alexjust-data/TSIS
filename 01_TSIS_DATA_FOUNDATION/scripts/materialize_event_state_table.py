from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from _state_fixture_builder import (
    FixtureValidationError,
    build_deterministic_fixture_sample,
    parse_utc,
    prohibited_prefixes,
    validate_no_prohibited_keys,
    validate_required_flags,
)


DATASET_ID = "event_state_table_v0_1"
STATUS = "contract_defined_not_materialized"
SCHEMA_VERSION = "event_state_table_v0_1"
CANDIDATE_DATASET_ID = "event_state_table_v0_1_candidate"
CANDIDATE_DATASET_DIR_NAME = "event_state_table_v0_1_candidate_microstructure_halt_controlled"
CANDIDATE_SCOPE = "halt_event_window_event_state_controlled_candidate"
CANDIDATE_BUILDER_VERSION = "event_state_builder_candidate_v0_1"
SOURCE_CUTOFF_POLICY_VERSION = "event_state_cutoff_policy_v0_1_candidate"
LEAKAGE_POLICY_VERSION = "event_state_leakage_policy_v0_1_candidate"
FEATURE_NAMESPACE_VERSION = "event_state_feature_namespaces_v0_1_candidate"

MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\event_state_table")
DEFAULT_MARKET_STATE_ROOT = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_state_table"
    r"\market_state_table_v0_1_candidate_microstructure_halt_controlled"
)
DEFAULT_MARKET_STATE_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_state_table"
    r"\_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json"
)
DEFAULT_EVENT_WINDOWS = Path(
    r"E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet"
)

REQUIRED_CONTRACTS = {
    "composition_contract": "01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "build_loop_runbook": "01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "schema": "01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/event_state_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml",
    "validators": "01_foundations/validators/outputs/event_state_table_validators.md",
}

EVENT_WINDOW_COLUMNS = [
    "event_window_id",
    "source_event_id",
    "event_source_dataset_id",
    "event_family",
    "event_type",
    "event_code",
    "event_source",
    "ticker",
    "instrument_id",
    "session_date",
    "event_time_utc",
    "resume_trade_utc",
    "window_role",
    "window_start_utc",
    "window_end_utc",
    "contains_post_event_information",
    "leakage_safe_as_pre_event_feature",
    "source_event_quality_state",
    "event_window_quality_state",
    "event_window_consumption_state",
    "valid_for_microstructure_feature_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_backtest_event_window_candidate",
    "schema_version",
    "quality_policy_version",
    "build_run_id",
]


def contract_status() -> dict[str, Any]:
    paths = {
        name: {
            "relative_path": relative_path,
            "exists": (MODULE_ROOT / relative_path).exists(),
        }
        for name, relative_path in REQUIRED_CONTRACTS.items()
    }
    return {
        "dataset_id": DATASET_ID,
        "status": STATUS,
        "materialized": False,
        "builder_implemented": False,
        "official_builder_implemented": False,
        "candidate_builder_implemented": True,
        "fixture_builder_implemented": True,
        "writes_output": False,
        "official_output_writes": False,
        "required_contracts": paths,
        "missing_contracts": [
            name for name, item in paths.items() if not bool(item["exists"])
        ],
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_id(*parts: object) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _json_bundle(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _safe_remove_dataset_dir(dataset_dir: Path, output_root: Path) -> None:
    resolved_dataset = dataset_dir.resolve()
    resolved_root = output_root.resolve()
    if resolved_dataset == resolved_root:
        raise RuntimeError(f"Refusing to delete output root: {dataset_dir}")
    if "event_state_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    shutil.rmtree(dataset_dir)


def _sha256_parquet_tree(root: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        file_hash = _sha256_file(path)
        total_bytes += size
        digest.update(rel.encode("utf-8"))
        digest.update(str(size).encode("ascii"))
        digest.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def _write_partitioned(frame: pd.DataFrame, dataset_dir: Path) -> None:
    frame = frame.copy()
    frame["decision_year"] = pd.to_datetime(frame["decision_timestamp_utc"], utc=True).dt.year
    for (event_family, year), part in frame.groupby(["event_family", "decision_year"], dropna=False):
        part_dir = dataset_dir / f"event_family={event_family}" / f"decision_year={int(year):04d}"
        part_dir.mkdir(parents=True, exist_ok=True)
        part.drop(columns=["event_family", "decision_year"]).to_parquet(part_dir / "part-0000.parquet", index=False)


def _state_role(window_role: str, contains_post_event_information: bool) -> str:
    if window_role == "pre_event_30m" and not contains_post_event_information:
        return "pre_event"
    if window_role == "same_session_regular":
        return "post_event_review"
    if contains_post_event_information:
        return "post_event_review"
    return "research_replay"


def _state_quality(state_role: str, market_state_quality: str) -> str:
    if market_state_quality.startswith("state_blocked") or market_state_quality.startswith("state_bad"):
        return "event_state_blocked_invalid_component_quality"
    if state_role == "post_event_review":
        return "event_state_review_microstructure_seed_only"
    return "event_state_review_microstructure_seed_only"


def materialize_event_state_candidate(
    *,
    market_state_root: Path,
    market_state_manifest: Path,
    event_windows_path: Path,
    output_root: Path,
    overwrite: bool,
    dataset_dir_name: str = CANDIDATE_DATASET_DIR_NAME,
    manifest_name: str = "_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json",
    summary_name: str = "_event_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv",
) -> dict[str, Any]:
    for label, path in {
        "market state root": market_state_root,
        "market state manifest": market_state_manifest,
        "event windows table": event_windows_path,
    }.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {label}: {path}")

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / dataset_dir_name
    manifest_path = output_root / manifest_name
    summary_path = output_root / summary_name
    if dataset_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {dataset_dir}")
        _safe_remove_dataset_dir(dataset_dir, output_root)

    created_at_utc = _utc_now()
    build_run_id = datetime.now(timezone.utc).strftime("event_state_table_v0_1_candidate_%Y%m%dT%H%M%SZ")
    market = pd.read_parquet(market_state_root)
    events = pd.read_parquet(event_windows_path, columns=EVENT_WINDOW_COLUMNS)
    merged = market.merge(
        events,
        left_on="source_event_window_id",
        right_on="event_window_id",
        how="left",
        suffixes=("", "_event"),
    )
    if merged["event_window_id"].isna().any():
        missing = merged.loc[merged["event_window_id"].isna(), "source_event_window_id"].head(5).tolist()
        raise ValueError(f"Missing event-window joins for: {missing}")

    market_manifest = _read_json(market_state_manifest)
    market_manifest_sha = _sha256_file(market_state_manifest)
    event_windows_sha = _sha256_file(event_windows_path)
    rows: list[dict[str, Any]] = []
    passthrough_prefixes = (
        "identity__",
        "calendar__",
        "halt__",
        "microstructure__",
        "quality__",
    )
    for item in merged.to_dict(orient="records"):
        contains_post = bool(item.get("contains_post_event_information", False))
        role = _state_role(str(item.get("window_role")), contains_post)
        decision_ts = pd.Timestamp(item["decision_timestamp_utc"]).tz_convert("UTC")
        event_ts = pd.Timestamp(item["event_time_utc"]).tz_convert("UTC") if pd.notna(item.get("event_time_utc")) else None
        state_cutoff = min(decision_ts, event_ts) if event_ts is not None and role in {"pre_event", "at_event"} else decision_ts
        window_start = item.get("window_start_utc_event", item.get("window_start_utc"))
        window_end = item.get("window_end_utc_event", item.get("window_end_utc"))
        event_state_id = "event_state_" + _stable_id(
            item["event_window_id"],
            item["market_state_id"],
            role,
            decision_ts.isoformat(),
            SCHEMA_VERSION,
        )
        output: dict[str, Any] = {
            "event_state_id": event_state_id,
            "event_id": item["source_event_id"],
            "event_window_id": item["event_window_id"],
            "market_state_id": item["market_state_id"],
            "instrument_id": item["instrument_id"],
            "ticker": item["ticker"],
            "event_family": item["event_family"],
            "event_timestamp_utc": event_ts.isoformat() if event_ts is not None else None,
            "decision_timestamp_utc": decision_ts.isoformat(),
            "decision_date": decision_ts.date().isoformat(),
            "state_role": role,
            "state_schema_version": SCHEMA_VERSION,
            "state_builder_version": CANDIDATE_BUILDER_VERSION,
            "state_quality_state": _state_quality(role, str(item.get("state_quality_state"))),
            "event_window_start_utc": pd.Timestamp(window_start).tz_convert("UTC").isoformat(),
            "event_window_end_utc": pd.Timestamp(window_end).tz_convert("UTC").isoformat(),
            "pre_event_window_start_utc": pd.Timestamp(window_start).tz_convert("UTC").isoformat()
            if role == "pre_event"
            else None,
            "pre_event_window_end_utc": pd.Timestamp(window_end).tz_convert("UTC").isoformat()
            if role == "pre_event"
            else None,
            "state_cutoff_utc": state_cutoff.isoformat(),
            "state_cutoff_reason": "pre_event_or_event_cutoff" if role in {"pre_event", "at_event"} else "post_event_review_window_end",
            "event_source_dataset_id": item["event_source_dataset_id"],
            "event_source_quality_state": item.get("source_event_quality_state"),
            "outcome_join_key": item["event_window_id"],
            "label_join_key": item["event_window_id"],
            "outcome_values_inline_allowed": False,
            "label_columns_inline_allowed": False,
            "reward_columns_inline_allowed": False,
            "valid_for_pattern_discovery": True,
            "valid_for_ml_feature_candidate": False,
            "valid_for_backtest_context_candidate": False,
            "valid_for_rl_state_candidate": False,
            "valid_for_rl_training_direct": False,
            "valid_for_execution_context_candidate": False,
            "valid_for_execution_simulator_direct": False,
            "contains_future_information_without_event_filter": contains_post,
            "requires_asof_filter": True,
            "full_universe_claim": False,
            "execution_truth": False,
            "build_run_id": build_run_id,
            "created_at_utc": created_at_utc,
            "market_state_build_run_id": item.get("build_run_id"),
            "event_windows_build_run_id": item.get("build_run_id_event") or item.get("build_run_id"),
            "component_manifest_hash_bundle": _json_bundle(
                {
                    "market_state_manifest_sha256": market_manifest_sha,
                    "event_windows_table_sha256": event_windows_sha,
                }
            ),
            "source_cutoff_policy_version": SOURCE_CUTOFF_POLICY_VERSION,
            "leakage_policy_version": LEAKAGE_POLICY_VERSION,
            "feature_namespace_version": FEATURE_NAMESPACE_VERSION,
            "event__window_role": item.get("window_role"),
            "event__event_type": item.get("event_type"),
            "event__event_code": item.get("event_code"),
            "event__event_source": item.get("event_source"),
            "quality__source_market_state_dataset_id": market_manifest.get("dataset_id"),
            "quality__candidate_dataset_id": CANDIDATE_DATASET_ID,
            "quality__candidate_materialization_scope": CANDIDATE_SCOPE,
        }
        for key, value in item.items():
            if key.startswith(passthrough_prefixes):
                output[key] = value
        rows.append(output)

    frame = pd.DataFrame(rows)
    duplicate_state_ids = int(frame["event_state_id"].duplicated().sum())
    if duplicate_state_ids:
        raise ValueError(f"Duplicate event_state_id rows: {duplicate_state_ids}")

    _write_partitioned(frame, dataset_dir)
    output_tree = _sha256_parquet_tree(dataset_dir)
    summary = pd.DataFrame(
        [
            {
                "dataset_id": CANDIDATE_DATASET_ID,
                "build_run_id": build_run_id,
                "materialization_scope": CANDIDATE_SCOPE,
                "row_count": int(len(frame)),
                "ticker_count": int(frame["ticker"].nunique()),
                "event_window_count": int(frame["event_window_id"].nunique()),
                "pre_event_rows": int(frame["state_role"].eq("pre_event").sum()),
                "post_event_review_rows": int(frame["state_role"].eq("post_event_review").sum()),
                "valid_for_pattern_discovery_rows": int(frame["valid_for_pattern_discovery"].sum()),
                "valid_for_ml_feature_candidate_rows": int(frame["valid_for_ml_feature_candidate"].sum()),
                "valid_for_rl_state_candidate_rows": int(frame["valid_for_rl_state_candidate"].sum()),
                "full_universe_claim_rows": int(frame["full_universe_claim"].sum()),
                "duplicate_state_id_rows": duplicate_state_ids,
                "state_quality_counts_json": _json_bundle(frame["state_quality_state"].value_counts().to_dict()),
                "output_tree_sha256": output_tree["tree_sha256"],
            }
        ]
    )
    summary.to_csv(summary_path, index=False)
    manifest = {
        "dataset_id": CANDIDATE_DATASET_ID,
        "physical_dataset_id": dataset_dir_name,
        "schema_version": SCHEMA_VERSION,
        "status": "controlled_candidate_not_promoted",
        "promotion_level": "controlled_candidate",
        "materialization_scope": CANDIDATE_SCOPE,
        "full_universe_claim": False,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": str(dataset_dir),
        "manifest_path": str(manifest_path),
        "summary_path": str(summary_path),
        "output_tree": output_tree,
        "source_inputs": {
            "market_state_root": str(market_state_root),
            "market_state_manifest": str(market_state_manifest),
            "event_windows_table": str(event_windows_path),
        },
        "source_hashes": {
            "market_state_manifest_sha256": market_manifest_sha,
            "event_windows_table_sha256": event_windows_sha,
        },
        "source_root_states": market_manifest.get("source_root_states", {}),
        "contracts": REQUIRED_CONTRACTS,
        "validations": summary.iloc[0].to_dict(),
        "limitations": [
            "Controlled candidate only; not institutional event_state_table_v0_1.",
            "Built from controlled market_state candidate and halt event windows.",
            "No labels, rewards, strategy signals, actions, fills, PnL or outcomes are embedded.",
            "ML/RL/backtest/execution direct-use gates remain false.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def validate_event_state_row(row: dict[str, Any], config: dict[str, Any]) -> None:
    required_fields = [
        "event_state_id",
        "event_id",
        "event_window_id",
        "market_state_id",
        "instrument_id",
        "ticker",
        "event_family",
        "event_timestamp_utc",
        "decision_timestamp_utc",
        "decision_date",
        "state_role",
        "state_schema_version",
        "state_builder_version",
        "state_quality_state",
        "state_cutoff_utc",
    ]
    for field in required_fields:
        if field not in row:
            raise FixtureValidationError(f"missing required event state field: {field}")

    validate_no_prohibited_keys(row, prohibited_prefixes(config))
    validate_required_flags(row, config.get("required_flags", {}))

    allowed_roles = set(config.get("allowed_state_roles", []))
    state_role = row["state_role"]
    if state_role not in allowed_roles:
        raise FixtureValidationError(f"state_role is not allowed: {state_role}")

    decision_timestamp = parse_utc(
        row["decision_timestamp_utc"], "decision_timestamp_utc"
    )
    state_cutoff = parse_utc(row["state_cutoff_utc"], "state_cutoff_utc")
    assert decision_timestamp is not None
    if state_cutoff is not None and state_cutoff > decision_timestamp:
        raise FixtureValidationError(
            "state_cutoff_utc must be <= decision_timestamp_utc"
        )

    ml_roles = set(config.get("ml_feature_state_roles", []))
    if row.get("valid_for_ml_feature_candidate") is True and state_role not in ml_roles:
        raise FixtureValidationError(
            "post_event/replay rows cannot be valid_for_ml_feature_candidate"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Skeleton guard and controlled-candidate builder for "
            "event_state_table_v0_1. This script does not materialize official "
            "institutional output."
        )
    )
    parser.add_argument(
        "--contract-check-only",
        action="store_true",
        help="Validate that required contracts exist and exit without writing output.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Future validated builder config. Required before materialization is implemented.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Test-run output directory for deterministic fixture samples. Must live "
            "under C:/TSIS_Data/tests/test_runs."
        ),
    )
    parser.add_argument(
        "--materialize-candidate",
        action="store_true",
        help="Write a controlled candidate event_state sample from market_state candidate.",
    )
    parser.add_argument("--market-state-root", type=Path, default=DEFAULT_MARKET_STATE_ROOT)
    parser.add_argument("--market-state-manifest", type=Path, default=DEFAULT_MARKET_STATE_MANIFEST)
    parser.add_argument("--event-windows", type=Path, default=DEFAULT_EVENT_WINDOWS)
    parser.add_argument("--candidate-output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--candidate-dataset-dir-name", default=CANDIDATE_DATASET_DIR_NAME)
    parser.add_argument(
        "--candidate-manifest-name",
        default="_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json",
    )
    parser.add_argument(
        "--candidate-summary-name",
        default="_event_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    status = contract_status()
    if args.contract_check_only:
        print(json.dumps(status, indent=2, sort_keys=True))
        if status["missing_contracts"]:
            raise SystemExit(1)
        return

    if args.materialize_candidate:
        if status["missing_contracts"]:
            raise SystemExit(
                "Required event_state_table_v0_1 contracts are missing; refusing "
                "candidate build."
            )
        manifest = materialize_event_state_candidate(
            market_state_root=args.market_state_root,
            market_state_manifest=args.market_state_manifest,
            event_windows_path=args.event_windows,
            output_root=args.candidate_output_root,
            overwrite=args.overwrite,
            dataset_dir_name=args.candidate_dataset_dir_name,
            manifest_name=args.candidate_manifest_name,
            summary_name=args.candidate_summary_name,
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "manifest": manifest["manifest_path"],
                    "output": manifest["output_path"],
                    "validations": manifest["validations"],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if args.config is not None:
        if status["missing_contracts"]:
            raise SystemExit(
                "Required event_state_table_v0_1 contracts are missing; refusing "
                "fixture build."
            )
        if args.output_dir is None:
            raise SystemExit("--output-dir is required with --config")
        try:
            manifest = build_deterministic_fixture_sample(
                dataset_id=DATASET_ID,
                config_path=args.config,
                output_dir=args.output_dir,
                row_validator=validate_event_state_row,
            )
        except FixtureValidationError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    raise SystemExit(
        "event_state_table_v0_1 is contract-defined but not materialized. "
        "Use --contract-check-only for the current skeleton check, or --config "
        "--output-dir for deterministic fixture-only validation. Use "
        "--materialize-candidate for the controlled candidate sample. Official "
        "institutional materialization still requires promotion gates."
    )


if __name__ == "__main__":
    main()
