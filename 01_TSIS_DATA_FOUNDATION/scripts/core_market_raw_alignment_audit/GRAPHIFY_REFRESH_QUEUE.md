# Graphify refresh queue

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
