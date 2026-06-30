# Data Foundation Graphify and Table Design Protocol

## Estado

Tipo: module contract transversal.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: CAPA 1 - Data Foundation.

Este documento gobierna como usar Graphify para entender `01_foundations` y
`00_data_certification` antes de disenar tablas institucionales.

La operacion de build y refresco vive en:

```text
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Este documento define metodologia de scope y criterios de tabla. No sustituye
el protocolo operativo de build.

## Objetivo

Evitar que futuros agentes definan tablas de CAPA 1 solo desde:

- una conversacion;
- una intuicion arquitectonica;
- un `README` de alto nivel;
- o un grafo gigante sin separacion semantica.

La pregunta correcta no es:

```text
Que tablas suenan razonables?
```

La pregunta correcta es:

```text
Que tablas quedan justificadas por contratos, certificacion, evidencia y datos
fisicos reales?
```

## Jerarquia de autoridad

Para CAPA 1, la jerarquia practica es:

1. contratos raiz TSIS y reglas locales del modulo;
2. `01_foundations/module_contracts/`;
3. `01_foundations/contract_registry/dataset_contracts/`;
4. `01_foundations/canonical_schemas/`;
5. `01_foundations/dataset_registry/`;
6. `01_foundations/data_consumption_policies/`;
7. `01_foundations/validators/`;
8. `01_foundations/inspection_dossiers/`;
9. `01_research/01_auditoria_RAW_DATA/00_data_certification/`;
10. outputs runtime y datos fisicos.

`00_CTO` define arquitectura objetivo y lenguaje de sistema.

`01_foundations` define autoridad operativa para datos, contratos, schemas,
registries, policies y validators.

`00_data_certification` preserva auditoria, diagnostico, closeouts y decisiones
de certificacion que deben ser promovidas con cuidado hacia `01_foundations`.

## Reglas no negociables

No hacer:

```text
graphify 01_foundations
graphify 01_research/01_auditoria_RAW_DATA/00_data_certification
graphify 01_TSIS_backtest_SmallCaps
```

como primer paso.

Esos scopes son demasiado amplios y mezclan:

- contratos;
- schemas;
- evidencia;
- imagenes;
- notebooks;
- parquet;
- CSV;
- scripts;
- runtime;
- y material historico preservado.

Tampoco hacer:

```text
tabla propuesta por arquitectura -> contrato final
```

sin pasar por certificacion y profiling fisico.

## Regla oficial Graphify

Un grafo solo se considera Graphify oficial si lo genero el flujo oficial de
Graphify.

Flujos aceptados:

- `$graphify <path>` desde Codex con la skill Graphify activa;
- `graphify <path>` desde CLI;
- `graphify <path> --update` cuando exista manifest compatible y el scope no
  haya cambiado;
- `graphify merge-graphs ...` u otro merge oficial si la version instalada lo
  soporta.

Prohibido:

- escribir `graphify-out/graph.json` manualmente;
- crear un JSON compatible y llamarlo Graphify oficial;
- mezclar outputs viejos con corpus nuevo sin manifest;
- usar `graphify-out/` como source of truth.

### Modo sin APIs y cobertura semantica

TSIS no asume APIs externas disponibles para Graphify.

Para corpus documentales de CAPA 1, el modo oficial sin APIs es:

```text
skill Graphify activa
-> AST local para codigo
-> subagentes/host agent para documentos, papers e imagenes
-> build con root del scan
-> diagnostics
-> BUILD_MANIFEST con version, corpus y cobertura.
```

Un `graphify update` CLI code-only o AST-only no basta para sostener decisiones
sobre tablas cuando cambiaron markdown, contratos, schemas, policies,
certification docs, papers o imagenes. En ese caso el agente debe ejecutar el
flujo semantico de la skill Graphify, o un `graphify extract` oficial con
backend ya configurado. Si no existen backend ni subagentes disponibles, el
resultado debe quedar bloqueado como `pending_semantic_graph_refresh`.

El `BUILD_MANIFEST.md` usado para justificar una tabla debe declarar como
minimo:

- `graphify_package_version`;
- `graphify_skill_version_or_source`;
- `graphify_upstream_reference`;
- `no_api_mode`;
- `semantic_extraction_mode`;
- `build_from_json_root_or_equivalent`;
- `semantic_update_coverage`.

## Runtime reconstruible

`graphify-out/` es runtime reconstruible.

TSIS lo ignora por Git salvo promocion explicita. Por tanto, la memoria
versionada debe ser el protocolo y, cuando proceda, un build manifest ligero.

Un build manifest promovido debe declarar:

- graph name;
- objetivo;
- fecha;
- commit;
- version de Graphify;
- corpus incluido;
- corpus excluido;
- flags usados;
- ruta de output runtime;
- si es full rebuild o update;
- y limitaciones conocidas.

## Grafos independientes requeridos

Los nombres de esta seccion no son carpetas fisicas.

Son nombres de builds/slices oficiales de Graphify. Un slice puede incluir
archivos de varias carpetas reales. El objetivo es cubrir `01_foundations` por
capas semanticas, no escanear todo el arbol de una vez.

El grafo raiz esperado, si llega a construirse, es:

```text
data_foundation_root_graph
```

Ese root debe nacer de leaves oficiales, no de un primer escaneo monolitico.

### 1. `foundations_authority_graph`

Objetivo:

Mapear autoridad contractual viva de CAPA 1.

Corpus principal:

```text
01_foundations/module_contracts/
01_foundations/contract_registry/dataset_contracts/
01_foundations/canonical_schemas/
01_foundations/dataset_registry/
01_foundations/data_consumption_policies/
01_foundations/validators/
```

Excluir por defecto:

```text
01_foundations/inspection_dossiers/
graphify-out/
evidence_assets/
*.parquet
*.csv
*.png
*.jpg
*.jpeg
*.webp
*.ipynb
```

Uso:

- descubrir que contrato gobierna cada dataset;
- encontrar conflictos entre schema, policy, registry y validator;
- identificar huecos antes de disenar tablas maestras.

### 2. `certification_decisions_graph`

Objetivo:

Mapear decisiones finales de auditoria/certificacion.

Corpus principal:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/*/*closeout*.md
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/*/*policy*.md
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/*/*contrato*.md
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/*.md
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/*.json
```

