# TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_trade_eligibility_policy` |
| `document_version` | `v0_2` |
| `document_role` | `EXPERIMENTAL_TRADE_ELIGIBILITY_POLICY` |
| `document_status` | `DRAFT_EXECUTED_ON_DETERMINISTIC_PILOT` |
| `review_verdict` | `PASS_WITH_RESTRICTIONS_FOR_PILOT` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `source_id` | `trades_ticks_prod_2005_2026_legacy_rth_reduced` |
| `condition_snapshot_status` | `MATERIALIZED_AND_HASHED` |
| `condition_mapping_status` | `14_OF_55_CANDIDATE_REVIEWED` |
| `revision_mode` | `RECONCILED_FINAL_ONLY` |
| `supersession_history` | `predecessor consolidated and removed 2026-08-07` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Proposito

Definir que filas legacy RTH pueden contribuir experimentalmente a las
dimensiones fisicas de `Trading Activity` para Wake-up.

La decision se separa en cinco ejes:

```text
ACTIVITY EVENT
El mensaje representa actividad transaccional utilizable.

SHARE VOLUME
El tamano puede contribuir al volumen de acciones.

DOLLAR VOLUME
Precio por tamano puede contribuir al valor nocional.

CAUSAL ARRIVAL
El evento puede tratarse provisionalmente como contemporaneo en el
scope legacy event-time research-only.

PRICE FORMING
El precio puede contribuir a una trayectoria de precio separada.
```

Una regla del proveedor que actualiza volumen consolidado no demuestra por si
sola que el mensaje sea contemporaneo ni apto para detectar Wake-up.

```text
provider_consolidated_updates_volume
!=
causal_activity_eligible
```

---

## 2. Evidencia fuente versionada

Snapshot oficial materializado:

```text
tests/third_party_evidence/massive/market_operations/
snapshot_20260806T220504Z/
massive_stock_trade_conditions_normalized_v0_1.csv

SHA256
=
6325f5e61f783d20703a6ed188b6bf693d9d77c12c8e1050422195d8e8237398
```

Matriz derivada:

```text
tests/third_party_evidence/massive/market_operations/
snapshot_20260806T220504Z/policy_matrix_candidate_v0_1/
trading_activity_trade_condition_policy_matrix_candidate_v0_1.csv

SHA256
=
b2f208496809cb970437d04024d93bfb98780b54b5d790091362aa145eb9635f
```

Registro de decisiones:

```text
01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies/
trading_activity_wake_up_trade_condition_policy_candidate_v0_1.json

SHA256
=
b68e10b21f83b936ad55b9c9f810dceae539b2525ee45fba347300360e5a516e
```

El snapshot conserva 55 codigos actuales. No proporciona intervalos historicos
de vigencia; por tanto:

```text
historical_temporality_state
=
CURRENT_SNAPSHOT_NO_HISTORICAL_EFFECTIVE_INTERVAL
```

---

## 3. Estados y efectos

Estados de fila:

```text
ELIGIBLE_WITH_RESTRICTIONS
INELIGIBLE
UNKNOWN_FAIL_CLOSED
```

Efectos por eje:

```text
ALLOW
DENY
NO_RESTRICTION
REVIEW_REQUIRED
```

`ALLOW` nunca significa elegibilidad canonica. Bajo este scope se materializa
como `ELIGIBLE_WITH_RESTRICTIONS`.

---

## 4. Reglas generales

### 4.1 Sin condicion especial reportada

```text
conditions = []

state
=
ELIGIBLE_WITH_RESTRICTIONS

reason
=
NO_SPECIAL_CONDITION_REPORTED_LEGACY
```

No demuestra que el payload enriquecido original careciera de otros metadatos.

### 4.2 Codigo conocido y revisado

Se aplican los efectos de la matriz candidata por cada eje.

### 4.3 Codigo conocido pero no revisado

```text
KNOWN_BUT_UNREVIEWED
=
UNKNOWN_FAIL_CLOSED
```

### 4.4 Codigo ausente del snapshot

```text
UNKNOWN CONDITION CODE
=
UNKNOWN_FAIL_CLOSED
```

### 4.5 Multiples codigos

Por cada eje se aplica:

```text
DENY
>
REVIEW_REQUIRED
>
ALLOW
>
NO_RESTRICTION
```

Un qualifier `NO_RESTRICTION` no puede rehabilitar una condicion `DENY`.

---

## 5. Mapping candidato observado

