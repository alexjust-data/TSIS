# Auditoría de las tablas de estado frente al punto 10 de features microestructurales

Sí. He descomprimido `stade_table.zip` y he leído las 19 fichas de tablas, incluyendo el contenido y los atributos de cada una.

La respuesta central es:

> **El punto 10 no se refiere, en general, a las tablas de estado completas. Se refiere a features microestructurales calculadas a partir de trades y quotes.**
>
> En tu arquitectura, esas features deberían nacer principalmente en `015 - microstructure_features_table` y después incorporarse, con el namespace `microstructure__`, a `016 - market_state_table` y `017 - event_state_table`.

Pero hay un matiz importante:

> **La tabla 015 que tienes definida actualmente sólo contiene una primera capa muy básica de estadísticas microestructurales. La mayoría de las features científicas enumeradas en el punto 10 todavía no están explícitamente definidas como atributos.**

---

# 1. Qué decía realmente el punto 10

El punto 10 clasificaba tres grupos:

## Features calculables sólo con trades

```text
trade_count_rate
share_volume_rate
dollar_volume_rate
intertrade_duration
trade_size_distribution
odd_lot_ratio
large_trade_ratio
trade_size_entropy
price_change_per_trade
realized volatility event-time
volume-weighted price movement
trade clustering
burst intensity
tape acceleration
tape deceleration
trade direction persistence
price impact after trade bursts
```

## Features que necesitan trades sincronizados con quotes L1

```text
signed trade volume
bid-hit rate
ask-lift rate
effective spread
realized spread
trade-to-mid displacement
quote response latency
best-bid depletion proxy
best-ask depletion proxy
L1 order flow imbalance
microprice L1
spread compression/expansion
```

## Features que no pueden calcularse científicamente sin MBP-10 o MBO

```text
depth imbalance top 10
book slope
book convexity
liquidity gaps multinivel
queue position
queue imbalance real
order age
cancel rate
add rate
replenishment por order_id
spoofing lifecycle
full order-book resiliency
```

Por tanto, el punto 10 no estaba describiendo una tabla concreta ya existente. Estaba diciendo:

> “Con tus datos raw de trades y quotes, estas son las variables científicamente defendibles que podrías construir.”

---

# 2. Dónde encajan esas features en tus tablas

La secuencia correcta en tu arquitectura sería:

```text
trades raw + quotes raw
            ↓
microstructure_features_table
            ↓
market_state_table
            ↓
event_state_table
            ↓
modelos ML / pattern discovery / RL candidate
```

Más concretamente:

```text
015 microstructure_features_table
```

sería la tabla especializada que calcula y almacena las métricas.

Después:

```text
016 market_state_table
```

construiría una fotografía completa del mercado en un instante de decisión, incluyendo:

```text
microstructure__trade_count_rate_1s
microstructure__ask_lift_ratio_5s
microstructure__spread_bps_median_10s
microstructure__tape_acceleration_5s
...
```

Y:

```text
017 event_state_table
```

tomaría ese `market_state` y lo anclaría a un evento específico:

```text
pre_event
at_event
post_event_review
research_replay
```

Por tanto:

- `015` contiene las features microestructurales.
- `016` contiene esas features dentro del estado general del mercado.
- `017` contiene ese estado asociado a un evento.
- `008 outcomes_table` contiene resultados posteriores y debe permanecer separada.

Esta separación está conceptualmente bien diseñada.

---

# 3. Qué contiene actualmente tu tabla 015

Tu contrato actual de `microstructure_features_table_v0_1` tiene como grano:

```text
event_window_id
+ ticker
+ window_start_utc
+ window_end_utc
```

Es decir:

> Una fila representa la microestructura agregada de un ticker durante una ventana de evento.

Actualmente contiene estas features de quotes:

```text
quotes_rows
quotes_window_rows
quotes_first_ts_utc
quotes_last_ts_utc

quotes_ask_zero_pct
quotes_bid_zero_pct
quotes_ask_size_zero_pct
quotes_bid_size_zero_pct

quotes_two_sided_rows
quotes_crossed_rows
quotes_locked_rows
quotes_crossed_ratio_pct_all_rows
quotes_crossed_ratio_pct_two_sided
quotes_locked_ratio_pct_two_sided

quotes_spread_bps_median
quotes_spread_bps_p90
quotes_top_depth_mean
```

Y estas features de trades:

```text
trades_rows
trades_window_rows
trades_first_ts_utc
trades_last_ts_utc

trades_invalid_price_rows
trades_invalid_size_rows
trades_odd_lot_ratio_pct
trades_duplicate_exact_ratio_pct
trades_off_regular_session_ratio_pct

trades_total_volume
trades_dollar_volume

trades_price_min
trades_price_max
trades_price_last

trades_size_median
trades_size_p90
```

Estas columnas sí corresponden parcialmente con el punto 10.

Por ejemplo:

| Punto 10 | Campo existente |
|---|---|
| `odd_lot_ratio` | `trades_odd_lot_ratio_pct` |
| `share_volume` | `trades_total_volume` |
| `dollar_volume` | `trades_dollar_volume` |
| `trade_size_distribution` | `trades_size_median`, `trades_size_p90` |
| spread | `quotes_spread_bps_median`, `quotes_spread_bps_p90` |
| top-of-book depth | `quotes_top_depth_mean` |
| calidad de quotes | crossed, locked, zero bid/ask |

