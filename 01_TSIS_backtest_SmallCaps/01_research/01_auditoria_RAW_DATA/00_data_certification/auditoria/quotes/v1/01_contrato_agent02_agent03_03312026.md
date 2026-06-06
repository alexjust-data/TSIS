## Contrato de datos entre Agent02 y Agent03

### Objetivo

Definir de forma explícita la interfaz de datos entre:

- Agent02
- Agent03

dentro de un mismo RUN_DIR del pipeline de quotes.

Este contrato describe:

- qué artefactos publica Agent02
- qué artefactos consume Agent03
- qué significado tiene cada artefacto
- qué parte es fuente de verdad
- qué parte es materialización de compatibilidad
- cómo se define la validez de un quotes.parquet
- qué papel analítico cumple Agent03 sobre los outputs de Agent02

No redefine la lógica interna completa de descarga ni la lógica interna completa de investigación posterior fuera de este pipeline.

———

## 1. Ámbito y directorio de intercambio

Todos los artefactos se leen y escriben dentro de un mismo:

- RUN_DIR

Ejemplo observado:

C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean

La interfaz contractual entre Agent02 y Agent03 se considera local a ese RUN_DIR.

———

## 2. Modelo contractual v2

### 2.1. Fuente de verdad operativa

En Agent02 v2, la fuente de verdad operativa deja de ser:

- CSV grandes
- JSON grandes
- estado reconstruido por reescritura completa

y pasa a ser:

- Parquet append-only para eventos batch
- DuckDB como capa de consulta, compactación y materialización

### 2.2. Materializaciones de compatibilidad

Los siguientes artefactos siguen existiendo en RUN_DIR, pero dejan de ser backend primario y pasan a ser:

- materializaciones derivadas
- exports de compatibilidad
- vistas consumibles por notebooks, monitores y Agent03

Artefactos obligatorios de compatibilidad:

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- live_status_quotes_strict.json
- run_config_quotes_strict.json
- batch_manifest_quotes_strict.csv

### 2.3. Regla general

Agent02 v2 puede cambiar completamente por dentro siempre que:

- mantenga el contrato semántico de validación por file
- mantenga las materializaciones visibles consumidas por Agent03
- mantenga estabilidad en claves, nombres y significado observable

———

## 3. Artefactos publicados por Agent02

## 3.1. quotes_agent_strict_events_current.csv

### Rol

Snapshot actual de validación strict por file.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- file

### Semántica

Representa el último evento vigente conocido por file dentro del run.

No es:

- historial completo
- log append-only

Sí es:

- una vista current derivada desde el backend incremental

### Columnas mínimas obligatorias

- file
- severity
- issues
- warns
- action
- processed_at_utc
- run_id

### Columnas v2 recomendadas

- validator_version
- scan_reason
- validation_kind

### Uso contractual

- input principal de Agent03
- input de notebooks de monitorización
- input de supervisor

———

## 3.2. retry_queue_quotes_strict_current.csv

### Rol

Snapshot actual de files pendientes de retry o revisión activa.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- file

### Semántica

Subset del estado current que contiene files retryables y aún activos.

Debe excluir:

- files cerrados
- files frozen
- files ya resueltos

### Columnas mínimas obligatorias

- file
- severity
- issues
- warns
- action
- processed_at_utc

### Columnas v2 recomendadas

- validator_version
- scan_reason
- validation_kind
- retry_attempts_effective

### Uso contractual

- input de Agent03
- input de monitores
- input de supervisor
- cola operativa de retry

———

## 3.3. retry_frozen_quotes_strict.csv

### Rol

Snapshot actual de files congelados fuera de retry activo.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- file

### Semántica

Contiene files que:

- son retryables o problemáticos
- superaron la política de retry activa
- no deben seguir en retry_current salvo acción explícita

### Columnas mínimas obligatorias

- file
- severity
- issues
- warns
- processed_at_utc

### Columnas v2 recomendadas

- retry_attempts_effective
- freeze_reason
- validator_version
- validation_kind

### Uso contractual

- input de revisión en Agent03
- diagnóstico y priorización

———

## 3.4. live_status_quotes_strict.json

### Rol

Resumen live o último estado conocido del run.

### Tipo

Snapshot escalar, no tabular.

### Semántica

Debe resumir el estado observable del run en el momento de materialización.

### Campos mínimos obligatorios

- run_id
- updated_utc
- files_discovered_total
- files_pending
- files_current_snapshot
- severity_counts_current
- retry_pending_files_current

### Campos recomendados

- materialization_utc
- backend_mode
- current_materialized_from
- retry_materialized_from

### Uso contractual

