#!/usr/bin/env python3
"""Validate the Event State incremental lineage chain.

Review-only runner. It expands the second-generation Event State candidate into
baseline, delta1, delta2 and unavailable origins, then checks row identity,
content fingerprints, dependency fingerprints and parent evidence immutability.
It does not execute resolvers, materialize records, mutate registry entries,
promote datasets, or open downstream authority.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
CONFIGS = ROOT / "configs"

GATE_ID = "event_state_on_demand_incremental_lineage_chain_validation_v0_1"
SCRIPT_VERSION = "event_state_on_demand_incremental_lineage_chain_validation_runner_v0_1"
VALIDATION_ID = f"{GATE_ID}_20260728T000000Z"
STATUS_PASS = "CLOSED_PASS_EVENT_STATE_INCREMENTAL_LINEAGE_CHAIN_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION"
STATUS_FAIL = "CLOSED_BLOCKED_EVENT_STATE_INCREMENTAL_LINEAGE_CHAIN_VALIDATION_FAILURE"
NEXT_GATE = "event_state_on_demand_scale_validation_v0_1"

BASELINE_RUN_ID = "event_state_on_demand_bounded_execution_v0_1_20260727T200322Z"
GEN1_RUN_ID = "event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z"
GEN2_RUN_ID = "event_state_on_demand_second_generation_incremental_extension_v0_1_20260728T103016Z"
SOURCE_REVIEW_RUN_ID = (
    "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260728T110845Z"
)
SOURCE_REVIEW_ID = (
    "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260728T000000Z"
)

BASELINE_RUN = RUNS / BASELINE_RUN_ID
GEN1_RUN = RUNS / GEN1_RUN_ID
GEN2_RUN = RUNS / GEN2_RUN_ID
SOURCE_REVIEW_RUN = RUNS / SOURCE_REVIEW_RUN_ID

EXPECTED = {
    "source_review_status": "CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION",
    "gen2_run_status": "CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
    "baseline_candidate_dataset_fingerprint": "d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33",
    "gen1_candidate_dataset_fingerprint": "f88cc0a0a39117f315baf4312dc13533baae8b8574c6966ca91582ca98406c4f",
    "gen2_candidate_dataset_fingerprint": "9a31d9b8bf3af01c1c4a5cd18a37309eec7b3cb41011501ab85e0ef4a4831746",
    "gen1_logical_dataset_fingerprint": "73b2f81b76697eb67b55faffecd36c8e77ecf926c1c1f9e56cf6ee0e0ecb10f6",
    "gen2_logical_dataset_fingerprint": "b4774100b8ab27794e8d9a9205227c6e694442e8287b92bf5d899ec3a0b66f33",
    "baseline_market_state_fingerprint": "433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b",
    "delta1_market_state_fingerprint": "5e8da235219628220bac462f342cab469fbd2a48d047eef0772cb5a2cffe893f",
    "delta2_market_state_fingerprint": "f2cfd5cf55d0c1be1722693cc0216ffd425bbb869e19c17745976c030f2c7a2a",
    "requested_contexts": 15,
    "represented_contexts": 14,
    "baseline_origin_rows": 8,
    "delta1_origin_rows": 3,
    "delta2_origin_rows": 3,
    "unavailable_contexts": 1,
    "unavailable_session_date": "2022-11-25",
    "unavailable_instrument_id": "figi_share_class:BBG001S5N8T1",
    "unavailable_reason": "missing_exact_market_state_binding",
    "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1",
    "event_type_id": "event_type:market_data:session_opened",
    "event_window_definition_id": "session_opened_at_anchor_context_v0_1",
}

REQUIRED_RECORD_FIELDS = [
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


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_obj(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def context_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            str(row.get("event_type_id", "")),
            str(row.get("exchange_id", "")),
            str(row.get("session_date", "")),
            str(row.get("instrument_id", "")),
            str(row.get("event_anchor_timestamp_utc", row.get("decision_timestamp_utc", ""))),
            str(row.get("event_window_definition_id", "")),
        ]
    )


def row_identity(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_state_record_id": row.get("event_state_record_id"),
        "event_state_record_fingerprint": row.get("event_state_record_fingerprint"),
        "event_instance_id": row.get("event_instance_id"),
        "event_window_binding_id": row.get("event_window_binding_id"),
        "event_state_instrument_session_projection_id": row.get("event_state_instrument_session_projection_id"),
        "market_state_record_id": row.get("market_state_record_id"),
        "state_output_fingerprint": row.get("state_output_fingerprint"),
        "source_market_state_candidate_dataset_fingerprint": row.get("source_market_state_candidate_dataset_fingerprint"),
    }


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    passed: bool,
    evidence: Any = None,
    severity: str = "BLOCKING",
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "status": "PASS" if passed else "FAIL",
            "severity": severity,
            "evidence": evidence,
        }
    )


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(key, "")) for row in rows).items()))


def review_readout(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Event State On-Demand Incremental Lineage Chain Validation Readout v0.1

Status: `{matrix['validation_status']}`
Date: `2026-07-28`

```text
validation_id = {matrix['validation_id']}
validation_run_id = {matrix['validation_run_id']}
source_review = {matrix['source_review_run_id']}
validation_decision = {d['validation_decision']}
requested_contexts = {d['requested_contexts']}
represented_contexts = {d['represented_contexts']}
baseline_origin_rows = {d['baseline_origin_rows']}
delta1_origin_rows = {d['delta1_origin_rows']}
delta2_origin_rows = {d['delta2_origin_rows']}
unavailable_contexts = {d['unavailable_contexts']}
unaccounted_contexts = {d['unaccounted_contexts']}
duplicate_canonical_contexts = {d['duplicate_canonical_contexts']}
missing_parent_refs = {d['missing_parent_refs']}
row_identity_mismatches = {d['row_identity_mismatches']}
hard_validation_failures = {d['hard_validation_failures']}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

The lineage chain is accepted only as bounded Event State runtime evidence. The
validation proves that generation 2 is a governed composition of immutable
baseline, delta1 and delta2 evidence, with the inherited unavailable context
preserved and no promotion or downstream authority opened.
"""


