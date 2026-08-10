from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from sec_pit.change_explanation import build_daily_change_explanations


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--daily-context", type=Path, required=True)
    parser.add_argument("--cusip-intervals", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.output_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(UTC).isoformat()
    _write(
        run_dir / "pre_manifest.json",
        {
            "run_id": args.run_id,
            "status": "RUNNING",
            "started_at_utc": started,
            "pid": os.getpid(),
            "builder": "daily_change_explanation_v0_1",
            "daily_context": str(args.daily_context),
            "cusip_intervals": str(args.cusip_intervals),
        },
    )
    daily = pd.read_parquet(args.daily_context)
    intervals = pd.read_parquet(args.cusip_intervals)
    rows, readout = build_daily_change_explanations(
        daily.to_dict("records"), intervals.to_dict("records")
    )
    pd.DataFrame(rows).to_parquet(run_dir / "daily_change_explanation_ledger.parquet", index=False)
    _write(run_dir / "g16_change_explanation_readout.json", readout)
    final = {
        "run_id": args.run_id,
        "status": "COMPLETE",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "g16_status": readout["status"],
        "readout": readout,
    }
    _write(run_dir / "final_manifest.json", final)
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
