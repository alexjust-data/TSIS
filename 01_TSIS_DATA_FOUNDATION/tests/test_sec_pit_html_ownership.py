from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.ownership_html import extract_html_ownership_snapshots  # noqa: E402


def _context(form: str) -> dict[str, object]:
    return {
        "cik": "0000000001",
        "accession_number": "0000000001-25-000001",
        "form": form,
        "accepted_at": "2025-04-01T16:00:00Z",
        "instrument_id": "instrument",
        "security_class_id": "class",
        "source_url": "https://example.test/filing",
        "source_sha256": "a" * 64,
        "availability_policy": EdgarAvailabilityPolicy(),
    }


def test_extract_proxy_ownership_rows_without_admitting_them() -> None:
    payload = b"""
    <table>
      <tr><th>Name of Beneficial Owner</th><th>Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Named Executive Officers</td></tr>
      <tr><td>Jane Doe (1)</td><td>1,200,000</td><td>12.5%</td></tr>
      <tr><td>5% Stockholders</td></tr>
      <tr><td>Example LLC (2)</td><td>900,000</td><td>9.4%</td></tr>
    </table>
    """
    rows = extract_html_ownership_snapshots(payload, **_context("DEF 14A"))
    assert [row.attributes["holder_name"] for row in rows] == ["Jane Doe", "Example LLC"]
    assert rows[0].attributes["holder_category"] == "OFFICER_OR_DIRECTOR"
    assert rows[1].attributes["holder_category"] == "FIVE_PERCENT_HOLDER"
    assert all(row.value is not None for row in rows)
    assert all(not row.quality_state.startswith("ADMITTED") for row in rows)


def test_extract_schedule_cover_sheet_and_preserve_overlap_inputs() -> None:
    payload = b"""
    <table>
      <tr><td>1. Names of Reporting Persons Example Holdings LLC</td></tr>
      <tr><td>2. Check the Appropriate Box if a Member of a Group</td></tr>
      <tr><td>7. Sole Voting Power 0</td></tr>
      <tr><td>8. Shared Voting Power 8,765,568</td></tr>
      <tr><td>9. Sole Dispositive Power 0</td></tr>
      <tr><td>10. Shared Dispositive Power 8,765,568</td></tr>
      <tr><td>11. Aggregate Amount Beneficially Owned by Each Reporting Person 8,765,568</td></tr>
      <tr><td>13. Percent of Class Represented by Amount in Row (11) 24.4%</td></tr>
    </table>
    """
    rows = extract_html_ownership_snapshots(payload, **_context("SC 13D"))
    assert len(rows) == 1
    assert rows[0].value == 8_765_568
    assert rows[0].attributes["reported_percent"] == 24.4
    assert rows[0].attributes["shared_voting_power"] == 8_765_568


def test_proxy_footnote_excludes_supported_option_component() -> None:
    payload = b"""
    <p>Beneficial ownership is determined according to SEC rules.</p>
    <table>
      <tr><th>Name of Beneficial Owner</th><th>Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Named Executive Officers</td></tr>
      <tr><td>Jane Doe (1)</td><td>1,200,000</td><td>12.5%</td></tr>
    </table>
    <p>* Represents beneficial ownership of less than 1%.</p>
    <p>(1) Includes 200,000 options to purchase shares of Common Stock.</p>
    <p>(1) Unrelated later section must not overwrite the ownership note.</p>
    """
    rows = extract_html_ownership_snapshots(payload, **_context("DEF 14A"))
    assert len(rows) == 1
    assert rows[0].attributes["footnote_marker"] == "1"
    assert rows[0].attributes["supported_issued_common_shares"] == 1_000_000
    assert rows[0].attributes["ownership_component_state"] == (
        "DERIVATIVE_COMPONENT_EXCLUDED_FROM_REPORTED_TOTAL"
    )

def test_proxy_prefers_transfer_agent_table_value_but_preserves_conflict() -> None:
    payload = b"""
    <p>Beneficial ownership is determined according to SEC rules.</p>
    <table>
      <tr><th>Name of Beneficial Owner</th><th>Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Named Executive Officers</td></tr>
      <tr><td>Jane Doe (1)</td><td>601,952</td><td>1.3%</td></tr>
    </table>
    <p>* Represents beneficial ownership of less than 1%.</p>
    <p>(1) Ownership is based off of the transfer agent report. Jane self-reported
    80,862 options and 751,952 shares, which the Company is reconciling with its records.</p>
    """
    row = extract_html_ownership_snapshots(payload, **_context("DEF 14A"))[0]
    assert row.attributes["supported_issued_common_shares"] == 601_952
    assert row.attributes["ownership_component_state"] == (
        "TRANSFER_AGENT_TABLE_VALUE_SELECTED_SOURCE_CONFLICT"
    )


def test_proxy_uses_explicit_common_component_when_reported_total_conflicts() -> None:
    payload = b"""
    <p>Beneficial ownership is determined according to SEC rules.</p>
    <table>
      <tr><th>Name of Beneficial Owner</th><th>Beneficially Owned</th><th>Percentage</th></tr>
      <tr><td>Directors and Named Executive Officers</td></tr>
      <tr><td>Jane Doe (1)</td><td>46,868</td><td>*</td></tr>
    </table>
    <p>* Represents beneficial ownership of less than 1%.</p>
    <p>(1) Includes 337,625 options to purchase shares of Common Stock and
    46,686 shares of Common Stock received in connection with resignation.</p>
    """
    row = extract_html_ownership_snapshots(payload, **_context("DEF 14A"))[0]
    assert row.attributes["supported_issued_common_shares"] == 46_686
    assert row.attributes["ownership_component_state"] == (
        "EXPLICIT_COMMON_COMPONENT_FROM_CONFLICTING_FOOTNOTE"
    )