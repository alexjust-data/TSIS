"""Minimal event loop for a programmed open/close mechanical short path."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayEvent

from .contracts import (
    BUY_TO_COVER,
    CLOSE_PROXY,
    OPEN_PROXY,
    SELL_SHORT,
    Fill,
    MechanicalRunResult,
    MechanicalRunSummary,
    Order,
    OrderIntent,
    Position,
    ScheduledDecision,
    TradeLedger,
)


class MechanicalEventLoopError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class _ExecutionTarget:
    decision: ScheduledDecision
    event: ReplayBarEvent
    price: float
    execution_timestamp: datetime
    order_type: str


class MechanicalEventLoop:
    """Processes replay events into a declared mechanical short round trip."""

    def run(self, run_id: str, events: Iterable[ReplayEvent], scheduled_decisions: tuple[ScheduledDecision, ...]) -> MechanicalRunResult:
        if len(scheduled_decisions) != 2:
            raise MechanicalEventLoopError("MECHANICAL_DECISION_COUNT_UNSUPPORTED", "minimum loop requires exactly open and close decisions")
        decisions_by_proxy = {decision.target_proxy: decision for decision in scheduled_decisions}
        if set(decisions_by_proxy) != {OPEN_PROXY, CLOSE_PROXY}:
            raise MechanicalEventLoopError("MECHANICAL_PROXY_SET_UNSUPPORTED", "minimum loop requires OPEN_PROXY and CLOSE_PROXY")
        tickers = {decision.ticker for decision in scheduled_decisions}
        if len(tickers) != 1:
            raise MechanicalEventLoopError("MECHANICAL_SINGLE_TICKER_REQUIRED", "minimum loop supports one ticker")
        ticker = next(iter(tickers))

        bars = tuple(event for event in events if isinstance(event, ReplayBarEvent) and event.ticker == ticker)
        if not bars:
            raise MechanicalEventLoopError("MECHANICAL_NO_BARS_FOR_TICKER", f"no replay bars for {ticker}")
        bars = tuple(sorted(bars, key=lambda event: (event.bar.ts_start, event.ticker)))
        open_target = _ExecutionTarget(
            decision=decisions_by_proxy[OPEN_PROXY],
            event=bars[0],
            price=bars[0].bar.open,
            execution_timestamp=bars[0].bar.ts_start,
            order_type="MARKET_ON_OPEN_PROXY",
        )
        close_target = _ExecutionTarget(
            decision=decisions_by_proxy[CLOSE_PROXY],
            event=bars[-1],
            price=bars[-1].bar.close,
            execution_timestamp=bars[-1].bar.ts_end,
            order_type="MARKET_ON_CLOSE_PROXY",
        )
        self._validate_target(open_target, expected_action=SELL_SHORT)
        self._validate_target(close_target, expected_action=BUY_TO_COVER)
        if open_target.decision.quantity != close_target.decision.quantity:
            raise MechanicalEventLoopError("MECHANICAL_QUANTITY_MISMATCH", "open and close quantities must match")

        intents = (self._intent(open_target), self._intent(close_target))
        orders = (self._order(intents[0], open_target), self._order(intents[1], close_target))
        fills = (self._fill(orders[0], open_target), self._fill(orders[1], close_target))
        final_position = self._position_from_fills(ticker, fills)
        quantity = open_target.decision.quantity
        gross_pnl = quantity * (open_target.price - close_target.price)
        linear_reference = quantity * (open_target.price - close_target.price)
        summary = MechanicalRunSummary(
            run_id=run_id,
            ticker=ticker,
            quantity=quantity,
            entry_price=open_target.price,
            exit_price=close_target.price,
            gross_pnl=gross_pnl,
            linear_reference_gross_pnl=linear_reference,
            pnl_matches_reference=abs(gross_pnl - linear_reference) < 1e-9 and abs(final_position.realized_gross_pnl - linear_reference) < 1e-9,
            final_position_quantity=final_position.quantity,
            order_count=len(orders),
            fill_count=len(fills),
            execution_realism_claimed=False,
            edge_evaluated=False,
            limitations=(
                "mechanical proxy fills only",
                "no fill realism claimed",
                "no edge evaluated",
            ),
        )
        return MechanicalRunResult(summary=summary, ledger=TradeLedger(intents, orders, fills, final_position))

    @staticmethod
    def _validate_target(target: _ExecutionTarget, expected_action: str) -> None:
        decision = target.decision
        if decision.action != expected_action:
            raise MechanicalEventLoopError("MECHANICAL_ACTION_MISMATCH", f"expected {expected_action}, got {decision.action}")
        if decision.quantity <= 0:
            raise MechanicalEventLoopError("MECHANICAL_INVALID_QUANTITY", "quantity must be positive")
        if decision.scheduled_at >= target.execution_timestamp:
            raise MechanicalEventLoopError("MECHANICAL_DECISION_NOT_SCHEDULED_BEFORE_EXECUTION", "scheduled decision must precede proxy execution timestamp")
        if target.event.available_at < target.execution_timestamp:
            raise MechanicalEventLoopError("MECHANICAL_EVENT_RECORDED_BEFORE_EXECUTION", "event availability cannot precede execution timestamp")

    @staticmethod
    def _intent(target: _ExecutionTarget) -> OrderIntent:
        decision = target.decision
        return OrderIntent(
            intent_id=f"intent-{decision.decision_id}",
            decision_id=decision.decision_id,
            ticker=decision.ticker,
            action=decision.action,
            quantity=decision.quantity,
            target_proxy=decision.target_proxy,
            created_at=decision.scheduled_at,
            reason=decision.reason,
        )

    @staticmethod
    def _order(intent: OrderIntent, target: _ExecutionTarget) -> Order:
        return Order(
            order_id=f"order-{intent.intent_id}",
            intent_id=intent.intent_id,
            ticker=intent.ticker,
            side=intent.action,
            quantity=intent.quantity,
            order_type=target.order_type,
            submitted_at=intent.created_at,
            status="FILLED",
        )

    @staticmethod
    def _fill(order: Order, target: _ExecutionTarget) -> Fill:
        bar = target.event.bar
        return Fill(
            fill_id=f"fill-{order.order_id}",
            order_id=order.order_id,
            ticker=order.ticker,
            side=order.side,
            quantity=order.quantity,
            price=target.price,
            execution_timestamp=target.execution_timestamp,
            recorded_at=target.event.available_at,
            source_bar_ts_start=bar.ts_start,
            source_bar_ts_end=bar.ts_end,
            source_event_available_at=target.event.available_at,
        )

    @staticmethod
    def _position_from_fills(ticker: str, fills: tuple[Fill, ...]) -> Position:
        quantity = 0
        short_entry_price: float | None = None
        short_quantity = 0
        realized = 0.0
        for fill in fills:
            if fill.side == SELL_SHORT:
                quantity -= fill.quantity
                short_quantity += fill.quantity
                short_entry_price = fill.price if short_entry_price is None else short_entry_price
            elif fill.side == BUY_TO_COVER:
                if short_entry_price is None or short_quantity < fill.quantity:
                    raise MechanicalEventLoopError("MECHANICAL_COVER_WITHOUT_SHORT", "cannot cover more than open short quantity")
                quantity += fill.quantity
                short_quantity -= fill.quantity
                realized += fill.quantity * (short_entry_price - fill.price)
                if short_quantity == 0:
                    short_entry_price = None
            else:
                raise MechanicalEventLoopError("MECHANICAL_FILL_SIDE_UNSUPPORTED", fill.side)
        return Position(ticker=ticker, quantity=quantity, average_entry_price=short_entry_price, realized_gross_pnl=realized)
