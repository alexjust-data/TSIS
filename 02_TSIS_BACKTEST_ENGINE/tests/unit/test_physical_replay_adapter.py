from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from tsis_backtest.backtest.contracts import canonical_hash
from tsis_backtest.physical_replay import (
    BT_GATE_013,
    PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
    PhysicalBarReplayAdapterV0_1,
    PhysicalHistoricalReplaySliceRunner,
    PhysicalReplayAdapterError,
    PhysicalReplaySliceRequest,
)
from tsis_backtest.preflight.real_data_inspector import sha256_file
from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayGapEvent

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "runs" / "bt_gate_013_physical_historical_replay_slice_v0_1.json"


class PhysicalReplayAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="tsis_bt013_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def test_adapter_builds_causal_replay_events_from_authorized_physical_identity(self) -> None:
        bundle = PhysicalBarReplayAdapterV0_1().build_bundle(_request())
        bars = [event for event in bundle.events if isinstance(event, ReplayBarEvent)]
        gaps = [event for event in bundle.events if isinstance(event, ReplayGapEvent)]
        self.assertEqual(len(bars), 3700)
        self.assertEqual(len(gaps), 200)
        self.assertEqual(len(bundle.events), 3900)
        self.assertEqual(bundle.adapter_manifest["source_table_id"], "013_ohlcv_1m_quote_guarded")
        self.assertEqual(bundle.adapter_manifest["fixture_manifest_validation"], "PASS")
        self.assertEqual(bundle.adapter_manifest["portable_fixture_manifest_sha256"], _config()["portable_fixture_manifest_sha256"])
        self.assertEqual(bundle.adapter_manifest["validation_manifest_sha256"], "7baf90cc64d382b66cf4bde6e434f1ec6a0656e51bec5d45945f36e4b7787ddf")
        self.assertEqual(bundle.adapter_manifest["selected_physical_row_count"], 3700)
        self.assertNotIn("vw", bundle.source_schema_binding["requested_columns"])
        first_bar = bars[0]
        self.assertEqual(first_bar.available_at, first_bar.bar.ts_end)
        self.assertEqual(first_bar.bar.available_at, first_bar.bar.ts_end)
        self.assertEqual(first_bar.physical_lineage["source_as_of_native_field"], "NONE")
        self.assertEqual(first_bar.physical_lineage["repair_fields_execution_input"], "PROHIBITED")
        self.assertEqual(first_bar.bar.quality_flags, ())
        self.assertIn("repair_lookup_state", first_bar.physical_lineage["repair_fields"])
        self.assertNotIn("inspection_location", first_bar.physical_lineage)
        for prefix in ("fixture_manifest", "validation_manifest", "calendar"):
            self.assertEqual(
                bundle.adapter_manifest[f"{prefix}_hash_before_read"],
                bundle.adapter_manifest[f"{prefix}_hash_after_read"],
            )
        locator = first_bar.physical_lineage["source_row_locator"]
        self.assertIn("source_file_sha256", locator)
        self.assertIn("parquet_row_group_index", locator)
        self.assertIn("row_index_within_row_group", locator)
        self.assertTrue(locator["zero_based"])
        self.assertTrue(all(gap.reason == "UNKNOWN_SOURCE_GAP" for gap in gaps))
        self.assertTrue(all(gap.available_at == gap.ts_end for gap in gaps))
        self.assertTrue(all(gap.physical_lineage["halt_inference"] == "NOT_AUTHORIZED" for gap in gaps))
        self.assertEqual({item["ticker"] for item in bundle.selected_physical_rows}, {"ABAT", "ABEO", "ABSI", "ABTC", "ACB"})

    def test_physical_runner_preserves_bt012_portfolio_semantics(self) -> None:
        config = _config()
        runner = PhysicalHistoricalReplaySliceRunner()
        result, bundle = runner.run(
            _request(),
            output_root=self.temp / "runs",
            starting_equity=Decimal(config["starting_equity"]),
            quantity_per_symbol=int(config["quantity_per_symbol"]),
        )
        repeat, _ = runner.run(
            _request(),
            output_root=self.temp / "runs",
            starting_equity=Decimal(config["starting_equity"]),
            quantity_per_symbol=int(config["quantity_per_symbol"]),
        )
        self.assertEqual(result.summary.gate_id, BT_GATE_013)
        self.assertEqual(result.summary.capability, PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1)
        self.assertEqual(result.summary.validation_status, "PASS")
        self.assertEqual(result.summary.session_count, 2)
        self.assertEqual(result.summary.symbol_count, 5)
        self.assertEqual(result.summary.symbol_session_count, 10)
        self.assertEqual(result.summary.replay_bar_count, 3700)
        self.assertEqual(result.summary.replay_gap_count, 200)
        self.assertEqual(result.summary.order_count, 20)
        self.assertEqual(result.summary.fill_count, 20)
        self.assertEqual(result.summary.trade_count, 10)
        self.assertTrue(result.summary.final_position_all_zero)
        self.assertEqual(result.summary.deterministic_output_hash, repeat.summary.deterministic_output_hash)
        self.assertEqual(result.portfolio_run_manifest.state_provider_restrictions["StateReplayFeed"], "NOT_AUTHORIZED")
        self.assertEqual(result.portfolio_run_manifest.accounting_policy["portfolio_valuation_price_field"], "close")
        self.assertGreater(len(bundle.row_to_event_lineage), 0)

    def test_write_result_includes_complete_manifest_and_executed_negative_evidence(self) -> None:
        config = _config()
        runner = PhysicalHistoricalReplaySliceRunner()
        result, bundle = runner.run(_request(run_id="bt013_write"), self.temp / "runs", Decimal(config["starting_equity"]), int(config["quantity_per_symbol"]))
        run_dir = runner.write_result(result, bundle, determinism_report={"status": "PASS"})
        for name in (
            "resolved_input_manifest.json",
            "source_file_inventory.json",
            "source_schema_binding.json",
            "selected_symbol_sessions.json",
            "selected_physical_rows.json",
            "row_to_event_lineage.json",
            "replay_bar_events.json",
            "replay_gap_events.json",
            "negative_derivative_report.json",
            "physical_replay_validation_report.json",
            "final_manifest.json",
        ):
            self.assertTrue((run_dir / name).exists(), name)
        negative = json.loads((run_dir / "negative_derivative_report.json").read_text(encoding="utf-8"))
        self.assertEqual(negative["status"], "PASS")
        self.assertEqual(negative["case_count"], 15)
        self.assertTrue(negative["report_generated_from_executions"])
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_01"], "FAIL_SOURCE_HASH_MISMATCH")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_02"], "FAIL_SOURCE_MUTATION")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_04"], "FAIL_DUPLICATE_PHYSICAL_BAR")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_05"], "FAIL_CONFLICTING_PHYSICAL_BAR")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_10"], "FAIL_MISSING_CONTRACTUAL_CLOSE")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_13"], "PASS_WITH_IDENTICAL_SCIENTIFIC_HASH")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_14"], "PASS_WITH_IDENTICAL_CANONICAL_EVENT_SEQUENCE")
        self.assertEqual(negative["executed_negative_derivatives"]["NEGATIVE_15"], "PASS_GAP_NO_PRICE_NO_FILL_NO_MARK_UPDATE")
        self.assertEqual(negative["supplemental_case_count"], 5)
        self.assertTrue(all(item["status"] == "PASS" for item in negative["supplemental_results"]))
        validation = json.loads((run_dir / "physical_replay_validation_report.json").read_text(encoding="utf-8"))
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(validation["boundary_preservation"]["StateReplayFeed"], "NOT_AUTHORIZED")
        final_manifest = json.loads((run_dir / "final_manifest.json").read_text(encoding="utf-8"))
        required = {
            "validation_manifest_relative_path",
            "validation_manifest_sha256",
            "calendar_relative_path",
            "calendar_sha256",
            "source_files",
            "timestamp_ranges",
            "available_at_ranges",
            "adapter_version",
            "engine_version",
            "strategy_version",
            "selected_rows_hash",
            "events_hash",
            "orders_hash",
            "fills_hash",
            "trades_hash",
            "ledger_hash",
            "equity_curve_hash",
            "manifest_hashes",
            "negative_test_aggregate_results",
        }
        self.assertTrue(required.issubset(final_manifest))
        self.assertEqual(len(final_manifest["source_files"]), 5)
        self.assertEqual(final_manifest["negative_test_aggregate_results"]["status"], "PASS")
        configuration_snapshot = json.loads((run_dir / "configuration_snapshot.json").read_text(encoding="utf-8"))
        self.assertEqual(configuration_snapshot["output_root"], "runs")
        self.assertEqual(configuration_snapshot["session_calendar_snapshot_path"], _config()["session_calendar_snapshot_relative"])
        self.assertFalse(Path(configuration_snapshot["output_root"]).is_absolute())
        self.assertFalse(Path(configuration_snapshot["session_calendar_snapshot_path"]).is_absolute())
        portfolio_manifest = json.loads((run_dir / "portfolio_run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(final_manifest["portfolio_run_manifest_hash"], canonical_hash(portfolio_manifest))
        self.assertEqual(final_manifest["manifest_hashes"]["portfolio_run_manifest_hash"], canonical_hash(portfolio_manifest))

    def test_scope_leakage_is_rejected(self) -> None:
        request = _request(symbols=("ABAT", "ABEO", "ABSI"))
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(request)
        self.assertEqual(ctx.exception.code, "FAIL_SCOPE_LEAKAGE")

    def test_calendar_hash_mismatch_is_rejected(self) -> None:
        request = _request(calendar_sha="0" * 64)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(request)
        self.assertEqual(ctx.exception.code, "FAIL_CALENDAR_HASH_MISMATCH")

    def test_fixture_manifest_hash_is_consumed(self) -> None:
        request = _request(fixture_sha="0" * 64)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(request)
        self.assertEqual(ctx.exception.code, "FAIL_SOURCE_HASH_MISMATCH")

    def test_preexisting_source_hash_mismatch_is_rejected(self) -> None:
        root = _copy_fixture_root(self.temp)
        path = _source_path(root, "ABAT")
        path.write_bytes(path.read_bytes() + b"x")
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(_request(physical_root=root))
        self.assertEqual(ctx.exception.code, "FAIL_SOURCE_HASH_MISMATCH")

    def test_validation_manifest_hash_mismatch_is_rejected(self) -> None:
        root = _copy_fixture_root(self.temp)
        validation_path = root / _config()["validation_manifest_path"].split("source_root/", 1)[1]
        validation_path.write_text(validation_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(_request(physical_root=root, validation_manifest_path=validation_path))
        self.assertEqual(ctx.exception.code, "FAIL_SOURCE_HASH_MISMATCH")

    def test_missing_schema_field_is_rejected_after_authorized_identity(self) -> None:
        root = _copy_fixture_root(self.temp)
        path = _source_path(root, "ABAT")
        table = pq.ParquetFile(path).read().drop(["ts_utc"])
        pq.write_table(table, path)
        request = _request(physical_root=root)
        request = _authorize_current_tree(self.temp, request, root)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(request)
        self.assertEqual(ctx.exception.code, "FAIL_SOURCE_SCHEMA_MISMATCH")

    def test_duplicate_and_conflicting_bars_are_distinct(self) -> None:
        duplicate_root = _copy_fixture_root(self.temp / "dupe")
        _append_row(duplicate_root, "ABAT", mutate=False)
        duplicate_request = _authorize_current_tree(self.temp / "dupe", _request(physical_root=duplicate_root), duplicate_root)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(duplicate_request)
        self.assertEqual(ctx.exception.code, "FAIL_DUPLICATE_PHYSICAL_BAR")

        conflict_root = _copy_fixture_root(self.temp / "conflict")
        _append_row(conflict_root, "ABAT", mutate=True)
        conflict_request = _authorize_current_tree(self.temp / "conflict", _request(physical_root=conflict_root), conflict_root)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx2:
            PhysicalBarReplayAdapterV0_1().build_bundle(conflict_request)
        self.assertEqual(ctx2.exception.code, "FAIL_CONFLICTING_PHYSICAL_BAR")

    def test_temporal_availability_violation_is_rejected(self) -> None:
        bundle = PhysicalBarReplayAdapterV0_1().build_bundle(_request())
        first = next(event for event in bundle.events if isinstance(event, ReplayBarEvent))
        bad = replace(first, available_at=first.bar.ts_start)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1.validate_temporal_availability((bad,))
        self.assertEqual(ctx.exception.code, "FAIL_TEMPORAL_AVAILABILITY_VIOLATION")

    def test_calendar_timezone_contract_is_rejected(self) -> None:
        calendar = self.temp / "calendar.json"
        payload = json.loads((ROOT / _config()["session_calendar_snapshot_path"]).read_text(encoding="utf-8"))
        payload["timezone"] = "UTC"
        calendar.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        request = _request(calendar_path=calendar, calendar_sha=sha256_file(calendar))
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(request)
        self.assertEqual(ctx.exception.code, "FAIL_CALENDAR_TIMEZONE_CONTRACT")

    def test_missing_contractual_close_fails_before_gap_imputation(self) -> None:
        root = _copy_fixture_root(self.temp)
        _remove_timestamp(root, "ABAT", "2026-01-06T20:59:00Z")
        request = _authorize_current_tree(self.temp, _request(physical_root=root), root)
        with self.assertRaises(PhysicalReplayAdapterError) as ctx:
            PhysicalBarReplayAdapterV0_1().build_bundle(request)
        self.assertEqual(ctx.exception.code, "FAIL_MISSING_CONTRACTUAL_CLOSE")


def _config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def _request(
    *,
    run_id: str = "bt013_test",
    symbols: tuple[str, ...] | None = None,
    calendar_sha: str | None = None,
    calendar_path: Path | None = None,
    fixture_sha: str | None = None,
    fixture_manifest_path: Path | None = None,
    validation_manifest_path: Path | None = None,
    physical_root: Path | None = None,
) -> PhysicalReplaySliceRequest:
    config = _config()
    return PhysicalReplaySliceRequest(
        run_id=run_id,
        physical_root=physical_root or ROOT / config["physical_root"],
        source_root_relative=config["source_root_relative"],
        validation_manifest_path=validation_manifest_path or ROOT / config["validation_manifest_path"],
        validation_manifest_relative=config["validation_manifest_relative"],
        portable_fixture_manifest_path=fixture_manifest_path or ROOT / config["portable_fixture_manifest_path"],
        portable_fixture_manifest_sha256=fixture_sha or config["portable_fixture_manifest_sha256"],
        session_calendar_snapshot_path=calendar_path or ROOT / config["session_calendar_snapshot_path"],
        session_calendar_snapshot_relative=config["session_calendar_snapshot_relative"],
        session_calendar_snapshot_sha256=calendar_sha or config["session_calendar_snapshot_sha256"],
        symbols=symbols or tuple(config["symbols"]),
        session_dates=tuple(date.fromisoformat(item) for item in config["session_dates"]),
        price_view=config.get("price_view", "quote_guarded_1m"),
    )


def _copy_fixture_root(temp: Path) -> Path:
    source = ROOT / "tests" / "fixtures" / "bt_gate_013_physical_qg5_slice" / "source_root"
    target = temp / "source_root"
    shutil.copytree(source, target)
    return target


def _source_path(root: Path, symbol: str) -> Path:
    return root / "year=2026" / f"ticker={symbol}" / "month=01" / "part-000.parquet"


def _authorize_current_tree(temp: Path, request: PhysicalReplaySliceRequest, root: Path) -> PhysicalReplaySliceRequest:
    manifest = json.loads((ROOT / _config()["portable_fixture_manifest_path"]).read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = root / Path(item["canonical_source_relative_path"]).relative_to(request.source_root_relative)
        item["sha256"] = sha256_file(path)
        item["size_bytes"] = path.stat().st_size
    validation_path = request.validation_manifest_path
    manifest["validation_manifest"]["sha256"] = sha256_file(validation_path)
    manifest["validation_manifest"]["size_bytes"] = validation_path.stat().st_size
    manifest_path = temp / "FIXTURE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return replace(request, portable_fixture_manifest_path=manifest_path, portable_fixture_manifest_sha256=sha256_file(manifest_path))


def _append_row(root: Path, symbol: str, *, mutate: bool) -> None:
    path = _source_path(root, symbol)
    table = pq.ParquetFile(path).read()
    rows = table.to_pylist()
    selected_index = next(index for index, row in enumerate(rows) if row["ts_utc"] == "2026-01-05T14:30:00Z")
    row = dict(rows[selected_index])
    if mutate:
        row["c"] = float(row["c"]) + 0.01
    pq.write_table(pa.concat_tables([table, pa.Table.from_pylist([row], schema=table.schema)]), path)


def _remove_timestamp(root: Path, symbol: str, timestamp: str) -> None:
    path = _source_path(root, symbol)
    table = pq.ParquetFile(path).read()
    keep = [not (row["ticker"] == symbol and row["ts_utc"] == timestamp) for row in table.to_pylist()]
    pq.write_table(table.filter(pa.array(keep)), path)


if __name__ == "__main__":
    unittest.main()
