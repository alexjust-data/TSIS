# 007 event_windows_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Ventanas temporales alrededor de eventos.
```

## Familias Relevantes

### Eventos

Fenomeno del mercado que representa:
```text
Alineacion de observaciones respecto a un evento.
```

Hipotesis cientifica:
```text
El comportamiento se entiende mejor relativo a un ancla de evento que solo por timestamp
absoluto.
```

Preguntas que permite responder:
```text
Que evento es?
Que ventana pre/at/post se analiza?
Que fuente lo define?
```

Variables minimas:
```text
event_window_id,
source_event_id,
event_family,
event_type,
event_code,
event_source.
```

Tabla donde deben vivir:
```text
Deben vivir en 007 event_windows_table.
```

Consumidores:
```text
Event State,
outcomes,
research experiments,
ML/IRL/RL.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
Separacion causal entre antes,
durante y despues.
```

Hipotesis cientifica:
```text
No se debe mezclar informacion posterior al evento con estado previo.
```

Preguntas que permite responder:
```text
Que era observable antes del evento?
Que pertenece al outcome?
```

Variables minimas:
```text
window_start,
window_end,
window_role,
event_timestamp.
```

Tabla donde deben vivir:
```text
007 para geometria;
017 para estado observable;
008 para outcomes.
```

Consumidores:
```text
Event State,
outcomes,
backtests,
ML/RL.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

