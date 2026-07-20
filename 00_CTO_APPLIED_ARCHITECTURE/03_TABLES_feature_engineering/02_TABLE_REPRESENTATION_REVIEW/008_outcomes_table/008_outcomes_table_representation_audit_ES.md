# 008 outcomes_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Respuesta futura usada como label/evaluacion.
```

## Familias Relevantes

### Eventos / Outcomes

Fenomeno del mercado que representa:
```text
Lo que ocurre despues de un evento,
estado o ventana.
```

Hipotesis cientifica:
```text
Una representacion solo puede evaluarse midiendo su respuesta futura separada de los inputs.
```

Preguntas que permite responder:
```text
Que retorno futuro hubo?
Cual fue MFE/MAE?
Hubo break/failure?
Que horizonte se mide?
```

Variables minimas:
```text
outcome_id,
event_window_id,
horizon,
future_return,
MFE,
MAE,
break_flag,
failure_flag.
```

Tabla donde deben vivir:
```text
Deben vivir en 008 outcomes_table, nunca dentro de Market State o Event State observable.
```

Consumidores:
```text
Backtest,
ML como y/label,
RL como reward si hay contrato,
AlphaEvolve como objetivo de evaluacion.
```

### Liquidez / Ejecucion

Fenomeno del mercado que representa:
```text
Condiciones futuras que afectan si la respuesta era operable.
```

Hipotesis cientifica:
```text
Una prediccion no vale igual si el spread,
impacto o liquidez impiden ejecutarla.
```

Preguntas que permite responder:
```text
La respuesta futura era tradable?
Hubo spread/impacto adverso?
```

Variables minimas:
```text
future_spread,
future_liquidity,
price_impact,
response_latency.
```

Tabla donde deben vivir:
```text
008 para outcomes;
execution tables si se modela ejecucion real.
```

Consumidores:
```text
Execution research,
backtests,
RL y evaluacion de estrategias.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

