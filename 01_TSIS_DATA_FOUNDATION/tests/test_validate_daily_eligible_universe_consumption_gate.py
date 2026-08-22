from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder_tests = _load_module(
    "daily_eligible_universe_builder_tests",
    Path(__file__).with_name("test_daily_eligible_universe_consumption_gate.py"),
)
validator = _load_module(
    "daily_eligible_universe_validator",
    SCRIPTS / "validate_daily_eligible_universe_consumption_gate.py",
)


def test_independent_validator_accepts_fixture_gate(tmp_path: Path) -> None:
    config = builder_tests._write_fixture(tmp_path)
    output = tmp_path / "run"
    result = builder_tests.gate.build(config, output, "fixture-run", 1, "1GB")
    assert result["status"] == "PASS"

    validation = validator.validate(config, output)
    assert validation["validation_gate"] == "PASS"
    assert validation["interval_metrics"]["physical_rows"] == 1
    assert validation["interval_metrics"]["logical_symbol_seconds"] == 23399


def test_independent_validator_detects_manifest_tamper(tmp_path: Path) -> None:
    config = builder_tests._write_fixture(tmp_path)
    output = tmp_path / "run"
    builder_tests.gate.build(config, output, "fixture-run", 1, "1GB")
    final_path = output / "final_manifest.json"
    final = json.loads(final_path.read_text(encoding="utf-8"))
    final["consumption_manifest_sha256"] = "0" * 64
    final_path.write_text(json.dumps(final), encoding="utf-8")

    validation = validator.validate(config, output)
    assert validation["validation_gate"] == "FAIL"
    assert not validation["checks"]["consumption_manifest_hash_matches_final"]
