# Daily Return Labels `<1B>` Promotion Plan `v0_1`

## 1. Rol

Este documento define como pasar `daily_return_labels_v0_1` desde:

- target layer piloto de `daily_adjusted`

hacia:

- target layer diario usable por research, backtest y ML sobre universo `<1B>`.

No declara que esa promocion ya exista.

## 2. Por que esta capa importa para TSIS

TSIS necesita labels defendibles para evaluar hipotesis, entrenar modelos y comparar decisiones.

Un label mal construido puede contaminar todo el research.

En microcaps/small caps el error critico es:

- usar cierres raw;
- dejar que splits/reverse splits/dividendos entren como retorno economico falso;
- y entrenar modelos contra targets contaminados.

Por eso `daily_return_labels` debe nacer desde:

- `daily_adjusted`
- `c_adjusted`

no desde:

- `daily_raw`
- `c`

## 3. Estado actual

Estado actual:

- `pilot_materialization`
- `pilot_target_layer`

Evidencia existente:

- piloto materializado en `E:\TSIS\data\daily_return_labels`;
- `10` tickers;
- `177` parquets;
- years `2005-2026`;
- labels `ret_1d`, `ret_3d`, `ret_5d`;
- provenance `label_source_view = daily_adjusted_v0_1`.

## 4. Lectura correcta en la fase actual

Esta capa no debe confundirse con un set de features.

La pregunta que ya responde el piloto es:

- podemos construir targets diarios economicos usando `daily_adjusted` en vez de raw?

La pregunta que todavia no responde es:

- estos labels estan materializados para todo `<1B>`?
- un modelo entrenado con ellos tiene edge?
- el backtest core ya debe depender de esta raiz?
- la cobertura global esta auditada?

Por tanto, en la fase actual `daily_return_labels` aporta validacion de target semantics.

No aporta todavia:

- edge;
- features;
- ejecucion;
- slippage;
- fills;
- backtest global;
- target layer full-universe.

## 5. Diferencia con `intraday_regime_features`

`intraday_regime_features` puede convertirse en atributos/states.

`daily_return_labels` son outcomes.

La separacion obligatoria es:

- `intraday_regime_features` -> potencial `X`;
- `daily_return_labels` -> `y`;
- backtest/evaluation -> compara decisiones contra outcomes.

No deben mezclarse.

Si un pipeline permite que `ret_1d`, `ret_3d` o `ret_5d` entren como input, ese pipeline tiene leakage.

## 6. Lo que falta para backtest/ML `<1B>`

### A. Universo

Debe definirse el universo objetivo:

- `<1B>`;
- membership temporal;
- survivorship control;
- reglas de elegibilidad compatibles con `reference`.

### B. Cobertura daily_adjusted

Debe verificarse:

- expected ticker-years;
- present ticker-years;
- healthy ticker-years;
- usable ticker-years;
- gaps por ticker;
- nulos por horizonte.

### C. Materializacion separada

La futura promocion `<1B>` debe usar raiz separada:

- `E:\TSIS\data\daily_return_labels_lt1b`

No debe sobreescribir:

- `E:\TSIS\data\daily_return_labels`

que queda como piloto historico.

### D. Auditoria anti-leakage

Debe quedar probado:

- que labels se calculan solo desde `c_adjusted`;
- que no se usa `c raw`;
- que no se incorporan como features;
- que cada horizonte respeta su disponibilidad futura;
- que train/test temporal no filtra informacion posterior.

### E. Auditoria agregada

La corrida `<1B>` debe dejar:

- summary por ticker/year;
- row counts;
- nulos por label;
- distribution stats por label;
- checks de source view;
- manifest de errores;
- manifest de casos extremos;
- readout institucional.

## 7. Fases recomendadas

### Fase 1 - Dry run de cobertura

Objetivo:

- estimar universo esperado;
- contar parquets `daily_adjusted`;
- medir cobertura por ticker/year;
- detectar huecos antes de escribir labels globales.

### Fase 2 - Materializacion controlada

Objetivo:

- escribir labels sobre raiz `_lt1b`;
- no sobreescribir piloto;
- preservar idempotencia;
- dejar summary incremental.

### Fase 3 - Auditoria contractual agregada

Objetivo:

- comprobar schema;
- comprobar source view;
- comprobar nulos esperados;
- comprobar que no hay raw leakage;
- producir casos extremos para inspeccion.

### Fase 4 - Promocion de target layer

Solo despues puede proponerse:

- `ml_target_candidate`
- `backtest_evaluation_candidate`

No:

- feature layer;
- execution signal;
- live signal;
- policy final.

## 8. Condicion para uso en backtest

Un backtest puede usar esta capa solo como:

- outcome;
- target;
- benchmark;
- evaluacion posterior.

Debe declarar:

- universe version;
- label root;
- label contract;
- horizon;
- availability timestamp;
- train/test split;
- leakage policy.

## 9. Veredicto

El siguiente paso natural no es declarar `daily_return_labels` full-universe.

El siguiente paso natural es preparar una promocion `<1B>` disciplinada:

- con universo definido;
- materializacion separada;
- auditoria de coverage;
- auditoria anti-leakage;
- y solo despues consumo por research/backtest/ML.
