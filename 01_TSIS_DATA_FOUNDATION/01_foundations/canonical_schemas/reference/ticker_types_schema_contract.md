# Reference Ticker Types Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `reference/ticker_types`.

La capa representa el diccionario de codigos de tipo de ticker usados por la fuente de referencia.

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-type-code row`

Cada fila describe un codigo de tipo de instrumento.

## 3. Layout fisico observado

Ejemplo inspeccionado:

- `D:\reference\ticker_types\ticker_types.parquet`

Columnas fisicas observadas:

- `code`
- `description`
- `asset_class`
- `locale`
- `_dataset`
- `_ingested_utc`

Resultado observado:

- `rows = 25`

## 4. Claves logicas

Clave primaria recomendada:

- `code`

Claves auxiliares:

- `asset_class`
- `locale`

## 5. Campos requeridos

Campos requeridos:

- `code`
- `description`
- `asset_class`
- `locale`
- `_dataset`
- `_ingested_utc`

## 6. Tipos semanticos esperados

- `code`: string no vacio
- `description`: string
- `asset_class`: string
- `locale`: string
- `_dataset`: string, debe ser `ticker_types`
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- `code` no debe ser nulo.
- `description` no debe ser nula.
- `_dataset` debe ser `ticker_types`.
- `_ingested_utc` debe ser parseable.
- `code` no deberia duplicarse dentro del file salvo limitacion documentada.

## 8. Reglas de interpretacion

Esta capa sirve para traducir codigos como:

- `CS`
- `PFD`
- `WARRANT`
- `RIGHT`

No decide por si sola:

- elegibilidad de universo;
- liquidez;
- smallcap status;
- ni consumo de backtest.

## 9. Conclusion operacional

`reference/ticker_types` queda definido como diccionario canonico de codigos de instrumento.
