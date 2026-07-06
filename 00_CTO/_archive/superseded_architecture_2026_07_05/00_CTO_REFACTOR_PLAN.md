# 00_CTO Refactor Plan

Fecha de creacion: 2026-06-18
Estado: plan gobernado para alinear `00_CTO` con `TSIS_LAB_ARCHITECTURE.md`.

## Objetivo

Alinear el arbol de `00_CTO` con la arquitectura TSIS Lab sin destruir memoria
historica ni duplicar autoridad operativa.

Este plan existe para que otro agente no tenga que inferir desde conversaciones
que carpetas se quedan, cuales se modifican y con que criterio.

## Documentos fuente

Fuentes promovidas o a promover:

- `LOCAL_RULES.md`
- `TSIS_LAB_ARCHITECTURE.md`
- `README.md`
- `CHANGELOG.md`

Fuentes privadas usadas como input:

- `00_private/arquitectura.md`
- `00_private/eventos.md`
- `13_TRADING_SYSTEMS/revision.md`

Contratos relacionados:

- `PROJECT_OPERATING_SYSTEM.md`
- `PROJECT_RULES.md`
- `VERSIONING_STANDARDS.md`
- `AGENTS.md`
- `RESEARCH_PHILOSOPHY.md`
- `01_TSIS_backtest_SmallCaps/LOCAL_RULES.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md`

## Principio rector

No conservar carpetas por inercia.

Cada carpeta que quede activa debe tener:

- proposito funcional;
- inputs;
- outputs esperados;
- no-goals;
- estado de madurez;
- relacion con TSIS Lab;
- y razon para vivir en esa ruta.

## Acciones permitidas

- `KEEP`: se queda sin cambio fisico.
- `CLARIFY`: se queda, pero requiere README/rol mas claro.
- `REFACTOR`: cambia estructura interna o nombres.
- `MOVE`: se mueve por estar en capa equivocada.
- `SPLIT`: se divide por mezclar responsabilidades.
- `ARCHIVE`: se conserva como memoria historica no activa.
- `RUNTIME`: se trata como output reconstruible.
- `REFERENCE`: se conserva como fuente externa no autoritativa.

## Matriz funcional actual

