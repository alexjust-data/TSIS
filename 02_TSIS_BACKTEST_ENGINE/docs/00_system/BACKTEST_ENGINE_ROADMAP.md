## Current Authoritative State - BT-GATE-015 closed with restrictions

```text
BT-GATE-014 = CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-014_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
BT-GATE-014_V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_BT_GATE_014_V0.5 = PROHIBITED

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

BT-GATE-015_V0.4 = CONSUMED_FINAL
SECOND_EXECUTION_BT_GATE_015_V0.4 = PROHIBITED
BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW = PASS
PHYSICAL_COMMAND_V0.4 = EXECUTED_ONCE_PASS
EVENT_STATE_PHYSICAL_READ_V0.4 = EXECUTED_PASS
PHYSICAL_DATA_FILES_OPENED_V0.4 = 1
PHYSICAL_STATE_RECORDS_SCANNED_V0.4 = 8
PHYSICAL_STATE_ROWS_SELECTED_V0.4 = 1
EVENTS / STORE_INSERTS / OBSERVATIONS_V0.4 = 1 / 1 / 1
DELIVERY_BEFORE_AVAILABLE_AT_V0.4 = 0
DETERMINISTIC_OUTPUT_HASH_V0.4 = 35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a
POSTEXECUTION_PACKAGE_SHA256 = 62f1503694c9a3d9153179289b37bc4809d660315a0779cb8a30a52f367e0870
BT-GATE-015_CLOSED_PASS = CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS

BT-GATE-016 = NOT_OPEN
BT-GATE-016_IMPLEMENTATION = NOT_AUTHORIZED
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

# Backtest Engine Roadmap

Status: LIVE_ROADMAP
Last updated: 2026-07-30

## Propósito

Definir la secuencia vigente de capacidades después de `BT-GATE-010` sin
fragmentar el desarrollo en microgates.

## Historical Gate Snapshot - SUPERSEDED BY CURRENT BT-GATE-014

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED

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
```

`BT-GATE-012` and `BT-GATE-013` were closed and accepted at this historical snapshot. The current gate is BT-GATE-014 as declared at the top. StateReplayFeed, Market State, Event State, StateBundle reads, provider integration, the full 2005-2026 backtest, optimization and edge claims remain closed.

## Macrogates Vigentes

```text
BT-GATE-011
SINGLE_STRATEGY_END_TO_END_BACKTEST
```

Incluye:

- StrategySpec reproducible.
- Primera estrategia fija y deliberadamente simple.
- Integración EventLoop -> Execution -> Accounting.
- Deterministic Fill Simulator.
- Trade Ledger.
- Métricas mínimas.
- Unified Run Manifest.
- Primer run histórico end-to-end.

Etiqueta obligatoria de los primeros runs:

```text
ENGINE_VALIDATION_RUN
NOT_EDGE_EVIDENCE
NOT_ECONOMICALLY_REALISTIC
```

```text
BT-GATE-012
MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
```

Incluye:

- Múltiples símbolos.
- Múltiples sesiones.
- Orden temporal global determinista.
- Cash y posiciones compartidos.
- Concurrencia de órdenes.
- Cierre de sesión.
- Portfolio equity curve.

```text
BT-GATE-013
PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
```

Incluye:

- Filas fisicas `013_ohlcv_1m_quote_guarded` hacia `ReplayBarEvent` / `ReplayGapEvent`.
- Binding exacto de schema fisico y timestamp.
- Disponibilidad legal `available_at = bar_end`.
- Linaje reproducible fila a evento.
- Rutas relativas portables y hashes de inputs.
- Gaps como `UNKNOWN_SOURCE_GAP`, sin forward-fill ni inferencia de halts.
- Ejecucion con el motor aceptado de `BT-GATE-012`, sin cambiar fills, costes ni accounting.

No incluye halts, SSR, borrow/locates, liquidez/capacidad, batch research, DSR/PBO/CSCV ni edge evidence.

## Regla De Agrupación

Los antiguos incrementos candidatos `BT-GATE-011` a `BT-GATE-017` no deben
recrearse automáticamente como gates independientes. Deben agruparse en las
tres capacidades anteriores salvo que exista una dependencia o frontera material
que exija separarlos.

## Fronteras Cerradas

```text
StateReplayFeed = NOT_AUTHORIZED
Market State consumption = NOT_AUTHORIZED
Event State consumption = NOT_AUTHORIZED
state_bundle_physical_read = BLOCKED
```

## 2026-07-29 | BT-GATE-011 single-strategy end-to-end implementation

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
run_id = bt_gate_011_open_short_close_qg5_v0_1
validation_status = PASS
engine_suite = 99 tests OK
FINAL_OWNER_REVIEW = ACCEPTED
```

Implemented path:

```text
StrategySpec -> HistoricalReplayFeed -> point-in-time decisions -> ExecutionOrder -> DeterministicFillSimulator V0.1 -> accounting -> Trade Ledger -> equity curve -> Unified Run Manifest
```

The run remains `ENGINE_VALIDATION_RUN`, `EDGE_EVIDENCE = NOT_AUTHORIZED`, `ECONOMIC_REALISM = INCOMPLETE`.

## 2026-07-29 | BT-GATE-011 corrective acceptance evidence

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
EVENT_LOOP_INTEGRATION = PROVEN_BY_ONLINE_REPLAY_COORDINATOR_V0_1
PACKAGE_TEST_REPRODUCIBILITY = PASS
END_TO_END_RUN_REPRODUCIBILITY = PASS_WITH_PORTABLE_QG5_FIXTURE
engine_suite = 99 tests OK
```

The gate is closed after final owner acceptance review.

## 2026-07-29 | BT-GATE-011 accepted and BT-GATE-012 contract draft opened

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
FINAL_OWNER_REVIEW = ACCEPTED

HISTORICAL_CURRENT_GATE_AT_TIME = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
```

Contract draft:

```text
docs/00_system/12_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_CONTRACT_V0_1.md
```

## Historical Snapshot - 2026-07-29 | BT-GATE-013 boundary corrected

```text
BT-GATE-013_NAME = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_ENGINE
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER = FUTURE_GATE_FAMILY_NOT_YET_OPEN
```

Rationale: BT-GATE-013 must cross exactly one new boundary after BT-GATE-012: from accepted portable fixture replay to reproducible physical historical data. It must prove physical row lineage, timestamp availability, session legality, replay determinism and accounting preservation before any small-caps tradability, SSR, borrow, locates, liquidity/capacity, batch research, DSR/PBO/CSCV or edge-evidence gates are opened.

Central rule preserved for future gates:

```text
mechanically executable order != actually shortable security != economically valid trade != demonstrated edge
```

The next work is contract definition only:

```text
docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
Status = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
Implementation = NOT_AUTHORIZED
```

## Historical Snapshot - 2026-07-29 | BT-GATE-013 contract corrected after read-only review

```text
READ_ONLY_REVIEW = ACCEPTED
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PROVIDER_EVIDENCE_REQUIRED = false
ACCEPTANCE_SLICE = ABAT, ABEO, ABSI, ABTC, ACB / 2026-01-05, 2026-01-06
```

The corrected scope keeps `SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER` as a future gate family.



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
