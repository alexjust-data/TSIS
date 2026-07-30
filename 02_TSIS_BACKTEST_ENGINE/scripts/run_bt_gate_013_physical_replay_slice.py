from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tsis_backtest.physical_replay import PhysicalHistoricalReplaySliceRunner, PhysicalReplaySliceRequest  # noqa: E402

DEFAULT_CONFIG = ROOT / "configs" / "runs" / "bt_gate_013_physical_historical_replay_slice_v0_1.json"


def _resolve(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BT-GATE-013 physical historical replay slice.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--expect-hash", default=None)
    args = parser.parse_args()

    os.chdir(ROOT)
    config = json.loads(_resolve(args.config).read_text(encoding="utf-8"))
    request = PhysicalReplaySliceRequest(
        run_id=args.run_id or config["run_id"],
        physical_root=_resolve(config["physical_root"]),
        source_root_relative=config["source_root_relative"],
        validation_manifest_path=_resolve(config["validation_manifest_path"]),
        validation_manifest_relative=config["validation_manifest_relative"],
        portable_fixture_manifest_path=_resolve(config["portable_fixture_manifest_path"]),
        portable_fixture_manifest_sha256=config["portable_fixture_manifest_sha256"],
        session_calendar_snapshot_path=_resolve(config["session_calendar_snapshot_path"]),
        session_calendar_snapshot_relative=config["session_calendar_snapshot_relative"],
        session_calendar_snapshot_sha256=config["session_calendar_snapshot_sha256"],
        symbols=tuple(config["symbols"]),
        session_dates=tuple(date.fromisoformat(item) for item in config["session_dates"]),
        price_view=config.get("price_view", "quote_guarded_1m"),
    )
    runner = PhysicalHistoricalReplaySliceRunner()
    output_root = _resolve(args.output_root or config["output_root"])
    result, bundle = runner.run(
        request,
        output_root=output_root,
        starting_equity=Decimal(config["starting_equity"]),
        quantity_per_symbol=int(config["quantity_per_symbol"]),
    )
    repeat, repeat_bundle = runner.run(
        request,
        output_root=output_root,
        starting_equity=Decimal(config["starting_equity"]),
        quantity_per_symbol=int(config["quantity_per_symbol"]),
    )
    hashes_match = result.summary.deterministic_output_hash == repeat.summary.deterministic_output_hash
    lineage_hashes_match = runner._physical_manifest(request, bundle, result)["row_to_event_lineage_hash"] == runner._physical_manifest(request, repeat_bundle, repeat)["row_to_event_lineage_hash"]
    expected_hash = args.expect_hash if args.expect_hash is not None else config.get("expected_deterministic_output_hash")
    expected_hash_matches = expected_hash is None or result.summary.deterministic_output_hash == expected_hash
    determinism_report = {
        "status": "PASS" if hashes_match and lineage_hashes_match and expected_hash_matches else "FAIL",
        "repeat_count": 2,
        "first_deterministic_output_hash": result.summary.deterministic_output_hash,
        "second_deterministic_output_hash": repeat.summary.deterministic_output_hash,
        "semantic_hashes_match": hashes_match,
        "row_to_event_lineage_hashes_match": lineage_hashes_match,
        "expected_hash": expected_hash,
        "expected_hash_matches": expected_hash_matches,
        "validation_statuses": [result.summary.validation_status, repeat.summary.validation_status],
    }
    run_dir = runner.write_result(result, bundle, determinism_report=determinism_report)
    payload = {
        "run_dir": str(run_dir),
        "validation_status": result.summary.validation_status,
        "session_count": result.summary.session_count,
        "symbol_count": result.summary.symbol_count,
        "symbol_session_count": result.summary.symbol_session_count,
        "replay_event_count": result.summary.replay_event_count,
        "replay_bar_count": result.summary.replay_bar_count,
        "replay_gap_count": result.summary.replay_gap_count,
        "order_count": result.summary.order_count,
        "fill_count": result.summary.fill_count,
        "trade_count": result.summary.trade_count,
        "gross_pnl": str(result.summary.gross_pnl),
        "total_costs": str(result.summary.total_costs),
        "net_pnl": str(result.summary.net_pnl),
        "ending_equity": str(result.summary.ending_equity),
        "event_loop_mode": result.summary.event_loop_mode,
        "deterministic_output_hash": result.summary.deterministic_output_hash,
        "expected_hash_matches": expected_hash_matches,
        "physical_run_authorization": "AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE",
        "StateReplayFeed": "NOT_AUTHORIZED",
        "Market State consumption": "NOT_AUTHORIZED",
        "Event State consumption": "NOT_AUTHORIZED",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.summary.validation_status == "PASS" and determinism_report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
