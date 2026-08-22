"""Rebuild canonical closeout artifacts from committed task shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_core_market_raw_alignment import (
    EXPECTED_FAMILIES,
    finalize_run,
    ledger_snapshot,
    load_config,
    runtime_paths,
    task_manifest_valid,
    task_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config, _config_sha = load_config(args.config)
    run_root = Path(str(config["runtime"]["output_root"])) / args.run_id
    pre_manifest_path = runtime_paths(run_root)["control"] / "pre_manifest.json"
    if not pre_manifest_path.is_file():
        raise SystemExit(f"Pre-manifest does not exist: {pre_manifest_path}")
    pre_manifest = json.loads(pre_manifest_path.read_text(encoding="utf-8"))
    selected = [str(value) for value in pre_manifest["selected_tickers"]]
    ledger_path = runtime_paths(run_root)["control"] / "run_state.sqlite"
    snapshot = ledger_snapshot(ledger_path)
    expected_tasks = len(EXPECTED_FAMILIES) * len(selected)
    if int(snapshot["status_counts"].get("committed", 0)) != expected_tasks:
        raise SystemExit(
            f"Finalization refused: committed tasks do not equal {expected_tasks}: {snapshot['status_counts']}"
        )
    invalid = [
        f"{family}:{ticker}"
        for family in EXPECTED_FAMILIES
        for ticker in selected
        if not task_manifest_valid(
            task_paths(run_root, family, ticker)["manifest"],
            str(pre_manifest["run_contract_sha256"]),
        )
    ]
    if invalid:
        raise SystemExit(f"Finalization refused: invalid committed task artifacts: {invalid[:20]}")
    summary = finalize_run(config, run_root, pre_manifest)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
