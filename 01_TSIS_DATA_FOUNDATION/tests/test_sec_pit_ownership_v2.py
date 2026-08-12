from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.holders_v2 import build_holder_position_ledger_v0_8  # noqa: E402
from sec_pit.ownership_class_reconcile import (  # noqa: E402
    reconcile_multiclass_proxy_positions,
)
from sec_pit.ownership_v2 import (  # noqa: E402
    _is_aggregate_management,
    extract_document_identity,
    extract_holder_class_components,
    extract_name_change_events,
    extract_normalized_ownership_snapshots,
    issuer_name_present_in_text,
)


def test_aggregate_management_recognizes_governed_language_variants() -> None:
    assert _is_aggregate_management(
        "Executive Officers and Directors as Group (13 persons)"
    )
    assert _is_aggregate_management(
        "Directors and officers as a group (6 persons)"
    )
    assert _is_aggregate_management(
        "All Directors, Director Nominees and NEOs as a Group (8 Persons)"
    )
    assert not _is_aggregate_management("Directors and Named Executive Officers")
    assert not _is_aggregate_management("Outside Fund and its directors as a group")


def context(form: str) -> dict[str, object]:
    return {
        "cik": "0000000001",
        "accession_number": "0000000001-25-000001",
        "form": form,
        "accepted_at": "2025-07-17T21:00:00Z",
        "instrument_id": "instrument",
        "security_class_id": None,
        "source_url": "https://example.test/filing",
        "source_sha256": "a" * 64,
        "availability_policy": EdgarAvailabilityPolicy(),
    }


def test_proxy_v04_parses_name_and_address_table_and_blocks_multiclass_sum() -> None:
    payload = b"""
    <p>The following table sets forth beneficial ownership of ordinary shares
    as of July 15, 2025. There are Class A ordinary shares and Class B ordinary shares.</p>
    <table>
      <tr><th>Name and Address of Beneficial Owner (1)</th><th></th>
          <th>Number of Shares Beneficially Owned</th><th></th>
          <th>Approximate Percentage of Outstanding Shares</th></tr>
      <tr><td>Jane Director</td><td></td><td>100</td><td></td><td>1.0</td><td>%</td></tr>
      <tr><td>All officers and directors as a group</td><td></td><td>100</td><td></td><td>1.0</td><td>%</td></tr>
      <tr><td>5% Holders</td></tr>
      <tr><td>Example Sponsor LLC (2)</td><td></td><td>900</td><td></td><td>9.0</td><td>%</td></tr>
    </table>
    <p>____________ (1) Address note. (2) Example Sponsor LLC is the sponsor;
    Controller Person has voting and investment discretion.</p>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert len(rows) == 3
    assert rows[0].measurement_at == "2025-07-15"
    assert rows[0].attributes["holder_category"] == "OFFICER_OR_DIRECTOR"
    assert rows[1].attributes["holder_category"] == "AGGREGATE_GROUP"
    assert rows[2].attributes["explicit_affiliate_candidate"] is True
    assert all(
        row.attributes["supported_issued_common_shares"] is None for row in rows
    )


def test_proxy_category_headers_classify_directors_before_five_percent_holders() -> None:
    payload = b"""
    <p>Beneficial ownership as of July 15, 2025.</p>
    <table>
      <tr><th>Name of Beneficial Owner</th><th>Shares Beneficially Owned</th></tr>
      <tr><td>Directors and Named Executive Officers</td></tr>
      <tr><td>Jane Director</td><td>100</td><td>1.0</td></tr>
      <tr><td>All current directors and executive officers as a group (2 persons)</td><td>100</td><td>1.0</td></tr>
      <tr><td>5% Stockholders</td></tr>
      <tr><td>Outside Fund LLC</td><td>900</td><td>9.0</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert [row.attributes["holder_category"] for row in rows] == [
        "OFFICER_OR_DIRECTOR",
        "AGGREGATE_GROUP",
        "FIVE_PERCENT_HOLDER",
    ]