- monitorización
- supervisor
- visualización ligera
- notebooks

———

## 3.5. run_config_quotes_strict.json

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

———

## 3.6. batch_manifest_quotes_strict.csv

### Rol

Manifest del lote operativo más reciente o del lote objetivo materializado.

### Unidad lógica

- una fila por file

### Clave primaria lógica

- file

### Semántica

Describe el conjunto de files considerados en la materialización o lote operativo correspondiente.

No es historial global.
Es un manifest de trabajo o checkpoint operativo.

### Columnas mínimas obligatorias

- file

### Columnas recomendadas

- batch_id
- materialized_at_utc
- selection_reason

### Uso contractual

- input de Agent03
- monitorización
- reconciliación de cobertura y missing

———

## 4. Contrato de validación de un file quotes.parquet

### 4.1. Objetivo

Definir de forma explícita cómo Agent02 v2 decide si un file quotes.parquet es:

- PASS
- SOFT_FAIL
- HARD_FAIL

y qué evidencia mínima debe persistir por file.

La validez del file no depende del backend DuckDB + Parquet.
El backend solo persiste el resultado.
La decisión la toma el contrato de validación.

### 4.2. Unidad de validación

La unidad lógica primaria es:

- file

Ejemplo:

D:\quotes\AAPL\year=2024\month=01\day=03\quotes.parquet

Cada file debe producir exactamente un resultado de validación por evento de ejecución.

### 4.3. Principio general

La decisión de validez de un file debe seguir este orden lógico:

1. ¿se puede leer?
2. ¿tiene la estructura esperada?
3. ¿pertenece a la partición esperada?
4. ¿sus filas son coherentes?
5. ¿sus métricas cruzan umbrales?
6. ¿debe aceptarse, revisarse o congelarse?

### 4.4. Capa 1. Validación física

#### Checks obligatorios

- el file existe
- size_bytes > 0
- el parquet se puede abrir sin excepción

#### Fallos asociados

- file_missing
- zero_byte_file
- parquet_unreadable

#### Severidad esperada

- cualquier fallo de esta capa implica:
    - HARD_FAIL

### 4.5. Capa 2. Validación de partición

#### Objetivo

Comprobar que el path físico identifica correctamente:

- ticker
- year
- month
- day

#### Checks obligatorios

El path debe cumplir el patrón:

{root}\{ticker}\year=YYYY\month=MM\day=DD\quotes.parquet

Debe poder derivarse desde el path:

- ticker_path
- year_path
- month_path
- day_path

#### Fallos asociados

- invalid_partition_path
- missing_partition_component
- unparseable_partition_date

#### Severidad esperada

- cualquier fallo de esta capa implica:
    - HARD_FAIL

### 4.6. Capa 3. Validación de schema

#### Objetivo

Verificar que el parquet contiene el esquema mínimo requerido para ser interpretable por el pipeline.

#### Columnas mínimas obligatorias

- timestamp
- bid_price
- ask_price
- bid_size
- ask_size

#### Checks obligatorios

- todas las columnas mínimas existen
- los tipos son compatibles con el contrato esperado

#### Compatibilidad de tipos esperada

- timestamp
    - entero compatible
- bid_price
    - float o double compatible
- ask_price
    - float o double compatible
- bid_size
    - entero compatible
- ask_size
    - entero compatible

#### Fallos asociados

- missing_required_columns
- dtype_mismatch

#### Severidad esperada

- missing_required_columns
    - HARD_FAIL
- dtype_mismatch
    - SOFT_FAIL por defecto
    - salvo que se demuestre que rompe semánticamente la lectura

### 4.7. Capa 4. Validación de contenido

#### Objetivo

Verificar que las filas del parquet son coherentes y económicamente defendibles.

#### Checks obligatorios

- rows > 0
- timestamp parseable
- bid_price parseable
- ask_price parseable
- bid_size parseable
- ask_size parseable
- ausencia de precios negativos
- timestamps dentro del día esperado por partición
- dataset no vacío tras parseo

#### Fallos asociados

- zero_rows
- negative_prices_any_row
- timestamp_out_of_partition_day
- all_rows_invalid_after_parse

#### Severidad esperada

- estos fallos implican:
    - HARD_FAIL

### 4.8. Capa 5. Métricas microestructurales

#### Objetivo

Cuantificar si el file contiene señales de deterioro o anomalía operativa.

#### Métricas mínimas a calcular

- rows
- crossed_rows
- crossed_ratio_pct
- negative_price_rows
- ask_integer_pct
- bid_integer_pct
- ask_eq_round_bid_pct

#### Reglas mínimas observadas en Agent02 legacy

