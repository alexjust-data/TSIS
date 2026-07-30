"""Contracts for BT-GATE-012 portfolio slice."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from tsis_backtest.backtest.contracts import (
    BacktestOrderIntent,
    BacktestOrderRecord,
    CashLedgerEntryV0,
    EquityCurvePoint,
    MetricsSummary,
    PositionSnapshot,
    StrategyDecision,
    StrategySpec,
    TradeRecord,
    to_jsonable,
)


BT_GATE_012 = "BT-GATE-012"
MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE = "MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE"
PORTFOLIO_EVENT_LOOP_MODE_V0_1 = "ONLINE_PORTFOLIO_REPLAY_COORDINATOR_V0_1"
GLOBAL_REPLAY_ORDER_V0_1 = "GLOBAL_REPLAY_ORDER_V0_1"
ACTIVE_ORDER_EVALUATION_ORDER_V0_1 = "ACTIVE_ORDER_EVALUATION_ORDER_V0_1"
PORTFOLIO_EQUITY_POLICY_V0_1 = "PORTFOLIO_EQUITY_POLICY_V0_1"
REGULAR_ONLY_XNYS_V0_1 = "REGULAR_ONLY_XNYS_V0_1"
TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1 = "TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1"


@dataclass(frozen=True)
class PortfolioRunRequest:
    run_id: str
    strategy_spec: StrategySpec
    preflight_report_paths: tuple[Path, ...]
    output_root: Path
    fixture_id: str
    session_dates: tuple[date, ...]
    session_calendar_snapshot_path: Path
    session_calendar_snapshot_sha256: str
    starting_equity: Decimal
    run_purpose: str = "ENGINE_VALIDATION_RUN"
    edge_evidence: str = "NOT_AUTHORIZED"
    economic_realism: str = "INCOMPLETE"
    strategy_optimization: str = "NOT_AUTHORIZED"
    gate_id: str = BT_GATE_012
    capability: str = MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
    preloaded_replay_events: tuple[Any, ...] | None = None
    preloaded_replay_summaries: tuple[Any, ...] = ()
    preloaded_input_reports: tuple[Mapping[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class SessionCalendarEntry:
    session_date: date
    regular_open_utc: datetime
    regular_close_utc: datetime
    calendar_id: str = "XNYS"
    timezone: str = "America/New_York"
    early_close: bool = False

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class EventSequenceRecord:
    event_index: int
    global_order_policy_id: str
    available_at_utc: datetime
    session_date: date
    event_type_priority: int
    event_type: str
    ticker_normalized: str
    source_event_identity: str
    order_key: tuple[Any, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PortfolioEventLoopTraceRecord:
    event_loop_mode: str
    replay_event_index: int
    session_date: date
    replay_event_type: str
    ticker: str
    event_available_at: datetime
    source_event_identity: str
    global_order_key: tuple[Any, ...]
    target_label: str | None
    decision_id: str | None
    decision_timestamp: datetime | None
    order_id: str | None
    order_submission_timestamp: datetime | None
    active_order_evaluation_key: tuple[Any, ...] | None
    order_registered_before_replay_started: bool
    order_registered_before_replay_event: bool
    order_registration_replay_index: int | None
    eligible_replay_event_index: int | None
    simulator_event_count: int
    max_replay_event_index_visible_to_simulator: int
    terminal_order_outcome: str | None
    fill_id: str | None
    accounting_applied_at_replay_event_index: int | None
    position_after_fill: int
    cash_after_event: Decimal
    equity_after_event: Decimal
    valuation_price_after_event: Decimal | None
    replay_gap_supplied_execution_price: bool
    replay_gap_triggered_fill: bool

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PortfolioSessionResult:
    session_date: date
    order_count: int
    fill_count: int
    trade_count: int
    gross_pnl: Decimal
    total_costs: Decimal
    net_pnl: Decimal
    ending_cash: Decimal
    final_positions_zero: bool

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PortfolioRunSummary:
    run_id: str
    gate_id: str
    capability: str
    fixture_id: str
    session_count: int
    symbol_count: int
    symbol_session_count: int
    replay_event_count: int
    replay_bar_count: int
    replay_gap_count: int
    order_count: int
    fill_count: int
    trade_count: int
    final_position_all_zero: bool
    event_loop_mode: str
    event_loop_trace_count: int
    event_sequence_hash: str
    active_order_evaluation_hash: str
    portfolio_equity_curve_hash: str
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
class PortfolioRunManifest:
    manifest_schema_version: str
    run_id: str
    gate_id: str
    capability: str
    fixture_id: str
    strategy_id: str
    strategy_spec_version: str
    input_identities: Mapping[str, Any]
    symbol_set: tuple[str, ...]
    sessions: tuple[str, ...]
    initial_cash: Decimal
    quantity_policy: Mapping[str, Any]
    global_replay_order_policy: str
    active_order_evaluation_order_policy: str
    portfolio_equity_policy: str
    session_policy: str
    calendar_authority: str
    calendar_snapshot_sha256: str
    execution_profile: Mapping[str, Any]
    cost_model: Mapping[str, Any]
    slippage_model: Mapping[str, Any]
    accounting_policy: Mapping[str, Any]
    run_classifications: Mapping[str, Any]
    output_artifacts: Mapping[str, str]
    validation_status: str
    reconciliation_status: str
    state_provider_restrictions: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PortfolioRunResult:
    request: PortfolioRunRequest
    strategy_spec: StrategySpec
    session_calendar_snapshot: Mapping[str, Any]
    event_sequence_manifest: tuple[EventSequenceRecord, ...]
    decisions: tuple[StrategyDecision, ...]
    order_intents: tuple[BacktestOrderIntent, ...]
    orders: tuple[BacktestOrderRecord, ...]
    order_results: tuple[Any, ...]
    fills: tuple[Any, ...]
    cost_breakdowns: tuple[Any, ...]
    event_loop_trace: tuple[PortfolioEventLoopTraceRecord, ...]
    trades: tuple[TradeRecord, ...]
    cash_ledger: tuple[CashLedgerEntryV0, ...]
    positions_by_symbol: tuple[PositionSnapshot, ...]
    session_results: tuple[PortfolioSessionResult, ...]
    portfolio_equity_curve: tuple[EquityCurvePoint, ...]
    metrics: MetricsSummary
    summary: PortfolioRunSummary
    portfolio_run_manifest: PortfolioRunManifest

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)
