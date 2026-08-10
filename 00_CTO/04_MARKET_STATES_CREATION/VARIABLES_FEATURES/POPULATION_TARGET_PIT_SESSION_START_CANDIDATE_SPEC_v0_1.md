# POPULATION_TARGET_PIT_SESSION_START_CANDIDATE_SPEC_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_pit_session_start_candidate_spec` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_DAILY_PIT_SELECTOR_SPECIFICATION` |
| `document_status` | `SPECIFIED_AS_DRAFT` |
| `controlled_fixture_execution` | `AUTHORIZED` |
| `full_materialization` | `NOT_AUTHORIZED_YET` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `owner_layer` | `01_TSIS_DATA_FOUNDATION` |
| `consumer_workstream` | `wake_up_trading_activity_ta_3` |
| `created_at` | `2026-08-07` |

## 1. Purpose

Build the daily, causal eligibility context needed to answer at the start of
each session:

```text
Was this resolved common-stock instrument observable with
$0.50 <= prior eligible price <= $20
and market-cap proxy < $100M
using only information available before the session opened?
```

This candidate is a daily universe and stratification context. It is not a
Trading Activity feature, scanner result, Wake-up Event or intraday market-cap
series.

## 2. Dataset identity and grain

```text
dataset_id
= population_target_pti_session_start_candidate_v0_1

grain
= instrument_id x session_date

primary key
= population_context_id
```

`ticker + session_date` is prohibited as a primary key because the recovered
legacy panel proves that ticker reuse can create overlapping identities.

## 3. Governed inputs

### Required primary inputs

```text
master_daily_table_v0_1
  price_view = daily_raw
  session spine + prior_close + corporate-action context

fundamentals_asof_table_v0_1
  income-statement share measures + filing/as-of lineage

instrument_master_v0_1
  stable instrument identity and common-stock context

corporate_actions_table_v0_1
  split and ticker-change context
```

### Reconciliation-only input

```text
population_target_pti_legacy_run_01
```

The recovered legacy panel may support fixtures and reconciliation. It is not
the primary session-start source and cannot be renamed as this candidate.

## 4. Session spine

The candidate starts from exactly one `daily_raw` row per governed
instrument-session in `master_daily_table_v0_1`.

Every source row is retained with an explicit state. Missing data does not
silently remove a denominator row.

Required source projection:

```text
instrument_id
ticker
session_date
expected_session
expected_reason
data_present
prior_close
row_level_price_integrity_state
selected_price_hard_invalid
corporate-action flags and lineage
```

Foundation quality labels are evidence. They do not cause automatic exclusion
without a variable-relevant local audit. Causal violations and unresolved
identity collisions remain hard blockers for the affected row.

## 5. Price at session start

Primary candidate:

```text
price_at_session_start
= daily_raw.prior_close
```

Required legality:

```text
prior_close belongs to a completed earlier session
prior_close was available before target session open
target-session open/high/low/close are not used
```

Base price state:

```text
PRICE_AVAILABLE
PRICE_UNAVAILABLE
PRICE_NONPOSITIVE
PRICE_OUTSIDE_PROFILE
CORPORATE_ACTION_REVIEW
```

A split effective between the prior close and the target session open requires
a governed bridge or a local review disposition. Raw prior close cannot be
silently combined with post-split shares.

## 6. Shares as of session start

Candidate source observations are income-statement rows with:

```text
as_of_date < session_date
finite positive candidate share measure
age at session start <= 180 calendar days
```

The strict `< session_date` rule is mandatory because the source provides only
date-level filing availability. Same-date filings are conservatively treated
as unavailable before the session opens.

Measure priority:

```text
1. basic_shares_outstanding
   measure_type = BASIC_WEIGHTED_AVERAGE_SHARES_PROXY

2. diluted_shares_outstanding
   measure_type = DILUTED_WEIGHTED_AVERAGE_SHARES_PROXY
   use only when basic is unavailable
```

Neither measure may be named:

```text
legal_common_shares_outstanding
float_shares
free_float
```

Selection order for multiple admissible observations:

```text
as_of_date descending
period_end descending
basic-before-diluted measure priority
fundamental_asof_id ascending as deterministic final tie-break
```

The chosen row must preserve:

```text
fundamental_asof_id
as_of_date
period_end
measure_type
source value
age days
source quality labels
local audit disposition
```

