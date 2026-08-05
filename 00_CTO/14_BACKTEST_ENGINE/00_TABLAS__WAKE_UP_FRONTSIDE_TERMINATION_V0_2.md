# TSIS · Reconstrucción integral del proceso científico y arquitectónico  
## Wake-up Event + Frontside Termination Event

```text
DOCUMENT_ROLE
=
PROPOSED_INTEGRATED_ARCHITECTURE
+
SCIENTIFIC_WORKFLOW_BLUEPRINT
+
PEDAGOGICAL_VERTICAL_SLICE

EXECUTABLE_AUTHORITY
=
NO

IMPORTANT
=
Los nombres de perfiles, Event Types, contratos y artefactos propuestos
en este documento son CANDIDATOS hasta que pasen por la gobernanza viva de TSIS.

El estado de gates, perfiles admitidos, datasets oficiales y autorizaciones
NO debe deducirse de este documento.
Debe resolverse siempre desde:
- Gate Register vigente
- readouts aceptados
- registries vivos
- profile manifests
- 99_ruta_de_trabajo.md
- contratos especializados aplicables
```

---

# 0. Propósito

Este documento reconstruye, de principio a fin, cómo debería abordarse en TSIS el estudio científico de dos fenómenos relacionados del episodio frontside en microcaps y smallcaps:

```text
1. Wake-up Event
   ¿Cuándo deja un ticker de estar dormido?

2. Frontside Termination Event
   ¿Cuándo empieza a deteriorarse el régimen comprador
   y aumenta materialmente el riesgo de backside?
```

El objetivo no es construir inmediatamente una estrategia rentable.

El objetivo inicial es entender y materializar correctamente esta cadena:

```text
PREGUNTA CIENTÍFICA
↓
NECESIDADES DE INFORMACIÓN
↓
INFORMATION OBJECTS
↓
MODELOS DE REPRESENTACIÓN
↓
FEATURES / VARIABLES
↓
FUENTES FÍSICAS
↓
MARKET STATE
↓
DETECTOR
↓
EVENT INSTANCE
↓
EPISODE INSTANCE
↓
EVENT STATE, si es necesario
↓
OUTCOMES SEPARADOS
↓
EVALUACIÓN DEL DETECTOR
↓
POLÍTICAS
↓
BACKTEST
↓
VALIDACIÓN CIENTÍFICA
```

---

# 1. Rectificación de la premisa inicial

## 1.1 Lo que NO debe construirse

No debe plantearse así:

```text
wake_up_event
→ su propia market_state_table

frontside_termination_event
→ otra market_state_table
```

Tampoco debe plantearse así:

```text
una megatabla física universal
con todas las variables posibles
para todos los tickers
en todos los timestamps
```

## 1.2 La premisa correcta

La arquitectura correcta es:

```text
UNA SEMÁNTICA CANÓNICA DE MARKET STATE
+
UN IDENTIFICADOR LÓGICO COMÚN
+
UN CORE COMPARTIDO
+
EXTENSIONES FÍSICAS SEGÚN PERFIL, COSTE Y COBERTURA
```

Conceptualmente:

```text
Market State
=
¿Qué sabía TSIS sobre este instrumento
en este decision_timestamp?
```

Físicamente puede materializarse mediante perfiles compatibles:

```text
market_state_core_light
market_state_wakeup_extension
market_state_active_episode_extension
market_state_price_structure_extension
market_state_news_extension
```

Todos deben vincularse mediante identidades y reglas comunes como:

```text
market_state_id
instrument_id
decision_timestamp
state_available_at
representation_profile_version
```

La fórmula fundamental es:

```text
Canonicalidad
=
misma semántica,
mismas reglas temporales,
misma identidad lógica.

Materialización
=
cuándo,
dónde,
con qué cobertura,
con qué resolución,
y con qué extensiones
se representa esa semántica.
```

---

# 2. La imagen mental que debe conservarse

Para entender el sistema, conviene imaginar siete cuadernos separados.

---

## 2.1 Cuaderno 1 · Hechos físicos observados

Contiene lo que realmente llega desde las fuentes:

```text
trades
quotes
OHLCV
news
filings
halts
reference data
fundamentals
short-side context
corporate actions
```

Ejemplo ilustrativo:

```text
09:42:08.247
TRADE XYZ
price = 3.21
size = 2,500

09:42:08.251
QUOTE XYZ
bid = 3.20
ask = 3.23
bid_size = ...
ask_size = ...
```

Estos son hechos fuente.

Todavía no son Market State.

---

## 2.2 Cuaderno 2 · Market State

Market State responde:

```text
¿Qué información observable y legalmente disponible
tenía TSIS sobre XYZ en t?
```

Ejemplo conceptual:

```text
market_state_id
instrument_id
decision_timestamp
state_as_of_utc
state_available_at_utc

trade_rate_1s
trade_rate_5s
dollar_volume_rate_5s
mid_return_5s
spread_bps
quote_age_ms
order_flow_imbalance
distance_to_hod
```

