## Current Authoritative State - V0.4 Physical Result

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

## Current Authoritative State - 2026-07-30

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

# Guia TSIS Para Sistemas Profesionales De Trading

Estado: GUIA_VIVA
Alcance: primero el backtest engine, despues la guia.

Esta carpeta es la guia de trabajo del backtest engine de TSIS. Esta organizada por capas de infraestructura, no por capitulos de libros ni por practicas de Sersan.

La guia no debe terminarse antes de programar. Cada documento se abre cuando esa capa sea necesaria para el vertical slice.

## Menu

- [1. Regla](#1-regla)
- [2. Documentos Por Capa](#2-documentos-por-capa)
- [3. Como Se Escribe Cada Capa](#3-como-se-escribe-cada-capa)
- [4. Estados De Madurez](#4-estados-de-madurez)
- [5. Prioridad Actual](#5-prioridad-actual)
- [6. Handoff Para Agentes](#6-handoff-para-agentes)

## 1. Regla

```text
Necesidad concreta del backtester
  -> leer contratos TSIS
  -> leer Sersan
  -> leer libros procesados
  -> tomar una decision TSIS pequena
  -> definir contrato/gate
  -> implementar o preparar implementacion
  -> actualizar AGENTS.md, guia, registros y changelog
```

Esto evita dos errores:

```text
escribir un manual gigante antes de que exista el motor
programar un motor sin dejar rastro de por que se tomo cada decision
```

## 2. Documentos Por Capa

| Orden | Archivo | Proposito | Estado |
|---:|---|---|---|
| 01 | `01_DATA.md` | Contratos de datos, universo, vistas de precio, sesiones y legalidad temporal | `VALIDADO_ACOTADO` |
| 02 | `02_REPLAY.md` | Replay historico, reloj, cola de eventos y politica de timestamps iguales | `VALIDADO_ACOTADO` |
| 03 | `03_MECHANICAL_TRADE_PATH.md` | Recorrido mecanico decision, order intent, order, fill, posicion y PnL bruto | `VALIDADO_ACOTADO` |
| 04 | `04_STATE.md` | Futuro consumo de estado observable | `NOT_AUTHORIZED` |
| 05 | `05_DECISION.md` | Strategy spec, setup, senal, decision y order intent | `NO_INICIADO` |
| 06 | `06_RISK_SIZING.md` | Position sizing, riesgo pre-trade y limites de exposicion | `NO_INICIADO` |
| 07 | `07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md` | Semántica de órdenes, fills, costes y slippage | `CORRECTED_DRAFT_READY_FOR_REVIEW` |
| 08 | `08_ACCOUNTING.md` | Fill ledger, posiciones, cash, PnL, equity y trades cerrados | `VALIDADO_ACOTADO` |
| 09 | `09_REPORTING.md` | Metricas, lista de trades, diagnosticos, limitaciones e informes | `NO_INICIADO` |
| 10 | `10_VALIDATION.md` | Tests anti-leakage, determinismo, walk-forward y robustez | `NO_INICIADO` |
| 11 | `11_OPERATIONS.md` | Paridad replay/live, paper trading, monitorizacion y retirada | `NO_INICIADO` |

`01_DATA.md`, `02_REPLAY.md`, `03_MECHANICAL_TRADE_PATH.md` y `08_ACCOUNTING.md` existen porque ya tienen evidencia acotada sobre fixture real.

## 3. Como Se Escribe Cada Capa

Cada capa debe contener:

```text
proposito
fuentes consultadas
que implican las fuentes
decision TSIS para v0.1
contratos minimos
outputs
gates de aceptacion
que queda explicitamente fuera por ahora
siguiente paso de implementacion
preguntas abiertas
```

## 4. Estados De Madurez

```text
SOURCE_KNOWLEDGE
  observado en Sersan o en la literatura.

TSIS_DECISION_PENDING
  util, pero todavia no implementado ni probado en TSIS.

TSIS_CONTRACT_DEFINED
  contrato o gate escrito; implementacion todavia incompleta.

TSIS_VALIDATED_CONTRACT
  implementado y respaldado por tests o evidencia reproducible.
```

## 5. Prioridad Actual

Prioridad actual:

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
CURRENT_GATE = BT-GATE-014 / POINT_IN_TIME_MARKET_STATE_CONSUMER
BT-GATE-014_PHASE_B_EXTERNAL_RE_REVIEW = PASS
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_1 =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_2 =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3 = AUTHORIZED_NOT_CONSUMED
PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED

No ejecutar todavía backtest completo 2005-2026.
StateReplayFeed, Event State, consumo amplio de Market State y modificaciones del provider permanecen NOT_AUTHORIZED.
```
## 6. Handoff Para Agentes

Antes de modificar una capa, el agente debe leer:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/AGENTS.md
```

Cada paso cerrado debe actualizar:

```text
AGENTS.md
CHANGELOG.md
el documento de capa afectado
los registros de governance aplicables
```



