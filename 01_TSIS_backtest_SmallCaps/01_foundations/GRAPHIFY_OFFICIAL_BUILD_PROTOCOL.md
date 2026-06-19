# Graphify Official Build Protocol for 01_foundations

Fecha: 2026-06-19
Estado: regla operativa local para agentes.

## Proposito

Este documento gobierna los builds oficiales de Graphify para:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

`01_foundations` es autoridad contractual de CAPA 1. Por tanto, su grafo no debe
tratarse como un grafo documental generico. Debe separar contratos vivos,
schemas, registries, policies, validators, dossiers y evidencia historica.

## Regla corta

```text
No escribas manualmente 01_foundations/graphify-out/graph.json.
Si no lo genero Graphify, no es Graphify oficial.
```

## Documentos que gobiernan este flujo

Leer en este orden:

1. `01_TSIS_backtest_SmallCaps/LOCAL_RULES.md`
2. `01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
3. `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`
4. `01_foundations/module_contracts/graphify/README.md`
5. `01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md`
6. los dataset contracts, schemas, registries, policies y validators del slice
   que se vaya a construir.

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
- hacer un grafo monolitico de todo el modulo y llamarlo CAPA 1 si mezcla
  contratos, runtime, evidencia pesada y datos fisicos.

Regla:

```text
Formato compatible no prueba procedencia.
```

## Divergencia TSIS respecto al workflow de Graphify

Graphify upstream puede recomendar compartir `graphify-out/` con el equipo.

En TSIS, `graphify-out/` se trata como runtime reconstruible salvo promocion
explicita. La memoria versionada de como construir el grafo vive en:

```text
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/module_contracts/graphify/
```

Esto solo gobierna versionado y trazabilidad. No autoriza builds manuales.

## Directorio de ejecucion

Graphify interpreta `.` como el directorio actual de la sesion, no como el
modulo que el humano tiene en mente.

Si Codex esta abierto en:

```text
C:\TSIS_Data
```

entonces esto esta prohibido para el grafo de CAPA 1:

```text
$graphify .
```

porque intentaria construir un grafo del monorepo completo.

No hace falta abrir otro agente solo por estar en el directorio raiz. El agente
debe usar una ruta absoluta o cambiar de directorio al leaf exacto antes de usar
`.`.

Ejemplos validos:

```text
$graphify C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts
```

o:

```powershell
Set-Location C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts
$graphify .
```

Antes de ejecutar `$graphify .`, el agente debe verificar y declarar cual es el
directorio actual efectivo.

## Scope correcto

No hacer como primer paso:

```text
graphify C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
graphify C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification
graphify C:\TSIS_Data\01_TSIS_backtest_SmallCaps
```

Motivo:

- `01_foundations` contiene contratos y tambien dossiers pesados;
- `00_data_certification` contiene auditoria, scripts, imagenes, parquet,
  caches y notebooks preservados;
- un grafo monolitico mezclaria autoridad contractual con evidencia y runtime.

## Grafo raiz y leaves

El grafo de `01_foundations` debe entenderse como familia de grafos:

```text
data_foundation_root_graph
  foundations_authority_graph
  certification_decisions_graph
  reference_identity_graph
  daily_ohlcv_graph
  microstructure_quotes_trades_graph
  additional_fundamentals_news_graph
```

Estos nombres no son carpetas fisicas.

Son nombres de builds/slices oficiales de Graphify. Cada leaf puede tomar
archivos de varias carpetas reales y excluir evidencia pesada, runtime o datos
fisicos que no deben entrar en el mapa semantico.

El root solo debe existir cuando sus leaves oficiales hayan sido construidos o
cuando exista una razon operativa clara para tener una vista fusionada.

Regla:

```text
Primero leaf. Despues root, si aporta valor.
```

Por tanto:

```text
Si, se pretende cubrir 01_foundations.
No, no se pretende hacerlo con un unico graphify 01_foundations inicial.
```

## Slices canonicos

La definicion detallada de corpus vive en:

```text
01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md
```

Resumen operativo:

```text
foundations_authority_graph
-> module_contracts, dataset_contracts, schemas, registries, policies,
   validators.

certification_decisions_graph
-> certification markdown, closeouts, policies y global metrics livianos.

reference_identity_graph
-> reference contract, schemas, registry, validators, corporate actions,
   event inventory y certification/reference.

daily_ohlcv_graph
-> daily/OHLCV contracts, schemas, registry, validators, sessions, price views.

microstructure_quotes_trades_graph
-> quotes/trades contracts, schemas, registry, validators, certification.

additional_fundamentals_news_graph
-> additional/financial schemas, additional contract, registry, policy,
   certification/additional.
