# Market Microstructure State - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Market Microstructure State` despues de Domain Definition y Representation Landscape. No constituye admision formal.

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
Name: Market Microstructure State
Information Object Family: Market Microstructure
Source Domain: Quotes, Trades, Halts boundary
Temporal Resolution: second, event_window, intraday_bar
Institutional Role: observable, quality_context_candidate, state_input_candidate
```

## 2. Definicion

```text
Objeto que preserva el estado observable del top-of-book y tape
que condiciona la interpretabilidad de observaciones intradia.
```

## 3. Modelos Candidatos Con Restricciones

| Modelo | Decision |
| --- | --- |
| `two_sided_quote_state_model` | `allowed_with_quote_quality_gates` |
| `locked_crossed_state_model` | `allowed_as_microstructure_quality_context` |
| `quote_activity_state_model` | `allowed_as_extension` |
| `quote_staleness_lifetime_model` | `pending_timestamp_sequence_policy` |
| `tape_integrity_context_model` | `quality_context_only` |
| `interruption_context_model` | `move_to_halt_context` |

## 4. Restricciones

```text
1. No autoriza variables directamente para State.

2. Requiere Operational Mapping antes de consumo.

3. No debe absorber Liquidity, Trading Activity ni Order Flow Pressure.

4. Locked/crossed y tape integrity son contexto/gate,
no alpha por defecto.

5. L2/MBO queda bloqueado por falta de fuente gobernada.
```

## 5. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
El Objeto conserva informacion distinta sobre condiciones microestructurales
observables que afectan interpretabilidad de precio, liquidez y actividad.
```

## 6. Estado De Promocion

```text
information_object_status = candidate_defined
formal_admission_required = true
operational_mapping_required = true
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
```

## 7. Siguiente Paso

```text
Continuar bucle cientifico con:

Order Flow Pressure
    -> Domain Definition
    -> Representation Landscape
    -> Object Admission
```

## 8. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\market_microstructure_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\market_microstructure_state_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
```

