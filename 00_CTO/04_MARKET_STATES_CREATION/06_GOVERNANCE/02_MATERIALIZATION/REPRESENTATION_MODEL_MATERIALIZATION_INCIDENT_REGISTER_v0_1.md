# Representation Model Materialization Incident Register v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `representation_model_materialization_incident_register` |
| `document_version` | `v0_1` |
| `document_role` | `APPEND_ONLY_INCIDENT_AND_PREVENTION_CONTROL_REGISTER` |
| `document_status` | `ACTIVE` |
| `created_at` | `2026-08-14` |
| `governing_protocol` | `REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md` |

## 1. Register rules

This register is append-only. Existing incident facts and identifiers must not
be silently rewritten or removed. Corrections, status changes and closure
evidence are appended with dates and immutable artifact references.

Minimum fields for every new incident:

```text
incident_id, detected_at, model, binding, run_id, severity, status,
observed_failure, containment, root_cause, affected_contracts,
correction_version, regression_tests, shard_probe_evidence,
terminal_rehearsal_evidence, prevention_control_id, applicability,
closure_decision, closure_date
```

## 2. Active incident matrix

| Incident | Severity | Status | Root cause | Prevention control |
|---|---|---|---|---|
| `RM-MAT-INC-001` | `HIGH` | `BOUNDED_VERIFIED_FULL_CLOSURE_PENDING` | The terminal certifier compared three physical-family counts with an expected dictionary that also contained metadata field `decision_seconds_total`. | `RM-MAT-CTRL-001` |
| `RM-MAT-INC-002` | `HIGH` | `BOUNDED_VERIFIED_FULL_CLOSURE_PENDING` | The exact 2,400-row `TARGET` denominator was collapsed to an evaluation-date interval, so the complete block scope was materialized instead of exact target membership. | `RM-MAT-CTRL-002` |
| `RM-MAT-INC-003` | `HIGH` | `BOUNDED_VERIFIED_FULL_CLOSURE_PENDING` | Count logic was duplicated and stale: session seconds did not apply the terminal-second exclusion and PIT-baseline totals omitted the five-window dimension. | `RM-MAT-CTRL-003` |
| `RM-MAT-INC-004` | `HIGH` | `CORRECTED_BOUNDED_VERIFIED_FULL_CLOSURE_PENDING` | `target_ordinal` was assumed globally unique although its domain restarts across upstream groups; the real identity is the frozen four-field TARGET key. | `RM-MAT-CTRL-004` |
| `RM-MAT-INC-005` | `MEDIUM` | `CORRECTED_BOUNDED_VERIFIED_FULL_CLOSURE_PENDING` | Dataset-style Parquet reading inferred `run_id=...` from the parent path and collided with the physical manifest `run_id` column. | `RM-MAT-CTRL-005` |

The first three incidents were exposed at terminal certification of:

```text
logical run id  = trading_activity_ta3_cpp_full_v0_1_20260811
physical run id = ta3_cpp_v0_1_20260811
calculation     = COMPLETE_4_OF_4_240_OF_240
certification   = FAILED_NOT_PROMOTED
```

Authoritative detailed evidence:

`VARIABLES_FEATURES/TRADING_ACTIVITY_STAGE8_CPP_FULL_MATERIALIZATION_EXECUTION_AND_CERTIFICATION_READOUT_v0_1.md`

The failed source artifacts remain frozen. No entry authorizes relabelling that
run or recomputing all 240 blocks.

Status update `2026-08-14`: focused tests and fresh production-equivalent
probes in all four shards provide bounded PASS evidence for controls 001..005.
Incidents 004..005 were then caught by the preparation gate before any full
integrity run was authorized. All five remain open until the full closure gate
and later-model inheritance requirements pass.

## 3. Prevention controls

### RM-MAT-CTRL-001 — typed metadata/family-count separation

The plan, runner and certifier must represent physical-family row counts in a
typed structure containing only physical families. Metadata and derived scalar
totals live in a separate structure. A full terminal-path fixture must prove
that the certifier compares like-for-like domains and writes the expected final
manifest.

### RM-MAT-CTRL-002 — exact target membership

Selection must join against the immutable exact target key set. Range inference
from minimum and maximum dates is prohibited. Tests must include a sparse,
non-contiguous target list inside a wider available interval and prove that no
non-target session is selected or counted.

### RM-MAT-CTRL-003 — single authoritative cardinality contract

One authoritative function/specification must calculate decision-grid and
family cardinalities for the plan, runner and certifier. Tests must cover a
regular session, an early close and the full declared dimension product. An
independent assertion must compare preregistered plan totals with runtime totals
without reimplementing the formula.

### RM-MAT-CTRL-004 — prove identity domain; never trust an ordinal implicitly

