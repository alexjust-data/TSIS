# Graphify Official Build Protocol for 00_CTO

Fecha: 2026-06-18
Estado: regla operativa local para agentes.

## Proposito

Este documento existe para evitar que otro agente confunda un grafo compatible
con Graphify con un grafo producido oficialmente por Graphify.

`00_CTO` puede usar Graphify como mapa semantico de navegacion, pero el grafo
solo se considera valido si fue generado por el pipeline oficial de Graphify.

## Regla corta

```text
No escribas manualmente 00_CTO/graphify-out/graph.json.
Si no lo genero Graphify, no es Graphify oficial.
```

## Que cuenta como build oficial

Un build oficial de Graphify debe venir de uno de estos flujos:

- `$graphify .` desde Codex, con la skill Graphify activa;
- `graphify extract <scope>` usando el CLI oficial;
- `graphify update`, `graphify cluster-only`, `graphify merge-graphs` o exports
  oficiales sobre un grafo ya generado por Graphify.

El build oficial esperado genera, salvo decision documentada:

```text
graphify-out/
├── graph.html
├── GRAPH_REPORT.md
└── graph.json
```

Si se omite HTML por `--no-viz` u otra opcion oficial, esa decision debe quedar
registrada en el changelog o manifest del build.

## Divergencia TSIS respecto al workflow de equipo de Graphify

Graphify upstream recomienda normalmente compartir `graphify-out/` con el
equipo para que todos empiecen con el mismo mapa.

TSIS puede decidir algo distinto por gobierno institucional: tratar
`graphify-out/` como runtime reconstruible salvo promocion explicita.

Esa divergencia es aceptable solo en la politica de versionado/commit del
artefacto. No autoriza a cambiar el modo de generacion.

Regla:

```text
TSIS puede gobernar si se versiona graphify-out/.
TSIS no puede llamar Graphify oficial a algo que Graphify no genero.
```

## Que no cuenta como build oficial

No cuenta como oficial:

- crear `graph.json` a mano con PowerShell, Python u otro script propio;
- generar nodos y edges curados manualmente;
- construir un JSON que solo sea legible por `graphify query`;
- usar `graphify explain` o `graphify path` como prueba suficiente de origen;
- presentar un fallback compatible como si fuera salida de Graphify.

Regla:

```text
Formato compatible no prueba procedencia.
```

## Por que ocurrio el fallo de 2026-06-18

Durante el intento inicial de construir el grafo de `00_CTO`, el agente mezclo
dos objetivos distintos:

1. cumplir la politica TSIS de separar scope operativo, subgrafos y runtime;
2. entregar rapidamente `graph.json` y `GRAPH_REPORT.md`.

Al fallar el camino oficial por una combinacion de:

- ausencia de un backend LLM/API key utilizable para `graphify extract`;
- confusion entre flujo de skill Graphify y flujo CLI headless;
- problemas de escritura desde Python en `graphify-out`;
- presion por no perder la extraccion semantica;

el agente genero un fallback manual compatible con el formato de Graphify.

Ese fallback fue un error porque uso los nombres canonicos:

```text
00_CTO/graphify-out/graph.json
00_CTO/graphify-out/GRAPH_REPORT.md
```

Eso podia activar el fast path de Graphify y hacer creer a futuros agentes que
existia un grafo oficial.

## Correccion aplicada

El fallback no oficial fue retirado del path canonico y movido a cuarentena:

```text
C:\tmp\graphify_00_cto\non_official_fallback_2026-06-18
```

Tambien se retiro el mirror temporal que habia quedado en:

```text
C:\tmp\graphify_00_cto\phase1_outputs
```

Mientras no exista un build oficial, este path no debe existir:

```text
00_CTO/graphify-out/graph.json
```

## Procedimiento correcto para el proximo intento

Desde Codex:

```powershell
cd C:\TSIS_Data\00_CTO
$graphify .
```

Si se ejecuta headless:

```powershell
graphify extract C:\TSIS_Data\00_CTO\<scope> --out C:\tmp\graphify_00_cto\<build_id>
```

El agente debe parar si:

- Graphify pide backend LLM y no existe backend disponible;
- la skill no puede lanzar subagentes;
- mas de la mitad de chunks fallan;
- no se genera `GRAPH_REPORT.md`;
- no se genera `graph.json`;
- no se genera `graph.html` y no hubo `--no-viz` documentado;
- el output procede de un script manual.

## Criterios minimos de aceptacion

Antes de declarar exito, el agente debe comprobar:

```powershell
Test-Path .\graphify-out\graph.json
Test-Path .\graphify-out\GRAPH_REPORT.md
Test-Path .\graphify-out\graph.html
graphify diagnose multigraph --graph .\graphify-out\graph.json
graphify explain "<nodo canonico>" --graph .\graphify-out\graph.json
```

Si `graph.html` falta por decision oficial, debe indicarse el flag usado.

## Protocolo de actualizacion incremental

El grafo raiz de `00_CTO` es un grafo fusionado. No debe actualizarse como un
escaneo monolitico de todo `00_CTO` cuando el cambio pertenece a un slice
concreto.

Regla:

```text
Primero se actualiza el subgrafo leaf afectado.
Despues se fusiona oficialmente contra el grafo raiz.
```

Flujo obligatorio para nuevos archivos o modificaciones:

1. Revisar `git status --short` y localizar archivos nuevos, modificados o
   eliminados.
2. Mapear cada path al slice Graphify correspondiente.
3. Ejecutar el flujo oficial Graphify sobre ese slice:
   - `graphify update` si el slice ya tiene manifest compatible;
   - o rebuild del leaf con la skill Graphify si contiene docs, papers,
     imagenes o material semantico que requiere extraccion LLM/subagentes.
4. Fusionar el leaf actualizado con `graphify merge-graphs`.
5. Recalcular comunidades con `graphify cluster-only`.
6. Validar con `graphify diagnose multigraph`.
7. Actualizar `graphify-out/BUILD_MANIFEST.md` y, si el cambio altera scope o
   semantica, actualizar `README.md` y `CHANGELOG.md`.

Mapping operativo actual:

```text
13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/
-> core_cto_graph / trading_systems_slice
-> docs/papers de estrategia; requiere extraccion semantica oficial

12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/
12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/
-> data_quality_harness_graph

12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/
-> sersan_distillation_graph

99_REFERENCE_LIBRARY/SersanSistemas/
-> reference_sersan_graph
-> puede fusionarse al grafo raiz solo con decision explicita de scope
```

No se debe usar `.graphifyignore` para ocultar material semanticamente
importante. `.graphifyignore` sirve para excluir runtime, caches, datasets,
artefactos pesados y outputs reconstruibles. La separacion entre `core`,
`distillation` y `reference` se gobierna por slices y manifests, no por esconder
fuentes relevantes.

Para una carpeta nueva como:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\01_STRATEGY_LIBRARY
```

el agente debe tratarla como ampliacion del `core_cto_graph` mediante un
`trading_systems_slice`. El grafo raiz no debe declararse actualizado hasta que
ese slice haya sido extraido por Graphify, fusionado, reclusterizado y
diagnosticado.

## Prohibicion final

Un agente no debe "salvar" una extraccion fallida escribiendo un grafo manual
en `graphify-out/`.

La accion correcta ante un fallo es diagnosticar, documentar y parar.
