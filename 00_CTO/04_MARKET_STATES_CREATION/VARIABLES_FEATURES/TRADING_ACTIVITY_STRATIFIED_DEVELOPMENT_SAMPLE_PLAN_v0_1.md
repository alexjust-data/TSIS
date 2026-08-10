# TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_stratified_development_sample_plan` |
| `document_version` | `v0_1` |
| `document_role` | `PREREGISTERED_DEVELOPMENT_SAMPLE_PLAN` |
| `document_status` | `PREREGISTERED_WITH_BLOCKING_SOURCE_GATE` |
| `roadmap_stage` | `TA_3` |
| `information_object_id` | `trading_activity` |
| `binding_id` | `trading_activity_binding_a_candidate_v0_1` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `sample_seed` | `20260807` |
| `pit_selector_gate` | `PENDING` |
| `sample_manifest_status` | `NOT_MATERIALIZED` |
| `broad_execution_status` | `BLOCKED_PENDING_PIT_SELECTOR_GATE` |
| `oos_status` | `NOT_AUTHORIZED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |

---

## 1. Purpose

Preregister the first stratified development sample used to test whether
Binding A remains physically representable beyond the one-ticker AACT pilot.

This plan governs sample selection. It does not:

```text
select a winning detector
define Wake-up labels
open OOS data
promote canonical features
authorize predictive consumption
```

---

## 2. Entry gate

TA-1 and TA-2 are closed:

```text
FULL DETERMINISTIC SYMBOL-SECOND PILOT
= PASS_WITH_RESTRICTIONS

FULL LEGACY SOURCE GATE
= PASS_WITH_RESTRICTIONS
```

TA-3 design is authorized. Physical sample selection remains blocked until a
daily point-in-time selector can prove the requested market-cap and price
membership at each target session.

Required dependency:

```text
POPULATION_TARGET_PIT_SELECTOR_GATE
= PASS_WITH_RESTRICTIONS or PASS
```

Authority:

```text
POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md
```

---

## 3. Scientific population

The target population is not a list of current tickers. It is a set of
point-in-time instrument-session contexts:

```text
instrument listed and observable at session s
AND common stock eligibility known as-of s
AND market_cap_at_session_start(s) < 100,000,000 USD
AND 0.50 <= prior_close_eligible(s) <= 20.00 USD
AND identity and calendar context resolvable
```

The operational `<1B` universe is an upstream candidate pool and window
constraint. It is not daily proof of `<$100M` membership.

Required accounting:

```text
requested instrument-session contexts
= eligible
  + excluded
  + blocked
```

`blocked` must not be rewritten as `excluded` or `ineligible`.

---

## 4. Physical source facts already established

### 4.1 Daily price and calendar spine

```text
dataset_id
= master_daily_table_v0_1

physical root
= G:/TSIS/data/data_foundation_outputs/master_daily_table/
  master_daily_table_v0_1

tickers
= 4,824

expected instrument-session rows per price view
= 7,369,699

date range
= 2005-01-03 through 2026-03-09

duplicate key groups
= 0

hard fail count
= 0
```

The selection price view is `daily_raw`, because the scanner question concerns
the price observable in the historical session, not a retrospectively
normalized current-share price. Corporate actions effective before the target
session must still be reconciled when deriving the eligible prior close.

### 4.2 Shares candidate source

```text
dataset_id
= fundamentals_asof_table_v0_1

rows
= 621,756

tickers
= 4,813

as-of date range
= 2010-04-22 through 2026-04-03

income-statement rows
= 242,886

candidate fields
= basic_shares_outstanding
  diluted_shares_outstanding
```

These fields are candidates, not automatically accepted point-in-time common
shares. Their accounting meaning, availability date and suitability for market
capitalization must pass the population-target source audit.

### 4.3 Trade source

```text
source_dataset_id
= trades_ticks_prod_2005_2026_legacy_rth

physical root
= G:/TSIS/data/trades_ticks_prod_2005_2026
```

The same condition, latency, coverage and quality policies used by the AACT
pilot remain frozen for TA-3 unless a versioned amendment is approved.

---

## 5. Temporal partitions frozen before feature inspection

```text
DEVELOPMENT RANGE
= 2011-01-03 through 2022-12-30

DEVELOPMENT COHORT D1
= 2011-01-03 through 2013-12-31

DEVELOPMENT COHORT D2
= 2014-01-02 through 2016-12-30

DEVELOPMENT COHORT D3
= 2017-01-03 through 2019-12-31

