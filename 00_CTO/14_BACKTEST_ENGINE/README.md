## Current Authoritative State - BT-GATE-014 final closure

```text
BT-GATE-014 = CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-014_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_V0.5 = PROHIBITED
physical files / rows / events / inserts / observations = 1 / 2 / 2 / 2 / 2
early delivered / orders / fills / PnL = 0 / 0 / 0 / false
deterministic_output_hash = 6331839dfc6538f7dd6fda9a1fd7efbc7497d541dcb0c0d89cfd679762067cb1
BT-GATE-015 = NOT_OPEN
BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED
Event State = NOT_AUTHORIZED
```

Mandatory restart handoff:
`docs/00_system/CURRENT_PROJECT_HANDOFF.md`

All subsequent status blocks are historical snapshots and are superseded by
this block.
## Historical Snapshot - Superseded - Current Authoritative State - BT-GATE-014 V0.5

```text
BT-GATE-014 = OPEN_PENDING_V0_5_EXTERNAL_PREEXECUTION_REVIEW
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3/V0.4 = PROHIBITED
RESTRICTION_DOMAIN_BINDING = ADOPTED
V0.5 = AUTHORIZED_NOT_CONSUMED
PHYSICAL_COMMAND_V0.5 = NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
PHYSICAL_READ_V0.5 = NOT_EXECUTED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
Event State = NOT_OPEN
```

The provider/shared-boundary clarification separates physical provenance,
bounded replay-consumption and component replay restriction domains. V0.5 may
be executed once only after an independent pre-execution PASS.

## Historical Snapshot - Superseded - Current Authoritative State - V0.4 Physical Result

```text
BT-GATE-014 = OPEN_CONTRACT_CORRECTION_REQUIRED
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
PHYSICAL_READ_V0.4 = EXECUTED_FAILED / 1 FILE / 2 ROWS / 0 EVENTS
SECOND_EXECUTION_V0.4 = PROHIBITED
NEW_SINGLE_USE_AUTHORIZATION = NOT_AUTHORIZED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

Physical rows carry design/provenance restrictions while the sidecar and components carry bounded-consumption restrictions. The current contract incorrectly requires these distinct domains to be identical. Older current-state blocks below are HISTORICAL / SUPERSEDED.

## Historical Snapshot - Superseded - Current Authoritative State - 2026-07-30

```text
BT-GATE-014 = OPEN_CORRECTION_REQUIRED
V0.3 = CONSUMED_FAILED_FINAL
PHYSICAL_READ_V0.3 = EXECUTED_FAILED / 1 FILE / 2 ROWS / 0 EVENTS
SECOND_EXECUTION_V0.3 = PROHIBITED
V0.4 = AUTHORIZED_NOT_CONSUMED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
PHYSICAL_COMMAND_V0.4 = NOT_APPROVED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

All older current-state blocks below are HISTORICAL / SUPERSEDED.

## Historical Snapshot - Superseded - Current Gate - BT-GATE-014

```text
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
BT-GATE-014 = SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3_ISSUED_NOT_CONSUMED
BT-GATE-014_CONSUMER_CONTRACT = IMPLEMENTED
PHASE_B_NON_PHYSICAL_IMPLEMENTATION = ACCEPTED
BT-GATE-014_PHASE_B_EXTERNAL_RE_REVIEW = PASS
SYNTHETIC_CONSUMER_TESTS = PASS
PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
PHYSICAL_CONSUMER_EVIDENCE = NOT_YET_PRODUCED
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_1 = SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_2 = SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3 = AUTHORIZED_NOT_CONSUMED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
Event State = NOT_OPEN
```

# TSIS Backtest Engine — Authority Root

Status: `INTEGRATED_GOVERNANCE_BASELINE_V0_1_1`
Effective date: 2026-07-29

This directory is the architectural and governance authority for:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

It does not contain the engine implementation. It records why the engine is built as it is, which policies are binding, which gates are closed, what evidence supports them, and what remains unauthorized or unproven.

## Historical Authoritative State - SUPERSEDED BY CURRENT BT-GATE-014

```text
DATA_PREFLIGHT = CLOSED_PASS
HISTORICAL_REPLAY_MINIMUM = CLOSED_PASS
MECHANICAL_TRADE_PATH = CLOSED_PASS
ACCOUNTING_MINIMUM = CLOSED_PASS
EXECUTION_SEMANTICS_CONTRACT = CLOSED_PASS
DETERMINISTIC_FILL_SIMULATOR = IMPLEMENTED_AND_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED

BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

LAST_CLOSED_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
BT-GATE-013_CONTRACT = CONTRACT_ACCEPTED
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
PHYSICAL_RUN = AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED
CURRENT_GATE = NONE
NEXT_GATE = NOT_OPEN
CODE_IMPLEMENTATION = NOT_AUTHORIZED_OUTSIDE_CLOSED_BT_GATE_013_SCOPE

BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
BROKER_COST_REALISM = NOT_CLAIMED
FILL_REALISM_BEYOND_V0_1 = NOT_CLAIMED
SHORT_TRADABILITY = NOT_EVALUATED
EDGE = NOT_EVALUATED
PRODUCTION = false
DOWNSTREAM = false
```

## Navigation

