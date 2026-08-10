#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.storage import atomic_write_json  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(args: argparse.Namespace) -> dict:
    policy = EdgarAvailabilityPolicy()
    selected: list[dict] = []
    with args.candidates.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if args.ticker and row.get("ticker", "").upper() != args.ticker.upper():
                continue
            selected.append(row)

    missing_sources = 0
    hash_mismatches = 0
    availability_unresolved = 0
    invalid_values = 0
    methods: Counter[str] = Counter()
    forms: Counter[str] = Counter()
    for row in selected:
        methods[row.get("extraction_method", "UNKNOWN")] += 1
        forms[row.get("form", "UNKNOWN")] += 1
        try:
            if float(row.get("metric_value", 0)) <= 0:
                invalid_values += 1
        except (TypeError, ValueError):
            invalid_values += 1
        decision = policy.resolve(row.get("acceptance_datetime_edgar"), row.get("form"))
        if decision.eligible_from_session is None:
            availability_unresolved += 1
        source = args.pilot_root / row.get("source_relative_path", "")
        if not source.exists():
            missing_sources += 1
        elif args.verify_hashes and row.get("source_sha256") and sha256(source) != row["source_sha256"]:
            hash_mismatches += 1

    result = {
        "audit_id": "sec_pit_existing_pilot_compatibility_v0_1",
        "ticker": args.ticker,
        "candidate_rows": len(selected),
        "unique_candidate_ids": len({row.get("candidate_id") for row in selected}),
        "unique_accessions": len({row.get("accession_number") for row in selected}),
        "missing_source_files": missing_sources,
        "source_hash_mismatches": hash_mismatches,
        "availability_unresolved": availability_unresolved,
        "invalid_metric_values": invalid_values,
        "extraction_methods": dict(sorted(methods.items())),
        "forms": dict(sorted(forms.items())),
        "compatibility_verdict": "PASS_WITH_RESTRICTIONS" if selected and not missing_sources and not hash_mismatches and not invalid_values else "FAIL",
        "restrictions": [
            "legacy candidates remain candidate evidence, not admitted O/S anchors",
            "ownership, holder deduplication and float gates are not evaluated by this audit",
            "availability is recomputed under edgar_availability_conservative_v0_1",
        ],
    }
    if args.output:
        atomic_write_json(args.output, result)
    return result


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Audit compatibility of the existing SEC pilot")
    value.add_argument("--pilot-root", type=Path, default=Path(r"D:\sec_float_pit_v0_1"))
    value.add_argument("--candidates", type=Path, default=Path(r"D:\sec_float_pit_v0_1\derived\os_candidates_v0_1.jsonl"))
    value.add_argument("--ticker")
    value.add_argument("--verify-hashes", action="store_true")
    value.add_argument("--output", type=Path)
    return value


if __name__ == "__main__":
    args = parser().parse_args()
    print(json.dumps(audit(args), indent=2, sort_keys=True))

