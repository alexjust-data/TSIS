"""Conservative extraction of regulatory lifecycle source observations."""

from __future__ import annotations

import gzip
import json
import re
import warnings
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

EXCHANGE_PATTERNS = (
    ("NASDAQ", re.compile(r"\b(?:The\s+)?Nasdaq(?: Stock Market LLC| Global Market| Capital Market)?\b", re.I)),
    ("NYSE", re.compile(r"\b(?:The\s+)?New York Stock Exchange\b|\bNYSE\b", re.I)),
    ("NYSE_AMERICAN", re.compile(r"\bNYSE American\b", re.I)),
    ("OTC", re.compile(r"\bOTCQX\b|\bOTCQB\b|\bOTC Markets?\b", re.I)),
)
DATE_PATTERN = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{1,2},\s+\d{4}\b|\b20\d{2}-\d{2}-\d{2}\b",
    re.I,
)
ITEM_301_START = re.compile(r"\bItem\s+3\.01\b[\s.:;-]*", re.I)
NEXT_ITEM = re.compile(r"\bItem\s+(?!3\.01\b)\d+\.\d+\b", re.I)


def load_payload(path: Path) -> bytes:
    payload = path.read_bytes()
    return gzip.decompress(payload) if path.suffix == ".gz" else payload


def parse_document(payload: bytes) -> tuple[BeautifulSoup, str, str]:
    stripped = payload.lstrip()
    is_xml = stripped.startswith(b"<?xml") or stripped.startswith(b"<notificationOfRemoval")
    parser = "xml" if is_xml else "lxml"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(payload, parser)
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
    return soup, text, "XML" if is_xml else "HTML_OR_TEXT"


def item_301_section(text: str) -> str | None:
    match = ITEM_301_START.search(text)
    if not match:
        return None
    tail = text[match.start():]
    next_match = NEXT_ITEM.search(tail, match.end() - match.start())
    section = tail[: next_match.start()] if next_match else tail
    return section[:12000].strip()


def exchange_mentions(text: str) -> list[str]:
    return [name for name, pattern in EXCHANGE_PATTERNS if pattern.search(text)]


def date_mentions(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0) for match in DATE_PATTERN.finditer(text)))


def classify_item_301(section: str | None) -> list[str]:
    if not section:
        return ["ITEM_3_01_SECTION_NOT_FOUND"]
    lowered = section.lower()
    labels: list[str] = []
    if (
        "has regained compliance" in lowered
        or "regained compliance" in lowered
        or re.search(r"notified.{0,160}regained compliance", lowered)
    ):
        labels.append("CONTINUED_LISTING_COMPLIANCE_REGAINED")
    if (
        "deficiency notice" in lowered
        or "failed to comply" in lowered
        or "does not comply" in lowered
        or "noncompliance" in lowered
        or "non-compliance" in lowered
        or "not in compliance" in lowered
    ):
        labels.append("CONTINUED_LISTING_NONCOMPLIANCE_NOTICE")
    if (
        "transfer the listing" in lowered
        or "transfer its listing" in lowered
        or "trading will commence on the nyse" in lowered
    ):
        labels.append("LISTING_TRANSFER")
    if "voluntarily withdraw" in lowered or "voluntary withdrawal" in lowered:
        labels.append("VOLUNTARY_WITHDRAWAL")
    if (
        "will be delisted" in lowered
        or "determined to delist" in lowered
        or "delisting determination" in lowered
        or "staff delisting" in lowered
        or "suspend trading" in lowered
        or "will suspend" in lowered
    ):
        labels.append("DELISTING_OR_SUSPENSION_ACTION")
    return labels or ["ITEM_3_01_OTHER_OR_UNRESOLVED"]


def _clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" \t\r\n:;|")


