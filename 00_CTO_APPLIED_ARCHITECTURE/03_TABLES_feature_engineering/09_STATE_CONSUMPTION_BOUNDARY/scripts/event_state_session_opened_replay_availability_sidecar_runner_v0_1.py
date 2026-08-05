#!/usr/bin/env python3
"""Build and validate one Event State replay-availability sidecar record."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

TABLES = Path(__file__).resolve().parents[2]
BOUNDARY = TABLES / "09_STATE_CONSUMPTION_BOUNDARY"
RUNTIME = TABLES / "08_RUNTIME_CAPABILITIES"
RUN = RUNTIME / "runs" / "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"

SCOPE = BOUNDARY / "configs" / "event_state_session_opened_replay_availability_sidecar_execution_scope_v0_1.json"
RECEIPT = BOUNDARY / "event_state_session_opened_replay_availability_sidecar_authorization_consumption_v0_1.json"
CONTRACT = BOUNDARY / "event_state_session_opened_replay_availability_sidecar_contract_v0_1.json"
MARKET_SIDECAR = BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
INSTANCE = RUN / "event_instance_manifest.json"
WINDOW = RUN / "event_window_binding_manifest.json"
PROJECTION = RUN / "instrument_session_projection_manifest.json"
LINEAGE = RUN / "event_state_lineage_manifest.json"
VALIDATION = RUN / "event_state_validation_report.json"
FINAL = RUN / "final_manifest.json"
PAYLOAD_BINDING = BOUNDARY / "event_state_session_opened_typed_payload_binding_v0_1.json"
EVENT_SCHEMA = TABLES / "07_EVENT_STATE_INTEGRATION" / "official_profiles" / "event_state_core_four_intraday_profile_v0_1" / "EVENT_STATE_SCHEMA_CONTRACT.json"
MARKET_SCHEMA = TABLES / "06_MARKET_STATE_INTEGRATION" / "official_profiles" / "market_state_core_four_intraday_profile_v0_1" / "PHYSICAL_SCHEMA_CONTRACT.json"

OUTPUT = BOUNDARY / "event_state_session_opened_replay_availability_sidecar_manifest_v0_1.json"
MATRIX = BOUNDARY / "event_state_session_opened_replay_availability_sidecar_matrix_v0_1.json"
READOUT = BOUNDARY / "event_state_session_opened_replay_availability_sidecar_readout_v0_1.md"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"non-canonical UTC timestamp: {value}")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def one(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    found = [row for row in rows if row.get(key) == value]
    if len(found) != 1:
        raise ValueError(f"{key}={value}: expected one row, found {len(found)}")
    return found[0]


def case(rows: list[dict[str, Any]], case_id: str, passed: bool, observed: Any) -> None:
    rows.append({"case_id": case_id, "status": "PASS" if passed else "FAIL", "observed": observed})


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    scope = load(SCOPE)
    receipt = load(RECEIPT)
    binding = receipt["selected_record_binding"]

    if receipt["authorization_state"] != "CONSUMED_FINAL":
        raise ValueError("authorization receipt is not consumed")
    if receipt["physical_files_opened"] != 1 or receipt["candidate_rows_selected"] != 1:
        raise ValueError("bounded read counters are invalid")
    if receipt["candidate_records_sha256_before"] != receipt["candidate_records_sha256_after"]:
        raise ValueError("candidate file mutated during bounded read")

    instance = one(load(INSTANCE), "event_instance_id", binding["event_instance_id"])
    window = one(load(WINDOW), "event_window_binding_id", binding["event_window_binding_id"])
    projection = one(
        load(PROJECTION),
        "event_state_instrument_session_projection_id",
        binding["instrument_projection_id"],
    )
    market_sidecar = load(MARKET_SIDECAR)
    market = one(market_sidecar["records"], "materialized_state_candidate_id", binding["market_state_record_id"] )
    lineage = load(LINEAGE)
    validation = load(VALIDATION)
    final = load(FINAL)
    payload_binding = load(PAYLOAD_BINDING)
    event_schema = load(EVENT_SCHEMA)
    market_schema = load(MARKET_SCHEMA)

    anchor = instance["event_anchor_timestamp_utc"]
    event_instance_as_of = instance["first_observable_timestamp_utc"]
    event_instance_available = instance["first_observable_timestamp_utc"]
    window_as_of = max(window["event_anchor_timestamp_utc"], window["window_end_utc"])
    window_available = max(event_instance_available, window["window_end_utc"])
    projection_as_of = max(projection["event_anchor_timestamp_utc"], window_as_of)
    projection_available = max(event_instance_available, window_available, projection["event_anchor_timestamp_utc"])
    market_as_of = market["state_as_of_utc"]
    market_available = market["state_available_at_utc"]
    event_state_as_of = max(event_instance_as_of, window_as_of, projection_as_of, market_as_of)
    base_available = max(event_instance_available, window_available, projection_available, market_available)
    publication_latency = timedelta(seconds=0)
    event_state_available = iso_utc(parse_utc(base_available) + publication_latency)

    replay_restrictions = sorted(
        {
            "candidate_runtime_only",
            "not_official_dataset",
            "no_downstream",
            "no_production",
            "research_only",
            *market["restriction_codes"],
        }
    )
    refs = {
        "authorization_consumption_sha256": sha256(RECEIPT),
        "event_instance_manifest_sha256": sha256(INSTANCE),
        "event_window_binding_manifest_sha256": sha256(WINDOW),
        "instrument_projection_manifest_sha256": sha256(PROJECTION),
        "market_state_replay_sidecar_sha256": sha256(MARKET_SIDECAR),
        "event_state_lineage_manifest_sha256": sha256(LINEAGE),
        "event_state_validation_report_sha256": sha256(VALIDATION),
        "event_state_final_manifest_sha256": sha256(FINAL),
        "typed_payload_binding_sha256": sha256(PAYLOAD_BINDING),
        "event_state_schema_sha256": sha256(EVENT_SCHEMA),
        "market_state_schema_sha256": sha256(MARKET_SCHEMA),
    }
    record = {
        "event_state_record_id": receipt["selected_event_state_record_id"],
        "event_state_record_fingerprint": receipt["selected_event_state_record_fingerprint"],
        "event_instance_id": binding["event_instance_id"],
        "event_window_binding_id": binding["event_window_binding_id"],
        "instrument_projection_id": binding["instrument_projection_id"],
        "market_state_record_id": binding["market_state_record_id"],
        "market_state_state_output_fingerprint": binding["market_state_state_output_fingerprint"],
        "market_state_dependency_dataset_fingerprint": lineage["market_state_dependency"]["market_state_candidate_dataset_fingerprint"],
        "market_state_availability_evidence_dataset_fingerprint": market_sidecar["candidate_dataset_fingerprint"],
        "market_state_cross_dataset_binding": "EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE",
        "instrument_id": binding["instrument_id"],
        "ticker": binding["ticker"],
        "exchange_id": binding["exchange_id"],
        "session_date": binding["session_date"],
        "event_anchor_timestamp_utc": anchor,
        "event_instance_as_of_utc": event_instance_as_of,
        "event_instance_available_at_utc": event_instance_available,
        "event_window_binding_as_of_utc": window_as_of,
        "event_window_binding_available_at_utc": window_available,
        "instrument_projection_as_of_utc": projection_as_of,
        "instrument_projection_available_at_utc": projection_available,
        "market_state_as_of_utc": market_as_of,
        "market_state_available_at_utc": market_available,
        "event_state_as_of_utc": event_state_as_of,
        "event_state_available_at_utc": event_state_available,
        "event_state_publication_latency": "PT0S",
        "state_replay_consumption_legality": binding["consumption_legality"],
        "event_state_provenance_restriction_codes": sorted(binding["restriction_codes"]),
        "replay_consumption_restriction_codes": replay_restrictions,
        "evidence_refs": refs,
    }
    sidecar = {
        "sidecar_id": "event_state_session_opened_replay_availability_sidecar_v0_1_AAME_2021_01_19",
        "state_kind": "event_state",
        "profile_id": "event_state_core_four_intraday_profile_v0_1",
        "event_type_id": "event_type:market_data:session_opened",
        "publication_policy": {
            "policy_id": "zero_latency_candidate_event_state_replay_publication_policy_v0_1",
            "latency": "PT0S",
            "bounded_validation_only": True,
        },
        "record_count": 1,
        "records": [record],
    }
    context = {
        "scope": scope,
        "receipt": receipt,
        "instance": instance,
        "window": window,
        "projection": projection,
        "market": market,
        "market_sidecar": market_sidecar,
        "lineage": lineage,
        "validation": validation,
        "final": final,
        "payload_binding": payload_binding,
        "event_schema": event_schema,
        "market_schema": market_schema,
    }
    return sidecar, context


def semantic_errors(sidecar: dict[str, Any], context: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if sidecar.get("record_count") != 1 or len(sidecar.get("records", [])) != 1:
        return ["record_cardinality_invalid"]
    record = sidecar["records"][0]
    binding = context["receipt"]["selected_record_binding"]
    market = context["market"]
    expected = {
        "event_state_record_id": context["receipt"]["selected_event_state_record_id"],
        "event_state_record_fingerprint": context["receipt"]["selected_event_state_record_fingerprint"],
        "event_instance_id": context["instance"]["event_instance_id"],
        "event_window_binding_id": context["window"]["event_window_binding_id"],
        "instrument_projection_id": context["projection"]["event_state_instrument_session_projection_id"],
        "market_state_record_id": market["materialized_state_candidate_id"],
        "market_state_state_output_fingerprint": market["state_output_fingerprint"],
    }
    for key, value in expected.items():
        if record.get(key) != value:
            errors.append(f"{key}_mismatch")
    as_of_keys = ("event_instance_as_of_utc", "event_window_binding_as_of_utc", "instrument_projection_as_of_utc", "market_state_as_of_utc")
    available_keys = ("event_instance_available_at_utc", "event_window_binding_available_at_utc", "instrument_projection_available_at_utc", "market_state_available_at_utc")
    if record.get("event_state_as_of_utc") != max(record[key] for key in as_of_keys):
        errors.append("event_state_as_of_formula_mismatch")
    if record.get("event_state_available_at_utc") != max(record[key] for key in available_keys):
        errors.append("event_state_available_at_formula_mismatch")
    if record.get("event_state_publication_latency") != "PT0S":
        errors.append("publication_latency_policy_mismatch")
    required_replay = {"candidate_runtime_only", "not_official_dataset", "no_downstream", "no_production", "research_only"}
    if not required_replay.issubset(set(record.get("replay_consumption_restriction_codes", []))):
        errors.append("replay_restrictions_weakened")
    if set(record.get("event_state_provenance_restriction_codes", [])) != set(binding["restriction_codes"]):
        errors.append("provenance_restrictions_changed")
    if record.get("state_replay_consumption_legality") != "research_only":
        errors.append("consumption_legality_weakened")
    if record.get("market_state_cross_dataset_binding") != "EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE":
        errors.append("cross_dataset_binding_invalid")
    return errors


def validate(sidecar: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    contract = load(CONTRACT)
    Draft202012Validator.check_schema(contract)
    errors = sorted(
        Draft202012Validator(contract, format_checker=FormatChecker()).iter_errors(sidecar),
        key=lambda error: list(error.path),
    )
    case(rows, "SCHEMA_draft_2020_12_valid", not errors, [error.message for error in errors])

    record = sidecar["records"][0]
    receipt = context["receipt"]
    binding = receipt["selected_record_binding"]
    instance = context["instance"]
    window = context["window"]
    projection = context["projection"]
    market = context["market"]

    case(rows, "AUTH_single_use_consumed", receipt["authorization_state"] == "CONSUMED_FINAL", receipt["authorization_state"])
    case(rows, "AUTH_second_use_prohibited", receipt["second_execution_authorized"] is False, receipt["second_execution_authorized"])
    case(rows, "AUTH_one_file_opened", receipt["physical_files_opened"] == 1, receipt["physical_files_opened"])
    case(rows, "AUTH_one_row_selected", receipt["candidate_rows_selected"] == 1, receipt["candidate_rows_selected"])
    case(rows, "AUTH_candidate_hash_stable", receipt["candidate_records_sha256_before"] == receipt["candidate_records_sha256_after"], receipt["candidate_records_sha256_after"])
    case(rows, "AUTH_record_fingerprint_recomputed", receipt["selected_record_fingerprint_recomputed"] is True, receipt["selected_record_fingerprint_recomputed"])

    case(rows, "BIND_event_record_id", record["event_state_record_id"] == receipt["selected_event_state_record_id"], record["event_state_record_id"])
    case(rows, "BIND_event_record_fingerprint", record["event_state_record_fingerprint"] == receipt["selected_event_state_record_fingerprint"], record["event_state_record_fingerprint"])
    case(rows, "BIND_event_instance", record["event_instance_id"] == instance["event_instance_id"], record["event_instance_id"])
    case(rows, "BIND_window", record["event_window_binding_id"] == window["event_window_binding_id"], record["event_window_binding_id"])
    case(rows, "BIND_projection", record["instrument_projection_id"] == projection["event_state_instrument_session_projection_id"], record["instrument_projection_id"])
    case(rows, "BIND_market_state_id", record["market_state_record_id"] == market["materialized_state_candidate_id"], record["market_state_record_id"])
    case(rows, "BIND_market_state_fingerprint", record["market_state_state_output_fingerprint"] == market["state_output_fingerprint"], record["market_state_state_output_fingerprint"])
    case(rows, "BIND_market_state_dependency_dataset", record["market_state_dependency_dataset_fingerprint"] == context["lineage"]["market_state_dependency"]["market_state_candidate_dataset_fingerprint"], record["market_state_dependency_dataset_fingerprint"])
    case(rows, "BIND_market_state_availability_dataset", record["market_state_availability_evidence_dataset_fingerprint"] == context["market_sidecar"]["candidate_dataset_fingerprint"], record["market_state_availability_evidence_dataset_fingerprint"])
    case(rows, "BIND_cross_dataset_row_equivalence", record["market_state_cross_dataset_binding"] == "EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE" and record["market_state_record_id"] == market["materialized_state_candidate_id"] and record["market_state_state_output_fingerprint"] == market["state_output_fingerprint"], record["market_state_cross_dataset_binding"] )
    case(rows, "BIND_context", all(record[key] == binding[key] for key in ("instrument_id", "ticker", "exchange_id", "session_date", "event_anchor_timestamp_utc")), {key: record[key] for key in ("instrument_id", "ticker", "exchange_id", "session_date")})

    as_of_inputs = [record[key] for key in ("event_instance_as_of_utc", "event_window_binding_as_of_utc", "instrument_projection_as_of_utc", "market_state_as_of_utc")]
    available_inputs = [record[key] for key in ("event_instance_available_at_utc", "event_window_binding_available_at_utc", "instrument_projection_available_at_utc", "market_state_available_at_utc")]
    case(rows, "TIME_as_of_formula", record["event_state_as_of_utc"] == max(as_of_inputs), {"inputs": as_of_inputs, "result": record["event_state_as_of_utc"]})
    case(rows, "TIME_available_at_formula", record["event_state_available_at_utc"] == max(available_inputs), {"inputs": available_inputs, "result": record["event_state_available_at_utc"], "latency": "PT0S"})
    case(rows, "TIME_anchor_not_later_than_as_of", parse_utc(record["event_anchor_timestamp_utc"]) <= parse_utc(record["event_state_as_of_utc"]), record["event_state_as_of_utc"])
    case(rows, "TIME_as_of_not_later_than_available", parse_utc(record["event_state_as_of_utc"]) <= parse_utc(record["event_state_available_at_utc"]), record["event_state_available_at_utc"])
    case(rows, "TIME_created_at_excluded", record["event_state_available_at_utc"] != receipt["consumed_at_utc"], {"available_at": record["event_state_available_at_utc"], "receipt_time": receipt["consumed_at_utc"]})
    case(rows, "TIME_delivery_rule", load(BOUNDARY / "event_state_session_opened_replay_availability_contract_v0_1.json")["required_formula"]["delivery_eligibility"] == "event_loop.clock >= event_state_available_at_utc", "event_loop.clock >= event_state_available_at_utc")

    provenance = set(record["event_state_provenance_restriction_codes"])
    replay = set(record["replay_consumption_restriction_codes"])
    case(rows, "RESTRICT_provenance_preserved", provenance == set(binding["restriction_codes"]), sorted(provenance))
    case(rows, "RESTRICT_replay_required", {"candidate_runtime_only", "not_official_dataset", "no_downstream", "no_production", "research_only"}.issubset(replay), sorted(replay))
    case(rows, "RESTRICT_domains_separate", record["event_state_provenance_restriction_codes"] != record["replay_consumption_restriction_codes"], {"provenance": len(provenance), "replay": len(replay)})
    case(rows, "BOUNDARY_research_only", record["state_replay_consumption_legality"] == "research_only", record["state_replay_consumption_legality"])
    case(rows, "BOUNDARY_no_bt_implementation", context["scope"]["prohibited"]["authorize_bt_gate_015_implementation"] is True, context["scope"]["prohibited"])
    case(rows, "BOUNDARY_no_physical_consumption", context["scope"]["prohibited"]["authorize_event_state_physical_consumption"] is True, context["scope"]["prohibited"])
    case(rows, "BOUNDARY_no_market_parquet", receipt["market_state_parquet_opened"] is False, receipt["market_state_parquet_opened"])
    case(rows, "BOUNDARY_no_backtester_change", receipt["backtester_modified"] is False, receipt["backtester_modified"])
    case(rows, "SOURCE_event_run_pass", context["final"]["final_run_status"].startswith("CLOSED_PASS_"), context["final"]["final_run_status"])
    case(rows, "SOURCE_validation_pass", context["validation"]["validation_status"] == "pass_with_restrictions", context["validation"]["validation_status"])

    payload_binding = context["payload_binding"]
    payload_schema = payload_binding["scientific_payload_schema"]
    payload_fields = payload_schema["required"]
    market_columns = {column["name"]: column for column in context["market_schema"]["columns"]}
    receipt_fields = binding["source_market_state_value_snapshot_fields"]
    Draft202012Validator.check_schema(payload_schema)
    case(rows, "PAYLOAD_event_schema_hash", sha256(EVENT_SCHEMA) == payload_binding["source_event_state_schema"]["sha256"], sha256(EVENT_SCHEMA))
    case(rows, "PAYLOAD_market_schema_hash", sha256(MARKET_SCHEMA) == payload_binding["source_market_state_schema"]["sha256"], sha256(MARKET_SCHEMA))
    case(rows, "PAYLOAD_event_envelope_38", context["event_schema"]["field_count"] == 38 == payload_binding["source_event_state_schema"]["field_count"], context["event_schema"]["field_count"])
    case(rows, "PAYLOAD_market_schema_40", context["market_schema"]["column_count"] == 40, context["market_schema"]["column_count"])
    case(rows, "PAYLOAD_exact_17_fields", len(payload_fields) == 17 == binding["source_market_state_value_snapshot_field_count"], len(payload_fields))
    case(rows, "PAYLOAD_observed_snapshot_present", binding["source_market_state_value_snapshot_present"] is True, binding["source_market_state_value_snapshot_present"])
    case(rows, "PAYLOAD_observed_fields_exact", set(payload_fields) == set(receipt_fields), sorted(receipt_fields))
    case(rows, "PAYLOAD_all_fields_governed_double", all(name in market_columns and market_columns[name]["type"] == "double" and market_columns[name]["nullable"] is False for name in payload_fields), payload_fields)
    group_sizes = {name: len(fields) for name, fields in payload_binding["scientific_payload_groups"].items()}
    case(rows, "PAYLOAD_core_four_group_sizes", group_sizes == {"price_location_structure": 5, "price_movement": 5, "trading_activity": 4, "volatility_range_state": 3}, group_sizes)
    case(rows, "PAYLOAD_no_unapproved_event_features", payload_binding["event_specific_scientific_features"] == [], payload_binding["event_specific_scientific_features"])
    case(rows, "PAYLOAD_created_at_excluded", "created_at_utc" not in payload_fields, payload_binding["excluded_from_scientific_payload"])
    synthetic = {name: 0.0 for name in payload_fields}
    payload_validator = Draft202012Validator(payload_schema)
    case(rows, "PAYLOAD_positive_schema_fixture", not list(payload_validator.iter_errors(synthetic)), len(synthetic))
    missing = dict(synthetic)
    missing.pop(payload_fields[0])
    case(rows, "PAYLOAD_missing_field_rejected", bool(list(payload_validator.iter_errors(missing))), payload_fields[0])
    extra = dict(synthetic)
    extra["unapproved_event_indicator"] = 1.0
    case(rows, "PAYLOAD_extra_field_rejected", bool(list(payload_validator.iter_errors(extra))), "unapproved_event_indicator")

    case(rows, "SEMANTIC_positive_sidecar", semantic_errors(sidecar, context) == [], semantic_errors(sidecar, context))
    mutation = deepcopy(sidecar)
    mutation["records"][0]["market_state_record_id"] = "0" * 64
    errors = semantic_errors(mutation, context)
    case(rows, "NEG_market_state_id_mutation_rejected", "market_state_record_id_mismatch" in errors, errors)
    mutation = deepcopy(sidecar)
    mutation["records"][0]["event_state_available_at_utc"] = "2021-01-19T14:29:59Z"
    errors = semantic_errors(mutation, context)
    case(rows, "NEG_early_available_at_rejected", "event_state_available_at_formula_mismatch" in errors, errors)
    mutation = deepcopy(sidecar)
    mutation["records"][0]["replay_consumption_restriction_codes"].remove("research_only")
    errors = semantic_errors(mutation, context)
    case(rows, "NEG_research_only_removal_rejected", "replay_restrictions_weakened" in errors, errors)
    return rows


def main() -> int:
    sidecar, context = build()
    rows = validate(sidecar, context)
    failed = [row for row in rows if row["status"] != "PASS"]
    OUTPUT.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8", newline="\n")
    matrix = {
        "gate": "event_state_session_opened_replay_availability_evidence_sidecar_v0_1",
        "status": "PASS" if not failed else "FAIL",
        "case_count": len(rows),
        "failed_cases": len(failed),
        "physical_files_opened": 1,
        "candidate_rows_scanned": 8,
        "candidate_rows_selected": 1,
        "market_state_parquet_opened": False,
        "backtester_files_modified": 0,
        "bt_gate_015_implementation_authorized": False,
        "cases": rows,
    }
    MATRIX.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    status = "CLOSED_PASS_ROW_ADDRESSABLE_EVENT_STATE_REPLAY_AVAILABILITY_EVIDENCE_WITH_RESTRICTIONS_NO_CONSUMER_AUTHORIZATION" if not failed else "FAILED_VALIDATION"
    READOUT.write_text(
        "\n".join(
            [
                "# Event State `session_opened` Replay Availability Sidecar Readout v0.1",
                "",
                "```text",
                "event_state_session_opened_replay_availability_evidence_sidecar_v0_1 =",
                status,
                f"case_count = {len(rows)}",
                f"failed_cases = {len(failed)}",
                "physical Event State candidate files opened = 1",
                "candidate rows scanned = 8",
                "candidate rows selected = 1",
                "Market State Parquet opened = false",
                "backtester files modified = 0",
                "BT-GATE-015 implementation = NOT_AUTHORIZED",
                "Event State physical consumer read = NOT_AUTHORIZED",
                "```",
                "",
                "The row-addressable sidecar proves `event_state_available_at_utc`",
                "for the exact on-demand AAME record. It does not itself authorize",
                "consumer implementation or physical replay.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": status, "case_count": len(rows), "failed_cases": len(failed), "sidecar": str(OUTPUT)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
