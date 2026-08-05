# TSIS Backtest Engine - Current Project Handoff

Status: `LIVE_RESTART_AUTHORITY`
As of: `2026-08-05`

This document is the canonical cold-start entry for the Backtest Engine. Read
it before changing code, governance, authorizations or physical inputs. It
summarizes the current state; accepted contracts, evidence packages and
machine-readable registers remain the underlying authorities.

## Current Authoritative State

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
BT-GATE-014 = CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS

BT-GATE-015 = NON_PHYSICAL_IMPLEMENTATION_ACCEPTED_PENDING_SINGLE_USE_PHYSICAL_AUTHORIZATION
BT-GATE-015_CONTRACT = OWNER_REVIEW_PASS
BT-GATE-015_IMPLEMENTATION = ACCEPTED_NON_PHYSICAL_ONLY
BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW = PASS
IMPLEMENTATION_ACCEPTANCE = ACCEPTED_NON_PHYSICAL_ONLY

EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED
SINGLE_USE_PHYSICAL_AUTHORIZATION = NOT_AUTHORIZED
PHYSICAL_STATE_ROWS_READ_BY_BACKTESTER = 0
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED
```

## Last Accepted Capability

BT-GATE-014 is closed. Its bounded Market State execution consumed V0.5 once
and produced:

```text
physical files / rows / events / inserts / observations = 1 / 2 / 2 / 2 / 2
early deliveries / orders / fills / PnL = 0 / 0 / 0 / false
deterministic_output_hash = 6331839dfc6538f7dd6fda9a1fd7efbc7497d541dcb0c0d89cfd679762067cb1
V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_V0.5 = PROHIBITED
```

Do not reopen or reuse any BT-GATE-014 single-use authorization.

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

## Frozen Future Physical Slice

Any future single-use authorization must remain limited to:

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
maximum physical rows = 1
```

## Next Required Work

The next increment belongs to the backtester:

```text
1. Prepare one machine-readable single-use authorization candidate.
2. Bind its document, state, configuration, runner and all governed inputs.
3. Prove fail-closed behavior without opening Event State physical data.
4. Produce a self-contained pre-execution review package.
5. Obtain an independent PREEXECUTION PASS.
6. Only then execute the exact physical command once.
7. Audit the post-execution evidence.
8. Close BT-GATE-015 only after post-execution acceptance.
```

Existing local V0.1 and V0.2 authorization files are draft candidates only.
They are not executable authority and must not be consumed.

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
7. provider initial and completion handoff packages listed above
```

If any living surface contradicts this document, fail closed and reconcile
governance before preparing or executing a physical authorization.
