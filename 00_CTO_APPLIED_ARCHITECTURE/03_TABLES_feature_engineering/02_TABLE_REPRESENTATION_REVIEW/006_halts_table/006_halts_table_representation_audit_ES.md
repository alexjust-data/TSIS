# 006 halts_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Eventos de halt/resume y su contexto temporal.
```

## Familias Relevantes

### Eventos

Fenomeno del mercado que representa:
```text
Interrupcion discreta de negociacion.
```

Hipotesis cientifica:
```text
Un halt cambia observabilidad,
liquidez,
riesgo y respuesta posterior.
```

Preguntas que permite responder:
```text
Hubo halt?
Cuando empezo?
Cuando resume?
Que fuente lo reporta?
```

Variables minimas:
```text
halt_event_id,
source_event_key,
halt_date,
halt_start_et,
resume_time,
halt_reason.
```

Tabla donde deben vivir:
```text
Deben vivir en 006 halts_table;
ventanas derivadas en 007.
```

Consumidores:
```text
Event State,
outcomes,
scanners,
backtests,
execution research.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
Intervalo no negociable o de negociacion alterada.
```

Hipotesis cientifica:
```text
Durante un halt no se puede interpretar el mercado como en una sesion normal.
```

Preguntas que permite responder:
```text
t cae dentro del halt?
El evento ocurre antes o despues del resume?
```

Variables minimas:
```text
halt_start,
resume_time,
halt_duration,
session_date.
```

Tabla donde deben vivir:
```text
006 para evento;
017 para estado relativo.
```

Consumidores:
```text
Market State,
Event State,
backtests y execution policies.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

