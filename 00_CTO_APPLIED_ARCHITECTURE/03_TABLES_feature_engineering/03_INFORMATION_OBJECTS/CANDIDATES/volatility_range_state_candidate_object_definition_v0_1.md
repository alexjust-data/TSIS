# Volatility / Range State - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Volatility / Range State` despues de Domain Definition y Representation Landscape. No constituye admision formal.

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
Name: Volatility / Range State
Information Object Family: Volatility / Range State
Source Domain: OHLCV Daily, OHLCV 1m
Temporal Resolution: daily, intraday_bar, event_window
Institutional Role: observable, state_input_candidate, research_input_candidate
```

## 2. Definicion

```text
Objeto que preserva amplitud, dispersion e incertidumbre observable
del precio en una ventana temporal declarada y legal.
```

## 3. Hipotesis Cientifica

```text
La amplitud y dispersion observadas del precio condicionan
la interpretacion de movimientos, eventos, riesgos, continuation,
failure y operabilidad.
```

## 4. Modelos Candidatos Con Restricciones

| Modelo | Decision |
| --- | --- |
| `daily_range_model` | `allowed_after_market_close_or_prior_history` |
| `rolling_daily_volatility_model` | `allowed_with_prior_only_variant` |
| `rolling_daily_range_model` | `allowed_with_prior_only_variant` |
| `intraday_range_so_far_model` | `allowed_after_bar_close` |
| `closed_window_realized_volatility_model` | `pending_formula_before_state_mapping` |
| `compression_expansion_model` | `extension_only_until_formula_defined` |
| `future_range_response_model` | `outcome_only_prohibited_as_input` |

## 5. Capacidades Candidatas

Core candidatas:

```text
daily__daily_range_pct
intraday__high_so_far
intraday__low_so_far
intraday__range_so_far_ratio
```

Extension candidatas:

```text
daily__volatility_Nd
daily__range_Nd
closed_window_realized_volatility
compression_expansion_ratio
```

Excluidas:

```text
future volatility
future range
future__mfe_H
future__mae_H
```

## 6. Restricciones

```text
1. No autoriza variables directamente para State.

2. Requiere Operational Mapping antes de consumo.

3. Daily range final no es decision-safe intradia.

4. Intraday range solo puede usar barras cerradas <= t.

5. Rolling volatility/range debe ser prior-only o ventana cerrada.

6. Debe separarse de Price Movement y Price Location.

7. Future volatility/range pertenece a outcomes.
```

## 7. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
El Objeto conserva informacion distinta sobre amplitud,
dispersion e incertidumbre observable.
No queda absorbido por direccion, localizacion, actividad,
liquidez ni outcomes.
```

## 8. Estado De Promocion

```text
information_object_status = candidate_defined
formal_admission_required = true
operational_mapping_required = true
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
```

## 9. Siguiente Paso

```text
Continuar bucle cientifico con:

Liquidity
    -> Domain Definition
    -> Representation Landscape
    -> Object Admission
```

Operational mapping queda pendiente hasta tener suficientes Objetos core admitidos.

## 10. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

