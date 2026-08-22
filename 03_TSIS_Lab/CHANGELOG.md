# CHANGELOG - 03_TSIS_Lab

## 2026-08-17 | Wake-up RTH full candidate run and blind-panel repair

- Completed the development candidate scan at 2,400/2,400 targets, 4,447
  candidates, zero failures and 159 typed source-unavailable sessions.
- Invalidated the initial blind panel after detecting 240/240 rows in
  `CLOSE_240M_PLUS`; the candidate pool remains valid.
- Replaced lexical truncation with deterministic RTH-balanced sampling, added
  input-lineage and temporal-coverage checks, staging-before-promotion repair
  and a dedicated monitor.
- Passed six unit tests and the repair probe at 25/25 checks with all three RTH
  buckets represented. The full panel-only rebuild remains human-launched.

## 2026-08-17 | Wake-up RTH oracle calibration probe certified

- Added `EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001` with binding-neutral
  candidate/control search, blind panel, price-path-free gallery, two-reviewer
  aggregation, adjudication, WUL evidence and terminal validation.
- Passed five unit tests, one production-equivalent target per D1..D4 and
  terminal validation 20/20; final preflight covers exactly 2,400 development
  targets.
- Corrected the legacy 23,400 versus 23,399 cardinality discrepancy, replaced
  non-global `target_ordinal` with a composite target identity and hardened
  resume against mixed config/code/schema/identity.
- Full execution remains a human-launched long operation. D07, B-03, A/B
  comparison and both OOS paths remain closed.

## 2026-07-23 | physical data plane root aligned to G

- Updated Lab responsibility map and `LOCAL_RULES.md` to reference `G:/TSIS/data` as the active physical data plane for heavy outputs, materializations, runs and 1m raw/repair lineage checks.
- Role preserved: Lab governs experiments and validation; it does not own physical market data semantics.

## 2026-07-22 | root path migration | lab root moved to 03_TSIS_Lab

- Canonical root is now `C:/TSIS_Data/03_TSIS_Lab`.
- Legacy root `C:/TSIS_Data/00_TSIS_Lab` must resolve through `C:/TSIS_Data/PATH_MIGRATION_2026_07_22.md`.
- Role preserved: transversal research experiment lab for contracts, registries, templates, evidence and validation.

