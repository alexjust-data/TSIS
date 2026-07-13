# Revisión completa desde cero con toda la data nueva

> Tus datos de quotes contienen bid, ask y tamaños, también conservan `participant_timestamp`, `sequence_number`, timestamp del feed, `ask_exchange`, `bid_exchange`, `tape`, `conditions`, `indicators` y `trf_timestamp`.

Además:

> Los trades tienen timestamp con precisión física de microsegundos, no sólo milisegundos.

Esto no te proporciona MBO ni diez niveles de profundidad,   
pero sí permite construir una capa de microestructura L1 mucho más seria, especialmente para:

```text
secuenciación de quotes
latencia participant-to-feed
dinámica del BBO
quote update intensity
venue transitions
microprice
L1 imbalance
OFI
trade-quote alignment
aggressor classification
spread dynamics
depletion/replenishment proxies
```

Voy a reconstruir la respuesta desde los datos físicos hacia las tablas de features, estados y outcomes.

---

# 1. Inventario real de los datos que tienes

## 1.1 Trades event-level

Schema físico:

```text
ticker
date
timestamp timestamp[us]
price
size
exchange
conditions[]
year
month
day
```

Esto permite estudiar:

```text
secuencia de ejecuciones
precio
tamaño
venue/exchange
sale conditions
tiempo entre trades
intensidad del tape
distribución de tamaños
odd lots
movimiento de precio por ejecución
```

La precisión física declarada es:

```text
timestamp[us]
```

Por tanto, la unidad almacenada admite microsegundos.

Eso no garantiza que todos los eventos originales tengan precisión real de microsegundos ni que el orden dentro de timestamps idénticos sea perfecto, pero es mejor de lo que habíamos asumido.

### Limitaciones del trade raw

No aparecen demostrados:

```text
trade sequence_number
trade_id
sip_timestamp separado
participant_timestamp separado
correction_id
cancel_reference
order_id
```

Por tanto, para trades:

- puedes ordenar por timestamp;
- no siempre puedes resolver empates perfectos;
- la deduplicación económica sigue siendo incierta;
- las correcciones y cancelaciones necesitan una política basada en `conditions`.

---

## 1.2 Quotes L1 event-level

Schema físico:

```text
ask_exchange
ask_price
ask_size
bid_exchange
bid_price
bid_size
conditions[]
indicators[]
participant_timestamp
sequence_number
timestamp
tape
trf_timestamp
year
month
day
```

Esta tabla es mucho más potente de lo que habíamos considerado.

Tienes dos referencias temporales fundamentales:

```text
participant_timestamp
timestamp
```

Y una referencia de orden:

```text
sequence_number
```

Esto permite calcular, bajo validación previa:

```text
feed_latency =
    timestamp - participant_timestamp
```

También permite:

```text
ordenar quotes de forma más robusta
detectar gaps de secuencia
detectar quotes fuera de orden
medir quote update rate
estudiar estabilidad del BBO
distinguir exchanges en bid y ask
estudiar cambios de venue
analizar conditions e indicators
```

### Lo que todavía no es

No contiene:

```text
bid level 2
bid level 3
...
ask level 10
order_id
order lifecycle
queue position
número de órdenes por nivel
```

Por tanto sigue siendo:

```text
L1 / BBO event-level
```

No:

```text
MBP-10
MBO
L3
```

---

## 1.3 Daily OHLCV

Schema:

```text
ticker
date
year
o
h
l
c
v
vw
n
t
```

Además de OHLCV tienes:

```text
vw = VWAP diario
n  = número de transacciones
t  = timestamp
```

`n` es especialmente útil. Permite crear:

```text
average_trade_size_daily = volume / transaction_count
daily_trade_intensity
daily_transaction_count_surprise
volume_vs_transaction_count
dollar_volume_per_transaction
```

---

## 1.4 Daily adjusted

Además del daily raw tienes:

```text
future_split_factor
o_split_normalized
h_split_normalized
l_split_normalized
c_split_normalized

future_dividend_sum
future_dividend_factor
future_adjustment_factor

o_adjusted
h_adjusted
l_adjusted
c_adjusted

o_adjusted_proxy
h_adjusted_proxy
l_adjusted_proxy
c_adjusted_proxy

materialized_price_view
source_daily_file
source_splits_file
source_dividends_file
```

Esto te permite mantener varias vistas económicas:

```text
raw
split-normalized
fully adjusted
adjusted proxy
```

Es muy importante no usar automáticamente los campos llamados `future_*` dentro de un estado de decisión.

El hecho de que una tabla calcule un factor usando acciones corporativas futuras para normalización histórica no significa que ese factor fuera conocido en la fecha original.

Debe distinguirse:

```text
normalización retrospectiva para comparabilidad
vs.
información observable point-in-time
```

---

## 1.5 OHLCV de un minuto

Schema:

```text
ticker
ts_utc
date
year
month
o
h
l
c
v
vw
n
t
```

También tienes:

```text
VWAP por barra
transaction_count por barra
```

Esto amplía mucho las features intradía.

No sólo puedes medir volumen; puedes medir:

```text
trade_count por minuto
average trade size por minuto
volume per transaction
dollar volume per transaction
transaction-count acceleration
```

---

## 1.6 OHLCV 1m split-normalized

Añade:

```text
future_split_factor
o_split_normalized
h_split_normalized
l_split_normalized
c_split_normalized
vw_split_normalized
materialized_price_view
source_1m_file
source_splits_file
pilot_role
pilot_event_type
pilot_event_date
```

Y tu arquitectura contempla además una vista:

```text
1m_quote_guarded_raw
```

para corregir o proteger barras sospechosas mediante quotes.

