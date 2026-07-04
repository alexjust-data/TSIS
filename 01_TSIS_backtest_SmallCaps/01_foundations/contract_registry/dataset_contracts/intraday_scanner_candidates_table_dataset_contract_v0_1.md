# Intraday Scanner Candidates Table Dataset Contract v0.1

Dataset identity:

```text
intraday_scanner_candidates_table_v0_1
```

Status:

```text
dataset_contract_candidate_controlled_replay_not_promoted
```

## Purpose

Provides an intraday candidate denominator for smallcap/microcap in-play
research by detecting first +50% moves from `ohlcv_1m` in extended hours.

## Authority

Semantic authority:

```text
01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
```

Schema authority:

```text
01_foundations/canonical_schemas/outputs/intraday_scanner_candidates_table_schema_contract.md
```

## Source Roots

```text
E:/TSIS/data/ohlcv_1m
E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

## Promotion State

Controlled replay evidence exists. Official E-root promoted dataset does not
exist yet.

Controlled replay:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
```

## Prohibited Claims

```text
market_state
event_state
strategy_signal
ML/RL-ready state
execution truth
full universe
official promoted table
```
