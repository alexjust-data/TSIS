from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.assignment_restriction_extract import (  # noqa: E402
    extract_assignment_restriction_events,
)
from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402


def test_assignment_events_preserve_numeric_conflict_without_correction() -> None:
    payload = b"""
    <html><body>Assignment Agreement On August 26, 2024 (the Assignment Effective Date),
    the Company entered into a share assignment and lockup release agreement.
    Purchasers assumed an aggregate of 1,185,000 shares of Common Stock (the Sponsor Securities).
    The Company agreed to release 1,252,500 shares of Common Stock from certain restrictions.
    Within five business days the Sponsor Members will transfer an aggregate of 50,000 Sponsor Securities
    and the remaining 1,1350,000 Sponsor Securities into the Share Escrow Account.
    Sponsor Members agreed from August 26, 2024 until the earliest of (i) March 14, 2025 and (ii)
    a merger not to Transfer an amount representing more than 25% of the average daily trading volume.
    Standby Equity Purchase Agreement</body></html>
    """
    rows = extract_assignment_restriction_events(
        payload,
        cik="1",
        accession_number="a",
        form="8-K",
        accepted_at="2024-08-26T21:00:00Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    by_type = {row.attributes["restriction_event_type"]: row for row in rows}
    assert by_type["SPONSOR_SECURITIES_ASSIGNMENT_REPORTED"].value == 1_185_000
    assert by_type["LOCKUP_RELEASE_COMMITMENT_REPORTED"].value == 1_252_500
    escrow = by_type["SPONSOR_ESCROW_CONDITIONAL_RELEASE"]
    assert escrow.value is None
    assert escrow.attributes["reported_numeric_value"] == 11_350_000
    assert escrow.attributes["implied_remainder_value"] == 1_135_000
    assert escrow.attributes["source_numeric_conflict"] is True
    assert escrow.quality_state == "SOURCE_NUMERIC_CONFLICT"
    assert escrow.effective_at == "2024-08-26"
    volume_restriction = by_type["SPONSOR_TRANSFER_VOLUME_RESTRICTION"]
    assert volume_restriction.attributes["scheduled_end_date"] == "2025-03-14"
    assert all(not row.attributes["tradable_supply_confirmation"] for row in rows)
