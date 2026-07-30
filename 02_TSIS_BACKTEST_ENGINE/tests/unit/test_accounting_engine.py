from __future__ import annotations

import hashlib
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tsis_backtest.accounting.contracts import CostModel  # noqa: E402
from tsis_backtest.accounting.engine import AccountingEngine, AccountingError  # noqa: E402
from tsis_backtest.mechanics.contracts import BUY_TO_COVER, CLOSE_PROXY, OPEN_PROXY, SELL_SHORT, Position, ScheduledDecision, TradeLedger  # noqa: E402
from tsis_backtest.mechanics.event_loop import MechanicalEventLoop  # noqa: E402
from tsis_backtest.preflight.contracts import MarketDataBar1m, to_jsonable  # noqa: E402
from tsis_backtest.replay.contracts import ReplayBarEvent  # noqa: E402
from tsis_backtest.replay.historical_feed import HistoricalReplayFeed  # noqa: E402


class AccountingEngineTests(unittest.TestCase):
    def test_zero_costs_net_equals_gross(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=100)

        result = AccountingEngine().run("acct_zero", mechanical.ledger, mechanical.summary, CostModel("zero"), Decimal("10000.00"))

        self.assertEqual(result.summary.gross_pnl, Decimal("150.00"))
        self.assertEqual(result.summary.total_costs, Decimal("0.00"))
        self.assertEqual(result.summary.realized_net_pnl, Decimal("150.00"))
        self.assertEqual(result.summary.ending_equity, Decimal("10150.00"))
        self.assertTrue(result.summary.net_pnl_reconciles)
        self.assertTrue(result.summary.ending_equity_reconciles)
        self.assertTrue(result.summary.ledger_balance_reconciles)

    def test_commission_per_share_applies_to_both_orders(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=100)
        model = CostModel("per_share", commission_per_share=Decimal("0.01"))

        result = AccountingEngine().run("acct_per_share", mechanical.ledger, mechanical.summary, model, Decimal("10000.00"))

        self.assertEqual(result.summary.total_costs, Decimal("2.00"))
        self.assertEqual(result.summary.realized_net_pnl, Decimal("148.00"))

    def test_minimum_commission_per_order(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=10)
        model = CostModel("min_commission", commission_per_share=Decimal("0.01"), minimum_commission_per_order=Decimal("1.00"))

        result = AccountingEngine().run("acct_min", mechanical.ledger, mechanical.summary, model, Decimal("10000.00"))

        self.assertEqual(result.summary.total_costs, Decimal("2.00"))
        self.assertEqual([breakdown.total_cost for breakdown in result.cost_breakdowns], [Decimal("1.00"), Decimal("1.00")])

    def test_multiple_components_are_kept_separate_and_summed(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=100)
        model = CostModel(
            "multi",
            commission_per_share=Decimal("0.01"),
            routing_or_ecn_fee_per_share=Decimal("0.002"),
            regulatory_fee_per_order=Decimal("0.03"),
            locate_fee_per_order=Decimal("0.50"),
            borrow_fee_per_order=Decimal("0.25"),
            other_fee_per_order=Decimal("0.10"),
            entry_fixed_fee=Decimal("0.40"),
            exit_fixed_fee=Decimal("0.20"),
        )

        result = AccountingEngine().run("acct_multi", mechanical.ledger, mechanical.summary, model, Decimal("10000.00"))

        categories = [component.category for component in result.cost_breakdowns[0].components]
        self.assertEqual(categories, ["commission", "routing_or_ecn_fee", "regulatory_fee", "locate_fee", "borrow_fee", "other_fee"])
        self.assertEqual(result.summary.total_costs, Decimal("4.76"))
        self.assertEqual(result.summary.realized_net_pnl, Decimal("145.24"))

    def test_short_loser_net_pnl(self) -> None:
        mechanical = self._mechanical_result(entry_open=3.87, exit_close=4.665, quantity=100)
        model = CostModel("loser_cost", commission_per_share=Decimal("0.005"), minimum_commission_per_order=Decimal("1.00"))

        result = AccountingEngine().run("acct_loser", mechanical.ledger, mechanical.summary, model, Decimal("10000.00"))

        self.assertEqual(result.summary.gross_pnl, Decimal("-79.50"))
        self.assertEqual(result.summary.total_costs, Decimal("2.00"))
        self.assertEqual(result.summary.realized_net_pnl, Decimal("-81.50"))
        self.assertEqual(result.summary.ending_equity, Decimal("9918.50"))

    def test_open_position_not_closeable(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=100)
        broken = TradeLedger(mechanical.ledger.order_intents, mechanical.ledger.orders, mechanical.ledger.fills[:1], Position("AAA", -100, 10.0, 0.0))

        with self.assertRaises(AccountingError) as ctx:
            AccountingEngine().run("acct_open", broken, mechanical.summary, CostModel("zero"), Decimal("10000.00"))

        self.assertEqual(ctx.exception.code, "ACCOUNTING_POSITION_NOT_CLOSED")

    def test_gross_mismatch_is_reported(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=100)
        bad_summary = type(mechanical.summary)(
            **{**mechanical.summary.to_dict(), "gross_pnl": "151.00", "linear_reference_gross_pnl": "151.00"}
        )

        result = AccountingEngine().run("acct_bad", mechanical.ledger, bad_summary, CostModel("zero"), Decimal("10000.00"))

        self.assertFalse(result.summary.gross_pnl_matches_mechanical)

    def test_same_inputs_same_accounting_hash(self) -> None:
        mechanical = self._mechanical_result(entry_open=10.0, exit_close=8.5, quantity=100)
        model = CostModel("deterministic", commission_per_share=Decimal("0.01"))

        first = AccountingEngine().run("acct_hash", mechanical.ledger, mechanical.summary, model, Decimal("10000.00")).to_dict()
        second = AccountingEngine().run("acct_hash", mechanical.ledger, mechanical.summary, model, Decimal("10000.00")).to_dict()

        self.assertEqual(self._hash(first), self._hash(second))

    def test_cost_model_serialization_preserves_sub_cent_rates(self) -> None:
        model = CostModel("sub_cent", commission_per_share=Decimal("0.005"), routing_or_ecn_fee_per_share=Decimal("0.0025"))

        payload = model.to_dict()

        self.assertEqual(payload["commission_per_share"], "0.005")
        self.assertEqual(payload["routing_or_ecn_fee_per_share"], "0.0025")
    def test_real_fixture_abat_accounting(self) -> None:
        report_path = ROOT / "tests/fixtures/bt_gate_011_qg5_portable/data_preflight_report.json"
        self.assertTrue(report_path.is_file(), "portable QG5 preflight fixture missing")
        events = HistoricalReplayFeed.from_preflight_report(report_path).stream_events()
        mechanical = MechanicalEventLoop().run("mechanical_abat_real_fixture_v0_1", events, self._decisions("ABAT", 100))
        model = CostModel("min_commission_v0_1", commission_per_share=Decimal("0.005"), minimum_commission_per_order=Decimal("1.00"))

        result = AccountingEngine().run("accounting_abat_real_fixture_v0_1", mechanical.ledger, mechanical.summary, model, Decimal("10000.00"))

        self.assertEqual(result.summary.gross_pnl, Decimal("-79.50"))
        self.assertEqual(result.summary.total_costs, Decimal("2.00"))
        self.assertEqual(result.summary.realized_net_pnl, Decimal("-81.50"))
        self.assertEqual(result.summary.final_position_quantity, 0)
        self.assertFalse(result.summary.broker_cost_realism_claimed)
        self.assertFalse(result.summary.fill_realism_claimed)
        self.assertFalse(result.summary.short_tradability_evaluated)
        self.assertFalse(result.summary.edge_evaluated)

    def _mechanical_result(self, entry_open: float, exit_close: float, quantity: int):
        return MechanicalEventLoop().run("mechanical_synthetic", self._events("AAA", entry_open, exit_close), self._decisions("AAA", quantity))

    def _decisions(self, ticker: str, quantity: int) -> tuple[ScheduledDecision, ScheduledDecision]:
        scheduled_at = datetime(2026, 1, 5, 14, 29, tzinfo=timezone.utc)
        return (
            ScheduledDecision("open", ticker, SELL_SHORT, quantity, OPEN_PROXY, scheduled_at, "programmed open proxy short"),
            ScheduledDecision("close", ticker, BUY_TO_COVER, quantity, CLOSE_PROXY, scheduled_at, "programmed close proxy cover"),
        )

    def _events(self, ticker: str, entry_open: float, exit_close: float) -> tuple[ReplayBarEvent, ReplayBarEvent]:
        open_start = datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc)
        close_start = datetime(2026, 1, 5, 20, 59, tzinfo=timezone.utc)
        return (
            self._bar_event(ticker, open_start, entry_open, entry_open + 0.1),
            self._bar_event(ticker, close_start, exit_close - 0.1, exit_close),
        )

    def _bar_event(self, ticker: str, ts_start: datetime, open_price: float, close_price: float) -> ReplayBarEvent:
        bar = MarketDataBar1m(
            ticker=ticker,
            ts_start=ts_start,
            ts_end=ts_start + timedelta(minutes=1),
            available_at=ts_start + timedelta(minutes=1),
            session_label="2026-01-05:REGULAR_ONLY",
            open=open_price,
            high=max(open_price, close_price),
            low=min(open_price, close_price),
            close=close_price,
            volume=1000,
            price_view="quote_guarded_1m",
        )
        return ReplayBarEvent("BAR", ticker, bar.available_at, bar)

    @staticmethod
    def _hash(payload: dict) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    unittest.main()


