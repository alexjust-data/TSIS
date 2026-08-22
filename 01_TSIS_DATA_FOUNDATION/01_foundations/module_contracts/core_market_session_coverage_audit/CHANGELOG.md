# Changelog

## 0.2.0 - 2026-08-22

- Added contract-bound deferred families without reading their live source state.
- Added an explicit three-family comparison mode for Daily, 1m and Quotes while Trades remains in recovery.
- Separated deferred families from source-pending families in presence, windows and closeout artifacts.

## 0.1.0 — 2026-08-22

- Added corrected `session_date_et` coverage semantics for the four core market RAW families.
- Added transactional per-ticker checkpoints, controlled stop/resume and hash-bound operational artifacts.
- Added factual absence, diagnostic gap classes and explicit unverified leading/trailing boundaries.
- Certified the production-equivalent probe and the detached stop/resume smoke.
