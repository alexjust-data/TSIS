# Confirmación de la arquitectura 000–029 y significado institucional de `event`

Sí: **tu interpretación general es correcta**, pero hay tres correcciones importantes en el pipeline y algunos matices en el uso de la palabra `event`.

# 1. Confirmación de la estructura 000–029

Esta lectura es correcta:

```text
000–013 = salidas Data Foundation ya materializadas
          o artefactos operativos para su scope declarado

014–018 = siguientes superficies oficiales previstas,
          pero todavía no promovidas/full-universe

019–029 = propuesta arquitectónica posterior y orientativa,
          no parte oficial actual del mapa
```

Con dos precisiones.

## 000–013 no tienen exactamente el mismo grado de materialización

`000–012` son salidas operativas para el alcance que declara cada una.

`013_ohlcv_1m_quote_guarded` es un caso especial:

```text
no es todavía la tabla institucional definitiva de barras 1m
```

Es principalmente:

```text
repair manifest promovido
+
overlay/vista quote-guarded
+
materialización física candidate no plenamente promovida
```

Por tanto, la frase más precisa sería:

```text
000–012:
salidas operativas para su scope declarado

013:
manifest/overlay quote-guarded operativo,
pero no master intraday bar oficial

014–018:
schemas y candidatos todavía no promovidos
```

## 019–029 no deben convertirse ahora en autoridad

Correcto.

Los nombres propuestos describen separaciones arquitectónicas útiles, pero no debes crear inmediatamente:

```text
019
020
021
...
029
```

como si fueran contratos aprobados.

Primero conviene consolidar:

```text
014
015
016
017
018
```

Y sólo después decidir cuáles de las superficies propuestas merecen convertirse en datasets institucionales.

---

# 2. Tu árbol de carpetas es razonable

Esta estructura es válida como representación del estado actual:

```text
C:\TSIS_Data\00_CTO_1\003_STATE_tables\

  000_instrument_master\
  001_market_calendar\
  002_expected_data_calendar\
  003_dataset_certification_matrix\
  004_master_daily_table\
  005_corporate_actions_table\
  006_halts_table\
  007_event_windows_table\
  008_outcomes_table\
  009_fundamentals_asof_table\
  010_news_context_table\
  011_short_context_table\
  012_regime_context_table\
  013_ohlcv_1m_quote_guarded\

  014_master_intraday_bar_table\
  015_microstructure_features_table\
  016_market_state_table\
  017_event_state_table\
  018_intraday_scanner_candidates_table\
```

También es razonable mantener las ideas posteriores en una zona no autoritativa:

```text
_future_expansion_not_authority\
```

Eso evita que un agente interprete erróneamente que esas tablas ya han sido aprobadas o materializadas.

Pero no asumiría todavía que cada idea futura acabará siendo una tabla física. Algunas podrían ser:

```text
tablas físicas
vistas
módulos de construcción
contratos
registries
artefactos de lineage
```

Por ejemplo:

```text
microstructure_feature_registry
```

probablemente sea un contrato o catálogo de metadata, no necesariamente una tabla Parquet comparable a `market_state`.

---

# 3. Corrección importante del pipeline causal

Tu pipeline contiene una idea correcta, pero esta parte necesita corregirse:

```text
013 + raw trades/quotes/1m
  alimentan 014

014
  alimenta 015
```

No es exactamente así.

## Flujo correcto de `014`

`014_master_intraday_bar_table` se construye principalmente desde:

```text
OHLCV 1m raw
+
splits/corporate actions
+
overlay quote-guarded
+
quality manifests
```

Conceptualmente:

```text
raw OHLCV 1m
        +
corporate actions / split normalization
        +
013 quote-guarded repair manifest/overlay
        ↓
014 master_intraday_bar_table
```

Los **trades raw no son un upstream principal de 014**.

Las quotes sí intervienen indirectamente mediante la reparación quote-guarded, pero `013` no debe entenderse como una tabla de barras completa que simplemente se copia en `014`.

`013` proporciona:

```text
qué barras requieren reparación
qué vista quote-guarded aplicar
qué controles y lineage acompañan la reparación
```

`014` es la superficie oficial futura que institucionaliza las distintas vistas de barra.

---

## Flujo correcto de `015`

`015_microstructure_features_table` no debería depender principalmente de `014`.

Sus upstream fundamentales son:

```text
raw trades event-level
+
raw quotes event-level
+
trade/quote eligibility policies
+
quality gates
+
event windows o decision timestamps
```

Conceptualmente:

```text
raw trades
raw quotes
quality/certification
event windows o decision timestamps
        ↓
015 microstructure_features_table
```

`014` puede aportar contexto auxiliar:

```text
precio de referencia
session VWAP
bar context
HOD/LOD
price-view quality
```