Pero esto sólo cubre una parte pequeña.

---

# 4. Qué features del punto 10 ya están realmente definidas

## Definidas directamente

Estas sí aparecen materializadas como atributos:

```text
odd_lot_ratio
total share volume
total dollar volume
trade size median
trade size p90
trade price min
trade price max
trade price last
median spread
spread p90
top-of-book depth mean
locked-market ratio
crossed-market ratio
```

Además tienes métricas de calidad:

```text
invalid price rows
invalid size rows
duplicate exact ratio
off-session trade ratio
zero bid/ask ratio
zero bid/ask-size ratio
```

Estas últimas no son alpha features propiamente dichas. Son principalmente:

```text
quality features
consumption gates
data integrity diagnostics
```

Son muy importantes, pero no describen directamente la conducta económica del tape.

---

# 5. Qué features pueden derivarse, pero aún no están definidas como columnas

Varias features del punto 10 podrían calcularse usando los campos actuales y los timestamps de la ventana, pero no están explícitamente materializadas.

## `trade_count_rate`

Tienes:

```text
trades_window_rows
window_start_utc
window_end_utc
```

Por tanto puedes calcular:

```text
trade_count_rate =
    trades_window_rows
    / window_duration_seconds
```

Pero no existe hoy una columna como:

```text
trades_count_rate_per_second
```

## `share_volume_rate`

Tienes:

```text
trades_total_volume
```

Puede derivarse:

```text
share_volume_rate =
    trades_total_volume
    / window_duration_seconds
```

No está explícita.

## `dollar_volume_rate`

Tienes:

```text
trades_dollar_volume
```

Puede derivarse:

```text
dollar_volume_rate =
    trades_dollar_volume
    / window_duration_seconds
```

Tampoco está explícita.

## Rango de precios

Con:

```text
trades_price_min
trades_price_max
trades_price_last
```

puedes construir alguna medida de rango, pero no:

```text
realized volatility event-time
price change per trade
path efficiency
trade-by-trade price movement
```

Para eso necesitas procesar la secuencia completa, no sólo los agregados finales.

## Dispersión de tamaños

Tienes:

```text
trades_size_median
trades_size_p90
```

Eso representa parcialmente `trade_size_distribution`, pero es insuficiente para:

```text
trade_size_entropy
large_trade_ratio
size concentration
size tail index
coefficient of variation
```

Por tanto, están cubiertas parcialmente, no completamente.

---

# 6. Qué features importantes del punto 10 faltan en la tabla 015

Actualmente no encuentro columnas explícitas para:

```text
intertrade_duration
large_trade_ratio
trade_size_entropy
price_change_per_trade
realized_volatility_event_time
volume_weighted_price_movement
trade_clustering
burst_intensity
tape_acceleration
tape_deceleration
trade_direction_persistence
price_impact_after_trade_bursts
```

Tampoco aparecen las features que requieren sincronización trade-quote:

```text
signed_trade_volume
bid_hit_rate
ask_lift_rate
effective_spread
realized_spread
trade_to_mid_displacement
quote_response_latency
best_bid_depletion_proxy
best_ask_depletion_proxy
l1_order_flow_imbalance
microprice_l1
spread_compression
spread_expansion
```

Por tanto, mi respuesta concreta es:

> **No, las features del punto 10 no están todavía completamente definidas en las tablas que has enviado.**
>
> La arquitectura tiene reservado el lugar correcto para ellas, especialmente la tabla 015, pero el contrato actual sólo contiene un conjunto inicial de agregados y controles de calidad.

---

# 7. La diferencia entre una “tabla de features” y una “tabla de estado”

Aquí está probablemente la raíz de la confusión.

## Tabla de features microestructurales

La tabla `015_microstructure_features_table` responde:

> ¿Qué ocurrió en trades y quotes durante una ventana concreta?

Ejemplo:

```text
ticker = XYZ
window = 09:31:10–09:31:15

trade_count_rate = 38.4 trades/s
ask_lift_ratio = 0.72
signed_volume = +18.400 acciones
spread_bps_median = 42
tape_acceleration = 2.7
microprice_deviation_bps = +9
```

Es una tabla especializada. Su única responsabilidad es transformar el flujo raw de trades y quotes en medidas microestructurales.

No debería contener, por ejemplo:

```text
market_cap
news_catalyst
gap_pct
distance_to_hod
short_interest
market_regime
```

Esas variables pertenecen a otras familias.

## `market_state_table`

La tabla `016_market_state_table` responde:

> ¿Cuál era el conjunto completo de información observable del mercado y del instrumento en un instante exacto de decisión?

Esta tabla puede incorporar información procedente de muchas superficies:

```text
identity__
calendar__
scanner__
daily__
intraday__
microstructure__
halt__
fundamentals__
news__
short_context__
short_constraints__
regime__
quality__
```

Un ejemplo simplificado:

```text
instrument_id = XYZ
decision_timestamp_utc = 13:34:15.000

daily__gap_pct = 42.8
daily__rvol_20d = 11.6
intraday__distance_to_hod_pct = -1.2
intraday__distance_to_vwap_pct = +4.7

microstructure__trade_count_rate_1s = 46.0
microstructure__ask_lift_ratio_5s = 0.74
microstructure__signed_volume_5s = +22.500
microstructure__spread_bps_median_5s = 38
microstructure__tape_acceleration_1s_vs_5s = 1.9

news__catalyst_present = true
news__catalyst_age_minutes = 46

short_context__short_volume_ratio = 0.38
regime__market_intraday_return_pct = -0.22
```

La tabla de estado no recalcula necesariamente todo desde los raw. Puede consumir las features ya producidas por las tablas especializadas y materializarlas como una fotografía coherente.

## `event_state_table`

La tabla `017_event_state_table` responde:

> ¿Qué estado del mercado estaba asociado a un evento concreto y qué papel temporal representa ese estado?

Ejemplo:

```text
event_id = PM_SQUEEZE_XYZ_2026_07_10_093415
event_family = PM_SQUEEZE

event_timestamp_utc = 13:34:15
decision_timestamp_utc = 13:34:15

state_role = at_event
market_state_id = ...
```

Otras filas del mismo evento podrían representar:

```text
pre_event
at_event
post_event_review
research_replay
```

Por tanto, la relación conceptual es:

```text
microstructure_features_table
        ↓
medidas especializadas de trades y quotes

market_state_table
        ↓
fotografía observable completa en t

event_state_table
        ↓
fotografía vinculada a un evento y a un rol temporal
```

No son tres formas diferentes de almacenar exactamente lo mismo.

---

# 8. El problema del grano actual de la tabla 015

Tu tabla `015` tiene actualmente este grano:

```text
event_window_id
+ ticker
+ window_start_utc
+ window_end_utc
```

Esto significa:

> Una fila resume toda la actividad microestructural de un ticker dentro de una ventana de evento.

Es un diseño válido para una primera auditoría o para análisis agregados.

Pero presenta un problema para scalping:

> Una única agregación de toda la ventana puede ocultar el orden temporal de lo que ocurrió.

Imagina una ventana de cinco minutos:

```text
09:30:00–09:35:00
```

La tabla puede decir:

```text
trades_total_volume = 600.000
spread_bps_median = 44
odd_lot_ratio = 71 %
trades_size_p90 = 800
```

Pero esas métricas no revelan si:

```text
el tape aceleró a las 09:34:57
el spread se comprimió justo antes de romper HOD
las compras agresivas desaparecieron después del breakout
el bid se debilitó en los últimos dos segundos
la presión compradora se concentró al inicio o al final
```

Dos secuencias completamente diferentes podrían producir prácticamente los mismos agregados finales.

### Secuencia A

```text
Primeros 4 minutos:
actividad lenta

Últimos 10 segundos:
explosión de trades
ask lifts
compresión del spread
ruptura de HOD
```

### Secuencia B

```text
Primer minuto:
actividad intensa

Últimos 4 minutos:
agotamiento
spread creciente
presión vendedora
```

Las dos podrían tener:

```text
mismo volumen total
mismo número de trades
misma mediana del spread
mismo rango de precios
```

Pero para decidir una entrada a las `09:34:57`, son estados opuestos.

---

# 9. Necesitas features multi-window ancladas al timestamp de decisión

Para trading intradía, las features no deberían depender solamente de una ventana extensa de evento.

Necesitas observar distintos horizontes retrospectivos desde el mismo instante:

```text
100 ms
250 ms
500 ms
1 s
2 s
5 s
10 s
30 s
60 s
```

Por ejemplo, para:

```text
decision_timestamp_utc = 13:34:15.000
```

podrías calcular:

```text
trade_count_rate_1s
trade_count_rate_5s
trade_count_rate_30s

share_volume_rate_1s
share_volume_rate_5s
share_volume_rate_30s

ask_lift_ratio_1s
ask_lift_ratio_5s
ask_lift_ratio_30s

spread_bps_median_1s
spread_bps_median_5s
spread_bps_median_30s
```

Esto permite saber no sólo el nivel actual, sino también su dinámica.

Ejemplo:

```text
trade_count_rate_1s = 70 trades/s
trade_count_rate_5s = 32 trades/s
trade_count_rate_30s = 8 trades/s
```

Aquí hay una aceleración muy fuerte.

En cambio:

```text
trade_count_rate_1s = 8 trades/s
trade_count_rate_5s = 27 trades/s
trade_count_rate_30s = 31 trades/s
```

Aquí el tape se está desacelerando.

El volumen agregado de los últimos treinta segundos podría ser parecido, pero el estado de decisión no lo es.

## Dos formas razonables de materializarlo

### Alternativa A: formato ancho

Una fila por timestamp de decisión:

```text
instrument_id
decision_timestamp_utc

trade_count_rate_1s
trade_count_rate_5s
trade_count_rate_30s

share_volume_rate_1s
share_volume_rate_5s
share_volume_rate_30s

ask_lift_ratio_1s
ask_lift_ratio_5s
ask_lift_ratio_30s
```

Ventaja:

```text
fácil de consumir por modelos
```

Desventaja:

```text
muchas columnas
menos flexible al añadir ventanas
```

### Alternativa B: formato largo

Una fila por:

```text
instrument_id
decision_timestamp_utc
feature_window
feature_set_version
```

Ejemplo:

```text
XYZ | 13:34:15 | 1s  | trade_count_rate=70 | ask_lift_ratio=0.81
XYZ | 13:34:15 | 5s  | trade_count_rate=32 | ask_lift_ratio=0.69
XYZ | 13:34:15 | 30s | trade_count_rate=8  | ask_lift_ratio=0.56
```

Ventaja:

```text
más extensible
mejor para investigación
```

Desventaja:

```text
requiere pivotar o ensamblar antes de ciertos modelos
```

Una arquitectura seria puede mantener ambas:

```text
long canonical feature store
wide model-ready materialization
```

---

# 10. Cómo deben definirse científicamente estas features

No basta con crear una columna llamada:

```text
tape_acceleration
```

Ese nombre no tiene significado científico por sí solo.

Hay que definir:

```text
qué eventos entran
qué condiciones de trade se aceptan
qué ventana temporal se utiliza
qué denominador se emplea
qué ocurre si no hay trades
cómo se tratan duplicados
cómo se ordenan timestamps iguales
qué versión de datos se usa
qué información estaba disponible en t
```

## Ejemplo: `trade_count_rate`

```text
trade_count_rate_1s(t) =
    número de trades elegibles en (t − 1 segundo, t]
    / 1 segundo
```

La palabra importante es:

```text
elegibles
```

Debes definir si excluyes:

```text
late prints
out-of-sequence trades
cancelled trades
corrections
trades con precio inválido
duplicados de ingestión
ciertas sale conditions
off-session trades
```

Sin esa política, dos implementaciones pueden producir resultados diferentes aunque usen el mismo nombre.

## Ejemplo: `share_volume_rate`

```text
share_volume_rate_5s(t) =
    suma del tamaño de trades elegibles en (t − 5s, t]
    / 5
```

Unidad:

```text
acciones por segundo
```

Conviene guardar también:

```text
log1p_share_volume_rate_5s
```

porque la distribución puede ser extremadamente asimétrica.

## Ejemplo: `dollar_volume_rate`

```text
dollar_volume_rate_5s(t) =
    Σ(price_i × size_i)
    / 5
```

Unidad:

```text
dólares por segundo
```

Es diferente de `share_volume_rate`.

En small caps, el número de acciones puede ser alto sólo porque el precio es muy bajo. El dollar volume ayuda a distinguir:

```text
actividad económica real
vs.
gran número nominal de acciones
```

## Ejemplo: `intertrade_duration`

Para cada trade:

```text
Δt_i = timestamp_i − timestamp_(i−1)
```

Luego, dentro de una ventana, pueden calcularse:

```text
intertrade_duration_mean
intertrade_duration_median
intertrade_duration_p10
intertrade_duration_p90
intertrade_duration_std
zero_duration_ratio
```

`zero_duration_ratio` es importante cuando muchos eventos comparten el mismo milisegundo:

```text
número de Δt = 0
/
número total de intervalos
```

Pero debe interpretarse con prudencia si no conservas sequence number.

## Ejemplo: `large_trade_ratio`

No debería existir sin declarar qué significa “large”.

Opciones:

### Umbral fijo en acciones

```text
size >= 1.000 acciones
```

Problema:

```text
no es comparable entre una acción de 0,50 USD
y una acción de 20 USD
```

### Umbral fijo en notional

```text
price × size >= 10.000 USD
```

Mejor económicamente, pero puede seguir siendo arbitrario.

### Umbral relativo

```text
size >= percentil 90
de la distribución histórica del ticker
en un contexto comparable
```

Más adaptable, aunque más complejo.

Una política robusta podría materializar varias:

```text
large_trade_ratio_shares_1000
large_trade_ratio_notional_10000
large_trade_ratio_rolling_p90
```

No deberían mezclarse bajo un único nombre genérico.

## Ejemplo: `trade_size_entropy`

Una posible definición consiste en discretizar tamaños en buckets:

```text
1–9
10–49
50–99
100–199
200–499
500–999
1.000+
```

Y calcular:

```text
H = −Σ p_k log(p_k)
```

Interpretación:

```text
entropía baja:
actividad concentrada en pocos tamaños

entropía alta:
distribución más heterogénea
```

Pero los buckets deben estar versionados y justificados.

Otra opción sería usar bins relativos o logarítmicos.

## Ejemplo: `price_change_per_trade`

```text
price_change_per_trade_i =
    price_i − price_(i−1)
```

Agregados útiles:

```text
mean_price_change_per_trade
median_price_change_per_trade
positive_price_change_ratio
negative_price_change_ratio
zero_price_change_ratio
absolute_price_change_per_trade_mean
```

También puede normalizarse:

```text
price_change_bps_per_trade
```

para poder comparar tickers de distinto precio.

## Ejemplo: volatilidad en event time

En vez de medir volatilidad por minuto, se mide sobre la secuencia de trades:

```text
r_i = log(price_i / price_(i−1))
```

```text
realized_volatility_event_time =
    sqrt(Σ r_i²)
```

Esto responde:

> ¿Cuánta variación de precio apareció a lo largo de los eventos ejecutados?

No es exactamente igual que la volatilidad en clock time.

Una ventana con muchos trades y pequeños movimientos puede comportarse de forma diferente a una ventana con pocos trades y saltos grandes.

