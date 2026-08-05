## Current Authoritative State - BT-GATE-015 closed with restrictions

```text
BT-GATE-014 = CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-014_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
BT-GATE-014_V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_BT_GATE_014_V0.5 = PROHIBITED

BT-GATE-015 = CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-015_CONTRACT = OWNER_REVIEW_PASS
BT-GATE-015_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW = PASS
BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW = PASS
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

BT-GATE-015_V0.3 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_BT_GATE_015_V0.3 = PROHIBITED
POSTEXECUTION_FAILURE_EVIDENCE_V0.3 = ACCEPTED
ROOT_CAUSE = CONFIRMED_CONSUMER_DATASET_FINGERPRINT_DOMAIN_BINDING_ERROR

BT-GATE-015_V0.4 = CONSUMED_FINAL
SECOND_EXECUTION_BT_GATE_015_V0.4 = PROHIBITED
BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW = PASS
PHYSICAL_COMMAND_V0.4 = EXECUTED_ONCE_PASS
EVENT_STATE_PHYSICAL_READ_V0.4 = EXECUTED_PASS
PHYSICAL_DATA_FILES_OPENED_V0.4 = 1
PHYSICAL_STATE_RECORDS_SCANNED_V0.4 = 8
PHYSICAL_STATE_ROWS_SELECTED_V0.4 = 1
EVENTS / STORE_INSERTS / OBSERVATIONS_V0.4 = 1 / 1 / 1
DELIVERY_BEFORE_AVAILABLE_AT_V0.4 = 0
DETERMINISTIC_OUTPUT_HASH_V0.4 = 35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a
POSTEXECUTION_PACKAGE_SHA256 = 62f1503694c9a3d9153179289b37bc4809d660315a0779cb8a30a52f367e0870
BT-GATE-015_CLOSED_PASS = CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS

BT-GATE-016 = NOT_OPEN
BT-GATE-016_IMPLEMENTATION = NOT_AUTHORIZED
```
## 2026-08-05 | Root launcher cleanup after BT-GATE-015 closure

Removed five unreferenced, superseded root artifacts: the two obsolete
BT-GATE-015 reproduction notes and the BT-GATE-014 V0.3/V0.4/V0.5
pre-execution test wrappers. Accepted ZIP evidence and governed run artifacts
remain unchanged. Canonical regression, non-physical reproduction and
BT-GATE-015 audit launchers remain available; consumed physical authorizations
remain non-reusable.

Mandatory restart handoff:
`docs/00_system/CURRENT_PROJECT_HANDOFF.md`

All subsequent status blocks are historical snapshots and are superseded by
this block.
## Historical Snapshot - Superseded - Current Authoritative State - BT-GATE-014 V0.5

```text
BT-GATE-014 = OPEN_PENDING_V0_5_EXTERNAL_PREEXECUTION_REVIEW
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3/V0.4 = PROHIBITED
RESTRICTION_DOMAIN_BINDING = ADOPTED
V0.5 = AUTHORIZED_NOT_CONSUMED
PHYSICAL_COMMAND_V0.5 = NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
PHYSICAL_READ_V0.5 = NOT_EXECUTED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
Event State = NOT_OPEN
```

The provider/shared-boundary clarification separates physical provenance,
bounded replay-consumption and component replay restriction domains. V0.5 may
be executed once only after an independent pre-execution PASS.

## Historical Snapshot - Superseded - Current Authoritative State - V0.4 Physical Result

```text
BT-GATE-014 = OPEN_CONTRACT_CORRECTION_REQUIRED
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
PHYSICAL_READ_V0.4 = EXECUTED_FAILED / 1 FILE / 2 ROWS / 0 EVENTS
SECOND_EXECUTION_V0.4 = PROHIBITED
NEW_SINGLE_USE_AUTHORIZATION = NOT_AUTHORIZED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

Physical rows carry design/provenance restrictions while the sidecar and components carry bounded-consumption restrictions. The current contract incorrectly requires these distinct domains to be identical. Older current-state blocks below are HISTORICAL / SUPERSEDED.

## Historical Snapshot - Superseded - Current Authoritative State - 2026-07-30

```text
BT-GATE-014 = OPEN_CORRECTION_REQUIRED
V0.3 = CONSUMED_FAILED_FINAL
PHYSICAL_READ_V0.3 = EXECUTED_FAILED / 1 FILE / 2 ROWS / 0 EVENTS
SECOND_EXECUTION_V0.3 = PROHIBITED
V0.4 = AUTHORIZED_NOT_CONSUMED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
PHYSICAL_COMMAND_V0.4 = NOT_APPROVED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

All older current-state blocks below are HISTORICAL / SUPERSEDED.

## Historical Snapshot - Superseded - Current Gate - BT-GATE-014

