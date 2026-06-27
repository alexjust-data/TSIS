# Event State Table Validators `v0_1`

## 1. Scope

This validator contract governs the future:

```text
event_state_table_v0_1
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
- `market_state_table` contract exists;
- builder config exists;
- builder declares event source;
- builder declares state role rules;
- builder declares label separation policy.

## 3. Hard Validation Checks

The build must fail if:

- `event_state_id` is duplicated;
- `event_window_id` is null;
- `market_state_id` is null;
- `decision_timestamp_utc` is null;
- `state_cutoff_utc` is after `decision_timestamp_utc`;
- any prohibited column family appears;
- any outcome, label or reward value is inlined;
- `post_event_review` rows are marked as ML feature candidates;
- any linked market state fails its own leakage gates.

## 4. Required Quality Checks

The validator must emit:

- row count;
- event family counts;
- state role counts;
- decision timestamp range;
- linked market state count;
- `state_quality_state` distribution;
- label/outcome inline scan result;
- consumer-gate counts;
- leakage failure counts.

## 5. Required Consumer Gates

Every v0.1 materialized row must expose:

```text
valid_for_pattern_discovery
valid_for_ml_feature_candidate
valid_for_backtest_context_candidate
valid_for_rl_state_candidate
valid_for_rl_training_direct
valid_for_execution_context_candidate
valid_for_execution_simulator_direct
contains_future_information_without_event_filter
requires_asof_filter
full_universe_claim
execution_truth
```

Direct RL training and execution simulation default to false unless a later
contract explicitly promotes them:

```text
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
execution_truth = false
```

## 6. Required Adversarial Tests

Future tests must inject or simulate:

- inline outcome column;
- inline label column;
- inline reward column;
- event cutoff after decision timestamp;
- `post_event_review` row marked for ML features;
- missing event window id;
- missing linked market state id.

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
