# Daily Return Labels Consumption Policy `v0_1`

## 1. Decision

`daily_return_labels_v0_1` queda aprobada como:

- consumidor piloto de `daily_adjusted`;
- target layer diario inicial;
- evidencia de que los retornos objetivo deben calcularse sobre `c_adjusted`;
- base metodologica para evaluacion futura diaria.

No queda aprobada todavia como:

- target layer full-universe `<1B>`;
- feature layer;
- input de modelo;
- senal live;
- simulador de ejecucion;
- ni prueba de edge.

## 2. Lectura de fase

Ahora mismo esta capa responde una pregunta de arquitectura:

- podemos construir labels diarios economicos sin contaminar los targets con splits/dividendos?

La respuesta piloto es:

- si, para 10 tickers seleccionados, usando `daily_adjusted` y `c_adjusted`.

No responde todavia:

- si esos labels cubren todo `<1B>`;
- si un modelo entrenado con ellos tiene edge;
- si el backtest core ya debe depender de esta ruta;
- si los labels estan listos para una corrida global de ML.

## 3. Usos permitidos actuales

Usos permitidos:

- validacion downstream de `daily_adjusted`;
- research piloto de targets diarios;
- pruebas de schema y provenance;
- comprobacion de que labels no usan `c raw`;
- diseno de promocion `<1B>` futura;
- evaluacion manual o notebooks piloto en los 10 tickers cubiertos.

## 4. Usos prohibidos hasta nueva promocion

No se debe usar como:

- input feature;
- variable explicativa;
- filtro de entrada;
- senal de trading;
- feature de RL;
- backtest full-universe;
- target global `<1B>` sin auditoria de coverage;
- ni evidencia de performance.

Regla estricta:

- `ret_1d`, `ret_3d`, `ret_5d` son `y`, no `X`.

## 5. Regla de fuente

Fuente obligatoria:

- `daily_adjusted_v0_1`

Columna obligatoria:

- `c_adjusted`

Fuente prohibida para labels economicos:

- `daily_raw`
- `c`

Si algun label futuro se calcula sobre raw, debe tener otro nombre, otro contrato y otra justificacion.

## 6. Regla de disponibilidad temporal

Los labels son forward-looking.

Por tanto:

- `ret_1d` solo se conoce despues de observar `t+1`;
- `ret_3d` solo se conoce despues de observar `t+3`;
- `ret_5d` solo se conoce despues de observar `t+5`.

Ningun pipeline puede consumirlos antes de ese timestamp como si fueran informacion disponible.

## 7. Diferencia con `intraday_regime_features`

`intraday_regime_features` puede convertirse en atributos/states.

`daily_return_labels` no.

La relacion correcta es:

- features/states viven en `X`;
- labels viven en `y`;
- backtest/evaluacion compara decisiones contra outcomes;
- labels nunca deben filtrarse hacia el lado de features.

## 8. Condiciones para promocion futura

Para pasar de piloto a target layer usable en research/backtest/ML `<1B>`, debe existir:

- universo objetivo temporal `<1B>`;
- materializacion reproducible sobre ese universo;
- coverage expected/present/healthy/usable;
- auditoria contra `daily_adjusted` full-universe;
- conteo de nulos por horizonte;
- validacion de no uso de `c raw`;
- validacion de monotonicidad temporal;
- policy de train/test temporal;
- manifest de errores;
- changelog de promocion.

## 9. Veredicto

La capa es importante porque convierte `daily_adjusted` en targets economicos diarios.

Pero su estado actual debe leerse como:

- `pilot_target_layer`

no como:

- `full_universe_target_layer`.