```text
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
BT-GATE-014 = SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3_ISSUED_NOT_CONSUMED
BT-GATE-014_CONSUMER_CONTRACT = IMPLEMENTED
PHASE_B_NON_PHYSICAL_IMPLEMENTATION = ACCEPTED
BT-GATE-014_PHASE_B_EXTERNAL_RE_REVIEW = PASS
SYNTHETIC_CONSUMER_TESTS = PASS
PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
PHYSICAL_CONSUMER_EVIDENCE = NOT_YET_PRODUCED
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_1 = SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_2 = SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3 = AUTHORIZED_NOT_CONSUMED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
Event State = NOT_OPEN
```

# AGENTS - TSIS Backtest Engine

Status: LIVE_HANDOFF
Last updated: 2026-07-29
Scope: agent handoff for the executable implementation root.

This file is the first read for any agent entering `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE`.

## Política de velocidad de desarrollo y granularidad de gates

### Prioridad vigente

La prioridad del proyecto es construir un backtester de small caps serio,
riguroso, reproducible y científicamente defendible.

La governance debe proteger esa finalidad, pero no debe sustituir el desarrollo
ni fragmentarlo en microaprobaciones.

### Regla fundamental

```text
Un gate = una capacidad científicamente utilizable
```

No debe abrirse un gate independiente para:

```text
un documento
una autorización intermedia
una corrección de imports
una corrección de packaging
una actualización de manifests
una sincronización rutinaria de governance
una corrección menor de tests o evidencia
```

Estas correcciones deben resolverse dentro del gate de capacidad que permanezca
abierto, salvo que impliquen:

```text
cambio de semántica
ampliación material de alcance
nueva fuente de datos
nueva capacidad de ejecución
riesgo de look-ahead
cambio del modelo contable
cambio de una frontera arquitectónica congelada
```

### Ciclo operativo obligatorio

Cada gate de capacidad debe seguir este ciclo:

```text
1. Definir antes de implementar:
   - alcance
   - contrato
   - prohibiciones
   - criterios de aceptación
   - evidencias requeridas

2. Autorizar una sola vez el gate completo.

3. Ejecutar sin pausas intermedias:
   - implementación
   - correcciones
   - tests
   - run
   - documentación
   - manifests
   - empaquetado

4. Realizar una única revisión externa al final.

5. Si la revisión encuentra defectos menores de implementación,
   tests, imports, evidencia o packaging:
   - mantener abierto el mismo gate;
   - corregirlos dentro del gate;
   - no crear un nuevo gate ni solicitar una nueva autorización arquitectónica.

6. Reabrir la decisión solamente si la corrección cambia materialmente:
   - alcance
   - semántica
   - contrato
   - datos consumidos
   - modelo de ejecución
   - contabilidad
   - fronteras autorizadas
```

### Prohibición de microgates

No debe utilizarse esta secuencia como flujo normal:

```text
documento
→ auditoría
→ autorización
→ cambio pequeño
→ paquete
→ auditoría
→ corrección menor
→ nueva auditoría
```

El flujo normal debe ser:

```text
contrato y aceptación completos
→ autorización del incremento completo
→ implementación continua
→ tests y run
→ paquete final
→ revisión externa final
```

### Plan de capacidades vigente

Después del cierre de `BT-GATE-010`, el desarrollo debe organizarse
preferentemente en estos macrogates:

```text
BT-GATE-011
SINGLE_STRATEGY_END_TO_END_BACKTEST

Incluye:
- StrategySpec reproducible
- integración EventLoop → Execution → Accounting
- Deterministic Fill Simulator
- Trade Ledger
- métricas mínimas
- Unified Run Manifest
- primer run histórico end-to-end
```

```text
BT-GATE-012
MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE

Incluye:
- múltiples símbolos
- múltiples sesiones
- orden temporal global determinista
- cash y posiciones compartidos
- concurrencia de órdenes
- cierre de sesión
- portfolio equity curve
```

```text
BT-GATE-013
PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1

Incluye:
- puente desde filas fisicas 013 a ReplayBarEvent / ReplayGapEvent
- binding fisico exacto de schema y timestamp
- disponibilidad legal available_at = bar_end
- linaje fila a evento
- hashes de inputs fisicos
- gaps como UNKNOWN_SOURCE_GAP sin forward-fill
- replay multi-symbol/multi-session con motor aceptado BT-GATE-012
- reconciliacion contable y determinismo

No incluye:
- halts
- SSR
- borrow/locates
- liquidez/capacidad
- batch research
- DSR/PBO/CSCV
- edge evidence
```

Esta agrupación es la orientación vigente. Un agente no debe volver a separar
automáticamente estas capacidades en los antiguos `BT-GATE-011–017` sin
justificar una dependencia o frontera material que lo haga necesario.

### Regla de evidencia económica

Los runs anteriores a la incorporación del realismo específico de small caps
pueden utilizarse para validar el motor, pero deben etiquetarse:

```text
ENGINE_VALIDATION_RUN
NOT_EDGE_EVIDENCE
NOT_ECONOMICALLY_REALISTIC
```

No deben utilizarse para afirmar rentabilidad o edge mientras permanezcan sin
modelar restricciones materiales como borrow, locate, SSR, halts, liquidez o
capacidad.

