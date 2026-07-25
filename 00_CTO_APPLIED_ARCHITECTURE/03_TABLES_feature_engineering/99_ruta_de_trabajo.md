## 24/07/2026



Sí. El objetivo final no es simplemente “tener unas tablas”, sino llegar a esto:

```text
Solicitud reproducible
↓
Contrato de generación
↓
Resolución de fuentes y perfiles
↓
Construcción determinista
↓
Validación automática
↓
Market State Tables
+
Event State Tables
↓
Manifest + lineage + hashes
```

Actualmente estáis aquí:

```text
MARKET STATE
=
perfil semántico y evidencia física candidata disponibles

EVENT STATE
=
bounded execution-chain cerrada
+
candidate output validado y revisado
+
semantic profile promovido y artifact validation cerrada
+
operational registry / consumption policy design cerrado como referencia semantica
+
runtime capabilities architecture registrado sin ejecucion
+
market_state_on_demand_capability_design cerrado sin ejecucion
+
market_state_request_contract_design cerrado sin ejecucion
+
market_state_execution_plan_contract_design cerrado sin ejecucion
+
market_state_profile_resolver_design cerrado sin ejecucion
+
market_state_universe_resolver_design cerrado sin ejecucion
+
market_state_source_resolver_design cerrado sin ejecucion
+
market_state_partition_and_coverage_resolver_design cerrado sin ejecucion
+
market_state_materializer_design cerrado sin ejecucion
+
market_state_validator_design cerrado sin ejecucion
+
market_state_candidate_dataset_registry_design cerrado sin ejecucion
+
market_state_run_lifecycle_and_manifest_design cerrado sin ejecucion
+
market_state_on_demand_execution_chain_joint_review cerrado y aprobado para bounded execution authorization
+
market_state_bounded_on_demand_execution_authorization registrada
+
market_state_bounded_on_demand_execution cerrado como candidate parcial validado y registrado
+
sin official dataset/produccion/downstream
```

La ejecucion acotada de `session_opened`, XNYS, tres sesiones, tres instrumentos y nueve contextos ya cerro con 8 registros candidatos no oficiales y 1 contexto bloqueado. Esas filas son evidencia candidata validada; no son un dataset oficial de Event State.

# Mapa general

```text
PUNTO ACTUAL
│
├── A. Demostrar físicamente Event State
│
├── B. Promover Market State físico
│
├── C. Promover Event State físico
│
├── D. Construir materializadores parametrizados
│
├── E. Construir el Request Resolver
│
├── F. Construir validación y catálogo de resultados
│
└── G. Abrir generación bajo demanda
```

---

# FASE A — Demostrar la cadena física de Event State (TERMINADO)

## A1. Ejecutar el bounded run autorizado (TERMINADO)

Siguiente gate inmediato:

```text
event_state_bounded_execution_chain_execution_v0_1
```

Debe ejecutar exclusivamente:

```text
event_type =
session_opened

exchange =
XNYS

sessions =
3

instruments =
3

maximum contexts =
9
```

Debe producir:

```text
Event Instances
Event Window Bindings
Instrument Session Projections
Market State Bindings
Event State candidate records
Blocked-binding reports
Validation reports
Determinism report
Final manifest
```

No necesita producir nueve filas válidas.

Necesita demostrar:

```text
9 requested contexts
=
emitted contexts
+
blocked contexts
```

La autorización ya ha congelado la fuente física de Market State, la política `exactly_one`, la ausencia de fallbacks y los límites cuantitativos.

**TERMINADO**

A1 ya está hecho.

Estado real ahora:
```
Event State bounded execution
    = CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT

accepted_run =
event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z

candidate_records_jsonl = 8
blocked_contexts = 1
hard_validation_failures = 0
event_state_parquet = 0
official_dataset = false
downstream = false
```

## A2. Validación física del bounded run (TERMINADO)

Gate:

```text
event_state_bounded_execution_chain_physical_validation_v0_1
```

Comprobará:

```text
schema
types
identificadores
unicidad
exact-one bindings
lineage
hashes
temporal legality
state_role
consumption_legality
determinismo
scope compliance
```

Resultado posible:

```text
CLOSED_PASS_WITH_RESTRICTIONS
```

o:

```text
CLOSED_BLOCKED_NO_PROMOTION
```

## A3. Revisión del dataset candidato (TERMINADO)

Gate:

```text
event_state_candidate_dataset_review_v0_1
```

Aquí ya no se revisa solo si el software “funcionó”.

Se revisa si el output representa correctamente:

```text
Event State
=
Market State
+
Event Instance
+
Event Window
+
Instrument Projection
+
State Role
+
Consumption Legality
```

## A4. Correcciones y segunda ejecución controlada (NO REQUERIDO POR AHORA)

Es probable que el primer run encuentre:

```text
Market State rows inexistentes exactamente en el anchor
problemas de projection as-of
insuficiente prueba de decision_safe
campos de lineage incompletos
```

Eso no sería un fracaso.

La secuencia sería:

```text
finding
↓
contract correction
↓
new authorization/version
↓
bounded rerun
↓
physical validation
```

No deberíais ampliar el scope hasta conseguir una ejecución determinista y completamente reconciliada.

---

# FASE B — Convertir Market State en una capacidad física oficial

Ahora mismo Event State puede consumir solamente un parquet candidato no oficial:

```text
source_status =
non_official_candidate_reference_only
```

Esto sirve para demostrar la arquitectura, pero no para ofrecer tablas bajo demanda.

## B1. Cerrar el contrato físico de cada perfil de Market State

Debéis definir qué perfiles podrán solicitarse.

Por ejemplo:

```text
market_state_core
market_state_daily_context
market_state_intraday_core
market_state_microstructure
market_state_research
```

No todos tienen que existir inicialmente.

Primera versión recomendable:

```text
market_state_core_four_intraday_profile_v0_1
```

Cada perfil debe declarar:

```text
profile_id
profile_version
grain
required Information Objects
required Representation Models
required variables
source tables/views
temporal cutoff policy
point-in-time rules
quality gates
physical schema
partitioning
identity policy
fingerprint policy
```

## B2. Promoción física del primer perfil

Secuencia:

```text
candidate materialization
↓
physical validation
↓
candidate dataset review
↓
profile promotion review
↓
official profile contract
↓
official physical dataset authority
```

Resultado:

```text
market_state_core_four_intraday_profile_v0_1
=
OFFICIAL_PHYSICAL_PROFILE
```

Solo entonces dejará de dependerse del parquet experimental Scale C.

## B3. Construir el Market State Materializer

Este será el componente que pueda recibir:

```text
profile_id
universe
date range
resolution
source view versions
output destination
```

y producir:

```text
Market State table
manifest
validation report
lineage
hashes
```

La cadena será:

```text
Request
↓
Market State Profile Resolver
↓
Source Dataset/View Resolver
↓
Point-in-Time Universe Resolver
↓
Market State Builder
↓
Physical Materializer
↓
Validators
↓
Official or Candidate Output
```

