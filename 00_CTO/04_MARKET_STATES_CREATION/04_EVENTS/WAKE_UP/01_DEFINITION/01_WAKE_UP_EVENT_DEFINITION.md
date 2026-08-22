# 01 — WAKE-UP EVENT DEFINITION v0.1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `wake_up_event_definition` |
| `document_version` | `v0_1` |
| `document_role` | `SCIENTIFIC_EVENT_DEFINITION_DRAFT` |
| `document_status` | `DRAFT_FOR_HUMAN_AND_SCIENTIFIC_REVIEW_NOT_FROZEN` |
| `candidate_event_type_id` | `event_type:market_activity:wake_up` |
| `event_type_registry_status` | `UNREGISTERED_CANDIDATE_NOT_ADMITTED` |
| `subject_scope` | `instrument` |
| `primary_information_object` | `trading_activity` |
| `composite_event_scope` | `MULTI_INFORMATION_OBJECT_CHARACTERIZATION` |
| `implementation_authorized` | `false` |
| `label_materialization_authorized` | `false` |
| `event_instance_materialization_authorized` | `false` |
| `binding_a_b_comparison_authorized` | `false` |
| `temporal_oos_authorized` | `false` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-17` |

## 1. Propósito

Este documento define científicamente el fenómeno **Wake-up** sin confundirlo con:

- una representación física concreta de `Trading Activity`;
- un scanner de volumen acumulado;
- un evento de precio;
- una confirmación de rebreak;
- un estado `In-Play`;
- una señal de entrada;
- una operación rentable;
- un outcome futuro.

La definición debe servir como autoridad científica común para:

1. construir un oracle de labels independiente;
2. comparar Binding A y Binding B sin favorecer a ninguno;
3. definir posteriormente un Event Type candidato;
4. crear Event Instances y Event State de forma temporalmente legal;
5. extender el mismo fenómeno desde un perfil RTH restringido a un perfil full-session cuando existan fuentes gobernadas.

Este documento no congela todavía thresholds, horizontes, presupuestos de falsas activaciones ni fórmulas de detector.

---

## 2. Definición científica

> **Wake-up es una transición de régimen en la que un instrumento pasa desde una condición contextual de baja participación negociada hacia una condición de participación realizada, anómala, multievento y económicamente material, corroborada con evidencia temporal suficiente y sin depender de su continuación posterior.**

Forma lógica provisional:

```text
POSITIVE_WAKE_UP
=
PRIOR_CONTEXTUAL_DORMANCY
AND
RELATIVE_ACTIVITY_TRANSITION
AND
MULTI_EVENT_EVIDENCE
AND
ANTI_ARTIFACT_ECONOMIC_MATERIALITY
AND
TEMPORAL_CORROBORATION
AND
SOURCE_AND_TEMPORAL_LEGALITY
```

Las cantidades exactas que implementen cada término deben calibrarse y congelarse en artefactos posteriores.

---

## 3. Identidad mínima estable del evento

Wake-up deja de ser Wake-up si desaparece cualquiera de estas propiedades:

```text
1. Existe un estado previo contextual de actividad baja o dormida.

2. Aparece negociación realizada observable;
   no basta con interés teórico, quotes o una noticia.

3. La nueva actividad es anómala respecto a un baseline PIT
   del mismo instrumento y contexto horario.

4. La evidencia contiene varios eventos o clusters independientes;
   un único print no confirma por sí solo el evento.

5. La actividad supera un suelo económico antinartefacto.

6. La transición posee persistencia o corroboración temporal suficiente.

