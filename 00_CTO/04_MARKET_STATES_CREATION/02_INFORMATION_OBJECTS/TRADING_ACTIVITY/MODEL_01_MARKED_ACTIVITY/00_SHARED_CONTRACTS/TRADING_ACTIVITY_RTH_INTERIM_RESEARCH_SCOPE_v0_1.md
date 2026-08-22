# TRADING_ACTIVITY_RTH_INTERIM_RESEARCH_SCOPE_v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_rth_interim_research_scope` |
| `document_version` | `v0_1` |
| `document_role` | `INTERIM_RESEARCH_SCOPE_CONTRACT` |
| `document_status` | `DRAFT_CANDIDATE` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `source_id` | `trades_ticks_prod_2005_2026_legacy_rth_reduced` |
| `session_scope` | `REGULAR_TRADING_HOURS_ONLY` |
| `availability_mode` | `SIMULATED_NOT_OBSERVED` |
| `backfill_dependency` | `../_MASSIVE_TRADES_FULL_BACKFILL_REQUIREMENTS.md` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `predictive_consumption` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Decisión transitoria

TSIS continuará la investigación y la implementación física experimental de
`Trading Activity` utilizando temporalmente los trades legacy de market hours.

```text
CURRENT OPERATING SCOPE
=
LEGACY_RTH_RECONCILED_EVENT_TIME_RESEARCH_ONLY
```

Este scope existe únicamente hasta que se complete y audite:

```text
Massive full universe
× full history
× premarket + RTH + after-hours
× complete provider trade payload
```

El scope transitorio no sustituye el objetivo científico completo de Wake-up.

---

## 2. Sesión incluida

```text
REGULAR TRADING HOURS
09:30:00 <= America/New_York < 16:00:00
```

Los límites efectivos deberán resolverse mediante calendario gobernado para:

```text
DST
half days
exchange holidays
exceptional sessions
```

---

## 3. Sesiones temporalmente fuera de scope

```text
PREMARKET
= OUT_OF_SCOPE_PENDING_MASSIVE_BACKFILL

AFTER-HOURS
= OUT_OF_SCOPE_PENDING_MASSIVE_BACKFILL
```

Fuera de scope no significa irrelevante ni descartado. Significa que no existe
todavía cobertura física suficiente en el dataset legacy evaluado.

---

## 4. Rectificación semántica esencial

Con RTH solamente puede observarse:

```text
primera transición de actividad observada durante RTH
```

No puede afirmarse universalmente:

```text
primer Wake-up del episodio completo
```

porque el instrumento podría haberse activado en premarket.

Por tanto, durante este scope las etiquetas de investigación permitidas son:

```text
RTH_ACTIVITY_TRANSITION_CANDIDATE
RTH_ACTIVATION_CANDIDATE
RTH_REACTIVATION_CANDIDATE
```

No se promoverá desde este scope:

```text
WAKE_UP_DETECTED as full-session Event Type
```

---

## 5. Qué trabajo puede continuar ahora

```text
Trading Activity source audit
trade eligibility research policy
temporal and missingness policy
RTH PIT baseline design
Binding A experimental physical specification
RTH variable implementation
feature validity tests
RTH false-alarm research
RTH OOS comparison
```

---

## 6. Qué queda bloqueado

```text
full-session Wake-up claim
episode-opening claim when premarket is unobserved
premarket baseline calibration
after-hours continuity
provider-ID causal dedupe
as-of correction/cancellation replay
observed historical TSIS availability
C1/C2 promotion
canonical feature promotion
predictive consumption
strategy and execution
```

---

## 7. Artefactos gobernados por este scope

```text
TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md

TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md

TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md

TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md
```

Todos deberán declarar:

```text
scope_id
= legacy_rth_reconciled_event_time_research_only

sunset_trigger
= MASSIVE_FULL_HISTORY_BACKFILL_AUDITED
```

---

## 8. Condición de caducidad

Cuando el backfill Massive quede descargado y supere su auditoría:

```text
1. este scope no se promociona automáticamente;
2. cambia a REQUIRES_REVALIDATION;
3. se reejecuta Source Observability Audit;
4. se recalibran baselines por sesión;
5. se reconstruyen variables con timestamps enriquecidos;
6. se comparan resultados legacy RTH frente a full-session;
7. se decide qué componentes sobreviven o se versionan.
```

No se mezclarán silenciosamente features producidas con la fuente legacy y con
la fuente Massive enriquecida.

---

## 9. Regla de lineage

Toda fila o feature producida bajo este scope deberá referenciar:

```text
scope_id
source_dataset_id
source_schema_version
trade_eligibility_policy_id
temporal_missingness_contract_id
baseline_policy_id
binding_specification_id
availability_mode
quality_state
feature_input_max_available_at
```

---

## 10. Secuencia de trabajo

```text
RTH Interim Research Scope
↓
Trade Eligibility Policy
+ Temporal and Missingness Contract
↓
PIT Baseline Policy RTH
↓
Binding A Exact Experimental Specification
↓
RTH Experimental Variables
↓
Validation and OOS Comparison
↓
Massive Backfill Audit when available
↓
Full-Session Revalidation
```

---

## 11. Estado final

```text
RTH_RESEARCH
= AUTHORIZED_TO_CONTINUE UNDER RESTRICTIONS

PREMARKET_AND_AFTER_HOURS
= DEFERRED_PENDING_MASSIVE_BACKFILL

FULL_WAKE_UP_SEMANTICS
= NOT_AUTHORIZED FROM RTH-ONLY DATA

CANONICAL_PROMOTION
= NOT_AUTHORIZED

SUNSET_TRIGGER
= MASSIVE_FULL_HISTORY_BACKFILL_AUDITED
```