def test_proxy_accepts_shares_beneficially_owned_multicolumn_header() -> None:
    payload = b"""
    <p>The table reports ownership as of July 6, 2022.</p>
    <table>
      <tr><th></th><th>Shares Beneficially Owned</th></tr>
      <tr><th>Title or Class of Securities:</th></tr>
      <tr><th></th><th>Common Stock</th><th>Preferred Stock</th></tr>
      <tr><th></th><th>Shares</th><th>Percent</th><th>Shares</th><th>Percent</th></tr>
      <tr><td>Directors:</td></tr>
      <tr><td>Jane Director</td><td></td><td>200</td><td>(1)</td><td>2.0</td></tr>
      <tr><td>All directors and executive officers as a group</td><td></td><td>200</td><td>(2)</td><td>2.0</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert [row.attributes["holder_name"] for row in rows] == [
        "Jane Director",
        "All directors and executive officers as a group",
    ]
    assert rows[0].measurement_at == "2022-07-06"
    assert rows[1].attributes["holder_category"] == "AGGREGATE_GROUP"


def test_proxy_tracks_separate_management_sections_and_named_aggregate() -> None:
    payload = b"""
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth information, as of July 6, 2022,
    regarding beneficial ownership of our voting securities.</p>
    <table>
      <tr><th></th><th>Shares Beneficially Owned</th></tr>
      <tr><th>Title or Class of Securities:</th></tr>
      <tr><th></th><th>Common Stock</th><th>Shares</th><th>Percent</th></tr>
      <tr><td>Directors:</td></tr>
      <tr><td>Jane Director</td><td>200</td><td>2.0</td></tr>
      <tr><td>Other Named Officers:</td></tr>
      <tr><td>John Officer</td><td>100</td><td>1.0</td></tr>
      <tr><td>All Example Company directors and executive officers as a group</td><td>300</td><td>3.0</td></tr>
      <tr><td>5% or greater stockholders</td></tr>
      <tr><td>Outside Fund</td><td>600</td><td>6.0</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert [row.attributes["holder_category"] for row in rows] == [
        "OFFICER_OR_DIRECTOR",
        "OFFICER_OR_DIRECTOR",
        "AGGREGATE_GROUP",
        "FIVE_PERCENT_HOLDER",
    ]


def test_proxy_accepts_number_of_common_shares_beneficially_owned_header() -> None:
    payload = b"""
    <p>Security Ownership as of December 31, 2024.</p>
    <table>
      <tr><th></th><th>Number of shares of Common Stock Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Officers:</td></tr>
      <tr><td>Jane Director (1)</td><td>4</td><td>*</td></tr>
      <tr><td>All directors and executive officers as a group (2 persons)</td><td>22</td><td>*</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert [row.value for row in rows] == [4, 22]
    assert rows[0].measurement_at == "2024-12-31"
    assert rows[1].attributes["holder_category"] == "AGGREGATE_GROUP"


def test_proxy_binds_date_to_ownership_table_not_prior_compensation_table() -> None:
    payload = b"""
    <p>The following compensation table reports awards as of December 31, 2024.</p>
    <table><tr><th>Option Awards</th></tr><tr><td>10</td></tr></table>
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth beneficial ownership of our common stock
    as of March 1, 2025.</p>
    <table>
      <tr><th>Beneficial Owner</th><th>Number of Shares of Common Stock Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Officers:</td></tr>
      <tr><td>Jane Director</td><td>4</td><td>*</td></tr>
      <tr><td>All directors and executive officers as a group (2 persons)</td><td>22</td><td>*</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert rows
    assert {row.measurement_at for row in rows} == {"2025-03-01"}


def test_proxy_keeps_owned_shares_and_uses_last_numeric_as_percent() -> None:
    payload = b"""
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth beneficial ownership of our common stock
    as of March 1, 2025.</p>
    <table>
      <tr><th>Beneficial Owner</th><th>Number of Shares of Common Stock Owned</th>
          <th>Acquirable Within 60 Days</th><th>Total Beneficially Owned</th>
          <th>Percentage</th></tr>
      <tr><td>Directors and Officers:</td></tr>
      <tr><td>All directors and executive officers as a group (10 persons) (18)</td>
          <td>1,400,094</td><td>2,172,129</td><td>3,572,223</td><td>3.92</td><td>%</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert len(rows) == 1
    assert rows[0].value == 1_400_094
    assert rows[0].attributes["supported_issued_common_shares"] == 1_400_094
    assert rows[0].attributes["reported_percent"] == 3.92


def test_proxy_rejects_unrelated_compensation_date_for_ownership_table() -> None:
    payload = b"""
    <p>Outstanding equity awards as of December 31, 2024.</p>
    <table><tr><th>Option Awards</th></tr><tr><td>10</td></tr></table>
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <table>
      <tr><th></th><th>Number of shares of Common Stock Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Officers:</td></tr>
      <tr><td>Jane Director</td><td>4</td><td>*</td></tr>
      <tr><td>All directors and executive officers as a group (2 persons)</td><td>22</td><td>*</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert rows
    assert {row.measurement_at for row in rows} == {None}


