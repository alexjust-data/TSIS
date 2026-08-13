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
    singularized_core = {
        token[:-1] if len(token) >= 6 and token.endswith("s") else token
        for token in core_tokens
    }
    singularized_text = {
        token[:-1] if len(token) >= 6 and token.endswith("s") else token
        for token in text_key.split()
    }
    if len(singularized_core) >= 2 and singularized_core.issubset(singularized_text):
        return "ISSUER_CORE_NAME_SINGULARIZED_TOKEN_EVIDENCE"
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


def _schedule_cover_value(
    visible_strings: list[str],
    marker: str,
) -> str | None:
    marker_key = re.sub(r"[^a-z]", "", marker.casefold())
    for index, value in enumerate(visible_strings):
        value_key = re.sub(r"[^a-z]", "", value.casefold())
        if marker_key not in value_key:
            continue
        inline = re.search(
            re.escape(marker) + r"\s*:\s*([^\r\n]+)", value, flags=re.I
        )
        if inline:
            return _normalized_visible_text(inline.group(1)) or None
        before = re.split(r"\(\s*" + re.escape(marker) + r"\s*\)", value, flags=re.I)[0].strip()
        if before and re.sub(r"[^a-z]", "", before.casefold()) != marker_key:
            lines = [
                _normalized_visible_text(line)
                for line in before.splitlines()
                if _normalized_visible_text(line)
                and not re.fullmatch(r"[-_=]+", _normalized_visible_text(line))
            ]
            if lines:
                return lines[-1]
        if index > 0:
            return visible_strings[index - 1].strip() or None
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
    visible_strings = list(soup.stripped_strings)
    text = " ".join(visible_strings)
    cover_issuer = _schedule_cover_value(visible_strings, "Name of Issuer")
    cover_class = _schedule_cover_value(
        visible_strings, "Title of Class of Securities"
    )
    cover_cusip = _schedule_cover_value(visible_strings, "CUSIP Number")
    if cover_issuer:
        identity["issuer_name"] = identity["issuer_name"] or cover_issuer
    if cover_class:
        identity["security_class_title"] = (
            identity["security_class_title"] or cover_class
        )
    if cover_cusip and not identity["issuer_cusip"]:
        normalized_cover_cusip = re.sub(r"[^A-Z0-9]", "", cover_cusip.upper())
        if 8 <= len(normalized_cover_cusip) <= 12:
            identity["issuer_cusip"] = normalized_cover_cusip
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


def _following_table_notes(table: Any, *, max_chars: int = 6000) -> str:
    """Return notes belonging to the table without crossing a later table.

    SEC HTML commonly nests the ownership table inside layout tables, so direct
    siblings are not reliable. Walk document order, allow strings inside an
    ancestor layout table, and stop when a genuinely different nested table or
    a semantic heading starts.
    """

    ancestor_tables = {
        parent for parent in table.parents if getattr(parent, "name", None) == "table"
    }
    notes: list[str] = []
    length = 0
    for node in table.find_all_next(string=True):
        parent_table = node.find_parent("table")
        if parent_table is table:
            continue
        if (
            parent_table is not None
            and parent_table is not table
            and parent_table not in ancestor_tables
        ):
            parent_table_text = _normalized_visible_text(
                " ".join(parent_table.stripped_strings)
            )
            if not re.match(
                r"^(?:\(\d+\)|\*?\s*Less\s+than\s+1%)",
                parent_table_text,
                re.I,
            ):
                break
        if node.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"]):
            break
        value = _normalized_visible_text(str(node))
        if not value:
            continue
        notes.append(value)
        length += len(value)
        if length >= max_chars:
            break
    return " ".join(notes)


def _numbered_notes(text: str) -> dict[str, str]:
    """Extract numbered notes from the bounded text following one table."""
    normalized = _normalized_visible_text(text)
    matches = list(re.finditer(r"(?:^|\s)\((\d{1,2})\)\s+", normalized))
    notes: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        note = normalized[match.end() : end].strip()
        if note:
            notes.setdefault(match.group(1), note)
    return notes


