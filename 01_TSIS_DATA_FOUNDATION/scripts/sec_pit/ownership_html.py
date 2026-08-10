from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from bs4 import BeautifulSoup

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import stable_id
from sec_pit.models import SourceObservation

_PROXY_FORMS = {"DEF 14A", "DEFA14A", "10-K", "10-K/A"}
_SCHEDULE_FORMS = {
    "SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A",
    "SCHEDULE 13D", "SCHEDULE 13D/A", "SCHEDULE 13G", "SCHEDULE 13G/A",
}


HTML_OWNERSHIP_FORMS = _PROXY_FORMS | _SCHEDULE_FORMS


def _number(value: str) -> float | None:
    cleaned = re.sub(r"[^0-9.]", "", value)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _clean_name(value: str) -> str:
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    return re.sub(r"\s+", " ", value).strip(" |")


def _proxy_footnotes(full_text: str) -> dict[str, str]:
    start = full_text.lower().find("beneficial ownership is determined")
    if start < 0:
        return {}
    section = full_text[start:]
    marker_start = re.search(r"\*\s*Represents beneficial ownership", section, re.I)
    if marker_start:
        section = section[marker_start.end():]
    matches = list(re.finditer(r"\((\d+)\)\s+", section))
    notes: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        note = section[match.end():end].strip()
        if note:
            notes.setdefault(match.group(1), note)
    return notes


def _supported_proxy_common_shares(
    shares: float,
    footnote_text: str | None,
) -> tuple[float | None, str]:
    if not footnote_text:
        return shares, "NO_ROW_FOOTNOTE_REPORTED_AS_ISSUED_COMMON"
    lowered = footnote_text.lower()
    if "reconciling with its records" in lowered:
        if "transfer agent report" in lowered:
            return shares, "TRANSFER_AGENT_TABLE_VALUE_SELECTED_SOURCE_CONFLICT"
        return None, "SOURCE_CONFLICT_REQUIRES_MANUAL_RECONCILIATION"
    option_matches = re.findall(
        r"([0-9][0-9,]*)\s+(?:vested\s+)?options?\s+to\s+purchase",
        footnote_text,
        re.I,
    )
    option_shares = sum(float(value.replace(",", "")) for value in option_matches)
    if option_shares > shares:
        common_match = re.search(
            r"and\s+([0-9][0-9,]*)\s+shares?\s+of\s+Common Stock",
            footnote_text,
            re.I,
        )
        if common_match:
            return (
                float(common_match.group(1).replace(",", "")),
                "EXPLICIT_COMMON_COMPONENT_FROM_CONFLICTING_FOOTNOTE",
            )
        return None, "DERIVATIVE_COMPONENT_EXCEEDS_REPORTED_TOTAL"
    if option_shares:
        return shares - option_shares, "DERIVATIVE_COMPONENT_EXCLUDED_FROM_REPORTED_TOTAL"
    return shares, "FOOTNOTE_REVIEWED_NO_DERIVATIVE_COMPONENT_IDENTIFIED"

def _row_observation(
    *,
    holder_name: str,
    shares: float,
    percent: float | None,
    holder_category: str,
    measurement_at: str | None,
    cik: str,
    accession_number: str,
    form: str,
    accepted_at: str | None,
    instrument_id: str | None,
    security_class_id: str | None,
    source_url: str,
    source_sha256: str,
    source_excerpt: str,
    extraction_method: str,
    availability_policy: EdgarAvailabilityPolicy,
    attributes: dict[str, Any] | None = None,
) -> SourceObservation:
    availability = availability_policy.resolve(accepted_at, form)
    merged = {
        "holder_cik": None,
        "holder_name": holder_name,
        "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
        "direct_or_indirect": None,
        "security_title": "Common Stock",
        "reported_percent": percent,
        "holder_category": holder_category,
        "derivative_inclusion_state": "FOOTNOTE_REVIEW_REQUIRED",
    }
    merged.update(attributes or {})
    return SourceObservation(
        observation_id=stable_id(
            extraction_method,
            cik,
            accession_number,
            holder_name,
            shares,
            percent,
            holder_category,
        ),
        observation_type="HOLDER_POSITION_SNAPSHOT",
        cik=cik,
        accession_number=accession_number,
        form=form,
        instrument_id=instrument_id,
        security_class_id=security_class_id,
        value=shares,
        unit="shares",
        measurement_at=measurement_at,
        effective_at=measurement_at,
        filing_accepted_at=accepted_at,
        eligible_from_session=(
            availability.eligible_from_session.isoformat()
            if availability.eligible_from_session
            else None
        ),
        availability_policy_id=availability.policy_id,
        source_url=source_url,
        source_sha256=source_sha256,
        source_excerpt=source_excerpt[:1000],
        extraction_method=extraction_method,
        quality_state="CANDIDATE_REQUIRES_FOOTNOTE_AND_OVERLAP_RESOLUTION",
        causality_state=availability.state,
        attributes=merged,
    )