Every membership, uniqueness and resume key must use the governed composite
identity unless the producing contract explicitly proves an ordinal globally
unique over the same denominator. Tests must contain duplicate ordinals attached
to distinct valid target keys and prove that both remain distinct.

### RM-MAT-CTRL-005 — explicit manifest files bypass dataset partition inference

A named Parquet manifest below directories such as `run_id=...` must be read as
an explicit file, not as a partitioned dataset, unless partition-column merging
is intentional and schema-certified. Tests must include the same column both in
the path and physical file and prove no type collision or silent substitution.

## 4. Applicability

```text
Trading Activity target-only recovery       = REQUIRED
Trading Activity Binding B and optional C   = REQUIRED
ten subsequent Representation Models        = CONTROLS_001_003_REQUIRED; 004_005_WHERE_APPLICABLE
future Representation Model materialization = REQUIRED_WHERE_APPLICABLE
```

Any `not_applicable` result must be justified in the later model's
`inherited_incident_controls` matrix.

## 5. Closure gate for RM-MAT-INC-001..005

These incidents remain open until the target-only recovery version provides:

- versioned implementation and plan/config identities;
- focused regression and adversarial tests for all three controls;
- fresh `PASS` probes on all four logical shards;
- one exact wrapper-to-final-manifest terminal rehearsal;
- human-authorized target-only execution and terminal certification;
- a versioned execution readout linking hashes and evidence;
- proof that the next applicable model plan imports the controls.

Until then their status must not be changed to `CLOSED_VERIFIED`.

## 6. Appended incident records

### RM-MAT-INC-004 — non-global ordinal used as target identity

```text
detected_at: 2026-08-14, real PROBE-plan construction
model / binding: Trading Activity / Binding A Stage-8 target-only recovery
run_id: ta3_stage8_target_only_probe_v0_2_20260814 preparation
severity: HIGH
status: CORRECTED_BOUNDED_VERIFIED_FULL_CLOSURE_PENDING
observed_failure: plan construction rejected duplicate target_ordinal=1 across valid targets
containment: no long run authorized; failed plan was not written or executed
root_cause: target_ordinal has a local upstream domain and was incorrectly treated as global identity
affected_contracts: target membership, probe selection, inventory uniqueness, resume identity
correction_version: trading_activity_stage8_target_only_contract_v0_2 exact four-field key correction
regression_tests: test_trading_activity_stage8_target_only_recovery.py PASS
all-shard probe evidence: target-only implementation/probe readout; PASS 4/4
terminal rehearsal evidence: exact wrapper-to-final-manifest probes PASS 4/4
prevention_control_id: RM-MAT-CTRL-004
applicability: every model using ordinals for identity, membership, uniqueness or resume
closure_decision: PENDING_FULL_TERMINAL_PASS_AND_LATER_PLAN_IMPORT
closure_date: null
```

### RM-MAT-INC-005 — accidental Hive inference on explicit Parquet manifest

```text
detected_at: 2026-08-14, focused terminal fixture
model / binding: Trading Activity / Binding A Stage-8 target-only recovery
run_id: local bounded terminal rehearsal
severity: MEDIUM
status: CORRECTED_BOUNDED_VERIFIED_FULL_CLOSURE_PENDING
observed_failure: Arrow type merge conflict for run_id physical column versus run_id=... path partition
containment: test failed before real probe; no source or runtime evidence mutated
root_cause: dataset-style reader applied Hive partition inference to an explicitly named manifest file
affected_contracts: source hash-index loading and sample partition inspection
correction_version: explicit ParquetFile.read implementation
regression_tests: test_trading_activity_stage8_target_only_recovery.py PASS 5/5
all-shard probe evidence: target-only implementation/probe readout; PASS 4/4
terminal rehearsal evidence: exact wrapper-to-final-manifest probes PASS 4/4
prevention_control_id: RM-MAT-CTRL-005
applicability: models reading explicit Parquet files under key=value directories
closure_decision: PENDING_FULL_TERMINAL_PASS_AND_LATER_PLAN_IMPORT
closure_date: null
```

## 7. Template for appended incidents

### RM-MAT-INC-NNN — short title

```text
detected_at:
model / binding:
run_id:
severity:
status:
observed_failure:
containment:
root_cause:
affected_contracts:
correction_version:
regression_tests:
all-shard probe evidence:
terminal rehearsal evidence:
prevention_control_id:
applicability:
closure_decision:
closure_date:
```

## 8. Appended terminal verification update — 2026-08-14

This update is append-only and does not rewrite the historical incident facts.

```text
run_id: ta3_stage8_target_only_full_recovery_v0_3_20260814
terminal_status: PASS
final_manifest_sha256: 421c5728cd9dd54195e7993258636884ffb6c887ab543d36d924579cab424956
exact_target_count: 2400
partition_verification: 7200/7200 PASS
failed_partitions: 0
source_blocks_recomputed: 0
runtime_controls: RM-MAT-CTRL-001..005 PASS
execution_readout: TRADING_ACTIVITY_STAGE8_TARGET_ONLY_FULL_EXECUTION_AND_CERTIFICATION_READOUT_v0_1.md
```