## Ejemplo: `volume_weighted_price_movement`

Una posible definición:

```text
Σ(size_i × Δprice_i)
/
Σ size_i
```

Pero hay varias definiciones plausibles.

También podrías calcular:

```text
signed_volume_weighted_return
```

o:

```text
VWAP_end − VWAP_start
```

Por eso el nombre debe ir acompañado de una fórmula concreta.

## Ejemplo: `trade_clustering`

Puede medir si los trades llegan:

```text
uniformemente
```

o en:

```text
ráfagas concentradas
```

Posibles medidas:

```text
coefficient_of_variation_intertrade_duration
Fano factor
burstiness index
proporción de trades dentro de clusters
```

Una medida clásica de burstiness:

```text
B = (σ_Δt − μ_Δt) / (σ_Δt + μ_Δt)
```

Interpretación aproximada:

```text
B cerca de -1:
eventos muy regulares

B cerca de 0:
comportamiento parecido a Poisson

B cerca de +1:
eventos muy concentrados en ráfagas
```

Pero no deberías llamar a todo esto simplemente `trade_clustering`. Cada métrica debe tener nombre propio.

---

# 11. Tape acceleration y tape deceleration

“Tape acceleration” puede significar varias cosas:

```text
aumento del número de trades
aumento del volumen por segundo
aumento del dollar volume por segundo
reducción del tiempo entre trades
aumento de trades agresivos
```

No existe una única tape acceleration universal.

Podrías definir una familia:

```text
tape_count_acceleration
tape_share_volume_acceleration
tape_dollar_volume_acceleration
tape_signed_volume_acceleration
```

## Ejemplo de aceleración por número de trades

```text
tape_count_acceleration_1s_vs_5s =
    log1p(trade_count_rate_1s)
    − log1p(trade_count_rate_5s)
```

Interpretación:

```text
positivo:
la actividad reciente supera el ritmo medio de 5 segundos

negativo:
la actividad reciente está decayendo
```

## Ejemplo por volumen

```text
tape_volume_acceleration_1s_vs_10s =
    log1p(share_volume_rate_1s)
    − log1p(share_volume_rate_10s)
```

## Ejemplo normalizado históricamente

```text
tape_count_rate_zscore =
    (current_rate − expected_rate)
    / historical_std
```

Pero el baseline debe ser point-in-time y condicionado, por ejemplo, por:

```text
ticker
hora del día
precio
liquidez
régimen
tipo de evento
```

Comparar las `09:31` con las `12:45` sin corregir la estacionalidad intradía puede crear señales engañosas.

---

# 12. `trade_direction_persistence`

Para calcular persistencia de dirección primero necesitas clasificar cada trade:

```text
buy-initiated
sell-initiated
unknown
```

Con trades solos puedes usar reglas como:

```text
tick rule
```

Pero con quotes sincronizadas puedes usar:

```text
trade price vs bid/ask/mid
```

Una vez clasificados:

```text
sign_i ∈ {-1, 0, +1}
```

puedes construir:

```text
same_sign_transition_ratio
run_length_mean
run_length_max
sign_autocorrelation_lag1
sign_autocorrelation_lagN
```

Ejemplo:

```text
+ + + + + − + + +
```

indica mayor persistencia compradora que:

```text
+ − + − + − + −
```

aunque ambas secuencias contengan un número parecido de compras y ventas.

Esta diferencia puede ser muy relevante para tape reading.

---

# 13. Features que necesitan sincronización entre trades y quotes

Ésta es la segunda familia del punto 10.

Tus raw de trades por sí solos no permiten conocer con suficiente fundamento si una ejecución fue:

```text
en bid
en ask
dentro del spread
fuera del quote observado
```

Necesitas asociar cada trade con una quote de referencia.

La operación conceptual es:

```text
para cada trade en t:
buscar la última quote elegible conocida antes de t
```

Pero esto no es trivial por latencias y desfases.

Puede que el trade se publique con retraso respecto a la quote que estaba vigente cuando se ejecutó.

Por eso conviene estudiar varias políticas:

```text
quote en t
quote anterior a t
quote anterior a t − 1 ms
quote anterior a t − 5 ms
quote anterior a t − 10 ms
quote anterior a t − 25 ms
quote anterior a t − 50 ms
```

Y medir si la clasificación cambia materialmente.

## `bid_hit_rate`

```text
bid_hit_rate =
    número o volumen de trades clasificados en bid
    /
    trades clasificables
```

Puede existir en dos versiones:

```text
bid_hit_count_ratio
bid_hit_volume_ratio
```

No significan exactamente lo mismo.

## `ask_lift_rate`

```text
ask_lift_rate =
    número o volumen de trades clasificados en ask
    /
    trades clasificables
```

De nuevo:

```text
ask_lift_count_ratio
ask_lift_volume_ratio
```

Un ticker puede tener muchos pequeños ask lifts y pocos grandes bid hits. Por número parecería comprador; por volumen, vendedor.

Por eso conviene guardar ambas perspectivas.

## `signed_trade_volume`

Una definición sencilla:

```text
signed_trade_volume =
    Σ(sign_i × size_i)
```

donde:

```text
sign_i = +1 para ask lift
sign_i = -1 para bid hit
sign_i = 0 para no clasificado
```

También:

```text
signed_dollar_volume =
    Σ(sign_i × size_i × price_i)
```

Y una versión normalizada:

```text
signed_volume_imbalance =
    signed_trade_volume
    / total_classified_volume
```

Con rango aproximado:

```text
-1 a +1
```

## `effective_spread`

Para un trade clasificado con dirección:

```text
effective_spread_i =
    2 × sign_i × (trade_price_i − midquote_i)
```

En bps:

```text
effective_spread_bps_i =
    10.000 × effective_spread_i / midquote_i
```

Mide el coste efectivo de cruzar el mercado respecto al midquote.

Necesita:

```text
trade price
trade direction
midquote contemporáneo
```

## `trade_to_mid_displacement`

```text
trade_to_mid_displacement_bps =
    10.000 × (trade_price − midquote)
    / midquote
```

A diferencia del effective spread, puede mantenerse con signo natural sin multiplicar por la dirección.

## `microprice L1`

Con:

```text
best_bid_price
best_ask_price
best_bid_size
best_ask_size
```

una definición habitual es:

```text
microprice =
    (
      ask_price × bid_size
      +
      bid_price × ask_size
    )
    /
    (bid_size + ask_size)
```

La lógica es que si existe más tamaño en bid que en ask, el microprice se desplaza hacia el ask, reflejando una presión teórica alcista.

Puedes derivar:

```text
microprice_minus_mid_bps
```

```text
microprice_pressure =
    (microprice − mid)
    / spread
```

Pero esto es sólo L1.

No debe llamarse:

```text
full book microprice
```

ni confundirse con una medida de profundidad multinivel.

## L1 order flow imbalance

Una versión de OFI L1 utiliza cambios en:

```text
best bid price
best bid size
best ask price
best ask size
```

Por ejemplo, de manera simplificada:

```text
bid contribution:
+ tamaño nuevo si el bid sube
− tamaño anterior si el bid baja
cambio de tamaño si el precio no cambia

ask contribution:
− tamaño nuevo si el ask baja
+ tamaño anterior si el ask sube
− cambio de tamaño bajo ciertas convenciones
```

Después:

```text
OFI = contribución bid − contribución ask
```

La fórmula exacta debe quedar fijada en contrato.

No es lo mismo que:

```text
signed trade volume
```

Porque OFI utiliza cambios de quotes, incluso aunque no haya ejecuciones.

## `spread_compression` y `spread_expansion`

Ejemplo:

```text
spread_change_bps =
    spread_bps_now
    − spread_bps_at_window_start
```

O:

```text
spread_compression_ratio =
    spread_now
    / median_spread_previous_30s
```

Puede medirse como:

```text
nivel actual
pendiente
cambio absoluto
cambio relativo
percentil histórico
```

En small caps, conviene trabajar tanto en:

```text
dólares
ticks
basis points
```

porque un spread de `0,01 USD` no tiene el mismo significado en una acción de `0,50 USD` que en una de `20 USD`.

---

# 14. Depletion proxies y replenishment L1

Con quotes L1 puedes construir aproximaciones, no observaciones completas del libro.

## `best_bid_depletion_proxy`

Podría detectar:

```text
reducción del tamaño visible en best bid
junto con trades ejecutados en bid
```

Ejemplo:

```text
bid_size_before = 10.000
sell volume at bid = 8.000
bid_size_after = 1.500
```

Esto parece compatible con consumo del bid.

Pero no puedes saber exactamente:

```text
cuánto fue cancelado
cuánto fue ejecutado
cuánto fue reemplazado por órdenes nuevas
qué órdenes individuales permanecen
```

Por eso debe llamarse:

```text
depletion_proxy
```

y no:

```text
true_bid_depletion
```

## `replenishment proxy`

Si después de ejecuciones en bid el tamaño visible vuelve a crecer rápidamente:

```text
bid size:
10.000 → 2.000 → 9.000
```

puedes inferir replenishment visible en L1.

Pero no sabes si:

```text
es la misma entidad
son nuevas órdenes
es iceberg
es una nueva cola
la quote estaba agregada
```

Debe mantenerse como aproximación.

---

# 15. Features que implican información futura

Aquí hay una distinción crítica.

No todo lo que puede calcularse científicamente puede utilizarse como feature de decisión en el mismo instante.

## Ejemplo: `price_impact_after_trade_bursts`

Supón que defines:

```text
price_impact_after_burst_5s =
    midquote(t + 5s)
    − midquote(t)
```

Para conocer ese valor necesitas esperar cinco segundos.

Por tanto, en el instante `t` es:

```text
información futura
```

No puede incluirse en el `market_state` utilizado para decidir en `t`.

Debe ir en:

```text
outcomes_table
labels
evaluation table
microstructure response table
```

Puede utilizarse como feature sólo para episodios anteriores ya finalizados, nunca para el evento actual antes de conocer el futuro.

## `realized_spread`

El realized spread suele medir el resultado respecto a un midquote posterior:

```text
realized_spread_5s =
    2 × sign ×
    (trade_price − midquote_t_plus_5s)
```

Eso también requiere futuro.

Por tanto:

```text
effective_spread:
observable al asociar trade y quote contemporánea

realized_spread_5s:
resultado posterior
```

No deben almacenarse bajo la misma semántica temporal.

## `quote_response_latency`

