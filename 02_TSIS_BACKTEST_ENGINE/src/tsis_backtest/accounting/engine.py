"""Minimum gross-to-net accounting over a mechanical trade ledger."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from tsis_backtest.mechanics.contracts import BUY_TO_COVER, SELL_SHORT, MechanicalRunSummary, TradeLedger

from .contracts import (
    COST_CATEGORIES,
    AccountState,
    AccountingRunResult,
    AccountingRunSummary,
    CashLedgerEntry,
    CostBreakdown,
    CostComponent,
    CostModel,
)


class AccountingError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class AccountingEngine:
    def run(
        self,
        run_id: str,
        ledger: TradeLedger,
        mechanical_summary: MechanicalRunSummary,
        cost_model: CostModel,
        starting_equity: Decimal,
    ) -> AccountingRunResult:
        if ledger.final_position.quantity != 0:
            raise AccountingError("ACCOUNTING_POSITION_NOT_CLOSED", "minimum accounting requires final position quantity 0")
        cash = Decimal("0.00")
        cost_breakdowns = []
        cash_entries = []
        for fill in ledger.fills:
            fill_notional = _money(_dec(fill.quantity) * _dec(fill.price))
            if fill.side == SELL_SHORT:
                cash += fill_notional
                cash_entries.append(self._cash_entry(fill, "SHORT_SALE_PROCEEDS", fill_notional, cash, "short sale proceeds"))
            elif fill.side == BUY_TO_COVER:
                cash -= fill_notional
                cash_entries.append(self._cash_entry(fill, "SHORT_COVER_PAYMENT", -fill_notional, cash, "short cover payment"))
            else:
                raise AccountingError("ACCOUNTING_FILL_SIDE_UNSUPPORTED", fill.side)
            breakdown = self._cost_breakdown(fill, cost_model)
            cost_breakdowns.append(breakdown)
            if breakdown.total_cost:
                cash -= breakdown.total_cost
                cash_entries.append(self._cash_entry(fill, "COST", -breakdown.total_cost, cash, "transaction costs"))

        total_costs = _money(sum((breakdown.total_cost for breakdown in cost_breakdowns), Decimal("0.00")))
        gross_pnl = _money(_dec(ledger.final_position.realized_gross_pnl))
        mechanical_gross = _money(_dec(mechanical_summary.gross_pnl))
        realized_net = _money(gross_pnl - total_costs)
        ending_equity = _money(starting_equity + realized_net)
        final_state = AccountState(
            starting_equity=_money(starting_equity),
            cash=_money(cash),
            position_market_value=Decimal("0.00"),
            realized_gross_pnl=gross_pnl,
            accrued_costs=total_costs,
            realized_net_pnl=realized_net,
            unrealized_pnl=Decimal("0.00"),
            equity=ending_equity,
        )
        cash_ledger_sum = _money(sum((entry.amount for entry in cash_entries), Decimal("0.00")))
        summary = AccountingRunSummary(
            run_id=run_id,
            cost_model_id=cost_model.model_id,
            starting_equity=_money(starting_equity),
            gross_pnl=gross_pnl,
            total_costs=total_costs,
            realized_net_pnl=realized_net,
            ending_equity=ending_equity,
            final_cash=_money(cash),
            final_position_quantity=ledger.final_position.quantity,
            cost_component_count=sum(len(breakdown.components) for breakdown in cost_breakdowns),
            cash_ledger_entry_count=len(cash_entries),
            gross_pnl_matches_mechanical=gross_pnl == mechanical_gross,
            net_pnl_reconciles=realized_net == _money(gross_pnl - total_costs),
            ending_equity_reconciles=ending_equity == _money(starting_equity + realized_net),
            ledger_balance_reconciles=cash_ledger_sum == _money(cash),
            broker_cost_realism_claimed=False,
            fill_realism_claimed=False,
            short_tradability_evaluated=False,
            edge_evaluated=False,
            limitations=(
                "minimum deterministic cost accounting only",
                "broker cost realism not claimed",
                "borrow and locate costs default to configured components only",
                "cash is not equity for open short positions",
            ),
        )
        return AccountingRunResult(
            summary=summary,
            cost_breakdowns=tuple(cost_breakdowns),
            cash_ledger=tuple(cash_entries),
            final_account_state=final_state,
        )

    @staticmethod
    def _cost_breakdown(fill, cost_model: CostModel) -> CostBreakdown:
        per_share_commission = _dec(fill.quantity) * cost_model.commission_per_share
        commission = max(per_share_commission, cost_model.minimum_commission_per_order)
        fixed_fee = cost_model.entry_fixed_fee if fill.side == SELL_SHORT else cost_model.exit_fixed_fee
        components = (
            CostComponent("commission", _money(commission), cost_model.currency, "commission per share with minimum"),
            CostComponent("routing_or_ecn_fee", _money(_dec(fill.quantity) * cost_model.routing_or_ecn_fee_per_share), cost_model.currency, "routing/ECN fee proxy"),
            CostComponent("regulatory_fee", _money(cost_model.regulatory_fee_per_order), cost_model.currency, "regulatory fee proxy"),
            CostComponent("locate_fee", _money(cost_model.locate_fee_per_order), cost_model.currency, "locate fee proxy"),
            CostComponent("borrow_fee", _money(cost_model.borrow_fee_per_order), cost_model.currency, "borrow fee proxy"),
            CostComponent("other_fee", _money(cost_model.other_fee_per_order + fixed_fee), cost_model.currency, "other/fixed fee proxy"),
        )
        categories = tuple(component.category for component in components)
        if categories != COST_CATEGORIES:
            raise AccountingError("ACCOUNTING_COST_COMPONENTS_INCOMPLETE", "cost components must match declared categories")
        return CostBreakdown(fill.fill_id, fill.order_id, components)

    @staticmethod
    def _cash_entry(fill, entry_type: str, amount: Decimal, cash_after: Decimal, description: str) -> CashLedgerEntry:
        return CashLedgerEntry(
            entry_id=f"cash-{fill.fill_id}-{entry_type}",
            fill_id=fill.fill_id,
            order_id=fill.order_id,
            ticker=fill.ticker,
            entry_type=entry_type,
            amount=_money(amount),
            cash_after=_money(cash_after),
            timestamp=fill.recorded_at,
            description=description,
        )


def _dec(value) -> Decimal:
    return Decimal(str(value))


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
