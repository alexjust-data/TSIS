from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / 'scripts'
    / 'core_market_session_coverage_audit'
    / 'monitor_core_market_session_coverage_ledger.py'
)
SPEC = importlib.util.spec_from_file_location('coverage_ledger_monitor', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_ledger_snapshot_uses_all_tasks_as_denominator(tmp_path: Path) -> None:
    database = tmp_path / 'run_state.sqlite'
    with sqlite3.connect(database) as connection:
        connection.execute('CREATE TABLE run_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        connection.execute(
            '''
            CREATE TABLE tasks(
                ticker TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                worker_pid INTEGER,
                started_at_utc TEXT,
                files_read INTEGER,
                minute_rows_read INTEGER,
                presence_rows INTEGER,
                gap_rows INTEGER
            )
            '''
        )
        connection.execute('INSERT INTO run_metadata VALUES(?, ?)', ('run_id', 'test_run'))
        connection.executemany(
            'INSERT INTO tasks VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
            [
                ('AAA', 'committed', 1, None, 2, 100, 20, 3),
                ('BBB', 'pending', None, None, None, None, None, None),
                ('CCC', 'running', 9, '2026-08-22T00:00:00Z', None, None, None, None),
            ],
        )

    snapshot = MODULE.ledger_snapshot(database)

    assert snapshot['total'] == 3
    assert snapshot['counts'] == {'committed': 1, 'pending': 1, 'running': 1}
    assert snapshot['files_read'] == 2
    assert snapshot['minute_rows_read'] == 100
    assert snapshot['presence_rows'] == 20
    assert snapshot['gap_rows'] == 3
    assert snapshot['active'] == [('CCC', 9, '2026-08-22T00:00:00Z')]