7. Todo input utilizado respeta disponibilidad y cutoff point-in-time.
```

No forman parte de la identidad mínima:

```text
dirección del precio;
retorno futuro;
nuevo HOD;
VWAP;
rebreak;
continuación alcista;
spread aceptable;
depth suficiente;
borrow;
orden, fill o slippage;
entrada rentable;
PnL;
MFE o MAE.
```

---

## 4. Por qué `Trading Activity` es el ancla mínima, pero no el Wake-up completo

### 4.1 Ancla mínima del onset

`Trading Activity` responde:

```text
¿Ha aparecido participación negociada realizada
donde antes existía actividad contextual baja?
```

Por ello es el propietario semántico natural del **onset mínimo**.

Una noticia puede aparecer sin que nadie negocie.  
Un precio puede saltar por un único print.  
Un spread puede cambiar sin participación realizada.

En cambio, el lenguaje humano “la acción ha despertado” implica normalmente que la negociación ha comenzado a llegar con una intensidad y materialidad distintas.

### 4.2 Wake-up completo

El episodio completo es multiobjeto:

```text
Trading Activity
=
algo ha empezado

Otros Information Objects
=
qué clase de cambio es,
cómo se desarrolla,
en qué dirección,
con qué calidad,
en qué contexto
y si puede llegar a ser operable
```

Por tanto:

```text
WAKE_UP MINIMAL EVENT IDENTITY
=
Trading Activity transition

WAKE_UP COMPOSITE STATE
=
multi-Information-Object evidence

TRADABLE IN-PLAY
=
separate eligibility/classification claim

STRATEGY ACTION
=
separate policy
```

---

## 5. Papel de los diez Information Objects

| Information Object | Papel en el fenómeno Wake-up | ¿Es obligatorio para la identidad mínima? |
|---|---|---:|
| **Trading Activity — Baseline-Relative Marked Activity Process** | Detecta la transición básica de participación: frecuencia, intensidad, marks, concentración, sorpresa, persistencia y decaimiento. | **Sí** |
| **Market Microstructure State — Observed Trade–Quote Event Coupling State** | Corrobora la calidad del acoplamiento entre trades y quotes; detecta evidencia degradada o artefactos. | No |
| **Price Movement — Signed Multiscale Price-Path Response** | Mide si la actividad se convierte en desplazamiento direccional. | No |
| **Liquidity — Observable Top-of-Book Liquidity and Resilience State** | Determina observabilidad y potencial operabilidad: spread, quote availability, resiliencia y capacidad observable. | No |
| **Volatility / Range State — Unsigned Multiscale Variation and Range-Expansion State** | Mide expansión de variación y rango. | No |
| **Price Location / Structure — Causal Anchor-Relative Location State** | Sitúa el episodio respecto a prior close, HOD, VWAP, gaps y otros anchors causales. | No |
| **Fundamental Context — PIT Structural Scale and Eligibility Context** | Proporciona escala y elegibilidad estructural: precio, market-cap proxy, shares y contexto PIT. | No; gobierna scope |
| **News / Catalyst Context — Availability-Aware Catalyst Event Context** | Explica una causa conocida y disponible; una noticia sin negociación no es aún Wake-up de mercado. | No |
| **Halt Context — Institutional Continuity State Machine** | Representa interrupciones, reanudaciones y continuidad institucional. | No |
| **Order Flow Pressure — Signed Flow–Price Conversion with Classification Confidence** | Describe dirección y eficacia del flujo realizado. | No |

Regla:

```text
La ausencia de un contexto no obligatorio
no transforma automáticamente un Wake-up en negativo.

