# CURRENT_STATUS_AND_HANDOFF_v0_24

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `CURRENT_HANDOFF` |
| `snapshot_at` | `2026-08-15` |
| `active_workstream` | `trading_activity_binding_b_exact_specification_review` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `next_gate` | `CLOSE_B02_BLOCKING_DECISIONS_AND_EXPLICIT_HUMAN_FREEZE` |
| `supersedes` | `CURRENT_STATUS_AND_HANDOFF_v0_23.md` |

## 1. Punto exacto

```text
Binding A terminal/scientific evidence             = PASS_WITH_SCOPE_RESTRICTIONS
Binding A independent percentile replay            = PASS_EXACT_3,351,960,000_CELLS
Binding B preparation package external audit       = PASS
Binding B inheritance/delta contract B-01           = FROZEN_BY_HUMAN
Binding B exact specification B-02                  = DRAFT_PREPARED_NOT_FROZEN
B-02 blocking decisions                             = 12 OPEN
Binding B implementation B-03                       = NOT_AUTHORIZED
Binding B all-variable/all-shard probes B-08        = NOT_AUTHORIZED
Binding B long materialization B-12                 = NOT_AUTHORIZED
A/B comparison B-17                                 = NOT_AUTHORIZED
temporal OOS B-18                                   = NOT_AUTHORIZED
canonical promotion                                 = NOT_AUTHORIZED
```

## 2. External audit and freeze evidence

Audited immutable package:

```text
trading_activity_binding_b_preparation_handoff_v0_1_20260815.zip
SHA-256
= 6419be68576a579c4ce6ac3ec38dab58a83d01318d8c202f29da0f61fa14e6fd
```

Decision readout:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md
```

The external auditor passed preparation and scientific direction for exact-
specification drafting, while keeping implementation and all downstream gates
closed. The human then explicitly authorized B-01 freeze and B-02 drafting.

Frozen contract:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md

SHA-256
= 50dbfa50730ed0832711d626864a719a285195e582e6157650faca7d4a20ffd9
```

## 3. What B-01 now freezes

Binding B must preserve A's scientific object, source, RTH scope, eligibility,
latency, decision grid, prior-only baseline membership, exact denominator and
OOS discipline. It adds but does not weaken:

```text
timestamp clusters without asserted within-cluster order
explicit timestamp-resolution and cluster-history states
zero-baseline and economic-clock censoring states
mandatory B-renewal-only / B-kernel-only / B-full ablations
development-only calibration
capacity-matched detector probes
paired session-level uncertainty
```

## 4. B-02 draft now prepared

Authority under review:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md
```

It translates the 22 primary variables into formulas, units, dtypes, causal
availability, timestamp clustering, piecewise PIT intensity, continuous
kernels, economic time, missingness, candidate output topology, test cases and
comparison rules. It is deliberately `NOT_FROZEN`.

## 5. Twelve decisions still blocking B-02 freeze

```text
B02-D01 fast-duration threshold
B02-D02 zero-dominated threshold
B02-D03 silence-break formula
B02-D04 kernel epsilon
B02-D05 economic-unit positive support
B02-D06 physical family topology/cardinality
B02-D07 false-activation budget
B02-D08 detector grids/effective-capacity cap
B02-D09 p95 delay non-inferiority margin
B02-D10 paired uncertainty unit/replicates/confidence
B02-D11 compute budget
B02-D12 exact final-lockbox manifest identity
```

These are review questions, not implementation freedoms. No agent may choose
them silently inside code.

## 6. Next safe action

```text
review B02-D01..D12
-> amend B-02 until internally exact
-> independent scientific review
-> explicit human authorization to freeze B-02
```

Only after that separate freeze may B-03 code be proposed. The mandatory TSIS
sequence remains implementation/tests, one production-equivalent probe per
variable in every shard, value-level audit, versioned certification and human
PASS before any long materialization.

## 7. Prohibitions for the next agent

Do not:

- treat the B-02 draft as executable authority;
- create a long runner or materialization config;
- open temporal validation or final OOS;
- change the 2,400 TARGET denominator;
- use `physical_row_ordinal` as causal event order;
- turn zero, unavailable, censored or insufficient states into numeric zero;
- overwrite the externally audited ZIP.

