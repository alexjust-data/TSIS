from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.metadata import filing_roles, stratified_primary_selection  # noqa: E402
from sec_pit.models import FilingRecord  # noqa: E402

AUDITOR_PATH = SCRIPTS / "sec_pit" / "audit_lifecycle_metadata_lane.py"
SPEC = importlib.util.spec_from_file_location("audit_lifecycle_metadata_lane", AUDITOR_PATH)
assert SPEC and SPEC.loader
AUDITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDITOR)

POLICY = json.loads(
    (Path(__file__).resolve().parents[1] / "configs" / "sec_pit_lifecycle_source_selection_policy_v0_1.json").read_text(
        encoding="utf-8"
    )
)


def filing(form: str, items: str | None = None) -> FilingRecord:
    return FilingRecord(
        cik="0000000001",
        accession_number="0000000001-25-000001",
        form=form,
        filing_date="2025-01-01",
        report_date=None,
        acceptance_datetime="2025-01-01T12:00:00.000Z",
        primary_document="primary.htm",
        primary_document_description=None,
        items=items,
        is_xbrl=None,
        is_inline_xbrl=None,
        filing_size_bytes=None,
        metadata_source="fixture",
    )


def selection_row(accession: str, role: str, accepted: str) -> dict:
    return {
        "accession_number": accession,
        "roles": [role],
        "primary_document_url": f"https://example.test/{accession}",
        "acceptance_datetime": accepted,
    }


def test_lifecycle_role_is_assigned_only_to_supported_candidates() -> None:
    assert "LIFECYCLE_EVIDENCE_CANDIDATE" in filing_roles(filing("8-A12B"))
    assert "LIFECYCLE_EVIDENCE_CANDIDATE" in filing_roles(filing("25-NSE"))
    assert "LIFECYCLE_EVIDENCE_CANDIDATE" in filing_roles(filing("8-K", "3.01,9.01"))
    assert "LIFECYCLE_EVIDENCE_CANDIDATE" not in filing_roles(filing("8-K", "2.02,9.01"))


def test_primary_selection_prioritizes_lifecycle_evidence_under_cap() -> None:
    rows = [
        selection_row("lifecycle", "LIFECYCLE_EVIDENCE_CANDIDATE", "2020-01-01"),
        selection_row("os", "OS_EVIDENCE_CANDIDATE", "2025-01-01"),
    ]
    selected = stratified_primary_selection(rows, 1)
    assert [item["accession_number"] for item in selected] == ["lifecycle"]


def test_candidate_type_classifies_lifecycle_sources() -> None:
    assert AUDITOR.candidate_type("8-A12G", None, POLICY) == "REGISTRATION_FILING_CANDIDATE"
    assert AUDITOR.candidate_type("25", None, POLICY) == "FORM_25_FILING_CANDIDATE"
    assert AUDITOR.candidate_type("8-K", "3.01,9.01", POLICY) == "ITEM_3_01_DISCLOSURE_CANDIDATE"
    assert AUDITOR.candidate_type("8-K", "2.02,9.01", POLICY) is None


def test_security_class_gate_rejects_depositary_preferred_conflict() -> None:
    snapshots = pd.DataFrame({"name": ["Depositary Shares Representing Preferred Stock"]})
    state, reason = AUDITOR.security_class_gate({"is_common_stock": True}, snapshots)
    assert state == "FAIL"
    assert reason == "REFERENCE_COMMON_FLAG_CONFLICTS_WITH_PREFERRED_OR_DEPOSITARY_NAME"


def test_security_class_gate_rejects_missing_snapshot_evidence() -> None:
    state, reason = AUDITOR.security_class_gate({"is_common_stock": True}, pd.DataFrame(columns=["name"]))
    assert state == "FAIL"
    assert reason == "NO_GOVERNED_TICKER_SNAPSHOTS"

def test_target_identity_snapshots_separates_ticker_reuse() -> None:
    snapshots = pd.DataFrame(
        [
            {
                "ticker": "BBBY",
                "snapshot_date": "2023-05-02",
                "cik": "0000886158",
                "share_class_figi": "OLD_FIGI",
                "name": "Old issuer",
            },
            {
                "ticker": "BBBY",
                "snapshot_date": "2025-09-01",
                "cik": "0001130713",
                "share_class_figi": "NEW_FIGI",
                "name": "Current issuer",
            },
        ]
    )
    result = AUDITOR.target_identity_snapshots(
        {"cik": "0001130713", "share_class_figi": "NEW_FIGI"},
        snapshots,
    )

    assert result["snapshot_date"].tolist() == ["2025-09-01"]
    assert result["cik"].tolist() == ["0001130713"]