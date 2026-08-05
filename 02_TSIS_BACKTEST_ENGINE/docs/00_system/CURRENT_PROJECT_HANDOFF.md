# TSIS Backtest Engine - Current Project Handoff

Status: `LIVE_RESTART_AUTHORITY`
As of: `2026-08-05`

This document is the canonical cold-start entry for the Backtest Engine. Read
it before changing code, governance, authorizations or physical inputs. It
summarizes the current state; accepted contracts, evidence packages and
machine-readable registers remain the underlying authorities.

## Current Authoritative State

```text
BT-GATE-014 = CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-014_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
BT-GATE-014_V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_BT_GATE_014_V0.5 = PROHIBITED
BT-GATE-014 deterministic_output_hash = 6331839dfc6538f7dd6fda9a1fd7efbc7497d541dcb0c0d89cfd679762067cb1

BT-GATE-015 = CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-015_CONTRACT = OWNER_REVIEW_PASS
BT-GATE-015_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW = PASS
BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW = PASS
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

BT-GATE-015_V0.3 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_BT_GATE_015_V0.3 = PROHIBITED
POSTEXECUTION_FAILURE_EVIDENCE_V0.3 = ACCEPTED
ROOT_CAUSE = CONFIRMED_CONSUMER_DATASET_FINGERPRINT_DOMAIN_BINDING_ERROR
PHYSICAL_FILES_OPENED / RECORDS_SCANNED / ROWS_SELECTED_V0.3 = 1 / 8 / 1
EVENTS / STORE_INSERTS / OBSERVATIONS_V0.3 = 0 / 0 / 0

BT-GATE-015_V0.4 = CONSUMED_FINAL
SECOND_EXECUTION_BT_GATE_015_V0.4 = PROHIBITED
BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW = PASS
PHYSICAL_FILES_OPENED / RECORDS_SCANNED / ROWS_SELECTED_V0.4 = 1 / 8 / 1
EVENTS / STORE_INSERTS / OBSERVATIONS_V0.4 = 1 / 1 / 1
DELIVERY_BEFORE_AVAILABLE_AT_V0.4 = 0
DETERMINISTIC_OUTPUT_HASH_V0.4 = 35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a
POSTEXECUTION_PACKAGE_SHA256 = 62f1503694c9a3d9153179289b37bc4809d660315a0779cb8a30a52f367e0870
BT-GATE-015_CLOSED_PASS = CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS

BT-GATE-016 = NOT_OPEN
BT-GATE-016_IMPLEMENTATION = NOT_AUTHORIZED
```

## Last Accepted Capability

BT-GATE-015 is closed. Its bounded Event State execution consumed V0.4 once
and produced:

```text
physical files / scanned / selected = 1 / 8 / 1
Market State dependencies / Event State events = 1 / 1
store inserts / observations = 1 / 1
early deliveries / orders / fills / PnL = 0 / 0 / 0 / false
deterministic_output_hash = 35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a
V0.4 = CONSUMED_FINAL
SECOND_EXECUTION_V0.4 = PROHIBITED
```

BT-GATE-014 remains closed as the accepted bounded Market State predecessor.
Do not reopen or reuse any BT-GATE-014 or BT-GATE-015 single-use authorization.

## BT-GATE-015 Accepted Non-Physical Evidence

```text
package = deliverables/bt_gate_015_non_physical_acceptance_packet_r3_20260731T115617Z.zip
package_sha256 = 0757cdb4b700144ffde1c0cb4f2fda433ea296172e410297494435dea406b525
focused_tests = 13/13 PASS
full_repository_suite = 235/235 PASS
governance_validation = 123/123 PASS
positive_cases = 7/7 PASS
negative_cases = 22/22 PASS
required_failure_codes = 8/8 covered
deterministic_output_hash = f149ab854105252a1b929d28858065a163bcee134bad69588b7b99a9e8de0d8d
physical Event State rows read = 0
orders / fills / PnL = 0 / 0 / false
```

The accepted synthetic path is:

```text
ReplayBarEvent
-> BoundedMarketStateAvailable
-> BoundedEventStateAvailable
-> EventStateStore
```

## Provider / Shared-Boundary Status

The provider work for the frozen Event State slice is complete. The provider
has no active gate and must remain idle unless the backtester finds a material
defect in the accepted evidence.

```text
active provider gate = none
provider modification = NOT_AUTHORIZED
new provider evidence = NOT_REQUIRED
scope expansion = NOT_AUTHORIZED

initial handoff =
event_state_session_opened_bt_gate_015_contract_handoff_v0_1_20260731T064518Z.zip
sha256 = b7a4783d0ab64ffaf37fbfdf2ee76dffacbe9b14cf3f059891908c87116369b2

completion handoff =
event_state_session_opened_bt_gate_015_provider_completion_v0_1_20260731T071317Z.zip
sha256 = 3a6bf3ca04c0428a1728e1719cd6aeaea6bfaef43e12fb83939dde3cb6cb85d9
```

The provider inspected one candidate file to produce the completion evidence.
That provider-side inspection is not the backtester physical consumer read.

## Historical Physical Slice Used By V0.3 And V0.4

The consumed V0.3 and V0.4 authorizations were limited to:

```text
event_type = event_type:market_data:session_opened
instrument = AAME
exchange = XNYS
session = 2021-01-19
candidate_file = event_state_candidate_records.jsonl
candidate_file_sha256 = ed975ad7d7a3e0ac68bd7dfe2c91743c86931a545162a4440d270cbb689477dd
record_id = e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76
record_fingerprint = 31f1463baf0dc8f0dba3bc130c0bb1d61092897595849df57abc6b1023853a01
maximum physical files = 1
maximum candidate records scanned = 8
maximum records selected = 1
```

