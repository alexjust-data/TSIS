# Quantum Finance - Source Map

## Menu

- [Lectura por tarea](#lectura-por-tarea)
- [Trazabilidad por paginas](#trazabilidad-por-paginas)
- [Como citar en tareas TSIS](#como-citar-en-tareas-tsis)

## Lectura por tarea

| Tarea TSIS | Leer | Motivo |
|---|---:|---|
| Disenar feature tipo S/R cuantitativo | 116-140 | QPL y computacion numerica |
| Clasificar familias de setups | 146-181 | Trend, breakout, reversal, channel, stops, hedge |
| Explorar GA/fuzzy/neural | 186-230 | AI tools y genetic/fuzzy modules |
| Traducir MQL a Python | 300-319, 331-349 | Flujo de lectura, calculo, forecast y escritura |
| Estudiar forecast batch multi-producto | 325-353 | TSCNON architecture/results |
| Estudiar futuro RL | 398-417 | Forecaster/trader/critic y rewards |

## Trazabilidad por paginas

| Paginas | Contenido | Nota TSIS |
|---:|---|---|
| 42-44 | Modelo por capas | Convertir a arquitectura experimental, no core |
| 146-181 | Catalogo de estrategias | Alimenta `StrategyPatternLibrary` |
| 207-213 | GA | Requiere control de sobreoptimizacion |
| 300-319 | QPL MQL | Pipeline programatico util para traduccion |
| 325-353 | TSCNON | Forecast batch, rankings y performance por producto |
| 398-417 | Multiagent RL trader | Separar forecaster, policy y critic |

## Como citar en tareas TSIS

Usar como:

```text
Fuente de modelo experimental / feature engineering / futura RL policy
```

No usar como:

```text
Fuente principal de backtesting, execution simulator o validacion estadistica
```
