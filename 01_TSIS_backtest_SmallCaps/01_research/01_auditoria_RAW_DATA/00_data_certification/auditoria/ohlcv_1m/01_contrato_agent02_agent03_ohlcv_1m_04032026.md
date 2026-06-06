## Contrato Agent02 / Agent03 para `ohlcv_1m`

### Objetivo

Definir el contrato reproducible de auditoría para el universo:

- `D:\ohlcv_1m`

La meta no es volver a descargar.
La meta es:

- inventariar exactamente qué files existen
- validar qué significa que un file `minute_aggs_*.parquet` sea técnicamente sano
- distinguir:
  - cobertura física
  - legibilidad estructural
  - coherencia de schema
  - validez económica OHLCV
- producir artefactos v2 compatibles con Agent03

---

## 1. Unidad lógica auditada

La unidad auditada en `ohlcv_1m` es:

- un file físico `minute_aggs_{ticker}_{year}_{month}.parquet`

Ejemplo real observado:

- `D:\ohlcv_1m\ticker=ZLS\year=2024\month=03\minute_aggs_ZLS_2024_03.parquet`

Cada file representa, conceptualmente:

- un ticker
- un año natural
- un mes natural
- múltiples barras de un minuto

No es una fila por día.
Es un contenedor mensual por ticker.

---

## 2. Schema observado en sample real

Leído file a file con `ParquetFile.read()`, el schema observado es:

- `ticker: string`
- `ts_utc: string`
- `date: string`
- `year: int64`
- `month: int64`
- `o: double`
- `h: double`
- `l: double`
- `c: double`
- `v: int64`
- `vw: double`
- `n: int64`
- `t: int64`

Sample confirmado:

- `D:\ohlcv_1m\ticker=ZLS\year=2024\month=03\minute_aggs_ZLS_2024_03.parquet`

---

## 3. Hallazgo estructural inicial

Se observó una anomalía reproducible de lectura:

- `pyarrow.parquet.read_table(file_path)` falla
- `pyarrow.parquet.ParquetFile(file_path).read()` funciona

Error observado:

- `ArrowTypeError: Unable to merge: Field ticker has incompatible types: string vs dictionary<values=string, indices=int32, ordered=0>`

Interpretación contractual:

- el file individual es legible
- pero el universo `ohlcv_1m` presenta heterogeneidad física de schema al menos en el campo `ticker`
- por tanto el auditor de `ohlcv_1m` debe validar dos cosas distintas:
  - legibilidad file-level
  - compatibilidad de schema para lectura estilo dataset

Esto no implica corrupción económica del contenido.
Sí implica anomalía estructural real del universo.

---

## 4. Qué esperamos de cada file

### 4.1. Expectativa de partición

El path esperado debe seguir este patrón:

- `ticker={TICKER}\year={YYYY}\month={MM}\minute_aggs_{TICKER}_{YYYY}_{MM}.parquet`

De ese path Agent02 debe derivar:

- `ticker_path`
- `year_path`
- `month_path`
- `filename_ticker`
- `filename_year`
- `filename_month`

Y comprobar consistencia interna.

### 4.2. Expectativa de cobertura lógica

Cada file debería contener:

- un solo ticker lógico
- un solo año lógico
- un solo mes lógico
- una o más filas de minuto

Y sus fechas deberían caer dentro del `year/month` del path.

### 4.3. Expectativa de columnas

Columnas requeridas mínimas:

- `ticker`
- `ts_utc`
- `date`
- `year`
- `month`
- `o`
- `h`
- `l`
- `c`
- `v`
- `vw`
- `n`
- `t`

### 4.4. Expectativa de tipos

Esperado:

- `ticker`: string compatible
- `ts_utc`: string compatible con parseo a timestamp UTC
- `date`: string compatible con parseo a fecha
- `year`: entero
- `month`: entero
- `o/h/l/c/vw`: numérico real
- `v/n/t`: entero o entero compatible

### 4.5. Expectativa económica OHLCV

Por cada fila de minuto:

- `o > 0`
- `h > 0`
- `l > 0`
- `c > 0`
- `v >= 0`
- `vw >= 0` si existe volumen
- `h >= max(o, c, l)`
- `l <= min(o, c, h)`
- `date` consistente con `ts_utc`

### 4.6. Expectativa de consistencia mensual

Dentro del file:

- `ticker` constante
- `year` constante
- `month` constante
- `ts_utc` sin duplicados
- `date` y `ts_utc` ordenables y parseables
- fechas dentro del `year/month` esperado

---

## 5. Metadatos mínimos por file en inventario

Cada fila de inventario debe incluir, como mínimo:

- `root`
- `root_path`
- `file`
- `relpath`
- `ticker`
- `year`
- `month`
- `task_key`
- `size_bytes`
- `mtime_utc`
- `inventory_seen_utc`

