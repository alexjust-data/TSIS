# EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003

Fecha: 2026-07-08
Estado: draft_operativo
Tipo: research experiment

## Objetivo

Este experimento nace para resolver el primer evento operativo de DAS:

```text
Como detectar en tiempo real el primer despertar/impulso limpio de una accion
muerta, antes de seguir estudiando first dip, rebreak, profit, stop o sizing.
```

El foco cambia respecto a 0001/0002:

```text
0001 = gramatica visual de first push, first dip, rebreak
0002 = denominador scanner y recuperacion/destruccion posterior
0003 = evento real-time de despertar/primer impulso, sin depender de velas como
       senal primaria
```

No se debe seguir trabajando en puntos visuales hasta que este experimento fije
una definicion medible de `DAS_IMPULSE_START` y determine que datos permiten
detectarlo sin mirar el futuro.

## Pregunta Central

```text
Podemos cazar el primer movimiento DAS de forma limpia usando datos real-time
sin velas, o solo podemos estudiarlo retrospectivamente con OHLCV 1m?
```

Subpreguntas:

- Que hacen los profesionales/HFT para detectar ese tipo de transicion?
- Que datos reales tenemos en TSIS para aproximarlo?
- Es suficiente el dataset actual para detectar el evento premarket?
- Si no es suficiente, que parte si se puede demostrar ahora?
- Que queda bloqueado hasta conseguir mas datos?

## Clon De La Respuesta Operativa Previa

Texto base que motiva este experimento:

```text
Si: ahora el problema real ya no son los puntos. Es definir un evento tradeable
en tiempo real. Y aqui hay una verdad incomoda: el first_push_high no se puede
"cazar" exactamente en vivo, porque solo sabes que fue el high del primer push
cuando ya empieza el dip. Por tanto, hay dos cosas distintas:

- Detectar el arranque del push: posible en tiempo real, pero con incertidumbre.
- Marcar first_push_high / first_dip_low: util para estudiar, clasificar y
  operar fases posteriores, pero parcialmente retrospectivo.

Como lo hacen los profesionales:

Los mas potentes no cazan esto con EMA8 o Donchian de 1m como senal principal.
Eso puede servir como vista agregada. En tiempo real usan:

1. Order flow imbalance / order book imbalance.
   La literatura de microestructura muestra que a horizontes cortos los
   movimientos vienen mas de desequilibrios de ordenes que de volumen OHLCV
   agregado.

2. Limit order book + trades agresores.
   Modelos modernos tipo DeepLOB usan estructura del libro de ordenes, no velas
   1m, para predecir movimientos de precio.

3. Filtros de ruido en flujo de ordenes.
   Mucho order book es falso/transitorio. Hay que separar cambios persistentes
   de ruido de cotizacion.

4. Regimenes, no senales aisladas.
   Los pros no dicen "EMA8 toca, compro". Dicen: hay regimen de expansion,
   liquidez entrando, presion compradora, spread aceptable, profundidad
   suficiente, volatilidad manejable y riesgo definido.

Con nuestra data 1m, no somos HFT. Pero si podemos construir un detector de
evento DAS serio.

Que significa cazar el primer movimiento:

No deberiamos buscar la vela perfecta. Debemos detectar transicion de estado:

DEAD / COMPRESSED
-> AWAKENING
-> IMPULSE_CANDIDATE
-> VALID_DAS_FIRST_PUSH
-> FIRST_DIP
-> DIP_RECOVERY / FAIL

El evento 1 no es first_push_high. El evento 1 real-time deberia ser:

DAS_IMPULSE_START_CONFIRMED

Eso ocurre cuando el ticker deja de estar muerto y empieza una expansion limpia.

Detector base que si tiene sentido:

dead_base_score:
- rango previo comprimido
- EMA8 plana o poco inclinada
- bajo volumen relativo previo
- pocas velas amplias
- poco avance neto

impulse_score:
- retorno en 2-5 velas
- velocidad %/min
- volumen relativo vs ultimas N velas
- dollar-volume
- closes cerca del high de vela
- precio por encima de EMA8
- pendiente EMA8 positiva
- distancia positiva a VWAP/EMA8
- avance neto / rango total alto

chop_penalty:
- demasiadas alternancias rojo/verde
- muchas cruces de EMA8
- mechas grandes sin cierre
- rango grande pero avance neto bajo
- volumen alto sin direccion

Si impulse_score - chop_penalty pasa umbral, hay patron. Si no pasa, se imprime
chart sin puntos y estado no_valid_das_impulse.

Donchian:
Si, Donchian puede ayudar, pero no como sistema completo. Sirve para decir:
rompe el high de las ultimas N velas. Pero en choppy stocks va a dar basura.
Debe ir combinado con compresion previa, volumen relativo, velocidad y
eficiencia direccional.

ML:
ML si, pero despues. Primero necesitamos labels buenos/malos de imagenes. Luego
entrenamos un clasificador/ranker:

input: features disponibles hasta minuto t
label: valid_das_push / bad_chop / no_punch / late_move
modelo inicial: logistic / random forest / xgboost
metrica: precision@topK, recall de buenos, false positive rate, EV neto con
slippage

Nada de usar futuro como feature. El futuro solo sirve para label/evaluacion.

Para profit:

Hay tres entradas distintas a investigar, no una:

A. impulse entry:
entra durante el arranque confirmado.
riesgo alto, mejor reward, mas slippage.

B. first dip recovery:
entra cuando el primer dip recupera.
mas limpio, llega tarde, stop bajo dip low.

C. rebreak:
entra al romper first_push_high.
mas confirmado, peor precio, menos falsos positivos.

Recomendacion: no intentar resolver profit todavia. Primero demostrar que
podemos detectar DAS_IMPULSE_START_CONFIRMED con alta precision. Despues se
prueba si A, B o C tiene edge.

Lo que debemos construir ahora es un DAS Event Detector v0, no otro renderer.
Mantiene todos los tickers, pero clasifica:

valid_das_impulse
no_valid_no_dead_base
no_valid_too_choppy
no_valid_too_slow
no_valid_no_volume_expansion
valid_impulse_but_failed_after_dip

Ese es el primer problema cientifico. Si lo resolvemos, los puntos salen solos.
```

