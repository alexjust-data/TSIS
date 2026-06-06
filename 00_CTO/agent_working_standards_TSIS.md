# Estándares de calidad para trabajar con agentes IA en el proyecto TSIS

**Proyecto:** Backtesting, Machine Learning y Offline RL para Small Caps / Microcaps  
**Objetivo:** empezar el proyecto con una forma de trabajo profesional, reproducible, segura y escalable usando agentes como Codex, Claude Code, Cursor, Gemini CLI, Jules, Copilot Coding Agent, Devin, etc.

---

## 0. Principio rector

Un agente no debe tratarse como un chatbot al que se le pide “hazme esto”. Debe tratarse como un **miembro técnico del equipo** que necesita:

1. contexto duradero,
2. límites claros,
3. tareas pequeñas,
4. criterios de finalización,
5. pruebas automáticas,
6. trazabilidad,
7. revisión humana,
8. observabilidad,
9. control de versiones,
10. prohibición de modificar datos RAW o resultados científicos sin auditoría.

En un proyecto cuantitativo como TSIS, el estándar debe ser todavía más estricto que en un proyecto web normal, porque un error silencioso puede generar:

- backtests falsos,
- leakage temporal,
- datos contaminados,
- resultados irreproducibles,
- modelos ML sobreajustados,
- decisiones financieras erróneas.

---

## 1. Arquitectura base del proyecto

La estructura principal debe separar claramente:

```text
C:\TSIS_Data\02_backtest_SmallCaps\
│
├── research\
│   ├── 00_raw_polygon
│   ├── 01_data_auditoria_polygon
│   ├── 02_reference_layer
│   ├── 03_universe_builder
│   ├── 04_feature_engine
│   ├── 05_event_engine
│   ├── 06_strategy_engine
│   ├── 07_execution_simulator
│   ├── 08_research_backtests
│   ├── 09_edge_estadistico
│   ├── 10_regime_modeling
│   └── 11_ml_offline_rl
│
├── infrastructure\
│   ├── 12_reporting
│   ├── 13_configs
│   ├── 14_logs
│   └── 15_exports
│
├── docs\
├── tests\
├── scripts\
├── notebooks\
└── AGENTS.md
```

Regla fundamental:

> Los agentes pueden trabajar en código, tests, docs y configs; pero nunca deben modificar datos RAW, resultados finales certificados o experimentos históricos sin una tarea explícita y revisión humana.

---

## 2. Crear `AGENTS.md` desde el día 1

`AGENTS.md` debe ser el archivo principal que leen los agentes antes de tocar el proyecto. Funciona como un “README para agentes”: un lugar predecible donde se explican comandos, convenciones, estructura, límites y criterios de calidad.

Debe vivir en la raíz:

```text
C:\TSIS_Data\02_backtest_SmallCaps\AGENTS.md
```

### 2.1. Contenido mínimo de `AGENTS.md`

```md
# AGENTS.md

## Project purpose
TSIS is a research-grade quantitative trading framework for US small caps / microcaps. It is designed for historical data auditing, universe reconstruction, feature engineering, event detection, strategy backtesting, execution simulation, statistical edge analysis, regime modeling, ML and Offline RL.

## Non-negotiable rules
- Never modify raw market data.
- Never overwrite certified research outputs.
- Never introduce look-ahead bias.
- Never use future data in features.
- Never change strategy logic without adding or updating tests.
- Never optimize parameters directly on final out-of-sample periods.
- Always preserve reproducibility.

## Folder map
- research/00_raw_polygon: immutable raw data.
- research/01_data_auditoria_polygon: data quality checks.
- research/02_reference_layer: structural reference tables.
- research/03_universe_builder: historical tradable universe.
- research/04_feature_engine: market features.
- research/05_event_engine: market events.
- research/06_strategy_engine: theoretical signals.
- research/07_execution_simulator: realistic fills and slippage.
- research/08_research_backtests: validation and robustness.
- research/09_edge_estadistico: statistical edge maps.
- research/10_regime_modeling: hidden state and regime analysis.
- research/11_ml_offline_rl: ML, meta-labeling, imitation learning, offline RL.
- infrastructure/12_reporting: reports and dashboards.
- infrastructure/13_configs: YAML/JSON/TOML configs.
- infrastructure/14_logs: logs and traces.
- infrastructure/15_exports: final exportable outputs.

## Required workflow
Before coding:
1. Read this AGENTS.md.
2. Identify the exact module affected.
3. Explain the intended change.
4. Check existing tests.
5. Make the smallest safe change.
6. Run tests.
7. Summarize what changed and what was not touched.

## Testing commands
- Run unit tests: `pytest tests/unit`
- Run integration tests: `pytest tests/integration`
- Run linting: `ruff check .`
- Run formatting: `ruff format .`

## Data safety
- Raw data is read-only.
- Any generated table must include dataset version, config hash, code version, and timestamp.
- Any backtest output must include the exact config used.

## Coding style
- Prefer explicit code over clever code.
- Prefer pure functions for feature/event/strategy logic.
- Avoid hidden global state.
- Every function that can introduce leakage must document what timestamps it reads.
- Financial calculations must be tested with known examples.

## Done definition
A task is only complete when:
- code runs,
- tests pass,
- outputs are reproducible,
- no raw data was modified,
- assumptions are documented,
- limitations are listed.
```

