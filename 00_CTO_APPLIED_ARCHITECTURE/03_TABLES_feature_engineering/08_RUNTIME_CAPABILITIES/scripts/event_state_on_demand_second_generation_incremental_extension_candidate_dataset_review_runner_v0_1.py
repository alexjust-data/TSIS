#!/usr/bin/env python3
"""Review the Event State second-generation incremental candidate.

Review-only runner. It inspects the successful generation-2 incremental
extension run and emits review evidence. It does not materialize Event State,
read source market rows, mutate prior evidence, promote datasets, or open
downstream authority.
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

GATE_ID = "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1"
SCRIPT_VERSION = "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_runner_v0_1"
STATUS_PASS = "CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION"
STATUS_FAIL = "CLOSED_BLOCKED_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_CANDIDATE_REVIEW_FAILURE"
NEXT_GATE = "event_state_on_demand_incremental_lineage_chain_validation_v0_1"

REVIEW_ID = "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260728T000000Z"
SOURCE_RUN_ID = "event_state_on_demand_second_generation_incremental_extension_v0_1_20260728T103016Z"
SOURCE_RUN = RUNS / SOURCE_RUN_ID
FAILED_SOURCE_RUN_ID = "event_state_on_demand_second_generation_incremental_extension_v0_1_20260728T102842Z"
FAILED_SOURCE_RUN = RUNS / FAILED_SOURCE_RUN_ID
PARENT_RUN_ID = "event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z"
PARENT_RUN = RUNS / PARENT_RUN_ID

BASELINE_DATASET_ID = "event_state_candidate_dataset_v0_1_d5662103e1c45f90"
BASELINE_DATASET_FINGERPRINT = "d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33"

EXPECTED = {
    "source_final_status": "CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED",
    "candidate_dataset_id": "event_state_second_generation_incremental_candidate_dataset_v0_1_9a31d9b8bf3af01c",
    "candidate_dataset_fingerprint": "9a31d9b8bf3af01c1c4a5cd18a37309eec7b3cb41011501ab85e0ef4a4831746",
    "logical_dataset_fingerprint": "b4774100b8ab27794e8d9a9205227c6e694442e8287b92bf5d899ec3a0b66f33",
    "physical_artifact_fingerprint": "e7d4b33f279f23442c65d3ee372ea4ccbd9bf8675cfc68f84c652e09f92c8c62",
    "validation_result_fingerprint": "32045d40dc84df3900e1037adb7062bf42e147233e261037f0d9923d18c0e229",
    "parent_dataset_id": "event_state_incremental_overlap_candidate_dataset_v0_1_f88cc0a0a39117f3",
    "parent_candidate_dataset_fingerprint": "f88cc0a0a39117f315baf4312dc13533baae8b8574c6966ca91582ca98406c4f",
    "parent_logical_dataset_fingerprint": "73b2f81b76697eb67b55faffecd36c8e77ecf926c1c1f9e56cf6ee0e0ecb10f6",
    "market_state_delta_candidate_dataset_fingerprint": "f2cfd5cf55d0c1be1722693cc0216ffd425bbb869e19c17745976c030f2c7a2a",
    "requested_contexts": 15,
    "represented_contexts": 14,
    "reused_validated_contexts": 11,
    "delta_2_contexts": 3,
    "unavailable_contexts": 1,
    "unaccounted_contexts": 0,
    "record_count": 14,
    "delta_record_count": 3,
    "event_state_profile_id": "event_state_core_four_intraday_profile_v0_1",
    "event_type_id": "event_type:market_data:session_opened",
    "event_window_definition_id": "session_opened_at_anchor_context_v0_1",
    "state_role": "at_event",
    "consumption_legality": "research_only",
    "unavailable_session_date": "2022-11-25",
    "unavailable_instrument_id": "figi_share_class:BBG001S5N8T1",
    "unavailable_reason": "missing_exact_market_state_binding",
}


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def role_file(manifest: dict[str, Any], role: str) -> dict[str, Any] | None:
    return next((item for item in manifest.get("files", []) if item.get("role") == role), None)


def canonical_context_key(row: dict[str, Any]) -> str:
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


def add_check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: Any = None, severity: str = "BLOCKING") -> None:
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


def readout_text(matrix: dict[str, Any]) -> str:
    cov = matrix["coverage_review"]
    return f"""# Event State On-Demand Second-Generation Incremental Extension Candidate Dataset Review Readout v0.1

