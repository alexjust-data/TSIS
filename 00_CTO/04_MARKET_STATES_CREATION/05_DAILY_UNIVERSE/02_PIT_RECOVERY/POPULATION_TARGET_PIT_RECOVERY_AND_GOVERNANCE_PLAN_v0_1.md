# POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_pit_recovery_and_governance_plan` |
| `document_version` | `v0_1` |
| `document_role` | `UPSTREAM_PIT_SELECTOR_RECOVERY_PLAN` |
| `document_status` | `ACTIVE_DEPENDENCY_PLAN` |
| `owner_layer` | `01_TSIS_DATA_FOUNDATION` |
| `consumer_workstream` | `wake_up_trading_activity_ta_3` |
| `legacy_artifact_location` | `UNRESOLVED` |
| `rebuild_status` | `NOT_STARTED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |

---

## 1. Purpose

Recover, validate or rebuild the daily point-in-time population panel needed
to answer:

```text
Was instrument i a common-stock candidate with
market cap < $100M and price between $0.50 and $20
using only information available before session s?
```

This is an upstream universe and stratification dataset. It is not a Trading
Activity feature table, scanner output, Wake-up Event or In-Play label.

---

## 2. Historical evidence

Preserved certification states that `population_target_pti.parquet` was built:

```text
rows_total        = 29,735,570
tickers_total     = 13,066
date_min          = 2005-01-01
date_max          = 2026-03-09
rows_classifiable = 10,278,625
anti-lookahead    = 0
shares TTL        = 180 days
```

Historical formula:

```text
market_cap_t = close_t x shares_outstanding_t
```

The preserved path belongs to a retired module root and the physical parquet
has not yet been resolved under the current workspace or physical data plane.
This is a recovery problem, not evidence that the panel was never built.

---

## 3. Current reusable sources

### Daily spine

```text
master_daily_table_v0_1
4,824 tickers
7,369,699 expected instrument-session rows per price view
2005-01-03 through 2026-03-09
```

### Fundamentals as-of

```text
fundamentals_asof_table_v0_1
621,756 statement observations
4,813 tickers
2010-04-22 through 2026-04-03
```

Candidate share fields:

```text
basic_shares_outstanding
diluted_shares_outstanding
```

### Identity and operational universe

```text
instrument_master_v0_1
lt1b_universe_v0_1
market_calendar_v0_1
corporate_actions_table_v0_1
```

`instrument_master.lt1b_market_cap_t` is one last-observed context per ticker.
It is reconciliation evidence and cannot replace daily membership.

---

## 4. Recovery-first rule

Before rebuilding:

1. search manifests, backups and migrated run roots for the original parquet,
   summary, year summary, build config and source script;
2. preserve any recovered artifact byte-for-byte;
3. hash and register it as historical evidence;
4. do not silently rename it as a new governed dataset;
5. compare its output with a reproducible rebuild over fixed fixtures.

Possible recovered identity:

```text
population_target_pti_legacy_run_01
```

Recovery does not by itself authorize current consumption.

---

## 5. New governed panel

Candidate dataset identity:

```text
population_target_pti_session_start_candidate_v0_1
```

Grain:

```text
instrument_id x session_date
```

It covers every resolvable instrument-session in the operational candidate
pool, not a blind Cartesian product and not only selected TA-3 cases.

Required fields:

```text
population_context_id
instrument_id
ticker_as_of_session
session_date
session_open_utc
listing_state_as_of_session
security_type_as_of_session
is_common_stock_as_of_session
operational_lt1b_window_state
prior_close_eligible
prior_close_source
prior_close_available_at
shares_outstanding_as_of_session
shares_measure_type
shares_effective_at
shares_available_at
shares_age_days
shares_source
shares_source_row_id
market_cap_at_session_start
market_cap_calculation_state
price_eligibility_state
market_cap_eligibility_state
population_membership_state
population_membership_reason
quality_state
blocked_reason_codes
schema_version
build_run_id
lineage_manifest_id
```

---

## 6. Temporal formula

For a target session `s`:

```text
shares_as_of_session(s)
= latest accepted shares observation
  with shares_available_at <= session_open_utc(s)
  and shares_age_days <= governed TTL

price_at_session_start(s)
= prior_close_eligible known before session open

market_cap_at_session_start(s)
= shares_as_of_session(s) x price_at_session_start(s)
```

The initial compatibility rebuild uses the historically documented primary TTL
of `180` days. TTL sensitivity may be evaluated separately, but cannot change
the primary panel in place.

The panel must distinguish:

```text
CALCULATED
SHARES_UNAVAILABLE
SHARES_STALE
PRICE_UNAVAILABLE
IDENTITY_BLOCKED
CORPORATE_ACTION_REVIEW
SOURCE_SEMANTICS_REVIEW
```

No future share observation may be backfilled into an earlier session.

---

## 7. Shares source audit

`basic_shares_outstanding` and `diluted_shares_outstanding` may represent
period averages rather than point-in-time legal common shares. Before use, the
audit must establish:

```text
source field definition
accounting period meaning
filing-date availability
amendment and restatement behavior
units and scaling
split behavior
common versus diluted share meaning
coverage by ticker and year
missingness and stale intervals
```

Source priority must be explicit. A fallback source receives a different
`shares_measure_type`, source ID and quality state; it may not masquerade as an
equivalent primary observation.

---

## 8. Price policy

For historical scanner eligibility, use the price legally observable before
the session begins. Do not use the target-session close.

Primary candidate:

```text
master_daily_table_v0_1
price_view = daily_raw
field = prior_close
```

Corporate actions effective before session open require a governed bridge so
that the prior close represents the price an observer would have used at that
time. Retrospective `adjusted` or `split_normalized` price views cannot be
substituted silently.

---

## 9. Dynamic intraday market cap

The daily panel is not expanded to one-minute or one-second rows.

At runtime or replay:

```text
market_cap_as_of(t)
= shares_outstanding_as_of(t) x eligible_price_as_of(t)
```

Before the first eligible trade, the price fallback is the governed prior
close. Afterward, the consuming profile must declare the eligible trade,
midprice or other observable price policy.

Required distinction:

```text
daily_eligibility_at_session_start
dynamic_eligibility_as_of_t
```

The daily state provides a stable scientific denominator. Dynamic membership
is a separate scanner/runtime policy and must not rewrite the daily panel.

---

## 10. Validation gates

```text
schema and grain validation
requested = resolved + excluded + blocked
no duplicate instrument-session keys
shares_available_at <= session_open_utc
prior_close_available_at <= session_open_utc
no target close used at session start
shares TTL enforced
corporate-action fixtures pass
ticker-change fixtures pass
market-cap formula recomputes exactly
legacy equivalence fixtures recorded where recoverable
coverage by year, price and market-cap band emitted
deterministic rebuild hash passes
```

Required verdict:

```text
POPULATION_TARGET_PIT_SELECTOR_GATE
= PASS
  PASS_WITH_RESTRICTIONS
  or FAIL
```

Only `PASS` or an explicitly accepted `PASS_WITH_RESTRICTIONS` may unblock the
TA-3 sample manifest.

---

## 11. Data Foundation deliverables

```text
canonical schema candidate
dataset contract candidate
consumption policy
registry entry candidate
source observability audit
builder and config
validators and fixtures
pre-manifest and final manifest
coverage and reconciliation readout
selector-gate decision
```

Proposed physical root after authorization:

```text
G:/TSIS/data/data_foundation_outputs/
population_target_pti_session_start_candidate_v0_1/
```

No output may overwrite `master_daily_table`, `instrument_master`, the
historical population panel or any raw source.

