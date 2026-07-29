"""Deterministic fill simulator V0.1."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal

from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayEvent, ReplayGapEvent

from .contracts import (
    BAR_BASED_EXECUTION_PROFILE_V0_1,
    BPS_OF_PRICE_ADVERSE,
    BUY,
    BUY_TO_COVER,
    COMMISSION,
    COST_CATEGORIES,
    DAY,
    EXPIRED_UNFILLED,
    FAIL_AMBIGUOUS_BAR,
    FAIL_AMBIGUOUS_BAR_ONLY,
    FILLED,
    FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE,
    FULL_FILL,
    FULL_FILL_ONLY,
    LIMIT,
    LOCATE_FEE,
    MARKET_PROXY,
    NO_FILL_GAP,
    NO_FILL_MISSING_PRICE,
    NO_FILL_NOT_ELIGIBLE,
    OTHER_FEE,
    PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION,
    PESSIMISTIC,
    REGULATORY_FEE,
    REJECTED_BY_CONTRACT,
    ROUTING_OR_ECN_FEE,
    SELL,
    SELL_SHORT,
    SIDES,
    STOP_MARKET_PROXY,
    SUPPORTED_ORDER_TYPES,
    SUPPORTED_SLIPPAGE_UNITS,
    ZERO_SLIPPAGE,
    BORROW_FEE,
    CostBreakdownV0,
    CostComponentV0,
    CostModelV0,
    EvaluationResult,
    ExecutionOrder,
    ExecutionPolicy,
    ExecutionSimulationError,
    FillRecord,
    OrderSimulationResult,
    SimulationRunManifest,
    SlippageModel,
    dec,
    money,
)


class DeterministicFillSimulator:
    def __init__(
        self,
        execution_policy: ExecutionPolicy | None = None,
        slippage_model: SlippageModel | None = None,
        cost_model: CostModelV0 | None = None,
    ) -> None:
        self.execution_policy = execution_policy or ExecutionPolicy()
        self.slippage_model = slippage_model or SlippageModel("zero_slippage_v0_1")
        self.cost_model = cost_model or CostModelV0("zero_cost_v0_1")
        self._validate_static_configuration()

    def evaluate_order(self, order: ExecutionOrder, events: tuple[ReplayEvent, ...] | list[ReplayEvent]) -> EvaluationResult:
        """Return the terminal evaluation for callers that do not need full trace."""
        return self.simulate_order(order, events).evaluations[-1]

    def simulate_order(self, order: ExecutionOrder, events: tuple[ReplayEvent, ...] | list[ReplayEvent]) -> OrderSimulationResult:
        config_reject = self._contract_rejection(order)
        if config_reject is not None:
            rejected = self._result(order, REJECTED_BY_CONTRACT, REJECTED_BY_CONTRACT, config_reject, config_reject)
            return OrderSimulationResult(order.order_id, order.ticker, (rejected,), REJECTED_BY_CONTRACT)

        evaluations: list[EvaluationResult] = []
        for event in sorted(events, key=self._event_key):
            if getattr(event, "ticker", None) != order.ticker:
                continue
            result = self._evaluate_event(order, event)
            evaluations.append(result)
            if result.evaluation_outcome == FULL_FILL:
                return OrderSimulationResult(order.order_id, order.ticker, tuple(evaluations), FILLED, result.fill, result.cost_breakdown)
            if result.evaluation_outcome in {REJECTED_BY_CONTRACT, FAIL_AMBIGUOUS_BAR}:
                terminal = self._with_terminal(result, REJECTED_BY_CONTRACT)
                evaluations[-1] = terminal
                return OrderSimulationResult(order.order_id, order.ticker, tuple(evaluations), REJECTED_BY_CONTRACT)
        if evaluations:
            terminal = self._with_terminal(evaluations[-1], EXPIRED_UNFILLED)
            evaluations[-1] = terminal
            return OrderSimulationResult(order.order_id, order.ticker, tuple(evaluations), EXPIRED_UNFILLED)
        missing = self._result(order, NO_FILL_MISSING_PRICE, EXPIRED_UNFILLED, "NO_EVENTS_FOR_TICKER", "no source events for order ticker")
        return OrderSimulationResult(order.order_id, order.ticker, (missing,), EXPIRED_UNFILLED)

    def run_manifest(self) -> SimulationRunManifest:
        return SimulationRunManifest(
            execution_profile_id=self.execution_policy.execution_profile_id,
            execution_profile_version=self.execution_policy.execution_profile_version,
            fill_model_id=self.execution_policy.fill_model_id,
            fill_model_version=self.execution_policy.fill_model_version,
            slippage_model_id=self.slippage_model.slippage_model_id,
            slippage_model_version=self.slippage_model.slippage_model_version,
            slippage_unit=self.slippage_model.slippage_unit,
            slippage_value=self.slippage_model.slippage_value,
            cost_model_id=self.cost_model.cost_model_id,
            cost_model_version=self.cost_model.cost_model_version,
            rounding_policy_id=self.cost_model.rounding_policy_id,
            tick_size_policy_id=self.execution_policy.tick_size_policy_id,
            missing_execution_price_policy="NO_FILL_MISSING_PRICE_OR_NO_FILL_GAP",
            ambiguous_bar_policy=self.execution_policy.ambiguous_bar_policy,
            terminal_order_outcome_policy_id=self.execution_policy.terminal_order_outcome_policy_id,
            short_execution_mechanics_state=self.execution_policy.short_execution_mechanics_state,
            short_tradability_state=self.execution_policy.short_tradability_state,
            broker_cost_realism_claimed=self.execution_policy.broker_cost_realism_claimed,
            fill_realism_claimed=self.execution_policy.fill_realism_claimed,
            edge_evaluated=self.execution_policy.edge_evaluated,
        )

    def deterministic_hash(self, payload: object) -> str:
        encoded = json.dumps(self._to_plain(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _evaluate_event(self, order: ExecutionOrder, event: ReplayEvent) -> EvaluationResult:
        if isinstance(event, ReplayGapEvent):
            if event.ts_start < order.order_submission_timestamp:
                return self._result(order, NO_FILL_NOT_ELIGIBLE, None, "SOURCE_BAR_BEFORE_ORDER_ACTIVE", "gap interval starts before order submission", event)
            return self._result(order, NO_FILL_GAP, None, "REPLAY_GAP_EVENT", "selected source interval is ReplayGapEvent", event)
        if not isinstance(event, ReplayBarEvent):
            return self._result(order, REJECTED_BY_CONTRACT, REJECTED_BY_CONTRACT, "EVENT_TYPE_UNSUPPORTED", "unsupported replay event type")
        bar = event.bar
        if bar.ts_start < order.order_submission_timestamp:
            return self._result(order, NO_FILL_NOT_ELIGIBLE, None, "SOURCE_BAR_BEFORE_ORDER_ACTIVE", "source bar starts before order submission", event)
        missing_reason = self._missing_price_reason(order, bar)
        if missing_reason is not None:
            return self._result(order, NO_FILL_MISSING_PRICE, None, missing_reason, "required source price is absent, nonpositive or nonfinite", event)
        if self._is_ambiguous(order, bar):
            return self._result(order, FAIL_AMBIGUOUS_BAR, REJECTED_BY_CONTRACT, "AMBIGUOUS_INTRABAR_SEQUENCE", "ambiguous intrabar sequence under V0.1", event)
        base_price = self._base_price(order, bar)
        if base_price is None:
            return self._result(order, NO_FILL_NOT_ELIGIBLE, None, "ORDER_TRIGGER_NOT_REACHED", "limit or stop trigger is not reached", event)
        fill_price_before_slippage = base_price
        slippage_amount = self._slippage_amount(base_price)
        fill_price = self._apply_slippage(order.side, order.order_type, base_price, slippage_amount)
        if fill_price <= Decimal("0"):
            return self._result(order, REJECTED_BY_CONTRACT, REJECTED_BY_CONTRACT, "FILL_PRICE_NONPOSITIVE", "computed fill_price <= 0", event)
        gross_notional = abs(dec(order.quantity)) * fill_price
        fill_id = f"fill-{order.order_id}-{self._bar_id(bar)}"
        cost_breakdown_id = f"cost-{fill_id}"
        cost_breakdown = self._cost_breakdown(order, fill_id, gross_notional)
        fill = FillRecord(
            fill_id=fill_id,
            order_id=order.order_id,
            ticker=order.ticker,
            side=order.side,
            fill_quantity=order.quantity,
            execution_timestamp=bar.ts_end if order.order_type == MARKET_PROXY and order.market_price_field == "close" else bar.ts_start,
            fill_recorded_at=bar.available_at,
            execution_price_before_slippage=fill_price_before_slippage,
            slippage_amount=slippage_amount,
            fill_price=fill_price,
            gross_notional=gross_notional,
            source_price_profile=self.execution_policy.execution_profile_id,
            source_bar_id=self._bar_id(bar),
            source_bar_available_at=bar.available_at,
            cost_breakdown_id=cost_breakdown_id,
        )
        return self._result(order, FULL_FILL, FILLED, "FULL_FILL", "order filled by deterministic V0.1 simulator", event, fill, cost_breakdown)

    def _contract_rejection(self, order: ExecutionOrder) -> str | None:
        if order.side not in SIDES:
            return "SIDE_UNSUPPORTED"
        if order.quantity <= 0:
            return "QUANTITY_NOT_POSITIVE"
        if order.order_type not in SUPPORTED_ORDER_TYPES:
            return "ORDER_TYPE_UNSUPPORTED"
        if order.time_in_force != DAY:
            return "TIME_IN_FORCE_UNSUPPORTED"
        if order.fill_capability != FULL_FILL_ONLY:
            return "PARTIAL_FILL_RESERVED_NOT_IMPLEMENTED"
        if order.execution_profile_id != BAR_BASED_EXECUTION_PROFILE_V0_1:
            return "EXECUTION_PROFILE_UNAUTHORIZED"
        if order.order_type == LIMIT and order.limit_price is None:
            return "LIMIT_PRICE_REQUIRED"
        if order.order_type == STOP_MARKET_PROXY and order.stop_price is None:
            return "STOP_PRICE_REQUIRED"
        if order.order_type == MARKET_PROXY and (order.limit_price is not None or order.stop_price is not None):
            return "MARKET_PROXY_PRICE_FIELDS_UNSUPPORTED"
        if order.order_type == MARKET_PROXY and order.market_price_field not in {"open", "close"}:
            return "MARKET_PROXY_PRICE_FIELD_UNSUPPORTED"
        if self.cost_model.borrow_fee_per_order and not self.cost_model.authorized_borrow_model:
            return "BORROW_MODEL_NOT_AUTHORIZED"
        return None

    def _validate_static_configuration(self) -> None:
        policy = self.execution_policy
        if policy.execution_profile_id != BAR_BASED_EXECUTION_PROFILE_V0_1:
            raise ExecutionSimulationError("EXECUTION_PROFILE_UNAUTHORIZED", "only bar_based_execution_profile_v0_1 is authorized")
        if policy.tick_size_policy_id != PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION:
            raise ExecutionSimulationError("FAIL_CLOSED_WHEN_TICK_POLICY_REQUIRED", "unsupported tick policy")
        if policy.ambiguous_bar_policy == PESSIMISTIC:
            raise ExecutionSimulationError("PESSIMISTIC_RESERVED_NOT_IMPLEMENTED", "PESSIMISTIC ambiguous-bar policy is reserved")
        if policy.ambiguous_bar_policy != FAIL_AMBIGUOUS_BAR_ONLY:
            raise ExecutionSimulationError("AMBIGUOUS_BAR_POLICY_UNSUPPORTED", "only FAIL_AMBIGUOUS_BAR_ONLY is authorized")
        if self.slippage_model.slippage_unit not in SUPPORTED_SLIPPAGE_UNITS:
            raise ExecutionSimulationError("SLIPPAGE_MODEL_UNSUPPORTED", "unsupported slippage model")
        if self.slippage_model.slippage_value < 0:
            raise ExecutionSimulationError("SLIPPAGE_VALUE_NEGATIVE", "slippage value must be nonnegative")
        if self.cost_model.rounding_policy_id != "ROUND_HALF_EVEN_CENTS":
            raise ExecutionSimulationError("ROUNDING_POLICY_UNSUPPORTED", "only ROUND_HALF_EVEN_CENTS is authorized")
        if self.cost_model.regulatory_fee_per_share and self.cost_model.regulatory_fee_bps:
            raise ExecutionSimulationError("REGULATORY_FEE_MODE_CONFLICT", "only one regulatory fee mode may be active")
        for field in (
            self.cost_model.commission_per_share,
            self.cost_model.minimum_commission_per_order,
            self.cost_model.fixed_fee_per_order,
            self.cost_model.routing_or_ecn_fee_per_share,
            self.cost_model.regulatory_fee_per_share,
            self.cost_model.regulatory_fee_bps,
            self.cost_model.locate_fee_per_share,
            self.cost_model.borrow_fee_per_order,
            self.cost_model.other_fixed_fee_per_filled_order,
        ):
            if field < 0:
                raise ExecutionSimulationError("COST_FIELD_NEGATIVE", "cost fields must be nonnegative")

    def _base_price(self, order: ExecutionOrder, bar: MarketDataBar1m) -> Decimal | None:
        if order.order_type == MARKET_PROXY:
            return dec(bar.close) if order.market_price_field == "close" else dec(bar.open)
        if order.order_type == LIMIT:
            limit = dec(order.limit_price)
            if order.side in {BUY, BUY_TO_COVER} and dec(bar.low) <= limit:
                return limit
            if order.side in {SELL, SELL_SHORT} and dec(bar.high) >= limit:
                return limit
            return None
        stop = dec(order.stop_price)
        if order.side in {BUY, BUY_TO_COVER}:
            if dec(bar.high) < stop:
                return None
            return max(stop, dec(bar.open))
        if dec(bar.low) > stop:
            return None
        return min(stop, dec(bar.open))

    def _is_ambiguous(self, order: ExecutionOrder, bar: MarketDataBar1m) -> bool:
        if order.order_type == LIMIT and order.stop_price is not None:
            limit = dec(order.limit_price)
            stop = dec(order.stop_price)
            if order.side in {BUY, BUY_TO_COVER}:
                return dec(bar.low) <= limit and dec(bar.high) >= stop
            return dec(bar.high) >= limit and dec(bar.low) <= stop
        if order.order_type == STOP_MARKET_PROXY and order.limit_price is not None:
            limit = dec(order.limit_price)
            stop = dec(order.stop_price)
            if order.side in {BUY, BUY_TO_COVER}:
                return dec(bar.high) >= stop and dec(bar.low) <= limit
            return dec(bar.low) <= stop and dec(bar.high) >= limit
        return False

    def _missing_price_reason(self, order: ExecutionOrder, bar: MarketDataBar1m) -> str | None:
        required = [bar.open]
        if order.order_type == MARKET_PROXY:
            required.append(bar.close if order.market_price_field == "close" else bar.open)
        elif order.order_type == LIMIT:
            required.extend([bar.high, bar.low])
        elif order.order_type == STOP_MARKET_PROXY:
            required.extend([bar.open, bar.high, bar.low])
        for value in required:
            price = dec(value)
            if not price.is_finite() or price <= 0:
                return "REQUIRED_PRICE_INVALID"
        return None

    def _slippage_amount(self, base_price: Decimal) -> Decimal:
        unit = self.slippage_model.slippage_unit
        value = self.slippage_model.slippage_value
        if unit == ZERO_SLIPPAGE:
            return Decimal("0")
        if unit == FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE:
            return value
        if unit == BPS_OF_PRICE_ADVERSE:
            return base_price * value / Decimal("10000")
        raise ExecutionSimulationError("SLIPPAGE_MODEL_UNSUPPORTED", unit)

    @staticmethod
    def _apply_slippage(side: str, order_type: str, base_price: Decimal, slippage_amount: Decimal) -> Decimal:
        if order_type == LIMIT:
            return base_price
        if side in {BUY, BUY_TO_COVER}:
            return base_price + slippage_amount
        return base_price - slippage_amount

    def _cost_breakdown(self, order: ExecutionOrder, fill_id: str, gross_notional: Decimal) -> CostBreakdownV0:
        model = self.cost_model
        quantity = abs(dec(order.quantity))
        raw_commission = quantity * model.commission_per_share
        commission = max(raw_commission, model.minimum_commission_per_order)
        routing = quantity * model.routing_or_ecn_fee_per_share
        regulatory = Decimal("0")
        if order.side in {SELL, SELL_SHORT}:
            regulatory = quantity * model.regulatory_fee_per_share if model.regulatory_fee_per_share else gross_notional * model.regulatory_fee_bps / Decimal("10000")
        locate = quantity * model.locate_fee_per_share if order.side == SELL_SHORT else Decimal("0")
        borrow = model.borrow_fee_per_order if model.authorized_borrow_model else Decimal("0")
        other = model.fixed_fee_per_order + model.other_fixed_fee_per_filled_order
        components = (
            self._component(COMMISSION, commission, "max(abs(fill_quantity) * commission_per_share, minimum_commission_per_order)"),
            self._component(ROUTING_OR_ECN_FEE, routing, "abs(fill_quantity) * routing_or_ecn_fee_per_share"),
            self._component(REGULATORY_FEE, regulatory, "sell-side regulatory fee per-share or notional bps"),
            self._component(LOCATE_FEE, locate, "SELL_SHORT locate_fee_per_share, otherwise zero"),
            self._component(BORROW_FEE, borrow, "ZERO_ONLY unless authorized borrow model"),
            self._component(OTHER_FEE, other, "fixed_fee_per_order + other_fixed_fee_per_filled_order"),
        )
        if tuple(component.category for component in components) != COST_CATEGORIES:
            raise ExecutionSimulationError("COST_COMPONENTS_INCOMPLETE", "cost components must match canonical categories")
        total = sum((component.rounded_amount for component in components), Decimal("0.00"))
        return CostBreakdownV0(f"cost-{fill_id}", order.order_id, fill_id, components, money(total), model.currency)

    def _component(self, category: str, raw: Decimal, formula: str) -> CostComponentV0:
        return CostComponentV0(category, raw, money(raw), self.cost_model.currency, formula)

    def _result(
        self,
        order: ExecutionOrder,
        evaluation_outcome: str,
        terminal_order_outcome: str | None,
        reason_code: str,
        reason: str,
        event: ReplayEvent | None = None,
        fill: FillRecord | None = None,
        cost_breakdown: CostBreakdownV0 | None = None,
    ) -> EvaluationResult:
        bar = event.bar if isinstance(event, ReplayBarEvent) else None
        gap = event if isinstance(event, ReplayGapEvent) else None
        return EvaluationResult(
            order_id=order.order_id,
            ticker=order.ticker,
            evaluation_outcome=evaluation_outcome,
            terminal_order_outcome=terminal_order_outcome,
            reason_code=reason_code,
            reason=reason,
            source_event_type=getattr(event, "event_type", None),
            source_bar_id=self._bar_id(bar) if bar else (self._gap_id(gap) if gap else None),
            source_bar_ts_start=bar.ts_start if bar else (gap.ts_start if gap else None),
            source_bar_ts_end=bar.ts_end if bar else (gap.ts_end if gap else None),
            source_bar_available_at=bar.available_at if bar else (gap.available_at if gap else None),
            fill=fill,
            cost_breakdown=cost_breakdown,
        )

    @staticmethod
    def _with_terminal(result: EvaluationResult, terminal: str) -> EvaluationResult:
        return EvaluationResult(
            result.order_id,
            result.ticker,
            result.evaluation_outcome,
            terminal,
            result.reason_code,
            result.reason,
            result.source_event_type,
            result.source_bar_id,
            result.source_bar_ts_start,
            result.source_bar_ts_end,
            result.source_bar_available_at,
            result.fill,
            result.cost_breakdown,
        )

    @staticmethod
    def _event_key(event: ReplayEvent) -> tuple:
        if isinstance(event, ReplayGapEvent):
            return (event.available_at, 0, event.ticker)
        return (event.available_at, 1, event.ticker)

    @staticmethod
    def _bar_id(bar: MarketDataBar1m) -> str:
        return f"{bar.ticker}:{bar.ts_start.isoformat()}:{bar.ts_end.isoformat()}"

    @staticmethod
    def _gap_id(gap: ReplayGapEvent | None) -> str | None:
        if gap is None:
            return None
        return f"{gap.ticker}:{gap.ts_start.isoformat()}:{gap.ts_end.isoformat()}:GAP"

    @staticmethod
    def _to_plain(value: object) -> object:
        if hasattr(value, "to_dict"):
            return value.to_dict()
        if isinstance(value, dict):
            return {str(k): DeterministicFillSimulator._to_plain(v) for k, v in value.items()}
        if isinstance(value, (tuple, list)):
            return [DeterministicFillSimulator._to_plain(v) for v in value]
        return value
