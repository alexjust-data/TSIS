# Agent Contract: Market States Creation

Estado: contrato local de entrada y handoff para
`00_CTO/04_MARKET_STATES_CREATION`.

Complementa `C:/TSIS_Data/AGENTS.md` y `00_CTO/LOCAL_RULES.md`. No los
reemplaza ni puede debilitarlos.

## 1. Rol local

Esta carpeta preserva definiciones cientificas, Information Objects,
Representation Models, contratos experimentales, decisiones, readouts,
roadmaps y handoffs.

No es la autoridad operativa de Data Foundation. No alojar aqui una segunda
source of truth de schemas, policies ejecutables, builders, tests o datasets.

## 2. Lectura obligatoria local

Despues del orden de lectura raiz:

1. `C:/TSIS_Data/00_CTO/LOCAL_RULES.md`
2. `README.md`
3. `CURRENT_STATUS_AND_HANDOFF_v0_10.md`
4. `EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md`
5. `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md`
6. `CHANGELOG.md`
6. `01_WAKE_UP_EVENT_DEFINITION.md`
7. `VARIABLES_FEATURES/TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`
8. `VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`
9. `VARIABLES_FEATURES/TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`
10. `VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md`
11. `VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1.md`
12. `VARIABLES_FEATURES/TRADING_ACTIVITY_BINDING_A_MULTISESSION_RUNNER_IMPLEMENTATION_READOUT_v0_2.md`
13. `VARIABLES_FEATURES/TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`
14. `VARIABLES_FEATURES/POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md`
15. `VARIABLES_FEATURES/FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md`
16. `TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md`

Los handoffs anteriores son historia incorporada por `v0_10`.

Antes de preparar, recomendar, lanzar o reanudar un run multisesion, leer:

```text
C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md
```

## 3. Precedencia documental

La rectificacion:

```text
TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md
```

prevalece solamente sobre las clausulas conflictivas que enumera.

Versiones vigentes:

```text
current status and handoff          = v0_10
source observability readout        = v0_5
Binding A exact specification       = v0_2
trade eligibility policy            = v0_2
RTH coverage sidecar specification  = v0_2
multisession runner readout          = v0_2
```

Las versiones anteriores son evidencia historica, no estado vigente.

`00_TABLES_MARKET_STATE_EVENT_STATE.md` no fue el origen del conflicto de
naming rectificado. No modificarlo basandose en esa atribucion incorrecta.

## 4. Semantica gobernante

```text
Information Object
= Trading Activity

Representation Model Candidate
= ABSOLUTE-AND-PIT-RELATIVE
  MULTISCALE MARKED ACTIVITY PROCESS

Temporal dimension
= TRANSITION DYNAMICS
  AND MINIMAL ANTI-ARTIFACT CORROBORATION
```

Los aliases historicos no gobiernan nuevos artefactos.

## 5. Fronteras no negociables

```text
candidate representation != canonical state
experimental binding != canonical feature
feature value != detector threshold
RTH transition != complete-episode Wake-up
Wake-up != In-Play
Wake-up != Frontside
Wake-up != signal
Wake-up != outcome
Wake-up != edge
```

No introducir en los bindings:

- outcomes futuros;
- scanner labels;
- `wake_up_flag`;
- `in_play_probability`;
- entry, stop, target o sizing;
- execution cost para una orden propia;
- causalidad no observable en la fuente.

## 6. Scope fisico actual

```text
LEGACY RTH RECONCILED EVENT-TIME RESEARCH-ONLY
```

Interpretacion admitida:

```text
first observable transition during RTH
```

Interpretaciones prohibidas:

```text
first Wake-up of the complete episode
revision-aware historical detection
measured historical available_at
premarket or after-hours episode onset
```

La latencia historica es simulada y debe declarar `latency_policy_id`.

## 7. Limite CTO / Data Foundation

`00_CTO` define significado, contrato, secuencia y veredicto.

`01_TSIS_DATA_FOUNDATION` mantiene scripts, tests, policies ejecutables,
snapshots, sidecars, outputs fisicos y readouts de auditoria.

Builders y validators pertenecen por defecto a Data Foundation.

## 8. Estado de autorizacion

```text
TA-1 DETERMINISTIC AACT PILOT
= PASS_WITH_RESTRICTIONS

TA-2 FULL LEGACY SOURCE GATE
= PASS_WITH_RESTRICTIONS

TA-3 SAMPLE DESIGN
= FROZEN_AND_VALIDATED

POPULATION TARGET PIT SELECTOR GATE
= PASS_WITH_RESTRICTIONS_FOR_FROZEN_TA3_SAMPLE

TA-3 SAMPLE MANIFEST
= FROZEN_AND_VALIDATED

TA-3 BROAD EXECUTION
= RUNNING_WITH_CONTROLLED_TWO_WORKER_CONCURRENCY

FLOAT OWNER-EXCLUSION GATE
= PASS_WITH_RESTRICTIONS

FLOAT TRADABILITY GATE
= BLOCKED_BY_INPUT_GATES

OOS COMPARISON
= NOT_AUTHORIZED

CANONICAL IMPLEMENTATION
= NOT_AUTHORIZED

WAKE-UP DETECTOR
= NOT_STARTED

PREDICTIVE CONSUMPTION
= NOT_AUTHORIZED
```

