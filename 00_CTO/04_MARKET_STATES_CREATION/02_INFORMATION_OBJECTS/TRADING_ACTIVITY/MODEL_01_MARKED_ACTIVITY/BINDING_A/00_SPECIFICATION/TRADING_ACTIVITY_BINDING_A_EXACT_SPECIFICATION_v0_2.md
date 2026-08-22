# TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_binding_a_exact_specification` |
| `document_version` | `v0_2` |
| `document_role` | `EXPERIMENTAL_PHYSICAL_BINDING_SPECIFICATION` |
| `document_status` | `IMPLEMENTATION_DESIGN_FROZEN_FOR_DETERMINISTIC_PILOT` |
| `binding_id` | `trading_activity_binding_a_minimal_multiscale_rth_v0_2` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `source_id` | `trades_ticks_prod_2005_2026_legacy_rth_reduced` |
| `trade_eligibility_policy` | `TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md` |
| `temporal_missingness_contract` | `TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md` plus governing amendment |
| `baseline_policy` | `TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md` plus governing amendment |
| `latency_registry` | `TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md` |
| `decision_unit` | `SYMBOL_SECOND` |
| `availability_mode` | `SIMULATED_NOT_OBSERVED` |
| `supersession_history` | `predecessor consolidated and removed 2026-08-07` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Proposito

Cerrar los parametros necesarios para implementar Binding A sin convertirlos
en semantica canonica ni en un detector Wake-up.

```text
Binding A
=
absolute activity
+ event intensity
+ basic marks
+ basic temporal concentration
+ PIT-relative surprise
+ transition dynamics
+ minimal anti-artifact corroboration
```

---

## 2. Unidad y rejilla de decision

```text
experimental sampling unit
=
symbol-second
```

Para cada sesion XNYS gobernada se emite un `decision_timestamp` por segundo
entero UTC tal que:

```text
session_open_utc < decision_timestamp < session_close_utc
```

```text
decision_clock
=
decision_timestamp
```

Las sesiones, DST y early closes proceden de:

```text
market_calendar_v0_1
calendar = XNYS
```

No se generan puntos premarket ni after-hours.

Esta unidad queda congelada solo para el primer piloto. No resuelve la unidad
definitiva del Detector Experiment Contract.

---

## 3. Ventanas y bordes

```text
W_SET_V0_2
= {5s, 15s, 30s, 60s, 300s}

SHORT_LONG_PAIRS_V0_2
= {(5s, 60s), (15s, 300s)}
```

Cada ventana es:

```text
(decision_timestamp - W, decision_timestamp]
```

Una ventana es calculable solo si:

```text
decision_timestamp - W >= session_open_utc
AND coverage_gate_state = PASS_WITH_RESTRICTIONS
```

Antes de acumular `W` segundos completos:

```text
observation_state
= OBSERVED_ZERO or OBSERVED_NONZERO when physically inspectable

calculation_state
= INSUFFICIENT_WINDOW_HISTORY

primary feature values
= NULL
```

No se reduce el denominador.

---

## 4. Disponibilidad simulada

Por trade elegible:

```text
simulated_available_at_i
=
legacy_event_time_i + latency(policy_id)
```

Registro:

```text
LATENCY_PRIMARY_CONSERVATIVE = 1,000 ms
LATENCY_SENSITIVITY_LOW      =   100 ms
LATENCY_SENSITIVITY_HIGH     = 5,000 ms
```

Un trade entra en `T_W(t)` solo si:

```text
legacy_event_time_i <= decision_timestamp
simulated_available_at_i <= decision_clock
```

La politica primaria del piloto es:

```text
LATENCY_PRIMARY_CONSERVATIVE
```

Las otras dos politicas se ejecutan como sensibilidad separada y nunca se
mezclan dentro del mismo `latency_policy_id`.

---

## 5. Elegibilidad y calidad de ventana

Input admitido:

```text
trade_activity_eligibility_state
= ELIGIBLE_WITH_RESTRICTIONS
```

Input excluido:

```text
INELIGIBLE
UNKNOWN_FAIL_CLOSED
```

Si existe un `UNKNOWN_FAIL_CLOSED` fisico dentro de la ventana:

```text
observation_state = DEGRADED
calculation_state = NOT_CALCULATED_COVERAGE_GATE_FAILED
primary feature values = NULL
```

Los codigos conocidos excluidos por politica no degradan la ventana; forman
parte de la definicion experimental de elegibilidad.

Los duplicados exactos se preservan en la ejecucion primaria. Una vista de
sensibilidad puede excluir solo las repeticiones posteriores, con otro
`duplicate_policy_id`.

---

## 6. Actividad absoluta

Para cada `W` calculable:

```text
eligible_trade_count_W
= count(T_W(t))

eligible_share_volume_W
= sum(size_i)

eligible_dollar_volume_W
= sum(price_i * size_i)
```

Si no hay trades elegibles y la cobertura pasa:

```text
observation_state = OBSERVED_ZERO
count = 0
share volume = 0
dollar volume = 0
```

---

## 7. Intensidad y duraciones

```text
trade_arrival_rate_W
=
eligible_trade_count_W / W_seconds
```

El denominador siempre es la duracion registrada completa de `W`.

Las duraciones se calculan solo entre pares cuyos dos eventos pertenecen a
`T_W(t)`, ordenados por:

```text
legacy_event_time
physical_row_ordinal
```

```text
median_intertrade_duration_us_W
p10_intertrade_duration_us_W
```

Con menos de dos trades:

```text
duration_calculation_state = INSUFFICIENT_SAMPLE
duration values = NULL
```

Los ties conservan duracion cero. No se usa un trade futuro ni un carry-in no
gobernado para completar la duracion de borde.

---

## 8. Marks y concentracion

```text
largest_trade_volume_share_W
= max(size_i) / eligible_share_volume_W
```

Subventana:

```text
W <= 30s -> w = 1s
W > 30s  -> w = 5s
```

Las subventanas se anclan al borde derecho de la ventana completa:

```text
(t-W, t-W+w]
...
(t-w, t]
```

```text
active_subwindow_fraction_W_w
max_subwindow_trade_share_W_w
max_subwindow_volume_share_W_w
consecutive_active_subwindows_W_w
```

Sin actividad:

```text
concentration_calculation_state
= NOT_APPLICABLE_ZERO_ACTIVITY

concentration values
= NULL
```

No se imputa concentracion cero.

---

## 9. Baseline PIT

```text
BASELINE_CANDIDATES
= {B20, B60, B120}

PRIMARY DEVELOPMENT
= B60
```

Para un ticker, fecha, minuto ET y `W`, cada baseline usa las sesiones
elegibles anteriores mas recientes:

```text
B20  -> prior 20 sessions
B60  -> prior 60 sessions
B120 -> prior 120 sessions
```

Poblacion de observaciones:

```text
all calculated symbol-seconds
from the same America/New_York clock-minute bucket
in prior eligible sessions
for the same W, latency policy, eligibility policy and schema regime
```

No entra ninguna observacion de la sesion actual ni de fechas futuras.

Una sesion `DOWNLOADED_EMPTY` gobernada aporta ceros observados. Una sesion
`UNAVAILABLE` no entra en el baseline.

Cardinalidades minimas:

| Baseline | Sesiones | Observaciones totales |
|---|---:|---:|
| `B20` | 15 | 15 |
| `B60` | 40 | 40 |
| `B120` | 80 | 80 |

Masa en cero:

```text
baseline_zero_fraction
= count(x = 0) / baseline_total_count
```

```text
ZERO_DOMINATED_PRIMARY
= baseline_zero_fraction >= 0.80
```

La mediana usada por el log-ratio es incondicional e incluye ceros.

---

## 10. Percentiles PIT

Nombres gobernados:

```text
trade_count_percentile_pit_W_B
share_volume_percentile_pit_W_B
dollar_volume_percentile_pit_W_B
arrival_rate_percentile_pit_W_B
```

Definicion empirica:

```text
percentile(x)
=
count(reference_value <= x) / baseline_total_count
```

No se usa interpolacion ni midrank en v0_2.

Minimos positivos para estadisticos positivos:

```text
median and MAD = 10
p50            = 10
p75            = 20
p90            = 50
p95            = 100
p99            = 500
```

---

## 11. Sorpresa relativa

```text
trade_count_log_ratio_to_pit_W_B
= log((count_W + 1 trade) / (median_count_B + 1 trade))

share_volume_log_ratio_to_pit_W_B
= log((shares_W + 1 share) / (median_shares_B + 1 share))

dollar_volume_log_ratio_to_pit_W_B
= log((dollars_W + 1 USD) / (median_dollars_B + 1 USD))
```

Si el baseline no supera cardinalidad:

```text
baseline_calculation_state = BASELINE_INSUFFICIENT_HISTORY
relative feature values = NULL
```

---

## 12. Contraste multiescala

Nombre gobernado:

```text
activity_rate_multiscale_log_ratio_Ws_Wl
= log(
    (trade_arrival_rate_Ws + epsilon_rate)
    /
    (trade_arrival_rate_Wl + epsilon_rate)
  )

epsilon_rate
= 1 / Wl_seconds
```

No se denomina aceleracion.

Compresion de duraciones:

```text
intertrade_duration_compression_W_B
= log(
    (baseline_median_intertrade_duration_W + 1 microsecond)
    /
    (median_intertrade_duration_W + 1 microsecond)
  )
```

Solo se calcula cuando ambas medianas existen.

---

## 13. Forma fisica experimental

El piloto puede materializar dos artefactos separados:

```text
CURRENT_STATE
grain = instrument_id, decision_timestamp, W, latency_policy_id

PIT_BASELINE_AND_SURPRISE
grain = instrument_id, decision_timestamp, W,
        latency_policy_id, baseline_candidate_id
```

Los contrastes multiescala pueden vivir en un tercer output experimental con
grain `instrument_id, decision_timestamp, pair_id, latency_policy_id`.

Esto no decide aun las tablas canonicas `000-018`.

---

## 14. Metadata obligatoria

```text
feature_spec_id
feature_version
binding_id
scope_id
instrument_id
ticker
decision_timestamp
window_seconds
subwindow_seconds
baseline_candidate_id when applicable
trade_eligibility_policy_id
latency_policy_id
duplicate_policy_id
source_dataset_id
source_schema_version
market_calendar_build_run_id
input_event_count
feature_input_max_available_at
observation_state
calculation_state per feature family
quality_state
coverage_mode
lineage_manifest_id
future_window_used = false
```

---

## 15. Tests obligatorios

```text
observed-zero
unavailable and degraded
one-trade window
same-timestamp trades
exact-duplicate preservation and sensitivity
unknown-condition degradation
left-boundary censoring
right-boundary no-lookahead
all W and w boundaries
fixed denominator
simulated latency tie
RTH open insufficient history
early close
DST
typed percentiles
zero-dominated baseline
B20/B60/B120 cardinalities
no current-day baseline input
deterministic rebuild
no outcome dependency
```

---

## 16. Autorizacion

```text
EXACT PILOT SPECIFICATION
= FROZEN_FOR_DETERMINISTIC_PILOT

COMPUTATIONAL KERNEL AND FIXTURES
= AUTHORIZED

DETERMINISTIC PILOT MATERIALIZATION
= AUTHORIZED

STRATIFIED OR OOS COMPARISON
= NOT_AUTHORIZED

TABLE MAPPING
= NOT_STARTED

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

Al auditarse el backfill Massive se debe crear una nueva version; nunca se
sobrescriben outputs legacy en sitio.
