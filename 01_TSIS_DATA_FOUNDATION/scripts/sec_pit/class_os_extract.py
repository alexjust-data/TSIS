from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import _parse_date, html_to_text, stable_id
from sec_pit.models import SourceObservation


_AS_OF_ISSUED_BLOCK = re.compile(
    r"As\s+of\s+(?P<measurement>[A-Za-z]+\s+\d{1,2},\s+\d{4}),"
    r"\s+there\s+were\s+(?P<body>.{0,900}?)\s+issued\s+and\s+outstanding",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class InstrumentAdmissionDecision:
    decision: str
    reason: str
    registrant_match: bool
    ticker_class_match: bool
    evidence_excerpt: str | None


def admit_target_interval_document(
    payload: bytes,
    *,
    temporal_scope_state: str,
    accession_link_state: str,
    registrant_name: str,
    ticker: str,
    target_class_label: str,
) -> InstrumentAdmissionDecision:
    if temporal_scope_state == "OPENING_STATE_PREHISTORY_CANDIDATE":
        return InstrumentAdmissionDecision(
            "REJECT_AIFE_OR_OTHER_INSTRUMENT",
            "multiple_instrument_prehistory_not_admitted_to_pgac",
            False,
            False,
            None,
        )
    if temporal_scope_state == "POST_INTERVAL_CONFIRMATION_CANDIDATE":
        return InstrumentAdmissionDecision(
            "REJECT_POST_INTERVAL_WITHOUT_TARGET",
            "post_interval_selection_has_no_target_instrument_candidate",
            False,
            False,
            None,
        )
    if temporal_scope_state != "TARGET_INTERVAL":
        return InstrumentAdmissionDecision(
            "UNRESOLVED_REQUIRES_MANUAL_REVIEW",
            "unsupported_temporal_scope_state",
            False,
            False,
            None,
        )
    if accession_link_state != "SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN":
        return InstrumentAdmissionDecision(
            "UNRESOLVED_REQUIRES_MANUAL_REVIEW",
            "target_interval_link_state_not_single_candidate",
            False,
            False,
            None,
        )

    text = html_to_text(payload)
    registrant_match = registrant_name.casefold() in text.casefold()
    class_ticker = re.search(
        rf"{re.escape(target_class_label)}.{{0,180}}?\b{re.escape(ticker)}\b",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    ticker_class_match = class_ticker is not None
    if registrant_match and ticker_class_match:
        start = max(0, class_ticker.start() - 180)
        end = min(len(text), class_ticker.end() + 240)
        return InstrumentAdmissionDecision(
            "ADMITTED_PGAC_CLASS_A",
            "registrant_and_exchange_trading_table_identify_pgac_class_a",
            True,
            True,
            text[start:end],
        )
    return InstrumentAdmissionDecision(
        "UNRESOLVED_REQUIRES_MANUAL_REVIEW",
        "registrant_or_class_ticker_evidence_missing",
        registrant_match,
        ticker_class_match,
        None,
    )


def extract_cover_page_class_os(
    payload: bytes,
    *,
    cik: str,
    accession_number: str,
    form: str,
    accepted_at: str | None,
    instrument_id: str,
    security_class_id: str | None,
    target_class_label: str,
    source_url: str,
    source_sha256: str,
    availability_policy: EdgarAvailabilityPolicy,
) -> list[SourceObservation]:
    text = html_to_text(payload)
    target_pattern = re.compile(
        rf"(?P<value>[0-9][0-9,]*)\s+of\s+the\s+registrant[’']s\s+"
        rf"(?P<class>{re.escape(target_class_label)})\b",
        re.IGNORECASE,
    )
    observations: list[SourceObservation] = []
    for block in _AS_OF_ISSUED_BLOCK.finditer(text):
        class_match = target_pattern.search(block.group("body"))
        if class_match is None:
            continue
        measurement = _parse_date(block.group("measurement"))
        numeric = int(class_match.group("value").replace(",", ""))
        availability = availability_policy.resolve(accepted_at, form)
        excerpt = block.group(0)[:1200]
        observations.append(SourceObservation(
            observation_id=stable_id(
                "cover_class_os_v0_1",
                cik,
                accession_number,
                target_class_label,
                measurement,
                numeric,
            ),
            observation_type="SHARES_OUTSTANDING_ANCHOR_CANDIDATE",
            cik=cik,
            accession_number=accession_number,
            form=form,
            instrument_id=instrument_id,
            security_class_id=security_class_id,
            value=float(numeric),
            unit="shares",
            measurement_at=measurement,
            effective_at=measurement,
            filing_accepted_at=accepted_at,
            eligible_from_session=(
                availability.eligible_from_session.isoformat()
                if availability.eligible_from_session
                else None
            ),
            availability_policy_id=availability.policy_id,
            source_url=source_url,
            source_sha256=source_sha256,
            source_excerpt=excerpt,
            extraction_method="COVER_PAGE_CLASS_OS_TEXT_V0_1",
            quality_state=(
                "CANDIDATE_REQUIRES_RECONCILIATION"
                if accepted_at
                else "CANDIDATE_REQUIRES_ACCEPTANCE_TIMESTAMP"
            ),
            causality_state=availability.state,
            attributes={
                "security_class_label": target_class_label,
                "availability_reason": availability.reason,
            },
        ))
    unique = {item.observation_id: item for item in observations}
    return list(unique.values())

