# Representation Model Materialization and Incident Learning Protocol v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `representation_model_materialization_and_incident_learning_protocol` |
| `document_version` | `v0_1` |
| `document_role` | `CROSS_MODEL_MATERIALIZATION_GOVERNANCE_PROTOCOL` |
| `document_status` | `ACTIVE` |
| `scope` | `All current and future Representation Model materializations` |
| `semantic_owner` | `00_CTO/04_MARKET_STATES_CREATION` |
| `executable_owner` | `01_TSIS_DATA_FOUNDATION` |
| `created_at` | `2026-08-14` |

## 1. Purpose

Every materialization defect must become durable prevention knowledge. A fix is
not complete when one run succeeds: it is complete only when the defect is
registered, tested, verified through the terminal production path and imported
as an applicable control by later Representation Models.

This protocol governs Trading Activity recovery and the ten subsequent model
materializations currently anticipated by the workstream.

## 2. Non-negotiable lifecycle

```text
detect
-> freeze and contain affected artifacts
-> persist evidence
-> register incident before correction
-> establish root cause
-> implement a versioned correction
-> add regression and adversarial tests
-> repeat production-equivalent probes on every planned shard
-> rehearse the exact terminal path
-> close incident as verified
-> promote the prevention control
-> import applicable controls into the next model
```

Errors are never deleted from the register. Superseded plans, failed manifests,
logs and outputs remain immutable historical evidence. `resume` must never mix
code, schema, plan, source or policy versions.

## 3. What production-equivalent means

A probe is production-equivalent only when it exercises the same:

- source and eligibility policy;
- exact membership selection;
- formulas, schema and lineage;
- runner and worker implementation;
- wrapper and aggregation path;
- terminal certifier and final-manifest writer;
- failure handling, heartbeat, resume and telemetry contracts.

Testing only the calculation engine is insufficient. The terminal path is part
of the product and must be exercised before a long run is authorized.

## 4. Incident classes and minimum evidence

| Severity | Meaning | Required treatment |
|---|---|---|
| `LOW` | Local defect with no semantic or denominator impact | Register, correct and add a focused regression test. |
| `MEDIUM` | Reproducibility, telemetry or bounded operational impact | Register, version correction, test and terminal-path probe. |
| `HIGH` | Schema, cardinality, target membership, PIT, certification or promotion risk | Register, detailed readout, all-shard reprobe and terminal rehearsal. |
| `CRITICAL` | Leakage, silent data corruption, false promotion or destructive loss | Stop work, quarantine evidence, detailed readout, independent review and full gate repetition. |

All incidents require a register entry. `HIGH` and `CRITICAL` incidents also
require a dedicated versioned incident or execution readout.

## 5. Mandatory prevention controls

Every model plan, implementation and certifier must enforce:

1. **Exact target membership.** An explicit target list may not be replaced by
   `min(date) <= date <= max(date)` or any interval proxy.
2. **Typed count domains.** Metadata such as `decision_seconds_total` must not
   share dictionaries, schemas or equality checks with physical-family counts.
3. **One cardinality authority.** Plan, runner, monitor and certifier must call
   or derive from the same authoritative count specification. Duplicated count
   formulas are prohibited.
4. **Correct decision grid.** Session decision seconds obey the declared
   boundary convention, including the terminal-second exclusion where the
   contract specifies `session_seconds - 1`.
5. **Complete dimension product.** Counts must include every declared horizon,
   baseline and window dimension, including the five PIT-baseline windows in
   Trading Activity Binding A.
6. **Adversarial fixtures.** Tests must include sparse non-contiguous targets,
   early-close sessions, metadata/count separation and at least one complete
   small end-to-end terminal run.
7. **Shard equivalence.** One bounded production-equivalent probe must pass on
   every planned shard after any correction; a failure invalidates all probes
   for that version.
8. **Specification-bound validators.** Validator parameters and branches must
   be tied to a versioned specification/configuration hash and tested across
   every declared value and boundary; ungoverned simplifying constants are
   prohibited.

## 6. Required inherited-control section

Every long-run plan must contain `inherited_incident_controls`. For each
applicable control it records:

```text
control_id
source_incident_id
applicability = applicable | not_applicable_with_reason
implementation_reference
regression_test_reference
probe_evidence_reference
terminal_rehearsal_reference
status = PASS | FAIL | PENDING
```

A `not_applicable` decision requires an explicit technical reason. Silence is
not equivalent to non-applicability.

The execution readout must repeat the matrix with immutable hashes and actual
test/probe results. A later model cannot inherit a control only by citing this
protocol; it must prove the control is present in its own execution path.

## 7. Authorization formula

```text
MODEL_LONG_MATERIALIZATION_AUTHORIZED =
    specification_frozen
AND authoritative_count_formula_single
AND exact_membership_selection_pass
AND unit_and_adversarial_tests_pass
AND end_to_end_terminal_rehearsal_pass
AND all_shard_probes_pass
AND inherited_incident_controls_pass
AND plan_config_code_schema_source_hashes_frozen
AND human_or_governed_authorization
```

Any false or pending term is fail-closed.

## 8. Incident closure formula

```text
CLOSED_VERIFIED =
    root_cause_documented
AND correction_versioned
AND regression_tests_pass
AND all_planned_shard_probes_repeated_and_pass
AND exact_terminal_path_rehearsal_pass
AND prevention_control_registered
AND next_applicable_plan_imports_control
```

A calculation reaching its last block does not imply certification. A failed
historical run is never relabelled after recovery; the recovery receives its
own run identity and readout.

## 9. Responsibilities

`00_CTO/04_MARKET_STATES_CREATION` owns semantic policy, incident taxonomy,
applicability and model-to-model inheritance. `01_TSIS_DATA_FOUNDATION` owns
executable enforcement, test fixtures, runner/certifier parity, manifests and
evidence. The human or governed gate owns final authorization for long runs.

## 10. Current mandatory controls

The current inherited control set is `RM-MAT-CTRL-001` through
`RM-MAT-CTRL-006` in
`REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md`. These are
mandatory for Trading Activity target-only recovery. Controls 001..003 are
universally required for later materializations; 004..005 are required wherever
their identity and explicit-Parquet-file conditions apply. Control 006 is
required for every parameterized validator, certifier and evidence auditor.
