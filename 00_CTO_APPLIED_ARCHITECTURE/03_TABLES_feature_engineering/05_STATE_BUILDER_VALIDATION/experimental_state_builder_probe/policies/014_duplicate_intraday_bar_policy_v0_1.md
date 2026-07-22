# 014 Duplicate Intraday Bar Policy v0.1

Status: `experimental_non_production_policy`
Date: `2026-07-21`
Scope: `bounded_quality_and_lineage_validation`

This policy governs duplicate candidate keys in `014_master_intraday_bar_table_candidate` for experimental builder validation.

It does not repair the source, claim full-history uniqueness, or authorize production consumption.

## Duplicate Classes

```text
identical duplicate rows
    same ticker + ts_utc
    same checked OHLCV state values

conflicting duplicate rows
    same ticker + ts_utc
    different checked OHLCV state values
```

## Decision

```text
identical duplicate rows
    deterministic collapse allowed for experimental builder validation
    collapse must be stable and recorded in probe evidence
    source rows must not be modified

conflicting duplicate rows
    no silent collapse
    no arbitrary first-row selection
    ordering/source precedence policy required before builder execution
```

## Rule

```text
if duplicate_group_classification = identical:
    builder_execution_blocker = false
    promotion_only_restriction = true

if duplicate_group_classification = conflicting:
    builder_execution_blocker = true
    required_resolution = governed source precedence or ordering evidence
```

## Current Gate Authority

```text
bounded_sample_data_read_allowed = true_under_scope_only
feature_builder_execution_allowed = false
state_materialization_allowed = false
source_mutation_allowed = false
```
