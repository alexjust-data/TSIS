# Certification Decisions Graph Protocol

## Estado

Tipo: graph slice protocol.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification
```

## Objetivo

Construir el primer leaf oficial de Graphify para decisiones de auditoria y
certificacion:

```text
certification_decisions_graph
```

Este grafo debe responder:

- que familias de datos fueron certificadas;
- que decisiones finales existen;
- que significan `expected`, `present`, `healthy` y `usable_for`;
- que familias quedaron `good`, `review`, `bad`, recuperables o excluidas;
- donde estan los closeouts y policies que justifican esas decisiones;
- que global metrics livianos resumen el estado de certificacion.

## No objetivo

Este leaf no debe:

- reescribir closeouts;
- reorganizar `auditoria/` o `certification/`;
- absorber notebooks;
- indexar imagenes o evidence assets;
- indexar parquet/CSV;
- tratar outputs runtime como source of truth;
- sustituir contratos vivos de `01_foundations`.

## Corpus principal

Incluir:

```text
certification/**/*.md
certification/global_metrics/*.json
auditoria/*/*closeout*.md
auditoria/*/*policy*.md
auditoria/*/*contrato*.md
auditoria/*/v*/*contrato*.md
```

Incluir tambien la gobernanza local Graphify:

```text
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
GRAPHIFY_REFRESH_QUEUE.md
module_contracts/graphify/README.md
module_contracts/graphify/certification_decisions_graph_protocol.md
```

## Exclusiones por defecto

Excluir:

```text
graphify-out/
module_contracts/graphify-out/
*.ipynb
*.parquet
*.csv
*.png
*.jpg
*.jpeg
*.webp
cache*/
img/
runtime/
run/
runs/
__pycache__/
.pytest_cache/
```

## Notebooks

Los notebooks deben preservarse y despues mapearse en:

```text
certification_notebook_evidence_graph
```

Ese leaf futuro debe capturar:

- que notebook existe;
- que auditoria o dataset investiga;
- que outputs o plots produce;
- que conclusion estable fue promovida;
- que queda como hipotesis o evidencia no promovida.

## Familias esperadas

El grafo debe reconocer, cuando existan documentos fuente:

```text
additional
daily
halts
ohlcv_1m
quotes
reference
short
trades
global_metrics
```

## Relaciones esperadas

Graphify debe capturar relaciones como:

```text
closeout -> certification decision
policy -> usable_for state
contract -> expected/present/healthy semantics
global metrics -> family status
recovery policy -> review/recoverable/exclusion buckets
certification decision -> downstream foundation contract
```

No inventar relaciones. Si una relacion es plausible pero no explicita, marcarla
como `INFERRED`. Si es incierta, marcarla como `AMBIGUOUS`.

## Criterios de aceptacion

Un build de este leaf queda aceptado solo si existen:

```text
graphify-out/leaf_slices/certification_decisions/graph.json
graphify-out/leaf_slices/certification_decisions/GRAPH_REPORT.md
graphify-out/leaf_slices/certification_decisions/graph.html
graphify-out/leaf_slices/certification_decisions/BUILD_MANIFEST.md
```

Y si pasan:

```text
graphify diagnose multigraph --graph graphify-out/leaf_slices/certification_decisions/graph.json
graphify explain "<nodo canonico>" --graph graphify-out/leaf_slices/certification_decisions/graph.json
```

## Impacto downstream

Este leaf no promueve tablas por si solo.

Sirve como mapa de evidencia para disenar o revisar:

```text
dataset_certification_matrix
instrument_master
corporate_actions_table
master_daily_table
master_intraday_bar_table
fundamentals_asof_table
microstructure_features
```

La promocion de cualquier tabla requiere profiling fisico y contratos en
`01_foundations`.