Esta superficie es muy valiosa para:

```text
calidad de precios
detección de prints aberrantes
reparación controlada
comparabilidad de price views
sensibilidad del modelo a precios raw vs corregidos
```

---

## 1.7 Reference snapshots

Schema:

```text
ticker
name
market
locale
primary_exchange
type
active
currency_name
cik
composite_figi
share_class_figi
last_updated_utc
snapshot_date
_exchange_filter
_dataset
_ingested_utc
```

Esto permite resolver mejor:

```text
identidad económica
ticker reuse
exchange
tipo de instrumento
vigencia
CIK
FIGI
```

Tu `instrument_master` materializado ya amplía esto a 53 atributos, incluyendo:

```text
instrument_id
identity_resolution_level
valid_from
valid_to
ticker_type
is_common_stock
market cap observado
shares outstanding
clasificación <1B
ticker changes
temporal identity
```

Esto es fundamental para evitar que features históricas de dos entidades distintas se mezclen bajo un mismo ticker.

---

## 1.8 Halts

Tienes:

```text
source
source_priority
ticker
issuer_name
listing_exchange
halt_date
halt_start_et
resume_quote_et
resume_trade_et
halt_code
halt_type
raw_reason
release_no
item_link
url_source
is_sec_suspension
```

La separación entre:

```text
resume_quote_et
resume_trade_et
```

es especialmente interesante.

Permite calcular:

```text
quote-to-trade resume latency
duración del halt
tiempo hasta primera quote
tiempo hasta primera ejecución
comportamiento inmediatamente posterior
```

---

## 1.9 Short interest

Tienes:

```text
settlement_date
ticker
short_interest
avg_daily_volume
days_to_cover
```

Es una superficie de baja frecuencia —normalmente quincenal—, pero útil como contexto.

No debe confundirse con:

```text
short sale volume diario
borrow availability en tiempo real
locates
borrow fee intradía
```

---

# 2. Qué cambia respecto a mi respuesta anterior

La corrección más importante es:

## Antes asumíamos quotes con información temporal limitada

Ahora sabemos que existen:

```text
participant_timestamp
sequence_number
timestamp
tape
bid_exchange
ask_exchange
conditions
indicators
```

Por tanto puedes investigar científicamente:

```text
participant-to-feed latency
quote sequence integrity
quote message intensity
quote bursts
venue changes at BBO
bid/ask venue persistence
quote update asymmetry
stale quote detection
sequence gaps
timestamp disorder
```

## Antes considerábamos granularidad al menos milisegundo

Ahora el trade schema declara:

```text
timestamp[us]
```

Y los ejemplos muestran microsegundos:

```text
2025-05-12T13:30:18.770626
```

Esto permite ventanas como:

```text
100 µs
500 µs
1 ms
5 ms
10 ms
50 ms
100 ms
```

Pero con una cautela:

> Que el almacenamiento sea de microsegundos no demuestra que la fuente original, la secuencia ni la latencia económica sean exactas a esa resolución.

Para monetización real, seguiría priorizando:

```text
100 ms
250 ms
500 ms
1 s
2 s
5 s
```

frente a inferencias submilisegundo.

---

# 3. La separación correcta de la arquitectura

No basta con distinguir:

```text
tablas de features
vs.
tablas de estado
```

Para TSIS necesitas distinguir al menos siete capas:

```text
1. Raw event data
2. Clean/eligible event views
3. Primitive tables
4. Feature tables
5. State tables
6. Outcomes/labels
7. Execution and policy tables
```

Arquitectura:

```text
RAW TRADES / RAW QUOTES
        │
        ├── eligibility
        ├── condition decoding
        ├── sequence validation
        ├── timestamp normalization
        ├── deduplication views
        └── quality gates
                │
                ▼
EVENT PRIMITIVES
        │
        ├── trade primitives
        ├── quote primitives
        ├── trade-quote matches
        └── microstructure episodes
                │
                ▼
FEATURE TABLES
        │
        ├── trade features
        ├── quote features
        ├── trade-quote features
        ├── intraday features
        ├── daily features
        ├── halt features
        ├── short features
        ├── fundamentals/news
        └── regime features
                │
                ▼
STATE TABLES
        │
        ├── market_state
        ├── event_state
        ├── strategy_state
        ├── position_state
        └── execution_state
                │
                ▼
DECISION / POLICY
                │
                ▼
OUTCOMES
```

---

# 4. Las tablas de features que te recomiendo

Tu `015_microstructure_features_table` actual es demasiado amplia conceptualmente y demasiado pobre en features físicas.

La dividiría lógicamente en estas superficies.

## 4.1 `trade_event_primitives_table`

Grano:

```text
un trade elegible
```

Campos:

```text
trade_event_id
instrument_id
ticker
timestamp_utc
price
size
notional
exchange
conditions
session_segment
trade_eligibility_state
dedup_view
previous_trade_timestamp
intertrade_duration_us
previous_trade_price
price_change
log_return
tick_direction
```

No es una feature agregada. Es una capa primitiva reproducible.

---

## 4.2 `quote_event_primitives_table`

Grano:

```text
un mensaje de quote
```

Campos derivados:

```text
quote_event_id
participant_timestamp
sip_or_feed_timestamp
sequence_number
sequence_gap
timestamp_latency_ns
bid_price
ask_price
bid_size
ask_size
bid_exchange
ask_exchange
midprice
spread_dollars
spread_bps
top_depth
l1_imbalance
microprice
quote_age_from_previous
bid_changed
ask_changed
bid_price_changed
ask_price_changed
bid_size_changed
ask_size_changed
```

---

