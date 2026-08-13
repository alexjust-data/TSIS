from __future__ import annotations

import re

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.class_os_extract_v2 import (
    _AS_OF_DATE,
    class_pattern,
    extract_cover_page_class_os_v0_2,
)
from sec_pit.extract import _parse_date, html_to_text, stable_id
from sec_pit.models import SourceObservation


_FLEX_DATE = r"(?P<measurement>[A-Za-z]+\s+\d{1,2}\s*,\s+\d{4})"


def _residual_patterns(target_class_label: str) -> tuple[re.Pattern[str], ...]:
    target = class_pattern(target_class_label)
    return (
        re.compile(
            rf"{target}\b.{{0,120}}?(?P<value>[0-9][0-9,]*)\s+"
            rf"(?:\(Class\)\s+)?Outstanding\s+at\s+{_AS_OF_DATE}",
            re.I | re.S,
        ),
        re.compile(
            rf"number\s+of\s+shares\s+outstanding\s+of\s+.{{0,100}}?"
            rf"at\s+{_AS_OF_DATE}.{{0,220}}?{target}\b.{{0,100}}?"
            rf"(?P<value>[0-9][0-9,]{{3,}})",
            re.I | re.S,
        ),
        re.compile(
            rf"At\s+{_AS_OF_DATE},?\s+the\s+number\s+of\s+shares\s+"
            rf"outstanding\s+of\s+.{{0,100}}?{target}\b\s+(?:was|were)\s+"
            rf"(?P<value>[0-9][0-9,]*)\s+shares?",
            re.I | re.S,
        ),
        re.compile(
            rf"number\s+of\s+shares\s+outstanding\s+of\s+.{{0,100}}?"
            rf"{target}\b\s+as\s+of\s+{_AS_OF_DATE}\s*[:\-]?\s*"
            rf"(?P<value>[0-9][0-9,]*)",
            re.I | re.S,
        ),
        re.compile(
            rf"number\s+of\s+shares\s+of\s+{target}\b\s+outstanding\s+"
            rf"as\s+of\s+{_AS_OF_DATE}\s*[:\-]?\s*"
            rf"(?P<value>[0-9][0-9,]*)",
            re.I | re.S,
        ),
        re.compile(
            rf"(?:registrant|issuer|company)\s+had\s+"
            rf"(?P<value>[0-9][0-9,]*)\s+shares\s+of\s+"
            rf"(?:its\s+)?{target}\b\s+outstanding\s+as\s+of\s+{_AS_OF_DATE}",
            re.I | re.S,
        ),
        re.compile(
            rf"ANNUAL\s+REPORT.{{0,260}}?fiscal\s+year\s+ended\s+"
            rf"{_FLEX_DATE}.{{0,3000}}?Indicate\s+the\s+number\s+of\s+"
            rf"outstanding\s+shares.{{0,500}}?as\s+of\s+the\s+close\s+of\s+"
            rf"the\s+period\s+covered\s+by\s+the\s+annual\s+report\.\s*"
            rf"{target}\s*:\s*(?P<value>[0-9][0-9,]*)",
            re.I | re.S,
        ),
    )


def extract_cover_page_class_os_v0_3(
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
    """Add bounded cover-page layouts while preserving v0.2 candidates."""
    kwargs = dict(
        cik=cik,
        accession_number=accession_number,
        form=form,
        accepted_at=accepted_at,
        instrument_id=instrument_id,
        security_class_id=security_class_id,
        target_class_label=target_class_label,
        source_url=source_url,
        source_sha256=source_sha256,
        availability_policy=availability_policy,
    )
    observations = extract_cover_page_class_os_v0_2(payload, **kwargs)
    text = html_to_text(payload)
    availability = availability_policy.resolve(accepted_at, form)
    for pattern in _residual_patterns(target_class_label):
        for match in pattern.finditer(text):
            matched = match.group(0)
            if re.search(r"\b(?:authorized|issuable|reserved|underlying)\b", matched, re.I):
                continue
            raw_measurement = re.sub(r"\s+,", ",", match.group("measurement"))
            measurement = _parse_date(raw_measurement)
            numeric = int(match.group("value").replace(",", ""))
            observations.append(SourceObservation(
                observation_id=stable_id(
                    "cover_class_os_v0_3", cik, accession_number,
                    target_class_label, measurement, numeric,
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
                    if availability.eligible_from_session else None
                ),
                availability_policy_id=availability.policy_id,
                source_url=source_url,
                source_sha256=source_sha256,
                source_excerpt=matched[:1200],
                extraction_method="COVER_PAGE_CLASS_OS_TEXT_V0_3",
                quality_state=(
                    "CANDIDATE_REQUIRES_RECONCILIATION"
                    if accepted_at else "CANDIDATE_REQUIRES_ACCEPTANCE_TIMESTAMP"
                ),
                causality_state=availability.state,
                attributes={
                    "security_class_label": target_class_label,
                    "availability_reason": availability.reason,
                    "numeric_selection_state": "RESIDUAL_LAYOUT_EXPLICIT_OUTSTANDING",
                },
            ))
    return list({item.observation_id: item for item in observations}.values())