## B4. Pruebas de escala

No pasar directamente de 104 filas a todo 2005–2026.

Escalas recomendadas:

```text
Scale A
=
pocos instrumentos, pocos días

Scale B
=
decenas de instrumentos, varias semanas

Scale C
=
muestra representativa amplia

Scale D
=
un año o segmento completo

Scale E
=
universo y rango completo
```

Cada escala debe probar:

```text
determinismo
memoria
tiempo
particiones
idempotencia
restartability
incremental builds
duplicate prevention
```

---

# FASE C — Convertir Event State en capacidad física oficial

Event State no puede oficializarse antes de disponer de una autoridad física estable de Market State.

## C1. Promover el primer Event State Profile (TERMINADO)

Primer perfil:

```text
event_state_core_four_intraday_profile_v0_1
```

**TERMINADO**

```text
promotion_run = event_state_profile_promotion_v0_1_20260724T203016Z
promotion_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
official_event_state_dataset = false
official_parquet = false
downstream_consumption = false
artifact_validation_run = event_state_profile_artifact_validation_v0_1_20260724T204410Z
artifact_validation_status = CLOSED_PASS_WITH_RESTRICTIONS
artifact_validation_registry_artifacts_checked = 4
artifact_validation_hash_mismatches = 0
artifact_validation_invariant_failures = 0
operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
operational_registry_or_consumption_policy_design_profile_reference_allowed = true
operational_registry_or_consumption_policy_design_physical_consumption_allowed = false
runtime_capabilities_architecture = RECORDED_ARCHITECTURE_NO_EXECUTION
runtime_capabilities_layer = 08_RUNTIME_CAPABILITIES
market_state_on_demand_capability_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_request_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_execution_plan_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_profile_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_universe_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_source_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_partition_and_coverage_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_materializer_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_validator_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_candidate_dataset_registry_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_run_lifecycle_and_manifest_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_on_demand_execution_chain_joint_review = CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
market_state_bounded_on_demand_execution_authorization = CONSUMED_BY_RUN
market_state_bounded_on_demand_execution = CLOSED_PASS_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED
market_state_bounded_on_demand_execution_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
market_state_request_records_created = 1
market_state_execution_plans_created = 1
market_state_profile_resolver_executions = 1
market_state_profile_registry_runtime_reads = 0
market_state_universe_resolver_executions = 1
market_state_universe_manifests_created = 0
market_state_instrument_session_contexts_created = 9
market_state_calendar_runtime_reads = 0
market_state_instrument_master_runtime_reads = 0
market_state_instrument_identity_runtime_reads = 0
market_state_source_resolver_executions = 1
market_state_source_registry_runtime_reads = 0
market_state_source_contract_runtime_reads = 0
market_state_source_schema_runtime_reads = 0
market_state_source_consumption_policy_runtime_reads = 0
market_state_source_parquet_files_read = 0
market_state_resolved_source_sets_created = 0
market_state_partition_coverage_resolver_executions = 1
market_state_partition_manifests_created = 0
market_state_coverage_manifests_created = 0
market_state_existing_dataset_registry_runtime_reads = 0
market_state_source_manifest_runtime_reads = 0
market_state_partition_status_transitions = 0
market_state_execution_plan_instances_created = 1
market_state_materializer_executions = 1
market_state_builder_executions = 1
market_state_staging_directories_created = 0
market_state_candidate_data_files_written = 2
market_state_candidate_parquet_files_written = 1
market_state_output_manifests_created = 0
market_state_lineage_manifests_created = 0
market_state_content_hashes_computed = 0
market_state_validation_reports_created = 5
market_state_validator_executions = 1
market_state_candidate_files_read = 0
market_state_parquet_files_read = 0
market_state_partition_status_changes = 0
market_state_quarantine_actions = 0
market_state_dataset_registry_entries_written = 1
market_state_registry_runtime_reads = 0
market_state_datasets_registered = 1
market_state_datasets_promoted = 0
market_state_datasets_superseded = 0
market_state_quarantine_transitions = 0
market_state_official_dataset = false
market_state_run_records_created = 1
market_state_run_manifests_created = 3
market_state_final_manifests_created = 1
market_state_heartbeat_records_written = 1
market_state_run_state_transitions = 4
market_state_recovery_actions = 0
market_state_execution_authorizations_consumed = 1
market_state_execution_plans_consumed = 1
market_state_joint_reviews_closed = 1
market_state_joint_review_hard_findings = 0
market_state_joint_review_restriction_findings = 2
market_state_bounded_on_demand_execution_authorizations_recorded = 1
market_state_bounded_on_demand_execution_authorized_max_contexts = 9
market_state_bounded_on_demand_execution_runs = 1
market_state_bounded_on_demand_execution_requested_contexts = 9
market_state_bounded_on_demand_execution_materialized_rows = 8
market_state_bounded_on_demand_execution_unavailable_contexts = 1
market_state_bounded_on_demand_execution_hard_validation_failures = 0
market_state_bounded_on_demand_execution_reuse_eligibility = pending_determinism_validation
market_state_bounded_on_demand_candidate_dataset_review = CLOSED_APPROVED_AS_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION
market_state_bounded_on_demand_candidate_dataset_review_id = market_state_bounded_on_demand_candidate_dataset_review_v0_1_20260725T000000Z
market_state_bounded_on_demand_candidate_dataset_review_failures = 0
market_state_bounded_on_demand_candidate_dataset_review_hard_failures = 0
market_state_bounded_on_demand_deterministic_rerun_authorization = CONSUMED_BY_RERUN
market_state_bounded_on_demand_deterministic_rerun_authorization_baseline_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
market_state_bounded_on_demand_deterministic_rerun_contract_content_sha256_excluding_hash_field = b3bc623ca83885f8773d8bd95f48418e1fa15c6038840d35da7cad860595f231
market_state_bounded_on_demand_deterministic_rerun_execution = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS
market_state_bounded_on_demand_deterministic_rerun_run = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z
market_state_bounded_on_demand_deterministic_rerun_blocked_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z
market_state_bounded_on_demand_deterministic_rerun_attempts = 2
market_state_bounded_on_demand_deterministic_rerun_successful_runs = 1
market_state_bounded_on_demand_deterministic_rerun_blocked_comparison_normalization_attempts = 1
market_state_bounded_on_demand_determinism_comparisons_created = 2
market_state_bounded_on_demand_determinism_successful_comparisons_created = 1
market_state_bounded_on_demand_determinism_status = PROVEN_FOR_BOUNDED_SCOPE
market_state_bounded_on_demand_determinism_blocking_failures = 0
market_state_bounded_on_demand_determinism_runtime_only_differences = 2
market_state_bounded_on_demand_determinism_comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb
market_state_bounded_on_demand_determinism_scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
market_state_bounded_on_demand_reuse_transition_ready = true
market_state_bounded_on_demand_reuse_eligibility_changes = 0
market_state_bounded_on_demand_determinism_validation = CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION
market_state_bounded_on_demand_determinism_validation_id = market_state_bounded_on_demand_determinism_validation_v0_1_20260725T000000Z
market_state_bounded_on_demand_determinism_validation_failures = 0
market_state_bounded_on_demand_determinism_validation_hard_failures = 0
market_state_bounded_on_demand_determinism_validation_reuse_eligibility_after_validation = pending_idempotency_reuse_test
market_state_bounded_on_demand_determinism_validation_reuse_eligibility_changes = 0
market_state_bounded_on_demand_idempotency_reuse_test_authorization = CONSUMED_BY_REUSE_TEST
market_state_bounded_on_demand_idempotency_reuse_test_authorization_baseline_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
market_state_bounded_on_demand_idempotency_reuse_test_authorization_scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
market_state_bounded_on_demand_idempotency_reuse_test_contract_content_sha256_excluding_hash_field = c836f3ae2d5821a0d2d7b66ee1c2db1c1866fe83b36a2d1fbb27f31bf678b98d
market_state_bounded_on_demand_idempotency_reuse_test_execution = CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS
market_state_bounded_on_demand_idempotency_reuse_test_run = market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z
market_state_bounded_on_demand_idempotency_status = PROVEN_FOR_BOUNDED_EXACT_MATCH_REUSE
market_state_bounded_on_demand_idempotency_reuse_test_runs = 1
market_state_bounded_on_demand_idempotency_reuse_test_candidate_registry_metadata_reads = 1
market_state_bounded_on_demand_idempotency_reuse_test_materializer_executions = 0
market_state_bounded_on_demand_idempotency_reuse_test_source_market_data_rows_read = 0
market_state_bounded_on_demand_idempotency_reuse_test_source_candidate_records_read = 0
market_state_bounded_on_demand_idempotency_reuse_test_candidate_parquet_files_read = 0
market_state_bounded_on_demand_idempotency_reuse_test_new_candidate_parquet_files = 0
market_state_bounded_on_demand_idempotency_reuse_test_new_candidate_dataset_registry_entries = 0
market_state_bounded_on_demand_idempotency_reuse_test_evidence_entries_written = 1
market_state_bounded_on_demand_idempotency_reuse_test_reuse_eligibility_after_test = pending_reuse_eligibility_transition_review
market_state_bounded_on_demand_idempotency_reuse_test_reuse_eligibility_changes = 0
market_state_bounded_on_demand_idempotency_reuse_test_report_fingerprint = 2fe42810eff703a99aa64ebc67dda9126567c7548b6f99fbe589664490c6f537
market_state_bounded_on_demand_idempotency_reuse_test_evidence_entry_fingerprint = 97f3f0cb5bde4cac4a666f95f16fee2ee71eea821701355d7e8495963aff92b4
market_state_bounded_on_demand_reuse_eligibility_transition_review = CLOSED_APPROVED_REUSE_ELIGIBILITY_TRANSITION_FOR_BOUNDED_EXACT_MATCH_WITH_RESTRICTIONS_NO_PROMOTION
market_state_bounded_on_demand_reuse_eligibility_transition_review_run = market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061233Z
market_state_bounded_on_demand_reuse_eligibility_transition_review_blocked_attempt = market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061154Z
market_state_bounded_on_demand_reuse_eligibility_transition_review_technical_write_failure_attempt = market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061119Z
market_state_bounded_on_demand_reuse_eligibility_after_review = eligible_for_bounded_exact_match_reuse
market_state_bounded_on_demand_reuse_eligibility_transition_scope = bounded_exact_match_only
market_state_bounded_on_demand_reuse_eligibility_transition_registry_entry_mutations = 0
market_state_bounded_on_demand_reuse_eligibility_transition_official_dataset = false
market_state_bounded_on_demand_reuse_eligibility_transition_production = false
market_state_bounded_on_demand_reuse_eligibility_transition_downstream = false
market_state_bounded_on_demand_reuse_eligibility_transition_matrix_fingerprint = e8f1010c078a7ab9e68fa8ef072d7d9fb212f8623341617254e550aa26924f9a
market_state_bounded_on_demand_reuse_eligibility_transition_record_fingerprint = a1ea1e56d7f1b44cd0c91a37e0f6ecc2f4cbbbb16fd6be247f4e4e8959d8d845
market_state_requests_executed = 1
market_state_datasets_written = 1
next_gate = market_state_on_demand_incremental_overlap_execution_authorization_v0_1
```

