  - [Agent02 Trades: estado actual, problemas observados y propuesta de rediseño](#agent02-trades-estado-actual-problemas-observados-y-propuesta-de-rediseño)
  - [1. Run de referencia](#1-run-de-referencia)
  - [2. Estado actual del run](#2-estado-actual-del-run)
  - [3. Conclusión operativa del estado actual](#3-conclusion-operativa-del-estado-actual)
  - [4. Archivos que gobiernan el estado de Agent02](#4-archivos-que-gobiernan-el-estado-de-agent02)
  - [5. Implementación objetivo de Agent02 v2](#5-implementacion-objetivo-de-agent02-v2)
    - [5.1. Inventario exacto](#51-inventario-exacto)
    - [5.2. Validación profunda por file](#52-validacion-profunda-por-file)
    - [5.3. Materialización current retry live](#53-materializacion-current-retry-live)
  - [6. Problemas lógicos y estructurales a evitar](#6-problemas-logicos-y-estructurales-a-evitar)
    - [6.1. Repetir el diseño legacy de quotes](#61-repetir-el-diseno-legacy-de-quotes)
    - [6.2. Auditar trades sin cruzar con OHLCV](#62-auditar-trades-sin-cruzar-con-ohlcv)
    - [6.3. Mezclar cobertura física con validez económica](#63-mezclar-cobertura-fisica-con-validez-economica)
    - [6.4. Inflación artificial de retry attempts](#64-inflacion-artificial-de-retry-attempts)
  - [7. Contrato de validación de market.parquet](#7-contrato-de-validacion-de-marketparquet)
    - [7.1. Schema observado](#71-schema-observado)
    - [7.2. Capas de validación](#72-capas-de-validacion)
    - [7.3. Salida correcta por file](#73-salida-correcta-por-file)
  - [8. Tablas maestras v2](#8-tablas-maestras-v2)
    - [8.1. trades_inventory_files](#81-trades_inventory_files)
    - [8.2. trades_validation_events](#82-trades_validation_events)
    - [8.3. trades_current](#83-trades_current)
  - [9. Orden recomendado de implementación](#9-orden-recomendado-de-implementacion)
  - [10. Estrategia de auditoría operativa recomendada](#10-estrategia-de-auditoria-operativa-recomendada)
  - [11. Veredicto técnico](#11-veredicto-tecnico)


## Agent02 Trades: estado actual, problemas observados y propuesta de rediseño

### 1. Run de referencia

El universo y cobertura de `trades_ticks` ya quedaron documentados en:

- `C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\00_auditoria_general.md`

La descarga operativa histórica de `trades_ticks` se apoyó en:

- `D:\trades_ticks_prod_2005_2026`
- `C:\TSIS_Data\data\trades_ticks_prod_2005_2026`

Y en la rama `<1B` quedaron materializados:

- `tasks_trades_lt_1b_master.csv`
- `tasks_trades_lt_1b_missing_only.csv`
- shards de descarga
- inventarios de ficheros finales

El objetivo ahora ya no es descargar.
El objetivo es construir el espejo de auditoría de `quotes`, pero para `trades`.

### 2. Estado actual del run

Según la auditoría general:

- existe inventario histórico de `trades_ticks`
- la descarga operativa ya terminó
- el volumen físico local es masivo
- hay cobertura material suficiente como para pasar a auditoría profunda file-level

Además, el universo `<1B` y el universo total `quotes + trades` ya se cruzaron previamente.

Por tanto:

- no estamos en fase de discovery de cobertura bruta
- estamos en fase de diseño de auditoría técnica reproducible

### 3. Conclusión operativa del estado actual

En `trades` la prioridad ya no es:

- bajar más datos

La prioridad es:

- definir el contrato de validación de `market.parquet`
- construir Agent02 v2 para `trades`
- materializar `current/retry/live`
- hacer a Agent03 capaz de interpretar el run

El cuello de botella esperado no será tanto la ausencia de datos, sino:

- decidir qué significa que un file de trades sea válido
- cruzarlo correctamente con `ohlcv_1m` y `ohlcv_daily`
- separar corrupción real de anomalía de microestructura o sesión

---

## 4. Archivos que gobiernan el estado de Agent02

En v2, dentro de un mismo `RUN_DIR`, los artefactos principales de `trades` deben ser:

- `live_status_trades_strict.json`
- `trades_agent_strict_events_current.csv`
- `retry_queue_trades_strict_current.csv`
- `retry_frozen_trades_strict.csv`
- `run_config_trades_strict.json`
- `batch_manifest_trades_strict.csv`
- `validation_checkpoint.json`
- `validation_run_manifest.json`
- `events_batches\batch_*.parquet`
- `materialization_summary.json`

Adicionalmente, para inventario:

- `trades_inventory_files.parquet`
- `trades_inventory_files.csv`
- `trades_inventory_by_ticker.parquet`
- `trades_inventory_by_ticker.csv`
- `trades_inventory_summary.json`

---

## 5. Implementación objetivo de Agent02 v2

### 5.1. Inventario exacto

La fase de inventario debe responder:

- qué `market.parquet` existen
- en qué root existen
- a qué `ticker,date` pertenecen
- qué tamaño tienen
- cuándo se observaron

No decide todavía si el file es bueno o malo.

### 5.2. Validación profunda por file

La fase de validación debe abrir cada `market.parquet` y decidir:

- `PASS`
- `SOFT_FAIL`
- `HARD_FAIL`

con reglas reproducibles y persistencia append-only por batch.

### 5.3. Materialización current retry live

La fase de materialización debe derivar desde el log append-only:

- `trades_current`
- `retry_current`
- `retry_frozen`
- `live_status`

y exportar vistas compatibles con Agent03.

---

## 6. Problemas lógicos y estructurales a evitar

### 6.1. Repetir el diseño legacy de quotes

No conviene reconstruir un Agent02 legacy equivalente al de `quotes`:

- CSV gigantes como backend vivo
- JSON gigantes como estado
- reconstrucción global repetida
- retry contaminado por reevaluaciones

En `trades` hay que nacer directamente en v2.

### 6.2. Auditar trades sin cruzar con OHLCV

En `quotes`, mucho del contrato sale del propio file.

En `trades`, eso no basta.

Si no cruzas con:

- `ohlcv_1m`
- `ohlcv_daily`

no puedes distinguir bien entre:

- corrupción real
- print raro pero posible
- sesión periférica
- desajuste por split o evento corporativo

### 6.3. Mezclar cobertura física con validez económica

Un `market.parquet` puede:

- existir físicamente
- estar bien particionado
- ser legible

y aun así ser:

- económicamente sospechoso
- inconsistente con `ohlcv_1m`
- incoherente con `ohlcv_daily`

Por eso:

- inventario
- validación
- current

deben quedar claramente separados.

### 6.4. Inflación artificial de retry attempts

La semántica correcta debe ser la misma que en `quotes`:

- `attempts` no cuenta relecturas
- `attempts` cuenta retry real
- `validation_kind` separa:
  - `normal_validation`
  - `retry_validation`
  - `revalidation_only`

---

## 7. Contrato de validación de market.parquet

### 7.1. Schema observado

En el file inspeccionado:

- `D:\trades_ticks_prod_2005_2026\KZR\year=2021\month=04\day=2021-04-07\market.parquet`

se observó:

- `ticker: string`
- `date: string`
- `timestamp: timestamp[us]`
- `price: double`
- `size: int64`
- `exchange: int64`
- `conditions: list<int64>`
- `year: int64`
- `month: int64`
- `day: string`

Ese schema debe ser la base del contrato mínimo.

### 7.2. Capas de validación

La validación correcta de un `market.parquet` debe seguir estas capas:

#### Capa 1. Validación física

- file existe
- `size_bytes > 0`
- parquet legible

#### Capa 2. Validación de partición

Derivar desde el path:

- `ticker_path`
- `year_path`
- `month_path`
- `day_path`

y contrastarlo con columnas:

- `ticker`
- `date`
- `year`
- `month`
- `day`

#### Capa 3. Validación de schema

Verificar:

- columnas mínimas requeridas
- tipos compatibles

#### Capa 4. Validación de contenido

Verificar:

- `rows > 0`
- `timestamp` parseable
- `price > 0`
- `size > 0`
- timestamps dentro del día esperado
- ticker constante en el file
- date constante en el file
- no todo inválido tras parseo

#### Capa 5. Métricas microestructurales de trades

Calcular como mínimo:

- `rows`
- `price_min`
- `price_max`
- `size_sum`
- `size_max`
- `exchange_nunique`
- `duplicate_exact_trade_rows`
- `duplicate_exact_trade_ratio_pct`
- `off_session_trade_pct`
- `max_trades_same_timestamp`

#### Capa 6. Validación cruzada con `ohlcv_1m`

Cruzar contra un file tipo:

- `D:\ohlcv_1m\ticker=EMA\year=2026\month=03\minute_aggs_EMA_2026_03.parquet`

Verificar:

- rango temporal observable
- compatibilidad `price_min/price_max` con `l/h`
- compatibilidad de volumen agregado
- compatibilidad razonable de intensidad de prints

#### Capa 7. Validación cruzada con `ohlcv_daily`

Cruzar contra un file tipo:

- `D:\ohlcv_daily\ticker=AACQ\year=2021\day_aggs_AACQ_2021.parquet`

Verificar:

- `price_min >= daily_low - tol`
- `price_max <= daily_high + tol`
- volumen agregado compatible
- `vwap_trades` compatible con `daily_vw`

#### Capa 8. Validación contextual

Añadir contexto:

- sesión
- splits
- eventos corporativos
- exchange concentration
- conditions patterns

### 7.3. Salida correcta por file

Cada validación debe producir, como mínimo:

- `file`
- `ticker`
- `date`
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

La clasificación final debe ser:

- `PASS`
- `SOFT_FAIL`
- `HARD_FAIL`

según el contrato detallado en:

- `01_contrato_agent02_agent03_trades_04012026.md`

---

## 8. Tablas maestras v2

## 8.1. trades_inventory_files

Una fila por file físico:

- `root`
- `file`
- `ticker`
- `date`
- `task_key`
- `size_bytes`
- `mtime_utc`

Rol:

- universo físico observado
- base para coverage exacta
- base para decidir qué abrir después

## 8.2. trades_validation_events

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

Rol:

- log append-only de validaciones
- fuente de verdad del estado evaluado
- base para reconstruir `current`, `retry` y `frozen`

## 8.3. trades_current

Una fila por file lógico actual:

- último estado vigente
- si está en `C`
- si está en `D`
- si está en ambos
- si pasa o no pasa

Rol:

- snapshot operativo derivado
- equivalente contractual moderno de:
  - `trades_agent_strict_events_current.csv`

---

## 9. Orden recomendado de implementación

El orden correcto para `trades` sería:

1. fijar contrato de validación de `market.parquet`
2. construir `051_trades_v2_inventory.py`
3. construir `050_trades_v2_validate_file.py`
4. construir `052_trades_v2_validate_batches.py`
5. construir `053_trades_v2_materialize_current.py`
6. correr smoke sobre universo acotado
7. construir Agent03 Trades
8. escalar a full

No conviene empezar por:

- dashboards
- causalidad
- GO/NO-GO

sin haber fijado antes:

- inventario
- contrato de validación
- persistencia incremental

---

## 10. Estrategia de auditoría operativa recomendada

No abriría todo el histórico completo de golpe.

Primero haría:

1. universo objetivo acotado
   - por ejemplo root `D`
   - ventana temporal concreta
   - límite de files

2. smoke de validación profunda

3. materialización `current/retry/live`

4. lectura humana con Agent03

5. solo después escalar a histórico amplio

En `trades`, el orden correcto es:

- primero cobertura física
- luego validez técnica
- luego coherencia contra `ohlcv_1m/daily`
- después interpretación humana

---

## 11. Veredicto técnico

`trades` no debe copiar el contenido analítico de `quotes`.

Sí debe copiar su arquitectura:

- Agent02 produce verdad técnica file-level
- Agent03 produce legibilidad operacional y analítica humana
- backend incremental
- append-only por batch
- materialización `current/retry/live`
- compatibilidad contractual estable

La diferencia está en el contrato de validación:

- `quotes` gira alrededor de bid/ask
- `trades` gira alrededor de:
  - `price`
  - `size`
  - `timestamp`
  - `exchange`
  - `conditions`
  - coherencia con `ohlcv_1m`
  - coherencia con `ohlcv_daily`

En una frase:

- el espejo correcto de `quotes` a `trades` es arquitectónico, no literal
