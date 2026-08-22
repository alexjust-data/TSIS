# TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_contract_rectification_and_alignment` |
| `document_version` | `v0_1` |
| `document_role` | `GOVERNING_SEMANTIC_AND_CONTRACT_AMENDMENT` |
| `document_status` | `DRAFT_GOVERNING_AMENDMENT` |
| `information_object_id` | `trading_activity` |
| `representation_profile_id` | `wake_up_information_object_profile_candidate_v0_1` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `effective_precedence` | `OVERRIDES_CONFLICTING_CLAUSES_ONLY` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Proposito

Resolver las inconsistencias semanticas y contractuales detectadas antes de
implementar el primer binding experimental de `Trading Activity`.

Esta enmienda prevalece, solamente en las clausulas que rectifica, sobre:

```text
00_WAKE_UP_END_to_END.md
REPRESENTATION_MODELS.md
TRADING_ACTIVITY_RTH_INTERIM_RESEARCH_SCOPE_v0_1.md
TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md
TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1.md
TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md
TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md
TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md
```

No altera la definicion cientifica de Wake-up, no admite features canonicas y
no autoriza consumo predictivo.

---

## 2. Rectificacion de procedencia

Los nombres desalineados no aparecen en
`00_TABLES_MARKET_STATE_EVENT_STATE.md`. Aparecen en los artefactos especificos
de Wake-up:

```text
00_WAKE_UP_END_to_END.md
= PIT-NORMALIZED MULTISCALE MARKED ACTIVITY PROCESS
  + BURST DYNAMICS

REPRESENTATION_MODELS.md
= BASELINE-RELATIVE MARKED ACTIVITY PROCESS
  + PERSISTENCE
```

Por tanto, el documento arquitectonico general no se declara desactualizado por
esta causa. La rectificacion afecta al vocabulario especifico de Wake-up.

---

## 3. Nombre gobernante del modelo

```text
INFORMATION OBJECT
= Trading Activity

REPRESENTATION MODEL CANDIDATE
= ABSOLUTE-AND-PIT-RELATIVE
  MULTISCALE MARKED ACTIVITY PROCESS

representation_model_candidate_id
= absolute_and_pit_relative_multiscale_marked_activity_process
```

El nombre conserva expresamente las dos condiciones cientificas:

```text
ABSOLUTE
= materialidad observable sin normalizar

PIT-RELATIVE
= sorpresa respecto al baseline causal aplicable
```

`PIT-normalized` y `baseline-relative` quedan como aliases historicos, no como
el nombre gobernante para nuevos artefactos.

---

## 4. Dimension temporal gobernante

```text
TRANSITION DYNAMICS
AND MINIMAL ANTI-ARTIFACT CORROBORATION
```

Debe conservar:

```text
velocidad del cambio de intensidad
continuidad contemporanea minima
decaimiento observable
reactivacion
```

La continuidad minima solo descarta prints aislados y discontinuidades
microscopicas. No equivale a la persistencia economica posterior exigida para
confirmar `In-Play`.

Los nombres siguientes quedan deprecados como etiquetas gobernantes:

```text
BURST DYNAMICS
PERSISTENCE
ANTI-ARTIFACT PERSISTENCE
```

---

## 5. Frontera Binding A / Binding B

Se adopta la opcion que conserva en Binding A una estructura antinartefacto
minima y redefine Binding B como ampliacion explicita.

```text
BINDING A
= Minimal Multiscale Activity
  with Basic Anti-Artifact Structure
```

Binding A puede conservar:

```text
absolute counts, shares and notional
arrival rate
median and p10 intertrade duration
largest-trade volume share
basic active-subwindow coverage
maximum subwindow concentration
PIT-relative surprise
multiscale rate contrast
duration compression
maximum consecutive active subwindows
```

```text
BINDING B
= Expanded Marks, Duration Distribution
  and Concentration Geometry
```

Binding B debe añadir, como minimo, dimensiones que no esten ya en A:

```text
trade-size distribution beyond largest-trade share
trade-notional distribution
fuller intertrade-duration distribution
time since last eligible trade
event-time entropy or equivalent dispersion geometry
additional concentration geometry
```

La comparacion A/B debe registrar la lista exacta de variables exclusivas de B.
No se permite presentar una variable ya incluida en A como aportacion marginal
de B.

---

## 6. Separacion de estados

### 6.1 `observation_state`

```text
OBSERVED_NONZERO
OBSERVED_ZERO
DEGRADED
UNAVAILABLE
OUT_OF_SCOPE
```

### 6.2 `calculation_state`

```text
CALCULATED
INSUFFICIENT_SAMPLE
INSUFFICIENT_WINDOW_HISTORY
NOT_APPLICABLE_ZERO_ACTIVITY
BASELINE_UNAVAILABLE
NOT_CALCULATED_COVERAGE_GATE_FAILED
```

`INSUFFICIENT_SAMPLE` no es un estado de observacion. Una ventana puede estar
correctamente observada y, al mismo tiempo, no contener eventos suficientes
para calcular una duracion o un percentil.

---

## 7. Denominador de intensidad

La tasa principal no puede reducir su denominador para compensar cobertura
parcial.

```text
coverage_gate_state = PASS
AND full_window_inside_authorized_RTH = true

=>

trade_arrival_rate_W
= eligible_trade_count_W / elapsed_window_seconds_W

elapsed_window_seconds_W
= exact registered duration of W
```