DEVELOPMENT COHORT D4
= 2020-01-02 through 2022-12-30

VALIDATION LOCKBOX
= 2023-01-03 through 2024-12-31

ENGINEERING-EXPOSED EMBARGO
= 2025-01-02 through 2025-03-14

FINAL TEST LOCKBOX
= 2025-03-17 through 2026-03-09
```

The AACT pilot range remains engineering evidence and cannot be reused as
untouched OOS evidence. No TA-3 feature materialization may read validation or
final-test target sessions.

Manifest-level schema, aggregate coverage and path existence checks are not
feature inspection and may be performed for capacity planning.

---

## 6. Sampling unit and target size

Primary sampling unit:

```text
instrument x block of 10 consecutive PIT-eligible target contexts
```

Each block requires:

```text
120 strictly prior governed sessions for PIT baseline support
+
10 full RTH PIT-eligible target sessions
```

`Consecutive` means consecutive in the instrument's eligible-context sequence.
Intervening exchange sessions remain visible to baseline and audit logic but are
not target outputs unless independently selected. Every target session must pass
the PIT population rule separately. The block stratum is assigned from the first
target context, while per-session price, market-cap and membership states remain
preserved.

Preregistered target:

```text
60 blocks per development cohort
x 4 cohorts
= 240 blocks

240 blocks x 10 target sessions
= 2,400 instrument-session targets
```

Constraints:

```text
maximum blocks per instrument = 2
minimum separation when reused = 252 governed sessions
target blocks may not overlap for the same instrument
all target sessions use the complete RTH decision grid
```

If fewer than 1,200 eligible instrument-session targets survive the PIT and
physical-source gates, broad execution is not authorized and the plan must be
versioned before changing the target.

---

## 7. Preregistered marginal strata

The sample is balanced on marginal distributions. It is not required to fill
the full Cartesian product of every stratum.

### 7.1 Price at session start

```text
P1 = [0.50, 1.00)
P2 = [1.00, 2.00)
P3 = [2.00, 5.00)
P4 = [5.00, 10.00)
P5 = [10.00, 20.00]
```

Minimum per cohort: `8` blocks in every feasible price band.

### 7.2 Market capitalization at session start

```text
M1 = [0, 10M)
M2 = [10M, 25M)
M3 = [25M, 50M)
M4 = [50M, 100M)
```

Minimum per cohort: `12` blocks in every feasible market-cap band.

### 7.3 Strictly prior activity

Sampling activity must not use the target session. It is calculated from the
20 strictly prior sessions in `master_daily_table_v0_1`:

```text
prior_20_observed_session_count
prior_20_median_transaction_count
prior_20_median_dollar_volume
prior_20_zero_transaction_session_fraction
```

Candidate activity strata within each temporal cohort:

```text
A0 = no positive transaction-count observation
A1 = positive activity <= cohort positive p33
A2 = cohort positive p33 to p67
A3 = positive activity > cohort positive p67
AU = prior activity unavailable or insufficient
```

Positive percentiles are calculated once from the eligible development
inventory, recorded in the sample-design readout and frozen before reading
target trades.

### 7.4 Prior zero-activity prevalence

```text
Z1 = prior zero-session fraction >= 0.90
Z2 = prior zero-session fraction in [0.50, 0.90)
Z3 = prior zero-session fraction < 0.50
ZU = unavailable or insufficient prior sessions
```

### 7.5 Source-quality evidence

Foundation labels are mandatory metadata and not automatic exclusions.

For every label or local disposition with at least five feasible blocks in a
cohort, select at least five when compatible with the higher-priority price,
market-cap and activity margins. Scarce categories are included in full where
possible and recorded as shortfalls rather than silently replaced.

---

## 8. Deterministic selection algorithm

1. Build the complete development inventory using only information available
   before each candidate block starts.
2. Apply identity, common-stock, PIT market-cap and price eligibility.
3. Require 120 prior governed sessions; retain unavailable source contexts as
   blocked evidence.
4. Assign temporal, price, market-cap, prior-activity, zero-prevalence and
   quality strata.
5. Compute:

```text
selection_hash
= SHA256(
    "20260807" |
    cohort_id |
    instrument_id |
    block_start_session
  )
