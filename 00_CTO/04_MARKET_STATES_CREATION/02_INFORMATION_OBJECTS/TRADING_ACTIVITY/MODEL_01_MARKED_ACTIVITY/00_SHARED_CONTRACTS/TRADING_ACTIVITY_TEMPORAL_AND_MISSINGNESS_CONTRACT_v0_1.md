# TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_temporal_and_missingness_contract` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_TEMPORAL_MISSINGNESS_CONTRACT` |
| `document_status` | `DRAFT_CANDIDATE` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `source_id` | `trades_ticks_prod_2005_2026_legacy_rth_reduced` |
| `session_scope` | `REGULAR_TRADING_HOURS_ONLY` |
| `availability_mode` | `SIMULATED_NOT_OBSERVED` |
| `coverage_granularity_current` | `TICKER_DAY_WITH_WINDOW_INFERENCE_RESTRICTED` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Propósito

Definir cómo se interpretan el tiempo, la disponibilidad simulada, la cobertura,
los ceros y la ausencia de datos durante la implementación experimental de
`Trading Activity` con trades legacy RTH.

---

## 2. Naturaleza temporal de la fuente legacy

El downloader histórico construyó:

```text
legacy_timestamp
=
first_non_null(
  sip_timestamp,
  participant_timestamp,
  trf_timestamp
)
```

y lo persistió como:

```text
timestamp[us]
timezone-naive
```

La transformación original partió de UTC, pero la fila final no conserva:

```text
source_timestamp_type
source nanosecond precision
timezone metadata
arrival order
```

Por tanto:

```text
event_time_mode
= LEGACY_COLLAPSED_SOURCE_TIMESTAMP
```

---

## 3. Scope de sesión

```text
09:30:00 <= America/New_York < 16:00:00
```

La pertenencia a RTH se resuelve con calendario gobernado y conversión UTC
DST-aware. No se infiere únicamente con una hora fija UTC.

Premarket y after-hours quedan:

```text
OUT_OF_SCOPE_PENDING_MASSIVE_BACKFILL
```

---

## 4. Tiempos gobernados

| Campo | Significado |
|---|---|
| `decision_timestamp` | Instante de mercado representado. |
| `legacy_event_time` | `timestamp` físico legacy interpretado bajo su lineage. |
| `source_causal_anchor` | En legacy, `legacy_event_time` con restricción de timestamp colapsado. |
| `simulated_available_at` | `source_causal_anchor + simulated_latency`. |
| `feature_input_max_available_at` | Máximo `simulated_available_at` de los inputs. |
| `decision_clock` | Reloj contra el que se comprueba disponibilidad. |

No existen históricamente:

```text
observed_at_utc real de TSIS
available_at_utc real de TSIS
```

---

## 5. Política de disponibilidad simulada

```text
simulated_available_at_i
=
source_causal_anchor_i
+ latency(policy_id, session, source_period)
```

Reglas:

```text
latency_policy_id IS NOT NULL
latency >= 0
availability_mode = SIMULATED_NOT_OBSERVED
feature_input_max_available_at <= decision_clock
future_window_used = false
```

La latencia exacta no queda congelada en esta versión. Deberá preregistrarse en
el experimento mediante un conjunto finito de políticas candidatas y una
política conservadora principal.

No se permite ajustar latencia ticker por ticker después de observar outcomes.

---

## 6. Estados de observación

```text
OBSERVED_NONZERO
OBSERVED_ZERO
INSUFFICIENT_SAMPLE
DEGRADED
UNAVAILABLE
OUT_OF_SCOPE
```

### 6.1 `OBSERVED_NONZERO`

Existe al menos un trade elegible dentro de la ventana y la partición supera el
gate mínimo de cobertura.

### 6.2 `OBSERVED_ZERO`

No existe ningún trade elegible, pero debe existir evidencia positiva de que la
fuente cubrió el intervalo.

```text
zero rows found
!=
observed zero
```

### 6.3 `INSUFFICIENT_SAMPLE`

La ventana está observada, pero no contiene cardinalidad suficiente para una
feature concreta. Ejemplo: un trade permite count y volume, pero no una duración
intertrade.

### 6.4 `DEGRADED`

Existe información parcial o ambigua que permite algunas variables, pero no una
afirmación completa de cobertura o elegibilidad.

### 6.5 `UNAVAILABLE`

