"""Canonical state-aware ordering extension for replay consumers."""
from __future__ import annotations

from typing import Any

from tsis_backtest.market_state.consumer import state_aware_order_key as market_state_order_key
from tsis_backtest.market_state.contracts import MarketStateContractError


def state_aware_order_key(event: Any) -> tuple[Any, ...]:
    """Order GAP/BAR/Market State with accepted semantics, then Event State."""
    if getattr(event, "event_type", None) == "BoundedEventStateAvailable":
        return (
            event.event_state_available_at_utc,
            3,
            event.session_date.isoformat(),
            event.ticker.upper(),
            event.event_state_record_id,
        )
    try:
        return market_state_order_key(event)
    except MarketStateContractError:
        raise
