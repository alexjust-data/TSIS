# Estandar De `State Snapshots`

## Objetivo

Este documento fija como deben tratarse los artefactos que resumen el estado de una fase del modulo, por ejemplo:

- `*_review_v0_1.md`
- `*_status_v0_1.md`
- `*_integration_status.md`
- y documentos equivalentes de cierre transversal

Su funcion no es reemplazar policies vivas.
Su funcion es congelar una lectura institucional del estado del modulo en un momento dado.

## Naturaleza Correcta

Un `state snapshot` es:

- un documento de estado
- versionado
- temporalmente valido
- y subordinado a los artefactos vivos mas especificos

No es:

- la policy primaria
- la fuente normativa unica
- ni una verdad eterna del modulo

## Jerarquia

Si existe conflicto entre un `state snapshot` y un documento vivo mas especifico, manda el documento vivo mas especifico.

Documentos vivos tipicos que prevalecen:

- `module_contracts/*.md` de politica primaria
- `contract_registry/*.md`
- `dataset_registry/*.yaml`
- `validators/*.md`
- `data_consumption_policies/*.md`
- readouts activos que se sigan regenerando y manteniendo

## Contenido Minimo Obligatorio

Todo `state snapshot` debe incluir:

### 1. alcance

- que cubre
- que no cubre
- y a que fase del modulo pertenece

### 2. naturaleza del documento

- que es snapshot de estado
- que no sustituye policies vivas
- y que su validez depende del estado versionado

### 3. capas de cierre

- que esta cerrado
- que esta casi cerrado
- que sigue abierto de verdad
- que es deuda metodologica
- que es deuda cosmética

### 4. prioridad recomendada

- siguiente paso fuerte
- siguiente paso de acabado
- y condicion de promocion a consumidores mas delicados

### 5. regla de no obsolescencia

- cuando debe revisarse
- cuando debe reemplazarse
- y que gatillos invalidan su lectura vieja

## Gatillos De Revision Obligatorios

Un `state snapshot` debe revisarse o versionarse de nuevo si ocurre cualquiera de estas condiciones:

- cambia el estado de integracion de una capa critica
- cambia una policy primaria que el snapshot resume
- aparece un consumidor real nuevo con semantica propia
- se cierra una deuda metodologica declarada como abierta
- se abre una deuda nueva que cambia el veredicto global
- cambia de fase el modulo

## Regla De Versionado

Un snapshot no debe reescribirse de forma silenciosa cuando el cambio es estructural.

Regla:

- cambios menores de claridad o enlaces: se puede actualizar la misma version
- cambios de estado institucional real: se crea una version nueva

Ejemplos:

- `foundations_transversal_final_review_v0_1.md`
- luego `foundations_transversal_final_review_v0_2.md`

La version anterior puede seguir existiendo como memoria historica, pero no debe fingirse que describe el presente si ya no lo hace.

## Convencion De Titulo Recomendada

Se recomienda usar nombres que ya indiquen su naturaleza de snapshot:

- `*_review_v0_1.md`
- `*_status_v0_1.md`
- `*_integration_status.md`

y dentro del documento incluir una seccion temprana llamada:

- `Naturaleza Del Documento`

## Regla Editorial

Un snapshot debe ser:

- sintetico
- jerarquico
- y accionable

Debe evitar dos errores:

- convertirse en changelog largo y amorfo
- convertirse en policy duplicada

Su trabajo es responder:

- donde estamos
- que esta realmente cerrado
- que sigue abierto
- y que cambia la prioridad siguiente

## Consecuencia Practica

Este estandar protege al modulo contra dos fallos frecuentes:

- snapshots que envejecen sin que nadie lo note
- documentos de estado que compiten con las policies vivas

La lectura correcta siempre debe ser:

- policy viva para gobernanza diaria
- snapshot versionado para memoria de fase
