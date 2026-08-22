# Trading Activity Binding B development and certification plan v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_b_development_and_certification_plan` |
| `document_version` | `v0_1` |
| `document_role` | `GOVERNED_BINDING_DEVELOPMENT_AND_CERTIFICATION_SEQUENCE` |
| `document_status` | `PREREGISTERED_SEQUENCE_NOT_EXECUTABLE` |
| `information_object_id` | `trading_activity` |
| `binding_id_proposed` | `trading_activity_binding_b_event_time_renewal_burst_v0_1` |
| `representation_proposed` | `PIT_NORMALIZED_EVENT_TIME_MARKED_RENEWAL_AND_BURST_STATE` |
| `comparison_incumbent` | `trading_activity_binding_a_candidate_v0_2` |
| `binding_a_terminal_evidence` | `PASS_WITH_SCOPE_RESTRICTIONS` |
| `binding_b_preregistration` | `DRAFT_NOT_FROZEN` |
| `b01_inheritance_delta` | `FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT` |
| `b02_exact_specification` | `DRAFT_PREPARED_NOT_FROZEN` |
| `implementation_authorized` | `false` |
| `probe_execution_authorized` | `false` |
| `long_materialization_authorized` | `false` |
| `a_b_comparison_authorized` | `false` |
| `temporal_oos_authorized` | `false` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-15` |

## 1. Purpose

This plan reconstructs the actual path followed by Binding A and converts it
into the shortest governed path for Binding B. It does not clone incidental
failures, historical recovery branches or implementation-specific optimizations.

The rule is:

```text
replicate every scientific and operational gate
!=
copy every historical artifact or defect
```

Binding B remains a challenger representation of the same Information Object.
It must not change the population, outcomes, false-alarm budget or OOS rules in
order to obtain a favorable comparison.

## 2. Authorities and frozen evidence

### 2.1 Binding B proposal

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md

SHA-256
= 9fff47896562575883d6a428b839046a49d2179c9d95220f7f0b9fa0dec8d923

status
= DRAFT_FOR_HUMAN_AND_SCIENTIFIC_REVIEW_NOT_FROZEN
```

### 2.2 Binding A incumbent evidence

```text
Binding A exact specification SHA-256
= e6f59fae69dadc032d5d7f35add287110917e89926f6a0bead5ddaf644d29b19

Binding A independent replay final manifest SHA-256
= 634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857

terminal targets / partitions
= 2,400 / 7,200

independent percentile cells / mismatches
= 3,351,960,000 / 0

scientific verdict
= PASS_WITH_SCOPE_RESTRICTIONS
```

### 2.3 Shared development denominator

Binding B must reuse, without reselection:

```text
sample manifest
= G:/TSIS/data/data_foundation_outputs/
  trading_activity_ta3_stratified_sample/
  trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z/
  sample_manifest_v0_2.json

sample manifest SHA-256
= 100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf

selected target table
= G:/TSIS/data/data_foundation_outputs/
  trading_activity_ta3_stratified_sample/
  trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z/
  selected_target_contexts_v0_1.parquet

selected target table SHA-256
= 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220

blocks / TARGET sessions
= 240 / 2,400
```

No Binding B result may change this denominator, choose replacement sessions
or use feature values to alter membership.

## 3. What Binding A actually did

The valid Binding A chain was:

```text
scientific meaning and source boundaries
-> exact physical specification
-> pure semantic kernel and unit tests
-> single-partition physical smoke
-> governed multisession plan
-> runner, monitor, resume and terminal manifests
-> normal-session and early-close integration smoke
-> deterministic multisession pilot
-> independent post-run validation
-> frozen stratified development sample
-> TA-3 preflight and bounded orchestrator smoke
-> specification/implementation conformance audit
-> all-shard production-equivalent probes
-> early output audit
-> performance profiling and exact engine equivalence
-> separately authorized 240-block materialization
-> exact TARGET terminal certification
-> family-by-family scientific audit
-> independent percentile replay
-> candidate-comparison admission
```

Binding A also exposed defects. Those are not optional history; their controls
must be imported before B code exists:

```text
RM-MAT-CTRL-001 typed metadata vs. physical family counts
RM-MAT-CTRL-002 exact target membership, never min/max inference
RM-MAT-CTRL-003 one authoritative cardinality contract
RM-MAT-CTRL-004 composite identity; never trust an ordinal implicitly
RM-MAT-CTRL-005 explicit Parquet paths; no accidental Hive inference
RM-MAT-CTRL-006 validators bound to exact specification/config SHA
```

## 4. Repeat, reuse or prohibit

| Binding A element | Binding B treatment | Reason |
|---|---|---|
| Information Object meaning | `REUSE_EXACTLY` | A and B must represent Trading Activity, not different objects. |
| Legacy-RTH source scope | `REUSE_EXACTLY` | Comparison must preserve the same observational limitation. |
| Trade eligibility policy v0.2 | `REUSE_EXACTLY` | No candidate-specific trade filtering. |
| Temporal/missingness contract | `REUSE_PLUS_B_DELTA` | Same states and causal availability; B adds cluster/kernel state rules. |
| Latency policy | `REUSE_EXACTLY` | Same simulated availability. |
| PIT baseline sessions B20/B60/B120 | `REUSE_EXACTLY` | Same prior-only population and contexts. |
| TA-3 sample and TARGET denominator | `REUSE_EXACTLY` | Prevent candidate-dependent sampling. |
| Pure Python semantic oracle | `REPEAT_FOR_B` | B has different mathematics. |
| Unit and adversarial fixtures | `REPEAT_AND_EXTEND` | Event-time clusters require new boundary cases. |
| Physical smoke | `REPEAT_FOR_B` | New schema and state topology. |
| Long-run wrapper/telemetry primitives | `REUSE_INFRASTRUCTURE_ONLY` | Preserve mature atomic writes, resume and heartbeat behavior. |
| All-variable/all-shard probes | `REPEAT_FOR_B` | Mandatory gate for every Representation Model. |
| Early output value audit | `REPEAT_FOR_B` | Prevent expensive invalid expansion. |
| C++ optimization | `ONLY_IF_PROFILE_JUSTIFIES` | It was an A bottleneck response, not a scientific gate. |
| Target-only recovery | `DO_NOT_PLAN` | It was required by an A terminal-contract defect. B must test the terminal path first. |
| Scientific family audit | `REPEAT_FOR_B` | Completion is not evidence of correct values. |
| Independent nonlinear-feature replay | `REPEAT_FOR_B` | Baselines, duration rescaling and kernels need an independent oracle. |
| A/B comparison | `NEW_SHARED_GATE` | Same detector heads and false-alarm budget. |

## 5. Binding B mandatory sequence

### B-00 — Preregistration proposal

```text
artifact
= TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md

current state
= COMPLETE_AS_DRAFT_NOT_FROZEN
```

This stage records the scientific challenger. It does not authorize code.

### B-01 — Inheritance and delta closure

Freeze what B inherits unchanged and what must be specified differently:

- Information Object and exclusion boundary;
- source and RTH scope;
- decision grid;
- eligibility, duplicates and latency;
- observation/calculation states;
- baseline population and context grouping;
- timestamp cluster semantics;
- event-time and economic-time state;
- kernel reset and boundary behavior.

Required artifact:

```text
TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md

current state
= FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT

freeze evidence
= TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md
```

### B-02 — Exact specification drafting and freeze

Required artifact:

```text
TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md
```

It must freeze before implementation:

- all primary/secondary/diagnostic variables;
- exact formulas and units;
- `K`, `tau`, `epsilon`, floors and thresholds;
- baseline-zero and insufficient-history behavior;
- session reset, ties, gaps and boundary censoring;
- feature names, dtypes, order and nullable fields;
- physical grain and family topology;
- lineage/version metadata;
- common A/B comparison contract;
- independent-audit formulas.

Current state:

```text
draft = AMENDED_NOT_FROZEN
resolved decisions = B02-D01..D06, B02-D08..D11
blocking decisions = B02-D07, B02-D12 OPEN
freeze = PENDING_SEPARATE_EXPLICIT_HUMAN_GATE
```

Gate:

```text
BINDING_B_EXACT_SPECIFICATION
= FROZEN_BY_EXPLICIT_HUMAN_GATE
```

