# Auditoria General `<1B` Replanteamiento

## Contexto

Este documento recoge el replanteamiento de `01_auditoria_1B_general.ipynb` tras revisar:

- `00_auditoria_general.md`
- `01_auditoria_1B_general.ipynb`
- `quotes/02_diseno_arquitectura_quotes_CD.md`
- `trades/03_diseno_implementacion_trades_CD.md`

La conclusión es que este notebook debe centrarse ahora solo en cobertura de data, no en sanidad.

Tambien debe seguir el mismo principio arquitectonico ya fijado para `quotes` y `trades`:

- Jupyter no debe procesar el parquet full
- Jupyter no debe reconstruir la cobertura recorriendo millones de filas en vivo
- el calculo pesado debe ir fuera del notebook
- el notebook debe ser visor de artefactos pequenos y drilldown puntual

## Objetivo

Tener una visualizacion clara, nitida y facil de entender para el equipo sobre:

- que datasets tiene cada ticker del universo `<1B`
- en que ventana temporal PTI vive ese ticker
- como se solapan temporalmente los datasets disponibles
- que cobertura real existe por ticker dentro de `2005-2026`

Sin entrar todavia en:

- severidades
- issues
- warns
- validacion de calidad
- sanidad de contenido

Eso ira despues.

## Principio rector

Este notebook no debe parecerse a un ETL embebido.

Debe parecerse al patron `quotes/trades`:

1. `build`
   Script offline pesado, fuera de Jupyter, que construye caches de cobertura.

2. `view`
   Notebook ligero que solo lee:
   - `manifest.json`
   - tablas agregadas
   - indices pequenos
   - caches temporales ya materializados

3. `drilldown`
   Carga puntual bajo demanda para un ticker concreto o una vista puntual.

Regla operativa:

- Jupyter no procesa el full
- Jupyter consume artefactos
- el parquet bruto solo se toca en `build` o en un drilldown muy concreto

## Lo que no debemos hacer

- no cargar `quotes_current.parquet` full en notebook
- no cargar `trades_current.parquet` full en notebook
- no expandir ventanas PTI completas a diario dentro de celdas si eso provoca joins gigantes
- no repetir lecturas full por bloque visual
- no mezclar semanticas distintas de cobertura en una sola matriz binaria sin contexto

## Enfoque correcto para cobertura

Hay que separar datasets por tipo de cobertura.

### A. Datasets densos de mercado

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`

Estos si deben entrar en el eje principal de cobertura temporal y solape.

### B. Datasets de eventos

- `halts`

Esto no debe tratarse como "missing" si no hay eventos.
Debe verse como capa de eventos sobre la vida PTI del ticker.

### C. Datasets fundamentals

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`
- `ratios`

Estos no deben tratarse como cobertura diaria.
Deben verse como cobertura de reporting o de observaciones fundamentals.

## Grano visual recomendado

El grano visual principal debe ser mensual.

Motivo:

- diario para todo el universo `<1B` es demasiado pesado para notebook y para lectura visual
- mensual permite ver solapes reales de `daily`, `1m`, `quotes` y `trades`
- mensual encaja muy bien con `ohlcv_1m`
- mensual reduce mucho el tamano de los caches

Por tanto, la pieza central debe ser:

- `ticker x month x dataset`

No `ticker x day x dataset` en notebook.

## Definicion de cobertura

### Universo base

Universo objetivo:

- `market_cap_cutoff_lt_1b_active_inactive.parquet`

Cada ticker tiene una ventana base:

- `first_seen_date`
- `last_observed_date`

Esa es la ventana PTI que gobierna la cobertura esperada.

### Cobertura para datasets densos

Para cada ticker y para cada mes dentro de su ventana PTI:

- `has_daily`
- `has_ohlcv_1m`
- `has_quotes`
- `has_trades`

Esto no es sanidad.
Solo presencia temporal.

### Cobertura para `halts`

Para cada ticker:

- numero de halts
- primer halt
- ultimo halt
- meses con evento

`halts` no pinta "hueco" cuando no hay datos.
Pinta evento cuando existe.

### Cobertura para `financials`

Para cada ticker y dataset fundamental:

- primer filing / observacion
- ultimo filing / observacion
- numero de filings
- meses o trimestres con observacion

No debe visualizarse como ausencia roja diaria.

## Arquitectura propuesta

## 1. Build offline

Script nuevo sugerido:

- `notebooks/00_data_certification/auditoria/cel_code/build_lt1b_coverage_artifacts.py`

Responsabilidad:

- leer fuentes minimas
- recorrer por columnas minimas
- agregar incrementalmente
- escribir caches pequenos reutilizables

Reglas:

- no usar `parts.append(...)` gigantes para luego concatenar todo
- agregar en streaming
- no expandir mas de lo necesario
- usar mensual como unidad central

### Inputs principales

- `market_cap_cutoff_lt_1b_active_inactive.parquet`
- `daily_inventory_by_ticker.parquet`
- `ohlcv_1m_inventory_by_ticker.parquet`
- `quotes_inventory_by_ticker.parquet`
- `trades_inventory_by_ticker.parquet`

Y para la construccion real del mapa temporal mensual:

