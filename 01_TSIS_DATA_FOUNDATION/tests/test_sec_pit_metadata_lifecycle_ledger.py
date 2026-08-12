from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.build_metadata_lifecycle_ledger import lifecycle_row


def test_metadata_lifecycle_never_promotes_legal_dates() -> None:
    case = {"ticker": "TEST", "cik": "0000000001", "instrument_id": "i", "security_class_id": "s", "first_seen_date": "2005-01-01", "last_observed_date": "2025-01-01"}
    inventory = pd.DataFrame([
        {"form": "8-A12B", "filing_date": "2005-01-01", "items": ""},
        {"form": "8-K", "filing_date": "2024-01-01", "items": "3.01"},
        {"form": "25-NSE", "filing_date": "2024-02-01", "items": ""},
    ])
    row = lifecycle_row(case, inventory)
    assert row["sec_legal_list_date"] is None
    assert row["sec_legal_delist_date"] is None
    assert row["sec_registration_candidate_count"] == 1
    assert row["sec_delisting_candidate_count"] == 1
    assert "FORM_25_METADATA_CANDIDATE" in row["sec_boundary_state"]
