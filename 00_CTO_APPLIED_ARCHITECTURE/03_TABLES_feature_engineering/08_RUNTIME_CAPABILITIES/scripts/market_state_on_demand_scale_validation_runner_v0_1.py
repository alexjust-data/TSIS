from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


SCRIPT_VERSION = "market_state_on_demand_scale_validation_runner_v0_1"
GATE_ID = "market_state_on_demand_scale_validation_v0_1"
BASE = Path(__file__).resolve().parents[1]
FEATURE_ROOT = BASE.parent
MARKET_ROOT = FEATURE_ROOT / "06_MARKET_STATE_INTEGRATION"
OUTPUT_ROOT = BASE / "runs"

BOUNDED_RUNNER_PATH = BASE / "scripts" / "market_state_bounded_on_demand_execution_runner_v0_1.py"
SOURCE_SCOPE_PATH = MARKET_ROOT / "configs" / "experimental_core_four_market_state_scale_c_candidate_materialization_scope_v0_1.json"
PROFILE_ROOT = MARKET_ROOT / "official_profiles" / "market_state_core_four_intraday_profile_v0_1"
PROFILE_MANIFEST_PATH = PROFILE_ROOT / "PROFILE_MANIFEST.json"
PROFILE_SCHEMA_PATH = PROFILE_ROOT / "PHYSICAL_SCHEMA_CONTRACT.json"

AUTH_SCOPE_PATH = BASE / "configs" / "market_state_on_demand_scale_validation_scope_v0_1.json"
AUTH_CONTRACT_PATH = BASE / "market_state_on_demand_scale_validation_contract_v0_1.json"
AUTH_MD_PATH = BASE / "market_state_on_demand_scale_validation_authorization_v0_1.md"
AUTH_READOUT_PATH = BASE / "market_state_on_demand_scale_validation_authorization_readout_v0_1.md"

REQUEST_CONTRACT_PATH = BASE / "market_state_request_contract_v0_1.json"
EXECUTION_PLAN_CONTRACT_PATH = BASE / "market_state_execution_plan_contract_v0_1.json"
MATERIALIZER_CONTRACT_PATH = BASE / "market_state_materializer_contract_v0_1.json"
VALIDATOR_CONTRACT_PATH = BASE / "market_state_validator_contract_v0_1.json"
REGISTRY_CONTRACT_PATH = BASE / "market_state_candidate_dataset_registry_contract_v0_1.json"

LINEAGE_CHAIN_LEDGER_PATH = BASE / "incremental_lineage_chain_ledger_v0_1.json"
LINEAGE_CHAIN_MATRIX_PATH = BASE / "market_state_on_demand_incremental_lineage_chain_validation_matrix_v0_1.json"
BASELINE_PARQUET = OUTPUT_ROOT / "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z" / "market_state_bounded_on_demand_candidate_v0_1.parquet"
DELTA1_PARQUET = OUTPUT_ROOT / "market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z" / "market_state_incremental_delta_candidate_v0_1.parquet"
DELTA2_PARQUET = OUTPUT_ROOT / "market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103901Z" / "market_state_second_generation_delta_candidate_v0_1.parquet"
SECOND_GEN_FINAL_MANIFEST = OUTPUT_ROOT / "market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103901Z" / "final_manifest.json"


class ScaleValidationError(RuntimeError):
    pass


def load_bounded_runner() -> Any:
    spec = importlib.util.spec_from_file_location("bounded_market_state_runner", BOUNDED_RUNNER_PATH)
    if not spec or not spec.loader:
        raise ScaleValidationError(f"Cannot import bounded runner: {BOUNDED_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bounded = load_bounded_runner()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def hash_excluding(payload: dict[str, Any], excluded_key: str) -> str:
    return sha256_payload({k: v for k, v in payload.items() if k != excluded_key})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ScaleValidationError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def require_file(path: Path) -> None:
    if not path.exists():
        raise ScaleValidationError(f"Required file missing: {path}")


def context_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row["instrument_id"]), str(row["session_date"]), str(row["decision_timestamp_utc"]))


def normalized_context_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row["instrument_id"]),
        bounded.normalize(row["session_date"]),
        bounded.normalize(row["decision_timestamp_utc"]),
    )


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def make_logical_partition_id(profile_id: str, row: dict[str, Any]) -> str:
    return sha256_payload(
        {
            "profile_id": profile_id,
            "instrument_id": row["instrument_id"],
            "session_date": row["session_date"],
            "decision_timestamp_utc": row["decision_timestamp_utc"],
        }
    )


