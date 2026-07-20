# 005 corporate_actions_table - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Eventos corporativos que cambian comparabilidad historica.
```

## Familias Relevantes

### Estructura

Fenomeno del mercado que representa:
```text
Cambios estructurales del instrumento: splits,
dividends,
symbol/name changes u otros ajustes.
```

Hipotesis cientifica:
```text
Sin corporate actions,
precio y volumen historicos pueden compararse mal.
```

Preguntas que permite responder:
```text
Hubo ajuste?
La serie es comparable?
Que fuente gobierna la accion?
```

Variables minimas:
```text
corporate_action_id,
action_type,
action_date,
source_system,
source_priority.
```

Tabla donde deben vivir:
```text
Deben vivir en 005 corporate_actions_table.
```

Consumidores:
```text
004,
013/014,
Market State,
Event State y validadores.
```

### Eventos

Fenomeno del mercado que representa:
```text
Corporate action como posible evento o contexto de evento.
```

Hipotesis cientifica:
```text
Un split,
dividend o cambio estructural puede alterar liquidez,
atencion y comportamiento futuro.
```

Preguntas que permite responder:
```text
La accion puede crear una ventana de evento?
Debe condicionar outcomes?
```

Variables minimas:
```text
action_type,
action_date,
source_event_id.
```

Tabla donde deben vivir:
```text
Evento fuente en 005;
ventanas en 007;
estado relativo al evento en 017.
```

Consumidores:
```text
Event State,
outcomes,
research experiments,
backtests.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

