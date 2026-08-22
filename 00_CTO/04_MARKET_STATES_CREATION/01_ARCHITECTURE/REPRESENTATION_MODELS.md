# Aquí está el núcleo científico de todo el experimento

Hasta ahora has definido **qué significados necesita conservar TSIS** para estudiar el `Wake-up`.   
Ahora vas a decidir **con qué sistema conceptual de coordenadas será observable ese significado**.

Esa decisión es mucho más profunda que escoger indicadores:

```text
Information Object
=
qué significado queremos preservar

Representation Model
=
qué dimensiones observables consideramos necesarias
para representar ese significado

Physical Implementation
=
qué variables, fórmulas, ventanas y fuentes
materializan cada dimensión

Detector
=
cómo combinamos las representaciones
para decidir si existe Wake-up
```

Tu arquitectura ya establece correctamente que el Objeto de Información debe permanecer estable aunque cambie su modelo o su implementación física. 

Y el perfil candidato actual queda coherentemente dividido en:

* cuatro objetos `CORE`;
* dos objetos de contexto;
* tres objetos condicionados;
* una extensión diferida. 

Pero hay una rectificación decisiva:

> **La literatura científica no podrá demostrar que existe un único modelo verdadero y que todos los demás son falsos.**

Lo que sí puede hacer es:

1. demostrar qué dimensiones del fenómeno han sido observadas de forma recurrente;
2. demostrar las limitaciones conocidas de determinadas medidas;
3. descartar modelos incompatibles con tu pregunta científica, tus datos o tu causalidad;
4. producir varios modelos candidatos defendibles;
5. permitir que un protocolo experimental preregistrado decida cuál se admite para el perfil `Wake-up`.

Metodológicamente, esto es un problema de **validez de constructo**: el objeto —por ejemplo, `Liquidity`— no está definido por una única operación de medida; hay que demostrar que la representación conserva realmente el constructo que pretende representar. ([meehl.umn.edu][1])

Por tanto:

```text
LA LITERATURA
no selecciona automáticamente el modelo ganador.

LA LITERATURA
define el espacio de modelos científicamente defendibles
y ayuda a descartar los conceptualmente inválidos.

EL EXPERIMENTO TSIS
selecciona el modelo admitido para Wake-up.
```

---

# 1. Lo que muestran SGN y LIDR

Los gráficos son especialmente útiles para definir los requisitos semánticos, aunque por sí solos no puedan validar un modelo.

## SGN

Visualmente se observa:

```text
régimen prácticamente dormido
↓
compresión abrupta del tiempo entre operaciones
↓
explosión de volumen
↓
desplazamiento de precio
↓
trayectoria ascendente
↓
breakout de PMH mucho más tarde
```

El `Gap and Go trigger` de las 10:01 no representa el despertar.

Cuando aparece ese trigger, SGN lleva mucho tiempo completamente activado y ha recorrido ya gran parte del frontside.

Por tanto:

```text
PMH breakout
≠
Wake-up

PMH breakout
=
posible evento posterior dentro del Episode Instance
```

## LIDR

En LIDR parece existir:

```text
actividad previa no completamente dormida
↓
primera activación alrededor de las 04:20
↓
larga trayectoria/consolidación
↓
reactivación próxima a la apertura
↓
breakout de PMH
↓
terminación violenta
```

El breakout de las 09:36 tampoco es necesariamente el primer `Wake-up`. Puede ser:

```text
reactivation
continuation burst
breakout event
phase transition
```

dentro de un episodio que comenzó horas antes.

Esto encaja con tu distinción entre:

```text
Wake-up
↓
Episode Instance
↓
bursts, pullbacks, halts y reactivaciones
↓
termination
```

El propio perfil ya define `Episode Instance` como la entidad encargada de seguir esa evolución posterior. 

## Consecuencia científica

Los modelos de representación no pueden construirse alrededor de:

* `PMH breakout`;
* una vela grande;
* `volume > 500k`;
* una subida porcentual fija;
* un patrón gráfico concreto.

Necesitan conservar:

```text
1. estado anterior;
2. nivel absoluto actual;
3. sorpresa respecto al baseline PIT;
4. velocidad de transición;
5. organización temporal de los eventos;
6. respuesta contemporánea del mercado;
7. persistencia o desaparición de la activación.
```

---

# 2. Wake-up es un problema de detección secuencial de cambio

La pregunta científica no es simplemente:

```text
¿Este ticker tiene mucho volumen?
```

Es:

```text
¿En qué instante podemos afirmar,
usando solamente información disponible hasta t,
que el proceso observable ha dejado de comportarse
como su régimen dormido contextual?
```

Formalmente:

```text
H0:
el instrumento continúa dentro de su régimen
contextualmente esperable.

H1:
el proceso observable ha cambiado
hacia una activación materialmente anómala
y suficientemente corroborada.
```

La literatura de detección secuencial de cambios plantea precisamente el compromiso entre:

```text
retraso de detección
versus
tasa de falsas alarmas
```

Lorden formalizó la detección rápida de un cambio mediante reglas de parada, y Bayesian Online Changepoint Detection representa cambios como alteraciones abruptas de los parámetros generadores de una secuencia observada. ([Project Euclid][2])

