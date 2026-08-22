# ruff: noqa: E402
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.authorization import validate_download_authorization


def test_authorization_cannot_include_a_security_class_halt(tmp_path: Path) -> None:
    manifest = tmp_path / "final_manifest.json"
    selection = tmp_path / "selection.parquet"
    authorization = tmp_path / "authorization.json"
    manifest.write_text('{"probe_gate":"PASS"}', encoding="utf-8")
    selection.write_bytes(b"selection")
    authorization.write_text(json.dumps({
        "status": "AUTHORIZED",
        "policy_id": "sec_pit_predownload_control_v0_2",
        "probe_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "selection_plan_sha256": hashlib.sha256(selection.read_bytes()).hexdigest(),
        "allowed_tickers": ["BNAI", "CNOBP"],
    }), encoding="utf-8")
    decision = validate_download_authorization(
        authorization,
        probe_manifest_path=manifest,
        selection_plan_path=selection,
        technically_eligible_tickers=["BNAI"],
    )
    assert decision.gate == "FAIL"
    assert decision.reason == "AUTHORIZED_SCOPE_EXCEEDS_TECHNICAL_GATE"


def test_authorization_is_bound_to_exact_probe_and_selection_hashes(tmp_path: Path) -> None:
    manifest = tmp_path / "final_manifest.json"
    selection = tmp_path / "selection.parquet"
    authorization = tmp_path / "authorization.json"
    manifest.write_text('{}', encoding="utf-8")
    selection.write_bytes(b"selection")
    authorization.write_text(json.dumps({
        "status": "AUTHORIZED",
        "policy_id": "sec_pit_predownload_control_v0_2",
        "probe_manifest_sha256": "wrong",
        "selection_plan_sha256": hashlib.sha256(selection.read_bytes()).hexdigest(),
        "allowed_tickers": ["BNAI"],
    }), encoding="utf-8")
    decision = validate_download_authorization(
        authorization,
        probe_manifest_path=manifest,
        selection_plan_path=selection,
        technically_eligible_tickers=["BNAI"],
    )
    assert decision.reason == "PROBE_MANIFEST_HASH_MISMATCH"


def test_authorization_is_bound_to_exact_gate_matrix_hash(tmp_path: Path) -> None:
    manifest = tmp_path / "final_manifest.json"
    selection = tmp_path / "selection.parquet"
    gates = tmp_path / "gate_matrix.parquet"
    authorization = tmp_path / "authorization.json"
    manifest.write_text('{"probe_gate":"PASS"}', encoding="utf-8")
    selection.write_bytes(b"selection")
    gates.write_bytes(b"gates")
    authorization.write_text(json.dumps({
        "status": "AUTHORIZED",
        "policy_id": "sec_pit_predownload_control_v0_2",
        "probe_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "selection_plan_sha256": hashlib.sha256(selection.read_bytes()).hexdigest(),
        "gate_matrix_sha256": "wrong",
        "allowed_tickers": ["BNAI"],
    }), encoding="utf-8")
    decision = validate_download_authorization(
        authorization,
        probe_manifest_path=manifest,
        selection_plan_path=selection,
        gate_matrix_path=gates,
        technically_eligible_tickers=["BNAI"],
    )
    assert decision.gate == "FAIL"
    assert decision.reason == "GATE_MATRIX_HASH_MISMATCH"