def write_authorization_artifacts(run_id: str, consumed_at: str) -> str:
    scope = {
        "scope_id": "market_state_on_demand_scale_validation_scope_v0_1",
        "gate": GATE_ID,
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RUN",
        "consumed_by_run_id": run_id,
        "consumed_at_utc": consumed_at,
        "source_authority": {
            "candidate_source_scope": str(SOURCE_SCOPE_PATH),
            "lineage_chain_validation": str(LINEAGE_CHAIN_MATRIX_PATH),
            "lineage_chain_ledger": str(LINEAGE_CHAIN_LEDGER_PATH),
        },
        "bounded_scale": {
            "source_surface": "Scale C integrated Market State candidate context surface",
            "requested_contexts": 120,
            "expected_reusable_validated_contexts": 14,
            "expected_to_build_scale_delta_contexts": 90,
            "expected_unavailable_contexts": 16,
            "expected_represented_contexts": 104,
            "expected_instruments": 10,
            "expected_sessions": 8,
        },
        "authority": {
            "source_market_data_reads_allowed": False,
            "candidate_record_reads_allowed": True,
            "prior_candidate_parquet_reads_allowed": True,
            "scale_candidate_parquet_write_allowed": True,
            "candidate_registry_entry_write_allowed": True,
            "full_universe_execution_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_consumption_allowed": False,
            "event_state_on_demand_allowed": False,
        },
        "limits": {
            "maximum_requested_contexts": 120,
            "maximum_reusable_validated_contexts": 14,
            "maximum_delta_to_build_contexts": 90,
            "maximum_unavailable_contexts": 16,
            "maximum_source_candidate_records_read": 104,
            "maximum_source_market_data_rows_read": 0,
            "maximum_candidate_parquet_files_written": 1,
            "maximum_candidate_rows_written": 104,
            "maximum_output_bytes": 16000000,
        },
    }
    contract = {
        "contract_id": "market_state_on_demand_scale_validation_contract_v0_1",
        "gate": GATE_ID,
        "contract_status": "accepted_for_bounded_scale_validation_run",
        "consumed_by_run_id": run_id,
        "required_invariants": {
            "requested_contexts": 120,
            "represented_contexts": 104,
            "reusable_validated_contexts": 14,
            "scale_delta_materialized_contexts": 90,
            "unavailable_contexts": 16,
            "unaccounted_contexts": 0,
            "source_market_data_rows_read": 0,
            "candidate_parquet_files_written": 1,
            "candidate_registry_entries_written": 1,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "partition_accounting": "requested = reusable_validated + to_build_scale_delta + unavailable",
        "reuse_policy": "reuse_incremental_lineage_chain_validated_contexts_and_build_scale_delta_only",
        "next_gate_on_pass": "market_state_on_demand_capability_promotion_review_v0_1",
    }
    contract["contract_content_sha256_excluding_hash_field"] = hash_excluding(contract, "contract_content_sha256_excluding_hash_field")

    auth_md = f"""# Market State On-Demand Scale Validation Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RUN`
Date: `2026-07-27`

```text
gate = {GATE_ID}
consumed_by_run_id = {run_id}
consumed_at_utc = {consumed_at}
requested_contexts = 120
expected_reusable_validated_contexts = 14
expected_scale_delta_to_build_contexts = 90
expected_unavailable_contexts = 16
source_market_data_reads_allowed = false
full_universe_execution_allowed = false
official_dataset_promotion_allowed = false
production = false
downstream = false
```
"""
    auth_readout = f"""# Market State On-Demand Scale Validation Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RUN`
Date: `2026-07-27`

```text
gate = {GATE_ID}
consumed_by_run_id = {run_id}
contract_content_sha256_excluding_hash_field = {contract['contract_content_sha256_excluding_hash_field']}
next_allowed_gate = {GATE_ID}
```

This authorization is consumed by one bounded scale validation run. It does not
authorize full-universe generation, official dataset promotion, production or
downstream consumption.
"""
    write_json(AUTH_SCOPE_PATH, scope)
    write_json(AUTH_CONTRACT_PATH, contract)
    AUTH_MD_PATH.write_text(auth_md, encoding="utf-8")
    AUTH_READOUT_PATH.write_text(auth_readout, encoding="utf-8")
    return contract["contract_content_sha256_excluding_hash_field"]


def main() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    for path in [
        BOUNDED_RUNNER_PATH,
        REQUEST_CONTRACT_PATH,
        EXECUTION_PLAN_CONTRACT_PATH,
        MATERIALIZER_CONTRACT_PATH,
        VALIDATOR_CONTRACT_PATH,
        REGISTRY_CONTRACT_PATH,
        SOURCE_SCOPE_PATH,
        PROFILE_MANIFEST_PATH,
        PROFILE_SCHEMA_PATH,
        LINEAGE_CHAIN_LEDGER_PATH,
        LINEAGE_CHAIN_MATRIX_PATH,
        BASELINE_PARQUET,
        DELTA1_PARQUET,
        DELTA2_PARQUET,
        SECOND_GEN_FINAL_MANIFEST,
    ]:
        require_file(path)

    run_id = f"{GATE_ID}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists():
        raise ScaleValidationError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    started_at = utc_now()
    contract_hash = write_authorization_artifacts(run_id, started_at)

    source_scope = read_json(SOURCE_SCOPE_PATH)
    profile_manifest = read_json(PROFILE_MANIFEST_PATH)
    schema_contract = read_json(PROFILE_SCHEMA_PATH)
    validator_contract = read_json(VALIDATOR_CONTRACT_PATH)
    lineage_chain = read_json(LINEAGE_CHAIN_LEDGER_PATH)

    source_records_path = (SOURCE_SCOPE_PATH.parent / source_scope["input_artifacts"]["market_state_candidate_records"]).resolve()
    context_report_path = (SOURCE_SCOPE_PATH.parent / source_scope["input_artifacts"]["integration_context_report"]).resolve()
    source_records = read_jsonl(source_records_path)
    context_rows = read_csv_rows(context_report_path)
    source_records_by_key = {context_key(row): row for row in source_records}
    if len(source_records) != 104 or len(context_rows) != 120:
        raise ScaleValidationError("Unexpected Scale C source counts")

    profile_id = "market_state_core_four_intraday_profile_v0_1"
    schema_version = schema_contract["state_schema_version"]
    column_order, column_defs, arrow_schema = bounded.schema_from_contract(schema_contract)
    request_template = {
        "request_type": "market_state",
        "request_contract_version": "market_state_request_contract_v0_1",
        "profile_id": profile_id,
        "profile_version": "v0_1",
        "profile_version_policy": "exact",
        "resolution": "1m",
        "grain": "instrument_decision_timestamp",
        "universe_definition_id": "scale_c_integration_context_surface_v0_1",
        "explicit_instrument_ids": sorted({row["instrument_id"] for row in context_rows}),
        "session_dates": sorted({row["session_date"] for row in context_rows}),
        "exchange_scope": ["XNYS"],
        "calendar_authority_id": "governed_exchange_session_calendar_xnys_v0_1",
        "point_in_time_policy_id": "scale_c_context_surface_not_revalidated_v0_1",
        "source_version_policy": "exact_governed_or_block",
        "output_mode": "candidate_scale_validation",
        "output_format": "parquet_scale_candidate_plus_lineage_ledger",
        "reuse_policy": "reuse_incremental_lineage_chain_validated_contexts_and_build_scale_delta_only",
        "validation_level": "bounded_scale_validation",
        "requested_context_count": len(context_rows),
    }
    request_fingerprint = sha256_payload(request_template)
    request = {
        "request_id": "market_state_request_scale_validation_v0_1_" + request_fingerprint[:16],
        "request_status": "accepted_for_scale_validation_resolution",
        "requested_at_utc": utc_now(),
        "requested_by": os.environ.get("USERNAME") or os.environ.get("USER"),
        "request_purpose": "bounded_scale_validation_probe",
        **request_template,
        "request_fingerprint": request_fingerprint,
    }
    write_json(run_dir / "request_record.json", request)

    profile_resolution = {
        "resolution_status": "RESOLVED_EXACTLY_ONE",
        "resolved_profile_id": profile_id,
        "resolved_profile_version": "v0_1",
        "profile_manifest": str(PROFILE_MANIFEST_PATH),
        "profile_manifest_sha256": sha256_file(PROFILE_MANIFEST_PATH),
        "schema_contract": str(PROFILE_SCHEMA_PATH),
        "schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
        "expected_state_schema_version": schema_version,
        "expected_grain": request["grain"],
        "required_source_aliases": ["scale_c_integrated_market_state_candidate_records"],
        "profile_artifact_validation_run": profile_manifest.get("artifact_validation_run_id"),
    }
    resolved_profile_fingerprint = sha256_payload(profile_resolution)
    write_json(run_dir / "profile_resolution_report.json", profile_resolution)

    universe_resolution = {
        "resolution_status": "RESOLVED_SCALE_C_CONTEXT_SURFACE",
        "resolved_universe_definition_id": request["universe_definition_id"],
        "resolved_instrument_count": len(set(row["instrument_id"] for row in context_rows)),
        "resolved_session_count": len(set(row["session_date"] for row in context_rows)),
        "resolved_instrument_session_context_count": len(context_rows),
        "contexts": [
            {
                "context_id": row["context_id"],
                "instrument_id": row["instrument_id"],
                "ticker_label_non_authoritative": row["ticker"],
                "session_date": row["session_date"],
                "exchange_id": "XNYS",
                "decision_timestamp_utc": row["decision_timestamp_utc"],
                "membership_status": "AUTHORIZED_SCALE_C_CONTEXT_SURFACE",
            }
            for row in sorted(context_rows, key=lambda x: x["context_id"])
        ],
    }
    resolved_universe_fingerprint = sha256_payload(universe_resolution)
    write_json(run_dir / "universe_resolution_report.json", universe_resolution)

    source_resolution = {
        "resolution_status": "RESOLVED_EXACTLY_ONE",
        "resolved_source_alias": "scale_c_integrated_market_state_candidate_records",
        "source_records_path": str(source_records_path),
        "source_records_sha256": sha256_file(source_records_path),
        "context_report_path": str(context_report_path),
        "context_report_sha256": sha256_file(context_report_path),
        "source_candidate_records_read": len(source_records),
        "source_context_records_read": len(context_rows),
        "source_market_data_rows_read": 0,
        "source_scope_contract": str(SOURCE_SCOPE_PATH),
        "source_scope_contract_sha256": sha256_file(SOURCE_SCOPE_PATH),
    }
    resolved_source_set_fingerprint = sha256_payload(source_resolution)
    write_json(run_dir / "source_resolution_report.json", source_resolution)

    reusable_keys = {
        context_key(entry)
        for entry in lineage_chain["entries"]
        if entry.get("expanded_origin_mode") in {"baseline_origin", "delta1_origin", "delta2_origin"}
    }
    if len(reusable_keys) != 14:
        raise ScaleValidationError(f"Expected 14 reusable lineage keys, found {len(reusable_keys)}")

    reusable_rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    for parquet_path in [BASELINE_PARQUET, DELTA1_PARQUET, DELTA2_PARQUET]:
        for row in pq.read_table(parquet_path).to_pylist():
            key = normalized_context_key(row)
            if key in reusable_keys:
                reusable_rows[key] = row
    if set(reusable_rows) != reusable_keys:
        raise ScaleValidationError("Reusable physical rows do not match lineage-chain keys")

    partition_rows: list[dict[str, Any]] = []
    physical_rows: list[dict[str, Any]] = []
    lineage_rows: list[dict[str, Any]] = []
    unavailable_rows: list[dict[str, Any]] = []
    disposition_counts: Counter[str] = Counter()

    for ctx in sorted(context_rows, key=lambda x: x["context_id"]):
        key = context_key(ctx)
        base = {
            "context_id": ctx["context_id"],
            "instrument_id": ctx["instrument_id"],
            "ticker_label_non_authoritative": ctx["ticker"],
            "session_date": ctx["session_date"],
            "exchange_id": "XNYS",
            "decision_timestamp_utc": ctx["decision_timestamp_utc"],
            "decision_case": ctx["decision_case"],
            "logical_partition_id": make_logical_partition_id(profile_id, ctx),
            "context_input_fingerprint": ctx["context_input_fingerprint"],
        }
        if key in reusable_keys:
            disposition = "reusable_validated"
            cause = "represented_by_validated_incremental_lineage_chain"
            row = reusable_rows[key]
            physical_rows.append(row)
            lineage_rows.append({**base, "origin_mode": "reused_from_incremental_lineage_chain", "state_output_fingerprint": row["state_output_fingerprint"], "materialized_state_candidate_id": row["materialized_state_candidate_id"]})
        elif ctx["integration_status"] == "INTEGRABLE_COMPLETE_WITH_RESTRICTIONS":
            disposition = "to_build_scale_delta"
            cause = "integrable_scale_c_candidate_not_previously_represented"
            record = source_records_by_key.get(key)
            if record is None:
                raise ScaleValidationError(f"Missing source candidate record for integrable context {key}")
            row = bounded.build_row(record, run_id, profile_id, schema_version, source_scope, column_order, column_defs)
            physical_rows.append(row)
            lineage_rows.append({**base, "origin_mode": "scale_delta_materialized", "source_candidate_record_id": record["market_state_candidate_id"], "state_output_fingerprint": row["state_output_fingerprint"], "materialized_state_candidate_id": row["materialized_state_candidate_id"]})
        else:
            disposition = "unavailable"
            cause = ctx.get("rejected_reason") or "source_context_not_integrable"
            unavailable_rows.append({**base, "origin_mode": "unavailable", "disposition_cause": cause})
        disposition_counts[disposition] += 1
        partition_rows.append({**base, "partition_disposition": disposition, "disposition_cause": cause})

    physical_rows = sorted(physical_rows, key=lambda row: (str(row["instrument_id"]), bounded.normalize(row["session_date"]), bounded.normalize(row["decision_timestamp_utc"]), str(row["context_id"])))
    if len(physical_rows) != 104:
        raise ScaleValidationError(f"Expected 104 represented rows, got {len(physical_rows)}")

    partition_report = {
        "requested_logical_partitions": len(partition_rows),
        "reusable_validated": disposition_counts["reusable_validated"],
        "to_build_scale_delta": disposition_counts["to_build_scale_delta"],
        "unavailable": disposition_counts["unavailable"],
        "quarantined": 0,
        "blocked": 0,
        "partition_accounting_pass": len(partition_rows) == disposition_counts["reusable_validated"] + disposition_counts["to_build_scale_delta"] + disposition_counts["unavailable"],
        "partitions": partition_rows,
    }
    partition_coverage_fingerprint = sha256_payload(partition_report)
    write_json(run_dir / "partition_coverage_resolution_report.json", partition_report)

    execution_plan = {
        "execution_plan_id": "market_state_execution_plan_scale_validation_v0_1_" + sha256_payload({"request": request_fingerprint, "coverage": partition_coverage_fingerprint})[:16],
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "plan_status": "resolved_authorized_for_bounded_scale_validation",
        "created_at_utc": utc_now(),
        "planner_version": SCRIPT_VERSION,
        "resolved_profile_fingerprint": resolved_profile_fingerprint,
        "resolved_universe_fingerprint": resolved_universe_fingerprint,
        "resolved_source_set_fingerprint": resolved_source_set_fingerprint,
        "partition_coverage_resolution_fingerprint": partition_coverage_fingerprint,
        "partition_disposition_summary": {k: disposition_counts[k] for k in sorted(disposition_counts)},
        "validator_versions": [validator_contract.get("contract_id", "market_state_validator_contract_v0_1")],
        "output_policy": {"candidate_output_root": str(run_dir), "candidate_parquet_filename": "market_state_scale_validation_candidate_v0_1.parquet"},
        "quantitative_limits": read_json(AUTH_SCOPE_PATH)["limits"],
    }
    execution_plan["execution_plan_fingerprint"] = sha256_payload(execution_plan)
    write_json(run_dir / "execution_plan.json", execution_plan)

    pre_manifest = {
        "run_id": run_id,
        "gate": GATE_ID,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root),
        "git_commit": git_value(["git", "rev-parse", "HEAD"], workspace_root),
        "git_dirty_state": bool(git_value(["git", "status", "--porcelain"], workspace_root)),
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
        "authorization_contract_hash": contract_hash,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "pre_run_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": "RUNNING", "stage": "materializing_scale_delta"})

    parquet_path = run_dir / "market_state_scale_validation_candidate_v0_1.parquet"
    table = bounded.pa.Table.from_pylist(physical_rows, schema=arrow_schema)
    pq.write_table(table, parquet_path)
    observed_rows = pq.read_table(parquet_path).to_pylist()
    file_hash = sha256_file(parquet_path)

    schema_match = [field.name for field in pq.read_schema(parquet_path)] == column_order
    primary_key_fields = ["instrument_id", "decision_timestamp_utc", "state_profile_id", "state_schema_version"]
    primary_keys = [tuple(bounded.normalize(row[field]) for field in primary_key_fields) for row in observed_rows]
    duplicate_primary_keys = sum(count - 1 for count in Counter(primary_keys).values() if count > 1)
    null_failures = sum(1 for row in observed_rows for name in column_order if row.get(name) is None and not column_defs[name]["nullable"])

    fp_fields = source_scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
    id_fields = source_scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
    fingerprint_failures = 0
    for row in observed_rows:
        recalculated_state = bounded.row_fingerprint(row, fp_fields)
        recalculated_id = bounded.row_fingerprint({**row, "state_output_fingerprint": recalculated_state}, id_fields)
        if recalculated_state != row["state_output_fingerprint"] or recalculated_id != row["materialized_state_candidate_id"]:
            fingerprint_failures += 1

    context_by_key = {context_key(row): row for row in context_rows}
    temporal_failures = sum(0 if bounded.normalize(row["decision_timestamp_utc"]) == context_by_key[normalized_context_key(row)]["decision_timestamp_utc"] else 1 for row in observed_rows)
    lineage_failures = 0
    for row in observed_rows:
        for field in ["source_lineage_json", "policy_versions_json", "formula_versions_json", "restriction_codes_json"]:
            try:
                json.loads(row[field])
            except Exception:
                lineage_failures += 1

    lineage_manifest = {
        "run_id": run_id,
        "lineage_policy": "row_origin_preserved_for_reuse_and_scale_delta",
        "reused_contexts": disposition_counts["reusable_validated"],
        "scale_delta_materialized_contexts": disposition_counts["to_build_scale_delta"],
        "unavailable_contexts": disposition_counts["unavailable"],
        "row_lineage": lineage_rows,
        "unavailable_contexts_detail": unavailable_rows,
    }
    lineage_manifest["lineage_manifest_sha256"] = hash_excluding(lineage_manifest, "lineage_manifest_sha256")
    write_json(run_dir / "lineage_manifest.json", lineage_manifest)
    write_json(run_dir / "market_state_lineage_validation_report.json", {"lineage_json_parse_failures": lineage_failures, "lineage_manifest": "lineage_manifest.json"})
    write_json(run_dir / "market_state_temporal_legality_report.json", {"failures": temporal_failures})

    partition_validation = {
        "requested_logical_partitions": len(partition_rows),
        "reusable_validated": disposition_counts["reusable_validated"],
        "to_build_scale_delta": disposition_counts["to_build_scale_delta"],
        "unavailable": disposition_counts["unavailable"],
        "materialized_partitions": len(observed_rows),
        "partition_accounting_pass": partition_report["partition_accounting_pass"],
        "represented_accounting_pass": len(observed_rows) == disposition_counts["reusable_validated"] + disposition_counts["to_build_scale_delta"],
        "unaccounted_contexts": len(partition_rows) - len(observed_rows) - disposition_counts["unavailable"],
    }
    write_json(run_dir / "market_state_partition_validation_report.json", partition_validation)

    validation_hard_failures = sum(
        [
            0 if schema_match else 1,
            duplicate_primary_keys,
            null_failures,
            fingerprint_failures,
            temporal_failures,
            lineage_failures,
            0 if partition_validation["partition_accounting_pass"] else 1,
            0 if partition_validation["represented_accounting_pass"] else 1,
            partition_validation["unaccounted_contexts"],
            0 if disposition_counts["reusable_validated"] == 14 else 1,
            0 if disposition_counts["to_build_scale_delta"] == 90 else 1,
            0 if disposition_counts["unavailable"] == 16 else 1,
        ]
    )
    validation_status = "PASS_WITH_RESTRICTIONS" if validation_hard_failures == 0 else "FAIL"
    validation_report = {
        "validation_status": validation_status,
        "schema_match": schema_match,
        "row_count": len(observed_rows),
        "duplicate_primary_keys": duplicate_primary_keys,
        "non_nullable_null_failures": null_failures,
        "fingerprint_failures": fingerprint_failures,
        "temporal_failures": temporal_failures,
        "lineage_failures": lineage_failures,
        "partition_accounting_pass": partition_validation["partition_accounting_pass"],
        "represented_accounting_pass": partition_validation["represented_accounting_pass"],
        "hard_validation_failures": validation_hard_failures,
        "eligible_for_candidate_registry": validation_hard_failures == 0,
        "reuse_eligibility": "pending_scale_validation_review",
        "promotion_review_eligibility": "not_eligible_pending_scale_validation_review",
    }
    validation_result_fingerprint = sha256_payload(validation_report)
    write_json(run_dir / "market_state_validation_report.json", validation_report)

    normalized_rows = [{field: bounded.normalize(row.get(field)) for field in fp_fields + ["materialized_state_candidate_id", "state_output_fingerprint"]} for row in observed_rows]
    scientific_dataset_fingerprint = sha256_payload(
        {
            "profile_id": profile_id,
            "schema_version": schema_version,
            "rows": sorted(normalized_rows, key=lambda x: x["materialized_state_candidate_id"]),
            "unavailable_contexts": sorted(unavailable_rows, key=lambda x: x["context_id"]),
            "lineage_policy": lineage_manifest["lineage_policy"],
        }
    )
    candidate_dataset_fingerprint = sha256_payload(
        {
            "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
            "file_hash": file_hash,
            "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
            "validation_result_fingerprint": validation_result_fingerprint,
            "coverage": partition_validation,
        }
    )
    candidate_dataset_id = "market_state_candidate_dataset_scale_validation_v0_1_" + candidate_dataset_fingerprint[:16]
    candidate_output_manifest = {
        "candidate_dataset_id": candidate_dataset_id,
        "candidate_dataset_status": "candidate_pending_scale_review",
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
        "profile_id": profile_id,
        "coverage": {
            "requested_contexts": len(partition_rows),
            "reusable_validated_contexts": disposition_counts["reusable_validated"],
            "scale_delta_materialized_contexts": disposition_counts["to_build_scale_delta"],
            "represented_contexts": len(observed_rows),
            "unavailable_contexts": disposition_counts["unavailable"],
        },
        "files": [{"path": str(parquet_path), "sha256": file_hash, "bytes": parquet_path.stat().st_size, "rows": len(observed_rows)}],
        "schema_contract": str(PROFILE_SCHEMA_PATH),
        "schema_contract_sha256": sha256_file(PROFILE_SCHEMA_PATH),
    }
    write_json(run_dir / "candidate_output_manifest.json", candidate_output_manifest)

    registry_entry = {
        "dataset_id": candidate_dataset_id,
        "dataset_kind": "market_state_candidate_dataset_scale_validation",
        "registry_status": "validated_candidate" if validation_hard_failures == 0 else "failed",
        "validation_status": validation_status.lower(),
        "reuse_eligibility": "pending_scale_validation_review",
        "promotion_review_eligibility": "not_eligible_pending_scale_validation_review",
        "downstream_eligibility": False,
        "request_fingerprint": request_fingerprint,
        "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "profile_id": profile_id,
        "coverage": candidate_output_manifest["coverage"],
        "file_manifest_ref": "candidate_output_manifest.json",
        "lineage_manifest_ref": "lineage_manifest.json",
        "validation_report_ref": "market_state_validation_report.json",
    }
    registry_entry["registry_entry_fingerprint"] = sha256_payload(registry_entry)
    write_json(run_dir / "candidate_registry_entry.json", registry_entry)

    final_status = (
        "CLOSED_PASS_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED"
        if validation_hard_failures == 0
        else "CLOSED_BLOCKED_SCALE_VALIDATION_FAILED"
    )
    scale_matrix = {
        "validation_id": run_id,
        "gate": GATE_ID,
        "status": final_status,
        "decision": {
            "requested_contexts": len(partition_rows),
            "represented_contexts": len(observed_rows),
            "reusable_validated_contexts": disposition_counts["reusable_validated"],
            "scale_delta_materialized_contexts": disposition_counts["to_build_scale_delta"],
            "unavailable_contexts": disposition_counts["unavailable"],
            "unaccounted_contexts": partition_validation["unaccounted_contexts"],
            "hard_validation_failures": validation_hard_failures,
        },
        "fingerprints": {
            "request_fingerprint": request_fingerprint,
            "resolved_profile_fingerprint": resolved_profile_fingerprint,
            "resolved_universe_fingerprint": resolved_universe_fingerprint,
            "resolved_source_set_fingerprint": resolved_source_set_fingerprint,
            "partition_coverage_resolution_fingerprint": partition_coverage_fingerprint,
            "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
            "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
            "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
            "validation_result_fingerprint": validation_result_fingerprint,
            "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        },
        "next_allowed_gate": "market_state_on_demand_capability_promotion_review_v0_1" if validation_hard_failures == 0 else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    scale_matrix["scale_validation_matrix_sha256"] = hash_excluding(scale_matrix, "scale_validation_matrix_sha256")
    write_json(BASE / "market_state_on_demand_scale_validation_matrix_v0_1.json", scale_matrix)

    context_ledger = {"validation_id": run_id, "gate": GATE_ID, "counts": scale_matrix["decision"], "entries": partition_rows}
    context_ledger["scale_context_ledger_sha256"] = hash_excluding(context_ledger, "scale_context_ledger_sha256")
    write_json(BASE / "scale_validation_context_ledger_v0_1.json", context_ledger)

    fp_comparison = {
        "validation_id": run_id,
        "physical_artifact_fingerprint": file_hash,
        "logical_scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "normalization_policy": "exclude runtime ids and paths from scientific fingerprint; include governed row content, row fingerprints, coverage ledger and lineage policy",
        "reused_contexts": disposition_counts["reusable_validated"],
        "scale_delta_contexts": disposition_counts["to_build_scale_delta"],
        "unavailable_contexts": disposition_counts["unavailable"],
    }
    fp_comparison["fingerprint_comparison_sha256"] = hash_excluding(fp_comparison, "fingerprint_comparison_sha256")
    write_json(BASE / "scale_validation_fingerprint_comparison_v0_1.json", fp_comparison)

    final_manifest = {
        "run_id": run_id,
        "gate": GATE_ID,
        "status": final_status,
        "created_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "pid": os.getpid(),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root),
        "git_commit": git_value(["git", "rev-parse", "HEAD"], workspace_root),
        "git_dirty_state": bool(git_value(["git", "status", "--porcelain"], workspace_root)),
        "source_candidate_records_read": len(source_records),
        "source_context_records_read": len(context_rows),
        "source_market_data_rows_read": 0,
        "requested_contexts": len(partition_rows),
        "represented_contexts": len(observed_rows),
        "reusable_validated_contexts": disposition_counts["reusable_validated"],
        "scale_delta_materialized_contexts": disposition_counts["to_build_scale_delta"],
        "unavailable_contexts": disposition_counts["unavailable"],
        "candidate_parquet_files_written": 1,
        "candidate_registry_entries_written": 1 if validation_hard_failures == 0 else 0,
        "hard_validation_failures": validation_hard_failures,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "request_fingerprint": request_fingerprint,
        "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
        "candidate_dataset_fingerprint": candidate_dataset_fingerprint,
        "scientific_dataset_fingerprint": scientific_dataset_fingerprint,
        "validation_result_fingerprint": validation_result_fingerprint,
        "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "next_allowed_gate": scale_matrix["next_allowed_gate"],
        "artifacts": {
            "request_record": str(run_dir / "request_record.json"),
            "execution_plan": str(run_dir / "execution_plan.json"),
            "candidate_output_manifest": str(run_dir / "candidate_output_manifest.json"),
            "lineage_manifest": str(run_dir / "lineage_manifest.json"),
            "market_state_validation_report": str(run_dir / "market_state_validation_report.json"),
            "candidate_registry_entry": str(run_dir / "candidate_registry_entry.json"),
            "candidate_parquet": str(parquet_path),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": final_status, "stage": "closed"})

    readout = f"""# Market State On-Demand Scale Validation Readout v0.1

Status: `{final_status}`
Date: `2026-07-27`

```text
run_id = {run_id}
requested_contexts = {len(partition_rows)}
represented_contexts = {len(observed_rows)}
reusable_validated_contexts = {disposition_counts['reusable_validated']}
scale_delta_materialized_contexts = {disposition_counts['to_build_scale_delta']}
unavailable_contexts = {disposition_counts['unavailable']}
unaccounted_contexts = {partition_validation['unaccounted_contexts']}
source_candidate_records_read = {len(source_records)}
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
candidate_registry_entries_written = {1 if validation_hard_failures == 0 else 0}
hard_validation_failures = {validation_hard_failures}
candidate_dataset_fingerprint = {candidate_dataset_fingerprint}
scientific_dataset_fingerprint = {scientific_dataset_fingerprint}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {scale_matrix['next_allowed_gate']}
```

The scale validation remains bounded to Scale C runtime evidence. It proves a
larger controlled request can reuse validated lineage-chain contexts and build
only the remaining scale delta. It does not promote an official dataset and does
not authorize downstream use.
"""
    (run_dir / "market_state_on_demand_scale_validation_readout_v0_1.md").write_text(readout, encoding="utf-8")
    (BASE / "market_state_on_demand_scale_validation_readout_v0_1.md").write_text(readout, encoding="utf-8")

    print(json.dumps(final_manifest, indent=2, ensure_ascii=False, default=str))
    return 0 if validation_hard_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
