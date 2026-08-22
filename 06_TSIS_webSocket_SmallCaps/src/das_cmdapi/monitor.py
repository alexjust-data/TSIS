"""Simple monitor for DAS CMD API run files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor a TSIS DAS CMD API run root")
    parser.add_argument("run_root", type=Path)
    args = parser.parse_args()
    heartbeat = args.run_root / "heartbeat.json"
    summary = args.run_root / "final_summary.json"
    if heartbeat.exists():
        data = json.loads(heartbeat.read_text(encoding="utf-8-sig"))
        print("TSIS DAS CMD API monitor")
        print(f"Run root: {args.run_root}")
        print(f"Stage: {data.get('stage')}")
        print(f"Updated: {data.get('updated_at_utc')}")
        print(f"Planned commands: {data.get('planned_command_count')}")
        print(f"Validation failures: {data.get('validation_failures')}")
    else:
        print(f"heartbeat missing: {heartbeat}")
    if summary.exists():
        data = json.loads(summary.read_text(encoding="utf-8-sig"))
        print(f"Final status: {data.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
