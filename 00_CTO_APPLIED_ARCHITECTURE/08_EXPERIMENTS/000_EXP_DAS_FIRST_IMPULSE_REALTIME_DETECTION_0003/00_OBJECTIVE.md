# Objetivo

```
¿Qué cambios observables en tape, libro y velocidad distinguen   
el despertar real de una microcap muerta frente a un falso arranque? y, 
¿permiten entrar antes de que el movimiento esté demasiado extendido?
```` 

1. [¿Qué debe responder el modelo?](#qué-debe-responder-el-modelo)  
    1.1 [Estado A: DEAD_BASE](#estado-a-dead_base)  
    1.2 [Estado B: AWAKENING](#estado-b-awakening)  
    1.3 [Estado C: IMPULSE_CONFIRMED](#estado-c-impulse_confirmed)  
    1.4 [Estado D: EXHAUSTION_OR_FAILURE](#estado-d-exhaustion_or_failure)  

2. [Aproximacion a sus variables estructurales](#aproximacion-a-sus-variables-estructurales)  
    2.1 [Grupo 1. Activación del tape](#grupo-1-activación-del-tape)  
    2.2 [Grupo 2. Dirección de la agresión](#grupo-2-dirección-de-la-agresión)  
    2.3 [Grupo 3. Consumo y reposición de liquidez](#grupo-3-consumo-y-reposición-de-liquidez)  
    2.4 [Grupo 4. Queue dynamics](#grupo-4-queue-dynamics)  
    2.5 [Grupo 5. Forma del libro](#grupo-5-forma-del-libro)  

3. [Spread y operabilidad](#spread-y-operabilidad)  

4. [Respuesta del precio al order flow](#respuesta-del-precio-al-order-flow)  
    4.1 [Alta agresión + alto avance](#alta-agresión--alto-avance)  
    4.2 [Alta agresión + poco avance](#alta-agresión--poco-avance)  
    4.3 [Poca agresión + gran avance](#poca-agresión--gran-avance)  

5. [Absorción](#absorción)  
    5.1 [Absorción vendedora](#absorción-vendedora)  
    5.2 [Absorción compradora](#absorción-compradora)  

6. [Velocidad y aceleración](#velocidad-y-aceleración)  
    6.1 [Velocidad del tape](#velocidad-del-tape)  
    6.2 [Velocidad del precio](#velocidad-del-precio)  
    6.3 [Velocidad del book](#velocidad-del-book)  
    6.4 [Aceleraciones](#aceleraciones)  

7. [Variables de transición desde acción muerta](#variables-de-transición-desde-acción-muerta)  
    7.1 [Baseline dinámico](#baseline-dinámico)  
    7.2 [Ratios](#ratios)  
    7.3 [Score de despertar](#score-de-despertar)  

8. [Variables para saber si se llega tarde](#variables-para-saber-si-se-llega-tarde)  

9. [¿Qué datos raw descargar?](#qué-datos-raw-descargar)  
    9.1 [A. Raw obligatorio](#a-raw-obligatorio)  
    9.2 [B. Raw deseable](#b-raw-deseable)  
    9.3 [C. Derivados](#c-derivados)  
    9.4 [D. Labels/outcomes](#d-labelsoutcomes)  

10. [¿Qué resolución temporal usar?](#qué-resolución-temporal-usar)  
    10.1 [Event store raw](#event-store-raw)  
    10.2 [State tables](#state-tables)  

11. [¿Qué ventana histórica descargar alrededor del evento?](#qué-ventana-histórica-descargar-alrededor-del-evento)  

12. [¿Qué hipótesis concretas probaría primero?](#qué-hipótesis-concretas-probaría-primero)  
    12.1 [H1. Aceleración del tape](#h1-aceleración-del-tape)  
    12.2 [H2. Agresión + respuesta](#h2-agresión--respuesta)  
    12.3 [H3. Consumo y reposición](#h3-consumo-y-reposición)  
    12.4 [H4. Persistencia](#h4-persistencia)  
    12.5 [H5. Extensión y fallo](#h5-extensión-y-fallo)  

13. [La arquitectura de datos propuesta](#la-arquitectura-de-datos-propuesta)  

14. [Decisión importante sobre el proveedor](#decisión-importante-sobre-el-proveedor)  

15. [Conclusión](#conclusión)  

![alt text](0003_SONN_2025-07-14_push476.62_rebreak_03_event_day_premarket_detail.png)

## ¿Qué debe responder el modelo?

```
1. ¿La acción ha dejado realmente de estar dormida?
2. ¿Existe presión compradora real o solo prints aislados?
3. ¿La liquidez del ask está siendo consumida?
4. ¿El bid se repone detrás del movimiento?
5. ¿El spread permite entrar?
6. ¿El movimiento sigue siendo temprano?
7. ¿El riesgo de fallo inmediato es aceptable?
8. ¿Existe suficiente recorrido antes de una extensión extrema?
```

### Estado A: `DEAD_BASE`

La acción está dormida.  
Características esperadas:
```
pocos trades por segundo
poco volumen por segundo
pocas actualizaciones de quotes
spread relativamente estable
escasa profundidad
precio casi inmóvil
OFI cercano a cero
sin persistencia compradora
```

Este estado es esencial porque el modelo necesita aprender la transición desde inactividad.  
No basta con entrenar solo sobre los segundos del push.  

### Estado B: `AWAKENING`

Empieza a ocurrir algo, pero todavía no sabemos si será un movimiento válido.  
Señales posibles:
```
aumento súbito de trades por segundo
aumento de volumen por segundo
más compradores agresores
best ask cambia más rápido
best bid empieza a subir
el spread se comprime o se mantiene controlado
aumenta el ritmo de mensajes MBO
aparecen cancelaciones en el ask
se reduce la profundidad cercana del ask
```

Aquí estará probablemente la señal de entrada más temprana.

### Estado C: `IMPULSE_CONFIRMED`

El movimiento ya muestra estructura direccional.
Señales:
```
agresión compradora persistente
consumo repetido del ask
reposición del bid
subida del microprice
OFI positivo persistente
precio responde al volumen comprador
pocas regresiones profundas
spread todavía operable
break de niveles acompañado de prints
```
Este es el punto donde el sistema puede decidir entrar.

### Estado D: `EXHAUSTION_OR_FAILURE`

El push pierde calidad o entra en peligro.  
Señales:
```
mucho volumen sin avance
ask se repone continuamente
baja la respuesta del precio a la agresión
aumentan cancelaciones del bid
el bid deja de subir
spread se amplía
aparecen ventas agresoras grandes
el microprice deja de liderar
aumenta el chop
```
Esto puede utilizarse tanto para evitar entrar tarde como para salir.

## Aproximacion a sus variables estructurales



### Grupo 1. Activación del tape**

Estas variables responden:

```
¿La acción está despertando realmente?
```

Raw necesario

```text
trade timestamp
trade price
trade size
trade venue
trade condition
sequence number
```

Features derivadas

```text
trades_per_100ms
trades_per_250ms
trades_per_1s
trades_per_5s

