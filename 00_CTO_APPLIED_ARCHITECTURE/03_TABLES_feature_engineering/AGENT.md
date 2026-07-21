# 03_TABLES_feature_engineering - Agent Handoff Prompt

Status: `agent_handoff_prompt_v0_1`
Date: `2026-07-21`
Scope: `tsis_market_ontology_v1_frozen_phase_b_continuation`

Este documento es el prompt local de continuidad para agentes que trabajen en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

No sustituye:

```text
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\AGENTS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\LOCAL_RULES.md
```

Si hay conflicto, manda la autoridad superior.

## 1. Prompt De Arranque Para El Agente

```text
Estas continuando despues del freeze de TSIS Market Ontology v1 dentro de:

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering

Tu objetivo no es crear mas metodologia.
Tu objetivo no es admitir nuevos Information Objects en v1.
Tu objetivo no es reabrir la ciencia congelada salvo contradiccion real.
Tu objetivo no es desarrollar builders de produccion.
Tu objetivo no es autorizar consumo operativo de State.

Tu objetivo actual es iniciar Phase B como ingenieria gobernada,
empezando por Operational Mapping de los Information Objects admitidos.

Trabaja como agente de ingenieria ontologica:

1. lee los contratos indicados abajo;
2. trata `TSIS Market Ontology v1` como dependencia frozen/locked;
3. usa las Formal Admissions y el Freeze Act como autoridad;
4. crea Operational Mapping solo para objetos admitidos;
5. conserva production builders, State consumption, schema changes,
   physical materialization y dataset promotion como false hasta gates
   explicitos de Phase B;
6. actualiza changelogs cuando el cambio sea semantico,
   estructural o de gobernanza;
7. no toques metodologia ni reabras Phase A salvo contradiccion
   estructural demostrada.
```

## 2. Lectura Obligatoria Antes De Tocar Nada

Leer en este orden:

```text
1. C:\TSIS_Data\AGENTS.md
2. C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
3. C:\TSIS_Data\PROJECT_RULES.md
4. C:\TSIS_Data\VERSIONING_STANDARDS.md
5. C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
6. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\AGENTS.md
7. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\LOCAL_RULES.md
8. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\README.md
9. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\CHANGELOG.md
10. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
11. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\CHANGELOG.md
12. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
13. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
14. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\README.md
15. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\04_TSIS_MARKET_ONTOLOGY_PHASE_v0_1.md
16. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md
17. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
18. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\README.md
```

Nota:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\LOCAL_RULES.md
```

no existe a fecha `2026-07-21`. No lo inventes. Usa las reglas superiores y
este handoff local.

## 3. Lectura Obligatoria Para Operational Mapping De Un Objeto

Para cada Information Object admitido, leer en este orden:

```text
1. DOMAIN_DEFINITIONS\<object>_domain_definition_v0_1.md
2. DOMAIN_DEFINITIONS\<object>_representation_landscape_v0_1.md
3. CANDIDATES\<object>_candidate_object_definition_v0_1.md
4. CANDIDATES\object_admission_review\<object>_v0_1.md
5. ACCEPTED_WITH_RESTRICTIONS\<object>_formal_admission_v0_1.md
6. TSIS_MARKET_ONTOLOGY_V1_REVIEW.md
7. TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
8. 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\README.md
9. 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md
```

El punto 9 es piloto de proceso y estilo, no autoridad operativa automatica.
El Freeze Act manda sobre cualquier texto pre-freeze que conserve un estado
de fase anterior.
## 4. Punto Exacto Del Proyecto

```text
ontology = TSIS Market Ontology v1
ontology_status = FROZEN
ontology_lock_status = LOCKED
phase_a_status = CLOSED
phase_b_status = OPEN
phase_b_scope = governed_engineering
production_builder_development_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
```

El vertical de `Trading Activity` ya demostro el lifecycle completo:

```text
Formal Admission
    -> Operational Mapping
        -> Builder Validation
            -> Market State Integration
