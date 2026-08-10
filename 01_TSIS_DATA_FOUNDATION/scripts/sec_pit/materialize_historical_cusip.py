from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from sec_pit.historical_cusip import extract_cusips, resolve_cusip_intervals


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--corporate-actions", type=Path, required=True)
    parser.add_argument("--instrument-id", required=True)
    parser.add_argument("--valid-from", required=True)
    parser.add_argument("--valid-to", required=True)
    parser.add_argument("--admitted-cusip-issuer-number", required=True)
    args = parser.parse_args()

    run_dir = args.output_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(UTC).isoformat()
    inventory_path = args.source_run / "filing_inventory.parquet"
    acquisition_path = args.source_run / "acquisition.jsonl"
    _write(
        run_dir / "pre_manifest.json",
        {
            "run_id": args.run_id,
            "status": "RUNNING",
            "started_at_utc": started,
            "pid": os.getpid(),
            "builder": "historical_cusip_v0_1",
            "source_run": str(args.source_run),
            "filing_inventory_sha256": _hash(inventory_path),
            "acquisition_sha256": _hash(acquisition_path),
            "corporate_actions_sha256": _hash(args.corporate_actions),
            "admitted_cusip_issuer_number": args.admitted_cusip_issuer_number,
        },
    )

    inventory = pd.read_parquet(inventory_path)
    metadata = inventory.set_index("accession_number").to_dict("index")
    observations: list[dict] = []
    seen_objects: set[str] = set()
    for line in acquisition_path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        logical_path = str(record.get("logical_path", ""))
        match = re.search(r"filings/\d+/(\d{10}-\d{2}-\d{6})/", logical_path)
        object_path = record.get("object_path")
        if not match or not object_path or object_path in seen_objects:
            continue
        seen_objects.add(object_path)
        try:
            text = gzip.open(object_path, "rb").read().decode("utf-8", "ignore")
        except (OSError, EOFError):
            continue
        accession = match.group(1)
        filing = metadata.get(accession)
        if not filing:
            continue
        for cusip in extract_cusips(text):
            observations.append(
                {
                    "cusip": cusip,
                    "accession_number": accession,
                    "form": filing["form"],
                    "filing_date": str(filing["filing_date"])[:10],
                    "eligible_from_session": str(filing["eligible_from_session"])[:10],
                    "logical_path": logical_path,
                    "object_sha256": record.get("sha256"),
                }
            )

    actions = pd.read_parquet(args.corporate_actions)
    actions = actions.loc[actions["instrument_id"].eq(args.instrument_id)].copy()
    intervals, readout = resolve_cusip_intervals(
        observations,
        args.valid_from,
        args.valid_to,
        actions.to_dict("records"),
        args.admitted_cusip_issuer_number,
    )
    pd.DataFrame(observations).to_parquet(run_dir / "cusip_source_observations.parquet", index=False)
    pd.DataFrame(intervals).to_parquet(run_dir / "historical_cusip_intervals.parquet", index=False)
    _write(run_dir / "g11_historical_cusip_readout.json", readout)
    final = {
        "run_id": args.run_id,
        "status": "COMPLETE",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "g11_status": readout["status"],
        "readout": readout,
    }
    _write(run_dir / "final_manifest.json", final)
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
