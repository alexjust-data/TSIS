# Intraday Regime Features - Operational Landing `v0_1`

## 1. Decision

La primera promocion operativa de `intraday_regime_features` debe vivir en:

- `E:\TSIS\data\intraday_regime_features`

## 2. Fuentes obligatorias

Fuentes obligatorias:

- `D:\ohlcv_1m`
- `E:\TSIS\data\ohlcv_1m_split_normalized`

Fuentes opcionales de fase posterior:

- `E:\TSIS\data\ohlcv_daily_adjusted`
- halts
- eventos
- `quotes_raw`
- `trades_raw`

## 3. Layout recomendado

La capa debe materializarse de forma que preserve trazabilidad por unidad temporal usada por el consumidor.

Version minima recomendada:

- grano `ticker-day`

Ejemplo:

- `E:\TSIS\data\intraday_regime_features\ticker=BNGO\year=2025\day_features_BNGO_2025.parquet`

Version posterior posible:

- grano `ticker-minute`

si el consumidor online o quasi-online lo necesita de verdad.

## 4. Regla operacional central

No debe haber una sola columna de precio base para todo.

El pipeline debe materializar explicitamente:

- features que usan `1m_split_normalized`
- y features que usan `1m raw`

o, como minimo, debe dejar metadatos claros de que familia usa cada vista.

## 5. Script operativo actual

Script actual:

- `scripts/materialize_intraday_regime_features.py`

Su responsabilidad actual es:

- leer ambas capas;
- construir una primera familia minima de features;
- dejar provenance;
- y materializar explicitamente la separacion entre:
  - features cross-session sobre `1m_split_normalized`
  - y features intrasesion sobre `1m raw`

La primera salida real queda en:

- `E:\TSIS\data\intraday_regime_features`

## 6. Veredicto

Esta capa es el siguiente consumidor intradia natural porque convierte la validacion semantica de `1m_split_normalized` en una utilidad directa para ML y backtest de regimen, sin abrir todavia el problema mucho mas duro de la ejecucion fina.
