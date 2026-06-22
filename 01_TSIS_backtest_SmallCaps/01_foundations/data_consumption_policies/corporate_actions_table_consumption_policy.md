# Corporate Actions Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
corporate_actions_table_v0_1
```

## 2. Permitted Meaning

Consumers may use this table to:

- identify split dates and split ratios;
- identify dividend ex-dates and cash amounts;
- identify ticker-change events;
- build event/context flags;
- explain discontinuities;
- support adjusted-price pipelines.

## 3. Prohibited Meaning

Consumers must not use this table to:

- infer alpha by itself;
- replace raw or adjusted price views;
- silently repair OHLCV;
- assert full economic identity continuity after ticker change;
- collapse `reference` and `additional` without a declared dedup policy.

## 4. Consumer Classes

Permitted:

- `data_quality_report`
- `dataset_certification_matrix`
- `event_engine`
- `research_only`
- `forensic_only`

Conditionally permitted:

- `master_daily_table`
- `master_intraday_bar_table`
- `backtest_core`
- `backtest_extended`
- `ml_flagged`

Conditions:

- preserve `source_system`;
- preserve `source_priority`;
- preserve `within_instrument_valid_window`;
- do not treat `additional` as primary when `reference` exists;
- prevent leakage when building labels/features.

Restricted:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 5. Required Downstream Fields

Downstream tables using corporate actions must preserve or derive traceably:

- `action_type`;
- `action_date`;
- `source_system`;
- `source_event_id`;
- split/dividend/ticker-change payload fields relevant to the use;
- source build id;
- schema version.

## 6. Final Rule

Corporate actions are context and adjustment lineage.

They are not price, not signal and not final continuity truth.

