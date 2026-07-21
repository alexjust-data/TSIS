# Short-Side Context - Candidate Object Definition v0.1  Status: `candidate_object_definition_v0_1` Date: `2026-07-20` Scope: `post_landscape_pre_formal_admission`  Este documento define el Objeto candidato `Short-Side Context` despues de Domain Definition y Representation Landscape. No constituye admision formal.  No disena tablas. No promociona datasets. No modifica schemas, builders, validators ni contratos. No autoriza variables concretas para `Market State` o `Event State`.  ## 1. Identificacion  ```text Name: Short-Side Context Source Domain: Short Temporal Resolution: as_of, daily, event_window Institutional Role: observable_context, state_extension_candidate, research_input_candidate ```  ## 2. Definicion  ```text Objeto que preserva informacion observable con lag sobre presion, crowding o restricciones del lado short. ```  ## 3. Hipotesis Cientifica  ```text La actividad short, days-to-cover, restricciones y crowding pueden cambiar la interpretacion de squeezes, continuidad, fallos y riesgo de ejecucion. ```  ## 4. Capacidades Candidatas  Core candidatas:  ```text short__days_to_cover, short__short_volume_ratio ```  Extension o bloqueadas:  ```text short__short_interest_z_WINDOW, short__borrow_availability_state, short__locate_state, short__ssr_state ```  ## 5. Restricciones  ```text lag/as_of obligatorio; no fusionar con Trading Activity; borrow/locate/SSR bloqueados sin fuente gobernada; short volume no equivale a agresion intradia; no usar como outcome. ```  ## 6. Decision  ```text decision = candidate_defined_pending_formal_admission ```  ## 7. Estado De Promocion  ```text information_object_status = candidate_defined formal_admission_required = true
operational_mapping_required = true state_consumption_authorized = false physical_variables_authorized = false schema_change_authorized = false builder_change_authorized = false ```  ## 8. Siguiente Paso  ```text Continuar bucle cientifico con:  broad_market_context ```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\011_short_context_table\table_representation_audit_ES.md
```



## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```

