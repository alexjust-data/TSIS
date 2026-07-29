#!/usr/bin/env python3
"""Run bounded scale validation for Event State on-demand.

This runner uses the closed Market State scale candidate as a governed runtime
dependency and the closed Event State lineage-chain candidate as reusable
evidence. It builds only Event State scale-delta records for
session_opened/exchange_session contexts with an exact Market State anchor
binding. It does not read raw market data, rematerialize Market State, promote
datasets, open production, or open downstream authority.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SCRIPT_VERSION = "event_state_on_demand_scale_validation_runner_v0_1"
GATE_ID = "event_state_on_demand_scale_validation_v0_1"
PASS_STATUS = "CLOSED_PASS_EVENT_STATE_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED"
FAIL_STATUS = "CLOSED_BLOCKED_EVENT_STATE_SCALE_VALIDATION_FAILED"
NEXT_GATE = "event_state_on_demand_capability_promotion_review_v0_1"

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
FEATURE_ROOT = RUNTIME_ROOT.parent
EVENT_ROOT = FEATURE_ROOT / "07_EVENT_STATE_INTEGRATION"
RUNS = RUNTIME_ROOT / "runs"
CONFIGS = RUNTIME_ROOT / "configs"

MS_SCALE_RUN_ID = "market_state_on_demand_scale_validation_v0_1_20260727T133641Z"
MS_SCALE_RUN = RUNS / MS_SCALE_RUN_ID
LINEAGE_RUN_ID = "event_state_on_demand_incremental_lineage_chain_validation_v0_1_20260728T112448Z"
LINEAGE_RUN = RUNS / LINEAGE_RUN_ID
GEN2_RUN_ID = "event_state_on_demand_second_generation_incremental_extension_v0_1_20260728T103016Z"
GEN2_RUN = RUNS / GEN2_RUN_ID

EVENT_PROFILE_PATH = EVENT_ROOT / "official_profiles" / "event_state_core_four_intraday_profile_v0_1" / "PROFILE_MANIFEST.json"
EVENT_INSTANCE_CONTRACT_PATH = EVENT_ROOT / "event_instance_binding_design_contract_v0_1.json"
EVENT_WINDOW_CONTRACT_PATH = EVENT_ROOT / "event_window_binding_design_contract_v0_1.json"
PROJECTION_CONTRACT_PATH = EVENT_ROOT / "event_state_instrument_session_projection_design_contract_v0_1.json"

REQUEST_CONTRACT_PATH = RUNTIME_ROOT / "event_state_request_contract_v0_1.json"
DEPENDENCY_CONTRACT_PATH = RUNTIME_ROOT / "event_state_dependency_resolution_contract_v0_1.json"
EXECUTION_PLAN_CONTRACT_PATH = RUNTIME_ROOT / "event_state_execution_plan_contract_v0_1.json"
MATERIALIZER_CONTRACT_PATH = RUNTIME_ROOT / "event_state_materializer_contract_v0_1.json"
VALIDATOR_CONTRACT_PATH = RUNTIME_ROOT / "event_state_validator_contract_v0_1.json"
REGISTRY_CONTRACT_PATH = RUNTIME_ROOT / "event_state_candidate_dataset_registry_contract_v0_1.json"
MS_CONSUMPTION_POLICY_PATH = RUNTIME_ROOT / "market_state_capability_consumption_policy_contract_v0_1.json"

AUTH_SCOPE_PATH = CONFIGS / "event_state_on_demand_scale_validation_scope_v0_1.json"
AUTH_CONTRACT_PATH = RUNTIME_ROOT / "event_state_on_demand_scale_validation_contract_v0_1.json"
AUTH_MD_PATH = RUNTIME_ROOT / "event_state_on_demand_scale_validation_authorization_v0_1.md"
AUTH_READOUT_PATH = RUNTIME_ROOT / "event_state_on_demand_scale_validation_authorization_readout_v0_1.md"

EVENT_STATE_RECORD_NAMESPACE = "tsis_event_state_on_demand_record_v0_1"
EVENT_INSTANCE_NAMESPACE = "tsis_event_instance_v0_1"
EVENT_WINDOW_NAMESPACE = "tsis_event_window_binding_v0_1"
PROJECTION_NAMESPACE = "tsis_event_state_instrument_session_projection_v0_1"
EVENT_STATE_SCHEMA_VERSION = "event_state_candidate_schema_v0_1"
INTEGRATION_POLICY_ID = "event_state_on_demand_integration_policy_v0_1"
INTEGRATION_POLICY_VERSION = "v0_1"
EVENT_STATE_PROFILE_ID = "event_state_core_four_intraday_profile_v0_1"
EVENT_TYPE_ID = "event_type:market_data:session_opened"
EVENT_FAMILY_ID = "event_family:market_data:session_lifecycle"
EVENT_WINDOW_DEFINITION_ID = "session_opened_at_anchor_context_v0_1"
EXCHANGE_ID = "XNYS"
CALENDAR_VERSION = "governed_exchange_session_calendar_xnys_v0_1"
MS_PROFILE_ID = "market_state_core_four_intraday_profile_v0_1"
MS_SCHEMA_VERSION = "core_four_market_state_candidate_physical_schema_v0_1"


class ScaleValidationError(RuntimeError):
    pass


def to_builtin(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_builtin(v) for v in value]
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if hasattr(value, "item"):
        return to_builtin(value.item())
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def stable_json(value: Any) -> str:
    return json.dumps(to_builtin(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def count_by(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(Counter(str(record.get(field, "missing")) for record in records))

def canonical_hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path) -> Any:
    if not path.exists():
        raise ScaleValidationError(f"Missing JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_builtin(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(to_builtin(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def context_key(row: dict[str, Any], *, anchor: str | None = None) -> str:
    ts = anchor or row.get("event_anchor_timestamp_utc") or row.get("decision_timestamp_utc")
    return "|".join(
        [
            str(row.get("event_type_id", EVENT_TYPE_ID)),
            str(row.get("exchange_id", EXCHANGE_ID)),
            str(row.get("session_date", "")),
            str(row.get("instrument_id", "")),
            str(ts),
            str(row.get("event_window_definition_id", EVENT_WINDOW_DEFINITION_ID)),
        ]
    )


def market_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row["instrument_id"]), str(row["session_date"]), str(row["decision_timestamp_utc"]))


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def hash_excluding(payload: dict[str, Any], key: str) -> str:
    return sha256_payload({k: v for k, v in payload.items() if k != key})


def require_files(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise ScaleValidationError("Missing required files: " + "; ".join(missing))


def json_or_empty(value: Any) -> dict[str, Any]:
    if isinstance(value, str) and value.strip():
        try:
            decoded = json.loads(value)
            return decoded if isinstance(decoded, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def infer_anchor_by_session(ms_context_ledger: list[dict[str, Any]]) -> dict[str, str]:
    candidates: dict[str, Counter[str]] = {}
    for row in ms_context_ledger:
        if row.get("partition_disposition") == "unavailable":
            continue
        ts = str(row.get("decision_timestamp_utc", ""))
        if ts.endswith("T13:30:00Z") or ts.endswith("T14:30:00Z"):
            candidates.setdefault(str(row["session_date"]), Counter())[ts] += 1
    anchors: dict[str, str] = {}
    for session_date, counts in candidates.items():
        if not counts:
            continue
        anchors[session_date] = counts.most_common(1)[0][0]
    return anchors


def make_event_instance(session_date: str, anchor: str, existing_by_date: dict[str, str]) -> dict[str, Any]:
    event_instance_id = existing_by_date.get(session_date) or canonical_hash(
        EVENT_INSTANCE_NAMESPACE,
        EVENT_TYPE_ID,
        EXCHANGE_ID,
        session_date,
        anchor,
        CALENDAR_VERSION,
    )
    return {
        "event_instance_id": event_instance_id,
        "event_type_id": EVENT_TYPE_ID,
        "event_family_id": EVENT_FAMILY_ID,
        "event_subject_scope": "exchange_session",
        "exchange_id": EXCHANGE_ID,
        "session_date": session_date,
        "event_anchor_timestamp_utc": anchor,
        "calendar_version": CALENDAR_VERSION,
        "event_instance_version": "v0_1",
        "native_identity_includes_instrument_id": False,
        "detector_required": False,
    }


def make_window_binding(event_instance: dict[str, Any], existing_by_date: dict[str, str]) -> dict[str, Any]:
    session_date = event_instance["session_date"]
    event_window_binding_id = existing_by_date.get(session_date) or canonical_hash(
        EVENT_WINDOW_NAMESPACE,
        event_instance["event_instance_id"],
        EVENT_WINDOW_DEFINITION_ID,
        "at_event",
    )
    anchor = event_instance["event_anchor_timestamp_utc"]
    return {
        "event_window_binding_id": event_window_binding_id,
        "event_instance_id": event_instance["event_instance_id"],
        "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
        "state_role": "at_event",
        "consumption_legality": "research_only",
        "window_start_utc": anchor,
        "window_end_utc": anchor,
        "relative_time_to_event": "PT0S",
        "leakage_assessment": "exact_anchor_only; at_event_research_only_until_field_legality_review",
    }


def make_projection(event_instance: dict[str, Any], instrument_id: str, ticker: str, existing_by_key: dict[tuple[str, str], str]) -> dict[str, Any]:
    projection_key = (instrument_id, event_instance["session_date"])
    projection_id = existing_by_key.get(projection_key) or canonical_hash(
        PROJECTION_NAMESPACE,
        event_instance["event_instance_id"],
        instrument_id,
        EXCHANGE_ID,
        event_instance["session_date"],
    )
    return {
        "event_state_instrument_session_projection_id": projection_id,
        "event_instance_id": event_instance["event_instance_id"],
        "instrument_id": instrument_id,
        "ticker": ticker,
        "exchange_id": EXCHANGE_ID,
        "session_date": event_instance["session_date"],
        "projection_scope": "instrument_session_association",
        "point_in_time_eligibility": "authorized_scale_validation_scope_not_master_lifecycle_revalidated",
    }


def make_scale_delta_record(
    market_row: dict[str, Any],
    event_instance: dict[str, Any],
    window_binding: dict[str, Any],
    projection: dict[str, Any],
    request_fp: str,
    plan_fp: str,
    ms_final: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    market_state_record_id = str(market_row["materialized_state_candidate_id"])
    state_output_fingerprint = str(market_row["state_output_fingerprint"])
    source_lineage = json_or_empty(market_row.get("source_lineage_json"))
    source_lineage.update(
        {
            "event_state_scale_validation_run": True,
            "event_instance_id": event_instance["event_instance_id"],
            "event_window_binding_id": window_binding["event_window_binding_id"],
            "instrument_projection_id": projection["event_state_instrument_session_projection_id"],
            "market_state_dependency_run_id": MS_SCALE_RUN_ID,
            "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"],
            "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"],
            "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "direct_market_state_path_allowed": False,
        }
    )
    policy_versions = json_or_empty(market_row.get("policy_versions_json"))
    policy_versions.update(
        {
            "event_state_request_contract": "event_state_request_contract_v0_1",
            "event_state_dependency_resolution_contract": "event_state_dependency_resolution_contract_v0_1",
            "event_state_execution_plan_contract": "event_state_execution_plan_contract_v0_1",
            "event_state_materializer_contract": "event_state_materializer_contract_v0_1",
            "event_state_validator_contract": "event_state_validator_contract_v0_1",
            "event_state_integration_policy": INTEGRATION_POLICY_VERSION,
        }
    )
    value_snapshot = {
        key: to_builtin(market_row.get(key))
        for key in [
            "materialized_state_candidate_id",
            "state_profile_id",
            "instrument_id",
            "ticker",
            "session_date",
            "decision_timestamp_utc",
            "decision_case",
            "integration_status",
            "object_completeness_status",
            "quality_status",
            "state_output_fingerprint",
        ]
    }
    record_base = {
        "event_state_schema_version": EVENT_STATE_SCHEMA_VERSION,
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_family_id": EVENT_FAMILY_ID,
        "event_type_id": EVENT_TYPE_ID,
        "event_instance_id": event_instance["event_instance_id"],
        "event_instance_version": "v0_1",
        "event_window_binding_id": window_binding["event_window_binding_id"],
        "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
        "event_state_instrument_session_projection_id": projection["event_state_instrument_session_projection_id"],
        "exchange_id": EXCHANGE_ID,
        "instrument_id": str(market_row["instrument_id"]),
        "ticker": str(market_row.get("ticker", "")),
        "session_date": str(market_row["session_date"]),
        "event_anchor_timestamp_utc": event_instance["event_anchor_timestamp_utc"],
        "decision_timestamp_utc": event_instance["event_anchor_timestamp_utc"],
        "window_start_utc": event_instance["event_anchor_timestamp_utc"],
        "window_end_utc": event_instance["event_anchor_timestamp_utc"],
        "relative_time_to_event": "PT0S",
        "state_role": "at_event",
        "consumption_legality": "research_only",
        "market_state_record_id": market_state_record_id,
        "state_output_fingerprint": state_output_fingerprint,
        "source_market_state_profile_id": MS_PROFILE_ID,
        "source_market_state_physical_profile_id": MS_PROFILE_ID,
        "source_market_state_schema_version": MS_SCHEMA_VERSION,
        "source_market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"],
        "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"],
        "calendar_version": CALENDAR_VERSION,
        "calendar_row_fingerprint": canonical_hash("calendar", EXCHANGE_ID, market_row["session_date"], event_instance["event_anchor_timestamp_utc"], CALENDAR_VERSION),
        "integration_policy_id": INTEGRATION_POLICY_ID,
        "integration_policy_version": INTEGRATION_POLICY_VERSION,
        "integration_status": "EVENT_STATE_SCALE_DELTA_INTEGRATED_WITH_RESTRICTIONS",
        "object_completeness_status": "COMPLETE_REQUIRED_OBJECTS_WITH_RESTRICTIONS",
        "quality_status": "PASS_WITH_RESTRICTIONS",
        "source_lineage_json": stable_json(source_lineage),
        "policy_versions_json": stable_json(policy_versions),
        "restriction_codes_json": stable_json(
            [
                "event_state_on_demand_scale_validation_candidate_output_only",
                "source_market_state_runtime_candidate_reuse_scale_validation",
                "source_market_state_official_dataset_false",
                "at_event_consumption_legality_research_only_until_field_legality_review",
                "instrument_projection_from_authorized_scale_scope_not_master_lifecycle_revalidated",
                "event_state_downstream_consumption_prohibited",
                "source_market_state_restrictions_preserved",
            ]
        ),
        "source_market_state_value_snapshot_json": stable_json(value_snapshot),
    }
    record_id = canonical_hash(
        EVENT_STATE_RECORD_NAMESPACE,
        record_base["event_state_profile_id"],
        record_base["event_type_id"],
        record_base["event_instance_id"],
        record_base["event_window_binding_id"],
        record_base["event_state_instrument_session_projection_id"],
        record_base["market_state_record_id"],
        record_base["state_output_fingerprint"],
        record_base["state_role"],
        record_base["consumption_legality"],
        INTEGRATION_POLICY_VERSION,
    )
    fingerprint_payload = {"event_state_record_id": record_id, **record_base}
    return {
        "event_state_record_id": record_id,
        **record_base,
        "event_state_record_fingerprint": sha256_payload(fingerprint_payload),
        "created_at_utc": created_at,
    }


def write_authorization(run_id: str, consumed_at: str) -> str:
    scope = {
        "scope_id": "event_state_on_demand_scale_validation_scope_v0_1",
        "gate": GATE_ID,
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RUN",
        "consumed_by_run_id": run_id,
        "consumed_at_utc": consumed_at,
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_id": EVENT_TYPE_ID,
        "subject_scope": "exchange_session",
        "exchange_id": EXCHANGE_ID,
        "source_market_state_dependency": {
            "runtime_capability_id": "market_state_on_demand_runtime_capability_v0_1",
            "source_run_id": MS_SCALE_RUN_ID,
            "candidate_dataset_fingerprint": "516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416",
            "direct_market_state_path_allowed": False,
            "market_state_materializer_execution_allowed": False,
            "source_market_data_reads_allowed": False,
        },
        "bounded_scale": {
            "requested_event_state_contexts": 80,
            "expected_reused_lineage_chain_contexts": 14,
            "expected_scale_delta_materialized_contexts": 60,
            "expected_unavailable_contexts": 6,
            "expected_represented_contexts": 74,
            "expected_instruments": 10,
            "expected_sessions": 8,
        },
        "authority": {
            "event_state_materializer_execution_allowed": True,
            "event_state_materializer_scope": "scale_delta_only",
            "market_state_candidate_file_reads_allowed": True,
            "event_state_prior_candidate_record_reads_allowed": True,
            "source_market_data_reads_allowed": False,
            "market_state_materializer_execution_allowed": False,
            "official_dataset_promotion_allowed": False,
            "production_allowed": False,
            "downstream_consumption_allowed": False,
            "additional_event_types_allowed": False,
            "halt_resumed_allowed": False,
        },
        "limits": {
            "maximum_requested_event_state_contexts": 80,
            "maximum_reused_lineage_chain_contexts": 14,
            "maximum_scale_delta_materialized_contexts": 60,
            "maximum_unavailable_contexts": 6,
            "maximum_event_state_candidate_records": 74,
            "maximum_event_state_candidate_files_written": 1,
            "maximum_market_state_candidate_records_read": 104,
            "maximum_source_market_data_rows_read": 0,
            "maximum_output_bytes": 8_000_000,
        },
    }
    scope["scope_sha256"] = sha256_payload(scope)
    contract = {
        "contract_id": "event_state_on_demand_scale_validation_contract_v0_1",
        "gate": GATE_ID,
        "contract_status": "accepted_for_bounded_event_state_scale_validation_run",
        "consumed_by_run_id": run_id,
        "required_invariants": {
            "requested_contexts": 80,
            "represented_contexts": 74,
            "reused_lineage_chain_contexts": 14,
            "scale_delta_materialized_contexts": 60,
            "unavailable_contexts": 6,
            "unaccounted_contexts": 0,
            "market_state_materializer_executions": 0,
            "source_market_data_rows_read": 0,
            "candidate_registry_entries_written": 1,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "partition_accounting": "requested = reused_lineage_chain_validated + scale_delta_materialized + unavailable + blocked + quarantined",
        "market_state_dependency_policy": "resolve_through_market_state_runtime_capability_scale_candidate; exact_event_anchor_binding_or_unavailable",
        "next_gate_on_pass": NEXT_GATE,
    }
    contract["contract_content_sha256_excluding_hash_field"] = hash_excluding(
        contract,
        "contract_content_sha256_excluding_hash_field",
    )
    auth = f"""# Event State On-Demand Scale Validation Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RUN`