## 4.3 `trade_quote_alignment_table`

Grano:

```text
un trade emparejado con una quote
```

Campos:

```text
trade_event_id
matched_quote_event_id
trade_timestamp
quote_participant_timestamp
quote_feed_timestamp
alignment_method
alignment_lag_ns
bid
ask
mid
bid_size
ask_size
trade_location
trade_sign
classification_method
classification_confidence
```

Esta tabla debería ser central.

No recalcularía trade signing dentro de cada modelo.

---

## 4.4 `microstructure_window_features_table`

Grano recomendado:

```text
instrument_id
+ decision_timestamp_utc
+ feature_window
+ feature_policy_version
```

No sólo:

```text
event_window_id + start + end
```

Las ventanas deberían ser retrospectivas:

```text
100ms
250ms
500ms
1s
2s
5s
10s
30s
60s
120s
300s
```

---

## 4.5 `microstructure_episode_table`

Grano:

```text
un episodio microestructural detectado
```

Tipos:

```text
trade_burst
quote_burst
spread_collapse
spread_expansion
bid_depletion
ask_depletion
apparent_replenishment
signed_flow_flip
liquidity_vacuum
price_jump
tape_stall
venue_switch
quote_latency_spike
```

---

## 4.6 `intraday_features_table`

Derivada del OHLCV 1m, no de trades y quotes.

Grano:

```text
instrument_id
+ ts_utc
+ lookback_window
+ price_view
```

---

## 4.7 `daily_features_table`

Derivada de daily raw y de price views normalizadas.

Grano:

```text
instrument_id + session_date + price_view
```

---

# 5. Features microestructurales basadas sólo en trades

## 5.1 Intensidad

Para una ventana \(W\):

\[
\lambda_N(t,W)=\frac{N(t-W,t]}{W}
\]

```text
trade_count
trade_count_rate
share_volume
share_volume_rate
dollar_volume
dollar_volume_rate
```

Añadiría:

```text
transaction_notional_mean
transaction_notional_median
volume_per_trade
dollar_volume_per_trade
```

Ventanas:

```text
100ms
250ms
500ms
1s
2s
5s
10s
30s
60s
```

---

## 5.2 Duraciones entre trades

```text
intertrade_duration_mean
intertrade_duration_median
intertrade_duration_p10
intertrade_duration_p25
intertrade_duration_p75
intertrade_duration_p90
intertrade_duration_p99
intertrade_duration_std
intertrade_duration_cv
intertrade_duration_min
intertrade_duration_max
zero_duration_ratio
long_silence_ratio
```

En microcaps es útil distinguir:

```text
silencio
actividad normal
burst
```

---

## 5.3 Distribución de tamaños

```text
trade_size_mean
trade_size_median
trade_size_std
trade_size_cv
trade_size_p10
trade_size_p25
trade_size_p75
trade_size_p90
trade_size_p95
trade_size_p99
trade_size_max
trade_size_skewness
trade_size_kurtosis
```

Ratios:

```text
odd_lot_count_ratio
odd_lot_volume_ratio
round_lot_count_ratio
round_lot_volume_ratio
sub_10_share_ratio
sub_50_share_ratio
size_100_exact_ratio
size_500_plus_ratio
size_1000_plus_ratio
```

---

## 5.4 Concentración y fragmentación

```text
trade_size_entropy
trade_notional_entropy
trade_size_herfindahl
top_1pct_volume_share
top_5pct_volume_share
largest_trade_volume_share
unique_size_count
repeated_size_ratio
modal_trade_size
modal_size_frequency
```

Esto puede medir:

```text
fragmentación
concentración
repetición de tamaños
heterogeneidad del tape
```

Sin afirmar automáticamente que existe un iceberg o un algoritmo concreto.

---

## 5.5 Secuencia de precios

Para cada trade:

\[
r_i=\log(P_i/P_{i-1})
\]

Features:

```text
positive_tick_ratio
negative_tick_ratio
zero_tick_ratio
price_change_mean
price_change_median
absolute_price_change_mean
absolute_price_change_p90
event_time_realized_variance
event_time_realized_volatility
trade_price_range
number_of_price_levels_traded
price_level_transition_count
```

---

## 5.6 Eficiencia del desplazamiento

\[
ER=
\frac{|P_{end}-P_{start}|}
{\sum_i |P_i-P_{i-1}|}
\]

```text
trade_path_efficiency
net_move_per_trade
net_move_per_1000_shares
net_move_per_10000_dollars
ticks_moved_per_100_trades
volume_per_tick_moved
dollar_volume_per_tick_moved
```

Esto diferencia:

```text
movimiento limpio
chop
absorción aparente
fragilidad
agotamiento
```

---

## 5.7 Burstiness

\[
B=
\frac{\sigma_{\Delta t}-\mu_{\Delta t}}
{\sigma_{\Delta t}+\mu_{\Delta t}}
\]

```text
burstiness_index
fano_factor
max_trades_in_1ms
max_trades_in_10ms
max_trades_in_100ms
max_trades_in_1s
burst_count
burst_duration_mean
burst_trade_count_mean
burst_volume_mean
burst_volume_max
burst_notional_max
```

---

## 5.8 Aceleración del tape

No una única columna, sino una familia:

```text
trade_count_acceleration
share_volume_acceleration
dollar_volume_acceleration
intertrade_duration_compression
```

Ejemplo:

\[
A_{1s,5s}
=
\log(1+\lambda_{1s})
-
\log(1+\lambda_{5s})
\]

```text
count_acceleration_250ms_vs_1s
count_acceleration_1s_vs_5s
count_acceleration_5s_vs_30s

share_volume_acceleration_1s_vs_5s
dollar_volume_acceleration_1s_vs_5s
```

