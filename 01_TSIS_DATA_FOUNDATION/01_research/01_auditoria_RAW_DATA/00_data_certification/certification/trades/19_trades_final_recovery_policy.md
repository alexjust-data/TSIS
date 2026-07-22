# Trades | Final Recovery Policy

Esta nota fija la política operativa final de recuperación para `trades`, sin reabrir la auditoría base.

## Estados finales

Para certificación de `trades`, la salida final debe distinguir:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

## Regla por bucket

### `good`

Entra aquí:

- `good`

Salvedad:

- existe, pero es muy pequeño
- no debe sobrerrepresentarse en el cierre global

### `bad`

Entra aquí:

- `bad_data`

Salvedad:

- existe fuga residual pequeña de escala extrema
- no cambia la lectura general del bucket

### `recoverable_with_flag`

Entran aquí de forma provisional:

- `review_no_1m_reference`
- subconjunto rehabilitable de `review`
- subconjunto rehabilitable de `review_microstructure`
- subconjunto rehabilitable de `review_1m_reference_alignment`

Y entra aquí de forma potencial, pero no todavía operativa:

- `reference_scale_mismatch`
  - solo cuando exista prueba de reconciliación de escala estable

### `review_not_rehabilitated`

Entra aquí:

- residuo de `review` que no cumpla la regla de rehabilitación
- parte no rehabilitada de `review_microstructure`
- parte no rehabilitada de `review_1m_reference_alignment`
- `reference_scale_mismatch` mientras no exista corrección validada

## Regla estricta para `review`

Subconjunto `review` rehabilitable si cumple todo:

- `daily_vw_to_trade_vw` cerca de `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`
- `outside_daily_regular_pct <= 1`
- `outside_1m_regular_pct <= 15`

Resultado historico sobre `57e/full_clean` materializado:

- `review` total: `2,825,748`
- `review` rehabilitable estricto: `2,427,056`
- peso: `85.89%`
- residuo no rehabilitado: `398,692`

## Regla extendida para `review`

Versión más amplia:

- `daily_vw_to_trade_vw` cerca de `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `outside_daily_regular_pct <= 2`
- `outside_1m_regular_pct <= 20`

Resultado:

- `review` rehabilitable extendido: `2,557,888`
- peso: `90.52%`
- residuo no rehabilitado: `267,860`

## Política recomendada

Para cierre formal, la política prudente es:

- usar la regla estricta como baseline oficial
- dejar la regla extendida como sensibilidad

Eso evita inflar recuperación demasiado pronto.

## Lectura por uso

### `backtest_core`

Solo:

- `good`

### `backtest_extended`

Puede incluir:

- `review_no_1m_reference`
- `review` rehabilitable estricto
- parte rehabilitable de `review_microstructure`
- parte rehabilitable de `review_1m_reference_alignment`

### `ml_flagged`

Puede incluir:

- todo lo anterior
- `reference_scale_mismatch` como señal informada

### `ml_primary`

No debería incluir por defecto:

- buckets recuperados con flag

## Decisión

La lectura final de `trades` ya no es:

- casi todo `review` queda abierto

La lectura final es:

- `bad_data` sigue en `bad`
- `good` existe pero pesa poco
- una parte grande de `review` sí puede rehabilitarse con regla explícita
- varios buckets `review` específicos también admiten recuperación con limitaciones
