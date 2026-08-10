from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.historical_cusip import (  # noqa: E402
    extract_cusips,
    is_valid_cusip,
    resolve_cusip_intervals,
)


def test_checksum_rejects_narrative_false_positives() -> None:
    assert is_valid_cusip("104932108")
    assert is_valid_cusip("104932207")
    assert is_valid_cusip("G2758T109")
    assert not is_valid_cusip("NUMBERFOR")
    assert not is_valid_cusip("SEPTEMBER")


def test_extracts_spaced_cusip_from_narrative() -> None:
    text = "The CUSIP number for the Common Stock will be 104932 207."
    assert extract_cusips(text) == ["104932207"]


def test_resolver_excludes_pre_instrument_observation_and_uses_split_date() -> None:
    observations = [
        {
            "cusip": "G2758T109",
            "filing_date": "2024-02-14",
            "eligible_from_session": "2024-02-15",
            "accession_number": "pre",
            "form": "SC 13G",
        },
        {
            "cusip": "104932108",
            "filing_date": "2024-07-26",
            "eligible_from_session": "2024-07-29",
            "accession_number": "old",
            "form": "SC 13D",
        },
        {
            "cusip": "104932207",
            "filing_date": "2025-12-01",
            "eligible_from_session": "2025-12-02",
            "accession_number": "new",
            "form": "8-K",
        },
    ]
    split = [
        {
            "action_type": "split",
            "source_system": "reference",
            "within_instrument_valid_window": True,
            "action_date": "2025-12-12",
        }
    ]
    rows, readout = resolve_cusip_intervals(
        observations, "2024-03-15", "2026-03-09", split, "104932"
    )
    assert [row["cusip"] for row in rows] == ["104932108", "104932207"]
    assert rows[0]["effective_from"] == "2024-07-29"
    assert rows[0]["effective_to"] == "2025-12-11"
    assert rows[1]["effective_from"] == "2025-12-12"
    assert readout["pre_first_evidence_state"] == "CUSIP_UNAVAILABLE"
