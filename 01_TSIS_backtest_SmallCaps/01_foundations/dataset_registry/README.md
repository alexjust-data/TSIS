# Dataset Registry

## Rol de esta carpeta

`dataset_registry/` es el registro operativo de datasets, vistas y capas promovidas o materializadas dentro del modulo 01.

Su funcion principal es responder:

- que dataset existe institucionalmente;
- como se llama su identidad logica;
- donde vive fisicamente;
- que estado de promocion tiene;
- que contrato lo gobierna;
- que schema lo describe;
- que policy de consumo aplica;
- que validators lo protegen;
- que evidencia sostiene su estado;
- y que lineage o dependencias deben conocerse antes de consumirlo.

Esta carpeta no define por si sola la semantica completa del dataset.

La semantica vive en los contratos, schemas, policies y dossiers enlazados desde cada entry.

## Autoridades relacionadas

El `dataset_registry` debe leerse junto con:

- `01_foundations/module_contracts/operational_boundaries.md`
- `01_foundations/module_contracts/promotion_pipeline.md`
- `01_foundations/module_contracts/dataset_contract_template.md`
- `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
- `01_foundations/module_contracts/naming_authority.md`
- `01_foundations/module_contracts/state_snapshot_standard.md`
- `01_foundations/contract_registry/dataset_contracts/`
- `01_foundations/data_consumption_policies/`
- `01_foundations/canonical_schemas/`
- `01_foundations/validators/`
- `01_foundations/inspection_dossiers/`

Regla de autoridad:

- el dataset contract define que es el dataset;
- el schema define su forma;
- la consumption policy define como puede consumirse;
- los validators definen que debe comprobarse;
- el inspection dossier muestra por que el estado es defendible;
- el registry entry localiza y conecta todo lo anterior.

## Que es una registry entry

Una registry entry es una ficha operativa versionada de un dataset o capa.

Debe permitir que un humano o agente pueda localizar y evaluar un dataset sin depender de memoria conversacional.

Una registry entry debe contestar, cuando aplique:

- identidad logica;
- dominio;
- version;
- estado institucional;
- si esta activa;
- familia de dataset;
- unidad primaria;
- raiz fisica;
- patron de layout;
- fuentes upstream;
- contrato aplicable;
- schema aplicable;
- policy de consumo;
- validators;
- evidencia de auditoria o promocion;
- coverage snapshot;
- limites conocidos;
- consumidores permitidos o restringidos;
- y notas operativas.

## Que no es esta carpeta

`dataset_registry/` no es:

- una carpeta de datos raw;
- un lugar para guardar parquets pesados;
- un sustituto del contrato de dataset;
- un sustituto de `canonical_schemas`;
- un sustituto de `data_consumption_policies`;
- un sustituto de `inspection_dossiers`;
- ni una lista informal de paths.

Una ruta fisica sin contrato no convierte un dataset en institucional.

Un contrato sin registry puede describir semantica, pero deja debil la localizacion operativa.

Un registry sin evidencia o policy no debe usarse como autorizacion de consumo productivo.

## Relacion con promocion

El registry participa en el pipeline:

```text
exploratory -> provisional -> validated -> institutional -> deprecated -> archived
```

Tambien puede reflejar estados mas especificos cuando el proyecto ya los ha fijado, por ejemplo:

- `institutional`;
- `draft_institutionalized`;
- `full_universe_promoted`;
- `institutional_raw_closeout_reconciled_lt1b`;
- `pilot`;
- `active`;
- `deprecated`;
- `archived`.

El estado de promocion no debe inventarse por comodidad local.

Debe estar respaldado por:

- evidencia;
- contrato;
- validacion;
- trazabilidad;
- y policy de consumo.

## Relacion con almacenamiento fisico

El registry es el puente entre la capa institucional y la topologia fisica.

Debe declarar, cuando aplique:

- raiz canonica;
- raiz raw;
- raiz derivada;
- layout esperado;
- particiones observadas;
- representative file;
- source root;
- materializer script;
- o run artifact activo.

Ejemplos de roles fisicos:

- `D:/...` puede ser fuente raw o materializacion operativa pesada;
- `E:/TSIS/data/...` puede ser landing operativo promovido;
- `C:/TSIS_Data/data/...` puede contener familias de soporte o fuentes auxiliares;
- `runs/...` puede contener caches o closeouts historicos activos;
- `01_foundations/...` contiene contratos, policies, schemas, validators, dossiers y registry, no datos pesados.

Regla critica:

- dos carpetas con nombres parecidos no implican la misma semantica.

El registry debe ayudar a distinguir:

- raw;
- adjusted;
- split-normalized;
- derived feature;
- label;
- universe;
- support/reference;
- y provenance.

## Relacion con `expected`, `present`, `healthy` y `usable`

Para datasets de mercado, universo o coverage, el registry puede incluir snapshots o referencias que permitan razonar sobre:

- `expected`;
- `present`;
- `healthy`;
- `usable`.

Estas palabras no son intercambiables.

- `expected` depende del universo, ventana temporal y semantica del dataset.
- `present` significa que el objeto o file existe.
- `healthy` significa que supera condiciones de calidad definidas.
- `usable` significa que puede consumirse bajo una policy concreta.

Un file presente no es automaticamente usable.

Un ticker miembro de un universo no implica que todos sus dias, meses o eventos sean esperados.

Para claims `<1B>`, debe declararse la referencia de universo y la interseccion temporal o PTI aplicable.

## Registry entries vs manifests

Esta carpeta contiene dos tipos de artefactos relacionados pero distintos.

### Registry entries

Son fichas institucionales de dataset o capa.

Normalmente aparecen como:

```text
<dataset>_registry_entry.yaml
```

Su funcion es describir el dataset o capa como activo registrado.

### Manifests

Son listas versionadas de casos, pilotos, tickers, meses, files o unidades de inspeccion.

Pueden aparecer como:

```text
*_manifest_v0_1.csv
*_manifest_v0_2.csv
*_manifest_v0_1.md
```

Su funcion es fijar una muestra, piloto o scope reproducible.

Un manifest no es por si solo un registry entry.

Un registry entry puede enlazar manifests cuando estos forman parte de evidencia, piloto, materializacion o lineage.

## Estructura actual

La estructura actual de la carpeta incluye:

```text
dataset_registry/
  additional/
  daily/
  features/
  ohlcv_1m/
  quotes/
  short/
  short_review/
  trades/
  universes/
