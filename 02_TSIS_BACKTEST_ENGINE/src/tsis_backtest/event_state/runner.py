"""Reproducible non-physical acceptance runner for BT-GATE-015."""
from __future__ import annotations

import hashlib
import json

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.market_state.consumer import MarketStateConsumerV0_1
from tsis_backtest.replay.contracts import ReplayBarEvent

from .consumer import (
    EventStateConsumerV0_1,
    PROVIDER_COMPLETION_HANDOFF_SHA256,
    PROVIDER_CONTRACT_HANDOFF_SHA256,
    canonical_hash,
    event_state_aware_order_key,
    utc,
)
from .contracts import (
    BoundedEventStateAvailable,
    EventStateContractError,
    to_event_state_jsonable,
)
from .store import EventStateStore


@dataclass(frozen=True)
class SyntheticEventStateRunRequest:
    run_id: str
    fixture_root: Path
    output_root: Path
    initial_handoff: Path
    completion_handoff: Path
    physical_read_authorized: bool = False


class SyntheticEventStateRunner:
    def __init__(self) -> None:
        self.consumer = EventStateConsumerV0_1()

    def run(self, request: SyntheticEventStateRunRequest) -> dict[str, Any]:
        if request.physical_read_authorized:
            raise EventStateContractError(
                "FAIL_BT_GATE_015_PHYSICAL_READ_NOT_AUTHORIZED", request.run_id
            )
        for path, expected in (
            (request.initial_handoff, PROVIDER_CONTRACT_HANDOFF_SHA256),
            (request.completion_handoff, PROVIDER_COMPLETION_HANDOFF_SHA256),
        ):
            if path.suffix.lower() != ".zip":
                raise EventStateContractError("FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH", str(path))
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise EventStateContractError("FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH", path.name)
            with zipfile.ZipFile(path) as archive:
                if any(name.lower().endswith((".parquet", ".jsonl")) for name in archive.namelist()):
                    raise EventStateContractError("FAIL_BT_GATE_015_PHYSICAL_READ_NOT_AUTHORIZED", path.name)
                if archive.testzip() is not None:
                    raise EventStateContractError("FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH", path.name)
        manifest = self._json(request.fixture_root / "synthetic_fixture_manifest.json")
        expected_names = {
            "synthetic_event_state_rows.json",
            "synthetic_event_state_sidecar.json",
            "synthetic_market_state_row.json",
            "synthetic_market_state_sidecar_record.json",
            "synthetic_ordering_bar.json",
        }
        if set(manifest["files"]) != expected_names:
            raise EventStateContractError("FAIL_SYNTHETIC_EVENT_STATE_MANIFEST_COVERAGE", "closed inventory")
        docs = {}
        identities = {}
        for name, declared in manifest["files"].items():
            path = request.fixture_root / name
            before = path.read_bytes()
            actual = hashlib.sha256(before).hexdigest()
            if actual != declared["sha256"] or len(before) != declared["size_bytes"]:
                raise EventStateContractError("FAIL_SYNTHETIC_EVENT_STATE_INPUT_HASH_MISMATCH", name)
            docs[name] = json.loads(before.decode("utf-8"))
            after = path.read_bytes()
            if hashlib.sha256(after).hexdigest() != actual:
                raise EventStateContractError("FAIL_SOURCE_MUTATION", name)
            identities[name] = {"sha256_before": actual, "sha256_after": actual, "size_bytes": len(before)}
        side_hash = identities["synthetic_event_state_sidecar.json"]["sha256_before"]
        market = self._market_state_dependency_event(request, docs)
        validated = self.consumer.join_bytes(
            (request.fixture_root / "synthetic_event_state_rows.json").read_bytes(),
            (request.fixture_root / "synthetic_event_state_sidecar.json").read_bytes(),
            side_hash,
            market,
        )
        if len(validated) != 1:
            raise EventStateContractError("FAIL_EVENT_STATE_SCOPE_LEAKAGE", str(len(validated)))
        event = validated[0].event
        bar_doc = docs["synthetic_ordering_bar.json"]
        bar_value = MarketDataBar1m(
            bar_doc["ticker"], utc(bar_doc["ts_start"]), utc(bar_doc["ts_end"]),
            utc(bar_doc["available_at"]), bar_doc["session_label"],
            float(bar_doc["open"]), float(bar_doc["high"]), float(bar_doc["low"]),
            float(bar_doc["close"]), int(bar_doc["volume"]), bar_doc["price_view"],
        )
        bar = ReplayBarEvent("BAR", event.ticker, bar_value.available_at, bar_value, {"synthetic": True})
        ordered = tuple(sorted((event, market, bar), key=event_state_aware_order_key))
        if [item.event_type for item in ordered] != ["BAR", "BoundedMarketStateAvailable", "BoundedEventStateAvailable"]:
            raise EventStateContractError("FAIL_EVENT_STATE_EQUAL_TIMESTAMP_PRIORITY", "sequence")
        store = EventStateStore()
        sequence = []
        observations = []
        for index, item in enumerate(ordered):
            sequence.append({
                "index": index,
                "event_type": item.event_type,
                "order_key": event_state_aware_order_key(item),
            })
            if isinstance(item, BoundedEventStateAvailable):
                insert = store.insert(validated[0], item.event_state_available_at_utc)
                visible = store.get_exact(item.event_state_record_id, item.event_state_available_at_utc)
                if visible is None:
                    raise EventStateContractError("FAIL_EVENT_STATE_OBSERVATION_BEFORE_STORE", item.event_state_record_id)
                observations.append({
                    "event_state_record_id": item.event_state_record_id,
                    "observed_at_utc": item.event_state_available_at_utc,
                    "store_insert_sequence": insert,
                    "typed_payload_field_count": 17,
                })
        semantic = {
            "event_sequence": sequence,
            "market_state_dependency": {
                "validated_event_type": market.event_type,
                "materialized_state_candidate_id": market.materialized_state_candidate_id,
                "state_output_fingerprint": market.state_output_fingerprint,
                "payload_sha256": canonical_hash(market.payload.to_dict()),
                "event_state_declared_record_id": event.market_state_record_id,
                "event_state_declared_fingerprint": event.market_state_state_output_fingerprint,
                "identity_match": market.materialized_state_candidate_id == event.market_state_record_id,
                "fingerprint_match": market.state_output_fingerprint == event.market_state_state_output_fingerprint,
                "payload_match": canonical_hash(market.payload.to_dict()) == canonical_hash(event.payload.to_dict()),
            },
            "event": event.to_dict(),
            "store_trace": to_event_state_jsonable(store.trace),
            "observations": observations,
        }
        semantic = to_event_state_jsonable(semantic)
        return {
            "gate_id": "BT-GATE-015",
            "validation_status": "PASS",
            "physical_data_files_opened": 0,
            "physical_state_rows_read": 0,
            "event_state_events": 1,
            "store_inserts": store.count,
            "observations": len(observations),
            "strategy_callbacks": 0,
            "orders": 0,
            "fills": 0,
            "pnl_calculated": False,
            "input_identities": identities,
            "semantic": semantic,
            "deterministic_output_hash": canonical_hash(semantic),
        }

    @staticmethod
    def _market_state_dependency_event(request: SyntheticEventStateRunRequest, docs: dict[str, Any]):
        root = request.fixture_root.parents[2]
        config = json.loads(
            (root / "configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json").read_text(encoding="utf-8")
        )
        side_path = request.fixture_root / "synthetic_market_state_sidecar_record.json"
        return MarketStateConsumerV0_1().validate_and_seal(
            docs["synthetic_market_state_row.json"],
            docs["synthetic_market_state_sidecar_record.json"],
            config["authority"],
            hashlib.sha256(side_path.read_bytes()).hexdigest(),
        ).event

    def write_result(self, request: SyntheticEventStateRunRequest, result: dict[str, Any], test_report: dict[str, Any]) -> Path:
        run_dir = request.output_root / request.run_id
        if run_dir.exists() and any(run_dir.iterdir()):
            raise EventStateContractError("FAIL_NONEMPTY_RUN_DIRECTORY", str(run_dir))
        run_dir.mkdir(parents=True, exist_ok=True)
        artifacts = {
            "resolved_input_manifest.json": {
                "fixture_class": "SYNTHETIC_TYPED_EVENT_STATE",
                "physical_rows": 0,
                "initial_handoff_sha256": PROVIDER_CONTRACT_HANDOFF_SHA256,
                "completion_handoff_sha256": PROVIDER_COMPLETION_HANDOFF_SHA256,
                "inputs": result["input_identities"],
            },
            "bounded_event_state_event.json": result["semantic"]["event"],
            "state_aware_event_sequence.json": result["semantic"]["event_sequence"],
            "event_state_store_trace.json": result["semantic"]["store_trace"],
            "bounded_probe_observations.json": result["semantic"]["observations"],
            "test_report.json": test_report,
            "availability_sidecar_validation_report.json": {
                "status": "PASS", "schema_sha256": result["semantic"]["event"]["audit_lineage"]["sidecar_schema_sha256"],
                "record_count": 1, "bijection": "PASS", "temporal_formula": "PASS",
            },
            "typed_payload_binding_report.json": {
                "status": "PASS", "field_count": 17,
                "binding_sha256": result["semantic"]["event"]["audit_lineage"]["typed_payload_binding_sha256"],
                "additional_properties": 0,
            },
            "fingerprint_and_dependency_report.json": {
                "status": "PASS",
                "synthetic_fingerprint_recomputed": True,
                "fingerprint_policy_id": result["semantic"]["event"]["audit_lineage"]["synthetic_fingerprint_policy_id"],
                "market_state_cross_dataset_binding": result["semantic"]["event"]["market_state_cross_dataset_binding"],
                "validated_market_state_dependency": result["semantic"]["market_state_dependency"],
            },
            "restriction_domain_report.json": {
                "status": "PASS", "provenance_domain_preserved": True,
                "replay_consumption_domain_closed": True,
                "component_restriction_domain": "NOT_MATERIALIZED_NOT_AUTHORIZED",
            },
            "boundary_preservation_report.json": {
                "status": "PASS", "physical_reads": 0, "strategy": False,
                "orders": 0, "fills": 0, "pnl": False,
                "StateReplayFeed": "NOT_AUTHORIZED",
            },
            "determinism_report.json": {
                "status": "PASS",
                "deterministic_output_hash": result["deterministic_output_hash"],
            },
        }
        hashes = {}
        for name, data in artifacts.items():
            path = run_dir / name
            self._write(path, data)
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        final = {
            "gate_id": "BT-GATE-015",
            "implementation_phase": "BOUNDED_NON_PHYSICAL_IMPLEMENTATION",
            "validation_status": "PASS",
            "physical_data_files_opened": 0,
            "physical_state_rows_read": 0,
            "event_state_events": 1,
            "store_inserts": result["store_inserts"],
            "observations": result["observations"],
            "orders": 0, "fills": 0, "pnl_calculated": False,
            "output_artifact_hashes": hashes,
            "deterministic_output_hash": result["deterministic_output_hash"],
            "implementation_acceptance": "PENDING_EXTERNAL_NON_PHYSICAL_REVIEW",
            "event_state_physical_read": "NOT_AUTHORIZED",
            "next_required_action": "EXTERNAL_NON_PHYSICAL_IMPLEMENTATION_REVIEW",
        }
        final["scientific_manifest_hash"] = canonical_hash(final)
        self._write(run_dir / "final_manifest.json", final)
        return run_dir

    @staticmethod
    def _json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write(path: Path, data: Any) -> None:
        path.write_text(
            json.dumps(to_event_state_jsonable(data), indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n",
            encoding="utf-8", newline="\n",
        )
