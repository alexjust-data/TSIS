# TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2

> Contrato ejecutable de auditoría de observabilidad física para el Objeto de
> Información `Trading Activity` dentro del perfil candidato `Wake-up`.

---

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_audit_contract` |
| `document_version` | `v0_2` |
| `document_role` | `SOURCE_OBSERVABILITY_AUDIT_CONTRACT` |
| `document_status` | `DRAFT_EXECUTABLE` |
| `review_verdict` | `PASS_WITH_REQUIRED_REVISIONS_APPLIED` |
| `workflow_status` | `SOURCE_AUDIT_IN_PROGRESS` |
| `source_audit_status` | `IN_PROGRESS` |
| `freeze_status` | `NOT_READY_FOR_FREEZE` |
| `supersedes` | `TRADING_ACTIVITY_AUDIT_CONTRACT_v0_1.md` |
| `base_requirements_adopted` | `TA-SO-001 ... TA-SO-028 from v0_1` |
| `base_tests_adopted` | `TA-ST-001 ... TA-ST-015 from v0_1` |
| `current_legacy_source_status` | `UNDER_AUDIT` |
| `target_enriched_source_status` | `DEFERRED_PENDING_MASSIVE_BACKFILL` |
| `expected_readout` | `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1.md` |
| `information_object_id` | `trading_activity` |
| `representation_profile_id` | `wake_up_information_object_profile_candidate_v0_1` |
| `representation_model_candidate_id` | `absolute_and_pit_relative_multiscale_marked_activity_process` |
| `output_table_mapping_status` | `NOT_STARTED` |
| `canonical_feature_promotion_status` | `NOT_AUTHORIZED` |
| `downstream_consumption_status` | `NOT_AUTHORIZED` |
| `updated_at` | `2026-08-06` |
| `owner` | `TBD` |

```text
CURRENT CONTRACT VERDICT
========================

CONTRACT DESIGN
= PASS_WITH_REQUIRED_REVISIONS_APPLIED

CURRENT LEGACY SOURCE AUDIT
= IN_PROGRESS

TARGET ENRICHED SOURCE AUDIT
= DEFERRED_PENDING_MASSIVE_BACKFILL

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

---

## 1. Razón de la revisión

La `v0_1` definió correctamente la matriz de observabilidad, los bindings y los
casos de prueba, pero trataba la ausencia de ciertos campos físicos como un
posible bloqueo único de toda la auditoría.

La `v0_2` separa:

```text
1. lo que puede auditarse y ejecutarse ahora
   contra la fuente legacy disponible;

2. lo que requiere el backfill histórico enriquecido de Massive;

3. lo que nunca será un hecho histórico observado
   y solo puede representarse mediante simulación reproducible;

4. lo que deberá capturarse prospectivamente en live/shadow.
```

La ausencia de datos pendientes no invalida el Information Object ni el
Representation Model. Restringe la fuerza de las afirmaciones autorizadas.

---

## 2. Normativa heredada de v0_1

La `v0_2` incorpora sin cambios semánticos las siguientes partes de la `v0_1`:

```text
Information Object
Representation Model Candidate
Experimental Physical Bindings A / B / C1 / C2
Source Observability Matrix TA-SO-001 ... TA-SO-028
Trade Eligibility Matrix
Coverage and Observation States
Zero-Mass Baseline Requirements
Cardinality and Boundary Censoring
Mandatory Tests TA-ST-001 ... TA-ST-015
Evidence Package
Output Table and Canonical Promotion Prohibitions
```

En caso de conflicto, las reglas temporales, los estados de veredicto y la
ejecución por fases definidos en esta `v0_2` tienen precedencia.

---

## 3. Ejecución por fases

### 3.1 Fase actual: Legacy Source Audit

Se ejecutan ahora todos los requisitos y tests soportados por la fuente actual.

```text
CURRENT_LEGACY_SOURCE
=
existing reduced-schema historical trades
```

