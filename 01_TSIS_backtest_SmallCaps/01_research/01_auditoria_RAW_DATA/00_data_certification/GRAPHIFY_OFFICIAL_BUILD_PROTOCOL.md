# Graphify Official Build Protocol for 00_data_certification

Fecha: 2026-06-19
Estado: regla operativa local para agentes.

## Proposito

Este documento gobierna los builds oficiales de Graphify para:

```text
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification
```

`00_data_certification` es memoria cientifica preservada de auditoria,
diagnostico, closeouts y decisiones de certificacion. Su grafo no debe tratarse
como un escaneo documental generico ni como reemplazo de los contratos vivos en
`01_foundations`.

## Regla corta

```text
No escribas manualmente 00_data_certification/graphify-out/graph.json.
Si no lo genero Graphify, no es Graphify oficial.
```

## Relacion con 01_foundations

`01_foundations` define autoridad operativa viva:

```text
contracts, schemas, registries, policies, validators
```

`00_data_certification` preserva evidencia historica y decisiones:

```text
expected/present/healthy/usable_for, recovery, exclusion, closeouts,
certification policies, global metrics, audit contracts
```

El grafo de certificacion debe ayudar a detectar si `01_foundations`
simplifica demasiado una decision historica.

## Que cuenta como build oficial

Un build oficial debe venir de uno de estos flujos:

- `$graphify <path>` desde Codex, con la skill Graphify activa;
- `graphify <path>` desde CLI;
- `graphify <path> --update` cuando exista manifest compatible;
- `graphify <path> --cluster-only` sobre un grafo ya oficial;
- merge o export oficial ofrecido por la version instalada de Graphify.

El build oficial esperado genera, salvo decision documentada:

```text
graphify-out/
  graph.html
  GRAPH_REPORT.md
  graph.json
```

Si se omite `graph.html` por `--no-viz`, debe quedar documentado en la cola o
manifest del build.

## Que no cuenta como build oficial

No cuenta como oficial:

- crear `graph.json` a mano con PowerShell, Python u otro script propio;
- generar nodos/edges curados manualmente;
- copiar un JSON compatible sin conservar procedencia;
- presentar un fallback compatible como si fuera Graphify;
- usar `graphify query`, `graphify explain` o `graphify path` como prueba de
  procedencia;
- hacer un grafo monolitico de todo `00_data_certification` si mezcla
  certification docs, notebooks, imagenes, parquet, CSV, scripts y runtime.

Regla:

```text
Formato compatible no prueba procedencia.
```

## Divergencia TSIS respecto al workflow de Graphify

Graphify upstream puede recomendar compartir `graphify-out/` con el equipo.

En TSIS, `graphify-out/` se trata como runtime reconstruible salvo promocion
explicita. La memoria versionada de como construir el grafo vive en:

```text
00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
00_data_certification/module_contracts/graphify/
```

Esto gobierna versionado y trazabilidad. No autoriza builds manuales.

## Scope correcto

No hacer como primer paso:

```text
graphify 00_data_certification
graphify 01_research/01_auditoria_RAW_DATA
graphify 01_TSIS_backtest_SmallCaps
```

Motivo:

- `00_data_certification` contiene auditoria, notebooks, imagenes, parquet,
  CSV, scripts, caches y material historico preservado;
- un grafo monolitico mezclaria decisiones finales con evidencia fisica,
  exploracion y runtime;
- los notebooks son importantes, pero deben entrar en un leaf de evidencia de
  notebooks, no en el grafo inicial de decisiones de certificacion.

## Familia de grafos

El grafo de certificacion debe entenderse como familia de leaves:

```text
certification_decisions_graph
certification_notebook_evidence_graph
certification_physical_evidence_graph
```

El primer leaf oficial es:

```text
certification_decisions_graph
```

Ese leaf mapea decisiones finales, policies, closeouts y global metrics
livianos. No absorbe notebooks ni evidencia binaria.

## Documentos que gobiernan este flujo

Leer en este orden:

1. `01_TSIS_backtest_SmallCaps/LOCAL_RULES.md`
2. `00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
3. `00_data_certification/GRAPHIFY_REFRESH_QUEUE.md`
4. `00_data_certification/module_contracts/graphify/README.md`
5. `00_data_certification/module_contracts/graphify/certification_decisions_graph_protocol.md`
6. los closeouts, policies, contratos y global metrics del slice.

## Procedimiento de build

1. Revisar esta politica y la cola local.
2. Elegir un solo slice.
3. Confirmar corpus incluido y excluido.
4. Ejecutar Graphify con flujo oficial.
5. Verificar que existen:

```powershell
Test-Path .\graphify-out\leaf_slices\<leaf>\graph.json
Test-Path .\graphify-out\leaf_slices\<leaf>\GRAPH_REPORT.md
Test-Path .\graphify-out\leaf_slices\<leaf>\graph.html
```

6. Validar con:

```powershell
graphify diagnose multigraph --graph .\graphify-out\leaf_slices\<leaf>\graph.json
graphify explain "<nodo canonico>" --graph .\graphify-out\leaf_slices\<leaf>\graph.json
```

7. Actualizar `GRAPHIFY_REFRESH_QUEUE.md` y el manifest del leaf.

## Regla para notebooks

Los notebooks son evidencia historica importante. Se excluyen por defecto del
`certification_decisions_graph` para evitar que exploracion, celdas fuera de
orden, outputs visuales y paths locales se mezclen con decisiones finales.

Los notebooks deben entrar en un leaf separado:

```text
certification_notebook_evidence_graph
```

Ese leaf debe declarar claramente que mapea exploracion/evidencia, no autoridad
final.
