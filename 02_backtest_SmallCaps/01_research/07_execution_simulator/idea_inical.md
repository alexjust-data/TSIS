Aquí es donde mueren el 90% de backtests de microcaps.

Porque:

```sh
spread
liquidity vacuum
halts
SSR
slippage
partial fills
```

destruyen completamente los resultados.

Tu documento insiste correctamente en esto.



Yo haría 3 simuladores:

A) Simulador ingenuo

Fill perfecto.

Solo sirve para:

¿existe edge teórico?
B) Simulador realista

Con:

bid/ask
spread
slippage dinámico
participación máxima del volumen

Aquí empiezas a acercarte a realidad.

C) Simulador microestructural

Con:

quotes
trades
queue depletion
liquidity shocks
halts
execution delay

Este ya es nivel serio.


---

# 07_execution_simulator

## Objetivo

Simular ejecución realista de órdenes.

---

# Problema

Muchos backtests son irreales porque ignoran:

- spread
- slippage
- liquidity
- halts
- partial fills

---

# Inputs

- quotes
- trades
- signals
- market state

---

# Simula

- fills
- slippage
- queue priority
- execution delay
- stop execution
- halts

---

# Outputs

## executed_trades.parquet

Trades realmente simulados.

---

# Filosofía

Aquí el sistema se enfrenta a:

la realidad microestructural del mercado.