- si crossed_ratio_pct > threshold estricto
    - HARD_FAIL
- si crossed_ratio_pct > hard cap
    - HARD_FAIL
- si hay crossed_rows > 0 pero por debajo del umbral
    - SOFT_FAIL
- si ask_integer_pct muy alto y coincide con cruces anómalos
    - HARD_FAIL

#### Fallos o warnings asociados

- crossed_ratio_gt_threshold
- crossed_ratio_gt_hard_cap
- crossed_rows_present_but_under_threshold
- ask_integer_with_crossed_anomaly

#### Severidad esperada

- issues duros:
    - HARD_FAIL
- warnings:
    - SOFT_FAIL

### 4.9. Capa 6. Validación contextual

#### Objetivo

Añadir contexto explicativo sin mezclar causalidad con la validez base del file.

#### Contexto opcional enriquecido

- cercanía a split
- cercanía a ticker change
- sesión:
    - premarket
    - market
    - afterhours

#### Regla

Esta capa no debe cambiar por sí sola un PASS a HARD_FAIL salvo que exista una regla explícita aprobada.

Su función principal es:

- explicabilidad
- priorización
- soporte a Agent03

### 4.10. Política de clasificación final

#### HARD_FAIL

Asignar HARD_FAIL si existe al menos un issue duro, incluyendo:

- file_missing
- zero_byte_file
- parquet_unreadable
- invalid_partition_path
- missing_required_columns
- zero_rows
- negative_prices_any_row
- timestamp_out_of_partition_day
- crossed_ratio_gt_threshold
- crossed_ratio_gt_hard_cap
- ask_integer_with_crossed_anomaly

#### SOFT_FAIL

Asignar SOFT_FAIL si no existe HARD_FAIL pero sí warnings, incluyendo:

- dtype_mismatch
- crossed_rows_present_but_under_threshold
- soft_rule_eval_error

#### PASS

Asignar PASS si:

- no hay issues
- no hay warnings
- el file es estructural y económicamente coherente bajo el contrato actual

### 4.11. Acción operativa por severidad

#### Para PASS

- accept_raw

#### Para SOFT_FAIL

- review_queue
- o accept_with_warning si se define una whitelist explícita de warnings cerrables

#### Para HARD_FAIL

- quarantine_and_retry
- o review_queue según política operativa del run

### 4.12. Salida obligatoria por file

Cada validación de file debe producir como mínimo:

- file
- ticker
- date
- rows
- severity
- issues
- warns
- action
- metrics_json
- validator_version
- processed_at_utc
- run_id
- batch_id
- scan_reason
- validation_kind

### 4.13. Principio contractual final

La validez de un file no queda definida por:

- que exista en disco
- que esté en C
- que esté en D
- que tenga cobertura aparente

La validez de un file queda definida por:

- integridad física
- integridad de partición
- integridad de schema
- integridad de contenido
- métricas microestructurales
- clasificación contractual reproducible

———

## 5. Backend interno y modelo de datos de Agent02 v2

### 5.1. Log append-only

Agent02 v2 debe persistir un log append-only de eventos batch.

#### Unidad lógica

- una fila por evento de validación

#### Clave lógica del evento

- file + processed_at_utc + batch_id

#### Columnas mínimas

- file
- processed_at_utc
- severity
- issues
- warns
- action
- validator_version
- run_id
- batch_id
- scan_reason
- validation_kind

### 5.2. Query layer

DuckDB actúa como:

- catálogo de eventos
- capa de current
- capa de retry
- capa de frozen
- capa de live materialization

### 5.3. Clave primaria lógica de estado

La clave primaria lógica para current, retry y frozen es:

- file

### 5.4. Tabla quotes_inventory_files

#### Rol

Representa el inventario físico observado de files quotes.parquet.

#### Unidad lógica

- una fila por file físico

#### Clave primaria lógica

- file

#### Columnas mínimas obligatorias

- root
- file
- ticker
- date
- task_key
- size_bytes
- mtime_utc

#### Columnas recomendadas

- year
- month
- day
- exists_flag
- inventory_run_id
- inventory_seen_utc

#### Propósito

Responder:

- qué file existe
- en qué root existe
- a qué ticker,date pertenece
- cuándo se observó
- cuánto pesa

### 5.5. Tabla quotes_validation_events

#### Rol

Representa el log append-only de validaciones de files.

#### Unidad lógica

- una fila por evento de validación

#### Clave lógica del evento

- file + processed_at_utc + batch_id

#### Clave lógica del objeto validado

- file

#### Columnas mínimas obligatorias