shares_traded_100ms
shares_traded_1s
shares_traded_5s

dollar_volume_1s
dollar_volume_5s

trade_rate_acceleration
volume_rate_acceleration

median_trade_size
mean_trade_size
max_trade_size
trade_size_percentiles

unique_trade_prices_1s
price_levels_crossed_1s
```

Variables especialmente importantes

```text
trade_rate_ratio_vs_baseline
volume_rate_ratio_vs_baseline
```

Ejemplo:

```text
trades_per_second_actual
/
mediana de trades por segundo de los 5 minutos anteriores
```

Eso captura matemáticamente el paso:

```text
muerta → despierta
```

Tu documento ya identifica que Time & Sales debe ser P0 porque el despertar debería mostrar aceleración de prints y continuidad, no solo quotes. 


### Grupo 2. Dirección de la agresión

Volumen no equivale a presión compradora.

Necesitas separar:

```text
compradores levantando ask
vendedores golpeando bid
trades indeterminados
```

Features

```text
buy_aggressive_volume_1s
sell_aggressive_volume_1s

buy_trade_count_1s
sell_trade_count_1s

aggressor_volume_imbalance_1s
aggressor_volume_imbalance_5s

buy_aggression_persistence
sell_aggression_persistence

consecutive_buy_aggressor_runs
consecutive_sell_aggressor_runs
```

Ejemplo:

```text
aggressor_imbalance =
(buy_aggressive_volume - sell_aggressive_volume)
/
(buy_aggressive_volume + sell_aggressive_volume)
```

Pero no usaría una sola ventana.

Calcularía:

```text
100 ms
250 ms
1 s
3 s
5 s
10 s
```

Porque una señal de hiperscalping puede existir a 250 ms y desaparecer en la agregación de un segundo.

El Documento 2 señala correctamente que el aggressor side es imprescindible porque un volumen alto puede corresponder a distribución, no a demanda real. 


### Grupo 3. Consumo y reposición de liquidez

Esta parte es la que más justifica MBO.

La pregunta es:

```
¿Los compradores están atravesando la oferta o simplemente están negociando dentro de un libro que se repone continuamente?
```

Ask depletion

```text
ask_size_removed_by_execution
ask_size_removed_by_cancel
ask_levels_consumed
time_to_consume_best_ask
best_ask_turnover_rate
```

Bid replenishment

```text
bid_add_volume_after_uptick
bid_replenishment_after_trade
bid_queue_recovery_time
bid_depth_growth_after_break
```

Ask replenishment

```text
ask_replenishment_after_execution
same_price_ask_reload_count
ask_queue_regeneration_speed
```

Variables clave

```text
ask_depletion_ratio
bid_replenishment_ratio
ask_reload_ratio
```

Ejemplo conceptual:

```text
ask_depletion_ratio =
executed_ask_volume
/
visible_ask_volume_before_execution
```

Y:

```text
bid_replenishment_ratio =
new_bid_size_added_after_uptick
/
bid_size_consumed_or_removed
```

Un push sano suele parecerse más a:

```text
consume ask
+
bid follows
+
new bids appear higher
```

Un falso push puede parecerse a:

```text
prints verdes
+
ask replenishes endlessly
+
bid does not follow
```

Tu catálogo describe precisamente MBO como el medio para observar add, cancel, modify y execute por orden individual, y diferenciar liquidez retirada de liquidez ejecutada. 


### Grupo 4. Queue dynamics

Esta es una de las ventajas reales de MBO frente a MBP-10.

Features

```text
order_count_bid_l1
order_count_ask_l1

