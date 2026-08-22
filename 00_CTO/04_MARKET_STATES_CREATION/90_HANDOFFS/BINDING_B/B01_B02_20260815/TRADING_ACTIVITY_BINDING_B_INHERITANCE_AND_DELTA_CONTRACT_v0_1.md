# Trading Activity Binding B inheritance and delta contract v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_b_inheritance_and_delta_contract` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_BINDING_INHERITANCE_AND_DELTA_CONTRACT` |
| `document_status` | `FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT` |
| `information_object_id` | `trading_activity` |
| `binding_id_proposed` | `trading_activity_binding_b_event_time_renewal_burst_v0_1` |
| `comparison_incumbent` | `trading_activity_binding_a_candidate_v0_2` |
| `binding_b_preregistration_sha256` | `9fff47896562575883d6a428b839046a49d2179c9d95220f7f0b9fa0dec8d923` |
| `binding_a_exact_specification_sha256` | `e6f59fae69dadc032d5d7f35add287110917e89926f6a0bead5ddaf644d29b19` |
| `sample_manifest_sha256` | `100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf` |
| `target_table_sha256` | `55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220` |
| `external_audit_verdict` | `PASS_FOR_EXACT_SPECIFICATION_DRAFTING` |
| `audited_preparation_zip_sha256` | `6419be68576a579c4ce6ac3ec38dab58a83d01318d8c202f29da0f61fa14e6fd` |
| `freeze_authorization` | `AUTHORIZED_BY_ALEXJ_2026-08-15` |
| `freeze_readout` | `TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md` |
| `exact_specification_drafting_authorized` | `true` |
| `implementation_authorized` | `false` |
| `probe_execution_authorized` | `false` |
| `long_materialization_authorized` | `false` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-15` |

## 1. Purpose

Binding B must differ from A only in the physical representation of Trading
Activity. This contract prevents an apparent B advantage from being caused by
a different source, population, eligibility rule, latency assumption,
missingness policy, denominator or OOS treatment.

```text
same scientific object and experiment
+ different representation
= valid challenger
```

This artifact does not freeze the exact B formulas. It freezes the inheritance
boundary that the later exact specification must obey. Its freeze was granted
after external review of the preparation package and is evidenced by
`TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md`.

## 2. Governing authorities

Binding B inherits the non-conflicting clauses of:

1. `TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`
2. `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`
3. `TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`
4. `TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md`
5. `TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md`
6. `TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md`
7. `TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md`
8. `TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`
9. `EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_2.md`
10. `REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md`
11. `REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md`
12. `TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md`
13. `TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md`

Any exact-specification clause that conflicts with the inherited boundary must
identify the conflict, justify a new version and explain the A/B comparability
impact. Silence does not supersede inheritance.

## 3. Stable scientific identity inherited unchanged

```text
Information Object
= Trading Activity

minimum meaning
= observable traded participation
  + intensity
  + explicit temporal scale
  + realized trading
  + point-in-time legality
```

Binding B must preserve information about:

- absolute activity;
- event intensity;
- activity marks;
- temporal concentration;
- PIT-relative surprise;
- persistence, decay and reactivation.

Binding B must not include:

```text
price direction or returns
spread or depth
aggressor side
signed flow or OFI
scanner selection
news or halt labels
future continuation or outcomes
MFE / MAE
entry, stop, target or sizing
```

## 4. Source scope inherited unchanged

```text
scope_id
= legacy_rth_reconciled_event_time_research_only

source_id
= trades_ticks_prod_2005_2026_legacy_rth_reduced

governed physical source root
= G:/TSIS/data/trades_ticks_prod_2005_2026

valid interpretation
= first observable transition during RTH
```

Binding B may not claim:

```text
complete premarket-to-after-hours Wake-up episode
measured historical available_at
revision-aware historical detection
authoritative exchange sequence inside timestamp ties
```

Missing source sessions stay in the governed denominator as explicit
`UNAVAILABLE`; they are not silently dropped.

## 5. Decision grid and session scope inherited unchanged

```text
decision_unit
= SYMBOL_SECOND

calendar
= XNYS from market_calendar_v0_1

decision timestamps
= integer UTC seconds satisfying
  session_open_utc < decision_timestamp < session_close_utc