Pero la microestructura no debería calcularse a partir de barras de un minuto.

Por tanto:

```text
014 no es el padre causal principal de 015
```

La relación real es más parecida a:

```text
014 intraday features ─────────┐
                              │
015 microstructure features ──┼──► 016 market_state
                              │
004 daily/context ────────────┘
```

Es decir, `014` y `015` son principalmente **superficies hermanas**, no una cadena lineal.

---

# 4. Pipeline corregido

La versión más precisa sería:

```text
000 instrument_master
001 market_calendar
002 expected_data_calendar
003 dataset_certification_matrix
005 corporate_actions
013 quote-guarded manifest/overlay
raw OHLCV 1m
        ↓
014 master_intraday_bar_table
```

En paralelo:

```text
raw trades
raw quotes
003 certification/quality
007 event windows o decision timestamps
        ↓
015 microstructure_features_table
```

El scanner:

```text
000 instrument master
001 calendar
004 master daily
014 intraday bars
        ↓
018 intraday_scanner_candidates_table
```

El estado general:

```text
000 identity
001 calendar
003 quality
004 daily
006 halts
009 fundamentals
010 news
011 short
012 regime
014 intraday
015 microstructure
018 scanner
        ↓
016 market_state_table
```

Y el estado asociado a eventos:

```text
016 market_state_table
+
007 event_windows_table
+
metadata del source event
        ↓
017 event_state_table
```

Finalmente:

```text
017 event_state_table
        ↓
X / inputs observables para research y modelos

008 outcomes_table
        ↓
Y / resultados posteriores
```

Ésta sería la representación completa:

```text
                    ┌─────────────────────────┐
raw OHLCV 1m ──────►│ 014 intraday bars       │─────┐
013 overlay ───────►│                         │     │
                    └─────────────────────────┘     │
                                                    │
                    ┌─────────────────────────┐     │
raw trades ────────►│ 015 microstructure      │─────┤
raw quotes ────────►│ features                │     │
                    └─────────────────────────┘     │
                                                    ▼
004 / 009–012 / 018 ───────────────────────► 016 market_state
                                                    │
007 event_windows ──────────────────────────────────┤
                                                    ▼
                                             017 event_state

008 outcomes ───────────────────────────────► labels/Y separados
```

---

# 5. Orden de trabajo recomendado

Tu orden es prácticamente correcto:

## Primero: `014`

```text
master_intraday_bar_table
```

Porque debes institucionalizar:

```text
raw 1m
split-normalized 1m
quote-guarded raw
quality
lineage
price views
```

## Después o en paralelo: `015`

```text
microstructure_features_table
```

Pero no necesitas esperar a terminar toda la tabla 014 para empezar el diseño de 015.

Puedes avanzar en paralelo:

```text
014:
barras, price views y contexto intradía

015:
trades, quotes, BBO y microestructura
```

Lo que sí debería estar resuelto antes de consolidar 015 es:

```text
trade conditions policy
quote conditions/indicators policy
timestamp semantics
sequence policy
deduplication policy
trade–quote alignment policy
```

## Después: `016`

```text
market_state_table
```

No debería consolidarse antes de que estén suficientemente definidos:

```text
014 intraday
015 microstructure
```

Porque `016` debe consumirlos, no reinventarlos.

## Después: `017`

```text
event_state_table
```

Consume:

```text
market state
+
event window
+
event metadata
+
state role
```

## `018`

Puede construirse en paralelo con `014`.

Sin embargo, si quieres incorporar sus campos a `market_state`:

```text
scanner_rank
scanner_selection_state
first_cross timestamp
candidate reasons
```

entonces `018` se convierte en upstream opcional de `016`, siempre respetando:

```text
scanner_as_of_utc <= decision_timestamp_utc
```

---

# 6. ¿Debes dividir ahora físicamente `015` en 015A y 015B?

Conceptualmente sí; físicamente, todavía no necesariamente.

La idea de:

```text
015A_microstructure_window_features_core
015B_microstructure_research_features
```

significa:

## Core

Features aprobadas, estables y gobernadas:

```text
trade_count_rate
share_volume_rate
spread
top depth
L1 imbalance
microprice
quote update rate
signed flow
OFI
```

## Research

Features todavía experimentales:

```text
burst algorithms
entropy variants
venue transition metrics
replenishment proxies
liquidity-vacuum detectors
nonlinear interactions
latency regimes
```

Pero puedes implementarlo inicialmente dentro de una misma familia:

```text
015_microstructure_features\
    contracts\
    core\
    research\
    manifests\
    tests\
```

No tienes por qué declarar ahora dos datasets oficiales independientes.

La separación importante es:

```text
core promovible
vs.
research experimental
```

No el nombre exacto de la carpeta.

---

# 7. Confirmación del significado de “event”

