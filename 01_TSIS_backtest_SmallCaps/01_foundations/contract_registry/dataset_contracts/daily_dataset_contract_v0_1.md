# Daily Dataset Contract v0.1 - Modulo 01

## 1. dataset_identity

Companions explicativos:

- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/daily_acceptance_policy_explained.md`
- `01_foundations/module_contracts/daily_rules_explained_line_by_line.md`

- `name`: `daily_core_v0_1`
- `domain`: `daily`
- `logical_version`: `v0_1`
- `contract_type`: `dataset_contract`
- `supersedes`: none

## 2. status

- `promotion_state`: `institutional`
- `contract_version`: `v0_1`
- `owner`: `01_TSIS_backtest_SmallCaps`
- `active`: `true`

## 3. purpose

Este dataset existe para proporcionar la capa canonica de barras `daily` consumibles por el modulo 01.

Su papel institucional es:

- servir como base historica diaria para backtesting defendible;
- soportar universe studies y research historico de baja frecuencia;
- alimentar pipelines downstream permitidos con politica explicita;
- y materializar una lectura estable de la auditoria y certificacion ya cerradas para `daily`.

No pretende cubrir:

- semantica microestructural intradia;
- simulacion de ejecucion de alta fidelidad;
- ni consumo RL por defecto.

## 4. semantic_scope

`daily` representa barras historicas por `ticker-day`.

Unidad semantica principal:

- una barra diaria historica para un instrumento y una fecha de sesion.

Representa, como minimo:

- `open`
- `high`
- `low`
- `close`
- `volume`

Y, cuando aplique:

- `vw`
- `n`

La interpretacion institucional de este dataset es:

- dataset ampliamente sano;
- residuo dominante de `vw` mayoritariamente explicable por borde de regla e iliquidez extrema;
- tail duro pequeno y bien aislado de parse/precio invalido;
- cobertura alta con una franja acotada de recuperacion con o sin flag.

La verdad principal del dataset no descansa en `vw`.

En `daily`, la autoridad primaria del dataset esta en:

- parse;
- fechas;
- `open/high/low/close`;
- `volume`;
- y coverage.

`vw` o `vwap` debe leerse como capa secundaria:

- util para flags;
- util para diagnostico fino;
- util para abrir inspeccion;
- pero no como fundamento unico de invalidez global del bloque.

## 5. source_lineage

Este contrato se apoya en evidencia preservada, no la sustituye.

Referencias principales:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/00_daily_current_state.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/01_daily_recovery_and_coverage.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/02_daily_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/03_daily_closeout.md`
- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`

La semantica institucional encapsulada aqui nace de esa auditoria y certificacion.

## 6. schema

Schema logico canonico:

- ver `01_foundations/canonical_schemas/daily/daily_schema_contract.md`

Claves logicas:

- `ticker`
- `session_date`

Campos criticos:

- `open`
- `high`
- `low`
- `close`
- `volume`

Campos condicionales relevantes:

- `vw`
- `n`

Estos campos no desplazan la autoridad primaria del schema `OHLCV`.

## 6b. price_semantics

`daily` no debe interpretarse como automaticamente equivalente a charts externos.

El uso correcto de esta capa exige distinguir:

- `daily_raw`
- `adjusted`
- `adjusted_proxy`

La politica transversal y la arquitectura de vistas de precio viven en:

- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/pipeline_price_view_policy.md`

## 7. coverage

Estado resumido de coverage segun el closeout actual:

- universo auditado `<1B>` sobre `44,423` `ticker-year files`
- `102` `ticker-year` excluidos como `bad`
- `653` tickers sin `complete_daily`
- `374` recuperables sin penalizacion
- `222` recuperables con flag
- `57` abiertos como frontera de coverage

Lectura operativa:

- la mayor parte del dataset es consumible;
- el exclusion tail duro es pequeno;
- la mayor parte del faltante de coverage no debe interpretarse como fallo duro.

## 8. quality_policy

Taxonomia del eje de calidad para `daily`:

- `good`
- `recoverable_with_flag`
- `bad`

La definicion literal de buckets, thresholds y regla de corte vive en:

- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`

Mapeo actual:

- `good`
  - `schema_only_or_other`
  - `vw_edge_absmax_only`
- `recoverable_with_flag`
  - `vw_low_ratio_limited_days`
  - `vw_mid_ratio_illiquid_regime`
  - `vw_high_ratio_illiquid_regime`
  - `vw_warn_minor_or_material`
- `bad`
  - `hard_invalid_parse_or_price`

Regla de traduccion historico -> contractual:

- `review` historico de `daily`
  - debe leerse contractualmente como `recoverable_with_flag`
  - salvo que una policy posterior cree una categoria mas fina y versione este contrato

Eso implica que, en el estado actual del modulo:

- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `vw_warn_minor_or_material`

pertenecen todos a la misma franja contractual:

- `recoverable_with_flag`

Taxonomia de coverage relevante:

- `recoverable_without_penalty`
  - `LIKELY_VALID_GAP_ONLY`
- `recoverable_with_flag`
  - `AMBIGUOUS_REVIEW`
- `review_not_rehabilitated`
  - `REALLY_PROBLEMATIC_UNEXPECTED`

La decision operativa final del dataset no sale solo de este eje.

Sale de combinar:

- eje de calidad
- eje de coverage

Por eso la semantica final completa del bloque es:

- `good`
- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

## 9. allowed_consumers

Consumidores permitidos por defecto para el dataset institucional `daily`:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`
- `forensic_only`

Consumidores restringidos o no implicados automaticamente:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

La habilitacion concreta depende de:

- `01_foundations/data_consumption_policies/daily_consumption_policy.md`

## 10. validators

Artefactos de validacion requeridos:

- `01_foundations/validators/daily/daily_validators.md`
- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`
- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`

Checks minimos exigidos:

- parse estructural del bar;
- integridad minima OHLCV;
- consistencia de rango;
- clasificacion de `vw` por severidad y regimen;
- materializacion del exclusion set duro;
- clasificacion de coverage segun politica vigente.

## 11. known_limitations

Limitaciones conocidas:

- el campo `vw` no debe interpretarse de forma ingenua en contextos de iliquidez extrema;
- `vw` no debe sobredominar la lectura de salud del dataset;
- existe una franja `recoverable_with_flag` que no equivale a `good`;
- existe una frontera de coverage abierta que no debe colapsarse en binario `ok/fallo`;
- este contrato no define semantica de ejecucion ni de microestructura intradia.
- comparaciones visuales con plataformas externas pueden divergir si la serie externa esta ajustada por dividendos, splits o remaps y la serie interna se esta leyendo en modo `raw`.

Para ese tipo de contraste debe seguirse:

- `01_foundations/module_contracts/external_price_comparison_caveats.md`

Cuando un caso `daily` quede clasificado como `bad`, su tratamiento institucional debe seguir ademas el protocolo definido en:

- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`

Eso implica:

- evidencia trazable;
- explicacion logica del fallo;
- inspeccion revisable cuando sea viable;
- y evaluacion explicita de si existe rehabilitacion defendible sin dano para backtest o ML.

### Regla especifica para barras con campos criticos en cero o contradiccion interna

La presencia en `daily` de filas con:

- `o = h = l = c = 0`
- uno o varios campos criticos en cero como `open = 0`, `low = 0` o `close = 0`
- `high < low`
- o contradicciones internas como `vw > high` mientras `high = 0`

no debe interpretarse automaticamente como comportamiento real de mercado.

Estas filas deben tratarse inicialmente como no aptas para `backtest_core` salvo que exista evidencia adicional suficiente para demostrar que:

- representan una sesion real interpretable;
- su semantica esta clara;
- y su inclusion no contamina retornos, filtros, features o targets.

Mientras esa defendibilidad no exista:

- deben quedar fuera del consumo principal;
- pueden preservarse para `forensic_only`;
- y pueden reabrirse como candidatas a rehabilitacion si otra evidencia permite reconstruir o reinterpretar su semantica.

## 12. change_policy

Requieren nueva version logica del contrato:

- cambio de taxonomia de calidad;
- cambio de consumers permitidos;
- cambio de schema canonico material;
- cambio de interpretacion de coverage;
- cambio de exclusion tail duro.

Son compatibles sin nueva version logica mayor:

- clarificaciones no semanticas;
- evidencia adicional que no altere el veredicto operativo;
- refuerzo de validators manteniendo la misma semantica.

## 13. conclusion operacional

`daily_core_v0_1` es el primer dataset institucional del modulo 01 porque ya cumple la combinacion minima de:

- evidencia trazable;
- interpretacion cerrada;
- schema logico;
- policy de consumo;
- validators base;
- y registry entry asociada.