Excluir por defecto:

```text
*.parquet
*.csv
*.png
*.jpg
*.jpeg
*.webp
*.ipynb
cache*/
img/
```

Uso:

- distinguir `expected`, `present`, `healthy`, `usable_for`;
- entender recovery y exclusion;
- detectar si `01_foundations` simplifica demasiado una decision historica.

### 3. `reference_identity_graph`

Objetivo:

Mapear identidad temporal, universo, ticker lifecycle, corporate actions y
semantica de referencia.

Corpus:

```text
01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md
01_foundations/canonical_schemas/reference/
01_foundations/dataset_registry/reference/
01_foundations/data_consumption_policies/reference_consumption_policy.md
01_foundations/validators/reference/
01_foundations/module_contracts/corporate_actions_adjustment_methodology.md
01_foundations/module_contracts/event_families_and_reference_inventory.md
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/*closeout*.md
```

Uso:

- justificar `instrument_master` o equivalente;
- justificar `corporate_actions_table`;
- evitar survivorship bias;
- evitar confundir ticker actual con identidad economica temporal.

### 4. `daily_ohlcv_graph`

Objetivo:

Mapear daily, OHLCV 1m, sesiones, price views y split normalization.

Corpus:

```text
01_foundations/contract_registry/dataset_contracts/daily*_contract*.md
01_foundations/contract_registry/dataset_contracts/ohlcv_1m*_contract*.md
01_foundations/canonical_schemas/daily/
01_foundations/canonical_schemas/ohlcv_1m/
01_foundations/dataset_registry/daily/
01_foundations/dataset_registry/ohlcv_1m/
01_foundations/data_consumption_policies/daily_consumption_policy.md
01_foundations/data_consumption_policies/ohlcv_1m_raw_consumption_policy.md
01_foundations/validators/daily/
01_foundations/validators/ohlcv_1m/
01_foundations/module_contracts/market_session_scope.md
01_foundations/module_contracts/price_semantics_and_adjustment_policy.md
01_foundations/module_contracts/price_views_registry.md
01_foundations/module_contracts/pipeline_price_view_policy.md
```

