# ruff: noqa: E402
"""Network-free integrity audit for a Massive SEC acquisition run."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.massive_sec_storage import MassiveSecStorage
from sec_pit.storage import atomic_write_json


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def audit(output_root: Path, run_id: str, *, rebuild_ledgers: bool) -> dict[str, Any]:
    storage = MassiveSecStorage(output_root.resolve(), run_id)
    run_root = storage.run_root
    if not run_root.is_dir():
        raise FileNotFoundError(run_root)
    final_path = run_root / "final_manifest.json"
    final = json.loads(final_path.read_text(encoding="utf-8-sig")) if final_path.is_file() else {}
    receipts = list(storage.iter_receipts())
    errors: list[str] = []
    endpoint_counts: Counter[str] = Counter()
    request_ids: Counter[str] = Counter()
    result_rows = raw_bytes = 0
    for receipt in receipts:
        endpoint_id = str(receipt.get("endpoint_id") or "")
        work_id = str(receipt.get("work_id") or "")
        try:
            validated = storage.load_receipt(endpoint_id, work_id)
            if validated is None:
                raise RuntimeError("receipt disappeared during audit")
        except Exception as exc:
            errors.append(f"{endpoint_id}/{work_id}: {type(exc).__name__}: {exc}")
            continue
        endpoint_counts[endpoint_id] += 1
        request_ids[str(receipt.get("request_id") or "")] += 1
        result_rows += int(receipt.get("result_count") or 0)
        raw_bytes += int(receipt.get("raw_bytes") or 0)
    duplicate_work_ids = len(receipts) - len({str(row.get("work_id")) for row in receipts})
    blank_request_ids = request_ids.pop("", 0)
    temp_files = [path.as_posix() for path in run_root.rglob("*.tmp")]
    datasets_root = output_root / "datasets"
    if datasets_root.is_dir():
        temp_files.extend(path.as_posix() for path in datasets_root.rglob("*.tmp"))
    temp_files = sorted(set(temp_files))
    ledger_summary = storage.rebuild_request_ledgers() if rebuild_ledgers else None
    status = (
        "PASS"
        if final.get("status") == "COMPLETE"
        and not errors
        and duplicate_work_ids == 0
        and blank_request_ids == 0
        else "FAIL_OR_INCOMPLETE"
    )
    report = {
        "audit_id": "massive_sec_acquisition_integrity_audit_v0_1",
        "run_id": run_id,
        "generated_at_utc": utc_now(),
        "status": status,
        "run_final_status": final.get("status", "MISSING"),
        "receipt_count": len(receipts),
        "endpoint_page_counts": dict(sorted(endpoint_counts.items())),
        "result_rows": result_rows,
        "raw_bytes": raw_bytes,
        "duplicate_work_ids": duplicate_work_ids,
        "blank_request_ids": blank_request_ids,
        "receipt_validation_errors": errors,
        "orphan_temp_files": temp_files,
        "temp_scan_scope": "RUN_ROOT_AND_DATASETS; CAS_SKIPPED_BY_DESIGN",
        "ledger_summary": ledger_summary,
        "scope": "STORAGE_AND_LINEAGE_ONLY_NOT_SCHEMA_OR_SEMANTIC_PROMOTION",
    }
    atomic_write_json(run_root / "audit_manifest.json", report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--rebuild-ledgers", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.output_root, args.run_id, rebuild_ledgers=args.rebuild_ledgers)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