Debe producir:
DEGRADED, UNAVAILABLE o CONTEXT_NOT_OBSERVED,
según el contrato aplicable.
```

---

## 6. Capas posteriores al onset

La arquitectura científica propuesta es:

```text
DORMANT
↓
ACTIVITY_TRANSITION_DETECTED
↓
WAKE_UP_EVENT_INSTANCE
↓
EPISODE_INSTANCE
↓
WAKE_UP_COMPOSITE_CORROBORATION
↓
IN_PLAY_ELIGIBLE / DISCARD / CONTINUE_OBSERVING
↓
STRATEGY POLICY
```

### 6.1 `ACTIVITY_TRANSITION_DETECTED`

Pregunta:

```text
¿Ha dejado de estar dormida la participación negociada?
```

Propietario principal:

```text
Trading Activity
```

### 6.2 `WAKE_UP_COMPOSITE_CORROBORATION`

Pregunta:

```text
¿La transición de actividad coincide con un cambio
más amplio y observable del régimen de mercado?
```

Puede incorporar:

```text
Price Movement
Volatility / Range
Market Microstructure
Order Flow Pressure
```

### 6.3 `IN_PLAY_ELIGIBLE`

Pregunta:

```text
¿Este episodio merece vigilancia intensiva
o puede llegar a ser operable?
```

Puede incorporar:

```text
Liquidity
Price Location / Structure
Fundamental Context
News / Catalyst Context
Halt Context
```

### 6.4 Estrategia

Decide separadamente:

```text
WATCH
ENTER
REDUCE
EXIT
SHORT
NO_ACTION
```

Wake-up nunca equivale por sí solo a una acción de estrategia.

---

## 7. Invariancia semántica respecto al horario

La identidad científica es la misma a las 04:30, 08:30, 09:31 o 14:00.

```text
horario
!=
identidad del evento
```

El horario sí modifica:

```text
baseline esperado;
fuentes disponibles;
calidad y cobertura;
censura al inicio del scope;
claim permitido;
observation profile.
```

Se propone una sola identidad semántica:

```text
candidate_event_type_id
=
event_type:market_activity:wake_up
```

y perfiles de observación separados:

```text
wake_up_observation_profile_rth_legacy_v0_1
=
primera transición observable dentro de RTH

wake_up_observation_profile_full_session_v0_1
=
primera transición observable en premarket + RTH + after-hours
```

Estos IDs son candidatos y no están admitidos.

### 7.1 Restricción del experimento actual

Binding A y Binding B actuales observan únicamente RTH bajo fuente legacy.

Por tanto, solo pueden afirmar:

```text
first observable Trading Activity transition during RTH
```

No pueden afirmar:

```text
complete full-session Wake-up onset
```

Si un instrumento llega activo a la apertura regular:

```text
classification
=
LEFT_CENSORED_ACTIVE_AT_SCOPE_START

reason
=
PREVIOUS_ONSET_UNOBSERVED
```

No se debe fingir que el primer segundo RTH fue el Wake-up.

---

## 8. Daily Eligible Universe y relación con el evento

Wake-up no define por sí mismo el universo de instrumentos.

El parent universe se resuelve mediante una política externa y versionada, por ejemplo:

```text
presession market-cap proxy < 100,000,000 USD
price policy gobernada
identidad válida
session válida
```

La implementación experimental actualmente disponible utiliza, con restricciones:

```text
0.50 <= prior eligible RTH close <= 20.00
presession_reference_market_cap_proxy < 100,000,000 USD
```

La definición Wake-up no posee esos thresholds.

Reglas:

```text
fuera del Daily Eligible Universe
=
OUT_OF_SCOPE

no
=
NEGATIVE_WAKE_UP
```

Binding A, Binding B y el detector deben evaluar todos los instrumentos elegibles de la sesión, incluidos los que permanecen dormidos. Los negativos no pueden seleccionarse retrospectivamente solo entre tickers que ya despertaron.

---

## 9. Morfologías positivas admitidas por la ontología

El mismo Event Type puede aparecer con distintas formas:

```text
POSITIVE_WAKE_UP_ABRUPT
=
explosión rápida tras actividad dormida

POSITIVE_WAKE_UP_PROGRESSIVE
=
transición gradual y persistente

