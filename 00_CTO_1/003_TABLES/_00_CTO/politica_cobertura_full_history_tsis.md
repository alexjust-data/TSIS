# Política de cobertura histórica para tablas, features, estados y outcomes en TSIS

Tu planteamiento es **correcto en lo esencial**, pero hay una corrección decisiva:

> No conviene elegir entre “microestructura full history” y “microestructura sólo cuando ya exista un evento”.
>
> Necesitas una arquitectura híbrida: **raw e índices amplios, contextos compactos full history, features microestructurales pesadas bajo demanda y materializaciones persistentes para eventos, candidatos y controles**.

Si calculas la microestructura únicamente después de tener una ventana de evento, puedes caer en tres problemas:

```text
1. No podrás detectar eventos nuevos que dependan de microestructura.
2. Sólo observarás situaciones ya seleccionadas y crearás selection bias.
3. No tendrás ventanas de control para saber si una feature es realmente excepcional.
```

La frase correcta sería:

```text
Full history para datos canónicos y contexto compacto.

Cobertura amplia pero estrecha para índices,
resúmenes y features baratas.

Materialización selectiva para microestructura pesada.

Estados sólo en timestamps de decisión declarados.

Event states sólo alrededor de eventos gobernados.

Outcomes siempre separados.
```

# 1. Qué significa realmente “full history”

Hay que separar cuatro conceptos que ahora aparecen mezclados:

## A. Raw full history

Significa conservar el dato fuente completo:

```text
trades
quotes
daily
1m
halts
corporate actions
news
fundamentals
short interest
```

No implica calcular todas las features posibles sobre cada registro.

Tus trades y quotes históricos ya son, conceptualmente, un archivo full history de eventos.

---

## B. Canonical table full history

Significa construir una representación limpia, gobernada y relativamente estrecha de todo el dato disponible.

Ejemplo:

```text
master_daily_table
master_intraday_bar_table
instrument_master
corporate_actions_table
```

Puede incluir columnas fundamentales y flags de calidad, pero no miles de features experimentales.

---

## C. Feature full history

Significa calcular una feature para:

```text
cada ticker
cada timestamp
toda la historia
```

Esto puede resultar razonable para algunas features baratas de daily o 1m.

No es razonable, inicialmente, para todas las features microestructurales de trades y quotes.

---

## D. Research-population full coverage

Significa calcular todas las features necesarias para **cada miembro de una población de investigación declarada**.

Por ejemplo:

```text
todos los halts 2005–2026
todos los candidatos del scanner
todas las detecciones de breakout candidate
todas las ventanas de control emparejadas
```

Esto no es full universe, pero sí es cobertura completa del experimento.

Éste debería ser el objetivo de `015`, `016`, `017` y `008`.

---

# 2. Matriz correcta para tus tablas actuales

## `000_instrument_master`

### Objetivo

```text
Full history temporal: sí
```

Debe cubrir toda la identidad económica conocida:

```text
instrument_id
ticker
valid_from
valid_to
ticker changes
exchange
security type
CIK
FIGI
```

No basta una fotografía actual. Debe ser temporal para no mezclar identidades y evitar ticker reuse.

---

## `001_market_calendar`

### Objetivo

```text
Full history: sí
```

Todo el calendario necesario para 2005–2026:

```text
sesiones
festivos
half-days
open/close
timezone
```

Es compacto y fundamental.

---

## `002_expected_data_calendar`

### Objetivo

```text
Full history: sí
```

Debe cubrir el universo esperado por:

```text
instrumento
fecha
dataset
sesión
```

Esto permite distinguir:

```text
no hubo actividad
vs.
faltan datos
```

---

## `003_dataset_certification_matrix`

### Objetivo

```text
Full history para todo el scope auditado: sí
```

Debe existir para todos los:

```text
ticker-days
datasets
particiones
price views
```

No es una feature económica. Es infraestructura de consumo y calidad.

---

## `004_master_daily_table`

### Objetivo

```text
Full history: sí
```

Idealmente 2005–2026 para todo el universo gobernado, con:

```text
daily raw
price views
features daily compactas
quality
lineage
```

