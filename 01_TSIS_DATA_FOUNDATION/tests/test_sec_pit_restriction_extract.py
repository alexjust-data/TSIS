from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.restriction_extract import (  # noqa: E402
    extract_effect_event,
    extract_registration_component_candidate,
    extract_registration_scope_clause_candidates,
    extract_selling_holder_share_lots,
    reconcile_registration_to_selling_lots,
    summarize_registration_component_conflicts,
)


def test_effect_is_eligibility_evidence_not_tradable_supply() -> None:
    payload = b"""<?xml version="1.0"?>
    <edgarSubmission><effectiveData>
      <finalEffectivenessDispDate>2024-04-25</finalEffectivenessDispDate>
      <finalEffectivenessDispTime>16:00:00</finalEffectivenessDispTime>
      <form>S-1</form><filer><fileNumber>333-278673</fileNumber></filer>
    </effectiveData></edgarSubmission>"""
    rows = extract_effect_event(
        payload,
        cik="0001838163",
        accession_number="a",
        form="EFFECT",
        accepted_at="2024-04-26T04:15:08Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert len(rows) == 1
    assert rows[0].attributes["restriction_event_type"] == "RESALE_REGISTRATION_EFFECTIVE"
    assert rows[0].attributes["tradable_supply_confirmation"] is False
    assert rows[0].value is None


def test_424b3_preserves_mixed_registration_components_without_tradability_claim() -> None:
    payload = b"""
    <html><body>
    Filed Pursuant to Rule 424(b)(3) Registration No. 333-278673
    BRAND ENGAGEMENT NETWORK INC.
    46,752,838 Shares of Common Stock
    (Inclusive of 21,190,316 Shares of Common Stock Underlying Warrants,
    1,583,334 Shares of Common Stock Underlying Convertible Notes and
    163,407 Shares of Common Stock Underlying Options)
    This prospectus relates to up to 23,815,781 shares of our common stock
    held by certain existing stockholders and up to 6,126,010 shares of
    Common Stock that may be issued upon exercise of warrants.
    </body></html>
    """
    rows = extract_registration_component_candidate(
        payload,
        cik="0001838163",
        accession_number="a",
        form="424B3",
        accepted_at="2024-04-25T21:01:24Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.value == 46_752_838
    assert row.attributes["file_number"] == "333-278673"
    assert row.attributes["cover_underlying_warrant_shares"] == 21_190_316
    assert row.attributes["cover_underlying_convertible_note_shares"] == 1_583_334
    assert row.attributes["cover_underlying_option_shares"] == 163_407
    assert row.attributes["tradable_supply_confirmation"] is False
    assert row.quality_state == "MIXED_REGISTRATION_REQUIRES_SHARE_LOT_LINKAGE"


def test_424b3_supplement_does_not_promote_underlying_component_to_cover_total() -> None:
    payload = b"""
    <html><body>
    Prospectus Supplement No. 14 Filed Pursuant to Rule 424(b)(3)
    Registration No. 333-280366 BRAND ENGAGEMENT NETWORK INC.
    6,393,333 Shares of Common Stock
    (Inclusive of 4,200,000 Shares of Common Stock Underlying Warrants)
    </body></html>
    """
    rows = extract_registration_component_candidate(
        payload,
        cik="0001838163",
        accession_number="supplement",
        form="424B3",
        accepted_at="2026-01-28T00:38:06Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert len(rows) == 1
    assert rows[0].value == 6_393_333
    assert rows[0].attributes["cover_underlying_warrant_shares"] == 4_200_000


def test_registration_component_conflicts_ignore_missing_but_preserve_disagreement() -> None:
    rows = [
        {"attributes": {"file_number": "333-1", "cover_underlying_warrant_shares": 21_190_316}},
        {"attributes": {"file_number": "333-1", "cover_underlying_warrant_shares": None}},
        {"attributes": {"file_number": "333-1", "cover_underlying_warrant_shares": 2_119_016}},
    ]
    conflicts = summarize_registration_component_conflicts(rows)
    assert conflicts == {"333-1": {"cover_underlying_warrant_shares": [2_119_016.0, 21_190_316.0]}}


def test_selling_holder_table_is_neutral_share_lot_evidence() -> None:
    payload = b"""
    <html><body>
    Registration No. 333-282132
    <table>
      <tr><td></td><td>Number of Shares of Common Stock Beneficially Owned</td>
          <td>Maximum Number of Shares of Common Stock Being Offered</td>
          <td>Shares of Common Stock Beneficially Owned After Sale</td></tr>
      <tr><td>Name of Selling Holder</td><td>Number</td><td>Offered</td><td>Number</td></tr>
      <tr><td>YA II PN, LTD. (4)</td><td>280,899</td><td>28,370,786</td><td>-</td></tr>
    </table>
    </body></html>
    """
    rows = extract_selling_holder_share_lots(
        payload,
        cik="0001838163",
        accession_number="a",
        form="424B3",
        accepted_at="2024-09-25T21:18:30Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.attributes["holder_name"] == "YA II PN, LTD."
    assert row.attributes["beneficial_common_shares_before"] == 280_899
    assert row.attributes["maximum_common_shares_offered"] == 28_370_786
    assert row.attributes["offered_exceeds_current_beneficial"] is True
    assert row.attributes["issued_common_classification"] == "UNRESOLVED"
    assert row.attributes["tradable_supply_confirmation"] is False


def test_registration_to_selling_lot_reconciliation_preserves_mismatch() -> None:
    registrations = [
        {"attributes": {"file_number": "333-1", "cover_total_registered_common_shares": 100}}
    ]
    lots = [
        {
            "accession_number": "a",
            "attributes": {"file_number": "333-1", "maximum_common_shares_offered": 40},
        },
        {
            "accession_number": "a",
            "attributes": {"file_number": "333-1", "maximum_common_shares_offered": 50},
        },
    ]
    result = reconcile_registration_to_selling_lots(registrations, lots)
    assert result["333-1"]["status"] == "MISMATCH"
    assert result["333-1"]["minimum_absolute_difference"] == 10
    registrations[0]["attributes"]["includes_issuer_issuance_scope"] = True
    result = reconcile_registration_to_selling_lots(registrations, lots)
    assert result["333-1"]["status"] == "PARTIAL_MATCH_MIXED_ISSUER_ISSUANCE"
    registrations[0]["attributes"]["includes_issuer_issuance_scope"] = False
    lots.append(
        {
            "accession_number": "b",
            "attributes": {"file_number": "333-1", "maximum_common_shares_offered": 100},
        }
    )
    result = reconcile_registration_to_selling_lots(registrations, lots)
    assert result["333-1"]["status"] == "EXACT_MATCH"
    assert result["333-1"]["matching_accessions"] == ["b"]


def test_registration_scope_clauses_separate_held_issued_and_future_shares() -> None:
    payload = b"""
    <html><body>Registration No. 333-000001
    This prospectus relates to 100 shares of our Common Stock held by existing holders,
    200 shares of Common Stock that we may, at our discretion, elect to issue and
    30 shares of Common Stock issued to the investor as commitment shares.
    The shares are collectively referred to in this prospectus as offered securities.
    </body></html>
    """
    rows = extract_registration_scope_clause_candidates(
        payload,
        cik="1",
        accession_number="a",
        form="424B3",
        accepted_at="2024-09-25T21:18:30Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    by_value = {int(row.value): row.attributes for row in rows}
    assert by_value[100]["component_classification"] == "REPORTED_HELD"
    assert by_value[200]["component_classification"] == "CONTINGENT_OR_FUTURE"
    assert by_value[200]["issued_common_state"] == "NOT_CURRENT_ISSUED_COMMON"
    assert by_value[30]["component_classification"] == "REPORTED_ISSUED"
    assert all(not row.attributes["tradable_supply_confirmation"] for row in rows)


def test_registration_scope_prioritizes_underlying_over_issued_wording() -> None:
    payload = b"""
    <html><body>Registration No. 333-000002
    This prospectus relates to 1,583,334 shares of Common Stock issuable upon
    exercise of a convertible note issued to the holder, 960,000 shares of
    Common Stock underlying warrants that may be issued upon exercise, and
    93,333 shares of Common Stock held by October 3 Holdings which shares were
    issued pursuant to a debt conversion agreement.
    We will not receive any of the proceeds.
    </body></html>
    """
    rows = extract_registration_scope_clause_candidates(
        payload,
        cik="1",
        accession_number="a",
        form="424B3",
        accepted_at="2024-09-25T21:18:30Z",
        instrument_id="i",
        security_class_id="s",
        source_url="u",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    by_value = {int(row.value): row for row in rows}
    assert by_value[1_583_334].attributes["component_classification"] == ("CONTINGENT_OR_FUTURE")
    assert by_value[960_000].attributes["component_classification"] == ("CONTINGENT_OR_FUTURE")
    assert by_value[93_333].attributes["component_classification"] == ("REPORTED_ISSUED")
    assert all(row.extraction_method == "SEC_424B3_REGISTRATION_SCOPE_CLAUSE_V0_2" for row in rows)
