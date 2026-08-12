from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import replace
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import extract_form345_owner_snapshot, stable_id
from sec_pit.models import SourceObservation
from sec_pit.ownership_html import (
    HTML_OWNERSHIP_FORMS,
    extract_html_ownership_snapshots,
)


FORM_345 = frozenset({"3", "3/A", "4", "4/A", "5", "5/A"})
PROXY_FORMS = frozenset({"DEF 14A", "10-K", "10-K/A", "20-F", "20-F/A"})
SCHEDULE_FORMS = frozenset(
    {
        "SC 13D",
        "SC 13D/A",
        "SC 13G",
        "SC 13G/A",
        "SCHEDULE 13D",
        "SCHEDULE 13D/A",
        "SCHEDULE 13G",
        "SCHEDULE 13G/A",
    }
)


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    normalized = re.sub(r"\s+", " ", value.replace("\u00a0", " ")).strip()
    for pattern in ("%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(normalized, pattern).date().isoformat()
        except ValueError:
            continue
    return None


def normalized_name_key(value: Any) -> str | None:
    if not value:
        return None
    ignored = {"corp", "corporation", "inc", "limited", "ltd", "the"}
    tokens = re.findall(r"[a-z0-9]+", str(value).lower())
    tokens = sorted(token for token in tokens if token not in ignored)
    return " ".join(tokens) or None


_VENDOR_SECURITY_NAME_TOKENS = frozenset(
    {
        "adr", "ads", "bermuda", "class", "classes", "common",
        "delaware", "depositary", "depository", "nevada", "nv", "ord",
        "ordinary", "par", "preference", "preferred", "sf", "share",
        "shares", "stock", "stocks", "usd", "value",
    }
)


def normalized_issuer_core_tokens(value: Any) -> frozenset[str]:
    """Remove vendor security/jurisdiction labels from an issuer name."""

    key = normalized_name_key(value)
    if not key:
        return frozenset()
    return frozenset(
        token
        for token in key.split()
        if token not in _VENDOR_SECURITY_NAME_TOKENS and not token.isdigit()
    )


def issuer_name_match_basis(issuer_name: Any, source_text: Any) -> str | None:
    """Return a traceable match basis, never a CIK-only identity admission."""

    name_key = normalized_name_key(issuer_name)
    text_key = normalized_name_key(source_text)
    if not name_key or not text_key:
        return None
    if set(name_key.split()).issubset(set(text_key.split())):
        return "FULL_VENDOR_NAME_TOKEN_EVIDENCE"
    core_tokens = normalized_issuer_core_tokens(issuer_name)
    if len(core_tokens) >= 2 and core_tokens.issubset(set(text_key.split())):
        return "ISSUER_CORE_NAME_TOKEN_EVIDENCE"
    return None


def _normalized_visible_text(value: Any) -> str:
    """Collapse SEC HTML whitespace without changing visible token order."""

    return re.sub(
        r"\s+",
        " ",
        re.sub(r"[\u200b\u200c\u200d\ufeff]", "", str(value).replace("\u00a0", " ")),
    ).strip()


def issuer_name_present_in_text(issuer_name: Any, source_text: Any) -> bool:
    """Match an issuer name in filing text without sorted-token adjacency."""
    return issuer_name_match_basis(issuer_name, source_text) is not None


def _xml_text(root: ET.Element, *suffixes: str) -> str | None:
    wanted = set(suffixes)
    for node in root.iter():
        if node.tag.split("}")[-1] not in wanted:
            continue
        text = " ".join(part.strip() for part in node.itertext() if part.strip())
        if text:
            return text
    return None


def extract_document_identity(payload: bytes) -> dict[str, Any]:
    identity: dict[str, Any] = {
        "issuer_cik": None,
        "issuer_name": None,
        "issuer_cusip": None,
        "security_class_title": None,
    }
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        root = None
    if root is not None:
        identity.update(
            {
                "issuer_cik": _xml_text(root, "issuerCik"),
                "issuer_name": _xml_text(root, "issuerName"),
                "issuer_cusip": _xml_text(root, "issuerCusip", "cusipNumber"),
                "security_class_title": _xml_text(
                    root, "securitiesClassTitle", "securityClassTitle"
                ),
            }
        )
    soup = BeautifulSoup(payload, "xml" if root is not None else "html.parser")
    for fact in soup.find_all(attrs={"name": re.compile("EntityRegistrantName$", re.I)}):
        value = " ".join(fact.stripped_strings)
        if value:
            identity["issuer_name"] = identity["issuer_name"] or value
            break
    text = " ".join(soup.stripped_strings)
    if not identity["issuer_cusip"]:
        cusip_match = re.search(r"CUSIP\s+(?:No\.?\s*)?([A-Z0-9]{8,12})", text, re.I)
        if cusip_match:
            identity["issuer_cusip"] = cusip_match.group(1).upper()
    if not identity["issuer_name"]:
        issuer_match = re.search(
            r"NAME OF ISSUER\s+(.{2,180}?)(?=\s+\(b\)|\s+CUSIP)",
            text,
            re.I,
        )
        if issuer_match:
            identity["issuer_name"] = re.sub(
                r"\s+", " ", issuer_match.group(1)
            ).strip()
    identity["source_text"] = text
    return identity


def extract_name_change_events(payload: bytes) -> list[dict[str, Any]]:
    text = extract_document_identity(payload)["source_text"]
    events: list[dict[str, Any]] = []
    pattern = re.compile(
        r"(?:\bname\s+change\s+from\b|\bchange(?:d|s|ing)?\b.{0,220}?\bname\s+from\b)"
        r"\s*[\"“‘']([^\"”’']+)[\"”’']\s+to\s+[\"“‘']([^\"”’']+)[\"”’']",
        re.I | re.S,
    )
    for match in pattern.finditer(text):
        excerpt = text[max(0, match.start() - 120) : match.end() + 220]
        events.append(
            {
                "prior_name": match.group(1).strip(),
                "new_name": match.group(2).strip(),
                "source_excerpt": excerpt,
            }
        )
    return events


def _number(value: str) -> float | None:
    cleaned = re.sub(r"[^0-9.]", "", value)
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _is_aggregate_management(value: str) -> bool:
    normalized = re.sub(r"\s+", " ", value)
    has_group = bool(re.search(r"\bas\s+(?:a\s+)?group\b", normalized, re.I))
    has_director = bool(
        re.search(r"\bdirectors?\b|\bdirector\s+nominees?\b", normalized, re.I)
    )
    has_officer = bool(
        re.search(
            r"\b(?:executive\s+)?officers?\b|\bNEOs?\b|"
            r"\bnamed\s+executive\s+officers?\b",
            normalized,
            re.I,
        )
    )
    return has_group and has_director and has_officer


def _proxy_footnotes(text: str, header_start: int) -> dict[str, str]:
    section = text[header_start:]
    separator = re.search(r"_{3,}", section)
    if not separator:
        return {}
    section = section[separator.end() :]
    matches = list(re.finditer(r"\((\d+)\)\s+", section))
    notes: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        note = section[match.end() : end]
        note = re.split(
            r"\b(?:Table of Contents|Where You Can Find More Information)\b",
            note,
            maxsplit=1,
            flags=re.I,
        )[0].strip()
        if note:
            notes.setdefault(match.group(1), note)
    return notes


_MONTH_DATE_PATTERN = (
    r"(?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+\d{1,2},\s+\d{4}"
)


def _unique_normalized_date(matches: list[str]) -> str | None:
    dates = {date for value in matches if (date := normalize_date(value))}
    return next(iter(dates)) if len(dates) == 1 else None


def _explicit_document_ownership_date(text: str) -> str | None:
    normalized = re.sub(r"\s+", " ", text)
    patterns = (
        rf"the following table.{{0,300}}?(?:beneficial ownership|ownership)"
        rf".{{0,140}}?\b(?:as of|on)\s+({_MONTH_DATE_PATTERN})",
        rf"the following table.{{0,220}}?\b(?:as of|on)\s+"
        rf"({_MONTH_DATE_PATTERN}).{{0,180}}?(?:beneficial ownership|ownership)",
    )
    matches = [
        match.group(1)
        for pattern in patterns
        for match in re.finditer(pattern, normalized, re.I)
    ]
    return _unique_normalized_date(matches)


def _document_record_date(text: str) -> str | None:
    normalized = re.sub(r"\s+", " ", text)
    patterns = (
        rf"\brecord date\b.{{0,180}}?\b(?:is|as of|at)\s+"
        rf"(?:the close of business\s+(?:on|at)\s+)?({_MONTH_DATE_PATTERN})",
        rf"(?:the close of business\s+(?:on|at)\s+)?({_MONTH_DATE_PATTERN})"
        rf"\s*(?:\([^)]{{0,40}}\brecord date\b[^)]*\)|,\s*as the record date\b)",
    )
    matches = [
        match.group(1)
        for pattern in patterns
        for match in re.finditer(pattern, normalized, re.I)
    ]
    return _unique_normalized_date(matches)


def _proxy_measurement_date(text: str, table_start: int) -> str | None:
    """Return only an explicit date bound to the selected ownership table.

    Proxy statements commonly contain unrelated ``as of`` dates for awards,
    compensation, record dates, and outstanding equity tables. Proximity to a
    document-level ownership heading is therefore insufficient. The date must
    occur in a local passage that also identifies ownership.
    """

    table_context = text[max(0, table_start - 6000) : table_start + 800]
    matches = list(
        re.finditer(
            r"as of\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
            table_context,
            re.I,
        )
    )
    for match in reversed(matches):
        preceding_context = table_context[max(0, match.start() - 800) : match.end()]
        following_same_sentence = table_context[
            match.end() : min(len(table_context), match.end() + 250)
        ]
        ownership_pattern = (
            r"\b(?:beneficial ownership|beneficially owned|security ownership|"
            r"share ownership|ownership)\b"
        )
        if re.search(ownership_pattern, preceding_context, re.I) or re.search(
            rf"^[^.\;]{{0,250}}{ownership_pattern}",
            following_same_sentence,
            re.I,
        ):
            return normalize_date(match.group(1))
    explicit_date = _explicit_document_ownership_date(text)
    if explicit_date:
        return explicit_date
    normalized_text = re.sub(r"\s+", " ", text)
    record_date_reference = re.search(
        r"(?:beneficial ownership|security ownership|share ownership|ownership)"
        r".{0,600}?\b(?:as of|on)\s+(?:the\s+)?record date\b|"
        r"\b(?:as of|on)\s+(?:the\s+)?record date\b.{0,600}?"
        r"(?:beneficial ownership|security ownership|share ownership|ownership)",
        normalized_text,
        re.I,
    )
    if record_date_reference:
        return _document_record_date(text)
    return None


def _proxy_rows(
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
    soup = BeautifulSoup(payload, "html.parser")
    full_text = _normalized_visible_text(" ".join(soup.stripped_strings))
    beneficial_owner_header = re.search(
        r"Name(?:\s+and\s+Address)?\s+of\s+Beneficial\s+Owner", full_text, re.I
    )
    share_ownership_header = re.search(
        r"\b(?:Share|Security|Beneficial) Ownership\b|"
        r"\bShares Beneficially Owned\b",
        full_text,
        re.I,
    )
    header = beneficial_owner_header or share_ownership_header
    if not header:
        return []
    footnotes = _proxy_footnotes(full_text, header.start())
    multi_class = bool(
        re.search(r"Class\s+A ordinary shares", full_text, re.I)
        and re.search(r"Class\s+B ordinary shares", full_text, re.I)
    )
    availability = availability_policy.resolve(accepted_at, form)
    results: list[SourceObservation] = []
    table_search_start = 0
    for table in soup.find_all("table"):
        table_text = _normalized_visible_text(" ".join(table.stripped_strings))
        table_prefix = table_text[: min(160, len(table_text))]
        table_start = (
            full_text.find(table_prefix, table_search_start) if table_prefix else -1
        )
        if table_start >= 0:
            table_search_start = table_start + len(table_prefix)
        standard_table = bool(
            re.search(
                r"Name(?:\s+and\s+Address)?\s+of\s+Beneficial\s+Owner",
                table_text,
                re.I,
            )
        )
        shares_beneficially_owned_table = bool(
            re.search(
                r"(?:Number of )?Shares(?: of (?:Common Stock|Ordinary Shares))? "
                r"Beneficially Owned|Shares Beneficially Owned",
                table_text,
                re.I,
            )
            and re.search(r"\b(?:Percent(?:age)?|%)\b", table_text, re.I)
            and re.search(
                r"\b(?:Directors?|Officers?|Management|Beneficial Owners?)\b",
                table_text,
                re.I,
            )
        )
        beneficial_owner_shares_owned_table = bool(
            re.search(r"\bBeneficial Owner\b", table_text, re.I)
            and re.search(
                r"Number of Shares of (?:Common Stock|Ordinary Shares) (?:Owned|Held)",
                table_text,
                re.I,
            )
            and re.search(r"\bPercent(?:age)?\b", table_text, re.I)
            and re.search(
                r"\b(?:Directors?|Officers?|Management|Beneficial Owners?)\b",
                table_text,
                re.I,
            )
        )
        share_ownership_multiclass_table = bool(
            share_ownership_header
            and re.search(r"Class\s+A", table_text, re.I)
            and re.search(r"Class\s+B", table_text, re.I)
            and re.search(r"Beneficial Ownership", table_text, re.I)
        )
        table_mentions_multiple_classes = bool(
            re.search(r"\bClass\s+A\b", table_text, re.I)
            and re.search(r"\bClass\s+B\b", table_text, re.I)
        )
        single_class_aggregate_table = bool(
            share_ownership_header
            and _is_aggregate_management(table_text)
            and not table_mentions_multiple_classes
            and re.search(
                r"\b(?:Number\s+of\s+Shares|Shares\s+Owned|"
                r"Shares\s+Beneficially\s+Owned|Amount\s+and\s+Nature\s+of\s+"
                r"Beneficial\s+Ownership|Beneficial\s+Ownership\s+as\s+of)\b",
                table_text,
                re.I,
            )
            and re.search(r"\b(?:Percent(?:age)?|%)\b", table_text, re.I)
        )
        if not (
            standard_table
            or shares_beneficially_owned_table
            or beneficial_owner_shares_owned_table
            or share_ownership_multiclass_table
            or single_class_aggregate_table
        ):
            continue
        measurement_at = _proxy_measurement_date(
            full_text,
            table_start if table_start >= 0 else 0,
        )
        measurement_basis = "EXPLICIT_AS_OF_DATE"
        annual_report_context = (
            full_text[max(0, table_start - 3000) : table_start + 800]
            if table_start >= 0
            else ""
        )
        if (
            measurement_at is None
            and share_ownership_header
            and re.search(
                r"as of the date of this annual report",
                annual_report_context,
                re.I,
            )
        ):
            measurement_at = normalize_date((accepted_at or "")[:10])
            measurement_basis = "ANNUAL_REPORT_DATE_FROM_ACCEPTANCE_DATE"
        management_first = bool(
            _is_aggregate_management(table_text)
            and re.search(
                r"(?:5%|Five\s+Percent)(?:\s+or\s+(?:greater|more))?\s+"
                r"(?:Holders|Stockholders|Shareholders)\s*:?[ ]*",
                table_text,
                re.I,
            )
        )
        category = "OFFICER_OR_DIRECTOR" if management_first else "UNCLASSIFIED"
        for tr in table.find_all("tr"):
            cells = [
                _normalized_visible_text(" ".join(cell.stripped_strings))
                for cell in tr.find_all(["td", "th"])
            ]
            compact = [cell for cell in cells if cell and cell != "%"]
            if not compact:
                continue
            row_text = " ".join(compact)
            if re.search(
                r"(?:5%|Five\s+Percent)(?:\s+or\s+(?:greater|more))?\s+"
                r"(?:Holders|Stockholders|Shareholders)\s*:?",
                row_text,
                re.I,
            ):
                category = "FIVE_PERCENT_HOLDER"
                continue
            if (
                not re.search(r"\d", row_text)
                and re.fullmatch(
                    r"(?:Other\s+Named\s+)?(?:Directors?|Officers?)\s*:?",
                    row_text,
                    re.I,
                )
            ):
                category = "OFFICER_OR_DIRECTOR"
                continue
            if (
                not re.search(r"\d", row_text)
                and not _is_aggregate_management(row_text)
                and re.search(
                    r"(?:directors.*(?:executive\s+)?officers|(?:executive\s+)?officers.*directors)",
                    row_text,
                    re.I,
                )
            ):
                category = "OFFICER_OR_DIRECTOR"
                continue
            if re.search(
                r"Name(?: and Address)? of Beneficial Owner|"
                r"(?:Number of )?Shares(?: of (?:Common Stock|Ordinary Shares))? "
                r"Beneficially Owned|Shares Beneficially Owned|"
                r"^Title or Class of Securities:?$|^Common Stock$|"
                r"^Preferred Stock$|^Shares$|^Percent(?:age)?$",
                row_text,
                re.I,
            ):
                continue
            if share_ownership_multiclass_table and not standard_table:
                holder_raw = compact[0]
                if re.search(
                    r"^(?:Class\s+[AB]|Ordinary|Shares|% of Beneficial)",
                    holder_raw,
                    re.I,
                ):
                    continue
                slots = [
                    value
                    for value in compact[1:]
                    if value not in {"\u200b", ""}
                ]
                if len(slots) < 2:
                    continue

                def share_value(value: str) -> float | None:
                    if value in {"-", "—", "–"}:
                        return 0.0
                    if value == "*":
                        return None
                    return _number(value)

                class_a_shares = share_value(slots[0])
                class_b_shares = share_value(slots[1])
                if class_a_shares is None and class_b_shares is None:
                    continue
                class_a_shares = class_a_shares or 0.0
                class_b_shares = class_b_shares or 0.0
                if class_a_shares + class_b_shares == 0:
                    continue
                marker = re.search(r"\((\d+)\)\s*$", holder_raw)
                holder_name = re.sub(r"\s*\(\d+\)\s*$", "", holder_raw).strip(" :")
                row_category = (
                    "AGGREGATE_GROUP"
                    if _is_aggregate_management(holder_name)
                    else category
                )
                percent = _number(slots[2]) if len(slots) > 2 else None
                shares = class_a_shares + class_b_shares
                footnote = footnotes.get(marker.group(1)) if marker else None
                attrs = {
                    "holder_cik": None,
                    "holder_name": holder_name,
                    "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
                    "direct_or_indirect": None,
                    "security_title": "MULTI_CLASS_ORDINARY_SHARES",
                    "reported_percent": percent,
                    "holder_category": row_category,
                    "footnote_marker": marker.group(1) if marker else None,
                    "footnote_text": footnote,
                    "footnote_texts": [footnote] if footnote else [],
                    "supported_issued_common_shares": None,
                    "ownership_component_state": "EXPLICIT_TABLE_CLASS_COMPONENTS",
                    "explicit_affiliate_candidate": False,
                    "table_class_basis": "MULTI_CLASS_ORDINARY_SHARES",
                    "measurement_date_basis": measurement_basis,
                    "reported_class_components": [
                        {
                            "security_class_title": "Class A ordinary shares",
                            "shares": class_a_shares,
                        },
                        {
                            "security_class_title": "Class B ordinary shares",
                            "shares": class_b_shares,
                        },
                    ],
                }
                results.append(
                    SourceObservation(
                        observation_id=stable_id(
                            "sec_20f_share_ownership_table_v0_1",
                            cik,
                            accession_number,
                            holder_name,
                            shares,
                            percent,
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
                        source_excerpt=" ".join(cells)[:1000],
                        extraction_method="SEC_20F_SHARE_OWNERSHIP_TABLE_V0_1",
                        quality_state="CANDIDATE_REQUIRES_CLASS_ALLOCATION",
                        causality_state=availability.state,
                        attributes=attrs,
                    )
                )
                continue
            numeric = [
                _number(value)
                for value in compact[1:]
                if re.fullmatch(r"[0-9][0-9,]*(?:\.[0-9]+)?", value)
            ]
            if not numeric or numeric[0] is None:
                continue
            holder_raw = compact[0]
            marker = re.search(r"\((\d+)\)\s*$", holder_raw)
            holder_name = re.sub(r"\s*\(\d+\)\s*$", "", holder_raw).strip()
            row_category = (
                "AGGREGATE_GROUP"
                if _is_aggregate_management(holder_name)
                else category
            )
            footnote = footnotes.get(marker.group(1)) if marker else None
            shares = float(numeric[0])
            percent = (
                float(numeric[-1])
                if len(numeric) > 1
                and numeric[-1] is not None
                and re.search(r"(?:Percent(?:age)?|%)", table_text, re.I)
                else None
            )
            attrs = {
                "holder_cik": None,
                "holder_name": holder_name,
                "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
                "direct_or_indirect": None,
                "security_title": "MULTI_CLASS_ORDINARY_SHARES" if multi_class else "Common Stock",
                "reported_percent": percent,
                "holder_category": row_category,
                "footnote_marker": marker.group(1) if marker else None,
                "footnote_text": footnote,
                "footnote_texts": [footnote] if footnote else [],
                "supported_issued_common_shares": None if multi_class else shares,
                "ownership_component_state": (
                    "MULTI_CLASS_ALLOCATION_REQUIRED"
                    if multi_class
                    else "NO_MULTI_CLASS_CONFLICT_IDENTIFIED"
                ),
                "explicit_affiliate_candidate": bool(
                    re.search(r"\bsponsor\b", holder_name, re.I)
                    or re.search(r"\bsponsor\b", footnote or "", re.I)
                ),
                "table_class_basis": (
                    "MULTI_CLASS_ORDINARY_SHARES" if multi_class else "SINGLE_OR_UNSPECIFIED"
                ),
                "measurement_date_basis": measurement_basis,
            }
            results.append(
                SourceObservation(
                    observation_id=stable_id(
                        "sec_proxy_ownership_table_v0_4",
                        cik,
                        accession_number,
                        holder_name,
                        shares,
                        percent,
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
                    source_excerpt=" ".join(cells)[:1000],
                    extraction_method="SEC_PROXY_OWNERSHIP_TABLE_V0_4",
                    quality_state=(
                        "CANDIDATE_REQUIRES_CLASS_ALLOCATION"
                        if multi_class
                        else "CANDIDATE_REQUIRES_OVERLAP_RESOLUTION"
                    ),
                    causality_state=availability.state,
                    attributes=attrs,
                )
            )
    return results


def extract_normalized_ownership_snapshots(
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
    common = dict(
        cik=cik,
        accession_number=accession_number,
        form=form,
        accepted_at=accepted_at,
        source_url=source_url,
        source_sha256=source_sha256,
        availability_policy=availability_policy,
    )
    if normalized_form in FORM_345:
        return extract_form345_owner_snapshot(payload, **common)
    if normalized_form in PROXY_FORMS:
        rows = _proxy_rows(
            payload,
            instrument_id=instrument_id,
            security_class_id=security_class_id,
            **common,
        )
        if rows:
            return rows
    if normalized_form not in HTML_OWNERSHIP_FORMS:
        return []
    identity = extract_document_identity(payload)
    rows = extract_html_ownership_snapshots(
        payload,
        instrument_id=instrument_id,
        security_class_id=security_class_id,
        **common,
    )
    normalized: list[SourceObservation] = []
    for row in rows:
        attributes = {
            **row.attributes,
            "issuer_cik": identity.get("issuer_cik"),
            "issuer_name": identity.get("issuer_name"),
            "issuer_cusip": identity.get("issuer_cusip"),
            "security_title": identity.get("security_class_title")
            or row.attributes.get("security_title"),
        }
        normalized.append(
            replace(
                row,
                measurement_at=normalize_date(row.measurement_at),
                effective_at=normalize_date(row.effective_at),
                extraction_method=row.extraction_method + "_NORMALIZED_V0_4",
                attributes=attributes,
            )
        )
    return normalized


def extract_holder_class_components(
    payload: bytes,
    observations: list[SourceObservation],
) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    for row in observations:
        for index, component in enumerate(
            row.attributes.get("reported_class_components") or []
        ):
            shares = component.get("shares")
            title = component.get("security_class_title")
            if shares is None or not title:
                continue
            components.append(
                {
                    "component_id": stable_id(
                        "ownership_table_class_component_v0_1",
                        row.observation_id,
                        index,
                        title,
                        shares,
                    ),
                    "holder_name": row.attributes.get("holder_name"),
                    "holder_name_key": normalized_name_key(
                        row.attributes.get("holder_name")
                    ),
                    "security_class_title": title,
                    "shares": float(shares),
                    "measurement_at": row.measurement_at,
                    "eligible_from_session": row.eligible_from_session,
                    "source_observation_id": row.observation_id,
                    "source_accession": row.accession_number,
                    "source_excerpt": row.source_excerpt,
                    "component_state": "EXPLICIT_OWNERSHIP_TABLE_CLASS_COMPONENT",
                }
            )
        if row.form and row.form.upper() in FORM_345 and row.attributes.get("holding_type") == "NON_DERIVATIVE":
            components.append(
                {
                    "component_id": stable_id("form345_class_component_v0_1", row.observation_id),
                    "holder_name": row.attributes.get("holder_name"),
                    "holder_name_key": normalized_name_key(row.attributes.get("holder_name")),
                    "security_class_title": row.attributes.get("security_title"),
                    "shares": row.value,
                    "measurement_at": row.attributes.get("period_of_report"),
                    "eligible_from_session": row.eligible_from_session,
                    "source_observation_id": row.observation_id,
                    "source_accession": row.accession_number,
                    "component_state": "EXPLICIT_FORM345_CLASS_BALANCE",
                }
            )
    if not observations:
        return components
    schedule_rows = [
        row
        for row in observations
        if row.form and row.form.upper() in {"SC 13D", "SC 13D/A", "SCHEDULE 13D", "SCHEDULE 13D/A"}
    ]
    if not schedule_rows:
        return components
    text = " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    component_clause = re.search(
        r"It includes\s*\(i\)(.{0,1800}?)(?=\s+\(2\)|\s+SCHEDULE\s+13D)",
        text,
        re.I,
    )
    if not component_clause:
        return components
    component_text = component_clause.group(1)
    class_matches = list(
        re.finditer(
            r"([0-9][0-9,]*)\s+(Class\s+[A-Za-z0-9]+\s+ordinary share(?:s)?)",
            component_text,
            re.I,
        )
    )
    holder_match = re.search(
        r"of the issuer that\s+(.+?)\s+\(the\s+[\"“]Sponsor[\"”]\)",
        component_text,
        re.I,
    )
    holder = (
        holder_match.group(1).strip()
        if holder_match
        else schedule_rows[0].attributes.get("holder_name")
    )
    seen: set[tuple[str, float]] = set()
    for match in class_matches:
        shares = float(match.group(1).replace(",", ""))
        title = re.sub(r"\s+", " ", match.group(2)).strip()
        key = (title.lower(), shares)
        if key in seen:
            continue
        seen.add(key)
        components.append(
            {
                "component_id": stable_id(
                    "schedule13d_class_component_v0_1",
                    schedule_rows[0].accession_number,
                    holder,
                    title,
                    shares,
                ),
                "holder_name": holder,
                "holder_name_key": normalized_name_key(holder),
                "security_class_title": title,
                "shares": shares,
                "measurement_at": schedule_rows[0].measurement_at,
                "eligible_from_session": schedule_rows[0].eligible_from_session,
                "source_observation_id": schedule_rows[0].observation_id,
                "source_accession": schedule_rows[0].accession_number,
                "source_excerpt": component_text[max(0, match.start() - 180) : match.end() + 260],
                "component_state": "EXPLICIT_SCHEDULE13D_CLASS_COMPONENT",
            }
        )
    return components






