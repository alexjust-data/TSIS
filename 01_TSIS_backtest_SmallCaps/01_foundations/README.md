# 01 Foundations - Institutional Coverage Map

## Menu

- [Rol de esta carpeta](#rol-de-esta-carpeta)
- [Como leer los porcentajes](#como-leer-los-porcentajes)
- [Resumen ejecutivo](#resumen-ejecutivo)
- [Graphify operativo](#graphify-operativo)
- [Mapa por elemento de data](#mapa-por-elemento-de-data)
  - [Daily raw](#daily-raw)
  - [Daily adjusted](#daily-adjusted)
  - [Daily return labels](#daily-return-labels)
  - [Quotes raw](#quotes-raw)
  - [Trades raw](#trades-raw)
  - [OHLCV 1m raw](#ohlcv-1m-raw)
  - [OHLCV 1m split-normalized](#ohlcv-1m-split-normalized)
  - [Intraday regime features](#intraday-regime-features)
  - [Halts](#halts)
  - [Reference](#reference)
  - [Additional context](#additional-context)
  - [Short](#short)
  - [Short review FINRA](#short-review-finra)
  - [LT1B universe](#lt1b-universe)
  - [Financial standalone schemas](#financial-standalone-schemas)
  - [Regime indicators schemas](#regime-indicators-schemas)
- [Lectura transversal por carpeta](#lectura-transversal-por-carpeta)
- [Deuda principal para cerrar 01_foundations](#deuda-principal-para-cerrar-01foundations)
- [Regla final](#regla-final)

## Rol de esta carpeta

`01_foundations/` es la capa institucional de gobierno de datos del modulo `01_TSIS_backtest_SmallCaps`.

Su funcion no es guardar datos pesados. Su funcion es hacer que cada dataset, vista derivada, universo, label, feature o bloque contextual pueda responder:

- que es;
- que no es;
- que unidad gobierna;
- que schema lo describe;
- que contrato lo define;
- que policy de consumo lo restringe;
- que registry entry lo localiza;
- que validator o modelo de validacion lo protege;
- que dossier o evidencia explica su estado;
- que module contracts transversales o especificos lo gobiernan;
- y que tan cerca esta de considerarse terminado institucionalmente.

Este README es un mapa de estado. No sustituye los contratos, schemas, policies, registries, validators ni dossiers vivos.

Si este README contradice un artefacto vivo mas especifico, manda el artefacto vivo mas especifico.

Para Graphify, la operacion de build y refresco no se gobierna desde memoria de
conversacion. Vive en:

- [GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md](GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md)
- [GRAPHIFY_REFRESH_QUEUE.md](GRAPHIFY_REFRESH_QUEUE.md)
- [.graphifyignore](.graphifyignore)
- [module_contracts/graphify/README.md](module_contracts/graphify/README.md)
- [module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md](module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md)

## Como leer los porcentajes

El porcentaje es una lectura de completitud institucional dentro de `01_foundations`, no una garantia estadistica de calidad absoluta del dataset.

La escala usada aqui combina siete pilares:

1. `validators/`
2. `canonical_schemas/`
3. `contract_registry/dataset_contracts/`
4. `data_consumption_policies/`
5. `dataset_registry/`
6. `inspection_dossiers/`
7. `module_contracts/`

Lectura practica:

- `95-100%`: capa promovida o practicamente cerrada; hay contrato, schema, registry, evidencia fuerte, policy y trazabilidad operacional.
- `85-94%`: capa institucional fuerte; puede tener deuda editorial, validator especifico pendiente, promocion no total o frontera abierta documentada.
- `70-84%`: capa aceptada o reconciliada con restricciones; faltan piezas propias o el consumo es condicionado.
- `50-69%`: capa definida/pilotada; util para continuar, pero no cerrada para uso amplio.
- `<50%`: familia parcial, normalmente schema-only o backlog de gobierno.

Los porcentajes no deben usarse para saltarse las policies de consumo. Un dataset al `90%` puede seguir bloqueado para `rl_allowed`, `execution_simulator` o `live_downstream_candidate`.

## Resumen ejecutivo

| Elemento | Estado rapido | Completitud | Lectura de una linea |
| --- | --- | ---: | --- |
| [Daily raw](#daily-raw) | institucional | 92% | Capa diaria base bien gobernada; calidad y coverage separados. |
| [Daily adjusted](#daily-adjusted) | full-universe promoted | 100% | Vista diaria economica promovida, materializada y auditada full-universe. |
| [Daily return labels](#daily-return-labels) | pilot target layer | 62% | Labels definidos y materializados en piloto; no son full-universe ni features. |
| [Quotes raw](#quotes-raw) | institucional | 93% | Libro observado con taxonomia, casepacks y frontera review/bad auditada. |
| [Trades raw](#trades-raw) | draft institutionalized | 90% | Tape ejecutado muy rico en evidencia; falta limpiar deuda de indice y promocion editorial final. |
| [OHLCV 1m raw](#ohlcv-1m-raw) | raw closeout reconciled | 82% | Raw intradia entendido y reconciliado para LT1B, pero no globalmente limpio. |
| [OHLCV 1m split-normalized](#ohlcv-1m-split-normalized) | Nivel 5 consumida | 90% | Deuda critica de splits auditada; no equivale a promocion full-universe total. |
| [Intraday regime features](#intraday-regime-features) | Nivel 3 pilotada | 66% | Primer consumidor real de 1m split-normalized; falta auditoria amplia y validator. |
| [Halts](#halts) | foundation promotion ready | 92% | Eventos oficiales gobernados con dossier moderno, coverage y casepacks. |
| [Reference](#reference) | foundation promotion ready | 90% | Identidad, corporate actions y eventos bien encapsulados; no es fuente alpha ni precio. |
| [Additional context](#additional-context) | accepted auxiliary | 78% | Bloque auxiliar institucional con restricciones por subfamilia; sin validator propio. |
| [Short](#short) | accepted with restrictions | 74% | Contexto short usable con flags; no es core limpio universal. |
| [Short review FINRA](#short-review-finra) | FINRA baseline | 76% | Baseline oficial/free y provenance; no sustituye short local. |
| [LT1B universe](#lt1b-universe) | canonical operational cut | 78% | Corte operacional canonico; no es membership diaria fully PTI. |
| [Financial standalone schemas](#financial-standalone-schemas) | schema-only | 25% | Hay schemas de financial statements/ratios, pero falta gobierno completo propio. |
| [Regime indicators schemas](#regime-indicators-schemas) | schema-only | 22% | Hay schemas y notas de calidad, pero falta contrato, registry, policy y dossier. |

Lectura de avance global de la seccion:

- Si se mide por datasets/capas principales ya gobernadas: `01_foundations` esta alrededor de `82-85%`.
- Si se incluyen tambien familias schema-only y contextuales pendientes: la cobertura transversal real baja a `75-80%`.
- La deuda ya no es ausencia de arquitectura. La deuda esta en uniformidad final, validators especificos de capas derivadas/contextuales, dossiers de familias parciales y cierre editorial de algunas navegaciones.

## Graphify operativo

`01_foundations` usa Graphify como mapa semantico, no como source of truth ni
como profiler fisico de datos.

Regla corta:

```text
No escribir graphify-out/graph.json manualmente.
No construir un grafo monolitico de 01_foundations como primer paso.
Primero leaf graph. Despues root graph solo si aporta valor.
```

Importante:

```text
foundations_authority_graph no es una carpeta.
Es el nombre del primer grafo leaf oficial.
```

Cubrir `01_foundations` no significa escanear todo el arbol en un solo comando.
Significa cubrir sus partes institucionales mediante grafos leaf separados y,
si aporta valor, fusionarlos despues en `data_foundation_root_graph`.

Entrada operativa:

- [GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md](GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md) define que cuenta como build oficial, como validar outputs y cuando parar.
- [GRAPHIFY_REFRESH_QUEUE.md](GRAPHIFY_REFRESH_QUEUE.md) registra refrescos pendientes y evita tratar Graphify como si fuera Git.
- [module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md](module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md) define los slices semanticos y el flujo para pasar de grafo a diseno de tablas.

Slices canonicos:

```text
data_foundation_root_graph
foundations_authority_graph
certification_decisions_graph
reference_identity_graph
daily_ohlcv_graph
microstructure_quotes_trades_graph
additional_fundamentals_news_graph
```

Ninguna tabla CAPA 1 queda promovida solo por aparecer en un grafo. La regla de
promocion sigue siendo:

```text
contract + certification + evidence + physical profiling + validator
```

## Mapa por elemento de data

### Daily raw

**Identidad:** `daily_core_v0_1`.

**Que hay:** barras diarias `ticker-day` raw/core. Es la capa diaria institucional base. Distingue calidad de cobertura y no trata `vw` como autoridad primaria global.

**Artefactos por carpeta:**

- `validators`: [daily_validators.md](validators/daily/daily_validators.md)
- `canonical_schemas`: [daily_schema_contract.md](canonical_schemas/daily/daily_schema_contract.md)
- `contract_registry`: [daily_dataset_contract_v0_1.md](contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md), [daily_label_taxonomy_and_cut_policy.md](contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md)
- `data_consumption_policies`: [daily_consumption_policy.md](data_consumption_policies/daily_consumption_policy.md)
- `dataset_registry`: [daily_registry_entry.yaml](dataset_registry/daily/daily_registry_entry.yaml)
- `inspection_dossiers`: [daily_inspection_readout_v0_1.md](inspection_dossiers/daily/daily_inspection_readout_v0_1.md), [daily_hard_invalid_cases_v0_1.md](inspection_dossiers/daily/bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md), [daily_non_good_quality_cases_v0_1.md](inspection_dossiers/daily/flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md), [daily_good_cases_v0_1.md](inspection_dossiers/daily/good_justification/daily_good_cases_v0_1.md), [daily_coverage_cases_v0_1.md](inspection_dossiers/daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md)
- `module_contracts`: [daily_contracts_index.md](module_contracts/daily_contracts_index.md), [daily_acceptance_policy_explained.md](module_contracts/daily_acceptance_policy_explained.md), [daily_rules_explained_line_by_line.md](module_contracts/daily_rules_explained_line_by_line.md)

**Madurez:** `92%`.

**Lectura institucional:** suficientemente cerrada como base diaria. La deuda principal no es semantica, sino mantener sincronizada la lectura con capas derivadas y preservar la separacion entre `good`, `recoverable_with_flag`, `bad` y coverage.

### Daily adjusted

**Identidad:** `daily_adjusted_v0_1`.

**Que hay:** vista diaria derivada para verdad economica lenta, con `split_normalized`, `adjusted`, factores futuros y provenance. No reemplaza `trades_raw`, `quotes_raw` ni ejecucion intradia.

**Artefactos por carpeta:**

- `validators`: cubierto indirectamente por validacion de capa derivada y auditoria full-universe; no hay `validators/daily/daily_adjusted_validators.md` dedicado.
- `canonical_schemas`: [daily_adjusted_schema_contract.md](canonical_schemas/daily/daily_adjusted_schema_contract.md)
- `contract_registry`: [daily_adjusted_dataset_contract_v0_1.md](contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md)
- `data_consumption_policies`: gobernado por [daily_consumption_policy.md](data_consumption_policies/daily_consumption_policy.md) y las policies transversales de price view.
- `dataset_registry`: [daily_adjusted_registry_entry.yaml](dataset_registry/daily/daily_adjusted_registry_entry.yaml), [daily_adjusted_pilot_manifest_v0_1.csv](dataset_registry/daily/daily_adjusted_pilot_manifest_v0_1.csv), [daily_adjusted_pilot_manifest_v0_2.csv](dataset_registry/daily/daily_adjusted_pilot_manifest_v0_2.csv)
- `inspection_dossiers`: [daily_adjusted_full_universe_audit_v0_1.md](inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md), [daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md](inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md)
- `module_contracts`: [daily_adjusted_operational_landing_v0_1.md](module_contracts/daily_adjusted_operational_landing_v0_1.md), [daily_adjusted_incremental_materialization_plan_v0_1.md](module_contracts/daily_adjusted_incremental_materialization_plan_v0_1.md), [daily_adjusted_full_universe_promotion_plan_v0_1.md](module_contracts/daily_adjusted_full_universe_promotion_plan_v0_1.md), [daily_adjusted_pilot_results_v0_2.md](module_contracts/daily_adjusted_pilot_results_v0_2.md)

**Madurez:** `100%`.

**Lectura institucional:** es la capa mas cerrada de `01_foundations`: promovida full-universe, materializada, auditada contra `D:/ohlcv_daily`, consumida por labels y registrada como active operational derived price view. La frontera abierta es extension metodologica a corporate actions mas complejas, no promocion base.

### Daily return labels

**Identidad:** `daily_return_labels_v0_1`.

**Que hay:** capa piloto de labels forward-looking (`ret_1d`, `ret_3d`, `ret_5d`) derivada de `c_adjusted`. Es target/outcome, nunca feature disponible en decision time.

**Artefactos por carpeta:**

- `validators`: no hay validator dedicado todavia.
- `canonical_schemas`: [daily_return_labels_schema_contract.md](canonical_schemas/daily/daily_return_labels_schema_contract.md)
- `contract_registry`: [daily_return_labels_dataset_contract_v0_1.md](contract_registry/dataset_contracts/daily_return_labels_dataset_contract_v0_1.md)
- `data_consumption_policies`: [daily_return_labels_consumption_policy.md](data_consumption_policies/daily_return_labels_consumption_policy.md)
- `dataset_registry`: [daily_return_labels_registry_entry.yaml](dataset_registry/daily/daily_return_labels_registry_entry.yaml)
- `inspection_dossiers`: no hay dossier propio dedicado; la evidencia vive sobre todo en landing, consumer contract y materializacion piloto.
- `module_contracts`: [daily_return_labels_consumer_contract_v0_1.md](module_contracts/daily_return_labels_consumer_contract_v0_1.md), [daily_return_labels_operational_landing_v0_1.md](module_contracts/daily_return_labels_operational_landing_v0_1.md), [daily_return_labels_lt1b_promotion_plan_v0_1.md](module_contracts/daily_return_labels_lt1b_promotion_plan_v0_1.md)

**Madurez:** `62%`.

**Lectura institucional:** bien definida y pilotada, pero no cerrada. Falta promocion LT1B, validator anti-leakage/coverage dedicado, dossier propio y root separado si se promueve a full-universe.

### Quotes raw

**Identidad:** `quotes_core_v0_1`.

**Que hay:** libro observado `bid/ask` por quote observation. No es issuer identity, no es halt source, no es corporate action source y no se rehabilita automaticamente con contexto externo.

**Artefactos por carpeta:**

- `validators`: [quotes_validators.md](validators/quotes/quotes_validators.md)
- `canonical_schemas`: [quotes_schema_contract.md](canonical_schemas/quotes/quotes_schema_contract.md)
- `contract_registry`: [quotes_dataset_contract_v0_1.md](contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md), [quotes_label_taxonomy_and_cut_policy.md](contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md)
- `data_consumption_policies`: [quotes_consumption_policy.md](data_consumption_policies/quotes_consumption_policy.md)
- `dataset_registry`: [quotes_registry_entry.yaml](dataset_registry/quotes/quotes_registry_entry.yaml)
- `inspection_dossiers`: [quotes_inspection_readout_v0_1.md](inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md), [quotes_open_casepacks_audit_v0_1.md](inspection_dossiers/quotes/quotes_open_casepacks_audit_v0_1.md), [quotes_good_cases_v0_1.md](inspection_dossiers/quotes/good_justification/quotes_good_cases_v0_1.md), [quotes_review_cases_v0_1.md](inspection_dossiers/quotes/flagged_case_evidence_packs/quotes_review_cases_v0_1.md), [quotes_bad_cases_v0_1.md](inspection_dossiers/quotes/bad_case_evidence_packs/quotes_bad_cases_v0_1.md)
- `module_contracts`: [quotes_contracts_index.md](module_contracts/quotes_contracts_index.md), [quotes_acceptance_policy_explained.md](module_contracts/quotes_acceptance_policy_explained.md), [quotes_rules_explained_line_by_line.md](module_contracts/quotes_rules_explained_line_by_line.md)

**Madurez:** `93%`.

**Lectura institucional:** bloque fuerte. Tiene taxonomia, readout global, casepacks y auditoria de integridad de la frontera `review/bad`. La deuda restante es mas de uniformidad notebook/global que de contrato.

### Trades raw

**Identidad:** `trades_raw` y file-level trade acceptance audit.

**Que hay:** tape ejecutado raw. La unidad raw es trade row; la unidad de aceptacion es file/ticker-day. La regla central es no confundir desacuerdo con `daily` o `1m` con corrupcion intrinseca del tape.

**Artefactos por carpeta:**

- `validators`: [trades_validators.md](validators/trades/trades_validators.md)
- `canonical_schemas`: [trades_schema_contract.md](canonical_schemas/trades/trades_schema_contract.md)
- `contract_registry`: [trades_dataset_contract_v0_1.md](contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md), [trades_label_taxonomy_and_cut_policy.md](contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md)
- `data_consumption_policies`: [trades_consumption_policy.md](data_consumption_policies/trades_consumption_policy.md)
- `dataset_registry`: [trades_registry_entry.yaml](dataset_registry/trades/trades_registry_entry.yaml)
- `inspection_dossiers`: [trades_inspection_readout_v0_1.md](inspection_dossiers/trades/trades_inspection_readout_v0_1.md), [trades_global_universe_readout_v0_1.md](inspection_dossiers/trades/trades_global_universe_readout_v0_1.md), [trades_population_readout_v0_1.md](inspection_dossiers/trades/population_evidence_packs/trades_population_readout_v0_1.md), [trades_file_acceptance_readout_v0_1.md](inspection_dossiers/trades/file_acceptance_evidence_packs/trades_file_acceptance_readout_v0_1.md), [trades_good_cases_v0_1.md](inspection_dossiers/trades/good_justification/trades_good_cases_v0_1.md), [trades_review_cases_v0_1.md](inspection_dossiers/trades/flagged_case_evidence_packs/trades_review_cases_v0_1.md), [trades_bad_cases_v0_1.md](inspection_dossiers/trades/bad_case_evidence_packs/trades_bad_cases_v0_1.md), [trades_sampling_strategy_v0_1.md](inspection_dossiers/trades/trades_sampling_strategy_v0_1.md)
- `module_contracts`: [trades_contracts_index.md](module_contracts/trades_contracts_index.md), [trades_acceptance_policy_explained.md](module_contracts/trades_acceptance_policy_explained.md), [trades_rules_explained_line_by_line.md](module_contracts/trades_rules_explained_line_by_line.md)

**Madurez:** `90%`.

**Lectura institucional:** es el bloque mas rico en evidencia global y lectura cuantitativa. La deuda no es analitica base: es limpiar navegacion/indice de family casepacks, homogeneizar acabado editorial y formalizar que el registry sigue en `draft_institutionalized` aunque la evidencia sea fuerte.

### OHLCV 1m raw

**Identidad:** `ohlcv_1m_raw_v0_1`.

**Que hay:** barras intradia raw `ticker-minute`. Es observacion raw, no split-normalized y no ajustada. Sirve para investigacion intradia con restricciones, no para aprender comparabilidad cross-session sin tratamiento de splits.

**Artefactos por carpeta:**

- `validators`: [ohlcv_1m_raw_validators.md](validators/ohlcv_1m/ohlcv_1m_raw_validators.md)
- `canonical_schemas`: [ohlcv_1m_schema_contract.md](canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md)
- `contract_registry`: [ohlcv_1m_raw_dataset_contract_v0_1.md](contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md)
- `data_consumption_policies`: [ohlcv_1m_raw_consumption_policy.md](data_consumption_policies/ohlcv_1m_raw_consumption_policy.md)
- `dataset_registry`: [ohlcv_1m_raw_registry_entry.yaml](dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml)
- `inspection_dossiers`: [raw_1m_lt1b_closeout_recalculation_v0_1.md](inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md), [raw_1m_schema_only_lt1b_inspection_readout_v0_1.md](inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md), [minute_core_quality_visual_cases_v0_1.md](inspection_dossiers/minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md)
- `module_contracts`: [ohlcv_1m_contracts_index.md](module_contracts/ohlcv_1m_contracts_index.md), [ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md](module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md)

**Madurez:** `82%`.

**Lectura institucional:** raw 1m esta entendido y reconciliado, no universalmente limpio. El propio registry fija una cola `bad` grande y separa raw de split-normalized. Puede sostener research/control con flags, pero no debe inflarse a capa intradia limpia para todos los consumidores.

### OHLCV 1m split-normalized

**Identidad:** `ohlcv_1m_split_normalized_v0_1`.

**Que hay:** vista intradia derivada para comparabilidad a traves de splits. Preserva observacion intradia local, aplica normalizacion por splits y no aplica dividendos.

**Artefactos por carpeta:**

- `validators`: no hay validator dedicado en `validators/ohlcv_1m/` para split-normalized; la validacion vive en dossier, notebooks y module contracts de capa derivada.
- `canonical_schemas`: [ohlcv_1m_split_normalized_schema_contract.md](canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md)
- `contract_registry`: [ohlcv_1m_split_normalized_dataset_contract_v0_1.md](contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md)
- `data_consumption_policies`: no hay policy dedicada; debe leerse junto a [ohlcv_1m_raw_consumption_policy.md](data_consumption_policies/ohlcv_1m_raw_consumption_policy.md) y price-view policies transversales.
- `dataset_registry`: [ohlcv_1m_split_normalized_registry_entry.yaml](dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml), [ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv](dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv)
- `inspection_dossiers`: [ohlcv_1m_split_normalized_final_readout_v0_1.md](inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md), [ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md](inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md), [ohlcv_1m_split_normalized_pilot_readout_v0_1.md](inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md)
- `module_contracts`: [ohlcv_1m_split_normalized_operational_landing_v0_1.md](module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md), [ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md](module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md), [ohlcv_1m_split_normalized_semantic_pilot_v0_1.md](module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md), [ohlcv_1m_split_normalized_pilot_results_v0_1.md](module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md)

**Madurez:** `90%`.

**Lectura institucional:** muy fuerte para la deuda concreta de splits. La auditoria full-universe de eventos split auditables reporta `FAIL = 0`, pero la capa no debe presentarse como auditoria total de toda la calidad intradia ni como promocion full-universe general.

### Intraday regime features

**Identidad:** `intraday_regime_features_v0_1`.

**Que hay:** primera capa derivada de features/estado intradia. Usa raw para estado local intradia y split-normalized para estado cross-session. No es edge, no es execution simulator y no es RL.

**Artefactos por carpeta:**

- `validators`: no hay validator dedicado.
- `canonical_schemas`: [intraday_regime_features_schema_contract.md](canonical_schemas/features/intraday_regime_features_schema_contract.md)
- `contract_registry`: [intraday_regime_features_dataset_contract_v0_1.md](contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md)
- `data_consumption_policies`: [intraday_regime_features_consumption_policy.md](data_consumption_policies/intraday_regime_features_consumption_policy.md)
- `dataset_registry`: [intraday_regime_features_registry_entry.yaml](dataset_registry/features/intraday_regime_features_registry_entry.yaml)
- `inspection_dossiers`: [intraday_regime_features_semantic_pilot_readout_v0_1.md](inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md)
- `module_contracts`: [intraday_regime_features_consumer_contract_v0_1.md](module_contracts/intraday_regime_features_consumer_contract_v0_1.md), [intraday_regime_features_variable_taxonomy_v0_1.md](module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md), [intraday_regime_features_operational_landing_v0_1.md](module_contracts/intraday_regime_features_operational_landing_v0_1.md), [intraday_regime_features_initial_materialization_results_v0_1.md](module_contracts/intraday_regime_features_initial_materialization_results_v0_1.md), [intraday_regime_features_semantic_pilot_results_v0_1.md](module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md), [intraday_regime_features_lt1b_promotion_plan_v0_1.md](module_contracts/intraday_regime_features_lt1b_promotion_plan_v0_1.md)

**Madurez:** `66%`.

**Lectura institucional:** pilotada y arquitectonicamente importante, pero todavia no auditada de forma amplia. Falta validator, dossier mas rico, coverage mayor y demostracion downstream mas completa.

### Halts

**Identidad:** `halts_v0_1`.

**Que hay:** eventos oficiales de halt/suspension desde Nasdaq, NYSE y SEC. Es evidence/reference event layer, no OHLCV, no quotes, no trades y no fuente unica de causalidad intradia.

**Artefactos por carpeta:**

- `validators`: [halts_validators.md](validators/halts/halts_validators.md)
- `canonical_schemas`: [halts_master_multisource_schema_contract.md](canonical_schemas/halts/halts_master_multisource_schema_contract.md), [halts_raw_sources_schema_contract.md](canonical_schemas/halts/halts_raw_sources_schema_contract.md), [halts_source_specific_outputs_schema_contract.md](canonical_schemas/halts/halts_source_specific_outputs_schema_contract.md), [halts_operational_summary_schema_contract.md](canonical_schemas/halts/halts_operational_summary_schema_contract.md), [halts_universe_coverage_schema_contract.md](canonical_schemas/halts/halts_universe_coverage_schema_contract.md)
- `contract_registry`: [halts_dataset_contract_v0_1.md](contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md)
- `data_consumption_policies`: [halts_consumption_policy.md](data_consumption_policies/halts_consumption_policy.md)
- `dataset_registry`: [halts_registry_entry.yaml](dataset_registry/halts/halts_registry_entry.yaml)
- `inspection_dossiers`: [halts_inspection_readout_v0_1.md](inspection_dossiers/halts/halts_inspection_readout_v0_1.md), [halts_good_coherent_visual_cases_v0_1.md](inspection_dossiers/halts/good_justification/halts_good_coherent_visual_cases_v0_1.md), [halts_review_visual_cases_v0_1.md](inspection_dossiers/halts/flagged_case_evidence_packs/halts_review_visual_cases_v0_1.md), [halts_bad_residual_cases_v0_1.md](inspection_dossiers/halts/bad_case_evidence_packs/halts_bad_residual_cases_v0_1.md), [halts_causal_overlay_cases_v0_1.md](inspection_dossiers/halts/causal_case_evidence_packs/halts_causal_overlay_cases_v0_1.md), [halts_universe_coverage_cases_v0_1.md](inspection_dossiers/halts/coverage_case_evidence_packs/halts_universe_coverage_cases_v0_1.md)
- `module_contracts`: [event_families_and_reference_inventory.md](module_contracts/event_families_and_reference_inventory.md), [market_session_scope.md](module_contracts/market_session_scope.md), [auditoria_and_certification_source_hierarchy.md](module_contracts/auditoria_and_certification_source_hierarchy.md)

**Madurez:** `92%`.

**Lectura institucional:** muy bien cubierto. Tiene canonical root, historical evidence, modern dossier, visual buckets, population snapshot, source allowlist y consumption restrictions. Falta solo mantener separadas las semanticas SEC/date-level/review visual/intraday full event.

### Reference

**Identidad:** `reference_v0_1`.

**Que hay:** identidad, overview, events, splits, dividends, exchanges, ticker types y artefactos operacionales. Es soporte de corporate actions, coverage, universo y overlays causales; no es precio ni ejecucion.

**Artefactos por carpeta:**

- `validators`: [reference_validators.md](validators/reference/reference_validators.md)
- `canonical_schemas`: [all_tickers_snapshot_schema_contract.md](canonical_schemas/reference/all_tickers_snapshot_schema_contract.md), [overview_schema_contract.md](canonical_schemas/reference/overview_schema_contract.md), [events_schema_contract.md](canonical_schemas/reference/events_schema_contract.md), [splits_schema_contract.md](canonical_schemas/reference/splits_schema_contract.md), [dividends_schema_contract.md](canonical_schemas/reference/dividends_schema_contract.md), [exchanges_schema_contract.md](canonical_schemas/reference/exchanges_schema_contract.md), [ticker_types_schema_contract.md](canonical_schemas/reference/ticker_types_schema_contract.md), [operational_run_schema_contract.md](canonical_schemas/reference/operational_run_schema_contract.md)
- `contract_registry`: [reference_dataset_contract_v0_1.md](contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md)
- `data_consumption_policies`: [reference_consumption_policy.md](data_consumption_policies/reference_consumption_policy.md)
- `dataset_registry`: [reference_registry_entry.yaml](dataset_registry/reference/reference_registry_entry.yaml)
- `inspection_dossiers`: [reference_inspection_readout_v0_2.md](inspection_dossiers/reference/reference_inspection_readout_v0_2.md), [reference_institutional_closeout_v0_1.md](inspection_dossiers/reference/reference_institutional_closeout_v0_1.md), [reference_modernization_gap_audit_2026-06-12.md](inspection_dossiers/reference/reference_modernization_gap_audit_2026-06-12.md), [reference_casepacks_traceability_audit_v0_1.md](inspection_dossiers/reference/reference_casepacks_traceability_audit_v0_1.md)
- `module_contracts`: [event_families_and_reference_inventory.md](module_contracts/event_families_and_reference_inventory.md), [corporate_actions_adjustment_methodology.md](module_contracts/corporate_actions_adjustment_methodology.md), [price_semantics_and_adjustment_policy.md](module_contracts/price_semantics_and_adjustment_policy.md)

**Madurez:** `90%`.

**Lectura institucional:** reference esta modernizado y promovible como soporte foundation. La limitacion importante es no tratar `all_tickers` como universo final, `overview.market_cap` como membership diaria PTI, ni ticker changes como continuidad economica automatica.

### Additional context

**Identidad:** `additional_v0_1`.

**Que hay:** bloque auxiliar Polygon para `financials`, `corporate_actions`, `economic`, `ipos` y `news`. No debe consumirse como dataset uniforme; cada subfamilia tiene semantica y riesgo propio.

**Artefactos por carpeta:**

- `validators`: no hay validator propio.
- `canonical_schemas`: [additional_financials_schema_contract.md](canonical_schemas/additional/additional_financials_schema_contract.md), [additional_corporate_actions_schema_contract.md](canonical_schemas/additional/additional_corporate_actions_schema_contract.md), [additional_economic_schema_contract.md](canonical_schemas/additional/additional_economic_schema_contract.md), [additional_ipos_schema_contract.md](canonical_schemas/additional/additional_ipos_schema_contract.md), [additional_news_schema_contract.md](canonical_schemas/additional/additional_news_schema_contract.md)
- `contract_registry`: [additional_dataset_contract_v0_1.md](contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md)
- `data_consumption_policies`: [additional_consumption_policy.md](data_consumption_policies/additional_consumption_policy.md)
- `dataset_registry`: [additional_registry_entry.yaml](dataset_registry/additional/additional_registry_entry.yaml)
- `inspection_dossiers`: [additional_institutional_closeout_v0_1.md](inspection_dossiers/additional/additional_institutional_closeout_v0_1.md)
- `module_contracts`: usa contratos transversales de eventos, price views, storage, consumers y evidence; no tiene indice/module-contract especifico propio.

**Madurez:** `78%`.

**Lectura institucional:** aceptado como bloque auxiliar con restricciones. La deuda es validator por subfamilia, mayor dossier visual/casepack si se abre consumo sensible y separacion mas fuerte de `corporate_actions` frente a `reference`.

### Short

**Identidad:** `short_v0_1`.

**Que hay:** short interest y short volume como contexto auxiliar/event-context. Tiene cobertura LT1B materializada, pero estado de certificacion mixto y restricciones por ventana/source.

**Artefactos por carpeta:**

- `validators`: no hay validator propio.
- `canonical_schemas`: [short_interest_schema_contract.md](canonical_schemas/short/short_interest_schema_contract.md), [short_volume_schema_contract.md](canonical_schemas/short/short_volume_schema_contract.md)
- `contract_registry`: [short_dataset_contract_v0_1.md](contract_registry/dataset_contracts/short_dataset_contract_v0_1.md)
- `data_consumption_policies`: [short_consumption_policy.md](data_consumption_policies/short_consumption_policy.md)
- `dataset_registry`: [short_registry_entry.yaml](dataset_registry/short/short_registry_entry.yaml)
- `inspection_dossiers`: [short_institutional_closeout_v0_1.md](inspection_dossiers/short/short_institutional_closeout_v0_1.md)
- `module_contracts`: no hay module-contract especifico; gobiernan consumers, promotion pipeline y evidence model transversales.

**Madurez:** `74%`.

**Lectura institucional:** aceptado con restricciones. Sirve para research, backtest extended y ML flagged, no para backtest core o ML primary sin conservar estado de certificacion y ventanas.

### Short review FINRA

**Identidad:** `short_review_finra_v0_1`.

**Que hay:** baseline oficial/free FINRA y capa de provenance para comparar y auditar short local.

**Artefactos por carpeta:**

- `validators`: no hay validator propio.
- `canonical_schemas`: [finra_short_interest_schema_contract.md](canonical_schemas/short_review/finra_short_interest_schema_contract.md), [finra_short_volume_schema_contract.md](canonical_schemas/short_review/finra_short_volume_schema_contract.md), [finra_short_provenance_schema_contract.md](canonical_schemas/short_review/finra_short_provenance_schema_contract.md)
- `contract_registry`: [short_review_dataset_contract_v0_1.md](contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md)
- `data_consumption_policies`: [short_review_consumption_policy.md](data_consumption_policies/short_review_consumption_policy.md)
- `dataset_registry`: [short_review_registry_entry.yaml](dataset_registry/short_review/short_review_registry_entry.yaml)
- `inspection_dossiers`: [short_institutional_closeout_v0_1.md](inspection_dossiers/short/short_institutional_closeout_v0_1.md)
- `module_contracts`: no hay module-contract especifico; gobiernan consumers, evidence y promotion transversales.

**Madurez:** `76%`.

**Lectura institucional:** buena capa de baseline/provenance. No sustituye `E:/TSIS/data/short`, no certifica historia completa `2005-2026` y requiere preservar scope/date windows.

### LT1B universe

**Identidad:** `lt1b_universe_v0_1`.

**Que hay:** corte operacional `<1B` usado para auditorias, materializaciones, expected coverage y download manifests. No es membership diaria fully point-in-time.

**Artefactos por carpeta:**

- `validators`: no hay validator propio.
- `canonical_schemas`: [lt1b_universe_schema_contract.md](canonical_schemas/universes/lt1b_universe_schema_contract.md)
- `contract_registry`: [lt1b_universe_dataset_contract_v0_1.md](contract_registry/dataset_contracts/lt1b_universe_dataset_contract_v0_1.md)
- `data_consumption_policies`: [lt1b_universe_consumption_policy.md](data_consumption_policies/lt1b_universe_consumption_policy.md)
- `dataset_registry`: [lt1b_universe_registry_entry.yaml](dataset_registry/universes/lt1b_universe_registry_entry.yaml)
- `inspection_dossiers`: no tiene dossier propio dedicado; aparece enlazado desde la reconciliacion `1m` y otros closeouts.
- `module_contracts`: [ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md](module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md), [data_storage_topology_and_target_state.md](module_contracts/data_storage_topology_and_target_state.md)

**Madurez:** `78%`.

**Lectura institucional:** corte canonico y operativo. Le falta validator/dossier propio si se quiere elevarlo como fuente universal de membership esperada diaria. Cada claim `<1B>` debe intersectar ticker y ventana PTI.

### Financial standalone schemas

**Identidad:** familia `financial/` en canonical schemas.

**Que hay:** schemas para `balance_sheets`, `cash_flow_statements`, `income_statements`, `ratios`, `operational_audit` y `operational_run`. Esta familia no es lo mismo que `additional/financials`; aqui se ven contratos de forma de estados financieros/fundamentals mas generales.

**Artefactos por carpeta:**

- `validators`: no hay validator propio.
- `canonical_schemas`: [balance_sheets_schema_contract.md](canonical_schemas/financial/balance_sheets_schema_contract.md), [cash_flow_statements_schema_contract.md](canonical_schemas/financial/cash_flow_statements_schema_contract.md), [income_statements_schema_contract.md](canonical_schemas/financial/income_statements_schema_contract.md), [ratios_schema_contract.md](canonical_schemas/financial/ratios_schema_contract.md), [operational_audit_schema_contract.md](canonical_schemas/financial/operational_audit_schema_contract.md), [operational_run_schema_contract.md](canonical_schemas/financial/operational_run_schema_contract.md)
- `contract_registry`: no hay dataset contract financiero standalone.
- `data_consumption_policies`: no hay policy financiera standalone.
- `dataset_registry`: no hay registry financiero standalone.
- `inspection_dossiers`: no hay dossier financiero standalone.
- `module_contracts`: no hay module-contract financiero standalone.

**Madurez:** `25%`.

**Lectura institucional:** familia parcialmente preparada a nivel schema, pero no gobernada como dataset propio. Para consumo sistematico haria falta contrato, registry, policy, validator, dossier y una decision explicita de relacion con `additional/financials`.

### Regime indicators schemas

**Identidad:** familia `regime_indicators/` en canonical schemas.

**Que hay:** schemas para proxies ETF/index y metadata de regimen. Incluye quality notes, pero no una capa institucional operativa completa.

**Artefactos por carpeta:**

- `validators`: no hay validator propio.
- `canonical_schemas`: [regime_etf_bars_schema_contract.md](canonical_schemas/regime_indicators/regime_etf_bars_schema_contract.md), [regime_index_bars_schema_contract.md](canonical_schemas/regime_indicators/regime_index_bars_schema_contract.md), [regime_metadata_schema_contract.md](canonical_schemas/regime_indicators/regime_metadata_schema_contract.md), [regime_indicators_quality_notes.md](canonical_schemas/regime_indicators/regime_indicators_quality_notes.md)
- `contract_registry`: no hay dataset contract de regime indicators.
- `data_consumption_policies`: no hay consumption policy de regime indicators.
- `dataset_registry`: no hay registry entry de regime indicators.
- `inspection_dossiers`: no hay dossier.
- `module_contracts`: no hay module-contract especifico.

**Madurez:** `22%`.

**Lectura institucional:** backlog de gobierno. Hay forma de datos y notas de riesgo, pero no contrato, ubicacion operativa, policy, validator ni evidencia de cierre.

## Lectura transversal por carpeta

| Carpeta | Estado | Lectura |
| --- | --- | --- |
| [validators](validators/README.md) | parcial fuerte | Cubre `daily`, `quotes`, `trades`, `ohlcv_1m_raw`, `reference`, `halts`. Faltan validators dedicados para `daily_adjusted`, `daily_return_labels`, `1m_split_normalized`, `intraday_regime_features`, `additional`, `short`, `short_review`, `lt1b_universe`, `financial`, `regime_indicators`. |
| [canonical_schemas](canonical_schemas/README.md) | muy amplio | Es la carpeta mas extensa y transversal. Cubre market data, derived views, labels, features, universes, reference, additional, financial, halts, regime indicators, short y short_review. |
| [contract_registry](contract_registry/dataset_contracts/README.md) | fuerte | Cubre todos los datasets principales y auxiliares institucionalizados. No cubre financial standalone ni regime indicators. |
| [data_consumption_policies](data_consumption_policies/README.md) | fuerte | Cubre datasets principales, contextuales, universe y features. Falta policy dedicada para `1m_split_normalized`, financial standalone y regime indicators. |
| [dataset_registry](dataset_registry/README.md) | fuerte | Localiza la mayoria de capas activas. Faltan registry entries para financial standalone y regime indicators. |
| [inspection_dossiers](inspection_dossiers/README.md) | fuerte pero desigual | Muy fuerte en `daily`, `quotes`, `trades`, `halts`, `reference`, `1m_split_normalized` y `minute`. Mas delgado en `short`, `additional`, `intraday_regime_features`; ausente en financial standalone y regime indicators. |
| [module_contracts](module_contracts/README.md) | muy fuerte | Excelente para reglas transversales, price views, evidence, consumers, daily, quotes, trades, 1m y features. Menos especifico para short/additional/financial/regime indicators. |

## Deuda principal para cerrar 01_foundations

1. Crear validators dedicados para capas derivadas y auxiliares que ya tienen consumo potencial: `daily_return_labels`, `ohlcv_1m_split_normalized`, `intraday_regime_features`, `additional`, `short`, `short_review` y `lt1b_universe`.
2. Crear o completar dossiers propios para `daily_return_labels`, `lt1b_universe`, `financial standalone` y `regime indicators` si se decide que no son solo schema/backlog.
3. Decidir si `financial/` standalone se fusiona semanticamente bajo `additional/financials` o si merece dataset contract, policy y registry propios.
4. Decidir si `regime_indicators/` pasa de schema-only a capa institucional; si pasa, necesita contrato, registry, policy, validators y dossier.
5. Separar policy propia de `ohlcv_1m_split_normalized` si se va a promover mas alla del piloto/split audit.
6. Limpiar deuda de navegacion en `trades` family casepacks para que el indice liste todas las familias documentadas.
7. Mantener sincronizados snapshots transversales antiguos con registros especificos mas nuevos; los artefactos vivos especificos mandan.

## Regla final

`01_foundations` esta suficientemente madura para seguir construyendo encima, pero no debe tratar todas sus familias como igualmente cerradas.

La linea correcta es:

- usar `daily_adjusted`, `daily`, `quotes`, `trades`, `reference`, `halts` y `1m_split_normalized` con respeto estricto a sus policies;
- tratar `daily_return_labels`, `intraday_regime_features`, `short`, `short_review`, `additional` y `lt1b_universe` como capas utiles pero condicionadas;
- tratar `financial standalone` y `regime indicators` como familias schema-only hasta que tengan gobierno completo.

El objetivo de este README es que un humano o agente pueda identificar de volada donde esta cerrado el sistema, donde esta condicionado y donde todavia falta institucionalizacion real.

## Nota final: aprovechamiento de `00_data_certification` para bloques por debajo del 80%

Esta nota revisa solo los elementos que en la tabla anterior quedaron por debajo del `80%`.

La fuente historica inspeccionada es:

- [00_data_certification](../01_research/01_auditoria_RAW_DATA/00_data_certification)

Regla de uso:

- la evidencia historica se puede aprovechar como fuente de auditoria, criterios, scripts, caches, coverage y closeout;
- no debe copiarse como contrato vivo sin normalizar rutas, encoding, nombres de modulo y semantica actual;
- si un documento historico contradice un contrato vivo de `01_foundations`, manda `01_foundations`.

| Elemento <80% | Evidencia historica directa | Podemos aprovechar | Limite |
| --- | --- | --- | --- |
| `daily_return_labels` | No aparece cierre historico directo de labels forward-looking en `00_data_certification`. | Parcialmente. Se puede aprovechar la certificacion historica de `daily` como base de calidad upstream, pero el layer de labels debe seguir gobernado por `daily_adjusted`, anti-leakage y materializacion propia. | No convertir los closeouts historicos de daily en certificacion de labels. Falta validator/dossier propio de labels. |
| `intraday_regime_features` | No aparece cierre historico directo de esta feature layer. | Parcialmente. Se puede aprovechar la auditoria historica de `1m`, `quotes`, `trades`, `halts` y `daily` como evidencia upstream, pero no como validacion de features. | Falta auditoria semantica propia de features, validator y dossier amplio. |
| `additional` | Si. Ver [03_additional_root_cause_audit_phase1_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/03_additional_root_cause_audit_phase1_closeout.md), [04_additional_causal_overlay_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md), [04_additional_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_closeout.md), [descarga_additional.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/descarga_additional.md) y [02_additional_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/certification/additional/02_additional_closeout.md). | Si, bastante. Ya hay separacion por subbloques, coverage efectiva, causal overlay y policy historica: `financials_core` fuerte, `news` mixto pero valioso, `ipos` contextual, `economic` macro, `corporate_actions_additional` secundario frente a `reference`, `ratios` en review. | No aprovecharlo como dataset plano. Lo reutilizable debe entrar por subbloque y con validator/policy modernos. |
| `short` | Si. Ver [cobertura_short_data.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/cobertura_short_data.md), [03_short_root_cause_audit_phase1_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/03_short_root_cause_audit_phase1_closeout.md), [04_short_causal_overlay_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/04_short_causal_overlay_closeout.md), [04_short_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/04_short_closeout.md) y [02_short_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/certification/short/02_short_closeout.md). | Si. La decision historica es clara: `FINRA` como baseline oficial; `Polygon short` como comparativo/secundario. Hay evidencia de coverage, ticker reuse risk, provider comparison, causal overlay y uso contextual. | No promover `Polygon short_volume` como baseline historico. No usar `short_interest` como causalidad intradia fina. Falta validator moderno especifico. |
| `short_review` | Si, a traves del mismo trabajo de `short`. | Si. El trabajo historico de FINRA reconstruido es precisamente la base que justifica `short_review_finra_v0_1` como baseline oficial/free y provenance. | No sustituye automaticamente el root `short` local ni certifica cobertura completa 2005-2026. |
| `lt1b_universe` | Si. Ver [00_descarga_universo.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/00_descarga_universo.md), [01_checklist_auditoria_universo_fundamentals.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/01_checklist_auditoria_universo_fundamentals.md) y [00_final_certification_process.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/certification/00_final_certification_process.md). | Si, para reconstruir dossier y validator de universo: hay trabajo PTI, anti-survivorship, lifecycle, market-cap logic y criterios `expected/present/healthy/usable`. | El `lt1b_universe_v0_1` actual es un corte operacional, no membership diaria fully PTI. La evidencia historica debe reconciliarse antes de elevarlo. |
| `financial standalone schemas` | Si, pero disperso. Ver [00_descarga_universo.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/00_descarga_universo.md), [01_checklist_auditoria_universo_fundamentals.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/01_checklist_auditoria_universo_fundamentals.md), [descarga_additional.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/descarga_additional.md) y [04_additional_closeout.md](../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_closeout.md). | Si, como semilla fuerte para contrato/validator/dossier financiero: hubo descarga fundamentals, checklist reproducible, coverage por endpoint, auditoria temporal y evidencia de `financials_core` casi completo. | Hay que decidir si `financial/` standalone vive como dataset propio o queda absorbido por `additional/financials`. No basta con schemas. |
| `regime_indicators schemas` | No hay cierre historico directo de ETF/index regime indicators. Solo aparece una referencia conceptual a `macro -> market regime context` dentro de `additional`. | Muy poco. Se puede reutilizar `economic` de `additional` como antecedente de overlay macro, pero no como evidencia de `regime_indicators` ETF/index. | Requiere institutionalizacion casi desde cero: contrato, registry, policy, validator, dossier y fuente fisica clara. |

Conclusion operativa:

- `additional`, `short`, `short_review`, `lt1b_universe` y `financial standalone` pueden subir de madurez sin rehacer todo desde cero, porque hay material historico util.
- `daily_return_labels` e `intraday_regime_features` deben seguir como capas modernas: se apoyan en upstream certificado, pero no tienen cierre historico directo.
- `regime_indicators` no debe promoverse por arrastre desde `additional/economic`; necesita un trabajo institucional propio.
