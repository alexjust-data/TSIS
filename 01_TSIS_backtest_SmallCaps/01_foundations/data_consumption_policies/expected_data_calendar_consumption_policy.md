# Expected Data Calendar Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
expected_data_calendar_v0_1
```

## 2. Permitted Meaning

This table is a coverage expectation denominator.

Consumers may use it to ask:

- which ticker/sessions should be checked for daily data;
- which ticker/sessions should be checked for 1m data;
- which ticker/sessions should be checked for trades;
- which ticker/sessions should be checked for quotes;
- where missingness is expected to be evaluated.

## 3. Prohibited Meaning

Consumers must not use it as:

- evidence that a file exists;
- evidence that data is clean;
- a price table;
- a feature table;
- a backtest input by itself;
- a way to hide coverage holes.

## 4. Consumer Classes

Permitted:

- `data_quality_report`
- `dataset_certification_matrix`
- `research_only`
- `forensic_only`

Conditionally permitted:

- `master_daily_table`
- `master_intraday_bar_table`

Condition:

```text
Only as coverage denominator, never as observed data.
```

Restricted/prohibited:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`

## 5. Required Downstream Fields

Any downstream coverage report using this table must preserve:

- `dataset_family`
- `ticker`
- `session_date`
- `expected_session`
- `expected_reason`
- source build ids
- expectation policy version

## 6. Final Rule

`expected_data_calendar` defines what must be checked.

It does not decide whether the check passes.