Inicialmente podría admitir únicamente:

```text
event_type:market_data:session_opened
```

Eso está bien.

Un perfil oficial no necesita contener todos los eventos futuros.

Debe declarar:

```text
accepted Event Types
compatible Market State profiles
Event Instance policies
Window Definitions
Projection policies
state_role rules
consumption_legality rules
physical schema
identity and fingerprint rules
```

## C2. Crear el Event State Materializer

Cadena:

```text
Event State Request
↓
Event Type Registry Resolver
↓
Event Instance Resolver
↓
Event Window Resolver
↓
Instrument Projection Resolver
↓
Market State Profile Resolver
↓
Exact Binding Engine
↓
Event State Builder
↓
Validators
↓
Materializer
```

## C3. Ampliar Event Types de forma controlada

No se debe añadir cada nuevo evento directamente al builder.

Cada uno debe pasar:

```text
Candidate Event Type
↓
Admission Review
↓
Accepted / Accepted With Restrictions
↓
Instance Binding Design
↓
Window Binding Design
↓
Market State Compatibility
↓
Bounded Execution
↓
Validation
↓
Profile inclusion review
```

Ejemplos futuros:

```text
halt_resumed
vwap_cross_from_below
high_of_day_break
first_pullback_after_expansion
```

Pero cada uno evoluciona independientemente.

## C4. Resolver `halt_resumed`

Antes de admitirlo:

```text
resume effective timestamp
published timestamp
received timestamp
point-in-time availability
halt/resume pairing
multiple halts per session
venue coverage
UTC normalization
```

Hasta entonces no debe aparecer en Event State oficial.

---

# FASE D — Construir el sistema de solicitudes

Aquí empieza realmente la capacidad “a demanda”.

## D1. Canonical Request Contract

Necesitáis un contrato único de solicitud.

Ejemplo conceptual para Market State:

```json
{
  "request_type": "market_state",
  "profile_id": "market_state_core_four_intraday_profile_v0_1",
  "start_date": "2021-01-01",
  "end_date": "2021-01-31",
  "universe_definition": "daily_in_play_universe_v0_1",
  "resolution": "1m",
  "output_mode": "candidate"
}
```

Para Event State:

```json
{
  "request_type": "event_state",
  "profile_id": "event_state_core_four_intraday_profile_v0_1",
  "event_type_ids": [
    "event_type:market_data:session_opened"
  ],
  "start_date": "2021-01-01",
  "end_date": "2021-01-31",
  "universe_definition": "daily_in_play_universe_v0_1",
  "output_mode": "candidate"
}
```

