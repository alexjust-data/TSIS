#!/usr/bin/env python
"""Review bounded core-four Market State evidence for official-profile readiness.

This gate is review-only. It reads accepted artifacts and emits a decision, but
it never writes official parquet, copies candidate parquet, promotes datasets or
opens downstream consumption.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "official_market_state_candidate_promotion_review_v0_1"
DEFAULT_RUN_PREFIX = "official_market_state_candidate_promotion_review_v0_1"


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


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig") as fh:
        return sum(1 for line in fh if line.strip())


def parquet_rows(path: Path) -> int:
    try:
        import pyarrow.parquet as pq
    except Exception as exc:  # pragma: no cover - environment dependency
        raise RuntimeError(f"pyarrow is required to inspect parquet metadata: {exc}") from exc
    return pq.ParquetFile(path).metadata.num_rows


def fail_count(payload: dict[str, Any], keys: list[str]) -> int:
    total = 0
    for key in keys:
        value = payload.get(key, 0)
        if isinstance(value, bool):
            total += 0 if not value else 1
        elif isinstance(value, (int, float)):
            total += int(value)
    return total


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
    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "started_at_utc": started_at,
        "authority_boundary": scope["authority_boundary"],
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "started", "updated_at_utc": utc_now()})

    hard_failures: list[str] = []
    inventory_rows: list[dict[str, Any]] = []
    observed_counts: dict[str, int | None] = {}

    for artifact in scope["required_artifacts"]:
        path = (base_dir / artifact["path"]).resolve()
        exists = path.exists()
        observed_sha = sha256_file(path) if exists else None
        sha_match = exists and observed_sha == artifact["sha256"]
        row_count = None
        if exists and path.suffix == ".jsonl":
            row_count = count_jsonl(path)
        elif exists and path.suffix == ".parquet":
            row_count = parquet_rows(path)
        observed_counts[artifact["artifact_id"]] = row_count

        expected_count = artifact.get("expected_records", artifact.get("expected_rows"))
        count_match = expected_count is None or row_count == expected_count
        if not exists:
            hard_failures.append(f"missing_accepted_run_artifact:{artifact['artifact_id']}")
        if exists and not sha_match:
            hard_failures.append(f"fingerprint_mismatch:{artifact['artifact_id']}")
        if exists and not count_match:
            hard_failures.append(f"record_or_row_count_mismatch:{artifact['artifact_id']}")

        inventory_rows.append({
            "artifact_id": artifact["artifact_id"],
            "path": str(path),
            "exists": exists,
            "expected_sha256": artifact["sha256"],
            "observed_sha256": observed_sha or "",
            "sha256_match": sha_match,
            "expected_count": expected_count if expected_count is not None else "",
            "observed_count": row_count if row_count is not None else "",
            "count_match": count_match,
        })

    builder_manifest = load_json(base_dir / scope["required_artifacts"][1]["path"])
    integration_manifest = load_json(base_dir / scope["required_artifacts"][3]["path"])
    materialization_manifest = load_json(base_dir / scope["required_artifacts"][5]["path"])
    physical_manifest = load_json(base_dir / scope["required_artifacts"][6]["path"])

    invariants = scope["required_invariants"]
    observed = {
        "resolution_records": observed_counts.get("scale_c_builder_resolution_records"),
        "integrated_candidate_records": integration_manifest.get("candidate_records_emitted"),
        "physical_candidate_rows": physical_manifest.get("output_physical_rows"),
        "value_mappings_checked": physical_manifest.get("value_mappings_checked"),
        "semantic_rebuild_field_comparisons": physical_manifest.get("semantic_rebuild_field_comparisons"),
        "hard_validation_failures": (
            int(builder_manifest.get("hard_validation_failures", 0))
            + int(integration_manifest.get("hard_validation_failures", 0))
            + int(materialization_manifest.get("hard_validation_failures", 0))
            + int(physical_manifest.get("hard_validation_failures", 0))
        ),
        "source_market_data_rows_read_during_review": 0,
        "official_parquet_files_written": 0,
        "dataset_promotion_executed": False,
    }

    for key, expected in invariants.items():
        if observed.get(key) != expected:
            hard_failures.append(f"invariant_mismatch:{key}:expected={expected}:observed={observed.get(key)}")

    blocking_metric_failures = fail_count(integration_manifest, [
        "failed_context_consistency",
        "failed_contract_or_determinism",
        "future_leaks",
        "blocked_values_admitted",
        "sample_fingerprint_mismatches",
        "surface_fingerprint_mismatches",
    ]) + fail_count(materialization_manifest, [
        "fingerprint_mismatches",
        "semantic_equality_failures",
        "roundtrip_failures",
        "type_coercion_failures",
        "rejected_contexts_materialized_as_rows",
    ]) + fail_count(physical_manifest, [
        "authority_failures",
        "source_to_physical_value_mismatches",
        "context_fingerprint_mismatches",
        "state_output_fingerprint_mismatches",
        "semantic_rebuild_differences",
        "rejected_contexts_in_parquet",
    ])
    if blocking_metric_failures:
        hard_failures.append(f"blocking_validation_metric_failures:{blocking_metric_failures}")

    decision = "APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS" if not hard_failures else "BLOCKED_PENDING_EVIDENCE"
    next_gate = scope["next_allowed_gate_if_approved"] if not hard_failures else scope["next_allowed_gate_if_blocked"]

    with (run_dir / "evidence_inventory_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(inventory_rows[0].keys()))
        writer.writeheader()
        writer.writerows(inventory_rows)

    restriction_rows = [
        {"restriction": key, "value": value, "blocking": False}
        for key, value in scope["scope_restrictions"].items()
    ]
    with (run_dir / "promotion_review_restrictions_report.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["restriction", "value", "blocking"])
        writer.writeheader()
        writer.writerows(restriction_rows)

    decision_payload = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "reviewed_profile_id": scope["reviewed_object"]["profile_id"],
        "decision": decision,
        "blocking_failures": hard_failures,
        "observed_invariants": observed,
        "scope_restrictions_preserved": scope["scope_restrictions"],
        "authority_boundary_preserved": scope["authority_boundary"],
        "next_allowed_gate": next_gate,
        "official_profile_promotion_executed": False,
        "official_market_state_authorized": False,
        "official_parquet_files_written": 0,
        "source_market_data_rows_read": 0,
    }
    write_json(run_dir / "promotion_review_decision.json", decision_payload)

    final_manifest = {
        **decision_payload,
        "status": "complete",
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "evidence_artifacts_checked": len(inventory_rows),
        "hash_mismatches": sum(1 for row in inventory_rows if not row["sha256_match"]),
        "count_mismatches": sum(1 for row in inventory_rows if not row["count_match"]),
        "hard_validation_failures": len(hard_failures),
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "stage": "complete", "updated_at_utc": utc_now()})

    readout = f"""# Official Market State Candidate Promotion Review Readout v0.1

