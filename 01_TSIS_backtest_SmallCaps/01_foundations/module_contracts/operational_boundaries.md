# Operational Boundaries - Modulo 01

## 1. Rol del documento

Este documento fija los limites operativos del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su funcion es evitar expansion desordenada, ambiguedad de mandato y cambios que erosionen evidencia o contratos durante la fase actual.

## 2. Mandato actual

El mandato actual del modulo es:

`consolidacion institucional`

Esto significa:

- preservar evidencia historica;
- traducir conocimiento auditado a contratos consumibles;
- formalizar policies, schemas, lineage y validators;
- preparar una base institucional para capas downstream.

No significa:

- priorizar features nuevas;
- priorizar RL;
- abrir muchas estrategias nuevas;
- sofisticar simuladores sin cerrar antes las bases upstream;
- o limpiar carpetas por estetica.

## 3. Zonas congeladas

Durante esta fase, las siguientes rutas estan estructuralmente congeladas:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

En estas rutas no se debe:

- reorganizar arboles;
- mover evidencia;
- renombrar por coherencia cosmetica;
- rehacer closeouts o outputs solo para homogeneizar estilo;
- convertir runtime history en una estructura nueva.

## 4. Zonas preservadas pero evaluables

Las siguientes rutas deben preservarse en esta fase, aunque luego puedan recibir indice, contrato o mapeo institucional:

- `00_cto/`
- `01_research/` fuera de la zona congelada estricta
- `02_infrastructure/`

La regla aqui es:

`primero interpretar y mapear; despues decidir si hace falta formalizar o migrar`

## 5. Zonas habilitadas para construccion

La zona principal de construccion nueva es:

- `01_foundations/`

Tambien pueden recibir construccion controlada:

- `src/`
- `scripts/`
- `configs/`
- `docs/`
- `tests/`

Siempre bajo esta condicion:

`la nueva implementacion debe obedecer contratos y no redefinirlos silenciosamente`

## 6. Tipos de cambios permitidos ahora

Durante esta fase si se permiten:

- crear contratos del modulo;
- crear dataset registry;
- crear data consumption policies;
- crear canonical schemas;
- crear promotion states;
- crear ontology, lineage y validators;
- crear documentacion de gobierno local;
- crear builders y validadores de enforcement institucional;
- extraer conclusiones desde evidencia preservada hacia contratos nuevos.

## 7. Tipos de cambios que requieren umbral alto

Se consideran cambios de alta severidad:

- redefinir `good/review/bad`;
- cambiar allowed consumers de un dataset;
- alterar semantica de universe o lifecycle;
- alterar schema canonico;
- reinterpretar closeouts ya estabilizados;
- mover o colapsar arboles historicos;
- introducir nueva autoridad semantica fuera de `01_foundations/`.

Estos cambios deben ir acompanados de:

- razon explicita;
- impacto downstream explicito;
- documentacion local actualizada;
- y changelog si cambia semantica operativa.

## 8. Tipos de cambios que no deben liderar la fase

Aunque tecnicamente puedan existir, no deben gobernar la agenda actual:

- nuevas familias de features;
- nuevas familias de estrategias;
- nuevas capas RL;
- simuladores avanzados no anclados en contracts;
- refactors cosmeticos extensos;
- normalizaciones masivas de notebooks historicos.

## 9. Regla de preservacion

La evidencia historica del modulo tiene valor institucional.

Por tanto:

- no se destruye lineage para ganar orden visual;
- no se borra memoria cientifica para crear una estructura mas limpia;
- no se reemplaza una auditoria por un resumen sin enlazar la evidencia;
- no se declara institucional un output sin contrato, manifest y policy.

## 10. Regla de superposicion

La estrategia oficial de esta fase es:

`preservar la estructura actual + anadir una capa institucional al lado`

No es:

- reescribir todo el research;
- ni migrar todo a una estructura nueva de una vez.

## 11. Condicion de salida de esta fase

La fase de consolidacion institucional solo puede considerarse madura cuando exista, como minimo:

- gobernanza local completa;
- `01_foundations/` operativa;
- contracts del modulo definidos;
- dataset registry inicial;
- data consumption policies iniciales;
- schemas canonicos iniciales;
- estados de promocion definidos;
- validators basicos;
- y relacion explicita entre evidencia preservada y contrato institucional.

## 12. Regla final

Si aparece un conflicto entre:

- velocidad de construccion;
- limpieza superficial;
- o preservacion contractual y trazable;

la prioridad correcta es:

`preservacion contractual y trazable`
