"""Immutable point-in-time store for bounded Market State events."""
from __future__ import annotations
from datetime import datetime, timedelta
import math
from .contracts import BoundedMarketStateAvailable, EXPECTED_RESTRICTIONS, MarketStateContractError, MarketStateStoreTrace, TypedCoreFourMarketStatePayload, ValidatedBoundedMarketStateAvailable
from .consumer import (
    AVAILABILITY_POLICY_ID,
    FROZEN_PROVIDER_AUTHORITY,
    LATENCY_POLICY_ID,
    PHYSICAL_PROFILE_ID,
    PROFILE_ID,
    SHA256_PATTERN,
    STATE_SCHEMA_VERSION,
    canonical_hash,
    event_physical_identity,
    validate_frozen_lineage,
)

class MarketStateStore:
    def __init__(self) -> None:
        self._by_id: dict[str, BoundedMarketStateAvailable] = {}
        self._by_logical: dict[tuple[str,str,datetime], str] = {}
        self._insert_sequence: dict[str,int] = {}
        self._stored_at: dict[str,datetime] = {}
        self._trace: list[MarketStateStoreTrace] = []

    @property
    def trace(self) -> tuple[MarketStateStoreTrace,...]: return tuple(self._trace)
    @property
    def count(self) -> int: return len(self._by_id)

    def insert(self, validated: ValidatedBoundedMarketStateAvailable, clock_utc: datetime) -> int:
        if not isinstance(validated, ValidatedBoundedMarketStateAvailable):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_VALIDATION_RECEIPT_REQUIRED", type(validated).__name__)
        self._require_aware_utc(clock_utc,"clock_utc")
        event=validated.event; receipt=validated.receipt
        if receipt.validator_id!="BT_GATE_014_MARKET_STATE_VALIDATOR_V0_1" or receipt.validation_schema_version!="market_state_validation_receipt_v0_1" or receipt.validation_status!="PASS":
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_INVALID_VALIDATION_RECEIPT", "receipt identity")
        if (
            receipt.event_content_sha256!=canonical_hash(event.to_dict())
            or receipt.materialized_state_candidate_id!=event.materialized_state_candidate_id
            or receipt.state_output_fingerprint!=event.state_output_fingerprint
            or receipt.candidate_dataset_id!=event.candidate_dataset_id
            or receipt.candidate_dataset_fingerprint!=event.candidate_dataset_fingerprint
            or receipt.consumed_sidecar_sha256!=event.audit_lineage.consumed_sidecar_sha256
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_INVALID_VALIDATION_RECEIPT", "event binding")
        if (
            receipt.provider_handoff_sha256!=FROZEN_PROVIDER_AUTHORITY["provider_handoff_sha256"]
            or receipt.nested_provider_evidence_sha256!=FROZEN_PROVIDER_AUTHORITY["nested_provider_evidence_sha256"]
            or receipt.structural_schema_sha256!=FROZEN_PROVIDER_AUTHORITY["structural_schema_sha256"]
            or receipt.current_runtime_content_sha256!=FROZEN_PROVIDER_AUTHORITY["current_runtime_content_sha256"]
            or receipt.binding_sha256!=FROZEN_PROVIDER_AUTHORITY["binding_sha256"]
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_INVALID_VALIDATION_RECEIPT", "authority binding")
        self._validate_for_insert(event)
        if clock_utc < event.state_available_at_utc:
            raise MarketStateContractError("FAIL_MARKET_STATE_EARLY_STORE_INSERT", "clock precedes state availability")
        if event.materialized_state_candidate_id in self._by_id:
            raise MarketStateContractError("FAIL_DUPLICATE_MARKET_STATE_EVENT", event.materialized_state_candidate_id)
        logical=(event.profile_id,event.instrument_id,event.decision_timestamp_utc)
        if logical in self._by_logical:
            raise MarketStateContractError("FAIL_CONFLICTING_MARKET_STATE_EVENT", str(logical))
        seq=len(self._trace)
        self._by_id[event.materialized_state_candidate_id]=event
        self._by_logical[logical]=event.materialized_state_candidate_id
        self._insert_sequence[event.materialized_state_candidate_id]=seq
        self._stored_at[event.materialized_state_candidate_id]=clock_utc
        self._trace.append(MarketStateStoreTrace(seq,"INSERT",event.materialized_state_candidate_id,clock_utc,"PASS"))
        return seq

    @staticmethod
    def _validate_for_insert(event: BoundedMarketStateAvailable) -> None:
        if event.event_type!="BoundedMarketStateAvailable" or event.state_kind!="market_state" or event.profile_id!=PROFILE_ID or event.physical_profile_id!=PHYSICAL_PROFILE_ID or event.state_schema_version!=STATE_SCHEMA_VERSION:
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "event identity")
        for field,value in (
            ("candidate_dataset_id",event.candidate_dataset_id),
            ("instrument_id",event.instrument_id),
            ("ticker",event.ticker),
            ("materialized_state_candidate_id",event.materialized_state_candidate_id),
            ("state_output_fingerprint",event.state_output_fingerprint),
            ("context_id",event.audit_lineage.context_id),
            ("source_candidate_record_id",event.audit_lineage.source_candidate_record_id),
        ):
            if not isinstance(value,str) or not value.strip():
                raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",field)
        for field,value in (
            ("candidate_dataset_fingerprint",event.candidate_dataset_fingerprint),
            ("materialized_state_candidate_id",event.materialized_state_candidate_id),
            ("state_output_fingerprint",event.state_output_fingerprint),
            ("consumed_sidecar_sha256",event.audit_lineage.consumed_sidecar_sha256),
        ):
            if not isinstance(value,str) or not SHA256_PATTERN.fullmatch(value):
                raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",field)
        if event.state_publication_latency_policy_id!=LATENCY_POLICY_ID or event.state_publication_latency!="PT0S" or event.state_availability_policy_id!=AVAILABILITY_POLICY_ID:
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "availability policy")
        lineage=event.audit_lineage
        if (
            lineage.provider_handoff_sha256!=FROZEN_PROVIDER_AUTHORITY["provider_handoff_sha256"]
            or lineage.nested_provider_evidence_sha256!=FROZEN_PROVIDER_AUTHORITY["nested_provider_evidence_sha256"]
            or lineage.structural_schema_sha256!=FROZEN_PROVIDER_AUTHORITY["structural_schema_sha256"]
            or lineage.current_runtime_content_sha256!=FROZEN_PROVIDER_AUTHORITY["current_runtime_content_sha256"]
            or lineage.state_bundle_ref_id!=FROZEN_PROVIDER_AUTHORITY["state_bundle_ref_id"]
            or lineage.state_bundle_canonical_sha256!=FROZEN_PROVIDER_AUTHORITY["state_bundle_canonical_sha256"]
            or lineage.provider_sidecar_authority_sha256!=FROZEN_PROVIDER_AUTHORITY["sidecar_sha256"]
            or lineage.binding_id!=FROZEN_PROVIDER_AUTHORITY["binding_id"]
            or lineage.binding_sha256!=FROZEN_PROVIDER_AUTHORITY["binding_sha256"]
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "lineage authority")
        validate_frozen_lineage(event)
        if event.state_replay_consumption_legality != "decision_safe" or event.state_availability_status != "available_for_decision_replay":
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "legality")
        if event.replay_consumption_restriction_codes != EXPECTED_RESTRICTIONS:
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "restrictions")
        if not isinstance(event.payload, TypedCoreFourMarketStatePayload):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "payload type")
        payload_values=[]
        for component in (event.payload.price_location_structure,event.payload.price_movement,event.payload.trading_activity,event.payload.volatility_range_state):
            payload_values.extend(vars(component).values())
        if len(payload_values)!=17 or any(not isinstance(value,float) or not math.isfinite(value) for value in payload_values):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "payload values")
        components=event.audit_lineage.component_availability_evidence
        expected_components={"price_location_structure","price_movement","trading_activity","volatility_range_state"}
        if (
            len(components)!=4
            or {item.information_object_id for item in components}!=expected_components
            or len({item.component_id for item in components})!=4
            or any(
                not item.component_id.strip()
                or not item.cutoff_rule_id.strip()
                or not item.availability_rule_id.strip()
                for item in components
            )
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "components")
        if event.state_as_of_utc!=max(item.component_as_of_utc for item in components) or event.state_available_at_utc!=max([event.decision_timestamp_utc]+[item.component_available_at_utc for item in components]):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT", "temporal derivation")
        component_union: set[str] = set()
        for item in components:
            component_codes = item.component_replay_restriction_codes
            if (
                item.component_as_of_utc > event.decision_timestamp_utc
                or item.component_available_at_utc > event.state_available_at_utc
                or not component_codes
                or len(component_codes) != len(set(component_codes))
                or not set(component_codes).issubset(
                    set(event.replay_consumption_restriction_codes)
                )
                or item.availability_status != "available"
            ):
                raise MarketStateContractError(
                    "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
                    "component legality",
                )
            component_union.update(component_codes)
        if not component_union.issubset(
            set(event.replay_consumption_restriction_codes)
        ):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
                "component replay restriction union",
            )
        projected = tuple(
            (
                item.information_object_id,
                item.component_replay_restriction_codes,
            )
            for item in components
        )
        if event.component_replay_restriction_codes != projected:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
                "component restriction projection",
            )
        state_fingerprint,candidate_id=event_physical_identity(event)
        if (
            state_fingerprint!=event.state_output_fingerprint
            or candidate_id!=event.materialized_state_candidate_id
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT","physical identity")

    @staticmethod
    def _require_aware_utc(value: datetime,field: str) -> None:
        if (
            not isinstance(value,datetime)
            or value.tzinfo is None
            or value.utcoffset() is None
            or value.utcoffset()!=timedelta(0)
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC",field)

    def get_exact(self, candidate_id: str, observed_at_utc: datetime) -> BoundedMarketStateAvailable | None:
        event=self._by_id.get(candidate_id)
        if event is None or event.state_available_at_utc > observed_at_utc or self._stored_at[candidate_id] > observed_at_utc: return None
        return event

    def insert_sequence(self, candidate_id: str) -> int: return self._insert_sequence[candidate_id]

    def latest_visible(self, profile_id: str, instrument_id: str, decision_timestamp_utc: datetime, observed_at_utc: datetime) -> BoundedMarketStateAvailable | None:
        values=[e for e in self._by_id.values() if e.profile_id==profile_id and e.instrument_id==instrument_id and e.decision_timestamp_utc<=decision_timestamp_utc and e.state_as_of_utc<=decision_timestamp_utc and e.state_available_at_utc<=observed_at_utc and self._stored_at[e.materialized_state_candidate_id]<=observed_at_utc]
        return max(values,key=lambda e:(e.decision_timestamp_utc,e.state_available_at_utc,e.materialized_state_candidate_id),default=None)
