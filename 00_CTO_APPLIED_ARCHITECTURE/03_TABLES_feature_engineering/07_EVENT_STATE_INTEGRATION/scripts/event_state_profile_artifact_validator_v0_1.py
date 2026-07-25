#!/usr/bin/env python
"""Validate the promoted Event State profile registry package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "event_state_profile_artifact_validation_v0_1"
DEFAULT_RUN_PREFIX = "event_state_profile_artifact_validation_v0_1"
SCHEMA_CONTRACT_FILE = "EVENT_STATE_SCHEMA_CONTRACT.json"


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


def check_hash(path: Path, expected: str, label: str, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"missing_artifact:{label}")
        return ""
    observed = sha256_file(path)
    if observed.lower() != expected.lower():
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
    registry_dir = (base_dir / scope["registry_path"]).resolve()
    root_readout_path = base_dir / "event_state_profile_artifact_validation_readout_v0_1.md"
    failures: list[str] = []

    write_json(run_dir / "pre_manifest.json", {
        "authority_boundary": scope["authority_boundary"],
        "registry_dir": str(registry_dir),
        "run_id": run_id,
        "scope_path": str(scope_path),
        "script_version": SCRIPT_VERSION,
        "started_at_utc": started_at,
    })
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "started", "updated_at_utc": utc_now()})

    prior = scope["required_prior_promotion"]
    promotion_dir = runs_root / prior["run_id"]
    check_hash(promotion_dir / "final_manifest.json", prior["final_manifest_sha256"], "promotion_final_manifest", failures)
    check_hash(promotion_dir / "promotion_manifest.json", prior["promotion_manifest_sha256"], "promotion_manifest", failures)
    check_hash(promotion_dir / "official_profile_registry_write_report.csv", prior["registry_write_report_sha256"], "registry_write_report", failures)
    check_hash(promotion_dir / "readout.md", prior["readout_sha256"], "promotion_readout", failures)

    artifact_rows: list[dict[str, Any]] = []
    for item in scope["required_registry_artifacts"]:
        path = registry_dir / item["name"]
        observed = check_hash(path, item["sha256"], item["name"], failures)
        artifact_rows.append({
            "artifact": item["name"],
            "bytes": path.stat().st_size if path.exists() else 0,
            "exists": path.exists(),
            "expected_sha256": item["sha256"],
            "observed_sha256": observed,
            "path": str(path),
            "sha256_match": observed.lower() == item["sha256"].lower(),
        })

    with (run_dir / "registry_artifact_validation_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(artifact_rows[0].keys()))
        writer.writeheader()
        writer.writerows(artifact_rows)

    profile_manifest = load_json(registry_dir / "PROFILE_MANIFEST.json") if (registry_dir / "PROFILE_MANIFEST.json").exists() else {}
    evidence_manifest = load_json(registry_dir / "EVIDENCE_MANIFEST.json") if (registry_dir / "EVIDENCE_MANIFEST.json").exists() else {}
    schema_contract = load_json(registry_dir / SCHEMA_CONTRACT_FILE) if (registry_dir / SCHEMA_CONTRACT_FILE).exists() else {}
    expected = scope["expected_registry_invariants"]

    checks = {
        "accepted_event_type_ids": profile_manifest.get("accepted_event_type_ids") == expected["accepted_event_type_ids"],
        "accepted_event_types": len(profile_manifest.get("accepted_event_type_ids", [])) == expected["accepted_event_types"],
        "accepted_subject_scope": profile_manifest.get("accepted_subject_scope") == expected["accepted_subject_scope"],
        "candidate_event_state_records_copied": evidence_manifest.get("candidate_event_state_records_copied") is expected["candidate_event_state_records_copied"],
        "candidate_event_state_records_reference_only": evidence_manifest.get("candidate_event_state_records_reference_only") is expected["candidate_event_state_records_reference_only"],
        "candidate_records_checked": schema_contract.get("candidate_records_checked") == expected["candidate_records_checked"],
        "complete_tsis_event_state": profile_manifest.get("complete_tsis_event_state") is expected["complete_tsis_event_state"],
        "downstream_consumption_authorized": profile_manifest.get("downstream_consumption_authorized") is expected["downstream_consumption_authorized"],
        "event_detection_authorized": profile_manifest.get("event_detection_authorized") is expected["event_detection_authorized"],
        "event_state_materialization_authorized": profile_manifest.get("event_state_materialization_authorized") is expected["event_state_materialization_authorized"],
        "field_count": schema_contract.get("field_count") == expected["field_count"],
        "field_contract_len": len(schema_contract.get("field_contract", [])) == expected["field_count"],
        "all_schema_fields_required": all(field.get("required") == "true" for field in schema_contract.get("field_contract", [])),
        "official_dataset_registry_write_authorized": profile_manifest.get("official_dataset_registry_write_authorized") is expected["official_dataset_registry_write_authorized"],
        "official_event_state_dataset_promotion": profile_manifest.get("official_event_state_dataset_promotion") is expected["official_event_state_dataset_promotion"],
        "official_event_state_parquet_written": profile_manifest.get("official_event_state_parquet_written") is expected["official_event_state_parquet_written"],
        "physical_validation_schema_failures": schema_contract.get("physical_validation_schema_failures") == expected["physical_validation_schema_failures"],
        "production_authorized": profile_manifest.get("production_authorized") is expected["production_authorized"],
        "profile_classification": profile_manifest.get("profile_classification") == expected["profile_classification"],
        "profile_id": profile_manifest.get("profile_id") == expected["profile_id"],
        "profile_status": profile_manifest.get("status") == expected["profile_status"],
        "promotion_run_id": profile_manifest.get("promotion_run_id") == prior["run_id"],
        "source_market_state_physical_dataset_official": profile_manifest.get("source_market_state_physical_dataset_official") is expected["source_market_state_physical_dataset_official"],
        "source_market_state_profile_id": profile_manifest.get("source_market_state_profile_id") == expected["source_market_state_profile_id"],
        "source_market_state_schema_version": profile_manifest.get("source_market_state_schema_version") == expected["source_market_state_schema_version"],
        "no_parquet_in_registry": not any(registry_dir.glob("*.parquet")),
    }
    for key, ok in checks.items():
        if not ok:
            failures.append(f"registry_invariant_failure:{key}")

    write_json(run_dir / "registry_invariant_validation_report.json", checks)

    validation_status = "CLOSED_PASS_WITH_RESTRICTIONS" if not failures else "BLOCKED_PROFILE_ARTIFACT_VALIDATION"
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "complete" if not failures else "blocked", "updated_at_utc": utc_now()})

    artifact_paths = {
        "pre_manifest": run_dir / "pre_manifest.json",
        "heartbeat": run_dir / "heartbeat.json",
        "registry_artifact_validation_report": run_dir / "registry_artifact_validation_report.csv",
        "registry_invariant_validation_report": run_dir / "registry_invariant_validation_report.json",
    }
    final_manifest = {
        "artifacts": {name: str(path) for name, path in artifact_paths.items()},
        "artifacts_sha256": {name: sha256_file(path) for name, path in artifact_paths.items()},
        "blocking_failures": failures,
        "candidate_event_state_records_copied": False,
        "completed_at_utc": utc_now(),
        "downstream_consumption": False,
        "event_detection_authorized": False,
        "event_state_materialization": False,
        "event_state_profile_artifact_validation": validation_status,
        "final_manifest_self_hash_policy": "not_recorded_to_avoid_self_referential_hash",
        "hard_validation_failures": len(failures),
        "next_allowed_gate": scope["next_allowed_gate"],
        "official_event_state_dataset_promotion": False,
        "official_event_state_parquet_files_written": 0,
        "official_event_state_profile_write": False,
        "production": False,
        "profile_id": scope["profile_id"],
        "registry_artifacts_checked": len(artifact_rows),
        "registry_dir": str(registry_dir),
        "registry_invariant_failures": sum(1 for ok in checks.values() if not ok),
        "registry_sha256_mismatches": sum(1 for row in artifact_rows if not row["sha256_match"]),
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "source_market_data_rows_read": 0,
        "started_at_utc": started_at,
        "status": "complete" if not failures else "blocked",
    }
    write_json(run_dir / "final_manifest.json", final_manifest)

    readout = f"""# Event State Profile Artifact Validation Readout v0.1

run_id = `{run_id}`
script_version = `{SCRIPT_VERSION}`

```text
event_state_profile_artifact_validation = {validation_status}
profile_id = {scope['profile_id']}
registry_artifacts_checked = {len(artifact_rows)}
registry_sha256_mismatches = {final_manifest['registry_sha256_mismatches']}
registry_invariant_failures = {final_manifest['registry_invariant_failures']}
hard_validation_failures = {final_manifest['hard_validation_failures']}
official_event_state_dataset_promotion = false
official_event_state_parquet_files_written = 0
candidate_event_state_records_copied = false
event_detection_authorized = false
source_market_data_rows_read = 0
production = false
downstream_consumption = false
next_allowed_gate = {scope['next_allowed_gate']}
```

The profile registry package is validated only if this gate closes pass with
restrictions. Operational dataset promotion, production, official parquet and
full-history/full-universe execution remain closed.
"""
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")
    root_readout_path.write_text(readout, encoding="utf-8")
    print(json.dumps(final_manifest, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
