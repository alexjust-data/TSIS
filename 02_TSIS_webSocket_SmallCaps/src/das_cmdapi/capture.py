"""Terminal entry point for DAS CMD API capture v0.

Current implementation is a dry-run scaffold: it validates config, command
allowlist/blocklist, and run-file writing without opening a DAS socket.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import os
import sys
from pathlib import Path
from typing import Iterable

from .allowlist import BLOCKED_PREFIXES, redacted_command, validate_command
from .config import CaptureConfig, config_to_dict, load_config
from .run_files import append_jsonl, append_log, atomic_write_json, ensure_run_files, make_run_id, raw_run_root, utc_now
from .screener import denominator_to_dict


def build_command_plan(config: CaptureConfig) -> list[str]:
    commands: list[str] = ["ECHO OFF", "CLIENT", "ReturnFullLv1 YES"]
    if config.socket_login_enabled:
        commands.insert(0, "LOGIN <user> <password> <account> 0")
    if "TOPLIST" in {c.upper() for c in config.channels}:
        commands.extend(["SB TOPLIST", "UNSB TOPLIST"])
    for symbol in config.symbols:
        channels = {c.upper() for c in config.channels}
        if "LV1" in channels:
            commands.extend([f"SB {symbol} Lv1", f"UNSB {symbol} Lv1"])
        if "TMS" in channels:
            commands.extend([f"SB {symbol} tms", f"UNSB {symbol} tms"])
        if "LV2" in channels:
            commands.extend([f"SB {symbol} Lv2", f"UNSB {symbol} Lv2"])
        if "DAYCHART" in channels:
            commands.extend([f"SB {symbol} DAYCHART <start> <end>", f"UNSB {symbol} DAYCHART"])
        if "MINCHART" in channels:
            commands.extend([f"SB {symbol} MINCHART <start> <end> 1", f"UNSB {symbol} MINCHART"])
        for query in config.symbol_queries:
            q = query.upper()
            if q == "SHORTINFO":
                commands.append(f"GET SHORTINFO {symbol}")
            elif q == "LDLU":
                commands.append(f"GET LDLU {symbol}")
            elif q == "SYMSTATUS":
                commands.append(f"GET SymStatus {symbol}")
    for query in config.account_queries:
        commands.append("GET " + query)
    commands.append("QUIT")
    return commands


def validate_plan(config: CaptureConfig, commands: Iterable[str]) -> list[dict[str, str | bool]]:
    rows: list[dict[str, str | bool]] = []
    for command in commands:
        validation = validate_command(
            command,
            socket_login_enabled=config.socket_login_enabled,
            locate_queries_enabled=config.locate_queries_enabled,
        )
        rows.append(
            {
                "command": redacted_command(command),
                "allowed": validation.allowed,
                "blocked": validation.blocked,
                "reason": validation.reason,
            }
        )
    return rows


def run_dry_run(config: CaptureConfig, run_id: str) -> Path:
    run_root = raw_run_root(config.data_root, run_id)
    paths = ensure_run_files(run_root)
    planned_commands = build_command_plan(config)
    validation_rows = validate_plan(config, planned_commands)
    failures = [row for row in validation_rows if not row["allowed"]]
    started_at = utc_now()

    pre_manifest = {
        "schema_version": "das_cmdapi_pre_manifest_v0_1",
        "created_at_utc": started_at,
        "run_id": run_id,
        "mode": "dry_run",
        "data_root": str(config.data_root),
        "run_root": str(run_root),
        "login_mode": config.login_mode,
        "socket_login_enabled": config.socket_login_enabled,
        "locate_queries_enabled": config.locate_queries_enabled,
        "config": config_to_dict(config),
        "blocked_prefixes": list(BLOCKED_PREFIXES),
        "planned_command_count": len(planned_commands),
        "screener_initial_denominator": denominator_to_dict(config.screener),
    }
    atomic_write_json(paths["pre_manifest"], pre_manifest)

    pid_manifest = {
        "schema_version": "das_cmdapi_pid_manifest_v0_1",
        "created_at_utc": utc_now(),
        "run_id": run_id,
        "pid": os.getpid(),
        "cwd": str(Path.cwd()),
        "python": sys.executable,
        "run_root": str(run_root),
        "output_files": {key: str(value) for key, value in paths.items()},
    }
    atomic_write_json(paths["pid_manifest"], pid_manifest)

    atomic_write_json(
        paths["subscription_state"],
        {
            "schema_version": "das_cmdapi_subscription_state_v0_1",
            "updated_at_utc": utc_now(),
            "run_id": run_id,
            "mode": "dry_run",
            "active_subscriptions": [],
            "planned_symbols": list(config.symbols),
            "planned_channels": list(config.channels),
        },
    )

    for row in validation_rows:
        append_jsonl(
            paths["command_transcript"],
            {
                "schema_version": "das_cmdapi_command_transcript_v0_1",
                "observed_at_utc": utc_now(),
                "run_id": run_id,
                "mode": "dry_run",
                "command": row["command"],
                "allowed": row["allowed"],
                "blocked": row["blocked"],
                "reason": row["reason"],
                "sent_to_socket": False,
                "response": None,
            },
        )

    append_jsonl(
        paths["events"],
        {
            "schema_version": "das_cmdapi_event_v0_1",
            "observed_at_utc": utc_now(),
            "run_id": run_id,
            "mode": "dry_run",
            "event_type": "dry_run_no_socket",
            "raw_line": None,
            "message": "No DAS socket opened; command plan and run files validated only.",
        },
    )
    append_log(paths["capture_log"], "dry_run started")
    append_log(paths["capture_log"], f"planned_commands={len(planned_commands)} failures={len(failures)}")

    heartbeat = {
        "schema_version": "das_cmdapi_heartbeat_v0_1",
        "updated_at_utc": utc_now(),
        "run_id": run_id,
        "stage": "dry_run_complete" if not failures else "dry_run_validation_failed",
        "mode": "dry_run",
        "planned_command_count": len(planned_commands),
        "validation_failures": len(failures),
        "command_transcript_lines": len(validation_rows),
        "event_lines": 1,
        "last_error": None if not failures else "command_plan_contains_disallowed_commands",
    }
    atomic_write_json(paths["heartbeat"], heartbeat)

    summary = {
        "schema_version": "das_cmdapi_final_summary_v0_1",
        "created_at_utc": utc_now(),
        "run_id": run_id,
        "status": "PASS" if not failures else "FAIL",
        "mode": "dry_run",
        "run_root": str(run_root),
        "planned_command_count": len(planned_commands),
        "validation_failures": failures,
        "socket_opened": False,
        "das_commands_sent": 0,
        "notes": [
            "Dry-run validates config, command allowlist/blocklist, and required run files only.",
            "Real DAS capture is intentionally disabled until the next implementation step.",
        ],
    }
    atomic_write_json(paths["final_summary"], summary)
    append_log(paths["capture_log"], "dry_run complete")
    if failures:
        raise SystemExit(f"Dry-run validation failed with {len(failures)} disallowed planned commands. Run root: {run_root}")
    return run_root


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TSIS DAS CMD API capture v0")
    parser.add_argument("--config", type=Path, help="JSON config path. Defaults are used when omitted.")
    parser.add_argument("--data-root", type=Path, help="Override DAS live data root. Default: E:/TSIS/data_DAS_live")
    parser.add_argument("--run-id", help="Run id. Defaults to timestamped dry-run id.")
    parser.add_argument("--symbol", action="append", help="Override symbols. Can be repeated.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and write run files without connecting to DAS.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    if args.data_root is not None:
        config = replace(config, data_root=args.data_root)
    if args.symbol:
        config = replace(config, symbols=tuple(s.upper() for s in args.symbol))
    run_id = args.run_id or make_run_id("dry_run")
    if not args.dry_run:
        print("Refusing to open DAS socket: only --dry-run is implemented in this scaffold.", file=sys.stderr)
        return 2
    run_root = run_dry_run(config, run_id)
    print(f"DAS CMD API dry-run PASS: {run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



