from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from tsis_backtest.market_state.consumer import (
    EXPECTED_TYPES,
    PHYSICAL_COLUMNS,
    MarketStateConsumerV0_1,
    _canonical_restrictions,
    state_aware_order_key,
)
from tsis_backtest.market_state.contracts import (
    EXPECTED_RESTRICTIONS,
    MarketStateContractError,
)
from tsis_backtest.market_state.physical_authorization_v0_4 import (
    AUTHORIZATION_ID,
    CONSUMED_STATUS,
    CONSUMER_ID,
    CONTRACT_CONSUMER_ID,
    RUN_ID,
    AuthorizationV04,
)
from tsis_backtest.market_state.physical_runner_v0_4 import (
    CONFIG_FIELDS,
    PHYSICAL_INPUT_NAMES,
    FrozenPhysicalRunSpec,
    PRODUCTION_SPEC,
    PhysicalRunnerV04,
)
from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.replay.contracts import ReplayBarEvent


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_FIXTURE_ROOT = (
    REPOSITORY_ROOT / "tests/fixtures/bt_gate_014_synthetic_market_state"
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysicalV04Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.tsis_root = Path(self.temporary.name)
        self.engine_root = self.tsis_root / "02_TSIS_BACKTEST_ENGINE"
        self.engine_root.mkdir()

        self.rows = json.loads(
            (
                SYNTHETIC_FIXTURE_ROOT / "synthetic_raw_rows.json"
            ).read_text(encoding="utf-8")
        )["records"]
        self.sidecars = json.loads(
            (
                SYNTHETIC_FIXTURE_ROOT / "synthetic_sidecar.json"
            ).read_text(encoding="utf-8")
        )["records"]
        self.authorized_rows = tuple(
            {
                "context_id": row["context_id"],
                "decision_timestamp_utc": row[
                    "decision_timestamp_utc"
                ],
                "instrument_id": row["instrument_id"],
                "materialized_state_candidate_id": row[
                    "materialized_state_candidate_id"
                ],
                "session_date": row["session_date"],
                "source_candidate_record_id": row[
                    "source_candidate_record_id"
                ],
                "state_available_at_utc": sidecar[
                    "state_available_at_utc"
                ],
                "state_output_fingerprint": row[
                    "state_output_fingerprint"
                ],
                "ticker": row["ticker"],
            }
            for row, sidecar in zip(self.rows, self.sidecars)
        )

        provider_relative_paths: dict[str, str] = {}
        physical_input_sha256: dict[str, str] = {}
        for name in PHYSICAL_INPUT_NAMES:
            suffix = ".parquet" if name == "candidate_parquet" else ".json"
            path = self.tsis_root / "provider" / f"{name}{suffix}"
            if name == "physical_schema_contract":
                value: object = {
                    "column_count": 40,
                    "columns": [
                        {
                            "name": column,
                            "nullable": False,
                            "type": EXPECTED_TYPES[column],
                        }
                        for column in PHYSICAL_COLUMNS
                    ],
                }
                write_json(path, value)
            elif name == "sidecar_manifest":
                value = {
                    "candidate_dataset_fingerprint": self.sidecars[0][
                        "candidate_dataset_fingerprint"
                    ],
                    "candidate_dataset_id": self.sidecars[0][
                        "candidate_dataset_id"
                    ],
                    "records": self.sidecars,
                    "sidecar_id": self.sidecars[0]["sidecar_id"],
                    "sidecar_schema_id": self.sidecars[0][
                        "sidecar_schema_id"
                    ],
                }
                write_json(path, value)
            elif name == "candidate_parquet":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"synthetic-not-a-provider-parquet\n")
            else:
                write_json(path, {"fixture_input": name})
            provider_relative_paths[name] = path.relative_to(
                self.tsis_root
            ).as_posix()
            physical_input_sha256[name] = sha256(path)

        adopted_relative_paths: dict[str, str] = {}
        adopted_sha256: dict[str, str] = {}
        for name in (
            "outer_provider_handoff",
            "nested_provider_evidence",
        ):
            path = (
                self.engine_root
                / "evidence/provider_handoffs/bt_gate_014"
                / f"{name}.zip"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"synthetic-{name}\n".encode("utf-8"))
            adopted_relative_paths[name] = path.relative_to(
                self.engine_root
            ).as_posix()
            adopted_sha256[name] = sha256(path)

        self.barrier_path = (
            self.engine_root
            / "configs/fixtures/"
            "BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_4.json"
        )
        write_json(
            self.barrier_path,
            {
                "execution_input": False,
                "fixture_id": (
                    "BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_4"
                ),
                "physical_source_rows": 0,
                "price_use": "PROHIBITED",
                "records": [
                    {
                        "available_at": sidecar[
                            "state_available_at_utc"
                        ],
                        "barrier_id": f"barrier-{index}",
                        "close": 1.0,
                        "high": 1.0,
                        "low": 1.0,
                        "open": 1.0,
                        "session_label": "REGULAR",
                        "ticker": row["ticker"],
                        "ts_end": sidecar["state_available_at_utc"],
                        "ts_start": (
                            "2026-01-05T14:30:00Z"
                            if index == 0
                            else "2026-01-05T14:31:00Z"
                        ),
                        "volume": 0,
                    }
                    for index, (row, sidecar) in enumerate(
                        zip(self.rows, self.sidecars)
                    )
                ],
                "scientific_market_data_claim": False,
            },
        )
        barrier_relative_path = self.barrier_path.relative_to(
            self.engine_root
        ).as_posix()
        self.spec = FrozenPhysicalRunSpec(
            provider_relative_paths=provider_relative_paths,
            physical_input_sha256=physical_input_sha256,
            adopted_evidence_relative_paths=adopted_relative_paths,
            adopted_evidence_sha256=adopted_sha256,
            authorized_rows=self.authorized_rows,
            barrier_fixture_relative_path=barrier_relative_path,
            barrier_fixture_sha256=sha256(self.barrier_path),
        )

        self.binding_path = self.engine_root / "binding_component.py"
        self.binding_path.write_text(
            "FROZEN_TEST_BINDING = True\n",
            encoding="utf-8",
        )
        self.bindings = {
            "binding_component.py": sha256(self.binding_path)
        }
        self.configuration = self._configuration()

        self.document_path = (
            self.engine_root
            / "docs/00_system/"
            "18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_"
            "AUTHORIZATION_V0_4.md"
        )
        self.document_path.parent.mkdir(parents=True, exist_ok=True)
        self.document_path.write_text(
            "# Synthetic V0.4 authorization fixture\n",
            encoding="utf-8",
        )
        self.configuration_path = (
            self.engine_root
            / "configs/runs/"
            "bt_gate_014_single_use_physical_market_state_"
            "consumer_v0_4.json"
        )
        write_json(self.configuration_path, self.configuration)
        self.state_path = (
            self.engine_root
            / "configs/authorizations/"
            "bt_gate_014_single_use_physical_consumer_"
            "authorization_v0_4.json"
        )
        write_json(
            self.state_path,
            {
                "authorization_document_sha256": sha256(
                    self.document_path
                ),
                "authorization_id": AUTHORIZATION_ID,
                "binding_sha256": self.bindings,
                "configuration_sha256": sha256(
                    self.configuration_path
                ),
                "consumed_by_run_id": None,
                "consumer_id": CONSUMER_ID,
                "contract_consumer_id": CONTRACT_CONSUMER_ID,
                "physical_consumer_read": "NOT_EXECUTED",
                "physical_state_rows_read": 0,
                "status": "AUTHORIZED_NOT_CONSUMED",
            },
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def run_directory(self) -> Path:
        return self.engine_root / "runs" / RUN_ID

    def _configuration(self) -> dict:
        configuration = {
            "adopted_evidence_relative_paths": dict(
                self.spec.adopted_evidence_relative_paths
            ),
            "adopted_evidence_sha256": dict(
                self.spec.adopted_evidence_sha256
            ),
            "allowed_operation": (
                "ONE_PHYSICAL_READ_AND_ONE_INTEGRATION_RUN"
            ),
            "authorization_id": AUTHORIZATION_ID,
            "authorization_version": "V0.4",
            "authorized_rows": [
                dict(row) for row in self.spec.authorized_rows
            ],
            "barrier_fixture_relative_path": (
                self.spec.barrier_fixture_relative_path
            ),
            "barrier_fixture_sha256": (
                self.spec.barrier_fixture_sha256
            ),
            "binding_sha256": self.bindings,
            "consumer_id": CONSUMER_ID,
            "contract_consumer_id": CONTRACT_CONSUMER_ID,
            "fills": 0,
            "maximum_physical_files": 1,
            "maximum_physical_rows": 2,
            "orders": 0,
            "physical_input_sha256": dict(
                self.spec.physical_input_sha256
            ),
            "pnl": False,
            "production": False,
            "provider_relative_paths": dict(
                self.spec.provider_relative_paths
            ),
            "run_directory": self.spec.run_directory,
            "run_id": self.spec.run_id,
            "strategy": "NONE",
        }
        self.assertEqual(set(configuration), CONFIG_FIELDS)
        return configuration

    def runner(
        self,
        rows: list[dict] | None = None,
        *,
        reader: Mock | None = None,
    ) -> PhysicalRunnerV04:
        row_reader = reader or Mock(
            return_value=copy.deepcopy(
                self.rows if rows is None else rows
            )
        )
        return PhysicalRunnerV04(
            row_reader,
            spec=self.spec,
        )

    def execute(
        self,
        rows: list[dict] | None = None,
        *,
        reader: Mock | None = None,
        authorization: AuthorizationV04 | None = None,
        configuration: dict | None = None,
    ) -> dict:
        return self.runner(rows, reader=reader).execute(
            self.tsis_root,
            configuration or self.configuration,
            authorization or AuthorizationV04(self.state_path),
            self.bindings,
        )

    def test_success_is_complete_and_bar_precedes_state(self) -> None:
        final_manifest = self.execute()
        self.assertEqual(final_manifest["validation_status"], "PASS")
        self.assertEqual(
            [
                item["event_type"]
                for item in json.loads(
                    (
                        self.run_directory
                        / "state_aware_event_sequence.json"
                    ).read_text(encoding="utf-8")
                )
            ],
            [
                "BAR",
                "BoundedMarketStateAvailable",
                "BAR",
                "BoundedMarketStateAvailable",
            ],
        )
        fixture_configuration = json.loads(
            (
                REPOSITORY_ROOT
                / "configs/runs/"
                "bt_gate_014_non_physical_market_state_consumer_v0_1.json"
            ).read_text(encoding="utf-8")
        )
        validated = MarketStateConsumerV0_1().validate_and_seal(
            self.rows[0],
            self.sidecars[0],
            fixture_configuration["authority"],
            sha256(SYNTHETIC_FIXTURE_ROOT / "synthetic_sidecar.json"),
        )
        shared_available_at = datetime(
            2026, 1, 6, 14, 30, tzinfo=timezone.utc
        )
        state = replace(
            validated.event,
            session_date=date(2026, 1, 5),
            state_available_at_utc=shared_available_at,
            ticker="AAA",
        )
        bar_start = shared_available_at - timedelta(minutes=1)
        bar = ReplayBarEvent(
            event_type="ReplayBarEvent",
            ticker="ZZZ",
            available_at=shared_available_at,
            bar=MarketDataBar1m(
                ticker="ZZZ",
                ts_start=bar_start,
                ts_end=shared_available_at,
                available_at=shared_available_at,
                session_label="REGULAR",
                open=1.0,
                high=1.0,
                low=1.0,
                close=1.0,
                volume=0,
                price_view="quote_guarded_raw",
            ),
        )
        self.assertEqual(
            [
                type(event).__name__
                for event in sorted((state, bar), key=state_aware_order_key)
            ],
            ["ReplayBarEvent", "BoundedMarketStateAvailable"],
        )
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8"))[
                "status"
            ],
            CONSUMED_STATUS,
        )
        self.assertEqual(
            json.loads(
                (
                    self.run_directory / "failure_manifest.json"
                ).read_text(encoding="utf-8")
            )["status"],
            "SUPERSEDED_BY_FINAL_MANIFEST_PASS",
        )

    def test_success_metrics_and_identity_are_explicit(self) -> None:
        final_manifest = self.execute()
        expected = {
            "bounded_consumer_observations": 2,
            "delivery_before_available_at": 0,
            "fills": 0,
            "identity_fingerprint_mismatches": 0,
            "market_state_events_emitted": 2,
            "market_state_store_inserts": 2,
            "orders": 0,
            "physical_data_files_opened": 1,
            "physical_state_rows_read": 2,
            "pnl_calculated": False,
            "provider_modification": False,
            "strategy_decisions": 0,
            "typed_scientific_values_per_event": 17,
        }
        for key, value in expected.items():
            self.assertEqual(final_manifest[key], value, key)
        self.assertRegex(
            final_manifest["scientific_identity_sha256"],
            r"^[0-9a-f]{64}$",
        )
        self.assertRegex(
            final_manifest["deterministic_output_hash"],
            r"^[0-9a-f]{64}$",
        )

    def test_receipt_write_failure_is_durably_evidenced(self) -> None:
        row_reader = Mock(return_value=copy.deepcopy(self.rows))
        authorization = AuthorizationV04(self.state_path)
        with patch.object(
            authorization,
            "_write_receipt",
            side_effect=OSError("injected receipt write failure"),
        ):
            with self.assertRaises(OSError):
                self.execute(
                    reader=row_reader,
                    authorization=authorization,
                )
        row_reader.assert_not_called()
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8"))[
                "status"
            ],
            CONSUMED_STATUS,
        )
        self.assertFalse(
            (
                self.run_directory
                / "authorization_consumption_receipt.json"
            ).exists()
        )
        failure = json.loads(
            (
                self.run_directory / "failure_manifest.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(failure["status"], "FAIL")
        self.assertTrue(failure["authorization_consumed"])
        self.assertEqual(failure["physical_state_rows_read"], 0)

    def test_state_transition_failure_keeps_armed_guard(self) -> None:
        import tsis_backtest.market_state.physical_authorization_v0_4 as auth_module

        original_write = auth_module.atomic_write_json

        def fail_only_consumption_state(path: Path, value: object) -> None:
            if (
                Path(path) == self.state_path
                and isinstance(value, dict)
                and value.get("status") == CONSUMED_STATUS
            ):
                raise OSError("injected authorization-state write failure")
            original_write(Path(path), value)

        row_reader = Mock(return_value=copy.deepcopy(self.rows))
        with patch.object(
            auth_module,
            "atomic_write_json",
            side_effect=fail_only_consumption_state,
        ):
            with self.assertRaises(OSError):
                self.execute(reader=row_reader)
        row_reader.assert_not_called()
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8"))[
                "status"
            ],
            "AUTHORIZED_NOT_CONSUMED",
        )
        failure = json.loads(
            (
                self.run_directory / "failure_manifest.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(failure["status"], "FAIL")
        self.assertFalse(failure["authorization_consumed"])
        self.assertFalse(
            (
                self.run_directory
                / "authorization_consumption_receipt.json"
            ).exists()
        )

    def test_post_consumption_input_hash_failure_has_receipt_and_failure(
        self,
    ) -> None:
        candidate_path = (
            self.tsis_root
            / self.spec.provider_relative_paths["candidate_parquet"]
        )
        candidate_path.write_bytes(b"mutated-after-authorization\n")
        row_reader = Mock(return_value=copy.deepcopy(self.rows))
        with self.assertRaisesRegex(
            MarketStateContractError,
            "PHYSICAL_INPUT_HASH_MISMATCH",
        ):
            self.execute(reader=row_reader)
        row_reader.assert_not_called()
        self.assertTrue(
            (
                self.run_directory
                / "authorization_consumption_receipt.json"
            ).is_file()
        )
        self.assertEqual(
            json.loads(
                (
                    self.run_directory / "failure_manifest.json"
                ).read_text(encoding="utf-8")
            )["status"],
            "FAIL",
        )

    def test_incomplete_rows_fail_after_consumption_with_manifest(
        self,
    ) -> None:
        incomplete = [
            {
                "materialized_state_candidate_id": row[
                    "materialized_state_candidate_id"
                ],
                "state_output_fingerprint": row[
                    "state_output_fingerprint"
                ],
            }
            for row in self.rows
        ]
        with self.assertRaisesRegex(
            MarketStateContractError,
            "PHYSICAL_SCHEMA_MISMATCH",
        ):
            self.execute(incomplete)
        self.assertEqual(
            json.loads(
                (
                    self.run_directory / "failure_manifest.json"
                ).read_text(encoding="utf-8")
            )["status"],
            "FAIL",
        )

    def test_scope_expansion_fails_before_consumption(self) -> None:
        expanded = copy.deepcopy(self.configuration)
        expanded["authorized_rows"].append(
            copy.deepcopy(expanded["authorized_rows"][0])
        )
        row_reader = Mock(return_value=copy.deepcopy(self.rows))
        with self.assertRaisesRegex(
            MarketStateContractError,
            "CLOSED_CONFIGURATION_MISMATCH",
        ):
            self.execute(
                reader=row_reader,
                configuration=expanded,
            )
        row_reader.assert_not_called()
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8"))[
                "status"
            ],
            "AUTHORIZED_NOT_CONSUMED",
        )
        self.assertFalse(self.run_directory.exists())

    def test_binding_mutation_fails_before_consumption(self) -> None:
        self.binding_path.write_text(
            "FROZEN_TEST_BINDING = False\n",
            encoding="utf-8",
        )
        row_reader = Mock(return_value=copy.deepcopy(self.rows))
        with self.assertRaisesRegex(
            MarketStateContractError,
            "AUTHORIZED_RUNNER_HASH_MISMATCH",
        ):
            self.execute(reader=row_reader)
        row_reader.assert_not_called()
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8"))[
                "status"
            ],
            "AUTHORIZED_NOT_CONSUMED",
        )

    def test_second_use_is_rejected_without_mutating_pass_evidence(
        self,
    ) -> None:
        self.execute()
        guard_path = self.run_directory / "failure_manifest.json"
        guard_before = guard_path.read_bytes()
        with self.assertRaisesRegex(
            MarketStateContractError,
            "AUTHORIZATION_ALREADY_CONSUMED",
        ):
            self.execute()
        self.assertEqual(guard_path.read_bytes(), guard_before)

    def test_canonical_v01_and_v02_are_superseded_unconsumed(self) -> None:
        for version in ("v0_1", "v0_2"):
            path = (
                REPOSITORY_ROOT
                / "configs/authorizations/"
                f"bt_gate_014_single_use_physical_consumer_"
                f"authorization_{version}.json"
            )
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["status"],
                "SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL",
            )

    def test_no_general_state_or_operational_surface_is_enabled(
        self,
    ) -> None:
        final_manifest = self.execute()
        boundary = json.loads(
            (
                self.run_directory / "boundary_preservation_report.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(boundary["state_replay_feed"], "NOT_AUTHORIZED")
        self.assertEqual(boundary["event_state"], "NOT_OPEN")
        self.assertFalse(boundary["market_state_as_execution_price"])
        self.assertEqual(final_manifest["BT_GATE_014_CLOSED_PASS"], "NOT_AUTHORIZED")


    def test_restriction_equivalence_is_closed_and_order_independent(self) -> None:
        reordered = tuple(reversed(EXPECTED_RESTRICTIONS))
        self.assertEqual(
            _canonical_restrictions(reordered, "test"),
            EXPECTED_RESTRICTIONS,
        )
        invalid = (
            EXPECTED_RESTRICTIONS[:-1],
            EXPECTED_RESTRICTIONS + (EXPECTED_RESTRICTIONS[0],),
            EXPECTED_RESTRICTIONS + ("unexpected",),
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(MarketStateContractError) as context:
                    _canonical_restrictions(value, "test")
                self.assertEqual(
                    context.exception.code,
                    "FAIL_MARKET_STATE_RESTRICTION_PROPAGATION",
                )

    def test_failure_after_physical_rows_loaded_reports_real_progress(self) -> None:
        sidecar_path = self.tsis_root / self.spec.provider_relative_paths[
            "sidecar_manifest"
        ]
        document = json.loads(sidecar_path.read_text(encoding="utf-8"))
        document["records"][0]["restriction_codes"] = ["unexpected"]
        write_json(sidecar_path, document)
        updated_hashes = dict(self.spec.physical_input_sha256)
        updated_hashes["sidecar_manifest"] = sha256(sidecar_path)
        self.spec = replace(self.spec, physical_input_sha256=updated_hashes)
        self.configuration = self._configuration()
        write_json(self.configuration_path, self.configuration)
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state["configuration_sha256"] = sha256(self.configuration_path)
        write_json(self.state_path, state)
        with self.assertRaises(MarketStateContractError):
            self.execute()
        failure = json.loads(
            (self.run_directory / "failure_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(failure["physical_data_files_opened"], 1)
        self.assertEqual(failure["physical_state_rows_read"], 2)
        self.assertEqual(
            failure["validation_phase_reached"],
            "RESTRICTION_VALIDATION",
        )
        diagnostics = failure["restriction_diagnostics"]
        self.assertEqual(diagnostics["expected_restrictions"], list(EXPECTED_RESTRICTIONS))
        self.assertEqual(len(diagnostics["rows"]), 2)
        self.assertEqual(len(diagnostics["sidecars"]), 2)

    def test_reader_failure_before_open_reports_attempted_zero_zero(self) -> None:
        reader = Mock(side_effect=OSError("injected before open"))
        with self.assertRaises(OSError):
            self.execute(reader=reader)
        failure = json.loads((self.run_directory / "failure_manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(failure["physical_access_attempted"])
        self.assertFalse(failure["physical_access_started"])
        self.assertEqual(failure["physical_data_files_opened"], 0)
        self.assertEqual(failure["physical_state_rows_read"], 0)
        self.assertEqual(failure["validation_phase_reached"], "CANDIDATE_PARQUET_OPEN_ATTEMPT")


class PhysicalV04CanonicalBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state_path = REPOSITORY_ROOT / "configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_4.json"
        self.state = json.loads(self.state_path.read_text(encoding="utf-8"))

    def test_v04_is_historical_consumed_failed(self) -> None:
        self.assertEqual(self.state["authorization_id"], "BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-4")
        self.assertTrue(self.state["status"].startswith("CONSUMED_BY_RUN_"))
        self.assertEqual(self.state["consumed_by_run_id"], "bt_gate_014_single_use_physical_market_state_consumer_v0_4")

    def test_v04_closed_binding_is_preserved_as_historical_evidence(self) -> None:
        self.assertEqual(len(self.state["binding_sha256"]), 9)
        self.assertTrue(all(len(value) == 64 for value in self.state["binding_sha256"].values()))

    def test_production_spec_matches_canonical_v04_configuration(self) -> None:
        configuration = json.loads((REPOSITORY_ROOT / "configs/runs/bt_gate_014_single_use_physical_market_state_consumer_v0_4.json").read_text(encoding="utf-8"))
        self.assertEqual(PRODUCTION_SPEC.barrier_fixture_relative_path, configuration["barrier_fixture_relative_path"])
        self.assertEqual(PRODUCTION_SPEC.barrier_fixture_sha256, configuration["barrier_fixture_sha256"])
        self.assertEqual(dict(PRODUCTION_SPEC.provider_relative_paths), configuration["provider_relative_paths"])
        self.assertEqual(dict(PRODUCTION_SPEC.physical_input_sha256), configuration["physical_input_sha256"])

    def test_v03_and_v04_consumed_failure_evidence_exists(self) -> None:
        v03 = json.loads((REPOSITORY_ROOT / "configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_3.json").read_text(encoding="utf-8"))
        self.assertTrue(v03["status"].startswith("CONSUMED_BY_RUN_"))
        run03 = REPOSITORY_ROOT / "runs/bt_gate_014_single_use_physical_market_state_consumer_v0_3"
        for name in ("authorization_consumption_receipt.json", "pre_run_manifest.json", "failure_manifest.json"):
            self.assertTrue((run03 / name).is_file(), name)
        run04 = REPOSITORY_ROOT / "runs/bt_gate_014_single_use_physical_market_state_consumer_v0_4"
        for name in ("authorization_consumption_receipt.json", "pre_run_manifest.json", "failure_manifest.json", "physical_progress.json"):
            self.assertTrue((run04 / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
