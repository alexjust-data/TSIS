# Quotes Consumption Policy - Modulo 01

## 1. Rol

Esta policy define como puede consumirse `quotes_core_v0_1` dentro del modulo 01.

No sustituye el dataset contract.

Lo operacionaliza.

Companions explicativos:

- `../module_contracts/policy_explanation_standard.md`
- `../module_contracts/quotes_acceptance_policy_explained.md`
- `../module_contracts/quotes_rules_explained_line_by_line.md`

## 2. Principio rector

`quotes` no es un bloque que deba consumirse en binario `limpio / basura`.

La policy correcta distingue:

- calidad local del libro;
- explicacion contextual del episodio;
- franja usable con cautela;
- y exclusiones duras del uso core.

La regla central de consumo es:

- el contexto externo puede explicar un episodio;
- pero no habilita automaticamente el consumo del libro como si estuviera limpio.

## 3. Mapa de consumo por estado de calidad

### good

Buckets:

- `clean_pass_or_other`
- `soft_crossed_micro_noise`
- `persistent_soft_crossed_low`
- `utc_rollover_large_day_clean`

Allowed for:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`
- `research_only`

Interpretacion:

- `quotes` bueno puede entrar en los consumidores principales permitidos del bloque;
- aun asi no autoriza por si solo simulacion de ejecucion ni live.

### review

Buckets:

- `persistent_soft_crossed_mid_large_scale`
- `large_file_threshold_edge_hard_many_crosses`

Allowed for:

- `backtest_extended`
- `ml_flagged`
- `research_only`

Condiciones:

- el consumo debe preservar la condicion de `review`;
- no debe presentarse como equivalente a `good`;
- no entra en `backtest_core` salvo policy futura mas fuerte.

### bad

Buckets:

- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

Allowed for:

- `forensic_only`

No permitido para:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`

## 4. Consumidores no implicados

Esta policy no habilita automaticamente:

- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Para esos consumidores haria falta contrato adicional.

## 4b. Price view por pipeline

La semantica transversal de vistas y su asignacion por pipeline viven en:

- `01_foundations/module_contracts/pipeline_price_view_policy.md`

Para `quotes`, la traduccion operativa base es:

- execution research y simulacion microestructural
  - `quotes_raw`
  - `trades_raw`
- forensic reconciliation
  - `quotes_raw`
  - `split_normalized`
  - `adjusted_proxy`
- signal research diario y factor research
  - no debe usar `quotes_raw` como vista principal de retorno economico multi-dia
- ML microestructural
  - `quotes_raw`
  - `trades_raw`

Regla:

- `quotes` es vista primaria del libro observado;
- no es vista primaria de retorno economico interdiario.

## 5. Regla de aplicacion

Cuando el contexto externo y la calidad local del libro entren en conflicto, debe prevalecer la interpretacion mas restrictiva del libro.

Ejemplo:

- si un caso `review` esta bien contextualizado por `halt`, no por eso entra como `good`;
- si un caso `bad` coincide con evento real, no por eso entra en `backtest_extended`.

## 6. Regla final

`quotes` es un dataset muy valioso para inspeccion microestructural y lectura del libro observado, pero su consumo institucional correcto depende de distinguir con rigor:

- `good`
- `review`
- `bad`
- y la diferencia entre explicacion causal y libro operativamente limpio.
