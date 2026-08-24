# Changelog

## 2026-08-24 | OHLCV 1m no-RTH forensic decision

- Clarified that the 14,302 rows are present extended-session observations,
  not missing rows.
- Crossed the 5,238 no-RTH cases with Daily and legacy RTH Trades and retained
  eight high-confidence local inconsistency candidates without claiming
  current-provider parity.
- Froze the operational decision: no 1m redownload or repair before complete
  Trades and the daily screener; reconstruct a versioned derived view only for
  screener-selected cases that materially require it.

## 2026-08-24 | OHLCV 1m Full audit closeout

- Added a reproducible deep analyzer and hash-bound evidence assets for the
  completed 4,824-ticker `ohlcv_1m` audit.
- Reconciled 5,238 observed ticker-session dates without RTH, including a
  deterministic 2025/2026 sample and the prior narrower 4,264-case result.
- Certified present-file technical evidence while recording the archive as
  temporally incomplete after March 2026 relative to the 2026-08-20 scope.

## 2026-08-23 | Production-equivalent probes

- Certified the Daily and 1m production-equivalent probes before Full launch.
- Kept Quotes behind its independent probe gate at that point in the sequence.