```

pero queda clasificado como:

```text
pilot_vertical_artifact
proof_of_process
not_operational_authority
```

El trabajo activo ahora es Phase B:

```text
Operational Mapping
    -> Builder Validation
        -> Market State Integration
            -> Event State Integration
                -> Operational Promotion
```

La primera unidad activa de trabajo es:

```text
Operational Mapping
```

## 5. Estado Real De Admissions

Object Admission Reviews completos:

```text
broad_market_context_v0_1.md
fundamental_context_v0_1.md
halt_context_v0_1.md
liquidity_v0_1.md
market_microstructure_state_v0_1.md
news_catalyst_context_v0_1.md
order_flow_pressure_v0_1.md
price_location_structure_v0_1.md
price_movement_v0_1.md
short_side_context_v0_1.md
trading_activity_v0_1.md
volatility_range_state_v0_1.md
```

Formal Admissions ya creadas:

```text
Trading Activity = accepted_with_restrictions
Price Movement = accepted_with_restrictions
Price Location / Structure = accepted_with_restrictions
Volatility / Range State = accepted_with_restrictions
Liquidity = accepted_with_restrictions
Market Microstructure State = accepted_with_restrictions
Order Flow Pressure = accepted_with_restrictions
News / Catalyst Context = accepted_with_restrictions
Fundamental Context = accepted_with_restrictions
Short-Side Context = accepted_with_restrictions
Broad Market Context = accepted_with_restrictions
Halt Context = accepted_with_restrictions
```

Formal Admissions pendientes:

```text
none
```

`Event Window Context` queda fuera de la cola ordinaria:

```text
classification = infrastructure_context
formal_object_admission = not_applicable
state_variables_authorized = false
```

## 6. Estado De Freeze Y Siguiente Trabajo

La cola de Formal Admission ya esta completa.

La Cross-Object Ontology Review ya esta creada:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md
review_result = passes_with_restrictions
freeze_recommendation = proceed_to_freeze_artifact
```

La TSIS Market Ontology v1 ya esta congelada:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
ontology_status = FROZEN
ontology_lock_status = LOCKED
phase_a_status = CLOSED
phase_b_status = OPEN
```

El siguiente paso es Phase B:

```text
1. Operational Mapping
2. Builder Validation
3. Market State Integration
4. Event State Integration
5. Operational Promotion
```

Ningun nuevo Information Object entra en v1 salvo evidencia extraordinaria,
contradiccion estructural demostrada o decision explicita de gobierno para
abrir v1.1/v2.
## 6.1 Estado De Operational Mapping

Operational Mappings de `TSIS Market Ontology v1`:

```text
status = complete_for_v1
objects_with_governed_mapping = 12
production_builder_authorized = false
state_consumption_authorized = false
```

Inventario:

```text
Trading Activity:
    artifact = trading_activity_operational_mapping_v0_1.md
    ratification = trading_activity_operational_mapping_phase_b_ratification_v0_1.md
    status = mapping_ready_pending_builder_validation

Price Movement:
    artifact = price_movement_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Price Location / Structure:
    artifact = price_location_structure_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Volatility / Range State:
    artifact = volatility_range_state_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Liquidity:
    artifact = liquidity_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Market Microstructure State:
    artifact = market_microstructure_state_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Order Flow Pressure:
    artifact = order_flow_pressure_operational_mapping_v0_1.md
    status = mapping_documented_but_state_blocked
    unblock_requires = trade_quote_alignment + side_classifier + confidence_policy

News / Catalyst Context:
    artifact = news_catalyst_context_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Fundamental Context:
    artifact = fundamental_context_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Short-Side Context:
    artifact = short_side_context_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Broad Market Context:
    artifact = broad_market_context_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation

Halt Context:
    artifact = halt_context_operational_mapping_v0_1.md
    status = mapping_ready_pending_builder_validation
