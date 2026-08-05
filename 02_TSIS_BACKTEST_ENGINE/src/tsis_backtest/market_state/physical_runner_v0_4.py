"""Frozen two-row physical Market State integration runner for BT-GATE-014."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.replay.contracts import ReplayBarEvent

from .consumer import (
    EXPECTED_TYPES,
    FROZEN_PROVIDER_AUTHORITY,
    MarketStateConsumerV0_1,
    PHYSICAL_COLUMNS,
    _utc,
    canonical_hash,
    state_aware_order_key,
)
from .contracts import (
    BoundedConsumerProbeObservation,
    BoundedMarketStateAvailable,
    EXPECTED_RESTRICTIONS,
    MarketStateContractError,
    ValidatedBoundedMarketStateAvailable,
    to_market_state_jsonable,
)
from .physical_authorization_v0_4 import (
    AUTHORIZATION_ID,
    CONSUMER_ID,
    CONTRACT_CONSUMER_ID,
    RUN_ID,
    AuthorizationV04,
    atomic_write_json,
    sha256_file,
)
from .store import MarketStateStore


PHYSICAL_INPUT_NAMES = (
    "candidate_parquet",
    "physical_schema_contract",
    "binding",
    "sidecar_manifest",
    "sidecar_contract",
    "timestamp_contract",
    "lineage_manifest",
    "temporal_legality_report",
    "state_bundle_manifest",
)

PROVIDER_RELATIVE_PATHS = {
    "binding": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "09_STATE_CONSUMPTION_BOUNDARY/"
        "market_state_core_four_scale_validation_physical_schema_binding_v0_1.json"
    ),
    "candidate_parquet": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "08_RUNTIME_CAPABILITIES/runs/"
        "market_state_on_demand_scale_validation_v0_1_20260727T133641Z/"
        "market_state_scale_validation_candidate_v0_1.parquet"
    ),
    "lineage_manifest": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "08_RUNTIME_CAPABILITIES/runs/"
        "market_state_on_demand_scale_validation_v0_1_20260727T133641Z/"
        "lineage_manifest.json"
    ),
    "physical_schema_contract": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "06_MARKET_STATE_INTEGRATION/official_profiles/"
        "market_state_core_four_intraday_profile_v0_1/"
        "PHYSICAL_SCHEMA_CONTRACT.json"
    ),
    "sidecar_contract": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "09_STATE_CONSUMPTION_BOUNDARY/"
        "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json"
    ),
    "sidecar_manifest": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "09_STATE_CONSUMPTION_BOUNDARY/"
        "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
    ),
    "state_bundle_manifest": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "08_RUNTIME_CAPABILITIES/"
        "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_"
        "state_bundle_manifest_v0_1.json"
    ),
    "temporal_legality_report": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "08_RUNTIME_CAPABILITIES/runs/"
        "market_state_on_demand_scale_validation_v0_1_20260727T133641Z/"
        "market_state_temporal_legality_report.json"
    ),
    "timestamp_contract": (
        "00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/"
        "09_STATE_CONSUMPTION_BOUNDARY/"
        "market_state_core_four_replay_availability_timestamp_contract_v0_1.json"
    ),
}

PHYSICAL_INPUT_SHA256 = {
    "binding": "4006e80f099bb8abec147e33670294d7cc2eb565d25a10a08d6bf929c247f083",
    "candidate_parquet": "bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68",
    "lineage_manifest": "85e7331b1b022d4075608bc4b8663de53dcb6234f21215ff232ad84c85cd4c52",
    "physical_schema_contract": "595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b",
    "sidecar_contract": "a29f656a6fe741432c7272d6715637eeb49fd5d34ca550c3ac0f33166bc1b169",
    "sidecar_manifest": "8e426b09bb1cafac26e49c7a81de31ef4ea60ca3b56ac3aa766ba13a0772c5ac",
    "state_bundle_manifest": "0845642ba80fac75f0094bccd370db71157da2759cad7807885b2928d2d49ab0",
    "temporal_legality_report": "0eb607a4286dd3d4819f9aeb8da0eb21a18955a269b87e001f8f672378c44c70",
    "timestamp_contract": "eae02c685f7bc2cc8b55e6e3bb4a6912dc3b391042c0178b3dc29387fa6b690d",
}

ADOPTED_EVIDENCE_RELATIVE_PATHS = {
    "outer_provider_handoff": (
        "evidence/provider_handoffs/bt_gate_014/"
        "market_state_pit_bt_gate_014_contract_handoff_v0_1_20260730T091041Z.zip"
    ),
    "nested_provider_evidence": (
        "evidence/provider_handoffs/bt_gate_014/"
        "bounded_state_bundle_read_and_replay_execution_and_review_v0_1_files_"
        "20260730T080831Z.zip"
    ),
}

ADOPTED_EVIDENCE_SHA256 = {
    "outer_provider_handoff": "2c578ce9216bb3fd9010ef1f4afe8ba4022ab6b15f665d276a957f50acb35112",
    "nested_provider_evidence": "8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7",
}

BARRIER_FIXTURE_RELATIVE_PATH = (
    "configs/fixtures/BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_4.json"
)

AUTHORIZED_ROWS = (
    {
        "context_id": "scale_c_context_0058",
        "decision_timestamp_utc": "2021-03-15T13:30:00Z",
        "instrument_id": "cik_ticker:0001651625:ACIU",
        "materialized_state_candidate_id": (
            "f09492ac417d05161f70ee75f81e345a9cc315cef9beb9939d2df6ff3eb58dd3"
        ),
        "session_date": "2021-03-15",
        "source_candidate_record_id": (
            "25672915a752b75e823409fc6dad6b55eaeddb900a0e58b7f5eab5f7c2ed941d"
        ),
        "state_available_at_utc": "2021-03-15T13:30:00Z",
        "state_output_fingerprint": (
            "f7c926be8e8bb6e84433061213bc554d54de2e03d0910a799e974ff5aea04617"
        ),
        "ticker": "ACIU",
    },
    {
        "context_id": "scale_c_context_0115",
        "decision_timestamp_utc": "2021-03-15T20:00:00Z",
        "instrument_id": "cik_ticker:0001651625:ACIU",
        "materialized_state_candidate_id": (
            "26d923a282355ad242a5d91ad7d6183bed6a94842041ecf966ac70c366308c0e"
        ),
        "session_date": "2021-03-15",
        "source_candidate_record_id": (
            "27c2b0b4973a880ab31d3df65c9977014f8b6e0a41c8d94e176031ff27672198"
        ),
        "state_available_at_utc": "2021-03-15T20:00:00Z",
        "state_output_fingerprint": (
            "2420034cb851629b48ee3216713b6bc1a337ce0a4356096575a3db1a91edb7bd"
        ),
        "ticker": "ACIU",
    },
)


@dataclass(frozen=True)
class FrozenPhysicalRunSpec:
    provider_relative_paths: Mapping[str, str]
    physical_input_sha256: Mapping[str, str]
    adopted_evidence_relative_paths: Mapping[str, str]
    adopted_evidence_sha256: Mapping[str, str]
    authorized_rows: tuple[Mapping[str, str], ...]
    barrier_fixture_relative_path: str
    barrier_fixture_sha256: str
    run_id: str = RUN_ID
    run_directory: str = f"runs/{RUN_ID}"


PRODUCTION_SPEC = FrozenPhysicalRunSpec(
    provider_relative_paths=PROVIDER_RELATIVE_PATHS,
    physical_input_sha256=PHYSICAL_INPUT_SHA256,
    adopted_evidence_relative_paths=ADOPTED_EVIDENCE_RELATIVE_PATHS,
    adopted_evidence_sha256=ADOPTED_EVIDENCE_SHA256,
    authorized_rows=AUTHORIZED_ROWS,
    barrier_fixture_relative_path=BARRIER_FIXTURE_RELATIVE_PATH,
    barrier_fixture_sha256=(
        "03268886123d7b2361711385970c13048ba7d1ba9027e386a88ebeed7a35e8b2"
    ),
)


CONFIG_FIELDS = {
    "adopted_evidence_relative_paths",
    "adopted_evidence_sha256",
    "allowed_operation",
    "authorization_id",
    "authorization_version",
    "authorized_rows",
    "barrier_fixture_relative_path",
    "barrier_fixture_sha256",
    "binding_sha256",
    "consumer_id",
    "contract_consumer_id",
    "fills",
    "maximum_physical_files",
    "maximum_physical_rows",
    "orders",
    "physical_input_sha256",
    "pnl",
    "production",
    "provider_relative_paths",
    "run_directory",
    "run_id",
    "strategy",
}

SUCCESS_ARTIFACTS_BEFORE_FINAL = (
    "authorization_consumption_receipt.json",
    "pre_run_manifest.json",
    "resolved_physical_input_manifest.json",
    "physical_schema_validation_report.json",
    "physical_row_identity_report.json",
    "bounded_market_state_events.json",
    "state_aware_event_sequence.json",
    "market_state_store_trace.json",
    "bounded_consumer_probe_observations.json",
    "boundary_preservation_report.json",
    "deterministic_reproduction_source.json",
    "physical_consumer_validation_report.json",
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise MarketStateContractError(
            "FAIL_BT_GATE_014_PHYSICAL_INPUT_JSON_INVALID",
            str(path),
        ) from exc


def _write_json(path: Path, data: Any) -> None:
    atomic_write_json(path, to_market_state_jsonable(data))


def _normalize_arrow_row(row: Mapping[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, dt.datetime):
            if (
                value.tzinfo is None
                or value.utcoffset() is None
                or value.utcoffset() != dt.timedelta(0)
            ):
                raise MarketStateContractError(
                    "FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC",
                    key,
                )
            normalized[key] = (
                value.astimezone(dt.timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )
        elif isinstance(value, dt.date):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    return normalized


class BoundedPhysicalMarketStateEventLoopV04:
    """Dispatch only synthetic barriers and the two authorized state events."""

    def __init__(self, consumer: MarketStateConsumerV0_1) -> None:
        self.consumer = consumer

    def run(
        self,
        validated_events: Sequence[ValidatedBoundedMarketStateAvailable],
        barrier_events: Sequence[ReplayBarEvent],
    ) -> tuple[
        MarketStateStore,
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        by_id = {
            item.event.materialized_state_candidate_id: item
            for item in validated_events
        }
        if len(by_id) != len(validated_events):
            raise MarketStateContractError(
                "FAIL_DUPLICATE_MARKET_STATE_EVENT",
                "validated event identities",
            )
        ordered = tuple(
            sorted(
                [
                    *barrier_events,
                    *(item.event for item in validated_events),
                ],
                key=state_aware_order_key,
            )
        )
        self.consumer.validate_ordered_sequence(ordered)

        store = MarketStateStore()
        sequence: list[dict[str, Any]] = []
        observations: list[dict[str, Any]] = []
        processed_barriers: set[tuple[str, dt.datetime]] = set()

        for event_index, event in enumerate(ordered):
            order_key = state_aware_order_key(event)
            if isinstance(event, ReplayBarEvent):
                processed_barriers.add(
                    (event.ticker.upper(), event.available_at)
                )
                sequence.append(
                    {
                        "available_at_utc": event.available_at,
                        "event_index": event_index,
                        "event_type": "BAR",
                        "execution_input": False,
                        "order_key": order_key,
                        "priority": 1,
                        "scientific_market_data_claim": False,
                        "ticker": event.ticker,
                    }
                )
                continue

            barrier_key = (
                event.ticker.upper(),
                event.state_available_at_utc,
            )
            if barrier_key not in processed_barriers:
                raise MarketStateContractError(
                    "FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY",
                    event.materialized_state_candidate_id,
                )
            validated = by_id[event.materialized_state_candidate_id]
            insert_sequence = store.insert(
                validated,
                event.state_available_at_utc,
            )
            visible = self.consumer.require_probe_visibility(
                store,
                event.materialized_state_candidate_id,
                event.state_available_at_utc,
            )
            if visible is not event:
                raise MarketStateContractError(
                    "FAIL_MARKET_STATE_OBSERVATION_BEFORE_STORE",
                    event.materialized_state_candidate_id,
                )
            observation = BoundedConsumerProbeObservation(
                probe_observation_id=(
                    f"bt-gate-014-v0-3-probe-{len(observations):02d}"
                ),
                event_sequence=event_index,
                observed_at_utc=event.state_available_at_utc,
                materialized_state_candidate_id=(
                    event.materialized_state_candidate_id
                ),
                state_output_fingerprint=event.state_output_fingerprint,
                typed_payload_field_count=17,
                replay_consumption_restriction_codes=event.replay_consumption_restriction_codes,
                store_insert_sequence=insert_sequence,
                visibility_status="VISIBLE",
            )
            observations.append(observation.to_dict())
            sequence.append(
                {
                    "available_at_utc": event.state_available_at_utc,
                    "event_index": event_index,
                    "event_type": event.event_type,
                    "order_key": order_key,
                    "priority": 2,
                    "store_insert_sequence": insert_sequence,
                    "ticker": event.ticker,
                }
            )

        if (
            len(sequence) != 4
            or [item["event_type"] for item in sequence]
            != [
                "BAR",
                "BoundedMarketStateAvailable",
                "BAR",
                "BoundedMarketStateAvailable",
            ]
            or store.count != 2
            or len(observations) != 2
        ):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY",
                "expected BAR -> STATE for both authorized timestamps",
            )
        return store, sequence, observations


class PhysicalRunnerV04:
    def __init__(
        self,
        row_reader: Callable[
            [Path, Mapping[str, Any]],
            list[Mapping[str, Any]],
        ]
        | None = None,
        *,
        spec: FrozenPhysicalRunSpec = PRODUCTION_SPEC,
    ) -> None:
        self.consumer = MarketStateConsumerV0_1()
        self._uses_default_reader = row_reader is None
        self._physical_open_callback = None
        self.row_reader = row_reader or self._read_parquet
        self.spec = spec

    @property
    def authorized_candidate_ids(self) -> tuple[str, ...]:
        return tuple(
            row["materialized_state_candidate_id"]
            for row in self.spec.authorized_rows
        )

    def _read_parquet(
        self,
        path: Path,
        schema_contract: Mapping[str, Any],
    ) -> list[Mapping[str, Any]]:
        import pyarrow.parquet as parquet

        parquet.ParquetFile(path)
        if self._physical_open_callback is not None:
            self._physical_open_callback()
        table = parquet.read_table(
            path,
            filters=[
                (
                    "materialized_state_candidate_id",
                    "in",
                    list(self.authorized_candidate_ids),
                )
            ],
        )
        observed_schema = [
            {
                "name": field.name,
                "nullable": field.nullable,
                "type": str(field.type),
            }
            for field in table.schema
        ]
        if observed_schema != schema_contract["columns"]:
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH",
                "actual Parquet schema differs from frozen 40-column schema",
            )
        return table.to_pylist()

    @staticmethod
    def _resolve_contained(
        root: Path,
        relative_path: str,
        *,
        code: str,
    ) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise MarketStateContractError(code, relative_path)
        resolved_root = root.resolve()
        resolved = (root / candidate).resolve()
        if resolved != resolved_root and resolved_root not in resolved.parents:
            raise MarketStateContractError(code, relative_path)
        return resolved

    def _validate_config(
        self,
        engine_root: Path,
        configuration: Mapping[str, Any],
        bindings: Mapping[str, str],
    ) -> None:
        if set(configuration) != CONFIG_FIELDS:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_CLOSED_CONFIGURATION_MISMATCH",
                "configuration fields",
            )
        expected_scalars = {
            "allowed_operation": "ONE_PHYSICAL_READ_AND_ONE_INTEGRATION_RUN",
            "authorization_id": AUTHORIZATION_ID,
            "authorization_version": "V0.4",
            "barrier_fixture_relative_path": (
                self.spec.barrier_fixture_relative_path
            ),
            "barrier_fixture_sha256": self.spec.barrier_fixture_sha256,
            "consumer_id": CONSUMER_ID,
            "contract_consumer_id": CONTRACT_CONSUMER_ID,
            "fills": 0,
            "maximum_physical_files": 1,
            "maximum_physical_rows": 2,
            "orders": 0,
            "pnl": False,
            "production": False,
            "run_directory": self.spec.run_directory,
            "run_id": self.spec.run_id,
            "strategy": "NONE",
        }
        for field, expected in expected_scalars.items():
            if configuration.get(field) != expected:
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_CLOSED_CONFIGURATION_MISMATCH",
                    field,
                )
        expected_mappings = {
            "adopted_evidence_relative_paths": dict(
                self.spec.adopted_evidence_relative_paths
            ),
            "adopted_evidence_sha256": dict(
                self.spec.adopted_evidence_sha256
            ),
            "binding_sha256": dict(bindings),
            "physical_input_sha256": dict(
                self.spec.physical_input_sha256
            ),
            "provider_relative_paths": dict(
                self.spec.provider_relative_paths
            ),
        }
        for field, expected in expected_mappings.items():
            if configuration.get(field) != expected:
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_CLOSED_CONFIGURATION_MISMATCH",
                    field,
                )
        if configuration.get("authorized_rows") != [
            dict(row) for row in self.spec.authorized_rows
        ]:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_CLOSED_CONFIGURATION_MISMATCH",
                "authorized_rows",
            )
        barrier = self._resolve_contained(
            engine_root,
            self.spec.barrier_fixture_relative_path,
            code="FAIL_BT_GATE_014_SCOPE_LEAKAGE",
        )
        if (
            not barrier.is_file()
            or sha256_file(barrier) != self.spec.barrier_fixture_sha256
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH",
                self.spec.barrier_fixture_relative_path,
            )

    def _validate_adopted_evidence(self, engine_root: Path) -> None:
        if set(self.spec.adopted_evidence_relative_paths) != set(
            self.spec.adopted_evidence_sha256
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_ADOPTED_EVIDENCE_INVENTORY",
                "adopted evidence keys",
            )
        for name, relative_path in (
            self.spec.adopted_evidence_relative_paths.items()
        ):
            path = self._resolve_contained(
                engine_root,
                relative_path,
                code="FAIL_BT_GATE_014_SCOPE_LEAKAGE",
            )
            if (
                not path.is_file()
                or sha256_file(path)
                != self.spec.adopted_evidence_sha256[name]
            ):
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_ADOPTED_EVIDENCE_HASH_MISMATCH",
                    name,
                )

    def validate_preconsumption(
        self,
        tsis_root: Path,
        configuration: Mapping[str, Any],
        bindings: Mapping[str, str],
    ) -> None:
        engine_root = tsis_root / "02_TSIS_BACKTEST_ENGINE"
        self._validate_config(engine_root, configuration, bindings)
        self._validate_adopted_evidence(engine_root)
        if (
            set(self.spec.provider_relative_paths)
            != set(PHYSICAL_INPUT_NAMES)
            or set(self.spec.physical_input_sha256)
            != set(PHYSICAL_INPUT_NAMES)
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_INPUT_INVENTORY",
                "exactly nine physical inputs required",
            )
        for relative_path in self.spec.provider_relative_paths.values():
            self._resolve_contained(
                tsis_root,
                relative_path,
                code="FAIL_BT_GATE_014_SCOPE_LEAKAGE",
            )

    def execute(
        self,
        tsis_root: Path | str,
        configuration: Mapping[str, Any],
        authorization: AuthorizationV04,
        bindings: Mapping[str, str],
    ) -> dict[str, Any]:
        tsis_root = Path(tsis_root)
        run_directory = (
            tsis_root
            / "02_TSIS_BACKTEST_ENGINE"
            / self.spec.run_directory
        )
        phase = "PRECONSUMPTION_VALIDATION"
        try:
            self.validate_preconsumption(
                tsis_root,
                configuration,
                bindings,
            )
            phase = "AUTHORIZATION_CONSUMPTION"
            authorization.consume(bindings, run_directory)
            phase = "PHYSICAL_INTEGRATION"
            final_manifest = self._after_consumption(
                tsis_root,
                configuration,
                run_directory,
            )
            phase = "SUCCESS_GUARD_FINALIZATION"
            final_manifest_sha256 = sha256_file(
                run_directory / "final_manifest.json"
            )
            authorization.mark_success_guard(
                run_directory,
                final_manifest_sha256,
            )
            return final_manifest
        except Exception as exc:
            authorization.record_failure(
                run_directory,
                exc,
                phase=phase,
            )
            raise

    def _resolve_and_hash_inputs(
        self,
        tsis_root: Path,
    ) -> tuple[dict[str, Path], dict[str, dict[str, Any]]]:
        paths: dict[str, Path] = {}
        identities: dict[str, dict[str, Any]] = {}
        for name in PHYSICAL_INPUT_NAMES:
            relative_path = self.spec.provider_relative_paths[name]
            path = self._resolve_contained(
                tsis_root,
                relative_path,
                code="FAIL_BT_GATE_014_SCOPE_LEAKAGE",
            )
            if not path.is_file():
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_PHYSICAL_INPUT_MISSING",
                    name,
                )
            before = sha256_file(path)
            if before != self.spec.physical_input_sha256[name]:
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_PHYSICAL_INPUT_HASH_MISMATCH",
                    name,
                )
            paths[name] = path
            identities[name] = {
                "relative_path": relative_path,
                "sha256_before": before,
                "size_bytes": path.stat().st_size,
            }
        return paths, identities

    def _load_barriers(self, engine_root: Path) -> list[ReplayBarEvent]:
        path = engine_root / self.spec.barrier_fixture_relative_path
        fixture = _load_json(path)
        if (
            not isinstance(fixture, dict)
            or set(fixture)
            != {
                "execution_input",
                "fixture_id",
                "physical_source_rows",
                "price_use",
                "records",
                "scientific_market_data_claim",
            }
            or fixture["fixture_id"]
            != "BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_4"
            or fixture["physical_source_rows"] != 0
            or fixture["execution_input"] is not False
            or fixture["price_use"] != "PROHIBITED"
            or fixture["scientific_market_data_claim"] is not False
            or not isinstance(fixture["records"], list)
            or len(fixture["records"]) != 2
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_CAUSAL_BARRIER_FIXTURE",
                "fixture boundary",
            )
        expected_by_available = {
            row["state_available_at_utc"]: row
            for row in self.spec.authorized_rows
        }
        bars: list[ReplayBarEvent] = []
        for record in fixture["records"]:
            if (
                set(record)
                != {
                    "available_at",
                    "barrier_id",
                    "close",
                    "high",
                    "low",
                    "open",
                    "session_label",
                    "ticker",
                    "ts_end",
                    "ts_start",
                    "volume",
                }
                or record["available_at"] not in expected_by_available
                or record["ticker"]
                != expected_by_available[record["available_at"]]["ticker"]
                or record["session_label"] != "REGULAR"
                or record["ts_end"] != record["available_at"]
            ):
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_CAUSAL_BARRIER_FIXTURE",
                    str(record.get("barrier_id")),
                )
            bar = MarketDataBar1m(
                ticker=record["ticker"],
                ts_start=_utc(record["ts_start"]),
                ts_end=_utc(record["ts_end"]),
                available_at=_utc(record["available_at"]),
                session_label=record["session_label"],
                open=float(record["open"]),
                high=float(record["high"]),
                low=float(record["low"]),
                close=float(record["close"]),
                volume=int(record["volume"]),
                price_view=(
                    "synthetic_causal_barrier_not_execution_input"
                ),
            )
            bars.append(
                ReplayBarEvent(
                    event_type="BAR",
                    ticker=bar.ticker,
                    available_at=bar.available_at,
                    bar=bar,
                    physical_lineage={
                        "barrier_id": record["barrier_id"],
                        "execution_input": False,
                        "physical_source_rows": 0,
                        "scientific_market_data_claim": False,
                    },
                )
            )
        return bars

    def _validate_row_identities(
        self,
        rows: Sequence[Mapping[str, Any]],
        sidecars: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        expected = {
            row["materialized_state_candidate_id"]: dict(row)
            for row in self.spec.authorized_rows
        }
        if len(expected) != 2:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY",
                "authorization identity inventory",
            )
        row_by_id: dict[str, Mapping[str, Any]] = {}
        for row in rows:
            candidate_id = row.get("materialized_state_candidate_id")
            if not isinstance(candidate_id, str) or candidate_id in row_by_id:
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY",
                    "duplicate or missing row id",
                )
            row_by_id[candidate_id] = row
        sidecar_by_id: dict[str, Mapping[str, Any]] = {}
        for sidecar in sidecars:
            candidate_id = sidecar.get("materialized_state_candidate_id")
            if (
                not isinstance(candidate_id, str)
                or candidate_id in sidecar_by_id
            ):
                raise MarketStateContractError(
                    "FAIL_MARKET_STATE_SIDECAR_DUPLICATE",
                    str(candidate_id),
                )
            sidecar_by_id[candidate_id] = sidecar
        if set(row_by_id) != set(expected) or set(sidecar_by_id) != set(
            expected
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY",
                "authorized identity set",
            )

        report: list[dict[str, Any]] = []
        for candidate_id, identity in expected.items():
            row = row_by_id[candidate_id]
            sidecar = sidecar_by_id[candidate_id]
            comparisons = {
                "context_id": identity["context_id"],
                "decision_timestamp_utc": identity[
                    "decision_timestamp_utc"
                ],
                "instrument_id": identity["instrument_id"],
                "materialized_state_candidate_id": candidate_id,
                "session_date": identity["session_date"],
                "source_candidate_record_id": identity[
                    "source_candidate_record_id"
                ],
                "state_output_fingerprint": identity[
                    "state_output_fingerprint"
                ],
                "ticker": identity["ticker"],
            }
            for field, expected_value in comparisons.items():
                if (
                    row.get(field) != expected_value
                    or sidecar.get(field) != expected_value
                ):
                    raise MarketStateContractError(
                        "FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY",
                        f"{candidate_id}:{field}",
                    )
            if (
                sidecar.get("state_available_at_utc")
                != identity["state_available_at_utc"]
            ):
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY",
                    f"{candidate_id}:state_available_at_utc",
                )
            report.append(
                {
                    **identity,
                    "identity_match": True,
                    "sidecar_match": True,
                }
            )
        return report

    def _after_consumption(
        self,
        tsis_root: Path,
        configuration: Mapping[str, Any],
        run_directory: Path,
    ) -> dict[str, Any]:
        receipt_path = (
            run_directory / "authorization_consumption_receipt.json"
        )
        if not receipt_path.is_file():
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_RECEIPT_MISSING",
                str(receipt_path),
            )
        receipt = _load_json(receipt_path)
        if (
            receipt.get("authorization_id") != AUTHORIZATION_ID
            or receipt.get("physical_access_started") is not False
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_RECEIPT_MISMATCH",
                str(receipt_path),
            )

        paths, identities = self._resolve_and_hash_inputs(tsis_root)
        parsed_inputs: dict[str, Any] = {}
        for name, path in paths.items():
            if name != "candidate_parquet":
                parsed_inputs[name] = _load_json(path)

        schema = parsed_inputs["physical_schema_contract"]
        self.consumer.validate_schema_contract(schema)
        progress_path = run_directory / "physical_progress.json"
        progress = {
            "physical_access_attempted": True,
            "physical_access_started": False,
            "physical_data_files_opened": 0,
            "physical_state_rows_read": 0,
            "validation_phase_reached": "CANDIDATE_PARQUET_OPEN_ATTEMPT",
        }
        _write_json(progress_path, progress)

        def confirm_open() -> None:
            progress.update({
                "physical_access_started": True,
                "physical_data_files_opened": 1,
                "validation_phase_reached": "CANDIDATE_PARQUET_OPEN_CONFIRMED",
            })
            _write_json(progress_path, progress)

        self._physical_open_callback = confirm_open
        try:
            rows = [
                _normalize_arrow_row(row)
                for row in self.row_reader(
                    paths["candidate_parquet"],
                    schema,
                )
            ]
        finally:
            self._physical_open_callback = None
        if not progress["physical_access_started"]:
            confirm_open()
        progress.update({
            "physical_state_rows_read": len(rows),
            "validation_phase_reached": "PHYSICAL_ROWS_LOADED",
        })
        _write_json(progress_path, progress)
        if len(rows) != 2:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_PHYSICAL_ROW_CARDINALITY",
                str(len(rows)),
            )
        if any(
            set(row) != set(PHYSICAL_COLUMNS)
            or len(row) != len(PHYSICAL_COLUMNS)
            for row in rows
        ):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH",
                "physical row shape",
            )

        sidecar_document = parsed_inputs["sidecar_manifest"]
        sidecar_records = sidecar_document.get("records")
        if not isinstance(sidecar_records, list):
            raise MarketStateContractError(
                "FAIL_MARKET_STATE_SIDECAR_SCHEMA_MISMATCH",
                "sidecar records",
            )
        authorized_ids = set(self.authorized_candidate_ids)
        sidecars = []
        for raw_sidecar in sidecar_records:
            if (
                isinstance(raw_sidecar, dict)
                and raw_sidecar.get("materialized_state_candidate_id")
                in authorized_ids
            ):
                sidecars.append(
                    {
                        **raw_sidecar,
                        "sidecar_id": sidecar_document["sidecar_id"],
                        "sidecar_schema_id": sidecar_document[
                            "sidecar_schema_id"
                        ],
                    }
                )
        identity_report = self._validate_row_identities(rows, sidecars)

        row_by_id = {
            row["materialized_state_candidate_id"]: row for row in rows
        }
        sidecar_by_id = {
            row["materialized_state_candidate_id"]: row
            for row in sidecars
        }
        ordered_rows = [
            row_by_id[candidate_id]
            for candidate_id in self.authorized_candidate_ids
        ]
        ordered_sidecars = [
            sidecar_by_id[candidate_id]
            for candidate_id in self.authorized_candidate_ids
        ]
        authority = {
            **FROZEN_PROVIDER_AUTHORITY,
            "candidate_dataset_fingerprint": sidecar_document[
                "candidate_dataset_fingerprint"
            ],
            "candidate_dataset_id": sidecar_document[
                "candidate_dataset_id"
            ],
        }
        progress["restriction_diagnostics"] = {
            "expected_restrictions": list(EXPECTED_RESTRICTIONS),
            "rows": [json.loads(row["restriction_codes_json"]) for row in ordered_rows],
            "sidecars": [list(item["restriction_codes"]) for item in ordered_sidecars],
            "components": [
                [list(component["restriction_codes"]) for component in item["component_availability_evidence"]]
                for item in ordered_sidecars
            ],
        }
        progress["validation_phase_reached"] = "RESTRICTION_VALIDATION"
        _write_json(progress_path, progress)
        validated = self.consumer.validate_join_and_seal(
            ordered_rows,
            ordered_sidecars,
            authority,
            identities["sidecar_manifest"]["sha256_before"],
        )
        events = [item.event for item in validated]
        if (
            tuple(
                event.materialized_state_candidate_id for event in events
            )
            != self.authorized_candidate_ids
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY",
                "validated event order/identity",
            )

        barriers = self._load_barriers(
            tsis_root / "02_TSIS_BACKTEST_ENGINE"
        )
        event_loop = BoundedPhysicalMarketStateEventLoopV04(
            self.consumer
        )
        store, sequence, observations = event_loop.run(
            validated,
            barriers,
        )

        provider_modification = False
        for name, path in paths.items():
            after = sha256_file(path)
            identities[name]["sha256_after"] = after
            identities[name]["hash_before_after_match"] = (
                after == identities[name]["sha256_before"]
            )
            if not identities[name]["hash_before_after_match"]:
                provider_modification = True
        if provider_modification:
            raise MarketStateContractError(
                "FAIL_SOURCE_MUTATION",
                "provider input changed during run",
            )

        event_dicts = [event.to_dict() for event in events]
        store_trace = to_market_state_jsonable(store.trace)
        scientific_identity = {
            "authorized_candidate_ids": list(
                self.authorized_candidate_ids
            ),
            "candidate_dataset_fingerprint": events[
                0
            ].candidate_dataset_fingerprint,
            "candidate_dataset_id": events[0].candidate_dataset_id,
            "event_content_sha256": [
                canonical_hash(event) for event in event_dicts
            ],
            "profile_id": events[0].profile_id,
            "state_output_fingerprints": [
                event.state_output_fingerprint for event in events
            ],
            "state_schema_version": events[0].state_schema_version,
        }
        deterministic_source = {
            "bounded_consumer_probe_observations": observations,
            "bounded_market_state_events": event_dicts,
            "market_state_store_trace": store_trace,
            "state_aware_event_sequence": sequence,
        }
        scientific_identity_sha256 = canonical_hash(scientific_identity)
        deterministic_output_hash = canonical_hash(
            deterministic_source
        )

        artifacts = {
            "resolved_physical_input_manifest.json": {
                "adopted_evidence_sha256": dict(
                    self.spec.adopted_evidence_sha256
                ),
                "inputs": identities,
                "physical_input_count": 9,
                "provider_modification": False,
            },
            "physical_schema_validation_report.json": {
                "column_count": 40,
                "column_names": list(PHYSICAL_COLUMNS),
                "expected_types": EXPECTED_TYPES,
                "nullable_columns": 0,
                "status": "PASS",
            },
            "physical_row_identity_report.json": {
                "authorized_row_count": 2,
                "duplicate_rows": 0,
                "identity_fingerprint_mismatches": 0,
                "missing_authorized_rows": 0,
                "records": identity_report,
                "status": "PASS",
                "unlisted_rows_delivered": 0,
            },
            "bounded_market_state_events.json": event_dicts,
            "state_aware_event_sequence.json": sequence,
            "market_state_store_trace.json": store_trace,
            "bounded_consumer_probe_observations.json": observations,
            "boundary_preservation_report.json": {
                "cash_mutations": 0,
                "downstream": False,
                "equity_mutations": 0,
                "event_state": "NOT_OPEN",
                "fills": 0,
                "market_state_as_execution_price": False,
                "market_state_as_market_data": False,
                "market_state_as_valuation_price": False,
                "orders": 0,
                "pnl_calculated": False,
                "positions_mutated": 0,
                "production": False,
                "provider_modification": False,
                "signals": 0,
                "state_replay_feed": "NOT_AUTHORIZED",
                "status": "PASS",
                "strategy_decisions": 0,
            },
            "deterministic_reproduction_source.json": {
                "determinism_policy": (
                    "ONE_PHYSICAL_RUN_THEN_NON_PHYSICAL_REPRODUCTION_"
                    "FROM_IMMUTABLE_RUN_EVIDENCE"
                ),
                "deterministic_output_hash": deterministic_output_hash,
                "physical_rerun_authorized": False,
                "scientific_identity": scientific_identity,
                "scientific_identity_sha256": (
                    scientific_identity_sha256
                ),
                **deterministic_source,
            },
            "physical_consumer_validation_report.json": {
                "bounded_consumer_observations": 2,
                "delivery_before_available_at": 0,
                "event_loop_id": (
                    "BOUNDED_PHYSICAL_MARKET_STATE_EVENT_LOOP_V0_4"
                ),
                "identity_fingerprint_mismatches": 0,
                "market_state_events_emitted": 2,
                "market_state_store_inserts": 2,
                "physical_data_files_opened": 1,
                "physical_state_rows_read": 2,
                "provider_modification": False,
                "status": "PASS",
                "typed_scientific_values_per_event": 17,
            },
        }
        for name, data in artifacts.items():
            _write_json(run_directory / name, data)

        output_hashes = {
            name: sha256_file(run_directory / name)
            for name in SUCCESS_ARTIFACTS_BEFORE_FINAL
        }
        final_manifest = {
            "BT_GATE_014_CLOSED_PASS": "NOT_AUTHORIZED",
            "authorization_consumed": True,
            "authorization_id": AUTHORIZATION_ID,
            "authorization_version": "V0.4",
            "bounded_consumer_observations": 2,
            "delivery_before_available_at": 0,
            "deterministic_output_hash": deterministic_output_hash,
            "external_acceptance_review": "PENDING",
            "failure_manifest_required_after_consumption": True,
            "fills": 0,
            "gate_id": "BT-GATE-014",
            "identity_fingerprint_mismatches": 0,
            "market_state_events_emitted": 2,
            "market_state_store_inserts": 2,
            "orders": 0,
            "output_artifact_hashes": output_hashes,
            "physical_data_files_opened": 1,
            "physical_state_rows_read": 2,
            "pnl_calculated": False,
            "provider_modification": False,
            "run_id": configuration["run_id"],
            "scientific_identity_sha256": scientific_identity_sha256,
            "strategy_decisions": 0,
            "typed_scientific_values_per_event": 17,
            "validation_status": "PASS",
        }
        _write_json(
            run_directory / "final_manifest.json",
            final_manifest,
        )
        return final_manifest

