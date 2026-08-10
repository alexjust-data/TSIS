# TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_to_wake_up_completion_roadmap` |
| `document_version` | `v0_3` |
| `document_role` | `WORKSTREAM_COMPLETION_ROADMAP` |
| `document_status` | `CURRENT_PLANNING_SEQUENCE` |
| `current_stage` | `TA_3_STRATIFIED_DEVELOPMENT` |
| `current_next_gate` | `HUMAN_LAUNCH_BROAD_TA3_BINDING_A` |
| `consolidates` | `v0_1 detailed sequence + v0_2 TA-3 status` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `predictive_consumption` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |
| `owner` | `TBD` |

---

## 1. Purpose

Persistir la secuencia completa desde el estado actual hasta dos cierres
distintos:

```text
CLOSURE A
= Trading Activity Representation Profile completed

CLOSURE B
= Wake-up operational predictive promotion evaluated
```

Completar `Trading Activity` no completa Wake-up. Trading Activity es el primer
Information Object central del perfil candidato.

---

## 2. Current position

```text
TA-1 governed multisession pilot
= PASS_WITH_RESTRICTIONS

TA-2 full legacy source gate
= PASS_WITH_RESTRICTIONS

TA-3 stratified development design
= PREREGISTERED

TA-3 sample implementation
= FROZEN_FOR_TA3_SAMPLE_BUILD

TA-3 broad Binding A execution
= PENDING RUNNER GENERALIZATION, SMOKE AND HUMAN LAUNCH

TA-4 Binding B
= NOT_STARTED

TA-6 temporal OOS
= NOT_AUTHORIZED
```

Current authorities:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md

VARIABLES_FEATURES/
TRADING_ACTIVITY_TA3_SAMPLE_IMPLEMENTATION_DECISION_v0_1.md