Esto implica que el objetivo del modelo de representación no es producir directamente una alerta. Debe proporcionar al detector una representación suficiente para observar:

```text
antes del cambio
durante la transición
después del cambio
```

Podemos expresarlo así:

[
Z_O(t)=f_O\left(H_t^{legal},B_O(t)\right)
]

donde:

```text
O
=
Information Object

H_t^legal
=
todo el historial legalmente disponible hasta t

B_O(t)
=
baseline PIT aplicable al objeto O en t

Z_O(t)
=
representación causal del objeto O en t
```

Y el detector sería otra pieza:

[
\tau=\inf{t:g(Z_{t-w:t})\geq h}
]

donde `τ` es el instante de detección.

---

# 3. Sobre tu ejemplo de Liquidity: los modelos A y B no sirven para este perfil

Tus ejemplos son correctos como explicación arquitectónica, pero **no deben convertirse en los modelos candidatos definitivos de Wake-up**.

El propio documento de arquitectura utiliza esos modelos como ilustración de la separación entre objeto, modelo y variables. No los declara como modelos canónicos. 

Tus ejemplos dicen:

```text
MODELO A

- Coste de ejecución
- Facilidad para cruzar órdenes
- Profundidad disponible
```

y:

```text
MODELO B

- Liquidez implícita del order book
- Impacto esperado de una orden
- Elasticidad del precio
```

Pero tu perfil `Wake-up` ya ha excluido expresamente:

```text
target_order_size
coste esperado de nuestra orden
impacto estimado para nuestro tamaño
decisión final de Tradability
```



Por tanto, ambos modelos responden parcialmente a otra pregunta:

```text
¿Podría ejecutar mi orden de tamaño Q
con un coste aceptable?
```

Esa sería una pregunta de:

```text
Execution Model
Tradability
Order-conditioned Liquidity
Entry Eligibility
```

No es la pregunta actual:

```text
¿Qué condiciones observables de liquidez
acompañan al Wake-up?
```

La solución correcta no es eliminar para siempre esos modelos. Es hacerlos **dependientes del perfil de consumo**:

```text
Information Object:
Liquidity

Representation Model para Wake-up:
observable market liquidity state

Representation Model para Execution:
order-size-conditioned executable liquidity

Representation Model para Portfolio Capacity:
capacity and market-impact liquidity
```

El objeto sigue siendo `Liquidity`, pero no se obliga a que una única representación universal sirva para todos los problemas.

La clave determinista sería:

```text
information_object_id
+
representation_profile_id
+
representation_model_version
```

Por ejemplo:

```text
liquidity
+
wake_up_information_object_profile_v0_1
+
observable_l1_liquidity_state_v0_1
```

---

# 4. Envolvente común para los modelos de Wake-up

Debido a que Wake-up es una transición, cada modelo central debería conservar, cuando tenga sentido, cuatro perspectivas:

```text
CURRENT LEVEL
¿Qué estado observable existe ahora?

BASELINE-RELATIVE SURPRISE
¿Cómo difiere respecto al régimen PIT esperado?

TRANSITION DYNAMICS
¿A qué velocidad está cambiando?

PERSISTENCE / DECAY
¿Se mantiene la alteración o desaparece inmediatamente?
```

Separadamente, sin introducirlos dentro del significado del objeto:

```text
AVAILABILITY
QUALITY
COVERAGE
LINEAGE
CONFIDENCE
```

deben proceder de los contratos temporales y de calidad.

Esto permite distinguir, por ejemplo:

```text
Ticker A:
pasa de 1 trade/minuto a 20 trades/minuto
→ sorpresa relativa enorme
→ materialidad quizá insuficiente

Ticker B:
pasa de 20.000 a 40.000 acciones/minuto
→ sorpresa relativa moderada
→ materialidad absoluta relevante
```

Por eso tu necesidad científica exige conservar simultáneamente:

* sorpresa respecto al baseline;
* materialidad absoluta. 

---

# 5. Modelos de representación candidatos

Los siguientes modelos no deberían declararse todavía como `ACCEPTED`. Mi recomendación es registrarlos como:

```text
REPRESENTATION_MODEL_CANDIDATE_V0_1
```

---

## 5.1 Trading Activity

```text
INFORMATION OBJECT
Trading Activity

REPRESENTATION MODEL CANDIDATE
BASELINE-RELATIVE MARKED ACTIVITY PROCESS
```

### Qué conceptualiza

La actividad transaccional se representa como un proceso irregular de eventos cuyos:

* tiempos de llegada;
* tamaños;
* valores nocionales;
* concentraciones;
* cambios de intensidad;

se comparan con el régimen PIT esperado del instrumento.

### Debe conservar

```text
ABSOLUTE ACTIVITY
- número de trades
- número de acciones
- dollar volume
- presencia o ausencia de actividad

EVENT INTENSITY
- ritmo de llegada de trades
- duración entre trades
- compresión o expansión del tiempo entre eventos

ACTIVITY MARKS
- distribución de tamaños
- distribución de dollar sizes
- concentración en prints pequeños o grandes

TEMPORAL CONCENTRATION
- actividad dispersa
- actividad agrupada en bursts
- proporción concentrada en subventanas breves

RELATIVE SURPRISE
- desviación respecto al baseline PIT
- desviación respecto a la franja horaria y sesión
- desviación respecto al régimen reciente

PERSISTENCE
- continuidad de la intensidad
- duración del burst
- decaimiento
- reactivación
```

