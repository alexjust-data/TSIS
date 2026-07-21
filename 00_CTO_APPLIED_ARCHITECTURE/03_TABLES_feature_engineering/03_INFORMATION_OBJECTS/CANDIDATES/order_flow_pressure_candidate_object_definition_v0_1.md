# Order Flow Pressure - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Order Flow Pressure` despues de Domain Definition y Representation Landscape. No constituye admision formal.

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
Name: Order Flow Pressure
Information Object Family: Market Microstructure / Order Flow
Source Domain: Trades, Quotes
Temporal Resolution: second, event_window
Institutional Role: observable_candidate, state_extension_candidate, research_input_candidate
```

## 2. Definicion

```text
Objeto que preserva presion direccional inferida desde flujo de trades
y quotes gobernadas, incluyendo signo, agresion e imbalance.
```

## 3. Hipotesis Cientifica

```text
La direccion e imbalance del flujo observado pueden explicar
por que movimientos similares tienen distinta probabilidad de continuation,
failure, liquidity consumption o reversal.
```

## 4. Modelos Candidatos Con Restricciones

| Modelo | Decision |
| --- | --- |
| `bid_hit_ask_lift_model` | `accepted_conceptually_blocked_for_state_until_alignment` |
| `signed_flow_model` | `accepted_conceptually_blocked_for_state_until_classifier` |
| `aggressor_imbalance_model` | `accepted_conceptually_blocked_for_state_until_classifier` |
| `ofi_l1_model` | `accepted_conceptually_extension_only_until_policy` |
| `alignment_confidence_model` | `mandatory_support_model` |

## 5. Restricciones

```text
1. No autoriza variables directamente para State.

2. Requiere trade-quote alignment gobernado.

3. Requiere side classifier y confidence policy.

4. Requiere timestamp/sequence validation.

5. OFI debe declararse como L1-limited.

6. No debe absorber Trading Activity ni Liquidity.
```

## 6. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
El Objeto conserva informacion cientifica distinta:
presion direccional del flujo.
Pero su materializacion debe quedar bloqueada para State
hasta cerrar alignment, classifier y confidence.
```

## 7. Estado De Promocion

```text
information_object_status = candidate_defined
formal_admission_required = true
operational_mapping_required = true
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
```

## 8. Siguiente Paso

```text
Continuar bucle cientifico con:

News / Catalyst Context
    -> Domain Definition
    -> Representation Landscape
    -> Object Admission
```

## 9. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\order_flow_pressure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\order_flow_pressure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
```

