# Core Four Market State Integration Design v0.1

Status: `design_ready_with_restrictions_v0_1`
Date: `2026-07-21`
Scope: `design_only_no_execution`
Profile: `market_state_core_four_intraday_experimental_v0_1`

This document defines how the accepted core-four Information Object resolution
records may be integrated into an experimental Market State profile.

It does not execute integration.
It does not read source market tables.
It does not materialize parquet.
It does not authorize downstream consumption.
It does not authorize production builders.

## 1. Decision

```text
core_four_builder_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_market_state_integration_execution = NOT_OPEN
market_state_materialization = NOT_AUTHORIZED
production_builder = NOT_AUTHORIZED
```

The design is allowed because the record acceptance review verified the 40
core-four records from:

```text
experimental_state_builder_probe_v0_10_20260721T193918Z
```

Reference review:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_core_four_resolution_record_acceptance_review_v0_1.md
```

## 2. Integration Unit

The integration unit is not an individual object request.

```text
request_id != Market State join key
```

The experimental join key is:

```text
context_id
```

The semantic join key is:

```text
instrument_id
+ ticker
+ session_date
+ decision_timestamp_utc
+ decision_case
```

A future execution probe may compute:

```text
market_state_candidate_id =
sha256(
    market_state_profile_id
    + semantic_join_key
    + context_input_fingerprint
)
```

## 3. Required Object Set

Each accepted context must contain exactly these four records:

```text
trading_activity
price_movement
price_location_structure
volatility_range_state
```

No quote-dependent object may enter this profile.

## 4. Context Acceptance Rules

A context is eligible for integration only if all of these hold:

```text
exactly 4 records per context_id
exactly the required core-four object_ids
same ticker
same instrument_id
same session_date
same decision_timestamp_utc
same decision_case
same 004 daily evidence
same 014 selected bar evidence
no future_bar_leak
all output contracts pass
all determinism checks pass
```

The acceptance review already produced one shared:

```text
context_input_fingerprint
```

per context.

## 5. Object Atomicity

Object atomicity is required for this first Market State profile.

```text
if object resolution_status in PASS / PASS_WITH_RESTRICTIONS:
    admit all produced object values

if object resolution_status starts with BLOCKED:
    admit no values from that object
    write rejection/diagnostic evidence only
```

Blocked records may contain partial diagnostic values. Those values are not
Market State values.

Reason:

```text
A Market State row must not silently mix complete Objects with partial blocked
Objects unless a separate partial-object profile is explicitly approved.
```

## 6. Context Status Policy

Allowed context statuses:

```text
INTEGRABLE_COMPLETE
    all four Objects pass without restrictions.

INTEGRABLE_COMPLETE_WITH_RESTRICTIONS
    all four Objects pass or pass with restrictions.

REJECTED_REQUIRED_OBJECT_BLOCKED
    at least one required Object is blocked.
    No Market State row may be emitted.

FAILED_CONTEXT_CONSISTENCY
    identity, timestamp or shared evidence differs across records.

FAILED_CONTRACT_OR_DETERMINISM
    output contract, cutoff or determinism evidence failed.
```

In the v0.10 reference sample:

```text
contexts_reviewed = 10
integrable_contexts_expected = 8
rejected_required_object_blocked_contexts_expected = 2
```

The two rejected contexts are pre-bar contexts. They are valid diagnostic
cases, not State rows.

## 7. Candidate Output Shape

An integration execution probe may emit a non-materialized candidate record
with this conceptual shape:

```text
market_state_candidate_id
market_state_profile_id
context_id
instrument_id
ticker
session_date
decision_timestamp_utc
decision_case
context_input_fingerprint
integration_status
object_statuses
object_record_ids
admitted_namespaces
values
shared_source_evidence
policy_versions
restrictions
```

Allowed value namespaces:

```text
trading_activity__*
price_movement__*
price_location_structure__*
volatility_range_state__*
```

No field outside those namespaces may be admitted into this profile.

## 8. Shared Evidence And Lineage

The integrated candidate must preserve shared evidence once per context:

```text
004 daily file path
004 row ordinal
selected price_view
014 intraday file path
014 selected row ordinal
014 selected_bar_end_utc
014 duplicate classification
context_input_fingerprint
policy versions
```

The four object-level records remain the provenance source for object-specific
values and restrictions.

## 9. Cross-Object Semantic Rules

These semantic equalities must continue to hold when values are admitted:

```text
price_movement__intraday_return_vs_prior_close_ratio
=
price_location_structure__intraday_return_vs_prior_close_ratio_as_location

price_movement__intraday_return_vs_session_open_ratio
=
price_location_structure__intraday_return_vs_session_open_ratio_as_location
```

They are equal numerically but remain in different namespaces because they
answer different scientific questions.

## 10. Preserved Restrictions

### Session Calendar

v0.10 uses fixed UTC session times:

```text
13:30:00 -> 20:00:00 UTC
```

This is acceptable for the bounded probe but not canonical. Operational design
must replace it with:

```text
governed_exchange_session_calendar
session_open_utc
session_close_utc
session_type
calendar_version
```

### Sample End Case

```text
after_last_sampled_bar
```

means after the last sampled input bar, not after exchange close and not final
session state.

### Trading Activity RVOL

The current metric is:

```text
session_volume_to_time / prior_20_full_session_volume_mean
```

It is not same-time-of-day historical RVOL. Naming and mapping must preserve
that exact meaning.

### Duplicate Metrics

Duplicate evidence in v0.10 is request-impact evidence. A future dataset audit
must separately report physical duplicate group counts.

### Quote-Dependent Objects

Quote-dependent objects remain blocked pending:

```text
raw_quotes.as_of_utc
raw_quotes.quote_ordering_key
```

They cannot enter this profile.

## 11. Non-Authority

This design does not authorize:

```text
parquet materialization
full-history execution
full-universe execution
production scheduling
downstream ML/RL consumption
event detection consumption
quote-dependent object integration
dataset promotion
```

## 12. Next Gate

The next gate is not execution by default. It must be separately authorized:

```text
experimental_core_four_market_state_integration_execution_authorization_v0_1
```

That future authorization must define:

```text
input run id
maximum contexts
allowed records file
allowed output directory
whether candidate JSONL output is permitted
whether rejected-context report output is permitted
maximum rows emitted
no parquet materialization
no downstream consumption
```

## 13. Contract Artifact

Machine-readable contract:

```text
core_four_market_state_integration_design_contract_v0_1.json
```
