## Agent02 ohlcv_1m: estado objetivo, contrato operativo y propuesta de auditoría v2

### 1. Run de referencia

El universo `ohlcv_1m` descargado y disponible localmente está en:

- `D:\ohlcv_1m`

Y la rama general de contexto está documentada en:

- [00_auditoria_general.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\00_auditoria_general.md)

En la auditoría general ya quedó fijado que:

- `ohlcv_1m` se descargó por ticker
- `ohlcv_1m` es referencia estructural para:
  - cobertura `daily vs 1m`
  - diagnóstico de `trades`
  - contrastes posteriores con `quotes`

El objetivo ahora ya no es descargar.
El objetivo es construir Agent02 v2 para `ohlcv_1m`.

---

## 2. Estado inicial observado

Se ha inspeccionado el sample real:

- `D:\ohlcv_1m\ticker=ZLS\year=2024\month=03\minute_aggs_ZLS_2024_03.parquet`

Hallazgos observados file a file con `ParquetFile.read()`:

- `rows = 62`
- columnas:
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
- `date_min = 2024-03-01`
- `date_max = 2024-03-28`
- `ts_min = 2024-03-01T19:50:00Z`
- `ts_max = 2024-03-28T19:25:00Z`
- sin nulos en el sample leído

Hallazgo estructural importante:

- `pyarrow.parquet.read_table(file_path)` falla
- `pyarrow.parquet.ParquetFile(file_path).read()` funciona

Error reproducido:

- `ArrowTypeError: Unable to merge: Field ticker has incompatible types: string vs dictionary<values=string, indices=int32, ordered=0>`

Interpretación operativa:

- el universo `ohlcv_1m` parece legible file a file
- pero no necesariamente homogéneo cuando PyArrow intenta unificar schema en modo dataset

Esto implica que `ohlcv_1m` tiene, como mínimo, una anomalía estructural del universo.

---

## 3. Conclusión operativa del estado actual

No estamos ante una mera auditoría de OHLC minuto.

En `ohlcv_1m` hay que auditar simultáneamente:

1. cobertura física del universo
2. legibilidad file-level
3. compatibilidad estructural de schema
4. coherencia de partición
5. plausibilidad OHLCV
6. densidad temporal por mes
7. consistencia de fechas y timestamps intrames

Por tanto, el espejo correcto de `quotes/trades/daily` para `ohlcv_1m` debe nacer directamente en v2 y no copiar un backend legacy.

---

## 4. Archivos que deben gobernar el estado de Agent02 ohlcv_1m

Dentro de un `RUN_DIR` v2, los artefactos objetivo deben ser:

- `live_status_ohlcv_1m_strict.json`
- `ohlcv_1m_agent_strict_events_current.csv`
- `retry_queue_ohlcv_1m_strict_current.csv`
- `retry_frozen_ohlcv_1m_strict.csv`
- `run_config_ohlcv_1m_strict.json`
- `batch_manifest_ohlcv_1m_v2.csv`
- `validation_checkpoint.json`
- `validation_run_manifest.json`
- `events_batches\batch_*.parquet`
- `materialization_summary.json`

Para inventario:

- `ohlcv_1m_inventory_files.parquet`
- `ohlcv_1m_inventory_files.csv`
- `ohlcv_1m_inventory_by_ticker.parquet`
- `ohlcv_1m_inventory_by_ticker.csv`
- `ohlcv_1m_inventory_summary.json`

---

## 5. Implementación objetivo de Agent02 v2

### 5.1. Inventario exacto

La fase de inventario debe responder:

- qué files `minute_aggs_*.parquet` existen
- en qué root existen
- qué `ticker|year|month` representan
- qué tamaño tienen
- cuándo se observaron

La unidad lógica aquí es:

- `task_key = ticker|year|month`

### 5.2. Validación profunda por file

La validación debe decidir para cada file:

- `PASS`
- `SOFT_FAIL`
- `HARD_FAIL`

Y debe hacerlo separando:

- lectura file-level
- lectura dataset-style
- schema
- partición
- contenido OHLCV
- densidad mensual

### 5.3. Materialización current / retry / live

Desde el log append-only por batch deben derivarse:

- `ohlcv_1m_current`
- `retry_current`
- `retry_frozen`
- `live_status`

y exports contractuales para Agent03.

---

## 6. Problemas lógicos y estructurales a evitar

### 6.1. Repetir un backend legacy

No conviene usar:

- CSV gigantes como fuente de verdad
- JSON grandes como estado vivo
- relectura completa en cada ciclo

`ohlcv_1m` debe nacer directamente con:

- Parquet append-only
- checkpoint
- manifest
- materialización periódica

### 6.2. Auditar solo OHLC y olvidar el schema físico

