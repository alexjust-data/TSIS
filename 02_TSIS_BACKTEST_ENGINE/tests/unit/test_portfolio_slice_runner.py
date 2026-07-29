from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from tsis_backtest.backtest import BacktestRunError, default_open_short_close_strategy
from tsis_backtest.portfolio import PortfolioRunRequest, PortfolioSliceRunner


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "runs" / "bt_gate_012_multi_symbol_multi_session_qg5_v0_1.json"


class PortfolioSliceRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="tsis_bt012_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def test_portable_qg5_multi_session_portfolio_run_passes(self) -> None:
        result = PortfolioSliceRunner().run(self._request("bt012_smoke"))

        self.assertEqual(result.summary.validation_status, "PASS")
        self.assertEqual(result.summary.session_count, 2)
        self.assertEqual(result.summary.symbol_count, 5)
        self.assertEqual(result.summary.symbol_session_count, 10)
        self.assertEqual(result.summary.order_count, 20)
        self.assertEqual(result.summary.fill_count, 20)
        self.assertEqual(result.summary.trade_count, 10)
        self.assertTrue(result.summary.final_position_all_zero)
        self.assertEqual(str(result.metrics.gross_pnl), "-146.00")
        self.assertEqual(str(result.metrics.total_costs), "20.00")
        self.assertEqual(str(result.metrics.net_pnl), "-166.00")
        self.assertEqual(str(result.metrics.ending_equity), "9834.00")
        self.assertEqual(len(result.portfolio_equity_curve), result.summary.replay_event_count + 1)
        self.assertEqual(result.portfolio_run_manifest.state_provider_restrictions["StateReplayFeed"], "NOT_AUTHORIZED")

    def test_global_order_and_gap_policy_are_contractual(self) -> None:
        result = PortfolioSliceRunner().run(self._request("bt012_ordering"))
        keys = [record.order_key for record in result.event_sequence_manifest]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(len(keys), len(set(keys)))
        self.assertGreater(result.summary.replay_gap_count, 0)
        for trace in result.event_loop_trace:
            if trace.replay_event_type == "GAP":
                self.assertFalse(trace.replay_gap_supplied_execution_price)
                self.assertFalse(trace.replay_gap_triggered_fill)
                self.assertIsNone(trace.fill_id)
                self.assertIsNone(trace.order_id)
        paired = {}
        for record in result.event_sequence_manifest:
            key = (record.available_at_utc, record.session_date)
            paired.setdefault(key, []).append(record.event_type_priority)
        self.assertTrue(any(0 in values and 1 in values and sorted(values).index(0) < sorted(values).index(1) for values in paired.values()))

    def test_orders_are_pre_registered_and_accounting_is_online(self) -> None:
        result = PortfolioSliceRunner().run(self._request("bt012_event_loop"))
        fill_traces = [trace for trace in result.event_loop_trace if trace.order_id]
        self.assertEqual(len(fill_traces), result.summary.order_count)
        for trace in fill_traces:
            self.assertTrue(trace.order_registered_before_replay_started)
            self.assertTrue(trace.order_registered_before_replay_event)
            self.assertEqual(trace.order_registration_replay_index, -1)
            self.assertEqual(trace.eligible_replay_event_index, trace.replay_event_index)
            self.assertEqual(trace.simulator_event_count, 1)
            self.assertEqual(trace.max_replay_event_index_visible_to_simulator, trace.replay_event_index)
            self.assertEqual(trace.accounting_applied_at_replay_event_index, trace.replay_event_index)
        self.assertFalse(any(trace.order_id and not trace.order_registered_before_replay_started for trace in result.event_loop_trace))

    def test_session_results_and_portfolio_totals_reconcile(self) -> None:
        result = PortfolioSliceRunner().run(self._request("bt012_reconcile"))
        self.assertEqual(sum(row.trade_count for row in result.session_results), result.summary.trade_count)
        self.assertEqual(sum(row.fill_count for row in result.session_results), result.summary.fill_count)
        self.assertEqual(str(sum(row.gross_pnl for row in result.session_results)), str(result.metrics.gross_pnl))
        self.assertEqual(str(sum(row.total_costs for row in result.session_results)), str(result.metrics.total_costs))
        self.assertEqual(str(sum(row.net_pnl for row in result.session_results)), str(result.metrics.net_pnl))

    def test_same_inputs_produce_same_hash_and_outputs_can_be_written(self) -> None:
        runner = PortfolioSliceRunner()
        first = runner.run(self._request("bt012_hash"))
        second = runner.run(self._request("bt012_hash"))
        self.assertEqual(first.summary.deterministic_output_hash, second.summary.deterministic_output_hash)
        run_dir = runner.write_result(first, determinism_report={"status": "PASS"})
        for name in (
            "portfolio_run_manifest.json",
            "configuration_snapshot.json",
            "portfolio_strategy_spec.json",
            "event_sequence_manifest.json",
            "decisions.json",
            "order_intents.json",
            "orders.json",
            "fills.json",
            "event_loop_trace.json",
            "trade_ledger.json",
            "cash_ledger.json",
            "positions_by_symbol.json",
            "session_results.json",
            "portfolio_equity_curve.json",
            "session_calendar_snapshot.json",
            "metrics_summary.json",
            "validation_report.json",
            "determinism_report.json",
            "artifact_hashes.json",
        ):
            self.assertTrue((run_dir / name).exists(), name)

    def test_calendar_snapshot_hash_is_required(self) -> None:
        request = self._request("bt012_bad_calendar")
        bad = PortfolioRunRequest(
            request.run_id,
            request.strategy_spec,
            request.preflight_report_paths,
            request.output_root,
            request.fixture_id,
            request.session_dates,
            request.session_calendar_snapshot_path,
            "0" * 64,
            request.starting_equity,
            request.run_purpose,
            request.edge_evidence,
            request.economic_realism,
            request.strategy_optimization,
        )
        with self.assertRaises(BacktestRunError) as ctx:
            PortfolioSliceRunner().run(bad)
        self.assertEqual(ctx.exception.code, "BT012_SESSION_CALENDAR_SNAPSHOT_HASH_MISMATCH")

    def test_truncated_session_derivative_fails_full_run(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        calendar_path = self._calendar_with_missing_close()
        config["session_calendar_snapshot_path"] = str(calendar_path)
        config["session_calendar_snapshot_sha256"] = __import__("tsis_backtest.preflight.real_data_inspector", fromlist=["sha256_file"]).sha256_file(calendar_path)
        request = self._request("bt012_truncated", config=config)
        with self.assertRaises(BacktestRunError) as ctx:
            PortfolioSliceRunner().run(request)
        self.assertEqual(ctx.exception.code, "BT012_MISSING_CONTRACTUAL_CLOSE")

    def _request(self, run_id: str, config: dict | None = None) -> PortfolioRunRequest:
        config = dict(config or json.loads(CONFIG.read_text(encoding="utf-8")))
        symbols = tuple(config["symbols"])
        return PortfolioRunRequest(
            run_id=run_id,
            strategy_spec=default_open_short_close_strategy(symbols, quantity_per_symbol=int(config["quantity_per_symbol"])),
            preflight_report_paths=tuple(ROOT / path for path in config["preflight_report_paths"]),
            output_root=self.temp / "runs",
            fixture_id=config["fixture_id"],
            session_dates=tuple(date.fromisoformat(item) for item in config["session_dates"]),
            session_calendar_snapshot_path=ROOT / config["session_calendar_snapshot_path"],
            session_calendar_snapshot_sha256=config["session_calendar_snapshot_sha256"],
            starting_equity=Decimal(config["starting_equity"]),
            run_purpose=config["run_classification"]["RUN_PURPOSE"],
            edge_evidence=config["run_classification"]["EDGE_EVIDENCE"],
            economic_realism=config["run_classification"]["ECONOMIC_REALISM"],
            strategy_optimization=config["run_classification"]["STRATEGY_OPTIMIZATION"],
        )

    def _calendar_with_missing_close(self) -> Path:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        source = ROOT / config["session_calendar_snapshot_path"]
        payload = json.loads(source.read_text(encoding="utf-8"))
        for session in payload["sessions"]:
            if session["session_date"] == "2026-01-06":
                session["regular_close_utc"] = "2026-01-06T21:01:00Z"
        target = self.temp / "session_calendar_snapshot_missing_close.json"
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return target



if __name__ == "__main__":
    unittest.main()
