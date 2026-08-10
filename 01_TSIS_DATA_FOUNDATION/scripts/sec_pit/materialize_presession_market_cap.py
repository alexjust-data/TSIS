from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from sec_pit.presession_market_cap import build_presession_reference_market_cap


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--daily-os", type=Path, required=True)
    parser.add_argument("--daily-price-root", type=Path, required=True)
    parser.add_argument("--corporate-actions", type=Path, required=True)
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--instrument-id", required=True)
    args = parser.parse_args()

    run_dir = args.output_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(UTC).isoformat()
    price_files = sorted(args.daily_price_root.glob("year=*/day_aggs_*.parquet"))
    pre_manifest = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "started_at_utc": started,
        "pid": os.getpid(),
        "builder": "presession_market_cap_v0_1",
        "ticker": args.ticker,
        "instrument_id": args.instrument_id,
        "daily_os_path": str(args.daily_os),
        "daily_os_sha256": _sha256(args.daily_os),
        "daily_price_root": str(args.daily_price_root),
        "daily_price_checkpoint_semantics": "adjusted=true",
        "daily_price_files": [str(path) for path in price_files],
        "corporate_actions_path": str(args.corporate_actions),
        "corporate_actions_sha256": _sha256(args.corporate_actions),
    }
    _write_json(run_dir / "pre_manifest.json", pre_manifest)

    os_frame = pd.read_parquet(args.daily_os)
    price_frame = pd.concat((pd.read_parquet(path) for path in price_files), ignore_index=True)
    actions = pd.read_parquet(args.corporate_actions)
    actions = actions.loc[actions["instrument_id"].eq(args.instrument_id)].copy()
    rows, readout = build_presession_reference_market_cap(
        os_frame.to_dict("records"),
        price_frame.to_dict("records"),
        actions.to_dict("records"),
    )
    output_path = run_dir / "daily_presession_reference_market_cap.parquet"
    pd.DataFrame(rows).to_parquet(output_path, index=False)
    actions_path = run_dir / "corporate_action_evidence.parquet"
    actions.to_parquet(actions_path, index=False)
    _write_json(run_dir / "g10_presession_market_cap_readout.json", readout)

    final_manifest = {
        "run_id": args.run_id,
        "status": "COMPLETE",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "g10_status": readout["status"],
        "readout": readout,
        "outputs": {
            output_path.name: _sha256(output_path),
            actions_path.name: _sha256(actions_path),
        },
    }
    _write_json(run_dir / "final_manifest.json", final_manifest)
    print(json.dumps(final_manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