POSITIVE_WAKE_UP_MULTISTAGE
=
varias fases de aceleración antes de la confirmación
```

La morfología no cambia la identidad del evento.

Además:

```text
Wake-up real que después fracasa
=
sigue siendo Wake-up
```

Por tanto:

```text
Wake-up
!=
rebreak confirmado
!=
continuación alcista
!=
operación rentable
!=
In-Play
```

---

## 10. Taxonomía del oracle y labels

Estas clases pertenecen al oracle de investigación. Solo las clases positivas pueden originar un Event Instance.

### Positivas

```text
POSITIVE_WAKE_UP_ABRUPT
POSITIVE_WAKE_UP_PROGRESSIVE
POSITIVE_WAKE_UP_MULTISTAGE
```

### Negativas

```text
NEGATIVE_ONE_PRINT_OR_DUST
NEGATIVE_TRANSIENT_BURST
NEGATIVE_HIGH_BUT_CONTEXTUALLY_NORMAL_ACTIVITY
NEGATIVE_DATA_ARTIFACT
```

### No binarias

```text
LEFT_CENSORED_ACTIVE_AT_SCOPE_START
AMBIGUOUS
UNAVAILABLE_SOURCE_OR_QUALITY
OUT_OF_SCOPE
```

No se deben colapsar:

```text
UNAVAILABLE
AMBIGUOUS
OUT_OF_SCOPE
```

en:

```text
NEGATIVE
```

---

## 11. Relojes y legalidad temporal

Deben separarse, como mínimo:

```text
reference_onset_timestamp_utc
=
inicio retrospectivo estimado del cambio

onset_interval_start_utc / onset_interval_end_utc
=
intervalo retrospectivo cuando el onset exacto no es identificable

confirmation_end_timestamp_utc
=
fin de la evidencia futura utilizada por el oracle

detected_at_utc
=
primer instante en que un detector causal acumuló evidencia suficiente

available_at_utc
=
primer instante legal de entrega al consumidor
```

Restricciones:

```text
detected_at_utc
>=
max(available_at de todos los inputs consumidos)

available_at_utc
>=
detected_at_utc
```

Y:

```text
confirmation_end_timestamp_utc
=
LABEL / OUTCOME ONLY

confirmation_end_timestamp_utc
MUST NOT
enter detector inputs at an earlier decision time
```

Cuando la fuente solo permite localizar un intervalo:

```text
onset_precision
=
INTERVAL_CENSORED
```

No se debe inventar un timestamp puntual.

---

## 12. Definición representacionalmente neutral del oracle

El oracle no puede definirse mediante las variables finales de Binding A o Binding B.

Prohibido:

```text
Binding A scores o percentiles finales;
Binding B kernels, durations o scores finales;
scanner de 500k;
scanner +50%;
rebreak;
retorno futuro;
MFE / MAE;
PnL;
resultado de estrategia.
```

El oracle puede utilizar, bajo contrato independiente:

```text
raw eligible trades;
timestamp clusters;
trade counts;
share volume;
dollar volume;
distribución temporal;
baseline PIT independiente;
coverage y calidad fuente;
quotes únicamente como evidencia de calidad o artefacto,
no como condición necesaria de la identidad Trading Activity.
```

La definición debe ser suficientemente neutral para no premiar a:

```text
Binding A
por usar ventanas rectangulares

ni a

Binding B
por usar event time, kernels o duraciones
```

---

## 13. Esqueleto matemático provisional

Sea `A_t` la evidencia de Trading Activity disponible legalmente en `t`.

```text
D_t
=
prior contextual dormancy state

R_t
=
relative activity transition evidence

M_t
=
multi-event corroboration

E_t
=
anti-artifact economic materiality

P_t
=
temporal persistence / corroboration

Q_t
=
source and temporal quality state
```

Entonces:

```text
WakeUpOracle(t)
=
D_t AND R_t AND M_t AND E_t AND P_t AND Q_t
```

No se congelan todavía:

```text
dormancy horizon;
confirmation horizon;
minimum distinct clusters;
economic floor;
relative anomaly threshold;
persistence rule;
matching window.
```

Deben calibrarse en development mediante una matriz preregistrada y buscar una región estable, no un único punto óptimo.

---

## 14. Actividad económica mínima

El suelo económico es solo un control antinartefacto.

No significa:

```text
500,000 acciones;
liquidez suficiente;
capacidad de ejecución;
minimum strategy size;
tradability.
```

Forma general:

```text
economic_activity_confirmed
=
cumulative eligible dollar volume
>=
max(
    absolute_de_minimis_floor,
    relative_PIT_activity_floor
)
```

La fórmula exacta y sus valores no se congelan aquí.

También deben exigirse:

```text
varios timestamp clusters;
dispersión temporal suficiente;
persistencia;
calidad fuente.
```

No basta con notional aislado.

---

## 15. Matching, deduplicación y falsas activaciones

La ventana de matching no define Wake-up. Solo vincula una alerta causal con un onset retrospectivo.

Debe congelarse separadamente:

```text
maximum early lead;
maximum late delay;
one-to-one matching;
multiple-alert treatment;
multiple-event treatment;
merge gap;
closure duration;
refractory period;
session reset.
```

Regla fundamental:

```text
20 segundos consecutivos sobre threshold
=
una activation episode