- `daily_current.parquet` o inventario equivalente por ano si basta para mensual
- `ohlcv_1m_current.parquet` o inventario mensual
- `quotes_current.parquet` por batches y columnas minimas `ticker,date`
- `trades_current.parquet` por batches y columnas minimas `ticker,date`
- `halts_master_multisource.parquet`
- parquets de `financial`

### Columnas minimas por fuente

Usar siempre proyecciones minimas:

- `daily`: `ticker, year`
- `ohlcv_1m`: `ticker, year, month`
- `quotes`: `ticker, date`
- `trades`: `ticker, date`
- `halts`: `ticker, halt_date`
- `financials`:
  - `ticker, filing_date, period_end`
  - o `ticker, date` si el dataset ya viene asi

## 2. View en notebook

`01_auditoria_1B_general.ipynb` debe quedar como visor.

La primera celda no debe cargar el full parquet.

Debe abrir solo:

- `manifest.json`
- `exec_summary.parquet`
- `dataset_coverage_summary.parquet`
- `dataset_overlap_summary.parquet`
- `ticker_coverage_summary.parquet`
- `ticker_month_coverage.parquet`
- `event_month_overlay.parquet`
- `case_index_coverage.parquet`

## 3. Drilldown puntual

Si el usuario quiere revisar un ticker concreto:

- el notebook filtra `case_index_coverage`
- y solo entonces abre el subconjunto puntual necesario

Nunca debe reescanear los full en una vista normal.

## Artefactos offline recomendados

### Resumen ejecutivo

- `exec_summary.parquet`
- `dataset_coverage_summary.parquet`
- `dataset_overlap_summary.parquet`

### Cobertura por ticker

- `ticker_coverage_summary.parquet`

Una fila por ticker.

Columnas recomendadas:

- `ticker`
- `classification_1b`
- `pti_start`
- `pti_end`
- `pti_months`
- `daily_obs_start`
- `daily_obs_end`
- `daily_months_present`
- `daily_coverage_pct`
- `ohlcv_1m_obs_start`
- `ohlcv_1m_obs_end`
- `ohlcv_1m_months_present`
- `ohlcv_1m_coverage_pct`
- `quotes_obs_start`
- `quotes_obs_end`
- `quotes_months_present`
- `quotes_coverage_pct`
- `trades_obs_start`
- `trades_obs_end`
- `trades_months_present`
- `trades_coverage_pct`
- `halts_events_total`
- `halts_first_date`
- `halts_last_date`
- `income_filings_total`
- `balance_filings_total`
- `cash_flow_filings_total`
- `ratio_points_total`

### Cobertura temporal mensual

- `ticker_month_coverage.parquet`

Columnas recomendadas:

- `ticker`
- `month`
- `in_pti_window`
- `has_daily`
- `has_ohlcv_1m`
- `has_quotes`
- `has_trades`
- `has_halts_event`
- `has_income_statement`
- `has_balance_sheet`
- `has_cash_flow_statement`
- `has_ratio`

### Overlay de eventos

- `event_month_overlay.parquet`

Para enriquecer la visualizacion sin contaminar el mapa principal.

### Indice para widgets

- `case_index_coverage.parquet`

Una fila por ticker visualizable.

Columnas sugeridas:

- `ticker`
- `display_label`
- `pti_start`
- `pti_end`
- `missing_datasets_count`
- `coverage_bucket`
- `top_gap_dataset`
- `top_gap_month`
- `rank_score`

### Control

- `manifest.json`
- `build_log.json`

## Tres propuestas de visualizacion

## Propuesta 1. Coverage Map por ticker

La mas clara para equipo.

Formato:

- una fila por ticker
- columnas por dataset
- en cada dataset:
  - inicio observado
  - fin observado
  - meses presentes
  - `% cobertura`
- al lado, mini timeline mensual condensado

Responde muy bien:

- que tiene este ticker
- desde cuando
- hasta cuando
- que datasets le faltan

Artefactos necesarios:

- `ticker_coverage_summary.parquet`
- `ticker_month_coverage.parquet`

## Propuesta 2. Timeline matricial ticker x mes

La mejor para ver solape temporal real.

Formato:

- eje Y: tickers
- eje X: meses `2005-2026`
- una banda por dataset

Colores:

- azul: hay data
- blanco: no hay data
- gris: fuera de ventana PTI

`halts` y `financials` deben entrar como overlay de eventos/observaciones, no como missing.

Responde muy bien:

- donde se solapan `daily`, `1m`, `quotes` y `trades`
- donde empieza y acaba cada dataset dentro de la vida del ticker

Artefactos necesarios:

- `ticker_month_coverage.parquet`
- `event_month_overlay.parquet`

## Propuesta 3. Ladder de cobertura del universo

La mejor como portada del notebook.

Formato:

- total tickers `<1B`
- tickers con `daily`
- tickers con `1m`
- tickers con `quotes`
- tickers con `trades`
- tickers con `financials`
- tickers con `halts`

Mas abajo:

- tabla de intersecciones:
  - `daily & 1m`
  - `daily & quotes`
  - `daily & trades`
  - `all market data`
  - `all market data + financials`

Responde muy bien:

- cuanto universo tenemos realmente cubierto por dataset
- que intersecciones son fuertes
- donde estan los grandes huecos de cobertura

Artefactos necesarios:

- `exec_summary.parquet`
- `dataset_overlap_summary.parquet`

## Recomendacion

La recomendacion es combinar:

- Propuesta 3 como portada ejecutiva
- Propuesta 1 como tabla principal por ticker
- Propuesta 2 como drilldown visual temporal

Eso da una lectura muy clara y evita saturar la memoria del notebook.

## Estructura recomendada del notebook final

1. Cargar `manifest.json` y resumen de artefactos
2. Mostrar resumen ejecutivo del universo `<1B`
3. Mostrar ladder de cobertura global
4. Mostrar tabla de overlaps entre datasets
5. Mostrar tabla por ticker con filtros
6. Mostrar timeline mensual para ticker o grupo seleccionado
7. Mostrar overlay de `halts` y `financials`
8. Drilldown puntual de ticker

## Siguiente paso correcto

No rehacer primero el notebook.

El siguiente paso correcto es:

1. construir el builder offline de cobertura `<1B`
2. definir y materializar los artefactos pequenos
3. refactorizar `01_auditoria_1B_general.ipynb` para que solo lea esos artefactos

## Decision tomada

Por ahora:

- este notebook queda enfocado solo a cobertura
- no entra todavia sanidad
- se adopta el patron `build + view + drilldown`
- se evita cargar full parquets en Jupyter
- el eje principal sera `ticker x month x dataset`

## Estado real del notebook

La refactorizacion ya esta hecha en el notebook actual.

`01_auditoria_1B_general.ipynb` ya no esta en modo ETL embebido.
El notebook real:

- tiene 9 celdas en total
- tiene 8 celdas de codigo ejecutadas
- consume artefactos desde `cache_lt1b_coverage`
- no lee `quotes_current.parquet` ni `trades_current.parquet` full
- funciona como visor ligero con drilldown puntual

Por tanto, este documento debe leerse como contrato y criterio de interpretacion del notebook actual, no como una refactorizacion aun pendiente.

## Refactorizacion celda por celda

La referencia historica a un notebook de 14 celdas ya no aplica al estado actual.

El notebook vigente tiene esta estructura:

1. portada markdown
2. carga de rutas, validacion de artefactos y lectura de `manifest.json`
3. carga de artefactos ejecutivos
4. ladder global del universo `<1B`
5. overlaps entre datasets
6. tabla principal por ticker y buckets
7. seleccion de ticker para drilldown
8. heatmap mensual de market data
9. overlay mensual de eventos y fundamentals

Problema principal del estado actual:

- ya no mezcla ETL pesado con visualizacion
- el punto delicado ahora es semantico:
  - como nombramos buckets
  - como interpretamos presencia vs cobertura temporal
  - como distinguimos cobertura de sanidad

La refactorizacion correcta es convertirlo en un visor de artefactos.

## Mapa de sustitucion

No hace falta mantener aqui un mapa de sustitucion contra las antiguas 14 celdas.
Ese estado ya no representa el notebook vigente.

## Notebook nuevo recomendado

El notebook refactorizado deberia quedar en 10 celdas.

Nota:

- el notebook real ya esta muy cerca de ese objetivo
- hoy tiene 9 celdas
- su arquitectura efectiva ya es `build + view + drilldown`

## Semantica correcta de buckets

El punto mas importante a fijar es este:

`coverage_bucket` no mide sanidad ni cobertura temporal fuerte.

Mide solo presencia estructural de datasets dentro del ticker.

Semantica actual observada:

- `all_market_data`
  - el ticker tiene al menos una observacion en:
    - `daily`
    - `ohlcv_1m`
    - `quotes`
    - `trades`
  - no implica cobertura temporal alta
  - no implica continuidad
  - no implica calidad

- `missing_quotes`
  - el ticker tiene `daily`, `ohlcv_1m`, `trades`
  - pero no tiene `quotes`

- `partial_market_data`
  - falta mas de una pieza de market data
  - o el ticker no alcanza el set minimo de los cuatro datasets densos

Esto significa que un ticker puede aparecer en `all_market_data` y aun asi tener:

- `quotes_coverage_pct` bajo
- `trades_coverage_pct` bajo
- grandes huecos temporales dentro de su vida PTI

Por tanto, `all_market_data` debe leerse como:

- "presencia en los cuatro datasets"

y no como:

- "ticker bien cubierto"

## Nombres recomendados para evitar ambiguedad

Si mas adelante decides renombrar los buckets en builder y notebook, la opcion mas clara es:

- `all_market_data` -> `has_all_market_datasets`
- `missing_quotes` -> `has_market_data_except_quotes`
- `partial_market_data` -> `missing_multiple_market_datasets`

Alternativa mas corta:

- `all_market_data` -> `all_present`
- `missing_quotes` -> `quotes_absent`
- `partial_market_data` -> `partial_present`

La primera opcion es mejor porque deja mucho menos espacio para interpretar cobertura temporal como si fuera completitud.

## Reglas de lectura del notebook

Para interpretar bien las tablas del notebook:

1. `*_has_any`
   significa presencia observada alguna vez para el ticker.

2. `*_months_present`
   significa cuantos meses tienen observacion.

3. `*_coverage_pct`
   significa porcentaje de meses cubiertos dentro de la ventana PTI del ticker.

4. `coverage_bucket`
   resume presencia estructural, no calidad ni completitud temporal.

5. `top_gap_dataset`
   apunta al dataset con mayor hueco relativo para ese ticker.

## Artefactos y esquema real observados

Artefactos consumidos por el notebook actual:

- `manifest.json`
- `build_log.json`
- `exec_summary.parquet`
- `dataset_coverage_summary.parquet`
- `dataset_overlap_summary.parquet`
- `ticker_coverage_summary.parquet`
- `ticker_month_coverage.parquet`
- `event_month_overlay.parquet`
- `case_index_coverage.parquet`

Esquema importante:

- `top_gap_month` esta en `case_index_coverage.parquet`
- `top_gap_month` no esta en `ticker_coverage_summary.parquet`

Esto importa para no documentar columnas en tablas donde realmente no existen.

## Celda 0. Portada y contrato del notebook

Tipo:

- markdown

Objetivo:

- explicar que este notebook audita cobertura `<1B`
- dejar claro que no entra todavia sanidad
- definir datasets cubiertos

Contenido recomendado:

- universo `<1B`
- ventana PTI por ticker
- datasets densos: `daily`, `ohlcv_1m`, `quotes`, `trades`
- overlays: `halts`, `financials`
- regla: notebook visor, no procesador full

## Celda 1. Carga minima de artefactos

Tipo:

- code

Debe hacer solo:

- importar librerias ligeras
- definir `CACHE_ROOT`
- abrir `manifest.json`
- validar existencia de artefactos

Inputs:

- `manifest.json`
- rutas de los caches

Outputs en memoria:

- `manifest`
- `artifact_paths`

No debe hacer:

- `pd.read_parquet(...)` sobre `quotes_current` o `trades_current`
- construir coverage desde cero

## Celda 2. Resumen ejecutivo del build

Tipo:

- code

Debe leer solo:

- `exec_summary.parquet`
- o `dataset_coverage_summary.parquet`

Debe mostrar:

- tickers objetivo `<1B`
- rango PTI agregado
- tickers con data por dataset
- meses observados por dataset

Salida visual:

- tabla compacta de resumen

Equivale a:

- reemplazar las actuales celdas 2 y 3, pero usando artefactos pequeños

## Celda 3. Ladder de cobertura global

Tipo:

- code

Debe leer solo:

- `dataset_coverage_summary.parquet`

Debe pintar:

- total universo
- cobertura por dataset
- opcionalmente `% tickers con presencia`

Grafico recomendado:

- barra horizontal o vertical simple

Esta sera la nueva portada visual del notebook.

## Celda 4. Overlap entre datasets

Tipo:

- code

Debe leer:

- `dataset_overlap_summary.parquet`

Debe mostrar:

- `daily & 1m`
- `daily & quotes`
- `daily & trades`
- `quotes & trades`
- `all market data`

Visualizacion recomendada:

- tabla ordenada por cardinalidad
- heatmap pequeno de intersecciones si aporta claridad

Esta celda sustituye la logica binaria gruesa de las celdas 8, 10 y 12 actuales.

## Celda 5. Tabla principal por ticker

Tipo:

- code

Debe leer:

- `ticker_coverage_summary.parquet`

Debe mostrar:

- una tabla filtrable por ticker
- inicio y fin PTI
- inicio y fin observado por dataset
- `% cobertura` por dataset
- contadores resumidos de `halts` y `financials`

Columnas minimas recomendadas:

- `ticker`
- `classification_1b`
- `pti_start`
- `pti_end`
- `daily_coverage_pct`
- `ohlcv_1m_coverage_pct`
- `quotes_coverage_pct`
- `trades_coverage_pct`
- `halts_events_total`
- `income_filings_total`

Esta es la celda central del notebook.

## Celda 6. Selector de ticker o grupo

Tipo:

- code

Debe leer:

- `case_index_coverage.parquet`

Debe crear:

- selector de ticker
- filtro por bucket de cobertura
- ranking por `rank_score`

Ejemplos de bucket:

- `all_market_data`
- `missing_quotes`
- `missing_trades`
- `partial_market_data`
- `only_daily_1m`

Regla:

- el widget filtra `case_index_coverage`
- no filtra el full dataset bruto

## Celda 7. Timeline mensual del ticker seleccionado

Tipo:

- code

Debe leer:

- `ticker_month_coverage.parquet`

Debe filtrar solo:

- el ticker o grupo seleccionado

Debe pintar:

- eje X: meses
- filas o bandas: `daily`, `ohlcv_1m`, `quotes`, `trades`

Colores:

- gris: fuera PTI
- blanco: dentro PTI sin data
- azul: data presente

Esta celda es la heredera correcta de la narrativa de timeline de la celda 13 actual.

## Celda 8. Overlay de halts y financials

Tipo:

- code

Debe leer:

- `event_month_overlay.parquet`

Debe pintar:

- marcas de meses con `halts`
- marcas de meses con observaciones de `income`
- marcas de meses con observaciones de `balance`
- marcas de meses con observaciones de `cash_flow`
- marcas de meses con observaciones de `ratios`

Esto debe verse como capa adicional, no como heatmap de missing.

## Celda 9. Drilldown puntual

Tipo:

- code

Debe activarse solo si el usuario selecciona un ticker.

Debe usar:

- un loader puntual
- lectura minima por ticker

Puede mostrar:

- tabla mensual detallada del ticker
- resumen de ventanas continuas por dataset
- lista de meses donde aparece cada dataset

Si hiciera falta, esta es la unica celda donde podria abrirse una fuente mas detallada.

Pero siempre por ticker puntual, nunca full.

## Builder offline necesario

Antes de tocar el notebook, hay que construir este script:

- `notebooks/00_data_certification/auditoria/cel_code/build_lt1b_coverage_artifacts.py`

Debe producir estos artefactos:

- `manifest.json`
- `build_log.json`
- `exec_summary.parquet`
- `dataset_coverage_summary.parquet`
- `dataset_overlap_summary.parquet`
- `ticker_coverage_summary.parquet`
- `ticker_month_coverage.parquet`
- `event_month_overlay.parquet`
- `case_index_coverage.parquet`

## Logica minima del builder

### Paso 1. Universo base

Leer:

- `market_cap_cutoff_lt_1b_active_inactive.parquet`

Construir:

- universo de tickers
- `pti_start`
- `pti_end`
- malla mensual PTI por ticker

No construir malla diaria salvo que sea estrictamente necesaria para una agregacion puntual.

### Paso 2. Cobertura `daily`

Fuente recomendada:

- `daily_inventory_by_ticker.parquet`
- si hace falta precision mensual, usar fuente mensual derivada o `daily_current` con proyeccion minima

Construir:

- primer y ultimo ano observado
- meses cubiertos si se materializa a mensual

### Paso 3. Cobertura `ohlcv_1m`

Fuente recomendada:

- `ohlcv_1m_inventory_by_ticker.parquet`
- o `ohlcv_1m_current` si se necesita trazabilidad mensual exacta

Construir:

- meses presentes por ticker
- primera y ultima observacion

### Paso 4. Cobertura `quotes`

Fuente:

- `quotes_current.parquet`

Lectura:

- solo `ticker,date`
- por batches pequenos

Construir:

- meses presentes por ticker
- primer y ultimo mes observado

No debe:

- expandir `metrics_json`
- tocar columnas pesadas

### Paso 5. Cobertura `trades`

Fuente:

- `trades_current.parquet`

Lectura:

- solo `ticker,date`
- por batches pequenos

Construir:

- meses presentes por ticker
- primer y ultimo mes observado

### Paso 6. Overlay `halts`

Fuente:

- `halts_master_multisource.parquet`

Construir:

- eventos por ticker
- meses con halt
- primer y ultimo halt

### Paso 7. Overlay `financials`

Fuentes:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`
- `ratios`

Construir:

- meses o trimestres con observacion
- primer y ultimo filing/observacion
- conteo por ticker

### Paso 8. Artefactos finales

Agregaciones finales:

- resumen ejecutivo
- overlap matrix
- resumen por ticker
- malla mensual
- indice para widgets

## Correspondencia exacta con notebook actual

### Celda actual 0

Estado:

- texto libre y mezcla de ideas

Accion:

- reescribir completa

### Celda actual 1

Estado:

- bootstrap util, pero probablemente mezcla demasiado

Accion:

- conservar solo imports, helpers ligeros y carga de `manifest`

### Celda actual 2

Estado:

- resumen de artefactos por dataset

Accion:

- sustituir por lectura de `exec_summary`

### Celda actual 3

Estado:

- cobertura binaria por ticker

Accion:

- sustituir por `ticker_coverage_summary`

### Celda actual 4

Estado:

- expansion diaria PTI

Accion:

- eliminar del notebook
- mover al builder si de verdad hace falta

### Celda actual 5

Estado:

- merge grande `expected_daily` vs inventarios

Accion:

- eliminar del notebook
- mover completo al builder

### Celda actual 6

Estado:

- calculo de faltantes por ticker y fecha

Accion:

- sustituir por lectura de `case_index_coverage`

### Celda actual 7

Estado:

- markdown de idea visual

Accion:

- mantener la idea, pero reescribir narrativa segun nuevo flujo

### Celdas actuales 8, 10, 12, 13

Estado:

- graficos utiles pero apoyados en `DataFrame` construidos en vivo

Accion:

- reescribir para que lean solo caches pequenos

### Celdas actuales 9 y 11

Estado:

- markdown de soporte

Accion:

- compactar y reordenar

## Orden correcto de trabajo

1. Definir contrato final de artefactos offline
2. Implementar `build_lt1b_coverage_artifacts.py`
3. Ejecutar build offline
4. Revisar cardinalidad y tamano de caches
5. Refactorizar `01_auditoria_1B_general.ipynb`
6. Ajustar visuales y widgets

## Criterio de aceptacion

Diremos que la refactorizacion esta bien hecha cuando:

- la primera celda no lea ningun parquet full
- el notebook abra rapido
- el notebook no dispare memoria virtual
- la narrativa visual deje claro por ticker que data existe
- el equipo pueda ver facil el solape temporal entre datasets
- `halts` y `financials` aparezcan como overlays y no como falsos missing

## Contrato exacto de artefactos offline

Este bloque fija el contrato operativo para implementar:

- `build_lt1b_coverage_artifacts.py`

La idea es que despues no haya ambiguedad sobre:

- nombres de archivos
- columnas
- claves
- semantica de cada campo
- reglas de construccion

## Ubicacion recomendada

Output root sugerido:

- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\cache_lt1b_coverage\`

Dentro de ese root:

- `manifest.json`
- `build_log.json`
- `exec_summary.parquet`
- `dataset_coverage_summary.parquet`
- `dataset_overlap_summary.parquet`
- `ticker_coverage_summary.parquet`
- `ticker_month_coverage.parquet`
- `event_month_overlay.parquet`
- `case_index_coverage.parquet`

Regla:

- no escribir dentro de los runs productivos
- no mezclar estos caches con `quotes` o `trades`

## Convenciones generales

### Normalizacion de ticker

Siempre:

- `str.strip().upper()`

### Tipo de fecha

Reglas:

- columnas `*_date` en formato timestamp o datetime parseable
- columna `month` como primer dia del mes
- ejemplo: `2020-05-01`

### Semantica de ventana PTI

Para cada ticker `<1B`:

- `pti_start = first_seen_date`
- `pti_end = last_observed_date`

Regla:

- ambos incluidos

### Semantica mensual

Un mes pertenece a la ventana PTI del ticker si:

- el primer dia del mes es `<= pti_end`
- y el ultimo dia del mes es `>= pti_start`

Pragmaticamente:

- basta con construir todos los meses entre `pti_start.to_period("M")` y `pti_end.to_period("M")`

### Datasets densos

Para:

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`

