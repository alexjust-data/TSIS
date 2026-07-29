from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BOUNDARY = SCRIPT_DIR.parent
RUNNER = BOUNDARY / "scripts" / "market_state_core_four_scale_validation_replay_sidecar_and_reissue_runner_v0_1.py"

sys.path.insert(0, str(RUNNER.parent))
from market_state_core_four_scale_validation_replay_sidecar_and_reissue_runner_v0_1 import main

if __name__ == "__main__":
    raise SystemExit(main())