def extract_table_security_mentions(soup: BeautifulSoup) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    seen: set[tuple[str | None, str | None, str | None]] = set()
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [_clean_cell(cell.get_text(" ", strip=True)) for cell in tr.find_all(["th", "td"])]
            cells = [cell for cell in cells if cell]
            if cells:
                rows.append(cells)
        header_index = None
        header_text = ""
        for index, cells in enumerate(rows):
            joined = " | ".join(cells).lower()
            if "title of each class" in joined or "title for each class" in joined:
                header_index = index
                header_text = joined
                break
        if header_index is None:
            continue
        for cells in rows[header_index + 1:]:
            joined = " | ".join(cells)
            if any(
                marker in joined.lower()
                for marker in (
                    "indicate by check mark",
                    "if this form relates",
                    "securities act registration",
                )
            ):
                break
            exchanges = exchange_mentions(joined)
            if not exchanges:
                continue
            title = cells[0] if cells else None
            symbol = cells[1] if len(cells) >= 3 and "trading symbol" in header_text else None
            exchange = cells[-1] if len(cells) >= 2 else exchanges[0]
            key = (title, symbol, exchange)
            if key in seen:
                continue
            seen.add(key)
            mentions.append(
                {
                    "security_title_candidate": title,
                    "trading_symbol_candidate": symbol,
                    "exchange_candidate": exchange,
                    "exchange_normalized_candidates_json": json.dumps(exchanges),
                    "mention_method": "HTML_TABLE_ROW",
                }
            )
    return mentions


def _find_tag_case_insensitive(parent: Any, name: str) -> Any:
    target = name.lower()
    return parent.find(lambda tag: bool(tag.name) and str(tag.name).lower() == target)


def extract_form25_fields(soup: BeautifulSoup, text: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "issuer_name_candidate": None,
        "exchange_name_candidate": None,
        "security_description_candidate": None,
        "rule_provision_candidate": None,
        "signature_date_candidate": None,
    }
    root = _find_tag_case_insensitive(soup, "notificationOfRemoval")
    if root:
        exchange = _find_tag_case_insensitive(root, "exchange")
        issuer = _find_tag_case_insensitive(root, "issuer")
        result.update(
            {
                "issuer_name_candidate": (
                    _find_tag_case_insensitive(issuer, "entityName").get_text(" ", strip=True)
                    if issuer and _find_tag_case_insensitive(issuer, "entityName")
                    else None
                ),
                "exchange_name_candidate": (
                    _find_tag_case_insensitive(exchange, "entityName").get_text(" ", strip=True)
                    if exchange and _find_tag_case_insensitive(exchange, "entityName")
                    else None
                ),
                "security_description_candidate": (
                    _find_tag_case_insensitive(root, "descriptionClassSecurity").get_text(" ", strip=True)
                    if _find_tag_case_insensitive(root, "descriptionClassSecurity")
                    else None
                ),
                "rule_provision_candidate": (
                    _find_tag_case_insensitive(root, "ruleProvision").get_text(" ", strip=True)
                    if _find_tag_case_insensitive(root, "ruleProvision")
                    else None
                ),
                "signature_date_candidate": (
                    _find_tag_case_insensitive(root, "signatureDate").get_text(" ", strip=True)
                    if _find_tag_case_insensitive(root, "signatureDate")
                    else None
                ),
            }
        )
        return result

    issuer_exchange = re.search(
        r"Commission File Number:\s*\S+\s+(.{2,180}?)\s+"
        r"((?:The\s+)?Nasdaq[^()]{0,60}|(?:The\s+)?New York Stock Exchange|NYSE[^()]{0,40})"
        r"\s+\(Exact name of Issuer",
        text,
        re.I,
    )
    if issuer_exchange:
        result["issuer_name_candidate"] = _clean_cell(issuer_exchange.group(1))
        result["exchange_name_candidate"] = _clean_cell(issuer_exchange.group(2))
    security = re.search(
        r"\(Address.{0,260}?principal executive offices\)\s+(.{2,220}?)\s+"
        r"\(Description of class of securities\)",
        text,
        re.I,
    )
    if security:
        result["security_description_candidate"] = _clean_cell(security.group(1))
    # HTML Form 25 signature dates require a labeled-field extractor.
    result["signature_date_candidate"] = None
    return result


def identity_timing_state(filing_date: Any, first_observed_snapshot: Any) -> str:
    if not filing_date or not first_observed_snapshot:
        return "IDENTITY_TIMING_UNAVAILABLE"
    filing = str(filing_date)[:10]
    first = str(first_observed_snapshot)[:10]
    return (
        "PRE_OBSERVED_TARGET_INTERVAL"
        if filing < first
        else "WITHIN_OR_AFTER_OBSERVED_TARGET_INTERVAL"
    )


def target_symbol_state(target_ticker: str, mentions: list[dict[str, Any]]) -> str:
    symbols = {
        str(row["trading_symbol_candidate"]).upper()
        for row in mentions
        if row.get("trading_symbol_candidate")
    }
    if target_ticker.upper() in symbols:
        return "TARGET_TICKER_EXPLICITLY_MENTIONED"
    if symbols:
        return "OTHER_OR_PREDECESSOR_TICKER_MENTIONED"
    return "TRADING_SYMBOL_NOT_EXTRACTED"


