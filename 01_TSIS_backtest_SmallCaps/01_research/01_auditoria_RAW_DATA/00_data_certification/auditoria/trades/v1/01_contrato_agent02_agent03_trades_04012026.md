## Contrato de datos entre Agent02 y Agent03 para Trades

### Objetivo

Definir de forma explícita la interfaz de datos entre:

- Agent02
- Agent03

dentro de un mismo `RUN_DIR` del pipeline de `trades_ticks`.

Este contrato describe:

- qué artefactos publica Agent02
- qué artefactos consume Agent03
- qué significado tiene cada artefacto
- qué parte es fuente de verdad
- qué parte es materialización de compatibilidad
- cómo se define la validez de un `market.parquet`
- qué papel analítico cumple Agent03 sobre los outputs de Agent02

No redefine la lógica interna completa de descarga ni la lógica completa de investigación posterior fuera de este pipeline.

---

## 1. Ámbito y directorio de intercambio

Todos los artefactos se leen y escriben dentro de un mismo:

- `RUN_DIR`

Ejemplo esperado en v2:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\<run_name>`

La interfaz contractual entre Agent02 y Agent03 se considera local a ese `RUN_DIR`.

---

## 2. Modelo contractual v2

### 2.1. Fuente de verdad operativa

En Agent02 v2, la fuente de verdad operativa deja de ser:

- CSV grandes
- JSON grandes
- estado reconstruido por reescritura completa

y pasa a ser:

- Parquet append-only para eventos batch
- checkpoint y manifest de validate
- materialización derivada de current/retry/live

### 2.2. Materializaciones de compatibilidad

Los siguientes artefactos siguen existiendo en `RUN_DIR`, pero dejan de ser backend primario y pasan a ser:

- materializaciones derivadas
- exports de compatibilidad
- vistas consumibles por notebooks, monitores y Agent03

Artefactos obligatorios de compatibilidad:

- `trades_agent_strict_events_current.csv`
- `retry_queue_trades_strict_current.csv`
- `retry_frozen_trades_strict.csv`
- `live_status_trades_strict.json`
- `run_config_trades_strict.json`
- `batch_manifest_trades_strict.csv`

### 2.3. Regla general

Agent02 v2 puede cambiar completamente por dentro siempre que:

- mantenga el contrato semántico de validación por file
- mantenga las materializaciones visibles consumidas por Agent03
- mantenga estabilidad en claves, nombres y significado observable

---

## 3. Artefactos publicados por Agent02

## 3.1. `trades_agent_strict_events_current.csv`

### Rol

Snapshot actual de validación strict por file.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- `file`

### Semántica

Representa el último evento vigente conocido por file dentro del run.

No es:

- historial completo
- log append-only

Sí es:

- una vista current derivada desde el backend incremental

### Columnas mínimas obligatorias

- `file`
- `severity`
- `issues`
- `warns`
- `action`
- `processed_at_utc`
- `run_id`

### Columnas v2 recomendadas

- `validator_version`
- `scan_reason`
- `validation_kind`
- `ticker`
- `date`
- `rows`
- `metrics_json`

### Uso contractual

- input principal de Agent03
- input de notebooks de monitorización
- input de supervisor

---

## 3.2. `retry_queue_trades_strict_current.csv`

### Rol

Snapshot actual de files pendientes de retry o revisión activa.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- `file`

### Semántica

Subset del estado current que contiene files retryables y aún activos.

Debe excluir:

- files cerrados
- files frozen
- files ya resueltos

### Columnas mínimas obligatorias

- `file`
- `severity`
- `issues`
- `warns`
- `action`
- `processed_at_utc`

### Columnas v2 recomendadas

- `validator_version`
- `scan_reason`
- `validation_kind`
- `retry_attempts_effective`

### Uso contractual

- input de Agent03
- input de monitores
- input de supervisor
- cola operativa de retry

---

## 3.3. `retry_frozen_trades_strict.csv`

### Rol

Snapshot actual de files congelados fuera de retry activo.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- `file`

### Semántica

Contiene files que:

- son problemáticos o retryables
- superaron la política de retry activa
- no deben seguir en `retry_current` salvo acción explícita

### Columnas mínimas obligatorias

- `file`
- `severity`
- `issues`
- `warns`
- `processed_at_utc`

### Columnas v2 recomendadas

- `retry_attempts_effective`
- `freeze_reason`
- `validator_version`
- `validation_kind`

### Uso contractual

- input de revisión en Agent03
- diagnóstico y priorización

---

## 3.4. `live_status_trades_strict.json`

### Rol

Resumen live o último estado conocido del run.

### Tipo

Snapshot escalar, no tabular.

### Semántica

Debe resumir el estado observable del run en el momento de materialización.

### Campos mínimos obligatorios

- `run_id`
- `updated_utc`
- `files_discovered_total`
- `files_pending`
- `files_current_snapshot`
- `severity_counts_current`
- `retry_pending_files_current`

### Campos recomendados

- `materialization_utc`
- `backend_mode`
- `current_materialized_from`
- `retry_materialized_from`
- `validation_checkpoint_source`
- `validation_manifest_source`
- `validation_completion_status`
- `materialization_scope`

### Uso contractual

- monitorización
- supervisor
- visualización ligera
- notebooks

---

## 3.5. `run_config_trades_strict.json`

### Rol

Configuración efectiva del run.

### Tipo

Snapshot escalar de configuración.

### Semántica

Refleja la configuración activa con la que Agent02 ejecuta la validación del run.

### Uso contractual

- input de Agent03
- reproducibilidad
- auditoría técnica
- handoff operativo

---

## 3.6. `batch_manifest_trades_strict.csv`

### Rol

Manifest del lote operativo más reciente o del lote objetivo materializado.

### Unidad lógica

- una fila por batch

### Clave primaria lógica

- `batch_id`

### Semántica

Describe el conjunto de batches considerados en la materialización o lote operativo correspondiente.

### Columnas mínimas obligatorias

- `batch_id`
- `batch_path`
- `files_selected`
- `events_written`

### Columnas recomendadas

- `severity_counts_json`
- `materialized_at_utc`

### Uso contractual

- input de Agent03
- monitorización
- reconciliación de cobertura y missing

---

## 4. Contrato de validación de un file `market.parquet`

### 4.1. Objetivo

Definir de forma explícita cómo Agent02 v2 decide si un `market.parquet` es:

- `PASS`
- `SOFT_FAIL`
- `HARD_FAIL`

y qué evidencia mínima debe persistir por file.

La validez del file no depende del backend de estado.
El backend solo persiste el resultado.
La decisión la toma el contrato de validación.

### 4.2. Unidad de validación

La unidad lógica primaria es:

- `file`

Ejemplo:

- `D:\trades_ticks_prod_2005_2026\KZR\year=2021\month=04\day=2021-04-07\market.parquet`

Cada file debe producir exactamente un resultado de validación por evento de ejecución.

### 4.3. Schema observado y columnas mínimas obligatorias

Según el file inspeccionado:

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

Columnas mínimas obligatorias:

- `ticker`
- `date`
- `timestamp`
- `price`
- `size`
- `exchange`
- `conditions`
- `year`
- `month`
- `day`

### 4.4. Capa 1. Validación física

#### Checks obligatorios

- el file existe
- `size_bytes > 0`
- el parquet se puede abrir sin excepción

#### Fallos asociados

- `file_missing`
- `zero_byte_file`
- `parquet_unreadable`

#### Severidad esperada

- cualquier fallo de esta capa implica:
  - `HARD_FAIL`

### 4.5. Capa 2. Validación de partición

#### Objetivo

Comprobar que el path físico identifica correctamente:

- `ticker`
- `year`
- `month`
- `day`

#### Patrón esperado

- `{root}\{ticker}\year=YYYY\month=MM\day=YYYY-MM-DD\market.parquet`

#### Checks obligatorios

Debe poder derivarse desde el path:

- `ticker_path`
- `year_path`
- `month_path`
- `day_path`

Y además debe ser consistente con columnas:

- `ticker`
- `date`
- `year`
- `month`
- `day`

#### Fallos asociados

- `invalid_partition_path`
- `missing_partition_component`
- `partition_vs_column_ticker_mismatch`
- `partition_vs_column_date_mismatch`
- `partition_vs_column_year_mismatch`
- `partition_vs_column_month_mismatch`

#### Severidad esperada

- cualquier fallo fuerte de partición implica:
  - `HARD_FAIL`

### 4.6. Capa 3. Validación de schema

#### Objetivo

Verificar que el parquet contiene el esquema mínimo requerido para ser interpretable por el pipeline.

#### Checks obligatorios

- todas las columnas mínimas existen
- los tipos son compatibles con el contrato esperado

#### Compatibilidad de tipos esperada

- `ticker`
  - string compatible
- `date`
  - string compatible
- `timestamp`
  - timestamp o compatible temporal
- `price`
  - float o double compatible
- `size`
  - entero compatible
- `exchange`
  - entero compatible
- `conditions`
  - lista de enteros o compatible
- `year`
  - entero compatible
- `month`
  - entero compatible
- `day`
  - string compatible

#### Fallos asociados

- `missing_required_columns`
- `dtype_mismatch`

#### Severidad esperada

- `missing_required_columns`
  - `HARD_FAIL`
- `dtype_mismatch`
  - `SOFT_FAIL` por defecto
  - salvo que rompa semánticamente la lectura

### 4.7. Capa 4. Validación de contenido base

#### Objetivo

Verificar que las filas del parquet son coherentes y defendibles como trades.

#### Checks obligatorios

- `rows > 0`
- `timestamp` parseable
- `price` parseable
- `size` parseable
- `price > 0`
- `size > 0`
- timestamps dentro del día esperado por partición
- `ticker` constante dentro del file
- `date` constante dentro del file
- dataset no vacío tras parseo

#### Fallos asociados

- `zero_rows`
- `all_rows_invalid_after_parse`
- `negative_or_zero_price_rows`
- `negative_or_zero_size_rows`
- `timestamp_out_of_partition_day`
- `multiple_tickers_in_file`
- `multiple_dates_in_file`

#### Severidad esperada

- estos fallos implican:
  - `HARD_FAIL`

### 4.8. Capa 5. Métricas microestructurales de trades

#### Objetivo

Cuantificar si el file contiene señales de deterioro o anomalía operativa.

#### Métricas mínimas a calcular

- `rows`
- `price_min`
- `price_max`
- `size_sum`
- `size_max`
- `timestamp_min_utc`
- `timestamp_max_utc`
- `exchange_nunique`
- `conditions_nonempty_pct`
- `duplicate_exact_trade_rows`
- `duplicate_exact_trade_ratio_pct`
- `max_trades_same_timestamp`
- `off_session_trade_pct`

#### Warnings o issues asociados

- `duplicate_exact_trade_rows_present`
- `off_session_trades_present`
- `single_print_file`
- `extreme_size_outlier`
- `suspicious_exchange_concentration`

#### Severidad esperada

- warnings leves:
  - `SOFT_FAIL`
- anomalías extremas demostrables:
  - `HARD_FAIL`

### 4.9. Capa 6. Validación cruzada con `ohlcv_1m`

#### Objetivo

Cruzar los trades del `ticker,date` con el agregado de 1 minuto.

Schema observado de referencia:

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

#### Checks recomendados

- trades dentro del rango temporal observado por `ohlcv_1m`
- `price_min` no cae muy por debajo de `l` agregado esperado
- `price_max` no excede gravemente `h` agregado esperado
- `sum(size)` del file compatible con volumen agregado del día/minuto
- número de prints y volumen compatibles con `n` y `v` cuando sea defendible

#### Warnings o issues asociados

- `trade_price_outside_1m_range`
- `trades_volume_vs_1m_volume_mismatch`
- `trades_count_vs_1m_count_mismatch`
- `missing_ohlcv_1m_reference`

#### Severidad esperada

- ausencia de referencia:
  - warning contextual
- incompatibilidad extrema y repetida:
  - `HARD_FAIL`

### 4.10. Capa 7. Validación cruzada con `ohlcv_daily`

#### Objetivo

Cruzar el file contra el agregado diario.

Schema observado de referencia:

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

#### Checks recomendados

- `price_min >= daily_low - tol`
- `price_max <= daily_high + tol`
- `sum(size)` compatible con `daily_volume`
- `vwap_trades` compatible con `daily_vw`

#### Warnings o issues asociados

- `trade_price_outside_daily_range`
- `trades_volume_vs_daily_volume_mismatch`
- `trades_vwap_vs_daily_vw_mismatch`
- `missing_ohlcv_daily_reference`

#### Severidad esperada

- referencia ausente:
  - warning contextual
- incompatibilidad fuerte:
  - `HARD_FAIL`

### 4.11. Capa 8. Validación contextual

#### Objetivo

Añadir contexto explicativo sin mezclar causalidad con la validez base del file.

#### Contexto opcional enriquecido

- cercanía a split
- cercanía a ticker change
- sesión:
  - premarket
  - market
  - afterhours
- distribución de `conditions`
- distribución de `exchange`

#### Regla

Esta capa no debe cambiar por sí sola un `PASS` a `HARD_FAIL` salvo que exista una regla explícita aprobada.

Su función principal es:

- explicabilidad
- priorización
- soporte a Agent03

### 4.12. Política de clasificación final

#### HARD_FAIL

Asignar `HARD_FAIL` si existe al menos un issue duro, incluyendo:

- `file_missing`
- `zero_byte_file`
- `parquet_unreadable`
- `invalid_partition_path`
- `missing_required_columns`
- `zero_rows`
- `all_rows_invalid_after_parse`
- `negative_or_zero_price_rows`
- `negative_or_zero_size_rows`
- `timestamp_out_of_partition_day`
- `multiple_tickers_in_file`
- `multiple_dates_in_file`
- `trade_price_outside_daily_range` severo
- `trade_price_outside_1m_range` severo

#### SOFT_FAIL

Asignar `SOFT_FAIL` si no existe `HARD_FAIL` pero sí warnings, incluyendo:

- `dtype_mismatch`
- `duplicate_exact_trade_rows_present`
- `off_session_trades_present`
- `single_print_file`
- `missing_ohlcv_1m_reference`
- `missing_ohlcv_daily_reference`

#### PASS

Asignar `PASS` si:

- no hay issues
- no hay warnings
- el file es estructural y económicamente coherente bajo el contrato actual

### 4.13. Acción operativa por severidad

#### Para PASS

- `accept_raw`

#### Para SOFT_FAIL

- `review_queue`
- o `accept_with_warning` si se define whitelist explícita

#### Para HARD_FAIL

- `quarantine_and_retry`
- o `review_queue` según política del run

### 4.14. Salida obligatoria por file

Cada validación de file debe producir como mínimo:

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

---

## 5. Backend interno y modelo de datos de Agent02 v2

### 5.1. Log append-only

Agent02 v2 debe persistir un log append-only de eventos batch.

#### Unidad lógica

- una fila por evento de validación

#### Clave lógica del evento

- `file + processed_at_utc + batch_id`

#### Columnas mínimas

- `file`
- `processed_at_utc`
- `severity`
- `issues`
- `warns`
- `action`
- `validator_version`
- `run_id`
- `batch_id`
- `scan_reason`
- `validation_kind`

### 5.2. Query layer

La capa de materialización actúa como:

- catálogo de eventos
- capa de current
- capa de retry
- capa de frozen
- capa de live materialization

### 5.3. Clave primaria lógica de estado

La clave primaria lógica para current, retry y frozen es:

- `file`

### 5.4. Tabla `trades_inventory_files`

#### Rol

Representa el inventario físico observado de files `market.parquet`.

#### Unidad lógica

- una fila por file físico

#### Clave primaria lógica

- `file`

#### Columnas mínimas obligatorias

- `root`
- `file`
- `ticker`
- `date`
- `task_key`
- `size_bytes`
- `mtime_utc`

### 5.5. Tabla `trades_validation_events`

#### Rol

Representa el log append-only de validaciones de files.

#### Unidad lógica

- una fila por evento de validación

#### Clave lógica del evento

- `file + processed_at_utc + batch_id`

#### Columnas mínimas obligatorias

- `file`
- `processed_at_utc`
- `severity`
- `issues`
- `warns`
- `action`
- `validator_version`
- `run_id`
- `batch_id`
- `scan_reason`
- `validation_kind`

### 5.6. Tabla `trades_current`

#### Rol

Representa el último estado vigente por file.

#### Unidad lógica

- una fila por file lógico actual

#### Clave primaria lógica

- `file`

#### Compatibilidad contractual

Debe poder materializar:

- `trades_agent_strict_events_current.csv`

### 5.7. Tabla `retry_current`

#### Rol

Representa la cola activa de retry.

#### Compatibilidad contractual

Debe poder materializar:

- `retry_queue_trades_strict_current.csv`

### 5.8. Tabla `retry_frozen`

#### Rol

Representa files retirados del retry activo.

#### Compatibilidad contractual

Debe poder materializar:

- `retry_frozen_trades_strict.csv`

---

## 6. Consumo contractual de Agent03

Agent03 consume desde el mismo `RUN_DIR` los siguientes artefactos:

- `trades_agent_strict_events_current.csv`
- `retry_queue_trades_strict_current.csv`
- `retry_frozen_trades_strict.csv`
- `run_config_trades_strict.json`
- `batch_manifest_trades_strict.csv`

Adicionalmente, en algunos flujos de monitorización y visualización consume:

- `live_status_trades_strict.json`

### Regla

Mientras Agent03 y los notebooks actuales sigan dependiendo de esos nombres y esa semántica, Agent02 v2 debe seguir materializando esos outputs.

---

## 7. Rol analítico de Agent03 y significado de sus visualizaciones

### 7.1. Objetivo funcional de Agent03

Agent03 no sustituye a Agent02 ni revalida los archivos raw desde cero.

Su función es:

- consumir el estado ya producido por Agent02
- agregarlo por ticker, fecha, causa y severidad
- convertirlo en una lectura humana operativa
- soportar decisiones de:
  - cobertura
  - calidad
  - prioridad de revisión
  - cierre o no cierre del run
  - formulación de hipótesis causales

En términos funcionales:

- Agent02 produce estado técnico file a file
- Agent03 transforma ese estado en diagnóstico humano interpretable

### 7.2. Qué no hace Agent03

Agent03 no es:

- el motor primario de validación raw
- la fuente de verdad del run
- el responsable de clasificar el file por primera vez

Agent03 parte de un supuesto fuerte:

- Agent02 ya materializó un snapshot current coherente por file

---

## 8. Arquitectura conceptual de Agent03 Trades

Las visualizaciones y tablas de Agent03 Trades se organizan en cinco capas analíticas.

### 8.1. Capa de cobertura y causas

Debe responder:

- qué parte del universo esperado está cubierta
- qué parte tiene `PASS/SOFT/HARD`
- qué causa domina por ticker

### 8.2. Capa de diagnóstico visual legible

Debe presentar:

- top causas
- top tickers problemáticos
- distribución temporal de problemas

### 8.3. Capa de ejemplos concretos

Debe bajar de la agregación a files representativos:

- por issue dominante
- por ticker
- por sesión

### 8.4. Capa de severidad cuantitativa de trades

Debe cuantificar:

- desvíos frente a `ohlcv_1m`
- desvíos frente a `ohlcv_daily`
- duplicados
- outliers de precio
- outliers de tamaño
- off-session anomalies

### 8.5. Capa de decisión GO / NO-GO

Debe reducir el estado del run a una decisión operativa:

- `GO`
- `NO-GO`
- `NO_CLOSE_RETRY_PENDING`

### 8.6. Capa de hipótesis causal

Debe cruzar los files problemáticos con:

- splits
- `ohlcv_1m`
- `ohlcv_daily`
- sesiones
- exchange
- conditions

---

## 9. Resumen contractual mínimo

### Fuente de verdad v2

- Parquet append-only de eventos
- checkpoint y manifest de validate

### Materializaciones obligatorias de compatibilidad

- `trades_agent_strict_events_current.csv`
- `retry_queue_trades_strict_current.csv`
- `retry_frozen_trades_strict.csv`
- `live_status_trades_strict.json`
- `run_config_trades_strict.json`
- `batch_manifest_trades_strict.csv`

### Agent02 publica

- estado current por file
- retry current por file
- retry frozen por file
- estado live
- config del run
- manifest operativo del lote

### Agent03 consume

- current
- retry current
- retry frozen
- run config
- batch manifest
- opcionalmente live status

### Interfaz compartida

- mismo `RUN_DIR`
- mismos nombres de artefacto
- misma semántica observable
- backend interno libre, siempre que mantenga compatibilidad contractualmente visible




# Nota De Cambio De Contrato: `trade_price_outside_daily_range`

  ## Regla que cambia

  Hasta `050_trades_v2_validate_file.py` `v0.1.0`, la regla era:

  - si un `market.parquet` cae en `trade_price_outside_daily_range`
  - entonces el file se clasifica como `HARD_FAIL`
  - salvo algunos casos ya degradados por heurística de `possible_corporate_action_scale_mismatch`

  La propuesta de cambio es:

  - `trade_price_outside_daily_range` deja de ser `HARD_FAIL` automatico
  - primero debe clasificarse en subtipos
  - los casos con desalineacion consistente de escala pasan a `SOFT_FAIL`
  - `HARD_FAIL` queda reservado para:
    - ruptura de rango sin explicacion de escala
    - o combinado con senales estructurales adicionales

  ## Por qué cambia

  El smoke `trades_validate_q1_2024_d_smoke` mostró que:

  - `1789` files quedaron como `HARD_FAIL`
  - `1786` de esos `1789` se explican por una sola regla:
    - `trade_price_outside_daily_range`

  Eso indica que el validador no esta detectando “muchos tipos de corrupcion”.
  Indica que una unica regla esta dominando el resultado del smoke.

  La auditoria visual y cuantitativa posterior mostró que una parte relevante de esos casos no parece corrupcion interna de
  `market.parquet`, sino desalineacion entre:

  - `trades`
  - `ohlcv_daily`
  - `ohlcv_1m`

  En varios ejemplos, `daily` y `1m` estan alineados entre si, mientras que `trades` aparece en otra escala estable.

  ## Evidencia visual que lo justificó

  ### Caso forense representativo

  En el caso `AQMS 2024-03-21` se observó:

  - `trades` alrededor de `0.48`
  - `ohlcv_daily` alrededor de `96`
  - `ohlcv_1m` alrededor de `96`
  - `outside_daily_pct = 100%`

  Métricas observadas:

  - `possible_price_scale_factor_vs_daily ≈ 0.0050`
  - `possible_price_scale_factor_vs_1m ≈ 0.0050`
  - `trade_volume_vs_daily_ratio ≈ 206`
  - `trade_volume_vs_1m_ratio ≈ 210`

  Eso muestra un patrón compatible con:

  - fuerte desalineacion de escala
  - precio dividido aproximadamente por `200`
  - volumen multiplicado aproximadamente por `200`

  La figura forense mostró:

  - `trades` coherentes entre sí en una banda baja
  - `daily` y `1m` coherentes entre sí en una banda alta
  - incompatibilidad de escala entre ambos bloques
  - no un pequeño escape marginal del rango

  ### Evidencia agregada del smoke

  La clasificación agregada de `trade_price_outside_daily_range` mostró tres poblaciones:

  - `scale_mismatch_strong`
  - `true_outside_range_without_scale_shift`
  - `other_reference_break`

  La revisión posterior del bucket `other_reference_break` mostró que gran parte de ese grupo seguía alineado en diagonales de:

  - `possible_price_scale_factor_vs_daily` vs `possible_price_scale_factor_vs_1m`
  - `trade_volume_vs_daily_ratio` vs `trade_volume_vs_1m_ratio`

  Eso sugiere que el clasificador actual infra-detecta casos de escalado y los deja indebidamente en buckets no explicados.

  En particular, el subtipo dominante `mixed_other_break` presentó medianas como:

  - `median_pf_daily ≈ 0.0125`
  - `median_pf_1m ≈ 0.0125`
  - `median_vol_daily ≈ 79.9`
  - `median_vol_1m ≈ 87.7`

  Eso es consistente con una desalineacion sistematica de escala, no con ruido aleatorio.

  ## Impacto esperado sobre severidades

  El impacto esperado del cambio es:

  - reducir materialmente el número de `HARD_FAIL`
  - aumentar el número de `SOFT_FAIL`
  - mantener `PASS` aproximadamente estable
  - concentrar los `HARD_FAIL` en casos realmente estructurales

  Esperado en términos cualitativos:

  - casos con mismatch de escala:
    - `HARD_FAIL -> SOFT_FAIL`
  - casos de rango roto en la misma escala:
    - permanecen como `HARD_FAIL`
  - casos con schema roto, timestamps fuera de día, precios/tamaños imposibles:
    - permanecen como `HARD_FAIL`

  ## Principio de implementación

  La nueva lógica no debe depender de una lista cerrada de factores como:

  - `1/10`
  - `1/20`
  - `1/200`

  Debe detectar escalado probable por coherencia conjunta entre:

  - `possible_price_scale_factor_vs_daily`
  - `possible_price_scale_factor_vs_1m`
  - `trade_volume_vs_daily_ratio`
  - `trade_volume_vs_1m_ratio`

  Criterio conceptual:

  - si `daily` y `1m` apuntan al mismo factor de escala
  - y el volumen acompaña razonablemente el inverso esperado
  - entonces el caso debe reclasificarse como `scale_mismatch_*`
  - y degradarse a `SOFT_FAIL`

  ## Trazabilidad y reproducibilidad

  Este cambio no invalida la evidencia previa.

  Para preservar reproducibilidad:

  - el smoke actual queda congelado como baseline
  - el cambio se hará con nueva `validator_version`
  - el nuevo run se ejecutará en un `outdir` distinto
  - el notebook podrá comparar:
    - baseline `v0.1.0`
    - nuevo run `v0.2.0`

  Así, la evidencia queda separada en:

  - comportamiento del contrato anterior
  - evidencia visual que justifica el cambio
  - comportamiento del contrato nuevo