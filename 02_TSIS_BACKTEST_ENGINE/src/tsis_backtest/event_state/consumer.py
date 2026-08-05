"""Fail-closed synthetic consumer for BT-GATE-015."""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence

from tsis_backtest.replay.state_ordering import state_aware_order_key
from tsis_backtest.market_state.contracts import (
    BoundedMarketStateAvailable,
    PriceLocationStructurePayload,
    PriceMovementPayload,
    TradingActivityPayload,
    TypedCoreFourMarketStatePayload,
    VolatilityRangeStatePayload,
)
from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayGapEvent

from .contracts import (
    BoundedEventStateAvailable,
    EventStateAuditLineage,
    EventStateContractError,
    EventStateValidationReceipt,
    EXPECTED_REPLAY_RESTRICTIONS,
    ValidatedBoundedEventStateAvailable,
    freeze,
)

PROFILE_ID = "event_state_core_four_intraday_profile_v0_1"
SCHEMA_ID = "event_state_candidate_schema_v0_1"
EVENT_STATE_SCHEMA_SHA256 = "e68be24763c4320419f7f2216a3560dc94ce36f02b293fdf2dad2ea88bba9515"
SYNTHETIC_FINGERPRINT_POLICY_ID = "BT_GATE_015_SYNTHETIC_EVENT_STATE_CANONICAL_ROW_SHA256_V0_1"
EVENT_TYPE_ID = "event_type:market_data:session_opened"
WINDOW_DEFINITION_ID = "session_opened_at_anchor_context_v0_1"
LATENCY_POLICY_ID = "zero_latency_candidate_event_state_replay_publication_policy_v0_1"
SIDECAR_SCHEMA_SHA256 = "7d814dcb50fdd9b0da604e4f443497f3b733082070ccc2ed8ff89293e773ad77"
TYPED_PAYLOAD_BINDING_SHA256 = "320fc3e9dfb532aad0e12a48af6117d50a214642b2b827a4628265808d4d3d43"
PROVIDER_CONTRACT_HANDOFF_SHA256 = "b7a4783d0ab64ffaf37fbfdf2ee76dffacbe9b14cf3f059891908c87116369b2"
PROVIDER_COMPLETION_HANDOFF_SHA256 = "3a6bf3ca04c0428a1728e1719cd6aeaea6bfaef43e12fb83939dde3cb6cb85d9"
PHYSICAL_EVENT_STATE_JSONL_SHA256 = "ed975ad7d7a3e0ac68bd7dfe2c91743c86931a545162a4440d270cbb689477dd"
PHYSICAL_EVENT_STATE_RECORD_ID = "e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76"
PHYSICAL_EVENT_STATE_RECORD_FINGERPRINT = "31f1463baf0dc8f0dba3bc130c0bb1d61092897595849df57abc6b1023853a01"
HISTORICAL_EVENT_STATE_RECORD_ID = "47102c58b14c538c0d4279ce40d4205031bd48d46986e9654fb0ccee059498e0"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

PAYLOAD_FIELDS = (
    "price_location_structure__daily_open_price",
    "price_location_structure__daily_prior_close",
    "price_location_structure__intraday_bar_close_price",
    "price_location_structure__intraday_return_vs_prior_close_ratio_as_location",
    "price_location_structure__intraday_return_vs_session_open_ratio_as_location",
    "price_movement__daily_gap_pct",
    "price_movement__daily_prior_close",
    "price_movement__intraday_bar_close_price",
    "price_movement__intraday_return_vs_prior_close_ratio",
    "price_movement__intraday_return_vs_session_open_ratio",
    "trading_activity__daily_volume_20d_avg",
    "trading_activity__intraday_bar_volume",
    "trading_activity__intraday_session_volume_to_time",
    "trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean",
    "volatility_range_state__intraday_high_so_far",
    "volatility_range_state__intraday_low_so_far",
    "volatility_range_state__intraday_range_so_far_ratio",
)

