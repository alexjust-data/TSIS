"""Audit lifecycle primary-document acquisition outputs byte by byte."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.storage import atomic_write_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path)
    return parser.parse_args()


def load_object(path: Path) -> bytes:
    payload = path.read_bytes()
    return gzip.decompress(payload) if path.suffix == ".gz" else payload


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    plan = pd.read_parquet(run_root / "lifecycle_primary_acquisition_plan.parquet")
    results = pd.read_parquet(run_root / "lifecycle_primary_acquisition_results.parquet")

    joined = plan.merge(
        results[["ticker", "accession_number"]],
        on=["ticker", "accession_number"],
        how="left",
        indicator=True,
    )
    missing_results = int(joined["_merge"].ne("both").sum())
    bad_objects: list[dict[str, Any]] = []
    verified_bytes = 0
    error_signatures = (
        b"access denied",
        b"rate threshold exceeded",
        b"your request originates from an undeclared automated tool",
    )
    for row in results.to_dict("records"):
        object_path = Path(str(row.get("object_path") or ""))
        issue: dict[str, Any] = {
            "ticker": row.get("ticker"),
            "accession_number": row.get("accession_number"),
            "object_path": object_path.as_posix(),
        }
        if not object_path.is_file():
            issue["reason"] = "OBJECT_MISSING"
            bad_objects.append(issue)
            continue
        try:
            payload = load_object(object_path)
        except Exception as error:
            issue["reason"] = f"OBJECT_UNREADABLE:{type(error).__name__}"
            bad_objects.append(issue)
            continue
        verified_bytes += len(payload)
        digest = hashlib.sha256(payload).hexdigest()
        if digest != row.get("sha256"):
            issue["reason"] = "SHA256_MISMATCH"
            bad_objects.append(issue)
        elif len(payload) != int(row.get("bytes") or 0):
            issue["reason"] = "BYTE_COUNT_MISMATCH"
            bad_objects.append(issue)
        elif any(signature in payload[:2000].lower() for signature in error_signatures):
            issue["reason"] = "SEC_ERROR_PAGE_SIGNATURE"
            bad_objects.append(issue)

    duplicate_count = int(results.duplicated(["ticker", "accession_number"]).sum())
    fetched_count = int(results["status"].eq("FETCHED").sum())
    complete_path_count = int(
        results["logical_path"].astype(str).str.contains("complete", case=False).sum()
    )
    exhibit_path_count = int(
        results["logical_path"]
        .astype(str)
        .str.contains(r"exhibit|/ex\d", case=False, regex=True)
        .sum()
    )
    readout = {
        "run_id": json.loads(
            (run_root / "pre_manifest.json").read_text(encoding="utf-8")
        )["run_id"],
        "status": "PASS",
        "plan_rows": len(plan),
        "result_rows": len(results),
        "fetched_rows": fetched_count,
        "failed_rows": int(results["status"].eq("FAILED").sum()),
        "missing_result_rows": missing_results,
        "duplicate_ticker_accession_rows": duplicate_count,
        "bad_object_rows": len(bad_objects),
        "verified_response_bytes": verified_bytes,
        "complete_submission_logical_paths": complete_path_count,
        "exhibit_logical_paths": exhibit_path_count,
        "null_sha256_rows": int(results["sha256"].isna().sum()),
        "null_object_path_rows": int(results["object_path"].isna().sum()),
        "rows_by_ticker": {
            str(key): int(value) for key, value in results.groupby("ticker").size().items()
        },
        "rows_by_candidate_type": {
            str(key): int(value)
            for key, value in results.groupby("candidate_type").size().items()
        },
        "bad_objects": bad_objects,
        "primary_document_extraction": "NOT_EXECUTED",
        "lifecycle_event_resolution": "NOT_EXECUTED",
        "promotion_status": "NOT_AUTHORIZED",
    }
    fail_values = (
        readout["plan_rows"] != 50,
        readout["result_rows"] != readout["plan_rows"],
        readout["fetched_rows"] != readout["plan_rows"],
        readout["failed_rows"] != 0,
        readout["missing_result_rows"] != 0,
        readout["duplicate_ticker_accession_rows"] != 0,
        readout["bad_object_rows"] != 0,
        readout["complete_submission_logical_paths"] != 0,
        readout["exhibit_logical_paths"] != 0,
        readout["null_sha256_rows"] != 0,
        readout["null_object_path_rows"] != 0,
    )
    if any(fail_values):
        readout["status"] = "FAIL"
    atomic_write_json(run_root / "lifecycle_primary_acquisition_audit.json", readout)
    print(json.dumps(readout, indent=2))
    return 0 if readout["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())