## Fuentes De Investigacion Externa

Estas referencias no son reglas de trading; fijan el marco metodologico:

- Cont, Kukanov, Stoikov, "The Price Impact of Order Book Events":
  https://arxiv.org/abs/1011.6402
  - Lectura para TSIS: en horizontes cortos, order-flow imbalance en best bid/ask
    explica cambios de precio mejor que volumen agregado.
- Zhang, Zohren, Roberts, "DeepLOB":
  https://arxiv.org/abs/1808.03668
  - Lectura para TSIS: los modelos modernos de microestructura usan limit order
    book, no velas 1m, cuando buscan movimientos de alta frecuencia.
- Budish, Cramton, Shim, "The High-Frequency Trading Arms Race":
  https://academic.oup.com/qje/article/130/4/1547/1916146
  - Lectura para TSIS: la ventaja HFT real vive en diseno de mercado, latencia,
    libro continuo y microestructura, no en indicadores visuales lentos.
- FINRA / regulatory concept of momentum ignition:
  https://www.finra.org/rules-guidance/key-topics/algorithmic-trading
  - Lectura para TSIS: hay que separar deteccion legitima de impulso de practicas
    manipulativas como spoofing/layering/momentum ignition. Este experimento es
    de deteccion pasiva, no de inducir movimiento.

## Auditoria De Datos Disponibles

Lectura obligatoria realizada:

```text
E:/TSIS/data/README.md
```

Conclusiones de ese README:

- `E:/TSIS/data` es plano fisico, no autoridad semantica por si solo.
- La autoridad conceptual vive en contratos de `01_foundations`.
- Para intradia 1m, la raiz fisica canonica es `E:/TSIS/data/ohlcv_1m`.
- `quotes` es book observations raw/staged.
- `trades_ticks_prod_2005_2026` es raw/staged trades/tape production history.
- Las vistas derivadas, features y labels no deben confundirse con RAW.

### Fuentes Fisicas Relevantes

```text
E:/TSIS/data/quotes
E:/TSIS/data/quotes_
E:/TSIS/data/trades_ticks_prod_2005_2026
E:/TSIS/data/ohlcv_1m
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
E:/TSIS/data/data_foundation_outputs/microstructure_features_table
```

### Quotes