Cada requisito recibirá uno de los veredictos definidos en el apartado 5. Los
huecos de fuente se registrarán individualmente y no detendrán pruebas
independientes.

### 3.2 Fase futura: Enriched Source Audit

```text
TARGET_ENRICHED_SOURCE
=
full-universe
× full-history
× premarket + RTH + after-hours
× complete Massive trade payload
```

Su adquisición está gobernada por:

```text
../_MASSIVE_TRADES_FULL_BACKFILL_REQUIREMENTS.md
```

Hasta completar ese backfill:

```text
TARGET_ENRICHED_SOURCE_GATE
= DEFERRED_PENDING_MASSIVE_BACKFILL
```

### 3.3 Fase prospectiva: Live/Shadow Temporal Capture

Los timestamps reales de recepción y disponibilidad TSIS solo pueden capturarse
prospectivamente:

```text
observed_at_utc
available_at_utc
```

Su ausencia histórica no se falsifica ni se rellena con el momento de descarga
REST.

---

## 4. Política temporal rectificada

### 4.1 Tiempos de mercado y conocimiento

| Símbolo | Significado |
|---|---|
| `event_time_i` | Tiempo económico seleccionado por política versionada. |
| `participant_timestamp_i` | Generación del trade en participante/exchange, cuando exista. |
| `sip_timestamp_i` | Recepción del trade por el SIP, cuando exista. |
| `observed_at_i` | Recepción física por TSIS; solo observable prospectivamente. |
| `available_at_i` | Primer consumo TSIS autorizado; solo observable prospectivamente. |
| `simulated_available_at_i` | Disponibilidad histórica simulada mediante política versionada. |
| `t_d` | `decision_timestamp` representado. |
| `t_a` | Cutoff de conocimiento utilizado por el estado. |

### 4.2 Replay histórico experimental

Cuando no exista `available_at_i` histórico observado, podrá utilizarse:

```text
source_causal_anchor_i
= sip_timestamp_i

simulated_available_at_i
= source_causal_anchor_i
   + latency_policy_versioned
```

Si la fuente legacy solo conserva un timestamp derivado, deberá declararse su
lineage y la simulación quedará restringida a esa semántica física.

La vista experimental será:

```text
T_W_SIM(t_d, t_a)
=
{
  i:
  eligible_i_under_reconciled_policy
  AND t_d - W < event_time_i <= t_d
  AND simulated_available_at_i <= t_a
}
```

Debe cumplirse:

```text
availability_mode = SIMULATED_NOT_OBSERVED
latency_policy_id IS NOT NULL
future_window_used = false
outcome_dependency = false
```

### 4.3 Límite de la simulación

La simulación puede autorizar investigación histórica y comparación OOS bajo un
contrato explícito. No demuestra la latencia histórica real de Massive ni de
TSIS y no autoriza por sí sola promoción decision-safe o live.

---

## 5. Vocabulario de veredictos

| Veredicto | Significado |
|---|---|
| `OBSERVABLE` | La fuente actual aporta evidencia suficiente y reproducible. |
| `OBSERVABLE_WITH_RESTRICTIONS` | Observable bajo restricciones explícitas de sesión, periodo, resolución o política. |
| `REPRODUCIBLE_SIMULATION_ONLY` | El hecho histórico no fue observado, pero existe una simulación causal versionable; nunca equivale a observado. |
| `DEFERRED_PENDING_MASSIVE_BACKFILL` | Massive documenta o puede aportar el dato, pero el dataset legacy no lo preserva y queda pendiente de backfill. |
| `DEFERRED_PENDING_LIVE_CAPTURE` | Solo una ingesta prospectiva puede observar el dato. |
| `REQUIRES_EVIDENCE` | Aún faltan documentación, muestra o test para emitir veredicto. |
| `REQUIRES_PROVIDER_CONFIRMATION` | La documentación pública no resuelve la semántica necesaria. |
| `NOT_OBSERVABLE` | La fuente evaluada no contiene el hecho y no existe reconstrucción admisible. |
| `NOT_APPLICABLE` | El requisito no aplica al binding o fuente evaluados. |

