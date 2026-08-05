"""Durable single-use authorization state machine for BT-GATE-015 V0.3."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .contracts import EventStateContractError, to_event_state_jsonable

AUTHORIZATION_ID = "BT-GATE-015-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-3"
RUN_ID = "bt_gate_015_single_use_physical_event_state_consumer_v0_3"
AUTHORIZED_STATUS = "AUTHORIZED_NOT_CONSUMED"
CONSUMED_STATUS = f"CONSUMED_BY_RUN_{RUN_ID}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def strict_load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        raise EventStateContractError(
            "FAIL_BT_GATE_015_AUTHORIZATION_STATE_INVALID", str(path)
        ) from exc
    if not isinstance(value, dict):
        raise EventStateContractError(
            "FAIL_BT_GATE_015_AUTHORIZATION_STATE_INVALID", "object required"
        )
    return value


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        json.dumps(
            to_event_state_jsonable(value),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    handle, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
        except (AttributeError, OSError):
            return
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _progress_defaults() -> dict[str, Any]:
    return {
        "authorization_consumed": False,
        "physical_access_attempted": False,
        "physical_access_started": False,
        "physical_data_files_opened": 0,
        "physical_state_records_scanned": 0,
        "physical_state_rows_selected": 0,
        "market_state_dependency_events": 0,
        "event_state_events_emitted": 0,
        "event_state_store_inserts": 0,
        "bounded_probe_observations": 0,
        "validation_phase_reached": "PRECONSUMPTION",
    }


class AuthorizationV03:
    def __init__(self, state_path: Path, spec_path: Path) -> None:
        self.state_path = Path(state_path)
        self.spec_path = Path(spec_path)

    def validate_intact(self) -> dict[str, Any]:
        state = strict_load_json(self.state_path)
        specification = strict_load_json(self.spec_path)
        expected = {
            "authorization_id": AUTHORIZATION_ID,
            "run_id": RUN_ID,
            "single_use": True,
            "status": AUTHORIZED_STATUS,
            "consumed_by_run_id": None,
            "authorization_consumption_count": 0,
        }
        if any(state.get(key) != value for key, value in expected.items()):
            code = (
                "FAIL_BT_GATE_015_AUTHORIZATION_ALREADY_CONSUMED"
                if state.get("status") == CONSUMED_STATUS
                else "FAIL_BT_GATE_015_AUTHORIZATION_STATE_INVALID"
            )
            raise EventStateContractError(code, str(state.get("status")))
        if state.get("specification_sha256") != sha256_file(self.spec_path):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH",
                "specification_sha256",
            )
        binding_paths = specification.get("executable_binding_paths")
        binding_count = specification.get("executable_binding_count")
        if (
            not isinstance(binding_paths, list)
            or not binding_paths
            or any(not isinstance(path, str) or not path for path in binding_paths)
            or len(binding_paths) != len(set(binding_paths))
            or binding_count != len(binding_paths)
        ):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH",
                "executable_binding_paths",
            )
        for relative in binding_paths:
            path = PurePosixPath(relative)
            if path.is_absolute() or ".." in path.parts or "\\" in relative:
                raise EventStateContractError(
                    "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH",
                    f"unsafe executable binding: {relative}",
                )
        bindings = state.get("binding_sha256")
        if (
            not isinstance(bindings, dict)
            or set(bindings) != set(binding_paths)
            or any(
                not isinstance(value, str)
                or len(value) != 64
                or any(character not in "0123456789abcdef" for character in value)
                for value in bindings.values()
            )
        ):
            raise EventStateContractError(
                "FAIL_BT_GATE_015_AUTHORIZATION_BINDING_MISMATCH",
                "binding_sha256 exact closed set",
            )
        return state

    def consume(self, run_directory: Path) -> dict[str, Any]:
        state = self.validate_intact()
        run_directory = Path(run_directory)
        run_directory.mkdir(parents=True, exist_ok=False)
        guard_path = run_directory / "failure_manifest.json"
        progress_path = run_directory / "physical_progress.json"
        progress = _progress_defaults()
        atomic_write_json(progress_path, progress)
        atomic_write_json(
            guard_path,
            {
                "status": "ARMED_PRECONSUMPTION",
                "gate_id": "BT-GATE-015",
                "authorization_id": AUTHORIZATION_ID,
                "run_id": RUN_ID,
                **progress,
            },
        )
        consumed = False
        try:
            consumed_state = dict(state)
            consumed_state.update(
                {
                    "status": CONSUMED_STATUS,
                    "consumed_by_run_id": RUN_ID,
                    "consumed_at_utc": utc_now(),
                    "authorization_consumption_count": 1,
                }
            )
            atomic_write_json(self.state_path, consumed_state)
            consumed = True
            receipt = {
                "authorization_id": AUTHORIZATION_ID,
                "authorization_state_sha256": sha256_file(self.state_path),
                "consumed_at_utc": consumed_state["consumed_at_utc"],
                "consumed_by_run_id": RUN_ID,
                "single_use": True,
                "status": CONSUMED_STATUS,
            }
            self._write_receipt(
                run_directory / "authorization_consumption_receipt.json", receipt
            )
            progress["authorization_consumed"] = True
            progress["validation_phase_reached"] = "AUTHORIZATION_CONSUMED"
            atomic_write_json(progress_path, progress)
            atomic_write_json(
                guard_path,
                {
                    "status": "ARMED_POSTCONSUMPTION",
                    "gate_id": "BT-GATE-015",
                    "authorization_id": AUTHORIZATION_ID,
                    "run_id": RUN_ID,
                    **progress,
                },
            )
            return receipt
        except BaseException as exc:
            progress["authorization_consumed"] = consumed
            progress["validation_phase_reached"] = "AUTHORIZATION_CONSUMPTION_FAILED"
            try:
                atomic_write_json(progress_path, progress)
                atomic_write_json(
                    guard_path,
                    {
                        "status": "FAIL",
                        "gate_id": "BT-GATE-015",
                        "authorization_id": AUTHORIZATION_ID,
                        "run_id": RUN_ID,
                        "failure_code": getattr(
                            exc,
                            "code",
                            "FAIL_BT_GATE_015_AUTHORIZATION_CONSUMPTION",
                        ),
                        "failure_message": str(exc),
                        **progress,
                    },
                )
            finally:
                raise

    @staticmethod
    def _write_receipt(path: Path, receipt: Mapping[str, Any]) -> None:
        atomic_write_json(path, receipt)

    @staticmethod
    def write_progress(run_directory: Path, progress: Mapping[str, Any]) -> None:
        atomic_write_json(Path(run_directory) / "physical_progress.json", progress)

    @staticmethod
    def record_failure(
        run_directory: Path,
        error: BaseException,
        progress: Mapping[str, Any],
        diagnostics: Mapping[str, Any] | None = None,
    ) -> None:
        atomic_write_json(
            Path(run_directory) / "failure_manifest.json",
            {
                "status": "FAIL",
                "gate_id": "BT-GATE-015",
                "authorization_id": AUTHORIZATION_ID,
                "run_id": RUN_ID,
                "failure_code": getattr(
                    error, "code", "FAIL_BT_GATE_015_PHYSICAL_CONSUMER"
                ),
                "failure_message": str(error),
                "diagnostics": dict(diagnostics or {}),
                **dict(progress),
            },
        )

    @staticmethod
    def record_success(run_directory: Path, progress: Mapping[str, Any]) -> None:
        atomic_write_json(
            Path(run_directory) / "failure_manifest.json",
            {
                "status": "SUPERSEDED_BY_FINAL_MANIFEST_PASS",
                "gate_id": "BT-GATE-015",
                "authorization_id": AUTHORIZATION_ID,
                "run_id": RUN_ID,
                **dict(progress),
            },
        )
