# TSIS Market Ontology Phase v0.1

Status: `ontology_phase_active_v0_1`
Date: `2026-07-20`
Scope: `information_object_formal_admission_governance`

Este documento activa la fase institucional de ontologia de mercado para los
Information Objects principales de TSIS.

No crea nuevos dominios.
No reabre los Object Admission Reviews.
No autoriza operational mapping adicional.
No autoriza builder development.
No autoriza schemas, datasets ni materializaciones fisicas.

## 1. Institutional Decision

```text
phase = TSIS Market Ontology Phase
phase_status = ACTIVE
phase_type = scientific_governance
engineering_phase_status = DEFERRED
production_builder_development_authorized = false
```

Decision:

```text
No se desarrolla ningun Builder de produccion para Market State
hasta que todos los Information Objects principales hayan pasado
por Formal Admission y exista una revision transversal de ontologia.
```

## 2. Rationale

El vertical de `Trading Activity` demostro que el lifecycle institucional
funciona:

```text
Discovery
    -> Candidate
        -> Object Admission Review
            -> Formal Admission
                -> Operational Mapping
                    -> Builder Validation
                        -> Market State Integration
                            -> Operational Promotion
```

Pero ese recorrido mezcla dos ritmos distintos:

```text
scientific rhythm = que existe y por que.
engineering rhythm = como se construye y ejecuta.
```

Regla:

```text
La ciencia debe congelar la ontologia antes de ampliar la ingenieria.
```

## 3. Phase A - Ontology Completion

Objetivo:

```text
Completar la Formal Admission de todos los Information Objects
principales revisados, sin avanzar a nuevos Operational Mappings
salvo correcciones del vertical piloto.
```

Cadena activa:

```text
Domain Definition
    -> Representation Landscape
        -> Candidate Object Definition
            -> Object Admission Review
                -> Formal Admission
                    -> Cross-Object Ontology Review
                        -> TSIS Market Ontology v1 freeze
```

No pertenece a Phase A:

```text
new production builders;
new Market State schemas;
new Event State schemas;
new physical materialization;
new operational datasets;
new downstream consumption authorization.
```

## 4. Phase B - Engineering Integration

Solo empieza despues de congelar `TSIS Market Ontology v1`.

Cadena posterior:

```text
TSIS Market Ontology v1
    -> Operational Mapping for all admitted Objects
        -> Builder Validation
            -> Market State Integration
                -> Event State Integration
                    -> Operational Promotion
```

Regla:

```text
Los documentos existentes de Operational Mapping, Builder Validation
y Market State Integration para Trading Activity son pilot artifacts.

No autorizan expandir Phase B objeto por objeto antes de cerrar Phase A.
```

## 5. Formal Admission Queue

| Information Object | Review status | Formal Admission status | Operational status |
| --- | --- | --- | --- |
| `Trading Activity` | `review_complete` | `accepted_with_restrictions` | `pilot_vertical_complete_but_not_operational` |
| `Price Movement` | `review_complete` | `pending` | `phase_b_deferred` |
| `Price Location / Structure` | `review_complete` | `pending` | `phase_b_deferred` |
| `Volatility / Range State` | `review_complete` | `pending` | `phase_b_deferred` |
| `Liquidity` | `review_complete` | `pending` | `phase_b_deferred` |
| `Market Microstructure State` | `review_complete` | `pending` | `phase_b_deferred` |
| `Order Flow Pressure` | `review_complete` | `pending` | `phase_b_deferred` |
| `News / Catalyst Context` | `review_complete` | `pending` | `phase_b_deferred` |
| `Fundamental Context` | `review_complete` | `pending` | `phase_b_deferred` |
| `Short-Side Context` | `review_complete` | `pending` | `phase_b_deferred` |
| `Broad Market Context` | `review_complete` | `pending` | `phase_b_deferred` |
| `Halt Context` | `review_complete` | `pending` | `phase_b_deferred` |

## 6. Cross-Object Ontology Review

Antes de congelar `TSIS Market Ontology v1`, TSIS debe revisar:

```text
1. si hay huecos informacionales;
2. si hay redundancias entre Objetos;
3. si algun dominio quedo demasiado grande;
4. si algun dominio quedo demasiado pequeno;
5. si algun modelo merece subir a Objeto;
6. si algun Objeto debe fusionarse o dividirse;
7. si shared evidence esta bien separada de shared identity;
8. si todas las minimal semantic identities son compatibles.
```

Preguntas criticas:

```text
Momentum es modelo, Objeto o subobjeto?

Relative Activity es modelo o nuevo Objeto?

Trade Size Distribution pertenece a Trading Activity
o a Market Microstructure State?

Order Flow Pressure depende de una fuente aun no gobernada?

Liquidity y Trading Activity comparten evidencia sin compartir identidad?
```

## 7. Freeze Criteria

`TSIS Market Ontology v1` solo puede congelarse cuando:

```text
1. Todos los 12 Information Objects principales tengan Formal Admission.
2. Cada decision sea accepted, accepted_with_restrictions o rejected.
3. Cada Objeto tenga semantic capability y minimal semantic identity.
4. Cada frontera critica este resuelta o marcada como restriction.
5. La revision transversal este documentada.
6. No existan dudas abiertas que cambien la identidad de otro Objeto.
7. State consumption siga false hasta Phase B.
```

## 8. Engineering Gate

```text
production_market_state_builder_authorized = false
production_event_state_builder_authorized = false
new_operational_mapping_batch_authorized = false
new_builder_validation_batch_authorized = false
market_state_schema_change_authorized = false
event_state_schema_change_authorized = false
physical_materialization_authorized = false
```

Excepcion:

```text
Se permiten correcciones documentales del vertical piloto de Trading Activity
si sirven para clarificar Phase A o evitar confusion de autoridad.
```

## 9. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\trading_activity_builder_validation_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\trading_activity_market_state_integration_v0_1.md
```