### 2.2. Sub-`AGENTS.md` por carpeta

En módulos críticos, puede haber instrucciones locales:

```text
research/04_feature_engine/AGENTS.md
research/07_execution_simulator/AGENTS.md
research/11_ml_offline_rl/AGENTS.md
```

Los agentes deben obedecer el archivo más específico aplicable.

Ejemplo para `04_feature_engine/AGENTS.md`:

```md
# Feature Engine Agent Rules

- Never use future candles to compute current features.
- Every feature must declare its lookback window.
- Every feature must declare whether it is daily, intraday, premarket, regular-session, or after-hours.
- Rolling features must be shifted when required to avoid leakage.
- Features must be deterministic and reproducible.
- Add tests for edge cases: missing bars, halts, splits, zero volume, symbol changes.
```

---

## 3. Estándar de contexto para cada tarea

Un agente produce mejores resultados cuando recibe una tarea con cuatro piezas:

```text
Goal
Context
Constraints
Done when
```

### Plantilla obligatoria para pedir trabajo a un agente

```md
## Goal
What should be built, fixed, researched, or changed?

## Context
Which folder, files, config, previous decision, bug, or output matters?

## Constraints
What must not be touched? What standards must be followed?

## Done when
How do we know the task is complete?
```

### Ejemplo malo

```text
Hazme el universe builder.
```

### Ejemplo bueno

```md
## Goal
Create the first version of `universe_daily.parquet` from the reference layer.

## Context
Use only `research/02_reference_layer/ticker_daily_reference.parquet` and trading calendar files. Do not use OHLCV yet.

## Constraints
- No survivorship bias.
- No future information.
- Do not write into raw data folders.
- Output must be partitioned by year.

## Done when
- A script exists in `scripts/build_universe_daily.py`.
- Unit tests cover active/delisted tickers.
- Output schema is documented.
- The build command is added to README or AGENTS.md.
```

---

## 4. Unidad mínima de trabajo para agentes

No pedir a un agente “construye todo el sistema”.

Pedir unidades pequeñas y verificables:

```text
malo: construye el backtester completo
bueno: crea el schema de executed_trades.parquet
bueno: implementa slippage_model_v01
bueno: añade test de halt behavior
bueno: genera reporte de MAE/MFE para una estrategia ya ejecutada
```

Regla:

> Una tarea de agente debe poder revisarse en un diff razonable.

---

## 5. Workflow estándar: de idea a producción

### Fase 0 — Setup inicial del repositorio

Objetivo: crear una base limpia para que agentes y humanos trabajen sin caos.

Checklist:

- Crear repo Git.
- Crear estructura de carpetas.
- Crear `AGENTS.md` raíz.
- Crear `README.md` humano.
- Crear `docs/architecture.md`.
- Crear `docs/data_contracts.md`.
- Crear `docs/research_protocol.md`.
- Crear `tests/` desde el día 1.
- Añadir `.gitignore` para datos pesados, logs y outputs.
- Añadir `pyproject.toml` con lint, format, test.
- Añadir `pre-commit`.
- Añadir convenciones de naming.

