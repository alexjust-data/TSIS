from __future__ import annotations

import math
from bisect import bisect_left
from datetime import date
from typing import Any


def _as_date(value: Any) -> date:
    return date.fromisoformat(str(value)[:10])


def _primary_splits(split_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (
            row
            for row in split_rows
            if row.get("action_type") == "split"
            and row.get("source_system") == "reference"
            and bool(row.get("within_instrument_valid_window"))
            and float(row.get("split_ratio") or 0) > 0
        ),
        key=lambda row: str(row["action_date"]),
    )


def build_presession_reference_market_cap(
    daily_os_rows: list[dict[str, Any]],
    vendor_adjusted_daily_rows: list[dict[str, Any]],
    split_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Resolve prior-close market cap at each presession cutoff.

    The vendor source is explicitly expected to be split-adjusted to a later
    basis. We first recover the price's historical basis with all future split
    ratios, then align that price to the target session basis with splits that
    become effective after the price observation and no later than the session.
    """
    splits = _primary_splits(split_rows)
    prices = sorted(
        (
            {
                "date": _as_date(row["date"]),
                "close": float(row["c"]),
            }
            for row in vendor_adjusted_daily_rows
            if row.get("date") is not None and row.get("c") is not None
        ),
        key=lambda row: row["date"],
    )
    price_dates = [row["date"] for row in prices]
    resolved: list[dict[str, Any]] = []

    for os_source in daily_os_rows:
        row = dict(os_source)
        session = _as_date(row["session_date"])
        price_index = bisect_left(price_dates, session) - 1
        if price_index < 0:
            row.update(
                {
                    "reference_price_observation_date": None,
                    "vendor_adjusted_prior_close": None,
                    "price_historical_basis_factor": None,
                    "price_session_alignment_factor": None,
                    "presession_reference_price_as_known": None,
                    "price_applied_corporate_action_ids": [],
                    "presession_reference_market_cap_estimate_as_known": None,
                    "market_cap_state": "MARKET_CAP_UNAVAILABLE_PRICE",
                }
            )
            resolved.append(row)
            continue

        price_observation = prices[price_index]
        price_date = price_observation["date"]
        vendor_close = price_observation["close"]
        future_factor = 1.0
        session_alignment_factor = 1.0
        applied_ids: list[str] = []
        for split in splits:
            effective = _as_date(split["action_date"])
            ratio = float(split["split_ratio"])
            if effective > price_date:
                future_factor *= ratio
            if price_date < effective <= session:
                session_alignment_factor *= ratio
                applied_ids.append(str(split["corporate_action_id"]))

        historical_basis_close = vendor_close * future_factor
        session_basis_close = historical_basis_close / session_alignment_factor
        os_value = row.get("shares_outstanding_estimate_as_known")
        os_is_available = os_value is not None and math.isfinite(float(os_value))
        market_cap = session_basis_close * float(os_value) if os_is_available else None
        row.update(
            {
                "reference_price_observation_date": price_date.isoformat(),
                "vendor_adjusted_prior_close": vendor_close,
                "price_historical_basis_factor": future_factor,
                "price_session_alignment_factor": session_alignment_factor,
                "presession_reference_price_as_known": session_basis_close,
                "price_applied_corporate_action_ids": applied_ids,
                "presession_reference_market_cap_estimate_as_known": market_cap,
                "market_cap_state": (
                    "MARKET_CAP_ESTIMATED_AS_KNOWN"
                    if market_cap is not None
                    else "MARKET_CAP_UNAVAILABLE_OS"
                ),
            }
        )
        resolved.append(row)

    non_null = sum(
        row["presession_reference_market_cap_estimate_as_known"] is not None
        for row in resolved
    )
    return resolved, {
        "status": "PASS_WITH_RESTRICTIONS",
        "daily_rows": len(resolved),
        "market_cap_non_null_rows": non_null,
        "market_cap_unavailable_rows": len(resolved) - non_null,
        "primary_split_rows": len(splits),
        "source_price_view": "MASSIVE_DAILY_ADJUSTED_TRUE",
        "output_price_view": "SESSION_BASIS_PRIOR_ELIGIBLE_RTH_CLOSE",
    }
