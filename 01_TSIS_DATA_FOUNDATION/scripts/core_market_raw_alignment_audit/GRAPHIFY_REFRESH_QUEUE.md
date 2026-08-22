# Graphify refresh queue

## GFQ-20260822-TRADES-ACCELERATOR-001

- Status: `pending`
- Date: `2026-08-22`
- Severity: `HIGH`
- Scope: suspend the single original Trades worker, preserve its active ticker,
  claim pending Trades tasks atomically with six workers, then resume the
  original worker for normal parent closeout.
- Affected files: `accelerate_trades_workers.py`,
  `run_trades_accelerator.ps1`, `monitor_trades_accelerator.ps1`,
  `stop_trades_accelerator.ps1`, focused tests and this README.
- Leaf target: Data Foundation core-market raw-alignment audit tooling.
- Pending reason: the governed raw-alignment and session-coverage runs are live;
  rebuilding Graphify would add avoidable I/O during those operations.
- Closeout: refresh and diagnose the tooling leaf after both runs close.

## GFQ-20260821-QUOTES-SCALEOUT-001

- Status: `pending`
- Date: `2026-08-21`
- Severity: `MEDIUM`
- Scope: safe runtime scale-out from three to six concurrent `quotes_` audit
  workers while preserving the active Trades worker.
- Affected files: `scale_out_quotes_workers.py`,
  `monitor_quotes_scaleout.ps1` and `test_quotes_scaleout.py`.
- Leaf target: Data Foundation core-market raw-alignment audit tooling.
- Pending reason: no Graphify rebuild is run while the long core-market audit is
  active.
- Closeout: refresh and diagnose the affected tooling leaf after the audit
  reaches a terminal state.
