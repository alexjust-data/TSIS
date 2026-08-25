from __future__ import annotations

import os

from tsis_statistics_patterns.operational_certification import (
    REQUIRED_PRE_FIELDS,
    certify_operational_surface,
)
from tsis_statistics_patterns.orchestrate import RunTelemetry, _atomic_json


def test_operational_surface_requires_live_and_final_evidence(tmp_path) -> None:
    run_id = "probe_test_v0_1"
    pre = {name: "test" for name in REQUIRED_PRE_FIELDS}
    pre.update(
        {
            "run_id": run_id,
            "wrapper_pid": os.getpid(),
            "status": "running",
            "git": {"commit": "abc", "branch": "test", "dirty": False},
        }
    )
    _atomic_json(tmp_path / "pre_manifest.json", pre)

    telemetry = RunTelemetry(tmp_path, run_id, total_shards=8)
    telemetry.start()
    telemetry.set_stage("materialize_shards")
    telemetry.shard_finished(0, 0)
    live = certify_operational_surface(tmp_path, require_final=False)
    assert live["status"] == "pass"
    assert live["heartbeat_records"] >= 3

    telemetry.finish("pass", "complete")
    _atomic_json(
        tmp_path / "operation_final_manifest.json",
        {"run_id": run_id, "status": "pass", "exit_code": 0},
    )
    final = certify_operational_surface(tmp_path, require_final=True)
    assert final["status"] == "pass"
    assert final["violations"]["pid_still_expected_alive"] == 0