mean_order_size_bid_l1
mean_order_size_ask_l1

median_order_lifetime_bid
median_order_lifetime_ask

cancel_rate_bid
cancel_rate_ask

add_rate_bid
add_rate_ask

modify_rate_bid
modify_rate_ask

queue_turnover_bid
queue_turnover_ask

queue_survival_probability
queue_age_distribution
```

Variables que pueden ser muy valiosas

```text
short_lived_ask_orders_ratio
short_lived_bid_orders_ratio
```

Esto puede ayudar a detectar liquidez poco comprometida.

También:

```text
persistent_bid_orders
persistent_ask_orders
```

Una hipótesis útil sería:

```
Los mejores primeros pushes están precedidos por aumento de agresión compradora y reducción de persistencia de las órdenes en el ask, mientras aumenta la persistencia o reposición del bid.
```

No asumiría que esto es verdad. Lo convertiría en una hipótesis medible.

### Grupo 5. Forma del libro

Aquí MBP-10 ya aporta mucho.

Features por nivel

Para los niveles `1–10`:

```text
bid_price_i
bid_size_i
bid_order_count_i

ask_price_i
ask_size_i
ask_order_count_i
```

Agregados

```text
depth_bid_1
depth_ask_1

depth_bid_3
depth_ask_3

depth_bid_5
depth_ask_5

