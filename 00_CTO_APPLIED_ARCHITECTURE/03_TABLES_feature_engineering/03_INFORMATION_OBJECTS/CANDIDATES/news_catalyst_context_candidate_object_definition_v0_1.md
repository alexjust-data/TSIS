# News / Catalyst Context - Candidate Object Definition v0.1  Status: `candidate_object_definition_v0_1` Date: `2026-07-20` Scope: `post_landscape_pre_formal_admission`  Este documento define el Objeto candidato `News / Catalyst Context` despues de Domain Definition y Representation Landscape. No constituye admision formal.  No disena tablas. No promociona datasets. No modifica schemas, builders, validators ni contratos. No autoriza variables concretas para `Market State` o `Event State`.  ## 1. Identificacion  ```text Name: News / Catalyst Context Source Domain: News Temporal Resolution: as_of, daily, event_window Institutional Role: observable_context, state_extension_candidate, research_input_candidate ```  ## 2. Definicion  ```text Objeto que preserva informacion externa publicada o disponible as-of que puede alterar la interpretacion del instrumento, evento o sesion. ```  ## 3. Hipotesis Cientifica  ```text La presencia, edad, tipo, novedad y relevancia de noticias/catalizadores puede cambiar la interpretacion del estado observable y la respuesta futura. ```  ## 4. Capacidades Candidatas  Core candidatas:  ```text news__published_utc, news__as_of_utc, news__article_count_WINDOW, news__freshness_minutes ```  Extension o bloqueadas:  ```text news__keyword_flag, news__sentiment_score, news__novelty_score ```  ## 5. Restricciones  ```text as_of obligatorio; attribution policy obligatoria; sentiment/novelty requieren modelo versionado; no usar noticias publicadas despues de t; catalyst category no es verdad sin taxonomia gobernada. ```  ## 6. Decision  ```text decision = candidate_defined_pending_formal_admission ```  ## 7. Estado De Promocion  ```text information_object_status = candidate_defined formal_admission_required = true
operational_mapping_required = true state_consumption_authorized = false physical_variables_authorized = false schema_change_authorized = false builder_change_authorized = false ```  ## 8. Siguiente Paso  ```text Continuar bucle cientifico con:  fundamental_context ```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\010_news_context_table\table_representation_audit_ES.md
```



## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```