## V0.3 Execution, Failure And Root Cause

```text
approved_preexecution_package =
deliverables/bt_gate_015_single_use_physical_preexecution_packet_v0_3_corrected_r2_20260805T105320Z.zip
approved_preexecution_sha256 = 52aab61b0f6343448d47ae988bc575df1ae86d485c4c4d3ab854bfdd554c47fe
V0.3 = CONSUMED_FAILED_FINAL
second execution = PROHIBITED
physical files opened = 1
records scanned / selected = 8 / 1
Event State events / store inserts / observations = 0 / 0 / 0
failure = FAIL_EVENT_STATE_IDENTITY_MISMATCH
root cause = CONFIRMED_CONSUMER_DATASET_FINGERPRINT_DOMAIN_BINDING_ERROR
```

The physical row provenance fingerprint `433288b6...6c235b` must bind to
`market_state_dependency_dataset_fingerprint`. The independent replay
availability evidence fingerprint `516a27d0...ac416` validates the Market State
availability sidecar. Provider evidence remains accepted and unchanged.

## V0.4 Execution Result

```text
approved_preexecution_package =
deliverables/bt_gate_015_single_use_physical_preexecution_packet_v0_4_corrected_r1_20260805T142620Z.zip
approved_preexecution_sha256 = ed26dd77908e87a84dddaac287798ca0073d9011e775ef72a5f4c1f1998d1bb5
preexecution_external_review = PASS
V0.4 = CONSUMED_FINAL
second execution = PROHIBITED
physical files opened = 1
records scanned / selected = 8 / 1
Market State dependency events = 1
Event State events / store inserts / observations = 1 / 1 / 1
typed scientific values = 17
delivery before available_at = 0
orders / fills / PnL = 0 / 0 / false
deterministic_output_hash = 35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a
validation_status = PASS
```

The independent post-execution review accepted this result and closed
BT-GATE-015 with restrictions. The physical execution must not be repeated.

## Final External Acceptance

```text
postexecution package =
deliverables/bt_gate_015_v0_4_physical_postexecution_packet_r1_20260805T150757Z.zip
postexecution package sha256 =
62f1503694c9a3d9153179289b37bc4809d660315a0779cb8a30a52f367e0870
external review = PASS
external report sha256 =
92a723ed5a704c4631431fafc928abd01d223e3218467a0c423ad3046f98c9be
```

## Next Required Work

```text
1. Preserve V0.3 and V0.4 authorizations, receipts and run evidence unchanged.
2. Do not execute RUN_BT_GATE_015_PHYSICAL_V0_4.py again.
3. Do not open BT-GATE-016 implicitly.
4. Define and review the complete BT-GATE-016 contract before implementation.
```

## Package Retention

Only the auditable package chain remains under `deliverables`:

```text
BT-GATE-014:
- final closure packet
- approved V0.5 R3 pre-execution packet
- accepted V0.5 R2 post-execution packet

BT-GATE-015:
- accepted R3 non-physical packet
- approved V0.3 R2 pre-execution packet
- accepted V0.3 consumed-failure post-execution packet
- approved V0.4 R1 pre-execution packet
- accepted V0.4 R1 post-execution packet
```

The three BT-GATE-015 external review reports are retained under
`evidence/external_reviews/bt_gate_015` with governed SHA-256 identities.
Rejected or superseded ZIP revisions, temporary audit scripts and temporary
extractions were removed on `2026-08-05`.

## Boundaries Still Closed

```text
general Event State consumption = NOT_AUTHORIZED
general Market State consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
StateBundle general reads = NOT_AUTHORIZED
provider modification = NOT_AUTHORIZED
full 2005-2026 backtest = NOT_AUTHORIZED
strategy state routing = NOT_AUTHORIZED
orders / fills / PnL from Event State = NOT_AUTHORIZED
optimization / edge claims = NOT_AUTHORIZED
```

## Mandatory Restart Reading Order

```text
1. AGENTS.md
2. LOCAL_RULES.md
3. docs/00_system/CURRENT_PROJECT_HANDOFF.md
4. docs/00_system/20_BT_GATE_015_POINT_IN_TIME_EVENT_STATE_CONSUMER_CONTRACT_V0_1.md
5. 00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/GATE_REGISTER.json
6. 00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW_ACCEPTANCE_V0_1.md
7. 00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE_V0_1.md
8. docs/00_system/26_BT_GATE_015_V0_3_CONSUMED_FAILURE_READOUT.md
9. docs/00_system/27_BT_GATE_015_V0_3_POSTEXECUTION_EXTERNAL_REVIEW.md
10. docs/00_system/28_BT_GATE_015_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_4.md
11. docs/00_system/31_BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW.md
12. docs/00_system/32_BT_GATE_015_V0_4_CONSUMED_SUCCESS_READOUT.md
13. docs/00_system/33_BT_GATE_015_V0_4_POSTEXECUTION_REVIEW_REQUEST.md
14. docs/00_system/34_BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE.md
15. runs/bt_gate_015_single_use_physical_event_state_consumer_v0_4/final_manifest.json
16. provider initial and completion handoff packages listed above
```

If any living surface contradicts this document, fail closed and reconcile
governance before preparing or executing a physical authorization.
