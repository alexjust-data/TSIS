# WAKE_UP_EVENT_CANDIDATE_DEFINITION_V0_2

Estado: candidato para admisión semántica.
Dictamen: PASS_WITH_MINOR_REVISIONS_APPLIED.

No constituye todavía:

Event Type promovido operacionalmente
detector definitivo
calibración de ventanas o umbrales
señal de compra
autorización para consumo predictivo
demostración de edge

———

## 1. Separación conceptual

  Capa                     Pregunta
━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Definición científica    ¿Qué fenómeno queremos identificar?
───────────────────────  ─────────────────────────────────────────────────
  Representación           ¿Qué información observable debe conservarse?
───────────────────────  ─────────────────────────────────────────────────
  Detector                 ¿Cómo reconocemos causalmente el fenómeno?
───────────────────────  ─────────────────────────────────────────────────
  Calibración              ¿Qué ventanas y umbrales concretos utilizamos?
───────────────────────  ─────────────────────────────────────────────────
  Política                 ¿Qué hacemos después de detectarlo?
───────────────────────  ─────────────────────────────────────────────────
  Ejecución                ¿Qué tamaño, orden, precio y fill son posibles?

WAKE-UP ≠ fórmula del detector
DETECTOR ≠ política de entrada
WAKE-UP ≠ IN-PLAY confirmado
IN-PLAY ≠ FRONTSIDE
IN-PLAY ≠ tradable para cualquier tamaño
ENTRY_ELIGIBLE ≠ orden ni fill
WAKE-UP ≠ continuación futura ni edge

Market State conserva observaciones. El detector determina si existe suficiente evidencia para emitir Wake-
up. La política decide si considera una entrada. Risk, OMS y Execution determinan si puede enviarse y
ejecutarse una orden.

———

## 2. Definición científica candidata

> Dentro de un universo point-in-time elegible y una sesión autorizada, un Wake-up Event es la transición
> causalmente detectable que abre un nuevo episodio de activación —conforme a sus reglas de deduplicación y
> rearme y siempre que no exista un Market Activation Episode vigente— desde un régimen dormido o de baja
> actividad contextual hacia un régimen de actividad materialmente anómala respecto a un baseline
> point-in-time.
>
> La transición debe estar sustentada por una sorpresa relativa de actividad, un suelo absoluto de minimis
> destinado exclusivamente a descartar cambios microscópicos y una corroboración contemporánea multievento
> o multifuente suficientemente no redundante para excluir un print aislado, ruido transitorio, desorden
> temporal o un defecto de datos.
>
> Cuando clock >= wake_up_available_at_utc, la detección inicia WATCH, crea un
> CandidateMarketActivationEpisodeInstance e incorpora el instrumento al ResearchActiveSymbolSet. No afirma
> todavía que la participación sea persistente, que exista un frontside, que el instrumento sea tradable
> para un tamaño determinado, que el precio vaya a continuar, que una política permita entrar ni que exista
> edge económico.
>
> Una activación que posteriormente falle, vuelva al régimen dormido o nunca alcance In-Play no invalida
> retrospectivamente el Wake-up emitido con información causalmente disponible.

Representación operacional:

WAKE-UP
=
¿el instrumento ha abandonado causalmente
su régimen dormido contextual?

OUTPUT
=
WATCH
+
CANDIDATE MARKET ACTIVATION EPISODE INSTANCE
+
RESEARCH ACTIVE SYMBOL SET

visible únicamente cuando:
clock >= wake_up_available_at_utc

NO AFIRMA
=
IN_PLAY
FRONTSIDE
TRADABILITY
ENTRY_ELIGIBLE
ORDER
FILL
CONTINUATION
EDGE

———

## 3. Wake-up por episodio

La expresión “primera transición” se refiere al primer Wake-up de un Market Activation Episode, no
necesariamente al primero de toda la sesión.

despertar
→ fallar
→ volver a dormirse
→ cumplir las reglas de rearme
→ despertar en un nuevo episodio

Por tanto:

NO:
primer Wake-up absoluto de la sesión

SÍ:
primer Wake-up dentro del episodio de activación

Si existe un episodio activo:

episode_status = ACTIVE
→ nuevo burst = REACTIVATION / RENEWED_ACTIVITY
→ no crea automáticamente otro Wake-up primario

