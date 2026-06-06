## Diseño de implementación `ohlcv_1m v2`

### Objetivo

Traducir el contrato de `ohlcv_1m` a una implementación v2 concreta, reproducible y paralela, sin backend legacy.

Artefactos objetivo:

- `050_ohlcv_1m_v2_validate_file.py`
- `051_ohlcv_1m_v2_inventory.py`
- `052_ohlcv_1m_v2_validate_batches.py`
- `053_ohlcv_1m_v2_materialize_current.py`

---

## 1. Unidad lógica y claves

### Unidad física

- un parquet mensual:
  - `minute_aggs_{ticker}_{year}_{month}.parquet`

### Unidad lógica

- `task_key = ticker|year|month`

### Claves mínimas

- `file`
- `task_key`
- `ticker`
- `year`
- `month`

---

## 2. `051_ohlcv_1m_v2_inventory.py`

### Función

Recorrer roots físicos de `ohlcv_1m`, encontrar todos los `minute_aggs_*.parquet`, derivar metadata estructural y persistir inventario incremental.

### Inputs

- `--d-root`
- `--outdir`
- `--batch-size`
- `--resume`
- opcional:
  - `--limit-per-root`

### Pattern esperado

Detectar paths tipo:

- `ticker={TICKER}\year={YYYY}\month={MM}\minute_aggs_{TICKER}_{YYYY}_{MM}.parquet`

### Columnas de `ohlcv_1m_inventory_files`

- `root`
- `root_path`
- `file`
- `relpath`
- `ticker`
- `year`
- `month`
- `filename_ticker`
- `filename_year`
- `filename_month`
- `task_key`
- `size_bytes`
- `mtime_utc`
- `inventory_seen_utc`

### Persistencia incremental

Debe escribir:

- `inventory_batches\inventory_batch_000001.parquet`
- `inventory_batches\inventory_batch_000002.parquet`
- ...

Y mantener:

- `inventory_checkpoint.json`
- `inventory_run_manifest.json`

### Outputs finales

- `ohlcv_1m_inventory_files.parquet`
- `ohlcv_1m_inventory_files.csv`
- `ohlcv_1m_inventory_by_ticker.parquet`
- `ohlcv_1m_inventory_by_ticker.csv`
- `ohlcv_1m_inventory_summary.json`

### Checks mínimos del summary

- rows por root
- tickers por root
- years min/max por root
- months min/max
- bytes totales
- `all_rows`
- `all_tickers`

---

## 3. `050_ohlcv_1m_v2_validate_file.py`

### Función

Validar un solo `minute_aggs_*.parquet` y devolver un evento estructurado.

### Inputs

- `--file`
- `--expected-root`
- `--run-id`
- `--batch-id`
- `--scan-reason`
- `--validation-kind`
- `--out-json`

Y parámetros de tolerancia:

- `--min-expected-price`
- `--min-active-days-warn`
- `--max-gap-days-warn`

### Capas de validación

#### Física

- file existe
- no 0 bytes
- `ParquetFile.read()` funciona

#### Estructural

- intentar `read_table(...)`
- si falla:
  - registrar:
    - `dataset_read_incompatible_schema`
    - `dataset_read_error`

#### Partición

Derivar y validar:

- `ticker_path`
- `year_path`
- `month_path`
- `filename_ticker`
- `filename_year`
- `filename_month`

#### Schema

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

#### Contenido

- rows > 0
- parseo de `ts_utc`
- parseo de `date`
- ticker único
- year único
- month único
- sin `ts_utc` duplicados
- fechas dentro del mes

#### OHLCV

- `o/h/l/c > 0`
- `v >= 0`
- `h >= max(o,c,l)`
- `l <= min(o,c,h)`
- `vw` dentro de rango cuando `v > 0`

#### Continuidad

Calcular:

- `date_min`
- `date_max`
- `rows_after_parse`
- `active_days`
- `active_minutes`
- `max_gap_days`

### Issues sugeridos

- `file_missing`
- `zero_byte_file`
- `parquet_unreadable`
- `invalid_partition_path`
- `partition_vs_filename_ticker_mismatch`
- `partition_vs_filename_year_mismatch`
- `partition_vs_filename_month_mismatch`
- `partition_vs_column_ticker_mismatch`
- `partition_vs_column_year_mismatch`
- `partition_vs_column_month_mismatch`
- `missing_required_columns`
- `zero_rows`
- `all_rows_invalid_after_parse`
- `multiple_tickers_in_file`
- `multiple_years_in_file`
- `multiple_months_in_file`
- `duplicate_ts_utc_in_file`
- `date_out_of_partition_month`
- `negative_or_zero_ohlc_rows`
- `negative_volume_rows`
- `high_low_inversion_rows`
- `vw_outside_range_rows`

### Warns sugeridos