Segunda derivada:

```text
tape_jerk
```

que representa:

```text
cambio de la aceleración
```

---

## 5.9 Trade-direction provisional

Sólo con trades:

```text
tick_rule_sign
reverse_tick_rule_sign
zero_tick_carry_sign
```

Features:

```text
tick_signed_trade_count
tick_signed_share_volume
tick_signed_dollar_volume
same_sign_transition_ratio
positive_run_length_mean
negative_run_length_mean
positive_run_length_max
negative_run_length_max
sign_autocorrelation_lag1
sign_autocorrelation_lag5
```

Debe etiquetarse claramente:

```text
trade_sign_method = tick_rule
```

y no mezclarse con el signing basado en quotes.

---

## 5.10 Exchange y condiciones de trades

Como tienes:

```text
exchange
conditions[]
```

puedes crear:

```text
trade_exchange_count
trade_exchange_entropy
dominant_trade_exchange
dominant_trade_exchange_share
exchange_switch_rate
exchange_concentration
```

También:

```text
condition_code_count
condition_entropy
condition_specific_ratios
late_trade_ratio
out_of_sequence_condition_ratio
eligible_price_forming_ratio
```

Pero antes debes crear un:

```text
trade_conditions_decoding_contract
```

No es científicamente correcto tratar todas las condiciones igual.

---

# 6. Features basadas sólo en quotes

## 6.1 Estado L1 básico

```text
bid_price
ask_price
bid_size
ask_size
midprice
spread_dollars
spread_ticks
spread_bps
top_depth
```

Mantendría las tres representaciones del spread:

```text
dólares
ticks
basis points
```

---

## 6.2 L1 imbalance

\[
I=
\frac{Q_b-Q_a}
{Q_b+Q_a}
\]

```text
l1_size_imbalance
bid_top_depth_share
ask_top_depth_share
log_bid_ask_size_ratio
```

No es queue imbalance real. Es imbalance agregado visible en L1.

---

## 6.3 Microprice

\[
MP=
\frac{Ask\cdot Q_b+Bid\cdot Q_a}
{Q_b+Q_a}
\]

```text
microprice
microprice_minus_mid
microprice_minus_mid_bps
microprice_position_in_spread
microprice_pressure
```

---

## 6.4 Quote update intensity

Gracias a `sequence_number` y timestamps puedes calcular:

```text
quote_update_count
quote_update_rate
bid_update_rate
ask_update_rate
bid_price_update_rate
ask_price_update_rate
bid_size_update_rate
ask_size_update_rate
```

Y:

```text
quote_interarrival_mean
quote_interarrival_median
quote_interarrival_p10
quote_interarrival_cv
quote_burstiness
```

---

## 6.5 Sequence integrity

```text
sequence_gap_count
sequence_gap_size_total
sequence_gap_max
sequence_duplicate_count
sequence_reversal_count
out_of_order_timestamp_count
sequence_timestamp_disagreement
```

Esto no es alpha directamente, pero es esencial para saber cuándo las features son fiables.

---

## 6.6 Participant-to-feed latency

Si ambas unidades temporales están correctamente documentadas:

\[
L_i =
timestamp_i-participant\_timestamp_i
\]

Features:

```text
quote_feed_latency_mean
quote_feed_latency_median
quote_feed_latency_p90
quote_feed_latency_p99
quote_feed_latency_std
quote_feed_latency_spike_ratio
negative_latency_count
```

Puede ser útil para:

```text
quality control
régimen del feed
alineamiento trade-quote
detección de episodios de congestión
```

No asumiría inicialmente que esa latencia representa exactamente tu latencia futura de recepción live. Representa la diferencia entre los timestamps conservados por el proveedor.

---

## 6.7 Dinámica del spread

```text
spread_mean
spread_median
spread_p10
spread_p90
spread_std
spread_cv
spread_min
spread_max
spread_time_weighted_mean
```

Derivadas:

```text
spread_change
spread_slope
spread_acceleration
spread_compression_ratio
spread_expansion_ratio
time_at_one_tick
time_locked
time_crossed
locked_transition_rate
crossed_transition_rate
```

---

## 6.8 Estabilidad y flicker

```text
quote_age
time_at_same_bbo
time_at_same_bid
time_at_same_ask
quote_persistence
quote_flicker_rate
quote_reversal_rate
bid_reversal_rate
ask_reversal_rate
```

Puedes definir flicker como:

```text
cambio que se revierte dentro de X ms
```

con varias ventanas:

```text
1ms
5ms
10ms
50ms
100ms
```

---

## 6.9 Venue features en BBO

Tienes:

```text
bid_exchange
ask_exchange
```

Puedes calcular:

```text
bid_exchange_entropy
ask_exchange_entropy
dominant_bid_exchange
dominant_ask_exchange
bid_exchange_persistence
ask_exchange_persistence
bid_venue_switch_rate
ask_venue_switch_rate
same_exchange_both_sides_ratio
```

Y transiciones:

```text
bid_exchange_transition_matrix
ask_exchange_transition_matrix
```

Esto no recrea el libro de cada exchange, pero sí describe qué venue aparece en el BBO.

---

## 6.10 Quote conditions e indicators

Puedes generar:

```text
quote_condition_frequency
quote_indicator_frequency
condition_transition_rate
indicator_transition_rate
condition_specific_spread
indicator_specific_spread
condition_specific_depth
```

Pero primero necesitas decodificar oficialmente los códigos.

No trataría `conditions` ni `indicators` como números continuos.

Son categorías semánticas.

---

# 7. Features trade–quote

