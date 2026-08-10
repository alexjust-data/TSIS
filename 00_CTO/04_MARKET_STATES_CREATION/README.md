# Market States Creation

Este directorio conserva la arquitectura conceptual, los contratos candidatos,
las decisiones, la evidencia resumida y los handoffs del trabajo de creacion de
`Market State` y `Event State`.

Workstream activo:

```text
Wake-up
-> Trading Activity Information Object
-> Experimental Physical Binding A
-> governed multisession RTH pilot
```

`00_CTO` organiza significado, contratos y decisiones. La implementacion,
tests y outputs fisicos viven en `01_TSIS_DATA_FOUNDATION`.

## Estado actual

Snapshot operativo: `2026-08-10`.

```text
WAKE-UP SEMANTIC DEFINITION
= CANDIDATE

TRADING ACTIVITY REPRESENTATION MODEL
= CANDIDATE GOVERNED BY AMENDMENT

FULL LEGACY RTH SOURCE GATE
= PASS_WITH_RESTRICTIONS

BINDING A EXACT SPECIFICATION
= FROZEN_FOR_DETERMINISTIC_PILOT

CURRENT-STATE AND PIT BASELINE KERNELS
= IMPLEMENTED_AND_TESTED

MULTISESSION PILOT RUN PLAN
= COMPLETE

MULTISESSION RUNNER, CONFIG AND MONITOR
= IMPLEMENTED_AND_TESTED

REGRESSION AFTER POSTLAUNCH FIX
= PASS, 46 TESTS

AACT NORMAL + EARLY-CLOSE PHYSICAL SMOKE
= PASS

FULL 130-SESSION PILOT
= COMPLETE

INDEPENDENT POST-RUN VALIDATION
= PASS

STRATIFIED DEVELOPMENT SAMPLE DESIGN
= FROZEN_AND_VALIDATED

POPULATION TARGET PIT SELECTOR GATE
= PASS_WITH_RESTRICTIONS_FOR_FROZEN_TA3_SAMPLE

STRATIFIED DEVELOPMENT EXECUTION
= RUNNING_WITH_CONTROLLED_TWO_WORKER_CONCURRENCY

SEC PIT BNAI G7 OWNER-EXCLUSION
= PASS_WITH_RESTRICTIONS

SEC PIT BNAI G8 TRADABILITY
= BLOCKED_BY_INPUT_GATES

OOS COMPARISON
= NOT_AUTHORIZED

TABLE MAPPING
= NOT_STARTED

WAKE-UP DETECTOR
= NOT_STARTED

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

La fuente legacy permite estudiar:

```text
first observable transition during RTH
```

No permite afirmar:

```text
first Wake-up of the complete episode
```

## Entrada para agentes

Despues del orden de lectura raiz de `C:/TSIS_Data/AGENTS.md`, leer:

1. [`AGENTS.md`](AGENTS.md)
2. [`CURRENT_STATUS_AND_HANDOFF_v0_10.md`](CURRENT_STATUS_AND_HANDOFF_v0_10.md)
3. [`EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md`](EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md)
4. [`TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md`](TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md)
5. [`CHANGELOG.md`](CHANGELOG.md)
5. [`01_WAKE_UP_EVENT_DEFINITION.md`](01_WAKE_UP_EVENT_DEFINITION.md)
6. [`TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md)
7. [`TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md)
8. [`TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md)
9. [`TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md)
10. [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md)
11. [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md)
12. [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md)
13. [`TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md)
14. [`POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md`](VARIABLES_FEATURES/POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md)
15. [`FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md`](VARIABLES_FEATURES/FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md)
16. [`TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md`](TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md)

Los handoffs anteriores se conservan como historia incorporada por
`CURRENT_STATUS_AND_HANDOFF_v0_10.md`.

No preparar ni lanzar una materializacion multisesion sin leer
`C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md`.

## Mapa documental

### Proceso y semantica

