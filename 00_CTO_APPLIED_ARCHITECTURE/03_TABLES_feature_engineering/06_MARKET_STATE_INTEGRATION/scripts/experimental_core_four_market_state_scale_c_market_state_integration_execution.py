from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core_four_market_state_integration_probe import (
    ProbeError,
    compact_json,
    git_value,
    integrate_contexts,
    is_within_or_equal,
    read_csv_rows,
    read_json,
    read_jsonl,
    resolve_path,
    sha256_file,
    sha256_payload,
    status_is_blocked,
    utc_now,
    write_csv_rows,
    write_json,
    write_jsonl,
)


SCRIPT_VERSION = "experimental_core_four_market_state_scale_c_market_state_integration_execution_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_c_market_state_integration_execution_scope_v0_1.json"
)


def validate_authority(scope: dict[str, Any]) -> None:
    if scope.get("mode") != "experimental_core_four_market_state_scale_c_market_state_integration_execution":
        raise ProbeError(f"Unsupported mode: {scope.get('mode')}")

    authority = scope.get("authority", {})
    must_be_false = [
        "source_row_reads_allowed",
        "filesystem_market_data_reads_allowed",
        "bounded_sample_market_data_read_allowed",
        "full_data_read_allowed",
        "013_direct_reads_allowed",
        "surface_rebuild_allowed",
        "sample_reselection_allowed",
        "fixed_utc_probe_calendar_fallback_allowed",
        "production_builder_authorized",
        "state_materialization_allowed",
        "parquet_write_allowed",
        "downstream_consumption_authorized",
        "dataset_promotion_authorized",
    ]
    for key in must_be_false:
        if authority.get(key) is not False:
            raise ProbeError(f"Authority violation: {key} must be false")

    for key in ["candidate_jsonl_output_allowed", "rejected_context_report_allowed"]:
        if authority.get(key) is not True:
            raise ProbeError(f"Authority violation: {key} must be true")


def validate_base_contract(scope: dict[str, Any], contract: dict[str, Any]) -> None:
    if contract.get("profile_id") != scope.get("profile_id"):
        raise ProbeError("Base design contract profile_id does not match scope")
    if contract.get("required_object_ids") != scope.get("required_object_ids"):
        raise ProbeError("Base design contract required_object_ids does not match scope")
    if contract.get("allowed_output_namespaces") != scope.get("allowed_value_namespaces"):
        raise ProbeError("Base design contract allowed_output_namespaces does not match scope")

    input_authority = contract.get("input_authority", {})
    for key in [
        "source_row_reads_allowed",
        "parquet_write_allowed",
        "production_builder_authorized",
        "state_materialization_allowed",
        "downstream_consumption_authorized",
    ]:
        if input_authority.get(key) is not False:
            raise ProbeError(f"Base design contract authority violation: {key} must be false")


def validate_input_artifact_paths(
    paths: dict[str, Path],
    expected_hashes: dict[str, str],
    allowed_roots: list[Path],
) -> dict[str, dict[str, Any]]:
    report: dict[str, dict[str, Any]] = {}
    for name, path in paths.items():
        if not any(is_within_or_equal(path, root) for root in allowed_roots):
            raise ProbeError(f"Input artifact {name} resolves outside allowed roots: {path}")
        if not path.exists():
            raise ProbeError(f"Input artifact {name} does not exist: {path}")
        if path.suffix.lower() == ".parquet":
            raise ProbeError(f"Parquet input is not authorized for this gate: {path}")
        digest = sha256_file(path)
        expected = expected_hashes.get(name)
        if expected and digest != expected:
            raise ProbeError(f"Input artifact hash mismatch for {name}: {digest} != {expected}")
        report[name] = {
            "path": str(path),
            "sha256": digest,
            "bytes": path.stat().st_size,
        }
    return report


