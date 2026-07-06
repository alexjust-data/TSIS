# Outcomes Table Validators `v0_1`

## 1. Scope

Dataset:

```text
outcomes_table_v0_1
```

Root:

```text
E:/TSIS/data/data_foundation_outputs/outcomes_table
```

## 2. Governed Artifacts

- dataset contract: `01_foundations/contract_registry/dataset_contracts/outcomes_table_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/outcomes_table_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/outcomes_table_consumption_policy.md`
- materializer: `scripts/materialize_outcomes_table.py`

## 3. Unit Of Validation

```text
event_window_id + outcome_horizon + price_view
```

## 4. Minimum Validators

### 4.1 Artifact Presence

Must check:

- parquet dataset `outcomes_table_v0_1.parquet`;
- `_outcomes_table_manifest_v0_1.json`;
- `_outcomes_table_summary_v0_1.csv`;
- all contract paths declared in manifest.

### 4.2 Schema Conformity

Must check:

- required columns exist;
- `schema_version = outcomes_table_v0_1`;
- `quality_policy_version = outcomes_table_policy_v0_1`;
- `materialization_scope = halt_next_session_daily_outcomes_v0_1`;
- `outcome_horizon = next_session_regular_daily`;
- allowed `price_view` values only;
- one build id per materialization.

### 4.3 Grain Integrity

Hard failures:

- duplicate `outcome_id`;
- duplicate `event_window_id + outcome_horizon + price_view`;
- missing event or outcome date;
- missing price view;
- row count not equal to `next_session_regular event windows * 3`.

### 4.4 Source Reconciliation

Must check:

- source `event_windows_table_v0_1` SHA matches manifest;
- source `master_daily_table_v0_1` tree hash matches manifest;
- every v0.1 row comes from `window_role = next_session_regular`;
- every v0.1 row has a source daily event row;
- missing source daily outcome rows are preserved as review rows and counted in
  manifest validations;
- three price views exist for every source event window.

### 4.5 Outcome Semantics

Must check:

- post-event rows are marked `contains_post_event_information = true`;
- rows are marked `prohibited_as_pre_event_feature = true`;
- `valid_for_rl_reward_candidate = false`;
- ML label gate is true only for `good_daily_outcome`;
- return fields are null for rows without valid event close/outcome prices;
- threshold labels are false when a row is not a valid label candidate.

### 4.6 Price-View Integrity

Must check:

- event side and outcome side share the same `price_view`;
- allowed price views are exactly `daily_raw`, `split_normalized`, `adjusted`;
- no consumer may mix raw execution semantics with adjusted daily labels.

## 5. Output Fields

A validator must emit:

- run id;
- dataset id;
- rows checked;
- rows by price view;
- outcome quality counts;
- valid label rows;
- review rows;
- duplicate key groups;
- source hashes;
- source build ids;
- evidence artifacts path.

## 6. Final Rule

Passing this validator proves that daily post-event labels are structurally
coherent, source-linked and separated from pre-event features.

It does not prove intraday execution realism, RL reward validity, or final
market-state readiness.

## 7. Extension Candidate Intradia 1m Quote-Guarded Controlada

Validator scope adicional para el candidate controlado:

```text
dataset_id = outcomes_table_v0_1_candidate
physical_dataset_id = outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
outcome_horizon = post_event_30m_intraday_1m
price_view = 1m_quote_guarded_raw
```

Checks minimos:

- artifact presence: parquet `data.parquet`, manifest y summary;
- schema/conformidad: `schema_version = outcomes_table_v0_1_candidate_intraday_1m_quote_guarded`;
- grain: sin duplicados por `event_window_id + outcome_horizon + price_view`;
- source reconciliation: cada row viene de `post_event_30m` con `valid_for_outcome_window_candidate = true`;
- reference rule: `reference_price` sale del `event_state` `at_event`;
- outcome bars: solo barras `1m_quote_guarded_raw` con `window_start_utc <= ts_utc < window_end_utc`;
- leakage: `contains_post_event_information=true` y `prohibited_as_pre_event_feature=true`;
- gates: `valid_for_ml_label_candidate=false`, `valid_for_rl_reward_candidate=false`, `full_universe_claim=false`, `execution_truth=false`.

Evidencia controlada 2026-07-05:

```text
outcome_rows = 5
quality_counts = good_intraday_1m_outcome: 3, review_intraday_missing_bars: 2
bars_expected_total = 150
bars_observed_total = 134
validator_status = passed
```

Passing este validator prueba separacion estructural X/y para el scope
controlado. No prueba full-universe, labels ML, rewards RL, slippage, fills ni
realismo de ejecucion.