- file
- processed_at_utc
- severity
- issues
- warns
- action
- validator_version
- run_id
- batch_id
- scan_reason
- validation_kind

#### Columnas recomendadas

- ticker
- date
- rows
- metrics_json
- root
- size_bytes_seen
- mtime_utc_seen
- schema_version
- validation_elapsed_ms

#### Regla estructural

Esta tabla es append-only.
No se reescribe como snapshot.
La deduplicación solo se usa para derivar vistas current.

### 5.6. Tabla quotes_current

#### Rol

Representa el último estado vigente por file.

#### Unidad lógica

- una fila por file lógico actual

#### Clave primaria lógica

- file

#### Derivación

Se obtiene desde:

- quotes_validation_events

quedándose con el último evento vigente por file y enriqueciéndose con:

- quotes_inventory_files

#### Columnas mínimas obligatorias

- file
- severity
- issues
- warns
- action
- processed_at_utc
- validator_version
- scan_reason
- validation_kind

#### Columnas recomendadas

- ticker
- date
- task_key
- present_in_c
- present_in_d
- present_in_both
- rows
- metrics_json
- current_as_of_utc

#### Compatibilidad contractual

Debe poder materializar:

- quotes_agent_strict_events_current.csv

### 5.7. Tabla retry_current

#### Rol

Representa la cola activa de retry.

#### Unidad lógica

- una fila por file

#### Clave primaria lógica

- file

#### Derivación

Subset de quotes_current más enriquecimiento de política de retry.

#### Columnas mínimas obligatorias

- file
- severity
- issues
- warns
- action
- processed_at_utc

#### Columnas recomendadas

- retry_attempts_effective
- last_retry_at_utc
- retry_policy_status
- validator_version
- validation_kind
- scan_reason

#### Regla

No debe incluir:

- files cerrados
- files aceptados
- files frozen

#### Compatibilidad contractual

Debe poder materializar:

- retry_queue_quotes_strict_current.csv

### 5.8. Tabla retry_frozen

#### Rol

Representa files retirados del retry activo.

#### Unidad lógica

- una fila por file

#### Clave primaria lógica

- file

#### Columnas mínimas obligatorias

- file
- severity
- issues
- warns
- processed_at_utc

#### Columnas recomendadas

- retry_attempts_effective
- freeze_reason
- frozen_at_utc
- validator_version
- validation_kind

#### Regla

Un file en retry_frozen no debe seguir apareciendo en retry_current salvo reapertura explícita.

#### Compatibilidad contractual

Debe poder materializar:

- retry_frozen_quotes_strict.csv

### 5.9. Tabla retry_actions o equivalente

#### Rol

Registrar acciones reales de retry.

#### Unidad lógica

- una fila por acción de retry

#### Clave lógica

- file + retry_action_utc

#### Columnas mínimas recomendadas

- file
- retry_action_utc
- retry_action_type
- retry_action_reason
- operator_or_system
- source_run_id

#### Importancia

Esta tabla es la base correcta para calcular:

- retry_attempts_effective

y evitar contaminarlo con revalidaciones repetidas.

### 5.10. Relación entre tablas

#### Flujo lógico

1. quotes_inventory_files
    - describe qué existe
2. quotes_validation_events
    - describe qué dijo el validador en cada ejecución
3. quotes_current
    - resume el último estado vigente por file
4. retry_current
    - subset operativo de files aún abiertos en retry
5. retry_frozen
    - subset operativo de files apartados del retry activo
6. retry_actions
    - evidencia de retry real

### 5.11. Regla de derivación de current

quotes_current debe obtenerse por esta lógica:

- agrupar por file
- ordenar por:
    - processed_at_utc
    - batch_id
- quedarse con el último evento válido

No debe depender de:

- CSV previos legacy
- listas JSON de procesados
- reescritura acumulada manual

### 5.12. Regla de derivación de retry

#### retry_current

Debe incluir files cuyo último estado vigente:

- no es PASS
- no está cerrado por whitelist explícita
- no está congelado
- sigue abierto operativamente

#### retry_frozen

Debe incluir files cuyo estado vigente:

- sigue siendo problemático
- pero ya superó la política de retry
- o fue congelado explícitamente

### 5.13. Materializaciones derivadas obligatorias

Desde estas tablas deben poder generarse las materializaciones de compatibilidad:

- desde quotes_current
    - quotes_agent_strict_events_current.csv
- desde retry_current
    - retry_queue_quotes_strict_current.csv
- desde retry_frozen
    - retry_frozen_quotes_strict.csv
- desde agregaciones de estado
    - live_status_quotes_strict.json

### 5.14. Beneficio del modelo

