# TRADING_ACTIVITY_TA3_SAMPLE_IMPLEMENTATION_DECISION_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_ta3_sample_implementation_decision` |
| `document_version` | `v0_1` |
| `document_role` | `PREREGISTERED_SAMPLE_IMPLEMENTATION_DECISION` |
| `document_status` | `FROZEN_FOR_TA3_SAMPLE_BUILD` |
| `roadmap_stage` | `TA_3B` |
| `sample_seed` | `20260807` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `created_at` | `2026-08-07` |

---

## 1. Purpose

Resolve the physical ambiguities that remain between the preregistered TA-3
sample plan and the validated presession population candidate. This decision
does not change the scientific population, open a lockbox or authorize broad
Binding A execution.

Authority remains:

```text
TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md
```

---

## 2. Frozen population binding

```text
population dataset
= population_target_presession_4824_candidate_v0_1

population dataset sha256
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

membership state admitted for target selection
= ELIGIBLE_UNDER_DECLARED_PROXY

share policy
= S1_DILUTED_FIRST

TTL
= 180 calendar days

valid scientific claim
= restricted development evidence inside lt1b_universe_v0_1
  under the declared prior-close and shares proxy
```

The selector source gate is `PASS_WITH_RESTRICTIONS`. These restrictions must
be copied into every TA-3 manifest and readout.

---

## 3. Identity and governed-session semantics

The physical identity key is:

```text
instrument_context_key
= instrument_id x ticker_as_of_session
```

`instrument_id` alone is not exclusive in the recovered parent-universe data.
The composite key therefore governs ordering, windows, overlap and block reuse.
For additional conservatism, no bare `instrument_id` may contribute more than
two selected blocks across all ticker contexts.

A `governed session` for TA-3 sampling is:

```text
one expected exchange session represented by exactly one row
for the composite instrument-ticker context in
population_target_presession_4824_candidate_v0_1
and master_daily_table_v0_1
```

It need not be target-population eligible. Ineligible and unavailable
intervening sessions remain visible to baseline ordering and source audit.

---

## 4. Block semantics

One candidate block contains:

```text
10 consecutive ELIGIBLE_UNDER_DECLARED_PROXY contexts
in the composite instrument-ticker eligible sequence
```

All ten target contexts must belong to the same frozen development cohort. The
first target context assigns the block strata.

Baseline support requires at least 120 strictly prior governed sessions before
the first target. The physical work scope begins at governed index `start - 120`
and ends at the tenth target. All intervening governed sessions remain in the
scope even when they are not target-population eligible.

---

## 5. Strictly prior activity strata

The 20-session activity summaries are calculated only from governed sessions
strictly before the first target:

```text
prior_20_observed_session_count
prior_20_positive_session_count
prior_20_median_transaction_count
prior_20_positive_median_transaction_count
prior_20_median_dollar_volume
prior_20_zero_transaction_session_fraction
```

`prior_20_median_transaction_count` includes observed zero values. The positive
median is an additional implementation field used to assign `A1/A2/A3` without
misclassifying a context whose unconditional median is zero but which contains
positive prior sessions.

Assignment:

```text
AU = fewer than 20 observed prior sessions
A0 = 20 observed sessions and zero positive sessions
A1/A2/A3 = cohort p33/p67 of positive-session medians
```

Percentile thresholds are computed once from the complete feasible development
block inventory and frozen before any target trade file is read by Binding A.

---

## 6. Source-quality metadata

Foundation `acceptance_label` and local dispositions are mandatory metadata.
They are not automatic exclusions and cannot remove a selected symbol-second
denominator.

The block quality stratum is the Foundation label attached to the first target
file. `NO_FOUNDATION_EVIDENCE` is a first-class state. A quality label may be
used only to ensure representation of source conditions; its numerical trade
metrics are prohibited selection inputs.

Every quality label or local disposition with at least five feasible blocks in
a cohort receives a minimum marginal target of five. Any impossible quota is
reported as an explicit shortfall.

---

## 7. Deterministic quota resolution

Hard cohort capacity remains 60 blocks. Hard marginal targets are:

```text
price band
= 8 per feasible band

market-cap band
= 12 per feasible band

Foundation quality label
= 5 when at least 5 feasible blocks exist

local disposition
= 5 when at least 5 feasible blocks exist
```

Activity and zero-prevalence strata are balanced as secondary margins. Their
per-cohort soft target is the equal allocation of 60 blocks across feasible
states.

Selection uses the preregistered hash:

```text
SHA256(
  "20260807" |
  cohort_id |
  instrument_id |
  block_start_session
)
```

When two physical contexts share that exact hash input, the deterministic
tie-break is:

```text
ticker_as_of_session
population_context_id
```

At each selection step, the compatible candidate satisfying the largest number
of outstanding hard margins is chosen. Remaining ties are resolved by
normalized hard deficit, secondary-margin deficit and finally the frozen hash
order. Selection stops at 60 blocks per cohort.

Constraints remain:

```text
maximum two blocks per composite instrument context
maximum two blocks per bare instrument_id
minimum 252 governed-session separation when a composite context is reused
no overlapping target blocks
```

---

## 8. Development lockbox guard

Only these target dates may enter the sample inventory:

```text
2011-01-03 through 2022-12-30
```

The builder must fail if any selected, feasible or activity-derived row exceeds
the development boundary. Validation and final-test rows may not contribute to
percentiles, quotas, hashes or replacement decisions.

---

## 9. Required outputs

```text
development_context_accounting.parquet
feasible_blocks.parquet
selected_blocks.parquet
selected_target_contexts.parquet
sample_design_summary.json
sample_manifest.json
independent_validation.json
```

The manifest must bind source hashes, config hash, output hashes, exact selected
targets, quota shortfalls and expected Binding A row projection.

---

## 10. Authorization boundary

```text
TA-3 SAMPLE BUILDER AND VALIDATOR
= AUTHORIZED

TA-3 SAMPLE BUILD
= AUTHORIZED

SELECTED-BLOCK PHYSICAL SOURCE AUDIT
= REQUIRED_AFTER_SAMPLE BUILD

BROAD BINDING A MATERIALIZATION
= NOT AUTHORIZED UNTIL SAMPLE AND SOURCE GATES PASS

OOS
= NOT AUTHORIZED

CANONICAL PROMOTION
= NOT AUTHORIZED
```