- `dtype_mismatch`
- `dataset_read_incompatible_schema`
- `schema_merge_conflict_ticker_encoding`
- `suspicious_sparse_month`
- `large_internal_gap_days`
- `rows_lt_10`

### Salida por file

- `file`
- `ticker`
- `year`
- `month`
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

### Acción derivada

- `HARD_FAIL -> quarantine_and_retry`
- `SOFT_FAIL -> review_queue`
- `PASS -> accept_raw`

---

## 4. `052_ohlcv_1m_v2_validate_batches.py`

### Función

Leer `ohlcv_1m_inventory_files.parquet`, filtrar el universo objetivo, trocearlo en batches y validar en paralelo vía `050`.

### Inputs

- `--inventory-parquet`
- `--outdir`
- `--run-id`
- `--workers`
- `--chunk-size`
- `--root`
- `--ticker`
- `--year-from`
- `--year-to`
- `--month-from`
- `--month-to`
- `--limit`
- `--scan-reason`
- `--validation-kind`
- `--resume`

### Filtrado lógico

Permitir:

- por root
- por ticker
- por rango de años
- por rango de meses
- por límite de files

### Ejecución

1. leer inventario
2. filtrar
3. trocear en batches
4. ejecutar validación en paralelo
5. persistir cada batch como append-only
6. actualizar checkpoint y manifest

### Persistencia

- `events_batches\batch_000001.parquet`
- ...
- `validation_checkpoint.json`
- `validation_run_manifest.json`
- `batch_manifest_ohlcv_1m_v2.csv`
- `batch_manifest_ohlcv_1m_v2.parquet`
- `validation_run_summary.json`

### Campos mínimos de `batch_manifest`

- `batch_id`
- `files_selected`
- `events_written`
- `started_at_utc`
- `finished_at_utc`
- `severity_counts_json`

---

## 5. `053_ohlcv_1m_v2_materialize_current.py`

### Función

Leer solo batches confirmados por checkpoint/manifest, reconstruir el estado actual y exportar vistas contractuales.

### Inputs

- `--validation-outdir`
- `--inventory-parquet`
- `--run-id`
- `--outdir`

### Reconstrucciones requeridas

- `ohlcv_1m_current.parquet`
- `retry_current.parquet`
- `retry_frozen.parquet`

Y exports contractuales:

- `ohlcv_1m_agent_strict_events_current.csv`
- `retry_queue_ohlcv_1m_strict_current.csv`
- `retry_frozen_ohlcv_1m_strict.csv`
- `live_status_ohlcv_1m_strict.json`
- `materialization_summary.json`

---

## 6. Severidad inicial recomendada

### HARD_FAIL

- ilegibilidad física
- partición inválida
- columnas mínimas ausentes
- parseo completamente inválido
- múltiples tickers
- múltiples años
- múltiples meses
- `ts_utc` duplicado
- OHLC imposible

### SOFT_FAIL

- incompatibilidad dataset-style de schema
- conflicto `ticker string vs dictionary-encoded string`
- sparsity mensual
- gaps internos grandes
- `vw` fuera de rango

### PASS

- file legible
- schema contractual presente
- partición consistente
- sin issues duros

---

## 7. Orden de implementación

1. `050_ohlcv_1m_v2_validate_file.py`
2. `051_ohlcv_1m_v2_inventory.py`
3. `052_ohlcv_1m_v2_validate_batches.py`
4. `053_ohlcv_1m_v2_materialize_current.py`
5. notebook raíz de problemas `03_ohlcv_1m_root_cause_audit_notebook.ipynb`

---

## 8. Hallazgo inicial que ya debe quedar fijado

Antes de implementar nada más, queda fijado como hallazgo estructural de `ohlcv_1m`:

- `read_table(...)` falla sobre sample real
- `ParquetFile.read()` funciona
- el conflicto observado vuelve a recaer en `ticker`

Esto convierte a `ohlcv_1m` en un universo que debe auditar:

- legibilidad file-level
- homogeneidad estructural de schema

como dos capas distintas y explícitas.

# Ejecutamos

La secuencia que hemos ido siguiendo en daily y la que ya habíamos asentado en trades es, en esencia, esta:

```
1. definir contrato y muestra base

- leer files reales
- fijar unidad lógica auditada
- describir schema, partición, naming y expectativas

2. 050: validador de un file

- contrato estructural
- parseo
- checks de contenido
- severidad PASS/SOFT_FAIL/HARD_FAIL

3. 051: inventario físico

- qué files existen realmente
- task_key
- resumen por ticker
- artefacto reproducible

4. si el universo es grande: shardizar

- construir shards
- lanzar varios procesos
- mergear artefactos

5. 052: validación batch/full

- aplicar 050 sobre todo el inventario
- escribir batches append-only
- checkpoint + manifest + summary

6. 053: materialización current

- colapsar batches en artefactos operativos
- current, hard_fail, soft_fail, pass
- tablas resumidas para notebook y auditoría

7. 054+

- verify / smoke / controles de consistencia
- auditorías específicas
- span contiguity
- cruces contra universo/calendario
- comparativas entre datasets
- notebooks de análisis

En daily además hicimos después:

- 055: span contiguity por ticker
- 056: cruce contra universo + calendario
- 057: cruce <1B vs complete daily
- 058: clasificación de incompletos <1B
- 059+: colas de descarga y autopsias
- comparativas con 1m, quotes, trades
```