Este modelo separa claramente:

- existencia física
- resultado de validación
- estado actual
- retry activo
- retry congelado

y elimina la ambigüedad del diseño legacy, donde:

- CSV history
- CSV current
- retry queue
- retry attempts
- state JSON

mezclaban:

- fuente de verdad
- snapshots
- estado operativo
- historia

———

## 6. Semántica obligatoria de campos nuevos

## 6.1. scan_reason

Valores esperados:

- new
- changed
- rescan_all
- drain_full_reconcile
- manual_recheck

### Semántica

Explica por qué ese file volvió a entrar en validación.

## 6.2. validation_kind

Valores esperados:

- normal_validation
- retry_validation
- revalidation_only

### Semántica

Distingue entre:

- validación normal
- retry real
- reevaluación sin acción correctiva previa

———

## 7. Regla contractual de retry attempts

retry_attempts no debe representar cuántas veces fue observado un file.

Debe representar cuántos retries reales fueron ejecutados sobre ese file.

### Definición correcta

- retry_attempts = count(retry_validation) por file

### Definición incorrecta

- retry_attempts = count(validations) por file

### Implicación contractual

Una revalidación de snapshot o un rescan sin acción correctiva no debe incrementar retry_attempts.

———

## 8. Consumo contractual de Agent03

Agent03 consume desde el mismo RUN_DIR los siguientes artefactos:

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- run_config_quotes_strict.json
- batch_manifest_quotes_strict.csv

Adicionalmente, en algunos flujos de monitorización y visualización consume:

- live_status_quotes_strict.json

### Regla

Mientras Agent03 y los notebooks actuales sigan dependiendo de esos nombres y esa semántica, Agent02 v2 debe seguir materializando esos
outputs.

———

## 9. Uso observable en notebooks y scripts

## 9.1. Notebook de Agent02

Notebook:

C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\quotes\agent_02_validate_quotes_trades_realtime.ipynb

Rol observado:

- fija contexto del run
- muestra artefactos ya materializados
- documenta el handoff a Agent03

No ejecuta el análisis causal profundo.

## 9.2. Notebook de Agent03

Notebook:

C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\quotes\agent_03_monitor_coverage_and_stats_realtime_v2_clean.ipynb

Inputs observados:

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- batch_manifest_quotes_strict.csv
- run_config_quotes_strict.json

En algunos flujos:

- live_status_quotes_strict.json

## 9.3. Scripts de monitorización Agent03

Scripts observados:

- run_agent03_monitor_loop.ps1
- run_agent03_monitor_compact.ps1

Consumen:

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- batch_manifest_quotes_strict.csv
- run_config_quotes_strict.json

———

## 10. Frecuencia de materialización

Los exports de compatibilidad no deben regenerarse en cada mini batch.

### Política recomendada

Materializar periódicamente:

- cada 50k o 100k files validados
- o cada 10-15 minutos
- o al cierre explícito del run
- o bajo demanda antes de abrir notebooks o monitores

### Regla

Los exports de compatibilidad:

- no son estado vivo primario
- no deben gobernar el loop principal
- no deben ser la fuente de verdad del sistema

———

## 11. Reglas de compatibilidad

## 11.1. No puede cambiar sin migración coordinada

- nombre del artefacto
- significado lógico del artefacto
- clave primaria lógica
- columnas mínimas consumidas por Agent03

## 11.2. Sí puede cambiar internamente

- backend de almacenamiento
- estrategia de validación
- modelo de append-only
- frecuencia de compactación
- columnas adicionales
- estrategia de materialización

———

## 12. Resumen contractual mínimo

### Fuente de verdad v2

- Parquet append-only de eventos
- DuckDB como capa de consulta y materialización

### Materializaciones obligatorias de compatibilidad

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- live_status_quotes_strict.json
- run_config_quotes_strict.json
- batch_manifest_quotes_strict.csv

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

- mismo RUN_DIR
- mismos nombres de artefacto
- misma semántica observable
- backend interno libre, siempre que mantenga compatibilidad contractualmente visible

———

## 13. Rol analítico de Agent03 y significado de sus visualizaciones

### 13.1. Objetivo funcional de Agent03

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

### 13.2. Qué no hace Agent03

Agent03 no es:

- el motor primario de validación raw
- la fuente de verdad del run
- el responsable de clasificar el file por primera vez

Agent03 parte de un supuesto fuerte:

- Agent02 ya materializó un snapshot current coherente por file

Por tanto, Agent03 es una capa de:

- interpretación
- agregación
- priorización
- análisis visual
- análisis causal

———

## 14. Notebook principal de Agent03