- `GOVERNANCE_README.md`: inspection and maintenance protocol.
- `01_GUIDE/`: system status and inspector guide.
- `02_ARCHITECTURE/`: authority/evidence boundary and component map.
- `03_CONTRACTS/`: contract inventory and lifecycle.
- `04_DECISIONS/DECISION_LEDGER.json`: normalized decisions and rationale.
- `05_POLICIES/POLICY_REGISTER.json`: binding and proposed policies.
- `06_TRACEABILITY/TRACEABILITY_MATRIX.json`: policy/decision → implementation → test → run.
- `07_EXCEPTIONS/EXCEPTION_AND_WAIVER_REGISTER.json`: contradictions, limitations, waivers and debt.
- `08_GATES_AND_REVIEWS/GATE_REGISTER.json`: authorization history and next gate.
- `09_SCHEMAS/GOVERNANCE_SCHEMA.json`: machine-readable validation schema.
- `10_VALIDATION/GOVERNANCE_VALIDATION_REPORT.md`: baseline audit result.
- `11_HISTORICAL_SNAPSHOTS/`: preserved pre-governance roots, explicitly non-authoritative.

## Applied Architecture context

Only these external documents may be consulted as general architectural context:

```text
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/AGENTS.md
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/README.md
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/CHANGELOG.md
```

The future provider boundary may be read, but not integrated as an active backtester capability:

```text
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/
03_TABLES_feature_engineering/
09_STATE_CONSUMPTION_BOUNDARY/README.md
```

These references do not authorize `Market State`, `Event State`, `StateReplayFeed`,
physical StateBundle reads, or backtest execution with states. They do not replace
the local contracts of `02_TSIS_BACKTEST_ENGINE`.

## Authority rule

When this directory and the implementation tree disagree:

1. execution evidence remains factual evidence of what ran;
2. this directory controls what is authorized or claimed;
3. the conflict must be entered in the exception register;
4. no new dependent gate may close until the conflict is resolved or explicitly waived.

## Historical Execution Contract Gate Superseded

BT-GATE-006 = CLOSED_PASS
EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1 = CLOSED_REVIEWED_READY_FOR_BOUNDED_IMPLEMENTATION_AUTHORIZATION
NEXT_GATE = DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION / OPEN_FOR_DECISION
CODE_IMPLEMENTATION = NOT_AUTHORIZED

## Historical Deterministic Fill Simulator Gate Superseded

BT-GATE-009 = CLOSED_PASS_AUTHORIZATION_GRANTED
CODE_IMPLEMENTATION = AUTHORIZED_FOR_DETERMINISTIC_FILL_SIMULATOR_V0_1_ONLY
NEXT_GATE = BT-GATE-010 / DETERMINISTIC_FILL_SIMULATOR_V0_1_IMPLEMENTATION_AND_ACCEPTANCE

Historical note: BT-GATE-010 later closed as implementation accepted.

## 2026-07-29 | Historical BT-GATE-011 Implementation Awaiting Final Acceptance Review

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
run_id = bt_gate_011_open_short_close_qg5_v0_1
validation_status = PASS
HISTORICAL_ENGINE_SUITE_AT_TIME_OF_ENTRY = 95 tests OK
FINAL_ACCEPTED_ENGINE_SUITE = 99 tests OK
HISTORICAL_FINAL_OWNER_REVIEW_STATE = AWAITING_REVIEW_AT_TIME_OF_ENTRY_SUPERSEDED_BY_ACCEPTED
```

The run validates the engine path only:

```text
RUN_PURPOSE = ENGINE_VALIDATION_RUN
EDGE_EVIDENCE = NOT_AUTHORIZED
ECONOMIC_REALISM = INCOMPLETE
```

State Provider, Market State, Event State and StateReplayFeed restrictions remain closed.

## 2026-07-29 | Historical BT-GATE-013 corrected contract state superseded

```text
READ_ONLY_REVIEW = ACCEPTED
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = CONTRACT_ACCEPTED
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
PHYSICAL_RUN = AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED
PROVIDER_EVIDENCE_REQUIRED = false
```

The corrected contract addresses source identity layering, exact physical binding,
derived time fields, source row locator, portable relative paths and repair-field
restriction. It does not authorize StateReplayFeed, Market State, Event State,
provider modification, physical execution or full 2005-2026 backtest.



## 2026-07-29 | BT-GATE-013 implementation evidence prepared

```text
BT-GATE-013 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
PHYSICAL_RUN = AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED
IMPLEMENTATION_ACCEPTANCE = PENDING_FINAL_EXTERNAL_REVIEW
ENGINE_TEST_SUITE = 119 tests PASS
BT-GATE-013_FOCUSED_TESTS = 13 physical replay tests PASS
BT-GATE-013_VALIDATION_STATUS = PASS
BT-GATE-013_DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
RUN_ID = bt_gate_013_physical_historical_replay_slice_v0_1
```

This is implementation evidence only. Do not record `BT-GATE-013 = CLOSED_PASS` until the final acceptance packet is externally reviewed. StateReplayFeed, Market State, Event State, StateBundle reads, provider modification, full 2005-2026 backtest, optimization and edge claims remain not authorized.

## 2026-07-30 | BT-GATE-013 corrected acceptance evidence regenerated

```text
BT-GATE-013 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
IMPLEMENTATION_ACCEPTANCE = PENDING_FINAL_EXTERNAL_REVIEW
ENGINE_TEST_SUITE = 119 tests PASS
BT-GATE-013_FOCUSED_TESTS = 13 physical replay tests PASS
NEGATIVE_DERIVATIVES = 15 executed cases PASS
AUTHORIZED_SOURCE_IDENTITY_VALIDATION = PASS
FINAL_MANIFEST_REQUIRED_FIELDS = PASS
BT-GATE-013_DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
```

This supersedes the rejected BT-GATE-013 acceptance packet identity `42421cbe0668c458b4559eadf0aad44f2ec8f00a64956622920a384586c1fe1d`. The gate remains open until the corrected final acceptance packet is externally reviewed. StateReplayFeed, Market State, Event State, StateBundle reads, provider modification, full 2005-2026 backtest, optimization and edge claims remain not authorized.
