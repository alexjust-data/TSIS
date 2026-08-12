# Graphify Refresh Queue

Estado: cola operativa versionada para el grafo raiz de `C:\TSIS_Data`.

## Regla

Toda tarea con impacto semantico sobre una rama que contenga `graphify-out/`
debe terminar con el leaf oficial actualizado y diagnosticado o con una entrada
`pending` en la cola mas cercana. Esta cola es el fallback para cambios de
alcance raiz o para ramas sin cola local.

Cada entrada debe incluir fecha, estado, severidad, scope, leaf objetivo,
archivos afectados, motivo del aplazamiento y criterio de cierre.

## Pending

### GFQ-20260811-ROOT-002 - Governed Graphify backlog reconciliation and leaf-first root rebuild

- **Estado:** `pending`
- **Fecha:** `2026-08-11`
- **Severidad:** `CRITICAL`
- **Scope:** reconciliacion transversal de las colas Graphify, refresco de leaves
  oficiales afectados por cambios posteriores al ultimo baseline y
  reconstruccion controlada del grafo raiz del proyecto.
- **Leaves objetivo:** `graphify_governance`, Market States/TA-3/SEC PIT,
  Data Foundation execution/output topology, `foundations_authority`,
  `00_CTO_APPLIED_ARCHITECTURE`, `backtest_engine_current` y posterior fusion
  `project_root`.
- **Colas fuente:** las siete `GRAPHIFY_REFRESH_QUEUE.md` de root, `00_CTO`,
  `00_CTO_APPLIED_ARCHITECTURE`, Data Foundation root, `01_foundations`,
  `00_data_certification` y `02_TSIS_BACKTEST_ENGINE`.
- **Motivo:** el Git interno confirma el patron historico
  `leaf -> diagnostics -> BUILD_MANIFEST -> root merge`, pero varias colas no
  reconciliaron sus estados tras los batches del 29/30 de junio y del 5 de
  julio. La migracion de rutas del commit
  `c3d6f141f9a3b8bd68c858a72583cde9fe7652ec` movio los artefactos sin
  reconstruir los leaves promocionados. Los leaves de julio aun conservan
  `source_file` bajo `01_TSIS_backtest_SmallCaps` y `00_TSIS_Lab`; un merge
  aditivo podria retener rutas obsoletas.
- **Baselines Git a contrastar:**
  - `be6a2d6749447cda4489081a37fda2ee6a90bb94`: batch de leaves 2026-06-29/30;
  - `e7cbd148d9927b2019d2f9bcc27d406631eb5f4d`: refresh y fusion raiz 2026-07-05;
  - `713805e0ce38b4fde695ff27dceefe26a636c7bd`: leaves semanticos de
    certificacion y Backtest publicados el 2026-08-05/06;
  - `e8892333fb40b25e3dd00880a53958beb3399599`: baseline previo a los cambios
    activos de TA-3/SEC PIT.

#### Precondicion de ejecucion

No iniciar extraccion, clustering ni merge mientras la materializacion larga
TA-3 `ta3_cpp_v0_1_20260811` siga activa. Esperar a su estado terminal y
preservar su CPU, RAM e I/O. Antes del lote registrar rama, commit,
`git status --short`, dirty/untracked paths y version efectiva de Graphify.

La version instalada observada es `graphifyy 0.9.33` y la procedencia vigente
es `https://github.com/Graphify-Labs/graphify`. Actualizar la metadata de nuevos
builds que aun replique `0.9.1` o la procedencia historica, sin reescribir
manifests historicos inmutables.

#### Secuencia obligatoria

1. **Reconciliar las colas antes de construir.** Comparar cada entrada con
   corpus manifests, `BUILD_MANIFEST.md`, diagnosticos y commits posteriores.
   Marcarla `covered`, `superseded`, `closed` o mantenerla `pending`; el
   recuento textual bruto de estados antiguos no equivale a rebuilds reales.
2. **Asignar cada delta a un unico leaf canonico.** Evitar duplicar el mismo
   cambio en CTO, Data Foundation y root; las colas locales conservan el
   detalle y esta entrada conserva orden y dependencias.
3. **Refrescar primero `graphify_governance`.** Incorporar gobierno raiz,
   reglas de cierre, protocolos vigentes y migracion de rutas.
4. **Refrescar Market States/TA-3/SEC PIT tras el final de TA-3.** Incluir
   lifecycle experimental-canonical, Binding A, recovery/supervision,
   telemetria, SEC PIT y handoffs sin convertir runtime en autoridad.
5. **Refrescar Data Foundation execution/output topology y
   `foundations_authority`.** Incorporar contratos, builders, recovery y
   long-running operations en sus slices. Mantener separado el leaf semantico
   `certification_decisions` de 2026-08-05 salvo delta real de su corpus.
6. **Refrescar `00_CTO_APPLIED_ARCHITECTURE` y
   `backtest_engine_current`.** En Backtest resolver el refresh posterior al
   snapshot y excluir evidence/archive de la autoridad current.
