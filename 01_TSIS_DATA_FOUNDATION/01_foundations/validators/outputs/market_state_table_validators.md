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

## 7. Current Expected Official v0.1 Counts

Because the official institutional table is not materialized:

```text
expected_parquet_rows: 0
official_materialized: false
official_builder_implemented: false
```

## 8. Current Controlled Candidate Evidence

As of `2026-06-29`, a controlled candidate exists:

```text
dataset_id: market_state_table_v0_1_candidate
status: controlled_candidate_not_promoted
dataset: E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/
manifest: E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
summary: E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv
rows: 50
tickers: 9
event_windows: 50
valid_for_event_context_candidate_rows: 50
valid_for_ml_feature_candidate_rows: 0
valid_for_rl_state_candidate_rows: 0
full_universe_claim_rows: 0
state_quality_counts: {"state_review_microstructure_seed_only":50}
```

Executable evidence:

```text
tests/data_foundation_outputs/test_market_state_table_contract.py
```

The candidate validator proves schema gates, prohibited-prefix absence,
as-of legality, unique `market_state_id`, manifest presence and non-promotion
flags. It does not promote the official table and does not allow direct
ML/RL/backtest/execution use.


As of `2026-07-05`, an additional intraday controlled candidate exists:

```text
dataset_id: market_state_table_v0_1_candidate
status: controlled_candidate_not_promoted
dataset: C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
manifest: C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
summary: C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_summary_v0_1_candidate_intraday_quote_guarded_controlled.csv
rows: 10835
tickers: 3
valid_for_event_context_candidate_rows: 0
valid_for_ml_feature_candidate_rows: 0
valid_for_rl_state_candidate_rows: 0
full_universe_claim_rows: 0
execution_truth_rows: 0
intraday_as_of_after_decision_rows: 0
bar_end_decision_timestamp_mismatch_rows: 0
state_quality_counts: {"state_review_scoped_intraday_component":10835}
validator_status: passed
```

Executable evidence:

```text
tests/data_foundation_outputs/test_market_state_intraday_quote_guarded_candidate_builder.py
python -m pytest tests/data_foundation_outputs/test_market_state_intraday_quote_guarded_candidate_builder.py -q
```

This candidate validator proves the closed-1m-bar timestamp rule, prohibited-prefix absence, unique `market_state_id`, no full-universe claim and non-promotion flags for the intraday quote-guarded controlled scope.
