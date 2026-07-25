# 02_TSIS_BACKTEST_ENGINE

Status: implementation shell; no production backtest engine is authorized yet.

This module is the future implementation area for the professional TSIS backtest engine.

It is not the Data Foundation, not the raw audit archive, not the source of truth for dataset certification and not the CTO architecture authority.

## Current Decision

The active boundary decision is documented in:

- `docs/00_system/backtest_engine_boundary_and_data_plane_v0_1.md`

Summary:

```text
00_CTO/14_BACKTEST_ENGINE
= architecture, decisions and governance

01_TSIS_DATA_FOUNDATION
= governed data semantics and contracts

G:/TSIS/data
= current physical data provider root

02_TSIS_BACKTEST_ENGINE
= executable engine, simulation, accounting, ledgers and reports

03_TSIS_Lab
= scientific governance, validation and interpretation
```

Rule:

```text
00_CTO defines what must exist and why.
02_TSIS_BACKTEST_ENGINE implements and executes.
```

## Required Inputs

- `C:/TSIS_Data/PATH_MIGRATION_2026_07_22.md`
- `C:/TSIS_Data/PROJECT_OPERATING_SYSTEM.md`
- `C:/TSIS_Data/PROJECT_RULES.md`
- `C:/TSIS_Data/VERSIONING_STANDARDS.md`
- `C:/TSIS_Data/RESEARCH_PHILOSOPHY.md`
- `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`
- `C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/02_NOTAS/arquitectura_backtester_profesional_TSIS.md`
- future promoted `TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/README.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations`
- `G:/TSIS/data/README.md`

## Boundary

The engine should own:

- simulation input adapters;
- deterministic clock and event loop;
- online state consumption;
- strategy / decision policy interfaces;
- portfolio construction;
- pre-trade and post-trade risk hooks;
- order management;
- execution simulation / broker adapters;
- accounting, ledgers, reports and validation outputs.

It must consume governed Data Foundation contracts. It must not redefine raw data quality, price semantics, corporate-action policy, dataset promotion or data immutability.

## Data Policy

Do not duplicate market data inside this module.

The engine may keep only:

```text
dataset manifests
resolution manifests
run-local extracts
temporary caches
outputs derived from an experiment
```

No artifact under `02_TSIS_BACKTEST_ENGINE` can be treated as RAW source of truth. Every run must declare logical dataset identity, physical source root, price view, quality policy, fill model and lineage.

## Lab Experiment Boundary

```text
02_TSIS_BACKTEST_ENGINE/experiments
= executable engine experiments

03_TSIS_Lab/04_experiments
= scientific governance of experiments
```

Relationship:

```text
TSIS Lab experiment
        -> authorizes
Backtest Engine experiment
        -> executes
TSIS Lab
        -> interprets and validates
Knowledge Layer
        -> preserves the conclusion
```

## Current Physical Scaffold

The current scaffold is intentionally minimal:

```text
configs/datasets
configs/universes
configs/strategies
configs/execution
configs/experiments
docs/00_system
src/tsis_backtest/common
src/tsis_backtest/dataset_resolution
src/tsis_backtest/temporal
src/tsis_backtest/universe
src/tsis_backtest/loaders
src/tsis_backtest/strategies/open_to_close
src/tsis_backtest/execution
src/tsis_backtest/portfolio
src/tsis_backtest/engines/tabular
src/tsis_backtest/metrics
src/tsis_backtest/validation
src/tsis_backtest/experiments
src/tsis_backtest/reports
notebooks/00_data_inspection
notebooks/01_universe_research
notebooks/02_single_day_backtest
notebooks/03_validation
experiments/EXP_0001_INPLAY_OPEN_TO_CLOSE
outputs/EXP_0001_INPLAY_OPEN_TO_CLOSE
tests/unit
tests/integration
tests/hand_calculated_cases
```

Future folders such as `orders`, `engines/vectorized`, `engines/event_driven`, `configs/portfolios`, `configs/validation`, richer docs, richer tests and `scripts/` are valid only when a promoted construction phase or concrete implementation task requires them.

## Verdict

```text
Ubicar el motor dentro de C:/TSIS_Data
= correcto

Crear 02_TSIS_BACKTEST_ENGINE
= correcto

Conservar 00_CTO/14_BACKTEST_ENGINE
= correcto

Usar ambos para lo mismo
= incorrecto
```
