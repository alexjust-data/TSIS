# Layer Model - Modulo 01

## 1. Rol del documento

Este documento define el modelo de capas del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es fijar separacion semantica, direccion de dependencias y responsabilidades institucionales.

No describe solamente carpetas.

Describe:

- que significa cada capa;
- que tipo de objetos puede contener;
- que puede consumir;
- que puede emitir;
- y que dependencias estan permitidas o prohibidas.

## 2. Principio rector

El modulo 01 debe entenderse como un sistema historico de investigacion gobernada.

La regla principal del modelo de capas es:

`cada capa debe tener una semantica clara y no debe redefinir silenciosamente la semantica de otra`

Por tanto:

- una capa downstream no redefine contratos upstream;
- una capa exploratoria no se presenta como capa institucional;
- una capa operativa no nace desde memoria implicita;
- una capa de investigacion no sustituye una capa de contrato.

## 3. Capas del modulo

### Capa 0. Evidencia preservada

Incluye principalmente:

- `00_cto/`
- `01_research/`

Funcion:

- preservar memoria cientifica;
- preservar razonamiento historico;
- preservar closeouts, auditorias, notebooks, decisiones y contexto.

Consume:

- datos, artefactos y resultados historicos;
- observaciones forenses;
- decisiones metodologicas.

Produce:

- evidencia;
- diagnostico;
- hipotesis;
- closeouts;
- justificacion para contratos futuros.

No produce por si sola:

- contratos operativos finales;
- schemas canonicos vigentes;
- politicas institucionales consumibles.

### Capa 1. Foundations institucionales

Incluye:

- `01_foundations/`

Funcion:

- formalizar contratos;
- fijar schemas canonicos;
- fijar politicas de consumo;
- fijar estados de promocion;
- fijar lineage y validators institucionales.

Consume:

- evidencia preservada;
- contratos raiz de TSIS;
- decisiones de certificacion consolidadas.

Produce:

- definiciones operativas explicitas;
- contratos consumibles;
- politicas de uso;
- autoridad semantica local del modulo.

Esta es la capa que traduce:

`auditoria y certificacion -> sistema operativo institucional`

### Capa 2. Implementacion estable

Incluye principalmente:

- `src/`
- `scripts/`
- `configs/`
- `docs/`
- `tests/`

Funcion:

- implementar procesos reproducibles;
- ejecutar validaciones;
- construir artefactos gobernados;
- dar soporte a pipelines y verificaciones institucionales.

Consume:

- contratos de `01_foundations/`;
- configuraciones y manifests;
- datos protegidos sin redefinir su significado.

Produce:

- validadores;
- builders;
- scripts de integracion;
- evidencia reproducible derivada.

No debe:

- crear semantica institucional nueva sin contrato;
- reinterpretar politicas sin actualizar `01_foundations/`.

### Capa 3. Artefactos operativos protegidos

Incluye:

- `data/`
- `run/`
- `runs/`

Funcion:

- contener datos locales protegidos;
- contener outputs runtime;
- contener artefactos historicos y evidencia de ejecucion.

Estas rutas no son la autoridad semantica del modulo.

Son artefactos operativos protegidos y congelados durante la fase actual.

## 4. Subcapas funcionales futuras o ya presentes

Dentro de la evolucion del modulo, las siguientes subcapas funcionales deben interpretarse con separacion clara:

- `reference/universe`
- `market data foundation`
- `features`
- `events`
- `strategy`
- `execution simulation`
- `research programs`

Su semantica esperada es:

### Reference and universe

Define identidad de instrumentos, lifecycle, elegibilidad y universo institucional.

### Market data foundation

Define datasets historicos consumibles como `daily`, `ohlcv_1m`, `quotes`, `trades`, `halts` y equivalentes.

### Features

Define transformaciones derivadas sobre datasets ya certificados y schemas ya fijados.

### Events

Define objetos causales o de estructura de mercado apoyados en contratos upstream.

### Strategy and simulation

Define logica de decision y simulacion, siempre downstream de universe, data y events.

### Research programs

Define estudios, backtests, edge analysis, regime work y preparacion ML sobre contratos y datasets ya institucionalizados.

## 5. Direccion de dependencias permitida

La direccion correcta es:

`evidencia preservada -> foundations -> implementacion estable -> research programado o simulacion`

Se permite:

- extraer conclusiones de auditoria hacia contracts;
- implementar validators a partir de contracts;
- consumir datasets certificados en research y backtests;
- promover logica repetible desde notebooks hacia `src/` o `scripts/`.

No se permite:

- que una estrategia defina la semantica de un dataset;
- que un notebook reescriba silenciosamente una policy canonicamente vigente;
- que un output runtime se convierta en source of truth institucional por costumbre;
- que una necesidad downstream fuerce una redefinicion upstream no documentada.

## 6. Relacion entre auditoria, certificacion y foundations

En este modulo:

- `auditoria` = conocimiento forense;
- `certification` = traduccion a politica operativa;
- `foundations` = contrato institucional consumible.

La consolidacion actual no busca borrar las dos primeras.

Busca encapsularlas en la tercera.

## 7. Regla de evolucion

Toda evolucion estructural futura debe respetar esta secuencia:

1. observar evidencia
2. cerrar interpretacion
3. formalizar contrato
4. implementar validacion o consumo
5. promover uso downstream

Si no existe el paso 3, la evolucion no esta institucionalmente cerrada.

## 8. Regla final

Si existe duda sobre donde vive una definicion, la respuesta correcta es:

- evidencia historica en `00_cto/` o `01_research/`;
- contrato operativo en `01_foundations/`;
- implementacion reproducible en `src/`, `scripts/`, `configs/` o `tests/`;
- artefacto runtime en `data/`, `run/` o `runs/`.