Tu segunda interpretación también es esencialmente correcta.

La palabra `event` está siendo usada en varios niveles distintos. Yo distinguiría incluso **cinco**, no cuatro.

```text
1. raw data event
2. source/domain event
3. governed event window
4. strategy candidate event
5. event state
```

---

# 8. Primer significado: raw data event

Es una observación elemental del stream:

```text
trade
quote update
bar
news record
filing record
short-interest observation
```

En microestructura se usa además la expresión:

```text
event time
```

donde cada trade o quote update hace avanzar el reloj lógico.

Ejemplo:

```text
trade event 1
quote event 2
quote event 3
trade event 4
```

Esto no es un evento estratégico.

Es simplemente:

> Una nueva observación elemental en la secuencia de datos.

Por eso hablamos de:

```text
trade_event_primitives
quote_event_primitives
event-time volatility
```

Aquí `event` significa “mensaje u observación del mercado”.

---

# 9. Segundo significado: source o domain event

Es un suceso de negocio o de mercado con identidad propia.

Ejemplos:

```text
halt
resume
news publication
filing
split
reverse split
ticker change
scanner qualification
microstructure burst
```

No todos son raw events elementales.

Un halt, por ejemplo, puede tener:

```text
event_id
start
resume quote
resume trade
halt code
```

Es un episodio de dominio.

En tu implementación oficial actual, `007_event_windows_table` está materializada principalmente para:

```text
halt-derived event windows
```

Por tanto, aunque conceptualmente pueda soportar otras familias, hoy no debes afirmar que `007` contiene:

```text
news events
scanner events
strategy events
microstructure episodes
```

Actualmente su alcance declarado es:

```text
halts
```

---

# 10. Tercer significado: governed event window

Correcto:

> Es una ventana temporal gobernada alrededor de un source event.

Pero no tiene que reducirse a:

```text
pre_event
at_event
post_event
```

Tu tabla 007 actual utiliza roles más concretos, como:

```text
prior_session_regular
pre_event_30m
event_to_resume_or_30m
same_session_regular
next_session_regular
```

Cada fila establece:

```text
source_event_id
event_family
event_type
window_role
window_start_utc
window_end_utc
consumption state
quality state
```

Por ejemplo:

```text
source event:
halt

window:
30 minutos anteriores al halt

window_role:
pre_event_30m
```

Otra fila del mismo source event puede ser:

```text
window_role:
event_to_resume_or_30m
```

Y otra:

```text
window_role:
next_session_regular
```

Por tanto:

```text
un source event
        ↓
puede generar múltiples event windows
```

---

# 11. Cuarto significado: strategy candidate event

También correcto.

Ejemplos:

```text
first_high_push
rebreak
breakout_attempt
pullback_to_vwap
red_to_green_cross
opening_range_break
first_green_day_setup
```

Pero la formulación institucional debería ser:

```text
strategy_candidate_event
```

o incluso:

```text
market_pattern_candidate_event
```

No:

```text
strategy truth
confirmed strategy
valid entry
```

Porque el detector sólo dice:

> Se ha detectado una geometría o condición candidata.

No dice:

```text
comprar
vender
entrar
la estrategia funciona
```

---

# 12. Importante: un scanner candidate no es automáticamente un event

Tu texto dice:

```text
scanner_candidate_selected
```

como ejemplo de strategy candidate event.

Es posible, pero requiere una transformación explícita.

`018_intraday_scanner_candidates_table` tiene grano:

```text
scanner_run_id + ticker + session_date
```

Y contiene:

```text
selected_intraday_in_play_candidate
first_cross_50_ts_utc
scanner_selection_state
candidate_reasons
```

Pero una fila de scanner no se convierte automáticamente en un `event_id`.

Para convertirla en source event necesitas una operación de “eventización”:

```text
scanner candidate row
        ↓
seleccionar timestamp de anclaje
        ↓
crear source_event_id
        ↓
definir event_family
        ↓
crear event windows
```

Ejemplo:

```text
source_event_id =
hash(scanner_run_id, ticker, first_cross_50_ts_utc)

event_family =
scanner_qualification

event_timestamp =
first_cross_50_ts_utc
```

Sólo entonces puede alimentar formalmente:

```text
event_windows_table
```

---

# 13. Quinto significado: `event_state_table`

Tu explicación es correcta:

```text
event_state =
market_state
+
event anchoring
+
event window
+
state role
```

Pero conviene una precisión:

> Una fila de `event_state_table` no es necesariamente un resumen agregado de toda la ventana.

El grano definido es:

```text
event_window_id
+ decision_timestamp_utc
+ state_role
+ state_schema_version
```

Por tanto, representa:

> Un estado observable en un timestamp de decisión concreto, vinculado a una ventana de evento y a un rol.

Ejemplo:

```text
event_window_id = halt_X_pre30m
decision_timestamp_utc = 14:27:00
state_role = pre_event
market_state_id = ...
```

La fila responde:

```text
¿Cómo estaba el mercado en este instante,
dentro del contexto de esta ventana de evento?
```

No responde:

```text
¿Fue una buena entrada?
¿El patrón era rentable?
¿Debo comprar?
```

---

# 14. Tu traducción mental es correcta

La mejor traducción conceptual es:

```text
event_state_table
=
observable_state_anchored_to_a_governed_event_context
```

O en español:

```text
estado observable contextualizado
por un evento y una ventana gobernada
```

No:

```text
tabla de señales estratégicas
```

---

# 15. Relación correcta entre las superficies de eventos

Tu secuencia es correcta con un pequeño cambio de terminología:

```text
source_event o event_candidate
    dice:
    ocurrió o fue detectado algo
```

```text
event_windows_table
    dice:
    qué ventanas temporales gobernadas
    se definen alrededor de ese evento
```

```text
market_state_table
    dice:
    cómo estaba el mercado en un timestamp
```

```text
event_state_table
    dice:
    qué market state corresponde
    a ese evento, ventana y rol
```

```text
outcomes_table
    dice:
    qué ocurrió posteriormente
```

Gráficamente:

```text
source event
    │
    ├── halt
    ├── news
    ├── scanner qualification
    ├── microstructure episode
    └── strategy candidate
            │
            ▼
event_windows_table
            │
            ├── pre-event window
            ├── at-event window
            ├── response window
            └── outcome window
                    │
                    ▼
market_state_table ─────► event_state_table
                              │
                              ├── pre_event
                              ├── at_event
                              ├── post_event_review
                              └── research_replay

outcomes_table permanece separada
```

---

# 16. Qué eventos admite hoy y cuáles son futuros

## Materializado actualmente en `007`

Principalmente:

```text
halt events
```

## Conceptualmente admisibles en el futuro

```text
news events
filing events
scanner qualification events
corporate-action events
microstructure episodes
strategy candidate events
```

Pero cada nueva familia necesita:

```text
source event contract
event_id policy
event timestamp policy
event family/type taxonomy
quality policy
window-generation policy
leakage rules
```

No basta con añadir un string nuevo a `event_family`.

---

# 17. Diferencia entre microstructure episode y strategy candidate event

Ésta es importante.

## Microstructure episode

Ejemplo:

```text
trade burst
spread collapse
signed-flow flip
ask depletion proxy
quote burst
```

Dice:

> Ocurrió un fenómeno observable en trades o quotes.

No impone una operación.

## Strategy candidate event

Ejemplo:

```text
breakout attempt
first pullback
VWAP reclaim candidate
```

Dice:

> Una geometría que una familia de estrategias podría utilizar ha sido detectada.

Puede construirse usando uno o varios episodios microestructurales:

```text
breakout candidate
=
precio cerca de HOD
+
compresión
+
tape acceleration
+
signed flow comprador
```

Pero no son la misma capa.

---

# 18. Mi corrección final de tu lectura

Tu interpretación está aproximadamente en un **90 % correcta**.

Las correcciones necesarias son:

```text
1. 013 es manifest/overlay especial,
   no master bar table completa.

2. 014 no alimenta causalmente a 015 como paso obligatorio.

3. 014 y 015 son superficies hermanas:
   intraday bars vs microstructure.

4. 015 se alimenta directamente de raw trades/quotes,
   quality policies y timestamps/event windows.

5. 018 puede alimentar a 016,
   pero sólo as-of y sin convertirse automáticamente en event.

6. El event_windows actual está materializado para halts,
   no todavía para todas las familias conceptuales.

7. Un raw trade/quote event,
   un source event,
   un strategy candidate
   y un event_state son objetos distintos.

8. event_state no es una señal;
   es un market state contextualizado por un evento.
```

La arquitectura final que deberías conservar mentalmente es:

```text
DATA FOUNDATION Y CONTEXTOS
000–013
        │
        ├───────────────────────────┐
        ▼                           ▼
014 intraday bars          015 microstructure features
        │                           │
        ├─────────────┬─────────────┤
                      ▼
               016 market_state
                      │
source events ─► 007 event_windows
                      │
                      ▼
               017 event_state

018 scanner candidates
    puede alimentar 016
    y puede convertirse en source event
    sólo mediante una eventización explícita

008 outcomes
    permanece completamente separado
```

Y la frase definitiva es:

> `market_state` describe el mercado; `event_window` define el contexto temporal de algo que ocurrió; `event_state` vincula ambos; `strategy_candidate_event` describe una geometría candidata; `outcomes` dicen qué pasó después. Ninguno de esos objetos, por sí solo, significa “comprar”.