```

6. Select the lowest hashes subject to marginal quotas, instrument reuse and
   non-overlap constraints.
7. Fill remaining cohort capacity by lowest hash across feasible unselected
   blocks.
8. Freeze the selected and blocked manifests, their hashes and all shortfalls.

Prohibited selection inputs:

```text
target-session trade activity
scanner 500k appearance
known Wake-up or In-Play labels
gap size
future return
frontside outcome
chart review
human winner list
```

Replacement is permitted only for `LOCALLY_AUDITED_REPLACE_WINDOW`, from the
same cohort and closest feasible marginal strata, using the next deterministic
hash. Original and replacement rows must both remain in the manifest.

---

## 9. Denominator

For every selected target session:

```text
eligible RTH symbol-seconds
= every governed decision second from session open to session close
  under the frozen open/close boundary policy
```

No second may be removed because it contains:

```text
zero trades
no activation
unfavorable chart behavior
Foundation review label
locally degraded variables
```

Rows must preserve `OBSERVED_ZERO`, `DEGRADED`, `UNAVAILABLE` and
`OUT_OF_SCOPE` separately.

---

## 10. Binding A outputs

Target outputs remain separate:

```text
CURRENT_STATE
MULTISCALE_CONTRAST
PIT_BASELINE_AND_SURPRISE
```

The target session writes full outputs. Warmup sessions may be consumed through
a deterministic baseline cache and audit evidence without materializing all
warmup symbol-second feature rows, provided kernel equivalence against the
frozen implementation passes.

Normal-session row projection per target session:

```text
CURRENT_STATE              = 117,000
MULTISCALE_CONTRAST        = 46,800
PIT_BASELINE_AND_SURPRISE  = 70,200
TOTAL                      = 234,000
```

Approximate full target projection:

```text
2,400 normal-equivalent sessions
x 234,000 rows
= 561,600,000 representation rows
```

Early closes reduce this count. A preflight must calculate the exact expected
rows and compressed-size projection from the frozen sample manifest before a
human launch decision.

---

## 11. Required source and local audits

Every warmup and target instrument-session must preserve:

```text
physical trade source
acquisition evidence
Foundation label and reasons
coverage gate
trade eligibility disposition
unknown conditions
duplicates
timestamp and ordering findings
price and size validity
local variable-family disposition
affected variable IDs
```

No source label alone excludes a row. Variable-relevant local findings control
`USABLE`, `USABLE_WITH_FLAGS`, `DEGRADED` or `REPLACE_WINDOW`.

---

## 12. Implementation boundary

The AACT runner is single-instrument and contiguous-session scoped. TA-3
requires a new versioned orchestration layer that consumes a frozen sample
manifest and executes independent instrument-block work units.

Reusable components:

```text
Binding A computational kernels
condition policy
latency policy
coverage audit
atomic writers
hash sidecars
resume validation
post-run validator logic
```

Required new controls:

```text
sample-manifest hash binding
instrument-block work queue
block-level baseline cache
per-block heartbeat progress
block-level cooperative stop
cross-block row and grain validation
instrument reuse validation
development-lockbox guard
```

---

## 13. Long-running operation requirements

Before any broad run:

```text
pre-manifest
config and sample-manifest hashes
PID manifest
heartbeat latest and JSONL history
live log
output-size preflight
minimum free-space gate
cooperative stop
hash-validated resume
attempt and final manifests
independent post-run validation
```

The human launches the broad operation. An agent may design, implement, test,
smoke and present commands, but must not autonomously start it.

---

## 14. TA-3 acceptance gates

### 14.1 Sample-design gate

```text
PIT selector source gate passes
development and lockbox dates frozen
sample seed frozen
all requested contexts accounted
marginal quota shortfalls explicit
no prohibited selection input used
sample manifest and hash emitted
exact expected rows emitted
```

### 14.2 Execution gate

```text
all selected blocks audited
no silent block removal
complete symbol-second denominator
all expected rows and unique grains validate
all hashes validate
temporal violations = 0
lockbox reads = 0
kernel equivalence passes
independent validation passes
```

Exit verdict:

```text
STRATIFIED DEVELOPMENT SOURCE GATE
= PASS_WITH_RESTRICTIONS or FAIL
```

---

## 15. Authorization boundary after this plan

```text
TA-3 DESIGN
= PREREGISTERED

PIT INVENTORY AND SELECTOR AUDIT
= AUTHORIZED

RUNNER GENERALIZATION AND TESTS
= AUTHORIZED

FINAL SAMPLE MANIFEST
= PENDING PIT SELECTOR GATE

BROAD TA-3 MATERIALIZATION
= NOT_AUTHORIZED UNTIL MANIFEST FREEZE

BINDING B
= NOT_STARTED

OOS
= NOT_AUTHORIZED

MODEL ADMISSION
= NOT_AUTHORIZED

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

