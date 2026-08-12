#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def execute(selection_path: Path, output: Path) -> Path:
    selection_path, output = selection_path.resolve(), output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    selection = pd.read_parquet(selection_path)
    lifecycle = selection.loc[selection["roles_v0_2"].map(
        lambda roles: "LIFECYCLE_EVIDENCE_CANDIDATE" in list(roles)
    )].copy().sort_values(["ticker", "filing_date", "accession_number"])
    path = output / "lifecycle_primary_acquisition_plan.parquet"
    lifecycle.to_parquet(path, index=False)
    manifest = {
        "run_id": output.name, "status": "COMPLETE", "created_at_utc": datetime.now(UTC).isoformat(),
        "policy_id": "sec_pit_lifecycle_metadata_selection_v0_1",
        "source_selection_sha256": sha256_file(selection_path),
        "ticker_count": lifecycle["ticker"].nunique(), "document_count": len(lifecycle),
        "network_access": "PROHIBITED_AND_NOT_USED", "primary_documents": "NOT_ACQUIRED",
        "output_sha256": sha256_file(path),
    }
    (output / "final_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args.selection, args.output))
