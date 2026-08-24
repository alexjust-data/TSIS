# Graphify Refresh Queue

## Pending
- date: 2026-08-24
  scope: OHLCV 1m Full audit closeout, denominator semantics and temporal incompleteness
  files: `analyze_ohlcv_1m_full_audit.py`, full readout, README, changelogs and evidence assets
  severity: HIGH
  leaf_target: Data Foundation core market family download audit and minute inspection evidence
  reason: official Graphify leaf refresh deferred until Daily and Quotes Full closeouts can be indexed in one coherent rebuild


- date: 2026-08-23
  scope: new independent Daily, 1m and Quotes download-evidence audit
  files: `scripts/core_market_family_download_audit/*`, family audit contract and schema v0.1
  severity: HIGH
  leaf_target: Data Foundation core market raw/session coverage governance
  reason: implementation and production-equivalent probes must close before the official semantic leaf can be refreshed

