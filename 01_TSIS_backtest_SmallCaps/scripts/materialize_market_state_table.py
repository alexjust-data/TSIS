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


DATASET_ID = "market_state_table_v0_1"
STATUS = "contract_defined_not_materialized"

MODULE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CONTRACTS = {
    "composition_contract": "01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md",
    "build_loop_runbook": "01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md",
    "schema": "01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/market_state_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml",
    "validators": "01_foundations/validators/outputs/market_state_table_validators.md",
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
            "Skeleton guard for market_state_table_v0_1. This script does not "
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
        "--output-dir for deterministic fixture-only validation. Official "
        "materialization still requires validated config, schema, validators, "
        "tests and manifest policy."
    )


if __name__ == "__main__":
    main()
