# Reference Operational Run Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema canonico para artefactos operacionales bajo:

- `D:\reference\_run`

Estos files no son datasets de referencia de mercado.

Son artefactos de control, auditoria y progreso del proceso de descarga.

## 2. Files observados

Archivos observados:

- `download_reference_universe_polygon.audit.csv`
- `download_reference_universe_polygon.errors.csv`
- `download_reference_universe_polygon.progress.json`

## 3. Schema CSV de auditoria y errores

Aplica a:

- `download_reference_universe_polygon.audit.csv`
- `download_reference_universe_polygon.errors.csv`

Columnas observadas:

- `ticker`
- `dataset`
- `request_date`
- `http_status`
- `pages`
- `rows_saved`
- `status`
- `msg`
- `out_file`
- `ts_utc`

### Tipos semanticos esperados

- `ticker`: string o vacio para datasets globales
- `dataset`: string
- `request_date`: fecha parseable o vacia
- `http_status`: entero
- `pages`: entero
- `rows_saved`: entero
- `status`: string
- `msg`: string
- `out_file`: path
- `ts_utc`: timestamp parseable

### Reglas estructurales minimas

- `dataset` no debe ser nulo.
- `status` no debe ser nulo.
- `out_file` debe apuntar al artefacto afectado o esperado.
- `ts_utc` debe ser parseable.
- En `errors.csv`, `status` normalmente debe ser `error`.

## 4. Schema JSON de progreso

Aplica a:

- `download_reference_universe_polygon.progress.json`

Campos observados:

- `status`
- `input`
- `outdir`
- `datasets`
- `done_tickers`
- `total_tickers`
- `progress_pct`
- `errors`
- `updated_at_utc`
- `audit_csv`
- `errors_csv`

### Tipos semanticos esperados

- `status`: string
- `input`: path
- `outdir`: path
- `datasets`: lista de strings
- `done_tickers`: entero no negativo
- `total_tickers`: entero no negativo
- `progress_pct`: numerico entre `0` y `100`
- `errors`: entero no negativo
- `updated_at_utc`: timestamp parseable
- `audit_csv`: path
- `errors_csv`: path

## 5. Reglas de interpretacion

Estos artefactos sirven para:

- trazabilidad de descarga;
- reanudacion;
- conteo de errores;
- auditoria operacional.

No deben usarse como:

- source of truth de referencia;
- schema de market data;
- ni prueba de calidad semantica de los datasets descargados.

## 6. Conclusion operacional

`D:\reference\_run` queda definido como capa operacional de descarga.

Sus schemas deben preservarse para reproducibilidad, pero no mezclarse con contratos semanticos de `all_tickers`, `overview`, `events`, `splits`, `dividends`, `exchanges` o `ticker_types`.