```

Builder Validation designs quedan completos para los 12 Objetos de v1.

Siguiente gate recomendado:

```text
Experimental State Builder
```

No empezar `Market State Integration` hasta revisar los hallazgos del builder
experimental y hasta que el Objeto correspondiente supere sus gates de Builder
Validation.

## 6.2 Estado De Builder Validation

Builder Validation design coverage de `TSIS Market Ontology v1`:

```text
status = complete_for_v1_design
objects_with_builder_validation_design = 12
objects_design_ready_pending_execution = 11
objects_blocked_pending_prerequisites = 1
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
```

Inventario:

```text
Trading Activity:
    artifact = 05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_v0_1.md
    ratification = 05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_phase_b_ratification_v0_1.md
    status = design_ready_pending_execution

Price Movement:
    artifact = 05_STATE_BUILDER_VALIDATION/price_movement_builder_validation_v0_1.md
    status = design_ready_pending_execution

Price Location / Structure:
    artifact = 05_STATE_BUILDER_VALIDATION/price_location_structure_builder_validation_v0_1.md
    status = design_ready_pending_execution

Volatility / Range State:
    artifact = 05_STATE_BUILDER_VALIDATION/volatility_range_state_builder_validation_v0_1.md
    status = design_ready_pending_execution

Liquidity:
    artifact = 05_STATE_BUILDER_VALIDATION/liquidity_builder_validation_v0_1.md
    status = design_ready_pending_execution

Market Microstructure State:
    artifact = 05_STATE_BUILDER_VALIDATION/market_microstructure_state_builder_validation_v0_1.md
    status = design_ready_pending_execution

Order Flow Pressure:
    artifact = 05_STATE_BUILDER_VALIDATION/order_flow_pressure_builder_validation_v0_1.md
    status = blocked_pending_state_capability_prerequisites
    unblock_requires = trade_quote_alignment_policy + side_classifier_policy + classifier_confidence_policy

News / Catalyst Context:
    artifact = 05_STATE_BUILDER_VALIDATION/news_catalyst_context_builder_validation_v0_1.md
    status = design_ready_pending_execution

Fundamental Context:
    artifact = 05_STATE_BUILDER_VALIDATION/fundamental_context_builder_validation_v0_1.md
    status = design_ready_pending_execution

Short-Side Context:
    artifact = 05_STATE_BUILDER_VALIDATION/short_side_context_builder_validation_v0_1.md
    status = design_ready_pending_execution

Broad Market Context:
    artifact = 05_STATE_BUILDER_VALIDATION/broad_market_context_builder_validation_v0_1.md
    status = design_ready_pending_execution

Halt Context:
    artifact = 05_STATE_BUILDER_VALIDATION/halt_context_builder_validation_v0_1.md
    status = design_ready_pending_execution
```

## 6.3 Siguiente Paso: Builder Experimental

El siguiente builder no es un builder de produccion. Es un builder experimental
para descubrir problemas que los documentos no revelan completamente.

Artefacto de frontera:

```text
05_STATE_BUILDER_VALIDATION/experimental_state_builder_boundary_v0_1.md
```

Objetivo del builder experimental:

```text
source availability gaps
join-key ambiguity
timestamp and cutoff ambiguity
profile resolution failures
missing lineage
quality flag propagation failures
cross-object naming conflicts
blocked capability leaks
source/schema mismatch
```

Autoridad:

```text
experimental_builder_allowed = true_as_non_production_resolution_probe
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
```

Si el builder experimental ejecuta una operacion larga, debe cumplir:

```text
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
```
## 6.4 Resultado Del Primer Builder Experimental

Primer smoke ejecutado:

```text
run_id = experimental_state_builder_probe_v0_1_20260721T091253Z
mode = contract_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
overall_status = passed_with_findings_and_expected_blocks
fail_count = 0
warn_count = 21
source_warn_count = 21
blocked_expected_count = 1
blocked_capability_leaks = 0
```

Artefactos:

```text
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_state_builder_probe_smoke_readout_v0_1.md
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/runs/experimental_state_builder_probe_v0_1_20260721T091253Z/
```

Hallazgo principal:

```text
El circuito documental de los 12 Objetos resuelve sin fallos ni leaks,
pero los source aliases activos no tienen todavia binding fisico gobernado
en la config experimental.
```

Siguiente paso recomendado:

```text
crear source binding layer experimental:
  source_alias
      -> governed candidate physical path
      -> expected grain
      -> expected keys
      -> timestamp/as_of fields
      -> minimum schema probe
      -> quality/lineage fields
