"""Contracts for deterministic fill simulation V0.1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

from tsis_backtest.preflight.contracts import to_jsonable


BUY = "BUY"
SELL = "SELL"
SELL_SHORT = "SELL_SHORT"
BUY_TO_COVER = "BUY_TO_COVER"
SIDES = (BUY, SELL, SELL_SHORT, BUY_TO_COVER)

MARKET_PROXY = "MARKET_PROXY"
LIMIT = "LIMIT"
STOP_MARKET_PROXY = "STOP_MARKET_PROXY"
SUPPORTED_ORDER_TYPES = (MARKET_PROXY, LIMIT, STOP_MARKET_PROXY)

DAY = "DAY"
FULL_FILL_ONLY = "FULL_FILL_ONLY"
BAR_BASED_EXECUTION_PROFILE_V0_1 = "bar_based_execution_profile_v0_1"
PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION = "PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION"
FAIL_AMBIGUOUS_BAR_ONLY = "FAIL_AMBIGUOUS_BAR_ONLY"
PESSIMISTIC = "PESSIMISTIC"

FULL_FILL = "FULL_FILL"
NO_FILL_NOT_ELIGIBLE = "NO_FILL_NOT_ELIGIBLE"
NO_FILL_MISSING_PRICE = "NO_FILL_MISSING_PRICE"
NO_FILL_GAP = "NO_FILL_GAP"
FAIL_AMBIGUOUS_BAR = "FAIL_AMBIGUOUS_BAR"
REJECTED_BY_CONTRACT = "REJECTED_BY_CONTRACT"
SUPPORTED_EVALUATION_OUTCOMES = (
    FULL_FILL,
    NO_FILL_NOT_ELIGIBLE,
    NO_FILL_MISSING_PRICE,
    NO_FILL_GAP,
    FAIL_AMBIGUOUS_BAR,
    REJECTED_BY_CONTRACT,
)

FILLED = "FILLED"
EXPIRED_UNFILLED = "EXPIRED_UNFILLED"
SUPPORTED_TERMINAL_ORDER_OUTCOMES = (FILLED, EXPIRED_UNFILLED, REJECTED_BY_CONTRACT)

ZERO_SLIPPAGE = "ZERO_SLIPPAGE"
FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE = "FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE"
BPS_OF_PRICE_ADVERSE = "BPS_OF_PRICE_ADVERSE"
SUPPORTED_SLIPPAGE_UNITS = (ZERO_SLIPPAGE, FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, BPS_OF_PRICE_ADVERSE)

COMMISSION = "commission"
ROUTING_OR_ECN_FEE = "routing_or_ecn_fee"
REGULATORY_FEE = "regulatory_fee"
LOCATE_FEE = "locate_fee"
BORROW_FEE = "borrow_fee"
OTHER_FEE = "other_fee"
COST_CATEGORIES = (COMMISSION, ROUTING_OR_ECN_FEE, REGULATORY_FEE, LOCATE_FEE, BORROW_FEE, OTHER_FEE)


class ExecutionSimulationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ExecutionOrder:
    order_id: str
    ticker: str
    side: str
    quantity: int
    order_type: str
    order_submission_timestamp: datetime
    time_in_force: str = DAY
    limit_price: Decimal | None = None
    stop_price: Decimal | None = None
    market_price_field: str = "open"
    execution_profile_id: str = BAR_BASED_EXECUTION_PROFILE_V0_1
    fill_capability: str = FULL_FILL_ONLY

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class SlippageModel:
    slippage_model_id: str
    slippage_model_version: str = "0.1"
    slippage_unit: str = ZERO_SLIPPAGE
    slippage_value: Decimal = Decimal("0")
    side_adjustment_rule: str = "ADVERSE_BY_SIDE"

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class CostModelV0:
    cost_model_id: str
    cost_model_version: str = "0.1"
    commission_per_share: Decimal = Decimal("0")
    minimum_commission_per_order: Decimal = Decimal("0")
    fixed_fee_per_order: Decimal = Decimal("0")
    routing_or_ecn_fee_per_share: Decimal = Decimal("0")
    regulatory_fee_per_share: Decimal = Decimal("0")
    regulatory_fee_bps: Decimal = Decimal("0")
    locate_fee_per_share: Decimal = Decimal("0")
    borrow_fee_policy: str = "ZERO_ONLY"
    borrow_fee_per_order: Decimal = Decimal("0")
    other_fixed_fee_per_filled_order: Decimal = Decimal("0")
    currency: str = "USD"
    rounding_policy_id: str = "ROUND_HALF_EVEN_CENTS"
    authorized_borrow_model: bool = False

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class ExecutionPolicy:
    execution_profile_id: str = BAR_BASED_EXECUTION_PROFILE_V0_1
    execution_profile_version: str = "0.1"
    fill_model_id: str = "DETERMINISTIC_FILL_SIMULATOR_V0_1"
    fill_model_version: str = "0.1"
    tick_size_policy_id: str = PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION
    ambiguous_bar_policy: str = FAIL_AMBIGUOUS_BAR_ONLY
    terminal_order_outcome_policy_id: str = "EVALUATION_OUTCOME_THEN_DAY_TERMINAL_V0_1"
    short_execution_mechanics_state: str = "ALLOWED_FOR_ENGINE_VALIDATION"
    short_tradability_state: str = "NOT_EVALUATED"
    broker_cost_realism_claimed: bool = False
    fill_realism_claimed: bool = False
    edge_evaluated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class CostComponentV0:
    category: str
    raw_amount: Decimal
    rounded_amount: Decimal
    currency: str = "USD"
    formula: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class CostBreakdownV0:
    cost_breakdown_id: str
    order_id: str
    fill_id: str | None
    components: tuple[CostComponentV0, ...]
    total_cost: Decimal
    currency: str = "USD"

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class FillRecord:
    fill_id: str
    order_id: str
    ticker: str
    side: str
    fill_quantity: int
    execution_timestamp: datetime
    fill_recorded_at: datetime
    execution_price_before_slippage: Decimal
    slippage_amount: Decimal
    fill_price: Decimal
    gross_notional: Decimal
    source_price_profile: str
    source_bar_id: str
    source_bar_available_at: datetime
    cost_breakdown_id: str

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class EvaluationResult:
    order_id: str
    ticker: str
    evaluation_outcome: str
    terminal_order_outcome: str | None
    reason_code: str
    reason: str
    source_event_type: str | None = None
    source_bar_id: str | None = None
    source_bar_ts_start: datetime | None = None
    source_bar_ts_end: datetime | None = None
    source_bar_available_at: datetime | None = None
    fill: FillRecord | None = None
    cost_breakdown: CostBreakdownV0 | None = None

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)




@dataclass(frozen=True)
class OrderSimulationResult:
    order_id: str
    ticker: str
    evaluations: tuple[EvaluationResult, ...]
    terminal_order_outcome: str
    fill: FillRecord | None = None
    cost_breakdown: CostBreakdownV0 | None = None

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)

@dataclass(frozen=True)
class SimulationRunManifest:
    execution_profile_id: str
    execution_profile_version: str
    fill_model_id: str
    fill_model_version: str
    slippage_model_id: str
    slippage_model_version: str
    slippage_unit: str
    slippage_value: Decimal
    cost_model_id: str
    cost_model_version: str
    rounding_policy_id: str
    tick_size_policy_id: str
    missing_execution_price_policy: str
    ambiguous_bar_policy: str
    terminal_order_outcome_policy_id: str
    short_execution_mechanics_state: str
    short_tradability_state: str
    broker_cost_realism_claimed: bool
    fill_realism_claimed: bool
    edge_evaluated: bool

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


def dec(value: Any) -> Decimal:
    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def decimal_str(value: Decimal) -> str:
    return format(value, "f")


def _jsonable_decimal(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_str(value)
    if isinstance(value, tuple):
        return [_jsonable_decimal(item) for item in value]
    if isinstance(value, list):
        return [_jsonable_decimal(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable_decimal(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        payload = to_jsonable(value)
        return _jsonable_decimal(payload)
    return value