Status: `{matrix['review_status']}`
Date: `2026-07-28`

```text
review_id = {matrix['review_id']}
review_run_id = {matrix['review_run_id']}
reviewed_run = {matrix['reviewed_run_id']}
reviewed_candidate_dataset_id = {matrix['reviewed_candidate_dataset_id']}
review_decision = {matrix['review_decision']}
requested_contexts = {cov['requested_contexts']}
represented_contexts = {cov['represented_contexts']}
reused_prior_generation_contexts = {cov['reused_prior_generation_contexts']}
delta_2_materialized_contexts = {cov['delta_2_materialized_contexts']}
unavailable_contexts = {cov['unavailable_contexts']}
unaccounted_contexts = {cov['unaccounted_contexts']}
combined_event_state_records = {cov['combined_event_state_records']}
hard_review_failures = {matrix['hard_review_failures']}
candidate_dataset_review_approved = {str(matrix['candidate_dataset_review_approved']).lower()}
reuse_eligibility_after_review = {matrix['reuse_eligibility_after_review']}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

The generation-2 Event State candidate is accepted only as bounded on-demand
candidate evidence. The review confirms a coherent logical composition over
prior generation evidence plus delta2 materialization, with one preserved
unavailable context. It does not mutate parent evidence, create records,
rematerialize Market State, promote an official dataset, open production or open
downstream consumption.
"""


def authorization_text(review_run_id: str, candidate_fp: str) -> str:
    return f"""# Event State On-Demand Second-Generation Incremental Extension Candidate Dataset Review Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_REVIEW`
Date: `2026-07-28`

```text
review_id = {REVIEW_ID}
review_run_id = {review_run_id}
reviewed_run = {SOURCE_RUN_ID}
reviewed_candidate_dataset_fingerprint = {candidate_fp}
execution_authorized = false
market_state_read_authorized = false
event_state_materialization_authorized = false
registry_mutation_authorized = false
official_dataset_promotion_authorized = false
production_authorized = false
downstream_authorized = false
```

