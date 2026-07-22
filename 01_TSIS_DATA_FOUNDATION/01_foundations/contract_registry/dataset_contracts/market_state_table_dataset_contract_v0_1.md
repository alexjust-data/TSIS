# Market State Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: market_state_table_v0_1
family: data_foundation_outputs
class: state_composition_table
grain: instrument_id + decision_timestamp_utc + state_horizon + state_scope + state_schema_version
status: contract_defined_not_materialized
```

## 2. Purpose

`market_state_table` is the future governed feature-state snapshot table for
TSIS.

It answers:

```text
At this decision timestamp, what was legally knowable about this instrument and
its market context from governed CAPA 1 components?
```

It does not answer:

- what trade to take;
- what strategy to run;
- what outcome happened later;
- what reward should be assigned;
- whether a fill occurred;
- whether a short order was executable without short-sale constraints data.

## 3. Source Components

Potential components are limited to governed outputs and explicitly declared
source policies:

```text
instrument_master_v0_1
market_calendar_v0_1
expected_data_calendar_v0_1
dataset_certification_matrix_v0_1
corporate_actions_table_v0_1
master_daily_table_v0_1
daily_scanner_candidates_table_v0_1 when used as candidate-set lineage
master_intraday_bar_table_v0_1
master_intraday_bar_table_v0_2_candidate_quote_guarded when scoped candidate and not promoted
microstructure_features_table_v0_1
halts_table_v0_1
fundamentals_asof_table_v0_1
news_context_table_v0_1
short_context_table_v0_1
regime_context_table_v0_1
short_sale_constraints_table_v0_1 when materialized
real_time_corporate_event_alerts_table_v0_1 when materialized
```

Explicit non-feature components:

```text
outcomes_table_v0_1
```

`outcomes_table_v0_1` may only be joined later as labels/y through a separate
training/label builder.

## 4. Current Scope

```text
materialized: false
builder_implemented: false
full_universe_claim: false
direct_rl_training_allowed: false
execution_truth: false
```

The current contract defines the future official dataset. It is not evidence that a promoted institutional state table exists.

## 4.1 Current Controlled Candidate Evidence

```text
microstructure_halt_controlled_candidate_rows = 50
intraday_quote_guarded_controlled_candidate_rows = 10835
intraday_quote_guarded_controlled_manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
intraday_quote_guarded_controlled_status = controlled_candidate_not_promoted
full_universe_claim = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

These candidates are integration proofs only and do not change `status: contract_defined_not_materialized` for the official dataset.

## 5. Required Semantics

All component rows must be selected under:

```text
component_as_of_utc <= decision_timestamp_utc
```

Components that use `date` instead of timestamp must use their consumption
policy lag/as-of rule.

The builder must preserve:

- component source dataset id;
- component build run id;
- component quality state;
- component availability state;
- component as-of timestamp/date;
- leakage policy version;
- feature namespace version.

## 6. Prohibited Semantics

The table must not contain:

- outcome values;
- label values;
- reward values;
- actions;
- policies;
- fills;
- PnL;
- strategy decisions;
- un-namespaced feature columns.

## 7. Allowed Consumers

Allowed only after materialization and validators pass:

- `event_state_builder`
- `event_engine` as context
- `pattern_discovery`
- `ml_feature_builder` with label separation
- `backtest_extended` as context
- `research_only`
- `forensic_only`

Not enabled by this contract:

- direct `rl_training`;
- `execution_simulator` direct;
- live trading authority;
- strategy signal authority.

## 8. Change Policy

Version bump required when:

- target grain changes;
- feature namespace policy changes;
- any prohibited column family becomes allowed;
- an upstream component is promoted from blocked/scoped to primary;
- same-session regime or daily aggregates become legal under a new intraday
  cutoff contract;
- short-sale constraints become materialized and included;
- RL direct training is enabled.