Los datos transaccionales llegan en intervalos irregulares, por lo que la literatura de ultra-alta frecuencia los modela naturalmente mediante procesos puntuales marcados y modelos de duración. Engle y Russell representan explícitamente el tiempo entre eventos como un proceso estocástico; Dufour y Engle encuentran que duraciones más cortas entre operaciones están asociadas con cambios en la velocidad y el impacto del ajuste de precios. ([EconPapers][3])

También es necesario normalizar por franja temporal: la periodicidad intradía afecta fuertemente a la dinámica observada, y la negociación fuera de horario posee condiciones de precio y participación diferentes de la sesión regular. ([ScienceDirect][4])

### Por qué no representar Trading Activity solamente mediante volumen

```text
CUMULATIVE VOLUME ONLY
```

falla porque:

* no preserva el tiempo exacto de llegada;
* no distingue 100 operaciones de una sola operación grande;
* no distingue actividad concentrada de actividad dispersa;
* depende fuertemente del momento de la sesión;
* llega tarde si el umbral es 500.000 acciones;
* no conserva la forma de la transición.

### Por qué no congelar ACD o Hawkes como modelo canónico

`ACD`, `Hawkes`, `CUSUM` o `BOCPD` serían posibles **estimadores o detectores**.

No deberían ser la identidad conceptual del modelo.

El modelo conceptual correcto es:

```text
marked activity intensity
+
baseline-relative surprise
+
transition and persistence
```

Después se podrá comparar físicamente:

```text
IMPLEMENTATION A
rolling counts and volumes

IMPLEMENTATION B
conditional duration / intensity estimates

IMPLEMENTATION C
self-exciting point-process estimates
```

sin cambiar el modelo conceptual.

### Veredicto provisional

```text
RECOMMENDED CANDIDATE
Baseline-Relative Marked Activity Process

REJECT AS SUFFICIENT MODEL
Raw cumulative volume
1-minute RVOL alone
trade count alone
one fixed-window z-score
```

---

## 5.2 Market Microstructure State

```text
INFORMATION OBJECT
Market Microstructure State

REPRESENTATION MODEL CANDIDATE
OBSERVED TRADE–QUOTE EVENT COUPLING STATE
```

### Qué conceptualiza

Representa cómo se organizan y relacionan temporalmente los eventos observados de:

```text
trades
bid updates
ask updates
quote-size updates
midprice revisions
```

durante la transición.

No representa todavía quién está comprando o vendiendo. Eso pertenecería a `Order Flow Pressure`.

### Debe conservar

```text
EVENT COMPOSITION
- proporción de trades y quote updates
- cambios de precio frente a cambios solo de tamaño

SEQUENCING
- orden causal de trades y quotes
- intervalos entre eventos
- secuencias repetidas

TRADE–QUOTE COUPLING
- quote revisions posteriores a trades
- latencia observable trade → quote
- cambios de midprice alrededor de trades

MULTIEVENT CORROBORATION
- múltiples eventos consistentes
- print aislado
- quote aislada
- secuencia coherente de activación

CONTINUITY
- flujo continuo
- bursts fragmentados
- largos silencios
- reanudaciones

CONTEMPORANEOUS RESPONSE
- respuesta de bid
- respuesta de ask
- respuesta de midprice
```

Hasbrouck propuso modelar conjuntamente trades y revisiones de quotes para estudiar el efecto informativo persistente de las operaciones. Engle y otros modelos de procesos puntuales muestran que la relación entre llegadas de trades y quotes contiene información que desaparece al agregarlos prematuramente. ([EconPapers][5])

La evidencia sobre eventos del libro también muestra que las variaciones cortas de precio dependen de la organización conjunta de demanda, oferta y profundidad, y no únicamente del volumen negociado. ([OUP Academic][6])

### Limitación decisiva de tus datos

TSIS tiene `trades` y `quotes`, pero eso no significa necesariamente que posea un feed completo de órdenes individuales.

Por tanto, el modelo debe hablar de:

```text
observed quote updates
```

y no afirmar sin evidencia:

```text
new limit order
cancellation
hidden order
full order-book depletion
```

Un cambio de tamaño en una quote consolidada no demuestra por sí solo qué evento latente lo produjo.

### Por qué no usar OHLCV de un minuto

Una barra puede mostrar:

```text
volume = 100.000
high = 2.00
low = 1.70
close = 1.95
```

pero no revela si ocurrió:

```text
un solo print erróneo
cincuenta operaciones coherentes
quotes sin respuesta
spread abierto durante casi toda la ventana
actividad agrupada en dos segundos
actividad uniforme durante un minuto
```

### Frontera con los demás objetos

```text
Trading Activity
=
cuánta actividad y a qué ritmo

Market Microstructure State
=
cómo se organizan e interactúan los eventos

Liquidity
=
qué condiciones observables de capacidad y fricción existen

Order Flow Pressure
=
qué presión direccional inferida ejerce el flujo
```

### Veredicto provisional