Si defines:

```text
tiempo desde un burst
hasta que cambia el best bid/ask
```

también necesitas observar lo que ocurre después del burst.

Para investigar episodios pasados es válida.

Pero para el snapshot exacto de inicio del burst todavía no está disponible.

La regla debe ser:

> Una feature puede entrar en `market_state` sólo si su valor estaba completamente determinado utilizando información disponible como máximo en `decision_timestamp_utc`.

---

# 16. Qué papel desempeñan las otras tablas del ZIP

He revisado las 19 fichas. El diseño general está bien separado por responsabilidades.

## `000 instrument_master`

Resuelve identidad temporal:

```text
ticker
instrument_id
company identity
ticker lifecycle
exchange
vigencia
```

Es fundamental para evitar mezclar empresas distintas que reutilizan un ticker.

No contiene las features del punto 10.

## `001 market_calendar`

Define:

```text
trading dates
session open
session close
half-days
holidays
timezone
```

Sirve para interpretar correctamente timestamps y sesiones.

No es una tabla de alpha features.

## `002 expected_data_calendar`

Define qué cobertura debería existir:

```text
ticker-date
dataset esperado
sesión esperada
```

Sirve para detectar ausencia de datos y distinguir:

```text
cero actividad
```

de:

```text
archivo ausente
```

## `003 dataset_certification_matrix`

Contiene estados de certificación, calidad o usabilidad:

```text
certified
review
bad_data
recoverable_with_flag
reference mismatch
```

Sus campos pueden convertirse en:

```text
quality gates
sample eligibility
sample weights
```

Pero no son señales económicas del tape.

## `004 master_daily_table`

Aporta contexto diario:

```text
open
high
low
close
volume
gap
ATR
RVOL
range
dollar volume
```

Puede formar parte del `market_state` bajo:

```text
daily__
```

No sustituye la microestructura.

## `005 corporate_actions_table`

Gestiona:

```text
splits
reverse splits
dividends
ticker changes
effective dates
adjustment factors
```

Es esencial para que las comparaciones históricas sean económicamente coherentes.

## `006 halts_table`

Contiene episodios de suspensión:

```text
halt start
resume time
halt code
duration
```

Puede aportar:

```text
time_since_resume
halts_count_today
currently_halted
```

al estado.

## `007 event_windows_table`

Define las ventanas vinculadas a los eventos:

```text
event_window_id
event_id
pre-event start
event timestamp
post-event end
```

Es el marco temporal de extracción.

No debería almacenar todas las features calculadas.

## `008 outcomes_table`

Debe contener resultados posteriores:

```text
MFE
MAE
return after N seconds
HOD break
failure
halt
time to target
time to stop
```

Aquí encajan mejor varias métricas prospectivas del punto 10, como:

```text
price impact after trade bursts
realized spread en horizonte futuro
quote response posterior
```

Es correcto que esté separada de `market_state`.

## `009 fundamentals_asof_table`

Aporta datos fundamentales point-in-time:

```text
market cap
shares outstanding
float, si existe
filings
fundamental effective timestamp
```

Debe respetar disponibilidad histórica y evitar usar publicaciones posteriores.

## `010 news_context_table`

Aporta:

```text
headline
news timestamp
catalyst category
source
novelty
age of catalyst
```

Puede incorporarse al estado como:

```text
news__
```

## `011 short_context_table`

Aporta contexto de ventas en corto:

```text
short volume
short volume ratio
availability
borrow context
```

Según la fuente y el timestamp disponible.

## `012 regime_context_table`

Define el régimen:

```text
market trend
volatility regime
small-cap activity
time-of-day regime
risk-on/risk-off proxies
```

Sirve para condicionar señales y modelos.

## `013`

La ficha correspondiente actúa dentro de las superficies previas o intermedias del pipeline según tu estructura, pero no reemplaza la tabla microestructural. Su contenido debe tratarse como una fuente contextual o de ensamblaje, no como la definición de las features de trades y quotes del punto 10.

## `014 master_intraday_bar_table`

Contiene barras intradía:

```text
open
high
low
close
volume
VWAP o derivados
price views
quality flags
split handling
```

Permite calcular:

```text
distance to VWAP
distance to HOD
bar return
range
volume acceleration de barras
intraday volatility
```

Pero una barra de un minuto no puede reproducir:

```text
intertrade duration
ask lifts
bid hits
signed trade volume
tape burstiness
quote response en milisegundos
```

Por tanto, `014` y `015` son complementarias.

## `015 microstructure_features_table`

Es la superficie correcta para el punto 10.

Actualmente, sin embargo, tiene principalmente:

```text
aggregates
coverage
quality diagnostics
basic spread/depth
basic trade volume and size
```

Necesita una ampliación significativa.

## `016 market_state_table`

Debe ensamblar el estado completo observable en el timestamp de decisión.

No debería ser la primera superficie donde se inventen las fórmulas microestructurales.

Debe consumirlas ya definidas y versionadas.

## `017 event_state_table`

Debe vincular estados con eventos y roles temporales.

No es el lugar principal para calcular las features raw.

## `018 intraday_scanner_candidates_table`

Contiene criterios de selección intradía, como:

```text
gap_pct
rvol_20d
extended_volume
max_move_vs_prev_close_pct
first_cross_50_ts_utc
volume_to_time_at_first_cross
selected_intraday_in_play_candidate
```

Responde:

> ¿Qué símbolos fueron considerados candidatos y por qué?

No responde:

> ¿Qué estaba haciendo el tape en los últimos cinco segundos?

Es una tabla de selección, no una tabla de microestructura ni el estado completo.

---

# 17. Estado de materialización real

También hay que distinguir:

```text
schema definido
```

de:

```text
tabla producida y validada sobre el universo
```

Según las fichas:

```text
014 master_intraday_bar_table:
piloto o scoped
no promovida todavía como full-universe oficial
```

```text
015 microstructure_features_table:
seed_event_window_smoke
1 fila
1 ticker
1 ventana
```

```text
016 market_state_table:
schema objetivo definido
tabla oficial no materializada
candidate controlado no promovido
```

```text
017 event_state_table:
schema objetivo definido
tabla oficial no materializada
candidate controlado no promovido
```

```text
018 intraday_scanner_candidates_table:
candidate controlled replay
no promovida
```

Esto significa que, en este momento, tienes principalmente:

```text
arquitectura
contratos
schemas
prototipos controlados
```

No todavía:

```text
una feature store microestructural completa,
materializada y certificada para todo el histórico
```

Eso no es una crítica. Es simplemente el estado real del proyecto.

---

# 18. Respuesta exacta a tu pregunta

Tu pregunta era:

> ¿Las tablas del punto 10 están definidas aquí? ¿El texto del punto 10 se refiere a este tipo de tablas?

La respuesta precisa es:

## Sí, se refiere a este tipo de arquitectura

Las features del punto 10 deben vivir en el sistema de tablas que has diseñado.

La localización correcta es:

```text
015 microstructure_features_table
        ↓
016 market_state_table
        ↓
017 event_state_table
```

## Pero no están definidas completamente

La tabla `015` sólo contiene una primera capa de:

```text
volumen total
dollar volume
odd lots
tamaño de trades
spread
top depth L1
crossed/locked markets
calidad y cobertura
```

Faltan la mayoría de las features dinámicas:

```text
rate
durations
bursts
acceleration
direction
signed flow
aggressor classification
microprice
OFI
depletion proxies
spread dynamics
```

## Y algunas no son features de estado

Variables como:

```text
price impact after burst
realized spread
future quote response
```

dependen de datos posteriores.

Deberían ir principalmente en:

```text
008 outcomes_table
```

o en una tabla especializada de respuestas microestructurales.

No en el estado observable que utiliza el modelo para decidir.

---

# 19. Cómo debería quedar conceptualmente la arquitectura

```text
RAW TRADES
RAW QUOTES
      │
      ├── quality policies
      ├── trade-condition eligibility
      ├── deduplication views
      ├── timestamp policy
      └── quote-trade alignment policy
              │
              ▼
015 microstructure_features_table
      │
      ├── trade intensity
      ├── volume intensity
      ├── intertrade durations
      ├── size distributions
      ├── signed order flow
      ├── bid-hit / ask-lift
      ├── spread and microprice
      ├── L1 OFI
      ├── acceleration
      ├── burstiness
      └── depletion proxies
              │
              ▼
016 market_state_table
      │
      ├── daily context
      ├── intraday bars
      ├── microstructure
      ├── news
      ├── fundamentals
      ├── short context
      ├── halts
      ├── regime
      └── quality
              │
              ▼
017 event_state_table
      │
      ├── pre_event
      ├── at_event
      ├── replay
      └── review state
              │
              ├──────────────► model inputs
              │
              ▼
008 outcomes_table
      ├── future returns
      ├── MFE / MAE
      ├── break / failure
      ├── price impact
      ├── future spread
      └── response latency
```

---

# 20. Mi conclusión final

Lo que has construido no contradice el punto 10.

En realidad, has construido el **esqueleto arquitectónico correcto** para poder implementar el punto 10.

Pero aún no has construido el contenido microestructural completo.

La situación real es:

```text
arquitectura de tablas:
bien encaminada

separación de responsabilidades:
correcta

ubicación de microstructure features:
correcta

features básicas:
parcialmente definidas

features dinámicas de tape:
mayoritariamente ausentes

features trade-quote:
ausentes o no formalizadas

features futuras:
deben separarse como outcomes

materialización full-history:
todavía pendiente
```

La formulación más exacta sería:

> La tabla `015_microstructure_features_table` es el lugar donde deben definirse científicamente las variables del punto 10. Las tablas `016_market_state_table` y `017_event_state_table` deben consumir esas variables y situarlas en el contexto de decisión y del evento. Sin embargo, el contrato actual de la tabla 015 sólo contiene una primera capa de agregados y controles de calidad; todavía no incorpora la mayor parte de las features dinámicas de tape, agresión, flujo firmado, microprice, OFI, aceleración y respuesta del spread descritas en el punto 10.

El siguiente paso lógico no es crear otra tabla general. Es desarrollar un contrato específico como:

```text
microstructure_feature_definitions_contract_v0_1.md
```

que defina, para cada feature:

```text
nombre canónico
familia
fórmula
unidad
raw inputs
ventana
timestamp semantics
trade eligibility
quote alignment
null policy
quality requirements
observability
leakage status
version
```



