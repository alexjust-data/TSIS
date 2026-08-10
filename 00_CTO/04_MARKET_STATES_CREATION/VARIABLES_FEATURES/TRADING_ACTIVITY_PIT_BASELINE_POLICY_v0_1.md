# TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_pit_baseline_policy` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_PIT_BASELINE_POLICY` |
| `document_status` | `DRAFT_CANDIDATE` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `session_scope` | `REGULAR_TRADING_HOURS_ONLY` |
| `source_revision_mode` | `RECONCILED_FINAL_ONLY` |
| `baseline_temporality` | `PRIOR_INFORMATION_ONLY` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Propósito

Definir cómo construir baselines point-in-time para comparar la actividad RTH
actual del instrumento con su régimen histórico contextual.

```text
RELATIVE SURPRISE
=
current observable activity
versus
baseline available before decision time
```

Este documento no define el detector Wake-up ni sus thresholds.

---

## 2. Dependencia Massive y condición de caducidad

Esta política utiliza temporalmente la fuente legacy RTH.

Cuando el backfill Massive quede descargado y auditado deberá:

```text
1. cambiar a REQUIRES_REVALIDATION;
2. incorporar premarket y after-hours como regímenes separados;
3. reconstruir timestamps y elegibilidad con schema enriquecido;
4. recalcular todos los baselines;
5. comparar estabilidad legacy versus enriched;
6. prohibir mezcla silenciosa de baseline versions.
```

---

## 3. Población PIT

Para un instrumento `s`, trading date `d`, reloj RTH `c` y ventana `W`:

```text
B(s,d,c,W)
=
observaciones de sesiones anteriores d' < d
que estaban disponibles según el cutoff del experimento
y pertenecen al mismo contexto gobernado
```

Está prohibido usar:

```text
datos posteriores a d
datos posteriores al decision timestamp dentro de d
clasificaciones futuras de liquidez
universe membership retrospectiva
outcomes o labels Wake-up
scanner appearance futura
full-year statistics todavía no disponibles
```

---

## 4. Unidad contextual RTH

El baseline mínimo se condiciona por:

```text
instrument_id PIT
RTH session
clock-time bucket
window W
trade eligibility policy version
source schema regime
```

Clock bucket candidato inicial:

```text
1 minute of America/New_York RTH clock
```

La apertura y las medias sesiones no se mezclarán con minutos que representen
otro régimen horario.

---

## 5. Variables base del baseline

Por cada `W` se conservarán distribuciones históricas de:

```text
eligible_trade_count_W
eligible_share_volume_W
eligible_dollar_volume_W
trade_arrival_rate_W
median_intertrade_duration_W when calculable
max_subwindow_trade_share_W
max_subwindow_volume_share_W
```

El baseline no almacena etiquetas Wake-up ni outcomes.

---

## 6. Registro de lookbacks experimentales

```text
B20
= prior 20 eligible RTH sessions

B60
= prior 60 eligible RTH sessions

B120
= prior 120 eligible RTH sessions
```

Uso inicial:

```text
B60
= primary development candidate

B20 and B120
= sensitivity candidates
```

Estos lookbacks son candidatos experimentales, no valores canónicos. La
comparación OOS deberá evaluar estabilidad, cobertura y retardo de adaptación.

---

## 7. Masa en cero

Microcaps dormidas pueden tener muchas ventanas sin trades. Por tanto, cada
baseline debe separar:

```text
zero_probability
= P(x = 0)

positive_distribution
= distribution of x conditional on x > 0
```

No se permite calcular una media única que oculte la masa en cero.

Outputs mínimos:

```text
baseline_zero_fraction
baseline_positive_count
baseline_total_count
baseline_positive_median
baseline_positive_mad
baseline_positive_percentiles
```

---

## 8. Estadísticos robustos

Por distribución se conservarán como candidatos:

```text
median
MAD
p50
p75
p90
p95
p99 when sample size permits
```

