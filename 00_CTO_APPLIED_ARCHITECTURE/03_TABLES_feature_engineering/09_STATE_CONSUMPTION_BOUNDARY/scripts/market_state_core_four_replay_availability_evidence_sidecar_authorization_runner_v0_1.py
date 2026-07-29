from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
BOUNDARY = FEATURE_ROOT / "09_STATE_CONSUMPTION_BOUNDARY"
CONFIGS = BOUNDARY / "configs"
SCRIPTS = BOUNDARY / "scripts"
CHANGELOG = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"

GATE = "market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1"
STATUS = (
    "CLOSED_AUTHORIZED_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_EXECUTION_AND_VALIDATION_"
    "WITH_RESTRICTIONS_NO_PHYSICAL_READ"
)
NEXT_GATE = (
    "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1"
)

PREVIOUS_REGRESSION_READOUT = (
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_readout_v0_1.md"
)
PREVIOUS_REGRESSION_MATRIX = (
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_matrix_v0_1.json"
)
TIMESTAMP_CONTRACT = (
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_v0_1.json"
)
TIMESTAMP_MATRIX = (
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_matrix_v0_1.json"
)
CORE_FOUR_MATERIALIZATION_CONTRACT = (
    FEATURE_ROOT
    / "06_MARKET_STATE_INTEGRATION"
    / "core_four_market_state_materialization_design_contract_v0_1.json"
)
CORE_FOUR_PHYSICAL_VALIDATION_READOUT = (
    FEATURE_ROOT
    / "06_MARKET_STATE_INTEGRATION"
    / "core_four_market_state_candidate_physical_validation_readout_v0_1.md"
)

OUTPUTS = {
    "authorization": BOUNDARY
    / "market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1.md",
    "scope": CONFIGS
    / "market_state_core_four_replay_availability_evidence_sidecar_authorization_scope_v0_1.json",
    "contract": BOUNDARY
    / "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json",
    "matrix": BOUNDARY
    / "market_state_core_four_replay_availability_evidence_sidecar_authorization_matrix_v0_1.json",
    "readout": BOUNDARY
    / "market_state_core_four_replay_availability_evidence_sidecar_authorization_readout_v0_1.md",
}

REQUIRED_OBJECTS = [
    "trading_activity",
    "price_movement",
    "price_location_structure",
    "volatility_range_state",
]

