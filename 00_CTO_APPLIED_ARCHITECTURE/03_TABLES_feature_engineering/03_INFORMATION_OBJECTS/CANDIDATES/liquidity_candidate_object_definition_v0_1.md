# Liquidity - Candidate Object Definition v0.1

Status: `candidate_object_definition_v0_1`
Date: `2026-07-20`
Scope: `post_landscape_pre_formal_admission`

Este documento define el Objeto candidato `Liquidity` despues de Domain Definition y Representation Landscape. No constituye admision formal.

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
Name: Liquidity
Information Object Family: Liquidity
Source Domain: Quotes, Trades, OHLCV
Temporal Resolution: intraday_bar, event_window, daily_context
Institutional Role: observable, state_input_candidate, execution_context_candidate
```

## 2. Definicion

```text
Objeto que preserva facilidad, coste y disponibilidad observable
para negociar un instrumento en una escala temporal declarada.
```

## 3. Hipotesis Cientifica

```text
La liquidez condiciona la interpretacion y operabilidad
de cualquier estado, senal, evento o resultado investigado.
```

## 4. Modelos Candidatos Con Restricciones

| Modelo | Decision |
| --- | --- |
| `quoted_spread_cost_model` | `allowed_with_quote_quality_gates` |
| `displayed_depth_model` | `allowed_as_L1_only` |
| `quote_availability_model` | `allowed_as_context_or_extension` |
| `tradability_proxy_model` | `proxy_only_not_liquidity_truth` |
| `effective_spread_model` | `pending_alignment_and_side_policy` |
| `price_impact_model` | `pending_formula_and_domain_boundary` |
| `realized_spread_model` | `outcome_or_research_only` |

## 5. Capacidades Candidatas

Core candidatas:

```text
quotes__spread_bps_median_WINDOW
quotes__spread_bps_p90_WINDOW
quotes__top_depth_mean_WINDOW
quotes__two_sided_rows_WINDOW
quotes__quote_count_WINDOW
```

Extension/proxy candidatas:

```text
quotes__quote_update_rate_WINDOW
quotes__locked_ratio_pct_two_sided_WINDOW
quotes__crossed_ratio_pct_two_sided_WINDOW
daily__dollar_volume
intraday__session_dollar_volume_to_time
trades__dollar_volume_WINDOW
trades__trade_count_WINDOW
trade_quote__effective_spread_bps_WINDOW
trade_quote__price_impact_proxy_WINDOW
```

Excluidas o no core:

```text
trade_quote__realized_spread_bps_WINDOW
trade_quote__ofi_l1_WINDOW
trades__signed_flow_WINDOW
trades__aggressor_imbalance_WINDOW
borrow availability without governed source
L2/MBO depth without governed source
```

## 6. Restricciones

```text
1. No autoriza variables directamente para State.

2. Requiere Operational Mapping antes de consumo.

3. L1 depth no debe presentarse como profundidad total del mercado.

4. Dollar volume/trade count son proxies de tradability, no liquidez completa.

5. Effective spread requiere alignment y side classifier gobernados.

6. Realized spread con horizonte futuro no puede ser input de State.

7. OFI/signed/aggressor pertenecen a Order Flow Pressure.

8. Quote integrity puede viajar como quality/microstructure context,
pero no debe confundirse con alpha.
```

## 7. Decision

```text
decision = candidate_defined_pending_formal_admission
```

Justificacion:

```text
Liquidity conserva informacion distinta sobre coste, facilidad
y disponibilidad de negociacion. Es necesaria para interpretar
small caps y evitar estados no operables.
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

Market Microstructure State
    -> Domain Definition
    -> Representation Landscape
    -> Object Admission
```

Operational mapping queda pendiente hasta tener suficientes Objetos core admitidos.

## 10. Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