no
=
20 falsas activaciones
```

Definición futura:

```text
false activation
=
activation episode no emparejado
con ningún POSITIVE_WAKE_UP válido
bajo el matching contract congelado
```

El presupuesto debe expresarse como:

```text
false activation episodes
per million eligible symbol-seconds
```

y traducirse además a:

```text
falsas alertas por sesión/día
```

---

## 16. Candidate Event Instance contract

Ejemplo no autoritativo:

```yaml
event_instance_id: WU_<instrument>_<timestamp>
event_type_id: event_type:market_activity:wake_up
event_type_version: v0_1_candidate
subject_scope: instrument
instrument_id: <governed instrument id>

observation_profile_id: <rth or full-session profile>
reference_onset_timestamp_utc: <retrospective onset or null>
onset_interval_start_utc: <optional>
onset_interval_end_utc: <optional>

detected_at_utc: <causal detector time>
available_at_utc: <legal delivery time>

minimal_evidence:
  primary_information_object: trading_activity
  market_state_ids: []
  evidence_state: confirmed

composite_corroboration:
  price_movement: optional
  volatility_range_state: optional
  market_microstructure_state: optional
  order_flow_pressure: optional

context:
  liquidity: optional
  price_location_structure: optional
  fundamental_context: optional
  news_catalyst_context: optional
  halt_context: optional

restrictions:
  - candidate_event_type_not_admitted
  - research_only_until_separate_authorization
```

---

## 17. Relación con Episode Instance y Event State

Un Wake-up positivo puede iniciar:

```text
episode_instance_id
```

que conservará:

```text
instrument_id;
wake-up event id;
episode start;
activation references;
phase;
episode HOD;
bursts;
halts;
expiration;
termination state.
```

Event State puede contextualizar Market State respecto al Wake-up:

```text
pre_event
at_event
post_event
```

Pero:

```text
una fila pre_event
no era conocible como “pre_event”
antes de detectar el evento.
```

Por tanto, la relación retrospectiva `pre_event` es:

```text
research_only
```

en el timestamp original, salvo que se recupere después de la detección como contexto histórico disponible para una decisión posterior.

Event State no debe convertirse obligatoriamente en dependencia de baja latencia del detector. El tracker puede consumir Market State + Episode Memory y materializar Event State para investigación, replay y auditoría.

---

## 18. Protocolo de calibración requerido

Antes de congelar el label:

1. Construir un panel independiente de A/B.
2. Incluir positivos, negativos, ambiguos, unavailable y left-censored.
3. Incluir múltiples horas y regímenes.
4. Evaluar, como candidatos y no como autoridad:

```text
confirmation horizons:
30s, 60s, 120s, 300s

prior observed dormancy:
15m, 30m, 60m

relative anomaly:
varios niveles de cola PIT

corroboration:
distinct clusters
+ temporal dispersion
+ dollar volume