```

## Exclusiones por defecto

La raiz `01_foundations/.graphifyignore` debe excluir runtime y evidencia pesada
cuando se construyan grafos desde esta raiz.

Exclusiones conceptuales:

```text
graphify-out/
inspection_dossiers/
evidence_assets/
*.parquet
*.csv
*.png
*.jpg
*.jpeg
*.webp
*.ipynb
__pycache__/
.pytest_cache/
```

No usar `.graphifyignore` para ocultar documentos semanticamente importantes.
Si un documento importa para el grafo, debe entrar por el slice correcto.

## Procedimiento de build

1. Leer este protocolo y el protocolo metodologico en
   `module_contracts/graphify/`.
2. Revisar `GRAPHIFY_REFRESH_QUEUE.md`.
3. Identificar si se necesita nuevo build o solo registrar pending refresh.
4. Elegir un solo slice.
5. Confirmar corpus incluido y excluido.
6. Ejecutar Graphify con flujo oficial.
7. Verificar que existen:

```powershell
Test-Path .\graphify-out\graph.json
Test-Path .\graphify-out\GRAPH_REPORT.md
Test-Path .\graphify-out\graph.html
```

8. Si `graph.html` no existe por decision oficial, anotar el flag.
9. Consultar al menos un nodo canonico con `graphify explain` o una query
   equivalente.
10. Actualizar `GRAPHIFY_REFRESH_QUEUE.md` con estado final.
11. Si cambia scope o politica de uso, actualizar `CHANGELOG.md`.

## Cadencia de actualizacion

Graphify no sigue cada commit.

Git es memoria continua. Graphify es mapa semantico. Se refresca por hito,
severidad o lote.

```text
LOW      -> no actualizar Graphify
MEDIUM   -> anotar en GRAPHIFY_REFRESH_QUEUE.md
HIGH     -> reconstruir leaf en ventana dedicada
CRITICAL -> reconstruir leaf y decidir root explicitamente
```

## Severidad

### LOW

- typo;
- nota menor;
- ajuste editorial sin cambio de meaning;
- cambio en `graphify-out/` runtime no versionado.

Accion:

```text
No tocar Graphify.
```

### MEDIUM

- nuevo documento explicativo;
- ampliacion documental sin cambiar contrato;
- nuevo README local;
- nueva evidencia ligera no promovida.

Accion:

```text
Anotar en cola.
```

### HIGH

- nuevo dataset contract;
- nuevo schema canonico;
- cambio de data consumption policy;
- cambio de validator con impacto de aceptacion;
- nuevo graph slice;
- nuevo table design protocol;
- nuevo closeout que cambia interpretacion.

Accion:

```text
Construir o actualizar leaf oficial.
```

### CRITICAL

- renombre/eliminacion de rutas ya indexadas;
- cambio de semantica de dataset;
- cambio de price semantics;
- cambio de recovery/certification state;
- promocion de tabla master;
- cambio que afecte consumidores downstream.

Accion:

```text
Construir leaf si aporta valor inmediato.
No fusionar root de forma aditiva sin comprobar rutas antiguas.
```

## Relacion con diseno de tablas

Graphify no decide tablas por si solo.

Despues de construir o consultar un grafo, una tabla solo puede avanzar si se
cumple:

```text
contract + certification + evidence + physical profiling + validator
```

El profiling fisico de parquet/CSV es obligatorio para tablas CAPA 1.

## Prompt operativo reutilizable

```text
Actualiza o construye el grafo Graphify oficial de 01_foundations.

Reglas:
- Lee 01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md.
- Lee 01_foundations/GRAPHIFY_REFRESH_QUEUE.md.
- Lee 01_foundations/module_contracts/graphify/README.md.
- Lee 01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md.
- No uses `$graphify .` salvo que hayas verificado que el directorio actual es el leaf exacto.
- Si la sesion esta en `C:\TSIS_Data`, usa ruta absoluta; no abras otro agente solo por el path.
- No hagas un rebuild monolitico de 01_foundations por defecto.
- Identifica el slice Graphify correspondiente.
- Clasifica severidad: LOW, MEDIUM, HIGH o CRITICAL.
- Si es LOW, no actualices Graphify.
- Si es MEDIUM, anota o actualiza la refresh queue y termina.
- Si es HIGH o CRITICAL, reconstruye el leaf con flujo oficial Graphify.
- No escribas graphify-out/graph.json con scripts manuales.
- Trata graphify-out/ como runtime reconstruible.
- No propongas tablas sin profiling fisico posterior.
```

## Regla final

Un agente no debe "salvar" una extraccion fallida escribiendo un grafo manual
en `graphify-out/`.

La accion correcta ante un fallo es diagnosticar, documentar y parar.
