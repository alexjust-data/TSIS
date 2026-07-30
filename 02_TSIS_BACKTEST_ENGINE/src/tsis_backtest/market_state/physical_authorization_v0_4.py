"""Durable single-use authorization state machine for BT-GATE-014 V0.4."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .contracts import MarketStateContractError


AUTHORIZATION_ID = "BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-4"
RUN_ID = "bt_gate_014_single_use_physical_market_state_consumer_v0_4"
CONSUMER_ID = "BT_GATE_014_BOUNDED_MARKET_STATE_CONSUMER"
CONTRACT_CONSUMER_ID = "BT_GATE_014_bounded_market_state_consumer_v0_1"
CONSUMED_STATUS = f"CONSUMED_BY_RUN_{RUN_ID}"
DOCUMENT_RELATIVE_PATH = (
    "docs/00_system/"
    "18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_4.md"
)
CONFIG_RELATIVE_PATH = (
    "configs/runs/"
    "bt_gate_014_single_use_physical_market_state_consumer_v0_4.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def atomic_write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            json.dump(
                data,
                handle,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    finally:
        temporary_path.unlink(missing_ok=True)


def _strict_load_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
        )
    except Exception as exc:
        raise MarketStateContractError(
            "FAIL_BT_GATE_014_AUTHORIZATION_STATE_INVALID",
            str(path),
        ) from exc
    if not isinstance(value, dict):
        raise MarketStateContractError(
            "FAIL_BT_GATE_014_AUTHORIZATION_STATE_INVALID",
            str(path),
        )
    return value


def _error_code(error: BaseException) -> str:
    return str(getattr(error, "code", type(error).__name__))


def _failure_guard(
    *,
    status: str,
    authorization_consumed: bool | str,
    error_code: str,
    error: str,
) -> dict[str, Any]:
    return {
        "authorization_consumed": authorization_consumed,
        "authorization_id": AUTHORIZATION_ID,
        "bounded_consumer_observations": 0,
        "error": error,
        "error_code": error_code,
        "fills": 0,
        "market_state_events_emitted": 0,
        "orders": 0,
        "physical_data_files_opened": 0,
        "physical_state_rows_read": 0,
        "pnl_calculated": False,
        "provider_modification": False,
        "run_id": RUN_ID,
        "status": status,
        "strategy_decisions": 0,
    }


class AuthorizationV04:
    """Consume exactly one frozen permission and arm durable failure evidence."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")

    @property
    def engine_root(self) -> Path:
        return self.path.parents[2]

    def _validate_relative_binding_path(self, relative_path: str) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH",
                relative_path,
            )
        resolved = (self.engine_root / candidate).resolve()
        engine_root = self.engine_root.resolve()
        if resolved != engine_root and engine_root not in resolved.parents:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH",
                relative_path,
            )
        return resolved

    def _validate_state_and_bindings(
        self,
        state: Mapping[str, Any],
        bindings: Mapping[str, str],
    ) -> None:
        if state.get("authorization_id") != AUTHORIZATION_ID:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_ID_MISMATCH",
                str(state.get("authorization_id")),
            )
        if (
            state.get("consumer_id") != CONSUMER_ID
            or state.get("contract_consumer_id") != CONTRACT_CONSUMER_ID
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_CONSUMER_ID_MISMATCH",
                "consumer identity",
            )
        status = state.get("status")
        if isinstance(status, str) and status.startswith("CONSUMED_BY_RUN_"):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_ALREADY_CONSUMED",
                status,
            )
        if status != "AUTHORIZED_NOT_CONSUMED":
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_NOT_ISSUED",
                str(status),
            )
        if state.get("consumed_by_run_id") is not None:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_STATE_INVALID",
                "consumed_by_run_id",
            )
        if state.get("binding_sha256") != dict(bindings):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH",
                "binding inventory",
            )
        for relative_path, expected_sha256 in bindings.items():
            target = self._validate_relative_binding_path(relative_path)
            if (
                not target.is_file()
                or sha256_file(target) != expected_sha256
            ):
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH",
                    relative_path,
                )
        document = self.engine_root / DOCUMENT_RELATIVE_PATH
        configuration = self.engine_root / CONFIG_RELATIVE_PATH
        if (
            not document.is_file()
            or sha256_file(document)
            != state.get("authorization_document_sha256")
            or not configuration.is_file()
            or sha256_file(configuration)
            != state.get("configuration_sha256")
        ):
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZED_BINDING_HASH_MISMATCH",
                "document/configuration",
            )

    def is_consumed_for_this_run(self) -> bool:
        try:
            state = _strict_load_json(self.path)
        except Exception:
            return False
        return (
            state.get("status") == CONSUMED_STATUS
            and state.get("consumed_by_run_id") == RUN_ID
        )

    def record_failure(
        self,
        run_directory: Path,
        error: BaseException,
        *,
        phase: str,
    ) -> None:
        run_directory = Path(run_directory)
        if not run_directory.is_dir():
            return
        failure_path = run_directory / "failure_manifest.json"
        if failure_path.is_file():
            try:
                existing = _strict_load_json(failure_path)
            except Exception:
                existing = {}
            if existing.get("status") in {
                "FAIL",
                "SUPERSEDED_BY_FINAL_MANIFEST_PASS",
            }:
                return
        consumed = self.is_consumed_for_this_run()
        manifest = _failure_guard(
            status="FAIL",
            authorization_consumed=consumed,
            error_code=_error_code(error),
            error=str(error),
        )
        progress_path = run_directory / "physical_progress.json"
        if progress_path.is_file():
            try:
                progress = _strict_load_json(progress_path)
            except Exception:
                progress = {}
            for key in (
                "physical_access_attempted",
                "physical_access_started",
                "physical_data_files_opened",
                "physical_state_rows_read",
                "validation_phase_reached",
                "restriction_diagnostics",
            ):
                if key in progress:
                    manifest[key] = progress[key]
        manifest["failure_phase"] = phase
        manifest["receipt_present"] = (
            run_directory / "authorization_consumption_receipt.json"
        ).is_file()
        try:
            atomic_write_json(failure_path, manifest)
        except Exception:
            # The pre-armed guard remains the durable fail-closed evidence.
            pass

    def _write_receipt(
        self,
        path: Path,
        receipt: Mapping[str, Any],
    ) -> None:
        atomic_write_json(path, dict(receipt))

    def consume(
        self,
        bindings: Mapping[str, str],
        run_directory: Path | str,
    ) -> dict[str, Any]:
        run_directory = Path(run_directory)
        expected_run_directory = self.engine_root / "runs" / RUN_ID
        if run_directory.resolve() != expected_run_directory.resolve():
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_RUN_DIRECTORY_MISMATCH",
                str(run_directory),
            )
        try:
            descriptor = os.open(
                self.lock_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
            os.close(descriptor)
        except FileExistsError as exc:
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_LOCKED",
                str(self.lock_path),
            ) from exc

        phase = "PRECONSUMPTION_VALIDATION"
        try:
            state = _strict_load_json(self.path)
            self._validate_state_and_bindings(state, bindings)
            if run_directory.exists():
                raise MarketStateContractError(
                    "FAIL_NONEMPTY_RUN_DIRECTORY",
                    str(run_directory),
                )

            phase = "DURABLE_FAILURE_GUARD_ARMING"
            run_directory.mkdir(parents=True, exist_ok=False)
            armed_guard = _failure_guard(
                status="FAIL_CLOSED_ARMED",
                authorization_consumed=(
                    "RECONCILE_WITH_CANONICAL_AUTHORIZATION_STATE"
                ),
                error_code="FAIL_BT_GATE_014_RUN_NOT_COMPLETED",
                error=(
                    "The run is incomplete unless final_manifest.json "
                    "supersedes this guard."
                ),
            )
            atomic_write_json(
                run_directory / "failure_manifest.json",
                armed_guard,
            )
            atomic_write_json(
                run_directory / "pre_run_manifest.json",
                {
                    "authorization_id": AUTHORIZATION_ID,
                    "binding_sha256": dict(bindings),
                    "physical_access_started": False,
                    "run_id": RUN_ID,
                    "status": (
                        "PREPARED_BEFORE_AUTHORIZATION_CONSUMPTION"
                    ),
                },
            )

            phase = "ATOMIC_AUTHORIZATION_CONSUMPTION"
            consumed_state = dict(state)
            consumed_state["status"] = CONSUMED_STATUS
            consumed_state["consumed_by_run_id"] = RUN_ID
            atomic_write_json(self.path, consumed_state)
            state_sha256 = sha256_file(self.path)

            phase = "CONSUMPTION_RECEIPT_WRITE"
            receipt = {
                "authorization_id": AUTHORIZATION_ID,
                "authorization_state_sha256_after_consumption": (
                    state_sha256
                ),
                "binding_sha256": dict(bindings),
                "consumer_id": CONSUMER_ID,
                "contract_consumer_id": CONTRACT_CONSUMER_ID,
                "physical_access_started": False,
                "run_id": RUN_ID,
                "status": CONSUMED_STATUS,
            }
            receipt_path = (
                run_directory / "authorization_consumption_receipt.json"
            )
            self._write_receipt(receipt_path, receipt)
            if _strict_load_json(receipt_path) != receipt:
                raise MarketStateContractError(
                    "FAIL_BT_GATE_014_AUTHORIZATION_RECEIPT_MISMATCH",
                    str(receipt_path),
                )

            phase = "RECEIPT_VERIFICATION"
            atomic_write_json(
                run_directory / "pre_run_manifest.json",
                {
                    "authorization_consumed": True,
                    "authorization_id": AUTHORIZATION_ID,
                    "authorization_receipt_sha256": sha256_file(
                        receipt_path
                    ),
                    "binding_sha256": dict(bindings),
                    "physical_access_started": False,
                    "run_id": RUN_ID,
                    "status": (
                        "AUTHORIZATION_CONSUMED_RECEIPT_VERIFIED_"
                        "PHYSICAL_ACCESS_NOT_STARTED"
                    ),
                },
            )
            return receipt
        except Exception as exc:
            self.record_failure(run_directory, exc, phase=phase)
            raise
        finally:
            self.lock_path.unlink(missing_ok=True)

    def mark_success_guard(
        self,
        run_directory: Path | str,
        final_manifest_sha256: str,
    ) -> None:
        run_directory = Path(run_directory)
        if not self.is_consumed_for_this_run():
            raise MarketStateContractError(
                "FAIL_BT_GATE_014_AUTHORIZATION_STATE_INVALID",
                "success without consumed authorization",
            )
        atomic_write_json(
            run_directory / "failure_manifest.json",
            {
                "authorization_consumed": True,
                "authorization_id": AUTHORIZATION_ID,
                "failure": False,
                "final_manifest_sha256": final_manifest_sha256,
                "run_id": RUN_ID,
                "status": "SUPERSEDED_BY_FINAL_MANIFEST_PASS",
                "superseded_by": "final_manifest.json",
            },
        )