def _expanded_row_cells(tr: Any) -> list[str]:
    """Expand HTML colspans so SEC spacer-heavy ownership tables align."""
    expanded: list[str] = []
    for cell in tr.find_all(["td", "th"], recursive=False):
        text = _normalized_visible_text(" ".join(cell.stripped_strings))
        try:
            colspan = max(1, int(cell.get("colspan", 1)))
        except (TypeError, ValueError):
            colspan = 1
        expanded.extend([text] * colspan)
    return expanded


def _explicit_multiclass_table_rows(table: Any) -> list[dict[str, Any]]:
    """Extract exact Class A/B components from aligned ownership columns.

    Empty cells never imply zero. A component is emitted only when its class
    column contains a number or an explicit dash.
    """
    rows = [_expanded_row_cells(tr) for tr in table.find_all("tr")]
    if not rows:
        return []
    header_index = next(
        (
            index
            for index, cells in enumerate(rows)
            if re.search(r"\bClass\s+A\b", " ".join(cells), re.I)
            and re.search(r"\bClass\s+B\b", " ".join(cells), re.I)
        ),
        None,
    )
    if header_index is None:
        return []
    header_rows = rows[: min(len(rows), header_index + 9)]
    width = max(map(len, header_rows))
    contexts = [
        " ".join(
            cells[column]
            for cells in header_rows
            if column < len(cells) and cells[column]
        )
        for column in range(width)
    ]
    class_a_positions = {
        index for index, value in enumerate(contexts)
        if re.search(r"\bClass\s+A\b", value, re.I)
    }
    class_b_positions = {
        index for index, value in enumerate(contexts)
        if re.search(r"\bClass\s+B\b", value, re.I)
    }
    if not class_a_positions or not class_b_positions:
        return []

    def percentage_positions(class_positions: set[int]) -> list[int]:
        return [
            index for index in sorted(class_positions)
            if re.search(r"(?:Percent(?:age)?|%)", contexts[index], re.I)
        ]

    def share_positions(class_positions: set[int]) -> list[int]:
        positions = [
            index for index in sorted(class_positions)
            if not re.search(r"(?:Percent(?:age)?|%)", contexts[index], re.I)
        ]
        return positions or sorted(class_positions)

    a_share_positions = share_positions(class_a_positions)
    b_share_positions = share_positions(class_b_positions)
    a_percentage_positions = percentage_positions(class_a_positions)
    b_percentage_positions = percentage_positions(class_b_positions)
    first_class_position = min(class_a_positions | class_b_positions)

    def exact_share(
        cells: list[str],
        positions: list[int],
        percent_positions: list[int],
    ) -> float | None:
        if percent_positions and not any(
            position < len(cells)
            and (
                cells[position].strip() in {"-", "\u2014", "\u2013", "â€”", "â€“", "*"}
                or re.fullmatch(
                    r"[0-9][0-9,]*(?:\.\d+)?",
                    cells[position].strip(),
                )
            )
            for position in percent_positions
        ):
            return None
        seen: set[str] = set()
        for position in positions:
            if position >= len(cells):
                continue
            value = cells[position].strip()
            if not value or value in seen:
                continue
            seen.add(value)
            if value in {"-", "\u2014", "\u2013", "â€”", "â€“"}:
                return 0.0
            if re.fullmatch(r"[0-9][0-9,]*(?:\.\d+)?", value):
                parsed = _number(value)
                if parsed is not None and float(parsed).is_integer():
                    return float(parsed)
        return None

    header_text = " ".join(rows[header_index])
    header_context_text = " ".join(contexts)
    security_kind = (
        "ordinary shares"
        if re.search(r"ordinary\s+shares", header_context_text, re.I)
        else "common stock"
        if re.search(r"common\s+(?:stock|shares)", header_context_text, re.I)
        else "shares"
    )
    extracted: list[dict[str, Any]] = []
    table_text = _normalized_visible_text(" ".join(table.stripped_strings))
    category = (
        "OFFICER_OR_DIRECTOR"
        if _is_aggregate_management(table_text)
        and re.search(r"(?:5%|Five\s+Percent).{0,80}?(?:Holders|Stockholders|Shareholders)", table_text, re.I)
        else "UNCLASSIFIED"
    )
    for cells in rows[header_index + 1 :]:
        row_text = " ".join(value for value in cells if value)
        if re.search(
            r"(?:5%|Five\s+Percent).{0,80}?(?:Holders|Stockholders|Shareholders)",
            row_text,
            re.I,
        ):
            category = "FIVE_PERCENT_HOLDER"
            continue
        if not re.search(r"\d", row_text) and re.search(
            r"(?:Directors?.*(?:Executive\s+)?Officers?|"
            r"(?:Executive\s+)?Officers?.*Directors?)",
            row_text,
            re.I,
        ):
            category = "OFFICER_OR_DIRECTOR"
            continue
        holder = next(
            (value for value in cells[:first_class_position] if value.strip()),
            "",
        )
        if not holder or re.search(
            r"Name(?: and Address)? of Beneficial Owner|Beneficially Owned|"
            r"Approximate Percentage|Number of Shares",
            holder,
            re.I,
        ):
            continue
        class_a = exact_share(cells, a_share_positions, a_percentage_positions)
        class_b = exact_share(cells, b_share_positions, b_percentage_positions)
        if class_a is None or class_b is None:
            continue
        if class_a + class_b == 0:
            continue
        extracted.append(
            {
                "holder_raw": holder,
                "cells": cells,
                "class_a": class_a,
                "class_b": class_b,
                "security_kind": security_kind,
                "holder_category": (
                    "AGGREGATE_GROUP"
                    if _is_aggregate_management(holder)
                    else category
                ),
            }
        )
    return extracted


