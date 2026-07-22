# Raw Quote Quality Policy v0.1

Status: `experimental_non_production_policy`
Date: `2026-07-21`
Scope: `bounded_quality_and_lineage_validation`

This policy defines bounded experimental derivation of quote quality labels for `raw_quotes`.

It does not repair quotes, filter rows for production, validate quote quality over full history, or authorize quote-dependent builders.

## Derived Fields

```text
two_sided_flag
quote_quality_flag
```

## Rule

A quote row is two-sided when:

```text
bid_price is present
ask_price is present
bid_size is present
ask_size is present
bid_price > 0
ask_price > 0
bid_size >= 0
ask_size >= 0
```

A two-sided quote is classified as:

```text
normal_quote
    ask_price > bid_price

locked_quote
    ask_price = bid_price

crossed_quote
    ask_price < bid_price
```

Rows that fail two-sided requirements are classified as:

```text
not_two_sided_or_invalid_quote
```

## Decision

The bounded gate may derive these labels for reporting and readiness classification only. Derived labels are experimental evidence, not a repaired source dataset and not a promoted quality surface.

```text
quote_quality_flag derivable by policy = true
quote_quality_full_history_validated = false
promotion_only_restriction = true
```

## Current Gate Authority

```text
bounded_sample_data_read_allowed = true_under_scope_only
feature_builder_execution_allowed = false
state_materialization_allowed = false
source_mutation_allowed = false
```