**Comenzamos con OHLV1m**


El validador `050_ohlcv_1m_v2_validate_file.py` ya está creado. Antes de seguir con 051, conviene hacer un smoke mínimo sobre el sample ZLS 2024-03
para ver si la semántica del contrato y la anomalía estructural salen como esperamos.

Script

```
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/050_ohlcv_1m_v2_validate_file.py
```

Qué hace ya:

```
- valida partición:
    - ticker|year|month
- intenta:
    - read_table(...)
    - ParquetFile.read()
- captura la anomalía estructural:
    - dataset_read_incompatible_schema
    - schema_merge_conflict_ticker_encoding
- valida:
    - ts_utc
    - date
    - year
    - month
    - duplicados ts_utc
    - OHLC
    - vw
    - densidad mensual
    - gap interno
```

El siguiente paso correcto es un smoke manual sobre el file que has dado. Lanza esto:

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\050_ohlcv_1m_v2_validate_file.py --file D:\ohlcv_1m\ticker=ZLS\year=2024\month=03\minute_aggs_ZLS_2024_03.parquet --expected-root D:\ohlcv_1m --run-id ohlcv_1m_manual_smoke --batch-id batch_manual_000001 --scan-reason manual_probe --validation-kind manual_validation
```

## inventario físico de ohlcv_1m

- recorre D:\ohlcv_1m
- encuentra todos los files:
    - minute_aggs_{ticker}_{year}_{month}.parquet
- valida que el path encaje con el patrón:
    - ticker={TICKER}\year={YYYY}\month={MM}\...
- extrae metadata sin abrir el contenido del parquet
- construye una fila de inventario por file mensual


Qué guarda por cada file


- root
- root_path
- file
- relpath
- ticker
- year
- month
- filename_ticker
- filename_year
- filename_month
- task_key = ticker|year|month
- size_bytes
- mtime_utc
- inventory_seen_utc


Qué artefactos produce


- ohlcv_1m_inventory_files.parquet
- ohlcv_1m_inventory_files.csv
- ohlcv_1m_inventory_by_ticker.parquet
- ohlcv_1m_inventory_by_ticker.csv
- ohlcv_1m_inventory_summary.json
- inventory_checkpoint.json
- inventory_run_manifest.json
- inventory_batches\inventory_batch_*.parquet


Qué deja:


- inventario por file mensual ticker|year|month
- ohlcv_1m_inventory_files.parquet/csv
- ohlcv_1m_inventory_by_ticker.parquet/csv
- ohlcv_1m_inventory_summary.json
- inventory_checkpoint.json
- inventory_run_manifest.json
- inventory_batches\inventory_batch_*.parquet

enumera jerárquicamente:
      - ticker=*
      - year=*
      - month=*
      - minute_aggs_*.parquet
  - mantiene el mismo contrato y los mismos outputs
  - añade filtros de smoke reales:
      - --ticker
      - --ticker-prefix
      - --max-tickers


Ya queda la línea paralela de inventario por shards:
```sh
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/051_ohlcv_1m_v2_inventory.py
- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/051b_ohlcv_1m_v2_build_inventory_shards.py
```
Qué he dejado:
```sh
- 051b construye shards de tickers a partir de D:\ohlcv_1m\ticker=*
- 051 ya acepta:
    - --tickers-parquet
    - --tickers-csv
- así cada terminal procesa solo su shard
- el contrato no cambia:
    - mismo inventario por file
    - mismo task_key = ticker|year|month
    - mismos outputs
```
**Paso 1. Construir shards**
```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051b_ohlcv_1m_v2_build_inventory_shards.py --d-root D:\ohlcv_1m --shards 8 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory
```
Eso te dejará algo como:
```sh
- tasks_ohlcv_1m_inventory.shard_01_of_08.parquet
- ...
- tasks_ohlcv_1m_inventory.shard_08_of_08.parquet
- ohlcv_1m_inventory_shards_manifest.json
```
**Paso 2. Lanzamientos paralelos reales**

Abre 4 u 8 terminales. Ejemplo con 4 primeros shards:

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_01_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_01_of_08 --resume


python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_02_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_02_of_08 --resume


python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_03_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_03_of_08 --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_04_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_04_of_08 --resume


python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_05_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_05_of_08 --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_06_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_06_of_08 --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_07_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_07_of_08 --resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_ohlcv_1m_v2_inventory.py --d-root D:\ohlcv_1m --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_08_of_08.parquet --batch-size 100000 --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_shard_08_of_08 --resume



```

