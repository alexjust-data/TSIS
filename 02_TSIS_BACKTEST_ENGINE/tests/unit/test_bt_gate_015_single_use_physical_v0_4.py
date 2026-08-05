from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

from tsis_backtest.event_state.contracts import EventStateContractError
from tsis_backtest.event_state.physical_authorization_v0_4 import (
    AUTHORIZATION_ID,
    CONSUMED_STATUS,
    RUN_ID,
    AuthorizationV04,
)
from tsis_backtest.event_state.physical_consumer_v0_4 import (
    PhysicalEventStateConsumerV04,
    physical_record_fingerprint,
)
from tsis_backtest.event_state.physical_runner_v0_4 import PhysicalRunnerV04

ROOT = Path(__file__).resolve().parents[2]
TSIS_ROOT = ROOT.parent
FIXTURE = ROOT / "tests/fixtures/bt_gate_015_synthetic_event_state"
CANONICAL_SPEC = (
    ROOT
    / "configs/authorizations/"
    "bt_gate_015_single_use_physical_event_state_consumer_v0_4_spec.json"
)
CANONICAL_STATE = (
    ROOT
    / "configs/authorizations/"
    "bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
)
CANONICAL_CONFIG = (
    ROOT
    / "configs/runs/"
    "bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


class PhysicalV04Fixture:
    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.tsis_root = Path(self.temporary.name)
        self.engine_root = self.tsis_root / "02_TSIS_BACKTEST_ENGINE"
        self.spec_path = (
            self.engine_root
            / "configs/authorizations/"
            "bt_gate_015_single_use_physical_event_state_consumer_v0_4_spec.json"
        )
        self.state_path = (
            self.engine_root
            / "configs/authorizations/"
            "bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
        )
        self.config_path = (
            self.engine_root
            / "configs/runs/"
            "bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
        )
        self.barrier_path = (
            self.engine_root
            / "configs/fixtures/BT_GATE_015_PHYSICAL_INTEGRATION_BARRIERS_V0_4.json"
        )
        self.spec = json.loads(CANONICAL_SPEC.read_text(encoding="utf-8"))
        self._build_inputs()
        self.materialize()

    def close(self) -> None:
        self.temporary.cleanup()

    @property
    def run_directory(self) -> Path:
        return self.engine_root / "runs" / RUN_ID

    def _build_inputs(self) -> None:
        rows_document = json.loads(
            (FIXTURE / "synthetic_event_state_rows.json").read_text(encoding="utf-8")
        )
        row = copy.deepcopy(rows_document["records"][0])
        event_sidecar = json.loads(
            (FIXTURE / "synthetic_event_state_sidecar.json").read_text(
                encoding="utf-8"
            )
        )
        event_record = event_sidecar["records"][0]
        event_record["evidence_refs"]["market_state_schema_sha256"] = "f" * 64
        market_record = json.loads(
            (FIXTURE / "synthetic_market_state_sidecar_record.json").read_text(
                encoding="utf-8"
            )
        )
        market_record["candidate_dataset_fingerprint"] = event_record[
            "market_state_availability_evidence_dataset_fingerprint"
        ]
        row["state_output_fingerprint"] = market_record["state_output_fingerprint"]
        row["source_market_state_physical_profile_id"] = market_record[
            "physical_profile_id"
        ]
        row["source_market_state_candidate_dataset_fingerprint"] = event_record[
            "market_state_dependency_dataset_fingerprint"
        ]
        row["market_state_dependency_request_fingerprint"] = "1" * 64
        row["market_state_dependency_execution_plan_fingerprint"] = "2" * 64
        row["event_state_record_fingerprint"] = physical_record_fingerprint(row)
        event_record["event_state_record_fingerprint"] = row[
            "event_state_record_fingerprint"
        ]
        event_record["market_state_state_output_fingerprint"] = row[
            "state_output_fingerprint"
        ]
        self.row = row
        self.event_sidecar = event_sidecar
        self.market_document = {
            "sidecar_id": "synthetic_market_state_dependency_document_v0_4",
            "records": [market_record],
        }
        decoys = [json.dumps({"decoy": index}, sort_keys=True) for index in range(7)]
        selected = json.dumps(row, sort_keys=True, separators=(",", ":"))
        self.candidate_raw = ("\n".join(decoys + [selected]) + "\n").encode("utf-8")
        for name, binding in self.spec["governed_inputs"].items():
            path = self.tsis_root / binding["relative_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            if name == "candidate_jsonl":
                path.write_bytes(self.candidate_raw)
            elif name == "replay_availability_sidecar_manifest":
                write_json(path, self.event_sidecar)
            elif name == "market_state_replay_sidecar":
                write_json(path, self.market_document)
            elif path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("PACKAGE_MANIFEST.json", "{}\n")
            else:
                write_json(path, {"fixture": name})
            binding["sha256"] = sha256(path)
            binding["size_bytes"] = path.stat().st_size
        self.spec["physical_identity"]["candidate_jsonl_sha256"] = hashlib.sha256(
            self.candidate_raw
        ).hexdigest()
        self.spec["physical_identity"]["event_state_record_id"] = row[
            "event_state_record_id"
        ]
        self.spec["physical_identity"]["event_state_record_fingerprint"] = row[
            "event_state_record_fingerprint"
        ]
        self.spec["selection"].update(
            {
                "event_state_record_id": row["event_state_record_id"],
                "event_state_record_fingerprint": row[
                    "event_state_record_fingerprint"
                ],
            }
        )
        self.spec["market_state_dependency"].update(
            {
                "availability_evidence_dataset_fingerprint": market_record[
                    "candidate_dataset_fingerprint"
                ],
                "dependency_dataset_fingerprint": event_record[
                    "market_state_dependency_dataset_fingerprint"
                ],
                "record_id": market_record["materialized_state_candidate_id"],
                "state_output_fingerprint": market_record[
                    "state_output_fingerprint"
                ],
            }
        )
        self.barrier_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            ROOT
            / "configs/fixtures/BT_GATE_015_PHYSICAL_INTEGRATION_BARRIERS_V0_4.json",
            self.barrier_path,
        )

    def materialize(self) -> None:
        write_json(self.spec_path, self.spec)
        config = {
            "authorization_id": AUTHORIZATION_ID,
            "barrier_fixture_relative_path": str(
                self.barrier_path.relative_to(self.tsis_root)
            ).replace("\\", "/"),
            "boundaries": self.spec["boundaries"],
            "contract_id": self.spec["contract_id"],
            "event_state_scope": self.spec["event_state_scope"],
            "expected_outputs": self.spec["expected_outputs"],
            "gate_id": "BT-GATE-015",
            "governed_inputs": self.spec["governed_inputs"],
            "physical_command_status": "NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW",
            "run_directory_relative_path": f"02_TSIS_BACKTEST_ENGINE/runs/{RUN_ID}",
            "run_id": RUN_ID,
            "specification_relative_path": str(
                self.spec_path.relative_to(self.tsis_root)
            ).replace("\\", "/"),
            "specification_sha256": sha256(self.spec_path),
        }
        write_json(self.config_path, config)
        binding_hashes = {}
        for relative in self.spec["executable_binding_paths"]:
            path = self.tsis_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.is_file():
                path.write_text(
                    f"synthetic executable binding: {relative}\n",
                    encoding="utf-8",
                    newline="\n",
                )
            binding_hashes[relative] = sha256(path)
        write_json(
            self.state_path,
            {
                "authorization_id": AUTHORIZATION_ID,
                "authorization_consumption_count": 0,
                "binding_sha256": binding_hashes,
                "configuration_sha256": sha256(self.config_path),
                "consumed_by_run_id": None,
                "run_id": RUN_ID,
                "single_use": True,
                "specification_sha256": sha256(self.spec_path),
                "status": "AUTHORIZED_NOT_CONSUMED",
            },
        )
        self.config = config

    def rematerialize_selected_row(self) -> None:
        self.row["event_state_record_fingerprint"] = physical_record_fingerprint(
            self.row
        )
        self.event_sidecar["records"][0]["event_state_record_fingerprint"] = (
            self.row["event_state_record_fingerprint"]
        )
        decoys = [json.dumps({"decoy": index}, sort_keys=True) for index in range(7)]
        selected = json.dumps(self.row, sort_keys=True, separators=(",", ":"))
        self.candidate_raw = ("\n".join(decoys + [selected]) + "\n").encode(
            "utf-8"
        )
        candidate_path = self.tsis_root / self.spec["governed_inputs"][
            "candidate_jsonl"
        ]["relative_path"]
        candidate_path.write_bytes(self.candidate_raw)
        self.spec["governed_inputs"]["candidate_jsonl"].update(
            {
                "sha256": hashlib.sha256(self.candidate_raw).hexdigest(),
                "size_bytes": len(self.candidate_raw),
            }
        )
        self.spec["physical_identity"]["candidate_jsonl_sha256"] = hashlib.sha256(
            self.candidate_raw
        ).hexdigest()
        self.spec["physical_identity"]["event_state_record_fingerprint"] = self.row[
            "event_state_record_fingerprint"
        ]
        self.spec["selection"]["event_state_record_fingerprint"] = self.row[
            "event_state_record_fingerprint"
        ]
        sidecar_path = self.tsis_root / self.spec["governed_inputs"][
            "replay_availability_sidecar_manifest"
        ]["relative_path"]
        write_json(sidecar_path, self.event_sidecar)
        self.spec["governed_inputs"]["replay_availability_sidecar_manifest"].update(
            {"sha256": sha256(sidecar_path), "size_bytes": sidecar_path.stat().st_size}
        )
        self.materialize()
    def reset_run(self) -> None:
        if self.run_directory.exists():
            shutil.rmtree(self.run_directory)
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state.update(
            {
                "authorization_consumption_count": 0,
                "consumed_by_run_id": None,
                "status": "AUTHORIZED_NOT_CONSUMED",
            }
        )
        state.pop("consumed_at_utc", None)
        write_json(self.state_path, state)

    def execute(self, reader=None):
        return PhysicalRunnerV04(reader).execute(
            self.tsis_root,
            self.config_path,
            AuthorizationV04(self.state_path, self.spec_path),
        )


class PhysicalEventStateV04Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = PhysicalV04Fixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_real_v04_classes_complete_synthetic_eight_to_one_path(self) -> None:
        result = self.fixture.execute()
        self.assertEqual(result["validation_status"], "PASS")
        self.assertEqual(result["physical_state_records_scanned"], 8)
        self.assertEqual(result["physical_state_rows_selected"], 1)
        self.assertEqual(result["event_state_events_emitted"], 1)
        self.assertEqual(result["event_state_store_inserts"], 1)
        self.assertEqual(result["orders"], 0)
        sequence = json.loads(
            (self.fixture.run_directory / "state_aware_event_sequence.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            [item["event_type"] for item in sequence],
            ["BAR", "BoundedMarketStateAvailable", "BoundedEventStateAvailable"],
        )

    def test_dependency_and_availability_dataset_domains_remain_distinct(self) -> None:
        event_record = self.fixture.event_sidecar["records"][0]
        self.assertEqual(
            self.fixture.row["source_market_state_candidate_dataset_fingerprint"],
            event_record["market_state_dependency_dataset_fingerprint"],
        )
        self.assertNotEqual(
            event_record["market_state_dependency_dataset_fingerprint"],
            event_record["market_state_availability_evidence_dataset_fingerprint"],
        )
        self.assertEqual(self.fixture.execute()["validation_status"], "PASS")

    def test_dependency_dataset_mismatch_records_field_expected_and_observed(self) -> None:
        event_record = self.fixture.event_sidecar["records"][0]
        dependency = event_record["market_state_dependency_dataset_fingerprint"]
        availability = event_record[
            "market_state_availability_evidence_dataset_fingerprint"
        ]
        self.fixture.row[
            "source_market_state_candidate_dataset_fingerprint"
        ] = availability
        self.fixture.rematerialize_selected_row()
        with self.assertRaisesRegex(EventStateContractError, "IDENTITY_MISMATCH"):
            self.fixture.execute()
        failure = json.loads(
            (self.fixture.run_directory / "failure_manifest.json").read_text()
        )
        diagnostic = failure["diagnostics"]["identity_mismatch"]
        self.assertEqual(
            diagnostic,
            {
                "field": "source_market_state_candidate_dataset_fingerprint",
                "expected": dependency,
                "observed": availability,
            },
        )
    def test_market_state_availability_sidecar_uses_availability_dataset(self) -> None:
        event_record = self.fixture.event_sidecar["records"][0]
        self.fixture.market_document["records"][0]["candidate_dataset_fingerprint"] = (
            event_record["market_state_dependency_dataset_fingerprint"]
        )
        market_path = self.fixture.tsis_root / self.fixture.spec["governed_inputs"][
            "market_state_replay_sidecar"
        ]["relative_path"]
        write_json(market_path, self.fixture.market_document)
        self.fixture.spec["governed_inputs"]["market_state_replay_sidecar"].update(
            {"sha256": sha256(market_path), "size_bytes": market_path.stat().st_size}
        )
        self.fixture.materialize()
        with self.assertRaisesRegex(
            EventStateContractError, "MARKET_STATE_DEPENDENCY_MISMATCH"
        ):
            self.fixture.execute()
    def test_preconsumption_never_calls_candidate_reader(self) -> None:
        reader = Mock(side_effect=AssertionError("candidate opened"))
        runner = PhysicalRunnerV04(reader)
        runner.validate_preconsumption(
            self.fixture.tsis_root,
            self.fixture.config_path,
            AuthorizationV04(self.fixture.state_path, self.fixture.spec_path),
        )
        reader.assert_not_called()

    def test_second_use_is_rejected_and_pass_evidence_is_unchanged(self) -> None:
        self.fixture.execute()
        final_before = (self.fixture.run_directory / "final_manifest.json").read_bytes()
        with self.assertRaisesRegex(EventStateContractError, "ALREADY_CONSUMED"):
            self.fixture.execute()
        self.assertEqual(
            (self.fixture.run_directory / "final_manifest.json").read_bytes(),
            final_before,
        )

    def test_candidate_hash_mismatch_consumes_and_fails_before_rows(self) -> None:
        candidate = self.fixture.tsis_root / self.fixture.spec["governed_inputs"][
            "candidate_jsonl"
        ]["relative_path"]
        original = candidate.read_bytes()
        candidate.write_bytes(b"X" + original[1:])
        with self.assertRaisesRegex(EventStateContractError, "PHYSICAL_INPUT_HASH"):
            self.fixture.execute()
        failure = json.loads(
            (self.fixture.run_directory / "failure_manifest.json").read_text()
        )
        self.assertTrue(failure["authorization_consumed"])
        self.assertEqual(failure["physical_data_files_opened"], 1)
        self.assertEqual(failure["physical_state_records_scanned"], 0)

    def test_reader_failure_records_attempted_zero_zero(self) -> None:
        with self.assertRaisesRegex(OSError, "before open"):
            self.fixture.execute(Mock(side_effect=OSError("before open")))
        failure = json.loads(
            (self.fixture.run_directory / "failure_manifest.json").read_text()
        )
        self.assertTrue(failure["physical_access_attempted"])
        self.assertFalse(failure["physical_access_started"])
        self.assertEqual(failure["physical_data_files_opened"], 0)
        self.assertEqual(failure["physical_state_records_scanned"], 0)

    def test_stale_physical_fingerprint_fails_after_eight_rows(self) -> None:
        self.fixture.row["quality_status"] = "mutated"
        lines = [json.dumps({"decoy": index}) for index in range(7)]
        lines.append(json.dumps(self.fixture.row, sort_keys=True, separators=(",", ":")))
        raw = ("\n".join(lines) + "\n").encode("utf-8")
        candidate = self.fixture.tsis_root / self.fixture.spec["governed_inputs"][
            "candidate_jsonl"
        ]["relative_path"]
        candidate.write_bytes(raw)
        self.fixture.spec["governed_inputs"]["candidate_jsonl"].update(
            {"sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
        )
        self.fixture.materialize()
        with self.assertRaisesRegex(EventStateContractError, "FINGERPRINT_MISMATCH"):
            self.fixture.execute()
        failure = json.loads(
            (self.fixture.run_directory / "failure_manifest.json").read_text()
        )
        self.assertEqual(failure["physical_state_records_scanned"], 8)

    def test_metadata_mutation_fails_before_consumption(self) -> None:
        binding = self.fixture.spec["governed_inputs"]["typed_payload_binding"]
        path = self.fixture.tsis_root / binding["relative_path"]
        original = path.read_bytes()
        path.write_bytes(b"X" + original[1:])
        with self.assertRaisesRegex(EventStateContractError, "METADATA_HASH"):
            self.fixture.execute()
        state = json.loads(self.fixture.state_path.read_text())
        self.assertEqual(state["status"], "AUTHORIZED_NOT_CONSUMED")
        self.assertFalse(self.fixture.run_directory.exists())

    def test_provider_handoff_must_be_a_valid_zip(self) -> None:
        binding = self.fixture.spec["governed_inputs"]["initial_provider_handoff"]
        path = self.fixture.tsis_root / binding["relative_path"]
        path.write_bytes(b"not-a-zip")
        binding.update({"sha256": sha256(path), "size_bytes": path.stat().st_size})
        self.fixture.materialize()
        with self.assertRaisesRegex(
            EventStateContractError, "PROVIDER_EVIDENCE_ZIP_INTEGRITY"
        ):
            self.fixture.execute()
        state = json.loads(self.fixture.state_path.read_text())
        self.assertEqual(state["status"], "AUTHORIZED_NOT_CONSUMED")
        self.assertFalse(self.fixture.run_directory.exists())

    def test_provider_handoff_cannot_embed_physical_state(self) -> None:
        binding = self.fixture.spec["governed_inputs"]["provider_completion_handoff"]
        path = self.fixture.tsis_root / binding["relative_path"]
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("event_state_candidate_records.jsonl", "{}\n")
        binding.update({"sha256": sha256(path), "size_bytes": path.stat().st_size})
        self.fixture.materialize()
        with self.assertRaisesRegex(
            EventStateContractError, "PROVIDER_EVIDENCE_SCOPE_LEAKAGE"
        ):
            self.fixture.execute()
        state = json.loads(self.fixture.state_path.read_text())
        self.assertEqual(state["status"], "AUTHORIZED_NOT_CONSUMED")
        self.assertFalse(self.fixture.run_directory.exists())

    def test_configuration_extra_field_fails_before_consumption(self) -> None:
        config = json.loads(self.fixture.config_path.read_text())
        config["unexpected"] = True
        write_json(self.fixture.config_path, config)
        state = json.loads(self.fixture.state_path.read_text())
        state["configuration_sha256"] = sha256(self.fixture.config_path)
        write_json(self.fixture.state_path, state)
        with self.assertRaisesRegex(EventStateContractError, "CLOSED_CONFIGURATION"):
            self.fixture.execute()
        self.assertFalse(self.fixture.run_directory.exists())

    def test_empty_binding_map_fails_before_consumption(self) -> None:
        state = json.loads(self.fixture.state_path.read_text())
        state["binding_sha256"] = {}
        write_json(self.fixture.state_path, state)
        with self.assertRaisesRegex(EventStateContractError, "BINDING_MISMATCH"):
            self.fixture.execute()
        self.assertFalse(self.fixture.run_directory.exists())

    def test_incomplete_binding_map_fails_before_consumption(self) -> None:
        state = json.loads(self.fixture.state_path.read_text())
        state["binding_sha256"].pop(next(iter(state["binding_sha256"])))
        write_json(self.fixture.state_path, state)
        with self.assertRaisesRegex(EventStateContractError, "BINDING_MISMATCH"):
            self.fixture.execute()
        self.assertFalse(self.fixture.run_directory.exists())

    def test_extra_binding_map_entry_fails_before_consumption(self) -> None:
        state = json.loads(self.fixture.state_path.read_text())
        state["binding_sha256"]["02_TSIS_BACKTEST_ENGINE/unapproved.py"] = "0" * 64
        write_json(self.fixture.state_path, state)
        with self.assertRaisesRegex(EventStateContractError, "BINDING_MISMATCH"):
            self.fixture.execute()
        self.assertFalse(self.fixture.run_directory.exists())

    def test_bound_transitive_module_mutation_fails_before_consumption(self) -> None:
        relative = "02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/event_state/consumer.py"
        path = self.fixture.tsis_root / relative
        path.write_bytes(path.read_bytes() + b"# mutation\n")
        with self.assertRaisesRegex(EventStateContractError, "BINDING_MISMATCH"):
            self.fixture.execute()
        self.assertFalse(self.fixture.run_directory.exists())
    def test_receipt_write_failure_is_durable_and_never_reads(self) -> None:
        reader = Mock(return_value=self.fixture.candidate_raw)
        authorization = AuthorizationV04(
            self.fixture.state_path, self.fixture.spec_path
        )
        with patch.object(
            authorization,
            "_write_receipt",
            side_effect=OSError("receipt write failure"),
        ):
            with self.assertRaisesRegex(OSError, "receipt write failure"):
                PhysicalRunnerV04(reader).execute(
                    self.fixture.tsis_root, self.fixture.config_path, authorization
                )
        reader.assert_not_called()
        state = json.loads(self.fixture.state_path.read_text())
        self.assertEqual(state["status"], CONSUMED_STATUS)
        failure = json.loads(
            (self.fixture.run_directory / "failure_manifest.json").read_text()
        )
        self.assertTrue(failure["authorization_consumed"])
        self.assertEqual(failure["physical_data_files_opened"], 0)

    def test_duplicate_selected_record_fails_closed(self) -> None:
        selected = json.dumps(self.fixture.row, sort_keys=True, separators=(",", ":"))
        raw = ("\n".join([json.dumps({"decoy": i}) for i in range(7)] + [selected, selected]) + "\n").encode("utf-8")
        candidate = self.fixture.tsis_root / self.fixture.spec["governed_inputs"][
            "candidate_jsonl"
        ]["relative_path"]
        candidate.write_bytes(raw)
        self.fixture.spec["selection"]["candidate_records_scanned"] = 9
        self.fixture.spec["governed_inputs"]["candidate_jsonl"].update(
            {"sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
        )
        self.fixture.materialize()
        with self.assertRaisesRegex(EventStateContractError, "SCOPE_LEAKAGE"):
            self.fixture.execute()

    def test_failure_and_success_metrics_never_enable_trading(self) -> None:
        final = self.fixture.execute()
        boundary = json.loads(
            (self.fixture.run_directory / "boundary_preservation_report.json").read_text()
        )
        self.assertFalse(boundary["market_state_physical_read"])
        self.assertFalse(boundary["strategy"])
        self.assertEqual((final["orders"], final["fills"], final["pnl_calculated"]), (0, 0, False))


class PhysicalEventStateV04CanonicalTests(unittest.TestCase):
    def test_canonical_preconsumption_bindings_are_complete_without_read(self) -> None:
        self.assertTrue(CANONICAL_SPEC.is_file())
        self.assertTrue(CANONICAL_CONFIG.is_file())
        self.assertTrue(CANONICAL_STATE.is_file())
        specification = json.loads(CANONICAL_SPEC.read_text(encoding="utf-8"))
        configuration = json.loads(CANONICAL_CONFIG.read_text(encoding="utf-8"))
        state = json.loads(CANONICAL_STATE.read_text(encoding="utf-8"))
        self.assertEqual(configuration["governed_inputs"], specification["governed_inputs"])
        self.assertEqual(len(specification["governed_inputs"]), 11)
        self.assertEqual(
            set(state["binding_sha256"]),
            set(specification["executable_binding_paths"]),
        )
        self.assertEqual(len(state["binding_sha256"]), 27)
        candidate = specification["governed_inputs"]["candidate_jsonl"]
        self.assertEqual(candidate["sha256"], "ed975ad7d7a3e0ac68bd7dfe2c91743c86931a545162a4440d270cbb689477dd")
        self.assertEqual(candidate["size_bytes"], 70001)
        for name, binding in specification["governed_inputs"].items():
            if name == "candidate_jsonl":
                continue
            path = TSIS_ROOT / binding["relative_path"]
            self.assertTrue(path.is_file(), name)
            self.assertEqual(sha256(path), binding["sha256"], name)
            if "size_bytes" in binding:
                self.assertEqual(path.stat().st_size, binding["size_bytes"], name)

    def test_living_changelogs_have_one_current_block_and_balanced_fences(self) -> None:
        paths = (
            ROOT / "CHANGELOG.md",
            TSIS_ROOT / "00_CTO/14_BACKTEST_ENGINE/CHANGELOG.md",
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            self.assertTrue(lines[0].startswith("## Current Authoritative State"), path)
            self.assertEqual(text.count("\n## Current Authoritative State"), 0, path)
            self.assertNotIn("text", {line.strip() for line in lines}, path)
            self.assertEqual(
                sum(line.startswith("```") for line in lines) % 2,
                0,
                path,
            )
    def test_previous_candidates_remain_non_executable(self) -> None:
        expected = {
            "v0_1": "DRAFT_SUPERSEDED_NEVER_AUTHORIZED",
            "v0_2": "DRAFT_NOT_AUTHORIZED_PENDING_PREEXECUTION_REVIEW",
            "v0_3": "CONSUMED_BY_RUN_bt_gate_015_single_use_physical_event_state_consumer_v0_3",
        }
        for version, status in expected.items():
            path = ROOT / "configs/authorizations" / (
                f"bt_gate_015_single_use_physical_event_state_consumer_{version}.json"
            )
            self.assertEqual(json.loads(path.read_text())["status"], status)

    def test_canonical_v04_state_records_single_successful_consumption(self) -> None:
        state = json.loads(CANONICAL_STATE.read_text())
        specification = json.loads(CANONICAL_SPEC.read_text())
        self.assertEqual(state["status"], CONSUMED_STATUS)
        self.assertEqual(state["consumed_by_run_id"], RUN_ID)
        self.assertEqual(state["authorization_consumption_count"], 1)
        self.assertEqual(state["event_state_physical_read"], "EXECUTED_PASS")
        self.assertEqual(state["physical_command_status"], "EXECUTED_ONCE_PASS")
        self.assertEqual(state["postexecution_review_status"], "PENDING_EXTERNAL_REVIEW")
        run_directory = ROOT / "runs" / RUN_ID
        self.assertTrue(run_directory.is_dir())
        final = json.loads((run_directory / "final_manifest.json").read_text())
        self.assertEqual(final["validation_status"], "PASS")
        self.assertEqual(final["physical_state_records_scanned"], 8)
        self.assertEqual(final["physical_state_rows_selected"], 1)
        self.assertEqual(final["event_state_events_emitted"], 1)
        self.assertEqual(final["event_state_store_inserts"], 1)
        self.assertEqual(final["bounded_probe_observations"], 1)
        self.assertEqual(final["delivery_before_available_at"], 0)
        self.assertEqual(
            (final["orders"], final["fills"], final["pnl_calculated"]),
            (0, 0, False),
        )
        dependency = specification["market_state_dependency"]
        self.assertNotEqual(
            dependency["dependency_dataset_fingerprint"],
            dependency["availability_evidence_dataset_fingerprint"],
        )

    def test_canonical_v04_output_hashes_resolve_to_written_artifacts(self) -> None:
        run_directory = ROOT / "runs" / RUN_ID
        final = json.loads((run_directory / "final_manifest.json").read_text())
        for name, expected in final["output_artifact_hashes"].items():
            self.assertEqual(sha256(run_directory / name), expected, name)
        failure = json.loads((run_directory / "failure_manifest.json").read_text())
        self.assertEqual(failure["status"], "SUPERSEDED_BY_FINAL_MANIFEST_PASS")

if __name__ == "__main__":
    unittest.main()
