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

from tsis_backtest.backtest import default_open_short_close_strategy  # noqa: E402
from tsis_backtest.portfolio import PortfolioRunRequest, PortfolioSliceRunner  # noqa: E402

DEFAULT_CONFIG = ROOT / "configs" / "runs" / "bt_gate_012_multi_symbol_multi_session_qg5_v0_1.json"


def _resolve(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BT-GATE-012 multi-symbol multi-session portfolio slice.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--expect-hash", default=None)
    args = parser.parse_args()

    os.chdir(ROOT)
    config = json.loads(_resolve(args.config).read_text(encoding="utf-8"))
    symbols = tuple(config["symbols"])
    strategy_spec = default_open_short_close_strategy(symbols, quantity_per_symbol=int(config["quantity_per_symbol"]))
    request = PortfolioRunRequest(
        run_id=args.run_id or config["run_id"],
        strategy_spec=strategy_spec,
        preflight_report_paths=tuple(_resolve(path) for path in config["preflight_report_paths"]),
        output_root=_resolve(args.output_root or config["output_root"]),
        fixture_id=config["fixture_id"],
        session_dates=tuple(date.fromisoformat(item) for item in config["session_dates"]),
        session_calendar_snapshot_path=_resolve(config["session_calendar_snapshot_path"]),
        session_calendar_snapshot_sha256=config["session_calendar_snapshot_sha256"],
        starting_equity=Decimal(config["starting_equity"]),
        run_purpose=config["run_classification"]["RUN_PURPOSE"],
        edge_evidence=config["run_classification"]["EDGE_EVIDENCE"],
        economic_realism=config["run_classification"]["ECONOMIC_REALISM"],
        strategy_optimization=config["run_classification"]["STRATEGY_OPTIMIZATION"],
    )
    runner = PortfolioSliceRunner()
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
        "session_count": result.summary.session_count,
        "symbol_count": result.summary.symbol_count,
        "symbol_session_count": result.summary.symbol_session_count,
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
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.summary.validation_status == "PASS" and determinism_report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
