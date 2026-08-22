from __future__ import annotations

import importlib.util
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "core_market_raw_alignment_audit"
)
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
SCRIPT_PATH = SCRIPT_DIR / "scale_out_quotes_workers.py"
SPEC = importlib.util.spec_from_file_location("quotes_scaleout_test_target", SCRIPT_PATH)
assert SPEC and SPEC.loader
SCALEOUT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCALEOUT
SPEC.loader.exec_module(SCALEOUT)


def _ledger(tmp_path: Path, tickers: list[str]) -> Path:
    path = tmp_path / "run_state.sqlite"
    SCALEOUT.ACCEL.AUDIT.initialize_ledger(
        path,
        run_id="test",
        run_contract_sha256="TEST",
        families=["quotes_", "trades_ticks_prod_2005_2026"],
        tickers=tickers,
    )
    SCALEOUT.ACCEL.initialize_accelerator_ledger(path)
    return path


def test_six_concurrent_claimers_never_claim_a_ticker_twice(tmp_path: Path) -> None:
    tickers = [f"T{number:03d}" for number in range(240)]
    ledger = _ledger(tmp_path, tickers)

    def claim_all(worker_pid: int) -> list[str]:
        claimed: list[str] = []
        while True:
            result = SCALEOUT.ACCEL.claim_next_quote_task(ledger, worker_pid)
            if result is None:
                return claimed
            claimed.append(result[0])

    with ThreadPoolExecutor(max_workers=6) as pool:
        groups = list(pool.map(claim_all, range(20_001, 20_007)))

    claims = [ticker for group in groups for ticker in group]
    assert len(claims) == len(tickers)
    assert len(set(claims)) == len(tickers)
    assert set(claims) == set(tickers)


def test_recovery_only_requeues_tasks_owned_by_added_workers(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path, ["AAA", "BBB", "CCC"])
    connection = sqlite3.connect(ledger)
    try:
        connection.execute(
            "UPDATE tasks SET status='running',worker_pid=101,attempt=1 "
            "WHERE family='quotes_' AND ticker='AAA'"
        )
        connection.execute(
            "UPDATE tasks SET status='running',worker_pid=202,attempt=1 "
            "WHERE family='quotes_' AND ticker='BBB'"
        )
        connection.execute(
            "UPDATE tasks SET status='running',worker_pid=303,attempt=1 "
            "WHERE family='trades_ticks_prod_2005_2026' AND ticker='AAA'"
        )
        connection.commit()
    finally:
        connection.close()

    recovered = SCALEOUT.recover_added_worker_tasks(ledger, [202], "test_recovery")
    assert recovered == ["BBB"]
    connection = sqlite3.connect(ledger)
    try:
        rows = {
            (family, ticker): (status, worker_pid)
            for family, ticker, status, worker_pid in connection.execute(
                "SELECT family,ticker,status,worker_pid FROM tasks"
            )
        }
    finally:
        connection.close()
    assert rows[("quotes_", "AAA")] == ("running", 101)
    assert rows[("quotes_", "BBB")] == ("pending", None)
    assert rows[("trades_ticks_prod_2005_2026", "AAA")] == ("running", 303)