Regla:

```text
DEFERRED
!= OBSERVABLE
!= FAIL OF THE REPRESENTATION MODEL
```

---

## 6. Regla de ejecución de TA-SO y TA-ST

Cada requisito `TA-SO-001 ... TA-SO-028` y cada test
`TA-ST-001 ... TA-ST-015` debe ejecutarse o clasificarse individualmente.

No se permite:

```text
1. detener toda la auditoría al encontrar el primer campo ausente;
2. convertir un pendiente de backfill en OBSERVABLE;
3. convertir una simulación en timestamp observado;
4. declarar PASS de la fuente enriquecida antes de descargarla;
5. usar el estado final reconciliado como conocimiento histórico silencioso.
```

La ejecución se registra en:

```text
TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1.md
```

---

## 7. Hard gates separados

### 7.1 Current Legacy Source Gate

Puede emitir:

```text
PASS
PASS_WITH_RESTRICTIONS
FAIL
IN_PROGRESS
```

Un `PASS_WITH_RESTRICTIONS` puede autorizar exclusivamente un perfil como:

```text
RECONCILED_RTH_EVENT_TIME_RESEARCH_ONLY
```

si los tests correspondientes lo sostienen.

### 7.2 Target Enriched Source Gate

Mientras no exista el backfill:

```text
TARGET_ENRICHED_SOURCE_GATE
= DEFERRED_PENDING_MASSIVE_BACKFILL
```

No puede inferirse su PASS a partir de la documentación del proveedor.

### 7.3 Decision-Safe Promotion Gate

Permanece cerrado cuando:

```text
observed historical availability is absent
OR revision semantics are unresolved
OR full required session coverage is absent
OR source lineage is insufficient
```

Una política `simulated_available_at` puede permitir investigación, pero no
abre automáticamente este gate.

---

## 8. Resultado y cierre

El contrato puede cerrar la fase legacy cuando el Readout contenga:

```text
1. source identity and schema evidence;
2. TA-SO-001 ... TA-SO-028 verdicts;
3. TA-ST-001 ... TA-ST-015 outcomes;
4. binding A / B / C1 / C2 current-source verdicts;
5. restrictions register;
6. deferred Massive backfill register;
7. deferred live/shadow capture register;
8. next authorized step.
```

Cerrar la fase legacy no cierra la fase enriquecida.

---

## 9. Siguiente trabajo autorizable

Si el Readout sostiene al menos un perfil experimental restringido, podrá
autorizarse después:

```text
TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md
↓
TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md
↓
TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md
```

No se autoriza todavía:

```text
canonical implementation
output table creation
Market State or Event State consumption
predictive backtest claims
live production
strategy or execution
```

---

## 10. Estado final de esta versión

```text
DOCUMENT_STATUS                = DRAFT_EXECUTABLE
WORKFLOW_STATUS                = SOURCE_AUDIT_IN_PROGRESS
SOURCE_AUDIT_STATUS            = IN_PROGRESS
CURRENT_LEGACY_SOURCE_GATE     = IN_PROGRESS
TARGET_ENRICHED_SOURCE_GATE    = DEFERRED_PENDING_MASSIVE_BACKFILL
LIVE_TEMPORAL_CAPTURE          = DEFERRED_PENDING_LIVE_CAPTURE
BINDING_A_EXACT_SPECIFICATION  = NOT_AUTHORIZED_YET
OUTPUT_TABLE_MAPPING           = NOT_STARTED
CANONICAL_PROMOTION            = NOT_AUTHORIZED
FREEZE_STATUS                  = NOT_READY_FOR_FREEZE
```

---

## 11. Change Log

| Versión | Fecha | Cambio |
|---|---|---|
| `v0_2` | `2026-08-06` | Ejecución por fases; separación legacy/backfill/live; `simulated_available_at`; estados deferred; inicio formal del Readout. |
