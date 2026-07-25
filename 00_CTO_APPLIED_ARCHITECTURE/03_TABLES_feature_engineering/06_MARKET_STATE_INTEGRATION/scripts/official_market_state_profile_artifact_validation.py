#!/usr/bin/env python
"""Validate the promoted core-four Market State profile registry package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "official_market_state_profile_artifact_validation_v0_1"
DEFAULT_RUN_PREFIX = "official_market_state_profile_artifact_validation_v0_1"


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
    registry_dir = (base_dir / scope["registry_path"]).resolve()
    failures: list[str] = []

    write_json(run_dir / "pre_manifest.json", {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "registry_dir": str(registry_dir),
        "authority_boundary": scope["authority_boundary"],
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
            "path": str(path),
            "exists": path.exists(),
            "expected_sha256": item["sha256"],
            "observed_sha256": observed,
            "sha256_match": observed == item["sha256"],
            "bytes": path.stat().st_size if path.exists() else 0,
        })

    with (run_dir / "registry_artifact_validation_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(artifact_rows[0].keys()))
        writer.writeheader()
        writer.writerows(artifact_rows)

    profile_manifest = load_json(registry_dir / "PROFILE_MANIFEST.json") if (registry_dir / "PROFILE_MANIFEST.json").exists() else {}
    evidence_manifest = load_json(registry_dir / "EVIDENCE_MANIFEST.json") if (registry_dir / "EVIDENCE_MANIFEST.json").exists() else {}
    schema_contract = load_json(registry_dir / "PHYSICAL_SCHEMA_CONTRACT.json") if (registry_dir / "PHYSICAL_SCHEMA_CONTRACT.json").exists() else {}
    expected = scope["expected_registry_invariants"]

    checks = {
        "profile_status": profile_manifest.get("status") == expected["profile_status"],
        "profile_classification": profile_manifest.get("profile_classification") == expected["profile_classification"],
        "source_physical_profile_id": profile_manifest.get("source_physical_profile_id") == expected["source_physical_profile_id"],
        "schema_version": schema_contract.get("state_schema_version") == expected["state_schema_version"],
        "complete_tsis_market_state": profile_manifest.get("complete_tsis_market_state") is expected["complete_tsis_market_state"],
        "required_information_objects": len(profile_manifest.get("required_information_objects", [])) == expected["required_information_objects"],
        "physical_schema_column_count": schema_contract.get("column_count") == expected["physical_schema_column_count"],
        "candidate_parquet_reference_only": evidence_manifest.get("candidate_parquet_reference_only") is expected["candidate_parquet_reference_only"],
        "candidate_parquet_copied": evidence_manifest.get("candidate_parquet_copied") is expected["candidate_parquet_copied"],
        "official_market_state_authorized": profile_manifest.get("official_market_state_authorized") is expected["official_market_state_authorized"],
        "official_parquet_written": schema_contract.get("official_parquet_written") is expected["official_parquet_written"],
        "downstream_consumption_authorized": profile_manifest.get("downstream_consumption_authorized") is expected["downstream_consumption_authorized"],
        "production_builder_authorized": profile_manifest.get("production_builder_authorized") is expected["production_builder_authorized"],
        "no_parquet_in_registry": not any(registry_dir.glob("*.parquet")),
    }
    for key, ok in checks.items():
        if not ok:
            failures.append(f"registry_invariant_failure:{key}")

    write_json(run_dir / "registry_invariant_validation_report.json", checks)

    validation_status = "CLOSED_PASS_WITH_RESTRICTIONS" if not failures else "BLOCKED_PROFILE_ARTIFACT_VALIDATION"
    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "status": "complete" if not failures else "blocked",
        "official_market_state_profile_artifact_validation": validation_status,
        "profile_id": scope["profile_id"],
        "registry_dir": str(registry_dir),
        "registry_artifacts_checked": len(artifact_rows),
        "registry_sha256_mismatches": sum(1 for row in artifact_rows if not row["sha256_match"]),
        "registry_invariant_failures": sum(1 for ok in checks.values() if not ok),
        "blocking_failures": failures,
        "hard_validation_failures": len(failures),
        "official_market_state_authorized": False,
        "official_parquet_files_written": 0,
        "candidate_parquet_copied": False,
        "source_market_data_rows_read": 0,
        "next_allowed_gate": scope["next_allowed_gate"],
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": final_manifest["status"], "updated_at_utc": utc_now()})

    readout = f"""# Official Market State Profile Artifact Validation Readout v0.1

run_id = `{run_id}`
script_version = `{SCRIPT_VERSION}`

```text
official_market_state_profile_artifact_validation = {validation_status}
profile_id = {scope['profile_id']}
registry_artifacts_checked = {len(artifact_rows)}
registry_sha256_mismatches = {final_manifest['registry_sha256_mismatches']}
registry_invariant_failures = {final_manifest['registry_invariant_failures']}
hard_validation_failures = {final_manifest['hard_validation_failures']}
official_market_state_authorized = false
official_parquet_files_written = 0
candidate_parquet_copied = false
source_market_data_rows_read = 0
next_allowed_gate = {scope['next_allowed_gate']}
```

The profile registry package is validated only if this gate closes pass with
restrictions. Operational consumption, production, official parquet and
full-history/full-universe execution remain closed.
"""
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")
    print(json.dumps(final_manifest, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
