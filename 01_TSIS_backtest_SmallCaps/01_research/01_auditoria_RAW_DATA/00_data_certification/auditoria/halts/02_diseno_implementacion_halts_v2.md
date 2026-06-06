# Diseno de implementacion `halts v2`

## Objetivo

Llevar `halts` al mismo patron operacional que `daily`, `ohlcv_1m`, `quotes` y `trades`:

- build offline pesado
- artefactos pequenos y reutilizables
- notebook metodologico
- notebook de closeout

## Regla arquitectonica

- Jupyter no debe releer todo el raw.
- Jupyter no debe reconstruir deduplicacion pesada.
- Jupyter debe consumir artefactos pequenos ya materializados.
- El raw solo debe tocarse en el builder o en drilldown puntual.

## Estructura objetivo

- `halts/01_contrato_halts.md`
- `halts/02_diseno_implementacion_halts_v2.md`
- `halts/cell_code/build_halts_audit_artifacts.py`
- `halts/03_halts_root_cause_audit_notebook.ipynb`
- `halts/04_halts_closeout.ipynb`
- `halts/04_halts_closeout.md`

## Inputs base

- `D:\\Halts\\raw\\...`
- `D:\\Halts\\processed\\halts_master_nasdaq_for_run_dates.parquet`
- `D:\\Halts\\processed\\halts_master_nyse_1y.parquet`
- `D:\\Halts\\processed\\halts_master_sec.parquet`
- `D:\\Halts\\processed\\halts_master_multisource.parquet`
- universo PTI o universo `<1B`
- artefactos de `quotes` y `trades` para cruce causal

## Builder offline

Script objetivo:

- `halts/cell_code/build_halts_audit_artifacts.py`

Responsabilidades:

1. Cargar fuentes procesadas por source y consolidado multisource.
2. Normalizar campos canonicos para auditoria.
3. Medir completitud y calidad por source.
4. Reconstruir clave canonica de evento.
5. Medir duplicados exactos y semanticos.
6. Medir usabilidad analitica del evento.
7. Cruzar cobertura con universo PTI o `<1B`.
8. Cruzar ventanas de eventos con artefactos de `quotes` y `trades`.
9. Escribir artefactos ligeros para notebook.

## Artefactos esperados

- `manifest.json`
- `build_log.json`
- `source_quality_summary.parquet`
- `field_completeness_summary.parquet`
- `canonical_event_summary.parquet`
- `duplicate_analysis.parquet`
- `cross_source_overlap_summary.parquet`
- `ticker_halt_coverage_summary.parquet`
- `ticker_year_halt_presence.parquet`
- `event_taxonomy_summary.parquet`
- `case_index_halts.parquet`
- `halts_quotes_link_candidates.parquet`
- `halts_trades_link_candidates.parquet`
- `event_window_alignment_summary.parquet`

## Capas de validacion

### 1. Integridad fisica

- existencia de raws esperados
- legibilidad
- tamano no trivial
- schema minimo
- parse ratio por source

### 2. Normalizacion estructural

- ticker normalizado
- fechas parseadas
- timezone coherente
- columnas canonicas presentes
- preservacion de `halt_code`, `halt_type`, `release_no`

### 3. Calidad del evento por source

- `% ticker no nulo`
- `% halt_date no nulo`
- `% halt_start_et no nulo`
- `% resume_trade_et no nulo`
- `% links y referencias no nulas`
- `% eventos con granularidad usable`

### 4. Deduplicacion multisource

- duplicado exacto
- duplicado semantico
- conflicto entre sources
- fusion dudosa

### 5. Usabilidad analitica

- `full_intraday_usable`
- `date_only_usable`
- `regulatory_context_only`
- `insufficient_event_detail`

### 6. Cobertura y cruce causal

- cobertura por ticker PTI
- cobertura por anio
- mix por source
- alineacion contra `quotes`
- alineacion contra `trades`

## Notebook metodologico

`03_halts_root_cause_audit_notebook.ipynb` debe responder:

1. Cuanto del master es realmente usable para causalidad intradia.
2. Cuanto valor aporta cada source.
3. Si la consolidacion multisource esta perdiendo granularidad.
4. Si SEC aporta cobertura o solo contexto.
5. Que parte de los casos anomalos de `quotes/trades` coincide con halts reales.

## Notebook closeout

`04_halts_closeout.ipynb` debe fijar:

- alcance auditado
- porcentaje usable por tipo de analisis
- fuentes dominantes
- limitaciones abiertas
- decision operativa final

## Criterio de cierre

`halts` solo debe considerarse auditado al nivel de los otros bloques si al final existen:

- contrato formal
- diseno v2
- builder reproducible
- artefactos reutilizables
- notebook metodologico
- notebook closeout
- taxonomia operativa
- politica explicita de uso
- cruce real con `quotes` y `trades`

## Fase 2. Overlay intradia visual `<1B>`

## Objetivo

La siguiente fase no debe quedarse en un join diario `ticker-date`.

Debe construir una capa visual de evento intradia donde:

- `halts` actua como verdad del evento
- `quotes` y `trades` actuan como evidencia microestructural
- el usuario puede ver fisicamente el halt sobre el eje temporal, no solo como flag o match tabular

## Restriccion de universo

Esta fase debe trabajar sobre el universo canonico `<1B>`.

Regla:

- no se visualizan todos los halts del master multisource
- primero se filtra `ticker in market_cap_cutoff_lt_1b_active_inactive.parquet`
- los halts fuera de ese universo no deben entrar en el viewer final

Interpretacion correcta:

- `halts` puede tener mas eventos que el universo auditado
- eso no es problema
- el viewer causal debe operar solo sobre los eventos relevantes para el universo `<1B>`

## Cambio de grano

La unidad correcta de esta fase ya no es:

- `ticker-date`

La unidad correcta pasa a ser:

- `intraday_visual_halt_event`

Eso implica trabajar con:

- `event_id_canonical`
- `halt_start_et`
- `resume_trade_et`
- raw intradia de `quotes`
- raw intradia de `trades`

## Builder adicional requerido

El builder de `halts` debe extenderse con una fase de materializacion visual.

Artefactos recomendados:

- `halts_lt1b_event_index.parquet`
- `halts_intraday_overlay_index.parquet`
- `halts_quotes_trades_visual_cases.parquet`

## Artefacto 1. `halts_lt1b_event_index.parquet`

Grano:

- una fila por `canonical_halt_event` restringido a `<1B>`

Columnas minimas:

- `event_id_canonical`
- `ticker`
- `halt_date`
- `halt_start_et`
- `resume_quote_et`
- `resume_trade_et`
- `resume_same_day`
- `event_taxonomy`
- `sources`
- `source_count`
- `in_lt1b_universe`
- `has_intraday_anchor`

## Artefacto 2. `halts_intraday_overlay_index.parquet`

Grano:

- una fila por evento visualizable

Columnas minimas:

- `event_id_canonical`
- `ticker`
- `visual_date`
- `quotes_file_visual`
- `trades_file_visual`
- `quotes_file_resume`
- `trades_file_resume`
- `has_intraday_quotes`
- `has_intraday_trades`
- `visual_case_bucket`
- `visual_key`

## Artefacto 3. `halts_quotes_trades_visual_cases.parquet`

Objetivo:

- servir al widget del notebook sin releer ni recalcular indices cada vez

Columnas minimas:

- `event_id_canonical`
- `ticker`
- `display_label`
- `halt_date`
- `halt_start_et`
- `resume_trade_et`
- `visual_case_bucket`
- `quotes_link_strength`
- `trades_link_strength`
- `quotes_problem_flag`
- `trades_problem_flag`
- `visual_key`
- `rank_score`

## Buckets visuales del overlay

Estos buckets no son decorativos. Deben ser la capa de lectura previa a la figura para que el usuario entienda que tipo de caso esta abriendo.

### `confirmed_halt_microstructure_coherent`

Significa:

- existe halt oficial usable
- `quotes` y/o `trades` muestran un patron consistente cerca del halt o del reopen
- la lectura causal es fuerte

Lectura esperada:

- el halt parece explicar visualmente la anomalia de mercado

### `halt_with_quotes_signal_only`

Significa:

- hay halt oficial
- `quotes` muestran senal util
- `trades` no muestran senal comparable o no enlazan bien

Lectura esperada:

- el libro reacciona al evento, pero el tape no aporta confirmacion fuerte

### `halt_with_trades_signal_only`

Significa:

- hay halt oficial
- `trades` muestran senal util
- `quotes` no muestran senal comparable o no enlazan bien

Lectura esperada:

- el tape reacciona, pero el libro no deja evidencia igual de fuerte

### `halt_present_but_market_clean`

Significa:

- existe halt oficial
- el raw visual disponible no muestra anomalia clara
- o bien el evento no deja huella visible en estas fuentes

Lectura esperada:

- caso de revision de granularidad, cobertura real o naturaleza del evento

### `market_signal_without_clear_halt_window`

Significa:

- la senal de mercado existe
- pero la ventana temporal del halt no explica bien lo observado
- o la correspondencia temporal del evento es dudosa