```

Binding B computes internal state in event time and projects it onto this same
grid. It does not obtain more decision opportunities than A.

Every stateful B component resets at the governed RTH session boundary unless
the exact specification explicitly defines a strictly prior-session baseline
input. No intraday event-state mass, duration sequence, burst run or kernel
recursion crosses the session boundary.

## 6. Availability and latency inherited unchanged

```text
availability_mode
= SIMULATED_NOT_OBSERVED
```

At decision time `t`, Binding B may consume only trades whose simulated
availability is not later than `t`, under the same registered latency policy as
A. An event with source time before `t` but simulated availability after `t`
remains future information and is excluded.

Sensitivity policies `100ms` and `5000ms` remain secondary preregistered
analyses. They cannot replace the primary latency policy after results are
observed.

## 7. Trade eligibility and duplicates inherited unchanged

`TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md` governs both candidates.

```text
same eligible raw trade rows
same condition-code policy
same unknown-condition degradation
same exact-duplicate preservation and flagging
same duplicate sensitivity population
```

Binding B may aggregate eligible rows into timestamp clusters, but aggregation
does not change which rows were eligible or erase duplicate/condition evidence.
Raw eligible-row counts and duplicate flags must remain reconstructible through
mandatory companions or lineage.

## 8. Quality evidence inherited unchanged

Foundation quality labels remain evidence metadata:

```text
quality label
!= automatic exclusion
```

`good`, `review`, `review_microstructure`, `bad_data`, missing evidence or local
dispositions may define audit strata. They may not silently change B's output
denominator or make its population differ from A.

## 9. Observation and calculation states inherited unchanged

The following state vocabulary remains mandatory where applicable:

```text
OBSERVED_NONZERO
OBSERVED_ZERO
INSUFFICIENT_SAMPLE
DEGRADED
UNAVAILABLE
OUT_OF_SCOPE
```

Rules:

- observed zero is not missing;
- insufficient history is not zero;
- unavailable source is not inactivity;
- degraded eligibility/coverage remains explicit;
- a feature that cannot be calculated is typed `NULL` with a reason state;
- no hidden floor may turn an unavailable or zero-dominated baseline into a
  finite normal observation.

Binding B may add more specific reason codes, but cannot weaken these states or
collapse them into a single nullable value.

The following Binding B reason codes are mandatory and may not be renamed or
collapsed by the exact specification:

```text
TIMESTAMP_RESOLUTION_INSUFFICIENT
INSUFFICIENT_DISTINCT_CLUSTERS
EVENT_ORDER_UNRESOLVED
INSUFFICIENT_CLUSTER_HISTORY
ZERO_DOMINATED
BASELINE_INSUFFICIENT_HISTORY
RIGHT_CENSORED_ECONOMIC_CLOCK
```

## 10. PIT baseline population inherited unchanged

The baseline candidates remain:

```text
B20
B60 primary
B120
```

Reference sessions must be:

- strictly prior to the target session;
- from the same governed instrument context;
- aligned to the same XNYS RTH minute/context and frozen policy dimensions;
- bounded by the requested lookback candidate;
- free of target-day or future-session inputs.

Binding B changes the statistics estimated from that population, not the
population itself. Its `lambda0`, duration distributions, kernel baselines and
economic-unit baseline must all be derived from the same prior-only session
membership that the exact specification freezes.

## 11. Frozen development population inherited unchanged

Binding B reuses without reselection:

```text
sample_manifest_v0_2.json
SHA-256
= 100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf

selected_target_contexts_v0_1.parquet
SHA-256
= 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220

blocks
= 240

