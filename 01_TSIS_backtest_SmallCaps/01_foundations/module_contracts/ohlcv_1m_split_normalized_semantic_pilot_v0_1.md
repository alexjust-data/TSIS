# Ohlcv 1m Split-Normalized Semantic Pilot `v0_1`

## 1. Rol

Este documento define el piloto semantico inicial de `1m_split_normalized`.

No es todavia la corrida completa.

Es la prueba controlada que debe demostrar que la capa corrige discontinuidades mecanicas de split entre sesiones sin inventar cambios donde no debe.

## 2. Pregunta central

La pregunta del piloto es esta:

- cuando un ticker cruza un split o reverse split dentro del rango real disponible de `1m`, la capa `1m_split_normalized` deja de mostrar un shock mecanico falso y vuelve comparable la escala entre sesiones

## 3. Que debe incluir el piloto

El piloto debe mezclar:

- casos con `forward split`
- casos con `reverse split`
- casos control sin eventos

Y, muy importante:

- el evento debe caer dentro del rango real disponible de `1m`

No basta con que el ticker aparezca en la tabla maestra de splits.

## 4. Unidad recomendada

La unidad minima del piloto no es solo ticker.

Debe seleccionarse por:

- `ticker`
- `month`

porque la capa objetivo se materializara por `ticker-month`.

## 5. Criterios de seleccion

Cada candidato debe cumplir:

- existe en `D:\ohlcv_1m`
- existe corporate action de split o reverse split en fuentes maestras
- la fecha del evento cae dentro del rango real cubierto por `1m`

Los controles deben cumplir:

- existe en `D:\ohlcv_1m`
- no tiene split activo en la ventana elegida

## 6. Verificaciones semanticas obligatorias

Cada caso piloto debe demostrar:

- que el precio raw si muestra discontinuidad mecanica entre sesiones
- que `1m_split_normalized` la neutraliza
- que las barras fuera de la zona afectada permanecen coherentes
- que los controles sin evento quedan neutros

## 7. Que responde

Responde:

- si el algoritmo de split-normalization intradia hace lo correcto en casos reales
- si protege a ML y backtest intradia contra shocks falsos por split

## 8. Que no responde

No responde:

- si hace falta un `1m_adjusted` economico completo por dividendos
- ni si toda la capa debe ya materializarse full-universe

## 9. Salida esperada del piloto

El piloto debe dejar:

- un manifest versionado de casos `ticker-month`
- una nota de resultados ticker por ticker
- y, si es posible, paneles comparativos raw vs split-normalized para algunos casos

Estado actual:

- el primer lote real ya queda fijado en:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
  - `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`

## 10. Veredicto

El piloto semantico es la puerta obligatoria antes de abrir:

- un consumidor intradia real dependiente de continuidad entre sesiones
- o cualquier expansion amplia de `1m_split_normalized`
