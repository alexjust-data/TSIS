# AGENTS - 02_TSIS_BACKTEST_ENGINE

Before making changes here, read:

1. `C:/TSIS_Data/PATH_MIGRATION_2026_07_22.md`
2. `C:/TSIS_Data/PROJECT_OPERATING_SYSTEM.md`
3. `C:/TSIS_Data/PROJECT_RULES.md`
4. `C:/TSIS_Data/VERSIONING_STANDARDS.md`
5. `C:/TSIS_Data/RESEARCH_PHILOSOPHY.md`
6. `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`
7. `C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/02_NOTAS/arquitectura_backtester_profesional_TSIS.md`
8. `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/README.md`
9. `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/README.md`
10. `G:/TSIS/data/README.md`
11. `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/backtest_engine_boundary_and_data_plane_v0_1.md`

## Operational Boundary

Do not implement a production backtest engine until the architecture contract is promoted. Experimental vertical slices must declare scope, inputs, outputs, deterministic assumptions, data view, cost/fill model and validation gates.

The module boundary is:

```text
00_CTO/14_BACKTEST_ENGINE
= architecture, decisions and governance

02_TSIS_BACKTEST_ENGINE
= executable technical product
```

`00_CTO` defines what must exist and why. `02_TSIS_BACKTEST_ENGINE` implements and executes.

## Data Rule

The current physical data provider root for this module is:

```text
G:/TSIS/data
```

The physical root is not the semantic authority. Data semantics, dataset contracts, price views, corporate-action policy, quality gates and consumption permissions remain governed by `01_TSIS_DATA_FOUNDATION` and especially `01_foundations`.

Never copy ambiguous RAW market data into this module. The only data-adjacent artifacts allowed inside the engine are dataset manifests, resolution manifests, run-local extracts, temporary caches and experiment-derived outputs, each with explicit lineage.

## Lab Boundary

`02_TSIS_BACKTEST_ENGINE/experiments` contains executable engine experiments. `03_TSIS_Lab/04_experiments` contains scientific governance, authorization, evidence interpretation and validation decisions.

Relationship:

```text
TSIS Lab experiment -> authorizes
Backtest Engine experiment -> executes
TSIS Lab -> interprets and validates
Knowledge Layer -> preserves the conclusion
```
