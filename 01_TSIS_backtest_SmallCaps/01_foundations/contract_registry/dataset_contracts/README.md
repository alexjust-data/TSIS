# Dataset Contracts

## Menu

- [Rol de esta carpeta](#rol-de-esta-carpeta)
- [Autoridades relacionadas](#autoridades-relacionadas)
- [Que es un dataset contract](#que-es-un-dataset-contract)
- [Que es una taxonomy / cut policy](#que-es-una-taxonomy--cut-policy)
- [Que no es esta carpeta](#que-no-es-esta-carpeta)
- [Tipos de contratos actuales](#tipos-de-contratos-actuales)
  - [Dataset raw o core](#dataset-raw-o-core)
  - [Derived price views](#derived-price-views)
  - [Labels](#labels)
  - [Features / states](#features--states)
  - [Universes](#universes)
  - [Auxiliary / contextual datasets](#auxiliary--contextual-datasets)
- [Estructura actual](#estructura-actual)
- [Lectura por documento actual](#lectura-por-documento-actual)
  - [`daily_dataset_contract_v0_1.md`](#dailydatasetcontractv01md)
  - [`daily_label_taxonomy_and_cut_policy.md`](#dailylabeltaxonomyandcutpolicymd)
  - [`daily_adjusted_dataset_contract_v0_1.md`](#dailyadjusteddatasetcontractv01md)
  - [`daily_return_labels_dataset_contract_v0_1.md`](#dailyreturnlabelsdatasetcontractv01md)
  - [`quotes_dataset_contract_v0_1.md`](#quotesdatasetcontractv01md)
  - [`quotes_label_taxonomy_and_cut_policy.md`](#quoteslabeltaxonomyandcutpolicymd)
  - [`reference_dataset_contract_v0_1.md`](#referencedatasetcontractv01md)
  - [`trades_dataset_contract_v0_1.md`](#tradesdatasetcontractv01md)
  - [`trades_label_taxonomy_and_cut_policy.md`](#tradeslabeltaxonomyandcutpolicymd)
  - [`ohlcv_1m_raw_dataset_contract_v0_1.md`](#ohlcv1mrawdatasetcontractv01md)
  - [`ohlcv_1m_split_normalized_dataset_contract_v0_1.md`](#ohlcv1msplitnormalizeddatasetcontractv01md)
  - [`intraday_regime_features_dataset_contract_v0_1.md`](#intradayregimefeaturesdatasetcontractv01md)
  - [`lt1b_universe_dataset_contract_v0_1.md`](#lt1buniversedatasetcontractv01md)
  - [`additional_dataset_contract_v0_1.md`](#additionaldatasetcontractv01md)
  - [`short_dataset_contract_v0_1.md`](#shortdatasetcontractv01md)
  - [`short_review_dataset_contract_v0_1.md`](#shortreviewdatasetcontractv01md)
- [Campos recomendados para dataset contracts](#campos-recomendados-para-dataset-contracts)
- [Campos recomendados para taxonomy/cut policies](#campos-recomendados-para-taxonomycut-policies)
- [Homogeneidad y compatibilidad](#homogeneidad-y-compatibilidad)
- [Criterios para crear un contrato nuevo](#criterios-para-crear-un-contrato-nuevo)
- [Checklist antes de declarar un contrato institucional](#checklist-antes-de-declarar-un-contrato-institucional)
- [Checklist de modificacion](#checklist-de-modificacion)
- [Errores que debe evitar esta carpeta](#errores-que-debe-evitar-esta-carpeta)
- [Relacion con `CHANGELOG.md`](#relacion-con-changelogmd)
- [Regla final](#regla-final)


## Rol de esta carpeta

`contract_registry/dataset_contracts/` contiene los contratos formales de datasets, capas derivadas, universos, labels, features y politicas de taxonomia/corte del modulo 01.

Su funcion principal es responder:

- que es cada dataset o capa;
- que no es;
- que identidad logica tiene;
- que version institucional tiene;
- que estado de promocion tiene;
- que semantica representa;
- que fuentes y lineage lo sostienen;
- que schema lo describe;
- que coverage cubre;
- que politica de calidad aplica;
- que consumidores pueden existir;
- que validators necesita;
- que limitaciones conocidas tiene;
- y que cambios obligan a versionar.

Esta carpeta es una de las autoridades semanticas principales de `01_foundations`.

Si hay conflicto entre memoria conversacional, nombres legacy, notebooks historicos o intuicion local, manda el contrato vivo especifico, salvo que un contrato transversal de mayor jerarquia diga otra cosa.

## Autoridades relacionadas

Estos contratos deben leerse junto con:

- `01_foundations/module_contracts/dataset_contract_template.md`
- `01_foundations/module_contracts/semantic_authority.md`
- `01_foundations/module_contracts/promotion_pipeline.md`
- `01_foundations/module_contracts/consumer_classes.md`
- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/pipeline_price_view_policy.md`
- `01_foundations/canonical_schemas/`
- `01_foundations/data_consumption_policies/`
- `01_foundations/dataset_registry/`
- `01_foundations/validators/`
- `01_foundations/inspection_dossiers/`

Regla de relacion:

- el dataset contract define la semantica del activo;
- la taxonomy/cut policy define como se clasifican estados o buckets;
- el schema define la forma esperada;
- la consumption policy traduce el contrato a uso por consumidor;
- el registry localiza fisicamente y operacionalmente la capa;
- los validators definen checks minimos;
- el inspection dossier muestra la evidencia humana que sostiene el veredicto.

## Que es un dataset contract

Un dataset contract es el documento formal que fija la identidad y la interpretacion institucional de un dataset o capa.

Debe contestar, como minimo:

- `dataset_identity`;
- `status`;
- `purpose`;
- `semantic_scope`;
- `source_lineage`;
- `schema`;
- `coverage`;
- `quality_policy`;
- `allowed_consumers`;
- `validators`;
- `known_limitations`;
- `change_policy`.

No todos los contratos actuales tienen exactamente el mismo formato, porque la carpeta evoluciono por bloques. Pero todos deben responder la misma clase de preguntas institucionales.

## Que es una taxonomy / cut policy

Algunos documentos de esta carpeta no son dataset contracts base, sino politicas de taxonomia y corte.

Ejemplos:

- `daily_label_taxonomy_and_cut_policy.md`
- `quotes_label_taxonomy_and_cut_policy.md`
- `trades_label_taxonomy_and_cut_policy.md`
- `daily_label_taxonomy_and_cut_policy.md`

Su funcion es fijar:

- unidad exacta de decision;
- senales upstream consumidas;
- buckets intermedios;
- umbrales literales;
- etiquetas finales;
- reglas de traduccion historica a vocabulario contractual;
- y separacion entre ejes que no deben mezclarse.

Una taxonomy/cut policy no sustituye el dataset contract.

Lo aterriza.

El dataset contract dice que es el dataset y que estados institucionales existen.

La cut policy dice como se llega a esos estados de forma auditable.

## Que no es esta carpeta

Esta carpeta no es:

- una carpeta de datos;
- un registry fisico;
- un schema completo por columnas;
- un validator ejecutable;
- un dossier visual;
- un changelog;
- ni una policy de consumo detallada por pipeline.

Tampoco debe usarse para esconder decisiones operativas no justificadas.

Si un contrato habilita consumidores, debe remitir a una consumption policy.

Si un contrato declara calidad, debe remitir a evidencia y validators.

Si un contrato declara una capa promovida, debe poder apuntar a registry, schema y evidencia.

## Tipos de contratos actuales

La carpeta contiene varios tipos de documentos.

### Dataset raw o core

Contratos para datasets base observados o canonicos del modulo.

Ejemplos:

- `daily_dataset_contract_v0_1.md`
- `quotes_dataset_contract_v0_1.md`
- `trades_dataset_contract_v0_1.md`
- `ohlcv_1m_raw_dataset_contract_v0_1.md`

Estos contratos deben ser especialmente claros sobre:

- unidad semantica;
- vista de precio nativa;
- sesion;
- lineage historico;
- quality policy;
- coverage;
- consumers no implicados;
- y limitaciones.

### Derived price views

Contratos para capas derivadas de precio.

Ejemplos:

- `daily_adjusted_dataset_contract_v0_1.md`
- `ohlcv_1m_split_normalized_dataset_contract_v0_1.md`

Estos contratos deben distinguir:

- raw vs adjusted;
- raw vs split-normalized;
- vista diagnostica vs vista canonica;
- fuente upstream;
- transformacion canonica;
- campos derivados;
- materializacion;
- promocion;
- y consumidores permitidos.

Regla:

- una capa derivada no queda promovida solo porque existan parquets; requiere evidencia, validacion y registry.

### Labels

Contratos para capas de target/outcome.

Ejemplo:

- `daily_return_labels_dataset_contract_v0_1.md`

Estos contratos deben distinguir:

- labels como `y`;
- features como `X`;
- availability temporal;
- source view obligatoria;
- leakage;
- estado piloto vs full-universe;
- y condiciones de promocion futura.

Regla:

- un label forward-looking nunca debe consumirse como feature disponible en decision time.

### Features / states

Contratos para capas derivadas de atributos o estados.

Ejemplo:

- `intraday_regime_features_dataset_contract_v0_1.md`

Estos contratos deben distinguir:

- feature/state research;
- consumidor piloto;
- upstream normalizado;
- scope;
- coverage;
- leakage;
- y madurez.

Regla:

- una feature layer piloto no es por si misma evidencia de edge ni autorizacion full-universe.

### Universes

Contratos para universos o capas de elegibilidad.

Ejemplo:

- `lt1b_universe_dataset_contract_v0_1.md`

Estos contratos deben distinguir:

- ticker membership;
- ventana temporal;
- PTI;
- expected coverage;
- y limitaciones frente a membership diaria fully point-in-time.

Regla:

- un universo puede ayudar a definir `expected`, pero no decide por si solo `present`, `healthy` ni `usable`.

### Auxiliary / contextual datasets

Contratos para familias de soporte.

Ejemplos:

- `additional_dataset_contract_v0_1.md`
- `short_dataset_contract_v0_1.md`
- `short_review_dataset_contract_v0_1.md`

Estos contratos deben declarar:

- source scope;
- subfamilias;
- provenance;
- limitaciones;
- relacion con features o eventos;
- y consumidores restringidos.

Regla:

- un dataset contextual no queda automaticamente habilitado como feature productiva o input de backtest core.

## Estructura actual

La carpeta contiene actualmente:

```text
contract_registry/dataset_contracts/
  additional_dataset_contract_v0_1.md
  daily_adjusted_dataset_contract_v0_1.md
  daily_dataset_contract_v0_1.md
  daily_label_taxonomy_and_cut_policy.md
  daily_return_labels_dataset_contract_v0_1.md
  intraday_regime_features_dataset_contract_v0_1.md
  lt1b_universe_dataset_contract_v0_1.md
  ohlcv_1m_raw_dataset_contract_v0_1.md
  ohlcv_1m_split_normalized_dataset_contract_v0_1.md
  quotes_dataset_contract_v0_1.md
  quotes_label_taxonomy_and_cut_policy.md
  short_dataset_contract_v0_1.md
  short_review_dataset_contract_v0_1.md
  trades_dataset_contract_v0_1.md
  trades_label_taxonomy_and_cut_policy.md
```

## Lectura por documento actual

### `daily_dataset_contract_v0_1.md`

Contrato institucional de `daily_core_v0_1`.

Fija:

- barras `ticker-day`;
- autoridad primaria en OHLCV y coverage;
- `vw` como capa secundaria de diagnostico;
- ejes separados de calidad y coverage;
- estados finales como `good`, `recoverable_without_penalty`, `recoverable_with_flag`, `review_not_rehabilitated`, `bad`;
- consumers permitidos y restringidos;
- relacion con price semantics y external comparison caveats.

### `daily_label_taxonomy_and_cut_policy.md`

Politica exacta de taxonomia y corte de `daily`.

Fija:

- unidad `ticker-year file`;
- senales upstream;
- buckets de calidad;
- thresholds literales;
- coverage taxonomy;
- y traduccion de `review` historico a `recoverable_with_flag` contractual.

### `daily_adjusted_dataset_contract_v0_1.md`

Contrato de `daily_adjusted`.

Fija:

- vista economica diaria;
- continuidad comparable para retornos multi-dia;
- secuencia `daily_raw -> split_normalized -> adjusted`;
- campos derivados;
- provenance minima;
- consumidores para backtest diario, benchmark, labels y research;
- no uso para ejecucion, microestructura o tape observado.

### `daily_return_labels_dataset_contract_v0_1.md`

Contrato de labels diarios.

Fija:

- `daily_return_labels_v0_1`;
- fuente obligatoria `daily_adjusted`;
- columna obligatoria `c_adjusted`;
- labels `ret_1d`, `ret_3d`, `ret_5d`;
- estado piloto;
- no full-universe;
- regla anti-contaminacion `y` vs `X`;
- y condiciones de promocion futura.

### `quotes_dataset_contract_v0_1.md`

Contrato institucional de `quotes_core_v0_1`.

Fija:

- libro observado `bid/ask`;
- unidad `ticker-session` / observacion de quote;
- session scope `04:00-20:00 America/New_York`;
- separacion entre calidad local del libro y contexto externo;
- estados `good`, `review`, `bad`;
- consumers permitidos y no implicados;
- y limitaciones de external adjusted comparison.

### `quotes_label_taxonomy_and_cut_policy.md`

Politica exacta de taxonomia y corte de `quotes`.

Fija:

- unidad `ticker, date, file`;
- familias buenas, review y bad;
- regla de que contexto causal puede explicar pero no rehabilita automaticamente;
- y lectura local del libro como autoridad primaria.

### `trades_dataset_contract_v0_1.md`

Contrato institucional de `trades`.

Fija:

- `trades_raw` como observed execution tape;
- no uso como serie economica diaria generica;
- jerarquia historica de auditoria/certificacion/foundations;
- unidad file-level y raw row-level;
- price semantics, session basis y size basis;
- closeout `57f`;
- labels file-level;
- estados finales `good`, `recoverable_with_flag`, `review_not_rehabilitated`, `bad`;
- y regla de no tratar todo desacuerdo con `daily`/`1m` como bad tape.

### `trades_label_taxonomy_and_cut_policy.md`

Politica de taxonomia y corte de `trades`.

Fija:

- familias de `trades`;
- significado de buckets;
- relacion con final certification semantics;
- rehabilitacion;
- y separacion entre label tecnico y autorizacion final de pipeline.

### `ohlcv_1m_raw_dataset_contract_v0_1.md`

Contrato de `ohlcv_1m_raw`.

Debe leerse como raw intraday layer entendida institucionalmente, no como capa globalmente limpia para todos los consumidores.

Fija:

- raw one-minute OHLCV;
- alcance `<1B>` cuando aplique;
- relacion con `ohlcv_1m_split_normalized`;
- limites de raw frente a splits;
- policy/validators/dossiers asociados.

### `ohlcv_1m_split_normalized_dataset_contract_v0_1.md`

Contrato de `ohlcv_1m_split_normalized`.

Fija:

- capa derivada split-normalized;
- comparabilidad cross-session a traves de splits;
- no sustitucion de verdad local intradia raw cuando no toca;
- estado de piloto/full-universe segun evidencia;
- y relacion con feature layers downstream.

### `intraday_regime_features_dataset_contract_v0_1.md`

Contrato de capa de features/states.

Fija:

- features de contexto intradia;
- consumidor piloto validado de `ohlcv_1m_split_normalized`;
- preguntas de contexto;
- no evidencia de alpha;
- no uso full-universe sin promocion.

### `lt1b_universe_dataset_contract_v0_1.md`

Contrato de universo `<1B>`.

Fija:

- corte operativo transversal;
- tickers;
- ventana PTI;
- uso para expected coverage;
- no equivalencia con membership diaria fully PTI por market cap.

### `additional_dataset_contract_v0_1.md`

Contrato del bloque `additional`.

Fija:

- familias auxiliares;
- rol contextual;
- source scope;
- relacion con features/eventos;
- y restricciones de consumo.

### `reference_dataset_contract_v0_1.md`

Contrato institucional de `reference_v0_1`.

Fija:

- identidad, snapshots, events, splits, dividends, exchanges y ticker types;
- raiz operativa actual `E:/TSIS/data/reference`;
- relacion con price views, universe builder, event overlays y auditoria de market data;
- estados `good`, `review` y `bad_unresolved_identity`;
- y restriccion explicita de backtest, ML, execution, live y RL hasta contrato posterior.

### `short_dataset_contract_v0_1.md`

Contrato de `short`.

Fija:

- datos short como capa util pero certification-bound;
- estados de certificacion;
- ventanas limitadas;
- ticker reuse;
- reference conflicts;
- y relacion con `short_review`.

### `short_review_dataset_contract_v0_1.md`

Contrato de `short_review`.

Fija:

- capa official/free baseline/provenance;
- uso para validacion de fuente y coverage comparison;
- no sustitucion silenciosa de `short`;
- y no feature productiva por defecto.

## Campos recomendados para dataset contracts

Todo contrato nuevo o revisado deberia tender a cubrir:

```text
1. dataset_identity
2. status
3. purpose
4. semantic_scope
5. source_lineage
6. schema
7. price_semantics, si aplica
8. session_scope, si aplica
9. coverage
10. quality_policy
11. allowed_consumers
12. validators
13. known_limitations
14. change_policy
15. conclusion operacional
```

No todos los contratos necesitan la misma longitud.

Pero todos deben dejar claro que representan y que no representan.

## Campos recomendados para taxonomy/cut policies

Una taxonomy/cut policy deberia cubrir:

```text
1. rol
2. fuentes de autoridad
3. unidad exacta de decision
4. ejes separados de politica
5. senales upstream
6. buckets intermedios
7. umbrales o reglas literales
8. etiqueta final
9. traduccion al vocabulario contractual
10. consumidores afectados o referencias a consumption policy
11. validators relacionados
12. limites y errores metodologicos que evita
```

Regla:

- si una taxonomia clasifica objetos, debe declarar la unidad exacta de decision.

No es lo mismo:

- ticker;
- ticker-day;
- ticker-year file;
- ticker-date-file;
- raw row;
- file-level audit row;
- month parquet;
- feature row;
- label row.

## Homogeneidad y compatibilidad

Los contratos existentes no deben reescribirse masivamente solo por estetica.

La carpeta evoluciono por dominios y algunos documentos usan estilos distintos.

La estrategia correcta es:

- mantener compatibilidad historica;
- mejorar homogeneidad cuando se toque un contrato por una razon real;
- no mezclar refactor editorial con cambio semantico;
- y versionar cuando cambie la meaning institucional.

## Criterios para crear un contrato nuevo

Debe crearse un contrato cuando:

- un dataset pasa de exploratorio a institucional/provisional/validated;
- una capa derivada se materializa para consumo repetible;
- una price view queda promovida;
- un universo gobierna expected coverage;
- una label layer se crea como target;
- una feature layer pasa a research sistematico;
- una familia auxiliar empieza a afectar backtest/ML/eventos;
- o una taxonomia de calidad queda estabilizada.

No debe crearse contrato para:

- un notebook aislado;
- un parquet temporal;
- un output sin semantica estable;
- una imagen de dossier;
- una muestra puntual sin scope reproducible;
- o una carpeta que solo existe en disco pero no tiene decision institucional.

## Checklist antes de declarar un contrato institucional

Antes de marcar un contrato como institucional:

1. Identidad logica estable.
2. Dominio y version definidos.
3. Purpose claro.
4. Semantica y out-of-scope claros.
5. Lineage y evidencia enlazados.
6. Schema canonico o equivalente enlazado.
7. Coverage o scope cuantitativo declarado.
8. Quality policy definida.
9. Consumers permitidos/restringidos referenciados.
10. Consumption policy enlazada si hay uso downstream.
11. Validators requeridos enlazados.
12. Registry entry existente o prevista.
13. Inspection dossier o evidencia trazable.
14. Known limitations explicitas.
15. Change policy definida.

Si faltan varias de estas piezas, el contrato debe permanecer provisional o piloto.

## Checklist de modificacion

Al modificar un contrato:

1. Determinar si el cambio es editorial, operacional o semantico.
2. Si cambia identidad, versionar.
3. Si cambia semantica, revisar schema, policy, registry y validators.
4. Si cambia consumers, revisar consumption policy.
5. Si cambia quality/taxonomy, revisar cut policy y validators.
6. Si cambia coverage/universe, revisar registry e inspection dossier.
7. Si cambia price view, revisar price semantics y pipeline price view policy.
8. Si cambia estado de promocion, revisar evidence y changelog.
9. Si afecta downstream, registrar impacto.

## Errores que debe evitar esta carpeta

No debe ocurrir que:

- un dataset se declare institucional sin evidencia;
- un contrato contradiga su consumption policy;
- un contract permita consumidores que la policy no permite;
- una taxonomy no declare unidad de decision;
- un raw tape se trate como adjusted economic series;
- una capa piloto parezca full-universe;
- un label parezca feature;
- un universo parezca prueba de calidad;
- una comparison externa ignore price semantics;
- o un cambio de meaning se haga sin versionar.

## Relacion con `CHANGELOG.md`

Debe registrarse cambio cuando:

- se crea un contrato nuevo;
- cambia `promotion_state`;
- cambia `contract_type`;
- cambia identidad o version;
- cambia semantica;
- cambia allowed consumers;
- cambia quality policy o taxonomy;
- cambia coverage o universo;
- cambia price view;
- cambia validators requeridos;
- o se depreca/archiva un contrato.

Cambios editoriales menores o enlaces sin impacto semantico pueden no requerir entrada propia.

## Regla final

Un dataset no esta institucionalmente definido porque exista en disco, tenga schema o aparezca en un notebook.

Esta institucionalmente definido cuando tiene contrato, semantica estable, evidencia trazable, policy de consumo, schema/validators, registry y limites conocidos.

`dataset_contracts/` es la capa que fija esa definicion.
