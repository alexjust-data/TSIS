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


DATASET_ID = "market_state_table_v0_1"
STATUS = "contract_defined_not_materialized"
SCHEMA_VERSION = "market_state_table_v0_1"
CANDIDATE_DATASET_ID = "market_state_table_v0_1_candidate"
CANDIDATE_DATASET_DIR_NAME = "market_state_table_v0_1_candidate_microstructure_halt_controlled"
CANDIDATE_SCOPE = "halt_event_window_microstructure_controlled_candidate"
CANDIDATE_BUILDER_VERSION = "market_state_builder_candidate_v0_1"
SOURCE_CUTOFF_POLICY_VERSION = "market_state_cutoff_policy_v0_1_candidate"
LEAKAGE_POLICY_VERSION = "market_state_leakage_policy_v0_1_candidate"
FEATURE_NAMESPACE_VERSION = "market_state_feature_namespaces_v0_1_candidate"

MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\market_state_table")
DEFAULT_MICROSTRUCTURE_PARQUET = Path(
    r"E:\TSIS\data\data_foundation_outputs\microstructure_features_table"
    r"\microstructure_features_table_v0_2_candidate_controlled_25_per_role"
    r"\year=2025\month=12\part-0000.parquet"
)
DEFAULT_MICROSTRUCTURE_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\microstructure_features_table"
    r"\_microstructure_features_table_manifest_v0_2_candidate_controlled_25_per_role.json"
)
DEFAULT_EVENT_WINDOWS = Path(
    r"E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet"
)

REQUIRED_CONTRACTS = {
    "composition_contract": "01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "build_loop_runbook": "01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "schema": "01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/market_state_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml",
    "validators": "01_foundations/validators/outputs/market_state_table_validators.md",
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
    "event_session_phase",
    "window_role",
    "window_start_utc",
    "window_end_utc",
    "contains_post_event_information",
    "leakage_safe_as_pre_event_feature",
    "event_window_quality_state",
    "event_window_consumption_state",
    "valid_for_microstructure_feature_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_backtest_event_window_candidate",
    "schema_version",
    "quality_policy_version",
    "build_run_id",
]

