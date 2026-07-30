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

# AGENTS — Backtest Engine authority operating contract

Status: `ACTIVE`

## Scope

Authorized authority root:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE
```

Governed implementation root:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

## Mandatory behavior

Before changing the backtester, resolve the applicable `policy_id`, `decision_id`, contract and gate. Fail closed if the intended change has no authority.

Every completed increment must update, when applicable:

```text
DECISION_LEDGER.json
POLICY_REGISTER.json
TRACEABILITY_MATRIX.json
EXCEPTION_AND_WAIVER_REGISTER.json
GATE_REGISTER.json
CHANGELOG.md
```

No gate may be recorded as closed without:

- bounded scope;
- explicit authorization;
- implementation bindings;
- acceptance-test bindings;
- evidence-run bindings when physical behavior is claimed;
- limitations and non-claims;
- status consistency across living documents.

## Historical Gate Snapshot - SUPERSEDED BY BT-GATE-014

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

LAST_CLOSED_GATE =
BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1

BT-GATE-013 =
CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED

BT-GATE-013_CONTRACT =
CONTRACT_ACCEPTED

BT-GATE-013_IMPLEMENTATION =
IMPLEMENTED_AND_ACCEPTED

IMPLEMENTATION_ACCEPTANCE =
ACCEPTED

PHYSICAL_RUN =
AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED

CURRENT_GATE =
NONE

NEXT_GATE =
NOT_OPEN
```

This entire gate snapshot is historical and superseded by the BT-GATE-014 current-state block at the top. Historical BT-GATE-006, BT-GATE-009 and BT-GATE-010 sections are also superseded. They remain relevant as closed evidence, not as current gates.

## Frozen boundaries

Do not open through this authority increment:

```text
StateReplayFeed
Market State
Event State
state bundle physical reads
strategy state consumption
borrow or locate realism
broker realism
production
downstream
edge claims
```

Historical sections must be labeled `HISTORICAL_SNAPSHOT` or `SUPERSEDED`; they must not compete with the current-state block.

## Applied Architecture boundary

The root `AGENTS.md`, `README.md` and `CHANGELOG.md` of
`00_CTO_APPLIED_ARCHITECTURE` are context only. The
`09_STATE_CONSUMPTION_BOUNDARY/README.md` may be inspected only to maintain:

```text
FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_strategy_execution = false
state_bundle_physical_read = BLOCKED
```

Provider responsibilities are validation, resolution, construction/reuse and
StateBundle references. The Consumption Boundary would authorize a bounded
physical opening. A future consumer would read, type, order and replay under
its own contracts. None of those consumer actions is authorized now.

## Autoridad de mantenimiento

El agente del backtester está autorizado para mantener sincronizados los
registros de governance con evidencia verificable producida por
`02_TSIS_BACKTEST_ENGINE`.

Puede:

- registrar hechos demostrados;
- actualizar paths y referencias;
- añadir tests y runs como evidencia;
- corregir estados documentales obsoletos;
- abrir registros pendientes;
- marcar contradicciones;
- regenerar validaciones y manifests.

No puede, salvo instrucción explícita:

- autorizar una capacidad previamente NOT_AUTHORIZED;
- cerrar un gate que requiera revisión externa o aprobación humana;
- eliminar limitaciones sin evidencia;
- convertir una implementación en autoridad;
- activar consumo de Market State/Event State;
- autorizar StateReplayFeed o lectura física de StateBundles.

## 2026-07-29 | Historical BT-GATE-012 implementation acceptance evidence

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
ENGINE_TEST_SUITE = 106 tests OK
BT-GATE-012_VALIDATION_STATUS = PASS
BT-GATE-012_DETERMINISM_STATUS = PASS
BT-GATE-012_DETERMINISTIC_OUTPUT_HASH = 414aceb2bc80836f8fa821cd4d14071e54c86f3c7855c0a34c82ffd8b1c79182
NEXT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
```

BT-GATE-012 later closed as accepted. StateReplayFeed, Market State, Event State and provider integration remain closed.

## Historical Snapshot - 2026-07-29 | BT-GATE-013 boundary corrected

```text
BT-GATE-013_NAME = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_ENGINE
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER = FUTURE_GATE_FAMILY_NOT_YET_OPEN
```

`BT-GATE-013` is not a small-caps research runner. It is the physical historical replay bridge from `013_ohlcv_1m_quote_guarded` rows into the accepted replay/portfolio engine. Future small-caps rigorous research capability remains deferred until the physical bar boundary, Market/Event State consumption gates, scaling/batch gates, tradability/execution-realism gates and statistical validation gates are separately authorized.

## Historical Snapshot - 2026-07-29 | BT-GATE-013 contract draft placed in canonical backtester docs

```text
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = HISTORICAL_CONTRACT_DRAFT_PENDING_OWNER_REVIEW_SUPERSEDED_BY_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
CONTRACT_ARTIFACT = docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
```

The contract draft was copied into the canonical backtester document location. This does not authorize implementation, Market State consumption, Event State consumption, StateReplayFeed, provider modification or full 2005-2026 execution.

## Historical Snapshot - 2026-07-29 | BT-GATE-013 corrected contract pending final owner review

```text
READ_ONLY_REVIEW = ACCEPTED
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PROVIDER_EVIDENCE_REQUIRED = false
```

No implementation, physical run, StateReplayFeed, Market State, Event State or provider modification is authorized by this correction.



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
