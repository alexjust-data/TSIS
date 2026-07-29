"""Contracts for minimum accounting mechanics."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from tsis_backtest.preflight.contracts import to_jsonable


COST_CATEGORIES = (
    "commission",
    "routing_or_ecn_fee",
    "regulatory_fee",
    "locate_fee",
    "borrow_fee",
    "other_fee",
)


@dataclass(frozen=True)
class CostComponent:
    category: str
    amount: Decimal
    currency: str = "USD"
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class CostBreakdown:
    fill_id: str
    order_id: str
    components: tuple[CostComponent, ...]

    @property
    def total_cost(self) -> Decimal:
        return sum((component.amount for component in self.components), Decimal("0.00"))

    def to_dict(self) -> dict[str, Any]:
        payload = _jsonable_decimal(self)
        payload["total_cost"] = _money_str(self.total_cost)
        return payload


@dataclass(frozen=True)
class CostModel:
    model_id: str
    commission_per_share: Decimal = Decimal("0.00")
    minimum_commission_per_order: Decimal = Decimal("0.00")
    entry_fixed_fee: Decimal = Decimal("0.00")
    exit_fixed_fee: Decimal = Decimal("0.00")
    routing_or_ecn_fee_per_share: Decimal = Decimal("0.00")
    regulatory_fee_per_order: Decimal = Decimal("0.00")
    locate_fee_per_order: Decimal = Decimal("0.00")
    borrow_fee_per_order: Decimal = Decimal("0.00")
    other_fee_per_order: Decimal = Decimal("0.00")
    currency: str = "USD"
    rounding: str = "ROUND_HALF_UP_CENTS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "commission_per_share": _decimal_str(self.commission_per_share),
            "minimum_commission_per_order": _decimal_str(self.minimum_commission_per_order),
            "entry_fixed_fee": _decimal_str(self.entry_fixed_fee),
            "exit_fixed_fee": _decimal_str(self.exit_fixed_fee),
            "routing_or_ecn_fee_per_share": _decimal_str(self.routing_or_ecn_fee_per_share),
            "regulatory_fee_per_order": _decimal_str(self.regulatory_fee_per_order),
            "locate_fee_per_order": _decimal_str(self.locate_fee_per_order),
            "borrow_fee_per_order": _decimal_str(self.borrow_fee_per_order),
            "other_fee_per_order": _decimal_str(self.other_fee_per_order),
            "currency": self.currency,
            "rounding": self.rounding,
        }


@dataclass(frozen=True)
class CashLedgerEntry:
    entry_id: str
    fill_id: str
    order_id: str
    ticker: str
    entry_type: str
    amount: Decimal
    cash_after: Decimal
    timestamp: Any
    description: str

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class AccountState:
    starting_equity: Decimal
    cash: Decimal
    position_market_value: Decimal
    realized_gross_pnl: Decimal
    accrued_costs: Decimal
    realized_net_pnl: Decimal
    unrealized_pnl: Decimal
    equity: Decimal

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class AccountingRunSummary:
    run_id: str
    cost_model_id: str
    starting_equity: Decimal
    gross_pnl: Decimal
    total_costs: Decimal
    realized_net_pnl: Decimal
    ending_equity: Decimal
    final_cash: Decimal
    final_position_quantity: int
    cost_component_count: int
    cash_ledger_entry_count: int
    gross_pnl_matches_mechanical: bool
    net_pnl_reconciles: bool
    ending_equity_reconciles: bool
    ledger_balance_reconciles: bool
    broker_cost_realism_claimed: bool
    fill_realism_claimed: bool
    short_tradability_evaluated: bool
    edge_evaluated: bool
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


@dataclass(frozen=True)
class AccountingRunResult:
    summary: AccountingRunSummary
    cost_breakdowns: tuple[CostBreakdown, ...]
    cash_ledger: tuple[CashLedgerEntry, ...]
    final_account_state: AccountState

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_decimal(self)


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _money_str(value: Decimal) -> str:
    return format(_money(value), "f")


def _decimal_str(value: Decimal) -> str:
    return format(value, "f")


def _jsonable_decimal(value: Any) -> Any:
    if isinstance(value, Decimal):
        return _money_str(value)
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


