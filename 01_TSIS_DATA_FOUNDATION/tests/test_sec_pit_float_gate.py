from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.float_estimate import resolve_owner_exclusion_float  # noqa: E402


def test_float_is_null_when_ownership_or_overlap_gates_are_open() -> None:
    rows, readout = resolve_owner_exclusion_float(
        daily_os_rows=[{
            "instrument_id": "i",
            "session_date": "2025-01-02",
            "shares_outstanding_estimate_as_known": 10_000_000.0,
        }],
        holder_ledger=[],
        ownership_coverage={"structured_extraction_complete": False},
        holder_deduplication={
            "economic_position_resolution_complete": False,
            "owner_exclusion_authorized": False,
        },
    )
    assert rows[0]["float_owner_exclusion_estimate_as_known"] is None
    assert rows[0]["estimation_state"] == "BLOCKED_BY_INPUT_GATES"
    assert readout["non_null_float_rows"] == 0



def test_authorized_methodology_still_blocks_unresolved_overlap() -> None:
    _, readout = resolve_owner_exclusion_float(
        daily_os_rows=[],
        holder_ledger=[],
        ownership_coverage={"structured_extraction_complete": True},
        holder_deduplication={"economic_position_resolution_complete": False},
        methodology_authorized=True,
    )
    assert "OWNER_EXCLUSION_NOT_AUTHORIZED" not in readout["blocker_codes"]
    assert "ECONOMIC_POSITION_OVERLAP_UNRESOLVED" in readout["blocker_codes"]


def test_daily_float_is_available_only_between_complete_baseline_and_pending_update() -> None:
    daily_os = [
        {
            "instrument_id": "i",
            "session_date": session,
            "shares_outstanding_estimate_as_known": 10_000_000.0,
        }
        for session in ("2025-01-02", "2025-01-03", "2025-01-06")
    ]
    baseline = {
        "holder_position_id": "proxy-position",
        "economic_position_id": "person-1",
        "form": "DEF 14A",
        "accession_number": "proxy",
        "eligible_from_session": "2025-01-03",
        "methodology_relevant": True,
        "supported_issued_common_shares": 1_000_000.0,
        "ownership_component_state": "NO_ROW_FOOTNOTE_REPORTED_AS_ISSUED_COMMON",
    }
    pending_update = {
        "holder_position_id": "form4-position",
        "economic_position_id": "person-1-update",
        "form": "4",
        "accession_number": "form4",
        "eligible_from_session": "2025-01-06",
        "methodology_relevant": True,
        "supported_issued_common_shares": 900_000.0,
        "ownership_component_state": None,
    }
    rows, readout = resolve_owner_exclusion_float(
        daily_os_rows=daily_os,
        holder_ledger=[baseline, pending_update],
        ownership_coverage={"structured_extraction_complete": True},
        holder_deduplication={
            "row_level_economic_position_resolution_complete": True,
        },
        methodology_authorized=True,
    )
    assert rows[0]["float_owner_exclusion_estimate_as_known"] is None
    assert rows[0]["estimation_state"] == "OWNERSHIP_BASELINE_UNAVAILABLE"
    assert rows[1]["float_owner_exclusion_estimate_as_known"] == 9_000_000
    assert rows[1]["estimation_state"] == "CALCULATED"
    assert rows[2]["float_owner_exclusion_estimate_as_known"] is None
    assert rows[2]["estimation_state"] == "POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED"
    assert readout["status"] == "PASS_WITH_RESTRICTIONS"
    assert readout["non_null_float_rows"] == 1

def test_new_post_baseline_officer_uses_latest_sequential_account_snapshot() -> None:
    daily_os = [{
        "instrument_id": "i",
        "session_date": "2025-12-17",
        "shares_outstanding_estimate_as_known": 10_000_000.0,
    }]
    baseline = {
        "holder_position_id": "proxy-position",
        "economic_position_id": "baseline-person",
        "holder_name": "Existing Director",
        "form": "DEF 14A",
        "accession_number": "proxy",
        "eligible_from_session": "2025-11-07",
        "methodology_relevant": True,
        "supported_issued_common_shares": 1_000_000.0,
        "ownership_component_state": "NO_ROW_FOOTNOTE_REPORTED_AS_ISSUED_COMMON",
    }
    updates = []
    for accession, transaction_date, shares in (
        ("earlier", "2025-12-12", 15_994.0),
        ("later", "2025-12-15", 15_727.0),
    ):
        updates.append({
            "holder_position_id": accession,
            "economic_position_id": accession,
            "canonical_holder_id": "sec_cik:0000000009",
            "canonical_holder_group_id": None,
            "holder_name": "New Officer",
            "direct_or_indirect": "D",
            "security_class_id": "s",
            "form": "4",
            "accession_number": accession,
            "eligible_from_session": "2025-12-17",
            "transaction_date": transaction_date,
            "holding_sequence": 1,
            "methodology_relevant": True,
            "supported_issued_common_shares": shares,
            "ownership_component_state": None,
        })
    rows, readout = resolve_owner_exclusion_float(
        daily_os_rows=daily_os,
        holder_ledger=[baseline, *updates],
        ownership_coverage={"structured_extraction_complete": True},
        holder_deduplication={
            "row_level_economic_position_resolution_complete": True,
        },
        methodology_authorized=True,
    )
    assert rows[0]["unique_supported_excluded_shares"] == 1_015_727
    assert rows[0]["float_owner_exclusion_estimate_as_known"] == 8_984_273
    assert rows[0]["ownership_update_observation_count"] == 1
    assert rows[0]["ownership_update_latest_transaction_date"] == "2025-12-15"
    assert rows[0]["estimation_state"] == "CALCULATED_AND_TEMPORAL_UPDATE"
    assert readout["post_baseline_temporal_update_resolution_complete"] is True
    assert readout["historical_ownership_coverage_complete"] is True


def test_existing_baseline_holder_update_remains_blocked_without_account_set() -> None:
    baseline = {
        "holder_position_id": "proxy-position",
        "economic_position_id": "baseline-person",
        "holder_name": "Tyler J. Luck",
        "form": "DEF 14A",
        "accession_number": "proxy",
        "eligible_from_session": "2025-11-07",
        "methodology_relevant": True,
        "supported_issued_common_shares": 1_000_000.0,
        "ownership_component_state": None,
    }
    update = {
        "holder_position_id": "form4",
        "canonical_holder_id": "sec_cik:0000000009",
        "holder_name": "Luck Tyler J",
        "direct_or_indirect": "D",
        "security_class_id": "s",
        "form": "4",
        "accession_number": "form4",
        "eligible_from_session": "2025-12-17",
        "transaction_date": "2025-12-15",
        "holding_sequence": 1,
        "methodology_relevant": True,
        "supported_issued_common_shares": 900_000.0,
    }
    rows, _ = resolve_owner_exclusion_float(
        daily_os_rows=[{
            "instrument_id": "i",
            "session_date": "2025-12-17",
            "shares_outstanding_estimate_as_known": 10_000_000.0,
        }],
        holder_ledger=[baseline, update],
        ownership_coverage={"structured_extraction_complete": True},
        holder_deduplication={
            "row_level_economic_position_resolution_complete": True,
        },
        methodology_authorized=True,
    )
    assert rows[0]["float_owner_exclusion_estimate_as_known"] is None
    assert "EXISTING_BASELINE_HOLDER_ACCOUNT_SET_INCOMPLETE" in rows[0]["blocker_codes"]