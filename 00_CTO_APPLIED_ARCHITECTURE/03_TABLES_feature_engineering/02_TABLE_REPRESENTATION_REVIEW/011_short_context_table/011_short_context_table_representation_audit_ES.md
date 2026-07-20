# 011 short_context_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Contexto short-side: short interest, short volume o borrow cuando exista.
```

## Familias Relevantes

### Participacion

Fenomeno del mercado que representa:
```text
Presion o participacion del lado short.
```

Hipotesis cientifica:
```text
La presion short puede condicionar squeezes,
reversions,
liquidez y respuesta a noticias/eventos.
```

Preguntas que permite responder:
```text
Hay short pressure?
Esta aumentando?
Es reciente o stale?
```

Variables minimas:
```text
short_interest,
short_volume,
short_ratio,
days_to_cover,
source_family,
source_scope.
```

Tabla donde deben vivir:
```text
Deben vivir en 011 short_context_table.
```

Consumidores:
```text
Market State,
Event State,
clustering,
ML,
IRL,
RL y AlphaEvolve con lag/as-of policy.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
Lag entre trade date,
settlement date,
observation date y as-of date.
```

Hipotesis cientifica:
```text
Short data suele publicarse con retraso; usarla sin lag crea leakage.
```

Preguntas que permite responder:
```text
Cuando se observo?
Cuando se publico?
Era legal en t?
```

Variables minimas:
```text
observation_date_type,
observation_date,
settlement_date,
trade_date,
as_of_date,
as_of_semantics.
```

Tabla donde deben vivir:
```text
011 para contexto;
016/017 para consumo agregado.
```

Consumidores:
```text
Market State,
Event State,
backtests y modelos point-in-time.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

