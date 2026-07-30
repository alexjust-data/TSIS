"""Contracts for the bounded point-in-time Market State consumer."""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping

BT_GATE_014 = "BT-GATE-014"
POINT_IN_TIME_MARKET_STATE_CONSUMER_V0_1 = "POINT_IN_TIME_MARKET_STATE_CONSUMER_V0_1"
STATE_AWARE_GLOBAL_EVENT_ORDER_V0_2 = "STATE_AWARE_GLOBAL_EVENT_ORDER_V0_2"
EXPECTED_RESTRICTIONS = ("candidate_runtime_only", "not_official_dataset", "no_downstream", "no_production")

class MarketStateContractError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def to_market_state_jsonable(value: Any) -> Any:
    """Serialize BT-GATE-014 values with the contract's canonical UTC spelling."""
    if is_dataclass(value):
        return {
            field.name: to_market_state_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC",
                "naive datetime",
            )
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {
            str(key): to_market_state_jsonable(item)
            for key, item in value.items()
        }
    if isinstance(value, (tuple, list)):
        return [to_market_state_jsonable(item) for item in value]
    return value


@dataclass(frozen=True)
class PriceLocationStructurePayload:
    daily_open_price: float
    daily_prior_close: float
    intraday_bar_close_price: float
    intraday_return_vs_prior_close_ratio_as_location: float
    intraday_return_vs_session_open_ratio_as_location: float

@dataclass(frozen=True)
class PriceMovementPayload:
    daily_gap_pct: float
    daily_prior_close: float
    intraday_bar_close_price: float
    intraday_return_vs_prior_close_ratio: float
    intraday_return_vs_session_open_ratio: float

@dataclass(frozen=True)
class TradingActivityPayload:
    session_volume_to_time_over_prior_20_full_session_volume_mean: float
    daily_volume_20d_avg: float
    intraday_bar_volume: float
    intraday_session_volume_to_time: float

@dataclass(frozen=True)
class VolatilityRangeStatePayload:
    intraday_high_so_far: float
    intraday_low_so_far: float
    intraday_range_so_far_ratio: float

@dataclass(frozen=True)
class TypedCoreFourMarketStatePayload:
    price_location_structure: PriceLocationStructurePayload
    price_movement: PriceMovementPayload
    trading_activity: TradingActivityPayload
    volatility_range_state: VolatilityRangeStatePayload

    def to_dict(self) -> dict[str, Any]:
        return to_market_state_jsonable(self)

@dataclass(frozen=True)
class MarketStateComponentAvailabilityEvidence:
    component_id: str
    information_object_id: str
    source_timestamp_utc: datetime
    component_as_of_utc: datetime
    component_available_at_utc: datetime
    availability_status: str
    component_replay_restriction_codes: tuple[str, ...]
    cutoff_rule_id: str
    availability_rule_id: str

    @property
    def restriction_codes(self) -> tuple[str, ...]:
        """Historical API alias; the serialized field remains domain-labelled."""
        return self.component_replay_restriction_codes

@dataclass(frozen=True)
class MarketStateAuditLineage:
    materialization_run_id: str
    source_integration_run_id: str
    source_candidate_record_id: str
    source_integration_profile_id: str
    decision_case: str
    context_id: str
    integration_status: str
    object_completeness_status: str
    quality_status: str
    calendar_version: str
    context_input_fingerprint: str
    source_lineage_raw_json: str
    source_lineage: Mapping[str, Any]
    policy_versions_raw_json: str
    policy_versions: Mapping[str, Any]
    formula_versions_raw_json: str
    formula_versions: Mapping[str, Any]
    physical_restriction_codes_raw_json: str
    physical_provenance_restriction_codes: tuple[str, ...]
    component_availability_evidence: tuple[MarketStateComponentAvailabilityEvidence, ...]

    @property
    def restriction_codes_raw_json(self) -> str:
        """Historical API alias for physical fingerprint reconstruction only."""
        return self.physical_restriction_codes_raw_json
    provider_handoff_sha256: str
    nested_provider_evidence_sha256: str
    structural_schema_sha256: str
    current_runtime_content_sha256: str
    state_bundle_ref_id: str
    state_bundle_canonical_sha256: str
    sidecar_id: str
    sidecar_schema_id: str
    consumed_sidecar_sha256: str
    provider_sidecar_authority_sha256: str
    binding_id: str
    binding_sha256: str

@dataclass(frozen=True)
class BoundedMarketStateAvailable:
    event_type: Literal["BoundedMarketStateAvailable"]
    state_kind: Literal["market_state"]
    profile_id: str
    state_schema_version: str
    physical_profile_id: str
    candidate_dataset_id: str
    candidate_dataset_fingerprint: str
    materialized_state_candidate_id: str
    state_output_fingerprint: str
    instrument_id: str
    ticker: str
    session_date: date
    decision_timestamp_utc: datetime
    state_as_of_utc: datetime
    state_available_at_utc: datetime
    state_availability_policy_id: str
    state_publication_latency_policy_id: str
    state_publication_latency: str
    state_replay_consumption_legality: str
    state_availability_status: str
    replay_consumption_restriction_codes: tuple[str, ...]
    component_replay_restriction_codes: tuple[tuple[str, tuple[str, ...]], ...]
    payload: TypedCoreFourMarketStatePayload

    @property
    def restriction_codes(self) -> tuple[str, ...]:
        """Historical API alias for bounded replay restrictions only."""
        return self.replay_consumption_restriction_codes
    audit_lineage: MarketStateAuditLineage

    def to_dict(self) -> dict[str, Any]:
        return to_market_state_jsonable(self)

@dataclass(frozen=True)
class MarketStateStoreTrace:
    sequence: int
    action: str
    materialized_state_candidate_id: str
    clock_utc: datetime
    status: str

@dataclass(frozen=True)
class BoundedConsumerProbeObservation:
    probe_observation_id: str
    event_sequence: int
    observed_at_utc: datetime
    materialized_state_candidate_id: str
    state_output_fingerprint: str
    typed_payload_field_count: int
    replay_consumption_restriction_codes: tuple[str, ...]
    store_insert_sequence: int

    @property
    def restriction_codes(self) -> tuple[str, ...]:
        return self.replay_consumption_restriction_codes
    visibility_status: str

    def to_dict(self) -> dict[str, Any]:
        return to_market_state_jsonable(self)


@dataclass(frozen=True)
class MarketStateValidationReceipt:
    validator_id: Literal["BT_GATE_014_MARKET_STATE_VALIDATOR_V0_1"]
    validation_schema_version: Literal["market_state_validation_receipt_v0_1"]
    event_content_sha256: str
    materialized_state_candidate_id: str
    state_output_fingerprint: str
    candidate_dataset_id: str
    candidate_dataset_fingerprint: str
    provider_handoff_sha256: str
    nested_provider_evidence_sha256: str
    structural_schema_sha256: str
    current_runtime_content_sha256: str
    consumed_sidecar_sha256: str
    binding_sha256: str
    validation_status: Literal["PASS"]

@dataclass(frozen=True)
class ValidatedBoundedMarketStateAvailable:
    event: BoundedMarketStateAvailable
    receipt: MarketStateValidationReceipt