```text
RECOMMENDED CANDIDATE
Observed Trade–Quote Event Coupling State

REJECT AS SUFFICIENT MODEL
OHLCV-only microstructure
independent trade and quote summaries
static quote snapshot
full order-book model unsupported by source data
```

---

## 5.3 Price Movement

```text
INFORMATION OBJECT
Price Movement

REPRESENTATION MODEL CANDIDATE
SIGNED MULTISCALE PRICE-PATH RESPONSE
```

### Qué conceptualiza

El movimiento se representa como una trayectoria firmada y multiescala, no como un retorno único.

### Debe conservar

```text
DIRECTION
- up
- down
- mixed
- indeterminate

DISPLACEMENT
- desplazamiento neto
- desplazamiento desde el inicio aparente del burst
- desplazamiento desde referencias causales

VELOCITY
- cambio por unidad de tiempo
- cambio por evento
- aceleración

PATH EFFICIENCY
- desplazamiento neto
  dividido por recorrido total
- movimiento directo frente a movimiento errático

PRICE-SOURCE AGREEMENT
- last trade
- eligible trade price
- midprice
- bid
- ask

PERSISTENCE
- continuidad
- estancamiento
- reversión
- agotamiento inicial

MULTISCALE STRUCTURE
- respuesta inmediata
- respuesta breve
- respuesta acumulada
```

A frecuencias elevadas, el precio transaccional contiene ruido microestructural; observar más frecuentemente sin modelar ese ruido no garantiza una estimación más limpia del movimiento subyacente. ([OUP Academic][7])

Por eso el modelo no debe depender exclusivamente de:

```text
last_trade_price
```

Debe poder contrastar:

```text
trade price
midquote
bid
ask
```

y conservar desacuerdos entre ellos.

### Diferencia con Volatility / Range State

```text
Price Movement
=
trayectoria firmada
dirección y progreso

Volatility / Range State
=
variación no firmada
magnitud e inestabilidad
```

Un ticker puede tener:

```text
alta volatilidad
+
casi cero desplazamiento neto
```

o:

```text
baja oscilación
+
desplazamiento direccional muy eficiente
```

### Por qué no utilizar un retorno o indicador de momentum como modelo

```text
return_1m
RSI
MACD
slope
```

son posibles implementaciones.

No representan por sí solas toda la semántica del objeto porque no conservan necesariamente:

* recorrido;
* eficiencia;
* confirmación de bid/ask;
* aceleración;
* persistencia;
* reversión.

### Por qué PMH breakout no pertenece aquí

`PMH breakout` combina:

```text
Price Movement
+
Price Location / Structure
+
una regla de Event Type
```

No es una representación general de `Price Movement`.

### Veredicto provisional

```text
RECOMMENDED CANDIDATE
Signed Multiscale Price-Path Response

REJECT AS SUFFICIENT MODEL
single return
last-trade-only movement
RSI/MACD representation
chart-pattern label
PMH-break flag
```

---

## 5.4 Liquidity

```text
INFORMATION OBJECT
Liquidity

REPRESENTATION MODEL CANDIDATE
OBSERVABLE TOP-OF-BOOK LIQUIDITY
AND RESILIENCE STATE
```

### Qué conceptualiza

Representa las condiciones de liquidez observables que existen en el mercado durante la activación, sin condicionar todavía la representación al tamaño de nuestra orden.

### Debe conservar

```text
AVAILABILITY
- existencia de bid
- existencia de ask
- mercado bilateral
- ausencia temporal de quotes

FRESHNESS
- edad de bid
- edad de ask
- quotes stale
- continuidad de actualización

TIGHTNESS
- spread absoluto
- spread relativo
- spread en ticks

DISPLAYED DEPTH
- tamaño mostrado en bid
- tamaño mostrado en ask
- profundidad en acciones
- profundidad en dólares

ASYMMETRY
- diferencia bid/ask
- concentración unilateral
- cambio de asimetría

RESILIENCE
- recuperación después de una reducción de profundidad
- cierre del spread después de abrirse
- reposición observable
- persistencia del deterioro

CONTINUITY
- estabilidad del mercado bilateral
- alternancia entre mercado y no-mercado
- fragmentación temporal
```

Kyle describe la liquidez como un fenómeno multidimensional relacionado con tightness, depth y resilience. La evidencia específica de la SEC sobre small caps estadounidenses muestra además que los valores de menor capitalización, especialmente por debajo de 100 millones de dólares, presentan en promedio spreads mayores, menor volumen y menor profundidad que grupos de mayor capitalización. ([Personas Duke][8])

Esto obliga a conservar tanto:

```text
valores absolutos
```

como:

```text
valores normalizados por precio,
tick, escala y baseline del instrumento
```

### Qué no debe contener

```text
expected_cost_for_our_order
impact_for_target_order_size
fill probability for our order
tradability decision
entry eligibility
```

Esas dimensiones pertenecerán a una representación posterior condicionada por orden o al modelo de ejecución.

### Por qué volumen no representa liquidez

Puede existir:

```text
mucho volumen
+
spread enorme
+
depth mínima
+
alta inestabilidad
```

y también:

```text
poco volumen observado
+
quotes estrechas
+
profundidad estable
```

`Volume` aporta información sobre `Trading Activity`, no sustituye la representación de `Liquidity`.