def load_context_report_from_resolution_summary(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv_rows(path)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        status = row.get("context_resolution_status", "")
        if status not in {
            "INTEGRABLE_COMPLETE_OR_WITH_RESTRICTIONS",
            "BLOCKED_REQUIRED_OBJECT_INPUT_UNAVAILABLE",
        }:
            raise ProbeError(f"Unexpected context_resolution_status for {row.get('context_id')}: {status}")
        row = dict(row)
        row["context_acceptance_status"] = "PASS"
        result[row["context_id"]] = row
    return result


def validate_builder_manifest(
    final_manifest: dict[str, Any],
    builder_summary: dict[str, Any],
    scope: dict[str, Any],
) -> dict[str, Any]:
    expected = scope["expected_reference_result"]
    bindings = scope["accepted_bindings"]
    summary = final_manifest.get("summary") or {}

    if final_manifest.get("run_id") != scope["source_builder_run_id"]:
        raise ProbeError("Builder final_manifest run_id does not match scope")
    if builder_summary.get("run_id") != scope["source_builder_run_id"]:
        raise ProbeError("Builder summary run_id does not match scope")
    if summary.get("builder_resolution_execution_status") != scope["source_builder_status"]:
        raise ProbeError("Builder status does not match scope")
    if builder_summary.get("builder_resolution_execution_status") != scope["source_builder_status"]:
        raise ProbeError("Builder summary status does not match scope")

    exact_keys = {
        "scale_c_sample_fingerprint": bindings["scale_c_sample_fingerprint"],
        "scale_c_execution_surface_fingerprint": bindings["scale_c_execution_surface_fingerprint"],
        "calendar_binding_run_id": bindings["calendar_binding_run_id"],
        "calendar_version": bindings["calendar_version"],
        "calendar_source_snapshot_fingerprint": bindings["calendar_source_snapshot_fingerprint"],
    }
    for key, expected_value in exact_keys.items():
        if summary.get(key) != expected_value or builder_summary.get(key) != expected_value:
            raise ProbeError(f"Builder binding mismatch for {key}")

    numeric_expectations = {
        "requested_contexts": expected["contexts_seen"],
        "resolution_records": expected["input_resolution_records"],
        "integrable_contexts": expected["candidate_records_expected"],
        "blocked_contexts": expected["rejected_required_object_blocked_contexts_expected"],
        "failed_contexts": expected["failed_contexts_expected"],
        "source_013_rows_read": 0,
        "013_direct_builder_rows_read": 0,
        "future_bar_leaks": 0,
        "calendar_binding_failures": 0,
        "decision_case_semantic_mismatches": 0,
        "early_close_cutoff_failures": 0,
        "fixed_utc_fallback_uses": 0,
        "output_contract_failures": 0,
        "nondeterministic_records": 0,
        "hard_validation_failures": 0,
    }
    for key, expected_value in numeric_expectations.items():
        if summary.get(key) != expected_value or builder_summary.get(key) != expected_value:
            raise ProbeError(f"Builder summary mismatch for {key}")

    authority = final_manifest.get("authority") or {}
    for key in [
        "sample_reselected",
        "sample_manifest_mutated",
        "surface_rebuilt",
        "013_direct_builder_reads_allowed",
        "fixed_utc_probe_calendar_fallback_used",
        "market_state_integration_executed",
        "official_market_state_allowed",
        "production_builder_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
    ]:
        if authority.get(key) is not False:
            raise ProbeError(f"Builder authority boundary is not closed for {key}")

    return summary


def validate_resolution_record_bindings(
    records: list[dict[str, Any]],
    scope: dict[str, Any],
) -> dict[str, int]:
    bindings = scope["accepted_bindings"]
    counts = {
        "missing_temporal_lineage_fields": 0,
        "calendar_binding_mismatches": 0,
        "surface_fingerprint_mismatches": 0,
        "sample_fingerprint_mismatches": 0,
        "fixed_utc_fallback_uses": 0,
        "future_bar_leaks": 0,
        "bars_beyond_governed_close_admitted": 0,
    }
    required_temporal_fields = [
        "calendar_id",
        "calendar_version",
        "calendar_row_fingerprint",
        "session_open_utc",
        "session_close_utc",
        "session_type",
        "is_early_close",
    ]
    for record in records:
        lineage = record.get("lineage") or {}
        cutoff = record.get("cutoff_evidence") or {}
        source_evidence = record.get("source_evidence") or {}
        calendar_binding = source_evidence.get("governed_calendar_binding") or {}
        temporal_lineage = lineage.get("temporal_lineage") or {}

        if any(record.get(field) is None for field in required_temporal_fields):
            counts["missing_temporal_lineage_fields"] += 1
        if calendar_binding.get("calendar_version") != bindings["calendar_version"]:
            counts["calendar_binding_mismatches"] += 1
        if temporal_lineage.get("calendar_version") != bindings["calendar_version"]:
            counts["calendar_binding_mismatches"] += 1
        if lineage.get("scale_c_execution_surface_fingerprint") != bindings["scale_c_execution_surface_fingerprint"]:
            counts["surface_fingerprint_mismatches"] += 1
        if lineage.get("scale_c_sample_fingerprint") != bindings["scale_c_sample_fingerprint"]:
            counts["sample_fingerprint_mismatches"] += 1
        if cutoff.get("fixed_utc_probe_calendar_fallback_used") is True:
            counts["fixed_utc_fallback_uses"] += 1
        if cutoff.get("future_bar_leak") is True:
            counts["future_bar_leaks"] += 1
        selected_bar_end = cutoff.get("selected_bar_end_utc")
        governed_close = cutoff.get("governed_session_close_utc") or record.get("session_close_utc")
        if selected_bar_end and governed_close and selected_bar_end > governed_close:
            counts["bars_beyond_governed_close_admitted"] += 1
    return counts


def add_scale_c_lineage(
    candidates: list[dict[str, Any]],
    records: list[dict[str, Any]],
    scope: dict[str, Any],
) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["context_id"]].append(record)

    bindings = scope["accepted_bindings"]
    for candidate in candidates:
        context_records = grouped[candidate["context_id"]]
        representative = context_records[0]
        calendar_binding = (representative.get("source_evidence") or {}).get("governed_calendar_binding")
        candidate.update(
            {
                "calendar_id": representative.get("calendar_id"),
                "calendar_version": representative.get("calendar_version"),
                "calendar_row_fingerprint": representative.get("calendar_row_fingerprint"),
                "session_open_utc": representative.get("session_open_utc"),
                "session_close_utc": representative.get("session_close_utc"),
                "session_type": representative.get("session_type"),
                "is_early_close": representative.get("is_early_close"),
                "scale_c_sample_fingerprint": bindings["scale_c_sample_fingerprint"],
                "scale_c_execution_surface_fingerprint": bindings["scale_c_execution_surface_fingerprint"],
            }
        )
        candidate["shared_source_evidence"]["governed_calendar_binding"] = calendar_binding
        candidate["lineage"] = {
            "source_builder_run_id": scope["source_builder_run_id"],
            "integration_scope_id": scope["scope_id"],
            "scale_c_sample_run_id": bindings["scale_c_sample_run_id"],
            "scale_c_sample_fingerprint": bindings["scale_c_sample_fingerprint"],
            "scale_c_execution_surface_run_id": bindings["scale_c_execution_surface_run_id"],
            "scale_c_execution_surface_fingerprint": bindings["scale_c_execution_surface_fingerprint"],
            "calendar_binding_run_id": bindings["calendar_binding_run_id"],
            "calendar_version": bindings["calendar_version"],
            "calendar_source_snapshot_fingerprint": bindings["calendar_source_snapshot_fingerprint"],
            "temporal_lineage": {
                "calendar_id": representative.get("calendar_id"),
                "calendar_version": representative.get("calendar_version"),
                "calendar_row_fingerprint": representative.get("calendar_row_fingerprint"),
                "session_open_utc": representative.get("session_open_utc"),
                "session_close_utc": representative.get("session_close_utc"),
                "session_type": representative.get("session_type"),
                "is_early_close": representative.get("is_early_close"),
            },
        }
        candidate["authority"].update(
            {
                "source_market_data_rows_read": 0,
                "surface_rebuilt": False,
                "sample_reselected": False,
                "parquet_write_allowed": False,
                "state_materialization_allowed": False,
                "downstream_consumption_authorized": False,
                "dataset_promotion_authorized": False,
            }
        )
        candidate["market_state_candidate_fingerprint"] = sha256_payload(
            {
                "market_state_candidate_id": candidate["market_state_candidate_id"],
                "context_id": candidate["context_id"],
                "object_record_ids": candidate["object_record_ids"],
                "values": candidate["values"],
                "lineage": candidate["lineage"],
            }
        )


