# 002 expected_data_calendar - Lectura De Representacion

Status: `representation_reading_v0_2_concise`

Date: `2026-07-16`

Este documento es deliberadamente corto.

No intenta certificar la tabla ni repetir contratos.
Solo responde que familia de informacion representa la tabla, por que esas variables merecen existir y quien las consumira downstream.

## Ser De La Tabla

```text
Expectedness: que dato deberia existir para instrumento/sesion/fuente.
```

## Familias Relevantes

### Estructura

Fenomeno del mercado que representa:
```text
La expectativa institucional de existencia de datos.
```

Hipotesis cientifica:
```text
Una ausencia solo es informativa si sabemos que el dato era esperado.
```

Preguntas que permite responder:
```text
Deberia existir dato para este instrumento y sesion?
Si falta, es fallo o ausencia esperada?
```

Variables minimas:
```text
expected_dataset_id,
expected_source_root,
expected_session,
expected_reason,
expectation_scope.
```

Tabla donde deben vivir:
```text
Deben vivir en 002 expected_data_calendar.
```

Consumidores:
```text
Certification matrix,
validators,
Market State,
Event State,
scanners y backtests como control de cobertura.
```

### Temporalidad

Fenomeno del mercado que representa:
```text
Cobertura esperada por sesion.
```

Hipotesis cientifica:
```text
La completitud de datos es una propiedad por sesion,
no solo por archivo.
```

Preguntas que permite responder:
```text
Que sesiones son esperadas?
Desde cuando es valida esta expectativa?
```

Variables minimas:
```text
instrument_id,
ticker,
session_date,
valid_from,
month.
```

Tabla donde deben vivir:
```text
Deben vivir en 002 expected_data_calendar.
```

Consumidores:
```text
003,
004,
013,
014 y downstream que necesite distinguir missing de no esperado.
```

## Lectura Final

```text
La tabla debe mantenerse solo en las familias indicadas. Cualquier variable nueva debe justificar familia, hipotesis y consumidor antes de entrar.
```

