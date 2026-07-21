# Broad Market Context - Candidate Object Definition v0.1  Status: `candidate_object_definition_v0_1` Date: `2026-07-20` Scope: `post_landscape_pre_formal_admission`  Este documento define el Objeto candidato de contexto despues de Domain Definition y Representation Landscape. No constituye admision formal.  No disena tablas. No promociona datasets. No modifica schemas, builders, validators ni contratos. No autoriza variables concretas para `Market State` o `Event State`.  ## 1. Identificacion  ```text Name: Broad Market Context Source Domain: Market / Economic Context Temporal Resolution: as_of, daily, intraday_bar, event_window Institutional Role: observable_context, state_extension_candidate, research_input_candidate ```  ## 2. Definicion  ```text Objeto que preserva el entorno general de mercado observable as-of que condiciona la interpretacion del instrumento. ```  ## 3. Hipotesis Cientifica  ```text El comportamiento de small caps puede depender del contexto general: index return, rango, risk-on/off proxy y regimen de mercado disponible en t. ```  ## 4. Capacidades Candidatas  Core candidatas:  ```text regime__intraday_return, regime__close_to_previous_close_return, regime__high_to_open_return, regime__low_to_open_return, regime__intraday_range_pct ```  Extension o infraestructura relacionada:  ```text regime__bar_coverage_state, risk_on_off_state candidate, volatility proxy candidate, macro/economic context candidates ```  ## 5. Restricciones  ```text as_of obligatorio; no confundir Market Regime con objeto separado sin prueba; proxies de indice no son verdad macro; coverage state es calidad/contexto, no alpha. ```  ## 6. Decision  ```text decision = candidate_defined_pending_formal_admission ```  ## 7. Estado De Promocion  ```text information_object_status = candidate_defined formal_admission_required = true
operational_mapping_required = true state_consumption_authorized = false physical_variables_authorized = false schema_change_authorized = false builder_change_authorized = false ```  ## 8. Siguiente Paso  ```text Continuar con batch review y operational mappings una vez cerrados los dominios core. ```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\012_regime_context_table\table_representation_audit_ES.md
```



## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```

