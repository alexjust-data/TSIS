# Daily Consumption Policy - Modulo 01

## 1. Rol

Esta policy define como puede consumirse `daily_core_v0_1` dentro del modulo 01.

No sustituye el dataset contract.

Lo operacionaliza.

Companions explicativos:

- `../module_contracts/policy_explanation_standard.md`
- `../module_contracts/daily_acceptance_policy_explained.md`
- `../module_contracts/daily_rules_explained_line_by_line.md`

## 2. Principio rector

`daily` es ampliamente consumible, pero no todo su residuo debe tratarse igual.

La policy correcta distingue:

- calidad principal;
- recuperabilidad con flag;
- exclusiones duras;
- y frontier de coverage.

## 3. Mapa de consumo por estado de calidad

### good

Buckets:

- `schema_only_or_other`
- `vw_edge_absmax_only`

Allowed for:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`

### recoverable_with_flag

Buckets:

- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `vw_warn_minor_or_material`

Allowed for:

- `backtest_extended`
- `ml_flagged`
- `research_only`

Condiciones:

- el consumo debe preservar la condicion de flag;
- no debe presentarse como equivalente a `good`;
- no entra en `backtest_core` salvo policy futura mas fuerte.

Interpretacion adicional:

- la taxonomia historica de `daily` usa `review` para esta franja;
- la taxonomia contractual del modulo 01 la traduce a `recoverable_with_flag`;
- ambas deben leerse hoy como la misma clase operativa de consumo restringido con flag.

### bad

Buckets:

- `hard_invalid_parse_or_price`

Allowed for:

- `forensic_only`

No permitido para:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`

## 4. Mapa de consumo por estado de coverage

### recoverable_without_penalty

Cobertura:

- `LIKELY_VALID_GAP_ONLY`

Allowed for:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`

### recoverable_with_flag

Cobertura:

- `AMBIGUOUS_REVIEW`

Allowed for:

- `backtest_extended`
- `ml_flagged`
- `research_only`

Condicion:

- la ambiguedad de coverage debe viajar como condicion explicita.

### review_not_rehabilitated

Cobertura:

- `REALLY_PROBLEMATIC_UNEXPECTED`

Allowed for:

- `research_only`
- `forensic_only`

## 4b. Estado final de certificacion

La decision final de uso en `daily` no sale de mirar un unico bucket.

Sale de combinar:

- estado de calidad
- estado de coverage

La lectura final correcta del bloque es:

- `good`
  - calidad `good`
  - y coverage no degradada o `recoverable_without_penalty`
- `recoverable_without_penalty`
  - frontier de coverage valida sin degradar la capa principal de uso
- `recoverable_with_flag`
  - dano o ambiguedad que sigue permitiendo uso restringido con marca explicita
- `review_not_rehabilitated`
  - frontera abierta de coverage que no debe entrar en consumo principal
- `bad`
  - invalidez dura de parse o precio

Esto evita un error comun:

- confundir la triparticion visual `good / flagged / bad` con la semantica final completa del dataset.

## 5. Consumidores no implicados

Esta policy no habilita automaticamente:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Para esos consumidores haria falta contrato adicional.

## 5b. Price view por pipeline

La semantica transversal de vistas y su asignacion por pipeline viven en:

- `01_foundations/module_contracts/pipeline_price_view_policy.md`

Para `daily`, la traduccion operativa base es:

- vendor audit / forensic reconciliation
  - `daily_raw`
  - `split_normalized`
  - `adjusted_proxy`
- signal research diario y factor research
  - `adjusted`
- portfolio valuation y benchmark interno
  - `adjusted`
- ML daily / labels de retorno
  - `adjusted`

Regla:

- `daily_raw` no debe usarse por defecto como vista principal de retorno economico multi-dia cuando el pipeline requiera comparabilidad a traves de corporate actions.

## 6. Regla de aplicacion

Cuando calidad y coverage entren en conflicto, debe prevalecer la interpretacion mas restrictiva.

Ejemplo:

- si un objeto es `good` en calidad pero `recoverable_with_flag` en coverage, no debe entrar como `backtest_core` sin flag.

## 7. Regla final

`daily` es un dataset ampliamente utilizable, pero su consumo institucional correcto depende de distinguir con rigor:

- `good`
- `recoverable_with_flag`
- `bad`
- y las clases de coverage abiertas.
