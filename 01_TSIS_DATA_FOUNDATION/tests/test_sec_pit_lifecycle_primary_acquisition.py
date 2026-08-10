from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

RUNNER_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "sec_pit"
    / "run_lifecycle_primary_acquisition.py"
)
SPEC = importlib.util.spec_from_file_location("run_lifecycle_primary_acquisition", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_build_plan_keeps_only_passed_unique_primary_documents() -> None:
    ledger = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "accession_number": "a1",
                "primary_document_url": "https://example.test/a1.htm",
                "candidate_type": "REGISTRATION_FILING_CANDIDATE",
                "filing_size_bytes": 10,
                "filing_date": "2020-01-01",
            },
            {
                "ticker": "BBB",
                "accession_number": "b1",
                "primary_document_url": "https://example.test/b1.htm",
                "candidate_type": "FORM_25_FILING_CANDIDATE",
                "filing_size_bytes": 20,
                "filing_date": "2020-01-02",
            },
            {
                "ticker": "AAA",
                "accession_number": "a2",
                "primary_document_url": None,
                "candidate_type": "ITEM_3_01_DISCLOSURE_CANDIDATE",
                "filing_size_bytes": 30,
                "filing_date": "2020-01-03",
            },
        ]
    )
    gates = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "security_class_gate": "PASS",
                "deep_acquisition_state": "ELIGIBLE",
            },
            {
                "ticker": "BBB",
                "security_class_gate": "FAIL",
                "deep_acquisition_state": "HALT_SECURITY_CLASS",
            },
        ]
    )

    result = RUNNER.build_plan(ledger, gates)

    assert result["accession_number"].tolist() == ["a1"]
    assert result["security_class_gate"].tolist() == ["PASS"]


def test_build_plan_rejects_duplicate_accessions_per_ticker() -> None:
    ledger = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "accession_number": "a1",
                "primary_document_url": "https://example.test/a1.htm",
                "candidate_type": "REGISTRATION_FILING_CANDIDATE",
                "filing_size_bytes": 10,
                "filing_date": "2020-01-01",
            },
            {
                "ticker": "AAA",
                "accession_number": "a1",
                "primary_document_url": "https://example.test/a1.htm",
                "candidate_type": "REGISTRATION_FILING_CANDIDATE",
                "filing_size_bytes": 10,
                "filing_date": "2020-01-01",
            },
        ]
    )
    gates = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "security_class_gate": "PASS",
                "deep_acquisition_state": "ELIGIBLE",
            }
        ]
    )

    try:
        RUNNER.build_plan(ledger, gates)
    except ValueError as error:
        assert "Duplicate ticker/accession" in str(error)
    else:
        raise AssertionError("Duplicate accessions must fail closed")