## D2. Request Resolver

Debe resolver:

```text
¿Existe el perfil?
¿Está aceptado?
¿Qué versión debe utilizarse?
¿Qué datos físicos necesita?
¿Qué Event Types están permitidos?
¿Qué rango temporal tiene cobertura?
¿Qué universe definition es legal?
¿Qué output status puede producir?
```

Si algo no está autorizado:

```text
request =
BLOCKED_BEFORE_EXECUTION
```

## D3. Plan de ejecución

Antes de construir datos, el sistema produce:

```text
execution_plan.json
```

Con:

```text
resolved profile
resolved sources
partitions
estimated rows
estimated bytes
calendar sessions
instrument universe
Event Types
Window Definitions
output location
validators
quantitative limits
```

## D4. Identificador determinista de request

Cada solicitud debe producir:

```text
request_fingerprint
```

basado en:

```text
profile version
source versions
universe definition
date range
resolution
event types
window definitions
builder version
```

Así:

```text
misma solicitud
+
mismas autoridades
=
mismo request fingerprint
```

Esto permite detectar si el resultado ya existe.

---

# FASE E — Ejecución reproducible bajo demanda

## E1. Run lifecycle

Cada petición debe recorrer:

```text
REQUESTED
↓
RESOLVED
↓
AUTHORIZED
↓
RUNNING
↓
VALIDATING
↓
CLOSED_PASS
```

o:

```text
BLOCKED
FAILED
QUARANTINED
```

## E2. Idempotencia

Si solicitas dos veces exactamente lo mismo:

```text
same request fingerprint
```

el sistema debe:

```text
devolver el output existente
```

o:

```text
reconstruirlo y demostrar igualdad
```

Nunca generar dos datasets aparentemente distintos sin razón.

## E3. Incrementalidad

Solicitar:

```text
2021-01-01 → 2021-12-31
```

y posteriormente:

```text
2022-01-01 → 2022-12-31
```

no debería exigir reconstruir 2021.

Necesitáis:

```text
partition-aware materialization
incremental manifests
partition hashes
partition validation
```

## E4. Restartability

Un run interrumpido debe poder continuar desde:

```text
last certified partition
```

No desde cero.

## E5. Outputs estándar

Cada solicitud debe devolver:

```text
data files
final_manifest.json
validation_report.json
lineage_manifest.json
request_contract.json
execution_plan.json
run_readout.md
```

Y para Event State:

```text
blocked_bindings_report
Event Instance manifest
Window Binding manifest
Projection manifest
```

---

# FASE F — Catálogo y registro de datasets generados

Necesitáis un catálogo local para responder:

```text
¿Qué tablas existen?
¿Con qué perfil?
¿Para qué fechas?
¿Con qué universe?
¿Con qué fuentes?
¿Pasaron validación?
¿Están obsoletas?
```

## Dataset Registry

Cada resultado debería registrar:

```text
dataset_id
request_fingerprint
dataset_kind
profile_id
profile_version
coverage
universe
row count
file paths
file hashes
source lineage
builder version
validation status
promotion status
created_at
supersession status
```

Estados:

```text
candidate
validated_candidate
official
quarantined
superseded
deprecated
```

Este catálogo es imprescindible para que “a demanda” no signifique construir ciegamente cada vez.

---

# FASE G — Interfaz operativa

No necesitáis una GUI.

La primera interfaz puede ser CLI o Python.

## CLI conceptual

```text
tsis build market-state \
  --profile market_state_core_four_intraday_profile_v0_1 \
  --from 2021-01-01 \
  --to 2021-01-31 \
  --universe daily_in_play_universe_v0_1
```

```text
tsis build event-state \
  --profile event_state_core_four_intraday_profile_v0_1 \
  --events session_opened \
  --from 2021-01-01 \
  --to 2021-01-31 \
  --universe daily_in_play_universe_v0_1
```

## Python API conceptual

```python
result = tsis.build_market_state(
    profile_id="market_state_core_four_intraday_profile_v0_1",
    start_date="2021-01-01",
    end_date="2021-01-31",
    universe_id="daily_in_play_universe_v0_1",
)
```

```python
result = tsis.build_event_state(
    profile_id="event_state_core_four_intraday_profile_v0_1",
    event_type_ids=["event_type:market_data:session_opened"],
    start_date="2021-01-01",
    end_date="2021-01-31",
    universe_id="daily_in_play_universe_v0_1",
)
```

La CLI y la API deben llamar al mismo núcleo.

No deben contener lógica científica propia.

---

# Roadmap concreto desde hoy

## Tramo 1 — Cerrar la prueba Event State (TERMINADO)

```text
1. Execute bounded Event State chain (TERMINADO)
2. Physical validation (TERMINADO)
3. Candidate dataset review (TERMINADO)
4. Fix findings (NO REQUERIDO POR AHORA)
5. Deterministic bounded rerun (NO REQUERIDO POR AHORA)
```

**Resultado:**

```text
Event State physical chain proven
```

## Tramo 2 — Oficializar Market State

```text
6. Freeze first official Market State physical profile
7. Promote physical Market State source
8. Build parameterized Market State materializer
9. Validate at progressively larger scales
10. Certify incremental and deterministic builds
```

**Resultado:**

```text
Market State can be requested on demand
```

## Tramo 3 — Oficializar Event State

```text
11. Promote first Event State profile (TERMINADO)
12. Build parameterized Event State materializer
13. Run candidate scale tests
14. Validate exact bindings and temporal legality
15. Certify incremental and deterministic builds
```

**Resultado:**

```text
Event State can be requested on demand
for accepted Event Types
```

## Tramo 4 — Request and Registry Layer

```text
16. Define canonical request contract
17. Build request resolver
18. Build execution planner
19. Build run lifecycle
20. Build dataset registry
21. Build cache/idempotency logic
22. Build partition and restart logic
```

**Resultado:**

```text
same request
=
same governed result
```

## Tramo 5 — User-facing invocation

```text
23. CLI
24. Python API
25. notebooks as client
26. operational documentation
27. end-to-end acceptance tests
```

**Resultado final:**

```text
Solicito Market State o Event State
↓
TSIS resuelve el contrato
↓
construye o reutiliza el dataset
↓
valida
↓
registra
↓
entrega tablas reproducibles
```

---

# Cuándo podremos decir que está “terminado”

## Market State on demand estará terminado cuando

```text
un perfil oficial pueda solicitarse
para un rango y universo arbitrarios autorizados;
```

```text
las fuentes se resuelvan automáticamente;
```

```text
la construcción sea point-in-time;
```

```text
los outputs sean deterministas;
```

```text
el resultado tenga manifest, lineage y hashes;
```

```text
pueda construirse incrementalmente;
```

```text
una solicitud repetida reutilice o reproduzca el mismo resultado.
```

## Event State on demand estará terminado cuando, además

```text
solo acepte Event Types admitidos;
```

```text
genere Event Instances deterministas;
```

