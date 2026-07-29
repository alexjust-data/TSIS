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
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
CURRENT_GATE = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED

No ejecutar todavía backtest completo 2005-2026.
BT-GATE-012 fue aceptado como CLOSED_PASS_IMPLEMENTATION_ACCEPTED. No ejecutar todavia un backtest completo 2005-2026. StateReplayFeed, Market State, Event State y provider permanecen NOT_AUTHORIZED.
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



