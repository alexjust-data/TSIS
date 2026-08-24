# Graphify refresh queue

## GFQ-20260821-SCREENER-DATA-DECISION-001

- Status: `pending`
- Date: `2026-08-21`
- Severity: `MEDIUM`
- Scope: frozen Massive + SEC source contract for the future 04:01 ET
  price/market-cap screener, plus governed deferral of 1m remediation until
  complete Trades and actual screener selections exist.
- Affected file:
  `MASSIVE_SEC_SCREENER_DATA_DECISION_v0_1.md`.
- Leaf target: future governed `04_TSIS_SCREENERS` leaf.
- Pending reason: the active root graph predates the August 2026 acquisition
  work and was not rebuilt during the ongoing core-market alignment audit.
- Closeout: build and diagnose the screener leaf after acquisition contracts
  and data are complete, then merge it into the next controlled root refresh.
