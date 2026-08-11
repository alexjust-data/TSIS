# SEC PIT Resolved Daily States Schema Contract `v0_2`

Status: `experimental_schema_contract_not_canonically_promoted`
Owner: `01_TSIS_DATA_FOUNDATION`
Supersedes: `sec_pit_resolved_daily_states_schema_contract_v0_1.md` for new runs
Breaking change: `float_percent_estimate_as_known` unit correction and explicit
fraction field

## Role and promotion boundary

This contract governs new experimental daily PIT resolutions derived from SEC
PIT source observations. It does not promote a canonical float dataset and does
not authorize scanner, backtest, ML/RL or live consumption.

Historical `v0_1` outputs are preserved. They must not be silently relabeled or
rewritten because the BNAI implementation stored a 0–1 ratio in a field named
`float_percent_estimate_as_known`.

## Common grain

```text
one instrument_id x session_date x methodology_id
```

Missing or blocked estimates remain NULL and are never coerced to zero or to
shares outstanding.

## daily_float_state required order

```text
instrument_id
session_date
schema_version
shares_outstanding_estimate_as_known
float_owner_exclusion_estimate_as_known
float_fraction_estimate_as_known
float_percent_estimate_as_known
unique_supported_excluded_shares
methodology_id
ownership_baseline_accession
ownership_baseline_eligible_from_session
ownership_update_observation_count
ownership_update_latest_transaction_date
ownership_conflict_state
estimation_state
blocker_codes
```

`schema_version` must equal:

```text
sec_pit_resolved_daily_states_v0_2
```

## Unit contract

```text
float_fraction_estimate_as_known
= float_owner_exclusion_estimate_as_known
  / shares_outstanding_estimate_as_known
unit = ratio
valid range = [0, 1]

float_percent_estimate_as_known
= 100 * float_fraction_estimate_as_known
unit = percent
valid range = [0, 100]
```

The two fields are not aliases. A value of `0.75` is a fraction; the matching
percent is `75.0`.

## Invariants

```text
estimation_state in {
  BLOCKED_BY_INPUT_GATES,
  OWNERSHIP_BASELINE_UNAVAILABLE,
  POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED,
  SHARES_OUTSTANDING_UNAVAILABLE,
  SHARES_OUTSTANDING_NON_POSITIVE,
  EXCLUDED_SHARES_EXCEED_OS
}
->
float_owner_exclusion_estimate_as_known = NULL
float_fraction_estimate_as_known = NULL
float_percent_estimate_as_known = NULL
blocker_codes is non-empty
```

For every calculated row:

```text
0 <= unique_supported_excluded_shares <= shares_outstanding_estimate_as_known
0 <= float_owner_exclusion_estimate_as_known <= shares_outstanding_estimate_as_known
0 <= float_fraction_estimate_as_known <= 1
0 <= float_percent_estimate_as_known <= 100
abs(float_percent_estimate_as_known - 100 * float_fraction_estimate_as_known)
  <= governed numeric tolerance
```

## daily_tradability_state

The `v0_1` tradability fields remain structurally unchanged. Tradability is a
separate lane and does not inherit owner-exclusion float as proof of freely
tradable supply.

## Migration rule

New runs must emit `v0_2`. Existing outputs without
`float_fraction_estimate_as_known` remain historical `v0_1` evidence. Consumers
must not infer the legacy unit from the column name alone; they must use the run
and schema lineage.