### B-03 — Pure semantic oracle

Create in Data Foundation:

```text
scripts/trading_activity_binding_b_kernel.py
tests/test_trading_activity_binding_b_kernel.py
```

The initial oracle must favor clarity and exactness over throughput. It becomes
the semantic reference for every optimized implementation.

Minimum tests include:

```text
same-timestamp cluster aggregation
no claimed within-cluster causal order
last-K cluster insufficiency
event exactly at decision timestamp
event after simulated availability cutoff
normal-session reset
early-close reset
no cross-session kernel carry
zero-dominated baseline
silence break
kernel closed-form decay between events
kernel update at event time
economic-unit accumulation
mark HHI and top-three concentration
burst start, decay and reactivation
NULL vs zero vs unavailable
deterministic rebuild
no outcome dependency
```

### B-04 — Typed schema and single-session physical smoke

Create stable schemas before any multisession runner. Every configured column
must exist with identical name, dtype, order and NULL semantics even when all
values in a shard are NULL.

Required evidence:

```text
TRADING_ACTIVITY_BINDING_B_IMPLEMENTATION_READOUT_v0_1.md
```

Gate:

```text
unit/adversarial tests = PASS
single-session normal smoke = PASS
single-session early-close smoke = PASS
schema variants = 1 per frozen family
```

### B-05 — Governed multisession plan and runtime

Prepare, but do not launch broadly:

```text
scripts/run_trading_activity_binding_b_multisession_pilot.py
scripts/monitor_trading_activity_binding_b_multisession_pilot.ps1
configs/trading_activity_binding_b_multisession_pilot_v0_1.json
tests/test_trading_activity_binding_b_multisession_engine.py
tests/test_trading_activity_binding_b_multisession_runner.py
```

The wrapper must implement the long-running-operation contract from its first
test: pre-manifest, PID, heartbeat, live log, atomic partitions, hashes,
checkpoint/resume, clean stop, final manifest and single-writer protection.

The same wrapper, aggregator and terminal certifier used by the long run must be
exercised in the probe. A kernel-only probe is insufficient.

### B-06 — Bounded multisession pilot

Run a bounded pilot containing at least:

- one normal session;
- one early close;
- an active ticker;
- a zero-dominated context;
- same-timestamp clusters;
- insufficient K-history;
- unavailable/degraded cases;
- controlled stop and `--resume`.

Required evidence:

```text
TRADING_ACTIVITY_BINDING_B_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md
```

The independent validator must recompute values from source events, not merely
re-read output metadata.

### B-07 — Frozen A/B denominator binding

Binding B does not build a new stratified sample. It binds to the exact A
manifest and target-table hashes from section 2.3.

Required preflight assertions:

```text
blocks = 240
targets = 2,400 exact identities
target table SHA = expected
sample manifest SHA = expected
development dates only
validation/final OOS absent
source root = governed G root only
```

### B-08 — All-variable, all-shard production-equivalent probes

Before any broad materialization, run one bounded production-equivalent probe
in each of the four frozen logical shards using identical code, config, schema,
sources, wrapper, aggregator and certifier.

Each of the 22 primary variables, every mandatory raw/audit companion and every
state/metadata column must pass:

```text
formula and semantics
name, dtype and order
grain, cardinality and uniqueness
PIT causality
zero/NULL/stale/degraded/unavailable/insufficient sample
version and lineage IDs
cross-shard equivalence
readable value sample
terminal manifest rehearsal
```

Required artifacts:

```text
TRADING_ACTIVITY_BINDING_B_FOUR_SHARD_PROBE_PLAN_v0_1.json
TRADING_ACTIVITY_BINDING_B_FOUR_SHARD_PROBE_CERTIFICATION_READOUT_v0_1.md
```

Gate:

```text
SHARD_EXPANSION_AUTHORIZED
= all variables PASS in all 4 shards
  and terminal certifier rehearsal PASS
  and human gate PASS
```

Any formula, schema, policy, source or lineage change invalidates all four
probes. Resume must never mix versions.

### B-09 — Early output audit

Before allowing a broad run to continue beyond its initial bounded exposure,
audit real Parquet values and masks from every family. This gate specifically
tests that production serialization did not change semantics.

