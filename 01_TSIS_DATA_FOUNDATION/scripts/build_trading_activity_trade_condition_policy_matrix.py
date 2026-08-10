#!/usr/bin/env python3
"""Build the experimental Wake-up trade-condition policy matrix."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_CSV_NAME = "trading_activity_trade_condition_policy_matrix_candidate_v0_1.csv"
OUTPUT_MANIFEST_NAME = (
    "trading_activity_trade_condition_policy_matrix_candidate_v0_1.manifest.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized == "":
        return None
    raise ValueError(f"Unsupported boolean value: {value!r}")


def load_snapshot(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "id",
        "name",
        "type",
        "legacy",
        "consolidated_updates_high_low",
        "consolidated_updates_open_close",
        "consolidated_updates_volume",
    }
    missing = required.difference(rows[0].keys() if rows else set())
    if missing:
        raise ValueError(f"Snapshot is missing required columns: {sorted(missing)}")

    ids = [int(row["id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Snapshot contains duplicate condition IDs")
    return sorted(rows, key=lambda row: int(row["id"]))


def load_policy(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("status") != "EXPERIMENTAL_CANDIDATE_NOT_CANONICAL":
        raise ValueError("Policy status does not permit candidate matrix generation")
    return policy


def build_matrix(
    snapshot_rows: list[dict[str, str]], policy: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rules = {
        int(rule["condition_id"]): rule for rule in policy.get("condition_rules", [])
    }
    if len(rules) != len(policy.get("condition_rules", [])):
        raise ValueError("Policy contains duplicate condition IDs")

    snapshot_by_id = {int(row["id"]): row for row in snapshot_rows}
    missing_policy_ids = sorted(set(rules).difference(snapshot_by_id))
    if missing_policy_ids:
        raise ValueError(
            f"Policy references IDs absent from snapshot: {missing_policy_ids}"
        )

    matrix: list[dict[str, Any]] = []
    for source in snapshot_rows:
        condition_id = int(source["id"])
        rule = rules.get(condition_id)
        if rule:
            if source["name"] != rule["expected_name"]:
                raise ValueError(
                    "Condition name mismatch for ID "
                    f"{condition_id}: {source['name']!r} != {rule['expected_name']!r}"
                )
            review_state = "CANDIDATE_REVIEWED_FOR_PILOT"
            semantic_class = rule["semantic_class"]
            effects = {
                key: rule[key]
                for key in (
                    "activity_event_effect",
                    "share_volume_effect",
                    "dollar_volume_effect",
                    "causal_arrival_effect",
                    "price_path_effect",
                )
            }
            reason_code = rule["reason_code"]
            confidence = rule["policy_confidence"]
        else:
            review_state = "KNOWN_BUT_UNREVIEWED_FAIL_CLOSED"
            semantic_class = "UNREVIEWED_CURRENT_SNAPSHOT_CONDITION"
            effects = {
                "activity_event_effect": "REVIEW_REQUIRED",
                "share_volume_effect": "REVIEW_REQUIRED",
                "dollar_volume_effect": "REVIEW_REQUIRED",
                "causal_arrival_effect": "REVIEW_REQUIRED",
                "price_path_effect": "REVIEW_REQUIRED",
            }
            reason_code = "KNOWN_CONDITION_REQUIRES_SEMANTIC_REVIEW"
            confidence = "NOT_REVIEWED"

        matrix.append(
            {
                "condition_id": condition_id,
                "condition_name": source["name"],
                "condition_type": source["type"],
                "legacy": parse_bool(source["legacy"]),
                "provider_consolidated_updates_volume": parse_bool(
                    source["consolidated_updates_volume"]
                ),
                "provider_consolidated_updates_high_low": parse_bool(
                    source["consolidated_updates_high_low"]
                ),
                "provider_consolidated_updates_open_close": parse_bool(
                    source["consolidated_updates_open_close"]
                ),
                "policy_review_state": review_state,
                "semantic_class": semantic_class,
                **effects,
                "reason_code": reason_code,
                "policy_confidence": confidence,
                "historical_temporality_state": policy[
                    "historical_temporality_state"
                ],
                "policy_id": policy["policy_id"],
            }
        )

    reviewed = [
        row
        for row in matrix
        if row["policy_review_state"] == "CANDIDATE_REVIEWED_FOR_PILOT"
    ]
    summary = {
        "condition_count": len(matrix),
        "candidate_reviewed_condition_count": len(reviewed),
        "known_but_unreviewed_condition_count": len(matrix) - len(reviewed),
        "candidate_reviewed_condition_ids": [row["condition_id"] for row in reviewed],
        "all_policy_ids_present_in_snapshot": not missing_policy_ids,
    }
    return matrix, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition-snapshot", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    snapshot_rows = load_snapshot(args.condition_snapshot)
    policy = load_policy(args.policy)
    matrix, summary = build_matrix(snapshot_rows, policy)

    output_csv = args.output_dir / OUTPUT_CSV_NAME
    output_manifest = args.output_dir / OUTPUT_MANIFEST_NAME
    write_csv(output_csv, matrix)

    manifest = {
        "artifact_id": "trading_activity_trade_condition_policy_matrix_candidate",
        "artifact_version": "v0_1",
        "artifact_status": "EXPERIMENTAL_CANDIDATE_NOT_CANONICAL",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "condition_snapshot_path": str(args.condition_snapshot.resolve()),
        "condition_snapshot_sha256": sha256_file(args.condition_snapshot),
        "policy_path": str(args.policy.resolve()),
        "policy_sha256": sha256_file(args.policy),
        "output_csv_path": str(output_csv.resolve()),
        "output_csv_sha256": sha256_file(output_csv),
        "summary": summary,
        "full_condition_semantic_review_complete": False,
        "canonical_promotion_authorized": False,
    }
    write_json(output_manifest, manifest)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
