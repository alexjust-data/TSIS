# Reference Splits Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `reference/splits`.

La capa representa eventos de split y reverse split por ticker.

Es fuente primaria para construir `split_normalized` y para validar `ohlcv_1m_split_normalized`.

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-split event`

Cada fila con payload representa un evento de split asociado a un ticker y fecha de ejecucion.

## 3. Layout fisico observado

Ejemplo con payload real:

- `D:\reference\splits\ticker=AA\splits_AA.parquet`

Columnas fisicas observadas con payload:

- `execution_date`
- `id`
- `split_from`
- `split_to`
- `ticker`
- `_dataset`
- `_ingested_utc`

Ejemplo sin payload:

- `D:\reference\splits\ticker=F\splits_F.parquet`

Columnas fisicas observadas sin eventos:

- `ticker`
- `_dataset`
- `_ingested_utc`

## 4. Claves logicas

Claves recomendadas para filas con payload:

- `ticker`
- `id`

Claves alternativas:

- `ticker`
- `execution_date`
- `split_from`
- `split_to`

## 5. Campos requeridos

Campos requeridos para cualquier file:

- `ticker`
- `_dataset`
- `_ingested_utc`

Campos requeridos para filas con payload:

- `execution_date`
- `id`
- `split_from`
- `split_to`

## 6. Tipos semanticos esperados

- `ticker`: string no vacio
- `execution_date`: fecha parseable
- `id`: string identificador del evento
- `split_from`: entero positivo
- `split_to`: entero positivo
- `_dataset`: string, debe ser `splits`
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- Todo file debe conservar `ticker`, `_dataset` e `_ingested_utc`.
- En files con payload, `execution_date` debe ser parseable.
- En files con payload, `split_from > 0` y `split_to > 0`.
- En files con payload, `ticker + id` no deberia duplicarse salvo limitacion documentada.
- Un file con solo `ticker`, `_dataset`, `_ingested_utc` debe leerse como `no split events observed`, no como schema roto.

## 8. Reglas de interpretacion

La razon de split se interpreta como:

- `split_ratio = split_to / split_from`

Ejemplos:

- `split_from = 1`, `split_to = 2` -> forward split 2-for-1
- `split_from = 10`, `split_to = 1` -> reverse split 1-for-10

La direccion exacta debe mantenerse explicita para evitar invertir factores.

## 9. Relacion con price views

Esta capa alimenta:

- `split_normalized`
- `daily_adjusted`
- `ohlcv_1m_split_normalized`
- reconciliacion entre `daily`, `1m`, `quotes` y `trades`

No representa:

- ajuste economico por dividendos;
- continuidad corporativa por ticker change;
- ni verdad de ejecucion.

## 10. Conclusion operacional

`reference/splits` queda definido como fuente canonica de eventos de split por ticker, con dos formas fisicas validas:

- payload real de eventos;
- file sin eventos con metadata minima.
