# Testing and Tuning Market Trading Systems - Source Map

## Menu

- [Lectura por tarea](#lectura-por-tarea)
- [Trazabilidad por paginas](#trazabilidad-por-paginas)
- [Como citar en tareas TSIS](#como-citar-en-tareas-tsis)

## Lectura por tarea

| Tarea TSIS | Leer | Motivo |
|---|---:|---|
| Auditar indicadores antes de optimizar | 21-45 | Stationarity/entropy |
| Disenar optimizador | 46-110 | Regularizacion y differential evolution |
| Estimar bias de entrenamiento | 115-121 | `StocBias` y OOS logic |
| Definir walkforward correcto | 153-176 | IS/OOS, selection bias, lookahead, buffers |
| Decidir granularidad de retornos | 235-240 | Bar-by-bar vs completed trades |
| Reportar bounds estadisticos | 254-283 | Lower bounds y bootstrap |
| Estimar drawdown futuro | 286-337 | Drawdown bounds |
| Implementar permutation testing | 338-360 | p-values y selection-bias-aware tests |

## Trazabilidad Por Paginas

| Paginas | Contenido | Nota TSIS |
|---:|---|---|
| 12-16 | Alcance y advertencias | Testing avanzado, no libro de motor |
| 21-24 | Stationarity | Feature QA |
| 46-48 | Overfitting y regularizacion | Model complexity |
| 153-161 | Training/selection bias | Research governance |
| 168-176 | Walkforward blunders | Temporal integrity |
| 235-240 | Trade analysis | Ledger granularity |
| 338-360 | Permutation tests | Robust validation |

## Como citar en tareas TSIS

Usar como fuente primaria para:

```text
validacion, bias, walkforward, bootstrap, permutation tests y retorno bar-by-bar
```

No usar como fuente principal para:

```text
event loop, OMS, broker adapter o execution simulator
```