```text
resuelva ventanas, proyecciones y Market State exactamente una vez;
```

```text
bloquee ambigüedades;
```

```text
preserve state_role y consumption_legality;
```

```text
no permita leakage;
```

```text
registre todos los bindings y bloqueos.
```

# La idea central

No faltan cientos de documentos conceptuales.

Lo que falta desde este punto es transformar la arquitectura gobernada en tres capacidades operativas:

```text
1. Materialize Market State
```

```text
2. Materialize Event State
```

```text
3. Resolve and execute requests
```

El orden correcto es:

```text
probar una ejecución mínima
↓
promover los perfiles físicos
↓
generalizar los builders
↓
añadir request resolver
↓
añadir registry e incrementalidad
↓
abrir consumo bajo demanda
```

El próximo paso inmediato no cambia:

```text
event_state_bounded_execution_chain_execution_v0_1
```

Pero el verdadero hito posterior será:

```text
market_state_on_demand_materialization_v0_1
```

porque Event State dependerá siempre de que Market State pueda resolverse y materializarse de forma estable.




#######



## Mi ajuste a la ruta sería este:

1. Validar físicamente el bounded Event State output
2. Revisar el candidate Event State dataset
3. Si pasa, cerrar “Event State physical chain proven”
4. Volver a Market State on-demand/materializer
5. Solo después generalizar Event State on-demand

Estoy de acuerdo con la idea central:

Solicitud reproducible
↓
Contrato
↓
Resolver
↓
Build determinista
↓
Validación
↓
Manifest + lineage + hashes

Pero no saltaría demasiado rápido a “promoción física oficial”. Primero demostraría la capacidad operativa parametrizada:

profile resolver
source resolver
execution planner
materializer
validator
dataset registry
idempotency/cache

Para Market State, el hito real no es copiar el parquet Scale C ni llamarlo oficial. Es crear:

market_state_on_demand_materialization_v0_1

capaz de construir un perfil autorizado para un scope solicitado, con manifests y validación.

Para Event State, haría lo mismo después, porque siempre dependerá de Market State.

Ruta corregida:

A. Event State bounded physical validation
B. Event State candidate dataset review
C. Market State materializer/request capability
D. Market State scale/idempotency validation
E. Event State materializer/request capability
F. Dataset registry + request resolver común
G. CLI/API

La frase clave: no promover primero tablas; primero promover capacidades reproducibles de generación y validación. Luego las tablas oficiales salen como
consecuencia gobernada de esas capacidades.



Sí. **Tu corrección es mejor que mi formulación anterior.**

La diferencia central es esta:

```text
promover tablas
```

no debe ser el objetivo inmediato.

El objetivo inmediato debe ser:

```text
promover una capacidad reproducible
de generación, validación y registro
```

Y solo después:

```text
las tablas oficiales
=
outputs gobernados de esa capacidad
```

# Ruta corregida y definitiva

```text
A. Event State bounded physical validation
↓
B. Event State candidate dataset review
↓
C. Market State on-demand materialization capability
↓
D. Market State scale, determinism and idempotency validation
↓
E. Event State on-demand materialization capability
↓
F. Common request resolver and dataset registry
↓
G. CLI / Python API
```

Esta ruta es más sólida porque evita convertir un artefacto físico puntual en “producto oficial” antes de haber demostrado que puede reconstruirse.

---

# A. Event State bounded physical validation

El bounded run autorizado debe ejecutarse y validarse físicamente.

Objetivo:

```text
demostrar que la cadena diseñada
puede producir Event State real
sin romper sus contratos
```

Debe comprobarse:

```text
Event Instance determinista
Event Window determinista
Instrument Projection válida
Market State binding exactly-one
state_role correcto
consumption_legality correcta
lineage completa
hashes reproducibles
blocked contexts reconciliados
```

El resultado no es todavía una capacidad on-demand.

Es:

```text
Event State physical chain proven
```

---

# B. Event State candidate dataset review

Después de la validación física:

```text
candidate output
↓
scientific and architectural review
```

Aquí se decide si el output representa realmente Event State y no solo si el script terminó.

Debe responder:

```text
¿La identidad es correcta?
¿Los timestamps son legales?
¿Los bindings son exactos?
¿Existe leakage?
¿La projection conserva la identidad exchange-session?
¿Los bloqueos son correctos?
¿El dataset es reproducible?
```

Si pasa:

```text
event_state_physical_chain
=
PROVEN_WITH_RESTRICTIONS
```

Después se detiene Event State temporalmente.

No se generaliza todavía.

---

# C. Market State on-demand materialization capability

Este es el siguiente gran bloque real.

No consiste en promocionar el parquet Scale C.

Consiste en crear:

```text
market_state_on_demand_materialization_v0_1
```

La capacidad debe aceptar una solicitud como:

```text
profile_id
date range
universe
resolution
source versions
output mode
```

y producir:

```text
Market State dataset
manifest
lineage
validation report
hashes
registry entry
```

## Componentes mínimos

```text
Market State Request Contract
↓
Profile Resolver
↓
Source Resolver
↓
Execution Planner
↓
Market State Builder
↓
Materializer
↓
Validator
↓
Dataset Registry
```

## Principio importante

El `profile resolver` decide:

```text
qué representación se solicita
```

El `source resolver` decide:

```text
qué fuentes físicas autorizadas
pueden construirla
```

El `execution planner` decide:

```text
cómo se divide y ejecuta el trabajo
```

El `materializer` construye:

```text
las tablas
```

El `validator` determina:

```text
si son utilizables
```

El `dataset registry` conserva:

```text
qué se construyó
con qué inputs
y con qué resultado
```

---

# D. Market State scale, determinism and idempotency validation

Una vez exista el materializer, no se declara terminado inmediatamente.

Debe probarse por escalas.

```text
Scale A
pocos instrumentos y pocos días
```

```text
Scale B
decenas de instrumentos y semanas
```

```text
Scale C
muestra representativa
```

```text
Scale D
periodo amplio
```

```text
Scale E
universo completo autorizado
```

## Pruebas obligatorias

### Determinismo

```text
same request
+
same source versions
+
same builder version
=
same dataset hashes
```

### Idempotencia

```text
same request fingerprint
=
reuse existing validated output
or prove equivalent rebuild
```

### Incrementalidad

```text
existing partitions
+
new requested period
=
build only missing partitions
```

### Restartability

```text
interrupted run
=
resume from last certified partition
```

### Scope compliance

El sistema no puede leer:

```text
otras fechas
otros instrumentos
otras vistas
otras versiones
```

fuera del plan resuelto.

### Reconciliation

```text
requested contexts
=
emitted
+
blocked
+
quarantined
```

Siempre.

## Hito de cierre

```text
market_state_on_demand_materialization_v0_1
=
PROVEN_OPERATIONAL_CAPABILITY
```

En ese momento ya puede decirse:

```text
TSIS puede construir Market State bajo demanda
```

aunque todavía solo para perfiles y scopes autorizados.

---

# E. Event State on-demand materialization capability