Sólo puede emitirse un nuevo Wake-up cuando:

episode_status = CLOSED
+
rearm conditions = satisfied

El Episode Instance Contract y el contrato del detector deberán definir posteriormente:

cooldown
TTL
tiempo dormido mínimo para rearmar
deduplicación de bursts próximos
reactivación del episodio
creación de un episodio nuevo

Estos parámetros no quedan congelados en la definición semántica V0.2.

———

## 4. Régimen dormido y baseline PIT

Dormido no significa necesariamente:

cero trades
cero volumen
precio inmóvil

Significa que el instrumento permanece dentro de una distribución de actividad dormida o de baja actividad
esperable para su contexto causalmente disponible y que no existe un Market Activation Episode vigente:

instrument_id
sesión
franja horaria
actividad histórica reciente
precio
grupo de liquidez
calidad y cobertura de la fuente

actividad anómala
≠
actividad alta en términos absolutos

actividad anómala
=
actividad inesperada respecto
a un baseline contextual PIT

El baseline debe construirse exclusivamente con información disponible hasta el instante correspondiente.
No puede utilizar:

datos futuros de la misma sesión
la distribución anual completa todavía no observable
clasificaciones retrospectivas de liquidez
datos corregidos que no estaban disponibles entonces

La definición no determina todavía si se emplearán percentiles empíricos, mediana y MAD, CUSUM, z-score
robusto o detección bayesiana.

———

## 5. Evidencia mínima

  Familia                        Qué debe demostrar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Elegibilidad PIT               Instrumento, sesión y contexto eran elegibles con información disponible
                                entonces.
─────────────────────────────  ────────────────────────────────────────────────────────────────────────────
  Régimen previo                 Existía un baseline dormido o de baja actividad contextual y no había un
                                Market Activation Episode vigente.
─────────────────────────────  ────────────────────────────────────────────────────────────────────────────
  Sorpresa relativa              La actividad reciente es anómala respecto al baseline PIT.
─────────────────────────────  ────────────────────────────────────────────────────────────────────────────
  Suelo absoluto de minimis      La anomalía no procede de una actividad materialmente microscópica.
─────────────────────────────  ────────────────────────────────────────────────────────────────────────────
  Corroboración no redundante    La decisión no depende de una única observación o de varias features
                                derivadas del mismo mensaje.
─────────────────────────────  ────────────────────────────────────────────────────────────────────────────
  Calidad temporal               No depende de cancelaciones, correcciones, desorden temporal, quotes stale
                                o información futura.

La sorpresa relativa puede observarse mediante una combinación de:

trade intensity
dollar-volume intensity
interarrival-time collapse
quote-update intensity
actividad respecto al baseline

La corroboración contemporánea puede ser:

varios trades en timestamps distintos
burst de trades + desplazamiento del NBBO
trades + quote response
actividad repetida durante una ventana causal

Debe considerarse sospechoso:

un único trade
un print tardío
una corrección
una operación fuera de secuencia
una quote aislada
un mensaje representado por varias features redundantes

No se exige independencia estadística entre trades, quotes, bid/ask y midprice. Se exige evidencia
multievento o multifuente suficientemente no redundante.

———

## 6. Suelo absoluto de minimis

El suelo absoluto evita casos como:

baseline:
1 trade cada 20 minutos

actividad reciente:
2 trades en 5 segundos

shock relativo:
enorme

actividad económica:
microscópica

Su único propósito es impedir que una sorpresa relativa enorme pero materialmente microscópica produzca
Wake-up.

DE-MINIMIS ANTI-ARTIFACT FLOOR
≠
minimum tradable volume

≠
minimum capacity

≠
target-order-size gate

≠
In-Play confirmado

No debe convertirse en otro umbral equivalente al scanner de 500.000 acciones.

———

## 7. Persistencia

Deben distinguirse dos formas de persistencia:

persistencia antinartefacto
=
eventos o timestamps suficientes
para descartar un one-print

pertenece a Wake-up

persistencia económica
=
participación que continúa,
es aceptada y mantiene relevante el episodio

pertenece a In-Play

Wake-up exige consistencia mínima, pero no continuidad económica.

———

## 8. Máquinas de estados

El detector y el episodio no comparten la misma máquina de estados.

