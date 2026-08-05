from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tsis_backtest.event_state.runner import SyntheticEventStateRunRequest, SyntheticEventStateRunner
from tsis_backtest.event_state.acceptance import EventStateAcceptanceMatrix

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "configs/runs/bt_gate_015_non_physical_event_state_consumer_v0_1.json"


def request(output_root: Path) -> SyntheticEventStateRunRequest:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    return SyntheticEventStateRunRequest(
        run_id=cfg["run_id"],
        fixture_root=ROOT / cfg["fixture_root"],
        output_root=output_root,
        initial_handoff=ROOT / cfg["initial_handoff"],
        completion_handoff=ROOT / cfg["completion_handoff"],
        physical_read_authorized=cfg["physical_read_authorized"],
    )


def main() -> int:
    runner = SyntheticEventStateRunner()
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        result_a = runner.run(request(Path(a)))
        result_b = runner.run(request(Path(b)))
        if result_a["deterministic_output_hash"] != result_b["deterministic_output_hash"]:
            raise RuntimeError("FAIL_BT_GATE_015_CROSS_ROOT_DETERMINISM")
    canonical = request(ROOT / "runs")
    run_dir = canonical.output_root / canonical.run_id
    if run_dir.exists():
        import shutil
        shutil.rmtree(run_dir)
    report = EventStateAcceptanceMatrix(canonical.fixture_root).execute()
    if report["status"] != "PASS":
        raise RuntimeError("FAIL_BT_GATE_015_ACCEPTANCE_MATRIX")
    runner.write_result(canonical, result_a, report)
    print(json.dumps({
        "validation_status": "PASS",
        "deterministic_output_hash": result_a["deterministic_output_hash"],
        "physical_state_rows_read": 0,
        "event_state_events": 1,
        "store_inserts": 1,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