La variable principal es:

- `has_<dataset>`

Significado:

- existe al menos una observacion de ese dataset para ese `ticker, month`

No significa:

- cobertura completa del mes
- calidad buena
- sanidad

### Datasets de overlay

Para:

- `halts`
- `income`
- `balance`
- `cash_flow`
- `ratio`

El campo significa:

- existe al menos un evento u observacion en ese `ticker, month`

No debe interpretarse como missing si vale `False`.

## Archivo 1. `manifest.json`

Objetivo:

- describir el build ejecutado
- validar reproducibilidad
- permitir que el notebook enseñe metadata sin tocar fuentes pesadas

Claves minimas:

- `build_name`
- `build_version`
- `built_at_utc`
- `output_root`
- `universe_source`
- `inputs`
- `artifacts`
- `row_counts`
- `build_params`

### `inputs`

Debe incluir como minimo:

- `lt1b_universe_parquet`
- `daily_inventory_by_ticker`
- `ohlcv_1m_inventory_by_ticker`
- `quotes_inventory_by_ticker`
- `trades_inventory_by_ticker`
- `quotes_current`
- `trades_current`
- `halts_master_multisource`
- `financial_income_root`
- `financial_balance_root`
- `financial_cash_flow_root`
- `financial_ratios_root`

### `artifacts`

Mapa nombre a ruta relativa:

- `exec_summary`
- `dataset_coverage_summary`
- `dataset_overlap_summary`
- `ticker_coverage_summary`
- `ticker_month_coverage`
- `event_month_overlay`
- `case_index_coverage`

### `row_counts`

Debe incluir:

- `lt1b_tickers`
- `ticker_month_rows`
- `ticker_coverage_rows`
- `event_overlay_rows`
- `case_index_rows`

### `build_params`

Debe incluir:

- `month_grain`
- `quotes_batch_size`
- `trades_batch_size`
- `include_financial_overlays`
- `include_halts_overlay`

## Archivo 2. `build_log.json`

Objetivo:

- trazabilidad de ejecucion

Claves minimas:

- `started_at_utc`
- `finished_at_utc`
- `duration_sec`
- `steps`
- `warnings`

`steps` debe listar:

- `load_universe`
- `build_pti_month_grid`
- `load_daily`
- `load_ohlcv_1m`
- `scan_quotes_current`
- `scan_trades_current`
- `scan_halts`
- `scan_financials`
- `write_artifacts`

## Archivo 3. `exec_summary.parquet`

Objetivo:

- portada ejecutiva del notebook

Grano:

- una sola fila

Columnas:

- `universe_name`
- `as_of_date`
- `lt1b_tickers_total`
- `pti_min_date`
- `pti_max_date`
- `pti_month_rows_total`
- `tickers_with_daily`
- `tickers_with_ohlcv_1m`
- `tickers_with_quotes`
- `tickers_with_trades`
- `tickers_with_any_market_data`
- `tickers_with_all_market_data`
- `tickers_with_halts`
- `tickers_with_income`
- `tickers_with_balance`
- `tickers_with_cash_flow`
- `tickers_with_ratio`

Regla:

- `all_market_data = daily + ohlcv_1m + quotes + trades`

## Archivo 4. `dataset_coverage_summary.parquet`

Objetivo:

- resumen global por dataset

Grano:

- una fila por dataset

Datasets esperados:

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`
- `halts`
- `income`
- `balance`
- `cash_flow`
- `ratio`

Columnas:

- `dataset`
- `dataset_kind`
- `tickers_with_data`
- `tickers_without_data`
- `months_with_data`
- `obs_min_date`
- `obs_max_date`
- `coverage_vs_universe_pct`

Semantica:

- `dataset_kind = dense_market | event | fundamental`
- `coverage_vs_universe_pct = tickers_with_data / lt1b_tickers_total`

## Archivo 5. `dataset_overlap_summary.parquet`

Objetivo:

- medir intersecciones entre datasets

Grano:

- una fila por combinacion

Columnas:

- `combo_key`
- `combo_label`
- `tickers_count`
- `pct_universe`

Combinaciones minimas:

- `daily&ohlcv_1m`
- `daily&quotes`
- `daily&trades`
- `quotes&trades`
- `daily&ohlcv_1m&quotes&trades`
- `all_market_data+income`
- `all_market_data+financials_any`

`financials_any` significa:

- al menos uno entre `income`, `balance`, `cash_flow`, `ratio`

## Archivo 6. `ticker_coverage_summary.parquet`

Objetivo:

- tabla principal por ticker

Grano:

- una fila por ticker

Clave:

- `ticker`

Columnas base:

- `ticker`
- `classification_1b`
- `classification_reason_1b`
- `pti_start`
- `pti_end`
- `pti_months`

### Bloque `daily`

- `daily_has_any`
- `daily_obs_start`
- `daily_obs_end`
- `daily_months_present`
- `daily_coverage_pct`

### Bloque `ohlcv_1m`

- `ohlcv_1m_has_any`
- `ohlcv_1m_obs_start`
- `ohlcv_1m_obs_end`
- `ohlcv_1m_months_present`
- `ohlcv_1m_coverage_pct`

### Bloque `quotes`

- `quotes_has_any`
- `quotes_obs_start`
- `quotes_obs_end`
- `quotes_months_present`
- `quotes_coverage_pct`

### Bloque `trades`

- `trades_has_any`
- `trades_obs_start`
- `trades_obs_end`
- `trades_months_present`
- `trades_coverage_pct`

### Bloque `halts`

- `halts_has_any`
- `halts_events_total`
- `halts_first_date`
- `halts_last_date`
- `halts_months_present`

### Bloque `financials`

- `income_has_any`
- `income_first_date`
- `income_last_date`
- `income_filings_total`
- `income_months_present`

- `balance_has_any`
- `balance_first_date`
- `balance_last_date`
- `balance_filings_total`
- `balance_months_present`

- `cash_flow_has_any`
- `cash_flow_first_date`
- `cash_flow_last_date`
- `cash_flow_filings_total`
- `cash_flow_months_present`

- `ratio_has_any`
- `ratio_first_date`
- `ratio_last_date`
- `ratio_points_total`
- `ratio_months_present`

### Bloque derivado de cobertura

- `market_datasets_present_count`
- `coverage_bucket`
- `top_gap_dataset`

Reglas:

- `market_datasets_present_count` cuenta solo `daily`, `ohlcv_1m`, `quotes`, `trades`
- `coverage_bucket` se asigna desde estos cuatro datasets

Buckets minimos:

- `all_market_data`
- `missing_daily`
- `missing_ohlcv_1m`
- `missing_quotes`
- `missing_trades`
- `partial_market_data`
- `no_market_data`

## Archivo 7. `ticker_month_coverage.parquet`

Objetivo:

- ser la malla central del notebook

Grano:

- una fila por `ticker, month`

Clave:

- `ticker`
- `month`

Columnas:

- `ticker`
- `month`
- `pti_start`
- `pti_end`
- `in_pti_window`
- `has_daily`
- `has_ohlcv_1m`
- `has_quotes`
- `has_trades`
- `market_datasets_present_count`

Semantica:

- `month` es el primer dia del mes
- `in_pti_window` debe ser siempre `True` dentro del archivo si el builder ya emite solo meses PTI
- si se decide emitir meses fuera de PTI para visualizacion extendida, entonces esos meses deben venir con `in_pti_window = False`

Recomendacion:

- emitir solo meses PTI para reducir tamano

## Archivo 8. `event_month_overlay.parquet`

Objetivo:

- superponer eventos y observations no densas sobre el timeline principal

Grano:

- una fila por `ticker, month`

Clave:

- `ticker`
- `month`

Columnas:

- `ticker`
- `month`
- `has_halts_event`
- `halts_events_count`
- `has_income_statement`
- `income_events_count`
- `has_balance_sheet`
- `balance_events_count`
- `has_cash_flow_statement`
- `cash_flow_events_count`
- `has_ratio`
- `ratio_points_count`

Regla:

- este archivo no participa en el calculo de gaps de market data

## Archivo 9. `case_index_coverage.parquet`

Objetivo:

- alimentar widgets y filtros sin tocar tablas grandes

Grano:

- una fila por ticker

Clave:

- `ticker`

Columnas:

- `ticker`
- `display_label`
- `classification_1b`
- `pti_start`
- `pti_end`
- `coverage_bucket`
- `market_datasets_present_count`
- `daily_coverage_pct`
- `ohlcv_1m_coverage_pct`
- `quotes_coverage_pct`
- `trades_coverage_pct`
- `top_gap_dataset`
- `top_gap_month`
- `rank_score`

Semantica:

- `display_label` ejemplo:
  - `ABCD | 2009-03 .. 2018-11 | missing_quotes`
- `rank_score` sirve para ordenar:
  - primero tickers mas interesantes para revisar

Regla recomendada para `rank_score`:

- priorizar tickers con mas meses PTI
- y con peores coberturas market data

## Reglas de construccion por fuente

## Universo `<1B`

Fuente:

- `market_cap_cutoff_lt_1b_active_inactive.parquet`

Columnas reales observadas:

- `ticker`
- `first_seen_date`
- `last_observed_date`
- `classification_1b`
- `classification_reason_1b`

Reglas:

- deduplicar por `ticker`
- descartar tickers sin `first_seen_date` o `last_observed_date`
- si `pti_end < pti_start`, loggear warning y excluir

## `daily`

Fuente minima:

- `daily_inventory_by_ticker.parquet`

Columnas reales observadas:

- `ticker`
- `year_min`
- `year_max`

Semantica:

- este inventario solo garantiza rango anual, no presencia mes a mes

Decision:

- usarlo para resumen por ticker si basta
- si queremos timeline mensual defendible, derivar mensual desde una fuente adicional mas fina

Contrato pragmatcio:

- version 1 del builder puede mapear `daily` a todos los meses entre `year_min` y `year_max`
- dejando claro en `build_log` que es una aproximacion anual expandida a mensual

## `ohlcv_1m`

Fuente minima:

- `ohlcv_1m_inventory_by_ticker.parquet`

Columnas reales observadas:

- `ticker`
- `year_min`
- `year_max`
- `month_min`
- `month_max`

Decision:

- esta fuente sirve bien para timeline mensual

Regla:

- si existe una fuente mensual mas exacta, usarla
- si no, usar el inventario para estimar rango mensual observado

## `quotes`

Fuentes:

- `quotes_inventory_by_ticker.parquet`
- `quotes_current.parquet`

Columnas reales observadas en `quotes_current`:

- `ticker`
- `date`

Regla:

- el resumen por ticker puede salir del inventory
- la malla mensual debe salir del `quotes_current.parquet` escaneado por batches

Lectura recomendada:

- `ticker,date`
- `batch_size` pequeno

Salida intermedia conceptual:

- conjunto de `ticker, month` observados en quotes

## `trades`

Fuentes:

- `trades_inventory_by_ticker.parquet`
- `trades_current.parquet`

Columnas reales observadas en `trades_current`:

- `ticker`
- `date`

Regla:

- igual que `quotes`
- summary desde inventory si ayuda
- timeline mensual desde `trades_current` por batches

## `halts`

Fuente:

- `halts_master_multisource.parquet`

Columnas reales observadas:

- `ticker`
- `halt_date`

Regla:

- parsear `halt_date`
- derivar `month`
- agrupar por `ticker, month`

## `income`, `balance`, `cash_flow`

Fuentes:

- directorios parquet por ticker

Columnas reales observadas:

- `ticker`
- `filing_date`
- `period_end`

Regla:

- usar `filing_date` como fecha principal de observacion
- si falta, fallback a `period_end`
- derivar `month`

## `ratio`

Fuente:

- directorio parquet por ticker

Columnas reales observadas:

- `ticker`
- `date`

Regla:

- derivar `month`
- agrupar por `ticker, month`

## Reglas de merge final

### Merge principal

Base:

- malla PTI mensual por ticker

Sobre esa base se hace left join de:

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`

