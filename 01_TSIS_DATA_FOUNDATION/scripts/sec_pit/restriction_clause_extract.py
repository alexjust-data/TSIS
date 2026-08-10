from __future__ import annotations

import re

from bs4 import BeautifulSoup

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import stable_id
from sec_pit.models import SourceObservation

CLAUSE_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (
        "LOCKUP_RELEASE_AGREEMENT_REPORTED",
        r"share assignment and lock[ -]?up release agreement",
        "SPECIFIC_AGREEMENT",
    ),
    (
        "LOCKUP_TRANSFER_RESTRICTION_REPORTED",
        r"subject to.{0,180}(?:transfer restrictions|lock[ -]?up provisions)",
        "SPECIFIC_OR_CLASS_RESTRICTION",
    ),
    (
        "LOCKUP_EXPIRATION_RESALE_LANGUAGE",
        r"may be sold after the expiration of (?:their|the) respective lock[ -]?ups",
        "GENERAL_CLASS_LANGUAGE",
    ),
    (
        "RESTRICTED_SECURITIES_RULE_144_REPORTED",
        r"restricted securities under Rule 144",
        "GENERAL_CLASS_LANGUAGE",
    ),
    (
        "RULE_144_RESALE_ELIGIBILITY_LANGUAGE",
        r"(?:entitled to sell|resale would be saleable).{0,180}Rule 144",
        "GENERAL_ELIGIBILITY_LANGUAGE",
    ),
    (
        "RESTRICTIVE_LEGEND_CONDITION_REPORTED",
        r"(?:restrictive legend|legend removal|removal of (?:the )?legend)",
        "SPECIFIC_OR_GENERAL_CONDITION",
    ),
    (
        "RESALE_REGISTRATION_FILED_LANGUAGE",
        r"filed (?:one or more|multiple) (?:resale )?registration statements?"
        r".{0,180}(?:resale|selling holder|selling stockholder)",
        "GENERAL_REGISTRATION_LANGUAGE",
    ),
)


def extract_restriction_clause_candidates(
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
    if form.upper() == "EFFECT":
        return []
    text = re.sub(
        r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)
    ).strip()
    if not text:
        return []
    availability = availability_policy.resolve(accepted_at, form)
    observations: list[SourceObservation] = []
    for clause_type, pattern, specificity in CLAUSE_PATTERNS:
        match = re.search(pattern, text, re.I)
        if not match:
            continue
        excerpt = text[max(0, match.start() - 350) : min(len(text), match.end() + 650)]
        observations.append(
            SourceObservation(
                observation_id=stable_id(
                    "restriction_clause_candidate_v0_1",
                    cik,
                    accession_number,
                    clause_type,
                    excerpt,
                ),
                observation_type="SHARE_RESTRICTION_CLAUSE_CANDIDATE",
                cik=cik,
                accession_number=accession_number,
                form=form,
                instrument_id=instrument_id,
                security_class_id=security_class_id,
                value=None,
                unit=None,
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
                source_excerpt=excerpt[:2000],
                extraction_method="SEC_RESTRICTION_CLAUSE_REGEX_V0_1",
                quality_state="CLAUSE_CANDIDATE_REQUIRES_SHARE_LOT_LINKAGE",
                causality_state=availability.state,
                attributes={
                    "restriction_clause_type": clause_type,
                    "clause_specificity": specificity,
                    "condition_state": "REPORTED_NOT_RESOLVED",
                    "share_lot_linkage_state": "UNRESOLVED",
                    "tradable_supply_confirmation": False,
                },
            )
        )
    return observations
