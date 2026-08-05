"""Execute the exact BT-GATE-015 V0.4 physical probe once after external PASS."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tsis_backtest.event_state.physical_authorization_v0_4 import AuthorizationV04
from tsis_backtest.event_state.physical_runner_v0_4 import PhysicalRunnerV04

ENGINE_ROOT = Path(__file__).resolve().parent
TSIS_ROOT = ENGINE_ROOT.parent
DEFAULT_CONFIG = (
    ENGINE_ROOT
    / "configs/runs/bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
)
DEFAULT_STATE = (
    ENGINE_ROOT
    / "configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_4.json"
)
DEFAULT_SPEC = (
    ENGINE_ROOT
    / "configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_4_spec.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--execute-authorized-physical-read",
        action="store_true",
        help="Required explicit acknowledgement after independent preexecution PASS.",
    )
    args = parser.parse_args()
    if not args.execute_authorized_physical_read:
        parser.error(
            "physical execution is fail-closed; provide "
            "--execute-authorized-physical-read only after external PASS"
        )
    authorization = AuthorizationV04(DEFAULT_STATE, DEFAULT_SPEC)
    result = PhysicalRunnerV04().execute(TSIS_ROOT, args.config, authorization)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
