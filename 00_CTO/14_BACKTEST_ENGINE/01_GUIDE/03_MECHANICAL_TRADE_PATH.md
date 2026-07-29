# 03 MECHANICAL TRADE PATH

Estado: TSIS_VALIDATED_CONTRACT_ACOTADO
Fecha: 2026-07-28
Alcance: primer recorrido mecanico `Decision/Order/Fill/Position` para `BACKTEST_VERTICAL_SLICE_V0_1`.

Este documento no define una estrategia real ni un modelo de fills realista. Documenta el primer circuito mecanico cerrado desde eventos de replay hasta ledger y PnL bruto.

## 1. Proposito

Responder:

```text
Puede TSIS convertir eventos historicos aprobados en decisiones programadas, ordenes, fills, posicion final y PnL bruto sin mezclar tiempos ni afirmar realismo?
```

## 2. Regla Ejecutable

El recorrido mecanico solo puede consumir eventos de `HistoricalReplayFeed`. No puede leer Parquet directamente ni saltarse `RunPreflight`.

## 3. Decisiones TSIS V0.1

### MECH-DEC-001: Decision programada antes del proxy

La decision de entrada/salida debe existir antes del timestamp de ejecucion proxy.

Para apertura:

```text
execution_timestamp = ts_start de la primera barra
recorded_at = available_at de la primera barra
execution_price = open
```

Para cierre:

```text
execution_timestamp = ts_end de la ultima barra
recorded_at = available_at de la ultima barra
execution_price = close
```

### MECH-DEC-002: Fill proxy mecanico

Los fills generados son:

```text
fill_model = MECHANICAL_PROXY_FILL
execution_realism_claimed = false
edge_evaluated = false
```

### MECH-DEC-003: Posicion y PnL derivan de fills

No se calcula PnL desde precios sueltos. El ledger de fills genera posicion final y PnL bruto.

## 4. Contratos Minimos

Implementacion:

```text
src/tsis_backtest/mechanics/contracts.py
src/tsis_backtest/mechanics/event_loop.py
```

Contratos:

```text
ScheduledDecision
OrderIntent
Order
Fill
Position
TradeLedger
MechanicalRunSummary
MechanicalEventLoop
```

## 5. Gates Probados

```text
MECH_G1_DECISION_BEFORE_EXECUTION
MECH_G2_OPEN_PROXY_SHORT_FILL
MECH_G3_CLOSE_PROXY_COVER_FILL
MECH_G4_POSITION_FROM_FILLS
MECH_G5_GROSS_PNL_FROM_FILLS
MECH_G6_LINEAR_REFERENCE_MATCH
MECH_G7_NO_FILL_REALISM_CLAIM
MECH_G8_NO_EDGE_EVALUATION
MECH_G9_REAL_ABAT_FIXTURE_SMOKE
```

## 6. Evidencia

Suite:

```text
$env:PYTHONPATH='src'; python -m unittest discover -s tests
# Ran 51 tests OK
```

Smoke real ABAT:

```text
run_id = mechanical_abat_short_open_close_v0_1
ticker = ABAT
quantity = 100
entry_price = 3.87
exit_price = 4.665
gross_pnl = -79.5
linear_reference_gross_pnl = -79.5
final_position_quantity = 0
execution_realism_claimed = false
edge_evaluated = false
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/mechanical_abat_short_open_close_v0_1/mechanical_run_summary.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/mechanical_abat_short_open_close_v0_1/trade_ledger.json
```

## 7. Fuera De Alcance

```text
fill realism
slippage realista
costes netos propios de accounting
borrow/locates
portfolio
strategy edge
full 2005-2026 backtest
```

## 8. Siguiente Paso

El siguiente incremento recomendado ya fue ejecutado en:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/08_ACCOUNTING.md
```