### 8.1 Máquina del detector

DORMANT
↓
ACTIVATION_CANDIDATE
├── ONE_PRINT_ANOMALY
├── DATA_QUALITY_REJECTED
└── WAKE_UP_DETECTED

WAKE_UP_DETECTED es un evento inmutable. No se transforma posteriormente en Failed Activation, Returned to
Dormant o In-Play.

### 8.2 Máquina del episodio

Cuando el Wake-up puede entregarse legalmente:

clock >= wake_up_available_at_utc
↓
CandidateMarketActivationEpisodeInstance

El episodio comienza como:

episode_kind  = market_activation_episode
current_phase = activation_observed

No comienza como:

episode_kind = confirmed_frontside

Su evolución puede ser:

ACTIVATION_OBSERVED
→ IN_PLAY_CANDIDATE
→ IN_PLAY_CONFIRMED

O:

ACTIVATION_OBSERVED
→ EPISODE_CLOSED(reason=FAILED_ACTIVATION)

IN_PLAY_CANDIDATE
→ EPISODE_CLOSED(reason=RETURNED_TO_DORMANT)

El frontside debe emerger posteriormente:

Wake-up
↓
In-Play
↓
conversión direccional alcista
↓
impulso o continuación
↓
UPWARD_FRONTSIDE_ACTIVE

———

## 9. Evento, fases y desenlace del episodio

Wake-up y Failed Activation no pertenecen a la misma columna semántica.

EVENT CANDIDATE:
WAKE_UP_DETECTED

EPISODE PHASES:
ACTIVATION_OBSERVED
IN_PLAY_CANDIDATE
IN_PLAY_CONFIRMED
UPWARD_FRONTSIDE_ACTIVE
STRESSED
TERMINATION_CANDIDATE

EPISODE OUTCOMES / CLOSE REASONS:
FAILED_ACTIVATION
RETURNED_TO_DORMANT
DATA_COVERAGE_LOST
SESSION_ENDED
EXPIRED
TERMINATED

IN_PLAY_CONFIRMED es una fase positiva del episodio, no un outcome terminal ni un close reason.

Wake-up representa un hecho detectado causalmente. FAILED_ACTIVATION representa un resultado posterior del
episodio.

El fracaso del episodio no elimina ni invalida retrospectivamente el evento.

———

## 10. Timestamps

Deben conservarse cuatro conceptos temporales:

activation_onset_estimated_at_utc
=
estimación producida por la versión congelada
del detector utilizando únicamente información
disponible en wake_up_detected_at_utc

activation_onset_estimate_available_at_utc
=
primer instante desde el que esa estimación
puede consumirse legalmente

wake_up_detected_at_utc
=
primer instante en que el detector
acumula evidencia causal suficiente

wake_up_available_at_utc
=
primer instante legal de publicación
y consumo del Wake-up

También puede existir:

activation_onset_research_label_at_utc
=
onset retrospectivo producido
por el Outcome Engine usando información futura

Este último es research_only y está prohibido como input predictivo.

Una estimación causal puede apuntar a un instante anterior, pero el conocimiento no puede retrotraerse a
ese instante:

activation_onset_estimated_at_utc
<
wake_up_detected_at_utc

activation_onset_estimate_available_at_utc
>=
wake_up_detected_at_utc

wake_up_available_at_utc
>=
wake_up_detected_at_utc

consumo legal de la estimación
>=
activation_onset_estimate_available_at_utc

creación visible del CandidateMarketActivationEpisodeInstance
e incorporación al ResearchActiveSymbolSet
sólo cuando:

clock >= wake_up_available_at_utc

———

## 11. Wake-up, In-Play, Frontside y Tradability

  Nivel                       Pregunta                                   Resultado
━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Activation Candidate        ¿Existe evidencia inicial de cambio?       Observar brevemente o rechazar
──────────────────────────  ─────────────────────────────────────────  ────────────────────────────────────
  Wake-up                     ¿Ha abandonado causalmente el régimen      WATCH + Candidate Episode Instance
                              dormido?
──────────────────────────  ─────────────────────────────────────────  ────────────────────────────────────
  In-Play                     ¿La actividad anómala se mantiene y        IN_PLAY_CONFIRMED
                              sigue siendo relevante?
