from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any


PROBE_ID = "experimental_state_builder_probe_v0_1"
SCRIPT_VERSION = "experimental_state_builder_probe_v0_10"
SCRIPT_PATH = Path(__file__).resolve()
PROBE_ROOT = SCRIPT_PATH.parents[1]
VALIDATION_ROOT = PROBE_ROOT.parent
FEATURE_ENGINEERING_ROOT = VALIDATION_ROOT.parent
DEFAULT_CONFIG = PROBE_ROOT / "configs" / "experimental_state_builder_probe_v0_1.json"
DEFAULT_RUN_ROOT = PROBE_ROOT / "runs"
SCHEMA_MODE = "binding_and_schema_check_only"
COLUMN_BINDING_MODE = "logical_to_physical_binding_check_only"
BOUNDED_SAMPLE_MODE = "bounded_identity_and_temporal_validation"
BOUNDED_GRAIN_MODE = "bounded_grain_validation"
BOUNDED_QUALITY_LINEAGE_MODE = "bounded_quality_and_lineage_validation"
CORE_FOUR_BUILDER_MODE = "experimental_builder_validation_execution_core_four"
SUPPORTED_MODES = {"contract_check_only", "binding_and_path_check_only", SCHEMA_MODE, COLUMN_BINDING_MODE, BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE}
SCHEMA_METADATA_SCOPE = "filesystem_and_schema_metadata_only"
COLUMN_BINDING_SCOPE = "logical_to_physical_binding_metadata_only"
BOUNDED_SAMPLE_SCOPE = "bounded_identity_temporal_limited_row_read"
BOUNDED_GRAIN_SCOPE = "bounded_grain_limited_row_read"
BOUNDED_QUALITY_LINEAGE_SCOPE = "bounded_quality_lineage_limited_row_read"
CORE_FOUR_BUILDER_SCOPE = "core_four_builder_validation_execution_limited"

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
    "state_materialization_allowed",
)

BOUNDED_SCOPE_FALSE_FLAGS = (
    "production_builder_authorized",
    "state_consumption_authorized",
    "physical_materialization_authorized",
    "dataset_promotion_authorized",
    "full_data_read_allowed",
    "state_materialization_allowed",
    "writes_to_source_allowed",
)

FIRST_BOUNDED_SAMPLE_ALIASES = {
    "004_master_daily_table",
    "013_ohlcv_1m_quote_guarded",
    "014_master_intraday_bar_table_candidate",
    "015_microstructure_features_table_candidate",
    "raw_quotes",
}

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


def resolve_policy_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROBE_ROOT / "policies" / value).resolve()


def ensure_output_dir(output_root: Path, run_id: str) -> Path:
    root = output_root.resolve()
    workspace_root = Path("C:/TSIS_Data").resolve()
    if not is_within_or_equal(root, workspace_root):
        raise ProbeError(f"output root must be under {workspace_root}: {root}")
    run_dir = (root / run_id).resolve()
    if not is_within_or_equal(run_dir, root):
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
    if config.get("mode") in {COLUMN_BINDING_MODE, BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE} and "column_binding_registry" not in config:
        raise ProbeError("config must reference column_binding_registry for logical-to-physical or bounded row-read modes")
    if config.get("mode") == BOUNDED_SAMPLE_MODE and "bounded_sample_scope" not in config:
        raise ProbeError("config must reference bounded_sample_scope for bounded_identity_and_temporal_validation")
    if config.get("mode") == BOUNDED_GRAIN_MODE and "bounded_grain_scope" not in config:
        raise ProbeError("config must reference bounded_grain_scope for bounded_grain_validation")
    if config.get("mode") == BOUNDED_QUALITY_LINEAGE_MODE and "bounded_quality_lineage_scope" not in config:
        raise ProbeError("config must reference bounded_quality_lineage_scope for bounded_quality_and_lineage_validation")
    if config.get("mode") == CORE_FOUR_BUILDER_MODE and "core_four_builder_scope" not in config:
        raise ProbeError("config must reference core_four_builder_scope for experimental_builder_validation_execution_core_four")


def validate_registry(registry_doc: dict[str, Any], mode: str) -> None:
    if registry_doc.get("registry_status") != "experimental_non_production":
        raise ProbeError("source binding registry must be experimental_non_production")
    authority = registry_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("source binding registry must declare authority")
    for flag in REGISTRY_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"registry authority flag {flag} must be false")
    if mode in {"binding_and_path_check_only", SCHEMA_MODE, COLUMN_BINDING_MODE, BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE}:
        if authority.get("filesystem_metadata_read_allowed") is not True:
            raise ProbeError(f"filesystem metadata reads must be allowed for {mode}")
    if mode in {SCHEMA_MODE, COLUMN_BINDING_MODE, BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE}:
        if authority.get("schema_metadata_read_allowed") is not True:
            raise ProbeError(f"schema metadata reads must be allowed for {mode}")
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


def load_binding_registry(config: dict[str, Any], config_path: Path, mode: str) -> tuple[dict[str, Any], Path | None, str | None]:
    registry_ref = config.get("source_binding_registry")
    if registry_ref:
        registry_path = resolve_registry_path(str(registry_ref), config_path).resolve()
        registry_doc = read_json(registry_path)
        validate_registry(registry_doc, mode)
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


def validate_column_binding_registry(column_doc: dict[str, Any], source_registry_doc: dict[str, Any]) -> None:
    if column_doc.get("registry_status") != "experimental_non_production":
        raise ProbeError("column binding registry must be experimental_non_production")
    authority = column_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("column binding registry must declare authority")
    for flag in REGISTRY_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"column binding authority flag {flag} must be false")
    if authority.get("filesystem_metadata_read_allowed") is not True:
        raise ProbeError("column binding registry must allow filesystem metadata reads only")
    if authority.get("schema_metadata_read_allowed") is not True:
        raise ProbeError("column binding registry must allow schema metadata reads only")
    bindings = column_doc.get("bindings")
    if not isinstance(bindings, dict) or not bindings:
        raise ProbeError("column binding registry must declare bindings")
    active_aliases = {alias for alias, binding in source_registry_doc.get("bindings", {}).items() if binding.get("binding_status") != "blocked"}
    missing_aliases = sorted(active_aliases - set(bindings))
    if missing_aliases:
        raise ProbeError(f"column binding registry missing active aliases: {', '.join(missing_aliases)}")
    required_entry_fields = {
        "source_alias",
        "logical_field",
        "logical_field_groups",
        "binding_status",
        "physical_resolution_type",
        "expected_type_family",
        "semantic_role",
        "criticality",
        "review_status",
        "binding_evidence",
    }
    allowed_resolution_types = set(column_doc.get("physical_resolution_types", []))
    for alias in sorted(active_aliases):
        alias_bindings = bindings.get(alias)
        if not isinstance(alias_bindings, dict) or not alias_bindings:
            raise ProbeError(f"column bindings for {alias} must be a non-empty object")
        source_binding = source_registry_doc["bindings"][alias]
        expected_fields = set(source_binding.get("minimum_required_columns", []))
        for key in ("event_timestamp_field", "availability_timestamp_field", "as_of_field", "valid_from_field", "valid_to_field"):
            value = source_binding.get(key)
            if value:
                expected_fields.add(str(value))
        expected_fields.update(source_binding.get("quality_fields", []))
        expected_fields.update(source_binding.get("lineage_fields", []))
        missing_fields = sorted(expected_fields - set(alias_bindings))
        if missing_fields:
            raise ProbeError(f"column binding registry for {alias} missing logical fields: {', '.join(missing_fields)}")
        for logical_field, binding in alias_bindings.items():
            if not isinstance(binding, dict):
                raise ProbeError(f"column binding {alias}.{logical_field} must be an object")
            missing = sorted(required_entry_fields - set(binding))
            if missing:
                raise ProbeError(f"column binding {alias}.{logical_field} missing fields: {', '.join(missing)}")
            if binding.get("source_alias") != alias:
                raise ProbeError(f"column binding source_alias mismatch for {alias}.{logical_field}")
            if binding.get("logical_field") != logical_field:
                raise ProbeError(f"column binding logical_field mismatch for {alias}.{logical_field}")
            resolution_type = binding.get("physical_resolution_type")
            if allowed_resolution_types and resolution_type not in allowed_resolution_types:
                raise ProbeError(f"column binding {alias}.{logical_field} has unsupported physical_resolution_type={resolution_type}")


def load_column_binding_registry(config: dict[str, Any], config_path: Path, source_registry_doc: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None, str | None]:
    registry_ref = config.get("column_binding_registry")
    if not registry_ref:
        return None, None, None
    registry_path = resolve_registry_path(str(registry_ref), config_path).resolve()
    registry_doc = read_json(registry_path)
    validate_column_binding_registry(registry_doc, source_registry_doc)
    return registry_doc, registry_path, sha256_file(registry_path)


def validate_bounded_sample_scope(scope_doc: dict[str, Any], config: dict[str, Any], source_registry_doc: dict[str, Any]) -> None:
    if scope_doc.get("scope_status") != "experimental_non_production":
        raise ProbeError("bounded sample scope must be experimental_non_production")
    if scope_doc.get("mode") != BOUNDED_SAMPLE_MODE:
        raise ProbeError(f"bounded sample scope mode must be {BOUNDED_SAMPLE_MODE}")
    authority = scope_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("bounded sample scope must declare authority")
    if authority.get("bounded_sample_data_read_allowed") is not True:
        raise ProbeError("bounded sample scope must explicitly allow bounded sample data reads")
    for flag in BOUNDED_SCOPE_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"bounded sample scope authority flag {flag} must be false")
    limits = scope_doc.get("global_limits")
    if not isinstance(limits, dict):
        raise ProbeError("bounded sample scope must declare global_limits")
    max_sources = int(limits.get("maximum_sources", 0))
    max_files = int(limits.get("maximum_files_per_source", 0))
    max_rows = int(limits.get("maximum_rows_per_file", 0))
    max_total_rows = int(limits.get("maximum_total_rows", 0))
    if limits.get("full_scan_allowed") is not False:
        raise ProbeError("bounded sample scope must keep full_scan_allowed=false")
    if max_sources <= 0 or max_sources > 5:
        raise ProbeError("bounded sample scope maximum_sources must be between 1 and 5")
    if max_files <= 0 or max_files > 3:
        raise ProbeError("bounded sample scope maximum_files_per_source must be between 1 and 3")
    if max_rows <= 0 or max_rows > 1000:
        raise ProbeError("bounded sample scope maximum_rows_per_file must be between 1 and 1000")
    if max_total_rows <= 0 or max_total_rows > 10000:
        raise ProbeError("bounded sample scope maximum_total_rows must be between 1 and 10000")
    sources = scope_doc.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ProbeError("bounded sample scope must declare sources")
    source_aliases = set(sources)
    active_aliases = set(unique_active_aliases(config))
    if not source_aliases <= FIRST_BOUNDED_SAMPLE_ALIASES:
        extra = sorted(source_aliases - FIRST_BOUNDED_SAMPLE_ALIASES)
        raise ProbeError(f"bounded sample scope includes aliases outside first bounded gate: {', '.join(extra)}")
    if not source_aliases <= active_aliases:
        extra = sorted(source_aliases - active_aliases)
        raise ProbeError(f"bounded sample scope includes aliases not active in config: {', '.join(extra)}")
    if len(source_aliases) > max_sources:
        raise ProbeError("bounded sample source count exceeds maximum_sources")
    source_bindings = source_registry_doc.get("bindings", {})
    for alias, source_scope in sources.items():
        if alias not in source_bindings or source_bindings[alias].get("binding_status") == "blocked":
            raise ProbeError(f"bounded sample source {alias} is not an active bound source")
        if not isinstance(source_scope, dict):
            raise ProbeError(f"bounded sample source scope for {alias} must be an object")
        allowed_columns = source_scope.get("allowed_columns")
        if not isinstance(allowed_columns, list) or not allowed_columns:
            raise ProbeError(f"bounded sample source {alias} must declare allowed_columns")
        if int(source_scope.get("max_files", 0)) <= 0 or int(source_scope.get("max_files", 0)) > max_files:
            raise ProbeError(f"bounded sample source {alias} exceeds maximum_files_per_source")
        if int(source_scope.get("max_rows_per_file", 0)) <= 0 or int(source_scope.get("max_rows_per_file", 0)) > max_rows:
            raise ProbeError(f"bounded sample source {alias} exceeds maximum_rows_per_file")


def load_bounded_sample_scope(config: dict[str, Any], config_path: Path, source_registry_doc: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None, str | None]:
    if config.get("mode") != BOUNDED_SAMPLE_MODE:
        return None, None, None
    scope_ref = config.get("bounded_sample_scope")
    if not scope_ref:
        return None, None, None
    scope_path = resolve_registry_path(str(scope_ref), config_path).resolve()
    scope_doc = read_json(scope_path)
    validate_bounded_sample_scope(scope_doc, config, source_registry_doc)
    return scope_doc, scope_path, sha256_file(scope_path)



def validate_bounded_grain_scope(scope_doc: dict[str, Any], config: dict[str, Any], source_registry_doc: dict[str, Any]) -> None:
    if scope_doc.get("scope_status") != "experimental_non_production":
        raise ProbeError("bounded grain scope must be experimental_non_production")
    if scope_doc.get("mode") != BOUNDED_GRAIN_MODE:
        raise ProbeError(f"bounded grain scope mode must be {BOUNDED_GRAIN_MODE}")
    authority = scope_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("bounded grain scope must declare authority")
    if authority.get("bounded_sample_data_read_allowed") is not True:
        raise ProbeError("bounded grain scope must explicitly allow bounded sample data reads")
    for flag in BOUNDED_SCOPE_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"bounded grain scope authority flag {flag} must be false")
    limits = scope_doc.get("global_limits")
    if not isinstance(limits, dict):
        raise ProbeError("bounded grain scope must declare global_limits")
    max_sources = int(limits.get("maximum_sources", 0))
    max_files = int(limits.get("maximum_files_per_source", 0))
    max_rows = int(limits.get("maximum_rows_per_file", 0))
    max_total_rows = int(limits.get("maximum_total_rows", 0))
    if limits.get("full_scan_allowed") is not False:
        raise ProbeError("bounded grain scope must keep full_scan_allowed=false")
    if max_sources <= 0 or max_sources > 5:
        raise ProbeError("bounded grain scope maximum_sources must be between 1 and 5")
    if max_files <= 0 or max_files > 3:
        raise ProbeError("bounded grain scope maximum_files_per_source must be between 1 and 3")
    if max_rows <= 0 or max_rows > 2000:
        raise ProbeError("bounded grain scope maximum_rows_per_file must be between 1 and 2000")
    if max_total_rows <= 0 or max_total_rows > 20000:
        raise ProbeError("bounded grain scope maximum_total_rows must be between 1 and 20000")
    sources = scope_doc.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ProbeError("bounded grain scope must declare sources")
    source_aliases = set(sources)
    active_aliases = set(unique_active_aliases(config))
    if not source_aliases <= FIRST_BOUNDED_SAMPLE_ALIASES:
        extra = sorted(source_aliases - FIRST_BOUNDED_SAMPLE_ALIASES)
        raise ProbeError(f"bounded grain scope includes aliases outside first bounded gates: {', '.join(extra)}")
    if not source_aliases <= active_aliases:
        extra = sorted(source_aliases - active_aliases)
        raise ProbeError(f"bounded grain scope includes aliases not active in config: {', '.join(extra)}")
    if len(source_aliases) > max_sources:
        raise ProbeError("bounded grain source count exceeds maximum_sources")
    source_bindings = source_registry_doc.get("bindings", {})
    for alias, source_scope in sources.items():
        if alias not in source_bindings or source_bindings[alias].get("binding_status") == "blocked":
            raise ProbeError(f"bounded grain source {alias} is not an active bound source")
        if not isinstance(source_scope, dict):
            raise ProbeError(f"bounded grain source scope for {alias} must be an object")
        allowed_columns = source_scope.get("allowed_columns")
        if not isinstance(allowed_columns, list) or not allowed_columns:
            raise ProbeError(f"bounded grain source {alias} must declare allowed_columns")
        if int(source_scope.get("max_files", 0)) <= 0 or int(source_scope.get("max_files", 0)) > max_files:
            raise ProbeError(f"bounded grain source {alias} exceeds maximum_files_per_source")
        if int(source_scope.get("max_rows_per_file", 0)) <= 0 or int(source_scope.get("max_rows_per_file", 0)) > max_rows:
            raise ProbeError(f"bounded grain source {alias} exceeds maximum_rows_per_file")
        for key_name in ("physical_key_components", "canonical_key_components"):
            components = source_scope.get(key_name)
            if not isinstance(components, list) or not components:
                raise ProbeError(f"bounded grain source {alias} must declare {key_name}")
            for component in components:
                component_text = str(component)
                if component_text.startswith("partition:"):
                    continue
                if component_text not in allowed_columns:
                    raise ProbeError(f"bounded grain source {alias} key component {component_text} is not in allowed_columns")


def load_bounded_grain_scope(config: dict[str, Any], config_path: Path, source_registry_doc: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None, str | None]:
    if config.get("mode") != BOUNDED_GRAIN_MODE:
        return None, None, None
    scope_ref = config.get("bounded_grain_scope")
    if not scope_ref:
        return None, None, None
    scope_path = resolve_registry_path(str(scope_ref), config_path).resolve()
    scope_doc = read_json(scope_path)
    validate_bounded_grain_scope(scope_doc, config, source_registry_doc)
    return scope_doc, scope_path, sha256_file(scope_path)

def validate_bounded_quality_lineage_scope(scope_doc: dict[str, Any], config: dict[str, Any], source_registry_doc: dict[str, Any]) -> None:
    if scope_doc.get("scope_status") != "experimental_non_production":
        raise ProbeError("bounded quality/lineage scope must be experimental_non_production")
    if scope_doc.get("mode") != BOUNDED_QUALITY_LINEAGE_MODE:
        raise ProbeError(f"bounded quality/lineage scope mode must be {BOUNDED_QUALITY_LINEAGE_MODE}")
    authority = scope_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("bounded quality/lineage scope must declare authority")
    if authority.get("bounded_sample_data_read_allowed") is not True:
        raise ProbeError("bounded quality/lineage scope must explicitly allow bounded sample data reads")
    for flag in BOUNDED_SCOPE_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"bounded quality/lineage scope authority flag {flag} must be false")
    if authority.get("feature_builder_execution_allowed") is not False:
        raise ProbeError("bounded quality/lineage scope must keep feature_builder_execution_allowed=false")
    limits = scope_doc.get("global_limits")
    if not isinstance(limits, dict):
        raise ProbeError("bounded quality/lineage scope must declare global_limits")
    max_sources = int(limits.get("maximum_sources", 0))
    max_files = int(limits.get("maximum_files_per_source", 0))
    max_rows = int(limits.get("maximum_rows_per_file", 0))
    max_total_rows = int(limits.get("maximum_total_rows", 0))
    if limits.get("full_scan_allowed") is not False:
        raise ProbeError("bounded quality/lineage scope must keep full_scan_allowed=false")
    if max_sources <= 0 or max_sources > 5:
        raise ProbeError("bounded quality/lineage scope maximum_sources must be between 1 and 5")
    if max_files <= 0 or max_files > 3:
        raise ProbeError("bounded quality/lineage scope maximum_files_per_source must be between 1 and 3")
    if max_rows <= 0 or max_rows > 2000:
        raise ProbeError("bounded quality/lineage scope maximum_rows_per_file must be between 1 and 2000")
    if max_total_rows <= 0 or max_total_rows > 20000:
        raise ProbeError("bounded quality/lineage scope maximum_total_rows must be between 1 and 20000")
    sources = scope_doc.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ProbeError("bounded quality/lineage scope must declare sources")
    source_aliases = set(sources)
    active_aliases = set(unique_active_aliases(config))
    if not source_aliases <= FIRST_BOUNDED_SAMPLE_ALIASES:
        extra = sorted(source_aliases - FIRST_BOUNDED_SAMPLE_ALIASES)
        raise ProbeError(f"bounded quality/lineage scope includes aliases outside first bounded gates: {', '.join(extra)}")
    if not source_aliases <= active_aliases:
        extra = sorted(source_aliases - active_aliases)
        raise ProbeError(f"bounded quality/lineage scope includes aliases not active in config: {', '.join(extra)}")
    if len(source_aliases) > max_sources:
        raise ProbeError("bounded quality/lineage source count exceeds maximum_sources")
    source_bindings = source_registry_doc.get("bindings", {})
    for alias, source_scope in sources.items():
        if alias not in source_bindings or source_bindings[alias].get("binding_status") == "blocked":
            raise ProbeError(f"bounded quality/lineage source {alias} is not an active bound source")
        if not isinstance(source_scope, dict):
            raise ProbeError(f"bounded quality/lineage source scope for {alias} must be an object")
        allowed_columns = source_scope.get("allowed_columns")
        if not isinstance(allowed_columns, list) or not allowed_columns:
            raise ProbeError(f"bounded quality/lineage source {alias} must declare allowed_columns")
        if int(source_scope.get("max_files", 0)) <= 0 or int(source_scope.get("max_files", 0)) > max_files:
            raise ProbeError(f"bounded quality/lineage source {alias} exceeds maximum_files_per_source")
        if int(source_scope.get("max_rows_per_file", 0)) <= 0 or int(source_scope.get("max_rows_per_file", 0)) > max_rows:
            raise ProbeError(f"bounded quality/lineage source {alias} exceeds maximum_rows_per_file")
        policy_refs = source_scope.get("policy_refs", [])
        if not isinstance(policy_refs, list):
            raise ProbeError(f"bounded quality/lineage source {alias} policy_refs must be a list")
        for policy_ref in policy_refs:
            if str(policy_ref) and not resolve_policy_path(str(policy_ref)).exists():
                raise ProbeError(f"bounded quality/lineage policy missing for {alias}: {policy_ref}")
        checks = source_scope.get("quality_lineage_checks")
        if not isinstance(checks, list):
            raise ProbeError(f"bounded quality/lineage source {alias} must declare quality_lineage_checks")
        fields = source_scope.get("quality_lineage_fields")
        if not isinstance(fields, list) or not fields:
            raise ProbeError(f"bounded quality/lineage source {alias} must declare quality_lineage_fields")
        check_ids = {str(check.get("check_id")) for check in checks if isinstance(check, dict)}
        for field in fields:
            if not isinstance(field, dict):
                raise ProbeError(f"bounded quality/lineage field entry for {alias} must be an object")
            for required in ("logical_field", "field_family", "resolution_strategy", "criticality", "builder_blocker_scope", "builder_execution_impact", "promotion_impact"):
                if required not in field:
                    raise ProbeError(f"bounded quality/lineage field for {alias} missing {required}")
            policy_check = str(field.get("policy_check", ""))
            if policy_check and policy_check not in check_ids:
                raise ProbeError(f"bounded quality/lineage field {alias}.{field.get('logical_field')} references unknown policy_check={policy_check}")


def load_bounded_quality_lineage_scope(config: dict[str, Any], config_path: Path, source_registry_doc: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None, str | None]:
    if config.get("mode") != BOUNDED_QUALITY_LINEAGE_MODE:
        return None, None, None
    scope_ref = config.get("bounded_quality_lineage_scope")
    if not scope_ref:
        return None, None, None
    scope_path = resolve_registry_path(str(scope_ref), config_path).resolve()
    scope_doc = read_json(scope_path)
    validate_bounded_quality_lineage_scope(scope_doc, config, source_registry_doc)
    return scope_doc, scope_path, sha256_file(scope_path)



def validate_core_four_builder_scope(scope_doc: dict[str, Any], config: dict[str, Any], source_registry_doc: dict[str, Any]) -> None:
    if scope_doc.get("scope_status") != "experimental_non_production":
        raise ProbeError("core-four builder scope must be experimental_non_production")
    if scope_doc.get("mode") != CORE_FOUR_BUILDER_MODE:
        raise ProbeError(f"core-four builder scope mode must be {CORE_FOUR_BUILDER_MODE}")
    authority = scope_doc.get("authority")
    if not isinstance(authority, dict):
        raise ProbeError("core-four builder scope must declare authority")
    if authority.get("bounded_sample_data_read_allowed") is not True:
        raise ProbeError("core-four builder scope must explicitly allow bounded row reads")
    if authority.get("experimental_formula_execution_allowed") is not True:
        raise ProbeError("core-four builder scope must explicitly allow experimental formula execution")
    if authority.get("experimental_resolution_records_allowed") is not True:
        raise ProbeError("core-four builder scope must allow experimental resolution records")
    for flag in BOUNDED_SCOPE_FALSE_FLAGS:
        if authority.get(flag) is not False:
            raise ProbeError(f"core-four builder scope authority flag {flag} must be false")
    for flag in ("market_state_integration_authorized", "quote_dependent_builder_execution_authorized", "full_data_read_allowed"):
        if authority.get(flag) is not False:
            raise ProbeError(f"core-four builder scope authority flag {flag} must be false")
    limits = scope_doc.get("global_limits")
    if not isinstance(limits, dict):
        raise ProbeError("core-four builder scope must declare global_limits")
    if limits.get("full_scan_allowed") is not False:
        raise ProbeError("core-four builder scope must keep full_scan_allowed=false")
    checks = {
        "maximum_objects": (1, 4),
        "maximum_instruments": (1, 3),
        "maximum_sessions_per_instrument": (1, 2),
        "maximum_decision_timestamps_per_session": (1, 5),
        "maximum_resolution_requests": (1, 120),
        "maximum_total_input_rows": (1, 30000),
    }
    for key, (low, high) in checks.items():
        value = int(limits.get(key, 0))
        if value < low or value > high:
            raise ProbeError(f"core-four builder scope {key} must be between {low} and {high}")
    core_objects = {"trading_activity", "price_movement", "price_location_structure", "volatility_range_state"}
    objects = scope_doc.get("objects")
    if not isinstance(objects, dict) or set(objects) != core_objects:
        raise ProbeError("core-four builder scope must declare exactly the four core objects")
    formula_rules = scope_doc.get("formula_rules")
    if not isinstance(formula_rules, dict) or not formula_rules:
        raise ProbeError("core-four builder scope must declare formula_rules")
    for object_id, object_doc in objects.items():
        for required in ("display_name", "profile_id", "output_namespace", "required_capabilities"):
            if required not in object_doc:
                raise ProbeError(f"core-four object {object_id} missing {required}")
        caps = object_doc.get("required_capabilities")
        if not isinstance(caps, list) or not caps:
            raise ProbeError(f"core-four object {object_id} must declare required_capabilities")
        missing_rules = sorted(str(cap) for cap in caps if str(cap) not in formula_rules)
        if missing_rules:
            raise ProbeError(f"core-four object {object_id} missing formula rules: {', '.join(missing_rules)}")
    sources = scope_doc.get("sources")
    if not isinstance(sources, dict) or set(sources) != {"004_master_daily_table", "014_master_intraday_bar_table_candidate"}:
        raise ProbeError("core-four builder scope must declare exactly 004 and 014 sources")
    active_aliases = set(unique_active_aliases(config))
    source_bindings = source_registry_doc.get("bindings", {})
    for alias, source_scope in sources.items():
        if alias not in active_aliases:
            raise ProbeError(f"core-four source {alias} is not active in config")
        if alias not in source_bindings or source_bindings[alias].get("binding_status") == "blocked":
            raise ProbeError(f"core-four source {alias} is not an active bound source")
        if not isinstance(source_scope, dict):
            raise ProbeError(f"core-four source scope for {alias} must be an object")
        allowed_columns = source_scope.get("allowed_columns")
        if not isinstance(allowed_columns, list) or not allowed_columns:
            raise ProbeError(f"core-four source {alias} must declare allowed_columns")
        if int(source_scope.get("max_files", 0)) <= 0 or int(source_scope.get("max_files", 0)) > 3:
            raise ProbeError(f"core-four source {alias} max_files must be between 1 and 3")
        if int(source_scope.get("max_rows_per_file", 0)) <= 0 or int(source_scope.get("max_rows_per_file", 0)) > 25000:
            raise ProbeError(f"core-four source {alias} max_rows_per_file must be between 1 and 25000")
    if sources["004_master_daily_table"].get("selected_price_view") != "split_normalized":
        raise ProbeError("core-four builder scope must select split_normalized price_view for 004")
    duplicate_policy = sources["014_master_intraday_bar_table_candidate"].get("duplicate_policy")
    if duplicate_policy and not resolve_policy_path(str(duplicate_policy)).exists():
        raise ProbeError(f"core-four duplicate policy missing: {duplicate_policy}")


def load_core_four_builder_scope(config: dict[str, Any], config_path: Path, source_registry_doc: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None, str | None]:
    if config.get("mode") != CORE_FOUR_BUILDER_MODE:
        return None, None, None
    scope_ref = config.get("core_four_builder_scope")
    if not scope_ref:
        return None, None, None
    scope_path = resolve_registry_path(str(scope_ref), config_path).resolve()
    scope_doc = read_json(scope_path)
    validate_core_four_builder_scope(scope_doc, config, source_registry_doc)
    return scope_doc, scope_path, sha256_file(scope_path)


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


def is_within(candidate: Path, allowed: Path) -> bool:
    return is_within_or_equal(candidate, allowed)


def allowed_root_status(physical_root: str | None, allowed_roots: list[str]) -> tuple[str, str]:
    if not physical_root:
        return "NOT_BOUND", "no physical_candidate_root declared"
    candidate = Path(physical_root).resolve()
    for root in allowed_roots:
        allowed = Path(root).resolve()
        if is_within(candidate, allowed):
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


def check_sources(obj: dict[str, Any], registry_doc: dict[str, Any], source_rows: list[dict[str, Any]], pass_fail: list[dict[str, Any]], *, check_physical_paths: bool, mode: str) -> None:
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
        elif binding.get("binding_status") == "blocked":
            severity = "FAIL"
            finding = "active source alias is blocked in binding registry"
            path_root_status = "BLOCKED_ALIAS"
            path_check_status = "NOT_EXECUTED"
            row_binding = binding
        elif mode == "contract_check_only":
            severity = "INFO"
            finding = "source alias declared in registry; physical binding not evaluated in contract_check_only"
            path_root_status = "CONTRACT_ONLY"
            path_check_status = "NOT_EXECUTED"
            row_binding = binding
        else:
            row_binding = binding
            physical_root = binding.get("physical_candidate_root")
            path_root_status, evidence = allowed_root_status(physical_root, allowed_roots)
            if path_root_status == "OUTSIDE_ALLOWED_ROOT":
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
                finding = "physical candidate root declared; path check not requested"
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

        check_sources(obj, registry_doc, source_rows, pass_fail, check_physical_paths=check_physical_paths, mode=config["mode"])
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


