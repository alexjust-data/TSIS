"""Contracts for the first mechanical trading path."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from tsis_backtest.preflight.contracts import to_jsonable


SELL_SHORT = "SELL_SHORT"
BUY_TO_COVER = "BUY_TO_COVER"
OPEN_PROXY = "OPEN_PROXY"
CLOSE_PROXY = "CLOSE_PROXY"
MECHANICAL_PROXY_FILL = "MECHANICAL_PROXY_FILL"


@dataclass(frozen=True)
class ScheduledDecision:
    decision_id: str
    ticker: str
    action: str
    quantity: int
    target_proxy: str
    scheduled_at: datetime
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class OrderIntent:
    intent_id: str
    decision_id: str
    ticker: str
    action: str
    quantity: int
    target_proxy: str
    created_at: datetime
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class Order:
    order_id: str
    intent_id: str
    ticker: str
    side: str
    quantity: int
    order_type: str
    submitted_at: datetime
    status: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class Fill:
    fill_id: str
    order_id: str
    ticker: str
    side: str
    quantity: int
    price: float
    execution_timestamp: datetime
    recorded_at: datetime
    source_bar_ts_start: datetime
    source_bar_ts_end: datetime
    source_event_available_at: datetime
    fill_model: str = MECHANICAL_PROXY_FILL

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class Position:
    ticker: str
    quantity: int
    average_entry_price: float | None
    realized_gross_pnl: float

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class TradeLedger:
    order_intents: tuple[OrderIntent, ...]
    orders: tuple[Order, ...]
    fills: tuple[Fill, ...]
    final_position: Position

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class MechanicalRunSummary:
    run_id: str
    ticker: str
    quantity: int
    entry_price: float
    exit_price: float
    gross_pnl: float
    linear_reference_gross_pnl: float
    pnl_matches_reference: bool
    final_position_quantity: int
    order_count: int
    fill_count: int
    execution_realism_claimed: bool
    edge_evaluated: bool
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class MechanicalRunResult:
    summary: MechanicalRunSummary
    ledger: TradeLedger

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)
