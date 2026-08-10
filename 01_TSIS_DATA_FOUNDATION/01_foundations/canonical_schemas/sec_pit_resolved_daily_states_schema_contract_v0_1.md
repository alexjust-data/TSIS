# SEC PIT Resolved Daily States Schema Contract v0_1

## Role

This contract governs experimental daily PIT resolutions derived from
sec_pit_source_observations_v0_1. These tables are methodology-dependent
research outputs. They are not observed facts and are not canonically promoted.

## Common grain

~~~
one instrument_id x session_date x methodology_id
~~~

Missing or blocked estimates must remain NULL; they must never be coerced to
zero or to shares outstanding.

## daily_float_state

Required columns:

~~~
instrument_id
session_date
shares_outstanding_estimate_as_known
float_owner_exclusion_estimate_as_known
float_percent_estimate_as_known
unique_supported_excluded_shares
methodology_id
estimation_state
blocker_codes
~~~

Invariant:

~~~
estimation_state = BLOCKED_BY_INPUT_GATES
->
all float estimate fields = NULL
blocker_codes is non-empty
~~~

## daily_tradability_state

Required columns:

~~~
instrument_id
session_date
float_owner_exclusion_estimate_as_known
float_tradability_eligibility_estimate_as_known
restricted_or_locked_shares_estimate_as_known
methodology_id
estimation_state
blocker_codes
~~~

Invariant:

~~~
estimation_state = BLOCKED_BY_INPUT_GATES
->
all tradability estimate fields = NULL
blocker_codes is non-empty
~~~

Tradability eligibility is not confirmed entry into freely tradable supply.

## Promotion boundary

~~~
status = experimental_one_ticker
canonical_promotion = not_authorized
scanner_consumption = not_authorized
~~~