Ésta puede convertirse en la familia más valiosa de tus datos.

## 7.1 Alineamiento temporal

Para cada trade se deben probar políticas como:

```text
matched quote by participant_timestamp
matched quote by feed timestamp
latest quote before trade
latest quote before trade minus 1ms
minus 5ms
minus 10ms
minus 25ms
minus 50ms
```

Ahora que las quotes tienen:

```text
participant_timestamp
feed timestamp
sequence_number
```

puedes hacer una investigación de alineamiento mucho más rigurosa.

Campos de calidad:

```text
alignment_lag_us
alignment_method
quote_age_at_trade
classification_stability_across_lags
alignment_confidence
```

---

## 7.2 Trade location

\[
Location_i=
\frac{P_i-Bid_i}
{Ask_i-Bid_i}
\]

```text
trade_at_bid_ratio
trade_at_ask_ratio
trade_at_mid_ratio
trade_inside_spread_ratio
trade_outside_bbo_ratio
trade_location_mean
trade_location_volume_weighted
```

---

## 7.3 Aggressor classification

```text
ask_lift_count
ask_lift_volume
ask_lift_notional

bid_hit_count
bid_hit_volume
bid_hit_notional

inside_spread_count
unclassified_count
```

Ratios:

```text
ask_lift_count_ratio
ask_lift_volume_ratio
ask_lift_notional_ratio
bid_hit_count_ratio
bid_hit_volume_ratio
bid_hit_notional_ratio
classified_trade_ratio
```

---

## 7.4 Signed flow

\[
SV=\sum_i s_iq_i
\]

```text
signed_trade_count
signed_share_volume
signed_dollar_volume
signed_count_imbalance
signed_volume_imbalance
signed_dollar_imbalance
```

Es importante mantener las tres versiones porque pueden contradecirse:

```text
muchas compras pequeñas
vs.
pocas ventas grandes
```

---

## 7.5 Effective spread

\[
ES_i=
2s_i(P_i-M_i)
\]

```text
effective_spread_dollars_mean
effective_spread_bps_mean
effective_spread_bps_median
effective_spread_volume_weighted
```

---

## 7.6 L1 Order Flow Imbalance

Usando cambios en:

```text
bid price
bid size
ask price
ask size
```

Features:

```text
ofi_raw
ofi_per_second
ofi_normalized_by_top_depth
ofi_cumulative
ofi_mean
ofi_std
ofi_slope
ofi_acceleration
ofi_zscore
ofi_positive_event_ratio
ofi_negative_event_ratio
```

Ventanas:

```text
100ms
250ms
500ms
1s
5s
10s
30s
60s
```

Mantendría separadas:

```text
quote_OFI
signed_trade_flow
combined_flow
```

---

## 7.7 Flow-to-price response

```text
mid_return_per_unit_ofi
trade_return_per_signed_share
trade_return_per_signed_dollar
price_change_per_ask_lift_volume
price_change_per_bid_hit_volume
```

Asimetrías:

```text
positive_flow_price_beta
negative_flow_price_beta
flow_response_asymmetry
```

Esto puede identificar estados como:

```text
mucho flujo comprador con poco avance
poco flujo comprador con gran avance
mucho flujo vendedor sin caída
flujo vendedor que rompe el bid rápidamente
```

---

## 7.8 Depletion proxies

```text
bid_depletion_proxy
ask_depletion_proxy
bid_size_drop_after_bid_hits
ask_size_drop_after_ask_lifts
executed_volume_to_visible_bid_ratio
executed_volume_to_visible_ask_ratio
```

No son depletion real por orden.

Son:

```text
proxies L1 agregados
```

---

## 7.9 Apparent replenishment

```text
bid_refill_after_bid_hits
ask_refill_after_ask_lifts
refill_latency
refill_size_ratio
repeated_refill_count
```

Ejemplo:

```text
ask visible = 2.000
se ejecutan 10.000 en ask
ask sigue mostrando 2.000
```

Eso es compatible con:

```text
replenishment
liquidez oculta
nuevas órdenes
agregación del feed
```

No permite concluir:

```text
iceberg identificado
```

---

## 7.10 Quote response to trades

```text
time_to_bid_change_after_sell
time_to_ask_change_after_buy
time_to_mid_move_after_signed_burst
time_to_spread_change_after_trade
```

Estas variables tienen dos usos diferentes:

### Como outcomes de un episodio actual

Usan futuro:

```text
no pueden entrar en el estado inicial
```

### Como estadísticas históricas cerradas

Por ejemplo:

```text
median_response_latency_last_20_completed_bursts
```

Sí pueden ser observables en un estado posterior.

---

# 8. Features de latencia y calidad que antes no contemplábamos

Con tus quotes puedes crear una familia específica:

```text
quote_latency_features_table
```

Features:

```text
participant_to_feed_latency
latency_percentile
latency_spike
latency_regime
latency_autocorrelation
latency_vs_quote_rate
latency_vs_spread
latency_vs_volatility
```

También:

```text
sequence_integrity_score
timestamp_integrity_score
quote_freshness_score
alignment_reliability_score
```

Estas pueden funcionar como:

```text
quality gates
sample weights
confidence features
```

No sólo como filtros binarios.

---

# 9. Features intradía no microestructurales

Tus barras de un minuto incluyen:

```text
OHLC
volume
VWAP
transaction_count
```

Eso permite una capa muy rica.

## 9.1 Retornos y localización

```text
return_1m
return_2m
return_5m
return_10m
return_30m
```

```text
distance_to_vwap_pct
distance_to_hod_pct
distance_to_lod_pct
distance_to_open_pct
distance_to_previous_close_pct
distance_to_premarket_high_pct
distance_to_premarket_low_pct
```