Current appended disposition for each incident:

| Incident | Appended status | Remaining closure term |
|---|---|---|
| `RM-MAT-INC-001` | `FULL_TERMINAL_VERIFIED_LATER_PLAN_IMPORT_PENDING` | next applicable model plan imports `RM-MAT-CTRL-001` |
| `RM-MAT-INC-002` | `FULL_TERMINAL_VERIFIED_LATER_PLAN_IMPORT_PENDING` | next applicable model plan imports `RM-MAT-CTRL-002` |
| `RM-MAT-INC-003` | `FULL_TERMINAL_VERIFIED_LATER_PLAN_IMPORT_PENDING` | next applicable model plan imports `RM-MAT-CTRL-003` |
| `RM-MAT-INC-004` | `FULL_TERMINAL_VERIFIED_LATER_PLAN_IMPORT_PENDING` | import if applicable or justify non-applicability |
| `RM-MAT-INC-005` | `FULL_TERMINAL_VERIFIED_LATER_PLAN_IMPORT_PENDING` | import if applicable or justify non-applicability |

The full-denominator runtime term is satisfied. None is yet
`CLOSED_VERIFIED`, because the protocol also requires immutable evidence from
the next applicable model plan.

## 9. Appended Binding A evidence-audit incidents — 2026-08-14

This section is append-only. It preserves both failed attempts before the
operative `rerun3` result.

### RM-MAT-INC-005 recurrence — explicit Parquet control not imported by new auditor

```text
detected_at: 2026-08-14, first Binding A value-level evidence audit attempt
model / binding: Trading Activity / Binding A v0.2
run_id: trading_activity_binding_a_full_evidence_audit_v0_1_20260814
severity: MEDIUM
status: RECURRENCE_CORRECTED_BOUNDED_VERIFIED_LATER_PLAN_IMPORT_PENDING
observed_failure: Arrow type merge conflict for ticker physical string versus ticker=... path partition
containment: process stopped before the first selected target; no materialized data changed
root_cause: the new auditor failed to import already-applicable RM-MAT-CTRL-005
correction_version: audit_trading_activity_binding_a_full_evidence.py explicit ParquetFile reader
regression_tests: explicit Hive-looking path plus physical ticker column PASS
bounded evidence: rerun3 covered 20 sessions across all four shards and passed
prevention_control_id: RM-MAT-CTRL-005
closure_decision: PENDING_NEXT_APPLICABLE_PLAN_IMPORT
closure_date: null
```

### RM-MAT-INC-006 — validator parameter assumed instead of bound to specification

```text
detected_at: 2026-08-14, Binding A value-level evidence audit rerun1
model / binding: Trading Activity / Binding A v0.2
run_id: trading_activity_binding_a_full_evidence_audit_v0_1_rerun1_20260814
severity: MEDIUM
status: CORRECTED_BOUNDED_VERIFIED_LATER_PLAN_IMPORT_PENDING
observed_failure: 849,560 false failures from requiring one-second subwindows for W=60 and W=300
containment: verdict remained FAIL and was not promoted; source outputs were read-only
root_cause: auditor encoded an unreviewed constant instead of the exact W-to-w specification
affected_contracts: variable conformance, temporal concentration and human evidence gate
correction_version: explicit Binding A v0.2 mapping plus specification SHA-256 in manifests
regression_tests: four focused auditor tests PASS, including all five W-to-w values
bounded evidence: rerun3 repeated all 20 sessions, 79 check types and zero hard failures
prevention_control_id: RM-MAT-CTRL-006
applicability: every parameterized model validator, certifier and scientific evidence audit
closure_decision: PENDING_NEXT_APPLICABLE_PLAN_IMPORT
closure_date: null
```

### RM-MAT-CTRL-006 — validator parameters bound to governed specification

Every validator, certifier and scientific evidence auditor must bind its
parameter expectations to a versioned specification or executable
configuration and persist that authority's SHA-256. Tests must exercise every
declared parameter branch and boundary. A validator-specific default or
hardcoded simplification that is not present in the governed authority is
prohibited.

Current appended disposition:

| Incident | Appended status | Remaining closure term |
|---|---|---|
| `RM-MAT-INC-005` | `RECURRENCE_CORRECTED_BOUNDED_VERIFIED_LATER_PLAN_IMPORT_PENDING` | next applicable plan imports and proves `RM-MAT-CTRL-005` |
| `RM-MAT-INC-006` | `CORRECTED_BOUNDED_VERIFIED_LATER_PLAN_IMPORT_PENDING` | next applicable plan imports and proves `RM-MAT-CTRL-006` |