run_id = `{run_id}`
script_version = `{SCRIPT_VERSION}`

```text
official_market_state_candidate_promotion_review = {decision}
reviewed_profile_id = {scope["reviewed_object"]["profile_id"]}
evidence_artifacts_checked = {len(inventory_rows)}
resolution_records = {observed["resolution_records"]}
integrated_candidate_records = {observed["integrated_candidate_records"]}
physical_candidate_rows = {observed["physical_candidate_rows"]}
value_mappings_checked = {observed["value_mappings_checked"]}
semantic_rebuild_field_comparisons = {observed["semantic_rebuild_field_comparisons"]}
hash_mismatches = {final_manifest["hash_mismatches"]}
count_mismatches = {final_manifest["count_mismatches"]}
hard_validation_failures = {final_manifest["hard_validation_failures"]}
official_profile_promotion_executed = false
official_market_state_authorized = false
official_parquet_files_written = 0
source_market_data_rows_read = 0
next_allowed_gate = {next_gate}
```

The review approves the bounded core-four intraday profile candidate for a
separate promotion authorization only if the decision is
`APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS`. It does not promote
an official table, copy parquet, authorize production, authorize downstream
consumption or open full-history/full-universe execution.
"""
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")
    print(json.dumps(final_manifest, indent=2, sort_keys=True))
    return 0 if not hard_failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