Los percentiles no se publican cuando la cardinalidad no alcanza el mínimo
establecido por el baseline specification del experimento.

No se imputa dispersión cero como evidencia de certeza.

---

## 9. Estados de cálculo

```text
BASELINE_AVAILABLE
BASELINE_AVAILABLE_WITH_RESTRICTIONS
BASELINE_ZERO_DOMINATED
BASELINE_INSUFFICIENT_HISTORY
BASELINE_DEGRADED
BASELINE_UNAVAILABLE
```

Cada estado debe conservar:

```text
reference_session_count
reference_observation_count
positive_observation_count
zero_observation_count
first_reference_date
last_reference_date
baseline_input_max_available_at
```

---

## 10. Fallback hierarchy candidata

```text
LEVEL 1
instrument + RTH minute bucket + W

LEVEL 2
instrument + broader RTH phase + W

LEVEL 3
instrument + full RTH + W

LEVEL 4
BASELINE_UNAVAILABLE
```

No se activa todavía un peer-group fallback. Añadirlo exigiría un Universe and
Peer Context Contract PIT para evitar clasificaciones retrospectivas.

RTH phases candidatas:

```text
OPENING       09:30-10:00
MIDDAY        10:00-15:30
CLOSING       15:30-session close
```

Los límites son experimentales y calendar-aware.

---

## 11. Nuevos, sparse y corporate actions

### 11.1 Historia insuficiente

Un ticker sin historia suficiente produce:

```text
BASELINE_INSUFFICIENT_HISTORY
```

No se sustituye silenciosamente por cero o por una distribución futura.

### 11.2 Symbol changes

La continuidad se resuelve mediante `instrument_id` PIT, no solo ticker.

### 11.3 Splits y cambios de escala

No se aplican factores corporativos conocidos posteriormente. La política
candidata debe segmentar regímenes cuando un cambio de escala material haga no
comparable la historia previa.

```text
corporate_action_regime_id
```

debe acompañar al baseline cuando exista autoridad PIT suficiente.

---

## 12. Surprise transforms candidatos

Para `x >= 0`:

```text
log_ratio(x, m, epsilon)
=
log((x + epsilon) / (m + epsilon))
```

Epsilons dimensionales candidatos:

```text
trade count     1 trade
share volume    1 share
dollar volume   1 USD
arrival rate    1 / observable_window_seconds
```

Robust z-score candidato:

```text
robust_z
=
(x - median) / max(1.4826 × MAD, governed_scale_floor)
```

`governed_scale_floor` debe definirse por variable y no puede ajustarse después
de observar resultados OOS.

---

## 13. Metadata obligatoria

```text
baseline_policy_id
baseline_policy_version
baseline_candidate_id
scope_id
instrument_id
session_phase
clock_bucket
window
lookback_sessions
trade_eligibility_policy_id
source_schema_version
reference counts
zero fraction
center and scale method
fallback level
baseline_input_max_available_at
calculation_state
quality_state
lineage_manifest_id
```

---

## 14. Tests mínimos

```text
1. no future session enters baseline
2. no same-day future window enters baseline
3. zero-dominated dormant instrument
4. active instrument with stable positive distribution
5. new ticker with insufficient history
6. symbol change with stable instrument identity
7. split or material scale change
8. half day
9. DST period
10. missing reference sessions
11. schema regime change
12. B20/B60/B120 sensitivity
13. fallback level transition
14. baseline rebuild reproducibility
```

---

## 15. Estado de decisión

```text
PIT TEMPORALITY
= SPECIFIED

RTH CONTEXT
= SPECIFIED AS CANDIDATE

LOOKBACK REGISTRY
= B20 / B60 / B120 CANDIDATES

PRIMARY DEVELOPMENT CANDIDATE
= B60

PEER FALLBACK
= NOT_AUTHORIZED

PREMARKET_AND_AFTER_HOURS BASELINES
= DEFERRED_PENDING_MASSIVE_BACKFILL

CANONICAL BASELINE
= NOT_SELECTED
```