REQUIRED_CASE_IDS = [
    "SIDE_AUTH_INPUTS_001",
    "SIDE_AUTH_PREVIOUS_BLOCK_001",
    "SIDE_AUTH_TIMESTAMP_CONTRACT_001",
    "SIDE_AUTH_PHYSICAL_IDENTITY_001",
    "SIDE_AUTH_CONTRACT_SCHEMA_COMPILE_001",
    "SIDE_AUTH_CONTRACT_GOOD_FIXTURE_001",
    "SIDE_AUTH_CONTRACT_MISSING_ROW_ID_BLOCKS_001",
    "SIDE_AUTH_CONTRACT_MISSING_AVAILABLE_AT_BLOCKS_001",
    "SIDE_AUTH_CONTRACT_CORE_FOUR_COMPONENTS_REQUIRED_001",
    "SIDE_AUTH_CONTRACT_NO_PRODUCTION_DOWNSTREAM_001",
    "SIDE_AUTH_NEXT_EXECUTION_SCOPE_001",
    "SIDE_AUTH_BOUNDARIES_001",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def zulu_schema() -> dict[str, Any]:
    return {
        "type": "string",
        "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$",
    }


def sha_schema() -> dict[str, Any]:
    return {"type": "string", "pattern": r"^[a-f0-9]{64}$"}


def duration_schema() -> dict[str, Any]:
    return {
        "type": "string",
        "pattern": r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$",
    }


def sidecar_contract() -> dict[str, Any]:
    component_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "component_id",
            "information_object_id",
            "source_timestamp_utc",
            "component_as_of_utc",
            "component_available_at_utc",
            "availability_status",
            "restriction_codes",
        ],
        "properties": {
            "component_id": {"type": "string", "minLength": 1},
            "information_object_id": {"type": "string", "enum": REQUIRED_OBJECTS},
            "source_timestamp_utc": zulu_schema(),
            "component_as_of_utc": zulu_schema(),
            "component_available_at_utc": zulu_schema(),
            "availability_status": {
                "type": "string",
                "enum": ["available", "research_only", "blocked"],
            },
            "restriction_codes": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "uniqueItems": True,
            },
        },
    }
    record_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "materialized_state_candidate_id",
            "source_candidate_record_id",
            "state_output_fingerprint",
            "candidate_dataset_id",
            "candidate_dataset_fingerprint",
            "instrument_id",
            "ticker",
            "session_date",
            "context_id",
            "profile_id",
            "physical_profile_id",
            "decision_timestamp_utc",
            "state_as_of_utc",
            "state_available_at_utc",
            "state_availability_policy_id",
            "state_publication_latency_policy_id",
            "state_publication_latency",
            "component_availability_evidence",
            "state_replay_consumption_legality",
            "restriction_codes",
        ],
        "properties": {
            "materialized_state_candidate_id": sha_schema(),
            "source_candidate_record_id": sha_schema(),
            "state_output_fingerprint": sha_schema(),
            "candidate_dataset_id": {"type": "string", "minLength": 1},
            "candidate_dataset_fingerprint": sha_schema(),
            "instrument_id": {"type": "string", "minLength": 1},
            "ticker": {"type": "string", "minLength": 1},
            "session_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "context_id": {"type": "string", "minLength": 1},
            "profile_id": {
                "const": "market_state_core_four_intraday_profile_v0_1"
            },
            "physical_profile_id": {"const": "core_four_market_state_profile_v0_1"},
            "decision_timestamp_utc": zulu_schema(),
            "state_as_of_utc": zulu_schema(),
            "state_available_at_utc": zulu_schema(),
            "state_availability_policy_id": {
                "const": "market_state_core_four_replay_availability_policy_v0_1"
            },
            "state_publication_latency_policy_id": {"type": "string", "minLength": 1},
            "state_publication_latency": duration_schema(),
            "component_availability_evidence": {
                "type": "array",
                "minItems": 4,
                "maxItems": 4,
                "items": component_schema,
            },
            "state_replay_consumption_legality": {
                "type": "string",
                "enum": ["decision_safe", "research_only", "blocked_temporal_legality"],
            },
            "restriction_codes": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "uniqueItems": True,
            },
        },
    }
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://tsis.local/schemas/"
            "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json"
        ),
        "title": "Market State Core Four Replay Availability Evidence Sidecar v0.1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "sidecar_id",
            "sidecar_schema_id",
            "created_at_utc",
            "state_kind",
            "profile_id",
            "physical_profile_id",
            "candidate_dataset_id",
            "candidate_dataset_fingerprint",
            "candidate_output_manifest_sha256",
            "candidate_parquet_sha256",
            "physical_schema_sha256",
            "source_lineage_manifest_sha256",
            "row_count",
            "records",
            "official_dataset",
            "production",
            "downstream",
            "backtest_consumption_authorized",
        ],
        "properties": {
            "sidecar_id": {"type": "string", "minLength": 1},
            "sidecar_schema_id": {
                "const": "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1"
            },
            "created_at_utc": zulu_schema(),
            "state_kind": {"const": "market_state"},
            "profile_id": {"const": "market_state_core_four_intraday_profile_v0_1"},
            "physical_profile_id": {"const": "core_four_market_state_profile_v0_1"},
            "candidate_dataset_id": {"type": "string", "minLength": 1},
            "candidate_dataset_fingerprint": sha_schema(),
            "candidate_output_manifest_sha256": sha_schema(),
            "candidate_parquet_sha256": sha_schema(),
            "physical_schema_sha256": sha_schema(),
            "source_lineage_manifest_sha256": sha_schema(),
            "row_count": {"type": "integer", "minimum": 1, "maximum": 8},
            "records": {
                "type": "array",
                "minItems": 1,
                "maxItems": 8,
                "items": record_schema,
            },
            "official_dataset": {"const": False},
            "production": {"const": False},
            "downstream": {"const": False},
            "backtest_consumption_authorized": {"const": False},
        },
    }
    return {
        "contract_id": "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1",
        "contract_version": "0.1",
        "status": "AUTHORIZED_SCHEMA_FOR_NEXT_EXECUTION_NOT_YET_MATERIALIZED",
        "owner_layer": "09_STATE_CONSUMPTION_BOUNDARY",
        "json_schema": schema,
        "semantic_validation_requirements": [
            "records.length == row_count",
            "materialized_state_candidate_id unique",
            "state_output_fingerprint unique",
            "one sidecar record per physical candidate row",
            "one physical candidate row per sidecar record",
            "component information_object_id set equals core four required objects",
            "state_as_of_utc = max(component_as_of_utc)",
            "state_available_at_utc = max(decision_timestamp_utc, component_available_at_utc) + state_publication_latency",
            "component restriction_codes subset of row restriction_codes",
            "component blocked or research_only prevents row decision_safe",
        ],
        "execution_boundaries": {
            "sidecar_materialized_by_this_contract": False,
            "parquet_modified": False,
            "market_state_recalculated": False,
            "StateReplayFeed_authorized": False,
            "backtest_authorized": False,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
    }


def good_sidecar() -> dict[str, Any]:
    record_id = "a" * 64
    fingerprint = "b" * 64
    dataset_fp = "c" * 64
    components = [
        {
            "component_id": f"component_{obj}_v0_1",
            "information_object_id": obj,
            "source_timestamp_utc": "2026-01-05T14:42:00Z",
            "component_as_of_utc": "2026-01-05T14:42:00Z",
            "component_available_at_utc": "2026-01-05T14:42:00Z",
            "availability_status": "available",
            "restriction_codes": ["candidate_runtime_only"],
        }
        for obj in REQUIRED_OBJECTS
    ]
    return {
        "sidecar_id": "market_state_core_four_replay_availability_evidence_sidecar_probe_v0_1",
        "sidecar_schema_id": "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1",
        "created_at_utc": "2026-01-05T14:42:00Z",
        "state_kind": "market_state",
        "profile_id": "market_state_core_four_intraday_profile_v0_1",
        "physical_profile_id": "core_four_market_state_profile_v0_1",
        "candidate_dataset_id": "core_four_market_state_candidate_v0_1",
        "candidate_dataset_fingerprint": dataset_fp,
        "candidate_output_manifest_sha256": "d" * 64,
        "candidate_parquet_sha256": "e" * 64,
        "physical_schema_sha256": "f" * 64,
        "source_lineage_manifest_sha256": "1" * 64,
        "row_count": 1,
        "records": [
            {
                "materialized_state_candidate_id": record_id,
                "source_candidate_record_id": "9" * 64,
                "state_output_fingerprint": fingerprint,
                "candidate_dataset_id": "core_four_market_state_candidate_v0_1",
                "candidate_dataset_fingerprint": dataset_fp,
                "instrument_id": "instrument_001",
                "ticker": "AAMC",
                "session_date": "2026-01-05",
                "context_id": "core_four_context_probe",
                "profile_id": "market_state_core_four_intraday_profile_v0_1",
                "physical_profile_id": "core_four_market_state_profile_v0_1",
                "decision_timestamp_utc": "2026-01-05T14:42:00Z",
                "state_as_of_utc": "2026-01-05T14:42:00Z",
                "state_available_at_utc": "2026-01-05T14:42:00Z",
                "state_availability_policy_id": "market_state_core_four_replay_availability_policy_v0_1",
                "state_publication_latency_policy_id": "zero_latency_candidate_replay_publication_policy_v0_1",
                "state_publication_latency": "PT0S",
                "component_availability_evidence": components,
                "state_replay_consumption_legality": "decision_safe",
                "restriction_codes": ["candidate_runtime_only"],
            }
        ],
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption_authorized": False,
    }


def validate_schema(schema: dict[str, Any], obj: dict[str, Any]) -> list[str]:
    if Draft202012Validator is None:
        return ["jsonschema_unavailable"]
    return [e.message for e in Draft202012Validator(schema).iter_errors(obj)]


def build_scope(now: str) -> dict[str, Any]:
    return {
        "gate": GATE,
        "created_at_utc": now,
        "status": "AUTHORIZED_NEXT_EXECUTION_SCOPE_NO_PHYSICAL_READ_IN_THIS_GATE",
        "owner_layer": "09_STATE_CONSUMPTION_BOUNDARY",
        "purpose": (
            "Authorize the next bounded execution-and-validation gate that will create a "
            "row-addressable replay availability evidence sidecar for the validated Market "
            "State core-four physical candidate."
        ),
        "authorized_next_gate": NEXT_GATE,
        "allowed_primary_inputs_for_next_gate": [
            "core-four source candidate records JSONL",
            "core-four materialization manifest",
            "core-four final manifest",
            "core-four physical validation evidence",
            "market_state_core_four_replay_availability_timestamp_contract_v0_1",
            "closed physical schema contract",
        ],
        "conditional_next_gate_physical_read_allowance": {
            "allowed": True,
            "only_if_metadata_inputs_do_not_expose_required_row_identity_fields": True,
            "exact_candidate_only": True,
            "max_parquet_files": 1,
            "max_rows": 8,
            "allowed_column_classes": [
                "row identity",
                "state output fingerprint",
                "decision timestamp",
                "restriction lineage JSON",
                "source lineage JSON",
                "policy/formula lineage JSON",
            ],
            "forbidden_column_classes": [
                "scientific value columns used as strategy inputs",
                "future outcomes",
                "execution prices",
                "fills",
                "PnL",
                "downstream projections",
            ],
        },
        "hard_boundaries_this_gate": {
            "sidecar_records_written": 0,
            "parquet_opened": False,
            "state_rows_read": 0,
            "StateReplayFeed_records_emitted": 0,
            "runtime_requests_executed": 0,
            "runtime_builds_executed": 0,
            "datasets_written": 0,
            "registry_mutations": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
            "backtest_consumption": False,
        },
        "authorized_outputs": {
            **{k: rel(v) for k, v in OUTPUTS.items()},
            "runner": rel(SCRIPTS / "market_state_core_four_replay_availability_evidence_sidecar_authorization_runner_v0_1.py"),
        },
    }


def build_matrix(now: str, contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def row(case_id: str, area: str, expected: str, observed: str, result: str, refs: list[str]) -> None:
        rows.append(
            {
                "case_id": case_id,
                "area": area,
                "expected": expected,
                "observed": observed,
                "result": result,
                "evidence_refs": refs,
            }
        )

    inputs = [
        PREVIOUS_REGRESSION_READOUT,
        PREVIOUS_REGRESSION_MATRIX,
        TIMESTAMP_CONTRACT,
        TIMESTAMP_MATRIX,
        CORE_FOUR_MATERIALIZATION_CONTRACT,
        CORE_FOUR_PHYSICAL_VALIDATION_READOUT,
    ]
    missing = [rel(p) for p in inputs if not p.exists()]
    row("SIDE_AUTH_INPUTS_001", "input_inventory", "Required prior evidence is present.", f"missing={missing}", "PASS" if not missing else "BLOCK", [rel(p) for p in inputs if p.exists()])

    previous = read_text(PREVIOUS_REGRESSION_READOUT)
    previous_block = (
        "CLOSED_BLOCKED_REQUIRES_ROW_ADDRESSABLE_REPLAY_AVAILABILITY_EVIDENCE_NO_PHYSICAL_READ"
        in previous
    )
    row("SIDE_AUTH_PREVIOUS_BLOCK_001", "previous_block", "Previous gate blocked exactly on missing row-addressable replay evidence.", f"previous_block={previous_block}", "PASS" if previous_block else "BLOCK", [rel(PREVIOUS_REGRESSION_READOUT)])

    timestamp_matrix = read_json(TIMESTAMP_MATRIX)
    timestamp_ok = timestamp_matrix.get("case_count") == 30 and timestamp_matrix.get("failed_cases") == 0
    row("SIDE_AUTH_TIMESTAMP_CONTRACT_001", "timestamp_contract", "Timestamp contract is closed and validation hardened.", f"case_count={timestamp_matrix.get('case_count')}; failed_cases={timestamp_matrix.get('failed_cases')}", "PASS" if timestamp_ok else "BLOCK", [rel(TIMESTAMP_MATRIX), rel(TIMESTAMP_CONTRACT)])

    materialization = read_json(CORE_FOUR_MATERIALIZATION_CONTRACT)
    validation_text = read_text(CORE_FOUR_PHYSICAL_VALIDATION_READOUT)
    fields = set(materialization.get("physical_schema", {}).get("required_identity_fields", []))
    lineage = set(materialization.get("physical_schema", {}).get("required_lineage_fields", []))
    identity_ok = {"materialized_state_candidate_id", "instrument_id", "decision_timestamp_utc"}.issubset(fields) and "state_output_fingerprint" in lineage
    validation_ok = all(
        token in validation_text
        for token in [
            "output_physical_rows = 8",
            "state_output_fingerprint_matches = 8",
            "materialized_state_candidate_id_matches = 8",
        ]
    )
    row("SIDE_AUTH_PHYSICAL_IDENTITY_001", "physical_identity", "Validated core-four physical candidate has row identity and fingerprint evidence.", f"identity_ok={identity_ok}; validation_ok={validation_ok}", "PASS" if identity_ok and validation_ok else "BLOCK", [rel(CORE_FOUR_MATERIALIZATION_CONTRACT), rel(CORE_FOUR_PHYSICAL_VALIDATION_READOUT)])

    schema = contract["json_schema"]
    if Draft202012Validator is None:
        compile_ok = False
        compile_note = "jsonschema_unavailable"
    else:
        try:
            Draft202012Validator.check_schema(schema)
            compile_ok = True
            compile_note = "compiled"
        except Exception as exc:
            compile_ok = False
            compile_note = str(exc)
    row("SIDE_AUTH_CONTRACT_SCHEMA_COMPILE_001", "contract_schema", "Sidecar JSON Schema compiles under Draft 2020-12.", compile_note, "PASS" if compile_ok else "BLOCK", [rel(OUTPUTS["contract"])])

    good = good_sidecar()
    good_errors = validate_schema(schema, good)
    row("SIDE_AUTH_CONTRACT_GOOD_FIXTURE_001", "contract_schema", "Positive sidecar fixture validates.", f"errors={good_errors}", "PASS" if not good_errors else "BLOCK", [rel(OUTPUTS["contract"])])

    missing_row = json.loads(json.dumps(good))
    del missing_row["records"][0]["materialized_state_candidate_id"]
    row("SIDE_AUTH_CONTRACT_MISSING_ROW_ID_BLOCKS_001", "contract_schema", "Missing physical row id is blocked.", f"errors={validate_schema(schema, missing_row)}", "PASS" if validate_schema(schema, missing_row) else "BLOCK", [rel(OUTPUTS["contract"])])

    missing_available = json.loads(json.dumps(good))
    del missing_available["records"][0]["state_available_at_utc"]
    row("SIDE_AUTH_CONTRACT_MISSING_AVAILABLE_AT_BLOCKS_001", "contract_schema", "Missing available-at timestamp is blocked.", f"errors={validate_schema(schema, missing_available)}", "PASS" if validate_schema(schema, missing_available) else "BLOCK", [rel(OUTPUTS["contract"])])

    missing_object = json.loads(json.dumps(good))
    missing_object["records"][0]["component_availability_evidence"].pop()
    row("SIDE_AUTH_CONTRACT_CORE_FOUR_COMPONENTS_REQUIRED_001", "contract_schema", "Exactly four component availability records are required.", f"errors={validate_schema(schema, missing_object)}", "PASS" if validate_schema(schema, missing_object) else "BLOCK", [rel(OUTPUTS["contract"])])

    production = json.loads(json.dumps(good))
    production["production"] = True
    production["downstream"] = True
    row("SIDE_AUTH_CONTRACT_NO_PRODUCTION_DOWNSTREAM_001", "contract_schema", "Sidecar cannot authorize production or downstream.", f"errors={validate_schema(schema, production)}", "PASS" if validate_schema(schema, production) else "BLOCK", [rel(OUTPUTS["contract"])])

    scope = build_scope(now)
    next_scope_ok = (
        scope["authorized_next_gate"] == NEXT_GATE
        and scope["conditional_next_gate_physical_read_allowance"]["max_rows"] == 8
        and scope["hard_boundaries_this_gate"]["parquet_opened"] is False
    )
    row("SIDE_AUTH_NEXT_EXECUTION_SCOPE_001", "next_execution_scope", "Next execution-and-validation scope is bounded and exact-candidate only.", json.dumps(scope["conditional_next_gate_physical_read_allowance"], sort_keys=True), "PASS" if next_scope_ok else "BLOCK", [])

    row("SIDE_AUTH_BOUNDARIES_001", "hard_boundaries", "This authorization gate writes no sidecar records and opens no physical data.", "sidecar_records_written=0; parquet_opened=false; state_rows_read=0; StateReplayFeed=0; backtest=false", "PASS", [])

    ids = [r["case_id"] for r in rows]
    blocking = [r for r in rows if r["result"] == "BLOCK"]
    return {
        "gate": GATE,
        "created_at_utc": now,
        "status": STATUS if not blocking else "BLOCKED_AUTHORIZATION_PREREQUISITE_FAILURE",
        "case_count": len(rows),
        "failed_cases": len(blocking),
        "missing_required_case_ids": sorted(set(REQUIRED_CASE_IDS) - set(ids)),
        "duplicate_case_ids": sorted({case_id for case_id in ids if ids.count(case_id) > 1}),
        "unexpected_case_ids": sorted(set(ids) - set(REQUIRED_CASE_IDS)),
        "sidecar_records_written": 0,
        "parquet_opened": False,
        "state_rows_read": 0,
        "StateReplayFeed_records_emitted": 0,
        "runtime_requests_executed": 0,
        "runtime_builds_executed": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption": False,
        "next_gate": NEXT_GATE,
        "rows": rows,
    }


def render_authorization() -> str:
    return f"""# Market State Core Four Replay Availability Evidence Sidecar Authorization v0.1

Gate: `{GATE}`
Date: `2026-07-29`
Status: `{STATUS}`

## Purpose

Authorize the next bounded execution-and-validation gate to create row-addressable replay availability evidence for the already validated Market State core-four physical candidate.

This authorization exists because the prior runtime interface regression correctly blocked before v0.1.2 reissue:

```text
physical row identity
↔
state_as_of_utc / state_available_at_utc
=
not yet bound one-to-one
```

## Authorized Next Gate

```text
{NEXT_GATE}
```

The next gate may create and validate the sidecar. This authorization gate itself creates no sidecar records and opens no physical data.

## Required Sidecar Fields

```text
materialized_state_candidate_id
state_output_fingerprint
candidate_dataset_id
candidate_dataset_fingerprint
instrument_id
profile_id
physical_profile_id
decision_timestamp_utc
state_as_of_utc
state_available_at_utc
state_availability_policy_id
state_publication_latency_policy_id
state_publication_latency
component_availability_evidence
state_replay_consumption_legality
restriction_codes
```

## Boundaries

```text
sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
backtest_consumption = false
official_dataset = false
production = false
downstream = false
```
"""


def render_readout(matrix: dict[str, Any]) -> str:
    return f"""# Market State Core Four Replay Availability Evidence Sidecar Authorization Readout v0.1

Gate: `{GATE}`
Date: `2026-07-29`
Status: `{matrix['status']}`

## Result

```text
case_count = {matrix['case_count']}
failed_cases = {matrix['failed_cases']}
missing_required_case_ids = {len(matrix['missing_required_case_ids'])}
duplicate_case_ids = {len(matrix['duplicate_case_ids'])}
unexpected_case_ids = {len(matrix['unexpected_case_ids'])}

sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
production = false
downstream = false
official_dataset = false
```

## Decision

The sidecar execution-and-validation gate is authorized with restrictions. It must create a row-addressable sidecar or envelope that binds every physical Market State core-four candidate row to replay availability evidence.

If metadata inputs already expose all row identities and fingerprints, the next gate should not open parquet. If they do not, the next gate may authorize only a bounded read of the exact validated candidate parquet for identity/fingerprint/lineage fields, with max rows = 8 and max files = 1.

## Next Gate

```text
{NEXT_GATE}
```

Still not authorized:

```text
StateReplayFeed
backtest consumption
strategy execution
production
downstream
official dataset promotion
```
"""


def prepend_once(path: Path, title: str, block: str) -> None:
    text = read_text(path) if path.exists() else ""
    if title in text:
        return
    write_text(path, block.rstrip() + "\n\n" + text.rstrip() + "\n")


def fix_route_newline_residue() -> None:
    path = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    text = read_text(path)
    text = text.replace(
        "current_gate_at_closure`n=`nruntime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending",
        "current_gate_at_closure\n=\nruntime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending",
    )
    write_text(path, text)


def update_live_docs(matrix: dict[str, Any]) -> None:
    fix_route_newline_residue()
    route_title = "Market State Core Four Replay Availability Evidence Sidecar Authorization v0.1 Closed - 2026-07-29"
    route_block = f"""## {route_title}

```text
{GATE}
=
{matrix['status']}

current_gate
=
{NEXT_GATE}_pending

sidecar_records_written
=
0

physical_read_authorization_ready
=
false

StateReplayFeed
=
NOT_AUTHORIZED
```

The next gate may create and validate a row-addressable replay availability sidecar for the exact validated Market State core-four candidate. This gate does not create the sidecar and does not open physical replay.
"""
    prepend_once(FEATURE_ROOT / "99_ruta_de_trabajo.md", route_title, route_block)

    agent_title = "Current Runtime Handoff Override - Replay Availability Sidecar Authorization Closed"
    agent_block = f"""# {agent_title}

Status: `agent_handoff_prompt_v0_147`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`

```text
last_closed_gate = {GATE}
last_closed_status = {matrix['status']}
current_gate = {NEXT_GATE}_pending
sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next gate must create and validate the sidecar/envelope before any physical evidence alignment retry.
"""
    prepend_once(FEATURE_ROOT / "AGENT.md", agent_title, agent_block)

    boundary_title = "Market State Core Four Replay Availability Evidence Sidecar Authorization v0.1"
    boundary_block = f"""## {boundary_title}

```text
{GATE} = {matrix['status']}
current_gate = {NEXT_GATE}_pending
sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
```

The next execution-and-validation gate must produce the row-addressable replay availability sidecar or block fail-closed.
"""
    prepend_once(BOUNDARY / "README.md", boundary_title, boundary_block)

    runtime_title = "Replay Availability Evidence Sidecar Authorization v0.1"
    runtime_block = f"""## {runtime_title}

```text
{GATE} = {matrix['status']}
next_gate = {NEXT_GATE}
```

Runtime provider v0.1.2 remains frozen. The next work is a shared-boundary sidecar execution-and-validation gate; no runtime build, StateReplayFeed, backtest or downstream consumption is authorized.
"""
    prepend_once(RUNTIME / "README.md", runtime_title, runtime_block)

    changelog_title = "## 2026-07-29 - Replay availability sidecar authorization closed"
    changelog_block = f"""{changelog_title}

- Closed `{GATE}` as `{matrix['status']}`.
- Authorized the next bounded sidecar execution-and-validation gate for row-addressable Market State core-four replay availability evidence.
- Preserved sidecar records written = 0, parquet opened = false, state rows read = 0, `StateReplayFeed = NOT_AUTHORIZED`, production = false and downstream = false.
- Next gate is `{NEXT_GATE}`.
"""
    prepend_once(CHANGELOG, changelog_title, changelog_block)


def package_files(stamp: str) -> Path:
    files = [
        OUTPUTS["authorization"],
        OUTPUTS["scope"],
        OUTPUTS["contract"],
        OUTPUTS["matrix"],
        OUTPUTS["readout"],
        SCRIPTS / "market_state_core_four_replay_availability_evidence_sidecar_authorization_runner_v0_1.py",
        FEATURE_ROOT / "99_ruta_de_trabajo.md",
        FEATURE_ROOT / "AGENT.md",
        RUNTIME / "README.md",
        BOUNDARY / "README.md",
        CHANGELOG,
    ]
    entries = [
        {"path": rel(p), "sha256": sha256_file(p), "size_bytes": p.stat().st_size}
        for p in files
        if p.exists()
    ]
    manifest = {
        "package_id": "market_state_core_four_replay_availability_evidence_sidecar_authorization_files",
        "created_at_utc": stamp,
        "gate": GATE,
        "file_count": len(entries),
        "artifacts": entries,
        "explicitly_excluded": [
            "02_TSIS_BACKTEST_ENGINE",
            "parquet files",
            "StateReplayFeed implementation",
            "backtest runs",
            "downstream row delivery artifacts",
        ],
    }
    zip_path = FEATURE_ROOT / f"{GATE}_files_{stamp.replace(':', '').replace('-', '')}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for entry in entries:
            zf.write(ROOT / entry["path"], entry["path"])
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-live-docs", action="store_true")
    parser.add_argument("--zip", action="store_true")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    contract = sidecar_contract()
    write_json(OUTPUTS["contract"], contract)
    scope = build_scope(now)
    matrix = build_matrix(now, contract)

    write_text(OUTPUTS["authorization"], render_authorization())
    write_json(OUTPUTS["scope"], scope)
    write_json(OUTPUTS["matrix"], matrix)
    write_text(OUTPUTS["readout"], render_readout(matrix))

    if args.update_live_docs and matrix["failed_cases"] == 0:
        update_live_docs(matrix)

    zip_path = package_files(now) if args.zip else None
    print(
        json.dumps(
            {
                "gate": GATE,
                "status": matrix["status"],
                "case_count": matrix["case_count"],
                "failed_cases": matrix["failed_cases"],
                "next_gate": NEXT_GATE,
                "update_live_docs": args.update_live_docs and matrix["failed_cases"] == 0,
                "zip_path": str(zip_path) if zip_path else None,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if matrix["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
