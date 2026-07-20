# 009 fundamentals_asof_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Contexto fundamental disponible legalmente en un tiempo dado.
```

## Familias Relevantes

### Fundamentales

Fenomeno del mercado que representa:
```text
Condicion financiera y de reporting de la compania.
```

Hipotesis cientifica:
```text
Fundamentales pueden cambiar atencion,
riesgo,
elegibilidad,
regimen y respuesta a eventos.
```

Preguntas que permite responder:
```text
Que se sabia de la compania en t?
Era informacion fresca o stale?
Que filing gobierna?
```

Variables minimas:
```text
as_of_date,
filing_date,
period_end,
fiscal_year,
fiscal_quarter,
timeframe,
CIK,
fundamental_metric,
staleness.
```

Tabla donde deben vivir:
```text
Deben vivir en 009 fundamentals_asof_table.
```

Consumidores:
```text
Market State,
Event State,
clustering,
ML,
IRL,
RL y AlphaEvolve solo con point-in-time/as-of enforcement.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
Disponibilidad legal de la informacion fundamental.
```

Hipotesis cientifica:
```text
Usar period_end como si fuera fecha conocida crea leakage.
```

Preguntas que permite responder:
```text
La informacion estaba publicada antes de t?
Cuanto tiempo llevaba disponible?
```

Variables minimas:
```text
filing_date,
as_of_date,
availability_flag,
metric_staleness.
```

Tabla donde deben vivir:
```text
009 para snapshot as-of;
016/017 para consumo agregado.
```

Consumidores:
```text
Market State,
Event State,
ML/RL con control point-in-time.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

