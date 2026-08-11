from __future__ import annotations

import re
from typing import Any, Iterable

from bs4 import BeautifulSoup


BASELINE_FORMS = frozenset({"DEF 14A", "10-K", "10-K/A", "20-F", "20-F/A"})
MANAGEMENT_CATEGORIES = frozenset({"OFFICER_OR_DIRECTOR", "AGGREGATE_GROUP"})


def _observation_value(row: dict[str, Any], key: str) -> Any:
    if key in row:
        return row.get(key)
    return (row.get("attributes") or {}).get(key)


def classify_baseline_document(
    payload: bytes,
    *,
    form: str,
    extracted_rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Classify baseline usability from filing content, never from form alone."""
    normalized_form = form.upper()
    rows = list(extracted_rows)
    text = " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    lower = text.lower()
    has_management = any(
        _observation_value(row, "holder_category") in MANAGEMENT_CATEGORIES
        for row in rows
    )
    supported_management = any(
        _observation_value(row, "holder_category") in MANAGEMENT_CATEGORIES
        and (
            _observation_value(row, "supported_issued_common_shares") is not None
            or bool(_observation_value(row, "reported_class_components"))
        )
        for row in rows
    )
    has_measurement = bool(rows) and all(row.get("measurement_at") for row in rows)

    if normalized_form == "DEF 14A":
        if re.search(r"\bspecial meeting\b", lower):
            purpose = "SPECIAL_PROXY"
        elif re.search(r"\bannual meeting\b", lower):
            purpose = "ANNUAL_PROXY"
        else:
            purpose = "PROXY_PURPOSE_UNRESOLVED"
    elif normalized_form.startswith("20-F"):
        purpose = "FOREIGN_ANNUAL_REPORT"
    elif normalized_form.startswith("10-K"):
        purpose = "DOMESTIC_ANNUAL_REPORT"
    else:
        purpose = "NOT_BASELINE_FORM"

    partial_amendment = bool(
        normalized_form.endswith("/A")
        and (
            re.search(r"\b(?:only|solely)\s+(?:amends?|amending)\b", lower)
            or re.search(r"\bitems?\s+\d+[a-z]?(?:\s+and\s+\d+[a-z]?)?\b.{0,180}\bamend", lower)
            or re.search(r"\bamendment\b.{0,220}\blimited to\b", lower)
        )
    )

    if normalized_form not in BASELINE_FORMS:
        completeness = "NOT_BASELINE_FORM"
    elif not rows:
        completeness = (
            "PARTIAL_AMENDMENT_NO_OWNERSHIP_TABLE"
            if partial_amendment
            else "NO_OWNERSHIP_TABLE"
        )
    elif not has_measurement:
        completeness = "OWNERSHIP_TABLE_MEASUREMENT_DATE_UNRESOLVED"
    elif not has_management:
        completeness = "OWNERSHIP_TABLE_NO_MANAGEMENT_BASELINE"
    elif not supported_management:
        completeness = "OWNERSHIP_TABLE_REQUIRES_CLASS_RECONCILIATION"
    else:
        completeness = "OWNERSHIP_BASELINE_CONTENT_COMPLETE_CANDIDATE"

    return {
        "form": form,
        "document_family": (
            "FOREIGN_20F_FAMILY"
            if normalized_form.startswith("20-F")
            else "DOMESTIC_ANNUAL_OWNERSHIP_FAMILY"
        ),
        "proxy_or_annual_purpose_state": purpose,
        "amendment_scope_state": (
            "PARTIAL_AMENDMENT_DETECTED"
            if partial_amendment
            else "NOT_PARTIAL_AMENDMENT_DETECTED"
        ),
        "ownership_table_state": completeness,
        "structured_position_rows": len(rows),
        "has_management_rows": has_management,
        "has_supported_management_shares": supported_management,
        "measurement_dates_complete": has_measurement,
        "baseline_content_complete_candidate": (
            completeness
            in {
                "OWNERSHIP_BASELINE_CONTENT_COMPLETE_CANDIDATE",
                "OWNERSHIP_TABLE_REQUIRES_CLASS_RECONCILIATION",
            }
        ),
    }