def test_proxy_resolves_explicit_document_record_date_referenced_by_table() -> None:
    payload = b"""
    <p>The Board fixed the close of business on April 12, 2023
    (the Record Date) for the annual meeting.</p>
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth beneficial ownership of our common stock
    as of the Record Date.</p>
    <table>
      <tr><th>Beneficial Owner</th><th>Shares Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>All directors and executive officers as a group (2 persons)</td><td>22</td><td>*</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert rows
    assert {row.measurement_at for row in rows} == {"2023-04-12"}


def test_proxy_rejects_ambiguous_document_record_dates() -> None:
    payload = b"""
    <p>The Board fixed April 12, 2023 (the Record Date).</p>
    <p>An amendment fixed April 13, 2023 (the Record Date).</p>
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth beneficial ownership as of the Record Date.</p>
    <table>
      <tr><th>Beneficial Owner</th><th>Shares Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>All directors and executive officers as a group</td><td>22</td><td>*</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert rows
    assert {row.measurement_at for row in rows} == {None}


def test_proxy_resolves_date_explicitly_bound_to_following_table() -> None:
    payload = b"""
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth information, as of July 6, 2022,
    regarding beneficial ownership of our common stock.</p>
    <table>
      <tr><th>Beneficial Owner</th><th>Shares Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>All directors and executive officers as a group</td><td>22</td><td>*</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert rows
    assert {row.measurement_at for row in rows} == {"2022-07-06"}


def test_proxy_normalizes_sec_header_whitespace_before_table_classification() -> None:
    payload = """
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth beneficial ownership as of March 18, 2024.</p>
    <table>
      <tr><th>Name\n and Address of Beneficial Owner</th><th>Number\u00a0of Shares</th><th>Percent</th></tr>
      <tr><td>Directors and Named Executive Officers:</td><td></td><td></td></tr>
      <tr><td>Jane Director</td><td>50,000</td><td>*</td></tr>
      <tr><td>All directors and officers as a group (1 individual)</td><td>50,000</td><td>*</td></tr>
    </table>
    """.encode("utf-8")
    rows = extract_normalized_ownership_snapshots(payload, **context("10-K"))
    aggregate = next(
        row for row in rows
        if row.attributes["holder_category"] == "AGGREGATE_GROUP"
    )
    assert aggregate.value == 50000
    assert aggregate.measurement_at == "2024-03-18"


def test_proxy_accepts_single_class_aggregate_table_without_owner_name_header() -> None:
    payload = b"""
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <p>The following table sets forth beneficial ownership as of April 7, 2023.</p>
    <table>
      <tr><th>Title of Class</th><th>Number of Shares Owned</th><th>Percentage</th></tr>
      <tr><td>Executive Officers and Directors:</td><td></td><td></td></tr>
      <tr><td>Jane Director Common Stock</td><td>125</td><td>1.2</td></tr>
      <tr><td>All current executive officers and directors as a group</td><td>125</td><td>1.2</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    aggregate = next(
        row for row in rows
        if row.attributes["holder_category"] == "AGGREGATE_GROUP"
    )
    assert aggregate.value == 125
    assert aggregate.attributes["table_class_basis"] == "SINGLE_OR_UNSPECIFIED"


def test_generic_single_class_family_stays_closed_for_multiclass_table() -> None:
    payload = b"""
    <p>Security Ownership of Certain Beneficial Owners and Management.</p>
    <table>
      <tr><th>Name</th><th>Class A Number of Shares</th><th>Class B Number of Shares</th><th>Percentage</th></tr>
      <tr><td>All directors and executive officers as a group</td><td>100</td><td>900</td><td>10.0</td></tr>
    </table>
    """
    rows = extract_normalized_ownership_snapshots(payload, **context("DEF 14A"))
    assert rows == []


