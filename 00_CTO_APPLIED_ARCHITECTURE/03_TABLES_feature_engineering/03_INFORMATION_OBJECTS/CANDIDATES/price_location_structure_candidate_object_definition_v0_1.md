# Price Location / Structure - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Price Location / Structure` despues de Domain Definition y Representation Landscape. No constituye admision formal.

No disena tablas.
No promociona datasets.
No modifica schemas, builders, validators ni contratos.
No autoriza variables concretas para `Market State` o `Event State`.

## Nota De Estado

```text
Este documento no admite institucionalmente el Objeto.
Solo fija una definicion candidata trazable para futura admision formal.

Domain = unidad cientifica de trabajo.
Candidate Object = posible unidad semantica dentro del dominio.
Accepted Object = decision institucional posterior, aun no ejecutada aqui.
```


## 1. Identificacion

```text
Name: Price Location / Structure
Information Object Family: Price Location / Structure
Source Domain: OHLCV Daily, OHLCV 1m
Temporal Resolution: daily, intraday_bar, event_window
Institutional Role: observable, state_input_candidate, research_input_candidate
```

## 2. Definicion

```text
Objeto que preserva la posicion contextual del precio
en t respecto a referencias estructurales legalmente conocidas.
```

## 3. Hipotesis Cientifica

```text
La posicion del precio respecto a referencias como VWAP,
HOD/LOD observado, session open y prior close modifica
la interpretacion del estado y puede condicionar continuation,
failure, reversal, expansion o decision quality.
```

## 4. Por Que Merece Existir

```text
Porque el precio absoluto y el movimiento del precio no bastan.
TSIS necesita saber si el precio esta extendido, centrado,
cerca de un extremo, sobre/bajo VWAP o recuperando/perdiendo
una referencia critica.
```

## 5. Modelos Candidatos Con Restricciones

| Modelo | Decision |
| --- | --- |
| `session_anchor_location_model` | `allowed_after_bar_close` |
| `prior_close_location_model` | `allowed_after_bar_close_with_prior_close_asof` |
| `vwap_location_model` | `allowed_after_vwap_policy` |
| `hod_lod_proximity_model` | `allowed_only_with_high_low_so_far` |
| `range_position_model` | `extension_only_until_formula_defined` |
| `pullback_retrace_location_model` | `extension_or_pattern_research_only_until_boundary_resolved` |
| `final_daily_structure_model` | `after_close_or_prior_day_only` |

## 6. Capacidades Candidatas

Core candidatas:

```text
intraday__bar_close_price
intraday__high_so_far
intraday__low_so_far
intraday__return_vs_session_open_ratio
intraday__return_vs_prior_close_ratio
intraday__vwap_distance_ratio
```

Extension candidatas:

```text
intraday__return_vs_segment_open_ratio
intraday__pullback_ratio_W
intraday__retrace_ratio_W
```

Pendientes de registrar o formular:

```text
distance_to_session_hod
distance_to_session_lod
session_range_position
anchored_vwap_distance
```

## 7. Tablas Fuente

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table
```

## 8. Restricciones

```text
1. No autoriza variables directamente para State.

2. Requiere Operational Mapping antes de consumo.

3. No puede usar HOD/LOD final del dia antes del cierre.

4. VWAP debe estar construido solo con informacion <= t.

5. Pullback/retrace no entra en core hasta resolver si es estructura o pattern.

6. Debe separarse de Price Movement y Volatility / Range State.

7. Las capacidades no registradas deben pasar por 05_DATA_derivable antes de mapping.
```

## 9. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
El Objeto conserva informacion observable y distinta:
la localizacion estructural del precio.

No queda absorbido por movimiento, volatilidad, actividad,
liquidez, outcomes ni calidad.
```

## 10. Estado De Promocion

```text
information_object_status = candidate_defined
formal_admission_required = true
operational_mapping_required = true
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
```

## 11. Siguiente Paso

```text
Continuar bucle cientifico con:

Volatility / Range State
    -> Domain Definition
    -> Representation Landscape
    -> Object Admission
```

Operational mapping queda pendiente hasta tener suficientes Objetos core admitidos.

## 12. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

