from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from tsis_backtest.market_state.consumer import (
    FINGERPRINT_FIELDS,
    ID_FIELDS,
    MarketStateConsumerV0_1,
    _normalize,
    canonical_hash,
)
from tsis_backtest.market_state.contracts import (
    EXPECTED_RESTRICTIONS,
    MarketStateContractError,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/bt_gate_014_synthetic_market_state"
CONFIG = ROOT / "configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json"
PHYSICAL_CODES = tuple(f"physical_provenance_{index:02d}" for index in range(26))


class RestrictionDomainBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.consumer = MarketStateConsumerV0_1()
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.row = json.loads(
            (FIXTURE / "synthetic_raw_rows.json").read_text(encoding="utf-8")
        )["records"][0]
        self.sidecar = json.loads(
            (FIXTURE / "synthetic_sidecar.json").read_text(encoding="utf-8")
        )["records"][0]
        self.sidecar_hash = hashlib.sha256(
            (FIXTURE / "synthetic_sidecar.json").read_bytes()
        ).hexdigest()

    def physical_row(self) -> tuple[dict, dict]:
        row = copy.deepcopy(self.row)
        sidecar = copy.deepcopy(self.sidecar)
        row["restriction_codes_json"] = json.dumps(
            PHYSICAL_CODES, separators=(",", ":")
        )
        state_fingerprint = canonical_hash(
            {field: _normalize(row[field]) for field in FINGERPRINT_FIELDS}
        )
        row["state_output_fingerprint"] = state_fingerprint
        sidecar["state_output_fingerprint"] = state_fingerprint
        candidate_id = canonical_hash(
            {
                field: (
                    state_fingerprint
                    if field == "state_output_fingerprint"
                    else _normalize(row[field])
                )
                for field in ID_FIELDS
            }
        )
        row["materialized_state_candidate_id"] = candidate_id
        sidecar["materialized_state_candidate_id"] = candidate_id
        return row, sidecar

    def test_physical_provenance_is_preserved_but_not_executable_policy(self) -> None:
        row, sidecar = self.physical_row()
        event = self.consumer.build_event(
            row, sidecar, self.config["authority"], self.sidecar_hash
        )
        self.assertEqual(
            event.audit_lineage.physical_provenance_restriction_codes,
            PHYSICAL_CODES,
        )
        self.assertEqual(
            event.replay_consumption_restriction_codes,
            EXPECTED_RESTRICTIONS,
        )
        self.assertNotEqual(
            event.audit_lineage.physical_provenance_restriction_codes,
            event.replay_consumption_restriction_codes,
        )

    def test_component_replay_restrictions_may_be_labelled_subsets(self) -> None:
        row, sidecar = self.physical_row()
        for index, component in enumerate(
            sidecar["component_availability_evidence"]
        ):
            component["restriction_codes"] = list(
                EXPECTED_RESTRICTIONS[: index % 4 + 1]
            )
        event = self.consumer.build_event(
            row, sidecar, self.config["authority"], self.sidecar_hash
        )
        self.assertEqual(len(event.component_replay_restriction_codes), 4)
        for _, codes in event.component_replay_restriction_codes:
            self.assertTrue(set(codes).issubset(set(EXPECTED_RESTRICTIONS)))

    def test_component_replay_extra_is_rejected(self) -> None:
        row, sidecar = self.physical_row()
        sidecar["component_availability_evidence"][0]["restriction_codes"].append(
            "physical_only_code"
        )
        with self.assertRaises(MarketStateContractError) as raised:
            self.consumer.build_event(
                row, sidecar, self.config["authority"], self.sidecar_hash
            )
        self.assertEqual(
            raised.exception.code,
            "FAIL_MARKET_STATE_RESTRICTION_PROPAGATION",
        )

    def test_serialized_event_uses_domain_labelled_fields(self) -> None:
        row, sidecar = self.physical_row()
        event = self.consumer.build_event(
            row, sidecar, self.config["authority"], self.sidecar_hash
        ).to_dict()
        self.assertIn("replay_consumption_restriction_codes", event)
        self.assertIn("component_replay_restriction_codes", event)
        self.assertIn(
            "physical_provenance_restriction_codes", event["audit_lineage"]
        )
        self.assertIn(
            "physical_restriction_codes_raw_json", event["audit_lineage"]
        )
        self.assertNotIn("restriction_codes", event)


if __name__ == "__main__":
    unittest.main()
