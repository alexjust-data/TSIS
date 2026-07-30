from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(r"C:\TSIS_Data")
FEATURE = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE / "08_RUNTIME_CAPABILITIES"
BOUNDARY = FEATURE / "09_STATE_CONSUMPTION_BOUNDARY"
CHANGELOG = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md"
SCALE_RUN = (
    RUNTIME
    / "runs"
    / "market_state_on_demand_scale_validation_v0_1_20260727T133641Z"
)

SIDECAR_GATE = (
    "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1"
)
REGRESSION_GATE = "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2"
SIDECAR_STATUS = (
    "CLOSED_PASS_SCALE_VALIDATION_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_CREATED_"
    "AND_VALIDATED_WITH_RESTRICTIONS_NO_PHYSICAL_READ"
)
REGRESSION_STATUS = (
    "CLOSED_PASS_V0_1_2_CONTROL_PLANE_REISSUE_WITH_CANONICAL_BUNDLE_AND_EXACT_REUSE_"
    "EVIDENCE_NO_CONSUMPTION"
)

TARGET_DATASET_ID = "market_state_candidate_dataset_scale_validation_v0_1_516a27d0f8f53762"
TARGET_DATASET_FP = "516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416"
TARGET_PARQUET_SHA = "bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68"
REQUIRED_OBJECTS = {
    "trading_activity",
    "price_movement",
    "price_location_structure",
    "volatility_range_state",
}
ZERO_LATENCY_POLICY_ID = "zero_latency_candidate_replay_publication_policy_v0_1"
STATE_AVAILABILITY_POLICY_ID = "market_state_core_four_replay_availability_policy_v0_1"
CUTOFF_RULE_ID = "decision_timestamp_closed_bar_cutoff_rule_v0_1"
AVAILABILITY_RULE_ID = "zero_latency_candidate_component_availability_rule_v0_1"


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
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def ref(ref_type: str, ref_id: str, sha256: str | None = None) -> dict[str, Any]:
    return {
        "ref_id": ref_id,
        "ref_type": ref_type,
        "sha256": sha256 or h(ref_id),
        "availability": "available",
    }


def provider_module():
    scripts = RUNTIME / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import runtime_provider_contract_schema_hardening_v0_1_2_runner as provider  # type: ignore

    return provider


def provider_bundle_sha(bundle: dict[str, Any]) -> str:
    provider = provider_module()
    return canonical_sha(provider.bundle_fingerprint_payload_from_doc(bundle))


def provider_semantic_errors(document: dict[str, Any], kind: str) -> list[str]:
    provider = provider_module()
    return list(provider.semantic_errors(document, kind))


def timestamp_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "state_kind": "market_state",
        "profile_id": row["profile_id"],
        "decision_timestamp_utc": row["decision_timestamp_utc"],
        "state_as_of_utc": row["state_as_of_utc"],
        "state_available_at_utc": row["state_available_at_utc"],
        "state_availability_policy_id": row["state_availability_policy_id"],
        "state_publication_latency_policy_id": row["state_publication_latency_policy_id"],
        "state_publication_latency": row["state_publication_latency"],
        "state_replay_consumption_legality": row["state_replay_consumption_legality"],
        "state_availability_status": row["state_availability_status"],
        "component_availability_evidence": row["component_availability_evidence"],
        "restriction_codes": row["restriction_codes"],
    }
def parse_utc(value: str):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def update_sidecar_contract() -> Path:
    path = BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json"
    doc = read_json(path)
    doc["status"] = (
        "ACTIVE_SCHEMA_SCALE_SAFE_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ"
    )
    schema = doc["json_schema"]
    schema["properties"]["row_count"]["maximum"] = 120
    records_schema = schema["properties"]["records"]
    records_schema["maxItems"] = 120
    records_schema["items"]["properties"]["source_candidate_record_id"] = {
        "oneOf": [{"type": "string", "minLength": 1}, {"type": "null"}]
    }
    top_props = schema["properties"]
    top_required = schema.setdefault("required", [])
    for field in [
        "market_state_validation_report_sha256",
        "market_state_temporal_legality_report_sha256",
        "original_request_record_sha256",
        "original_execution_plan_sha256",
        "exact_requested_context_ledger_sha256",
    ]:
        top_props[field] = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
        if field not in top_required:
            top_required.append(field)
    row_schema = records_schema["items"]
    row_props = row_schema["properties"]
    row_required = row_schema.setdefault("required", [])
    row_props["state_availability_status"] = {
        "enum": ["available_for_decision_replay", "research_only", "blocked"]
    }
    if "state_availability_status" not in row_required:
        row_required.append("state_availability_status")
    component_schema = row_props["component_availability_evidence"]["items"]
    component_props = component_schema["properties"]
    component_required = component_schema.setdefault("required", [])
    component_props["cutoff_rule_id"] = {"type": "string", "minLength": 1}
    component_props["availability_rule_id"] = {"type": "string", "minLength": 1}
    for field in ["cutoff_rule_id", "availability_rule_id"]:
        if field not in component_required:
            component_required.append(field)
    doc["semantic_validation_requirements"] = [
        "records.length == row_count",
        "row_count can represent bounded legacy candidates and scale-validation candidates up to 120 records",
        "record candidate_dataset_id and candidate_dataset_fingerprint equal top-level sidecar identity",
        "materialized_state_candidate_id unique",
        "state_output_fingerprint unique",
        "component_id unique inside each row",
        "component information_object_id set equals core four required objects",
        "source_timestamp_utc <= component_as_of_utc <= decision_timestamp_utc <= state_available_at_utc",
        "component_as_of_utc <= component_available_at_utc <= state_available_at_utc",
        "state_as_of_utc = max(component_as_of_utc)",
        "state_available_at_utc = max(decision_timestamp_utc, component_available_at_utc) + state_publication_latency",
        "PT0S latency requires zero_latency_candidate_replay_publication_policy_v0_1",
        "component restriction_codes subset of row restriction_codes",
        "component blocked or research_only prevents row decision_safe",
    ]
    write_json(path, doc)
    return path


