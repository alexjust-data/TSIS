from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"C:\TSIS_Data")
RUNNER = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering" / "09_STATE_CONSUMPTION_BOUNDARY" / "scripts" / "market_state_core_four_scale_validation_replay_sidecar_and_reissue_runner_v0_1.py"

sys.path.insert(0, str(RUNNER.parent))
from market_state_core_four_scale_validation_replay_sidecar_and_reissue_runner_v0_1 import main

if __name__ == "__main__":
    raise SystemExit(main())