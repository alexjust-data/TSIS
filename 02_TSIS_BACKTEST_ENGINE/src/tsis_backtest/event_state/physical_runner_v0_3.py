"""Bounded physical runner for the BT-GATE-015 V0.3 single-use probe."""
from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.replay.contracts import ReplayBarEvent
from tsis_backtest.replay.state_ordering import state_aware_order_key

from .consumer import EventStateConsumerV0_1, canonical_hash, utc
from .contracts import (
    BoundedEventStateAvailable,
    EventStateContractError,
    to_event_state_jsonable,
)
from .physical_authorization_v0_3 import (
    AUTHORIZATION_ID,
    RUN_ID,
    AuthorizationV03,
    atomic_write_json,
    sha256_file,
    strict_load_json,
)
from .physical_consumer_v0_3 import PhysicalEventStateConsumerV03
from .store import EventStateStore

CONFIG_FIELDS = {
    "authorization_id",
    "barrier_fixture_relative_path",
    "boundaries",
    "contract_id",
    "event_state_scope",
    "expected_outputs",
    "gate_id",
    "governed_inputs",
    "physical_command_status",
    "run_directory_relative_path",
    "run_id",
    "specification_relative_path",
    "specification_sha256",
}


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        raise EventStateContractError(
            "FAIL_EVENT_STATE_SCHEMA_MISMATCH", label
        ) from exc
    if not isinstance(value, dict):
        raise EventStateContractError(
            "FAIL_EVENT_STATE_SCHEMA_MISMATCH", f"{label}: object required"
        )
    return value


def _read_jsonl(raw: bytes) -> list[tuple[dict[str, Any], str]]:
    rows: list[tuple[dict[str, Any], str]] = []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EventStateContractError(
            "FAIL_EVENT_STATE_SCHEMA_MISMATCH", "candidate JSONL UTF-8"
        ) from exc
    for ordinal, line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        rows.append(
            (
                _strict_json_bytes(line.encode("utf-8"), f"candidate row {ordinal}"),
                _sha256(line.encode("utf-8")),
            )
        )
    return rows


def _validate_provider_evidence_zip(path: Path, label: str) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_PROVIDER_EVIDENCE_ZIP_INTEGRITY",
                    f"{label}: duplicate member",
                )
            for info in infos:
                member = PurePosixPath(info.filename.replace("\\", "/"))
                mode = info.external_attr >> 16
                if (
                    member.is_absolute()
                    or ".." in member.parts
                    or stat.S_ISLNK(mode)
                ):
                    raise EventStateContractError(
                        "FAIL_BT_GATE_015_PROVIDER_EVIDENCE_ZIP_INTEGRITY",
                        f"{label}: unsafe member {info.filename}",
                    )
                if member.suffix.lower() in {".jsonl", ".parquet"}:
                    raise EventStateContractError(
                        "FAIL_BT_GATE_015_PROVIDER_EVIDENCE_SCOPE_LEAKAGE",
                        f"{label}: physical member {info.filename}",
                    )
            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_PROVIDER_EVIDENCE_ZIP_INTEGRITY",
                    f"{label}: CRC failure {corrupt_member}",
                )
    except EventStateContractError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise EventStateContractError(
            "FAIL_BT_GATE_015_PROVIDER_EVIDENCE_ZIP_INTEGRITY", label
        ) from exc
    return {
        "entry_count": len(infos),
        "physical_members": 0,
        "zip_integrity": "PASS",
    }


@dataclass(frozen=True)
class PreconsumptionEvidence:
    specification: Mapping[str, Any]
    configuration: Mapping[str, Any]
    authorization_state: Mapping[str, Any]
    metadata_documents: Mapping[str, Mapping[str, Any]]
    input_identities: Mapping[str, Mapping[str, Any]]


