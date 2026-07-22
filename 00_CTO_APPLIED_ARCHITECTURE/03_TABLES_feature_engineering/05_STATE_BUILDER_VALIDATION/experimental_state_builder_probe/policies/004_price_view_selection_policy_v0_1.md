# 004 Price View Selection Policy v0.1

Status: `experimental_non_production_policy`
Date: `2026-07-21`
Scope: `bounded_quality_and_lineage_validation`

This policy governs experimental use of `004_master_daily_table` when the same logical daily key can appear under more than one physical `price_view`.

It does not rewrite the source, merge price views, claim full-history view consistency, or authorize production consumption.

## Decision

`price_view` is a physical hidden dimension. A builder must not consume a daily row unless a governed price view has been selected before row resolution.

For the experimental core-four builder validation path, the selected view is:

```text
selected_price_view = split_normalized
```

This selection is valid only for bounded experimental validation of closed-price and prior-session observables. Any total-return, dividend-adjusted or corporate-action-specific interpretation must request a separate price-view decision.

## Rule

```text
if multiple price_view surfaces are available:
    require explicit selected_price_view
    read only rows from selected_price_view
    record selected_price_view in lineage

if selected_price_view is absent from the physical surface:
    block builder execution for daily-source-dependent objects

if selected_price_view exists but full-history consistency is not validated:
    allow experimental execution with promotion restriction
```

## Current Gate Authority

```text
bounded_sample_data_read_allowed = true_under_scope_only
feature_builder_execution_allowed = false
state_materialization_allowed = false
source_mutation_allowed = false
```