y luego uno de los dos shards.

Lo siguiente correcto, cuando tengas al menos un shard terminado, es preparar el merge de inventarios shardizados en un artefacto full único. Si
quieres, te hago ese 051c_merge_ohlcv_1m_inventory_shards.py.

- cada shard produce un inventario completo de su trozo
- luego, si queremos el full único, se hace un merge posterior

Importante
No comparten outdir.
Cada shard debe escribir en su propio directorio.

Si compartieran outdir:

- pisarían checkpoint
- pisarían manifest
- y romperíamos reproducibilidad


**celda/comando para monitorizar los shards a la vez en una sola tabla**

- C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/run_monitor_ohlcv_1m_inventory_shards.ps1

Lanzadera:

```sh
powershell -NoProfile -ExecutionPolicy Bypass -File C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\run_monitor_ohlcv_1m_inventory_shards.ps1 -IntervalSec 5
```

```sh
base_dir=C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory
pattern=ohlcv_1m_inventory_shard_*_of_*
run_dirs=8
interval_sec=5


run_dir                           updated_utc                      persisted_rows_total batches_written next_batch_index active_root last_relpath finalized final_rows final_tickers
-------                           -----------                      -------------------- --------------- ---------------- ----------- ------------ --------- ---------- -------------
ohlcv_1m_inventory_shard_01_of_08 2026-04-03T18:14:40.496892+00:00               158950               2                3                               True     158950          1486
ohlcv_1m_inventory_shard_02_of_08 2026-04-03T18:14:41.153817+00:00               156172               2                3                               True     156172          1491
ohlcv_1m_inventory_shard_03_of_08 2026-04-03T18:14:38.948273+00:00               155085               2                3                               True     155085          1487
ohlcv_1m_inventory_shard_04_of_08 2026-04-03T18:14:41.397337+00:00               159207               2                3                               True     159207          1480
ohlcv_1m_inventory_shard_05_of_08 2026-04-03T18:32:14.749889+00:00               160264               2                3                               True     160264          1491
ohlcv_1m_inventory_shard_06_of_08 2026-04-03T18:32:13.409965+00:00               157695               2                3                               True     157695          1499
ohlcv_1m_inventory_shard_07_of_08 2026-04-03T18:32:14.115451+00:00               160467               2                3                               True     160467          1482
ohlcv_1m_inventory_shard_08_of_08 2026-04-03T18:32:15.144178+00:00               164164               2                3                               True     164164          1488


TOTAL
persisted_rows_total=1272004 | final_rows=1272004 | finalized=8/8 | running=0
```


Los 8 shards ya están cerrados y el siguiente paso ya está preparado.

  He creado:

  - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/051c_ohlcv_1m_v2_merge_inventory_shards.py

  Qué hace:

  - lee todos los ohlcv_1m_inventory_files.parquet de los shards
  - concatena
  - reconstruye:
      - ohlcv_1m_inventory_files.parquet/csv
      - ohlcv_1m_inventory_by_ticker.parquet/csv
      - ohlcv_1m_inventory_summary.json
  - además deja:
      - ohlcv_1m_inventory_duplicate_task_keys.parquet/csv
      - ohlcv_1m_inventory_shard_manifest.parquet/csv

  Así comprobamos que no haya colisiones entre shards.

  Lanzadera

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051c_ohlcv_1m_v2_merge_inventory_shards.py --base-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory --pattern "ohlcv_1m_inventory_shard_*_of_08" --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged
{
  "merged_at_utc": "2026-04-03T18:34:43.524110+00:00",
  "base_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory",
  "pattern": "ohlcv_1m_inventory_shard_*_of_08",
  "shards_found": 8,
  "merged_rows": 1272004,
  "merged_task_keys": 1272004,
  "merged_tickers": 11904,
  "duplicate_task_keys": 0,
  "year_min": 2005,
  "year_max": 2026,
  "month_min": 1,
  "month_max": 12,
  "total_bytes": 160255317441,
  "outputs": {
    "ohlcv_1m_inventory_files_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_files.parquet",
    "ohlcv_1m_inventory_files_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_files.csv",
    "ohlcv_1m_inventory_by_ticker_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_by_ticker.parquet",
    "ohlcv_1m_inventory_by_ticker_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_by_ticker.csv",
    "duplicate_task_keys_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_duplicate_task_keys.parquet",
    "duplicate_task_keys_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_duplicate_task_keys.csv",
    "shard_manifest_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_shard_manifest.parquet",
    "shard_manifest_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_shard_manifest.csv",
    "summary_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_summary.json"
  },
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged"
}
```

El merge quedó perfecto: *1,272,004 task keys y 0 duplicados*. Voy a clonar ahora la lógica estable de `052_daily_v2_validate_batches.py` hacia ohlcv_1m, manteniendo el mismo backend append-only y el mismo patrón de resume.

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_ohlcv_1m_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_smoke --run-id ohlcv_1m_validate_smoke --workers 1 --chunk-size 500 --root D --year-from 2024 --year-to 2026 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --resume
`` 

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_ohlcv_1m_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_full --run-id ohlcv_1m_validate_full --workers 1 --chunk-size 1000 --root D --scan-reason rescan_all --validation-kind normal_validation --resume
```

