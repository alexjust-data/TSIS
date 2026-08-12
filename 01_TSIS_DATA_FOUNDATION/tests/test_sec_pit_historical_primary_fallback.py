from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.run_authorized_primary_acquisition_v0_2 import complete_submission_fallback_url


def test_fallback_is_bound_to_same_cik_and_accession() -> None:
    row = {"cik": "0000887247", "accession_number": "0000891836-00-000470"}
    assert complete_submission_fallback_url(row) == (
        "https://www.sec.gov/Archives/edgar/data/887247/"
        "000089183600000470/0000891836-00-000470.txt"
    )


def test_fallback_rejects_missing_identity() -> None:
    with pytest.raises(ValueError):
        complete_submission_fallback_url({"cik": "", "accession_number": "x"})


def test_fallback_derives_cik_from_authorized_primary_url() -> None:
    row = {
        "accession_number": "0000891836-00-000470",
        "primary_document_url": (
            "https://www.sec.gov/Archives/edgar/data/887247/"
            "000089183600000470/0001.txt"
        ),
    }
    assert complete_submission_fallback_url(row).endswith(
        "/887247/000089183600000470/0000891836-00-000470.txt"
    )