Market State no escribe:

```text
esto es Wake-up
esto es una entrada
esto es el top
hay que comprar
hay que vender
```

Market State describe.

No decide.

---

## 2.3 Cuaderno 3 · Detector / Tracker

Un detector consume una secuencia de Market States.

Ejemplo:

```text
MS(t-5s)
MS(t-4s)
MS(t-3s)
MS(t-2s)
MS(t-1s)
MS(t)
```

Y evalúa una hipótesis.

Ejemplos:

```text
Wake-up Detector
Frontside Phase Tracker
Termination Hazard Model
Backside Confirmation Detector
```

El detector no es Market State.

El detector interpreta Market State.

---

## 2.4 Cuaderno 4 · Event Instance

Cuando un detector supera su contrato, crea un evento.

Ejemplo:

```text
Wake-up detectado
```

o:

```text
Frontside Termination Risk High
```

Ejemplo conceptual:

```text
event_instance_id
event_type_id
instrument_id
event_occurred_at
event_detected_at
event_available_at
detector_version
```

El orden causal correcto es:

```text
Market State
↓
Detector
↓
Event Instance
```

Nunca:

```text
Event Instance
↓
Detector
```

---

## 2.5 Cuaderno 5 · Episode Instance

Wake-up no es sólo una alerta.

Wake-up inicia un episodio de mercado.

```text
Wake-up Event
↓
Episode Instance
```

La entidad `episode_instance_id` es central.

Debe permitir conservar:

```text
instrument_id
episode_started_by_event_id
episode_onset_at
episode_detected_at
episode_available_at
episode_status
current_phase
activation_price
activation_vwap
episode_hod
episode_lod
number_of_bursts
number_of_halts
last_activity_at
expiry_rule
close_reason
```

El episodio organiza:

```text
Wake-up
↓
Impulse
↓
Pullback
↓
Continuation
↓
Stress
↓
Termination Warning
↓
Termination Detected
↓
Backside Confirmed
↓
Episode End
```

Sin `episode_instance_id` sería difícil determinar:

```text
qué movimientos pertenecen al mismo frontside;
si un segundo burst es continuación o un nuevo episodio;
qué HOD pertenece al episodio;
qué activation VWAP debe utilizarse;
cuándo retirar el ticker del Active Symbol Set;
cómo deduplicar eventos;
cómo agrupar train/test sin dividir el mismo episodio.
```

---

## 2.6 Cuaderno 6 · Event State

Event State contextualiza Market State respecto a un Event Instance.

Ejemplo:

```text
Wake-up E123

09:41:48 → pre_event
09:42:03 → pre_event
09:42:08 → at_event
09:42:13 → post_event
```

Añade relaciones como:

```text
event_instance_id
episode_instance_id
market_state_id
state_role
relative_time_to_event
consumption_legality
```

Pero Event State no tiene por qué ser una dependencia obligatoria del tracker en tiempo real.

El runtime puede operar así:

```text
Wake-up Event
↓
Episode Memory en RAM
↓
secuencia de Market States
↓
Frontside Tracker
```

Mientras Event State puede materializarse para:

```text
investigación;
comparación entre episodios;
datasets de ML;
replay gobernado;
auditoría;
ventanas pre/at/post;
análisis de patrones.
```

---

## 2.7 Cuaderno 7 · Outcomes

Outcomes conserva lo que ocurrió después.

Ejemplos:

```text
nuevo HOD;
drawdown del 5%;
drawdown del 10%;
tiempo hasta el máximo;
frontside peak retrospectivo;
reversión completa;
backside confirmado;
MFE;
MAE.
```

La frontera sagrada es:

```text
X
=
Market State,
Event State decision-safe,
contexto observable legalmente en t.

Y
=
Outcomes,
labels,
rewards,
futuro posterior al cutoff.
```

Nunca debe existir:

```text
Y
→ detector
→ estrategia
```

---

# 3. Un programa científico padre, no una única hipótesis gigante

No conviene construir un único Scientific Problem Contract que mezcle Wake-up y Termination.

Debe existir un programa padre:

```text
MICROCAP_MARKET_EPISODE_RESEARCH_PROGRAM
```

Y debajo, como mínimo, dos experimentos separados.

---

## 3.1 Experimento A

```text
WAKE_UP_DETECTION_EXPERIMENT
```

Pregunta:

```text
¿Puede TSIS detectar que una microcap ha dejado
el régimen dormido antes que el scanner acumulativo
de 500.000 acciones, manteniendo controladas
las falsas alertas y preservando operabilidad?
```

---

## 3.2 Experimento B

```text
FRONTSIDE_TERMINATION_EXPERIMENT
```

Pregunta:

```text
Dentro de episodios frontside ya activados,
¿aporta la microestructura información incremental
sobre el riesgo de drawdown antes de un nuevo HOD?
```

---

## 3.3 Contratos compartidos

Ambos experimentos pueden reutilizar:

```text
Shared Universe Contract
Shared Point-in-Time Policy
Shared Market State Semantics
Shared Source Admissibility
Shared Episode Representation Contract
Shared Feature Lineage Rules
Shared Quality Policy
```

Pero no deben compartir forzosamente:

```text
hipótesis;
baseline;
población;
outcomes;
métricas;
falsación;
modelo;
umbral de decisión.
```

---

# 4. Arquitectura física Light / Heavy

## 4.1 Problema de coste

No es razonable calcular permanentemente para miles de símbolos:

```text
bid resilience
ask absorption
impact asymmetry
high acceptance
episode-relative burst renewal
historical resistance clusters
```

con el mismo coste que:

```text
trade_count_1s
dollar_volume_5s
last_price
best_bid
best_ask
spread
```

Por tanto, la arquitectura debe ser escalonada.

---

## 4.2 Market State Core / Light

Se calcula para todo el universo elegible.

Variables candidatas de bajo coste:

```text
last_trade_price
best_bid
best_ask
spread_bps
quote_age_ms
trade_count_1s
trade_count_5s
shares_1s
shares_5s
dollar_volume_1s
dollar_volume_5s
mid_return_1s
mid_return_5s
session_hod
distance_to_hod
```

Su misión es:

```text
detectar actividad anormal;
mantener el universo observable;
alimentar Wake-up;
no saturar el sistema.
```

---

## 4.3 Ring Buffer pre-event

Aunque la microestructura pesada se active después del Wake-up, necesitamos conservar el pasado inmediato.

Para todo el universo elegible debe existir un buffer corto de hechos fuente:

```text
RAW EVENT RING BUFFER
=
últimos N segundos/minutos
de trades y quotes
por instrumento
```

El valor exacto de `N` no debe fijarse aquí sin estudio.

Puede investigarse, por ejemplo:

```text
30s
60s
120s
300s
```

Cuando aparece Wake-up:

```text
1. se activa el ticker;
2. se recupera el buffer previo;
3. se reconstruyen las extensiones pesadas pre-event;
4. se continúa calculando online post-event.
```

La arquitectura correcta es:

```text
FULL UNIVERSE
↓
MARKET STATE LIGHT
+
RAW RING BUFFER
↓
WAKE-UP
↓
ACTIVE SYMBOL
↓
HEAVY PRE-EVENT BACKFILL
+
HEAVY ONLINE CONTINUATION
```

Sin este buffer perderíamos la transición:

```text
dormido
→ preactivación
→ activación
```

---

## 4.4 Active-Episode Heavy Extension

Sólo se habilita para tickers despertados o autorizados.

Puede incluir, si las fuentes lo permiten:

```text
order-flow imbalance
aggressor-side proxies
interarrival collapse
venue breadth
trade-size concentration
bid resilience
ask replenishment
ask absorption proxy
buy response
sell response
impact asymmetry
high acceptance
burst renewal
directional efficiency
overhead density
resistance clusters
event-relative features
```

---

# 5. Timestamps que no deben confundirse

## 5.1 Market State

```text
decision_timestamp
=
instante que el estado representa.

state_as_of_utc
=
máximo timestamp de información fuente incorporada.

state_available_at_utc
=
primer instante legal en que el consumidor
puede recibir ese estado.
```

---

## 5.2 Event Instance

```text
event_occurred_at
=
instante asignado al fenómeno o evidencia base.

event_detected_at
=
instante en que el detector completó su decisión.

event_available_at
=
primer instante legal en que el evento
puede entregarse a consumidores.
```

---

## 5.3 Episode Instance

Debe distinguir:

```text
episode_onset_at
=
instante retrospectivo o estimado
en que comenzó la activación.

episode_detected_at
=
instante en que Wake-up reconoció el episodio.

episode_available_at
=
primer instante legal en que el episodio
existe para consumidores.
```

Ejemplo ilustrativo:

```text
09:42:07.850  episode_onset_at
09:42:08.300  episode_detected_at
09:42:08.310  episode_available_at
```

El episodio puede referenciar un comienzo anterior.

Pero no puede consumirse antes de `episode_available_at`.

---

# 6. Dos tipos de run que deben permanecer separados

Ésta es una de las fronteras más importantes.

---

## 6.1 Detector Research Run

Objetivo:

```text
descubrir,
construir,
evaluar o falsar
un detector de eventos.
```

Ejemplo:

```text
Wake-up Detector Research Run
```

Inputs permitidos:

```text
trades
quotes
Market State observable
contexto point-in-time
```

Output del run:

```text
Wake-up Event Instances generados durante el replay
```

Regla crítica:

```text
Un Detector Research Run
NO puede consumir como input
el mismo Event Type que está intentando generar.
```

No puede ocurrir:

```text
Wake-up Event precomputado
→ Wake-up Detector candidato
```

porque sería circular.

La cadena correcta es:

```text
Market State
↓
Detector candidato
↓
Event Instance generado
↓
evaluación contra Outcomes
```

---

## 6.2 Policy Backtest Run

Objetivo:

```text
evaluar una política
que consume un detector ya congelado.
```