def _extract_proxy_tables(
    soup: BeautifulSoup,
    **context: Any,
) -> list[SourceObservation]:
    results: list[SourceObservation] = []
    full_text = " ".join(soup.stripped_strings)
    proxy_footnotes = _proxy_footnotes(full_text)
    date_match = re.search(
        r"(?:beneficial owner|known by the Company).{0,220}?as of\s+"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        full_text,
        re.I,
    )
    measurement_at = date_match.group(1) if date_match else None
    current_category = "UNCLASSIFIED_BENEFICIAL_OWNER"

    for table in soup.find_all("table"):
        table_text = " ".join(table.stripped_strings)
        if not (
            re.search(r"Name of Beneficial Owner", table_text, re.I)
            and re.search(r"Beneficially Owned", table_text, re.I)
        ):
            continue
        for tr in table.find_all("tr"):
            cells = [" ".join(cell.stripped_strings) for cell in tr.find_all(["td", "th"])]
            cells = [cell for cell in cells if cell]
            if not cells:
                continue
            row_text = " ".join(cells)
            if re.fullmatch(r"Directors and (?:Named )?Executive Officers", row_text, re.I):
                current_category = "OFFICER_OR_DIRECTOR"
                continue
            if re.fullmatch(r"5% Stockholders", row_text, re.I):
                current_category = "FIVE_PERCENT_HOLDER"
                continue
            if re.search(r"Name of Beneficial Owner", row_text, re.I):
                continue
            match = re.match(
                r"^(.*?)\s+([0-9][0-9,]*)\s+(\*|[0-9]+(?:\.[0-9]+)?)\s*%?\s*$",
                row_text,
            )
            if not match:
                continue
            raw_holder_name = match.group(1)
            marker_match = re.search(r"\((\d+)\)\s*$", raw_holder_name)
            footnote_marker = marker_match.group(1) if marker_match else None
            footnote_text = proxy_footnotes.get(footnote_marker) if footnote_marker else None
            holder_name = _clean_name(raw_holder_name)
            if not holder_name:
                continue
            shares = _number(match.group(2))
            if shares is None:
                continue
            percent = None if match.group(3) == "*" else _number(match.group(3))
            supported_common, component_state = _supported_proxy_common_shares(
                shares, footnote_text
            )
            category = (
                "AGGREGATE_GROUP"
                if re.search(r"directors and executive officers as a group", holder_name, re.I)
                else current_category
            )
            results.append(_row_observation(
                holder_name=holder_name,
                shares=shares,
                percent=percent,
                holder_category=category,
                measurement_at=measurement_at,
                source_excerpt=row_text,
                extraction_method="SEC_PROXY_OWNERSHIP_TABLE_V0_3",
                attributes={
                    "footnote_marker": footnote_marker,
                    "footnote_text": footnote_text,
                    "supported_issued_common_shares": supported_common,
                    "ownership_component_state": component_state,
                },
                **context,
            ))
    return results


def _reported_power(text: str, label: str) -> float | None:
    match = re.search(label + r"\s+([0-9][0-9,]*)", text, re.I)
    return _number(match.group(1)) if match else None


