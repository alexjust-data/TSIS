from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import _parse_date, html_to_text, stable_id
from sec_pit.models import SourceObservation


_AS_OF_DATE = r"(?P<measurement>[A-Za-z]+\s+\d{1,2},\s+\d{4})"


@dataclass(frozen=True)
class InstrumentAdmissionDecision:
    decision: str
    reason: str
    registrant_match: bool
    ticker_class_match: bool
    evidence_excerpt: str | None


def normalized_text_key(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", normalized.casefold()).strip()


def class_pattern(target_class_label: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", target_class_label)
    if not words:
        raise ValueError("target class label has no searchable tokens")
    return r"\s+".join(re.escape(word) for word in words)


def admit_target_instrument_document(
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
            "REJECT_PREHISTORY_NOT_PROVEN",
            "prehistory_requires_separate_instrument_continuity_resolution",
            False,
            False,
            None,
        )
    if temporal_scope_state == "POST_INTERVAL_CONFIRMATION_CANDIDATE":
        return InstrumentAdmissionDecision(
            "REJECT_POST_INTERVAL_NOT_PROVEN",
            "post_interval_document_not_admitted_to_probe_window",
            False,
            False,
            None,
        )
    if temporal_scope_state != "TARGET_INTERVAL":
        return InstrumentAdmissionDecision(
            "UNRESOLVED_REQUIRES_REVIEW",
            "unsupported_temporal_scope_state",
            False,
            False,
            None,
        )
    if accession_link_state != "SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN":
        return InstrumentAdmissionDecision(
            "UNRESOLVED_REQUIRES_REVIEW",
            "target_interval_link_state_not_single_candidate",
            False,
            False,
            None,
        )

    text = html_to_text(payload)
    registrant_key = normalized_text_key(registrant_name)
    text_key = normalized_text_key(text)
    registrant_match = bool(registrant_key and registrant_key in text_key)
    class_ticker = re.search(
        rf"{class_pattern(target_class_label)}.{{0,220}}?\b{re.escape(ticker)}\b",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    ticker_class_match = class_ticker is not None
    if registrant_match and ticker_class_match:
        start = max(0, class_ticker.start() - 220)
        end = min(len(text), class_ticker.end() + 280)
        return InstrumentAdmissionDecision(
            "ADMITTED_TARGET_INSTRUMENT_CLASS",
            "registrant_and_exchange_table_identify_target_ticker_and_class",
            True,
            True,
            text[start:end],
        )
    return InstrumentAdmissionDecision(
        "UNRESOLVED_REQUIRES_REVIEW",
        "registrant_or_class_ticker_evidence_missing",
        registrant_match,
        ticker_class_match,
        None,
    )


def _candidate_patterns(target_class_label: str) -> tuple[re.Pattern[str], ...]:
    target = class_pattern(target_class_label)
    possessive = r"(?:the\s+)?(?:registrant|issuer|company)(?:[’']s)?"
    return (
        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},\s+there\s+were\s+"
            rf"(?P<value>[0-9][0-9,]*)\s+(?:of\s+{possessive}\s+)?"
            rf"{target}\b.{{0,500}}?(?:issued\s+and\s+)?outstand",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},?\s+there\s+were\s+"
            rf"(?P<value>[0-9][0-9,]*)\s+sh\s*ares\s+of\s+"
            rf"(?:{possessive}\s+)?{target}\b.{{0,500}}?"
            rf"(?:issued\s+and\s+)?outstand",
            re.IGNORECASE | re.DOTALL,
        ),        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},?\s+(?P<value>[0-9][0-9,]*)\s+"
            rf"sh\s*ares\s+of\s+(?:{possessive}\s+)?{target}\b.{{0,500}}?"
            rf"(?:(?:were|was)\s+)?(?:issued\s+and\s+)?outstand",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},?\s+(?:the\s+)?"
            rf"(?:registrant|issuer|company)\s+had\s+"
            rf"(?P<value>[0-9][0-9,]*)\s+sh\s*ares\s+of\s+{target}\b"
            rf".{{0,500}}?outstand",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},.{{0,260}}?number\s+of\s+shares\s+of\s+"
            rf"{target}\s+outstanding\s+(?:was|were)\s+"
            rf"(?P<value>[0-9][0-9,]*)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"Indicate\s+the\s+number\s+of\s+outstanding\s+shares.{{0,500}}?"
            rf"(?:An\s+aggregate\s+of\s+[0-9][0-9,]*\s+ordinary\s+shares,\s+"
            rf"consisting\s+of\s+)?(?P<value>[0-9][0-9,]*)\s+{target}\b"
            rf".{{0,500}}?as\s+of\s+{_AS_OF_DATE}",
            re.IGNORECASE | re.DOTALL,
        ),
    )


def extract_cover_page_class_os_v0_2(
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
    observations: list[SourceObservation] = []
    for pattern in _candidate_patterns(target_class_label):
        for match in pattern.finditer(text):
            measurement = _parse_date(match.group("measurement"))
            numeric_source = match.group("value")
            issued_outstanding = re.search(
                r"issued\s+and\s+([0-9][0-9,]*)\s+"
                r"shares?\s+outstand",
                match.group(0),
                re.IGNORECASE | re.DOTALL,
            )
            if issued_outstanding:
                numeric_source = issued_outstanding.group(1)
            numeric = int(numeric_source.replace(",", ""))
            availability = availability_policy.resolve(accepted_at, form)
            observations.append(SourceObservation(
                observation_id=stable_id(
                    "cover_class_os_v0_2",
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
                source_excerpt=match.group(0)[:1200],
                extraction_method="COVER_PAGE_CLASS_OS_TEXT_V0_2",
                quality_state=(
                    "CANDIDATE_REQUIRES_RECONCILIATION"
                    if accepted_at
                    else "CANDIDATE_REQUIRES_ACCEPTANCE_TIMESTAMP"
                ),
                causality_state=availability.state,
                attributes={
                    "security_class_label": target_class_label,
                    "availability_reason": availability.reason,
                    "numeric_selection_state": (
                        "OUTSTANDING_VALUE_AFTER_DISTINCT_ISSUED_VALUE"
                        if issued_outstanding
                        else "PRIMARY_PATTERN_VALUE"
                    ),
                },
            ))
    return list({item.observation_id: item for item in observations}.values())
