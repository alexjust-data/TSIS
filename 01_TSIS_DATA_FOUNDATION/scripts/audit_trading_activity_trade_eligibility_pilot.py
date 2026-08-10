#!/usr/bin/env python3
"""Apply the candidate trade-eligibility policy to a governed RTH pilot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from evaluate_trading_activity_trade_eligibility import (
    evaluate_trade,
    load_condition_matrix,
)


PER_FILE_NAME = "trading_activity_trade_eligibility_pilot_per_file_v0_1.csv"
CONDITION_COUNTS_NAME = "trading_activity_trade_eligibility_pilot_conditions_v0_1.csv"
MANIFEST_NAME = "trading_activity_trade_eligibility_pilot_v0_1.manifest.json"

COUNT_FIELDS = (
    "physical_row_count",
    "evaluated_row_count",
    "activity_eligible_count",
    "activity_ineligible_count",
    "activity_unknown_fail_closed_count",
    "volume_eligible_count",
    "notional_eligible_count",
    "causal_arrival_eligible_count",
    "price_forming_eligible_count",
    "exact_duplicate_flag_count",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def duplicate_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("timestamp"),
        row.get("price"),
        row.get("size"),
        row.get("exchange"),
        tuple(row.get("conditions") or []),
    )


def empty_counts() -> dict[str, int]:
    return {field: 0 for field in COUNT_FIELDS if field != "physical_row_count"}


def audit_file(
    sidecar: dict[str, str], matrix: dict[int, dict[str, str]]
) -> tuple[dict[str, Any], Counter[int], Counter[str]]:
    status = sidecar["acquisition_status"]
    result: dict[str, Any] = {
        "task_key": sidecar["task_key"],
        "ticker": sidecar["ticker"],
        "trading_date": sidecar["trading_date"],
        "acquisition_status": status,
        "coverage_gate_state": sidecar["coverage_gate_state"],
        "physical_row_count": int(sidecar["physical_row_count"] or 0),
        **empty_counts(),
    }
    if status == "DOWNLOADED_EMPTY":
        result["file_policy_state"] = "OBSERVED_ZERO_WITH_RESTRICTIONS"
        return result, Counter(), Counter()
    if status != "DOWNLOADED_OK":
        result["file_policy_state"] = "SOURCE_NOT_EVALUABLE"
        return result, Counter(), Counter(["SOURCE_NOT_EVALUABLE"])

    columns = [
        "ticker",
        "date",
        "timestamp",
        "price",
        "size",
        "exchange",
        "conditions",
    ]
    physical_path = Path(sidecar["active_physical_file"])
    rows = pq.ParquetFile(physical_path).read(columns=columns).to_pylist()
    if len(rows) != result["physical_row_count"]:
        raise ValueError(
            f"Physical row-count drift for {sidecar['task_key']}: "
            f"{len(rows)} != {result['physical_row_count']}"
        )

    row_states: Counter[str] = Counter()
    axis_counts: Counter[str] = Counter()
    condition_counts: Counter[int] = Counter()
    reason_counts: Counter[str] = Counter()
    seen: set[tuple[Any, ...]] = set()
    source_available = sidecar["coverage_gate_state"] == "PASS_WITH_RESTRICTIONS"

    for row in rows:
        condition_counts.update(int(value) for value in (row.get("conditions") or []))
        key = duplicate_key(row)
        duplicate = key in seen
        seen.add(key)
        result["exact_duplicate_flag_count"] += int(duplicate)

        decision = evaluate_trade(
            row,
            matrix,
            in_rth=sidecar["session"] == "market",
            source_available=source_available,
            exact_duplicate_research_flag=duplicate,
        )
        row_states[decision["trade_row_policy_state"]] += 1
        reason_counts.update(decision["eligibility_reason_codes"])
        for axis in (
            "trade_volume_eligibility_state",
            "trade_notional_eligibility_state",
            "trade_causal_arrival_eligibility_state",
            "trade_price_forming_eligibility_state",
        ):
            axis_counts[axis] += int(decision[axis] == "ELIGIBLE_WITH_RESTRICTIONS")

    result.update(
        {
            "evaluated_row_count": len(rows),
            "activity_eligible_count": row_states["ELIGIBLE_WITH_RESTRICTIONS"],
            "activity_ineligible_count": row_states["INELIGIBLE"],
            "activity_unknown_fail_closed_count": row_states["UNKNOWN_FAIL_CLOSED"],
            "volume_eligible_count": axis_counts["trade_volume_eligibility_state"],
            "notional_eligible_count": axis_counts["trade_notional_eligibility_state"],
            "causal_arrival_eligible_count": axis_counts[
                "trade_causal_arrival_eligibility_state"
            ],
            "price_forming_eligible_count": axis_counts[
                "trade_price_forming_eligibility_state"
            ],
            "file_policy_state": (
                "UNKNOWN_FAIL_CLOSED_PRESENT"
                if row_states["UNKNOWN_FAIL_CLOSED"]
                else "PASS_WITH_RESTRICTIONS"
            ),
        }
    )
    return result, condition_counts, reason_counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", required=True, type=Path)
    parser.add_argument("--matrix", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    sidecars = sorted(read_csv(args.sidecar), key=lambda row: row["task_key"])
    matrix = load_condition_matrix(args.matrix)
    per_file: list[dict[str, Any]] = []
    conditions: Counter[int] = Counter()
    reasons: Counter[str] = Counter()
    for sidecar in sidecars:
        row, file_conditions, file_reasons = audit_file(sidecar, matrix)
        per_file.append(row)
        conditions.update(file_conditions)
        reasons.update(file_reasons)

    per_file_path = args.output_dir / PER_FILE_NAME
    conditions_path = args.output_dir / CONDITION_COUNTS_NAME
    manifest_path = args.output_dir / MANIFEST_NAME
    write_csv(per_file_path, per_file, list(per_file[0].keys()))
    condition_rows = [
        {
            "condition_id": condition_id,
            "observed_row_count": count,
            "policy_review_state": matrix.get(condition_id, {}).get(
                "policy_review_state", "UNKNOWN_CONDITION"
            ),
            "condition_name": matrix.get(condition_id, {}).get(
                "condition_name", "UNKNOWN"
            ),
        }
        for condition_id, count in sorted(conditions.items())
    ]
    write_csv(
        conditions_path,
        condition_rows,
        ["condition_id", "observed_row_count", "policy_review_state", "condition_name"],
    )

    totals: Counter[str] = Counter()
    for row in per_file:
        totals.update({field: int(row[field]) for field in COUNT_FIELDS})
    evaluated = totals["evaluated_row_count"]
    manifest = {
        "artifact_id": "trading_activity_trade_eligibility_pilot",
        "artifact_version": "v0_1",
        "artifact_status": "EXPERIMENTAL_EVIDENCE_NOT_CANONICAL",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sidecar_path": str(args.sidecar.resolve()),
        "sidecar_sha256": sha256_file(args.sidecar),
        "matrix_path": str(args.matrix.resolve()),
        "matrix_sha256": sha256_file(args.matrix),
        "task_count": len(per_file),
        "downloaded_ok_task_count": sum(
            row["acquisition_status"] == "DOWNLOADED_OK" for row in per_file
        ),
        "downloaded_empty_task_count": sum(
            row["acquisition_status"] == "DOWNLOADED_EMPTY" for row in per_file
        ),
        "totals": dict(totals),
        "activity_eligible_fraction": (
            totals["activity_eligible_count"] / evaluated if evaluated else None
        ),
        "unknown_fail_closed_fraction": (
            totals["activity_unknown_fail_closed_count"] / evaluated
            if evaluated
            else None
        ),
        "observed_condition_ids": sorted(conditions),
        "all_observed_condition_ids_candidate_reviewed": all(
            matrix.get(condition_id, {}).get("policy_review_state")
            == "CANDIDATE_REVIEWED_FOR_PILOT"
            for condition_id in conditions
        ),
        "reason_code_counts": dict(sorted(reasons.items())),
        "per_file_output_path": str(per_file_path.resolve()),
        "per_file_output_sha256": sha256_file(per_file_path),
        "condition_output_path": str(conditions_path.resolve()),
        "condition_output_sha256": sha256_file(conditions_path),
        "full_universe_claim": False,
        "stratified_sample_claim": False,
        "binding_a_execution_authorized_by_this_artifact": False,
        "canonical_promotion_authorized": False,
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
