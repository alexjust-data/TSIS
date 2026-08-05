Sí. Ahora el problema está definido con más precisión:

> **Scanner 1** detecta que el ticker ha despertado.
> **Scanner 2** debe determinar, pocos segundos después, si ese despertar ya se ha convertido en una participación direccional real, ejecutable y suficientemente persistente como para declarar la acción `in play`.

Eso es mucho más temprano que esperar 500.000 acciones acumuladas.

También matizaría una frontera importante:

```text
Scanner 2
→ ENTRY_ELIGIBLE

Entry Policy
→ BUY / NO BUY
```

Si Scanner 2 envía directamente la orden, técnicamente deja de ser sólo un scanner y pasa a ser también una **estrategia de entrada**. No es incorrecto, pero conviene mantener ambas responsabilidades separadas para poder determinar si falla:

* La detección.
* La clasificación `in play`.
* La regla de entrada.
* La ejecución.

---

# 1. La arquitectura que propondría

```text
DORMANT
   │
   │ actividad estadísticamente anormal
   ▼
WAKE_UP_DETECTED
   │
   │ participación real + liquidez + respuesta
   ▼
TRADABLE_DIRECTIONAL_PARTICIPATION
   │
   │ persistencia suficiente
   ▼
ENTRY_ELIGIBLE
   │
   ├── entrada inmediata de activación
   ├── esperar primer pullback
   └── esperar ruptura de nivel
```

Scanner 2 no debería preguntar simplemente:

```text
¿Hay mucho volumen?
```

Sino:

```text
1. ¿La actividad procede de muchos eventos reales
   o de un único print?

2. ¿Existe volumen negociable suficiente
   para nuestro tamaño?

3. ¿La presión compradora está desplazando
   el bid, el ask y el midprice?

4. ¿El movimiento está siendo aceptado
   o inmediatamente rechazado?

5. ¿La intensidad persiste después
   del primer burst?

6. ¿La microestructura está mejorando,
   deteriorándose o siendo absorbida?
```

Eso es lo que sustituye al filtro discrecional de 500.000 acciones.

---

# 2. Cómo encaja exactamente con Market State y Event State

El documento que has adjuntado confirma que TSIS ya posee la arquitectura conceptual adecuada:

* `Market State` representa qué sabía el sistema en `t`.
* `Event State` contextualiza ese estado respecto a un evento.
* Puede existir una arquitectura multirresolución con `market_state_1s` y `market_state_microstructure_window`.
* Las extensiones microestructurales pueden materializarse sólo para instrumentos y ventanas autorizadas, sin crear una megatabla universal. 

Por tanto, no necesitamos nuevos Information Objects. Utilizaríamos los ya admitidos:

```text
price_movement
trading_activity
volatility_range_state
liquidity
market_microstructure_state
order_flow_pressure
price_location_intraday
news_catalyst_context
fundamental_context
short_side_context
halt_context
```

Lo que necesitamos es un **nuevo modelo de representación microestructural** para algunos de ellos.

La cadena correcta sería:

```text
Trades + Quotes
      ↓
observaciones microestructurales derivables
      ↓
Market State microstructure extension
      ↓
Wake-up Event Detector
      ↓
Event State anclado al wake-up
      ↓
Tradable In-Play Classifier
      ↓
Entry Policy
```

Una precisión institucional: el documento indica que actualmente los ejemplos `PM_Squeeze_Event` y `VWAP_Reclaim_Event` son ilustrativos y no Event Types registrados; el scope admitido sigue limitado a `session_opened`. Por tanto, lo que describo es una **arquitectura científica candidata**, no un Event State actualmente autorizado para el backtester. 

---

# 3. Para este problema, menos de un minuto es claramente mejor

Sí: para detectar el primer movimiento, **1 minuto es demasiado grueso**.

Una barra de un minuto puede contener:

```text
09:42:01  ticker muerto
09:42:08  primeros trades
09:42:15  +5%
09:42:27  +15%
09:42:45  primer pullback
09:42:58  segundo breakout
```

Una sola barra no permite distinguir esos estados.

Pero tampoco materializaría velas de un segundo para todo el universo como única solución. Utilizaría tres relojes simultáneamente:

## Tiempo de mercado

```text
250 ms
1 s
3 s
5 s
15 s
30 s
60 s
```

## Tiempo de eventos

```text
últimos 5 trades
últimos 20 trades
últimos 50 trades
últimos 100 trades
```

## Tiempo económico

```text
últimos $10.000 negociados
últimos $25.000
últimos $100.000
últimas 25.000 acciones
```

Esto es especialmente importante en microcaps.

Cinco segundos pueden contener:

```text
Ticker muerto:
2 trades

Ticker activo:
400 trades
```

Una ventana temporal de cinco segundos representa cantidades completamente distintas de información. En cambio, “los últimos 50 trades” permite comparar procesos de actividad más homogéneos.

Por tanto:

> El backtest definitivo debe reproducir trades y quotes evento por evento. Las velas de 1 s y 5 s son vistas derivadas muy útiles, pero no la fuente de verdad de la decisión ni de la ejecución.

La arquitectura multirresolución descrita en vuestro propio documento permite precisamente tener `market_state_1m`, `market_state_1s` y `market_state_microstructure_window` bajo una misma semántica canónica. 

---

# 4. Cómo procesar todo el universo sin un coste absurdo

La cascada sería:

```text
UNIVERSO ELEGIBLE
4.000–5.000 símbolos
        ↓
Procesamiento barato de trades
por evento e incremental
        ↓
WAKE-UP
quizás 10–30 símbolos
        ↓
Activar quotes y microestructura pesada
        ↓
TRADABLE IN-PLAY
quizás 1–5 símbolos
        ↓
Entrada o seguimiento
```

No se recalcula todo para todos los símbolos.

Para cada instrumento se conserva en RAM un estado pequeño:

```text
last_trade_timestamp
trade_count_1s
trade_count_5s
dollar_volume_1s
dollar_volume_5s
last_bid
last_ask
midprice
session_high
activity_baseline
```

Cuando llega un evento:

```python
event = next_market_event()

state = state_by_instrument[event.instrument_id]
state.update_incrementally(event)
```

Si un ticker está muerto y no recibe eventos, prácticamente no requiere trabajo.

Los feeds directos como Nasdaq ITCH están construidos precisamente como secuencias de mensajes de órdenes, ejecuciones, cancelaciones y otros eventos identificados por instrumento. No son un conjunto de gráficos que se recorra continuamente. ([Nasdaq Trader][1])

---

# 5. Qué observaciones adicionales propondría

Además de `trade rate`, `dollar-volume rate`, `quote rate`, retorno y aceleración, añadiría estas representaciones.

## A. Colapso del tiempo entre trades

Cuando una acción despierta, una de las primeras cosas que cambia es el tiempo entre operaciones.

[
IAT_collapse_t =
\frac{
\operatorname{median}(\Delta t_{\text{baseline}})
}{
\operatorname{median}(\Delta t_{\text{recent}})
+\varepsilon
}
]

Ejemplo:

```text
Baseline:
1 trade cada 20 segundos

Ahora:
1 trade cada 80 milisegundos

IAT collapse:
muy elevado
```

Esto puede detectar el cambio antes que el volumen acumulado.

---

## B. Amplitud de participación por venues

Cuando el dato contiene identificadores de exchange o venue:

```text
número de venues ejecutando
concentración del volumen por venue
número de venues actualizando bid/ask
```

Puede calcularse una amplitud como:

[
ParticipationBreadth =
1-\sum_v share_v^2
]

Interpretación:

```text
Un único print en un venue
≠
participación distribuida

Trades continuos en varios venues
=
evidencia más robusta
```

