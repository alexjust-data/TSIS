  - [Agent02 Quotes: estado actual, problemas observados y propuesta de rediseño](#agent02-quotes-estado-actual-problemas-observados-y-propuesta-de-rediseño)
  - [1. Run de referencia](#1-run-de-referencia)
  - [2. Estado actual del run](#2-estado-actual-del-run)
  - [3. Conclusión operativa del estado actual](#3-conclusion-operativa-del-estado-actual)
  - [4. Archivos que gobiernan el estado de Agent02](#4-archivos-que-gobiernan-el-estado-de-agent02)
  - [5. Implementación actual de Agent02](#5-implementacion-actual-de-agent02)
    - [5.1. Script lanzador](#51-script-lanzador)
    - [5.2. Motor real](#52-motor-real)
    - [5.3. Flujo actual](#53-flujo-actual)
  - [6. Problemas lógicos y estructurales observados](#6-problemas-logicos-y-estructurales-observados)
    - [6.1. Validación en serie](#61-validacion-en-serie)
    - [6.2. Relectura y reescritura completa de artefactos grandes](#62-relectura-y-reescritura-completa-de-artefactos-grandes)
    - [6.3. Estado persistente en JSON con lista grande de files](#63-estado-persistente-en-json-con-lista-grande-de-files)
    - [6.4. Semántica confusa entre estado y snapshot](#64-semantica-confusa-entre-estado-y-snapshot)
    - [6.5. Inflación artificial de retry attempts](#65-inflacion-artificial-de-retry-attempts)
  - [7. Propuesta 1: paralelizar validación y separar validación de consolidación](#7-propuesta-1-paralelizar-validacion-y-separar-validacion-de-consolidacion)
    - [7.1. Cambio propuesto](#71-cambio-propuesto)
    - [7.2. Ejecución propuesta](#72-ejecucion-propuesta)
    - [7.3. Condiciones de implementación](#73-condiciones-de-implementacion)
    - [7.4. Consolidación](#74-consolidacion)
    - [7.5. Ganancia esperada](#75-ganancia-esperada)
  - [8. Propuesta 2: sustituir el backend de estado por un backend incremental](#8-propuesta-2-sustituir-el-backend-de-estado-por-un-backend-incremental)
    - [8.1. Cambio propuesto](#81-cambio-propuesto)
    - [8.2. Backend propuesto](#82-backend-propuesto)
    - [8.3. Justificación](#83-justificacion)
    - [8.4. Cambio de complejidad](#84-cambio-de-complejidad)
    - [8.5. Fuente de verdad propuesta](#85-fuente-de-verdad-propuesta)
    - [8.6. Columnas mínimas por evento](#86-columnas-minimas-por-evento)
    - [8.7. Campos semánticos clave](#87-campos-semanticos-clave)
    - [8.8. Semántica correcta de attempts](#88-semantica-correcta-de-attempts)
    - [8.9. Dos niveles de persistencia](#89-dos-niveles-de-persistencia)
  - [9. Orden recomendado de implementación](#9-orden-recomendado-de-implementacion)
  - [10. Estrategia de relanzamiento recomendada](#10-estrategia-de-relanzamiento-recomendada)
  - [11. Veredicto técnico](#11-veredicto-tecnico)


ponta al día con el proyecto C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\00_auditoria_general.md en
concreto ahora he terminado este notebook C:
\TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_root_cause_audit_notebook.ipynb debes
leer
cada celda y sus respuestas. Además estoy creando ahora mismo C:
\TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_full_C_D_audit.ipynb. Pero lo que has de
hacer de verdad, a parte de leer todo lo que te he pasado, cada texto, scripts y celda, tu trabajo será generar una auditoria para
quotes en un notebook nuevo. lee la estructura de los notebooks de C:
\TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_root_cause_audit_notebook.ipynb C:
\TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_full_C_D_audit.ipynb para hacerte unaidea
de la granulidad que buscamos, queremos conocer profundamente la data que tenemos. C:
\TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\cell_code debes crear los scripts largos en esta
folder y en las celdas del notebook las lanzaderas para visualizaciones y analitica. Debes ejecutar tu el notebook y comprobar que
funciona todo bien.

---- 

 ponta al día con el proyecto C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\00_auditoria_general.md en
  concreto ahora he terminado este notebook C:
  \TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_root_cause_audit_notebook.ipynb debes leer
  cada celda y sus respuestas. Despues continuaremos phaciendo lo que hacia un agente cuando se fue la luuz, el me dijo # Nota

  El notebook de trades que hemos trabajado no está analizando todavía el merge final C + D. Está analizando el run full de D:

  - trades_validate_2005_2026_d_full/trades_current.parquet aparece citado como el current de D C:/TSIS_Data/02_backtest_SmallCaps/
  notebooks/00_data_certification/auditoria/00_auditoria_general.md:5007

  En ese mismo documento se deja explícito que después hubo un merge final D + C separado:

  - “trades quedó cerrado correctamente a nivel de merge y materialización final current” C:/TSIS_Data/02_backtest_SmallCaps/
  notebooks/00_data_certification/auditoria/00_auditoria_general.md:4749
  - el dataset final mergeado queda en trades_v2_materialized/trades_current_cd_merged C:/TSIS_Data/02_backtest_SmallCaps/
  notebooks/00_data_certification/auditoria/00_auditoria_general.md:4767
  - el merge correcto se lanza con 053b_trades_v2_merge_cd_current.py C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/
  auditoria/00_auditoria_general.md:4689

  Así que la formulación precisa es:

  - el notebook trades que hemos refactorizado audita el full materializado de D
  - no el current_cd_merged final de C + D
  - el merge final C + D sí existe y quedó verificado en el proyecto, pero no es el parquet que estaba usando ese notebook y ahora la
  consigna era crear este notebook nuevo C:
  \TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_full_C_D_audit.ipynb para replicar lo que
  hicomos para D en el notebook anterior, es decir que hay que generar nuevos scripts y nuevas celdas co msus lanzaderas para obtener los
• Voy a ponerme al día con ese bloque de auditoría leyendo el 00_auditoria_general.md y el notebook
  03_trades_root_cause_audit_notebook.ipynb, incluyendo celdas y outputs, para reconstruir exactamente en qué punto quedó el trabajo y qué
  falta para el nuevo notebook 03_trades_full_C_D_audit.ipynb.

  no debes tocar ningun scripts que se haya usado antes, debes crear desde cero para replicar en el notebook C:
  \TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_full_C_D_audit.ipynb lo que hicimos antes
  en C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\03_trades_root_cause_audit_notebook.ipynb para
  la data en D. Se nota que no has leido C:
  \TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\trades\cell_code\40_cd_run_snapshot.py C:
--- 

## Agent02 Quotes: estado actual, problemas observados y propuesta de rediseño

### 1. Run de referencia

El análisis de Agent02 para quotes está en:

C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean

Ese directorio contiene el estado operativo y los artefactos generados por el proceso de validación estricta.

### 2. Estado actual del run

Según:

C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean\live_status_quotes_strict.json

estado observado:

- updated_utc: 2026-03-22T09:17:12.849651+00:00
- files_current_snapshot: 2,205,543
- files_pending: 0
- retry_pending_files_current: 947,643

Según:

C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean\quotes_agent_strict_events_current.csv

distribución del snapshot actual:

- PASS: 1,247,335
- SOFT_FAIL: 861,248
- HARD_FAIL: 96,960

Adicionalmente, el run reporta:

- retry_frozen: 10,565

### 3. Conclusión operativa del estado actual

Agent02 sí completó el discovery del snapshot actual y sí generó un estado actual completo de validación.

No quedan pendientes de descubrimiento:

- files_pending = 0

Lo que queda es una cola muy grande de revisión o retry:

- retry_pending_files_current = 947,643

Por tanto, el cuello de botella actual no está en discovery sino en validación persistida, consolidación y gestión de retry.

———

## 4. Archivos que gobiernan el estado de Agent02

Dentro de:

C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean

los artefactos principales son:

- live_status_quotes_strict.json
Estado resumido en vivo y último estado conocido.
- quotes_agent_strict_state.json
Estado persistente interno del proceso.
- quotes_agent_strict_events_current.csv
Último estado por file.
- quotes_agent_strict_events_history.csv
Historial acumulado de validaciones.
- retry_queue_quotes_strict_current.csv
Cola actual pendiente de retry.
- retry_queue_quotes_strict.csv
Cola persistida completa.
- retry_attempts_quotes_strict.csv
Contador de reintentos registrados.
- retry_frozen_quotes_strict.csv
Files congelados fuera de retry activo.
- run_config_quotes_strict.json
Configuración efectiva del run.
- quotes_reconciliation_status.json
Estado de reconciliación.
- granular_strict\
Artefactos de diagnóstico granular por file y por ticker.

———

## 5. Implementación actual de Agent02

### Script lanzador

C:\TSIS_Data\02_backtest_SmallCaps\scripts\agents\run_agent02_quotes_strict_loop.ps1

### Motor real

C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\032_probe_quotes_agent_behavior_strict.py

### Flujo actual

1. Descubre quotes.parquet en D:\quotes
2. Mantiene índice de descubrimiento:
    - quotes_discovered_index.parquet
3. Construye cola pendiente:
    - quotes_pending_queue.parquet
4. Valida cada file con _assess_file(...)
5. Clasifica cada file:
    - PASS
    - SOFT_FAIL
    - HARD_FAIL
6. Escribe historial y snapshot actual:
    - quotes_agent_strict_events_history.csv
    - quotes_agent_strict_events_current.csv
7. Reconstruye retry:
    - retry_queue_quotes_strict.csv
    - retry_queue_quotes_strict_current.csv
    - retry_attempts_quotes_strict.csv
    - retry_frozen_quotes_strict.csv
8. Genera estado live:
    - live_status_quotes_strict.json

———

## 6. Problemas lógicos y estructurales observados

### 6.1. Validación en serie

La validación se ejecuta en serie mediante:

out_df = pd.DataFrame([_assess_file(fp) for fp in files])

Eso implica:

- apertura file a file
- validación secuencial
- ausencia de paralelismo

Para millones de parquet pequeños, este diseño es lento.

### 6.2. Relectura y reescritura completa de artefactos grandes

En cada ciclo se rehacen operaciones costosas sobre artefactos grandes:

- lectura de quotes_agent_strict_events_history.csv
- reconstrucción de quotes_agent_strict_events_current.csv
- reconstrucción de colas de retry
- reescritura de outputs granulares
- reescritura de retry_attempts_quotes_strict.csv

Tamaños observados:

- quotes_agent_strict_events_history.csv: 867,741,846 bytes
- quotes_agent_strict_events_current.csv: 538,975,035 bytes
- retry_queue_quotes_strict.csv: 161,029,944 bytes
- retry_attempts_quotes_strict.csv: 140,707,500 bytes

Esto introduce una carga de I/O administrativo elevada por ciclo.

### 6.3. Estado persistente en JSON con lista grande de files

quotes_agent_strict_state.json guarda una lista extensa de files cerrados.

Consecuencias:

- JSON grande
- parseo lento
- serialización lenta
- alto consumo de RAM
- write amplification innecesario

### 6.4. Semántica confusa entre estado y snapshot

Se observa:

- files_processed_total_state = 1,092,297
- PASS + SOFT_FAIL + HARD_FAIL = 2,205,543

No implica necesariamente un bug fatal, pero sí una semántica operativa ambigua:

- state mide files cerrados en el estado interno
- current representa el snapshot actual total

Esto dificulta la lectura rápida del progreso real.

### 6.5. Inflación artificial de retry attempts

La lógica actual incrementa attempts cuando cambia processed_at_utc.

Eso implica que un file puede aumentar su contador de intentos aunque no haya habido una reparación o retry real.

La distribución observada lo confirma:

- 931,824 files con intento 1
- existen files con intentos muy altos:
    - 100+
    - hasta 248

Eso no representa retry operativo real; representa reevaluación repetida del mismo snapshot.

———

## 7. Propuesta 1: paralelizar validación y separar validación de consolidación

### 7.1. Cambio propuesto

Mantener discovery como está y cambiar la fase de validación:

- validar files en paralelo
- ejecutar por lotes shardados
- escribir resultados por batch
- diferir la consolidación global

### 7.2. Ejecución propuesta

Sustituir la validación secuencial por un mapa paralelo de _assess_file(fp) mediante:

- ProcessPoolExecutor
- o ThreadPoolExecutor, tras benchmark

Rango inicial de workers propuesto para benchmark:

- 4
- 8
- 12
- 16

No se propone fijar 32 workers por defecto.

### 7.3. Condiciones de implementación

El shard debe ser determinista, no arbitrario. La partición debe definirse con una clave estable por file.

Cada resultado batch debe persistirse como append-only e incluir como mínimo:

- file
- processed_at_utc
- severity
- issues
- warns
- action
- validator_version
- run_id
- batch_id

### 7.4. Consolidación

La consolidación de:

- events_current
- retry_current
- granular
- live_status

no debe ejecutarse en cada mini batch.

Debe ejecutarse:

- cada cierto número de batches
- o cada cierto umbral temporal
- mediante materialización periódica

Esto permite reducir reescrituras completas repetidas sin perder visibilidad operativa.

### 7.5. Ganancia esperada

La mejora de velocidad estimada para esta propuesta es de:

- 4x a 10x

condicionada a:

- rendimiento del disco
- tamaño medio de los parquet
- presión de CPU
- presión de I/O
- reducción simultánea de la consolidación repetitiva

Paralelizar _assess_file(fp) sin corregir el backend de estado no elimina por sí solo el cuello de botella principal.

———

## 8. Propuesta 2: sustituir el backend de estado por un backend incremental

### 8.1. Cambio propuesto

Sustituir como fuente de verdad viva:

- quotes_agent_strict_state.json
- quotes_agent_strict_events_history.csv
- quotes_agent_strict_events_current.csv
- retry_attempts_quotes_strict.csv

por un backend incremental.

### 8.2. Backend propuesto

Dos niveles:

#### Log durable append-only

- Parquet fragmentado append-only para eventos batch

#### Capa de consulta y compactación

- DuckDB como capa de consulta y materialización

Los CSV pueden mantenerse como exports para consumo humano o notebooks, pero no como fuente de verdad operativa.

### 8.3. Justificación

El problema principal actual no es solo la validación file a file; es el diseño de estado:

- JSON grande
- CSV grandes
- reconstrucción global repetida
- retry con semántica contaminada

Con backend incremental:

- el coste se mueve desde relectura global hacia upsert o append por batch
- events_current sale por query
- retry_current sale por query
- attempts deja de depender de reevaluaciones repetidas

### 8.4. Cambio de complejidad

Coste actual aproximado por ciclo:

- O(batch_validate) + O(history_total) + O(current_total) + O(retry_total)

Coste objetivo:

- O(batch_validate) + O(batch_upsert)

### 8.5. Fuente de verdad propuesta

#### Append-only

- events_batches/ en Parquet append-only

#### Query layer

- DuckDB como catálogo y capa de compactación

#### Clave lógica primaria

- file

### 8.6. Columnas mínimas por evento

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

### 8.7. Campos semánticos clave

#### scan_reason

Valores propuestos:

- new
- changed
- rescan_all
- drain_full_reconcile
- manual_recheck

#### validation_kind

Valores propuestos:

- normal_validation
- retry_validation
- revalidation_only

Estos campos separan conceptualmente:

- validación normal
- retry real
- revalidación del mismo file sin acción correctiva

### 8.8. Semántica correcta de attempts

attempts no debe incrementarse por el simple hecho de que un file vuelva a ser validado.

Debe incrementarse únicamente cuando:

- el file estaba en cola de retry
- hubo una acción operativa real asociada
- se ejecutó una validación posterior atribuible a ese retry

Definición correcta:

- attempts = count(retry_validation) por file

Definición incorrecta:

- attempts = count(validations) por file

### 8.9. Dos niveles de persistencia

#### Nivel 1: log append-only

Cada batch validado escribe su fragmento:

- barato
- robusto ante crash
- auditable

#### Nivel 2: materialización periódica

Cada cierto umbral:

- 50k o 100k files
- o cada 10-15 minutos

se recalculan:

- events_current
- retry_current
- retry_frozen
- live_status

Esto evita quedar sin visibilidad operativa si el proceso cae.

———

## 9. Orden recomendado de implementación

Si solo se pudiera hacer una mejora:

- priorizar Propuesta 2

Si se implementan ambas:

1. corregir semántica de eventos y retry
2. introducir backend incremental DuckDB + Parquet
3. introducir materialización periódica
4. paralelizar _assess_file(fp)

No se recomienda paralelizar primero un flujo cuya semántica de estado y retry sigue siendo incorrecta.

———

## 10. Estrategia de relanzamiento recomendada

No se recomienda relanzar Agent02 actual sobre todo el universo desde cero.

Secuencia recomendada:

1. congelar el run actual como snapshot histórico
2. reutilizar:
    - quotes_discovered_index.parquet
3. migrar el estado actual a Agent02 v2
4. reinyectar como cola inicial:
    - retry_queue_quotes_strict_current.csv

Objetivo operativo:

- no reescaneo total
- arranque desde los 947,643 files problemáticos ya identificados

———

## 11. Veredicto técnico

Agent02 no está roto conceptualmente. El problema es de arquitectura de ejecución y persistencia de estado.

Problemas principales:

- validación en serie
- consolidación global repetida
- uso de CSV y JSON grandes como estado vivo
- semántica incorrecta de retry attempts
- mezcla entre retry real y revalidación repetida

Recomendación técnica final:

- mantener file como clave lógica principal
- mover la verdad operativa a log append-only + query layer incremental
- derivar current y retry_current por query
- mantener CSV solo como export
- corregir attempts para que refleje únicamente retry real
- después de eso, paralelizar la validación

Si quieres, en el siguiente paso puedo convertir este texto en una especificación v2 cerrada con secciones de:

- inputs
- outputs
- tablas
- claves
- fases
- reglas de materialización
- compatibilidad con Agent03.


# Ejecucion


- [1. Cerrar el diseño de Agent02 v2](#1-cerrar-el-diseno-de-agent02-v2)
- [1.1. Qué hacía Agent02 legacy al validar un file](#11-que-hacia-agent02-legacy-al-validar-un-file)
- [1.2. Qué cambia ahora en Agent02 v2](#12-que-cambia-ahora-en-agent02-v2)
- [2. Construir el auditor forense v2 para quotes](#2-construir-el-auditor-forense-v2-para-quotes)
- [2.1. Capa A. Inventario exacto](#21-capa-a-inventario-exacto)
- [2.2. Capa B. Validación profunda](#22-capa-b-validacion-profunda)
- [2.2.1. Capa 1. Validación física](#221-capa-1-validacion-fisica)
- [2.2.2. Capa 2. Validación de partición](#222-capa-2-validacion-de-particion)
- [2.2.3. Capa 3. Validación de schema](#223-capa-3-validacion-de-schema)
- [2.2.4. Capa 4. Validación de contenido](#224-capa-4-validacion-de-contenido)
- [2.2.5. Capa 5. Validación contextual](#225-capa-5-validacion-contextual)
- [2.2.6. Salida correcta por file](#226-salida-correcta-por-file)
- [3. Auditar primero el universo objetivo, no todo el histórico mezclado](#3-auditar-primero-el-universo-objetivo-no-todo-el-historico-mezclado)
- [4. Materializar tres tablas maestras](#4-materializar-tres-tablas-maestras)
- [4.1. quotes_inventory_files](#41-quotes_inventory_files)
- [4.2. quotes_validation_events](#42-quotes_validation_events)
- [4.3. quotes_current](#43-quotes_current)
- [5. Priorizar la auditoría profunda](#5-priorizar-la-auditoria-profunda)
- [6. Mantener compatibilidad con Agent03](#6-mantener-compatibilidad-con-agent03)
- [Recomendación operativa inmediata](#recomendacion-operativa-inmediata)
- [En una frase](#en-una-frase)

## 1. Cerrar el diseño de Agent02 v2

Antes de volver a correr auditorías masivas, fijar:

- backend DuckDB + Parquet
- semántica de:
    - file
    - events_current
    - retry_current
    - retry_frozen
    - retry_attempts
    - scan_reason
    - validation_kind

Pero eso no es suficiente por sí solo.

La pieza central del rediseño no es solo el backend.
La pieza central es:

- cómo se valida un quotes.parquet
- qué significa que un file sea válido
- qué checks produce la severidad final
- qué información queda persistida por file

Sin ese contrato de validación, mover el estado a DuckDB + Parquet solo cambia dónde guardas el resultado, pero no mejora la fiabilidad del
auditor.

## 1.1. Qué hacía Agent02 legacy al validar un file

Agent02 legacy validaba cada file en la función _assess_file(fp) del script:

- 032_probe_quotes_agent_behavior_strict.py

### Reglas que aplicaba

#### Integridad física

- file existe
- no es 0 bytes
- parquet legible
- path válido bajo patrón:
    - ticker/year=YYYY/month=MM/day=DD/quotes.parquet

#### Integridad estructural

- rows > 0
- columnas obligatorias:
    - timestamp
    - bid_price
    - ask_price
    - bid_size
    - ask_size

#### Integridad de tipos

- precios con tipo flotante compatible
- tamaños y timestamp con tipo entero compatible
- si no cuadra:
    - dtype_mismatch como SOFT_FAIL

#### Integridad económica mínima

- no precios negativos
- calcula:
    - crossed_rows
    - crossed_ratio_pct
    - ask_integer_pct
    - bid_integer_pct
    - ask_eq_round_bid_pct

#### Clasificación final

- HARD_FAIL si hay:
    - parquet_unreadable
    - zero_byte_file
    - invalid_partition_path
    - zero_rows
    - missing_required_columns
    - negative_prices_any_row
    - crossed_ratio_gt_threshold
    - crossed_ratio_gt_hard_cap
    - ask_integer_with_crossed_anomaly
- SOFT_FAIL si no hay HARD_FAIL pero sí:
    - dtype_mismatch
    - crossed_rows_present_but_under_threshold
    - soft_rule_eval_error
- PASS si no hay issues ni warns

## 1.2. Qué cambia ahora en Agent02 v2

Agent02 v2 no debe limitarse a “mover lo mismo a DuckDB”.

Debe separar claramente:

- contrato de validación por file
- persistencia de eventos
- materialización current
- retry/frozen
- exports de compatibilidad

El backend nuevo será:

- Parquet append-only para eventos de validación
- DuckDB para:
    - current
    - retry
    - frozen
    - live status
    - materializaciones periódicas

Pero el criterio de validez seguirá dependiendo de una validación fuerte por file.

———

## 2. Construir el auditor forense v2 para quotes

Separado del loop legacy.

Dos capas:

### Capa A. Inventario exacto

Sobre:

- C:\TSIS_Data\data\quotes
- D:\quotes

salida por:

- file
- ticker,date

### Capa B. Validación profunda

Sobre cada quotes.parquet, no solo verificar presencia, sino decidir si es válido o no con reglas fuertes.

Esto incluye:

- lectura parquet
- schema
- filas
- consistencia file -> ticker,date
- métricas bid/ask
- validator_version
- fingerprint o hash opcional

## 2.1. Capa A. Inventario exacto

La capa de inventario no decide si el file es bueno.

Solo responde:

- qué files existen
- dónde existen
- qué ticker/date representan
- si están en C
- si están en D
- si están en ambos

Sirve para construir el universo físico real antes de abrir los parquet.

## 2.2. Capa B. Validación profunda

La validación profunda sí decide si el file es aceptable o no.

Yo la estructuraría en cinco capas.

## 2.2.1. Capa 1. Validación física

Checks mínimos:

- exists
- size_bytes > 0
- parquet_read_ok

Objetivo:

- descartar corrupción física evidente
- descartar archivos vacíos
- descartar parquet ilegible

## 2.2.2. Capa 2. Validación de partición

Derivar desde el path:

- ticker_path
- year_path
- month_path
- day_path

y verificar que el file pertenece exactamente a esa partición.

Objetivo:

- detectar rutas mal construidas
- detectar colocación incorrecta del file
- asegurar consistencia entre path y unidad lógica del dato

## 2.2.3. Capa 3. Validación de schema

Comprobar:

- columnas requeridas
- tipos compatibles
- columnas extra permitidas
- versión de schema si aplica

Objetivo:

- separar corrupción estructural de simple diferencia cosmética
- fijar un contrato de lectura estable

## 2.2.4. Capa 4. Validación de contenido

Checks sobre filas:

- rows > 0
- timestamp no nulo
- bid_price y ask_price parseables
- bid_size y ask_size parseables
- sin precios negativos
- timestamps dentro del día esperado
- consistencia razonable del dataset
- cálculo de:
    - % crossed
    - % ask integer
    - % bid integer
    - % ask_eq_round_bid
    - métricas adicionales si se introducen placeholders o heurísticas nuevas

Objetivo:

- decidir si el contenido es económicamente coherente
- distinguir:
    - problema leve
    - problema severo
    - corrupción estructural

## 2.2.5. Capa 5. Validación contextual

Esta capa no debe decidir siempre el PASS/HARD_FAIL base, pero sí enriquecer el evento con contexto.

Cruces posibles:

- cercanía a split
- cercanía a ticker change
- sesión:
    - premarket
    - market
    - afterhours
- referencias complementarias si existen

Objetivo:

- añadir explicabilidad
- no mezclar todavía causalidad con corrupción base
- permitir a Agent03 formular hipótesis después

## 2.2.6. Salida correcta por file

Cada validación debe producir, como mínimo:

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
- scan_reason
- validation_kind
- processed_at_utc

La decisión de validez debe seguir este orden lógico:

1. ¿se puede leer?
2. ¿tiene el schema esperado?
3. ¿sus filas son coherentes?
4. ¿sus métricas cruzan umbrales?
5. ¿requiere aceptación, retry o freeze?

———

## 3. Auditar primero el universo objetivo, no todo el histórico mezclado

Primero cruzar contra el universo operativo que te importa.

Hoy eso sería, según objetivo:

- <1B
- o <2B

Porque si no mezclas:

- histórico fuera de target
- C y D legacy
- retries viejos
- universos distintos

y acabas auditando más volumen del necesario con peor capacidad de interpretación.

———

## 4. Materializar tres tablas maestras

Para quotes haría estas tres.

## 4.1. quotes_inventory_files

Una fila por file físico:

- root
- file
- ticker
- date
- task_key
- size_bytes
- mtime

Rol:

- universo físico observado
- base para comparar C vs D
- base para decidir qué abrir después

## 4.2. quotes_validation_events

Una fila por validación:

- file
- processed_at_utc
- severity
- issues
- warns
- validator_version
- validation_kind
- scan_reason

Idealmente también:

- batch_id
- run_id
- metrics_json

Rol:

- log append-only de validaciones
- fuente de verdad del estado evaluado
- base para reconstruir current, retry y frozen

## 4.3. quotes_current

Una fila por file lógico actual:

- último estado vigente
- si está en C
- si está en D
- si está en ambos
- si pasa o no pasa

Rol:

- snapshot operativo derivado
- equivalente contractual moderno de:
    - quotes_agent_strict_events_current.csv

———

## 5. Priorizar la auditoría profunda

No abriría 10 millones de files de golpe.

Orden:

1. intersección exacta C ∩ D
    - 168
2. universo objetivo <1B o <2B
3. files con:
    - tamaño 0
    - schema raro
    - HARD_FAIL
    - retry_frozen
4. resto del universo

La idea es:

- máxima señal primero
- menor coste total
- validación incremental
- cierre operacional más rápido

———

## 6. Mantener compatibilidad con Agent03

Mientras tanto, seguir materializando:

- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- live_status_quotes_strict.json
- run_config_quotes_strict.json
- batch_manifest_quotes_strict.csv

pero ya como:

- export derivado
- materialización de compatibilidad
- no backend operativo primario

———

## Recomendación operativa inmediata

El siguiente paso correcto no es “reanudar el Agent02 viejo”.

El siguiente paso correcto es:

1. diseñar Agent02 v2
2. fijar el contrato de validación de un file
3. implementar:
    - inventario exacto
    - validador profundo v2
4. correr primero sobre:
    - quotes del universo <1B
5. validar que Agent03 sigue leyendo bien los exports
6. luego escalar al resto

———




## Agente2 v2 

### Fase 1: Inventory `051_quotes_v2_inventory.py`

El launcher ejecuta exactamente esto:

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_quotes_v2_inventory.py --c-
root C:\TSIS_Data\data\quotes --d-root D:\quotes
```

Importante:

```sh
- aquí todavía no usa -Root D
- aquí todavía no usa -DateFrom
- aquí todavía no usa -DateTo
- aquí todavía no usa -Limit 5000
```

051 hace esto internamente:

```sh
1. crea un directorio de salida nuevo en:
    C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/quotes_v2_inventory
    con nombre tipo YYYYMMDD_HHMMSS_quotes_v2_inventory

2. crea la estructura de persistencia del run de inventory:
    - inventory_batches/
    - inventory_checkpoint.json
    - inventory_run_manifest.json

3. empieza a recorrer recursivamente:
    - C:\TSIS_Data\data\quotes
    - D:\quotes

4. por cada quotes.parquet encontrado:
    - extrae del path:
        - ticker
        - year
        - month
        - day
        - date
    - guarda metadatos:
        - root (C o D)
        - root_path
        - file
        - relpath
        - task_key = ticker|date
        - size_bytes
        - mtime_utc
        - inventory_seen_utc

5. acumula filas en memoria por bloque operativo
    - por ejemplo 50k o 100k rows

6. cuando un bloque se completa:
    - escribe un shard incremental en:
        - inventory_batches/inventory_batch_000001.parquet
        - inventory_batches/inventory_batch_000002.parquet
        - etc.
    - actualiza:
        - inventory_checkpoint.json
        - inventory_run_manifest.json

7. mientras recorre, imprime progreso:
    - scan_C: matched=100000
    - scan_C: matched=200000
    - etc.
```

Cuando 051 termina del todo, escribe estos artefactos:

```sh
- quotes_inventory_files.parquet
- quotes_inventory_files.csv
- quotes_inventory_by_ticker.parquet
- quotes_inventory_by_ticker.csv
- quotes_inventory_summary.json
```

Todo eso queda dentro del run dir de inventario.

**Qué contiene ese inventario**

La tabla principal `quotes_inventory_files.parquet` es una fila por file físico encontrado.

Ejemplo conceptual:
```sh
- root = D
- file = D:\quotes\AABA\year=2017\month=06\day=19\quotes.parquet
- ticker = AABA
- date = 2017-06-19
- task_key = AABA|2017-06-19
```

Aquí todavía no sabemos si el parquet está bien o mal. Solo sabemos que existe y cómo está particionado.

Si quieres lanzarlo independiente sin el launcher :

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_quotes_v2_inventory.py `
--c-root C:\TSIS_Data\data\quotes `
--d-root D:\quotes `
--outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\mi_run `
--batch-size 100000 `
--resume
```


### Fase 2: Validate `052_quotes_v2_validate_batches.py`

Solo cuando 051 termina, el launcher busca el inventario recién creado y lanza 052.

Aquí sí usa tus filtros:
```sh
- -Root D
- -DateFrom 2024-01-01
- -DateTo 2024-03-31
- -Limit 5000
```

`052_quotes_v2_validate_batches.py` hace esto:

```sh
 1. lee quotes_inventory_files.parquet

2. filtra filas del inventario:
    - solo root = D
    - solo fechas entre 2024-01-01 y 2024-03-31
    - luego se queda con las primeras 5000

3. trocea esas 5000 filas en batches de 500
    - o sea, espera 10 batches

4. crea un directorio de salida nuevo en:
    C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/quotes_v2_validation
    con nombre tipo YYYYMMDD_HHMMSS_quotes_v2_validation

5. crea la estructura de persistencia del run de validate:
    - events_batches/
    - validation_checkpoint.json
    - validation_run_manifest.json

6. para cada batch:
    - toma 500 files del inventario
    - lanza 8 workers (-Workers 8)
    - cada worker llama a 
        C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/050_quotes_v2_validate_file.py
    para un file

7. 050 abre cada parquet y valida:
    - path de partición
    - columnas requeridas
    - parseo
    - timestamps
    - precios negativos
    - cruces bid/ask
    - ratios microestructurales

8. por cada file, 050 devuelve un evento estructurado

9. 052 junta los 500 eventos del batch y escribe:
    - events_batches/batch_000001.parquet
    - luego batch_000002.parquet
    - etc.

10. después de persistir cada batch:
    - actualiza validation_checkpoint.json
    - actualiza validation_run_manifest.json
    - registra:
        - batch_id escrito
        - files_selected del batch
        - events_written
        - filtros efectivos del run
        - último batch persistido
        - batches completados
        - rows validadas acumuladas

11. al finalizar todos los batches:
    - escribe batch_manifest_quotes_v2.csv
    - escribe batch_manifest_quotes_v2.parquet
    - escribe validation_run_summary.json
```

Qué contiene cada evento de validación

Cada file validado produce una fila como esta, conceptualmente:

```sh
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
- run_id = quotes_v2_q1_2024_d
- batch_id = batch_00000X
- scan_reason = rescan_all
- validation_kind = normal_validation
```

Artefactos esperados

```sh
Además de los outputs actuales, se espera que el run de validate produzca y mantenga estos artefactos de control:

- events_batches/
    - batch_000001.parquet
    - batch_000002.parquet
    - ...
- validation_checkpoint.json
- validation_run_manifest.json
- batch_manifest_quotes_v2.csv
- batch_manifest_quotes_v2.parquet
- validation_run_summary.json
```


### Fase 3: Materialize `053_quotes_v2_materialize_current.py`

Solo cuando 052 termina, el launcher llama a 053_quotes_v2_materialize_current.py.

053 hace esto:

```sh
1. lee validation_checkpoint.json y validation_run_manifest.json si existen
    - para conocer:
        - batches completados
        - último batch persistido
        - estado del run
        - si la validación está finalizada o parcial

2. lee los batch_*.parquet confirmados de events_batches
    - no solo los batch files presentes
    - sino los batch files reconocidos como persistidos válidamente por el manifest/checkpoint

3. concatena todos los eventos válidos

4. deriva current:
    - una fila por file
    - se queda con el último evento por file

5. enriquece current con el inventario:
    - root
    - task_key
    - present_in_c
    - present_in_d
    - present_in_both

6. deriva retry_current:
    - básicamente todos los files cuyo severity != PASS

7. deriva retry_frozen
    - ahora mismo queda vacío por diseño inicial

8. calcula estado de materialización:
    - partial o final
    - según el estado del validate y los batches confirmados

9. escribe outputs “contractuales” para Agent03

10. escribe materialization_summary.json enriquecido con:
    - events_rows
    - current_rows
    - retry_current_rows
    - retry_frozen_rows
    - batches_read
    - batches_confirmed
    - materialization_mode
    - validation_completion_status

11. escribe live_status_quotes_strict.json enriquecido con:
    - materialization_utc
    - backend_mode
    - current_materialized_from
    - retry_materialized_from
    - validation_checkpoint_source
    - validation_manifest_source
    - validation_completion_status
    - materialization_scope
```

**Qué esperamos al final de todo el proceso**

Si el pipeline completo termina bien, el resultado final estará en un directorio de validación tipo:

```sh
C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/quotes_v2_validation
```

y contendrá al menos:

```sh
- events_batches\batch_000001.parquet
- events_batches\batch_000002.parquet
- ...
- validation_checkpoint.json
- validation_run_manifest.json
- batch_manifest_quotes_v2.csv
- batch_manifest_quotes_v2.parquet
- validation_run_summary.json
- quotes_current.parquet
- quotes_current.csv
- retry_current.parquet
- retry_current.csv
- retry_frozen.parquet
- retry_frozen.csv
- quotes_agent_strict_events_current.csv
- retry_queue_quotes_strict_current.csv
- retry_frozen_quotes_strict.csv
- live_status_quotes_strict.json
- materialization_summary.json
```

Qué significan esos outputs finales

```sh
- events_batches/*.parquet
    - log append-only por lotes de validación confirmados
- validation_checkpoint.json
    - último punto confirmado del validate
- validation_run_manifest.json
    - manifiesto del run de validate y batches persistidos
- validation_run_summary.json
    - resumen del run de validación
- quotes_current.*
    - estado vigente por file
- retry_current.*
    - cola operativa de retry
- retry_frozen.*
    - subconjunto congelado fuera del retry activo
- quotes_agent_strict_events_current.csv
    - export compatible con Agent03
- retry_queue_quotes_strict_current.csv
    - export compatible con Agent03
- retry_frozen_quotes_strict.csv
    - export compatible con Agent03
- live_status_quotes_strict.json
    - resumen vivo del run y del estado de materialización
- materialization_summary.json
    - resumen técnico de la materialización current/retry/live
```

La secuencia de trabajo queda así:

```
1. lanzar 051
2. verificar inventario
3. lanzar 052
4. verificar validate
5. lanzar 053
6. verificar materialización final
```

Operativamente, esto te da:

```
- control explícito del outdir de cada fase
- reanudación clara en 051 y 052
- inspección intermedia antes de avanzar
- menos riesgo de repetir trabajo por culpa del launcher
```

La disciplina correcta ahora es:

```
- 051 no se da por bueno solo porque termine
    - hay que revisar:
        - quotes_inventory_files.parquet
        - quotes_inventory_summary.json
        - inventory_checkpoint.json
        - inventory_run_manifest.json
- 052 no se da por bueno solo porque escriba batches
    - hay que revisar:
        - events_batches/
        - validation_checkpoint.json
        - validation_run_manifest.json
        - batch_manifest_quotes_v2.csv
        - validation_run_summary.json
- 053 no se da por bueno solo porque escriba csv/parquet
    - hay que revisar:
        - quotes_current.*
        - retry_current.*
        - live_status_quotes_strict.json
        - materialization_summary.json
```

### Lanzaderas

**1. Inventory 051**

```sh
**Lanzo 051**

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\051_quotes_v2_inventory.py --c-root C:\TSIS_Data\data\quotes --d-root D:\quotes --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026 --batch-size 100000 --resume

=== SUMMARY ===
{
  "outdir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026",
  "c_root": "C:\\TSIS_Data\\data\\quotes",
  "d_root": "D:\\quotes",
  "resume": true,
  "batch_size": 100000,
  "c_inventory": {
    "root": "C",
    "rows": 1767826,
    "task_keys": 1767826,
    "tickers": 3100,
    "date_min": "2005-01-03",
    "date_max": "2026-03-06",
    "total_bytes": 136207705211
  },
  "d_inventory": {
    "root": "D",
    "rows": 8170261,
    "task_keys": 8170261,
    "tickers": 5207,
    "date_min": "2003-09-10",
    "date_max": "2026-03-20",
    "total_bytes": 673314757477
  },
  "all_rows": 9938087,
  "all_task_keys": 9937919,
  "all_tickers": 5207,
  "outputs": {
    "quotes_inventory_files_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\quotes_inventory_files.parquet",
    "quotes_inventory_files_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\quotes_inventory_files.csv",
    "quotes_inventory_by_ticker_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\quotes_inventory_by_ticker.parquet",
    "quotes_inventory_by_ticker_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\quotes_inventory_by_ticker.csv",
    "summary_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\quotes_inventory_summary.json",
    "checkpoint_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\inventory_checkpoint.json",
    "manifest_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\inventory_run_manifest.json",
    "inventory_batches_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\quotes_v2_inventory\\quotes_inventory_2005_2026\\inventory_batches"
  }
}
```

**2. Validate 052**


```sh
# smoke 2024
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_quotes_v2_validate_batches.py
`
--inventory-parquet C:
\TSIS_Data\v1\backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.p
arquet `
--outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_q1_2024_d_smoke `
--run-id quotes_validate_q1_2024_d_smoke `
--workers 8 `
--chunk-size 500 `
--root D `
--date-from 2024-01-01 `
--date-to 2024-03-31 `
--limit 5000 `
--scan-reason rescan_all `
--validation-kind normal_validation `
--resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_quotes_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_q1_2024_d_smoke --run-id quotes_validate_q1_2024_d_smoke --workers 8 --chunk-size 500 --root D --date-from 2024-01-01 --date-to 2024-03-31 --limit 5000 --scan-reason rescan_all --validation-kind normal_validation --resume

# 2005-2026 full
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_quotes_v2_validate_batches.py
`
--inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet `
--outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_2005_2026_d_full `
--run-id quotes_validate_2005_2026_d_full `
--workers 8 `
--chunk-size 500 `
--root D `
--date-from 2005-01-01 `
--date-to 2026-03-31 `
--scan-reason rescan_all `
--validation-kind normal_validation `
--resume

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\052_quotes_v2_validate_batches.py --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_2005_2026_d_full --run-id quotes_validate_2005_2026_d_full --workers 8 --chunk-size 500 --root D --date-from 2005-01-01 --date-to 2026-03-31 --scan-reason rescan_all --validation-kind normal_validation --resume
```

**3. Materialize 053**


```sh
# materialize smoke 2024
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_quotes_v2_materialize_current.py    
    --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_q1_2024_d_smoke 
    --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet 
    --run-id quotes_validate_q1_2024_d_smoke

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_quotes_v2_materialize_current.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_q1_2024_d_smoke --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet --run-id quotes_validate_q1_2024_d_smoke

# materialize 2005-2026 full
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_quotes_v2_materialize_current.py `
    --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_2005_2026_d_full `
    --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet 
    --run-id quotes_validate_2005_2026_d_full

python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\053_quotes_v2_materialize_current.py --validation-outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_validation\quotes_validate_2005_2026_d_full --inventory-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_files.parquet --run-id quotes_validate_2005_2026_d_full
```

Qué identifica un lanzamiento


```sh
- En 051, lo que manda es el outdir.
    - Si vuelves a usar el mismo outdir con --resume, es el mismo run.
    - Si usas otro outdir, es otro run.
- En 052, mandan dos cosas:
    - outdir
    - run_id
- En 053, también:
    - validation_outdir
    - run_id
```

Cuál es el identificador realmente importante


```sh
- El identificador fuerte para no mezclar runs es el outdir.
- run_id es semántico y queda grabado dentro de eventos y resúmenes.
- batch_id no identifica un run global; solo identifica lotes dentro de un outdir.
```

**Cómo sabe el sistema que un relanzamiento es “el mismo trabajo”**

Porque apuntas al mismo outdir:
```sh
- mismo inventory_outdir en 051
- mismo validation_outdir en 052
```
Ahí están:
```sh
- inventory_checkpoint.json
- inventory_run_manifest.json
- validation_checkpoint.json
- validation_run_manifest.json
```


# Notebooks, revisión