7. **Tratar Sersan/reference e historia como leaves separados.** La
   reorganizacion Sersan es `CRITICAL` y exige rebuild/reemplazo del slice; los
   leaves de evidencia y archivo de Backtest conservan menor prioridad.
8. **Validar y promocionar cada leaf por separado.** No avanzar al root hasta
   que cada leaf seleccionado cumpla todos los gates de aceptacion.
9. **Reconstruir el root desde leaves vigentes.** No hacer `merge-graphs`
   aditivo sobre el root de julio ni sobre leaves con rutas antiguas. Crear una
   fusion oficial nueva, ejecutar `cluster-only`, diagnosticar y comprobar
   consultas canonicas.
10. **Cerrar el lote.** Actualizar las siete colas, cada `BUILD_MANIFEST.md` y
    el manifest del root con `queue_entries_covered` y
    `queue_entries_left_pending` explicitos.

#### Gates de aceptacion por leaf y root

- corpus controlado y reconstruible, con inclusiones/exclusiones explicitas;
- paridad de corpus y hashes entre workspace controlado y paths canonicos;
- extraccion AST y semantica acorde al tipo de archivo; `graphify update`
  code-only no demuestra cobertura de Markdown/contracts;
- `graph.json`, `GRAPH_REPORT.md` y `graph.html`, salvo `--no-viz` documentado;
- `graphify diagnose multigraph` limpio: cero endpoints ausentes/dangling,
  self-loops inesperados o edges colapsados;
- smoke `graphify explain` o `graphify query` sobre nodos canonicos;
- `BUILD_MANIFEST.md` con rama, commit, dirty state, paths, timestamp, comando,
  version efectiva, fuente de skill, modo semantico, corpus, diagnosticos y
  siguientes deltas;
- ningun `source_file` promocionado conserva prefijos obsoletos de la migracion
  de 2026-07-22;
- cumplimiento de `LONG_RUNNING_OPERATIONS_CONTRACT.md` si el build es largo:
  pre-manifest, PID, heartbeat, log vivo, monitor separado y final manifest.

- **Cierre esperado:** entradas previas reconciliadas contra evidencia; leaves
  prioritarios construidos y diagnosticados; root reconstruido desde leaves
  vigentes sin rutas antiguas; clustering y smoke queries pasan; manifests y
  colas distinguen claramente cobertura y pendientes.
- **Aplazamiento actual:** no se ejecuto rebuild Graphify durante esta auditoria
  para no competir con la materializacion TA-3 activa.

### GFQ-20260805-ROOT-001 - Agent Graphify closeout policy

- **Estado:** `pending`
- **Severidad:** `HIGH`
- **Scope:** gobierno raiz y herencia de agentes
- **Leaf objetivo:** `graphify_governance` y siguiente fusion raiz
- **Archivos afectados:** `C:\TSIS_Data\AGENTS.md`,
  `C:\TSIS_Data\GRAPHIFY_REFRESH_QUEUE.md`
- **Motivo:** se normalizo la obligacion de cerrar cada trabajo con un leaf
  actualizado o una entrada pendiente. No se reconstruyo el grafo raiz.
- **Cierre esperado:** reconstruir y diagnosticar el leaf de gobierno y
  sustituir su cobertura en la siguiente fusion raiz oficial.

### GFQ-20260812-SEC-PIT-OWNERSHIP-002 - Ownership resolver loops v0.9-v0.11

- **Estado:** `pending`
- **Fecha:** `2026-08-12`
- **Severidad:** `HIGH`
- **Scope:** SEC PIT owner-exclusion resolver, causal baseline selection,
  identity/date admission, split fail-closed gate and SEC HTML ownership table
  normalization.
- **Leaf objetivo:** Market States / SEC PIT leaf in the next controlled root
  rebuild.
- **Archivos afectados:**
  `01_TSIS_DATA_FOUNDATION/scripts/sec_pit/ownership_v2.py`,
  `ownership_baseline.py`, `float_estimate.py`, `float_estimate_v2.py`,
  `run_no_network_owner_exclusion_probe.py`, governed config/tests, and the five
  SEC PIT shard/readout dossiers created on 2026-08-12.
- **Motivo pendiente:** the active root graph has no ownership, baseline,
  amendment, parser or float vocabulary for this corpus. A constrained query
  expanded only to `table`/`tables` and returned unrelated generic table nodes.
  Rebuild remains forbidden while TA-3 `ta3_cpp_v0_1_20260811` is active.
- **Evidence state:** v0.11 completed 99/99 O/S and 99/99 owner cases, zero
  execution failures and zero network resolution; system audit PASS; float
  coverage 20/99; scale to 4,824 not granted.
- **Cierre esperado:** after TA-3 reaches a terminal state, refresh and diagnose
  the SEC PIT leaf, update its `BUILD_MANIFEST.md`, verify queries for ownership
  baseline/parser/split/identity/float, and include it in the controlled root
  reconstruction without treating runtime artifacts as authority.