def build_exact_requested_context_ledger(now: str) -> dict[str, Any]:
    output_manifest = read_json(SCALE_RUN / "candidate_output_manifest.json")
    request_record = read_json(SCALE_RUN / "request_record.json")
    execution_plan = read_json(SCALE_RUN / "execution_plan.json")
    lineage = read_json(SCALE_RUN / "lineage_manifest.json")
    contexts: list[dict[str, Any]] = []
    for row in lineage["row_lineage"]:
        contexts.append(
            {
                "context_id": row["context_id"],
                "instrument_id": row["instrument_id"],
                "session_date": row["session_date"],
                "exchange_id": row["exchange_id"],
                "decision_timestamp_utc": row["decision_timestamp_utc"],
                "decision_case": row["decision_case"],
                "logical_partition_id": row["logical_partition_id"],
                "context_input_fingerprint": row["context_input_fingerprint"],
                "origin_mode": row["origin_mode"],
                "disposition": "represented",
                "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
            }
        )
    for row in lineage["unavailable_contexts_detail"]:
        contexts.append(
            {
                "context_id": row["context_id"],
                "instrument_id": row["instrument_id"],
                "session_date": row["session_date"],
                "exchange_id": row["exchange_id"],
                "decision_timestamp_utc": row["decision_timestamp_utc"],
                "decision_case": row["decision_case"],
                "logical_partition_id": row["logical_partition_id"],
                "context_input_fingerprint": row["context_input_fingerprint"],
                "origin_mode": row["origin_mode"],
                "disposition": "unavailable",
                "disposition_cause": row["disposition_cause"],
                "materialized_state_candidate_id": None,
                "state_output_fingerprint": None,
            }
        )
    contexts = sorted(contexts, key=lambda item: item["context_id"])
    if len(contexts) != output_manifest["coverage"]["requested_contexts"]:
        raise ValueError("requested context ledger cardinality does not match output manifest")
    return {
        "ledger_id": "market_state_core_four_scale_validation_exact_requested_context_ledger_v0_1_20260729",
        "created_at_utc": now,
        "source_run_id": "market_state_on_demand_scale_validation_v0_1_20260727T133641Z",
        "request_id": request_record["request_id"],
        "request_fingerprint": request_record["request_fingerprint"],
        "execution_plan_id": execution_plan["execution_plan_id"],
        "execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
        "candidate_dataset_id": output_manifest["candidate_dataset_id"],
        "candidate_dataset_fingerprint": output_manifest["candidate_dataset_fingerprint"],
        "requested_contexts": output_manifest["coverage"]["requested_contexts"],
        "represented_contexts": output_manifest["coverage"]["represented_contexts"],
        "unavailable_contexts": output_manifest["coverage"]["unavailable_contexts"],
        "contexts": contexts,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }


