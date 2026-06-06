# Daily Return Labels - Operational Landing `v0_1`

## 1. Decision

La primera promocion operativa de labels diarios de retorno debe vivir en:

- `E:\TSIS\data\daily_return_labels`

## 2. Fuente obligatoria

La fuente obligatoria de este consumidor es:

- `E:\TSIS\data\ohlcv_daily_adjusted`

No debe construirse desde:

- `daily_raw`

## 3. Layout recomendado

La capa debe espejar el layout de `daily_adjusted`.

Ejemplo:

- `E:\TSIS\data\daily_return_labels\ticker=A\year=2005\day_aggs_A_2005_labels.parquet`

## 4. Labels iniciales

- `ret_1d`
- `ret_3d`
- `ret_5d`

## 5. Script operativo inicial

- `scripts/materialize_daily_return_labels.py`

## 6. Estado actual

La ruta operativa ya fue poblada a nivel de piloto con el mismo lote semantico validado de `daily_adjusted`.

Resumen del piloto materializado:

- `A`: `22` files / `5327` rows
- `AAME`: `22` / `4949`
- `ABEO`: `12` / `2693`
- `ABIO`: `16` / `3925`
- `ABTX`: `8` / `1758`
- `BBW`: `22` / `5327`
- `CASS`: `22` / `5241`
- `CVLY`: `20` / `4420`
- `SELF`: `11` / `2548`
- `SGC`: `22` / `5199`

Manifest de resumen:

- `E:\TSIS\data\daily_return_labels\_labels_materialization_summary.csv`

## 7. Veredicto

Este es el primer consumidor real recomendado de `daily_adjusted` porque usa de forma limpia:

- `c_adjusted`

como base de retornos economicos diarios comparables.