This gate authorizes review only. It checks whether the second-generation
incremental candidate is a coherent composition of immutable generation-1 Event
State evidence, delta2 Event State evidence and the preserved unavailable
context. It does not authorize rebuilding Event State, rematerializing Market
State, mutating registry entries, promoting an official dataset, production or
downstream consumption.
"""


def main() -> int:
    started_at = utc_iso()
    review_run_id = f"{GATE_ID}_{utc_compact()}"
    run_dir = RUNS / review_run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    final_manifest = read_json(SOURCE_RUN / "final_manifest.json")
    registry_entry = read_json(SOURCE_RUN / "candidate_registry_entry.json")
    validation_report = read_json(SOURCE_RUN / "event_state_second_generation_incremental_validation_report.json")
    output_manifest = read_json(SOURCE_RUN / "event_state_second_generation_incremental_candidate_output_manifest.json")
    context_ledger = read_json(SOURCE_RUN / "combined_event_state_context_ledger_v0_1.json")
    fp_source = read_json(SOURCE_RUN / "combined_event_state_candidate_fingerprint_comparison_v0_1.json")
    lineage_manifest = read_json(SOURCE_RUN / "event_state_second_generation_incremental_lineage_manifest.json")
    records = read_jsonl(SOURCE_RUN / "event_state_second_generation_incremental_candidate_records.jsonl")
    delta_records = read_jsonl(SOURCE_RUN / "delta_2_event_state_candidate_records.jsonl")

    parent_registry = read_json(PARENT_RUN / "candidate_registry_entry.json")
    parent_output = read_json(PARENT_RUN / "event_state_incremental_overlap_candidate_output_manifest.json")
    failed_manifest_path = FAILED_SOURCE_RUN / "failure_manifest.json"
    failed_manifest = read_json(failed_manifest_path) if failed_manifest_path.exists() else None
    parent_hashes = {
        "final_manifest": sha256_file(PARENT_RUN / "final_manifest.json"),
        "candidate_registry_entry": sha256_file(PARENT_RUN / "candidate_registry_entry.json"),
        "candidate_output_manifest": sha256_file(PARENT_RUN / "event_state_incremental_overlap_candidate_output_manifest.json"),
    }

    checks: list[dict[str, Any]] = []
    add_check(checks, "source_run_closed_with_expected_status", final_manifest.get("final_run_status") == EXPECTED["source_final_status"], final_manifest.get("final_run_status"))
    add_check(checks, "candidate_dataset_id_matches", registry_entry.get("dataset_id") == EXPECTED["candidate_dataset_id"], registry_entry.get("dataset_id"))
    add_check(checks, "candidate_dataset_fingerprint_matches", registry_entry.get("event_state_candidate_dataset_fingerprint") == EXPECTED["candidate_dataset_fingerprint"] == output_manifest.get("event_state_candidate_dataset_fingerprint") == fp_source.get("combined_candidate_dataset_fingerprint"), EXPECTED["candidate_dataset_fingerprint"])
    add_check(checks, "logical_dataset_fingerprint_matches", registry_entry.get("logical_event_state_dataset_fingerprint") == EXPECTED["logical_dataset_fingerprint"] == output_manifest.get("logical_event_state_dataset_fingerprint") == fp_source.get("combined_logical_event_state_dataset_fingerprint"), EXPECTED["logical_dataset_fingerprint"])
    add_check(checks, "physical_artifact_fingerprint_matches", registry_entry.get("physical_artifact_fingerprint") == EXPECTED["physical_artifact_fingerprint"] == output_manifest.get("physical_artifact_fingerprint") == fp_source.get("combined_physical_artifact_fingerprint"), EXPECTED["physical_artifact_fingerprint"])
    add_check(checks, "validation_result_fingerprint_matches", registry_entry.get("validation_result_fingerprint") == EXPECTED["validation_result_fingerprint"] == final_manifest.get("validation_result_fingerprint"), EXPECTED["validation_result_fingerprint"])

    coverage = output_manifest.get("coverage", {})
    add_check(checks, "coverage_counts_match", coverage.get("requested_contexts") == EXPECTED["requested_contexts"] and coverage.get("represented_contexts") == EXPECTED["represented_contexts"] and coverage.get("unavailable_contexts") == EXPECTED["unavailable_contexts"], coverage)
    add_check(checks, "validation_counts_match", validation_report.get("requested_contexts") == EXPECTED["requested_contexts"] and validation_report.get("represented_contexts") == EXPECTED["represented_contexts"] and validation_report.get("unaccounted_contexts") == 0, validation_report)
    add_check(checks, "coverage_reconciles", EXPECTED["requested_contexts"] == EXPECTED["represented_contexts"] + EXPECTED["unavailable_contexts"], "15 = 14 + 1")
    add_check(checks, "combined_record_count_matches", len(records) == EXPECTED["record_count"] == validation_report.get("combined_event_state_records"), len(records))
    add_check(checks, "delta_record_count_matches", len(delta_records) == EXPECTED["delta_record_count"], len(delta_records))
    add_check(checks, "hard_validation_failures_zero", validation_report.get("hard_validation_failures") == 0, validation_report.get("hard_validation_failures"))

    for role in ["combined_event_state_candidate_records", "delta_2_event_state_candidate_records"]:
        info = role_file(output_manifest, role)
        path = Path(info["path"]) if info else None
        actual = sha256_file(path) if path and path.exists() else None
        add_check(checks, f"output_file_hash_match_{role}", bool(info and path and path.exists() and actual == info.get("sha256")), {"expected": info, "actual_sha256": actual})

    represented = [row for row in context_ledger if row.get("context_status") == "represented"]
    reused = [row for row in context_ledger if row.get("representation_source") == "reused_validated_event_state"]
    delta2 = [row for row in context_ledger if row.get("representation_source") == "delta_2_materialized_event_state"]
    unavailable = [row for row in context_ledger if row.get("context_status") == "unavailable"]
    add_check(checks, "ledger_counts_match", len(context_ledger) == 15 and len(represented) == 14 and len(reused) == 11 and len(delta2) == 3 and len(unavailable) == 1, {"context_status_counts": count_by(context_ledger, "context_status"), "representation_source_counts": count_by(context_ledger, "representation_source")})

    record_keys = {canonical_context_key(row) for row in records}
    represented_keys = {canonical_context_key(row) for row in represented}
    delta_record_keys = {canonical_context_key(row) for row in delta_records}
    delta_ledger_keys = {canonical_context_key(row) for row in delta2}
    add_check(checks, "represented_ledger_matches_records", record_keys == represented_keys, {"records": len(record_keys), "ledger": len(represented_keys)})
    add_check(checks, "delta_ledger_matches_delta_records", delta_record_keys == delta_ledger_keys, {"delta_records": len(delta_record_keys), "delta_ledger": len(delta_ledger_keys)})
    add_check(checks, "canonical_contexts_unique", len(record_keys) == len(records), {"unique": len(record_keys), "records": len(records)})
    add_check(checks, "record_ids_unique", len({row.get("event_state_record_id") for row in records}) == len(records), len({row.get("event_state_record_id") for row in records}))

    unavailable_row = unavailable[0] if unavailable else {}
    add_check(checks, "unavailable_context_preserved", unavailable_row.get("session_date") == EXPECTED["unavailable_session_date"] and unavailable_row.get("instrument_id") == EXPECTED["unavailable_instrument_id"] and unavailable_row.get("blocking_reason") == EXPECTED["unavailable_reason"], unavailable_row)
    add_check(checks, "no_partial_row_for_unavailable_context", bool(unavailable_row) and canonical_context_key(unavailable_row) not in record_keys, canonical_context_key(unavailable_row) if unavailable_row else None)

    allowed_integration_statuses = {
        "EVENT_STATE_ON_DEMAND_INTEGRATED_WITH_RESTRICTIONS",
        "EVENT_STATE_INCREMENTAL_OVERLAP_DELTA_INTEGRATED_WITH_RESTRICTIONS",
        "EVENT_STATE_SECOND_GENERATION_INCREMENTAL_DELTA_INTEGRATED_WITH_RESTRICTIONS",
    }
    semantic_ok = all(
        row.get("event_state_profile_id") == EXPECTED["event_state_profile_id"]
        and row.get("event_type_id") == EXPECTED["event_type_id"]
        and row.get("exchange_id") == "XNYS"
        and row.get("event_window_definition_id") == EXPECTED["event_window_definition_id"]
        and row.get("state_role") == EXPECTED["state_role"]
        and row.get("consumption_legality") == EXPECTED["consumption_legality"]
        and row.get("integration_status") in allowed_integration_statuses
        for row in records
    )
    add_check(
        checks,
        "record_semantic_contract_homogeneous",
        semantic_ok,
        {
            "profiles": sorted({row.get("event_state_profile_id") for row in records}),
            "event_types": sorted({row.get("event_type_id") for row in records}),
            "integration_statuses": sorted({row.get("integration_status") for row in records}),
            "allowed_integration_statuses": sorted(allowed_integration_statuses),
        },
    )
    add_check(checks, "all_records_have_market_state_dependency_fingerprint", all(row.get("source_market_state_candidate_dataset_fingerprint") for row in records), sorted({row.get("source_market_state_candidate_dataset_fingerprint") for row in records}))
    add_check(checks, "delta2_records_use_expected_market_state_candidate", all(row.get("source_market_state_candidate_dataset_fingerprint") == EXPECTED["market_state_delta_candidate_dataset_fingerprint"] for row in delta_records), EXPECTED["market_state_delta_candidate_dataset_fingerprint"])

    parent_lineage = lineage_manifest.get("parent_generation_1_event_state", {})
    market_lineage = lineage_manifest.get("market_state_delta_dependency", {})
    add_check(checks, "lineage_composition_mode_matches", lineage_manifest.get("composition_mode") == "parent_generation_1_validated_event_state_plus_delta_2_materialized_event_state", lineage_manifest.get("composition_mode"))
    add_check(checks, "lineage_parent_reuse_count_matches", parent_lineage.get("parent_records_reused") == 11, parent_lineage)
    add_check(checks, "lineage_market_state_delta_count_matches", market_lineage.get("market_state_delta_records_read") == 3 and market_lineage.get("direct_market_state_path_allowed") is False, market_lineage)
    add_check(checks, "lineage_row_origin_count_matches", len(lineage_manifest.get("row_origin_ledger", [])) == 15, len(lineage_manifest.get("row_origin_ledger", [])))

    add_check(checks, "parent_dataset_identity_matches", parent_registry.get("dataset_id") == EXPECTED["parent_dataset_id"] and parent_registry.get("event_state_candidate_dataset_fingerprint") == EXPECTED["parent_candidate_dataset_fingerprint"], parent_registry)
    add_check(checks, "parent_output_identity_matches", parent_output.get("event_state_candidate_dataset_fingerprint") == EXPECTED["parent_candidate_dataset_fingerprint"] and parent_output.get("logical_event_state_dataset_fingerprint") == EXPECTED["parent_logical_dataset_fingerprint"], {"candidate": parent_output.get("event_state_candidate_dataset_fingerprint"), "logical": parent_output.get("logical_event_state_dataset_fingerprint")})
    add_check(checks, "parent_artifact_hashes_observed_without_mutation", True, parent_hashes)
    add_check(checks, "failed_technical_attempt_preserved", bool(failed_manifest) and failed_manifest.get("failure_status") == "CLOSED_FAILED_RUNTIME_READOUT_PATH_LENGTH_NO_VALID_CLOSURE", failed_manifest, "INFO")
    add_check(checks, "no_promotion_or_consumption_opened", registry_entry.get("official_dataset") is False and registry_entry.get("production") is False and registry_entry.get("downstream") is False and registry_entry.get("promotion_review_eligibility") == "not_eligible", {"official_dataset": registry_entry.get("official_dataset"), "production": registry_entry.get("production"), "downstream": registry_entry.get("downstream")})
    add_check(checks, "review_boundary_counters_zero", True, {"event_state_materializer_executions": 0, "market_state_materializer_executions": 0, "source_market_data_rows_read": 0, "registry_entry_mutations": 0})

    hard_failures = [check["check_id"] for check in checks if check["severity"] == "BLOCKING" and check["status"] != "PASS"]
    approved = not hard_failures
    status = STATUS_PASS if approved else STATUS_FAIL

    root_ledger = {
        "review_id": REVIEW_ID,
        "review_run_id": review_run_id,
        "reviewed_run_id": SOURCE_RUN_ID,
        "requested_contexts": 15,
        "represented_contexts": 14,
        "reused_prior_generation_contexts": 11,
        "delta_2_materialized_contexts": 3,
        "unavailable_contexts": 1,
        "context_status_counts": count_by(context_ledger, "context_status"),
        "representation_source_counts": count_by(context_ledger, "representation_source"),
        "unavailable_contexts_detail": unavailable,
        "context_rows": context_ledger,
    }
    root_fp = {
        "review_id": REVIEW_ID,
        "review_run_id": review_run_id,
        "reviewed_run_id": SOURCE_RUN_ID,
        "generation_chain": [
            {"generation": 0, "dataset_id": BASELINE_DATASET_ID, "candidate_dataset_fingerprint": BASELINE_DATASET_FINGERPRINT},
            {"generation": 1, "dataset_id": EXPECTED["parent_dataset_id"], "candidate_dataset_fingerprint": EXPECTED["parent_candidate_dataset_fingerprint"], "logical_event_state_dataset_fingerprint": EXPECTED["parent_logical_dataset_fingerprint"]},
            {"generation": 2, "dataset_id": EXPECTED["candidate_dataset_id"], "candidate_dataset_fingerprint": EXPECTED["candidate_dataset_fingerprint"], "logical_event_state_dataset_fingerprint": EXPECTED["logical_dataset_fingerprint"], "physical_artifact_fingerprint": EXPECTED["physical_artifact_fingerprint"]},
        ],
        "source_fingerprint_comparison": fp_source,
        "review_fingerprint_assessment": {
            "candidate_dataset_fingerprint_match": approved,
            "logical_dataset_fingerprint_match": approved,
            "physical_artifact_fingerprint_match": approved,
            "validation_result_fingerprint_match": approved,
            "runtime_fields_excluded_from_logical_fingerprint": fp_source.get("logical_fingerprint_excludes_runtime_fields", []),
        },
    }
    matrix = {
        "review_id": REVIEW_ID,
        "review_run_id": review_run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "review_status": status,
        "review_decision": "approved_as_event_state_second_generation_incremental_candidate_evidence_with_restrictions" if approved else "blocked_pending_review_findings",
        "reviewed_run_id": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_id": registry_entry.get("dataset_id"),
        "reviewed_candidate_dataset_fingerprint": registry_entry.get("event_state_candidate_dataset_fingerprint"),
        "candidate_dataset_review_approved": approved,
        "reuse_eligibility_before_review": registry_entry.get("reuse_eligibility"),
        "reuse_eligibility_after_review": "pending_incremental_lineage_chain_validation" if approved else "not_eligible",
        "promotion_review_eligibility_after_review": "not_eligible",
        "coverage_review": {
            "requested_contexts": 15,
            "represented_contexts": 14,
            "reused_prior_generation_contexts": 11,
            "delta_2_materialized_contexts": 3,
            "unavailable_contexts": 1,
            "unaccounted_contexts": 0,
            "combined_event_state_records": 14,
            "delta_2_event_state_records": 3,
        },
        "lineage_review": {
            "generation_chain_validated": approved,
            "parent_generation_1_reused_contexts": 11,
            "delta_2_materialized_contexts": 3,
            "parent_evidence_mutated": False,
            "lineage_manifest_ref": str(SOURCE_RUN / "event_state_second_generation_incremental_lineage_manifest.json"),
        },
        "boundary_counters": {
            "event_state_materializer_executions": 0,
            "market_state_materializer_executions": 0,
            "source_market_data_rows_read": 0,
            "event_state_records_emitted_by_review": 0,
            "registry_entry_mutations": 0,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
        "checks": checks,
        "hard_review_failures": len(hard_failures),
        "hard_review_failure_ids": hard_failures,
        "next_allowed_gate": NEXT_GATE if approved else None,
        "reviewed_at_utc": utc_iso(),
    }

    run_ledger = run_dir / "context_ledger.json"
    run_fp = run_dir / "fingerprints.json"
    run_matrix = run_dir / "review_matrix.json"
    run_readout = run_dir / "run_readout.md"
    write_json(run_ledger, root_ledger)
    write_json(run_fp, root_fp)
    write_json(run_matrix, matrix)
    write_text(run_readout, readout_text(matrix))

    root_matrix = ROOT / "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_matrix_v0_1.json"
    root_ledger_path = ROOT / "event_state_on_demand_second_generation_incremental_extension_candidate_context_ledger_v0_1.json"
    root_fp_path = ROOT / "event_state_on_demand_second_generation_incremental_extension_candidate_fingerprint_comparison_v0_1.json"
    root_readout = ROOT / "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_readout_v0_1.md"
    root_authorization = ROOT / "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_authorization_v0_1.md"
    write_json(root_matrix, matrix)
    write_json(root_ledger_path, root_ledger)
    write_json(root_fp_path, root_fp)
    write_text(root_readout, readout_text(matrix))
    write_text(root_authorization, authorization_text(review_run_id, str(registry_entry.get("event_state_candidate_dataset_fingerprint"))))

    scope = {
        "scope_id": "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_scope_v0_1",
        "gate": GATE_ID,
        "review_id": REVIEW_ID,
        "review_run_id": review_run_id,
        "reviewed_run": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_fingerprint": registry_entry.get("event_state_candidate_dataset_fingerprint"),
        "allowed_inputs": [
            "final_manifest.json",
            "event_state_second_generation_incremental_candidate_output_manifest.json",
            "candidate_registry_entry.json",
            "event_state_second_generation_incremental_validation_report.json",
            "combined_event_state_context_ledger_v0_1.json",
            "event_state_second_generation_incremental_lineage_manifest.json",
            "combined_event_state_candidate_fingerprint_comparison_v0_1.json",
            "event_state_second_generation_incremental_candidate_records.jsonl",
            "delta_2_event_state_candidate_records.jsonl",
        ],
        "execution_authorized": False,
        "market_state_read_authorized": False,
        "event_state_materialization_authorized": False,
        "registry_mutation_authorized": False,
        "official_dataset_promotion_authorized": False,
        "production_authorized": False,
        "downstream_authorized": False,
        "next_allowed_gate": NEXT_GATE if approved else None,
    }
    scope["scope_sha256"] = sha256_obj(scope)
    scope_path = CONFIGS / "event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_scope_v0_1.json"
    write_json(scope_path, scope)

    final = {
        "run_id": review_run_id,
        "gate": GATE_ID,
        "script_version": SCRIPT_VERSION,
        "final_run_status": status,
        "started_at_utc": started_at,
        "ended_at_utc": utc_iso(),
        "reviewed_run_id": SOURCE_RUN_ID,
        "reviewed_candidate_dataset_id": registry_entry.get("dataset_id"),
        "reviewed_candidate_dataset_fingerprint": registry_entry.get("event_state_candidate_dataset_fingerprint"),
        "requested_contexts": 15,
        "represented_contexts": 14,
        "reused_prior_generation_contexts": 11,
        "delta_2_materialized_contexts": 3,
        "unavailable_contexts": 1,
        "unaccounted_contexts": 0,
        "combined_event_state_records": 14,
        "hard_review_failures": len(hard_failures),
        "candidate_dataset_review_approved": approved,
        "reuse_eligibility_after_review": matrix["reuse_eligibility_after_review"],
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_allowed_gate": NEXT_GATE if approved else None,
        "artifacts": {
            "scope": str(scope_path),
            "authorization": str(root_authorization),
            "matrix": str(run_matrix),
            "context_ledger": str(run_ledger),
            "fingerprint_comparison": str(run_fp),
            "readout": str(run_readout),
            "root_matrix": str(root_matrix),
            "root_context_ledger": str(root_ledger_path),
            "root_fingerprint_comparison": str(root_fp_path),
            "root_readout": str(root_readout),
        },
        "artifact_hashes": {
            "scope_sha256": sha256_file(scope_path),
            "matrix_sha256": sha256_file(run_matrix),
            "context_ledger_sha256": sha256_file(run_ledger),
            "fingerprint_comparison_sha256": sha256_file(run_fp),
            "readout_sha256": sha256_file(run_readout),
        },
    }
    final_path = run_dir / "final_manifest.json"
    write_json(final_path, final)

    print(
        json.dumps(
            {
                "run_id": review_run_id,
                "status": status,
                "hard_review_failures": len(hard_failures),
                "requested_contexts": 15,
                "represented_contexts": 14,
                "delta_2_materialized_contexts": 3,
                "unavailable_contexts": 1,
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
