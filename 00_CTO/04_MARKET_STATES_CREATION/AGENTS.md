# Agent Contract: Market States Creation

Estado: contrato local de entrada y handoff para
`00_CTO/04_MARKET_STATES_CREATION`.

Complementa `C:/TSIS_Data/AGENTS.md` y `00_CTO/LOCAL_RULES.md`. No los
reemplaza ni puede debilitarlos.

La navegacion fisica vigente, las expansiones completas de nombres y el mapa
de rutas anteriores se leen en:

```text
00_CTO/README.md
00_CTO/TREE_v0_2.md
00_CTO/PATH_MAP_v0_1.csv
C:/TSIS_Data/PATH_NAMING_POLICY.md
```

No introducir nuevas siglas de carpetas sin registrarlas. Todo path nuevo debe
ser legible por un humano y pasar los presupuestos de longitud de la policy
raiz.

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
3. `00_START_HERE/CURRENT_STATUS_AND_HANDOFF_v0_28.md`
4. `06_GOVERNANCE/02_MATERIALIZATION/REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md`
5. `06_GOVERNANCE/02_MATERIALIZATION/REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md`
6. `06_GOVERNANCE/01_LIFECYCLE/EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_2.md`
7. `00_START_HERE/TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_17.md`
8. `CHANGELOG.md`
9. `04_EVENTS/WAKE_UP/01_DEFINITION/01_WAKE_UP_EVENT_DEFINITION.md`
10. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/02_MATERIALIZATION/TRADING_ACTIVITY_STAGE8_CPP_FULL_MATERIALIZATION_EXECUTION_AND_CERTIFICATION_READOUT_v0_1.md`
11. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/03_AUDIT/TRADING_ACTIVITY_STAGE8_TARGET_ONLY_IMPLEMENTATION_AND_FOUR_SHARD_PROBE_READOUT_v0_1.md`
12. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/03_AUDIT/TRADING_ACTIVITY_STAGE8_TARGET_ONLY_FULL_EXECUTION_AND_CERTIFICATION_READOUT_v0_1.md`
13. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/04_VERDICT/TRADING_ACTIVITY_BINDING_A_FULL_SCIENTIFIC_EVIDENCE_VERDICT_v0_2.md`
14. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/00_PREREGISTRATION/TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md`
15. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/03_DEVELOPMENT_CERTIFICATION/TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md`
16. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/01_INHERITANCE/TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md`
17. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/01_INHERITANCE/TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md`
18. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/02_EXACT_SPECIFICATION/TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md`
19. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/02_BINDING_COMPARISON/TRADING_ACTIVITY_D07_D12_UPSTREAM_AUTHORITY_WORKSTREAM_READOUT_v0_1.md`
20. `04_EVENTS/WAKE_UP/03_LABELS/WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md`
21. `04_EVENTS/WAKE_UP/03_LABELS/WAKE_UP_LABEL_AND_DENOMINATOR_MATERIALIZATION_CONTRACT_v0_1.md`
22. `04_EVENTS/WAKE_UP/03_LABELS/TRADING_ACTIVITY_FALSE_ACTIVATION_COUNTING_CONTRACT_v0_1.md`
23. `04_EVENTS/WAKE_UP/04_OOS_LOCKBOX/TRADING_ACTIVITY_VALIDATION_AND_FINAL_OOS_SELECTION_AND_SEAL_CONTRACT_v0_1.md`
24. `04_EVENTS/WAKE_UP/04_OOS_LOCKBOX/TRADING_ACTIVITY_LOCKBOX_MANIFEST_SCHEMA_v0_1.json`
25. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/02_EXACT_SPECIFICATION/TRADING_ACTIVITY_BINDING_B_B02_DECISION_RESOLUTION_AND_SCIENTIFIC_REVIEW_v0_1.md`
26. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/02_BINDING_COMPARISON/TRADING_ACTIVITY_BINDING_A_STATISTICAL_INPUT_INVENTORY_FOR_B_COMPARISON_v0_1.md`
27. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_B/02_EXACT_SPECIFICATION/TRADING_ACTIVITY_BINDING_B_B02_COMPUTE_BUDGET_ANNEX_v0_1.md`
28. `04_EVENTS/WAKE_UP/04_OOS_LOCKBOX/TRADING_ACTIVITY_FINAL_TEMPORAL_OOS_LOCKBOX_BLOCKING_EVIDENCE_v0_1.md`
29. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/03_AUDIT/TRADING_ACTIVITY_STAGE8_TARGET_ONLY_RECOVERY_AND_RECERTIFICATION_PLAN_v0_1.md`
30. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/00_SHARED_CONTRACTS/TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`
31. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/00_SHARED_CONTRACTS/TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`
32. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/00_SHARED_CONTRACTS/TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`
33. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/00_SPECIFICATION/TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md`
34. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/01_IMPLEMENTATION/TRADING_ACTIVITY_STAGE8_CPP_ENGINE_INTEGRATION_AND_FOUR_SHARD_RECERTIFICATION_READOUT_v0_1.md`
35. `02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/03_POPULATION_AND_SAMPLE/TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`
36. `05_DAILY_UNIVERSE/02_PIT_RECOVERY/POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md`
37. `02_INFORMATION_OBJECTS/FLOAT_CONTEXT/MODEL_01_PIT_SCALE_ELIGIBILITY/05_SEC_PIT_RESEARCH/FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1.md`
38. `90_HANDOFFS/TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1.md`
39. `05_DAILY_UNIVERSE/00_POLICY/DAILY_ELIGIBLE_UNIVERSE_SELECTOR_AND_BINDING_CONSUMPTION_CONTRACT_v0_1.md`
40. `05_DAILY_UNIVERSE/01_BINDING_AB_BRIDGE/TRADING_ACTIVITY_AB_DENOMINATOR_DAILY_ELIGIBLE_UNIVERSE_RECONCILIATION_READOUT_v0_1.md`

Los snapshots anteriores están inventariados por hash y sustituidos por
autoridades duraderas en
`90_HANDOFFS/TRADING_ACTIVITY_HANDOFF_AND_ROADMAP_LINEAGE_CONSOLIDATION_v0_1.md`.
`v0_12` se conserva solo por compatibilidad con un puntero externo; redirige a
`v0_28` y no es el handoff vigente.

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
current status and handoff          = v0_28
completion roadmap                  = v0_17
daily eligible universe gate        = selector upstream before D07/D12
representation lifecycle            = v0_2
materialization incident protocol   = v0_1
materialization incident register   = v0_1
source observability readout        = v0_5
Binding A exact specification       = v0_2
Binding B preregistration           = v0_1 DRAFT_NOT_FROZEN
Binding B development plan          = v0_1 NOT_EXECUTABLE
Binding B inheritance/delta contract = v0_1 FROZEN_BY_HUMAN
Binding B exact specification        = v0_1 DRAFT_AMENDED_10_OF_12_RESOLVED
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
= CALCULATION_COMPLETE_240_OF_240_CERTIFICATION_PENDING

STAGE-8 C++ REPRESENTATIVE EQUIVALENCE
= PASS_EXACT

STAGE-8 LIMITED STRATIFIED EQUIVALENCE
= PASS_EXACT

STAGE-8 EXPLICIT ENGINE INTEGRATION
= COMPLETE_FINGERPRINTED

STAGE-8 FOUR-SHARD RECERTIFICATION
= PASS_4_OF_4

NEW 240-BLOCK C++ MATERIALIZATION
= PHYSICAL_OUTPUTS_COMPLETE_240_OF_240

FULL-RUN TERMINAL CERTIFICATION
= FAILED_ON_ROW_COUNT_CONTRACT_SHAPE

TARGET-ONLY RECOVERY AND RECERTIFICATION
= FULL_TERMINAL_PASS_2400_TARGET_7200_PARTITIONS

BINDING A SCIENTIFIC EVIDENCE VERDICT
= PASS_WITH_RESTRICTIONS_FOR_CANDIDATE_COMPARISON

MATERIALIZATION INCIDENT CONTROLS RM-MAT-CTRL-001..006
= FULL_RUNTIME_PASS_LATER_PLAN_IMPORT_PENDING

BINDING B PREREGISTRATION
= DRAFT_NOT_FROZEN

BINDING B DEVELOPMENT AND CERTIFICATION PLAN
= PREREGISTERED_NOT_EXECUTABLE

SEC PIT COHORT 01 METADATA
= COMPLETE_824_OF_824

SEC PIT COHORT 01 PRIMARY T01
= RUNNING_EXACT_250_ROWS_REMAINDER_NOT_AUTHORIZED

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
06_GOVERNANCE/01_LIFECYCLE/EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_2.md
```
The physical data-root authority for every Information Object and Representation Model is:

```text
08_REGISTRIES/INFORMATION_OBJECT_DATA_ROOT_AUTHORITY_v0_1.md
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
00_START_HERE/CURRENT_STATUS_AND_HANDOFF_v0_28.md
```

Current TA-3 recovery plan:

```text
02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/BINDING_A/03_AUDIT/TRADING_ACTIVITY_STAGE8_TARGET_ONLY_RECOVERY_AND_RECERTIFICATION_PLAN_v0_1.md
```

The target-only inventory, certifier, focused tests, one production-equivalent
probe per logical shard and the FULL 2,400-TARGET/7,200-partition terminal audit
are complete and pass. The bounded Binding A family-by-family evidence audit is
also complete with `PASS_WITH_RESTRICTIONS`. The Binding B proposal and its
development/certification sequence are documented. B-01 is frozen after
external audit. B-02 incorporates ten audited decisions. D07/D12 upstream
architectures are prepared but not frozen: the scientific owner must fix the
label/counting numbers and selection/custody decisions; Data Foundation and an
independent custodian must then create the exact artifacts. Re-audit consistency
and explicitly freeze B-02 only after their hashes exist. It must import
every applicable incident control. Do not
interpret either PASS as canonical promotion or long-run authorization.

SEC PIT cohort 01 submissions metadata completed `824/824`. The separately
authorized exact T01 tranche of 250 rows is running; the C01 remainder and
cohorts 02-05 remain unauthorized. This parallel lane does not alter the
Trading Activity recovery gate and must not be polled or modified here.