No afirmaría que esto puede construirse hasta comprobar el contrato físico de trades y los campos disponibles.

---

## C. Concentración de prints

```text
largest_trade_share_5s
top_3_trades_share_5s
trade_size_entropy
```

Queremos separar:

```text
Un bloque de 400.000 acciones
```

de:

```text
2.000 operaciones que suman 400.000 acciones
```

Pueden tener el mismo volumen, pero representar fenómenos muy diferentes.

---

## D. Coherencia del flujo

```text
aggressor_buy_ratio
signed_dollar_imbalance
buy_run_length
trade_sign_autocorrelation
trade_sign_entropy
```

No basta con que haya muchas operaciones. Queremos saber si existe una presión coherente.

La investigación pública encuentra que, en ventanas cortas, el desequilibrio de eventos en bid y ask explica los movimientos de precio más consistentemente que el volumen negociado aislado. ([arXiv][2])

---

## E. Conversión del flujo en desplazamiento

[
FlowResponse_t =
\frac{\Delta midprice_t}
{|OFI_t|+\varepsilon}
]

Pero aquí no buscaría simplemente “cuanto más alto, mejor”.

Existen tres zonas:

```text
Respuesta casi cero
→ posible absorción

Respuesta moderada y persistente
→ presión convirtiéndose en precio

Respuesta gigantesca con volumen mínimo
→ vacío de liquidez; puede ser frágil e inoperable
```

Esto permite buscar una zona de respuesta saludable, no una optimización monótona.

---

## F. Eficiencia direccional del recorrido

[
DirectionalEfficiency =
\frac{
|mid_t-mid_{t-W}|
}{
\sum_{i \in W}|\Delta mid_i|
}
]

Dos acciones pueden subir un 5%:

```text
Acción A:
sube prácticamente en línea recta

Acción B:
oscila violentamente arriba y abajo
```

La primera tiene mayor coherencia direccional.

---

## G. Follow-through del bid

Después de compras agresivas:

```text
¿El bid asciende?
¿Aparece nuevo tamaño en el bid superior?
¿El bid permanece?
¿O desaparece inmediatamente?
```

Una representación:

```text
bid_step_up_after_buy_burst_ratio
bid_hold_duration
bid_reversion_rate
```

Esto es particularmente valioso para diferenciar:

```text
un print alcista
```

de:

```text
una subasta que realmente está desplazándose hacia arriba
```

---

## H. Depleción y reposición

Si disponemos de tamaños bid/ask:

```text
ask_depletion_rate
ask_replenishment_rate
bid_replenishment_rate
depth_recovery_time
```

Una configuración favorable puede ser:

```text
ask consumido repetidamente
+
bid ascendiendo y reponiéndose
```

Una configuración peligrosa:

```text
muchas compras
+
ask se repone infinitamente
+
precio no avanza
```

Eso sugiere absorción.

El desequilibrio de las colas bid/ask ha mostrado capacidad predictiva sobre la dirección del siguiente cambio de midprice en estudios de Nasdaq, aunque esa evidencia procede de acciones líquidas y no demuestra directamente el mismo comportamiento en microcaps. ([arXiv][3])

---

## I. Conversión quote-to-trade

```text
marketable trades
dividido por
quote updates
```

Queremos distinguir:

```text
muchísimo movimiento de quotes
pero casi ninguna ejecución
```

de:

```text
quotes actualizándose
y operaciones reales consumiendo liquidez
```

Es una protección frente a un scanner activado sólo por ruido de cotizaciones.

---

## J. Aceptación microestructural

No basta con tocar un nivel.

Después de cruzarlo:

```text
¿Qué porcentaje del tiempo permanece por encima?
¿Qué porcentaje de eventos permanece por encima?
¿El bid se establece por encima?
¿Cuánto tarda en volver debajo?
```

Variables:

```text
acceptance_ratio_1s
acceptance_ratio_3s
events_above_level_ratio
time_to_rejection
```

Esto sustituye la expresión visual:

```text
“rompió y aguantó”
```

por una representación medible.

---

## K. Segundo burst y relevancia residual

Para saber si puede aparecer una segunda oportunidad:

```text
activity_intensity_decay
residual_activity_vs_baseline
time_since_last_burst
second_burst_intensity
price_above_activation_vwap
price_above_activation_base
```

Un ticker puede dejar de acelerar, pero seguir claramente `in play`:

```text
actividad cae de 100× a 20× baseline
precio conserva el 80% del impulso
spread se normaliza
bid se reconstruye
```

Eso es distinto de:

```text
actividad vuelve a 1× baseline
precio pierde todo el impulso
spread se abre
```

---

# 6. Mi definición de `TRADABLE IN-PLAY`

No la definiría por una cantidad absoluta de volumen.

La definiría mediante cuatro familias de evidencia.

```text
A — ACTIVITY SURPRISE
La acción ha salido del régimen dormido.

L — LIQUIDITY / CAPACITY
Podemos ejecutar nuestro tamaño con un coste aceptable.

D — DIRECTIONAL CONVERSION
La presión está desplazando realmente el mercado.

P — PERSISTENCE / ACCEPTANCE
El cambio no es un único print ni un rechazo instantáneo.
```

El flujo sería:

```text
A
→ WAKE-UP

A + L + D
→ EARLY ENTRY_ELIGIBLE

A + L + D + P
→ CONFIRMED ENTRY_ELIGIBLE
```

Así existen dos posibles políticas:

```text
Política agresiva:
entra en A + L + D

Política conservadora:
espera A + L + D + P
```

No obligaría a que todos los indicadores individuales superasen umbrales rígidos. Utilizaría un **quorum de evidencias**:

```text
Activity Surprise obligatorio
Tradability obligatoria

y además:

2 de 3:
- order-flow coherence
- price-response efficiency
- persistence/acceptance
```

Esto es más robusto que una cadena de quince filtros obligatorios.

---

# 7. Cómo cortar sin sobreoptimizar

Esta es probablemente la cuestión más importante.

## Market State no debe contener el corte

`Market State` debe conservar observaciones:

```text
trade_rate_percentile
iat_collapse
dollar_volume_rate
spread_bps
capacity_ratio
ofi
directional_efficiency
acceptance_ratio
```

No debería decir:

```text
buy = true
```

El corte pertenece a:

```text
Event Detector
o
Entry Policy
```

La separación sería:

```text
Market State
= descripción observable

Event Detector
= ha ocurrido suficiente cambio para emitir un evento

Event State
= contexto respecto a ese evento

Entry Policy
= compro o no compro
```

Eso encaja con el documento: los patrones y estrategias deben ser proyecciones consumidoras de una representación canónica, no definiciones alternativas de Market State. 

---

## No calibrar contra los ganadores

El error sería:

```text
Miro 500 movimientos buenos.
Busco los valores que mejor los describen.
Creo el filtro.
```

El universo de calibración debe contener:

```text
todos los instrumentos elegibles
×
todos los instantes observables
×
días buenos y normales
×
activaciones exitosas y fallidas
```

El ZIP no debe definir el detector. Sirve para entender el fenómeno y construir hipótesis.

---

## Transformar las variables a sorpresa estadística

En vez de decir:

```text
trade_count_5s >= 20
```

podemos expresar:

```text
trade_count_5s está en el percentil 99,9
para ese ticker, franja horaria y contexto
```

Cada observación se convierte en:

[
surprise(x_t)
=============

-\log\left(
1-F_{\text{baseline}}(x_t)
\right)
]

La baseline puede condicionarse por:

```text
ticker o grupo de liquidez
precio
franja horaria
premarket / regular
día de la semana
historial reciente
```

Esto evita que un mismo número absoluto signifique cosas distintas para dos acciones.

---

## El umbral se selecciona por carga operativa, no por P&L

Por ejemplo:

```text
Objetivo del Wake-up Scanner:

máximo 20 alertas diarias
o

menos de 1 falsa activación
por cada 10.000 symbol-seconds
```

Entonces seleccionamos el nivel de sorpresa que cumple ese presupuesto.

No elegimos:

```text
el umbral que produjo más beneficio histórico
```

Elegimos:

```text
el umbral que controla la frecuencia de falsas alarmas
y permite operar el sistema
```

Después, con el detector congelado, evaluamos la estrategia.

---

## Hard gates frente a soft evidence

### Hard gates

Proceden de restricciones reales:

```text
market cap
precio
calidad del dato
quote no stale
spread máximo tolerable
capacidad mínima para nuestro tamaño
no halt activo
```

No se eligen para maximizar el Sharpe. Se derivan de:

```text
tamaño de orden
riesgo máximo
slippage tolerable
mercado operable
```

### Soft evidence

```text
activity surprise
OFI
price response
persistence
acceptance
```

Estas variables pueden formar un score o ranking.

En lugar de cortar arbitrariamente en 0,713:

```text
ordenamos todos los candidatos
y observamos sólo el top K
```

Un `top-K` por score suele ser operativamente más estable que multitud de umbrales absolutos.

---

## Proceso de validación

Evaluaría el detector mediante:

```text
tiempo hasta la detección
retorno ya recorrido al detectarlo
alertas por símbolo-hora
porcentaje de wake-ups fallidos
spread ejecutable en la detección
capacidad disponible
persistencia tras la alerta
```

No inicialmente mediante beneficio.

Después congelaría el detector y evaluaría las políticas de entrada mediante:

```text
desarrollo
calibración
test temporal no visto
purging por ticker/día/episodio
embargo entre eventos relacionados
estabilidad en regiones vecinas
```

No aceptaría un parámetro porque sea el máximo. Buscaría una **meseta estable**:

```text
5 s, 8 trades  → funciona
5 s, 10 trades → funciona
5 s, 12 trades → funciona
3 s, 10 trades → funciona
10 s, 10 trades → funciona
```

No:

```text
sólo funciona exactamente con
7 segundos y 13 trades
```

---

# 8. Ejemplo de perfil de Market State

Conceptualmente:

```yaml
profile_id: market_state_microstructure_wakeup_extension_v0_1

instrument_id: ABCD
decision_timestamp: 09:42:08.250
state_available_at: 09:42:08.260

trading_activity:
  trade_rate_1s: ...
  trade_rate_5s: ...
  dollar_volume_rate_5s: ...
  interarrival_collapse_20trades: ...
  venue_breadth_5s: ...
  largest_trade_share_5s: ...

liquidity:
  spread_bps: ...
  quote_age_ms: ...
  bid_notional: ...
  ask_notional: ...
  target_order_capacity_ratio: ...
  bid_replenishment_rate: ...
  ask_replenishment_rate: ...

order_flow_pressure:
  aggressor_buy_ratio_1s: ...
  signed_dollar_imbalance_5s: ...
  ofi_1s: ...
  buy_run_length: ...

price_movement:
  mid_return_1s: ...
  mid_return_5s: ...
  velocity: ...
  acceleration: ...
  directional_efficiency: ...
  flow_response_efficiency: ...

market_microstructure_state:
  bid_step_follow_ratio: ...
  quote_to_trade_conversion: ...
  acceptance_ratio: ...
  rejection_rate: ...

price_location:
  distance_to_hod: ...
  distance_to_pmh: ...
  distance_to_tsis_vwap: ...
  distance_to_activation_vwap: ...
```

Después, el detector observa una **secuencia de Market States**, no sólo una fila.

---

# 9. Cómo detectar los patrones visuales

No comenzaría codificando literalmente:

```text
si aparecen tres velas verdes
y después dos rojas pequeñas
es una bandera
```

Eso es demasiado dependiente de:

```text
resolución de la vela
hora de inicio
duración de la barra
criterios visuales del observador
```

La expresión `single-candle rebreak` cambia completamente si usamos velas de:

```text
1 s
5 s
15 s
1 min
```

Por tanto, los patrones deben convertirse en **trayectorias de estados invariantes a la resolución**.

## Impulse

```text
desplazamiento positivo
+
actividad anormal
+
eficiencia direccional
+
presión compradora
+
expansión de rango
```

No requiere que exista una vela verde concreta.

---

## First pullback

```text
impulso previo válido
+
retroceso desde el máximo
+
retracement ratio acotado
+
disminución de actividad
+
presión vendedora menor que la compradora del impulso
+
conservación del activation VWAP o nivel estructural
```

---

## Ascending flag

```text
máximos contenidos
+
mínimos ascendentes
+
contracción de rango
+
actividad decreciente durante la pausa
+
bid reconstruyéndose
```

---

## Multi-candle flag

No sería otro fenómeno diferente de `ascending flag`.

Sería:

```text
la misma fase de consolidación
con mayor duración
```

La duración sería una variable:

```text
consolidation_duration_seconds
consolidation_event_count
```

---

## Flat shelf

```text
precio próximo al HOD
+
rango comprimido
+
pendiente aproximadamente plana
+
múltiples tests del techo
+
reacciones bajistas cada vez menores
+
persistencia de actividad por encima del baseline
```

---

## Rebreak

```text
final de pullback/consolidación
+
ruptura del máximo local
+
renovación de trade intensity
+
renovación de OFI comprador
+
bid avanzando
+
aceptación por encima del nivel
```

---

## VWAP reclaim

No es sólo:

```text
last > VWAP
```

Debe incluir:

```text
venía desde debajo
cruza TSIS_VWAP
bid se establece sobre VWAP
permanece sobre VWAP
flujo comprador acompaña
no existe rechazo inmediato
```

---

## Last-red-high break

Es principalmente un **nivel de referencia**:

```text
identificar último segmento bajista cerrado
guardar su máximo
detectar ruptura
evaluar microestructura en la ruptura
```

No debería ser una estrategia completa por sí solo.

---

## Failure / exhaustion

```text
compras agresivas elevadas
+
escaso progreso de precio

o

nuevo máximo
+
rechazo inmediato
+
spread aumentando
+
bid desapareciendo
+
menor actividad en el segundo impulso
+
pérdida del activation VWAP
```

Esto es más útil como:

```text
veto de entrada
salida
reducción de tamaño
cambio de estado frontside → backside
```

---

# 10. Cómo lo hace la alta frecuencia

No sabemos las reglas exactas de cada fondo; son propietarias.

Pero la evidencia pública sobre microestructura muestra que el enfoque habitual no consiste en reconocer gráficamente “banderas” como lo haría un trader discrecional.

La unidad fundamental suele ser:

```text
evento de orden
evento de cancelación
ejecución
cambio bid/ask
cambio de profundidad
tiempo entre eventos
estado de la cola
```

La investigación sobre queue imbalance muestra que una variable muy sencilla de desequilibrio del libro puede aportar información sobre el siguiente movimiento de precio. ([arXiv][3])

Otros trabajos utilizan miles de millones de transacciones y quotes para aprender directamente relaciones entre la dinámica de oferta/demanda del libro y movimientos posteriores del precio. ([arXiv][4])

La interpretación correcta no es:

```text
HFT no utiliza niveles técnicos nunca.
```

Puede utilizar:

```text
HOD
VWAP
máximos locales
niveles de apertura
round numbers
```

porque otros participantes reaccionan a esos niveles.

Pero normalmente los representa como:

```text
distancia al nivel
intensidad al aproximarse
consumo de liquidez
probabilidad de cruce
aceptación después del cruce
respuesta del libro
```

No como una imagen subjetiva de una bandera.

---

# 11. ¿Una estrategia o varias?

