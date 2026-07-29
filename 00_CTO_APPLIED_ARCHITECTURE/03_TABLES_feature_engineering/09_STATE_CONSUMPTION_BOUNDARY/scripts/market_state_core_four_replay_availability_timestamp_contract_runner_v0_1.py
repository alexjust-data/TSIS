from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
GATE = "market_state_core_four_replay_availability_timestamp_contract_v0_1"
STATUS = "CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ"
CONTRACT = ROOT / "market_state_core_four_replay_availability_timestamp_contract_v0_1.json"
SCOPE = ROOT / "configs" / "market_state_core_four_replay_availability_timestamp_contract_scope_v0_1.json"
MATRIX = ROOT / "market_state_core_four_replay_availability_timestamp_contract_matrix_v0_1.json"
READOUT = ROOT / "market_state_core_four_replay_availability_timestamp_contract_readout_v0_1.md"

REQUIRED_OBJECTS = [
    "trading_activity",
    "price_movement",
    "price_location_structure",
    "volatility_range_state",
]
ZERO_LATENCY_POLICY = "zero_latency_candidate_replay_publication_policy_v0_1"
UTC_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
DURATION_RE = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$"
)

REQ = [
    "TS_CONTRACT_JSON_PARSE_001",
    "TS_JSON_SCHEMA_COMPILE_001",
    "TS_SCHEMA_VALIDATES_GOOD_RECORD_001",
    "TS_SCHEMA_REJECTS_NON_CANONICAL_UTC_OFFSET_001",
    "TS_SCHEMA_REJECTS_BAD_DURATION_ORDER_001",
    "TS_SCOPE_BOUNDARIES_001",
    "TS_TIMESTAMP_DEFINITIONS_001",
    "TS_STATE_AS_OF_MAX_COMPONENT_001",
    "TS_STATE_AVAILABLE_AT_INCLUDES_PUBLICATION_LATENCY_001",
    "TS_DECISION_TIMESTAMP_ONLY_NOT_DELIVERY_001",
    "TS_MATERIALIZATION_TIME_NOT_AVAILABILITY_001",
    "TS_MISSING_AS_OF_BLOCKS_001",
    "TS_MISSING_AVAILABLE_AT_BLOCKS_001",
    "TS_COMPONENT_AS_OF_AFTER_DECISION_BLOCKS_001",
    "TS_AVAILABLE_AT_BEFORE_DECISION_BLOCKS_001",
    "TS_SOURCE_AFTER_DECISION_BLOCKS_001",
    "TS_COMPONENT_AVAILABLE_BEFORE_AS_OF_BLOCKS_001",
    "TS_CORE_FOUR_INFORMATION_OBJECT_COVERAGE_001",
    "TS_DUPLICATED_OBJECTS_MISSING_REQUIRED_BLOCKS_001",
    "TS_COMPONENT_BLOCKED_DECISION_SAFE_BLOCKS_001",
    "TS_COMPONENT_RESEARCH_ONLY_DECISION_SAFE_BLOCKS_001",
    "TS_GLOBAL_BLOCKED_DECISION_SAFE_BLOCKS_001",
    "TS_LATENCY_OMISSION_BLOCKS_001",
    "TS_ZERO_LATENCY_POLICY_REQUIRED_001",
    "TS_RESTRICTION_PROPAGATION_REQUIRED_001",
    "TS_RESEARCH_ONLY_CONSISTENT_NOT_DELIVERABLE_001",
    "TS_EVENT_LOOP_DELIVERY_RULE_001",
    "TS_CORE_FOUR_PROFILE_NOT_EXPANDED_001",
    "TS_REPLAY_LEGALITY_DECISION_SAFE_ONLY_001",
    "TS_NON_EXECUTION_BOUNDARIES_001",
]


def ts(value: str) -> datetime:
    if not isinstance(value, str) or not UTC_Z_RE.match(value):
        raise ValueError("timestamp_not_canonical_utc_z")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def parse_duration(value: str) -> timedelta:
    if not isinstance(value, str):
        raise ValueError("duration_not_string")
    match = DURATION_RE.match(value)
    if not match or value in {"P", "PT"}:
        raise ValueError("invalid_duration")
    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = float(match.group("seconds") or 0)
    if days == hours == minutes == 0 and seconds == 0 and value != "PT0S":
        raise ValueError("zero_duration_requires_PT0S")
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def comp(obj: str, as_of: str, avail: str, *, source: str | None = None, status: str = "available", restrictions: list[str] | None = None) -> dict[str, Any]:
    return {
        "component_id": f"core_four_intraday_{obj}_component_v0_1",
        "information_object_id": obj,
        "source_timestamp_utc": source or as_of,
        "component_as_of_utc": as_of,
        "component_available_at_utc": avail,
        "cutoff_rule_id": "component_as_of_lte_decision_timestamp_utc_v0_1",
        "availability_rule_id": "component_available_at_lte_state_available_at_utc_v0_1",
        "availability_status": status,
        "restriction_codes": restrictions if restrictions is not None else ["candidate_runtime_only"],
    }


