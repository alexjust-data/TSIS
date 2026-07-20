# 001 market_calendar - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Calendario legal de sesiones de mercado.
```

## Familias Relevantes

### Temporalidad

Fenomeno del mercado que representa:
```text
La estructura temporal legal del mercado: sesiones,
horarios,
early closes y timezone.
```

Hipotesis cientifica:
```text
El mismo observable cambia de significado segun fase de sesion,
apertura,
cierre o calendario.
```

Preguntas que permite responder:
```text
El mercado estaba abierto?
Cuanto dura la sesion?
Es early close?
Que timezone gobierna?
```

Variables minimas:
```text
session_date,
open_utc,
close_utc,
open_et,
close_et,
session_minutes,
is_early_close.
```

Tabla donde deben vivir:
```text
Deben vivir en 001 market_calendar.
```

Consumidores:
```text
Expected data,
014 intraday bars,
Market State,
Event State,
backtests,
ML/RL.
```

### Estructura

Fenomeno del mercado que representa:
```text
Particion y autoridad de calendario.
```

Hipotesis cientifica:
```text
Sin calendario canonico no hay expectedness ni alineacion temporal reproducible.
```

Preguntas que permite responder:
```text
Que calendario aplica?
Que dia/mes/session partition corresponde?
```

Variables minimas:
```text
calendar,
timezone,
year,
month,
dow.
```

Tabla donde deben vivir:
```text
Deben vivir en 001 market_calendar.
```

Consumidores:
```text
Builders,
validators,
registries y auditorias.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