La mejor estructura sería:

```text
UN ÚNICO FRONTSIDE STATE TRACKER
        ↓
VARIAS ENTRY POLICIES
```

## Estrategia 1 — Early Activation Entry

```text
A + L + D
→ entrada rápida
```

Busca entrar durante la activación inicial.

Tiene:

```text
mayor potencial
mayor slippage
mayor tasa de falsos positivos
mayor sensibilidad a latencia
```

Debe evaluarse separadamente.

---

## Estrategia 2 — First-Pullback Continuation

Incluye como variantes:

```text
rapid rebreak
ascending flag
multi-event flag
flat shelf
```

No crearía una estrategia distinta para cada dibujo. Todas comparten la misma hipótesis económica:

> Después de un impulso con participación real, el flujo vendedor del primer pullback es menor y aparece una nueva expansión compradora.

La duración, pendiente y forma de la consolidación serían atributos del estado.

---

## Estrategia 3 — Reference-Level Continuation

```text
PMH breakout
HOD breakout
VWAP reclaim
last-red-high break
opening-range breakout
```

Comparten la idea de que un nivel observable concentra decisiones y liquidez, pero conservaría atribución separada por trigger.

---

## Failure / Exhaustion

No lo trataría como estrategia larga.

Sería:

```text
entry veto
exit policy
frontside termination detector
posible activador de investigación short
```

---

## Por qué separarlas inicialmente

Aunque compartan Market State y State Tracker, difieren en:

```text
instante de entrada
latencia
slippage
stop estructural
duración
riesgo de halt
capacidad
distribución de resultados
```

Por tanto:

```text
shared state representation
shared event tracker
separate strategy IDs
separate PnL attribution
```

Sólo después de demostrar edge individual tendría sentido un router:

```text
estado actual
      ↓
elige entry policy más adecuada
```

---

# 12. La propuesta TSIS concreta

```text
TSIS_MICROCAP_WAKEUP_DETECTOR_V0_1
=
detector de alta sensibilidad
sobre trades y actividad

TSIS_TRADABLE_INPLAY_CLASSIFIER_V0_1
=
participación
+ capacidad
+ conversión direccional
+ persistencia

TSIS_FRONTSIDE_STATE_TRACKER_V0_1
=
impulse
pullback
compression
rebreak_ready
continuation
failure
terminated

ENTRY_POLICY_ACTIVATION_V0_1
=
entrada temprana

ENTRY_POLICY_FIRST_PULLBACK_V0_1
=
entrada de continuación

ENTRY_POLICY_REFERENCE_LEVEL_V0_1
=
PMH/HOD/VWAP/local-level
```

Y la separación institucional:

```text
Market State
=
hechos y representaciones observables

Wake-up Detector
=
emite el primer evento

Event State
=
contextualiza la secuencia respecto al wake-up

Tradable In-Play Classifier
=
declara ENTRY_ELIGIBLE

Entry Policy
=
decide la orden

Execution Model
=
decide fill, tamaño y precio
```

La idea central queda así:

> **No sustituir el volumen de 500.000 acciones por otro único filtro más rápido. Sustituirlo por una transición de estado basada en sorpresa de actividad, amplitud de participación, capacidad ejecutable, conversión del order flow en precio y persistencia microestructural.**

Y para no sobreoptimizar:

> **Market State conserva observaciones; el detector se calibra contra el régimen dormido y un presupuesto de falsas alertas; la estrategia se evalúa sólo después de congelar el detector.**

[1]: https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf?utm_source=chatgpt.com "Nasdaq TotalView-ITCH 5.0"
[2]: https://arxiv.org/abs/1011.6402?utm_source=chatgpt.com "The Price Impact of Order Book Events"
[3]: https://arxiv.org/abs/1512.03492?utm_source=chatgpt.com "Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book"
[4]: https://arxiv.org/abs/1803.06917?utm_source=chatgpt.com "Universal features of price formation in financial markets"
