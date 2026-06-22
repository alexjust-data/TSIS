# Dataset Certification Matrix Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
dataset_certification_matrix_v0_1
```

## 2. Permitted Meaning

This table is a family-level quality and evidence gate.

Consumers may use it to ask:

- is this family human-inspector-ready?
- is this family visually complete?
- is the data verdict usable, scoped or blocked?
- what policy/evidence files govern this family?
- can this family enter an event case, backtest, ML run or only forensic review?

## 3. Prohibited Meaning

Consumers must not use it as:

- price data;
- quote data;
- trade tape;
- fundamental data;
- feature value;
- label;
- proof that a ticker/date observation is present;
- proof that row-level data is clean.

## 4. Consumer Classes

Permitted:

- `data_quality_report`
- `event_engine`
- `research_only`
- `forensic_only`

Conditionally permitted:

- `master_daily_table`
- `master_intraday_bar_table`
- `microstructure_features_table`
- `backtest_core`
- `backtest_extended`
- `ml_flagged`

Condition:

```text
Only as a gate, flag, mask or evidence link. The actual data must still pass
the family-specific validator and consumption policy.
```

Restricted/prohibited:

- `execution_simulator` as primary input;
- `ml_primary` as a feature;
- `rl_allowed` without later RL-specific contract;
- live trading decision without live-specific policy.

## 5. Gate Semantics

`declared_scope_allowed`:

```text
The family may be considered for consumers allowed by its own policy.
```

`scoped_only`:

```text
The family may be used only with explicit scope flags, masks or sample metadata.
```

`blocked_from_backtest_core`:

```text
The family must not enter backtest_core, ml_primary or unflagged features until
repair, waiver or later versioned promotion.
```

## 6. Required Downstream Fields

Any downstream table using this matrix must preserve or be able to trace:

- `dataset_family`;
- `data_quality_verdict`;
- `foundations_completion_status`;
- `visual_inspection_status`;
- `production_use_gate`;
- `event_consumption_gate`;
- `quality_policy_version`;
- `source_matrix_sha256`;
- `build_run_id`;
- evidence path or manifest reference.

## 7. Final Rule

`dataset_certification_matrix` decides whether a family is allowed to be
considered. It does not prove that a particular observation is usable.

