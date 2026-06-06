# 01_TSIS_backtest_SmallCaps

Modulo de research historico, certificacion de datos, formalizacion de estados de mercado y backtesting con ejecucion realista para TSIS.

Este modulo es la capa de investigacion y simulacion historica de TSIS para microcaps y small caps.
No debe tratarse como un sandbox generico de notebooks ni como una coleccion suelta de scripts.

Su funcion es:

- construir datasets y universos historicos defendibles;
- auditar y certificar calidad de market data;
- formalizar features, eventos, estados y objetos de research;
- simular ejecucion con restricciones realistas;
- producir evidencia reproducible para promocion, cuarentena o descarte;
- soportar capas downstream live y offline RL sin redefinir silenciosamente semantica upstream.

## Fase actual

La fase actual del modulo es:

`consolidacion institucional`

Eso significa que la prioridad inmediata no es:

- multiplicar features nuevas;
- abrir mucho trabajo RL;
- abrir muchas estrategias nuevas;
- ni sofisticar simuladores antes de cerrar contratos.

La prioridad inmediata es:

- preservar memoria cientifica;
- formalizar gobernanza local;
- convertir conocimiento auditado en contratos institucionales explicitos;
- construir una nueva capa operativa al lado del arbol actual de research.

## Regla dura de preservacion

Este modulo ya contiene una gran cantidad de trabajo acumulado:

- auditoria;
- certificacion;
- notebooks historicos;
- scripts;
- outputs;
- artefactos runtime;
- y evidencia de decisiones.

La estrategia correcta es:

`preservar la estructura actual de evidencia + construir una capa operativa institucional al lado`

No:

`sustituir la estructura actual`

## Zonas de no tocar

Las siguientes rutas estan congeladas durante la fase actual y no deben reorganizarse estructuralmente:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Eso implica:

- no renombrar esos arboles;
- no mover sus contenidos;
- no colapsarlos en una estructura "mas limpia";
- no borrar evidencia historica;
- no reescribir outputs in place;
- no normalizarlos por estetica.

Estas rutas representan:

- lineage historico de auditoria;
- evidencia de certificacion;
- historia runtime;
- memoria critica para reproducibilidad.

## Estructura conceptual del modulo

Hoy este modulo debe entenderse en cuatro zonas.

### 1. Memoria cientifica y de auditoria preservada

- `00_cto/`
- `01_research/`
- especialmente `01_research/01_auditoria_RAW_DATA/`

### 2. Artefactos operativos protegidos

- `data/`
- `run/`
- `runs/`

### 3. Capa estable de implementacion

- `src/`
- `scripts/`
- `configs/`
- `docs/`
- `tests/`

### 4. Nueva capa institucional a construir

- `01_foundations/`

Esta es la capa semantica-operacional que hoy falta en el modulo.

## Por que existe 01_foundations

El modulo ya contiene mucho conocimiento valido distribuido entre:

- auditorias;
- closeouts;
- notas de certificacion;
- crosswalks;
- razonamiento en notebooks;
- discusiones de policies;
- outputs historicos.

Lo que todavia falta es una capa compacta para:

- contratos del modulo;
- ontology;
- promotion states;
- dataset registry;
- canonical schemas;
- data consumption policies;
- lineage maps;
- validators;
- contract registries.

Ese trabajo nuevo debe vivir en:

- `01_foundations/`

## Orden inmediato de construccion

El orden recomendado para la fase actual es:

1. completar `README.md`
2. completar `AGENTS.md` local
3. completar `LOCAL_RULES.md`
4. completar `CHANGELOG.md`
5. crear `01_foundations/`
6. empezar por `01_foundations/module_contracts/`

## Orden de lectura

Antes de cambiar algo en este modulo, leer en este orden:

1. `C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md`
2. `C:\TSIS_Data\PROJECT_RULES.md`
3. `C:\TSIS_Data\VERSIONING_STANDARDS.md`
4. `C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md`
5. `C:\TSIS_Data\RESEARCH_PHILOSOPHY.md`
6. `AGENTS.md` local
7. `LOCAL_RULES.md` local
8. `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
9. `01_foundations/module_contracts/event_families_and_reference_inventory.md`
10. `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
11. `01_foundations/module_contracts/price_views_registry.md`
12. `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`
13. `01_foundations/module_contracts/external_price_comparison_caveats.md`
14. `01_foundations/module_contracts/policy_explanation_standard.md`

Estos documentos adicionales no son lectura opcional.

Son lectura obligatoria cuando el trabajo toque:

- datasets;
- price views;
- corporate actions;
- reconciliacion externa;
- backtest;
- ML;
- o inspeccion institucional de evidencia.

## Regla general de explicacion de evidencia

Toda evidencia de inspeccion del modulo debe presentarse de forma didactica y decisional.

Para cada:

- grafico
- tabla
- ejemplo
- familia de casos
- y bloque visual

debe quedar claro:

- `que muestra`
- `responde`
- `no responde`
- `consecuencia`

La idea es evitar dos fallos tipicos:

1. describir solo lo visible sin decir que pregunta resuelve;
2. asumir que el lector entiende el significado de un bucket por su nombre tecnico.

En este modulo, una imagen o tabla no debe tratarse como decoracion.

Debe dejar claro:

- que preguntas permite contestar;
- cuales no;
- y que decision institucional, operativa o metodologica cambia.

## No-objetivos de la fase actual

La fase actual no debe confundirse con:

- limpieza masiva de carpetas;
- migracion de notebooks por estetica;
- sustitucion de arboles historicos por un arbol nuevo limpio;
- ni una declaracion prematura de cierre institucional.

El objetivo actual es:

`formalizar como el modulo piensa, certifica, promociona y consume conocimiento auditado`

## Regla final

Si existe tension entre:

- limpieza estructural;
- preservacion de evidencia historica;
- o construccion de contratos institucionales explicitos;

la opcion correcta en esta fase es:

`preservar evidencia primero, formalizar contratos despues, reorganizar solo cuando este semantica y operativamente justificado`

## Mandatory certification source reading

- `01_foundations/module_contracts/auditoria_and_certification_source_hierarchy.md` when working any certified block (`daily`, `quotes`, `trades`).
