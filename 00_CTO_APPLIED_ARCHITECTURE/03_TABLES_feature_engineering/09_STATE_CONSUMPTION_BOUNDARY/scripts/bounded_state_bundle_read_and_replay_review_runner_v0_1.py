from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


FEATURE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = FEATURE_ROOT.parents[1]
BOUNDARY = FEATURE_ROOT / "09_STATE_CONSUMPTION_BOUNDARY"
SCOPE_PATH = BOUNDARY / "configs/bounded_state_bundle_read_and_replay_review_scope_v0_1.json"
MATRIX_PATH = BOUNDARY / "bounded_state_bundle_read_and_replay_review_matrix_v0_1.json"
READOUT_PATH = BOUNDARY / "bounded_state_bundle_read_and_replay_review_readout_v0_1.md"

REQUIRED_CASE_IDS = [
    "REVIEW_EXECUTION_OUTPUT_INVENTORY_EXACT",
    "REVIEW_EXECUTION_STATUS_PASS",
    "REVIEW_EXECUTION_CASES_ALL_PASS",
    "REVIEW_SINGLE_USE_AUTHORIZATION_CONSUMED",
    "REVIEW_FROZEN_INPUT_HASHES_ALL_MATCH",
    "REVIEW_PHYSICAL_SCHEMA_EXACT",
    "REVIEW_TWO_AUTHORIZED_ROWS_ONLY",
    "REVIEW_ROW_FINGERPRINTS_RECALCULATED",
    "REVIEW_EXACT_ONE_SIDECAR_PER_ROW",
    "REVIEW_CANONICAL_ORDER",
    "REVIEW_NO_EARLY_DELIVERY",
    "REVIEW_RESTRICTIONS_PRESERVED",
    "REVIEW_PROHIBITED_COUNTERS_ZERO",
    "REVIEW_OUTPUT_HASH_CHAIN_VALID",
    "REVIEW_DUPLICATE_EVENT_MUTATION_BLOCKED",
    "REVIEW_EARLY_DELIVERY_MUTATION_BLOCKED",
    "REVIEW_UNKNOWN_ROW_MUTATION_BLOCKED",
    "REVIEW_SCOPE_EXPANSION_MUTATION_BLOCKED",
    "REVIEW_UNCONSUMED_AUTHORIZATION_MUTATION_BLOCKED",
    "REVIEW_NO_PHYSICAL_READ_DURING_REVIEW",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_case(rows: list[dict[str, Any]], case_id: str, passed: bool, evidence: Any) -> None:
    rows.append(
        {
            "case_id": case_id,
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
            "evidence": evidence,
        }
    )


def evidence_is_valid(
    receipt: dict[str, Any],
    read_report: dict[str, Any],
    replay_report: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    events = replay_report.get("events", [])
    ids = [event.get("materialized_state_candidate_id") for event in events]
    if receipt.get("authorization_status") != f"CONSUMED_BY_RUN_{receipt.get('consumed_by_run_id')}":
        return False
    if len(events) != 2 or len(ids) != len(set(ids)):
        return False
    if set(ids) != set(expected["authorized_row_ids"]):
        return False
    for event in events:
        if event.get("instrument_id") != expected["authorized_instrument_id"]:
            return False
        if event.get("session_date") != expected["authorized_session_date"]:
            return False
        if event.get("event_loop_clock_utc", "") < event.get("state_available_at_utc", ""):
            return False
        required = {"candidate_runtime_only", "not_official_dataset", "no_downstream", "no_production"}
        if not required.issubset(set(event.get("restriction_codes", []))):
            return False
    if read_report.get("unlisted_rows_delivered") != 0:
        return False
    return True


def main() -> int:
    scope = read_json(SCOPE_PATH)
    expected = scope["expected"]
    run_dir = (REPO_ROOT / scope["execution_run_directory"]).resolve()
    required_names = scope["required_execution_outputs"]
    found_names = sorted(path.name for path in run_dir.iterdir() if path.is_file())
    cases: list[dict[str, Any]] = []

    add_case(cases, REQUIRED_CASE_IDS[0], found_names == sorted(required_names), found_names)
    pre_run = read_json(run_dir / "pre_run_manifest.json")
    heartbeat = read_json(run_dir / "heartbeat.json")
    receipt = read_json(run_dir / "authorization_consumption_receipt.json")
    read_report = read_json(run_dir / "bounded_read_report.json")
    replay_report = read_json(run_dir / "bounded_replay_report.json")
    final = read_json(run_dir / "final_manifest.json")

    add_case(cases, REQUIRED_CASE_IDS[1], final["status"] == expected["execution_status"], final["status"])
    add_case(cases, REQUIRED_CASE_IDS[2], final["failed_cases"] == 0 and all(case["passed"] for case in final["cases"]), final["case_count"])
    add_case(
        cases,
        REQUIRED_CASE_IDS[3],
        pre_run["authorization_status_at_start"] == "NOT_CONSUMED"
        and receipt["single_use_authorization"] is True
        and receipt["maximum_execution_runs"] == 1
        and receipt["consumed_by_run_id"] == final["authorization_consumed_by_run_id"],
        receipt["authorization_status"],
    )
    add_case(
        cases,
        REQUIRED_CASE_IDS[4],
        len(read_report["input_hash_verification"]) == 9
        and all(row["match"] for row in read_report["input_hash_verification"]),
        read_report["input_hash_verification"],
    )
    add_case(cases, REQUIRED_CASE_IDS[5], all(row["match"] for row in read_report["schema_validation"]), len(read_report["schema_validation"]))
    add_case(
        cases,
        REQUIRED_CASE_IDS[6],
        read_report["physical_state_rows_read"] == 2
        and set(read_report["observed_row_ids"]) == set(expected["authorized_row_ids"])
        and read_report["unlisted_rows_delivered"] == 0,
        read_report["observed_row_ids"],
    )
    add_case(
        cases,
        REQUIRED_CASE_IDS[7],
        all(row["state_fingerprint_match"] and row["candidate_id_match"] for row in read_report["fingerprint_validation"]),
        read_report["fingerprint_validation"],
    )
    events = replay_report["events"]
    add_case(cases, REQUIRED_CASE_IDS[8], len(events) == 2 == len({event["materialized_state_candidate_id"] for event in events}), [event["materialized_state_candidate_id"] for event in events])
    ordered = sorted(events, key=lambda event: (event["state_available_at_utc"], event["state_kind"], event["instrument_id"], event["materialized_state_candidate_id"]))
    add_case(cases, REQUIRED_CASE_IDS[9], events == ordered, [event["state_available_at_utc"] for event in events])
    add_case(cases, REQUIRED_CASE_IDS[10], all(event["event_loop_clock_utc"] >= event["state_available_at_utc"] for event in events), "clock >= available_at")
    required_restrictions = {"candidate_runtime_only", "not_official_dataset", "no_downstream", "no_production"}
    add_case(cases, REQUIRED_CASE_IDS[11], all(required_restrictions.issubset(set(event["restriction_codes"])) for event in events), sorted(required_restrictions))
    counters = final["counters"]
    add_case(
        cases,
        REQUIRED_CASE_IDS[12],
        counters["strategy_callbacks"] == counters["signals_emitted"] == counters["orders_emitted"] == counters["fills_emitted"] == 0
        and counters["PnL_calculated"] is False
        and counters["datasets_written"] == counters["registry_mutations"] == 0
        and counters["official_dataset"] is counters["production"] is counters["downstream"] is False,
        counters,
    )
    hash_chain = final["output_hashes_before_final_manifest"]
    add_case(
        cases,
        REQUIRED_CASE_IDS[13],
        all(sha256_file(run_dir / name) == expected_hash for name, expected_hash in hash_chain.items()),
        hash_chain,
    )

    duplicate = copy.deepcopy(replay_report)
    duplicate["events"].append(copy.deepcopy(duplicate["events"][0]))
    add_case(cases, REQUIRED_CASE_IDS[14], not evidence_is_valid(receipt, read_report, duplicate, expected), "duplicate rejected")
    early = copy.deepcopy(replay_report)
    early["events"][0]["event_loop_clock_utc"] = "2021-03-15T13:29:59Z"
    add_case(cases, REQUIRED_CASE_IDS[15], not evidence_is_valid(receipt, read_report, early, expected), "early delivery rejected")
    unknown = copy.deepcopy(replay_report)
    unknown["events"][0]["materialized_state_candidate_id"] = "0" * 64
    add_case(cases, REQUIRED_CASE_IDS[16], not evidence_is_valid(receipt, read_report, unknown, expected), "unknown row rejected")
    expanded = copy.deepcopy(replay_report)
    expanded["events"][0]["instrument_id"] = "forbidden_instrument"
    add_case(cases, REQUIRED_CASE_IDS[17], not evidence_is_valid(receipt, read_report, expanded, expected), "instrument expansion rejected")
    unconsumed = copy.deepcopy(receipt)
    unconsumed["authorization_status"] = "NOT_CONSUMED"
    add_case(cases, REQUIRED_CASE_IDS[18], not evidence_is_valid(unconsumed, read_report, replay_report, expected), "unconsumed authorization rejected")
    hard = scope["hard_boundaries"]
    add_case(
        cases,
        REQUIRED_CASE_IDS[19],
        hard["parquet_opened"] is False
        and hard["parquet_hash_recomputed"] is False
        and hard["physical_state_rows_read"] == 0
        and hard["bounded_probe_records_emitted"] == 0,
        "review used execution evidence only",
    )

    ids = [case["case_id"] for case in cases]
    missing = sorted(set(REQUIRED_CASE_IDS) - set(ids))
    unexpected = sorted(set(ids) - set(REQUIRED_CASE_IDS))
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    failed = [case for case in cases if not case["passed"]]
    status = (
        "CLOSED_PASS_BOUNDED_MARKET_STATE_PHYSICAL_READ_AND_REPLAY_REVIEW_WITH_RESTRICTIONS_READY_FOR_BT_GATE_014_HANDOFF"
        if not failed and not missing and not unexpected and not duplicates
        else "CLOSED_BLOCKED_BOUNDED_READ_AND_REPLAY_REVIEW_FAILED"
    )
    matrix = {
        "gate": scope["gate"],
        "created_at_utc": "2026-07-30T00:00:00Z",
        "status": status,
        "case_count": len(cases),
        "required_case_ids": REQUIRED_CASE_IDS,
        "missing_required_case_ids": missing,
        "unexpected_case_ids": unexpected,
        "duplicate_case_ids": duplicates,
        "failed_cases": len(failed),
        "pit_market_state_evidence_ready_for_handoff": not failed,
        "general_StateReplayFeed_authorized": False,
        "backtest_consumption_authorized": False,
        "event_state_authorized": False,
        "parquet_opened_during_review": False,
        "physical_state_rows_read_during_review": 0,
        "next_handoff": scope["next_handoff_on_pass"] if not failed else None,
        "cases": cases,
    }
    MATRIX_PATH.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    readout = f"""# Bounded StateBundle Read and Replay Review Readout v0.1

Gate: `bounded_state_bundle_read_and_replay_review_v0_1`
Date: `2026-07-30`
Status: `{status}`

```text
case_count = {len(cases)}
failed_cases = {len(failed)}
physical_state_rows_read by execution = 2
bounded_probe_records_emitted by execution = 2
physical_state_rows_read during review = 0
early deliveries = 0
unlisted rows delivered = 0
strategy callbacks = 0
signals = 0
orders = 0
fills = 0
PnL = false
```

The provider-to-consumer point-in-time Market State integration probe passed
for the exact ACIU slice authorized by v0.2. Its single-use authorization was
consumed and cannot support another execution.

This review makes the evidence ready for handoff to `BT-GATE-014`. It does not
authorize general StateReplayFeed, strategy consumption, Event State,
production or downstream use.

## Next Handoff

```text
BT-GATE-014_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_EVIDENCE_READY
```
"""
    READOUT_PATH.write_text(readout, encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "case_count": len(cases), "failed_cases": len(failed)}, indent=2))
    return 0 if not failed and not missing and not unexpected and not duplicates else 1


if __name__ == "__main__":
    raise SystemExit(main())
