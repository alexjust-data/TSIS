from __future__ import annotations

import copy
import hashlib
import json
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path

from tsis_backtest.event_state.acceptance import EventStateAcceptanceMatrix
from tsis_backtest.event_state.consumer import EventStateConsumerV0_1
from tsis_backtest.event_state.contracts import EventStateContractError
from tsis_backtest.event_state.store import EventStateStore
from tsis_backtest.market_state.consumer import MarketStateConsumerV0_1

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/bt_gate_015_synthetic_event_state"


def documents():
    rows = json.loads((FIXTURE / "synthetic_event_state_rows.json").read_text(encoding="utf-8"))
    side_path = FIXTURE / "synthetic_event_state_sidecar.json"
    return rows, json.loads(side_path.read_text(encoding="utf-8")), hashlib.sha256(side_path.read_bytes()).hexdigest()


class EventStateConsumerTests(unittest.TestCase):
    def setUp(self):
        self.consumer = EventStateConsumerV0_1()
        self.rows, self.side, self.side_hash = documents()
        config = json.loads((ROOT / "configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json").read_text(encoding="utf-8"))
        market_row = json.loads((FIXTURE / "synthetic_market_state_row.json").read_text(encoding="utf-8"))
        market_side_path = FIXTURE / "synthetic_market_state_sidecar_record.json"
        market_side = json.loads(market_side_path.read_text(encoding="utf-8"))
        self.market = MarketStateConsumerV0_1().validate_and_seal(
            market_row, market_side, config["authority"],
            hashlib.sha256(market_side_path.read_bytes()).hexdigest(),
        ).event

    def validated(self):
        return self.consumer.join_document(copy.deepcopy(self.rows), copy.deepcopy(self.side), self.side_hash, self.market)[0]

    def code(self, expected, action):
        with self.assertRaises(EventStateContractError) as ctx:
            action()
        self.assertEqual(ctx.exception.code, expected)

    def test_provider_compatible_shapes_and_payload(self):
        validated = self.validated()
        self.assertEqual(validated.event.schema_id, "event_state_candidate_schema_v0_1")
        self.assertEqual(len(validated.event.audit_lineage.source_event_state_envelope), 39)
        self.assertEqual(validated.event.audit_lineage.physical_source_rows, 0)

    def test_payload_mutation_with_stale_fingerprint_fails(self):
        rows = copy.deepcopy(self.rows)
        payload = json.loads(rows["records"][0]["source_market_state_value_snapshot_json"])
        payload["price_movement__daily_gap_pct"] = 999.0
        rows["records"][0]["source_market_state_value_snapshot_json"] = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self.code("FAIL_EVENT_STATE_FINGERPRINT_MISMATCH", lambda: self.consumer.join_document(rows, self.side, self.side_hash, self.market))

    def test_missing_contract_surfaces_fail_explicitly(self):
        side = copy.deepcopy(self.side); del side["records"][0]["event_state_available_at_utc"]
        self.code("FAIL_EVENT_STATE_TEMPORAL_EVIDENCE_MISSING", lambda: self.consumer.join_document(self.rows, side, self.side_hash, self.market))
        rows = copy.deepcopy(self.rows); del rows["records"][0]["source_market_state_value_snapshot_json"]
        self.code("FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISSING", lambda: self.consumer.join_document(rows, self.side, self.side_hash, self.market))
        side = copy.deepcopy(self.side); side["records"][0]["component_replay_restriction_codes"] = {}
        self.code("FAIL_EVENT_STATE_COMPONENT_RESTRICTIONS_NOT_AUTHORIZED", lambda: self.consumer.join_document(self.rows, side, self.side_hash, self.market))

    def test_store_rejects_forged_receipts(self):
        valid = self.validated(); event = valid.event
        for field, value in (("validator_id", "forged"), ("schema_version", "forged"), ("consumed_sidecar_sha256", "0" * 64)):
            forged = replace(valid, receipt=replace(valid.receipt, **{field: value}))
            self.code("FAIL_EVENT_STATE_STORE_INVALID_VALIDATION_RECEIPT", lambda f=forged: EventStateStore().insert(f, event.event_state_available_at_utc))

    def test_provider_sidecar_document_is_accepted_exactly(self):
        handoff = ROOT / "evidence/provider_handoffs/bt_gate_015/event_state_session_opened_bt_gate_015_provider_completion_v0_1_20260731T071317Z.zip"
        internal = "09_STATE_CONSUMPTION_BOUNDARY/event_state_session_opened_replay_availability_sidecar_manifest_v0_1.json"
        with zipfile.ZipFile(handoff) as archive:
            document = json.loads(archive.read(internal))
        records = self.consumer.validate_sidecar_document(document)
        self.assertEqual(len(records), 1)
        self.assertIn("market_state_dependency_dataset_fingerprint", records[0])
        self.assertIn("market_state_availability_evidence_dataset_fingerprint", records[0])
        self.assertIn("evidence_refs", records[0])

    def test_acceptance_matrix_is_execution_generated(self):
        report = EventStateAcceptanceMatrix(FIXTURE).execute()
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["report_generated_from_executions"])
        self.assertEqual(report["positive_case_count"], 7)
        self.assertEqual(report["negative_case_count"], 22)
        self.assertEqual(report["failed_case_count"], 0)
        self.assertEqual(report["missing_required_contract_failure_codes"], [])


if __name__ == "__main__":
    unittest.main()