depth_bid_10
depth_ask_10
```

Imbalances

```text
depth_imbalance_l1
depth_imbalance_l3
depth_imbalance_l5
depth_imbalance_l10
```

Geometría

```text
distance_to_next_bid_level
distance_to_next_ask_level

largest_bid_gap
largest_ask_gap

book_convexity_bid
book_convexity_ask

depth_concentration_bid
depth_concentration_ask
```

En microcaps es especialmente importante medir:

```text
liquidity_vacuum_above
```

Porque una acción puede subir violentamente no solo por gran demanda, sino porque encima hay muy poca oferta.

Eso no es necesariamente malo para el long, pero cambia la interpretación:

```text
pressure-driven move
vs
vacuum-driven move
```

## Spread y operabilidad

El modelo no puede considerar edge un movimiento imposible de ejecutar.

Features

```text
spread_absolute
spread_bps
spread_ticks

spread_mean_1s
spread_max_1s
spread_std_1s

spread_compression_rate
spread_expansion_rate

time_at_one_tick_spread
time_at_wide_spread
```

También:

```text
spread_relative_to_expected_move
```

Ejemplo:

```text
spread_bps
/
predicted_move_bps_5s
```

Una señal puede ser predictiva y no ser económicamente explotable.

Tu documento ya separa correctamente la existencia del impulso de la tradeability, y marca spread y estabilidad como variables necesarias para filtrar movimientos de libro vacío. 

## Respuesta del precio al order flow

Esta puede ser una de las variables más importantes de todas.  
No basta con medir cuánto compran.  
Hay que medir:

```
¿Cuánto avanza el precio por unidad de presión compradora?
```

Features

```text
price_change_per_buy_volume
price_change_per_net_aggressive_volume
price_change_per_trade
price_change_per_book_event
```

Ejemplo:

```text
flow_efficiency_1s =
mid_return_1s
/
net_aggressive_volume_1s
```

Interpretación:

### Alta agresión + alto avance

```text
demanda efectiva
```

### Alta agresión + poco avance

```text
absorción
posible seller oculto
posible agotamiento
```

### Poca agresión + gran avance

```text
libro vacío
liquidity vacuum
riesgo alto
```

Esta relación será mucho más informativa que una sola variable de volumen.

## Absorción

Para tu estrategia, la absorción no es solo negativa.

Puede haber dos tipos.

### Absorción vendedora**

Compradores golpean el ask, pero el precio no avanza.

```text
buy aggressive volume alto
+
ask reload alto
+
mid return bajo
```

Puede anticipar fallo.

### Absorción compradora**

Vendedores golpean el bid, pero el precio no baja.

```text
sell aggressive volume alto
+
bid replenishment alto
+
mid return estable o positivo
```

Puede anticipar continuación.

Features

```text
ask_absorption_score
bid_absorption_score

buy_volume_without_uptick
sell_volume_without_downtick

