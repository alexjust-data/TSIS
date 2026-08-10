#!/usr/bin/env python3
"""Independent post-run validator for Trading Activity Binding A pilot runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from trading_activity_binding_a_multisession_engine import (
    atomic_write_json,
    sha256_file,
    utc_text,
)

INTERNAL_VALIDATIONS = (
    "row_count_validation",
    "grain_uniqueness_validation",
    "temporal_legality_validation",
    "kernel_equivalence_validation",
    "baseline_reference_validation",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    return parser


def _increment(counter: Counter[str], values: pd.Series) -> None:
    for key, count in values.fillna("<NULL>").astype(str).value_counts().items():
        counter[str(key)] += int(count)


def _metadata_rows(paths: Iterable[Path]) -> int:
    return sum(pq.ParquetFile(path).metadata.num_rows for path in paths)


def _timestamp_violations(frame: pd.DataFrame, left: str, right: str) -> int:
    left_values = pd.to_datetime(frame[left], utc=True, errors="coerce")
    right_values = pd.to_datetime(frame[right], utc=True, errors="coerce")
    return int((left_values.notna() & right_values.notna() & (left_values > right_values)).sum())


def _validate_hash_index(run_root: Path) -> dict[str, Any]:
    index_path = run_root / "validation" / "output_hashes.parquet"
    index = pd.read_parquet(index_path)
    failures: list[str] = []
    total_bytes = 0
    for row in index.to_dict("records"):
        path = Path(row["path"])
        if not path.is_file():
            failures.append(f"MISSING:{path}")
            continue
        actual = sha256_file(path)
        expected = str(row["sha256"])
        if actual != expected:
            failures.append(f"INDEX_HASH_MISMATCH:{path}")
        sidecar = path.with_suffix(path.suffix + ".sha256")
        if not sidecar.is_file():
            failures.append(f"MISSING_SIDECAR:{path}")
        elif sidecar.read_text(encoding="ascii").strip() != actual:
            failures.append(f"SIDECAR_HASH_MISMATCH:{path}")
        total_bytes += path.stat().st_size

    index_sidecar = index_path.with_suffix(index_path.suffix + ".sha256")
    index_hash = sha256_file(index_path)
    if not index_sidecar.is_file():
        failures.append(f"MISSING_INDEX_SIDECAR:{index_path}")
    elif index_sidecar.read_text(encoding="ascii").strip() != index_hash:
        failures.append(f"INDEX_SIDECAR_HASH_MISMATCH:{index_path}")
    return {
        "status": "PASS" if not failures else "FAIL",
        "indexed_partition_count": int(len(index)),
        "unique_indexed_path_count": int(index["path"].nunique()),
        "indexed_resumed_partition_count": int(index["resumed"].sum()),
        "indexed_partition_bytes": total_bytes,
        "index_path": str(index_path),
        "index_sha256": index_hash,
        "failures": failures,
    }


def _current_summary(paths: list[Path]) -> dict[str, Any]:
    counters = {
        "observation_state": Counter(),
        "calculation_state": Counter(),
        "duration_calculation_state": Counter(),
        "concentration_calculation_state": Counter(),
        "quality_state": Counter(),
        "coverage_state": Counter(),
        "local_window_disposition": Counter(),
    }
    future_window_rows = 0
    availability_violations = 0
    degraded_rows = 0
    for path in paths:
        frame = pd.read_parquet(
            path,
            columns=[
                *counters,
                "future_window_used",
                "feature_input_max_available_at",
                "decision_timestamp",
            ],
        )
        for field, counter in counters.items():
            _increment(counter, frame[field])
        future_window_rows += int(frame["future_window_used"].fillna(True).sum())
        availability_violations += _timestamp_violations(
            frame, "feature_input_max_available_at", "decision_timestamp"
        )
        degraded_rows += int(frame["quality_state"].eq("DEGRADED").sum())
    return {
        "partition_count": len(paths),
        "row_count": _metadata_rows(paths),
        **{field: dict(counter) for field, counter in counters.items()},
        "future_window_true_rows": future_window_rows,
        "availability_after_decision_rows": availability_violations,
        "degraded_rows": degraded_rows,
    }


def _multiscale_summary(paths: list[Path]) -> dict[str, Any]:
    calculation = Counter()
    quality = Counter()
    pair = Counter()
    availability_violations = 0
    future_window_rows = 0
    for path in paths:
        frame = pd.read_parquet(
            path,
            columns=[
                "calculation_state",
                "quality_state",
                "pair_id",
                "feature_input_max_available_at",
                "decision_timestamp",
                "future_window_used",
            ],
        )
        _increment(calculation, frame["calculation_state"])
        _increment(quality, frame["quality_state"])
        _increment(pair, frame["pair_id"])
        availability_violations += _timestamp_violations(
            frame, "feature_input_max_available_at", "decision_timestamp"
        )
        future_window_rows += int(frame["future_window_used"].fillna(True).sum())
    return {
        "partition_count": len(paths),
        "row_count": _metadata_rows(paths),
        "calculation_state": dict(calculation),
        "quality_state": dict(quality),
        "pair_id": dict(pair),
        "future_window_true_rows": future_window_rows,
        "availability_after_decision_rows": availability_violations,
    }


def _baseline_summary(paths: list[Path]) -> dict[str, Any]:
    state = Counter()
    candidate = Counter()
    current_calculation = Counter()
    candidate_state: dict[str, Counter[str]] = defaultdict(Counter)
    candidate_reference_sessions: dict[str, dict[str, int]] = defaultdict(
        lambda: {"min": 10**9, "max": -1}
    )
    baseline_availability_violations = 0
    current_availability_violations = 0
    future_window_rows = 0
    for path in paths:
        frame = pd.read_parquet(
            path,
            columns=[
                "baseline_candidate_id",
                "baseline_calculation_state",
                "reference_session_count",
                "calculation_state",
                "baseline_input_max_available_at",
                "feature_input_max_available_at",
                "decision_timestamp",
                "future_window_used",
            ],
        )
        _increment(state, frame["baseline_calculation_state"])
        _increment(candidate, frame["baseline_candidate_id"])
        _increment(current_calculation, frame["calculation_state"])
        grouped = frame.groupby(
            ["baseline_candidate_id", "baseline_calculation_state"], dropna=False
        ).size()
        for (candidate_id, state_id), count in grouped.items():
            candidate_state[str(candidate_id)][str(state_id)] += int(count)
        for candidate_id, group in frame.groupby("baseline_candidate_id"):
            values = pd.to_numeric(group["reference_session_count"], errors="coerce").dropna()
            if not values.empty:
                record = candidate_reference_sessions[str(candidate_id)]
                record["min"] = min(record["min"], int(values.min()))
                record["max"] = max(record["max"], int(values.max()))
        baseline_availability_violations += _timestamp_violations(
            frame, "baseline_input_max_available_at", "decision_timestamp"
        )
        current_availability_violations += _timestamp_violations(
            frame, "feature_input_max_available_at", "decision_timestamp"
        )
        future_window_rows += int(frame["future_window_used"].fillna(True).sum())
    return {
        "partition_count": len(paths),
        "row_count": _metadata_rows(paths),
        "baseline_calculation_state": dict(state),
        "baseline_candidate_id": dict(candidate),
        "current_calculation_state": dict(current_calculation),
        "candidate_by_state": {
            key: dict(value) for key, value in candidate_state.items()
        },
        "candidate_reference_session_range": dict(candidate_reference_sessions),
        "future_window_true_rows": future_window_rows,
        "current_availability_after_decision_rows": current_availability_violations,
        "baseline_availability_after_decision_rows": baseline_availability_violations,
    }


def _scope_summary(run_root: Path) -> dict[str, Any]:
    dense = pd.read_parquet(run_root / "scope" / "dense_input_manifest.parquet")
    audit = pd.read_parquet(run_root / "scope" / "selected_session_local_audit.parquet")
    return {
        "dense_session_rows": int(len(dense)),
        "source_exists": dense["source_exists"].value_counts(dropna=False).to_dict(),
        "acquisition_evidence_state": dense[
            "acquisition_evidence_state"
        ].value_counts(dropna=False).to_dict(),
        "foundation_quality_label": dense[
            "foundation_quality_label"
        ].value_counts(dropna=False).to_dict(),
        "local_audit_rows": int(len(audit)),
        "local_audit_variable_families": audit[
            "variable_family"
        ].value_counts(dropna=False).to_dict(),
        "local_audit_disposition": audit[
            "local_audit_disposition"
        ].value_counts(dropna=False).to_dict(),
        "automatic_exclusion_rows": int(
            audit["automatic_exclusion_applied"].fillna(True).sum()
        ),
    }


def validate(run_root: Path, runtime_root: Path) -> dict[str, Any]:
    final = json.loads((runtime_root / "final_manifest.json").read_text(encoding="utf-8"))
    summary = json.loads(
        (run_root / "metadata" / "run_summary.json").read_text(encoding="utf-8")
    )
    internal = {
        name: json.loads(
            (run_root / "validation" / f"{name}.json").read_text(encoding="utf-8")
        )["status"]
        for name in INTERNAL_VALIDATIONS
    }
    current_paths = sorted((run_root / "current_state").rglob("part-*.parquet"))
    multiscale_paths = sorted(
        (run_root / "multiscale_contrast").rglob("part-*.parquet")
    )
    baseline_paths = sorted(
        (run_root / "pit_baseline_and_surprise").rglob("part-*.parquet")
    )
    hashes = _validate_hash_index(run_root)
    current = _current_summary(current_paths)
    multiscale = _multiscale_summary(multiscale_paths)
    baseline = _baseline_summary(baseline_paths)
    scope = _scope_summary(run_root)

    failures: list[str] = []
    if final["status"] != "COMPLETE":
        failures.append("FINAL_STATUS_NOT_COMPLETE")
    if summary["run_completion"] != "PASS":
        failures.append("RUN_SUMMARY_NOT_PASS")
    if any(value != "PASS" for value in internal.values()):
        failures.append("INTERNAL_VALIDATION_NOT_PASS")
    if hashes["status"] != "PASS":
        failures.append("HASH_VALIDATION_FAILED")
    expected = summary["expected_row_counts"]
    for key, actual in (
        ("current_state_rows", current["row_count"]),
        ("multiscale_rows", multiscale["row_count"]),
        ("baseline_rows", baseline["row_count"]),
    ):
        if int(expected[key]) != int(actual):
            failures.append(f"ROW_COUNT_MISMATCH:{key}")
    if scope["dense_session_rows"] != 130 or scope["local_audit_rows"] != 520:
        failures.append("SCOPE_GRAIN_MISMATCH")
    if scope["automatic_exclusion_rows"]:
        failures.append("AUTOMATIC_EXCLUSION_FOUND")
    temporal_values = (
        current["future_window_true_rows"],
        current["availability_after_decision_rows"],
        multiscale["future_window_true_rows"],
        multiscale["availability_after_decision_rows"],
        baseline["future_window_true_rows"],
        baseline["current_availability_after_decision_rows"],
        baseline["baseline_availability_after_decision_rows"],
    )
    if any(temporal_values):
        failures.append("TEMPORAL_LEGALITY_VIOLATION")
    return {
        "document_role": "INDEPENDENT_POST_RUN_VALIDATION",
        "generated_at_utc": utc_text(),
        "run_id": final["run_id"],
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "final_manifest": {
            "status": final["status"],
            "partition_count": final["partition_count"],
            "resumed_partition_count": len(final["resumed_partitions"]),
            "promotion_status": final["promotion_status"],
        },
        "internal_validation_status": internal,
        "scope": scope,
        "hash_validation": hashes,
        "current_state": current,
        "multiscale_contrast": multiscale,
        "pit_baseline_and_surprise": baseline,
    }


def main() -> int:
    args = _parser().parse_args()
    result = validate(args.run_root.resolve(), args.runtime_root.resolve())
    output = args.run_root / "validation" / "post_run_independent_validation.json"
    atomic_write_json(output, result)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
