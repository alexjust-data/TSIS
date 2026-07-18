# 000 instrument_master - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Identidad institucional de los instrumentos.
```

## Familias Relevantes

### Estructura

Fenomeno del mercado que representa:
```text
La identidad estable del instrumento: ticker,
instrumento,
listado,
mercado y tipo de security.
```

Hipotesis cientifica:
```text
Sin identidad estable no se puede comparar precio,
volumen,
eventos ni outcomes entre fechas.
```

Preguntas que permite responder:
```text
Que instrumento es?
Es el mismo ticker a traves del tiempo?
En que mercado/listado vive?
```

Variables minimas:
```text
instrument_id,
ticker,
identity_resolution_level,
ticker_identity_scope,
market,
primary_exchange,
ticker_type.
```

Tabla donde deben vivir:
```text
Deben vivir en 000 instrument_master.
```

Consumidores:
```text
Todas las tablas: Market State,
Event State,
scanners,
backtests,
ML,
IRL,
RL y AlphaEvolve como metadata de identidad.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
La validez temporal de la identidad.
```

Hipotesis cientifica:
```text
Un ticker puede cambiar de significado; la identidad solo es valida dentro de una ventana
temporal.
```

Preguntas que permite responder:
```text
Esta identidad es valida en la fecha t?
Puedo unir esta observacion con este instrumento?
```

Variables minimas:
```text
valid_from,
valid_to.
```

Tabla donde deben vivir:
```text
Deben vivir en 000 instrument_master.
```

Consumidores:
```text
Todos los builders que hagan joins historicos.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

