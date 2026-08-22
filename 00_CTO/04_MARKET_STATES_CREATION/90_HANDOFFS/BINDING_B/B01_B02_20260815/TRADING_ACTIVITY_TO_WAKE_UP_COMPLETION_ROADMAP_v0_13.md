# Trading Activity to Wake-up completion roadmap v0.13

## 0. Artifact control

| Field | Value |
|---|---|
| `document_version` | `v0_13` |
| `document_role` | `WORKSTREAM_COMPLETION_ROADMAP` |
| `document_status` | `CURRENT_PLANNING_SEQUENCE` |
| `current_stage` | `TA_3R8_BINDING_B_EXACT_SPECIFICATION_REVIEW` |
| `current_next_gate` | `CLOSE_B02_DECISIONS_AND_EXPLICIT_HUMAN_FREEZE` |
| `supersedes` | `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_12.md` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `predictive_consumption` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-15` |

## 1. Current position

```text
B-00 Binding B proposal                       = COMPLETE_DRAFT_NOT_FROZEN
B-01 inheritance/delta                        = FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT
B-02 exact specification                      = DRAFT_PREPARED_NOT_FROZEN
B-02 blocking decisions                       = 12 OPEN
B-03 implementation                           = NOT_AUTHORIZED
B-08 all-variable/all-shard probes            = NOT_AUTHORIZED
B-12 long materialization                     = NOT_AUTHORIZED
B-17 A/B comparison                           = NOT_AUTHORIZED
B-18 temporal OOS                             = NOT_AUTHORIZED
```

## 2. Governing authorities

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md

VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md

VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md

VARIABLES_FEATURES/
TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md
```

## 3. Current review gate

B-01 is closed. B-02 is not. The next gate is to resolve its twelve explicit
decisions covering mathematical thresholds, zero/censoring, storage topology,
statistical capacity, false-alarm calibration, uncertainty, compute budget and
the hash-bound final lockbox.

```text
B-02 review
-> resolve B02-D01..D12
-> independent scientific consistency audit
-> explicit human B-02 freeze
```

No code is authorized by this roadmap version.

## 4. Sequence after a future B-02 freeze

```text
B-03 pure semantic oracle and adversarial tests
-> B-04 typed schema and physical smoke
-> B-05 governed runner, monitor, resume and terminal certifier
-> B-06 bounded multisession pilot
-> B-07 bind exact A denominator without reselection
-> B-08 one production-equivalent probe per variable in every shard
-> B-09 value-level output audit and versioned certification
-> B-10 performance profile and optional equivalent optimization
-> B-11 prepared non-executable full plan
-> separate explicit human authorization
-> B-12 long materialization
-> B-13 terminal certification
-> B-14 family-by-family scientific audit
-> B-15 independent nonlinear-feature replay
-> B-16 candidate-comparison admission
-> B-17 A/B comparison at frozen false-activation budget
-> select one candidate
-> B-18 final temporal OOS for the selected candidate only
```

## 5. Long-run boundary

No long operation is authorized. A future long path must comply with
`LONG_RUNNING_OPERATIONS_CONTRACT.md`, refuse resume across spec/schema/config/
code hash changes, rehearse its terminal certifier in every shard probe and
receive a separate human launch authorization.