TARGET sessions
= 2,400 exact identities
```

Binding B may read the same governed scope sessions required for prior history,
but only the exact TARGET identities belong to the A/B comparison denominator.

## 12. Representation delta: timestamp clusters

Binding A processes eligible trades inside fixed clock windows. Binding B first
creates timestamp clusters.

For every governed instrument-session, all eligible and causally available
trades sharing the exact normalized `legacy_event_time` form one cluster:

```text
cluster timestamp = tau_j
cluster trade count = n_j
cluster share volume = q_j
cluster dollar volume = v_j
intercluster duration = tau_j - tau_(j-1)
```

The contract forbids claiming a causal ordering between rows inside one
cluster. `physical_row_ordinal` may support deterministic reconstruction and
lineage only; it is not economic sequence.

The exact specification must freeze:

- normalized timestamp dtype and precision;
- whether condition/duplicate reason metadata is list-valued or summarized;
- cluster availability metadata;
- integer overflow policy for counts and shares;
- numeric precision for dollar aggregation.

The following companions are mandatory:

```text
same_timestamp_cluster_trade_count
timestamp_resolution_us
distinct_cluster_count_available
```

Artificial jitter, timestamp interpolation and causal use of
`physical_row_ordinal` are prohibited. The ordinal may support deterministic
lineage or summation order only.

## 13. Representation delta: renewal and operational time

Binding B may use the time required to observe the last `K` clusters and the
current intercluster duration. It may rescale durations using strictly prior PIT
expected activity.

The exact specification must freeze:

- `K = 5, 20, 50` semantics at session boundaries;
- fewer-than-K behavior;
- `lambda0` estimator, units and minimum support;
- integration/approximation across minute-context boundaries;
- fast-duration threshold;
- run-length reset rules;
- zero-dominated and insufficient-baseline behavior;
- `silence_break_surprise_B60` formula.

No implicit intensity floor is inherited or authorized.

## 14. Representation delta: continuous kernels

Binding B may maintain causal exponential kernels over cluster marks and project
their state onto each decision second.

Primary proposed decays remain:

```text
tau = 2s, 10s, 60s
```

`300s` remains secondary context. The exact specification must freeze:

- continuous-time recursion;
- event-at-decision ordering;
- kernel units and normalization by `tau`;
- initialization at session open;
- no-event decay;
- mark definitions for trades, shares and dollars;
- robust PIT-surprise estimator;
- `epsilon` and log-ratio policy;
- raw companion columns.

The production recursion must later pass exact or explicitly tolerance-bound
comparison against an independent direct-sum oracle.

## 15. Representation delta: economic time

Binding B may measure the elapsed time required to accumulate a strictly prior
PIT-normal dollar unit `U_B60`.

The exact specification must freeze:

- estimator for `U_B60`;
- positive-session and zero-session handling;
- unit availability time;
- partial accumulation at session open;
- no-attainment state by decision time;
- minimum positive floor, if any;
- upper/lower censoring and units of the compression result.

`U_B60` may not use current-session realized dollars after the decision point.

## 16. Representation delta: marks and burst dynamics

Binding B may represent:

- HHI and top-three dollar concentration over recent clusters;
- dollar size per trade;
- robust mark shift against the PIT baseline;
- current intensity relative to the recent event-time peak;
- burst age, slope, decay and reactivation.

The exact specification must freeze rolling support, fewer-than-K behavior,
zero denominators, peak initialization, burst entry/exit thresholds, silence
separation and which variables are primary, secondary or diagnostic-only.

## 17. A/B comparison boundary inherited unchanged

Binding A and B must use:

```text
same exact symbol-seconds
same target and denominator manifests
same source rows and policies
same labels/outcomes outside both bindings
same detector families and search budget
same false-activation budget
same temporal splits and strata
same no-peeking rule
```

Development plus temporal-validation OOS may compare candidates. The final
temporal OOS lockbox is opened only for the already selected candidate.

Before results exist, the exact specification must bind these mandatory
ablations:

```text
B-renewal-only
B-kernel-only
B-full
```

The primary comparison remains Binding A versus B-full. Ablations explain the
source of any advantage and cannot become post-hoc candidate variants.

The comparison contract must also freeze development-only preprocessing,
typed missingness treatment, regularization, search budget, effective-capacity
limits and paired uncertainty clustered by ticker-session or another governed
session/episode block. It may not treat millions of symbol-seconds as
independent observations.

False-activation thresholds must be calibrated only in development and applied
unchanged in temporal validation. The primary estimand, non-inferiority
constraints, uncertainty method and selection margins must be fixed before A/B
comparison begins.

## 18. Incident controls inherited unchanged

Binding B must bind and demonstrate:

```text
RM-MAT-CTRL-001
RM-MAT-CTRL-002
RM-MAT-CTRL-003
RM-MAT-CTRL-004
RM-MAT-CTRL-005
RM-MAT-CTRL-006
```

The later executable plan must contain `inherited_incident_controls` with
implementation, unit/adversarial test, all-shard probe and terminal-rehearsal
evidence for every applicable control. A citation without executable proof is
not PASS.

The B-specific controls `TA-B-CTRL-001..008` are defined in the development and
certification plan and must be imported by the exact specification.

## 19. Output and lineage boundary

The exact physical family topology remains to be frozen. It must not be copied
blindly from A's three families because B's natural groups differ.

Every family must still share:

- exact `symbol-second` target identity;
- stable typed schema;
- explicit calculation/observation state;
- binding, feature, policy and source IDs;
- specification/config/code hashes;
- maximum input availability time;
- `future_window_used = false` or its exact B equivalent;
- atomic partition and content hash;
- one authoritative cardinality contract.

Representation output authority:

```text
D:/TSIS/IO
```

`G:/TSIS/data` remains upstream source authority and is not a new B output root.

## 20. Decisions intentionally left to exact specification

This frozen inheritance/delta contract delegates the following choices to B-02
and does not freeze them:

```text
lambda0 estimator
fast-duration threshold
kernel epsilon
robust-z estimator and fallback
U_B60 estimator
burst entry/exit thresholds
primary schema dtypes and column order
physical family topology and partition counts
comparison margins and compute budget
```

These are not implementation freedoms. They must be decided in
`TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md` before code is
authorized.

## 21. External-audit freeze record

```text
pre-freeze draft SHA-256
= 5b4da079008c9689ff2061399773c298fcfb178f358fbfea4439645763e815c5

audited preparation ZIP SHA-256
= 6419be68576a579c4ce6ac3ec38dab58a83d01318d8c202f29da0f61fa14e6fd

external preparation verdict
= PASS_FOR_EXACT_SPECIFICATION_DRAFTING

human freeze authorization
= AUTHORIZED_BY_ALEXJ_2026-08-15
```

The audited ZIP remains immutable pre-freeze provenance. This contract imports
the auditor's five required closures: timestamp resolution, zero/censoring,
mandatory ablations, comparable statistical capacity and exact development-
only calibration/selection discipline.

## 22. Current authorization

```text
inheritance/delta contract       = FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT
human/scientific review          = PASS_FOR_B01_FREEZE
exact specification drafting     = AUTHORIZED
exact specification freeze       = NOT_AUTHORIZED
implementation                   = NOT_AUTHORIZED
probe execution                  = NOT_AUTHORIZED
long materialization             = NOT_AUTHORIZED
A/B comparison                   = NOT_AUTHORIZED
temporal OOS                     = NOT_AUTHORIZED
canonical promotion              = NOT_AUTHORIZED
```
