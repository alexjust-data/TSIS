# TSIS Backtest Engine — Authority Root

Status: `INTEGRATED_GOVERNANCE_BASELINE_V0_1_1`
Effective date: 2026-07-29

This directory is the architectural and governance authority for:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

It does not contain the engine implementation. It records why the engine is built as it is, which policies are binding, which gates are closed, what evidence supports them, and what remains unauthorized or unproven.

## Current authoritative state

```text
DATA_PREFLIGHT = CLOSED_PASS
HISTORICAL_REPLAY_MINIMUM = CLOSED_PASS
MECHANICAL_TRADE_PATH = CLOSED_PASS
ACCOUNTING_MINIMUM = CLOSED_PASS
EXECUTION_SEMANTICS_CONTRACT = CLOSED_PASS
DETERMINISTIC_FILL_SIMULATOR = IMPLEMENTED_AND_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED

BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
CURRENT_GATE = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
EXECUTION_MODE = CLOSED_ACCEPTED
NO_INTERMEDIATE_MICROGATES = PRESERVED
NEXT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1_CONTRACT_DRAFT_PENDING_OWNER_REVIEW

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

