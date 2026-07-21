from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROBE_ID = "experimental_state_builder_probe_v0_1"
SCRIPT_VERSION = "experimental_state_builder_probe_v0_2"
SCRIPT_PATH = Path(__file__).resolve()
PROBE_ROOT = SCRIPT_PATH.parents[1]
VALIDATION_ROOT = PROBE_ROOT.parent
FEATURE_ENGINEERING_ROOT = VALIDATION_ROOT.parent
DEFAULT_CONFIG = PROBE_ROOT / "configs" / "experimental_state_builder_probe_v0_1.json"
DEFAULT_RUN_ROOT = PROBE_ROOT / "runs"
SUPPORTED_MODES = {"contract_check_only", "binding_and_schema_check_only"}

AUTHORITY_FLAGS = (
    "official_output_allowed",
    "production_builder_authorized",
    "state_consumption_authorized",
    "physical_materialization_authorized",
    "dataset_promotion_authorized",
    "market_state_operational_authority",
)

REGISTRY_FALSE_FLAGS = (
    "production_builder_authorized",
    "state_consumption_authorized",
    "physical_materialization_authorized",
    "dataset_promotion_authorized",
    "bounded_sample_data_read_allowed",
    "full_data_read_allowed",
)

REQUIRED_BINDING_FIELDS = (
    "source_alias",
    "binding_status",
    "governance_status",
    "physical_candidate_root",
    "physical_candidate_type",
    "dataset_format",
    "expected_grain",
    "expected_primary_keys",
    "expected_partition_keys",
    "event_timestamp_field",
    "availability_timestamp_field",
    "as_of_field",
    "valid_from_field",
    "valid_to_field",
    "minimum_required_columns",
    "quality_fields",
    "lineage_fields",
    "read_scope",
    "read_authorized",
    "schema_probe_authorized",
    "full_data_read_authorized",
    "binding_evidence",
    "binding_version",
    "review_status",
)


class ProbeError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def git_value(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=FEATURE_ENGINEERING_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def git_info() -> dict[str, Any]:
    return {
        "git_branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"]),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["status", "--short"])),
    }


def resolve_feature_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return FEATURE_ENGINEERING_ROOT / path


def resolve_registry_path(value: str, config_path: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    for candidate in (config_path.parent / path, PROBE_ROOT / path):
        if candidate.exists():
            return candidate
    return PROBE_ROOT / path


def ensure_output_dir(output_root: Path, run_id: str) -> Path:
    root = output_root.resolve()
    workspace_root = Path("C:/TSIS_Data").resolve()
    if not str(root).lower().startswith(str(workspace_root).lower()):
        raise ProbeError(f"output root must be under {workspace_root}: {root}")
    run_dir = (root / run_id).resolve()
    if not str(run_dir).lower().startswith(str(root).lower()):
        raise ProbeError(f"run dir escapes output root: {run_dir}")
    if run_dir.exists():
        raise ProbeError(f"run dir already exists; choose another run id: {run_dir}")
    run_dir.mkdir(parents=True)
    if root != DEFAULT_RUN_ROOT.resolve() and "experimental_state_builder_probe" not in str(root):
        raise ProbeError("custom output root must remain clearly experimental")
    return run_dir


def validate_authority_flags(config: dict[str, Any]) -> None:
    for flag in AUTHORITY_FLAGS:
        if config.get(flag) is not False:
            raise ProbeError(f"{flag} must be false for experimental probe")


def validate_config(config: dict[str, Any]) -> None:
    if config.get("probe_id") != PROBE_ID:
        raise ProbeError(f"probe_id must be {PROBE_ID}")
    if config.get("mode") not in SUPPORTED_MODES:
        raise ProbeError(f"mode must be one of {sorted(SUPPORTED_MODES)}")
    validate_authority_flags(config)
    objects = config.get("objects")
    if not isinstance(objects, list) or len(objects) != 12:
        raise ProbeError("config must contain exactly 12 objects")
    if "source_binding_registry" not in config and "source_registry" not in config:
        raise ProbeError("config must reference source_binding_registry")


def validate_registry(registry_doc: dict[str, Any]) -> None:
    if registry_doc.get("registry_status") != "experimental_non_production":
        raise ProbeError("source binding registry must be experimental_non_production")
    authority = registry_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("source binding registry must declare authority")
    for flag in REGISTRY_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"registry authority flag {flag} must be false")
    if authority.get("filesystem_metadata_read_allowed") is not True:
        raise ProbeError("filesystem metadata reads must be allowed for this mode")
    if authority.get("schema_metadata_read_allowed") is not True:
        raise ProbeError("schema metadata reads must be allowed for this mode")
    bindings = registry_doc.get("bindings")
    if not isinstance(bindings, dict) or not bindings:
        raise ProbeError("source binding registry must declare bindings")
    for alias, binding in bindings.items():
        if not isinstance(binding, dict):
            raise ProbeError(f"binding for {alias} must be an object")
        missing = [field for field in REQUIRED_BINDING_FIELDS if field not in binding]
        if missing:
            raise ProbeError(f"binding for {alias} missing fields: {', '.join(missing)}")
        if binding.get("source_alias") != alias:
            raise ProbeError(f"binding source_alias mismatch for {alias}")
        if binding.get("read_authorized") is not False:
            raise ProbeError(f"binding {alias} must keep read_authorized=false")
        if binding.get("full_data_read_authorized") is not False:
            raise ProbeError(f"binding {alias} must keep full_data_read_authorized=false")