Contrato revisado:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/quotes/quotes_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/quotes_consumption_policy.md
```

Unidad logica:

```text
una observacion del libro bid/ask
```

Campos disponibles observados en ejemplos:

```text
ask_exchange
ask_price
ask_size
bid_exchange
bid_price
bid_size
conditions
indicators
participant_timestamp
sequence_number
timestamp
tape
trf_timestamp
year
month
day
```

Lectura:

- Si hay `bid_price`, `ask_price`, `bid_size`, `ask_size` y timestamp
  nanosegundo.
- Esto permite construir senales de estado de libro level-1 / top-of-book:
  mid, spread, imbalance bid/ask size, quote update rate, quote pressure,
  spread compression, best-bid/best-ask movement.
- No es libro profundo L2/L3.
- No contiene la cola completa por nivel, ni add/cancel por profundidad, ni
  prioridad de orden.

### Trades

Contrato revisado:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/trades/trades_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/trades_consumption_policy.md
```

Campos disponibles observados:

```text
ticker
date
timestamp
price
size
exchange
conditions
year
month
day
```

Lectura:

- Sirve para raw tape regular-session, execution research y microstructure
  feature engineering si pasa policy/quality gates.
- En los ejemplos DAS inspeccionados, el archivo `market.parquet` empieza a
  las 09:30 ET.
- Por tanto, no cubre el despertar premarket DAS en 04:00-09:30 para esos
  casos.

### Microstructure Features Table Existente

Policy revisada:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/microstructure_features_table_consumption_policy.md
```

Estado:

```text
materialization_scope = seed_event_window_smoke
full_universe_claim = false
execution_sim_candidate = false
backtest_core_microstructure_candidate = false
```

Lectura:

- No es feature store de produccion.
- No puede usarse como dataset principal de 0003.
- Si puede servir como referencia de forma/schema para una futura tabla de
  microestructura por ventanas de evento.

## Cobertura En Denominador 0002

Base medida:

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_worklist/anchor_worklist_from_denominator_v0_1.parquet
```

Filas:

```text
152 casos
130 tickers unicos
```

Cobertura day-exact medida:

```text
quotes official E:/TSIS/data/quotes       = 21 / 152
quotes recovered E:/TSIS/data/quotes_     = 129 / 152
quotes any                                = 150 / 152
trades regular-session market.parquet     = 95 / 152
quotes any + trades regular               = 95 / 152
quotes any only                           = 55 / 152
trades only                               = 0 / 152
neither quotes nor trades                 = 2 / 152
```

Casos sin quotes ni trades day-exact en el denominador 0002:

```text
NVVE 2026-03-09
SOAR 2026-03-09
```

Ejemplos inspeccionados:

```text
OPAD 2026-01-09
- quotes: 301337 rows
- quotes first/last ET: 04:00:00 - 19:59:58
- quotes rows 04:00-09:30: 150329
- trades: 284873 rows
- trades first/last ET: 09:30:00 - 15:59:59

AMOD 2026-01-07
- quotes: 106500 rows
- quotes first/last ET: 04:00:00 - 19:59:57
- quotes rows 04:00-09:30: 65336
- trades: 74984 rows
- trades first/last ET: 09:30:00 - 15:59:59

MSS 2025-09-29
- quotes: 511753 rows
- quotes first/last ET: 04:00:00 - 19:59:59
- quotes rows 04:00-09:30: 362390
- trades: 210101 rows
- trades first/last ET: 09:30:00 - 15:59:59
```

## Veredicto De Suficiencia

### Lo Que Si Tenemos

Tenemos suficiente para investigar un detector real-time `quote-driven` desde
04:00 ET para la mayoria de candidatos DAS:

```text
input primario = top-of-book quotes level-1
frecuencia = evento quote/timestamp, no vela OHLCV
cobertura denominador 0002 = 150/152 con quotes day-exact
```

Esto permite construir features sin velas:

```text
mid_price
spread_bps
bid_ask_size_imbalance
quote_update_rate
mid_return_5s_15s_30s_60s
best_bid_rise_rate
best_ask_rise_rate
spread_compression
spread_expansion
ask_size_depletion_proxy
bid_size_replenishment_proxy
top_of_book_donchian_breakout
quote_chop_penalty
quote_impulse_score
dead_quote_base_score
```

### Lo Que No Tenemos

No tenemos suficiente para replicar un detector profesional/HFT completo:

```text
no full L2/L3 depth
no full add/cancel/order queue by level
no order priority
no broker/routing/latency state
no premarket trades in trades_ticks_prod_2005_2026 market.parquet examples
no aggressor-side trade classification premarket from tape
no live execution simulator approved
```

