from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.ownership_baseline import classify_baseline_document  # noqa: E402


def management_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "holder_category": "AGGREGATE_GROUP",
        "supported_issued_common_shares": 100.0,
        "measurement_at": "2025-01-01",
    }
    row.update(overrides)
    return row


def test_special_proxy_without_table_is_not_a_baseline() -> None:
    result = classify_baseline_document(
        b"<html><body>Notice of Special Meeting of Stockholders</body></html>",
        form="DEF 14A",
        extracted_rows=[],
    )
    assert result["proxy_or_annual_purpose_state"] == "SPECIAL_PROXY"
    assert result["ownership_table_state"] == "NO_OWNERSHIP_TABLE"
    assert not result["baseline_content_complete_candidate"]


def test_partial_20f_amendment_inherits_instead_of_becoming_empty_baseline() -> None:
    result = classify_baseline_document(
        b"<html><body>This Amendment No. 3 only amends Item 4 and Item 5.</body></html>",
        form="20-F/A",
        extracted_rows=[],
    )
    assert result["document_family"] == "FOREIGN_20F_FAMILY"
    assert result["amendment_scope_state"] == "PARTIAL_AMENDMENT_DETECTED"
    assert result["ownership_table_state"] == "PARTIAL_AMENDMENT_NO_OWNERSHIP_TABLE"


def test_annual_report_with_supported_management_table_is_candidate() -> None:
    result = classify_baseline_document(
        b"<html><body>Annual report</body></html>",
        form="20-F",
        extracted_rows=[management_row()],
    )
    assert result["baseline_content_complete_candidate"]


def test_multiclass_management_table_is_candidate_for_separate_reconciliation() -> None:
    result = classify_baseline_document(
        b"<p>E. Share Ownership</p>",
        form="20-F",
        extracted_rows=[
            {
                "measurement_at": "2025-01-01",
                "attributes": {
                    "holder_category": "AGGREGATE_GROUP",
                    "supported_issued_common_shares": None,
                },
            }
        ],
    )
    assert result["ownership_table_state"] == (
        "OWNERSHIP_TABLE_REQUIRES_CLASS_RECONCILIATION"
    )
    assert result["baseline_content_complete_candidate"] is True
