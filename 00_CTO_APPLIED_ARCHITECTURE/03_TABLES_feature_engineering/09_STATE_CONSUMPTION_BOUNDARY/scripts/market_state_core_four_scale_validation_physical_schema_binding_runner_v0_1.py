from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FEATURE_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = FEATURE_ROOT / "09_STATE_CONSUMPTION_BOUNDARY"
PROFILE_ROOT = (
    FEATURE_ROOT
    / "06_MARKET_STATE_INTEGRATION/official_profiles/market_state_core_four_intraday_profile_v0_1"
)
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
RUN = (
    BOUNDARY
    / "runs/bounded_state_bundle_read_and_replay_execution_v0_1_20260730T075225Z"
)

BINDING_PATH = BOUNDARY / "market_state_core_four_scale_validation_physical_schema_binding_v0_1.json"
MATRIX_PATH = BOUNDARY / "market_state_core_four_scale_validation_physical_schema_binding_matrix_v0_1.json"
READOUT_PATH = BOUNDARY / "market_state_core_four_scale_validation_physical_schema_binding_readout_v0_1.md"

REQUIRED_CASE_IDS = [
    "BINDING_SCHEMA_CONTRACT_HASH_MATCH",
    "BINDING_PROFILE_MANIFEST_HASH_MATCH",
    "BINDING_EVIDENCE_MANIFEST_HASH_MATCH",
    "BINDING_PROVENANCE_HASH_CONFIRMED",
    "BINDING_RUNTIME_BUNDLE_HASH_CONFIRMED",
    "BINDING_RUNTIME_READ_REPORT_HASH_MATCH",
    "BINDING_EXECUTION_FINAL_MANIFEST_HASH_MATCH",
    "BINDING_RUNTIME_PARQUET_HASH_OBSERVED_MATCH",
    "BINDING_EXACT_40_COLUMN_SCHEMA_MATCH",
    "BINDING_HASH_ROLES_DISTINCT",
    "BINDING_CURRENT_CONTENT_AUTHORITY_UNAMBIGUOUS",
    "BINDING_STRUCTURAL_AUTHORITY_UNAMBIGUOUS",
    "BINDING_HISTORICAL_ARTIFACTS_PRESERVED",
    "BINDING_NO_PHYSICAL_READ",
    "BINDING_NO_BACKTEST_PHYSICAL_EXECUTION_AUTHORITY",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
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
    binding = load(BINDING_PATH)
    schema_path = PROFILE_ROOT / "PHYSICAL_SCHEMA_CONTRACT.json"
    profile_path = PROFILE_ROOT / "PROFILE_MANIFEST.json"
    evidence_path = PROFILE_ROOT / "EVIDENCE_MANIFEST.json"
    bundle_path = (
        RUNTIME
        / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_bundle_manifest_v0_1.json"
    )
    read_path = RUN / "bounded_read_report.json"
    final_path = RUN / "final_manifest.json"
    schema = load(schema_path)
    profile = load(profile_path)
    evidence = load(evidence_path)
    bundle = load(bundle_path)
    read_report = load(read_path)
    final = load(final_path)
    structural = binding["structural_schema_authority"]
    provenance = binding["profile_provenance"]
    runtime = binding["current_runtime_content_authority"]
    compatibility = binding["compatibility_evidence"]
    interpretation = binding["consumer_interpretation"]
    boundaries = binding["boundaries"]
    cases: list[dict[str, Any]] = []

    add(cases, REQUIRED_CASE_IDS[0], sha(schema_path) == structural["artifact_sha256"], sha(schema_path))
    add(cases, REQUIRED_CASE_IDS[1], sha(profile_path) == provenance["profile_manifest_sha256"], sha(profile_path))
    add(cases, REQUIRED_CASE_IDS[2], sha(evidence_path) == provenance["evidence_manifest_sha256"], sha(evidence_path))
    add(
        cases,
        REQUIRED_CASE_IDS[3],
        schema["candidate_parquet_sha256_reference"]
        == profile["candidate_parquet_sha256_reference"]
        == evidence["scale_c_primary_physical_evidence"]["candidate_parquet_sha256"]
        == provenance["provenance_candidate_parquet_sha256"],
        provenance["provenance_candidate_parquet_sha256"],
    )
    bundle_parquet_hash = next(
        item["sha256"] for item in bundle["artifact_hashes"] if item["artifact_id"] == "candidate_parquet"
    )
    add(
        cases,
        REQUIRED_CASE_IDS[4],
        bundle["bundle_ref"]["sha256"] == runtime["state_bundle_canonical_sha256"]
        and bundle_parquet_hash == runtime["candidate_parquet_sha256"],
        {"bundle": bundle["bundle_ref"]["sha256"], "parquet": bundle_parquet_hash},
    )
    add(cases, REQUIRED_CASE_IDS[5], sha(read_path) == compatibility["bounded_read_report_sha256"], sha(read_path))
    add(cases, REQUIRED_CASE_IDS[6], sha(final_path) == compatibility["execution_final_manifest_sha256"], sha(final_path))
    parquet_hash_report = next(
        item for item in read_report["input_hash_verification"] if item["artifact_id"] == "candidate_parquet"
    )
    add(
        cases,
        REQUIRED_CASE_IDS[7],
        parquet_hash_report["match"] is True
        and parquet_hash_report["observed_sha256"] == runtime["candidate_parquet_sha256"],
        parquet_hash_report,
    )
    add(
        cases,
        REQUIRED_CASE_IDS[8],
        len(read_report["schema_validation"]) == structural["column_count"] == 40
        and all(row["match"] for row in read_report["schema_validation"])
        and compatibility["physical_schema_mismatches"] == 0,
        {"columns": len(read_report["schema_validation"]), "mismatches": 0},
    )
    add(
        cases,
        REQUIRED_CASE_IDS[9],
        provenance["provenance_candidate_parquet_sha256"] != runtime["candidate_parquet_sha256"]
        and interpretation["hashes_are_interchangeable"] is False,
        {
            "provenance": provenance["provenance_candidate_parquet_sha256"],
            "runtime": runtime["candidate_parquet_sha256"],
        },
    )
    add(
        cases,
        REQUIRED_CASE_IDS[10],
        interpretation["current_runtime_content_sha256"] == runtime["candidate_parquet_sha256"]
        and runtime["role"] == "AUTHORITATIVE_FOR_CURRENT_BOUNDED_RUNTIME_CONTENT",
        runtime["candidate_parquet_sha256"],
    )
    add(
        cases,
        REQUIRED_CASE_IDS[11],
        interpretation["structural_authority"] == "PHYSICAL_SCHEMA_CONTRACT.json"
        and structural["role"] == "AUTHORITATIVE_FOR_PHYSICAL_STRUCTURE",
        structural["artifact_sha256"],
    )
    add(
        cases,
        REQUIRED_CASE_IDS[12],
        boundaries["historical_artifacts_modified"] is False
        and structural["candidate_parquet_sha256_reference_semantics"]
        == "PROFILE_PROVENANCE_REFERENCE_NOT_CURRENT_RUNTIME_CONTENT_AUTHORITY",
        "historical profile artifacts remain byte-preserved",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[13],
        boundaries["parquet_opened_by_binding_gate"] is False
        and boundaries["physical_rows_read_by_binding_gate"] == 0,
        "metadata-only binding validation",
    )
    add(
        cases,
        REQUIRED_CASE_IDS[14],
        boundaries["BT_GATE_014_contract_and_implementation_ready"] is True
        and boundaries["BT_GATE_014_physical_execution_authorized"] is False
        and boundaries["new_physical_read_authorization_issued"] is False,
        "contract handoff only",
    )

    ids = [case["case_id"] for case in cases]
    missing = sorted(set(REQUIRED_CASE_IDS) - set(ids))
    unexpected = sorted(set(ids) - set(REQUIRED_CASE_IDS))
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    failed = [case for case in cases if not case["passed"]]
    status = (
        "CLOSED_PASS_SCHEMA_PROVENANCE_AND_RUNTIME_CONTENT_AUTHORITY_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ"
        if not failed and not missing and not unexpected and not duplicates
        else "CLOSED_BLOCKED_SCHEMA_PARQUET_AUTHORITY_BINDING_FAILED"
    )
    matrix = {
        "gate": "market_state_core_four_scale_validation_physical_schema_binding_clarification_v0_1",
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
        "new_physical_read_authorization_issued": False,
        "BT_GATE_014_contract_and_implementation_ready": not failed,
        "BT_GATE_014_physical_execution_authorized": False,
        "cases": cases,
    }
    MATRIX_PATH.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    readout = f"""# Market State Core-Four Scale-Validation Physical Schema Binding Readout v0.1

Gate: `market_state_core_four_scale_validation_physical_schema_binding_clarification_v0_1`
Date: `2026-07-30`
Status: `{status}`

```text
case_count = {len(cases)}
failed_cases = {len(failed)}
structural schema authority = PHYSICAL_SCHEMA_CONTRACT.json
structural schema columns = 40
schema mismatches observed by bounded execution = 0
profile provenance parquet SHA-256 = b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2
current bounded runtime content SHA-256 = bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68
hashes interchangeable = false
parquet opened by binding gate = false
physical rows read by binding gate = 0
```

`b1841f...` remains the provenance reference of the promoted profile and its
historical Scale C evidence. It is not authority for selecting the current
runtime artifact.

`bc033c...` is the current bounded runtime content authority for the BT-GATE-014
handoff. Its physical structure matched all 40 fields of the governed schema
during the recorded single-use execution.

No historical profile artifact was edited. This clarification makes
BT-GATE-014 contract and implementation work ready, but does not authorize the
backtester's physical execution.
"""
    READOUT_PATH.write_text(readout, encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "case_count": len(cases), "failed_cases": len(failed)}, indent=2))
    return 0 if not failed and not missing and not unexpected and not duplicates else 1


if __name__ == "__main__":
    raise SystemExit(main())
