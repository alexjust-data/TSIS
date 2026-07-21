# Market Microstructure State - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Market Microstructure State`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `two_sided_quote_state_model` | Si existe mercado bid/ask observable. | `quotes__two_sided_rows_WINDOW` | Quotes L1; `015` | `existing` | Confundir ausencia de rows con ausencia real de mercado sin coverage. |
| `locked_crossed_state_model` | Estados locked/crossed del top-of-book. | `quotes__locked_rows_WINDOW`, `quotes__crossed_rows_WINDOW`, ratios | Quotes L1; `015` | `existing` | Puede ser quality context, no alpha. |
| `quote_activity_state_model` | Ritmo de actualizacion del book. | `quotes__quote_count_WINDOW`, `quotes__quote_update_rate_WINDOW` | Quotes L1; `015` | `requires_variant` | Puede solaparse con Activity si se interpreta como participacion. |
| `quote_staleness_lifetime_model` | Persistencia/staleness de quotes. | `quotes__staleness_WINDOW`, `quotes__lifetime_WINDOW` | Quotes L1; `015` | `requires_variant` |
Requiere timestamp/sequence policy. |
| `tape_integrity_context_model` | Condiciones del tape que afectan lectura. | duplicate/off-regular/invalid ratios | Trades; `015` | `existing_quality_context` | No convertir calidad en senal sin justificacion. |
| `interruption_context_model` | Halt/interrupcion del mercado. | `halts__is_halted_at_t` | `006` | `boundary_model` | Pertenece mejor a Halt Context. |

## Modelos Que
Requieren Separacion

```text
Liquidity: spread/depth pueden usar microestructura, pero responden coste/facilidad.
```

```text
Order Flow Pressure: signed flow, aggressor imbalance y OFI introducen direccion.
```

```text
Quality/Governance: coverage y validacion son gates, no estado microestructural economico por si solos.
```

## Modelos Bloqueados O No Listos

```text
staleness_lifetime_model: blocked_reason:  requiere confirmar timestamp/sequence behavior.
```

```text
L2/MBO_microstructure_model: blocked_reason:  no existe fuente gobernada L2/MBO.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
Existe un Objeto candidato coherente centrado en condiciones observables del top-of-book/tape, sin absorber liquidez ni order flow.
```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
```