Notebook observado:

C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\quotes\agent_03_monitor_coverage_and_stats_realtime_v2_clean.ipynb

### 14.1. Naturaleza del notebook

Este notebook sí hace el análisis profundo y visual.

No es un simple monitor pasivo.
Ejecuta varios scripts especializados que trabajan sobre los outputs de Agent02.

### 14.2. Inputs observados

Consume principalmente:

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- batch_manifest_quotes_strict.csv
- run_config_quotes_strict.json

En algunos flujos adicionales también usa:

- live_status_quotes_strict.json

Y en bloques causales o de referencia también cruza con:

- official_lifecycle_compiled.csv
- D:\reference\splits
- D:\reference\events
- D:\reference\overview
- D:\ohlcv_daily
- D:\ohlcv_1m

### 14.3. Outputs propios de Agent03

Agent03 genera y materializa en:

RUN_DIR\agent03_outputs

artefactos como:

- coverage_by_ticker.csv
- quality_summary_by_ticker.csv
- causes_by_ticker.csv
- ticker_diagnosis.csv
- run_summary.json

y además una subcarpeta de análisis causal:

RUN_DIR\agent03_outputs\causal_hypotheses

———

## 15. Arquitectura conceptual de Agent03

Las visualizaciones y tablas de Agent03 se organizan en cinco capas analíticas.

### 15.1. Capa de cobertura y causas

Scripts principales:

- 036_agent3_quotes_coverage_and_causes.py
- 037_agent3_diagnostics_tables_hist.py

### 15.2. Capa de ejemplos concretos

Script principal:

- 041_agent3_examples_independent.py

### 15.3. Capa de severidad cuantitativa bid/ask

Scripts principales:

- 043_dtype_rounding_plots.py
- 038_bid_ask_cross_deviation_metrics.py

### 15.4. Capa de decisión GO / NO-GO

Script principal:

- 044_agent3_go_nogo_review.py

### 15.5. Capa de hipótesis causal

Script principal:

- 045_agent3_causal_hypotheses.py

———

## 16. Capa 1: cobertura y causas

### 16.1. Qué hace

La primera capa convierte el snapshot file-level de Agent02 en una lectura por ticker.

Calcula, entre otros:

- cobertura temporal esperada vs observada
- días presentes
- días presentes con estado considerado aceptable
- días faltantes
- causa dominante por ticker
- estado de cierre o bloqueo por ticker

Outputs típicos:

- coverage_by_ticker.csv
- quality_summary_by_ticker.csv
- causes_by_ticker.csv
- ticker_diagnosis.csv
- run_summary.json

### 16.2. Qué se espera visualmente

Un humano debe esperar aquí:

- tablas de cobertura por ticker
- tablas de diagnóstico por ticker
- resúmenes globales del run
- rankings de causas dominantes

No debe esperar todavía:

- causalidad profunda
- inspección forense del raw
- lectura file a file completa

### 16.3. Qué decisión humana habilita

Esta capa permite responder:

- qué tickers están bien
- cuáles no están bien
- por qué no pasan
- si el problema dominante es coverage, retry o hard fail

### 16.4. Qué significa el resumen de run

El run_summary.json resume, por ejemplo:

- número de files deduplicados
- número de tickers
- retry pendiente
- hard fails
- cobertura media
- gate status

Ese summary no es una vista cosmética.
Es la primera síntesis ejecutiva del run.

Interpretación esperada:

- si gate_status es NO_CLOSE_RETRY_PENDING, el run no está operativo para cierre aunque la validación exista
- si la cobertura media es baja, la calidad operativa no se puede considerar suficiente

———

## 17. Capa 2: diagnóstico visual legible

### 17.1. Qué hace

La segunda capa no inventa una métrica nueva.
Hace legible y explicable lo ya generado en la capa 1.

Presenta:

- leyenda de causas
- resumen por severidad
- ticker diagnosis
- cobertura temporal por ticker
- histogramas o tablas de top causas

### 17.2. Para qué se quiere ver visualmente

La razón de visualizar esta capa es operacional:

- una tabla cruda de events_current no deja ver el patrón dominante
- la agregación visual sí permite priorizar

El objetivo no es “hacer gráficos por hacerlos”.
El objetivo es permitir triaje humano rápido.

### 17.3. Qué debe esperar el humano

Debe esperar:

- una lectura de priorización
- una forma rápida de identificar qué está alimentando el problema
- una separación entre:
    - problemas técnicos
    - problemas de cobertura
    - problemas de retry

No debe esperar:

- confirmación causal final
- prueba forense por sí sola

———

## 18. Capa 3: ejemplos concretos

