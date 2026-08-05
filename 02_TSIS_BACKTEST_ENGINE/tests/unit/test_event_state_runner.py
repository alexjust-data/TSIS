import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tsis_backtest.event_state.contracts import EventStateContractError
from tsis_backtest.event_state.runner import SyntheticEventStateRunRequest, SyntheticEventStateRunner

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "configs/runs/bt_gate_015_non_physical_event_state_consumer_v0_1.json").read_text())


def req(out, **changes):
    values = dict(
        run_id=CFG["run_id"],
        fixture_root=ROOT / CFG["fixture_root"],
        output_root=Path(out),
        initial_handoff=ROOT / CFG["initial_handoff"],
        completion_handoff=ROOT / CFG["completion_handoff"],
        physical_read_authorized=False,
    )
    values.update(changes)
    return SyntheticEventStateRunRequest(**values)


class EventStateRunnerTests(unittest.TestCase):
    def test_cross_root_determinism(self):
        runner = SyntheticEventStateRunner()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.assertEqual(runner.run(req(a))["deterministic_output_hash"], runner.run(req(b))["deterministic_output_hash"])

    def test_physical_read_fails_closed(self):
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaisesRegex(EventStateContractError, "PHYSICAL_READ_NOT_AUTHORIZED"):
                SyntheticEventStateRunner().run(req(out, physical_read_authorized=True))

    def test_handoff_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as out:
            bad = Path(out) / "bad.zip"
            bad.write_bytes(b"not-provider-evidence")
            with self.assertRaisesRegex(EventStateContractError, "HANDOFF_HASH_MISMATCH"):
                SyntheticEventStateRunner().run(req(out, initial_handoff=bad))

    def test_written_manifest_resolves_artifacts(self):
        runner = SyntheticEventStateRunner()
        with tempfile.TemporaryDirectory() as out:
            request = req(out)
            result = runner.run(request)
            run_dir = runner.write_result(request, result, {"status": "PASS"})
            final = json.loads((run_dir / "final_manifest.json").read_text())
            for name, expected in final["output_artifact_hashes"].items():
                self.assertEqual(hashlib.sha256((run_dir / name).read_bytes()).hexdigest(), expected)
            self.assertEqual(final["physical_state_rows_read"], 0)

    def test_sequence_uses_accepted_real_market_state_type(self):
        with tempfile.TemporaryDirectory() as out:
            result = SyntheticEventStateRunner().run(req(out))
            self.assertEqual(
                [item["event_type"] for item in result["semantic"]["event_sequence"]],
                ["BAR", "BoundedMarketStateAvailable", "BoundedEventStateAvailable"],
            )
            self.assertNotIn("+00:00", json.dumps(result["semantic"]["event_sequence"]))

    def test_acceptance_outputs_are_materialized_from_executions(self):
        from tsis_backtest.event_state.acceptance import EventStateAcceptanceMatrix
        runner = SyntheticEventStateRunner()
        with tempfile.TemporaryDirectory() as out:
            request = req(out); result = runner.run(request)
            report = EventStateAcceptanceMatrix(request.fixture_root).execute()
            run_dir = runner.write_result(request, result, report)
            self.assertTrue(report["report_generated_from_executions"])
            for name in ("availability_sidecar_validation_report.json", "typed_payload_binding_report.json", "fingerprint_and_dependency_report.json", "restriction_domain_report.json"):
                self.assertTrue((run_dir / name).is_file(), name)

    def test_provider_compatible_fixture_has_full_envelope(self):
        rows = json.loads((ROOT / CFG["fixture_root"] / "synthetic_event_state_rows.json").read_text())
        side = json.loads((ROOT / CFG["fixture_root"] / "synthetic_event_state_sidecar.json").read_text())
        self.assertEqual(len(rows["records"][0]), 39)
        self.assertEqual(set(side), {"sidecar_id", "state_kind", "profile_id", "event_type_id", "publication_policy", "record_count", "records"})
        for required in ("market_state_dependency_dataset_fingerprint", "market_state_availability_evidence_dataset_fingerprint", "evidence_refs"):
            self.assertIn(required, side["records"][0])


if __name__ == "__main__":
    unittest.main()
