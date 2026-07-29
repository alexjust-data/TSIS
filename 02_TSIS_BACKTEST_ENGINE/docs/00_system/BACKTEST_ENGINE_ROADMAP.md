# Backtest Engine Roadmap

Status: LIVE_ROADMAP
Last updated: 2026-07-29

## Propósito

Definir la secuencia vigente de capacidades después de `BT-GATE-010` sin
fragmentar el desarrollo en microgates.

## Gate Actual

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED

CURRENT_GATE = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
EXECUTION_MODE = CLOSED_ACCEPTED
NO_INTERMEDIATE_MICROGATES = PRESERVED
NEXT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1_CONTRACT_DRAFT_PENDING_OWNER_REVIEW
```

`BT-GATE-012` has produced its implementation, tests, portable rerun and acceptance packet. Final implementation acceptance is still pending final owner/external review.

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

- Halts.
- SSR.
- Borrow/locates.
- Liquidez y capacidad.
- Batch control.
- Validación temporal.
- Control de múltiples pruebas.
- DSR y PBO/CSCV cuando resulten aplicables.

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

CURRENT_GATE = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
```

Contract draft:

```text
docs/00_system/12_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_CONTRACT_V0_1.md
```


## 2026-07-29 | BT-GATE-013 boundary corrected

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
Status = CONTRACT_DRAFT_PENDING_OWNER_REVIEW
Implementation = NOT_AUTHORIZED
```
