from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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

MODULE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CONTRACTS = {
    "composition_contract": "01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "build_loop_runbook": "01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "schema": "01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/event_state_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml",
    "validators": "01_foundations/validators/outputs/event_state_table_validators.md",
}


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
        "fixture_builder_implemented": True,
        "writes_output": False,
        "official_output_writes": False,
        "required_contracts": paths,
        "missing_contracts": [
            name for name, item in paths.items() if not bool(item["exists"])
        ],
    }


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
            "Skeleton guard for event_state_table_v0_1. This script does not "
            "materialize official output yet."
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    status = contract_status()
    if args.contract_check_only:
        print(json.dumps(status, indent=2, sort_keys=True))
        if status["missing_contracts"]:
            raise SystemExit(1)
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
        "--output-dir for deterministic fixture-only validation. Official "
        "materialization still requires validated config, schema, validators, "
        "tests and manifest policy."
    )


if __name__ == "__main__":
    main()