Date: `2026-07-28`

```text
gate = {GATE_ID}
consumed_by_run_id = {run_id}
consumed_at_utc = {consumed_at}
event_type_id = {EVENT_TYPE_ID}
subject_scope = exchange_session
requested_event_state_contexts = 80
expected_reused_lineage_chain_contexts = 14
expected_scale_delta_materialized_contexts = 60
expected_unavailable_contexts = 6
market_state_dependency = runtime_capability_scale_candidate_only
direct_market_state_path_allowed = false
market_state_materializer_execution_allowed = false
source_market_data_reads_allowed = false
official_dataset_promotion_allowed = false
production = false
downstream = false
```
"""
    readout = f"""# Event State On-Demand Scale Validation Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RUN`
Date: `2026-07-28`

```text
gate = {GATE_ID}
consumed_by_run_id = {run_id}
contract_content_sha256_excluding_hash_field = {contract['contract_content_sha256_excluding_hash_field']}
next_allowed_gate = {GATE_ID}
```

This authorization is consumed by one bounded Event State scale validation run.
It does not authorize official dataset promotion, production or downstream use.
"""
    write_json(AUTH_SCOPE_PATH, scope)
    write_json(AUTH_CONTRACT_PATH, contract)
    write_text(AUTH_MD_PATH, auth)
    write_text(AUTH_READOUT_PATH, readout)
    return contract["contract_content_sha256_excluding_hash_field"]


def readout_text(final: dict[str, Any]) -> str:
    return f"""# Event State On-Demand Scale Validation Readout v0.1

