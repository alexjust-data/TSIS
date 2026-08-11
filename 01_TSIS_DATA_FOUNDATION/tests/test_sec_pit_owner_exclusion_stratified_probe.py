from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.build_owner_exclusion_stratified_probe import select_case  # noqa: E402


def row(accession: str, form: str, filing_date: str, roles: list[str]) -> dict:
    return {
        "ticker": "TEST",
        "accession_number": accession,
        "form": form,
        "filing_date": filing_date,
        "roles_v0_2": roles,
        "temporal_scope_state": "TARGET_INTERVAL",
        "accession_link_state": "SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        "filing_size_bytes": 100,
        "primary_document_url": f"https://example.test/{accession}",
    }


def test_selection_is_methodology_scoped_without_numeric_cap() -> None:
    rows = pd.DataFrame(
        [
            row("old-3", "3", "2024-01-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("old-13d", "SC 13D", "2024-01-02", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("old-13g", "SC 13G", "2024-01-03", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("q1", "10-Q", "2025-01-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("proxy", "DEF 14A", "2025-02-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("q2", "10-Q", "2025-03-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("post-4", "4", "2025-03-02", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("q3", "10-Q", "2025-04-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("post-13g", "SC 13G", "2025-04-02", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("life", "8-K", "2025-04-03", ["EVENT_CONTENT_PROBE_CANDIDATE"]),
        ]
    )
    lifecycle = pd.DataFrame(
        [{"ticker": "TEST", "accession_number": "life", "filing_date": "2025-04-03"}]
    )
    selected, summary = select_case(
        rows,
        lifecycle,
        ticker="TEST",
        probe_end="2025-04-30",
    )
    accessions = set(selected["accession_number"])
    assert accessions == {
        "old-3",
        "old-13d",
        "proxy",
        "q2",
        "q3",
        "post-4",
        "post-13g",
        "life",
    }
    assert "old-13g" not in accessions
    assert "q1" not in accessions
    assert summary["baseline_accession"] == "proxy"
    assert summary["selected_documents"] == 8


def test_foreign_annual_report_can_be_the_baseline() -> None:
    rows = pd.DataFrame(
        [
            row("annual", "20-F", "2025-01-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("schedule", "SCHEDULE 13D", "2025-02-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
        ]
    )
    lifecycle = pd.DataFrame(columns=["ticker", "accession_number", "filing_date"])
    selected, summary = select_case(
        rows,
        lifecycle,
        ticker="TEST",
        probe_end="2025-03-01",
    )
    assert set(selected["accession_number"]) == {"annual", "schedule"}
    assert summary["baseline_form"] == "20-F"


def test_foreign_amendment_selects_complete_annual_family_chain() -> None:
    rows = pd.DataFrame(
        [
            row("prior", "20-F", "2024-01-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("original", "20-F", "2025-01-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("amend-1", "20-F/A", "2025-02-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("amend-2", "20-F/A", "2025-03-01", ["OS_EVIDENCE_CANDIDATE"]),
        ]
    )
    lifecycle = pd.DataFrame(columns=["ticker", "accession_number", "filing_date"])
    selected, summary = select_case(
        rows,
        lifecycle,
        ticker="TEST",
        probe_end="2025-04-01",
        baseline_as_of="2025-04-01",
    )
    assert set(selected["accession_number"]) == {"original", "amend-1", "amend-2"}
    assert summary["baseline_accession"] == "amend-2"
    assert summary["baseline_candidate_accessions"] == [
        "original",
        "amend-1",
        "amend-2",
    ]


def test_domestic_discovery_prefers_bounded_target_interval_candidates() -> None:
    rows = pd.DataFrame(
        [
            {**row("old", "DEF 14A", "2022-01-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]), "temporal_scope_state": "OPENING_STATE_PREHISTORY_CANDIDATE"},
            {**row("opening", "DEF 14A", "2022-10-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]), "temporal_scope_state": "OPENING_STATE_PREHISTORY_CANDIDATE"},
            row("annual", "DEF 14A", "2023-08-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("special", "DEF 14A", "2025-03-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
            row("future", "DEF 14A", "2025-05-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
        ]
    )
    lifecycle = pd.DataFrame(columns=["ticker", "accession_number", "filing_date"])
    selected, summary = select_case(
        rows,
        lifecycle,
        ticker="TEST",
        probe_end="2025-06-01",
        baseline_as_of="2025-04-01",
    )
    assert set(summary["baseline_candidate_accessions"]) == {
        "annual",
        "special",
    }
    assert "future" not in set(summary["baseline_candidate_accessions"])
    assert "future" in set(selected["accession_number"])


def test_full_interval_keeps_all_periodic_filings_and_predecessor() -> None:
    rows = pd.DataFrame(
        [
            row("before", "10-Q", "2024-12-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("q1", "10-Q", "2025-02-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("q2", "10-Q", "2025-05-01", ["OS_EVIDENCE_CANDIDATE"]),
            row("annual", "DEF 14A", "2024-11-01", ["OWNERSHIP_EVIDENCE_CANDIDATE"]),
        ]
    )
    lifecycle = pd.DataFrame(columns=["ticker", "accession_number", "filing_date"])
    selected, summary = select_case(
        rows,
        lifecycle,
        ticker="TEST",
        probe_end="2025-06-01",
        baseline_as_of="2025-01-02",
        full_interval=True,
    )
    assert {"before", "q1", "q2"}.issubset(set(selected["accession_number"]))
    assert summary["os_periodic_documents"] == 3
    assert summary["session_scope_mode"] == "FULL_GOVERNED_INTERVAL"
