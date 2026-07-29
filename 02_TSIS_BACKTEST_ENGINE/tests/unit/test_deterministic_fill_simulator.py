from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tsis_backtest.execution.contracts import (  # noqa: E402
    BPS_OF_PRICE_ADVERSE,
    BUY,
    BUY_TO_COVER,
    DAY,
    EXPIRED_UNFILLED,
    FAIL_AMBIGUOUS_BAR,
    FILLED,
    FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE,
    FULL_FILL,
    LIMIT,
    MARKET_PROXY,
    NO_FILL_GAP,
    NO_FILL_MISSING_PRICE,
    NO_FILL_NOT_ELIGIBLE,
    PESSIMISTIC,
    REJECTED_BY_CONTRACT,
    SELL,
    SELL_SHORT,
    STOP_MARKET_PROXY,
    ZERO_SLIPPAGE,
    CostModelV0,
    ExecutionOrder,
    ExecutionPolicy,
    ExecutionSimulationError,
    SlippageModel,
)
from tsis_backtest.execution.simulator import DeterministicFillSimulator  # noqa: E402
from tsis_backtest.preflight.contracts import MarketDataBar1m  # noqa: E402
from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayGapEvent  # noqa: E402


class DeterministicFillSimulatorTests(unittest.TestCase):
    def test_market_proxy_buy_uses_open_and_adverse_fixed_slippage(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("0.05")))

        result = sim.evaluate_order(self._order("mkt-buy", BUY, MARKET_PROXY), [self._event(open_price="10.00")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertEqual(result.terminal_order_outcome, FILLED)
        self.assertEqual(result.fill.execution_price_before_slippage, Decimal("10.00"))
        self.assertEqual(result.fill.slippage_amount, Decimal("0.05"))
        self.assertEqual(result.fill.fill_price, Decimal("10.05"))
        self.assertEqual(result.fill.gross_notional, Decimal("1005.00"))

    def test_market_proxy_sell_short_slippage_is_adverse_downward(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("0.05")))

        result = sim.evaluate_order(self._order("mkt-short", SELL_SHORT, MARKET_PROXY), [self._event(open_price="10.00")])

        self.assertEqual(result.fill.fill_price, Decimal("9.95"))
        self.assertEqual(result.fill.gross_notional, Decimal("995.00"))

    def test_bps_slippage_is_base_price_times_bps_over_10000(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("bps", slippage_unit=BPS_OF_PRICE_ADVERSE, slippage_value=Decimal("25")))

        result = sim.evaluate_order(self._order("mkt-bps", BUY, MARKET_PROXY), [self._event(open_price="20.00")])

        self.assertEqual(result.fill.slippage_amount, Decimal("0.0500"))
        self.assertEqual(result.fill.fill_price, Decimal("20.0500"))

    def test_order_exactly_at_source_bar_start_is_eligible(self) -> None:
        order = self._order("exact", BUY, MARKET_PROXY, submitted_at=self._ts(0))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event()])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)

    def test_order_after_source_bar_start_is_not_eligible_and_expires(self) -> None:
        order = self._order("late", BUY, MARKET_PROXY, submitted_at=self._ts(0) + timedelta(seconds=1))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event()])

        self.assertEqual(result.evaluation_outcome, NO_FILL_NOT_ELIGIBLE)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_gap_evaluation_is_preserved_before_later_fill(self) -> None:
        order = self._order("gap-then-fill", BUY, MARKET_PROXY, submitted_at=self._ts(0))
        gap = self._gap(0)
        later = self._event(ts_start=self._ts(1), open_price="11.00")

        result = DeterministicFillSimulator().simulate_order(order, [later, gap])

        self.assertEqual([ev.evaluation_outcome for ev in result.evaluations], [NO_FILL_GAP, FULL_FILL])
        self.assertEqual(result.terminal_order_outcome, FILLED)
        self.assertEqual(result.fill.fill_price, Decimal("11.00"))

    def test_gap_only_expires_but_keeps_gap_evaluation(self) -> None:
        result = DeterministicFillSimulator().simulate_order(self._order("gap", BUY, MARKET_PROXY), [self._gap(0)])

        self.assertEqual(result.evaluations[0].evaluation_outcome, NO_FILL_GAP)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_missing_or_nonpositive_required_price_returns_no_fill_missing_price(self) -> None:
        result = DeterministicFillSimulator().evaluate_order(self._order("missing", BUY, MARKET_PROXY), [self._event(open_price="0")])

        self.assertEqual(result.evaluation_outcome, NO_FILL_MISSING_PRICE)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_buy_limit_touched_fills_at_limit_without_adverse_slippage(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("1.00")))
        order = self._order("buy-limit", BUY, LIMIT, limit_price=Decimal("9.90"))

        result = sim.evaluate_order(order, [self._event(open_price="10.00", high="10.50", low="9.80")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertLessEqual(result.fill.fill_price, Decimal("9.90"))
        self.assertEqual(result.fill.fill_price, Decimal("9.90"))
        self.assertEqual(result.fill.slippage_amount, Decimal("1.00"))

    def test_buy_limit_not_touched_expires(self) -> None:
        order = self._order("buy-limit-no", BUY, LIMIT, limit_price=Decimal("9.70"))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(low="9.80")])

        self.assertEqual(result.evaluation_outcome, NO_FILL_NOT_ELIGIBLE)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_sell_limit_touched_fills_at_or_above_limit(self) -> None:
        order = self._order("sell-limit", SELL, LIMIT, limit_price=Decimal("10.40"))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(high="10.50")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertGreaterEqual(result.fill.fill_price, Decimal("10.40"))
        self.assertEqual(result.fill.fill_price, Decimal("10.40"))

    def test_sell_limit_not_touched_expires(self) -> None:
        order = self._order("sell-limit-no", SELL, LIMIT, limit_price=Decimal("10.60"))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(high="10.50")])

        self.assertEqual(result.evaluation_outcome, NO_FILL_NOT_ELIGIBLE)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_buy_stop_gap_through_uses_adverse_open_before_slippage(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("0.10")))
        order = self._order("buy-stop", BUY_TO_COVER, STOP_MARKET_PROXY, stop_price=Decimal("10.00"))

        result = sim.evaluate_order(order, [self._event(open_price="10.60", high="10.80", low="10.40")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertEqual(result.fill.execution_price_before_slippage, Decimal("10.60"))
        self.assertEqual(result.fill.fill_price, Decimal("10.70"))

    def test_sell_stop_gap_through_uses_adverse_open_before_slippage(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("0.10")))
        order = self._order("sell-stop", SELL_SHORT, STOP_MARKET_PROXY, stop_price=Decimal("10.00"))

        result = sim.evaluate_order(order, [self._event(open_price="9.40", high="9.70", low="9.20")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertEqual(result.fill.execution_price_before_slippage, Decimal("9.40"))
        self.assertEqual(result.fill.fill_price, Decimal("9.30"))

    def test_stop_not_triggered_expires(self) -> None:
        order = self._order("stop-no", BUY, STOP_MARKET_PROXY, stop_price=Decimal("10.80"))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(high="10.50")])

        self.assertEqual(result.evaluation_outcome, NO_FILL_NOT_ELIGIBLE)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_ambiguous_intrabar_sequence_fails_closed_and_maps_to_rejected(self) -> None:
        order = self._order("ambiguous", BUY, LIMIT, limit_price=Decimal("9.90"), stop_price=Decimal("10.40"))

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(high="10.50", low="9.80")])

        self.assertEqual(result.evaluation_outcome, FAIL_AMBIGUOUS_BAR)
        self.assertEqual(result.terminal_order_outcome, REJECTED_BY_CONTRACT)

    def test_pessimistic_ambiguous_bar_policy_is_reserved(self) -> None:
        with self.assertRaises(ExecutionSimulationError) as ctx:
            DeterministicFillSimulator(execution_policy=ExecutionPolicy(ambiguous_bar_policy=PESSIMISTIC))

        self.assertEqual(ctx.exception.code, "PESSIMISTIC_RESERVED_NOT_IMPLEMENTED")

    def test_unsupported_partial_fill_request_rejected_by_contract(self) -> None:
        order = self._order("partial", BUY, MARKET_PROXY)
        order = ExecutionOrder(**{**order.to_dict(), "fill_capability": "PARTIAL_FILL"})

        result = DeterministicFillSimulator().evaluate_order(order, [self._event()])

        self.assertEqual(result.evaluation_outcome, REJECTED_BY_CONTRACT)
        self.assertEqual(result.reason_code, "PARTIAL_FILL_RESERVED_NOT_IMPLEMENTED")

    def test_time_in_force_other_than_day_rejected_by_contract(self) -> None:
        order = ExecutionOrder(**{**self._order("gtd", BUY, MARKET_PROXY).to_dict(), "time_in_force": "GTC"})

        result = DeterministicFillSimulator().evaluate_order(order, [self._event()])

        self.assertEqual(result.evaluation_outcome, REJECTED_BY_CONTRACT)
        self.assertEqual(result.reason_code, "TIME_IN_FORCE_UNSUPPORTED")

    def test_unsupported_tick_policy_fails_closed_at_configuration(self) -> None:
        with self.assertRaises(ExecutionSimulationError) as ctx:
            DeterministicFillSimulator(execution_policy=ExecutionPolicy(tick_size_policy_id="SNAP_TO_CENTS"))

        self.assertEqual(ctx.exception.code, "FAIL_CLOSED_WHEN_TICK_POLICY_REQUIRED")

    def test_computed_fill_price_nonpositive_returns_rejected_by_contract(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("huge", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("20.00")))

        result = sim.evaluate_order(self._order("bad-price", SELL_SHORT, MARKET_PROXY), [self._event(open_price="10.00")])

        self.assertEqual(result.evaluation_outcome, REJECTED_BY_CONTRACT)
        self.assertEqual(result.reason_code, "FILL_PRICE_NONPOSITIVE")

    def test_cost_components_use_declared_categories_and_round_half_even(self) -> None:
        model = CostModelV0(
            "costs",
            commission_per_share=Decimal("0.005"),
            minimum_commission_per_order=Decimal("1.00"),
            fixed_fee_per_order=Decimal("0.125"),
            routing_or_ecn_fee_per_share=Decimal("0.0025"),
            regulatory_fee_per_share=Decimal("0.0002"),
            locate_fee_per_share=Decimal("0.01"),
            other_fixed_fee_per_filled_order=Decimal("0.125"),
        )
        result = DeterministicFillSimulator(cost_model=model).evaluate_order(self._order("cost-short", SELL_SHORT, MARKET_PROXY), [self._event(open_price="10.00")])

        breakdown = result.cost_breakdown
        self.assertEqual([c.category for c in breakdown.components], ["commission", "routing_or_ecn_fee", "regulatory_fee", "locate_fee", "borrow_fee", "other_fee"])
        self.assertEqual([c.rounded_amount for c in breakdown.components], [Decimal("1.00"), Decimal("0.25"), Decimal("0.02"), Decimal("1.00"), Decimal("0.00"), Decimal("0.25")])
        self.assertEqual(breakdown.total_cost, Decimal("2.52"))
        self.assertEqual(breakdown.components[1].raw_amount, Decimal("0.2500"))

    def test_borrow_fee_without_authorized_borrow_model_rejected_by_contract(self) -> None:
        sim = DeterministicFillSimulator(cost_model=CostModelV0("borrow", borrow_fee_per_order=Decimal("0.01")))

        result = sim.evaluate_order(self._order("borrow", SELL_SHORT, MARKET_PROXY), [self._event()])

        self.assertEqual(result.evaluation_outcome, REJECTED_BY_CONTRACT)
        self.assertEqual(result.reason_code, "BORROW_MODEL_NOT_AUTHORIZED")

    def test_run_manifest_records_required_models_and_non_claims(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("zero", slippage_unit=ZERO_SLIPPAGE), cost_model=CostModelV0("zero"))

        manifest = sim.run_manifest().to_dict()

        self.assertEqual(manifest["execution_profile_id"], "bar_based_execution_profile_v0_1")
        self.assertEqual(manifest["fill_model_id"], "DETERMINISTIC_FILL_SIMULATOR_V0_1")
        self.assertEqual(manifest["tick_size_policy_id"], "PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION")
        self.assertEqual(manifest["ambiguous_bar_policy"], "FAIL_AMBIGUOUS_BAR_ONLY")
        self.assertFalse(manifest["broker_cost_realism_claimed"])
        self.assertFalse(manifest["fill_realism_claimed"])
        self.assertFalse(manifest["edge_evaluated"])

    def test_same_inputs_same_canonical_hash(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("0.01")))
        order = self._order("hash", BUY, MARKET_PROXY)
        events = [self._event()]

        first = sim.simulate_order(order, events).to_dict()
        second = sim.simulate_order(order, events).to_dict()

        self.assertEqual(sim.deterministic_hash(first), sim.deterministic_hash(second))


    def test_market_proxy_close_field_uses_bar_close_and_records_at_available_at(self) -> None:
        close_start = self._ts(389)
        order = self._order("close-proxy", BUY_TO_COVER, MARKET_PROXY, submitted_at=close_start, market_price_field="close")

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(ts_start=close_start, open_price="9.90", close="10.25")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertEqual(result.fill.execution_price_before_slippage, Decimal("10.25"))
        self.assertEqual(result.fill.fill_price, Decimal("10.25"))
        self.assertEqual(result.fill.execution_timestamp, close_start + timedelta(minutes=1))
        self.assertEqual(result.fill.fill_recorded_at, close_start + timedelta(minutes=1))

    def test_close_proxy_order_after_final_bar_start_is_ineligible(self) -> None:
        close_start = self._ts(389)
        order = self._order("late-close", BUY_TO_COVER, MARKET_PROXY, submitted_at=close_start + timedelta(seconds=1), market_price_field="close")

        result = DeterministicFillSimulator().evaluate_order(order, [self._event(ts_start=close_start, open_price="9.90", close="10.25")])

        self.assertEqual(result.evaluation_outcome, NO_FILL_NOT_ELIGIBLE)
        self.assertEqual(result.terminal_order_outcome, EXPIRED_UNFILLED)

    def test_sell_stop_activated_uses_sell_side_adverse_rule(self) -> None:
        sim = DeterministicFillSimulator(slippage_model=SlippageModel("fixed", slippage_unit=FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE, slippage_value=Decimal("0.10")))
        order = self._order("sell-stop", SELL, STOP_MARKET_PROXY, stop_price=Decimal("10.00"))

        result = sim.evaluate_order(order, [self._event(open_price="9.40", high="9.70", low="9.20")])

        self.assertEqual(result.evaluation_outcome, FULL_FILL)
        self.assertEqual(result.fill.execution_price_before_slippage, Decimal("9.40"))
        self.assertEqual(result.fill.fill_price, Decimal("9.30"))

    def test_order_type_not_authorized_rejected_by_contract(self) -> None:
        order = self._order("unsupported", BUY, MARKET_PROXY)
        order = ExecutionOrder(**{**order.to_dict(), "order_type": "MOC"})

        result = DeterministicFillSimulator().evaluate_order(order, [self._event()])

        self.assertEqual(result.evaluation_outcome, REJECTED_BY_CONTRACT)
        self.assertEqual(result.reason_code, "ORDER_TYPE_UNSUPPORTED")

    def test_market_proxy_unknown_price_field_rejected_by_contract(self) -> None:
        order = self._order("bad-field", BUY, MARKET_PROXY, market_price_field="vwap")

        result = DeterministicFillSimulator().evaluate_order(order, [self._event()])

        self.assertEqual(result.evaluation_outcome, REJECTED_BY_CONTRACT)
        self.assertEqual(result.reason_code, "MARKET_PROXY_PRICE_FIELD_UNSUPPORTED")

    def _order(self, order_id: str, side: str, order_type: str, submitted_at: datetime | None = None, limit_price: Decimal | None = None, stop_price: Decimal | None = None, market_price_field: str = "open") -> ExecutionOrder:
        return ExecutionOrder(
            order_id=order_id,
            ticker="AAA",
            side=side,
            quantity=100,
            order_type=order_type,
            order_submission_timestamp=submitted_at or self._ts(0),
            time_in_force=DAY,
            limit_price=limit_price,
            stop_price=stop_price,
            market_price_field=market_price_field,
        )

    def _event(self, ts_start: datetime | None = None, open_price: str = "10.00", high: str = "10.50", low: str = "9.80", close: str = "10.10") -> ReplayBarEvent:
        ts_start = ts_start or self._ts(0)
        bar = MarketDataBar1m(
            ticker="AAA",
            ts_start=ts_start,
            ts_end=ts_start + timedelta(minutes=1),
            available_at=ts_start + timedelta(minutes=1),
            session_label="2026-01-05:REGULAR_ONLY",
            open=float(open_price),
            high=float(high),
            low=float(low),
            close=float(close),
            volume=1000,
            price_view="quote_guarded_1m",
        )
        return ReplayBarEvent("BAR", "AAA", bar.available_at, bar)

    def _gap(self, minute_offset: int) -> ReplayGapEvent:
        ts_start = self._ts(minute_offset)
        return ReplayGapEvent(
            event_type="GAP",
            ticker="AAA",
            ts_start=ts_start,
            ts_end=ts_start + timedelta(minutes=1),
            available_at=ts_start + timedelta(minutes=1),
            session_label="2026-01-05:REGULAR_ONLY",
            price_view="quote_guarded_1m",
            reason="OBSERVED_MINUTE_GAP",
        )

    @staticmethod
    def _ts(minute_offset: int) -> datetime:
        return datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=minute_offset)


if __name__ == "__main__":
    unittest.main()