En varias unidades:

```text
dólares
porcentaje
ticks
ATR
volatilidad intradía
```

---

## 9.2 Geometría del rango

\[
Position=
\frac{P-LOD}{HOD-LOD}
\]

```text
position_in_day_range
position_in_premarket_range
distance_from_range_mid
range_expansion
range_contraction
```

---

## 9.3 Transaction-count features

Ésta es una mejora importante respecto a mi respuesta anterior.

Como tienes `n`:

```text
transaction_count_1m
transaction_count_5m
transaction_count_rate
transaction_count_acceleration
volume_per_transaction
dollar_volume_per_transaction
```

Puedes distinguir:

```text
mucho volumen en pocas operaciones grandes
vs.
mucho volumen en muchas operaciones pequeñas
```

Eso es muy relevante en small caps.

---

## 9.4 VWAP de barra y VWAP acumulado

```text
bar_vwap
distance_close_to_bar_vwap
distance_to_session_vwap
session_vwap_slope
price_vwap_spread
price_vwap_spread_slope
```

Eventos:

```text
first_vwap_reclaim
failed_vwap_reclaim
vwap_hold_duration
vwap_rejection_magnitude
vwap_cross_count
```

---

## 9.5 Volumen y trade-count surprise

```text
volume_vs_same_minute_history
transaction_count_vs_same_minute_history
cumulative_volume_vs_expected
cumulative_transactions_vs_expected
```

Ratios combinados:

```text
volume_surprise / transaction_surprise
average_trade_size_surprise
```

---

## 9.6 Estructura de máximos y mínimos

```text
number_of_hod_tests
number_of_lod_tests
time_since_hod
time_since_lod
volume_since_hod
transactions_since_hod
drawdown_from_hod
recovery_from_lod
failed_break_count
```

---

## 9.7 Trayectoria

```text
linear_slope
linear_fit_r2
path_efficiency
higher_high_count
higher_low_count
lower_high_count
lower_low_count
bar_overlap_ratio
body_to_range_ratio
upper_wick_ratio
lower_wick_ratio
```

---

# 10. Features daily

Como tienes:

```text
OHLCV
VWAP
transaction_count
```

puedes crear:

```text
gap_pct
daily_return_pct
intraday_return_pct
daily_range_pct
ATR
ATR_pct
RVOL
dollar_volume
transaction_count_daily
average_trade_size_daily
dollar_volume_per_transaction
```

Históricas:

```text
volume_percentile_20d
transaction_count_percentile_20d
average_trade_size_percentile_20d
range_percentile_20d
gap_percentile
VWAP_close_displacement
```

---

# 11. Features de price-view y calidad

Tu sistema tiene múltiples vistas:

```text
raw
split_normalized
adjusted
adjusted_proxy
quote_guarded_raw
```

Eso permite crear una familia que casi ningún sistema retail tiene:

```text
raw_vs_split_price_difference
raw_vs_adjusted_difference
raw_vs_quote_guarded_difference
bar_repair_applied
repair_magnitude
repair_reason
price_view_disagreement
VWAP_view_disagreement
```

Estas variables no son alpha puro, pero permiten:

```text
detectar muestras inestables
medir sensibilidad del modelo
evitar aprender errores de precio
ponderar observaciones
```

---

# 12. Features de identidad e instrumento

Tu `instrument_master` tiene mucha más información de la que habíamos tratado.

Puedes usar:

```text
identity_resolution_level
ticker_age
days_since_list_date
is_common_stock
primary_exchange
SIC
market_cap
weighted_shares_outstanding
ticker_change_count
days_since_ticker_change
```

Especialmente:

```text
market_cap
shares outstanding
ticker age
listing age
exchange
security type
```

Pero debes respetar la temporalidad de:

```text
overview_request_date
shares_observed_date
shares_age_days
```

Una cifra de market cap solicitada en 2025 no puede usarse como si fuera conocida en 2010.

---

# 13. Features de corporate actions

```text
split_count
reverse_split_count
days_since_split
days_until_known_announced_split
split_factor
dividend_count
ticker_change_count
days_since_ticker_change
```

Debes separar:

```text
effective date
announcement date
known_at date
```

Especialmente en reverse splits, que son fundamentales en microcaps.

---

# 14. Features de halts

Con tus atributos puedes construir:

```text
halt_count_today
time_since_last_halt
halt_duration
resume_quote_delay
resume_trade_delay
quote_to_trade_resume_gap
halt_code
halt_type
is_sec_suspension
```

Al reanudar:

```text
resume_spread
resume_bid_size
resume_ask_size
resume_trade_rate
resume_volume_rate
resume_signed_flow
resume_price_jump
```

También outcomes:

```text
time_to_second_halt
second_halt
post_resume_MFE
post_resume_MAE
```

---

# 15. Features de short interest

```text
short_interest
days_to_cover
short_interest_change
short_interest_pct_change
days_to_cover_change
short_interest_zscore
days_since_short_settlement
short_data_age_days
```

Si dispones de shares/float temporalmente válidos:

```text
short_interest_pct_shares_outstanding
short_interest_pct_float
```

Pero sólo con float point-in-time fiable.

---

# 16. Las tablas de estado que deberías tener

Ahora podemos separar claramente feature tables de state tables.

## 16.1 `market_state_table`

Grano actual definido:

```text
instrument_id
+ decision_timestamp_utc
+ state_horizon
+ state_scope
+ state_schema_version
```

Es correcto.

Debe contener un snapshot seleccionado de namespaces:

```text
identity__
calendar__
daily__
intraday__
microstructure__
halts__
short__
fundamentals__
news__
regime__
scanner__
quality__
```

No todas las features existentes.

---

## 16.2 `event_state_table`

Grano definido:

```text
event_window_id
+ decision_timestamp_utc
+ state_role
+ state_schema_version
```

También es correcto.

Roles:

```text
pre_event
at_event
confirmation
post_event_review
research_replay
```

Pero:

```text
post_event_review
```

no puede usarse como feature del momento inicial.

Tu contrato ya bloquea esta fuga.

---

## 16.3 `strategy_state_table`

Esta tabla todavía te falta conceptualmente.

No debe guardar la decisión final, sino la geometría de una hipótesis.

Ejemplo breakout:

```text
strategy_family = breakout
break_level
distance_to_level
number_of_tests
compression_below_level
volume_between_tests
signed_flow_into_level
spread_at_level
```

Ejemplo pullback:

```text
pullback_depth
pullback_duration
retracement_fraction
sell_flow_decay
bid_stability
volume_contraction
```

La misma `market_state` puede producir varios `strategy_state`.

---

## 16.4 `position_state_table`

Para decisiones secuenciales:

```text
position_side
shares
average_entry
time_in_trade
unrealized_pnl
MFE_so_far
MAE_so_far
distance_to_stop
distance_to_target
current_tape
current_spread
current_liquidity
```

Es esencial para:

```text
mantener
añadir
reducir
salir
```

---

## 16.5 `execution_state_table`

Debe separar alpha de ejecutabilidad:

```text
current_spread
quote_age
bid_size
ask_size
recent_executed_volume
recent_signed_flow
quote_stability
latency_regime
expected_slippage
fill_probability_proxy
halt_risk
SSR
borrow availability
```

Sin esto, puedes encontrar predicción de precio que no produzca beneficio realizable.

---

# 17. Qué no debe entrar en las tablas de estado

Tu contrato actual prohíbe correctamente:

```text
outcome__*
label__*
reward__*
action__*
policy__*
fill__*
pnl__*
future__*
strategy__*
signal__*
```

Haría un matiz:

```text
strategy_state
```

puede existir como tabla independiente, pero no debe introducir:

```text
strategy_decision
entry_signal
action recomendada
```

Puede describir la geometría de una estrategia sin contener la respuesta.

---

# 18. Outcomes que debes separar

## Price outcomes

```text
return_100ms
return_500ms
return_1s
return_2s
return_5s
return_10s
return_30s
return_60s
return_5m
return_15m
return_30m
```

## Path outcomes

```text
MFE
MAE
time_to_MFE
time_to_MAE
drawdown_before_target
runup_before_stop
future_path_efficiency
```

## Microstructure outcomes

```text
future_mid_move
future_spread
future_top_depth
future_OFI
price_impact_after_burst
realized_spread
quote_response_latency
depth_recovery_time
```

## Event outcomes

```text
HOD_break
breakout_failure
VWAP_hold
VWAP_loss
halt
second_halt
extension_1pct
extension_3pct
```

## Execution outcomes

```text
fill
partial_fill
time_to_fill
slippage
adverse_selection
realized_execution_cost
```

---

# 19. Horizonte y relevancia de las features

## Menos de 10 ms

Puedes investigarlo técnicamente gracias a timestamps y sequence en quotes.

Pero no lo trataría como una capa monetizable central porque faltan:

```text
MBO
queue position
latencia propia
routing
trade sequence
exchange-native feed completo
```

Útil principalmente para:

```text
quality
message structure
latency
alignment sensitivity
```

---

## 10–100 ms

Puedes estudiar:

```text
quote bursts
spread flicker
sequence dynamics
microprice
OFI
venue switches
```

Todavía con cautela de ejecución.

---

## 100 ms–1 s

Es un horizonte mucho más defendible para:

```text
tape acceleration
signed flow
OFI
spread compression
microprice displacement
depletion proxies
quote latency regimes
```

---

## 1–5 segundos

Probablemente una de tus mejores zonas para hiperscalping investigable.

Combina:

```text
trade intensity
signed flow
OFI
spread
top depth
microprice
venue state
price response
```

---

## 5–30 segundos

Horizonte fuerte para:

```text
breakout confirmation
failed breakout
VWAP reclaim
tape continuation
flow reversal
post-halt behavior
```

---

## 30 segundos–5 minutos

Probablemente el horizonte más robusto con el conjunto actual.

Combina:

```text
microestructura
OHLCV 1m
VWAP
HOD/LOD
event geometry
news
halts
short context
daily context
```

---

## 5–30 minutos

La microestructura sigue siendo útil como timing, pero pesan más:

```text
estructura intradía
VWAP
volumen acumulado
transaction-count trajectory
catalyst
float/shares
capital structure
regime
```

---

# 20. Lo que sigue sin ser científicamente defendible

Aunque la nueva data sea mejor, no puedes afirmar que tienes:

```text
MBP-10 histórico
MBO
order lifecycle
queue position
queue age
true cancel rate
true add rate
true order replenishment
full book slope
full book convexity
multi-level liquidity gaps
spoofing lifecycle
```

Tampoco puedes reconstruir diez niveles combinando:

```text
TradeStation
IBKR
L1 histórico
prints
```

Puedes crear proxies muy valiosos, pero no fabricar observaciones que nunca existieron.

---

# 21. Qué debe ocurrir con tu tabla 015

La `015_microstructure_features_table` actual contiene principalmente:

```text
calidad
cobertura
spread básico
top depth
volumen
odd lots
tamaño de trades
```

No la eliminaría.

La convertiría en un sistema con dos niveles.

