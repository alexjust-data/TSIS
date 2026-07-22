# Intraday Bar Identity And Cutoff Policy v0.1

Status: `experimental_non_production_policy`
Date: `2026-07-21`
Scope: `metadata_only_column_binding_gate`

This policy resolves two metadata-only bindings for
`014_master_intraday_bar_table_candidate` after schema inspection found:

```text
instrument_id observed_type = null
ticker observed_type = string
ts_utc observed_type = string
```

It does not validate row values, grain uniqueness, timestamp parsing, timezone
semantics or canonical identity correctness.

## Instrument Identity

When physical `instrument_id` is present but reported as `NullType`, the
experimental gate may bind logical `instrument_id` to physical `ticker` with
restrictions:

```text
logical instrument_id -> physical ticker
identity_resolution_required = true
```

A later gate must normalize `ticker` to canonical `instrument_id` through a
governed reference identity source as-of the decision timestamp. Until then, the
binding is resolved only as physical identity evidence, not as canonical identity
validation.

## Decision Timestamp Context

`decision_timestamp` is not a physical field supplied by 014. It is the external
builder invocation cutoff.

The source contributes the observation timestamp:

```text
bar_end -> ts_utc
```

The builder context contributes:

```text
decision_timestamp_utc
```

The future temporal legality rule is:

```text
bar_end <= decision_timestamp_utc
```

`decision_timestamp_or_bar_end` is therefore retained only as a legacy logical
placeholder for this metadata gate and is resolved by builder context, not by a
physical source column.

## Current Gate Authority

```text
bounded_sample_data_read_allowed = false
grain_validation = not_executed
temporal_value_validation = not_executed
state_materialization_allowed = false
```