economic floor:
varios niveles derivados de development
```

5. Buscar una región estable de parámetros.
6. Ejecutar auditoría humana ciega:
   - dos revisores;
   - adjudicación de desacuerdos;
   - sin scores A/B;
   - sin resultados de estrategia.
7. Congelar el oracle y sus hashes antes de comparar A/B.

Los gráficos de un minuto pueden ayudar a construir la ontología, pero no son autoridad suficiente del segundo o microsegundo exacto del onset.

---

## 19. Pruebas científicas separadas

### 19.1 Prueba de fidelidad del Information Object

```text
Binding A
vs.
Binding B
```

Objetivo:

```text
representar y detectar
la transición mínima de Trading Activity
```

Contexto prohibido en esta comparación:

```text
price;
liquidity;
order flow;
news;
halts;
PnL.
```

### 19.2 Prueba de utilidad dentro del Wake-up completo

Después:

```text
Common multiobject context + Binding A
vs.
Common multiobject context + Binding B
```

Objetivos posibles:

```text
WAKE_UP_COMPOSITE_CORROBORATION;
DIRECTIONAL_ACTIVATION;
IN_PLAY_ELIGIBILITY.
```

Así se separa:

```text
qué binding representa mejor actividad
```

de:

```text
qué sistema multiobjeto detecta mejor
un episodio operable.
```

---

## 20. Criterios para congelar esta definición

Este documento solo podrá pasar a `FROZEN` cuando exista:

```text
1. Daily Eligible Universe policy adoptada y versionada.

2. RTH observation profile definido.

3. Full-session requirements declarados,
   aunque la implementación quede diferida.

4. Wake-up oracle calibration protocol congelado.

5. Label and negative definition contract.

6. Panel de calibración no sesgado.

7. Blind human audit protocol.

8. False activation counting contract.

9. Matching and deduplication contract.

10. Exact temporal legality and source-quality policy.

11. Evidencia de que el oracle no favorece
    a Binding A ni a Binding B.

12. Human scientific freeze explícito.
```

Criterios de rechazo:

```text
labels dependen de rebreak, retorno o PnL;
un solo print puede crear Wake-up;
unavailable se trata como negativo;
el onset se inventa fuera de la resolución fuente;
la definición cambia después de observar A/B;
el parent universe se selecciona retrospectivamente;
el detector consume confirmation_end futura.
```

---

## 21. Límites actuales

Este documento no autoriza:

```text
Event Type admission;
Event Instance creation;
label materialization;
Binding B implementation;
A/B comparison;
temporal validation;
final OOS;
strategy consumption;
production;
downstream;
canonical promotion.
```

La fuente legacy de Binding A/B actual solo permite investigación RTH restringida. Un claim full-session exige fuentes premarket/RTH/after-hours, nueva materialización y validación específica.

---

## 22. Artefactos siguientes

```text
01_WAKE_UP_EVENT_DEFINITION_v0_1.md
=
este documento

02_WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md

03_WAKE_UP_ORACLE_CALIBRATION_PROTOCOL_v0_1.md

04_WAKE_UP_FALSE_ACTIVATION_COUNTING_CONTRACT_v0_1.md

05_WAKE_UP_RTH_OBSERVATION_PROFILE_v0_1.md

06_WAKE_UP_FULL_SESSION_REQUIREMENTS_v0_1.md

07_WAKE_UP_DEVELOPMENT_LABEL_MANIFEST_v0_1

08_WAKE_UP_TEMPORAL_VALIDATION_MANIFEST_v0_1

09_WAKE_UP_EVENT_TYPE_ADMISSION_REVIEW_v0_1
```

Los nombres son propuestas documentales, no artefactos autorizados todavía.

---

## 23. Fuentes internas utilizadas

Este borrador sintetiza y respeta la terminología de:

- `TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md`
- `TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md`
- `TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md`
- `TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md`
- `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_13.md`
- análisis de los ejemplos visuales Wake-up aportados;
- propuesta de Daily Eligible Universe / Screener Engine;
- discusiones científicas sobre Wake-up, Trading Activity y arquitectura multiobjeto.

Cuando estas fuentes discrepan o no congelan una cantidad, este documento mantiene la decisión como abierta.

---

## 24. Definición resumida

```text
Wake-up es el primer cambio corroborado
desde una condición contextual de baja participación negociada
hacia una condición de participación realizada,
anómala, multievento y económicamente material.

Trading Activity ancla el onset mínimo.

Los demás Information Objects describen
dirección, expansión, microestructura,
operabilidad, estructura, causa y continuidad.

Wake-up no equivale a In-Play,
rebreak, entrada ni resultado rentable.

El horario no cambia el fenómeno;
cambia el baseline, el scope observable
y el observation profile autorizado.
```