Uso:

- justificar `master_daily_table`;
- justificar `master_intraday_bar_table`;
- decidir raw, split-normalized, adjusted proxy o adjusted;
- preservar comparabilidad temporal.

### 5. `microstructure_quotes_trades_graph`

Objetivo:

Mapear quotes/trades como capas microestructurales gobernadas, no como master
tables simples.

Corpus:

```text
01_foundations/contract_registry/dataset_contracts/quotes*_contract*.md
01_foundations/contract_registry/dataset_contracts/trades*_contract*.md
01_foundations/canonical_schemas/quotes/
01_foundations/canonical_schemas/trades/
01_foundations/dataset_registry/quotes/
01_foundations/dataset_registry/trades/
01_foundations/data_consumption_policies/quotes_consumption_policy.md
01_foundations/data_consumption_policies/trades_consumption_policy.md
01_foundations/validators/quotes/
01_foundations/validators/trades/
01_foundations/module_contracts/market_session_scope.md
01_foundations/module_contracts/price_semantics_and_adjustment_policy.md
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/
```

Uso:

- decidir que queda como raw governed source;
- decidir que se promueve a microstructure features;
- evitar crear `master_quotes_table` o `master_trades_table` sin necesidad real;
- separar ejecucion, diagnostico y alpha.

### 6. `additional_fundamentals_news_graph`

Objetivo:

Mapear fundamentals, ratios, news, IPOs, economic y corporate actions externos
con semantica `as-of`.

Corpus:

```text
01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md
01_foundations/canonical_schemas/additional/
01_foundations/canonical_schemas/financial/
01_foundations/dataset_registry/additional/
01_foundations/data_consumption_policies/additional_consumption_policy.md
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/additional/
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/*closeout*.md
```

Uso:

- justificar `fundamentals_asof_table`;
- separar financial statements de ratios;
- controlar leakage por filing date, period end y publication time;
- no tratar news o macro como causalidad ticker-level por defecto.

## Diseno de tablas: flujo obligatorio

Antes de crear o promover una tabla de CAPA 1, seguir este flujo:

1. Identificar la pregunta institucional que responde.
2. Consultar `foundations_authority_graph`.
3. Consultar el grafo de certificacion o familia correspondiente.
4. Leer los contratos exactos enlazados por el grafo.
5. Perfilar fisicamente parquet/CSV reales.
6. Declarar grain canonico.
7. Declarar keys.
8. Declarar as-of semantics.
9. Declarar price semantics.
10. Declarar universe scope.
11. Declarar expected/present/healthy/usable logic.
12. Definir schema.
13. Definir registry entry.
14. Definir consumption policy.
15. Definir validator minimo.
16. Registrar changelog si altera consumo o semantica.

Sin esos pasos, una tabla puede ser propuesta, pero no promovida.

## Clasificacion de tablas

Toda tabla candidata debe clasificarse como una de estas:

```text
source governed table
reference/context table
certification/quality table
analytical master table
derived feature table
execution/microstructure table
forensic evidence table
```

No mezclar clases.

Ejemplo:

- `master_daily_table` es analytical master table.
- `master_intraday_bar_table` es analytical master table.
- `instrument_master` es reference/context table.
- `corporate_actions_table` es reference/context table.
- `market_calendar` es reference/context table.
- `dataset_certification_matrix` es certification/quality table.
- `quotes` y `trades` son source governed tables.
- microstructure features derivadas de quotes/trades son derived feature tables.

## Hipotesis actuales, no contratos finales

Las siguientes entidades estan justificadas como hipotesis de trabajo, pero no
quedan promovidas por este documento:

```text
instrument_master
corporate_actions_table
market_calendar
expected_data_calendar
master_daily_table
master_intraday_bar_table
dataset_certification_matrix
fundamentals_asof_table
microstructure_features
execution_features
```

`symbol_master` no debe adoptarse sin revisar nombre. El nombre preferido para
discusion es `instrument_master`, porque ticker/symbol es una etiqueta temporal,
no la identidad economica completa.

## Quotes y trades

No asumir que deben existir como `master_quotes_table` y
`master_trades_table`.

Quotes y trades son de alta granularidad, alto volumen y semantica distinta a
daily/OHLCV.

La ruta correcta por defecto es:

```text
quotes_core / trades_core
  -> certificacion y filtros
  -> microstructure_features / execution_features
  -> joins controlados hacia master intraday si procede
```

Solo crear una master table de quotes/trades si existe:

- consumidor claro;
- grain estable;
- coste operativo defendible;
- policy de calidad;
- schema;
- validator;
- y razon para no mantenerlo como source layer + feature layer.

## Fundamentals, news y additional

No volcar fundamentals o news dentro de `master_daily_table` sin semantica
`as-of`.

Regla:

```text
period_end != filing_date != publication_time != usable_asof_time
```

La tabla probable es `fundamentals_asof_table`, no una mezcla directa en daily.

News debe tratarse como contexto/evento con lag y fuente, no como verdad causal
ticker-level por defecto.

## Profiling fisico obligatorio

Graphify no inspecciona exhaustivamente parquet/CSV como autoridad de datos.

Despues del grafo, todo diseno de tabla debe ejecutar profiling fisico:

```text
row count
column names
types
primary key candidates
duplicate rates
null rates
min/max dates
ticker coverage
session coverage
file roots
partition layout
sample rows
known bad/review/good overlap
```

El profiling debe declarar path fisico y, si aplica, run id o manifest.

## Severidad Graphify

Graphify no se actualiza por cada commit.

Clasificacion:

```text
LOW      -> no actualizar Graphify
MEDIUM   -> anotar en cola/manifest futuro
HIGH     -> reconstruir leaf graph afectado
CRITICAL -> reconstruir leaf y revisar merges/consumidores
```

Ejemplos `HIGH`:

- nuevo dataset contract;
- cambio de schema canonico;
- cambio de consumption policy;
- cambio de validator que altere aceptacion;
- cambio de certificacion final;
- nuevo master table contract.

## Criterio de aceptacion para tablas CAPA 1

Una tabla de CAPA 1 no queda aceptada hasta que tenga:

- nombre canonico;
- clase de tabla;
- grain;
- keys;
- schema;
- source lineage;
- quality/certification semantics;
- as-of semantics si aplica;
- price semantics si aplica;
- universe scope;
- registry entry;
- consumption policy;
- validator minimo;
- changelog si cambia consumo institucional;
- y evidencia/profiling que justifique que se puede materializar.

## Prompt recomendado para futuros agentes

```text
Actualiza o construye el mapa Graphify para CAPA 1 Data Foundation.

Antes de ejecutar Graphify:
- Lee AGENTS.md, PROJECT_* docs, VERSIONING_STANDARDS.md y LOCAL_RULES.md.
- Lee 01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md.
- Lee 01_foundations/GRAPHIFY_REFRESH_QUEUE.md.
- Lee 01_foundations/module_contracts/graphify/README.md.
- Lee este protocolo.
- No construyas un grafo unico gigante.
- Selecciona el slice correspondiente.
- Usa solo flujos oficiales de Graphify.
- No escribas graph.json manualmente.
- Trata graphify-out/ como runtime reconstruible.
- Despues del grafo, no propongas tablas sin profiling fisico de datos.
```

## Regla final

Graphify ayuda a navegar relaciones documentales.

La autoridad institucional nace cuando:

```text
contrato + certificacion + evidencia + profiling fisico + validator
```

coinciden.

Hasta entonces, una tabla es solo una hipotesis de diseno.
