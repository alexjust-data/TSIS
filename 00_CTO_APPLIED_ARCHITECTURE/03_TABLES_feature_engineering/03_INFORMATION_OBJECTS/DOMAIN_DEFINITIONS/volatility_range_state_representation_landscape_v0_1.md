# Volatility / Range State - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Volatility / Range State`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Dominio

```text
Volatility / Range State
```

## Candidatos A Objeto Dentro Del Dominio 

| Candidato | Lectura cientifica | Decision pre-admision |
| --- | --- | --- |
| `Volatility / Range State` | Candidato principal. Preserva amplitud/dispersion observable. | `forward_to_object_admission` |
| `Daily Volatility Range` | Modelo/resolucion diaria. | `not_separate_object_by_default` |
| `Intraday Volatility` | Modelo/resolucion intradia. | `not_separate_object_by_default` |
| `Compression` | Estado/modelo derivado. | `representation_model_candidate` |
| `Expansion` | Estado/modelo derivado. | `representation_model_candidate` |
| `Future Volatility` | Resultado posterior. | `prohibited_as_state_input` |

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Capacidades derivables relacionadas | Fuentes / tablas | Estado | Riesgo principal |
| --- | --- | --- | --- | --- | --- |
| `daily_range_model` | Amplitud diaria cerrada. | `daily__daily_range_pct` | OHLCV Daily; `004_master_daily_table` | `existing` | No legal antes de cierre para dia actual. |
| `rolling_daily_volatility_model` | Dispersion historica de retornos diarios. | `daily__volatility_Nd` | OHLCV Daily; `004` | `requires_variant` | Debe usar solo sesiones previas/as-of. |
| `rolling_daily_range_model` | Rango historico agregado. | `daily__range_Nd` | OHLCV Daily; `004` | `requires_variant` | Definir estadistico y min_periods. |
| `intraday_range_so_far_model` | Amplitud observada hasta t. | `intraday__high_so_far`, `intraday__low_so_far`, `intraday__range_so_far_ratio` | OHLCV 1m; `014` | `formula_defined` | Solo barras cerradas <= t. |
| `closed_window_realized_volatility_model` | Dispersion de retornos dentro de ventana cerrada. | return series from closed 1m bars | OHLCV 1m; `014` | `candidate_requires_formula` | Falta formula atomica y variante W. |
| `compression_expansion_model` | Cambio relativo del rango/volatilidad contra baseline. | range/volatility baseline variants | `004`, `014` | `candidate_requires_formula` | Riesgo de crear demasiadas variantes sin valor incremental. |
| `future_range_response_model` | Amplitud posterior tras t. | future range/volatility | outcomes | `prohibited_as_feature` | Es label/outcome. |

## Modelos Que Podrian Ser Redundantes

```text
Daily range vs Rolling daily range:  No son identicos. Uno mide el dia observado cerrado; el otro mide contexto historico previo.
```

```text
Intraday range so far vs Price Location high/low proximity:  Range so far mide amplitud. HOD/LOD proximity mide posicion dentro de esa estructura.
```

## Modelos Que
Requieren Separacion

```text
Price Movement: returns, speed y acceleration no son volatilidad por si mismos.
```

```text
Price Location: distance_to_HOD/LOD no es rango; es posicion relativa.
```

```text
Outcome Response: future realized volatility/range debe quedar fuera de X.
```

## Modelos Bloqueados O No Listos

```text
closed_window_realized_volatility_model: blocked_reason:  falta capacidad atomica canonica en 05_DATA_derivable. missing_source_or_policy:  ventana, return input, estimator, min_periods.
```

```text
compression_expansion_model: blocked_reason:  falta baseline y formula version. missing_source_or_policy:  historical reference, denominator, window.
```

## Fronteras Para La Admision

```text
1. Volatility / Range sera un unico Objeto o dos?  2. Que modelo minimo entra en core?  3. Daily range final puede usarse solo after-close o historical prior?  4. Que ventanas intradia son legales?  5. Como se separa amplitud de direccion y localizacion?
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
Existe un Objeto candidato coherente. Los modelos comparten la pregunta de amplitud/dispersion observable.
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
