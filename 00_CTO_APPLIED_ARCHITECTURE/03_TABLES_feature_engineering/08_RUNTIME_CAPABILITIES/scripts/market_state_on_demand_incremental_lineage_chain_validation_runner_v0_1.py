from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BASE = Path(r"C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\08_RUNTIME_CAPABILITIES")
GATE_ID = "market_state_on_demand_incremental_lineage_chain_validation_v0_1"
VALIDATION_ID = f"{GATE_ID}_20260727T000000Z"
STATUS = "CLOSED_PASS_INCREMENTAL_LINEAGE_CHAIN_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION"
NEXT_GATE = "market_state_on_demand_scale_validation_v0_1"
SECOND_REVIEW_ID = "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260727T000000Z"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def sha_json(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def hash_excluding(data: dict[str, Any], key: str) -> str:
    return sha_json({k: v for k, v in data.items() if k != key})


def ckey(row: dict[str, Any]) -> str:
    return "|".join([str(row["instrument_id"]), str(row["session_date"]), str(row["decision_timestamp_utc"])])


def md(matrix: dict[str, Any]) -> str:
    d = matrix["decision"]
    return f"""# Market State On-Demand Incremental Lineage Chain Validation Readout v0.1

Status: `{matrix['status']}`
Date: `2026-07-27`

```text
validation_id = {matrix['validation_id']}
source_review = {matrix['source_review']}
validation_decision = {d['validation_decision']}
requested_contexts = {d['requested_contexts']}
represented_contexts = {d['represented_contexts']}
baseline_origin_rows = {d['baseline_origin_rows']}
delta1_origin_rows = {d['delta1_origin_rows']}
delta2_origin_rows = {d['delta2_origin_rows']}
unavailable_contexts = {d['unavailable_contexts']}
unaccounted_contexts = {d['unaccounted_contexts']}
hard_validation_failures = {d['hard_validation_failures']}
official_dataset = false
production = false
downstream = false
next_allowed_gate = {matrix['next_allowed_gate']}
```

The lineage chain is accepted only as bounded runtime evidence. It does not
promote an official Market State dataset and does not authorize downstream use.
"""


def main() -> int:
    second_matrix = read_json(BASE / "market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_matrix_v0_1.json")
    second_ledger = read_json(BASE / "second_generation_candidate_context_ledger_v0_1.json")
    second_fp = read_json(BASE / "second_generation_candidate_fingerprint_comparison_v0_1.json")
    parent_ledger = read_json(BASE / "combined_candidate_context_ledger_v0_1.json")
    parent_fp = read_json(BASE / "combined_candidate_fingerprint_comparison_v0_1.json")

    parent_by_key = {ckey(x): x for x in parent_ledger["entries"]}
    expanded_entries = []
    missing_parent_refs = 0
    baseline_origin_rows = 0
    delta1_origin_rows = 0
    delta2_origin_rows = 0
    unavailable_contexts = 0

    for entry in second_ledger["entries"]:
        mode = entry["origin_mode"]
        out = dict(entry)
        if mode == "base_combined_reused_validated":
            parent = parent_by_key.get(ckey(entry))
            if parent is None:
                missing_parent_refs += 1
                out["expanded_origin_mode"] = "missing_parent_reference"
            else:
                parent_mode = parent["origin_mode"]
                out["parent_origin_mode"] = parent_mode
                out["parent_origin_run_id"] = parent.get("origin_run_id")
                out["parent_origin_dataset_id"] = parent.get("origin_dataset_id")
                if parent_mode == "reused_validated":
                    baseline_origin_rows += 1
                    out["expanded_origin_mode"] = "baseline_origin"
                elif parent_mode == "materialized_delta":
                    delta1_origin_rows += 1
                    out["expanded_origin_mode"] = "delta1_origin"
                else:
                    missing_parent_refs += 1
                    out["expanded_origin_mode"] = "unexpected_parent_origin"
        elif mode == "second_delta_materialized":
            delta2_origin_rows += 1
            out["expanded_origin_mode"] = "delta2_origin"
        elif mode == "unavailable_preserved_from_base_combined_candidate":
            parent = parent_by_key.get(ckey(entry))
            if parent is None or parent.get("origin_mode") != "unavailable":
                missing_parent_refs += 1
                out["expanded_origin_mode"] = "missing_parent_unavailable_reference"
            else:
                unavailable_contexts += 1
                out["parent_origin_mode"] = parent.get("origin_mode")
                out["expanded_origin_mode"] = "unavailable_preserved"
        else:
            missing_parent_refs += 1
            out["expanded_origin_mode"] = "unexpected_second_generation_origin"
        expanded_entries.append(out)

    requested_contexts = len(expanded_entries)
    represented_contexts = baseline_origin_rows + delta1_origin_rows + delta2_origin_rows
    unaccounted_contexts = requested_contexts - represented_contexts - unavailable_contexts
    duplicate_contexts = requested_contexts - len({ckey(x) for x in expanded_entries})

    checks = [
        (second_matrix["status"] == "CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION", "source_review_closed_pass"),
        (hash_excluding(second_ledger, "context_ledger_sha256") == second_ledger["context_ledger_sha256"], "second_generation_ledger_hash_match"),
        (hash_excluding(parent_ledger, "context_ledger_sha256") == parent_ledger["context_ledger_sha256"], "parent_ledger_hash_match"),
        (hash_excluding(second_fp, "fingerprint_comparison_sha256") == second_fp["fingerprint_comparison_sha256"], "second_generation_fingerprint_comparison_hash_match"),
        (hash_excluding(parent_fp, "fingerprint_comparison_sha256") == parent_fp["fingerprint_comparison_sha256"], "parent_fingerprint_comparison_hash_match"),
        (requested_contexts == 15, "requested_contexts_15"),
        (represented_contexts == 14, "represented_contexts_14"),
        (baseline_origin_rows == 8, "baseline_origin_rows_8"),
        (delta1_origin_rows == 3, "delta1_origin_rows_3"),
        (delta2_origin_rows == 3, "delta2_origin_rows_3"),
        (unavailable_contexts == 1, "unavailable_contexts_1"),
        (unaccounted_contexts == 0, "unaccounted_contexts_zero"),
        (duplicate_contexts == 0, "duplicate_contexts_zero"),
        (missing_parent_refs == 0, "missing_parent_refs_zero"),
        (second_matrix["official_dataset"] is False and second_matrix["downstream"] is False, "authority_boundaries_closed"),
    ]
    hard_failures = sum(0 if passed else 1 for passed, _ in checks)
    status = STATUS if hard_failures == 0 else "CLOSED_BLOCKED_INCREMENTAL_LINEAGE_CHAIN_VALIDATION"

    expanded = {
        "validation_id": VALIDATION_ID,
        "validation_gate": GATE_ID,
        "source_review": SECOND_REVIEW_ID,
        "counts": {
            "requested_contexts": requested_contexts,
            "represented_contexts": represented_contexts,
            "baseline_origin_rows": baseline_origin_rows,
            "delta1_origin_rows": delta1_origin_rows,
            "delta2_origin_rows": delta2_origin_rows,
            "unavailable_contexts": unavailable_contexts,
            "unaccounted_contexts": unaccounted_contexts,
            "duplicate_contexts": duplicate_contexts,
            "missing_parent_refs": missing_parent_refs,
        },
        "entries": expanded_entries,
    }
    expanded["lineage_chain_ledger_sha256"] = hash_excluding(expanded, "lineage_chain_ledger_sha256")

    matrix = {
        "validation_id": VALIDATION_ID,
        "validation_gate": GATE_ID,
        "status": status,
        "source_review": SECOND_REVIEW_ID,
        "decision": {
            "validation_decision": "lineage_chain_validated_with_restrictions" if hard_failures == 0 else "blocked",
            "requested_contexts": requested_contexts,
            "represented_contexts": represented_contexts,
            "baseline_origin_rows": baseline_origin_rows,
            "delta1_origin_rows": delta1_origin_rows,
            "delta2_origin_rows": delta2_origin_rows,
            "unavailable_contexts": unavailable_contexts,
            "unaccounted_contexts": unaccounted_contexts,
            "hard_validation_failures": hard_failures,
        },
        "checks": [{"check_id": name, "status": "PASS" if passed else "FAIL"} for passed, name in checks],
        "evidence": {
            "lineage_chain_ledger_sha256": expanded["lineage_chain_ledger_sha256"],
            "second_generation_context_ledger_sha256": second_ledger["context_ledger_sha256"],
            "parent_context_ledger_sha256": parent_ledger["context_ledger_sha256"],
            "second_generation_fingerprint_comparison_sha256": second_fp["fingerprint_comparison_sha256"],
            "parent_fingerprint_comparison_sha256": parent_fp["fingerprint_comparison_sha256"],
        },
        "next_allowed_gate": NEXT_GATE if hard_failures == 0 else None,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }

    scope = {
        "scope_id": "market_state_on_demand_incremental_lineage_chain_validation_scope_v0_1",
        "gate": GATE_ID,
        "validation_id": VALIDATION_ID,
        "source_review": SECOND_REVIEW_ID,
        "execution_authorized": False,
        "dataset_mutation_authorized": False,
        "official_dataset_promotion_authorized": False,
        "downstream_consumption_authorized": False,
        "next_allowed_gate": matrix["next_allowed_gate"],
    }

    auth = f"""# Market State On-Demand Incremental Lineage Chain Validation Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_VALIDATION`
Date: `2026-07-27`

```text
validation_id = {VALIDATION_ID}
source_review = {SECOND_REVIEW_ID}
execution_authorized = false
dataset_mutation_authorized = false
official_dataset_promotion_authorized = false
downstream_consumption_authorized = false
```
"""

    write_json(BASE / "configs" / "market_state_on_demand_incremental_lineage_chain_validation_scope_v0_1.json", scope)
    write_json(BASE / "market_state_on_demand_incremental_lineage_chain_validation_matrix_v0_1.json", matrix)
    write_json(BASE / "incremental_lineage_chain_ledger_v0_1.json", expanded)
    (BASE / "market_state_on_demand_incremental_lineage_chain_validation_authorization_v0_1.md").write_text(auth, encoding="utf-8")
    (BASE / "market_state_on_demand_incremental_lineage_chain_validation_readout_v0_1.md").write_text(md(matrix), encoding="utf-8")
    print(json.dumps({"status": status, "hard_validation_failures": hard_failures, "next_gate": matrix["next_allowed_gate"]}, indent=2))
    return 0 if hard_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
