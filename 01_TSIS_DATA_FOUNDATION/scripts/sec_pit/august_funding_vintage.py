from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from sec_pit.extract import stable_id


def _iso_date(value: str) -> str:
    return datetime.strptime(value, "%B %d, %Y").date().isoformat()


def _number(value: str) -> int:
    multiplier = 1_000_000 if "million" in value.lower() else 1
    match = re.search(r"\d[\d,]*(?:\.\d+)?", value)
    if match is None:
        raise ValueError(f"No numeric token in {value!r}")
    return round(float(match.group(0).replace(",", "")) * multiplier)


def extract_august_funding_vintages(
    payload: bytes,
    *,
    accession_number: str,
    form: str,
    filing_accepted_at: str,
    eligible_from_session: str,
    source_sha256: str,
) -> list[dict[str, Any]]:
    text = re.sub(r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings))
    events: list[dict[str, Any]] = []

    patterns = [
        (
            "AUGUST_ESCROW_RELEASE_REPORTED_UNATTRIBUTED",
            re.compile(
                r"As of ([A-Z][a-z]+ \d{1,2}, \d{4}), ([0-9,]+) shares of Common Stock "
                r"have been released from escrow upon payment by the August Purchasers",
                re.I,
            ),
        ),
        (
            "AUGUST_PURCHASER_SHARES_AND_PROCEEDS_REPORTED",
            re.compile(
                r"As of ([A-Z][a-z]+ \d{1,2}, \d{4}), a total of ([0-9,]+) shares[^.]{0,300}?"
                r"issued to(?: \d+ Table of Contents)? the August Purchasers[^.]{0,200}?"
                r"gross proceeds of \$\s*([0-9,.]+(?: million)?)",
                re.I,
            ),
        ),
        (
            "AUGUST_SPA_PARTIAL_TERMINATION_REPORTED",
            re.compile(
                r"As of ([A-Z][a-z]+ \d{1,2}, \d{4}), the August SPA has been terminated "
                r"with respect to certain August Purchasers[^.]*\.",
                re.I,
            ),
        ),
    ]

    seen: set[tuple[str, str, int | None, int | None]] = set()
    for event_type, pattern in patterns:
        for match in pattern.finditer(text):
            measurement_at = _iso_date(match.group(1))
            shares = _number(match.group(2)) if match.lastindex and match.lastindex >= 2 else None
            proceeds = _number(match.group(3)) if match.lastindex and match.lastindex >= 3 else None
            key = (event_type, measurement_at, shares, proceeds)
            if key in seen:
                continue
            seen.add(key)
            events.append(
                {
                    "event_id": stable_id("august_funding_vintage_v0_1", *key),
                    "event_type": event_type,
                    "measurement_at": measurement_at,
                    "shares_reported": shares,
                    "gross_proceeds_reported": proceeds,
                    "lot_attribution_state": (
                        "UNATTRIBUTED_ESCROW_LOT"
                        if event_type == "AUGUST_ESCROW_RELEASE_REPORTED_UNATTRIBUTED"
                        else "NOT_APPLICABLE_OR_REQUIRES_RESOLUTION"
                    ),
                    "termination_scope": (
                        "CERTAIN_PURCHASERS_UNIDENTIFIED"
                        if event_type == "AUGUST_SPA_PARTIAL_TERMINATION_REPORTED"
                        else None
                    ),
                    "cancellation_quantity": None,
                    "filing_accepted_at": filing_accepted_at,
                    "eligible_from_session": eligible_from_session,
                    "accession_number": accession_number,
                    "form": form,
                    "source_sha256": source_sha256,
                    "source_excerpt": match.group(0),
                    "tradable_supply_confirmation": False,
                }
            )
    return events


def reconcile_august_funding_vintages(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["event_type"], row["measurement_at"]), []).append(row)
    result = []
    for _key, evidence in sorted(grouped.items()):
        evidence.sort(key=lambda row: (row["filing_accepted_at"], row["accession_number"]))
        chosen = dict(evidence[0])
        if chosen["event_type"] == "AUGUST_PURCHASER_SHARES_AND_PROCEEDS_REPORTED":
            expected = 2 * chosen["gross_proceeds_reported"] / 5
            chosen["economic_equation_consistent"] = expected == chosen["shares_reported"]
            chosen["quality_state"] = (
                "REPORTED_EQUATION_CONSISTENT"
                if chosen["economic_equation_consistent"]
                else "SOURCE_NUMERIC_CONFLICT"
            )
        else:
            chosen["economic_equation_consistent"] = None
            chosen["quality_state"] = "REPORTED_WITH_UNRESOLVED_SCOPE"
        chosen["corroborating_accessions"] = sorted({row["accession_number"] for row in evidence})
        chosen["corroboration_count"] = len(evidence)
        result.append(chosen)
    return result, {
        "status": "PASS_WITH_RESTRICTIONS" if result else "NOT_OBSERVABLE",
        "source_event_rows": len(rows),
        "reconciled_vintage_rows": len(result),
        "partial_termination_rows": sum(
            row["event_type"] == "AUGUST_SPA_PARTIAL_TERMINATION_REPORTED" for row in result
        ),
        "tradable_supply_confirmed_rows": 0,
    }
