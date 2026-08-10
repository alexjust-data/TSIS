from __future__ import annotations

import re
from datetime import datetime

from bs4 import BeautifulSoup

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import stable_id
from sec_pit.models import SourceObservation


def _number(token: str) -> float:
    return float(token.replace(",", ""))


def _iso_date(value: str | None) -> str | None:
    if value is None:
        return None
    return datetime.strptime(value, "%B %d, %Y").date().isoformat()


def extract_assignment_restriction_events(
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
    text = re.sub(
        r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    ).strip()
    if "share assignment and lockup release agreement" not in text.lower():
        return []
    section_start = text.lower().find("assignment agreement")
    section_end = text.lower().find("standby equity purchase agreement", section_start)
    section = text[section_start : section_end if section_end > section_start else None]
    effective_match = re.search(
        r"on ([A-Z][a-z]+ \d{1,2}, \d{4}) \(the\s+[^A-Za-z0-9]?Assignment Effective Date",
        section,
        re.I,
    )
    effective_date = _iso_date(effective_match.group(1) if effective_match else None)
    aggregate_match = re.search(
        r"aggregate of ([0-9][0-9,]*) shares of Common Stock.*?Sponsor Securities",
        section,
        re.I,
    )
    release_match = re.search(
        r"release ([0-9][0-9,]*) shares of Common Stock from certain restrictions",
        section,
        re.I,
    )
    transfer_match = re.search(
        r"transfer,? an aggregate of ([0-9][0-9,]*) Sponsor Securities",
        section,
        re.I,
    )
    escrow_match = re.search(
        r"remaining ([0-9][0-9,]*) Sponsor Securities into the Share Escrow Account",
        section,
        re.I,
    )
    lockup_end_match = re.search(
        r"until the earliest of \(i\) ([A-Z][a-z]+ \d{1,2}, \d{4}) and \(ii\)",
        section,
    )
    volume_cap_match = re.search(
        r"amount representing more than ([0-9]+)% of the average daily trading volume",
        section,
        re.I,
    )
    availability = availability_policy.resolve(accepted_at, form)
    effective_at = effective_date
    aggregate = _number(aggregate_match.group(1)) if aggregate_match else None
    initial_transfer = _number(transfer_match.group(1)) if transfer_match else None
    escrow_reported = _number(escrow_match.group(1)) if escrow_match else None
    escrow_implied = (
        aggregate - initial_transfer
        if aggregate is not None and initial_transfer is not None
        else None
    )
    escrow_conflict = (
        escrow_reported is not None
        and escrow_implied is not None
        and escrow_reported != escrow_implied
    )
    specs = [
        (
            "SPONSOR_SECURITIES_ASSIGNMENT_REPORTED",
            aggregate,
            "REPORTED_EFFECTIVE_AGREEMENT",
            aggregate_match.group(0) if aggregate_match else None,
            {},
        ),
        (
            "LOCKUP_RELEASE_COMMITMENT_REPORTED",
            _number(release_match.group(1)) if release_match else None,
            "REPORTED_COMMITMENT_NOT_TRADABILITY",
            release_match.group(0) if release_match else None,
            {},
        ),
        (
            "SPONSOR_INITIAL_TRANSFER_SCHEDULED",
            initial_transfer,
            "SCHEDULED_NOT_CONFIRMED",
            transfer_match.group(0) if transfer_match else None,
            {"deadline_rule": "WITHIN_FIVE_BUSINESS_DAYS_OF_ASSIGNMENT"},
        ),
        (
            "SPONSOR_ESCROW_CONDITIONAL_RELEASE",
            None if escrow_conflict else escrow_reported,
            "SOURCE_CONFLICT" if escrow_conflict else "CONDITIONS_PENDING",
            escrow_match.group(0) if escrow_match else None,
            {
                "reported_raw_token": escrow_match.group(1) if escrow_match else None,
                "reported_numeric_value": escrow_reported,
                "implied_remainder_value": escrow_implied,
                "source_numeric_conflict": escrow_conflict,
                "release_condition": "REQUIRED_FUNDINGS_PRO_RATA",
                "failure_disposition": "RETURN_TO_COMPANY_AND_CANCEL",
            },
        ),
        (
            "SPONSOR_TRANSFER_VOLUME_RESTRICTION",
            None,
            "TIME_OR_CORPORATE_EVENT_CONDITION",
            lockup_end_match.group(0) if lockup_end_match else None,
            {
                "scheduled_end_date": _iso_date(
                    lockup_end_match.group(1) if lockup_end_match else None
                ),
                "alternative_end_condition": "LIQUIDATION_MERGER_SHARE_EXCHANGE",
                "maximum_adv_percent": (
                    float(volume_cap_match.group(1)) if volume_cap_match else None
                ),
            },
        ),
    ]
    observations: list[SourceObservation] = []
    for event_type, value, condition_state, excerpt, extra in specs:
        if excerpt is None:
            continue
        observations.append(
            SourceObservation(
                observation_id=stable_id(
                    "assignment_restriction_event_v0_1",
                    cik,
                    accession_number,
                    event_type,
                    excerpt,
                ),
                observation_type="SHARE_RESTRICTION_EVENT_CANDIDATE",
                cik=cik,
                accession_number=accession_number,
                form=form,
                instrument_id=instrument_id,
                security_class_id=security_class_id,
                value=value,
                unit="shares" if value is not None else None,
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
                source_excerpt=excerpt[:2000],
                extraction_method="SEC_ASSIGNMENT_RESTRICTION_EVENT_V0_1",
                quality_state=(
                    "SOURCE_NUMERIC_CONFLICT"
                    if condition_state == "SOURCE_CONFLICT"
                    else "EVENT_CANDIDATE_REQUIRES_SHARE_LOT_LINKAGE"
                ),
                causality_state=availability.state,
                attributes={
                    "restriction_event_type": event_type,
                    "condition_state": condition_state,
                    "share_lot_linkage_state": "UNRESOLVED",
                    "tradable_supply_confirmation": False,
                    **extra,
                },
            )
        )
    return observations
