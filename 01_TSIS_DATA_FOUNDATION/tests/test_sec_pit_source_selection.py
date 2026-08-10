from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.metadata import primary_document_url, stratified_primary_selection  # noqa: E402
from sec_pit.models import FilingRecord  # noqa: E402


def row(accession: str, role: str, accepted: str) -> dict:
    return {
        "accession_number": accession,
        "roles": [role],
        "primary_document_url": f"https://example.test/{accession}",
        "acceptance_datetime": accepted,
    }


def test_primary_selection_preserves_source_families_under_cap() -> None:
    rows = [
        *[row(f"os-{index}", "OS_EVIDENCE_CANDIDATE", f"2025-01-{index + 1:02d}") for index in range(10)],
        row("ownership", "OWNERSHIP_EVIDENCE_CANDIDATE", "2024-01-01"),
        row("restriction", "RESTRICTION_EVIDENCE_CANDIDATE", "2024-01-01"),
        row("institutional", "INSTITUTIONAL_CONTEXT_CANDIDATE", "2024-01-01"),
    ]
    selected = stratified_primary_selection(rows, 4)
    roles = {item["roles"][0] for item in selected}
    assert roles == {
        "OS_EVIDENCE_CANDIDATE",
        "OWNERSHIP_EVIDENCE_CANDIDATE",
        "RESTRICTION_EVIDENCE_CANDIDATE",
        "INSTITUTIONAL_CONTEXT_CANDIDATE",
    }


def test_primary_document_url_strips_sec_xsl_transform_prefix() -> None:
    filing = FilingRecord(
        cik="0001838163",
        accession_number="0002012914-25-000007",
        form="4",
        filing_date="2025-12-16",
        report_date=None,
        acceptance_datetime="2025-12-16T23:36:48.000Z",
        primary_document="xslF345X05/primary_doc.xml",
        primary_document_description=None,
        items=None,
        is_xbrl=None,
        is_inline_xbrl=None,
        filing_size_bytes=None,
        metadata_source="fixture",
    )
    assert primary_document_url(filing).endswith("/000201291425000007/primary_doc.xml")