| ID | Condicion | Actividad | Volumen | Nocional | Llegada causal | Precio | Reason code principal |
|---:|---|---|---|---|---|---|---|
| `2` | Average Price Trade | DENY | DENY | DENY | DENY | DENY | `NON_CAUSAL_AVERAGE_PRICE_REPORT` |
| `7` | Cash Sale | DENY | DENY | DENY | DENY | DENY | `SPECIAL_SETTLEMENT_FAIL_CLOSED` |
| `9` | Cross Trade | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `CROSS_TRANSACTION_REQUIRES_STRUCTURAL_CONTEXT` |
| `10` | Derivatively Priced | DENY | DENY | DENY | DENY | DENY | `DERIVATIVELY_PRICED_FAIL_CLOSED` |
| `12` | Form T/Extended Hours | DENY | DENY | DENY | DENY | DENY | `OUTSIDE_OR_NONCONTEMPORANEOUS_RTH_ACTIVITY` |
| `14` | Intermarket Sweep | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `INTERMARKET_SWEEP_TRANSACTION` |
| `16` | Market Center Official Open | DENY | DENY | DENY | DENY | DENY | `OFFICIAL_MARKER_NOT_TRANSACTION_ACTIVITY` |
| `17` | Market Center Opening Trade | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `OPENING_TRANSACTION_REQUIRES_SESSION_CONTEXT` |
| `31` | Sold Last and Stopped Stock | DENY | DENY | DENY | DENY | DENY | `LEGACY_TIMING_AMBIGUOUS_FAIL_CLOSED` |
| `32` | Sold Out Of Sequence | DENY | DENY | DENY | DENY | DENY | `OUT_OF_SEQUENCE_NOT_CAUSAL_ACTIVITY` |
| `37` | Odd Lot Trade | ALLOW | ALLOW | ALLOW | ALLOW | DENY | `ODD_LOT_ACTIVITY_NOT_PRICE_FORMING` |
| `41` | Trade Thru Exempt | NO RESTRICTION | NO RESTRICTION | NO RESTRICTION | NO RESTRICTION | NO RESTRICTION | `TRADE_THRU_EXEMPT_QUALIFIER` |
| `52` | Contingent Trade | DENY | DENY | DENY | DENY | DENY | `CONTINGENT_TRANSACTION_FAIL_CLOSED` |
| `53` | Qualified Contingent Trade | DENY | DENY | DENY | DENY | DENY | `QUALIFIED_CONTINGENT_TRANSACTION_FAIL_CLOSED` |

Estas decisiones son conservadoras y provisionales. No son una ontologia
universal de condiciones de venta ni sustituyen una especificacion historica
CTA/UTP con vigencia efectiva.

Los otros 41 codigos del snapshot permanecen:

```text
KNOWN_BUT_UNREVIEWED_FAIL_CLOSED
```

---

## 6. Hard checks fisicos

Una fila falla cerrada si presenta:

```text
INVALID_TICKER
INVALID_DATE
INVALID_TIMESTAMP
NONPOSITIVE_OR_INVALID_PRICE
NONPOSITIVE_OR_INVALID_SIZE
INVALID_EXCHANGE
UNPARSABLE_CONDITIONS
OUTSIDE_RTH_SCOPE
SOURCE_UNAVAILABLE
```

La ausencia explicita de exchange se conserva como degradacion; no se inventa
un venue.

---

## 7. Duplicados y revisiones

Sin `provider_trade_id` ni `sequence_number` no se eliminan automaticamente
filas economicamente identicas.

```text
exact duplicate
->
EXACT_DUPLICATE_RESEARCH_FLAG
->
fila preservada
```

La revision historica sigue siendo:

```text
RECONCILED_FINAL_ONLY
```

No puede afirmarse elegibilidad revision-aware as-of con el schema legacy.

---

## 8. Resultado ejecutado del piloto

Piloto gobernado:

```text
100 tareas deterministas
83 DOWNLOADED_OK
17 DOWNLOADED_EMPTY
23,855 trades evaluados
```

Resultado:

```text
activity eligible with restrictions = 23,604
activity ineligible                 =    251
unknown fail-closed                 =      0
exact duplicate flags              =     98
price-forming eligible             = 15,157
```

```text
activity eligible fraction
=
98.9478096835%
```

La muestra no es estratificada ni representa el universo completo. Sus 100
tareas pertenecen a `AACT` y `AAGR`.

---

## 9. Autorizacion

```text
POLICY FRAMEWORK
= SPECIFIED_AND_EXECUTED_ON_DETERMINISTIC_PILOT

OBSERVED PILOT CONDITION COVERAGE
= PASS_WITH_RESTRICTIONS

FULL 55-CODE SEMANTIC REVIEW
= NOT_COMPLETE

BINDING A CODE SCAFFOLDING
= AUTHORIZED

BINDING A DETERMINISTIC PILOT EXECUTION
= AUTHORIZED

BINDING A STRATIFIED OR OOS COMPARISON
= NOT_AUTHORIZED

CANONICAL FEATURE PROMOTION
= NOT_AUTHORIZED
```

---

## 10. Revalidacion obligatoria

Esta politica debe versionarse de nuevo cuando ocurra cualquiera de estos
triggers:

```text
Massive full-history enriched backfill audited
new condition code observed
provider condition-name or update-rule drift
historical CTA/UTP effective mapping obtained
premarket or after-hours profile enabled
revision-aware event reconstruction enabled
```