repeated_execution_same_ask_price
repeated_execution_same_bid_price
```

Con MBO puedes observar mejor si el mismo nivel se repone.

## Velocidad y aceleración

La “velocidad” que ves como trader debe transformarse en varias variables distintas.

No existe una única velocidad.

### Velocidad del tape

```text
trades_per_second
shares_per_second
dollar_volume_per_second
```

### Velocidad del precio

```text
mid_return_per_second
best_bid_rise_per_second
best_ask_rise_per_second
levels_crossed_per_second
```

### Velocidad del book

```text
book_updates_per_second
adds_per_second
cancels_per_second
modifies_per_second
executions_per_second
```

### Aceleraciones

```text
delta_trades_per_second
delta_volume_per_second
delta_price_velocity
delta_cancel_rate
delta_add_rate
```

Para detectar el despertar, la aceleración puede tener más valor que el nivel absoluto.

Ejemplo:

```text
5 trades/s
```

puede ser alto o bajo según el ticker.

Pero:

```text
de 0,1 trades/s a 5 trades/s en 2 segundos
```

sí representa claramente un cambio de régimen.

## Variables de transición desde acción muerta

Dado que tu patrón parte de una acción dormida, mediría explícitamente el contraste con su baseline.

### Baseline dinámico

Calcular sobre:

```text
últimos 30 s
últimos 60 s
últimos 5 min
desde inicio de premarket
```

### Ratios

```text
trade_rate_vs_5m_baseline
volume_rate_vs_5m_baseline
quote_rate_vs_5m_baseline
cancel_rate_vs_5m_baseline
spread_vs_5m_baseline
volatility_vs_5m_baseline
depth_vs_5m_baseline
```

### Score de despertar

```text
awakening_score =
f(
  trade_rate_acceleration,
  volume_rate_acceleration,
  quote_rate_acceleration,
  positive_OFI,
  buy_aggression,
  ask_depletion,
  bid_replenishment
)
```

Pero inicialmente no definiría una fórmula cerrada.

Guardaría todas las variables y permitiría que el modelo aprendiera sus combinaciones.

## Variables para saber si se llega tarde

En SONN el movimiento fue extraordinariamente rápido.   
Por tanto, no basta con detectar calidad.   
También hay que medir extensión.

Features

```text
return_from_dead_base
return_from_scanner_trigger
return_from_awakening_start
return_from_first_aggressive_burst

distance_from_recent_low
distance_from_vwap
distance_from_microprice
distance_from_last_consolidation

price_velocity_current
price_acceleration_current

seconds_since_awakening
seconds_since_first_volume_burst
seconds_since_scanner_entry
```

Además:

```text
fraction_of_current_impulse_already_traveled
```

No puedes conocer el recorrido final, pero puedes estimar extensión relativa mediante:

```text
movimiento actual / volatilidad reciente
movimiento actual / spread
movimiento actual / profundidad disponible
movimiento actual / ATR intradía estimado
```

## ¿Qué datos raw descargar?

Tu documento guía debería separar claramente:

### A. Raw obligatorio

```text
MBO:
- event timestamp
- receive timestamp
- sequence number
- order_id
- action
- side
- price
- size
- venue
- flags

Trades:
- event timestamp
- receive timestamp
- sequence number
- price
- size
- venue
- condition

Reference:
- symbol
- listing venue
- instrument id
- tick size
- trading status
- corporate actions

