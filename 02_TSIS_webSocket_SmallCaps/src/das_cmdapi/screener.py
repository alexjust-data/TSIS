"""Screener denominator helpers for DAS CMD API v0."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .config import ScreenerDenominator


def denominator_to_dict(denominator: ScreenerDenominator) -> dict[str, Any]:
    result = asdict(denominator)
    result["sessions"] = list(denominator.sessions)
    result["volume_source_priority"] = list(denominator.volume_source_priority)
    return result


def candidate_passes_denominator(candidate: dict[str, Any], denominator: ScreenerDenominator) -> tuple[bool, list[str]]:
    """Evaluate a candidate row without inventing missing data."""
    failures: list[str] = []
    market_cap = candidate.get("market_cap_usd")
    price = candidate.get("price_usd")
    volume = candidate.get("volume_shares")
    session = candidate.get("session")

    if session is not None and session not in denominator.sessions:
        failures.append("session_not_in_scope")
    if market_cap is None:
        failures.append("market_cap_unavailable")
    elif float(market_cap) >= denominator.market_cap_usd_lt:
        failures.append("market_cap_above_limit")
    if price is None:
        failures.append("price_unavailable")
    else:
        price_value = float(price)
        if price_value < denominator.price_usd_min or price_value > denominator.price_usd_max:
            failures.append("price_outside_range")
    if volume is None:
        failures.append("volume_unavailable")
    elif int(volume) < denominator.min_volume_shares:
        failures.append("volume_below_min")
    return not failures, failures
