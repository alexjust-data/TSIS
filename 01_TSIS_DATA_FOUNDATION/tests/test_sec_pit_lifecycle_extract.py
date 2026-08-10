from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.lifecycle_extract import (  # noqa: E402
    classify_item_301,
    extract_form25_fields,
    extract_table_security_mentions,
    identity_timing_state,
    item_301_section,
    parse_document,
    target_symbol_state,
)


def test_item_301_section_stops_before_next_item_and_classifies_transfer() -> None:
    text = (
        "Header Item 3.01 Notice of Delisting. The Company will voluntarily "
        "withdraw and transfer the listing to the New York Stock Exchange. "
        "Trading will commence on November 6, 2023. Item 5.03 Amendments."
    )
    section = item_301_section(text)

    assert section is not None
    assert "Item 5.03" not in section
    assert classify_item_301(section) == [
        "LISTING_TRANSFER",
        "VOLUNTARY_WITHDRAWAL",
    ]


def test_item_301_noncompliance_does_not_become_effective_delisting() -> None:
    section = (
        "Item 3.01 The Company received a deficiency notice because it failed "
        "to comply with the minimum bid price requirement."
    )
    assert classify_item_301(section) == [
        "CONTINUED_LISTING_NONCOMPLIANCE_NOTICE"
    ]


def test_form25_xml_fields_are_extracted_structurally() -> None:
    payload = b"""<?xml version="1.0"?>
    <notificationOfRemoval>
      <exchange><entityName>Nasdaq Stock Market LLC</entityName></exchange>
      <issuer><entityName>Brand Engagement Network Inc.</entityName></issuer>
      <descriptionClassSecurity>Unit</descriptionClassSecurity>
      <ruleProvision>17 CFR 240.12d2-2(a)(3)</ruleProvision>
      <signatureData><signatureDate>2024-03-15</signatureDate></signatureData>
    </notificationOfRemoval>"""
    soup, text, physical_format = parse_document(payload)
    result = extract_form25_fields(soup, text)

    assert physical_format == "XML"
    assert result["issuer_name_candidate"] == "Brand Engagement Network Inc."
    assert result["exchange_name_candidate"] == "Nasdaq Stock Market LLC"
    assert result["security_description_candidate"] == "Unit"
    assert result["rule_provision_candidate"] == "17 CFR 240.12d2-2(a)(3)"
    assert result["signature_date_candidate"] == "2024-03-15"


def test_registration_table_preserves_multiple_security_classes() -> None:
    payload = b"""
    <html><table>
      <tr><th>Title for each class to be so registered</th>
          <th>Name of each exchange on which each class is to be registered</th></tr>
      <tr><td>Common stock, par value $0.0001</td>
          <td>The New York Stock Exchange</td></tr>
      <tr><td>Warrants to purchase common stock</td>
          <td>The New York Stock Exchange</td></tr>
    </table></html>
    """
    soup, _, _ = parse_document(payload)
    mentions = extract_table_security_mentions(soup)

    assert len(mentions) == 2
    assert mentions[0]["security_title_candidate"].startswith("Common stock")
    assert mentions[1]["security_title_candidate"].startswith("Warrants")


def test_target_symbol_and_identity_timing_remain_explicit() -> None:
    mentions = [
        {
            "trading_symbol_candidate": "OSTK",
            "security_title_candidate": "Common Stock",
        }
    ]
    assert target_symbol_state("BBBY", mentions) == "OTHER_OR_PREDECESSOR_TICKER_MENTIONED"
    assert identity_timing_state("2023-10-24", "2025-09-01") == "PRE_OBSERVED_TARGET_INTERVAL"