### Obligación de los agentes

Todo agente que comience o continúe el backtester debe:

1. Leer este `AGENTS.md`.
2. Identificar el gate vigente y su capacidad final.
3. Trabajar hasta producir la evidencia completa del gate.
4. Evitar detenerse por microtransiciones documentales.
5. Mantener el rigor temporal, de ejecución, contable y de reproducibilidad.
6. No ampliar el alcance sin autorización.
7. Priorizar siempre un backtest end-to-end utilizable sobre componentes
   aislados sin integración.

## Sincronización obligatoria con Backtest Engine Governance

La autoridad institucional del backtester reside en:

C:\TSIS_Data\00_CTO\14_BACKTEST_ENGINE

La implementación, los tests, las configuraciones y los runs residen en:

C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE

Después de completar cualquier incremento material, el agente debe evaluar y,
cuando corresponda, actualizar Backtest Engine Governance antes de declarar
cerrado el trabajo.

Se considera incremento material cualquier cambio que:

- cree, modifique, cierre, sustituya o retire una decisión;
- cree o modifique una política;
- cree o modifique un contrato;
- abra, cierre, rechace o sustituya un gate;
- cambie el alcance autorizado;
- implemente una capacidad nueva;
- modifique semántica de ejecución, replay, accounting o datos;
- añada tests de aceptación o evidencia ejecutada;
- introduzca una limitación, excepción, waiver o deuda;
- cambie un estado como NOT_AUTHORIZED, DRAFT, CLOSED o IMPLEMENTED;
- invalide o sustituya documentación viva.

Para estos incrementos, la actualización de governance forma parte de la
Definition of Done. No es una tarea opcional posterior.

El agente debe seguir:

C:\TSIS_Data\00_CTO\14_BACKTEST_ENGINE\
08_GATES_AND_REVIEWS\GOVERNANCE_UPDATE_PROTOCOL.md

Como mínimo debe revisar si corresponde actualizar:

- README.md
- AGENTS.md
- LOCAL_RULES.md
- CHANGELOG.md
- 04_DECISIONS\DECISION_LEDGER.json
- 05_POLICIES\POLICY_REGISTER.json
- 06_TRACEABILITY\TRACEABILITY_MATRIX.json
- 07_EXCEPTIONS\EXCEPTION_AND_WAIVER_REGISTER.json
- 08_GATES_AND_REVIEWS\
- 10_VALIDATION\
- PACKAGE_MANIFEST.json

Ningún gate puede declararse CLOSED si la trazabilidad aplicable no conecta:

decisión o política
→ contrato
→ implementación
→ tests
→ evidencia o run
→ limitaciones
→ gate
→ changelog

No deben inventarse evidencias ni autorizaciones.

Si el código o los documentos locales demuestran una situación que todavía no
ha sido revisada institucionalmente, debe registrarse con el estado adecuado,
por ejemplo:

- DRAFT
- PENDING_REVIEW
- IMPLEMENTED_NOT_AUTHORIZED
- MISSING_EVIDENCE
- CONTRADICTORY
- NOT_EVALUATED

El agente no puede convertir unilateralmente una corrección técnica en
autorización institucional cuando el gate exige aprobación explícita.

La sincronización de governance no autoriza:

- Market State o Event State consumption;
- StateReplayFeed;
- lectura física de StateBundles;
- backtest con estados;
- integración activa con el State Provider.

Ese carril continuará como:

FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED

salvo autorización explícita posterior procedente de la autoridad correspondiente.

## Historical State Consumption Hold - SUPERSEDED BY BT-GATE-014

`HISTORICAL_SNAPSHOT`: this entire hold block records the boundary before
BT-GATE-014. It is not a current instruction and grants no present authority.
The current bounded authority is defined exclusively by the `Current Gate -
BT-GATE-014` block at the top of this file and the accepted V0.3 authorization.
StateReplayFeed, Event State, general Market State consumption and production
use remain unauthorized.

```text
AUTHORIZED_SCOPE = C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
BACKTEST_STATE_CONSUMPTION_LANE = FROZEN_DRAFT / HOLD / NOT_AUTHORIZED
BACKTEST_CONSUMER_CONTRACTS = DRAFT
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
PRODUCTION = false
DOWNSTREAM = false
```

