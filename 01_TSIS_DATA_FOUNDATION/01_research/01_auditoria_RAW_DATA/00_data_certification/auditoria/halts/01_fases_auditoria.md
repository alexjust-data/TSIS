## Principio rector

**La auditoría de halts debe responder cinco cosas:**

1. Si el dataset oficial está bien descargado, versionado y reconstruible.
2. Si el master multisource está normalizado sin romper la semántica del evento.
3. Si cada evento tiene calidad suficiente para análisis causal.
4. Si el cruce contra universo/PTI está bien hecho y no induce falsos huecos.
5. Si el dataset es utilizable operativamente para explicar fenómenos en quotes y trades.

Hoy solo está resuelta sobre todo la primera mitad: inventario, fuentes, schema y cobertura básica. Falta la segunda mitad: calidad del evento,
deduplicación semántica, alineación temporal, taxonomía operativa y política explícita de uso.



## Fase 0. Fijar contrato analítico

Escribir documento equivalente a daily/quotes/trades con estas definiciones:

- Unidad lógica auditada: halt_event
- Clave candidata por source:
    - Nasdaq: ticker + halt_date + halt_code + halt_start_et
    - NYSE: ticker + halt_date + halt_type + halt_start_et
    - SEC: issuer/ticker + publish/release date + release_no
- Unidad consolidada multisource:
    - event_id_canonical
- Rol de cada fuente:
    - Nasdaq y NYSE: venue truth para trading halt
    - SEC: regulatory suspension truth
- Semántica de cobertura:
    - ausencia de halt no es “missing data”
    - solo es problema cuando esperamos evidencia de evento y no aparece, o cuando el evento existe pero es inusable

Ese documento sería algo como halts/01_contrato_halts.md

## Fase 1. Diseñar la arquitectura v2
Igual que en quotes/trades, separaría:

- build offline
- artifacts/cache
- notebook metodológico
- notebook closeout

Archivos objetivo:

- halts/02_diseno_implementacion_halts_v2.md
- halts/cell_code/build_halts_audit_artifacts.py
- halts/03_halts_root_cause_audit_notebook.ipynb
- halts/04_halts_closeout.ipynb
- halts/04_halts_closeout.md

La regla debe ser la misma que ya usaste bien en otros bloques:

- Jupyter no parsea todo el raw
- Jupyter no reconstruye deduplicación pesada
- Jupyter consume artefactos pequeños
- el raw solo se toca en builder o drilldown puntual

## Fase 2. Definir capas de validación
Aquí está la parte importante. Para halts usaría 6 capas.

1. Integridad física
    - existencia de raws esperados
    - legibilidad de CSV/HTML/XML/PDF-linked metadata
    - tamaños no triviales
    - schema mínimo presente
    - porcentaje de filas parseables por source
2. Normalización estructural
    - columnas canónicas completas
    - parseo correcto de fechas y horas
    - timezone consistente
    - ticker normalizado
    - halt_code, halt_type, release_no conservados sin colapsar semántica
3. Calidad del evento por source
    - % ticker no nulo
    - % halt_date no nulo
    - % halt_start_et no nulo
    - % resume_trade_et no nulo
    - % source_url/item_link no nulo
    - % eventos con suficiente granularidad temporal para análisis causal
4. Deduplicación y consolidación multisource
    - duplicados exactos
    - duplicados semánticos entre Nasdaq/NYSE/SEC
    - colisiones donde dos rows parecen el mismo evento pero discrepan en campos clave
    - casos donde la consolidación puede estar fusionando de más o de menos
5. Usabilidad analítica
    - qué eventos sirven para ventanas pre-halt / halt / reopen
    - qué eventos solo sirven para “hubo suspensión” pero no para timing intradía
    - qué eventos son demasiado incompletos para causalidad fina
    - taxonomía de uso real:
        - full_intraday_usable
        - date_only_usable
        - regulatory_context_only
        - insufficient_event_detail
6. Cobertura y cruce con universo
    - cobertura por ticker PTI
    - cobertura por año
    - mix por source
    - concentración sectorial / exchange si aplica
    - detección de gaps improbables
    - cruce puntual con casos problemáticos de quotes y trades

## Fase 3. Builder offline
El builder debe materializar artefactos comparables al patrón quotes/trades.

Entradas:

- D:\Halts\raw\...
- D:\Halts\processed\halts_master_nasdaq_for_run_dates.parquet
- D:\Halts\processed\halts_master_nyse_1y.parquet
- D:\Halts\processed\halts_master_sec.parquet
- D:\Halts\processed\halts_master_multisource.parquet
- universo PTI / <1B si se audita contra corte final
- opcionalmente índices de casos de quotes y trades

Artefactos que debería producir:

- manifest.json
- build_log.json
- source_quality_summary.parquet
- field_completeness_summary.parquet
- canonical_event_summary.parquet
- duplicate_analysis.parquet
- cross_source_overlap_summary.parquet
- ticker_halt_coverage_summary.parquet
- ticker_year_halt_presence.parquet
- event_taxonomy_summary.parquet
- case_index_halts.parquet
- halts_quotes_link_candidates.parquet
- halts_trades_link_candidates.parquet

