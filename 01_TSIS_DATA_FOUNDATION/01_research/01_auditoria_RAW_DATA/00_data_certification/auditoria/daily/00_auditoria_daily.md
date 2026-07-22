## Agent02 Daily: estado objetivo, contrato operativo y propuesta de auditoría v2

### 1. Run de referencia

El universo `daily` descargado y disponible localmente está en:

- `D:\ohlcv_daily`

Y la rama general de contexto está documentada en:

- [00_auditoria_general.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\00_auditoria_general.md)

En la auditoría general ya quedó fijado que:

- `daily` se descargó desde un universo operativo por ticker único
- `daily` es referencia estructural para:
  - cobertura `daily vs 1m`
  - diagnóstico de `trades`
  - verificaciones cruzadas posteriores

El objetivo ahora ya no es descargar.
El objetivo es construir Agent02 v2 para `daily`.

---

## 2. Estado inicial observado

Se han inspeccionado samples reales de `daily`, entre ellos:

- `D:\ohlcv_daily\ticker=AACQ\year=2021\day_aggs_AACQ_2021.parquet`
- `D:\ohlcv_daily\ticker=AAI\year=2011\day_aggs_AAI_2011.parquet`
- `D:\ohlcv_daily\ticker=MASI\year=2015\day_aggs_MASI_2015.parquet`
- `D:\ohlcv_daily\ticker=MASI\year=2026\day_aggs_MASI_2026.parquet`

Hallazgo importante:

- `pyarrow.parquet.read_table(file_path)` falla
- `pyarrow.parquet.ParquetFile(file_path).read()` funciona

Error reproducido:

- `ArrowTypeError: Unable to merge: Field ticker has incompatible types: string vs dictionary<values=string, indices=int32, ordered=0>`

Interpretación operativa:

- el universo `daily` parece legible file a file
- pero no necesariamente homogéneo cuando PyArrow intenta unificar schema en modo dataset

Esto implica que `daily` tiene, como mínimo, una anomalía estructural del universo.

---

## 3. Conclusión operativa del estado actual

No estamos ante una mera auditoría de OHLC.

En `daily` hay que auditar simultáneamente:

1. cobertura física del universo
2. legibilidad file-level
3. compatibilidad estructural de schema
4. coherencia de partición
5. plausibilidad OHLCV
6. densidad temporal por año

Por tanto, el espejo correcto de `quotes/trades` para `daily` debe nacer directamente en v2 y no copiar un backend legacy.

---

## 4. Archivos que deben gobernar el estado de Agent02 Daily

Dentro de un `RUN_DIR` v2, los artefactos objetivo deben ser:

- `live_status_daily_strict.json`
- `daily_agent_strict_events_current.csv`
- `retry_queue_daily_strict_current.csv`
- `retry_frozen_daily_strict.csv`
- `run_config_daily_strict.json`
- `batch_manifest_daily_v2.csv`
- `validation_checkpoint.json`
- `validation_run_manifest.json`
- `events_batches\batch_*.parquet`
- `materialization_summary.json`

Para inventario:

- `daily_inventory_files.parquet`
- `daily_inventory_files.csv`
- `daily_inventory_by_ticker.parquet`
- `daily_inventory_by_ticker.csv`
- `daily_inventory_summary.json`

---

## 5. Implementación objetivo de Agent02 v2

### 5.1. Inventario exacto

La fase de inventario debe responder:

- qué files `day_aggs_*.parquet` existen
- en qué root existen
- qué `ticker|year` representan
- qué tamaño tienen
- cuándo se observaron

La unidad lógica aquí es:

- `task_key = ticker|year`

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
- densidad anual

### 5.3. Materialización current / retry / live

Desde el log append-only por batch deben derivarse:

- `daily_current`
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

`daily` debe nacer directamente con:

- Parquet append-only
- checkpoint
- manifest
- materialización periódica

### 6.2. Auditar solo OHLC y olvidar el schema físico

En `daily` ya vimos que hay una anomalía estructural del universo.

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

### 6.4. Suponer que sparsity = corrupción

En `daily`, un file anual puede ser corto por:

- IPO
- delisting
- ticker parcial ese año
- año en curso

La baja cobertura temporal no debe caer directamente en `HARD_FAIL`.

---

## 7. Contrato de validación de `day_aggs_*.parquet`

La referencia contractual detallada está en:

- [01_contrato_agent02_agent03_daily_04032026.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\daily\01_contrato_agent02_agent03_daily_04032026.md)

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
- `day_aggs_{TICKER}_{YYYY}.parquet`

contra columnas:

- `ticker`
- `year`
- `date`

### Capa 4. Schema

Columnas mínimas:

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

### Capa 5. Contenido

- filas > 0
- ticker único
- year único
- fechas parseables
- fechas dentro del año
- sin duplicados por `date`

### Capa 6. OHLCV económico

- OHLC positivos
- `high >= low`
- `high >= open/close`
- `low <= open/close`
- `vw` razonable

### Capa 7. Densidad y continuidad

- `date_min`
- `date_max`
- cobertura vs business days
- huecos máximos

---

## 8. Tablas maestras v2

### 8.1. `daily_inventory_files`

Una fila por file físico:

- `root`
- `file`
- `ticker`
- `year`
- `task_key`
- `size_bytes`
- `mtime_utc`

### 8.2. `daily_validation_events`

Una fila por validación:

- `file`
- `processed_at_utc`
- `severity`
- `issues`
- `warns`
- `validator_version`
- `validation_kind`
- `scan_reason`
- `batch_id`
- `run_id`
- `metrics_json`

### 8.3. `daily_current`

Una fila por file lógico actual:

- último estado vigente
- root
- task_key
- presente en `C`
- presente en `D`
- severity actual

---

## 9. Fases objetivo

## 9.1. Inventory `051_daily_v2_inventory.py`

Debe:

- recorrer roots físicos
- localizar `day_aggs_*.parquet`
- derivar `ticker|year`
- persistir:
  - `inventory_batches`
  - `inventory_checkpoint.json`
  - `inventory_run_manifest.json`

Y al final materializar:

- `daily_inventory_files.parquet`
- `daily_inventory_by_ticker.parquet`
- `daily_inventory_summary.json`

## 9.2. Validate `050/052`

- `050_daily_v2_validate_file.py`
  - valida un file
- `052_daily_v2_validate_batches.py`
  - trocea inventario en batches
  - ejecuta validación paralela
  - persiste:
    - `events_batches`
    - `validation_checkpoint.json`
    - `validation_run_manifest.json`
    - `batch_manifest_daily_v2.*`
    - `validation_run_summary.json`

## 9.3. Materialize `053_daily_v2_materialize_current.py`

Debe derivar:

- `daily_current.*`
- `retry_current.*`
- `retry_frozen.*`
- `live_status_daily_strict.json`
- `materialization_summary.json`

---

## 10. Estrategia de auditoría recomendada

No conviene empezar con todo el histórco de golpe.

Orden correcto:

1. construir contrato
2. inventario global
3. smoke de validación sobre subconjunto acotado
4. notebook Agent03 Daily
5. solo entonces escalar a full

El smoke ideal debería cubrir:

- varios tickers
- varios años
- casos viejos y recientes
- casos donde ya vimos la anomalía estructural

---

## 11. Relación con `1m` y `trades`

Esta auditoría no es aislada.

Si `daily` tiene:

- incompatibilidades de schema
- problemas de densidad
- OHLC inconsistentes

eso afecta directamente a:

- `daily vs 1m`
- `trades vs daily`
- interpretación de `trade_price_outside_daily_range`

Por eso tiene sentido aparcar parcialmente la rama de `trades` y auditar ahora `daily`.

---

## 12. Veredicto técnico

`daily` necesita una auditoría propia y completa.

La razón no es solo que sea referencia para `trades`.
La razón es que ya hemos observado una anomalía estructural real del universo:

- legible file a file
- no homogéneo en lectura dataset-style

En una frase:

- el auditor de `daily` debe validar tanto el contenido OHLCV como la salud estructural del parquet anual por ticker.

---

## 13. Cierre operativo alcanzado

La auditoría de `daily` ya queda aterrizada sobre el run full y cerrada para el universo `<1B>` filtrado desde ese run:

- `daily_v2_validation/daily_validate_2005_2026_d_full_v030`
- `daily_current.parquet`
- `validation_run_manifest.json`
- `materialization_summary.json`

Diagnóstico final alcanzado:

- `schema` es una anomalía estructural conocida y transversal
- el residuo económico relevante está concentrado en `vw_outside_range_*`
- el `severe` actual de `v030` mezcla dos cosas distintas:
  - borde de regla por `abs_max >= 1.0` con muy pocos días afectados
  - régimen persistente de iliquidez con barras planas o casi planas
- el núcleo duro real ya no es `vw`, sino:
  - `all_rows_invalid_after_parse`
  - `negative_or_zero_ohlc_rows`

Refinamiento operativo aplicado:

- `schema_only_or_other`
- `vw_edge_absmax_only`
- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `hard_invalid_parse_or_price`

Lectura clave:

- muchos `severe` de `v030` no son corrupción del file
- en nombres líquidos aparecen como 1-2 días aislados con gap absoluto alto pero ratio muy bajo
- en nombres ilíquidos aparecen como muchos días con `h == l` o barra casi plana, `n` muy bajo y `v` muy bajo, donde `vw` queda ligeramente fuera del rango del OHLC del día

Verificación en notebooks:

- `03_daily_root_cause_audit_notebook.ipynb` queda como notebook metodológico
- `04_daily_closeout.ipynb` queda como notebook ejecutivo final

Conclusión:

- `daily` `<1B>` queda ampliamente sano a nivel operativo
- no puede decirse literalmente que no tenga errores, porque persiste un tail pequeño de `hard_invalid_parse_or_price`
- sí puede decirse que el problema dominante ya no apunta a corrupción masiva de `daily`, sino a una mezcla de regla conservadora sobre `vw` e iliquidez extrema en ciertos años/tickers

Detalle adicional del tail duro `<1B>`:

- `102` files sobre `44,423`
- `19` parse-only
- `83` con `negative_or_zero_ohlc_rows`
- `70` son además `micro_price`
- `83` tienen `l_min = 0`

Verificación raw:

- hay files con precios absurdamente escalados y `v = 0`, `vw = NaN`
- hay files con OHLC todo-cero y volumen positivo

Eso confirma que el tail duro no es solo una clasificación conservadora, sino residuo real de datos inválidos.

Artefacto operativo dejado para exclusión directa:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_ticker_year.parquet`
- `summary`: `daily_lt1b_hard_invalid_exclusion_summary.json`

Cardinalidad:

- `102` files
- `102` `ticker-year`
- `54` tickers
