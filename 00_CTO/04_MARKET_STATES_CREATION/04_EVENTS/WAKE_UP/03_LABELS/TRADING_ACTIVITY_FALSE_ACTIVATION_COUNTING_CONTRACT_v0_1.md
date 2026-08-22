# Trading Activity false activation counting contract v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_false_activation_counting_contract` |
| `document_version` | `v0_1` |
| `document_role` | `A_B_FALSE_ACTIVATION_EPISODE_COUNTING_DRAFT` |
| `document_status` | `AMENDED_DRAFT_BLOCKED_BY_LABEL_AND_HUMAN_TIMING_DECISIONS` |
| `created_at` | `2026-08-15` |

## 1. Fixed denominator

The denominator is the count of eligible symbol-seconds under the shared A/B
population, source, latency, missingness and observability contract. A second
is excluded only by a frozen eligibility reason applied identically to A and B.

## 2. Episode-counting state machine

The comparison counts episodes, not every above-threshold second.

```text
ARMED
-> first eligible second with score >= frozen threshold
-> OPEN episode; count one activation

OPEN
-> subsequent above-threshold seconds remain the same episode
-> below-threshold seconds accumulate a quiet run

OPEN + quiet run reaches quiet_close_seconds
-> CLOSED
-> begin rearm interval

CLOSED + rearm_seconds eligible seconds complete
-> ARMED

session boundary
-> close any open episode
-> reset to ARMED for the next governed session
```

Missing, unavailable or degraded seconds do not count as below-threshold quiet
seconds. They suspend the state machine until eligibility resumes or the
session ends.

## 3. Exact matching semantics

Every activation episode is matched one-to-one against the independent
Wake-up label manifest. Candidate matching uses the frozen label reference
onset and an asymmetric timing interval:

```text
episode opens at alert_timestamp_utc
label onset is reference_onset_timestamp_utc

match allowed iff:
  label onset - maximum_allowed_early_lead_seconds
  <= alert timestamp
  <= label onset + maximum_allowed_late_delay_seconds
```

Matching is performed in ascending event time within
`instrument_id + session_date`. When more than one alert is feasible for one
positive label, the earliest alert is matched and later alerts remain unmatched
unless a different positive episode is available. One alert cannot satisfy two
labels and one label cannot satisfy two alerts.

`AMBIGUOUS`, `UNAVAILABLE` and `NEGATIVE_DATA_ARTIFACT` never create a true
match. They remain separately reported and are excluded from the primary false-
activation numerator only according to a human-frozen quality policy; they are
never silently converted to ordinary economic negatives.

An unmatched alert inside an adjudicable negative/dormant denominator is one
false activation episode. Every eligible alert must resolve to exactly one of:

```text
TRUE_MATCHED_WAKE_UP
FALSE_UNMATCHED_ECONOMIC
EXCLUDED_AMBIGUOUS_LABEL
EXCLUDED_UNAVAILABLE_LABEL
EXCLUDED_DATA_ARTIFACT
```

## 4. Still-open numerical parameters

```text
quiet_close_seconds                  = BLOCKING_D07
rearm_seconds                        = BLOCKING_D07
maximum_allowed_early_lead_seconds   = BLOCKING_D07
maximum_allowed_late_delay_seconds   = BLOCKING_D07
```

These values affect episode count, precision and delay materially. They may not
be selected after inspecting temporal validation.

## 5. Label authority

An activation episode can be classified false only by an exact, versioned
negative-label authority evaluated over its governed assessment horizon.

```text
negative_label_manifest_path   = MISSING
negative_label_manifest_sha256 = MISSING
assessment_horizon             = BLOCKING_D07
```

Foundation data-quality labels and the halt-derived daily outcomes table are
not Wake-up negative-label authorities. The required upstream draft is
`WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md`; it is not yet frozen.

## 6. Budget derivation and proposal

```text
eligible_symbol_seconds_per_day
= shared A/B eligible denominator for the governed day

false_activation_budget_per_million
= maximum_tolerable_false_episodes_per_day
  / (eligible_symbol_seconds_per_day / 1,000,000)
```

The scientific owner must first approve the operational daily burden. The
current candidate remains:

```text
primary candidate            = 1.0 per 1,000,000 eligible symbol-seconds
diagnostic-only sensitivities = 0.5 and 2.0 per 1,000,000
```

It is not frozen and cannot be copied without reporting the implied false
episodes per governed day. Threshold calibration occurs in development only;
the threshold is then frozen for temporal validation.

## 7. Required metrics

```text
false activation episodes per 1,000,000 eligible symbol-seconds
false activation episodes per governed session
daily p50/p90/p95/max alert burden
true matched episodes
unmatched economic episodes
ambiguous/unavailable/artifact exclusions
median/p90/p95 detection delay for matched positives
```

## 8. Current verdict

```text
episode unit                       = DEFINED
threshold crossing semantics       = DEFINED
session reset                      = DEFINED
one-to-one matching policy          = DEFINED
quality outcome taxonomy            = DEFINED
quiet close / rearm                = OPEN_HUMAN_DECISION
early lead / late delay            = OPEN_HUMAN_DECISION
daily burden tolerance              = OPEN_HUMAN_DECISION
numeric budget                      = PROPOSED_NOT_FROZEN
negative-label authority           = MISSING
B02-D07                             = OPEN
```