### 18.1. Qué hace

La tercera capa baja de la agregación a ejemplos concretos de files y causas.

No pretende ser exhaustiva.
Pretende mostrar casos representativos de los problemas dominantes.

### 18.2. Qué problema resuelve

Sin ejemplos, un ranking de causas puede inducir errores de interpretación:

- una causa muy frecuente puede ser leve
- una causa poco frecuente puede ser catastrófica
- un patrón puede ser coherente o puede ser un artefacto

Los ejemplos ayudan a validar la intuición técnica.

### 18.3. Qué debe esperar el humano

Debe esperar:

- pocos ejemplos representativos
- apoyo al olfato técnico
- confirmación visual de si el patrón parece real o espurio

No debe esperar:

- cierre estadístico del problema
- inferencia causal definitiva

———

## 19. Capa 4: severidad cuantitativa bid/ask

Esta capa intenta responder no solo si hay cruces bid > ask, sino cuánto pesan y cómo se distribuyen.

### 19.1. Subcapa de dtype y rounding

Script:

- 043_dtype_rounding_plots.py

#### Qué hace

Evalúa si parte del problema puede venir de:

- tipos de dato incorrectos
- redondeos
- enterización de precios
- deformaciones mecánicas del raw

#### Qué debe esperar el humano

Una prueba o descarte de hipótesis mecánicas simples.

Por ejemplo:

- si no aparecen dtype_mismatch, se elimina una explicación obvia
- si aparecen patrones de enterización, hay sospecha de anomalía de feed o transformación

#### Qué decisión habilita

- decidir si merece la pena investigar una hipótesis de codificación o serialización
- separar problemas de mercado real de problemas de representación

### 19.2. Subcapa de métricas globales de desviación bid/ask

Script:

- 038_bid_ask_cross_deviation_metrics.py

#### Qué hace

Calcula métricas como:

- files totales
- files con cruces
- porcentaje de files con cruces
- filas totales
- filas cruzadas totales
- weighted_crossed_ratio_pct
- percentiles del crossed_ratio_pct
- histogramas globales
- zoom cerca de cero
- rango por ticker
- rango por causa

#### Por qué queremos verlo visualmente

Porque el conteo de files afectados no basta.

Hay que distinguir:

- muchos files con microcruces casi irrelevantes
- pocos files con severidad extrema
- distribución con cola pesada
- problema extendido pero débil
- problema concentrado y muy dañino

La visualización es necesaria para ver forma de distribución, no solo magnitud.

#### Qué debe esperar el humano

Una lectura cuantitativa de severidad.

Interpretación esperada:

- si files_with_cross_pct es alto pero weighted_crossed_ratio_pct es bajo, el problema está extendido pero el daño agregado puede ser limitado
- si el percentil 99 o el máximo son muy altos, hay outliers severos
- si el zoom cerca de cero concentra casi todo, el fenómeno puede ser estructural pero tenue
- si ciertos tickers concentran la cola, la priorización debe ser selectiva

#### Qué decisión habilita

- si el problema es tolerable o no
- si hace falta limpieza masiva
- si el run está dañado por pocos outliers o por una patología general

———

## 20. Capa 5: decisión GO / NO-GO

Script:

- 044_agent3_go_nogo_review.py

### 20.1. Qué hace

Reduce el estado del run a una decisión operativa.

No intenta explicar todos los detalles.
Intenta responder:

- ¿cerramos este run?
- ¿lo dejamos abierto?
- ¿qué problema impide cerrar?

### 20.2. Problemas dominantes que considera

El diseño observado concentra la decisión en dos ejes:

1. severidad de crossed bid > ask
2. presión operativa de:
    - retry_pending
    - retry_frozen

### 20.3. Qué visualiza

- resumen de severidad
- buckets de crossed ratio
- top files problemáticos
- presión de retry
- top tickers problemáticos
- serie temporal mensual de carga operativa

### 20.4. Por qué la visualización es importante

Un humano no toma la decisión solo con un número.

Necesita ver:

- si el daño está concentrado o extendido
- si el retry pendiente es marginal o estructural
- si los hard fails son residuales o dominantes
- si el problema se concentra temporalmente

### 20.5. Qué debe esperar el humano

Debe esperar una decisión ejecutiva defendible:

- GO
- NO-GO
- o “no cerrar todavía”

No debe esperar una explicación causal exhaustiva.

### 20.6. Interpretación esperada

- muchos retry_pending implican que el pipeline no está estabilizado
- muchos retry_frozen implican deuda operativa no resuelta
- pocos hard fails extremos pueden ser más importantes que muchos soft fails leves
- una cola mensual creciente sugiere que el proceso no converge

