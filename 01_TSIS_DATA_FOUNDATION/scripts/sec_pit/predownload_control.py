"""Fail-closed SEC PIT controls applied before primary-document acquisition.

This module is deliberately network-free.  It converts already acquired SEC
submission metadata plus governed identity intervals into an auditable
selection plan.  It never claims that CIK-level metadata proves a security
class match.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Any

from sec_pit.metadata import (
    LIFECYCLE_DELISTING_FORMS,
    LIFECYCLE_REGISTRATION_FORMS,
    has_item,
)
from sec_pit.models import FilingRecord

POLICY_ID = "sec_pit_predownload_control_v0_2"

PERIODIC_FORMS = frozenset({"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A"})
REGISTRATION_FORMS = frozenset({
    "S-1", "S-1/A", "S-3", "S-3/A", "F-1", "F-1/A", "F-3", "F-3/A",
    "424B1", "424B2", "424B3", "424B4", "424B5", "POS AM", "EFFECT",
})
SCHEDULE_13_FORMS = frozenset({
    "SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A",
    "SCHEDULE 13D", "SCHEDULE 13D/A", "SCHEDULE 13G", "SCHEDULE 13G/A",
})
FORM_345 = frozenset({"3", "3/A", "4", "4/A", "5", "5/A"})
RELEVANT_8K_ITEMS = frozenset({"3.01", "3.02", "3.03", "5.03"})
CONTENT_PROBE_8K_ITEMS = frozenset({"1.01", "2.01", "8.01"})
PREFERRED_NAME_MARKERS = (
    "preferred stock",
    "preferred shares",
    "depositary share",
    "depositary shares",
    "depositary receipt",
)


@dataclass(frozen=True)
class SelectionPlan:
    selected: list[dict[str, Any]]
    required_count: int
    capacity: int | None
    gate: str
    reason: str


def security_class_gate(scope: dict[str, Any]) -> tuple[str, str]:
    """Reject an unconfirmed or contradictory common-equity classification."""
    name = str(scope.get("name") or "").lower()
    if any(marker in name for marker in PREFERRED_NAME_MARKERS):
        return "FAIL", "SECURITY_NAME_IDENTIFIES_PREFERRED_OR_DEPOSITARY_INSTRUMENT"
    if scope.get("is_common_stock") is not True:
        return "FAIL", "COMMON_STOCK_NOT_CONFIRMED"
    if not scope.get("instrument_id"):
        return "FAIL", "INSTRUMENT_ID_MISSING"
    return "PASS", "COMMON_EQUITY_IDENTITY_CONFIRMED_WITHOUT_NAME_CONFLICT"


def filing_roles_v0_2(record: FilingRecord) -> list[str]:
    """Assign acquisition lanes without treating every 8-K/6-K as relevant."""
    form = record.form.upper()
    roles: list[str] = []
    if (
        form in LIFECYCLE_REGISTRATION_FORMS
        or form in LIFECYCLE_DELISTING_FORMS
        or (form in {"8-K", "8-K/A"} and has_item(record.items, "3.01"))
    ):
        roles.append("LIFECYCLE_EVIDENCE_CANDIDATE")
    if form in PERIODIC_FORMS:
        roles.extend(["OS_EVIDENCE_CANDIDATE", "PERIODIC_ANCHOR_CANDIDATE"])
    elif form in REGISTRATION_FORMS:
        roles.extend(["OS_EVIDENCE_CANDIDATE", "RESTRICTION_EVIDENCE_CANDIDATE", "REGISTRATION_CHAIN_CANDIDATE"])
    elif form in {"8-K", "8-K/A"}:
        items = {item.strip() for item in str(record.items or "").split(",") if item.strip()}
        if items & RELEVANT_8K_ITEMS:
            roles.append("EVENT_CONTENT_PROBE_CANDIDATE")
        if "3.02" in items:
            roles.extend(["OS_EVIDENCE_CANDIDATE", "RESTRICTION_EVIDENCE_CANDIDATE"])
        if items & {"3.03", "5.03"}:
            roles.append("RESTRICTION_EVIDENCE_CANDIDATE")
        if items & CONTENT_PROBE_8K_ITEMS and "EVENT_CONTENT_PROBE_CANDIDATE" not in roles:
            roles.append("EVENT_CONTENT_PROBE_CANDIDATE")
    elif form in {"6-K", "6-K/A"}:
        roles.append("FOREIGN_EVENT_CONTENT_PROBE_CANDIDATE")
    if form in SCHEDULE_13_FORMS:
        roles.extend(["OWNERSHIP_EVIDENCE_CANDIDATE", "BENEFICIAL_OWNER_EVENT_CANDIDATE"])
    elif form in FORM_345:
        roles.extend(["OWNERSHIP_EVIDENCE_CANDIDATE", "FORM_345_EVENT_CANDIDATE"])
    elif form in {"DEF 14A", "DEFA14A"}:
        roles.extend(["OWNERSHIP_EVIDENCE_CANDIDATE", "PROXY_OWNERSHIP_ANCHOR_CANDIDATE"])
    elif form in {"10-K", "10-K/A"} and "OWNERSHIP_EVIDENCE_CANDIDATE" not in roles:
        roles.append("OWNERSHIP_EVIDENCE_CANDIDATE")
    if form.startswith("13F"):
        roles.append("MANAGER_13F_GLOBAL_LANE_ONLY")
    return list(dict.fromkeys(roles))


def temporal_scope_state(
    filing_date: str | None,
    interval_start: str | date | None,
    interval_end: str | date | None,
) -> str:
    """Classify issuer evidence relative to the governed target interval."""
    if not filing_date:
        return "UNKNOWN_DATE_REVIEW"
    observed = str(filing_date)[:10]
    start = str(interval_start)[:10] if interval_start else None
    end = str(interval_end)[:10] if interval_end else None
    if start and observed < start:
        return "OPENING_STATE_PREHISTORY_CANDIDATE"
    if end and observed > end:
        return "POST_INTERVAL_CONFIRMATION_CANDIDATE"
    return "TARGET_INTERVAL"


def accession_link_state(
    *,
    filing_cik: str,
    candidate_instruments: Iterable[dict[str, Any]],
    filing_date: str | None,
) -> tuple[str, list[str]]:
    """Return candidates; never force one security class from issuer CIK alone."""
    normalized = "".join(ch for ch in str(filing_cik) if ch.isdigit()).zfill(10)
    candidates: list[str] = []
    for row in candidate_instruments:
        row_cik = "".join(ch for ch in str(row.get("cik") or "") if ch.isdigit()).zfill(10)
        if row_cik != normalized:
            continue
        state = temporal_scope_state(filing_date, row.get("valid_from"), row.get("valid_to"))
        if state in {"TARGET_INTERVAL", "OPENING_STATE_PREHISTORY_CANDIDATE"}:
            candidates.append(str(row.get("instrument_id")))
    candidates = sorted(set(candidates))
    if not candidates:
        return "NO_INSTRUMENT_CANDIDATE", []
    if len(candidates) > 1:
        return "REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES", candidates
    return "SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN", candidates


def selection_plan_v0_2(rows: list[dict[str, Any]], capacity: int | None) -> SelectionPlan:
    """Build a deterministic plan and fail if capacity would truncate required evidence."""
    eligible = [row for row in rows if row.get("roles_v0_2") and row.get("primary_document_url")]
    required_roles = {
        "LIFECYCLE_EVIDENCE_CANDIDATE",
        "PERIODIC_ANCHOR_CANDIDATE",
        "REGISTRATION_CHAIN_CANDIDATE",
        "BENEFICIAL_OWNER_EVENT_CANDIDATE",
        "FORM_345_EVENT_CANDIDATE",
        "PROXY_OWNERSHIP_ANCHOR_CANDIDATE",
    }
    required = [row for row in eligible if required_roles.intersection(row["roles_v0_2"])]
    optional = [row for row in eligible if row not in required]
    def key(row):
        return (row.get("acceptance_datetime") or row.get("filing_date") or "", row.get("accession_number") or "")
    required.sort(key=key)
    optional.sort(key=key)
    if capacity is not None and len(required) > capacity:
        return SelectionPlan(
            selected=required,
            required_count=len(required),
            capacity=capacity,
            gate="FAIL",
            reason="SELECTION_CAPACITY_BELOW_REQUIRED_EVIDENCE_COUNT",
        )
    selected = list(required)
    if capacity is None:
        selected.extend(optional)
    else:
        selected.extend(optional[: max(0, capacity - len(selected))])
    return SelectionPlan(
        selected=selected,
        required_count=len(required),
        capacity=capacity,
        gate="PASS",
        reason="REQUIRED_EVIDENCE_PRESERVED_WITHOUT_TRUNCATION",
    )