Before touching anything, read at minimum:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/AGENTS.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/LOCAL_RULES.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/README.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/STATE_PROVIDER_CONSUMER_HOLD_HANDOFF_V0_1.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/contracts/backtest/backtest_run_spec_contract_v0_1.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/contracts/backtest/backtest_input_manifest_contract_v0_1.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/05_RUNPREFLIGHT_STATE_CONSUMPTION_IMPLEMENTATION_PLAN_V0_1.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/06_STATE_REPLAY_FEED_IMPLEMENTATION_PLAN_V0_1.md
```

Context-only reads require explicit user approval and do not grant edit authority:

```text
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/README.md
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/99_archive/v0_1_2_boundary_quarantine_20260728/README.md
```

Do not edit or generate files under:

```text
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES
```

Do not implement or execute yet:

```text
StateReplayFeed
RunPreflight state consumption
Market/Event State physical reads
StateBundleManifest physical opening
EventLoop state delivery
strategy access to Market State/Event State
orders/fills/PnL driven by states
provider-consumer compatibility review
```

If work involving Market State or Event State appears, keep it as DRAFT/fail-closed and wait until the provider delivers an authorized provider-only package that has passed independent external audit.

The backtester may continue only with bounded work that does not depend on state consumption, such as historical replay already authorized for OHLCV, mechanical event loop, accounting, run manifests, execution semantics drafts, tests and local engine infrastructure.

Before each new operational step, state the intended files and action to the user. Do not exceed this folder without explicit user authorization.
## 1. What This Folder Is

```text
02_TSIS_BACKTEST_ENGINE
= Python implementation root for the backtester
```

It contains code, tests, configs, executable runs and engine outputs.

It does not own the high-level architecture or data certification. Those remain here:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION
```

## 2. Read First

Read in this order:

```text
1. C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/README.md
2. C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/LOCAL_RULES.md
3. C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/CHANGELOG.md
4. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/AGENT.md
5. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/LOCAL_RULES
6. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/README.md
7. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/01_DATA.md
8. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/02_REPLAY.md
9. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/03_MECHANICAL_TRADE_PATH.md
10. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/08_ACCOUNTING.md
```

If touching intraday data consumption, also read:

```text
8. G:/TSIS/data/README.md
9. C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
10. C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
11. C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/README.md
12. C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
```

## 3. Historical Objective Snapshot - SUPERSEDED BY BT-GATE-014

`HISTORICAL_SNAPSHOT`: this objective predates the accepted execution,
BT-GATE-013 physical replay and the current BT-GATE-014 bounded Market State
consumer work. It is retained only as project history.

Objective at that time:

```text
review EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1 before any execution-simulator code
```

Purpose:

```text
No strategy or order path may consume data until RunPreflight has resolved the dataset, universe, price views, session, timezone, missing-data policy, corporate-action policy and candidate authorization.

The next implementation increment must remain bounded and must not start until the execution semantics and cost-model contract is reviewed and explicitly authorized for code.
```
## 4. Historical Next Concrete Step Superseded By BT-GATE-012

Historical closed chain at the time of this note:

```text
RunPreflight
  -> HistoricalReplayFeed
  -> MechanicalEventLoop
  -> AccountingEngine
  -> real ABAT gross-to-net smoke
```

Historical next concrete step at the time of this note:

```text
HISTORICAL_GATE_AT_2026_07_29 = EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1_REVIEW
CONTRACT_STATE = CORRECTED_DRAFT_READY_FOR_REVIEW
CODE_IMPLEMENTATION = NOT_AUTHORIZED
NEXT_GATE_IF_CORRECTED_AND_AUTHORIZED = DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION

Do not start full 2005-2026 backtest.
```

Current evidence:

```text
run_id = accounting_abat_short_open_close_v0_1
preflight_status = PREFLIGHT_PASS
physical_inspection_status = PHYSICAL_INSPECTION_PASS
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
tests = 61 OK
```
## 5. Completed Gates

Completed verification:

```text
engine suite -> 61 tests OK
bounded real fixture preflight -> PREFLIGHT_PASS
bounded real fixture replay -> PASS
mechanical ABAT round trip -> PASS
accounting ABAT gross-to-net -> PASS
```

Completed accounting tests covered:

```text
zero costs -> net equals gross
commission per share and minimum commission
multiple cost components kept separate and summed
short loser net PnL
open position rejected
mechanical gross mismatch reported
deterministic accounting hash
real ABAT accounting smoke
```
## 6. Data Rules

For V0.1:

```text
session = REGULAR_ONLY
market_timezone = America/New_York
bar_interval = [ts_start, ts_end)
available_at = ts_end
hash_policy = SHA-256 only for files or partitions actually consumed
quote_guarded_1m execution use = proxy_allowed_for_engine_mechanics_only
```

Do not claim fill realism or edge from the first vertical slice.

## 7. Update Protocol

Every completed operational step must update:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/AGENTS.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/CHANGELOG.md
```

If a decision or contract changes, also update:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/AGENT.md
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/CHANGELOG.md
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/<affected_layer>.md
```

## 8. Live Log

Format:

```text
YYYY-MM-DD - STATUS - action - files touched - next action
```

Entries:

```text
2026-07-28 - DONE - Reset implementation root and recreated clean scaffold - README.md, AGENTS.md, LOCAL_RULES.md, CHANGELOG.md, pyproject.toml, src/, tests/, configs/, runs/, docs/ - next action: implement RunPreflight contracts and first synthetic tests
2026-07-28 - DONE - Implemented RunPreflight synthetic increment - docs/00_system/01_RUNPREFLIGHT_IMPLEMENTATION_PLAN_V0_1.md, contracts.py, registries.py, manifests.py, run_preflight.py, tests/unit/test_run_preflight.py - next action: select TSIS_REAL_DATA_FIXTURE
```

