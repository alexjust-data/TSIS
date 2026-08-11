from __future__ import annotations

import html
import re

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.class_os_extract_v2 import class_pattern
from sec_pit.extract import stable_id
from sec_pit.models import SourceObservation


_FACT = re.compile(
    r"<ix:(?:nonFraction|nonfraction)\b(?P<attrs>[^>]*)>"
    r"(?P<value>.*?)</ix:(?:nonFraction|nonfraction)>",
    re.IGNORECASE | re.DOTALL,
)


def _attribute(attrs: str, name: str) -> str | None:
    match = re.search(
        rf"\b{re.escape(name)}\s*=\s*[\"']([^\"']+)[\"']",
        attrs,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _measurement_date(raw: str, context_ref: str, fact_start: int) -> str | None:
    context = re.search(
        rf"<xbrli:context\b[^>]*\bid=[\"']{re.escape(context_ref)}[\"'][^>]*>"
        rf"(?P<body>.*?)</xbrli:context>",
        raw,
        re.IGNORECASE | re.DOTALL,
    )
    if context:
        instant = re.search(
            r"<xbrli:instant>\s*(\d{4}-\d{2}-\d{2})\s*</xbrli:instant>",
            context.group("body"),
            re.IGNORECASE,
        )
        if instant:
            return instant.group(1)
    compact = re.search(r"(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)", context_ref)
    if compact:
        return f"{compact.group(1)}-{compact.group(2)}-{compact.group(3)}"
    preceding = html.unescape(raw[max(0, fact_start - 500):fact_start])
    matches = list(re.finditer(
        r"As\s+of\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        preceding,
        re.IGNORECASE,
    ))
    if not matches:
        return None
    from sec_pit.extract import _parse_date

    return _parse_date(matches[-1].group(1))


def extract_ixbrl_class_os_v0_2(
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
    raw = payload.decode("utf-8", errors="replace")
    target = re.compile(class_pattern(target_class_label), re.IGNORECASE)
    observations: list[SourceObservation] = []
    for match in _FACT.finditer(raw):
        attrs = match.group("attrs")
        if (_attribute(attrs, "name") or "").casefold() != (
            "dei:EntityCommonStockSharesOutstanding".casefold()
        ):
            continue
        following = raw[match.end():match.end() + 700]
        next_fact = re.search(r"<ix:(?:nonFraction|nonfraction)\b", following, re.I)
        if next_fact:
            following = following[:next_fact.start()]
        following = html.unescape(following)
        following_text = re.sub(r"<[^>]+>", " ", following)
        following_text = re.sub(r"\s+", " ", following_text)
        if not target.search(following_text):
            continue
        context_ref = _attribute(attrs, "contextRef") or _attribute(attrs, "contextref")
        if not context_ref:
            continue
        measurement = _measurement_date(raw, context_ref, match.start())
        if not measurement:
            continue
        numeric_text = re.sub(r"<[^>]+>", "", match.group("value"))
        numeric_text = html.unescape(numeric_text)
        cleaned = re.sub(r"[^0-9.-]", "", numeric_text)
        if not cleaned:
            continue
        numeric = float(cleaned)
        scale = int(_attribute(attrs, "scale") or 0)
        numeric *= 10**scale
        availability = availability_policy.resolve(accepted_at, form)
        observations.append(SourceObservation(
            observation_id=stable_id(
                "ixbrl_class_os_v0_2",
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
            source_excerpt=html.unescape(raw[match.start():match.end() + 500])[:1200],
            extraction_method="INLINE_XBRL_CLASS_CONTEXT_V0_2",
            quality_state=(
                "CANDIDATE_REQUIRES_RECONCILIATION"
                if accepted_at
                else "CANDIDATE_REQUIRES_ACCEPTANCE_TIMESTAMP"
            ),
            causality_state=availability.state,
            attributes={
                "taxonomy": "dei",
                "concept": "EntityCommonStockSharesOutstanding",
                "context_ref": context_ref,
                "security_class_label": target_class_label,
                "availability_reason": availability.reason,
            },
        ))
    return list({item.observation_id: item for item in observations}.values())
