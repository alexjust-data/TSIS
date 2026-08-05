"""Exact physical Event State adapter for the bounded BT-GATE-015 V0.3 slice."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Mapping

from tsis_backtest.market_state.contracts import (
    BoundedMarketStateAvailable,
    MarketStateAuditLineage,
    MarketStateComponentAvailabilityEvidence,
)

from .consumer import (
    EVENT_STATE_SCHEMA_SHA256,
    EVENT_TYPE_ID,
    EXPECTED_REPLAY_RESTRICTIONS,
    LATENCY_POLICY_ID,
    PHYSICAL_EVENT_STATE_RECORD_FINGERPRINT,
    PHYSICAL_EVENT_STATE_RECORD_ID,
    PROFILE_ID,
    PROVIDER_COMPLETION_HANDOFF_SHA256,
    PROVIDER_CONTRACT_HANDOFF_SHA256,
    SCHEMA_ID,
    SIDECAR_RECORD_FIELDS,
    SIDECAR_SCHEMA_SHA256,
    TYPED_PAYLOAD_BINDING_SHA256,
    WINDOW_DEFINITION_ID,
    _ISSUED_RECEIPTS,
    _payload,
    _strict_json,
    canonical_hash,
    utc,
)
from .contracts import (
    BoundedEventStateAvailable,
    EventStateAuditLineage,
    EventStateContractError,
    EventStateValidationReceipt,
    ValidatedBoundedEventStateAvailable,
    freeze,
)

PHYSICAL_FINGERPRINT_POLICY_ID = (
    "EVENT_STATE_ON_DEMAND_CANONICAL_RECORD_SHA256_V0_1"
)
PHYSICAL_ROW_FIELDS = (
    "event_state_record_id",
    "event_state_record_fingerprint",
    "event_state_schema_version",
    "event_state_profile_id",
    "event_type_id",
    "event_family_id",
    "event_instance_id",
    "event_instance_version",
    "event_window_binding_id",
    "event_window_definition_id",
    "event_state_instrument_session_projection_id",
    "instrument_id",
    "ticker",
    "exchange_id",
    "session_date",
    "calendar_version",
    "calendar_row_fingerprint",
    "event_anchor_timestamp_utc",
    "decision_timestamp_utc",
    "window_start_utc",
    "window_end_utc",
    "relative_time_to_event",
    "state_role",
    "consumption_legality",
    "market_state_record_id",
    "state_output_fingerprint",
    "source_market_state_profile_id",
    "source_market_state_physical_profile_id",
    "source_market_state_schema_version",
    "source_market_state_value_snapshot_json",
    "source_lineage_json",
    "policy_versions_json",
    "restriction_codes_json",
    "object_completeness_status",
    "integration_status",
    "integration_policy_id",
    "integration_policy_version",
    "quality_status",
    "created_at_utc",
    "supersedes_event_state_record_id",
    "superseded_by_event_state_record_id",
    "source_market_state_candidate_dataset_fingerprint",
    "market_state_dependency_request_fingerprint",
    "market_state_dependency_execution_plan_fingerprint",
)


def physical_record_fingerprint(row: Mapping[str, Any]) -> str:
    """Reproduce the provider on-demand Event State fingerprint exactly."""
    payload = {
        key: value
        for key, value in row.items()
        if key not in {"event_state_record_fingerprint", "created_at_utc"}
    }
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _closed_codes(value: Any, expected: tuple[str, ...], label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise EventStateContractError(
            "FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH", label
        )
    codes = tuple(value)
    if len(codes) != len(set(codes)) or set(codes) != set(expected):
        raise EventStateContractError(
            "FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH", label
        )
    return tuple(sorted(codes))


class PhysicalEventStateConsumerV03:
    """Validate the exact provider row and atomically issue a store receipt."""

    def __init__(
        self,
        expected_record_id: str = PHYSICAL_EVENT_STATE_RECORD_ID,
        expected_record_fingerprint: str = PHYSICAL_EVENT_STATE_RECORD_FINGERPRINT,
    ) -> None:
        self.expected_record_id = expected_record_id
        self.expected_record_fingerprint = expected_record_fingerprint

    def build_market_state_dependency(
        self,
        document: Mapping[str, Any],
        event_sidecar: Mapping[str, Any],
        payload: Any,
        market_sidecar_sha256: str,
    ) -> BoundedMarketStateAvailable:
        records = document.get("records")
        if not isinstance(records, list):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
                "Market State sidecar records",
            )
        matches = [
            record
            for record in records
            if record.get("materialized_state_candidate_id")
            == event_sidecar["market_state_record_id"]
        ]
        if len(matches) != 1:
            raise EventStateContractError(
                "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
                "exactly one Market State sidecar record required",
            )
        record = matches[0]
        required = {
            "materialized_state_candidate_id": event_sidecar["market_state_record_id"],
            "state_output_fingerprint": event_sidecar[
                "market_state_state_output_fingerprint"
            ],
            "candidate_dataset_fingerprint": event_sidecar[
                "market_state_availability_evidence_dataset_fingerprint"
            ],
            "instrument_id": event_sidecar["instrument_id"],
            "ticker": event_sidecar["ticker"],
            "session_date": event_sidecar["session_date"],
        }
        if any(record.get(key) != value for key, value in required.items()):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
                "Market State sidecar identity",
            )
        components = record.get("component_availability_evidence")
        if not isinstance(components, list) or len(components) != 4:
            raise EventStateContractError(
                "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
                "four Market State components required",
            )
        component_objects = []
        component_codes = []
        seen_ids: set[str] = set()
        for component in components:
            component_id = component.get("component_id")
            if not isinstance(component_id, str) or not component_id or component_id in seen_ids:
                raise EventStateContractError(
                    "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
                    "component identity",
                )
            seen_ids.add(component_id)
            codes = _closed_codes(
                component.get("restriction_codes"),
                ("candidate_runtime_only", "no_downstream", "no_production", "not_official_dataset"),
                component_id,
            )
            component_codes.append((component_id, codes))
            component_objects.append(
                MarketStateComponentAvailabilityEvidence(
                    component_id=component_id,
                    information_object_id=component["information_object_id"],
                    source_timestamp_utc=utc(component["source_timestamp_utc"]),
                    component_as_of_utc=utc(component["component_as_of_utc"]),
                    component_available_at_utc=utc(component["component_available_at_utc"]),
                    availability_status=component["availability_status"],
                    component_replay_restriction_codes=codes,
                    cutoff_rule_id=component["cutoff_rule_id"],
                    availability_rule_id=component["availability_rule_id"],
                )
            )
        replay_codes = _closed_codes(
            record.get("restriction_codes"),
            ("candidate_runtime_only", "no_downstream", "no_production", "not_official_dataset"),
            "Market State replay restrictions",
        )
        lineage = MarketStateAuditLineage(
            materialization_run_id="EVENT_STATE_PROVIDER_SIDECAR_DEPENDENCY",
            source_integration_run_id="EVENT_STATE_PROVIDER_COMPLETION_V0_1",
            source_candidate_record_id=str(record.get("source_candidate_record_id") or ""),
            source_integration_profile_id=record["profile_id"],
            decision_case="BT_GATE_015_BOUNDED_DEPENDENCY",
            context_id=record["context_id"],
            integration_status="DEPENDENCY_RECONSTRUCTED_FROM_GOVERNED_SIDECAR",
            object_completeness_status="CORE_FOUR_COMPLETE",
            quality_status="PASS_WITH_RESTRICTIONS",
            calendar_version="PROVIDER_EVENT_STATE_HANDOFF",
            context_input_fingerprint=event_sidecar[
                "market_state_dependency_dataset_fingerprint"
            ],
            source_lineage_raw_json="{}",
            source_lineage=freeze({"physical_market_state_read": False}),
            policy_versions_raw_json="{}",
            policy_versions=freeze({}),
            formula_versions_raw_json="{}",
            formula_versions=freeze({}),
            physical_restriction_codes_raw_json="[]",
            physical_provenance_restriction_codes=(),
            component_availability_evidence=tuple(component_objects),
            provider_handoff_sha256=PROVIDER_CONTRACT_HANDOFF_SHA256,
            nested_provider_evidence_sha256=PROVIDER_COMPLETION_HANDOFF_SHA256,
            structural_schema_sha256=event_sidecar["evidence_refs"][
                "market_state_schema_sha256"
            ],
            current_runtime_content_sha256=record["candidate_dataset_fingerprint"],
            state_bundle_ref_id="NOT_READ_BT_GATE_015",
            state_bundle_canonical_sha256="0" * 64,
            sidecar_id=document.get("sidecar_id", "market_state_replay_sidecar"),
            sidecar_schema_id="market_state_replay_availability_sidecar_v0_1",
            consumed_sidecar_sha256=market_sidecar_sha256,
            provider_sidecar_authority_sha256=market_sidecar_sha256,
            binding_id="BT_GATE_015_EVENT_TO_MARKET_STATE_EXACT_DEPENDENCY",
            binding_sha256=event_sidecar[
                "market_state_dependency_dataset_fingerprint"
            ],
        )
        return BoundedMarketStateAvailable(
            event_type="BoundedMarketStateAvailable",
            state_kind="market_state",
            profile_id=record["profile_id"],
            state_schema_version="market_state_candidate_schema_v0_1",
            physical_profile_id=record["physical_profile_id"],
            candidate_dataset_id=record["candidate_dataset_id"],
            candidate_dataset_fingerprint=record["candidate_dataset_fingerprint"],
            materialized_state_candidate_id=record["materialized_state_candidate_id"],
            state_output_fingerprint=record["state_output_fingerprint"],
            instrument_id=record["instrument_id"],
            ticker=record["ticker"],
            session_date=datetime.fromisoformat(record["session_date"]).date(),
            decision_timestamp_utc=utc(record["decision_timestamp_utc"]),
            state_as_of_utc=utc(record["state_as_of_utc"]),
            state_available_at_utc=utc(record["state_available_at_utc"]),
            state_availability_policy_id=record["state_availability_policy_id"],
            state_publication_latency_policy_id=record[
                "state_publication_latency_policy_id"
            ],
            state_publication_latency=record["state_publication_latency"],
            state_replay_consumption_legality=record[
                "state_replay_consumption_legality"
            ],
            state_availability_status=record["state_availability_status"],
            replay_consumption_restriction_codes=replay_codes,
            component_replay_restriction_codes=tuple(component_codes),
            payload=payload,
            audit_lineage=lineage,
        )

    def validate_and_seal(
        self,
        row: Mapping[str, Any],
        sidecar: Mapping[str, Any],
        sidecar_sha256: str,
        market_state: BoundedMarketStateAvailable,
        candidate_sha256: str,
        raw_line_sha256: str,
    ) -> ValidatedBoundedEventStateAvailable:
        if set(row) != set(PHYSICAL_ROW_FIELDS) or set(sidecar) != set(
            SIDECAR_RECORD_FIELDS
        ):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_SCHEMA_MISMATCH", "closed 44-field physical row"
            )
        if (
            row["event_state_record_id"] != self.expected_record_id
            or row["event_state_record_fingerprint"]
            != self.expected_record_fingerprint
            or physical_record_fingerprint(row)
            != row["event_state_record_fingerprint"]
        ):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_FINGERPRINT_MISMATCH", "physical record"
            )
        frozen = {
            "event_state_profile_id": PROFILE_ID,
            "event_state_schema_version": SCHEMA_ID,
            "event_type_id": EVENT_TYPE_ID,
            "event_window_definition_id": WINDOW_DEFINITION_ID,
            "event_state_record_id": sidecar["event_state_record_id"],
            "event_state_record_fingerprint": sidecar[
                "event_state_record_fingerprint"
            ],
            "event_instance_id": sidecar["event_instance_id"],
            "event_window_binding_id": sidecar["event_window_binding_id"],
            "event_state_instrument_session_projection_id": sidecar[
                "instrument_projection_id"
            ],
            "market_state_record_id": sidecar["market_state_record_id"],
            "state_output_fingerprint": sidecar[
                "market_state_state_output_fingerprint"
            ],
            "source_market_state_candidate_dataset_fingerprint": sidecar[
                "market_state_availability_evidence_dataset_fingerprint"
            ],
            "instrument_id": sidecar["instrument_id"],
            "ticker": sidecar["ticker"],
            "exchange_id": sidecar["exchange_id"],
            "session_date": sidecar["session_date"],
            "event_anchor_timestamp_utc": sidecar["event_anchor_timestamp_utc"],
            "consumption_legality": sidecar[
                "state_replay_consumption_legality"
            ],
        }
        if any(row.get(key) != value for key, value in frozen.items()):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_IDENTITY_MISMATCH", "physical-sidecar identity"
            )
        for key in (
            "market_state_dependency_request_fingerprint",
            "market_state_dependency_execution_plan_fingerprint",
        ):
            value = row.get(key)
            if not isinstance(value, str) or len(value) != 64:
                raise EventStateContractError(
                    "FAIL_EVENT_STATE_IDENTITY_MISMATCH", key
                )
        provenance = _strict_json(row["restriction_codes_json"], "restriction_codes_json")
        provenance_codes = _closed_codes(
            provenance,
            tuple(sidecar["event_state_provenance_restriction_codes"]),
            "Event State provenance restrictions",
        )
        replay_codes = _closed_codes(
            sidecar["replay_consumption_restriction_codes"],
            EXPECTED_REPLAY_RESTRICTIONS,
            "Event State replay restrictions",
        )
        payload, snapshot_hash = _payload(
            row["source_market_state_value_snapshot_json"]
        )
        if (
            market_state.materialized_state_candidate_id
            != sidecar["market_state_record_id"]
            or market_state.state_output_fingerprint
            != sidecar["market_state_state_output_fingerprint"]
            or canonical_hash(market_state.payload.to_dict())
            != canonical_hash(payload.to_dict())
        ):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH",
                "identity, fingerprint or payload",
            )
        as_of = [
            utc(sidecar[key])
            for key in (
                "event_instance_as_of_utc",
                "event_window_binding_as_of_utc",
                "instrument_projection_as_of_utc",
                "market_state_as_of_utc",
            )
        ]
        available = [
            utc(sidecar[key])
            for key in (
                "event_instance_available_at_utc",
                "event_window_binding_available_at_utc",
                "instrument_projection_available_at_utc",
                "market_state_available_at_utc",
            )
        ]
        event_as_of = utc(sidecar["event_state_as_of_utc"])
        event_available = utc(sidecar["event_state_available_at_utc"])
        if (
            sidecar["event_state_publication_latency"] != "PT0S"
            or event_as_of != max(as_of)
            or event_available != max(available)
            or utc(sidecar["event_anchor_timestamp_utc"]) > event_as_of
            or event_as_of > event_available
        ):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION", "derivation"
            )
        lineage = EventStateAuditLineage(
            source_snapshot_raw_json=row["source_market_state_value_snapshot_json"],
            source_snapshot_sha256=snapshot_hash,
            event_state_provenance_restriction_codes=provenance_codes,
            consumed_sidecar_sha256=sidecar_sha256,
            provider_contract_handoff_sha256=PROVIDER_CONTRACT_HANDOFF_SHA256,
            provider_completion_handoff_sha256=PROVIDER_COMPLETION_HANDOFF_SHA256,
            sidecar_schema_sha256=SIDECAR_SCHEMA_SHA256,
            typed_payload_binding_sha256=TYPED_PAYLOAD_BINDING_SHA256,
            event_state_schema_sha256=EVENT_STATE_SCHEMA_SHA256,
            synthetic_fingerprint_policy_id=PHYSICAL_FINGERPRINT_POLICY_ID,
            source_event_state_envelope=freeze(dict(row)),
            synthetic_fixture=False,
            physical_source_rows=1,
            details=freeze(
                {
                    "candidate_jsonl_sha256": candidate_sha256,
                    "raw_jsonl_line_sha256": raw_line_sha256,
                    "state_output_fingerprint_semantics": "MARKET_STATE_DEPENDENCY_FINGERPRINT",
                    "event_state_record_fingerprint_field": "event_state_record_fingerprint",
                    "physical_market_state_read": False,
                    "evidence_refs": dict(sidecar["evidence_refs"]),
                }
            ),
        )
        event = BoundedEventStateAvailable(
            event_type="BoundedEventStateAvailable",
            state_kind="event_state",
            profile_id=PROFILE_ID,
            schema_id=SCHEMA_ID,
            event_type_id=EVENT_TYPE_ID,
            event_instance_id=sidecar["event_instance_id"],
            event_window_binding_id=sidecar["event_window_binding_id"],
            instrument_projection_id=sidecar["instrument_projection_id"],
            market_state_record_id=sidecar["market_state_record_id"],
            market_state_state_output_fingerprint=sidecar[
                "market_state_state_output_fingerprint"
            ],
            market_state_cross_dataset_binding=sidecar[
                "market_state_cross_dataset_binding"
            ],
            event_state_record_id=sidecar["event_state_record_id"],
            event_state_record_fingerprint=sidecar[
                "event_state_record_fingerprint"
            ],
            instrument_id=sidecar["instrument_id"],
            ticker=sidecar["ticker"],
            exchange_id=sidecar["exchange_id"],
            session_date=datetime.fromisoformat(sidecar["session_date"]).date(),
            event_anchor_timestamp_utc=utc(sidecar["event_anchor_timestamp_utc"]),
            event_state_as_of_utc=event_as_of,
            event_state_available_at_utc=event_available,
            event_state_publication_latency_policy_id=LATENCY_POLICY_ID,
            event_state_publication_latency="PT0S",
            state_replay_consumption_legality="research_only",
            replay_consumption_restriction_codes=replay_codes,
            payload=payload,
            audit_lineage=lineage,
        )
        receipt = EventStateValidationReceipt(
            validator_id="BT_GATE_015_EVENT_STATE_VALIDATOR_V0_1",
            schema_version="event_state_validation_receipt_v0_1",
            event_content_sha256=canonical_hash(event.to_dict()),
            event_state_record_id=event.event_state_record_id,
            event_state_record_fingerprint=event.event_state_record_fingerprint,
            consumed_sidecar_sha256=sidecar_sha256,
            provider_contract_handoff_sha256=PROVIDER_CONTRACT_HANDOFF_SHA256,
            provider_completion_handoff_sha256=PROVIDER_COMPLETION_HANDOFF_SHA256,
            sidecar_schema_sha256=SIDECAR_SCHEMA_SHA256,
            typed_payload_binding_sha256=TYPED_PAYLOAD_BINDING_SHA256,
            event_state_schema_sha256=EVENT_STATE_SCHEMA_SHA256,
            validation_status="PASS",
        )
        _ISSUED_RECEIPTS[id(receipt)] = (
            receipt.event_content_sha256,
            receipt.event_state_record_id,
        )
        return ValidatedBoundedEventStateAvailable(event=event, receipt=receipt)
