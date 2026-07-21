# Halt Context - Candidate Object Definition v0.1  Status: `candidate_object_definition_v0_1` Date: `2026-07-20` Scope: `post_landscape_pre_formal_admission`  Este documento define el Objeto candidato de contexto despues de Domain Definition y Representation Landscape. No constituye admision formal.  No disena tablas. No promociona datasets. No modifica schemas, builders, validators ni contratos. No autoriza variables concretas para `Market State` o `Event State`.  ## 1. Identificacion  ```text Name: Halt Context Source Domain: Halts / SEC suspensions / Event windows Temporal Resolution: as_of, daily, intraday_bar, event_window Institutional Role: observable_context, state_extension_candidate, research_input_candidate ```  ## 2. Definicion  ```text Dominio que separa interrupciones observables de mercado, como halts, de infraestructura temporal de eventos. ```  ## 3. Hipotesis Cientifica  ```text La presencia, tipo y recencia de interrupciones alteran radicalmente la interpretacion de precio, liquidez, actividad y outcomes alrededor de eventos. ```  ## 4. Capacidades Candidatas  Core candidatas:  ```text halts__halt_type, halts__is_halted_at_t, halts__minutes_since_halt_start, halts__minutes_since_resume ```  Extension o infraestructura relacionada:  ```text halt clustering, post-resumption state, event window role, event relative time ```  ## 5. Restricciones  ```text halt/resume debe ser as_of; post-resumption puede ser research-only segun timestamp; Event Window Context es infraestructura temporal, no Objeto de Informacion comun; no confundir halt source event con Event State. ```  ## 6. Decision  ```text decision = candidate_defined_pending_formal_admission ```  ## 7. Estado De Promocion  ```text information_object_status = candidate_defined formal_admission_required = true
operational_mapping_required = true state_consumption_authorized = false physical_variables_authorized = false schema_change_authorized = false builder_change_authorized = false ```  ## 8. Siguiente Paso  ```text Continuar con batch review y operational mappings una vez cerrados los dominios core. ```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\006_halts_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\007_event_windows_table\table_representation_audit_ES.md
```



## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```

