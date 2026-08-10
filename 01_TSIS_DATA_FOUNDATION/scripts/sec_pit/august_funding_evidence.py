from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup


def _number(token: str) -> int:
    multiplier = 1_000_000 if "million" in token.lower() else 1
    cleaned = re.sub(r"[^0-9.]", "", token)
    return round(float(cleaned) * multiplier)


def extract_august_funding_evidence(payload: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    text = re.sub(r"\s+", " ", " ".join(BeautifulSoup(payload, "html.parser").stripped_strings))
    section = text
    candidates = re.split(r"August Private Placement", text, flags=re.I)[1:]
    candidates = [
        candidate
        for candidate in candidates
        if "For every $5.00" in candidate and "220,000 shares" in candidate
    ]
    if candidates:
        section = candidates[0]

    as_of = re.search(
        r"As of ([A-Z][a-z]+ \d{1,2}, \d{4}), a total of ([0-9,]+) shares[^.]{0,300}?issued to(?: \d+ Table of Contents)? the August Purchasers[^.]{0,200}?"
        r"gross proceeds of \$([0-9,.]+(?: million)?)",
        text,
        re.I,
    )
    failures = re.search(
        r"failed to make their required fundings.*?aggregate amount of \$([0-9,.]+(?: million)?)",
        section,
        re.I,
    )
    conversion = re.search(
        r"For every \$([0-9.]+) paid.*?release one share.*?August SPA and one share.*?Assignment Agreement",
        section,
        re.I,
    )
    if not (as_of and conversion):
        return [], {"status": "NOT_OBSERVABLE", "reason": "FUNDING_EVIDENCE_NOT_FOUND"}

    combined_shares = _number(as_of.group(2))
    gross_proceeds = _number(as_of.group(3))
    dollars_per_pair = float(conversion.group(1))
    supported_pairs = round(gross_proceeds / dollars_per_pair)
    equation_consistent = combined_shares == 2 * supported_pairs
    events = [
        {
            "event_type": "AUGUST_FUNDING_AGGREGATE_REPORTED",
            "measurement_at_reported": as_of.group(1),
            "gross_proceeds_reported": gross_proceeds,
            "combined_shares_reported": combined_shares,
            "contract_dollars_per_share_pair": dollars_per_pair,
            "spa_shares_supported": supported_pairs if equation_consistent else None,
            "sponsor_shares_supported": supported_pairs if equation_consistent else None,
            "equation_consistent": equation_consistent,
            "tradable_supply_confirmation": False,
        }
    ]
    if failures:
        events.append(
            {
                "event_type": "AUGUST_REQUIRED_FUNDING_FAILURE_REPORTED",
                "failed_funding_amount_reported": _number(failures.group(1)),
                "purchaser_allocation": None,
                "cancellation_quantity": None,
                "tradable_supply_confirmation": False,
            }
        )
    return events, {
        "status": "PASS_WITH_RESTRICTIONS" if equation_consistent else "SOURCE_CONFLICT",
        "event_rows": len(events),
        "equation_consistent": equation_consistent,
        "tradable_supply_confirmed_rows": 0,
    }