def unique_active_aliases(config: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    for obj in config["objects"]:
        aliases.extend(obj.get("active_source_aliases", []))
    return sorted(set(aliases))


def alias_object_refs(config: dict[str, Any]) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for obj in config["objects"]:
        for alias in obj.get("active_source_aliases", []):
            refs.setdefault(alias, []).append(obj["object_id"])
    return {alias: sorted(objects) for alias, objects in refs.items()}


def bounded_first_parquet(root: Path, *, reverse: bool = False, max_dirs: int = 2000) -> Path | None:
    stack = [root]
    visited_dirs = 0
    while stack:
        current = stack.pop()
        if current.is_file():
            return current if current.suffix.lower() == ".parquet" else None
        if not current.is_dir():
            continue
        visited_dirs += 1
        if visited_dirs > max_dirs:
            return None
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.lower(), reverse=reverse)
        except OSError:
            return None
        parquet_files = [child for child in children if child.is_file() and child.suffix.lower() == ".parquet"]
        if parquet_files:
            return parquet_files[0]
        directories = [child for child in children if child.is_dir()]
        stack.extend(reversed(directories))
    return None


def discover_schema_files(binding: dict[str, Any], *, max_files: int = 3) -> tuple[list[Path], str]:
    physical_root = binding.get("physical_candidate_root")
    if not physical_root:
        return [], "NO_PHYSICAL_ROOT"
    root = Path(str(physical_root)).resolve()
    if not root.exists():
        return [], "PHYSICAL_ROOT_MISSING"
    dataset_format = binding.get("dataset_format")
    files: list[Path] = []
    if root.is_file():
        if root.suffix.lower() == ".parquet":
            return [root], "SINGLE_FILE"
        return [], "ROOT_IS_NOT_PARQUET"
    if dataset_format == "single_parquet_file":
        return [], "SINGLE_FILE_ROOT_NOT_FILE"
    for candidate_name in ("data.parquet", "part-00000.parquet"):
        candidate = root / candidate_name
        if candidate.exists() and candidate.is_file() and candidate.suffix.lower() == ".parquet":
            files.append(candidate.resolve())
    for reverse in (False, True):
        candidate = bounded_first_parquet(root, reverse=reverse)
        if candidate:
            files.append(candidate.resolve())
    unique_files: list[Path] = []
    seen: set[str] = set()
    for file_path in files:
        key = str(file_path).lower()
        if key not in seen:
            seen.add(key)
            unique_files.append(file_path)
        if len(unique_files) >= max_files:
            break
    return unique_files, "BOUNDED_REPRESENTATIVE_FILES" if unique_files else "NO_PARQUET_FOUND_WITH_BOUNDED_DISCOVERY"


def discover_sample_files(binding: dict[str, Any], source_scope: dict[str, Any], *, max_files: int) -> tuple[list[Path], str]:
    include_tokens = [str(token).replace("\\", "/").lower() for token in source_scope.get("include_path_contains", [])]
    if not include_tokens:
        return discover_schema_files(binding, max_files=max_files)
    physical_root = binding.get("physical_candidate_root")
    if not physical_root:
        return [], "NO_PHYSICAL_ROOT"
    root = Path(str(physical_root)).resolve()
    if not root.exists():
        return [], "PHYSICAL_ROOT_MISSING"
    if root.is_file():
        normalized = str(root).replace("\\", "/").lower()
        if root.suffix.lower() == ".parquet" and all(token in normalized for token in include_tokens):
            return [root], "SCOPED_SINGLE_FILE"
        return [], "SCOPED_FILE_FILTER_NO_MATCH"
    matched: list[Path] = []
    stack = [root]
    visited_dirs = 0
    max_dirs = int(source_scope.get("max_discovery_dirs", 10000))
    while stack and len(matched) < max_files:
        current = stack.pop()
        if not current.is_dir():
            continue
        visited_dirs += 1
        if visited_dirs > max_dirs:
            break
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            continue
        for child in children:
            if child.is_file() and child.suffix.lower() == ".parquet":
                normalized = str(child).replace("\\", "/").lower()
                if all(token in normalized for token in include_tokens):
                    matched.append(child.resolve())
                    if len(matched) >= max_files:
                        break
        if len(matched) >= max_files:
            break
        stack.extend(reversed([child for child in children if child.is_dir()]))
    status = "SCOPED_FILTERED_FILES" if matched else "NO_PARQUET_FOUND_WITH_SCOPED_FILTER"
    return matched, status


def parquet_schema(path: Path) -> tuple[dict[str, str], str]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise ProbeError("pyarrow is required for schema metadata inspection") from exc
    parquet_file = pq.ParquetFile(str(path))
    schema = parquet_file.schema_arrow
    columns = {field.name: str(field.type) for field in schema}
    fingerprint_payload = json.dumps(columns, ensure_ascii=False, sort_keys=True)
    fingerprint = hashlib.sha256(fingerprint_payload.encode("utf-8")).hexdigest()
    return columns, fingerprint


def type_family(type_text: str) -> str:
    value = type_text.lower()
    if "timestamp" in value:
        return "timestamp"
    if value.startswith("date"):
        return "date"
    if value.startswith("time"):
        return "time"
    if value.startswith("bool"):
        return "boolean"
    if value.startswith(("int", "uint")):
        return "integer"
    if value.startswith(("float", "double", "decimal", "half_float")):
        return "numeric"
    if "string" in value or value in {"utf8", "large_utf8"}:
        return "string"
    if "binary" in value:
        return "binary"
    return "other"


def compatible_type_family(observed: str, expected_families: list[str]) -> bool:
    observed_family = type_family(observed)
    expanded = set(expected_families)
    if "numeric" in expanded:
        expanded.add("integer")
    if "identifier" in expanded:
        expanded.update({"string", "integer"})
    if "date" in expanded:
        expanded.add("timestamp")
    return observed_family in expanded


def required_temporal_columns(binding: dict[str, Any]) -> list[str]:
    fields = []
    for key in ("event_timestamp_field", "availability_timestamp_field", "as_of_field", "valid_from_field", "valid_to_field"):
        value = binding.get(key)
        if value:
            fields.append(str(value))
    return sorted(set(fields))


