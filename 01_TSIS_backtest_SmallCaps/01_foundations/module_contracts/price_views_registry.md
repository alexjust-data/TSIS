# Price Views Registry - Modulo 01

## 1. Rol del documento

Este documento registra las vistas canonicamente reconocidas de precio en el modulo.

Su funcion es dejar explicito:

- que vista existe;
- que representa;
- para que consumidores es valida;
- y que usos son incorrectos o peligrosos.

## 2. Vistas registradas

### `quotes_raw`

Representa:

- libro observado `bid/ask` intradia

Fuente tipica:

- `C:\TSIS_Data\data\quotes`
- `D:\quotes`

Consumidores validos:

- ejecucion
- slippage
- microestructura
- control de calidad del libro
- dossiers forenses

Consumidores no validos por defecto:

- retorno economico multi-dia
- benchmarking portfolio

### `trades_raw`

Representa:

- prints observados intradia

Fuente tipica:

- `C:\TSIS_Data\data\trades_ticks_prod_2005_2026`
- `D:\trades_ticks_prod_2005_2026`

Consumidores validos:

- ejecucion
- validacion cruzada con quotes
- analisis microestructural

### `daily_raw`

Representa:

- barra diaria del vendor en su escala primaria operativa

Fuente tipica:

- `D:\ohlcv_daily`

Consumidores validos:

- auditoria vendor
- control OHLCV
- reconciliacion raw
- evidencia institucional `daily`

### `split_normalized`

Representa:

- vista reexpresada a una base coherente de split

Estado:

- reconocida institucionalmente
- primera implementacion reusable global ya creada en:
  - `src/data/price_views.py`
- sigue pendiente su integracion completa en todos los pipelines del modulo

Consumidores validos:

- reconciliacion `quotes` vs `daily`
- continuidad temporal
- contraste entre datasets con distinta politica de split handling

### `adjusted`

Representa:

- vista economica comparable tras corporate actions relevantes

Estado:

- reconocida institucionalmente
- primera implementacion reusable global ya creada en:
  - `src/data/price_views.py`
- el alcance actual cubre:
  - cadena `split_normalized -> future dividend factor`
- sigue pendiente, para futuras iteraciones, ampliar la metodologia si el modulo incorpora:
  - stock dividends
  - spin-offs
  - otros eventos corporativos mas complejos

Consumidores validos:

- retornos
- factor research
- labels ML
- valoracion portfolio
- benchmarking

### `adjusted_proxy`

Representa:

- aproximacion diagnostica para contraste con plataformas externas

Estado:

- permitida para dossiers e inspeccion
- no sustituye `adjusted`
- primera implementacion reusable global ya creada en:
  - `src/data/price_views.py`

Consumidores validos:

- reconciliacion externa
- explicacion forense
- comparacion `raw` vs `adjusted`

Consumidores no validos:

- backtest core final
- target canonico de ML

## 3. Relacion entre vistas

La cadena conceptual correcta es:

`quotes_raw / trades_raw -> daily_raw -> split_normalized -> adjusted`

Donde `adjusted_proxy` es una rama auxiliar de diagnostico, no la vista economica definitiva.

## 4. Regla de consumo

Todo pipeline debe declarar, como minimo:

- `signal_price_view`
- `execution_price_view`
- `valuation_price_view`
- `benchmark_price_view`

o, en ML:

- `feature_price_view`
- `target_price_view`

## 5. Relacion con otros documentos

- `price_semantics_and_adjustment_policy.md`
- `corporate_actions_adjustment_methodology.md`
- contratos de dataset `daily`, `quotes`, `trades`, `1m`
