from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

BASE = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\08_RUNTIME_CAPABILITIES")
RUN_ID = "market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103901Z"
RUN_DIR = BASE / "runs" / RUN_ID
INVALID_ATTEMPT_ID = "market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103756Z"
BASE_COMBINED_RUN_ID = "market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z"
BASE_COMBINED_RUN_DIR = BASE / "runs" / BASE_COMBINED_RUN_ID
GATE_ID = "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1"
REVIEW_ID = f"{GATE_ID}_20260727T000000Z"
STATUS = "CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION"
NEXT_GATE = "market_state_on_demand_incremental_lineage_chain_validation_v0_1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_json(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def hash_excluding(data: dict[str, Any], key: str) -> str:
    return sha_json({k: v for k, v in data.items() if k != key})


def norm_ts(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.isoformat().replace("+00:00", "Z")


def norm_date(value: Any) -> str:
    return pd.Timestamp(value).date().isoformat()


def parquet_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for row in pd.read_parquet(path).to_dict(orient="records"):
        out = dict(row)
        out["session_date"] = norm_date(out["session_date"])
        out["decision_timestamp_utc"] = norm_ts(out["decision_timestamp_utc"])
        rows.append(out)
    return rows


def ckey(row: dict[str, Any]) -> str:
    return "|".join([str(row["instrument_id"]), str(row["session_date"]), str(row["decision_timestamp_utc"])])


def md(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Market State On-Demand Second-Generation Incremental Extension Candidate Dataset Review Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-27`

```text
review_id = {matrix['review_id']}
reviewed_run = {matrix['reviewed_run']}
reviewed_candidate_dataset_id = {matrix['reviewed_candidate_dataset_id']}
review_decision = {d['review_decision']}
requested_contexts = {d['requested_contexts']}
represented_contexts = {d['represented_contexts']}
base_combined_reused_contexts = {d['base_combined_reused_contexts']}
second_delta_materialized_rows = {d['second_delta_materialized_rows']}
unavailable_contexts = {d['unavailable_contexts']}
unaccounted_contexts = {d['unaccounted_contexts']}
hard_review_failures = {d['hard_review_failures']}
candidate_dataset_validated = {str(d['candidate_dataset_validated']).lower()}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

The candidate is accepted only as bounded second-generation incremental Market
State on-demand evidence. It is not an official physical dataset, not production
and not downstream-consumable.
"""


def main() -> int:
    final_manifest = read_json(RUN_DIR / "final_manifest.json")
    candidate_manifest = read_json(RUN_DIR / "candidate_output_manifest.json")
    registry_entry = read_json(RUN_DIR / "candidate_registry_entry.json")
    validation_report = read_json(RUN_DIR / "market_state_validation_report.json")
    partition_report = read_json(RUN_DIR / "partition_coverage_resolution_report.json")
    execution_report = read_json(RUN_DIR / "market_state_second_generation_incremental_extension_report.json")
    invalid_attempt = read_json(BASE / "runs" / INVALID_ATTEMPT_ID / "failure_manifest.json")
    base_registry = read_json(BASE_COMBINED_RUN_DIR / "candidate_registry_entry.json")
    base_final = read_json(BASE_COMBINED_RUN_DIR / "final_manifest.json")
    base_candidate_manifest = read_json(BASE_COMBINED_RUN_DIR / "candidate_output_manifest.json")
    parent_ledger = read_json(BASE / "combined_candidate_context_ledger_v0_1.json")
    parent_fingerprint_comparison = read_json(BASE / "combined_candidate_fingerprint_comparison_v0_1.json")

    delta2_file = Path(candidate_manifest["new_second_delta_files"][0]["path"])
    delta2_rows = parquet_rows(delta2_file)
    delta2_by_key = {ckey(row): row for row in delta2_rows}
    delta2_columns = list(pd.read_parquet(delta2_file).columns)

    baseline_artifact = parent_fingerprint_comparison["baseline_physical_artifact"]
    delta1_artifact = parent_fingerprint_comparison["delta_physical_artifact"]
    baseline_hash_ok = sha_file(Path(baseline_artifact["path"])) == baseline_artifact["recorded_sha256"]
    delta1_hash_ok = sha_file(Path(delta1_artifact["path"])) == delta1_artifact["recorded_sha256"]
    delta2_hash_ok = sha_file(delta2_file) == candidate_manifest["new_second_delta_files"][0]["sha256"]

    ledger_entries = []
    for part in partition_report["partitions"]:
        entry = dict(part)
        disp = part["partition_disposition"]
        if disp == "reusable_validated":
            entry.update({
                "origin_mode": "base_combined_reused_validated",
                "origin_run_id": BASE_COMBINED_RUN_ID,
                "origin_dataset_id": candidate_manifest["base_combined_candidate_reused"]["dataset_id"],
                "origin_candidate_dataset_fingerprint": candidate_manifest["base_combined_candidate_reused"]["candidate_dataset_fingerprint"],
                "physical_row_rewritten_by_second_generation_run": False,
            })
        elif disp == "to_build":
            row = delta2_by_key[ckey(part)]
            entry.update({
                "origin_mode": "second_delta_materialized",
                "origin_run_id": RUN_ID,
                "origin_dataset_id": candidate_manifest["candidate_dataset_id"],
                "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
            })
        elif disp == "unavailable":
            entry.update({
                "origin_mode": "unavailable_preserved_from_base_combined_candidate",
                "origin_run_id": BASE_COMBINED_RUN_ID,
                "origin_dataset_id": candidate_manifest["base_combined_candidate_reused"]["dataset_id"],
            })
        ledger_entries.append(entry)

    counts = {
        "requested_contexts": len(ledger_entries),
        "base_combined_reused": sum(1 for x in ledger_entries if x["origin_mode"] == "base_combined_reused_validated"),
        "second_delta_materialized": sum(1 for x in ledger_entries if x["origin_mode"] == "second_delta_materialized"),
        "unavailable": sum(1 for x in ledger_entries if x["origin_mode"] == "unavailable_preserved_from_base_combined_candidate"),
    }
    counts["represented_contexts"] = counts["base_combined_reused"] + counts["second_delta_materialized"]
    counts["unaccounted_contexts"] = counts["requested_contexts"] - counts["represented_contexts"] - counts["unavailable"]

    duplicate_contexts = counts["requested_contexts"] - len({ckey(x) for x in ledger_entries})
    schema_contract_match = candidate_manifest["schema_contract_sha256"] == base_candidate_manifest["schema_contract_sha256"]
    base_registry_unchanged = execution_report["base_combined_registry_entry_mutated"] is False and final_manifest["base_combined_registry_entry_mutations"] == 0
    invalid_attempt_marked = invalid_attempt["status"] == "CLOSED_FAILED_RUNTIME_ARTIFACT_PATH_TOO_LONG" and invalid_attempt["valid_gate_closure"] is False

    checks = [
        (final_manifest["status"] == "CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED", "run_closed_pass"),
        (validation_report["hard_validation_failures"] == 0, "validator_hard_failures_zero"),
        (registry_entry["registry_status"] == "validated_candidate", "registry_validated_candidate"),
        (registry_entry["downstream_eligibility"] is False, "downstream_closed"),
        (counts == {"requested_contexts": 15, "base_combined_reused": 11, "second_delta_materialized": 3, "unavailable": 1, "represented_contexts": 14, "unaccounted_contexts": 0}, "ledger_counts_match"),
        (duplicate_contexts == 0, "duplicate_contexts_zero"),
        (schema_contract_match, "schema_contract_match"),
        (baseline_hash_ok and delta1_hash_ok and delta2_hash_ok, "physical_artifact_hashes_match"),
        (base_registry_unchanged, "base_combined_registry_unchanged"),
        (execution_report["materializer_build_scope_second_delta_only"] is True, "materializer_second_delta_only"),
        (invalid_attempt_marked, "invalid_attempt_marked"),
    ]
    hard_failures = sum(0 if passed else 1 for passed, _ in checks)
    decision_status = STATUS if hard_failures == 0 else "CLOSED_BLOCKED_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_REVIEW"

    context_ledger = {
        "review_id": REVIEW_ID,
        "review_gate": GATE_ID,
        "source_run": RUN_ID,
        "ledger_grain": "profile_id+instrument_id+session_date+decision_timestamp_utc",
        "counts": counts,
        "entries": ledger_entries,
    }
    context_ledger["context_ledger_sha256"] = hash_excluding(context_ledger, "context_ledger_sha256")

    fingerprint_comparison = {
        "review_id": REVIEW_ID,
        "review_gate": GATE_ID,
        "candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "scientific_dataset_fingerprint": candidate_manifest["scientific_dataset_fingerprint"],
        "base_combined_candidate_fingerprint": candidate_manifest["base_combined_candidate_reused"]["candidate_dataset_fingerprint"],
        "base_combined_scientific_fingerprint": candidate_manifest["base_combined_candidate_reused"]["scientific_dataset_fingerprint"],
        "delta2_physical_artifact": {
            "path": str(delta2_file),
            "recorded_sha256": candidate_manifest["new_second_delta_files"][0]["sha256"],
            "current_sha256": sha_file(delta2_file),
            "hash_match": delta2_hash_ok,
            "rows": len(delta2_rows),
            "columns": len(delta2_columns),
        },
        "parent_base_artifacts": {
            "baseline_hash_match": baseline_hash_ok,
            "delta1_hash_match": delta1_hash_ok,
            "parent_context_ledger_sha256": parent_ledger["context_ledger_sha256"],
        },
    }
    fingerprint_comparison["fingerprint_comparison_sha256"] = hash_excluding(fingerprint_comparison, "fingerprint_comparison_sha256")

    matrix = {
        "review_id": REVIEW_ID,
        "review_gate": GATE_ID,
        "status": decision_status,
        "reviewed_run": RUN_ID,
        "reviewed_candidate_dataset_id": candidate_manifest["candidate_dataset_id"],
        "reviewed_candidate_dataset_fingerprint": candidate_manifest["candidate_dataset_fingerprint"],
        "base_combined_candidate": candidate_manifest["base_combined_candidate_reused"],
        "decision": {
            "review_decision": "approved_as_second_generation_incremental_candidate_evidence_with_restrictions" if hard_failures == 0 else "blocked",
            "requested_contexts": counts["requested_contexts"],
            "represented_contexts": counts["represented_contexts"],
            "base_combined_reused_contexts": counts["base_combined_reused"],
            "second_delta_materialized_rows": counts["second_delta_materialized"],
            "unavailable_contexts": counts["unavailable"],
            "unaccounted_contexts": counts["unaccounted_contexts"],
            "hard_review_failures": hard_failures,
            "dataset_completeness": "partial",
            "candidate_dataset_validated": hard_failures == 0,
            "official_dataset_after_review": False,
            "production_after_review": False,
            "downstream_after_review": False,
        },
        "checks": [{"check_id": name, "status": "PASS" if passed else "FAIL"} for passed, name in checks],
        "evidence": {
            "context_ledger_sha256": context_ledger["context_ledger_sha256"],
            "fingerprint_comparison_sha256": fingerprint_comparison["fingerprint_comparison_sha256"],
            "validation_result_fingerprint": validation_report["validation_result_fingerprint"],
            "registry_entry_fingerprint": registry_entry["registry_entry_fingerprint"],
        },
        "next_allowed_gate": NEXT_GATE if hard_failures == 0 else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }

    scope = {
        "scope_id": "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_scope_v0_1",
        "gate": GATE_ID,
        "review_id": REVIEW_ID,
        "reviewed_run": RUN_ID,
        "allowed_inputs": [
            "final_manifest.json",
            "candidate_output_manifest.json",
            "candidate_registry_entry.json",
            "market_state_validation_report.json",
            "partition_coverage_resolution_report.json",
            "market_state_second_generation_incremental_extension_report.json",
        ],
        "execution_authorized": False,
        "dataset_mutation_authorized": False,
        "official_dataset_promotion_authorized": False,
        "downstream_consumption_authorized": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
    }

    auth = f"""# Market State On-Demand Second-Generation Incremental Extension Candidate Dataset Review Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_REVIEW`
Date: `2026-07-27`

```text
review_id = {REVIEW_ID}
reviewed_run = {RUN_ID}
execution_authorized = false
dataset_mutation_authorized = false
official_dataset_promotion_authorized = false
downstream_consumption_authorized = false
```
"""

    write_json(BASE / "configs" / "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_scope_v0_1.json", scope)
    write_json(BASE / "second_generation_candidate_context_ledger_v0_1.json", context_ledger)
    write_json(BASE / "second_generation_candidate_fingerprint_comparison_v0_1.json", fingerprint_comparison)
    write_json(BASE / "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_matrix_v0_1.json", matrix)
    (BASE / "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_authorization_v0_1.md").write_text(auth, encoding="utf-8")
    (BASE / "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_readout_v0_1.md").write_text(md(matrix), encoding="utf-8")
    print(json.dumps({"status": decision_status, "hard_review_failures": hard_failures, "next_gate": matrix["next_allowed_gate"]}, indent=2))
    return 0 if hard_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