MICROSTRUCTURE_FEATURE_COLUMNS = [
    "quotes_rows",
    "quotes_window_rows",
    "quotes_two_sided_rows",
    "quotes_crossed_rows",
    "quotes_locked_rows",
    "quotes_crossed_ratio_pct_all_rows",
    "quotes_locked_ratio_pct_two_sided",
    "quotes_spread_bps_median",
    "quotes_spread_bps_p90",
    "quotes_top_depth_mean",
    "trades_rows",
    "trades_window_rows",
    "trades_invalid_price_rows",
    "trades_invalid_size_rows",
    "trades_odd_lot_ratio_pct",
    "trades_duplicate_exact_ratio_pct",
    "trades_total_volume",
    "trades_dollar_volume",
    "trades_price_min",
    "trades_price_max",
    "trades_price_last",
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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_id(*parts: object) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_remove_dataset_dir(dataset_dir: Path, output_root: Path) -> None:
    resolved_dataset = dataset_dir.resolve()
    resolved_root = output_root.resolve()
    if resolved_dataset == resolved_root:
        raise RuntimeError(f"Refusing to delete output root: {dataset_dir}")
    if "market_state_table" not in str(resolved_dataset):
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


def _json_bundle(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _component_state(row: pd.Series, component: str) -> str:
    if component == "identity":
        return "included_good" if bool(row.get("instrument_identity_temporal_match", False)) else "missing_required"
    if component == "calendar":
        return "included_good" if pd.notna(row.get("event_session_phase")) else "missing_optional"
    if component == "microstructure":
        quality = str(row.get("microstructure_quality_state", ""))
        if quality.startswith("hard_fail"):
            return "missing_required"
        return "included_good" if quality == "pass_seed_window" else "included_review"
    if component == "halt":
        return "included_good" if str(row.get("event_family")) == "halt" else "not_requested"
    if component == "quality":
        return "included_review"
    if component == "short_constraints":
        return "blocked_by_policy"
    return "not_requested"


def _state_quality(row: pd.Series) -> str:
    if pd.isna(row.get("window_end_utc")):
        return "state_bad_missing_decision_timestamp"
    if _component_state(row, "identity") == "missing_required":
        return "state_blocked_required_component_missing"
    if _component_state(row, "microstructure") == "missing_required":
        return "state_blocked_invalid_component_quality"
    return "state_review_microstructure_seed_only"


def _write_partitioned(frame: pd.DataFrame, dataset_dir: Path) -> None:
    frame = frame.copy()
    frame["decision_year"] = pd.to_datetime(frame["decision_timestamp_utc"], utc=True).dt.year
    frame["decision_month"] = pd.to_datetime(frame["decision_timestamp_utc"], utc=True).dt.month
    for (year, month), part in frame.groupby(["decision_year", "decision_month"], dropna=False):
        part_dir = dataset_dir / f"decision_year={int(year):04d}" / f"decision_month={int(month):02d}"
        part_dir.mkdir(parents=True, exist_ok=True)
        part.drop(columns=["decision_year", "decision_month"]).to_parquet(part_dir / "part-0000.parquet", index=False)


def materialize_market_state_candidate(
    *,
    microstructure_parquet: Path,
    microstructure_manifest: Path,
    event_windows_path: Path,
    output_root: Path,
    overwrite: bool,
    dataset_dir_name: str = CANDIDATE_DATASET_DIR_NAME,
    manifest_name: str = "_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json",
    summary_name: str = "_market_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv",
) -> dict[str, Any]:
    for label, path in {
        "microstructure parquet": microstructure_parquet,
        "microstructure manifest": microstructure_manifest,
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
    build_run_id = datetime.now(timezone.utc).strftime("market_state_table_v0_1_candidate_%Y%m%dT%H%M%SZ")
    micro = pd.read_parquet(microstructure_parquet)
    events = pd.read_parquet(event_windows_path, columns=EVENT_WINDOW_COLUMNS)
    merged = micro.merge(events, on="event_window_id", how="left", suffixes=("", "_event"))
    if merged["source_event_id"].isna().any():
        missing = merged.loc[merged["source_event_id"].isna(), "event_window_id"].head(5).tolist()
        raise ValueError(f"Missing event-window joins for: {missing}")

    micro_manifest = _read_json(microstructure_manifest)
    event_windows_sha = _sha256_file(event_windows_path)
    micro_manifest_sha = _sha256_file(microstructure_manifest)
    rows: list[dict[str, Any]] = []
    for item in merged.to_dict(orient="records"):
        row = pd.Series(item)
        decision_ts = pd.Timestamp(item["window_end_utc"]).tz_convert("UTC")
        decision_iso = decision_ts.isoformat()
        component_availability = {
            name: _component_state(row, name)
            for name in [
                "identity",
                "calendar",
                "scanner",
                "daily",
                "intraday",
                "microstructure",
                "halt",
                "fundamentals",
                "news",
                "short_context",
                "short_constraints",
                "regime",
                "quality",
            ]
        }
        market_state_id = _stable_id(
            item["instrument_id"],
            item["event_window_id"],
            decision_iso,
            item["window_label"],
            SCHEMA_VERSION,
        )
        component_quality = {
            "microstructure_quality_state": item.get("microstructure_quality_state"),
            "event_window_quality_state": item.get("event_window_quality_state"),
            "quotes_root_state": item.get("quotes_root_state"),
            "trades_root_state": item.get("trades_root_state"),
        }
        halt_as_of = (
            pd.Timestamp(item["event_time_utc"]).tz_convert("UTC")
            if pd.notna(item.get("event_time_utc"))
            else None
        )
        halt_as_of_iso = halt_as_of.isoformat() if halt_as_of is not None and halt_as_of <= decision_ts else None
        output: dict[str, Any] = {
            "market_state_id": "market_state_" + market_state_id,
            "source_event_window_id": item["event_window_id"],
            "source_event_id": item["source_event_id"],
            "source_microstructure_feature_id": item["microstructure_feature_id"],
            "instrument_id": item["instrument_id"],
            "ticker": item["ticker"],
            "decision_timestamp_utc": decision_iso,
            "decision_date": decision_ts.date().isoformat(),
            "decision_session_date": str(item["session_date"]),
            "state_horizon": item["window_label"],
            "state_scope": CANDIDATE_SCOPE,
            "state_schema_version": SCHEMA_VERSION,
            "state_builder_version": CANDIDATE_BUILDER_VERSION,
            "state_quality_state": _state_quality(row),
            "build_run_id": build_run_id,
            "created_at_utc": created_at_utc,
            "source_cutoff_policy_version": SOURCE_CUTOFF_POLICY_VERSION,
            "leakage_policy_version": LEAKAGE_POLICY_VERSION,
            "feature_namespace_version": FEATURE_NAMESPACE_VERSION,
            "component_manifest_hash_bundle": _json_bundle(
                {
                    "microstructure_manifest_sha256": micro_manifest_sha,
                    "event_windows_table_sha256": event_windows_sha,
                }
            ),
            "component_build_run_id_bundle": _json_bundle(
                {
                    "microstructure_build_run_id": micro_manifest.get("build_run_id"),
                    "event_windows_build_run_id": item.get("build_run_id_event") or item.get("build_run_id"),
                }
            ),
            "component_quality_bundle": _json_bundle(component_quality),
            "component_availability_bundle": _json_bundle(component_availability),
            "valid_for_event_context_candidate": True,
            "valid_for_ml_feature_candidate": False,
            "valid_for_backtest_context_candidate": False,
            "valid_for_rl_state_candidate": False,
            "valid_for_rl_training_direct": False,
            "valid_for_execution_simulator_direct": False,
            "contains_future_information_without_event_filter": bool(item.get("contains_post_event_information", False)),
            "requires_asof_filter": True,
            "full_universe_claim": False,
            "execution_truth": False,
            "identity_component_state": component_availability["identity"],
            "calendar_component_state": component_availability["calendar"],
            "scanner_component_state": component_availability["scanner"],
            "daily_component_state": component_availability["daily"],
            "intraday_component_state": component_availability["intraday"],
            "microstructure_component_state": component_availability["microstructure"],
            "halt_component_state": component_availability["halt"],
            "fundamentals_component_state": component_availability["fundamentals"],
            "news_component_state": component_availability["news"],
            "short_context_component_state": component_availability["short_context"],
            "short_constraints_component_state": component_availability["short_constraints"],
            "regime_component_state": component_availability["regime"],
            "quality_component_state": component_availability["quality"],
            "identity_as_of_utc": None,
            "calendar_as_of_utc": decision_iso,
            "scanner_as_of_utc": None,
            "daily_as_of_utc": None,
            "intraday_as_of_utc": None,
            "microstructure_as_of_utc": decision_iso,
            "halt_as_of_utc": halt_as_of_iso,
            "fundamentals_as_of_utc": None,
            "news_as_of_utc": None,
            "short_context_as_of_utc": None,
            "short_constraints_as_of_utc": None,
            "regime_as_of_utc": None,
            "identity__is_common_stock": item.get("is_common_stock"),
            "identity__is_lt1b_operational": item.get("is_lt1b_operational"),
            "identity__instrument_identity_temporal_match": item.get("instrument_identity_temporal_match"),
            "calendar__session_date": str(item["session_date"]),
            "calendar__event_session_phase": item.get("event_session_phase"),
            "halt__event_family": item.get("event_family"),
            "halt__event_type": item.get("event_type"),
            "halt__event_code": item.get("event_code"),
            "halt__event_source": item.get("event_source"),
            "microstructure__quotes_root_state": item.get("quotes_root_state"),
            "microstructure__trades_root_state": item.get("trades_root_state"),
            "microstructure__source_quotes_file_present": item.get("source_quotes_file_present"),
            "microstructure__source_trades_file_present": item.get("source_trades_file_present"),
            "microstructure__quality_state": item.get("microstructure_quality_state"),
            "quality__candidate_dataset_id": CANDIDATE_DATASET_ID,
            "quality__candidate_materialization_scope": CANDIDATE_SCOPE,
            "quality__requires_rebuild_after_e_quotes_parity": True,
            "quality__source_microstructure_dataset_id": micro_manifest.get("dataset_id"),
            "quality__source_quotes_root_state": item.get("quotes_root_state"),
        }
        for column in MICROSTRUCTURE_FEATURE_COLUMNS:
            output[f"microstructure__{column}"] = item.get(column)
        rows.append(output)

    frame = pd.DataFrame(rows)
    duplicate_state_ids = int(frame["market_state_id"].duplicated().sum())
    if duplicate_state_ids:
        raise ValueError(f"Duplicate market_state_id rows: {duplicate_state_ids}")

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
                "event_window_count": int(frame["source_event_window_id"].nunique()),
                "valid_for_event_context_candidate_rows": int(frame["valid_for_event_context_candidate"].sum()),
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
            "microstructure_parquet": str(microstructure_parquet),
            "microstructure_manifest": str(microstructure_manifest),
            "event_windows_table": str(event_windows_path),
        },
        "source_hashes": {
            "microstructure_manifest_sha256": micro_manifest_sha,
            "event_windows_table_sha256": event_windows_sha,
        },
        "source_root_states": {
            "quotes_root_state": "provisional_d_legacy_recovery_root_pending_e_parity",
            "requires_rebuild_after_e_quotes_parity": True,
        },
        "contracts": REQUIRED_CONTRACTS,
        "validations": summary.iloc[0].to_dict(),
        "limitations": [
            "Controlled candidate only; not institutional market_state_table_v0_1.",
            "Built from microstructure v0.2 candidate windows; full_universe_claim=false.",
            "D:/quotes lineage is provisional through upstream microstructure component.",
            "No labels, rewards, strategy signals, actions, fills, PnL or outcomes are embedded.",
            "ML/RL/backtest/execution direct-use gates remain false.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def validate_market_state_row(row: dict[str, Any], config: dict[str, Any]) -> None:
    required_fields = [
        "market_state_id",
        "instrument_id",
        "ticker",
        "decision_timestamp_utc",
        "decision_date",
        "state_schema_version",
        "state_builder_version",
        "state_quality_state",
    ]
    for field in required_fields:
        if field not in row:
            raise FixtureValidationError(f"missing required market state field: {field}")

    validate_no_prohibited_keys(row, prohibited_prefixes(config))
    validate_required_flags(row, config.get("required_flags", {}))

    decision_timestamp = parse_utc(
        row["decision_timestamp_utc"], "decision_timestamp_utc"
    )
    assert decision_timestamp is not None
    for field, value in row.items():
        if not field.endswith("_as_of_utc"):
            continue
        component_timestamp = parse_utc(value, field)
        if component_timestamp is not None and component_timestamp > decision_timestamp:
            raise FixtureValidationError(
                f"{field} must be <= decision_timestamp_utc"
            )

    required_namespaces = config.get("required_feature_namespaces", [])
    for namespace in required_namespaces:
        namespace = str(namespace)
        component_state_field = f"{namespace.removesuffix('__')}_component_state"
        has_feature = any(key.startswith(namespace) for key in row)
        has_component_state = component_state_field in row
        if not has_feature and not has_component_state:
            raise FixtureValidationError(
                f"missing namespace or component state for {namespace}"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Skeleton guard and controlled-candidate builder for "
            "market_state_table_v0_1. This script does not materialize official "
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
        help="Write a controlled candidate market_state sample from microstructure v0.2.",
    )
    parser.add_argument("--microstructure-parquet", type=Path, default=DEFAULT_MICROSTRUCTURE_PARQUET)
    parser.add_argument("--microstructure-manifest", type=Path, default=DEFAULT_MICROSTRUCTURE_MANIFEST)
    parser.add_argument("--event-windows", type=Path, default=DEFAULT_EVENT_WINDOWS)
    parser.add_argument("--candidate-output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--candidate-dataset-dir-name", default=CANDIDATE_DATASET_DIR_NAME)
    parser.add_argument(
        "--candidate-manifest-name",
        default="_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json",
    )
    parser.add_argument(
        "--candidate-summary-name",
        default="_market_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv",
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
                "Required market_state_table_v0_1 contracts are missing; refusing "
                "candidate build."
            )
        manifest = materialize_market_state_candidate(
            microstructure_parquet=args.microstructure_parquet,
            microstructure_manifest=args.microstructure_manifest,
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
                "Required market_state_table_v0_1 contracts are missing; refusing "
                "fixture build."
            )
        if args.output_dir is None:
            raise SystemExit("--output-dir is required with --config")
        try:
            manifest = build_deterministic_fixture_sample(
                dataset_id=DATASET_ID,
                config_path=args.config,
                output_dir=args.output_dir,
                row_validator=validate_market_state_row,
            )
        except FixtureValidationError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    raise SystemExit(
        "market_state_table_v0_1 is contract-defined but not materialized. "
        "Use --contract-check-only for the current skeleton check, or --config "
        "--output-dir for deterministic fixture-only validation. Use "
        "--materialize-candidate for the controlled candidate sample. Official "
        "institutional materialization still requires promotion gates."
    )


if __name__ == "__main__":
    main()