Ejemplo:

```text
Long Entry Policy
Long Exit Policy
Backside Entry Policy
```

El detector debe estar:

```text
versionado;
congelado;
temporalmente validado;
identificado en manifest;
autorizado para el scope del run.
```

Existen dos opciones válidas.

### Opción A · Regeneración causal

```text
Market State
↓
Detector congelado v1.0
↓
Event Instance
↓
Policy
```

### Opción B · Consumo de eventos precomputados

```text
Event Instances precomputados
+
detector_version exacta
+
available_at reproducible
+
manifest y hashes
↓
Policy
```

Ambas deben producir una semántica equivalente dentro del alcance demostrado.

Por tanto:

```text
DETECTOR RESEARCH RUN
≠
POLICY BACKTEST RUN
```

---

## 6.3 Event-State Research Run

Puede existir un tercer modo:

```text
EVENT-STATE RESEARCH RUN
```

Su objetivo es:

```text
construir ventanas pre/at/post;
comparar episodios;
preparar datasets de ML;
analizar trayectorias;
no ejecutar una política.
```

Puede consumir:

```text
Event Instances congelados
Market States
Episode Instances
Outcomes research-only
```

---

# 7. Arquitectura causal completa

```text
UNIVERSO ELEGIBLE PIT
        ↓
HECHOS FUENTE
trades · quotes · bars · news · halts
        ↓
MARKET STATE CORE / LIGHT
        ↓
WAKE-UP DETECTOR
        ↓
WAKE-UP EVENT INSTANCE
        ↓
EPISODE INSTANCE
        ↓
ACTIVE SYMBOL REGISTRY
        ↓
BACKFILL DESDE RING BUFFER
        ↓
MARKET STATE HEAVY EXTENSIONS
        ↓
TRADABLE IN-PLAY CLASSIFIER
        ↓
FRONTSIDE PHASE TRACKER
        ↓
TERMINATION HAZARD MODEL
        ↓
TERMINATION EVENT INSTANCE
        ↓
BACKSIDE CONFIRMATION
        ↓
EPISODE END
```

En paralelo:

```text
FUTURO OBSERVADO
        ↓
OUTCOME ENGINE
        ├── frontside peak retrospectivo
        ├── drawdown D × H
        ├── nuevo HOD
        ├── recuperación
        ├── reversión completa
        └── backside outcomes
```

Y después:

```text
ESTADOS + EVENTOS + EPISODIO
        ↓
POLÍTICAS
        ├── long entry
        ├── long add/reduce
        ├── long exit
        ├── short entry
        ├── short add/reduce
        └── cover
```

---

# 8. Caso A completo · Wake-up

## 8.1 Pregunta científica

> ¿Puede una combinación point-in-time de sorpresa de actividad, actividad absoluta, respuesta direccional y liquidez detectar que una microcap ha pasado de régimen dormido a actividad anormal antes que el scanner acumulativo de 500.000 acciones, manteniendo una tasa de falsas alertas compatible con la operación?

---

## 8.2 Hipótesis

```text
H0
=
trades, quotes, precio y liquidez
no mejoran de forma estable
al scanner actual.

H1
=
permiten detectar antes
sin superar el presupuesto de falsas alertas
y preservando una operabilidad mínima.
```

---

## 8.3 Baseline

```text
scanner clásico
=
market cap < límite
+
last price < límite
+
session volume >= 500,000 shares
```

El baseline debe conservarse.

No debe eliminarse para hacer quedar bien al nuevo detector.

---

## 8.4 Criterios de fracaso

El detector fracasa si:

```text
produce demasiadas alertas;
reacciona a un único print;
detecta tickers inoperables;
llega cuando el movimiento ya recorrió casi todo;
solo funciona con un umbral exacto;
no mejora fuera de muestra;
depende de información posterior;
su ventaja desaparece con costes o latencia razonables.
```

---

## 8.5 Necesidades de información

| Pregunta | Necesidad |
|---|---|
| ¿Ha dejado de estar dormido? | Sorpresa de actividad |
| ¿Es actividad real? | Persistencia, amplitud y concentración |
| ¿La actividad mueve el mercado? | Conversión direccional |
| ¿Es observablemente negociable? | Spread, quote quality y capacidad |
| ¿El cambio se mantiene? | Persistencia y aceptación |
| ¿Existe una causa externa? | News, filings y halts disponibles en t |

---

## 8.6 Information Objects

```text
Trading Activity
Price Movement
Liquidity
Market Microstructure State
Order Flow Pressure
Price Location / Structure
Volatility / Range State
News Catalyst Context
Fundamental Context
Halt Context
```

No debe crearse un Information Object llamado:

```text
WakeUp
```

Wake-up es un Event Type candidato.

---

## 8.7 Modelos de representación

### Trading Activity

```text
trade intensity
dollar-volume rate
interarrival collapse
venue breadth
trade-size concentration
```

Variables candidatas:

```text
trade_rate_1s
trade_rate_5s
dollar_volume_rate_5s
interarrival_collapse_20trades
venue_breadth_5s
largest_trade_share_5s
```

### Liquidity

```text
coste observable de inmediatez
quote availability
observable capacity
depletion
replenishment
```

Variables candidatas:

```text
spread_bps
quote_age_ms
bid_notional
ask_notional
target_order_capacity_ratio
bid_replenishment_rate
ask_replenishment_rate
```

### Price Movement

```text
mid return
velocity
acceleration
directional efficiency
price response
```

### Order Flow Pressure

```text
signed dollar imbalance
OFI
aggressor-side proxies
buy/sell intensity
```

---

## 8.8 Source Admissibility

Antes de implementar cualquier feature debe demostrarse:

```text
dataset autoritativo;
columnas exactas;
timestamp autoritativo;
sequence;
timezone;
trade conditions;
corrections/cancellations;
premarket coverage;
NBBO o venue-level quotes;
quote staleness;
symbol mapping;
available-at rule.
```

La existencia física de una carpeta no demuestra admisibilidad.

---

## 8.9 Feature Specification

Ejemplo:

```text
feature_id
=
trade_rate_5s

information_object
=
Trading Activity

formula
=
count(eligible trades in (t-5s, t])

source
=
governed trades dataset

cutoff
=
solo eventos disponibles en t

state_available_at_rule
=
max(input_available_at)
+
builder_publication_latency

quality rules
=
excluir trades cancelados,
corregidos o no elegibles

lineage
=
dataset_id
+
schema_version
+
builder_version
```

---

## 8.10 Wake-up Detector

El detector observa una secuencia de estados.

Puede organizar su evidencia como:

```text
A = Activity Surprise
L = Liquidity
D = Directional Conversion
P = Persistence / Acceptance
```

La primera salida debe ser:

```text
WATCH
```

No:

```text
BUY
```

Separación obligatoria:

```text
Wake-up Detector
→ merece observación

Tradable In-Play Classifier
→ participación real y operable

Entry Policy
→ comprar o no comprar
```

---

## 8.11 Wake-up Event Candidate

Ejemplo conceptual:

```yaml
event_instance_id: WU_XYZ_20260119_094208310
event_type_id: market_activity:wake_up_detected
instrument_id: XYZ

event_occurred_at_utc: 09:42:08.250
event_detected_at_utc: 09:42:08.300
event_available_at_utc: 09:42:08.310

detector_version: wake_up_detector_v0_1
```

Este Event Type debe pasar por:

```text
candidate definition
semantic review
admission
schema
deduplication rules
negative cases
versioning
temporal policy
registry
authorization
```

---

## 8.12 Episode Instance

```yaml
episode_instance_id: EP_XYZ_20260119_094208310
instrument_id: XYZ

episode_started_by_event_id:
  WU_XYZ_20260119_094208310

episode_onset_at:
  09:42:07.850

episode_detected_at:
  09:42:08.300

episode_available_at:
  09:42:08.310

episode_status:
  active

current_phase:
  activation
```

---

## 8.13 Event State de Wake-up

Ventanas candidatas:

```text
[-300s, -60s] = dormant baseline
[-60s, -15s]  = preactivation
[-15s, 0s]    = immediate activation
[0s, +5s]     = initial response
[0s, +15s]    = confirmation
[0s, +60s]    = impulse development
```

Precisión temporal:

```text
Market State pre-event
=
observable en su timestamp.

La relación “pre_event respecto a E123”
=
solo existe después de que E123 sea detectado.
```

Por tanto:

```text
state_role = pre_event
```

no significa:

```text
TSIS sabía entonces
que estaba antes de un evento.
```

---

# 9. Caso B completo · Frontside Termination

## 9.1 Condición de entrada al experimento

Frontside Termination no se evalúa sobre cualquier ticker.

Requiere:

```text
episode_instance_id activo
```

Y una historia mínima del episodio:

```text
Wake-up
↓
Activation
↓
Impulse
↓
Pullback / Continuation
```

---

## 9.2 Pregunta científica

> Dentro de episodios frontside ya activados, ¿aportan la pérdida de eficacia compradora, la degradación del bid, la absorción, la asimetría de impacto y la falta de aceptación de nuevos máximos información incremental sobre el riesgo de drawdown antes de un nuevo HOD?

---

## 9.3 Baseline obligatorio

```text
extensión desde prior close
hora de sesión
gap
volumen acumulado
float
market cap
duración del episodio
número de halts
```

La pregunta no es:

```text
¿los tickers muy extendidos suelen caer?
```

La pregunta es:

```text
¿la microestructura mejora
la predicción más allá
del contexto básico?
```

---

## 9.4 Necesidades de información

