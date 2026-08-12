from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.build_predownload_control import inventory_path, load_cases


def test_inventory_template_and_expected_class_override(tmp_path: Path) -> None:
    cases = tmp_path / "cases.json"
    cases.write_text('[{"ticker":"A"},{"ticker":"PREF"}]', encoding="utf-8")
    config = {
        "cases_path": str(cases),
        "metadata_inventory_template": str(tmp_path / "{ticker_lower}" / "filing_inventory.parquet"),
        "default_expected_class_gate": "PASS",
        "expected_class_gate_overrides": {"PREF": "FAIL"},
    }
    loaded = load_cases(config)
    assert [row["expected_class_gate"] for row in loaded] == ["PASS", "FAIL"]
    assert inventory_path(config, "ABC") == tmp_path / "abc" / "filing_inventory.parquet"