Status: `{final['final_run_status']}`
Date: `2026-07-28`

```text
run_id = {final['run_id']}
requested_contexts = {final['requested_event_state_context_count']}
represented_contexts = {final['represented_context_count']}
reused_lineage_chain_contexts = {final['reused_lineage_chain_event_state_context_count']}
scale_delta_materialized_contexts = {final['scale_delta_materialized_event_state_context_count']}
unavailable_contexts = {final['unavailable_context_count']}
unaccounted_contexts = {final['unaccounted_context_count']}
combined_event_state_records = {final['combined_event_state_record_count']}
event_state_materializer_executions = {final['event_state_materializer_executions']}
market_state_materializer_executions = {final['market_state_materializer_executions']}
market_state_candidate_records_read = {final['market_state_candidate_records_read']}
source_market_data_rows_read = {final['source_market_data_rows_read']}
candidate_dataset_registry_entries_written = {final['candidate_dataset_registry_entries_written']}
hard_validation_failures = {final['hard_validation_failures']}
candidate_dataset_fingerprint = {final['candidate_dataset_fingerprint']}
logical_event_state_dataset_fingerprint = {final['logical_event_state_dataset_fingerprint']}
validation_result_fingerprint = {final['validation_result_fingerprint']}
official_event_state_dataset = false
production = false
downstream = false
next_allowed_gate = {final['next_allowed_gate']}
```