## 9. Do Not Do Now

```text
- Do not rebuild the old scaffold blindly.
- Do not write a complete architecture guide here.
- Do not consume real data before RunPreflight exists.
- Do not copy RAW data into this folder.
- Do not promote candidate datasets from inside the engine.
- Do not implement optimization, validation, portfolio or live trading before the first vertical slice.
```

## 10. Update 2026-07-28 - RunPreflight Synthetic Increment

```text
DONE: micro-plan created
DONE: contracts.py created
DONE: registries.py created
DONE: manifests.py created
DONE: run_preflight.py created
DONE: tests/unit/test_run_preflight.py created
DONE: 10 synthetic tests passing
NEXT: select and configure TSIS_REAL_DATA_FIXTURE
```

## 11. Update 2026-07-28 - RunPreflight Hardening

```text
RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED
SYNTHETIC_UNIT_TESTS = PASS, 21 tests
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

```text
DONE: four missing fail-closed tests added
DONE: full missing/corporate-action policies serialized
DONE: outputs isolated under output_root/run_id
DONE: non-empty run output rejected with RUN_OUTPUT_NOT_EMPTY
NEXT: implement minimal real-data inspector and select TSIS_REAL_DATA_FIXTURE
```

## 12. Update 2026-07-28 - RunPreflight Pre-Real Guards

```text
RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED
SYNTHETIC_UNIT_TESTS = PASS, 21 tests
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

```text
DONE: unsafe run_id rejected with INVALID_RUN_ID before output writes
DONE: run output containment under output_root enforced
DONE: candidate accepted validation manifest must match DatasetDefinition.validation_manifest
DONE: candidate dataset without registered validation manifest rejected
DONE: TSIS_REAL_DATA_FIXTURE fails closed with PHYSICAL_INSPECTION_NOT_IMPLEMENTED until inspector exists
NEXT: inspect physical layout/schema and implement minimal real-data inspector
```

Live log entry:

```text
2026-07-28 - DONE - Added pre-real RunPreflight guards - contracts.py, run_preflight.py, tests/unit/test_run_preflight.py, README.md, AGENTS.md, CHANGELOG.md - next action: implement minimal real-data inspector and select TSIS_REAL_DATA_FIXTURE
```

## 13. Update 2026-07-28 - Physical Layout Discovery

```text
PHYSICAL_LAYOUT_DISCOVERED = PASS
TSIS_REAL_DATA_FIXTURE_SELECTED = SELECTED_NOT_INSPECTED
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

Artifacts:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/configs/fixtures/TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1.json
```

Selected fixture:

```text
fixture_id = TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1
session_date = 2026-01-05
symbols = ABAT, ABEO, ABSI, ABTC, ACB
```

NEXT was completed by the RealDataInspector increment below.

Live log entry:

```text
2026-07-28 - DONE - Physical layout discovered and real fixture selected - docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.md, docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.json, configs/fixtures/TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1.json - next action: implement RealDataInspector
```

## 14. Update 2026-07-28 - RealDataInspector And Real Fixture Preflight

```text
REAL_DATA_INSPECTOR_IMPLEMENTED = PASS
SYNTHETIC_UNIT_TESTS = PASS, 34 tests
REAL_DATA_INSPECTION = PASS
REAL_DATA_PREFLIGHT = PASS
BACKTEST_VERTICAL_SLICE = NOT_STARTED
```

Implemented:

```text
- RealDataInspector for the selected quote-guarded parquet layout.
- PhysicalDataInspection and TickerDayInspection reports.
- Hash capture for consumed files.
- Fixture/request binding with `REAL_FIXTURE_REQUEST_MISMATCH`.
- Dataset validation-manifest SHA-256 verification with `VALIDATION_MANIFEST_HASH_MISMATCH`.
- Drift comparison against discovery evidence.
- Fail-closed checks for file missing, schema missing, open/close missing, duplicate timestamps, invalid OHLCV and effective corporate actions.
- Interior minute gaps are recorded as OBSERVED_MINUTE_GAP and allowed only under EMIT_GAP_WITHOUT_IMPUTATION.
- Vendor VWAP/vw is treated as non-consumable vendor-derived data and is not required or validated.
```

Verification:

```text
$env:PYTHONPATH='src'; python -m unittest discover -s tests
# Ran 34 tests OK
```

Real preflight evidence:

```text
run_id = run_preflight_real_fixture_2026_01_05_qg5_v0_2
preflight_status = PREFLIGHT_PASS
physical_inspection_status = PHYSICAL_INSPECTION_PASS
rows_available = 1828
source_files_consumed = 5
content_hashes = 9
complete_tickers = ABAT, ABTC
gap_tickers = ABEO, ABSI, ACB
warning_codes = OBSERVED_MINUTE_GAP
corporate_action_exact_rows = 0
validation_manifest_hash = verified
fixture_request_binding = enforced
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2/data_manifest.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2/universe_manifest.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2/data_preflight_report.json
```

