# Trading Activity handoff and roadmap lineage consolidation v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_handoff_and_roadmap_lineage_consolidation` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTED_TRANSIENT_SNAPSHOT_PRUNING_AUDIT` |
| `document_status` | `PASS_LINEAGE_CONSOLIDATED` |
| `created_at` | `2026-08-15` |
| `scientific_semantics_changed` | `false` |
| `execution_authority_changed` | `false` |

## 1. Purpose

The handoff and completion-roadmap files are living pointers, not the durable
home of run evidence or scientific contracts. Successive versions had created
a chain of transient snapshots even though their substantive milestones were
already preserved in dedicated plans, readouts, manifests, incident records
and exact specifications.

This audit reduces the active corpus without deleting scientific evidence.

## 2. Retained files

```text
CURRENT_STATUS_AND_HANDOFF_v0_28.md
= sole current handoff authority

TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_17.md
= sole current roadmap authority

CURRENT_STATUS_AND_HANDOFF_v0_12.md
= temporary compatibility retention only;
  externally referenced by 00_CTO_APPLIED_ARCHITECTURE;
  original snapshot SHA-256
  e68cae3fa6dbacf3ffda8e85130b01fda48f518f523ea84bd4c26adc6eccbf31;
  amended with an explicit redirect to v0_28;
  not current authority
```

Post-consolidation transient successors were also removed after the selector
ownership correction:

```text
CURRENT_STATUS_AND_HANDOFF_v0_26.md
SHA-256 = bc5efdf8858653f170f9ac3d7d4f2a1242307f644a6231d2e1f8f371c7b3ae31
recovery = Recycle Bin

TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_15.md
SHA-256 = 925f0a9588f5b2af0d3b8bfb1c3b3399a16667acdda2af968579931395123045
recovery = Recycle Bin

CURRENT_STATUS_AND_HANDOFF_v0_27.md
SHA-256 = be3a982e4f4cbc00c5050e311dd37f6f3f717d1b1edff7e3fa8693b93c9e32fc
recovery = Recycle Bin

TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_16.md
SHA-256 = 53f0b50b9e7c7c1baa65306fb9dc3b9b97de56a1d5fc9270b1cb085d39cf12f6
recovery = Recycle Bin
```

Accepted audit-package copies were not modified. In particular, the immutable
Binding B handoff package may continue to contain its own v0.24/v0.13 snapshot
copies and hashes.

## 3. Removed handoff snapshots

| Version | SHA-256 before removal | Recorded stage | Recovery authority |
|---|---|---|---|
| `v0_8` | `5bd130bae39705ae2ec8eb79e411827466dde7e1d41e1119f84cd10375fce1e5` | `wake_up_trading_activity_ta_3` | Git |
| `v0_9` | `040ae33f9b666d2fb7f6fc95359299a78f14196256e0fc196e4d58c4643b2b87` | `wake_up_trading_activity_ta_3` | Git |
| `v0_10` | `45a7c6267d24712c3f07553a64500b463ffcba2d0c02ae148754eda195b86f3f` | `wake_up_trading_activity_ta_3` | Git |
| `v0_11` | `f545d9f0752c21ef6b9102574c5ce261c6038f8c4788dcc893635e04340cb750` | `wake_up_trading_activity_stage8_cpp_equivalence` | Git |
| `v0_13` | `46dac2b4ff2fbc33375d5bedc9a2d3e853f31d8a8280863e8eb2c038ab9f342f` | `wake_up_trading_activity_cpp_full_materialization` | Git |
| `v0_14` | `396ac8907b8bcf29035bb7b206d98804165db85229a07e2ee817754c63ccdf11` | `trading_activity_stage8_target_only_recovery_preparation` | Recycle Bin |
| `v0_15` | `fe3c9f6d1c5b3dccbe5cee5a0ef3b314fe5015c7df53817bff22b987863fc7ba` | `trading_activity_stage8_target_only_recovery_and_cross_model_incident_governance` | Recycle Bin |
| `v0_16` | `bbb7e7e9cf768da68541a90b1887ca6e5056bf5c0f0b5e9f4134d9138dc46365` | `trading_activity_stage8_target_only_full_integrity_authorization` | Recycle Bin |
| `v0_17` | `cc297dbb29275ce97ee1c9cff6b38e64d93bce5e4dd3bac422c710e816224ec8` | `trading_activity_stage8_target_only_full_integrity_execution` | Recycle Bin |
| `v0_18` | `eca63c510e82b40118946ce563342898b69fc09bb9941b36424d948eeb6118f3` | `trading_activity_binding_a_evidence_verdict` | Recycle Bin |
| `v0_19` | `92ff02be0edeaf0b942f7c0c140e919fb58d08b2840bfa4a029891a70227598b` | `trading_activity_binding_b_preregistration` | Recycle Bin |
| `v0_20` | `c04c45fa9bcdc0670592c4ad1d94a358f9fe11b689325627b6fe7f6cd2360d09` | `trading_activity_binding_a_independent_percentile_replay` | Recycle Bin |
| `v0_21` | `8271f1a2d2e9964519ab5e7ecc283db52d121bb7e366cb567b46d82f1927750e` | `trading_activity_binding_b_preregistration` | Recycle Bin |
| `v0_22` | `b204f4e52d234efc4657c7c7898f4f1d3fc1c0037166442adfa4df62df39cf4b` | `trading_activity_binding_b_preregistration_review` | Recycle Bin |
| `v0_23` | `9b8dd39875d40c6d2b204430a50ebf944c32320dbd056dab77fe9dea694b3804` | `trading_activity_binding_b_inheritance_and_exact_specification` | Recycle Bin |
| `v0_24` | `4eb5b1a1c28c72a063e44baa137510947f8773de3c4a57af5e49475539efaa0f` | `trading_activity_binding_b_exact_specification_review` | Recycle Bin; immutable package copy also exists |
| `v0_25` | `967a61e7a0da099a5294e619d1d1b9ca9566d1399915be671b881bfa991629d2` | `trading_activity_binding_b_b02_authority_completion` | Recycle Bin |

