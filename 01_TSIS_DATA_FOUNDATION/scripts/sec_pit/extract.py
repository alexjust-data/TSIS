from __future__ import annotations

import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.models import SourceObservation

OS_CONCEPTS = frozenset({
    "EntityCommonStockSharesOutstanding",
    "CommonStockSharesOutstanding",
})

_OS_PATTERNS = (
    re.compile(r"([0-9][0-9,\.]{2,})\s+shares\s+of\s+(?:the\s+)?(?:(?:registrant|issuer)(?:'s|s)?\s+|our\s+)?(?:common|ordinary)\s+(?:stock|shares)(?:(?!authorized|issuable|underlying|held\s+by|have\s+been\s+issued).){0,180}?(?:were\s+|was\s+)?outstanding\s+as\s+of\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", re.I | re.S),
    re.compile(r"as\s+of\s+([A-Za-z]+\s+\d{1,2},\s+\d{4}).{0,180}?([0-9][0-9,\.]{2,})\s+shares\s+of\s+(?:common|ordinary)\s+(?:stock|shares).*?outstanding", re.I | re.S),
)


def stable_id(*parts: Any) -> str:
    return hashlib.sha256("|".join("" if part is None else str(part) for part in parts).encode("utf-8")).hexdigest()


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def extract_companyfacts_os(
    payload: dict[str, Any],
    *,
    instrument_id: str | None,
    security_class_id: str | None,
    source_url: str,
    source_sha256: str,
    availability_policy: EdgarAvailabilityPolicy,
) -> list[SourceObservation]:
    cik = str(payload.get("cik", "")).zfill(10)
    observations: list[SourceObservation] = []
    for taxonomy, concepts in payload.get("facts", {}).items():
        for concept, fact in concepts.items():
            if concept not in OS_CONCEPTS:
                continue
            for unit, records in fact.get("units", {}).items():
                if unit.lower() not in {"shares", "share"}:
                    continue
                for record in records:
                    accession = record.get("accn")
                    form = record.get("form")
                    accepted = record.get("filed")
                    availability = availability_policy.resolve(accepted, form)
                    value = record.get("val")
                    observations.append(SourceObservation(
                        observation_id=stable_id("companyfacts", cik, accession, taxonomy, concept, record.get("end"), value),
                        observation_type="SHARES_OUTSTANDING_ANCHOR_CANDIDATE",
                        cik=cik,
                        accession_number=accession,
                        form=form,
                        instrument_id=instrument_id,
                        security_class_id=security_class_id,
                        value=float(value) if value is not None else None,
                        unit="shares",
                        measurement_at=record.get("end"),
                        effective_at=record.get("end"),
                        filing_accepted_at=None,
                        eligible_from_session=availability.eligible_from_session.isoformat() if availability.eligible_from_session else None,
                        availability_policy_id=availability.policy_id,
                        source_url=source_url,
                        source_sha256=source_sha256,
                        source_excerpt=None,
                        extraction_method="SEC_COMPANYFACTS_XBRL",
                        quality_state="REQUIRES_ACCESSION_ACCEPTANCE_ENRICHMENT",
                        causality_state="AVAILABILITY_UNCERTAIN",
                        attributes={"taxonomy": taxonomy, "concept": concept, "frame": record.get("frame"), "fy": record.get("fy"), "fp": record.get("fp")},
                    ))
    return observations


def html_to_text(payload: bytes) -> str:
    text = payload.decode("utf-8", errors="replace")
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def extract_cover_page_os(
    payload: bytes,
    *,
    cik: str,
    accession_number: str,
    form: str,
    accepted_at: str | None,
    instrument_id: str | None,
    security_class_id: str | None,
    source_url: str,
    source_sha256: str,
    availability_policy: EdgarAvailabilityPolicy,
) -> list[SourceObservation]:
    text = html_to_text(payload)
    availability = availability_policy.resolve(accepted_at, form)
    observations: list[SourceObservation] = []
    for pattern_index, pattern in enumerate(_OS_PATTERNS):
        for match in pattern.finditer(text):
            first, second = match.groups()
            if pattern_index == 0:
                raw_value, raw_date = first, second
            else:
                raw_date, raw_value = first, second
            numeric = re.sub(r"[^0-9]", "", raw_value)
            measurement = _parse_date(raw_date)
            if not numeric or measurement is None:
                continue
            excerpt = match.group(0)[:500]
            observations.append(SourceObservation(
                observation_id=stable_id("cover", cik, accession_number, measurement, numeric, excerpt),
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
                eligible_from_session=availability.eligible_from_session.isoformat() if availability.eligible_from_session else None,
                availability_policy_id=availability.policy_id,
                source_url=source_url,
                source_sha256=source_sha256,
                source_excerpt=excerpt,
                extraction_method="COVER_PAGE_TEXT_REGEX_V0_1",
                quality_state="CANDIDATE_REQUIRES_RECONCILIATION",
                causality_state=availability.state,
                attributes={"availability_reason": availability.reason},
            ))
    unique = {item.observation_id: item for item in observations}
    return list(unique.values())