Next action:

```text
start the minimum REPLAY/event-loop increment for the first vertical slice.
Do not start a full 2005-2026 backtest.
```

Live log entry:

```text
2026-07-28 - DONE - Implemented RealDataInspector and executed bounded real fixture preflight - real_data_inspector.py, contracts.py, manifests.py, run_preflight.py, tests/unit/test_real_data_inspector.py, fixture/discovery docs, pyproject.toml, runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2 - next action: minimum REPLAY/event-loop increment
```

## 15. Update 2026-07-28 - Minimum Replay

```text
REPLAY_MINIMUM_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 43 tests
REAL_FIXTURE_REPLAY_SMOKE = PASS
BACKTEST_VERTICAL_SLICE = DATA_REPLAY_READY
```

Implemented:

```text
- `src/tsis_backtest/replay/contracts.py`
- `src/tsis_backtest/replay/historical_feed.py`
- deterministic ordering by available_at, event priority, ticker
- `ReplayBarEvent` and `ReplayGapEvent`
- source hash verification before replay
- vendor `vw` excluded from event contract
```

Real replay evidence:

```text
replay_run_id = replay_real_fixture_2026_01_05_qg5_v0_1
event_count = 1950
bar_count = 1828
gap_count = 122
first_available_at = 2026-01-05T14:31:00+00:00
last_available_at = 2026-01-05T21:00:00+00:00
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/replay_real_fixture_2026_01_05_qg5_v0_1/replay_summary.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/replay_real_fixture_2026_01_05_qg5_v0_1/replay_event_sample.json
```

Next action:

```text
start the smallest mechanical Decision/Order/Fill/Position increment.
Do not start a full 2005-2026 backtest.
```

Live log entry:

```text
2026-07-28 - DONE - Implemented minimum REPLAY/event-loop and real fixture smoke - replay/contracts.py, replay/historical_feed.py, tests/unit/test_historical_replay_feed.py, docs/00_system/03_REPLAY_IMPLEMENTATION_PLAN_V0_1.md, runs/replay_real_fixture_2026_01_05_qg5_v0_1 - next action: mechanical Decision/Order/Fill/Position path
```

## 16. Update 2026-07-28 - Mechanical ABAT Round Trip

```text
MECHANICAL_TRADE_PATH_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 51 tests
REAL_ABAT_MECHANICAL_SMOKE = PASS
BACKTEST_VERTICAL_SLICE = GROSS_PNL_READY
```

Implemented:

```text
- `src/tsis_backtest/mechanics/contracts.py`
- `src/tsis_backtest/mechanics/event_loop.py`
- `ScheduledDecision`, `OrderIntent`, `Order`, `Fill`, `Position`, `TradeLedger`, `MechanicalRunSummary`
- programmed open/close proxy short path
- gross PnL derived from fills and checked against independent linear reference
```

Real ABAT evidence:

```text
run_id = mechanical_abat_short_open_close_v0_1
ticker = ABAT
quantity = 100
entry_price = 3.87
exit_price = 4.665
gross_pnl = -79.5
final_position_quantity = 0
execution_realism_claimed = false
edge_evaluated = false
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/mechanical_abat_short_open_close_v0_1/mechanical_run_summary.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/mechanical_abat_short_open_close_v0_1/trade_ledger.json
```

Next action:

```text
minimum accounting passed in the following section.
Do not start a full 2005-2026 backtest.
```

Live log entry:

```text
2026-07-28 - DONE - Implemented mechanical ABAT Decision/Order/Fill/Position round trip - mechanics/contracts.py, mechanics/event_loop.py, tests/unit/test_mechanical_event_loop.py, 01_GUIDE/03_MECHANICAL_TRADE_PATH.md, runs/mechanical_abat_short_open_close_v0_1 - next action: minimum cost/cash/net-PnL accounting
```

## 17. Update 2026-07-28 - Minimum Accounting

```text
ACCOUNTING_MINIMUM_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 61 tests
REAL_ABAT_ACCOUNTING_SMOKE = PASS
BACKTEST_VERTICAL_SLICE = ACCOUNTING_VERTICAL_SLICE_CLOSED
```

Implemented:

```text
- `src/tsis_backtest/accounting/contracts.py`
- `src/tsis_backtest/accounting/engine.py`
- `CostComponent`, `CostBreakdown`, `CostModel`, `CashLedgerEntry`, `AccountState`, `AccountingRunSummary`, `AccountingRunResult`
- gross-to-net reconciliation from mechanical ledger
- deterministic cash ledger and cost breakdowns
```

Real ABAT accounting evidence:

```text
run_id = accounting_abat_short_open_close_v0_1
ticker = ABAT
quantity = 100
starting_equity = 10000.00
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
ending_equity = 9918.50
final_position_quantity = 0
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/accounting_manifest.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/accounting_run_summary.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/cost_breakdowns.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/cash_ledger.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/account_state.json
```

