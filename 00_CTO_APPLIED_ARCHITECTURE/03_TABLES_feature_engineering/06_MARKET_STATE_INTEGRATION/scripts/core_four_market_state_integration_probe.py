from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "experimental_core_four_market_state_integration_execution_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "core_four_market_state_integration_execution_scope_v0_1.json"
)


class ProbeError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(compact_json(payload).encode("utf-8")).hexdigest()


def is_within_or_equal(candidate: Path, allowed: Path) -> bool:
    candidate = candidate.resolve()
    allowed = allowed.resolve()
    if candidate == allowed:
        return True
    try:
        candidate.relative_to(allowed)
        return True
    except ValueError:
        return False


def resolve_path(raw: str, base: Path) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: serialize_cell(row.get(k)) for k in fieldnames})


def serialize_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return compact_json(value)
    return str(value)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ProbeError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return records


def validate_authority(scope: dict[str, Any]) -> None:
    if scope.get("mode") != "experimental_core_four_market_state_integration_execution":
        raise ProbeError(f"Unsupported mode: {scope.get('mode')}")

    authority = scope.get("authority", {})
    must_be_false = [
        "source_row_reads_allowed",
        "filesystem_market_data_reads_allowed",
        "bounded_sample_market_data_read_allowed",
        "full_data_read_allowed",
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


def validate_contract(scope: dict[str, Any], contract: dict[str, Any]) -> None:
    if contract.get("profile_id") != scope.get("profile_id"):
        raise ProbeError("Design contract profile_id does not match scope")
    if contract.get("required_object_ids") != scope.get("required_object_ids"):
        raise ProbeError("Design contract required_object_ids does not match scope")
    if contract.get("allowed_output_namespaces") != scope.get("allowed_value_namespaces"):
        raise ProbeError("Design contract allowed_output_namespaces does not match scope")

    input_authority = contract.get("input_authority", {})
    for key in [
        "source_row_reads_allowed",
        "parquet_write_allowed",
        "production_builder_authorized",
        "state_materialization_allowed",
        "downstream_consumption_authorized",
    ]:
        if input_authority.get(key) is not False:
            raise ProbeError(f"Design contract authority violation: {key} must be false")

    allowed_names = set(input_authority.get("allowed_input_artifacts") or [])
    for artifact_path in scope.get("input_artifacts", {}).values():
        artifact_name = Path(artifact_path).name
        if artifact_name not in allowed_names:
            raise ProbeError(
                f"Scope input artifact is not allowed by design contract: {artifact_name}"
            )


def validate_input_artifact_paths(
    paths: dict[str, Path],
    allowed_roots: list[Path],
) -> dict[str, dict[str, Any]]:
    report: dict[str, dict[str, Any]] = {}
    for name, path in paths.items():
        if not any(is_within_or_equal(path, root) for root in allowed_roots):
            raise ProbeError(f"Input artifact {name} resolves outside allowed artifact roots: {path}")
        if not path.exists():
            raise ProbeError(f"Input artifact {name} does not exist: {path}")
        if path.suffix.lower() == ".parquet":
            raise ProbeError(f"Parquet input is not authorized for this gate: {path}")
        report[name] = {
            "path": str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return report


def load_contract_status(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    result: dict[str, str] = {}
    for row in rows:
        result[row["request_id"]] = row.get("output_contract_status", "")
    return result


def load_determinism_status(path: Path) -> dict[str, dict[str, Any]]:
    rows = read_csv_rows(path)
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        result[row["request_id"]] = {
            "determinism_status": row.get("determinism_status", ""),
            "repeat_run_fingerprint_match": row.get("repeat_run_fingerprint_match", "").lower()
            == "true",
        }
    return result


def load_cutoff_status(path: Path) -> dict[str, dict[str, Any]]:
    rows = read_csv_rows(path)
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        req = row["request_id"]
        future_leak = row.get("future_leak", "").lower() == "true"
        current = result.setdefault(req, {"future_leak": False, "rows": 0})
        current["future_leak"] = bool(current["future_leak"] or future_leak)
        current["rows"] = int(current["rows"]) + 1
    return result


def load_context_report(path: Path) -> dict[str, dict[str, str]]:
    return {row["context_id"]: row for row in read_csv_rows(path)}


def load_selected_source_report(path: Path) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in read_csv_rows(path):
        counts[row["request_id"]] += 1
    return dict(counts)


def status_is_blocked(status: str) -> bool:
    return status.startswith("BLOCKED")


def status_is_admitted(status: str, admitted_statuses: set[str]) -> bool:
    return status in admitted_statuses


def comparable_evidence(record: dict[str, Any], key: str) -> str:
    source_evidence = record.get("source_evidence") or {}
    return compact_json(source_evidence.get(key))


def validate_context_consistency(
    context_id: str,
    records: list[dict[str, Any]],
    required_object_ids: list[str],
    semantic_join_key: list[str],
) -> list[str]:
    findings: list[str] = []

    if len(records) != 4:
        findings.append(f"expected 4 records, observed {len(records)}")

    observed_objects = sorted(r.get("object_id") for r in records)
    if observed_objects != sorted(required_object_ids):
        findings.append(f"required object ids mismatch: {observed_objects}")

    for key in semantic_join_key:
        values = {r.get(key) for r in records}
        if len(values) != 1:
            findings.append(f"semantic join field differs: {key}={sorted(str(v) for v in values)}")

    daily_evidence = {comparable_evidence(r, "004_daily_row") for r in records}
    if len(daily_evidence) != 1:
        findings.append("004 daily evidence differs across object records")

    bar_evidence = {comparable_evidence(r, "014_selected_closed_bar") for r in records}
    if len(bar_evidence) != 1:
        findings.append("014 selected bar evidence differs across object records")

    return findings


def merge_policy_versions(records: list[dict[str, Any]]) -> tuple[dict[str, str], list[str]]:
    merged: dict[str, str] = {}
    findings: list[str] = []
    for record in records:
        policy_versions = ((record.get("lineage") or {}).get("policy_versions") or {})
        for name, version in policy_versions.items():
            if name in merged and merged[name] != version:
                findings.append(f"policy version conflict for {name}: {merged[name]} vs {version}")
            merged[name] = version
    return merged, findings


def validate_semantic_equalities(values: dict[str, Any]) -> list[str]:
    checks = [
        (
            "price_movement__intraday_return_vs_prior_close_ratio",
            "price_location_structure__intraday_return_vs_prior_close_ratio_as_location",
        ),
        (
            "price_movement__intraday_return_vs_session_open_ratio",
            "price_location_structure__intraday_return_vs_session_open_ratio_as_location",
        ),
    ]
    findings: list[str] = []
    for left, right in checks:
        if left in values and right in values:
            try:
                left_value = float(values[left])
                right_value = float(values[right])
            except (TypeError, ValueError):
                if values[left] != values[right]:
                    findings.append(f"semantic equality mismatch: {left} != {right}")
                continue
            if abs(left_value - right_value) > 1e-12:
                findings.append(f"semantic equality mismatch: {left} != {right}")
    return findings


def build_candidate_id(profile_id: str, representative: dict[str, Any], fingerprint: str) -> str:
    payload = {
        "profile_id": profile_id,
        "instrument_id": representative.get("instrument_id"),
        "ticker": representative.get("ticker"),
        "session_date": representative.get("session_date"),
        "decision_timestamp_utc": representative.get("decision_timestamp_utc"),
        "decision_case": representative.get("decision_case"),
        "context_input_fingerprint": fingerprint,
    }
    return sha256_payload(payload)


def integrate_contexts(
    records: list[dict[str, Any]],
    context_report: dict[str, dict[str, str]],
    output_contract_status: dict[str, str],
    determinism_status: dict[str, dict[str, Any]],
    cutoff_status: dict[str, dict[str, Any]],
    selected_source_counts: dict[str, int],
    scope: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    required_object_ids = scope["required_object_ids"]
    semantic_join_key = scope["semantic_join_key"]
    allowed_namespaces = scope["allowed_value_namespaces"]
    admitted_statuses = set(scope["object_atomicity"]["pass_statuses_admitted"])
    design_restrictions = [f"design_restriction:{r}" for r in contract.get("restrictions", [])]

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["context_id"]].append(record)

    candidate_records: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    context_rows: list[dict[str, Any]] = []
    value_rows: list[dict[str, Any]] = []

    for context_id in sorted(grouped):
        context_records = sorted(grouped[context_id], key=lambda r: str(r.get("object_id")))
        representative = context_records[0]
        context_acceptance = context_report.get(context_id, {})
        context_fingerprint = context_acceptance.get("context_input_fingerprint", "")
        object_statuses = {r["object_id"]: r.get("resolution_status", "") for r in context_records}
        object_record_ids = {r["object_id"]: r.get("record_id", "") for r in context_records}

        findings = validate_context_consistency(
            context_id,
            context_records,
            required_object_ids,
            semantic_join_key,
        )

        if not context_fingerprint:
            findings.append("missing context_input_fingerprint from acceptance context report")
        if context_acceptance.get("context_acceptance_status") != "PASS":
            findings.append(
                "acceptance context status is not PASS: "
                + str(context_acceptance.get("context_acceptance_status"))
            )

        contract_failures: list[str] = []
        determinism_failures: list[str] = []
        future_leaks: list[str] = []
        for record in context_records:
            req = record["request_id"]
            if output_contract_status.get(req) != "PASS":
                contract_failures.append(req)
            det = determinism_status.get(req, {})
            if det.get("determinism_status") != "PASS" or det.get("repeat_run_fingerprint_match") is not True:
                determinism_failures.append(req)
            cutoff = cutoff_status.get(req, {})
            record_future_leak = bool(((record.get("cutoff_evidence") or {}).get("future_bar_leak")))
            if cutoff.get("future_leak") or record_future_leak:
                future_leaks.append(req)

        policy_versions, policy_findings = merge_policy_versions(context_records)
        findings.extend(policy_findings)

        blocked_objects = [
            object_id for object_id, status in sorted(object_statuses.items()) if status_is_blocked(status)
        ]
        non_admitted_statuses = [
            f"{object_id}:{status}"
            for object_id, status in sorted(object_statuses.items())
            if not status_is_admitted(status, admitted_statuses) and not status_is_blocked(status)
        ]

        candidate_emitted = False
        rejected_reason = ""
        integration_status = ""
        admitted_value_count = 0

        if findings:
            integration_status = "FAILED_CONTEXT_CONSISTENCY"
            rejected_reason = "; ".join(findings)
        elif contract_failures or determinism_failures or future_leaks:
            integration_status = "FAILED_CONTRACT_OR_DETERMINISM"
            parts = []
            if contract_failures:
                parts.append("output_contract_failures=" + "|".join(contract_failures))
            if determinism_failures:
                parts.append("determinism_failures=" + "|".join(determinism_failures))
            if future_leaks:
                parts.append("future_leaks=" + "|".join(sorted(set(future_leaks))))
            rejected_reason = "; ".join(parts)
        elif blocked_objects:
            integration_status = "REJECTED_REQUIRED_OBJECT_BLOCKED"
            rejected_reason = "blocked_required_objects=" + "|".join(blocked_objects)
        elif non_admitted_statuses:
            integration_status = "FAILED_CONTRACT_OR_DETERMINISM"
            rejected_reason = "non_admitted_statuses=" + "|".join(non_admitted_statuses)
        else:
            values: dict[str, Any] = {}
            restrictions = set(design_restrictions)
            admitted_namespaces = set()
            namespace_findings: list[str] = []

            for record in context_records:
                for restriction in record.get("restrictions") or []:
                    restrictions.add(f"{record['object_id']}:{restriction}")

                for key, value in (record.get("values") or {}).items():
                    matching_namespaces = [ns for ns in allowed_namespaces if key.startswith(ns)]
                    if not matching_namespaces:
                        namespace_findings.append(f"value outside allowed namespace: {key}")
                        continue
                    admitted_namespaces.add(matching_namespaces[0])
                    if key in values and compact_json(values[key]) != compact_json(value):
                        namespace_findings.append(f"duplicate conflicting output field: {key}")
                        continue
                    values[key] = value

            semantic_findings = validate_semantic_equalities(values)
            namespace_findings.extend(semantic_findings)

            if namespace_findings:
                integration_status = "FAILED_CONTEXT_CONSISTENCY"
                rejected_reason = "; ".join(namespace_findings)
            else:
                any_object_restricted = any(
                    status == "PASS_WITH_RESTRICTIONS" for status in object_statuses.values()
                )
                integration_status = (
                    "INTEGRABLE_COMPLETE_WITH_RESTRICTIONS"
                    if any_object_restricted or restrictions
                    else "INTEGRABLE_COMPLETE"
                )
                candidate_id = build_candidate_id(scope["profile_id"], representative, context_fingerprint)
                shared_source_evidence = {
                    "004_daily_row": (representative.get("source_evidence") or {}).get("004_daily_row"),
                    "014_selected_closed_bar": (representative.get("source_evidence") or {}).get(
                        "014_selected_closed_bar"
                    ),
                    "014_closed_bar_count": (representative.get("source_evidence") or {}).get(
                        "014_closed_bar_count"
                    ),
                }
                candidate = {
                    "market_state_candidate_id": candidate_id,
                    "market_state_profile_id": scope["profile_id"],
                    "context_id": context_id,
                    "instrument_id": representative.get("instrument_id"),
                    "ticker": representative.get("ticker"),
                    "session_date": representative.get("session_date"),
                    "decision_timestamp_utc": representative.get("decision_timestamp_utc"),
                    "decision_case": representative.get("decision_case"),
                    "context_input_fingerprint": context_fingerprint,
                    "integration_status": integration_status,
                    "object_statuses": object_statuses,
                    "object_record_ids": object_record_ids,
                    "admitted_namespaces": sorted(admitted_namespaces),
                    "values": {k: values[k] for k in sorted(values)},
                    "shared_source_evidence": shared_source_evidence,
                    "policy_versions": dict(sorted(policy_versions.items())),
                    "restrictions": sorted(restrictions),
                    "authority": {
                        "candidate_records_are_canonical_market_state": False,
                        "candidate_records_are_downstream_consumable": False,
                        "state_materialization_allowed": False,
                        "parquet_write_allowed": False,
                    },
                }
                candidate_records.append(candidate)
                candidate_emitted = True
                admitted_value_count = len(values)

                for record in context_records:
                    for key in sorted((record.get("values") or {}).keys()):
                        if key in values:
                            ns = next((p for p in allowed_namespaces if key.startswith(p)), "")
                            value_rows.append(
                                {
                                    "market_state_candidate_id": candidate_id,
                                    "context_id": context_id,
                                    "object_id": record["object_id"],
                                    "source_record_id": record.get("record_id"),
                                    "value_namespace": ns,
                                    "value_field": key,
                                    "value_admitted": True,
                                }
                            )

        if not candidate_emitted:
            rejected_rows.append(
                {
                    "context_id": context_id,
                    "integration_status": integration_status,
                    "rejected_reason": rejected_reason,
                    "object_statuses": object_statuses,
                    "object_record_ids": object_record_ids,
                    "context_input_fingerprint": context_fingerprint,
                }
            )

        context_rows.append(
            {
                "context_id": context_id,
                "integration_status": integration_status,
                "candidate_emitted": candidate_emitted,
                "rejected": not candidate_emitted,
                "rejected_reason": rejected_reason,
                "instrument_id": representative.get("instrument_id"),
                "ticker": representative.get("ticker"),
                "session_date": representative.get("session_date"),
                "decision_timestamp_utc": representative.get("decision_timestamp_utc"),
                "decision_case": representative.get("decision_case"),
                "object_statuses": object_statuses,
                "object_record_ids": object_record_ids,
                "context_input_fingerprint": context_fingerprint,
                "admitted_value_count": admitted_value_count,
                "selected_source_report_rows": sum(
                    selected_source_counts.get(r["request_id"], 0) for r in context_records
                ),
            }
        )

    return candidate_records, rejected_rows, context_rows, value_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_findings(path: Path, summary: dict[str, Any]) -> None:
    text = f"""# Core Four Market State Integration Execution Findings v0.1

Status: `{summary["overall_status"]}`
Date: `2026-07-21`
Run: `{summary["run_id"]}`

## Result

```text
experimental_core_four_market_state_integration_execution = {summary["experimental_core_four_market_state_integration_execution"]}
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
source_row_reads_allowed = false
state_materialization_allowed = false
parquet_write_allowed = false
downstream_consumption_authorized = false
production_builder_authorized = false
dataset_promotion_authorized = false
candidate_records_are_canonical_market_state = false
```

## Interpretation

The probe integrated only accepted core-four resolution records from the
reference v0.10 builder validation run. It did not read physical market source
tables. It emitted non-canonical JSONL candidate records for integrable
contexts and rejected contexts containing blocked required Objects under the
object atomicity rule.

## Next Gate

```text
core_four_market_state_materialization_design = CONDITIONAL_NEXT_DESIGN_GATE
Market State parquet materialization = NOT_AUTHORIZED
production builder = NOT_AUTHORIZED
downstream consumption = NOT_AUTHORIZED
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
    feature_root = integration_root.parent
    probe_root = feature_root / "05_STATE_BUILDER_VALIDATION" / "experimental_state_builder_probe"
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
        "execution_class": "experimental_non_materializing_artifact_integration",
        "input_scope_path": str(scope_path),
        "output_root": str(run_root),
        "run_dir": str(run_dir),
        "expected_scope": "integrate accepted core-four resolution records only; no source market data reads",
        "overwrite_policy": "refuse_existing_run_dir",
        "success_criteria": "8 candidates emitted, 2 required-object-blocked contexts rejected, no consistency/contract/determinism failures",
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

    design_contract_path = resolve_path(scope["design_contract_path"], scope_dir)
    input_paths = {
        key: resolve_path(raw_path, scope_dir)
        for key, raw_path in scope.get("input_artifacts", {}).items()
    }
    input_paths["design_contract"] = design_contract_path
    artifact_report = validate_input_artifact_paths(
        input_paths,
        [integration_root.resolve(), probe_root.resolve()],
    )

    contract = read_json(design_contract_path)
    validate_contract(scope, contract)

    builder_manifest = read_json(input_paths["builder_final_manifest"])
    if builder_manifest.get("run_id") != scope["reference_builder_run_id"]:
        raise ProbeError("Builder final manifest run_id does not match scope")
    if builder_manifest.get("experimental_builder_validation_execution_core_four") != "PASS_WITH_RESTRICTIONS":
        raise ProbeError("Reference builder run did not close core-four builder validation with restrictions")
    if builder_manifest.get("state_materialization") != "NOT_AUTHORIZED":
        raise ProbeError("Reference builder run state materialization boundary is not closed")

    acceptance_summary = read_json(input_paths["acceptance_summary"])
    if acceptance_summary.get("review_status") != "CLOSED_PASS_WITH_RESTRICTIONS":
        raise ProbeError("Acceptance summary review_status is not CLOSED_PASS_WITH_RESTRICTIONS")
    if acceptance_summary.get("reference_run") != scope["reference_builder_run_id"]:
        raise ProbeError("Acceptance summary reference run does not match scope")

    records = read_jsonl(input_paths["resolution_records"])
    output_contract_status = load_contract_status(input_paths["builder_output_contract_report"])
    determinism_status = load_determinism_status(input_paths["determinism_report"])
    cutoff_status = load_cutoff_status(input_paths["cutoff_enforcement_report"])
    context_report = load_context_report(input_paths["acceptance_context_report"])
    selected_source_counts = load_selected_source_report(input_paths["selected_source_rows_report"])

    limits = scope["limits"]
    grouped_count = len({r.get("context_id") for r in records})
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
        cutoff_status=cutoff_status,
        selected_source_counts=selected_source_counts,
        scope=scope,
        contract=contract,
    )

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

    expected = scope["expected_reference_result"]
    if failed_context_consistency or failed_contract_or_determinism or future_bar_leaks or blocked_values_admitted:
        gate_status = "FAILED"
        overall_status = "failed_core_four_market_state_integration_execution"
    elif (
        len(candidates) == int(expected["candidate_records_expected"])
        and rejected_required_object_blocked
        == int(expected["rejected_required_object_blocked_contexts_expected"])
    ):
        gate_status = "PASS_WITH_RESTRICTIONS"
        overall_status = "passed_core_four_market_state_integration_execution_with_restrictions"
    else:
        gate_status = "PASS_WITH_FINDINGS"
        overall_status = "passed_core_four_market_state_integration_execution_with_findings"

    candidate_path = run_dir / "market_state_candidate_records.jsonl"
    rejected_path = run_dir / "rejected_context_report.csv"
    context_path = run_dir / "integration_context_report.csv"
    values_path = run_dir / "integration_value_manifest.csv"
    summary_path = run_dir / "core_four_market_state_integration_execution_summary.json"
    findings_path = run_dir / "core_four_market_state_integration_execution_findings.md"

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
        "experimental_core_four_market_state_integration_execution": gate_status,
        "profile_id": scope["profile_id"],
        "reference_builder_run_id": scope["reference_builder_run_id"],
        "reference_acceptance_review_id": scope["reference_acceptance_review_id"],
        "contexts_seen": grouped_count,
        "input_resolution_records": len(records),
        "candidate_records_emitted": len(candidates),
        "rejected_contexts": len(rejected),
        "rejected_required_object_blocked_contexts": rejected_required_object_blocked,
        "failed_context_consistency": failed_context_consistency,
        "failed_contract_or_determinism": failed_contract_or_determinism,
        "future_bar_leaks": future_bar_leaks,
        "blocked_values_admitted": blocked_values_admitted,
        "admitted_value_rows": len(value_rows),
        "candidate_jsonl_output_allowed": True,
        "candidate_records_are_canonical_market_state": False,
        "candidate_records_are_downstream_consumable": False,
        "source_row_reads_allowed": False,
        "source_market_data_rows_read": 0,
        "state_materialization_allowed": False,
        "parquet_write_allowed": False,
        "parquet_files_written": 0,
        "downstream_consumption_authorized": False,
        "production_builder_authorized": False,
        "dataset_promotion_authorized": False,
        "next_gate": "core_four_market_state_materialization_design_conditional_not_open",
        "created_at_utc": pre_manifest["created_at_utc"],
        "completed_at_utc": utc_now(),
        "artifacts": {
            "pre_manifest": str(run_dir / "pre_manifest.json"),
            "heartbeat": str(run_dir / "heartbeat.json"),
            "market_state_candidate_records": str(candidate_path),
            "rejected_context_report": str(rejected_path),
            "integration_context_report": str(context_path),
            "integration_value_manifest": str(values_path),
            "core_four_market_state_integration_execution_summary": str(summary_path),
            "core_four_market_state_integration_execution_findings": str(findings_path),
            "final_manifest": str(run_dir / "final_manifest.json"),
        },
        "input_artifacts": artifact_report,
    }
    write_json(summary_path, summary)
    write_findings(findings_path, summary)

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
    return 0 if gate_status in {"PASS_WITH_RESTRICTIONS", "PASS_WITH_FINDINGS"} else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
