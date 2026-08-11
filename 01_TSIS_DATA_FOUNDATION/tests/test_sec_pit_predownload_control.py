# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.models import FilingRecord
from sec_pit.predownload_control import (
    accession_link_state,
    filing_roles_v0_2,
    security_class_gate,
    selection_plan_v0_2,
    temporal_scope_state,
)


def filing(form: str, items: str = "") -> FilingRecord:
    return FilingRecord("1", "a", form, "2020-01-01", None, None, "a.htm", None, items, None, None, 1, "fixture")


def test_earnings_8k_is_not_os_or_restriction_evidence() -> None:
    assert filing_roles_v0_2(filing("8-K", "2.02")) == []


def test_relevant_8k_and_6k_use_explicit_content_lanes() -> None:
    roles = filing_roles_v0_2(filing("8-K", "3.01,3.02"))
    assert "LIFECYCLE_EVIDENCE_CANDIDATE" in roles
    assert "OS_EVIDENCE_CANDIDATE" in roles
    assert filing_roles_v0_2(filing("6-K")) == ["FOREIGN_EVENT_CONTENT_PROBE_CANDIDATE"]


def test_cnobp_style_name_halts_despite_common_flag() -> None:
    gate, reason = security_class_gate({
        "instrument_id": "i", "is_common_stock": True,
        "name": "Depositary Shares representing preferred stock",
    })
    assert gate == "FAIL"
    assert "PREFERRED_OR_DEPOSITARY" in reason


def test_issuer_prehistory_is_explicit_not_silently_merged() -> None:
    assert temporal_scope_state("2019-01-01", "2020-01-01", "2024-01-01") == "OPENING_STATE_PREHISTORY_CANDIDATE"
    assert temporal_scope_state("2022-01-01", "2020-01-01", "2024-01-01") == "TARGET_INTERVAL"


def test_cik_does_not_force_one_instrument_when_classes_are_ambiguous() -> None:
    state, candidates = accession_link_state(
        filing_cik="123",
        filing_date="2022-01-01",
        candidate_instruments=[
            {"cik": "123", "instrument_id": "common", "valid_from": "2020-01-01", "valid_to": None},
            {"cik": "123", "instrument_id": "preferred", "valid_from": "2021-01-01", "valid_to": None},
        ],
    )
    assert state == "REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES"
    assert candidates == ["common", "preferred"]


def test_capacity_failure_exposes_required_count_instead_of_truncating() -> None:
    rows = [
        {"accession_number": str(i), "acceptance_datetime": f"20{i:02d}-01-01", "primary_document_url": "x", "roles_v0_2": ["PERIODIC_ANCHOR_CANDIDATE"]}
        for i in range(4)
    ]
    plan = selection_plan_v0_2(rows, capacity=3)
    assert plan.gate == "FAIL"
    assert plan.required_count == 4
    assert len(plan.selected) == 4