## 4. Removed roadmap snapshots

| Version | SHA-256 before removal | Recorded stage | Recovery authority |
|---|---|---|---|
| `v0_3` | `157173ce296039bb78e9dea00810179bbfb5d971c1d2897ef6a6f2123bc3c37d` | `TA_3_STRATIFIED_DEVELOPMENT` | Git |
| `v0_4` | `8fb539270b9bb24c4116daa25ba12492a0fc0127f5c1073dca8f5eea63c59525` | `TA_3_BINDING_A_TARGET_ONLY_RECOVERY` | Recycle Bin |
| `v0_5` | `bd196ef89c2511456b9f44c6107b39e66217e47be1e376b92bb8c4bc8e174256` | `TA_3_BINDING_A_TARGET_ONLY_RECOVERY_AND_INCIDENT_CONTROL_VERIFICATION` | Recycle Bin |
| `v0_6` | `3dd5e636e02c8a92a7d41cc01c32a769a0177694a49ccc57048b986d545eb22c` | `TA_3_BINDING_A_FULL_TARGET_ONLY_INTEGRITY_AUTHORIZATION` | Recycle Bin |
| `v0_7` | `a4db1989a02fca38ee99ba3f969f75c2bacbb62e42d777dbe587f53bcc394ed0` | `TA_3R6_BINDING_A_EVIDENCE_VERDICT` | Recycle Bin |
| `v0_8` | `f72ec3bbfb163a111ad3143d39a53da320d465f6856c82949a417809a834de6f` | `TA_3R7_BINDING_B_PREREGISTRATION` | Recycle Bin |
| `v0_9` | `9b3c4500da5230eac1c767d828c1800f34da691a7c30a49bbffd334259cee05b` | `TA_3R6B_INDEPENDENT_PERCENTILE_REPLAY` | Recycle Bin |
| `v0_10` | `1bce4a809f0f2310d8193757b82c1f7cb2931c2578658f9e0637c5695722bb31` | `TA_3R7_BINDING_B_FROZEN_PREREGISTRATION` | Recycle Bin |
| `v0_11` | `32f84b1b906542894cf6c2338ecca4150457d483e16bac2a645ebad61f02fbbc` | `TA_3R7_BINDING_B_PREREGISTRATION_REVIEW` | Recycle Bin |
| `v0_12` | `16647493465bc964f8b374e65026738368b045ca30bcef13c37a2e22dfba18e2` | `TA_3R8_BINDING_B_INHERITANCE_AND_EXACT_SPECIFICATION` | Recycle Bin |
| `v0_13` | `8f633392d190c4ab2c0331a61baebca947dedf95d1ac3de24bb641dc0fdeb582` | `TA_3R8_BINDING_B_EXACT_SPECIFICATION_REVIEW` | Recycle Bin; immutable package copy also exists |
| `v0_14` | `1e9d08ddb286159c8b22eb6c34acc8a31e9b33c7e0ace1e4a543c6c3c020111c` | `TA_3R9_BINDING_B_B02_AUTHORITY_COMPLETION` | Recycle Bin |

## 5. Durable milestone authorities

```text
TA-3 sampling and source decisions
-> TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md
-> TRADING_ACTIVITY_TA3_BINDING_A_ORCHESTRATOR_READOUT_v0_1.md

C++ equivalence and full/target-only certification
-> TRADING_ACTIVITY_STAGE8_CPP_ENGINE_INTEGRATION_AND_FOUR_SHARD_RECERTIFICATION_READOUT_v0_1.md
-> TRADING_ACTIVITY_STAGE8_CPP_FULL_MATERIALIZATION_EXECUTION_AND_CERTIFICATION_READOUT_v0_1.md
-> TRADING_ACTIVITY_STAGE8_TARGET_ONLY_IMPLEMENTATION_AND_FOUR_SHARD_PROBE_READOUT_v0_1.md
-> TRADING_ACTIVITY_STAGE8_TARGET_ONLY_FULL_EXECUTION_AND_CERTIFICATION_READOUT_v0_1.md

incident prevention and replay evidence
-> REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md
-> TRADING_ACTIVITY_BINDING_A_FULL_SCIENTIFIC_EVIDENCE_VERDICT_v0_2.md
-> TRADING_ACTIVITY_BINDING_A_INDEPENDENT_PERCENTILE_REPLAY_FULL_EXECUTION_READOUT_v0_1.md

Binding B preparation and current blockers
-> TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md
-> TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md
-> TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md
-> TRADING_ACTIVITY_BINDING_B_B02_DECISION_RESOLUTION_AND_SCIENTIFIC_REVIEW_v0_1.md
-> TRADING_ACTIVITY_D07_D12_UPSTREAM_AUTHORITY_WORKSTREAM_READOUT_v0_1.md
```

## 6. Result

```text
snapshots reviewed                   = 36
current authorities retained         = 2
compatibility snapshot retained      = 1
transient snapshots removed          = 33
dedicated evidence artifacts removed = 0
accepted package contents modified   = 0
scientific gates changed             = 0
B-03 authorized                      = false
```
