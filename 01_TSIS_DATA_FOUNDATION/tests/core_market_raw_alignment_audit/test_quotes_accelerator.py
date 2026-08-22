from __future__ import annotations

import importlib.util
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "core_market_raw_alignment_audit"
    / "accelerate_quotes_workers.py"
)
SPEC = importlib.util.spec_from_file_location("quotes_accelerator_test_target", SCRIPT_PATH)
assert SPEC and SPEC.loader
ACCELERATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ACCELERATOR
SPEC.loader.exec_module(ACCELERATOR)


def _ledger(tmp_path: Path, tickers: list[str]) -> Path:
    path = tmp_path / "run_state.sqlite"
    ACCELERATOR.AUDIT.initialize_ledger(
        path,
        run_id="test",
        run_contract_sha256="TEST",
        families=["quotes_"],
        tickers=tickers,
    )
    ACCELERATOR.initialize_accelerator_ledger(path)
    return path


def test_atomic_claims_assign_each_quote_ticker_once(tmp_path: Path) -> None:
    tickers = [f"T{number:03d}" for number in range(120)]
    ledger = _ledger(tmp_path, tickers)

    def claim_all(worker_pid: int) -> list[str]:
        claimed: list[str] = []
        while True:
            result = ACCELERATOR.claim_next_quote_task(ledger, worker_pid)
            if result is None:
                return claimed
            claimed.append(result[0])

    with ThreadPoolExecutor(max_workers=8) as pool:
        groups = list(pool.map(claim_all, range(10_001, 10_009)))

    claims = [ticker for group in groups for ticker in group]
    assert len(claims) == len(tickers)
    assert len(set(claims)) == len(tickers)
    assert set(claims) == set(tickers)

    connection = sqlite3.connect(ledger)
    try:
        event_count = connection.execute(
            "SELECT COUNT(*) FROM quote_accelerator_events WHERE event_type='TASK_CLAIMED'"
        ).fetchone()[0]
        duplicate_count = connection.execute(
            "SELECT COUNT(*) FROM ("
            "SELECT ticker FROM quote_accelerator_events WHERE event_type='TASK_CLAIMED' "
            "GROUP BY ticker HAVING COUNT(*) > 1)"
        ).fetchone()[0]
    finally:
        connection.close()
    assert event_count == len(tickers)
    assert duplicate_count == 0


def test_recovery_changes_only_the_exact_quotes_worker_task(tmp_path: Path) -> None:
    ledger = tmp_path / "run_state.sqlite"
    ACCELERATOR.AUDIT.initialize_ledger(
        ledger,
        run_id="test",
        run_contract_sha256="TEST",
        families=["quotes_", "ohlcv_1m", "trades_ticks_prod_2005_2026"],
        tickers=["AACT"],
    )
    ACCELERATOR.initialize_accelerator_ledger(ledger)
    connection = ACCELERATOR.AUDIT.connect_ledger(ledger)
    try:
        connection.execute(
            "UPDATE tasks SET status='running',worker_pid=111,attempt=1 WHERE family='quotes_'"
        )
        connection.execute(
            "UPDATE tasks SET status='running',worker_pid=222,attempt=1 WHERE family='ohlcv_1m'"
        )
        connection.execute(
            "UPDATE tasks SET status='running',worker_pid=333,attempt=1 "
            "WHERE family='trades_ticks_prod_2005_2026'"
        )
        connection.commit()
    finally:
        connection.close()

    assert ACCELERATOR.recover_replaced_quote_task(ledger, 111) == "AACT"
    connection = sqlite3.connect(ledger)
    try:
        rows = {
            family: (status, worker_pid)
            for family, status, worker_pid in connection.execute(
                "SELECT family,status,worker_pid FROM tasks"
            )
        }
    finally:
        connection.close()
    assert rows["quotes_"] == ("pending", None)
    assert rows["ohlcv_1m"] == ("running", 222)
    assert rows["trades_ticks_prod_2005_2026"] == ("running", 333)
