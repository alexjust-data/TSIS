# CHANGELOG - 02_TSIS_BACKTEST_ENGINE

## 2026-07-23 | boundary and data-plane decision recorded

- Recorded the module boundary: `00_CTO/14_BACKTEST_ENGINE` defines architecture, decisions and governance; `02_TSIS_BACKTEST_ENGINE` implements and executes.
- Recorded `G:/TSIS/data` as the current physical data provider root for backtest-engine work while preserving `01_TSIS_DATA_FOUNDATION` as the semantic/data-contract authority.
- Clarified that `02_TSIS_BACKTEST_ENGINE/experiments` contains executable engine experiments, while `03_TSIS_Lab/04_experiments` contains scientific governance, authorization, interpretation and validation.
- Documented that raw market data must not be duplicated inside the engine; only manifests, run-local extracts, temporary caches and experiment-derived outputs are allowed with explicit lineage.
- Added `docs/00_system/backtest_engine_boundary_and_data_plane_v0_1.md` as the local decision record.

## 2026-07-23 | scaffold directories created

- Created the initial implementation scaffold for configs, docs, `src/tsis_backtest`, notebooks, experiments, outputs and tests.
- Added placeholder `.gitkeep` files so the empty scaffold remains versionable.
- Added `pyproject.toml` with a minimal src-layout package/test configuration.
- No production engine implementation, dataset consumption, run output or backtest execution was introduced.

## 2026-07-22 | module shell created

- Created the canonical implementation shell for the future TSIS professional backtest engine.
- Boundary preserved: architecture/theory remains under `00_CTO/14_BACKTEST_ENGINE`; Data Foundation remains under `01_TSIS_DATA_FOUNDATION`.
- No engine implementation, run output, dataset consumption or production backtest is authorized by this shell.
