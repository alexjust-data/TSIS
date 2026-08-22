# Representation Model Materialization Execution and Certification Contract v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `representation_model_materialization_execution_and_certification_contract` |
| `document_version` | `v0_1` |
| `document_role` | `DATA_FOUNDATION_EXECUTABLE_MATERIALIZATION_CONTRACT` |
| `document_status` | `ACTIVE_CONTRACT_IMPLEMENTATION_REQUIRED_PER_MODEL` |
| `semantic_authority` | `00_CTO/04_MARKET_STATES_CREATION/REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md` |
| `incident_register` | `00_CTO/04_MARKET_STATES_CREATION/REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md` |
| `created_at` | `2026-08-14` |

## 1. Purpose

Translate the CTO incident-learning policy into executable requirements for
Data Foundation runners, certifiers, tests, probes and manifests. This contract
does not itself certify any model; each model version must implement and prove
the assertions below.

## 2. Required plan fields

Every materialization plan must freeze:

```text
run_id
model_id and binding_version
exact target manifest path and SHA-256
source identities and SHA-256 or immutable version IDs
schema and policy IDs
runner, wrapper and certifier identities and SHA-256
planned shards and exact shard membership
authoritative cardinality implementation identity
expected typed physical-family counts
separate metadata/scalar expectations
inherited_incident_controls
resume compatibility identity
human or governed authorization evidence
```

## 3. Exact membership contract

The target manifest is a set of immutable keys, normally
`instrument_id x session_date` plus any declared binding key. Selection uses an
exact join. It must not use minimum/maximum dates as a membership substitute.

Required assertions:

```text
selected_target_keys == frozen_target_keys
selected_non_target_keys == empty
duplicate_target_keys == empty
unresolved_target_keys == empty or explicitly fail-closed by contract
```

## 4. Typed count contract

Physical-family row counts and metadata must use distinct structures.
`decision_seconds_total`, number of windows, target count and similar scalars
must not appear in a physical-family equality domain.

A single authoritative cardinality implementation must feed plan generation,
runtime validation and terminal certification. Monitors may display those
values but must not independently redefine them.

Required adversarial cases:

- regular session;
- early-close session;
- sparse non-contiguous target dates inside a wider source interval;
- all declared horizons, windows and PIT baselines;
- metadata key added or removed without changing family-count equality;
- deliberately wrong family count producing terminal `FAIL`.

## 5. Production-equivalent probe contract

One bounded probe per planned shard must execute the same runner, wrapper,
aggregation, certifier and final-manifest writer intended for scale. It must
also validate formula/schema/grain/PIT/missingness and show readable values.

Any code, config, schema, source, policy, cardinality or terminal-path change
invalidates every probe for that version. All shard probes must be repeated.

## 6. Terminal rehearsal

Before long-run authorization, execute at least one complete small rehearsal:

```text
pre-manifest
-> exact target selection
-> worker calculation or existing-output inventory
-> aggregation
-> terminal certification
-> atomic final manifest
```

The rehearsal must test both `PASS` and an injected fail-closed condition. A
runner-only or worker-only test is insufficient.

## 7. Inherited incident control matrix

The plan and readout must contain, for every prior control:

| Field | Requirement |
|---|---|
| `control_id` | Stable ID from the incident register. |
| `source_incident_id` | Incident that produced the control. |
| `applicability` | `applicable` or reasoned `not_applicable`. |
| `implementation_reference` | Versioned code/config reference and hash. |
| `regression_test_reference` | Test identity and result. |
| `probe_evidence_reference` | All-shard evidence and hashes. |
| `terminal_rehearsal_reference` | Final-path evidence. |
| `status` | `PASS`, `FAIL` or `PENDING`. |

Missing rows, `PENDING`, `FAIL` or unjustified `not_applicable` block the run.
The current required set is `RM-MAT-CTRL-001..005`, with explicit applicability
evaluation for controls 004 and 005.

## 8. Runtime and resume

Long runs must obey `C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md`.
`resume` is allowed only when the compatibility identity proves equality of
plan, code, config, schema, source, policies, target manifest and count
authority. Otherwise the runner stops and requires a new run identity.

## 9. Final manifest and certification

The final manifest must separately report:

```text
calculation_status
inventory_status
certification_status
exact_target_counts
physical_family_counts
metadata_scalars
hash_validation
schema/grain/PIT/temporal validation
inherited_incident_controls results
promotion_status
```

`completed_blocks == total_blocks` cannot set `certification_status=PASS`.
Promotion defaults to false and requires a separate governed decision.

## 10. Incident response

On any materialization or certification defect:

1. stop or contain without mutating historical artifacts;
2. write terminal failure evidence;
3. register the incident before correction;
4. version the correction and add regression tests;
5. repeat every shard probe and terminal rehearsal;
6. emit a versioned readout;
7. promote the verified prevention control for later models.

## 11. Current Trading Activity application

The Stage-8 240-block calculation is frozen `FAILED_NOT_PROMOTED` at aggregate
certification. The target-only implementation, focused tests and all four shard
probes now provide bounded `PASS` evidence for `RM-MAT-CTRL-001..005`. Full
closure still requires verification against exactly 2,400 frozen targets and
7,200 family partitions. This contract does not authorize that long recovery
and does not authorize recomputation of the 240 blocks.

Executed evidence is recorded in
`00_CTO/04_MARKET_STATES_CREATION/VARIABLES_FEATURES/TRADING_ACTIVITY_STAGE8_TARGET_ONLY_IMPLEMENTATION_AND_FOUR_SHARD_PROBE_READOUT_v0_1.md`.