Solo después se generaliza Event State.

Debe reutilizar Market State como servicio interno gobernado.

```text
Event State Request
↓
Event Type Registry Resolver
↓
Event Instance Resolver
↓
Window Resolver
↓
Instrument Projection Resolver
↓
Market State Request/Resolver
↓
Exact Binding Engine
↓
Event State Builder
↓
Validator
↓
Dataset Registry
```

## Diferencia fundamental

Event State no debería reconstruir Market State por su cuenta.

Debe solicitarlo mediante la capacidad ya probada:

```text
Event State Materializer
↓
Market State Request Contract
↓
Market State On-Demand Capability
```

Así se evita tener dos formas distintas de construir Market State.

## Primer alcance

Inicialmente:

```text
event_type =
session_opened
```

Posteriormente, cada Event Type nuevo deberá incorporarse mediante:

```text
admission
binding design
bounded execution
validation
profile inclusion
```

## Hito de cierre

```text
event_state_on_demand_materialization_v0_1
=
PROVEN_OPERATIONAL_CAPABILITY
```

---

# F. Common request resolver and dataset registry

Aquí matizaría ligeramente tu orden.

Los componentes pueden existir inicialmente dentro de Market State, pero después deben extraerse y convertirse en infraestructura común.

```text
Common Request Layer
├── Request Contract
├── Request Fingerprint
├── Profile Resolver
├── Execution Planner
├── Run Lifecycle
├── Dataset Registry
├── Cache / Idempotency
└── Output Resolver
```

Market State y Event State utilizarán la misma infraestructura, con resolvers especializados.

## Request Resolver común

Recibe:

```text
request_type =
market_state | event_state
```

y resuelve:

```text
perfil
versiones
fuentes
rango
universo
dependencias
particiones
outputs existentes
permisos
```

## Dataset Registry común

Debe poder responder:

```text
¿Existe ya esta solicitud?
¿Está validada?
¿Está completa?
¿Qué particiones faltan?
¿Qué versión la construyó?
¿Está superseded?
¿Puede consumirse downstream?
```

Estados posibles:

```text
planned
running
candidate
validated_candidate
official
quarantined
failed
superseded
deprecated
```

## Cache

No debería ser una cache opaca.

Debe ser:

```text
content-addressed governed reuse
```

Basada en:

```text
request_fingerprint
source fingerprints
builder version
profile version
```

---

# G. CLI y API

La CLI y la API son la última capa, no la arquitectura principal.

## CLI

```text
tsis build market-state \
  --profile market_state_core_four_intraday_profile_v0_1 \
  --from 2021-01-01 \
  --to 2021-01-31 \
  --universe scale_c_sample_v0_1
```

```text
tsis build event-state \
  --profile event_state_core_four_intraday_profile_v0_1 \
  --event-type event_type:market_data:session_opened \
  --from 2021-01-01 \
  --to 2021-01-31 \
  --universe scale_c_sample_v0_1
```

## Python API

```python
market_state_result = tsis.build_market_state(
    profile_id="market_state_core_four_intraday_profile_v0_1",
    start_date="2021-01-01",
    end_date="2021-01-31",
    universe_id="scale_c_sample_v0_1",
)
```

```python
event_state_result = tsis.build_event_state(
    profile_id="event_state_core_four_intraday_profile_v0_1",
    event_type_ids=["event_type:market_data:session_opened"],
    start_date="2021-01-01",
    end_date="2021-01-31",
    universe_id="scale_c_sample_v0_1",
)
```

Ambas interfaces deben invocar exactamente el mismo request resolver.

---

# Roadmap de gates recomendado

## Tramo inmediato: Event State bounded proof y perfil semantico (TERMINADO)

```text
1. event_state_bounded_execution_chain_execution_v0_1 (TERMINADO)
->
2. event_state_bounded_execution_chain_physical_validation_v0_1 (TERMINADO)
->
3. event_state_candidate_dataset_review_v0_1 (TERMINADO)
->
4. event_state_profile_promotion_review_v0_1 (TERMINADO)
->
5. event_state_profile_promotion_v0_1 (TERMINADO)
->
6. event_state_profile_artifact_validation_v0_1 (TERMINADO)
->
7. event_state_operational_registry_or_consumption_policy_design_v0_1 (TERMINADO)
->
8. runtime_capabilities_architecture_v0_1 (TERMINADO)
->
9. market_state_on_demand_capability_design_v0_1 (TERMINADO)
->
10. market_state_request_contract_design_v0_1 (TERMINADO)

11. market_state_execution_plan_contract_design_v0_1 (TERMINADO)

12. market_state_profile_resolver_design_v0_1 (TERMINADO)

13. market_state_universe_resolver_design_v0_1 (TERMINADO)

14. market_state_source_resolver_design_v0_1 (TERMINADO)

15. market_state_partition_and_coverage_resolver_design_v0_1 (TERMINADO)

16. market_state_materializer_design_v0_1 (TERMINADO)

17. market_state_validator_design_v0_1 (TERMINADO)
```

Resultado:

```text
Event State physical chain proven
```

---

## Tramo Market State on-demand

`	ext
9. market_state_on_demand_capability_design_v0_1 (TERMINADO)
->
10. market_state_request_contract_design_v0_1 (TERMINADO)
->
11. market_state_execution_plan_contract_design_v0_1 (TERMINADO)
->
12. market_state_profile_resolver_design_v0_1 (TERMINADO)
->
13. market_state_universe_resolver_design_v0_1 (TERMINADO)
->
14. market_state_source_resolver_design_v0_1 (TERMINADO)
->
15. market_state_partition_and_coverage_resolver_design_v0_1 (TERMINADO)
->
16. market_state_materializer_design_v0_1 (TERMINADO)
->
17. market_state_validator_design_v0_1 (TERMINADO)
->
18. market_state_candidate_dataset_registry_design_v0_1 (TERMINADO)
->
19. market_state_run_lifecycle_and_manifest_design_v0_1 (TERMINADO)
->
20. market_state_on_demand_execution_chain_joint_review_v0_1 (TERMINADO)
->
21. market_state_bounded_on_demand_execution_authorization_v0_1 (TERMINADO)
->
22. market_state_bounded_on_demand_execution_v0_1 (TERMINADO)
->
23. market_state_bounded_on_demand_candidate_dataset_review_v0_1 (TERMINADO)
->
24. market_state_bounded_on_demand_deterministic_rerun_authorization_v0_1 (TERMINADO)
->
25. market_state_bounded_on_demand_deterministic_rerun_v0_1 (TERMINADO)
->
26. market_state_bounded_on_demand_determinism_validation_v0_1 (TERMINADO)
->
27. market_state_bounded_on_demand_idempotency_reuse_test_authorization_v0_1 (TERMINADO)
->
28. market_state_bounded_on_demand_idempotency_reuse_test_v0_1 (TERMINADO)
->
29. market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1 (TERMINADO)
->
30. market_state_on_demand_incremental_overlap_execution_authorization_v0_1 (SIGUIENTE, NO ABIERTO)
->
31. market_state_on_demand_incremental_overlap_execution_v0_1
->
32. market_state_on_demand_scale_validation_v0_1
->
33. market_state_on_demand_capability_promotion_v0_1
`

