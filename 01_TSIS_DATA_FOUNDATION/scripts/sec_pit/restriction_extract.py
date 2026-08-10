from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET

import pandas as pd
from bs4 import BeautifulSoup

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import stable_id
from sec_pit.models import SourceObservation


def _text(root: ET.Element, suffix: str) -> str | None:
    for node in root.iter():
        if node.tag.split("}")[-1] == suffix and node.text and node.text.strip():
            return node.text.strip()
    return None


def _number(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def extract_registration_scope_clause_candidates(
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
    if form.upper() != "424B3":
        return []
    text = re.sub(
        r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    ).strip()
    header = text[:8000]
    file_match = re.search(
        r"Registration\s+(?:Statement\s+)?No\.?\s*(333-\d{6})",
        header,
        re.I,
    )
    start = text.lower().find("this prospectus relates")
    if not file_match or start < 0:
        return []
    end_markers = [
        text.lower().find(marker, start + 1)
        for marker in (
            "collectively referred to in this prospectus",
            "we will not receive any of the proceeds",
        )
    ]
    valid_ends = [value for value in end_markers if value > start]
    narrative_end = min(valid_ends) if valid_ends else min(len(text), start + 6000)
    narrative = text[start:narrative_end]
    availability = availability_policy.resolve(accepted_at, form)
    observations: list[SourceObservation] = []
    component_matches = list(
        re.finditer(
            r"([0-9][0-9,]*)\s+shares of (?:our )?Common Stock",
            narrative,
            re.I,
        )
    )
    for component_index, match in enumerate(component_matches):
        value = _number(match.group(1))
        if value is None:
            continue
        before = narrative[max(0, match.start() - 120) : match.start()].lower()
        next_start = (
            component_matches[component_index + 1].start()
            if component_index + 1 < len(component_matches)
            else min(len(narrative), match.end() + 500)
        )
        after_clause = narrative[match.end() : next_start].lower()
        context = narrative[
            max(0, match.start() - 120) : min(len(narrative), max(next_start, match.end() + 220))
        ]
        combined = f"{before} {after_clause}"
        component_prefix = before[-40:]
        if "including" in after_clause and not any(
            token in after_clause for token in ("held by", "issued to", "transferred")
        ):
            classification = "AGGREGATE_REGISTRATION_LIMIT"
            issued_common_state = "NOT_A_CURRENT_SHARE_COMPONENT"
        elif "average price" in after_clause and "exceed" in combined:
            classification = "CONDITIONAL_THRESHOLD_NOT_COMPONENT"
            issued_common_state = "NOT_A_CURRENT_SHARE_COMPONENT"
        elif any(
            token in after_clause
            for token in (
                "underlying",
                "issuable",
                "may be issued",
                "we may",
                "may issue",
                "upon exercise",
                "warrants to purchase",
                "issuable pursuant",
                "pricing option",
            )
        ) or any(
            token in component_prefix
            for token in (
                "underlying",
                "warrants to purchase",
            )
        ):
            classification = "CONTINGENT_OR_FUTURE"
            issued_common_state = "NOT_CURRENT_ISSUED_COMMON"
        elif "transferred" in after_clause:
            classification = "REPORTED_TRANSFERRED"
            issued_common_state = "REQUIRES_OS_RECONCILIATION"
        elif "issued to" in after_clause or "were issued" in after_clause:
            classification = "REPORTED_ISSUED"
            issued_common_state = "REQUIRES_OS_RECONCILIATION"
        elif "held by" in after_clause:
            classification = "REPORTED_HELD"
            issued_common_state = "REQUIRES_OS_RECONCILIATION"
        elif re.search(r"\([a-z]+\)\s+up to\s*$", component_prefix):
            classification = "REPORTED_COMMON_STOCK_OFFER_COMPONENT"
            issued_common_state = "REQUIRES_OS_RECONCILIATION"
        else:
            classification = "UNRESOLVED"
            issued_common_state = "UNRESOLVED"
        issuer_scope = (
            "issuance by us" in before
            or "we may" in after_clause
            or "company agreed to issue" in combined
        )
        observations.append(
            SourceObservation(
                observation_id=stable_id(
                    "registration_scope_clause_v0_2",
                    cik,
                    accession_number,
                    component_index,
                    value,
                    classification,
                    context,
                ),
                observation_type="REGISTRATION_SCOPE_COMPONENT_CANDIDATE",
                cik=cik,
                accession_number=accession_number,
                form=form,
                instrument_id=instrument_id,
                security_class_id=security_class_id,
                value=value,
                unit="shares",
                measurement_at=None,
                effective_at=None,
                filing_accepted_at=accepted_at,
                eligible_from_session=(
                    availability.eligible_from_session.isoformat()
                    if availability.eligible_from_session
                    else None
                ),
                availability_policy_id=availability.policy_id,
                source_url=source_url,
                source_sha256=source_sha256,
                source_excerpt=context[:2000],
                extraction_method="SEC_424B3_REGISTRATION_SCOPE_CLAUSE_V0_2",
                quality_state="CLAUSE_CANDIDATE_REQUIRES_COMPONENT_RECONCILIATION",
                causality_state=availability.state,
                attributes={
                    "file_number": file_match.group(1),
                    "component_index": component_index,
                    "component_classification": classification,
                    "issued_common_state": issued_common_state,
                    "issuer_issuance_scope": issuer_scope,
                    "tradable_supply_confirmation": False,
                },
            )
        )
    return observations


def _normalized_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _first_table_number(row: pd.Series, indexes: list[int]) -> float | None:
    for index in indexes:
        value = _number(_normalized_cell(row.iloc[index]))
        if value is not None:
            return value
    return None


def extract_selling_holder_share_lots(
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
    if form.upper() != "424B3":
        return []
    text = re.sub(
        r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    ).strip()
    file_match = re.search(
        r"Registration\s+(?:Statement\s+)?No\.?\s*(333-\d{6})",
        text[:8000],
        re.I,
    )
    if not file_match:
        return []
    try:
        tables = pd.read_html(io.BytesIO(payload))
    except ValueError:
        return []
    availability = availability_policy.resolve(accepted_at, form)
    observations: list[SourceObservation] = []
    for table_index, table in enumerate(tables):
        if len(table) < 3:
            continue
        first_header = [_normalized_cell(value).lower() for value in table.iloc[0]]
        second_header = [_normalized_cell(value).lower() for value in table.iloc[1]]
        holder_indexes = [
            index for index, value in enumerate(second_header) if "name of selling holder" in value
        ]
        beneficial_indexes = [
            index
            for index, (top, sub) in enumerate(zip(first_header, second_header, strict=True))
            if "beneficially owned" in top and "number" in sub and "after" not in top
        ]
        offered_indexes = [
            index
            for index, (top, sub) in enumerate(zip(first_header, second_header, strict=True))
            if "maximum" in top and "common stock" in top and "offered" in top and "offered" in sub
        ]
        after_indexes = [
            index
            for index, (top, sub) in enumerate(zip(first_header, second_header, strict=True))
            if "beneficially owned after" in top and "number" in sub
        ]
        if not holder_indexes or not offered_indexes:
            continue
        for row_index in range(2, len(table)):
            row = table.iloc[row_index]
            holder_raw = _normalized_cell(row.iloc[holder_indexes[0]])
            if not holder_raw or holder_raw.lower().startswith("total"):
                continue
            holder_name = re.sub(r"\s*\(\d+\)\s*$", "", holder_raw).strip()
            beneficial = _first_table_number(row, beneficial_indexes)
            offered = _first_table_number(row, offered_indexes)
            after = _first_table_number(row, after_indexes)
            if offered is None:
                continue
            observations.append(
                SourceObservation(
                    observation_id=stable_id(
                        "selling_holder_share_lot_v0_1",
                        cik,
                        accession_number,
                        table_index,
                        holder_name,
                        beneficial,
                        offered,
                        after,
                    ),
                    observation_type="SELLING_HOLDER_SHARE_LOT_CANDIDATE",
                    cik=cik,
                    accession_number=accession_number,
                    form=form,
                    instrument_id=instrument_id,
                    security_class_id=security_class_id,
                    value=offered,
                    unit="shares",
                    measurement_at=None,
                    effective_at=None,
                    filing_accepted_at=accepted_at,
                    eligible_from_session=(
                        availability.eligible_from_session.isoformat()
                        if availability.eligible_from_session
                        else None
                    ),
                    availability_policy_id=availability.policy_id,
                    source_url=source_url,
                    source_sha256=source_sha256,
                    source_excerpt=" | ".join(
                        _normalized_cell(value) for value in row if _normalized_cell(value)
                    )[:2000],
                    extraction_method="SEC_424B3_SELLING_HOLDER_TABLE_V0_1",
                    quality_state="SHARE_LOT_CANDIDATE_REQUIRES_COMPONENT_CLASSIFICATION",
                    causality_state=availability.state,
                    attributes={
                        "file_number": file_match.group(1),
                        "holder_name": holder_name,
                        "holder_name_reported": holder_raw,
                        "beneficial_common_shares_before": beneficial,
                        "maximum_common_shares_offered": offered,
                        "beneficial_common_shares_after_assuming_sale": after,
                        "offered_exceeds_current_beneficial": (
                            beneficial is not None and offered > beneficial
                        ),
                        "issued_common_classification": "UNRESOLVED",
                        "restriction_condition_state": "UNRESOLVED",
                        "tradable_supply_confirmation": False,
                        "source_table_index": table_index,
                        "source_row_index": row_index,
                    },
                )
            )
    return observations


def reconcile_registration_to_selling_lots(
    registration_rows: list[dict[str, object]],
    selling_lot_rows: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    cover_totals: dict[str, set[int]] = {}
    mixed_issuer_scope: dict[str, bool] = {}
    for row in registration_rows:
        attributes = row.get("attributes")
        if not isinstance(attributes, dict):
            continue
        file_number = attributes.get("file_number")
        total = attributes.get("cover_total_registered_common_shares")
        if isinstance(file_number, str) and isinstance(total, int | float):
            cover_totals.setdefault(file_number, set()).add(int(total))
            if bool(attributes.get("includes_issuer_issuance_scope")):
                mixed_issuer_scope[file_number] = True
    offered_by_accession: dict[str, dict[str, int]] = {}
    for row in selling_lot_rows:
        attributes = row.get("attributes")
        accession = row.get("accession_number")
        if not isinstance(attributes, dict) or not isinstance(accession, str):
            continue
        file_number = attributes.get("file_number")
        offered = attributes.get("maximum_common_shares_offered")
        if isinstance(file_number, str) and isinstance(offered, int | float):
            by_accession = offered_by_accession.setdefault(file_number, {})
            by_accession[accession] = by_accession.get(accession, 0) + int(offered)
    result: dict[str, dict[str, object]] = {}
    for file_number in sorted(cover_totals | offered_by_accession.keys()):
        covers = sorted(cover_totals.get(file_number, set()))
        accession_totals = offered_by_accession.get(file_number, {})
        matches = sorted(
            accession for accession, total in accession_totals.items() if total in covers
        )
        status = (
            "EXACT_MATCH"
            if matches
            else (
                "PARTIAL_MATCH_MIXED_ISSUER_ISSUANCE"
                if mixed_issuer_scope.get(file_number, False)
                else "MISMATCH"
            )
        )
        result[file_number] = {
            "status": status,
            "cover_totals": covers,
            "offered_totals_by_accession": dict(sorted(accession_totals.items())),
            "matching_accessions": matches,
            "minimum_absolute_difference": (
                min(
                    abs(offered - cover)
                    for offered in accession_totals.values()
                    for cover in covers
                )
                if accession_totals and covers
                else None
            ),
        }
    return result


def summarize_registration_component_conflicts(
    rows: list[dict[str, object]],
) -> dict[str, dict[str, list[float]]]:
    fields = (
        "cover_total_registered_common_shares",
        "cover_underlying_warrant_shares",
        "cover_underlying_convertible_note_shares",
        "cover_underlying_option_shares",
    )
    grouped: dict[str, dict[str, set[float]]] = {}
    for row in rows:
        attributes = row.get("attributes")
        if not isinstance(attributes, dict):
            continue
        file_number = attributes.get("file_number")
        if not isinstance(file_number, str):
            continue
        values = grouped.setdefault(file_number, {field: set() for field in fields})
        for field in fields:
            value = attributes.get(field)
            if isinstance(value, int | float):
                values[field].add(float(value))
    return {
        file_number: {
            field: sorted(values) for field, values in fields_by_name.items() if len(values) > 1
        }
        for file_number, fields_by_name in grouped.items()
        if any(len(values) > 1 for values in fields_by_name.values())
    }


def extract_effect_event(
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
    if form.upper() != "EFFECT":
        return []
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return []
    effective_date = _text(root, "finalEffectivenessDispDate")
    effective_time = _text(root, "finalEffectivenessDispTime")
    registration_form = _text(root, "form")
    file_number = _text(root, "fileNumber")
    if not effective_date or not file_number:
        return []
    effective_at = f"{effective_date}T{effective_time or '00:00:00'}"
    availability = availability_policy.resolve(accepted_at, form)
    return [
        SourceObservation(
            observation_id=stable_id(
                "effect_event_v0_1", cik, accession_number, file_number, effective_at
            ),
            observation_type="SHARE_RESTRICTION_EVENT",
            cik=cik,
            accession_number=accession_number,
            form=form,
            instrument_id=instrument_id,
            security_class_id=security_class_id,
            value=None,
            unit=None,
            measurement_at=effective_date,
            effective_at=effective_at,
            filing_accepted_at=accepted_at,
            eligible_from_session=(
                availability.eligible_from_session.isoformat()
                if availability.eligible_from_session
                else None
            ),
            availability_policy_id=availability.policy_id,
            source_url=source_url,
            source_sha256=source_sha256,
            source_excerpt=ET.tostring(root, encoding="unicode")[:1000],
            extraction_method="SEC_EFFECT_XML_V0_1",
            quality_state="ELIGIBILITY_EVENT_REQUIRES_SHARE_LOT_LINKAGE",
            causality_state=availability.state,
            attributes={
                "restriction_event_type": "RESALE_REGISTRATION_EFFECTIVE",
                "registration_form": registration_form,
                "file_number": file_number,
                "condition_state": "UNCONDITIONAL_EFFECTIVENESS_NOTICE",
                "tradable_supply_confirmation": False,
            },
        )
    ]


def extract_registration_component_candidate(
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
    if form.upper() != "424B3":
        return []
    text = re.sub(
        r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    ).strip()
    header = text[:8000]
    file_match = re.search(
        r"Registration\s+(?:Statement\s+)?No\.?\s*(333-\d{6})",
        header,
        re.I,
    )
    if not file_match:
        return []
    file_number = file_match.group(1)

    # SEC prospectus supplements often split the cover heading across tables.
    # Keep the search local so an underlying component cannot become the total.
    cover_block = header[file_match.start() : file_match.start() + 2500]
    cover_candidates = [
        _number(value)
        for value in re.findall(
            r"([0-9][0-9,]*)\s+Shares of (?:our )?Common Stock",
            cover_block,
            re.I,
        )
    ]
    cover_candidates = [value for value in cover_candidates if value is not None]
    if not cover_candidates:
        return []
    cover_total = max(cover_candidates)
    total_token = f"{int(cover_total):,}"
    total_match = re.search(
        rf"{re.escape(total_token)}\s+Shares of (?:our )?Common Stock",
        cover_block,
        re.I,
    )
    component_block = (
        cover_block[total_match.end() : total_match.end() + 900]
        if total_match
        else cover_block[:900]
    )

    def component(pattern: str) -> float | None:
        match = re.search(pattern, component_block, re.I | re.S)
        return _number(match.group(1)) if match else None

    held_candidates = sorted(
        {
            float(value.replace(",", ""))
            for value in re.findall(
                r"up to\s+([0-9][0-9,]*)\s+shares of (?:our )?common stock"
                r".{0,160}?held by",
                text[:30000],
                re.I | re.S,
            )
        }
    )
    future_candidates = sorted(
        {
            float(value.replace(",", ""))
            for value in re.findall(
                r"up to\s+([0-9][0-9,]*)\s+shares of (?:our )?common stock"
                r".{0,180}?(?:may be issued|issuable|underlying)",
                text[:30000],
                re.I | re.S,
            )
        }
    )
    availability = availability_policy.resolve(accepted_at, form)
    return [
        SourceObservation(
            observation_id=stable_id(
                "registration_component_v0_1",
                cik,
                accession_number,
                file_number,
                cover_total,
            ),
            observation_type="REGISTRATION_SHARE_COMPONENT_CANDIDATE",
            cik=cik,
            accession_number=accession_number,
            form=form,
            instrument_id=instrument_id,
            security_class_id=security_class_id,
            value=cover_total,
            unit="shares",
            measurement_at=None,
            effective_at=None,
            filing_accepted_at=accepted_at,
            eligible_from_session=(
                availability.eligible_from_session.isoformat()
                if availability.eligible_from_session
                else None
            ),
            availability_policy_id=availability.policy_id,
            source_url=source_url,
            source_sha256=source_sha256,
            source_excerpt=header[:2000],
            extraction_method="SEC_424B3_REGISTRATION_COMPONENT_V0_1",
            quality_state="MIXED_REGISTRATION_REQUIRES_SHARE_LOT_LINKAGE",
            causality_state=availability.state,
            attributes={
                "restriction_event_type": "RESALE_REGISTRATION_COMPONENT_CANDIDATE",
                "registration_form": form,
                "file_number": file_number,
                "cover_total_registered_common_shares": cover_total,
                "cover_underlying_warrant_shares": component(
                    r"([0-9][0-9,]*)\s+Shares of Common Stock Underlying Warrants"
                ),
                "cover_underlying_convertible_note_shares": component(
                    r"([0-9][0-9,]*)\s+Shares of Common Stock Underlying Convertible Notes"
                ),
                "cover_underlying_option_shares": component(
                    r"([0-9][0-9,]*)\s+Shares of Common Stock Underlying Options"
                ),
                "explicit_held_common_share_candidates": held_candidates,
                "explicit_future_issuance_share_candidates": future_candidates,
                "component_classification_state": (
                    "MIXED_ISSUED_AND_CONTINGENT_REQUIRES_SELLING_HOLDER_TABLE"
                ),
                "includes_issuer_issuance_scope": (
                    "this prospectus also relates to the issuance by us" in text.lower()
                ),
                "tradable_supply_confirmation": False,
            },
        )
    ]