Por tanto:

```text
No podemos demostrar todavia un detector HFT completo de order-flow imbalance
como lo haria una firma con full depth + prints premarket + routing.

Si podemos demostrar un detector TSIS real-time quote-state / top-of-book para
detectar despertar DAS sin usar velas como input primario.
```

### Punto Critico Sobre 03:30

Las quotes inspeccionadas empiezan a las 04:00 ET, no a las 03:30 ET.

Lectura:

- Para 04:00-09:30, quotes son muy utiles.
- Para 03:30-04:00, el dataset actual no demostro cobertura en ejemplos
  inspeccionados.
- Si el sistema debe operar desde 03:30, hay que confirmar otro feed o aceptar
  que 0003 empieza a 04:00 para el detector quote-driven.

## Definicion Del Evento 0003

No usar `first_push_high` como evento real-time primario.

Evento primario:

```text
DAS_IMPULSE_START_CANDIDATE
```

Confirmacion:

```text
DAS_IMPULSE_START_CONFIRMED
```

Estados propuestos:

```text
DEAD_OR_COMPRESSED
AWAKENING_CANDIDATE
IMPULSE_CANDIDATE
VALID_DAS_IMPULSE
NO_VALID_DAS_IMPULSE_NO_DEAD_BASE
NO_VALID_DAS_IMPULSE_TOO_CHOPPY
NO_VALID_DAS_IMPULSE_TOO_SLOW
NO_VALID_DAS_IMPULSE_NO_LIQUIDITY_CONFIRMATION
NO_VALID_DAS_IMPULSE_SPREAD_TOO_UNSTABLE
AMBIGUOUS_MANUAL_REVIEW
```

## Detector V0 Propuesto

Entrada:

```text
quotes level-1, 04:00-10:00 ET
```

No inputs:

```text
no OHLCV 1m como senal primaria
no future high
no first dip futuro
no rebreak futuro
no labels ni outcomes como features
```

Ventanas rolling:

```text
5s
15s
30s
60s
120s
```

Bloques de features:

### Dead Base

```text
mid_range_bps_prev_5m
mid_net_return_bps_prev_5m
spread_median_bps_prev_5m
quote_update_rate_prev_5m
top_of_book_chop_prev_5m
```

### Awakening

```text
mid_breaks_prev_N_second_high
best_bid_breaks_prev_N_second_high
spread_compresses_vs_prev_5m
quote_update_rate_accelerates
bid_size_imbalance_turns_positive
ask_size_available_not_exploding
```

### Impulse

```text
mid_return_bps_15s_30s_60s
best_bid_return_bps_15s_30s_60s
monotonic_mid_steps_ratio
positive_bid_updates_ratio
spread_stability_during_move
depth_or_size_support_proxy
```

### Chop Penalty

```text
mid_reversal_count
bid_ask_crossed_or_zero_artifact_rate
spread_instability
quote_direction_flip_rate
large_mid_range_low_net_return
```

Score inicial:

```text
das_quote_impulse_score =
  dead_base_score
+ awakening_score
+ impulse_score
- chop_penalty
- spread_risk_penalty
```

Salida:

```text
emitir evento si score >= threshold
si no, preservar caso como no_valid_* con reason codes
```

## Donchian En 0003

Donchian si, pero sobre `mid_price` o `best_bid`, no sobre velas 1m.

Uso correcto:

```text
top_of_book_donchian_breakout =
mid_price rompe max(mid_price) de los ultimos N segundos
```

No debe ser regla unica.

Debe ir condicionada por:

```text
dead_base_score alto
spread aceptable
quote_update_rate acelerando
chop_penalty bajo
```

## ML En 0003

ML se permite como ranking/clasificacion despues de construir labels humanos.

Primer modelo recomendado:

```text
logistic regression / random forest / xgboost
```

No empezar con deep learning.

Motivo:

```text
El problema principal no es capacidad del modelo.
El problema principal es definicion correcta de evento, labels, leakage y
features as-of.
```

Labels:

```text
valid_das_impulse
bad_chop
no_punch
late_move
ambiguous_review
```

Metricas:

```text
precision_at_top_k
recall_valid_das_impulse
false_positive_rate_on_chop
lead_time_vs_1m_scanner
lead_time_vs_manual_awaken_start
post_signal_MFE_MAE_as_diagnostic_only
```

