#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


TARGET_BLOCKERS = {
    "HOLDER_OVERLAP_UNRESOLVED",
    "ECONOMIC_POSITION_OVERLAP_UNRESOLVED",
}


def shard_for(instrument_id: str, count: int = 4) -> int:
    return int(hashlib.sha256(instrument_id.encode()).hexdigest(), 16) % count


def execute(args: argparse.Namespace) -> Path:
    cases = json.loads(args.case_matrix.read_text(encoding="utf-8"))
    requested = {ticker.upper() for ticker in args.ticker}
    cases = [case for case in cases if str(case["ticker"]).upper() in requested]
    if {str(case["ticker"]).upper() for case in cases} != requested:
        raise ValueError("selected ticker absent from case matrix")
    rows = []
    component_hashes = set()
    for case in cases:
        ticker = str(case["ticker"])
        root = args.run_root / "runs" / args.run_template.format(
            ticker=ticker, ticker_lower=ticker.lower()
        )
        manifest = json.loads((root / "final_manifest.json").read_text(encoding="utf-8"))
        holder = json.loads((root / "holder_deduplication.json").read_text(encoding="utf-8"))
        float_readout = json.loads((root / "float_methodology_readout.json").read_text(encoding="utf-8"))
        blockers = set(float_readout.get("blocker_codes") or [])
        target_absent = not (blockers & TARGET_BLOCKERS)
        row = {
            "ticker": ticker,
            "shard": shard_for(str(case["instrument_id"])),
            "policy_id": holder.get("policy_id"),
            "source_described_rows_resolved": holder.get(
                "source_described_indirect_account_rows_resolved", 0
            ),
            "unresolved_methodology_relevant_rows": holder.get(
                "unresolved_methodology_relevant_rows"
            ),
            "row_level_resolution_complete": holder.get(
                "row_level_economic_position_resolution_complete"
            ),
            "target_overlap_blockers_absent": target_absent,
            "remaining_blockers": sorted(blockers),
            "network_requests": manifest.get("network_requests"),
            "all_checks_pass": bool(
                manifest.get("network_requests") == 0
                and holder.get("policy_id")
                == "holder_methodology_scoped_economic_position_resolution_v0_10"
                and holder.get("unresolved_methodology_relevant_rows") == 0
                and holder.get("row_level_economic_position_resolution_complete") is True
                and target_absent
            ),
        }
        rows.append(row)
        component_hashes.add(json.dumps(manifest["component_hashes"], sort_keys=True))
    shards = {row["shard"] for row in rows if row["all_checks_pass"]}
    status = "SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING" if (
        shards == {0, 1, 2, 3}
        and all(row["all_checks_pass"] for row in rows)
        and len(component_hashes) == 1
    ) else "FAIL"
    result = {
        "status": status,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "policy_id": "sec_pit_holder_economic_overlap_recovery_audit_v0_1",
        "target_blockers": sorted(TARGET_BLOCKERS),
        "covered_shards": sorted(shards),
        "component_hashes_equivalent_across_cases": len(component_hashes) == 1,
        "cases": sorted(rows, key=lambda row: row["shard"]),
        "scale_authorization": "NOT_GRANTED_REQUIRES_HUMAN_OR_GOVERNED_GATE",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return args.output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-matrix", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--run-template", required=True)
    parser.add_argument("--ticker", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    print(execute(parse_args()))
