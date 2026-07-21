# Order Flow Pressure - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Order Flow Pressure`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `bid_hit_ask_lift_model` | Clasificacion de trades contra bid/ask. | `trades__bid_hit_ask_lift_WINDOW` | Trades + Quotes; `015`/future `021` | `candidate` |
Requiere alignment y condition decoding. |
| `signed_flow_model` | Volumen firmado por lado. | `trades__signed_flow_WINDOW` | Trades + Quotes; `015` | `candidate` | Error de clasificacion puede contaminar todo el modelo. |
| `aggressor_imbalance_model` | Desequilibrio entre agresion compradora/vendedora. | `trades__aggressor_imbalance_WINDOW` | Trades + Quotes; `015` | `candidate` | Sensible a classifier confidence. |
| `ofi_l1_model` | Desequilibrio de ordenes L1. | `trade_quote__ofi_l1_WINDOW` | Trades + Quotes L1 | `candidate` | L1 limitation y ordering policy. |
| `alignment_confidence_model` | Confianza del matching trade-quote. | `trade_quote__alignment_confidence`, `alignment_lag_ms` | future `021`; `015` support | `candidate` | Sin esto no debe entrar a State. |

## Modelos Que
Requieren Separacion

```text
Trading Activity: trade count y volume miden intensidad, no presion direccional.
```

```text
Liquidity: spread/depth miden coste/disponibilidad, no agresion.
```

```text
Execution: fill outcome y slippage realizado son resultados, no pressure observable neutral.
```

## Modelos Bloqueados O No Listos

```text
all_core_directional_models: blocked_reason:  requieren trade-quote alignment, side classifier,  timestamp policy y confidence governance.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
El Objeto es cientificamente coherente, pero debe aceptarse con restricciones fuertes porque su implementacion no esta lista para consumo de State.
```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
```