## Regla Antisesgo

No eliminar tickers malos del denominador.

Regla:

```text
todos los candidatos permanecen en la tabla
el detector emite estado y reason codes
solo los estados validos entran a estudios de operabilidad
```

Esto evita confundir filtro de calidad con supervivencia visual.

## No-Gos

No permitido en 0003:

- marcar first_push_high en todos los casos por obligacion visual;
- usar el +50% scanner como ancla conceptual del push;
- usar OHLCV 1m como input primario si el objetivo declarado es "sin velas";
- entrenar ML con features posteriores al evento;
- medir profit antes de validar el evento;
- presentar quotes level-1 como equivalente a full order book HFT;
- usar trades regular-session para inferir premarket execution flow.

## Output Esperado Del Experimento

Primera entrega:

```text
das_realtime_quote_event_candidates_v0_1.parquet
das_realtime_quote_event_candidates_v0_1.csv
das_realtime_quote_event_summary_v0_1.md
visual_quote_event_audit_png_v0_1/
```

Tabla minima:

```text
candidate_id
ticker
session_date
event_state
event_ts_utc
event_ts_et
event_price_mid
event_price_bid
event_price_ask
score_total
dead_base_score
awakening_score
impulse_score
chop_penalty
spread_risk_penalty
reason_codes
source_quotes_file
quotes_root_used
quotes_root_state
quotes_rows_in_window
first_available_quote_ts_et
last_available_quote_ts_et
asof_feature_cutoff_ts_utc
leakage_guard_pass
```

## Decision Actual

El experimento 0003 queda abierto con esta decision:

```text
TSIS tiene datos suficientes para investigar una version quote-driven,
top-of-book, real-time y sin velas del evento DAS_IMPULSE_START desde 04:00 ET
en la mayoria de candidatos.

TSIS no tiene, con lo auditado aqui, datos suficientes para afirmar que puede
replicar una estrategia HFT profesional completa de order-flow imbalance,
porque faltan full depth, cancel/add queue, premarket trades y execution/routing
state.
```

Siguiente trabajo:

```text
1. Construir el state table quote-driven para ventanas 04:00-10:00.
2. Probarlo contra casos humanos buenos/malos.
3. Medir si anticipa o discrimina el despertar DAS antes que OHLCV 1m.
4. Solo despues volver a first dip, rebreak, profit y riesgo.
```

## Addendum 2026-07-08 - Data Exacta Requerida

Esta seccion prevalece sobre cualquier frase anterior demasiado amplia. La
separacion correcta es:

```text
Historico auditado en E:/TSIS/data:
- quotes/top-of-book desde 04:00 en la mayoria de casos 0002
- trades historicos observados desde 09:30 en ejemplos inspeccionados
- no L3 certificado
- no full historical L2 certificado en E:/TSIS/data

Live DAS CMD API:
- Time & Sales disponible con SB <SYMBOL> tms, data_family=tms
- Level 2 disponible con SB <SYMBOL> Lv2, data_family=lv2
- L3 no certificado/no soportado en v0 salvo comando explicito en manual
```

Por tanto, 0003 debe trabajar con dos carriles:

```text
carril_historico = replay parcial con quotes/top-of-book y 1m como auditoria
carril_live = detector real con DAS events.jsonl tms + lv2
```

### 1. Datos De Universo, Identidad Y Referencia

Obligatorio por simbolo/dia:

```text
symbol
session_date
candidate_id
denominator_universe_id
prior_close usado por scanner
reference_price_source
split_adjustment_state_asof
ticker_continuity_state_asof
halt_status_asof
halt_timestamps_asof
trading_calendar
session_boundaries
feed_entitlement_state
data_source_version
```

Util pero no obligatorio en v0:

```text
float_asof
market_cap_asof
sector/industry
shortability/locate_state
SSR_state
news/catalyst_tags_asof
```

Regla:

```text
Si un campo no puede probarse as-of, no entra como feature. Puede quedar como
contexto o label auxiliar, pero no como input del detector.
```

### 2. Scanner, Denominador Y Suscripcion

Obligatorio:

```text
scanner_run_id
scanner_trigger_ts_utc
scanner_trigger_ts_et
scanner_trigger_price
scanner_trigger_reason
scanner_filters_passed
scanner_raw_payload si existe
watchlist_insert_ts_utc
subscription_requested_ts_utc
subscription_started_ts_utc
subscription_priority_rank
subscription_reason
subscription_denied_reason si aplica
not_subscribed_reason si aplica
```

Motivo:

```text
No queremos sesgo visual. Hay que conservar tambien los simbolos malos,
choppy, sin punch, sin datos o no suscritos.
```

### 3. Time And Sales Live DAS (`tms`)

Contrato v0:

```text
source = DAS_CMD_API
command = SB <SYMBOL> tms
data_family = tms
sink = events.jsonl
```

Campos obligatorios por evento:

```text
raw_payload
capture_ts_utc
source_ts_utc/source_ts_et si DAS lo entrega
symbol
price
size
exchange/venue si viene
condition_codes si vienen
sequence_number si viene
session_flag inferido: premarket/regular/afterhours
subscription_id
parser_version
quality_state
```

Deseable:

```text
trade_side si DAS lo entrega
aggressor_side_inferred si no lo entrega
aggressor_side_confidence
matched_quote_ts_utc usado para inferir side
latency_ms = capture_ts - source_ts si ambos existen
```

Regla:

```text
No basta con OHLCV ni con barras agregadas. Para cazar el despertar hacen falta
prints crudos, timestamp de recepcion y raw payload preservado.
```

### 4. Level 2 Live DAS (`Lv2`)

Contrato v0:

```text
source = DAS_CMD_API
command = SB <SYMBOL> Lv2
data_family = lv2
sink = events.jsonl
```

Campos obligatorios por evento:

```text
raw_payload
capture_ts_utc
source_ts_utc/source_ts_et si DAS lo entrega
symbol
side = bid/ask
level/rank si viene estructurado
price
size
market_maker/participant/venue si viene
operation/update_type si existe: snapshot/update/delete/replace
sequence_number si existe
snapshot_complete flag si puede inferirse
subscription_id
parser_version
quality_state
```

Features que requieren Lv2:

```text
depth_imbalance_by_levels
ask_liquidity_depletion
bid_replenishment
depth_weighted_mid
microprice
spread_stability
quote_update_velocity_by_level
liquidity_wall_distance
liquidity_pull_or_refresh_proxy
```

Restriccion practica:

```text
DAS suele limitar Lv2 a menos simbolos que Lv1/T&S. 0003 debe priorizar
simbolos y guardar explicitamente no_response/error/not_entitled/subscription_denied.
No se puede eliminar silenciosamente un ticker porque fallo la suscripcion.
```

### 5. L3 / Market-By-Order

Estado v0:

```text
L3 = no certificado / no soportado.
```

Regla:

```text
Solo se anade L3 al contrato si el manual local de DAS contiene un comando
explicito, el parser lo soporta y el comando entra en allowlist. Mientras tanto,
no se puede afirmar que TSIS tiene L3.
```

### 6. Top-Of-Book / Lv1

Puede derivarse de Lv2, de feed Lv1 o de quotes historicas.

Obligatorio por timestamp/evento:

```text
best_bid_price
best_bid_size
best_ask_price
best_ask_size
mid_price
spread_abs
spread_bps
quote_ts_utc
capture_ts_utc
source
quality_state
```

Uso en 0003:

```text
mid_return_5s_15s_30s_60s
best_bid_rise_rate
best_ask_rise_rate
spread_compression_or_expansion
bid_ask_size_imbalance
quote_update_rate
quote_chop_penalty
top_of_book_donchian_breakout
```

### 7. Calidad De Captura Y Runtime

Obligatorio por run y por simbolo:

```text
capture_run_id
process_id
machine_id
clock_sync_state
capture_start_ts_utc
capture_end_ts_utc
subscription_start_ts_utc
subscription_end_ts_utc
disconnect_events
reconnect_events
no_response_events
parser_errors
out_of_order_count
duplicate_count
gap_detected
raw_events_per_second
buffer_overflow_or_dropped_event_flag si existe
```

Regla:

```text
El detector debe distinguir entre no_hay_patron y no_tengo_datos_suficientes.
```

### 8. Labels Humanos

Obligatorio para entrenar/discriminar buenos y malos:

