# Module Contracts Migration Execution Plan v0.1

## Rol

Este documento prepara la migracion fisica de `01_foundations/module_contracts/` para que pueda ejecutarla otro agente de forma segura y trazable.

No ejecuta la migracion.

Su funcion es dejar preparado:

- el orden correcto;
- los lotes de riesgo;
- los checks obligatorios;
- y los criterios de parada.

## Regla principal

No debe ejecutarse una migracion masiva de golpe.

La migracion correcta debe ser:

1. incremental;
2. por lotes pequenos;
3. con verificacion post-fase;
4. y con posibilidad de detenerse sin dejar el sistema en un estado ambiguo.

## Artefactos previos que el agente debe usar

Antes de tocar nada, el agente debe leer como minimo:

- [README.md](./README.md)
- [module_contracts_migration_map_v0_1.md](./module_contracts_migration_map_v0_1.md)
- [module_contracts_reference_pre_audit_v0_1.md](./module_contracts_reference_pre_audit_v0_1.md)
- [state_snapshot_standard.md](./state_snapshot_standard.md)

## Supuesto operativo

La migracion fisica futura consiste en mover documentos planos desde:

- `01_foundations/module_contracts/`

hacia subcarpetas como:

- `module_contracts/daily/`
- `module_contracts/quotes/`
- `module_contracts/trades/`
- `module_contracts/minute/`
- `module_contracts/transversal/`
- `module_contracts/consumers/`
- `module_contracts/governance/`

## Criterio de seguridad

Un lote solo puede ejecutarse si cumple todo esto:

1. sus targets estan claramente mapeados en `module_contracts_migration_map_v0_1.md`;
2. se conocen sus referencias previas en la pre-auditoria;
3. el lote no mezcla demasiados documentos hipercitados y de alto acoplamiento;
4. existe verificacion post-lote antes de pasar al siguiente.

## Lotes recomendados

### Fase 0. Preparacion operativa

No mover nada todavia.

Objetivo:

- preparar el entorno y las reglas para que la migracion posterior no sea improvisada.

Tareas:

- confirmar que el mapa de migracion sigue vigente;
- confirmar que la pre-auditoria sigue vigente;
- regenerar, si hace falta, la pre-auditoria justo antes de la migracion real;
- definir donde quedara el log de ejecucion del agente;
- y definir si se hara un lote por turno o varios.

Salida minima esperada:

- decision de lote inicial aprobada;
- y fecha/commit/logico de arranque de migracion.

### Fase 1. Bajo riesgo

Empezar por documentos con:

- pocas referencias;
- poco acoplamiento relativo;
- y sin rol de indice maestro ni policy central hipercitada.

Buenos candidatos iniciales:

- algunos documentos `daily/*` de baja fan-out;
- algunos documentos `minute/*` poco citados;
- artefactos de resultados o pilotos con `1-2` referencias.

Evitar aqui:

- `policy_explanation_standard.md`
- `price_semantics_and_adjustment_policy.md`
- `pipeline_price_view_policy.md`
- `external_price_comparison_caveats.md`
- `market_session_scope.md`

### Fase 2. Riesgo medio

Mover documentos con:

- `3-6` referencias;
- acoplamiento moderado;
- y relaciones claras con un dominio unico.

Buenos candidatos:

- contratos de consumidores;
- documentos `daily` ya bien encapsulados;
- documentos `minute` ya bien cerrados.

### Fase 3. Riesgo alto

Mover documentos muy citados o muy transversales:

- `policy_explanation_standard.md`
- `price_semantics_and_adjustment_policy.md`
- `external_price_comparison_caveats.md`
- `pipeline_price_view_policy.md`
- `market_session_scope.md`

Tambien entran aqui:

- `README.md`
- snapshots de governance
- indices si su reubicacion afecta navegacion transversal

Esta fase no debe abrirse hasta que las anteriores hayan quedado verificadas.

## Checklist de entrada por lote

Antes de mover un lote, el agente debe comprobar:

1. que todos los documentos del lote aparecen en el mapa de migracion;
2. que conoce su `future_target_path`;
3. que tiene listado de `source_files` afectados en la pre-auditoria;
4. que ha identificado si existen enlaces markdown relativos internos entre documentos del propio lote;
5. que sabe si el lote afecta:
   - `CHANGELOG.md`
   - `AGENTS.md`
   - `LOCAL_RULES.md`
   - `dataset_registry/*.yaml`
   - `validators/*.md`
   - `inspection_dossiers/*.md`
   - notebooks `.ipynb`

Si alguna de estas respuestas es ambigua, el lote no debe empezar.

## Checklist de ejecucion por lote

Durante el lote, el agente debe:

1. mover solo los documentos del lote;
2. actualizar sus referencias internas obvias;
3. actualizar referencias externas en el repo segun la pre-auditoria;
4. no mezclar en el mismo lote reestructuracion editorial no relacionada;
5. dejar trazabilidad en `CHANGELOG.md`.

## Checklist de salida por lote

Despues de cada lote, el agente debe comprobar:

1. que los documentos movidos existen en su path nuevo;
2. que ya no quedan referencias activas al path antiguo para esos documentos concretos;
3. que los links markdown relativos afectados siguen resolviendo bien;
4. que los registry entries y validators afectados apuntan a rutas vigentes;
5. que el `README` y los indices siguen siendo navegables;
6. que no aparecen nuevos documentos huerfanos ni duplicados ambiguos.

## Criterio de parada

La migracion debe detenerse inmediatamente si ocurre cualquiera de estas condiciones:

- aparecen referencias rotas que el agente no puede resolver con certeza;
- el lote actual obliga a reinterpretar el mapa de migracion;
- se detectan referencias no previstas en notebooks o generadores automaticos;
- la actualizacion de rutas empieza a exigir cambios semanticos no relacionados con la migracion;
- el agente no puede demostrar con claridad que el lote quedo consistente.

## Regla sobre referencias antiguas

Hasta que toda la migracion haya terminado, pueden coexistir:

- documentos ya movidos;
- referencias antiguas historizadas en snapshots o changelog;
- y paths nuevos para lectura viva.

Por eso, cualquier agente debe asumir:

- no toda referencia antigua es error;
- algunas pueden ser historicas y legitimas;
- la resolucion correcta se hace contra el mapa de migracion y el contexto del documento.

## Lo que no debe hacer el agente

- no mover todo de una vez;
- no corregir rutas por intuicion;
- no mezclar migracion fisica con refactor semantico;
- no borrar rastros historicos validos del changelog o snapshots;
- no asumir que una referencia antigua en un documento historico debe reescribirse siempre.

## Handoff recomendado

Si otro agente toma esta tarea, deberia responder primero a estas preguntas antes de mover nada:

1. que lote exacto va a ejecutar;
2. cuantos documentos contiene;
3. cuantos `source_files` afectados tiene en la pre-auditoria;
4. que checks de salida va a usar;
5. y bajo que condicion se detendra sin seguir.

## Veredicto

La migracion ya no debe empezar desde cero.

Con este documento, el trabajo correcto para otro agente es:

- ejecutar una migracion por fases;
- con riesgos acotados;
- y con prueba explicita de consistencia despues de cada lote.