052 ya está listo:

  - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/052_ohlcv_1m_v2_validate_batches.py

  Qué hace:

  - lee el inventario merged
  - filtra por:
      - root
      - ticker
      - year_from/year_to
      - month_from/month_to
      - limit
  - valida cada file mensual con:
      - C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/050_ohlcv_1m_v2_validate_file.py
  - escribe batches append-only:
      - events_batches\batch_*.parquet
      - validation_checkpoint.json
      - validation_run_manifest.json
      - batch_manifest_ohlcv_1m_v2.csv/parquet
      - validation_run_summary.json

  Smoke recomendado
  Empieza con una muestra controlada. Como en este entorno el multiproceso puede dar guerra, usa --workers 1.

  python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_ohlcv_1m_v2_validate_batches.py --inventory-parquet C:
  \TSIS_Data\v1\backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --outdir C:
  \TSIS_Data\v1\backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_smoke --run-id ohlcv_1m_validate_smoke --workers 1
  --chunk-size 500 --root D --year-from 2024 --year-to 2026 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --resume

  Qué quiero ver cuando lo lances

  - selected_files
  - batches_written
  - severity_counts_total

  Si quieres, después preparo ya 053_ohlcv_1m_v2_materialize_current.py, pero primero conviene ver el smoke de 052.


› dame el lanzador para todos


• Sí. Para todo el universo merged de ohlcv_1m, usa este:
```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_ohlcv_1m_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_full --run-id ohlcv_1m_validate_full --workers 1 --chunk-size 1000 --root D --scan-reason rescan_all --validation-kind normal_validation --resume
[1/1273] batch_000001 files=1000 events=1000 counts={'SOFT_FAIL': 995, 'HARD_FAIL': 5}
[2/1273] batch_000002 files=1000 events=1000 counts={'SOFT_FAIL': 1000}
[3/1273] batch_000003 files=1000 events=1000 counts={'SOFT_FAIL': 1000}
[4/1273] batch_000004 files=1000 events=1000 counts={'SOFT_FAIL': 1000}
[1272/1273] batch_001272 files=1000 events=1000 counts={'SOFT_FAIL': 1000}
[1273/1273] batch_001273 files=4 events=4 counts={'SOFT_FAIL': 4}
{
  "run_id": "ohlcv_1m_validate_full",
  "validator_version": "ohlcv_1m_v2_validate_file/0.1.0",
  "started_at_utc": "2026-04-03T18:41:52.737554+00:00",
  "finished_at_utc": "2026-04-04T06:49:35.388279+00:00",
  "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\\ohlcv_1m_inventory_files.parquet",
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_validation\\ohlcv_1m_validate_full",
  "selected_files": 1272004,
  "workers": 1,
  "chunk_size": 1000,
  "batches_written": 1273,
  "severity_counts_total": {
    "SOFT_FAIL": 1268904,
    "HARD_FAIL": 3100
  },
  "filters": {
    "root": "D",
    "ticker": "",
    "year_from": "",
    "year_to": "",
    "month_from": "",
    "month_to": "",
    "limit": 0
  },
  "resume": true
}
```

Eso valida:

- todos los files del inventario merged
- sin limitar por ticker, año o mes

Nota práctica:

- te lo dejo con --workers 1 porque es la opción segura aquí
- si en tu terminal normal ves que multiproceso funciona, luego puedes subir a --workers 4 o 8

Cuando lo lances y termine, pégame el summary final y seguimos con 053_ohlcv_1m_v2_materialize_current.py.


**NOTA**

Podías haberlo hecho cde forma paralela así:

```sh
# Ahora ya puedes reutilizar los shards de 051b y lanzar 8 terminales. Ejemplo del shard 1:

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_ohlcv_1m_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --tickers-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_shards\20260403_shard_ohlcv_1m_inventory\tasks_ohlcv_1m_inventory.shard_01_of_08.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_shard_01_of_08 --run-id ohlcv_1m_validate_shard_01_of_08 --workers 1 --chunk-size 1000 --root D --scan-reason rescan_all --validation-kind normal_validation --resume

# Mi recomendación práctica:
#
# - no sigas invirtiendo tiempo en el full secuencial antiguo
# - relanza shardizado con los 8 shards ya construidos
# - --workers 1 por terminal ya te da paralelismo real y estable
# - si quieres, luego te doy las 8 lanzaderas exactas y un monitor .ps1 igual que el de inventario
```

