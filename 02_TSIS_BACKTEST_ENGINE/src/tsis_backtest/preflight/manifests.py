"""Manifest writers for RunPreflight outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .contracts import DataPreflightReport, to_jsonable


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_data_manifest(report: DataPreflightReport) -> dict[str, Any]:
    if report.resolved_context is None:
        raise ValueError("resolved_context is required for data_manifest.json")
    ctx = report.resolved_context
    return {
        "manifest_schema_version": "0.1",
        "run_id": report.run_id,
        "generated_at_utc": report.generated_at_utc,
        "dataset_id": ctx.dataset_id,
        "dataset_version": ctx.dataset_version,
        "resolved_physical_root": ctx.resolved_physical_root,
        "price_view_policy": ctx.price_view_policy,
        "date_range": report.date_range,
        "session_policy": ctx.session_policy,
        "timezone": ctx.timezone,
        "calendar_id": ctx.calendar_id,
        "source_partitions_or_files_consumed": report.source_partitions_or_files_consumed,
        "snapshot_or_content_hashes": report.snapshot_or_content_hashes or {},
        "validation_manifest": _validation_manifest(ctx),
        "candidate_authorization": ctx.candidate_consumption_policy,
        "missing_data_policy": report.missing_data_policy,
        "corporate_action_policy": report.corporate_action_policy,
        "known_limitations": ctx.known_limitations,
    }


def build_universe_manifest(report: DataPreflightReport) -> dict[str, Any]:
    if report.resolved_context is None or report.universe_policy is None:
        raise ValueError("resolved context and universe policy are required")
    ctx = report.resolved_context
    return {
        "manifest_schema_version": "0.1",
        "run_id": report.run_id,
        "generated_at_utc": report.generated_at_utc,
        "universe_id": ctx.universe_dataset_id,
        "universe_run_id": ctx.universe_run_id,
        "selection_rule": report.universe_policy.get("selection_rule"),
        "effective_window": report.date_range,
        "selected_symbols": ctx.selected_symbols,
        "source_snapshot": report.universe_policy.get("source_snapshot"),
        "source_hash": report.universe_policy.get("source_hash"),
        "exclusions_and_reasons": [],
        "limitations": report.universe_policy.get("limitations", []),
    }


def write_preflight_outputs(report: DataPreflightReport, output_root: Path) -> None:
    write_json(output_root / "data_preflight_report.json", report)
    if not report.resolved:
        return
    write_json(output_root / "data_manifest.json", build_data_manifest(report))
    write_json(output_root / "universe_manifest.json", build_universe_manifest(report))


def _validation_manifest(ctx: Any) -> Path | None:
    candidate_policy = ctx.candidate_consumption_policy
    if candidate_policy is not None:
        return candidate_policy.accepted_validation_manifest
    for binding in (
        ctx.price_view_policy.signal,
        ctx.price_view_policy.execution,
        ctx.price_view_policy.valuation,
    ):
        if binding.validation_manifest is not None:
            return binding.validation_manifest
    return None