## `015A_microstructure_window_features_core`

Features gobernadas y relativamente estables:

```text
trade intensity
spread
top depth
imbalance
microprice
signed flow
OFI
trade-size distribution
quote update rate
```

## `015B_microstructure_research_features`

Features experimentales:

```text
burst detection
venue transitions
latency regimes
apparent replenishment
liquidity vacuum
flow-response nonlinearities
entropy families
multi-scale interactions
```

Así evitas que cada experimento modifique el core.

---

# 22. Tablas nuevas que añadiría

```text
019_trade_event_primitives_table
020_quote_event_primitives_table
021_trade_quote_alignment_table
022_microstructure_episode_table
023_microstructure_feature_registry
024_intraday_feature_table
025_daily_feature_table
026_strategy_state_table
027_position_state_table
028_execution_state_table
029_execution_outcomes_table
```

Los números son orientativos. La separación conceptual es lo importante.

---

# 23. Feature registry obligatorio

Cada feature debe declarar:

```text
feature_name
feature_family
description
mathematical_formula
physical_interpretation
statistical_interpretation
units
raw_inputs
eligibility_policy
window
minimum_observations
timestamp_semantics
sequence_policy
alignment_policy
normalization
null_policy
quality_gate
future_dependent
allowed_in_market_state
allowed_in_event_state
version
tests
```

Ejemplo:

```text
feature_name:
microstructure__ofi_normalized_1s

formula:
sum(L1 order-flow contributions in (t-1s, t])
/
mean top depth in (t-1s, t]

inputs:
bid_price
bid_size
ask_price
ask_size
participant_timestamp
sequence_number

future_dependent:
false

allowed_in_market_state:
true
```

---

# 24. Cómo generar la máxima cantidad sin destruir la ciencia

No crear features manualmente una por una.

Usaría una gramática controlada.

## Primitivas

```text
trade count
share volume
dollar volume
trade size
intertrade duration
return
spread
depth
imbalance
microprice
OFI
latency
quote count
```

## Estadísticos

```text
sum
mean
median
std
CV
min
max
quantiles
skewness
kurtosis
entropy
autocorrelation
```

## Transformaciones temporales

```text
level
change
slope
acceleration
jerk
short/long ratio
log-ratio
z-score
percentile
```

## Ventanas

```text
100ms
250ms
500ms
1s
2s
5s
10s
30s
60s
5m
```

## Normalizaciones

```text
per second
per trade
per share
per dollar
per unit of depth
relative to ticker history
relative to time of day
relative to regime
```

Esto puede producir miles de candidatos, pero todos tienen trazabilidad matemática.

---

# 25. Prioridad real recomendada

## Fase 1 — integridad y primitivas

```text
decode trade conditions
decode quote conditions/indicators
validate timestamp units
validate sequence behavior
build trade primitives
build quote primitives
```

## Fase 2 — trade-quote alignment

```text
participant-time alignment
feed-time alignment
lag sensitivity
classification confidence
```

## Fase 3 — microstructure core

```text
trade intensity
intertrade durations
spread
top depth
imbalance
microprice
quote rate
signed flow
OFI
tape acceleration
```

## Fase 4 — episodios

```text
bursts
stalls
flow flips
spread collapse
depletion
apparent replenishment
venue switches
latency spikes
```

## Fase 5 — no microestructura

```text
1m transaction-count features
VWAP geometry
HOD/LOD geometry
daily context
identity
halts
short
corporate actions
regime
news/fundamentals
```

## Fase 6 — states y execution

```text
market_state
event_state
strategy_state
position_state
execution_state
```

---

# Veredicto final revisado

Con la nueva documentación, tu data es más potente de lo que habíamos concluido inicialmente.

## Lo que tienes realmente

```text
trades event-level con timestamp microsegundo
quotes L1 event-level con:
    participant timestamp
    feed timestamp
    sequence number
    bid/ask exchange
    tape
    conditions
    indicators

daily y 1m con:
    OHLCV
    VWAP
    transaction count

price views:
    raw
    split-normalized
    adjusted
    adjusted proxy
    quote-guarded

identidad:
    CIK
    FIGI
    exchange
    temporal validity

halts:
    halt
    resume quote
    resume trade

short interest:
    short interest
    average volume
    days to cover
```

## Qué implica

Puedes construir científicamente una representación muy rica de:

```text
tape
flujo ejecutado
dinámica del BBO
secuenciación de quotes
latencia del feed
venue behavior
spread
top depth
imbalance
microprice
OFI
agresión aproximada
depletion/replenishment proxies
geometría intradía
calidad y comparabilidad de precios
halts
short context
```

## Qué sigue faltando

```text
profundidad multinivel
órdenes individuales
colas
lifecycle
cancel/add exacto
MBO
```

La conclusión arquitectónica definitiva es:

> No debes intentar construir una única tabla gigantesca con todos los atributos. Debes construir un sistema de feature tables especializadas, gobernadas por un feature registry, que alimenten varias tablas de estado según el tipo de decisión.

La relación correcta es:

```text
raw events
    ↓
eligible primitives
    ↓
feature tables
    ↓
market/event/strategy/execution states
    ↓
decisions
    ↓
outcomes
```

Y la conclusión científica más importante es:

> Con tus trades y quotes actuales no puedes recrear MBO ni MBP-10, pero sí puedes construir una capa L1 event-level considerablemente más profunda y defendible de lo que creíamos, incluyendo secuencia, latencia, venue, microprice, OFI, agresión, aceleración y respuesta del BBO. Para scalping de segundos a minutos, esa capa puede ser suficientemente rica como para buscar edge serio antes de incorporar MBP-10 o MBO.