| Artefacto | Funcion | Estado |
|---|---|---|
| [`00_WAKE_UP_END_to_END.md`](00_WAKE_UP_END_to_END.md) | Mapa humano end-to-end. | Trabajo subordinado a rectificaciones posteriores. |
| [`01_WAKE_UP_EVENT_DEFINITION.md`](01_WAKE_UP_EVENT_DEFINITION.md) | Definicion cientifica candidata. | No Event Type operacional. |
| [`REPRESENTATION_MODELS.md`](REPRESENTATION_MODELS.md) | Espacio de modelos y metodo de admision. | Research. |
| [`VARIABLES_FEATURES.md`](VARIABLES_FEATURES.md) | Indice de implementacion fisica. | Punto de navegacion. |

### Estado y continuidad

| Artefacto | Funcion | Estado |
|---|---|---|
| [`CURRENT_STATUS_AND_HANDOFF_v0_10.md`](CURRENT_STATUS_AND_HANDOFF_v0_10.md) | Handoff vigente, incidente de runtime, recuperacion y siguiente gate. | `CURRENT_HANDOFF` |
| [`EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md`](EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md) | Separa bindings experimentales, admision canonica, materializacion historica y consumo por backtest. | `ACTIVE_LIFECYCLE_CONTRACT` |
| [`TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md`](TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md) | Secuencia para cerrar Trading Activity y Wake-up. | `CURRENT_PLANNING_SEQUENCE` |
| [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md) | Scope, outputs, telemetria y reglas del run ejecutado. | `EXECUTED` |
| [`TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md) | Prerregistro de poblacion, estratos, lockboxes y denominador TA-3. | `CURRENT_TA_3_PLAN` |
| [`POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md`](VARIABLES_FEATURES/POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md) | Dependencia PIT para market cap y precio al inicio de sesion. | `ACTIVE_DEPENDENCY_PLAN` |
| [`FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md`](VARIABLES_FEATURES/FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md) | Auditoria paralela de fuentes de float. | `ACTIVE_PARALLEL_PLAN` |
| [`DAILY_PIT_FUNDAMENTAL_CONTEXT_OUTPUTS_REFERENCE_v0_1.md`](_DESCAGRA_DATOS_NECESARIA_/DAILY_PIT_FUNDAMENTAL_CONTEXT_OUTPUTS_REFERENCE_v0_1.md) | Referencia diaria de outputs PIT, formulas, fuentes y limites para O/S, float, ownership, market cap, EV y net cash/share. | `ACTIVE_REFERENCE` |
| [`SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`](_DESCAGRA_DATOS_NECESARIA_/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md) | Contrato de adquisicion SEC por niveles, disponibilidad EDGAR, resolvers PIT, storage, gates y autorizacion de escala. | `DRAFT_FOR_ONE_TICKER_EXECUTION` |
| [`SEC_PIT_IMPLEMENTATION_READOUT_v0_1.md`](_DESCAGRA_DATOS_NECESARIA_/SEC_PIT_IMPLEMENTATION_READOUT_v0_1.md) | Readout ejecutado BNAI para O/S, ownership, G7 float estimado y G8 restriction/tradability. | `G7_PASS_WITH_RESTRICTIONS_G8_BLOCKED` |
| [`TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md`](TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md) | Carriles, ownership y gates de sincronizacion. | `CURRENT_COORDINATION` |
| [`CHANGELOG.md`](CHANGELOG.md) | Memoria de hitos locales. | Activo |

### Contratos vigentes de Trading Activity

| Artefacto | Version |
|---|---|
| [`TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md) | `v0_1` |
| [`TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md) | `v0_2` |
| [`TRADING_ACTIVITY_RTH_INTERIM_RESEARCH_SCOPE_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_RTH_INTERIM_RESEARCH_SCOPE_v0_1.md) | `v0_1` |
| [`TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md) | `v0_1`, rectificado donde aplique |
| [`TRADING_ACTIVITY_RTH_COVERAGE_SIDECAR_SPECIFICATION_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_RTH_COVERAGE_SIDECAR_SPECIFICATION_v0_2.md) | `v0_2` |
| [`TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md) | `v0_1` |
| [`TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md) | `v0_2` |
| [`TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md) | `v0_1` |
| [`TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md) | `v0_1`, rectificado donde aplique |
| [`TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md) | `v0_2` |

### Readouts ejecutados

| Artefacto | Evidencia |
|---|---|
| [`TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md) | Full legacy source gate restringido. |
| [`TRADING_ACTIVITY_BINDING_A_IMPLEMENTATION_READOUT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_IMPLEMENTATION_READOUT_v0_1.md) | Kernel y smoke de una particion. |
| [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md) | Runner, arreglo long-path, 46 tests y cierre post-run. |
| [`TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md`](VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md) | Evidencia del run completo e independiente. |
| [TRADING_ACTIVITY_TA3_BINDING_A_SPEC_IMPLEMENTATION_CONFORMANCE_READOUT_v0_1.md](VARIABLES_FEATURES/TRADING_ACTIVITY_TA3_BINDING_A_SPEC_IMPLEMENTATION_CONFORMANCE_READOUT_v0_1.md) | Auditoria provisional columna por columna sobre bloques TA-3 finalizados; detecta duration compression ausente, lineage v0.1 y schema baseline inestable. |

## Dependencia futura Massive

[`_MASSIVE_TRADES_FULL_BACKFILL_REQUIREMENTS.md`](_MASSIVE_TRADES_FULL_BACKFILL_REQUIREMENTS.md)
define el backfill futuro de historia accesible completa, todas las sesiones y
payload completo.

```text
not a blocker for the restricted legacy RTH pilot
mandatory revalidation trigger
new dataset version required
legacy RTH dataset must not be overwritten
```

## Reconciliacion lifecycle Massive / SEC

| Artefacto | Papel |
|---|---|
| [`MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_CONTRACT_v0_1.md`](_DESCAGRA_DATOS_NECESARIA_/MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_CONTRACT_v0_1.md) | Preserva la procedencia Massive/Polygon de las ventanas existentes y gobierna su comparacion por identidad y clase contra SEC. |
| [`SEC_PIT_TARGET_INTERVAL_FILING_REVIEW_READOUT_v0_1.md`](_DESCAGRA_DATOS_NECESARIA_/SEC_PIT_TARGET_INTERVAL_FILING_REVIEW_READOUT_v0_1.md) | Revision ejecutada de los 12 filings dentro/despues del intervalo objetivo. |
| [`MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_READOUT_v0_1.md`](_DESCAGRA_DATOS_NECESARIA_/MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_READOUT_v0_1.md) | Comparacion ejecutada para seis identidades entre ventanas vendor, SEC y presencia de mercado. |
## Siguiente hito

Completar los shards activos 0 y 1, reanudar 2 y 3 bajo el limite de dos
workers, reconciliar los 240 manifests y emitir el readout source-gate TA-3.

La materializacion TA-3 esta en ejecucion. Binding B, OOS y promocion canonica
permanecen no autorizados.

## Mantenimiento

Cuando cambie el estado:

1. crear una nueva version del readout o handoff;
2. actualizar este README como indice;
3. actualizar [`CHANGELOG.md`](CHANGELOG.md);
4. actualizar `00_CTO/CHANGELOG.md` si cambia semantica o estructura;
5. actualizar o encolar el slice en `00_CTO/GRAPHIFY_REFRESH_QUEUE.md`.

Las entradas padre pendientes viven en
[`PENDING_PARENT_REGISTRY_UPDATES_v0_4.md`](PENDING_PARENT_REGISTRY_UPDATES_v0_4.md).

Nunca promover un artefacto a `canonical`, `predictive` o `institutional`
modificando solamente este README o el roadmap.
## Handoff externo de 2026-08-07

El paquete autocontenido para revision independiente vive en:

```text
handoffs/
EXTERNAL_REVIEW_TRADING_ACTIVITY_PIT_20260807_v0_1.zip
```

El paquete se conserva como snapshot historico inmutable junto con:

```text
handoffs/
EXTERNAL_REVIEW_TRADING_ACTIVITY_PIT_20260807_v0_1.zip.sha256
```

SHA-256 verificado el 2026-08-07:

```text
7a2f839e2bc8d7460190ab89b43e078eee07b851838f4f1c080137d7554fff15
```

El ZIP conserva su manifest interno con rutas, tamanos y hashes. No es una
autoridad operativa vigente, no concede promocion canonica y no autoriza el
selector PIT en disputa. La carpeta expandida y el ZIP preliminar se eliminaron
despues de consolidar sus decisiones en las autoridades activas.

