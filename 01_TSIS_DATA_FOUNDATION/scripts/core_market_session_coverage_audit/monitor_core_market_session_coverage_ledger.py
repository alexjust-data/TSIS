'''Read-only live monitor for the core market session coverage SQLite ledger.

This monitor deliberately never opens heartbeat.json.  On Windows an open
heartbeat handle can race with the runner's atomic os.replace operation.
'''

from __future__ import annotations

import argparse
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


UTC = timezone.utc
RUNNER_NAME = 'audit_core_market_session_coverage.py'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root', type=Path, required=True)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--interval-seconds', type=int, default=10)
    args = parser.parse_args()
    if not 2 <= args.interval_seconds <= 300:
        parser.error('--interval-seconds must be between 2 and 300')
    return args


def matching_runner_pids(run_id: str) -> list[int]:
    matches: list[int] = []
    for process in psutil.process_iter(['pid', 'cmdline']):
        try:
            command = ' '.join(process.info.get('cmdline') or [])
            if RUNNER_NAME in command and run_id in command:
                matches.append(int(process.info['pid']))
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return sorted(matches)


def ledger_snapshot(database: Path) -> dict[str, object]:
    uri = database.resolve().as_uri() + '?mode=ro'
    with sqlite3.connect(uri, uri=True, timeout=5.0) as connection:
        connection.execute('PRAGMA query_only=ON')
        run_id_row = connection.execute(
            'SELECT value FROM run_metadata WHERE key=?', ('run_id',)
        ).fetchone()
        if run_id_row is None:
            raise RuntimeError('run_id missing from ledger metadata')
        counts = dict(connection.execute(
            'SELECT status, COUNT(*) FROM tasks GROUP BY status'
        ).fetchall())
        totals = connection.execute(
            '''
            SELECT
                COALESCE(SUM(files_read), 0),
                COALESCE(SUM(minute_rows_read), 0),
                COALESCE(SUM(presence_rows), 0),
                COALESCE(SUM(gap_rows), 0)
            FROM tasks
            WHERE status='committed'
            '''
        ).fetchone()
        active = connection.execute(
            '''
            SELECT ticker, worker_pid, started_at_utc
            FROM tasks
            WHERE status='running'
            ORDER BY ticker
            '''
        ).fetchall()
    return {
        'run_id': str(run_id_row[0]),
        'counts': counts,
        'total': sum(int(value) for value in counts.values()),
        'files_read': int(totals[0]),
        'minute_rows_read': int(totals[1]),
        'presence_rows': int(totals[2]),
        'gap_rows': int(totals[3]),
        'active': active,
    }


def render(snapshot: dict[str, object], database: Path) -> bool:
    now = datetime.now(UTC)
    counts = snapshot['counts']
    total = int(snapshot['total'])
    committed = int(counts.get('committed', 0))
    pending = int(counts.get('pending', 0))
    running = int(counts.get('running', 0))
    failed = int(counts.get('failed', 0))
    runner_pids = matching_runner_pids(str(snapshot['run_id']))
    ledger_age = max(0.0, now.timestamp() - database.stat().st_mtime)
    active_rows = snapshot['active']
    active_text = ','.join(str(row[0]) for row in active_rows) or 'n/a'
    status = 'running' if runner_pids else 'stopped'
    print(
        f'[{now.isoformat()}] status={status} stage=ledger_ticker_session_audit '
        f'progress={committed}/{total} pending={pending} running={running} '
        f'failed={failed} ledger_age_sec={ledger_age:.1f} '
        f'runner_pids={runner_pids or "n/a"} active={active_text} '
        f'files={snapshot["files_read"]} rows={snapshot["minute_rows_read"]} '
        f'presence_rows={snapshot["presence_rows"]} gaps={snapshot["gap_rows"]}',
        flush=True,
    )
    if not runner_pids and running:
        print('WARNING: no live runner; resume is required.', flush=True)
    return committed == total and pending == 0 and running == 0


def main() -> int:
    args = parse_args()
    database = args.run_root / '00_control' / 'run_state.sqlite'
    if not database.is_file():
        raise FileNotFoundError(f'Ledger not found: {database}')
    while True:
        try:
            terminal = render(ledger_snapshot(database), database)
        except (OSError, sqlite3.Error) as exc:
            print(
                f'[{datetime.now(UTC).isoformat()}] status=ledger_read_retry '
                f'error={type(exc).__name__}:{exc}',
                flush=True,
            )
            terminal = False
        if not args.watch or terminal:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == '__main__':
    raise SystemExit(main())
