# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.massive_sec_authorization import (
    FrozenTarget,
    validate_authorization,
    validate_config,
)
from sec_pit.massive_sec_storage import file_sha256


def _fixtures(tmp_path: Path) -> tuple[Path, Path, Path, FrozenTarget]:
    config = tmp_path / "config.json"
    target_manifest = tmp_path / "target_manifest.json"
    objective = tmp_path / "objective.md"
    target_data = tmp_path / "target.parquet"
    config.write_text('{"config_id":"test"}', encoding="utf-8")
    target_manifest.write_text('{"target_id":"test"}', encoding="utf-8")
    objective.write_text("# Objective\n", encoding="utf-8")
    target_data.write_bytes(b"frozen-target")
    target = FrozenTarget(
        path=target_data,
        sha256=file_sha256(target_data),
        row_count=4_824,
        unique_ticker_count=4_824,
        unique_instrument_count=4_626,
        unique_cik_count=4_288,
    )
    return config, target_manifest, objective, target


def _authorized_value(
    config: Path,
    target_manifest: Path,
    objective: Path,
    target: FrozenTarget,
) -> dict[str, object]:
    return {
        "authorization_id": "test-authorization",
        "status": "AUTHORIZED",
        "authorized_by": "human",
        "authorized_at_utc": "2026-08-22T00:00:00Z",
        "authorization_basis": "bounded probe approval",
        "authorization_scope": "PROBE_ONLY",
        "config_sha256": file_sha256(config),
        "target_manifest_sha256": file_sha256(target_manifest),
        "target_sha256": target.sha256,
        "objective_sha256": file_sha256(objective),
        "component_bundle_sha256": "c" * 64,
        "allowed_execution_modes": ["PROBE"],
        "allowed_endpoint_ids": ["edgar_index"],
        "allowed_target_case_count": 250,
        "allowed_unique_cik_count": 247,
        "license_retention_confirmation": {
            "status": "CONFIRMED",
            "confirmed_by": "human",
            "confirmed_at_utc": "2026-08-22T00:00:00Z",
            "evidence_reference": "written-license-evidence",
        },
        "conditional_gate_evidence": {},
    }


def _decision(
    authorization: Path,
    config: Path,
    target_manifest: Path,
    objective: Path,
    target: FrozenTarget,
    *,
    endpoint_ids: tuple[str, ...] = ("edgar_index",),
):
    return validate_authorization(
        authorization,
        config_path=config,
        target_manifest_path=target_manifest,
        objective_path=objective,
        component_bundle_sha256="c" * 64,
        target=target,
        requested_endpoint_ids=endpoint_ids,
        execution_mode="PROBE",
        requested_target_case_count=250,
        requested_unique_cik_count=247,
    )


def test_pending_authorization_fails_before_network(tmp_path: Path) -> None:
    config, target_manifest, objective, target = _fixtures(tmp_path)
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps({"authorization_id": "pending", "status": "PENDING_HUMAN_AUTHORIZATION"}),
        encoding="utf-8",
    )

    decision = _decision(authorization, config, target_manifest, objective, target)

    assert decision.gate == "FAIL"
    assert decision.reason == "AUTHORIZATION_STATUS_NOT_AUTHORIZED"


def test_license_and_retention_confirmation_is_mandatory(tmp_path: Path) -> None:
    config, target_manifest, objective, target = _fixtures(tmp_path)
    value = _authorized_value(config, target_manifest, objective, target)
    value["license_retention_confirmation"] = {"status": "PENDING"}
    authorization = tmp_path / "authorization.json"
    authorization.write_text(json.dumps(value), encoding="utf-8")

    assert _decision(
        authorization, config, target_manifest, objective, target
    ).reason == "LICENSE_RETENTION_NOT_CONFIRMED"


def test_authorization_is_bound_to_executable_bundle_hash(tmp_path: Path) -> None:
    config, target_manifest, objective, target = _fixtures(tmp_path)
    value = _authorized_value(config, target_manifest, objective, target)
    value["component_bundle_sha256"] = "wrong"
    authorization = tmp_path / "authorization.json"
    authorization.write_text(json.dumps(value), encoding="utf-8")

    assert _decision(
        authorization, config, target_manifest, objective, target
    ).reason == "COMPONENT_BUNDLE_HASH_MISMATCH"


def test_exact_probe_scope_can_pass(tmp_path: Path) -> None:
    config, target_manifest, objective, target = _fixtures(tmp_path)
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(_authorized_value(config, target_manifest, objective, target)),
        encoding="utf-8",
    )

    decision = _decision(authorization, config, target_manifest, objective, target)

    assert decision.gate == "PASS"
    assert decision.allowed_target_case_count == 250
    assert decision.allowed_unique_cik_count == 247


def test_conditional_endpoint_needs_separate_gate_evidence(tmp_path: Path) -> None:
    config, target_manifest, objective, target = _fixtures(tmp_path)
    value = _authorized_value(config, target_manifest, objective, target)
    value["allowed_endpoint_ids"] = ["eight_k_text"]
    authorization = tmp_path / "authorization.json"
    authorization.write_text(json.dumps(value), encoding="utf-8")

    decision = _decision(
        authorization,
        config,
        target_manifest,
        objective,
        target,
        endpoint_ids=("eight_k_text",),
    )

    assert decision.reason == "CONDITIONAL_GATE_MISSING_EIGHT_K_TEXT"


def test_governed_config_has_no_credentials_and_rejects_13f() -> None:
    config_path = ROOT / "configs" / "massive_sec_acquisition_v0_1.json"
    config = validate_config(config_path)

    assert config["api_key_source"] == "ENV:MASSIVE_API_KEY"
    assert "form_13f" not in config["endpoint_ids"]
