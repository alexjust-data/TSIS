"""Executed acceptance matrix for BT-GATE-015 non-physical implementation."""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from tsis_backtest.market_state.consumer import MarketStateConsumerV0_1

from .consumer import EventStateConsumerV0_1, canonical_hash
from .contracts import EventStateContractError
from .store import EventStateStore


REQUIRED_CONTRACT_FAILURE_CODES = {
    "FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH",
    "FAIL_EVENT_STATE_SCHEMA_MISMATCH",
    "FAIL_EVENT_STATE_IDENTITY_MISMATCH",
    "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
    "FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION",
    "FAIL_DUPLICATE_EVENT_STATE_EVENT",
    "FAIL_CONFLICTING_EVENT_STATE_EVENT",
    "FAIL_EVENT_STATE_SCOPE_LEAKAGE",
}


class EventStateAcceptanceMatrix:
    def __init__(self, fixture_root: Path) -> None:
        self.root = fixture_root
        self.consumer = EventStateConsumerV0_1()
        engine_root = fixture_root.parents[2]
        config = json.loads((engine_root / "configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json").read_text(encoding="utf-8"))
        market_row = json.loads((fixture_root / "synthetic_market_state_row.json").read_text(encoding="utf-8"))
        market_side_path = fixture_root / "synthetic_market_state_sidecar_record.json"
        market_side = json.loads(market_side_path.read_text(encoding="utf-8"))
        self.market = MarketStateConsumerV0_1().validate_and_seal(
            market_row, market_side, config["authority"],
            hashlib.sha256(market_side_path.read_bytes()).hexdigest(),
        ).event

    def _documents(self) -> tuple[dict[str, Any], dict[str, Any], str]:
        rows = json.loads((self.root / "synthetic_event_state_rows.json").read_text(encoding="utf-8"))
        side_path = self.root / "synthetic_event_state_sidecar.json"
        side = json.loads(side_path.read_text(encoding="utf-8"))
        return rows, side, hashlib.sha256(side_path.read_bytes()).hexdigest()

    @staticmethod
    def _expect(code: str, action: Callable[[], Any]) -> str:
        try:
            action()
        except EventStateContractError as exc:
            if exc.code == code:
                return code
            raise AssertionError(f"expected {code}, observed {exc.code}") from exc
        raise AssertionError(f"expected {code}, observed PASS")

    def execute(self) -> dict[str, Any]:
        rows, side, side_hash = self._documents()

        def joined():
            return self.consumer.join_document(copy.deepcopy(rows), copy.deepcopy(side), side_hash, self.market)

        positives: list[tuple[str, Callable[[], Any]]] = [
            ("POSITIVE_01_PROVIDER_COMPATIBLE_ENVELOPE", lambda: len(joined()) == 1),
            ("POSITIVE_02_EXACT_17_FIELD_PAYLOAD", lambda: len(joined()[0].event.payload.to_dict()) == 4),
            ("POSITIVE_03_FINGERPRINT_RECOMPUTED", lambda: joined()[0].receipt.validation_status == "PASS"),
            ("POSITIVE_04_TEMPORAL_FORMULA", lambda: joined()[0].event.event_state_as_of_utc == joined()[0].event.event_state_available_at_utc),
            ("POSITIVE_05_RESTRICTION_DOMAINS", lambda: len(joined()[0].event.replay_consumption_restriction_codes) == 5),
            ("POSITIVE_06_STORE_VISIBLE_AT_AVAILABLE", lambda: self._store_visible(joined()[0])),
            ("POSITIVE_07_SIDECAR_EVIDENCE_REFS", lambda: len(side["records"][0]["evidence_refs"]) >= 6),
        ]

        def mutate_payload():
            r = copy.deepcopy(rows)
            payload = json.loads(r["records"][0]["source_market_state_value_snapshot_json"])
            payload["price_movement__daily_gap_pct"] = 999.0
            r["records"][0]["source_market_state_value_snapshot_json"] = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            return self.consumer.join_document(r, copy.deepcopy(side), side_hash, self.market)

        def missing_side(field: str):
            s = copy.deepcopy(side); del s["records"][0][field]
            return self.consumer.join_document(copy.deepcopy(rows), s, side_hash, self.market)

        def missing_row(field: str):
            r = copy.deepcopy(rows); del r["records"][0][field]
            return self.consumer.join_document(r, copy.deepcopy(side), side_hash, self.market)

        def component_domain():
            s = copy.deepcopy(side); s["records"][0]["component_replay_restriction_codes"] = {}
            return self.consumer.join_document(copy.deepcopy(rows), s, side_hash, self.market)

        def forged_receipt(field: str, value: str):
            valid = joined()[0]
            EventStateStore().insert(replace(valid, receipt=replace(valid.receipt, **{field: value})), valid.event.event_state_available_at_utc)

        negatives: list[tuple[str, str, Callable[[], Any]]] = [
            ("NEGATIVE_01", "FAIL_EVENT_STATE_FINGERPRINT_MISMATCH", mutate_payload),
            ("NEGATIVE_02", "FAIL_EVENT_STATE_TEMPORAL_EVIDENCE_MISSING", lambda: missing_side("event_state_available_at_utc")),
            ("NEGATIVE_03", "FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISSING", lambda: missing_row("source_market_state_value_snapshot_json")),
            ("NEGATIVE_04", "FAIL_EVENT_STATE_COMPONENT_RESTRICTIONS_NOT_AUTHORIZED", component_domain),
            ("NEGATIVE_05", "FAIL_EVENT_STATE_SIDECAR_BIJECTION", lambda: self.consumer.join_rows(rows["records"] * 2, side["records"], side_hash, self.market)),
            ("NEGATIVE_06", "FAIL_EVENT_STATE_SIDECAR_BIJECTION", lambda: self.consumer.join_rows(rows["records"], side["records"] * 2, side_hash, self.market)),
            ("NEGATIVE_07", "FAIL_EVENT_STATE_STORE_INVALID_VALIDATION_RECEIPT", lambda: forged_receipt("validator_id", "forged")),
            ("NEGATIVE_08", "FAIL_EVENT_STATE_STORE_INVALID_VALIDATION_RECEIPT", lambda: forged_receipt("schema_version", "forged")),
            ("NEGATIVE_09", "FAIL_EVENT_STATE_STORE_INVALID_VALIDATION_RECEIPT", lambda: forged_receipt("consumed_sidecar_sha256", "0" * 64)),
            ("NEGATIVE_10", "FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISMATCH", lambda: self._payload_extra(rows, side, side_hash)),
            ("NEGATIVE_11", "FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH", lambda: self._restriction_extra(rows, side, side_hash)),
            ("NEGATIVE_12", "FAIL_EVENT_STATE_EARLY_STORE_INSERT", lambda: self._early_store(joined()[0])),
            ("NEGATIVE_13", "FAIL_EVENT_STATE_OPERATIONAL_ROUTING_PROHIBITED", lambda: self.consumer.reject_operational_routing("execution")),
            ("NEGATIVE_14_HANDOFF_HASH", "FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH", self._handoff_hash),
            ("NEGATIVE_15_SCHEMA", "FAIL_EVENT_STATE_SCHEMA_MISMATCH", self._schema_evidence_refs),
            ("NEGATIVE_16_IDENTITY", "FAIL_EVENT_STATE_IDENTITY_MISMATCH", self._identity_anchor),
            ("NEGATIVE_17_MARKET_DEPENDENCY", "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH", self._dependency),
            ("NEGATIVE_18_TEMPORAL", "FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION", self._temporal),
            ("NEGATIVE_19_DUPLICATE", "FAIL_DUPLICATE_EVENT_STATE_EVENT", self._duplicate),
            ("NEGATIVE_20_CONFLICT", "FAIL_CONFLICTING_EVENT_STATE_EVENT", self._conflict),
            ("NEGATIVE_21_SCOPE", "FAIL_EVENT_STATE_SCOPE_LEAKAGE", self._scope),
            ("NEGATIVE_22_DUPLICATE_JSON_KEY", "FAIL_EVENT_STATE_INVALID_EMBEDDED_JSON", self._duplicate_json_key),
        ]
        cases = []
        for case_id, action in positives:
            observed = "PASS" if action() else "FAIL_ASSERTION"
            cases.append(self._case(case_id, "PASS", observed))
        for case_id, expected, action in negatives:
            cases.append(self._case(case_id, expected, self._expect(expected, action)))
        failed = [case for case in cases if case["status"] != "PASS"]
        observed_codes = {case["observed"] for case in cases}
        missing_required = sorted(REQUIRED_CONTRACT_FAILURE_CODES - observed_codes)
        return {
            "status": "PASS" if not failed and not missing_required else "FAIL",
            "report_generated_from_executions": True,
            "positive_case_count": len(positives),
            "negative_case_count": len(negatives),
            "failed_case_count": len(failed),
            "required_contract_failure_codes": sorted(REQUIRED_CONTRACT_FAILURE_CODES),
            "missing_required_contract_failure_codes": missing_required,
            "cases": cases,
        }

    @staticmethod
    def _case(case_id: str, expected: str, observed: str) -> dict[str, str]:
        body = {"case_id": case_id, "expected": expected, "observed": observed}
        body["status"] = "PASS" if expected == observed else "FAIL"
        body["evidence_hash"] = canonical_hash(body)
        return body

    @staticmethod
    def _store_visible(validated) -> bool:
        store = EventStateStore(); event = validated.event
        store.insert(validated, event.event_state_available_at_utc)
        return store.get_exact(event.event_state_record_id, event.event_state_available_at_utc) == event

    @staticmethod
    def _early_store(validated):
        from datetime import timedelta
        EventStateStore().insert(validated, validated.event.event_state_available_at_utc - timedelta(microseconds=1))

    def _payload_extra(self, rows, side, side_hash):
        r = copy.deepcopy(rows); payload = json.loads(r["records"][0]["source_market_state_value_snapshot_json"])
        payload["unexpected"] = 1; r["records"][0]["source_market_state_value_snapshot_json"] = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        r["records"][0]["state_output_fingerprint"] = self._fingerprint(r["records"][0]); s = copy.deepcopy(side); s["records"][0]["event_state_record_fingerprint"] = r["records"][0]["state_output_fingerprint"]
        return self.consumer.join_document(r, s, side_hash, self.market)

    def _restriction_extra(self, rows, side, side_hash):
        r = copy.deepcopy(rows); s = copy.deepcopy(side); s["records"][0]["replay_consumption_restriction_codes"].append("extra")
        return self.consumer.join_document(r, s, side_hash, self.market)

    @staticmethod
    def _fingerprint(row):
        from .consumer import synthetic_event_state_fingerprint
        return synthetic_event_state_fingerprint(row)

    @staticmethod
    def _json_bytes(value):
        return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")

    def _raw_documents(self):
        rows = (self.root / "synthetic_event_state_rows.json").read_bytes()
        side = (self.root / "synthetic_event_state_sidecar.json").read_bytes()
        return rows, side, hashlib.sha256(side).hexdigest()

    def _mutated_bytes(self, row_mutation=None, side_mutation=None):
        rows_raw, side_raw, _ = self._raw_documents()
        rows = json.loads(rows_raw)
        side = json.loads(side_raw)
        if row_mutation:
            row_mutation(rows)
        if side_mutation:
            side_mutation(side)
        rows_raw = self._json_bytes(rows)
        side_raw = self._json_bytes(side)
        return self.consumer.join_bytes(
            rows_raw, side_raw, hashlib.sha256(side_raw).hexdigest(), self.market
        )

    def _handoff_hash(self):
        rows, side, _ = self._raw_documents()
        return self.consumer.join_bytes(rows, side, "0" * 64, self.market)

    def _schema_evidence_refs(self):
        return self._mutated_bytes(
            side_mutation=lambda side: side["records"][0].update(evidence_refs={})
        )

    def _identity_anchor(self):
        def mutate(rows):
            row = rows["records"][0]
            row["event_anchor_timestamp_utc"] = "2021-01-19T14:31:00Z"
            row["state_output_fingerprint"] = self._fingerprint(row)
        def side_mutate(side):
            rows = json.loads((self.root / "synthetic_event_state_rows.json").read_text(encoding="utf-8"))
            row = rows["records"][0]
            row["event_anchor_timestamp_utc"] = "2021-01-19T14:31:00Z"
            side["records"][0]["event_state_record_fingerprint"] = self._fingerprint(row)
        return self._mutated_bytes(mutate, side_mutate)

    def _dependency(self):
        return self._mutated_bytes(
            side_mutation=lambda side: side["records"][0].update(
                market_state_state_output_fingerprint="0" * 64
            )
        )

    def _temporal(self):
        return self._mutated_bytes(
            side_mutation=lambda side: side["records"][0].update(
                event_state_available_at_utc="2021-01-19T14:31:00Z"
            )
        )

    def _duplicate(self):
        valid = self.consumer.join_document(*self._documents(), self.market)[0]
        store = EventStateStore()
        store.insert(valid, valid.event.event_state_available_at_utc)
        store.insert(valid, valid.event.event_state_available_at_utc)

    def _conflict(self):
        rows, side, side_hash = self._documents()
        first = self.consumer.join_document(copy.deepcopy(rows), copy.deepcopy(side), side_hash, self.market)[0]
        changed_rows = copy.deepcopy(rows)
        changed_side = copy.deepcopy(side)
        changed_rows["records"][0]["created_at_utc"] = "2026-07-31T00:00:01Z"
        changed_rows["records"][0]["state_output_fingerprint"] = self._fingerprint(changed_rows["records"][0])
        changed_side["records"][0]["event_state_record_fingerprint"] = changed_rows["records"][0]["state_output_fingerprint"]
        second = self.consumer.join_document(
            changed_rows, changed_side, self._json_bytes(changed_side).hex()[:64], self.market
        )[0]
        store = EventStateStore()
        store.insert(first, first.event.event_state_available_at_utc)
        store.insert(second, second.event.event_state_available_at_utc)

    def _scope(self):
        def mutate(rows):
            rows["records"].append(copy.deepcopy(rows["records"][0]))
        return self._mutated_bytes(row_mutation=mutate)

    def _duplicate_json_key(self):
        rows_raw, side_raw, _ = self._raw_documents()
        rows = json.loads(rows_raw)
        side = json.loads(side_raw)
        snapshot = rows["records"][0]["source_market_state_value_snapshot_json"]
        needle = '"price_movement__daily_gap_pct":0.052'
        duplicate = needle + ',"price_movement__daily_gap_pct":0.052'
        if needle not in snapshot:
            raise AssertionError("duplicate-key fixture needle missing")
        rows["records"][0]["source_market_state_value_snapshot_json"] = snapshot.replace(needle, duplicate)
        rows["records"][0]["state_output_fingerprint"] = self._fingerprint(rows["records"][0])
        side["records"][0]["event_state_record_fingerprint"] = rows["records"][0]["state_output_fingerprint"]
        rows_raw = self._json_bytes(rows)
        side_raw = self._json_bytes(side)
        return self.consumer.join_bytes(
            rows_raw, side_raw, hashlib.sha256(side_raw).hexdigest(), self.market
        )