### Por qué no utilizar Amihud, Roll o Kyle lambda como modelo primario

Esas medidas pueden convertirse en:

* implementaciones auxiliares;
* contexto histórico;
* proxies cuando no hay quotes suficientes;
* extensiones de análisis de impacto.

Pero para detectar una transición en segundos o minutos, teniendo quotes observables, no deberían sustituir:

```text
spread
depth
quote continuity
freshness
resilience
```

### Veredicto provisional

```text
RECOMMENDED CANDIDATE
Observable Top-of-Book Liquidity
and Resilience State

REJECT FOR WAKE-UP PROFILE
order-size-conditioned liquidity
execution-cost model
volume-as-liquidity
latent full-book liquidity without full-book data
```

---

# 6. Supporting Context

## 6.1 Volatility / Range State

```text
REPRESENTATION MODEL CANDIDATE
UNSIGNED MULTISCALE VARIATION
AND RANGE-EXPANSION STATE
```

### Debe conservar

```text
- rango observable;
- variación acumulada;
- expansión respecto al baseline PIT;
- velocidad de expansión;
- estabilidad o inestabilidad;
- persistencia;
- discontinuidad o jump-like behavior;
- separación entre desplazamiento y oscilación.
```

La literatura de variación realizada distingue entre variación integrada y movimientos discontinuos, mientras que la literatura de ruido microestructural advierte que las estimaciones a muy alta frecuencia pueden quedar contaminadas si se utilizan retornos brutos sin tratar la estructura del dato. ([OUP Academic][9])

### No debe ser

```text
ATR de una ventana fija
```

como definición universal.

ATR puede ser una implementación candidata, pero no conserva por sí solo:

* baseline PIT;
* expansión;
* persistencia;
* diferencia entre jump y oscilación;
* estructura multiescala.

---

## 6.2 Price Location / Structure

```text
REPRESENTATION MODEL CANDIDATE
CAUSAL ANCHOR-RELATIVE LOCATION STATE
```

### Debe conservar

```text
- distancia al prior close;
- distancia a session open;
- posición dentro del rango conocido;
- distancia a máximo y mínimo conocidos hasta t;
- distancia a VWAP disponible hasta t;
- distancia a referencias premarket disponibles;
- edad y estado de cada referencia;
- cambio de localización.
```

### Regla causal esencial

Antes de que finalice el premarket no existe legalmente:

```text
final_premarket_high
```

Existe:

```text
running_premarket_high_as_of_t
```

Después de la apertura puede congelarse:

```text
premarket_high_final
```

porque entonces ya pertenece al pasado observable.

Lo mismo ocurre con:

```text
HOD
LOD
session range
VWAP
```

Deben ser siempre:

```text
as_of_t
```

Nunca máximos o mínimos finales obtenidos retrospectivamente.

### No debe representar

```text
flag
broken flag
cup and handle
Gap and Go
VWAP reclaim
PMH breakout
```

Esos son:

* Event Types;
* patrones;
* interpretaciones de consumidores;
* combinaciones de varios objetos.

No son el significado estable de `Price Location / Structure`.

---

# 7. Conditional Context

## 7.1 Fundamental Context

```text
REPRESENTATION MODEL CANDIDATE
PIT STRUCTURAL SCALE AND ELIGIBILITY CONTEXT
```

Debe conservar:

```text
- identidad del instrumento;
- security type;
- listing status;
- shares outstanding conocidas as-of;
- float conocido as-of, si la fuente es fiable;
- market capitalization calculable as-of;
- vigencia;
- fuente;
- available_at;
- edad de la observación.
```

Su función principal seguirá siendo:

```text
Universe Resolver
+
estratificación científica
```

No debe transformarse en un predicado obligatorio del detector salvo que el Universe Contract así lo determine.

---

## 7.2 News / Catalyst Context

```text
REPRESENTATION MODEL CANDIDATE
AVAILABILITY-AWARE CATALYST EVENT CONTEXT
```

Debe conservar:

```text
- noticia observable: yes / no / unknown;
- published_at;
- available_at;
- fuente;
- versión;
- relación con el instrumento;
- categoría;
- antigüedad;
- cobertura de la fuente.
```

Debe distinguir:

```text
NO_NEWS_OBSERVED
```

de:

```text
NEWS_COVERAGE_UNAVAILABLE
```

No recomiendo introducir todavía como dimensión canónica:

```text
sentiment score
good news / bad news
LLM-derived catalyst quality
```

Eso exigiría otro proceso de validación y podría introducir una interpretación mucho más inestable que la mera existencia, disponibilidad y categoría del evento.

---

## 7.3 Halt Context

```text
REPRESENTATION MODEL CANDIDATE
INSTITUTIONAL CONTINUITY STATE MACHINE
```

Estados candidatos:

```text
NORMAL_TRADING
HALT_ANNOUNCED
HALTED
RESUMPTION_INDICATED
REOPENED
POST_HALT_TRANSITION
UNKNOWN_OR_UNAVAILABLE
```

Debe conservar:

```text
- reason code;
- event timestamp;
- observed_at;
- available_at;
- duración;
- fuente;
- cambios de continuidad antes y después.
```

Aquí un modelo de máquina de estados es más apropiado que una colección desordenada de indicadores, porque el fenómeno posee transiciones institucionales discretas.