def column_rows_for_group(
    *,
    source_alias: str,
    group: str,
    columns: list[str],
    common_columns: set[str],
    observed_types: dict[str, list[str]],
    required_type_families: dict[str, list[str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    critical_group = group in {"minimum_required", "temporal"}
    for column in sorted(set(columns)):
        present = column in common_columns
        expected_families = required_type_families.get(column, [])
        column_types = observed_types.get(column, [])
        observed_families = sorted({type_family(type_value) for type_value in column_types})
        if not present:
            type_status = "NOT_EVALUATED"
            severity = "FAIL" if critical_group else "WARN"
            finding = "required column missing" if critical_group else "governance column missing"
        elif expected_families:
            compatible = all(compatible_type_family(type_value, expected_families) for type_value in column_types)
            type_status = "PASS" if compatible else "TYPE_MISMATCH"
            severity = "INFO" if compatible else ("FAIL" if critical_group else "WARN")
            finding = "column present with compatible type" if compatible else "column present with incompatible type family"
        else:
            type_status = "NOT_DECLARED"
            severity = "INFO"
            finding = "column present; no expected type family declared"
        rows.append({
            "source_alias": source_alias,
            "column_group": group,
            "column_name": column,
            "column_presence_status": "FOUND" if present else "MISSING",
            "expected_type_families": format_list(expected_families),
            "observed_type_strings": format_list(column_types),
            "observed_type_families": format_list(observed_families),
            "type_compatibility_status": type_status,
            "severity": severity,
            "finding": finding,
        })
    return rows


def default_schema_summary(mode: str) -> dict[str, Any]:
    return {
        "schema_resolution": "EXECUTED" if mode == SCHEMA_MODE else "NOT_EXECUTED",
        "schema_validation": "NOT_EXECUTED",
        "unique_sources_schema_checked": 0,
        "unique_sources_schema_passed": 0,
        "unique_sources_schema_passed_with_findings": 0,
        "unique_sources_schema_blocked": 0,
        "unique_sources_schema_failed": 0,
        "schema_files_discovered": 0,
        "schema_files_inspected": 0,
        "minimum_columns_expected": 0,
        "minimum_columns_found": 0,
        "minimum_columns_missing": 0,
        "temporal_fields_expected": 0,
        "temporal_fields_found": 0,
        "temporal_fields_missing": 0,
        "quality_fields_expected": 0,
        "quality_fields_found": 0,
        "quality_fields_missing": 0,
        "lineage_fields_expected": 0,
        "lineage_fields_found": 0,
        "lineage_fields_missing": 0,
        "type_checks_declared": 0,
        "type_mismatches": 0,
    }


def schema_summary_from_rows(mode: str, schema_rows: list[dict[str, Any]], column_rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = default_schema_summary(mode)
    summary["unique_sources_schema_checked"] = len(schema_rows)
    summary["unique_sources_schema_passed"] = sum(1 for row in schema_rows if row["schema_validation_status"] == "PASS")
    summary["unique_sources_schema_passed_with_findings"] = sum(1 for row in schema_rows if row["schema_validation_status"] == "PASS_WITH_FINDINGS")
    summary["unique_sources_schema_blocked"] = sum(1 for row in schema_rows if row["schema_validation_status"] == "BLOCKED")
    summary["unique_sources_schema_failed"] = sum(1 for row in schema_rows if row["schema_validation_status"] == "FAILED")
    summary["schema_files_discovered"] = sum(int(row["files_discovered"]) for row in schema_rows)
    summary["schema_files_inspected"] = sum(int(row["files_inspected"]) for row in schema_rows)
    for group, expected_key, found_key, missing_key in (
        ("minimum_required", "minimum_columns_expected", "minimum_columns_found", "minimum_columns_missing"),
        ("temporal", "temporal_fields_expected", "temporal_fields_found", "temporal_fields_missing"),
        ("quality", "quality_fields_expected", "quality_fields_found", "quality_fields_missing"),
        ("lineage", "lineage_fields_expected", "lineage_fields_found", "lineage_fields_missing"),
    ):
        group_rows = [row for row in column_rows if row["column_group"] == group]
        summary[expected_key] = len(group_rows)
        summary[found_key] = sum(1 for row in group_rows if row["column_presence_status"] == "FOUND")
        summary[missing_key] = sum(1 for row in group_rows if row["column_presence_status"] == "MISSING")
    summary["type_checks_declared"] = sum(1 for row in column_rows if row["type_compatibility_status"] in {"PASS", "TYPE_MISMATCH"})
    summary["type_mismatches"] = sum(1 for row in column_rows if row["type_compatibility_status"] == "TYPE_MISMATCH")
    if summary["unique_sources_schema_failed"]:
        summary["schema_validation"] = "FAILED"
    elif summary["unique_sources_schema_blocked"]:
        summary["schema_validation"] = "BLOCKED"
    elif summary["unique_sources_schema_passed_with_findings"]:
        summary["schema_validation"] = "PASS_WITH_FINDINGS"
    elif summary["unique_sources_schema_passed"] == summary["unique_sources_schema_checked"] and schema_rows:
        summary["schema_validation"] = "PASS"
    return summary


def schema_availability_row(
    *,
    alias: str,
    object_refs: list[str],
    binding: dict[str, Any] | None,
    discovery_status: str,
    files_discovered: int,
    files_inspected: int,
    consistency_status: str,
    fingerprint_count: int,
    missing_minimum: list[str],
    missing_temporal: list[str],
    missing_quality: list[str],
    missing_lineage: list[str],
    type_mismatches: list[str],
    status: str,
    severity: str,
    finding: str,
) -> dict[str, Any]:
    binding = binding or {}
    return {
        "source_alias": alias,
        "object_refs": format_list(object_refs),
        "physical_candidate_root": binding.get("physical_candidate_root"),
        "dataset_format": binding.get("dataset_format"),
        "schema_probe_authorized": binding.get("schema_probe_authorized"),
        "discovery_status": discovery_status,
        "files_discovered": files_discovered,
        "files_inspected": files_inspected,
        "schema_consistency_status": consistency_status,
        "schema_fingerprint_count": fingerprint_count,
        "missing_minimum_columns": format_list(missing_minimum),
        "missing_temporal_columns": format_list(missing_temporal),
        "missing_quality_fields": format_list(missing_quality),
        "missing_lineage_fields": format_list(missing_lineage),
        "type_mismatches": format_list(type_mismatches),
        "schema_validation_status": status,
        "severity": severity,
        "finding": finding,
    }


def evaluate_schema_columns(
    *,
    alias: str,
    binding: dict[str, Any],
    schemas: list[dict[str, str]],
    consistency_status: str,
) -> tuple[list[dict[str, Any]], list[str], list[str], list[str], list[str], list[str], str, str, str]:
    observed_columns = sorted(set().union(*(set(schema) for schema in schemas))) if schemas else []
    common_columns = set(observed_columns) if schemas else set()
    for schema in schemas:
        common_columns &= set(schema)
    observed_types: dict[str, list[str]] = {}
    for column in observed_columns:
        observed_types[column] = sorted({schema[column] for schema in schemas if column in schema})
    required_type_families = binding.get("minimum_required_type_families", {})
    if not isinstance(required_type_families, dict):
        required_type_families = {}
    rows: list[dict[str, Any]] = []
    for group, columns in (
        ("minimum_required", list(binding.get("minimum_required_columns", []))),
        ("temporal", required_temporal_columns(binding)),
        ("quality", list(binding.get("quality_fields", []))),
        ("lineage", list(binding.get("lineage_fields", []))),
    ):
        rows.extend(column_rows_for_group(
            source_alias=alias,
            group=group,
            columns=columns,
            common_columns=common_columns,
            observed_types=observed_types,
            required_type_families=required_type_families,
        ))
    missing_minimum = [row["column_name"] for row in rows if row["column_group"] == "minimum_required" and row["column_presence_status"] == "MISSING"]
    missing_temporal = [row["column_name"] for row in rows if row["column_group"] == "temporal" and row["column_presence_status"] == "MISSING"]
    missing_quality = [row["column_name"] for row in rows if row["column_group"] == "quality" and row["column_presence_status"] == "MISSING"]
    missing_lineage = [row["column_name"] for row in rows if row["column_group"] == "lineage" and row["column_presence_status"] == "MISSING"]
    type_mismatches = [row["column_name"] for row in rows if row["type_compatibility_status"] == "TYPE_MISMATCH"]
    if missing_minimum or missing_temporal or type_mismatches:
        return rows, missing_minimum, missing_temporal, missing_quality, missing_lineage, type_mismatches, "FAILED", "FAIL", "minimum physical schema compatibility failed"
    if missing_quality or missing_lineage or consistency_status == "INCONSISTENT":
        return rows, missing_minimum, missing_temporal, missing_quality, missing_lineage, type_mismatches, "PASS_WITH_FINDINGS", "WARN", "schema metadata passed with governance findings"
    return rows, missing_minimum, missing_temporal, missing_quality, missing_lineage, type_mismatches, "PASS", "INFO", "minimum schema metadata compatible"


def check_schema_metadata(config: dict[str, Any], registry_doc: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    aliases = unique_active_aliases(config)
    refs = alias_object_refs(config)
    bindings = registry_doc["bindings"]
    allowed_roots = registry_doc.get("allowed_roots", [])
    schema_rows: list[dict[str, Any]] = []
    column_rows: list[dict[str, Any]] = []
    fingerprint_report: dict[str, Any] = {"scope": SCHEMA_METADATA_SCOPE, "row_reads_authorized": False, "aliases": {}}

    for alias in aliases:
        binding = bindings.get(alias)
        object_refs = refs.get(alias, [])
        if binding is None:
            schema_rows.append(schema_availability_row(
                alias=alias, object_refs=object_refs, binding=None, discovery_status="MISSING_REGISTRY_BINDING",
                files_discovered=0, files_inspected=0, consistency_status="NOT_EVALUATED", fingerprint_count=0,
                missing_minimum=[], missing_temporal=[], missing_quality=[], missing_lineage=[], type_mismatches=[],
                status="FAILED", severity="FAIL", finding="active source alias has no registry binding"))
            continue

        physical_root = binding.get("physical_candidate_root")
        path_root_status, evidence = allowed_root_status(physical_root, allowed_roots)
        files: list[Path] = []
        schemas: list[dict[str, str]] = []
        fingerprints: list[str] = []
        file_errors: list[str] = []
        discovery_status = "NOT_EVALUATED"
        consistency_status = "NOT_EVALUATED"
        missing_minimum: list[str] = []
        missing_temporal: list[str] = []
        missing_quality: list[str] = []
        missing_lineage: list[str] = []
        type_mismatches: list[str] = []

        if binding.get("schema_probe_authorized") is not True:
            status, severity, finding = "BLOCKED", "WARN", "schema probe is not authorized for active source alias"
            discovery_status = "SCHEMA_PROBE_NOT_AUTHORIZED"
        elif path_root_status != "ALLOWED_ROOT":
            status, severity, finding = "FAILED", "FAIL", f"physical candidate root is not within allowed roots: {evidence}"
            discovery_status = path_root_status
        elif not Path(str(physical_root)).exists():
            status, severity, finding = "FAILED", "FAIL", "physical candidate root missing"
            discovery_status = "PHYSICAL_ROOT_MISSING"
        else:
            files, discovery_status = discover_schema_files(binding)
            if not files:
                status, severity, finding = "FAILED", "FAIL", f"no parquet schema file discovered: {discovery_status}"
            else:
                for file_path in files:
                    try:
                        schema, fingerprint = parquet_schema(file_path)
                    except Exception as exc:
                        file_errors.append(f"{file_path}: {exc}")
                        continue
                    schemas.append(schema)
                    fingerprints.append(fingerprint)
                fingerprint_count = len(set(fingerprints))
                if not schemas:
                    status, severity, finding = "FAILED", "FAIL", "no schema metadata footers could be inspected"
                elif file_errors:
                    status, severity, finding = "FAILED", "FAIL", "one or more schema metadata footers could not be inspected"
                else:
                    consistency_status = "CONSISTENT" if fingerprint_count == 1 else "INCONSISTENT"
                    rows, missing_minimum, missing_temporal, missing_quality, missing_lineage, type_mismatches, status, severity, finding = evaluate_schema_columns(
                        alias=alias, binding=binding, schemas=schemas, consistency_status=consistency_status)
                    column_rows.extend(rows)

        if schemas and consistency_status == "NOT_EVALUATED":
            consistency_status = "CONSISTENT" if len(set(fingerprints)) == 1 else "INCONSISTENT"
        fingerprint_count = len(set(fingerprints))
        observed_columns = sorted(set().union(*(set(schema) for schema in schemas))) if schemas else []
        observed_types: dict[str, list[str]] = {}
        for column in observed_columns:
            observed_types[column] = sorted({schema[column] for schema in schemas if column in schema})
        schema_rows.append(schema_availability_row(
            alias=alias, object_refs=object_refs, binding=binding, discovery_status=discovery_status,
            files_discovered=len(files), files_inspected=len(schemas), consistency_status=consistency_status,
            fingerprint_count=fingerprint_count, missing_minimum=missing_minimum, missing_temporal=missing_temporal,
            missing_quality=missing_quality, missing_lineage=missing_lineage, type_mismatches=type_mismatches,
            status=status, severity=severity, finding=finding))
        fingerprint_report["aliases"][alias] = {
            "physical_candidate_root": physical_root,
            "schema_files_inspected": [str(file_path) for file_path in files],
            "schema_fingerprints": fingerprints,
            "schema_consistency_status": consistency_status,
            "file_errors": file_errors,
            "observed_schema_columns": observed_columns,
            "observed_schema_types": observed_types,
        }

    schema_summary = schema_summary_from_rows(config["mode"], schema_rows, column_rows)
    return schema_rows, column_rows, fingerprint_report, schema_summary


def column_binding_severity(status: str, criticality: str) -> str:
    if status == "FAIL":
        return "FAIL"
    if status == "BLOCKED":
        return "BLOCKED"
    if status == "WARN":
        return "WARN"
    if criticality in {"quality_required", "lineage_required", "advisory"}:
        return "WARN"
    return "INFO"


def path_has_partition_key(files: list[Path], root: Path, key: str, binding_type: str | None) -> tuple[bool, str]:
    if not files:
        return False, "no files inspected"
    if binding_type == "positional_symbol_directory":
        for file_path in files:
            try:
                rel_parts = file_path.resolve().relative_to(root.resolve()).parts
            except ValueError:
                return False, f"file outside root: {file_path}"
            if len(rel_parts) < 2:
                return False, f"not enough path parts for positional binding: {file_path}"
            if rel_parts[0] and "=" not in rel_parts[0]:
                return True, rel_parts[0]
        return False, "no positional symbol directory found"
    expected_prefix = f"{key}="
    for file_path in files:
        try:
            rel_parts = file_path.resolve().relative_to(root.resolve()).parts
        except ValueError:
            return False, f"file outside root: {file_path}"
        for part in rel_parts:
            if part.startswith(expected_prefix):
                return True, part
    return False, f"partition key {key} not present in inspected paths"


def empty_column_binding_summary(mode: str) -> dict[str, Any]:
    return {
        "logical_column_resolution": "NOT_EXECUTED",
        "physical_schema_compatibility": "NOT_EXECUTED",
        "experimental_physical_schema_validation": "NOT_EXECUTED" if mode != COLUMN_BINDING_MODE else "REEXECUTED_WITH_COLUMN_BINDINGS",
        "schema_resolution": "NOT_EXECUTED" if mode != COLUMN_BINDING_MODE else "REEXECUTED_WITH_COLUMN_BINDINGS",
        "schema_validation": "NOT_EXECUTED",
        "unique_sources_schema_checked": 0,
        "unique_sources_schema_passed": 0,
        "unique_sources_schema_passed_with_findings": 0,
        "unique_sources_schema_blocked": 0,
        "unique_sources_schema_failed": 0,
        "schema_files_discovered": 0,
        "schema_files_inspected": 0,
        "minimum_columns_expected": 0,
        "minimum_columns_found": 0,
        "minimum_columns_missing": 0,
        "temporal_fields_expected": 0,
        "temporal_fields_found": 0,
        "temporal_fields_missing": 0,
        "quality_fields_expected": 0,
        "quality_fields_found": 0,
        "quality_fields_missing": 0,
        "lineage_fields_expected": 0,
        "lineage_fields_found": 0,
        "lineage_fields_missing": 0,
        "type_checks_declared": 0,
        "type_mismatches": 0,
        "logical_fields_expected": 0,
        "logical_fields_resolved": 0,
        "logical_fields_resolved_with_restrictions": 0,
        "logical_fields_unresolved": 0,
        "resolved_by_physical_column": 0,
        "resolved_by_partition_key": 0,
        "resolved_by_manifest_field": 0,
        "resolved_by_dataset_metadata": 0,
        "resolved_by_constant_scope": 0,
        "resolved_by_derivation": 0,
        "fields_requiring_cast": 0,
        "fields_blocked_pending_source_fix": 0,
        "critical_state_fields_failed": 0,
        "critical_state_fields_blocked": 0,
        "critical_temporal_fields_unresolved": 0,
        "quality_fields_unresolved": 0,
        "lineage_fields_unresolved": 0,
    }


def binding_report_row(
    *,
    source_alias: str,
    logical_field: str,
    binding: dict[str, Any],
    physical_presence_status: str,
    type_compatibility_status: str,
    resolution_status: str,
    severity: str,
    finding: str,
    evidence: str,
) -> dict[str, Any]:
    return {
        "source_alias": source_alias,
        "logical_field": logical_field,
        "logical_field_groups": format_list(binding.get("logical_field_groups", [])),
        "binding_status": binding.get("binding_status"),
        "physical_resolution_type": binding.get("physical_resolution_type"),
        "physical_column": binding.get("physical_column"),
        "partition_key": binding.get("partition_key"),
        "partition_key_binding_type": binding.get("partition_key_binding_type"),
        "manifest_field": binding.get("manifest_field"),
        "dataset_metadata_field": binding.get("dataset_metadata_field"),
        "expected_type_family": format_list(binding.get("expected_type_family", [])),
        "observed_type": format_list(binding.get("observed_type", [])),
        "observed_type_family": format_list(binding.get("observed_type_family", [])),
        "semantic_role": binding.get("semantic_role"),
        "criticality": binding.get("criticality"),
        "temporal_role": binding.get("temporal_role"),
        "quality_or_lineage_role": binding.get("quality_or_lineage_role"),
        "identity_resolution_required": binding.get("identity_resolution_required"),
        "cast_policy_required": binding.get("cast_policy_required"),
        "cast_target_type_family": binding.get("cast_target_type_family"),
        "parse_policy_status": binding.get("parse_policy_status"),
        "timestamp_unit_policy_required": binding.get("timestamp_unit_policy_required"),
        "type_readiness_status": binding.get("type_readiness_status"),
        "review_status": binding.get("review_status"),
        "physical_presence_status": physical_presence_status,
        "type_compatibility_status": type_compatibility_status,
        "resolution_status": resolution_status,
        "severity": severity,
        "finding": finding,
        "evidence": evidence,
    }


def evaluate_column_binding_entry(
    *,
    source_alias: str,
    logical_field: str,
    binding: dict[str, Any],
    common_columns: set[str],
    observed_types: dict[str, list[str]],
    schema_files: list[Path],
    physical_root: Path,
) -> dict[str, Any]:
    resolution_type = binding.get("physical_resolution_type")
    criticality = str(binding.get("criticality"))
    expected = binding.get("expected_type_family", []) or []
    physical_presence_status = "NOT_APPLICABLE"
    type_status = "NOT_EVALUATED"
    status = "RESOLVED_WITH_RESTRICTIONS"
    severity = "INFO"
    finding = "logical field resolved by governed binding"
    evidence = binding.get("binding_evidence", "")

    if resolution_type == "physical_column":
        column = binding.get("physical_column")
        physical_presence_status = "FOUND" if column in common_columns else "MISSING"
        types = observed_types.get(str(column), [])
        if physical_presence_status == "MISSING":
            if criticality == "temporal_required":
                status, severity, finding = "BLOCKED", "BLOCKED", "required temporal physical column missing"
            elif criticality == "state_required":
                status, severity, finding = "FAIL", "FAIL", "required state physical column missing"
            else:
                status, severity, finding = "UNRESOLVED", "WARN", "governance physical column missing"
        elif str(binding.get("type_readiness_status", "")).startswith("blocked"):
            status, severity, finding = "BLOCKED", "BLOCKED", "physical column exists but type readiness is blocked"
            type_status = "BLOCKED"
        elif binding.get("cast_policy_required") is True:
            status, severity, finding = "RESOLVED_WITH_RESTRICTIONS", "WARN", "physical column present but cast/parse policy is required"
            type_status = "CAST_REQUIRED"
        elif expected and types:
            compatible = all(compatible_type_family(type_value, expected) for type_value in types)
            if compatible:
                if binding.get("identity_resolution_required") is True:
                    status, severity, finding = "RESOLVED_WITH_RESTRICTIONS", "WARN", "physical identity column present but governed identity normalization is required"
                    type_status = "IDENTITY_NORMALIZATION_REQUIRED"
                else:
                    status, severity, finding = "RESOLVED", "INFO", "physical column present with compatible type family"
                    type_status = "PASS"
            elif criticality == "temporal_required":
                status, severity, finding = "BLOCKED", "BLOCKED", "temporal physical column type family is incompatible"
                type_status = "TYPE_MISMATCH"
            elif criticality == "state_required":
                status, severity, finding = "FAIL", "FAIL", "state physical column type family is incompatible"
                type_status = "TYPE_MISMATCH"
            else:
                status, severity, finding = "RESOLVED_WITH_RESTRICTIONS", "WARN", "governance physical column type family is incompatible"
                type_status = "TYPE_MISMATCH"
        else:
            if binding.get("identity_resolution_required") is True:
                status, severity, finding = "RESOLVED_WITH_RESTRICTIONS", "WARN", "physical identity column present but governed identity normalization is required"
                type_status = "IDENTITY_NORMALIZATION_REQUIRED"
            else:
                status, severity, finding = "RESOLVED", "INFO", "physical column present; no expected type family declared"
                type_status = "NOT_DECLARED"
    elif resolution_type == "partition_key":
        key = str(binding.get("partition_key"))
        ok, path_evidence = path_has_partition_key(schema_files, physical_root, key, binding.get("partition_key_binding_type"))
        physical_presence_status = "FOUND" if ok else "MISSING"
        evidence = f"{evidence} | path_evidence={path_evidence}"
        if ok:
            status, severity, finding = "RESOLVED_WITH_RESTRICTIONS", "WARN", "logical field resolves through partition metadata"
            type_status = "PARTITION_METADATA"
        elif criticality == "state_required":
            status, severity, finding = "FAIL", "FAIL", "required partition binding not present in inspected paths"
        elif criticality == "temporal_required":
            status, severity, finding = "BLOCKED", "BLOCKED", "required temporal partition binding not present in inspected paths"
        else:
            status, severity, finding = "UNRESOLVED", "WARN", "partition binding not present in inspected paths"
    elif resolution_type in {"manifest_field", "dataset_level_metadata", "constant_from_binding_scope", "derived_from_existing_column"}:
        status, severity = "RESOLVED_WITH_RESTRICTIONS", "WARN"
        type_status = resolution_type.upper()
        finding = f"logical field resolves through {resolution_type}; values not validated"
    elif resolution_type == "not_required_for_current_gate":
        status, severity, finding = "NOT_REQUIRED", "WARN", "logical field is explicitly outside current gate"
    elif resolution_type == "unavailable_pending_source_fix":
        if criticality == "state_required":
            status, severity, finding = "FAIL", "FAIL", "state-required logical field is unresolved"
        elif criticality == "temporal_required":
            status, severity, finding = "BLOCKED", "BLOCKED", "temporal-required logical field is unresolved"
        else:
            status, severity, finding = "UNRESOLVED", "WARN", "non-core governance logical field is unresolved"
    else:
        status, severity, finding = "FAIL", "FAIL", f"unsupported physical_resolution_type={resolution_type}"

    return binding_report_row(
        source_alias=source_alias,
        logical_field=logical_field,
        binding=binding,
        physical_presence_status=physical_presence_status,
        type_compatibility_status=type_status,
        resolution_status=status,
        severity=severity,
        finding=finding,
        evidence=evidence,
    )


def column_binding_summary_from_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = empty_column_binding_summary(COLUMN_BINDING_MODE)
    summary["logical_fields_expected"] = len(rows)
    summary["logical_fields_resolved"] = sum(1 for row in rows if row["resolution_status"] == "RESOLVED")
    summary["logical_fields_resolved_with_restrictions"] = sum(1 for row in rows if row["resolution_status"] == "RESOLVED_WITH_RESTRICTIONS")
    summary["logical_fields_unresolved"] = sum(1 for row in rows if row["resolution_status"] in {"UNRESOLVED", "FAIL", "BLOCKED"})
    resolution_key_map = {
        "physical_column": "resolved_by_physical_column",
        "partition_key": "resolved_by_partition_key",
        "manifest_field": "resolved_by_manifest_field",
        "dataset_level_metadata": "resolved_by_dataset_metadata",
        "constant_from_binding_scope": "resolved_by_constant_scope",
        "derived_from_existing_column": "resolved_by_derivation",
    }
    for resolution_type, metric in resolution_key_map.items():
        summary[metric] = sum(1 for row in rows if row["physical_resolution_type"] == resolution_type and row["resolution_status"] in {"RESOLVED", "RESOLVED_WITH_RESTRICTIONS"})
    summary["fields_requiring_cast"] = sum(1 for row in rows if str(row.get("cast_policy_required")) == "True")
    summary["fields_blocked_pending_source_fix"] = sum(1 for row in rows if row["physical_resolution_type"] == "unavailable_pending_source_fix")
    summary["critical_state_fields_failed"] = sum(1 for row in rows if row["criticality"] == "state_required" and row["resolution_status"] == "FAIL")
    summary["critical_state_fields_blocked"] = sum(1 for row in rows if row["criticality"] == "state_required" and row["resolution_status"] == "BLOCKED")
    summary["critical_temporal_fields_unresolved"] = sum(1 for row in rows if row["criticality"] == "temporal_required" and row["resolution_status"] in {"UNRESOLVED", "FAIL", "BLOCKED"})
    summary["quality_fields_unresolved"] = sum(1 for row in rows if row["criticality"] == "quality_required" and row["resolution_status"] in {"UNRESOLVED", "FAIL", "BLOCKED"})
    summary["lineage_fields_unresolved"] = sum(1 for row in rows if row["criticality"] == "lineage_required" and row["resolution_status"] in {"UNRESOLVED", "FAIL", "BLOCKED"})
    aliases = sorted({row["source_alias"] for row in rows})
    summary["unique_sources_schema_checked"] = len(aliases)
    summary["unique_sources_schema_passed"] = 0
    summary["unique_sources_schema_passed_with_findings"] = 0
    summary["unique_sources_schema_blocked"] = 0
    summary["unique_sources_schema_failed"] = 0
    if summary["critical_state_fields_failed"]:
        logical_status = "FAILED"
    elif summary["critical_state_fields_blocked"] or summary["critical_temporal_fields_unresolved"]:
        logical_status = "BLOCKED"
    elif summary["logical_fields_unresolved"] or summary["logical_fields_resolved_with_restrictions"] or summary["fields_requiring_cast"]:
        logical_status = "PASS_WITH_RESTRICTIONS"
    else:
        logical_status = "PASS"
    summary["logical_column_resolution"] = logical_status
    summary["physical_schema_compatibility"] = logical_status
    summary["schema_resolution"] = "REEXECUTED_WITH_COLUMN_BINDINGS"
    summary["schema_validation"] = logical_status
    return summary


def check_logical_to_physical_bindings(
    config: dict[str, Any],
    source_registry_doc: dict[str, Any],
    column_registry_doc: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    aliases = unique_active_aliases(config)
    source_bindings = source_registry_doc["bindings"]
    column_bindings = column_registry_doc["bindings"]
    binding_rows: list[dict[str, Any]] = []
    fingerprint_report: dict[str, Any] = {"scope": COLUMN_BINDING_SCOPE, "row_reads_authorized": False, "aliases": {}}
    for alias in aliases:
        source_binding = source_bindings[alias]
        physical_root = Path(str(source_binding.get("physical_candidate_root"))).resolve()
        schema_files, discovery_status = discover_schema_files(source_binding)
        schemas: list[dict[str, str]] = []
        fingerprints: list[str] = []
        file_errors: list[str] = []
        for file_path in schema_files:
            try:
                schema, fingerprint = parquet_schema(file_path)
            except Exception as exc:
                file_errors.append(f"{file_path}: {exc}")
                continue
            schemas.append(schema)
            fingerprints.append(fingerprint)
        observed_columns = sorted(set().union(*(set(schema) for schema in schemas))) if schemas else []
        common_columns = set(observed_columns) if schemas else set()
        for schema in schemas:
            common_columns &= set(schema)
        observed_types: dict[str, list[str]] = {}
        for column in observed_columns:
            observed_types[column] = sorted({schema[column] for schema in schemas if column in schema})
        for logical_field, binding in sorted(column_bindings[alias].items()):
            binding_rows.append(evaluate_column_binding_entry(
                source_alias=alias,
                logical_field=logical_field,
                binding=binding,
                common_columns=common_columns,
                observed_types=observed_types,
                schema_files=schema_files,
                physical_root=physical_root,
            ))
        fingerprint_report["aliases"][alias] = {
            "physical_candidate_root": str(physical_root),
            "schema_discovery_status": discovery_status,
            "schema_files_inspected": [str(file_path) for file_path in schema_files],
            "schema_fingerprints": fingerprints,
            "schema_consistency_status": "CONSISTENT" if len(set(fingerprints)) <= 1 else "INCONSISTENT",
            "file_errors": file_errors,
            "observed_schema_columns": observed_columns,
            "observed_schema_types": observed_types,
        }
    unresolved_rows = [row for row in binding_rows if row["resolution_status"] in {"UNRESOLVED", "FAIL", "BLOCKED"}]
    partition_rows = [row for row in binding_rows if row["physical_resolution_type"] == "partition_key"]
    manifest_rows = [row for row in binding_rows if row["physical_resolution_type"] in {"manifest_field", "dataset_level_metadata", "constant_from_binding_scope"}]
    cast_rows = [row for row in binding_rows if str(row.get("cast_policy_required")) == "True"]
    summary = column_binding_summary_from_rows(binding_rows)
    alias_statuses: dict[str, str] = {}
    for alias in aliases:
        alias_rows = [row for row in binding_rows if row["source_alias"] == alias]
        if any(row["resolution_status"] == "FAIL" for row in alias_rows):
            alias_statuses[alias] = "FAILED"
        elif any(row["resolution_status"] == "BLOCKED" for row in alias_rows):
            alias_statuses[alias] = "BLOCKED"
        elif any(row["resolution_status"] in {"UNRESOLVED", "RESOLVED_WITH_RESTRICTIONS"} for row in alias_rows):
            alias_statuses[alias] = "PASS_WITH_FINDINGS"
        else:
            alias_statuses[alias] = "PASS"
    summary["unique_sources_schema_passed"] = sum(1 for status in alias_statuses.values() if status == "PASS")
    summary["unique_sources_schema_passed_with_findings"] = sum(1 for status in alias_statuses.values() if status == "PASS_WITH_FINDINGS")
    summary["unique_sources_schema_blocked"] = sum(1 for status in alias_statuses.values() if status == "BLOCKED")
    summary["unique_sources_schema_failed"] = sum(1 for status in alias_statuses.values() if status == "FAILED")
    summary["schema_files_discovered"] = sum(len(doc.get("schema_files_inspected", [])) for doc in fingerprint_report["aliases"].values())
    summary["schema_files_inspected"] = summary["schema_files_discovered"]
    summary["column_binding_alias_statuses"] = alias_statuses
    return binding_rows, unresolved_rows, partition_rows, manifest_rows, cast_rows, fingerprint_report, summary



def read_bounded_parquet_rows(file_path: Path, allowed_columns: list[str], max_rows: int, row_filter_tickers: list[str] | None = None) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise ProbeError("pyarrow is required for bounded parquet sample reads") from exc
    parquet_file = pq.ParquetFile(str(file_path))
    available_columns = set(parquet_file.schema_arrow.names)
    selected_columns = [column for column in allowed_columns if column in available_columns]
    missing_columns = [column for column in allowed_columns if column not in available_columns]
    rows: list[dict[str, Any]] = []
    if not selected_columns:
        return rows, selected_columns, missing_columns
    filters = None
    if row_filter_tickers and "ticker" in selected_columns:
        filters = [("ticker", "in", [str(ticker) for ticker in row_filter_tickers])]
    if filters:
        table = pq.read_table(str(file_path), columns=selected_columns, filters=filters)
        for row in table.slice(0, max_rows).to_pylist():
            rows.append(row)
        return rows, selected_columns, missing_columns
    for batch in parquet_file.iter_batches(batch_size=min(500, max_rows), columns=selected_columns):
        for row in batch.to_pylist():
            rows.append(row)
            if len(rows) >= max_rows:
                return rows, selected_columns, missing_columns
    return rows, selected_columns, missing_columns


def partition_value(file_path: Path, root: Path, key: str, binding_type: str | None) -> str | None:
    try:
        rel_parts = file_path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return None
    if binding_type == "positional_symbol_directory":
        for part in rel_parts:
            if part and "=" not in part and part.lower() not in {"quotes.parquet", "data.parquet"}:
                return part
        return None
    prefix = f"{key}="
    for part in rel_parts:
        if part.startswith(prefix):
            return part[len(prefix):]
    return None


def numeric_epoch_unit(values: list[Any]) -> tuple[str, str]:
    numeric_values: list[float] = []
    for value in values:
        if isinstance(value, bool) or value is None:
            continue
        if isinstance(value, (int, float)):
            numeric_values.append(abs(float(value)))
    if not numeric_values:
        return "unknown", "no numeric timestamp values observed"
    median_value = sorted(numeric_values)[len(numeric_values) // 2]
    if median_value >= 10**17:
        return "nanoseconds", f"median_abs_epoch={median_value:.0f}"
    if median_value >= 10**14:
        return "microseconds", f"median_abs_epoch={median_value:.0f}"
    if median_value >= 10**11:
        return "milliseconds", f"median_abs_epoch={median_value:.0f}"
    if median_value >= 10**8:
        return "seconds", f"median_abs_epoch={median_value:.0f}"
    return "unknown", f"median_abs_epoch={median_value:.0f}"


def parse_datetime_text(value: str) -> tuple[datetime | None, str, bool, bool]:
    raw = value.strip()
    if not raw:
        return None, "empty timestamp string", False, False
    normalized = raw.replace("Z", "+00:00")
    if normalized.endswith(" UTC"):
        normalized = f"{normalized[:-4]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            import pandas as pd
        except ImportError:
            return None, "timestamp string is not ISO-parseable and pandas is unavailable", False, False
        try:
            parsed_value = pd.to_datetime(raw, utc=True, errors="raise")
        except Exception as exc:
            return None, f"timestamp string parse failed: {exc}", False, False
        parsed = parsed_value.to_pydatetime()
    timezone_detected = parsed.tzinfo is not None
    timezone_assumed = parsed.tzinfo is None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed, "parsed", timezone_detected, timezone_assumed


def parse_timestamp_value(value: Any, *, epoch_unit: str | None = None) -> tuple[datetime | None, str, bool, bool]:
    if value is None:
        return None, "null timestamp", False, False
    if isinstance(value, datetime):
        timezone_detected = value.tzinfo is not None
        timezone_assumed = value.tzinfo is None
        parsed = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
        return parsed, "parsed", timezone_detected, timezone_assumed
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=timezone.utc), "date coerced to utc midnight", False, True
    if isinstance(value, str):
        return parse_datetime_text(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        unit = epoch_unit or "unknown"
        divisors = {
            "seconds": 1,
            "milliseconds": 1_000,
            "microseconds": 1_000_000,
            "nanoseconds": 1_000_000_000,
        }
        divisor = divisors.get(unit)
        if divisor is None:
            return None, f"unsupported epoch unit: {unit}", False, False
        try:
            return datetime.fromtimestamp(float(value) / divisor, tz=timezone.utc), f"parsed_epoch_{unit}", True, False
        except Exception as exc:
            return None, f"epoch parse failed: {exc}", False, False
    return None, f"unsupported timestamp value type: {type(value).__name__}", False, False


def parse_session_date_value(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        parsed, _, _, _ = parse_datetime_text(raw)
        return parsed.date() if parsed else None


def sample_source_rows(
    *,
    alias: str,
    source_binding: dict[str, Any],
    source_scope: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    max_files = int(source_scope["max_files"])
    max_rows_per_file = int(source_scope["max_rows_per_file"])
    allowed_columns = list(source_scope["allowed_columns"])
    schema_files, discovery_status = discover_sample_files(source_binding, source_scope, max_files=max_files)
    physical_root = Path(str(source_binding.get("physical_candidate_root"))).resolve()
    sampled_rows: list[dict[str, Any]] = []
    limit_rows: list[dict[str, Any]] = []
    file_docs: list[dict[str, Any]] = []
    for file_path in schema_files[:max_files]:
        rows, selected_columns, missing_columns = read_bounded_parquet_rows(file_path, allowed_columns, max_rows_per_file, row_filter_tickers=source_scope.get("row_filter_tickers"))
        partition_doc = source_scope.get("partition_identity", {}) if isinstance(source_scope.get("partition_identity"), dict) else {}
        partition_identity_value = partition_value(file_path, physical_root, str(partition_doc.get("key", "")), partition_doc.get("type")) if partition_doc else None
        for row_ordinal, row in enumerate(rows):
            sampled_rows.append({
                "source_alias": alias,
                "file_path": str(file_path),
                "row_ordinal_in_file": row_ordinal,
                "partition_identity_value": partition_identity_value,
                "values": row,
            })
        limit_rows.append({
            "source_alias": alias,
            "file_path": str(file_path),
            "authorized_max_rows_per_file": max_rows_per_file,
            "rows_read": len(rows),
            "authorized_columns": format_list(allowed_columns),
            "columns_read": format_list(selected_columns),
            "missing_allowed_columns": format_list(missing_columns),
            "limit_respected": len(rows) <= max_rows_per_file,
            "write_to_source": False,
        })
        file_docs.append({
            "file_path": str(file_path),
            "rows_read": len(rows),
            "columns_read": selected_columns,
            "missing_allowed_columns": missing_columns,
            "row_filter_tickers": source_scope.get("row_filter_tickers", []),
            "partition_identity_value": partition_identity_value,
        })
    manifest_doc = {
        "source_alias": alias,
        "physical_candidate_root": str(physical_root),
        "schema_discovery_status": discovery_status,
        "files_discovered_for_sampling": [str(path) for path in schema_files],
        "files_sampled": file_docs,
        "rows_sampled": len(sampled_rows),
    }
    return sampled_rows, limit_rows, manifest_doc


def identity_report_row(alias: str, rows: list[dict[str, Any]], source_scope: dict[str, Any], reference_map: dict[str, set[str]], reference_ambiguities: set[str]) -> dict[str, Any]:
    identity_fields = list(source_scope.get("identity_fields", []))
    partition_values = sorted({str(row.get("partition_identity_value")) for row in rows if row.get("partition_identity_value")})
    row_tickers: list[str] = []
    non_null_identity_rows = 0
    missing_identity_rows = 0
    partition_row_mismatch_count = 0
    for row in rows:
        values = row["values"]
        row_identity_values = [values.get(field) for field in identity_fields if values.get(field) not in (None, "")]
        ticker = values.get("ticker")
        if ticker not in (None, ""):
            row_tickers.append(str(ticker))
        if row_identity_values or row.get("partition_identity_value"):
            non_null_identity_rows += 1
        else:
            missing_identity_rows += 1
        if row.get("partition_identity_value") and ticker not in (None, "") and str(ticker) != str(row.get("partition_identity_value")):
            partition_row_mismatch_count += 1
    unique_tickers = sorted(set(row_tickers or partition_values))
    reference_checked = len(unique_tickers)
    reference_resolved = sum(1 for ticker in unique_tickers if ticker in reference_map and len(reference_map[ticker]) == 1)
    ambiguity_count = sum(1 for ticker in unique_tickers if ticker in reference_ambiguities)
    if not rows:
        status, severity, finding = "FAILED", "FAIL", "no rows available for bounded identity check"
    elif missing_identity_rows == len(rows):
        status, severity, finding = "FAILED", "FAIL", "no row or partition identity evidence present in bounded sample"
    elif partition_row_mismatch_count:
        status, severity, finding = "FAILED", "FAIL", "partition identity conflicts with row ticker in bounded sample"
    elif ambiguity_count:
        status, severity, finding = "FAILED", "FAIL", "bounded canonical reference contains ambiguous ticker mapping"
    elif alias in {"014_master_intraday_bar_table_candidate", "raw_quotes"}:
        status, severity, finding = "PASS_WITH_RESTRICTIONS", "WARN", "identity evidence is usable in sample but requires governed canonical normalization before builder execution"
    elif reference_checked and reference_resolved < reference_checked and alias != "004_master_daily_table":
        status, severity, finding = "PASS_WITH_RESTRICTIONS", "WARN", "bounded sample did not resolve every ticker against sampled canonical reference"
    else:
        status, severity, finding = "PASS", "INFO", "bounded identity evidence is present and internally consistent"
    return {
        "source_alias": alias,
        "files_sampled": len({row["file_path"] for row in rows}),
        "rows_checked": len(rows),
        "identity_evidence_type": "partition_or_row" if partition_values else "row_column",
        "row_identity_fields": format_list(identity_fields),
        "partition_identity_values": format_list(partition_values),
        "non_null_identity_rows": non_null_identity_rows,
        "missing_identity_rows": missing_identity_rows,
        "partition_row_mismatch_count": partition_row_mismatch_count,
        "unique_row_tickers": format_list(unique_tickers),
        "canonical_reference_tickers_checked": reference_checked,
        "canonical_reference_tickers_resolved": reference_resolved,
        "ambiguous_reference_ticker_count": ambiguity_count,
        "identity_resolution_status": status,
        "severity": severity,
        "finding": finding,
    }


def timestamp_parse_report_rows(alias: str, rows: list[dict[str, Any]], source_scope: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, list[datetime]]]:
    report_rows: list[dict[str, Any]] = []
    parsed_by_field: dict[str, list[datetime]] = {}
    for field in source_scope.get("temporal_fields", []):
        values = [row["values"].get(field) for row in rows if field in row["values"]]
        unit, unit_evidence = numeric_epoch_unit(values) if any(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values) else ("not_applicable", "non-numeric timestamp field")
        parsed_values: list[datetime] = []
        failure_messages: list[str] = []
        null_count = 0
        timezone_detected_count = 0
        timezone_assumed_count = 0
        for value in values:
            if value is None or value == "":
                null_count += 1
                continue
            parsed, message, timezone_detected, timezone_assumed = parse_timestamp_value(value, epoch_unit=unit if unit != "not_applicable" else None)
            if parsed is None:
                failure_messages.append(message)
            else:
                parsed_values.append(parsed)
                timezone_detected_count += 1 if timezone_detected else 0
                timezone_assumed_count += 1 if timezone_assumed else 0
        parsed_by_field[field] = parsed_values
        checked = len(values)
        failures = len(failure_messages)
        if checked == 0:
            status, severity, finding = "FAILED", "FAIL", "temporal field not present in bounded rows"
        elif failures:
            status, severity, finding = "FAILED", "FAIL", "one or more bounded timestamp values failed to parse"
        elif timezone_assumed_count or unit in {"nanoseconds", "microseconds", "milliseconds", "seconds"}:
            status, severity, finding = "PASS_WITH_RESTRICTIONS", "WARN", "timestamp parses in sample but requires explicit temporal policy confirmation"
        else:
            status, severity, finding = "PASS", "INFO", "timestamp parses in bounded sample"
        report_rows.append({
            "source_alias": alias,
            "temporal_field": field,
            "values_checked": checked,
            "parse_success_count": len(parsed_values),
            "parse_failure_count": failures,
            "null_count": null_count,
            "parse_success_rate": round(len(parsed_values) / checked, 6) if checked else 0,
            "detected_unit": unit,
            "unit_detection_evidence": unit_evidence,
            "timezone_detected_count": timezone_detected_count,
            "timezone_assumed_count": timezone_assumed_count,
            "minimum_observed_timestamp_utc": min(parsed_values).isoformat().replace("+00:00", "Z") if parsed_values else "",
            "maximum_observed_timestamp_utc": max(parsed_values).isoformat().replace("+00:00", "Z") if parsed_values else "",
            "timestamp_parse_status": status,
            "severity": severity,
            "finding": finding,
            "evidence": format_list(sorted(set(failure_messages))[:5]),
        })
    return report_rows, parsed_by_field


def cutoff_legality_rows(alias: str, bar_times: list[datetime]) -> list[dict[str, Any]]:
    unique_times = sorted(set(bar_times))
    if not unique_times:
        return [{
            "source_alias": alias,
            "decision_case": "no_sampled_bar_times",
            "decision_timestamp_utc": "",
            "selected_bar_end_utc": "",
            "eligible_bar_count": 0,
            "future_bar_leak": False,
            "cutoff_status": "FAILED",
            "severity": "FAIL",
            "finding": "no parsed bar timestamps available for cutoff legality check",
        }]
    decision_cases: list[tuple[str, datetime]] = [
        ("before_first_bar", unique_times[0] - timedelta(seconds=1)),
        ("exact_first_bar", unique_times[0]),
        ("exact_last_bar", unique_times[-1]),
        ("after_last_bar", unique_times[-1] + timedelta(seconds=1)),
    ]
    if len(unique_times) > 1:
        midpoint = unique_times[0] + ((unique_times[1] - unique_times[0]) / 2)
        decision_cases.insert(2, ("between_first_two_bars", midpoint))
    rows: list[dict[str, Any]] = []
    for case_name, decision_ts in decision_cases:
        eligible = [bar_time for bar_time in unique_times if bar_time <= decision_ts]
        selected = max(eligible) if eligible else None
        future_leak = selected is not None and selected > decision_ts
        rows.append({
            "source_alias": alias,
            "decision_case": case_name,
            "decision_timestamp_utc": decision_ts.isoformat().replace("+00:00", "Z"),
            "selected_bar_end_utc": selected.isoformat().replace("+00:00", "Z") if selected else "",
            "eligible_bar_count": len(eligible),
            "future_bar_leak": future_leak,
            "cutoff_status": "FAILED" if future_leak else "PASS",
            "severity": "FAIL" if future_leak else "INFO",
            "finding": "future bar selected" if future_leak else "bounded resolver selected max(bar_end) <= decision_timestamp",
        })
    return rows


def daily_availability_rows(rows: list[dict[str, Any]], policy_doc: dict[str, Any]) -> list[dict[str, Any]]:
    availability_time_raw = str(policy_doc.get("derived_legal_availability_time_utc", "13:30:00"))
    hour, minute, second = [int(part) for part in availability_time_raw.split(":")]
    day_offset = int(policy_doc.get("availability_day_offset", 1))
    session_dates = sorted({parsed for parsed in (parse_session_date_value(row["values"].get("session_date")) for row in rows) if parsed})[:10]
    output_rows: list[dict[str, Any]] = []
    for session_day in session_dates:
        availability_dt = datetime.combine(session_day + timedelta(days=day_offset), time(hour, minute, second), tzinfo=timezone.utc)
        decisions = [
            ("same_session_before_close", datetime.combine(session_day, time(16, 0), tzinfo=timezone.utc), False),
            ("one_second_before_policy_availability", availability_dt - timedelta(seconds=1), False),
            ("at_policy_availability", availability_dt, True),
            ("one_second_after_policy_availability", availability_dt + timedelta(seconds=1), True),
        ]
        for case_name, decision_ts, expected in decisions:
            eligible = decision_ts >= availability_dt
            failed = eligible != expected
            output_rows.append({
                "source_alias": "004_master_daily_table",
                "session_date": session_day.isoformat(),
                "decision_case": case_name,
                "derived_legal_availability_utc": availability_dt.isoformat().replace("+00:00", "Z"),
                "decision_timestamp_utc": decision_ts.isoformat().replace("+00:00", "Z"),
                "row_eligible": eligible,
                "expected_row_eligible": expected,
                "policy_version": str(policy_doc.get("policy_id", "daily_row_availability_policy_v0_1")),
                "calendar_status": str(policy_doc.get("calendar_status", "not_declared")),
                "daily_availability_status": "FAILED" if failed else "PASS_WITH_RESTRICTIONS",
                "severity": "FAIL" if failed else "WARN",
                "finding": "daily availability policy mismatch" if failed else "conservative daily availability policy executed; calendar handling not fully validated in this gate",
            })
    if not output_rows:
        output_rows.append({
            "source_alias": "004_master_daily_table",
            "session_date": "",
            "decision_case": "no_session_dates",
            "derived_legal_availability_utc": "",
            "decision_timestamp_utc": "",
            "row_eligible": False,
            "expected_row_eligible": False,
            "policy_version": str(policy_doc.get("policy_id", "daily_row_availability_policy_v0_1")),
            "calendar_status": str(policy_doc.get("calendar_status", "not_declared")),
            "daily_availability_status": "FAILED",
            "severity": "FAIL",
            "finding": "no session_date values available to execute daily availability policy",
        })
    return output_rows


def bounded_sample_summary_from_reports(
    *,
    bounded_manifest: dict[str, Any],
    read_limit_rows: list[dict[str, Any]],
    identity_rows: list[dict[str, Any]],
    timestamp_rows: list[dict[str, Any]],
    cutoff_rows: list[dict[str, Any]],
    daily_rows: list[dict[str, Any]],
    scope_doc: dict[str, Any],
) -> dict[str, Any]:
    total_rows_read = sum(int(row["rows_read"]) for row in read_limit_rows)
    maximum_rows_authorized = int(scope_doc["global_limits"]["maximum_total_rows"])
    limit_violation = total_rows_read > maximum_rows_authorized or any(str(row["limit_respected"]) != "True" for row in read_limit_rows)
    identity_failures = sum(1 for row in identity_rows if row["severity"] == "FAIL")
    timestamp_failures = sum(1 for row in timestamp_rows if row["severity"] == "FAIL")
    cutoff_future_leaks = sum(1 for row in cutoff_rows if str(row["future_bar_leak"]) == "True")
    daily_policy_failures = sum(1 for row in daily_rows if row["severity"] == "FAIL")
    restriction_count = sum(1 for row in identity_rows + timestamp_rows + daily_rows if row["severity"] == "WARN")
    if limit_violation or identity_failures or timestamp_failures or cutoff_future_leaks or daily_policy_failures:
        validation = "FAILED"
        overall = "failed_bounded_identity_temporal_validation"
    elif restriction_count:
        validation = "PASS_WITH_RESTRICTIONS"
        overall = "passed_bounded_identity_temporal_validation_with_restrictions"
    else:
        validation = "PASS"
        overall = "passed_bounded_identity_temporal_validation"
    return {
        "overall_status": overall,
        "bounded_sample_validation": validation,
        "bounded_sample_data_read": "EXECUTED_WITH_LIMITS",
        "bounded_sample_scope": BOUNDED_SAMPLE_SCOPE,
        "bounded_sample_scope_id": scope_doc.get("scope_id"),
        "bounded_sample_sources_authorized": len(scope_doc.get("sources", {})),
        "bounded_sample_sources_sampled": len(bounded_manifest.get("sources", {})),
        "bounded_sample_files_sampled": sum(len(source_doc.get("files_sampled", [])) for source_doc in bounded_manifest.get("sources", {}).values()),
        "bounded_sample_rows_read": total_rows_read,
        "bounded_sample_maximum_rows_authorized": maximum_rows_authorized,
        "bounded_sample_limits_respected": not limit_violation,
        "bounded_identity_validation": "FAILED" if identity_failures else ("PASS_WITH_RESTRICTIONS" if any(row["identity_resolution_status"] == "PASS_WITH_RESTRICTIONS" for row in identity_rows) else "PASS"),
        "bounded_identity_failures": identity_failures,
        "bounded_temporal_parse_validation": "FAILED" if timestamp_failures else ("PASS_WITH_RESTRICTIONS" if any(row["timestamp_parse_status"] == "PASS_WITH_RESTRICTIONS" for row in timestamp_rows) else "PASS"),
        "bounded_timestamp_parse_failures": timestamp_failures,
        "bounded_cutoff_legality": "FAILED" if cutoff_future_leaks else "PASS",
        "bounded_cutoff_future_bar_leaks": cutoff_future_leaks,
        "daily_availability_policy_execution": "FAILED" if daily_policy_failures else "PASS_WITH_RESTRICTIONS",
        "daily_availability_policy_failures": daily_policy_failures,
        "data_resolution": "BOUNDED_SAMPLE_AUTHORIZED_BY_SCOPE",
        "data_validation": "BOUNDED_SAMPLE_EXECUTED_WITH_LIMITS",
        "temporal_value_validation": "BOUNDED_PARSE_AND_CUTOFF_EXECUTED",
        "grain_validation": "NOT_EXECUTED",
        "quality_semantics_validation": "PARTIAL_NOT_EXECUTED",
        "builder_validation_execution": "NOT_EXECUTED",
        "market_state_integration": "NOT_EXECUTED",
    }


def check_bounded_identity_and_temporal_validation(
    config: dict[str, Any],
    source_registry_doc: dict[str, Any],
    bounded_scope_doc: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    sampled_by_alias: dict[str, list[dict[str, Any]]] = {}
    read_limit_rows: list[dict[str, Any]] = []
    bounded_manifest: dict[str, Any] = {
        "scope": BOUNDED_SAMPLE_SCOPE,
        "row_reads_authorized": True,
        "full_data_read_authorized": False,
        "state_materialization_authorized": False,
        "sources": {},
    }
    for alias, source_scope in bounded_scope_doc["sources"].items():
        sampled_rows, source_limit_rows, source_manifest = sample_source_rows(
            alias=alias,
            source_binding=source_registry_doc["bindings"][alias],
            source_scope=source_scope,
        )
        sampled_by_alias[alias] = sampled_rows
        read_limit_rows.extend(source_limit_rows)
        bounded_manifest["sources"][alias] = source_manifest
    total_rows_read = sum(int(row["rows_read"]) for row in read_limit_rows)
    if total_rows_read > int(bounded_scope_doc["global_limits"]["maximum_total_rows"]):
        raise ProbeError("bounded sample row read limit exceeded")

    reference_map: dict[str, set[str]] = {}
    for row in sampled_by_alias.get("004_master_daily_table", []):
        values = row["values"]
        ticker = values.get("ticker")
        instrument_id = values.get("instrument_id")
        if ticker not in (None, "") and instrument_id not in (None, ""):
            reference_map.setdefault(str(ticker), set()).add(str(instrument_id))
    reference_ambiguities = {ticker for ticker, instrument_ids in reference_map.items() if len(instrument_ids) > 1}

    identity_rows = [
        identity_report_row(alias, sampled_by_alias.get(alias, []), source_scope, reference_map, reference_ambiguities)
        for alias, source_scope in bounded_scope_doc["sources"].items()
    ]

    timestamp_rows: list[dict[str, Any]] = []
    parsed_timestamps: dict[str, dict[str, list[datetime]]] = {}
    for alias, source_scope in bounded_scope_doc["sources"].items():
        rows, parsed_by_field = timestamp_parse_report_rows(alias, sampled_by_alias.get(alias, []), source_scope)
        timestamp_rows.extend(rows)
        parsed_timestamps[alias] = parsed_by_field

    cutoff_rows: list[dict[str, Any]] = []
    for alias in ("013_ohlcv_1m_quote_guarded", "014_master_intraday_bar_table_candidate"):
        bar_times = parsed_timestamps.get(alias, {}).get("ts_utc", [])
        cutoff_rows.extend(cutoff_legality_rows(alias, bar_times))

    daily_rows = daily_availability_rows(
        sampled_by_alias.get("004_master_daily_table", []),
        bounded_scope_doc.get("daily_availability_policy", {}),
    )
    summary = bounded_sample_summary_from_reports(
        bounded_manifest=bounded_manifest,
        read_limit_rows=read_limit_rows,
        identity_rows=identity_rows,
        timestamp_rows=timestamp_rows,
        cutoff_rows=cutoff_rows,
        daily_rows=daily_rows,
        scope_doc=bounded_scope_doc,
    )
    return bounded_manifest, read_limit_rows, identity_rows, timestamp_rows, cutoff_rows, daily_rows, summary



def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    try:
        return bool(value != value)
    except Exception:
        return False


def json_safe_value(value: Any) -> Any:
    if is_missing_value(value):
        return None
    if isinstance(value, datetime):
        parsed = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
        return parsed.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.hex()
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def key_value_from_partition(sample_row: dict[str, Any], source_binding: dict[str, Any], source_scope: dict[str, Any], key: str) -> Any:
    physical_root = Path(str(source_binding.get("physical_candidate_root"))).resolve()
    file_path = Path(str(sample_row.get("file_path"))).resolve()
    partition_doc = source_scope.get("partition_identity") if isinstance(source_scope.get("partition_identity"), dict) else {}
    if partition_doc and str(partition_doc.get("key")) == key:
        return sample_row.get("partition_identity_value") or partition_value(file_path, physical_root, key, partition_doc.get("type"))
    for dimension_doc in source_scope.get("partition_hidden_dimensions", []):
        if isinstance(dimension_doc, dict) and str(dimension_doc.get("key")) == key:
            return partition_value(file_path, physical_root, key, dimension_doc.get("type"))
    return partition_value(file_path, physical_root, key, "key_value_partition")


def resolve_grain_component(sample_row: dict[str, Any], source_binding: dict[str, Any], source_scope: dict[str, Any], component: str, epoch_units: dict[str, str]) -> tuple[Any, str | None]:
    if component.startswith("partition:"):
        key = component.split(":", 1)[1]
        value = key_value_from_partition(sample_row, source_binding, source_scope, key)
        normalized = json_safe_value(value)
        return normalized, None if not is_missing_value(normalized) else component
    values = sample_row.get("values", {})
    if component not in values:
        return None, component
    raw_value = values.get(component)
    if is_missing_value(raw_value):
        return None, component
    if component in set(source_scope.get("timestamp_fields", [])):
        epoch_unit = epoch_units.get(component)
        parsed, _, _, _ = parse_timestamp_value(raw_value, epoch_unit=epoch_unit if epoch_unit and epoch_unit != "not_applicable" else None)
        if parsed is None:
            return None, component
        return parsed.isoformat().replace("+00:00", "Z"), None
    if component in set(source_scope.get("date_fields", [])):
        parsed_date = parse_session_date_value(raw_value)
        if parsed_date is None:
            return None, component
        return parsed_date.isoformat(), None
    return json_safe_value(raw_value), None


def build_grain_key(sample_row: dict[str, Any], source_binding: dict[str, Any], source_scope: dict[str, Any], components: list[str], epoch_units: dict[str, str]) -> tuple[str | None, list[str], dict[str, Any]]:
    component_values: dict[str, Any] = {}
    missing_components: list[str] = []
    for component in components:
        value, missing = resolve_grain_component(sample_row, source_binding, source_scope, str(component), epoch_units)
        component_values[str(component)] = value
        if missing:
            missing_components.append(missing)
    if missing_components:
        return None, missing_components, component_values
    key_value = [(component, component_values[str(component)]) for component in components]
    return compact_json(key_value), [], component_values


def state_signature(sample_row: dict[str, Any], columns: list[str]) -> str:
    values = sample_row.get("values", {})
    present = {column: json_safe_value(values.get(column)) for column in columns if column in values}
    if not present:
        return "NO_STATE_COLUMNS_DECLARED_OR_READ"
    return compact_json(present)


def hidden_dimensions_for_row(sample_row: dict[str, Any], source_binding: dict[str, Any], source_scope: dict[str, Any]) -> dict[str, Any]:
    dimensions: dict[str, Any] = {}
    values = sample_row.get("values", {})
    hidden_names = [str(item) for item in source_scope.get("hidden_dimension_candidates", [])]
    for dimension_doc in source_scope.get("partition_hidden_dimensions", []):
        if isinstance(dimension_doc, dict):
            key = str(dimension_doc.get("key"))
            if key and key not in hidden_names:
                hidden_names.append(key)
    for key in hidden_names:
        value = values.get(key) if key in values else key_value_from_partition(sample_row, source_binding, source_scope, key)
        if not is_missing_value(value):
            dimensions[key] = json_safe_value(value)
    return dimensions


def timestamp_units_for_scope(rows: list[dict[str, Any]], source_scope: dict[str, Any]) -> dict[str, str]:
    units: dict[str, str] = {}
    for field in source_scope.get("timestamp_fields", []):
        values = [row["values"].get(field) for row in rows if field in row.get("values", {})]
        if any(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            units[str(field)], _ = numeric_epoch_unit(values)
        else:
            units[str(field)] = "not_applicable"
    return units


def duplicate_group_rows_for_scope(*, alias: str, key_scope: str, groups: dict[str, list[dict[str, Any]]], conflict_columns: list[str]) -> tuple[list[dict[str, Any]], int, int, int, int, int]:
    rows: list[dict[str, Any]] = []
    duplicate_groups = 0
    duplicate_rows = 0
    identical_groups = 0
    conflicting_groups = 0
    failed_groups = 0
    for key, docs in sorted(groups.items()):
        if len(docs) <= 1:
            continue
        duplicate_groups += 1
        duplicate_rows += len(docs)
        distinct_state = sorted({doc["state_signature"] for doc in docs})
        hidden_values: dict[str, list[Any]] = {}
        for doc in docs:
            for dimension, value in doc.get("hidden_dimensions", {}).items():
                hidden_values.setdefault(dimension, [])
                if value not in hidden_values[dimension]:
                    hidden_values[dimension].append(value)
        has_hidden_dimension_split = any(len(values) > 1 for values in hidden_values.values())
        if len(distinct_state) <= 1:
            identical_groups += 1
            classification = "non_unique_identical_duplicates"
        else:
            conflicting_groups += 1
            classification = "non_unique_conflicting_states"
        severity = "FAIL"
        if alias == "raw_quotes":
            severity = "WARN"
            finding = "same quote timestamp requires additional ordering key" if classification == "non_unique_conflicting_states" else "same quote timestamp has identical duplicate quote rows in sample"
        elif alias == "004_master_daily_table" and has_hidden_dimension_split:
            severity = "WARN"
            finding = "duplicate logical daily key appears across declared hidden dimension; selection policy required"
        elif classification == "non_unique_identical_duplicates":
            severity = "WARN"
            finding = "duplicate key rows are identical in checked state columns"
        else:
            finding = "duplicate key rows have conflicting state values"
        if severity == "FAIL":
            failed_groups += 1
        rows.append({
            "source_alias": alias,
            "key_scope": key_scope,
            "key_value": key,
            "row_count": len(docs),
            "file_count": len({doc["file_path"] for doc in docs}),
            "hidden_dimension_values": compact_json(hidden_values),
            "distinct_state_count": len(distinct_state),
            "duplicate_classification": classification,
            "severity": severity,
            "finding": finding,
        })
    return rows, duplicate_groups, duplicate_rows, identical_groups, conflicting_groups, failed_groups


def hidden_dimension_report_rows(alias: str, docs: list[dict[str, Any]], physical_groups: dict[str, list[dict[str, Any]]], source_scope: dict[str, Any]) -> list[dict[str, Any]]:
    dimensions = [str(item) for item in source_scope.get("hidden_dimension_candidates", [])]
    for dimension_doc in source_scope.get("partition_hidden_dimensions", []):
        if isinstance(dimension_doc, dict):
            key = str(dimension_doc.get("key"))
            if key and key not in dimensions:
                dimensions.append(key)
    output: list[dict[str, Any]] = []
    for dimension in dimensions:
        observed_values = sorted({str(doc.get("hidden_dimensions", {}).get(dimension)) for doc in docs if dimension in doc.get("hidden_dimensions", {})})
        affected_groups = 0
        for group_docs in physical_groups.values():
            values = {str(doc.get("hidden_dimensions", {}).get(dimension)) for doc in group_docs if dimension in doc.get("hidden_dimensions", {})}
            if len(values) > 1:
                affected_groups += 1
        if affected_groups:
            status, severity, finding = "AFFECTS_CANDIDATE_GRAIN", "WARN", "declared hidden dimension splits duplicate candidate keys in bounded sample"
        elif len(observed_values) > 1:
            status, severity, finding = "OBSERVED_NOT_DUPLICATING_IN_SAMPLE", "WARN", "declared hidden dimension has multiple observed values but did not split sampled duplicate keys"
        elif observed_values:
            status, severity, finding = "OBSERVED_SINGLE_VALUE", "INFO", "declared hidden dimension observed with one sampled value"
        else:
            status, severity, finding = "NOT_OBSERVED", "INFO", "declared hidden dimension not observed in bounded sample"
        output.append({
            "source_alias": alias,
            "dimension": dimension,
            "observed_values": format_list(observed_values),
            "affected_duplicate_groups": affected_groups,
            "status": status,
            "severity": severity,
            "finding": finding,
        })
    return output


def raw_quotes_same_timestamp_rows(alias: str, physical_groups: dict[str, list[dict[str, Any]]], source_scope: dict[str, Any]) -> list[dict[str, Any]]:
    if alias != "raw_quotes":
        return []
    output: list[dict[str, Any]] = []
    quote_columns = list(source_scope.get("raw_quote_state_columns", source_scope.get("state_columns_for_conflict_check", [])))
    for docs in physical_groups.values():
        if len(docs) <= 1:
            continue
        first_values = docs[0].get("component_values", {})
        distinct_quote_states = {state_signature({"values": doc["raw_values"]}, quote_columns) for doc in docs}
        classification = "instrument_id_plus_quote_timestamp_non_unique_with_distinct_quote_states" if len(distinct_quote_states) > 1 else "instrument_id_plus_quote_timestamp_non_unique_but_identical_duplicates"
        output.append({
            "source_alias": alias,
            "ticker": first_values.get("partition:ticker", ""),
            "quote_timestamp": first_values.get("timestamp", ""),
            "row_count": len(docs),
            "distinct_quote_state_count": len(distinct_quote_states),
            "classification": classification,
            "sequence_field_availability": "unavailable_in_current_scope",
            "source_row_ordinal_availability": "not_declared",
            "severity": "WARN",
            "finding": "quote timestamp alone is not sufficient as a governed physical ordering key" if len(distinct_quote_states) > 1 else "same-timestamp quote rows are duplicated identically in bounded sample",
        })
    return output


def window_overlap_metrics(rows: list[dict[str, Any]], source_scope: dict[str, Any], epoch_units: dict[str, str]) -> dict[str, Any]:
    overlap_config = source_scope.get("overlap_check") if isinstance(source_scope.get("overlap_check"), dict) else None
    if not overlap_config:
        return {"invalid_window_rows": 0, "window_overlap_groups": 0, "window_overlap_pairs": 0, "window_label_conflict_groups": 0}
    start_field = str(overlap_config.get("window_start"))
    end_field = str(overlap_config.get("window_end"))
    group_fields = [str(field) for field in overlap_config.get("group_by", [])]
    groups: dict[str, list[tuple[datetime, datetime]]] = {}
    invalid_count = 0
    labels_by_event_window: dict[str, set[str]] = {}
    for sample_row in rows:
        values = sample_row.get("values", {})
        start_ts, _, _, _ = parse_timestamp_value(values.get(start_field), epoch_unit=epoch_units.get(start_field))
        end_ts, _, _, _ = parse_timestamp_value(values.get(end_field), epoch_unit=epoch_units.get(end_field))
        event_window_id = values.get("event_window_id")
        window_label = values.get("window_label")
        if not is_missing_value(event_window_id) and not is_missing_value(window_label):
            labels_by_event_window.setdefault(str(event_window_id), set()).add(str(window_label))
        if start_ts is None or end_ts is None:
            invalid_count += 1
            continue
        if start_ts > end_ts:
            invalid_count += 1
        group_key = compact_json([(field, json_safe_value(values.get(field))) for field in group_fields])
        groups.setdefault(group_key, []).append((start_ts, end_ts))
    overlap_groups = 0
    overlap_pairs = 0
    for intervals in groups.values():
        ordered = sorted(intervals, key=lambda pair: (pair[0], pair[1]))
        last_end: datetime | None = None
        group_has_overlap = False
        for start_ts, end_ts in ordered:
            if last_end is not None and start_ts < last_end:
                overlap_pairs += 1
                group_has_overlap = True
            if last_end is None or end_ts > last_end:
                last_end = end_ts
        if group_has_overlap:
            overlap_groups += 1
    label_conflicts = sum(1 for labels in labels_by_event_window.values() if len(labels) > 1)
    return {
        "invalid_window_rows": invalid_count,
        "window_overlap_groups": overlap_groups,
        "window_overlap_pairs": overlap_pairs,
        "window_label_conflict_groups": label_conflicts,
    }


def grain_validate_source(*, alias: str, source_binding: dict[str, Any], source_scope: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    sampled_rows, read_limit_rows, manifest_doc = sample_source_rows(alias=alias, source_binding=source_binding, source_scope=source_scope)
    epoch_units = timestamp_units_for_scope(sampled_rows, source_scope)
    conflict_columns = list(source_scope.get("state_columns_for_conflict_check", []))
    physical_components = [str(component) for component in source_scope.get("physical_key_components", [])]
    canonical_components = [str(component) for component in source_scope.get("canonical_key_components", [])]
    null_key_rows: list[dict[str, Any]] = []
    physical_groups: dict[str, list[dict[str, Any]]] = {}
    canonical_groups: dict[str, list[dict[str, Any]]] = {}
    doc_rows: list[dict[str, Any]] = []

    for row_index, sample_row in enumerate(sampled_rows):
        physical_key, physical_missing, physical_values = build_grain_key(sample_row, source_binding, source_scope, physical_components, epoch_units)
        canonical_key, canonical_missing, canonical_values = build_grain_key(sample_row, source_binding, source_scope, canonical_components, epoch_units)
        hidden_dimensions = hidden_dimensions_for_row(sample_row, source_binding, source_scope)
        doc = {
            "row_index": row_index,
            "file_path": sample_row["file_path"],
            "raw_values": sample_row.get("values", {}),
            "component_values": {**physical_values, **canonical_values},
            "state_signature": state_signature(sample_row, conflict_columns),
            "hidden_dimensions": hidden_dimensions,
        }
        doc_rows.append(doc)
        for key_scope, key_value, missing_components, groups in (
            ("physical", physical_key, physical_missing, physical_groups),
            ("canonical", canonical_key, canonical_missing, canonical_groups),
        ):
            if missing_components:
                null_key_rows.append({
                    "source_alias": alias,
                    "key_scope": key_scope,
                    "row_index": row_index,
                    "file_path": sample_row["file_path"],
                    "missing_components": format_list(sorted(set(missing_components))),
                    "severity": "FAIL",
                    "finding": "one or more candidate grain key components are missing or unparsable",
                })
            elif key_value is not None:
                groups.setdefault(key_value, []).append(doc)

    physical_duplicate_rows, physical_duplicate_groups, physical_duplicate_row_count, physical_identical, physical_conflicting, physical_failed = duplicate_group_rows_for_scope(
        alias=alias, key_scope="physical", groups=physical_groups, conflict_columns=conflict_columns)
    canonical_duplicate_rows, canonical_duplicate_groups, canonical_duplicate_row_count, canonical_identical, canonical_conflicting, canonical_failed = duplicate_group_rows_for_scope(
        alias=alias, key_scope="canonical", groups=canonical_groups, conflict_columns=conflict_columns)
    duplicate_rows = physical_duplicate_rows + canonical_duplicate_rows
    hidden_rows = hidden_dimension_report_rows(alias, doc_rows, physical_groups, source_scope)
    raw_quote_rows = raw_quotes_same_timestamp_rows(alias, physical_groups, source_scope)
    window_metrics = window_overlap_metrics(sampled_rows, source_scope, epoch_units)

    physical_null_count = sum(1 for row in null_key_rows if row["key_scope"] == "physical")
    canonical_null_count = sum(1 for row in null_key_rows if row["key_scope"] == "canonical")
    restriction_reasons: list[str] = []
    if source_scope.get("canonical_identity_status"):
        restriction_reasons.append(str(source_scope.get("canonical_identity_status")))
    if source_scope.get("instrument_id_physical_readiness"):
        restriction_reasons.append(str(source_scope.get("instrument_id_physical_readiness")))
    if hidden_rows:
        restriction_reasons.append("hidden_dimension_policy_pending")
    if alias == "004_master_daily_table":
        restriction_reasons.append("daily_availability_policy_restricted")

    if physical_null_count or canonical_null_count:
        status, severity, finding = "BLOCKED_MISSING_KEY_COMPONENT", "FAIL", "bounded sample contains missing or unparsable candidate key components"
    elif physical_failed or canonical_failed:
        status, severity, finding = "FAILED", "FAIL", "bounded sample found duplicate candidate keys with conflicting state values"
    elif alias == "004_master_daily_table" and (physical_duplicate_groups or canonical_duplicate_groups):
        status, severity, finding = "NON_UNIQUE_EXPECTED_DIMENSION", "WARN", "bounded daily key is non-unique until declared hidden dimensions are governed"
    elif alias == "raw_quotes" and (physical_duplicate_groups or canonical_duplicate_groups):
        status, severity, finding = "PASS_WITH_RESTRICTIONS", "WARN", "quote timestamp grain requires an additional governed ordering key"
    elif physical_duplicate_groups or canonical_duplicate_groups:
        status, severity, finding = "PASS_WITH_RESTRICTIONS", "WARN", "duplicate candidate keys are identical in checked state columns; duplicate handling policy is required before builder execution"
    elif window_metrics["invalid_window_rows"]:
        status, severity, finding = "FAILED", "FAIL", "bounded sample contains invalid microstructure window ordering"
    elif window_metrics["window_overlap_groups"] or window_metrics["window_label_conflict_groups"] or restriction_reasons:
        status, severity, finding = "PASS_WITH_RESTRICTIONS", "WARN", "candidate grain is usable in sample with declared restrictions"
    elif not sampled_rows:
        status, severity, finding = "FAILED", "FAIL", "no rows available for bounded grain validation"
    else:
        status, severity, finding = "PASS", "INFO", "candidate grain key is unique and usable inside bounded sample"

    physical_uniqueness = "UNIQUE" if not physical_duplicate_groups and not physical_null_count else "NON_UNIQUE" if physical_duplicate_groups else "NULL_KEY_ROWS"
    canonical_uniqueness = "UNIQUE" if not canonical_duplicate_groups and not canonical_null_count else "NON_UNIQUE" if canonical_duplicate_groups else "NULL_KEY_ROWS"
    hidden_observed: dict[str, list[str]] = {}
    for doc in doc_rows:
        for dimension, value in doc.get("hidden_dimensions", {}).items():
            hidden_observed.setdefault(dimension, [])
            text = str(value)
            if text not in hidden_observed[dimension]:
                hidden_observed[dimension].append(text)
    source_row = {
        "source_alias": alias,
        "rows_checked": len(sampled_rows),
        "files_sampled": len({row["file_path"] for row in sampled_rows}),
        "physical_key_components": format_list(physical_components),
        "canonical_key_components": format_list(canonical_components),
        "key_rows_checked": len(sampled_rows),
        "null_key_rows": physical_null_count,
        "physical_duplicate_key_groups": physical_duplicate_groups,
        "physical_duplicate_key_rows": physical_duplicate_row_count,
        "canonical_duplicate_key_groups": canonical_duplicate_groups,
        "canonical_duplicate_key_rows": canonical_duplicate_row_count,
        "identical_duplicate_groups": physical_identical,
        "conflicting_duplicate_groups": physical_conflicting,
        "hidden_dimension_candidates": format_list(source_scope.get("hidden_dimension_candidates", [])),
        "hidden_dimension_values_observed": compact_json(hidden_observed),
        "physical_key_uniqueness": physical_uniqueness,
        "canonical_key_uniqueness": canonical_uniqueness,
        "instrument_id_physical_readiness": source_scope.get("instrument_id_physical_readiness", ""),
        "identity_resolution_source": source_scope.get("identity_resolution_source", ""),
        "sequence_field_availability": "unavailable_in_current_scope" if alias == "raw_quotes" else "not_applicable",
        "source_row_ordinal_availability": "not_declared" if alias == "raw_quotes" else "not_applicable",
        "window_invalid_rows": window_metrics["invalid_window_rows"],
        "window_overlap_groups": window_metrics["window_overlap_groups"],
        "window_overlap_pairs": window_metrics["window_overlap_pairs"],
        "window_label_conflict_groups": window_metrics["window_label_conflict_groups"],
        "grain_validation_status": status,
        "severity": severity,
        "finding": finding,
        "restriction_reasons": format_list(sorted(set(restriction_reasons))),
    }
    manifest_doc["epoch_units"] = epoch_units
    manifest_doc["physical_key_components"] = physical_components
    manifest_doc["canonical_key_components"] = canonical_components
    return source_row, read_limit_rows, duplicate_rows, null_key_rows, hidden_rows, raw_quote_rows, manifest_doc


def bounded_grain_summary_from_reports(*, bounded_manifest: dict[str, Any], read_limit_rows: list[dict[str, Any]], grain_rows: list[dict[str, Any]], duplicate_rows: list[dict[str, Any]], null_key_rows: list[dict[str, Any]], hidden_rows: list[dict[str, Any]], raw_quote_rows: list[dict[str, Any]], scope_doc: dict[str, Any]) -> dict[str, Any]:
    total_rows_read = sum(int(row["rows_read"]) for row in read_limit_rows)
    maximum_rows_authorized = int(scope_doc["global_limits"]["maximum_total_rows"])
    limit_violation = total_rows_read > maximum_rows_authorized or any(str(row["limit_respected"]) != "True" for row in read_limit_rows)
    failed_sources = sum(1 for row in grain_rows if row["grain_validation_status"] == "FAILED")
    blocked_sources = sum(1 for row in grain_rows if row["grain_validation_status"] == "BLOCKED_MISSING_KEY_COMPONENT")
    restricted_sources = sum(1 for row in grain_rows if row["grain_validation_status"] in {"PASS_WITH_RESTRICTIONS", "NON_UNIQUE_EXPECTED_DIMENSION"})
    if limit_violation or failed_sources:
        validation = "FAILED"
        overall = "failed_bounded_grain_validation"
    elif blocked_sources:
        validation = "BLOCKED"
        overall = "blocked_bounded_grain_validation"
    elif restricted_sources or any(row.get("severity") == "WARN" for row in duplicate_rows + hidden_rows + raw_quote_rows):
        validation = "PASS_WITH_RESTRICTIONS"
        overall = "passed_bounded_grain_validation_with_restrictions"
    else:
        validation = "PASS"
        overall = "passed_bounded_grain_validation"
    physical_unique_sources = sum(1 for row in grain_rows if row["physical_key_uniqueness"] == "UNIQUE")
    physical_non_unique_sources = sum(1 for row in grain_rows if row["physical_key_uniqueness"] != "UNIQUE")
    canonical_unique_sources = sum(1 for row in grain_rows if row["canonical_key_uniqueness"] == "UNIQUE")
    canonical_non_unique_sources = sum(1 for row in grain_rows if row["canonical_key_uniqueness"] != "UNIQUE")
    daily_policy = scope_doc.get("daily_availability_policy_readiness", {}) if isinstance(scope_doc.get("daily_availability_policy_readiness"), dict) else {}
    duplicate_group_count = sum(int(row["physical_duplicate_key_groups"]) for row in grain_rows)
    duplicate_row_count = sum(int(row["physical_duplicate_key_rows"]) for row in grain_rows)
    identical_duplicate_groups = sum(int(row["identical_duplicate_groups"]) for row in grain_rows)
    conflicting_duplicate_groups = sum(int(row["conflicting_duplicate_groups"]) for row in grain_rows)
    return {
        "overall_status": overall,
        "bounded_grain_validation": validation,
        "bounded_grain_data_read": "EXECUTED_WITH_LIMITS",
        "bounded_grain_scope": BOUNDED_GRAIN_SCOPE,
        "bounded_grain_scope_id": scope_doc.get("scope_id"),
        "bounded_grain_sources_authorized": len(scope_doc.get("sources", {})),
        "bounded_grain_sources_sampled": len(bounded_manifest.get("sources", {})),
        "bounded_grain_files_sampled": sum(len(source_doc.get("files_sampled", [])) for source_doc in bounded_manifest.get("sources", {}).values()),
        "bounded_grain_rows_read": total_rows_read,
        "bounded_grain_maximum_rows_authorized": maximum_rows_authorized,
        "bounded_grain_limits_respected": not limit_violation,
        "bounded_grain_sources_passed": sum(1 for row in grain_rows if row["grain_validation_status"] == "PASS"),
        "bounded_grain_sources_passed_with_restrictions": restricted_sources,
        "bounded_grain_sources_non_unique_expected_dimension": sum(1 for row in grain_rows if row["grain_validation_status"] == "NON_UNIQUE_EXPECTED_DIMENSION"),
        "bounded_grain_sources_blocked_missing_key_component": blocked_sources,
        "bounded_grain_sources_failed": failed_sources,
        "rows_checked": total_rows_read,
        "key_rows_checked": sum(int(row["key_rows_checked"]) for row in grain_rows),
        "null_key_rows": sum(int(row["null_key_rows"]) for row in grain_rows),
        "duplicate_key_rows": duplicate_row_count,
        "duplicate_key_groups": duplicate_group_count,
        "physical_key_unique_sources": physical_unique_sources,
        "physical_key_non_unique_sources": physical_non_unique_sources,
        "canonical_key_unique_sources": canonical_unique_sources,
        "canonical_key_non_unique_sources": canonical_non_unique_sources,
        "identical_duplicate_groups": identical_duplicate_groups,
        "conflicting_duplicate_groups": conflicting_duplicate_groups,
        "hidden_dimension_candidates": len(hidden_rows),
        "raw_quotes_same_timestamp_groups": len(raw_quote_rows),
        "daily_availability_policy_readiness": daily_policy.get("daily_availability_policy_status", "restricted"),
        "calendar_validation_pending": bool(daily_policy.get("calendar_validation_pending", True)),
        "timezone_session_policy_pending": bool(daily_policy.get("timezone_session_policy_pending", True)),
        "data_resolution": "BOUNDED_GRAIN_AUTHORIZED_BY_SCOPE",
        "data_validation": "BOUNDED_GRAIN_EXECUTED_WITH_LIMITS",
        "grain_validation": validation,
        "temporal_value_validation": "BOUNDED_PARSE_AVAILABLE_FOR_GRAIN_KEYS",
        "quality_semantics_validation": "PARTIAL_NOT_EXECUTED",
        "builder_validation_execution": "NOT_EXECUTED",
        "market_state_integration": "NOT_EXECUTED",
    }


def check_bounded_grain_validation(config: dict[str, Any], source_registry_doc: dict[str, Any], bounded_grain_scope_doc: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    read_limit_rows: list[dict[str, Any]] = []
    grain_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    null_key_rows: list[dict[str, Any]] = []
    hidden_rows: list[dict[str, Any]] = []
    raw_quote_rows: list[dict[str, Any]] = []
    bounded_manifest: dict[str, Any] = {
        "scope": BOUNDED_GRAIN_SCOPE,
        "row_reads_authorized": True,
        "full_data_read_authorized": False,
        "state_materialization_authorized": False,
        "sources": {},
    }
    for alias, source_scope in bounded_grain_scope_doc["sources"].items():
        source_row, source_limit_rows, source_duplicate_rows, source_null_rows, source_hidden_rows, source_raw_quote_rows, source_manifest = grain_validate_source(
            alias=alias,
            source_binding=source_registry_doc["bindings"][alias],
            source_scope=source_scope,
        )
        grain_rows.append(source_row)
        read_limit_rows.extend(source_limit_rows)
        duplicate_rows.extend(source_duplicate_rows)
        null_key_rows.extend(source_null_rows)
        hidden_rows.extend(source_hidden_rows)
        raw_quote_rows.extend(source_raw_quote_rows)
        bounded_manifest["sources"][alias] = source_manifest
    total_rows_read = sum(int(row["rows_read"]) for row in read_limit_rows)
    if total_rows_read > int(bounded_grain_scope_doc["global_limits"]["maximum_total_rows"]):
        raise ProbeError("bounded grain row read limit exceeded")
    summary = bounded_grain_summary_from_reports(
        bounded_manifest=bounded_manifest,
        read_limit_rows=read_limit_rows,
        grain_rows=grain_rows,
        duplicate_rows=duplicate_rows,
        null_key_rows=null_key_rows,
        hidden_rows=hidden_rows,
        raw_quote_rows=raw_quote_rows,
        scope_doc=bounded_grain_scope_doc,
    )
    return bounded_manifest, read_limit_rows, grain_rows, duplicate_rows, null_key_rows, hidden_rows, raw_quote_rows, summary


def numeric_probe_value(value: Any) -> float | None:
    if is_missing_value(value) or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def policy_statuses_for_scope(source_scope: dict[str, Any]) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    refs = [str(ref) for ref in source_scope.get("policy_refs", []) if str(ref)]
    for check in source_scope.get("quality_lineage_checks", []):
        if isinstance(check, dict):
            ref = str(check.get("policy_ref", ""))
            if ref and ref not in refs:
                refs.append(ref)
    for ref in refs:
        path = resolve_policy_path(ref)
        exists = path.exists()
        statuses[ref] = {"policy_ref": ref, "policy_path": str(path), "policy_exists": exists, "policy_sha256": sha256_file(path) if exists else ""}
    return statuses


def duplicate_metrics_for_quality(alias: str, rows: list[dict[str, Any]], source_binding: dict[str, Any], source_scope: dict[str, Any], check_doc: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    components = [str(component) for component in check_doc.get("key_components", [])]
    state_columns = [str(column) for column in check_doc.get("state_columns", [])]
    epoch_units = timestamp_units_for_scope(rows, source_scope)
    groups: dict[str, list[dict[str, Any]]] = {}
    missing_key_rows = 0
    for row_index, sample_row in enumerate(rows):
        key, missing, component_values = build_grain_key(sample_row, source_binding, source_scope, components, epoch_units)
        if missing:
            missing_key_rows += 1
            continue
        if key is None:
            continue
        groups.setdefault(key, []).append({
            "row_index": row_index,
            "file_path": sample_row["file_path"],
            "raw_values": sample_row.get("values", {}),
            "component_values": component_values,
            "state_signature": state_signature(sample_row, state_columns),
            "hidden_dimensions": hidden_dimensions_for_row(sample_row, source_binding, source_scope),
        })
    duplicate_rows, duplicate_groups, duplicate_row_count, identical_groups, conflicting_groups, failed_groups = duplicate_group_rows_for_scope(
        alias=alias,
        key_scope="quality_lineage_policy",
        groups=groups,
        conflict_columns=state_columns,
    )
    return duplicate_rows, {
        "rows_checked": len(rows),
        "duplicate_groups": duplicate_groups,
        "duplicate_rows": duplicate_row_count,
        "identical_duplicate_groups": identical_groups,
        "conflicting_duplicate_groups": conflicting_groups,
        "failed_duplicate_groups": failed_groups,
        "missing_key_rows": missing_key_rows,
    }


def price_view_selection_metrics(rows: list[dict[str, Any]], source_binding: dict[str, Any], source_scope: dict[str, Any], check_doc: dict[str, Any]) -> dict[str, Any]:
    selected = str(check_doc.get("selected_price_view", ""))
    observed: dict[str, int] = {}
    for row in rows:
        value = row.get("values", {}).get("price_view")
        if is_missing_value(value):
            value = key_value_from_partition(row, source_binding, source_scope, "price_view")
        if not is_missing_value(value):
            text = str(value)
            observed[text] = observed.get(text, 0) + 1
    return {
        "rows_checked": len(rows),
        "selected_price_view": selected,
        "observed_price_views": observed,
        "selected_price_view_rows": observed.get(selected, 0),
        "selected_price_view_present": bool(selected and observed.get(selected, 0) > 0),
    }


def temporal_legality_derivation_metrics(rows: list[dict[str, Any]], source_scope: dict[str, Any], check_doc: dict[str, Any]) -> dict[str, Any]:
    timestamp_fields = [str(field) for field in check_doc.get("timestamp_fields", source_scope.get("timestamp_fields", []))]
    local_scope = {**source_scope, "timestamp_fields": timestamp_fields}
    epoch_units = timestamp_units_for_scope(rows, local_scope)
    checked = 0
    parse_failures = 0
    null_values = 0
    parsed_pairs: list[tuple[datetime | None, datetime | None]] = []
    start_field = str(check_doc.get("window_start", ""))
    end_field = str(check_doc.get("window_end", ""))
    for sample_row in rows:
        values = sample_row.get("values", {})
        start_parsed: datetime | None = None
        end_parsed: datetime | None = None
        for field in timestamp_fields:
            if field not in values:
                continue
            checked += 1
            value = values.get(field)
            if is_missing_value(value):
                null_values += 1
                continue
            unit = epoch_units.get(field)
            parsed, _, _, _ = parse_timestamp_value(value, epoch_unit=unit if unit and unit != "not_applicable" else None)
            if parsed is None:
                parse_failures += 1
            if field == start_field:
                start_parsed = parsed
            if field == end_field:
                end_parsed = parsed
        if start_field and end_field:
            parsed_pairs.append((start_parsed, end_parsed))
    invalid_windows = sum(1 for start, end in parsed_pairs if start is not None and end is not None and start > end)
    return {"rows_checked": len(rows), "timestamp_values_checked": checked, "timestamp_parse_failures": parse_failures, "timestamp_null_values": null_values, "invalid_window_rows": invalid_windows, "timestamp_fields": timestamp_fields}


def raw_quote_quality_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    two_sided = normal = locked = crossed = invalid = missing_or_non_numeric = negative_size_rows = non_positive_price_rows = 0
    for sample_row in rows:
        values = sample_row.get("values", {})
        bid = numeric_probe_value(values.get("bid_price"))
        ask = numeric_probe_value(values.get("ask_price"))
        bid_size = numeric_probe_value(values.get("bid_size"))
        ask_size = numeric_probe_value(values.get("ask_size"))
        if bid is None or ask is None or bid_size is None or ask_size is None:
            invalid += 1
            missing_or_non_numeric += 1
            continue
        if bid <= 0 or ask <= 0:
            invalid += 1
            non_positive_price_rows += 1
            continue
        if bid_size < 0 or ask_size < 0:
            invalid += 1
            negative_size_rows += 1
            continue
        two_sided += 1
        if ask < bid:
            crossed += 1
        elif ask == bid:
            locked += 1
        else:
            normal += 1
    return {"rows_checked": len(rows), "two_sided_rows": two_sided, "normal_quote_rows": normal, "locked_quote_rows": locked, "crossed_quote_rows": crossed, "not_two_sided_or_invalid_rows": invalid, "missing_or_non_numeric_rows": missing_or_non_numeric, "negative_size_rows": negative_size_rows, "non_positive_price_rows": non_positive_price_rows}


def derivation_status_from_metrics(check_doc: dict[str, Any], metrics: dict[str, Any]) -> tuple[str, str, str]:
    check_type = str(check_doc.get("check_type"))
    if check_type == "price_view_selection":
        if not metrics.get("selected_price_view_present"):
            return "BLOCKED", "BLOCKED", "selected price_view not observed in bounded sample"
        return "PASS_WITH_RESTRICTIONS", "WARN", "selected price_view observed; full-history consistency not validated"
    if check_type == "duplicate_intraday_bar_policy":
        if int(metrics.get("missing_key_rows", 0)):
            return "FAILED", "FAIL", "duplicate policy cannot evaluate rows with missing key components"
        if int(metrics.get("conflicting_duplicate_groups", 0)):
            return "BLOCKED", "BLOCKED", "conflicting duplicate intraday bars require governed precedence before builder execution"
        if int(metrics.get("identical_duplicate_groups", 0)):
            return "PASS_WITH_RESTRICTIONS", "WARN", "identical duplicate intraday bars can be deterministically collapsed under policy"
        return "PASS", "INFO", "no duplicate intraday bar groups found in bounded sample"
    if check_type == "raw_quote_ordering_policy":
        if int(metrics.get("conflicting_duplicate_groups", 0)):
            return "BLOCKED", "BLOCKED", "same-timestamp raw quotes contain distinct states; additional ordering key required"
        if int(metrics.get("identical_duplicate_groups", 0)):
            return "PASS_WITH_RESTRICTIONS", "WARN", "same-timestamp raw quotes contain identical duplicates; promotion remains restricted"
        return "PASS", "INFO", "raw quote timestamp key had no duplicate groups in bounded sample"
    if check_type == "raw_quote_quality_policy":
        if int(metrics.get("rows_checked", 0)) == 0:
            return "FAILED", "FAIL", "no raw quote rows available for quality policy derivation"
        return "PASS_WITH_RESTRICTIONS", "WARN", "raw quote quality labels are derivable in sample but full-history quality is not validated"
    if check_type == "temporal_legality_derivation":
        if int(metrics.get("timestamp_parse_failures", 0)) or int(metrics.get("invalid_window_rows", 0)):
            return "FAILED", "FAIL", "temporal legality derivation found parse or window ordering failures"
        return "PASS_WITH_RESTRICTIONS", "WARN", "temporal legality flag is derivable for sampled rows; full temporal legality remains a later gate"
    if check_type == "dataset_lineage_metadata":
        return "PASS_WITH_RESTRICTIONS", "WARN", "dataset lineage anchor exists at binding level; row-level lineage not validated"
    return "PASS_WITH_RESTRICTIONS", "WARN", f"quality/lineage check type {check_type} classified with restrictions"


def quality_lineage_validate_source(alias: str, source_binding: dict[str, Any], source_scope: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sampled_rows, read_limit_rows, manifest_doc = sample_source_rows(alias=alias, source_binding=source_binding, source_scope=source_scope)
    policy_statuses = policy_statuses_for_scope(source_scope)
    check_results: dict[str, dict[str, Any]] = {}
    derivation_rows: list[dict[str, Any]] = []
    for check_doc in source_scope.get("quality_lineage_checks", []):
        check_id = str(check_doc.get("check_id"))
        check_type = str(check_doc.get("check_type"))
        if check_type in {"duplicate_intraday_bar_policy", "raw_quote_ordering_policy"}:
            _, metrics = duplicate_metrics_for_quality(alias, sampled_rows, source_binding, source_scope, check_doc)
        elif check_type == "price_view_selection":
            metrics = price_view_selection_metrics(sampled_rows, source_binding, source_scope, check_doc)
        elif check_type == "raw_quote_quality_policy":
            metrics = raw_quote_quality_metrics(sampled_rows)
        elif check_type == "temporal_legality_derivation":
            metrics = temporal_legality_derivation_metrics(sampled_rows, source_scope, check_doc)
        elif check_type == "dataset_lineage_metadata":
            metrics = {"rows_checked": len(sampled_rows), "binding_version": source_binding.get("binding_version", ""), "review_status": source_binding.get("review_status", "")}
        else:
            metrics = {"rows_checked": len(sampled_rows), "unsupported_check_type": check_type}
        status, severity, finding = derivation_status_from_metrics(check_doc, metrics)
        policy_ref = str(check_doc.get("policy_ref", ""))
        policy_exists = True if not policy_ref else bool(policy_statuses.get(policy_ref, {}).get("policy_exists"))
        if policy_ref and not policy_exists:
            status, severity, finding = "BLOCKED", "BLOCKED", "required policy artifact is missing"
        result = {"source_alias": alias, "policy_check": check_id, "check_type": check_type, "policy_ref": policy_ref, "policy_exists": policy_exists, "rows_checked": len(sampled_rows), "derivation_status": status, "severity": severity, "finding": finding, "metrics": metrics}
        check_results[check_id] = result
        derivation_rows.append({**result, "metrics": compact_json(metrics)})
    field_rows: list[dict[str, Any]] = []
    builder_blocker_rows: list[dict[str, Any]] = []
    promotion_rows: list[dict[str, Any]] = []
    for field in source_scope.get("quality_lineage_fields", []):
        strategy = str(field.get("resolution_strategy"))
        policy_ref = str(field.get("policy_ref", ""))
        policy_check = str(field.get("policy_check", ""))
        policy_exists = True if not policy_ref else bool(policy_statuses.get(policy_ref, {}).get("policy_exists"))
        check_result = check_results.get(policy_check, {})
        check_status = str(check_result.get("derivation_status", "PASS_WITH_RESTRICTIONS"))
        check_finding = str(check_result.get("finding", "classified by quality/lineage scope"))
        if strategy == "unavailable_pending_source_fix":
            status, severity, finding = "BLOCKED_PENDING_SOURCE_FIX", "BLOCKED", "logical field is unavailable until source contract exposes governed evidence"
        elif strategy == "policy_classification":
            if check_status == "BLOCKED":
                status, severity, finding = "BLOCKED_PENDING_ORDERING_KEY", "BLOCKED", check_finding
            elif check_status == "FAILED":
                status, severity, finding = "FAILED_POLICY_CLASSIFICATION", "FAIL", check_finding
            else:
                status, severity, finding = "POLICY_CLASSIFIED_WITH_RESTRICTIONS", "WARN", check_finding
        elif strategy in {"derived_by_policy", "derived_by_builder_validation"}:
            if not policy_exists:
                status, severity, finding = "BLOCKED_PENDING_POLICY", "BLOCKED", "required policy artifact is missing"
            elif check_status == "FAILED":
                status, severity, finding = "FAILED_DERIVATION_CHECK", "FAIL", check_finding
            elif check_status == "BLOCKED":
                status, severity, finding = "BLOCKED_BY_POLICY_CHECK", "BLOCKED", check_finding
            elif strategy == "derived_by_builder_validation":
                status, severity, finding = "DERIVABLE_BY_BUILDER_VALIDATION_WITH_RESTRICTIONS", "WARN", check_finding
            else:
                status, severity, finding = "DERIVABLE_BY_POLICY_WITH_RESTRICTIONS", "WARN", check_finding
        elif strategy == "dataset_level_metadata":
            status, severity, finding = "RESOLVED_BY_DATASET_METADATA_WITH_RESTRICTIONS", "WARN", check_finding
        else:
            status, severity, finding = "FAILED_UNSUPPORTED_RESOLUTION_STRATEGY", "FAIL", f"unsupported resolution_strategy={strategy}"
        row = {"source_alias": alias, "logical_field": str(field.get("logical_field")), "field_family": str(field.get("field_family", "")), "resolution_strategy": strategy, "policy_ref": policy_ref, "policy_check": policy_check, "policy_exists": policy_exists, "criticality": str(field.get("criticality", "")), "field_resolution_status": status, "builder_blocker_scope": str(field.get("builder_blocker_scope", "none")), "builder_execution_impact": str(field.get("builder_execution_impact", "none")), "promotion_impact": str(field.get("promotion_impact", "none")), "severity": severity, "finding": finding}
        field_rows.append(row)
        is_builder_blocker = severity in {"FAIL", "BLOCKED"} and row["builder_execution_impact"] != "none" and row["builder_blocker_scope"] != "none"
        if is_builder_blocker:
            builder_blocker_rows.append({"source_alias": alias, "logical_field": row["logical_field"], "builder_blocker_scope": row["builder_blocker_scope"], "builder_execution_impact": row["builder_execution_impact"], "field_resolution_status": status, "severity": severity, "required_resolution": row["promotion_impact"], "finding": finding})
        if row["promotion_impact"] != "none" and not is_builder_blocker:
            promotion_rows.append({"source_alias": alias, "logical_field": row["logical_field"], "promotion_impact": row["promotion_impact"], "field_resolution_status": status, "severity": severity, "finding": finding})
    manifest_doc["policy_statuses"] = policy_statuses
    manifest_doc["quality_lineage_checks"] = {key: {**value, "metrics": value.get("metrics", {})} for key, value in check_results.items()}
    return manifest_doc, read_limit_rows, field_rows, derivation_rows, builder_blocker_rows, promotion_rows


def bounded_quality_lineage_summary_from_reports(*, bounded_manifest: dict[str, Any], read_limit_rows: list[dict[str, Any]], field_rows: list[dict[str, Any]], derivation_rows: list[dict[str, Any]], builder_blocker_rows: list[dict[str, Any]], promotion_rows: list[dict[str, Any]], scope_doc: dict[str, Any]) -> dict[str, Any]:
    total_rows_read = sum(int(row["rows_read"]) for row in read_limit_rows)
    maximum_rows_authorized = int(scope_doc["global_limits"]["maximum_total_rows"])
    limit_violation = total_rows_read > maximum_rows_authorized or any(str(row["limit_respected"]) != "True" for row in read_limit_rows)
    failed_fields = sum(1 for row in field_rows if row["severity"] == "FAIL")
    blocked_fields = sum(1 for row in field_rows if row["severity"] == "BLOCKED")
    warning_fields = sum(1 for row in field_rows if row["severity"] == "WARN")
    core_builder_blockers = sum(1 for row in builder_blocker_rows if row.get("builder_blocker_scope") in {"all", "core_four", "core_four_initial_objects"})
    quote_builder_blockers = sum(1 for row in builder_blocker_rows if row.get("builder_blocker_scope") == "quote_dependent")
    if limit_violation or failed_fields:
        validation, overall = "FAILED", "failed_bounded_quality_lineage_validation"
    elif core_builder_blockers:
        validation, overall = "BLOCKED", "blocked_bounded_quality_lineage_validation"
    elif blocked_fields or warning_fields or builder_blocker_rows or promotion_rows:
        validation, overall = "PASS_WITH_RESTRICTIONS", "passed_bounded_quality_lineage_validation_with_restrictions"
    else:
        validation, overall = "PASS", "passed_bounded_quality_lineage_validation"
    return {"overall_status": overall, "bounded_quality_lineage_validation": validation, "bounded_quality_lineage_data_read": "EXECUTED_WITH_LIMITS", "bounded_quality_lineage_scope": BOUNDED_QUALITY_LINEAGE_SCOPE, "bounded_quality_lineage_scope_id": scope_doc.get("scope_id"), "bounded_quality_lineage_sources_authorized": len(scope_doc.get("sources", {})), "bounded_quality_lineage_sources_sampled": len(bounded_manifest.get("sources", {})), "bounded_quality_lineage_files_sampled": sum(len(source_doc.get("files_sampled", [])) for source_doc in bounded_manifest.get("sources", {}).values()), "bounded_quality_lineage_rows_read": total_rows_read, "bounded_quality_lineage_maximum_rows_authorized": maximum_rows_authorized, "bounded_quality_lineage_limits_respected": not limit_violation, "quality_lineage_fields_checked": len(field_rows), "quality_lineage_derivations_checked": len(derivation_rows), "quality_lineage_fields_failed": failed_fields, "quality_lineage_fields_blocked": blocked_fields, "quality_lineage_fields_with_restrictions": warning_fields, "builder_execution_blockers": len(builder_blocker_rows), "core_four_builder_execution_blockers": core_builder_blockers, "quote_dependent_builder_execution_blockers": quote_builder_blockers, "promotion_only_restrictions": len(promotion_rows), "core_four_builder_execution_readiness": "OPEN_FOR_EXPERIMENTAL_BUILDER_VALIDATION_DESIGN" if core_builder_blockers == 0 and not failed_fields and not limit_violation else "BLOCKED", "quote_dependent_builder_execution_readiness": "BLOCKED_PENDING_QUOTE_ORDERING_OR_ASOF" if quote_builder_blockers else "OPEN_WITH_RESTRICTIONS", "data_resolution": "BOUNDED_QUALITY_LINEAGE_AUTHORIZED_BY_SCOPE", "data_validation": "BOUNDED_QUALITY_LINEAGE_EXECUTED_WITH_LIMITS", "grain_validation": "CLOSED_PASS_WITH_RESTRICTIONS", "temporal_value_validation": "RECHECKED_FOR_QUALITY_LINEAGE_DERIVATION", "quality_semantics_validation": validation, "lineage_validation": "PASS_WITH_RESTRICTIONS" if validation in {"PASS", "PASS_WITH_RESTRICTIONS"} else validation, "builder_validation_execution": "NOT_EXECUTED", "market_state_integration": "NOT_OPEN"}


def check_bounded_quality_and_lineage_validation(config: dict[str, Any], source_registry_doc: dict[str, Any], bounded_quality_scope_doc: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    read_limit_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    derivation_rows: list[dict[str, Any]] = []
    builder_blocker_rows: list[dict[str, Any]] = []
    promotion_rows: list[dict[str, Any]] = []
    bounded_manifest: dict[str, Any] = {"scope": BOUNDED_QUALITY_LINEAGE_SCOPE, "row_reads_authorized": True, "full_data_read_authorized": False, "feature_builder_execution_authorized": False, "state_materialization_authorized": False, "sources": {}}
    for alias, source_scope in bounded_quality_scope_doc["sources"].items():
        source_manifest, source_limit_rows, source_field_rows, source_derivation_rows, source_builder_blocker_rows, source_promotion_rows = quality_lineage_validate_source(alias=alias, source_binding=source_registry_doc["bindings"][alias], source_scope=source_scope)
        bounded_manifest["sources"][alias] = source_manifest
        read_limit_rows.extend(source_limit_rows)
        field_rows.extend(source_field_rows)
        derivation_rows.extend(source_derivation_rows)
        builder_blocker_rows.extend(source_builder_blocker_rows)
        promotion_rows.extend(source_promotion_rows)
    if sum(int(row["rows_read"]) for row in read_limit_rows) > int(bounded_quality_scope_doc["global_limits"]["maximum_total_rows"]):
        raise ProbeError("bounded quality/lineage row read limit exceeded")
    summary = bounded_quality_lineage_summary_from_reports(bounded_manifest=bounded_manifest, read_limit_rows=read_limit_rows, field_rows=field_rows, derivation_rows=derivation_rows, builder_blocker_rows=builder_blocker_rows, promotion_rows=promotion_rows, scope_doc=bounded_quality_scope_doc)
    return bounded_manifest, read_limit_rows, field_rows, derivation_rows, builder_blocker_rows, promotion_rows, summary


def write_bounded_quality_lineage_findings(path: Path, *, run_id: str, summary: dict[str, Any], field_rows: list[dict[str, Any]], derivation_rows: list[dict[str, Any]], builder_blocker_rows: list[dict[str, Any]], promotion_rows: list[dict[str, Any]]) -> None:
    lines = [f"# Bounded Quality And Lineage Findings - {run_id}", "", f"script_version: `{SCRIPT_VERSION}`", f"overall_status: `{summary['overall_status']}`", "", "## Gate Status", "", f"bounded_quality_lineage_validation = {summary.get('bounded_quality_lineage_validation')}", f"bounded_quality_lineage_data_read = {summary.get('bounded_quality_lineage_data_read')}", f"quality_semantics_validation = {summary.get('quality_semantics_validation')}", f"lineage_validation = {summary.get('lineage_validation')}", f"builder_validation_execution = {summary.get('builder_validation_execution')}", f"market_state_integration = {summary.get('market_state_integration')}", "", "## Limits", "", f"sources_sampled = {summary.get('bounded_quality_lineage_sources_sampled')}", f"files_sampled = {summary.get('bounded_quality_lineage_files_sampled')}", f"rows_read = {summary.get('bounded_quality_lineage_rows_read')}", f"maximum_rows_authorized = {summary.get('bounded_quality_lineage_maximum_rows_authorized')}", f"rows_limit_respected = {summary.get('bounded_quality_lineage_limits_respected')}", "", "## Execution Readiness", "", f"builder_execution_blockers = {summary.get('builder_execution_blockers')}", f"core_four_builder_execution_blockers = {summary.get('core_four_builder_execution_blockers')}", f"quote_dependent_builder_execution_blockers = {summary.get('quote_dependent_builder_execution_blockers')}", f"promotion_only_restrictions = {summary.get('promotion_only_restrictions')}", f"core_four_builder_execution_readiness = {summary.get('core_four_builder_execution_readiness')}", f"quote_dependent_builder_execution_readiness = {summary.get('quote_dependent_builder_execution_readiness')}", "", "## Source Field Status", ""]
    for row in field_rows:
        lines.append(f"- {row['source_alias']}.{row['logical_field']}: {row['field_resolution_status']} - {row['finding']}")
    if builder_blocker_rows:
        lines.extend(["", "## Builder Execution Blockers", ""])
        for row in builder_blocker_rows:
            lines.append(f"- {row['source_alias']}.{row['logical_field']}: scope={row['builder_blocker_scope']}; impact={row['builder_execution_impact']}; finding={row['finding']}")
    if promotion_rows:
        lines.extend(["", "## Promotion-Only Restrictions", ""])
        for row in promotion_rows:
            lines.append(f"- {row['source_alias']}.{row['logical_field']}: {row['promotion_impact']}; status={row['field_resolution_status']}")
    findings = [row for row in derivation_rows if row.get("severity") in {"WARN", "FAIL", "BLOCKED"}]
    if findings:
        lines.extend(["", "## Policy Derivation Findings", ""])
        for row in findings:
            lines.append(f"- {row['source_alias']}.{row['policy_check']}: {row['derivation_status']} - {row['finding']}")
    lines.extend(["", "## Next Action", ""])
    if summary.get("bounded_quality_lineage_validation") == "FAILED":
        lines.append("Resolve failed bounded quality/lineage checks, then rerun this gate with the same bounded scope.")
    elif summary.get("core_four_builder_execution_readiness") == "OPEN_FOR_EXPERIMENTAL_BUILDER_VALIDATION_DESIGN":
        lines.append("Open experimental builder validation execution for Trading Activity, Price Movement, Price Location / Structure and Volatility / Range State only. Do not open Market State Integration.")
    else:
        lines.append("Resolve core-four builder execution blockers before opening experimental builder validation execution.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bounded_grain_findings(path: Path, *, run_id: str, summary: dict[str, Any], grain_rows: list[dict[str, Any]], duplicate_rows: list[dict[str, Any]], null_key_rows: list[dict[str, Any]], hidden_rows: list[dict[str, Any]], raw_quote_rows: list[dict[str, Any]]) -> None:
    lines = [
        f"# Bounded Grain Findings - {run_id}", "",
        f"script_version: `{SCRIPT_VERSION}`",
        f"overall_status: `{summary['overall_status']}`", "",
        "## Gate Status", "",
        f"bounded_grain_validation = {summary.get('bounded_grain_validation')}",
        f"bounded_grain_data_read = {summary.get('bounded_grain_data_read')}",
        f"grain_validation = {summary.get('grain_validation')}",
        f"builder_validation_execution = {summary.get('builder_validation_execution')}",
        f"market_state_integration = {summary.get('market_state_integration')}", "",
        "## Limits", "",
        f"sources_sampled = {summary.get('bounded_grain_sources_sampled')}",
        f"files_sampled = {summary.get('bounded_grain_files_sampled')}",
        f"rows_read = {summary.get('bounded_grain_rows_read')}",
        f"maximum_rows_authorized = {summary.get('bounded_grain_maximum_rows_authorized')}",
        f"rows_limit_respected = {summary.get('bounded_grain_limits_respected')}", "",
        "## Grain Metrics", "",
        f"null_key_rows = {summary.get('null_key_rows')}",
        f"duplicate_key_groups = {summary.get('duplicate_key_groups')}",
        f"duplicate_key_rows = {summary.get('duplicate_key_rows')}",
        f"identical_duplicate_groups = {summary.get('identical_duplicate_groups')}",
        f"conflicting_duplicate_groups = {summary.get('conflicting_duplicate_groups')}",
        f"physical_key_unique_sources = {summary.get('physical_key_unique_sources')}",
        f"physical_key_non_unique_sources = {summary.get('physical_key_non_unique_sources')}",
        f"canonical_key_unique_sources = {summary.get('canonical_key_unique_sources')}",
        f"canonical_key_non_unique_sources = {summary.get('canonical_key_non_unique_sources')}", "",
        "## Source Status", "",
    ]
    for row in grain_rows:
        lines.append(f"- {row['source_alias']}: {row['grain_validation_status']} - {row['finding']}")
    warnings = [row for row in duplicate_rows + null_key_rows + hidden_rows + raw_quote_rows if row.get("severity") in {"WARN", "FAIL"}]
    if warnings:
        lines.extend(["", "## Findings", ""])
        grouped: dict[tuple[str, str, str, str], int] = {}
        for row in warnings:
            alias = str(row.get("source_alias", "unknown"))
            finding = str(row.get("finding", ""))
            severity = str(row.get("severity", ""))
            status = str(row.get("duplicate_classification") or row.get("status") or row.get("classification") or "finding")
            key = (alias, finding, status, severity)
            grouped[key] = grouped.get(key, 0) + 1
        for (alias, finding, status, severity), count in sorted(grouped.items())[:80]:
            suffix = f"; occurrences={count}" if count > 1 else ""
            lines.append(f"- {alias}: {finding} (status={status}; severity={severity}{suffix})")
    lines.extend([
        "", "## Interpretation", "",
        "This run validates only bounded candidate grain evidence. It does not claim full-history uniqueness, feature correctness, builder correctness, State readiness, or operational authority.",
        "", "## Next Action", "",
    ])
    if summary.get("bounded_grain_validation") == "FAILED":
        lines.append("Resolve failed candidate grain conflicts, then rerun bounded grain validation with the same authority boundaries.")
    elif summary.get("bounded_grain_validation") == "BLOCKED":
        lines.append("Resolve missing or unparsable key components, then rerun bounded grain validation.")
    else:
        lines.append("Open bounded quality and lineage validation as a separate gate. Do not execute feature builders or materialize State from this artifact.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_bounded_sample_findings(
    path: Path,
    *,
    run_id: str,
    summary: dict[str, Any],
    identity_rows: list[dict[str, Any]],
    timestamp_rows: list[dict[str, Any]],
    cutoff_rows: list[dict[str, Any]],
    daily_rows: list[dict[str, Any]],
) -> None:
    lines = [
        f"# Bounded Sample Findings - {run_id}", "",
        f"script_version: `{SCRIPT_VERSION}`",
        f"overall_status: `{summary['overall_status']}`", "",
        "## Gate Status", "",
        f"bounded_sample_validation = {summary.get('bounded_sample_validation')}",
        f"bounded_identity_validation = {summary.get('bounded_identity_validation')}",
        f"bounded_temporal_parse_validation = {summary.get('bounded_temporal_parse_validation')}",
        f"bounded_cutoff_legality = {summary.get('bounded_cutoff_legality')}",
        f"daily_availability_policy_execution = {summary.get('daily_availability_policy_execution')}",
        f"grain_validation = {summary.get('grain_validation')}",
        f"builder_validation_execution = {summary.get('builder_validation_execution')}",
        f"market_state_integration = {summary.get('market_state_integration')}", "",
        "## Limits", "",
        f"sources_sampled = {summary.get('bounded_sample_sources_sampled')}",
        f"files_sampled = {summary.get('bounded_sample_files_sampled')}",
        f"rows_read = {summary.get('bounded_sample_rows_read')}",
        f"maximum_rows_authorized = {summary.get('bounded_sample_maximum_rows_authorized')}",
        f"rows_limit_respected = {summary.get('bounded_sample_limits_respected')}", "",
        "## Interpretation", "",
    ]
    if summary.get("bounded_sample_validation") == "FAILED":
        lines.append("The bounded identity and temporal gate found execution-critical sample failures. Do not open grain validation.")
    else:
        lines.append("The bounded row-read gate executed within scope. It validates only bounded identity evidence, timestamp parsing, cutoff mechanics, and the conservative daily availability policy.")
        lines.append("It does not validate grain, full temporal legality, quality semantics, feature formulas, Builder Validation execution, or Market State Integration.")
    findings = [row for row in identity_rows + timestamp_rows + cutoff_rows + daily_rows if row.get("severity") in {"WARN", "FAIL"}]
    if findings:
        grouped: dict[tuple[str, str, str, str], int] = {}
        for row in findings:
            alias = str(row.get("source_alias", "unknown"))
            status = str(row.get("identity_resolution_status") or row.get("timestamp_parse_status") or row.get("cutoff_status") or row.get("daily_availability_status"))
            severity = str(row.get("severity"))
            finding = str(row.get("finding"))
            key = (alias, finding, status, severity)
            grouped[key] = grouped.get(key, 0) + 1
        lines.extend(["", "## Findings", ""])
        for (alias, finding, status, severity), count in sorted(grouped.items())[:80]:
            suffix = f"; occurrences={count}" if count > 1 else ""
            lines.append(f"- {alias}: {finding} (status={status}; severity={severity}{suffix})")
    lines.extend(["", "## Next Action", ""])
    if summary.get("bounded_sample_validation") == "FAILED":
        lines.append("Resolve bounded identity or temporal parse failures, then rerun this gate with the same bounded scope.")
    else:
        lines.append("Open bounded grain validation as a separate gate. Do not execute feature builders or materialize State from this artifact.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def iso_utc(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def float_or_none(value: Any) -> float | None:
    numeric = numeric_probe_value(value)
    if numeric is None:
        return None
    return numeric


def session_time_utc(session_date: date, time_text: str) -> datetime:
    parts = [int(part) for part in str(time_text).split(":")]
    while len(parts) < 3:
        parts.append(0)
    return datetime.combine(session_date, time(parts[0], parts[1], parts[2]), tzinfo=timezone.utc)


def normalize_ticker(value: Any) -> str:
    return "" if is_missing_value(value) else str(value).strip().upper()


def prepare_core_daily_rows(rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, date], dict[str, Any]], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    daily_by_key: dict[tuple[str, date], dict[str, Any]] = {}
    daily_by_ticker: dict[str, list[dict[str, Any]]] = {}
    findings: list[dict[str, Any]] = []
    duplicate_tracker: dict[tuple[str, date], list[dict[str, Any]]] = {}
    for sample_row in rows:
        values = sample_row.get("values", {})
        ticker = normalize_ticker(values.get("ticker"))
        session_date = parse_session_date_value(values.get("session_date"))
        if not ticker or session_date is None:
            findings.append({"source_alias": "004_master_daily_table", "finding_type": "missing_daily_key", "severity": "FAIL", "finding": "daily row missing ticker or session_date", "evidence": compact_json({"file_path": sample_row.get("file_path"), "row_ordinal_in_file": sample_row.get("row_ordinal_in_file")})})
            continue
        prepared = {
            "source_alias": "004_master_daily_table",
            "file_path": sample_row.get("file_path"),
            "row_ordinal_in_file": sample_row.get("row_ordinal_in_file"),
            "ticker": ticker,
            "instrument_id": json_safe_value(values.get("instrument_id")),
            "session_date": session_date,
            "open": float_or_none(values.get("open")),
            "prior_close": float_or_none(values.get("prior_close")),
            "volume": float_or_none(values.get("volume")),
        }
        duplicate_tracker.setdefault((ticker, session_date), []).append(prepared)
    for key, docs in sorted(duplicate_tracker.items()):
        signatures = {compact_json({"open": row["open"], "prior_close": row["prior_close"], "volume": row["volume"], "instrument_id": row["instrument_id"]}) for row in docs}
        if len(docs) > 1 and len(signatures) > 1:
            findings.append({"source_alias": "004_master_daily_table", "finding_type": "conflicting_daily_duplicate", "severity": "FAIL", "finding": "multiple 004 rows conflict for ticker/session_date after selected price_view", "evidence": compact_json({"ticker": key[0], "session_date": key[1].isoformat(), "rows": len(docs)})})
        elif len(docs) > 1:
            findings.append({"source_alias": "004_master_daily_table", "finding_type": "identical_daily_duplicate", "severity": "WARN", "finding": "multiple identical 004 rows collapsed deterministically", "evidence": compact_json({"ticker": key[0], "session_date": key[1].isoformat(), "rows": len(docs)})})
        selected = sorted(docs, key=lambda row: (str(row.get("file_path")), int(row.get("row_ordinal_in_file") or 0)))[0]
        daily_by_key[key] = selected
        daily_by_ticker.setdefault(key[0], []).append(selected)
    for ticker in daily_by_ticker:
        daily_by_ticker[ticker] = sorted(daily_by_ticker[ticker], key=lambda row: row["session_date"])
    return daily_by_key, daily_by_ticker, findings


def prepare_core_intraday_rows(rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, date], list[dict[str, Any]]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    findings: list[dict[str, Any]] = []
    for sample_row in rows:
        values = sample_row.get("values", {})
        ticker = normalize_ticker(values.get("ticker"))
        session_date = parse_session_date_value(values.get("session_date"))
        bar_end, parse_message, _, _ = parse_timestamp_value(values.get("ts_utc"))
        if not ticker or session_date is None or bar_end is None:
            findings.append({"source_alias": "014_master_intraday_bar_table_candidate", "finding_type": "missing_intraday_key", "severity": "FAIL", "finding": f"014 row missing ticker/session_date/ts_utc: {parse_message}", "evidence": compact_json({"file_path": sample_row.get("file_path"), "row_ordinal_in_file": sample_row.get("row_ordinal_in_file")})})
            continue
        prepared = {
            "source_alias": "014_master_intraday_bar_table_candidate",
            "file_path": sample_row.get("file_path"),
            "row_ordinal_in_file": sample_row.get("row_ordinal_in_file"),
            "ticker": ticker,
            "instrument_id": json_safe_value(values.get("instrument_id")),
            "session_date": session_date,
            "bar_end_utc": bar_end,
            "open": float_or_none(values.get("open")),
            "high": float_or_none(values.get("high")),
            "low": float_or_none(values.get("low")),
            "close": float_or_none(values.get("close")),
            "volume": float_or_none(values.get("volume")),
            "raw_values": {key: json_safe_value(value) for key, value in values.items()},
        }
        key = compact_json([("ticker", ticker), ("bar_end_utc", iso_utc(bar_end))])
        grouped.setdefault(key, []).append(prepared)
    conflict_by_key: dict[str, dict[str, Any]] = {}
    bars_by_session: dict[tuple[str, date], list[dict[str, Any]]] = {}
    for key, docs in sorted(grouped.items()):
        signatures = {compact_json({field: row.get(field) for field in ("open", "high", "low", "close", "volume")}) for row in docs}
        first = sorted(docs, key=lambda row: (str(row.get("file_path")), int(row.get("row_ordinal_in_file") or 0)))[0]
        duplicate_status = "unique"
        if len(docs) > 1 and len(signatures) > 1:
            duplicate_status = "conflicting_duplicate_rows"
            conflict_by_key[key] = {"row_count": len(docs), "distinct_state_count": len(signatures)}
            findings.append({"source_alias": "014_master_intraday_bar_table_candidate", "finding_type": "conflicting_intraday_duplicate", "severity": "FAIL", "finding": "014 has conflicting duplicate bars for ticker/bar_end; request must block if selected", "evidence": compact_json({"key": key, "rows": len(docs), "distinct_state_count": len(signatures)})})
        elif len(docs) > 1:
            duplicate_status = "identical_duplicate_rows_collapsed"
            findings.append({"source_alias": "014_master_intraday_bar_table_candidate", "finding_type": "identical_intraday_duplicate", "severity": "WARN", "finding": "014 identical duplicate bars collapsed deterministically under policy", "evidence": compact_json({"key": key, "rows": len(docs)})})
        collapsed = {**first, "duplicate_status": duplicate_status, "duplicate_group_key": key, "duplicate_group_row_count": len(docs), "duplicate_group_distinct_state_count": len(signatures)}
        bars_by_session.setdefault((collapsed["ticker"], collapsed["session_date"]), []).append(collapsed)
    for session_key in bars_by_session:
        bars_by_session[session_key] = sorted(bars_by_session[session_key], key=lambda row: (row["bar_end_utc"], str(row.get("file_path")), int(row.get("row_ordinal_in_file") or 0)))
    return bars_by_session, conflict_by_key, findings


def prior_daily_rows(daily_by_ticker: dict[str, list[dict[str, Any]]], ticker: str, session_date: date, count: int = 20) -> list[dict[str, Any]]:
    history = [row for row in daily_by_ticker.get(ticker, []) if row["session_date"] < session_date and row.get("volume") is not None]
    return history[-count:]


def generate_core_four_requests(scope_doc: dict[str, Any], daily_by_key: dict[tuple[str, date], dict[str, Any]], daily_by_ticker: dict[str, list[dict[str, Any]]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    limits = scope_doc["global_limits"]
    request_generation = scope_doc.get("request_generation", {})
    decision_cases = [str(case) for case in request_generation.get("decision_cases", [])]
    max_instruments = int(limits["maximum_instruments"])
    max_sessions_per_instrument = int(limits["maximum_sessions_per_instrument"])
    max_decision_timestamps = int(limits["maximum_decision_timestamps_per_session"])
    max_resolution_requests = int(limits["maximum_resolution_requests"])
    object_ids = sorted(scope_doc["objects"])
    selected_sessions: dict[str, list[tuple[date, list[dict[str, Any]]]]] = {}
    for (ticker, session_date), bars in sorted(bars_by_session.items(), key=lambda item: (item[0][0], item[0][1])):
        if (ticker, session_date) not in daily_by_key:
            continue
        if len(prior_daily_rows(daily_by_ticker, ticker, session_date, 20)) < 20:
            continue
        selected_sessions.setdefault(ticker, [])
        if len(selected_sessions[ticker]) < max_sessions_per_instrument:
            selected_sessions[ticker].append((session_date, bars))
        if len(selected_sessions) >= max_instruments and all(len(sessions) >= max_sessions_per_instrument for sessions in selected_sessions.values()):
            break
    selected_tickers = sorted(selected_sessions)[:max_instruments]
    requests: list[dict[str, Any]] = []
    context_index = 0
    for ticker in selected_tickers:
        for session_date, bars in selected_sessions[ticker][:max_sessions_per_instrument]:
            if not bars:
                continue
            first_bar = bars[0]["bar_end_utc"]
            last_bar = bars[-1]["bar_end_utc"]
            case_timestamps: list[tuple[str, datetime]] = []
            for case in decision_cases[:max_decision_timestamps]:
                if case == "before_first_bar":
                    case_timestamps.append((case, first_bar - timedelta(seconds=1)))
                elif case == "exact_first_bar":
                    case_timestamps.append((case, first_bar))
                elif case == "between_first_two_bars" and len(bars) > 1:
                    second_bar = bars[1]["bar_end_utc"]
                    case_timestamps.append((case, first_bar + (second_bar - first_bar) / 2))
                elif case == "mid_session":
                    case_timestamps.append((case, bars[len(bars) // 2]["bar_end_utc"]))
                elif case == "after_last_sampled_bar":
                    case_timestamps.append((case, last_bar + timedelta(seconds=1)))
            for case, decision_timestamp in case_timestamps:
                context_index += 1
                context_id = f"core_four_context_{context_index:04d}"
                daily_row = daily_by_key[(ticker, session_date)]
                for object_id in object_ids:
                    if len(requests) >= max_resolution_requests:
                        return requests
                    requests.append({
                        "request_id": f"core_four_req_{len(requests) + 1:04d}",
                        "context_id": context_id,
                        "object_id": object_id,
                        "ticker": ticker,
                        "instrument_id": daily_row.get("instrument_id"),
                        "session_date": session_date,
                        "decision_case": case,
                        "decision_timestamp_utc": decision_timestamp,
                    })
    return requests


def value_field_for_capability(object_doc: dict[str, Any], capability_id: str) -> str:
    suffix = capability_id.replace("daily__", "daily_").replace("intraday__", "intraday_")
    return f"{object_doc.get('output_namespace')}{suffix}"


def selected_input_context(request: dict[str, Any], scope_doc: dict[str, Any], daily_by_key: dict[tuple[str, date], dict[str, Any]], daily_by_ticker: dict[str, list[dict[str, Any]]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]]) -> dict[str, Any]:
    ticker = str(request["ticker"])
    session_date = request["session_date"]
    decision_timestamp = request["decision_timestamp_utc"]
    request_generation = scope_doc.get("request_generation", {})
    session_open = session_time_utc(session_date, str(request_generation.get("session_open_time_utc", "13:30:00")))
    session_close = session_time_utc(session_date, str(request_generation.get("session_close_time_utc", "20:00:00")))
    bars = bars_by_session.get((ticker, session_date), [])
    closed_bars = [bar for bar in bars if bar["bar_end_utc"] <= decision_timestamp]
    selected_bar = closed_bars[-1] if closed_bars else None
    daily_row = daily_by_key.get((ticker, session_date))
    history_20 = prior_daily_rows(daily_by_ticker, ticker, session_date, 20)
    return {
        "ticker": ticker,
        "session_date": session_date,
        "decision_timestamp_utc": decision_timestamp,
        "session_open_utc": session_open,
        "session_close_utc": session_close,
        "daily_row": daily_row,
        "history_20": history_20,
        "bars": bars,
        "closed_bars": closed_bars,
        "selected_bar": selected_bar,
        "decision_after_session_open": decision_timestamp >= session_open,
    }


def calculate_core_capability(capability_id: str, context: dict[str, Any]) -> tuple[str, Any, str, list[str]]:
    daily_row = context.get("daily_row")
    selected_bar = context.get("selected_bar")
    closed_bars = context.get("closed_bars", [])
    history_20 = context.get("history_20", [])
    restrictions: list[str] = []
    if daily_row is None:
        return "BLOCKED_INPUT_UNAVAILABLE", None, "matched 004 daily row unavailable", restrictions
    if selected_bar is not None and selected_bar.get("duplicate_status") == "conflicting_duplicate_rows":
        return "BLOCKED_CONFLICTING_SOURCE_ROWS", None, "selected 014 bar has conflicting duplicate source rows", restrictions
    try:
        prior_close = daily_row.get("prior_close")
        session_open_price = daily_row.get("open")
        if capability_id == "daily__volume_20d_avg":
            values = [row.get("volume") for row in history_20 if row.get("volume") is not None]
            if len(values) < 20:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "fewer than 20 prior daily volume rows available", restrictions
            return "PASS", sum(values) / len(values), "prior 20 daily volume mean computed", restrictions
        if capability_id == "daily__rvol_20d":
            values = [row.get("volume") for row in history_20 if row.get("volume") is not None]
            if len(values) < 20:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "fewer than 20 prior daily volume rows available", restrictions
            baseline = sum(values) / len(values)
            if baseline <= 0:
                return "FAILED_FORMULA", None, "volume_20d_avg denominator is not positive", restrictions
            session_volume_to_time = sum(float(bar.get("volume") or 0.0) for bar in closed_bars if bar.get("volume") is not None)
            restrictions.append("daily_rvol_20d_uses_intraday_volume_to_time_proxy; final same-session daily volume is not consumed")
            return "PASS_WITH_RESTRICTIONS", session_volume_to_time / baseline, "session volume-to-time over prior 20 daily volume mean computed", restrictions
        if capability_id == "intraday__bar_volume":
            if selected_bar is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed 014 bar exists at decision timestamp", restrictions
            return "PASS", selected_bar.get("volume"), "selected closed bar volume resolved", restrictions
        if capability_id == "intraday__session_volume_to_time":
            if not closed_bars:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed 014 bars exist at decision timestamp", restrictions
            return "PASS", sum(float(bar.get("volume") or 0.0) for bar in closed_bars if bar.get("volume") is not None), "closed-bar volume sum resolved", restrictions
        if capability_id == "daily__prior_close":
            if prior_close is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "prior_close unavailable in 004 row", restrictions
            return "PASS", prior_close, "prior_close resolved from 004", restrictions
        if capability_id in {"daily__open_price", "daily__gap_pct"}:
            if not context.get("decision_after_session_open"):
                return "BLOCKED_INPUT_UNAVAILABLE", None, "daily open/gap not consumed before configured session open", restrictions
            if session_open_price is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "open unavailable in 004 row", restrictions
            if capability_id == "daily__open_price":
                return "PASS", session_open_price, "daily open resolved after session open", restrictions
            if prior_close is None or prior_close <= 0:
                return "FAILED_FORMULA", None, "prior_close denominator unavailable or non-positive for gap", restrictions
            return "PASS", session_open_price / prior_close - 1.0, "gap percent computed from open and prior_close", restrictions
        if capability_id == "intraday__bar_close_price":
            if selected_bar is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed 014 bar exists at decision timestamp", restrictions
            return "PASS", selected_bar.get("close"), "selected closed bar close resolved", restrictions
        if capability_id in {"intraday__return_vs_prior_close_ratio", "intraday__return_vs_prior_close_ratio_as_location"}:
            if selected_bar is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed 014 bar exists at decision timestamp", restrictions
            if prior_close is None or prior_close <= 0:
                return "FAILED_FORMULA", None, "prior_close denominator unavailable or non-positive", restrictions
            close = selected_bar.get("close")
            if close is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "selected bar close unavailable", restrictions
            return "PASS", close / prior_close - 1.0, "closed-bar return vs prior_close computed", restrictions
        if capability_id in {"intraday__return_vs_session_open_ratio", "intraday__return_vs_session_open_ratio_as_location"}:
            if not context.get("decision_after_session_open"):
                return "BLOCKED_INPUT_UNAVAILABLE", None, "session-open return not consumed before configured session open", restrictions
            if selected_bar is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed 014 bar exists at decision timestamp", restrictions
            if session_open_price is None or session_open_price <= 0:
                return "FAILED_FORMULA", None, "session open denominator unavailable or non-positive", restrictions
            close = selected_bar.get("close")
            if close is None:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "selected bar close unavailable", restrictions
            return "PASS", close / session_open_price - 1.0, "closed-bar return vs session open computed", restrictions
        if capability_id == "intraday__high_so_far":
            highs = [bar.get("high") for bar in closed_bars if bar.get("high") is not None]
            if not highs:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed high values available", restrictions
            return "PASS", max(highs), "high so far over closed bars computed", restrictions
        if capability_id == "intraday__low_so_far":
            lows = [bar.get("low") for bar in closed_bars if bar.get("low") is not None]
            if not lows:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "no closed low values available", restrictions
            return "PASS", min(lows), "low so far over closed bars computed", restrictions
        if capability_id == "intraday__range_so_far_ratio":
            highs = [bar.get("high") for bar in closed_bars if bar.get("high") is not None]
            lows = [bar.get("low") for bar in closed_bars if bar.get("low") is not None]
            if not highs or not lows:
                return "BLOCKED_INPUT_UNAVAILABLE", None, "closed high/low values unavailable", restrictions
            high_so_far = max(highs)
            low_so_far = min(lows)
            if low_so_far <= 0:
                return "FAILED_FORMULA", None, "low_so_far denominator is not positive", restrictions
            return "PASS", high_so_far / low_so_far - 1.0, "range so far ratio computed", restrictions
    except Exception as exc:
        return "FAILED_FORMULA", None, f"formula execution raised {type(exc).__name__}: {exc}", restrictions
    return "FAILED_FORMULA", None, f"unsupported capability_id={capability_id}", restrictions


def core_source_evidence(context: dict[str, Any]) -> dict[str, Any]:
    daily_row = context.get("daily_row") or {}
    selected_bar = context.get("selected_bar") or {}
    return {
        "004_daily_row": {
            "file_path": daily_row.get("file_path"),
            "row_ordinal_in_file": daily_row.get("row_ordinal_in_file"),
            "session_date": daily_row.get("session_date").isoformat() if daily_row.get("session_date") else None,
            "price_view": "split_normalized",
        } if daily_row else None,
        "014_selected_closed_bar": {
            "file_path": selected_bar.get("file_path"),
            "row_ordinal_in_file": selected_bar.get("row_ordinal_in_file"),
            "bar_end_utc": iso_utc(selected_bar.get("bar_end_utc")),
            "duplicate_status": selected_bar.get("duplicate_status"),
            "duplicate_group_row_count": selected_bar.get("duplicate_group_row_count"),
        } if selected_bar else None,
        "014_closed_bar_count": len(context.get("closed_bars", [])),
    }


def core_cutoff_evidence(context: dict[str, Any]) -> dict[str, Any]:
    selected_bar = context.get("selected_bar")
    decision_timestamp = context.get("decision_timestamp_utc")
    future_bar_leak = bool(selected_bar and selected_bar.get("bar_end_utc") and selected_bar["bar_end_utc"] > decision_timestamp)
    return {
        "decision_timestamp_utc": iso_utc(decision_timestamp),
        "session_open_utc": iso_utc(context.get("session_open_utc")),
        "decision_after_session_open": bool(context.get("decision_after_session_open")),
        "selected_bar_end_utc": iso_utc(selected_bar.get("bar_end_utc")) if selected_bar else None,
        "bar_end_lte_decision_timestamp": bool(selected_bar and selected_bar.get("bar_end_utc") <= decision_timestamp) if selected_bar else None,
        "future_bar_leak": future_bar_leak,
        "daily_open_fields_eligible": bool(context.get("decision_after_session_open")),
    }


def resolution_fingerprint(payload: dict[str, Any]) -> str:
    return hashlib.sha256(compact_json(payload).encode("utf-8")).hexdigest()


def execute_core_four_resolution_pass(scope_doc: dict[str, Any], requests: list[dict[str, Any]], daily_by_key: dict[tuple[str, date], dict[str, Any]], daily_by_ticker: dict[str, list[dict[str, Any]]], bars_by_session: dict[tuple[str, date], list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    request_rows: list[dict[str, Any]] = []
    capability_rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    cutoff_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    formula_rows: list[dict[str, Any]] = []
    output_contract_rows: list[dict[str, Any]] = []
    restriction_rows: list[dict[str, Any]] = []
    resolution_records: list[dict[str, Any]] = []
    formula_rules = scope_doc.get("formula_rules", {})
    objects = scope_doc.get("objects", {})
    for request in requests:
        object_doc = objects[request["object_id"]]
        context = selected_input_context(request, scope_doc, daily_by_key, daily_by_ticker, bars_by_session)
        source_evidence = core_source_evidence(context)
        cutoff_evidence = core_cutoff_evidence(context)
        selected_bar = context.get("selected_bar")
        daily_row = context.get("daily_row")
        if daily_row:
            selected_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "004_master_daily_table", "input_role": "matched_daily_row", "source_file_path": daily_row.get("file_path"), "source_row_ordinal_in_file": daily_row.get("row_ordinal_in_file"), "selected_source_timestamp_utc": "", "session_date": request["session_date"].isoformat(), "source_row_count": 1, "selection_rule": "ticker + session_date after selected price_view", "selection_status": "PASS", "evidence": compact_json({"ticker": request["ticker"], "price_view": "split_normalized"})})
        selected_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "004_master_daily_table", "input_role": "prior_20_daily_history", "source_file_path": "", "source_row_ordinal_in_file": "", "selected_source_timestamp_utc": "", "session_date": request["session_date"].isoformat(), "source_row_count": len(context.get("history_20", [])), "selection_rule": "last 20 sessions before current session", "selection_status": "PASS" if len(context.get("history_20", [])) >= 20 else "BLOCKED_INPUT_UNAVAILABLE", "evidence": compact_json({"ticker": request["ticker"]})})
        if selected_bar:
            selected_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "014_master_intraday_bar_table_candidate", "input_role": "selected_closed_bar", "source_file_path": selected_bar.get("file_path"), "source_row_ordinal_in_file": selected_bar.get("row_ordinal_in_file"), "selected_source_timestamp_utc": iso_utc(selected_bar.get("bar_end_utc")), "session_date": request["session_date"].isoformat(), "source_row_count": 1, "selection_rule": "max(bar_end_utc) <= decision_timestamp", "selection_status": "PASS" if selected_bar.get("duplicate_status") != "conflicting_duplicate_rows" else "BLOCKED_CONFLICTING_SOURCE_ROWS", "evidence": compact_json({"duplicate_status": selected_bar.get("duplicate_status"), "closed_bar_count": len(context.get("closed_bars", []))})})
            duplicate_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "014_master_intraday_bar_table_candidate", "selected_bar_end_utc": iso_utc(selected_bar.get("bar_end_utc")), "duplicate_group_key": selected_bar.get("duplicate_group_key"), "duplicate_group_row_count": selected_bar.get("duplicate_group_row_count"), "duplicate_group_distinct_state_count": selected_bar.get("duplicate_group_distinct_state_count"), "duplicate_handling_status": selected_bar.get("duplicate_status"), "severity": "FAIL" if selected_bar.get("duplicate_status") == "conflicting_duplicate_rows" else "WARN" if selected_bar.get("duplicate_status") == "identical_duplicate_rows_collapsed" else "INFO", "finding": "conflicting duplicate selected; request blocked" if selected_bar.get("duplicate_status") == "conflicting_duplicate_rows" else "identical duplicate collapsed deterministically" if selected_bar.get("duplicate_status") == "identical_duplicate_rows_collapsed" else "selected bar key unique in sampled data"})
        else:
            selected_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "014_master_intraday_bar_table_candidate", "input_role": "selected_closed_bar", "source_file_path": "", "source_row_ordinal_in_file": "", "selected_source_timestamp_utc": "", "session_date": request["session_date"].isoformat(), "source_row_count": 0, "selection_rule": "max(bar_end_utc) <= decision_timestamp", "selection_status": "BLOCKED_INPUT_UNAVAILABLE", "evidence": "no closed bars at decision timestamp"})
        cutoff_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "014_master_intraday_bar_table_candidate", "input_role": "closed_bar_cutoff", "source_timestamp_utc": cutoff_evidence.get("selected_bar_end_utc") or "", "availability_timestamp_utc": cutoff_evidence.get("selected_bar_end_utc") or "", "decision_timestamp_utc": iso_utc(request["decision_timestamp_utc"]), "eligible_at_decision": bool(selected_bar and selected_bar.get("bar_end_utc") <= request["decision_timestamp_utc"]), "future_leak": bool(cutoff_evidence.get("future_bar_leak")), "cutoff_status": "FAILED" if cutoff_evidence.get("future_bar_leak") else "PASS" if selected_bar else "BLOCKED_INPUT_UNAVAILABLE", "finding": "bar_end <= decision_timestamp" if selected_bar and not cutoff_evidence.get("future_bar_leak") else "no closed bar eligible at decision timestamp" if not selected_bar else "future bar leak detected"})
        cutoff_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "source_alias": "004_master_daily_table", "input_role": "daily_open_availability", "source_timestamp_utc": request["session_date"].isoformat(), "availability_timestamp_utc": iso_utc(context.get("session_open_utc")), "decision_timestamp_utc": iso_utc(request["decision_timestamp_utc"]), "eligible_at_decision": bool(context.get("decision_after_session_open")), "future_leak": False, "cutoff_status": "PASS" if context.get("decision_after_session_open") else "BLOCKED_INPUT_UNAVAILABLE", "finding": "daily open/gap fields eligible after configured session open" if context.get("decision_after_session_open") else "daily open/gap fields withheld before configured session open"})
        values: dict[str, Any] = {}
        capability_statuses: list[str] = []
        restrictions: list[str] = []
        for capability_id in object_doc.get("required_capabilities", []):
            status, value, finding, cap_restrictions = calculate_core_capability(str(capability_id), context)
            capability_statuses.append(status)
            output_field = value_field_for_capability(object_doc, str(capability_id))
            if status in {"PASS", "PASS_WITH_RESTRICTIONS"}:
                values[output_field] = json_safe_value(value)
            restrictions.extend(cap_restrictions)
            rule = formula_rules.get(str(capability_id), {})
            cap_row = {"request_id": request["request_id"], "object_id": request["object_id"], "capability_id": str(capability_id), "source_alias": str(rule.get("source_alias", "")), "input_fields": format_list(rule.get("inputs", [])), "formula_id": str(rule.get("formula_id", "")), "resolution_rule": str(rule.get("rule", "")), "resolution_status": status, "restriction": format_list(cap_restrictions), "finding": finding}
            capability_rows.append(cap_row)
            formula_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "capability_id": str(capability_id), "formula_id": cap_row["formula_id"], "input_fields": cap_row["input_fields"], "formula_status": status, "output_field": output_field, "output_value": json_safe_value(value), "severity": "FAIL" if status == "FAILED_FORMULA" else "BLOCKED" if status == "BLOCKED_CONFLICTING_SOURCE_ROWS" else "WARN" if status in {"BLOCKED_INPUT_UNAVAILABLE", "PASS_WITH_RESTRICTIONS"} else "INFO", "finding": finding, "restriction": format_list(cap_restrictions)})
            for restriction in cap_restrictions:
                restriction_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "restriction_type": "capability_restriction", "restriction": restriction, "severity": "WARN", "finding": finding})
        if any(status == "FAILED_FORMULA" for status in capability_statuses):
            resolution_status = "FAILED_FORMULA"
        elif any(status == "BLOCKED_CONFLICTING_SOURCE_ROWS" for status in capability_statuses):
            resolution_status = "BLOCKED_CONFLICTING_SOURCE_ROWS"
        elif any(status == "BLOCKED_INPUT_UNAVAILABLE" for status in capability_statuses):
            resolution_status = "BLOCKED_INPUT_UNAVAILABLE"
        elif any(status == "PASS_WITH_RESTRICTIONS" for status in capability_statuses) or restrictions:
            resolution_status = "PASS_WITH_RESTRICTIONS"
        else:
            resolution_status = "PASS"
        missing_fields = [] if resolution_status.startswith("BLOCKED") else [value_field_for_capability(object_doc, str(cap)) for cap in object_doc.get("required_capabilities", []) if value_field_for_capability(object_doc, str(cap)) not in values]
        namespace_valid = all(str(field).startswith(str(object_doc.get("output_namespace"))) for field in values)
        output_contract_status = "PASS" if not missing_fields and namespace_valid else "FAILED_OUTPUT_CONTRACT"
        if output_contract_status == "FAILED_OUTPUT_CONTRACT" and resolution_status not in {"FAILED_FORMULA", "BLOCKED_CONFLICTING_SOURCE_ROWS"}:
            resolution_status = "FAILED_OUTPUT_CONTRACT"
        output_contract_rows.append({"request_id": request["request_id"], "object_id": request["object_id"], "required_schema_fields_present": True, "output_namespace": object_doc.get("output_namespace"), "namespace_fields_valid": namespace_valid, "required_capabilities": format_list(object_doc.get("required_capabilities", [])), "value_fields_produced": format_list(sorted(values)), "missing_required_value_fields": format_list(missing_fields), "output_contract_status": output_contract_status, "severity": "FAIL" if output_contract_status == "FAILED_OUTPUT_CONTRACT" else "INFO", "finding": "resolution record satisfies experimental output contract" if output_contract_status == "PASS" else "resolved record missing required output fields or namespace"})
        quality_evidence = {"quality_lineage_gate": "CLOSED_PASS_WITH_RESTRICTIONS", "core_four_builder_execution_blockers": 0, "quote_dependent_builder_execution_blockers_remain_blocked": True}
        lineage = {"profile_id": object_doc.get("profile_id"), "source_scope_id": scope_doc.get("scope_id"), "policy_versions": {"004_price_view_selection_policy": "004_price_view_selection_policy_v0_1", "014_duplicate_intraday_bar_policy": "014_duplicate_intraday_bar_policy_v0_1"}}
        fingerprint_payload = {"request": {"object_id": request["object_id"], "instrument_id": request.get("instrument_id"), "ticker": request.get("ticker"), "decision_timestamp_utc": iso_utc(request["decision_timestamp_utc"])}, "values": values, "source_evidence": source_evidence, "cutoff_evidence": cutoff_evidence, "quality_evidence": quality_evidence, "lineage": lineage, "restrictions": restrictions, "resolution_status": resolution_status}
        fp = resolution_fingerprint(fingerprint_payload)
        record = {"record_id": f"{request['request_id']}::{request['object_id']}", "request_id": request["request_id"], "context_id": request["context_id"], "object_id": request["object_id"], "instrument_id": request.get("instrument_id"), "ticker": request.get("ticker"), "session_date": request["session_date"].isoformat(), "decision_case": request["decision_case"], "decision_timestamp_utc": iso_utc(request["decision_timestamp_utc"]), "resolution_status": resolution_status, "values": values, "source_evidence": source_evidence, "cutoff_evidence": cutoff_evidence, "quality_evidence": quality_evidence, "lineage": lineage, "restrictions": restrictions, "resolution_fingerprint": fp}
        resolution_records.append(record)
        request_rows.append({"request_id": request["request_id"], "context_id": request["context_id"], "object_id": request["object_id"], "instrument_id": request.get("instrument_id"), "ticker": request.get("ticker"), "session_date": request["session_date"].isoformat(), "decision_case": request["decision_case"], "decision_timestamp_utc": iso_utc(request["decision_timestamp_utc"]), "resolution_status": resolution_status, "resolution_fingerprint": fp, "capabilities_requested": len(object_doc.get("required_capabilities", [])), "capabilities_resolved": sum(1 for status in capability_statuses if status in {"PASS", "PASS_WITH_RESTRICTIONS"}), "restrictions_count": len(restrictions)})
    return request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records


def aggregate_core_preparation_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for finding in findings:
        key = (str(finding.get("source_alias", "")), str(finding.get("finding_type", "")), str(finding.get("severity", "")), str(finding.get("finding", "")))
        row = grouped.setdefault(key, {
            "source_alias": key[0],
            "finding_type": key[1],
            "severity": key[2],
            "finding": key[3],
            "count": 0,
            "evidence_examples": [],
        })
        row["count"] += 1
        if len(row["evidence_examples"]) < 5:
            row["evidence_examples"].append(finding.get("evidence", ""))
    output: list[dict[str, Any]] = []
    for row in grouped.values():
        output.append({**row, "evidence_examples": row["evidence_examples"]})
    return sorted(output, key=lambda row: (row["source_alias"], row["finding_type"], row["severity"]))


def core_four_summary_from_reports(scope_doc: dict[str, Any], bounded_manifest: dict[str, Any], read_limit_rows: list[dict[str, Any]], request_rows: list[dict[str, Any]], formula_rows: list[dict[str, Any]], output_contract_rows: list[dict[str, Any]], determinism_rows: list[dict[str, Any]], restriction_rows: list[dict[str, Any]], duplicate_rows: list[dict[str, Any]], cutoff_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_rows_read = sum(int(row["rows_read"]) for row in read_limit_rows)
    maximum_rows_authorized = int(scope_doc["global_limits"]["maximum_total_input_rows"])
    limit_violation = total_rows_read > maximum_rows_authorized or any(str(row["limit_respected"]) != "True" for row in read_limit_rows)
    formula_failures = sum(1 for row in formula_rows if row["formula_status"] == "FAILED_FORMULA")
    conflict_blocks = sum(1 for row in request_rows if row["resolution_status"] == "BLOCKED_CONFLICTING_SOURCE_ROWS")
    input_blocks = sum(1 for row in request_rows if row["resolution_status"] == "BLOCKED_INPUT_UNAVAILABLE")
    contract_failures = sum(1 for row in output_contract_rows if row["output_contract_status"] == "FAILED_OUTPUT_CONTRACT")
    nondeterministic = sum(1 for row in determinism_rows if row["repeat_run_fingerprint_match"] is not True)
    future_leaks = sum(1 for row in cutoff_rows if row.get("future_leak") is True or str(row.get("future_leak")) == "True")
    duplicate_restrictions = sum(1 for row in duplicate_rows if row["severity"] == "WARN")
    if limit_violation or formula_failures or contract_failures or nondeterministic or future_leaks:
        validation, overall = "FAILED", "failed_core_four_builder_validation"
    elif conflict_blocks:
        validation, overall = "BLOCKED", "blocked_core_four_builder_validation"
    elif input_blocks or restriction_rows or duplicate_restrictions:
        validation, overall = "PASS_WITH_RESTRICTIONS", "passed_core_four_builder_validation_with_restrictions"
    else:
        validation, overall = "PASS", "passed_core_four_builder_validation"
    return {
        "overall_status": overall,
        "experimental_builder_validation_execution_core_four": validation,
        "core_four_builder_validation_execution": validation,
        "core_four_builder_scope": CORE_FOUR_BUILDER_SCOPE,
        "core_four_builder_scope_id": scope_doc.get("scope_id"),
        "core_four_objects_authorized": len(scope_doc.get("objects", {})),
        "core_four_sources_sampled": len(bounded_manifest.get("sources", {})),
        "core_four_files_sampled": sum(len(source_doc.get("files_sampled", [])) for source_doc in bounded_manifest.get("sources", {}).values()),
        "core_four_rows_read": total_rows_read,
        "core_four_maximum_rows_authorized": maximum_rows_authorized,
        "core_four_limits_respected": not limit_violation,
        "core_four_resolution_requests": len(request_rows),
        "core_four_formula_rows": len(formula_rows),
        "core_four_formula_failures": formula_failures,
        "core_four_blocked_input_unavailable_requests": input_blocks,
        "core_four_conflicting_source_row_blocks": conflict_blocks,
        "core_four_future_bar_leaks": future_leaks,
        "core_four_output_contract_failures": contract_failures,
        "core_four_nondeterministic_records": nondeterministic,
        "core_four_restriction_rows": len(restriction_rows),
        "core_four_duplicate_restrictions": duplicate_restrictions,
        "data_resolution": "CORE_FOUR_BUILDER_BOUNDED_EXECUTION_AUTHORIZED_BY_SCOPE",
        "data_validation": "CORE_FOUR_BUILDER_EXECUTED_WITH_LIMITS",
        "grain_validation": "CLOSED_PASS_WITH_RESTRICTIONS",
        "quality_semantics_validation": "CLOSED_PASS_WITH_RESTRICTIONS",
        "lineage_validation": "CLOSED_PASS_WITH_RESTRICTIONS",
        "builder_validation_execution": validation,
        "quote_dependent_builder_execution": "BLOCKED_PENDING_QUOTE_ORDERING_OR_ASOF",
        "market_state_integration": "NOT_OPEN",
        "state_materialization": "NOT_AUTHORIZED",
        "production_builder": "NOT_AUTHORIZED",
    }


def check_core_four_builder_validation(config: dict[str, Any], source_registry_doc: dict[str, Any], core_scope_doc: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    sampled_by_alias: dict[str, list[dict[str, Any]]] = {}
    read_limit_rows: list[dict[str, Any]] = []
    bounded_manifest: dict[str, Any] = {"scope": CORE_FOUR_BUILDER_SCOPE, "execution_class": "experimental_non_materializing", "row_read_mode": "bounded", "row_reads_authorized": True, "full_data_read_authorized": False, "formula_execution_authorized": True, "resolution_records_authorized": True, "state_materialization_authorized": False, "market_state_integration_authorized": False, "production_builder_authorized": False, "sources": {}}
    for alias, source_scope in core_scope_doc["sources"].items():
        sampled_rows, source_limit_rows, source_manifest = sample_source_rows(alias=alias, source_binding=source_registry_doc["bindings"][alias], source_scope=source_scope)
        sampled_by_alias[alias] = sampled_rows
        read_limit_rows.extend(source_limit_rows)
        bounded_manifest["sources"][alias] = source_manifest
    if sum(int(row["rows_read"]) for row in read_limit_rows) > int(core_scope_doc["global_limits"]["maximum_total_input_rows"]):
        raise ProbeError("core-four builder row read limit exceeded")
    daily_by_key, daily_by_ticker, daily_findings = prepare_core_daily_rows(sampled_by_alias.get("004_master_daily_table", []))
    bars_by_session, conflict_by_key, intraday_findings = prepare_core_intraday_rows(sampled_by_alias.get("014_master_intraday_bar_table_candidate", []))
    requests = generate_core_four_requests(core_scope_doc, daily_by_key, daily_by_ticker, bars_by_session)
    if not requests:
        raise ProbeError("core-four builder scope produced no executable resolution requests")
    first = execute_core_four_resolution_pass(core_scope_doc, requests, daily_by_key, daily_by_ticker, bars_by_session)
    second = execute_core_four_resolution_pass(core_scope_doc, requests, daily_by_key, daily_by_ticker, bars_by_session)
    request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, restriction_rows, resolution_records = first
    second_records = second[-1]
    second_by_id = {record["record_id"]: record for record in second_records}
    determinism_rows: list[dict[str, Any]] = []
    for record in resolution_records:
        second_record = second_by_id.get(record["record_id"])
        match = bool(second_record and second_record.get("resolution_fingerprint") == record.get("resolution_fingerprint"))
        determinism_rows.append({"request_id": record["request_id"], "object_id": record["object_id"], "record_id": record["record_id"], "first_resolution_fingerprint": record.get("resolution_fingerprint"), "second_resolution_fingerprint": second_record.get("resolution_fingerprint") if second_record else "", "repeat_run_fingerprint_match": match, "determinism_status": "PASS" if match else "FAILED_NON_DETERMINISTIC", "severity": "INFO" if match else "FAIL", "finding": "repeat execution produced identical fingerprint" if match else "repeat execution produced divergent fingerprint"})
    preparation_findings = aggregate_core_preparation_findings(daily_findings + intraday_findings)
    for finding in preparation_findings:
        if finding.get("severity") == "FAIL":
            restriction_rows.append({"request_id": "preparation", "object_id": "core_four", "restriction_type": str(finding.get("finding_type")), "restriction": str(finding.get("finding")), "severity": str(finding.get("severity")), "finding": compact_json({"count": finding.get("count"), "evidence_examples": finding.get("evidence_examples", [])})})
    summary = core_four_summary_from_reports(core_scope_doc, bounded_manifest, read_limit_rows, request_rows, formula_rows, output_contract_rows, determinism_rows, restriction_rows, duplicate_rows, cutoff_rows)
    bounded_manifest["requests_generated"] = len(requests)
    bounded_manifest["preparation_findings"] = preparation_findings
    bounded_manifest["conflicting_intraday_duplicate_keys"] = conflict_by_key
    return bounded_manifest, read_limit_rows, request_rows, capability_rows, selected_rows, cutoff_rows, duplicate_rows, formula_rows, output_contract_rows, determinism_rows, restriction_rows, resolution_records, summary


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, default=json_safe_value))
            handle.write("\n")


def write_core_four_builder_findings(path: Path, *, run_id: str, summary: dict[str, Any], request_rows: list[dict[str, Any]], formula_rows: list[dict[str, Any]], determinism_rows: list[dict[str, Any]], restriction_rows: list[dict[str, Any]]) -> None:
    lines = [
        f"# Core Four Builder Validation Findings - {run_id}", "",
        f"script_version: `{SCRIPT_VERSION}`",
        f"overall_status: `{summary['overall_status']}`", "",
        "## Gate Status", "",
        f"experimental_builder_validation_execution_core_four = {summary.get('experimental_builder_validation_execution_core_four')}",
        f"builder_validation_execution = {summary.get('builder_validation_execution')}",
        f"quote_dependent_builder_execution = {summary.get('quote_dependent_builder_execution')}",
        f"market_state_integration = {summary.get('market_state_integration')}", "",
        "## Limits", "",
        f"objects_authorized = {summary.get('core_four_objects_authorized')}",
        f"sources_sampled = {summary.get('core_four_sources_sampled')}",
        f"files_sampled = {summary.get('core_four_files_sampled')}",
        f"rows_read = {summary.get('core_four_rows_read')}",
        f"maximum_rows_authorized = {summary.get('core_four_maximum_rows_authorized')}",
        f"rows_limit_respected = {summary.get('core_four_limits_respected')}", "",
        "## Execution Metrics", "",
        f"resolution_requests = {summary.get('core_four_resolution_requests')}",
        f"formula_rows = {summary.get('core_four_formula_rows')}",
        f"formula_failures = {summary.get('core_four_formula_failures')}",
        f"blocked_input_unavailable_requests = {summary.get('core_four_blocked_input_unavailable_requests')}",
        f"conflicting_source_row_blocks = {summary.get('core_four_conflicting_source_row_blocks')}",
        f"future_bar_leaks = {summary.get('core_four_future_bar_leaks')}",
        f"output_contract_failures = {summary.get('core_four_output_contract_failures')}",
        f"nondeterministic_records = {summary.get('core_four_nondeterministic_records')}",
        f"restriction_rows = {summary.get('core_four_restriction_rows')}", "",
        "## Object Status Counts", "",
    ]
    status_counts: dict[str, int] = {}
    for row in request_rows:
        status_counts[str(row.get("resolution_status"))] = status_counts.get(str(row.get("resolution_status")), 0) + 1
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    formula_findings = [row for row in formula_rows if row.get("severity") in {"FAIL", "BLOCKED", "WARN"}]
    if formula_findings:
        lines.extend(["", "## Formula Findings", ""])
        for row in formula_findings[:40]:
            lines.append(f"- {row['request_id']} {row['object_id']}.{row['capability_id']}: {row['formula_status']} - {row['finding']}")
    nondeterministic = [row for row in determinism_rows if row.get("determinism_status") != "PASS"]
    if nondeterministic:
        lines.extend(["", "## Determinism Failures", ""])
        for row in nondeterministic:
            lines.append(f"- {row['record_id']}: {row['finding']}")
    if restriction_rows:
        lines.extend(["", "## Restrictions", ""])
        for row in restriction_rows[:40]:
            lines.append(f"- {row['object_id']}: {row['restriction_type']} - {row['restriction']}")
    lines.extend(["", "## Next Action", ""])
    if summary.get("experimental_builder_validation_execution_core_four") == "FAILED":
        lines.append("Resolve failed formulas, output contract failures or determinism failures before any integration design.")
    elif summary.get("experimental_builder_validation_execution_core_four") == "BLOCKED":
        lines.append("Resolve conflicting source row blockers before rerunning core-four builder validation.")
    else:
        lines.append("Keep Market State Integration closed; review the four independent Information Object builder records before opening a separate integration gate.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(config: dict[str, Any], registry_doc: dict[str, Any], pass_fail: list[dict[str, Any]], source_rows: list[dict[str, Any]], blocked_rows: list[dict[str, Any]], schema_summary: dict[str, Any]) -> dict[str, Any]:
    fail_count = sum(1 for row in pass_fail if row["severity"] == "FAIL")
    warn_count = sum(1 for row in pass_fail if row["severity"] == "WARN")
    pass_count = sum(1 for row in pass_fail if row["status"] == "PASS")
    pass_with_finding_count = sum(1 for row in pass_fail if row["status"] == "PASS_WITH_FINDING")
    source_warn_count = sum(1 for row in source_rows if row["severity"] == "WARN")
    source_fail_count = sum(1 for row in source_rows if row["severity"] == "FAIL")
    blocked_expected = sum(1 for row in pass_fail if row["severity"] == "BLOCKED_EXPECTED")
    blocked_leaks = sum(1 for row in blocked_rows if row["status"] == "LEAK")
    metrics = alias_metrics(config, registry_doc, source_rows)
    schema_validation = schema_summary.get("schema_validation", "NOT_EXECUTED")
    if fail_count or source_fail_count or blocked_leaks:
        status = "failed_contract_check"
    elif schema_validation == "FAILED":
        status = "failed_schema_check"
    elif schema_validation == "BLOCKED":
        status = "blocked_logical_to_physical_binding" if config.get("mode") == COLUMN_BINDING_MODE else "blocked_schema_check"
    elif schema_validation in {"PASS_WITH_FINDINGS", "PASS_WITH_RESTRICTIONS"}:
        status = "passed_logical_to_physical_binding_with_restrictions" if config.get("mode") == COLUMN_BINDING_MODE else "passed_schema_check_with_findings"
    elif schema_validation == "PASS":
        status = "passed_schema_check" if not blocked_expected else "passed_schema_check_with_expected_blocks"
    elif source_warn_count or metrics["unbound_unique_source_aliases"]:
        status = "passed_contract_check_pending_source_binding"
    elif warn_count or blocked_expected:
        status = "passed_with_findings_and_expected_blocks"
    else:
        status = "passed"
    total_aliases = metrics["unique_active_source_aliases"]
    bound_aliases = metrics["bound_unique_source_aliases"]
    if metrics["physical_paths_missing"] or source_fail_count:
        physical_source_binding = "FAILED"
    elif total_aliases and bound_aliases == total_aliases:
        physical_source_binding = "PASS"
    elif bound_aliases > 0:
        physical_source_binding = "PARTIAL"
    else:
        physical_source_binding = "INCOMPLETE"
    if metrics["physical_paths_missing"]:
        path_validation = "FAILED"
    elif metrics["physical_paths_checked"] and metrics["physical_paths_found"] == metrics["physical_paths_checked"]:
        path_validation = "PASS"
    elif metrics["physical_paths_checked"]:
        path_validation = "PARTIAL"
    else:
        path_validation = "NOT_EXECUTED"
    physical_candidate_roots = physical_source_binding
    if physical_source_binding == "INCOMPLETE":
        physical_candidate_roots = "PENDING"
    elif physical_source_binding == "PASS":
        physical_candidate_roots = "BOUND"
    return {
        "overall_status": status,
        "contract_resolution": "PASS" if not fail_count and not source_fail_count else "FAIL",
        "ontology_to_mapping_resolution": "PASS" if not fail_count else "FAIL",
        "blocked_capability_masking": "PASS" if blocked_leaks == 0 else "FAIL",
        "order_flow_expected_block": "PASS" if blocked_expected else "NOT_PRESENT",
        "binding_contract_structure": "PASS" if not source_fail_count else "FAIL",
        "physical_candidate_roots": physical_candidate_roots,
        "physical_source_binding": physical_source_binding,
        "path_validation": path_validation,
        "data_resolution": "NOT_AUTHORIZED",
        "data_validation": "NOT_AUTHORIZED",
        "grain_validation": "NOT_EXECUTED",
        "temporal_value_validation": "NOT_EXECUTED",
        "quality_semantics_validation": "NOT_EXECUTED",
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
        **schema_summary,
    }


def write_findings(path: Path, *, run_id: str, summary: dict[str, Any], source_rows: list[dict[str, Any]], schema_rows: list[dict[str, Any]]) -> None:
    source_findings = [row for row in source_rows if row["role"] == "active" and row["severity"] in {"WARN", "FAIL"}]
    schema_findings = [row for row in schema_rows if row["severity"] in {"WARN", "FAIL"}]
    if summary["contract_resolution"] == "FAIL":
        interpretation = "Contract or governance failures were detected."
    elif summary["schema_validation"] == "FAILED":
        interpretation = "No contract or governance failures were detected. The schema metadata gate found minimum physical schema incompatibilities."
    elif summary["schema_validation"] == "BLOCKED":
        interpretation = "No contract or governance failures were detected. Logical-to-physical binding is blocked by unresolved critical physical evidence."
    elif summary["schema_validation"] in {"PASS_WITH_FINDINGS", "PASS_WITH_RESTRICTIONS"}:
        interpretation = "No contract or governance failures were detected. The metadata gate passed with governance restrictions."
    elif summary["schema_validation"] == "PASS":
        interpretation = "No contract or governance failures were detected. The schema metadata gate passed for inspected physical metadata surfaces."
    elif summary["physical_source_binding"] == "PASS":
        interpretation = "No contract or governance failures were detected. Active source surfaces are physically bound; schema validation remains out of scope for this run."
    else:
        interpretation = "No contract or governance failures were detected. Physical source binding remains incomplete."
    if summary.get("bounded_quality_lineage_data_read") == "EXECUTED_WITH_LIMITS":
        interpretation = "No contract or governance failures were detected. The bounded quality and lineage gate executed within explicit experimental row-read limits."
        row_read_scope_line = "This run reads bounded market-row samples only under the bounded quality/lineage scope. It classifies quality and lineage readiness only; it does not execute feature builders, materialize State, repair data, or authorize operational use."
    elif summary.get("bounded_grain_data_read") == "EXECUTED_WITH_LIMITS":
        interpretation = "No contract or governance failures were detected. The bounded grain gate executed within explicit experimental row-read limits."
        row_read_scope_line = "This run reads bounded market-row samples only under the bounded grain scope. It validates candidate key usability inside the sample only; it does not claim full-history grain uniqueness, feature correctness, builder correctness, State readiness, or operational use."
    elif summary.get("bounded_sample_data_read") == "EXECUTED_WITH_LIMITS":
        interpretation = "No contract or governance failures were detected. The bounded sample gate executed within explicit experimental row-read limits."
        row_read_scope_line = "This run reads bounded market-row samples only under explicit scope authorization. It does not validate grain uniqueness, validate complete temporal legality, infer complete quality semantics, materialize State, or authorize operational use."
    else:
        row_read_scope_line = "This run inspects filesystem and Parquet footer metadata only. It does not read market rows, validate grain uniqueness, validate temporal values, infer quality semantics, materialize State, or authorize operational use."
    lines = [
        f"# Experimental State Builder Probe Findings - {run_id}", "",
        f"script_version: `{SCRIPT_VERSION}`", f"overall_status: `{summary['overall_status']}`", "",
        "## Institutional Status", "",
        f"contract_resolution = {summary['contract_resolution']}",
        f"ontology_to_mapping_resolution = {summary['ontology_to_mapping_resolution']}",
        f"blocked_capability_masking = {summary['blocked_capability_masking']}",
        f"order_flow_expected_block = {summary['order_flow_expected_block']}",
        f"binding_contract_structure = {summary['binding_contract_structure']}",
        f"physical_candidate_roots = {summary['physical_candidate_roots']}",
        f"physical_source_binding = {summary['physical_source_binding']}",
        f"path_validation = {summary['path_validation']}",
        f"schema_resolution = {summary['schema_resolution']}",
        f"schema_validation = {summary['schema_validation']}",
        f"data_resolution = {summary['data_resolution']}",
        f"data_validation = {summary['data_validation']}",
        f"grain_validation = {summary['grain_validation']}",
        f"temporal_value_validation = {summary['temporal_value_validation']}",
        f"quality_semantics_validation = {summary['quality_semantics_validation']}",
        f"lineage_validation = {summary.get('lineage_validation', 'NOT_EXECUTED')}",
        f"builder_validation_execution = {summary.get('builder_validation_execution', 'NOT_EXECUTED')}",
        f"market_state_integration = {summary.get('market_state_integration', 'NOT_OPEN')}",
        f"core_four_builder_execution_readiness = {summary.get('core_four_builder_execution_readiness', 'NOT_EVALUATED')}",
        f"quote_dependent_builder_execution_readiness = {summary.get('quote_dependent_builder_execution_readiness', 'NOT_EVALUATED')}", "",
        "## Summary", "",
        f"pass_count = {summary['pass_count']}", f"pass_with_finding_count = {summary['pass_with_finding_count']}",
        f"fail_count = {summary['fail_count']}", f"warn_count = {summary['warn_count']}",
        f"source_warn_count = {summary['source_warn_count']}", f"blocked_expected_count = {summary['blocked_expected_count']}",
        f"active_source_alias_usages = {summary['active_source_alias_usages']}",
        f"unique_active_source_aliases = {summary['unique_active_source_aliases']}",
        f"bound_unique_source_aliases = {summary['bound_unique_source_aliases']}",
        f"unbound_unique_source_aliases = {summary['unbound_unique_source_aliases']}",
        f"physical_paths_checked = {summary['physical_paths_checked']}", f"physical_paths_found = {summary['physical_paths_found']}",
        f"physical_paths_missing = {summary['physical_paths_missing']}",
        f"unique_sources_schema_checked = {summary['unique_sources_schema_checked']}",
        f"unique_sources_schema_passed = {summary['unique_sources_schema_passed']}",
        f"unique_sources_schema_passed_with_findings = {summary['unique_sources_schema_passed_with_findings']}",
        f"unique_sources_schema_blocked = {summary['unique_sources_schema_blocked']}",
        f"unique_sources_schema_failed = {summary['unique_sources_schema_failed']}",
        f"schema_files_inspected = {summary['schema_files_inspected']}",
        f"minimum_columns_missing = {summary['minimum_columns_missing']}",
        f"temporal_fields_missing = {summary['temporal_fields_missing']}",
        f"quality_fields_missing = {summary['quality_fields_missing']}",
        f"lineage_fields_missing = {summary['lineage_fields_missing']}",
        f"logical_column_resolution = {summary.get('logical_column_resolution', 'NOT_EXECUTED')}",
        f"logical_fields_expected = {summary.get('logical_fields_expected', 0)}",
        f"logical_fields_resolved = {summary.get('logical_fields_resolved', 0)}",
        f"logical_fields_resolved_with_restrictions = {summary.get('logical_fields_resolved_with_restrictions', 0)}",
        f"logical_fields_unresolved = {summary.get('logical_fields_unresolved', 0)}",
        f"fields_requiring_cast = {summary.get('fields_requiring_cast', 0)}",
        f"critical_state_fields_failed = {summary.get('critical_state_fields_failed', 0)}",
        f"critical_state_fields_blocked = {summary.get('critical_state_fields_blocked', 0)}",
        f"critical_temporal_fields_unresolved = {summary.get('critical_temporal_fields_unresolved', 0)}", "",
        "## Interpretation", "", interpretation, "",
        row_read_scope_line,
    ]
    if source_findings:
        lines.extend(["", "## Active Source Binding Findings", ""])
        for row in source_findings:
            lines.append(f"- {row['object_id']} -> {row['source_alias']}: {row['finding']} (binding_status={row['binding_status']})")
    if schema_findings:
        lines.extend(["", "## Schema Metadata Findings", ""])
        for row in schema_findings:
            lines.append(f"- {row['source_alias']}: {row['finding']} (status={row['schema_validation_status']}; missing_minimum={row['missing_minimum_columns']}; missing_temporal={row['missing_temporal_columns']})")
    lines.extend(["", "## Next Action", ""])
    if summary["schema_validation"] == "FAILED":
        lines.append("Create a governed logical-to-physical column binding layer for aliases whose logical minimum schema does not match observed physical columns, then rerun the schema metadata gate.")
    elif summary["schema_validation"] == "BLOCKED":
        lines.append("Resolve the blocked critical logical-to-physical bindings, especially availability timestamps and identifier readiness, then rerun the metadata-only column binding gate.")
    elif summary.get("bounded_quality_lineage_data_read") == "EXECUTED_WITH_LIMITS" and summary.get("bounded_quality_lineage_validation") in {"PASS", "PASS_WITH_RESTRICTIONS"}:
        lines.append("Open experimental builder validation execution for the core four Objects only: Trading Activity, Price Movement, Price Location / Structure and Volatility / Range State. Do not open Market State Integration.")
    elif summary.get("bounded_grain_data_read") == "EXECUTED_WITH_LIMITS" and summary.get("bounded_grain_validation") in {"PASS", "PASS_WITH_RESTRICTIONS"}:
        lines.append("Open bounded quality and lineage validation as a separate gate. Do not execute feature builders or materialize State from this artifact.")
    elif summary.get("bounded_sample_data_read") == "EXECUTED_WITH_LIMITS" and summary.get("bounded_sample_validation") != "FAILED":
        lines.append("Open bounded grain validation as a separate gate. Do not execute feature builders or materialize State from this artifact.")
    elif summary["schema_validation"] in {"PASS", "PASS_WITH_FINDINGS", "PASS_WITH_RESTRICTIONS"}:
        lines.append("Resolve schema governance findings if any, then open the next non-production gate for bounded sample validation only by explicit authorization.")
    elif summary["physical_source_binding"] == "PASS":
        lines.append("Open `binding_and_schema_check_only` with schema metadata authorization. Do not enable data reads or materialization.")
    else:
        lines.append("Bind the unique active source aliases to governed experimental physical candidate roots, then rerun the path gate.")
    lines.extend(["", "Do not enable data reads or materialization from this artifact."])
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
    parser.add_argument("--allow-data-read", action="store_true", help="Legacy full-read override; rejected. Bounded reads are authorized only by explicit scope.")
    parser.add_argument("--allow-full-data-read", action="store_true", help="Always rejected by this experimental probe.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.allow_data_read or args.allow_full_data_read:
        raise ProbeError(f"{SCRIPT_VERSION} refuses full data reads; bounded reads require explicit scope authority")

    config_path = args.config.resolve()
    config = read_json(config_path)
    validate_config(config)
    registry_doc, registry_path, registry_sha256 = load_binding_registry(config, config_path, config["mode"])
    column_registry_doc, column_registry_path, column_registry_sha256 = load_column_binding_registry(config, config_path, registry_doc)
    bounded_scope_doc, bounded_scope_path, bounded_scope_sha256 = load_bounded_sample_scope(config, config_path, registry_doc)
    bounded_grain_scope_doc, bounded_grain_scope_path, bounded_grain_scope_sha256 = load_bounded_grain_scope(config, config_path, registry_doc)
    bounded_quality_scope_doc, bounded_quality_scope_path, bounded_quality_scope_sha256 = load_bounded_quality_lineage_scope(config, config_path, registry_doc)
    core_four_scope_doc, core_four_scope_path, core_four_scope_sha256 = load_core_four_builder_scope(config, config_path, registry_doc)
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
        "dry_run": False if config["mode"] == CORE_FOUR_BUILDER_MODE else True,
        "execution_class": "experimental_non_materializing" if config["mode"] == CORE_FOUR_BUILDER_MODE else "contract_or_metadata_probe",
        "row_read_mode": "bounded" if config["mode"] in {BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE} else "none",
        "dry_run_outputs_only": True if config["mode"] == CORE_FOUR_BUILDER_MODE else False,
        "bounded_source_reads_executed": False,
        "allow_data_read": False,
        "allow_full_data_read": False,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "source_binding_registry_path": str(registry_path) if registry_path else None,
        "source_binding_registry_sha256": registry_sha256,
        "source_binding_registry_id": registry_doc.get("registry_id"),
        "column_binding_registry_path": str(column_registry_path) if column_registry_path else None,
        "column_binding_registry_sha256": column_registry_sha256,
        "column_binding_registry_id": column_registry_doc.get("registry_id") if column_registry_doc else None,
        "bounded_sample_scope_path": str(bounded_scope_path) if bounded_scope_path else None,
        "bounded_sample_scope_sha256": bounded_scope_sha256,
        "bounded_sample_scope_id": bounded_scope_doc.get("scope_id") if bounded_scope_doc else None,
        "bounded_grain_scope_path": str(bounded_grain_scope_path) if bounded_grain_scope_path else None,
        "bounded_grain_scope_sha256": bounded_grain_scope_sha256,
        "bounded_grain_scope_id": bounded_grain_scope_doc.get("scope_id") if bounded_grain_scope_doc else None,
        "bounded_quality_lineage_scope_path": str(bounded_quality_scope_path) if bounded_quality_scope_path else None,
        "bounded_quality_lineage_scope_sha256": bounded_quality_scope_sha256,
        "bounded_quality_lineage_scope_id": bounded_quality_scope_doc.get("scope_id") if bounded_quality_scope_doc else None,
        "core_four_builder_scope_path": str(core_four_scope_path) if core_four_scope_path else None,
        "core_four_builder_scope_sha256": core_four_scope_sha256,
        "core_four_builder_scope_id": core_four_scope_doc.get("scope_id") if core_four_scope_doc else None,
        "bounded_sample_data_read_authorized": bool(bounded_scope_doc),
        "bounded_grain_data_read_authorized": bool(bounded_grain_scope_doc),
        "bounded_quality_lineage_data_read_authorized": bool(bounded_quality_scope_doc),
        "core_four_builder_data_read_authorized": bool(core_four_scope_doc),
        "output_root": str(args.output_root.resolve()),
        "run_dir": str(run_dir),
        "expected_scope": "experimental core-four builder execution; bounded reads and formulas only; no State materialization" if config["mode"] == CORE_FOUR_BUILDER_MODE else "bounded row reads authorized by scope only; no feature builder execution or state materialization" if config["mode"] in {BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE} else "12 objects, binding/path/schema/column-binding metadata probe only; no row reads",
        "overwrite_policy": "refuse_existing_run_dir",
        **git_info(),
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {
        "run_id": run_id,
        "status": "running",
        "updated_at_utc": utc_now(),
        "current_step": "bounded_identity_temporal_validation" if config["mode"] == BOUNDED_SAMPLE_MODE else "bounded_grain_validation" if config["mode"] == BOUNDED_GRAIN_MODE else "bounded_quality_and_lineage_validation" if config["mode"] == BOUNDED_QUALITY_LINEAGE_MODE else "experimental_builder_validation_execution_core_four" if config["mode"] == CORE_FOUR_BUILDER_MODE else "binding_path_schema_column_metadata_check",
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

    schema_rows: list[dict[str, Any]] = []
    column_rows: list[dict[str, Any]] = []
    logical_binding_rows: list[dict[str, Any]] = []
    unresolved_logical_rows: list[dict[str, Any]] = []
    partition_binding_rows: list[dict[str, Any]] = []
    manifest_binding_rows: list[dict[str, Any]] = []
    cast_policy_rows: list[dict[str, Any]] = []
    schema_summary = default_schema_summary(config["mode"])
    bounded_manifest: dict[str, Any] = {}
    read_limit_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    timestamp_rows: list[dict[str, Any]] = []
    cutoff_rows: list[dict[str, Any]] = []
    daily_availability_policy_rows: list[dict[str, Any]] = []
    bounded_summary: dict[str, Any] = {}
    grain_rows: list[dict[str, Any]] = []
    duplicate_key_group_rows: list[dict[str, Any]] = []
    null_key_rows: list[dict[str, Any]] = []
    hidden_dimension_rows: list[dict[str, Any]] = []
    raw_quotes_same_timestamp_rows_report: list[dict[str, Any]] = []
    bounded_grain_summary: dict[str, Any] = {}
    quality_lineage_field_rows: list[dict[str, Any]] = []
    quality_derivation_rows: list[dict[str, Any]] = []
    builder_execution_blocker_rows: list[dict[str, Any]] = []
    promotion_only_restriction_rows: list[dict[str, Any]] = []
    bounded_quality_lineage_summary: dict[str, Any] = {}
    core_four_request_rows: list[dict[str, Any]] = []
    core_four_capability_rows: list[dict[str, Any]] = []
    core_four_selected_source_rows: list[dict[str, Any]] = []
    core_four_cutoff_rows: list[dict[str, Any]] = []
    core_four_duplicate_rows: list[dict[str, Any]] = []
    core_four_formula_rows: list[dict[str, Any]] = []
    core_four_output_contract_rows: list[dict[str, Any]] = []
    core_four_determinism_rows: list[dict[str, Any]] = []
    core_four_restriction_rows: list[dict[str, Any]] = []
    core_four_resolution_records: list[dict[str, Any]] = []
    core_four_summary: dict[str, Any] = {}
    if config["mode"] == SCHEMA_MODE:
        schema_rows, column_rows, schema_fingerprint_report, schema_summary = check_schema_metadata(config, registry_doc)
        write_csv(run_dir / "schema_availability_report.csv", schema_rows, [
            "source_alias", "object_refs", "physical_candidate_root", "dataset_format", "schema_probe_authorized",
            "discovery_status", "files_discovered", "files_inspected", "schema_consistency_status", "schema_fingerprint_count",
            "missing_minimum_columns", "missing_temporal_columns", "missing_quality_fields", "missing_lineage_fields",
            "type_mismatches", "schema_validation_status", "severity", "finding",
        ])
        write_csv(run_dir / "column_compatibility_report.csv", column_rows, [
            "source_alias", "column_group", "column_name", "column_presence_status", "expected_type_families",
            "observed_type_strings", "observed_type_families", "type_compatibility_status", "severity", "finding",
        ])
        write_json(run_dir / "schema_fingerprint_report.json", schema_fingerprint_report)
        write_json(run_dir / "schema_gate_summary.json", schema_summary)
    elif config["mode"] in {COLUMN_BINDING_MODE, BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE}:
        if column_registry_doc is None:
            raise ProbeError("column binding registry is required for logical-to-physical or bounded row-read modes")
        logical_binding_rows, unresolved_logical_rows, partition_binding_rows, manifest_binding_rows, cast_policy_rows, column_fingerprint_report, schema_summary = check_logical_to_physical_bindings(config, registry_doc, column_registry_doc)
        binding_fields = [
            "source_alias", "logical_field", "logical_field_groups", "binding_status", "physical_resolution_type",
            "physical_column", "partition_key", "partition_key_binding_type", "manifest_field", "dataset_metadata_field",
            "expected_type_family", "observed_type", "observed_type_family", "semantic_role", "criticality", "temporal_role",
            "quality_or_lineage_role", "identity_resolution_required", "cast_policy_required", "cast_target_type_family",
            "parse_policy_status", "timestamp_unit_policy_required", "type_readiness_status", "review_status",
            "physical_presence_status", "type_compatibility_status", "resolution_status", "severity", "finding", "evidence",
        ]
        write_csv(run_dir / "logical_physical_binding_report.csv", logical_binding_rows, binding_fields)
        write_csv(run_dir / "unresolved_logical_fields_report.csv", unresolved_logical_rows, binding_fields)
        write_csv(run_dir / "partition_binding_report.csv", partition_binding_rows, binding_fields)
        write_csv(run_dir / "manifest_binding_report.csv", manifest_binding_rows, binding_fields)
        write_csv(run_dir / "cast_policy_requirements_report.csv", cast_policy_rows, binding_fields)
        write_json(run_dir / "column_binding_schema_fingerprint_report.json", column_fingerprint_report)
        write_json(run_dir / "column_binding_summary.json", schema_summary)
        if config["mode"] == BOUNDED_SAMPLE_MODE:
            if bounded_scope_doc is None:
                raise ProbeError("bounded sample scope is required for bounded identity and temporal validation")
            if schema_summary.get("critical_state_fields_failed") or schema_summary.get("critical_state_fields_blocked") or schema_summary.get("critical_temporal_fields_unresolved"):
                raise ProbeError("bounded sample validation cannot run while critical logical-to-physical bindings are unresolved")
            bounded_manifest, read_limit_rows, identity_rows, timestamp_rows, cutoff_rows, daily_availability_policy_rows, bounded_summary = check_bounded_identity_and_temporal_validation(config, registry_doc, bounded_scope_doc)
            write_json(run_dir / "bounded_sample_manifest.json", bounded_manifest)
            write_csv(run_dir / "sample_read_limits_report.csv", read_limit_rows, ["source_alias", "file_path", "authorized_max_rows_per_file", "rows_read", "authorized_columns", "columns_read", "missing_allowed_columns", "limit_respected", "write_to_source"])
            write_csv(run_dir / "identity_resolution_report.csv", identity_rows, ["source_alias", "files_sampled", "rows_checked", "identity_evidence_type", "row_identity_fields", "partition_identity_values", "non_null_identity_rows", "missing_identity_rows", "partition_row_mismatch_count", "unique_row_tickers", "canonical_reference_tickers_checked", "canonical_reference_tickers_resolved", "ambiguous_reference_ticker_count", "identity_resolution_status", "severity", "finding"])
            write_csv(run_dir / "timestamp_parse_report.csv", timestamp_rows, ["source_alias", "temporal_field", "values_checked", "parse_success_count", "parse_failure_count", "null_count", "parse_success_rate", "detected_unit", "unit_detection_evidence", "timezone_detected_count", "timezone_assumed_count", "minimum_observed_timestamp_utc", "maximum_observed_timestamp_utc", "timestamp_parse_status", "severity", "finding", "evidence"])
            write_csv(run_dir / "cutoff_legality_report.csv", cutoff_rows, ["source_alias", "decision_case", "decision_timestamp_utc", "selected_bar_end_utc", "eligible_bar_count", "future_bar_leak", "cutoff_status", "severity", "finding"])
            write_csv(run_dir / "daily_availability_policy_report.csv", daily_availability_policy_rows, ["source_alias", "session_date", "decision_case", "derived_legal_availability_utc", "decision_timestamp_utc", "row_eligible", "expected_row_eligible", "policy_version", "calendar_status", "daily_availability_status", "severity", "finding"])
            write_json(run_dir / "bounded_sample_summary.json", bounded_summary)
        elif config["mode"] == BOUNDED_GRAIN_MODE:
            if bounded_grain_scope_doc is None:
                raise ProbeError("bounded grain scope is required for bounded grain validation")
            if schema_summary.get("critical_state_fields_failed") or schema_summary.get("critical_state_fields_blocked") or schema_summary.get("critical_temporal_fields_unresolved"):
                raise ProbeError("bounded grain validation cannot run while critical logical-to-physical bindings are unresolved")
            bounded_manifest, read_limit_rows, grain_rows, duplicate_key_group_rows, null_key_rows, hidden_dimension_rows, raw_quotes_same_timestamp_rows_report, bounded_grain_summary = check_bounded_grain_validation(config, registry_doc, bounded_grain_scope_doc)
            write_json(run_dir / "bounded_grain_manifest.json", bounded_manifest)
            write_csv(run_dir / "sample_read_limits_report.csv", read_limit_rows, ["source_alias", "file_path", "authorized_max_rows_per_file", "rows_read", "authorized_columns", "columns_read", "missing_allowed_columns", "limit_respected", "write_to_source"])
            write_csv(run_dir / "grain_key_report.csv", grain_rows, ["source_alias", "rows_checked", "files_sampled", "physical_key_components", "canonical_key_components", "key_rows_checked", "null_key_rows", "physical_duplicate_key_groups", "physical_duplicate_key_rows", "canonical_duplicate_key_groups", "canonical_duplicate_key_rows", "identical_duplicate_groups", "conflicting_duplicate_groups", "hidden_dimension_candidates", "hidden_dimension_values_observed", "physical_key_uniqueness", "canonical_key_uniqueness", "instrument_id_physical_readiness", "identity_resolution_source", "sequence_field_availability", "source_row_ordinal_availability", "window_invalid_rows", "window_overlap_groups", "window_overlap_pairs", "window_label_conflict_groups", "grain_validation_status", "severity", "finding", "restriction_reasons"])
            write_csv(run_dir / "duplicate_key_groups.csv", duplicate_key_group_rows, ["source_alias", "key_scope", "key_value", "row_count", "file_count", "hidden_dimension_values", "distinct_state_count", "duplicate_classification", "severity", "finding"])
            write_csv(run_dir / "null_key_report.csv", null_key_rows, ["source_alias", "key_scope", "row_index", "file_path", "missing_components", "severity", "finding"])
            write_csv(run_dir / "hidden_dimension_findings.csv", hidden_dimension_rows, ["source_alias", "dimension", "observed_values", "affected_duplicate_groups", "status", "severity", "finding"])
            write_csv(run_dir / "raw_quotes_same_timestamp_report.csv", raw_quotes_same_timestamp_rows_report, ["source_alias", "ticker", "quote_timestamp", "row_count", "distinct_quote_state_count", "classification", "sequence_field_availability", "source_row_ordinal_availability", "severity", "finding"])
            write_json(run_dir / "bounded_grain_summary.json", bounded_grain_summary)
        elif config["mode"] == BOUNDED_QUALITY_LINEAGE_MODE:
            if bounded_quality_scope_doc is None:
                raise ProbeError("bounded quality/lineage scope is required for bounded quality and lineage validation")
            if schema_summary.get("critical_state_fields_failed") or schema_summary.get("critical_state_fields_blocked") or schema_summary.get("critical_temporal_fields_unresolved"):
                raise ProbeError("bounded quality/lineage validation cannot run while critical logical-to-physical bindings are unresolved")
            bounded_manifest, read_limit_rows, quality_lineage_field_rows, quality_derivation_rows, builder_execution_blocker_rows, promotion_only_restriction_rows, bounded_quality_lineage_summary = check_bounded_quality_and_lineage_validation(config, registry_doc, bounded_quality_scope_doc)
            write_json(run_dir / "bounded_quality_lineage_manifest.json", bounded_manifest)
            write_csv(run_dir / "quality_lineage_read_limits_report.csv", read_limit_rows, ["source_alias", "file_path", "authorized_max_rows_per_file", "rows_read", "authorized_columns", "columns_read", "missing_allowed_columns", "limit_respected", "write_to_source"])
            write_csv(run_dir / "quality_lineage_field_report.csv", quality_lineage_field_rows, ["source_alias", "logical_field", "field_family", "resolution_strategy", "policy_ref", "policy_check", "policy_exists", "criticality", "field_resolution_status", "builder_blocker_scope", "builder_execution_impact", "promotion_impact", "severity", "finding"])
            write_csv(run_dir / "quality_derivation_report.csv", quality_derivation_rows, ["source_alias", "policy_check", "check_type", "policy_ref", "policy_exists", "rows_checked", "derivation_status", "severity", "finding", "metrics"])
            write_csv(run_dir / "builder_execution_blockers_report.csv", builder_execution_blocker_rows, ["source_alias", "logical_field", "builder_blocker_scope", "builder_execution_impact", "field_resolution_status", "severity", "required_resolution", "finding"])
            write_csv(run_dir / "promotion_only_restrictions_report.csv", promotion_only_restriction_rows, ["source_alias", "logical_field", "promotion_impact", "field_resolution_status", "severity", "finding"])
            write_json(run_dir / "bounded_quality_lineage_summary.json", bounded_quality_lineage_summary)
        elif config["mode"] == CORE_FOUR_BUILDER_MODE:
            if core_four_scope_doc is None:
                raise ProbeError("core-four builder scope is required for experimental builder validation execution")
            if schema_summary.get("critical_state_fields_failed") or schema_summary.get("critical_state_fields_blocked") or schema_summary.get("critical_temporal_fields_unresolved"):
                raise ProbeError("core-four builder validation cannot run while critical logical-to-physical bindings are unresolved")
            bounded_manifest, read_limit_rows, core_four_request_rows, core_four_capability_rows, core_four_selected_source_rows, core_four_cutoff_rows, core_four_duplicate_rows, core_four_formula_rows, core_four_output_contract_rows, core_four_determinism_rows, core_four_restriction_rows, core_four_resolution_records, core_four_summary = check_core_four_builder_validation(config, registry_doc, core_four_scope_doc)
            write_json(run_dir / "core_four_builder_execution_manifest.json", bounded_manifest)
            write_csv(run_dir / "core_four_builder_read_limits_report.csv", read_limit_rows, ["source_alias", "file_path", "authorized_max_rows_per_file", "rows_read", "authorized_columns", "columns_read", "missing_allowed_columns", "limit_respected", "write_to_source"])
            write_csv(run_dir / "builder_request_report.csv", core_four_request_rows, ["request_id", "context_id", "object_id", "instrument_id", "ticker", "session_date", "decision_case", "decision_timestamp_utc", "resolution_status", "resolution_fingerprint", "capabilities_requested", "capabilities_resolved", "restrictions_count"])
            write_csv(run_dir / "capability_resolution_report.csv", core_four_capability_rows, ["request_id", "object_id", "capability_id", "source_alias", "input_fields", "formula_id", "resolution_rule", "resolution_status", "restriction", "finding"])
            write_csv(run_dir / "selected_source_rows_report.csv", core_four_selected_source_rows, ["request_id", "object_id", "source_alias", "input_role", "source_file_path", "source_row_ordinal_in_file", "selected_source_timestamp_utc", "session_date", "source_row_count", "selection_rule", "selection_status", "evidence"])
            write_csv(run_dir / "cutoff_enforcement_report.csv", core_four_cutoff_rows, ["request_id", "object_id", "source_alias", "input_role", "source_timestamp_utc", "availability_timestamp_utc", "decision_timestamp_utc", "eligible_at_decision", "future_leak", "cutoff_status", "finding"])
            write_csv(run_dir / "duplicate_handling_report.csv", core_four_duplicate_rows, ["request_id", "object_id", "source_alias", "selected_bar_end_utc", "duplicate_group_key", "duplicate_group_row_count", "duplicate_group_distinct_state_count", "duplicate_handling_status", "severity", "finding"])
            write_csv(run_dir / "formula_validation_report.csv", core_four_formula_rows, ["request_id", "object_id", "capability_id", "formula_id", "input_fields", "formula_status", "output_field", "output_value", "severity", "finding", "restriction"])
            write_csv(run_dir / "builder_output_contract_report.csv", core_four_output_contract_rows, ["request_id", "object_id", "required_schema_fields_present", "output_namespace", "namespace_fields_valid", "required_capabilities", "value_fields_produced", "missing_required_value_fields", "output_contract_status", "severity", "finding"])
            write_csv(run_dir / "determinism_report.csv", core_four_determinism_rows, ["request_id", "object_id", "record_id", "first_resolution_fingerprint", "second_resolution_fingerprint", "repeat_run_fingerprint_match", "determinism_status", "severity", "finding"])
            write_csv(run_dir / "builder_restrictions_report.csv", core_four_restriction_rows, ["request_id", "object_id", "restriction_type", "restriction", "severity", "finding"])
            write_jsonl(run_dir / "core_four_resolution_records.jsonl", core_four_resolution_records)
            write_json(run_dir / "core_four_builder_validation_summary.json", core_four_summary)

    sample_tickers = args.sample_tickers or config.get("sample_tickers", [])
    sample_decision_timestamps = args.sample_decision_timestamps or config.get("sample_decision_timestamps", [])
    dry_rows = 0
    if args.emit_dry_run_rows:
        dry_rows = write_dry_rows(run_dir / "dry_run_resolution_snapshots.jsonl", config, sample_tickers, sample_decision_timestamps)

    summary = summarize(config, registry_doc, pass_fail, source_rows, blocked_rows, schema_summary)
    if bounded_summary:
        summary.update(bounded_summary)
        write_bounded_sample_findings(run_dir / "bounded_sample_findings.md", run_id=run_id, summary=summary, identity_rows=identity_rows, timestamp_rows=timestamp_rows, cutoff_rows=cutoff_rows, daily_rows=daily_availability_policy_rows)
    if bounded_grain_summary:
        summary.update(bounded_grain_summary)
        write_bounded_grain_findings(run_dir / "bounded_grain_findings.md", run_id=run_id, summary=summary, grain_rows=grain_rows, duplicate_rows=duplicate_key_group_rows, null_key_rows=null_key_rows, hidden_rows=hidden_dimension_rows, raw_quote_rows=raw_quotes_same_timestamp_rows_report)
    if bounded_quality_lineage_summary:
        summary.update(bounded_quality_lineage_summary)
        write_bounded_quality_lineage_findings(run_dir / "bounded_quality_lineage_findings.md", run_id=run_id, summary=summary, field_rows=quality_lineage_field_rows, derivation_rows=quality_derivation_rows, builder_blocker_rows=builder_execution_blocker_rows, promotion_rows=promotion_only_restriction_rows)
    if core_four_summary:
        summary.update(core_four_summary)
        write_core_four_builder_findings(run_dir / "core_four_builder_validation_findings.md", run_id=run_id, summary=summary, request_rows=core_four_request_rows, formula_rows=core_four_formula_rows, determinism_rows=core_four_determinism_rows, restriction_rows=core_four_restriction_rows)
    write_findings(run_dir / "experimental_findings.md", run_id=run_id, summary=summary, source_rows=source_rows, schema_rows=schema_rows)
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
    if config["mode"] == SCHEMA_MODE:
        artifacts["schema_availability_report"] = str(run_dir / "schema_availability_report.csv")
        artifacts["column_compatibility_report"] = str(run_dir / "column_compatibility_report.csv")
        artifacts["schema_fingerprint_report"] = str(run_dir / "schema_fingerprint_report.json")
        artifacts["schema_gate_summary"] = str(run_dir / "schema_gate_summary.json")
    elif config["mode"] in {COLUMN_BINDING_MODE, BOUNDED_SAMPLE_MODE, BOUNDED_GRAIN_MODE, BOUNDED_QUALITY_LINEAGE_MODE, CORE_FOUR_BUILDER_MODE}:
        artifacts["logical_physical_binding_report"] = str(run_dir / "logical_physical_binding_report.csv")
        artifacts["unresolved_logical_fields_report"] = str(run_dir / "unresolved_logical_fields_report.csv")
        artifacts["partition_binding_report"] = str(run_dir / "partition_binding_report.csv")
        artifacts["manifest_binding_report"] = str(run_dir / "manifest_binding_report.csv")
        artifacts["cast_policy_requirements_report"] = str(run_dir / "cast_policy_requirements_report.csv")
        artifacts["column_binding_schema_fingerprint_report"] = str(run_dir / "column_binding_schema_fingerprint_report.json")
        artifacts["column_binding_summary"] = str(run_dir / "column_binding_summary.json")
    if config["mode"] == BOUNDED_SAMPLE_MODE:
        artifacts["bounded_sample_manifest"] = str(run_dir / "bounded_sample_manifest.json")
        artifacts["sample_read_limits_report"] = str(run_dir / "sample_read_limits_report.csv")
        artifacts["identity_resolution_report"] = str(run_dir / "identity_resolution_report.csv")
        artifacts["timestamp_parse_report"] = str(run_dir / "timestamp_parse_report.csv")
        artifacts["cutoff_legality_report"] = str(run_dir / "cutoff_legality_report.csv")
        artifacts["daily_availability_policy_report"] = str(run_dir / "daily_availability_policy_report.csv")
        artifacts["bounded_sample_summary"] = str(run_dir / "bounded_sample_summary.json")
        artifacts["bounded_sample_findings"] = str(run_dir / "bounded_sample_findings.md")
    if config["mode"] == BOUNDED_GRAIN_MODE:
        artifacts["bounded_grain_manifest"] = str(run_dir / "bounded_grain_manifest.json")
        artifacts["sample_read_limits_report"] = str(run_dir / "sample_read_limits_report.csv")
        artifacts["grain_key_report"] = str(run_dir / "grain_key_report.csv")
        artifacts["duplicate_key_groups"] = str(run_dir / "duplicate_key_groups.csv")
        artifacts["null_key_report"] = str(run_dir / "null_key_report.csv")
        artifacts["hidden_dimension_findings"] = str(run_dir / "hidden_dimension_findings.csv")
        artifacts["raw_quotes_same_timestamp_report"] = str(run_dir / "raw_quotes_same_timestamp_report.csv")
        artifacts["bounded_grain_summary"] = str(run_dir / "bounded_grain_summary.json")
        artifacts["bounded_grain_findings"] = str(run_dir / "bounded_grain_findings.md")
    if config["mode"] == BOUNDED_QUALITY_LINEAGE_MODE:
        artifacts["bounded_quality_lineage_manifest"] = str(run_dir / "bounded_quality_lineage_manifest.json")
        artifacts["quality_lineage_read_limits_report"] = str(run_dir / "quality_lineage_read_limits_report.csv")
        artifacts["quality_lineage_field_report"] = str(run_dir / "quality_lineage_field_report.csv")
        artifacts["quality_derivation_report"] = str(run_dir / "quality_derivation_report.csv")
        artifacts["builder_execution_blockers_report"] = str(run_dir / "builder_execution_blockers_report.csv")
        artifacts["promotion_only_restrictions_report"] = str(run_dir / "promotion_only_restrictions_report.csv")
        artifacts["bounded_quality_lineage_summary"] = str(run_dir / "bounded_quality_lineage_summary.json")
        artifacts["bounded_quality_lineage_findings"] = str(run_dir / "bounded_quality_lineage_findings.md")
    if config["mode"] == CORE_FOUR_BUILDER_MODE:
        artifacts["core_four_builder_execution_manifest"] = str(run_dir / "core_four_builder_execution_manifest.json")
        artifacts["core_four_builder_read_limits_report"] = str(run_dir / "core_four_builder_read_limits_report.csv")
        artifacts["builder_request_report"] = str(run_dir / "builder_request_report.csv")
        artifacts["capability_resolution_report"] = str(run_dir / "capability_resolution_report.csv")
        artifacts["selected_source_rows_report"] = str(run_dir / "selected_source_rows_report.csv")
        artifacts["cutoff_enforcement_report"] = str(run_dir / "cutoff_enforcement_report.csv")
        artifacts["duplicate_handling_report"] = str(run_dir / "duplicate_handling_report.csv")
        artifacts["formula_validation_report"] = str(run_dir / "formula_validation_report.csv")
        artifacts["builder_output_contract_report"] = str(run_dir / "builder_output_contract_report.csv")
        artifacts["determinism_report"] = str(run_dir / "determinism_report.csv")
        artifacts["builder_restrictions_report"] = str(run_dir / "builder_restrictions_report.csv")
        artifacts["core_four_resolution_records"] = str(run_dir / "core_four_resolution_records.jsonl")
        artifacts["core_four_builder_validation_summary"] = str(run_dir / "core_four_builder_validation_summary.json")
        artifacts["core_four_builder_validation_findings"] = str(run_dir / "core_four_builder_validation_findings.md")
    if args.emit_dry_run_rows:
        artifacts["dry_run_resolution_snapshots"] = str(run_dir / "dry_run_resolution_snapshots.jsonl")
    final_manifest = {
        **pre_manifest,
        "status": "complete",
        "completed_at_utc": utc_now(),
        "overall_status": summary["overall_status"],
        "objects_checked": len(config["objects"]),
        "source_rows": len(source_rows),
        "schema_rows": len(schema_rows),
        "schema_column_rows": len(column_rows),
        "logical_physical_binding_rows": len(logical_binding_rows),
        "unresolved_logical_field_rows": len(unresolved_logical_rows),
        "partition_binding_rows": len(partition_binding_rows),
        "manifest_binding_rows": len(manifest_binding_rows),
        "cast_policy_requirement_rows": len(cast_policy_rows),
        "bounded_identity_rows": len(identity_rows),
        "bounded_timestamp_parse_rows": len(timestamp_rows),
        "bounded_cutoff_legality_rows": len(cutoff_rows),
        "bounded_daily_availability_policy_rows": len(daily_availability_policy_rows),
        "bounded_sample_read_limit_rows": len(read_limit_rows) if config["mode"] == BOUNDED_SAMPLE_MODE else 0,
        "bounded_grain_rows": len(grain_rows),
        "bounded_grain_duplicate_key_group_rows": len(duplicate_key_group_rows),
        "bounded_grain_null_key_rows": len(null_key_rows),
        "bounded_grain_hidden_dimension_rows": len(hidden_dimension_rows),
        "bounded_grain_raw_quote_same_timestamp_rows": len(raw_quotes_same_timestamp_rows_report),
        "bounded_grain_read_limit_rows": len(read_limit_rows) if config["mode"] == BOUNDED_GRAIN_MODE else 0,
        "quality_lineage_field_rows": len(quality_lineage_field_rows),
        "quality_derivation_rows": len(quality_derivation_rows),
        "builder_execution_blocker_rows": len(builder_execution_blocker_rows),
        "promotion_only_restriction_rows": len(promotion_only_restriction_rows),
        "bounded_quality_lineage_read_limit_rows": len(read_limit_rows) if config["mode"] == BOUNDED_QUALITY_LINEAGE_MODE else 0,
        "core_four_builder_request_rows": len(core_four_request_rows),
        "core_four_capability_resolution_rows": len(core_four_capability_rows),
        "core_four_selected_source_rows": len(core_four_selected_source_rows),
        "core_four_cutoff_rows": len(core_four_cutoff_rows),
        "core_four_duplicate_rows": len(core_four_duplicate_rows),
        "core_four_formula_rows": len(core_four_formula_rows),
        "core_four_output_contract_rows": len(core_four_output_contract_rows),
        "core_four_determinism_rows": len(core_four_determinism_rows),
        "core_four_restriction_rows": len(core_four_restriction_rows),
        "core_four_resolution_record_rows": len(core_four_resolution_records),
        "core_four_builder_read_limit_rows": len(read_limit_rows) if config["mode"] == CORE_FOUR_BUILDER_MODE else 0,
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
    return 0 if summary["overall_status"] not in {"failed_contract_check", "failed_schema_check", "blocked_schema_check", "blocked_logical_to_physical_binding", "failed_bounded_identity_temporal_validation", "failed_bounded_grain_validation", "blocked_bounded_grain_validation", "failed_bounded_quality_lineage_validation", "blocked_bounded_quality_lineage_validation", "failed_core_four_builder_validation", "blocked_core_four_builder_validation"} else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
