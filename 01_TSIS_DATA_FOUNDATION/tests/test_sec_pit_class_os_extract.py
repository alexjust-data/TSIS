from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.class_os_extract import (  # noqa: E402
    admit_target_interval_document,
    extract_cover_page_class_os,
)


PAYLOAD = b"""
<html><body>
PANTAGES CAPITAL ACQUISITION CORPORATION
Class A ordinary shares, par value $0.0001 per share PGAC The Nasdaq Stock Market LLC
As of August 13, 2025, there were 8,869,250 of the registrant's Class A ordinary
shares, par value $0.0001 per share, and 2,156,250 of the registrant's Class B
ordinary shares, par value $0.0001 per share, issued and outstanding.
Basic and diluted weighted average shares outstanding 8,625,000.
</body></html>
"""


def test_target_interval_requires_registrant_and_class_ticker_table() -> None:
    decision = admit_target_interval_document(
        PAYLOAD,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        registrant_name="Pantages Capital Acquisition Corporation",
        ticker="PGAC",
        target_class_label="Class A ordinary shares",
    )
    assert decision.decision == "ADMITTED_PGAC_CLASS_A"
    assert decision.registrant_match is True
    assert decision.ticker_class_match is True


def test_prehistory_is_not_admitted_even_when_same_cik_payload_has_names() -> None:
    decision = admit_target_interval_document(
        PAYLOAD,
        temporal_scope_state="OPENING_STATE_PREHISTORY_CANDIDATE",
        accession_link_state="REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES",
        registrant_name="Pantages Capital Acquisition Corporation",
        ticker="PGAC",
        target_class_label="Class A ordinary shares",
    )
    assert decision.decision == "REJECT_AIFE_OR_OTHER_INSTRUMENT"


def test_class_os_extracts_class_a_not_class_b_or_weighted_average() -> None:
    rows = extract_cover_page_class_os(
        PAYLOAD,
        cik="0002030829",
        accession_number="a",
        form="10-Q",
        accepted_at="2025-08-14T20:00:00Z",
        instrument_id="cik_ticker:0002030829:PGAC",
        security_class_id=None,
        target_class_label="Class A ordinary shares",
        source_url="x",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert len(rows) == 1
    assert rows[0].value == 8_869_250
    assert rows[0].measurement_at == "2025-08-13"
    assert rows[0].attributes["security_class_label"] == "Class A ordinary shares"
    assert rows[0].eligible_from_session == "2025-08-15"


def test_missing_acceptance_preserves_candidate_but_blocks_causal_session() -> None:
    rows = extract_cover_page_class_os(
        PAYLOAD,
        cik="0002030829",
        accession_number="a",
        form="10-Q",
        accepted_at=None,
        instrument_id="cik_ticker:0002030829:PGAC",
        security_class_id=None,
        target_class_label="Class A ordinary shares",
        source_url="x",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert rows[0].eligible_from_session is None
    assert rows[0].causality_state == "AVAILABILITY_UNCERTAIN"
    assert rows[0].quality_state == "CANDIDATE_REQUIRES_ACCEPTANCE_TIMESTAMP"