No necesariamente cada punto necesita un documento enorme.

Algunos pueden agruparse en un único gate si el alcance queda bien controlado.

Resultado:

```text
Market State under request
=
operational and governed
```

---

## Tramo Event State on-demand

```text
22. event_state_on_demand_capability_design_authorization_v0_1
↓
23. event_state_request_contract_design_v0_1
↓
24. event_state_dependency_resolution_design_v0_1
↓
25. event_state_materializer_design_v0_1
↓
26. event_state_validator_design_v0_1
↓
27. event_state_on_demand_joint_review_v0_1
↓
28. event_state_on_demand_bounded_execution_v0_1
↓
29. event_state_on_demand_scale_validation_v0_1
↓
30. event_state_on_demand_idempotency_validation_v0_1
↓
31. event_state_on_demand_capability_promotion_v0_1
```

Resultado:

```text
Event State under request
=
operational for accepted Event Types
```

---

## Infraestructura común

```text
28. common_request_resolver_v0_1
↓
29. common_dataset_registry_v0_1
↓
30. common_run_lifecycle_v0_1
↓
31. common_cache_and_idempotency_v0_1
↓
32. common_partition_and_restart_v0_1
```

Parte de esta infraestructura habrá nacido durante Market State.

En esta fase se generaliza y elimina duplicación.

---

## Interfaces

```text
33. TSIS CLI v0.1
↓
34. TSIS Python API v0.1
↓
35. notebook client examples
↓
36. end-to-end acceptance suite
```

---

# Qué significa “promover capacidades”

Una capacidad se promueve cuando puede demostrar:

```text
valid request
↓
resolved plan
↓
authorized sources
↓
deterministic build
↓
validated result
↓
registered output
```

y también:

```text
invalid or ambiguous request
↓
blocked before unsafe execution
```

Una tabla individual no demuestra eso.

Puede ser correcta por casualidad o por ejecución manual.

La capacidad promovida demuestra que puede producirla de nuevo.

---

# Cuándo aparecen las tablas oficiales

Después de promover la capacidad, una solicitud puede indicar:

```text
output_mode =
official_candidate
```

El resultado pasa por:

```text
materialization
↓
validation
↓
dataset review
↓
promotion decision
```

Entonces:

```text
official table
=
validated output
of a promoted generation capability
```

No:

```text
official table
=
file manually selected and renamed
```

# Formulación final

Tu frase debería convertirse en el principio rector de esta fase:

```text
TSIS no promoverá primero tablas físicas aisladas.

TSIS promoverá capacidades reproducibles
de resolución, generación, validación y registro.

Las tablas oficiales serán resultados gobernados
de esas capacidades promovidas.
```

Y la ruta actual queda:

```text
Event State bounded proof
↓
Market State on-demand capability
↓
Market State operational validation
↓
Event State on-demand capability
↓
Common request and registry infrastructure
↓
CLI / API
↓
official datasets generated on demand
```

Ese es el roadmap que seguiría.





# oooooooooooooooooooooooooo




Sí. La dirección es correcta, pero haría un ajuste importante: **antes de diseñar resolvers separados, congelaría primero el contrato de solicitud y el contrato del plan de ejecución**. Así evitáis que cada resolver invente su propia semántica.

La secuencia que seguiría es esta:

```text
1. Market State Request Contract
↓
2. Market State Execution Plan Contract
↓
3. Profile Resolver Design
↓
4. Universe Resolver Design
↓
5. Source Resolver Design
↓
6. Partition / Coverage Resolver Design
↓
7. Materializer Design
↓
8. Validator Design
↓
9. Candidate Dataset Registry Design
↓
10. Joint Design Review
↓
11. Bounded On-Demand Execution Authorization
↓
12. Bounded On-Demand Execution
```

# 1. Siguiente gate inmediato

```text
market_state_request_contract_design_v0_1
```

Correcto.

Este gate debe responder exclusivamente:

```text
¿Qué ha solicitado el usuario o consumidor?
```

No:

```text
¿Cómo lo vamos a construir?
```

No:

```text
¿Qué archivos vamos a leer?
```

No:

```text
¿Dónde vamos a escribir?
```

Eso pertenece al futuro `Execution Plan`.

## Campos que debe contener la solicitud

Separaría los campos en cinco bloques.

### Identidad de la solicitud

```text
request_id
request_type
request_contract_version
requested_at_utc
requested_by
```

### Representación solicitada

```text
profile_id
profile_version_policy
resolution
grain
```

`profile_version_policy` debería permitir algo parecido a:

```text
exact
latest_accepted
latest_compatible
```

Para v0.1 probablemente solo autorizaría:

```text
exact
```

Así se evita que la misma solicitud cambie de significado en el futuro.

### Scope científico

```text
universe_definition_id
instrument_ids
start_date
end_date
session_dates
calendar_id
exchange_scope
```

Aquí debe existir una regla clara:

```text
universe_definition_id
```

o:

```text
explicit instrument_ids
```

pero no ambos, salvo que uno se utilice explícitamente como filtro del otro.

### Política temporal y de fuentes

```text
point_in_time_policy_id
source_version_policy
calendar_authority_id
as_of_policy_id
```

La solicitud no debería nombrar paths físicos.

Puede decir:

```text
source_version_policy = exact_governed
```

pero el Source Resolver decide qué artefactos cumplen esa política.

### Resultado solicitado

```text
output_mode
output_format
partition_policy
validation_level
reuse_policy
```

Por ejemplo:

```text
output_mode =
candidate
```

```text
reuse_policy =
reuse_if_exact_validated_match
```

# 2. El `request_fingerprint`

Es uno de los elementos más importantes.

Debe representar el significado completo de la solicitud, no detalles de ejecución.

Conceptualmente:

```text
request_fingerprint =
hash(
    normalized_request_contract
)
```

Debe incluir:

```text
request_type
profile_id
exact profile version
universe definition or instruments
date/session scope
resolution
calendar authority
point-in-time policy
source version policy
output mode
validation level
```

No debería incluir:

```text
requested_at_utc
run_id
output path
machine
temporary folder
```

Porque dos solicitudes semánticamente idénticas deben producir el mismo fingerprint aunque se realicen en días distintos.

## Regla

```text
same normalized request
=
same request_fingerprint
```

Pero:

```text
same request_fingerprint
```

no garantiza todavía:

```text
same dataset
```

Eso dependerá posteriormente de las fuentes y versiones resueltas.

Por eso necesitáis también:

```text
execution_plan_fingerprint
```

# 3. Diseñaría inmediatamente después el Execution Plan Contract

Yo movería:

```text
market_state_execution_plan_contract_v0_1
```

antes de los resolvers.

Porque el Request Contract representa:

```text
qué se pide
```

y el Execution Plan representa:

```text
cómo se ha resuelto
```

La relación será:

```text
Request
↓
Resolvers
↓
Execution Plan
```

Pero debéis definir previamente qué forma debe tener el resultado de los resolvers.

## Execution Plan mínimo

```text
execution_plan_id
request_id
request_fingerprint
resolved_profile_id
resolved_profile_version
resolved_universe
resolved_sessions
resolved_instruments
resolved_sources
resolved_source_versions
resolved_partitions
resolved_calendar
builder_version
validator_versions
expected_output_schema
expected_output_partitions
quantitative_limits
estimated_work
execution_plan_fingerprint
```

El plan debe ser completamente explícito.

Nada debería resolverse de nuevo durante el materializado.

```text
Materializer
=
consume plan
```

No:

```text
Materializer
=
vuelve a buscar fuentes
y decide qué construir
```

# 4. Profile Resolver

Después:

```text
market_state_profile_resolver_design_v0_1
```

Debe resolver:

```text
profile_id
+
version policy
```

en:

```text
exact profile contract
exact schema
required Information Objects
required variables
required source aliases
required builders
quality rules
```

Debe bloquear si:

```text
profile does not exist
profile is not authorized
version is ambiguous
required contract is missing
profile status is incompatible with output_mode
```

# 5. Añadiría un Universe Resolver explícito

En tu lista no aparece, pero es necesario:

```text
market_state_universe_resolver_design_v0_1
```

Porque el universo point-in-time es una de las partes más delicadas del backtest.

Debe resolver:

```text
universe_definition
+
date/session scope
```

en:

```text
instrument-session membership
```

Y debe preservar:

```text
symbol history
listing lifecycle
exchange membership
delistings
corporate identity
point-in-time eligibility
```

No debe confundirse con Source Resolver.

```text
Universe Resolver
=
qué instrumentos pertenecen al scope
```

```text
Source Resolver
=
qué datasets y vistas construyen las variables
```

# 6. Source Resolver

```text
market_state_source_resolver_design_v0_1
```

Debe consumir:

```text
profile requirements
+
resolved scope
+
source version policy
```

y producir:

```text
exact dataset contracts
exact view contracts
exact physical paths or dataset IDs
exact versions
exact fingerprints
coverage assessment
```

Debe bloquear ante:

```text
missing source
ambiguous version
coverage gap
unauthorized physical source
schema incompatibility
```

No debería hacer fallback silencioso.

Por ejemplo:

```text
quote_guarded_1m unavailable
```

no puede transformarse automáticamente en:

```text
raw ohlcv_1m
```

sin una política explícita del perfil.

# 7. Partition / Coverage Resolver

También lo haría explícito:

```text
market_state_partition_and_coverage_resolver_design_v0_1
```

Porque una fuente puede existir, pero no cubrir:

```text
todo el rango
todos los instrumentos
todas las sesiones
```

Debe producir:

```text
requested partitions
available partitions
missing partitions
blocked partitions
already materialized partitions
```

Este componente será fundamental para:

```text
incremental builds
restartability
cache reuse
```

# 8. Materializer

Solo entonces:

```text
market_state_materializer_design_v0_1
```

El materializer no interpreta la solicitud original.

Consume exclusivamente:

```text
frozen execution plan
```

Su responsabilidad:

```text
read authorized inputs
apply authorized builders
construct canonical records
write candidate partitions
emit lineage
```

No debe:

```text
select profile
choose sources
change universe
invent fallbacks
promote datasets
```

# 9. Validator

Debe existir como componente independiente:

```text
market_state_validator_design_v0_1
```

Validaciones mínimas:

```text
schema
grain
identity uniqueness
temporal cutoff
point-in-time legality
required fields
source lineage
content fingerprints
partition completeness
request reconciliation
determinism
```

Regla de reconciliación:

```text
requested contexts
=
emitted
+
blocked
+
quarantined
```

# 10. Dataset Registry

Yo lo incluiría antes de la primera ejecución bounded, aunque sea una versión mínima:

```text
market_state_candidate_dataset_registry_design_v0_1
```

Porque la primera ejecución on-demand ya debería registrar:

```text
request fingerprint
execution plan fingerprint
dataset fingerprint
coverage
files
hashes
validation status
```

De lo contrario, ejecutaréis primero y diseñaréis después cómo reconocer el resultado.

## Estados iniciales

```text
planned
running
candidate
validated_candidate
blocked
failed
quarantined
```

Todavía no hace falta:

```text
official
production
downstream_enabled
```

# 11. Joint Review

Antes de autorizar ejecución:

```text
market_state_on_demand_execution_chain_joint_review_v0_1
```

Debe verificar la coherencia completa:

```text
Request Contract
↓
Profile Resolver
↓
Universe Resolver
↓
Source Resolver
↓
Coverage Resolver
↓
Execution Plan
↓
Materializer
↓
Validator
↓
Dataset Registry
```

# 12. Primera bounded execution

Después:

```text
market_state_bounded_on_demand_execution_authorization_v0_1
```

La primera solicitud debería reutilizar, en la medida de lo posible, el scope Scale C ya conocido, pero no copiar el parquet anterior.

El objetivo sería demostrar:

```text
request
↓
resolution
↓
plan
↓
fresh materialization
↓
validation
↓
registry
```

Luego repetir exactamente la misma solicitud para probar:

```text
idempotency
```

Y una solicitud parcialmente solapada para probar:

```text
incrementality
```

# Ruta inmediata que recomiendo

```text
1. market_state_request_contract_design_v0_1
↓
2. market_state_execution_plan_contract_design_v0_1
↓
3. market_state_profile_resolver_design_v0_1
↓
4. market_state_universe_resolver_design_v0_1
↓
5. market_state_source_resolver_design_v0_1
↓
6. market_state_partition_and_coverage_resolver_design_v0_1
↓
7. market_state_materializer_design_v0_1
↓
8. market_state_validator_design_v0_1
↓
9. market_state_candidate_dataset_registry_design_v0_1
↓
10. market_state_on_demand_execution_chain_joint_review_v0_1
↓
11. market_state_bounded_on_demand_execution_authorization_v0_1
↓
12. bounded execution
↓
13. deterministic rerun
↓
14. overlapping incremental request
```

# Qué haría ahora mismo

Abriría:

```text
market_state_request_contract_design_v0_1
```

con estas fronteras:

```text
request records created = 0
resolvers executed = 0
sources read = 0
execution plans created = 0
Market State records emitted = 0
datasets written = 0
registry writes = 0
production = false
downstream = false
```

Y con un output principal:

```text
market_state_request_contract_v0_1.json
```

acompañado por:

```text
authorization
scope
design document
readout
```

La frase rectora de este gate debería ser:

```text
A Market State Request declares
what representation is required.

It does not decide
how that representation will be built.
```

Eso preservará la separación entre:

```text
intent
```

y:

```text
execution
```

que será la base de toda la capacidad on-demand.
