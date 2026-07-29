"""Contracts for BT-GATE-011 single-strategy end-to-end backtests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any, Mapping


BT_GATE_011 = "BT-GATE-011"
SINGLE_STRATEGY_END_TO_END_BACKTEST = "SINGLE_STRATEGY_END_TO_END_BACKTEST"
OPEN_SHORT_CLOSE_COVER_V0_1 = "open_short_close_cover_v0_1"

ENGINE_VALIDATION_RUN = "ENGINE_VALIDATION_RUN"
NOT_EDGE_EVIDENCE = "NOT_EDGE_EVIDENCE"
NOT_ECONOMICALLY_REALISTIC = "NOT_ECONOMICALLY_REALISTIC"
ECONOMIC_REALISM_INCOMPLETE = "INCOMPLETE"
STRATEGY_OPTIMIZATION_NOT_AUTHORIZED = "NOT_AUTHORIZED"

ENTRY_OPEN_LABEL = "ENTRY_OPEN_LABEL"
EXIT_CLOSE_LABEL = "EXIT_CLOSE_LABEL"

SELL_SHORT = "SELL_SHORT"
BUY_TO_COVER = "BUY_TO_COVER"
MARKET_PROXY = "MARKET_PROXY"
DAY = "DAY"
FULL_FILL_ONLY = "FULL_FILL_ONLY"

ROUND_HALF_EVEN_CENTS = "ROUND_HALF_EVEN_CENTS"


class BacktestRunError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str
    strategy_spec_version: str
    strategy_name: str
    universe_id: str
    symbols: tuple[str, ...]
    quantity_per_symbol: int
    entry_side: str = SELL_SHORT
    exit_side: str = BUY_TO_COVER
    entry_order_type: str = MARKET_PROXY
    exit_order_type: str = MARKET_PROXY
    entry_market_price_field: str = "open"
    exit_market_price_field: str = "close"
    time_in_force: str = DAY
    fill_capability: str = FULL_FILL_ONLY
    decision_policy_id: str = "PREPROGRAMMED_SESSION_SCHEDULE_V0_1"
    run_purpose: str = ENGINE_VALIDATION_RUN
    edge_evidence: str = "NOT_AUTHORIZED"
    economic_realism: str = ECONOMIC_REALISM_INCOMPLETE
    strategy_optimization: str = STRATEGY_OPTIMIZATION_NOT_AUTHORIZED
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class BacktestRunRequest:
    run_id: str
    strategy_spec: StrategySpec
    preflight_report_path: Path
    output_root: Path
    fixture_id: str
    session_date: date
    starting_equity: Decimal
    run_purpose: str = ENGINE_VALIDATION_RUN
    edge_evidence: str = "NOT_AUTHORIZED"
    economic_realism: str = ECONOMIC_REALISM_INCOMPLETE
    strategy_optimization: str = STRATEGY_OPTIMIZATION_NOT_AUTHORIZED

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class StrategyDecision:
    decision_id: str
    strategy_id: str
    strategy_spec_version: str
    ticker: str
    side: str
    quantity: int
    target_label: str
    decision_timestamp: datetime
    information_cutoff: datetime
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class BacktestOrderIntent:
    intent_id: str
    decision_id: str
    ticker: str
    side: str
    quantity: int
    order_type: str
    market_price_field: str
    target_label: str
    created_at: datetime
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class BacktestOrderRecord:
    order_id: str
    intent_id: str
    decision_id: str
    ticker: str
    side: str
    quantity: int
    order_type: str
    market_price_field: str
    time_in_force: str
    fill_capability: str
    order_submission_timestamp: datetime
    eligible_source_bar_id: str
    eligible_source_bar_ts_start: datetime
    eligible_source_bar_ts_end: datetime
    eligible_source_bar_available_at: datetime
    status: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PositionSnapshot:
    ticker: str
    quantity: int
    average_entry_price: Decimal | None
    realized_gross_pnl: Decimal
    realized_net_pnl: Decimal
    total_costs: Decimal
    last_mark_price: Decimal | None

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class TradeRecord:
    trade_id: str
    ticker: str
    quantity: int
    entry_order_id: str
    exit_order_id: str
    entry_fill_id: str
    exit_fill_id: str
    entry_execution_timestamp: datetime
    exit_execution_timestamp: datetime
    entry_recorded_at: datetime
    exit_recorded_at: datetime
    entry_price: Decimal
    exit_price: Decimal
    gross_pnl: Decimal
    total_costs: Decimal
    net_pnl: Decimal
    terminal_outcome: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class EventLoopTraceRecord:
    event_loop_mode: str
    replay_event_index: int
    replay_event_type: str
    ticker: str
    target_label: str
    event_available_at: datetime
    source_bar_id: str
    source_bar_ts_start: datetime
    source_bar_ts_end: datetime
    source_bar_available_at: datetime
    decision_id: str
    decision_timestamp: datetime
    order_id: str
    order_submission_timestamp: datetime
    order_registered_before_replay_started: bool
    order_registered_before_replay_event: bool
    order_registration_replay_index: int
    order_activation_timestamp: datetime
    coordinator_clock_at_order_registration: datetime
    eligible_replay_event_index: int
    accounting_applied_at_replay_event_index: int
    position_after_fill: int
    cash_after_fill: Decimal
    equity_after_fill: Decimal
    simulator_event_count: int
    max_replay_event_index_visible_to_simulator: int
    terminal_order_outcome: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class CashLedgerEntryV0:
    entry_id: str
    ticker: str
    fill_id: str
    order_id: str
    entry_type: str
    amount: Decimal
    cash_after: Decimal
    recorded_at: datetime
    description: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class EquityCurvePoint:
    sequence: int
    timestamp: datetime
    cash: Decimal
    position_market_value: Decimal
    equity: Decimal
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class MetricsSummary:
    trade_count: int
    winning_trade_count: int
    losing_trade_count: int
    flat_trade_count: int
    gross_profit: Decimal
    gross_loss: Decimal
    gross_pnl: Decimal
    total_costs: Decimal
    net_pnl: Decimal
    starting_equity: Decimal
    ending_equity: Decimal
    return_pct: Decimal
    max_drawdown: Decimal
    profit_factor: Decimal | None
    edge_evaluated: bool
    economic_realism_complete: bool

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class EndToEndRunSummary:
    run_id: str
    gate_id: str
    capability: str
    strategy_id: str
    strategy_spec_version: str
    fixture_id: str
    preflight_status: str
    replay_event_count: int
    replay_bar_count: int
    replay_gap_count: int
    symbol_count: int
    order_count: int
    fill_count: int
    trade_count: int
    final_position_all_zero: bool
    event_loop_mode: str
    event_loop_trace_count: int
    event_loop_future_event_access_detected: bool
    orders_pre_registered_before_replay: bool
    accounting_applied_inside_event_loop: bool
    gross_pnl: Decimal
    total_costs: Decimal
    net_pnl: Decimal
    ending_equity: Decimal
    deterministic_output_hash: str
    validation_status: str
    run_purpose: str
    edge_evidence: str
    economic_realism: str
    strategy_optimization: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class UnifiedRunManifest:
    manifest_schema_version: str
    run_id: str
    gate_id: str
    capability: str
    strategy_id: str
    strategy_spec_version: str
    fixture_id: str
    input_identities: Mapping[str, Any]
    symbol_set: tuple[str, ...]
    session: Mapping[str, Any]
    initial_cash: Decimal
    quantity_policy: Mapping[str, Any]
    execution_profile: Mapping[str, Any]
    cost_model: Mapping[str, Any]
    slippage_model: Mapping[str, Any]
    accounting_policy: Mapping[str, Any]
    software_identity: Mapping[str, Any]
    run_classifications: Mapping[str, Any]
    output_artifacts: Mapping[str, str]
    validation_status: str
    reconciliation_status: str
    state_provider_restrictions: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class EndToEndBacktestResult:
    request: BacktestRunRequest
    strategy_spec: StrategySpec
    decisions: tuple[StrategyDecision, ...]
    order_intents: tuple[BacktestOrderIntent, ...]
    orders: tuple[BacktestOrderRecord, ...]
    order_results: tuple[Any, ...]
    fills: tuple[Any, ...]
    cost_breakdowns: tuple[Any, ...]
    event_loop_trace: tuple[EventLoopTraceRecord, ...]
    trades: tuple[TradeRecord, ...]
    positions: tuple[PositionSnapshot, ...]
    cash_ledger: tuple[CashLedgerEntryV0, ...]
    equity_curve: tuple[EquityCurvePoint, ...]
    metrics: MetricsSummary
    summary: EndToEndRunSummary
    unified_run_manifest: UnifiedRunManifest

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


def dec(value: Any) -> Decimal:
    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def decimal_str(value: Decimal) -> str:
    return format(value, "f")


def canonical_hash(value: Any) -> str:
    payload = json.dumps(to_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_str(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if is_dataclass(value):
        return {field.name: to_jsonable(getattr(value, field.name)) for field in fields(value)}
    if hasattr(value, "to_dict"):
        return to_jsonable(value.to_dict())
    return value