def _find_text(root: ET.Element, suffix: str) -> str | None:
    for node in root.iter():
        if node.tag.split("}")[-1] != suffix:
            continue
        if node.text and node.text.strip():
            return node.text.strip()
        for descendant in node.iter():
            if descendant is not node and descendant.tag.split("}")[-1] == "value" and descendant.text:
                return descendant.text.strip()
    return None


def _footnote_texts(root: ET.Element, holding: ET.Element) -> list[str]:
    ids = {
        node.attrib.get("id")
        for node in holding.iter()
        if node.tag.split("}")[-1] == "footnoteId" and node.attrib.get("id")
    }
    values: list[str] = []
    for node in root.iter():
        if node.tag.split("}")[-1] != "footnote" or node.attrib.get("id") not in ids:
            continue
        text = " ".join(part.strip() for part in node.itertext() if part.strip())
        if text:
            values.append(text)
    return values

def extract_form345_owner_snapshot(
    payload: bytes,
    *,
    cik: str,
    accession_number: str,
    form: str,
    accepted_at: str | None,
    source_url: str,
    source_sha256: str,
    availability_policy: EdgarAvailabilityPolicy,
) -> list[SourceObservation]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return []
    owner_cik = _find_text(root, "rptOwnerCik")
    owner_name = _find_text(root, "rptOwnerName")
    issuer_cik = _find_text(root, "issuerCik") or cik
    availability = availability_policy.resolve(accepted_at, form)
    owner_is_director = _find_text(root, "isDirector") == "1"
    owner_is_officer = _find_text(root, "isOfficer") == "1"
    owner_is_ten_percent = _find_text(root, "isTenPercentOwner") == "1"
    owner_is_other = _find_text(root, "isOther") == "1"
    owner_officer_title = _find_text(root, "officerTitle")
    owner_other_text = _find_text(root, "otherText")
    period_of_report = _find_text(root, "periodOfReport")
    results: list[SourceObservation] = []
    holding_sequence = 0
    holding_nodes = (
        ("NON_DERIVATIVE", "nonDerivativeHolding"),
        ("NON_DERIVATIVE", "nonDerivativeTransaction"),
        ("DERIVATIVE", "derivativeHolding"),
        ("DERIVATIVE", "derivativeTransaction"),
    )
    for holding_type, tag in holding_nodes:
        for holding in (node for node in root.iter() if node.tag.split("}")[-1] == tag):
            holding_sequence += 1
            shares = _find_text(holding, "sharesOwnedFollowingTransaction")
            if shares is None:
                continue
            try:
                value = float(shares.replace(",", ""))
            except ValueError:
                continue
            direct = _find_text(holding, "directOrIndirectOwnership")
            title = _find_text(holding, "securityTitle")
            nature = _find_text(holding, "natureOfOwnership")
            footnotes = _footnote_texts(root, holding)
            transaction_date = _find_text(holding, "transactionDate")
            transaction_code = _find_text(holding, "transactionCode")
            acquired_disposed_code = _find_text(
                holding, "transactionAcquiredDisposedCode"
            )
            transaction_shares = _find_text(holding, "transactionShares")
            results.append(SourceObservation(
                observation_id=stable_id(
                    "form345_v0_2", issuer_cik, accession_number, owner_cik,
                    holding_type, title, value, direct, holding_sequence,
                ),
                observation_type="HOLDER_POSITION_SNAPSHOT",
                cik=str(issuer_cik).zfill(10),
                accession_number=accession_number,
                form=form,
                instrument_id=None,
                security_class_id=None,
                value=value,
                unit="shares",
                measurement_at=None,
                effective_at=None,
                filing_accepted_at=accepted_at,
                eligible_from_session=availability.eligible_from_session.isoformat() if availability.eligible_from_session else None,
                availability_policy_id=availability.policy_id,
                source_url=source_url,
                source_sha256=source_sha256,
                source_excerpt=None,
                extraction_method="SEC_OWNERSHIP_XML_V0_2",
                quality_state="DERIVATIVE_SEPARATED" if holding_type == "DERIVATIVE" else "CANDIDATE_REQUIRES_HOLDER_DEDUPLICATION",
                causality_state=availability.state,
                attributes={
                    "holder_cik": owner_cik,
                    "holder_name": owner_name,
                    "holding_type": holding_type,
                    "direct_or_indirect": direct,
                    "security_title": title,
                    "nature_of_ownership": nature,
                    "footnote_texts": footnotes,
                    "period_of_report": period_of_report,
                    "transaction_date": transaction_date,
                    "transaction_code": transaction_code,
                    "transaction_acquired_disposed_code": acquired_disposed_code,
                    "transaction_shares": transaction_shares,
                    "holding_sequence": holding_sequence,
                    "supported_issued_common_shares": (
                        value if holding_type == "NON_DERIVATIVE" else None
                    ),
                    "owner_is_director": owner_is_director,
                    "owner_is_officer": owner_is_officer,
                    "owner_is_ten_percent": owner_is_ten_percent,
                    "owner_is_other": owner_is_other,
                    "owner_officer_title": owner_officer_title,
                    "owner_other_text": owner_other_text,
                },
            ))
    return results


def observations_to_jsonl(observations: Iterable[SourceObservation]) -> str:
    return "".join(json.dumps(item.to_dict(), sort_keys=True, default=str) + "\n" for item in observations)