Scanner:
- timestamp
- symbol
- filter values
- enter/exit state
- reason
```

### B. Raw deseable

```text
NBBO
venue-specific BBO
auction imbalance
halts/LULD
news timestamps
float/market cap point-in-time
```

### C. Derivados

```text
OFI
microprice
aggressor side
depth imbalance
cancel rates
replenishment
absorption
flow efficiency
awakening score
impulse score
```

### D. Labels/outcomes

```text
valid awakening
false awakening
valid impulse
chop
failure
late entry
MFE
MAE
time to +R
time to -R
fillability
```

La distinción raw/derivado/label ya está implícita en el documento, pero conviene convertirla en una regla formal de adquisición. 

## ¿Qué resolución temporal usar?

No limitaría el sistema a una tabla por segundo.

Mantendría dos capas.

### Event store raw

Sin agregación:

```text
cada add
cada cancel
cada execution
cada trade
cada modificación
```

### State tables

Generaría varias resoluciones:

```text
100 ms
250 ms
500 ms
1 s
```

Para un primer push como SONN, una tabla exclusivamente de un segundo puede perder:

```text
secuencia cancel → trade → replenish
```

que puede ocurrir dentro del mismo segundo.

La tabla de 1 segundo será útil para investigación general, pero conservaría siempre el raw para reconstruir estados más finos.

## ¿Qué ventana histórica descargar alrededor del evento?

Para cada ticker que entra en el scanner:

```text
pre-roll mínimo: 10–30 minutos
periodo completo de actividad
post-roll: 10–30 minutos
```

Para estudiar el despertar desde acción muerta, yo preferiría:

```text
30 minutos antes del scanner trigger
hasta 30 minutos después del primer push high
```

O, cuando sea asequible:

```text
04:00–11:00 ET
```

para todos los symbol-days candidatos.

La ventana anterior es esencial porque el patrón empieza antes de la vela grande.

## ¿Qué hipótesis concretas probaría primero?

No empezaría con cien hipótesis.  
Empezaría con cinco.  

### H1. Aceleración del tape

```
Los pushes válidos presentan una aceleración de trades y volumen significativamente mayor que los falsos despertares.
```

### H2. Agresión + respuesta

```
El volumen comprador agresivo predice continuación solo cuando el precio responde eficientemente.
```

### H3. Consumo y reposición
```
Los mejores pushes muestran ask depletion y bid replenishment simultáneos.
```

### H4. Persistencia
```
La persistencia de OFI positivo durante varios intervalos es más informativa que un único spike.
```

### H5. Extensión y fallo
```
El riesgo de fallo aumenta cuando el volumen comprador sigue creciendo, pero la respuesta del precio cae y el ask se repone.
```

Estas cinco hipótesis ya justifican descargar:

```text
trades
NBBO
MBP-10
MBO
timestamps
scanner history
```

## La arquitectura de datos propuesta

```text
Scanner replay / live scanner
        ↓
Candidate symbol entered
        ↓
Raw market capture
        ├── trades
        ├── NBBO
        ├── MBP-10
        └── MBO
        ↓
Deterministic book reconstruction
        ↓
Microstructure feature engine
        ├── tape activation
        ├── aggressor flow
        ├── depletion/replenishment
        ├── queue dynamics
        ├── spread
        ├── absorption
        ├── price response
        └── extension
        ↓
State tables
        ├── 100 ms
        ├── 250 ms
        ├── 500 ms
        └── 1 s
        ↓
Labels/outcomes separados
        ↓
Supervised baseline
        ↓
Sequential model
        ↓
Trading policy
```

## Decisión importante sobre el proveedor

Para esta investigación, el proveedor debe permitir como mínimo:

```text
historical MBO
live MBO
mismo esquema o esquema reconciliable
trades
sequence numbers
timestamps de exchange
symbol mapping point-in-time
premarket coverage
snapshots o mecanismo correcto de book initialization
```

No compraría un proveedor solo porque diga “Level 3”.

Le exigiría evidencia de:

```text
order_id real
add/cancel/modify/execute
ordenación determinista
premarket
histórico y live comparables
reconstrucción del libro documentada
```



## Conclusión

Para automatizar una entrada como la de SONN, las variables centrales no son únicamente “L2” y “tape”.

Son estas relaciones:
```
aceleración del tape
+
agresión compradora
+
respuesta efectiva del precio
+
consumo del ask
+
reposición del bid
+
persistencia del flujo
-
absorción vendedora
-
spread excesivo
-
extensión tardía
-
chop
```

El documento guía que necesitas construir debería titularse algo parecido a:

[DAS_FIRST_IMPULSE_MICROSTRUCTURE_DATA_REQUIREMENTS_v0_1]()

y tener cinco bloques:
```
1. Fenómeno que se quiere detectar
2. Raw data obligatorio
3. Features microestructurales derivadas
4. Labels y outcomes
5. Requisitos mínimos del proveedor
```
La decisión más importante es esta:

```
No descargamos MBO porque sea el nivel de datos más rico. Lo descargamos para medir consumo, reposición, cancelación, persistencia y respuesta del precio, que son las propiedades que pueden distinguir un primer push válido de una explosión falsa.
```