```text
failure
-> clean stop
-> incident register
-> new version
-> repeat all four shard probes

PASS
-> broad continuation may remain authorized
```

### B-10 — Performance gate and optional optimization

Measure first. Record CPU, RAM, I/O, rows/s, projected wall time and projected
storage on the actual host.

```text
if Python meets the frozen budget
-> keep Python

if Python misses the budget
-> optimize after profiling
-> preserve Python as semantic oracle
-> require exact representative and 4/4-shard equivalence
```

C++ is not mandatory. Any native engine must have a composite fingerprint over
registry, adapter, source and binary and may change execution only.

### B-11 — Prepared full plan, still non-executable

Create a hash-bound plan with:

- exact target identities, not date ranges;
- authoritative per-family cardinalities;
- output schema hashes;
- implementation/config/specification hashes;
- inherited controls `RM-MAT-CTRL-001..006` with executable evidence;
- disk and memory preflight;
- run root, output root and single-writer guard;
- terminal certifier expected artifacts;
- clean stop and resume rules.

```text
artifact_status = PREREGISTERED_NOT_AUTHORIZED
human_authorization = NOT_AUTHORIZED
```

### B-12 — Separate human authorization and long materialization

Only after B-08 through B-11 pass may a separately frozen config receive human
authorization. The operator receives one launch command and one monitor command.

The planned physical output root is under the governed authority:

```text
D:/TSIS/IO/
  wake_up/
  trading_activity/
  event_time_renewal_burst/
  binding_b_v01/
  run_id=<immutable_run_id>/
```

The exact representation path remains a B-02 freeze decision. No new
representation output is written to `G:/TSIS/data`.

### B-13 — Terminal certification

The long run is incomplete until the terminal final manifest passes. The
certifier must use the same cardinality authority already exercised in every
shard probe.

Minimum terminal gates:

```text
exact 2,400 TARGET identities
exact expected family partitions
zero failed/duplicate target-family identities
one schema per family
hash-bound outputs
no future input
all inherited controls PASS
wrapper dead after final
status = PASS
```

`completed blocks = 240/240` without terminal PASS is not completion.

### B-14 — Family-by-family scientific audit

Create an independent auditor bound to the exact B specification and config
hashes. It must inspect readable values and independently recompute every
primary variable family, state branch and metadata contract.

Required evidence:

```text
TRADING_ACTIVITY_BINDING_B_FULL_SCIENTIFIC_EVIDENCE_VERDICT_v0_1.md
```

### B-15 — Independent replay of nonlinear features

Prepare an oracle that does not import production B engines. At minimum replay:

- operational-time rescaling;
- PIT robust surprises;
- silence-break behavior;
- exponential kernel state;
- economic-time compression;
- HHI/top-three mark concentration;
- burst persistence/decay fields selected as primary.

Sequence:

```text
tests
-> one block per shard probe
-> exact/tolerance-bound comparison
-> measured FULL plan
-> explicit human authorization
-> FULL independent replay
-> terminal readout
```

### B-16 — Candidate-comparison admission

B is admitted to comparison only if technical certification and scientific
evidence pass within the declared scope. Admission does not mean B wins.

### B-17 — A/B comparison

Use exactly:

- the same symbol-seconds and target manifest;
- the same labels/outcomes stored outside both bindings;
- common low-capacity detector heads;
- the same hyperparameter-search budget;
- the same false activations per million eligible symbol-seconds;
- frozen metrics, strata and noninferiority margins.

Development plus temporal-validation OOS may compare candidates. The final
temporal OOS lockbox remains closed.

### B-18 — Selection and final temporal OOS

Select one candidate before opening the final lockbox. Only the selected
candidate receives final temporal OOS evaluation.

```text
A and B equivalent
-> A wins by parsimony

B satisfies every hard gate and frozen superiority rule
-> B selected

A+B combination
-> new Binding C preregistration required
```

## 6. B-specific prevention controls

In addition to `RM-MAT-CTRL-001..006`, B must prove:

| Control | Requirement |
|---|---|
| `TA-B-CTRL-001` | Same-timestamp rows form one cluster; no physical-row causal order is claimed. |
| `TA-B-CTRL-002` | Kernel, renewal and burst state reset exactly at the frozen session boundary. |
| `TA-B-CTRL-003` | No event, kernel mass or duration crosses sessions unless explicitly specified and tested. |
| `TA-B-CTRL-004` | Fewer-than-K histories remain typed insufficient, never zero-filled. |
| `TA-B-CTRL-005` | Zero-dominated baseline never produces hidden infinite/floored surprise. |
| `TA-B-CTRL-006` | A and B share exact source, target and policy hashes. |
| `TA-B-CTRL-007` | Kernel recursion equals an independent direct-sum oracle at boundaries and random samples. |
| `TA-B-CTRL-008` | Raw kernel/rate companions remain materialized beside normalized surprises. |

These identifiers are preregistered plan controls, not yet incident-register
controls and not yet PASS.

## 7. Artifact map

### CTO scientific/governance artifacts

```text
TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md                  COMPLETE_DRAFT
TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md COMPLETE_PLAN
TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md  FROZEN_BY_HUMAN
TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md EXECUTED_PASS
TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md              COMPLETE_DRAFT_NOT_FROZEN
TRADING_ACTIVITY_BINDING_B_MULTISESSION_PILOT_RUN_PLAN_v0_1.md      BLOCKED
TRADING_ACTIVITY_BINDING_B_FOUR_SHARD_PROBE_CERTIFICATION_READOUT_v0_1.md BLOCKED
TRADING_ACTIVITY_BINDING_B_FULL_SCIENTIFIC_EVIDENCE_VERDICT_v0_1.md BLOCKED
TRADING_ACTIVITY_BINDING_B_INDEPENDENT_REPLAY_PLAN_v0_1.md          BLOCKED
TRADING_ACTIVITY_BINDING_B_INDEPENDENT_REPLAY_READOUT_v0_1.md       BLOCKED
TRADING_ACTIVITY_BINDING_A_B_COMPARISON_PREREGISTRATION_v0_1.md     BLOCKED
```

### Data Foundation executable artifacts

```text
scripts/trading_activity_binding_b_kernel.py                         BLOCKED
scripts/trading_activity_binding_b_multisession_engine.py            BLOCKED
scripts/run_trading_activity_binding_b_multisession_pilot.py         BLOCKED
scripts/monitor_trading_activity_binding_b_multisession_pilot.ps1    BLOCKED
scripts/preflight_trading_activity_binding_b.py                      BLOCKED
scripts/validate_trading_activity_binding_b_shard_probes.py          BLOCKED
scripts/audit_trading_activity_binding_b_full_evidence.py            BLOCKED
scripts/run_trading_activity_binding_b_independent_replay.py         BLOCKED
configs/trading_activity_binding_b_multisession_pilot_v0_1.json      BLOCKED
tests/test_trading_activity_binding_b_kernel.py                       BLOCKED
tests/test_trading_activity_binding_b_multisession_engine.py          BLOCKED
tests/test_trading_activity_binding_b_multisession_runner.py          BLOCKED
tests/test_audit_trading_activity_binding_b_full_evidence.py          BLOCKED
```

`BLOCKED` means the artifact must not be created as executable authority before
the exact specification receives its explicit freeze gate.

## 8. Current gate

```text
B-00 proposal                         = COMPLETE_DRAFT_NOT_FROZEN
A-process reconstruction              = COMPLETE
development/certification sequence    = PREREGISTERED_NOT_EXECUTABLE
B-01 inheritance and delta contract   = FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT
B-02 exact specification              = DRAFT_AMENDED_NOT_FROZEN_10_RESOLVED_2_OPEN
B-03 implementation                   = NOT_AUTHORIZED
B-08 shard probes                     = NOT_AUTHORIZED
B-12 long materialization             = NOT_AUTHORIZED
B-17 A/B comparison                   = NOT_AUTHORIZED
B-18 temporal OOS                     = NOT_AUTHORIZED
```

The next safe action is to create or obtain the governed Wake-up label/counting
authority for `B02-D07` and the sealed final-lockbox manifest for `B02-D12`,
then run a final consistency review and obtain a separate explicit human B-02
freeze. No Python implementation or runtime launch is authorized by this plan.
