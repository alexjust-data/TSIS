# Intraday Regime Features `<1B>` Promotion Plan `v0_1`

## 1. Rol

Este documento define como pasar `intraday_regime_features_v0_1` desde:

- consumidor piloto validado de `1m_split_normalized`

hacia:

- capa de features/states usable por backtest y ML sobre universo `<1B>`.

No declara que esa promocion ya exista.

## 2. Por que esta capa importa para TSIS

El objetivo de TSIS no es solo simular reglas sobre barras.

TSIS busca construir estados de mercado defendibles para research, backtesting, ML y RL.

Por eso `intraday_regime_features` es estructuralmente relevante:

- transforma `1m raw` y `1m_split_normalized` en features/states;
- separa verdad local intrasesion de comparabilidad entre sesiones;
- evita que el modelo aprenda falsos gaps o shocks mecanicos de split;
- y crea una primera base para representar regimen intradia sin mezclarlo con ejecucion fina.

## 3. Estado actual

Estado actual:

- `Nivel 3 - Pilotada`
- `pilot_semantic_validation_consumer`

Evidencia existente:

- piloto materializado en `E:\TSIS\data\intraday_regime_features`;
- 8 tickers piloto;
- 8 parquets;
- 243 filas `ticker-day`;
- readout semantico con casos positivos, frontera y controles;
- prueba de que `1m_split_normalized` corrige falsos shocks en features cross-session.

## 4. Lectura correcta en la fase actual

Esta capa no debe confundirse con el siguiente bloque productivo del backtest.

La pregunta que ya responde el piloto es:

- si una feature cruza sesiones, usa precios comparables o puede absorber splits como alpha falso?

La pregunta que todavia no responde es:

- estas features tienen edge economico?
- mejoran una estrategia?
- deben entrar en el backtest core?
- deben entrenar un modelo ML sobre `<1B>`?

Por tanto, en la fase actual `intraday_regime_features` aporta una validacion arquitectonica, no una feature layer final.

El valor actual es:

1. demostrar que `1m_split_normalized` corrige algo downstream y no solo cambia columnas;
2. fijar la regla futura de vistas:
   - cross-session -> `1m_split_normalized`;
   - intrasesion local -> `1m raw`;
3. dejar un template minimo para construir features/states cuando el proyecto entre formalmente en esa fase.

Las preguntas de regimen que estas features permiten formular son valiosas:

- abre muy extendida contra la sesion anterior?
- esta cerca o lejos del rango previo?
- la volatilidad reciente esta comprimida o expandida?
- el gap es excepcional respecto a su historia reciente?
- la sesion actual rompe el contexto de los ultimos dias?

Pero esas preguntas pertenecen a la fase de `features -> events/states -> strategy/backtest -> ML/RL`.

El trabajo actual del proyecto sigue estando principalmente en:

- data;
- normalization;
- reference/universe;
- contratos;
- datasets defendibles.

Por eso no debe invertirse esta fase en expandir `intraday_regime_features` como si ya fuera el set final de atributos.

## 5. Que aporta ahora y que no aporta

### Aporta ahora

- prueba real de consumo de `1m_split_normalized`;
- evidencia de que raw puede fabricar falsos gaps/shocks alrededor de splits;
- separacion documentada entre features cross-session y features intrasesion;
- base metodologica para no contaminar ML/backtest con discontinuidades mecanicas;
- criterio futuro para revisar cualquier feature que cruce sesiones.

### No aporta todavia

- edge validado;
- labels;
- ejecucion;
- slippage;
- decision policy;
- backtest core;
- feature layer full-universe `<1B>`;
- ni input ML productivo.

La regla practica es:

- conservarlo como evidencia y contrato de direccion;
- no dejar que bloquee el backtest base;
- no promoverlo a consumo global hasta que exista una corrida `<1B>` con leakage y coverage cerrados.

## 6. Relacion con el camino base de backtesting

El camino base de backtesting debe seguir priorizando:

- `daily_return_labels`;
- universo/reference;
- `1m raw` usable para `<1B>`;
- `daily_adjusted` como verdad economica lenta;
- `halts`;
- `quotes`/`trades` cuando el simulador necesite realismo de ejecucion.

`intraday_regime_features` entra despues como:

- contexto;
- estado;
- filtro;
- o input ML.

No debe entrar antes como dependencia obligatoria si el backtest inicial no usa memoria cross-session intradia.

Si el backtest o ML si usa memoria cross-session intradia, entonces la regla ya queda fijada:

- no calcular esas features sobre `1m raw`;
- usar `1m_split_normalized` o documentar explicitamente por que no aplica.

