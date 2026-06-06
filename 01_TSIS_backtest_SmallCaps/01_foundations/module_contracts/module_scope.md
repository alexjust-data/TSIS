# Module Scope - Modulo 01

## 1. Rol de este documento

`module_scope.md` define el alcance institucional de:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

No es un documento de filosofia general de TSIS.
No es un changelog.
No es un documento de implementacion tecnica detallada.

Su funcion es fijar:

- que es exactamente este modulo;
- que responsabilidad institucional tiene;
- que zonas pertenecen a su memoria preservada;
- que zonas estan protegidas;
- que zonas pueden evolucionar normalmente;
- y donde se construye la nueva capa institucional.

## 2. Que es el modulo 01

`01_TSIS_backtest_SmallCaps` es la capa historica de investigacion, auditoria, formalizacion y simulacion de TSIS.

Su mision institucional es:

- construir datasets historicos defendibles;
- reconstruir universos point-in-time;
- auditar y certificar market data y capas auxiliares;
- formalizar features, eventos, estados y objetos de research;
- evaluar hipotesis con simulacion y validacion reproducible;
- servir de fuente upstream disciplinada para live y offline RL.

No debe entenderse como:

- un simple backtester;
- un contenedor de notebooks;
- un sandbox de ideas de estrategia;
- ni un repositorio informal de outputs.

## 3. Que NO pertenece al mandato actual del modulo

Aunque el modulo contiene piezas relacionadas con estrategia, simulacion avanzada o preparacion ML, su prioridad institucional actual no es:

- proliferar nuevas features;
- abrir mas estrategias;
- empujar RL antes de cerrar contratos;
- ni sofisticar simuladores sin semantica consolidada upstream.

La prioridad actual del modulo es:

`consolidacion institucional del conocimiento auditado`

## 4. Alcance funcional del modulo

El alcance funcional propio del modulo 01 incluye:

- `reference and universe`
- `market data audit and certification`
- `feature formalization`
- `event formalization`
- `strategy research`
- `execution-aware backtesting`
- `edge evaluation`
- `regime research`
- `ML/RL preparation`

Pero no todo ese alcance esta en el mismo estado de madurez.

## 5. Zonas estructurales del modulo

Durante la fase actual, este modulo debe leerse en cuatro zonas estructurales.

### 5.1. Memoria cientifica y de auditoria preservada

Esta zona contiene conocimiento historico, razonamiento, evidencia y cierres de auditoria/certificacion.

Incluye principalmente:

- `00_cto/`
- `01_research/`
- en especial `01_research/01_auditoria_RAW_DATA/`

Esta zona debe preservarse como memoria cientifica viva del modulo.

### 5.2. Artefactos operativos protegidos

Esta zona contiene datos locales y huella runtime historica.

Incluye:

- `data/`
- `run/`
- `runs/`

No es source of truth institucional en si misma, pero si memoria operativa critica para reproducibilidad y trazabilidad local.

### 5.3. Capa estable de implementacion

Esta zona contiene codigo y soporte tecnico que puede evolucionar con disciplina normal.

Incluye:

- `src/`
- `scripts/`
- `configs/`
- `docs/`
- `tests/`

### 5.4. Nueva capa institucional

Esta zona no sustituye el arbol actual.
Se construye al lado para formalizar contratos y politicas del modulo.

Incluye:

- `01_foundations/`

Su funcion es convertir conocimiento auditado en:

- contracts;
- registries;
- schemas;
- policies;
- lineage;
- validators;
- promotion states.

## 6. Zonas congeladas

Durante la fase actual, las siguientes rutas quedan congeladas estructuralmente:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Congeladas significa:

- no renombrar;
- no mover;
- no aplastar en un arbol nuevo;
- no limpiar por estetica;
- no reescribir evidencia historica in place.

Estas rutas deben tratarse como:

- evidencia historica preservada;
- o artefactos operativos protegidos.

## 7. Estrategia correcta de evolucion

La estrategia correcta de evolucion del modulo 01 es:

`preservar estructura actual de evidencia + anadir capa institucional al lado`

No:

`reemplazar el arbol actual por una estructura nueva limpia`

Por tanto, cualquier consolidacion correcta debe:

- encapsular conclusiones;
- referenciar closeouts y auditorias existentes;
- extraer semantica estable;
- construir nuevos contratos en `01_foundations/`;
- preservar lineage y memoria historica.

## 8. Nueva capa institucional minima esperada

La nueva capa institucional del modulo debe poder alojar, como minimo:

- `module_contracts/`
- `ontology/`
- `promotion_states/`
- `dataset_registry/`
- `contract_registry/`
- `canonical_schemas/`
- `data_consumption_policies/`
- `lineage/`
- `validators/`

No todos estos componentes tienen que existir completos hoy, pero este es el alcance correcto de la capa.

## 9. Relacion con auditoria y certificacion

La auditoria y certificacion historicas no deben rehacerse como si no existieran.

La relacion correcta es:

- `01_research/01_auditoria_RAW_DATA/...` produce evidencia;
- `00_data_certification/auditoria/` produce diagnostico y closeouts por bloque;
- `00_data_certification/certification/` traduce parte de ese conocimiento a politicas de uso;
- `01_foundations/` debe convertir esas conclusiones en contratos institucionales consumibles.

## 10. Relacion con capas downstream

Este modulo es upstream de:

- live
- offline RL

Por tanto, no debe exportar semantica ambigua.

Lo que se promueva desde este modulo hacia consumo downstream debe pasar por:

- contratos explicitos;
- schemas canonicos;
- consumption policies;
- promotion states;
- y suficiente trazabilidad.

## 11. Regla final del alcance

El modulo 01 no esta en una fase de sustitucion de arboles ni de limpieza cosmetica.

Esta en una fase de:

`preservacion de evidencia + formalizacion institucional`

Toda decision estructural local debe evaluarse contra esa regla.