Aquí sí tiene sentido materializar ampliamente:

```text
gap
range
ATR
RVOL
daily volume
daily dollar volume
daily transaction count
historical percentiles
```

Siempre que sean point-in-time y razonablemente compactas.

---

## `005_corporate_actions_table`

### Objetivo

```text
Full history: sí
```

Debe ser completa dentro de la cobertura disponible:

```text
splits
reverse splits
dividends
ticker changes
announcement/effective dates
```

---

## `006_halts_table`

### Objetivo

```text
Full history de todos los halts disponibles: sí
```

Esto no significa una fila por ticker-día. Significa cubrir todos los episodios de halt conocidos.

---

## `007_event_windows_table`

### Objetivo

```text
Full coverage de todos los eventos gobernados: sí

Full universe de mercado: no
```

Es importante esta diferencia.

Debe tener todas las ventanas generadas para todos los source events que formen parte de una familia promovida.

Por ejemplo:

```text
todos los halt events 2005–2026
```

Si en el futuro se promueve `scanner_qualification_event`:

```text
todos los scanner qualification events
del periodo y scope declarado
```

No necesita contener una ventana para cada ticker y minuto.

---

## `008_outcomes_table`

### Objetivo

```text
Full coverage de cada población de eventos/decisiones promovida: sí

Full market grid: no
```

Para cada evento o timestamp de decisión incluido en research debería existir el conjunto de outcomes declarado, siempre que los datos futuros estén disponibles.

Ejemplo:

```text
si event_state tiene 100.000 observaciones elegibles,
outcomes debería cubrir esas 100.000
salvo censura o falta de datos explícitamente declarada
```

No debe cubrir “todo 2005–2026” de forma abstracta. Debe cubrir completamente su población de evaluación.

---

## `009_fundamentals_asof_table`

### Objetivo

```text
Full historical as-of disponible: sí, con cautela
```

No debes rellenar artificialmente 2005–2026 si la fuente sólo empieza más tarde.

Debe cubrir:

```text
todos los snapshots históricamente observables disponibles
```

y declarar:

```text
known_at
published_at
effective_at
data_age
```

---

## `010_news_context_table`

### Objetivo

```text
Full history de noticias disponibles: sí
```

Pero “full history” significa:

```text
todas las noticias conservadas por la fuente
```

No significa que tengas cobertura homogénea desde 2005.

Debe declarar cambios de proveedor, épocas sin cobertura y calidad.

---

## `011_short_context_table`

### Objetivo

```text
Full history disponible: sí
```

Pero por familia:

```text
short interest
short volume
borrow
SSR
```

Cada una puede empezar en fechas distintas.

No deben fusionarse como si tuvieran idéntica cobertura.

---

## `012_regime_context_table`

### Objetivo

```text
Full history: sí
```

Siempre que se construya sólo con información point-in-time:

```text
mercado general
actividad small-cap
breadth
volatilidad
time of day
```

Es una tabla compacta y reutilizable.

---

## `013_ohlcv_1m_quote_guarded`

### Objetivo

```text
Full manifest para todo lo auditado/reparado: sí

Full materialización de todas las barras: no necesariamente
```

Debe cubrir completamente:

```text
qué barras se revisaron
qué barras se corrigieron
qué política se aplicó
qué vista se produjo
```

Puede actuar como overlay sobre los datos 1m sin duplicar físicamente todo el histórico.

---

## `014_master_intraday_bar_table`

Aquí haría una corrección importante a tu planteamiento.

### Objetivo recomendado

```text
Sí debería tender a full source history.
```

No como gran tabla de features, sino como **tabla canónica estrecha de barras**.

Debería contener todas las filas 1m elegibles disponibles:

```text
instrument_id
timestamp
OHLCV
VWAP
transaction count
price_view
quality
lineage
session
```

Es decir:

```text
014 canonical bars:
full history

024 future intraday feature table:
selectiva o por familias de features
```

No intentaría materializar en `014`:

```text
miles de lookbacks
todas las pendientes
todas las interacciones
todos los indicadores
```

