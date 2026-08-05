"""Contracts for the bounded non-physical Event State consumer."""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timezone
from types import MappingProxyType
from typing import Any, Literal, Mapping

from tsis_backtest.market_state.contracts import TypedCoreFourMarketStatePayload

BT_GATE_015 = "BT-GATE-015"
EXPECTED_REPLAY_RESTRICTIONS = (
    "candidate_runtime_only",
    "no_downstream",
    "no_production",
    "not_official_dataset",
    "research_only",
)


class EventStateContractError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def to_event_state_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {
            field.name: to_event_state_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise EventStateContractError(
                "FAIL_EVENT_STATE_TIMESTAMP_NOT_CANONICAL_UTC", "naive datetime"
            )
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {
            str(key): to_event_state_jsonable(item)
            for key, item in value.items()
        }
    if isinstance(value, (tuple, list)):
        return [to_event_state_jsonable(item) for item in value]
    return value


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): freeze(item) for key, item in value.items()})
    if isinstance(value, (tuple, list)):
        return tuple(freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class EventStateAuditLineage:
    source_snapshot_raw_json: str
    source_snapshot_sha256: str
    event_state_provenance_restriction_codes: tuple[str, ...]
    consumed_sidecar_sha256: str
    provider_contract_handoff_sha256: str
    provider_completion_handoff_sha256: str
    sidecar_schema_sha256: str
    typed_payload_binding_sha256: str
    event_state_schema_sha256: str
    synthetic_fingerprint_policy_id: str
    source_event_state_envelope: Mapping[str, Any]
    synthetic_fixture: bool
    physical_source_rows: int
    details: Mapping[str, Any]


@dataclass(frozen=True)
class BoundedEventStateAvailable:
    event_type: Literal["BoundedEventStateAvailable"]
    state_kind: Literal["event_state"]
    profile_id: str
    schema_id: str
    event_type_id: str
    event_instance_id: str
    event_window_binding_id: str
    instrument_projection_id: str
    market_state_record_id: str
    market_state_state_output_fingerprint: str
    market_state_cross_dataset_binding: str
    event_state_record_id: str
    event_state_record_fingerprint: str
    instrument_id: str
    ticker: str
    exchange_id: str
    session_date: date
    event_anchor_timestamp_utc: datetime
    event_state_as_of_utc: datetime
    event_state_available_at_utc: datetime
    event_state_publication_latency_policy_id: str
    event_state_publication_latency: str
    state_replay_consumption_legality: str
    replay_consumption_restriction_codes: tuple[str, ...]
    payload: TypedCoreFourMarketStatePayload
    audit_lineage: EventStateAuditLineage

    def to_dict(self) -> dict[str, Any]:
        return to_event_state_jsonable(self)


@dataclass(frozen=True)
class EventStateValidationReceipt:
    validator_id: Literal["BT_GATE_015_EVENT_STATE_VALIDATOR_V0_1"]
    schema_version: Literal["event_state_validation_receipt_v0_1"]
    event_content_sha256: str
    event_state_record_id: str
    event_state_record_fingerprint: str
    consumed_sidecar_sha256: str
    provider_contract_handoff_sha256: str
    provider_completion_handoff_sha256: str
    sidecar_schema_sha256: str
    typed_payload_binding_sha256: str
    event_state_schema_sha256: str
    validation_status: Literal["PASS"]


@dataclass(frozen=True)
class ValidatedBoundedEventStateAvailable:
    event: BoundedEventStateAvailable
    receipt: EventStateValidationReceipt


@dataclass(frozen=True)
class EventStateStoreTrace:
    sequence: int
    action: str
    event_state_record_id: str
    clock_utc: datetime
    status: str
