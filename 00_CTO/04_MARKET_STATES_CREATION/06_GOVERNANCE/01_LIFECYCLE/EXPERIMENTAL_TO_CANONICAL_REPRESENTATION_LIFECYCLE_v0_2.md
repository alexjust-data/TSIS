# Experimental to Canonical Representation Lifecycle v0_2

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `experimental_to_canonical_representation_lifecycle` |
| `document_version` | `v0_2` |
| `document_role` | `REPRESENTATION_LIFECYCLE_CONTRACT` |
| `document_status` | `ACTIVE` |
| `scope` | `Market State and Wake-up Information Objects` |
| `supersedes` | `EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md` |
| `created_at` | `2026-08-14` |

## 1. Governing lifecycle

This contract separates candidate-model experimentation, canonical admission,
full-history materialization and downstream consumption. Version 0.2 adds an
explicit materialization incident-learning gate without weakening any v0.1
boundary.

```text
Information Object
-> Representation Model candidates
-> Experimental Physical Bindings
-> restricted development materialization
-> incident capture and prevention-control promotion
-> inherited-control gate for the next materialization
-> development and temporal OOS evidence
-> admitted specification and builder
-> separately authorized full-history canonical materialization
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

Feature horizons, PIT baseline lookbacks and materialization coverage are not
interchangeable.

## 3. Experimental bindings

An Experimental Physical Binding fixes candidate variables, formulas, horizons,
sources, temporal rules and missingness semantics for reproducible comparison.
Trading Activity Bindings A and B are required candidates; Binding C remains
optional and evidence-gated. Experimental means governed but not yet canonical
and not authorized for unrestricted downstream consumption.

## 4. Restricted development materialization

Candidate bindings first run on a frozen development sample of governed
`instrument_id x session_date` targets. This phase evaluates causal
calculability, determinism, observability, coverage, missingness, semantics,
cost and incremental information. It does not create universal canonical
history.

Before any long materialization, every variable must pass one bounded
production-equivalent probe per planned shard. Production-equivalent includes
the exact wrapper, aggregation, terminal certifier and final-manifest path.

## 5. Materialization incident-learning gate

Every defect follows
`REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md`
and is persisted in
`REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md`.

A later binding or model cannot start a long run until its plan declares every
prior applicable prevention control and supplies `PASS` evidence. Exact target
lists may not be generalized into intervals; metadata and physical counts must
remain typed separately; all count consumers must share one authoritative
cardinality specification.

```text
model N incident
-> versioned correction and verified closure
-> promoted prevention control
-> explicit import and PASS in model N+1
```

## 6. Comparison and temporal OOS

```text
1. Build Binding A on frozen development data.
2. Close or explicitly carry all materialization incidents.
3. Import applicable controls into Binding B and later models.
4. Build Binding B on the same governed population and periods.
5. Build Binding C only if preregistered evidence justifies it.
6. Compare candidates at the same false-alarm budget.
7. Select without opening the final temporal OOS lockbox.
8. Evaluate the selected candidate on untouched temporal OOS data.
9. Admit, reject or revise the Representation Model and physical binding.
```

OOS must not become a second development set.

## 7. Canonical promotion

Canonical promotion applies to semantic dimensions, selected variables, exact
formulas and horizons, PIT policy, sources, eligibility, temporal/missingness
semantics, schema, lineage, validated builder and inherited prevention controls.

```text
CANONICAL SPECIFICATION AND BUILDER
!= CANONICAL FULL-HISTORY MATERIALIZATION
```

A restricted output is never silently promoted to full-history canonical data.

## 8. Full-history production materialization

After admission and a separate authorization:

```text
admitted canonical builder
x governed source histories
x exact authorized parent-instrument/session membership
x authorized coverage
x inherited incident controls PASS
-> versioned historical representation dataset
```

The run retains `UNAVAILABLE`, `OUT_OF_SCOPE`, `DEGRADED`,
`INSUFFICIENT_SAMPLE` and `BASELINE_UNAVAILABLE`. It must not manufacture
coverage, infer exact membership from date ranges or use future information.

## 9. Warm-up

Published states may require earlier causal history. If the required history
does not exist, the state is `BASELINE_UNAVAILABLE`; the builder cannot use
future data or silently shorten the baseline.

## 10. Backtest consumption

The backtester reads versioned canonical representation rows plus quality and
availability states. It does not normally rescan raw data. New governed input,
formula, horizon, baseline, eligibility, bug correction, coverage or schema
requires a new versioned materialization and re-evaluation of applicable
incident controls.

## 11. Reuse

Later bindings should reuse eligible streams, decision grids, coverage states,
rolling aggregates and prior intermediates only where semantics and hashes
permit. Shared infrastructure must preserve PIT, availability and lineage.

## 12. Current interpretation

```text
Trading Activity Binding A calculation = COMPLETE_240_OF_240
terminal aggregate certification       = FAILED_NOT_PROMOTED
target-only recovery                    = IMPLEMENTED_PROBES_PASS_FULL_NOT_AUTHORIZED
materialization incidents 001..005      = BOUNDED_VERIFIED_FULL_CLOSURE_PENDING

NEXT
= human-authorized recovery and certification
-> Binding A evidence verdict
-> import controls into Binding B and every later applicable model
```

## 13. Institutional rule

```text
restricted experimental evidence cannot be consumed as canonical history
canonical specification does not imply complete physical coverage
backtest authorization requires validated coverage at requested timestamps
a corrected run does not rewrite a failed historical run
a later model cannot ignore applicable materialization incident controls
```

## 14. Appended current-status update — 2026-08-14

This update supersedes only the operational snapshot in section 12; it does not
change the lifecycle contract.

```text
Trading Activity Binding A calculation       = COMPLETE_240_OF_240
historical aggregate wrapper                 = FAILED_NOT_PROMOTED
target-only terminal certification           = PASS_2400_TARGET_7200_PARTITIONS
materialization incidents 001..005            = FULL_VERIFIED_LATER_PLAN_IMPORT_PENDING
canonical promotion                          = NOT_AUTHORIZED

NEXT
= Binding A evidence verdict
-> Binding B plan imports applicable controls
-> Binding B implementation, tests and all-shard probes
-> separately authorized Binding B materialization
-> candidate comparison
-> untouched temporal OOS
```

## 15. Appended terminal percentile-replay update — 2026-08-15

This dated append supersedes only the current-status interpretation in sections
12 and 14. It does not rewrite their historical evidence or change the
lifecycle contract.

```text
Trading Activity Binding A calculation       = COMPLETE_240_OF_240
target-only terminal certification           = PASS_2400_TARGET_7200_PARTITIONS
bounded family-by-family evidence audit       = PASS
independent percentile replay FULL            = PASS_EXACT
percentile cells / mismatches                 = 3,351,960,000 / 0
revised Binding A verdict                     = PASS_WITH_SCOPE_RESTRICTIONS
canonical promotion                           = NOT_AUTHORIZED

NEXT
= Binding B frozen preregistration
-> import and bind applicable RM-MAT-CTRL-001..006
-> implementation and unit tests
-> all-variable / all-shard production-equivalent probes
-> separate human gate before long materialization
-> candidate comparison on identical population and periods
-> untouched temporal OOS
```