Pero la base canónica de barras sí debería aspirar a abarcar todo lo disponible, particionada por:

```text
year / month / ticker o date
```

El motivo es que 1m es pesado, pero sigue siendo una representación enormemente más compacta que trades y quotes event-level.

---

## `015_microstructure_features_table`

### Objetivo

```text
No full-universe ciego.
```

Tu conclusión aquí es correcta.

Pero no debería limitarse únicamente a ventanas de eventos “positivos”.

Debe cubrir varias poblaciones:

```text
1. governed source-event windows
2. scanner candidates
3. strategy candidate events
4. microstructure episodes
5. matched control windows
6. calibration/sample windows
7. live/replay decision timestamps
```

Más adelante podría existir una pequeña capa full-history de resúmenes por ticker-día:

```text
daily quote count
daily trade count
median spread
quote coverage
sequence integrity
trade/quote availability
```

Pero no materializaría para todos los ticker-segundos de 2005–2026:

```text
OFI 100ms
microprice 250ms
signed flow 1s
burstiness 5s
tape acceleration 30s
todas sus variantes
```

---

## `016_market_state_table`

### Objetivo

```text
Full coverage del decision universe declarado.
```

No:

```text
full ticker × every timestamp × 2005–2026
```

Ejemplos de decision universe:

```text
cada scanner qualification timestamp
cada strategy candidate timestamp
cada evento halt
cada muestra de control
cada decisión de una política simulada
```

Si declaras:

```text
decision_population_id =
halt_research_v1
```

`016` debería cubrir todos los timestamps de decisión definidos por esa población.

Debe evitar una tabla monolítica que mezcle poblaciones sin metadata.

Campos obligatorios de cobertura:

```text
population_id
coverage_policy_id
decision_timestamp_policy_id
lookback_policy_id
feature_set_version
full_population_claim
source_start
source_end
eligible_count
materialized_count
missing_count
```

---

## `017_event_state_table`

### Objetivo

```text
Full coverage de todas las event windows promovidas.
```

Correcto:

```text
event_state sólo existe si hay:
source_event
event_window
decision_timestamp
state_role
```

Pero no debe limitarse necesariamente a una sola fila por evento.

Puede tener varios snapshots:

```text
pre_event
at_event
confirmation
post_event_review
research_replay
```

Los roles que miran al futuro no deben usarse como input de la decisión inicial.

---

## `018_intraday_scanner_candidates_table`

### Objetivo

```text
Full history de todos los scanner runs reproducidos
dentro del periodo declarado.
```

No sólo los candidatos seleccionados.

Conviene conservar:

```text
todos los símbolos evaluados
todos los que pasaron
todos los que fallaron
distancia a cada threshold
ranking
timestamp de cualificación
```

Si guardas sólo los seleccionados, introduces selection bias y pierdes los near misses.

No necesariamente podrás reproducirlo desde 2005 si faltan features históricas point-in-time. Su inicio real debe declararse.

---

# 3. La gran corrección: no imprimir sólo cuando ya tienes un evento

Tu pregunta central es:

> ¿Debería dejar todo preparado y, sólo cuando tuviera una ventana de evento, imprimir features o estados?

La respuesta es:

> Para las features microestructurales pesadas, sí debes calcularlas bajo demanda alrededor de anchors gobernados. Pero los anchors no pueden limitarse a eventos ya conocidos y exitosos.

Necesitas cuatro clases de anchors.

## 3.1 Anchors naturales

```text
halt
resume
news publication
filing
corporate action
scanner qualification
```

Tienen un timestamp fuente independiente de las features que quieres estudiar.

---

## 3.2 Anchors de patrón candidato

```text
HOD test
breakout attempt
VWAP cross
red-to-green cross
volume expansion
opening-range break candidate
```

Son detecciones mecánicas, no decisiones.

---

## 3.3 Anchors microestructurales

```text
trade burst
quote burst
spread collapse
OFI flip
depletion proxy
liquidity vacuum
```

Aquí surge una dependencia:

```text
para detectar el episodio
necesitas calcular algunas primitivas/features
antes de crear la event window
```

