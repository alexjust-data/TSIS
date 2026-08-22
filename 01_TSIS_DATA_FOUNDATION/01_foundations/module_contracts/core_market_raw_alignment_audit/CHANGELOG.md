# Core Market RAW Alignment Audit Changelog

## 2026-08-22 | Recovery handoff and session-date correction

- Added the v0.3 institutional handoff and a run-local recovery pointer for
  deterministic continuation after a host or power interruption.
- Preserved the physical/schema PASS for completed Daily and 1m tasks but
  invalidated the direct 1m/Daily raw `date` comparison as a session-alignment
  result because 1m uses UTC calendar dates.
- Recorded confirmed UTC rollover cases, real FCEL/DJCO gap evidence and the
  production-equivalent probe-first route to an exact ET session gap ledger.
- Kept all four `G:` roots read-only and deferred the additional 1m scan until
  the active Quotes and Trades readers have closed.

## 2026-08-21 | Adaptive Quotes workers for the active full audit

- Replaced only the original sequential `quotes_` worker with two
  transactionally claimed workers; the original `ohlcv_1m` and Trades workers
  remained alive and retained their PIDs.
- Added an automatic third Quotes worker gated on 4,824/4,824 committed 1m
  tasks, plus separate pre-manifest, PID, heartbeat, logs and terminal manifest.
- Concurrent claim and exact recovery tests pass 6/6 with zero duplicate
  ticker-attempt claims; all four RAW roots remain read-only.
- Documented the live topology and recovery route in
  `quotes_worker_acceleration_runbook_v0_1.md`.

## 2026-08-21 | Initial governed auditor

- Established the read-only four-family physical and exact ticker-date audit.
- Closed the production-equivalent v0.3 probe and authorized the full scan
  separately through the existing human gate.