def load_binding_registry(config: dict[str, Any], config_path: Path) -> tuple[dict[str, Any], Path | None, str | None]:
    registry_ref = config.get("source_binding_registry")
    if registry_ref:
        registry_path = resolve_registry_path(str(registry_ref), config_path).resolve()
        registry_doc = read_json(registry_path)
        validate_registry(registry_doc)
        return registry_doc, registry_path, sha256_file(registry_path)
    embedded = config.get("source_registry")
    if not isinstance(embedded, dict) or not embedded:
        raise ProbeError("legacy source_registry fallback must be non-empty")
    return {
        "registry_id": "embedded_source_registry_legacy",
        "registry_status": "experimental_non_production",
        "authority": {
            "filesystem_metadata_read_allowed": True,
            "schema_metadata_read_allowed": True,
            "bounded_sample_data_read_allowed": False,
            "full_data_read_allowed": False,
        },
        "allowed_roots": ["C:/TSIS_Data", "E:/TSIS/data", "G:/TSIS/data"],
        "bindings": embedded,
    }, None, None


def add_gate(rows: list[dict[str, Any]], *, object_id: str, gate: str, status: str, severity: str, finding: str, evidence: str = "") -> None:
    rows.append({
        "object_id": object_id,
        "gate": gate,
        "status": status,
        "severity": severity,
        "finding": finding,
        "evidence": evidence,
    })


def format_list(value: Any) -> str:
    if isinstance(value, list):
        return "|".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def temporal_fields(binding: dict[str, Any]) -> str:
    return json.dumps({
        "event_timestamp_field": binding.get("event_timestamp_field"),
        "availability_timestamp_field": binding.get("availability_timestamp_field"),
        "as_of_field": binding.get("as_of_field"),
        "valid_from_field": binding.get("valid_from_field"),
        "valid_to_field": binding.get("valid_to_field"),
    }, sort_keys=True)


def allowed_root_status(physical_root: str | None, allowed_roots: list[str]) -> tuple[str, str]:
    if not physical_root:
        return "NOT_BOUND", "no physical_candidate_root declared"
    candidate = Path(physical_root).resolve()
    for root in allowed_roots:
        allowed = Path(root).resolve()
        if str(candidate).lower().startswith(str(allowed).lower()):
            return "ALLOWED_ROOT", str(candidate)
    return "OUTSIDE_ALLOWED_ROOT", str(candidate)