An agent may also prepare, without launching or promoting:

- recovery inventory for the historical population-target panel;
- shares semantics and session-start prior-close audit;
- PIT selector schema, builder design, validators and fixtures;
- float source inventory and source observability audit;
- TA-3 sample-manifest schema and lockbox guards;
- instrument-block runner generalization, tests and bounded smoke.
- target-only reference-manifest, inventory and certifier implementation;
- bounded production-equivalent recovery probe in each of the four shards.

An agent must not:

- select historical sessions with current or last-observed market cap;
- use ungoverned float as a filter;
- inspect validation or final-test feature outputs;
- exceed two concurrent TA-3 workers without a new capacity validation;
- resume `ba2r2` with C++ or mix Python/C++ partitions under one run lineage;
- change or bypass the explicit C++ engine/source/binary fingerprint;
- authorize broad materialization without a separate governed human decision;
- mutate, delete or overwrite the completed Stage-8 source artifacts;
- launch a fresh 240-block materialization while recovery remains viable;
- certify from scope-session totals when the governed denominator is the frozen
  set of 2,400 explicit target sessions;
- infer model admission or canonical promotion.

Foundation quality labels remain evidence metadata and are not automatic
exclusion gates. Audit selected windows under
`TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`.

## 10. Secuencia posterior

Autoridad:

```text
00_START_HERE/TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_17.md
```

Orden:

```text
completed deterministic multisession pilot
-> full-run and legacy source-gate readout
-> completed 240-block Stage-8 physical calculation
-> completed target-only inventory, certifier, tests and 4/4 probes
-> completed FULL checksum recertification of 2,400 TARGET / 7,200 partitions
-> completed independent percentile replay PASS_EXACT over 3,351,960,000 cells
-> completed Binding A evidence verdict PASS_WITH_SCOPE_RESTRICTIONS
-> Binding B B-01 frozen and B-02 amended with D07/D12 still open
-> governed Wake-up label/counting authority and sealed final-lockbox manifest
-> explicit human B-02 freeze
-> Binding B plan imports applicable incident controls
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

Production-equivalent incluye runner, wrapper, agregador, certifier terminal y
escritura del final manifest exactos. Probar solamente el engine no satisface
este gate.

## 15. Aprendizaje de incidentes y herencia entre modelos

Todo fallo de materializacion se registra antes de corregirse en:

```text
06_GOVERNANCE/02_MATERIALIZATION/REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md
```

El tratamiento completo se rige por:

```text
06_GOVERNANCE/02_MATERIALIZATION/REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md
```

Cada plan de materializacion posterior MUST incluir
`inherited_incident_controls`, evaluar todos los controles anteriores
aplicables y aportar referencias de implementacion, tests, probes por shard y
ensayo terminal. `PENDING`, `FAIL` o una omision bloquean el run largo.

Reglas especificas:

- pertenencia exacta de targets, nunca inferida por intervalo;
- metadata separada de conteos fisicos por familia;
- una sola autoridad de cardinalidad para plan, runner y certifier;
- fixtures de targets dispersos, early-close y producto dimensional completo;
- incidente `HIGH/CRITICAL` con readout versionado;
- correccion seguida de reprobe completo de todos los shards;
- ningun modelo siguiente hereda una correccion solo por cita documental: debe
  demostrarla en su propia ruta ejecutable.