──────────────────────────  ─────────────────────────────────────────  ────────────────────────────────────
  Upward Frontside In-Play    ¿In-Play presenta conversión               UPWARD_FRONTSIDE_ACTIVE
                              direccional alcista compatible con el
                              episodio ascendente?
──────────────────────────  ─────────────────────────────────────────  ────────────────────────────────────
  Tradability                 ¿Este tamaño puede intentarse dentro de    PASS/FAIL por perfil
                              costes, impacto y riesgo?
──────────────────────────  ─────────────────────────────────────────  ────────────────────────────────────
  Entry Eligibility           ¿La política permite considerar una        ENTRY_ELIGIBLE/NO_ENTRY
                              entrada ahora?
──────────────────────────  ─────────────────────────────────────────  ────────────────────────────────────
  Execution                   ¿Qué orden puede enviarse y qué fill       Orden, no orden, fill o no fill
                              puede obtenerse?

Familias observables:

A = Activity Surprise
L = Liquidity / condiciones observables
D = Directional Conversion
P = Persistence / Acceptance

Condiciones completas de Wake-up:

E   = elegibilidad PIT
B   = baseline dormido
Ar  = sorpresa relativa
Aa  = suelo absoluto de minimis
C   = corroboración no redundante
Q   = calidad temporal

Secuencia corregida:

E + B + Ar + Aa + C + Q
→ WAKE_UP_DETECTED

WAKE_UP_DETECTED + L + D
→ EARLY_DIRECTIONAL_PARTICIPATION

WAKE_UP_DETECTED + P
→ IN_PLAY_CANDIDATE

IN_PLAY_CANDIDATE + relevancia sostenida
→ IN_PLAY_CONFIRMED

IN_PLAY_CONFIRMED + D alcista + scope upward_frontside
→ UPWARD_FRONTSIDE_ACTIVE

Tradability se evalúa separadamente:

TRADABILITY
=
f(
instrumento,
estado,
target_order_size,
cost_limits,
impact_limits,
risk_limits
)

Una acción puede estar claramente In-Play y no ser ejecutable para nuestro tamaño.

———

## 12. Dirección y scope ascendente

La semántica general de Wake-up puede ser neutral:

market_activity:wake_up_detected

activation_direction
=
up
down
mixed
indeterminate

También la semántica general de In-Play es neutral:

IN_PLAY_CONFIRMED
=
actividad anómala persistente y relevante,
independientemente de su dirección

El primer experimento puede restringirse a:

activation_direction = up
scope = upward_frontside

En ese experimento:

UPWARD_FRONTSIDE_IN_PLAY_CONFIRMED
=
IN_PLAY_CONFIRMED
+
conversión direccional alcista
+
compatibilidad con el episodio ascendente

El Event Type general no debe quedar contaminado por una dirección de estrategia concreta.

———

## 13. Denominador científico

El denominador base debe aproximarse a:

todos los symbol-times PIT elegibles
dentro del tiempo de sesión válido

Cada unidad podrá resolverse posteriormente como:

NORMAL
ACTIVATION_CANDIDATE
WAKE_UP
ONE_PRINT_ANOMALY
DATA_QUALITY_REJECTED
FAILED_ACTIVATION
IN_PLAY

El experimento debe contener:

activaciones exitosas
activaciones fallidas
one-print anomalies
instrumentos que permanecen dormidos
movimientos sin continuación
casos con mala liquidez
casos con datos insuficientes

No puede calibrarse únicamente con acciones elegidas retrospectivamente por el screener o con gráficos
ganadores.

Antes de seleccionar ventanas, features, umbrales o modelos deben congelarse:

unidad de muestreo
esquema de representación de periodos normales
tratamiento del desbalance de clases

La unidad podrá ser:

symbol-second
symbol-event
symbol-window

Su elección afecta a:

false-positive rate
precision
class balance
alert burden
calibración probabilística

Deben evaluarse separadamente:

symbol-time false-alarm evaluation

event-level detection and matching evaluation

La unidad definitiva debe quedar definida en el Detector Experiment Contract.

———

## 14. Scanner de 500.000 acciones e imágenes

El filtro de 500.000 acciones puede continuar como candidate proxy for established in-play, pero no
constituye ground truth de In-Play ni debe definir el instante científico de Wake-up.

