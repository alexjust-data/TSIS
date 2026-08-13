from __future__ import annotations

import re
from typing import Any


ADMITTED_IDENTITY_STATE = "ADMITTED_BY_GOVERNED_ISSUER_OR_CLASS_CONTINUITY"
LEGACY_ADMITTED_IDENTITY_STATE = "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
REJECTED_ISSUER_STATE = "REJECTED_NON_TARGET_ISSUER_CIK"
REJECTED_SECURITY_STATE = "REJECTED_NON_TARGET_SECURITY_CLASS"
UNRESOLVED_IDENTITY_STATE = "UNRESOLVED_IDENTITY_OR_CLASS"
ISSUER_FILED_BASELINE_FORMS = frozenset({"DEF 14A", "10-K", "10-K/A", "20-F", "20-F/A"})


def normalize_cik(value: Any) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(10) if digits else None


def archive_cik(source_url: Any) -> str | None:
    match = re.search(r"/Archives/edgar/data/(\d+)/", str(source_url or ""), re.I)
    return normalize_cik(match.group(1)) if match else None


def is_common_equity_title(value: Any) -> bool:
    title = re.sub(r"\s+", " ", str(value or "")).casefold()
    if not title:
        return False
    excluded = (
        "preferred", "preference", "warrant", "option", "note", "debenture",
        "restricted stock unit", "restricted share unit", "right to buy",
        "incentive distribution right", "general partner interest",
    )
    if any(token in title for token in excluded):
        return False
    return any(
        token in title
        for token in ("common", "ordinary", "beneficial interest", "common unit")
    )


def common_equity_row_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        is_common_equity_title((row.get("attributes") or {}).get("security_title"))
        for row in rows
    )


def is_identity_admitted(state: Any) -> bool:
    return str(state or "") in {
        ADMITTED_IDENTITY_STATE,
        LEGACY_ADMITTED_IDENTITY_STATE,
    }


def decide_document_identity(
    *,
    interval_resolution_allowed: bool,
    target_cik: Any,
    issuer_cik: Any,
    form: Any,
    source_url: Any,
    structured_position_rows: int,
    common_equity_rows: int,
    name_match: bool,
    name_match_basis: str | None,
    cusip_match: bool,
    explicit_non_target_name_match: bool = False,
    explicit_non_target_cusip: bool = False,
) -> tuple[str, str | None]:
    if not interval_resolution_allowed:
        return UNRESOLVED_IDENTITY_STATE, None
    target = normalize_cik(target_cik)
    issuer = normalize_cik(issuer_cik)
    if issuer and issuer != target:
        return REJECTED_ISSUER_STATE, "EXPLICIT_NON_TARGET_ISSUER_CIK"
    if issuer is None and explicit_non_target_name_match:
        return REJECTED_ISSUER_STATE, "NAME_LINKED_TO_EXPLICIT_NON_TARGET_CIK"
    if issuer is None and explicit_non_target_cusip:
        return REJECTED_SECURITY_STATE, "EXPLICIT_NON_TARGET_CLASS_CUSIP"
    if structured_position_rows > 0 and common_equity_rows == 0:
        return REJECTED_SECURITY_STATE, "NO_COMMON_EQUITY_POSITION_ROWS"
    if cusip_match:
        return ADMITTED_IDENTITY_STATE, "CLASS_CUSIP_EVIDENCE"
    if name_match:
        return ADMITTED_IDENTITY_STATE, name_match_basis or "TRUSTED_ISSUER_NAME_EVIDENCE"
    if issuer and issuer == target:
        return ADMITTED_IDENTITY_STATE, "TARGET_CIK_AND_COMMON_EQUITY_EVIDENCE"
    if (
        issuer is None
        and str(form or "").upper() in ISSUER_FILED_BASELINE_FORMS
        and archive_cik(source_url) == target
        and common_equity_rows > 0
    ):
        return ADMITTED_IDENTITY_STATE, "ISSUER_FILED_BASELINE_ARCHIVE_CONTINUITY"
    return UNRESOLVED_IDENTITY_STATE, None
