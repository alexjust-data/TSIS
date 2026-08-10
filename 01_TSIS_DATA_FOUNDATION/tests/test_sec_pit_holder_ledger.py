from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.holders import build_holder_position_ledger  # noqa: E402


def position(observation_id: str, direct: str = "D", holding_type: str = "NON_DERIVATIVE") -> dict:
    return {
        "observation_id": observation_id,
        "observation_type": "HOLDER_POSITION_SNAPSHOT",
        "instrument_id": "i",
        "security_class_id": "s",
        "accession_number": "a",
        "form": "4",
        "value": 100.0,
        "eligible_from_session": "2025-01-02",
        "source_sha256": "h",
        "attributes": {
            "holder_cik": "9",
            "holder_name": "Holder",
            "holding_type": holding_type,
            "direct_or_indirect": direct,
            "security_title": "Common Stock",
        },
    }


def test_holder_ledger_removes_exact_duplicate_but_not_indirect_overlap() -> None:
    rows, readout = build_holder_position_ledger([
        position("one"),
        position("duplicate"),
        position("indirect", direct="I"),
        position("derivative", holding_type="DERIVATIVE"),
    ])
    assert len(rows) == 3
    assert readout["exact_duplicate_rows_removed"] == 1
    assert readout["indirect_overlap_unresolved_rows"] == 1
    assert readout["derivative_rows"] == 1
    assert readout["owner_exclusion_authorized"] is False



def test_joint_schedule_position_is_not_additive() -> None:
    rows = []
    for name in ("Controller", "Controlled LLC"):
        row = position(name)
        row["accession_number"] = "schedule"
        row["form"] = "SC 13D"
        row["value"] = 500.0
        row["quality_state"] = "CANDIDATE_REQUIRES_FOOTNOTE_AND_OVERLAP_RESOLUTION"
        row["attributes"].update({
            "holder_cik": None,
            "holder_name": name,
            "holder_category": "SCHEDULE_REPORTING_PERSON",
            "reported_percent": 10.0,
            "direct_or_indirect": None,
        })
        rows.append(row)
    ledger, readout = build_holder_position_ledger(rows)
    assert len({row["economic_position_id"] for row in ledger}) == 1
    assert all(
        row["deduplication_state"] == "JOINT_REPORTING_POSITION_RESOLVED"
        for row in ledger
    )
    assert readout["joint_reporting_rows_resolved"] == 2


def test_indirect_position_resolves_only_from_explicit_controlled_entity() -> None:
    row = position("indirect", direct="I")
    row["attributes"].update({
        "owner_is_director": True,
        "supported_issued_common_shares": 100.0,
        "nature_of_ownership": "DHC Sponsor, LLC",
    })
    ledger, readout = build_holder_position_ledger([row])
    assert ledger[0]["deduplication_state"] == "INDIRECT_CONTROLLED_ENTITY_RESOLVED"
    assert ledger[0]["canonical_holder_group_id"].startswith("controlled_entity_name:")
    assert readout["unresolved_methodology_relevant_rows"] == 0
    assert readout["temporal_position_resolution_complete"] is None
    assert readout["temporal_position_resolution_authority"] == "DAILY_FLOAT_RESOLVER"


def test_indirect_position_resolves_entity_named_in_footnote() -> None:
    row = position("indirect-footnote", direct="I")
    row["attributes"].update({
        "owner_is_director": True,
        "supported_issued_common_shares": 100.0,
        "nature_of_ownership": "See Footnotes",
        "footnote_texts": [
            "Represents shares beneficially owned by Morgan Land LLC "
            ". The Reporting Person controls the entity."
        ],
    })
    ledger, _ = build_holder_position_ledger([row])
    assert ledger[0]["deduplication_state"] == "INDIRECT_CONTROLLED_ENTITY_RESOLVED"