Por eso necesitas una capa de detección ligera o streaming.

No puedes esperar a que exista la ventana para calcular la misma variable que crea el evento.

---

## 3.4 Control anchors

Son obligatorios científicamente.

Ejemplos:

```text
mismo ticker
misma hora del día
misma banda de precio
mismo régimen
día sin evento
timestamp aleatorio elegible
```

Si sólo calculas features alrededor de breakouts, halts o squeezes, no sabrás cómo se comportan esas features en condiciones normales.

Necesitas:

```text
event windows
+
matched control windows
```

---

# 4. Arquitectura de cálculo recomendada

Yo lo organizaría en tres niveles.

## Nivel 1 — siempre disponible

Datos e índices compactos que permiten localizar rápidamente qué leer:

```text
raw partition catalog
ticker-day manifest
trade count por archivo
quote count por archivo
first/last timestamp
quality state
sequence quality summary
session coverage
daily context
1m canonical bars
```

Esto sí debe tender a full history.

---

## Nivel 2 — detección ligera

Features suficientemente baratas para identificar posibles anchors:

```text
1m price/volume/transaction features
trade count por segundo o buckets básicos
quote count por segundo
spread summary básico
top-depth summary básico
```

No necesitas todas las features sofisticadas.

Puedes producir una capa estrecha de detección:

```text
microstructure_detection_grid
```

Por ejemplo, sólo para ticker-days in-play:

```text
1s:
trade_count
share_volume
quote_count
median_spread
last_mid
top_depth
```

Esta capa permite detectar:

```text
bursts
stalls
spread changes
high-activity zones
```

sin materializar todo el feature universe.

---

## Nivel 3 — cálculo profundo bajo demanda

Cuando existe un anchor elegible:

```text
source event
scanner candidate
strategy candidate
microstructure episode
control anchor
```

se extrae la ventana raw y se calculan:

```text
todas las ventanas multi-scale
trade signing
OFI
microprice dynamics
entropy
burstiness
venue features
depletion proxies
flow-to-price response
```

Y se persiste el resultado con:

```text
feature_set_version
window_policy_id
eligibility_policy_id
alignment_policy_id
quality_state
```

---

# 5. Materializar bajo demanda no significa calcularlo cada vez

Hay que distinguir:

```text
lazy computation
```

de:

```text
temporary computation
```

Mi recomendación es:

1. La primera vez que una ventana entra en una población promovida, calculas sus features.
2. Las guardas materializadas.
3. Las reutilizas mientras no cambie ninguna dependencia.
4. Si cambia el contrato, generas una versión nueva.

Clave de caché conceptual:

```text
instrument_id
anchor_timestamp
window_policy_id
feature_set_version
raw_view_version
eligibility_policy_id
alignment_policy_id
```

Así no relees millones de trades y quotes cada vez que ejecutas un experimento.

---

# 6. Qué debería ir full history dentro de microestructura

No todo tiene que ser estrictamente event-driven.

Mantendría full history estas capas estrechas:

## Catálogo físico

```text
ticker
date
partition path
row count
first timestamp
last timestamp
bytes
schema version
checksum
quality state
```

## Resumen ticker-day de trades

```text
trade_count
total_volume
dollar_volume
odd_lot ratio
invalid ratio
duplicate diagnostics
first/last trade
```

## Resumen ticker-day de quotes

```text
quote_count
first/last quote
two-sided ratio
median spread
sequence gaps
timestamp anomalies
zero bid/ask ratios
```

## Disponibilidad microestructural

```text
has_trades
has_quotes
trade_quote_overlap
regular-session coverage
premarket coverage
after-hours coverage
alignment eligibility
```

Estas tablas son relativamente compactas y permiten planificar cualquier extracción posterior.

No son una feature store de scalping completa.

---

# 7. Qué no debería ir full history inicialmente

No materializaría para cada ticker y cada instante:

```text
microprice_100ms
microprice_250ms
microprice_1s
OFI_100ms
OFI_250ms
OFI_1s
signed_flow_1s
signed_flow_5s
burstiness_10s
entropy_30s
tape_jerk
venue_transition matrices
apparent replenishment episodes
```