inicio del burst
≈ ACTIVATION_CANDIDATE

primer cambio causal corroborado
≈ WAKE_UP_DETECTED

marcador momentum/scanner
≈ candidate proxy for IN-PLAY tardío o establecido

rebreak y extensión posterior
≈ outcome

Los gráficos seleccionados y las barras de un minuto no permiten fijar el segundo exacto del evento ni
entrenar el detector. Eso exige replay de trades/quotes y un denominador con periodos normales, falsas
activaciones y anomalías.

———

## 15. Admisión en dos etapas

### 15.1 Admisión semántica candidata

Establece:

qué significa Wake-up
qué timestamps posee
cuáles son sus casos negativos
cómo habilita un CandidateMarketActivationEpisodeInstance
qué afirma y qué no afirma

Autoriza:

investigación
construcción experimental
diseño del dataset
evaluación del detector

Durante esta etapa, las entidades resultantes son:

WakeUpEventCandidateRecord
CandidateMarketActivationEpisodeInstance
ResearchActiveSymbolSet

No autoriza:

consumo predictivo
decisiones de estrategia
órdenes
fills
claims de edge

### 15.2 Promoción operacional

Sólo puede considerarse después de disponer de:

detector versionado
available-at validado
binding físico
cobertura conocida
evaluación OOS
false-alarm budget aceptado

Entonces podrá evaluarse la autorización para:

decision-safe consumption

Y, cuando exista autoridad explícita, podrán utilizarse entidades operacionales como:

WakeUpEventInstance
MarketActivationEpisodeInstance
GovernedActiveSymbolRegistry

Secuencia institucional:

candidate semantic admission
→ experimento físico
→ validación temporal y OOS
→ operational predictive promotion

———

## 16. Qué queda congelado en V0.2

significado semántico de Wake-up
primer Wake-up por episodio, no por sesión
baseline contextual PIT
sorpresa relativa
suelo absoluto de minimis antiartefacto
corroboración no redundante
casos negativos
separación de timestamps causales y research-only
output = WATCH
WakeUpEventCandidateRecord
CandidateMarketActivationEpisodeInstance
ResearchActiveSymbolSet
separación de In-Play, Frontside y Tradability
separación de evento, fases y outcome
denominador previo a calibración
admisión institucional en dos etapas

———

## 17. Qué no queda congelado

ventanas exactas
umbrales
número mínimo de trades
dollar volume exacto
retorno mínimo
spread máximo
quorum
features finales
score
modelo estadístico o ML
cooldown y TTL
reglas exactas de rearme
unidad de muestreo definitiva
latencia simulada exacta
target_order_size
política de entrada
stops o take profit

Antes de declarar calculables las features deben auditarse timestamps, secuencias, trade conditions,
corrections, cobertura premarket y naturaleza de las quotes.

———

## 18. Dictamen final

SCIENTIFIC SEMANTICS
=
PASS

WAKE-UP / IN-PLAY SEPARATION
=
PASS

FIRST TRANSITION SCOPE
=
CORRECTED TO EPISODE INSTANCE

BASELINE TEMPORALITY
=
CORRECTED TO POINT-IN-TIME

CORROBORATION
=
CORRECTED TO NON-REDUNDANT MULTIEVENT OR MULTISOURCE

ABSOLUTE FLOOR
=
CORRECTED TO DE-MINIMIS ANTI-ARTIFACT FLOOR

ONSET TEMPORALITY
=
SPLIT INTO CAUSAL ESTIMATE AND RESEARCH LABEL

TRADABILITY NAMING
=
CORRECTED

EPISODE LIFECYCLE
=
STARTS AS CANDIDATE MARKET ACTIVATION EPISODE

EVENT VS EPISODE PHASE VS OUTCOME
=
SEPARATED

DENOMINATOR
=
CORRECTED TO ELIGIBLE SYMBOL-TIME BASE

SEMANTIC CANDIDATE ADMISSION
=
READY

OPERATIONAL PREDICTIVE PROMOTION
=
NOT AUTHORIZED

WAKE_UP_EVENT_CANDIDATE_DEFINITION_V0_2 queda preparado para admisión semántica candidata y construcción
experimental.

No queda promovido como Event Type operacional ni autorizado para consumo predictivo.