Y si quieres profundidad real:

- event_window_alignment_summary.parquet
    - mide si existe timestamp suficiente para alinear el evento con quotes/trades

## Fase 4. Notebook metodológico
El notebook 03_halts_root_cause_audit_notebook.ipynb no debe limitarse a “hay 5681 raw files y 88683 rows”.

Debe abrir preguntas duras:

- ¿cuánto del master es realmente usable para causalidad intradía?
- ¿qué porcentaje del valor de halts viene de Nasdaq vs NYSE vs SEC?
- ¿la consolidación multisource está perdiendo granularidad?
- ¿SEC aporta cobertura o solo contexto regulatorio?
- ¿qué parte del universo con anomalías de crossed/outside coincide con halts reales?

Bloques del notebook:

1. snapshot ejecutivo
2. calidad por fuente
3. completitud de campos críticos
4. deduplicación exacta y semántica
5. taxonomía de eventos
6. cobertura por ticker y por tiempo
7. capacidad de alineación temporal con mercado
8. drilldown de casos representativos
9. cruce con casos de quotes/trades
10. lectura ejecutiva final

## Fase 5. Criterio de severidad
Aquí no usaría PASS / SOFT_FAIL / HARD_FAIL por file como en daily/trades, sino por evento y por source-row, y además una política final por bucket.

Buckets propuestos:

- good_full_intraday_event
    - ticker, fecha y hora de inicio fiables; sirve para ventanas pre/post-halt
- good_date_level_event
    - sirve para análisis diario/event-study, no para intradía fino
- review_cross_source_conflict
    - conflicto entre fuentes o fusión dudosa
- review_partial_identity
    - evento real pero con identidad incompleta
- review_missing_resume_time
    - útil para contexto, limitado para reopen analysis
- bad_unusable_event
    - parse roto, fecha inválida, ticker irreconciliable y sin valor operativo

Y una segunda política a nivel dataset:

- good for event overlay
- good for daily causal context
- review for intraday halt-window analysis
- not defensible as regulatory truth

Eso es el equivalente real al good/review/bad de los otros datasets.

### Halts vs trades/quotes**

**La formulación correcta sería esta:**

- halts es la fuente de verdad del evento.
- quotes y trades son la evidencia de comportamiento de mercado alrededor del evento.
- la auditoría fuerte consiste en medir si ambos lados son coherentes entre sí.

Y sí, eso sirve también para detectar fallos en cualquiera de los datasets:

- si halts dice que hubo halt y quotes/trades no muestran nada especial cerca de esa ventana, puede haber fallo en halts, en timestamps, en
timezone, en deduplicación o en el cruce.
- si quotes/trades muestran un patrón clarísimo de interrupción/reopen y halts no tiene evento, puede faltar cobertura en halts o puede no ser un
halt formal sino otro fenómeno microestructural.
- si el evento existe en halts pero la ventana temporal no alinea, el problema puede ser de normalización horaria, fecha efectiva o granularidad del
source.

Eso precisamente es lo que hace que halts deba auditarse con el mismo rigor que quotes/trades: no solo como inventario de eventos, sino como capa causal para validar o refutar patrones observados en mercado.

**La forma operativa de modelarlo sería:**

1. Construir una tabla canónica de eventos halt_event.
2. Para cada halt_event, derivar ventanas:
    - pre_halt
    - halt_core
    - reopen
    - post_reopen
3. Cruzar esas ventanas con métricas ya existentes de quotes y trades.
4. Medir coherencia:
    - crossed/spread anómalo antes o en reopen
    - caída o ausencia de quotes
    - ausencia de trades o prints de reapertura
    - outside-range / volatility burst tras reanudación
5. Taxonomizar:
    - confirmed_halt_coherent_with_quotes_trades
    - halt_present_but_weak_market_signal
    - market_signal_without_official_halt
    - timing_conflict_needs_review

## Fase 6. Closeout
04_halts_closeout.ipynb debe ser el notebook que cierra operación, no exploración.

Debe contestar:

- cuál es el alcance real auditado
- qué porcentaje del master es usable por tipo de análisis
- qué fuentes mandan
- qué limitaciones quedan abiertas
- si halts entra en producción para:
    - overlay de eventos
    - análisis causal de quotes
    - análisis causal de trades
    - entrenamiento ML / features event-driven

Y su markdown de cierre debe fijar la narrativa final, igual que en daily/ohlcv_1m/quotes/trades.

**Lo más importante: qué no haría**

Tampoco lo mezclaría con cobertura binaria tipo “ticker con halt / ticker sin halt”, porque eso en halts puede ser engañoso. Un ticker sin halts no indica ausencia de cobertura; puede indicar que no tuvo evento. La cobertura correcta aquí es cobertura de capacidad de detectar y caracterizar
eventos cuando existen.

Definición de éxito
Yo consideraría halts auditado al mismo nivel que los otros cuatro solo si al final tenemos:

- contrato formal
- diseño v2
- builder offline reproducible
- cache de artefactos pequeños
- notebook metodológico
- notebook de closeout
- taxonomía operativa de eventos
- política explícita de uso
- cruce real con quotes y trades
- lista clara de límites defendibles de Nasdaq/NYSE/SEC