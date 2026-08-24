"""Fail-closed configuration, target and human-authorization gates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from sec_pit.massive_sec_models import (
    CONDITIONAL_ENDPOINT_IDS,
    DIRECT_ENDPOINT_IDS,
    ENDPOINT_SPECS,
    normalize_cik,
)
from sec_pit.massive_sec_storage import file_sha256


@dataclass(frozen=True)
class FrozenTarget:
    path: Path
    sha256: str
    row_count: int
    unique_ticker_count: int
    unique_instrument_count: int
    unique_cik_count: int


@dataclass(frozen=True)
class AuthorizationDecision:
    gate: str
    reason: str
    authorization_id: str | None
    allowed_endpoint_ids: tuple[str, ...]
    allowed_target_case_count: int
    allowed_unique_cik_count: int


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _reject_secret_material(value: Any, trail: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).casefold().replace("-", "_")
            if normalized in {"api_key", "apikey", "massive_api_key", "authorization_header"}:
                raise ValueError(f"credential material is prohibited in config: {trail}.{key}")
            _reject_secret_material(child, f"{trail}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_secret_material(child, f"{trail}[{index}]")


def validate_config(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    _reject_secret_material(config)
    if config.get("config_id") != "massive_sec_acquisition_v0_1":
        raise ValueError("unexpected Massive SEC config_id")
    output_root = str(config.get("output_root") or "")
    if output_root in {"", "HUMAN_PROVIDED_OUTPUT_ROOT"}:
        raise ValueError("output_root must be the exact human-supplied absolute path")
    if Path(output_root).resolve() != Path(r"D:\sec_float_pit_MASSIVE").resolve():
        raise ValueError("output_root drift from the human-supplied governed root")
    requested = tuple(config.get("endpoint_ids") or ())
    if not requested or len(set(requested)) != len(requested):
        raise ValueError("endpoint_ids must be a non-empty unique list")
    unknown = sorted(set(requested) - set(ENDPOINT_SPECS))
    if unknown:
        raise ValueError(f"endpoint outside frozen allowlist: {unknown}")
    if "form_13f" in requested:
        raise ValueError("13F remains blocked pending its separate CUSIP/window gate")
    workers = int(config.get("http_workers") or 0)
    maximum_workers = int(config.get("maximum_http_workers_after_probe") or 0)
    if not 1 <= workers <= 4 or not workers <= maximum_workers <= 8:
        raise ValueError("worker policy must be initial<=4 and probe-gated maximum<=8")
    rps = float(config.get("requests_per_second") or 0)
    if not 0 < rps <= 5:
        raise ValueError("configured engineering request ceiling must be within (0, 5]")
    if float(config.get("minimum_free_space_gib") or 0) < 200:
        raise ValueError("minimum_free_space_gib must be at least 200")
    return config


def validate_frozen_target(target_manifest_path: Path) -> FrozenTarget:
    manifest = read_json(target_manifest_path)
    if manifest.get("target_id") != "massive_sec_target_4824_v0_1":
        raise ValueError("unexpected target manifest identity")
    target_path = Path(str(manifest["path"])).resolve()
    if not target_path.is_file():
        raise FileNotFoundError(target_path)
    observed_hash = file_sha256(target_path)
    expected_hash = str(manifest.get("sha256") or "").lower()
    if observed_hash.lower() != expected_hash:
        raise ValueError("target SHA-256 drift")
    frame = pd.read_parquet(
        target_path, columns=["instrument_id", "ticker", "cik"]
    )
    frame["ticker"] = frame["ticker"].astype(str).str.strip().str.upper()
    frame["cik"] = frame["cik"].map(normalize_cik)
    observed = FrozenTarget(
        path=target_path,
        sha256=observed_hash,
        row_count=len(frame),
        unique_ticker_count=int(frame["ticker"].nunique()),
        unique_instrument_count=int(frame["instrument_id"].nunique()),
        unique_cik_count=int(frame["cik"].nunique()),
    )
    checks = {
        "row_count": observed.row_count,
        "unique_ticker_count": observed.unique_ticker_count,
        "unique_instrument_count": observed.unique_instrument_count,
        "unique_cik_count": observed.unique_cik_count,
    }
    for field, value in checks.items():
        if int(manifest.get(field) or -1) != value:
            raise ValueError(f"target {field} drift: expected {manifest.get(field)}, got {value}")
    if observed.row_count != 4_824 or observed.unique_ticker_count != 4_824:
        raise ValueError("target no longer represents the exact 4,824 ticker membership")
    return observed


def validate_authorization(
    authorization_path: Path,
    *,
    config_path: Path,
    target_manifest_path: Path,
    objective_path: Path,
    component_bundle_sha256: str,
    target: FrozenTarget,
    requested_endpoint_ids: tuple[str, ...],
    execution_mode: str,
    requested_target_case_count: int,
    requested_unique_cik_count: int,
) -> AuthorizationDecision:
    if not authorization_path.is_file():
        return AuthorizationDecision("FAIL", "AUTHORIZATION_FILE_MISSING", None, (), 0, 0)
    value = read_json(authorization_path)
    if value.get("status") != "AUTHORIZED":
        return AuthorizationDecision(
            "FAIL",
            "AUTHORIZATION_STATUS_NOT_AUTHORIZED",
            value.get("authorization_id"),
            (),
            0,
            0,
        )
    for required in ("authorized_by", "authorized_at_utc", "authorization_basis"):
        if not str(value.get(required) or "").strip():
            return AuthorizationDecision(
                "FAIL",
                f"AUTHORIZATION_MISSING_{required.upper()}",
                value.get("authorization_id"),
                (),
                0,
                0,
            )
    expected_scope = "PROBE_ONLY" if execution_mode == "PROBE" else "FULL_AFTER_PROBE_PASS"
    if value.get("authorization_scope") != expected_scope:
        return AuthorizationDecision(
            "FAIL", "AUTHORIZATION_SCOPE_MISMATCH", value.get("authorization_id"), (), 0, 0
        )
    license_confirmation = value.get("license_retention_confirmation") or {}
    if license_confirmation.get("status") != "CONFIRMED":
        return AuthorizationDecision(
            "FAIL",
            "LICENSE_RETENTION_NOT_CONFIRMED",
            value.get("authorization_id"),
            (),
            0,
            0,
        )
    for required in ("confirmed_by", "confirmed_at_utc", "evidence_reference"):
        if not str(license_confirmation.get(required) or "").strip():
            return AuthorizationDecision(
                "FAIL",
                f"LICENSE_CONFIRMATION_MISSING_{required.upper()}",
                value.get("authorization_id"),
                (),
                0,
                0,
            )
    if str(value.get("config_sha256") or "").lower() != file_sha256(config_path).lower():
        return AuthorizationDecision(
            "FAIL", "CONFIG_HASH_MISMATCH", value.get("authorization_id"), (), 0, 0
        )
    if str(value.get("target_manifest_sha256") or "").lower() != file_sha256(
        target_manifest_path
    ).lower():
        return AuthorizationDecision(
            "FAIL", "TARGET_MANIFEST_HASH_MISMATCH", value.get("authorization_id"), (), 0, 0
        )
    if str(value.get("objective_sha256") or "").lower() != file_sha256(
        objective_path
    ).lower():
        return AuthorizationDecision(
            "FAIL", "OBJECTIVE_HASH_MISMATCH", value.get("authorization_id"), (), 0, 0
        )
    if str(value.get("component_bundle_sha256") or "").lower() != (
        component_bundle_sha256.lower()
    ):
        return AuthorizationDecision(
            "FAIL", "COMPONENT_BUNDLE_HASH_MISMATCH", value.get("authorization_id"), (), 0, 0
        )
    if str(value.get("target_sha256") or "").lower() != target.sha256.lower():
        return AuthorizationDecision(
            "FAIL", "TARGET_HASH_MISMATCH", value.get("authorization_id"), (), 0, 0
        )
    allowed_modes = set(value.get("allowed_execution_modes") or ())
    if execution_mode not in allowed_modes:
        return AuthorizationDecision(
            "FAIL", "EXECUTION_MODE_NOT_AUTHORIZED", value.get("authorization_id"), (), 0, 0
        )
    allowed_endpoints = tuple(value.get("allowed_endpoint_ids") or ())
    if set(requested_endpoint_ids) - set(allowed_endpoints):
        return AuthorizationDecision(
            "FAIL", "ENDPOINT_SCOPE_EXCEEDS_AUTHORIZATION", value.get("authorization_id"), (), 0, 0
        )
    if set(allowed_endpoints) - set(ENDPOINT_SPECS):
        return AuthorizationDecision(
            "FAIL",
            "AUTHORIZATION_CONTAINS_UNKNOWN_ENDPOINT",
            value.get("authorization_id"),
            (),
            0,
            0,
        )
    allowed_target_case_count = int(value.get("allowed_target_case_count") or 0)
    allowed_unique_cik_count = int(value.get("allowed_unique_cik_count") or 0)
    if allowed_target_case_count != requested_target_case_count:
        return AuthorizationDecision(
            "FAIL",
            "TARGET_CASE_COUNT_NOT_EXACTLY_AUTHORIZED",
            value.get("authorization_id"),
            (),
            0,
            0,
        )
    if allowed_unique_cik_count != requested_unique_cik_count:
        return AuthorizationDecision(
            "FAIL",
            "UNIQUE_CIK_COUNT_NOT_EXACTLY_AUTHORIZED",
            value.get("authorization_id"),
            (),
            0,
            0,
        )
    gates = value.get("conditional_gate_evidence") or {}
    for endpoint_id in set(requested_endpoint_ids).intersection(CONDITIONAL_ENDPOINT_IDS):
        evidence = gates.get(endpoint_id) or {}
        if evidence.get("status") != "PASS" or not evidence.get("manifest_sha256"):
            return AuthorizationDecision(
                "FAIL",
                f"CONDITIONAL_GATE_MISSING_{endpoint_id.upper()}",
                value.get("authorization_id"),
                (),
                0,
                0,
            )
    if not set(requested_endpoint_ids).issubset(
        set(DIRECT_ENDPOINT_IDS).union(CONDITIONAL_ENDPOINT_IDS)
    ):
        return AuthorizationDecision(
            "FAIL", "OBJECTIVE_ALLOWLIST_VIOLATION", value.get("authorization_id"), (), 0, 0
        )
    return AuthorizationDecision(
        "PASS",
        "HASH_BOUND_SCOPE_AND_LICENSE_AUTHORIZED",
        str(value.get("authorization_id")),
        allowed_endpoints,
        allowed_target_case_count,
        allowed_unique_cik_count,
    )
