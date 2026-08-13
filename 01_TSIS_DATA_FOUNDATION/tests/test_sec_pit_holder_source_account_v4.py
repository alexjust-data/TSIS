from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.holders_v4 import build_holder_position_ledger_v0_10  # noqa: E402


def position(footnotes: list[str]) -> dict:
    return {
        "observation_id": "position",
        "observation_type": "HOLDER_POSITION_SNAPSHOT",
        "instrument_id": "instrument",
        "security_class_id": "class",
        "accession_number": "accession",
        "form": "4",
        "value": 1_972_783.0,
        "eligible_from_session": "2022-06-09",
        "source_sha256": "sha",
        "quality_state": "CANDIDATE_REQUIRES_HOLDER_DEDUPLICATION",
        "attributes": {
            "holder_cik": "1273871",
            "holder_name": "PORTNOY ADAM D.",
            "holding_type": "NON_DERIVATIVE",
            "direct_or_indirect": "I",
            "security_title": "Common Stock",
            "nature_of_ownership": "See footnote",
            "footnote_texts": footnotes,
            "supported_issued_common_shares": 1_972_783.0,
            "owner_is_director": True,
        },
    }


def test_explicit_multi_vehicle_footnote_resolves_source_described_account() -> None:
    row = position([
        "1,799,999 Common Shares are held by ABP Acquisition LLC and 172,784 "
        "Common Shares are held by ABP Trust."
    ])
    ledger, readout = build_holder_position_ledger_v0_10([row])
    assert ledger[0]["deduplication_state"] == (
        "INDIRECT_SOURCE_DESCRIBED_ACCOUNT_RESOLVED"
    )
    assert ledger[0]["canonical_holder_group_id"].startswith(
        "source_described_account:"
    )
    assert readout["source_described_indirect_account_rows_resolved"] == 1
    assert readout["row_level_economic_position_resolution_complete"] is True


def test_relational_spouse_account_remains_unresolved_without_reciprocal_closure() -> None:
    row = position(["Held beneficially by the wife of the Reporting Person."])
    ledger, readout = build_holder_position_ledger_v0_10([row])
    assert ledger[0]["deduplication_state"] == (
        "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED"
    )
    assert readout["row_level_economic_position_resolution_complete"] is False


def test_same_explicit_account_deduplicates_across_reporting_owners() -> None:
    note = [
        "HCG Opportunity, LLC is the record holder of the securities reported "
        "herein."
    ]
    first = position(note)
    second = position(note)
    second["observation_id"] = "position-two"
    second["attributes"]["holder_cik"] = "999"
    second["attributes"]["holder_name"] = "SECOND REPORTER"
    ledger, readout = build_holder_position_ledger_v0_10([first, second])
    assert len(ledger) == 2
    assert len({row["economic_position_id"] for row in ledger}) == 1
    assert readout["row_level_economic_position_resolution_complete"] is True


def test_held_in_name_of_llc_and_named_capital_are_explicit_accounts() -> None:
    rows = [
        position(["100,000 shares are held in the name of Percival Services, LLC."]),
        position(["474,235 shares are owned by Sententia Capital."]),
    ]
    rows[1]["observation_id"] = "capital-position"
    rows[1]["attributes"]["holder_cik"] = "998"
    ledger, readout = build_holder_position_ledger_v0_10(rows)
    assert all(
        row["deduplication_state"] == "INDIRECT_SOURCE_DESCRIBED_ACCOUNT_RESOLVED"
        for row in ledger
    )
    assert readout["unresolved_methodology_relevant_rows"] == 0


def test_truncated_footnote_without_antecedent_remains_unresolved() -> None:
    row = position([
        "of which the Reporting Person is Vice-President, and 237,457 shares "
        "owned by the Reporting Person's family trust, TATS, LLC."
    ])
    ledger, readout = build_holder_position_ledger_v0_10([row])
    assert ledger[0]["deduplication_state"] == (
        "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED"
    )
    assert readout["row_level_economic_position_resolution_complete"] is False


def test_generic_see_footnote_without_account_evidence_remains_unresolved() -> None:
    row = position(["The Reporting Person disclaims beneficial ownership."])
    ledger, readout = build_holder_position_ledger_v0_10([row])
    assert ledger[0]["deduplication_state"] == (
        "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED"
    )
    assert readout["status"] == "FAIL"