def extract_lifecycle_observation(
    source: dict[str, Any],
    *,
    first_observed_snapshot: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    object_path = Path(str(source["object_path"]))
    payload = load_payload(object_path)
    soup, text, physical_format = parse_document(payload)
    candidate_type = str(source["candidate_type"])
    mentions = extract_table_security_mentions(soup)
    section = item_301_section(text) if candidate_type == "ITEM_3_01_DISCLOSURE_CANDIDATE" else None
    form25 = (
        extract_form25_fields(soup, text)
        if candidate_type == "FORM_25_FILING_CANDIDATE"
        else {}
    )

    if candidate_type == "REGISTRATION_FILING_CANDIDATE":
        form = str(source.get("form") or "").upper()
        labels = [
            "REGISTRATION_SECTION_12B"
            if "12B" in form
            else "REGISTRATION_SECTION_12G"
            if "12G" in form
            else "REGISTRATION_SECTION_UNRESOLVED"
        ]
        if form.endswith("/A"):
            labels.append("REGISTRATION_AMENDMENT")
        evidence = text[:4000]
    elif candidate_type == "FORM_25_FILING_CANDIDATE":
        labels = ["FORM_25_REMOVAL_NOTIFICATION"]
        evidence = text[:4000]
        if form25.get("security_description_candidate"):
            mentions.append(
                {
                    "security_title_candidate": form25["security_description_candidate"],
                    "trading_symbol_candidate": None,
                    "exchange_candidate": form25.get("exchange_name_candidate"),
                    "exchange_normalized_candidates_json": json.dumps(
                        exchange_mentions(str(form25.get("exchange_name_candidate") or ""))
                    ),
                    "mention_method": "FORM_25_STRUCTURED_OR_LABELED_FIELD",
                }
            )
    else:
        labels = classify_item_301(section)
        evidence = (section or text[:4000])[:4000]

    ticker = str(source["ticker"])
    observation = {
        "ticker": ticker,
        "instrument_id": source.get("instrument_id"),
        "security_class_id": source.get("security_class_id"),
        "cik": source.get("cik"),
        "accession_number": source.get("accession_number"),
        "form": source.get("form"),
        "candidate_type": candidate_type,
        "filing_date": source.get("filing_date"),
        "filing_accepted_at": source.get("filing_accepted_at"),
        "eligible_from_session": source.get("eligible_from_session"),
        "source_url": source.get("primary_document_url"),
        "source_sha256": source.get("sha256"),
        "source_object_path": object_path.as_posix(),
        "physical_format": physical_format,
        "event_type_candidates_json": json.dumps(labels),
        "reported_date_candidates_json": json.dumps(date_mentions(evidence)),
        "exchange_candidates_json": json.dumps(exchange_mentions(evidence)),
        "issuer_name_candidate": form25.get("issuer_name_candidate"),
        "security_description_candidate": form25.get("security_description_candidate"),
        "rule_provision_candidate": form25.get("rule_provision_candidate"),
        "signature_date_candidate": form25.get("signature_date_candidate"),
        "item_3_01_section_found": section is not None,
        "security_mention_count": len(mentions),
        "target_symbol_state": target_symbol_state(ticker, mentions),
        "identity_timing_state": identity_timing_state(
            source.get("filing_date"), first_observed_snapshot
        ),
        "event_effective_at": None,
        "first_trade_at": None,
        "last_trade_at": None,
        "event_resolution_state": (
            "SOURCE_OBSERVATION_EXTRACTED_REQUIRES_IDENTITY_CLASS_DATE_"
            "AND_MARKET_RECONCILIATION"
        ),
        "evidence_snippet": evidence,
        "extraction_method": "SEC_LIFECYCLE_PRIMARY_RULES_V0_1",
        "promotion_status": "NOT_AUTHORIZED",
    }
    mention_rows = []
    for index, mention in enumerate(mentions, start=1):
        mention_rows.append(
            {
                "ticker": ticker,
                "accession_number": source.get("accession_number"),
                "mention_index": index,
                **mention,
                "target_symbol_match": (
                    str(mention.get("trading_symbol_candidate") or "").upper()
                    == ticker.upper()
                ),
                "source_sha256": source.get("sha256"),
                "extraction_method": "SEC_LIFECYCLE_PRIMARY_RULES_V0_1",
            }
        )
    return observation, mention_rows