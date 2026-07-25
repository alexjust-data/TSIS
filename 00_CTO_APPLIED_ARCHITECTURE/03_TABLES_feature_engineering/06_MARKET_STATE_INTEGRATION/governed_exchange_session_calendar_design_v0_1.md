# Governed Exchange Session Calendar Design v0.1

Status: `design_ready_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `design_only_no_execution`
Prerequisite Closed Evidence: `experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS`

This document defines the governed exchange-session calendar layer required before any Scale B calendar-aware Market State execution.

It does not authorize calendar construction, source reads, builder execution, Market State integration, candidate materialization, parquet writing, production builders, State consumption, downstream use, full-history execution, full-universe execution or dataset promotion.

---

## 1. Decision

```text
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

governed_exchange_session_calendar_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

governed_exchange_session_calendar_binding_authorization = NOT_OPEN_NEXT
governed_exchange_session_calendar_binding_validation = NOT_AUTHORIZED
experimental_core_four_market_state_scale_b_authorization = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
experimental_core_four_market_state_scale_b_execution = NOT_AUTHORIZED

official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
state_consumption = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

The design closes because the calendar object, binding boundary, validation requirements, Scale B prerequisites and authority restrictions are now explicit.

---

## 2. Why This Exists

Scale A proved the core-four architecture across multiple instruments and contexts, but only under:

```text
fixed_utc_probe_calendar_v0_1
+
calendar compatibility guard
```

That evidence must not be reinterpreted as calendar-aware. Scale B requires a governed calendar because the US market session boundary changes in UTC across DST regimes and includes early closes, holidays and exceptional closures.

The next problem is not more rows. It is:

```text
Make market time a governed, versioned and validated dependency.
```

---

## 3. Existing Calendar Evidence

The repository already documents `001_market_calendar` as the relevant table representation.

Reference docs:

```text
02_TABLE_REPRESENTATION_REVIEW/001_market_calendar/001_market_calendar.md
02_TABLE_REPRESENTATION_REVIEW/001_market_calendar/001_market_calendar_representation_audit.md
```

Observed declared dataset:

```text
dataset_id = market_calendar_v0_1
calendar = XNYS
timezone = America/New_York
scope = 2005-01-03 to 2026-03-09
rows = 5328
physical_columns = 16
source = E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet
```

Observed schema fields:

```text
session_date
open_utc
close_utc
open_et
close_et
session_minutes
is_early_close
year
month
dow
calendar
timezone
source_calendar_artifact
build_run_id
schema_version
created_at_utc
```

This design treats `001_market_calendar` as the preferred source candidate for governed exchange-session boundaries, subject to a separate binding authorization and validation run.

---

## 4. Calendar Object

The governed calendar dependency is:

```text
governed_exchange_session_calendar
```

It represents:

```text
exchange session identity
legal market open and close boundaries
session length
timezone semantics
early-close status
calendar source lineage
calendar version
```

It does not represent:

```text
price behavior
volume behavior
liquidity
outcomes
signals
intraday phase features
operational State rows
```

---

## 5. Required Logical Contract

Minimum logical fields for Scale B:

```text
calendar_id
exchange_calendar_code
mic_or_exchange_code
session_date
session_open_utc
session_close_utc
session_open_local
session_close_local
timezone
session_minutes
session_type
is_regular_session
is_early_close
is_closed_or_holiday
calendar_version
source_calendar_artifact
source_snapshot_fingerprint
calendar_row_fingerprint
```

Mapping from observed `001_market_calendar` fields:

```text
calendar -> exchange_calendar_code
calendar -> mic_or_exchange_code when value is XNYS and no separate MIC field exists
session_date -> session_date
open_utc -> session_open_utc
close_utc -> session_close_utc
open_et -> session_open_local
close_et -> session_close_local
timezone -> timezone
session_minutes -> session_minutes
is_early_close -> is_early_close
schema_version -> calendar_version
source_calendar_artifact -> source_calendar_artifact
build_run_id -> source build lineage
created_at_utc -> source build lineage
```

`001_market_calendar` appears to contain trading sessions, not explicit closed-day rows. Therefore:

```text
is_closed_or_holiday = false for emitted session rows
closed_or_holiday evidence = derived from absence only if a separate expected-date universe is explicitly authorized
```

Scale B must not silently infer holiday rows unless that absence-based policy is authorized and validated.

---

## 6. Binding Boundary

The next executable unit is not Scale B. It is a calendar binding authorization:

```text
governed_exchange_session_calendar_binding_authorization_v0_1
```

That gate may authorize only:

```text
read bounded 001_market_calendar evidence
resolve physical path and snapshot
validate schema and logical mapping
emit calendar binding reports
emit a source snapshot fingerprint
emit no Market State candidate rows
write no Market State parquet
```

It must not authorize:

```text
builders
Information Object resolution
Market State integration
Market State materialization
Scale B execution
production use
downstream use
dataset promotion
full-history execution
full-universe execution
```

---

## 7. Required Binding Validation

The binding validation must prove:

```text
physical source exists
schema fields present
calendar = XNYS for all bound rows
timezone = America/New_York for all bound rows
session_date unique
open_utc < close_utc
open_et < close_et
UTC and local timestamps represent the same instants
session_minutes equals close_utc - open_utc in minutes
is_early_close is consistent with session_minutes < regular_session_minutes
calendar_version present
source_calendar_artifact present
source snapshot fingerprint present
calendar row fingerprints reproducible
```

Hard failures must be zero before Scale B can open.

---

## 8. Scale B Coverage Requirements

Scale B authorization must select sessions only from the accepted governed calendar binding and must include evidence for:

```text
winter regular session
summer regular session
US DST transition neighborhood
Europe/US DST desynchronization neighborhood when relevant
early-close session if observable in source scope
pre-bar context
regular intraday context
after_last_sampled_bar context with restricted semantics
```

Scale B acceptance must include:

```text
calendar boundary mismatches = 0
decision timestamp outside governed session when expected intraday = 0
future leaks = 0
decision-case semantic mismatches = 0
after_last_sampled_bar promoted to session_close = 0
fixed_utc_probe_calendar references admitted as current authority = 0
```

---

## 9. Scale A Preservation

Scale A remains accepted only as:

```text
multi-context evidence under fixed UTC compatibility guard
```

It must not be rewritten or relabeled as:

```text
calendar-aware evidence
historical session validation
operational Market State
production State
```

---

## 10. Next Gate

```text
next_allowed_gate = governed_exchange_session_calendar_binding_authorization_v0_1
```

The next gate should bind and validate existing `001_market_calendar` evidence for the bounded Scale B path. Scale B authorization remains blocked until that binding validation closes with restrictions or better.
