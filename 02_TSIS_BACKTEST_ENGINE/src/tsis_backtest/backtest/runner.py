"""BT-GATE-011 single-strategy end-to-end backtest runner."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from tsis_backtest.execution.contracts import (
    BUY_TO_COVER,
    DAY,
    FILLED,
    FULL_FILL_ONLY,
    MARKET_PROXY,
    SELL_SHORT,
    CostBreakdownV0,
    CostModelV0,
    ExecutionOrder,
    ExecutionPolicy,
    FillRecord,
    OrderSimulationResult,
    SlippageModel,
)
from tsis_backtest.execution.simulator import DeterministicFillSimulator
from tsis_backtest.replay import HistoricalReplayFeed, ReplayBarEvent, ReplayGapEvent, ReplayRunSummary
from tsis_backtest.replay.contracts import ReplayEvent

from .contracts import (
    BT_GATE_011,
    ENGINE_VALIDATION_RUN,
    ENTRY_OPEN_LABEL,
    EXIT_CLOSE_LABEL,
    NOT_EDGE_EVIDENCE,
    ROUND_HALF_EVEN_CENTS,
    SINGLE_STRATEGY_END_TO_END_BACKTEST,
    BacktestOrderIntent,
    BacktestOrderRecord,
    BacktestRunError,
    CashLedgerEntryV0,
    EndToEndBacktestResult,
    EndToEndRunSummary,
    EquityCurvePoint,
    EventLoopTraceRecord,
    MetricsSummary,
    PositionSnapshot,
    StrategyDecision,
    TradeRecord,
    UnifiedRunManifest,
    canonical_hash,
    dec,
    money,
    to_jsonable,
)
from .strategy import OpenShortCloseCoverStrategy


EVENT_LOOP_MODE = "ONLINE_REPLAY_COORDINATOR_V0_1"


class SingleStrategyEndToEndBacktestRunner:
    def __init__(
        self,
        execution_policy: ExecutionPolicy | None = None,
        slippage_model: SlippageModel | None = None,
        cost_model: CostModelV0 | None = None,
    ) -> None:
        self.execution_policy = execution_policy or ExecutionPolicy()
        self.slippage_model = slippage_model or SlippageModel("zero_slippage_v0_1")
        self.cost_model = cost_model or CostModelV0(
            "bt_gate_011_commission_minimum_v0_1",
            commission_per_share=Decimal("0.005"),
            minimum_commission_per_order=Decimal("1.00"),
        )
        self.simulator = DeterministicFillSimulator(
            execution_policy=self.execution_policy,
            slippage_model=self.slippage_model,
            cost_model=self.cost_model,
        )

    def run(self, request: BacktestRunRequest) -> EndToEndBacktestResult:
        self._validate_request(request)
        preflight_report = _read_json(request.preflight_report_path)
        feed = HistoricalReplayFeed.from_preflight_report(request.preflight_report_path)
        events = feed.stream_events()
        replay_summary = feed.summarize()
        strategy = OpenShortCloseCoverStrategy(request.strategy_spec)
        schedule = _session_schedule(preflight_report)
        self._validate_schedule(request, preflight_report, schedule)

        loop = self._run_online_event_loop(request, strategy, events, schedule)
        decisions = loop["decisions"]
        intents = loop["intents"]
        orders = loop["orders"]
        order_results = loop["order_results"]
        fills = loop["fills"]
        cost_breakdowns = loop["cost_breakdowns"]
        event_loop_trace = loop["event_loop_trace"]

        cash_ledger = loop["cash_ledger"]
        equity_curve = loop["equity_curve"]
        trades = _build_trades(request.strategy_spec.symbols, fills, cost_breakdowns)
        positions = _final_positions(request.strategy_spec.symbols, fills, cost_breakdowns, trades)
        metrics = _metrics(request.starting_equity, trades, tuple(equity_curve))
        deterministic_output_hash = canonical_hash(
            {
                "strategy_spec": request.strategy_spec,
                "decisions": decisions,
                "order_intents": intents,
                "orders": orders,
                "order_results": order_results,
                "fills": fills,
                "cost_breakdowns": cost_breakdowns,
                "event_loop_trace": event_loop_trace,
                "trades": trades,
                "positions": positions,
                "cash_ledger": cash_ledger,
                "equity_curve": equity_curve,
                "metrics": metrics,
            }
        )
        validation_status = _validation_status(request, order_results, fills, positions, metrics, event_loop_trace)
        summary = EndToEndRunSummary(
            run_id=request.run_id,
            gate_id=BT_GATE_011,
            capability=SINGLE_STRATEGY_END_TO_END_BACKTEST,
            strategy_id=request.strategy_spec.strategy_id,
            strategy_spec_version=request.strategy_spec.strategy_spec_version,
            fixture_id=request.fixture_id,
            preflight_status=str(preflight_report.get("preflight_status")),
            replay_event_count=replay_summary.event_count,
            replay_bar_count=replay_summary.bar_count,
            replay_gap_count=replay_summary.gap_count,
            symbol_count=len(request.strategy_spec.symbols),
            order_count=len(orders),
            fill_count=len(fills),
            trade_count=len(trades),
            final_position_all_zero=all(position.quantity == 0 for position in positions),
            event_loop_mode=EVENT_LOOP_MODE,
            event_loop_trace_count=len(event_loop_trace),
            event_loop_future_event_access_detected=_future_event_access_detected(event_loop_trace),
            orders_pre_registered_before_replay=_orders_pre_registered(event_loop_trace),
            accounting_applied_inside_event_loop=_accounting_applied_inside_loop(event_loop_trace),
            gross_pnl=metrics.gross_pnl,
            total_costs=metrics.total_costs,
            net_pnl=metrics.net_pnl,
            ending_equity=metrics.ending_equity,
            deterministic_output_hash=deterministic_output_hash,
            validation_status=validation_status,
            run_purpose=request.run_purpose,
            edge_evidence=request.edge_evidence,
            economic_realism=request.economic_realism,
            strategy_optimization=request.strategy_optimization,
            limitations=(
                "ENGINE_VALIDATION_RUN only",
                "NOT_EDGE_EVIDENCE",
                "NOT_ECONOMICALLY_REALISTIC",
                "borrow/locates not implemented",
                "SSR not implemented",
                "halts not implemented",
                "liquidity/capacity not implemented",
                "StateReplayFeed and Market/Event State consumption not authorized",
            ),
        )
        manifest = self._manifest(request, preflight_report, replay_summary, summary, output_artifacts={})
        return EndToEndBacktestResult(
            request=request,
            strategy_spec=request.strategy_spec,
            decisions=tuple(decisions),
            order_intents=tuple(intents),
            orders=tuple(orders),
            order_results=tuple(order_results),
            fills=tuple(fills),
            cost_breakdowns=tuple(cost_breakdowns),
            event_loop_trace=tuple(event_loop_trace),
            trades=tuple(trades),
            positions=tuple(positions),
            cash_ledger=tuple(cash_ledger),
            equity_curve=tuple(equity_curve),
            metrics=metrics,
            summary=summary,
            unified_run_manifest=manifest,
        )

    def write_result(self, result: EndToEndBacktestResult, determinism_report: Mapping[str, Any] | None = None) -> Path:
        run_dir = result.request.output_root / result.request.run_id
        if run_dir.exists() and any(run_dir.iterdir()):
            raise BacktestRunError("BT011_OUTPUT_DIR_NOT_EMPTY", str(run_dir))
        run_dir.mkdir(parents=True, exist_ok=True)

        artifacts: dict[str, Any] = {
            "backtest_run_request.json": result.request,
            "strategy_spec.json": result.strategy_spec,
            "decisions.json": result.decisions,
            "order_intents.json": result.order_intents,
            "orders.json": result.orders,
            "order_simulation_results.json": result.order_results,
            "fills.json": result.fills,
            "cost_breakdowns.json": result.cost_breakdowns,
            "event_loop_trace.json": result.event_loop_trace,
            "trade_ledger.json": {
                "trades": result.trades,
                "positions": result.positions,
                "fills": result.fills,
                "cost_breakdowns": result.cost_breakdowns,
            },
            "cash_ledger.json": result.cash_ledger,
            "equity_curve.json": result.equity_curve,
            "metrics_summary.json": result.metrics,
            "run_summary.json": result.summary,
            "validation_report.json": _validation_report(result),
            "determinism_report.json": determinism_report or {"status": "NOT_EXECUTED"},
        }
        for name, payload in artifacts.items():
            _write_json(run_dir / name, payload)
        hashes = {name: _sha256_file(run_dir / name) for name in artifacts}
        manifest = replace(result.unified_run_manifest, output_artifacts=hashes)
        _write_json(run_dir / "unified_run_manifest.json", manifest)
        hashes["unified_run_manifest.json"] = _sha256_file(run_dir / "unified_run_manifest.json")
        _write_json(run_dir / "artifact_hashes.json", hashes)
        _write_readme(run_dir, result)
        return run_dir

    def _run_online_event_loop(
        self,
        request: BacktestRunRequest,
        strategy: OpenShortCloseCoverStrategy,
        events: tuple[ReplayEvent, ...],
        schedule: Mapping[str, datetime],
    ) -> dict[str, list[Any]]:
        outputs: dict[str, list[Any]] = {
            "decisions": [],
            "intents": [],
            "orders": [],
            "order_results": [],
            "fills": [],
            "cost_breakdowns": [],
            "event_loop_trace": [],
            "cash_ledger": [],
            "equity_curve": [],
        }
        event_sequence = tuple(events)
        if not event_sequence:
            raise BacktestRunError("BT011_REPLAY_EVENTS_REQUIRED", "no replay events available")
        cash, position_states, equity_curve = _initial_accounting_state(request, event_sequence[0].available_at)
        outputs["equity_curve"].extend(equity_curve)

        agenda = self._pre_register_agenda(request, strategy, schedule)
        outputs["decisions"].extend(item["decision"] for item in agenda)
        outputs["intents"].extend(item["intent"] for item in agenda)
        pending_by_event = {
            (item["ticker"], item["target_bar_ts_start"], item["target_label"]): item
            for item in agenda
        }
        target_labels_by_ts = {
            schedule["entry_bar_ts_start"]: (ENTRY_OPEN_LABEL,),
            schedule["exit_bar_ts_start"]: (EXIT_CLOSE_LABEL,),
        }
        seen_targets: set[tuple[str, str]] = set()
        finalized_orders: list[BacktestOrderRecord] = []
        cash_ledger: list[CashLedgerEntryV0] = []

        for replay_event_index, event in enumerate(event_sequence):
            ticker = str(getattr(event, "ticker", ""))
            if ticker not in request.strategy_spec.symbols:
                continue
            for target_label in target_labels_by_ts.get(_event_ts_start(event), ()):
                item = pending_by_event.get((ticker, _event_ts_start(event), target_label))
                if item is None:
                    continue
                order = item["order"]
                execution_order = self._execution_order(order)
                result = self.simulator.simulate_order(execution_order, (event,))
                seen_targets.add((ticker, target_label))
                finalized_orders.append(replace(order, status=result.terminal_order_outcome))
                outputs["order_results"].append(result)

                position_after = int(position_states[ticker]["quantity"])
                cash_after = cash
                equity_after = outputs["equity_curve"][-1].equity
                accounting_index = -1
                if result.fill is not None:
                    outputs["fills"].append(result.fill)
                    if result.cost_breakdown is None:
                        raise BacktestRunError("BT011_FILL_WITHOUT_COST_BREAKDOWN", result.fill.fill_id)
                    outputs["cost_breakdowns"].append(result.cost_breakdown)
                    cash, position_after, cash_after, equity_after = _apply_fill_online(
                        result.fill,
                        result.cost_breakdown,
                        cash,
                        position_states,
                        cash_ledger,
                        outputs["equity_curve"],
                    )
                    accounting_index = replay_event_index

                outputs["event_loop_trace"].append(
                    EventLoopTraceRecord(
                        event_loop_mode=EVENT_LOOP_MODE,
                        replay_event_index=replay_event_index,
                        replay_event_type=str(getattr(event, "event_type")),
                        ticker=ticker,
                        target_label=target_label,
                        event_available_at=event.available_at,
                        source_bar_id=_event_id(event),
                        source_bar_ts_start=_event_ts_start(event),
                        source_bar_ts_end=_event_ts_end(event),
                        source_bar_available_at=event.available_at,
                        decision_id=item["decision"].decision_id,
                        decision_timestamp=item["decision"].decision_timestamp,
                        order_id=order.order_id,
                        order_submission_timestamp=order.order_submission_timestamp,
                        order_registered_before_replay_started=True,
                        order_registered_before_replay_event=True,
                        order_registration_replay_index=-1,
                        order_activation_timestamp=order.order_submission_timestamp,
                        coordinator_clock_at_order_registration=order.order_submission_timestamp,
                        eligible_replay_event_index=replay_event_index,
                        accounting_applied_at_replay_event_index=accounting_index,
                        position_after_fill=position_after,
                        cash_after_fill=cash_after,
                        equity_after_fill=equity_after,
                        simulator_event_count=1,
                        max_replay_event_index_visible_to_simulator=replay_event_index,
                        terminal_order_outcome=result.terminal_order_outcome,
                    )
                )
        outputs["orders"].extend(finalized_orders)
        outputs["cash_ledger"].extend(cash_ledger)
        missing = [
            f"{symbol}:{label}"
            for symbol in request.strategy_spec.symbols
            for label in (ENTRY_OPEN_LABEL, EXIT_CLOSE_LABEL)
            if (symbol, label) not in seen_targets
        ]
        if missing:
            raise BacktestRunError("BT011_REQUIRED_TARGET_EVENT_NOT_OBSERVED", ",".join(missing))
        return outputs

    def _pre_register_agenda(
        self,
        request: BacktestRunRequest,
        strategy: OpenShortCloseCoverStrategy,
        schedule: Mapping[str, datetime],
    ) -> list[dict[str, Any]]:
        agenda: list[dict[str, Any]] = []
        for target_label, target_ts in (
            (ENTRY_OPEN_LABEL, schedule["entry_bar_ts_start"]),
            (EXIT_CLOSE_LABEL, schedule["exit_bar_ts_start"]),
        ):
            for ticker in request.strategy_spec.symbols:
                decision = strategy.decision_for_target(ticker, target_label, target_ts)
                intent = strategy.intent_from_decision(decision)
                order = self._order_record_from_schedule(intent, target_ts)
                agenda.append(
                    {
                        "ticker": ticker,
                        "target_label": target_label,
                        "target_bar_ts_start": target_ts,
                        "decision": decision,
                        "intent": intent,
                        "order": order,
                    }
                )
        return agenda

    def _order_record_from_schedule(self, intent: BacktestOrderIntent, source_bar_ts_start: datetime) -> BacktestOrderRecord:
        source_bar_ts_end = source_bar_ts_start + timedelta(minutes=1)
        return BacktestOrderRecord(
            order_id=f"order-{intent.intent_id}",
            intent_id=intent.intent_id,
            decision_id=intent.decision_id,
            ticker=intent.ticker,
            side=intent.side,
            quantity=intent.quantity,
            order_type=intent.order_type,
            market_price_field=intent.market_price_field,
            time_in_force=DAY,
            fill_capability=FULL_FILL_ONLY,
            order_submission_timestamp=intent.created_at,
            eligible_source_bar_id=f"{intent.ticker}:{source_bar_ts_start.isoformat()}:{source_bar_ts_end.isoformat()}",
            eligible_source_bar_ts_start=source_bar_ts_start,
            eligible_source_bar_ts_end=source_bar_ts_end,
            eligible_source_bar_available_at=source_bar_ts_end,
            status="REGISTERED_ACTIVE",
        )

    def _order_record(self, intent: BacktestOrderIntent, target_event: ReplayEvent) -> BacktestOrderRecord:
        return BacktestOrderRecord(
            order_id=f"order-{intent.intent_id}",
            intent_id=intent.intent_id,
            decision_id=intent.decision_id,
            ticker=intent.ticker,
            side=intent.side,
            quantity=intent.quantity,
            order_type=intent.order_type,
            market_price_field=intent.market_price_field,
            time_in_force=DAY,
            fill_capability=FULL_FILL_ONLY,
            order_submission_timestamp=intent.created_at,
            eligible_source_bar_id=_event_id(target_event),
            eligible_source_bar_ts_start=_event_ts_start(target_event),
            eligible_source_bar_ts_end=_event_ts_end(target_event),
            eligible_source_bar_available_at=target_event.available_at,
            status="CREATED",
        )

    def _execution_order(self, order: BacktestOrderRecord) -> ExecutionOrder:
        return ExecutionOrder(
            order_id=order.order_id,
            ticker=order.ticker,
            side=order.side,
            quantity=order.quantity,
            order_type=MARKET_PROXY,
            order_submission_timestamp=order.order_submission_timestamp,
            time_in_force=DAY,
            market_price_field=order.market_price_field,
            fill_capability=FULL_FILL_ONLY,
        )

    def _manifest(
        self,
        request: BacktestRunRequest,
        preflight_report: Mapping[str, Any],
        replay_summary: ReplayRunSummary,
        summary: EndToEndRunSummary,
        output_artifacts: Mapping[str, str],
    ) -> UnifiedRunManifest:
        date_range = preflight_report.get("date_range", {})
        return UnifiedRunManifest(
            manifest_schema_version="bt_end_to_end_run_manifest_v0_1",
            run_id=request.run_id,
            gate_id=BT_GATE_011,
            capability=SINGLE_STRATEGY_END_TO_END_BACKTEST,
            strategy_id=request.strategy_spec.strategy_id,
            strategy_spec_version=request.strategy_spec.strategy_spec_version,
            fixture_id=request.fixture_id,
            input_identities={
                "preflight_report_path": request.preflight_report_path,
                "preflight_report_sha256": replay_summary.replay_preflight_report_sha256,
                "replay_event_sequence_sha256": replay_summary.replay_event_sequence_sha256,
                "dataset_id": preflight_report.get("dataset_id"),
                "fixture_kind": preflight_report.get("fixture_kind"),
                "portable_acceptance_fixture": bool(preflight_report.get("portable_acceptance_fixture")),
            },
            symbol_set=request.strategy_spec.symbols,
            session={
                "session_date": request.session_date.isoformat(),
                "date_range": date_range,
                "session_policy": preflight_report.get("session_policy"),
                "timezone": preflight_report.get("timezone"),
                "calendar_id": preflight_report.get("calendar_id"),
                "event_loop_mode": summary.event_loop_mode,
            },
            initial_cash=request.starting_equity,
            quantity_policy={
                "policy_id": "FIXED_QUANTITY_PER_SYMBOL_V0_1",
                "quantity_per_symbol": request.strategy_spec.quantity_per_symbol,
            },
            execution_profile=self.simulator.run_manifest().to_dict(),
            cost_model=self.cost_model.to_dict(),
            slippage_model=self.slippage_model.to_dict(),
            accounting_policy={
                "policy_id": "BT011_FILL_RECORD_ACCOUNTING_V0_1",
                "cost_source": "DeterministicFillSimulator.CostBreakdownV0",
                "rounding_policy_id": ROUND_HALF_EVEN_CENTS,
                "costs_counted_exactly_once": True,
            },
            software_identity={
                "package": "tsis-backtest-engine",
                "package_version": "0.1.0",
                "python_module": "tsis_backtest.backtest.runner",
            },
            run_classifications={
                "RUN_PURPOSE": request.run_purpose,
                "EDGE_EVIDENCE": request.edge_evidence,
                "ECONOMIC_REALISM": request.economic_realism,
                "STRATEGY_OPTIMIZATION": request.strategy_optimization,
                "NOT_EDGE_EVIDENCE": True,
                "NOT_ECONOMICALLY_REALISTIC": True,
            },
            output_artifacts=output_artifacts,
            validation_status=summary.validation_status,
            reconciliation_status="PASS" if summary.validation_status == "PASS" else "FAIL",
            state_provider_restrictions={
                "StateReplayFeed": "NOT_AUTHORIZED",
                "state_bundle_physical_read": "NOT_AUTHORIZED",
                "Market State consumption": "NOT_AUTHORIZED",
                "Event State consumption": "NOT_AUTHORIZED",
                "provider modification": "NOT_AUTHORIZED",
            },
        )

    @staticmethod
    def _validate_request(request: BacktestRunRequest) -> None:
        if request.run_purpose != ENGINE_VALIDATION_RUN:
            raise BacktestRunError("BT011_RUN_PURPOSE_UNSUPPORTED", request.run_purpose)
        if request.edge_evidence != "NOT_AUTHORIZED":
            raise BacktestRunError("BT011_EDGE_EVIDENCE_UNAUTHORIZED", request.edge_evidence)
        if request.strategy_optimization != "NOT_AUTHORIZED":
            raise BacktestRunError("BT011_OPTIMIZATION_UNAUTHORIZED", request.strategy_optimization)
        if request.starting_equity <= Decimal("0"):
            raise BacktestRunError("BT011_STARTING_EQUITY_NOT_POSITIVE", str(request.starting_equity))
        if not request.preflight_report_path.exists():
            raise BacktestRunError("BT011_PREFLIGHT_REPORT_NOT_FOUND", str(request.preflight_report_path))

    @staticmethod
    def _validate_schedule(request: BacktestRunRequest, preflight_report: Mapping[str, Any], schedule: Mapping[str, datetime]) -> None:
        if preflight_report.get("session_policy") != "REGULAR_ONLY":
            raise BacktestRunError("BT011_SESSION_POLICY_UNSUPPORTED", str(preflight_report.get("session_policy")))
        date_range = preflight_report.get("date_range", {})
        if date_range.get("date_start") != request.session_date.isoformat() or date_range.get("date_end") != request.session_date.isoformat():
            raise BacktestRunError("BT011_REQUEST_PREFLIGHT_DATE_MISMATCH", str(date_range))
        if schedule["entry_bar_ts_start"] >= schedule["exit_bar_ts_start"]:
            raise BacktestRunError("BT011_SESSION_SCHEDULE_INVALID", "entry bar must precede final regular bar")


def _initial_accounting_state(
    request: BacktestRunRequest,
    initial_timestamp: datetime,
) -> tuple[Decimal, dict[str, dict[str, Any]], list[EquityCurvePoint]]:
    cash = money(request.starting_equity)
    positions: dict[str, dict[str, Any]] = {
        ticker: {"quantity": 0, "avg_entry": None, "realized_gross": Decimal("0.00"), "costs": Decimal("0.00"), "last_mark": None}
        for ticker in request.strategy_spec.symbols
    }
    equity_curve = [EquityCurvePoint(0, initial_timestamp, cash, Decimal("0.00"), cash, "INITIAL_EQUITY")]
    return cash, positions, equity_curve


def _apply_fill_online(
    fill: FillRecord,
    cost_breakdown: CostBreakdownV0,
    cash: Decimal,
    positions: dict[str, dict[str, Any]],
    cash_ledger: list[CashLedgerEntryV0],
    equity_curve: list[EquityCurvePoint],
) -> tuple[Decimal, int, Decimal, Decimal]:
    state = positions[fill.ticker]
    quantity = int(fill.fill_quantity)
    notional = money(fill.gross_notional)
    cost = money(cost_breakdown.total_cost)
    if fill.side == SELL_SHORT:
        if state["quantity"] != 0:
            raise BacktestRunError("BT011_MULTIPLE_OPEN_POSITIONS_UNSUPPORTED", fill.ticker)
        cash = money(cash + notional)
        cash_ledger.append(_cash_entry(fill, "SHORT_SALE_PROCEEDS", notional, cash))
        state["quantity"] = -quantity
        state["avg_entry"] = fill.fill_price
    elif fill.side == BUY_TO_COVER:
        if state["quantity"] != -quantity or state["avg_entry"] is None:
            raise BacktestRunError("BT011_COVER_WITHOUT_MATCHING_SHORT", fill.ticker)
        cash = money(cash - notional)
        cash_ledger.append(_cash_entry(fill, "SHORT_COVER_PAYMENT", -notional, cash))
        state["realized_gross"] = money(state["realized_gross"] + dec(quantity) * (dec(state["avg_entry"]) - fill.fill_price))
        state["quantity"] = 0
        state["avg_entry"] = None
    else:
        raise BacktestRunError("BT011_FILL_SIDE_UNSUPPORTED", fill.side)

    if cost:
        cash = money(cash - cost)
        cash_ledger.append(_cash_entry(fill, "COST", -cost, cash))
    state["costs"] = money(state["costs"] + cost)
    state["last_mark"] = fill.fill_price
    equity_curve.append(_equity_point(len(equity_curve), fill.fill_recorded_at, cash, positions, f"AFTER_FILL:{fill.fill_id}"))
    return cash, int(state["quantity"]), cash, equity_curve[-1].equity


def _build_accounting(
    request: BacktestRunRequest,
    fills: list[FillRecord],
    cost_breakdowns: list[CostBreakdownV0],
) -> dict[str, tuple[Any, ...]]:
    costs_by_fill = {breakdown.fill_id: breakdown for breakdown in cost_breakdowns if breakdown.fill_id is not None}
    cash = money(request.starting_equity)
    positions: dict[str, dict[str, Any]] = {
        ticker: {"quantity": 0, "avg_entry": None, "realized_gross": Decimal("0.00"), "costs": Decimal("0.00"), "last_mark": None}
        for ticker in request.strategy_spec.symbols
    }
    cash_ledger: list[CashLedgerEntryV0] = []
    equity_curve: list[EquityCurvePoint] = []
    first_ts = min((fill.fill_recorded_at for fill in fills), default=datetime.now(timezone.utc))
    equity_curve.append(EquityCurvePoint(0, first_ts, cash, Decimal("0.00"), cash, "INITIAL_EQUITY"))

    for fill in sorted(fills, key=lambda item: (item.fill_recorded_at, item.order_id, item.fill_id)):
        state = positions[fill.ticker]
        quantity = int(fill.fill_quantity)
        notional = money(fill.gross_notional)
        cost = money(costs_by_fill[fill.fill_id].total_cost) if fill.fill_id in costs_by_fill else Decimal("0.00")
        if fill.side == SELL_SHORT:
            if state["quantity"] != 0:
                raise BacktestRunError("BT011_MULTIPLE_OPEN_POSITIONS_UNSUPPORTED", fill.ticker)
            cash = money(cash + notional)
            cash_ledger.append(_cash_entry(fill, "SHORT_SALE_PROCEEDS", notional, cash))
            state["quantity"] = -quantity
            state["avg_entry"] = fill.fill_price
        elif fill.side == BUY_TO_COVER:
            if state["quantity"] != -quantity or state["avg_entry"] is None:
                raise BacktestRunError("BT011_COVER_WITHOUT_MATCHING_SHORT", fill.ticker)
            cash = money(cash - notional)
            cash_ledger.append(_cash_entry(fill, "SHORT_COVER_PAYMENT", -notional, cash))
            state["realized_gross"] = money(state["realized_gross"] + dec(quantity) * (dec(state["avg_entry"]) - fill.fill_price))
            state["quantity"] = 0
            state["avg_entry"] = None
        else:
            raise BacktestRunError("BT011_FILL_SIDE_UNSUPPORTED", fill.side)

        if cost:
            cash = money(cash - cost)
            cash_ledger.append(_cash_entry(fill, "COST", -cost, cash))
        state["costs"] = money(state["costs"] + cost)
        state["last_mark"] = fill.fill_price
        equity_curve.append(_equity_point(len(equity_curve), fill.fill_recorded_at, cash, positions, f"AFTER_FILL:{fill.fill_id}"))
    return {"cash_ledger": tuple(cash_ledger), "equity_curve": tuple(equity_curve)}


def _build_trades(
    symbols: tuple[str, ...],
    fills: list[FillRecord],
    cost_breakdowns: list[CostBreakdownV0],
) -> tuple[TradeRecord, ...]:
    fills_by_symbol: dict[str, list[FillRecord]] = {symbol: [] for symbol in symbols}
    for fill in fills:
        fills_by_symbol.setdefault(fill.ticker, []).append(fill)
    costs = {breakdown.fill_id: breakdown.total_cost for breakdown in cost_breakdowns if breakdown.fill_id is not None}
    trades: list[TradeRecord] = []
    for symbol in symbols:
        symbol_fills = sorted(fills_by_symbol.get(symbol, ()), key=lambda item: (item.execution_timestamp, item.fill_id))
        if len(symbol_fills) != 2:
            continue
        entry, exit_fill = symbol_fills
        if entry.side != SELL_SHORT or exit_fill.side != BUY_TO_COVER:
            raise BacktestRunError("BT011_TRADE_FILL_SEQUENCE_UNSUPPORTED", symbol)
        quantity = entry.fill_quantity
        gross = money(dec(quantity) * (entry.fill_price - exit_fill.fill_price))
        total_costs = money(dec(costs.get(entry.fill_id, Decimal("0.00"))) + dec(costs.get(exit_fill.fill_id, Decimal("0.00"))))
        trades.append(
            TradeRecord(
                trade_id=f"trade-{symbol}-{entry.fill_id}-{exit_fill.fill_id}",
                ticker=symbol,
                quantity=quantity,
                entry_order_id=entry.order_id,
                exit_order_id=exit_fill.order_id,
                entry_fill_id=entry.fill_id,
                exit_fill_id=exit_fill.fill_id,
                entry_execution_timestamp=entry.execution_timestamp,
                exit_execution_timestamp=exit_fill.execution_timestamp,
                entry_recorded_at=entry.fill_recorded_at,
                exit_recorded_at=exit_fill.fill_recorded_at,
                entry_price=entry.fill_price,
                exit_price=exit_fill.fill_price,
                gross_pnl=gross,
                total_costs=total_costs,
                net_pnl=money(gross - total_costs),
                terminal_outcome=FILLED,
            )
        )
    return tuple(trades)


def _final_positions(
    symbols: tuple[str, ...],
    fills: list[FillRecord],
    cost_breakdowns: list[CostBreakdownV0],
    trades: tuple[TradeRecord, ...],
) -> tuple[PositionSnapshot, ...]:
    trade_by_symbol = {trade.ticker: trade for trade in trades}
    costs_by_symbol: dict[str, Decimal] = {symbol: Decimal("0.00") for symbol in symbols}
    last_mark: dict[str, Decimal | None] = {symbol: None for symbol in symbols}
    quantity_by_symbol: dict[str, int] = {symbol: 0 for symbol in symbols}
    costs_by_fill = {breakdown.fill_id: breakdown.total_cost for breakdown in cost_breakdowns if breakdown.fill_id is not None}
    for fill in fills:
        costs_by_symbol[fill.ticker] = money(costs_by_symbol.get(fill.ticker, Decimal("0.00")) + dec(costs_by_fill.get(fill.fill_id, Decimal("0.00"))))
        last_mark[fill.ticker] = fill.fill_price
        if fill.side == SELL_SHORT:
            quantity_by_symbol[fill.ticker] -= fill.fill_quantity
        elif fill.side == BUY_TO_COVER:
            quantity_by_symbol[fill.ticker] += fill.fill_quantity
    positions = []
    for symbol in symbols:
        trade = trade_by_symbol.get(symbol)
        gross = trade.gross_pnl if trade else Decimal("0.00")
        costs = costs_by_symbol[symbol]
        positions.append(
            PositionSnapshot(
                ticker=symbol,
                quantity=quantity_by_symbol[symbol],
                average_entry_price=None if quantity_by_symbol[symbol] == 0 else last_mark[symbol],
                realized_gross_pnl=money(gross),
                realized_net_pnl=money(gross - costs),
                total_costs=money(costs),
                last_mark_price=last_mark[symbol],
            )
        )
    return tuple(positions)


def _metrics(starting_equity: Decimal, trades: tuple[TradeRecord, ...], equity_curve: tuple[EquityCurvePoint, ...]) -> MetricsSummary:
    gross_profit = money(sum((trade.gross_pnl for trade in trades if trade.gross_pnl > 0), Decimal("0.00")))
    gross_loss = money(sum((trade.gross_pnl for trade in trades if trade.gross_pnl < 0), Decimal("0.00")))
    gross_pnl = money(sum((trade.gross_pnl for trade in trades), Decimal("0.00")))
    total_costs = money(sum((trade.total_costs for trade in trades), Decimal("0.00")))
    net_pnl = money(sum((trade.net_pnl for trade in trades), Decimal("0.00")))
    ending_equity = money(starting_equity + net_pnl)
    peak = None
    max_drawdown = Decimal("0.00")
    for point in equity_curve:
        equity = point.equity
        peak = equity if peak is None or equity > peak else peak
        drawdown = money(peak - equity)
        max_drawdown = drawdown if drawdown > max_drawdown else max_drawdown
    profit_factor = None if gross_loss == 0 else money(gross_profit / abs(gross_loss))
    return MetricsSummary(
        trade_count=len(trades),
        winning_trade_count=sum(1 for trade in trades if trade.net_pnl > 0),
        losing_trade_count=sum(1 for trade in trades if trade.net_pnl < 0),
        flat_trade_count=sum(1 for trade in trades if trade.net_pnl == 0),
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        gross_pnl=gross_pnl,
        total_costs=total_costs,
        net_pnl=net_pnl,
        starting_equity=money(starting_equity),
        ending_equity=ending_equity,
        return_pct=money((net_pnl / starting_equity) * Decimal("100")),
        max_drawdown=max_drawdown,
        profit_factor=profit_factor,
        edge_evaluated=False,
        economic_realism_complete=False,
    )


def _validation_status(
    request: BacktestRunRequest,
    order_results: list[OrderSimulationResult],
    fills: list[FillRecord],
    positions: tuple[PositionSnapshot, ...],
    metrics: MetricsSummary,
    event_loop_trace: list[EventLoopTraceRecord],
) -> str:
    expected_orders = len(request.strategy_spec.symbols) * 2
    if len(order_results) != expected_orders or len(fills) != expected_orders:
        return "FAIL"
    if len(event_loop_trace) != expected_orders:
        return "FAIL"
    if any(result.terminal_order_outcome != FILLED for result in order_results):
        return "FAIL"
    if any(position.quantity != 0 for position in positions):
        return "FAIL"
    if metrics.ending_equity != money(metrics.starting_equity + metrics.net_pnl):
        return "FAIL"
    if _future_event_access_detected(event_loop_trace):
        return "FAIL"
    if not _orders_pre_registered(event_loop_trace):
        return "FAIL"
    if not _accounting_applied_inside_loop(event_loop_trace):
        return "FAIL"
    return "PASS"


def _validation_report(result: EndToEndBacktestResult) -> dict[str, Any]:
    expected_orders = len(result.strategy_spec.symbols) * 2
    final_positions_zero = all(position.quantity == 0 for position in result.positions)
    order_results_filled = all(item.terminal_order_outcome == FILLED for item in result.order_results)
    costs_from_simulator = sum((dec(item.total_cost) for item in result.cost_breakdowns), Decimal("0.00"))
    costs_from_trades = sum((trade.total_costs for trade in result.trades), Decimal("0.00"))
    future_access = _future_event_access_detected(list(result.event_loop_trace))
    orders_pre_registered = _orders_pre_registered(result.event_loop_trace)
    accounting_online = _accounting_applied_inside_loop(result.event_loop_trace)
    return {
        "status": result.summary.validation_status,
        "gate_id": BT_GATE_011,
        "capability": SINGLE_STRATEGY_END_TO_END_BACKTEST,
        "run_id": result.request.run_id,
        "expected_order_count": expected_orders,
        "actual_order_count": len(result.orders),
        "actual_fill_count": len(result.fills),
        "order_count_matches": len(result.orders) == expected_orders,
        "fill_count_matches": len(result.fills) == expected_orders,
        "order_results_all_filled": order_results_filled,
        "final_positions_zero": final_positions_zero,
        "costs_counted_exactly_once": money(costs_from_simulator) == money(costs_from_trades) == result.metrics.total_costs,
        "ending_equity_reconciles": result.metrics.ending_equity == money(result.metrics.starting_equity + result.metrics.net_pnl),
        "event_loop_integration_proven": len(result.event_loop_trace) == expected_orders and not future_access and orders_pre_registered and accounting_online,
        "event_loop_mode": result.summary.event_loop_mode,
        "orders_pre_registered_before_replay": orders_pre_registered,
        "order_created_during_event_processing": not orders_pre_registered,
        "accounting_applied_inside_event_loop": accounting_online,
        "simulator_called_with_single_current_event_only": all(item.simulator_event_count == 1 for item in result.event_loop_trace),
        "future_event_access_detected": future_access,
        "state_provider_restrictions_preserved": True,
        "run_classifications": {
            "RUN_PURPOSE": result.request.run_purpose,
            "EDGE_EVIDENCE": result.request.edge_evidence,
            "ECONOMIC_REALISM": result.request.economic_realism,
            "STRATEGY_OPTIMIZATION": result.request.strategy_optimization,
        },
        "prohibited_capabilities_activated": [],
        "deterministic_output_hash": result.summary.deterministic_output_hash,
    }


def _session_schedule(preflight_report: Mapping[str, Any]) -> dict[str, datetime]:
    date_range = preflight_report.get("date_range", {})
    if date_range.get("date_start") != date_range.get("date_end"):
        raise BacktestRunError("BT011_MULTI_SESSION_NOT_SUPPORTED", str(date_range))
    session_date = datetime.fromisoformat(str(date_range["date_start"])).date()
    tz = ZoneInfo(str(preflight_report.get("timezone", "America/New_York")))
    session_start = datetime.combine(session_date, time(9, 30), tzinfo=tz).astimezone(timezone.utc)
    session_end = datetime.combine(session_date, time(16, 0), tzinfo=tz).astimezone(timezone.utc)
    return {
        "entry_bar_ts_start": session_start,
        "exit_bar_ts_start": session_end - timedelta(minutes=1),
        "session_end": session_end,
    }


def _event_ts_start(event: ReplayEvent) -> datetime:
    if isinstance(event, ReplayBarEvent):
        return event.bar.ts_start
    if isinstance(event, ReplayGapEvent):
        return event.ts_start
    raise BacktestRunError("BT011_REPLAY_EVENT_UNSUPPORTED", str(type(event)))


def _event_ts_end(event: ReplayEvent) -> datetime:
    if isinstance(event, ReplayBarEvent):
        return event.bar.ts_end
    if isinstance(event, ReplayGapEvent):
        return event.ts_end
    raise BacktestRunError("BT011_REPLAY_EVENT_UNSUPPORTED", str(type(event)))


def _event_id(event: ReplayEvent) -> str:
    if isinstance(event, ReplayBarEvent):
        return _bar_id(event)
    if isinstance(event, ReplayGapEvent):
        return f"{event.ticker}:{event.ts_start.isoformat()}:{event.ts_end.isoformat()}:GAP"
    raise BacktestRunError("BT011_REPLAY_EVENT_UNSUPPORTED", str(type(event)))


def _orders_pre_registered(event_loop_trace: list[EventLoopTraceRecord] | tuple[EventLoopTraceRecord, ...]) -> bool:
    return all(
        item.order_registered_before_replay_started
        and item.order_registered_before_replay_event
        and item.order_registration_replay_index == -1
        and item.order_activation_timestamp == item.order_submission_timestamp
        and item.coordinator_clock_at_order_registration == item.order_submission_timestamp
        and item.eligible_replay_event_index == item.replay_event_index
        and item.order_submission_timestamp <= item.source_bar_ts_start
        for item in event_loop_trace
    )


def _accounting_applied_inside_loop(event_loop_trace: list[EventLoopTraceRecord] | tuple[EventLoopTraceRecord, ...]) -> bool:
    return all(
        item.terminal_order_outcome == FILLED
        and item.accounting_applied_at_replay_event_index == item.replay_event_index
        for item in event_loop_trace
    )


def _future_event_access_detected(event_loop_trace: list[EventLoopTraceRecord] | tuple[EventLoopTraceRecord, ...]) -> bool:
    return any(item.max_replay_event_index_visible_to_simulator > item.replay_event_index for item in event_loop_trace)


def _bar_id(event: ReplayBarEvent) -> str:
    bar = event.bar
    return f"{bar.ticker}:{bar.ts_start.isoformat()}:{bar.ts_end.isoformat()}"


def _cash_entry(fill: FillRecord, entry_type: str, amount: Decimal, cash_after: Decimal) -> CashLedgerEntryV0:
    return CashLedgerEntryV0(
        entry_id=f"cash-{fill.fill_id}-{entry_type}",
        ticker=fill.ticker,
        fill_id=fill.fill_id,
        order_id=fill.order_id,
        entry_type=entry_type,
        amount=money(amount),
        cash_after=money(cash_after),
        recorded_at=fill.fill_recorded_at,
        description=entry_type.lower().replace("_", " "),
    )


def _equity_point(
    sequence: int,
    timestamp: datetime,
    cash: Decimal,
    positions: Mapping[str, Mapping[str, Any]],
    reason: str,
) -> EquityCurvePoint:
    market_value = Decimal("0.00")
    for state in positions.values():
        quantity = int(state["quantity"])
        last_mark = state["last_mark"]
        if quantity and last_mark is not None:
            market_value += dec(quantity) * dec(last_mark)
    market_value = money(market_value)
    return EquityCurvePoint(sequence, timestamp, money(cash), market_value, money(cash + market_value), reason)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(to_jsonable(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_readme(run_dir: Path, result: EndToEndBacktestResult) -> None:
    text = f"""# BT-GATE-011 End-To-End Run

run_id: {result.request.run_id}
status: {result.summary.validation_status}
purpose: ENGINE_VALIDATION_RUN
edge: NOT_AUTHORIZED
economic_realism: INCOMPLETE
event_loop_mode: {result.summary.event_loop_mode}

This run validates the backtest engine path only. It is not evidence of edge and
does not claim small-caps execution realism.
"""
    (run_dir / "README.md").write_text(text, encoding="utf-8")
