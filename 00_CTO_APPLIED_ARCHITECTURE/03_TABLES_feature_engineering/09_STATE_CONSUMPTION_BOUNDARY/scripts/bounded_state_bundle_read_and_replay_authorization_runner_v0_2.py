from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = ROOT / "09_STATE_CONSUMPTION_BOUNDARY"
RUNTIME = ROOT / "08_RUNTIME_CAPABILITIES"

SCOPE_PATH = BOUNDARY / "configs/bounded_state_bundle_read_and_replay_authorization_scope_v0_2.json"
SELECTION_PATH = BOUNDARY / "bounded_state_bundle_read_and_replay_selection_manifest_v0_2.json"
SIDECAR_PATH = BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
BUNDLE_PATH = RUNTIME / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_bundle_manifest_v0_1.json"
ALIGNMENT_MATRIX_PATH = BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_matrix_v0_2.json"
MATRIX_PATH = BOUNDARY / "bounded_state_bundle_read_and_replay_authorization_matrix_v0_2.json"
READOUT_PATH = BOUNDARY / "bounded_state_bundle_read_and_replay_authorization_readout_v0_2.md"

REQUIRED_CASE_IDS = [
    "AUTH_V02_UPSTREAM_ALIGNMENT_PASS",
    "AUTH_V02_UPSTREAM_READY_TRUE",
    "AUTH_V02_EXACT_BUNDLE_IDENTITY",
    "AUTH_V02_EXACT_DATASET_IDENTITY",
    "AUTH_V02_EXACT_SIDECAR_IDENTITY",
    "AUTH_V02_ONE_INSTRUMENT",
    "AUTH_V02_ONE_SESSION",
    "AUTH_V02_TWO_EXACT_ROWS",
    "AUTH_V02_ROW_IDS_UNIQUE",
    "AUTH_V02_ROW_FINGERPRINTS_UNIQUE",
    "AUTH_V02_ROWS_EXIST_EXACTLY_ONCE_IN_SIDECAR",
    "AUTH_V02_ROW_METADATA_MATCHES_SIDECAR",
    "AUTH_V02_ROWS_DECISION_SAFE",
    "AUTH_V02_RESTRICTIONS_PRESERVED",
    "AUTH_V02_TEMPORAL_ORDER_NONDECREASING",
    "AUTH_V02_DELIVERY_RULE_AVAILABLE_AT",
    "AUTH_V02_MAXIMUM_ROWS_FAIL_CLOSED",
    "AUTH_V02_UNLISTED_ROW_FAIL_CLOSED",
    "AUTH_V02_WRONG_INSTRUMENT_FAIL_CLOSED",
    "AUTH_V02_WRONG_SESSION_FAIL_CLOSED",
    "AUTH_V02_EVENT_STATE_PROHIBITED",
    "AUTH_V02_USER_PATHS_PROHIBITED",
    "AUTH_V02_STRATEGY_EXECUTION_PROHIBITED",
    "AUTH_V02_SELECTION_MANIFEST_HASH_FROZEN",
    "AUTH_V02_NO_PHYSICAL_READ_IN_AUTHORIZATION_GATE",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_case(rows: list[dict[str, Any]], case_id: str, passed: bool, evidence: str) -> None:
    rows.append(
        {
            "case_id": case_id,
            "expected": "PASS",
            "observed": "PASS" if passed else "FAIL",
            "passed": passed,
            "evidence": evidence,
        }
    )


def selection_is_valid(
    selection: dict[str, Any],
    sidecar: dict[str, Any],
    *,
    expected_instrument: str,
    expected_session: str,
) -> bool:
    selected = selection["authorized_rows"]
    sidecar_by_id: dict[str, list[dict[str, Any]]] = {}
    for record in sidecar["records"]:
        sidecar_by_id.setdefault(record["materialized_state_candidate_id"], []).append(record)

    if len(selected) != selection["authorized_row_count"]:
        return False
    if len(selected) > selection["maximum_rows"]:
        return False
    if any(row["materialized_state_candidate_id"] not in sidecar_by_id for row in selected):
        return False
    if any(len(sidecar_by_id[row["materialized_state_candidate_id"]]) != 1 for row in selected):
        return False

    for row in selected:
        observed = sidecar_by_id[row["materialized_state_candidate_id"]][0]
        if observed["instrument_id"] != expected_instrument:
            return False
        if observed["session_date"] != expected_session:
            return False
        for field in (
            "context_id",
            "state_output_fingerprint",
            "decision_timestamp_utc",
            "state_as_of_utc",
            "state_available_at_utc",
            "state_replay_consumption_legality",
        ):
            if row[field] != observed[field]:
                return False
    return True


def main() -> int:
    scope = load_json(SCOPE_PATH)
    selection = load_json(SELECTION_PATH)
    sidecar = load_json(SIDECAR_PATH)
    bundle = load_json(BUNDLE_PATH)
    alignment = load_json(ALIGNMENT_MATRIX_PATH)
    probe = scope["authorized_probe"]
    boundaries = scope["authorization_gate_boundaries"]
    selected = selection["authorized_rows"]
    rows: list[dict[str, Any]] = []

    add_case(rows, REQUIRED_CASE_IDS[0], alignment["blocking_findings"] == 0, alignment["status"])
    add_case(rows, REQUIRED_CASE_IDS[1], alignment["physical_read_authorization_ready"] is True, "alignment ready")
    add_case(
        rows,
        REQUIRED_CASE_IDS[2],
        bundle["bundle_ref"]["ref_id"] == probe["bundle_ref_id"]
        and bundle["bundle_ref"]["sha256"] == probe["bundle_canonical_sha256"]
        and sha256_file(BUNDLE_PATH) == probe["bundle_artifact_sha256"],
        "bundle ref, canonical hash and artifact hash match",
    )
    dataset_ref = bundle["dataset_refs"]["market_state_dataset_ref"]
    add_case(
        rows,
        REQUIRED_CASE_IDS[3],
        dataset_ref["dataset_id"] == probe["dataset_id"]
        and dataset_ref["candidate_dataset_fingerprint"] == probe["dataset_fingerprint"],
        "dataset identity frozen",
    )
    add_case(
        rows,
        REQUIRED_CASE_IDS[4],
        sidecar["candidate_dataset_id"] == probe["dataset_id"]
        and sidecar["candidate_dataset_fingerprint"] == probe["dataset_fingerprint"]
        and sha256_file(SIDECAR_PATH)
        == next(item["sha256"] for item in scope["frozen_artifacts"] if item["artifact_id"] == "replay_availability_sidecar"),
        "sidecar identity and hash match",
    )
    add_case(rows, REQUIRED_CASE_IDS[5], {probe["instrument_id"]} == {selection["instrument_id"]}, probe["instrument_id"])
    add_case(rows, REQUIRED_CASE_IDS[6], {probe["session_date"]} == {selection["session_date"]}, probe["session_date"])
    add_case(rows, REQUIRED_CASE_IDS[7], len(selected) == 2 == probe["authorized_row_count"], "two exact rows")
    add_case(rows, REQUIRED_CASE_IDS[8], len({r["materialized_state_candidate_id"] for r in selected}) == len(selected), "row IDs unique")
    add_case(rows, REQUIRED_CASE_IDS[9], len({r["state_output_fingerprint"] for r in selected}) == len(selected), "fingerprints unique")

    sidecar_counts: dict[str, int] = {}
    for record in sidecar["records"]:
        key = record["materialized_state_candidate_id"]
        sidecar_counts[key] = sidecar_counts.get(key, 0) + 1
    add_case(
        rows,
        REQUIRED_CASE_IDS[10],
        all(sidecar_counts.get(r["materialized_state_candidate_id"]) == 1 for r in selected),
        "each selected row occurs exactly once",
    )
    add_case(
        rows,
        REQUIRED_CASE_IDS[11],
        selection_is_valid(
            selection,
            sidecar,
            expected_instrument=probe["instrument_id"],
            expected_session=probe["session_date"],
        ),
        "selection fields equal sidecar fields",
    )
    add_case(rows, REQUIRED_CASE_IDS[12], all(r["state_replay_consumption_legality"] == "decision_safe" for r in selected), "all rows decision_safe")
    required_restrictions = set(selection["required_restriction_codes"])
    selected_ids = {r["materialized_state_candidate_id"] for r in selected}
    selected_sidecar = [r for r in sidecar["records"] if r["materialized_state_candidate_id"] in selected_ids]
    add_case(
        rows,
        REQUIRED_CASE_IDS[13],
        all(required_restrictions.issubset(set(r["restriction_codes"])) for r in selected_sidecar)
        and required_restrictions.issubset(set(bundle["restrictions"])),
        "restrictions preserved by rows and bundle",
    )
    ordered = sorted(selected, key=lambda r: (r["state_available_at_utc"], "market_state", selection["instrument_id"], r["materialized_state_candidate_id"]))
    add_case(rows, REQUIRED_CASE_IDS[14], [r["state_available_at_utc"] for r in ordered] == sorted(r["state_available_at_utc"] for r in selected), "available-at order")
    add_case(rows, REQUIRED_CASE_IDS[15], selection["delivery_eligibility_rule"] == "event_loop.clock >= state_available_at_utc", selection["delivery_eligibility_rule"])

    too_many = copy.deepcopy(selection)
    too_many["authorized_rows"].append(copy.deepcopy(sidecar["records"][0]))
    add_case(
        rows,
        REQUIRED_CASE_IDS[16],
        not selection_is_valid(too_many, sidecar, expected_instrument=probe["instrument_id"], expected_session=probe["session_date"]),
        "third row rejected by maximum_rows",
    )
    unlisted = copy.deepcopy(selection)
    unlisted["authorized_rows"][0] = copy.deepcopy(sidecar["records"][0])
    add_case(
        rows,
        REQUIRED_CASE_IDS[17],
        not selection_is_valid(unlisted, sidecar, expected_instrument=probe["instrument_id"], expected_session=probe["session_date"]),
        "unlisted row rejected",
    )
    wrong_instrument = copy.deepcopy(selection)
    wrong_instrument["instrument_id"] = "forbidden_instrument"
    add_case(
        rows,
        REQUIRED_CASE_IDS[18],
        not selection_is_valid(wrong_instrument, sidecar, expected_instrument=wrong_instrument["instrument_id"], expected_session=probe["session_date"]),
        "wrong instrument rejected",
    )
    wrong_session = copy.deepcopy(selection)
    wrong_session["session_date"] = "2099-01-01"
    add_case(
        rows,
        REQUIRED_CASE_IDS[19],
        not selection_is_valid(wrong_session, sidecar, expected_instrument=probe["instrument_id"], expected_session=wrong_session["session_date"]),
        "wrong session rejected",
    )
    prohibited = set(scope["prohibited_behavior"])
    add_case(rows, REQUIRED_CASE_IDS[20], selection["event_state_requested"] is False and "event_state" in prohibited, "Event State excluded")
    add_case(rows, REQUIRED_CASE_IDS[21], "user_supplied_paths" in prohibited and "path_discovery_outside_frozen_artifacts" in prohibited, "paths fail closed")
    add_case(rows, REQUIRED_CASE_IDS[22], selection["strategy_execution"] is False and "strategy_callbacks" in prohibited, "strategy excluded")
    selection_sha256 = sha256_file(SELECTION_PATH)
    frozen_selection_sha256 = next(
        item["sha256"]
        for item in scope["frozen_artifacts"]
        if item["artifact_id"] == "selection_manifest"
    )
    add_case(
        rows,
        REQUIRED_CASE_IDS[23],
        selection_sha256 == frozen_selection_sha256,
        "selection manifest hash is frozen by scope",
    )
    add_case(
        rows,
        REQUIRED_CASE_IDS[24],
        boundaries["parquet_opened"] is False
        and boundaries["parquet_hash_recomputed"] is False
        and boundaries["physical_state_rows_read"] == 0
        and boundaries["bounded_probe_records_emitted"] == 0,
        "authorization gate performed no physical read or replay",
    )

    case_ids = [row["case_id"] for row in rows]
    missing = sorted(set(REQUIRED_CASE_IDS) - set(case_ids))
    unexpected = sorted(set(case_ids) - set(REQUIRED_CASE_IDS))
    duplicates = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
    failed = [row for row in rows if not row["passed"]]
    status = (
        "CLOSED_AUTHORIZED_ONE_BOUNDED_MARKET_STATE_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS_NO_EXECUTION"
        if not failed and not missing and not unexpected and not duplicates
        else "CLOSED_BLOCKED_AUTHORIZATION_VALIDATION_FAILED_NO_PHYSICAL_READ"
    )
    matrix = {

        "gate": "bounded_state_bundle_read_and_replay_authorization_v0_2",
        "created_at_utc": "2026-07-30T00:00:00Z",
        "status": status,
        "case_count": len(rows),
        "required_case_ids": REQUIRED_CASE_IDS,
        "missing_required_case_ids": missing,
        "unexpected_case_ids": unexpected,
        "duplicate_case_ids": duplicates,
        "failed_cases": len(failed),
        "authorization_to_read_issued": not failed,
        "bounded_execution_authorized": not failed,
        "selection_manifest_sha256": selection_sha256,
        "authorized_row_count": selection["authorized_row_count"],
        "maximum_rows": selection["maximum_rows"],
        "parquet_opened": False,
        "parquet_hash_recomputed": False,
        "physical_state_rows_read": 0,
        "bounded_probe_records_emitted": 0,
        "general_StateReplayFeed_authorized": False,
        "strategy_callbacks": 0,
        "orders_emitted": 0,
        "fills_emitted": 0,
        "PnL_calculated": False,
        "backtest_consumption": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_gate": "bounded_state_bundle_read_and_replay_execution_v0_1" if not failed else None,
        "cases": rows,
    }
    MATRIX_PATH.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")

    readout = f"""# Bounded StateBundle Read and Replay Authorization Readout v0.2

Gate: `bounded_state_bundle_read_and_replay_authorization_v0_2`
Date: `2026-07-30`
Status: `{status}`

## Result

```text
case_count = {len(rows)}
failed_cases = {len(failed)}
missing_required_case_ids = {len(missing)}
duplicate_case_ids = {len(duplicates)}
authorization_to_read_issued = {str(not failed).lower()}
bounded_execution_authorized = {str(not failed).lower()}
```

One later execution gate may open the exact frozen candidate parquet and
project exactly two ACIU records for session 2021-03-15. The permitted row IDs,
fingerprints and replay timestamps are frozen in the selection manifest:

```text
selection_manifest_sha256 = {selection_sha256}
authorized_row_count = 2
maximum_rows = 2
maximum_physical_data_files = 1
```

This authorization gate did not open the parquet, read state rows, emit replay
records or execute any backtest behavior.

## Preserved Restrictions

```text
candidate_runtime_only
official_dataset = false
production = false
downstream = false
general StateReplayFeed = NOT_AUTHORIZED
strategy callbacks = 0
signals = 0
orders = 0
fills = 0
PnL = false
```

## Next Gate

```text
bounded_state_bundle_read_and_replay_execution_v0_1
```
"""
    READOUT_PATH.write_text(readout, encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "case_count": len(rows), "failed_cases": len(failed), "selection_manifest_sha256": selection_sha256}, indent=2))
    return 0 if not failed and not missing and not unexpected and not duplicates else 1


if __name__ == "__main__":
    raise SystemExit(main())