| Carpeta | Rol actual | Rol objetivo | Accion | Severidad | Motivo |
|---|---|---|---|---|---|
| `00_private` | notas, prompts, imagenes, fuentes crudas | source notes no autoritativas | CLARIFY | MEDIUM | Debe inspirar, no gobernar. |
| `01_RESEARCH_PHILOSOPHY` | notas de filosofia research | fuente CTO secundaria para doctrina de research | KEEP/CLARIFY | LOW | La autoridad raiz sigue en `RESEARCH_PHILOSOPHY.md`. |
| `02_SYSTEMS_ENGINEERING` | diseno general de sistema | arquitectura tecnica y limites de modulos | KEEP/CLARIFY | LOW | Debe explicar interfaces, no duplicar root docs. |
| `03_AGENT_ENGINEERING` | agentes, Harness y standards | fuente de agent engineering | KEEP/CLARIFY | MEDIUM | Debe alimentar `12_TSIS_COGNITIVE_ARCHITECTURE`, no reemplazar `AGENTS.md`. |
| `04_MEMORY_AND_KNOWLEDGE` | memoria, RAG, GraphRAG | diseno de memoria institucional | KEEP/CLARIFY | MEDIUM | Debe separar tooling de memoria institucional. |
| `05_EVALUATION_SYSTEMS` | evaluadores y fitness | autoridad CTO para evaluar antes de generar | CLARIFY | HIGH | Es barrera previa a Strategy Research, ML y AlphaEvolve. |
| `06_MLOPS_AND_REPRODUCIBILITY` | reproducibilidad y custodia | lineage, run ids, experiment tracking | KEEP/CLARIFY | MEDIUM | Debe soportar outputs, no guardar outputs pesados. |
| `07_DISTRIBUTED_SYSTEMS` | escalado e infraestructura | roadmap de compute/orquestacion | KEEP/CLARIFY | LOW | No debe adelantar Kubernetes antes de necesidad real. |
| `08_MACHINE_LEARNING` | ML y representacion | CAPA 8: estimacion probabilistica | CLARIFY | HIGH | Debe decir explicitamente que ML no decide trades. |
| `09_REINFORCEMENT_LEARNING` | RL | Decision Models / Offline RL | CLARIFY, posible RENAME futuro | HIGH | RL debe ir despues de estados, evaluadores y simulacion realista. |
| `10_AUTONOMOUS_RESEARCH_SYSTEMS` | AlphaEvolve/OpenEvolve/discovery | motores de evolucion bajo evaluadores bloqueados | CLARIFY | HIGH | No debe leerse como punto de partida. |
| `11_MARKET_SCIENCE` | microestructura, causalidad, invariantes | ciencia de dominio para estados/eventos/features | KEEP/CLARIFY | MEDIUM | Debe alimentar Event Library y Market State, no ser biblioteca suelta. |
| `12_TSIS_COGNITIVE_ARCHITECTURE` | Harness y operating models TSIS | arquitectura operativa de automatizacion TSIS | KEEP/CLARIFY | HIGH | Es workspace principal de Harness, Data Quality y Sersan. |
| `13_TRADING_SYSTEMS` | dominio trading, strategy-first parcial | laboratorio de conocimiento event-first | REFACTOR | HIGH | Debe alinear Evento -> Outcome -> Strategy -> Pattern -> Decision -> Evolution. |
| `99_REFERENCE_LIBRARY` | referencia externa | fuente externa no autoritativa | REFERENCE | MEDIUM | Solo gobierna tras destilacion/promocion. |
| `graphify-out` | grafo generado | runtime reconstruible Graphify | RUNTIME | MEDIUM | No es source of truth; actualizar por protocolo. |

## Target funcional de 13_TRADING_SYSTEMS

El cambio fisico mas fuerte debe ocurrir en `13_TRADING_SYSTEMS`.

Target propuesto:

```text
13_TRADING_SYSTEMS/
  README.md
  00_EVENT_LIBRARY/
  01_EVENT_ENGINE_MODEL/
  02_OUTCOME_RESEARCH/
  03_STRATEGY_LIBRARY/
  04_STRATEGY_RESEARCH/
  05_EDGE_HYPOTHESES/
  06_PATTERN_DISCOVERY/
  07_CLUSTER_RESEARCH/
  08_EXECUTION_MODELS/
  09_DECISION_MODELS/
  10_EVOLUTION_SYSTEMS/
  11_SQUEEZE_RESEARCH/
  90_DISCRETIONARY_FRAMEWORKS/
  99_EXPERIMENTAL/
```

Historical mappings executed on 2026-06-18:

- `00__EVENT_LIBRARY` -> `00_EVENT_LIBRARY`
- `01_STRATEGY_LIBRARY` -> `03_STRATEGY_LIBRARY`
- `03_EDGE_HYPOTHESES` -> `05_EDGE_HYPOTHESES`
- `04_PATTERN_CATALOG` -> `06_PATTERN_DISCOVERY`
- `05_EXECUTION_MODELS` -> `08_EXECUTION_MODELS`
- `06_DISCRETIONARY_FRAMEWORKS` -> `90_DISCRETIONARY_FRAMEWORKS`
- `07_STRATEGY_EVOLUTION` -> `10_EVOLUTION_SYSTEMS`
- `08_STRATEGY_CLUSTERS` -> `07_CLUSTER_RESEARCH`
- `02_SETUP_TAXONOMY` was removed because it was empty and no longer a
  top-level canonical layer.

Notes:

- Carpetas objetivo sin contenido real deben tener README minimo para que Git
  preserve la intencion.
- No crear implementacion operativa aqui si pertenece al modulo 01.

## Fases

### Fase 0 - Gobierno local

