from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import _parse_date, html_to_text, stable_id
from sec_pit.models import SourceObservation

_AS_OF_DATE = r"(?P<measurement>[A-Za-z]+\s+\d{1,2},\s+\d{4})"
COMMON_EQUITY_CLASS_CANDIDATE = "COMMON_STOCK_CLASS_CANDIDATE"
COMMON_EQUITY_CLASS_LABELS = (
    "Class A Common Stock",
    "Class B Common Stock",
    "Class A Ordinary Shares",
    "Class B Ordinary Shares",
    "Common Stock",
    "Common Shares",
    "Ordinary Shares",
)


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


def registrant_name_keys(value: str | None) -> list[str]:
    key = normalized_text_key(value)
    if not key:
        return []
    keys = {key}
    stripped = re.sub(
        r"\s+(?:class\s+[a-z0-9]+\s+)?(?:common\s+stock|common\s+shares|ordinary\s+shares)$",
        "",
        key,
    ).strip()
    if stripped:
        keys.add(stripped)
    return sorted(keys, key=len, reverse=True)


def strip_instrument_class_suffix(value: str | None) -> str:
    name = str(value or "").strip()
    stripped = re.sub(
        r"\s+(?:Class\s+[A-Za-z0-9]+\s+)?(?:Common\s+Stock|Common\s+Shares|Ordinary\s+Shares)$",
        "",
        name,
        flags=re.IGNORECASE,
    ).strip()
    return stripped or name


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
    text_key = normalized_text_key(text)
    registrant_match = any(key in text_key for key in registrant_name_keys(registrant_name))
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


def resolve_common_equity_class_candidate(
    payload: bytes,
    *,
    temporal_scope_state: str,
    accession_link_state: str,
    registrant_name: str,
    ticker: str,
) -> tuple[str | None, InstrumentAdmissionDecision]:
    """Resolve a generic common-equity gate to the class tied to the ticker."""
    admitted: list[tuple[str, InstrumentAdmissionDecision]] = []
    decisions: list[InstrumentAdmissionDecision] = []
    for label in COMMON_EQUITY_CLASS_LABELS:
        decision = admit_target_instrument_document(
            payload,
            temporal_scope_state=temporal_scope_state,
            accession_link_state=accession_link_state,
            registrant_name=registrant_name,
            ticker=ticker,
            target_class_label=label,
        )
        decisions.append(decision)
        if decision.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS":
            admitted.append((label, decision))
    if admitted:
        # A specific label may also satisfy its generic suffix (for example,
        # Class A Common Stock and Common Stock). Prefer the most specific label.
        admitted.sort(key=lambda item: (len(item[0].split()), len(item[0])), reverse=True)
        best_words = len(admitted[0][0].split())
        best = [item for item in admitted if len(item[0].split()) == best_words]
        if len(best) == 1:
            return best[0]
        return None, InstrumentAdmissionDecision(
            "UNRESOLVED_REQUIRES_REVIEW",
            "multiple_equally_specific_ticker_class_labels",
            all(item[1].registrant_match for item in best),
            False,
            None,
        )
    registrant_match = any(decision.registrant_match for decision in decisions)
    return None, InstrumentAdmissionDecision(
        "UNRESOLVED_REQUIRES_REVIEW",
        "common_equity_candidate_not_resolved_from_exchange_table",
        registrant_match,
        False,
        None,
    )


def _candidate_patterns(target_class_label: str) -> tuple[re.Pattern[str], ...]:
    target = class_pattern(target_class_label)
    possessive = r"(?:the\s+)?(?:registrant|issuer|company)(?:[’']s)?"
    return (
        re.compile(
            rf"(?:The\s+)?(?:registrant|issuer|company)\s+had\s+"
            rf"(?P<value>[0-9][0-9,]*)\s+sh\s*ares\s+of\s+"
            rf"{target}\b.{{0,180}}?outstanding\s+as\s+of\s+"
            rf"{_AS_OF_DATE}",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},?\s+(?:the\s+)?number\s+of\s+"
            rf"outstanding\s+shares\s+of\s+{possessive}\s+{target}\b"
            rf".{{0,180}}?(?:was|were)\s+(?P<value>[0-9][0-9,]*)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"As\s+of\s+{_AS_OF_DATE},?\s+(?:the\s+)?"
            rf"(?:registrant|issuer|company)\s+had\s+"
            rf"[0-9][0-9,]*\s+and\s+(?P<value>[0-9][0-9,]*)\s+"
            rf"sh\s*ares\s+of\s+{target}\b.{{0,180}}?"
            rf"issued\s+and\s+outstanding,?\s+respectively",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"(?:The\s+)?number\s+of\s+shares\s+outstanding\s+of\s+"
            rf"{possessive}\s+{target}\b.{{0,260}}?as\s+of\s+"
            rf"{_AS_OF_DATE},?\s+(?:was|were)\s+"
            rf"(?P<value>[0-9][0-9,]*)",
            re.IGNORECASE | re.DOTALL,
        ),
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
            matched_text = match.group(0)
            if re.search(
                r"\b(?:issuable|reserved)\s+(?:under|upon|for)\b",
                matched_text,
                re.IGNORECASE,
            ):
                continue
            measurement = _parse_date(match.group("measurement"))
            numeric_source = match.group("value")
            issued_outstanding = re.search(
                r"issued\s+and\s+([0-9][0-9,]*)\s+"
                r"shares?\s+outstand",
                matched_text,
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
                source_excerpt=matched_text[:1200],
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
