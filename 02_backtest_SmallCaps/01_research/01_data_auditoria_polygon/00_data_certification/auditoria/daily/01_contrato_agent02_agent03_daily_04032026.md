## Contrato Agent02 / Agent03 para `daily`

### Objetivo

Definir el contrato reproducible de auditoría para el universo:

- `D:\ohlcv_daily`
- `C:\TSIS_Data\data\ohlcv_daily` si existiera una réplica parcial

La meta no es volver a descargar.
La meta es:

- inventariar exactamente qué files existen
- validar qué significa que un file `day_aggs_*.parquet` sea técnicamente sano
- distinguir:
  - cobertura física
  - legibilidad estructural
  - coherencia de schema
  - validez económica OHLCV
- producir artefactos v2 compatibles con Agent03

---

## 1. Unidad lógica auditada

La unidad auditada en `daily` es:

- un file físico `day_aggs_{ticker}_{year}.parquet`

Ejemplo real observado:

- `D:\ohlcv_daily\ticker=AACQ\year=2021\day_aggs_AACQ_2021.parquet`

Cada file representa, conceptualmente:

- un ticker
- un año natural
- múltiples barras diarias

No es una fila por día.
Es un contenedor anual por ticker.

---

## 2. Schema observado en sample real

Leído file a file con `ParquetFile.read()`, el schema observado es:

- `ticker: string`
- `date: string`
- `year: int64`
- `o: double`
- `h: double`
- `l: double`
- `c: double`
- `v: double`
- `vw: double`
- `n: int64`
- `t: int64`

Samples confirmados:

- `D:\ohlcv_daily\ticker=AACQ\year=2021\day_aggs_AACQ_2021.parquet`
- `D:\ohlcv_daily\ticker=AAI\year=2011\day_aggs_AAI_2011.parquet`
- `D:\ohlcv_daily\ticker=MASI\year=2015\day_aggs_MASI_2015.parquet`
- `D:\ohlcv_daily\ticker=MASI\year=2026\day_aggs_MASI_2026.parquet`

---

## 3. Hallazgo estructural inicial

Se observó una anomalía reproducible de lectura:

- `pyarrow.parquet.read_table(file_path)` falla
- `pyarrow.parquet.ParquetFile(file_path).read()` funciona

Error observado:

- `ArrowTypeError: Unable to merge: Field ticker has incompatible types: string vs dictionary<values=string, indices=int32, ordered=0>`

Interpretación contractual:

- el file individual es legible
- pero el universo `daily` presenta heterogeneidad física de schema al menos en el campo `ticker`
- por tanto el auditor de `daily` debe validar dos cosas distintas:
  - legibilidad file-level
  - compatibilidad de schema para lectura estilo dataset

Esto no implica corrupción económica del contenido.
Sí implica anomalía estructural real del universo.

---

## 4. Qué esperamos de cada file

### 4.1. Expectativa de partición

El path esperado debe seguir este patrón:

- `ticker={TICKER}\year={YYYY}\day_aggs_{TICKER}_{YYYY}.parquet`

De ese path Agent02 debe derivar:

- `ticker_path`
- `year_path`
- `filename_ticker`
- `filename_year`

Y comprobar consistencia interna.

### 4.2. Expectativa de cobertura lógica

Cada file debería contener:

- un solo ticker lógico
- un solo año lógico
- una o más filas diarias

Y sus fechas deberían caer dentro del año del path.

### 4.3. Expectativa de columnas

Columnas requeridas mínimas:

- `ticker`
- `date`
- `year`
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
- `date`: string compatible con parseo a fecha
- `year`: entero
- `o/h/l/c/v/vw`: numérico real
- `n/t`: entero o entero compatible

### 4.5. Expectativa económica OHLCV

Por cada fila diaria:

- `o > 0`
- `h > 0`
- `l > 0`
- `c > 0`
- `v >= 0`
- `vw >= 0` si existe volumen
- `h >= max(o, c, l)`
- `l <= min(o, c, h)`
- `date` única por fila

### 4.6. Expectativa de consistencia anual

Dentro del file:

- `ticker` constante
- `year` constante
- `date` sin duplicados
- `date` ordenable y parseable
- fechas dentro del año esperado

---

## 5. Metadatos mínimos por file en inventario

Cada fila de inventario debe incluir, como mínimo:

- `root`
- `root_path`
- `file`
- `relpath`
- `ticker`
- `year`
- `task_key`
- `size_bytes`
- `mtime_utc`
- `inventory_seen_utc`

Semántica:

- `task_key = ticker|year`

En `daily`, la clave lógica natural no es `ticker|date`, sino:

- `ticker|year`

porque la unidad auditada es un parquet anual.

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
- `partition_vs_column_ticker_mismatch`
- `partition_vs_column_year_mismatch`

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
- `date` parseable
- `ticker` único
- `year` único
- `date` sin duplicados
- fechas dentro del año esperado

Issues:

- `zero_rows`
- `all_rows_invalid_after_parse`
- `multiple_tickers_in_file`
- `multiple_years_in_file`
- `duplicate_dates_in_file`
- `date_out_of_partition_year`

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
- `vw` razonable dentro de `[l, h]` cuando `v > 0`

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
- `business_days_covered_est`
- `coverage_ratio_vs_business_days`
- `max_gap_days`

Warnings:

- `suspicious_sparse_year`
- `large_internal_gap_days`

Esto no implica por sí solo fallo duro.
Puede reflejar:

- IPO
- delisting
- ticker parcial ese año
- año en curso

---

## 7. Clasificación de severidad

### HARD_FAIL

Reservado para:

- corrupción física
- falta de columnas mínimas
- parseo inviable
- incoherencia fuerte de partición
- OHLC imposible
- duplicados diarios incompatibles con el contrato

### SOFT_FAIL

Reservado para:

- dtype mismatch no bloqueante
- incompatibilidad de lectura estilo dataset
- sparsity sospechosa
- huecos grandes
- warnings de densidad o continuidad

### PASS

File legible, consistente y económicamente plausible bajo el contrato.

---

## 8. Salida correcta por file

Cada validación debe producir, como mínimo:

- `file`
- `ticker`
- `year`
- `rows`
- `severity`
- `issues`
- `warns`
- `action`
- `metrics_json`
- `validator_version`
- `processed_at_utc`
- `run_id`
- `batch_id`
- `scan_reason`
- `validation_kind`

En `metrics_json` deben quedar al menos:

- `size_bytes`
- `schema_columns`
- `schema_types`
- `rows_after_parse`
- `date_min`
- `date_max`
- `coverage_ratio_vs_business_days`
- `max_gap_days`
- `dataset_read_compatible`
- `dataset_read_error`

---

## 9. Artefactos contractuales v2

Agent02 Daily debe publicar:

- `daily_agent_strict_events_current.csv`
- `retry_queue_daily_strict_current.csv`
- `retry_frozen_daily_strict.csv`
- `live_status_daily_strict.json`
- `run_config_daily_strict.json`
- `batch_manifest_daily_v2.csv`

Y como backend v2:

- `daily_inventory_files.parquet`
- `daily_validation_events`
- `daily_current.parquet`
- `retry_current.parquet`
- `retry_frozen.parquet`

---

## 10. Qué debe consumir Agent03

Agent03 Daily debe poder responder:

- cobertura física por ticker y año
- files no legibles
- problemas de schema
- problemas de path/partición
- problemas OHLC imposibles
- densidad y gaps anómalos
- universo de warnings estructurales de `daily`

Y debe distinguir explícitamente:

- problema de contenido OHLCV
- problema físico de parquet
- problema de encoding/schema
- problema de cobertura temporal

---

## 11. Implicación para otras ramas

Esta auditoría no es aislada.
`daily` se usa como referencia en:

- `trades`
- comparativas con `1m`
- cobertura cruzada del universo

Por tanto, cualquier anomalía en `daily` afecta a la interpretación de:

- `trade_price_outside_daily_range`
- `trades vs daily`
- reconciliaciones `daily vs 1m`

---

## 12. Orden recomendado de trabajo

1. fijar este contrato
2. construir auditoría operativa `00_auditoria_daily.md`
3. implementar:
   - `051_daily_v2_inventory.py`
   - `050_daily_v2_validate_file.py`
   - `052_daily_v2_validate_batches.py`
   - `053_daily_v2_materialize_current.py`
4. correr smoke sobre subconjunto controlado
5. construir notebook Agent03 Daily
6. volver después a `trades` con referencias auditadas

---

## 13. En una frase

En `daily`, el contrato correcto no solo valida OHLCV.
También debe validar la legibilidad estructural del parquet y la compatibilidad de schema del universo.