```

No pasar a `Market State Integration` todavia.
No convertir el probe en builder productivo.
## 7. Estructura Esperada De Cada Operational Mapping

Ubicacion:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\<object>_operational_mapping_v0_1.md
```

El documento debe ser puente de ingenieria, no nueva ciencia.
Debe implementar la Formal Admission y el Freeze Act sin redefinir la identidad
del Objeto.

Debe contener como minimo:

```text
1. Governance Input
2. Approved Semantic Capability
3. Approved Representation Models
4. Capability To Physical Mapping
5. Source Tables And Temporal Legality
6. Operational Restrictions
7. Required Builder Validation
8. Authorized And Non-Authorized Consumers
9. Review Triggers
10. Evidence TSIS
```

El bloque de decision debe conservar:

```text
operational_mapping_phase_b_authorized = true
production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false_until_phase_b_artifacts
physical_materialization_authorized = false
dataset_promotion_authorized = false
builder_validation_required = true
market_state_integration_required = true
```

## 8. Verificaciones Obligatorias

Despues de crear cada Operational Mapping:

```text
1. Buscar autorizaciones accidentales:

   production_builder_authorized = true
   state_consumption_authorized = true
   physical_variables_authorized = true
   schema_change_authorized = true
   physical_materialization_authorized = true
   dataset_promotion_authorized = true
   operational_promotion_authorized = true

2. Confirmar que el mapping no redefine la scientific identity del Objeto.

3. Confirmar que cada variable fisica candidata tiene fuente, temporal rule,
   State profile previsto y restriction si falta una policy.

4. Ejecutar git diff --check sobre los archivos tocados.

5. Revisar git status --short solo para los archivos tocados.

6. Confirmar que no se modificaron builders, schemas, materializaciones,
   datasets productivos ni Market State Integration salvo instruccion explicita.
```
## 9. Artefactos De Cierre De Phase A

Phase A queda cerrada por estos artefactos:

```text
Formal Admissions:
    C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\

Cross-Object Ontology Review:
    C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md

Freeze Act:
    C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
```

No recrear estos documentos salvo contradiccion estructural real.

## 10. Autoridad De Phase B

El freeze autoriza iniciar Phase B como ingenieria gobernada:

```text
Operational Mapping
    -> Builder Validation
        -> Market State Integration
            -> Event State Integration
                -> Operational Promotion
```

Reglas de autoridad:

```text
operational_mapping_phase_b_authorized = true
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
schema_change_authorized = false_until_phase_b_artifacts
```

Usar el vertical de `Trading Activity` como piloto de proceso, no como
autoridad operativa automatica.

## 11. Lock De Ontologia v1

Ningun nuevo Information Object entra en `TSIS Market Ontology v1` salvo:

```text
extraordinary_evidence_of_missing_primary_informational_uncertainty
proven_structural_contradiction
phase_b_identity_loss_discovery
explicit_v1_1_or_v2_governance_decision
```

Los conceptos nuevos ordinarios van a backlog `vNext candidate`.
## 12. Regla Final

No dejar decisiones estructurales solo en conversacion.

Si una decision cambia semantica, estructura o gobierno, debe quedar en:

```text
formal admission
cross-object review
freeze artifact
changelog
```

No crear nuevas capas de proceso salvo contradiccion estructural real.
