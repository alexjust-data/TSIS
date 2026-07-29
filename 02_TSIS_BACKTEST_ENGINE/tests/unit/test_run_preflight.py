from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tsis_backtest.preflight.contracts import (  # noqa: E402
    CandidateConsumptionPolicy,
    CorporateActionPolicy,
    DatasetDefinition,
    MarketDataBar1m,
    MissingDataPolicy,
    PriceViewAuthorization,
    RunDataRequest,
    TSIS_REAL_DATA_FIXTURE,
    UniverseDefinition,
)
from tsis_backtest.preflight.registries import DatasetRegistry, UniverseRegistry  # noqa: E402
from tsis_backtest.preflight.run_preflight import RunPreflight  # noqa: E402


_UNSET = object()


class RunPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dataset_root = self.root / "dataset"
        self.dataset_root.mkdir()
        self.output_root = self.root / "out"
        self.run_id = "run_preflight_synthetic_v0_1"
        self.run_output_root = self.output_root / self.run_id
        self.validation_manifest = self.root / "validation_manifest.json"
        self.validation_manifest.write_text("{}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_unknown_dataset_fails_closed(self) -> None:
        preflight = self._preflight(datasets={})

        report = preflight.run(self._request(dataset_id="missing_dataset"))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "DATASET_NOT_FOUND")

    def test_dataset_root_missing_fails_closed(self) -> None:
        dataset = self._dataset(physical_root=self.root / "missing_dataset_root")
        preflight = self._preflight(dataset=dataset)

        report = preflight.run(self._request())

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "DATASET_ROOT_NOT_FOUND")

    def test_invalid_date_range_fails_closed(self) -> None:
        preflight = self._preflight()

        report = preflight.run(self._request(date_start=date(2026, 1, 6), date_end=date(2026, 1, 5)))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "INVALID_DATE_RANGE")

    def test_invalid_run_id_fails_closed_before_writing(self) -> None:
        preflight = self._preflight()

        for bad_run_id in ("", "../escape", r"..\escape", "C:/escape", "run id"):
            with self.subTest(run_id=bad_run_id):
                report = preflight.run(self._request(run_id=bad_run_id))

                self.assertFalse(report.resolved)
                self.assertEqual(report.failure.code, "INVALID_RUN_ID")

        self.assertFalse(self.output_root.exists())

    def test_unauthorized_price_view_fails_closed(self) -> None:
        preflight = self._preflight()

        report = preflight.run(self._request(signal_price_view="raw_1m"))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "PRICE_VIEW_NOT_AUTHORIZED")

    def test_unknown_universe_fails_closed(self) -> None:
        preflight = self._preflight(universes={})

        report = preflight.run(self._request(universe_id="missing_universe"))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "UNIVERSE_NOT_FOUND")

    def test_symbol_outside_universe_fails_closed(self) -> None:
        preflight = self._preflight()

        report = preflight.run(self._request(symbols_optional=("AAA", "ZZZ")))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "SYMBOL_NOT_IN_UNIVERSE")

    def test_candidate_without_consumption_policy_fails_closed(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))

        report = preflight.run(self._request())

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "CANDIDATE_POLICY_REQUIRED")

    def test_candidate_without_registered_validation_manifest_fails_closed(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True, validation_manifest=None))

        report = preflight.run(self._request(candidate_consumption_policy=self._candidate_policy()))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "CANDIDATE_REGISTERED_VALIDATION_MANIFEST_REQUIRED")

    def test_candidate_without_validation_manifest_fails_closed(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))
        policy = CandidateConsumptionPolicy(
            candidate_dataset_id="synthetic_dataset",
            candidate_physical_root=self.dataset_root,
            authorization_basis="validation_pass_for_controlled_downstream_consumption",
            accepted_validation_manifest=None,
            promotion_authorization=False,
            permitted_run_purposes=("ENGINE_MECHANICS_TEST",),
        )

        report = preflight.run(self._request(candidate_consumption_policy=policy))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "CANDIDATE_VALIDATION_MANIFEST_REQUIRED")

    def test_candidate_validation_manifest_mismatch_fails_closed(self) -> None:
        other_manifest = self.root / "other_validation_manifest.json"
        other_manifest.write_text("{}\n", encoding="utf-8")
        preflight = self._preflight(dataset=self._dataset(candidate=True))
        policy = self._candidate_policy(validation_manifest=other_manifest)

        report = preflight.run(self._request(candidate_consumption_policy=policy))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "CANDIDATE_VALIDATION_MANIFEST_MISMATCH")

    def test_candidate_with_missing_validation_manifest_path_fails_closed(self) -> None:
        missing_manifest = self.root / "does_not_exist.json"
        preflight = self._preflight(dataset=self._dataset(candidate=True, validation_manifest=missing_manifest))
        policy = self._candidate_policy(validation_manifest=missing_manifest)

        report = preflight.run(self._request(candidate_consumption_policy=policy))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "CANDIDATE_VALIDATION_MANIFEST_NOT_FOUND")

    def test_candidate_run_purpose_not_permitted_fails_closed(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))
        policy = self._candidate_policy()

        report = preflight.run(self._request(run_purpose="UNAUTHORIZED_PURPOSE", candidate_consumption_policy=policy))

        self.assertFalse(report.resolved)
        self.assertEqual(report.failure.code, "CANDIDATE_RUN_PURPOSE_NOT_PERMITTED")

    def test_real_data_fixture_requires_physical_inspection_before_pass(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))
        request = self._request(
            run_id="real_fixture_without_inspector",
            candidate_consumption_policy=self._candidate_policy(),
            fixture_kind=TSIS_REAL_DATA_FIXTURE,
        )

        report = preflight.run(request)

        real_output_root = self.output_root / "real_fixture_without_inspector"
        self.assertFalse(report.resolved)
        self.assertEqual(report.context_resolution_status, "CONTEXT_RESOLVED")
        self.assertEqual(report.physical_inspection_status, "NOT_IMPLEMENTED")
        self.assertEqual(report.preflight_status, "PREFLIGHT_FAIL")
        self.assertEqual(report.failure.code, "PHYSICAL_INSPECTION_NOT_IMPLEMENTED")
        self.assertTrue((real_output_root / "data_preflight_report.json").exists())
        self.assertFalse((real_output_root / "data_manifest.json").exists())
        self.assertFalse((real_output_root / "universe_manifest.json").exists())

    def test_synthetic_candidate_run_writes_required_manifests_under_run_id(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))

        report = preflight.run(self._request(candidate_consumption_policy=self._candidate_policy()))

        self.assertTrue(report.resolved)
        self.assertEqual(report.fixture_kind, "NON_EMPIRICAL_TEST_FIXTURE")
        self.assertEqual(report.context_resolution_status, "CONTEXT_RESOLVED")
        self.assertEqual(report.physical_inspection_status, "SYNTHETIC_NOT_REQUIRED")
        self.assertEqual(report.preflight_status, "PREFLIGHT_PASS")
        self.assertTrue((self.run_output_root / "data_manifest.json").exists())
        self.assertTrue((self.run_output_root / "universe_manifest.json").exists())
        self.assertTrue((self.run_output_root / "data_preflight_report.json").exists())
        data_manifest = json.loads((self.run_output_root / "data_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data_manifest["dataset_id"], "synthetic_dataset")
        self.assertEqual(
            data_manifest["price_view_policy"]["execution"]["allowed_use"],
            "proxy_allowed_for_engine_mechanics_only",
        )

    def test_success_manifest_serializes_complete_policies(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))

        report = preflight.run(self._request(candidate_consumption_policy=self._candidate_policy()))

        self.assertTrue(report.resolved)
        data_manifest = json.loads((self.run_output_root / "data_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data_manifest["missing_data_policy"]["on_missing_bar"], "EMIT_GAP_WITHOUT_IMPUTATION")
        self.assertEqual(data_manifest["missing_data_policy"]["on_required_open_missing"], "FAIL_TICKER_DAY")
        self.assertFalse(data_manifest["missing_data_policy"]["imputation_allowed"])
        self.assertEqual(data_manifest["corporate_action_policy"]["on_effective_action_inside_ticker_day"], "EXCLUDE_TICKER_DAY")
        self.assertEqual(data_manifest["corporate_action_policy"]["on_unknown_action_state"], "DECLARE_LIMITATION")

    def test_failed_run_writes_only_preflight_report_in_fresh_run_dir(self) -> None:
        preflight = self._preflight(datasets={})

        report = preflight.run(self._request(dataset_id="missing_dataset", run_id="failed_run"))

        failed_root = self.output_root / "failed_run"
        self.assertFalse(report.resolved)
        self.assertEqual(report.context_resolution_status, "NOT_RESOLVED")
        self.assertEqual(report.preflight_status, "PREFLIGHT_FAIL")
        self.assertTrue((failed_root / "data_preflight_report.json").exists())
        self.assertFalse((failed_root / "data_manifest.json").exists())
        self.assertFalse((failed_root / "universe_manifest.json").exists())

    def test_non_empty_run_output_is_rejected_without_deleting_old_manifests(self) -> None:
        preflight = self._preflight(dataset=self._dataset(candidate=True))
        request = self._request(candidate_consumption_policy=self._candidate_policy())
        first = preflight.run(request)
        old_manifest = self.run_output_root / "data_manifest.json"
        old_payload = old_manifest.read_text(encoding="utf-8")

        second = preflight.run(request)

        self.assertTrue(first.resolved)
        self.assertFalse(second.resolved)
        self.assertEqual(second.failure.code, "RUN_OUTPUT_NOT_EMPTY")
        self.assertEqual(old_manifest.read_text(encoding="utf-8"), old_payload)

    def test_bar_is_not_observable_before_available_at(self) -> None:
        bar = MarketDataBar1m(
            ticker="AAA",
            ts_start=datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc),
            ts_end=datetime(2026, 1, 5, 14, 31, tzinfo=timezone.utc),
            available_at=datetime(2026, 1, 5, 14, 31, tzinfo=timezone.utc),
            session_label="REGULAR",
            open=10.0,
            high=10.5,
            low=9.8,
            close=10.2,
            volume=1000,
            price_view="quote_guarded_1m",
        )

        self.assertFalse(bar.is_observable_at(datetime(2026, 1, 5, 14, 30, 59, tzinfo=timezone.utc)))
        self.assertTrue(bar.is_observable_at(datetime(2026, 1, 5, 14, 31, 0, tzinfo=timezone.utc)))

    def test_missing_data_policy_defaults_preserve_no_imputation_contract(self) -> None:
        policy = MissingDataPolicy(policy_id="missing_v0_1")

        self.assertEqual(policy.on_missing_bar, "EMIT_GAP_WITHOUT_IMPUTATION")
        self.assertEqual(policy.on_required_open_missing, "FAIL_TICKER_DAY")
        self.assertEqual(policy.on_required_close_missing, "FAIL_TICKER_DAY")
        self.assertFalse(policy.imputation_allowed)
        self.assertTrue(policy.gap_event_emitted)

    def test_same_inputs_with_fixed_timestamp_write_same_manifest_in_separate_run_dirs(self) -> None:
        request = self._request(candidate_consumption_policy=self._candidate_policy())
        preflight_one = self._preflight(dataset=self._dataset(candidate=True), output_root=self.root / "out_one")
        preflight_two = self._preflight(dataset=self._dataset(candidate=True), output_root=self.root / "out_two")

        first = preflight_one.run(request)
        first_manifest = (self.root / "out_one" / self.run_id / "data_manifest.json").read_text(encoding="utf-8")
        second = preflight_two.run(request)
        second_manifest = (self.root / "out_two" / self.run_id / "data_manifest.json").read_text(encoding="utf-8")

        self.assertTrue(first.resolved)
        self.assertTrue(second.resolved)
        self.assertEqual(first_manifest, second_manifest)

    def _preflight(
        self,
        datasets: dict[str, DatasetDefinition] | None = None,
        universes: dict[str, UniverseDefinition] | None = None,
        dataset: DatasetDefinition | None = None,
        output_root: Path | None = None,
    ) -> RunPreflight:
        if datasets is None:
            datasets = {"synthetic_dataset": dataset or self._dataset()}
        if universes is None:
            universes = {"synthetic_universe": self._universe()}
        return RunPreflight(
            DatasetRegistry(datasets),
            UniverseRegistry(universes),
            output_root=output_root or self.output_root,
            generated_at_utc="2026-07-28T00:00:00Z",
        )

    def _dataset(
        self,
        candidate: bool = False,
        physical_root: Path | None = None,
        validation_manifest: Path | None | object = _UNSET,
    ) -> DatasetDefinition:
        root = physical_root or self.dataset_root
        manifest = self.validation_manifest if candidate else None
        if validation_manifest is not _UNSET:
            manifest = validation_manifest
        auth = PriceViewAuthorization(
            price_view="quote_guarded_1m",
            physical_root=root,
            validation_manifest=manifest if candidate else None,
        )
        return DatasetDefinition(
            dataset_id="synthetic_dataset",
            dataset_version="v0_1",
            physical_root=root,
            schema_version="schema_v0_1",
            allowed_price_views={"quote_guarded_1m": auth},
            is_candidate=candidate,
            validation_manifest=manifest if candidate else None,
            raw_lineage="synthetic_fixture",
            known_limitations=("non_empirical_fixture",),
        )

    def _universe(self) -> UniverseDefinition:
        return UniverseDefinition(
            universe_id="synthetic_universe",
            universe_run_id="synthetic_universe_run_v0_1",
            selection_rule="explicit_symbols",
            symbols=("AAA", "BBB"),
            source_snapshot="synthetic",
            source_hash="synthetic_hash",
            limitations=("not_empirical",),
        )

    def _candidate_policy(self, validation_manifest: Path | None = None) -> CandidateConsumptionPolicy:
        return CandidateConsumptionPolicy(
            candidate_dataset_id="synthetic_dataset",
            candidate_physical_root=self.dataset_root,
            authorization_basis="validation_pass_for_controlled_downstream_consumption",
            accepted_validation_manifest=validation_manifest or self.validation_manifest,
            promotion_authorization=False,
            permitted_run_purposes=("ENGINE_MECHANICS_TEST",),
            accepted_limitations=("candidate_for_controlled_consumption",),
        )

    def _request(self, **overrides) -> RunDataRequest:
        values = {
            "run_id": self.run_id,
            "run_purpose": "ENGINE_MECHANICS_TEST",
            "dataset_id": "synthetic_dataset",
            "signal_price_view": "quote_guarded_1m",
            "execution_price_view": "quote_guarded_1m",
            "valuation_price_view": "quote_guarded_1m",
            "universe_id": "synthetic_universe",
            "date_start": date(2026, 1, 5),
            "date_end": date(2026, 1, 5),
            "session_policy": "REGULAR_ONLY",
            "timezone": "America/New_York",
            "calendar_id": "XNYS",
            "missing_data_policy": MissingDataPolicy(policy_id="missing_v0_1"),
            "corporate_action_policy": CorporateActionPolicy(policy_id="ca_v0_1"),
            "symbols_optional": (),
        }
        values.update(overrides)
        return RunDataRequest(**values)


if __name__ == "__main__":
    unittest.main()