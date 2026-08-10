from __future__ import annotations

from datetime import date
from typing import Any


def align_daily_os_to_splits(
    daily_rows: list[dict[str, Any]], split_rows: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    primary_splits = sorted(
        (
            row
            for row in split_rows
            if row.get("action_type") == "split"
            and row.get("source_system") == "reference"
            and bool(row.get("within_instrument_valid_window"))
        ),
        key=lambda row: str(row["action_date"]),
    )
    aligned = []
    for source in daily_rows:
        row = dict(source)
        session = date.fromisoformat(str(row["session_date"])[:10])
        measurement = (
            date.fromisoformat(str(row["anchor_measurement_at"])[:10])
            if row.get("anchor_measurement_at")
            else None
        )
        factor = 1.0
        applied_ids = []
        for split in primary_splits:
            effective = date.fromisoformat(str(split["action_date"])[:10])
            if measurement is not None and measurement < effective <= session:
                factor *= float(split["split_ratio"])
                applied_ids.append(split["corporate_action_id"])
        row["split_alignment_factor"] = factor
        row["applied_corporate_action_ids"] = applied_ids
        if factor != 1.0 and row.get("shares_outstanding_estimate_as_known") is not None:
            row["shares_outstanding_estimate_as_known"] = (
                float(row["shares_outstanding_estimate_as_known"]) * factor
            )
            row["os_state"] = "OS_SPLIT_TRANSFORMED_STALE_ANCHOR"
        aligned.append(row)
    transformed = sum(row["split_alignment_factor"] != 1.0 for row in aligned)
    return aligned, {
        "status": "PASS_WITH_RESTRICTIONS",
        "daily_rows": len(aligned),
        "primary_split_rows": len(primary_splits),
        "split_transformed_rows": transformed,
        "secondary_split_rows_ignored": sum(
            row.get("action_type") == "split" and row.get("source_system") != "reference"
            for row in split_rows
        ),
    }
