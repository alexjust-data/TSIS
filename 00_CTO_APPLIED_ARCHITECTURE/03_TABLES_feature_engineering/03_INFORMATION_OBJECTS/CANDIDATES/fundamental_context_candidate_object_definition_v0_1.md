# Fundamental Context - Candidate Object Definition v0.1  Status: `candidate_object_definition_v0_1` Date: `2026-07-20` Scope: `post_landscape_pre_formal_admission`  Este documento define el Objeto candidato `Fundamental Context` despues de Domain Definition y Representation Landscape. No constituye admision formal.  No disena tablas. No promociona datasets. No modifica schemas, builders, validators ni contratos. No autoriza variables concretas para `Market State` o `Event State`.  ## 1. Identificacion  ```text Name: Fundamental Context Source Domain: Fundamentals / SEC / Reference Temporal Resolution: as_of, daily, event_window Institutional Role: observable_context, state_extension_candidate, research_input_candidate ```  ## 2. Definicion  ```text Objeto que preserva contexto fundamental point-in-time sobre estructura economica, financiera o societaria del instrumento. ```  ## 3. Hipotesis Cientifica  ```text El significado de precio, liquidez, actividad y eventos cambia segun tamano, estructura de capital, disponibilidad de filings y recencia fundamental. ```  ## 4. Capacidades Candidatas  Core candidatas:  ```text fundamentals__filing_age_days, fundamentals__statement_recency_days, fundamentals__statement_value_FIELD ```  Extension o bloqueadas:  ```text fundamentals__ratio_FORMULA, reference__float_pit_state, market cap / shares candidates ```  ## 5. Restricciones  ```text PIT/as_of obligatorio; ratios requieren formula versionada; no usar revisiones posteriores; float PIT esta bloqueado si no hay fuente gobernada; no confundir contexto fundamental con outcome. ```  ## 6. Decision  ```text decision = candidate_defined_pending_formal_admission ```  ## 7. Estado De Promocion  ```text information_object_status = candidate_defined formal_admission_required = true
operational_mapping_required = true state_consumption_authorized = false physical_variables_authorized = false schema_change_authorized = false builder_change_authorized = false ```  ## 8. Siguiente Paso  ```text Continuar bucle cientifico con:  short_side_context ```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\009_fundamentals_asof_table\table_representation_audit_ES.md
```



## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```

