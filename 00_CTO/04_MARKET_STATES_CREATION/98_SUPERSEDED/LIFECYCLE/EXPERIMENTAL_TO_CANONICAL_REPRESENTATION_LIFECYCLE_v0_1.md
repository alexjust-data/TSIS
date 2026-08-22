# Experimental to Canonical Representation Lifecycle v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `experimental_to_canonical_representation_lifecycle` |
| `document_version` | `v0_1` |
| `document_role` | `REPRESENTATION_LIFECYCLE_CONTRACT` |
| `document_status` | `ACTIVE` |
| `scope` | `Market State and Wake-up Information Objects` |
| `created_at` | `2026-08-08` |

## 1. Governing lifecycle

This contract separates candidate-model experimentation, canonical admission,
full-history materialization and downstream consumption.

```text
Information Object
-> Representation Model candidates
-> Experimental Physical Bindings
-> development and temporal OOS evidence
-> admitted specification and builder
-> full-history canonical materialization
-> detector and backtest consumption
```

## 2. Independent time concepts

```text
FEATURE HORIZON W
= trailing interval represented at decision time t

PIT BASELINE LOOKBACK B
= causal history used to determine what was normal at t

MATERIALIZATION COVERAGE PERIOD
= calendar interval for which rows are physically produced
```

Examples:

```text
trade_count_10s(t)
share_volume_30s(t)
arrival_rate_1m(t)

B20  = previous 20 eligible sessions
B60  = previous 60 eligible sessions
B120 = previous 120 eligible sessions

coverage = approximately 2005 through 2026
```

These concepts are not interchangeable.

## 3. Experimental bindings

An Experimental Physical Binding is a governed candidate implementation of a
Representation Model. It fixes candidate variables, formulas, horizons,
sources, temporal rules and missingness semantics for reproducible comparison.

```text
Trading Activity Binding A
= initial multiscale activity implementation

Trading Activity Binding B
= expanded marks, durations and concentration

Trading Activity Binding C
= advanced conditional-intensity models, only if A/B evidence justifies it
```

Experimental means neither informal nor disposable. It means not yet admitted
as the canonical physical representation and not authorized for unrestricted
downstream consumption. Binding C is optional.

## 4. Restricted development materialization

Candidate bindings are first materialized on a frozen development sample of
selected `instrument_id x session_date` blocks. The current TA-3 Binding A run
belongs to this phase.

It provides evidence about causal calculability, determinism, observability,
coverage, missingness, semantic behavior, computational cost and incremental
information. It does not provide a canonical state for every timestamp from
2005 onward.

```text
TA-3 RESTRICTED OUTPUT
!= full-history canonical representation

TA-3 RESTRICTED OUTPUT
= experimental evidence for model and builder selection
```

## 5. Comparison and temporal OOS

```text
1. Build Binding A on frozen development data.
2. Build Binding B on the same governed population and periods.
3. Build Binding C only if preregistered evidence justifies it.
4. Compare candidates at the same false-alarm budget.
5. Select a candidate without opening the final temporal OOS lockbox.
6. Evaluate the selected candidate on untouched temporal OOS data.
7. Admit or reject the Representation Model and physical binding.
```

Selection includes detection delay, missed episodes, stability by stratum,
non-redundant information, robustness and complexity. OOS must not become a
second development set.

## 6. Canonical promotion

Canonical promotion initially applies to:

```text
semantic dimensions
selected variables
exact formulas and feature horizons
PIT baseline policy
source and eligibility policies
temporal and missingness semantics
schema and lineage requirements
validated builder implementation
```

```text
CANONICAL SPECIFICATION AND BUILDER
!= CANONICAL FULL-HISTORY MATERIALIZATION
```

A restricted TA-3 output is not silently promoted into a full-history dataset.

## 7. Full-history production materialization

After admission:

```text
admitted canonical builder
x governed source histories
x authorized parent-instrument scope
x approximately 2005-2026 coverage
-> versioned historical representation dataset
```

The exact instrument count, dates and eligible instrument-session membership
come from the frozen run manifest and PIT Universe Resolver. The build retains:

```text
UNAVAILABLE
OUT_OF_SCOPE
DEGRADED
INSUFFICIENT_SAMPLE
BASELINE_UNAVAILABLE
```

It must never manufacture coverage or use future information.

## 8. Warm-up

A 2005 published state may need raw history before 2005 to satisfy a baseline
such as the previous 60 eligible sessions. If that causal history does not
exist, the state is `BASELINE_UNAVAILABLE`; the builder cannot use future data
or silently shorten the baseline.

## 9. Backtest consumption

```text
Backtester requests instrument x decision timestamp
-> reads versioned canonical representation rows
-> reads quality and availability states
-> joins other admitted Information Objects
-> evaluates detector or strategy logic
```

A normal backtest does not rescan raw trades and recompute every window.
Recalculation occurs when governed inputs or definitions change, including a
new backfill, model version, formula, horizon, baseline, eligibility policy,
bug correction, coverage expansion or schema migration. Every such change
produces a new versioned materialization.

## 10. Reuse

Binding B should reuse eligible-event streams, decision grids, coverage states,
rolling aggregates and Binding A intermediates where semantics permit.
Information Objects should share governed rolling-window, PIT-baseline,
availability and trade-quote alignment infrastructure rather than independently
rescan the same raw data.

## 11. Current interpretation

```text
CURRENT TA-3 BINDING A RUN
= restricted experimental development materialization

NEXT
= finish Binding A
-> incremental Binding B
-> justified Binding C only if needed
-> comparison
-> temporal OOS
-> admission or rejection

AFTER ADMISSION
= separate validated full-history production materialization
```

## 12. Institutional rule

```text
restricted experimental evidence
cannot be consumed as universal canonical history

canonical specification
does not imply complete physical coverage

backtest authorization
requires a validated materialization covering requested timestamps
```
