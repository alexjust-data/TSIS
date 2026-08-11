from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import recover_trading_activity_stage8_cpp_full_materialization as recovery  # noqa: E402


def _plan(tmp_path: Path) -> dict:
    return {
        "runtime_root": str(tmp_path / "runtime"),
        "output_root": str(tmp_path / "outputs"),
        "pointer_root": str(tmp_path / "pointers"),
        "expected_stage8_engine_fingerprint": "engine-fingerprint",
        "shards": [
            {"shard_index": index, "run_id": f"ta3c1_s{index}", "expected_block_count": 60}
            for index in range(4)
        ],
    }


def _coordinator_command(plan: dict, index: int) -> list[str]:
    shard = plan["shards"][index]
    return [
        sys.executable,
        str(recovery.COORDINATOR),
        "--run-id",
        shard["run_id"],
        "--runtime-root",
        plan["runtime_root"],
        "--output-root",
        plan["output_root"],
        "--pointer-root",
        plan["pointer_root"],
        "--shard-index",
        str(index),
        "--shard-count",
        "4",
        "--stage8-engine",
        "cpp",
        "--expected-stage8-engine-fingerprint",
        plan["expected_stage8_engine_fingerprint"],
    ]


def test_atomic_json_retries_transient_replace_denial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "heartbeat_latest.json"
    real_replace = recovery.os.replace
    attempts = 0

    def flaky_replace(source: Path, destination: Path) -> None:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise PermissionError(5, "transient reader lock")
        real_replace(source, destination)

    monkeypatch.setattr(recovery.os, "replace", flaky_replace)
    monkeypatch.setattr(recovery.time, "sleep", lambda _: None)

    recovery.atomic_json(target, {"status": "RUNNING"})

    assert json.loads(target.read_text(encoding="utf-8")) == {"status": "RUNNING"}
    assert attempts == 3
    assert not list(tmp_path.glob("*.tmp"))


def test_discover_live_shards_adopts_exact_coordinator(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    records = [
        {
            "pid": 101,
            "create_time": 123.0,
            "name": "python.exe",
            "command": _coordinator_command(plan, 0),
        }
    ]

    found = recovery.discover_live_shards(plan, records)

    assert found[0]["pid"] == 101
    assert found[0]["mode"] == "ADOPTED_COORDINATOR"


def test_discover_live_shards_fails_closed_on_duplicate(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    records = [
        {
            "pid": pid,
            "create_time": float(pid),
            "name": "python.exe",
            "command": _coordinator_command(plan, 0),
        }
        for pid in (101, 202)
    ]

    with pytest.raises(RuntimeError, match="Duplicate live coordinators"):
        recovery.discover_live_shards(plan, records)


def test_discover_live_shards_rejects_mismatched_writer(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    command = _coordinator_command(plan, 0)
    command[command.index("--output-root") + 1] = str(tmp_path / "wrong")

    with pytest.raises(RuntimeError, match="mismatched command"):
        recovery.discover_live_shards(
            plan,
            [
                {
                    "pid": 101,
                    "create_time": 123.0,
                    "name": "python.exe",
                    "command": command,
                }
            ],
        )


def test_progress_preserves_complete_blocks_after_restart(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    runtime = Path(plan["runtime_root"])
    shard0 = runtime / "ta3c1_s0"
    shard1 = runtime / "ta3c1_s1"
    shard0.mkdir(parents=True)
    shard1.mkdir(parents=True)
    (shard0 / "final_manifest.json").write_text(
        json.dumps(
            {
                "final_status": "COMPLETE",
                "completed_blocks": [{"block_run_id": str(i)} for i in range(60)],
                "failed_blocks": [],
            }
        ),
        encoding="utf-8",
    )
    (shard1 / "heartbeat_history.jsonl").write_text(
        json.dumps({"completed_blocks": 27, "item": "ta3b:active"}) + "\n",
        encoding="utf-8",
    )

    completed, items = recovery.aggregate_progress(runtime, plan["shards"])

    assert completed == 87
    assert items == ["ta3b:active"]
    assert recovery.shard_complete(runtime, plan["shards"][0])[0] is True
    assert recovery.shard_complete(runtime, plan["shards"][1])[0] is False


def test_duplicate_supervisor_matches_same_plan_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path = tmp_path / "plan.json"
    other_plan = tmp_path / "other.json"
    records = [
        {
            "pid": 501,
            "create_time": 1.0,
            "name": "python.exe",
            "command": [
                sys.executable,
                str(recovery.SCRIPT_PATH),
                "--plan",
                str(plan_path),
            ],
        },
        {
            "pid": 502,
            "create_time": 2.0,
            "name": "python.exe",
            "command": [
                sys.executable,
                str(recovery.SCRIPT_PATH),
                "--plan",
                str(other_plan),
            ],
        },
    ]
    monkeypatch.setattr(recovery, "process_records", lambda: records)
    monkeypatch.setattr(recovery.os, "getpid", lambda: 999)

    assert recovery.duplicate_recovery_supervisors(plan_path) == [501]
