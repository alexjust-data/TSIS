# CHANGELOG - 03_TSIS_Lab

## 2026-07-23 | physical data plane root aligned to G

- Updated Lab responsibility map and `LOCAL_RULES.md` to reference `G:/TSIS/data` as the active physical data plane for heavy outputs, materializations, runs and 1m raw/repair lineage checks.
- Role preserved: Lab governs experiments and validation; it does not own physical market data semantics.

## 2026-07-22 | root path migration | lab root moved to 03_TSIS_Lab

- Canonical root is now `C:/TSIS_Data/03_TSIS_Lab`.
- Legacy root `C:/TSIS_Data/00_TSIS_Lab` must resolve through `C:/TSIS_Data/PATH_MIGRATION_2026_07_22.md`.
- Role preserved: transversal research experiment lab for contracts, registries, templates, evidence and validation.

