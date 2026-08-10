from __future__ import annotations

import html
import re
from datetime import date, timedelta
from typing import Any


def is_valid_cusip(value: str) -> bool:
    value = re.sub(r"[^A-Z0-9*@#]", "", value.upper())
    if len(value) != 9:
        return False

    def numeric(char: str) -> int:
        if char.isdigit():
            return int(char)
        if "A" <= char <= "Z":
            return ord(char) - ord("A") + 10
        return {"*": 36, "@": 37, "#": 38}[char]

    total = 0
    for index, char in enumerate(value[:8]):
        number = numeric(char) * (2 if index % 2 else 1)
        total += number // 10 + number % 10
    return value[-1].isdigit() and (10 - total % 10) % 10 == int(value[-1])


def extract_cusips(text: str) -> list[str]:
    plain = html.unescape(re.sub(r"<[^>]+>", " ", text))
    plain = re.sub(r"\s+", " ", plain)
    candidates: set[str] = set()
    for match in re.finditer(r"(?i)CUSIP.{0,180}", plain):
        for token in re.findall(r"\b[A-Z0-9*@#]{6}[ -]?[A-Z0-9*@#]{3}\b", match.group(0).upper()):
            normalized = token.replace(" ", "").replace("-", "")
            if is_valid_cusip(normalized):
                candidates.add(normalized)
    return sorted(candidates)


def resolve_cusip_intervals(
    observations: list[dict[str, Any]],
    instrument_valid_from: str,
    instrument_valid_to: str,
    split_rows: list[dict[str, Any]],
    admitted_cusip_issuer_number: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    valid_from = date.fromisoformat(instrument_valid_from[:10])
    valid_to = date.fromisoformat(instrument_valid_to[:10])
    in_scope = [
        row
        for row in observations
        if date.fromisoformat(str(row["filing_date"])[:10]) >= valid_from
        and str(row["cusip"])[:6] == admitted_cusip_issuer_number
    ]
    first_by_cusip: dict[str, dict[str, Any]] = {}
    for row in sorted(in_scope, key=lambda item: str(item["eligible_from_session"])):
        first_by_cusip.setdefault(str(row["cusip"]), row)

    primary_splits = sorted(
        (
            row
            for row in split_rows
            if row.get("action_type") == "split"
            and row.get("source_system") == "reference"
            and bool(row.get("within_instrument_valid_window"))
        ),
        key=lambda row: str(row["action_date"]),
    )
    ordered = sorted(first_by_cusip.values(), key=lambda item: str(item["eligible_from_session"]))
    intervals: list[dict[str, Any]] = []
    for index, observation in enumerate(ordered):
        start = date.fromisoformat(str(observation["eligible_from_session"])[:10])
        if index > 0 and primary_splits:
            split_date = date.fromisoformat(str(primary_splits[-1]["action_date"])[:10])
            if start <= split_date:
                start = split_date
        end = valid_to
        if index + 1 < len(ordered):
            next_start = date.fromisoformat(str(ordered[index + 1]["eligible_from_session"])[:10])
            if primary_splits:
                next_start = max(
                    next_start,
                    date.fromisoformat(str(primary_splits[-1]["action_date"])[:10]),
                )
            end = min(end, next_start - timedelta(days=1))
        intervals.append(
            {
                "cusip": observation["cusip"],
                "effective_from": max(valid_from, start).isoformat(),
                "effective_to": end.isoformat(),
                "source_accession": observation["accession_number"],
                "source_form": observation["form"],
                "source_eligible_from_session": observation["eligible_from_session"],
                "quality_state": "CUSIP_PIT_SUPPORTED_WITH_CURRENT_SOURCE_SET",
            }
        )
    return intervals, {
        "status": "PASS_WITH_RESTRICTIONS" if intervals else "FAIL",
        "source_observations": len(observations),
        "in_scope_observations": len(in_scope),
        "resolved_intervals": len(intervals),
        "pre_first_evidence_state": "CUSIP_UNAVAILABLE",
    }