No existe evidencia suficiente para representar la ventana.

### 6.6 `OUT_OF_SCOPE`

La ventana pertenece a premarket, after-hours o a un periodo excluido por este
scope transitorio.

---

## 7. Evidencia de cobertura legacy

Estados de adquisición observados:

```text
DOWNLOADED_OK
DOWNLOADED_EMPTY
DOWNLOAD_FAIL
```

Regla candidata a nivel ticker-día:

| Evidencia | Estado de cobertura candidato |
|---|---|
| `DOWNLOADED_OK` + archivo legible + paginación terminada | `DAY_COVERAGE_OBSERVED_WITH_RESTRICTIONS` |
| `DOWNLOADED_EMPTY` + petición terminada correctamente | `DAY_OBSERVED_ZERO_WITH_RESTRICTIONS` |
| `DOWNLOAD_FAIL` | `UNAVAILABLE` |
| Sin manifest verificable | `UNAVAILABLE` |
| Archivo ilegible o mismatch de manifest | `DEGRADED` o `UNAVAILABLE` |

La fuente actual no conserva heartbeat intradía. Por tanto, la inferencia de
coverage por ventana hereda la evidencia del ticker-día y debe llevar:

```text
coverage_mode
= INFERRED_FROM_SUCCESSFUL_FULL_RTH_REQUEST
```

hasta que un test demuestre la suficiencia del manifest y la paginación.

---

## 8. Ventanas causales

Para una ventana `W` cerrada en `t`:

```text
T_W(t)
=
{
  i:
  t - W < legacy_event_time_i <= t
  AND simulated_available_at_i <= decision_clock
  AND trade_activity_eligibility_state_i is admissible
}
```

Se utilizarán intervalos:

```text
(t - W, t]
```

para evitar doble conteo entre ventanas contiguas.

---

## 9. Orden, ties y duraciones

La fuente legacy está establemente ordenada por `timestamp`, pero carece de
provider sequence.

Reglas:

```text
same timestamp rows remain preserved
zero intertrade durations are allowed as observed ties
physical row ordinal may reproduce storage order
physical row ordinal is not called causal source sequence
```

Features sensibles al orden total deben declarar:

```text
ORDER_RESTRICTED_LEGACY_SOURCE
```

---

## 10. Boundary censoring

Para intertrade durations:

```text
left boundary duration
= censored unless a governed carry-in event is available

right boundary duration
= not created using a future trade
```

No se busca el siguiente trade posterior a `decision_timestamp` para completar
una duración.

---

## 11. Missingness por feature

Cada feature debe emitir:

```text
value
calculation_state
observation_state
quality_state
input_event_count
observable_seconds
feature_input_max_available_at
latency_policy_id
coverage_mode
```

No se permite sustituir automáticamente:

```text
UNAVAILABLE -> 0
DEGRADED -> 0
INSUFFICIENT_SAMPLE -> 0
```

---

## 12. Tests mínimos

```text
1. full observed RTH window with trades
2. full observed RTH window without trades
3. DOWNLOAD_FAIL ticker-day
4. absent manifest
5. one-trade window
6. same-timestamp trades
7. left-boundary censoring
8. right-boundary no-lookahead
9. half day
10. DST transition
11. simulated latency tie
12. unknown condition degrades window
13. premarket row becomes OUT_OF_SCOPE
14. after-hours row becomes OUT_OF_SCOPE
```

---

## 13. Revalidación tras Massive

Cuando el backfill enriquecido sea auditado deberán revisarse:

```text
source_causal_anchor
nanosecond precision
provider sequence
participant/SIP/TRF separation
coverage sidecars
revision handling
session coverage
simulated latency policy
```

Las features legacy no se mezclarán con las enriquecidas sin versión y lineage
distintos.

---

## 14. Estado de decisión

```text
TEMPORAL FRAMEWORK
= SPECIFIED FOR LEGACY RTH RESEARCH

EXACT LATENCY POLICY
= NOT_FROZEN

WINDOW COVERAGE VALIDATION
= IN_PROGRESS

PREMARKET_AND_AFTER_HOURS
= DEFERRED_PENDING_MASSIVE_BACKFILL

OBSERVED HISTORICAL AVAILABILITY
= NOT_AVAILABLE

CANONICAL PROMOTION
= NOT_AUTHORIZED
```