## 053

Objetivo

Construir un artefacto operativo `current` a partir de los batches ya validados por `052`, sin esperar necesariamente a que el run full haya terminado.

Esto permite:

```
- trabajar ya con el estado actual de la validación
- consolidar el último evento por file mensual `ticker|year|month`
- materializar colas operativas de retry
- generar resúmenes por severidad, warning, issue, ticker, year y month
```

Script

```text
C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_ohlcv_1m_v2_materialize_current.py

### Qué hace

- lee los batches append-only de:
  - events_batches\batch_*.parquet
- usa manifest + checkpoint para saber qué batches están confirmados
- concatena los eventos ya materializados
- normaliza campos:
  - issues
  - warns
  - metrics_json
- deriva un snapshot current:
  - último evento por file
- enriquece current con metadata del inventario:
  - ticker
  - year
  - month
  - task_key
  - size_bytes
  - root / relpath
- construye:
  - retry_current
  - retry_frozen
- genera resúmenes:
  - severity_counts_current
  - issue_counts_current
  - warn_counts_current
  - by_ticker_current
  - by_year_current
  - by_month_current
- emite live status y summary de materialización
```

Input

```
- validation outdir de 052:
  - C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_full

- inventory parquet merged de 051c:
  -C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet
```

Output

```
- ohlcv_1m_current.parquet / csv
- retry_current.parquet / csv
- retry_frozen.parquet / csv
- severity_counts_current.parquet / csv
- issue_counts_current.parquet / csv
- warn_counts_current.parquet / csv
- by_ticker_current.parquet / csv
- by_year_current.parquet / csv
- by_month_current.parquet / csv
- live_status_ohlcv_1m_strict.json
- materialization_summary.json
```

Lanzadera

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_ohlcv_1m_v2_materialize_current.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_full --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full --run-id ohlcv_1m_current_full
```

**¿Es rápido o hace falta paralelizar?**

```
- normalmente es mucho más rápido que 052
- no revalida files
- no abre los parquets originales de datos
- solo lee:
  - batches ya generados
  - inventario
  - manifest / checkpoint
```

Conclusión práctica:
```
- no debería necesitar paralelización en la mayoría de casos
- sí puede tardar algo porque concatena muchos batches
- pero está en otra liga de coste frente a 052
```

Regla operativa:

```
- 052:
  - sí merece shardización / paralelismo
- 053:
  - normalmente no
  - se puede relanzar varias veces mientras 052 sigue corriendo

```


```sh

› PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_ohlcv_1m_v2_materialize_current.py
  --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation\ohlcv_1m_validate_full --inventory-parquet C:
  \TSIS_Data\v1\backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_files.parquet --outdir C:
  \TSIS_Data\v1\backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_partial --run-id ohlcv_1m_current_partial
  {
    "run_id": "ohlcv_1m_current_partial",
    "materialized_at_utc": "2026-04-04T06:33:49.570721+00:00",
    "validation_outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_validation\\ohlcv_1m_validate_full",
    "inventory_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_inventory\\ohlcv_1m_inventory_full_merged\
  \ohlcv_1m_inventory_files.parquet",
    "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_materialized\\ohlcv_1m_current_partial",
    "events_rows": 1238000,
    "current_rows": 1238000,
    "retry_current_rows": 1238000,
    "retry_frozen_rows": 0,
    "batches_read": 1238,
    "batches_read_names": [
      "batch_000001.parquet",
      "batch_000002.parquet",    "batch_001231.parquet",
      "batch_001232.parquet",
      "batch_001233.parquet",
      "batch_001234.parquet",
      "batch_001235.parquet",
      "batch_001236.parquet",
      "batch_001237.parquet",
      "batch_001238.parquet"
    ],
    "batches_skipped_names": [],
    "materialization_mode": "partial",
    "validation_completion_status": "partial",
    "validation_checkpoint_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_validation\\ohlcv_1m_validate_full\
  \validation_checkpoint.json",
    "validation_manifest_source": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\ohlcv_1m_v2_validation\\ohlcv_1m_validate_full\
  \validation_run_manifest.json"
  }

```


## Notebook `03_ohlcv_1m_root_cause_audit_notebook.ipynb`

```
C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/ohlcv_1m/03_ohlcv_1m_root_cause_audit_notebook.ipynb
```

1. **Problema estructural universal del universo 1m**

Casi todo el universo cae en warnings estructurales:

```
- dataset_read_incompatible_schema
- schema_merge_conflict_ticker_encoding
```

Esto significa:

```
- el file individual abre
- pero read_table() detecta heterogeneidad física de schema, sobre todo en ticker
- no es, por sí solo, una corrupción económica del contenido
```

La solución aplicada fue conceptual y operativa:
```
- dejar de interpretar ese bloque como “fallo blando ambiguo”
- convertirlo en bucket conocido
- separar:
    - schema_only
    - schema_plus_vw
