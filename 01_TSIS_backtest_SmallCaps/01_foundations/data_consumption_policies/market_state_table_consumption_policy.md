# Market State Table Consumption Policy `v0_1`

## 2026-07-07 Quotes Root Supersession

`D:/quotes -> E:/TSIS/data/quotes_` is closed and approved. The official quotes E-root for new downstream work is `E:/TSIS/data/quotes_`, backed by Phase A structural parity and Phase B SHA256 retry evidence. Historical artifacts built from `D:/quotes` remain pre-approval/provenance evidence and must be rebuilt against the approved E-root before promotion to an official downstream table. The legacy `E:/TSIS/data/quotes` tree remains incomplete for this decision.


## 1. Scope

Dataset target:

```text
market_state_table_v0_1
```

Current status:

```text
contract_defined_not_materialized
```

## 1.1 Provisional Microstructure Source Rule

For the next controlled candidate loop, `market_state_table` may consume
microstructure components derived from:

```text
quotes_root_used = D:/quotes
quotes_root_state = pre_approval_d_recovery_lineage_requires_rebuild
target_official_quotes_root = E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root = E:/TSIS/data/quotes
```

This is a candidate-only allowance. Rows inheriting this root state must expose
lineage and must not be consumed as:

```text
valid_for_ml_feature_candidate = true
valid_for_backtest_context_candidate = true
valid_for_rl_state_candidate = true
valid_for_execution_simulator_direct = true
```

unless a later contract explicitly proves `E:/TSIS/data/quotes_` parity/audit
and recomputes or promotes the affected candidate. Until then, the correct
interpretation is:

```text
state_component_candidate = true
institutional_state = false
requires_rebuild_after_quotes_root_approval = true
```

## 2. Permitted Meaning

Permitted meaning after materialization:

```text
legal feature-state snapshot for one instrument at one decision timestamp
```

Forbidden meaning:

```text
strategy signal, label, reward, execution fill or live trading authority
```

## 3. Required Cutoff Rule

All consumers must respect:

```text
component_as_of_utc <= decision_timestamp_utc
```

Rows must not be consumed unless:

```text
requires_asof_filter = true
contains_future_information_without_event_filter = false
```

or the consumer is explicitly forensic and masks the row as leakage evidence.

## 4. Required Feature Namespace Rule

Consumers may only read feature columns from approved namespaces:

```text
identity__
calendar__
scanner__
daily__
intraday__
microstructure__
halt__
fundamentals__
news__
short_context__
short_constraints__
regime__
quality__
```

Consumers must reject un-namespaced feature columns.

## 5. Prohibited Consumption

No consumer may treat these as features:

```text
outcome__*
label__*
reward__*
action__*
policy__*
fill__*
pnl__*
future__*
strategy__*
signal__*
```

## 6. Consumer Rules

### Event Engine

May use `market_state_table` only as context after it is materialized and
validated.

### ML

May use it as `X` only when:

```text
valid_for_ml_feature_candidate = true
```

Labels must be joined from a separate label/outcome table.

### Offline RL

May use rows as state candidates only when:

```text
valid_for_rl_state_candidate = true
```

But direct RL training remains prohibited until a separate transition/reward
contract exists:

```text
valid_for_rl_training_direct = false
```

### Execution Simulator

May not treat `market_state_table` as execution truth:

```text
execution_truth = false
```

## 7. Final Rule

`market_state_table` is a feature-state snapshot. It is not a decision engine.
