# 08 ACCOUNTING

Estado: TSIS_VALIDATED_CONTRACT_ACOTADO
Fecha: 2026-07-28
Alcance: contabilidad minima gross-to-net para `BACKTEST_VERTICAL_SLICE_V0_1`.

Este documento no define costes broker realistas ni tradability short. Documenta el primer cierre contable reproducible desde un `TradeLedger` mecanico hasta cash, costes, PnL neto y equity final.

## 1. Proposito

Responder:

```text
Puede TSIS transformar fills mecanicos cerrados en cash ledger, costes declarados, PnL neto y equity final sin confundir cash con edge ni reclamar realismo de ejecucion?
```

## 2. Regla Ejecutable

Accounting solo consume el `TradeLedger` y el `MechanicalRunSummary` ya generados por la capa mecanica. No puede leer Parquet, no puede crear fills y no puede modificar el PnL bruto historico.

## 3. Decisiones TSIS V0.1

### ACCT-DEC-001: Costes por componentes

Los costes no se guardan como un total opaco. Cada fill produce un `CostBreakdown` con estas categorias:

```text
commission
routing_or_ecn_fee
regulatory_fee
locate_fee
borrow_fee
other_fee
```

En V0.1 varias categorias pueden ser cero, pero deben existir para que el contrato futuro no cambie de forma silenciosa.

### ACCT-DEC-002: Cash no es equity en posiciones short

El short aumenta cash al entrar, pero crea una posicion negativa. Por eso `AccountState` mantiene separados:

```text
cash
position_market_value
realized_gross_pnl
accrued_costs
realized_net_pnl
unrealized_pnl
equity
```

La version minima exige posicion final cerrada.

### ACCT-DEC-003: No hay reclamo de realismo

El modelo actual es determinista y contractual:

```text
broker_cost_realism_claimed = false
fill_realism_claimed = false
short_tradability_evaluated = false
edge_evaluated = false
```

## 4. Contratos Minimos

Implementacion:

```text
src/tsis_backtest/accounting/contracts.py
src/tsis_backtest/accounting/engine.py
```

Contratos:

```text
CostComponent
CostBreakdown
CostModel
CashLedgerEntry
AccountState
AccountingRunSummary
AccountingRunResult
AccountingEngine
```

## 5. Gates Probados

```text
ACCT_G1_ZERO_COSTS_NET_EQUALS_GROSS
ACCT_G2_COMMISSION_PER_SHARE_BOTH_ORDERS
ACCT_G3_MINIMUM_COMMISSION_PER_ORDER
ACCT_G4_MULTIPLE_COMPONENTS_SEPARATE_AND_SUMMED
ACCT_G5_SHORT_LOSER_NET_PNL
ACCT_G6_OPEN_POSITION_NOT_CLOSEABLE
ACCT_G7_GROSS_MISMATCH_REPORTED
ACCT_G8_DETERMINISTIC_ACCOUNTING_HASH
ACCT_G9_REAL_ABAT_ACCOUNTING_SMOKE
```

## 6. Evidencia

Suite:

```text
$env:PYTHONPATH='src'; python -m unittest discover -s tests
# Ran 61 tests OK
```

Smoke real ABAT:

```text
run_id = accounting_abat_short_open_close_v0_1
ticker = ABAT
quantity = 100
starting_equity = 10000.00
entry_price = 3.87
exit_price = 4.665
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
ending_equity = 9918.50
final_position_quantity = 0
cash_ledger_entry_count = 4
cost_component_count = 12
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/accounting_manifest.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/accounting_run_summary.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/cost_breakdowns.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/cash_ledger.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/account_state.json
```

## 7. Fuera De Alcance

```text
broker-cost realism
bid/ask spread
slippage realista
partial fills
liquidity/capacity
locate availability
locate price real
borrow rate real
halts
forced buy-ins
portfolio multi-simbolo
strategy edge
full 2005-2026 backtest
```

## 8. Estado posterior

`HISTORICAL_SNAPSHOT`: el siguiente menú fue válido al cerrar Accounting,
pero la opción B ya se ejecutó documentalmente:

```text
elegir el proximo aumento pequeno del vertical slice:
  opcion A: mismo circuito con varios simbolos del fixture acotado
  opcion B: primer contrato de execution semantics/cost realism
  opcion C: run manifest unico que encadene preflight -> replay -> mechanics -> accounting
```

Estado vivo actual:

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
CURRENT_GATE = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
```

BT-GATE-012 fue aceptado como CLOSED_PASS_IMPLEMENTATION_ACCEPTED. No ejecutar todavia un backtest completo 2005-2026. StateReplayFeed, Market State, Event State y provider permanecen NOT_AUTHORIZED.