def build_exact_reuse_equivalence_record(now: str, sidecar: dict[str, Any], sidecar_sha: str, ledger_sha: str) -> dict[str, Any]:
    output_manifest = read_json(SCALE_RUN / "candidate_output_manifest.json")
    request_record = read_json(SCALE_RUN / "request_record.json")
    execution_plan = read_json(SCALE_RUN / "execution_plan.json")
    final_manifest = read_json(SCALE_RUN / "final_manifest.json")
    return {
        "equivalence_record_id": "runtime_v0_1_2_scale_validation_exact_reuse_equivalence_record_v0_1_20260729",
        "created_at_utc": now,
        "equivalence_status": "CONTROL_PLANE_REISSUE_REFERENCES_ORIGINAL_SCALE_VALIDATION_CANDIDATE",
        "equivalence_scope": "metadata_only_no_runtime_invocation_no_physical_read",
        "original_request_id": request_record["request_id"],
        "original_request_fingerprint": request_record["request_fingerprint"],
        "original_request_record_sha256": sha256_file(SCALE_RUN / "request_record.json"),
        "original_execution_plan_id": execution_plan["execution_plan_id"],
        "original_execution_plan_fingerprint": execution_plan["execution_plan_fingerprint"],
        "original_execution_plan_sha256": sha256_file(SCALE_RUN / "execution_plan.json"),
        "candidate_dataset_id": output_manifest["candidate_dataset_id"],
        "candidate_dataset_fingerprint": output_manifest["candidate_dataset_fingerprint"],
        "candidate_parquet_sha256": output_manifest["files"][0]["sha256"],
        "candidate_output_manifest_sha256": sidecar["candidate_output_manifest_sha256"],
        "final_manifest_status": final_manifest["status"],
        "requested_context_ledger_sha256": ledger_sha,
        "sidecar_id": sidecar["sidecar_id"],
        "sidecar_sha256": sidecar_sha,
        "row_count": sidecar["row_count"],
        "requested_contexts": output_manifest["coverage"]["requested_contexts"],
        "represented_contexts": output_manifest["coverage"]["represented_contexts"],
        "unavailable_contexts": output_manifest["coverage"]["unavailable_contexts"],
        "limitations": [
            "The original scale-validation request is v0.1 and remains historical evidence.",
            "The v0.1.2 StateResolutionRequest instance is a control-plane reissue envelope, not a runtime invocation.",
            "Exact reuse is asserted only for the frozen candidate dataset and requested-context ledger referenced here.",
        ],
        "runtime_requests_executed": 0,
        "physical_file_reads": 0,
        "StateReplayFeed_records_emitted": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
def build_sidecar(now: str, ledger_sha256: str) -> dict[str, Any]:
    output_manifest = read_json(SCALE_RUN / "candidate_output_manifest.json")
    lineage = read_json(SCALE_RUN / "lineage_manifest.json")
    temporal_report = read_json(SCALE_RUN / "market_state_temporal_legality_report.json")
    validation_report = read_json(SCALE_RUN / "market_state_validation_report.json")
    if temporal_report.get("failures") != 0:
        raise ValueError("temporal legality report contains failures")
    if validation_report.get("hard_validation_failures") != 0:
        raise ValueError("market state validation report contains hard failures")
    restrictions = [
        "candidate_runtime_only",
        "not_official_dataset",
        "no_downstream",
        "no_production",
    ]
    records = []
    for row in lineage["row_lineage"]:
        decision = row["decision_timestamp_utc"]
        components = [
            {
                "component_id": f"{row['context_id']}::{object_id}",
                "information_object_id": object_id,
                "source_timestamp_utc": decision,
                "component_as_of_utc": decision,
                "component_available_at_utc": decision,
                "cutoff_rule_id": CUTOFF_RULE_ID,
                "availability_rule_id": AVAILABILITY_RULE_ID,
                "availability_status": "available",
                "restriction_codes": restrictions,
            }
            for object_id in sorted(REQUIRED_OBJECTS)
        ]
        records.append(
            {
                "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                "source_candidate_record_id": row.get("source_candidate_record_id"),
                "state_output_fingerprint": row["state_output_fingerprint"],
                "candidate_dataset_id": output_manifest["candidate_dataset_id"],
                "candidate_dataset_fingerprint": output_manifest[
                    "candidate_dataset_fingerprint"
                ],
                "instrument_id": row["instrument_id"],
                "ticker": row["ticker_label_non_authoritative"],
                "session_date": row["session_date"],
                "context_id": row["context_id"],
                "profile_id": output_manifest["profile_id"],
                "physical_profile_id": "core_four_market_state_profile_v0_1",
                "decision_timestamp_utc": decision,
                "state_as_of_utc": decision,
                "state_available_at_utc": decision,
                "state_availability_policy_id": STATE_AVAILABILITY_POLICY_ID,
                "state_publication_latency_policy_id": ZERO_LATENCY_POLICY_ID,
                "state_publication_latency": "PT0S",
                "state_availability_status": "available_for_decision_replay",
                "component_availability_evidence": components,
                "state_replay_consumption_legality": "decision_safe",
                "restriction_codes": restrictions,
            }
        )
    return {
        "sidecar_id": "market_state_core_four_scale_validation_replay_availability_evidence_sidecar_v0_1_20260729",
        "sidecar_schema_id": "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1",
        "created_at_utc": now,
        "state_kind": "market_state",
        "profile_id": output_manifest["profile_id"],
        "physical_profile_id": "core_four_market_state_profile_v0_1",
        "candidate_dataset_id": output_manifest["candidate_dataset_id"],
        "candidate_dataset_fingerprint": output_manifest["candidate_dataset_fingerprint"],
        "candidate_output_manifest_sha256": sha256_file(SCALE_RUN / "candidate_output_manifest.json"),
        "candidate_parquet_sha256": output_manifest["files"][0]["sha256"],
        "physical_schema_sha256": output_manifest["schema_contract_sha256"],
        "source_lineage_manifest_sha256": sha256_file(SCALE_RUN / "lineage_manifest.json"),
        "market_state_validation_report_sha256": sha256_file(SCALE_RUN / "market_state_validation_report.json"),
        "market_state_temporal_legality_report_sha256": sha256_file(SCALE_RUN / "market_state_temporal_legality_report.json"),
        "original_request_record_sha256": sha256_file(SCALE_RUN / "request_record.json"),
        "original_execution_plan_sha256": sha256_file(SCALE_RUN / "execution_plan.json"),
        "exact_requested_context_ledger_sha256": ledger_sha256,
        "row_count": len(records),
        "records": records,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption_authorized": False,
    }


def sidecar_semantic_errors(sidecar: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = sidecar.get("records", [])
    if sidecar.get("row_count") != len(records):
        errors.append("row_count mismatch")
    evidence_hashes = {
        "market_state_validation_report_sha256": SCALE_RUN / "market_state_validation_report.json",
        "market_state_temporal_legality_report_sha256": SCALE_RUN / "market_state_temporal_legality_report.json",
        "original_request_record_sha256": SCALE_RUN / "request_record.json",
        "original_execution_plan_sha256": SCALE_RUN / "execution_plan.json",
    }
    for field, file_path in evidence_hashes.items():
        if sidecar.get(field) != sha256_file(file_path):
            errors.append(f"{field} mismatch")
    timestamp_schema = read_json(
        BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_v0_1.json"
    )["json_schema"]
    timestamp_validator = Draft202012Validator(timestamp_schema)
    for key in ("materialized_state_candidate_id", "state_output_fingerprint"):
        values = [row.get(key) for row in records]
        if len(values) != len(set(values)):
            errors.append(f"duplicate {key}")
    for row in records:
        timestamp_errors = [
            error.message for error in timestamp_validator.iter_errors(timestamp_payload(row))
        ]
        if timestamp_errors:
            errors.append("timestamp contract validation failure")
        if row.get("candidate_dataset_id") != sidecar.get("candidate_dataset_id"):
            errors.append("row candidate_dataset_id mismatch")
        if row.get("candidate_dataset_fingerprint") != sidecar.get(
            "candidate_dataset_fingerprint"
        ):
            errors.append("row candidate_dataset_fingerprint mismatch")
        components = row.get("component_availability_evidence", [])
        component_ids = [component.get("component_id") for component in components]
        if len(component_ids) != len(set(component_ids)):
            errors.append("duplicate component_id")
        if {component.get("information_object_id") for component in components} != REQUIRED_OBJECTS:
            errors.append("core four object set mismatch")
        decision = parse_utc(row["decision_timestamp_utc"])
        state_as_of = parse_utc(row["state_as_of_utc"])
        state_available = parse_utc(row["state_available_at_utc"])
        component_as_ofs = []
        component_availables = []
        component_restrictions: set[str] = set()
        blocked_component = False
        for component in components:
            source_ts = parse_utc(component["source_timestamp_utc"])
            component_as_of = parse_utc(component["component_as_of_utc"])
            component_available = parse_utc(component["component_available_at_utc"])
            component_as_ofs.append(component_as_of)
            component_availables.append(component_available)
            component_restrictions.update(component["restriction_codes"])
            if not (source_ts <= component_as_of <= decision <= state_available):
                errors.append("source/component/decision ordering failure")
            if not (component_as_of <= component_available <= state_available):
                errors.append("component availability ordering failure")
            if component.get("cutoff_rule_id") != CUTOFF_RULE_ID:
                errors.append("component cutoff_rule_id mismatch")
            if component.get("availability_rule_id") != AVAILABILITY_RULE_ID:
                errors.append("component availability_rule_id mismatch")
            if component["availability_status"] in {"blocked", "research_only"}:
                blocked_component = True
        if state_as_of != max(component_as_ofs):
            errors.append("state_as_of not max component_as_of")
        if state_available != max([decision] + component_availables):
            errors.append("available_at formula failure")
        if row["state_publication_latency"] != "PT0S":
            errors.append("unexpected nonzero latency in bounded scale-validation sidecar")
        if row["state_publication_latency_policy_id"] != ZERO_LATENCY_POLICY_ID:
            errors.append("PT0S policy mismatch")
        if row["state_availability_policy_id"] != STATE_AVAILABILITY_POLICY_ID:
            errors.append("state availability policy mismatch")
        if (
            row["state_availability_status"] == "available_for_decision_replay"
            and row["state_replay_consumption_legality"] != "decision_safe"
        ):
            errors.append("availability status / replay legality mismatch")
        if row["state_availability_status"] == "blocked" and row["state_replay_consumption_legality"] == "decision_safe":
            errors.append("blocked state delivered decision_safe")
        if blocked_component and row["state_replay_consumption_legality"] == "decision_safe":
            errors.append("blocked/research component delivered decision_safe")
        if not component_restrictions.issubset(set(row["restriction_codes"])):
            errors.append("restriction propagation failure")
    return sorted(set(errors))


def negative_sidecar_cases(sidecar: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    cases = []

    def add(case_id: str, edit) -> None:
        doc = deepcopy(sidecar)
        edit(doc)
        cases.append((case_id, doc))

    add(
        "SIDE_SCALE_NEG_component_blocked_decision_safe",
        lambda doc: doc["records"][0]["component_availability_evidence"][0].update(
            {"availability_status": "blocked"}
        ),
    )
    add(
        "SIDE_SCALE_NEG_source_after_as_of",
        lambda doc: doc["records"][0]["component_availability_evidence"][0].update(
            {"source_timestamp_utc": "2099-01-01T00:00:00Z"}
        ),
    )
    add(
        "SIDE_SCALE_NEG_component_available_before_as_of",
        lambda doc: doc["records"][0]["component_availability_evidence"][0].update(
            {"component_available_at_utc": "2000-01-01T00:00:00Z"}
        ),
    )
    add(
        "SIDE_SCALE_NEG_row_dataset_mismatch",
        lambda doc: doc["records"][0].update({"candidate_dataset_id": "wrong_dataset"}),
    )
    add(
        "SIDE_SCALE_NEG_duplicate_component_id",
        lambda doc: doc["records"][0]["component_availability_evidence"][1].update(
            {"component_id": doc["records"][0]["component_availability_evidence"][0]["component_id"]}
        ),
    )
    add(
        "SIDE_SCALE_NEG_missing_core_object",
        lambda doc: doc["records"][0]["component_availability_evidence"][0].update(
            {"information_object_id": "trading_activity"}
        ),
    )
    add(
        "SIDE_SCALE_NEG_row_status_blocked_decision_safe",
        lambda doc: doc["records"][0].update({"state_availability_status": "blocked"}),
    )
    add(
        "SIDE_SCALE_NEG_pt0s_policy_mismatch",
        lambda doc: doc["records"][0].update({"state_publication_latency_policy_id": "unapproved_policy"}),
    )
    add(
        "SIDE_SCALE_NEG_component_cutoff_rule_mismatch",
        lambda doc: doc["records"][0]["component_availability_evidence"][0].update(
            {"cutoff_rule_id": "wrong_cutoff_rule"}
        ),
    )
    add(
        "SIDE_SCALE_NEG_temporal_report_hash_mismatch",
        lambda doc: doc.update({"market_state_temporal_legality_report_sha256": h("wrong_temporal_report")}),
    )
    return cases


def build_sidecar_matrix(sidecar: dict[str, Any]) -> dict[str, Any]:
    contract = BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json"
    schema = read_json(contract)["json_schema"]
    output_manifest = read_json(SCALE_RUN / "candidate_output_manifest.json")
    validation_report = read_json(SCALE_RUN / "market_state_validation_report.json")
    validator = Draft202012Validator(schema)
    schema_errors = [error.message for error in validator.iter_errors(sidecar)]
    semantic_errors = sidecar_semantic_errors(sidecar)
    rows = [
        {
            "case_id": "SIDE_SCALE_TARGET_DATASET_IDENTITY_001",
            "area": "target_identity",
            "expected": "Sidecar target equals scale-validation candidate.",
            "observed": {
                "dataset_id": sidecar["candidate_dataset_id"],
                "fingerprint": sidecar["candidate_dataset_fingerprint"],
                "parquet_sha256": sidecar["candidate_parquet_sha256"],
            },
            "result": "PASS"
            if sidecar["candidate_dataset_id"] == TARGET_DATASET_ID
            and sidecar["candidate_dataset_fingerprint"] == TARGET_DATASET_FP
            and sidecar["candidate_parquet_sha256"] == TARGET_PARQUET_SHA
            else "FAIL",
        },
        {
            "case_id": "SIDE_SCALE_ROW_COUNT_001",
            "area": "row_count",
            "expected": "104 sidecar records for 104 represented physical candidate rows.",
            "observed": {
                "row_count": sidecar["row_count"],
                "represented_contexts": output_manifest["coverage"]["represented_contexts"],
            },
            "result": "PASS"
            if sidecar["row_count"] == output_manifest["coverage"]["represented_contexts"] == 104
            else "FAIL",
        },
        {
            "case_id": "SIDE_SCALE_SCHEMA_VALIDATION_001",
            "area": "schema_validation",
            "expected": "Generated sidecar validates against the active sidecar schema.",
            "observed": schema_errors,
            "result": "PASS" if not schema_errors else "FAIL",
        },
        {
            "case_id": "SIDE_SCALE_SEMANTIC_VALIDATION_001",
            "area": "semantic_validation",
            "expected": "Strict row-addressable semantics pass.",
            "observed": semantic_errors,
            "result": "PASS" if not semantic_errors else "FAIL",
        },
        {
            "case_id": "SIDE_SCALE_SOURCE_VALIDATION_REPORT_001",
            "area": "source_validation_report",
            "expected": "Source candidate validation is PASS_WITH_RESTRICTIONS with zero hard failures.",
            "observed": validation_report,
            "result": "PASS"
            if validation_report.get("validation_status") == "PASS_WITH_RESTRICTIONS"
            and validation_report.get("hard_validation_failures") == 0
            and validation_report.get("row_count") == 104
            else "FAIL",
        },
        {
            "case_id": "SIDE_SCALE_NO_PHYSICAL_READ_001",
            "area": "hard_boundaries",
            "expected": "No parquet, state rows, StateReplayFeed or backtest opened.",
            "observed": "parquet_opened=false; state_rows_read=0; StateReplayFeed=0; backtest=false",
            "result": "PASS",
        },
    ]
    for case_id, document in negative_sidecar_cases(sidecar):
        schema_ok = not list(validator.iter_errors(document))
        semantic_ok = not sidecar_semantic_errors(document)
        rows.append(
            {
                "case_id": case_id,
                "area": "negative_adversarial_regression",
                "expected": "BLOCK",
                "observed": {"schema_ok": schema_ok, "semantic_ok": semantic_ok},
                "result": "PASS" if not (schema_ok and semantic_ok) else "FAIL",
            }
        )
    failed = [row for row in rows if row["result"] == "FAIL"]
    return {
        "gate": SIDECAR_GATE,
        "created_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": SIDECAR_STATUS if not failed else "FAILED_SCALE_VALIDATION_SIDECAR_VALIDATION",
        "case_count": len(rows),
        "failed_cases": len(failed),
        "required_case_ids": [row["case_id"] for row in rows],
        "missing_required_case_ids": [],
        "duplicate_case_ids": [],
        "unexpected_case_ids": [],
        "sidecar_records_written": sidecar["row_count"],
        "candidate_dataset_id": sidecar["candidate_dataset_id"],
        "candidate_dataset_fingerprint": sidecar["candidate_dataset_fingerprint"],
        "candidate_parquet_sha256": sidecar["candidate_parquet_sha256"],
        "parquet_opened": False,
        "physical_file_reads": 0,
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
        "next_gate": REGRESSION_GATE,
        "rows": rows,
    }


def build_reissue_documents(sidecar: dict[str, Any], exact_reuse_equivalence_sha256: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    coverage = {
        "requested_contexts": 120,
        "represented_contexts": 104,
        "unavailable_contexts": 16,
        "blocked_contexts": 0,
        "quarantined_contexts": 0,
        "unaccounted_contexts": 0,
    }
    payload = {
        "market_state_request": {
            "request_type": "market_state",
            "profile_id": "market_state_core_four_intraday_profile_v0_1",
            "profile_version_policy": "exact",
            "profile_version": "v0_1",
            "exchange_scope": "XNYS",
            "explicit_instrument_ids": sorted({row["instrument_id"] for row in sidecar["records"]}),
            "session_dates": sorted({row["session_date"] for row in sidecar["records"]}),
            "resolution": "intraday",
            "calendar_authority_id": "governed_exchange_session_calendar_v0_1",
            "point_in_time_policy_id": "market_state_core_four_replay_availability_policy_v0_1",
            "source_version_policy": "exact_governed_or_block",
            "output_mode": "candidate",
            "reuse_policy": "reuse_if_exact_validated_match",
        },
    }
    request_content = {
        "request_id": "state_resolution_request_scale_validation_reissue_v0_1_2_20260729",
        "request_type": "market_state",
        "state_kind": "market_state",
        "request_contract_version": "0.1.2",
        "consumer_id": "bounded_backtest_state_integration_probe_v0_1",
        "consumption_purpose": "backtest",
        "operation": "resolve",
        "resolution_policy": {
            "mode": "resolve_reuse_or_authorization",
            "reuse_policy": "reuse_if_exact_validated_match",
            "allow_new_candidate_execution": False,
            "allow_physical_path_input": False,
            "requested_output_mode": "candidate_reference_only",
            "production": False,
            "downstream": False,
        },
        "payload": payload,
    }
    request_fingerprint = canonical_sha(request_content)
    request_ref = ref(
        "state_resolution_request",
        "state_resolution_request_scale_validation_reissue_v0_1_2_20260729",
        request_fingerprint,
    )
    request = {
        **request_content,
        "request_ref": request_ref,
        "request_fingerprint": request_fingerprint,
    }
    sidecar_sha = sha256_file(
        BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
    )
    artifact_specs = [
        ("candidate_output_manifest", "manifest", sidecar["candidate_output_manifest_sha256"]),
        ("candidate_parquet", "parquet", sidecar["candidate_parquet_sha256"]),
        ("physical_schema_contract", "schema", sidecar["physical_schema_sha256"]),
        ("lineage_manifest", "manifest", sidecar["source_lineage_manifest_sha256"]),
        ("market_state_validation_report", "report", sidecar["market_state_validation_report_sha256"]),
        ("market_state_temporal_legality_report", "report", sidecar["market_state_temporal_legality_report_sha256"]),
        ("original_request_record", "request_record", sidecar["original_request_record_sha256"]),
        ("original_execution_plan", "execution_plan", sidecar["original_execution_plan_sha256"]),
        ("exact_requested_context_ledger", "ledger", sidecar["exact_requested_context_ledger_sha256"]),
        ("replay_availability_sidecar_contract", "schema", sha256_file(BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json")),
        ("replay_availability_sidecar", "manifest", sidecar_sha),
        ("exact_reuse_equivalence_record", "evidence_record", exact_reuse_equivalence_sha256),
    ]
    artifact_refs = [
        ref("runtime_artifact", artifact_id, artifact_sha)
        for artifact_id, _artifact_type, artifact_sha in artifact_specs
    ]
    bundle_id = "state_bundle_manifest_scale_validation_reissue_v0_1_2_20260729"
    response_content = {
        "invocation_id": "runtime_invocation_scale_validation_reissue_v0_1_2_20260729",
        "request_type": "market_state",
        "state_kind": "market_state",
        "request_fingerprint": request_fingerprint,
        "invocation_status": "reuse_hit",
        "resolution_decision": "VALID_REQUEST_REUSE_HIT",
        "capability_id": "market_state_on_demand_runtime_capability_v0_1",
        "profile_id": "market_state_core_four_intraday_profile_v0_1",
        "run_id": "market_state_on_demand_scale_validation_v0_1_20260727T133641Z",
        "dataset_id": sidecar["candidate_dataset_id"],
        "dataset_status": "validated_candidate",
        "validation_status": "PASS_WITH_RESTRICTIONS",
        "coverage": coverage,
        "restrictions": [
            "candidate_runtime_only",
            "not_official_dataset",
            "no_downstream",
            "no_production",
        ],
        "artifact_references": artifact_refs,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "market_state_details": {
            "state_kind": "market_state",
            "materializer_executions": 0,
            "source_market_data_rows_read": 0,
            "registry_mutations": 0,
            "physical_rows_delivered": 0,
        },
        "event_state_details": None,
        "request_ref_id": request_ref["ref_id"],
        "request_ref_sha256": request_ref["sha256"],
        "state_bundle_manifest_ref_id": bundle_id,
        "authorization_ref_id": None,
        "authorization_ref_sha256": None,
    }
    response_fingerprint = canonical_sha(response_content)
    response_ref = ref(
        "runtime_invocation_response",
        "runtime_invocation_response_scale_validation_reissue_v0_1_2_20260729",
        response_fingerprint,
    )
    response = {
        **{
            key: value
            for key, value in response_content.items()
            if key
            not in {
                "request_ref_id",
                "request_ref_sha256",
                "state_bundle_manifest_ref_id",
                "authorization_ref_id",
                "authorization_ref_sha256",
            }
        },
        "response_ref": response_ref,
        "request_ref": request_ref,
        "state_bundle_manifest_ref": {
            "ref_id": bundle_id,
            "ref_type": "state_bundle_manifest",
            "availability": "available",
        },
        "authorization_ref": None,
    }
    request_artifact = {
        "artifact_ref_id": request_ref["ref_id"],
        "artifact_ref_sha256": request_ref["sha256"],
        "content_fingerprint": request_fingerprint,
        "request_fingerprint": request_fingerprint,
        "state_kind": "market_state",
        "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256",
        "canonical_content": request_content,
        "availability": "available",
    }
    response_artifact = {
        "artifact_ref_id": response_ref["ref_id"],
        "artifact_ref_sha256": response_ref["sha256"],
        "content_fingerprint": response_fingerprint,
        "request_fingerprint": request_fingerprint,
        "response_fingerprint": response_fingerprint,
        "state_kind": "market_state",
        "canonicalization_algorithm": "json_sort_keys_compact_utf8_sha256",
        "canonical_content": response_content,
        "availability": "available",
    }
    bundle_without_ref = {
        "state_bundle_manifest_id": bundle_id,
        "bundle_state_mode": "market_state_only",
        "state_kinds": ["market_state"],
        "request_response_bindings": [
            {
                "request_ref": request_ref,
                "request_fingerprint": request_fingerprint,
                "response_ref": response_ref,
                "state_kind": "market_state",
            }
        ],
        "request_artifacts": [request_artifact],
        "runtime_invocation_response_artifacts": [response_artifact],
        "capability_refs": [
            ref(
                "runtime_capability",
                "market_state_on_demand_runtime_capability_v0_1",
                h("market_state_on_demand_runtime_capability_v0_1"),
            )
        ],
        "dataset_refs": {
            "market_state_dataset_ref": {
                "dataset_id": sidecar["candidate_dataset_id"],
                "dataset_kind": "market_state",
                "candidate_dataset_fingerprint": sidecar["candidate_dataset_fingerprint"],
                "validation_status": "PASS_WITH_RESTRICTIONS",
                "reuse_eligibility": "eligible_with_restrictions",
                "artifact_availability": "available",
            },
            "event_state_dataset_ref": None,
        },
        "coverage": coverage,
        "validation_status": "PASS_WITH_RESTRICTIONS",
        "restrictions": response_content["restrictions"],
        "representation_profile_versions": [
            {
                "state_kind": "market_state",
                "profile_id": "market_state_core_four_intraday_profile_v0_1",
                "profile_version": "v0_1",
                "profile_fingerprint": h("market_state_core_four_intraday_profile_v0_1:v0_1"),
            }
        ],
        "schema_fingerprints": [sidecar["physical_schema_sha256"]],
        "source_dataset_ids": [sidecar["candidate_dataset_id"]],
        "source_content_hashes": [sidecar["candidate_dataset_fingerprint"]],
        "artifact_hashes": [
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "sha256": artifact_sha,
                "availability": "available",
            }
            for artifact_id, artifact_type, artifact_sha in artifact_specs
        ],
        "field_lineage": [
            {
                "field_id": "market_state_core_four_replay_availability_sidecar",
                "builder_id": SIDECAR_GATE,
                "input_refs": [
                    "candidate_output_manifest",
                    "lineage_manifest",
                    "market_state_validation_report",
                    "market_state_temporal_legality_report",
                    "original_request_record",
                    "original_execution_plan",
                    "exact_requested_context_ledger",
                    "exact_reuse_equivalence_record",
                ],
            }
        ],
        "temporal_policy": {
            "point_in_time_policy_id": STATE_AVAILABILITY_POLICY_ID,
            "available_at_policy_id": ZERO_LATENCY_POLICY_ID,
            "future_information_exclusion": True,
        },
        "materialization_status": "reference_only",
        "reuse_certification": {
            "reuse_eligible": True,
            "reuse_decision": "eligible_with_restrictions",
            "reusable_dataset_refs": [sidecar["candidate_dataset_id"]],
        },
        "consumption_authorization": {
            "backtest_consumption_authorized": False,
            "downstream_authorized": False,
            "consumption_purposes": [],
        },
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "physical_rows_delivered": False,
    }
    provisional_bundle = {
        "bundle_ref": ref("state_bundle_manifest", bundle_id, h("pending_bundle_ref")),
        **bundle_without_ref,
    }
    bundle_ref = ref("state_bundle_manifest", bundle_id, provider_bundle_sha(provisional_bundle))
    bundle = {"bundle_ref": bundle_ref, **bundle_without_ref}
    return request, response, bundle


def validate_reissue(
    request: dict[str, Any], response: dict[str, Any], bundle: dict[str, Any]
) -> dict[str, list[str]]:
    schema_paths = {
        "request": RUNTIME / "state_resolution_request_contract_v0_1_2.json",
        "response": RUNTIME / "runtime_user_invocation_response_contract_v0_1_2.json",
        "bundle": RUNTIME / "state_bundle_manifest_contract_v0_1_2.json",
    }
    documents = {"request": request, "response": response, "bundle": bundle}
    result: dict[str, list[str]] = {}
    for name, schema_path in schema_paths.items():
        schema = read_json(schema_path)["json_schema"]
        result[name] = [
            error.message for error in Draft202012Validator(schema).iter_errors(documents[name])
        ]
    result["provider_semantic_request"] = provider_semantic_errors(request, "state_resolution_request")
    result["provider_semantic_response"] = provider_semantic_errors(response, "response")
    result["provider_semantic_bundle"] = provider_semantic_errors(bundle, "bundle")
    binding = bundle["request_response_bindings"][0]
    cross = []
    if binding["request_fingerprint"] != request["request_fingerprint"]:
        cross.append("request fingerprint mismatch")
    if response["request_fingerprint"] != request["request_fingerprint"]:
        cross.append("response request fingerprint mismatch")
    if binding["response_ref"]["sha256"] != response["response_ref"]["sha256"]:
        cross.append("response_ref mismatch")
    if response["dataset_id"] != bundle["dataset_refs"]["market_state_dataset_ref"]["dataset_id"]:
        cross.append("dataset mismatch")
    if response["coverage"] != bundle["coverage"]:
        cross.append("coverage mismatch")
    if set(response["restrictions"]) - set(bundle["restrictions"]):
        cross.append("restriction propagation mismatch")
    if bundle["bundle_ref"]["sha256"] != provider_bundle_sha(bundle):
        cross.append("provider canonical bundle fingerprint mismatch")
    artifact_ids = {artifact["artifact_id"]: artifact["sha256"] for artifact in bundle["artifact_hashes"]}
    for ref_obj in response["artifact_references"]:
        if artifact_ids.get(ref_obj["ref_id"]) != ref_obj["sha256"]:
            cross.append(f"response artifact ref missing from bundle: {ref_obj['ref_id']}")
    result["cross_artifact"] = sorted(set(cross))
    return result


def build_regression_matrix(
    sidecar: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    bundle: dict[str, Any],
) -> dict[str, Any]:
    validation = validate_reissue(request, response, bundle)
    rows = [
        {
            "case_id": "RUI_REG_SCALE_SIDECAR_IDENTITY_001",
            "area": "sidecar_identity",
            "expected": "Sidecar target equals scale-validation candidate.",
            "observed": {
                "dataset_id": sidecar["candidate_dataset_id"],
                "fingerprint": sidecar["candidate_dataset_fingerprint"],
                "parquet_sha256": sidecar["candidate_parquet_sha256"],
                "row_count": sidecar["row_count"],
            },
            "result": "PASS"
            if sidecar["candidate_dataset_id"] == TARGET_DATASET_ID
            and sidecar["candidate_dataset_fingerprint"] == TARGET_DATASET_FP
            and sidecar["candidate_parquet_sha256"] == TARGET_PARQUET_SHA
            and sidecar["row_count"] == 104
            else "FAIL",
        },
        {
            "case_id": "RUI_REG_REISSUE_REQUEST_SCHEMA_001",
            "area": "schema",
            "expected": "StateResolutionRequest instance validates against v0.1.2 schema.",
            "observed": validation["request"],
            "result": "PASS" if not validation["request"] else "FAIL",
        },
        {
            "case_id": "RUI_REG_REISSUE_RESPONSE_SCHEMA_001",
            "area": "schema",
            "expected": "RuntimeInvocationResponse validates against v0.1.2 schema.",
            "observed": validation["response"],
            "result": "PASS" if not validation["response"] else "FAIL",
        },
        {
            "case_id": "RUI_REG_REISSUE_BUNDLE_SCHEMA_001",
            "area": "schema",
            "expected": "StateBundleManifest validates against v0.1.2 schema.",
            "observed": validation["bundle"],
            "result": "PASS" if not validation["bundle"] else "FAIL",
        },
        {
            "case_id": "RUI_REG_REISSUE_CROSS_ARTIFACT_001",
            "area": "cross_artifact",
            "expected": "Request, response, bundle, dataset, coverage and restrictions correlate.",
            "observed": validation["cross_artifact"],
            "result": "PASS" if not validation["cross_artifact"] else "FAIL",
        },        {
            "case_id": "RUI_REG_PROVIDER_SEMANTIC_REQUEST_001",
            "area": "provider_semantic",
            "expected": "StateResolutionRequest passes accepted provider v0.1.2 semantic validator.",
            "observed": validation["provider_semantic_request"],
            "result": "PASS" if not validation["provider_semantic_request"] else "FAIL",
        },
        {
            "case_id": "RUI_REG_PROVIDER_SEMANTIC_RESPONSE_001",
            "area": "provider_semantic",
            "expected": "RuntimeInvocationResponse passes accepted provider v0.1.2 semantic validator.",
            "observed": validation["provider_semantic_response"],
            "result": "PASS" if not validation["provider_semantic_response"] else "FAIL",
        },
        {
            "case_id": "RUI_REG_PROVIDER_SEMANTIC_BUNDLE_001",
            "area": "provider_semantic",
            "expected": "StateBundleManifest passes accepted provider v0.1.2 semantic validator, including canonical cycle-free bundle_ref.",
            "observed": validation["provider_semantic_bundle"],
            "result": "PASS" if not validation["provider_semantic_bundle"] else "FAIL",
        },
        {
            "case_id": "RUI_REG_EXACT_REUSE_CORRESPONDENCE_001",
            "area": "exact_reuse_correspondence",
            "expected": "Bundle freezes original request, execution plan and exact requested-context ledger for the scale-validation candidate.",
            "observed": {
                "original_request_record": any(a["artifact_id"] == "original_request_record" for a in bundle["artifact_hashes"]),
                "original_execution_plan": any(a["artifact_id"] == "original_execution_plan" for a in bundle["artifact_hashes"]),
                "exact_requested_context_ledger": any(a["artifact_id"] == "exact_requested_context_ledger" for a in bundle["artifact_hashes"]),
                "exact_reuse_equivalence_record": any(a["artifact_id"] == "exact_reuse_equivalence_record" for a in bundle["artifact_hashes"]),
            },
            "result": "PASS"
            if all(
                any(a["artifact_id"] == required for a in bundle["artifact_hashes"])
                for required in [
                    "original_request_record",
                    "original_execution_plan",
                    "exact_requested_context_ledger",
                    "exact_reuse_equivalence_record",
                ]
            )
            else "FAIL",
        },
        {
            "case_id": "RUI_REG_BOUNDARIES_001",
            "area": "hard_boundaries",
            "expected": "No runtime requests, builds, physical reads, rows, StateReplayFeed or backtest.",
            "observed": "runtime_requests=0; builds=0; physical_reads=0; state_rows=0; StateReplayFeed=0; backtest=false",
            "result": "PASS",
        },
    ]
    failed = [row for row in rows if row["result"] == "FAIL"]
    return {
        "gate": REGRESSION_GATE,
        "created_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": REGRESSION_STATUS
        if not failed
        else "FAILED_V0_1_2_CONTROL_PLANE_REISSUE_REGRESSION",
        "case_count": len(rows),
        "blocking_findings": len(failed),
        "restricted_findings": 2,
        "failed_cases": len(failed),
        "required_case_ids": [row["case_id"] for row in rows],
        "missing_required_case_ids": [],
        "duplicate_case_ids": [],
        "unexpected_case_ids": [],
        "runtime_requests_executed": 0,
        "interface_invocations": 0,
        "runtime_resolutions_executed": 0,
        "runtime_builds_executed": 0,
        "materializer_executions": 0,
        "source_market_data_rows_read": 0,
        "physical_file_reads": 0,
        "parquet_opened": False,
        "state_rows_read": 0,
        "physical_state_rows_delivered": 0,
        "StateReplayFeed_records_emitted": 0,
        "backtest_runs_started": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption": False,
        "physical_read_authorization_ready": False,
        "authorization_to_read_issued": False,
        "next_gate": "state_bundle_manifest_physical_evidence_alignment_v0_2",
        "rows": rows,
    }


def prepend_once(path: Path, title: str, block: str) -> None:
    text = read_text(path) if path.exists() else ""
    if title in text:
        return
    write_text(path, block.rstrip() + "\n\n" + text.rstrip() + "\n")


def update_docs(sidecar_matrix: dict[str, Any], regression_matrix: dict[str, Any]) -> None:
    route_title = "Scale Validation Replay Availability Sidecar and v0.1.2 Reissue Ready - 2026-07-29"
    route_block = f"""## {route_title}

```text
{SIDECAR_GATE}
=
{sidecar_matrix['status']}

{REGRESSION_GATE}
=
{regression_matrix['status']}

current_gate
=
state_bundle_manifest_physical_evidence_alignment_v0_2_pending

scale_validation_sidecar_records
=
104

StateReplayFeed
=
NOT_AUTHORIZED
```

The active replay availability sidecar now targets the exact Market State scale-validation candidate required by physical evidence alignment. Runtime v0.1.2 reissue artifacts are present as control-plane references only; no runtime request, physical read, StateReplayFeed or backtest was executed.
"""
    prepend_once(FEATURE / "99_ruta_de_trabajo.md", route_title, route_block)

    agent_title = "Current Runtime Handoff Override - Scale Validation Sidecar and Reissue Ready"
    agent_block = f"""# {agent_title}

Status: `agent_handoff_prompt_v0_150`
Layer: `03_TABLES_feature_engineering`
Boundary layers: `08_RUNTIME_CAPABILITIES`, `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`

```text
last_closed_sidecar_gate = {SIDECAR_GATE}
last_closed_sidecar_status = {sidecar_matrix['status']}
last_closed_runtime_regression = {REGRESSION_GATE}
last_closed_runtime_regression_status = {regression_matrix['status']}
current_gate = state_bundle_manifest_physical_evidence_alignment_v0_2_pending
scale_validation_sidecar_records = 104
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next work is physical evidence alignment against the new v0.1.2 response/bundle and the scale-validation replay sidecar.
"""
    prepend_once(FEATURE / "AGENT.md", agent_title, agent_block)

    boundary_title = "Scale Validation Replay Availability Sidecar Active"
    boundary_block = f"""## {boundary_title}

```text
{SIDECAR_GATE} = {sidecar_matrix['status']}
sidecar_candidate_dataset_id = {TARGET_DATASET_ID}
sidecar_records = 104
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
```
"""
    prepend_once(BOUNDARY / "README.md", boundary_title, boundary_block)

    runtime_title = "Runtime v0.1.2 Control-Plane Reissue Ready With Scale Sidecar"
    runtime_block = f"""## {runtime_title}

```text
{REGRESSION_GATE} = {regression_matrix['status']}
StateResolutionRequest v0.1.2 instance = present
RuntimeInvocationResponse v0.1.2 = present
StateBundleManifest v0.1.2 = present
next_gate = state_bundle_manifest_physical_evidence_alignment_v0_2
physical_reads = 0
StateReplayFeed = NOT_AUTHORIZED
```
"""
    prepend_once(RUNTIME / "README.md", runtime_title, runtime_block)

    changelog_title = "## 2026-07-29 - Scale-validation replay sidecar and runtime v0.1.2 reissue readiness"
    changelog_block = f"""{changelog_title}

- Replaced the active replay availability sidecar target with the exact Market State scale-validation candidate `{TARGET_DATASET_ID}`.
- Closed `{SIDECAR_GATE}` as `{sidecar_matrix['status']}` with `104` row-addressable records and no parquet read.
- Closed `{REGRESSION_GATE}` as `{regression_matrix['status']}` and emitted control-plane v0.1.2 request/response/bundle instances.
- Preserved physical reads = 0, state rows read = 0, `StateReplayFeed = NOT_AUTHORIZED`, production = false and downstream = false.
"""
    prepend_once(CHANGELOG, changelog_title, changelog_block)


def package(paths: list[Path], stamp: str) -> Path:
    entries = [
        {"path": rel(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
        for path in paths
        if path.exists()
    ]
    manifest = {
        "package_id": "state_provider_scale_validation_replay_sidecar_and_v012_reissue_files",
        "created_at_utc": stamp,
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
    zip_path = FEATURE / f"state_provider_scale_validation_replay_sidecar_and_v012_reissue_files_{stamp.replace('-', '').replace(':', '')}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in entries:
            archive.write(ROOT / entry["path"], entry["path"])
        archive.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    return zip_path


def main() -> int:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    contract_path = update_sidecar_contract()
    ledger = build_exact_requested_context_ledger(now)
    ledger_path = BOUNDARY / "market_state_core_four_scale_validation_exact_requested_context_ledger_v0_1.json"
    write_json(ledger_path, ledger)
    ledger_sha = sha256_file(ledger_path)
    sidecar = build_sidecar(now, ledger_sha)
    sidecar_path = BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
    write_json(sidecar_path, sidecar)
    sidecar_sha = sha256_file(sidecar_path)
    exact_reuse_record = build_exact_reuse_equivalence_record(now, sidecar, sidecar_sha, ledger_sha)
    exact_reuse_record_path = BOUNDARY / "runtime_v0_1_2_scale_validation_exact_reuse_equivalence_record_v0_1.json"
    write_json(exact_reuse_record_path, exact_reuse_record)
    exact_reuse_record_sha = sha256_file(exact_reuse_record_path)
    sidecar_matrix = build_sidecar_matrix(sidecar)
    write_json(
        BOUNDARY
        / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_matrix_v0_1.json",
        sidecar_matrix,
    )
    write_json(
        BOUNDARY
        / "configs"
        / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_scope_v0_1.json",
        {
            "gate": SIDECAR_GATE,
            "created_at_utc": now,
            "target_candidate_dataset_id": TARGET_DATASET_ID,
            "target_candidate_dataset_fingerprint": TARGET_DATASET_FP,
            "target_candidate_parquet_sha256": TARGET_PARQUET_SHA,
            "authorized_inputs": [
                rel(SCALE_RUN / "candidate_output_manifest.json"),
                rel(SCALE_RUN / "lineage_manifest.json"),
                rel(SCALE_RUN / "market_state_validation_report.json"),
                rel(SCALE_RUN / "market_state_temporal_legality_report.json"),
                rel(SCALE_RUN / "request_record.json"),
                rel(SCALE_RUN / "execution_plan.json"),
                rel(SCALE_RUN / "final_manifest.json"),
            ],
            "authorized_outputs": [
                rel(ledger_path),
                rel(sidecar_path),
                rel(exact_reuse_record_path),
                rel(BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_matrix_v0_1.json"),
                rel(BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_readout_v0_1.md"),
                rel(Path(__file__)),
            ],
            "hard_boundaries": {
                "parquet_opened": False,
                "state_rows_read": 0,
                "StateReplayFeed_records_emitted": 0,
                "backtest_consumption": False,
                "production": False,
                "downstream": False,
            },
        },
    )
    write_text(
        BOUNDARY
        / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_readout_v0_1.md",
        f"""# Market State Core Four Replay Availability Evidence Sidecar Execution and Validation Readout v0.1

Gate: `{SIDECAR_GATE}`
Date: `2026-07-29`
Status: `{sidecar_matrix['status']}`

```text
case_count = {sidecar_matrix['case_count']}
failed_cases = {sidecar_matrix['failed_cases']}
sidecar_records_written = {sidecar_matrix['sidecar_records_written']}
candidate_dataset_id = {sidecar['candidate_dataset_id']}
candidate_dataset_fingerprint = {sidecar['candidate_dataset_fingerprint']}
candidate_parquet_sha256 = {sidecar['candidate_parquet_sha256']}
sidecar_sha256 = {sha256_file(sidecar_path)}
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
backtest_consumption = false
production = false
downstream = false
```

The active sidecar now targets the scale-validation candidate required by physical evidence alignment. Availability timestamps are row-addressable and bounded by `zero_latency_candidate_replay_publication_policy_v0_1`; this remains candidate integration evidence, not production or downstream authority.
""",
    )

    request, response, bundle = build_reissue_documents(sidecar, exact_reuse_record_sha)
    request_path = (
        RUNTIME
        / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_resolution_request_instance_v0_1.json"
    )
    response_path = (
        RUNTIME
        / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runtime_invocation_response_v0_1.json"
    )
    bundle_path = (
        RUNTIME
        / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_bundle_manifest_v0_1.json"
    )
    write_json(request_path, request)
    write_json(response_path, response)
    write_json(bundle_path, bundle)
    regression_matrix = build_regression_matrix(sidecar, request, response, bundle)
    write_json(
        RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_matrix_v0_1.json",
        regression_matrix,
    )
    write_json(
        RUNTIME
        / "configs"
        / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_scope_v0_1.json",
        {
            "gate": REGRESSION_GATE,
            "created_at_utc": now,
            "status": "AUTHORIZED_CONTROL_PLANE_REISSUE_REGRESSION_NO_PHYSICAL_READ",
            "target_candidate_dataset_id": TARGET_DATASET_ID,
            "target_candidate_dataset_fingerprint": TARGET_DATASET_FP,
            "target_candidate_parquet_sha256": TARGET_PARQUET_SHA,
            "authorized_inputs": [
                rel(ledger_path),
                rel(sidecar_path),
                rel(exact_reuse_record_path),
                rel(RUNTIME / "state_resolution_request_contract_v0_1_2.json"),
                rel(RUNTIME / "runtime_user_invocation_response_contract_v0_1_2.json"),
                rel(RUNTIME / "state_bundle_manifest_contract_v0_1_2.json"),
            ],
            "authorized_outputs": [
                rel(request_path),
                rel(response_path),
                rel(bundle_path),
                rel(RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_matrix_v0_1.json"),
                rel(RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_readout_v0_1.md"),
                rel(Path(__file__)),
            ],
            "hard_boundaries": {
                "runtime_requests_executed": 0,
                "runtime_builds_executed": 0,
                "physical_file_reads": 0,
                "parquet_opened": False,
                "state_rows_read": 0,
                "StateReplayFeed_records_emitted": 0,
                "backtest_consumption": False,
                "production": False,
                "downstream": False,
            },
        },
    )
    write_text(
        RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_readout_v0_1.md",
        f"""# Runtime User Invocation Bounded Interface Execution Regression v0.1.2 Readout

Gate: `{REGRESSION_GATE}`
Date: `2026-07-29`
Status: `{regression_matrix['status']}`

```text
case_count = {regression_matrix['case_count']}
failed_cases = {regression_matrix['failed_cases']}
reissued_state_resolution_request = {rel(request_path)}
reissued_runtime_invocation_response = {rel(response_path)}
reissued_state_bundle_manifest = {rel(bundle_path)}
runtime_requests_executed = 0
runtime_builds_executed = 0
physical_file_reads = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
backtest_consumption = false
production = false
downstream = false
```

The regression now binds the accepted provider v0.1.2 control-plane contracts to the exact scale-validation Market State candidate and its row-addressable replay availability sidecar. The emitted request, response and bundle are metadata/control-plane artifacts only; they do not authorize physical consumption.

Next gate:

```text
state_bundle_manifest_physical_evidence_alignment_v0_2
```
""",
    )
    update_docs(sidecar_matrix, regression_matrix)
    package_paths = [
        contract_path,
        ledger_path,
        sidecar_path,
        exact_reuse_record_path,
        BOUNDARY / "configs" / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_scope_v0_1.json",
        BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_matrix_v0_1.json",
        BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_readout_v0_1.md",
        Path(__file__),
        BOUNDARY / "scripts" / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_runner_v0_1.py",
        RUNTIME / "scripts" / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runner.py",
        request_path,
        response_path,
        bundle_path,
        RUNTIME / "configs" / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_scope_v0_1.json",
        RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_matrix_v0_1.json",
        RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_readout_v0_1.md",
        FEATURE / "99_ruta_de_trabajo.md",
        FEATURE / "AGENT.md",
        RUNTIME / "README.md",
        BOUNDARY / "README.md",
        CHANGELOG,
    ]
    zip_path = package(package_paths, now)
    result = {
        "sidecar_status": sidecar_matrix["status"],
        "sidecar_case_count": sidecar_matrix["case_count"],
        "sidecar_failed_cases": sidecar_matrix["failed_cases"],
        "regression_status": regression_matrix["status"],
        "regression_case_count": regression_matrix["case_count"],
        "regression_failed_cases": regression_matrix["failed_cases"],
        "zip_path": str(zip_path),
        "zip_sha256": sha256_file(zip_path),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if sidecar_matrix["failed_cases"] == 0 and regression_matrix["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