- Crear `LOCAL_RULES.md`.
- Crear `TSIS_LAB_ARCHITECTURE.md`.
- Crear este plan.
- Actualizar `README.md`.
- Actualizar `CHANGELOG.md`.

### Fase 1 - Auditoria funcional de carpetas top-level

Para cada carpeta top-level de `00_CTO`:

1. confirmar que existe README o documento equivalente;
2. declarar funcion practica;
3. declarar inputs y outputs;
4. declarar no-goals;
5. marcar estado: `source_note`, `draft`, `candidate_policy`, `promoted`;
6. decidir `KEEP`, `CLARIFY`, `REFACTOR`, `MOVE`, `SPLIT`, `ARCHIVE`,
   `RUNTIME` o `REFERENCE`.

### Fase 2 - Refactor event-first de Trading Systems

- Done: actualizar `13_TRADING_SYSTEMS/README.md`.
- Done: renombrar `00__EVENT_LIBRARY` a `00_EVENT_LIBRARY`.
- Done: crear README minimo para cada carpeta canonica.
- Done: mover contenido existente solo cuando el mapping era claro.
- Ongoing rule: no mezclar estrategias con eventos.
- Ongoing rule: no promocionar carpetas vacias como contenido validado.

Execution note 2026-06-18:

- `00__EVENT_LIBRARY` was renamed to `00_EVENT_LIBRARY`.
- `01_STRATEGY_LIBRARY` was moved to `03_STRATEGY_LIBRARY`.
- Empty legacy folders were mapped to canonical event-first folders where
  semantics were clear.
- Empty `02_SETUP_TAXONOMY` was removed because setup taxonomy is no longer a
  top-level canonical layer.
- Functional READMEs were added to the active target folders.
- Graphify event-first leaf build is done for `13_TRADING_SYSTEMS/`, but the
  root graph remains pending because it still contains historical trading paths
  and `graphify merge-graphs` is additive, not slice replacement.

### Fase 3 - Data Foundation alignment

- No mover `01_foundations`.
- Crear o actualizar en `00_CTO` solo documentacion arquitectonica que enlace a
  `01_foundations`.
- Dejar claro que los outputs pendientes son:

```text
master_daily_table
master_intraday_table
data_quality_report
symbol_master
corporate_actions_table
calendar_table
```

- La materializacion y gobierno de esos outputs pertenece al modulo 01.

### Fase 4 - Graphify

Despues de cambios estructurales:

1. identificar paths cambiados;
2. mapear slice;
3. reconstruir o actualizar leaf con Graphify oficial;
4. si no hubo renombres ni eliminaciones, `graphify merge-graphs`;
5. si hubo renombres o eliminaciones, no hacer merge aditivo hasta confirmar
   que el root no conserva nodos antiguos del slice;
6. `graphify cluster-only` despues de actualizar el root;
7. `graphify diagnose multigraph`;
8. actualizar `graphify-out/BUILD_MANIFEST.md`;
9. actualizar README/CHANGELOG si cambia scope.

## No-goals

Este refactor no debe:

- reorganizar `01_TSIS_backtest_SmallCaps/01_foundations`;
- mover evidencia historica del modulo 01;
- duplicar schemas, registries, validators o policies;
- convertir `00_private` en autoridad;
- hacer rebuild monolitico de Graphify por defecto;
- borrar referencia externa por limpieza estetica;
- promover AlphaEvolve antes de evaluadores bloqueados.

## Completion criteria

El refactor se considera completo para esta fase cuando:

- `LOCAL_RULES.md` existe y gobierna `00_CTO`;
- `TSIS_LAB_ARCHITECTURE.md` existe como arquitectura promovida;
- cada carpeta top-level tiene rol funcional documentado;
- `13_TRADING_SYSTEMS` es event-first;
- `00_private/arquitectura.md` queda como source note historica;
- `README.md` enlaza los documentos activos;
- `CHANGELOG.md` registra el cambio;
- Graphify leaf queda actualizado; el root queda actualizado solo si no retiene
  rutas antiguas del slice.