def write_findings(path: Path, summary: dict[str, Any]) -> None:
    text = f"""# Scale C Market State Integration Execution Findings v0.1

Status: `{summary["overall_status"]}`
Date: `2026-07-23`
Run: `{summary["run_id"]}`

## Result

```text
experimental_core_four_market_state_scale_c_market_state_integration_execution = {summary["experimental_core_four_market_state_scale_c_market_state_integration_execution"]}
contexts_seen = {summary["contexts_seen"]}
input_resolution_records = {summary["input_resolution_records"]}
candidate_records_emitted = {summary["candidate_records_emitted"]}
rejected_contexts = {summary["rejected_contexts"]}
rejected_required_object_blocked_contexts = {summary["rejected_required_object_blocked_contexts"]}
failed_context_consistency = {summary["failed_context_consistency"]}
failed_contract_or_determinism = {summary["failed_contract_or_determinism"]}
future_bar_leaks = {summary["future_bar_leaks"]}
blocked_values_admitted = {summary["blocked_values_admitted"]}
admitted_value_rows = {summary["admitted_value_rows"]}
```

## Authority Boundary

```text
source_market_data_rows_read = 0
013_direct_reads_allowed = false
surface_rebuild_allowed = false
sample_reselection_allowed = false
fixed_utc_probe_calendar_fallback_uses = {summary["fixed_utc_fallback_uses"]}
state_materialization_allowed = false
parquet_write_allowed = false
downstream_consumption_authorized = false
production_builder_authorized = false
dataset_promotion_authorized = false
candidate_records_are_canonical_market_state = false
```

## Interpretation

The execution integrated only accepted Scale C core-four resolution records from
the frozen builder/resolution run. It did not read physical market source
tables, rebuild the run-local 014 surface, reselect the sample or write parquet.

## Next Gate

```text
experimental_core_four_market_state_scale_c_candidate_materialization_authorization_v0_1 = CONDITIONAL_NEXT_AUTHORIZATION_GATE
Market State parquet materialization = NOT_AUTHORIZED
production builder = NOT_AUTHORIZED
downstream consumption = NOT_AUTHORIZED
```
"""
    path.write_text(text, encoding="utf-8")


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    text = f"""# Experimental Core Four Market State Scale C Market State Integration Execution Readout v0.1

Status: `{summary["experimental_core_four_market_state_scale_c_market_state_integration_execution"]}`
Date: `2026-07-23`
Run: `{summary["run_id"]}`

```text
source_builder_run_id = {summary["source_builder_run_id"]}
scale_c_sample_fingerprint = {summary["scale_c_sample_fingerprint"]}
scale_c_execution_surface_fingerprint = {summary["scale_c_execution_surface_fingerprint"]}
calendar_source_snapshot_fingerprint = {summary["calendar_source_snapshot_fingerprint"]}

contexts_seen = {summary["contexts_seen"]}
input_resolution_records = {summary["input_resolution_records"]}
candidate_records_emitted = {summary["candidate_records_emitted"]}
rejected_contexts = {summary["rejected_contexts"]}
rejected_required_object_blocked_contexts = {summary["rejected_required_object_blocked_contexts"]}
blocked_values_admitted = {summary["blocked_values_admitted"]}
admitted_value_rows = {summary["admitted_value_rows"]}

source_market_data_rows_read = 0
parquet_files_written = 0
fixed_utc_fallback_uses = {summary["fixed_utc_fallback_uses"]}
hard_validation_failures = {summary["hard_validation_failures"]}
```

The output is diagnostic JSONL only. It is not official Market State and is not
authorized for downstream consumption.

Next allowed gate:

```text
experimental_core_four_market_state_scale_c_candidate_materialization_authorization_v0_1
```
"""
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=str(DEFAULT_SCOPE))
    args = parser.parse_args(argv)

    scope_path = Path(args.scope).resolve()
    scope_dir = scope_path.parent
    integration_root = scope_dir.parent
    workspace_root = Path("C:/TSIS_Data").resolve()

    scope = read_json(scope_path)
    validate_authority(scope)

    run_root = resolve_path(scope["output_policy"]["output_root"], scope_dir)
    if not is_within_or_equal(run_root, integration_root):
        raise ProbeError(f"Output root must stay inside integration root: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{scope['output_policy']['run_id_prefix']}_{timestamp}"
    run_dir = run_root / run_id
    if run_dir.exists():
        raise ProbeError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    if not is_within_or_equal(run_dir, workspace_root):
        raise ProbeError(f"Refusing to write outside workspace: {run_dir}")

    command_line = " ".join([str(Path(__file__).resolve()), "--scope", str(scope_path)])
    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

    pre_manifest = {
        "run_id": run_id,
        "status": "starting",
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "command_line": command_line,
        "cwd": str(Path.cwd()),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getppid(),
        "pid": os.getpid(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_dirty_state": git_dirty_state,
        "mode": scope["mode"],
        "execution_class": "experimental_non_materializing_scale_c_artifact_integration",
        "input_scope_path": str(scope_path),
        "output_root": str(run_root),
        "run_dir": str(run_dir),
        "expected_scope": "integrate accepted Scale C core-four resolution records only; no source market data reads",
        "overwrite_policy": "refuse_existing_run_dir",
        "success_criteria": "64 candidates emitted, 8 required-object-blocked contexts rejected, no consistency/contract/determinism failures",
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "validate_inputs",
            "pid": os.getpid(),
            "run_dir": str(run_dir),
        },
    )

    design_contract_path = resolve_path(scope["base_design_contract_path"], scope_dir)
    input_paths = {
        key: resolve_path(raw_path, scope_dir)
        for key, raw_path in scope.get("input_artifacts", {}).items()
    }
    input_paths["base_design_contract"] = design_contract_path

    artifact_report = validate_input_artifact_paths(
        input_paths,
        scope.get("expected_input_artifact_sha256", {}),
        [integration_root.resolve()],
    )

    contract = read_json(design_contract_path)
    validate_base_contract(scope, contract)

    builder_final_manifest = read_json(input_paths["builder_final_manifest"])
    builder_summary = read_json(input_paths["builder_summary"])
    source_builder_summary = validate_builder_manifest(builder_final_manifest, builder_summary, scope)

    records = read_jsonl(input_paths["resolution_records"])
    binding_counts = validate_resolution_record_bindings(records, scope)
    output_contract_status = {
        row["request_id"]: row.get("output_contract_status", "")
        for row in read_csv_rows(input_paths["builder_output_contract_report"])
    }
    determinism_status = {
        row["request_id"]: {
            "determinism_status": row.get("determinism_status", ""),
            "repeat_run_fingerprint_match": row.get("repeat_run_fingerprint_match", "").lower() == "true",
        }
        for row in read_csv_rows(input_paths["determinism_report"])
    }
    cutoff_status: dict[str, dict[str, Any]] = defaultdict(lambda: {"future_leak": False, "rows": 0})
    for row in read_csv_rows(input_paths["cutoff_enforcement_report"]):
        req = row["request_id"]
        cutoff_status[req]["future_leak"] = (
            bool(cutoff_status[req]["future_leak"])
            or row.get("future_leak", "").lower() == "true"
        )
        cutoff_status[req]["rows"] = int(cutoff_status[req]["rows"]) + 1
    context_report = load_context_report_from_resolution_summary(input_paths["context_resolution_summary"])
    selected_source_counts: dict[str, int] = defaultdict(int)
    for row in read_csv_rows(input_paths["selected_source_rows_report"]):
        selected_source_counts[row["request_id"]] += 1

    limits = scope["limits"]
    expected = scope["expected_reference_result"]
    grouped_count = len({r.get("context_id") for r in records})
    if len(records) != int(expected["input_resolution_records"]):
        raise ProbeError("Input resolution record count does not match expected Scale C cardinality")
    if grouped_count != int(expected["contexts_seen"]):
        raise ProbeError("Input context count does not match expected Scale C cardinality")
    if len(records) > int(limits["maximum_input_resolution_records"]):
        raise ProbeError("Input resolution record limit exceeded")
    if grouped_count > int(limits["maximum_contexts"]):
        raise ProbeError("Context limit exceeded")

    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "integrate_contexts",
            "pid": os.getpid(),
            "input_resolution_records": len(records),
            "contexts_seen": grouped_count,
        },
    )

    candidates, rejected, context_rows, value_rows = integrate_contexts(
        records=records,
        context_report=context_report,
        output_contract_status=output_contract_status,
        determinism_status=determinism_status,
        cutoff_status=dict(cutoff_status),
        selected_source_counts=dict(selected_source_counts),
        scope=scope,
        contract=contract,
    )
    add_scale_c_lineage(candidates, records, scope)

    if len(candidates) > int(limits["maximum_candidate_records"]):
        raise ProbeError("Candidate record limit exceeded")
    if len(rejected) > int(limits["maximum_rejected_context_records"]):
        raise ProbeError("Rejected context record limit exceeded")
    if len(value_rows) > int(limits["maximum_output_value_rows"]):
        raise ProbeError("Output value row limit exceeded")

    failed_context_consistency = sum(
        1 for row in context_rows if row["integration_status"] == "FAILED_CONTEXT_CONSISTENCY"
    )
    failed_contract_or_determinism = sum(
        1 for row in context_rows if row["integration_status"] == "FAILED_CONTRACT_OR_DETERMINISM"
    )
    rejected_required_object_blocked = sum(
        1 for row in context_rows if row["integration_status"] == "REJECTED_REQUIRED_OBJECT_BLOCKED"
    )
    future_bar_leaks = sum(1 for row in cutoff_status.values() if row.get("future_leak"))
    blocked_values_admitted = 0
    for candidate in candidates:
        for object_id, status in candidate["object_statuses"].items():
            if status_is_blocked(status):
                blocked_values_admitted += sum(
                    1 for key in candidate["values"] if key.startswith(f"{object_id}__")
                )

    hard_validation_failures = sum(
        [
            failed_context_consistency,
            failed_contract_or_determinism,
            future_bar_leaks,
            blocked_values_admitted,
            binding_counts["missing_temporal_lineage_fields"],
            binding_counts["calendar_binding_mismatches"],
            binding_counts["surface_fingerprint_mismatches"],
            binding_counts["sample_fingerprint_mismatches"],
            binding_counts["fixed_utc_fallback_uses"],
            binding_counts["bars_beyond_governed_close_admitted"],
        ]
    )

    if (
        len(candidates) == int(expected["candidate_records_expected"])
        and rejected_required_object_blocked
        == int(expected["rejected_required_object_blocked_contexts_expected"])
        and len(rejected) == int(expected["rejected_required_object_blocked_contexts_expected"])
        and hard_validation_failures == 0
    ):
        gate_status = "CLOSED_PASS_WITH_RESTRICTIONS"
        overall_status = "passed_scale_c_market_state_integration_execution_with_restrictions"
    else:
        gate_status = "FAILED"
        overall_status = "failed_scale_c_market_state_integration_execution"

    candidate_path = run_dir / "market_state_candidate_records.jsonl"
    rejected_path = run_dir / "rejected_context_report.csv"
    context_path = run_dir / "integration_context_report.csv"
    values_path = run_dir / "integration_value_manifest.csv"
    summary_path = run_dir / "scale_c_integration_summary.json"
    findings_path = run_dir / "scale_c_integration_findings.md"
    readout_path = run_dir / "readout.md"

    write_jsonl(candidate_path, candidates)
    write_csv_rows(
        rejected_path,
        [
            "context_id",
            "integration_status",
            "rejected_reason",
            "object_statuses",
            "object_record_ids",
            "context_input_fingerprint",
        ],
        rejected,
    )
    write_csv_rows(
        context_path,
        [
            "context_id",
            "integration_status",
            "candidate_emitted",
            "rejected",
            "rejected_reason",
            "instrument_id",
            "ticker",
            "session_date",
            "decision_timestamp_utc",
            "decision_case",
            "object_statuses",
            "object_record_ids",
            "context_input_fingerprint",
            "admitted_value_count",
            "selected_source_report_rows",
        ],
        context_rows,
    )
    write_csv_rows(
        values_path,
        [
            "market_state_candidate_id",
            "context_id",
            "object_id",
            "source_record_id",
            "value_namespace",
            "value_field",
            "value_admitted",
        ],
        value_rows,
    )

    parquet_outputs = list(run_dir.rglob("*.parquet"))
    if parquet_outputs:
        raise ProbeError(f"Parquet outputs are forbidden: {parquet_outputs}")

    summary = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "mode": scope["mode"],
        "overall_status": overall_status,
        "experimental_core_four_market_state_scale_c_market_state_integration_execution": gate_status,
        "profile_id": scope["profile_id"],
        "source_builder_run_id": scope["source_builder_run_id"],
        "scale_c_sample_fingerprint": scope["accepted_bindings"]["scale_c_sample_fingerprint"],
        "scale_c_execution_surface_fingerprint": scope["accepted_bindings"][
            "scale_c_execution_surface_fingerprint"
        ],
        "calendar_binding_run_id": scope["accepted_bindings"]["calendar_binding_run_id"],
        "calendar_version": scope["accepted_bindings"]["calendar_version"],
        "calendar_source_snapshot_fingerprint": scope["accepted_bindings"][
            "calendar_source_snapshot_fingerprint"
        ],
        "contexts_seen": grouped_count,
        "input_resolution_records": len(records),
        "candidate_records_emitted": len(candidates),
        "candidate_records_expected": int(expected["candidate_records_expected"]),
        "rejected_contexts": len(rejected),
        "rejected_required_object_blocked_contexts": rejected_required_object_blocked,
        "rejected_required_object_blocked_contexts_expected": int(
            expected["rejected_required_object_blocked_contexts_expected"]
        ),
        "failed_context_consistency": failed_context_consistency,
        "failed_contract_or_determinism": failed_contract_or_determinism,
        "future_bar_leaks": future_bar_leaks,
        "blocked_values_admitted": blocked_values_admitted,
        "admitted_value_rows": len(value_rows),
        "missing_temporal_lineage_fields": binding_counts["missing_temporal_lineage_fields"],
        "calendar_binding_mismatches": binding_counts["calendar_binding_mismatches"],
        "surface_fingerprint_mismatches": binding_counts["surface_fingerprint_mismatches"],
        "sample_fingerprint_mismatches": binding_counts["sample_fingerprint_mismatches"],
        "fixed_utc_fallback_uses": binding_counts["fixed_utc_fallback_uses"],
        "bars_beyond_governed_close_admitted": binding_counts["bars_beyond_governed_close_admitted"],
        "candidate_jsonl_output_allowed": True,
        "candidate_records_are_canonical_market_state": False,
        "candidate_records_are_downstream_consumable": False,
        "source_row_reads_allowed": False,
        "source_market_data_rows_read": 0,
        "source_013_rows_read": 0,
        "state_materialization_allowed": False,
        "parquet_write_allowed": False,
        "parquet_files_written": 0,
        "downstream_consumption_authorized": False,
        "production_builder_authorized": False,
        "dataset_promotion_authorized": False,
        "market_state_rows_materialized": 0,
        "hard_validation_failures": hard_validation_failures,
        "next_allowed_gate": "experimental_core_four_market_state_scale_c_candidate_materialization_authorization_v0_1",
        "source_builder_summary": {
            "run_id": source_builder_summary["run_id"],
            "builder_resolution_execution_status": source_builder_summary[
                "builder_resolution_execution_status"
            ],
            "resolution_records": source_builder_summary["resolution_records"],
            "integrable_contexts": source_builder_summary["integrable_contexts"],
            "blocked_contexts": source_builder_summary["blocked_contexts"],
        },
        "created_at_utc": pre_manifest["created_at_utc"],
        "completed_at_utc": utc_now(),
        "artifacts": {
            "pre_manifest": str(run_dir / "pre_manifest.json"),
            "heartbeat": str(run_dir / "heartbeat.json"),
            "market_state_candidate_records": str(candidate_path),
            "rejected_context_report": str(rejected_path),
            "integration_context_report": str(context_path),
            "integration_value_manifest": str(values_path),
            "scale_c_integration_summary": str(summary_path),
            "scale_c_integration_findings": str(findings_path),
            "readout": str(readout_path),
            "final_manifest": str(run_dir / "final_manifest.json"),
        },
        "input_artifacts": artifact_report,
    }
    write_json(summary_path, summary)
    write_findings(findings_path, summary)
    write_readout(readout_path, summary)

    final_manifest = dict(pre_manifest)
    final_manifest.update(summary)
    final_manifest["status"] = "complete"
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "complete",
            "stage": "complete",
            "pid": os.getpid(),
            "overall_status": overall_status,
            "candidate_records_emitted": len(candidates),
            "rejected_contexts": len(rejected),
        },
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if gate_status == "CLOSED_PASS_WITH_RESTRICTIONS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
