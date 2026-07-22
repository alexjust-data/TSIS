# Plan Incremental De Materializacion De `daily_adjusted` `v0_1`

## 1. Objetivo

Este documento fija como debe promocionarse `daily_adjusted` sin lanzar primero una rematerializacion full-universe ciega.

La idea correcta es:

- empezar pequeno
- validar semantica
- validar consumidor real
- y solo despues escalar

## 2. Principio rector

La primera materializacion de `daily_adjusted` no debe medirse por volumen escrito.

Debe medirse por:

- correccion semantica
- trazabilidad
- utilidad real para un consumidor concreto
- y ausencia de ambiguedad en la lectura economica

## 3. Ruta operativa objetivo

La ruta canonica sigue siendo:

- `E:\TSIS\data\ohlcv_daily_adjusted`

La salida debe espejar el layout de `D:\ohlcv_daily`.

## 4. Estrategia incremental

La promocion debe hacerse en cuatro fases.

### Fase 1 - smoke test tecnico

Objetivo:

- probar que el materializador escribe bien
- comprobar columnas
- comprobar provenance
- y detectar fallos de layout o imports

Estado:

- ya ejecutado sobre `ticker=A`

Resultado esperado:

- escritura correcta
- columnas ajustadas presentes
- summary manifest minimo

### Fase 2 - piloto semantico con tickers de corporate actions reales

Objetivo:

- probar casos con:
  - forward splits
  - reverse splits
  - dividendos reales
  - combinaciones de historia sin eventos

Conjunto recomendado:

- `SGC`
- `AAIC`
- `ABEO`
- `SELF`
- `BBW`
- y un pequeno grupo control sin eventos materiales

El lote piloto inicial ya fijado vive en:

- [daily_adjusted_pilot_manifest_v0_1.md](./daily_adjusted_pilot_manifest_v0_1.md)

Y su refinamiento recomendado actual vive en:

- `01_foundations/dataset_registry/daily/daily_adjusted_pilot_manifest_v0_2.csv`

Pregunta que responde:

- la capa ajustada se comporta bien cuando de verdad hay corporate actions relevantes

Resultado esperado:

- `future_split_factor` distinto de `1.0` donde corresponda
- `future_dividend_factor` distinto de `1.0` donde corresponda
- continuidad economica defendible
- y ausencia de artefactos triviales de escritura

### Fase 3 - primer consumidor real

Objetivo:

- conectar un consumidor real pequeño pero institucionalmente importante

Primer consumidor recomendado:

- generador de labels diarios de retorno

Segunda opcion inmediata:

- benchmark / retorno base para `backtest_core`

Pregunta que responde:

- la capa ajustada ya no es solo un parquet correcto, sino una vista realmente util y consumida

Resultado esperado:

- labels construidos sobre `c_adjusted`
- trazabilidad de que el consumidor ya no trabaja sobre `daily_raw`

### Fase 4 - expansion controlada

Objetivo:

- ampliar el universo una vez validada la capa

Estrategia:

- incremental por `ticker-year`
- con manifests acumulativos
- y con politicas claras de overwrite / retry

Solo despues, si el piloto ya esta estable, evaluar:

- promocion full-universe

## 5. Unidad de trabajo recomendada

La unidad minima operativa debe ser:

- `ticker-year file`

No:

- ticker entero
- universo entero
- ni fechas aisladas desestructuradas

Esto simplifica:

- retries
- manifests
- recomputes
- control de coste

## 6. Artefactos obligatorios por corrida

Cada corrida incremental debe dejar:

- parquets materializados
- `_materialization_summary.csv`
- identificacion del lote
- fecha UTC de ejecucion
- ruta de fuentes usadas

Idealmente tambien:

- manifest parquet o csv de archivos escritos
- recuento de filas
- recuento de tickers
- recuento de archivos con splits
- recuento de archivos con dividendos

## 7. Validaciones minimas obligatorias

### Validacion estructural

- el parquet se puede leer
- las columnas esperadas existen
- `materialized_price_view = daily_adjusted_v0_1`

### Validacion semantica

- `future_split_factor > 0`
- `future_dividend_factor > 0`
- `future_adjustment_factor > 0`
- `o/h/l/c_adjusted` parseables

### Validacion de corporate actions

En tickers con eventos reales:

- no todo debe quedar en `1.0`
- debe verse efecto donde realmente existe split o dividendo

### Validacion de no-cambio espurio

En tickers sin eventos relevantes:

- `*_adjusted` debe coincidir con `*_raw` o diferir solo por tolerancias numericas triviales

## 8. Criterio de paso entre fases

### De Fase 1 a Fase 2

- smoke test tecnico correcto

### De Fase 2 a Fase 3

- piloto semantico correcto en varios tickers con eventos reales

Resultado actual:

- ya validado en:
  - [daily_adjusted_pilot_results_v0_2.md](./daily_adjusted_pilot_results_v0_2.md)

### De Fase 3 a Fase 4

- primer consumidor real ya conectado
- output estable
- manifests suficientes

### A full-universe

- cuando la capa ya haya demostrado:
  - valor real
  - estabilidad
  - y ausencia de ambiguedad institucional

## 9. Que no debe hacerse

- no escribir full-universe solo porque el script funciona
- no mezclar la capa ajustada dentro de `ohlcv_daily` raw
- no declarar la vista como productiva sin consumidor real
- no abrir `backtest_core` entero sobre ella sin pasar antes por labels o benchmark piloto

## 10. Veredicto final

La materializacion correcta de `daily_adjusted` debe seguir este orden:

1. smoke test tecnico
2. piloto semantico con corporate actions reales
3. primer consumidor real
4. expansion incremental
5. solo despues, full-universe si sigue teniendo sentido

La regla central es:

- primero demostrar valor y correccion
- despues escalar volumen