Next action:

```text
review execution semantics and cost-model contract; code implementation remains NOT_AUTHORIZED.
Do not start full 2005-2026 backtest.
```

Live log entry:

```text
2026-07-28 - DONE - Implemented minimum accounting and real ABAT gross-to-net smoke - accounting/contracts.py, accounting/engine.py, tests/unit/test_accounting_engine.py, 01_GUIDE/08_ACCOUNTING.md, runs/accounting_abat_short_open_close_v0_1 - next action: choose bounded next increment
```
## 18. Update 2026-07-29 - Execution Semantics And Cost Model Contract

```text
EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1 = CORRECTED_DRAFT_READY_FOR_REVIEW
CONTRACT_DEFINITION = AUTHORIZED
CODE_IMPLEMENTATION = NOT_AUTHORIZED
BROKER_COST_REALISM = NOT_CLAIMED
FILL_REALISM = NOT_CLAIMED
SHORT_TRADABILITY = NOT_EVALUATED
EDGE = NOT_EVALUATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
```

Created:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md
```

Defined:

```text
bar_based_execution_profile_v0_1 = PRIMARY_FOR_NEXT_IMPLEMENTATION
quote_aware_execution_profile_v0_1 = RESERVED_NOT_AUTHORIZED_FOR_IMPLEMENTATION
same-bar lookahead prohibition
programmed open/close proxy legality
next-bar market proxy rule
market/limit/stop V0.1 semantics
order and fill states
adverse deterministic slippage rules
cost components and decimal rounding rules
missing bar/gap behavior
short execution mechanics vs short tradability separation
future acceptance tests
```

Next action:

```text
review the corrected contract and decide whether to authorize DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION.
Do not modify code until explicit authorization.
Do not start full 2005-2026 backtest.
```

Live log entry:

```text
2026-07-29 - DONE - Created execution semantics and cost-model contract draft - docs/00_system/07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md, AGENTS.md, CHANGELOG.md - next action: review contract; code implementation remains NOT_AUTHORIZED
```

## 19. Update 2026-07-29 - Deterministic Fill Simulator V0.1

```text
DETERMINISTIC_FILL_SIMULATOR_V0_1 = IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW
BT-GATE-010 = IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW
ENGINE_TEST_SUITE = PASS, 91 tests
ACCEPTANCE_RUN = deterministic_fill_simulator_v0_1_acceptance_v0_2
CODE_IMPLEMENTATION = IMPLEMENTED_FOR_DETERMINISTIC_FILL_SIMULATOR_V0_1_ONLY
```

Next action:

```text
review BT-GATE-010 implementation and acceptance packet before declaring CLOSED_PASS.
Do not start full 2005-2026 backtest.
Do not activate StateReplayFeed, Market State or Event State.
```

## Historical Gate Override - 2026-07-29 - SUPERSEDED

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
FINAL_OWNER_REVIEW = ACCEPTED

BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

LAST_CLOSED_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
BT-GATE-013_CONTRACT = CONTRACT_ACCEPTED
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
PHYSICAL_RUN = AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED
CURRENT_GATE = NONE
NEXT_GATE = NOT_OPEN
CODE_IMPLEMENTATION = NOT_AUTHORIZED_OUTSIDE_CLOSED_BT_GATE_013_SCOPE
```

HISTORICAL_SNAPSHOT: BT-GATE-012 and BT-GATE-013 were closed and no subsequent gate was open at this snapshot. StateReplayFeed, Market State, Event State, StateBundle reads, provider integration, the full 2005-2026 backtest, optimization and edge claims remain closed.

## 2026-07-29 | BT-GATE-011 single-strategy end-to-end implementation

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
run_id = bt_gate_011_open_short_close_qg5_v0_1
validation_status = PASS
engine_suite = 99 tests OK
FINAL_OWNER_REVIEW = ACCEPTED
```

Implemented path:

```text
StrategySpec -> HistoricalReplayFeed -> point-in-time decisions -> ExecutionOrder -> DeterministicFillSimulator V0.1 -> accounting -> Trade Ledger -> equity curve -> Unified Run Manifest
```

The run remains `ENGINE_VALIDATION_RUN`, `EDGE_EVIDENCE = NOT_AUTHORIZED`, `ECONOMIC_REALISM = INCOMPLETE`.

## BT-GATE-011 corrective acceptance evidence

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
EVENT_LOOP_INTEGRATION = PROVEN_BY_ONLINE_REPLAY_COORDINATOR_V0_1
PACKAGE_TEST_REPRODUCIBILITY = PASS
END_TO_END_RUN_REPRODUCIBILITY = PASS_WITH_PORTABLE_QG5_FIXTURE
ENGINE_TEST_SUITE = 99 tests OK
```

No StateReplayFeed, Market State, Event State or State Provider integration is authorized by this correction.

## 2026-07-29 | BT-GATE-011 accepted and BT-GATE-012 contract draft opened

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
FINAL_OWNER_REVIEW = ACCEPTED

