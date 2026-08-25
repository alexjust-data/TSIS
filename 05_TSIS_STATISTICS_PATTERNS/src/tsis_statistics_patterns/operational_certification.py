from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_PRE_FIELDS = {
    "run_id",
    "status",
    "created_at_utc",
    "script_path",
    "script_sha256",
    "command_line",
    "cwd",
    "host",
    "user",
    "parent_pid",
    "wrapper_pid",
    "git",
    "mode",
    "dry_run",
    "input_roots",
    "output_root",
    "log_root",
    "manifest_paths",
    "expected_scope",
    "resume_policy",
    "overwrite_policy",
    "success_criteria",
    "monitor_command",
    "stop_command",
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def certify_operational_surface(run_root: Path, require_final: bool) -> dict:
    paths = {
        "pre_manifest": run_root / "pre_manifest.json",
        "pid_manifest": run_root / "pid_manifest.json",
        "heartbeat_latest": run_root / "heartbeat_latest.json",
        "heartbeat_jsonl": run_root / "heartbeat.jsonl",
        "orchestrator_log": run_root / "logs" / "orchestrator.log",
        "operation_final": run_root / "operation_final_manifest.json",
    }
    required_paths = [name for name in paths if name != "operation_final" or require_final]
    missing_paths = [name for name in required_paths if not paths[name].exists()]
    violations: dict[str, int] = {"missing_required_paths": len(missing_paths)}
    details: dict[str, Any] = {"missing_paths": missing_paths}
    if missing_paths:
        return {"status": "fail", "violations": violations, **details}

    pre = _read(paths["pre_manifest"])
    pid = _read(paths["pid_manifest"])
    heartbeat = _read(paths["heartbeat_latest"])
    jsonl_lines = [
        line for line in paths["heartbeat_jsonl"].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    missing_fields = sorted(REQUIRED_PRE_FIELDS - set(pre))
    violations.update(
        {
            "missing_pre_manifest_fields": len(missing_fields),
            "empty_heartbeat_jsonl": int(not jsonl_lines),
            "run_id_mismatch": int(
                len({pre.get("run_id"), pid.get("run_id"), heartbeat.get("run_id")}) != 1
            ),
            "wrapper_pid_mismatch": int(
                len({pre.get("wrapper_pid"), pid.get("wrapper_pid"), heartbeat.get("wrapper_pid")}) != 1
            ),
            "monitor_script_missing": int(
                not (
                    Path(__file__).resolve().parents[2]
                    / "scripts" / "monitor_atlas_run.py"
                ).exists()
            ),
            "orchestrator_log_empty": int(paths["orchestrator_log"].stat().st_size == 0),
        }
    )
    details.update(
        {
            "missing_pre_manifest_fields": missing_fields,
            "heartbeat_records": len(jsonl_lines),
            "heartbeat_stage": heartbeat.get("stage"),
            "heartbeat_status": heartbeat.get("status"),
        }
    )
    if require_final:
        final = _read(paths["operation_final"])
        violations.update(
            {
                "operation_final_not_pass": int(final.get("status") != "pass"),
                "operation_final_exit_nonzero": int(final.get("exit_code") != 0),
                "final_heartbeat_not_pass": int(heartbeat.get("status") != "pass"),
                "pid_still_expected_alive": int(bool(pid.get("expected_alive"))),
            }
        )
        details["operation_final_status"] = final.get("status")
    passed = not any(violations.values())
    return {"status": "pass" if passed else "fail", "violations": violations, **details}
