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
- builder declares independent consumption legality rules;
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
- `post_event_review` rows are marked `consumption_legality = decision_safe`;
- `consumption_legality` is missing or outside the allowed taxonomy;
- any linked market state fails its own leakage gates.

## 4. Required Quality Checks

The validator must emit:

- row count;
- event family counts;
- state role counts;
- consumption legality counts;
- decision timestamp range;
- linked market state count;
- `state_quality_state` distribution;
- label/outcome inline scan result;
- consumer-gate counts;
- leakage failure counts.

## 5. Required Consumer Gates

Every v0.1 materialized row must expose:

```text
consumption_legality
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
post_event_review -> consumption_legality != decision_safe
```

## 6. Required Adversarial Tests

Future tests must inject or simulate:

- inline outcome column;
- inline label column;
- inline reward column;
- event cutoff after decision timestamp;
- `post_event_review` row marked for ML features;
- `post_event_review` row marked `consumption_legality = decision_safe`;
- row with `valid_for_ml_feature_candidate = true` and `consumption_legality != decision_safe`;
- missing event window id;
- missing linked market state id.

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
dataset_id: event_state_table_v0_1_candidate
status: controlled_candidate_not_promoted
dataset: E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/
manifest: E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
summary: E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv
rows: 50
tickers: 9
event_windows: 50
pre_event_rows: 25
post_event_review_rows: 25
valid_for_pattern_discovery_rows: 50
valid_for_ml_feature_candidate_rows: 0
valid_for_rl_state_candidate_rows: 0
full_universe_claim_rows: 0
state_quality_counts: {"event_state_review_microstructure_seed_only":50}
```

Executable evidence:

```text
tests/data_foundation_outputs/test_event_state_table_contract.py
```

The candidate validator proves linked `market_state_id`, state-role separation, current implicit consumption boundary,
label/outcome/reward inline prohibition, state cutoff legality, unique
`event_state_id`, manifest presence and non-promotion flags. It does not
promote the official table and does not allow direct ML/RL/backtest/execution
use. Future official/candidate builders must emit `consumption_legality` explicitly.

## Evidencia 2026-07-05 - Event State Intradia Quote-Guarded Controlado

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_event_state_intraday_quote_guarded_candidate.py
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
joined_event_state_rows = 15
event_count = 5
state_role_counts = at_event: 5, post_event_review: 5, pre_event: 5
consumption_legality_counts = not_emitted_by_current_controlled_candidate_v0_1
validator_status = passed
full_universe_claim_rows = 0
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
execution_truth_rows = 0
```

Lectura correcta: esta evidencia no promociona `event_state_table_v0_1` oficial. Es un candidato controlado intradia para pattern discovery y para construir outcomes separados.