def good_record(*, latency: str = "PT0S", available_at: str = "2026-01-05T14:42:00Z", policy: str = ZERO_LATENCY_POLICY) -> dict[str, Any]:
    return {
        "state_kind": "market_state",
        "profile_id": "market_state_core_four_intraday_profile_v0_1",
        "decision_timestamp_utc": "2026-01-05T14:42:00Z",
        "state_as_of_utc": "2026-01-05T14:42:00Z",
        "state_available_at_utc": available_at,
        "state_availability_policy_id": "market_state_core_four_replay_availability_policy_v0_1",
        "state_publication_latency_policy_id": policy,
        "state_publication_latency": latency,
        "state_replay_consumption_legality": "decision_safe",
        "state_availability_status": "available_for_decision_replay",
        "component_availability_evidence": [
            comp(o, "2026-01-05T14:42:00Z", "2026-01-05T14:42:00Z") for o in REQUIRED_OBJECTS
        ],
        "restriction_codes": ["candidate_runtime_only"],
    }


def schema_errors(validator: jsonschema.Draft202012Validator, record: dict[str, Any]) -> list[str]:
    return [error.message for error in validator.iter_errors(record)]


def semantic_ok(record: dict[str, Any]) -> tuple[bool, str]:
    required = [
        "decision_timestamp_utc",
        "state_as_of_utc",
        "state_available_at_utc",
        "state_publication_latency_policy_id",
        "state_publication_latency",
        "state_replay_consumption_legality",
        "state_availability_status",
        "component_availability_evidence",
        "restriction_codes",
    ]
    for field in required:
        if field not in record or record[field] in (None, ""):
            return False, "missing_" + field
    try:
        decision = ts(record["decision_timestamp_utc"])
        as_of = ts(record["state_as_of_utc"])
        available = ts(record["state_available_at_utc"])
        latency = parse_duration(record["state_publication_latency"])
    except ValueError as exc:
        return False, str(exc)

    if record["state_publication_latency"] == "PT0S" and record["state_publication_latency_policy_id"] != ZERO_LATENCY_POLICY:
        return False, "zero_latency_policy_mismatch"
    if record["state_publication_latency"] != "PT0S" and record["state_publication_latency_policy_id"] == ZERO_LATENCY_POLICY:
        return False, "zero_latency_policy_with_nonzero_latency"

    status = record["state_availability_status"]
    legality = record["state_replay_consumption_legality"]
    if status == "available_for_decision_replay" and legality != "decision_safe":
        return False, "available_status_not_decision_safe"
    if status == "research_only" and legality != "research_only":
        return False, "research_status_not_research_only"
    if status == "blocked" and not legality.startswith("blocked_"):
        return False, "blocked_status_not_blocked_legality"
    if legality == "decision_safe" and status != "available_for_decision_replay":
        return False, "decision_safe_without_available_status"

    evidence = record["component_availability_evidence"]
    object_ids = [item.get("information_object_id") for item in evidence]
    if set(object_ids) != set(REQUIRED_OBJECTS):
        return False, "required_information_object_coverage_mismatch"

    comp_asofs: list[datetime] = []
    comp_avails: list[datetime] = []
    component_restrictions: set[str] = set()
    for item in evidence:
        for field in ["source_timestamp_utc", "component_as_of_utc", "component_available_at_utc"]:
            if not item.get(field):
                return False, "missing_" + field
        try:
            source_ts = ts(item["source_timestamp_utc"])
            item_as_of = ts(item["component_as_of_utc"])
            item_avail = ts(item["component_available_at_utc"])
        except ValueError as exc:
            return False, str(exc)
        if source_ts > item_as_of:
            return False, "source_timestamp_after_component_as_of"
        if source_ts > decision:
            return False, "source_timestamp_after_decision"
        if item_as_of > decision:
            return False, "component_as_of_after_decision"
        if item_avail < item_as_of:
            return False, "component_available_before_component_as_of"
        if item_avail > available:
            return False, "component_available_after_state_available"
        if legality == "decision_safe" and item["availability_status"] != "available":
            return False, "component_not_available_but_row_decision_safe"
        component_restrictions.update(item.get("restriction_codes", []))
        comp_asofs.append(item_as_of)
        comp_avails.append(item_avail)

    if as_of != max(comp_asofs):
        return False, "state_as_of_not_max_component"
    expected_available = max([decision] + comp_avails) + latency
    if available != expected_available:
        return False, "state_available_at_not_max_decision_components_plus_latency"
    if as_of > available:
        return False, "state_as_of_after_state_available"
    if decision > available:
        return False, "decision_after_state_available"
    row_restrictions = set(record.get("restriction_codes", []))
    if not component_restrictions.issubset(row_restrictions):
        return False, "restriction_propagation_missing"
    return True, "PASS"


