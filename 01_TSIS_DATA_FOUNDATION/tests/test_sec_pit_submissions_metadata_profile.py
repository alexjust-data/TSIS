from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.run_submissions_metadata_profile import (  # noqa: E402
    profile_inventory,
    require_canonical_object_root,
)


def test_profile_inventory_tags_document_strata() -> None:
    rows = []
    for index in range(55):
        rows.append({"form": "4", "filing_date": f"2025-01-{index % 28 + 1:02d}", "items": ""})
    rows.extend([
        {"form": "20-F", "filing_date": "2008-01-01", "items": ""},
        {"form": "20-F/A", "filing_date": "2008-02-01", "items": ""},
        {"form": "20-F/A", "filing_date": "2008-03-01", "items": ""},
        {"form": "8-K", "filing_date": "2024-01-01", "items": "1.03,2.01"},
    ])
    result = profile_inventory("TEST", "0000000001", pd.DataFrame(rows))
    assert result["form4_count"] == 55
    assert result["twenty_f_amendment_count"] == 2
    assert "MANY_FORM4" in result["document_strata_json"]
    assert "FOREIGN_20F_MULTIPLE_AMENDMENTS" in result["document_strata_json"]
    assert "BANKRUPTCY_OR_RECEIVERSHIP_ITEM_1_03" in result["document_strata_json"]


def test_metadata_runner_rejects_noncanonical_object_root(tmp_path: Path) -> None:
    canonical = tmp_path / "active" / "objects"
    canonical.mkdir(parents=True)
    assert require_canonical_object_root(canonical, canonical) == canonical.resolve()
    wrong = tmp_path / "legacy" / "raw"
    wrong.mkdir(parents=True)
    try:
        require_canonical_object_root(wrong, canonical)
    except ValueError as exc:
        assert "governed active SEC PIT content store" in str(exc)
    else:
        raise AssertionError("noncanonical object root was accepted")
