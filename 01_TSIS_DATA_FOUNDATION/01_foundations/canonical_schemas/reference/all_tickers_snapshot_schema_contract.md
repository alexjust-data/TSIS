# Reference All Tickers Snapshot Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para los snapshots historicos de `reference/all_tickers`.

La capa representa un snapshot fechado del universo de tickers disponible desde la fuente de referencia.

No representa por si sola:

- universo smallcaps final;
- elegibilidad `lt1b`;
- continuidad corporativa completa;
- ni calidad de market data.

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-reference-snapshot row`

Cada fila representa un ticker observado dentro de un snapshot `all_tickers` para una fecha de referencia.

## 3. Layout fisico observado

Ejemplo inspeccionado:

- `D:\reference\all_tickers\snapshot_date=2005-01-02.parquet`

Columnas fisicas observadas:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `cik`
- `composite_figi`
- `share_class_figi`
- `last_updated_utc`
- `snapshot_date`
- `_exchange_filter`
- `_dataset`
- `_ingested_utc`

Resultado de muestra:

- `rows = 2632`
- `_dataset = all_tickers`
- `snapshot_date = 2005-01-02`

## 4. Claves logicas

Claves minimas:

- `snapshot_date`
- `ticker`

Notas:

- `snapshot_date` puede estar en columna y tambien en el nombre fisico del file;
- `ticker` es simbolo de trading, no identidad corporativa estable universal.

## 5. Campos requeridos

Campos requeridos:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `snapshot_date`
- `_dataset`
- `_ingested_utc`

Campos identificadores recomendados cuando existan:

- `cik`
- `composite_figi`
- `share_class_figi`
- `last_updated_utc`
- `_exchange_filter`

## 6. Tipos semanticos esperados

- `ticker`: string no vacio
- `name`: string
- `market`: string, normalmente `stocks`
- `locale`: string, normalmente `us`
- `primary_exchange`: MIC o codigo de exchange
- `type`: codigo de tipo de ticker
- `active`: booleano
- `currency_name`: string
- `snapshot_date`: fecha parseable
- `_ingested_utc`: timestamp parseable

## 7. Reglas estructurales minimas

- `ticker` no debe ser nulo en filas validas.
- `snapshot_date` debe ser parseable.
- `_dataset` debe ser `all_tickers`.
- `_ingested_utc` debe ser parseable.
- La combinacion `snapshot_date + ticker` no deberia duplicarse dentro de un mismo file salvo limitacion documentada.

## 8. Reglas de interpretacion

Esta capa es una fotografia de referencia.

No debe usarse por si sola como:

- membership final del universo;
- prueba de que un ticker es smallcap;
- prueba de continuidad historica de una entidad;
- ni sustituto de `overview`, `events`, `splits` o `dividends`.

## 9. Consumidores esperados

Usos permitidos:

- construccion de universo bruto;
- auditoria de presencia historica de tickers;
- filtros preliminares por exchange, market, locale o type;
- trazabilidad de snapshots de descarga.

Usos que requieren capas adicionales:

- universe final `lt1b`;
- remaps corporativos;
- continuidad de identidad;
- backtest eligibility.

## 10. Conclusion operacional

`reference/all_tickers` queda definido como snapshot historico de presencia y metadatos basicos de tickers.

Es una capa de referencia upstream, no una policy final de elegibilidad.