```text
label_case_id
symbol
session_date
labeler_id
label_version
valid_das_impulse = true/false/ambiguous
bad_chop = true/false
no_punch = true/false
late_move = true/false
manual_impulse_start_ts_et si se marca
manual_first_push_high_ts_et si se marca
manual_first_dip_low_ts_et si se marca
label_confidence
label_notes
image_source_path
```

Regla anti-leakage:

```text
Los labels humanos nunca son features. Sirven para entrenar/evaluar.
```

### 9. Outcomes Para Evaluacion

Obligatorio despues del evento, pero nunca como feature:

```text
forward_mfe_30s_60s_120s_300s
forward_mae_30s_60s_120s_300s
time_to_first_dip_detected
time_to_rebreak
time_to_fail
destruction_state
regular_open_outcome
slippage_diagnostic si hay simulacion
```

Regla:

```text
Los outcomes miden utilidad posterior. No pueden participar en el score que
decide DAS_IMPULSE_START_CONFIRMED.
```

### 10. Relacion Con Tablas De Estado Existentes

Tabla revisada:

```text
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/runs/das_scanner_appearance_20260628T114046Z/state_tables/das_candidate_state_table_experimental_v0_1.parquet
```

Resumen observado:

```text
rows = 679
das__state = rebreak_confirmed en 679/679
quality__row_state = candidate_event en 679/679
```

Variantes:

```text
green_wick_reactivation = 329
vwap_dip_reclaim = 223
A_plus_continuation = 66
early_red_high_break = 58
unclear = 3
```

Columnas utiles para 0003 como contexto/labels retrospectivos:

```text
scanner__trigger_ts
scanner__trigger_price
scanner__trigger_volume
premarket__first_liquid_bar_ts
frontside__momentum_trigger_ts
frontside__first_push_start_ts
frontside__first_push_high_ts
frontside__first_dip_low_ts
frontside__rebreak_ts
das__state
das__variant
das__pattern_family
quality__*
```

Columnas prohibidas como features:

```text
human_label__*
outcome__*
```

Lectura:

```text
La tabla de estado existente es util como mapa retrospectivo y contrato de
nombres, pero no es suficiente como feature table live de 0003. Esta condicionada
al detector anterior y los 679 casos inspeccionados son rebreak_confirmed. Para
0003 faltan negativos reales: scanner_only, no_push, bad_chop, too_slow,
no_liquidity, failed_subscription, no_data.
```

Nueva tabla requerida:

```text
das_realtime_impulse_event_state_v0_1
```

Namespaces propuestos:

```text
identity__*
source__*
subscription__*
tms__*
lv2__*
topofbook__*
event__*
score__*
quality__*
label__*
outcome__*
```

### 11. Veredicto Actualizado

Con historico solamente:

```text
Podemos demostrar un detector top-of-book real-time-like desde 04:00 ET para la
mayoria de candidatos del denominador 0002. No podemos demostrar un sistema HFT
completo porque falta full historical L2/L3, prints premarket certificados y
estado de ejecucion/routing.
```

Con live DAS CMD API:

```text
Tenemos data suficiente para construir el detector real v1 si capturamos tms y
Lv2 en events.jsonl con raw payload, timestamps, subscription state, errores,
calidad y clock/latency state.
```

El minimo viable de 0003 no es otro renderer. Es esta tabla:

```text
das_realtime_impulse_event_state_v0_1.parquet
```

Con una fila por simbolo/evento/candidato y estos campos minimos:

```text
candidate_id
ticker
session_date
capture_run_id
denominator_universe_id
scanner_run_id
scanner_trigger_ts_utc
scanner_trigger_price
subscription_state_tms
subscription_state_lv2
event_state
event_ts_utc
event_ts_et
event_price_mid
event_price_bid
event_price_ask
score_total
dead_base_score
awakening_score
impulse_score
chop_penalty
spread_risk_penalty
tms_events_in_window
tms_buy_pressure_proxy
lv2_events_in_window
lv2_depth_imbalance
topofbook_quote_events_in_window
reason_codes
source_events_jsonl
source_quotes_file si se usa replay historico
first_available_event_ts_et
last_available_event_ts_et
asof_feature_cutoff_ts_utc
capture_quality_state
leakage_guard_pass
```

Decision:

```text
0003 puede avanzar si y solo si tratamos tms/Lv2 live como el contrato principal,
quotes historicas como replay parcial, labels humanos como target, outcomes como
evaluacion y tablas de estado anteriores como contexto retrospectivo no-feature.
```
