"""Authoritative target-only cardinality and membership contract for TA Stage-8."""

from __future__ import annotations

import math
from collections import Counter
from datetime import date, datetime
from typing import Any, Iterable, Mapping

CONTRACT_ID = "trading_activity_stage8_target_only_contract_v0_2"

FAMILY_MULTIPLIERS: dict[str, int] = {
    "current_state": 5,
    "multiscale_contrast": 2,
    "pit_baseline_and_surprise": 15,
}

PHYSICAL_FAMILY_KEYS = tuple(FAMILY_MULTIPLIERS)

COMMON_REQUIRED_COLUMNS = (
    "instrument_id",
    "ticker",
    "session_date",
    "decision_timestamp",
    "binding_id",
    "feature_spec_id",
    "feature_version",
    "scope_id",
    "source_dataset_id",
    "coverage_state",
    "calculation_state",
    "future_window_used",
    "feature_input_max_available_at",
    "lineage_manifest_id",
)

FAMILY_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "current_state": ("window_seconds",),
    "multiscale_contrast": (
        "short_window_seconds",
        "long_window_seconds",
        "pair_id",
    ),
    "pit_baseline_and_surprise": (
        "window_seconds",
        "baseline_candidate_id",
        "first_reference_date",
        "last_reference_date",
        "baseline_input_max_available_at",
    ),
}


def _exact_int(value: Any, field: str) -> int:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} is not numeric: {value!r}") from exc
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError(f"{field} must be a finite integer: {value!r}")
    return int(numeric)


def normalized_session_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value)
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError as exc:
        raise ValueError(f"Invalid session_date: {value!r}") from exc


def exact_target_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row["block_id"]),
        str(row["instrument_id"]),
        str(row["ticker_as_of_session"]),
        normalized_session_date(row["session_date"]),
    )


def decision_points(row: Mapping[str, Any]) -> int:
    source_seconds = _exact_int(row["decision_seconds"], "decision_seconds")
    points = source_seconds - 1
    if points <= 0:
        raise ValueError(
            f"Open/close-exclusive decision grid must be positive: {source_seconds}"
        )
    if "session_minutes" in row and row["session_minutes"] is not None:
        minutes = float(row["session_minutes"])
        if not math.isfinite(minutes) or int(round(minutes * 60)) != source_seconds:
            raise ValueError(
                "decision_seconds does not equal session_minutes * 60: "
                f"{source_seconds} vs {minutes}"
            )
    return points


def expected_physical_counts(row: Mapping[str, Any]) -> dict[str, int]:
    points = decision_points(row)
    return {
        family: points * multiplier
        for family, multiplier in FAMILY_MULTIPLIERS.items()
    }


def aggregate_contract(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    physical: Counter[str] = Counter()
    target_keys: set[tuple[str, str, str, str]] = set()
    decision_points_total = 0
    early_close_targets = 0
    count = 0
    for row in rows:
        count += 1
        key = exact_target_key(row)
        if key in target_keys:
            raise ValueError(f"Duplicate exact target key: {key}")
        target_keys.add(key)
        points = decision_points(row)
        decision_points_total += points
        early_close_targets += int(bool(row.get("is_early_close", False)))
        physical.update(expected_physical_counts(row))
    if count == 0:
        raise ValueError("Target set is empty")
    return {
        "contract_id": CONTRACT_ID,
        "physical_family_row_counts": {
            family: int(physical[family]) for family in PHYSICAL_FAMILY_KEYS
        },
        "metadata_scalars": {
            "target_count": count,
            "partition_count": count * len(PHYSICAL_FAMILY_KEYS),
            "decision_points_total": decision_points_total,
            "window_count": 5,
            "short_long_pair_count": 2,
            "baseline_candidate_count": 3,
            "early_close_target_count": early_close_targets,
        },
    }


def assert_physical_counts(
    actual: Mapping[str, Any], expected: Mapping[str, Any]
) -> None:
    actual_keys = tuple(actual.keys())
    expected_keys = tuple(expected.keys())
    if set(actual_keys) != set(PHYSICAL_FAMILY_KEYS):
        raise AssertionError(
            "Actual physical-count domain is not exactly the three families: "
            f"{actual_keys}"
        )
    if set(expected_keys) != set(PHYSICAL_FAMILY_KEYS):
        raise AssertionError(
            "Expected physical-count domain is not exactly the three families: "
            f"{expected_keys}"
        )
    normalized_actual = {key: int(actual[key]) for key in PHYSICAL_FAMILY_KEYS}
    normalized_expected = {key: int(expected[key]) for key in PHYSICAL_FAMILY_KEYS}
    if normalized_actual != normalized_expected:
        raise AssertionError(
            f"Physical family counts differ: {normalized_actual} != {normalized_expected}"
        )


def required_columns(family: str) -> tuple[str, ...]:
    if family not in FAMILY_REQUIRED_COLUMNS:
        raise KeyError(f"Unknown physical family: {family}")
    return COMMON_REQUIRED_COLUMNS + FAMILY_REQUIRED_COLUMNS[family]
