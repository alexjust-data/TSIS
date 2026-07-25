#!/usr/bin/env python
"""Promote the bounded core-four intraday Market State profile registry.

This script writes only profile-registry metadata. It does not copy parquet,
write official datasets, authorize complete Market State, production or
downstream consumption.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "official_market_state_candidate_promotion_v0_1"
DEFAULT_RUN_PREFIX = "official_market_state_candidate_promotion_v0_1"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_hash(path: Path, expected: str, label: str, failures: list[str]) -> str | None:
    if not path.exists():
        failures.append(f"missing_required_artifact:{label}")
        return None
    observed = sha256_file(path)
    if observed != expected:
        failures.append(f"sha256_mismatch:{label}")
    return observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    parser.add_argument("--output-root")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    scope_path = Path(args.scope).resolve()
    base_dir = scope_path.parents[1]
    runs_root = base_dir / "runs"
    output_root = Path(args.output_root).resolve() if args.output_root else runs_root
    run_id = args.run_id or f"{DEFAULT_RUN_PREFIX}_{utc_stamp()}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    started_at = utc_now()
    scope = load_json(scope_path)
    failures: list[str] = []
    target = scope["promotion_target"]
    evidence = scope["scale_c_primary_physical_evidence"]
    prior = scope["required_prior_review"]
    registry_dir = (base_dir / scope["official_profile_registry_path"]).resolve()

    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "registry_dir": str(registry_dir),
        "authority_boundary": scope["authority_boundary"],
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "started", "updated_at_utc": utc_now()})

    if registry_dir.exists():
        failures.append(f"profile_registry_already_exists:{registry_dir}")

    review_run_dir = runs_root / prior["run_id"]
    review_final = review_run_dir / "final_manifest.json"
    review_decision_artifact = review_run_dir / "promotion_review_decision.json"
    review_inventory = review_run_dir / "evidence_inventory_report.csv"
    review_restrictions = review_run_dir / "promotion_review_restrictions_report.csv"

    verify_hash(review_final, prior["final_manifest_sha256"], "review_final_manifest", failures)
    verify_hash(review_decision_artifact, prior["decision_artifact_sha256"], "review_decision_artifact", failures)
    verify_hash(review_inventory, prior["evidence_inventory_sha256"], "review_evidence_inventory", failures)
    verify_hash(review_restrictions, prior["restrictions_report_sha256"], "review_restrictions_report", failures)

    review_payload = load_json(review_final) if review_final.exists() else {}
    if review_payload.get("decision") != prior["decision"]:
        failures.append("review_decision_not_approved_for_promotion")
    if review_payload.get("official_profile_promotion_executed") is not False:
        failures.append("review_boundary_expected_no_prior_promotion")

    candidate_parquet = base_dir / evidence["candidate_parquet_relative_path"]
    schema_report_path = base_dir / evidence["schema_report_relative_path"]
    physical_final_path = base_dir / evidence["physical_validation_final_manifest_relative_path"]
    verify_hash(candidate_parquet, evidence["candidate_parquet_sha256"], "candidate_parquet_reference", failures)
    verify_hash(schema_report_path, evidence["schema_report_sha256"], "schema_report", failures)
    verify_hash(physical_final_path, evidence["physical_validation_final_manifest_sha256"], "physical_validation_final_manifest", failures)

    physical_final = load_json(physical_final_path) if physical_final_path.exists() else {}
    schema_report = load_json(schema_report_path) if schema_report_path.exists() else {}
    if physical_final.get("output_physical_rows") != evidence["candidate_parquet_rows"]:
        failures.append("physical_validation_row_count_mismatch")
    if physical_final.get("hard_validation_failures") != 0:
        failures.append("physical_validation_hard_failures_nonzero")
    if physical_final.get("candidate_rows_are_canonical_market_state") is not False:
        failures.append("source_candidate_rows_unexpectedly_canonical")
    if schema_report.get("schema_match") is not True:
        failures.append("schema_report_not_matching")

    if failures:
        final_manifest = {
            "run_id": run_id,
            "script_version": SCRIPT_VERSION,
            "status": "blocked",
            "promotion_status": "BLOCKED_PENDING_EVIDENCE",
            "blocking_failures": failures,
            "official_profile_promotion_executed": False,
            "official_market_state_authorized": False,
            "official_parquet_files_written": 0,
            "candidate_parquet_copied": False,
            "completed_at_utc": utc_now(),
        }
        write_json(run_dir / "final_manifest.json", final_manifest)
        write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "blocked", "updated_at_utc": utc_now()})
        print(json.dumps(final_manifest, indent=2, sort_keys=True))
        return 2

    registry_dir.mkdir(parents=True, exist_ok=False)
    promoted_at = utc_now()

    profile_manifest = {
        "profile_id": target["promoted_profile_id"],
        "profile_classification": target["profile_classification"],
        "profile_scope": target["profile_scope"],
        "status": "OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS",
        "promoted_at_utc": promoted_at,
        "promotion_run_id": run_id,
        "source_physical_profile_id": target["source_physical_profile_id"],
        "source_physical_schema_version": target["source_physical_schema_version"],
        "complete_tsis_market_state": False,
        "required_information_objects": [
            "trading_activity",
            "price_movement",
            "price_location_structure",
            "volatility_range_state",
        ],
        "excluded_information_object_classes": [
            "quote_dependent_objects",
            "complete_tsis_market_state_objects_outside_core_four",
        ],
        "primary_evidence": scope["evidence_summary"],
        "candidate_parquet_sha256_reference": evidence["candidate_parquet_sha256"],
        "official_market_state_authorized": False,
        "official_dataset_registry_write_authorized": False,
        "downstream_consumption_authorized": False,
        "production_builder_authorized": False,
    }
    evidence_manifest = {
        "profile_id": target["promoted_profile_id"],
        "promotion_run_id": run_id,
        "prior_review": prior,
        "scale_c_primary_physical_evidence": evidence,
        "evidence_summary": scope["evidence_summary"],
        "candidate_parquet_reference_only": True,
        "candidate_parquet_copied": False,
        "source_market_data_rows_read_by_promotion": 0,
    }
    physical_schema_contract = {
        "profile_id": target["promoted_profile_id"],
        "source_physical_profile_id": target["source_physical_profile_id"],
        "state_schema_version": target["source_physical_schema_version"],
        "schema_authority": "accepted_scale_c_candidate_physical_validation_schema_report",
        "column_count": schema_report["observed_column_count"],
        "columns": schema_report["observed_schema"],
        "candidate_parquet_sha256_reference": evidence["candidate_parquet_sha256"],
        "official_parquet_written": False,
        "official_table_name": None,
        "official_dataset_root": None,
    }
    readme = f"""# {target['promoted_profile_id']}

