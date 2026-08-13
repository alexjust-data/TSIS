from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.holders_v3 import build_holder_position_ledger_v0_9  # noqa: E402


def position(
    name: str,
    shares: float,
    category: str,
    *,
    footnote: str | None = None,
) -> dict:
    return {
        "observation_id": name,
        "observation_type": "HOLDER_POSITION_SNAPSHOT",
        "instrument_id": "instrument",
        "security_class_id": "class",
        "accession_number": "proxy",
        "form": "DEF 14A",
        "value": shares,
        "eligible_from_session": "2025-07-18",
        "source_sha256": "h",
        "quality_state": "ADMITTED_SINGLE_CLASS_PROXY_POSITION",
        "attributes": {
            "holder_cik": None,
            "holder_name": name,
            "holder_category": category,
            "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
            "direct_or_indirect": None,
            "security_title": "Common Stock",
            "reported_percent": None,
            "supported_issued_common_shares": shares,
            "footnote_texts": [footnote] if footnote else [],
        },
    }


def test_management_aggregate_supersedes_individual_components() -> None:
    ledger, readout = build_holder_position_ledger_v0_9(
        [
            position("Jane Director", 100, "OFFICER_OR_DIRECTOR"),
            position(
                "All current directors and executive officers as a group",
                125,
                "AGGREGATE_GROUP",
            ),
        ]
    )
    assert readout["aggregate_group_rows_used_as_baseline"] == 1
    assert readout["aggregate_component_rows_suppressed"] == 1
    relevant = [row for row in ledger if row["methodology_relevant"]]
    assert len(relevant) == 1
    assert relevant[0]["supported_issued_common_shares"] == 125
    assert relevant[0]["deduplication_state"] == (
        "AGGREGATE_OFFICER_DIRECTOR_POSITION_RESOLVED"
    )


def test_positive_aggregate_and_affiliate_overlap_blocks_resolution() -> None:
    ledger, readout = build_holder_position_ledger_v0_9(
        [
            position("Management group", 125, "AGGREGATE_GROUP"),
            position("Sponsor LLC", 50, "EXPLICIT_AFFILIATE"),
        ]
    )
    affiliate = next(row for row in ledger if row["holder_category"] == "EXPLICIT_AFFILIATE")
    assert affiliate["deduplication_state"] == (
        "AGGREGATE_AFFILIATE_OVERLAP_UNRESOLVED"
    )
    assert readout["row_level_economic_position_resolution_complete"] is True
    assert readout["aggregate_affiliate_overlap_unresolved_rows"] == 1
    assert readout["temporal_baseline_overlap_resolution_authority"] == (
        "DAILY_FLOAT_RESOLVER"
    )


def test_exact_same_note_nested_affiliates_close_to_management_aggregate() -> None:
    note = "Sponsor is record holder; controller is deemed beneficial owner."
    ledger, readout = build_holder_position_ledger_v0_9(
        [
            position("Management group", 2_127_904, "AGGREGATE_GROUP"),
            position("Sponsor LP", 852_162, "EXPLICIT_AFFILIATE", footnote=note),
            position("Owner Ltd", 1_275_742, "EXPLICIT_AFFILIATE", footnote=note),
            position("Controller", 2_127_904, "EXPLICIT_AFFILIATE", footnote=note),
        ]
    )
    affiliates = [
        row for row in ledger if row["holder_category"] == "EXPLICIT_AFFILIATE"
    ]
    assert all(not row["methodology_relevant"] for row in affiliates)
    assert all(
        row["deduplication_state"]
        == "AFFILIATE_SUPPRESSED_BY_EXACT_MANAGEMENT_AGGREGATE_CLOSURE"
        for row in affiliates
    )
    assert readout["aggregate_affiliate_overlap_unresolved_rows"] == 0
    assert readout["aggregate_affiliate_overlap_exactly_closed_rows"] == 3


def test_nested_affiliate_closure_requires_shared_note_and_exact_arithmetic() -> None:
    ledger, readout = build_holder_position_ledger_v0_9(
        [
            position("Management group", 125, "AGGREGATE_GROUP"),
            position("Sponsor LP", 50, "EXPLICIT_AFFILIATE", footnote="one"),
            position("Owner Ltd", 75, "EXPLICIT_AFFILIATE", footnote="two"),
            position("Controller", 125, "EXPLICIT_AFFILIATE", footnote="one"),
        ]
    )
    affiliates = [
        row for row in ledger if row["holder_category"] == "EXPLICIT_AFFILIATE"
    ]
    assert all(row["methodology_relevant"] for row in affiliates)
    assert readout["aggregate_affiliate_overlap_unresolved_rows"] == 3
    assert readout["aggregate_affiliate_overlap_exactly_closed_rows"] == 0