def source_row(*, object_id: str, alias: str, role: str, binding: dict[str, Any] | None, severity: str, finding: str, path_check_status: str, path_root_status: str) -> dict[str, Any]:
    binding = binding or {}
    return {
        "object_id": object_id,
        "source_alias": alias,
        "role": role,
        "binding_status": binding.get("binding_status", "missing_registry_binding"),
        "governance_status": binding.get("governance_status", "unknown"),
        "physical_candidate_root": binding.get("physical_candidate_root"),
        "dataset_format": binding.get("dataset_format"),
        "expected_grain": format_list(binding.get("expected_grain")),
        "expected_primary_keys": format_list(binding.get("expected_primary_keys")),
        "temporal_fields": temporal_fields(binding),
        "minimum_required_columns": format_list(binding.get("minimum_required_columns")),
        "path_root_status": path_root_status,
        "path_check_status": path_check_status,
        "schema_probe_authorized": binding.get("schema_probe_authorized"),
        "read_authorized": binding.get("read_authorized"),
        "severity": severity,
        "finding": finding,
    }


def check_sources(obj: dict[str, Any], registry_doc: dict[str, Any], source_rows: list[dict[str, Any]], pass_fail: list[dict[str, Any]], *, check_physical_paths: bool) -> None:
    object_id = obj["object_id"]
    bindings = registry_doc["bindings"]
    allowed_roots = registry_doc.get("allowed_roots", [])
    for alias in obj.get("active_source_aliases", []):
        binding = bindings.get(alias)
        if binding is None:
            severity = "FAIL"
            finding = "active source alias has no registry binding"
            path_root_status = "MISSING_REGISTRY_BINDING"
            path_check_status = "NOT_EXECUTED"
            row_binding = None
        else:
            row_binding = binding
            physical_root = binding.get("physical_candidate_root")
            path_root_status, evidence = allowed_root_status(physical_root, allowed_roots)
            if binding.get("binding_status") == "blocked":
                severity = "FAIL"
                finding = "active source alias is blocked in binding registry"
                path_check_status = "NOT_EXECUTED"
            elif path_root_status == "OUTSIDE_ALLOWED_ROOT":
                severity = "FAIL"
                finding = f"physical candidate root outside allowed roots: {evidence}"
                path_check_status = "NOT_EXECUTED"
            elif not physical_root:
                severity = "WARN"
                finding = "active source alias is governed but has no physical candidate root yet"
                path_check_status = "NOT_BOUND"
            elif check_physical_paths:
                exists = Path(str(physical_root)).exists()
                severity = "INFO" if exists else "FAIL"
                finding = "physical candidate root exists" if exists else "physical candidate root missing"
                path_check_status = "FOUND" if exists else "MISSING"
            else:
                severity = "INFO"
                finding = "binding declared; physical path check not requested"
                path_check_status = "NOT_CHECKED"
        source_rows.append(source_row(
            object_id=object_id,
            alias=alias,
            role="active",
            binding=row_binding,
            severity=severity,
            finding=finding,
            path_check_status=path_check_status,
            path_root_status=path_root_status,
        ))
        add_gate(
            pass_fail,
            object_id=object_id,
            gate="source_binding_resolution",
            status="FAIL" if severity == "FAIL" else "PASS_WITH_FINDING" if severity == "WARN" else "PASS",
            severity=severity,
            finding=finding,
            evidence=alias,
        )

    for alias in obj.get("blocked_source_aliases", []):
        binding = bindings.get(alias)
        blocked = binding is not None and binding.get("binding_status") == "blocked"
        severity = "INFO" if blocked else "WARN"
        finding = "blocked source alias preserved as non-consumable" if blocked else "blocked source alias is not explicitly blocked in registry"
        source_rows.append(source_row(
            object_id=object_id,
            alias=alias,
            role="blocked",
            binding=binding,
            severity=severity,
            finding=finding,
            path_check_status="NOT_EXECUTED",
            path_root_status="BLOCKED_ALIAS",
        ))