```

Resultado:
```
- schema_only = 204,928
- schema_plus_vw = 1,063,976
```

**2. Problema económico adicional en schema_plus_vw**

Dentro del bloque estructural aparece además:

```
- vw_outside_range_rows
```

Esto significa:
```
- vw cae fuera de [low, high] en muchas filas
- pero los files no están vacíos ni muertos
- suelen tener actividad real, cobertura razonable y gaps moderados
```

La solución aplicada fue:

```
- no mezclar este bloque con corrupción dura
- tratarlo como “rescatable con flag económico”
- medirlo visualmente en el notebook con:
    - mediana de vw_outside_range_rows
    - p95
    - rows_after_parse
    - active_days
    - max_gap_days
    - buckets de cobertura y gaps
```

Resultado:

```
- se ve que es una señal extensa pero no equivalente a file roto
- por tanto no debe mandar todo a cuarentena
```


**3. Problema duro all_rows_invalid_after_parse**


Aquí el parquet abre, pero tras parsear:

```
- timestamps
- fechas
- numéricos
```
no queda ni una fila válida.

Eso sí es un fallo real de rescate:

```
- no hay base operativa útil
- no se puede confiar en ese file
```

La solución aplicada fue:

```
- clasificarlo como cuarentena dura
- separarlo explícitamente del resto en la nueva política operativa
```
Resultado:
```
- QUARANTINE_PARSE_INVALID = 3,049
```


**4. Problema duro negative_or_zero_ohlc_rows**

Aquí sí hay contenido parseable, pero existen filas con:

```
- o <= 0
- h <= 0
- l <= 0
- c <= 0
```

Eso rompe la validez económica básica del OHLC.

La solución aplicada fue:

```
- mantenerlo en cuarentena dura
- no intentar rescatarlo automáticamente
```

Resultado:

```
- QUARANTINE_PRICE_INVALID = 51
```


**5. Solución operativa final aplicada**

He añadido al notebook una política explícita de decisión:

```
- schema_only -> RESCUE_SCHEMA_ONLY
- schema_plus_vw -> RESCUE_SCHEMA_PLUS_VW
- all_rows_invalid_after_parse -> QUARANTINE_PARSE_INVALID
- negative_or_zero_ohlc_rows -> QUARANTINE_PRICE_INVALID
```

Resultado final:

```
- rescatado: 1,268,904 files (99.75629%)
- cuarentena: 3,100 files (0.24371%)
```

**6. Salida materializada**

Además de explicarlo visualmente en el notebook, dejé exports operativos:

```sh
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/
  rescue_soft_all.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/
  rescue_schema_only.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/
  rescue_schema_plus_vw.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/
  hard_quarantine.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/
  operational_decision_summary.parquet
```

La idea central es esta:

```
- antes todo parecía “universo casi entero en soft fail”
- ahora queda explicado y resuelto como:
    - un bloque estructural conocido y rescatable
    - un subbloque con señal vw que también es rescatable con flag
    - un núcleo pequeño de hard fail que sí debe salir fuera
```


**Cierre conceptual de 1m:**

```sh
- el problema final de 1m no era “universo roto”.
- era una mezcla de:
    - anomalía estructural universal de schema (dataset_read_incompatible_schema + schema_merge_conflict_ticker_encoding)
    - una señal económica extendida en vw
    - y un núcleo pequeño de HARD_FAIL real
- por eso pasamos a auditar 1m: porque daily ya había mostrado el patrón útil para abrir vw, y 1m estaba estancado tratando casi todo el universo
  como SOFT_FAIL indiferenciado.
- la auditoría de 1m permitió separar:
    - schema_only rescatable
    - schema_plus_vw rescatable con flag
    - HARD_FAIL real en cuarentena
