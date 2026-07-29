from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from tsis_backtest.backtest import (
    BacktestRunError,
    BacktestRunRequest,
    SingleStrategyEndToEndBacktestRunner,
    default_open_short_close_strategy,
)
from tsis_backtest.backtest.contracts import ENGINE_VALIDATION_RUN
from tsis_backtest.execution.contracts import CostModelV0
from tsis_backtest.preflight.real_data_inspector import sha256_file


class SingleStrategyEndToEndBacktestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="tsis_bt011_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_synthetic_end_to_end_short_path_reconciles(self) -> None:
        report_path = self._synthetic_preflight_report(
            {
                "AAA": ("10.00", "8.00"),
                "BBB": ("5.00", "6.00"),
            }
        )
        request = self._request("synthetic_e2e", report_path, ("AAA", "BBB"))

        result = SingleStrategyEndToEndBacktestRunner().run(request)

        self.assertEqual(result.summary.validation_status, "PASS")
        self.assertEqual(result.summary.run_purpose, ENGINE_VALIDATION_RUN)
        self.assertEqual(result.summary.order_count, 4)
        self.assertEqual(result.summary.fill_count, 4)
        self.assertEqual(result.summary.trade_count, 2)
        self.assertTrue(result.summary.final_position_all_zero)
        self.assertEqual(str(result.metrics.gross_pnl), "100.00")
        self.assertEqual(str(result.metrics.total_costs), "4.00")
        self.assertEqual(str(result.metrics.net_pnl), "96.00")
        self.assertEqual(str(result.metrics.ending_equity), "10096.00")
        self.assertNotIn("MECHANICAL_PROXY_FILL", str(result.to_dict()))
        self.assertEqual({fill.source_price_profile for fill in result.fills}, {"bar_based_execution_profile_v0_1"})

    def test_decision_and_order_timestamps_precede_source_bars(self) -> None:
        report_path = self._synthetic_preflight_report({"AAA": ("10.00", "8.00")})
        result = SingleStrategyEndToEndBacktestRunner().run(self._request("timestamps", report_path, ("AAA",)))

        for decision, order in zip(result.decisions, result.orders, strict=True):
            self.assertEqual(decision.decision_timestamp, order.order_submission_timestamp)
            self.assertLessEqual(order.order_submission_timestamp, order.eligible_source_bar_ts_start)
            self.assertLess(decision.information_cutoff, order.eligible_source_bar_available_at)

    def test_online_event_loop_trace_proves_no_future_event_access(self) -> None:
        report_path = self._synthetic_preflight_report({"AAA": ("10.00", "8.00")})

        result = SingleStrategyEndToEndBacktestRunner().run(self._request("online_trace", report_path, ("AAA",)))

        self.assertEqual(result.summary.event_loop_mode, "ONLINE_REPLAY_COORDINATOR_V0_1")
        self.assertEqual(result.summary.event_loop_trace_count, result.summary.order_count)
        self.assertFalse(result.summary.event_loop_future_event_access_detected)
        for trace in result.event_loop_trace:
            self.assertEqual(trace.simulator_event_count, 1)
            self.assertEqual(trace.max_replay_event_index_visible_to_simulator, trace.replay_event_index)
            self.assertLessEqual(trace.order_submission_timestamp, trace.source_bar_ts_start)
            self.assertLess(trace.decision_timestamp, trace.source_bar_available_at)
            self.assertTrue(trace.order_registered_before_replay_started)
            self.assertTrue(trace.order_registered_before_replay_event)
            self.assertEqual(trace.order_registration_replay_index, -1)
            self.assertEqual(trace.order_activation_timestamp, trace.order_submission_timestamp)
            self.assertEqual(trace.coordinator_clock_at_order_registration, trace.order_submission_timestamp)
            self.assertEqual(trace.eligible_replay_event_index, trace.replay_event_index)

    def test_accounting_is_applied_inside_event_loop(self) -> None:
        report_path = self._synthetic_preflight_report({"AAA": ("10.00", "8.00")})

        result = SingleStrategyEndToEndBacktestRunner().run(self._request("online_accounting", report_path, ("AAA",)))

        self.assertTrue(result.summary.accounting_applied_inside_event_loop)
        self.assertTrue(result.summary.orders_pre_registered_before_replay)
        self.assertEqual(len(result.equity_curve), len(result.event_loop_trace) + 1)
        for index, trace in enumerate(result.event_loop_trace, start=1):
            self.assertEqual(trace.accounting_applied_at_replay_event_index, trace.replay_event_index)
            self.assertEqual(result.equity_curve[index].timestamp, trace.event_available_at)
            self.assertEqual(result.equity_curve[index].cash, trace.cash_after_fill)
            self.assertEqual(result.equity_curve[index].equity, trace.equity_after_fill)

    def test_orders_are_registered_before_replay_not_at_target_event_discovery(self) -> None:
        report_path = self._synthetic_preflight_report({"AAA": ("10.00", "8.00")})

        result = SingleStrategyEndToEndBacktestRunner().run(self._request("pre_registered", report_path, ("AAA",)))

        for trace in result.event_loop_trace:
            self.assertTrue(trace.order_registered_before_replay_started)
            self.assertEqual(trace.order_registration_replay_index, -1)
            self.assertLess(trace.coordinator_clock_at_order_registration, trace.source_bar_ts_start)
            self.assertLess(trace.coordinator_clock_at_order_registration, trace.event_available_at)

    def test_truncated_dataset_does_not_silently_redefine_close(self) -> None:
        report_path = self._synthetic_preflight_report({"AAA": ("10.00", "8.00")}, include_close=False)

        with self.assertRaises(BacktestRunError) as ctx:
            SingleStrategyEndToEndBacktestRunner().run(self._request("truncated", report_path, ("AAA",)))

        self.assertEqual(ctx.exception.code, "BT011_REQUIRED_TARGET_EVENT_NOT_OBSERVED")
        self.assertIn("AAA:EXIT_CLOSE_LABEL", ctx.exception.message)

    def test_same_inputs_produce_same_semantic_hash_and_artifacts(self) -> None:
        report_path = self._synthetic_preflight_report({"AAA": ("10.00", "8.00")})
        runner = SingleStrategyEndToEndBacktestRunner()
        first = runner.run(self._request("hash_a", report_path, ("AAA",)))
        second = runner.run(self._request("hash_b", report_path, ("AAA",)))

        self.assertEqual(first.summary.deterministic_output_hash, second.summary.deterministic_output_hash)

        run_dir = runner.write_result(first)
        self.assertTrue((run_dir / "unified_run_manifest.json").exists())
        self.assertTrue((run_dir / "artifact_hashes.json").exists())
        self.assertTrue((run_dir / "validation_report.json").exists())
        self.assertTrue((run_dir / "event_loop_trace.json").exists())

    def test_real_fixture_qg5_end_to_end_smoke(self) -> None:
        report_path = Path("tests/fixtures/bt_gate_011_qg5_portable/data_preflight_report.json")
        symbols = ("ABAT", "ABEO", "ABSI", "ABTC", "ACB")
        request = self._request("real_qg5_smoke", report_path, symbols, fixture_id="TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1")

        result = SingleStrategyEndToEndBacktestRunner().run(request)

        self.assertEqual(result.summary.validation_status, "PASS")
        self.assertEqual(result.summary.symbol_count, 5)
        self.assertEqual(result.summary.order_count, 10)
        self.assertEqual(result.summary.fill_count, 10)
        self.assertEqual(result.summary.trade_count, 5)
        self.assertTrue(result.summary.final_position_all_zero)
        self.assertEqual(result.unified_run_manifest.state_provider_restrictions["StateReplayFeed"], "NOT_AUTHORIZED")
        self.assertTrue(result.summary.orders_pre_registered_before_replay)
        self.assertTrue(result.summary.accounting_applied_inside_event_loop)

    def _request(
        self,
        run_id: str,
        report_path: Path,
        symbols: tuple[str, ...],
        fixture_id: str = "SYNTHETIC_BT011_FIXTURE",
    ) -> BacktestRunRequest:
        return BacktestRunRequest(
            run_id=run_id,
            strategy_spec=default_open_short_close_strategy(symbols, quantity_per_symbol=100),
            preflight_report_path=report_path,
            output_root=self.root / "runs",
            fixture_id=fixture_id,
            session_date=date(2026, 1, 5),
            starting_equity=Decimal("10000.00"),
        )

    def _synthetic_preflight_report(self, prices_by_symbol: dict[str, tuple[str, str]], include_close: bool = True) -> Path:
        qg_file = self.root / "qg.parquet"
        rows = []
        for ticker, (open_price, close_price) in prices_by_symbol.items():
            rows.append(self._row(ticker, 0, open_price, open_price))
            if include_close:
                rows.append(self._row(ticker, 389, close_price, close_price))
        pq.write_table(pa.Table.from_pylist(rows), qg_file)
        report = {
            "resolved": True,
            "run_id": "synthetic_preflight",
            "dataset_id": "synthetic_qg",
            "fixture_kind": "NON_EMPIRICAL_TEST_FIXTURE",
            "context_resolution_status": "CONTEXT_RESOLVED",
            "physical_inspection_status": "PHYSICAL_INSPECTION_PASS",
            "preflight_status": "PREFLIGHT_PASS",
            "source_partitions_or_files_consumed": [str(qg_file)],
            "snapshot_or_content_hashes": {str(qg_file): sha256_file(qg_file)},
            "date_range": {"date_start": "2026-01-05", "date_end": "2026-01-05"},
            "session_policy": "REGULAR_ONLY",
            "timezone": "America/New_York",
            "calendar_id": "XNYS",
            "symbols_available": list(prices_by_symbol),
            "price_view_policy": {"signal": {"price_view": "quote_guarded_1m"}},
            "physical_inspection": {"warning_codes": [], "per_ticker_day_results": []},
        }
        report_path = self.root / "data_preflight_report.json"
        report_path.write_text(__import__("json").dumps(report, indent=2), encoding="utf-8")
        return report_path

    @staticmethod
    def _row(ticker: str, minute_offset: int, open_price: str, close_price: str) -> dict:
        ts = datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=minute_offset)
        return {
            "ticker": ticker,
            "ts_utc": ts.isoformat().replace("+00:00", "Z"),
            "o": float(open_price),
            "h": max(float(open_price), float(close_price)),
            "l": min(float(open_price), float(close_price)),
            "c": float(close_price),
            "v": 1000.0,
            "dataset_id": "synthetic_qg",
            "build_run_id": "synthetic_bt011",
            "quote_guarded_repair_applied": False,
            "repair_lookup_state": "indexed_no_repair_rows",
        }


if __name__ == "__main__":
    unittest.main()
