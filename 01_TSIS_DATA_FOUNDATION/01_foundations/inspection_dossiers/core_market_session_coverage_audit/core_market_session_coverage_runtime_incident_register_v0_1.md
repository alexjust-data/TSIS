# Core Market Session Coverage Runtime Incident Register v0.1

## CSCA-20260822-001 - Blocking heartbeat reader on Windows

- Observed at: 2026-08-22T14:11:27Z.
- Run: 20260822_core_market_session_coverage_daily_1m_quotes_v0_2.
- State at interruption: 471 committed, 4.352 pending and BANL marked running.
- Failure: WinError 5 while replacing heartbeat.json atomically.
- Data impact: none; no RAW or committed task artifact failed.
- Evidence: 00_control/incidents/20260822T141127Z_heartbeat_replace_permission_error.log in the run root.
- Root cause: the original PowerShell monitor did not share delete/replace access while reading heartbeat.json.
- Control added: monitor_core_market_session_coverage_nonblocking.ps1 opens heartbeat and final manifest with FileShare ReadWrite plus Delete.
- Recovery: identical hash-bound run resumed with PID 523276; checkpoint adoption reached 478 committed at 2026-08-22T14:27:03Z.
- Inherited rule: do not use the original blocking monitor on a live session-coverage run.