def _extract_schedule_cover_sheets(
    soup: BeautifulSoup,
    **context: Any,
) -> list[SourceObservation]:
    results: list[SourceObservation] = []
    for table_index, table in enumerate(soup.find_all("table")):
        text = " ".join(table.stripped_strings)
        if not (
            re.search(r"NAME(?:S)? OF REPORTING PERSON(?:S)?", text, re.I)
            and re.search(r"AGGREGATE AMOUNT BENEFICIALLY OWNED", text, re.I)
            and re.search(r"PERCENT OF CLASS", text, re.I)
        ):
            continue
        name_match = re.search(
            r"NAME(?:S)? OF REPORTING PERSON(?:S)?\s+(.*?)\s+2\.?\s+CHECK",
            text,
            re.I | re.S,
        )
        shares_match = re.search(
            r"AGGREGATE AMOUNT BENEFICIALLY OWNED"
            r"(?: BY EACH REPORTING PERSON)?\s+([0-9][0-9,]*)",
            text,
            re.I,
        )
        percent_match = re.search(
            r"PERCENT OF CLASS(?: REPRESENTED BY AMOUNT IN ROW \(\d+\))?\s+"
            r"([0-9]+(?:\.[0-9]+)?)\s*%",
            text,
            re.I,
        )
        if not name_match or not shares_match:
            continue
        holder_name = _clean_name(name_match.group(1))
        shares = _number(shares_match.group(1))
        if not holder_name or shares is None:
            continue
        percent = _number(percent_match.group(1)) if percent_match else None


        results.append(_row_observation(
            holder_name=holder_name,
            shares=shares,
            percent=percent,
            holder_category="SCHEDULE_REPORTING_PERSON",
            measurement_at=None,
            source_excerpt=text,
            extraction_method="SEC_SCHEDULE_13D_G_COVER_V0_2",
            attributes={
                "cover_sheet_index": table_index,
                "sole_voting_power": _reported_power(text, "Sole Voting Power"),
                "shared_voting_power": _reported_power(text, "Shared Voting Power"),
                "sole_dispositive_power": _reported_power(text, "Sole Dispositive Power"),
                "shared_dispositive_power": _reported_power(text, "Shared Dispositive Power"),
            },
            **context,
        ))
    if not results:
        document_text = " ".join(soup.stripped_strings)
        starts = list(re.finditer(
            r"1\s+NAME(?:S)? OF REPORTING PERSON(?:S)?\s+",
            document_text,
            re.I,
        ))
        for index, start in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(document_text)
            segment = document_text[start.end():end]
            name_match = re.match(r"(.*?)\s+2\s+CHECK", segment, re.I | re.S)
            shares_match = re.search(
                r"AGGREGATE AMOUNT BENEFICIALLY OWNED"
                r"(?: BY EACH REPORTING PERSON)?\s+([0-9][0-9,]*)",
                segment,
                re.I,
            )
            percent_match = re.search(
                r"PERCENT OF CLASS(?: REPRESENTED BY AMOUNT IN ROW \(\d+\))?\s+"
                r"([0-9]+(?:\.[0-9]+)?)\s*%",
                segment,
                re.I,
            )
            if not name_match or not shares_match:
                continue
            holder_name = _clean_name(name_match.group(1))
            shares = _number(shares_match.group(1))
            if not holder_name or shares is None:
                continue
            results.append(_row_observation(
                holder_name=holder_name,
                shares=shares,
                percent=_number(percent_match.group(1)) if percent_match else None,
                holder_category="SCHEDULE_REPORTING_PERSON",
                measurement_at=None,
                source_excerpt=segment,
                extraction_method="SEC_SCHEDULE_13D_G_DOCUMENT_V0_1",
                attributes={
                    "sole_voting_power": _reported_power(segment, "Sole Voting Power"),
                    "shared_voting_power": _reported_power(segment, "Shared Voting Power"),
                    "sole_dispositive_power": _reported_power(segment, "Sole Dispositive Power"),
                    "shared_dispositive_power": _reported_power(segment, "Shared Dispositive Power"),
                },
                **context,
            ))
    return results


def _xml_text(node: ET.Element, suffix: str) -> str | None:
    for child in node.iter():
        if child.tag.split("}")[-1] == suffix and child.text and child.text.strip():
            return child.text.strip()
    return None


def _extract_schedule_xml(
    payload: bytes,
    **context: Any,
) -> list[SourceObservation]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return []
    event_date = _xml_text(root, "eventDateRequiresFilingThisStatement")
    results: list[SourceObservation] = []
    detail_nodes = [
        node for node in root.iter()
        if node.tag.split("}")[-1] == "coverPageHeaderReportingPersonDetails"
    ]
    for index, node in enumerate(detail_nodes):
        holder_name = _xml_text(node, "reportingPersonName")
        shares_raw = (
            _xml_text(node, "amountBeneficiallyOwned")
            or _xml_text(node, "reportingPersonBeneficiallyOwnedAggregateNumberOfShares")
        )
        if not holder_name or shares_raw is None:
            continue
        shares = _number(shares_raw)
        if shares is None:
            continue
        percent = _number(_xml_text(node, "classPercent") or "")
        results.append(_row_observation(
            holder_name=holder_name,
            shares=shares,
            percent=percent,
            holder_category="SCHEDULE_REPORTING_PERSON",
            measurement_at=event_date,
            source_excerpt=ET.tostring(node, encoding="unicode")[:1000],
            extraction_method="SEC_SCHEDULE_13D_G_XML_V0_1",
            attributes={
                "cover_sheet_index": index,
                "sole_voting_power": _number(_xml_text(node, "soleVotingPower") or ""),
                "shared_voting_power": _number(_xml_text(node, "sharedVotingPower") or ""),
                "sole_dispositive_power": _number(_xml_text(node, "soleDispositivePower") or ""),
                "shared_dispositive_power": _number(_xml_text(node, "sharedDispositivePower") or ""),
            },
            **context,
        ))
    return results


def extract_html_ownership_snapshots(
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
    normalized_form = form.upper()
    if normalized_form not in HTML_OWNERSHIP_FORMS:
        return []
    context = {
        "cik": cik,
        "accession_number": accession_number,
        "form": form,
        "accepted_at": accepted_at,
        "instrument_id": instrument_id,
        "security_class_id": security_class_id,
        "source_url": source_url,
        "source_sha256": source_sha256,
        "availability_policy": availability_policy,
    }
    if normalized_form in _SCHEDULE_FORMS and payload.lstrip().startswith(b"<?xml"):
        return _extract_schedule_xml(payload, **context)
    soup = BeautifulSoup(payload, "html.parser")
    if normalized_form in _SCHEDULE_FORMS:
        return _extract_schedule_cover_sheets(soup, **context)
    return _extract_proxy_tables(soup, **context)
