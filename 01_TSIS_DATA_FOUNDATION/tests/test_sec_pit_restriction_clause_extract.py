from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.restriction_clause_extract import (  # noqa: E402
    extract_restriction_clause_candidates,
)


def test_restriction_clauses_are_neutral_evidence_not_tradability() -> None:
    payload = b"""
    <html><body>
    The Company entered into a share assignment and lockup release agreement.
    These securities are restricted securities under Rule 144. The holder may
    request removal of the restrictive legend from the transfer agent.
    We filed one or more registration statements to provide for the resale by
    selling holders.
    </body></html>
    """
    rows = extract_restriction_clause_candidates(
        payload,
        cik="1",
        accession_number="a",
        form="10-Q",
        accepted_at="2024-09-25T21:18:30Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    types = {row.attributes["restriction_clause_type"] for row in rows}
    assert "LOCKUP_RELEASE_AGREEMENT_REPORTED" in types
    assert "RESTRICTED_SECURITIES_RULE_144_REPORTED" in types
    assert "RESTRICTIVE_LEGEND_CONDITION_REPORTED" in types
    assert "RESALE_REGISTRATION_FILED_LANGUAGE" in types
    assert all(not row.attributes["tradable_supply_confirmation"] for row in rows)
    assert all(row.value is None for row in rows)


def test_effect_is_not_parsed_as_a_narrative_restriction_clause() -> None:
    rows = extract_restriction_clause_candidates(
        b"<xml>lockup release agreement</xml>",
        cik="1",
        accession_number="a",
        form="EFFECT",
        accepted_at="2024-09-25T21:18:30Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert rows == []