EVENT_STATE_ROW_FIELDS = (
    "event_state_record_id", "event_state_profile_id", "event_state_schema_version",
    "integration_policy_id", "integration_policy_version", "event_type_id",
    "event_family_id", "event_instance_id", "event_instance_version",
    "event_window_definition_id", "event_window_binding_id",
    "event_state_instrument_session_projection_id", "source_market_state_profile_id",
    "source_market_state_schema_version", "market_state_record_id",
    "state_output_fingerprint", "instrument_id", "ticker", "exchange_id",
    "session_date", "decision_timestamp_utc", "event_anchor_timestamp_utc",
    "window_start_utc", "window_end_utc", "relative_time_to_event", "state_role",
    "consumption_legality", "object_completeness_status", "integration_status",
    "quality_status", "calendar_version", "calendar_row_fingerprint",
    "source_lineage_json", "policy_versions_json", "restriction_codes_json",
    "created_at_utc", "supersedes_event_state_record_id",
    "superseded_by_event_state_record_id", "source_market_state_value_snapshot_json",
)
SIDECAR_RECORD_FIELDS = (
    "event_state_record_id", "event_state_record_fingerprint", "event_instance_id",
    "event_window_binding_id", "instrument_projection_id", "market_state_record_id",
    "market_state_state_output_fingerprint", "market_state_dependency_dataset_fingerprint",
    "market_state_availability_evidence_dataset_fingerprint",
    "market_state_cross_dataset_binding", "instrument_id", "ticker", "exchange_id",
    "session_date", "event_anchor_timestamp_utc", "event_instance_as_of_utc",
    "event_instance_available_at_utc", "event_window_binding_as_of_utc",
    "event_window_binding_available_at_utc", "instrument_projection_as_of_utc",
    "instrument_projection_available_at_utc", "market_state_as_of_utc",
    "market_state_available_at_utc", "event_state_as_of_utc",
    "event_state_available_at_utc", "event_state_publication_latency",
    "state_replay_consumption_legality", "event_state_provenance_restriction_codes",
    "replay_consumption_restriction_codes", "evidence_refs",
)
SIDECAR_DOCUMENT_FIELDS = ("sidecar_id", "state_kind", "profile_id", "event_type_id", "publication_policy", "record_count", "records")

def synthetic_event_state_fingerprint(row: Mapping[str, Any]) -> str:
    projected = {key: row[key] for key in EVENT_STATE_ROW_FIELDS if key != "state_output_fingerprint"}
    return canonical_hash(projected)


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise EventStateContractError("FAIL_EVENT_STATE_TIMESTAMP_NOT_CANONICAL_UTC", str(value))
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.utcoffset() != timedelta(0):
        raise EventStateContractError("FAIL_EVENT_STATE_TIMESTAMP_NOT_CANONICAL_UTC", value)
    return parsed