VARIABLES_FEATURES/
TRADING_ACTIVITY_TA3_G_ONLY_SOURCE_AUTHORITY_DECISION_v0_1.md
```

The current research scope remains reconciled RTH event-time only. The future
Massive full-history backfill triggers mandatory all-session revalidation but
does not block present RTH engineering and development evidence.

---
## 3. Closure A: finish Trading Activity

### TA-1. Governed multisession pilot

Produce separate experimental outputs:

```text
CURRENT_STATE
PIT_BASELINE_AND_SURPRISE
```

Required controls:

- bounded symbol/session manifest;
- `symbol-second` output estimate;
- strictly prior PIT baseline sessions;
- B20, B60 and B120 availability accounting;
- deterministic partitions and rebuilds;
- pre-manifest, PID, heartbeat, live log and final manifest;
- no outcomes, scanner labels or Wake-up labels.

Exit state:

```text
FULL DETERMINISTIC SYMBOL-SECOND PILOT
= PASS_WITH_RESTRICTIONS or FAIL
```

### TA-2. Emit readout and close the legacy source gate

The pilot must produce a versioned execution readout that reconciles:

- requested and completed symbol-seconds;
- source coverage states;
- trade eligibility states;
- current-state outputs;
- PIT baseline availability;
- missingness and degradation;
- deterministic rebuild hashes;
- warnings and failures.

The readout must decide:

```text
FULL LEGACY SOURCE GATE
= PASS_WITH_RESTRICTIONS or FAIL
```

A pass is limited to the declared RTH research-only profile.

### TA-3. Expand to stratified development evidence

Only after TA-2 authorizes expansion, build a preregistered development sample
stratified at minimum by:

```text
price
market cap
historical activity
session date or market regime
coverage quality
zero-activity prevalence
```

The expansion must preserve the denominator of eligible `symbol-second`
exposure and must not select only known activations or chart winners.

Exit state:

```text
STRATIFIED DEVELOPMENT SOURCE GATE
= PASS_WITH_RESTRICTIONS or FAIL
```

### TA-4. Implement alternative bindings

Binding A is the minimal multiscale activity representation with basic
anti-artifact structure.

Implement Binding B as:

```text
Expanded Marks, Duration Distribution
and Concentration Geometry
```

Binding B must add information not already present in A, such as:

- broader trade-size and notional distributions;
- fuller intertrade-duration distribution;
- time since last eligible trade;
- event-time entropy or equivalent dispersion geometry;
- additional concentration geometry.

Binding C is conditional, not mandatory. It may be implemented only if a
written justification establishes that conditional duration, event-intensity
or self-excitation estimators can add testable, observable information beyond
A and B.

```text
Binding A = REQUIRED
Binding B = REQUIRED FOR MODEL COMPARISON
Binding C = JUSTIFICATION-GATED
```

### TA-5. Compare A, B and justified C

Candidate bindings must be compared with the same:

```text
source scope
decision grid
PIT rules
latency scenarios
development partitions
false-alarm budget
evaluation protocol
```

The comparison may use a fixed experimental detector shell or evaluation
probe. That probe is not the final Wake-up detector and cannot be promoted by
this step.

Required comparison dimensions:

- detection delay at a fixed false-alarm budget;
- episodes detected and omitted;
- alert burden per eligible exposure;
- stability by preregistered strata;
- missingness and representable coverage;
- non-redundant information contributed by each binding;
- computational and operational complexity;
- semantic coverage and boundary preservation.

Parsimony is the tie-breaker when performance is equivalent.

### TA-6. Execute temporal out-of-sample validation

After development choices are frozen:

```text
development period
-> validation period
-> untouched final test period
```

The OOS protocol must prevent:

- future baseline observations;
- repeated tuning against the final test period;
- ticker-specific memorization where recurring symbols matter;
- threshold changes after viewing OOS results;
- scanner 500k labels from becoming ground truth.

Exit state:

```text
TRADING ACTIVITY OOS VALIDITY
= PASS or FAIL
```

### TA-7. Select, reject or retain ambiguity

The admission decision must be one of:

```text
ADMIT_BINDING_A
ADMIT_BINDING_B
ADMIT_BINDING_C
ADMIT_COMPOSED_BINDING
RETAIN_MULTIPLE_NONINFERIOR_BINDINGS
REJECT_ALL_BINDINGS
```

The decision must cite hard-gate results, OOS evidence, false-alarm budget,
non-inferiority and complexity. A paper citation or a better in-sample score is
not sufficient.

### TA-8. Promote the admitted physical implementation

Only after TA-7 authorizes admission:

- freeze feature specifications and versions;
- freeze formulas, windows, cutoffs and availability rules;
- define schema and table mapping;
- define builder and validator ownership;
- preserve feature-to-source lineage;
- define quality and missingness outputs;
- create migration and downstream compatibility notes;
- keep research-only bindings separate from canonical outputs.

Exit state:

```text
TRADING_ACTIVITY_RTH_REPRESENTATION_PROFILE
= COMPLETE or REJECTED
```

This completes only the legacy RTH profile. It does not authorize Wake-up or
predictive consumption.

### TA-9. Revalidate after Massive full-history backfill

When the full Massive backfill is audited, execute:

```text
REQUIRES_REVALIDATION
REBUILD_NEW_DATASET_VERSION
FEATURE_VERSION_REVIEW
```

Revalidate:

- premarket, RTH and after-hours coverage;
- provider timestamps and sequence fields;
- trade identity and revision linkage;
- condition and exchange semantics;
- all-session PIT baselines;
- feature stability and version compatibility;
- differences between legacy and enriched outputs.

Never overwrite the legacy RTH dataset or its evidence in place.

Exit state:

```text
TRADING_ACTIVITY_FULL_SESSION_PROFILE
= COMPLETE, REVISED, REJECTED or STILL_PENDING
```

---

## 4. Closure B: finish Wake-up

Trading Activity completion opens, but does not complete, the remaining
Wake-up workstream.

### WU-1. Implement the remaining core Information Objects

Each object must pass the same chain of semantic model, physical binding,
source observability, causal validation and OOS evidence:

```text
Market Microstructure State
Price Movement
Liquidity
```

No object may silently absorb the meaning of another.

### WU-2. Implement supporting and conditional context

Supporting context:

```text
Volatility / Range State
Price Location / Structure
```

Conditional context:

```text
Fundamental Context
News / Catalyst Context
Halt Context
```

Deferred extension:

```text
Order Flow Pressure
```

Profile membership does not make a dimension a mandatory detector predicate.

### WU-3. Integrate the representation profile

Define a causal, versioned integration contract that states:

- which objects are required, supporting or conditional;
- how zero, unavailable, stale and degraded propagate;
- how timestamps and `input_max_available_at` compose;
- how object versions are bound to one detector experiment;
- which dimensions are optional under source limitations.

The integration output remains Market State representation, not Wake-up.

### WU-4. Specify and calibrate the Wake-up detector

Create a Detector Experiment Contract that freezes before calibration:

```text
scientific denominator
sampling unit
normal-period representation
class-imbalance treatment
false-alarm budget
deduplication and rearm rules
episode-open rule
candidate detector families
development and OOS periods
```

Then compare detector candidates under the same false-alarm budget using:

- detection delay;
- missed episodes;
- alerts per eligible exposure;
- robustness by stratum;
- one-print and data-defect rejection;
- scanner 500k timing as benchmark, not ground truth.

### WU-5. Implement Event and Episode lifecycle

If the detector passes, implement and validate:

```text
Wake-up Event candidate output
WATCH
CandidateMarketActivationEpisodeInstance
ResearchActiveSymbolSet
deduplication
rearm
episode expiry and closure
```

The episode must preserve wake-up, bursts, pullbacks, halts, reactivations and
later termination without rewriting the original event retrospectively.

### WU-6. Execute Wake-up OOS evaluation

Evaluate at minimum:

```text
false activations per eligible symbol-time
alert burden per session
detection delay
episodes detected and omitted
earliness versus scanner 500k
stability by price, market cap, session and coverage
data adequacy and unavailable states
```

Outcomes remain separate from detector inputs.

### WU-7. Evaluate operational predictive promotion

Operational promotion can only be considered after:

```text
versioned detector
validated available-at semantics
physical source binding
known coverage
accepted false-alarm budget
OOS evidence
reproducible builder and lineage
downstream compatibility review
```

Possible result:

```text
OPERATIONAL PREDICTIVE PROMOTION
= AUTHORIZED, REJECTED or DEFERRED
```

Even authorization would not demonstrate economic edge and would not authorize
orders, fills or execution policy.

---

## 5. End-to-end dependency sequence

```text
Binding A multisession pilot
-> legacy source-gate readout
-> stratified development evidence
-> Binding B and justified C
-> A/B/C comparison at fixed false-alarm budget
-> temporal OOS validation
-> Trading Activity admission decision
-> canonical physical binding and table lineage
-> remaining core Information Objects
-> supporting and conditional context
-> integrated Wake-up representation profile
-> Wake-up Detector Experiment Contract
-> detector calibration and OOS evaluation
-> Event and Episode lifecycle
-> operational predictive promotion decision
```

Massive backfill and revalidation run as a mandatory enriched-source branch.
They do not permit silent replacement of legacy evidence.

---

## 6. Definition of done

### Trading Activity RTH profile done

```text
source gate closed for declared scope
candidate bindings compared
temporal OOS complete
admission decision recorded
winning implementation versioned
table mapping and lineage defined
validators passing
canonical promotion explicitly decided
```

### Wake-up done

```text
all admitted Information Objects implemented
integrated representation profile versioned
detector contract frozen
false-alarm budget met
OOS evaluation passed
Episode lifecycle implemented
available-at and source binding validated
operational promotion explicitly decided
```

Neither definition of done includes strategy edge, entry policy, risk, OMS,
execution, fill or PnL.

---

## 7. Immediate next sequence

```text
1. Frozen TA-3 sample and G-only preflight: PASS.
2. Binding A block orchestrator and bounded smoke: PASS.
3. Human-launch four deterministic broad-run shards.
4. Reconcile all shard manifests and output hashes.
5. Emit the stratified development source-gate readout.
```

No later roadmap stage is authorized merely because it appears in this
document. Every transition requires the preceding gate and a versioned
readout.