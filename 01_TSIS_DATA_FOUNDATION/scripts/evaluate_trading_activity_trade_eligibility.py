#!/usr/bin/env python3
"""Evaluate legacy RTH trade rows against the candidate condition policy."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


EFFECT_FIELDS = (
    "activity_event_effect",
    "share_volume_effect",
    "dollar_volume_effect",
    "causal_arrival_effect",
    "price_path_effect",
)

OUTPUT_STATE_FIELDS = {
    "activity_event_effect": "trade_activity_eligibility_state",
    "share_volume_effect": "trade_volume_eligibility_state",
    "dollar_volume_effect": "trade_notional_eligibility_state",
    "causal_arrival_effect": "trade_causal_arrival_eligibility_state",
    "price_path_effect": "trade_price_forming_eligibility_state",
}


def load_condition_matrix(path: Path) -> dict[int, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matrix = {int(row["condition_id"]): row for row in rows}
    if len(matrix) != len(rows):
        raise ValueError("Condition policy matrix contains duplicate IDs")
    return matrix


def _valid_date(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if isinstance(value, date):
        return True
    if isinstance(value, str):
        try:
            date.fromisoformat(value[:10])
            return True
        except ValueError:
            return False
    return False


def _valid_timestamp(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
    return False


def _positive_finite(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0


def _normalize_conditions(value: Any) -> list[int]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError("conditions must be a list, tuple or null")
    normalized: list[int] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int):
            raise ValueError("condition IDs must be integers")
        normalized.append(item)
    return normalized


def _combine_effects(effects: Iterable[str]) -> str:
    values = set(effects)
    if "DENY" in values:
        return "DENY"
    if "REVIEW_REQUIRED" in values:
        return "REVIEW_REQUIRED"
    if "ALLOW" in values:
        return "ALLOW"
    if values == {"NO_RESTRICTION"}:
        return "ALLOW"
    raise ValueError(f"Unsupported effect combination: {sorted(values)}")


def _fail_result(reason_codes: list[str], state: str = "INELIGIBLE") -> dict[str, Any]:
    result: dict[str, Any] = {
        field: state for field in OUTPUT_STATE_FIELDS.values()
    }
    result.update(
        {
            "trade_row_policy_state": state,
            "eligibility_reason_codes": sorted(set(reason_codes)),
            "duplicate_research_flag": "NOT_EVALUATED",
            "revision_mode": "RECONCILED_FINAL_ONLY",
            "quality_state": "DEGRADED",
        }
    )
    return result


def evaluate_trade(
    row: dict[str, Any],
    matrix: dict[int, dict[str, str]],
    *,
    in_rth: bool,
    source_available: bool,
    exact_duplicate_research_flag: bool = False,
) -> dict[str, Any]:
    hard_failures: list[str] = []
    if not str(row.get("ticker", "")).strip():
        hard_failures.append("INVALID_TICKER")
    if not _valid_date(row.get("date")):
        hard_failures.append("INVALID_DATE")
    if not _valid_timestamp(row.get("timestamp")):
        hard_failures.append("INVALID_TIMESTAMP")
    if not _positive_finite(row.get("price")):
        hard_failures.append("NONPOSITIVE_OR_INVALID_PRICE")
    if not _positive_finite(row.get("size")):
        hard_failures.append("NONPOSITIVE_OR_INVALID_SIZE")

    exchange = row.get("exchange")
    if exchange is not None and (
        isinstance(exchange, bool) or not isinstance(exchange, int) or exchange < 0
    ):
        hard_failures.append("INVALID_EXCHANGE")
    if not in_rth:
        hard_failures.append("OUTSIDE_RTH_SCOPE")
    if not source_available:
        hard_failures.append("SOURCE_UNAVAILABLE")

    try:
        conditions = _normalize_conditions(row.get("conditions"))
    except ValueError:
        hard_failures.append("UNPARSABLE_CONDITIONS")
        conditions = []

    if hard_failures:
        return _fail_result(hard_failures)

    reason_codes: list[str] = []
    if exchange is None:
        reason_codes.append("EXPLICIT_UNKNOWN_EXCHANGE")

    if not conditions:
        combined = {field: "ALLOW" for field in EFFECT_FIELDS}
        reason_codes.append("NO_SPECIAL_CONDITION_REPORTED_LEGACY")
    else:
        condition_rows: list[dict[str, str]] = []
        unknown_ids: list[int] = []
        unreviewed_ids: list[int] = []
        for condition_id in conditions:
            condition = matrix.get(condition_id)
            if condition is None:
                unknown_ids.append(condition_id)
                continue
            if condition["policy_review_state"] != "CANDIDATE_REVIEWED_FOR_PILOT":
                unreviewed_ids.append(condition_id)
            condition_rows.append(condition)

        if unknown_ids:
            reason_codes.extend(
                f"UNKNOWN_CONDITION_{condition_id}" for condition_id in unknown_ids
            )
            return _fail_result(reason_codes, state="UNKNOWN_FAIL_CLOSED")
        if unreviewed_ids:
            reason_codes.extend(
                f"UNREVIEWED_CONDITION_{condition_id}" for condition_id in unreviewed_ids
            )
            return _fail_result(reason_codes, state="UNKNOWN_FAIL_CLOSED")

        combined = {
            field: _combine_effects(condition[field] for condition in condition_rows)
            for field in EFFECT_FIELDS
        }
        reason_codes.extend(condition["reason_code"] for condition in condition_rows)

    result: dict[str, Any] = {}
    for effect_field, output_field in OUTPUT_STATE_FIELDS.items():
        result[output_field] = (
            "ELIGIBLE_WITH_RESTRICTIONS"
            if combined[effect_field] == "ALLOW"
            else "INELIGIBLE"
        )

    result["trade_row_policy_state"] = result[
        "trade_activity_eligibility_state"
    ]
    result["eligibility_reason_codes"] = sorted(set(reason_codes))
    result["duplicate_research_flag"] = (
        "EXACT_DUPLICATE_RESEARCH_FLAG"
        if exact_duplicate_research_flag
        else "NO_EXACT_DUPLICATE_FLAG"
    )
    result["revision_mode"] = "RECONCILED_FINAL_ONLY"
    result["quality_state"] = (
        "DEGRADED" if exchange is None else "OBSERVED_WITH_RESTRICTIONS"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True, type=Path)
    parser.add_argument("--row-json", required=True)
    parser.add_argument("--in-rth", action="store_true")
    parser.add_argument("--source-available", action="store_true")
    args = parser.parse_args()

    matrix = load_condition_matrix(args.matrix)
    row = json.loads(args.row_json)
    result = evaluate_trade(
        row,
        matrix,
        in_rth=args.in_rth,
        source_available=args.source_available,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
