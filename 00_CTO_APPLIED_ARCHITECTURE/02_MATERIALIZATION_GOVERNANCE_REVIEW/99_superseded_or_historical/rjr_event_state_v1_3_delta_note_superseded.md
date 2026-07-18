# rjr_event_state_v1_3

Status: `candidate_record_v1_3`

Governed by:

``` text
representation_justification_contract_v0_8
```

Governance Scope:

``` text
candidate_governance
```

Derived from:

``` text
01_questions.md
```

Supersedes:

``` text
rjr_event_state_v1_2
```

> This revision only applies one consistency change:
>
> `event_state_schema_version` → `state_schema_version`

All remaining content is identical to `rjr_event_state_v1_2`.

## Granularity

Conceptual granularity:

``` text
event_window_id
+ decision_timestamp_utc
+ state_role
+ state_schema_version
```

This is aligned with the current Event State composition/schema
contracts.

## RJR Validity

``` text
rjr_validity = true
```

## Effective Acceptance

``` text
effective_acceptance = false
```

Reason:

``` text
decision = not_reviewed
```

## MDR Authorization

``` text
mdr_authorization = false
```

The record is now ready for formal architectural review.