def authorization_text(validation_run_id: str) -> str:
    return f"""# Event State On-Demand Incremental Lineage Chain Validation Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_VALIDATION`
Date: `2026-07-28`

```text
validation_id = {VALIDATION_ID}
validation_run_id = {validation_run_id}
source_review = {SOURCE_REVIEW_RUN_ID}
execution_authorized = false
event_state_materialization_authorized = false
market_state_materialization_authorized = false
source_market_data_reads_authorized = false
registry_mutation_authorized = false
official_dataset_promotion_authorized = false
production_authorized = false
downstream_authorized = false
```

This gate authorizes validation only. It may inspect closed manifests, records,
ledgers and hashes from Event State baseline, delta1 and delta2 evidence. It
does not authorize creating Event State rows, reading raw market data,
materializing Market State, mutating prior evidence, promoting datasets,
production or downstream consumption.
"""


def main() -> int:
    started_at = utc_iso()
    validation_run_id = f"{GATE_ID}_{utc_compact()}"
    run_dir = RUNS / validation_run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    baseline_final = read_json(BASELINE_RUN / "final_manifest.json")
    gen1_final = read_json(GEN1_RUN / "final_manifest.json")
    gen2_final = read_json(GEN2_RUN / "final_manifest.json")
    source_review_final = read_json(SOURCE_REVIEW_RUN / "final_manifest.json")
    source_review_matrix = read_json(ROOT / "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_matrix_v0_1.json")

    baseline_records = read_jsonl(BASELINE_RUN / "event_state_candidate_records.jsonl")
    gen1_records = read_jsonl(GEN1_RUN / "event_state_incremental_overlap_candidate_records.jsonl")
    gen2_records = read_jsonl(GEN2_RUN / "event_state_second_generation_incremental_candidate_records.jsonl")
    delta2_records = read_jsonl(GEN2_RUN / "delta_2_event_state_candidate_records.jsonl")

    baseline_ledger = read_json(BASELINE_RUN / "event_state_logical_context_ledger.json")
    gen1_ledger = read_json(GEN1_RUN / "combined_event_state_context_ledger_v0_1.json")
    gen2_ledger = read_json(GEN2_RUN / "combined_event_state_context_ledger_v0_1.json")
    gen2_lineage = read_json(GEN2_RUN / "event_state_second_generation_incremental_lineage_manifest.json")

    baseline_by_key = {context_key(row): row for row in baseline_records}
    gen1_by_key = {context_key(row): row for row in gen1_records}
    gen2_by_key = {context_key(row): row for row in gen2_records}
    delta2_by_key = {context_key(row): row for row in delta2_records}
    baseline_ledger_by_key = {context_key(row): row for row in baseline_ledger}
    gen1_ledger_by_key = {context_key(row): row for row in gen1_ledger}

    expanded_entries: list[dict[str, Any]] = []
    baseline_origin_rows = 0
    delta1_origin_rows = 0
    delta2_origin_rows = 0
    unavailable_contexts = 0
    missing_parent_refs = 0
    row_identity_mismatches = 0
    market_state_dependency_mismatches = 0
    mandatory_field_gaps = 0

    for entry in gen2_ledger:
        key = context_key(entry)
        source = entry.get("representation_source")
        out = dict(entry)
        out["context_key"] = key

        if source == "reused_validated_event_state":
            parent_ledger_entry = gen1_ledger_by_key.get(key)
            parent_record = gen1_by_key.get(key)
            gen2_record = gen2_by_key.get(key)
            if parent_ledger_entry is None or parent_record is None or gen2_record is None:
                missing_parent_refs += 1
                out["expanded_origin_mode"] = "missing_generation_1_reference"
            else:
                parent_source = parent_ledger_entry.get("representation_source")
                out["generation_1_representation_source"] = parent_source
                out["generation_1_origin_run_id"] = parent_ledger_entry.get("origin_run_id")
                out["generation_1_origin_dataset_id"] = parent_ledger_entry.get("origin_dataset_id")
                out["generation_1_origin_candidate_dataset_fingerprint"] = parent_ledger_entry.get(
                    "origin_candidate_dataset_fingerprint"
                )
                if row_identity(parent_record) != row_identity(gen2_record):
                    row_identity_mismatches += 1
                    out["row_identity_match"] = False
                    out["generation_1_row_identity"] = row_identity(parent_record)
                    out["generation_2_row_identity"] = row_identity(gen2_record)
                else:
                    out["row_identity_match"] = True

                if parent_source == "reused_validated_event_state":
                    baseline_ledger_entry = baseline_ledger_by_key.get(key)
                    baseline_record = baseline_by_key.get(key)
                    if baseline_ledger_entry is None or baseline_record is None:
                        missing_parent_refs += 1
                        out["expanded_origin_mode"] = "missing_baseline_reference"
                    elif row_identity(baseline_record) != row_identity(gen2_record):
                        row_identity_mismatches += 1
                        out["expanded_origin_mode"] = "baseline_origin_identity_mismatch"
                        out["baseline_row_identity"] = row_identity(baseline_record)
                    else:
                        baseline_origin_rows += 1
                        out["expanded_origin_mode"] = "baseline_origin"
                        out["origin_generation"] = 0
                        out["ultimate_origin_run_id"] = BASELINE_RUN_ID
                        out["ultimate_origin_dataset_fingerprint"] = EXPECTED["baseline_candidate_dataset_fingerprint"]
                elif parent_source == "delta_materialized_event_state":
                    delta1_origin_rows += 1
                    out["expanded_origin_mode"] = "delta1_origin"
                    out["origin_generation"] = 1
                    out["ultimate_origin_run_id"] = GEN1_RUN_ID
                    out["ultimate_origin_dataset_fingerprint"] = EXPECTED["gen1_candidate_dataset_fingerprint"]
                else:
                    missing_parent_refs += 1
                    out["expanded_origin_mode"] = "unexpected_generation_1_source"

        elif source == "delta_2_materialized_event_state":
            gen2_record = gen2_by_key.get(key)
            delta2_record = delta2_by_key.get(key)
            if gen2_record is None or delta2_record is None:
                missing_parent_refs += 1
                out["expanded_origin_mode"] = "missing_delta2_reference"
            elif row_identity(gen2_record) != row_identity(delta2_record):
                row_identity_mismatches += 1
                out["expanded_origin_mode"] = "delta2_origin_identity_mismatch"
                out["generation_2_row_identity"] = row_identity(gen2_record)
                out["delta2_row_identity"] = row_identity(delta2_record)
            else:
                delta2_origin_rows += 1
                out["expanded_origin_mode"] = "delta2_origin"
                out["origin_generation"] = 2
                out["ultimate_origin_run_id"] = GEN2_RUN_ID
                out["ultimate_origin_dataset_fingerprint"] = EXPECTED["gen2_candidate_dataset_fingerprint"]

        elif entry.get("context_status") == "unavailable":
            parent_ledger_entry = gen1_ledger_by_key.get(key)
            baseline_ledger_entry = baseline_ledger_by_key.get(key)
            if parent_ledger_entry is None or baseline_ledger_entry is None:
                missing_parent_refs += 1
                out["expanded_origin_mode"] = "missing_unavailable_parent_reference"
            elif (
                parent_ledger_entry.get("context_status") == "unavailable"
                and baseline_ledger_entry.get("context_status") == "unavailable"
                and entry.get("blocking_reason") == EXPECTED["unavailable_reason"]
            ):
                unavailable_contexts += 1
                out["expanded_origin_mode"] = "unavailable_preserved_from_baseline"
                out["origin_generation"] = "inherited_unavailable"
                out["ultimate_origin_run_id"] = BASELINE_RUN_ID
            else:
                missing_parent_refs += 1
                out["expanded_origin_mode"] = "unavailable_parent_status_mismatch"
        else:
            missing_parent_refs += 1
            out["expanded_origin_mode"] = "unexpected_generation_2_source"

        if entry.get("context_status") == "represented":
            row = gen2_by_key.get(key, {})
            missing_fields = [field for field in REQUIRED_RECORD_FIELDS if not row.get(field)]
            if missing_fields:
                mandatory_field_gaps += 1
                out["mandatory_field_gaps"] = missing_fields
            fp = row.get("source_market_state_candidate_dataset_fingerprint")
            if out.get("expanded_origin_mode") == "baseline_origin" and fp != EXPECTED["baseline_market_state_fingerprint"]:
                market_state_dependency_mismatches += 1
            if out.get("expanded_origin_mode") == "delta1_origin" and fp != EXPECTED["delta1_market_state_fingerprint"]:
                market_state_dependency_mismatches += 1
            if out.get("expanded_origin_mode") == "delta2_origin" and fp != EXPECTED["delta2_market_state_fingerprint"]:
                market_state_dependency_mismatches += 1

        expanded_entries.append(out)

    requested_contexts = len(expanded_entries)
    represented_contexts = baseline_origin_rows + delta1_origin_rows + delta2_origin_rows
    unaccounted_contexts = requested_contexts - represented_contexts - unavailable_contexts
    duplicate_contexts = requested_contexts - len({entry["context_key"] for entry in expanded_entries})
    duplicate_record_ids = len(gen2_records) - len({row.get("event_state_record_id") for row in gen2_records})
    unavailable_key = next((entry["context_key"] for entry in expanded_entries if entry.get("context_status") == "unavailable"), "")

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "source_review_closed_pass",
        source_review_final.get("final_run_status") == EXPECTED["source_review_status"]
        and source_review_matrix.get("review_status") == EXPECTED["source_review_status"],
        {
            "source_review_final": source_review_final.get("final_run_status"),
            "source_review_matrix": source_review_matrix.get("review_status"),
        },
    )
    add_check(checks, "gen2_run_closed_pass", gen2_final.get("final_run_status") == EXPECTED["gen2_run_status"], gen2_final.get("final_run_status"))
    add_check(checks, "generation_fingerprints_match", baseline_final.get("candidate_dataset_fingerprint") == EXPECTED["baseline_candidate_dataset_fingerprint"] and gen1_final.get("candidate_dataset_fingerprint") == EXPECTED["gen1_candidate_dataset_fingerprint"] and gen2_final.get("candidate_dataset_fingerprint") == EXPECTED["gen2_candidate_dataset_fingerprint"], {"baseline": baseline_final.get("candidate_dataset_fingerprint"), "gen1": gen1_final.get("candidate_dataset_fingerprint"), "gen2": gen2_final.get("candidate_dataset_fingerprint")})
    add_check(checks, "logical_generation_fingerprints_match", gen1_final.get("logical_event_state_dataset_fingerprint") == EXPECTED["gen1_logical_dataset_fingerprint"] and gen2_final.get("logical_event_state_dataset_fingerprint") == EXPECTED["gen2_logical_dataset_fingerprint"], {"gen1": gen1_final.get("logical_event_state_dataset_fingerprint"), "gen2": gen2_final.get("logical_event_state_dataset_fingerprint")})
    add_check(checks, "requested_contexts_15", requested_contexts == EXPECTED["requested_contexts"], requested_contexts)
    add_check(checks, "represented_contexts_14", represented_contexts == EXPECTED["represented_contexts"], represented_contexts)
    add_check(checks, "baseline_origin_rows_8", baseline_origin_rows == EXPECTED["baseline_origin_rows"], baseline_origin_rows)
    add_check(checks, "delta1_origin_rows_3", delta1_origin_rows == EXPECTED["delta1_origin_rows"], delta1_origin_rows)
    add_check(checks, "delta2_origin_rows_3", delta2_origin_rows == EXPECTED["delta2_origin_rows"], delta2_origin_rows)
    add_check(checks, "unavailable_contexts_1", unavailable_contexts == EXPECTED["unavailable_contexts"], unavailable_contexts)
    add_check(checks, "unaccounted_contexts_zero", unaccounted_contexts == 0, unaccounted_contexts)
    add_check(checks, "duplicate_canonical_contexts_zero", duplicate_contexts == 0, duplicate_contexts)
    add_check(checks, "duplicate_event_state_record_ids_zero", duplicate_record_ids == 0, duplicate_record_ids)
    add_check(checks, "missing_parent_refs_zero", missing_parent_refs == 0, missing_parent_refs)
    add_check(checks, "row_identity_mismatches_zero", row_identity_mismatches == 0, row_identity_mismatches)
    add_check(checks, "mandatory_record_lineage_fields_present", mandatory_field_gaps == 0, mandatory_field_gaps)
    add_check(checks, "market_state_dependency_fingerprints_by_generation_match", market_state_dependency_mismatches == 0, {"baseline": EXPECTED["baseline_market_state_fingerprint"], "delta1": EXPECTED["delta1_market_state_fingerprint"], "delta2": EXPECTED["delta2_market_state_fingerprint"], "mismatches": market_state_dependency_mismatches})
    add_check(checks, "unavailable_context_has_no_partial_record", unavailable_key not in gen2_by_key, unavailable_key)
    add_check(checks, "unavailable_context_identity_matches", any(entry.get("expanded_origin_mode") == "unavailable_preserved_from_baseline" and entry.get("session_date") == EXPECTED["unavailable_session_date"] and entry.get("instrument_id") == EXPECTED["unavailable_instrument_id"] and entry.get("blocking_reason") == EXPECTED["unavailable_reason"] for entry in expanded_entries), EXPECTED["unavailable_reason"])
    add_check(checks, "lineage_manifest_parent_and_delta_counts_match", gen2_lineage.get("parent_generation_1_event_state", {}).get("parent_records_reused") == 11 and gen2_lineage.get("market_state_delta_dependency", {}).get("market_state_delta_records_read") == 3 and len(gen2_lineage.get("row_origin_ledger", [])) == 15, gen2_lineage)
    add_check(checks, "semantic_scope_constant", all(row.get("event_state_profile_id") == EXPECTED["event_state_profile_id"] and row.get("event_type_id") == EXPECTED["event_type_id"] and row.get("event_window_definition_id") == EXPECTED["event_window_definition_id"] for row in gen2_records), {"profiles": sorted({row.get("event_state_profile_id") for row in gen2_records}), "event_types": sorted({row.get("event_type_id") for row in gen2_records})})
    add_check(checks, "authority_boundaries_closed", gen2_final.get("official_dataset") is False and gen2_final.get("production") is False and gen2_final.get("downstream") is False, {"official_dataset": gen2_final.get("official_dataset"), "production": gen2_final.get("production"), "downstream": gen2_final.get("downstream")})

    hard_failures = [check["check_id"] for check in checks if check["severity"] == "BLOCKING" and check["status"] != "PASS"]
    approved = not hard_failures
    validation_status = STATUS_PASS if approved else STATUS_FAIL

    generation_chain = [
        {
            "generation": 0,
            "role": "baseline",
            "run_id": BASELINE_RUN_ID,
            "candidate_dataset_fingerprint": EXPECTED["baseline_candidate_dataset_fingerprint"],
            "record_count": len(baseline_records),
            "market_state_candidate_dataset_fingerprint": EXPECTED["baseline_market_state_fingerprint"],
        },
        {
            "generation": 1,
            "role": "incremental_delta_1_and_combined_generation_1",
            "run_id": GEN1_RUN_ID,
            "candidate_dataset_fingerprint": EXPECTED["gen1_candidate_dataset_fingerprint"],
            "logical_event_state_dataset_fingerprint": EXPECTED["gen1_logical_dataset_fingerprint"],
            "record_count": len(gen1_records),
            "delta_origin_rows": delta1_origin_rows,
            "market_state_delta_candidate_dataset_fingerprint": EXPECTED["delta1_market_state_fingerprint"],
        },
        {
            "generation": 2,
            "role": "incremental_delta_2_and_combined_generation_2",
            "run_id": GEN2_RUN_ID,
            "candidate_dataset_fingerprint": EXPECTED["gen2_candidate_dataset_fingerprint"],
            "logical_event_state_dataset_fingerprint": EXPECTED["gen2_logical_dataset_fingerprint"],
            "record_count": len(gen2_records),
            "delta_origin_rows": delta2_origin_rows,
            "market_state_delta_candidate_dataset_fingerprint": EXPECTED["delta2_market_state_fingerprint"],
        },
    ]

    ledger = {
        "validation_id": VALIDATION_ID,
        "validation_run_id": validation_run_id,
        "validation_gate": GATE_ID,
        "source_review_id": SOURCE_REVIEW_ID,
        "source_review_run_id": SOURCE_REVIEW_RUN_ID,
        "generation_chain": generation_chain,
        "counts": {
            "requested_contexts": requested_contexts,
            "represented_contexts": represented_contexts,
            "baseline_origin_rows": baseline_origin_rows,
            "delta1_origin_rows": delta1_origin_rows,
            "delta2_origin_rows": delta2_origin_rows,
            "unavailable_contexts": unavailable_contexts,
            "unaccounted_contexts": unaccounted_contexts,
            "duplicate_canonical_contexts": duplicate_contexts,
            "duplicate_event_state_record_ids": duplicate_record_ids,
            "missing_parent_refs": missing_parent_refs,
            "row_identity_mismatches": row_identity_mismatches,
            "market_state_dependency_mismatches": market_state_dependency_mismatches,
            "mandatory_field_gaps": mandatory_field_gaps,
        },
        "origin_counts": count_by(expanded_entries, "expanded_origin_mode"),
        "entries": expanded_entries,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    ledger["lineage_chain_ledger_sha256"] = sha256_obj({k: v for k, v in ledger.items() if k != "lineage_chain_ledger_sha256"})

    matrix = {
        "validation_id": VALIDATION_ID,
        "validation_run_id": validation_run_id,
        "validation_gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "validation_status": validation_status,
        "source_review_id": SOURCE_REVIEW_ID,
        "source_review_run_id": SOURCE_REVIEW_RUN_ID,
        "decision": {
            "validation_decision": "lineage_chain_validated_with_restrictions" if approved else "blocked_pending_lineage_findings",
            "requested_contexts": requested_contexts,
            "represented_contexts": represented_contexts,
            "baseline_origin_rows": baseline_origin_rows,
            "delta1_origin_rows": delta1_origin_rows,
            "delta2_origin_rows": delta2_origin_rows,
            "unavailable_contexts": unavailable_contexts,
            "unaccounted_contexts": unaccounted_contexts,
            "duplicate_canonical_contexts": duplicate_contexts,
            "missing_parent_refs": missing_parent_refs,
            "row_identity_mismatches": row_identity_mismatches,
            "hard_validation_failures": len(hard_failures),
        },
        "checks": checks,
        "hard_validation_failures": len(hard_failures),
        "hard_validation_failure_ids": hard_failures,
        "evidence": {
            "lineage_chain_ledger_sha256": ledger["lineage_chain_ledger_sha256"],
            "generation_chain": generation_chain,
            "source_review_final_manifest_sha256": sha256_file(SOURCE_REVIEW_RUN / "final_manifest.json"),
            "gen2_final_manifest_sha256": sha256_file(GEN2_RUN / "final_manifest.json"),
            "gen2_records_sha256": sha256_file(GEN2_RUN / "event_state_second_generation_incremental_candidate_records.jsonl"),
            "gen2_lineage_manifest_sha256": sha256_file(GEN2_RUN / "event_state_second_generation_incremental_lineage_manifest.json"),
            "gen1_final_manifest_sha256": sha256_file(GEN1_RUN / "final_manifest.json"),
            "baseline_final_manifest_sha256": sha256_file(BASELINE_RUN / "final_manifest.json"),
        },
        "boundary_counters": {
            "event_state_requests_created": 0,
            "event_state_records_emitted": 0,
            "event_state_materializer_executions": 0,
            "market_state_materializer_executions": 0,
            "source_market_data_rows_read": 0,
            "registry_entry_mutations": 0,
            "datasets_promoted": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "next_allowed_gate": NEXT_GATE if approved else None,
        "validated_at_utc": utc_iso(),
    }

    scope = {
        "scope_id": "event_state_on_demand_incremental_lineage_chain_validation_scope_v0_1",
        "gate": GATE_ID,
        "validation_id": VALIDATION_ID,
        "validation_run_id": validation_run_id,
        "source_review_run_id": SOURCE_REVIEW_RUN_ID,
        "validated_generation_run_ids": [BASELINE_RUN_ID, GEN1_RUN_ID, GEN2_RUN_ID],
        "event_state_profile_id": EXPECTED["event_state_profile_id"],
        "event_type_id": EXPECTED["event_type_id"],
        "event_window_definition_id": EXPECTED["event_window_definition_id"],
        "allowed_inspection": [
            "closed final manifests",
            "closed candidate registry entries",
            "closed validation reports",
            "closed lineage manifests",
            "closed context ledgers",
            "closed candidate records",
        ],
        "event_state_request_creation_authorized": False,
        "event_instance_creation_authorized": False,
        "event_window_binding_creation_authorized": False,
        "instrument_projection_creation_authorized": False,
        "event_state_materialization_authorized": False,
        "market_state_materialization_authorized": False,
        "source_market_data_reads_authorized": False,
        "registry_mutation_authorized": False,
        "official_dataset_promotion_authorized": False,
        "production_authorized": False,
        "downstream_authorized": False,
        "next_allowed_gate": NEXT_GATE if approved else None,
    }
    scope["scope_sha256"] = sha256_obj(scope)

    run_ledger = run_dir / "lineage_ledger.json"
    run_matrix = run_dir / "review_matrix.json"
    run_readout = run_dir / "run_readout.md"
    write_json(run_ledger, ledger)
    write_json(run_matrix, matrix)
    write_text(run_readout, review_readout(matrix))

    root_auth = ROOT / "event_state_on_demand_incremental_lineage_chain_validation_authorization_v0_1.md"
    root_scope = CONFIGS / "event_state_on_demand_incremental_lineage_chain_validation_scope_v0_1.json"
    root_matrix = ROOT / "event_state_on_demand_incremental_lineage_chain_validation_matrix_v0_1.json"
    root_ledger = ROOT / "event_state_on_demand_incremental_lineage_chain_ledger_v0_1.json"
    root_readout = ROOT / "event_state_on_demand_incremental_lineage_chain_validation_readout_v0_1.md"
    write_text(root_auth, authorization_text(validation_run_id))
    write_json(root_scope, scope)
    write_json(root_matrix, matrix)
    write_json(root_ledger, ledger)
    write_text(root_readout, review_readout(matrix))

    final = {
        "run_id": validation_run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "final_run_status": validation_status,
        "started_at_utc": started_at,
        "ended_at_utc": utc_iso(),
        "source_review_run_id": SOURCE_REVIEW_RUN_ID,
        "validated_generation_run_ids": [BASELINE_RUN_ID, GEN1_RUN_ID, GEN2_RUN_ID],
        "lineage_chain_validated": approved,
        "requested_contexts": requested_contexts,
        "represented_contexts": represented_contexts,
        "baseline_origin_rows": baseline_origin_rows,
        "delta1_origin_rows": delta1_origin_rows,
        "delta2_origin_rows": delta2_origin_rows,
        "unavailable_contexts": unavailable_contexts,
        "unaccounted_contexts": unaccounted_contexts,
        "duplicate_canonical_contexts": duplicate_contexts,
        "missing_parent_refs": missing_parent_refs,
        "row_identity_mismatches": row_identity_mismatches,
        "hard_validation_failures": len(hard_failures),
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": NEXT_GATE if approved else None,
        "artifacts": {
            "scope": str(root_scope),
            "authorization": str(root_auth),
            "matrix": str(run_matrix),
            "lineage_ledger": str(run_ledger),
            "readout": str(run_readout),
            "root_matrix": str(root_matrix),
            "root_lineage_ledger": str(root_ledger),
            "root_readout": str(root_readout),
        },
        "artifact_hashes": {
            "scope_sha256": sha256_file(root_scope),
            "matrix_sha256": sha256_file(run_matrix),
            "lineage_ledger_sha256": sha256_file(run_ledger),
            "readout_sha256": sha256_file(run_readout),
        },
    }
    final_path = run_dir / "final_manifest.json"
    write_json(final_path, final)

    print(
        json.dumps(
            {
                "run_id": validation_run_id,
                "status": validation_status,
                "hard_validation_failures": len(hard_failures),
                "requested_contexts": requested_contexts,
                "represented_contexts": represented_contexts,
                "baseline_origin_rows": baseline_origin_rows,
                "delta1_origin_rows": delta1_origin_rows,
                "delta2_origin_rows": delta2_origin_rows,
                "unavailable_contexts": unavailable_contexts,
                "next_allowed_gate": NEXT_GATE if approved else None,
                "final_manifest": str(final_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