| Pregunta | Necesidad |
|---|---|
| ¿Las compras siguen provocando avance? | Esfuerzo comprador frente a progreso |
| ¿El ask absorbe? | Depletion y replenishment |
| ¿El bid se recupera? | Bid resilience |
| ¿Las ventas tienen más impacto? | Buy/sell impact asymmetry |
| ¿Los máximos son aceptados? | Tiempo/eventos sobre nivel |
| ¿Se renueva la participación? | Burst renewal |
| ¿Existe overhead? | Estructura histórica de precio y volumen |
| ¿El ticker suele revertir? | Historial con incertidumbre |
| ¿Apareció un evento exógeno? | News, filings y halts PIT |

---

## 9.5 Information Objects

```text
Price Movement
Trading Activity
Liquidity
Order Flow Pressure
Market Microstructure State
Price Location / Structure
News Catalyst Context
Fundamental Context
Halt Context
```

No debe crearse un Information Object llamado:

```text
Frontside Terminated
```

---

## 9.6 Features candidatas

```text
buy_response_decay
ask_absorption_proxy
bid_resilience
sell_buy_impact_asymmetry
order_flow_regime_change
high_acceptance_ratio
burst_renewal
directional_efficiency_decay
recovery_fraction_after_sell_burst
overhead_density
resistance_cluster_score
historical_reversion_posterior
```

Estas features son hipótesis.

No son señales demostradas hasta superar:

```text
physical definition
temporal validation
coverage
baseline comparison
OOS evaluation
selection-bias control
```

---

## 9.7 Frontside Phase Tracker

```text
FRONTSIDE_ACTIVE
        ↓
FRONTSIDE_STRESSED
        ├── recovery
        │      ↓
        │   FRONTSIDE_ACTIVE
        │
        ↓
TERMINATION_WARNING
        ↓
TERMINATION_RISK_HIGH
        ↓
TERMINATION_DETECTED
        ↓
BACKSIDE_CONFIRMED
```

No debe suponerse:

```text
support break
=
frontside terminated
```

El tracker debe distinguir:

```text
pullback saludable
vs
deterioro estructural.
```

---

## 9.8 Termination Hazard

El output no debe limitarse a:

```text
frontside_ended = true
```

Puede estimar:

```text
P(new HOD in 30s)
P(new HOD in 60s)
P(drawdown 5% before new HOD in 30s)
P(drawdown 10% before new HOD in 60s)
P(drawdown 15% in 5m)
P(halt before exit)
P(liquidity failure)
P(recovery)
```

---

## 9.9 Outcomes D × H

El máximo exacto es retrospectivo:

```text
frontside_peak_timestamp
=
Outcome / research label
```

No es un Event Type predictivo.

La familia candidata:

```text
D = {5%, 10%, 15%, 20%}
H = {15s, 30s, 60s, 5m, 15m, session}
```

No debe elegirse una celda porque maximice PnL.

Debe buscarse:

```text
continuidad entre vecinos
regiones estables
degradación progresiva
consistencia OOS
mejora incremental
```

---

## 9.10 Termination Event Candidate

Ejemplo:

```yaml
event_instance_id: FT_XYZ_20260119_100119250
episode_instance_id: EP_XYZ_20260119_094208310

event_type_id:
  market_episode:frontside_termination_detected

event_detected_at_utc:
  10:01:19.240

event_available_at_utc:
  10:01:19.250

detector_version:
  frontside_termination_detector_v0_1
```

Debe diferenciarse de:

```text
frontside_peak_outcome
```

---

# 10. Orden causal dentro del EventLoop

El orden exacto debe congelarse por contrato.

Conceptualmente:

```text
1. Source Market Event
   trade / quote / news / halt

2. Source Fact Update

3. Market State Available

4. Detector / Tracker Evaluation

5. Event Instance Creation

6. Episode Memory Update

7. Event State Available, si aplica

8. Classifier / Policy Decision

9. Order Intent

10. Risk / OMS

11. Execution

12. Fill / No Fill

13. Position / Ledger Update
```

Para Wake-up:

```text
Market State
→ Wake-up Detector
→ Wake-up Event
→ Episode Instance
→ In-Play Classifier
→ Entry Policy
```

Para terminación:

```text
Market State
+
Episode Memory
→ Phase Tracker
→ Termination Detector
→ Termination Event
→ Long Exit Policy
```

---

# 11. Qué solicita realmente el backtester

El backtester no debe pedir:

```text
la tabla Wake-up
la tabla Frontside Peak
un path
un parquet concreto
```

Debe declarar requisitos semánticos.

---

## 11.1 Detector Research RunSpec

Ejemplo conceptual:

```yaml
run_kind:
  detector_research

detector_id:
  wake_up_detector_candidate_v0_1

universe_id:
  microcap_eligible_universe_pit_v0_1

market_state_profiles:
  - core_light_candidate
  - wakeup_activity_candidate

event_types_as_input:
  []

event_types_generated:
  - wake_up_detected_candidate

consumption_purpose:
  detector_research
```

Regla:

```text
el mismo Event Type generado
no puede aparecer como input.
```

---

## 11.2 Policy Backtest RunSpec