```

### `additional/`

Registra la familia `additional`, incluyendo subfamilias de soporte como corporate actions, economic, financials, ipos y news cuando aplican al estado institucional del bloque.

Debe leerse junto con:

- `contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md`
- `data_consumption_policies/additional_consumption_policy.md`
- `canonical_schemas/additional/`
- `inspection_dossiers/additional/`

### `daily/`

Registra datasets y capas del dominio daily.

Incluye:

- `daily_registry_entry.yaml`
- `daily_adjusted_registry_entry.yaml`
- `daily_return_labels_registry_entry.yaml`
- manifests de piloto de `daily_adjusted`

Este dominio separa:

- `ohlcv_daily` raw;
- `ohlcv_daily_adjusted` como price view derivada;
- y `daily_return_labels` como capa de labels.

No deben mezclarse sus estados de promocion.

### `features/`

Registra capas derivadas de features, por ejemplo:

- `intraday_regime_features_registry_entry.yaml`

Estas capas no son datos raw.

Deben declarar:

- upstream;
- semantica de feature;
- scope;
- estado de madurez;
- consumer contract;
- y limites de consumo.

### `ohlcv_1m/`

Registra el dominio intraday minute.

Incluye:

- `ohlcv_1m_raw_registry_entry.yaml`
- `ohlcv_1m_split_normalized_registry_entry.yaml`
- manifests de piloto de `ohlcv_1m_split_normalized`

Debe distinguirse siempre:

- `ohlcv_1m_raw`;
- `ohlcv_1m_split_normalized`;
- piloto;
- auditoria full-universe;
- consumo real;
- y promocion.

Raw 1m no debe confundirse con split-normalized 1m.

### `quotes/`

Registra `quotes` como dataset de libro/quote tape.

Debe enlazar:

- contrato de dataset;
- taxonomia y cut policy;
- policy de consumo;
- schema;
- validators;
- inspection dossier;
- evidencia historica de auditoria.

En `quotes`, el registry no debe colapsar calidad local del libro con explicacion externa de eventos.

### `short/`

Registra la familia `short`.

Debe distinguir fuentes, snapshots y consumo gobernado frente a capas revisadas o provenance.

### `short_review/`

Registra `short_review` como capa/documentacion de revision y provenance relacionada con short data.

No debe confundirse automaticamente con una feature productiva.

Cuando aplique, manifests y logs quedan como provenance, no como features de modelo.

### `trades/`

Registra `trades` y sus closeouts/artefactos activos.

Es un dominio complejo porque debe separar:

- raw executed trade tape;
- notebooks historicos;
- run artifacts activos;
- closeout full;
- muestra metodologica;
- final labels;
- allowed consumers;
- y restricciones.

La registry entry de `trades` debe recordar que una muestra metodologica no reemplaza los conteos full-closeout.

### `universes/`

Registra universos institucionales, por ejemplo:

- `lt1b_universe_registry_entry.yaml`

Un universo registry no debe interpretarse automaticamente como membership diaria fully point-in-time por market cap si el contrato no lo dice.

Debe declarar:

- regla de construccion;
- alcance temporal;
- dependencias;
- limitaciones;
- y relacion con expected coverage de otros datasets.

## Campos recomendados

Aunque las entries actuales tienen cierta heterogeneidad historica, una registry entry madura deberia tender a cubrir estos bloques:

```yaml
dataset_identity:
  name:
  domain:
  logical_version:
  contract_type:

status:
  promotion_state:
  active:
  owner:

registry_classification:
  dataset_family:
  primary_unit:
  evidence_state:

artifacts:
  dataset_contract:
  consumption_policy:
  schema_contract:
  validators:
  inspection_dossier:

physical_layout:
  canonical_root:
  source_root:
  layout_pattern:
  representative_file:

source_lineage:
  upstream_sources: []
  transformation_summary:
  materializer_script:
  run_artifacts: []

scope:
  universe_reference:
  temporal_semantics:
  price_view:
  adjusted:
  split_adjusted:

coverage_snapshot:
  source:
  metrics: {}

quality_policy:
  states: []
  hard_exclusion_bucket:
  residual_handling:

allowed_consumers:
  permitted: []
  restricted: []
  prohibited: []

evidence_references: []

known_limitations: []

notes: []
```

No todos los datasets necesitan todos los campos.

Pero toda entry debe contestar las preguntas institucionales equivalentes.

## Homogeneidad y compatibilidad

Las entries existentes no deben reescribirse masivamente solo por estetica.

El objetivo es converger hacia homogeneidad sin romper trazabilidad historica.

Regla practica:

- si se crea una entry nueva, usar la estructura recomendada;
- si se toca una entry existente por cambio semantico, mejorarla hacia la estructura recomendada;
- si solo se corrige un link menor, no convertirlo en refactor masivo;
- si el cambio altera estado, consumo, raiz fisica, coverage o semantica, actualizar contratos/policies/dossiers relacionados y dejar trazabilidad.

## Criterios para crear una nueva registry entry

Debe crearse o actualizarse una registry entry cuando:

- un dataset pasa a tener contrato institucional;
- una capa derivada se materializa como activo reutilizable;
- una vista de precio queda promovida;
- un universo pasa a gobernar expected coverage;
- un label set queda disponible para consumo;
- un feature layer pasa de experimento a capa registrada;
- cambia la raiz fisica canonica;
- cambia el estado de promocion;
- cambia la policy de consumo;
- o se cierra una auditoria full-universe que modifica el estado operativo.

No debe crearse una registry entry para:

- un notebook exploratorio aislado;
- un CSV temporal;
- una imagen de dossier;
- un output sin contrato;
- una muestra sin semantica estable;
- o un experimento que no tenga intencion de consumo repetible.

## Checklist antes de declarar una entry activa

Antes de marcar una entry como activa o institucional, comprobar:

1. Existe dataset contract o documento equivalente.
2. Existe schema canonico cuando aplica.
3. Existe consumption policy cuando hay consumo downstream.
4. Existen validators o contrato de validacion cuando aplica.
5. Existe inspection dossier, closeout o evidencia trazable.
6. La raiz fisica existe o queda declarada como objetivo/landing.
7. El layout esta descrito.
8. El estado de promocion no exagera la evidencia.
9. Las restricciones de consumidor estan declaradas.
10. El lineage upstream esta claro.
11. El coverage snapshot tiene fuente o fecha/evidencia.
12. No contradice contratos vivos ni snapshots recientes.

## Checklist de modificacion

Al modificar una registry entry:

1. Identificar si el cambio es editorial u operativo.
2. Si cambia path fisico, revisar builders y consumers.
3. Si cambia estado de promocion, revisar evidence y changelog.
4. Si cambia allowed consumers, revisar consumption policy.
5. Si cambia schema, revisar canonical schema y validators.
6. Si cambia universo o scope, revisar expected coverage.
7. Si cambia una capa derivada, revisar maturity y layer validation.
8. Si se depreca algo, declarar sustituto o motivo.

## Errores que debe evitar esta carpeta

No debe ocurrir que:

- un registry entry apunte a paths obsoletos sin nota;
- un dataset figure activo sin contrato;
- un dataset figure promovido sin evidencia;
- una capa piloto parezca full-universe;
- una capa raw parezca adjusted;
- un feature layer parezca fuente primaria;
- un universo parezca membership diaria PTI si no lo es;
- manifests viejos se mezclen con manifests vigentes;
- o una entry contradiga su consumption policy.

## Relacion con `CHANGELOG.md`

Los cambios puramente editoriales de claridad pueden no requerir entrada propia.

Pero debe registrarse cambio cuando:

- se crea una registry entry institucional;
- cambia `promotion_state`;
- cambia `active`;
- cambia raiz fisica canonica;
- cambia allowed consumers;
- cambia coverage snapshot relevante;
- se promueve una capa full-universe;
- se depreca o archiva un dataset;
- o se corrige una inconsistencia que afectaba consumo.

## Regla final

Un dataset no esta institucionalmente localizable solo porque exista en disco.

Debe poder encontrarse en el registry, entenderse por contrato, validarse por schema/validators, consumirse por policy y defenderse por evidencia.

El registry es el indice operativo que conecta esas piezas.
