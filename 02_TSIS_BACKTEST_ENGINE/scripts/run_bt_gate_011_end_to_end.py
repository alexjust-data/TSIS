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

from tsis_backtest.backtest import (  # noqa: E402
    BacktestRunRequest,
    SingleStrategyEndToEndBacktestRunner,
    default_open_short_close_strategy,
)


DEFAULT_CONFIG = ROOT / "configs" / "runs" / "bt_gate_011_open_short_close_qg5_v0_1.json"


def _resolve_from_root(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BT-GATE-011 single-strategy end-to-end backtest.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--expect-hash", default=None)
    args = parser.parse_args()

    os.chdir(ROOT)
    config_path = _resolve_from_root(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    symbols = tuple(config["symbols"])
    strategy_spec = default_open_short_close_strategy(symbols, quantity_per_symbol=int(config["quantity_per_symbol"]))
    run_id = args.run_id or config["run_id"]
    output_root = _resolve_from_root(args.output_root or config["output_root"])
    request = BacktestRunRequest(
        run_id=run_id,
        strategy_spec=strategy_spec,
        preflight_report_path=_resolve_from_root(config["preflight_report_path"]),
        output_root=output_root,
        fixture_id=config["fixture_id"],
        session_date=date.fromisoformat(config["session_date"]),
        starting_equity=Decimal(config["starting_equity"]),
        run_purpose=config["run_classification"]["RUN_PURPOSE"],
        edge_evidence=config["run_classification"]["EDGE_EVIDENCE"],
        economic_realism=config["run_classification"]["ECONOMIC_REALISM"],
        strategy_optimization=config["run_classification"]["STRATEGY_OPTIMIZATION"],
    )
    runner = SingleStrategyEndToEndBacktestRunner()
    result = runner.run(request)
    repeat = runner.run(request)
    hashes_match = result.summary.deterministic_output_hash == repeat.summary.deterministic_output_hash
    expected_hash_matches = args.expect_hash is None or result.summary.deterministic_output_hash == args.expect_hash
    determinism_report = {
        "status": "PASS" if hashes_match and expected_hash_matches else "FAIL",
        "repeat_count": 2,
        "first_deterministic_output_hash": result.summary.deterministic_output_hash,
        "second_deterministic_output_hash": repeat.summary.deterministic_output_hash,
        "semantic_hashes_match": hashes_match,
        "expected_hash": args.expect_hash,
        "expected_hash_matches": expected_hash_matches,
        "validation_statuses": [result.summary.validation_status, repeat.summary.validation_status],
    }
    run_dir = runner.write_result(result, determinism_report=determinism_report)
    payload = {
        "run_dir": str(run_dir),
        "validation_status": result.summary.validation_status,
        "order_count": result.summary.order_count,
        "fill_count": result.summary.fill_count,
        "trade_count": result.summary.trade_count,
        "gross_pnl": str(result.summary.gross_pnl),
        "total_costs": str(result.summary.total_costs),
        "net_pnl": str(result.summary.net_pnl),
        "ending_equity": str(result.summary.ending_equity),
        "event_loop_mode": result.summary.event_loop_mode,
        "event_loop_future_event_access_detected": result.summary.event_loop_future_event_access_detected,
        "deterministic_output_hash": result.summary.deterministic_output_hash,
        "expected_hash_matches": expected_hash_matches,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.summary.validation_status == "PASS" and determinism_report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