Status: `OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS`
Date: `2026-07-23`

This directory registers the bounded core-four intraday Market State profile as
an official profile contract under applied architecture.

It is not complete TSIS Market State, not an operational Data Foundation dataset
registry, not production, and not downstream-consumable by itself.

```text
promotion_run_id = {run_id}
source_physical_profile_id = {target['source_physical_profile_id']}
state_schema_version = {target['source_physical_schema_version']}
candidate_parquet_sha256_reference = {evidence['candidate_parquet_sha256']}
physical_candidate_rows = {scope['evidence_summary']['physical_candidate_rows']}
value_mappings_checked = {scope['evidence_summary']['value_mappings_checked']}
hard_validation_failures = {scope['evidence_summary']['hard_validation_failures']}
official_market_state_authorized = false
official_parquet_written = false
downstream_consumption_authorized = false
```
"""

    write_json(registry_dir / "PROFILE_MANIFEST.json", profile_manifest)
    write_json(registry_dir / "EVIDENCE_MANIFEST.json", evidence_manifest)
    write_json(registry_dir / "PHYSICAL_SCHEMA_CONTRACT.json", physical_schema_contract)
    (registry_dir / "README.md").write_text(readme, encoding="utf-8")

    write_report_rows = []
    for path in [
        registry_dir / "README.md",
        registry_dir / "PROFILE_MANIFEST.json",
        registry_dir / "EVIDENCE_MANIFEST.json",
        registry_dir / "PHYSICAL_SCHEMA_CONTRACT.json",
    ]:
        write_report_rows.append({
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "artifact_class": "official_profile_registry_metadata",
        })

    with (run_dir / "official_profile_registry_write_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "bytes", "sha256", "artifact_class"])
        writer.writeheader()
        writer.writerows(write_report_rows)

    promotion_manifest = {
        "run_id": run_id,
        "profile_id": target["promoted_profile_id"],
        "promotion_status": "OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS",
        "registry_dir": str(registry_dir),
        "registry_artifacts_written": len(write_report_rows),
        "registry_write_report": "official_profile_registry_write_report.csv",
        "official_profile_promotion_executed": True,
        "official_market_state_authorized": False,
        "official_dataset_registry_write_authorized": False,
        "official_parquet_files_written": 0,
        "candidate_parquet_copied": False,
        "source_market_data_rows_read": 0,
        "next_allowed_gate": scope["next_allowed_gate"],
    }
    write_json(run_dir / "promotion_manifest.json", promotion_manifest)

    final_manifest = {
        **promotion_manifest,
        "script_version": SCRIPT_VERSION,
        "status": "complete",
        "blocking_failures": [],
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "hard_validation_failures": 0,
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "complete", "updated_at_utc": utc_now()})

    readout = f"""# Official Market State Candidate Promotion Readout v0.1

run_id = `{run_id}`
script_version = `{SCRIPT_VERSION}`

```text
official_market_state_candidate_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
promoted_profile_id = {target['promoted_profile_id']}
source_physical_profile_id = {target['source_physical_profile_id']}
registry_artifacts_written = {len(write_report_rows)}
official_profile_promotion_executed = true
official_market_state_authorized = false
official_dataset_registry_write_authorized = false
official_parquet_files_written = 0
candidate_parquet_copied = false
source_market_data_rows_read = 0
hard_validation_failures = 0
next_allowed_gate = {scope['next_allowed_gate']}
```

The promoted artifact is an official profile registry package only. It does not
promote complete TSIS Market State, write or copy parquet, authorize production,
authorize downstream consumption or open full-history/full-universe execution.
"""
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")
    print(json.dumps(final_manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