Lectura esperada:

- posible fenomeno no-halt o cruce temporal imperfecto

### `review_timestamp_alignment`

Significa:

- el caso necesita revision de tiempo
- puede haber conflicto entre timezone, fecha efectiva, `resume_trade_et` o granularidad de source

Lectura esperada:

- no decidir por la figura sin revisar primero alineacion temporal

## Regla de leyenda antes del grafico

Antes de cualquier figura del viewer debe aparecer una leyenda explicativa del bucket seleccionado.

Contenido minimo de esa leyenda:

- nombre del bucket
- definicion corta
- que debe esperar ver el usuario en `quotes`
- que debe esperar ver el usuario en `trades`
- si la lectura es:
  - `coherent`
  - `partial`
  - `review`

Regla:

- el usuario no debe abrir un grafico sin contexto de interpretacion
- la leyenda debe aparecer justo encima del grafico, no en otra seccion lejana del notebook

## Regla explicita de no duplicacion visual

El viewer no debe duplicar la misma evidencia fisica en varios graficos cuando el evento cae sobre el mismo raw.

Casos tipicos:

- `halt_day` y `resume_day` caen en la misma fecha
- `quotes` y `trades` reutilizan el mismo `ticker-day` para dos ventanas derivadas del mismo evento
- dos filas del mismo `event_id_canonical` apuntan al mismo raw visual

Regla de deduplicacion:

- un mismo evento visual debe tener un unico `visual_key`
- si `halt_day` y `resume_day` caen en el mismo `ticker-day`, se produce una sola figura compuesta
- la figura debe incluir ambas marcas temporales:
  - `halt_start_et`
  - `resume_trade_et`
- no se deben generar dos resultados visuales casi identicos por el mismo evento

Clave recomendada:

- `visual_key = ticker + halt_date/resume_date fisica + halt_start_et + resume_trade_et`

Si dos candidatos comparten el mismo `visual_key`:

- se conserva una sola entrada en el indice visual
- las demas deben colapsarse como duplicados de vista

## Especificacion de la figura intradia

La figura objetivo debe parecerse a las visualizaciones ya usadas en `quotes`, pero anadiendo la capa oficial de halt.

Layout recomendado:

### Panel 1. `quotes`

- `bid_price`
- `ask_price`
- puntos crossed
- linea vertical `halt_start_et`
- linea vertical `resume_quote_et` si existe
- linea vertical `resume_trade_et` si existe
- sombreado del intervalo de halt cuando sea defendible

### Panel 2. `trades`

- scatter de `price` por timestamp
- color por estado o familia de problema
- opcionalmente tamano por `size`
- mismas lineas verticales del halt

### Panel 3. `diagnostics`

- spread o crossed bps
- volumen o count por minuto
- outside range por minuto si aplica

## Lectura correcta de la figura

La figura no debe responder solo:

- si hay anomalia

Debe responder:

- si esa anomalia queda temporalmente alineada con el halt
- si la reaccion ocurre antes del halt
- si ocurre justo en el halt
- si ocurre en el reopen
- si solo aparece en `quotes`
- si solo aparece en `trades`
- si no aparece en ninguna fuente pese a existir halt oficial

## Uso del join diario ya construido

El join diario actual sigue siendo util, pero solo como `screening`.

No debe venderse como overlay causal final.

Papel correcto:

- priorizar casos
- medir cobertura
- decidir que eventos merecen bajar a visualizacion intradia

Papel incorrecto:

- sustituir la figura intradia
- o pretender explicar visualmente el evento solo con `ticker-date`

## Decision operativa

La secuencia correcta de trabajo queda asi:

1. filtrar `halts` al universo `<1B>`
2. construir `halts_lt1b_event_index`
3. derivar `visual_case_bucket`
4. deduplicar por `visual_key`
5. mostrar leyenda del bucket antes del grafico
6. abrir figura intradia compuesta `quotes + trades + halts`

## Estado implementado

Queda implementado ya en:

- `halts/cell_code/01_halts_intraday_visual_overlay.py`
- `halts/03_halts_root_cause_audit_notebook.ipynb`

Estado actual:

- el viewer consume `halts_quotes_trades_visual_cases.parquet`
- ese artefacto ya esta filtrado al universo `<1B>`
- la exploracion se hace sobre vistas fisicas deduplicadas `ticker-day`
- la leyenda del bucket aparece justo antes del grafico del caso seleccionado
- la figura compuesta ya superpone:
  - `quotes`
  - `trades`
  - lineas `halt_start_et`
  - lineas `resume_trade_et`
  - sombreado entre halt y reopen cuando la pareja temporal existe
