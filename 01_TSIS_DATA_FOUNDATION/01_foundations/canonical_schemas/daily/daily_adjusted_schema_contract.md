# Daily Adjusted Schema Contract - Modulo 01

## 1. Rol

Este documento fija el schema logico minimo esperado para la primera materializacion de `daily_adjusted`.

## 2. Unidad logica

La unidad logica sigue siendo:

- `ticker-day bar`

La capa ajustada no cambia la unidad del dataset.
Cambia la semantica economica de parte de sus columnas de precio.

## 3. Claves logicas

Claves minimas:

- `ticker`
- `date`

## 4. Campos base preservados

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

## 5. Campos derivados obligatorios

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

## 6. Campos de provenance obligatorios

- `materialized_price_view`
- `source_daily_file`
- `source_splits_file`
- `source_dividends_file`

## 7. Reglas semanticas

- `future_split_factor > 0`
- `future_dividend_factor > 0`
- `future_adjustment_factor > 0`
- `*_split_normalized` viven en base de escala mecanicamente consistente
- `*_adjusted` viven en base de continuidad economica diaria

## 8. Regla de interpretacion

Las columnas:

- `o_adjusted`
- `h_adjusted`
- `l_adjusted`
- `c_adjusted`

son las columnas canonicas de consumo para retorno economico diario dentro de esta capa.

Las columnas:

- `o`
- `h`
- `l`
- `c`

deben seguir leyendose como:

- precio observado bruto diario

y no deben confundirse con la vista ajustada.
