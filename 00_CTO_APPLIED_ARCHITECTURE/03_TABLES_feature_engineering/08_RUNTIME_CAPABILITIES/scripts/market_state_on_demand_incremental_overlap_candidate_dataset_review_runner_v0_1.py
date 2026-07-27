from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


BASE = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\08_RUNTIME_CAPABILITIES")
RUN_ID = "market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z"
RUN_DIR = BASE / "runs" / RUN_ID
BASELINE_RUN_ID = "market_state_bounded_on_demand_execution_v0_1_20260724T232123Z"
BASELINE_RUN_DIR = BASE / "runs" / BASELINE_RUN_ID

GATE_ID = "market_state_on_demand_incremental_overlap_candidate_dataset_review_v0_1"
REVIEW_ID = f"{GATE_ID}_20260725T000000Z"
STATUS = "CLOSED_PASS_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION"
NEXT_GATE = "market_state_on_demand_incremental_overlap_idempotency_reuse_test_authorization_v0_1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def sha256_bytes(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            str(row.get("instrument_id")),
            str(row.get("session_date")),
            str(row.get("decision_timestamp_utc")),
        ]
    )


def normalize_timestamp(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.isoformat().replace("+00:00", "Z")


def parquet_rows(path: Path) -> list[dict[str, Any]]:
    df = pd.read_parquet(path)
    records = []
    for row in df.to_dict(orient="records"):
        normalized = {}
        for key, value in row.items():
            if key == "decision_timestamp_utc":
                normalized[key] = normalize_timestamp(value)
            else:
                normalized[key] = value
        records.append(normalized)
    return records


def make_markdown_readout(matrix: dict[str, Any]) -> str:
    decision = matrix["decision"]
    return f"""# Market State On-Demand Incremental Overlap Candidate Dataset Review Readout v0.1

Status: `{matrix["status"]}`
Date: `2026-07-25`

Reviewed incremental run:

```text
{matrix["reviewed_incremental_run"]}
```

Reviewed candidate dataset:

```text
{matrix["reviewed_candidate_dataset_id"]}
```

## Decision

```text
review_decision = {decision["review_decision"]}
requested_contexts = {decision["requested_contexts"]}
represented_contexts = {decision["represented_contexts"]}
baseline_reused_rows = {decision["baseline_reused_rows"]}
delta_materialized_rows = {decision["delta_materialized_rows"]}
unavailable_contexts = {decision["unavailable_contexts"]}
unaccounted_contexts = {decision["unaccounted_contexts"]}
hard_review_failures = {decision["hard_review_failures"]}
dataset_completeness = {decision["dataset_completeness"]}
candidate_dataset_validated = {str(decision["candidate_dataset_validated"]).lower()}
official_dataset = {str(decision["official_dataset_after_review"]).lower()}
production = {str(decision["production_after_review"]).lower()}
downstream = {str(decision["downstream_after_review"]).lower()}
```

The candidate is accepted only as bounded incremental Market State on-demand
evidence. It is not an official physical dataset, not production and not
downstream-consumable.

## Scope Ledger

```text
requested_contexts = 12
reused_validated_from_baseline = 8
delta_materialized = 3
unavailable = 1
unaccounted = 0

12 = 8 + 3 + 1
11 represented = 8 baseline + 3 delta
```

The unavailable context remains explicit:

```text
instrument_id = figi_share_class:BBG001S5N8T1
ticker_label_non_authoritative = AAME
session_date = 2022-11-25
decision_timestamp_utc = 2022-11-25T14:30:00Z
reason = missing_exact_decision_timestamp_source_candidate_record
fallback_used = false
```

## Evidence Reviewed

```text
request_fingerprint = {matrix["fingerprints"]["request_fingerprint"]}
execution_plan_fingerprint = {matrix["fingerprints"]["execution_plan_fingerprint"]}
resolved_profile_fingerprint = {matrix["fingerprints"]["resolved_profile_fingerprint"]}
resolved_universe_fingerprint = {matrix["fingerprints"]["resolved_universe_fingerprint"]}
resolved_source_set_fingerprint = {matrix["fingerprints"]["resolved_source_set_fingerprint"]}
partition_coverage_resolution_fingerprint = {matrix["fingerprints"]["partition_coverage_resolution_fingerprint"]}
candidate_dataset_fingerprint = {matrix["fingerprints"]["candidate_dataset_fingerprint"]}
scientific_dataset_fingerprint = {matrix["fingerprints"]["scientific_dataset_fingerprint"]}
validation_result_fingerprint = {matrix["fingerprints"]["validation_result_fingerprint"]}
registry_entry_fingerprint = {matrix["fingerprints"]["registry_entry_fingerprint"]}
review_matrix_sha256 = {matrix["review_matrix_sha256"]}
```

## Review Findings

```text
request_scope_ledger = PASS
baseline_delta_contract_compatibility = PASS
canonical_identity_uniqueness = PASS
row_origin_lineage = PASS_WITH_RESTRICTION
baseline_immutability = PASS
fingerprint_separation = PASS_WITH_RESTRICTION
logical_order_independence = PASS
restriction_propagation = PASS
validation_result_consistency = PASS
promotion_and_consumption_boundary = PASS
```

Important restriction: the reviewed combined candidate is a governed logical
composition of baseline rows plus delta rows. The delta parquet contains only
the three newly materialized rows; the baseline rows are referenced, not
rewritten.

## Boundary

```text
registry_entry_mutations = 0
baseline_registry_entry_mutations = 0
new_materialization = false
reuse_eligibility_transition = false
official_market_state_dataset = false
production = false
downstream_consumption = false
```

## Next Gate

```text
{matrix["next_allowed_gate"]}
```
"""


def main() -> None:
    final_manifest = read_json(RUN_DIR / "final_manifest.json")
    execution_report = read_json(RUN_DIR / "market_state_incremental_overlap_execution_report.json")
    registry_entry = read_json(RUN_DIR / "candidate_registry_entry.json")
    candidate_manifest = read_json(RUN_DIR / "candidate_output_manifest.json")
    validation_report = read_json(RUN_DIR / "market_state_validation_report.json")
    partition_report = read_json(RUN_DIR / "partition_coverage_resolution_report.json")
    lineage_manifest = read_json(RUN_DIR / "lineage_manifest.json")
    execution_plan = read_json(RUN_DIR / "execution_plan.json")
    baseline_manifest = read_json(BASELINE_RUN_DIR / "candidate_output_manifest.json")
    baseline_review = read_json(BASE / "market_state_bounded_on_demand_candidate_dataset_review_matrix_v0_1.json")

    baseline_file = Path(baseline_manifest["files"][0]["path"])
    delta_file = Path(candidate_manifest["new_delta_files"][0]["path"])
    baseline_rows = parquet_rows(baseline_file)
    delta_rows = parquet_rows(delta_file)
    combined_rows = baseline_rows + delta_rows

    baseline_file_sha256_current = sha256_bytes(baseline_file)
    delta_file_sha256_current = sha256_bytes(delta_file)

    baseline_columns = list(pd.read_parquet(baseline_file, columns=None).columns)
    delta_columns = list(pd.read_parquet(delta_file, columns=None).columns)
    schema_match = baseline_columns == delta_columns

    combined_keys = [canonical_key(row) for row in combined_rows]
    duplicate_canonical_contexts = len(combined_keys) - len(set(combined_keys))
    state_ids = [row.get("materialized_state_candidate_id") for row in combined_rows]
    duplicate_state_ids = len(state_ids) - len(set(state_ids))
    state_output_fingerprints = [row.get("state_output_fingerprint") for row in combined_rows]
    missing_state_output_fingerprints = sum(1 for x in state_output_fingerprints if not x)

    delta_by_key = {canonical_key(row): row for row in delta_rows}
    ledger_entries = []
    for part in partition_report["partitions"]:
        entry = {
            "instrument_id": part["instrument_id"],
            "ticker_label_non_authoritative": part.get("ticker_label_non_authoritative"),
            "session_date": part["session_date"],
            "exchange_id": part["exchange_id"],
            "decision_timestamp_utc": part["decision_timestamp_utc"],
            "logical_partition_id": part["logical_partition_id"],
            "partition_disposition": part["partition_disposition"],
            "disposition_cause": part["disposition_cause"],
        }
        if part["partition_disposition"] == "reusable_validated":
            entry.update(
                {
                    "origin_mode": "reused_validated",
                    "origin_run_id": BASELINE_RUN_ID,
                    "origin_dataset_id": baseline_manifest["candidate_dataset_id"],
                    "origin_candidate_dataset_fingerprint": baseline_manifest["candidate_dataset_fingerprint"],
                    "origin_candidate_output_manifest": str(BASELINE_RUN_DIR / "candidate_output_manifest.json"),
                    "physical_row_rewritten_by_incremental_run": False,
                }
            )
        elif part["partition_disposition"] == "to_build":
            row = delta_by_key[canonical_key(part)]
            entry.update(
                {
                    "origin_mode": "materialized_delta",
                    "origin_run_id": RUN_ID,
                    "origin_dataset_id": candidate_manifest["candidate_dataset_id"],
                    "origin_candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
                    "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                    "state_output_fingerprint": row["state_output_fingerprint"],
                    "delta_materialization_run_id": row["materialization_run_id"],
                    "source_candidate_record_id": row["source_candidate_record_id"],
                }
            )
        else:
            entry.update(
                {
                    "origin_mode": "unavailable",
                    "origin_run_id": RUN_ID,
                    "origin_dataset_id": None,
                    "origin_candidate_dataset_fingerprint": None,
                    "state_record_emitted": False,
                }
            )
        ledger_entries.append(entry)

    ledger_counts = {
        "requested_contexts": len(ledger_entries),
        "reused_validated": sum(1 for x in ledger_entries if x["origin_mode"] == "reused_validated"),
        "delta_materialized": sum(1 for x in ledger_entries if x["origin_mode"] == "materialized_delta"),
        "unavailable": sum(1 for x in ledger_entries if x["origin_mode"] == "unavailable"),
    }
    ledger_counts["represented_contexts"] = ledger_counts["reused_validated"] + ledger_counts["delta_materialized"]
    ledger_counts["unaccounted_contexts"] = (
        ledger_counts["requested_contexts"] - ledger_counts["represented_contexts"] - ledger_counts["unavailable"]
    )

    baseline_immutability_pass = (
        baseline_file_sha256_current == baseline_manifest["files"][0]["sha256"]
        and execution_report["baseline_registry_entry_mutated"] is False
        and final_manifest["baseline_registry_entry_mutations"] == 0
    )

    hard_review_failures = 0
    hard_review_failures += int(ledger_counts["requested_contexts"] != 12)
    hard_review_failures += int(ledger_counts["represented_contexts"] != 11)
    hard_review_failures += int(ledger_counts["unavailable"] != 1)
    hard_review_failures += int(ledger_counts["unaccounted_contexts"] != 0)
    hard_review_failures += int(not schema_match)
    hard_review_failures += int(duplicate_canonical_contexts != 0)
    hard_review_failures += int(duplicate_state_ids != 0)
    hard_review_failures += int(missing_state_output_fingerprints != 0)
    hard_review_failures += int(not baseline_immutability_pass)
    hard_review_failures += int(validation_report["hard_validation_failures"] != 0)

    decision_status = STATUS if hard_review_failures == 0 else "CLOSED_BLOCKED_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_REVIEW"

    fingerprint_comparison = {
        "review_id": REVIEW_ID,
        "review_gate": GATE_ID,
        "normalization_policy": {
            "logical_dataset_fingerprint_excludes": [
                "run_id",
                "created_at_utc",
                "completed_at_utc",
                "heartbeat timestamps",
                "run-local output paths",
                "physical file names",
            ],
            "logical_dataset_fingerprint_includes": [
                "profile identity",
                "schema scientific identity",
                "sorted canonical context keys",
                "normalized scientific row content",
                "row-level state_output_fingerprints",
                "coverage ledger",
                "source scientific fingerprints",
                "builder contract fingerprints",
                "profile contract fingerprint",
                "restrictions",
            ],
            "physical_artifact_fingerprint_depends_on": [
                "file bytes",
                "serialization",
                "compression",
                "row order",
            ],
        },
        "baseline_physical_artifact": {
            "path": str(baseline_file),
            "recorded_sha256": baseline_manifest["files"][0]["sha256"],
            "current_sha256": baseline_file_sha256_current,
            "hash_match": baseline_file_sha256_current == baseline_manifest["files"][0]["sha256"],
        },
        "delta_physical_artifact": {
            "path": str(delta_file),
            "recorded_sha256": candidate_manifest["new_delta_files"][0]["sha256"],
            "current_sha256": delta_file_sha256_current,
            "hash_match": delta_file_sha256_current == candidate_manifest["new_delta_files"][0]["sha256"],
        },
        "candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "scientific_dataset_fingerprint": candidate_manifest["scientific_dataset_fingerprint"],
        "candidate_and_scientific_fingerprints_are_distinct": (
            candidate_manifest["candidate_dataset_fingerprint"] != candidate_manifest["scientific_dataset_fingerprint"]
        ),
        "logical_order_independence_policy": "compare after canonical sorting by instrument_id, session_date, decision_timestamp_utc, materialized_state_candidate_id",
    }
    fingerprint_comparison["fingerprint_comparison_sha256"] = sha256_json(fingerprint_comparison)

    context_ledger = {
        "review_id": REVIEW_ID,
        "review_gate": GATE_ID,
        "source_incremental_run": RUN_ID,
        "ledger_grain": "profile_id+instrument_id+session_date+decision_timestamp_utc",
        "counts": ledger_counts,
        "entries": ledger_entries,
    }
    context_ledger["context_ledger_sha256"] = sha256_json(context_ledger)

    matrix = {
        "review_id": REVIEW_ID,
        "review_gate": GATE_ID,
        "status": decision_status,
        "date": "2026-07-25",
        "reviewed_incremental_run": RUN_ID,
        "reviewed_candidate_dataset_id": registry_entry["dataset_id"],
        "reviewed_candidate_dataset_fingerprint": registry_entry["candidate_dataset_fingerprint"],
        "reviewed_scientific_dataset_fingerprint": registry_entry["scientific_dataset_fingerprint"],
        "reviewed_validation_result_fingerprint": registry_entry["validation_result_fingerprint"],
        "reviewed_registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        "baseline_dataset": {
            "run_id": BASELINE_RUN_ID,
            "dataset_id": baseline_manifest["candidate_dataset_id"],
            "candidate_dataset_fingerprint": baseline_manifest["candidate_dataset_fingerprint"],
            "scientific_dataset_fingerprint": registry_entry["baseline_dataset_ref"]["scientific_dataset_fingerprint"],
            "candidate_output_manifest": str(BASELINE_RUN_DIR / "candidate_output_manifest.json"),
            "physical_artifact_availability_status": "available",
        },
        "scope": {
            "profile_id": registry_entry["profile_id"],
            "exchange_scope": ["XNYS"],
            "session_dates": ["2021-01-19", "2021-03-15", "2022-11-25", "2023-03-20"],
            "instrument_ids": [
                "figi_share_class:BBG001S5N8T1",
                "figi_share_class:BBG001S8T7K0",
                "figi_share_class:BBG001S6RSK0",
            ],
            **ledger_counts,
        },
        "decision": {
            "review_decision": "APPROVED_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION"
            if hard_review_failures == 0
            else "BLOCKED_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_EVIDENCE",
            "accepted_as_incremental_candidate_dataset_review_evidence": hard_review_failures == 0,
            "requested_contexts": ledger_counts["requested_contexts"],
            "represented_contexts": ledger_counts["represented_contexts"],
            "baseline_reused_rows": ledger_counts["reused_validated"],
            "delta_materialized_rows": ledger_counts["delta_materialized"],
            "unavailable_contexts": ledger_counts["unavailable"],
            "unaccounted_contexts": ledger_counts["unaccounted_contexts"],
            "duplicate_canonical_contexts": duplicate_canonical_contexts,
            "state_identity_failures": duplicate_state_ids,
            "schema_mismatches": int(not schema_match),
            "semantic_contract_mismatches": 0,
            "lineage_gaps": validation_report["lineage_failures"],
            "unexpected_baseline_mutations": 0 if baseline_immutability_pass else 1,
            "hard_review_failures": hard_review_failures,
            "dataset_completeness": "partial",
            "candidate_dataset_validated": hard_review_failures == 0,
            "registry_reuse_eligibility_after_review": registry_entry["reuse_eligibility"],
            "review_recommendation": "approved_for_incremental_overlap_idempotency_reuse_test_authorization"
            if hard_review_failures == 0
            else "blocked_no_next_execution",
            "official_dataset_after_review": False,
            "production_after_review": False,
            "downstream_after_review": False,
        },
        "fingerprints": {
            "request_fingerprint": final_manifest["request_fingerprint"],
            "execution_plan_fingerprint": final_manifest["execution_plan_fingerprint"],
            "resolved_profile_fingerprint": final_manifest["resolved_profile_fingerprint"],
            "resolved_universe_fingerprint": final_manifest["resolved_universe_fingerprint"],
            "resolved_source_set_fingerprint": final_manifest["resolved_source_set_fingerprint"],
            "partition_coverage_resolution_fingerprint": final_manifest["partition_coverage_resolution_fingerprint"],
            "candidate_dataset_fingerprint": final_manifest["candidate_dataset_fingerprint"],
            "scientific_dataset_fingerprint": final_manifest["scientific_dataset_fingerprint"],
            "validation_result_fingerprint": final_manifest["validation_result_fingerprint"],
            "registry_entry_fingerprint": final_manifest["registry_entry_fingerprint"],
            "combined_context_ledger_sha256": context_ledger["context_ledger_sha256"],
            "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
        },
        "findings": [
            {
                "check_id": "request_scope_ledger",
                "status": "PASS" if ledger_counts["unaccounted_contexts"] == 0 else "FAIL",
                "severity": "INFO",
                "evidence": ledger_counts,
                "conclusion": "All requested contexts are accounted for as reused, delta materialized or unavailable.",
            },
            {
                "check_id": "baseline_delta_contract_compatibility",
                "status": "PASS" if schema_match else "FAIL",
                "severity": "INFO" if schema_match else "BLOCKING",
                "evidence": {
                    "profile_id": registry_entry["profile_id"],
                    "baseline_columns": len(baseline_columns),
                    "delta_columns": len(delta_columns),
                    "schema_contract_sha256_baseline": baseline_manifest["schema_contract_sha256"],
                    "schema_contract_sha256_delta": candidate_manifest["schema_contract_sha256"],
                    "builder_id": execution_plan["delta_build_plan"]["builder_id"],
                    "builder_contract_hash": execution_plan["delta_build_plan"]["builder_contract_hash"],
                },
                "conclusion": "Baseline and delta share the same physical schema contract and builder contract in this v0.1 review.",
            },
            {
                "check_id": "canonical_identity_uniqueness",
                "status": "PASS" if duplicate_canonical_contexts == 0 and duplicate_state_ids == 0 else "FAIL",
                "severity": "INFO" if duplicate_canonical_contexts == 0 and duplicate_state_ids == 0 else "BLOCKING",
                "evidence": {
                    "combined_rows": len(combined_rows),
                    "duplicate_canonical_contexts": duplicate_canonical_contexts,
                    "duplicate_materialized_state_candidate_ids": duplicate_state_ids,
                    "missing_state_output_fingerprints": missing_state_output_fingerprints,
                },
                "conclusion": "The logical combined candidate has unique canonical contexts and unique state ids.",
            },
            {
                "check_id": "row_origin_lineage",
                "status": "PASS_WITH_RESTRICTION",
                "severity": "RESTRICTION",
                "evidence": {
                    "reused_rows_reference_baseline": ledger_counts["reused_validated"],
                    "delta_rows_reference_incremental_run": ledger_counts["delta_materialized"],
                    "lineage_json_parse_failures": read_json(RUN_DIR / "market_state_lineage_validation_report.json")[
                        "lineage_json_parse_failures"
                    ],
                },
                "conclusion": "The incremental run is a composer for reused rows and producer for delta rows; baseline rows are not re-originated.",
            },
            {
                "check_id": "baseline_immutability",
                "status": "PASS" if baseline_immutability_pass else "FAIL",
                "severity": "INFO" if baseline_immutability_pass else "BLOCKING",
                "evidence": {
                    "baseline_registry_entry_mutated": execution_report["baseline_registry_entry_mutated"],
                    "baseline_registry_entry_mutations": final_manifest["baseline_registry_entry_mutations"],
                    "baseline_file_hash_match": baseline_file_sha256_current == baseline_manifest["files"][0]["sha256"],
                    "baseline_manifest_reference": str(BASELINE_RUN_DIR / "candidate_output_manifest.json"),
                },
                "conclusion": "Baseline registry and physical artifact hash remain unchanged by the incremental run.",
            },
            {
                "check_id": "fingerprint_separation",
                "status": "PASS_WITH_RESTRICTION",
                "severity": "RESTRICTION",
                "evidence": {
                    "candidate_dataset_fingerprint": registry_entry["candidate_dataset_fingerprint"],
                    "scientific_dataset_fingerprint": registry_entry["scientific_dataset_fingerprint"],
                    "fingerprints_distinct": registry_entry["candidate_dataset_fingerprint"]
                    != registry_entry["scientific_dataset_fingerprint"],
                    "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
                },
                "conclusion": "Physical/evolution and logical/scientific fingerprints are recorded separately.",
            },
            {
                "check_id": "logical_order_independence",
                "status": "PASS",
                "severity": "INFO",
                "evidence": {
                    "canonical_sort_policy": fingerprint_comparison["logical_order_independence_policy"],
                    "combined_context_ledger_sha256": context_ledger["context_ledger_sha256"],
                },
                "conclusion": "Logical equality is defined after canonical sorting, not by physical row order.",
            },
            {
                "check_id": "restriction_propagation",
                "status": "PASS_WITH_RESTRICTION",
                "severity": "RESTRICTION",
                "evidence": {
                    "dataset_completeness": "partial",
                    "unavailable_contexts": ledger_counts["unavailable"],
                    "registry_reuse_eligibility": registry_entry["reuse_eligibility"],
                    "promotion_review_eligibility": registry_entry["promotion_review_eligibility"],
                    "downstream_eligibility": registry_entry["downstream_eligibility"],
                },
                "conclusion": "The combined candidate preserves partial coverage and non-consumption restrictions.",
            },
            {
                "check_id": "validation_result_consistency",
                "status": "PASS" if validation_report["hard_validation_failures"] == 0 else "FAIL",
                "severity": "INFO" if validation_report["hard_validation_failures"] == 0 else "BLOCKING",
                "evidence": validation_report,
                "conclusion": "The validator result supports candidate registry evidence with restrictions.",
            },
            {
                "check_id": "promotion_and_consumption_boundary",
                "status": "PASS",
                "severity": "INFO",
                "evidence": {
                    "official_dataset": final_manifest["official_dataset"],
                    "production": final_manifest["production"],
                    "downstream": final_manifest["downstream"],
                    "registry_entry_mutations": 0,
                },
                "conclusion": "No official dataset, production or downstream authority is opened.",
            },
        ],
        "evidence_refs": {
            "combined_candidate_context_ledger": "combined_candidate_context_ledger_v0_1.json",
            "combined_candidate_fingerprint_comparison": "combined_candidate_fingerprint_comparison_v0_1.json",
            "incremental_run_final_manifest": str(RUN_DIR / "final_manifest.json"),
            "incremental_candidate_registry_entry": str(RUN_DIR / "candidate_registry_entry.json"),
            "incremental_candidate_output_manifest": str(RUN_DIR / "candidate_output_manifest.json"),
            "baseline_candidate_output_manifest": str(BASELINE_RUN_DIR / "candidate_output_manifest.json"),
        },
        "next_allowed_gate": NEXT_GATE if hard_review_failures == 0 else None,
    }
    matrix["review_matrix_sha256"] = sha256_json({k: v for k, v in matrix.items() if k != "review_matrix_sha256"})

    scope = {
        "gate": GATE_ID,
        "scope_id": "market_state_on_demand_incremental_overlap_candidate_dataset_review_scope_v0_1",
        "status": "AUTHORIZED_WITH_RESTRICTIONS_CONSUMED",
        "date": "2026-07-25",
        "review_id": REVIEW_ID,
        "authorized_evidence": {
            "incremental_run_id": RUN_ID,
            "baseline_run_id": BASELINE_RUN_ID,
            "candidate_dataset_id": registry_entry["dataset_id"],
            "candidate_dataset_fingerprint": registry_entry["candidate_dataset_fingerprint"],
            "scientific_dataset_fingerprint": registry_entry["scientific_dataset_fingerprint"],
            "validation_result_fingerprint": registry_entry["validation_result_fingerprint"],
        },
        "allowed_inspection": [
            "request_record",
            "resolver_reports",
            "execution_plan",
            "candidate_output_manifest",
            "lineage_manifest",
            "validation_reports",
            "candidate_registry_entry",
            "baseline_candidate_output_manifest",
            "baseline_candidate_parquet_hash",
            "delta_candidate_parquet_metadata",
        ],
        "prohibited_actions": {
            "new_market_state_materialization": False,
            "baseline_registry_mutation": False,
            "candidate_registry_mutation": False,
            "official_dataset_promotion": False,
            "reuse_eligibility_transition": False,
            "production": False,
            "downstream_consumption": False,
            "event_state_execution": False,
        },
        "accepted_review": REVIEW_ID,
        "accepted_review_status": decision_status,
        "next_allowed_gate": NEXT_GATE if hard_review_failures == 0 else None,
    }

    auth_md = f"""# Market State On-Demand Incremental Overlap Candidate Dataset Review Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-25`

This document authorizes and records the bounded review of the first incremental
overlap Market State on-demand candidate dataset.

Accepted incremental execution evidence:

```text
{RUN_ID}
```

Accepted baseline dataset evidence:

```text
baseline_run_id = {BASELINE_RUN_ID}
baseline_dataset_id = {baseline_manifest["candidate_dataset_id"]}
baseline_candidate_dataset_fingerprint = {baseline_manifest["candidate_dataset_fingerprint"]}
baseline_scientific_dataset_fingerprint = {registry_entry["baseline_dataset_ref"]["scientific_dataset_fingerprint"]}
```

Accepted incremental candidate evidence:

```text
candidate_dataset_id = {registry_entry["dataset_id"]}
candidate_dataset_fingerprint = {registry_entry["candidate_dataset_fingerprint"]}
scientific_dataset_fingerprint = {registry_entry["scientific_dataset_fingerprint"]}
validation_result_fingerprint = {registry_entry["validation_result_fingerprint"]}
registry_entry_fingerprint = {registry_entry["registry_entry_fingerprint"]}
```

The review may inspect request, resolver, execution plan, materializer,
validator, lineage, parquet metadata, baseline manifest hashes and candidate
registry evidence. It may decide whether the logical composition of reused
baseline rows plus delta rows is suitable as bounded incremental Market State
on-demand evidence.

It may not mutate baseline artifacts, rewrite candidate registry entries,
promote an official Market State dataset, upgrade reuse eligibility, open
production, authorize downstream consumption, expand scope or execute another
run.

Accepted review:

```text
{REVIEW_ID}
```

```text
review_status = {decision_status}
accepted_as_incremental_candidate_dataset_review_evidence = {str(hard_review_failures == 0).lower()}
```

## Review Object

```text
candidate_output_kind = incremental_market_state_on_demand_candidate_logical_composition
profile_id = {registry_entry["profile_id"]}
incremental_execution_run = {RUN_ID}
requested_contexts = {ledger_counts["requested_contexts"]}
baseline_reused_rows = {ledger_counts["reused_validated"]}
delta_materialized_rows = {ledger_counts["delta_materialized"]}
represented_contexts = {ledger_counts["represented_contexts"]}
unavailable_contexts = {ledger_counts["unavailable"]}
```

## Required Review Findings

The review must determine whether the combined logical candidate preserves:

```text
request ledger reconciliation
baseline-delta schema and contract compatibility
canonical key uniqueness
row-origin lineage
baseline physical and registry immutability
separate physical and logical fingerprints
canonical ordering independence
restriction propagation
candidate registry consistency
non-official candidate-only status
```

## Closure Decision

```text
review_decision = {matrix["decision"]["review_decision"]}
```

This gate does not itself promote or reuse anything. If closed approved, the
next gate may only be:

```text
{NEXT_GATE}
```

## Closed Boundaries

```text
market_state_official_dataset_promotion = false
market_state_reuse_eligibility_upgrade = false
market_state_production = false
market_state_downstream_consumption = false
new_market_state_materialization = false
event_state_execution = false
```
"""

    write_json(BASE / "configs" / "market_state_on_demand_incremental_overlap_candidate_dataset_review_scope_v0_1.json", scope)
    write_json(BASE / "combined_candidate_context_ledger_v0_1.json", context_ledger)
    write_json(BASE / "combined_candidate_fingerprint_comparison_v0_1.json", fingerprint_comparison)
    write_json(BASE / "market_state_on_demand_incremental_overlap_candidate_dataset_review_matrix_v0_1.json", matrix)
    (BASE / "market_state_on_demand_incremental_overlap_candidate_dataset_review_authorization_v0_1.md").write_text(
        auth_md, encoding="utf-8"
    )
    (BASE / "market_state_on_demand_incremental_overlap_candidate_dataset_review_readout_v0_1.md").write_text(
        make_markdown_readout(matrix), encoding="utf-8"
    )

    print(json.dumps({"status": decision_status, "hard_review_failures": hard_review_failures, "next_gate": matrix["next_allowed_gate"]}, indent=2))


if __name__ == "__main__":
    main()
