from __future__ import annotations

from sec_pit.class_os_extract_v2 import (
    COMMON_EQUITY_CLASS_LABELS,
    InstrumentAdmissionDecision,
    admit_target_instrument_document,
    resolve_common_equity_class_candidate,
)
from sec_pit.ownership_identity import archive_cik, normalize_cik


_RECOVERABLE_LINK_STATES = {
    "SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
    "REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES",
}


def _archive_continuity_allowed(
    *,
    temporal_scope_state: str,
    accession_link_state: str,
    target_cik: str,
    source_url: str,
) -> bool:
    return bool(
        temporal_scope_state == "TARGET_INTERVAL"
        and accession_link_state in _RECOVERABLE_LINK_STATES
        and archive_cik(source_url) == normalize_cik(target_cik)
    )


def admit_target_instrument_document_v0_3(
    payload: bytes,
    *,
    temporal_scope_state: str,
    accession_link_state: str,
    registrant_name: str,
    ticker: str,
    target_class_label: str,
    target_cik: str,
    source_url: str,
) -> InstrumentAdmissionDecision:
    legacy = admit_target_instrument_document(
        payload,
        temporal_scope_state=temporal_scope_state,
        accession_link_state=accession_link_state,
        registrant_name=registrant_name,
        ticker=ticker,
        target_class_label=target_class_label,
    )
    if legacy.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS":
        return legacy
    if not _archive_continuity_allowed(
        temporal_scope_state=temporal_scope_state,
        accession_link_state=accession_link_state,
        target_cik=target_cik,
        source_url=source_url,
    ):
        return legacy
    evidence = admit_target_instrument_document(
        payload,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        registrant_name=registrant_name,
        ticker=ticker,
        target_class_label=target_class_label,
    )
    if not evidence.ticker_class_match:
        return legacy
    return InstrumentAdmissionDecision(
        "ADMITTED_TARGET_INSTRUMENT_CLASS",
        "governed_target_cik_archive_and_exchange_table_identify_target_class",
        evidence.registrant_match,
        True,
        evidence.evidence_excerpt,
    )


def resolve_common_equity_class_candidate_v0_3(
    payload: bytes,
    *,
    temporal_scope_state: str,
    accession_link_state: str,
    registrant_name: str,
    ticker: str,
    target_cik: str,
    source_url: str,
) -> tuple[str | None, InstrumentAdmissionDecision]:
    label, legacy = resolve_common_equity_class_candidate(
        payload,
        temporal_scope_state=temporal_scope_state,
        accession_link_state=accession_link_state,
        registrant_name=registrant_name,
        ticker=ticker,
    )
    if label is not None:
        return label, legacy
    if not _archive_continuity_allowed(
        temporal_scope_state=temporal_scope_state,
        accession_link_state=accession_link_state,
        target_cik=target_cik,
        source_url=source_url,
    ):
        return None, legacy

    candidates: list[tuple[str, InstrumentAdmissionDecision]] = []
    for candidate in COMMON_EQUITY_CLASS_LABELS:
        decision = admit_target_instrument_document(
            payload,
            temporal_scope_state="TARGET_INTERVAL",
            accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
            registrant_name=registrant_name,
            ticker=ticker,
            target_class_label=candidate,
        )
        if decision.ticker_class_match:
            candidates.append((candidate, decision))
    candidates.sort(key=lambda item: (len(item[0].split()), len(item[0])), reverse=True)
    if not candidates:
        return None, legacy
    best_words = len(candidates[0][0].split())
    best = [item for item in candidates if len(item[0].split()) == best_words]
    if len(best) != 1:
        return None, InstrumentAdmissionDecision(
            "UNRESOLVED_REQUIRES_REVIEW",
            "multiple_equally_specific_ticker_class_labels_after_archive_continuity",
            any(item[1].registrant_match for item in best),
            False,
            None,
        )
    selected, evidence = best[0]
    return selected, InstrumentAdmissionDecision(
        "ADMITTED_TARGET_INSTRUMENT_CLASS",
        "governed_target_cik_archive_and_exchange_table_identify_target_class",
        evidence.registrant_match,
        True,
        evidence.evidence_excerpt,
    )