---

# 8. Deferred Extension: Order Flow Pressure

```text
REPRESENTATION MODEL CANDIDATE
SIGNED FLOW–PRICE CONVERSION
WITH CLASSIFICATION CONFIDENCE
```

### Debe conservar en el futuro

```text
- flujo firmado;
- persistencia de la presión;
- intensidad;
- trade/quote alignment;
- conversión del flujo en desplazamiento;
- divergencia entre esfuerzo y progreso;
- confianza de clasificación;
- cobertura clasificable.
```

Cont, Kukanov y Stoikov muestran que el desequilibrio de eventos en bid y ask posee una relación más robusta con cambios cortos de precio que el volumen bruto, con una sensibilidad relacionada inversamente con la profundidad. ([OUP Academic][6])

Pero clasificar trades como compradores o vendedores no es trivial. Lee y Ready documentan problemas cuando las quotes aparecen registradas antes que los trades que las provocaron o cuando una operación ocurre dentro del spread; pruebas posteriores también encuentran una precisión inferior a la esperada en diferentes algoritmos de clasificación. ([EconPapers][10])

Por eso es correcto conservarlo como extensión diferida.

Además:

```text
quote-based OFI
```

y:

```text
trade-aggressor imbalance
```

no deben tratarse como la misma cosa.

El primero puede inferirse parcialmente de cambios observados en bid/ask y tamaños. El segundo necesita una clasificación fiable del lado agresor.

---

# 9. Resumen de los modelos candidatos

| Information Object          | Representation Model candidato                                |
| --------------------------- | ------------------------------------------------------------- |
| Trading Activity            | `Baseline-Relative Marked Activity Process`                   |
| Market Microstructure State | `Observed Trade–Quote Event Coupling State`                   |
| Price Movement              | `Signed Multiscale Price-Path Response`                       |
| Liquidity                   | `Observable Top-of-Book Liquidity and Resilience State`       |
| Volatility / Range State    | `Unsigned Multiscale Variation and Range-Expansion State`     |
| Price Location / Structure  | `Causal Anchor-Relative Location State`                       |
| Fundamental Context         | `PIT Structural Scale and Eligibility Context`                |
| News / Catalyst Context     | `Availability-Aware Catalyst Event Context`                   |
| Halt Context                | `Institutional Continuity State Machine`                      |
| Order Flow Pressure         | `Signed Flow–Price Conversion with Classification Confidence` |

Esta lista define **dimensiones conceptuales**. Todavía no define:

```text
ventanas
fórmulas
thresholds
z-scores
percentiles
features
columnas
tablas
detector
```

---

# 10. Cómo demostrar científicamente “este modelo y no otro”

La selección tiene que hacerse mediante dos tipos de criterios.

## A. Gates obligatorios

Un modelo se rechaza inmediatamente si falla cualquiera de estos gates:

```text
GATE 1 — SEMANTIC COVERAGE
¿Representa todo el significado requerido por el objeto?

GATE 2 — SEMANTIC BOUNDARY
¿Evita apropiarse del significado de otros objetos?

GATE 3 — CAUSAL LEGALITY
¿Puede calcularse exclusivamente con información disponible en t?

GATE 4 — SOURCE OBSERVABILITY
¿Los datos físicos disponibles permiten observar lo que afirma representar?

GATE 5 — PROFILE COMPATIBILITY
¿Responde a la pregunta de Wake-up y no a una pregunta downstream distinta?

GATE 6 — MISSINGNESS SEMANTICS
¿Distingue cero, ausencia observable, stale y unavailable?

GATE 7 — REPRODUCIBILITY
¿Puede versionarse y reconstruirse de forma determinista?
```

Ejemplos de rechazo directo:

```text
final HOD usado antes del cierre
→ FAIL CAUSAL LEGALITY

full order-book elasticity sin datos full-book
→ FAIL SOURCE OBSERVABILITY

coste para una orden de 20.000 acciones
en el perfil Wake-up
→ FAIL PROFILE COMPATIBILITY

volume usado como representación completa de Liquidity
→ FAIL SEMANTIC COVERAGE
```

## B. Comparación experimental entre modelos que superan los gates

Después pueden competir modelos alternativos.

Por ejemplo, para `Trading Activity`:

```text
MODEL A
windowed counts and volumes

MODEL B
baseline-relative multihorizon intensity

MODEL C
conditional marked point-process representation
```

Se comparan manteniendo fijo un presupuesto de falsas alarmas.

La decisión no debería ser:

```text
gana el que tenga mayor accuracy
```

Debe ser:

```text
dado el mismo presupuesto de falsas activaciones:

- cuál detecta antes;
- cuál pierde menos episodios;
- cuál es más estable;
- cuál funciona en más estratos;
- cuál depende menos de supuestos frágiles;
- cuál conserva mejor la semántica;
- cuál es más sencillo si el rendimiento es equivalente.
```

La literatura de detección secuencial utiliza precisamente este compromiso entre retardo y falsas alarmas. ([Project Euclid][2])

---

# 11. Batería mínima de validación

## 11.1 Validez semántica

Para cada dimensión:

```text
¿Qué parte exacta de la pregunta semántica representa?

¿Qué caso real dejaría invisible si la eliminamos?

¿En qué otro objeto debería vivir si no pertenece aquí?
```

