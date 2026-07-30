"""Validation and adaptation for synthetic BT-GATE-014 Market State rows."""
from __future__ import annotations

import hashlib, json, math, re
from datetime import date, datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayGapEvent
from .contracts import (
    BoundedMarketStateAvailable, EXPECTED_RESTRICTIONS, MarketStateAuditLineage,
    MarketStateComponentAvailabilityEvidence, MarketStateContractError,
    PriceLocationStructurePayload, PriceMovementPayload, TradingActivityPayload,
    TypedCoreFourMarketStatePayload, VolatilityRangeStatePayload,
    MarketStateValidationReceipt, ValidatedBoundedMarketStateAvailable,
    to_market_state_jsonable,
)

PROFILE_ID="market_state_core_four_intraday_profile_v0_1"
PHYSICAL_PROFILE_ID="core_four_market_state_profile_v0_1"
STATE_SCHEMA_VERSION="core_four_market_state_candidate_physical_schema_v0_1"
AVAILABILITY_POLICY_ID="market_state_core_four_replay_availability_policy_v0_1"
LATENCY_POLICY_ID="zero_latency_candidate_replay_publication_policy_v0_1"
SIDECAR_SCHEMA_ID="market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1"
UTC_PATTERN=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")
SHA256_PATTERN=re.compile(r"^[0-9a-f]{64}$")
ENVELOPE_COLUMNS=("materialized_state_candidate_id","state_profile_id","state_schema_version","instrument_id","ticker","session_date","decision_timestamp_utc","restriction_codes_json","state_output_fingerprint")
PAYLOAD_COLUMNS=(
"price_location_structure__daily_open_price","price_location_structure__daily_prior_close","price_location_structure__intraday_bar_close_price","price_location_structure__intraday_return_vs_prior_close_ratio_as_location","price_location_structure__intraday_return_vs_session_open_ratio_as_location",
"price_movement__daily_gap_pct","price_movement__daily_prior_close","price_movement__intraday_bar_close_price","price_movement__intraday_return_vs_prior_close_ratio","price_movement__intraday_return_vs_session_open_ratio",
"trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean","trading_activity__daily_volume_20d_avg","trading_activity__intraday_bar_volume","trading_activity__intraday_session_volume_to_time",
"volatility_range_state__intraday_high_so_far","volatility_range_state__intraday_low_so_far","volatility_range_state__intraday_range_so_far_ratio")
LINEAGE_COLUMNS=("materialization_run_id","source_integration_run_id","source_candidate_record_id","source_integration_profile_id","decision_case","context_id","integration_status","object_completeness_status","quality_status","calendar_version","source_lineage_json","policy_versions_json","formula_versions_json","context_input_fingerprint")
def _canonical_restrictions(value: Any, source: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise MarketStateContractError("FAIL_MARKET_STATE_RESTRICTION_PROPAGATION", f"{source}: expected sequence")
    observed = tuple(value)
    if (
        any(not isinstance(item, str) or not item for item in observed)
        or len(observed) != len(EXPECTED_RESTRICTIONS)
        or len(set(observed)) != len(observed)
        or set(observed) != set(EXPECTED_RESTRICTIONS)
    ):
        raise MarketStateContractError(
            "FAIL_MARKET_STATE_RESTRICTION_PROPAGATION",
            json.dumps(
                {
                    "expected_restrictions": list(EXPECTED_RESTRICTIONS),
                    "observed_restrictions": list(observed),
                    "source": source,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    return EXPECTED_RESTRICTIONS


def _physical_provenance_restrictions(value: Any) -> tuple[str, ...]:
    """Validate physical restrictions without reinterpreting them as replay policy."""
    observed = tuple(value) if isinstance(value, (list, tuple)) else ()
    if (
        not observed
        or any(not isinstance(item, str) or not item for item in observed)
        or len(set(observed)) != len(observed)
    ):
        raise MarketStateContractError(
            "FAIL_MARKET_STATE_PHYSICAL_PROVENANCE_RESTRICTIONS_INVALID",
            "restriction_codes_json",
        )
    return observed


def _component_replay_restrictions(
    value: Any,
    source: str,
    row_replay_restrictions: tuple[str, ...],
) -> tuple[str, ...]:
    observed = tuple(value) if isinstance(value, (list, tuple)) else ()
    if (
        not observed
        or any(not isinstance(item, str) or not item for item in observed)
        or len(set(observed)) != len(observed)
        or not set(observed).issubset(set(row_replay_restrictions))
    ):
        raise MarketStateContractError(
            "FAIL_MARKET_STATE_RESTRICTION_PROPAGATION",
            json.dumps(
                {
                    "row_replay_consumption_restrictions": list(row_replay_restrictions),
                    "component_replay_restrictions": list(observed),
                    "source": source,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    return tuple(code for code in EXPECTED_RESTRICTIONS if code in observed)


PHYSICAL_COLUMNS=("materialized_state_candidate_id","state_profile_id","state_schema_version","materialization_run_id","source_integration_run_id","source_candidate_record_id","source_integration_profile_id","instrument_id","ticker","session_date","decision_timestamp_utc","decision_case","context_id","integration_status","object_completeness_status","quality_status",*PAYLOAD_COLUMNS,"calendar_version","source_lineage_json","policy_versions_json","formula_versions_json","restriction_codes_json","context_input_fingerprint","state_output_fingerprint")
FINGERPRINT_FIELDS=("state_profile_id","state_schema_version","source_integration_profile_id","instrument_id","ticker","session_date","decision_timestamp_utc","decision_case","context_id","integration_status","object_completeness_status","quality_status",*PAYLOAD_COLUMNS,"calendar_version","source_lineage_json","policy_versions_json","formula_versions_json","restriction_codes_json","context_input_fingerprint")
ID_FIELDS=("state_profile_id","state_schema_version","instrument_id","decision_timestamp_utc","context_input_fingerprint","state_output_fingerprint")
FROZEN_PROVIDER_AUTHORITY = {
    "provider_handoff_sha256": "2c578ce9216bb3fd9010ef1f4afe8ba4022ab6b15f665d276a957f50acb35112",
    "nested_provider_evidence_sha256": "8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7",
    "structural_schema_sha256": "595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b",
    "current_runtime_content_sha256": "bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68",
    "binding_id": "market_state_core_four_scale_validation_physical_schema_binding_v0_1",
    "binding_sha256": "4006e80f099bb8abec147e33670294d7cc2eb565d25a10a08d6bf929c247f083",
    "state_bundle_ref_id": "state_bundle_manifest_scale_validation_reissue_v0_1_2_20260729",
    "state_bundle_canonical_sha256": "0e9f7387acdf999a6e41f163ab16c3412c32cb545d1757cde4b5613572406be2",
    "sidecar_sha256": "8e426b09bb1cafac26e49c7a81de31ef4ea60ca3b56ac3aa766ba13a0772c5ac",
}
AUTHORITY_FIELDS=frozenset((*FROZEN_PROVIDER_AUTHORITY,"candidate_dataset_id","candidate_dataset_fingerprint"))
SIDECAR_FIELDS=frozenset((
    "physical_profile_id","candidate_dataset_id","candidate_dataset_fingerprint",
    "state_as_of_utc","state_available_at_utc","state_availability_policy_id",
    "state_publication_latency_policy_id","state_publication_latency",
    "state_availability_status","component_availability_evidence",
    "state_replay_consumption_legality","restriction_codes",
    "materialized_state_candidate_id","state_output_fingerprint","profile_id",
    "source_candidate_record_id","instrument_id","ticker","session_date",
    "context_id","decision_timestamp_utc","sidecar_id","sidecar_schema_id",
))
COMPONENT_FIELDS=frozenset((
    "component_id","information_object_id","source_timestamp_utc",
    "component_as_of_utc","component_available_at_utc","availability_status",
    "restriction_codes","cutoff_rule_id","availability_rule_id",
))
ROW_DOCUMENT_FIELDS=frozenset((
    "fixture_class","not_provider_evidence","not_scientific_observation",
    "physical_source_rows","provider_parquet_opened","records","synthetic",
))
SIDECAR_DOCUMENT_FIELDS=frozenset((
    "fixture_class","not_provider_evidence","not_scientific_observation",
    "physical_source_rows","provider_parquet_opened","records","synthetic",
))
MARKET_BAR_DOCUMENT_FIELDS=frozenset((
    "fixture_class","not_provider_evidence","not_scientific_observation",
    "physical_source_rows","provider_parquet_opened","records","synthetic",
))
FIXTURE_MANIFEST_FIELDS=frozenset((
    "files","fixture_class","fixture_id","market_bar_record_count",
    "not_provider_evidence","not_scientific_observation",
    "physical_source_rows","provider_parquet_opened","record_count","synthetic",
))
NONEMPTY_ROW_FIELDS=tuple(
    field for field in PHYSICAL_COLUMNS if field not in PAYLOAD_COLUMNS
)
EXPECTED_TYPES={name:("double" if name in PAYLOAD_COLUMNS else "date32[day]" if name=="session_date" else "timestamp[us, tz=UTC]" if name=="decision_timestamp_utc" else "string") for name in PHYSICAL_COLUMNS}


def _normalize(value: Any) -> Any:
    return to_market_state_jsonable(value)

def canonical_bytes(value: Any) -> bytes:
    try:
        normalized=to_market_state_jsonable(value)
        return json.dumps(normalized,sort_keys=True,ensure_ascii=True,separators=(",",":"),allow_nan=False).encode("utf-8")
    except (TypeError,ValueError) as exc:
        raise MarketStateContractError("FAIL_MARKET_STATE_NON_FINITE_VALUE","canonical JSON") from exc
def canonical_hash(value: Any) -> str: return hashlib.sha256(canonical_bytes(value)).hexdigest()
def format_utc_z(value: datetime) -> str:
    normalized=to_market_state_jsonable(value)
    if not isinstance(normalized,str) or not UTC_PATTERN.fullmatch(normalized):
        raise MarketStateContractError("FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC",str(value))
    return normalized
def _utc(value: str) -> datetime:
    if not isinstance(value,str) or not UTC_PATTERN.fullmatch(value): raise MarketStateContractError("FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC",str(value))
    return datetime.fromisoformat(value[:-1]+"+00:00")
def _strict_json_loads(raw: str, field: str) -> Any:
    def reject_constant(token: str) -> None:
        raise ValueError(f"non-finite constant {token}")
    def reject_duplicate_keys(pairs: list[tuple[str,Any]]) -> dict[str,Any]:
        result: dict[str,Any]={}
        for key,value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key}")
            result[key]=value
        return result
    if not isinstance(raw,str):
        raise MarketStateContractError("FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON",field)
    try:
        return json.loads(raw,parse_constant=reject_constant,object_pairs_hook=reject_duplicate_keys)
    except Exception as exc:
        raise MarketStateContractError("FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON",field) from exc
def strict_json_document(raw: str, field: str) -> Any:
    return _strict_json_loads(raw,field)
def _deep_freeze(value: Any) -> Any:
    if isinstance(value,Mapping):
        return MappingProxyType({str(key):_deep_freeze(item) for key,item in value.items()})
    if isinstance(value,(list,tuple)):
        return tuple(_deep_freeze(item) for item in value)
    if isinstance(value,float) and not math.isfinite(value):
        raise MarketStateContractError("FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON","non-finite nested value")
    return value
def is_deeply_immutable(value: Any) -> bool:
    if isinstance(value,MappingProxyType):
        return all(isinstance(key,str) and is_deeply_immutable(item) for key,item in value.items())
    if isinstance(value,tuple):
        return all(is_deeply_immutable(item) for item in value)
    return not isinstance(value,(dict,list,set,bytearray))
def _json_mapping(raw: str, field: str) -> Mapping[str,Any]:
    value=_strict_json_loads(raw,field)
    if not isinstance(value,dict): raise MarketStateContractError("FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON",field)
    return _deep_freeze(value)
def _json_sequence(raw: str, field: str) -> tuple[str,...]:
    value=_strict_json_loads(raw,field)
    if not isinstance(value,list) or not all(isinstance(x,str) for x in value): raise MarketStateContractError("FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON",field)
    return tuple(value)
def _require_nonempty_string(value: Any, field: str, code: str="FAIL_MARKET_STATE_IDENTITY_INVALID") -> str:
    if not isinstance(value,str) or not value.strip():
        raise MarketStateContractError(code,field)
    return value
def _require_sha256(value: Any, field: str, code: str="FAIL_MARKET_STATE_IDENTITY_INVALID") -> str:
    if not isinstance(value,str) or not SHA256_PATTERN.fullmatch(value):
        raise MarketStateContractError(code,field)
    return value


def _event_session_date_utc(value: datetime) -> str:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
        or value.utcoffset() != timezone.utc.utcoffset(value)
    ):
        raise MarketStateContractError(
            "FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC",
            "event session-date source",
        )
    return value.date().isoformat()


def state_aware_order_key(event: Any) -> tuple[Any,...]:
    if isinstance(event,ReplayGapEvent):
        return (
            event.available_at,
            0,
            _event_session_date_utc(event.ts_start),
            event.ticker.upper(),
            f"{event.ticker}:{format_utc_z(event.ts_start)}:GAP",
        )
    if isinstance(event,ReplayBarEvent):
        return (
            event.available_at,
            1,
            _event_session_date_utc(event.bar.ts_start),
            event.ticker.upper(),
            f"{event.ticker}:{format_utc_z(event.bar.ts_start)}:BAR",
        )
    if isinstance(event,BoundedMarketStateAvailable):
        return (
            event.state_available_at_utc,
            2,
            event.session_date.isoformat(),
            event.ticker.upper(),
            event.materialized_state_candidate_id,
        )
    raise MarketStateContractError("FAIL_EVENT_STATE_NOT_AUTHORIZED",type(event).__name__)


def event_physical_identity(
    event: BoundedMarketStateAvailable,
) -> tuple[str,str]:
    payload=event.payload
    lineage=event.audit_lineage
    values={
        "state_profile_id":event.profile_id,
        "state_schema_version":event.state_schema_version,
        "source_integration_profile_id":lineage.source_integration_profile_id,
        "instrument_id":event.instrument_id,
        "ticker":event.ticker,
        "session_date":event.session_date,
        "decision_timestamp_utc":event.decision_timestamp_utc,
        "decision_case":lineage.decision_case,
        "context_id":lineage.context_id,
        "integration_status":lineage.integration_status,
        "object_completeness_status":lineage.object_completeness_status,
        "quality_status":lineage.quality_status,
        "price_location_structure__daily_open_price":payload.price_location_structure.daily_open_price,
        "price_location_structure__daily_prior_close":payload.price_location_structure.daily_prior_close,
        "price_location_structure__intraday_bar_close_price":payload.price_location_structure.intraday_bar_close_price,
        "price_location_structure__intraday_return_vs_prior_close_ratio_as_location":payload.price_location_structure.intraday_return_vs_prior_close_ratio_as_location,
        "price_location_structure__intraday_return_vs_session_open_ratio_as_location":payload.price_location_structure.intraday_return_vs_session_open_ratio_as_location,
        "price_movement__daily_gap_pct":payload.price_movement.daily_gap_pct,
        "price_movement__daily_prior_close":payload.price_movement.daily_prior_close,
        "price_movement__intraday_bar_close_price":payload.price_movement.intraday_bar_close_price,
        "price_movement__intraday_return_vs_prior_close_ratio":payload.price_movement.intraday_return_vs_prior_close_ratio,
        "price_movement__intraday_return_vs_session_open_ratio":payload.price_movement.intraday_return_vs_session_open_ratio,
        "trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean":payload.trading_activity.session_volume_to_time_over_prior_20_full_session_volume_mean,
        "trading_activity__daily_volume_20d_avg":payload.trading_activity.daily_volume_20d_avg,
        "trading_activity__intraday_bar_volume":payload.trading_activity.intraday_bar_volume,
        "trading_activity__intraday_session_volume_to_time":payload.trading_activity.intraday_session_volume_to_time,
        "volatility_range_state__intraday_high_so_far":payload.volatility_range_state.intraday_high_so_far,
        "volatility_range_state__intraday_low_so_far":payload.volatility_range_state.intraday_low_so_far,
        "volatility_range_state__intraday_range_so_far_ratio":payload.volatility_range_state.intraday_range_so_far_ratio,
        "calendar_version":lineage.calendar_version,
        "source_lineage_json":lineage.source_lineage_raw_json,
        "policy_versions_json":lineage.policy_versions_raw_json,
        "formula_versions_json":lineage.formula_versions_raw_json,
        "restriction_codes_json":lineage.physical_restriction_codes_raw_json,
        "context_input_fingerprint":lineage.context_input_fingerprint,
    }
    state_fingerprint=canonical_hash({
        field:_normalize(values[field]) for field in FINGERPRINT_FIELDS
    })
    candidate_id=canonical_hash({
        field:(
            state_fingerprint
            if field=="state_output_fingerprint"
            else _normalize(values[field])
        )
        for field in ID_FIELDS
    })
    return state_fingerprint,candidate_id


def validate_frozen_lineage(event: BoundedMarketStateAvailable) -> None:
    lineage=event.audit_lineage
    pairs=(
        ("source_lineage_json",lineage.source_lineage_raw_json,lineage.source_lineage),
        ("policy_versions_json",lineage.policy_versions_raw_json,lineage.policy_versions),
        ("formula_versions_json",lineage.formula_versions_raw_json,lineage.formula_versions),
    )
    for field,raw,parsed in pairs:
        if not is_deeply_immutable(parsed):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
                f"{field} is not recursively immutable",
            )
        loaded=_strict_json_loads(raw,field)
        if loaded!=to_market_state_jsonable(parsed):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
                f"{field} raw/parsed mismatch",
            )
    physical_restrictions = _json_sequence(
        lineage.physical_restriction_codes_raw_json,
        "restriction_codes_json",
    )
    if physical_restrictions != lineage.physical_provenance_restriction_codes:
        raise MarketStateContractError(
            "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
            "physical provenance restriction raw/parsed mismatch",
        )
    if event.replay_consumption_restriction_codes != EXPECTED_RESTRICTIONS:
        raise MarketStateContractError(
            "FAIL_MARKET_STATE_STORE_UNVALIDATED_EVENT",
            "bounded replay restriction mismatch",
        )


class MarketStateConsumerV0_1:
    @staticmethod
    def validate_authority_roles(authority: Mapping[str, str]) -> None:
        if set(authority) != set(AUTHORITY_FIELDS):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_AUTHORITY_MISMATCH",
                "authority field set",
            )
        if authority.get("current_runtime_content_sha256") == "b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2":
            raise MarketStateContractError("FAIL_MARKET_STATE_HASH_ROLE_SUBSTITUTION", "historical profile provenance used as runtime content")
        for field, expected in FROZEN_PROVIDER_AUTHORITY.items():
            if authority.get(field) != expected:
                raise MarketStateContractError("FAIL_MARKET_STATE_AUTHORITY_MISMATCH", field)
        _require_nonempty_string(
            authority.get("candidate_dataset_id"),
            "candidate_dataset_id",
            "FAIL_MARKET_STATE_AUTHORITY_MISMATCH",
        )
        _require_sha256(
            authority.get("candidate_dataset_fingerprint"),
            "candidate_dataset_fingerprint",
            "FAIL_MARKET_STATE_AUTHORITY_MISMATCH",
        )

    @staticmethod
    def reject_operational_routing(target: str) -> None:
        if target in {"execution", "valuation", "strategy", "orders", "fills", "pnl"}:
            raise MarketStateContractError("FAIL_MARKET_STATE_OPERATIONAL_ROUTING_PROHIBITED", target)

    @staticmethod
    def require_typed_payload(payload: Any) -> None:
        if not isinstance(payload, TypedCoreFourMarketStatePayload):
            raise MarketStateContractError("FAIL_MARKET_STATE_TYPED_PAYLOAD_REQUIRED", type(payload).__name__)

    @staticmethod
    def validate_column_mapping(envelope: tuple[str, ...], payload: tuple[str, ...], lineage: tuple[str, ...]) -> None:
        mapped = envelope + payload + lineage
        if len(mapped) != len(set(mapped)) or set(mapped) != set(PHYSICAL_COLUMNS):
            raise MarketStateContractError("FAIL_MARKET_STATE_COLUMN_MAPPING_NOT_BIJECTIVE", "mapping")

    @staticmethod
    def validate_ordered_sequence(events: tuple[Any, ...]) -> None:
        keys = tuple(state_aware_order_key(event) for event in events)
        if keys != tuple(sorted(keys)):
            raise MarketStateContractError("FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY", "noncanonical sequence")
        if len(keys) != len(set(keys)):
            raise MarketStateContractError("FAIL_MARKET_STATE_UNRESOLVED_ORDER_TIE", "duplicate order key")

    @staticmethod
    def require_probe_visibility(store: Any, candidate_id: str, observed_at_utc: datetime) -> BoundedMarketStateAvailable:
        event = store.get_exact(candidate_id, observed_at_utc)
        if event is None:
            raise MarketStateContractError("FAIL_MARKET_STATE_OBSERVATION_BEFORE_STORE", candidate_id)
        return event

    @staticmethod
    def validate_fixture_boundary(fixture: Mapping[str, Any]) -> None:
        if set(fixture) != set(ROW_DOCUMENT_FIELDS):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED", "raw fixture schema")
        if (
            fixture.get("fixture_class") != "SYNTHETIC_TYPED_MARKET_STATE"
            or fixture.get("physical_source_rows") != 0
            or fixture.get("provider_parquet_opened") is not False
            or fixture.get("not_provider_evidence") is not True
            or fixture.get("not_scientific_observation") is not True
            or fixture.get("synthetic") is not True
            or not isinstance(fixture.get("records"),list)
        ):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED", "fixture boundary")

    @staticmethod
    def validate_sidecar_fixture_boundary(fixture: Mapping[str,Any]) -> None:
        if set(fixture) != set(SIDECAR_DOCUMENT_FIELDS):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED","sidecar fixture schema")
        if (
            fixture.get("fixture_class")!="SYNTHETIC_TYPED_MARKET_STATE"
            or fixture.get("physical_source_rows")!=0
            or fixture.get("provider_parquet_opened") is not False
            or fixture.get("not_provider_evidence") is not True
            or fixture.get("not_scientific_observation") is not True
            or fixture.get("synthetic") is not True
            or not isinstance(fixture.get("records"),list)
        ):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED","sidecar fixture boundary")

    @staticmethod
    def validate_market_bar_fixture_boundary(fixture: Mapping[str,Any]) -> None:
        if set(fixture) != set(MARKET_BAR_DOCUMENT_FIELDS):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED","bar fixture schema")
        if (
            fixture.get("fixture_class")!="SYNTHETIC_MARKET_DATA_BARS"
            or fixture.get("physical_source_rows")!=0
            or fixture.get("provider_parquet_opened") is not False
            or fixture.get("not_provider_evidence") is not True
            or fixture.get("not_scientific_observation") is not True
            or fixture.get("synthetic") is not True
            or not isinstance(fixture.get("records"),list)
        ):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED","bar fixture boundary")

    @staticmethod
    def validate_fixture_manifest_boundary(fixture: Mapping[str,Any]) -> None:
        if set(fixture) != set(FIXTURE_MANIFEST_FIELDS):
            raise MarketStateContractError("FAIL_SYNTHETIC_INPUT_MANIFEST_COVERAGE","fixture manifest schema")
        if (
            fixture.get("fixture_class")!="SYNTHETIC_TYPED_MARKET_STATE"
            or fixture.get("physical_source_rows")!=0
            or fixture.get("provider_parquet_opened") is not False
            or fixture.get("not_provider_evidence") is not True
            or fixture.get("not_scientific_observation") is not True
            or fixture.get("synthetic") is not True
            or fixture.get("record_count")!=2
            or fixture.get("market_bar_record_count")!=2
        ):
            raise MarketStateContractError("FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED","fixture manifest boundary")

    def validate_schema_contract(self, schema: Mapping[str,Any]) -> None:
        columns=schema.get("columns")
        if schema.get("column_count")!=40 or not isinstance(columns,list) or len(columns)!=40: raise MarketStateContractError("FAIL_MARKET_STATE_SCHEMA_COLUMN_COUNT","expected 40")
        names=tuple(c.get("name") for c in columns)
        if names!=PHYSICAL_COLUMNS: raise MarketStateContractError("FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH","column order/name mismatch")
        for c in columns:
            if c.get("type")!=EXPECTED_TYPES[c["name"]] or c.get("nullable") is not False: raise MarketStateContractError("FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH",c["name"])
        if set(ENVELOPE_COLUMNS)|set(PAYLOAD_COLUMNS)|set(LINEAGE_COLUMNS)!=set(PHYSICAL_COLUMNS): raise MarketStateContractError("FAIL_MARKET_STATE_COLUMN_MAPPING_NOT_BIJECTIVE","mapping coverage")
        if sum(map(len,(ENVELOPE_COLUMNS,PAYLOAD_COLUMNS,LINEAGE_COLUMNS)))!=40: raise MarketStateContractError("FAIL_MARKET_STATE_COLUMN_MAPPING_NOT_BIJECTIVE","mapping duplicate")

    def build_event(
        self,
        row: Mapping[str,Any],
        sidecar: Mapping[str,Any],
        authority: Mapping[str,str],
        consumed_sidecar_sha256: str,
    ) -> BoundedMarketStateAvailable:
        self.validate_authority_roles(authority)
        _require_sha256(
            consumed_sidecar_sha256,
            "consumed_sidecar_sha256",
            "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
        )
        if set(row) != set(PHYSICAL_COLUMNS) or len(row) != len(PHYSICAL_COLUMNS):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH",
                "synthetic row shape",
            )
        for field in NONEMPTY_ROW_FIELDS:
            _require_nonempty_string(row.get(field),field)
        if row["state_profile_id"]!=PROFILE_ID:
            raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH","profile")
        if row["state_schema_version"]!=STATE_SCHEMA_VERSION:
            raise MarketStateContractError("FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH","state_schema_version")
        _require_sha256(row["materialized_state_candidate_id"],"materialized_state_candidate_id")
        _require_sha256(row["state_output_fingerprint"],"state_output_fingerprint")
        _require_sha256(row["context_input_fingerprint"],"context_input_fingerprint")

        missing=set(SIDECAR_FIELDS)-set(sidecar)
        extra=set(sidecar)-set(SIDECAR_FIELDS)
        if missing:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
                f"missing: {sorted(missing)}",
            )
        if extra:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_SIDECAR_SCHEMA_MISMATCH",
                f"unexpected: {sorted(extra)}",
            )
        for field in SIDECAR_FIELDS-{
            "component_availability_evidence",
            "restriction_codes",
            "sidecar_schema_id",
        }:
            _require_nonempty_string(
                sidecar.get(field),
                field,
                "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
            )
        _require_sha256(
            sidecar["candidate_dataset_fingerprint"],
            "candidate_dataset_fingerprint",
            "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
        )
        _require_sha256(
            sidecar["materialized_state_candidate_id"],
            "materialized_state_candidate_id",
            "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
        )
        _require_sha256(
            sidecar["state_output_fingerprint"],
            "state_output_fingerprint",
            "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
        )
        pairs=(
            "materialized_state_candidate_id","source_candidate_record_id",
            "instrument_id","ticker","session_date","context_id",
            "decision_timestamp_utc",
        )
        for field in pairs:
            if row[field]!=sidecar[field]:
                raise MarketStateContractError(
                    "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
                    field,
                )
        if row["state_output_fingerprint"]!=sidecar["state_output_fingerprint"]:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_SIDECAR_FINGERPRINT_MISMATCH",
                "state_output_fingerprint",
            )
        if sidecar["physical_profile_id"]!=PHYSICAL_PROFILE_ID or sidecar["profile_id"]!=PROFILE_ID:
            raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH","profile")
        if sidecar["state_availability_policy_id"]!=AVAILABILITY_POLICY_ID:
            raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH","availability policy")
        if sidecar["sidecar_schema_id"]!=SIDECAR_SCHEMA_ID:
            raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH","sidecar schema")
        if (
            sidecar["candidate_dataset_id"]!=authority["candidate_dataset_id"]
            or sidecar["candidate_dataset_fingerprint"]!=authority["candidate_dataset_fingerprint"]
        ):
            raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH","dataset")

        values=[]
        for field in PAYLOAD_COLUMNS:
            value=row[field]
            if value is None:
                raise MarketStateContractError("FAIL_MARKET_STATE_CORE_FOUR_INCOMPLETE",field)
            if not isinstance(value,float) or not math.isfinite(value):
                raise MarketStateContractError("FAIL_MARKET_STATE_NON_FINITE_VALUE",field)
            values.append(value)

        source_lineage=_json_mapping(row["source_lineage_json"],"source_lineage_json")
        policy_versions=_json_mapping(row["policy_versions_json"],"policy_versions_json")
        formula_versions=_json_mapping(row["formula_versions_json"],"formula_versions_json")
        raw_restrictions=_json_sequence(row["restriction_codes_json"],"restriction_codes_json")
        restrictions=_canonical_restrictions(sidecar["restriction_codes"],"sidecar")
        decision=_utc(row["decision_timestamp_utc"])
        as_of=_utc(sidecar["state_as_of_utc"])
        available=_utc(sidecar["state_available_at_utc"])
        try:
            session_date=date.fromisoformat(row["session_date"])
        except ValueError as exc:
            raise MarketStateContractError("FAIL_MARKET_STATE_IDENTITY_INVALID","session_date") from exc

        state_fp=canonical_hash({field:_normalize(row[field]) for field in FINGERPRINT_FIELDS})
        if state_fp!=row["state_output_fingerprint"] or state_fp!=sidecar["state_output_fingerprint"]:
            raise MarketStateContractError("FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH","state fingerprint")
        candidate=canonical_hash({
            field:(state_fp if field=="state_output_fingerprint" else _normalize(row[field]))
            for field in ID_FIELDS
        })
        if candidate!=row["materialized_state_candidate_id"]:
            raise MarketStateContractError("FAIL_MARKET_STATE_CANDIDATE_ID_MISMATCH","candidate id")
        raw_restrictions=_physical_provenance_restrictions(raw_restrictions)

        components=self._components(sidecar,restrictions)
        if as_of>decision or decision>available:
            raise MarketStateContractError("FAIL_MARKET_STATE_TEMPORAL_LEAKAGE","row temporal order")
        component_as_of_max=max(item.component_as_of_utc for item in components)
        component_available_max=max(item.component_available_at_utc for item in components)
        if any(
            item.component_as_of_utc>decision
            or item.component_available_at_utc>available
            for item in components
        ):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_COMPONENT_TEMPORAL_ORDER",
                "component exceeds row decision/availability",
            )
        if as_of!=component_as_of_max:
            raise MarketStateContractError("FAIL_MARKET_STATE_AS_OF_DERIVATION_MISMATCH","state_as_of_utc")
        if available!=max(decision,component_available_max):
            raise MarketStateContractError("FAIL_MARKET_STATE_AVAILABILITY_DERIVATION_MISMATCH","state_available_at_utc")
        if sidecar["state_publication_latency"]!="PT0S" or sidecar["state_publication_latency_policy_id"]!=LATENCY_POLICY_ID:
            raise MarketStateContractError("FAIL_MARKET_STATE_ZERO_LATENCY_POLICY","latency")
        if sidecar["state_replay_consumption_legality"]!="decision_safe" or sidecar["state_availability_status"]!="available_for_decision_replay":
            raise MarketStateContractError("FAIL_MARKET_STATE_NOT_DECISION_SAFE","legality")

        payload=TypedCoreFourMarketStatePayload(
            PriceLocationStructurePayload(*values[0:5]),
            PriceMovementPayload(*values[5:10]),
            TradingActivityPayload(*values[10:14]),
            VolatilityRangeStatePayload(*values[14:17]),
        )
        lineage=MarketStateAuditLineage(
            materialization_run_id=row["materialization_run_id"],
            source_integration_run_id=row["source_integration_run_id"],
            source_candidate_record_id=row["source_candidate_record_id"],
            source_integration_profile_id=row["source_integration_profile_id"],
            decision_case=row["decision_case"],
            context_id=row["context_id"],
            integration_status=row["integration_status"],
            object_completeness_status=row["object_completeness_status"],
            quality_status=row["quality_status"],
            calendar_version=row["calendar_version"],
            context_input_fingerprint=row["context_input_fingerprint"],
            source_lineage_raw_json=row["source_lineage_json"],
            source_lineage=source_lineage,
            policy_versions_raw_json=row["policy_versions_json"],
            policy_versions=policy_versions,
            formula_versions_raw_json=row["formula_versions_json"],
            formula_versions=formula_versions,
            physical_restriction_codes_raw_json=row["restriction_codes_json"],
            physical_provenance_restriction_codes=raw_restrictions,
            component_availability_evidence=components,
            provider_handoff_sha256=authority["provider_handoff_sha256"],
            nested_provider_evidence_sha256=authority["nested_provider_evidence_sha256"],
            structural_schema_sha256=authority["structural_schema_sha256"],
            current_runtime_content_sha256=authority["current_runtime_content_sha256"],
            state_bundle_ref_id=authority["state_bundle_ref_id"],
            state_bundle_canonical_sha256=authority["state_bundle_canonical_sha256"],
            sidecar_id=sidecar["sidecar_id"],
            sidecar_schema_id=sidecar["sidecar_schema_id"],
            consumed_sidecar_sha256=consumed_sidecar_sha256,
            provider_sidecar_authority_sha256=authority["sidecar_sha256"],
            binding_id=authority["binding_id"],
            binding_sha256=authority["binding_sha256"],
        )
        return BoundedMarketStateAvailable(
            event_type="BoundedMarketStateAvailable",
            state_kind="market_state",
            profile_id=PROFILE_ID,
            state_schema_version=STATE_SCHEMA_VERSION,
            physical_profile_id=PHYSICAL_PROFILE_ID,
            candidate_dataset_id=authority["candidate_dataset_id"],
            candidate_dataset_fingerprint=authority["candidate_dataset_fingerprint"],
            materialized_state_candidate_id=candidate,
            state_output_fingerprint=state_fp,
            instrument_id=row["instrument_id"],
            ticker=row["ticker"],
            session_date=session_date,
            decision_timestamp_utc=decision,
            state_as_of_utc=as_of,
            state_available_at_utc=available,
            state_availability_policy_id=AVAILABILITY_POLICY_ID,
            state_publication_latency_policy_id=LATENCY_POLICY_ID,
            state_publication_latency="PT0S",
            state_replay_consumption_legality="decision_safe",
            state_availability_status="available_for_decision_replay",
            replay_consumption_restriction_codes=restrictions,
            component_replay_restriction_codes=tuple(
                (
                    item.information_object_id,
                    item.component_replay_restriction_codes,
                )
                for item in components
            ),
            payload=payload,
            audit_lineage=lineage,
        )

    def validate_and_seal(self,row: Mapping[str,Any],sidecar: Mapping[str,Any],authority: Mapping[str,str],consumed_sidecar_sha256: str) -> ValidatedBoundedMarketStateAvailable:
        """Atomically validate governed inputs and issue a receipt for that result."""
        event=self.build_event(row,sidecar,authority,consumed_sidecar_sha256)
        receipt=MarketStateValidationReceipt(
            validator_id="BT_GATE_014_MARKET_STATE_VALIDATOR_V0_1",
            validation_schema_version="market_state_validation_receipt_v0_1",
            event_content_sha256=canonical_hash(event.to_dict()),
            materialized_state_candidate_id=event.materialized_state_candidate_id,
            state_output_fingerprint=event.state_output_fingerprint,
            candidate_dataset_id=event.candidate_dataset_id,
            candidate_dataset_fingerprint=event.candidate_dataset_fingerprint,
            provider_handoff_sha256=authority["provider_handoff_sha256"],
            nested_provider_evidence_sha256=authority["nested_provider_evidence_sha256"],
            structural_schema_sha256=authority["structural_schema_sha256"],
            current_runtime_content_sha256=authority["current_runtime_content_sha256"],
            consumed_sidecar_sha256=consumed_sidecar_sha256,
            binding_sha256=authority["binding_sha256"],
            validation_status="PASS",
        )
        return ValidatedBoundedMarketStateAvailable(event,receipt)

    @staticmethod
    def _join_pairs(
        rows: list[Mapping[str,Any]],
        sidecars: list[Mapping[str,Any]],
    ) -> tuple[tuple[Mapping[str,Any],Mapping[str,Any]],...]:
        grouped: dict[str,list[Mapping[str,Any]]]={}
        for sidecar in sidecars:
            if not isinstance(sidecar,Mapping):
                raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH","sidecar type")
            candidate_id=sidecar.get("materialized_state_candidate_id")
            if not isinstance(candidate_id,str) or not candidate_id:
                raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH","candidate id")
            grouped.setdefault(candidate_id,[]).append(sidecar)
        pairs=[]; consumed:set[str]=set(); seen_rows:set[str]=set()
        for row in rows:
            if not isinstance(row,Mapping):
                raise MarketStateContractError("FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH","row type")
            candidate_id=row.get("materialized_state_candidate_id")
            if not isinstance(candidate_id,str) or not candidate_id:
                raise MarketStateContractError("FAIL_MARKET_STATE_IDENTITY_INVALID","candidate id")
            if candidate_id in seen_rows:
                raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_DUPLICATE",candidate_id)
            seen_rows.add(candidate_id)
            matches=grouped.get(candidate_id,[])
            if not matches:
                raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_MISSING",candidate_id)
            if len(matches)!=1:
                raise MarketStateContractError("FAIL_MARKET_STATE_SIDECAR_DUPLICATE",candidate_id)
            pairs.append((row,matches[0])); consumed.add(candidate_id)
        orphaned=set(grouped)-consumed
        if orphaned:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH",
                f"orphan sidecars: {sorted(orphaned)}",
            )
        return tuple(pairs)

    def validate_join_and_seal(
        self,
        rows: list[Mapping[str,Any]],
        sidecars: list[Mapping[str,Any]],
        authority: Mapping[str,str],
        consumed_sidecar_sha256: str,
    ) -> tuple[ValidatedBoundedMarketStateAvailable,...]:
        """Perform the closed bijection and atomic validation used by the runner."""
        return tuple(
            self.validate_and_seal(row,sidecar,authority,consumed_sidecar_sha256)
            for row,sidecar in self._join_pairs(rows,sidecars)
        )

    def join_rows(
        self,
        rows: list[Mapping[str,Any]],
        sidecars: list[Mapping[str,Any]],
        authority: Mapping[str,str],
        consumed_sidecar_sha256: str,
    ) -> tuple[BoundedMarketStateAvailable,...]:
        return tuple(
            validated.event
            for validated in self.validate_join_and_seal(
                rows,
                sidecars,
                authority,
                consumed_sidecar_sha256,
            )
        )

    def _components(self,sidecar: Mapping[str,Any],restrictions: tuple[str,...]) -> tuple[MarketStateComponentAvailabilityEvidence,...]:
        raw=sidecar.get("component_availability_evidence")
        if not isinstance(raw,list) or len(raw)!=4: raise MarketStateContractError("FAIL_MARKET_STATE_COMPONENT_SET","expected four")
        canonical_order=("price_location_structure","price_movement","trading_activity","volatility_range_state")
        expected=set(canonical_order); seen=[]; result=[]
        for item in raw:
            if not isinstance(item,Mapping) or set(item)!=set(COMPONENT_FIELDS):
                raise MarketStateContractError("FAIL_MARKET_STATE_COMPONENT_SCHEMA_MISMATCH","component field set")
            name=item.get("information_object_id"); seen.append(name)
            component_restrictions=_component_replay_restrictions(item.get("restriction_codes"),f"component:{name}",restrictions)
            source=_utc(item["source_timestamp_utc"]); as_of=_utc(item["component_as_of_utc"]); available=_utc(item["component_available_at_utc"])
            if source>as_of or as_of>available: raise MarketStateContractError("FAIL_MARKET_STATE_COMPONENT_TEMPORAL_ORDER",str(name))
            if item.get("availability_status")!="available": raise MarketStateContractError("FAIL_MARKET_STATE_COMPONENT_LEGALITY_CONTRADICTION",str(name))
            for required in ("component_id","cutoff_rule_id","availability_rule_id"):
                if not isinstance(item.get(required),str) or not item[required].strip(): raise MarketStateContractError("FAIL_MARKET_STATE_COMPONENT_IDENTITY",f"{name}:{required}")
            result.append(MarketStateComponentAvailabilityEvidence(str(item["component_id"]),str(name),source,as_of,available,str(item["availability_status"]),component_restrictions,str(item["cutoff_rule_id"]),str(item["availability_rule_id"])))
        component_ids=[item.component_id for item in result]
        if set(seen)!=expected or len(seen)!=len(set(seen)) or len(component_ids)!=len(set(component_ids)): raise MarketStateContractError("FAIL_MARKET_STATE_COMPONENT_SET",str(seen))
        if not set().union(*(set(item.component_replay_restriction_codes) for item in result)).issubset(set(restrictions)):
            raise MarketStateContractError("FAIL_MARKET_STATE_RESTRICTION_PROPAGATION","component replay union")
        return tuple(sorted(result,key=lambda item:canonical_order.index(item.information_object_id)))

