from __future__ import annotations

import html
import re

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import _parse_date, stable_id
from sec_pit.models import SourceObservation


_IXBRL_CLASS_OS = re.compile(
    r"As\s+of\s+(?P<measurement>[A-Za-z]+\s+\d{1,2},\s+\d{4}),"
    r"\s+there\s+were\s+"
    r"(?P<fact><ix:nonFraction\b(?=[^>]*\bname=[\"']dei:EntityCommonStockSharesOutstanding[\"'])[^>]*>"
    r"(?P<value>[0-9][0-9,]*)</ix:nonFraction>)"
    r"\s+of\s+the\s+registrant(?:&#8217;|&#x2019;|&rsquo;|[’'])s\s+"
    r"(?P<class>Class\s+[A-Za-z0-9]+\s+ordinary\s+shares)\b",
    re.IGNORECASE | re.DOTALL,
)


def extract_ixbrl_class_os(
    payload: bytes,
    *,
    cik: str,
    accession_number: str,
    form: str,
    accepted_at: str,
    instrument_id: str,
    security_class_id: str | None,
    target_class_label: str,
    source_url: str,
    source_sha256: str,
    availability_policy: EdgarAvailabilityPolicy,
) -> list[SourceObservation]:
    raw = payload.decode("utf-8", errors="replace")
    observations: list[SourceObservation] = []
    for match in _IXBRL_CLASS_OS.finditer(raw):
        observed_class = re.sub(r"\s+", " ", match.group("class")).strip()
        if observed_class.casefold() != target_class_label.casefold():
            continue
        measurement = _parse_date(match.group("measurement"))
        numeric = int(match.group("value").replace(",", ""))
        availability = availability_policy.resolve(accepted_at, form)
        excerpt = html.unescape(match.group(0))[:1200]
        observations.append(SourceObservation(
            observation_id=stable_id(
                "ixbrl_class_os_v0_1",
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
            extraction_method="INLINE_XBRL_CLASS_CONTEXT_V0_1",
            quality_state="CANDIDATE_REQUIRES_RECONCILIATION",
            causality_state=availability.state,
            attributes={
                "taxonomy": "dei",
                "concept": "EntityCommonStockSharesOutstanding",
                "security_class_label": target_class_label,
                "availability_reason": availability.reason,
            },
        ))
    unique = {item.observation_id: item for item in observations}
    return list(unique.values())