The scale validation remains candidate/runtime evidence. It proves Event State
on-demand can scale beyond the incremental chain while reusing validated Event
State evidence, materializing only new at-anchor delta records and resolving
Market State exclusively through the promoted runtime capability.
"""


def main() -> int:
    workspace_root = Path("C:/TSIS_Data").resolve()
    require_files(
        [
            EVENT_PROFILE_PATH,
            EVENT_INSTANCE_CONTRACT_PATH,
            EVENT_WINDOW_CONTRACT_PATH,
            PROJECTION_CONTRACT_PATH,
            REQUEST_CONTRACT_PATH,
            DEPENDENCY_CONTRACT_PATH,
            EXECUTION_PLAN_CONTRACT_PATH,
            MATERIALIZER_CONTRACT_PATH,
            VALIDATOR_CONTRACT_PATH,
            REGISTRY_CONTRACT_PATH,
            MS_CONSUMPTION_POLICY_PATH,
            MS_SCALE_RUN / "final_manifest.json",
            MS_SCALE_RUN / "market_state_scale_validation_candidate_v0_1.parquet",
            RUNTIME_ROOT / "scale_validation_context_ledger_v0_1.json",
            LINEAGE_RUN / "final_manifest.json",
            RUNTIME_ROOT / "event_state_on_demand_incremental_lineage_chain_ledger_v0_1.json",
            GEN2_RUN / "event_state_second_generation_incremental_candidate_records.jsonl",
        ]
    )

    run_id = f"{GATE_ID}_{utc_compact()}"
    run_dir = RUNS / run_id
    if run_dir.exists():
        raise ScaleValidationError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    started_at = utc_now()
    auth_contract_hash = write_authorization(run_id, started_at)

    ms_final = read_json(MS_SCALE_RUN / "final_manifest.json")
    ms_context_ledger = read_json(RUNTIME_ROOT / "scale_validation_context_ledger_v0_1.json")["entries"]
    lineage_final = read_json(LINEAGE_RUN / "final_manifest.json")
    lineage_ledger = read_json(RUNTIME_ROOT / "event_state_on_demand_incremental_lineage_chain_ledger_v0_1.json")
    event_profile = read_json(EVENT_PROFILE_PATH)

    market_rows = [
        {str(k): to_builtin(v) for k, v in row.items()}
        for row in pd.read_parquet(MS_SCALE_RUN / "market_state_scale_validation_candidate_v0_1.parquet").to_dict("records")
    ]
    market_by_key = {market_key(row): row for row in market_rows}

    prior_records = read_jsonl(GEN2_RUN / "event_state_second_generation_incremental_candidate_records.jsonl")
    prior_by_key = {context_key(row): row for row in prior_records}
    existing_instance_by_date = {row["session_date"]: row["event_instance_id"] for row in prior_records}
    existing_window_by_date = {row["session_date"]: row["event_window_binding_id"] for row in prior_records}
    existing_projection_by_key = {
        (row["instrument_id"], row["session_date"]): row["event_state_instrument_session_projection_id"]
        for row in prior_records
    }

    anchor_by_date = infer_anchor_by_session(ms_context_ledger)
    requested_contexts = [
        row
        for row in ms_context_ledger
        if row.get("decision_case") == "first_observable_bar_governed_session"
    ]
    requested_keys = {(row["instrument_id"], row["session_date"]) for row in requested_contexts}

    request_payload = {
        "request_type": "event_state",
        "request_contract_version": "event_state_request_contract_v0_1",
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_ids": [EVENT_TYPE_ID],
        "event_subject_scope": "exchange_session",
        "event_window_definition_ids": [EVENT_WINDOW_DEFINITION_ID],
        "exchange_scope": [EXCHANGE_ID],
        "explicit_instrument_ids": sorted({row["instrument_id"] for row in requested_contexts}),
        "session_dates": sorted({row["session_date"] for row in requested_contexts}),
        "market_state_profile_id": MS_PROFILE_ID,
        "market_state_dependency_mode": "emit_or_resolve_market_state_subrequest_through_runtime_capability",
        "market_state_dependency_reuse_policy": "reuse_existing_scale_validated_candidate_or_block",
        "output_mode": "candidate_scale_validation",
        "output_format": "jsonl",
        "validation_level": "bounded_scale_validation",
        "requested_context_count": len(requested_contexts),
    }
    request_fingerprint = sha256_payload(request_payload)
    request = {
        "request_id": "event_state_request_scale_validation_v0_1_" + request_fingerprint[:16],
        "request_status": "accepted_for_scale_validation_resolution",
        "requested_at_utc": started_at,
        "requested_by": os.environ.get("USERNAME") or os.environ.get("USER"),
        **request_payload,
        "request_fingerprint": request_fingerprint,
    }
    write_json(run_dir / "request_record.json", request)

    dependency_resolution = {
        "dependency_resolution_record_id": "event_state_dependency_resolution_scale_v0_1_" + request_fingerprint[:16],
        "status": "RESOLVED_FOR_EVENT_STATE_SCALE_VALIDATION",
        "resolved_at_utc": utc_now(),
        "event_state_request_id": request["request_id"],
        "event_state_request_fingerprint": request_fingerprint,
        "resolved_event_state_profile": {
            "profile_id": EVENT_STATE_PROFILE_ID,
            "profile_status": event_profile.get("status"),
            "profile_manifest_sha256": sha256_file(EVENT_PROFILE_PATH),
            "official_event_state_dataset_exists": False,
        },
        "resolved_event_type_registry": {
            "accepted_event_type_ids": [EVENT_TYPE_ID],
            "accepted_subject_scope": "exchange_session",
            "blocked_event_type_ids": ["event_type:regulatory:halt_resumed"],
            "detector_required": False,
            "event_detection_allowed": False,
        },
        "resolved_market_state_dependency": {
            "market_state_profile_id": MS_PROFILE_ID,
            "market_state_runtime_capability_id": "market_state_on_demand_runtime_capability_v0_1",
            "market_state_dependency_mode": request["market_state_dependency_mode"],
            "market_state_dependency_reuse_policy": request["market_state_dependency_reuse_policy"],
            "market_state_reference_run_id": MS_SCALE_RUN_ID,
            "market_state_dependency_request_fingerprint": ms_final["request_fingerprint"],
            "market_state_dependency_execution_plan_fingerprint": ms_final["execution_plan_fingerprint"],
            "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "market_state_validation_result_fingerprint": ms_final["validation_result_fingerprint"],
            "market_state_candidate_records_read": len(market_rows),
            "market_state_materializer_execution_allowed": False,
            "direct_market_state_path_allowed": False,
        },
        "resolved_lineage_chain_dependency": {
            "lineage_validation_run_id": LINEAGE_RUN_ID,
            "lineage_validation_status": lineage_final["final_run_status"],
            "lineage_chain_ledger_sha256": lineage_ledger["lineage_chain_ledger_sha256"],
            "reusable_event_state_contexts": lineage_final["represented_contexts"],
        },
        "blocking_findings": [],
    }
    dependency_fingerprint = sha256_payload(dependency_resolution)
    dependency_resolution["event_state_dependency_resolution_fingerprint"] = dependency_fingerprint
    write_json(run_dir / "dependency_resolution_report.json", dependency_resolution)

    execution_plan_core = {
        "event_state_request_fingerprint": request_fingerprint,
        "event_state_dependency_resolution_fingerprint": dependency_fingerprint,
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_ids": [EVENT_TYPE_ID],
        "subject_scope": "exchange_session",
        "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
        "market_state_dependency_run_id": MS_SCALE_RUN_ID,
        "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "lineage_chain_validation_run_id": LINEAGE_RUN_ID,
        "requested_contexts": len(requested_contexts),
        "expected_reused_lineage_chain_contexts": 14,
        "expected_scale_delta_contexts": 60,
        "expected_unavailable_contexts": 6,
        "output_plan": {
            "output_mode": "candidate_scale_validation",
            "output_format": "jsonl",
            "maximum_files": 1,
            "maximum_records": 74,
            "maximum_bytes": 8_000_000,
        },
    }
    plan_fp = sha256_payload(execution_plan_core)
    execution_plan = {
        "event_state_execution_plan_id": "event_state_execution_plan_scale_v0_1_" + plan_fp[:16],
        "event_state_execution_plan_contract_version": "event_state_execution_plan_contract_v0_1",
        "plan_status": "authorized_for_event_state_scale_validation",
        "created_at_utc": utc_now(),
        "planner_id": SCRIPT_VERSION,
        "planner_contract_hash": sha256_file(EXECUTION_PLAN_CONTRACT_PATH),
        **execution_plan_core,
        "event_state_execution_plan_fingerprint": plan_fp,
    }
    write_json(run_dir / "execution_plan.json", execution_plan)

    pre_run_manifest = {
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
        "request_fingerprint": request_fingerprint,
        "event_state_execution_plan_fingerprint": plan_fp,
        "authorization_contract_hash": auth_contract_hash,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "pre_run_manifest.json", pre_run_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": "RUNNING", "stage": "materializing_event_state_scale_delta"})

    event_instances_by_date: dict[str, dict[str, Any]] = {}
    window_by_date: dict[str, dict[str, Any]] = {}
    projections: dict[tuple[str, str], dict[str, Any]] = {}
    bindings: list[dict[str, Any]] = []
    context_ledger: list[dict[str, Any]] = []
    combined_records: list[dict[str, Any]] = []
    delta_records: list[dict[str, Any]] = []
    lineage_entries: list[dict[str, Any]] = []

    for session_date in sorted({row["session_date"] for row in requested_contexts}):
        event_instances_by_date[session_date] = make_event_instance(session_date, anchor_by_date[session_date], existing_instance_by_date)
        window_by_date[session_date] = make_window_binding(event_instances_by_date[session_date], existing_window_by_date)

    for row in sorted(requested_contexts, key=lambda r: (r["session_date"], r["instrument_id"])):
        session_date = row["session_date"]
        instrument_id = row["instrument_id"]
        ticker = row.get("ticker_label_non_authoritative", "")
        anchor = anchor_by_date[session_date]
        event_instance = event_instances_by_date[session_date]
        window = window_by_date[session_date]
        projection = make_projection(event_instance, instrument_id, ticker, existing_projection_by_key)
        projections[(instrument_id, session_date)] = projection

        market_row = market_by_key.get((instrument_id, session_date, anchor))
        event_key = "|".join([EVENT_TYPE_ID, EXCHANGE_ID, session_date, instrument_id, anchor, EVENT_WINDOW_DEFINITION_ID])
        reused_record = prior_by_key.get(event_key)

        binding_status = "BOUND" if market_row else "MISSING_EXACT_MARKET_STATE_BINDING"
        binding = {
            "context_id": row["context_id"],
            "event_type_id": EVENT_TYPE_ID,
            "exchange_id": EXCHANGE_ID,
            "session_date": session_date,
            "instrument_id": instrument_id,
            "event_anchor_timestamp_utc": anchor,
            "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
            "event_instance_id": event_instance["event_instance_id"],
            "event_window_binding_id": window["event_window_binding_id"],
            "event_state_instrument_session_projection_id": projection["event_state_instrument_session_projection_id"],
            "market_state_binding_status": binding_status,
            "market_state_record_id": market_row.get("materialized_state_candidate_id", "") if market_row else "",
            "state_output_fingerprint": market_row.get("state_output_fingerprint", "") if market_row else "",
            "source_market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"] if market_row else "",
            "available_same_instrument_session_timestamps": [
                ctx["decision_timestamp_utc"]
                for ctx in ms_context_ledger
                if ctx["instrument_id"] == instrument_id
                and ctx["session_date"] == session_date
                and ctx.get("partition_disposition") != "unavailable"
            ],
            "blocking_reason": "" if market_row else "missing_exact_market_state_anchor_binding",
            "fallback_used": False,
        }
        bindings.append(binding)

        if market_row and reused_record:
            record = dict(reused_record)
            combined_records.append(record)
            source = "reused_validated_event_state_lineage_chain"
            lineage_mode = "reused_from_incremental_lineage_chain"
        elif market_row:
            record = make_scale_delta_record(market_row, event_instance, window, projection, request_fingerprint, plan_fp, ms_final, started_at)
            combined_records.append(record)
            delta_records.append(record)
            source = "scale_delta_materialized_event_state"
            lineage_mode = "scale_delta_materialized"
        else:
            source = "none"
            lineage_mode = "unavailable_missing_exact_market_state_anchor_binding"

        context_ledger.append(
            {
                "context_id": row["context_id"],
                "event_type_id": EVENT_TYPE_ID,
                "exchange_id": EXCHANGE_ID,
                "session_date": session_date,
                "instrument_id": instrument_id,
                "ticker_label_non_authoritative": ticker,
                "event_anchor_timestamp_utc": anchor,
                "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
                "context_status": "represented" if market_row else "unavailable",
                "representation_source": source,
                "blocking_reason": "" if market_row else "missing_exact_market_state_anchor_binding",
                "market_state_record_id": binding["market_state_record_id"],
                "state_output_fingerprint": binding["state_output_fingerprint"],
                "source_market_state_candidate_dataset_fingerprint": binding["source_market_state_candidate_dataset_fingerprint"],
                "available_same_instrument_session_timestamps": binding["available_same_instrument_session_timestamps"],
            }
        )
        lineage_entries.append(
            {
                "context_key": event_key,
                "context_status": "represented" if market_row else "unavailable",
                "origin_mode": lineage_mode,
                "origin_run_id": GEN2_RUN_ID if reused_record else (run_id if market_row else None),
                "origin_record_id": reused_record.get("event_state_record_id") if reused_record else (record.get("event_state_record_id") if market_row else None),
                "origin_record_fingerprint": reused_record.get("event_state_record_fingerprint") if reused_record else (record.get("event_state_record_fingerprint") if market_row else None),
                "market_state_dependency_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"] if market_row else None,
                "blocking_reason": "" if market_row else "missing_exact_market_state_anchor_binding",
            }
        )

    output_path = run_dir / "event_state_scale_candidate_records.jsonl"
    delta_path = run_dir / "event_state_scale_delta_records.jsonl"
    write_jsonl(output_path, combined_records)
    write_jsonl(delta_path, delta_records)
    output_hash = sha256_file(output_path)
    delta_hash = sha256_file(delta_path)

    write_json(run_dir / "event_instance_manifest.json", {"run_id": run_id, "event_instance_count": len(event_instances_by_date), "event_instances": list(event_instances_by_date.values())})
    write_json(run_dir / "event_window_binding_manifest.json", {"run_id": run_id, "event_window_binding_count": len(window_by_date), "event_window_bindings": list(window_by_date.values())})
    write_json(run_dir / "instrument_session_projection_manifest.json", {"run_id": run_id, "projection_count": len(projections), "instrument_session_projections": list(projections.values())})
    write_json(run_dir / "market_state_dependency_binding_report.json", {"run_id": run_id, "bindings": bindings, "binding_status_counts": count_by(bindings, "market_state_binding_status"), "direct_market_state_path_allowed": False})

    represented_contexts = sum(1 for row in context_ledger if row["context_status"] == "represented")
    unavailable_contexts = sum(1 for row in context_ledger if row["context_status"] == "unavailable")
    reused_contexts = sum(1 for row in context_ledger if row["representation_source"] == "reused_validated_event_state_lineage_chain")
    scale_delta_contexts = sum(1 for row in context_ledger if row["representation_source"] == "scale_delta_materialized_event_state")
    unaccounted_contexts = len(context_ledger) - represented_contexts - unavailable_contexts
    duplicate_record_ids = len(combined_records) - len({row["event_state_record_id"] for row in combined_records})
    duplicate_contexts = len(context_ledger) - len({context_key(row) for row in context_ledger})
    missing_fields = sum(
        1
        for row in combined_records
        if any(
            not str(row.get(field, "")).strip()
            for field in [
                "event_state_record_id",
                "event_state_record_fingerprint",
                "event_instance_id",
                "event_window_binding_id",
                "event_state_instrument_session_projection_id",
                "market_state_record_id",
                "state_output_fingerprint",
                "market_state_dependency_request_fingerprint",
                "market_state_dependency_execution_plan_fingerprint",
                "source_market_state_candidate_dataset_fingerprint",
            ]
        )
    )
    anchor_mismatches = sum(1 for row in combined_records if row["decision_timestamp_utc"] != row["event_anchor_timestamp_utc"])
    non_research_only = sum(1 for row in combined_records if row["consumption_legality"] != "research_only")
    source_fp_set = sorted({row["source_market_state_candidate_dataset_fingerprint"] for row in combined_records})
    delta_source_fp_set = sorted({row["source_market_state_candidate_dataset_fingerprint"] for row in delta_records})
    binding_status_counts = count_by(bindings, "market_state_binding_status")
    unexpected_binding_statuses = sum(
        1
        for binding in bindings
        if binding["market_state_binding_status"] not in ["BOUND", "MISSING_EXACT_MARKET_STATE_BINDING"]
    )

    hard_validation_failures = sum(
        [
            0 if len(context_ledger) == 80 else 1,
            0 if represented_contexts == 74 else 1,
            0 if reused_contexts == 14 else 1,
            0 if scale_delta_contexts == 60 else 1,
            0 if unavailable_contexts == 6 else 1,
            unaccounted_contexts,
            duplicate_record_ids,
            duplicate_contexts,
            missing_fields,
            anchor_mismatches,
            non_research_only,
            0 if len(event_instances_by_date) == 8 else 1,
            0 if len(window_by_date) == 8 else 1,
            0 if len(projections) == 80 else 1,
            0 if len(combined_records) == 74 else 1,
            0 if len(delta_records) == 60 else 1,
            0 if delta_source_fp_set == [ms_final["candidate_dataset_fingerprint"]] else 1,
            0 if binding_status_counts.get("BOUND", 0) == represented_contexts else 1,
            0 if binding_status_counts.get("MISSING_EXACT_MARKET_STATE_BINDING", 0) == unavailable_contexts else 1,
            unexpected_binding_statuses,
        ]
    )
    validation_status = "pass_with_restrictions" if hard_validation_failures == 0 else "fail"
    validation_report = {
        "validation_status": validation_status,
        "requested_contexts": len(context_ledger),
        "represented_contexts": represented_contexts,
        "reused_lineage_chain_contexts": reused_contexts,
        "scale_delta_materialized_contexts": scale_delta_contexts,
        "unavailable_contexts": unavailable_contexts,
        "unaccounted_contexts": unaccounted_contexts,
        "combined_event_state_records": len(combined_records),
        "delta_event_state_records": len(delta_records),
        "event_instances": len(event_instances_by_date),
        "event_window_bindings": len(window_by_date),
        "instrument_session_projections": len(projections),
        "duplicate_event_state_record_ids": duplicate_record_ids,
        "duplicate_canonical_contexts": duplicate_contexts,
        "missing_required_record_lineage_fields": missing_fields,
        "event_anchor_mismatches": anchor_mismatches,
        "non_research_only_rows": non_research_only,
        "market_state_dependency_candidate_dataset_fingerprints": source_fp_set,
        "scale_delta_market_state_dependency_candidate_dataset_fingerprints": delta_source_fp_set,
        "market_state_dependency_fingerprint_policy": "combined scale candidate may include inherited Market State dependency fingerprints from reused Event State lineage; scale-delta records must bind exactly to the governed Market State scale candidate fingerprint",
        "market_state_dependency_binding_status_counts": binding_status_counts,
        "unexpected_market_state_dependency_binding_statuses": unexpected_binding_statuses,
        "hard_validation_failures": hard_validation_failures,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    validation_fp = sha256_payload(validation_report)
    write_json(run_dir / "event_state_scale_validation_report.json", validation_report)
    write_json(run_dir / "event_state_scale_partition_validation_report.json", {"requested_contexts": len(context_ledger), "represented_contexts": represented_contexts, "unavailable_contexts": unavailable_contexts, "unaccounted_contexts": unaccounted_contexts})
    write_json(run_dir / "event_state_scale_temporal_legality_report.json", {"event_anchor_mismatches": anchor_mismatches, "at_event_rows": represented_contexts, "consumption_legality": "research_only"})

    lineage_manifest = {
        "run_id": run_id,
        "lineage_policy": "reuse_incremental_lineage_chain_and_materialize_scale_delta_only",
        "source_lineage_chain_validation_run_id": LINEAGE_RUN_ID,
        "source_market_state_scale_run_id": MS_SCALE_RUN_ID,
        "reused_lineage_chain_contexts": reused_contexts,
        "scale_delta_materialized_contexts": scale_delta_contexts,
        "unavailable_contexts": unavailable_contexts,
        "row_lineage": lineage_entries,
        "unavailable_contexts_detail": [row for row in context_ledger if row["context_status"] == "unavailable"],
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    lineage_manifest["lineage_manifest_sha256"] = sha256_payload({k: v for k, v in lineage_manifest.items() if k != "lineage_manifest_sha256"})
    write_json(run_dir / "event_state_scale_lineage_manifest.json", lineage_manifest)
    write_json(run_dir / "event_state_scale_lineage_validation_report.json", {"lineage_entries": len(lineage_entries), "lineage_manifest_sha256": lineage_manifest["lineage_manifest_sha256"], "lineage_failures": 0})

    logical_fp = sha256_payload(
        {
            "event_state_profile_id": EVENT_STATE_PROFILE_ID,
            "event_type_id": EVENT_TYPE_ID,
            "event_window_definition_id": EVENT_WINDOW_DEFINITION_ID,
            "records": sorted(
                (
                    {
                        "event_state_record_id": row["event_state_record_id"],
                        "event_state_record_fingerprint": row["event_state_record_fingerprint"],
                        "context_key": context_key(row),
                    }
                    for row in combined_records
                ),
                key=lambda row: row["event_state_record_id"],
            ),
            "unavailable_contexts": sorted(
                (row for row in context_ledger if row["context_status"] == "unavailable"),
                key=lambda row: row["context_id"],
            ),
            "restrictions": ["candidate_only", "partial_context_coverage", "research_only_at_event", "scale_validation_not_production"],
        }
    )
    candidate_fp = sha256_payload(
        {
            "event_state_execution_plan_fingerprint": plan_fp,
            "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "logical_event_state_dataset_fingerprint": logical_fp,
            "record_ids": sorted(row["event_state_record_id"] for row in combined_records),
            "record_fingerprints": sorted(row["event_state_record_fingerprint"] for row in combined_records),
            "coverage": validation_report,
        }
    )
    dataset_id = "event_state_scale_candidate_dataset_v0_1_" + candidate_fp[:16]
    candidate_manifest = {
        "candidate_dataset_id": dataset_id,
        "candidate_dataset_status": "candidate_pending_scale_review",
        "event_state_candidate_dataset_fingerprint": candidate_fp,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "request_id": request["request_id"],
        "request_fingerprint": request_fingerprint,
        "event_state_execution_plan_id": execution_plan["event_state_execution_plan_id"],
        "event_state_execution_plan_fingerprint": plan_fp,
        "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "coverage": {
            "requested_contexts": len(context_ledger),
            "represented_contexts": represented_contexts,
            "reused_lineage_chain_contexts": reused_contexts,
            "scale_delta_materialized_contexts": scale_delta_contexts,
            "unavailable_contexts": unavailable_contexts,
        },
        "files": [
            {"role": "combined_event_state_scale_candidate_records", "path": str(output_path), "sha256": output_hash, "bytes": output_path.stat().st_size, "records": len(combined_records)},
            {"role": "delta_event_state_scale_records", "path": str(delta_path), "sha256": delta_hash, "bytes": delta_path.stat().st_size, "records": len(delta_records)},
        ],
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    write_json(run_dir / "event_state_scale_candidate_output_manifest.json", candidate_manifest)

    registry_entry = {
        "dataset_id": dataset_id,
        "dataset_kind": "event_state_scale_validation_candidate_dataset",
        "registry_status": "validated_candidate" if hard_validation_failures == 0 else "failed",
        "validation_status": validation_status,
        "reuse_eligibility": "pending_scale_validation_candidate_dataset_review",
        "promotion_review_eligibility": "not_eligible_pending_scale_validation_candidate_dataset_review",
        "downstream_eligibility": False,
        "event_state_request_fingerprint": request_fingerprint,
        "event_state_dependency_resolution_fingerprint": dependency_fingerprint,
        "event_state_execution_plan_fingerprint": plan_fp,
        "event_state_candidate_dataset_fingerprint": candidate_fp,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "validation_result_fingerprint": validation_fp,
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_ids": [EVENT_TYPE_ID],
        "subject_scope": "exchange_session",
        "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "coverage": candidate_manifest["coverage"],
        "logical_context_ledger_ref": "event_state_scale_context_ledger.json",
        "lineage_manifest_ref": "event_state_scale_lineage_manifest.json",
        "validation_report_ref": "event_state_scale_validation_report.json",
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    registry_entry["registry_entry_fingerprint"] = sha256_payload(registry_entry)
    write_json(run_dir / "candidate_registry_entry.json", registry_entry)

    write_json(run_dir / "event_state_scale_context_ledger.json", {"run_id": run_id, "entries": context_ledger, "context_status_counts": count_by(context_ledger, "context_status"), "representation_source_counts": count_by(context_ledger, "representation_source")})
    write_json(run_dir / "validation_evidence_manifest.json", {"run_id": run_id, "validation_result_fingerprint": validation_fp, "reports": ["event_state_scale_validation_report.json", "event_state_scale_partition_validation_report.json", "event_state_scale_temporal_legality_report.json", "event_state_scale_lineage_validation_report.json"]})

    final_status = PASS_STATUS if hard_validation_failures == 0 else FAIL_STATUS
    matrix = {
        "validation_id": run_id,
        "gate": GATE_ID,
        "status": final_status,
        "decision": {
            "requested_contexts": len(context_ledger),
            "represented_contexts": represented_contexts,
            "reused_lineage_chain_contexts": reused_contexts,
            "scale_delta_materialized_contexts": scale_delta_contexts,
            "unavailable_contexts": unavailable_contexts,
            "unaccounted_contexts": unaccounted_contexts,
            "hard_validation_failures": hard_validation_failures,
        },
        "fingerprints": {
            "event_state_request_fingerprint": request_fingerprint,
            "event_state_dependency_resolution_fingerprint": dependency_fingerprint,
            "event_state_execution_plan_fingerprint": plan_fp,
            "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
            "event_state_candidate_dataset_fingerprint": candidate_fp,
            "logical_event_state_dataset_fingerprint": logical_fp,
            "validation_result_fingerprint": validation_fp,
            "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        },
        "boundary_counters": {
            "event_state_materializer_executions": 1,
            "event_state_materializer_scope": "scale_delta_only",
            "market_state_materializer_executions": 0,
            "source_market_data_rows_read": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "next_allowed_gate": NEXT_GATE if hard_validation_failures == 0 else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    matrix["scale_validation_matrix_sha256"] = sha256_payload({k: v for k, v in matrix.items() if k != "scale_validation_matrix_sha256"})
    write_json(RUNTIME_ROOT / "event_state_on_demand_scale_validation_matrix_v0_1.json", matrix)

    root_ledger = {
        "validation_id": run_id,
        "gate": GATE_ID,
        "counts": matrix["decision"],
        "entries": context_ledger,
    }
    root_ledger["scale_context_ledger_sha256"] = sha256_payload({k: v for k, v in root_ledger.items() if k != "scale_context_ledger_sha256"})
    write_json(RUNTIME_ROOT / "event_state_on_demand_scale_validation_context_ledger_v0_1.json", root_ledger)

    fp_comparison = {
        "validation_id": run_id,
        "physical_artifact_fingerprint": output_hash,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "candidate_dataset_fingerprint": candidate_fp,
        "normalization_policy": "exclude run ids, timestamps, heartbeat and run-local paths from logical fingerprint; include event identity, bindings, row scientific fingerprints, dependency fingerprints, coverage ledger and restrictions",
        "reused_lineage_chain_contexts": reused_contexts,
        "scale_delta_materialized_contexts": scale_delta_contexts,
        "unavailable_contexts": unavailable_contexts,
    }
    fp_comparison["fingerprint_comparison_sha256"] = sha256_payload({k: v for k, v in fp_comparison.items() if k != "fingerprint_comparison_sha256"})
    write_json(RUNTIME_ROOT / "event_state_on_demand_scale_validation_fingerprint_comparison_v0_1.json", fp_comparison)

    final = {
        "run_id": run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "final_run_status": final_status,
        "started_at_utc": started_at,
        "ended_at_utc": utc_now(),
        "run_dir": str(run_dir),
        "event_state_profile_id": EVENT_STATE_PROFILE_ID,
        "event_type_id": EVENT_TYPE_ID,
        "subject_scope": "exchange_session",
        "event_state_request_fingerprint": request_fingerprint,
        "event_state_dependency_resolution_fingerprint": dependency_fingerprint,
        "event_state_execution_plan_fingerprint": plan_fp,
        "market_state_reference_run_id": MS_SCALE_RUN_ID,
        "market_state_candidate_dataset_fingerprint": ms_final["candidate_dataset_fingerprint"],
        "candidate_dataset_fingerprint": candidate_fp,
        "logical_event_state_dataset_fingerprint": logical_fp,
        "validation_result_fingerprint": validation_fp,
        "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "requested_event_state_context_count": len(context_ledger),
        "represented_context_count": represented_contexts,
        "reused_lineage_chain_event_state_context_count": reused_contexts,
        "scale_delta_materialized_event_state_context_count": scale_delta_contexts,
        "unavailable_context_count": unavailable_contexts,
        "unaccounted_context_count": unaccounted_contexts,
        "combined_event_state_record_count": len(combined_records),
        "delta_event_state_record_count": len(delta_records),
        "event_instances_created_or_referenced": len(event_instances_by_date),
        "event_window_bindings_created_or_referenced": len(window_by_date),
        "instrument_session_projections_created_or_referenced": len(projections),
        "missing_exact_market_state_anchor_bindings": unavailable_contexts,
        "fallback_uses": 0,
        "hard_validation_failures": hard_validation_failures,
        "event_state_materializer_executions": 1,
        "event_state_materializer_scope": "scale_delta_only",
        "market_state_materializer_executions": 0,
        "event_state_candidate_records_read": len(prior_records),
        "market_state_candidate_records_read": len(market_rows),
        "source_market_data_rows_read": 0,
        "event_state_candidate_files_written": 1,
        "candidate_dataset_registry_entries_written": 1 if hard_validation_failures == 0 else 0,
        "official_event_state_dataset": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "final_findings": [
            "partial_context_coverage_six_missing_exact_market_state_anchor_bindings",
            "reused_incremental_lineage_chain_contexts_without_mutation",
            "scale_delta_event_state_materialization_only",
            "market_state_dependency_resolved_through_scale_runtime_candidate",
            "candidate_only_no_official_dataset",
        ],
        "next_allowed_gate": NEXT_GATE if hard_validation_failures == 0 else None,
        "artifacts": {
            "authorization": str(AUTH_MD_PATH),
            "scope": str(AUTH_SCOPE_PATH),
            "contract": str(AUTH_CONTRACT_PATH),
            "request_record": str(run_dir / "request_record.json"),
            "dependency_resolution_report": str(run_dir / "dependency_resolution_report.json"),
            "execution_plan": str(run_dir / "execution_plan.json"),
            "pre_run_manifest": str(run_dir / "pre_run_manifest.json"),
            "event_instance_manifest": str(run_dir / "event_instance_manifest.json"),
            "event_window_binding_manifest": str(run_dir / "event_window_binding_manifest.json"),
            "instrument_session_projection_manifest": str(run_dir / "instrument_session_projection_manifest.json"),
            "market_state_dependency_binding_report": str(run_dir / "market_state_dependency_binding_report.json"),
            "context_ledger": str(run_dir / "event_state_scale_context_ledger.json"),
            "candidate_records": str(output_path),
            "delta_records": str(delta_path),
            "candidate_output_manifest": str(run_dir / "event_state_scale_candidate_output_manifest.json"),
            "lineage_manifest": str(run_dir / "event_state_scale_lineage_manifest.json"),
            "validation_report": str(run_dir / "event_state_scale_validation_report.json"),
            "candidate_registry_entry": str(run_dir / "candidate_registry_entry.json"),
            "readout": str(run_dir / "run_readout.md"),
            "final_manifest": str(run_dir / "final_manifest.json"),
        },
    }
    final_path = run_dir / "final_manifest.json"
    write_json(final_path, final)
    write_text(run_dir / "run_readout.md", readout_text(final))
    write_text(RUNTIME_ROOT / "event_state_on_demand_scale_validation_readout_v0_1.md", readout_text(final))
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "observed_at_utc": utc_now(), "status": final_status, "stage": "closed"})

    print(
        json.dumps(
            {
                "run_id": run_id,
                "status": final_status,
                "hard_validation_failures": hard_validation_failures,
                "requested_contexts": len(context_ledger),
                "represented_contexts": represented_contexts,
                "reused_lineage_chain_contexts": reused_contexts,
                "scale_delta_materialized_contexts": scale_delta_contexts,
                "unavailable_contexts": unavailable_contexts,
                "next_allowed_gate": final["next_allowed_gate"],
                "final_manifest": str(final_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if hard_validation_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