```yaml
run_kind:
  policy_backtest

policy_id:
  long_entry_policy_v0_1

detector_dependency:
  wake_up_detector_v1_0_frozen

event_input_mode:
  regenerate_causally
  # o consume_precomputed_versioned

market_state_profiles:
  - core_light
  - active_episode_heavy

event_types:
  - wake_up_detected_v1_0

consumption_purpose:
  strategy_backtest
```

---

## 11.3 Provider / Consumer

```text
BacktestRunSpec
↓
RunPreflight
↓
StateResolutionRequest
↓
State Provider
↓
StateBundleManifest
↓
BacktestInputManifest
↓
HistoricalReplayFeed
+
StateReplayFeed, si aplica
↓
EventLoop
```

El provider decide:

```text
qué existe;
qué debe construirse;
qué puede reutilizarse;
qué está autorizado;
qué cobertura posee;
qué restricciones tiene.
```

---

# 12. Artefactos físicos y lógicos esperados

## 12.1 Representaciones

```text
Market State Core / Light
Market State Wake-up Extension
Market State Active-Episode Extension
Market State Price Structure Extension
Market State News / Event Risk Extension
```

## 12.2 Entidades

```text
Event Instance Registry
Episode Instance Registry
Active Symbol Registry
```

## 12.3 Event State

```text
Wake-up Event State Windows
Termination Event State Windows
```

## 12.4 Outcomes

```text
frontside_peak_outcome
D_x_H_drawdown_outcomes
time_to_new_hod
time_to_recovery
full_reversion_outcome
backside_outcome
```

## 12.5 Datasets derivados

```text
wake_up_detector_research_dataset
tradable_inplay_research_dataset
frontside_termination_research_dataset
entry_policy_backtest_dataset
long_exit_policy_backtest_dataset
backside_policy_backtest_dataset
```

Los datasets derivados no son nuevas definiciones de Market State.

---

# 13. Cadena institucional completa

```text
01. Parent Research Program

02. Scientific Problem Contract por experimento

03. H0, H1, baseline y falsación

04. Universe PIT Contract

05. Session Scope

06. Event Candidate Definition

07. Negative Cases Definition

08. Episode Boundary Definition

09. Event Type Admission Review

10. Information Object Gap Analysis

11. Operational Mapping
    Object
    → Representation Model
    → Feature
    → Table 000–018

12. Source Admissibility Review

13. Derivable Capability Check

14. Feature Specification Registry

15. Market State Profile Candidate

16. Market State Profile Admission

17. Ring Buffer Contract

18. Episode Instance Contract

19. Active Symbol Registry Contract

20. Detector Contract

21. False-Alarm Budget

22. Deduplication / TTL / Expiry Contract

23. Event Window Contract

24. Event State Contract

25. Outcome Definition Family

26. Population Construction

27. Dataset Build

28. Detector Evaluation
    before PnL

29. Detector Freeze

30. Policy Contract

31. Policy Freeze

32. BacktestRunSpec

33. StateResolutionRequest

34. StateBundleManifest

35. BacktestInputManifest

36. Replay

37. Technical Review

38. Economic Realism Review

39. OOS / Walk-Forward / Purge / Embargo

40. Trial Ledger

41. Multiple-Testing Adjustment

42. Independent Replication

43. Promotion / Rejection
```

---

# 14. Vertical slices recomendados

## Slice 1 · Wake-up observable

```text
1 ticker
1 session

trades / quotes
↓
Market State Light
↓
Wake-up Detector
↓
Wake-up Event Instance
```

Sin estrategia.

Sin órdenes.

Sin PnL.

---

## Slice 2 · Episode Instance

```text
Wake-up Event
↓
episode_instance_id
↓
Active Symbol Registry
↓
activation references
```

---

## Slice 3 · Ring Buffer + Heavy Backfill

```text
Wake-up
↓
recover pre-event trades / quotes
↓
build heavy pre-event extension
↓
continue heavy online extension
```

---

## Slice 4 · Tradable In-Play

```text
Heavy Market State
↓
participation
liquidity
directional conversion
persistence
↓
WATCH / ENTRY_ELIGIBLE / DISCARD
```

Todavía sin comprar.

---

## Slice 5 · Outcomes de terminación

Sin detector todavía:

```text
frontside peak outcome
D × H drawdowns
time to new HOD
time to recovery
backside outcome
```

---

## Slice 6 · Frontside Tracker

```text
Episode Market State Sequence
↓
ACTIVE
↓
STRESSED
↓
WARNING
↓
RISK_HIGH
↓
DETECTED
```

---

## Slice 7 · Event State

```text
Wake-up pre / at / post
Termination pre / at / post
```

con:

```text
state_role
consumption_legality
available-at
```

---

## Slice 8 · Policies

```text
Long Entry Policy
Long Inventory Policy
Long Exit Policy
Backside Entry Policy
Short Inventory Policy
Cover Policy
```

Cada una con:

```text
Strategy ID propio
PnL separado
cost assumptions propias
validation propia
```

---

# 15. Ejemplo físico completo con un ticker

Los valores siguientes son ilustrativos.