def _exact_current_shares_from_footnote(
    total_beneficial_shares: float,
    footnote: str | None,
) -> float | None:
    """Resolve current shares only from an arithmetically closed footnote.

    Every numeric share component must be classified as currently issued or
    acquirable, and the components must sum exactly to the reported beneficial
    total. Partial ``includes`` disclosures therefore remain fail-closed.
    """
    if not footnote:
        return None
    text = _normalized_visible_text(footnote)
    components: dict[int, tuple[str, float]] = {}

    future_patterns = (
        r"(?P<n>[0-9][0-9,]*)\s+shares?\b"
        r"(?:(?![0-9][0-9,]*\s+shares?).){0,100}?"
        r"\b(?:issuable|underlying)\b",
        r"(?P<n>[0-9][0-9,]*)\s+(?:options?|warrants?)\b",
        r"(?:options?|warrants?)\s+(?:to\s+purchase|for\s+purchase\s+of)?\s*"
        r"(?P<n>[0-9][0-9,]*)\s+shares?\b",
        r"(?P<n>[0-9][0-9,]*)\s+shares?\s+subject\s+to\s+.{0,80}?"
        r"(?:options?|warrants?)\b",
    )
    for pattern in future_patterns:
        for match in re.finditer(pattern, text, re.I):
            position = match.start("n")
            components[position] = (
                "ACQUIRABLE",
                float(match.group("n").replace(",", "")),
            )

    current_pattern = re.compile(
        r"(?P<n>[0-9][0-9,]*)\s+shares?\s+of\s+.{0,90}?"
        r"(?:common\s+stock|ordinary\s+shares?)\b",
        re.I,
    )
    for match in current_pattern.finditer(text):
        position = match.start("n")
        if position in components:
            continue
        local = text[match.start() : min(len(text), match.end() + 36)]
        if re.search(r"\b(?:issuable|underlying|acquirable)\b", local, re.I):
            components[position] = (
                "ACQUIRABLE",
                float(match.group("n").replace(",", "")),
            )
            continue
        components[position] = (
            "CURRENT",
            float(match.group("n").replace(",", "")),
        )

    current = sum(value for role, value in components.values() if role == "CURRENT")
    acquirable = sum(
        value for role, value in components.values() if role == "ACQUIRABLE"
    )
    if not components or not acquirable:
        return None
    if abs((current + acquirable) - float(total_beneficial_shares)) > 0.5:
        return None
    return current