Ni sus combinaciones:

```text
raw
z-score
percentile
short/long ratio
slope
acceleration
regime-normalized
```

Eso produciría una explosión de:

```text
filas
columnas
I/O
versiones
coste de recalcular
riesgo de data snooping
```

---

# 8. El riesgo de sólo estudiar ventanas de eventos

Tu propuesta necesita añadir explícitamente:

```text
control windows
```

Si no, puedes concluir erróneamente:

```text
“la aceleración del tape aparece antes de los breakouts”
```

cuando quizá también aparece con igual frecuencia antes de:

```text
fallos
ruido
halts
reversiones
momentos aleatorios de alta actividad
```

Por cada población de eventos, construiría controles como:

```text
matched_same_ticker_same_time
matched_same_price_liquidity
matched_same_regime
matched_non_event
near_miss_candidate
```

Ejemplo:

```text
breakout candidates:
10.000 ventanas

matched controls:
30.000–50.000 ventanas
```

No es obligatorio que la proporción sea ésa, pero sí que los controles estén gobernados.

---

# 9. También necesitas near misses

No guardes únicamente:

```text
scanner selected = true
strategy candidate detected = true
```

Guarda observaciones cercanas al umbral:

```text
falló RVOL por poco
no llegó a romper HOD
reclamó VWAP pero no sostuvo
tape aceleró sin desplazamiento
OFI cambió sin breakout
```

Los near misses son muy valiosos para aprender la frontera entre:

```text
evento
no evento
evento fallido
evento incompleto
```

---

# 10. Lookback features no significa calcular toda la historia en cada fila

Tu regla:

```text
Lookback features para memoria estratégica
```

es correcta, pero conviene precisarla.

Una feature en `decision_timestamp = t` puede usar:

```text
últimos 5 segundos
últimos 30 minutos
sesión actual hasta t
últimos 20 días
historia de eventos anteriores cerrados
```

No puede usar:

```text
información posterior a t
resultado del evento actual
cierre de la sesión si aún no ocurrió
normalización calculada con futuro no observable
```

La memoria estratégica puede materializarse como:

```text
prior_event_count_20d
prior_breakout_success_rate_asof
days_since_last_halt
median_completed_burst_response_last_20
```

Pero sólo sobre episodios cerrados antes de `t`.

---

# 11. Propuesta definitiva por cobertura

Yo formalizaría cinco `coverage_mode`.

```text
FULL_SOURCE_HISTORY
FULL_CONTEXT_HISTORY
FULL_RESEARCH_POPULATION
SELECTIVE_EVENT_WINDOWS
ON_DEMAND_REPLAY
```

## `FULL_SOURCE_HISTORY`

Para:

```text
raw data
partition catalogs
canonical identities
calendar
corporate actions
halts
daily
canonical 1m, cuando se promueva
```

## `FULL_CONTEXT_HISTORY`

Para:

```text
daily features
regime
quality summaries
availability summaries
as-of context
```

## `FULL_RESEARCH_POPULATION`

Para:

```text
todos los scanner candidates de un replay
todos los halt events
todos los strategy candidates de un detector versionado
todos los controles asociados
```

## `SELECTIVE_EVENT_WINDOWS`

Para:

```text
features microestructurales profundas
market states
event states
execution features
```

## `ON_DEMAND_REPLAY`

Para:

```text
experimentos exploratorios
nuevas feature families
ventanas todavía no promovidas
debug
case studies
```

Cuando una población de replay se promueve, pasa de:

```text
ON_DEMAND_REPLAY
```

a:

```text
FULL_RESEARCH_POPULATION
```

---

# 12. Campos de cobertura que deberían acompañar todas las tablas derivadas

Añadiría a manifests y contratos:

```text
coverage_mode
coverage_policy_id
population_id
population_definition_version
source_date_start
source_date_end
eligible_instrument_count
eligible_session_count
eligible_anchor_count
materialized_anchor_count
missing_anchor_count
excluded_anchor_count
exclusion_reason_counts
full_source_history_claim
full_population_claim
full_universe_claim
lookback_policy_id
feature_set_version
builder_version
built_at_utc
```