No avanzar a research hasta que esto exista.

---

### Fase 1 — Data contracts

Antes de escribir pipelines, definir contratos de datos.

Cada tabla debe tener:

- nombre,
- propósito,
- owner,
- input sources,
- output path,
- schema,
- primary key,
- partitioning,
- timestamp semantics,
- leakage risks,
- quality checks,
- versioning.

Ejemplo:

```md
# Data Contract: master_daily_table

## Primary key
(date, ticker)

## Inputs
- universe_daily
- ohlcv_daily
- ohlcv_1m
- reference_layer
- halts

## Forbidden
- No future returns.
- No labels.
- No strategy outputs.

## Required metadata
- build_timestamp
- config_hash
- code_version
- data_version
```

---

### Fase 2 — Pipelines deterministas

Los primeros pipelines deben ser simples, deterministas y testeables:

1. auditoría de datos,
2. reference layer,
3. universe builder,
4. feature engine,
5. event engine.

Cada pipeline debe:

- leer inputs versionados,
- validar schema,
- generar outputs nuevos,
- escribir logs,
- escribir metadata,
- no sobrescribir outputs certificados,
- tener tests.

---

### Fase 3 — Research reproducible

Cada experimento debe tener:

```text
experiment_id
strategy_id
config_hash
data_version
code_version
train_period
test_period
validation_method
cost_model
slippage_model
result_path
```

No aceptar resultados sin metadata.

Regla:

> Si no puedes reconstruir un resultado, ese resultado no existe.

---

### Fase 4 — Backtesting científico

Los agentes pueden ayudar a codificar backtests, pero no deben decidir por sí solos que una estrategia “funciona”.

Requisitos mínimos:

- walk-forward,
- IS/OOS separado,
- purged validation si hay labels solapadas,
- embargo cuando haya dependencia temporal,
- costes,
- slippage,
- spread,
- liquidez,
- halts,
- capacity analysis,
- sensibilidad de parámetros,
- degradación IS/OOS.

---

### Fase 5 — ML / Meta-labeling

ML sólo debe entrar cuando ya existan:

- data contracts,
- features reproducibles,
- labels correctos,
- validation protocol,
- leakage checks,
- baseline rule-based model.

Prohibido:

```text
usar ML para encontrar magia en datos sin teoría
```

Permitido:

```text
usar ML para descubrir variables importantes, mejorar filtros, meta-labeling, sizing y ejecución
```

---

### Fase 6 — Offline RL / Imitation Learning

Offline RL sólo debe entrar cuando existan:

- state representation,
- action space,
- reward function,
- execution simulator,
- expert trajectories,
- baseline policy,
- offline validation,
- safety constraints.

Regla:

> Offline RL no debe descubrir el edge desde cero. Debe optimizar políticas alrededor de edges previamente investigados.

---

### Fase 7 — Producción / Paper trading

Antes de producción:

- frozen config,
- frozen model,
- frozen dataset version,
- monitoring,
- logging,
- rollback plan,
- kill switch,
- daily report,
- drift detection,
- slippage monitoring,
- human approval gates.

---

## 6. Estándar de revisión humana

Todo output de agente debe pasar por revisión humana si afecta:

- data cleaning,
- feature logic,
- labels,
- strategy logic,
- execution simulation,
- backtest validation,
- ML training,
- RL reward,
- risk management,
- exports finales.

Revisión mínima:

```text
1. ¿Qué cambió?
2. ¿Qué no cambió?
3. ¿Qué assumptions introdujo?
4. ¿Qué tests pasan?
5. ¿Dónde puede haber leakage?
6. ¿El resultado es reproducible?
7. ¿Hay impacto financiero?
```

---

## 7. Estándar de commits y ramas

### Branches

```text
main
research/dev
feature/<module>-<task>
fix/<module>-<bug>
experiment/<strategy>-<id>
```

### Commits

Formato:

```text
[module] action: short description
```

Ejemplos:

```text
[feature_engine] add premarket volume feature
[universe_builder] fix delisted ticker handling
[execution_simulator] add conservative slippage model
[tests] add halt overlap tests
```

---

## 8. Estándar de documentación

Cada módulo debe tener:

```text
README.md
AGENTS.md si es crítico
schemas/
examples/
tests/
```

Cada función crítica debe documentar:

- qué hace,
- qué inputs espera,
- qué outputs genera,
- qué timestamps usa,
- qué assumptions tiene,
- qué riesgos de leakage existen.

---

## 9. Estándar de seguridad para agentes

Los agentes NO deben tener permisos ilimitados.

### Permisos recomendados

| Zona | Permiso agente |
|---|---|
| raw data | read-only |
| code | read/write con PR |
| configs | read/write con revisión |
| logs | write |
| exports | write controlado |
| certified outputs | read-only |
| credentials | no access |
| broker/live trading | no access sin approval |

---

## 10. Estándar de observabilidad

Todo sistema con agentes debe registrar:

- user/task request,
- agent used,
- model/tool version,
- files read,
- files modified,
- commands executed,
- tests run,
- outputs generated,
- errors,
- cost/time,
- human approval.

Ejemplo de log:

```json
{
  "task_id": "FEAT-0042",
  "agent": "codex",
  "module": "04_feature_engine",
  "files_modified": ["features/premarket.py"],
  "commands_run": ["pytest tests/unit/test_premarket.py"],
  "tests_passed": true,
  "raw_data_modified": false,
  "review_required": true
}
```

---

## 11. Estándar para prompts de agentes

### Prompt de implementación

```md
You are working inside the TSIS SmallCaps research framework.

Read AGENTS.md first.

Task:
<describe task>

Module:
<folder>

Constraints:
- Do not modify raw data.
- Do not introduce look-ahead bias.
- Add or update tests.
- Keep the change minimal.

Done when:
- Tests pass.
- Schema is documented.
- Assumptions are listed.
- Output is reproducible.

Before coding, summarize your plan.
```

### Prompt de revisión

```md
Review this diff as a quant research code reviewer.

Focus on:
- leakage,
- timestamp correctness,
- reproducibility,
- data contracts,
- test coverage,
- financial logic,
- hidden assumptions.

Do not rewrite everything. List blocking issues first.
```

### Prompt de debugging

```md
Debug this failing pipeline.

Rules:
- Do not change business logic until root cause is identified.
- First inspect logs and failing tests.
- Propose hypotheses.
- Make the smallest fix.
- Add regression test.
```

---

## 12. Estándar de uso por herramienta

### Codex

Usarlo para:

- implementar scripts,
- refactorizar,
- crear tests,
- arreglar bugs,
- trabajar con AGENTS.md,
- tareas de repo bien delimitadas.

Mejor práctica:

- prompt con Goal/Context/Constraints/Done when,
- pedir plan antes del cambio,
- exigir tests,
- revisar diff.

### Claude Code

Usarlo para:

- exploración de codebase,
- refactors largos,
- debugging multiarchivo,
- documentación técnica,
- razonamiento sobre arquitectura.

Mejor práctica:

- gestionar contexto,
- usar `CLAUDE.md` o `AGENTS.md`,
- dividir sesiones largas,
- pedir resúmenes de estado,
- no dejar que acumule demasiado contexto inútil.

### Cursor / Copilot / IDE agents

Usarlos para:

- edición asistida,
- autocompletado,
- tests locales,
- revisión rápida,
- navegación de código.

### Agentes remotos tipo Devin / Jules / Copilot Coding Agent

Usarlos sólo con:

- issues muy definidos,
- branch aislada,
- permisos limitados,
- tests obligatorios,
- PR review.

---

## 13. Checklist antes de dejar trabajar a un agente

```text
[ ] Existe AGENTS.md actualizado.
[ ] La tarea tiene Goal/Context/Constraints/Done when.
[ ] La carpeta afectada está clara.
[ ] Hay tests o se piden tests nuevos.
[ ] Los datos RAW están protegidos.
[ ] Hay branch separada.
[ ] Está claro qué outputs puede generar.
[ ] Está claro qué NO puede tocar.
```

---

## 14. Checklist después de que trabaje un agente

```text
[ ] Revisé el diff.
[ ] Revisé archivos modificados.
[ ] Revisé que no tocó RAW.
[ ] Revisé tests.
[ ] Revisé assumptions.
[ ] Revisé posible leakage.
[ ] Revisé que outputs tienen metadata.
[ ] Revisé logs.
[ ] Aprobé o rechacé el cambio.
```