## 11.2 Validez convergente

Dos medidas distintas de una misma dimensión deberían comportarse coherentemente.

Ejemplo:

```text
Trading Activity intensity:

- trades per second
- inverse mean duration
- conditional event intensity
```

No tienen que ser idénticas, pero deberían coincidir razonablemente en los casos de activación intensa.

## 11.3 Validez discriminante

Objetos distintos no deberían colapsar en la misma medida.

Ejemplo:

```text
alto Trading Activity
no implica necesariamente
alta Liquidity

alta Volatility
no implica necesariamente
Price Movement direccional eficiente
```

## 11.4 Casos positivos y negativos conocidos

La batería debería contener como mínimo:

```text
A. Dormancy → burst genuino y persistente
   similar a SGN

B. Régimen previamente activo → nueva aceleración
   similar a LIDR

C. Un único print extremo

D. Corrección o trade fuera de secuencia

E. Quote flicker sin trades

F. Mucho volumen sin desplazamiento

G. Desplazamiento de last trade sin respuesta del midprice

H. Apertura regular con actividad estacional esperable

I. Halt y resumption

J. Datos ausentes o quotes stale
```

## 11.5 Robustez por estratos

Debe comprobarse separadamente por:

```text
- precio;
- market cap;
- actividad histórica;
- premarket;
- regular session;
- after-hours;
- exchange;
- nivel de cobertura;
- presencia o ausencia de noticia;
- días con y sin halt.
```

No debe suponerse que una intensidad o un spread bruto posee el mismo significado en todos esos grupos. La evidencia específica de small caps y de periodicidad intradía justifica esta estratificación. ([SEC][11])

## 11.6 Ablation

Para cada dimensión:

```text
modelo completo
versus
modelo sin esa dimensión
```

Ejemplos:

```text
sin absolute materiality
sin baseline-relative surprise
sin event duration
sin quote response
sin resilience
```

Pero la ablation no debe utilizarse solamente para maximizar un clasificador. También debe comprobarse que, al eliminar una dimensión, se pierde justamente el tipo de significado que esa dimensión debía conservar.

## 11.7 Generalización temporal

La selección debe realizarse fuera de muestra:

```text
development period
validation period
final untouched test period
```

Y separando episodios del mismo ticker cuando exista riesgo de memorizar su comportamiento recurrente.

---

# 12. Métricas correctas para Wake-up

La representación no debe validarse únicamente sobre una colección de gráficos positivos.

Tu propio contrato ya exige conservar el denominador de exposición y comparar contra el scanner de 500.000 acciones. 

Las métricas mínimas serían:

```text
FALSE ACTIVATIONS
- falsas activaciones por millón de symbol-seconds elegibles
- falsas activaciones por sesión
- carga media y p95 de alertas diarias

DETECTION
- episodios detectados
- episodios omitidos
- detection delay
- p50, p90 y worst-case delay

EARLINESS
- segundos/minutos antes del scanner 500k
- casos detectados solamente por Wake-up
- casos detectados solamente por el scanner

STABILITY
- estabilidad por precio
- market cap
- sesión
- año
- disponibilidad de quotes

PERSISTENCE
- activaciones que desaparecen inmediatamente
- activaciones que generan un Episode Instance sostenible

DATA ADEQUACY
- porcentaje de estados representables
- unavailable
- degraded
- stale
```

El scanner de 500.000 acciones es:

```text
BENCHMARK
```

No:

```text
GROUND TRUTH
```

De lo contrario, el nuevo detector simplemente aprendería a reproducir un umbral que precisamente intentas superar.

---

# 13. Regla determinista de admisión

Esta puede ser la regla institucional:

```text
A Representation Model será ADMITTED para el perfil Wake-up
solamente cuando:

1. cubra el significado requerido por el Information Object;

2. mantenga fronteras discriminantes frente a los demás objetos;

3. sea observable con los datos realmente disponibles;

4. sea causalmente construible en cada decision_timestamp;

5. diferencie zero, absent, stale y unavailable;

6. supere los casos de validación conocidos;

7. sea robusto entre los estratos preregistrados;

8. aporte información no redundante respecto al modelo mínimo;

9. alcance el presupuesto de falsas alarmas establecido;

10. sea no inferior o superior a los modelos alternativos
    en detección fuera de muestra;

11. y, en caso de equivalencia,
    sea seleccionado el modelo más simple.
```

En forma compacta:

```text
ADMIT(M)
=
HARD_GATES_PASS
AND
OUT_OF_SAMPLE_VALIDITY_PASS
AND
FALSE_ALARM_BUDGET_PASS
AND
NON_INFERIORITY_PASS
AND
PARSIMONY_TIE_BREAK_PASS
```

Esa es la fuente real de determinismo.

No:

```text
“un paper utilizó esta variable”
```

sino:

```text
“la literatura justifica esta dimensión;
nuestros datos permiten observarla;
el modelo supera los gates semánticos;
y el experimento preregistrado demuestra
que es preferible a sus alternativas”.
```

---

# Conclusión

La decisión provisional más defendible para `Wake-up` es una representación:

```text
DYNAMIC
porque Wake-up es una transición.

BASELINE-RELATIVE
porque cada instrumento posee un régimen previo diferente.

ABSOLUTE-AND-RELATIVE
porque una sorpresa enorme puede ser económicamente microscópica.

MULTISCALE
porque SGN y LIDR despiertan con velocidades diferentes.

EVENT-AWARE
porque trades y quotes llegan irregularmente.

CROSS-CONFIRMED
porque un único print no demuestra activación real.

SESSION-AWARE
porque premarket y sesión regular no son regímenes equivalentes.

CAUSAL
porque solo puede utilizar información disponible hasta t.

PROFILE-SCOPED
porque el modelo de Liquidity para Wake-up
no es el mismo que el modelo de Liquidity para ejecución.
```

Y hay una última frontera que debe permanecer congelada:

```text
PROFILE MEMBERSHIP
≠
MANDATORY DETECTOR PREDICATE
```

El hecho de que `Price Movement` o `Liquidity` pertenezcan al perfil no obliga todavía a que el detector exija movimiento de precio o una condición mínima de liquidez para emitir `Wake-up`. Esa decisión pertenece a la futura experimentación del detector, no a la admisión semántica de los objetos. 

El siguiente artefacto correcto es:

```text
WAKE_UP_REPRESENTATION_MODEL_ADMISSION_PLAN_v0_1.md
```

y el primer objeto que debería atravesar el proceso completo es:

```text
Trading Activity
```

comparando formalmente:

```text
A. Windowed Raw Activity
B. Baseline-Relative Multiscale Activity
C. Conditional Marked Event-Intensity Activity
```

sin definir todavía el detector final ni convertir ninguna feature concreta en autoridad canónica.

# Gate obligatorio de herencia de incidentes de materializacion

Antes de autorizar una materializacion larga, cada modelo debe cumplir
`REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md`
y declarar una matriz `inherited_incident_controls`.

La matriz debe incluir, como minimo:

```text
control_id
source_incident_id
applicability
implementation_reference
regression_test_reference
all_shard_probe_evidence
terminal_rehearsal_evidence
status
```

Los controles vigentes `RM-MAT-CTRL-001..005` obligan a separar metadata de
conteos físicos, seleccionar targets por pertenencia exacta, compartir una
única autoridad de cardinalidad, demostrar el dominio de cualquier ordinal
usado como identidad y aislar ficheros Parquet explícitos de inferencia Hive no
intencional. `PENDING`, `FAIL` u omisión bloquean la materialización.

Cada fallo nuevo debe registrarse antes de corregirse, verificarse en todos los
shards y convertirse en un control evaluado por los siguientes modelos. La
finalizacion del calculo no sustituye la certificacion terminal.

[1]: https://meehl.umn.edu/sites/meehl.umn.edu/files/files/036constructvalidityidx.pdf "https://meehl.umn.edu/sites/meehl.umn.edu/files/files/036constructvalidityidx.pdf"
[2]: https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-42/issue-6/Procedures-for-Reacting-to-a-Change-in-Distribution/10.1214/aoms/1177693055.short "https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-42/issue-6/Procedures-for-Reacting-to-a-Change-in-Distribution/10.1214/aoms/1177693055.short"
[3]: https://econpapers.repec.org/RePEc%3Aecm%3Aemetrp%3Av%3A66%3Ay%3A1998%3Ai%3A5%3Ap%3A1127-1162 "https://econpapers.repec.org/RePEc%3Aecm%3Aemetrp%3Av%3A66%3Ay%3A1998%3Ai%3A5%3Ap%3A1127-1162"
[4]: https://www.sciencedirect.com/science/article/pii/S0927539897000042 "https://www.sciencedirect.com/science/article/pii/S0927539897000042"
[5]: https://econpapers.repec.org/RePEc%3Abla%3Ajfinan%3Av%3A46%3Ay%3A1991%3Ai%3A1%3Ap%3A179-207 "https://econpapers.repec.org/RePEc%3Abla%3Ajfinan%3Av%3A46%3Ay%3A1991%3Ai%3A1%3Ap%3A179-207"
[6]: https://academic.oup.com/jfec/article/12/1/47/816163 "https://academic.oup.com/jfec/article/12/1/47/816163"
[7]: https://academic.oup.com/rfs/article-abstract/18/2/351/1599888 "https://academic.oup.com/rfs/article-abstract/18/2/351/1599888"
[8]: https://people.duke.edu/~qc2/BA532/1985%20EMA%20Kyle.pdf "https://people.duke.edu/~qc2/BA532/1985%20EMA%20Kyle.pdf"
[9]: https://academic.oup.com/jfec/article-abstract/2/1/1/960705 "https://academic.oup.com/jfec/article-abstract/2/1/1/960705"
[10]: https://econpapers.repec.org/RePEc%3Abla%3Ajfinan%3Av%3A46%3Ay%3A1991%3Ai%3A2%3Ap%3A733-46 "https://econpapers.repec.org/RePEc%3Abla%3Ajfinan%3Av%3A46%3Ay%3A1991%3Ai%3A2%3Ap%3A733-46"
[11]: https://www.sec.gov/marketstructure/research/small_cap_liquidity.pdf "https://www.sec.gov/marketstructure/research/small_cap_liquidity.pdf"