class PhysicalRunnerV03:
    def __init__(self, byte_reader: Callable[[Path], bytes] | None = None) -> None:
        self.byte_reader = byte_reader or (lambda path: path.read_bytes())

    def validate_preconsumption(
        self,
        tsis_root: Path,
        configuration_path: Path,
        authorization: AuthorizationV03,
    ) -> PreconsumptionEvidence:
        tsis_root = Path(tsis_root).resolve()
        configuration_path = Path(configuration_path).resolve()
        configuration = strict_load_json(configuration_path)
        if set(configuration) != CONFIG_FIELDS:
            raise EventStateContractError(
                "FAIL_BT_GATE_015_CLOSED_CONFIGURATION_MISMATCH",
                f"fields={sorted(configuration)}",
            )
        state = authorization.validate_intact()
        specification = strict_load_json(authorization.spec_path)
        expected = {
            "authorization_id": AUTHORIZATION_ID,
            "run_id": RUN_ID,
            "gate_id": "BT-GATE-015",
            "contract_id": specification["contract_id"],
            "event_state_scope": specification["event_state_scope"],
            "boundaries": specification["boundaries"],
            "expected_outputs": specification["expected_outputs"],
            "governed_inputs": specification["governed_inputs"],
            "specification_sha256": sha256_file(authorization.spec_path),
            "physical_command_status": "NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW",
        }
        if any(configuration.get(key) != value for key, value in expected.items()):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_CLOSED_CONFIGURATION_MISMATCH", "semantic fields"
            )
        if configuration["specification_relative_path"] != str(
            authorization.spec_path.resolve().relative_to(tsis_root)
        ).replace("\\", "/"):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_CLOSED_CONFIGURATION_MISMATCH",
                "specification_relative_path",
            )
        if state.get("configuration_sha256") != sha256_file(configuration_path):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH",
                "configuration_sha256",
            )
        binding_paths = specification["executable_binding_paths"]
        binding_hashes = state["binding_sha256"]
        if (
            specification["executable_binding_count"] != len(binding_paths)
            or set(binding_hashes) != set(binding_paths)
        ):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH",
                "executable binding set",
            )
        for relative in binding_paths:
            expected_hash = binding_hashes[relative]
            path = tsis_root / relative
            if not path.is_file() or sha256_file(path) != expected_hash:
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH", relative
                )
        identities: dict[str, dict[str, Any]] = {}
        documents: dict[str, Mapping[str, Any]] = {}
        inputs = specification["governed_inputs"]
        if len(inputs) != specification["governed_input_count"]:
            raise EventStateContractError(
                "FAIL_BT_GATE_015_CLOSED_CONFIGURATION_MISMATCH",
                "governed input count",
            )
        for name, binding in inputs.items():
            path = tsis_root / binding["relative_path"]
            if not path.is_file():
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_PHYSICAL_INPUT_MISSING", name
                )
            size = path.stat().st_size
            if "size_bytes" in binding and size != binding["size_bytes"]:
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_PHYSICAL_INPUT_SIZE_MISMATCH", name
                )
            if name == "candidate_jsonl":
                identities[name] = {
                    "relative_path": binding["relative_path"],
                    "sha256_expected": binding["sha256"],
                    "size_bytes": size,
                    "content_opened_preconsumption": False,
                }
                continue
            raw = path.read_bytes()
            actual = _sha256(raw)
            if actual != binding["sha256"]:
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_METADATA_HASH_MISMATCH", name
                )
            identities[name] = {
                "relative_path": binding["relative_path"],
                "sha256_before": actual,
                "size_bytes": len(raw),
                "content_opened_preconsumption": True,
            }
            if name in {"initial_provider_handoff", "provider_completion_handoff"}:
                identities[name].update(_validate_provider_evidence_zip(path, name))
            if path.suffix.lower() == ".json":
                documents[name] = _strict_json_bytes(raw, name)
        event_document = documents["replay_availability_sidecar_manifest"]
        event_records = EventStateConsumerV0_1().validate_sidecar_document(
            event_document
        )
        selection = specification["selection"]
        if (
            len(event_records) != 1
            or event_records[0]["event_state_record_id"]
            != selection["event_state_record_id"]
            or event_records[0]["event_state_record_fingerprint"]
            != selection["event_state_record_fingerprint"]
        ):
            raise EventStateContractError(
                "FAIL_EVENT_STATE_SIDECAR_BIJECTION", "frozen selection"
            )
        if specification["semantic_correction"]["status"] != (
            "TARGETED_CORRECTION_REQUIRED_BEFORE_PREEXECUTION_APPROVAL"
        ):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_CLOSED_CONFIGURATION_MISMATCH",
                "physical fingerprint semantics",
            )
        return PreconsumptionEvidence(
            specification=specification,
            configuration=configuration,
            authorization_state=state,
            metadata_documents=documents,
            input_identities=identities,
        )

    def execute(
        self,
        tsis_root: Path,
        configuration_path: Path,
        authorization: AuthorizationV03,
    ) -> dict[str, Any]:
        evidence = self.validate_preconsumption(
            tsis_root, configuration_path, authorization
        )
        specification = evidence.specification
        configuration = evidence.configuration
        tsis_root = Path(tsis_root).resolve()
        run_directory = tsis_root / configuration["run_directory_relative_path"]
        authorization.consume(run_directory)
        progress = {
            "authorization_consumed": True,
            "physical_access_attempted": False,
            "physical_access_started": False,
            "physical_data_files_opened": 0,
            "physical_state_records_scanned": 0,
            "physical_state_rows_selected": 0,
            "market_state_dependency_events": 0,
            "event_state_events_emitted": 0,
            "event_state_store_inserts": 0,
            "bounded_probe_observations": 0,
            "validation_phase_reached": "AUTHORIZATION_CONSUMED",
        }
        diagnostics: dict[str, Any] = {}
        try:
            atomic_write_json(
                run_directory / "pre_run_manifest.json",
                {
                    "gate_id": "BT-GATE-015",
                    "run_id": RUN_ID,
                    "authorization_id": AUTHORIZATION_ID,
                    "authorization_consumed": True,
                    "event_state_physical_read": "AUTHORIZED_SINGLE_USE_IN_PROGRESS",
                    "market_state_physical_read": "NOT_AUTHORIZED_NOT_EXECUTED",
                    "scope": specification["event_state_scope"],
                },
            )
            candidate_binding = specification["governed_inputs"]["candidate_jsonl"]
            candidate_path = tsis_root / candidate_binding["relative_path"]
            progress["physical_access_attempted"] = True
            progress["validation_phase_reached"] = "CANDIDATE_JSONL_READ_ATTEMPT"
            AuthorizationV03.write_progress(run_directory, progress)
            candidate_raw = self.byte_reader(candidate_path)
            progress["physical_access_started"] = True
            progress["physical_data_files_opened"] = 1
            progress["validation_phase_reached"] = "CANDIDATE_JSONL_OPENED"
            AuthorizationV03.write_progress(run_directory, progress)
            candidate_hash = _sha256(candidate_raw)
            if candidate_hash != candidate_binding["sha256"]:
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_PHYSICAL_INPUT_HASH_MISMATCH",
                    "candidate_jsonl",
                )
            rows = _read_jsonl(candidate_raw)
            progress["physical_state_records_scanned"] = len(rows)
            progress["validation_phase_reached"] = "CANDIDATE_ROWS_MATERIALIZED"
            AuthorizationV03.write_progress(run_directory, progress)
            if len(rows) != specification["selection"]["candidate_records_scanned"]:
                raise EventStateContractError(
                    "FAIL_EVENT_STATE_SCOPE_LEAKAGE", f"scanned={len(rows)}"
                )
            selected = [
                item
                for item in rows
                if item[0].get("event_state_record_id")
                == specification["selection"]["event_state_record_id"]
                and item[0].get("event_state_record_fingerprint")
                == specification["selection"]["event_state_record_fingerprint"]
            ]
            if len(selected) != 1:
                raise EventStateContractError(
                    "FAIL_EVENT_STATE_SCOPE_LEAKAGE",
                    f"selected={len(selected)}",
                )
            progress["physical_state_rows_selected"] = 1
            row, raw_line_hash = selected[0]
            event_document = evidence.metadata_documents[
                "replay_availability_sidecar_manifest"
            ]
            event_sidecar = event_document["records"][0]
            payload, _ = __import__(
                "tsis_backtest.event_state.consumer", fromlist=["_payload"]
            )._payload(row["source_market_state_value_snapshot_json"])
            physical_consumer = PhysicalEventStateConsumerV03(
                specification["selection"]["event_state_record_id"],
                specification["selection"]["event_state_record_fingerprint"],
            )
            market_document = evidence.metadata_documents[
                "market_state_replay_sidecar"
            ]
            market_state = physical_consumer.build_market_state_dependency(
                market_document,
                event_sidecar,
                payload,
                specification["governed_inputs"]["market_state_replay_sidecar"][
                    "sha256"
                ],
            )
            progress["market_state_dependency_events"] = 1
            progress["validation_phase_reached"] = "PHYSICAL_ROW_VALIDATION"
            AuthorizationV03.write_progress(run_directory, progress)
            validated = physical_consumer.validate_and_seal(
                row,
                event_sidecar,
                specification["governed_inputs"][
                    "replay_availability_sidecar_manifest"
                ]["sha256"],
                market_state,
                candidate_hash,
                raw_line_hash,
            )
            progress["event_state_events_emitted"] = 1
            barrier_path = tsis_root / configuration["barrier_fixture_relative_path"]
            barrier = strict_load_json(barrier_path)["events"][0]
            bar_value = MarketDataBar1m(
                ticker=barrier["ticker"],
                ts_start=utc(barrier["ts_start"]),
                ts_end=utc(barrier["ts_end"]),
                available_at=utc(barrier["available_at"]),
                session_label=barrier["session_label"],
                open=float(barrier["open"]),
                high=float(barrier["high"]),
                low=float(barrier["low"]),
                close=float(barrier["close"]),
                volume=int(barrier["volume"]),
                price_view=barrier["price_view"],
            )
            bar = ReplayBarEvent(
                event_type="BAR",
                ticker=barrier["ticker"],
                available_at=bar_value.available_at,
                bar=bar_value,
                physical_lineage={"fixture_role": "ORDERING_ONLY_NO_EXECUTION_NO_VALUATION"},
            )
            ordered = tuple(
                sorted(
                    (bar, market_state, validated.event), key=state_aware_order_key
                )
            )
            if [item.event_type for item in ordered] != [
                "BAR",
                "BoundedMarketStateAvailable",
                "BoundedEventStateAvailable",
            ]:
                raise EventStateContractError(
                    "FAIL_EVENT_STATE_EQUAL_TIMESTAMP_PRIORITY", "physical sequence"
                )
            store = EventStateStore()
            sequence = []
            observations = []
            for index, item in enumerate(ordered):
                sequence.append(
                    {
                        "index": index,
                        "event_type": item.event_type,
                        "order_key": state_aware_order_key(item),
                    }
                )
                if isinstance(item, BoundedEventStateAvailable):
                    insert_sequence = store.insert(
                        validated, item.event_state_available_at_utc
                    )
                    progress["event_state_store_inserts"] = 1
                    visible = store.get_exact(
                        item.event_state_record_id,
                        item.event_state_available_at_utc,
                    )
                    if visible is None:
                        raise EventStateContractError(
                            "FAIL_EVENT_STATE_OBSERVATION_BEFORE_STORE",
                            item.event_state_record_id,
                        )
                    observations.append(
                        {
                            "event_state_record_id": item.event_state_record_id,
                            "observed_at_utc": item.event_state_available_at_utc,
                            "store_insert_sequence": insert_sequence,
                            "typed_payload_field_count": 17,
                        }
                    )
                    progress["bounded_probe_observations"] = 1
            progress["validation_phase_reached"] = "EVENT_LOOP_COMPLETE"
            AuthorizationV03.write_progress(run_directory, progress)
            candidate_after = self.byte_reader(candidate_path)
            if _sha256(candidate_after) != candidate_hash:
                raise EventStateContractError(
                    "FAIL_SOURCE_MUTATION", "candidate_jsonl"
                )
            input_identities = {
                name: dict(identity)
                for name, identity in evidence.input_identities.items()
            }
            input_identities["candidate_jsonl"].update(
                {
                    "sha256_before": candidate_hash,
                    "sha256_after": _sha256(candidate_after),
                    "content_opened_preconsumption": False,
                }
            )
            for name, binding in specification["governed_inputs"].items():
                if name == "candidate_jsonl":
                    continue
                path = tsis_root / binding["relative_path"]
                after = sha256_file(path)
                if after != input_identities[name]["sha256_before"]:
                    raise EventStateContractError("FAIL_SOURCE_MUTATION", name)
                input_identities[name]["sha256_after"] = after
            semantic = to_event_state_jsonable(
                {
                    "event_sequence": sequence,
                    "market_state_dependency": market_state.to_dict(),
                    "event_state": validated.event.to_dict(),
                    "store_trace": store.trace,
                    "observations": observations,
                }
            )
            deterministic_hash = canonical_hash(semantic)
            artifacts = {
                "resolved_input_manifest.json": {
                    "status": "PASS",
                    "governed_input_count": len(input_identities),
                    "inputs": input_identities,
                },
                "physical_selection_report.json": {
                    "status": "PASS",
                    "records_scanned": len(rows),
                    "records_selected": 1,
                    "selection": specification["selection"],
                },
                "physical_identity_and_fingerprint_report.json": {
                    "status": "PASS",
                    "event_state_record_id": row["event_state_record_id"],
                    "event_state_record_fingerprint": row[
                        "event_state_record_fingerprint"
                    ],
                    "state_output_fingerprint": row["state_output_fingerprint"],
                    "state_output_fingerprint_semantics": "MARKET_STATE_DEPENDENCY_FINGERPRINT",
                    "raw_jsonl_line_sha256": raw_line_hash,
                },
                "state_aware_event_sequence.json": sequence,
                "bounded_market_state_dependency.json": market_state.to_dict(),
                "bounded_event_state_event.json": validated.event.to_dict(),
                "event_state_store_trace.json": to_event_state_jsonable(store.trace),
                "bounded_probe_observations.json": observations,
                "boundary_preservation_report.json": {
                    "status": "PASS",
                    "event_state_physical_files": 1,
                    "event_state_records_scanned": len(rows),
                    "event_state_rows_selected": 1,
                    "market_state_physical_read": False,
                    "provider_modification": False,
                    "strategy": False,
                    "orders": 0,
                    "fills": 0,
                    "pnl": False,
                    "StateReplayFeed": "NOT_AUTHORIZED",
                },
                "determinism_report.json": {
                    "status": "PASS",
                    "deterministic_output_hash": deterministic_hash,
                },
            }
            artifact_hashes = {}
            for name, value in artifacts.items():
                atomic_write_json(run_directory / name, value)
                artifact_hashes[name] = sha256_file(run_directory / name)
            final = {
                "gate_id": "BT-GATE-015",
                "run_id": RUN_ID,
                "validation_status": "PASS",
                **progress,
                "typed_scientific_values": 17,
                "delivery_before_available_at": 0,
                "strategy_decisions": 0,
                "orders": 0,
                "fills": 0,
                "pnl_calculated": False,
                "provider_modification": False,
                "output_artifact_hashes": artifact_hashes,
                "deterministic_output_hash": deterministic_hash,
                "BT_GATE_015_CLOSED_PASS": "NOT_AUTHORIZED_PENDING_POSTEXECUTION_EXTERNAL_REVIEW",
                "next_required_action": "POSTEXECUTION_EXTERNAL_REVIEW",
            }
            final["scientific_manifest_hash"] = canonical_hash(final)
            atomic_write_json(run_directory / "final_manifest.json", final)
            AuthorizationV03.record_success(run_directory, progress)
            return final
        except BaseException as exc:
            diagnostics["restriction_domains"] = {
                "expected_replay": specification[
                    "replay_consumption_restriction_codes"
                ]
            }
            AuthorizationV03.record_failure(
                run_directory, exc, progress, diagnostics
            )
            raise
