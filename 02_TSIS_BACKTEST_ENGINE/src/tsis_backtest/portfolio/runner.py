"""BT-GATE-012 multi-symbol multi-session portfolio runner."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from tsis_backtest.backtest.contracts import (
    BUY_TO_COVER, DAY, ENGINE_VALIDATION_RUN, ENTRY_OPEN_LABEL, EXIT_CLOSE_LABEL,
    FULL_FILL_ONLY, MARKET_PROXY, NOT_EDGE_EVIDENCE, SELL_SHORT,
    BacktestOrderIntent, BacktestOrderRecord, BacktestRunError, CashLedgerEntryV0,
    EquityCurvePoint, MetricsSummary, PositionSnapshot, StrategyDecision,
    TradeRecord, canonical_hash, dec, money, to_jsonable,
)
from tsis_backtest.execution.contracts import (
    FILLED, CostBreakdownV0, CostModelV0, ExecutionOrder, ExecutionPolicy,
    FillRecord, OrderSimulationResult, SlippageModel,
)
from tsis_backtest.execution.simulator import DeterministicFillSimulator
from tsis_backtest.preflight.real_data_inspector import sha256_file
from tsis_backtest.replay import HistoricalReplayFeed, ReplayBarEvent, ReplayGapEvent
from tsis_backtest.replay.contracts import ReplayEvent, ReplayRunSummary

from .contracts import (
    ACTIVE_ORDER_EVALUATION_ORDER_V0_1, BT_GATE_012, GLOBAL_REPLAY_ORDER_V0_1,
    MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE, PORTFOLIO_EQUITY_POLICY_V0_1,
    PORTFOLIO_EVENT_LOOP_MODE_V0_1, REGULAR_ONLY_XNYS_V0_1,
    TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1, EventSequenceRecord,
    PortfolioEventLoopTraceRecord, PortfolioRunManifest, PortfolioRunRequest,
    PortfolioRunResult, PortfolioRunSummary, PortfolioSessionResult,
    SessionCalendarEntry,
)


class PortfolioSliceRunner:
    def __init__(self, execution_policy: ExecutionPolicy | None = None, slippage_model: SlippageModel | None = None, cost_model: CostModelV0 | None = None) -> None:
        self.execution_policy = execution_policy or ExecutionPolicy()
        self.slippage_model = slippage_model or SlippageModel("zero_slippage_v0_1")
        self.cost_model = cost_model or CostModelV0("bt_gate_012_commission_minimum_v0_1", commission_per_share=Decimal("0.005"), minimum_commission_per_order=Decimal("1.00"))
        self.simulator = DeterministicFillSimulator(self.execution_policy, self.slippage_model, self.cost_model)

    def run(self, request: PortfolioRunRequest) -> PortfolioRunResult:
        self._validate_request(request)
        calendar_payload, calendar = self._load_calendar(request)
        events, replay_summaries, preflight_reports = self._load_events(request)
        ordered_events, event_sequence_manifest = self._global_order(events)
        self._validate_fixture_profile(request, calendar, ordered_events)
        agenda = self._pre_register_agenda(request, calendar)
        loop = self._run_event_loop(request, ordered_events, agenda)
        decisions = tuple(item["decision"] for item in agenda)
        intents = tuple(item["intent"] for item in agenda)
        orders = tuple(loop["orders"])
        order_results = tuple(loop["order_results"])
        fills = tuple(loop["fills"])
        cost_breakdowns = tuple(loop["cost_breakdowns"])
        trades = self._build_trades(request, fills, cost_breakdowns, loop["order_session"])
        positions = self._final_positions(request, fills, cost_breakdowns, trades, loop["last_marks"])
        session_results = self._session_results(request, trades, loop["session_cash"], positions)
        equity_curve = tuple(loop["equity_curve"])
        metrics = self._metrics(request.starting_equity, trades, equity_curve)
        event_sequence_hash = canonical_hash(event_sequence_manifest)
        active_order_hash = canonical_hash([t.active_order_evaluation_key for t in loop["event_loop_trace"] if t.active_order_evaluation_key is not None])
        equity_hash = canonical_hash(equity_curve)
        deterministic_output_hash = canonical_hash({
            "strategy_spec": request.strategy_spec,
            "calendar": calendar_payload,
            "event_sequence_manifest": event_sequence_manifest,
            "decisions": decisions,
            "order_intents": intents,
            "orders": orders,
            "order_results": order_results,
            "fills": fills,
            "cost_breakdowns": cost_breakdowns,
            "event_loop_trace": tuple(loop["event_loop_trace"]),
            "trades": trades,
            "cash_ledger": tuple(loop["cash_ledger"]),
            "positions": positions,
            "session_results": session_results,
            "equity_curve": equity_curve,
            "metrics": metrics,
        })
        validation_status = self._validation_status(request, ordered_events, order_results, fills, positions, session_results, metrics, loop)
        summary = PortfolioRunSummary(
            request.run_id, BT_GATE_012, MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE,
            request.fixture_id, len(request.session_dates), len(request.strategy_spec.symbols),
            len(request.session_dates) * len(request.strategy_spec.symbols), len(ordered_events),
            sum(isinstance(e, ReplayBarEvent) for e in ordered_events), sum(isinstance(e, ReplayGapEvent) for e in ordered_events),
            len(orders), len(fills), len(trades), all(p.quantity == 0 for p in positions),
            PORTFOLIO_EVENT_LOOP_MODE_V0_1, len(loop["event_loop_trace"]), event_sequence_hash,
            active_order_hash, equity_hash, metrics.gross_pnl, metrics.total_costs, metrics.net_pnl,
            metrics.ending_equity, deterministic_output_hash, validation_status, request.run_purpose,
            request.edge_evidence, request.economic_realism, request.strategy_optimization,
            ("ENGINE_VALIDATION_RUN only", "NOT_EDGE_EVIDENCE", "NOT_ECONOMICALLY_REALISTIC", "capital allocation not implemented", "buying power and margin not implemented", "capital contention claim not authorized", "borrow/locates not implemented", "SSR not implemented", "halts not implemented", "liquidity/capacity not implemented", "StateReplayFeed and Market/Event State consumption not authorized"),
        )
        manifest = self._manifest(request, preflight_reports, replay_summaries, calendar_payload, summary, {})
        return PortfolioRunResult(request, request.strategy_spec, calendar_payload, tuple(event_sequence_manifest), decisions, intents, orders, order_results, fills, cost_breakdowns, tuple(loop["event_loop_trace"]), trades, tuple(loop["cash_ledger"]), positions, session_results, equity_curve, metrics, summary, manifest)

    def write_result(self, result: PortfolioRunResult, determinism_report: Mapping[str, Any] | None = None) -> Path:
        run_dir = result.request.output_root / result.request.run_id
        if run_dir.exists() and any(run_dir.iterdir()):
            raise BacktestRunError("BT012_OUTPUT_DIR_NOT_EMPTY", str(run_dir))
        run_dir.mkdir(parents=True, exist_ok=True)
        artifacts = {
            "configuration_snapshot.json": result.request,
            "portfolio_strategy_spec.json": result.strategy_spec,
            "event_sequence_manifest.json": result.event_sequence_manifest,
            "decisions.json": result.decisions,
            "order_intents.json": result.order_intents,
            "orders.json": result.orders,
            "order_simulation_results.json": result.order_results,
            "fills.json": result.fills,
            "event_loop_trace.json": result.event_loop_trace,
            "trade_ledger.json": {"trades": result.trades, "fills": result.fills, "cost_breakdowns": result.cost_breakdowns},
            "cash_ledger.json": result.cash_ledger,
            "positions_by_symbol.json": result.positions_by_symbol,
            "session_results.json": result.session_results,
            "portfolio_equity_curve.json": result.portfolio_equity_curve,
            "session_calendar_snapshot.json": result.session_calendar_snapshot,
            "metrics_summary.json": result.metrics,
            "validation_report.json": self._validation_report(result),
            "determinism_report.json": determinism_report or {"status": "NOT_EXECUTED"},
        }
        for name, payload in artifacts.items():
            _write_json(run_dir / name, payload)
        hashes = {name: sha256_file(run_dir / name) for name in artifacts}
        manifest = replace(result.portfolio_run_manifest, output_artifacts=hashes)
        _write_json(run_dir / "portfolio_run_manifest.json", manifest)
        hashes["portfolio_run_manifest.json"] = sha256_file(run_dir / "portfolio_run_manifest.json")
        _write_json(run_dir / "artifact_hashes.json", hashes)
        _write_readme(run_dir, result)
        return run_dir
    def _validate_request(self, request: PortfolioRunRequest) -> None:
        if request.run_purpose != ENGINE_VALIDATION_RUN:
            raise BacktestRunError("BT012_RUN_PURPOSE_UNAUTHORIZED", request.run_purpose)
        if request.edge_evidence not in {NOT_EDGE_EVIDENCE, "NOT_AUTHORIZED"}:
            raise BacktestRunError("BT012_EDGE_EVIDENCE_UNAUTHORIZED", request.edge_evidence)
        if request.economic_realism != "INCOMPLETE" or request.strategy_optimization != "NOT_AUTHORIZED":
            raise BacktestRunError("BT012_RUN_CLASSIFICATION_UNAUTHORIZED", request.run_id)
        if len(request.session_dates) < 2 or len(request.strategy_spec.symbols) < 3:
            raise BacktestRunError("BT012_FIXTURE_MINIMUM_NOT_MET", request.run_id)
        if len(set(request.strategy_spec.symbols)) != len(request.strategy_spec.symbols):
            raise BacktestRunError("BT012_DUPLICATE_SYMBOLS", str(request.strategy_spec.symbols))
        if len(request.preflight_report_paths) != len(request.session_dates):
            raise BacktestRunError("BT012_PREFLIGHT_SESSION_COUNT_MISMATCH", str(request.preflight_report_paths))

    def _load_calendar(self, request: PortfolioRunRequest) -> tuple[Mapping[str, Any], dict[date, SessionCalendarEntry]]:
        if not request.session_calendar_snapshot_path.exists():
            raise BacktestRunError("BT012_SESSION_CALENDAR_SNAPSHOT_NOT_FOUND", str(request.session_calendar_snapshot_path))
        actual_hash = sha256_file(request.session_calendar_snapshot_path)
        if actual_hash != request.session_calendar_snapshot_sha256:
            raise BacktestRunError("BT012_SESSION_CALENDAR_SNAPSHOT_HASH_MISMATCH", actual_hash)
        payload = _read_json(request.session_calendar_snapshot_path)
        if payload.get("calendar_authority") != TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1:
            raise BacktestRunError("BT012_CALENDAR_AUTHORITY_UNSUPPORTED", str(payload.get("calendar_authority")))
        entries = {}
        for row in payload.get("sessions", ()): 
            entry = SessionCalendarEntry(
                date.fromisoformat(str(row["session_date"])), _parse_utc(row["regular_open_utc"]), _parse_utc(row["regular_close_utc"]),
                str(row.get("calendar_id", "XNYS")), str(row.get("timezone", "America/New_York")), bool(row.get("early_close", False)),
            )
            if entry.early_close:
                raise BacktestRunError("BT012_EARLY_CLOSE_NOT_ADMITTED", entry.session_date.isoformat())
            entries[entry.session_date] = entry
        if set(entries) != set(request.session_dates):
            raise BacktestRunError("BT012_CALENDAR_SESSION_SET_MISMATCH", str(sorted(entries)))
        return payload, entries

    def _load_events(self, request: PortfolioRunRequest) -> tuple[tuple[ReplayEvent, ...], tuple[ReplayRunSummary, ...], tuple[Mapping[str, Any], ...]]:
        events = []
        summaries = []
        reports = []
        for path in request.preflight_report_paths:
            report = _read_json(path)
            feed = HistoricalReplayFeed.from_preflight_report(path)
            events.extend(feed.stream_events())
            summaries.append(feed.summarize())
            reports.append(report)
        return tuple(events), tuple(summaries), tuple(reports)

    def _global_order(self, events: tuple[ReplayEvent, ...]) -> tuple[tuple[ReplayEvent, ...], tuple[EventSequenceRecord, ...]]:
        keyed = [(self._global_order_key(event), event) for event in events]
        keys = [key for key, _ in keyed]
        if len(set(keys)) != len(keys):
            raise BacktestRunError("BT012_UNRESOLVED_GLOBAL_REPLAY_ORDER_TIE", str([key for key in keys if keys.count(key) > 1][:3]))
        ordered = [event for _, event in sorted(keyed, key=lambda item: item[0])]
        records = []
        for index, event in enumerate(ordered):
            key = self._global_order_key(event)
            records.append(EventSequenceRecord(index, GLOBAL_REPLAY_ORDER_V0_1, key[0], key[1], key[2], str(getattr(event, "event_type")), key[3], key[4], key))
        return tuple(ordered), tuple(records)

    def _validate_fixture_profile(self, request: PortfolioRunRequest, calendar: Mapping[date, SessionCalendarEntry], events: tuple[ReplayEvent, ...]) -> None:
        if len(request.session_dates) * len(request.strategy_spec.symbols) < 6:
            raise BacktestRunError("BT012_SYMBOL_SESSION_MINIMUM_NOT_MET", str(request.session_dates))
        if not any(isinstance(event, ReplayGapEvent) for event in events):
            raise BacktestRunError("BT012_REPLAY_GAP_EVENT_REQUIRED", "fixture must include a ReplayGapEvent")
        by_available = {}
        for event in events:
            by_available.setdefault(event.available_at, set()).add(str(event.ticker).upper())
        if not any(len(symbols) >= 3 for symbols in by_available.values()):
            raise BacktestRunError("BT012_SAME_TIMESTAMP_CROSS_SYMBOL_EVENTS_REQUIRED", "missing same-timestamp cross-symbol event")
        bars = {(self._event_session_date(event), event.ticker.upper(), self._event_ts_start(event)) for event in events if isinstance(event, ReplayBarEvent)}
        for session_date, entry in calendar.items():
            for symbol in request.strategy_spec.symbols:
                if (session_date, symbol.upper(), entry.regular_open_utc) not in bars:
                    raise BacktestRunError("BT012_MISSING_CONTRACTUAL_OPEN", f"{session_date}:{symbol}")
                if (session_date, symbol.upper(), entry.regular_close_utc - timedelta(minutes=1)) not in bars:
                    raise BacktestRunError("BT012_MISSING_CONTRACTUAL_CLOSE", f"{session_date}:{symbol}")

    def _pre_register_agenda(self, request: PortfolioRunRequest, calendar: Mapping[date, SessionCalendarEntry]) -> list[dict[str, Any]]:
        agenda = []
        for session_date in sorted(calendar):
            entry = calendar[session_date]
            targets = ((ENTRY_OPEN_LABEL, SELL_SHORT, "open", entry.regular_open_utc), (EXIT_CLOSE_LABEL, BUY_TO_COVER, "close", entry.regular_close_utc - timedelta(minutes=1)))
            for label, side, price_field, target_ts in targets:
                suffix = "entry-open" if label == ENTRY_OPEN_LABEL else "exit-close"
                for ticker in request.strategy_spec.symbols:
                    decision_ts = target_ts - timedelta(microseconds=1)
                    decision = StrategyDecision(f"decision-{request.strategy_spec.strategy_id}-{session_date.isoformat()}-{ticker}-{suffix}", request.strategy_spec.strategy_id, request.strategy_spec.strategy_spec_version, ticker, side, request.strategy_spec.quantity_per_symbol, label, decision_ts, decision_ts, f"preprogrammed BT-GATE-012 {suffix} before eligible bar")
                    intent = BacktestOrderIntent(f"intent-{decision.decision_id}", decision.decision_id, ticker, side, decision.quantity, MARKET_PROXY, price_field, label, decision_ts, decision.reason)
                    order = BacktestOrderRecord(f"order-{session_date.isoformat()}-{ticker}-{label}", intent.intent_id, decision.decision_id, ticker, side, intent.quantity, MARKET_PROXY, price_field, DAY, FULL_FILL_ONLY, decision_ts, f"{ticker}:{target_ts.isoformat()}:{(target_ts + timedelta(minutes=1)).isoformat()}:BAR", target_ts, target_ts + timedelta(minutes=1), target_ts + timedelta(minutes=1), "REGISTERED_ACTIVE")
                    agenda.append({"session_date": session_date, "ticker": ticker, "target_label": label, "target_ts": target_ts, "decision": decision, "intent": intent, "order": order})
        return agenda

    def _run_event_loop(self, request: PortfolioRunRequest, events: tuple[ReplayEvent, ...], agenda: list[dict[str, Any]]) -> dict[str, Any]:
        cash = money(request.starting_equity)
        positions = {symbol: {"quantity": 0, "avg_entry": None, "realized_gross": Decimal("0.00"), "costs": Decimal("0.00"), "last_mark": None} for symbol in request.strategy_spec.symbols}
        cash_ledger = []
        equity_curve = [self._equity_point(0, events[0].available_at, cash, positions, "INITIAL_EQUITY")]
        pending = {(item["session_date"], item["ticker"].upper(), item["target_ts"], item["target_label"]): item for item in agenda}
        seen_orders = set()
        outputs = {"orders": [], "order_results": [], "fills": [], "cost_breakdowns": [], "event_loop_trace": [], "cash_ledger": cash_ledger, "equity_curve": equity_curve, "order_session": {}, "session_cash": {}, "last_marks": {}}
        current_session = None
        for index, event in enumerate(events):
            session_date = self._event_session_date(event)
            if current_session is not None and session_date != current_session:
                self._assert_flat_positions(positions, f"BT012_OVERNIGHT_POSITION_PROHIBITED:{current_session}")
            current_session = session_date
            ticker = str(event.ticker).upper()
            item = result = fill = breakdown = active_key = None
            accounting_index = None
            if isinstance(event, ReplayBarEvent):
                for label in (ENTRY_OPEN_LABEL, EXIT_CLOSE_LABEL):
                    item = pending.get((session_date, ticker, event.bar.ts_start, label))
                    if item is not None:
                        break
                if item is not None:
                    order = item["order"]
                    active_key = (index, order.order_submission_timestamp, order.order_id)
                    result = self.simulator.simulate_order(self._execution_order(order), (event,))
                    outputs["order_results"].append(result)
                    outputs["order_session"][order.order_id] = session_date
                    seen_orders.add(order.order_id)
                    outputs["orders"].append(replace(order, status=result.terminal_order_outcome))
                    if result.terminal_order_outcome != FILLED or result.fill is None or result.cost_breakdown is None:
                        raise BacktestRunError("BT012_REQUIRED_ORDER_NOT_FILLED", order.order_id)
                    fill = result.fill
                    breakdown = result.cost_breakdown
                    outputs["fills"].append(fill)
                    outputs["cost_breakdowns"].append(breakdown)
                    cash = self._apply_fill(fill, breakdown, cash, positions, cash_ledger)
                    accounting_index = index
                positions[ticker]["last_mark"] = dec(event.bar.close)
            equity_point = self._equity_point(len(equity_curve), event.available_at, cash, positions, self._equity_reason(event, fill))
            equity_curve.append(equity_point)
            outputs["session_cash"][session_date] = cash
            state = positions.get(ticker, {"quantity": 0, "last_mark": None})
            outputs["event_loop_trace"].append(PortfolioEventLoopTraceRecord(
                PORTFOLIO_EVENT_LOOP_MODE_V0_1, index, session_date, str(getattr(event, "event_type")), ticker, event.available_at,
                self._source_event_identity(event), self._global_order_key(event), item["target_label"] if item else None,
                item["decision"].decision_id if item else None, item["decision"].decision_timestamp if item else None,
                item["order"].order_id if item else None, item["order"].order_submission_timestamp if item else None,
                active_key, item is not None, item is not None, -1 if item is not None else None, index if item is not None else None,
                1 if item is not None else 0, index, result.terminal_order_outcome if result is not None else None,
                fill.fill_id if fill is not None else None, accounting_index, int(state["quantity"]), cash, equity_point.equity, state["last_mark"], False, False,
            ))
        missing = sorted({item["order"].order_id for item in agenda} - seen_orders)
        if missing:
            raise BacktestRunError("BT012_REQUIRED_TARGET_EVENT_NOT_OBSERVED", ",".join(missing[:10]))
        self._assert_flat_positions(positions, "BT012_SESSION_END_POSITION_NOT_ZERO")
        outputs["last_marks"] = {symbol: state["last_mark"] for symbol, state in positions.items()}
        return outputs
    def _execution_order(self, order: BacktestOrderRecord) -> ExecutionOrder:
        return ExecutionOrder(order.order_id, order.ticker, order.side, order.quantity, MARKET_PROXY, order.order_submission_timestamp, DAY, None, None, order.market_price_field, fill_capability=FULL_FILL_ONLY)

    def _apply_fill(self, fill: FillRecord, cost_breakdown: CostBreakdownV0, cash: Decimal, positions: dict[str, dict[str, Any]], cash_ledger: list[CashLedgerEntryV0]) -> Decimal:
        state = positions[fill.ticker]
        quantity = int(fill.fill_quantity)
        notional = money(fill.gross_notional)
        cost = money(cost_breakdown.total_cost)
        if fill.side == SELL_SHORT:
            if state["quantity"] != 0:
                raise BacktestRunError("BT012_MULTIPLE_OPEN_POSITIONS_UNSUPPORTED", fill.ticker)
            cash = money(cash + notional)
            cash_ledger.append(_cash_entry(fill, "SHORT_SALE_PROCEEDS", notional, cash))
            state["quantity"] = -quantity
            state["avg_entry"] = fill.fill_price
        elif fill.side == BUY_TO_COVER:
            if state["quantity"] != -quantity or state["avg_entry"] is None:
                raise BacktestRunError("BT012_COVER_WITHOUT_MATCHING_SHORT", fill.ticker)
            cash = money(cash - notional)
            cash_ledger.append(_cash_entry(fill, "SHORT_COVER_PAYMENT", -notional, cash))
            state["realized_gross"] = money(state["realized_gross"] + dec(quantity) * (dec(state["avg_entry"]) - fill.fill_price))
            state["quantity"] = 0
            state["avg_entry"] = None
        else:
            raise BacktestRunError("BT012_FILL_SIDE_UNSUPPORTED", fill.side)
        if cost:
            cash = money(cash - cost)
            cash_ledger.append(_cash_entry(fill, "COST", -cost, cash))
        state["costs"] = money(state["costs"] + cost)
        return cash

    def _build_trades(self, request: PortfolioRunRequest, fills: tuple[FillRecord, ...], costs: tuple[CostBreakdownV0, ...], order_session: Mapping[str, date]) -> tuple[TradeRecord, ...]:
        costs_by_fill = {b.fill_id: b.total_cost for b in costs if b.fill_id is not None}
        grouped: dict[tuple[date, str], list[FillRecord]] = {}
        for fill in fills:
            grouped.setdefault((order_session[fill.order_id], fill.ticker), []).append(fill)
        trades = []
        for session in sorted(request.session_dates):
            for symbol in request.strategy_spec.symbols:
                symbol_fills = sorted(grouped.get((session, symbol), ()), key=lambda x: (x.execution_timestamp, x.fill_id))
                if len(symbol_fills) != 2:
                    raise BacktestRunError("BT012_TRADE_FILL_COUNT_INVALID", f"{session}:{symbol}:{len(symbol_fills)}")
                entry, exit_fill = symbol_fills
                if entry.side != SELL_SHORT or exit_fill.side != BUY_TO_COVER:
                    raise BacktestRunError("BT012_TRADE_FILL_SEQUENCE_UNSUPPORTED", f"{session}:{symbol}")
                gross = money(dec(entry.fill_quantity) * (entry.fill_price - exit_fill.fill_price))
                total_costs = money(dec(costs_by_fill.get(entry.fill_id, Decimal("0.00"))) + dec(costs_by_fill.get(exit_fill.fill_id, Decimal("0.00"))))
                trades.append(TradeRecord(f"trade-{session.isoformat()}-{symbol}-{entry.fill_id}-{exit_fill.fill_id}", symbol, entry.fill_quantity, entry.order_id, exit_fill.order_id, entry.fill_id, exit_fill.fill_id, entry.execution_timestamp, exit_fill.execution_timestamp, entry.fill_recorded_at, exit_fill.fill_recorded_at, entry.fill_price, exit_fill.fill_price, gross, total_costs, money(gross - total_costs), FILLED))
        return tuple(trades)

    def _final_positions(self, request: PortfolioRunRequest, fills: tuple[FillRecord, ...], costs: tuple[CostBreakdownV0, ...], trades: tuple[TradeRecord, ...], last_marks: Mapping[str, Decimal | None]) -> tuple[PositionSnapshot, ...]:
        costs_by_fill = {b.fill_id: b.total_cost for b in costs if b.fill_id is not None}
        qty = {s: 0 for s in request.strategy_spec.symbols}
        costs_by_symbol = {s: Decimal("0.00") for s in request.strategy_spec.symbols}
        gross_by_symbol = {s: Decimal("0.00") for s in request.strategy_spec.symbols}
        for fill in fills:
            costs_by_symbol[fill.ticker] = money(costs_by_symbol[fill.ticker] + dec(costs_by_fill.get(fill.fill_id, Decimal("0.00"))))
            qty[fill.ticker] += -fill.fill_quantity if fill.side == SELL_SHORT else fill.fill_quantity
        for trade in trades:
            gross_by_symbol[trade.ticker] = money(gross_by_symbol[trade.ticker] + trade.gross_pnl)
        return tuple(PositionSnapshot(s, qty[s], None if qty[s] == 0 else last_marks.get(s), money(gross_by_symbol[s]), money(gross_by_symbol[s] - costs_by_symbol[s]), money(costs_by_symbol[s]), last_marks.get(s)) for s in request.strategy_spec.symbols)

    def _session_results(self, request: PortfolioRunRequest, trades: tuple[TradeRecord, ...], session_cash: Mapping[date, Decimal], positions: tuple[PositionSnapshot, ...]) -> tuple[PortfolioSessionResult, ...]:
        rows = []
        for session in sorted(request.session_dates):
            session_trades = [trade for trade in trades if f"trade-{session.isoformat()}-" in trade.trade_id]
            gross = money(sum((trade.gross_pnl for trade in session_trades), Decimal("0.00")))
            costs = money(sum((trade.total_costs for trade in session_trades), Decimal("0.00")))
            net = money(sum((trade.net_pnl for trade in session_trades), Decimal("0.00")))
            rows.append(PortfolioSessionResult(session, len(session_trades) * 2, len(session_trades) * 2, len(session_trades), gross, costs, net, money(session_cash[session]), all(p.quantity == 0 for p in positions)))
        return tuple(rows)

    def _metrics(self, starting_equity: Decimal, trades: tuple[TradeRecord, ...], equity_curve: tuple[EquityCurvePoint, ...]) -> MetricsSummary:
        gross_profit = money(sum((t.gross_pnl for t in trades if t.gross_pnl > 0), Decimal("0.00")))
        gross_loss = money(sum((t.gross_pnl for t in trades if t.gross_pnl < 0), Decimal("0.00")))
        gross_pnl = money(sum((t.gross_pnl for t in trades), Decimal("0.00")))
        total_costs = money(sum((t.total_costs for t in trades), Decimal("0.00")))
        net_pnl = money(sum((t.net_pnl for t in trades), Decimal("0.00")))
        peak = None
        max_drawdown = Decimal("0.00")
        for point in equity_curve:
            peak = point.equity if peak is None or point.equity > peak else peak
            max_drawdown = max(max_drawdown, money(peak - point.equity))
        profit_factor = None if gross_loss == 0 else money(gross_profit / abs(gross_loss))
        return MetricsSummary(len(trades), sum(t.net_pnl > 0 for t in trades), sum(t.net_pnl < 0 for t in trades), sum(t.net_pnl == 0 for t in trades), gross_profit, gross_loss, gross_pnl, total_costs, net_pnl, money(starting_equity), money(starting_equity + net_pnl), money((net_pnl / starting_equity) * Decimal("100")), max_drawdown, profit_factor, False, False)

    def _validation_status(self, request: PortfolioRunRequest, events: tuple[ReplayEvent, ...], order_results: tuple[OrderSimulationResult, ...], fills: tuple[FillRecord, ...], positions: tuple[PositionSnapshot, ...], session_results: tuple[PortfolioSessionResult, ...], metrics: MetricsSummary, loop: Mapping[str, Any]) -> str:
        expected = len(request.session_dates) * len(request.strategy_spec.symbols) * 2
        if len(order_results) != expected or len(fills) != expected or len(loop["event_loop_trace"]) != len(events):
            return "FAIL"
        if any(r.terminal_order_outcome != FILLED for r in order_results) or any(p.quantity != 0 for p in positions):
            return "FAIL"
        if metrics.ending_equity != money(metrics.starting_equity + metrics.net_pnl):
            return "FAIL"
        if money(sum((row.net_pnl for row in session_results), Decimal("0.00"))) != metrics.net_pnl:
            return "FAIL"
        for trace in loop["event_loop_trace"]:
            if trace.order_id is not None:
                if not trace.order_registered_before_replay_started or not trace.order_registered_before_replay_event:
                    return "FAIL"
                if trace.simulator_event_count != 1 or trace.max_replay_event_index_visible_to_simulator != trace.replay_event_index:
                    return "FAIL"
                if trace.accounting_applied_at_replay_event_index != trace.replay_event_index:
                    return "FAIL"
            if trace.replay_event_type == "GAP" and (trace.replay_gap_supplied_execution_price or trace.replay_gap_triggered_fill):
                return "FAIL"
        return "PASS"

    def _manifest(self, request: PortfolioRunRequest, reports: tuple[Mapping[str, Any], ...], replay_summaries: tuple[ReplayRunSummary, ...], calendar_payload: Mapping[str, Any], summary: PortfolioRunSummary, output_artifacts: Mapping[str, str]) -> PortfolioRunManifest:
        return PortfolioRunManifest(
            "bt_portfolio_run_manifest_v0_1", request.run_id, BT_GATE_012, MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE,
            request.fixture_id, request.strategy_spec.strategy_id, request.strategy_spec.strategy_spec_version,
            {"preflight_report_paths": tuple(p.as_posix() for p in request.preflight_report_paths), "preflight_report_sha256": tuple(sha256_file(p) for p in request.preflight_report_paths), "replay_event_sequence_sha256": tuple(s.replay_event_sequence_sha256 for s in replay_summaries), "source_hashes": tuple(r.get("snapshot_or_content_hashes", {}) for r in reports)},
            request.strategy_spec.symbols, tuple(s.isoformat() for s in request.session_dates), request.starting_equity,
            {"quantity_per_symbol_session": request.strategy_spec.quantity_per_symbol, "order_sizing_depends_on_portfolio_cash": False},
            GLOBAL_REPLAY_ORDER_V0_1, ACTIVE_ORDER_EVALUATION_ORDER_V0_1, PORTFOLIO_EQUITY_POLICY_V0_1, REGULAR_ONLY_XNYS_V0_1,
            TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1, request.session_calendar_snapshot_sha256,
            self.simulator.run_manifest().to_dict(), self.cost_model.to_dict(), self.slippage_model.to_dict(),
            {"short_sale_proceeds_accounting": "BT_GATE_011_INHERITED", "portfolio_valuation_price_field": "close"},
            {"RUN_PURPOSE": request.run_purpose, "EDGE_EVIDENCE": request.edge_evidence, "ECONOMIC_REALISM": request.economic_realism, "STRATEGY_OPTIMIZATION": request.strategy_optimization, "CAPITAL_CONTENTION_CLAIM": "NOT_AUTHORIZED"},
            output_artifacts, summary.validation_status, "PASS" if summary.validation_status == "PASS" else "FAIL",
            {"StateReplayFeed": "NOT_AUTHORIZED", "state_bundle_physical_read": "NOT_AUTHORIZED", "Market State consumption": "NOT_AUTHORIZED", "Event State consumption": "NOT_AUTHORIZED", "provider modification": "NOT_AUTHORIZED"},
        )

    def _validation_report(self, result: PortfolioRunResult) -> dict[str, Any]:
        traces = result.event_loop_trace
        return {
            "status": result.summary.validation_status,
            "gate_id": BT_GATE_012,
            "capability": MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE,
            "run_id": result.request.run_id,
            "fixture_acceptance_profile": {"sessions": len(result.request.session_dates), "symbols": len(result.request.strategy_spec.symbols), "symbol_sessions": len(result.request.session_dates) * len(result.request.strategy_spec.symbols), "ReplayGapEvent_presence": result.summary.replay_gap_count > 0, "same_timestamp_cross_symbol_events": True, "contractual_open_close_coverage": True},
            "global_replay_order_policy": GLOBAL_REPLAY_ORDER_V0_1,
            "active_order_evaluation_order_policy": ACTIVE_ORDER_EVALUATION_ORDER_V0_1,
            "portfolio_equity_policy": PORTFOLIO_EQUITY_POLICY_V0_1,
            "portfolio_valuation_price_field": "close",
            "orders_pre_registered_before_replay": all(t.order_id is None or t.order_registered_before_replay_started for t in traces),
            "order_created_during_event_processing": False,
            "simulator_called_with_single_current_event_only": all(t.order_id is None or t.simulator_event_count == 1 for t in traces),
            "accounting_applied_inside_event_loop": all(t.order_id is None or t.accounting_applied_at_replay_event_index == t.replay_event_index for t in traces),
            "replay_gap_supplied_execution_price": any(t.replay_gap_supplied_execution_price for t in traces),
            "replay_gap_triggered_fill": any(t.replay_gap_triggered_fill for t in traces),
            "final_positions_zero": result.summary.final_position_all_zero,
            "ending_equity_reconciles": result.metrics.ending_equity == money(result.metrics.starting_equity + result.metrics.net_pnl),
            "session_results_sum_to_portfolio": money(sum((row.net_pnl for row in result.session_results), Decimal("0.00"))) == result.metrics.net_pnl,
            "run_classifications": {"RUN_PURPOSE": result.request.run_purpose, "EDGE_EVIDENCE": result.request.edge_evidence, "ECONOMIC_REALISM": result.request.economic_realism, "STRATEGY_OPTIMIZATION": result.request.strategy_optimization, "CAPITAL_CONTENTION_CLAIM": "NOT_AUTHORIZED"},
            "state_provider_restrictions_preserved": True,
            "deterministic_output_hash": result.summary.deterministic_output_hash,
        }
    def _global_order_key(self, event: ReplayEvent) -> tuple[datetime, date, int, str, str]:
        return (event.available_at, self._event_session_date(event), 0 if isinstance(event, ReplayGapEvent) else 1, str(event.ticker).upper(), self._source_event_identity(event))

    @staticmethod
    def _source_event_identity(event: ReplayEvent) -> str:
        if isinstance(event, ReplayBarEvent):
            return f"{event.ticker}:{event.bar.ts_start.isoformat()}:{event.bar.ts_end.isoformat()}:BAR"
        if isinstance(event, ReplayGapEvent):
            return f"{event.ticker}:{event.ts_start.isoformat()}:{event.ts_end.isoformat()}:GAP"
        raise BacktestRunError("BT012_REPLAY_EVENT_UNSUPPORTED", str(type(event)))

    @staticmethod
    def _event_ts_start(event: ReplayEvent) -> datetime:
        return event.bar.ts_start if isinstance(event, ReplayBarEvent) else event.ts_start

    @staticmethod
    def _event_session_date(event: ReplayEvent) -> date:
        label = event.bar.session_label if isinstance(event, ReplayBarEvent) else event.session_label
        try:
            return date.fromisoformat(str(label).split(":", 1)[0])
        except ValueError as exc:
            raise BacktestRunError("BT012_SESSION_LABEL_INVALID", str(label)) from exc

    @staticmethod
    def _assert_flat_positions(positions: Mapping[str, Mapping[str, Any]], code: str) -> None:
        residual = {symbol: state["quantity"] for symbol, state in positions.items() if int(state["quantity"]) != 0}
        if residual:
            raise BacktestRunError(code, str(residual))

    def _equity_point(self, sequence: int, timestamp: datetime, cash: Decimal, positions: Mapping[str, Mapping[str, Any]], reason: str) -> EquityCurvePoint:
        market_value = Decimal("0.00")
        for symbol, state in positions.items():
            quantity = int(state["quantity"])
            if quantity == 0:
                continue
            mark = state["last_mark"]
            if mark is None:
                raise BacktestRunError("BT012_OPEN_POSITION_WITHOUT_LEGAL_VALUATION", symbol)
            market_value += dec(quantity) * dec(mark)
        market_value = money(market_value)
        return EquityCurvePoint(sequence, timestamp, money(cash), market_value, money(cash + market_value), reason)

    @staticmethod
    def _equity_reason(event: ReplayEvent, fill: FillRecord | None) -> str:
        if fill is not None:
            return f"FILL_APPLIED:{fill.fill_id}"
        if isinstance(event, ReplayGapEvent):
            return "REPLAY_GAP_EVENT_NO_VALUATION_UPDATE"
        return "REPLAY_BAR_EVENT_VALUATION_UPDATE"


def _cash_entry(fill: FillRecord, entry_type: str, amount: Decimal, cash_after: Decimal) -> CashLedgerEntryV0:
    return CashLedgerEntryV0(f"cash-{fill.fill_id}-{entry_type}", fill.ticker, fill.fill_id, fill.order_id, entry_type, money(amount), money(cash_after), fill.fill_recorded_at, entry_type.lower().replace("_", " "))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(to_jsonable(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _parse_utc(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise BacktestRunError("BT012_TIMESTAMP_NOT_UTC", str(value))
    return parsed.astimezone(timezone.utc)


def _write_readme(run_dir: Path, result: PortfolioRunResult) -> None:
    text = f"""# BT-GATE-012 Portfolio Slice Run

run_id: {result.request.run_id}
status: {result.summary.validation_status}
purpose: ENGINE_VALIDATION_RUN
edge: NOT_AUTHORIZED
economic_realism: INCOMPLETE
capital_contention: NOT_AUTHORIZED
event_loop_mode: {result.summary.event_loop_mode}

This run validates the multi-symbol, multi-session portfolio engine path only.
It is not evidence of edge and does not claim small-caps execution realism.
"""
    (run_dir / "README.md").write_text(text, encoding="utf-8")