The roadmap documents future stages but does not authorize them.

The representation lifecycle is governed by:

```text
EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md
```
The physical data-root authority for every Information Object and Representation Model is:

```text
INFORMATION_OBJECT_DATA_ROOT_AUTHORITY_v0_1.md
D:/TSIS/IO
```

All experimental bindings, OOS representations and future canonical representation datasets MUST use profile -> Information Object -> Representation Model -> binding/version -> run_id. `G:/TSIS/data` remains upstream source authority and is not an output root for new representation materializations.

Agents must preserve these distinctions:

```text
restricted development materialization
!= full-history canonical dataset

canonical specification and builder
!= complete physical historical coverage

backtest consumption
= read validated versioned representations
  rather than rebuild raw-event windows on every request
```

## 9. Trabajo permitido ahora

Current handoff:

```text
CURRENT_STATUS_AND_HANDOFF_v0_10.md
```

Current TA-3 plan:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md
```

An agent may work in parallel on:

- recovery inventory for the historical population-target panel;
- shares semantics and session-start prior-close audit;
- PIT selector schema, builder design, validators and fixtures;
- SEC PIT O/S/ownership evidence reconciliation;
- G8 lockup, legend and resale-condition extraction;
- float source inventory and source observability audit;
- TA-3 sample-manifest schema and lockbox guards;
- instrument-block runner generalization, tests and bounded smoke.

An agent must not:

- select historical sessions with current or last-observed market cap;
- use ungoverned float as a filter;
- inspect validation or final-test feature outputs;
- exceed two concurrent TA-3 workers without a new capacity validation;
- infer model admission or canonical promotion.

Foundation quality labels remain evidence metadata and are not automatic
exclusion gates. Audit selected windows under
`TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`.

## 10. Secuencia posterior

Autoridad:

```text
TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3.md
```

Orden:

```text
completed deterministic multisession pilot
-> full-run and legacy source-gate readout
-> stratified development evidence
-> Binding B and justified C
-> A/B/C comparison at fixed false-alarm budget
-> temporal OOS
-> Trading Activity admission
-> canonical physical binding and table lineage
-> remaining Wake-up Information Objects
-> integrated representation
-> detector calibration and OOS
-> Event and Episode lifecycle
-> operational promotion decision
```

Completar Trading Activity no completa Wake-up.

## 11. Massive dependency

El backfill Massive completo no bloquea el piloto RTH restringido. Cuando haya
sido auditado obliga a:

```text
REQUIRES_REVALIDATION
REBUILD_NEW_DATASET_VERSION
FEATURE_VERSION_REVIEW
```

No sobrescribir el dataset legacy ni sustituir silenciosamente sus outputs.

## 12. Checklist de arranque

1. comprobar rama y no trabajar en `main`;
2. revisar `git status` sin revertir cambios ajenos;
3. confirmar versiones vigentes;
4. declarar scope RTH o Massive enriched;
5. identificar ownership CTO o Data Foundation;
6. verificar gates y autorizaciones;
7. preparar lineage y tests antes de ampliar scope;
8. no iniciar operaciones largas sin handoff al humano.

## 13. Cierre de hitos

Actualizar cuando aplique:

- readout versionado;
- handoff vigente;
- roadmap si cambia la secuencia;
- `CHANGELOG.md` local;
- `README.md`;
- `00_CTO/CHANGELOG.md`;
- `00_CTO/GRAPHIFY_REFRESH_QUEUE.md` o leaf oficial.

No reescribir silenciosamente artefactos historicos. Cualquier recodificacion
de documentos con encoding antiguo debe ser un cambio separado y sin cambio
semantico.
## 14. Gate previo para variables y shards

Antes de materializar una variable candidata de cualquier Information Object a
escala experimental amplia, ejecutar y certificar un probe acotado por cada
shard con la configuracion exacta que se pretende ampliar.

El gate debe comparar specification, codigo, config y output real columna por
columna; validar formulas, schema estable, missingness, causalidad, metadata,
grain y equivalencia entre shards; y producir un readout versionado.

```text
SHARD_EXPANSION_AUTHORIZED
= all shard probes PASS
  and variable-level audit PASS
```

Un fallo obliga a detener la expansion, crear nueva version y repetir todos los
probes. Esta comprobacion precede a cualquier run de larga duracion y se repite
despues de cualquier cambio de formula, schema, policy o lineage.