En `ohlcv_1m` ya vimos una anomalía estructural del universo.

Por tanto no basta con decir:

- abre
- cuenta filas
- revisa precios

También hay que auditar:

- compatibilidad de schema físico
- conflicto `string vs dictionary-encoded string`
- diferencia entre legibilidad file-level y dataset-level

### 6.3. Mezclar cobertura física con validez económica

Un file puede:

- existir
- abrir bien con `ParquetFile`
- tener OHLC plausible

y aun así presentar:

- incompatibilidad de lectura dataset-style
- conflicto estructural de schema

Por tanto:

- inventario
- validación
- current

deben quedar claramente separados.

### 6.4. Suponer que sparsity intrames = corrupción

En `ohlcv_1m`, un file mensual puede ser corto por:

- ticker ilíquido
- IPO
- delisting
- mes parcial
- ausencia real de actividad en muchos minutos o días

La baja densidad temporal no debe caer directamente en `HARD_FAIL`.

---

## 7. Contrato de validación de `minute_aggs_*.parquet`

La referencia contractual detallada está en:

- [01_contrato_agent02_agent03_ohlcv_1m_04032026.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\ohlcv_1m\01_contrato_agent02_agent03_ohlcv_1m_04032026.md)

Resumen operativo:

### Capa 1. Física

- file existe
- `size_bytes > 0`
- `ParquetFile.read()` funciona

### Capa 2. Estructural

- `read_table(...)` funciona o no
- si no funciona:
  - registrar incompatibilidad estructural

### Capa 3. Partición

Contrastar:

- `ticker={TICKER}`
- `year={YYYY}`
- `month={MM}`
- `minute_aggs_{TICKER}_{YYYY}_{MM}.parquet`

contra columnas:

- `ticker`
- `date`
- `year`
- `month`

### Capa 4. Schema

Columnas mínimas:

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

### Capa 5. Contenido

- filas > 0
- `ts_utc` parseable
- `date` parseable
- ticker único
- year único
- month único
- fechas dentro del `year/month` esperado

### Capa 6. Economía minuto

- precios positivos
- volumen no negativo
- `high/low` coherente
- `vw` dentro de rango cuando `v > 0`

### Capa 7. Densidad mensual

- `date_min`
- `date_max`
- `rows_after_parse`
- `active_days`
- `max_gap_days`

---

## 8. Diseño de implementación

El diseño técnico se fija en:

- [02_diseno_implementacion_ohlcv_1m_v2.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\ohlcv_1m\02_diseno_implementacion_ohlcv_1m_v2.md)

El orden correcto de trabajo es:

1. contrato
2. diseño técnico
3. `050`
4. `051`
5. `052`
6. `053`
7. notebook raíz de problemas

---

## 9. Cierre operativo alcanzado

La auditoría ya queda aterrizada sobre los outputs reales de:

- `ohlcv_1m_v2_validation/ohlcv_1m_validate_full`
- `ohlcv_1m_v2_materialized/ohlcv_1m_current_full`
- `root_cause_operational_outputs`

Diagnóstico final alcanzado:

- `schema` = anomalía estructural conocida y separable
- `vw` = problema económico dominante
- `parse/price invalid` = núcleo duro pequeño pero real

Taxonomía refinada de `vw` fijada:

- `vw_mild_low_ratio`
- `vw_moderate_ratio`
- `vw_severe_tiny_base`
- `vw_severe_small_mass`
- `vw_severe_large_mass_diffuse`
- `vw_severe_large_mass_persistent`

Política operativa resultante:

- `good`
  - `RESCUE_SCHEMA_ONLY`
  - `vw_mild_low_ratio`
- `review`
  - `vw_moderate_ratio`
  - `vw_severe_tiny_base`
  - `vw_severe_small_mass`
- `bad`
  - `vw_severe_large_mass_diffuse`
  - `vw_severe_large_mass_persistent`
  - `QUARANTINE_PARSE_INVALID`
  - `QUARANTINE_PRICE_INVALID`

Verificación en notebooks:

- `03_ohlcv_1m_root_cause_audit_notebook.ipynb` queda como notebook metodológico con la apertura refinada de `vw`
- `04_ohlcv_1m_closeout.ipynb` queda como notebook ejecutivo final
- el `closeout` fue corregido para usar los campos reales de `validation_run_manifest.json` y `materialization_summary.json`
- el `closeout` fue validado ejecutando sus celdas contra los artifacts reales

Conclusión:

- `ohlcv_1m` puede darse por cerrado al mismo nivel operativo que `trades` y `quotes`
- si en el futuro se reabre, ya no sería para redescubrir el problema, sino para ajustar tolerancias de uso en research, backtesting o modelado