———

## 21. Capa 6: hipótesis causal

Script:

- 045_agent3_causal_hypotheses.py

### 21.1. Qué hace

Esta capa intenta explicar por qué aparecen los problemas observados.

Para ello cruza los files problemáticos con:

- splits
- corporate events
- overview
- ohlcv_daily
- ohlcv_1m

y analiza además:

- proximidad a splits
- proximidad a ticker changes
- proximidad a otros eventos corporativos
- sesión:
    - premarket
    - market
    - afterhours
- pares de exchange
- tape
- magnitud y contexto del cruce

### 21.2. Qué visualiza

- severidad por sesión
- pares de exchange con más cruces
- hipótesis por ventana de evento
- pathology files
- tablas de contexto por ticker y fecha

### 21.3. Por qué queremos verlo visualmente

La causalidad rara vez sale de una sola tabla.

Se necesita ver si el patrón parece más coherente con:

- microestructura en premarket o afterhours
- placeholders o cotizaciones anómalas
- cambios de ticker
- corporate actions
- efectos de split
- pares específicos de exchange o tape

La visualización permite detectar estructura, no solo correlación plana.

### 21.4. Qué debe esperar el humano

Debe esperar:

- hipótesis priorizadas
- explicaciones plausibles
- focos de investigación posteriores

No debe esperar:

- una prueba causal definitiva
- una certificación automática del origen del problema

### 21.5. Interpretación humana esperada

Por ejemplo:

- si afterhours y premarket concentran ratios muy superiores a market, la anomalía parece ligada a sesiones periféricas
- si los problemas aparecen cerca de splits, hay hipótesis fuerte de fricción de corporate actions
- si predominan ciertos exchange_pair, puede haber una patología de microestructura o codificación asociada
- si ticker_change no aparece cerca de los casos, esa hipótesis pierde fuerza

———

## 22. Qué espera un humano al abrir Agent03

El notebook de Agent03 no debe interpretarse como un dashboard genérico.

Debe interpretarse como una secuencia lógica de decisión.

### Secuencia esperada

1. Cobertura
    - ¿qué parte del universo o lote está razonablemente cubierta?
2. Calidad
    - ¿qué severidades dominan?
3. Priorización
    - ¿qué tickers y files requieren atención primero?
4. Decisión
    - ¿está el run listo para cerrar?
5. Hipótesis
    - ¿qué explicación técnica parece más plausible?

### Resultado esperado

Agent03 debe permitir que un humano pase de:

- un snapshot técnico file-level difícil de leer

a:

- una interpretación operativa completa del run

———

## 23. Relación funcional entre Agent02 y Agent03

### Agent02

Responsable de:

- descubrir
- validar
- clasificar
- materializar estado file-level

### Agent03

Responsable de:

- interpretar
- agregar
- visualizar
- priorizar
- apoyar decisión
- formular hipótesis causales

### Regla funcional

Agent03 no reemplaza la validación de Agent02.
Agent03 hace inteligible el estado producido por Agent02.

En resumen:

- Agent02 produce verdad técnica operacional
- Agent03 produce legibilidad operacional y analítica humana

———

## 24. Implicación contractual para la refactorización

La refactorización de Agent02 no puede evaluarse solo por:

- velocidad
- backend
- paralelización

También debe preservarse la capacidad analítica de Agent03.

Por tanto, Agent02 v2 debe seguir garantizando que Agent03 pueda reconstruir:

- cobertura por ticker
- severidad por file
- causes by ticker
- retry pressure
- gate status
- hipótesis causales

aunque internamente Agent02 cambie de:

- CSV y JSON
a:
- DuckDB + Parquet

### Regla contractual de compatibilidad analítica

Mientras Agent03 y sus notebooks no migren a lectura directa desde DuckDB o Parquet, Agent02 v2 debe seguir materializando outputs compatibles
que preserven:

- nombres
- claves
- columnas mínimas
- semántica observable

———

## 25. Resumen final

Agent03 existe para convertir los outputs técnicos de Agent02 en una lectura humana de:

- cobertura
- severidad
- prioridad
- decisión
- hipótesis causal

No es un validador raw primario.
Es una capa analítica de interpretación y decisión.

Su utilidad no es cosmética.
Sus visualizaciones existen para permitir que un humano responda con rapidez y fundamento a estas preguntas:

- ¿qué tan cubierto está el run?
- ¿qué tan grave es el problema?
- ¿dónde se concentra?
- ¿qué debo revisar primero?
- ¿puedo cerrar o no?
- ¿qué explicación técnica es más plausible?