def _session(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise EventStateContractError("FAIL_EVENT_STATE_TIMESTAMP_NOT_CANONICAL_UTC", "ordering")
    return value.date().isoformat()


def _z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


event_state_aware_order_key = state_aware_order_key


def _strict_json(raw: str, field: str) -> Any:
    def bad(value: str) -> None:
        raise ValueError(value)
    try:
        def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate key: {key}")
                result[key] = value
            return result
        return json.loads(raw, parse_constant=bad, object_pairs_hook=unique_object)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise EventStateContractError("FAIL_EVENT_STATE_INVALID_EMBEDDED_JSON", field) from exc


def _payload(raw: str) -> tuple[TypedCoreFourMarketStatePayload, str]:
    parsed = _strict_json(raw, "source_market_state_value_snapshot_json")
    if not isinstance(parsed, dict) or set(parsed) != set(PAYLOAD_FIELDS):
        raise EventStateContractError("FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISMATCH", "closed 17-field payload")
    if any(type(parsed[key]) not in (float, int) or not math.isfinite(float(parsed[key])) for key in PAYLOAD_FIELDS):
        raise EventStateContractError("FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISMATCH", "finite numbers required")
    value = {key: float(parsed[key]) for key in PAYLOAD_FIELDS}
    payload = TypedCoreFourMarketStatePayload(
        PriceLocationStructurePayload(
            value["price_location_structure__daily_open_price"],
            value["price_location_structure__daily_prior_close"],
            value["price_location_structure__intraday_bar_close_price"],
            value["price_location_structure__intraday_return_vs_prior_close_ratio_as_location"],
            value["price_location_structure__intraday_return_vs_session_open_ratio_as_location"],
        ),
        PriceMovementPayload(
            value["price_movement__daily_gap_pct"],
            value["price_movement__daily_prior_close"],
            value["price_movement__intraday_bar_close_price"],
            value["price_movement__intraday_return_vs_prior_close_ratio"],
            value["price_movement__intraday_return_vs_session_open_ratio"],
        ),
        TradingActivityPayload(
            value["trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean"],
            value["trading_activity__daily_volume_20d_avg"],
            value["trading_activity__intraday_bar_volume"],
            value["trading_activity__intraday_session_volume_to_time"],
        ),
        VolatilityRangeStatePayload(
            value["volatility_range_state__intraday_high_so_far"],
            value["volatility_range_state__intraday_low_so_far"],
            value["volatility_range_state__intraday_range_so_far_ratio"],
        ),
    )
    return payload, hashlib.sha256(raw.encode("utf-8")).hexdigest()


_ISSUED_RECEIPTS: dict[int, tuple[str, str]] = {}


def is_issued_receipt(receipt: EventStateValidationReceipt, event: BoundedEventStateAvailable) -> bool:
    return _ISSUED_RECEIPTS.get(id(receipt)) == (canonical_hash(event.to_dict()), event.event_state_record_id)


class EventStateConsumerV0_1:
    def build_event(self, row: Mapping[str, Any], sidecar: Mapping[str, Any], sidecar_sha256: str, market_state: BoundedMarketStateAvailable | None = None) -> BoundedEventStateAvailable:
        if not SHA256_RE.fullmatch(sidecar_sha256):
            raise EventStateContractError("FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH", "sidecar hash")
        if "source_market_state_value_snapshot_json" not in row:
            raise EventStateContractError("FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISSING", "source_market_state_value_snapshot_json")
        temporal = {"event_instance_as_of_utc", "event_instance_available_at_utc", "event_window_binding_as_of_utc", "event_window_binding_available_at_utc", "instrument_projection_as_of_utc", "instrument_projection_available_at_utc", "market_state_as_of_utc", "market_state_available_at_utc", "event_state_as_of_utc", "event_state_available_at_utc"}
        if temporal - set(sidecar):
            raise EventStateContractError("FAIL_EVENT_STATE_TEMPORAL_EVIDENCE_MISSING", ",".join(sorted(temporal-set(sidecar))))
        if "component_replay_restriction_codes" in row or "component_replay_restriction_codes" in sidecar:
            raise EventStateContractError("FAIL_EVENT_STATE_COMPONENT_RESTRICTIONS_NOT_AUTHORIZED", "third restriction domain")
        if set(row) != set(EVENT_STATE_ROW_FIELDS) or set(sidecar) != set(SIDECAR_RECORD_FIELDS):
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "closed provider-compatible shapes")
        if row["event_state_profile_id"] != PROFILE_ID or row["event_state_schema_version"] != SCHEMA_ID or row["event_type_id"] != EVENT_TYPE_ID or row["event_window_definition_id"] != WINDOW_DEFINITION_ID:
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "frozen envelope authority")
        if row["state_output_fingerprint"] != synthetic_event_state_fingerprint(row):
            raise EventStateContractError("FAIL_EVENT_STATE_FINGERPRINT_MISMATCH", "synthetic row recomputation")
        pairs = (
            ("state_output_fingerprint", "event_state_record_fingerprint"),
            ("event_state_record_id", "event_state_record_id"),
            ("event_instance_id", "event_instance_id"),
            ("event_window_binding_id", "event_window_binding_id"),
            ("market_state_record_id", "market_state_record_id"),
            ("event_state_instrument_session_projection_id", "instrument_projection_id"),
            ("consumption_legality", "state_replay_consumption_legality"),
            ("instrument_id", "instrument_id"), ("ticker", "ticker"),
            ("exchange_id", "exchange_id"), ("session_date", "session_date"),
            ("event_anchor_timestamp_utc", "event_anchor_timestamp_utc"),
        )
        if any(row[left] != sidecar[right] for left, right in pairs):
            raise EventStateContractError("FAIL_EVENT_STATE_IDENTITY_MISMATCH", "physical-sidecar join")
        provenance = _strict_json(row["restriction_codes_json"], "restriction_codes_json")
        if not isinstance(provenance, list) or len(provenance) != len(set(provenance)) or set(provenance) != set(sidecar["event_state_provenance_restriction_codes"]):
            raise EventStateContractError("FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH", "provenance")
        replay = tuple(sidecar["replay_consumption_restriction_codes"])
        if len(replay) != len(set(replay)) or set(replay) != set(EXPECTED_REPLAY_RESTRICTIONS):
            raise EventStateContractError("FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH", "replay")
        if sidecar["state_replay_consumption_legality"] != "research_only":
            raise EventStateContractError("FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION", "legality")
        if sidecar["market_state_cross_dataset_binding"] != "EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE":
            raise EventStateContractError("FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH", "cross-dataset binding")
        for field in (
            "event_state_record_id", "event_state_record_fingerprint", "event_instance_id",
            "event_window_binding_id", "instrument_projection_id", "market_state_record_id",
            "market_state_state_output_fingerprint", "market_state_dependency_dataset_fingerprint",
            "market_state_availability_evidence_dataset_fingerprint",
        ):
            if not isinstance(sidecar[field], str) or not SHA256_RE.fullmatch(sidecar[field]):
                raise EventStateContractError("FAIL_EVENT_STATE_IDENTITY_MISMATCH", field)
        if sidecar["event_state_record_id"] in {PHYSICAL_EVENT_STATE_RECORD_ID, HISTORICAL_EVENT_STATE_RECORD_ID}:
            raise EventStateContractError("FAIL_EVENT_STATE_SYNTHETIC_IDENTITY_COLLISION", "provider identity in synthetic fixture")
        payload, snapshot_hash = _payload(row["source_market_state_value_snapshot_json"])
        if market_state is None:
            raise EventStateContractError("FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH", "validated Market State required")
        if (
            market_state.materialized_state_candidate_id != sidecar["market_state_record_id"]
            or market_state.state_output_fingerprint != sidecar["market_state_state_output_fingerprint"]
            or market_state.instrument_id != sidecar["instrument_id"]
            or market_state.session_date.isoformat() != sidecar["session_date"]
            or canonical_hash(market_state.payload.to_dict()) != canonical_hash(payload.to_dict())
        ):
            raise EventStateContractError("FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH", "validated dependency identity/payload")
        as_of_fields = ("event_instance_as_of_utc", "event_window_binding_as_of_utc", "instrument_projection_as_of_utc", "market_state_as_of_utc")
        available_fields = ("event_instance_available_at_utc", "event_window_binding_available_at_utc", "instrument_projection_available_at_utc", "market_state_available_at_utc")
        as_of = [utc(sidecar[field]) for field in as_of_fields]
        available = [utc(sidecar[field]) for field in available_fields]
        event_as_of = utc(sidecar["event_state_as_of_utc"])
        event_available = utc(sidecar["event_state_available_at_utc"])
        if sidecar["event_state_publication_latency"] != "PT0S" or event_as_of != max(as_of) or event_available != max(available):
            raise EventStateContractError("FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION", "derivation")
        if utc(sidecar["event_anchor_timestamp_utc"]) > event_as_of or event_as_of > event_available:
            raise EventStateContractError("FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION", "ordering")
        lineage = EventStateAuditLineage(
            row["source_market_state_value_snapshot_json"], snapshot_hash,
            tuple(sorted(provenance)), sidecar_sha256,
            PROVIDER_CONTRACT_HANDOFF_SHA256, PROVIDER_COMPLETION_HANDOFF_SHA256,
            SIDECAR_SCHEMA_SHA256, TYPED_PAYLOAD_BINDING_SHA256, EVENT_STATE_SCHEMA_SHA256,
            SYNTHETIC_FINGERPRINT_POLICY_ID, freeze(dict(row)), True, 0,
            freeze({"window_definition_id": WINDOW_DEFINITION_ID, "physical_input": "NOT_READ", "evidence_refs": dict(sidecar["evidence_refs"])}),
        )
        return BoundedEventStateAvailable(
            "BoundedEventStateAvailable", "event_state", PROFILE_ID, SCHEMA_ID,
            EVENT_TYPE_ID, sidecar["event_instance_id"], sidecar["event_window_binding_id"],
            sidecar["instrument_projection_id"], sidecar["market_state_record_id"],
            sidecar["market_state_state_output_fingerprint"],
            sidecar["market_state_cross_dataset_binding"], sidecar["event_state_record_id"],
            sidecar["event_state_record_fingerprint"], sidecar["instrument_id"],
            sidecar["ticker"], sidecar["exchange_id"],
            datetime.fromisoformat(sidecar["session_date"]).date(),
            utc(sidecar["event_anchor_timestamp_utc"]), event_as_of, event_available,
            LATENCY_POLICY_ID, "PT0S", "research_only", tuple(sorted(replay)), payload, lineage,
        )

    def validate_and_seal(self, row: Mapping[str, Any], sidecar: Mapping[str, Any], sidecar_sha256: str, market_state: BoundedMarketStateAvailable | None = None) -> ValidatedBoundedEventStateAvailable:
        event = self.build_event(row, sidecar, sidecar_sha256, market_state)
        receipt = EventStateValidationReceipt(
            "BT_GATE_015_EVENT_STATE_VALIDATOR_V0_1",
            "event_state_validation_receipt_v0_1",
            canonical_hash(event.to_dict()), event.event_state_record_id,
            event.event_state_record_fingerprint, sidecar_sha256,
            PROVIDER_CONTRACT_HANDOFF_SHA256, PROVIDER_COMPLETION_HANDOFF_SHA256,
            SIDECAR_SCHEMA_SHA256, TYPED_PAYLOAD_BINDING_SHA256, EVENT_STATE_SCHEMA_SHA256, "PASS",
        )
        _ISSUED_RECEIPTS[id(receipt)] = (receipt.event_content_sha256, receipt.event_state_record_id)
        return ValidatedBoundedEventStateAvailable(event, receipt)

    def validate_sidecar_document(self, sidecar_document: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
        if set(sidecar_document) != set(SIDECAR_DOCUMENT_FIELDS):
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "sidecar envelope")
        if sidecar_document["state_kind"] != "event_state" or sidecar_document["profile_id"] != PROFILE_ID or sidecar_document["event_type_id"] != EVENT_TYPE_ID:
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "sidecar authority")
        policy = sidecar_document["publication_policy"]
        if policy != {"policy_id": LATENCY_POLICY_ID, "latency": "PT0S", "bounded_validation_only": True}:
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "publication policy")
        sidecars = sidecar_document.get("records")
        if not isinstance(sidecars, list) or not sidecars or sidecar_document["record_count"] != len(sidecars):
            raise EventStateContractError("FAIL_EVENT_STATE_SIDECAR_BIJECTION", "sidecar cardinality")
        temporal = {"event_instance_as_of_utc", "event_instance_available_at_utc", "event_window_binding_as_of_utc", "event_window_binding_available_at_utc", "instrument_projection_as_of_utc", "instrument_projection_available_at_utc", "market_state_as_of_utc", "market_state_available_at_utc", "event_state_as_of_utc", "event_state_available_at_utc"}
        for record in sidecars:
            if temporal - set(record):
                raise EventStateContractError("FAIL_EVENT_STATE_TEMPORAL_EVIDENCE_MISSING", ",".join(sorted(temporal-set(record))))
            if "component_replay_restriction_codes" in record:
                raise EventStateContractError("FAIL_EVENT_STATE_COMPONENT_RESTRICTIONS_NOT_AUTHORIZED", "third restriction domain")
            if set(record) != set(SIDECAR_RECORD_FIELDS):
                raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "sidecar record")
            refs = record.get("evidence_refs")
            if not isinstance(refs, dict) or len(refs) < 6 or any(
                not isinstance(value, str) or not SHA256_RE.fullmatch(value)
                for value in refs.values()
            ):
                raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "sidecar evidence_refs")
        return tuple(sidecars)

    def join_document(self, rows_document: Mapping[str, Any], sidecar_document: Mapping[str, Any], sidecar_sha256: str, market_state: BoundedMarketStateAvailable | None = None) -> tuple[ValidatedBoundedEventStateAvailable, ...]:
        sidecars = self.validate_sidecar_document(sidecar_document)
        rows = rows_document.get("records")
        if not isinstance(rows, list):
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "rows envelope")
        if len(rows) != 1 or len(sidecars) != 1:
            raise EventStateContractError("FAIL_EVENT_STATE_SCOPE_LEAKAGE", "bounded slice requires exactly one row")
        return self.join_rows(rows, sidecars, sidecar_sha256, market_state)

    def join_bytes(self, rows_raw: bytes, sidecar_raw: bytes, expected_sidecar_sha256: str, market_state: BoundedMarketStateAvailable) -> tuple[ValidatedBoundedEventStateAvailable, ...]:
        actual = hashlib.sha256(sidecar_raw).hexdigest()
        if actual != expected_sidecar_sha256:
            raise EventStateContractError("FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH", "sidecar bytes")
        try:
            rows_document = _strict_json(rows_raw.decode("utf-8"), "event rows document")
            sidecar_document = _strict_json(sidecar_raw.decode("utf-8"), "event sidecar document")
        except UnicodeDecodeError as exc:
            raise EventStateContractError("FAIL_EVENT_STATE_SCHEMA_MISMATCH", "UTF-8") from exc
        return self.join_document(rows_document, sidecar_document, actual, market_state)

    def join_rows(self, rows: Sequence[Mapping[str, Any]], sidecars: Sequence[Mapping[str, Any]], sidecar_sha256: str, market_state: BoundedMarketStateAvailable | None = None) -> tuple[ValidatedBoundedEventStateAvailable, ...]:
        if len(rows) != len(sidecars):
            raise EventStateContractError("FAIL_EVENT_STATE_SIDECAR_BIJECTION", "cardinality")
        row_keys = [row.get("state_output_fingerprint") for row in rows]
        side_keys = [side.get("event_state_record_fingerprint") for side in sidecars]
        if len(row_keys) != len(set(row_keys)) or len(side_keys) != len(set(side_keys)) or set(row_keys) != set(side_keys):
            raise EventStateContractError("FAIL_EVENT_STATE_SIDECAR_BIJECTION", "keys")
        by_key = {side["event_state_record_fingerprint"]: side for side in sidecars}
        return tuple(self.validate_and_seal(row, by_key[row["state_output_fingerprint"]], sidecar_sha256, market_state) for row in rows)

    @staticmethod
    def reject_operational_routing(target: str) -> None:
        if target in {"strategy", "execution", "valuation", "orders", "fills", "pnl"}:
            raise EventStateContractError("FAIL_EVENT_STATE_OPERATIONAL_ROUTING_PROHIBITED", target)
