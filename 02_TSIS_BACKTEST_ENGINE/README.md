# 02_TSIS_BACKTEST_ENGINE

Status: implementation shell; no production backtest engine is authorized yet.

This module is the future implementation area for the professional TSIS backtest engine.

It is not the Data Foundation, not the raw audit archive and not the source of truth for dataset certification.

## Required Inputs

- `C:/TSIS_Data/PATH_MIGRATION_2026_07_22.md`
- `C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/arquitectura_backtester_profesional_TSIS.md`
- future promoted `TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations`
- `E:/TSIS/data/README.md`

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