def test_20f_share_ownership_table_emits_exact_multiclass_components() -> None:
    payload = """
    <p>E. Share Ownership</p>
    <p>The following table sets forth information with respect to the beneficial
    ownership of our Ordinary Shares as of the date of this annual report.</p>
    <table>
      <tr><th></th><th>Class A</th><th>Class B</th><th>% of Beneficial Ownership</th></tr>
      <tr><th></th><th>Ordinary Shares</th><th>Ordinary Shares</th><th></th></tr>
      <tr><td>Directors and Executive Officers:</td></tr>
      <tr><td>Jane Director (1)</td><td>200</td><td>800</td><td>10.0</td></tr>
      <tr><td>All directors and executive officers as a group:</td><td>200</td><td>800</td><td>10.0</td></tr>
      <tr><td>5% Shareholders:​</td></tr>
      <tr><td>Outside Fund Ltd (2)</td><td>900</td><td>-</td><td>9.0</td></tr>
    </table>
    """.encode("utf-8")
    rows = extract_normalized_ownership_snapshots(payload, **context("20-F"))
    assert len(rows) == 3
    assert rows[0].measurement_at == "2025-07-17"
    assert rows[0].attributes["measurement_date_basis"] == (
        "ANNUAL_REPORT_DATE_FROM_ACCEPTANCE_DATE"
    )
    assert rows[0].value == 1000
    assert rows[2].attributes["holder_category"] == "FIVE_PERCENT_HOLDER"
    components = extract_holder_class_components(payload, rows)
    reconciled, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[row.to_dict() for row in rows],
        class_components=components,
        target_class_label="Class A ordinary shares",
    )
    assert readout["row_level_class_allocation_complete"] is True
    assert readout["unresolved_aggregate_group_rows"] == 0
    jane = next(
        row for row in reconciled
        if row["attributes"]["holder_name"] == "Jane Director"
    )
    assert jane["attributes"]["supported_issued_common_shares"] == 200


def test_schedule_xml_uses_real_class_cusip_and_iso_measurement_date() -> None:
    payload = b"""<?xml version="1.0"?>
    <submission>
      <issuerInfo><issuerCik>1</issuerCik><issuerName>Example Corp</issuerName>
      <issuerCusip>A12345678</issuerCusip></issuerInfo>
      <securitiesClassTitle>Class A ordinary shares</securitiesClassTitle>
      <eventDateRequiresFilingThisStatement>06/30/2025</eventDateRequiresFilingThisStatement>
      <coverPageHeaderReportingPersonDetails>
        <reportingPersonName>Example Manager</reportingPersonName>
        <reportingPersonBeneficiallyOwnedAggregateNumberOfShares>500</reportingPersonBeneficiallyOwnedAggregateNumberOfShares>
        <classPercent>5.0</classPercent>
      </coverPageHeaderReportingPersonDetails>
    </submission>"""
    identity = extract_document_identity(payload)
    assert identity["issuer_cusip"] == "A12345678"
    assert identity["security_class_title"] == "Class A ordinary shares"
    rows = extract_normalized_ownership_snapshots(payload, **context("SCHEDULE 13G"))
    assert len(rows) == 1
    assert rows[0].measurement_at == "2025-06-30"
    assert rows[0].attributes["security_title"] == "Class A ordinary shares"


def proxy_row(name: str, shares: float, category: str, affiliate: bool = False) -> dict:
    return {
        "observation_id": name,
        "observation_type": "HOLDER_POSITION_SNAPSHOT",
        "instrument_id": "instrument",
        "security_class_id": None,
        "accession_number": "proxy",
        "form": "DEF 14A",
        "value": shares,
        "eligible_from_session": "2025-07-18",
        "source_sha256": "h",
        "quality_state": "CANDIDATE_REQUIRES_CLASS_ALLOCATION",
        "attributes": {
            "holder_name": name,
            "holder_category": category,
            "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
            "reported_percent": None,
            "supported_issued_common_shares": None,
            "explicit_affiliate_candidate": affiliate,
        },
    }


def component(name: str, title: str, shares: float, number: int) -> dict:
    return {
        "component_id": f"component-{number}",
        "holder_name": name,
        "security_class_title": title,
        "shares": shares,
        "eligible_from_session": "2025-01-01",
        "source_accession": f"source-{number}",
    }