## 7. Lo que falta para backtest/ML `<1B>`

Para que esta capa pueda ser usada como input serio de backtest/ML, falta cerrar:

### A. Universo

Debe definirse el universo objetivo:

- `<1B>` segun la politica institucional vigente;
- con membership temporal;
- survivorship control;
- y reglas de elegibilidad compatibles con `reference`.

### B. Cobertura 1m necesaria

Debe verificarse:

- que cada ticker-dia esperado tiene `1m raw` suficiente;
- que la capa `1m_split_normalized` esta disponible o puede calcularse para los casos que cruzan splits;
- y que la falta de cobertura queda clasificada como `missing`, `partial`, `not_expected` o `review`.

### C. Feature scope

La primera promocion `<1B>` no debe abrir todas las familias posibles.

Debe limitarse a:

- features cross-session ya contratadas;
- features intrasesion locales ya contratadas;
- metadatos de provenance;
- flags de cobertura/lookback.

Quedan fuera:

- quotes/trades microestructura fina;
- news/catalyst features;
- halts-aware event state;
- modelos de ejecucion;
- labels o decisions.

### D. Leakage policy

Cada feature debe declarar:

- timestamp de disponibilidad;
- lookback usado;
- si requiere datos de cierre de sesion;
- si es usable premarket, intraday o post-session;
- y si puede entrar en backtest en decision time sin mirar futuro.

Regla minima:

- una feature `ticker-day` calculada con informacion completa de la sesion no puede usarse para decidir dentro de esa misma sesion salvo que se versionen features online/parciales.

### E. Materializacion

La promocion debe materializarse de forma reproducible.

Ruta propuesta:

- `E:\TSIS\data\intraday_regime_features_lt1b`

No debe sobreescribir:

- `E:\TSIS\data\intraday_regime_features`

que queda como piloto historico.

### F. Auditoria agregada

La corrida `<1B>` debe dejar:

- summary por ticker/year;
- expected/present/healthy/usable;
- nulos por feature;
- coverage por lookback;
- conteo de split-event windows;
- conteo de rows donde cross-session usa `1m_split_normalized`;
- conteo de rows con `source_raw_root` y `source_split_normalized_root`;
- manifest de errores;
- manifest de casos para inspeccion visual.

## 8. Fases recomendadas

### Fase 1 - Dry run sin escribir full output

Objetivo:

- estimar universo esperado;
- contar inputs disponibles;
- detectar huecos de cobertura;
- medir coste computacional.

Salida:

- audit report;
- no parquets productivos.

### Fase 2 - Materializacion incremental controlada

Objetivo:

- escribir una particion acotada por year o batch de tickers;
- preservar idempotencia;
- no sobreescribir parquets existentes salvo modo explicito.

Salida:

- parquets nuevos en ruta `_lt1b`;
- summary incremental.

### Fase 3 - Auditoria semantica masiva

Objetivo:

- comprobar schema;
- comprobar provenance;
- comprobar nulos esperados;
- comprobar leakage;
- comprobar casos de split;
- producir sample packs.

Salida:

- readout agregado;
- notebook de inspeccion;
- status por ticker/year.

### Fase 4 - Promocion de consumo

Solo despues de Fase 3, la capa puede proponerse como:

- `ml_primary_candidate`
- `backtest_context_candidate`

No como:

- `execution_truth`
- `policy_final`
- `live_signal`

## 9. Condicion para usar en backtest

Un backtest puede consumir esta capa solo si declara:

- universe version;
- feature root;
- feature contract;
- decision timestamp;
- leakage mode;
- coverage policy;
- fallback para missing features;
- y si las features son pre-session, intraday parcial o post-session.

## 10. Relacion con `daily_return_labels`

`daily_return_labels` puede evaluar resultados diarios o targets.

`intraday_regime_features` debe actuar como:

- contexto;
- estado;
- filtro;
- o input ML.

No deben mezclarse:

- labels como features;
- features calculadas con informacion posterior al decision time;
- ni adjusted daily truth con execution price truth.

## 11. Veredicto

El siguiente paso natural no es declarar `intraday_regime_features` lista ni expandirla como feature productiva por intuicion.

El siguiente paso natural es preparar una promocion `<1B>` disciplinada:

- con universo definido;
- leakage cerrado;
- materializacion separada;
- auditoria agregada;
- y solo despues consumo por backtest/ML.

Mientras tanto, su estado institucional correcto es:

- consumidor piloto validado;
- evidencia de normalizacion downstream;
- regla futura para features cross-session;
- no bloqueante para el backtest base.
