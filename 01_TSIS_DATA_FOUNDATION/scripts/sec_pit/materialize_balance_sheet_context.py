from __future__ import annotations

import argparse
import gzip
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from sec_pit.balance_sheet_context import (
    extract_balance_sheet_facts,
    resolve_daily_balance_sheet_context,
)


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--daily-market-cap", type=Path, required=True)
    parser.add_argument("--minimum-measurement-date", required=True)
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
            "builder": "balance_sheet_context_v0_1",
            "source_run": str(args.source_run),
            "daily_market_cap": str(args.daily_market_cap),
            "minimum_measurement_date": args.minimum_measurement_date,
        },
    )
    inventory = pd.read_parquet(args.source_run / "filing_inventory.parquet")
    eligible = dict(
        zip(inventory["accession_number"], inventory["eligible_from_session"], strict=False)
    )
    acquisition = [
        json.loads(line)
        for line in (args.source_run / "acquisition.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    companyfacts = next(
        row for row in acquisition if str(row.get("logical_path", "")).startswith("companyfacts/")
    )
    with gzip.open(companyfacts["object_path"], "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    facts = extract_balance_sheet_facts(payload, eligible, args.minimum_measurement_date)
    daily = pd.read_parquet(args.daily_market_cap)
    rows, readout = resolve_daily_balance_sheet_context(daily.to_dict("records"), facts)
    pd.DataFrame(facts).to_parquet(run_dir / "balance_sheet_fact_observations.parquet", index=False)
    pd.DataFrame(rows).to_parquet(run_dir / "daily_balance_sheet_context.parquet", index=False)
    _write(run_dir / "g13_balance_sheet_context_readout.json", readout)
    final = {
        "run_id": args.run_id,
        "status": "COMPLETE",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "g13_status": readout["status"],
        "readout": readout,
    }
    _write(run_dir / "final_manifest.json", final)
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
