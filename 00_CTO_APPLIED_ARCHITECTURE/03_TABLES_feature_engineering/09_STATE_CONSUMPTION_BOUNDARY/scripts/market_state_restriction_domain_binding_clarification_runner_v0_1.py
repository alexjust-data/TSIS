from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TABLES = Path(__file__).resolve().parents[2]
BOUNDARY = TABLES / "09_STATE_CONSUMPTION_BOUNDARY"
ROOT = TABLES.parents[1]
CONTRACT = BOUNDARY / "market_state_restriction_domain_binding_clarification_v0_1.json"
MATRIX = BOUNDARY / "market_state_restriction_domain_binding_clarification_matrix_v0_1.json"
READOUT = BOUNDARY / "market_state_restriction_domain_binding_clarification_readout_v0_1.md"
FAILURE = (
    ROOT
    / "02_TSIS_BACKTEST_ENGINE"
    / "runs"
    / "bt_gate_014_single_use_physical_market_state_consumer_v0_4"
    / "failure_manifest.json"
)

REQUIRED_CASE_IDS = [
    "RDB_CONTRACT_JSON_PARSE",
    "RDB_AUTHORITY_INPUT_HASHES_MATCH",
    "RDB_V0_4_FAILURE_MANIFEST_HASH_MATCH",
    "RDB_V0_4_CONSUMED_FAILURE_CONFIRMED",
    "RDB_PHYSICAL_PROVENANCE_DOMAIN_OBSERVED",
    "RDB_REPLAY_CONSUMPTION_DOMAIN_OBSERVED",
    "RDB_COMPONENT_REPLAY_DOMAIN_OBSERVED",
    "RDB_PHYSICAL_AND_REPLAY_DOMAINS_DISTINCT",
    "RDB_BOUNDED_CODES_MATCH_SELECTION_AUTHORITY",
    "RDB_SIDECAR_ROW_CODES_MATCH_BOUNDED_DOMAIN",
    "RDB_COMPONENT_CODES_SUBSET_ROW_CODES",
    "RDB_PHYSICAL_RAW_PRESERVATION_REQUIRED",
    "RDB_UNLABELED_UNION_PROHIBITED",
    "RDB_CONSUMER_PROJECTION_LABELS_COMPLETE",
    "RDB_NO_HISTORICAL_PROVIDER_MUTATION",
    "RDB_NO_BACKTESTER_MUTATION",
    "RDB_NO_PHYSICAL_READ",
    "RDB_NO_V0_5_AUTHORIZATION",
    "RDB_EVENT_STATE_REMAINS_CLOSED",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(cases: list[dict[str, Any]], case_id: str, passed: bool, evidence: Any) -> None:
    cases.append(
        {
            "case_id": case_id,
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
            "evidence": evidence,
        }
    )


def main() -> int:
    contract = load(CONTRACT)
    failure = load(FAILURE)
    selection = load(BOUNDARY / "bounded_state_bundle_read_and_replay_selection_manifest_v0_2.json")
    sidecar = load(
        BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
    )
    records = sidecar.get("records", sidecar.get("rows", []))
    diagnostics = failure["restriction_diagnostics"]
    physical_rows = diagnostics["rows"]
    replay_rows = diagnostics["sidecars"]
    component_rows = diagnostics["components"]
    bounded = set(contract["domains"]["replay_consumption_restriction_codes"]["required_codes"])
    cases: list[dict[str, Any]] = []

    add(cases, REQUIRED_CASE_IDS[0], contract["contract_id"].endswith("_v0_1"), contract["contract_id"])

    input_results = []
    for item in contract["authority_inputs"]:
        path = TABLES / item["path"]
        observed = sha256(path)
        input_results.append({"role": item["role"], "observed": observed, "match": observed == item["sha256"]})
    add(cases, REQUIRED_CASE_IDS[1], all(row["match"] for row in input_results), input_results)

    add(
        cases,
        REQUIRED_CASE_IDS[2],
        sha256(FAILURE) == contract["incident_evidence"]["failure_manifest_sha256"],
        sha256(FAILURE),
    )
    add(
        cases,
        REQUIRED_CASE_IDS[3],
        failure["error_code"] == "FAIL_MARKET_STATE_RESTRICTION_PROPAGATION"
        and failure["physical_data_files_opened"] == 1
        and failure["physical_state_rows_read"] == 2
        and failure["market_state_events_emitted"] == 0,
        {
            "error_code": failure["error_code"],
            "files": failure["physical_data_files_opened"],
            "rows": failure["physical_state_rows_read"],
            "events": failure["market_state_events_emitted"],
        },
    )
    add(
        cases,
        REQUIRED_CASE_IDS[4],
        len(physical_rows) == 2 and all(len(set(row)) == 26 for row in physical_rows),
        [len(set(row)) for row in physical_rows],
    )
    add(
        cases,
        REQUIRED_CASE_IDS[5],
        len(replay_rows) == 2 and all(set(row) == bounded for row in replay_rows),
        replay_rows,
    )
    add(
        cases,
        REQUIRED_CASE_IDS[6],
        len(component_rows) == 2
        and all(len(components) == 4 for components in component_rows)
        and all(set(codes) == bounded for components in component_rows for codes in components),
        {"rows": len(component_rows), "components_per_row": [len(row) for row in component_rows]},
    )
    add(
        cases,
        REQUIRED_CASE_IDS[7],
        all(set(physical) != set(replay) for physical, replay in zip(physical_rows, replay_rows)),
        "26 physical provenance codes are not the four bounded replay codes",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[8],
        set(selection["required_restriction_codes"]) == bounded,
        selection["required_restriction_codes"],
    )
    add(
        cases,
        REQUIRED_CASE_IDS[9],
        len(records) == 104 and all(set(row["restriction_codes"]) == bounded for row in records),
        {"sidecar_records": len(records), "bounded_codes": sorted(bounded)},
    )
    add(
        cases,
        REQUIRED_CASE_IDS[10],
        all(
            set(component["restriction_codes"]).issubset(set(row["restriction_codes"]))
            for row in records
            for component in row["component_availability_evidence"]
        ),
        "all component replay restrictions are subsets of their row replay restrictions",
    )
    rules = set(contract["binding_rules"])
    add(
        cases,
        REQUIRED_CASE_IDS[11],
        "physical row restriction_codes_json must remain fingerprinted and preserved byte-reproducibly" in rules,
        "physical raw restriction preservation is explicit",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[12],
        "an unlabeled union must not be used as the executable restriction policy" in rules,
        "unlabeled executable union is prohibited",
    )
    required_projection = {
        "physical_provenance_restriction_codes",
        "replay_consumption_restriction_codes",
        "component_replay_restriction_codes",
        "physical_restriction_codes_raw_json",
    }
    add(
        cases,
        REQUIRED_CASE_IDS[13],
        set(contract["consumer_projection"]["required_fields"]) == required_projection,
        sorted(required_projection),
    )
    boundaries = contract["boundaries"]
    add(
        cases,
        REQUIRED_CASE_IDS[14],
        boundaries["historical_sidecar_modified"] is False
        and boundaries["historical_provider_evidence_modified"] is False
        and boundaries["provider_control_plane_modified"] is False,
        "historical provider artifacts remain immutable",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[15],
        boundaries["backtester_modified"] is False,
        "consumer implementation remains owned by BT-GATE-014",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[16],
        boundaries["parquet_opened_by_this_gate"] is False
        and boundaries["physical_rows_read_by_this_gate"] == 0,
        "metadata and failure-evidence-only validation",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[17],
        boundaries["V0_4_reusable"] is False
        and boundaries["V0_5_authorized"] is False
        and boundaries["new_consumer_authorization_issued"] is False,
        "no reusable or new consumer authorization",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[18],
        boundaries["Event_State_authorized"] is False
        and boundaries["StateReplayFeed_general_authorized"] is False,
        "Event State and general StateReplayFeed remain closed",
    )

    ids = [case["case_id"] for case in cases]
    missing = sorted(set(REQUIRED_CASE_IDS) - set(ids))
    unexpected = sorted(set(ids) - set(REQUIRED_CASE_IDS))
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    failed = [case for case in cases if not case["passed"]]
    passed = not failed and not missing and not unexpected and not duplicates
    status = (
        "CLOSED_PASS_RESTRICTION_DOMAINS_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ_NO_CONSUMER_AUTHORIZATION"
        if passed
        else "CLOSED_BLOCKED_RESTRICTION_DOMAIN_BINDING_FAILED"
    )
    matrix = {
        "gate": contract["contract_id"],
        "created_at_utc": "2026-07-30T00:00:00Z",
        "status": status,
        "case_count": len(cases),
        "required_case_ids": REQUIRED_CASE_IDS,
        "missing_required_case_ids": missing,
        "unexpected_case_ids": unexpected,
        "duplicate_case_ids": duplicates,
        "failed_cases": len(failed),
        "parquet_opened": False,
        "physical_rows_read": 0,
        "backtester_files_modified": 0,
        "new_consumer_authorization_issued": False,
        "cases": cases,
    }
    MATRIX.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    readout = f"""# Market State Restriction Domain Binding Clarification Readout v0.1

Gate: `{contract["contract_id"]}`
Date: `2026-07-30`
Status: `{status}`

```text
case_count = {len(cases)}
failed_cases = {len(failed)}
physical provenance restrictions observed per row = 26
bounded replay-consumption restrictions = 4
required core-four components per row = 4
parquet opened by this gate = false
physical rows read by this gate = 0
backtester files modified = 0
new consumer authorization issued = false
```

The V0.4 failure is accepted as a correct fail-closed result. The physical row
restriction field and the replay sidecar restriction field are not the same
semantic domain and must not be compared for equality.

Physical provenance restrictions remain fingerprinted physical lineage.
Replay-consumption restrictions govern bounded delivery. Component replay
restrictions must propagate into the row replay-consumption set.

V0.4 remains consumed and cannot be reused. This clarification does not
authorize V0.5. The BT-GATE-014 owner must adopt the labeled domains in its
consumer contract, event, store, lineage and regression suite, then submit a
new single-use authorization for independent pre-execution review.
"""
    READOUT.write_text(readout, encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "case_count": len(cases), "failed_cases": len(failed)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
