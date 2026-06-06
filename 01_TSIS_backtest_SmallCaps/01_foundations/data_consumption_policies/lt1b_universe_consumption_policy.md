# Lt1b Universe Consumption Policy `v0_1`

## 1. Decision

`lt1b_universe_v0_1` queda aprobado como el corte operativo transversal vigente para afirmaciones `<1B>` dentro de `01_TSIS_backtest_SmallCaps`.

No es:

- `E:\TSIS\data\reference`;
- un dataset raw;
- un label;
- una feature;
- ni una tabla diaria fully point-in-time de membership por market cap.

Es:

- una capa derivada de universo/elegibilidad;
- basada en el run `20260320_market_cap_last_observed_cutoff`;
- con `4824` tickers;
- y ventana PTI por ticker.

## 2. Regla obligatoria de filtrado

Toda afirmacion de cobertura `<1B>` debe filtrar por:

1. `ticker` presente en `lt1b_universe_v0_1`;
2. interseccion temporal con la ventana:
   - `first_seen_date`
   - `last_observed_date`

No basta con filtrar solo por ticker.

Ejemplo correcto:

- incluir un parquet mensual `1m` si el ticker esta en `<1B>` y el mes del parquet intersecta la ventana PTI del ticker.

Ejemplo incorrecto:

- incluir todos los archivos historicos de un ticker solo porque el ticker aparece en el corte `<1B>`.

## 3. Usos permitidos

Usos permitidos:

- auditorias de cobertura `<1B>`;
- cierres de calidad restringidos a `<1B>`;
- filtros transversales para `daily`, `1m`, `quotes`, `trades`, `short`, `additional`, labels y features;
- calculo de expected/present/healthy/usable bajo alcance `<1B>`;
- construccion de manifests de descarga o auditoria.

## 4. Usos prohibidos o peligrosos

No se debe usar como:

- prueba de calidad de un dataset;
- garantia de presencia de datos;
- membership diaria fully point-in-time por market cap;
- sustituto de `reference` raw;
- sustituto de `population_target_pti`;
- filtro all-cap;
- filtro `<2B>`.

`unclassified_no_market_cap` no debe mezclarse con `<1B>`.

## 5. Relacion con `reference`

`reference` aporta informacion estructural:

- identidad;
- estado;
- exchange;
- corporate actions;
- metadata;
- fundamentos.

`lt1b_universe` es una decision derivada de universo.

Por eso vive en:

- `dataset_registry/universes`
- `canonical_schemas/universes`

y no en:

- `dataset_registry/reference`
- `canonical_schemas/reference`

## 6. Relacion con expected/present/healthy/usable

El universo `<1B>` ayuda a definir:

- `expected`

pero no decide por si solo:

- `present`;
- `healthy`;
- `usable`.

Regla:

- `expected` depende de ticker + ventana PTI + semantica del dataset;
- `present` depende de archivos/rows reales;
- `healthy` depende de validadores de calidad;
- `usable` depende de policy del consumidor.

## 7. Limitacion de version

Esta version es un corte operativo por:

- last observed;
- anchor date;
- market cap clasificable;
- status reconstruido.

No es un panel diario de:

- `ticker x date x is_small_cap_t`.

Si el proyecto necesita membership diaria estricta por market cap, debe crear y promocionar otro dataset:

- `population_target_pti`

con contrato propio.

## 8. Veredicto

Toda documentacion futura que diga `<1B>` debe poder apuntar a:

- este universo;
- su ruta fisica;
- sus `4824` tickers;
- y su regla de ventana PTI.