Si el gate falla:

```text
observation_state
= DEGRADED or UNAVAILABLE

calculation_state
= NOT_CALCULATED_COVERAGE_GATE_FAILED

trade_arrival_rate_W
= NULL
```

Si la ventana no contiene aun `W` segundos completos desde la apertura:

```text
calculation_state
= INSUFFICIENT_WINDOW_HISTORY
```

Una futura tasa ajustada por cobertura debera tener otro `feature_spec_id`; no
podra sustituir silenciosamente la tasa principal.

---

## 8. Cardinalidad y semantica del baseline

Este registro queda congelado solo para el primer experimento RTH.

### 8.1 Cardinalidad minima por lookback

| Baseline | `minimum_reference_session_count` | `minimum_total_observation_count` |
|---|---:|---:|
| `B20` | 15 | 15 |
| `B60` | 40 | 40 |
| `B120` | 80 | 80 |

### 8.2 Cardinalidad minima por estadistico positivo

| Estadistico | Minimo de observaciones positivas |
|---|---:|
| mediana positiva | 10 |
| MAD positiva | 10 |
| p50 | 10 |
| p75 | 20 |
| p90 | 50 |
| p95 | 100 |
| p99 | 500 |

Un estadistico que no alcance su cardinalidad se publica como `NULL` con
`calculation_state = INSUFFICIENT_SAMPLE`.

### 8.3 Regla zero-dominated

```text
ZERO_DOMINATED_PRIMARY
= baseline_zero_fraction >= 0.80

ZERO_DOMINATED_SENSITIVITY
= baseline_zero_fraction >= 0.90
```

La regla es descriptiva y no constituye un threshold Wake-up.

### 8.4 Medianas usadas por las transformaciones

```text
m_count
m_shares
m_dollars
m_arrival_rate

= unconditional PIT median
  including observed zeros
```

Las medianas positivas se conservan separadamente y no sustituyen a `m_x` en
los log-ratios de Binding A.

### 8.5 Percentiles tipados

El nombre ambiguo `activity_percentile_pit_W_B` queda deprecado. Binding A debe
usar:

```text
trade_count_percentile_pit_W_B
share_volume_percentile_pit_W_B
dollar_volume_percentile_pit_W_B
arrival_rate_percentile_pit_W_B
```

Cada percentil se calcula sobre la distribucion PIT incondicional de su propia
variable, incluyendo ceros observados.

---

## 9. Registro de latencia

La disponibilidad historica simulada queda gobernada por:

```text
TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md
```

No se autoriza ejecutar Binding A sin `latency_policy_id` preregistrado.

---

## 10. Nombre matematico del contraste multiescala

El nombre siguiente queda deprecado:

```text
activity_rate_acceleration_Ws_Wl
```

Se sustituye por:

```text
activity_rate_multiscale_log_ratio_Ws_Wl
= log(
    (trade_arrival_rate_Ws + epsilon_rate)
    /
    (trade_arrival_rate_Wl + epsilon_rate)
  )

epsilon_rate
= 1 / elapsed_window_seconds_Wl
```

La formula es un contraste entre escalas, no una segunda derivada temporal.

---

## 11. Autorizaciones normalizadas

```text
DOCUMENT AUTHORING
= COMPLETE_AS_DRAFT

IMPLEMENTATION DESIGN
= SPECIFIED_WITH_REQUIRED_REVISIONS_APPLIED

CODE SCAFFOLDING AND DETERMINISTIC FIXTURES
= AUTHORIZED

EXPERIMENTAL DATA EXECUTION
= PENDING_LEGACY_SOURCE_GATE_CLOSE

EXPERIMENTAL MATERIALIZATION
= PENDING_LEGACY_SOURCE_GATE_CLOSE

CANONICAL IMPLEMENTATION
= NOT_AUTHORIZED

PREDICTIVE CONSUMPTION
= NOT_AUTHORIZED
```

---

## 12. Dependencia de Massive

Todo lo definido aqui es transitorio para la fuente legacy RTH.

```text
MASSIVE_FULL_HISTORY_BACKFILL_AUDITED
=>
REQUIRES_REVALIDATION
```

La revalidacion debe cubrir timestamps enriquecidos, secuencia, IDs,
correcciones, condiciones, premarket, after-hours, cobertura y nuevos baselines.
No se sobrescriben en sitio los outputs legacy.

---

## 13. Estado

```text
SEMANTIC_ALIGNMENT                = RESOLVED_BY_GOVERNING_AMENDMENT
BINDING_A_B_BOUNDARY              = RESOLVED
OBSERVATION_CALCULATION_BOUNDARY  = RESOLVED
RATE_DENOMINATOR_POLICY           = RESOLVED
BASELINE_PARAMETER_REGISTRY       = FROZEN_FOR_FIRST_RTH_EXPERIMENT
LATENCY_POLICY                    = GOVERNED_BY_SEPARATE_REGISTRY
LEGACY_SOURCE_GATE                = IN_PROGRESS
READY_FOR_CODE_SCAFFOLDING        = YES
READY_FOR_EXPERIMENTAL_EXECUTION  = NO
READY_FOR_FREEZE                  = NO
CANONICAL_PROMOTION               = NOT_AUTHORIZED
```

