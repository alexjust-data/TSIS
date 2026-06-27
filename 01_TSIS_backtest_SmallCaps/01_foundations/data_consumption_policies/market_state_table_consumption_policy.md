# Market State Table Consumption Policy `v0_1`

## 1. Scope

Dataset target:

```text
market_state_table_v0_1
```

Current status:

```text
contract_defined_not_materialized
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
