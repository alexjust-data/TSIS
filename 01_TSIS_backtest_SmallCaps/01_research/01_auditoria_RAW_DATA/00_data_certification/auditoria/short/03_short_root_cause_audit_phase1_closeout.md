# Short Phase 1 Closeout

## Alcance

Fase 1 estructural del bloque `short`, ya con baseline oficial `FINRA` reconstruido en paralelo a `Polygon`.

## Decisiones fijadas

### Baseline

- `FINRA` queda fijado como baseline oficial.
- `Polygon` se conserva como provider secundario y de comparación.

### Universo

- Se mantiene el universo operativo `<1B>`.

## Hallazgos estructurales principales

### 1. short_volume: FINRA supera claramente a Polygon

`Polygon`
- `date_min = 2024-02-06`
- `date_max = 2026-04-02`
- `3381` tickers con filas
- `1443` tickers con `0` filas
- media `296.5` filas por ticker file

`FINRA`
- `date_min = 2018-08-01`
- `date_max = 2026-04-29`
- `4623` tickers con filas
- `0` tickers con `0` filas en la capa normalizada
- media `1014.3` filas por ticker file

Lectura:
- el histórico actual de `Polygon short_volume` queda claramente truncado frente a `FINRA`
- la mejora de `FINRA` no es marginal; es estructural

### 2. short_interest: Polygon y FINRA quedan más cerca, pero FINRA sigue mandando

`Polygon`
- `date_min = 2017-12-29`
- `date_max = 2026-03-13`
- `4693` tickers con filas
- `131` tickers con `0` filas

`FINRA`
- `date_min = 2017-12-29`
- `date_max = 2026-04-15`
- `4687` tickers con filas
- `0` tickers con `0` filas en la capa normalizada

Lectura:
- aquí la ventaja de `FINRA` es menos masiva que en `short_volume`
- aun así, `FINRA` sigue siendo la capa oficial y más limpia

### 3. Residuo `only Polygon`

#### short_volume
- `201` tickers `only Polygon`

#### short_interest
- `137` tickers `only Polygon`

Clasificación de identidad sobre `only Polygon`:
- `review_provider_coverage_gap = 272`
- `review_transient_or_remap_candidate = 41`
- `review_crossing_life_window = 25`

Lectura:
- el residuo no se concentra en ausencia total de `reference`
- se concentra más en:
  - coverage gap del provider
  - símbolos transitorios / share-class / remap
  - series que cruzan la ventana de vida del ticker

## Integridad interna

### short_interest

No aparecen:
- `negative_short_interest_rows`
- `negative_days_to_cover_rows`

Pero sí hay un matiz importante:
- `zero_adv_rows` altos en ambos providers
- errores grandes puntuales en `days_to_cover` cuando `avg_daily_volume = 0` o casi `0`

Lectura:
- la capa es usable
- pero `days_to_cover` no debe asumirse exacto sin tratar el problema de `ADV` cero / casi cero

### short_volume

No aparecen:
- `negative_total_rows`
- `negative_short_rows`

Y la identidad aritmética base:
- `short_volume = exempt_volume + non_exempt_volume`

sale esencialmente limpia en ambos providers.

Pero aparece un hallazgo duro:

`venue_err_mean`
- `FINRA ~= 41.18`
- `Polygon ~= 6950.68`

`venue_err_p95`
- `FINRA ~= 48.53`
- `Polygon ~= 28308.02`

Lectura:
- el breakdown por venue de `Polygon short_volume` queda mucho peor alineado con el total que el baseline `FINRA`
- este es un hallazgo estructural serio a favor de `FINRA`

## Conclusión de fase 1

La fase estructural deja esta decisión:

- `FINRA short_volume` pasa a baseline claramente superior
- `FINRA short_interest` pasa a baseline oficial preferido
- `Polygon` no se descarta, pero deja de ser fuente primaria de certificación

El siguiente paso correcto es la fase causal:
- `short_volume` contra `quotes`, `trades`, `halts`
- `short_interest` contra ventanas multi-día y eventos