def _has_position_specific_acquirable_disclosure(text: str | None) -> bool:
    """Detect a disclosed acquirable component, not a generic SEC definition."""
    if not text:
        return False
    normalized = _normalized_visible_text(text)
    return bool(
        re.search(
            r"\b(?:includes?|consists?\s+of|comprises?|reflects?)\b"
            r".{0,180}?"
            r"(?:\bshares?\b.{0,100}?\b(?:issuable|underlying|acquirable)\b|"
            r"\b(?:options?|warrants?)\b)",
            normalized,
            re.I,
        )
    )


def _named_acquirable_components(text: str | None) -> dict[str, float]:
    """Parse an exhaustive `following persons` list of future components."""
    if not text:
        return {}
    normalized = _normalized_visible_text(text)
    match = re.search(
        r"for\s+the\s+following\s+persons?.{0,240}?"
        r"(?:options?|awards?).{0,180}?:\s*(?P<items>[^.]{1,900})\.",
        normalized,
        re.I,
    )
    if not match:
        return {}
    result: dict[str, float] = {}
    for item in re.finditer(
        r"(?P<name>[A-Z][A-Za-z .'-]{2,80}?)\s*\((?P<shares>[0-9][0-9,]*)\)",
        match.group("items"),
    ):
        key = normalized_name_key(item.group("name"))
        shares = _number(item.group("shares"))
        if key and shares is not None:
            result[key] = float(shares)
    return result


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
            r"share ownership|shares owned|ownership)\b"
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
        r"\bShares Beneficially Owned\b|\bShares Owned\b",
        full_text,
        re.I,
    )
    header = beneficial_owner_header or share_ownership_header
    if not header:
        return []
    footnotes = _proxy_footnotes(full_text, header.start())
    document_mentions_multiple_ordinary_classes = bool(
        re.search(r"Class\s+A ordinary shares", full_text, re.I)
        and re.search(r"Class\s+B ordinary shares", full_text, re.I)
    )
    availability = availability_policy.resolve(accepted_at, form)
    results: list[SourceObservation] = []
    zero_management = re.search(
        r"\b(?:Unit|Share|Stock)\s+Ownership\s+of\s+Management\b"
        r"(?P<section>.{0,1400}?)"
        r"(?=\b(?:Changes\s+in\s+Control|Certain\s+Relationships|"
        r"ITEM\s+1[3-9])\b|$)",
        full_text,
        re.I,
    )
    if zero_management:
        zero_section = zero_management.group("section")
        explicit_zero = bool(
            re.search(
                r"\bNeither\b.{1,500}?\bowns?\s+any\s+"
                r"(?:Units|Shares|Stock)\b",
                zero_section,
                re.I,
            )
            or re.search(
                r"\bNo\s+(?:Units|Shares)\s+are\s+owned\s+by\b",
                zero_section,
                re.I,
            )
        )
        if explicit_zero:
            measurement_at = normalize_date((accepted_at or "")[:10])
            results.append(
                SourceObservation(
                    observation_id=stable_id(
                        "sec_explicit_zero_management_ownership_v0_1",
                        cik,
                        accession_number,
                        measurement_at,
                    ),
                    observation_type="HOLDER_POSITION_SNAPSHOT",
                    cik=cik,
                    accession_number=accession_number,
                    form=form,
                    instrument_id=instrument_id,
                    security_class_id=security_class_id,
                    value=0.0,
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
                    source_excerpt=_normalized_visible_text(
                        zero_management.group(0)
                    )[:1000],
                    extraction_method="SEC_EXPLICIT_ZERO_MANAGEMENT_OWNERSHIP_V0_1",
                    quality_state="CANDIDATE_REQUIRES_OVERLAP_RESOLUTION",
                    causality_state=availability.state,
                    attributes={
                        "holder_cik": None,
                        "holder_name": "Management ownership explicitly reported as zero",
                        "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
                        "direct_or_indirect": None,
                        "security_title": "Common Stock",
                        "reported_percent": 0.0,
                        "holder_category": "AGGREGATE_GROUP",
                        "footnote_marker": None,
                        "footnote_text": None,
                        "footnote_texts": [],
                        "supported_issued_common_shares": 0.0,
                        "ownership_component_state": (
                            "EXPLICIT_ZERO_CURRENTLY_ISSUED_MANAGEMENT_OWNERSHIP"
                        ),
                        "explicit_affiliate_candidate": False,
                        "table_class_basis": "SINGLE_OR_UNSPECIFIED",
                        "measurement_date_basis": (
                            "PRESENT_TENSE_ZERO_AS_OF_FILING_ACCEPTANCE_DATE"
                        ),
                    },
                )
            )
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
                r"(?:Number\s+of\s+)?Shares(?:\s+of\s+.{1,80}?)?\s+"
                r"Beneficially\s+Owned|Shares\s+Beneficially\s+Owned",
                table_text,
                re.I,
            )
            and re.search(r"(?:\bPercent(?:age)?\b|%)", table_text, re.I)
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
        table_mentions_multiple_classes = bool(
            re.search(r"\bClass\s+A\b", table_text, re.I)
            and re.search(r"\bClass\s+B\b", table_text, re.I)
        )
        nearby_table_context = (
            full_text[max(0, table_start - 1800) : table_start]
            if table_start >= 0
            else ""
        )
        nearby_mentions_multiple_ordinary_classes = bool(
            re.search(r"Class\s+A ordinary shares", nearby_table_context, re.I)
            and re.search(r"Class\s+B ordinary shares", nearby_table_context, re.I)
        )
        explicit_unnumbered_common_table = bool(
            re.search(
                r"(?:Common\s+Stock\s+Beneficially\s+Owned|"
                r"Shares\s+of\s+Common\s+Stock\s+Beneficially\s+Owned)",
                table_text,
                re.I,
            )
            and not table_mentions_multiple_classes
        )
        row_requires_class_allocation = bool(
            table_mentions_multiple_classes
            or (
                nearby_mentions_multiple_ordinary_classes
                and not explicit_unnumbered_common_table
            )
        )
        share_ownership_multiclass_table = bool(
            share_ownership_header
            and table_mentions_multiple_classes
            and _is_aggregate_management(table_text)
            and re.search(
                r"\bOwnership\b|%\s+of\s+Class\b|"
                r"\bPercent(?:age)?\s+of\s+Class\b",
                table_text,
                re.I,
            )
        )
        single_class_aggregate_table = bool(
            _is_aggregate_management(table_text)
            and not table_mentions_multiple_classes
            and re.search(
                r"\b(?:Number\s+of\s+Shares|Shares\s+Owned|"
                r"Shares\s+Beneficially\s+Owned|Amount\s+and\s+Nature\s+of\s+"
                r"Beneficial\s+Ownership|Beneficial\s+Ownership\s+as\s+of)\b",
                table_text,
                re.I,
            )
            and not re.search(
                r"\b(?:Subject\s+to\s+Grant|Equity\s+Awards?|Option\s+Awards?)\b",
                table_prefix,
                re.I,
            )
            and re.search(r"(?:\bPercent(?:age)?\b|%)", table_prefix, re.I)
        )
        if not (
            standard_table
            or shares_beneficially_owned_table
            or beneficial_owner_shares_owned_table
            or share_ownership_multiclass_table
            or single_class_aggregate_table
        ):
            continue
        following_table_notes: list[str] = []
        following_table_notes_length = 0
        for sibling in table.next_siblings:
            sibling_name = getattr(sibling, "name", None)
            if sibling_name in {
                "table", "h1", "h2", "h3", "h4", "h5", "h6"
            }:
                break
            sibling_text = _normalized_visible_text(
                " ".join(sibling.stripped_strings)
                if hasattr(sibling, "stripped_strings")
                else str(sibling)
            )
            if sibling_text:
                following_table_notes.append(sibling_text)
                following_table_notes_length += len(sibling_text)
            if following_table_notes_length >= 5000:
                break
        following_notes_text = _following_table_notes(table)
        table_notes = _numbered_notes(following_notes_text)
        named_acquirable_components = _named_acquirable_components(following_notes_text)
        table_option_context = " ".join((table_text, following_notes_text))
        explicit_current_shares_column = bool(
            re.search(
                r"(?<!Total\s)(?:"
                r"Number\s+of\s+Shares\s+of\s+Common\s+Stock\s+Owned|"
                r"Shares\s+of\s+common\s+stock\s+beneficially\s+owned|"
                r"Number\s+of\s+Shares\s+Beneficially\s+Owned|"
                r"Number\s+of\s+Shares\s+Beneficially\s+Held|"
                r"Common\s+Stock\s+Outstanding"
                r")",
                table_text,
                re.I,
            )
            or (
                re.search(r"\bCommon\s+Stock\b", table_text, re.I)
                and re.search(r"\bOutstanding\b", table_text, re.I)
            )
        )
        explicit_acquirable_shares_column = bool(
            re.search(
                r"(?:"
                r"Number\s+of\s+Shares\s+of\s+Common\s+Stock\s+"
                r"Acquirable\s+Within\s+\d+\s+Days|"
                r"Shares\s+acquirable\s+upon\s+exercise\s+of\s+options|"
                r"Shares\s+of\s+common\s+stock\s+issuable\s+upon\s+"
                r"exercise\s+of\s+(?:stock\s+)?options|"
                r"Right\s+to\s+Acquire|"
                r"Number\s+of\s+Shares\s+Issuable\s+Upon\s+Exercise\s+of\s+"
                r"Warrants\s+and\s+Options"
                r")",
                table_text,
                re.I,
            )
            or (
                re.search(r"\bRight\s+to\b", table_text, re.I)
                and re.search(r"\bAcquire\b", table_text, re.I)
            )
        )
        separates_current_and_acquirable_shares = bool(
            explicit_current_shares_column and explicit_acquirable_shares_column
        )
        explicit_total_shares_column = bool(
            re.search(
                r"\bTotal\s+(?:Shares\s+)?Beneficially\s+Owned\b|"
                r"\bTotal\s+Shares\b",
                table_text,
                re.I,
            )
        )
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
        exact_multiclass_rows = _explicit_multiclass_table_rows(table)
        if exact_multiclass_rows:
            for parsed_row in exact_multiclass_rows:
                holder_raw = str(parsed_row["holder_raw"])
                marker = re.search(r"\((\d+)\)\s*$", holder_raw)
                holder_name = re.sub(r"\s*\(\d+\)\s*$", "", holder_raw).strip(" :")
                footnote = (
                    table_notes.get(marker.group(1)) or footnotes.get(marker.group(1))
                    if marker
                    else None
                )
                class_a_shares = float(parsed_row["class_a"])
                class_b_shares = float(parsed_row["class_b"])
                shares = class_a_shares + class_b_shares
                security_kind = str(parsed_row["security_kind"])
                if security_kind == "shares" and (
                    document_mentions_multiple_ordinary_classes
                    or nearby_mentions_multiple_ordinary_classes
                ):
                    security_kind = "ordinary shares"
                attrs = {
                    "holder_cik": None,
                    "holder_name": holder_name,
                    "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
                    "direct_or_indirect": None,
                    "security_title": "MULTI_CLASS_ORDINARY_SHARES",
                    "reported_percent": None,
                    "reported_beneficial_total_shares": shares,
                    "holder_category": parsed_row["holder_category"],
                    "footnote_marker": marker.group(1) if marker else None,
                    "footnote_text": footnote,
                    "footnote_texts": [footnote] if footnote else [],
                    "supported_issued_common_shares": None,
                    "ownership_component_state": "EXPLICIT_TABLE_CLASS_COMPONENTS",
                    "explicit_affiliate_candidate": bool(
                        re.search(r"\bsponsor\b", holder_name, re.I)
                        or re.search(r"\bsponsor\b", footnote or "", re.I)
                    ),
                    "table_class_basis": "MULTI_CLASS_ORDINARY_SHARES",
                    "measurement_date_basis": measurement_basis,
                    "current_share_selection_state": "EXACT_TABLE_CLASS_COMPONENTS",
                    "reported_class_components": [
                        {
                            "security_class_title": f"Class A {security_kind}",
                            "shares": class_a_shares,
                        },
                        {
                            "security_class_title": f"Class B {security_kind}",
                            "shares": class_b_shares,
                        },
                    ],
                }
                results.append(
                    SourceObservation(
                        observation_id=stable_id(
                            "sec_explicit_multiclass_ownership_table_v0_2",
                            cik,
                            accession_number,
                            holder_name,
                            class_a_shares,
                            class_b_shares,
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
                        source_excerpt=" ".join(parsed_row["cells"])[:1000],
                        extraction_method="SEC_EXPLICIT_MULTICLASS_OWNERSHIP_TABLE_V0_2",
                        quality_state="CANDIDATE_REQUIRES_CLASS_ALLOCATION",
                        causality_state=availability.state,
                        attributes=attrs,
                    )
                )
            continue
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
                    if value in {"\u2014", "\u2013"}:
                        return 0.0
                    if value == "*":
                        return None
                    return _number(value)

                interleaved_class_percentages = bool(
                    re.search(
                        r"Class\s+A\s+Ordinary\s+Shares\s+%\s+of\s+Class\s+"
                        r"Class\s+B\s+Ordinary\s+Shares\s+%\s+of\s+Class",
                        table_text,
                        re.I,
                    )
                )
                class_b_index = 2 if interleaved_class_percentages else 1
                if len(slots) <= class_b_index:
                    continue
                class_a_shares = share_value(slots[0])
                class_b_shares = share_value(slots[class_b_index])
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
                percent = (
                    None
                    if interleaved_class_percentages
                    else (_number(slots[2]) if len(slots) > 2 else None)
                )
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
            footnote = (
                table_notes.get(marker.group(1)) or footnotes.get(marker.group(1))
                if marker
                else None
            )
            current_column_shares: float | None = None
            explicit_column_share_values: list[float] = []
            if separates_current_and_acquirable_shares:
                expected_share_values = 3 if explicit_total_shares_column else 2
                for value in compact[1:]:
                    normalized_value = value.strip()
                    if normalized_value in {"-", "\u2014", "\u2013", "\u200b"}:
                        explicit_column_share_values.append(0.0)
                    elif re.fullmatch(
                        r"[0-9][0-9,]*(?:\.[0-9]+)?", normalized_value
                    ):
                        parsed_value = _number(normalized_value)
                        if parsed_value is not None:
                            explicit_column_share_values.append(parsed_value)
                    if len(explicit_column_share_values) == expected_share_values:
                        break
                if explicit_column_share_values:
                    current_column_shares = explicit_column_share_values[0]
                if current_column_shares is None:
                    continue
            shares = float(
                current_column_shares
                if current_column_shares is not None
                else numeric[0]
            )
            exact_current_shares = _exact_current_shares_from_footnote(
                shares, footnote
            )
            named_component_current: float | None = None
            if named_acquirable_components and not separates_current_and_acquirable_shares:
                holder_key = normalized_name_key(holder_name)
                if row_category == "AGGREGATE_GROUP":
                    named_acquirable = sum(named_acquirable_components.values())
                else:
                    named_acquirable = next(
                        (
                            value for key, value in named_acquirable_components.items()
                            if key == holder_key or key in holder_key or holder_key in key
                        ),
                        0.0,
                    )
                if named_acquirable <= shares:
                    named_component_current = shares - named_acquirable
                    exact_current_shares = named_component_current
            row_option_context = footnote or table_option_context
            currently_issued_component_unresolved = bool(
                not separates_current_and_acquirable_shares
                and exact_current_shares is None
                and _has_position_specific_acquirable_disclosure(
                    row_option_context
                )
            )
            if exact_current_shares is not None:
                shares = exact_current_shares
            percent = (
                float(numeric[-1])
                if len(numeric) > 1
                and numeric[-1] is not None
                and re.search(r"(?:Percent(?:age)?|%)", table_text, re.I)
                else None
            )
            reported_beneficial_total_shares = float(numeric[0])
            if separates_current_and_acquirable_shares:
                reported_beneficial_total_shares = float(
                    explicit_column_share_values[2]
                    if explicit_total_shares_column
                    and len(explicit_column_share_values) >= 3
                    else sum(explicit_column_share_values[:2])
                )
            attrs = {
                "holder_cik": None,
                "holder_name": holder_name,
                "holding_type": "NON_DERIVATIVE_REPORTED_BENEFICIAL",
                "direct_or_indirect": None,
                "security_title": (
                    "MULTI_CLASS_ORDINARY_SHARES"
                    if row_requires_class_allocation
                    else "Common Stock"
                ),
                "reported_percent": percent,
                "reported_beneficial_total_shares": (
                    reported_beneficial_total_shares
                ),
                "holder_category": row_category,
                "footnote_marker": marker.group(1) if marker else None,
                "footnote_text": footnote,
                "footnote_texts": [footnote] if footnote else [],
                "supported_issued_common_shares": (
                    None
                    if row_requires_class_allocation
                    or currently_issued_component_unresolved
                    else shares
                ),
                "ownership_component_state": (
                    "MULTI_CLASS_ALLOCATION_REQUIRED"
                    if row_requires_class_allocation
                    else (
                        "CURRENTLY_ISSUED_COMPONENT_UNRESOLVED"
                        if currently_issued_component_unresolved
                        else "NO_MULTI_CLASS_CONFLICT_IDENTIFIED"
                    )
                ),
                "explicit_affiliate_candidate": bool(
                    re.search(r"\bsponsor\b", holder_name, re.I)
                    or re.search(r"\bsponsor\b", footnote or "", re.I)
                ),
                "table_class_basis": (
                    "MULTI_CLASS_ORDINARY_SHARES"
                    if row_requires_class_allocation
                    else "SINGLE_OR_UNSPECIFIED"
                ),
                "measurement_date_basis": measurement_basis,
                "current_share_selection_state": (
                    "EXPLICIT_CURRENT_SHARES_COLUMN"
                    if separates_current_and_acquirable_shares
                    else "EXHAUSTIVE_NAMED_ACQUIRABLE_COMPONENT_LIST"
                    if named_component_current is not None
                    else "EXACT_FOOTNOTE_COMPONENT_DECOMPOSITION"
                    if exact_current_shares is not None
                    else "TABLE_TOTAL_REQUIRES_COMPONENT_POLICY"
                ),
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
                    extraction_method="SEC_PROXY_OWNERSHIP_TABLE_V0_5",
                    quality_state=(
                        "CANDIDATE_REQUIRES_CLASS_ALLOCATION"
                        if row_requires_class_allocation
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