def full_ok(validator: jsonschema.Draft202012Validator, record: dict[str, Any]) -> tuple[bool, str]:
    errors = schema_errors(validator, record)
    if errors:
        return False, "schema:" + errors[0]
    return semantic_ok(record)


def mutate(record: dict[str, Any], fn) -> dict[str, Any]:
    out = copy.deepcopy(record)
    fn(out)
    return out


def add(rows: list[dict[str, Any]], cid: str, area: str, expected: str, observed: str, result: str) -> None:
    rows.append({"case_id": cid, "area": area, "expected": expected, "observed": observed, "result": result})


def expect_valid(rows: list[dict[str, Any]], validator: jsonschema.Draft202012Validator, cid: str, area: str, record: dict[str, Any], expected: str = "valid") -> None:
    ok, msg = full_ok(validator, record)
    add(rows, cid, area, expected, msg, "PASS" if ok else "FAIL")


def expect_invalid(rows: list[dict[str, Any]], validator: jsonschema.Draft202012Validator, cid: str, area: str, record: dict[str, Any], expected_reason: str) -> None:
    ok, msg = full_ok(validator, record)
    add(rows, cid, area, "blocked: " + expected_reason, msg, "PASS" if not ok else "FAIL")


def main() -> None:
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    add(rows, "TS_CONTRACT_JSON_PARSE_001", "json", "contract and scope parse", "parsed", "PASS")
    try:
        jsonschema.Draft202012Validator.check_schema(contract["json_schema"])
        validator = jsonschema.Draft202012Validator(contract["json_schema"], format_checker=jsonschema.FormatChecker())
        add(rows, "TS_JSON_SCHEMA_COMPILE_001", "schema", "Draft 2020-12 schema compiles", "compiled", "PASS")
    except Exception as exc:
        add(rows, "TS_JSON_SCHEMA_COMPILE_001", "schema", "Draft 2020-12 schema compiles", repr(exc), "FAIL")
        validator = jsonschema.Draft202012Validator({})

    rec = good_record()
    expect_valid(rows, validator, "TS_SCHEMA_VALIDATES_GOOD_RECORD_001", "schema", rec)
    expect_invalid(rows, validator, "TS_SCHEMA_REJECTS_NON_CANONICAL_UTC_OFFSET_001", "schema", mutate(rec, lambda r: r.__setitem__("decision_timestamp_utc", "2026-01-05T15:42:00+01:00")), "canonical UTC Z required")
    expect_invalid(rows, validator, "TS_SCHEMA_REJECTS_BAD_DURATION_ORDER_001", "schema", mutate(rec, lambda r: r.__setitem__("state_publication_latency", "PT1M2H")), "ordered ISO-8601 duration required")

    hb = scope["hard_boundaries"]
    boundaries_ok = (
        hb["physical_artifacts_opened"] == 0
        and hb["state_rows_read"] == 0
        and hb["runtime_requests_executed"] == 0
        and hb["production"] is False
        and hb["downstream"] is False
    )
    add(rows, "TS_SCOPE_BOUNDARIES_001", "boundaries", "no execution authority", str(boundaries_ok), "PASS" if boundaries_ok else "FAIL")
    defs = contract["timestamp_definitions"]
    defs_ok = all(k in defs for k in ["decision_timestamp_utc", "state_as_of_utc", "state_available_at_utc"])
    add(rows, "TS_TIMESTAMP_DEFINITIONS_001", "timestamps", "three timestamp definitions", str(defs_ok), "PASS" if defs_ok else "FAIL")

    ok, msg = full_ok(validator, rec)
    add(rows, "TS_STATE_AS_OF_MAX_COMPONENT_001", "semantic", "state_as_of is max component as_of", msg, "PASS" if ok else "FAIL")
    rec_latency = good_record(latency="PT1S", available_at="2026-01-05T14:42:01Z", policy="one_second_candidate_replay_publication_policy_v0_1")
    ok, msg = full_ok(validator, rec_latency)
    add(rows, "TS_STATE_AVAILABLE_AT_INCLUDES_PUBLICATION_LATENCY_001", "semantic", "available_at includes governed latency", msg, "PASS" if ok else "FAIL")
    add(rows, "TS_DECISION_TIMESTAMP_ONLY_NOT_DELIVERY_001", "delivery", "decision timestamp alone not enough", str(contract["decision_timestamp_only_delivery_allowed"] is False), "PASS" if contract["decision_timestamp_only_delivery_allowed"] is False else "FAIL")
    forbidden = set(contract["forbidden_availability_sources"])
    materialization_ok = {"parquet_created_at", "runtime_invocation_created_at", "bundle_created_at", "file_modified_at"}.issubset(forbidden)
    add(rows, "TS_MATERIALIZATION_TIME_NOT_AVAILABILITY_001", "delivery", "materialization/file/runtime times forbidden", str(materialization_ok), "PASS" if materialization_ok else "FAIL")

    expect_invalid(rows, validator, "TS_MISSING_AS_OF_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r.pop("state_as_of_utc")), "missing state_as_of")
    expect_invalid(rows, validator, "TS_MISSING_AVAILABLE_AT_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r.pop("state_available_at_utc")), "missing state_available_at")
    expect_invalid(rows, validator, "TS_COMPONENT_AS_OF_AFTER_DECISION_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r["component_availability_evidence"][0].__setitem__("component_as_of_utc", "2026-01-05T14:43:00Z")), "component as_of after decision")
    expect_invalid(rows, validator, "TS_AVAILABLE_AT_BEFORE_DECISION_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r.__setitem__("state_available_at_utc", "2026-01-05T14:41:00Z")), "available_at before decision")
    expect_invalid(rows, validator, "TS_SOURCE_AFTER_DECISION_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r["component_availability_evidence"][0].__setitem__("source_timestamp_utc", "2026-01-05T14:43:00Z")), "source after decision")
    expect_invalid(rows, validator, "TS_COMPONENT_AVAILABLE_BEFORE_AS_OF_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r["component_availability_evidence"][0].__setitem__("component_available_at_utc", "2026-01-05T14:41:59Z")), "component available before as_of")

    coverage_ok = set(item["information_object_id"] for item in rec["component_availability_evidence"]) == set(REQUIRED_OBJECTS)
    add(rows, "TS_CORE_FOUR_INFORMATION_OBJECT_COVERAGE_001", "semantic", "all four required objects represented", str(coverage_ok), "PASS" if coverage_ok else "FAIL")
    duplicated = good_record()
    duplicated["component_availability_evidence"] = [comp("trading_activity", "2026-01-05T14:42:00Z", "2026-01-05T14:42:00Z", restrictions=["candidate_runtime_only", f"dup_{i}"]) for i in range(4)]
    expect_invalid(rows, validator, "TS_DUPLICATED_OBJECTS_MISSING_REQUIRED_BLOCKS_001", "fail_closed", duplicated, "required object missing despite minItems")
    expect_invalid(rows, validator, "TS_COMPONENT_BLOCKED_DECISION_SAFE_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r["component_availability_evidence"][0].__setitem__("availability_status", "blocked")), "blocked component cannot be decision_safe")
    expect_invalid(rows, validator, "TS_COMPONENT_RESEARCH_ONLY_DECISION_SAFE_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r["component_availability_evidence"][0].__setitem__("availability_status", "research_only")), "research_only component cannot be decision_safe")
    expect_invalid(rows, validator, "TS_GLOBAL_BLOCKED_DECISION_SAFE_BLOCKS_001", "fail_closed", mutate(rec, lambda r: r.__setitem__("state_availability_status", "blocked")), "blocked state cannot be decision_safe")
    expect_invalid(rows, validator, "TS_LATENCY_OMISSION_BLOCKS_001", "fail_closed", good_record(latency="PT1S", available_at="2026-01-05T14:42:00Z", policy="one_second_candidate_replay_publication_policy_v0_1"), "latency must be added")
    expect_invalid(rows, validator, "TS_ZERO_LATENCY_POLICY_REQUIRED_001", "fail_closed", good_record(policy="non_zero_or_unspecified_policy_v0_1"), "PT0S requires zero latency policy")
    expect_invalid(rows, validator, "TS_RESTRICTION_PROPAGATION_REQUIRED_001", "fail_closed", mutate(rec, lambda r: r.__setitem__("restriction_codes", [])), "component restrictions must propagate")

    research = good_record()
    research["state_availability_status"] = "research_only"
    research["state_replay_consumption_legality"] = "research_only"
    ok, msg = full_ok(validator, research)
    deliverable = research["state_replay_consumption_legality"] == "decision_safe"
    add(rows, "TS_RESEARCH_ONLY_CONSISTENT_NOT_DELIVERABLE_001", "legality", "research_only evidence can be internally consistent but not replay-deliverable", f"valid={ok}; deliverable={deliverable}; {msg}", "PASS" if ok and not deliverable else "FAIL")

    add(rows, "TS_EVENT_LOOP_DELIVERY_RULE_001", "replay", "EventLoop delivery uses available_at", contract["delivery_rule"], "PASS" if contract["delivery_rule"] == "event_loop.clock >= state_available_at_utc" else "FAIL")
    profile_ok = contract["required_information_objects"] == REQUIRED_OBJECTS and "liquidity" in contract["not_added_information_objects"]
    add(rows, "TS_CORE_FOUR_PROFILE_NOT_EXPANDED_001", "profile", "profile not expanded", str(profile_ok), "PASS" if profile_ok else "FAIL")
    add(rows, "TS_REPLAY_LEGALITY_DECISION_SAFE_ONLY_001", "legality", "only decision_safe reaches replay", str(contract["strategy_facing_replay_allowed_legality"]), "PASS" if contract["strategy_facing_replay_allowed_legality"] == ["decision_safe"] else "FAIL")
    authority_ok = not any(contract["execution_authority"].values())
    add(rows, "TS_NON_EXECUTION_BOUNDARIES_001", "authority", "no physical/runtime/backtest authority", str(authority_ok), "PASS" if authority_ok else "FAIL")

    ids = [row["case_id"] for row in rows]
    result = {
        "gate": GATE,
        "status": STATUS if all(row["result"] == "PASS" for row in rows) else "FAILED",
        "created_at_utc": "2026-07-29T17:35:00Z",
        "case_count": len(rows),
        "failed_cases": sum(1 for row in rows if row["result"] != "PASS"),
        "required_case_ids": REQ,
        "missing_required_case_ids": sorted(set(REQ) - set(ids)),
        "duplicate_case_ids": sorted({case_id for case_id in ids if ids.count(case_id) > 1}),
        "unexpected_case_ids": sorted(set(ids) - set(REQ)),
        "physical_artifacts_opened": 0,
        "parquet_opened": False,
        "state_rows_read": 0,
        "StateReplayFeed_records_emitted": 0,
        "runtime_requests_executed": 0,
        "runtime_builds_executed": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "production": False,
        "downstream": False,
        "official_dataset": False,
        "rows": rows,
    }
    MATRIX.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    READOUT.write_bytes(f"""# Market State Core Four Replay Availability Timestamp Contract v0.1 Readout

Gate: `{GATE}`
Date: `2026-07-29`
Status: `{result['status']}`

## Result

The replay timestamp contract for `market_state_core_four_intraday_profile_v0_1` is closed as validation-hardened, contract-ready with restrictions and no physical read.

```text
case_count = {result['case_count']}
failed_cases = {result['failed_cases']}
missing_required_case_ids = {len(result['missing_required_case_ids'])}
duplicate_case_ids = {len(result['duplicate_case_ids'])}
unexpected_case_ids = {len(result['unexpected_case_ids'])}
```

## Validation Hardening

The runner now validates every fixture through both layers:

```text
JSON Schema validation
+
semantic validation
```

It also closes the external semantic-enforcement findings:

```text
required core-four Information Object coverage
component status -> row legality coherence
state_availability_status -> replay legality coherence
publication latency included in state_available_at_utc
PT0S bound to zero-latency policy
timestamp ordering across source/component/state
restriction propagation from components to row
canonical UTC Z timestamp representation
ordered ISO-8601 duration parsing
```

## Closed Timestamp Semantics

```text
decision_timestamp_utc = market instant represented by the row
state_as_of_utc = max source-information timestamp incorporated into the complete emitted row
state_available_at_utc = first historical instant the complete row could legally be delivered
```

Replay eligibility remains:

```text
event_loop.clock >= state_available_at_utc
```

## Boundaries Preserved

```text
physical_artifacts_opened = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```

## Next Required Gate

```text
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

After that gate reissues a v0.1.2 response/bundle with the required timestamp evidence, repeat `state_bundle_manifest_physical_evidence_alignment_v0_1` before reopening any bounded read-and-replay authorization.
""".encode("utf-8"))
    print(json.dumps({"status": result["status"], "case_count": result["case_count"], "failed_cases": result["failed_cases"]}, indent=2))


if __name__ == "__main__":
    main()