```

Y ya he leído los cuatro artefactos de daily. El estado que dejan es este:

```sh
- daily tiene el mismo problema estructural de schema en ticker
- el notebook de daily ya avanzó más que 1m en la apertura de vw
- daily tiene comparativa v020 vs v030
- el foco allí parece ser cerrar la granularidad de vw_outside_range_rows y el subconjunto severo, además del bloque histórico de “57 no se movió nada tras la redescarga”
```

Cuando quieras, el siguiente paso lo hacemos sobre daily ya con este aprendizaje:

## Conclusión refinada sobre `ohlcv_1m`

La lectura correcta ya no es:

```sh
- "todo el problema de 1m es vw"
```

La lectura correcta es:

```sh
- el problema global de 1m no es solo `vw`
- pero, una vez separado el problema estructural de schema, el principal problema economico que queda si es `vw`
```

Las tres capas ya diferenciadas son:

### 1. Problema estructural universal

```sh
- `dataset_read_incompatible_schema`
- `schema_merge_conflict_ticker_encoding`
```

Esto explica el bloque:

```sh
- `RESCUE_SCHEMA_ONLY`
```

Lectura:

```sh
- es una anomalía de lectura / merge dataset-style
- por si sola no demuestra que el contenido OHLCV del file sea malo
```

### 2. Problema económico dominante dentro del bloque rescatable

```sh
- `vw_outside_range_rows`
```

Lectura:

```sh
- aquí está el frente económico importante de `1m`
- no es un detalle marginal
- dentro de `schema_plus_vw`, más de la mitad del bloque ya cae en una familia severa con masa grande
- por tanto `schema_plus_vw` no puede tratarse entero como "soft benigno"
```

### 3. Núcleo duro pequeño pero real

```sh
- `all_rows_invalid_after_parse`
- `negative_or_zero_ohlc_rows`
```

Lectura:

```sh
- esto sí es cuarentena dura
- no es un problema estadístico fino ni de redondeo
```

## Síntesis operativa

En una frase:

```sh
- `schema` = anomalía estructural conocida
- `vw` = problema económico dominante
- `parse/price invalid` = núcleo duro pequeño
```

Implicación:

```sh
- ya no hace falta seguir gastando esfuerzo en reexplicar el problema de schema
- el siguiente trabajo útil es abrir `vw_outside_range_rows` con la misma granularidad con la que se abrió `quotes`
- solo después podrá fijarse una política final `good / review / bad` para `ohlcv_1m`
```

## Apertura refinada de `schema_plus_vw`

La apertura ya no debe hacerse solo por presencia de `vw_outside_range_rows`.

La lectura útil salió al combinar:

```sh
- ratio de filas con `vw` fuera de rango
- masa absoluta de filas afectadas
- persistencia por día activo
- tamaño efectivo del file mensual
```

### Taxonomía refinada propuesta

```sh
- `vw_mild_low_ratio`
- `vw_moderate_ratio`
- `vw_severe_tiny_base`
- `vw_severe_small_mass`
- `vw_severe_large_mass_diffuse`
- `vw_severe_large_mass_persistent`
```

Resumen cuantitativo:

```sh
- `vw_mild_low_ratio`
    - files: 274,639
    - pct_of_schema_plus_vw: 25.81%
    - median_vw_ratio_pct: 0.236%
- `vw_moderate_ratio`
    - files: 119,875
    - pct: 11.27%
    - median_vw_ratio_pct: 3.16%
- `vw_severe_tiny_base`
    - files: 22,661
    - pct: 2.13%
    - median_rows_after_parse: 49
- `vw_severe_small_mass`
    - files: 81,272
    - pct: 7.64%
    - median_vw_ratio_pct: 9.94%
- `vw_severe_large_mass_diffuse`
    - files: 192,575
    - pct: 18.10%
    - median_vw_rows: 287
    - median_vw_per_active_day: 13.79
- `vw_severe_large_mass_persistent`
    - files: 372,954
    - pct: 35.05%
    - median_vw_rows: 1,113
    - median_vw_ratio_pct: 21.92%
    - median_vw_per_active_day: 53.43
```

### Lectura importante

La conclusión clave es esta:

```sh
- `schema_plus_vw` no es un bloque homogéneo
- más de la mitad del bloque cae en familias severas de masa grande
- por tanto no puede tratarse entero como "soft rescatable con flag" sin más
```

Y además:

```sh
- la familia `vw_severe_large_mass_persistent` no está concentrada en cuatro outliers
- aparece extendida a través de muchos tickers y años
- eso la convierte en un régimen económico real y no en una simple rareza local
```

### Lectura de `schema_only`

`schema_only` sí parece mucho más homogéneo:

```sh
- files: 204,928
- tickers: 6,466
- median_rows_after_parse: 471
- p90_rows_after_parse: 2,371
- median_active_days: 20
- median_gap_days: 4
```

Lectura:

```sh
- por ahora `schema_only` parece compatible con una lectura `good`
- el problema principal de cierre ya no está ahí
- el problema principal está dentro de `vw`
```

## Política preliminar `good / review / bad` para `ohlcv_1m`

Todavía no es el closeout final, pero la política preliminar ya puede formularse:

```sh
- `good`
    - `RESCUE_SCHEMA_ONLY`
    - `vw_mild_low_ratio`
- `review`
    - `vw_moderate_ratio`
    - `vw_severe_tiny_base`
    - `vw_severe_small_mass`
- `bad` o `review` muy fuerte
    - `vw_severe_large_mass_diffuse`
    - `vw_severe_large_mass_persistent`
    - `QUARANTINE_PARSE_INVALID`
    - `QUARANTINE_PRICE_INVALID`
```

Motivo:

```sh
- `good`: señal leve y compatible con uso controlado
- `review`: mezcla donde la anomalía existe pero todavía hay que decidir tolerancia según uso
- `bad`: masa grande y persistente o fallo duro de parse/precio
```
