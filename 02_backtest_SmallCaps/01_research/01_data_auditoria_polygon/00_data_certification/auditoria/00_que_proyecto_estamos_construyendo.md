# Qué Proyecto Estamos Construyendo

## Idea central

Este proyecto no consiste en “descargar datos de mercado” ni en “auditar Polygon” como fin en sí mismo.

Lo que estamos construyendo realmente es una **infraestructura de verdad operativa para small caps `<1B>`**, utilizable entre `2005` y `2026`, con tres objetivos encadenados:

1. **Explicabilidad**
   - distinguir fenómeno económico real de mala data, problemas de microestructura, corporate actions, cambios de identidad o contexto exógeno.
2. **Research y backtest serio**
   - poder construir hipótesis y probarlas sin contaminar resultados con capas mal interpretadas.
3. **Feature store y modelado**
   - derivar señales defendibles para modelos o estrategias, sabiendo qué capa manda en cada tipo de pregunta.

La premisa del proyecto es esta:

- no basta con tener `daily`, `quotes`, `trades`, `halts`, `reference`, `short` y `additional`
- hay que saber **qué es verdad primaria**, **qué es contexto**, **qué es soporte**, **qué es redundante** y **qué conflictos pueden aparecer entre capas**

## Qué significa “verdad operativa”

Una capa de datos es útil solo si responde de forma defendible a preguntas concretas.

Por eso la auditoría se ha organizado en bloques que no compiten entre sí, sino que responden a preguntas diferentes:

- `daily` y `ohlcv_1m`
  - resumen el comportamiento de precio/volumen a escalas agregadas
- `quotes` y `trades`
  - describen la microestructura observada
- `halts`
  - fijan la verdad del evento de interrupción regulatoria/venue
- `reference`
  - fijan la verdad de identidad y corporate actions
- `short`
  - aportan contexto de crowding/short pressure
- `additional`
  - aportan contexto informacional, early-life, fundamental y macro

## Pregunta maestra del proyecto

Cuando aparece un caso raro en small caps, lo que este proyecto quiere poder responder es:

> **“¿Qué pasó realmente aquí, qué capa lo explica mejor y cuánto puedo confiar en esa explicación?”**

Ese es el hilo conductor de toda la auditoría.

## Qué pregunta responde cada bloque

### 1. `01_auditoria_1B_general`

Archivos base:

- [01_auditoria_1B_general.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\01_auditoria_1B_general.md)
- [01_auditoria_1B_general.ipynb](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\01_auditoria_1B_general.ipynb)
- cache asociada:
  - [cache_lt1b_coverage](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\cache_lt1b_coverage)

**Pregunta que responde**

- ¿Qué universo `<1B>` estamos auditando realmente?
- ¿Qué cobertura global tiene cada dataset sobre ese universo?
- ¿Qué huecos estructurales hay por ticker y por mes?
- ¿Qué casos merecen investigación prioritaria?

**No responde**

- no dice por sí sola por qué un ticker estuvo raro
- no resuelve causalidad fina

**Rol real**

- contrato global del universo y mapa de cobertura

### 2. `daily`

Archivo de cierre:

- [04_daily_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\daily\04_daily_closeout.md)

**Preguntas que responde**

- ¿Cuál es la trayectoria diaria de precio y volumen?
- ¿Dónde hay discontinuidades o jumps a nivel día?
- ¿Qué días tienen comportamiento agregado extraño?
- ¿Qué parte de la historia diaria es usable para backtest o features lentas?

**Qué aporta al resto**

- baseline agregado para contrastar:
  - `trades`
  - `quotes`
  - `short`
  - `reference`
  - `additional`

### 3. `ohlcv_1m`

Archivo de cierre:

- [04_ohlcv_1m_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\ohlcv_1m\04_ohlcv_1m_closeout.md)

**Preguntas que responde**

- ¿Cómo se ve el comportamiento intradía agregado a 1 minuto?
- ¿Qué discontinuidades o cambios de escala sobreviven al agregado?
- ¿Qué parte del movimiento intradía es compatible con la lectura de `trades`?

**Qué aporta al resto**

- puente entre:
  - `daily`
  - `trades`
  - `quotes`

### 4. `quotes`

Archivo de cierre:

- [04_quotes_full_C_D_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\04_quotes_full_C_D_closeout.md)

**Preguntas que responde**

- ¿Cómo se comportó el libro `bid/ask`?
- ¿Hubo crossed markets, spreads absurdos o timestamps extraños?
- ¿La microestructura del libro es sana, frágil o rota?
- ¿Qué rarezas del mercado vienen del lado `quotes`?

**No responde**

- no dice por sí sola si un halt fue formal
- no resuelve identidad

**Rol real**

- verdad primaria del estado del libro observado

### 5. `trades`

Bloque ya auditado previamente en el árbol `auditoria/trades`.

**Preguntas que responde**

- ¿Qué prints ocurrieron realmente?
- ¿Hubo trades fuera de rango, duplicados, off-session o rarezas de escala?
- ¿Qué parte del movimiento de precio viene del tape observado?

**Qué aporta al resto**

- verdad primaria del tape
- pieza central para validar:
  - `reference` splits
  - `halts` reopens
  - `short` contexto
  - `news` impacto

### 6. `halts`

Archivos de cierre:

- [04_halts_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_closeout.md)
- [04_halts_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_causal_overlay_closeout.md)

Artefacto central:

- [halts_quotes_trades_visual_cases.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2\halts_quotes_trades_visual_cases.parquet)

**Preguntas que responde**

