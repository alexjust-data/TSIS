"""Only authorized CLI entry point for the BT-GATE-014 V0.4 physical run."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ENGINE_ROOT = Path(__file__).resolve().parents[1]
TSIS_ROOT = ENGINE_ROOT.parent
sys.path.insert(0, str(ENGINE_ROOT / "src"))

from tsis_backtest.market_state.physical_authorization_v0_4 import (  # noqa: E402
    AUTHORIZATION_ID,
    CONFIG_RELATIVE_PATH,
    DOCUMENT_RELATIVE_PATH,
    AuthorizationV04,
)
from tsis_backtest.market_state.physical_runner_v0_4 import (  # noqa: E402
    PhysicalRunnerV04,
)


STATE_PATH = (
    ENGINE_ROOT
    / "configs/authorizations/"
    "bt_gate_014_single_use_physical_consumer_authorization_v0_4.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(
            "FAIL_BT_GATE_014_AUTHORIZATION_STATE_INVALID"
        )
    return value


def _verify_closed_binding(state: dict, configuration: dict) -> None:
    configuration_path = ENGINE_ROOT / CONFIG_RELATIVE_PATH
    document_path = ENGINE_ROOT / DOCUMENT_RELATIVE_PATH
    if (
        _sha256(configuration_path) != state.get("configuration_sha256")
        or _sha256(document_path)
        != state.get("authorization_document_sha256")
    ):
        raise SystemExit(
            "FAIL_BT_GATE_014_AUTHORIZED_BINDING_HASH_MISMATCH"
        )
    bindings = state.get("binding_sha256")
    if (
        not isinstance(bindings, dict)
        or configuration.get("binding_sha256") != bindings
    ):
        raise SystemExit(
            "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH"
        )
    for relative_path, expected_sha256 in bindings.items():
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise SystemExit(
                "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH"
            )
        target = (ENGINE_ROOT / candidate).resolve()
        if (
            ENGINE_ROOT.resolve() not in target.parents
            or not target.is_file()
            or _sha256(target) != expected_sha256
        ):
            raise SystemExit(
                "FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--confirm-authorization-id",
        required=True,
    )
    arguments = parser.parse_args()
    if arguments.confirm_authorization_id != AUTHORIZATION_ID:
        raise SystemExit(
            "FAIL_BT_GATE_014_AUTHORIZATION_ID_MISMATCH"
        )

    configuration_path = ENGINE_ROOT / CONFIG_RELATIVE_PATH
    state = _load_object(STATE_PATH)
    configuration = _load_object(configuration_path)
    _verify_closed_binding(state, configuration)

    result = PhysicalRunnerV04().execute(
        TSIS_ROOT,
        configuration,
        AuthorizationV04(STATE_PATH),
        configuration["binding_sha256"],
    )
    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
