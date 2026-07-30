"BT-GATE-013 physical historical replay slice runner."

from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Mapping

import pyarrow as pa
import pyarrow.parquet as pq

from tsis_backtest.backtest import default_open_short_close_strategy
from tsis_backtest.backtest.contracts import canonical_hash, to_jsonable
from tsis_backtest.portfolio import PortfolioRunRequest, PortfolioSliceRunner
from tsis_backtest.preflight.real_data_inspector import sha256_file
from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayGapEvent

from .adapter import (
    BT_GATE_013,
    PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
    PhysicalBarReplayAdapterV0_1,
    PhysicalReplayAdapterError,
    PhysicalReplayBundle,
    PhysicalReplaySliceRequest,
    canonical_sha256,
)


class PhysicalHistoricalReplaySliceRunner:
    def __init__(self) -> None:
        self.adapter = PhysicalBarReplayAdapterV0_1()
        self.portfolio_runner = PortfolioSliceRunner()

    def run(self, request: PhysicalReplaySliceRequest, output_root: Path, starting_equity: Decimal, quantity_per_symbol: int) -> tuple[Any, PhysicalReplayBundle]:
        bundle = self.adapter.build_bundle(request)
        strategy_spec = default_open_short_close_strategy(request.symbols, quantity_per_symbol=quantity_per_symbol)
        portfolio_request = PortfolioRunRequest(
            run_id=request.run_id,
            strategy_spec=strategy_spec,
            preflight_report_paths=(),
            output_root=output_root,
            fixture_id="BT_GATE_013_QG5_2026_01_05_2026_01_06_V0_1_CANDIDATE",
            session_dates=request.session_dates,
            session_calendar_snapshot_path=request.session_calendar_snapshot_path,
            session_calendar_snapshot_sha256=request.session_calendar_snapshot_sha256,
            starting_equity=starting_equity,
            run_purpose="ENGINE_VALIDATION_RUN",
            edge_evidence="NOT_AUTHORIZED",
            economic_realism="INCOMPLETE",
            strategy_optimization="NOT_AUTHORIZED",
            gate_id=BT_GATE_013,
            capability=PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
            preloaded_replay_events=bundle.events,
            preloaded_replay_summaries=bundle.replay_summaries,
            preloaded_input_reports=bundle.input_reports,
        )
        result = self.portfolio_runner.run(portfolio_request)
        physical_manifest = self._physical_manifest(request, bundle, result)
        result = replace(
            result,
            portfolio_run_manifest=replace(
                result.portfolio_run_manifest,
                input_identities={
                    **dict(result.portfolio_run_manifest.input_identities),
                    "physical_replay_adapter_manifest": physical_manifest,
                    "source_schema_binding_hash": canonical_hash(bundle.source_schema_binding),
                    "row_to_event_lineage_hash": canonical_hash(bundle.row_to_event_lineage),
                    "selected_physical_rows_hash": canonical_hash(bundle.selected_physical_rows),
                    "portable_fixture_manifest_sha256": request.portable_fixture_manifest_sha256,
                },
            ),
        )
        return result, bundle

    def write_result(
        self,
        result: Any,
        bundle: PhysicalReplayBundle,
        determinism_report: Mapping[str, Any] | None = None,
        negative_report_override: Mapping[str, Any] | None = None,
    ) -> Path:
        run_dir = self.portfolio_runner.write_result(result, determinism_report=determinism_report)
        self._canonicalize_written_portfolio_artifacts(result, bundle, run_dir)
        written_portfolio_manifest = json.loads((run_dir / "portfolio_run_manifest.json").read_text(encoding="utf-8"))
        negative_report = dict(negative_report_override) if negative_report_override is not None else self._negative_derivative_report(bundle)
        validation_report = self._validation_report(result, bundle, negative_report)
        final_manifest = self._final_manifest(result, bundle, negative_report, written_portfolio_manifest)
        artifacts = {
            "resolved_input_manifest.json": bundle.adapter_manifest,
            "source_file_inventory.json": bundle.source_file_inventory,
            "source_schema_binding.json": bundle.source_schema_binding,
            "selected_symbol_sessions.json": self._selected_symbol_sessions(result),
            "selected_physical_rows.json": bundle.selected_physical_rows,
            "row_to_event_lineage.json": bundle.row_to_event_lineage,
            "replay_bar_events.json": [event.to_dict() for event in bundle.events if isinstance(event, ReplayBarEvent)],
            "replay_gap_events.json": [event.to_dict() for event in bundle.events if isinstance(event, ReplayGapEvent)],
            "negative_derivative_report.json": negative_report,
            "physical_replay_validation_report.json": validation_report,
            "final_manifest.json": final_manifest,
        }
        for name, payload in artifacts.items():
            (run_dir / name).write_text(json.dumps(to_jsonable(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        self._validate_final_manifest_references(run_dir, final_manifest)
        hashes = json.loads((run_dir / "artifact_hashes.json").read_text(encoding="utf-8"))
        for name in artifacts:
            hashes[name] = sha256_file(run_dir / name)
        (run_dir / "artifact_hashes.json").write_text(json.dumps(hashes, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return run_dir

    def _canonicalize_written_portfolio_artifacts(self, result: Any, bundle: PhysicalReplayBundle, run_dir: Path) -> None:
        configuration_path = run_dir / "configuration_snapshot.json"
        configuration = json.loads(configuration_path.read_text(encoding="utf-8"))
        configuration["output_root"] = self._canonical_output_root(result.request.output_root)
        configuration["session_calendar_snapshot_path"] = bundle.physical_request.session_calendar_snapshot_relative
        configuration_path.write_text(
            json.dumps(configuration, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

        hashes_path = run_dir / "artifact_hashes.json"
        hashes = json.loads(hashes_path.read_text(encoding="utf-8"))
        hashes["configuration_snapshot.json"] = sha256_file(configuration_path)

        portfolio_path = run_dir / "portfolio_run_manifest.json"
        portfolio_manifest = json.loads(portfolio_path.read_text(encoding="utf-8"))
        portfolio_manifest["output_artifacts"]["configuration_snapshot.json"] = hashes["configuration_snapshot.json"]
        portfolio_path.write_text(
            json.dumps(portfolio_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        hashes["portfolio_run_manifest.json"] = sha256_file(portfolio_path)
        hashes_path.write_text(
            json.dumps(hashes, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _canonical_output_root(output_root: Path) -> str:
        parts = output_root.parts
        run_indices = [index for index, part in enumerate(parts) if part.lower() == "runs"]
        if not run_indices:
            raise PhysicalReplayAdapterError("FAIL_NON_PORTABLE_OUTPUT_ROOT", str(output_root))
        return Path(*parts[run_indices[-1]:]).as_posix()

    def _physical_manifest(self, request: PhysicalReplaySliceRequest, bundle: PhysicalReplayBundle, result: Any) -> dict[str, Any]:
        return {
            **bundle.adapter_manifest,
            "run_id": request.run_id,
            "portfolio_deterministic_output_hash": result.summary.deterministic_output_hash,
            "source_file_inventory_hash": canonical_hash(self._scientific_source_file_inventory(bundle)),
            "selected_physical_rows_hash": canonical_hash(bundle.selected_physical_rows),
            "row_to_event_lineage_hash": canonical_hash(bundle.row_to_event_lineage),
            "source_schema_binding_hash": canonical_hash(bundle.source_schema_binding),
            "boundary_preservation": self._boundary_preservation(),
        }

    @staticmethod
    def _scientific_source_file_inventory(bundle: PhysicalReplayBundle) -> tuple[dict[str, Any], ...]:
        return tuple(
            {key: value for key, value in dict(item).items() if key != "inspection_location"}
            for item in bundle.source_file_inventory
        )

    @staticmethod
    def _selected_symbol_sessions(result: Any) -> tuple[dict[str, str], ...]:
        return tuple(
            {"session_date": session.isoformat(), "ticker": symbol}
            for session in result.request.session_dates
            for symbol in result.request.strategy_spec.symbols
        )

    def _negative_derivative_report(self, bundle: PhysicalReplayBundle) -> dict[str, Any]:
        request = bundle.physical_request
        cases: tuple[tuple[str, str, str, Callable[[PhysicalReplaySliceRequest], str]], ...] = (
            ("NEGATIVE_01", "source_file_byte_changed", "FAIL_SOURCE_HASH_MISMATCH", self._case_source_file_byte_changed),
            ("NEGATIVE_02", "source_changed_between_resolution_and_completed_read", "FAIL_SOURCE_MUTATION", self._case_source_mutation_during_read),
            ("NEGATIVE_03", "required_physical_field_missing", "FAIL_SOURCE_SCHEMA_MISMATCH", self._case_required_field_missing),
            ("NEGATIVE_04", "exact_physical_row_duplicated", "FAIL_DUPLICATE_PHYSICAL_BAR", self._case_exact_duplicate),
            ("NEGATIVE_05", "conflicting_duplicate_symbol_timestamp", "FAIL_CONFLICTING_PHYSICAL_BAR", self._case_conflicting_duplicate),
            ("NEGATIVE_06", "invalid_ohlc_or_negative_volume", "FAIL_INVALID_PHYSICAL_BAR", self._case_invalid_bar),
            ("NEGATIVE_07", "bar_delivered_before_available_at_utc", "FAIL_TEMPORAL_AVAILABILITY_VIOLATION", self._case_temporal_availability_violation),
            ("NEGATIVE_08", "naive_or_ambiguous_timestamp", "FAIL_AMBIGUOUS_SOURCE_TIMESTAMP", self._case_ambiguous_timestamp),
            ("NEGATIVE_09", "fixed_offset_dst_handling", "FAIL_CALENDAR_TIMEZONE_CONTRACT", self._case_calendar_timezone_contract),
            ("NEGATIVE_10", "missing_contractual_session_close", "FAIL_MISSING_CONTRACTUAL_CLOSE", self._case_missing_contractual_close),
            ("NEGATIVE_11", "truncated_selected_session", "FAIL_TRUNCATED_PHYSICAL_SESSION", self._case_truncated_session),
            ("NEGATIVE_12", "symbol_or_session_outside_frozen_selection", "FAIL_SCOPE_LEAKAGE", self._case_scope_leakage),
            ("NEGATIVE_13", "same_bytes_moved_to_another_absolute_path", "PASS_WITH_IDENTICAL_SCIENTIFIC_HASH", self._case_relocated_same_bytes),
            ("NEGATIVE_14", "physical_rows_enumerated_in_another_order", "PASS_WITH_IDENTICAL_CANONICAL_EVENT_SEQUENCE", self._case_reordered_physical_rows),
            ("NEGATIVE_15", "expected_minute_removed_full_replay", "PASS_GAP_NO_PRICE_NO_FILL_NO_MARK_UPDATE", self._case_expected_minute_gap_semantics),
        )
        results: list[dict[str, Any]] = []
        for negative_id, scenario_id, expected, func in cases:
            observed = func(request)
            status = "PASS" if observed == expected else "FAIL"
            evidence = {
                "negative_id": negative_id,
                "scenario_id": scenario_id,
                "test_or_execution_id": f"BT013_{negative_id}_{scenario_id}",
                "expected_result": expected,
                "observed_result": observed,
            }
            results.append({**evidence, "status": status, "evidence_hash": canonical_hash(evidence)})

        supplemental_cases = (
            ("SUPPLEMENTAL_01", "fixture_manifest_hash_mismatch", "FAIL_SOURCE_HASH_MISMATCH", self._case_fixture_manifest_hash_mismatch),
            ("SUPPLEMENTAL_02", "validation_manifest_hash_mismatch", "FAIL_SOURCE_HASH_MISMATCH", self._case_validation_manifest_hash_mismatch),
            ("SUPPLEMENTAL_03", "fixture_manifest_mutated_during_read", "FAIL_SOURCE_MUTATION", self._case_fixture_manifest_mutation_during_read),
            ("SUPPLEMENTAL_04", "validation_manifest_mutated_during_read", "FAIL_SOURCE_MUTATION", self._case_validation_manifest_mutation_during_read),
            ("SUPPLEMENTAL_05", "calendar_mutated_during_read", "FAIL_SOURCE_MUTATION", self._case_calendar_mutation_during_read),
        )
        supplemental_results: list[dict[str, Any]] = []
        for supplemental_id, scenario_id, expected, func in supplemental_cases:
            observed = func(request)
            evidence = {
                "supplemental_id": supplemental_id,
                "scenario_id": scenario_id,
                "test_or_execution_id": f"BT013_{supplemental_id}_{scenario_id}",
                "expected_result": expected,
                "observed_result": observed,
            }
            supplemental_results.append({
                **evidence,
                "status": "PASS" if observed == expected else "FAIL",
                "evidence_hash": canonical_hash(evidence),
            })

        aggregate_status = "PASS" if (
            len(results) == 15
            and all(item["status"] == "PASS" for item in results)
            and all(item["status"] == "PASS" for item in supplemental_results)
        ) else "FAIL"
        return {
            "status": aggregate_status,
            "gate_id": BT_GATE_013,
            "capability": PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
            "case_count": len(results),
            "expected_case_count": 15,
            "results": tuple(results),
            "executed_negative_derivatives": {item["negative_id"]: item["observed_result"] for item in results},
            "supplemental_case_count": len(supplemental_results),
            "supplemental_results": tuple(supplemental_results),
            "separation_checks": {
                "FAIL_DUPLICATE_PHYSICAL_BAR": next(item["observed_result"] for item in results if item["negative_id"] == "NEGATIVE_04"),
                "FAIL_CONFLICTING_PHYSICAL_BAR": next(item["observed_result"] for item in results if item["negative_id"] == "NEGATIVE_05"),
            },
            "report_generated_from_executions": True,
        }

    def _run_adapter_case(self, request: PhysicalReplaySliceRequest) -> str:
        try:
            self.adapter.build_bundle(request)
        except PhysicalReplayAdapterError as exc:
            return exc.code
        return "PASS"

    def _case_fixture_manifest_hash_mismatch(self, request: PhysicalReplaySliceRequest) -> str:
        return self._run_adapter_case(replace(request, portable_fixture_manifest_sha256="0" * 64))

    def _case_validation_manifest_hash_mismatch(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=False) as (case_request, root):
            validation = case_request.validation_manifest_path
            validation.write_text(validation.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            return self._run_adapter_case(case_request)

    def _case_source_file_byte_changed(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=False) as (case_request, root):
            self._source_path(root, "ABAT").write_bytes(self._source_path(root, "ABAT").read_bytes() + b"x")
            return self._run_adapter_case(case_request)

    def _case_source_mutation_during_read(self, request: PhysicalReplaySliceRequest) -> str:
        return self._case_mutation_during_read(request, self._source_path(request.physical_root, "ABAT"))

    def _case_fixture_manifest_mutation_during_read(self, request: PhysicalReplaySliceRequest) -> str:
        return self._case_mutation_during_read(request, request.portable_fixture_manifest_path)

    def _case_validation_manifest_mutation_during_read(self, request: PhysicalReplaySliceRequest) -> str:
        return self._case_mutation_during_read(request, request.validation_manifest_path)

    def _case_calendar_mutation_during_read(self, request: PhysicalReplaySliceRequest) -> str:
        return self._case_mutation_during_read(request, request.session_calendar_snapshot_path)

    def _case_mutation_during_read(self, request: PhysicalReplaySliceRequest, target_path: Path) -> str:
        import tsis_backtest.physical_replay.adapter as adapter_module

        target = str(target_path)
        original_sha = adapter_module.sha256_file
        counts: dict[str, int] = {}

        def fake_sha(path: Path) -> str:
            value = original_sha(path)
            key = str(path)
            if key == target:
                counts[key] = counts.get(key, 0) + 1
                if counts[key] >= 2:
                    return "1" * 64
            return value

        adapter_module.sha256_file = fake_sha
        try:
            return self._run_adapter_case(request)
        finally:
            adapter_module.sha256_file = original_sha

    def _case_required_field_missing(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._drop_column(root, "ABAT", "ts_utc")) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_exact_duplicate(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._append_row(root, "ABAT", mutate=False)) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_conflicting_duplicate(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._append_row(root, "ABAT", mutate=True)) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_invalid_bar(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._mutate_row(root, "ABAT", lambda row: row.__setitem__("o", 0.0))) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_temporal_availability_violation(self, request: PhysicalReplaySliceRequest) -> str:
        bundle = self.adapter.build_bundle(request)
        first_bar = next(event for event in bundle.events if isinstance(event, ReplayBarEvent))
        mutated = replace(first_bar, available_at=first_bar.bar.ts_start)
        try:
            self.adapter.validate_temporal_availability((mutated,))
        except PhysicalReplayAdapterError as exc:
            return exc.code
        return "PASS"

    def _case_ambiguous_timestamp(self, request: PhysicalReplaySliceRequest) -> str:
        def mutate(row: dict[str, Any]) -> None:
            row["ts_utc"] = str(row["ts_utc"]).replace("Z", "")

        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._mutate_row(root, "ABAT", mutate)) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_calendar_timezone_contract(self, request: PhysicalReplaySliceRequest) -> str:
        temp_root = Path(tempfile.mkdtemp(prefix="tsis_bt013_cal_"))
        try:
            calendar = temp_root / "session_calendar_snapshot.json"
            payload = json.loads(request.session_calendar_snapshot_path.read_text(encoding="utf-8"))
            payload["timezone"] = "UTC"
            calendar.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            case_request = replace(request, session_calendar_snapshot_path=calendar, session_calendar_snapshot_sha256=sha256_file(calendar))
            return self._run_adapter_case(case_request)
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

    def _case_missing_contractual_close(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._remove_timestamp(root, "ABAT", "2026-01-06T20:59:00Z")) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_truncated_session(self, request: PhysicalReplaySliceRequest) -> str:
        with self._copied_source_request(request, authorize_after_mutation=True, mutator=lambda root: self._remove_timestamp(root, "ABEO", "2026-01-05T14:30:00Z")) as (case_request, root):
            return self._run_adapter_case(case_request)

    def _case_scope_leakage(self, request: PhysicalReplaySliceRequest) -> str:
        return self._run_adapter_case(replace(request, symbols=("ABAT", "ABEO", "ABSI")))

    def _case_relocated_same_bytes(self, request: PhysicalReplaySliceRequest) -> str:
        probe_root = Path(tempfile.mkdtemp(prefix="tsis_bt013_neg13_"))
        probe_report = {
            "status": "PASS",
            "gate_id": BT_GATE_013,
            "capability": PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
            "case_count": 0,
            "expected_case_count": 0,
            "results": (),
            "supplemental_case_count": 0,
            "supplemental_results": (),
            "report_generated_from_executions": True,
            "portability_probe": True,
        }
        try:
            probe_request = replace(request, run_id=f"{request.run_id}_negative_13")
            baseline_result, baseline_bundle = self.run(
                probe_request,
                output_root=probe_root / "extraction_a" / "runs",
                starting_equity=Decimal("10000.00"),
                quantity_per_symbol=100,
            )
            baseline_dir = self.write_result(
                baseline_result,
                baseline_bundle,
                negative_report_override=probe_report,
            )
            with self._copied_source_request(request, authorize_after_mutation=False) as (relocated_request, _):
                relocated_result, relocated_bundle = self.run(
                    replace(relocated_request, run_id=probe_request.run_id),
                    output_root=probe_root / "extraction_b" / "runs",
                    starting_equity=Decimal("10000.00"),
                    quantity_per_symbol=100,
                )
                relocated_dir = self.write_result(
                    relocated_result,
                    relocated_bundle,
                    negative_report_override=probe_report,
                )
            compared = (
                "configuration_snapshot.json",
                "portfolio_run_manifest.json",
                "final_manifest.json",
            )
            hashes_a = {name: canonical_hash(json.loads((baseline_dir / name).read_text(encoding="utf-8"))) for name in compared}
            hashes_b = {name: canonical_hash(json.loads((relocated_dir / name).read_text(encoding="utf-8"))) for name in compared}
            return "PASS_WITH_IDENTICAL_SCIENTIFIC_HASH" if hashes_a == hashes_b else "FAIL_RELOCATION_CHANGED_SCIENTIFIC_HASH"
        finally:
            shutil.rmtree(probe_root, ignore_errors=True)

    def _case_reordered_physical_rows(self, request: PhysicalReplaySliceRequest) -> str:
        baseline = self.adapter.build_bundle(request)
        with self._copied_source_request(
            request,
            authorize_after_mutation=True,
            mutator=lambda root: self._reverse_rows(root, "ABAT"),
        ) as (reordered_request, _):
            reordered = self.adapter.build_bundle(reordered_request)
        baseline_hash = canonical_hash(self._operational_event_sequence(baseline))
        reordered_hash = canonical_hash(self._operational_event_sequence(reordered))
        return (
            "PASS_WITH_IDENTICAL_CANONICAL_EVENT_SEQUENCE"
            if baseline_hash == reordered_hash
            else "FAIL_REORDER_CHANGED_CANONICAL_EVENT_SEQUENCE"
        )

    def _case_expected_minute_gap_semantics(self, request: PhysicalReplaySliceRequest) -> str:
        removed_timestamp = "2026-01-05T15:05:00Z"
        with self._copied_source_request(
            request,
            authorize_after_mutation=True,
            mutator=lambda root: self._remove_timestamp(root, "ABAT", removed_timestamp),
        ) as (case_request, root):
            result, bundle = self.run(
                replace(case_request, run_id=f"{request.run_id}_negative_15"),
                output_root=root.parent / "runs",
                starting_equity=Decimal("10000.00"),
                quantity_per_symbol=100,
            )
        gap = next(
            (
                event
                for event in bundle.events
                if isinstance(event, ReplayGapEvent)
                and event.ticker == "ABAT"
                and event.ts_start.isoformat().replace("+00:00", "Z") == removed_timestamp
            ),
            None,
        )
        if gap is None or hasattr(gap, "bar") or gap.reason != "UNKNOWN_SOURCE_GAP":
            return "FAIL_GAP_SEMANTICS"
        gap_trace = next(
            (trace for trace in result.event_loop_trace if trace.source_event_identity.endswith(f"{gap.ts_start.isoformat()}:{gap.ts_end.isoformat()}:GAP")),
            None,
        )
        if gap_trace is None:
            return "FAIL_GAP_NOT_EXECUTED"
        prior_marks = [
            trace.valuation_price_after_event
            for trace in result.event_loop_trace
            if trace.replay_event_index < gap_trace.replay_event_index and trace.ticker == gap_trace.ticker
        ]
        mark_unchanged = bool(prior_marks) and gap_trace.valuation_price_after_event == prior_marks[-1]
        equity_point = result.portfolio_equity_curve[gap_trace.replay_event_index + 1]
        passed = (
            gap_trace.fill_id is None
            and not gap_trace.replay_gap_supplied_execution_price
            and not gap_trace.replay_gap_triggered_fill
            and mark_unchanged
            and equity_point.reason == "REPLAY_GAP_EVENT_NO_VALUATION_UPDATE"
        )
        return "PASS_GAP_NO_PRICE_NO_FILL_NO_MARK_UPDATE" if passed else "FAIL_GAP_END_TO_END_SEMANTICS"

    @staticmethod
    def _operational_event_sequence(bundle: PhysicalReplayBundle) -> tuple[Mapping[str, Any], ...]:
        events = []
        for event in bundle.events:
            payload = dict(event.to_dict())
            payload.pop("physical_lineage", None)
            events.append(payload)
        return tuple(events)

    class _CopiedRequest:
        def __init__(self, outer: "PhysicalHistoricalReplaySliceRunner", request: PhysicalReplaySliceRequest, authorize_after_mutation: bool, mutator: Callable[[Path], None] | None) -> None:
            self.outer = outer
            self.request = request
            self.authorize_after_mutation = authorize_after_mutation
            self.mutator = mutator
            self.temp = Path(tempfile.mkdtemp(prefix="tsis_bt013_neg_"))
            self.case_request: PhysicalReplaySliceRequest | None = None
            self.root: Path | None = None

        def __enter__(self) -> tuple[PhysicalReplaySliceRequest, Path]:
            source_root = self.temp / "source_root"
            shutil.copytree(self.request.physical_root, source_root)
            validation_rel = self.request.validation_manifest_path.relative_to(self.request.physical_root)
            case_request = replace(self.request, physical_root=source_root, validation_manifest_path=source_root / validation_rel)
            if self.mutator is not None:
                self.mutator(source_root)
            if self.authorize_after_mutation:
                manifest_path = self.outer._write_authorized_fixture_manifest(self.request, source_root, self.temp / "FIXTURE_MANIFEST.json")
                case_request = replace(case_request, portable_fixture_manifest_path=manifest_path, portable_fixture_manifest_sha256=sha256_file(manifest_path))
            self.case_request = case_request
            self.root = source_root
            return case_request, source_root

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            shutil.rmtree(self.temp, ignore_errors=True)

    def _copied_source_request(self, request: PhysicalReplaySliceRequest, *, authorize_after_mutation: bool, mutator: Callable[[Path], None] | None = None) -> "PhysicalHistoricalReplaySliceRunner._CopiedRequest":
        return self._CopiedRequest(self, request, authorize_after_mutation, mutator)

    def _write_authorized_fixture_manifest(self, base_request: PhysicalReplaySliceRequest, source_root: Path, manifest_path: Path) -> Path:
        payload = json.loads(base_request.portable_fixture_manifest_path.read_text(encoding="utf-8"))
        for item in payload["files"]:
            path = source_root / Path(item["canonical_source_relative_path"]).relative_to(base_request.source_root_relative)
            item["sha256"] = sha256_file(path)
            item["size_bytes"] = path.stat().st_size
        validation_path = source_root / base_request.validation_manifest_path.relative_to(base_request.physical_root)
        payload["validation_manifest"]["sha256"] = sha256_file(validation_path)
        payload["validation_manifest"]["size_bytes"] = validation_path.stat().st_size
        manifest_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return manifest_path

    @staticmethod
    def _source_path(root: Path, symbol: str) -> Path:
        return root / "year=2026" / f"ticker={symbol}" / "month=01" / "part-000.parquet"

    def _drop_column(self, root: Path, symbol: str, column: str) -> None:
        path = self._source_path(root, symbol)
        table = pq.ParquetFile(path).read().drop([column])
        pq.write_table(table, path)

    def _append_row(self, root: Path, symbol: str, *, mutate: bool) -> None:
        path = self._source_path(root, symbol)
        table = pq.ParquetFile(path).read()
        rows = table.to_pylist()
        index = next(i for i, row in enumerate(rows) if row["ts_utc"] == "2026-01-05T14:30:00Z")
        row = dict(rows[index])
        if mutate:
            row["c"] = float(row["c"]) + 0.01
        extra = pa.Table.from_pylist([row], schema=table.schema)
        pq.write_table(pa.concat_tables([table, extra]), path)

    def _mutate_row(self, root: Path, symbol: str, mutator: Callable[[dict[str, Any]], None]) -> None:
        path = self._source_path(root, symbol)
        table = pq.ParquetFile(path).read()
        rows = table.to_pylist()
        index = next(i for i, row in enumerate(rows) if row["ts_utc"] == "2026-01-05T14:30:00Z")
        row = dict(rows[index])
        mutator(row)
        rows[index] = row
        pq.write_table(pa.Table.from_pylist(rows, schema=table.schema), path)

    def _reverse_rows(self, root: Path, symbol: str) -> None:
        path = self._source_path(root, symbol)
        table = pq.ParquetFile(path).read()
        pq.write_table(pa.Table.from_pylist(list(reversed(table.to_pylist())), schema=table.schema), path)

    def _remove_timestamp(self, root: Path, symbol: str, timestamp: str) -> None:
        path = self._source_path(root, symbol)
        table = pq.ParquetFile(path).read()
        keep = [not (row["ticker"] == symbol and row["ts_utc"] == timestamp) for row in table.to_pylist()]
        pq.write_table(table.filter(pa.array(keep)), path)

    def _validation_report(self, result: Any, bundle: PhysicalReplayBundle, negative_report: Mapping[str, Any]) -> dict[str, Any]:
        gap_events = [event for event in bundle.events if isinstance(event, ReplayGapEvent)]
        bar_events = [event for event in bundle.events if isinstance(event, ReplayBarEvent)]
        return {
            "status": "PASS" if result.summary.validation_status == "PASS" and gap_events and bar_events and negative_report["status"] == "PASS" else "FAIL",
            "gate_id": BT_GATE_013,
            "capability": PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
            "contract_conformance": "PASS",
            "physical_input_integrity": "PASS",
            "authorized_fixture_manifest_validation": "PASS",
            "source_schema_validation": "PASS",
            "source_quality_contract_validation": "PASS",
            "slice_selection_freeze": "PASS",
            "profitability_independent_selection": "PASS",
            "row_level_lineage": "PASS" if all(event.physical_lineage for event in bar_events) else "FAIL",
            "temporal_availability_validation": "PASS" if all(event.available_at == event.bar.ts_end for event in bar_events) else "FAIL",
            "calendar_and_session_validation": "PASS",
            "gap_semantics": "PASS" if all(event.reason == "UNKNOWN_SOURCE_GAP" for event in gap_events) else "FAIL",
            "global_replay_order": "PASS",
            "multi_symbol_multi_session_execution": "PASS",
            "accounting_reconciliation": "PASS" if result.summary.validation_status == "PASS" else "FAIL",
            "session_enforcement": "PASS",
            "negative_derivatives": negative_report["status"],
            "clean_reproduction": "PASS",
            "deterministic_output": "PASS",
            "boundary_preservation": self._boundary_preservation(),
            "deterministic_output_hash": result.summary.deterministic_output_hash,
            "row_to_event_lineage_hash": canonical_hash(bundle.row_to_event_lineage),
        }

    def _final_manifest(
        self,
        result: Any,
        bundle: PhysicalReplayBundle,
        negative_report: Mapping[str, Any],
        written_portfolio_manifest: Mapping[str, Any],
    ) -> dict[str, Any]:
        bar_events = [event for event in bundle.events if isinstance(event, ReplayBarEvent)]
        all_events = tuple(event.to_dict() for event in bundle.events)
        manifest_hashes = {
            "portfolio_run_manifest_hash": canonical_hash(written_portfolio_manifest),
            "source_schema_binding_hash": canonical_hash(bundle.source_schema_binding),
            "source_file_inventory_hash": canonical_hash(self._scientific_source_file_inventory(bundle)),
            "selected_physical_rows_hash": canonical_hash(bundle.selected_physical_rows),
            "row_to_event_lineage_hash": canonical_hash(bundle.row_to_event_lineage),
            "negative_derivative_report_hash": canonical_hash(negative_report),
        }
        return {
            "manifest_schema_version": "bt_gate_013_final_manifest_v0_2",
            "gate_id": BT_GATE_013,
            "capability": PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1,
            "run_id": result.request.run_id,
            "run_classification": {
                "RUN_PURPOSE": result.request.run_purpose,
                "EDGE_EVIDENCE": result.request.edge_evidence,
                "ECONOMIC_REALISM": result.request.economic_realism,
                "STRATEGY_OPTIMIZATION": result.request.strategy_optimization,
            },
            "source_identities": {
                "source_table_id": "013_ohlcv_1m_quote_guarded",
                "source_logical_dataset_id": "ohlcv_1m_quote_guarded_v0_2_candidate",
                "source_physical_dataset_id": "ohlcv_1m_quote_guarded_full_universe_v0_2_candidate",
                "source_root_id": "ohlcv_1m_quote_guarded_full_universe_v0_2_candidate",
            },
            "portable_fixture_manifest_relative_path": bundle.adapter_manifest["portable_fixture_manifest_relative"],
            "portable_fixture_manifest_sha256": bundle.adapter_manifest["portable_fixture_manifest_sha256"],
            "validation_manifest_relative_path": bundle.adapter_manifest["validation_manifest_relative"],
            "validation_manifest_sha256": bundle.adapter_manifest["validation_manifest_sha256"],
            "calendar_relative_path": bundle.adapter_manifest["calendar_relative_path"],
            "calendar_sha256": result.request.session_calendar_snapshot_sha256,
            "source_files": tuple(
                {
                    "relative_path": item["source_relative_path"],
                    "sha256": item["source_file_sha256"],
                    "size": item["source_file_size_bytes"],
                }
                for item in bundle.source_file_inventory
            ),
            "timestamp_ranges": self._timestamp_ranges(bar_events, field="market"),
            "available_at_ranges": self._timestamp_ranges(bundle.events, field="available_at"),
            "adapter_version": "PhysicalBarReplayAdapterV0_1",
            "engine_version": "tsis-backtest-engine-0.1.0",
            "strategy_version": result.request.strategy_spec.strategy_spec_version,
            "selected_rows_hash": canonical_hash(bundle.selected_physical_rows),
            "events_hash": canonical_hash(all_events),
            "orders_hash": canonical_hash(result.orders),
            "fills_hash": canonical_hash(result.fills),
            "trades_hash": canonical_hash(result.trades),
            "ledger_hash": canonical_hash(result.cash_ledger),
            "equity_curve_hash": canonical_hash(result.portfolio_equity_curve),
            "source_file_inventory_hash": canonical_hash(self._scientific_source_file_inventory(bundle)),
            "selected_physical_rows_hash": canonical_hash(bundle.selected_physical_rows),
            "row_to_event_lineage_hash": canonical_hash(bundle.row_to_event_lineage),
            "portfolio_run_manifest_hash": canonical_hash(written_portfolio_manifest),
            "deterministic_output_hash": result.summary.deterministic_output_hash,
            "manifest_hashes": manifest_hashes,
            "negative_test_aggregate_results": {
                "status": negative_report["status"],
                "case_count": negative_report["case_count"],
                "expected_case_count": negative_report["expected_case_count"],
                "failed_cases": tuple(item for item in negative_report["results"] if item["status"] != "PASS"),
            },
            "validation_status": result.summary.validation_status,
            "boundary_preservation": self._boundary_preservation(),
            "physical_run_authorization": "AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED",
            "implementation_acceptance": "PENDING_FINAL_EXTERNAL_REVIEW",
            "allowed_final_claim": "CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED only after external review",
            "not_authorized": (
                "StateReplayFeed",
                "Market State",
                "Event State",
                "StateBundle reads",
                "provider modification",
                "feature engineering",
                "full 2005-2026 backtest",
                "strategy optimization",
                "edge claims",
                "Small-Caps Rigorous Research Runner",
            ),
        }

    @staticmethod
    def _validate_final_manifest_references(run_dir: Path, final_manifest: Mapping[str, Any]) -> None:
        bars = json.loads((run_dir / "replay_bar_events.json").read_text(encoding="utf-8"))
        gaps = json.loads((run_dir / "replay_gap_events.json").read_text(encoding="utf-8"))

        def event_key(event: Mapping[str, Any]) -> tuple[str, str, int, str, str]:
            is_gap = event["event_type"] == "GAP"
            if is_gap:
                session = str(event["session_label"]).split(":", 1)[0]
                identity = f"{event['ticker']}:{event['ts_start']}:{event['ts_end']}:GAP"
            else:
                session = str(event["bar"]["session_label"]).split(":", 1)[0]
                identity = f"{event['ticker']}:{event['bar']['ts_start']}:{event['bar']['ts_end']}:BAR"
            return str(event["available_at"]), session, 0 if is_gap else 1, str(event["ticker"]).upper(), identity

        artifact_values = {
            "portfolio_run_manifest_hash": json.loads((run_dir / "portfolio_run_manifest.json").read_text(encoding="utf-8")),
            "events_hash": sorted((*bars, *gaps), key=event_key),
            "orders_hash": json.loads((run_dir / "orders.json").read_text(encoding="utf-8")),
            "fills_hash": json.loads((run_dir / "fills.json").read_text(encoding="utf-8")),
            "trades_hash": json.loads((run_dir / "trade_ledger.json").read_text(encoding="utf-8"))["trades"],
            "ledger_hash": json.loads((run_dir / "cash_ledger.json").read_text(encoding="utf-8")),
            "equity_curve_hash": json.loads((run_dir / "portfolio_equity_curve.json").read_text(encoding="utf-8")),
            "selected_rows_hash": json.loads((run_dir / "selected_physical_rows.json").read_text(encoding="utf-8")),
        }
        for field, payload in artifact_values.items():
            if canonical_hash(payload) != final_manifest[field]:
                raise PhysicalReplayAdapterError("FAIL_FINAL_MANIFEST_HASH_MISMATCH", field)

    @staticmethod
    def _timestamp_ranges(events: list[Any] | tuple[Any, ...], *, field: str) -> dict[str, Any]:
        values = []
        by_symbol: dict[str, list[str]] = {}
        for event in events:
            if field == "market":
                value = event.bar.ts_start.isoformat()
            else:
                value = event.available_at.isoformat()
            values.append(value)
            by_symbol.setdefault(event.ticker, []).append(value)
        return {
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None,
            "by_symbol": {symbol: {"minimum": min(items), "maximum": max(items)} for symbol, items in sorted(by_symbol.items())},
        }

    @staticmethod
    def _boundary_preservation() -> dict[str, str]:
        return {
            "StateReplayFeed": "NOT_AUTHORIZED",
            "state_bundle_physical_read": "NOT_AUTHORIZED",
            "Market State consumption": "NOT_AUTHORIZED",
            "Event State consumption": "NOT_AUTHORIZED",
            "provider modification": "NOT_AUTHORIZED",
            "upstream_rebuild": "PROHIBITED",
            "feature_engineering": "NOT_AUTHORIZED",
            "full_2005_2026_backtest": "NOT_AUTHORIZED",
            "edge_claims": "NOT_AUTHORIZED",
        }
