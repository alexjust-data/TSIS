# TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_latency_policy_registry` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_SIMULATED_LATENCY_POLICY_REGISTRY` |
| `document_status` | `FROZEN_FOR_FIRST_RTH_EXPERIMENT` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `availability_mode` | `SIMULATED_NOT_OBSERVED` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Proposito

Preregistrar un conjunto finito y determinista de latencias simuladas para
reconstrucciones historicas RTH donde TSIS no dispone de `observed_at` ni
`available_at` reales por trade.

Estos valores son escenarios experimentales. No son mediciones historicas del
proveedor, de la red ni de TSIS.

---

## 2. Registro

| `latency_policy_id` | Latencia | Rol |
|---|---:|---|
| `LATENCY_PRIMARY_CONSERVATIVE_V0_1` | 1000 ms | Politica primaria preregistrada. |
| `LATENCY_SENSITIVITY_LOW_V0_1` | 100 ms | Sensibilidad de latencia baja. |
| `LATENCY_SENSITIVITY_HIGH_V0_1` | 5000 ms | Sensibilidad conservadora alta. |

El resultado principal del primer experimento debe usar:

```text
LATENCY_PRIMARY_CONSERVATIVE_V0_1
```

Las otras politicas no pueden sustituirla despues de observar outcomes; solo
pueden publicarse como analisis de sensibilidad preregistrado.

---

## 3. Formula

```text
simulated_available_at_i
= source_causal_anchor_i + latency_ms(policy_id)
```

Un evento puede consumirse cuando:

```text
simulated_available_at_i <= decision_clock
```

Los empates se incluyen. La aritmetica se ejecuta en UTC y la conversion de
sesion se realiza separadamente con calendario `America/New_York`.

---

## 4. Ambito

```text
source
= trades_ticks_prod_2005_2026_legacy_rth_reduced

session
= RTH only

source period
= all physically audited legacy periods
```

No se permite variar la latencia por ticker, precio, outcome, ano o nivel de
actividad dentro de una misma policy version.

---

## 5. Metadata obligatoria

```text
latency_policy_id
latency_policy_version
latency_ms
availability_mode = SIMULATED_NOT_OBSERVED
source_causal_anchor_type
source_schema_version
decision_clock
feature_input_max_available_at
```

---

## 6. Tests

```text
1. non-negative latency
2. deterministic UTC addition
3. equality at decision clock is consumable
4. event one microsecond after decision clock is not consumable
5. stable result across rebuilds
6. explicit primary/low/high separation
7. no ticker-specific override
8. no outcome-conditioned override
9. DST does not alter UTC latency arithmetic
10. missing policy id fails closed
```

---

## 7. Revalidacion

Tras el backfill Massive se revisara el `source_causal_anchor`, pero la descarga
historica seguira sin recrear la llegada real a TSIS. La disponibilidad real
solo podra validarse prospectivamente mediante captura live/shadow.

```text
MASSIVE_FULL_HISTORY_BACKFILL_AUDITED
=> REQUIRES_REVALIDATION

LIVE_TEMPORAL_CAPTURE_VALIDATED
=> measured latency policies may be proposed under a new version
```

---

## 8. Estado

```text
POLICY REGISTRY               = FROZEN_FOR_FIRST_RTH_EXPERIMENT
PRIMARY POLICY                = LATENCY_PRIMARY_CONSERVATIVE_V0_1
MEASURED HISTORICAL LATENCY   = NOT_AVAILABLE
EXPERIMENTAL USE              = CONDITIONALLY_AUTHORIZABLE_AFTER_SOURCE_GATE
CANONICAL PROMOTION           = NOT_AUTHORIZED
```