```text
09:42:07.850
Comienza una aceleración observable,
pero todavía no existe un episodio conocido.

09:42:08.247
Llega un trade.

09:42:08.251
Llega una quote.

09:42:08.260
Market State Light queda disponible.

09:42:08.300
Wake-up Detector supera su contrato.

09:42:08.310
Wake-up Event queda disponible.

09:42:08.310
Episode Instance queda legalmente creado.

episode_onset_at
=
09:42:07.850

episode_detected_at
=
09:42:08.300

episode_available_at
=
09:42:08.310

09:42:08.315
El ticker entra en Active Symbol Registry.

09:42:08.320
El sistema recupera el Ring Buffer previo.

09:42:08.340
Se materializa la extensión pesada pre-event.

09:42:08.350
Tradable In-Play Classifier sigue en WATCH.

09:42:09.500
Participación, liquidez y persistencia
permiten ENTRY_ELIGIBLE.

10:01:18.900
Frontside Phase Tracker pasa a STRESSED.

10:01:19.200
Termination Hazard aumenta.

10:01:19.240
Termination Detector supera su contrato.

10:01:19.250
Termination Event queda disponible.

10:01:19.260
Long Exit Policy puede consumir el evento.

10:01:31.000
Backside Confirmation queda disponible.
```

En paralelo, después de observar el futuro:

```text
Outcome Engine calcula:
- frontside peak retrospectivo
- drawdowns D × H
- nuevo HOD o no
- tiempo de recuperación
- reversión completa
```

Esos outcomes no se reinyectan en decisiones pasadas.

---

# 16. Correcciones concretas a una arquitectura de backtester

## Correcto

```text
BacktestRunSpec
↓
RunPreflight
↓
StateResolutionRequest
↓
State Provider
↓
StateBundleManifest
↓
BacktestInputManifest
↓
Replay
↓
Decision
↓
Execution
↓
Ledger
```

## Debe evitarse

```text
Backtester
→ abre path manual

Backtester
→ descubre Parquets

Backtester
→ recalcula features

Strategy
→ construye Market State

Strategy
→ usa Outcomes

Detector Research Run
→ consume el Event Type que intenta generar
```

## Distinción de Stores

```text
market_state_table
=
persistencia gobernada del provider.

MarketStateStore
=
estado disponible dentro del run.

event_state_table
=
persistencia gobernada.

EventStateStore
=
estado contextual ya entregable
dentro del EventLoop.
```

---

# 17. Invariantes no negociables

```text
1. Market State describe; no decide.

2. Detector interpreta; no ejecuta.

3. Event Instance aparece después del detector.

4. Episode Instance aparece después de Wake-up disponible.

5. Episode onset puede ser anterior,
   pero no es consumible antes de episode_available_at.

6. Event State no inventa un segundo mercado.

7. pre_event no significa que TSIS supiera
   que estaba antes de un evento.

8. Outcomes viven separados de X.

9. Detector Research Run no consume
   el Event Type que genera.

10. Policy Backtest usa detector congelado.

11. Heavy State requiere Ring Buffer pre-event.

12. Frontside Termination depende de un episodio activo.

13. Salir long no equivale a entrar short.

14. Peak retrospectivo no equivale
    a Termination Event.

15. El backtester solicita perfiles,
    no paths.

16. Materializado no significa autorizado.

17. El estado de gates no se hardcodea
    desde documentos conceptuales.

18. Cada feature conserva:
    fórmula,
    fuente,
    ventana,
    cutoff,
    available-at,
    builder version
    y lineage.
```

---

# 18. Conclusión final

La premisa operativa correcta es:

```text
1. Definir un programa científico padre
   para episodios microcap.

2. Mantener separados:
   Wake-up Detection
   y
   Frontside Termination.

3. Construir un Market State Core / Light
   para todo el universo elegible.

4. Mantener un Ring Buffer corto
   de trades y quotes.

5. Detectar Wake-up.

6. Crear Wake-up Event Instance.

7. Crear Episode Instance
   con onset, detected y available-at.

8. Activar extensiones pesadas
   sólo para tickers despertados.

9. Reconstruir el tramo pre-event
   desde el Ring Buffer.

10. Determinar Tradable In-Play.

11. Seguir el episodio
    con Frontside Phase Tracker.

12. Estimar Termination Hazard.

13. Crear Termination Event Instances
    sólo desde evidencia observable.

14. Mantener Frontside Peak
    y D × H exclusivamente en Outcomes.

15. Separar:
    Detector Research Run
    de
    Policy Backtest Run.

16. Hacer que el backtester solicite
    perfiles, capacidades y versiones,
    nunca tablas físicas o paths.
```

La formulación más corta es:

```text
Wake-up inicia el episodio.

Episode Instance organiza el frontside.

Market State describe su evolución.

Frontside Tracker interpreta la trayectoria.

Termination Detector emite un evento operativo.

Frontside Peak permanece como outcome retrospectivo.

Las políticas long y short consumen
los eventos y probabilidades ya validados,
pero no definen el mercado.
```