---

## 15. Estándar específico para TSIS: errores prohibidos

Un cambio se rechaza automáticamente si:

- usa datos futuros para calcular features actuales,
- mezcla train/test aleatoriamente en series temporales,
- modifica raw data,
- sobrescribe resultados sin versionar,
- introduce parámetros hardcodeados sin config,
- genera backtests sin costes,
- genera labels sin timestamps de inicio/fin,
- no documenta schema,
- no añade tests en lógica crítica,
- no registra logs.

---

## 16. Roadmap operativo recomendado

### Semana 1 — Fundaciones

- Crear repo.
- Crear estructura.
- Crear AGENTS.md.
- Crear README humano.
- Crear data contracts iniciales.
- Crear pyproject, ruff, pytest.
- Crear carpeta tests.

### Semana 2 — Data audit + reference layer

- Crear scripts de auditoría.
- Crear reference layer.
- Crear schemas.
- Crear logs.
- Crear tests de datos.

### Semana 3 — Universe Builder

- Crear `universe_daily`.
- Validar delistings.
- Validar active/inactive.
- Tests contra survivorship bias.

### Semana 4 — Master Daily Table v0

- Crear features básicas:
  - gap,
  - volume,
  - rvol,
  - dollar volume,
  - range,
  - close_near_hod.
- Documentar schema.
- Tests anti-leakage.

### Semana 5 — Event Engine v0

- EVENT_GAP_UP.
- EVENT_RVOL_EXPLOSION.
- EVENT_HOD_BREAK.
- EVENT_CLOSE_NEAR_HOD.

### Semana 6 — Strategy Engine v0

- Primer setup mecánico:
  - Gap&Go v0.
- Señales teóricas, sin ejecución realista todavía.

### Semana 7 — Execution Simulator v0

- Fill ideal.
- Fill bid/ask.
- Slippage básico.
- Comisiones.

### Semana 8 — Backtest científico v0

- Walk-forward básico.
- Reportes.
- Edge maps.
- Revisión manual de trades.

### Después

- Microestructura.
- Meta-labeling.
- Imitation learning.
- Offline RL.
- Paper trading.
- Producción controlada.

---

## 17. Definición de producción

Una estrategia o modelo sólo puede llamarse “production-ready” si cumple:

```text
[ ] Dataset versionado.
[ ] Config congelada.
[ ] Código versionado.
[ ] Tests pasan.
[ ] Backtest reproducible.
[ ] Walk-forward validado.
[ ] Costes incluidos.
[ ] Slippage incluido.
[ ] Halts considerados.
[ ] Riesgo definido.
[ ] Logs activos.
[ ] Monitoring activo.
[ ] Kill switch definido.
[ ] Human approval definido.
```

---

## 18. Conclusión

Trabajar con agentes no consiste en pedirles que “hagan código”.

Consiste en construir un sistema donde los agentes puedan operar dentro de un marco:

- seguro,
- auditable,
- reproducible,
- testeable,
- científicamente válido,
- alineado con la arquitectura del proyecto.

La prioridad inicial de TSIS no debe ser velocidad.

Debe ser:

```text
calidad estructural desde el día 1
```

Si el framework nace ordenado, los agentes multiplicarán la productividad. Si nace desordenado, los agentes multiplicarán el caos.

---

# Fuentes consultadas

1. OpenAI Codex Best Practices: https://developers.openai.com/codex/learn/best-practices
2. Anthropic Claude Code Best Practices: https://code.claude.com/docs/es/best-practices
3. AGENTS.md open format: https://agents.md/
4. Google Cloud: A developer's guide to production-ready AI agents: https://cloud.google.com/blog/products/ai-machine-learning/a-devs-guide-to-production-ready-ai-agents
5. Microsoft Learn: Observability for Generative AI and agentic AI systems: https://learn.microsoft.com/en-us/security/zero-trust/sfi/observability-ai-systems
6. Microsoft Azure Agent Factory observability best practices: https://azure.microsoft.com/en-us/blog/agent-factory-top-5-agent-observability-best-practices-for-reliable-ai/
