# Wake-up label and negative definition contract v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `wake_up_label_and_negative_definition_contract` |
| `document_version` | `v0_1` |
| `document_role` | `OUTCOME_ONLY_LABEL_SEMANTICS_DRAFT` |
| `document_status` | `DRAFT_FOR_EXPLICIT_HUMAN_SCIENTIFIC_FREEZE` |
| `information_object_scope` | `wake_up_detection_evaluation` |
| `binding_a_or_b_feature_authority` | `false` |
| `implementation_authorized` | `false` |
| `label_materialization_authorized` | `false` |
| `created_at` | `2026-08-15` |

## 1. Normative semantic authority

This contract specializes, but does not redefine:

```text
01_WAKE_UP_EVENT_DEFINITION.md
SHA-256
= 1ff56c25744d069cbdac997af628c174a61215209dbd82ac8c7275bc67a9aa46
```

The inherited meaning is:

```text
Wake-up
= the first minimally corroborated transition within an episode
  from a PIT-dormant/low-activity regime
  to materially anomalous realized participation

Wake-up
!= price continuation
!= profitable entry
!= In-Play confirmation
!= frontside direction
!= tradability
```

Labels are retrospective outcome-only truth for detector evaluation. They are
stored outside Binding A, Binding B, market state and event state.

## 2. Anti-circularity boundary

The label oracle and candidate-reduction process must not import or inspect:

```text
Binding A variables, percentiles or detector scores
Binding B variables, kernels, durations or detector scores
A/B comparison results
scanner 500k selection or appearance time
strategy returns, PnL, MFE, MAE or fills
future price direction or HOD/frontside status
```

The oracle may consume only the frozen eligible raw trade/quote evidence,
quality/coverage metadata, PIT context needed to establish the prior dormant
regime and the explicitly frozen retrospective confirmation interval.

Candidate generation is recall-oriented workload reduction. Candidate presence
is not a label. The definitive label is emitted only by the frozen oracle and
its blind audit/adjudication protocol.

## 3. Label unit and timestamps

Logical grain:

```text
label_contract_id
+ instrument_id
+ session_date
+ episode_id
```

Required timestamps:

```text
reference_onset_timestamp_utc
= retrospective onset produced by the outcome-only oracle

confirmation_window_end_utc
= last timestamp inspected to establish minimum corroboration

label_available_at_utc
= first timestamp at which the retrospective label is complete
```

`reference_onset_timestamp_utc` may precede `label_available_at_utc`. It is
research-only and prohibited as a causal feature at the earlier time.

## 4. Primary classes

```text
POSITIVE_WAKE_UP
NEGATIVE_ONE_PRINT
NEGATIVE_INSUFFICIENT_CORROBORATION
NEGATIVE_CONTEXT_NORMAL_HIGH_ACTIVITY
NEGATIVE_DATA_ARTIFACT
AMBIGUOUS
UNAVAILABLE
```

Class meanings:

- `POSITIVE_WAKE_UP`: the prior regime is dormant/low-activity and the raw
  evidence crosses the frozen relative, de-minimis and corroboration rules.
- `NEGATIVE_ONE_PRINT`: the apparent transition is explained by one eligible
  print/timestamp cluster and fails the corroboration quorum.
- `NEGATIVE_INSUFFICIENT_CORROBORATION`: more than one observation exists but
  the frozen independent-event/source quorum is not met.
- `NEGATIVE_CONTEXT_NORMAL_HIGH_ACTIVITY`: activity is high in absolute terms
  but not anomalous relative to the prior PIT context.
- `NEGATIVE_DATA_ARTIFACT`: correction, ineligible condition, duplicate/data
  defect or temporal inconsistency explains the candidate.
- `AMBIGUOUS`: valid evidence exists but the frozen oracle cannot distinguish
  positive from economic negative with the available resolution.
- `UNAVAILABLE`: source, baseline, timestamp resolution or coverage is
  insufficient to adjudicate.

## 5. Failed activation is not a negative Wake-up

The semantic authority explicitly states that later failure does not invalidate
a causally valid Wake-up. Therefore:

```text
POSITIVE_WAKE_UP
+ later FAILED_ACTIVATION
= positive Wake-up label
  plus a separate episode outcome
```

`NEGATIVE_TRANSIENT_BURST` is not an allowed primary class because it would
silently mix Wake-up truth with later persistence. A brief candidate is negative
only when it fails the frozen minimum antinartefact corroboration rule. Economic
persistence and continuation belong to episode outcomes/In-Play.

## 6. Episode multiplicity

More than one positive Wake-up may occur in one session only when:

```text
prior episode CLOSED
+ frozen dormant/rearm conditions satisfied
+ a new independently corroborated transition occurs
```

Bursts while an episode is active are `REACTIVATION` or `RENEWED_ACTIVITY`, not
new primary Wake-ups. Session boundary closes the label-search state but does
not fabricate a positive or negative class.

## 7. Quality and abstention

The oracle must abstain rather than coerce uncertainty:

```text
broken or contradictory source        -> UNAVAILABLE or NEGATIVE_DATA_ARTIFACT
insufficient PIT dormant baseline      -> UNAVAILABLE
insufficient distinct timestamp support -> UNAVAILABLE
valid but scientifically undecidable   -> AMBIGUOUS
```

`AMBIGUOUS`, `UNAVAILABLE` and data artifacts are preserved in accounting and
cannot be folded into generic negatives for primary detector fitting.

## 8. Blind audit protocol

Primary proposal:

```text
frozen deterministic oracle
+ blind human audit of a stratified sample
+ adjudication of disagreements
```

Reviewers may see raw eligible evidence and quality/context companions only.
They may not see A/B identity, scores, selected model, strategy outcomes or PnL.
Every adjudication records oracle version, review status and reason code.

## 9. Blocking numerical decisions

The semantic boundary above is fixed for this draft. The following values remain
scientific-owner decisions and must not be selected inside code:

| ID | Decision | State |
|---|---|---|
| `WUL-D01` | retrospective confirmation horizon | `OPEN_HUMAN_DECISION` |
| `WUL-D02` | exact prior dormant-regime estimator/lookback | `OPEN_HUMAN_DECISION` |
| `WUL-D03` | exact relative-anomaly rule | `OPEN_HUMAN_DECISION` |
| `WUL-D04` | exact de-minimis economic floor | `OPEN_HUMAN_DECISION` |
| `WUL-D05` | minimum distinct timestamp clusters and/or source quorum | `OPEN_HUMAN_DECISION` |
| `WUL-D06` | minimum source coverage/timestamp resolution for adjudication | `OPEN_HUMAN_DECISION` |
| `WUL-D07` | episode close, dormant reset and rearm durations | `OPEN_HUMAN_DECISION` |
| `WUL-D08` | deterministic-vs-adjudicated primary oracle policy | `OPEN_HUMAN_DECISION` |

These decisions must be frozen before candidate generation or label
materialization. Sensitivity values must be preregistered and cannot replace the
primary oracle after temporal validation.

## 10. Current gate

```text
semantic class boundary        = PREPARED
feature/label separation       = PASS
failed-activation distinction  = PASS
numeric label oracle           = NOT_FROZEN
label authority                = DOES_NOT_YET_EXIST
label materialization          = NOT_AUTHORIZED
B02-D07                         = OPEN
```

