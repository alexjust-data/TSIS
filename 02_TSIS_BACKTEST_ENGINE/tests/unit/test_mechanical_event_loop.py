from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tsis_backtest.mechanics.contracts import BUY_TO_COVER, CLOSE_PROXY, OPEN_PROXY, SELL_SHORT, ScheduledDecision  # noqa: E402
from tsis_backtest.mechanics.event_loop import MechanicalEventLoop, MechanicalEventLoopError  # noqa: E402
from tsis_backtest.preflight.contracts import MarketDataBar1m  # noqa: E402
from tsis_backtest.replay.contracts import ReplayBarEvent  # noqa: E402
from tsis_backtest.replay.historical_feed import HistoricalReplayFeed  # noqa: E402


class MechanicalEventLoopTests(unittest.TestCase):
    def test_short_open_close_round_trip_derives_position_and_pnl_from_fills(self) -> None:
        events = self._events("AAA", entry_open=10.0, exit_close=8.5)
        decisions = self._decisions("AAA", quantity=100)

        result = MechanicalEventLoop().run("mechanical_synthetic", events, decisions)

        self.assertEqual(result.summary.final_position_quantity, 0)
        self.assertEqual(result.summary.order_count, 2)
        self.assertEqual(result.summary.fill_count, 2)
        self.assertAlmostEqual(result.summary.gross_pnl, 150.0)
        self.assertAlmostEqual(result.ledger.final_position.realized_gross_pnl, 150.0)
        self.assertTrue(result.summary.pnl_matches_reference)
        self.assertFalse(result.summary.execution_realism_claimed)
        self.assertFalse(result.summary.edge_evaluated)

    def test_open_fill_uses_execution_timestamp_before_recorded_at(self) -> None:
        result = MechanicalEventLoop().run("mechanical_synthetic", self._events("AAA", 10.0, 8.0), self._decisions("AAA", 50))
        entry_fill, exit_fill = result.ledger.fills

        self.assertEqual(entry_fill.execution_timestamp.isoformat(), "2026-01-05T14:30:00+00:00")
        self.assertEqual(entry_fill.recorded_at.isoformat(), "2026-01-05T14:31:00+00:00")
        self.assertEqual(exit_fill.execution_timestamp.isoformat(), "2026-01-05T21:00:00+00:00")
        self.assertEqual(exit_fill.recorded_at.isoformat(), "2026-01-05T21:00:00+00:00")

    def test_decision_must_be_scheduled_before_proxy_execution(self) -> None:
        decisions = (
            ScheduledDecision("open", "AAA", SELL_SHORT, 100, OPEN_PROXY, datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc), "too late"),
            ScheduledDecision("close", "AAA", BUY_TO_COVER, 100, CLOSE_PROXY, datetime(2026, 1, 5, 14, 29, tzinfo=timezone.utc), "close"),
        )

        with self.assertRaises(MechanicalEventLoopError) as ctx:
            MechanicalEventLoop().run("mechanical_synthetic", self._events("AAA", 10.0, 8.0), decisions)

        self.assertEqual(ctx.exception.code, "MECHANICAL_DECISION_NOT_SCHEDULED_BEFORE_EXECUTION")

    def test_quantity_mismatch_fails(self) -> None:
        decisions = (
            ScheduledDecision("open", "AAA", SELL_SHORT, 100, OPEN_PROXY, datetime(2026, 1, 5, 14, 29, tzinfo=timezone.utc), "open"),
            ScheduledDecision("close", "AAA", BUY_TO_COVER, 99, CLOSE_PROXY, datetime(2026, 1, 5, 14, 29, tzinfo=timezone.utc), "close"),
        )

        with self.assertRaises(MechanicalEventLoopError) as ctx:
            MechanicalEventLoop().run("mechanical_synthetic", self._events("AAA", 10.0, 8.0), decisions)

        self.assertEqual(ctx.exception.code, "MECHANICAL_QUANTITY_MISMATCH")

    def test_real_fixture_abat_short_round_trip_matches_linear_reference(self) -> None:
        report_path = Path(
            "C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/"
            "run_preflight_real_fixture_2026_01_05_qg5_v0_2/"
            "data_preflight_report.json"
        )
        if not report_path.exists():
            self.skipTest("local TSIS real fixture preflight report not present")
        events = HistoricalReplayFeed.from_preflight_report(report_path).stream_events()
        quantity = 100
        result = MechanicalEventLoop().run("mechanical_abat_real_fixture_v0_1", events, self._decisions("ABAT", quantity))

        self.assertAlmostEqual(result.summary.entry_price, 3.87)
        self.assertAlmostEqual(result.summary.exit_price, 4.665)
        linear_reference = quantity * (3.87 - 4.665)
        self.assertAlmostEqual(result.summary.gross_pnl, linear_reference)
        self.assertAlmostEqual(result.ledger.final_position.realized_gross_pnl, linear_reference)
        self.assertEqual(result.summary.final_position_quantity, 0)
        self.assertTrue(result.summary.pnl_matches_reference)
        self.assertFalse(result.summary.execution_realism_claimed)
        self.assertFalse(result.summary.edge_evaluated)

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
            self._bar_event(ticker, open_start, open_price=entry_open, close_price=entry_open + 0.1),
            self._bar_event(ticker, close_start, open_price=exit_close - 0.1, close_price=exit_close),
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


if __name__ == "__main__":
    unittest.main()
