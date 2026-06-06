# Quotes Dataset Contract v0.1 - Modulo 01

## 1. dataset_identity

- `name`: `quotes_core_v0_1`
- `domain`: `quotes`
- `logical_version`: `v0_1`
- `contract_type`: `dataset_contract`
- `supersedes`: none

## 2. status

- `promotion_state`: `institutional`
- `contract_version`: `v0_1`
- `owner`: `01_TSIS_backtest_SmallCaps`
- `active`: `true`

## 3. purpose

Este dataset existe para proporcionar la capa canonica de `quotes` consumibles por el modulo 01.

Su papel institucional es:

- servir como verdad primaria del estado observado del libro `bid/ask`;
- soportar research microestructural defendible sobre la sesion extendida;
- alimentar pipelines downstream permitidos con policy explicita;
- y materializar una lectura estable de la auditoria y certificacion ya cerradas para `quotes`.

No pretende cubrir por si solo:

- identidad canónica final del emisor;
- causalidad final del episodio de mercado;
- semantica formal de halt;
- ni reconciliacion corporativa completa.

Para esas capas mandan ademas:

- `halts`
- `reference`
- `additional`
- `news`
- `ipos`
- y el `crosswalk` multidataset

## 4. semantic_scope

`quotes` representa snapshots o observaciones del libro historico por `ticker-session`.

Unidad semantica principal:

- una observacion del libro `bid/ask` para un instrumento y un instante temporal concreto.

Representa, como minimo:

- `bid`
- `ask`
- `timestamp`

Y, cuando aplique:

- `bid_size`
- `ask_size`
- `exchange` o venue
- `conditions`
- `session_date`

La interpretacion institucional de este dataset es:

- dataset localmente fuerte para describir el libro observado;
- con una franja buena amplia;
- una franja `review` donde el contexto externo puede explicar pero no rehabilita automaticamente;
- y una cola `bad` asociada a crossed economicamente demasiado agresivos o a degradacion local no defendible del libro.

La verdad principal del dataset descansa en:

- integridad local de `bid/ask`;
- severidad economica del crossed cuando `ask > 0`;
- consistencia temporal y de sesion;
- y coherencia minima del libro observado.

El contexto externo debe leerse como capa explicativa adicional.

No debe desplazar la autoridad local del libro.

## 5. source_lineage

Este contrato se apoya en evidencia preservada, no la sustituye.

Referencias principales:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/05_crosswalk_multidataset.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v1/00_auditoria_quotes.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v1/01_contrato_agent02_agent03_03312026.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v1/02_diseno_arquitectura_quotes_CD.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_methodology.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/03_quotes_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/04_quotes_usage_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/12_quotes_open_buckets_synthesis.md`
- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`

La semantica institucional encapsulada aqui nace de esa auditoria y certificacion.

## 6. schema

Schema logico canonico:

- ver `01_foundations/canonical_schemas/quotes/quotes_schema_contract.md`

Claves logicas minimas:

- `ticker`
- `quote_timestamp`

Campos criticos:

- `bid`
- `ask`

Campos condicionales relevantes:

- `bid_size`
- `ask_size`
- `session_date`
- `exchange`
- `conditions`

## 7. session_scope

`quotes` queda gobernado por:

- `01_foundations/module_contracts/market_session_scope.md`

Por tanto, la sesion institucional objetivo es:

- `04:00-20:00 America/New_York`

Premarket y afterhours forman parte del alcance esperado del bloque.

## 7b. price_semantics

`quotes` puede vivir en una escala distinta a `daily_raw` o a una plataforma externa `adjusted`.

Eso no debe interpretarse automaticamente como error del libro.

La politica transversal de:

- `quotes_raw`
- `split_normalized`
- `daily_raw`
- `adjusted`
- `adjusted_proxy`

vive en:

- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/pipeline_price_view_policy.md`

## 8. quality_policy

Taxonomia de calidad final para `quotes`:

- `good`
- `review`
- `bad`

La definicion literal de familias y politica de corte vive en:

- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`

Lectura contractual vigente:

- `good`
  - familias limpias o de residuo leve no material
- `review`
  - familias mixtas, contextualizables o abiertas, pero no suficientemente limpias
- `bad`
  - familias donde el residuo local del libro sigue siendo economicamente demasiado agresivo

Buckets institucionalmente relevantes hoy:

- `good`
  - `clean_pass_or_other`
  - `soft_crossed_micro_noise`
  - `persistent_soft_crossed_low`
  - `utc_rollover_large_day_clean`
- `review`
  - `persistent_soft_crossed_mid_large_scale`
  - `large_file_threshold_edge_hard_many_crosses`
- `bad`
  - `medium_file_threshold_edge_hard_many_crosses`
  - `high_hard_crossed_10_to_20`

## 9. allowed_consumers

Consumidores permitidos por defecto para el dataset institucional `quotes`:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`
- `research_only`
- `forensic_only`

Consumidores restringidos o no implicados automaticamente:

- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

La habilitacion concreta depende de:

- `01_foundations/data_consumption_policies/quotes_consumption_policy.md`

## 10. validators

Artefactos de validacion requeridos:

- `01_foundations/validators/quotes/quotes_validators.md`
- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- `01_foundations/module_contracts/market_session_scope.md`

Checks minimos exigidos:

- presencia y parseabilidad de columnas criticas del libro;
- coherencia minima de `bid/ask`;
- cuantificacion del crossed y su severidad economica;
- verificacion de timestamp, sesion y rollover;
- deteccion de integerization o patrones de encoding problematicos;
- separacion entre contexto explicativo externo y calidad local del libro.

## 11. known_limitations

Limitaciones conocidas:

- `quotes` no debe leerse aislado del `crosswalk` cuando se investiga causalidad del episodio;
- el contexto `halt` puede explicar un episodio pero no rehabilita automaticamente el libro;
- la presencia de crossed leve no equivale por si sola a corrupcion dura;
- la presencia de crossed economicamente material con `ask > 0` exige lectura conservadora;
- la policy `good/review/bad` se aplica a la calidad local del libro, no a la historia corporativa completa del ticker.
- comparaciones de precio con plataformas externas pueden divergir si la plataforma esta mostrando una serie ajustada o remapeada y el contraste interno usa una serie `daily` o `quotes` no ajustada.

Para ese tipo de contraste debe seguirse:

- `01_foundations/module_contracts/external_price_comparison_caveats.md`

## 12. change_policy

Requieren nueva version logica del contrato:

- cambio de taxonomia de calidad;
- cambio de consumers permitidos;
- cambio de schema canonico material;
- cambio del alcance de sesion;
- cambio de la regla que separa calidad local del libro de explicacion causal externa.

Son compatibles sin nueva version logica mayor:

- clarificaciones no semanticas;
- evidencia adicional que no altere el veredicto operativo;
- refuerzo de validators manteniendo la misma semantica.

## 13. conclusion operacional

`quotes_core_v0_1` nace como segundo gran dataset institucional del modulo 01 porque ya dispone de:

- auditoria historica cerrada;
- taxonomia local fuerte;
- policy de uso conservadora;
- separacion explicita entre libro observado y contexto externo;
- y una base suficiente para construir validators y dossiers de inspeccion sin reauditar el bloque.
