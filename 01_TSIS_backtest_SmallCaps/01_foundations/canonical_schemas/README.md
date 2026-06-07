# Canonical Schemas

## Menu

- [Rol de esta carpeta](#rol-de-esta-carpeta)
- [Autoridades relacionadas](#autoridades-relacionadas)
- [Que es un schema canonico](#que-es-un-schema-canonico)
- [Que no es esta carpeta](#que-no-es-esta-carpeta)
- [Schema conformity vs quality](#schema-conformity-vs-quality)
- [Tipos de schemas actuales](#tipos-de-schemas-actuales)
  - [Market data raw/core](#market-data-rawcore)
  - [Derived price views](#derived-price-views)
  - [Labels](#labels)
  - [Features / states](#features--states)
  - [Universes](#universes)
  - [Reference](#reference)
  - [Additional](#additional)
  - [Financial](#financial)
  - [Halts](#halts)
  - [Regime indicators](#regime-indicators)
  - [Short y short_review](#short-y-shortreview)
- [Estructura actual](#estructura-actual)
- [Campos recomendados para un schema contract](#campos-recomendados-para-un-schema-contract)
- [Alias fisicos y nombres canonicos](#alias-fisicos-y-nombres-canonicos)
- [Sentinels y formas fisicas multiples](#sentinels-y-formas-fisicas-multiples)
- [Operational artifacts](#operational-artifacts)
- [Reglas de cambio](#reglas-de-cambio)
- [Checklist antes de crear un schema nuevo](#checklist-antes-de-crear-un-schema-nuevo)
- [Checklist de modificacion](#checklist-de-modificacion)
- [Errores que debe evitar esta carpeta](#errores-que-debe-evitar-esta-carpeta)
- [Relacion con `CHANGELOG.md`](#relacion-con-changelogmd)
- [Regla final](#regla-final)


## Rol de esta carpeta

`canonical_schemas/` contiene los contratos de schema canonico del modulo 01.

Su funcion principal es responder:

- cual es la unidad logica de cada dataset o capa;
- que columnas, claves o campos son obligatorios;
- que columnas son condicionales;
- que tipos semanticos se esperan;
- que aliases fisicos se aceptan;
- que reglas estructurales minimas aplican;
- que layout fisico observado se ha inspeccionado;
- que formas fisicas validas existen;
- y que limites de interpretacion no deben confundirse con certificacion de calidad.

Un schema canonico define la forma minima defendible de un dataset o vista.

No autoriza por si solo consumo productivo.

## Autoridades relacionadas

Estos schemas deben leerse junto con:

- `01_foundations/module_contracts/dataset_contract_template.md`
- `01_foundations/module_contracts/semantic_authority.md`
- `01_foundations/module_contracts/operational_boundaries.md`
- `01_foundations/contract_registry/dataset_contracts/`
- `01_foundations/data_consumption_policies/`
- `01_foundations/dataset_registry/`
- `01_foundations/validators/`
- `01_foundations/inspection_dossiers/`

Regla de relacion:

- el dataset contract define que es el dataset;
- el canonical schema define que forma debe tener;
- la consumption policy define quien puede consumirlo;
- el registry localiza la capa;
- los validators ejecutan o especifican checks;
- el dossier muestra evidencia humana;
- el schema no reemplaza ninguna de esas capas.

## Que es un schema canonico

Un schema canonico es un contrato de estructura y semantica de campos.

Debe fijar, cuando aplique:

- unidad logica;
- grano;
- claves;
- columnas requeridas;
- columnas condicionales;
- tipos esperados;
- alias fisicos observados;
- reglas estructurales minimas;
- layout fisico;
- representative files inspeccionados;
- sentinel forms;
- provenance fields;
- y documentos relacionados.

Ejemplos de unidades logicas:

- `ticker-day bar`;
- `ticker-minute bar`;
- raw trade row;
- file-level audit row;
- quote observation;
- event row;
- filing observation;
- label row;
- feature row;
- universe membership row;
- operational audit artifact.

## Que no es esta carpeta

`canonical_schemas/` no es:

- una carpeta de datos;
- un dataset registry;
- una consumption policy;
- una evidencia de calidad completa;
- un validador ejecutable;
- una taxonomia de good/review/bad;
- ni una autorizacion para backtest o ML.

Un parquet puede cumplir schema y aun asi no ser usable.

Un dataset puede tener columnas correctas y aun asi fallar por:

- coverage;
- semantica temporal;
- leakage;
- price view incorrecta;
- identity conflict;
- ticker lifecycle;
- calidad economica;
- o falta de policy de consumo.

## Schema conformity vs quality

La conformidad de schema responde:

- el objeto tiene la forma esperada?
- sus columnas minimas existen?
- sus claves se pueden interpretar?
- sus tipos son parseables?
- sus aliases se pueden mapear?

No responde por si sola:

- si el dataset es bueno;
- si esta completo;
- si es full-universe;
- si esta promovido;
- si puede entrar en `backtest_core`;
- si no hay leakage;
- si la serie representa precio economico comparable;
- si una fecha es point-in-time correcta;
- o si una feature tiene valor predictivo.

La calidad y el consumo se deciden con contracts, validators, policies, registry y dossiers.

## Tipos de schemas actuales

### Market data raw/core

Schemas para datos observados base:

- `daily/daily_schema_contract.md`
- `quotes/quotes_schema_contract.md`
- `trades/trades_schema_contract.md`
- `ohlcv_1m/ohlcv_1m_schema_contract.md`

Deben distinguir:

- unidad logica;
- campos criticos;
- claves temporales;
- aliases fisicos;
- raw price semantics;
- y que warning estructural no equivale automaticamente a exclusion final.

### Derived price views

Schemas para vistas derivadas:

- `daily/daily_adjusted_schema_contract.md`
- `ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md`

Deben distinguir:

- campos base preservados;
- campos derivados obligatorios;
- factores de ajuste;
- provenance;
- raw vs adjusted;
- raw vs split-normalized;
- y columnas canonicas de consumo.

### Labels

Schemas de targets/outcomes:

- `daily/daily_return_labels_schema_contract.md`

Deben declarar:

- fuente obligatoria;
- columnas label;
- formula;
- nulos esperados;
- disponibilidad temporal;
- y prohibicion de tratarlos como features.

### Features / states

Schemas de capas de features:

- `features/intraday_regime_features_schema_contract.md`

Deben declarar:

- grano de feature;
- upstream;
- price view usada;
- columnas de estado;
- lookbacks;
- provenance;
- y limites de madurez.

### Universes

Schemas de universos:

- `universes/lt1b_universe_schema_contract.md`

Deben declarar:

- identidad de ticker;
- ventana temporal;
- corte de universo;
- campos de membership;
- limitaciones frente a membership diaria fully PTI;
- y relacion con expected coverage.

### Reference

Schemas de referencia:

- `reference/all_tickers_snapshot_schema_contract.md`
- `reference/dividends_schema_contract.md`
- `reference/events_schema_contract.md`
- `reference/exchanges_schema_contract.md`
- `reference/operational_run_schema_contract.md`
- `reference/overview_schema_contract.md`
- `reference/splits_schema_contract.md`
- `reference/ticker_types_schema_contract.md`

Deben distinguir:

- metadata;
- identity;
- corporate actions;
- lifecycle;
- source/provenance;
- operational run artifacts;
- y relacion con datasets de mercado.

### Additional

Schemas de familias auxiliares:

- `additional/additional_corporate_actions_schema_contract.md`
- `additional/additional_economic_schema_contract.md`
- `additional/additional_financials_schema_contract.md`
- `additional/additional_ipos_schema_contract.md`
- `additional/additional_news_schema_contract.md`

Deben declarar:

- source scope;
- identidad temporal;
- forma de evento/noticia/fundamental;
- provenance;
- y limites de consumo.

### Financial

Schemas de fundamentals y artefactos operativos:

- `financial/balance_sheets_schema_contract.md`
- `financial/cash_flow_statements_schema_contract.md`
- `financial/income_statements_schema_contract.md`
- `financial/ratios_schema_contract.md`
- `financial/operational_audit_schema_contract.md`
- `financial/operational_run_schema_contract.md`

Estos schemas pueden tener dos formas fisicas validas:

- payload form;
- empty sentinel form.

Regla:

- `_empty = true` es no-data sentinel, no business row.
- `filing_date` gobierna disponibilidad point-in-time; `period_end` no basta para consumo temporal.
- missing numeric fundamentals no deben convertirse en cero.

### Halts

Schemas de eventos halt/suspension:

- `halts/halts_master_multisource_schema_contract.md`
- `halts/halts_operational_summary_schema_contract.md`
- `halts/halts_raw_sources_schema_contract.md`
- `halts/halts_source_specific_outputs_schema_contract.md`
- `halts/halts_universe_coverage_schema_contract.md`

Deben distinguir:

- raw sources;
- source-specific intermediate outputs;
- master multisource;
- operational summary;
- coverage artifacts.

Regla:

- `halts_master_multisource` es evento/reference evidence, no OHLCV ni quote/trade tape.
- `ticker` puede faltar en SEC suspensions y no debe ser la unica clave.

### Regime indicators

Schemas de proxies de regimen:

- `regime_indicators/regime_etf_bars_schema_contract.md`
- `regime_indicators/regime_index_bars_schema_contract.md`
- `regime_indicators/regime_metadata_schema_contract.md`
- `regime_indicators/regime_indicators_quality_notes.md`

Deben distinguir:

- ETF/index proxies;
- minute bars;
- daily bars;
- metadata;
- y blocking quality notes.

Regla:

- un layout de columnas coherente no basta si la semantica de fecha esta rota.
- ETF/index regime indicators no son securities small-cap tradables del universo objetivo.

### Short y short_review

Schemas de short data:

- `short/short_interest_schema_contract.md`
- `short/short_volume_schema_contract.md`
- `short_review/finra_short_interest_schema_contract.md`
- `short_review/finra_short_volume_schema_contract.md`
- `short_review/finra_short_provenance_schema_contract.md`

Deben declarar:

- source scope;
- settlement/reporting dates;
- provenance;
- official/free baseline constraints;
- y limites frente a short data completa.

## Estructura actual

La carpeta contiene actualmente:

```text
canonical_schemas/
  additional/
  daily/
  features/
  financial/
  halts/
  ohlcv_1m/
  quotes/
  reference/
  regime_indicators/
  short/
  short_review/
  trades/
  universes/
```

## Campos recomendados para un schema contract

Un schema contract nuevo o revisado deberia tender a incluir:

```text
1. Rol / purpose
2. Status
3. Dataset o capa gobernada
4. Unidad logica
5. Grano
6. Raiz fisica observada, si aplica
7. Layout fisico observado, si aplica
8. Representative files inspeccionados
9. Claves canonicas
10. Columnas requeridas
11. Columnas condicionales
12. Tipos semanticos esperados
13. Alias fisico -> logico, si aplica
14. Reglas estructurales minimas
15. Sentinel forms, si aplica
16. Provenance fields, si aplica
17. Reglas de interpretacion
18. Consumer rules basicas, si aplica
19. Documentos relacionados
20. Politica de cambio
21. Veredicto/conclusion operacional
```

No todos los schemas necesitan todos los campos.

Pero todos deben dejar claro cual es la forma minima del objeto y que no se puede inferir solo desde esa forma.

## Alias fisicos y nombres canonicos

Los datos legacy o vendor pueden usar nombres fisicos abreviados.

Ejemplo:

```text
o -> open
h -> high
l -> low
c -> close
v -> volume
ts_utc -> minute_timestamp
vw -> vwap
n -> bar_count
```

Regla:

- el schema puede aceptar alias fisicos si los declara;
- los contratos y consumers deben hablar en terminos canonicos cuando sea posible;
- un cambio de alias aceptado puede afectar validators, builders y consumers.

## Sentinels y formas fisicas multiples

Algunos datasets tienen mas de una forma fisica valida.

Ejemplo fundamentals:

- payload form con business rows;
- empty sentinel form con `_empty = true`.

Regla:

- una forma sentinel valida no es error estructural;
- pero tampoco es una observacion economica o fundamental;
- los consumers deben tratarla como no-data controlado.

## Operational artifacts

Algunos schemas describen artefactos operativos, no datasets finales de mercado.

Ejemplos:

- `_audit`;
- `_run`;
- operational summaries;
- provenance logs;
- coverage files.

Regla:

- estos artefactos sirven para trazabilidad, auditoria o reproduccion;
- no deben convertirse en features o datos de mercado sin contrato posterior.

## Reglas de cambio

Alterar un schema canonico es cambio de alta severidad cuando afecta:

- unidad logica;
- claves;
- columnas requeridas;
- tipos semanticos;
- price semantics;
- temporal semantics;
- sentinel semantics;
- o consumers downstream.

Debe revisarse:

- dataset contract;
- consumption policy;
- registry entry;
- validators;
- inspection dossier;
- builders/scripts;
- y changelog si cambia semantica operativa.

## Checklist antes de crear un schema nuevo

1. Identificar dataset/capa exacta.
2. Confirmar si es raw, derived view, label, feature, universe, reference, event, financial, operational artifact o provenance.
3. Inspeccionar al menos un representative file real cuando exista.
4. Declarar raiz y layout fisico observado.
5. Declarar unidad logica y grano.
6. Declarar claves.
7. Declarar columnas requeridas y condicionales.
8. Declarar tipos esperados.
9. Declarar aliases fisicos.
10. Declarar reglas estructurales.
11. Declarar sentinel forms si existen.
12. Declarar limites de interpretacion.
13. Enlazar dataset contract/policy/registry/validators si existen.
14. Indicar que calidad completa no se infiere solo del schema.

## Checklist de modificacion

Al modificar un schema:

1. Determinar si el cambio es editorial o semantico.
2. Si cambia una columna requerida, revisar validators.
3. Si cambia una clave, revisar registry, builders y consumers.
4. Si cambia una vista de precio, revisar price semantics.
5. Si cambia disponibilidad temporal, revisar leakage y policies.
6. Si cambia sentinel semantics, revisar consumers.
7. Si cambia layout fisico, revisar materializers y registry.
8. Si cambia conclusion operacional, revisar dossier/evidence.
9. Registrar en `CHANGELOG.md` si afecta consumo o contrato.

## Errores que debe evitar esta carpeta

No debe ocurrir que:

- cumplir schema se presente como certificacion de calidad total;
- un schema raw se use para autorizar adjusted economics;
- un label schema se trate como feature schema;
- un operational artifact se consuma como market data;
- un universe schema se trate como coverage saludable;
- una forma sentinel se cuente como business row;
- una fecha defectuosa se acepte por tener tipo timestamp;
- un alias fisico se use sin declararlo;
- una capa piloto se presente como full-universe;
- o un schema contradiga su dataset contract.

## Relacion con `CHANGELOG.md`

Debe registrarse cambio cuando:

- se crea un schema canonico nuevo;
- cambia unidad logica;
- cambian claves;
- cambian columnas requeridas;
- cambia interpretacion temporal;
- cambia price view;
- cambia sentinel semantics;
- cambia conclusion operacional;
- o se corrige una inconsistencia que afectaba validators, registry o consumers.

Cambios editoriales menores o enlaces sin impacto operativo pueden no requerir entrada propia.

## Regla final

Un schema canonico no dice que el dataset sea bueno.

Dice que forma debe tener para que contratos, validators, policies, registry y dossiers puedan hablar del mismo objeto sin ambiguedad.