- ¿Hubo halt formal o suspensión real?
- ¿Cuándo empezó y cuándo reanudó?
- ¿Qué parte de un episodio raro de mercado coincide con una interrupción oficial?
- ¿El reopen fue coherente o problemático?

**Rol real**

- verdad del evento regulatorio/venue

### 7. `reference`

Archivos de cierre:

- [04_reference_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_closeout.md)
- [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)

Artefactos clave:

- [reference_split_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_market_link_candidates.parquet)
- [reference_event_halt_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_halt_link_candidates.parquet)
- [reference_event_quotes_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_quotes_link_candidates.parquet)

**Preguntas que responde**

- ¿Qué era este ticker realmente en esta fecha?
- ¿Es common stock, warrant, preferred, unidad, símbolo transitorio?
- ¿Hay split, dividend o ticker change que explique la anomalía observada?
- ¿El problema es de identidad o de mercado?

**Rol real**

- verdad de identidad y corporate actions

### 8. `short`

Archivos de cierre:

- [04_short_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_closeout.md)
- [04_short_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_causal_overlay_closeout.md)

Artefactos clave:

- [short_volume_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_volume_market_link_candidates.parquet)
- [short_volume_halt_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_volume_halt_link_candidates.parquet)
- [short_interest_market_context_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_interest_market_context_candidates.parquet)

**Preguntas que responde**

- ¿Hay short-flow extremo o crowding alrededor del evento?
- ¿El caso raro viene acompañado de presión short diaria?
- ¿Hay `days_to_cover` extremo cerca de halts o squeezes potenciales?
- ¿Qué parte del contexto short es fiable si comparo Polygon con FINRA?

**Rol real**

- contexto de crowding, no verdad primaria del evento

### 9. `additional`

Archivos de cierre:

- [04_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_closeout.md)
- [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)

**Preguntas que responde**

Subcapas:

#### `financials_core`

- ¿Tenemos fundamentales utilizables para research y features lentas?
- ¿Qué calidad y cobertura tienen `income`, `balance` y `cash flow`?

#### `news`

- ¿Hay noticia mono-ticker cerca del evento?
- ¿La publicación precede o sigue a la reacción intradía?
- ¿La noticia explica, acompaña o solo contextualiza el episodio?

#### `ipos`

- ¿Es un caso de fragilidad normal de listing reciente?
- ¿El comportamiento raro es típico de early-life trading?

#### `economic`

- ¿Hay contexto macro relevante para el régimen del mercado?

#### `corporate_actions_additional`

- ¿Aporta algo frente a `reference` o solo confirma/reduplica?

**Rol real**

- bloque de contexto, no de verdad primaria de mercado

## Qué preguntas exactas ya podemos responder

Con el estado actual de la auditoría, el proyecto ya puede responder de forma defendible preguntas como estas:

### Preguntas de mercado observado

- ¿El libro estaba sano o roto?
- ¿El tape estaba limpio o contaminado?
- ¿La anomalía es diaria, 1m o puramente tick-level?

Capas:

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`

### Preguntas de evento formal

- ¿Hubo halt formal?
- ¿Hubo reopen?
- ¿La secuencia del halt explica la rareza del mercado?

Capas:

- `halts`
- `quotes`
- `trades`

### Preguntas de identidad y corporate action

- ¿Es el ticker correcto?
- ¿Hubo split, rename o corporate action?
- ¿El scale mismatch viene del mercado o del cambio corporativo?

Capas:

- `reference`
- apoyo de `additional corporate_actions`

### Preguntas de contexto short

- ¿Hay short-flow anormal o crowding?
- ¿La presión short precede o acompaña el evento?

Capas:

- `short`

### Preguntas de contexto informacional

- ¿Hay noticia before/after el evento?
- ¿El mercado ya estaba roto antes de `published_ny`?
- ¿La noticia es mono-ticker o ruido multi-ticker?

Capas:

- `additional.news`

### Preguntas de early-life / listing

- ¿Esto parece caos normal de salida a mercado?
- ¿Los halts y rarezas son compatibles con día/listing reciente?

Capas:

- `additional.ipos`

### Preguntas de contexto lento

- ¿Hay fundamentales utilizables?
- ¿Hay régimen macro que deba considerarse?

Capas:

- `additional.financials_core`
- `additional.economic`

## Qué NO estamos construyendo

Esto también conviene dejarlo explícito.

No estamos construyendo:

- un simple mirror de Polygon
- un dashboard superficial de calidad
- una colección de notebooks sin jerarquía

Y tampoco estamos afirmando que:

- toda anomalía de mercado tiene una explicación única
- cualquier same-day `news` es causal
- cualquier spike de `days_to_cover` es señal económica fuerte
- cualquier corporate action secundaria de `additional` desplace a `reference`

## Resultado final esperado

El resultado final que persigue esta auditoría es una pila así:

1. **mercado observado**
   - `daily`
   - `ohlcv_1m`
   - `quotes`
   - `trades`

2. **verdad del evento**
   - `halts`

3. **verdad de identidad y corporate action**
   - `reference`

4. **contexto adicional**
   - `short`
   - `news`
   - `ipos`
   - `financials_core`
   - `economic`

5. **reglas transversales**
   - [05_crosswalk_multidataset.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\05_crosswalk_multidataset.md)

## Documento complementario

Para pasar de “qué estamos construyendo” a “cómo se relacionan operativamente las capas”, el documento que completa este marco es:

- [05_crosswalk_multidataset.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\05_crosswalk_multidataset.md)

Ese archivo fija:

- qué capa manda en cada tipo de problema
- cómo resolver conflictos entre fuentes
- qué artefactos consultar primero según la pregunta