def test_generic_exact_multiclass_reconciliation_has_no_ticker_constants() -> None:
    reconciled, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[
            proxy_row("Example Sponsor LLC", 900, "FIVE_PERCENT_HOLDER", True),
            proxy_row("Jane Director", 100, "OFFICER_OR_DIRECTOR"),
            proxy_row("All officers and directors as a group", 100, "AGGREGATE_GROUP"),
        ],
        class_components=[
            component("Example Sponsor LLC", "Class A ordinary shares", 200, 1),
            component("Example Sponsor LLC", "Class B ordinary shares", 700, 2),
            component("Jane Director", "Class B ordinary shares", 100, 3),
        ],
        target_class_label="Class A ordinary shares",
    )
    assert readout["row_level_class_allocation_complete"] is True
    assert readout["target_supported_excluded_share_candidates"] == 200
    sponsor = next(row for row in reconciled if row["attributes"]["holder_name"] == "Example Sponsor LLC")
    assert sponsor["attributes"]["holder_category"] == "EXPLICIT_AFFILIATE"
    assert sponsor["attributes"]["supported_issued_common_shares"] == 200
    director = next(row for row in reconciled if row["attributes"]["holder_name"] == "Jane Director")
    assert director["attributes"]["supported_issued_common_shares"] == 0
    ledger, dedup = build_holder_position_ledger_v0_8(reconciled)
    assert dedup["row_level_economic_position_resolution_complete"] is True
    assert sum(
        row["supported_issued_common_shares"]
        for row in ledger
        if row["methodology_relevant"]
    ) == 200


def test_multiclass_reconciliation_blocks_non_exact_allocation() -> None:
    _, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[proxy_row("Unresolved Holder", 900, "OFFICER_OR_DIRECTOR")],
        class_components=[component("Unresolved Holder", "Class A ordinary shares", 200, 1)],
        target_class_label="Class A ordinary shares",
    )
    assert readout["status"] == "FAIL"
    assert readout["unresolved_atomic_position_rows"] == 1


def test_name_change_extraction_is_generic() -> None:
    payload = (
        '<p>The shareholders approved a proposal to change the Company\'s name '
        'from "Old Issuer Ltd" to "New Issuer Ltd".</p>'
    ).encode()
    events = extract_name_change_events(payload)
    assert [(row["prior_name"], row["new_name"]) for row in events] == [
        ("Old Issuer Ltd", "New Issuer Ltd")
    ]

def test_issuer_name_presence_does_not_depend_on_sorted_token_adjacency() -> None:
    assert issuer_name_present_in_text(
        "Sample Acquisition Corp.",
        "This proxy statement of Sample Acquisition Corp concerns its meeting.",
    )
    assert not issuer_name_present_in_text(
        "Sample Acquisition Corp.",
        "This proxy concerns a different acquisition company.",
    )


def test_issuer_name_presence_ignores_vendor_security_and_jurisdiction_labels() -> None:
    assert issuer_name_present_in_text(
        "Altamira Therapeutics Ltd. Common Shares 0.01 SF (Bermuda)",
        "ALTAMIRA THERAPEUTICS LTD. annual report",
    )
    assert issuer_name_present_in_text(
        "ADEONA PHARMACEUTICALS INC (NV)",
        "Proxy Statement of Adeona Pharmaceuticals, Inc.",
    )


def test_issuer_core_name_match_does_not_admit_a_different_issuer() -> None:
    assert not issuer_name_present_in_text(
        "AGL Resources Inc Holding Co",
        "This annual report was filed by agilon health, inc.",
    )
    assert not issuer_name_present_in_text(
        "Velocity Acquisition Corp Common Stock",
        "This proxy statement was filed by VELO3D, Inc.",
    )


def test_name_change_extraction_accepts_real_filing_wording_and_curly_quotes() -> None:
    payload = (
        "<p>The company effected a name change from “First Issuer Inc.” to “Second Issuer Inc.”.</p>"
        "<p>The shareholders approved the proposal to amend the charter to change the "
        "Company’s name from ‘Second Issuer Inc.’ to ‘Third Issuer Inc.’.</p>"
    ).encode("utf-8")
    events = extract_name_change_events(payload)
    assert [(row["prior_name"], row["new_name"]) for row in events] == [
        ("First Issuer Inc.", "Second Issuer Inc."),
        ("Second Issuer Inc.", "Third Issuer Inc."),
    ]

def test_single_class_proxy_reconciliation_does_not_require_multiclass_components() -> None:
    row = proxy_row("Single Class Director", 125, "OFFICER_OR_DIRECTOR")
    row["attributes"]["supported_issued_common_shares"] = 125
    row["attributes"]["security_title"] = "Common Stock"
    row["attributes"]["table_class_basis"] = "SINGLE_OR_UNSPECIFIED"
    reconciled, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[row],
        class_components=[],
        target_class_label="Common Stock",
    )
    assert readout["status"] == "PASS_WITH_RESTRICTIONS"
    assert readout["row_level_class_allocation_complete"] is True
    assert readout["target_supported_excluded_share_candidates"] == 125
    assert reconciled[0]["quality_state"] == "ADMITTED_SINGLE_CLASS_PROXY_POSITION"