Muy importante:

```text
full_universe_claim
```

no debería ser el único booleano.

Una tabla puede tener:

```text
full_universe_claim = false
full_population_claim = true
```

Ejemplo:

```text
No cubre todo el mercado,
pero sí cubre todos los halts elegibles 2005–2026.
```

Ésa es una afirmación fuerte y útil.

---

# 13. Qué mejoraría de tu contrato actual

Tu contrato de tres coberturas es bueno:

```text
full_history_context
daily_in_play_candidates
event_window_microstructure
```

Yo lo ampliaría a cinco, porque faltan dos poblaciones esenciales:

```text
full_history_context
daily_in_play_candidates
event_window_microstructure
matched_control_windows
policy_decision_trajectories
```

## `matched_control_windows`

Necesaria para inferencia científica y estimar base rates.

## `policy_decision_trajectories`

Necesaria más adelante para:

```text
position state
execution state
offline RL
imitation learning
secuencias de decisiones
```

Una trayectoria no es exactamente una event window aislada.

Puede abarcar:

```text
candidate detection
entry opportunity
position management
exit
post-trade evaluation
```

---

# 14. Orden físico recomendado

## Preparar ahora full history

```text
000 instrument master
001 calendar
002 expected coverage
003 certification
004 daily
005 corporate actions
006 halts
009 fundamentals as-of, según fuente
010 news as-of, según fuente
011 short context, según fuente
012 regime
013 repair manifest/overlay
014 canonical intraday bars
```

`007` y `008` deben cubrir plenamente las poblaciones gobernadas, no el mercado entero.

## Preparar ahora como infraestructura microestructural

Aunque no materialices todas las features:

```text
trade partition catalog
quote partition catalog
trade ticker-day summary
quote ticker-day summary
trade/quote overlap manifest
timestamp/sequence quality manifest
eligibility contracts
alignment contracts
feature registry
```

## Materializar por poblaciones

```text
015 microstructure features
016 market states
017 event states
018 scanner candidates
```

con:

```text
event windows
candidate windows
control windows
replay windows
```

---

# 15. Respuesta directa a tu propuesta

Tu visión:

```text
Full history para contexto.
Ventanas gobernadas para microestructura.
Estados para decisiones concretas.
Outcomes separados.
```

es correcta.

La completaría así:

```text
Full history para raw, identidad,
calendario, calidad y contexto compacto.

Full source history para la tabla canónica 1m,
pero sin convertirla en una feature explosion.

Microestructura profunda para eventos,
candidatos, controles y replays gobernados.

Una capa microestructural ligera full-history
para manifests, cobertura y detección.

Market state para todos los timestamps
de una población de decisiones declarada.

Event state para todas las ventanas promovidas.

Outcomes completos para la misma población,
pero físicamente y semánticamente separados.

Execution y policy trajectories
para las decisiones secuenciales posteriores.
```

# Veredicto final

**No debes calcular todas las features microestructurales para cada ticker y cada instante de 2005–2026.**

Pero tampoco debes esperar pasivamente a que alguien te entregue una event window y sólo entonces tener capacidad de análisis.

Debes dejar construido:

```text
1. Raw full history accesible y particionado.
2. Catálogos e índices full history.
3. Resúmenes ticker-day compactos.
4. Tabla canónica 1m amplia.
5. Detectores ligeros de anchors.
6. Generador gobernado de event/candidate/control windows.
7. Motor reproducible de features bajo demanda.
8. Caché/materialización versionada de resultados.
9. Builders de market_state y event_state.
10. Outcomes separados y alineados con la población.
```

La frase más precisa para TSIS sería:

> **Contexto completo, microestructura selectiva pero reproducible, controles obligatorios, estados poblacionales y outcomes separados.**

Y la regla operativa:

```text
No calcules todo siempre.

Sí debes poder calcular cualquier ventana
de forma reproducible.

Cuando una población se promueva,
materializa todas sus ventanas,
incluidos eventos, fallos, near misses y controles.
```
