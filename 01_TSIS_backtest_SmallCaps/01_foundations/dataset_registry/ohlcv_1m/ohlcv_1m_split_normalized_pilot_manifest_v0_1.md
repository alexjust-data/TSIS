# Ohlcv 1m Split-Normalized Pilot Manifest `v0_1`

## 1. Estado

Este manifest queda abierto como contenedor contractual del primer lote semantico de `1m_split_normalized`.

Todavia no fija tickers concretos.

## 2. Composicion minima obligatoria

El lote final debe incluir:

- al menos `2` casos con `reverse split`
- al menos `2` casos con `forward split`
- al menos `2` controles sin evento

## 3. Regla de elegibilidad

Un caso solo entra si:

- existe en `D:\ohlcv_1m`
- el split cae dentro del rango real de `1m`
- y puede expresarse en unidad `ticker-month`

## 4. Artefactos pendientes

La version siguiente de este manifest debera incluir:

- `ticker`
- `month`
- `year`
- `event_type`
- `event_date`
- `role`
  - `reverse_split`
  - `forward_split`
  - `control`
- `rationale`

## 5. Veredicto

Este manifest no se rellena por intuicion ni por nombre bonito de ticker.

Se rellena solo despues de verificar cobertura real en `1m`.
