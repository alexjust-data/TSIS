"""Immutable point-in-time store dedicated to Event State."""
from __future__ import annotations

from datetime import datetime, timedelta

from .consumer import (
    EVENT_STATE_SCHEMA_SHA256, PROVIDER_COMPLETION_HANDOFF_SHA256,
    PROVIDER_CONTRACT_HANDOFF_SHA256, SCHEMA_ID, SIDECAR_SCHEMA_SHA256,
    TYPED_PAYLOAD_BINDING_SHA256, canonical_hash, is_issued_receipt,
)
from .contracts import (
    BoundedEventStateAvailable,
    EventStateContractError,
    EventStateStoreTrace,
    ValidatedBoundedEventStateAvailable,
)


class EventStateStore:
    def __init__(self) -> None:
        self._events: dict[str, BoundedEventStateAvailable] = {}
        self._stored_at: dict[str, datetime] = {}
        self._logical: set[tuple[str, str, str]] = set()
        self._trace: list[EventStateStoreTrace] = []

    @property
    def count(self) -> int:
        return len(self._events)

    @property
    def trace(self) -> tuple[EventStateStoreTrace, ...]:
        return tuple(self._trace)

    def insert(self, validated: ValidatedBoundedEventStateAvailable, clock_utc: datetime) -> int:
        if not isinstance(validated, ValidatedBoundedEventStateAvailable):
            raise EventStateContractError("FAIL_EVENT_STATE_STORE_VALIDATION_RECEIPT_REQUIRED", type(validated).__name__)
        if clock_utc.tzinfo is None or clock_utc.utcoffset() != timedelta(0):
            raise EventStateContractError("FAIL_EVENT_STATE_TIMESTAMP_NOT_CANONICAL_UTC", "store clock")
        event, receipt = validated.event, validated.receipt
        if (
            not is_issued_receipt(receipt, event)
            or receipt.validator_id != "BT_GATE_015_EVENT_STATE_VALIDATOR_V0_1"
            or receipt.schema_version != "event_state_validation_receipt_v0_1"
            or receipt.validation_status != "PASS"
            or receipt.event_content_sha256 != canonical_hash(event.to_dict())
            or receipt.event_state_record_id != event.event_state_record_id
            or receipt.event_state_record_fingerprint != event.event_state_record_fingerprint
            or receipt.consumed_sidecar_sha256 != event.audit_lineage.consumed_sidecar_sha256
            or receipt.provider_contract_handoff_sha256 != PROVIDER_CONTRACT_HANDOFF_SHA256
            or receipt.provider_completion_handoff_sha256 != PROVIDER_COMPLETION_HANDOFF_SHA256
            or receipt.sidecar_schema_sha256 != SIDECAR_SCHEMA_SHA256
            or receipt.typed_payload_binding_sha256 != TYPED_PAYLOAD_BINDING_SHA256
            or receipt.event_state_schema_sha256 != EVENT_STATE_SCHEMA_SHA256
        ):
            raise EventStateContractError("FAIL_EVENT_STATE_STORE_INVALID_VALIDATION_RECEIPT", "complete receipt authority")
        if event.event_type != "BoundedEventStateAvailable" or event.state_kind != "event_state" or event.schema_id != SCHEMA_ID:
            raise EventStateContractError("FAIL_EVENT_STATE_STORE_INVALID_EVENT", "event authority")
        if clock_utc < event.event_state_available_at_utc:
            raise EventStateContractError("FAIL_EVENT_STATE_EARLY_STORE_INSERT", "clock")
        if event.event_state_record_id in self._events:
            existing = self._events[event.event_state_record_id]
            code = (
                "FAIL_DUPLICATE_EVENT_STATE_EVENT"
                if canonical_hash(existing.to_dict()) == canonical_hash(event.to_dict())
                else "FAIL_CONFLICTING_EVENT_STATE_EVENT"
            )
            raise EventStateContractError(code, event.event_state_record_id)
        logical = (event.event_type_id, event.instrument_id, event.event_anchor_timestamp_utc.isoformat())
        if logical in self._logical:
            raise EventStateContractError("FAIL_CONFLICTING_EVENT_STATE_EVENT", str(logical))
        sequence = len(self._trace)
        self._events[event.event_state_record_id] = event
        self._stored_at[event.event_state_record_id] = clock_utc
        self._logical.add(logical)
        self._trace.append(EventStateStoreTrace(sequence, "INSERT", event.event_state_record_id, clock_utc, "PASS"))
        return sequence

    def get_exact(self, record_id: str, observed_at_utc: datetime) -> BoundedEventStateAvailable | None:
        event = self._events.get(record_id)
        if event is None:
            return None
        if self._stored_at[record_id] > observed_at_utc or event.event_state_available_at_utc > observed_at_utc:
            return None
        return event