Semántica:

- `task_key = ticker|year|month`

En `ohlcv_1m`, la clave lógica natural no es `ticker|date`, sino:

- `ticker|year|month`

porque la unidad auditada es un parquet mensual.

---

## 6. Capas de validación por file

## 6.1. Capa 1. Validación física

Comprobar:

- file existe
- `size_bytes > 0`
- `ParquetFile.read()` funciona

Issues duros:

- `file_missing`
- `zero_byte_file`
- `parquet_unreadable`

## 6.2. Capa 2. Validación estructural de lectura

Comprobar adicionalmente:

- si `read_table(...)` funciona
- si falla, registrar la causa exacta

No tratarlo necesariamente como corrupción dura del contenido.
Sí registrarlo como anomalía estructural.

Warnings/issues sugeridos:

- `dataset_read_incompatible_schema`
- `schema_merge_conflict_ticker_encoding`

## 6.3. Capa 3. Validación de partición

Comprobar consistencia entre:

- path
- filename
- columnas del parquet

Issues:

- `invalid_partition_path`
- `partition_vs_filename_ticker_mismatch`
- `partition_vs_filename_year_mismatch`
- `partition_vs_filename_month_mismatch`
- `partition_vs_column_ticker_mismatch`
- `partition_vs_column_year_mismatch`
- `partition_vs_column_month_mismatch`

## 6.4. Capa 4. Validación de schema

Comprobar:

- columnas mínimas presentes
- tipos compatibles

Issues/warnings:

- `missing_required_columns`
- `dtype_mismatch`

## 6.5. Capa 5. Validación de contenido

Comprobar:

- `rows > 0`
- parseo de `ts_utc`
- parseo de `date`
- ticker único
- year único
- month único
- sin `ts_utc` duplicados
- fechas dentro del mes esperado

Issues:

- `zero_rows`
- `all_rows_invalid_after_parse`
- `multiple_tickers_in_file`
- `multiple_years_in_file`
- `multiple_months_in_file`
- `duplicate_ts_utc_in_file`
- `date_out_of_partition_month`

## 6.6. Capa 6. Validación económica OHLCV

Por fila y agregado del file:

- precios positivos
- volumen no negativo
- `h >= o`
- `h >= c`
- `h >= l`
- `l <= o`
- `l <= c`
- `l <= h`
- `vw` dentro de rango cuando `v > 0`

Issues:

- `negative_or_zero_ohlc_rows`
- `negative_volume_rows`
- `high_low_inversion_rows`
- `vw_outside_range_rows`

## 6.7. Capa 7. Validación de continuidad y densidad

Métricas esperadas:

- `rows`
- `date_min`
- `date_max`
- `active_days`
- `active_minutes`
- `coverage_ratio_vs_active_days_est`
- `max_gap_days`

Warnings:

- `suspicious_sparse_month`
- `large_internal_gap_days`
- `rows_lt_10`

Esto no implica por sí solo fallo duro.
Puede reflejar:

- ticker ilíquido
- mes parcial
- ausencia real de negocio durante casi todo el mes

---

## 7. Severidad contractual

### HARD_FAIL

Casos típicos:

- `parquet_unreadable`
- `file_missing`
- `zero_byte_file`
- `missing_required_columns`
- `all_rows_invalid_after_parse`
- `multiple_tickers_in_file`
- `multiple_years_in_file`
- `multiple_months_in_file`
- `duplicate_ts_utc_in_file`
- `negative_or_zero_ohlc_rows`
- `negative_volume_rows`
- `high_low_inversion_rows`

### SOFT_FAIL

Casos típicos:

- `dataset_read_incompatible_schema`
- `schema_merge_conflict_ticker_encoding`
- `dtype_mismatch`
- `suspicious_sparse_month`
- `large_internal_gap_days`
- `rows_lt_10`
- `vw_outside_range_rows` si se mantiene como warning de consistencia

### PASS

Cuando:

- el file abre
- el schema contractual está presente
- la partición es consistente
- no hay issues duros

---

## 8. Acción derivada

- `HARD_FAIL -> quarantine_and_retry`
- `SOFT_FAIL -> review_queue`
- `PASS -> accept_raw`

---

## 9. Contrato mínimo Agent03

Agent03 debe poder consumir:

- un `current` materializado
- un `retry_current`
- un `retry_frozen`
- un `live_status`

Sin reescanear el universo bruto.

Por tanto Agent02 v2 debe producir:

- `ohlcv_1m_current.parquet`
- `retry_current.parquet`
- `retry_frozen.parquet`
- `live_status_ohlcv_1m_strict.json`

además de los CSV contractuales equivalentes.