Y aparte se hace left join de overlays:

- `halts`
- `income`
- `balance`
- `cash_flow`
- `ratio`

### Fill default

Para columnas booleanas:

- `False`

Para contadores:

- `0`

### Cálculos derivados

Por `ticker`:

- `months_present`
- `% cobertura`
- `obs_start`
- `obs_end`

Por universo:

- tickers con algun dato
- intersecciones

## Checks minimos que debe hacer el builder

- `ticker` unico en `ticker_coverage_summary`
- unicidad de `ticker, month` en `ticker_month_coverage`
- unicidad de `ticker, month` en `event_month_overlay`
- `pti_months >= months_present` para cada dataset denso
- fechas observadas dentro de rango razonable `2005-01-01` a `2026-12-31`
- `coverage_pct` entre `0` y `100`

## Criterio de version 1

Se acepta una primera version si:

- el contrato de archivos y columnas queda estable
- el notebook ya puede abrir y visualizar cobertura sin tocar full parquets
- `quotes` y `trades` ya salen de scans chunked
- `halts` y `financials` ya aparecen como overlay
- `daily` y `ohlcv_1m` quedan documentados si alguna parte de su timeline mensual es aproximada

## Siguiente paso tras este contrato

Con este contrato cerrado, el siguiente paso correcto es implementar:

- `build_lt1b_coverage_artifacts.py`

y despues refactorizar el notebook contra estos artefactos.
