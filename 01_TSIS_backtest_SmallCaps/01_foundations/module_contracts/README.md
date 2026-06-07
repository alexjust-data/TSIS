# Module Contracts

## Menu

- [Rol de esta carpeta](#rol-de-esta-carpeta)
- [Autoridad institucional](#autoridad-institucional)
- [Que es un module contract](#que-es-un-module-contract)
- [Que no es esta carpeta](#que-no-es-esta-carpeta)
- [Decision actual sobre estructura fisica](#decision-actual-sobre-estructura-fisica)
- [Indices vivos](#indices-vivos)
- [Familias documentales](#familias-documentales)
- [1. Alcance, autoridad y operacion](#1-alcance-autoridad-y-operacion)
  - [`module_scope.md`](#modulescopemd)
  - [`operational_boundaries.md`](#operationalboundariesmd)
  - [`semantic_authority.md`](#semanticauthoritymd)
  - [`naming_authority.md`](#namingauthoritymd)
  - [`data_storage_topology_and_target_state.md`](#datastoragetopologyandtargetstatemd)
  - [`promotion_pipeline.md`](#promotionpipelinemd)
  - [`dataset_contract_template.md`](#datasetcontracttemplatemd)
- [2. Evidencia, inspeccion y rehabilitacion](#2-evidencia-inspeccion-y-rehabilitacion)
  - [`evidence_model.md`](#evidencemodelmd)
  - [`inspection_dossier_model.md`](#inspectiondossiermodelmd)
  - [`bad_evidence_and_rehabilitation.md`](#badevidenceandrehabilitationmd)
  - [`auditoria_and_certification_source_hierarchy.md`](#auditoriaandcertificationsourcehierarchymd)
  - [`layer_model.md`](#layermodelmd)
- [3. Consumers y consumo](#3-consumers-y-consumo)
  - [`consumer_classes.md`](#consumerclassesmd)
  - [`daily_return_labels_consumer_contract_v0_1.md`](#dailyreturnlabelsconsumercontractv01md)
  - [`intraday_regime_features_consumer_contract_v0_1.md`](#intradayregimefeaturesconsumercontractv01md)
  - [`price_view_consumer_integration_status.md`](#priceviewconsumerintegrationstatusmd)
  - [`price_view_integration_priority_plan_v0_1.md`](#priceviewintegrationpriorityplanv01md)
- [4. Price views y semantica de precio](#4-price-views-y-semantica-de-precio)
  - [`price_semantics_and_adjustment_policy.md`](#pricesemanticsandadjustmentpolicymd)
  - [`price_views_registry.md`](#priceviewsregistrymd)
  - [`pipeline_price_view_policy.md`](#pipelinepriceviewpolicymd)
  - [`pipeline_price_view_policy_explained.md`](#pipelinepriceviewpolicyexplainedmd)
  - [`pipeline_price_view_rules_line_by_line.md`](#pipelinepriceviewruleslinebylinemd)
  - [`price_semantics_rules_line_by_line.md`](#pricesemanticsruleslinebylinemd)
  - [`external_price_comparison_caveats.md`](#externalpricecomparisoncaveatsmd)
  - [`external_price_comparison_rules_line_by_line.md`](#externalpricecomparisonruleslinebylinemd)
  - [`corporate_actions_adjustment_methodology.md`](#corporateactionsadjustmentmethodologymd)
- [5. Reference, eventos y sesiones](#5-reference-eventos-y-sesiones)
  - [`event_families_and_reference_inventory.md`](#eventfamiliesandreferenceinventorymd)
  - [`market_session_scope.md`](#marketsessionscopemd)
- [6. Standards, madurez y snapshots](#6-standards-madurez-y-snapshots)
  - [`policy_explanation_standard.md`](#policyexplanationstandardmd)
  - [`layer_validation_standard_v0_1.md`](#layervalidationstandardv01md)
  - [`layer_maturity_assessment_v0_1.md`](#layermaturityassessmentv01md)
  - [`state_snapshot_standard.md`](#statesnapshotstandardmd)
  - [`foundations_transversal_final_review_v0_1.md`](#foundationstransversalfinalreviewv01md)
  - [`foundations_transversal_final_review_v0_2.md`](#foundationstransversalfinalreviewv02md)
- [7. Daily y derivados](#7-daily-y-derivados)
  - [`daily_acceptance_policy_explained.md`](#dailyacceptancepolicyexplainedmd)
  - [`daily_rules_explained_line_by_line.md`](#dailyrulesexplainedlinebylinemd)
  - [`daily_adjusted_operational_landing_v0_1.md`](#dailyadjustedoperationallandingv01md)
  - [`daily_adjusted_incremental_materialization_plan_v0_1.md`](#dailyadjustedincrementalmaterializationplanv01md)
  - [`daily_adjusted_full_universe_promotion_plan_v0_1.md`](#dailyadjustedfulluniversepromotionplanv01md)
  - [`daily_adjusted_pilot_manifest_v0_1.md`](#dailyadjustedpilotmanifestv01md)
  - [`daily_adjusted_pilot_results_v0_1.md`](#dailyadjustedpilotresultsv01md)
  - [`daily_adjusted_pilot_results_v0_2.md`](#dailyadjustedpilotresultsv02md)
  - [`daily_return_labels_operational_landing_v0_1.md`](#dailyreturnlabelsoperationallandingv01md)
  - [`daily_return_labels_lt1b_promotion_plan_v0_1.md`](#dailyreturnlabelslt1bpromotionplanv01md)
- [8. OHLCV 1m y split normalization](#8-ohlcv-1m-y-split-normalization)
  - [`ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`](#ohlcv1mhistoricalcloseoutlt1breconciliationv01md)
  - [`ohlcv_1m_split_normalized_operational_landing_v0_1.md`](#ohlcv1msplitnormalizedoperationallandingv01md)
  - [`ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`](#ohlcv1msplitnormalizedincrementalmaterializationplanv01md)
  - [`ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`](#ohlcv1msplitnormalizedsemanticpilotv01md)
  - [`ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`](#ohlcv1msplitnormalizedpilotmanifestv02md)
  - [`ohlcv_1m_split_normalized_pilot_results_v0_1.md`](#ohlcv1msplitnormalizedpilotresultsv01md)
- [9. Intraday regime features](#9-intraday-regime-features)
  - [`intraday_regime_features_variable_taxonomy_v0_1.md`](#intradayregimefeaturesvariabletaxonomyv01md)
  - [`intraday_regime_features_operational_landing_v0_1.md`](#intradayregimefeaturesoperationallandingv01md)
  - [`intraday_regime_features_initial_materialization_results_v0_1.md`](#intradayregimefeaturesinitialmaterializationresultsv01md)
  - [`intraday_regime_features_semantic_pilot_results_v0_1.md`](#intradayregimefeaturessemanticpilotresultsv01md)
  - [`intraday_regime_features_deferred_families_v0_1.md`](#intradayregimefeaturesdeferredfamiliesv01md)
  - [`intraday_regime_features_lt1b_promotion_plan_v0_1.md`](#intradayregimefeatureslt1bpromotionplanv01md)
- [10. Quotes y trades](#10-quotes-y-trades)
  - [`quotes_acceptance_policy_explained.md`](#quotesacceptancepolicyexplainedmd)
  - [`quotes_rules_explained_line_by_line.md`](#quotesrulesexplainedlinebylinemd)
  - [`trades_acceptance_policy_explained.md`](#tradesacceptancepolicyexplainedmd)
  - [`trades_rules_explained_line_by_line.md`](#tradesrulesexplainedlinebylinemd)
- [11. Governance, indices y migracion](#11-governance-indices-y-migracion)
  - [`README.md`](#readmemd)
  - [`daily_contracts_index.md`](#dailycontractsindexmd)
  - [`quotes_contracts_index.md`](#quotescontractsindexmd)
  - [`trades_contracts_index.md`](#tradescontractsindexmd)
  - [`ohlcv_1m_contracts_index.md`](#ohlcv1mcontractsindexmd)
  - [`transversal_contracts_index.md`](#transversalcontractsindexmd)
  - [`module_contracts_migration_map_v0_1.md`](#modulecontractsmigrationmapv01md)
  - [`module_contracts_reference_pre_audit_v0_1.md`](#modulecontractsreferencepreauditv01md)
  - [`module_contracts_migration_execution_plan_v0_1.md`](#modulecontractsmigrationexecutionplanv01md)
- [Documentos por sensibilidad](#documentos-por-sensibilidad)
  - [Muy alta sensibilidad](#muy-alta-sensibilidad)
  - [Alta sensibilidad por consumidores](#alta-sensibilidad-por-consumidores)
  - [Alta sensibilidad por capas derivadas](#alta-sensibilidad-por-capas-derivadas)
- [Como leer esta carpeta](#como-leer-esta-carpeta)
  - [Si vas a tocar market data o price views](#si-vas-a-tocar-market-data-o-price-views)
  - [Si vas a tocar un dataset certificado](#si-vas-a-tocar-un-dataset-certificado)
  - [Si vas a tocar una capa derivada](#si-vas-a-tocar-una-capa-derivada)
  - [Si vas a tocar consumidores](#si-vas-a-tocar-consumidores)
  - [Si vas a reorganizar documentos](#si-vas-a-reorganizar-documentos)
- [Reglas de creacion de nuevos module contracts](#reglas-de-creacion-de-nuevos-module-contracts)
- [Checklist antes de modificar un module contract](#checklist-antes-de-modificar-un-module-contract)
- [Errores que debe evitar esta carpeta](#errores-que-debe-evitar-esta-carpeta)
- [Relacion con `CHANGELOG.md`](#relacion-con-changelogmd)
- [Regla final](#regla-final)


## Rol de esta carpeta

`module_contracts/` es la capa de gobernanza transversal del modulo 01.

Es la carpeta que fija las reglas comunes que el resto de `01_foundations` debe obedecer.

Su funcion principal es responder:

- cual es el alcance del modulo;
- que autoridad semantica manda;
- que significa cada estado institucional;
- como se promociona un activo;
- que evidencia es suficiente;
- como se explican policies;
- como se validan capas derivadas;
- como se tratan price views;
- como se leen corporate actions;
- como se compara contra fuentes externas;
- como se define una sesion de mercado;
- como se construyen dossiers de inspeccion;
- como se gobiernan consumidores;
- como se aterrizan capas piloto;
- como se planifica una promocion full-universe;
- y como se preserva compatibilidad documental.

Esta carpeta no contiene datos raw.

Contiene reglas, planes, standards, snapshots, contratos de consumidor, inventarios, indices y decisiones metodologicas transversales.

## Autoridad institucional

La jerarquia practica dentro de `01_foundations` es:

1. contratos raiz TSIS y gobernanza global;
2. `AGENTS.md`, `LOCAL_RULES.md`, `README.md` del modulo;
3. `module_contracts/` para reglas transversales;
4. `contract_registry/dataset_contracts/` para contratos de datasets concretos;
5. `data_consumption_policies/` para consumo por pipeline;
6. `canonical_schemas/` para forma minima;
7. `dataset_registry/` para localizacion y estado operativo;
8. `validators/` para checks minimos;
9. `inspection_dossiers/` para evidencia humana e inspeccion.

Regla:

- si un documento especifico contradice una regla transversal viva, debe revisarse;
- si un snapshot antiguo contradice una policy viva mas especifica, manda la policy viva;
- si una conversacion o notebook contradice un contrato, manda el contrato.

## Que es un module contract

Un `module contract` puede ser:

- policy transversal;
- standard metodologico;
- contrato de consumidor;
- plan de promocion;
- operational landing;
- manifest de piloto;
- results document;
- snapshot de estado;
- inventario;
- indice;
- plan de migracion;
- o documento explicativo line-by-line.

No todos tienen el mismo peso.

Por eso es importante distinguir entre:

- policies vivas;
- standards;
- planes;
- resultados;
- snapshots;
- indices;
- documentos historicos versionados.

## Que no es esta carpeta

`module_contracts/` no es:

- una carpeta de datos;
- una carpeta de outputs temporales;
- una carpeta para notebooks;
- una carpeta de schemas por columnas;
- una registry fisica;
- ni un sustituto de los dataset contracts.

Tampoco debe usarse para esconder decisiones locales que pertenecen a:

- `contract_registry/dataset_contracts/`;
- `data_consumption_policies/`;
- `canonical_schemas/`;
- `dataset_registry/`;
- `validators/`;
- o `inspection_dossiers/`.

## Decision actual sobre estructura fisica

La carpeta esta aun en layout plano.

Esto es intencional.

Aunque ya existe una propuesta de migracion futura a subcarpetas, la migracion fisica no esta ejecutada.

Por tanto:

- la ruta canonica vigente de cada documento sigue siendo su path actual en `module_contracts/`;
- las referencias existentes al layout plano siguen siendo validas;
- no debe moverse ningun documento por estetica;
- no debe corregirse un path antiguo por intuicion;
- cualquier migracion futura debe pasar por mapa, pre-auditoria y plan de ejecucion.

Documentos que gobiernan esa futura migracion:

- `module_contracts_migration_map_v0_1.md`
- `module_contracts_reference_pre_audit_v0_1.md`
- `module_contracts_migration_execution_plan_v0_1.md`

La pre-auditoria encontro:

- `188` referencias vivas;
- `41` source files;
- `55` target documents.

Esto prueba que una migracion cosmetica podria romper mucho. Por eso la regla vigente es:

```text
primero navegacion,
despues mapa de dependencias,
solo despues migracion fisica si compensa.
```

## Indices vivos

Existen indices de navegacion:

- `daily_contracts_index.md`
- `quotes_contracts_index.md`
- `trades_contracts_index.md`
- `ohlcv_1m_contracts_index.md`
- `transversal_contracts_index.md`

Estos indices no reemplazan los contratos.

Sirven para descubrir documentos por dominio o categoria.

## Familias documentales

La carpeta puede leerse en diez familias principales:

1. alcance, autoridad y operacion del modulo;
2. evidencia, inspeccion y rehabilitacion;
3. consumers y consumo;
4. price views y semantica de precio;
5. corporate actions, reference y eventos;
6. standards de promocion, madurez y validacion;
7. daily y derivados;
8. ohlcv_1m y derivados;
9. features/labels downstream;
10. governance snapshots, indices y migracion.

## 1. Alcance, autoridad y operacion

### `module_scope.md`

Define el alcance del modulo 01.

Sirve para no confundir el modulo con un workspace generico de research ni con una capa live/RL.

Debe leerse al empezar cualquier trabajo que pueda cambiar el mandato del modulo.

### `operational_boundaries.md`

Fija los limites operativos de la fase actual: consolidacion institucional.

Establece que la prioridad es:

- preservar evidencia;
- formalizar contratos;
- construir policies, schemas, lineage y validators;
- evitar refactors cosmeticos de zonas historicas.

Tambien marca como cambio de alta severidad:

- redefinir `good/review/bad`;
- cambiar consumers;
- alterar schema canonico;
- alterar semantica de universo;
- reinterpretar closeouts;
- mover arboles historicos.

### `semantic_authority.md`

Define el significado institucional de terminos criticos.

Fija:

- `good`;
- `review`;
- `bad`;
- `recoverable`;
- `recoverable_with_flag`;
- `review_not_rehabilitated`;
- consumidores como `backtest_core`, `ml_primary`, `ml_flagged`;
- estados como `exploratory`, `validated`, `institutional`.

Regla:

- un termino critico no puede depender de memoria conversacional.

### `naming_authority.md`

Define como nombrar activos institucionales.

Evita:

- nombres ambiguos;
- `final`, `final2`, `ok_ahora`;
- colisiones de dominio;
- versionado improvisado.

Aplica a dataset identities, contracts, policies, schemas, validators, manifests y outputs que aspiren a consumo sistemico.

### `data_storage_topology_and_target_state.md`

Fija la lectura institucional de la topologia de datos.

Distingue:

- `C:/TSIS_Data/data`;
- `D:/`;
- `E:/TSIS/data`;
- `01_foundations`;
- run artifacts;
- data raw;
- materializaciones operativas.

Regla:

- dos carpetas con nombres parecidos no implican la misma semantica.

### `promotion_pipeline.md`

Define el pipeline:

```text
exploratory -> provisional -> validated -> institutional -> deprecated -> archived
```

Nada debe convertirse en activo consumible por costumbre.

La promocion exige:

- evidencia;
- contrato;
- validacion;
- trazabilidad.

### `dataset_contract_template.md`

Define la plantilla minima de contratos de dataset.

Obliga a responder:

- identidad;
- status;
- purpose;
- semantic scope;
- source lineage;
- schema;
- coverage;
- quality policy;
- allowed consumers;
- validators;
- known limitations;
- change policy.

## 2. Evidencia, inspeccion y rehabilitacion

### `evidence_model.md`

Define que cuenta como evidencia institucional.

Distingue:

- evidencia forense;
- evidencia de certificacion;
- evidencia de validacion;
- evidencia de lineage;
- evidencia de uso restringido.

Regla:

- evidencia no es opinion ni memoria conversacional.

### `inspection_dossier_model.md`

Define el modelo canonico de inspection dossiers.

Fija la cadena:

```text
evidencia historica preservada
-> artefactos reproducibles de inspeccion
-> inspection readout
-> contrato institucional
```

Tambien impone la regla:

```text
Que muestra
Responde
No responde
Consecuencia
```

### `bad_evidence_and_rehabilitation.md`

Define el protocolo para declarar `bad`.

Un `bad` no puede ser solo una flag de validador.

Debe tener:

- identidad;
- causa;
- evidencia;
- explicacion;
- posible rehabilitacion;
- estado final.

### `auditoria_and_certification_source_hierarchy.md`

Define la jerarquia correcta entre auditoria historica, certificacion y foundations.

Es especialmente importante para `daily`, `quotes` y `trades`.

Regla:

- foundations encapsula evidencia historica; no la borra ni la reinterpreta silenciosamente.

### `layer_model.md`

Define que es una capa institucional o derivada.

Ayuda a distinguir:

- raw dataset;
- price view;
- feature layer;
- label layer;
- consumer layer;
- audit artifact.

## 3. Consumers y consumo

### `consumer_classes.md`

Define el vocabulario base de consumidores:

- `backtest_core`;
- `backtest_extended`;
- `event_engine`;
- `execution_simulator`;
- `ml_primary`;
- `ml_flagged`;
- `rl_allowed`;
- `causal_only`;
- `research_only`;
- `forensic_only`;
- `live_downstream_candidate`.

Regla:

- las clases no son transitivas.

Ejemplos:

- `backtest_core` no implica `execution_simulator`;
- `ml_primary` no implica `rl_allowed`;
- `research_only` no implica `backtest_extended`.

### `daily_return_labels_consumer_contract_v0_1.md`

Define el consumidor inicial de `daily_adjusted` para labels diarios.

Fija que `daily_return_labels` son `y`, no `X`.

### `intraday_regime_features_consumer_contract_v0_1.md`

Define el consumidor piloto de `ohlcv_1m_split_normalized`.

Explica que `intraday_regime_features` valida semantica downstream y puede convertirse en feature/state research, pero no equivale a alpha ni a full-universe feature layer.

### `price_view_consumer_integration_status.md`

Snapshot de estado de integracion real de price views.

No redefine la policy; muestra que consumidores estan conectados o pendientes.

### `price_view_integration_priority_plan_v0_1.md`

Plan de prioridad para integrar price views.

Justifica por que `daily_adjusted` y sus consumidores diarios son una prioridad transversal antes de abrir capas mas sensibles.

## 4. Price views y semantica de precio

### `price_semantics_and_adjustment_policy.md`

Documento central.

Fija la politica transversal de semantica de precio.

Distingue:

- `raw`;
- `split_normalized`;
- `adjusted`;
- `adjusted_proxy`;
- vistas de book/tape;
- vistas economicas;
- comparacion externa;
- corporate actions.

Regla:

- no existe un unico precio universal.

### `price_views_registry.md`

Registry conceptual de price views.

Define las vistas reconocidas y su rol.

No sustituye dataset registry fisico.

### `pipeline_price_view_policy.md`

Asigna price views por pipeline/departamento funcional.

Evita que un pipeline diario economico consuma raw tape o que ejecucion consuma adjusted economic series como verdad local.

### `pipeline_price_view_policy_explained.md`

Capa explicativa de la policy anterior.

Existe por el standard de explicacion de policies.

### `pipeline_price_view_rules_line_by_line.md`

Version linea por linea de reglas de pipeline price view.

Sirve para lectura operativa comprimida.

### `price_semantics_rules_line_by_line.md`

Version linea por linea de `price_semantics_and_adjustment_policy.md`.

### `external_price_comparison_caveats.md`

Define como comparar con plataformas externas.

Regla:

- no se puede declarar discrepancia sin saber si la serie externa esta adjusted, raw, remapeada o con corporate actions.

### `external_price_comparison_rules_line_by_line.md`

Version linea por linea de las reglas de comparacion externa.

### `corporate_actions_adjustment_methodology.md`

Define metodologia de splits/dividendos y ajustes.

Es clave para `daily_adjusted`, `daily_return_labels` y capas cross-session.

## 5. Reference, eventos y sesiones

### `event_families_and_reference_inventory.md`

Inventario de familias de eventos y reference.

Conecta:

- splits;
- dividends;
- halts;
- reference;
- news;
- ipos;
- corporate actions;
- economic/financial context.

### `market_session_scope.md`

Define el alcance institucional de sesion.

La sesion objetivo del modulo para varios datasets es:

```text
04:00-20:00 America/New_York
```

Pero cada dataset debe interpretar premarket/afterhours segun su semantica.

## 6. Standards, madurez y snapshots

### `policy_explanation_standard.md`

Fija que una policy formal no basta.

Toda policy importante debe explicar:

- que significa;
- que pregunta responde;
- que no responde;
- que error evita;
- que consecuencia operacional tiene.

### `layer_validation_standard_v0_1.md`

Define los checks minimos para validar una capa derivada.

Incluye:

- validacion semantica;
- validacion de implementacion;
- controles negativos;
- inspeccion visual;
- consumidor real o equivalente;
- reproducibilidad;
- trazabilidad documental.

### `layer_maturity_assessment_v0_1.md`

Aplica el standard de madurez a capas activas.

Distingue niveles como:

- definida;
- implementada;
- pilotada;
- auditada;
- consumida;
- promovida.

### `state_snapshot_standard.md`

Define como escribir snapshots de estado.

Regla:

- un snapshot no reemplaza policies vivas.

### `foundations_transversal_final_review_v0_1.md`

Snapshot transversal anterior.

Debe leerse historicamente.

### `foundations_transversal_final_review_v0_2.md`

Snapshot transversal mas reciente que actualiza el estado de cierre.

Debe prevalecer sobre `v0_1` cuando el tema sea estado actual de fase, salvo documento vivo mas especifico.

## 7. Daily y derivados

### `daily_acceptance_policy_explained.md`

Explica la acceptance policy de `daily`.

Debe leerse junto con:

- `daily_dataset_contract_v0_1.md`;
- `daily_label_taxonomy_and_cut_policy.md`;
- `daily_consumption_policy.md`.

### `daily_rules_explained_line_by_line.md`

Explicacion linea por linea de reglas de daily.

### `daily_adjusted_operational_landing_v0_1.md`

Define el aterrizaje operacional de `daily_adjusted`.

### `daily_adjusted_incremental_materialization_plan_v0_1.md`

Plan incremental para materializar `daily_adjusted`.

### `daily_adjusted_full_universe_promotion_plan_v0_1.md`

Plan de promocion full-universe de `daily_adjusted`.

### `daily_adjusted_pilot_manifest_v0_1.md`

Manifest piloto inicial de casos/tickers para `daily_adjusted`.

### `daily_adjusted_pilot_results_v0_1.md`

Resultados piloto iniciales.

### `daily_adjusted_pilot_results_v0_2.md`

Resultados piloto actualizados y mas fuertes.

### `daily_return_labels_operational_landing_v0_1.md`

Aterrizaje operacional de `daily_return_labels`.

### `daily_return_labels_lt1b_promotion_plan_v0_1.md`

Plan para promover labels diarios hacia `<1B>`.

No implica que ya esten full-universe.

## 8. OHLCV 1m y split normalization

### `ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`

Reconcilia el closeout historico de `ohlcv_1m` con el scope `<1B>`.

Clave:

- raw 1m queda entendido institucionalmente, pero no automaticamente limpio para todo consumo.

### `ohlcv_1m_split_normalized_operational_landing_v0_1.md`

Aterrizaje operacional de `ohlcv_1m_split_normalized`.

### `ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`

Plan incremental de materializacion.

### `ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`

Define piloto semantico de split normalization.

### `ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`

Manifest piloto versionado.

### `ohlcv_1m_split_normalized_pilot_results_v0_1.md`

Resultados del piloto.

Debe distinguirse piloto de full-universe.

## 9. Intraday regime features

### `intraday_regime_features_variable_taxonomy_v0_1.md`

Taxonomia de variables de `intraday_regime_features`.

Explica familias como:

- normalized open/close/high/low;
- range;
- realized volatility;
- gap;
- context vs previous sessions;
- distance to recent highs/lows.

### `intraday_regime_features_operational_landing_v0_1.md`

Aterrizaje operacional de la capa.

### `intraday_regime_features_initial_materialization_results_v0_1.md`

Resultados de materializacion inicial.

### `intraday_regime_features_semantic_pilot_results_v0_1.md`

Resultados del piloto semantico.

### `intraday_regime_features_deferred_families_v0_1.md`

Familias aplazadas.

### `intraday_regime_features_lt1b_promotion_plan_v0_1.md`

Plan de promocion `<1B>`.

No convierte la capa piloto en full-universe por si solo.

## 10. Quotes y trades

### `quotes_acceptance_policy_explained.md`

Explica acceptance policy de `quotes`.

Regla central:

- contexto externo puede explicar un episodio, pero no rehabilita automaticamente la calidad local del libro.

### `quotes_rules_explained_line_by_line.md`

Reglas de `quotes` linea por linea.

### `trades_acceptance_policy_explained.md`

Explica acceptance policy de `trades`.

Regla central:

- `trades` es raw execution tape, no serie economica diaria generica.

### `trades_rules_explained_line_by_line.md`

Reglas de `trades` linea por linea.

Es importante para no confundir:

- file-level labels;
- final certification states;
- uso execution/microstructure;
- uso benchmark/daily labels;
- reconciliacion.

## 11. Governance, indices y migracion

### `README.md`

Este documento.

Mapa maestro de la carpeta.

### `daily_contracts_index.md`

Indice del bloque daily.

### `quotes_contracts_index.md`

Indice del bloque quotes.

### `trades_contracts_index.md`

Indice del bloque trades.

### `ohlcv_1m_contracts_index.md`

Indice del bloque ohlcv_1m y primer consumidor `intraday_regime_features`.

### `transversal_contracts_index.md`

Indice de gobernanza, semantica, evidencia, price views, operacion y storage.

### `module_contracts_migration_map_v0_1.md`

Mapa conceptual path actual -> path futuro.

No ejecuta migracion.

### `module_contracts_reference_pre_audit_v0_1.md`

Pre-auditoria de referencias al layout plano.

Cuantifica superficie de ruptura.

### `module_contracts_migration_execution_plan_v0_1.md`

Plan de ejecucion segura para una migracion futura por lotes.

Regla:

- no migrar todo de golpe;
- verificar referencias despues de cada lote;
- detenerse ante ambiguedad.

## Documentos por sensibilidad

### Muy alta sensibilidad

Estos documentos tienen impacto transversal fuerte y muchas referencias:

- `policy_explanation_standard.md`
- `price_semantics_and_adjustment_policy.md`
- `pipeline_price_view_policy.md`
- `external_price_comparison_caveats.md`
- `market_session_scope.md`
- `corporate_actions_adjustment_methodology.md`
- `price_views_registry.md`
- `data_storage_topology_and_target_state.md`
- `event_families_and_reference_inventory.md`
- `bad_evidence_and_rehabilitation.md`
- `semantic_authority.md`
- `operational_boundaries.md`

No deben moverse ni reinterpretarse sin plan.

### Alta sensibilidad por consumidores

- `consumer_classes.md`
- `daily_return_labels_consumer_contract_v0_1.md`
- `intraday_regime_features_consumer_contract_v0_1.md`
- `price_view_consumer_integration_status.md`
- `price_view_integration_priority_plan_v0_1.md`

Cambios aqui pueden abrir o cerrar pipelines.

### Alta sensibilidad por capas derivadas

- `daily_adjusted_*`
- `ohlcv_1m_split_normalized_*`
- `daily_return_labels_*`
- `intraday_regime_features_*`

Cambios aqui pueden alterar madurez, promocion o consumo downstream.

## Como leer esta carpeta

### Si vas a tocar market data o price views

Lee primero:

1. `data_storage_topology_and_target_state.md`
2. `event_families_and_reference_inventory.md`
3. `price_semantics_and_adjustment_policy.md`
4. `price_views_registry.md`
5. `corporate_actions_adjustment_methodology.md`
6. `external_price_comparison_caveats.md`
7. `pipeline_price_view_policy.md`
8. `policy_explanation_standard.md`

### Si vas a tocar un dataset certificado

Lee:

1. `auditoria_and_certification_source_hierarchy.md`
2. `semantic_authority.md`
3. `evidence_model.md`
4. `inspection_dossier_model.md`
5. `bad_evidence_and_rehabilitation.md`
6. el contrato de dataset especifico;
7. la consumption policy especifica;
8. validators y dossier.

### Si vas a tocar una capa derivada

Lee:

1. `layer_model.md`
2. `layer_validation_standard_v0_1.md`
3. `layer_maturity_assessment_v0_1.md`
4. `promotion_pipeline.md`
5. el operational landing;
6. el promotion plan;
7. el pilot/results document.

### Si vas a tocar consumidores

Lee:

1. `consumer_classes.md`
2. `data_consumption_policies/README.md`
3. `pipeline_price_view_policy.md`
4. consumer contract especifico;
5. dataset contract especifico.

### Si vas a reorganizar documentos

Lee:

1. `module_contracts_migration_map_v0_1.md`
2. `module_contracts_reference_pre_audit_v0_1.md`
3. `module_contracts_migration_execution_plan_v0_1.md`
4. este README
5. `CHANGELOG.md`
6. `AGENTS.md`
7. `LOCAL_RULES.md`

No muevas nada sin demostrar que las referencias quedan consistentes.

## Reglas de creacion de nuevos module contracts

Crear un nuevo documento aqui solo tiene sentido si:

- la regla es transversal;
- la regla afecta a mas de un dataset;
- define vocabulario institucional;
- define una metodologia comun;
- gobierna promocion, validacion, evidencia o consumidores;
- formaliza un landing/promotion plan de una capa institucional;
- o captura un snapshot de estado que seria peligroso dejar en conversacion.

No debe crearse aqui:

- un schema por columnas;
- una registry entry;
- una policy de consumo concreta si ya tiene carpeta propia;
- un case pack;
- un notebook;
- un output temporal;
- o un documento que pertenece claramente a otro folder de `01_foundations`.

## Checklist antes de modificar un module contract

1. Identificar si es policy viva, standard, plan, results, snapshot o indice.
2. Revisar documentos dependientes.
3. Revisar referencias en dataset contracts, policies, schemas, registry, validators y dossiers.
4. Determinar si el cambio es editorial, operativo o semantico.
5. Si cambia semantica, revisar consumidores downstream.
6. Si cambia price semantics, revisar price views y materializers.
7. Si cambia promocion/madurez, revisar registry y changelog.
8. Si cambia path, usar mapa de migracion y pre-auditoria.
9. Registrar en `CHANGELOG.md` si cambia comportamiento institucional.

## Errores que debe evitar esta carpeta

No debe ocurrir que:

- una policy transversal se contradiga con una policy de consumo;
- un plan se lea como resultado ejecutado;
- un piloto se lea como full-universe;
- un snapshot viejo se lea como policy viva;
- una regla de price view se ignore por comodidad;
- una feature layer se promueva sin validacion;
- un label se use como feature;
- una evidencia historica se borre en lugar de encapsularse;
- una migracion rompa paths por estetica;
- o un agente cree autoridad semantica fuera de `01_foundations`.

## Relacion con `CHANGELOG.md`

Debe registrarse cambio cuando:

- se crea un module contract nuevo;
- cambia una policy transversal;
- cambia un standard;
- cambia consumer semantics;
- cambia price view policy;
- cambia promocion/madurez de una capa;
- cambia snapshot de estado;
- cambia plan de migracion;
- se ejecuta migracion fisica;
- o se modifica cualquier regla que afecte consumo downstream.

Cambios menores de enlaces, navegacion o claridad pueden no requerir entrada propia si no cambian semantica.

## Regla final

`module_contracts/` es la capa que evita que el modulo dependa de memoria, costumbre o notebooks abiertos.

Si una regla afecta a varios datasets, consumidores, price views, validacion, evidencia, promocion o interpretacion institucional, debe poder encontrarse aqui o estar enlazada desde aqui.

La carpeta ya tiene mucho contenido. El objetivo ahora no es multiplicar documentos, sino mantener autoridad, navegacion y trazabilidad.