HISTORICAL_CURRENT_GATE_AT_TIME = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
```

Contract draft:

```text
docs/00_system/12_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_CONTRACT_V0_1.md
```

## 2026-07-29 | BT-GATE-012 owner-approved for continuous implementation

```text
BT-GATE-012_OWNER_CONTRACT_REVIEW = PASS
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
EXECUTION_MODE = CONTINUOUS_UNTIL_FINAL_ACCEPTANCE_PACKET
NEXT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
```

Proceed with BT-GATE-012 implementation continuously until the final acceptance packet unless a material scope or semantic stop condition appears.

## 2026-07-29 | Historical BT-GATE-012 implementation acceptance evidence

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
ENGINE_TEST_SUITE = 106 tests OK
BT-GATE-012_FOCUSED_TESTS = 7 portfolio tests OK
BT-GATE-012_VALIDATION_STATUS = PASS
BT-GATE-012_DETERMINISM_STATUS = PASS
BT-GATE-012_DETERMINISTIC_OUTPUT_HASH = 414aceb2bc80836f8fa821cd4d14071e54c86f3c7855c0a34c82ffd8b1c79182
NEXT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
```

BT-GATE-012 later closed as accepted. StateReplayFeed, Market State, Event State and provider integration remain closed.

## Historical Snapshot - 2026-07-29 | BT-GATE-013 boundary corrected

```text
BT-GATE-013_NAME = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_ENGINE
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER = FUTURE_GATE_FAMILY_NOT_YET_OPEN
```

Rationale: BT-GATE-013 must cross exactly one new boundary after BT-GATE-012: from accepted portable fixture replay to reproducible physical historical data. It must prove physical row lineage, timestamp availability, session legality, replay determinism and accounting preservation before any small-caps tradability, SSR, borrow, locates, liquidity/capacity, batch research, DSR/PBO/CSCV or edge-evidence gates are opened.

Central rule preserved for future gates:

```text
mechanically executable order != actually shortable security != economically valid trade != demonstrated edge
```

The next work is contract definition only:

```text
docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
Status = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
Implementation = NOT_AUTHORIZED
```

## Historical Snapshot - 2026-07-29 | BT-GATE-013 contract draft placed in canonical backtester docs

```text
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = HISTORICAL_CONTRACT_DRAFT_PENDING_OWNER_REVIEW_SUPERSEDED_BY_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
CONTRACT_ARTIFACT = docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
```

The contract draft was copied into the canonical backtester document location. This does not authorize implementation, Market State consumption, Event State consumption, StateReplayFeed, provider modification or full 2005-2026 execution.

## Historical Snapshot - 2026-07-29 | BT-GATE-013 contract corrected after read-only review

```text
READ_ONLY_REVIEW = ACCEPTED
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PROVIDER_EVIDENCE_REQUIRED = false
```

The corrected contract freezes source identity layering, exact physical schema binding,
derived timestamp semantics, source row locator policy, portable relative paths and
repair-field restrictions. This does not authorize implementation, physical execution,
StateReplayFeed, Market State, Event State, provider modification, full 2005-2026 execution
or edge claims.



## 2026-07-29 | BT-GATE-013 implementation evidence prepared

```text
BT-GATE-013 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
PHYSICAL_RUN = AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED
IMPLEMENTATION_ACCEPTANCE = PENDING_FINAL_EXTERNAL_REVIEW
ENGINE_TEST_SUITE = 119 tests PASS
BT-GATE-013_FOCUSED_TESTS = 13 physical replay tests PASS
BT-GATE-013_VALIDATION_STATUS = PASS
BT-GATE-013_DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
RUN_ID = bt_gate_013_physical_historical_replay_slice_v0_1
```

This is implementation evidence only. Do not record `BT-GATE-013 = CLOSED_PASS` until the final acceptance packet is externally reviewed. StateReplayFeed, Market State, Event State, StateBundle reads, provider modification, full 2005-2026 backtest, optimization and edge claims remain not authorized.

## 2026-07-30 | BT-GATE-013 corrected acceptance evidence regenerated

```text
BT-GATE-013 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
IMPLEMENTATION_ACCEPTANCE = PENDING_FINAL_EXTERNAL_REVIEW
ENGINE_TEST_SUITE = 119 tests PASS
BT-GATE-013_FOCUSED_TESTS = 13 physical replay tests PASS
NEGATIVE_DERIVATIVES = 15 executed cases PASS
AUTHORIZED_SOURCE_IDENTITY_VALIDATION = PASS
FINAL_MANIFEST_REQUIRED_FIELDS = PASS
BT-GATE-013_DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
```

This supersedes the rejected BT-GATE-013 acceptance packet identity `42421cbe0668c458b4559eadf0aad44f2ec8f00a64956622920a384586c1fe1d`. The gate remains open until the corrected final acceptance packet is externally reviewed. StateReplayFeed, Market State, Event State, StateBundle reads, provider modification, full 2005-2026 backtest, optimization and edge claims remain not authorized.
