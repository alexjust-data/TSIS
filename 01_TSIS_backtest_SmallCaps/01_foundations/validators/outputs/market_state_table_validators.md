# Market State Table Validators `v0_1`

## 1. Scope

This validator contract governs the future:

```text
market_state_table_v0_1
```

Current status:

```text
contract_defined_not_materialized
```

## 2. Required Pre-Materialization Checks

Before any parquet output is written, validators must confirm that:

- schema contract exists;
- dataset contract exists;
- consumption policy exists;
- registry entry exists;
- builder config exists;
- builder declares materialization scope;
- builder declares component source versions;
- builder declares cutoff/as-of rules.

## 3. Hard Validation Checks

The build must fail if:

- `market_state_id` is duplicated;
- `decision_timestamp_utc` is null;
- any component as-of timestamp is after `decision_timestamp_utc`;
- any prohibited column family appears;
- any feature column is un-namespaced;
- `outcomes_table_v0_1` values are inlined;
- `short_context_table_v0_1` is used as borrow/locate/SSR evidence;
- `regime_context_table_v0_1` same-session close aggregate is used before it is
  legally available;
- `microstructure_features_table_v0_1` is promoted as full-universe state;
- `master_intraday_bar_table_v0_1` is promoted as full-universe intraday state.

## 4. Required Quality Checks

The validator must emit:

- row count;
- instrument count;
- decision timestamp range;
- state horizon counts;
- state scope counts;
- `state_quality_state` distribution;
- component availability counts;
- consumer-gate counts;
- component manifest hash bundle summary;
- leakage failure counts;
- prohibited column scan result;
- namespace scan result.

## 5. Required Consumer Gates

Every v0.1 materialized row must expose:

```text
valid_for_event_context_candidate
valid_for_ml_feature_candidate
valid_for_backtest_context_candidate
valid_for_rl_state_candidate
valid_for_rl_training_direct
valid_for_execution_simulator_direct
contains_future_information_without_event_filter
requires_asof_filter
full_universe_claim
execution_truth
```

Direct RL training and execution truth default to false unless a later contract
explicitly promotes them:

```text
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
execution_truth = false
```

## 6. Required Adversarial Tests

Future tests must inject or simulate:

- future as-of component;
- inline outcome column;
- inline reward column;
- un-namespaced feature;
- duplicate state id;
- same-session regime leakage;
- short-context-as-borrow misuse.

The validator must fail these cases.

## 7. Current Expected v0.1 Counts

Because the table is not materialized:

```text
expected_parquet_rows: 0
materialized: false
builder_implemented: false
```

The current tests may validate contract consistency only. They must not claim
parquet validation.