def check_objects(config: dict[str, Any], registry_doc: dict[str, Any], *, check_physical_paths: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    pass_fail: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []
    lineage_rows: list[dict[str, Any]] = []
    namespace_seen: dict[str, str] = {}
    prohibited = tuple(config.get("prohibited_prefixes", []))

    for obj in config["objects"]:
        object_id = obj["object_id"]
        mapping_path = resolve_feature_path(obj["mapping_doc"])
        validation_path = resolve_feature_path(obj["builder_validation_doc"])
        add_gate(pass_fail, object_id=object_id, gate="mapping_doc_exists", status="PASS" if mapping_path.exists() else "FAIL", severity="INFO" if mapping_path.exists() else "FAIL", finding="mapping artifact found" if mapping_path.exists() else "mapping artifact missing", evidence=str(mapping_path))
        add_gate(pass_fail, object_id=object_id, gate="builder_validation_doc_exists", status="PASS" if validation_path.exists() else "FAIL", severity="INFO" if validation_path.exists() else "FAIL", finding="builder validation artifact found" if validation_path.exists() else "builder validation artifact missing", evidence=str(validation_path))

        namespace = obj.get("state_namespace", "")
        if namespace in namespace_seen:
            add_gate(pass_fail, object_id=object_id, gate="namespace_uniqueness", status="FAIL", severity="FAIL", finding=f"namespace duplicates {namespace_seen[namespace]}", evidence=namespace)
        else:
            namespace_seen[namespace] = object_id
            add_gate(pass_fail, object_id=object_id, gate="namespace_uniqueness", status="PASS", severity="INFO", finding="namespace is unique", evidence=namespace)

        status = obj.get("validation_status")
        if status == "blocked_pending_state_capability_prerequisites":
            add_gate(pass_fail, object_id=object_id, gate="object_execution_status", status="BLOCKED_EXPECTED", severity="BLOCKED_EXPECTED", finding="object correctly blocked pending prerequisites", evidence=";".join(obj.get("unblock_requires", [])))
        else:
            add_gate(pass_fail, object_id=object_id, gate="object_execution_status", status="PASS", severity="INFO", finding="object ready for non-production resolution probe", evidence=str(status))

        active_caps = set(obj.get("required_capabilities", [])) | set(obj.get("optional_capabilities", []))
        for cap in sorted(active_caps):
            leak = cap.startswith(prohibited)
            add_gate(pass_fail, object_id=object_id, gate="prohibited_prefix_check", status="FAIL" if leak else "PASS", severity="FAIL" if leak else "INFO", finding=f"active capability {'uses' if leak else 'does not use'} prohibited prefix", evidence=cap)
        for cap in sorted(obj.get("blocked_capabilities", [])):
            active_leak = cap in active_caps
            blocked_rows.append({"object_id": object_id, "capability": cap, "status": "LEAK" if active_leak else "MASKED", "severity": "FAIL" if active_leak else "INFO"})
            if active_leak:
                add_gate(pass_fail, object_id=object_id, gate="blocked_capability_mask", status="FAIL", severity="FAIL", finding="blocked capability appears in active capability set", evidence=cap)

        check_sources(obj, registry_doc, source_rows, pass_fail, check_physical_paths=check_physical_paths)
        lineage_rows.append({
            "object_id": object_id,
            "display_name": obj.get("display_name"),
            "mapping_doc": str(mapping_path),
            "builder_validation_doc": str(validation_path),
            "active_source_aliases": obj.get("active_source_aliases", []),
            "blocked_source_aliases": obj.get("blocked_source_aliases", []),
            "required_capabilities": obj.get("required_capabilities", []),
            "optional_capabilities": obj.get("optional_capabilities", []),
            "blocked_capabilities": obj.get("blocked_capabilities", []),
            "lineage_status": "doc_lineage_ready_pending_physical_binding",
        })
    return pass_fail, source_rows, blocked_rows, lineage_rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def write_dry_rows(path: Path, config: dict[str, Any], sample_tickers: list[str], sample_decision_timestamps: list[str]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for ticker in sample_tickers:
            for decision_ts in sample_decision_timestamps:
                for obj in config["objects"]:
                    payload = {
                        "experimental_snapshot": True,
                        "not_state_authority": True,
                        "object_id": obj["object_id"],
                        "ticker": ticker,
                        "decision_timestamp_utc": decision_ts,
                        "resolution_status": obj.get("validation_status"),
                        "active_source_aliases": obj.get("active_source_aliases", []),
                        "required_capabilities": obj.get("required_capabilities", []),
                        "optional_capabilities": obj.get("optional_capabilities", []),
                        "blocked_capabilities_masked": True,
                    }
                    handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
                    handle.write("\n")
                    count += 1
    return count


def alias_metrics(config: dict[str, Any], registry_doc: dict[str, Any], source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    active_usages: list[str] = []
    blocked_usages: list[str] = []
    for obj in config["objects"]:
        active_usages.extend(obj.get("active_source_aliases", []))
        blocked_usages.extend(obj.get("blocked_source_aliases", []))
    active_aliases = sorted(set(active_usages))
    blocked_aliases = sorted(set(blocked_usages))
    bindings = registry_doc["bindings"]
    bound_active = []
    unbound_active = []
    for alias in active_aliases:
        binding = bindings.get(alias)
        if binding and binding.get("physical_candidate_root") and binding.get("binding_status") != "blocked":
            bound_active.append(alias)
        else:
            unbound_active.append(alias)
    checked_roots = sorted({str(row.get("physical_candidate_root")) for row in source_rows if row.get("path_check_status") in {"FOUND", "MISSING"} and row.get("physical_candidate_root")})
    found_roots = sorted({str(row.get("physical_candidate_root")) for row in source_rows if row.get("path_check_status") == "FOUND" and row.get("physical_candidate_root")})
    missing_roots = sorted({str(row.get("physical_candidate_root")) for row in source_rows if row.get("path_check_status") == "MISSING" and row.get("physical_candidate_root")})
    return {
        "active_source_alias_usages": len(active_usages),
        "unique_active_source_aliases": len(active_aliases),
        "unique_active_source_alias_names": active_aliases,
        "bound_unique_source_aliases": len(bound_active),
        "bound_unique_source_alias_names": bound_active,
        "unbound_unique_source_aliases": len(unbound_active),
        "unbound_unique_source_alias_names": unbound_active,
        "blocked_unique_source_aliases": len(blocked_aliases),
        "blocked_unique_source_alias_names": blocked_aliases,
        "physical_paths_checked": len(checked_roots),
        "physical_paths_found": len(found_roots),
        "physical_paths_missing": len(missing_roots),
        "binding_registry_id": registry_doc.get("registry_id"),
    }


def summarize(config: dict[str, Any], registry_doc: dict[str, Any], pass_fail: list[dict[str, Any]], source_rows: list[dict[str, Any]], blocked_rows: list[dict[str, Any]]) -> dict[str, Any]:
    fail_count = sum(1 for row in pass_fail if row["severity"] == "FAIL")
    warn_count = sum(1 for row in pass_fail if row["severity"] == "WARN")
    pass_count = sum(1 for row in pass_fail if row["status"] == "PASS")
    pass_with_finding_count = sum(1 for row in pass_fail if row["status"] == "PASS_WITH_FINDING")
    source_warn_count = sum(1 for row in source_rows if row["severity"] == "WARN")
    source_fail_count = sum(1 for row in source_rows if row["severity"] == "FAIL")
    blocked_expected = sum(1 for row in pass_fail if row["severity"] == "BLOCKED_EXPECTED")
    blocked_leaks = sum(1 for row in blocked_rows if row["status"] == "LEAK")
    metrics = alias_metrics(config, registry_doc, source_rows)
    if fail_count or source_fail_count or blocked_leaks:
        status = "failed_contract_check"
    elif source_warn_count or metrics["unbound_unique_source_aliases"]:
        status = "passed_contract_check_pending_source_binding"
    elif warn_count or blocked_expected:
        status = "passed_with_findings_and_expected_blocks"
    else:
        status = "passed"
    physical_source_binding = "PASS"
    if metrics["unbound_unique_source_aliases"]:
        physical_source_binding = "INCOMPLETE"
    if metrics["physical_paths_missing"] or source_fail_count:
        physical_source_binding = "FAILED"
    return {
        "overall_status": status,
        "contract_resolution": "PASS" if not fail_count and not source_fail_count else "FAIL",
        "ontology_to_mapping_resolution": "PASS" if not fail_count else "FAIL",
        "blocked_capability_masking": "PASS" if blocked_leaks == 0 else "FAIL",
        "order_flow_expected_block": "PASS" if blocked_expected else "NOT_PRESENT",
        "physical_source_binding": physical_source_binding,
        "schema_resolution": "NOT_EXECUTED",
        "data_resolution": "NOT_AUTHORIZED",
        "fail_count": fail_count + source_fail_count,
        "contract_fail_count": fail_count,
        "source_fail_count": source_fail_count,
        "warn_count": warn_count,
        "source_warn_count": source_warn_count,
        "pass_count": pass_count,
        "pass_with_finding_count": pass_with_finding_count,
        "blocked_expected_count": blocked_expected,
        "blocked_capability_leaks": blocked_leaks,
        **metrics,
    }


def write_findings(path: Path, *, run_id: str, summary: dict[str, Any], source_rows: list[dict[str, Any]]) -> None:
    source_findings = [row for row in source_rows if row["role"] == "active" and row["severity"] in {"WARN", "FAIL"}]
    if summary["fail_count"]:
        interpretation = "Contract or governance failures were detected."
    else:
        interpretation = "No contract or governance failures were detected."
    lines = [
        f"# Experimental State Builder Probe Findings - {run_id}",
        "",
        f"script_version: `{SCRIPT_VERSION}`",
        f"overall_status: `{summary['overall_status']}`",
        "",
        "## Institutional Status",
        "",
        f"contract_resolution = {summary['contract_resolution']}",
        f"ontology_to_mapping_resolution = {summary['ontology_to_mapping_resolution']}",
        f"blocked_capability_masking = {summary['blocked_capability_masking']}",
        f"order_flow_expected_block = {summary['order_flow_expected_block']}",
        f"physical_source_binding = {summary['physical_source_binding']}",
        f"schema_resolution = {summary['schema_resolution']}",
        f"data_resolution = {summary['data_resolution']}",
        "",
        "## Summary",
        "",
        f"pass_count = {summary['pass_count']}",
        f"pass_with_finding_count = {summary['pass_with_finding_count']}",
        f"fail_count = {summary['fail_count']}",
        f"warn_count = {summary['warn_count']}",
        f"source_warn_count = {summary['source_warn_count']}",
        f"blocked_expected_count = {summary['blocked_expected_count']}",
        f"blocked_capability_leaks = {summary['blocked_capability_leaks']}",
        f"active_source_alias_usages = {summary['active_source_alias_usages']}",
        f"unique_active_source_aliases = {summary['unique_active_source_aliases']}",
        f"bound_unique_source_aliases = {summary['bound_unique_source_aliases']}",
        f"unbound_unique_source_aliases = {summary['unbound_unique_source_aliases']}",
        f"blocked_unique_source_aliases = {summary['blocked_unique_source_aliases']}",
        f"physical_paths_checked = {summary['physical_paths_checked']}",
        f"physical_paths_found = {summary['physical_paths_found']}",
        f"physical_paths_missing = {summary['physical_paths_missing']}",
        "",
        "## Interpretation",
        "",
        interpretation,
        "",
        "The run cannot yet evaluate physical resolvability because active source surfaces remain unbound in the experimental registry.",
    ]
    if source_findings:
        lines.extend(["", "## Active Source Binding Findings", ""])
        for row in source_findings:
            lines.append(f"- {row['object_id']} -> {row['source_alias']}: {row['finding']} (binding_status={row['binding_status']})")
    lines.extend([
        "",
        "## Next Action",
        "",
        "Bind the 10 unique active source aliases to governed experimental physical candidate roots, then rerun the probe in `binding_and_schema_check_only` mode.",
        "",
        "Do not enable data reads or materialization from this artifact.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Experimental State Builder probe")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--sample-ticker", action="append", dest="sample_tickers")
    parser.add_argument("--sample-decision-timestamp", action="append", dest="sample_decision_timestamps")
    parser.add_argument("--emit-dry-run-rows", action="store_true")
    parser.add_argument("--check-physical-paths", action="store_true")
    parser.add_argument("--allow-data-read", action="store_true", help="Reserved for later probe versions; v0.2 rejects data reads.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.allow_data_read:
        raise ProbeError("v0.2 refuses data reads")

    config_path = args.config.resolve()
    config = read_json(config_path)
    validate_config(config)
    registry_doc, registry_path, registry_sha256 = load_binding_registry(config, config_path)
    run_id = args.run_id or f"{SCRIPT_VERSION}_{safe_timestamp()}"
    run_dir = ensure_output_dir(args.output_root, run_id)

    pre_manifest = {
        "run_id": run_id,
        "status": "starting",
        "created_at_utc": utc_now(),
        "script_path": str(SCRIPT_PATH),
        "script_version": SCRIPT_VERSION,
        "probe_id": PROBE_ID,
        "script_sha256": sha256_file(SCRIPT_PATH),
        "command_line": " ".join(sys.argv),
        "cwd": os.getcwd(),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getppid(),
        "pid": os.getpid(),
        "mode": config["mode"],
        "dry_run": True,
        "allow_data_read": False,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "source_binding_registry_path": str(registry_path) if registry_path else None,
        "source_binding_registry_sha256": registry_sha256,
        "source_binding_registry_id": registry_doc.get("registry_id"),
        "output_root": str(args.output_root.resolve()),
        "run_dir": str(run_dir),
        "expected_scope": "12 objects, binding/schema metadata probe only",
        "overwrite_policy": "refuse_existing_run_dir",
        **git_info(),
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {
        "run_id": run_id,
        "status": "running",
        "updated_at_utc": utc_now(),
        "current_step": "binding_and_schema_contract_check",
    })

    pass_fail, source_rows, blocked_rows, lineage_rows = check_objects(config, registry_doc, check_physical_paths=args.check_physical_paths)
    write_csv(run_dir / "pass_fail_matrix.csv", pass_fail, ["object_id", "gate", "status", "severity", "finding", "evidence"])
    write_csv(run_dir / "source_availability_report.csv", source_rows, [
        "object_id",
        "source_alias",
        "role",
        "binding_status",
        "governance_status",
        "physical_candidate_root",
        "dataset_format",
        "expected_grain",
        "expected_primary_keys",
        "temporal_fields",
        "minimum_required_columns",
        "path_root_status",
        "path_check_status",
        "schema_probe_authorized",
        "read_authorized",
        "severity",
        "finding",
    ])
    write_csv(run_dir / "blocked_capability_report.csv", blocked_rows, ["object_id", "capability", "status", "severity"])
    write_json(run_dir / "lineage_report.json", lineage_rows)

    sample_tickers = args.sample_tickers or config.get("sample_tickers", [])
    sample_decision_timestamps = args.sample_decision_timestamps or config.get("sample_decision_timestamps", [])
    dry_rows = 0
    if args.emit_dry_run_rows:
        dry_rows = write_dry_rows(run_dir / "dry_run_resolution_snapshots.jsonl", config, sample_tickers, sample_decision_timestamps)

    summary = summarize(config, registry_doc, pass_fail, source_rows, blocked_rows)
    write_findings(run_dir / "experimental_findings.md", run_id=run_id, summary=summary, source_rows=source_rows)
    artifacts = {
        "pre_manifest": str(run_dir / "pre_manifest.json"),
        "heartbeat": str(run_dir / "heartbeat.json"),
        "pass_fail_matrix": str(run_dir / "pass_fail_matrix.csv"),
        "source_availability_report": str(run_dir / "source_availability_report.csv"),
        "blocked_capability_report": str(run_dir / "blocked_capability_report.csv"),
        "lineage_report": str(run_dir / "lineage_report.json"),
        "experimental_findings": str(run_dir / "experimental_findings.md"),
        "final_manifest": str(run_dir / "final_manifest.json"),
    }
    if args.emit_dry_run_rows:
        artifacts["dry_run_resolution_snapshots"] = str(run_dir / "dry_run_resolution_snapshots.jsonl")
    final_manifest = {
        **pre_manifest,
        "status": "complete",
        "completed_at_utc": utc_now(),
        "overall_status": summary["overall_status"],
        "objects_checked": len(config["objects"]),
        "source_rows": len(source_rows),
        "pass_fail_rows": len(pass_fail),
        "blocked_capability_rows": len(blocked_rows),
        "dry_run_resolution_snapshots": dry_rows,
        "official_output_allowed": False,
        "official_output_materialized": False,
        "state_consumption_authorized": False,
        "physical_materialization_authorized": False,
        "dataset_promotion_authorized": False,
        "artifacts": artifacts,
        **summary,
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {
        "run_id": run_id,
        "status": "complete",
        "updated_at_utc": utc_now(),
        "current_step": "complete",
        "overall_status": summary["overall_status"],
    })
    print(json.dumps({"run_id": run_id, "run_dir": str(run_dir), **summary}, indent=2))
    return 0 if summary["overall_status"] != "failed_contract_check" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
