# Daily Adjusted Dataset Contract - Modulo 01

## 1. Rol

Este documento define la primera promocion contractual de `daily_adjusted` como capa economica diaria del modulo.

Su objetivo es fijar una vista canonica para:

- `backtest_core`
- `backtest_extended`
- benchmarking interno
- labels diarios de ML
- research diario de senal

## 2. Semantica primaria

`daily_adjusted` no representa:

- el precio observado bruto;
- ni el libro ejecutable;
- ni el tape intradiario.

Representa:

- una serie diaria con continuidad economica suficiente para retornos comparables a traves del tiempo.

## 3. Fuente logica

La construccion parte de:

- `ohlcv_daily`
- `splits`
- `dividends`

y usa la implementacion reusable de:

- `src/data/price_views.py`

## 4. Transformacion canonica

Secuencia canonica:

1. partir de `daily_raw`
2. aplicar `split_normalized`
3. calcular factores futuros de dividendos sobre esa base ya normalizada
4. materializar:
   - `o_adjusted`
   - `h_adjusted`
   - `l_adjusted`
   - `c_adjusted`

## 5. Campos minimos esperados

Campos base preservados:

- `ticker`
- `date`
- `year`
- `o`
- `h`
- `l`
- `c`
- `v`
- `vw`
- `n`
- `t`

Campos derivados minimos:

- `future_split_factor`
- `future_dividend_factor`
- `future_adjustment_factor`
- `o_split_normalized`
- `h_split_normalized`
- `l_split_normalized`
- `c_split_normalized`
- `o_adjusted`
- `h_adjusted`
- `l_adjusted`
- `c_adjusted`

Campos de provenance minima:

- `materialized_price_view`
- `source_daily_file`
- `source_splits_file`
- `source_dividends_file`

## 6. Consumidores permitidos

Permitidos por defecto:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`
- `forensic_only`

## 7. Consumidores no habilitados automaticamente

No habilita por si solo:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 8. Para que sirve

Sirve para:

- retornos economicos multi-dia
- equity curves
- drawdown
- benchmarking comparable
- labels diarios disciplinados

## 9. Para que no sirve

No sirve como vista primaria para:

- ejecucion
- microestructura
- slippage
- lectura del libro
- interpretacion del tape observado

## 10. Relacion con otras vistas

- `daily_raw`: conserva el precio observado
- `split_normalized`: corrige escala mecanica
- `daily_adjusted`: corrige continuidad economica
- `adjusted_proxy`: sigue siendo vista diagnostica, no sustituto canonico de `daily_adjusted`

## 11. Estado

Este contrato define la primera promocion institucional de la capa.

No implica todavia que toda la infraestructura downstream del modulo la consuma ya de forma productiva.

Implica:

- que la semantica ya esta cerrada;
- que existe una primera ruta materializadora;
- y que esta es la capa correcta para empezar a aterrizar research diario, benchmark y labels.
