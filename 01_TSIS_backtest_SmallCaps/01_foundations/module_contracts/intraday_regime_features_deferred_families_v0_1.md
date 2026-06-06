# Intraday Regime Features - Deferred Families `v0_1`

## 1. Rol

Este documento registra familias futuras de features para `intraday_regime_features`.

No forman parte de la auditoria actual de data.

No forman parte del consumidor minimo `v0_1` que se uso para validar semanticamente:

- `ohlcv_1m_split_normalized`

Su funcion es evitar que ideas validas se pierdan, sin mezclar:

- auditoria de calidad de dato

con:

- feature engineering de estrategia;
- research de alpha;
- o diseno de modelos posteriores.

## 2. Regla institucional

Estas familias quedan:

- explicitamente aplazadas;
- fuera del alcance de la fase actual;
- y reservadas para una fase posterior de research, ML o backtest contextual.

La regla correcta es:

- no implementarlas ahora por inercia;
- no venderlas como parte de la auditoria actual;
- y no confundir backlog metodologico valido con trabajo que toque ya.

## 3. Justificacion de por que NO toca ahora

La fase actual tenia un objetivo acotado:

- demostrar que `1m_split_normalized` corrige de verdad el tipo de error cross-session que un consumidor real sufriria si usara `1m raw`.

Para eso bastaba un consumidor minimo con:

- gaps;
- retornos multi-sesion;
- distancias a referencias previas;
- y algunas variables intrasesion simples para preservar la separacion contractual entre vistas.

Ir mas alla en esta fase abriria prematuramente:

- investigacion de edge;
- modelado de comportamiento de apertura;
- taxonomias de volumen;
- o construccion de features de estrategia.

Eso seria correcto en una fase posterior.

No es correcto mezclarlo con la auditoria actual de la data.

## 4. Familias diferidas

### Familia 1 | Contexto premarket

Preguntas:

- el activo ya llegaba activado antes del open?
- venia haciendo `price discovery` real o solo un gap muerto?
- el premarket estaba limpio o disperso?

Features candidatas:

- `premarket_return_vs_prev_close`
- `premarket_high_vs_prev_close`
- `premarket_low_vs_prev_close`
- `premarket_range_pct`
- `premarket_volume`
- `premarket_volume_vs_prev_n_days`
- `premarket_close_vs_open`

Vista prevista:

- principalmente `1m_split_normalized` para comparaciones contra sesion previa;
- y `1m raw` para la geometria interna del propio premarket.

Estado:

- backlog valido;
- no parte del consumidor minimo actual.

### Familia 2 | Apertura y primera hora

Preguntas:

- la apertura confirma el despertar?
- hay continuation o failure inmediata?
- la primera hora esta expandiendo o colapsando?

Features candidatas:

- `open_5m_return`
- `open_15m_return`
- `open_30m_range_pct`
- `first_hour_high_break`
- `first_hour_low_break`
- `first_hour_volume_share`
- `opening_drive_persistence`
- `first_pullback_depth`

Vista prevista:

- `1m raw`

Estado:

- backlog valido;
- no parte del consumidor minimo actual.

### Familia 3 | Extension multi-sesion mas rica

Preguntas:

- el activo llega ya demasiado extendido?
- el setup aparece en dia 1, dia 2 o dia 5 de la expansion?
- el rango ya venia explotando antes?

Features candidatas:

- `n_day_close_to_open_return_1`
- `n_day_close_to_open_return_2`
- `n_day_close_to_open_return_10`
- `distance_to_5d_high`
- `distance_to_10d_high`
- `distance_to_20d_high`
- `n_day_realized_vol_5`
- `n_day_realized_vol_10`
- `range_expansion_zscore`

Vista prevista:

- `1m_split_normalized`

Estado:

- backlog valido;
- no parte del consumidor minimo actual.

### Familia 4 | Perfil intradia de volumen

Preguntas:

- estamos ante despertar real?
- squeeze raro?
- ilusion sin participacion?

Features candidatas:

- `open_30m_volume_share`
- `first_hour_volume_share`
- `cum_volume_vs_hist_open_window`
- `session_volume_vs_prev_5d_avg`
- `volume_curve_front_loaded`
- `midday_volume_decay`
- `late_day_reacceleration`

Vista prevista:

- `1m raw`
- y, para comparaciones multi-sesion, ratios construidos con agregados historicos ya alineados

Estado:

- backlog valido;
- no parte del consumidor minimo actual.

### Familia 5 | Posicion dentro del rango de la sesion

Preguntas:

- el activo esta rompiendo?
- sosteniendo?
- o fallando?

Features candidatas:

- `close_in_session_range`
- `current_price_in_session_range`
- `open_in_session_range`
- `midday_position_in_range`
- `close_vs_session_high`
- `close_vs_session_low`

Vista prevista:

- `1m raw`

Estado:

- backlog valido;
- no parte del consumidor minimo actual.

### Familia 6 | Compresion y expansion contextual

Preguntas:

- la sesion actual esta expandiendo mucho respecto a su historia reciente?
- el rango de apertura llega ya roto o todavia comprimido?

Features candidatas:

- `session_range_vs_prev_5d_mean`
- `session_range_vs_prev_20d_mean`
- `open_30m_range_vs_prev_mean`

Vista prevista:

- mezcla:
  - `1m raw` para el dia actual
  - `1m_split_normalized` para la comparacion historica

Estado:

- backlog valido;
- no parte del consumidor minimo actual.

## 5. Veredicto

Estas familias no se descartan.

Simplemente quedan anotadas en el lugar correcto.

La lectura institucional correcta es:

- son una expansion futura plausible y metodologicamente razonable;
- pero no pertenecen a la auditoria actual de data;
- ni deben mezclarse con la validacion minima ya cerrada de `1m_split_normalized`.
