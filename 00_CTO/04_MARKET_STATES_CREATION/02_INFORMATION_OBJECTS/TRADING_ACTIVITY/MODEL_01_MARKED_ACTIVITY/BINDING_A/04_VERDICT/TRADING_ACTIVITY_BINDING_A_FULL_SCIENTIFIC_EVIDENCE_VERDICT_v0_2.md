# Trading Activity Binding A full scientific evidence verdict v0.2

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `REVISED_SCIENTIFIC_EVIDENCE_VERDICT` |
| `document_status` | `EXECUTED_PASS_WITH_SCOPE_RESTRICTIONS` |
| `representation_candidate` | `ABSOLUTE_AND_PIT_RELATIVE_MULTISCALE_MARKED_ACTIVITY_PROCESS` |
| `binding_id` | `trading_activity_binding_a_candidate_v0_2` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `verdict` | `PASS_WITH_SCOPE_RESTRICTIONS` |
| `percentile_replay_restriction` | `CLOSED_PASS_EXACT` |
| `candidate_comparison` | `BINDING_A_READY_BINDING_B_NOT_YET_BUILT` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `supersedes` | `TRADING_ACTIVITY_BINDING_A_FULL_SCIENTIFIC_EVIDENCE_VERDICT_v0_1.md` |
| `created_at` | `2026-08-15` |

## 1. Revised decision

Binding A passes the complete governed scientific-evidence gate for candidate
comparison inside its declared legacy-RTH research scope.

```text
technical terminal certification       = PASS
bounded value-level evidence audit      = PASS
independent percentile replay FULL      = PASS_EXACT
current_state family                    = PASS
multiscale_contrast family              = PASS
pit_baseline_and_surprise family        = PASS
hard failures                           = 0
percentile mismatches                   = 0
Binding B preregistration               = NEXT_AUTHORIZABLE_GATE
Binding B long materialization          = NOT_AUTHORIZED
temporal OOS                            = NOT_AUTHORIZED
canonical promotion                     = NOT_AUTHORIZED
```

This is not a selection of Binding A and does not make it canonical. It means
Binding A is now an admissible incumbent candidate against a separately
preregistered and independently materialized Binding B.

## 2. Evidence chain

The v0.1 verdict established:

- terminal integrity over exactly 2,400 TARGET sessions and 7,200 partitions;
- value-level audit of all three physical families;
- causal dates, states, ratios, duration compression, schemas and metadata;
- zero hard failures, with one explicit percentile-replay evidence restriction.

The terminal independent replay then established:

```text
240/240 blocks
2,400/2,400 sessions
837,990,000 baseline rows
3,351,960,000 percentile cells
four percentile variables
exact values and exact NULL masks
zero mismatches
```

Authority:

```text
TRADING_ACTIVITY_BINDING_A_INDEPENDENT_PERCENTILE_REPLAY_FULL_EXECUTION_READOUT_v0_1.md
final manifest SHA-256
= 634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857
```

## 3. Restrictions that remain

The percentile restriction is closed. The following scope restrictions remain
and must be preserved in A/B comparison and downstream interpretation:

- source coverage is legacy regular trading hours only;
- historical availability is simulated, not measured;
- Binding A represents the first observable RTH transition, not the entire
  premarket-to-after-hours Wake-up episode;
- quality labels remain evidence metadata and not universal exclusion rules;
- the 240-block / 2,400-session denominator is frozen development evidence, not
  a claim of full 4,824-instrument, twenty-year canonical history;
- no temporal OOS has been opened;
- no predictive, operational or canonical promotion has occurred.

## 4. Binding B comparison contract

Binding B must preserve the same stable Trading Activity meaning while using a
genuinely alternative physical binding. Its preregistration must freeze before
implementation:

```text
scientific dimensions and exclusions
formulas and estimator identities
schema and metadata
source and availability assumptions
same governed A/B population and periods
fixed comparison metrics
fixed false-alarm budget
untouched temporal OOS boundary
inherited_incident_controls = RM-MAT-CTRL-001..006 as applicable
```

After implementation, every variable must pass one production-equivalent probe
in every planned shard, including readable values and missingness states. Only
then may a human separately authorize Binding B long materialization.

## 5. Next gate

```text
Binding B frozen preregistration
-> implementation and unit tests
-> all-variable / all-shard production-equivalent probes
-> governed human gate
-> separately authorized Binding B materialization
-> A/B comparison on identical population and periods
-> selection at fixed false-alarm budget
-> untouched temporal OOS
-> Trading Activity admission decision
```
