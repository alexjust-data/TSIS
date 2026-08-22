# Wake-up blind review protocol v0.1

Status: `DRAFT_NOT_EXECUTED`

## Reviewer-visible evidence

```text
blind case_id;
relative and RTH wall-clock time;
trade count per second;
distinct timestamp clusters per second;
share and dollar volume per second;
event raster and inter-cluster timing;
source coverage, duplicate and quality companions;
candidate interval and candidate discovery reason.
```

## Reviewer-hidden evidence

```text
Binding A/B identity, variables and scores;
scanner-selection state;
price path and direction;
rebreak/HOD;
returns, PnL, MFE/MAE and strategy outcomes;
temporal-validation or final-OOS membership/results.
```

## Review record

Each reviewer emits one immutable row per assigned case:

```text
reviewer_id
case_id
label_class
onset_interval_start_utc
onset_interval_end_utc
confidence
reason_codes
review_status
protocol_id
created_at_utc
```

Allowed classes are inherited from
`WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md`.

## Adjudication

Agreement is accepted directly. Disagreement receives a separate adjudicator
record retaining both original rows. `AMBIGUOUS` and `UNAVAILABLE` are valid
terminal review outcomes and cannot be coerced to negatives.