## 7. Market-cap proxy

```text
market_cap_proxy_at_session_start
= price_at_session_start
   x shares_proxy_as_of_session
```

The column name must retain `proxy` until exact historical legal shares
outstanding are available and validated.

Calculation states:

```text
CALCULATED_PROXY
PRICE_UNAVAILABLE
SHARES_UNAVAILABLE
SHARES_STALE
IDENTITY_REVIEW
CORPORATE_ACTION_REVIEW
SOURCE_SEMANTICS_REVIEW
```

## 8. Profile membership

Numeric candidate rules:

```text
0.50 <= price_at_session_start <= 20.00
market_cap_proxy_at_session_start < 100,000,000
```

Boundary rules:

```text
price = 0.50       included
price = 20.00      included
market cap = 100M excluded
```

Membership states:

```text
ELIGIBLE_PROXY
INELIGIBLE_PRICE
INELIGIBLE_MARKET_CAP_PROXY
UNAVAILABLE_PRICE
UNAVAILABLE_SHARES
STALE_SHARES
OUTSIDE_INSTRUMENT_VALIDITY
IDENTITY_REVIEW
CORPORATE_ACTION_REVIEW
SOURCE_SEMANTICS_REVIEW
```

`ELIGIBLE_PROXY` is research eligibility under the declared proxy. It is not a
claim that exact legal market cap or float is known.

## 9. Required output fields

```text
population_context_id
instrument_id
ticker_as_of_session
session_date
session_open_utc
expected_session
instrument_validity_state
common_stock_state
price_at_session_start
price_source
price_state
shares_proxy_as_of_session
shares_measure_type
shares_as_of_date
shares_period_end
shares_age_days
shares_source_row_id
market_cap_proxy_at_session_start
market_cap_calculation_state
price_eligibility_state
market_cap_eligibility_state
population_membership_state
population_membership_reason
foundation_quality_labels
local_audit_disposition
blocked_reason_codes
master_daily_id
fundamental_asof_id
schema_version
build_run_id
lineage_manifest_id
```

## 10. Missingness and denominator

The candidate must conserve:

```text
requested instrument-sessions
= eligible proxy rows
 + ineligible numeric rows
 + unavailable rows
 + review rows
 + outside-validity rows
```

It is prohibited to convert:

```text
missing shares -> zero shares
missing prior close -> zero price
review state -> automatic global exclusion
unavailable market cap -> market cap above threshold
```

## 11. Controlled fixture gate

Before broad materialization, executable tests must cover:

```text
normal prior-close session
same-date filing excluded at session start
latest prior-date filing selected
basic share proxy preferred
diluted proxy fallback
stale shares after 180 days
missing shares
missing prior close
split-effective session
ticker reuse with two entities
duplicate source observations and deterministic tie-break
$0.50 price boundary
$20 price boundary
$100M market-cap boundary
```

Required verdict:

```text
CONTROLLED_FIXTURE_GATE
= PASS
```

## 12. Probe before broad run

After fixtures pass, execute a small probe spanning:

```text
at least one session from each TA-3 development cohort
all four market-cap bands
all five price bands
normal, unavailable, stale and review states
at least one corporate-action case
at least one recovered identity-collision case
```

The probe must emit full requested/resolved/blocked accounting and preserve
row-level lineage.

## 13. Broad materialization gate

The full daily panel contains approximately 7.37 million operational-universe
instrument-session rows. It is a long-running governed operation and requires:

```text
pre-manifest
frozen config
run_id
PID and heartbeat
live log
separate monitor
output root with no overwrite
partition hashes
final manifest
independent validator
```

Full materialization is not authorized until fixture and probe readouts pass.

## 14. Relationship with float

```text
market_cap proxy
!=
float
```

`float_context_table` remains a parallel source-audit workstream. Its absence
does not block this candidate's controlled fixtures, but exact float-dependent
scanner rules cannot be claimed until that table exists.

## 15. TA-3 authorization boundary

```text
candidate spec complete
-> controlled fixtures
-> controlled probe
-> selector gate readout
-> broad daily materialization
-> deterministic TA-3 sample manifest
-> Trading Activity A/B/C comparison
```

No target-session Trading Activity, scanner appearance, gap outcome, chart
pattern or future Wake-up label may influence population membership.
