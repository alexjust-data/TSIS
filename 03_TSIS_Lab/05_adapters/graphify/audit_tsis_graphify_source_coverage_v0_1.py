from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit required and prohibited TSIS source paths in the root graph.")
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    graph = json.loads(args.graph.read_text(encoding="utf-8-sig"))
    records = [*graph.get("nodes", []), *graph.get("links", []), *graph.get("hyperedges", [])]
    source_files = [str(record.get("source_file", "")).replace("\\", "/").lower() for record in records]

    required = {
        "04_TSIS_SCREENERS": "04_tsis_screeners/",
        "05_TSIS_STATISTICS_PATTERNS": "05_tsis_statistics_patterns/",
    }
    prohibited = {
        "legacy_repository_root": "01_tsis_backtest_smallcaps",
        "legacy_data_root": "e:/tsis/data",
        "removed_trading_voice": "06_tsis_trading_voice",
        "operational_refresh_queues": "graphify_refresh_queue.md",
        "excluded_market_state_event_state": (
            "00_cto_applied_architecture/03_tables_feature_engineering/"
            "00_tables_market_state_event_state.md"
        ),
        "graphify_build_manifests": "/graphify-out/build_manifest.md",
    }

    required_hits = {name: sum(fragment in source for source in source_files) for name, fragment in required.items()}
    prohibited_hits = {
        name: sum(fragment in source for source in source_files) for name, fragment in prohibited.items()
    }
    required_pass = all(count > 0 for count in required_hits.values())
    prohibited_pass = all(count == 0 for count in prohibited_hits.values())
    status = "PASS" if required_pass and prohibited_pass else "FAIL"

    payload = {
        "schema_version": "TSIS_GRAPHIFY_SOURCE_COVERAGE_AUDIT_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "graph": str(args.graph),
        "record_count": len(records),
        "distinct_source_file_count": len(set(source_files)),
        "required_hits": required_hits,
        "prohibited_hits": prohibited_hits,
        "required_pass": required_pass,
        "prohibited_pass": prohibited_pass,
        "status": status,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
