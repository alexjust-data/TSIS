# ruff: noqa: E402
"""Run the exact production Massive SEC runner on the frozen first 250 cases."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.run_massive_sec_acquisition import execute


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--run-id", required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--resume", action="store_true")
    values = parser.parse_args()
    values.execution_mode = "PROBE"
    return values


if __name__ == "__main__":
    raise SystemExit(execute(parse_args()))
