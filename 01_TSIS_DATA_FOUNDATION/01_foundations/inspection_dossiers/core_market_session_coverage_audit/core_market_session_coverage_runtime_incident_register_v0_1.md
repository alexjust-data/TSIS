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

## CSCA-20260822-002 - FileShare.Delete was insufficient

- Observed at: 2026-08-22T14:50:43Z.
- Run: 20260822_core_market_session_coverage_daily_1m_quotes_v0_2.
- Durable state: 814 committed, 4.009 pending and CCRD marked running.
- Failure: a second WinError 5 while replacing heartbeat.json atomically.
- Data impact: none; the ledger and committed ticker manifests remained valid.
- Evidence: heartbeat.json.523276.1787410243908681300.partial in 00_control.
- Refined cause: the first non-blocking monitor still called Test-Path before opening the file with delete sharing; that metadata/read race was removed.
- Recovery: identical hash-bound run resumed with PID 540532.

## CSCA-20260822-003 - Heartbeat reads prohibited for the live run

- Observed at: 2026-08-22T16:36:24Z.
- Run: 20260822_core_market_session_coverage_daily_1m_quotes_v0_2.
- Durable state: 827 committed, 3.996 pending and CDNA marked running.
- Failure: a third WinError 5 coincident with a heartbeat read, despite FileShare.Delete and without Test-Path.
- Data impact: none; zero failed tasks and all 827 committed manifests remained reusable.
- Evidence: 00_control/incidents/20260822T163624Z_heartbeat_replace_permission_error.log, SHA-256 EE28F5CE7B28F368B8E1D87219FCF640320E9DA58E495A63D736BC6FF5715E94.
- Final runtime control: no process may open heartbeat.json while this audit is live. monitor_core_market_session_coverage_nonblocking.ps1 now delegates to monitor_core_market_session_coverage_ledger.py, which reads run_state.sqlite in read-only mode and discovers the runner PID independently.
- Recovery: identical hash-bound run resumed with PID 541572 and reached 829 committed at 2026-08-22T16:42:28Z.
- Inherited rule: live monitoring must use the SQLite-ledger monitor. The original heartbeat monitor remains part of the frozen run hash only and must not be executed.
