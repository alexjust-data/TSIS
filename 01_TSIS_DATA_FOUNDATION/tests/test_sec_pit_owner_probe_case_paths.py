from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.build_owner_exclusion_stratified_probe import load_cases


def test_owner_probe_loads_frozen_cases_with_class_override(tmp_path: Path) -> None:
    path = tmp_path / "cases.json"
    path.write_text('[{"ticker":"A","temporal_cohort":"2005_2008"},{"ticker":"P"}]', encoding="utf-8")
    cases = load_cases({
        "cases_path": str(path), "default_expected_security_class_gate": "PASS",
        "expected_security_class_gate_overrides": {"P": "FAIL"},
    })
    assert cases[0]["stratum"] == "2005_2008"
    assert cases[0]["target_class_label"] == "COMMON_STOCK_CLASS_CANDIDATE"
    assert [case["expected_security_class_gate"] for case in cases] == ["PASS", "FAIL"]
